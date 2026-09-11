# Millie web chat — long thread memory — design

**Ticket:** #170 · **Repos:** `mds-digest-web` (table, memory module, Team tool, both routes) + the Olivia n8n
workflow (two Code nodes, staged for Andy's promote) · **Status:** design approved in conversation 2026-09-11.

## Goal

A Millie web thread keeps its whole history, not just its tail. Reopening a three-day investigation and asking
"what did we decide earlier about X?" answers from the thread itself, and the per-question cost does not grow as
the thread grows.

## What exists today

Both web runtimes truncate at sixteen turns.

| Runtime | Modes | Where the cut happens |
|---|---|---|
| n8n graph `12wj6h1TWqb0d4Dq` | Test · Prod · Public | `Load Recent Turns` reads `olivia_web_messages` for the thread with `limit=16` |
| `mds-digest-web` research route | Team | `readThread(...)` then `history.slice(-16)` before the model loop |

`digest.olivia_web_threads` does not exist. There is no search over a thread. The sessions rail — New session,
search, per-mode grouping, reopening a thread with its provenance — shipped in #169 and is not touched here
(board AC 3, struck through).

The longest thread anyone holds today is thirteen member turns, so nothing has hit the ceiling yet. This is built
before the ceiling is hit, not after.

## Decisions (Andy, 2026-09-11)

| # | Decision | Words |
|---|---|---|
| D1 | Memory lands in Team research mode | "Team." |
| D2 | Public gets it too, if it can be done | "and if possible in Public." |
| D3 | Test and Prod targets stay as they are | they exist to reproduce what a WhatsApp member gets, and a member gets sixteen turns inside twenty-four hours; giving them more memory makes them stop being a faithful test |

## Architecture

### One store, one writer

New table `digest.olivia_web_threads`, service_role only, RLS on:

| Column | Type | Meaning |
|---|---|---|
| `thread_id` | `text` primary key | the thread, as `olivia_web_messages` keys it |
| `asker_email` | `text not null` | whose thread it is; every read filters on it |
| `mode` | `text not null` | `team` or `public` — Test and Prod threads get no row |
| `title` | `text` | first question, 80 characters, for parity with the rail |
| `summary` | `text` | the running summary of everything older than the verbatim window |
| `summary_through_id` | `bigint not null default 0` | the last `olivia_web_messages.id` folded into `summary` |
| `turns` | `int not null default 0` | member turns folded so far |
| `updated_at` | `timestamptz not null default now()` | |

`mds-digest-web` is the only writer. The n8n graph never touches this table.

### The memory module

New `src/lib/millie/thread-memory.ts`, server-only, used by both routes:

- `loadMemory({ askerEmail, threadId, mode })` returns `{ summary, recent }`. `recent` is the last sixteen turns
  verbatim, exactly as today. `summary` covers everything older.
- The summary is refreshed **lazily, at the start of a turn**, not after the previous one. When rows exist older
  than the verbatim window whose id is above `summary_through_id`, those rows — and only those — are folded into
  the stored summary with `claude-haiku-4-5`, and the row is upserted. Nothing is re-read twice, so the cost per
  turn is flat at roughly a tenth of a cent regardless of thread length, and there is no detached
  fire-and-forget work to lose when a request ends.
- The fold prompt gets the previous summary plus the new turns and returns one summary of at most 1,200
  characters, written to carry decisions, names, numbers and open questions rather than narration.
- A failed fold is not fatal: the turn proceeds with the stored summary and the verbatim window, and the row
  keeps its old `summary_through_id` so the next turn retries the same range.

### Team reads it in process

`src/app/api/admin/millie/research/route.ts` replaces `history.slice(-16)` with `loadMemory(...)`. The summary
goes in ahead of the recent turns as one framing message; the loop itself is unchanged.

Team also gains a fourth tool in `src/lib/millie/team/tools.ts`:

```
web_thread_search({ terms: string, limit?: number }) → passages from THIS thread
```

The model supplies only `terms`. `thread_id` and `asker_email` are injected server-side from the request and the
session, the way `p_phone` is injected for a member — so the tool can only ever search the caller's own thread,
and a model that asks for another thread cannot express the request. It reads `olivia_web_messages`, matches on
`text` and `answer_md`, and returns each hit with its date and role.

### Public gets the summary, no tool

`/api/admin/millie/chat` calls `loadMemory` for `mode: "public"` and sends the summary to the door as one new
field, `thread_summary`, on the existing POST. In the graph, `Log Inbound` carries the field through, and
`Prep Context` renders it as an earlier-in-this-thread block ahead of the recent turns when the channel is web
and the mode is public. `Load Recent Turns` keeps `limit=16`.

No new gated function, no new tool node, no new route into the member tool set: the only thing crossing into the
graph is a string of prose on a request that already exists. Test and Prod send no `thread_summary`, so their
behaviour is byte-identical to today.

This is the only part that needs a graph edit. It is staged on `bqHstPDi84uOhTCJ` and promoted by Andy.

## Error handling

- Missing row, missing table row for a new thread: treated as an empty summary, not an error.
- Haiku fold fails or times out: the turn answers from the stored summary plus the verbatim window; the range is
  retried next turn.
- Search tool returns nothing: an empty result list, which the loop already handles like any other empty tool
  result.
- The door rejecting an unknown field cannot happen — `Log Inbound` reads named fields and ignores the rest —
  but the web side still sends `thread_summary` only when it is non-empty.

## Testing

Vitest, beside the existing `src/lib/millie/**/**.test.ts`:

1. The fold reads only rows above `summary_through_id` and advances it.
2. A fold failure leaves `summary_through_id` unchanged and the turn still gets the old summary.
3. `loadMemory` returns the last sixteen turns verbatim and the summary for everything older.
4. `web_thread_search` ignores any thread id or asker offered in its arguments and filters on the injected pair.
5. Public sends `thread_summary`; Test and Prod send no such field.

## Proof for the acceptance criteria

| AC | How it is proven |
|---|---|
| 1 · a 100+ turn thread answers "what did we decide earlier about X?" | seed a Team thread past 100 turns with a decision made early, ask it live, read the answer and the trail |
| 2 · per-question cost within 10% of a fresh thread | compare `metrics.cost_usd` on that thread's next turn against the same question in a new thread |
| 4 · the tool is web-only and own-thread-only | the tool exists only in the Team tool set the graph never loads: the promoted graph JSON contains no `web_thread_search`; plus a WhatsApp probe turn asking for it, and `scripts/olivia_leak_gate.py` green |
| 5 · the table exists, service_role only | the migration, then the grants read back from live |

AC 3 is already delivered by #169 and is not rebuilt.

## Out of scope

Memory for Test and Prod targets · any change to WhatsApp memory (24 hours, sixteen turns) · the sessions rail ·
embedding web turns for semantic recall — the search tool is keyword over one thread, which is what exact recall
of a decision needs.
