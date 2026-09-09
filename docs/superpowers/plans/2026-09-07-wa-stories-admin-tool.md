# WA Stories Admin Tool — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give MDS staff a page in the admin portal where they read the WhatsApp stories the pipeline made, generate more from chats they choose, reject weak ones with a reason, and record what actually reached Facebook — and fix the day-window bug that makes those stories thin in the first place.

**Architecture:** The story pipeline is lifted out of the scheduled route into `src/lib/fbstory/pipeline.ts`, which both the schedule and new admin API routes call. One new module, `digest-day.ts`, owns the definition of a digest day so the ranker and the writer can never again read different 24 hours. The ledger gains a real human `rejected` status, separate from a system release.

**Tech Stack:** Next.js App Router (`mds-digest-web`), TypeScript, Vitest, Supabase/PostgREST via `sbRequest`, Anthropic SDK with structured output, Slack Web API.

## Global Constraints

- **Two repos.** All code changes are in `mds-digest-web`. This plan, the spec and the board live in `Scorecard`. Never edit one while working the other.
- **Branch per session, never commit on `main`.** `git fetch origin && git worktree add .claude/worktrees/<name> -b <branch> origin/main`. A merge to `main` in `mds-digest-web` **is a production deploy** — Render has no staging tier.
- **Supabase project** `nadtudwuwjhckotrngzn`, schema `digest`. Apply DDL with the Supabase MCP `apply_migration`, then **re-export `db/` in the Scorecard repo** (`python3 scripts/db_export_schema.py`) and commit it, or the #65 drift alarm fires.
- **Never write to Airtable.**
- **Tests:** `npm test` (Vitest). Every task ends green.
- **Verbatim copy rule:** the post text is plain text pasted into Facebook. `stripMarkdown` runs before the gate; nothing may re-introduce markdown.
- **Every "it works" claim cites live proof** — an exec id, a SQL result, an HTTP status.

## Scope of this plan

Phase 0 closes backlog ticket **#5** (the prerequisite). Phases 1–3 build everything behind the screen: the shared module, the data changes, the API and the tool registration.

**The screen's own components are deliberately not planned here.** Andy is producing the design (`docs/design/mds-admin/reference/WA Stories.dc.html`, brief at `docs/design/mds-admin/BRIEF-08-wa-stories.md`). Writing UI steps before that exists would be fiction. When the design lands it gets its own task file, exactly as the other seven screens did.

Two spec items ride with that later task and are deliberately absent here: the queue and detail
components, and **the read that shows what a posted story earned** (parse `posted_url`, join
`digest.fb_posts`, count `digest.fb_comments`, render reactions and reach as "not captured" when
null). The parsing and storage of the link are in Task 12; only its display is deferred.

## File structure

| File | Responsibility |
|---|---|
| `src/lib/fbstory/digest-day.ts` **(new)** | The one definition of what a `digest.summaries.date` covers, in UTC instants |
| `src/lib/fbstory/thread.ts` | Unchanged job; now takes its window from `digest-day.ts`, and gains a by-ids loader |
| `src/lib/fbstory/signals.ts` | Unchanged job; now groups messages by digest day |
| `src/lib/fbstory/pipeline.ts` **(new)** | Makes and claims stories. Knows nothing of Slack or HTTP |
| `src/app/api/fbstory/draft/route.ts` | Shrinks to: call the pipeline, post the card, release on failure |
| `src/lib/fbstory/ledger.ts` | Gains `rejected` in `TOLD`; status write helpers take an actor |
| `src/lib/fbstory/rank.ts` | Prompt splits human rejections from system releases |
| `src/app/api/admin/fbstory/{generate,rewrite,edit,reject,post}/route.ts` **(new)** | Staff-gated actions |
| `src/lib/tools/storefront-tools.ts`, `src/lib/tools-health/registry.ts` | Tool card and health row |
| `src/lib/fbstory/activity.ts` | **Deleted** — dead since the footer was removed 2026-09-02 |

---

# Phase 0 — Ticket #5: the story is written from the wrong 24 hours

### Task 1: One definition of a digest day

**Why this is not a one-liner.** The digest workflow (n8n `qo3qzeVtprhTW88F`, node "Compute Time Window") is:

```js
const now = Math.floor(Date.now() / 1000);
const from = now - 24 * 60 * 60;
const midpoint = Math.floor((now + from) / 2);
const digest_date = new Date(midpoint * 1000).toISOString().split('T')[0];
```

So a summary covers **the 24 hours ending at 07:00 America/New_York**, labelled with the **UTC date of that window's midpoint** (which is 19:00 ET the evening before). Consequence, and the reason this needs a function rather than a constant: under EDT the midpoint lands at 23:00Z and the label is the window's start date; under EST it lands at 00:00Z and the label is the window's **end** date. The same rule produces a label one day apart on either side of the DST change. Reconstructing it with a fixed `11:00Z` offset would be right all summer and silently wrong from November.

**Files:**
- Create: `src/lib/fbstory/digest-day.ts`
- Test: `src/lib/fbstory/digest-day.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `digestDayBounds(date: string): { fromIso: string; toIso: string }` and `digestDayOf(sentAtIso: string): string`. Both used by Tasks 2 and 6.

- [ ] **Step 1: Write the failing test**

```ts
// src/lib/fbstory/digest-day.test.ts
import { describe, it, expect } from "vitest";
import { digestDayBounds, digestDayOf } from "./digest-day";

describe("digestDayBounds", () => {
  it("covers 07:00 ET to 07:00 ET, labelled by the midpoint's UTC date (EDT)", () => {
    // Summer: the run at 2026-09-06 07:00 EDT is 11:00Z; midpoint 2026-09-05 23:00Z, so the label is the 5th.
    expect(digestDayBounds("2026-09-05")).toEqual({
      fromIso: "2026-09-05T11:00:00.000Z",
      toIso: "2026-09-06T11:00:00.000Z",
    });
  });

  it("shifts an hour and a day under EST", () => {
    // Winter: the run at 2026-12-10 07:00 EST is 12:00Z; midpoint 2026-12-10 00:00Z, so the label is the 10th
    // and the window is mostly the 9th. This is the case a fixed offset gets wrong.
    expect(digestDayBounds("2026-12-10")).toEqual({
      fromIso: "2026-12-09T12:00:00.000Z",
      toIso: "2026-12-10T12:00:00.000Z",
    });
  });

  it("round-trips: every instant in a day's window maps back to that day", () => {
    for (const date of ["2026-09-05", "2026-12-10", "2026-11-01"]) {
      const { fromIso, toIso } = digestDayBounds(date);
      expect(digestDayOf(fromIso)).toBe(date);
      expect(digestDayOf(new Date(Date.parse(toIso) - 1000).toISOString())).toBe(date);
    }
  });
});

describe("digestDayOf", () => {
  it("puts a late-evening ET message on the day the digest will label it", () => {
    // 2026-09-05 20:00 EDT = 2026-09-06 00:00Z. The UTC calendar day says the 6th; the digest says the 5th.
    expect(digestDayOf("2026-09-06T00:00:00.000Z")).toBe("2026-09-05");
  });

  it("puts an early-morning ET message before the 7am cutoff on the previous label", () => {
    // 2026-09-06 06:00 EDT = 10:00Z, still inside the window that closes at 11:00Z.
    expect(digestDayOf("2026-09-06T10:00:00.000Z")).toBe("2026-09-05");
  });

  it("puts a message after the cutoff on the next label", () => {
    expect(digestDayOf("2026-09-06T11:30:00.000Z")).toBe("2026-09-06");
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/digest-day.test.ts`
Expected: FAIL, `Failed to resolve import "./digest-day"`.

- [ ] **Step 3: Implement**

```ts
// src/lib/fbstory/digest-day.ts
//
// What a row in digest.summaries actually covers.
//
// The daily digest (n8n qo3qzeVtprhTW88F, "Compute Time Window") fetches the 24
// hours ending at its 07:00 America/New_York run, and labels the row with the UTC
// date of that window's MIDPOINT — 19:00 ET the evening before. Under EDT the
// midpoint is 23:00Z and the label is the window's start date; under EST it is
// 00:00Z and the label is the window's end date. So the label is one day apart on
// either side of the DST change, and a fixed "11:00Z to 11:00Z" offset is right
// all summer and wrong from November.
//
// Before this file existed, thread.ts and signals.ts fetched the UTC calendar day
// instead. The two windows overlap for 13 hours, so the ranker judged one
// conversation and the writer wrote from another: 9 of the 11 stories offered
// between 2026-09-02 and 2026-09-07 were built from a different message set than
// the one that was ranked, and one was built from a single message.

const ZONE = "America/New_York";
const RUN_HOUR_ET = 7;

/** UTC offset in minutes for `instant` in New York (240 under EDT, 300 under EST). */
function offsetMinutes(instant: Date): number {
  // "en-US" with timeZoneName: "shortOffset" yields e.g. "GMT-4".
  const label = new Intl.DateTimeFormat("en-US", { timeZone: ZONE, timeZoneName: "shortOffset" })
    .formatToParts(instant)
    .find((p) => p.type === "timeZoneName")?.value;
  const m = /GMT([+-]\d{1,2})(?::(\d{2}))?/.exec(label ?? "");
  if (!m) throw new Error(`could not read a UTC offset for ${ZONE} at ${instant.toISOString()}`);
  const hours = Number(m[1]);
  const mins = Number(m[2] ?? 0) * (hours < 0 ? -1 : 1);
  return hours * 60 + mins;
}

/** The instant of `RUN_HOUR_ET` on the ET calendar day `date` (YYYY-MM-DD). */
function runInstant(date: string): Date {
  const naive = Date.parse(`${date}T${String(RUN_HOUR_ET).padStart(2, "0")}:00:00Z`);
  // Guess with the offset at the naive instant, then re-resolve — one correction is
  // enough because the offset only changes by an hour and never at 07:00 local.
  const guess = new Date(naive - offsetMinutes(new Date(naive)) * 60_000);
  return new Date(naive - offsetMinutes(guess) * 60_000);
}

/** The UTC date the digest would label a window ending at `end`. */
function labelFor(end: Date): string {
  return new Date(end.getTime() - 12 * 3600_000).toISOString().slice(0, 10);
}

/**
 * The UTC instants a `digest.summaries.date` covers: [fromIso, toIso).
 * Solved rather than computed, because which ET run day produces a given label
 * depends on daylight saving.
 */
export function digestDayBounds(date: string): { fromIso: string; toIso: string } {
  for (const candidate of [nextDay(date), date]) {
    const end = runInstant(candidate);
    if (labelFor(end) === date) {
      return {
        fromIso: new Date(end.getTime() - 24 * 3600_000).toISOString(),
        toIso: end.toISOString(),
      };
    }
  }
  throw new Error(`no digest run window produces the label ${date}`);
}

/** The digest day an individual message belongs to. */
export function digestDayOf(sentAtIso: string): string {
  const t = Date.parse(sentAtIso);
  // The window closing at the next 07:00 ET at or after this instant is the one
  // that contains it.
  const sameDay = runInstant(new Date(t).toISOString().slice(0, 10));
  const end = t <= sameDay.getTime() ? sameDay : runInstant(nextDay(new Date(t).toISOString().slice(0, 10)));
  return labelFor(end);
}

function nextDay(date: string): string {
  return new Date(Date.parse(`${date}T00:00:00Z`) + 86_400_000).toISOString().slice(0, 10);
}
```

- [ ] **Step 4: Run the tests**

Run: `npm test -- src/lib/fbstory/digest-day.test.ts`
Expected: PASS, 6 tests.

If the EST case fails by an hour, the bug is in `runInstant`'s single correction — print `offsetMinutes` for both candidates before changing the expectation. The expectations above are derived from the workflow code, not from the implementation.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/digest-day.ts src/lib/fbstory/digest-day.test.ts
git commit -m "#5: one definition of what a digest day covers"
```

---

### Task 2: The thread and the signals use the digest day

**Files:**
- Modify: `src/lib/fbstory/thread.ts:118-124` (`loadThread`'s window)
- Modify: `src/lib/fbstory/signals.ts:85-105` (`loadSignalsByChatDay`'s window and grouping)
- Test: `src/lib/fbstory/digest-day.test.ts` (extend), `src/lib/fbstory/signals.test.ts` (extend)

**Interfaces:**
- Consumes: `digestDayBounds`, `digestDayOf` from Task 1.
- Produces: no signature changes. `loadThread(pick, chatName)` and `loadSignalsByChatDay(days, asof)` keep their shapes.

- [ ] **Step 1: Write the failing test for the grouping**

`groupByChatDay` does not exist yet — extract it from `loadSignalsByChatDay` so the grouping is testable without a network.

```ts
// append to src/lib/fbstory/signals.test.ts
import { groupByChatDay } from "./signals";

describe("groupByChatDay", () => {
  const msg = (id: string, chat_id: string, sent_at: string) => ({
    id, chat_id, sent_at, sender_member: "recA", text: "hello there", reply_to: null,
  });

  it("groups by digest day, not by UTC calendar day", () => {
    // 00:00Z on the 6th is 20:00 ET on the 5th — the digest calls it the 5th.
    const grouped = groupByChatDay([
      msg("m1", "chatA", "2026-09-05T18:00:00.000Z"),
      msg("m2", "chatA", "2026-09-06T00:00:00.000Z"),
      msg("m3", "chatA", "2026-09-06T11:30:00.000Z"),
    ]);
    expect([...grouped.keys()].sort()).toEqual(["chatA|2026-09-05", "chatA|2026-09-06"]);
    expect(grouped.get("chatA|2026-09-05")!.map((m) => m.id)).toEqual(["m1", "m2"]);
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/signals.test.ts`
Expected: FAIL, `groupByChatDay is not a function`.

- [ ] **Step 3: Implement the signals change**

In `src/lib/fbstory/signals.ts`, export the grouping and widen the fetch so a digest day's tail is inside it:

```ts
import { digestDayBounds, digestDayOf } from "./digest-day";

export function groupByChatDay<T extends { chat_id: string; sent_at: string }>(rows: T[]): Map<string, T[]> {
  const byKey = new Map<string, T[]>();
  for (const r of rows) {
    const key = `${r.chat_id}|${digestDayOf(r.sent_at)}`;
    const list = byKey.get(key) ?? [];
    list.push(r);
    byKey.set(key, list);
  }
  return byKey;
}
```

and in `loadSignalsByChatDay`, replace the `T00:00:00Z`/`T23:59:59Z` bounds and the `slice(0, 10)` grouping:

```ts
  const { start, end } = windowBounds(days, asof);
  // A digest day runs to 07:00 ET the following morning, so the fetch must reach
  // past the last labelled day or its evening is missing.
  const from = digestDayBounds(start).fromIso;
  const to = digestDayBounds(end).toIso;
  const rows = await sbRequest<Array<SignalMessage & { chat_id: string; sent_at: string }>>(
    `wa_messages?sent_at=gte.${from}&sent_at=lt.${to}` +
      `&select=id,chat_id,sender_member,text,reply_to,sent_at&order=sent_at.asc&limit=5000`,
  );

  const out = new Map<string, ThreadSignals>();
  for (const [key, msgs] of groupByChatDay(rows)) out.set(key, computeSignals(msgs));
  return out;
```

- [ ] **Step 4: Implement the thread change**

In `src/lib/fbstory/thread.ts`, replace the two window lines in `loadThread`:

```ts
import { digestDayBounds } from "./digest-day";
// …
  // The ranker picks days from digest.summaries, whose date is a digest day, not a
  // UTC calendar day. Fetching the calendar day cut the US evening off every story
  // and pulled in the previous morning — see digest-day.ts.
  const from = digestDayBounds(pick.window_start).fromIso;
  const to = digestDayBounds(pick.window_end).toIso;
  const rows = await sbRequest<RawMessage[]>(
    `wa_messages?chat_id=eq.${encodeURIComponent(pick.chat_id)}` +
      `&sent_at=gte.${from}&sent_at=lt.${to}` +
      `&select=id,sender_member,sent_at,text,reply_to&order=sent_at.asc&limit=${RAW_MESSAGE_LIMIT}`,
  );
```

Note the upper bound changes from `lte` to `lt`: `toIso` is the exclusive end of the window.

- [ ] **Step 5: Run the whole suite**

Run: `npm test`
Expected: PASS. If a `thread.test.ts` case asserted the old `T00:00:00Z` string, update it to the digest bounds — the old string encoded the bug.

- [ ] **Step 6: Commit**

```bash
git add src/lib/fbstory/thread.ts src/lib/fbstory/signals.ts src/lib/fbstory/signals.test.ts
git commit -m "#5: the writer and the ranker read the same 24 hours"
```

---

### Task 3: A thin thread is never written

**Why:** `MIN_MSGS = 5` in `candidates.ts` filters the *summary*, not the built thread. Once a pick is made, nothing checks the conversation is still a conversation — which is how a five-paragraph post came out of one message.

**Files:**
- Modify: `src/lib/fbstory/thread.ts` (export a check), `src/app/api/fbstory/draft/route.ts:~136` (use it)
- Test: `src/lib/fbstory/thread.test.ts`

**Interfaces:**
- Produces: `isTooThin(thread: Thread): string | null` — a reason, or null when the thread is postable. Task 5 moves the call site into the pipeline.

- [ ] **Step 1: Write the failing test**

```ts
// append to src/lib/fbstory/thread.test.ts
import { isTooThin } from "./thread";
import type { Thread, ThreadMessage } from "./types";

function thread(messages: Array<Partial<ThreadMessage>>): Thread {
  const msgs = messages.map((m, i) => ({
    id: `m${i}`, sender_member: "recA", sender_name: "Ann Lee",
    sent_at: `2026-09-05T1${i}:00:00.000Z`, text: "something substantive", reply_to: null, ...m,
  }));
  return {
    story_key: "chatA:m0", chat_id: "chatA", chat_name: "MDS DTC/Shopify",
    window_start: "2026-09-05", window_end: "2026-09-05", root_message_id: "m0",
    messages: msgs, message_ids: msgs.map((m) => m.id),
    member_names: [...new Set(msgs.map((m) => m.sender_name).filter((n): n is string => !!n))],
  };
}

describe("isTooThin", () => {
  it("refuses a single message", () => {
    expect(isTooThin(thread([{}]))).toMatch(/1 message/);
  });

  it("refuses one person talking to themselves", () => {
    expect(isTooThin(thread([{}, {}, {}, {}, {}]))).toMatch(/1 voice/);
  });

  it("accepts a real exchange", () => {
    const two = thread([
      { sender_member: "recA", sender_name: "Ann Lee" },
      { sender_member: "recB", sender_name: "Bo Ray" },
      { sender_member: "recA", sender_name: "Ann Lee" },
      { sender_member: "recB", sender_name: "Bo Ray" },
      { sender_member: "recA", sender_name: "Ann Lee" },
    ]);
    expect(isTooThin(two)).toBeNull();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/thread.test.ts`
Expected: FAIL, `isTooThin is not a function`.

- [ ] **Step 3: Implement**

```ts
// src/lib/fbstory/thread.ts
/** The summary-level MIN_MSGS in candidates.ts filters chat-days, not built
 *  threads. A pick whose reconstructed thread is one message still produced a
 *  five-paragraph post (2026-09-02 and 2026-09-04, DTC/Shopify). A story needs a
 *  conversation: several messages and more than one person in it. */
const MIN_THREAD_MSGS = 5;
const MIN_VOICES = 2;

export function isTooThin(thread: Thread): string | null {
  const msgs = thread.messages.filter((m) => m.text.trim().length > 0).length;
  if (msgs < MIN_THREAD_MSGS) {
    return `thread is ${msgs} message${msgs === 1 ? "" : "s"} (needs ${MIN_THREAD_MSGS})`;
  }
  const voices = new Set(thread.messages.map((m) => m.sender_member).filter(Boolean)).size;
  if (voices < MIN_VOICES) {
    return `thread has ${voices} voice${voices === 1 ? "" : "s"} (needs ${MIN_VOICES})`;
  }
  return null;
}
```

- [ ] **Step 4: Wire it into the route**

In `src/app/api/fbstory/draft/route.ts`, immediately after `const thread = await loadThread(...)` and before the dedupe check:

```ts
      const thin = isTooThin(thread);
      if (thin) {
        rejected.push(`${thread.chat_name}: ${thin}`);
        continue;
      }
```

Add `isTooThin` to the existing `@/lib/fbstory/thread` import. A run where every pick is thin already reports through the existing "none postable" quiet line, so no new reporting is needed.

- [ ] **Step 5: Run the suite and commit**

Run: `npm test`
Expected: PASS.

```bash
git add src/lib/fbstory/thread.ts src/lib/fbstory/thread.test.ts src/app/api/fbstory/draft/route.ts
git commit -m "#5: a thread that is not a conversation is never written"
```

---

### Task 4: Prove #5 against live data

No code. This produces the ticket's close.

- [ ] **Step 1: Merge and deploy**

Merge the branch to `main` in `mds-digest-web` (this deploys to Render) and confirm:

```bash
curl -s https://mds-digest-web.onrender.com/api/version
```

Expected: the merge commit's sha. Use `mds-digest-web.onrender.com`, never `digest.mds.co` — that hostname does not resolve on Andy's Mac.

- [ ] **Step 2: Re-measure the 11 rows (AC 2)**

For each `offered`/`draft` row in `digest.fb_group_posts`, compare its stored `message_ids` count against the summary it was ranked from:

```sql
select g.created_at::date as run_day, g.chat_name, g.window_start,
       array_length(g.message_ids, 1) as thread_msgs,
       (select sum(s.msg_count) from digest.summaries s
         where s.period_type = 'daily' and s.chat_id = g.chat_id
           and s.date between g.window_start and g.window_end) as summary_msgs
from digest.fb_group_posts g
where g.status in ('offered', 'draft')
order by g.created_at desc;
```

Baseline recorded 2026-09-07: **2 of 11 matched.** Then run the two picks the ticket names and check the counts now agree:

```bash
curl -s "https://mds-digest-web.onrender.com/api/fbstory/draft?secret=$FB_STORY_SECRET&dry=1&asof=2026-09-07" | python3 -m json.tool
```

- [ ] **Step 3: Release the one-message row (AC 4)**

The DTC/Shopify row `120363407426452368@g.us:O0bebZqK3HhiqA-gvsBq53hn5v7kA` is `offered` and was built from a single message. Release it so the corrected pipeline can tell that conversation properly:

```sql
update digest.fb_group_posts
   set status = 'skipped',
       skip_reason = 'Released 2026-09-XX (#5): built from 1 message by the pre-fix UTC-day window.'
 where story_key = '120363407426452368@g.us:O0bebZqK3HhiqA-gvsBq53hn5v7kA';
```

Confirm the two already-correct threads (Retail 09-04, AI 08-28) keep their story keys — a changed key would mean the window change moved the root message and broke dedupe.

- [ ] **Step 4: Before/after draft (AC 5)**

Put the 2026-09-07 DTC/Shopify draft and the re-run draft side by side in the ticket close. The counts are evidence; the story is the point.

- [ ] **Step 5: Close #5 in `FB_BACKLOG.md`**

Move the block to CLOSED with results, the AC checklist met/not, and the before/after numbers. Commit in the Scorecard repo.

---

# Phase 1 — The shared pipeline

### Task 5: Lift `makeStories` and `claimStories` out of the route

Behaviour-preserving extraction. No new features in this task — that is what makes it reviewable.

**Files:**
- Create: `src/lib/fbstory/pipeline.ts`, `src/lib/fbstory/pipeline.test.ts`
- Modify: `src/app/api/fbstory/draft/route.ts`

**Interfaces:**
- Consumes: everything already in `src/lib/fbstory/`.
- Produces:
  ```ts
  type MakeOptions = { days: number; asof?: Date; max: number;
                       chatIds?: string[]; date?: string; excludeStoryKeys?: string[] };
  type MakeResult = { made: CardOption[]; rejected: string[]; none?: string };
  makeStories(opts: MakeOptions): Promise<MakeResult>
  claimStories(made: CardOption[]): Promise<{ claimed: CardOption[]; rejected: string[] }>
  ```
  Tasks 6, 7 and 12 all call these.

- [ ] **Step 1: Write the failing test**

This is the feature's first test with mocks. The pattern matters — copy it.

```ts
// src/lib/fbstory/pipeline.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("./rank", () => ({ rankStory: vi.fn() }));
vi.mock("./write", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./write")>()),
  writePost: vi.fn(),
}));
vi.mock("./candidates", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./candidates")>()),
  loadCandidates: vi.fn(),
}));
vi.mock("./signals", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./signals")>()),
  loadSignalsByChatDay: vi.fn(async () => new Map()),
}));
vi.mock("./thread", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./thread")>()),
  loadThread: vi.fn(),
}));
vi.mock("./ledger", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./ledger")>()),
  loadRecentLedger: vi.fn(async () => []),
}));
vi.mock("./tags", () => ({ loadMemberTags: vi.fn(async () => []), formatTagLine: () => "" }));
vi.mock("@/lib/supabase", () => ({ sbRequest: vi.fn(async () => []), quoteInValue: (s: string) => s }));

import { makeStories } from "./pipeline";
import { loadCandidates } from "./candidates";
import { rankStory } from "./rank";
import { loadThread } from "./thread";
import { writePost } from "./write";

const candidate = {
  summary_key: "k", date: "2026-09-05", chat_id: "chatA", chat_name: "MDS DTC/Shopify",
  tl_dr: "They argued about AOV.", summary_text: "…", topics: "ads",
  msg_count: 16, participant_count: 5,
};

const thread = {
  story_key: "chatA:m0", chat_id: "chatA", chat_name: "MDS DTC/Shopify",
  window_start: "2026-09-05", window_end: "2026-09-05", root_message_id: "m0",
  messages: ["m0", "m1", "m2", "m3", "m4"].map((id, i) => ({
    id, sender_member: i % 2 ? "recB" : "recA", sender_name: i % 2 ? "Bo Ray" : "Ann Lee",
    sent_at: `2026-09-05T1${i}:00:00.000Z`, text: `line ${i}`, reply_to: null,
  })),
  message_ids: ["m0", "m1", "m2", "m3", "m4"],
  member_names: ["Ann Lee", "Bo Ray"],
};

beforeEach(() => {
  vi.mocked(loadCandidates).mockResolvedValue([candidate]);
  vi.mocked(loadThread).mockResolvedValue(thread);
  vi.mocked(writePost).mockResolvedValue({ post_text: "A post about margins.", members_named: [] });
  vi.mocked(rankStory).mockResolvedValue({
    picks: [{ chat_id: "chatA", window_start: "2026-09-05", window_end: "2026-09-05", topic: "AOV", why: "numbers" }],
  });
});

describe("makeStories", () => {
  it("returns a written, gated story", async () => {
    const res = await makeStories({ days: 7, max: 3 });
    expect(res.made).toHaveLength(1);
    expect(res.made[0].thread.story_key).toBe("chatA:m0");
  });

  it("refuses a pick for a chat that was never a candidate", async () => {
    vi.mocked(rankStory).mockResolvedValue({
      picks: [{ chat_id: "ghost", window_start: "2026-09-05", window_end: "2026-09-05", topic: "x", why: "y" }],
    });
    const res = await makeStories({ days: 7, max: 3 });
    expect(res.made).toHaveLength(0);
    expect(res.rejected[0]).toMatch(/not in the candidate set/);
  });

  it("passes the ranker's none straight through", async () => {
    vi.mocked(rankStory).mockResolvedValue({ none: "thin week" });
    const res = await makeStories({ days: 7, max: 3 });
    expect(res.none).toBe("thin week");
    expect(res.made).toHaveLength(0);
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/pipeline.test.ts`
Expected: FAIL, cannot resolve `./pipeline`.

- [ ] **Step 3: Move the code**

Create `src/lib/fbstory/pipeline.ts` and move code out of `src/app/api/fbstory/draft/route.ts` unchanged:

| From (current line numbers) | To |
|---|---|
| `84-105` — the `Promise.all` load, `selectCandidates`, the signals block | `makeStories`, top |
| `107-110` — the `rankStory` call and the `none` branch | `makeStories`, returning `{ made: [], rejected: [], none }` |
| `120-244` — the whole `for (const pick of ranked.picks)` loop | `makeStories`, the body |
| `264-303` — the claim loop with its duplicate-key handling | `claimStories` | Keep every comment — they record incidents. `makeStories` ends with `return { made: options, rejected }`, or `{ made: [], rejected, none: ranked.none }` when the ranker declines. `CardOption` moves from `slack.ts` into `types.ts` so the pipeline does not import Slack; `slack.ts` re-exports it so its own imports keep working.

- [ ] **Step 4: Shrink the route**

`src/app/api/fbstory/draft/route.ts` becomes: parse and validate the query, `makeStories({ days, asof, max: 3 })`, return the dry-run JSON if `dry`, else `claimStories`, `postCard`, and the existing release-on-failure path. The quiet-line helpers and every early return stay exactly as they are.

- [ ] **Step 5: Run everything**

Run: `npm test && npx next build`
Expected: PASS, and a clean build. Then a live dry run against the deployed previous version is not possible — instead prove the extraction locally:

```bash
npm run dev
curl -s "http://localhost:3000/api/fbstory/draft?secret=$FB_STORY_SECRET&dry=1" | python3 -m json.tool
```

Expected: the same shape as production returns — `ok`, `dry`, `options[]`, `rejected[]`.

- [ ] **Step 6: Commit**

```bash
git add src/lib/fbstory/pipeline.ts src/lib/fbstory/pipeline.test.ts src/lib/fbstory/types.ts src/lib/fbstory/slack.ts src/app/api/fbstory/draft/route.ts
git commit -m "refactor(fbstory): one pipeline module, called by the schedule and soon by the admin"
```

---

### Task 6: Scope a run to chats, a day, or away from a story

**Files:**
- Modify: `src/lib/fbstory/pipeline.ts`, `src/lib/fbstory/candidates.ts`
- Test: `src/lib/fbstory/pipeline.test.ts`, `src/lib/fbstory/candidates.test.ts`

**Interfaces:**
- Consumes: `MakeOptions` from Task 5.
- Produces: `selectCandidates(rows, excludedChatIds, onlyChatIds?, onlyDate?)`. Task 12's `generate` route passes all three of `chatIds`, `date` and `excludeStoryKeys`.

- [ ] **Step 1: Write the failing tests**

```ts
// append to src/lib/fbstory/candidates.test.ts
it("keeps only the chats asked for, without dropping the blocklist", () => {
  const rows = [cand({}), cand({ chat_id: "chatB" }), cand({ chat_id: "chatC" })];
  const kept = selectCandidates(rows, ["chatC"], ["chatB", "chatC"]);
  expect(kept.map((r) => r.chat_id)).toEqual(["chatB"]);
});

it("narrows to one day when asked", () => {
  const rows = [cand({ date: "2026-09-04" }), cand({ date: "2026-09-05" })];
  expect(selectCandidates(rows, [], undefined, "2026-09-05").map((r) => r.date)).toEqual(["2026-09-05"]);
});
```

```ts
// append to src/lib/fbstory/pipeline.test.ts
it("never re-offers an excluded story key", async () => {
  const res = await makeStories({ days: 7, max: 3, excludeStoryKeys: ["chatA:m0"] });
  expect(res.made).toHaveLength(0);
  expect(res.rejected[0]).toMatch(/excluded/);
});

it("honours max", async () => {
  vi.mocked(rankStory).mockResolvedValue({
    picks: [
      { chat_id: "chatA", window_start: "2026-09-05", window_end: "2026-09-05", topic: "a", why: "y" },
      { chat_id: "chatA", window_start: "2026-09-04", window_end: "2026-09-04", topic: "b", why: "y" },
    ],
  });
  const res = await makeStories({ days: 7, max: 1 });
  expect(res.made).toHaveLength(1);
});
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npm test -- src/lib/fbstory/candidates.test.ts src/lib/fbstory/pipeline.test.ts`
Expected: FAIL — extra arguments ignored, `excludeStoryKeys` unknown, `max` not enforced.

- [ ] **Step 3: Implement**

```ts
// src/lib/fbstory/candidates.ts
export function selectCandidates(
  rows: Candidate[],
  excludedChatIds: string[],
  onlyChatIds?: string[],
  onlyDate?: string,
): Candidate[] {
  const excluded = new Set(excludedChatIds);
  const only = onlyChatIds && onlyChatIds.length > 0 ? new Set(onlyChatIds) : null;
  return rows.filter((r) => {
    // The blocklist is never overridden by a request: an excluded chat is excluded
    // even when someone ticks it, because the reason is disclosure, not taste.
    if (excluded.has(r.chat_id)) return false;
    if (only && !only.has(r.chat_id)) return false;
    if (onlyDate && r.date !== onlyDate) return false;
    if (!r.tl_dr && !r.summary_text) return false;
    if ((r.msg_count ?? 0) < MIN_MSGS) return false;
    return true;
  });
}
```

In `pipeline.ts`: pass `opts.chatIds` and `opts.date` into `selectCandidates`; skip a built thread whose `story_key` is in `opts.excludeStoryKeys` with the reason `` `${thread.chat_name}: excluded by this request` ``; and `break` out of the pick loop once `made.length === opts.max`.

- [ ] **Step 4: Run and commit**

Run: `npm test`
Expected: PASS.

```bash
git add src/lib/fbstory/candidates.ts src/lib/fbstory/candidates.test.ts src/lib/fbstory/pipeline.ts src/lib/fbstory/pipeline.test.ts
git commit -m "feat(fbstory): a run can be scoped to chats, one day, or away from a story"
```

---

### Task 7: Rewrite one story from the same conversation

**Files:**
- Modify: `src/lib/fbstory/pipeline.ts`
- Test: `src/lib/fbstory/pipeline.test.ts`

**Interfaces:**
- Produces: `rewriteStory(storyKey: string): Promise<{ ok: true; option: CardOption } | { ok: false; reason: string }>`. Task 12's `rewrite` route calls it.

- [ ] **Step 1: Write the failing test**

```ts
// append to src/lib/fbstory/pipeline.test.ts
import { rewriteStory } from "./pipeline";
import { getLedgerRow } from "./ledger";

it("rewrites from the stored conversation and keeps the story key", async () => {
  vi.mocked(getLedgerRow).mockResolvedValue({
    story_key: "chatA:m0", chat_id: "chatA", chat_name: "MDS DTC/Shopify",
    window_start: "2026-09-05", window_end: "2026-09-05", message_ids: thread.message_ids,
    draft_text: "old text", why_picked: "numbers", confidence: null, status: "offered", skip_reason: null,
  });
  vi.mocked(writePost).mockResolvedValue({ post_text: "A sharper post.", members_named: [] });
  const res = await rewriteStory("chatA:m0");
  expect(res.ok).toBe(true);
  if (res.ok) {
    expect(res.option.draft.post_text).toContain("A sharper post.");
    expect(res.option.thread.story_key).toBe("chatA:m0");
  }
});
```

Add `getLedgerRow: vi.fn()` and `loadThreadByIds: vi.fn(async () => thread)` to the existing `./ledger` and `./thread` mocks.

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/pipeline.test.ts`
Expected: FAIL, `rewriteStory is not a function`.

- [ ] **Step 3: Implement**

```ts
// src/lib/fbstory/pipeline.ts
/** Same conversation, new words. The story key is minted from the root message,
 *  so a rewrite keeps it and the dedupe history stays intact. */
export async function rewriteStory(
  storyKey: string,
): Promise<{ ok: true; option: CardOption } | { ok: false; reason: string }> {
  const row = await getLedgerRow(storyKey);
  if (!row) return { ok: false, reason: `no story ${storyKey}` };
  const thread = await loadThreadByIds(row);
  const headerLine = `${thread.chat_name} - ${storyDate(thread.window_end)}`;
  const draft = await writePost(thread, headerLine);
  const { draft: reconciled } = reconcileNames(draft, thread);
  const gate = checkDraft(reconciled, thread, new Set(thread.member_names));
  if (!gate.ok) return { ok: false, reason: gate.reason };
  return {
    ok: true,
    option: {
      thread, draft: reconciled,
      pick: { chat_id: thread.chat_id, window_start: thread.window_start, window_end: thread.window_end,
              topic: "", why: row.why_picked ?? "" },
      signals: describeSignals(computeSignals(thread.messages)),
      tagLine: formatTagLine(await loadMemberTags(reconciled.members_named).catch(() => [])),
    },
  };
}
```

`loadThreadByIds` does not exist yet — build it here, in `src/lib/fbstory/thread.ts`:

```ts
/** Rebuild a stored story's conversation from its message ids. The ledger keeps
 *  ids, not text, and both a rewrite and an edit need the source messages — an
 *  edited post cannot be checked against a draft, only against what people said. */
export async function loadThreadByIds(row: LedgerRow): Promise<Thread> {
  const ids = row.message_ids;
  if (ids.length === 0) throw new Error(`story ${row.story_key} has no message ids`);
  const rows = await sbRequest<RawMessage[]>(
    `wa_messages?id=in.(${ids.map((i) => `"${i}"`).join(",")})` +
      `&select=id,sender_member,sent_at,text,reply_to&order=sent_at.asc&limit=${RAW_MESSAGE_LIMIT}`,
  );
  const memberIds = [...new Set(rows.map((r) => r.sender_member).filter((v): v is string => !!v))];
  const nameByRecordId = new Map<string, string>();
  if (memberIds.length > 0) {
    const members = await sbRequest<Array<{ airtable_id: string; name: string | null; full_name: string | null }>>(
      `members?airtable_id=in.(${memberIds.map((i) => `"${i}"`).join(",")})&select=airtable_id,name,full_name`,
    );
    for (const m of members) {
      const n = m.full_name || m.name;
      if (!n) continue;
      const cleaned = normaliseMemberName(n);
      if (cleaned) nameByRecordId.set(m.airtable_id, cleaned);
    }
  }
  return buildThread(
    { chat_id: row.chat_id, window_start: row.window_start, window_end: row.window_end, topic: "", why: "" },
    row.chat_name, rows, nameByRecordId,
  );
}
```

- [ ] **Step 4: Run and commit**

Run: `npm test`
Expected: PASS.

```bash
git add src/lib/fbstory/pipeline.ts src/lib/fbstory/pipeline.test.ts
git commit -m "feat(fbstory): rewrite a story from the same conversation"
```

---

### Task 8: Delete `activity.ts`

**Files:**
- Delete: `src/lib/fbstory/activity.ts`, `src/lib/fbstory/activity.test.ts`

- [ ] **Step 1: Confirm nothing imports it**

Run: `grep -rn "fbstory/activity\|from \"./activity\"" src/`
Expected: no matches outside the two files themselves. If there is a match, stop — it is not dead and this task is wrong.

- [ ] **Step 2: Delete, build and commit**

```bash
git rm src/lib/fbstory/activity.ts src/lib/fbstory/activity.test.ts
npm test && npx next build
git commit -m "chore(fbstory): drop activity.ts, dead since the footer was removed"
```

---

# Phase 2 — The record and the API

### Task 9: The ledger learns who did what

**Files:**
- Migration via Supabase MCP `apply_migration`, name `fb_group_posts_admin_actions`
- Modify (Scorecard repo): `db/tables.sql` via `python3 scripts/db_export_schema.py`
- Modify: `src/lib/fbstory/types.ts`

**Interfaces:**
- Produces: `LedgerStatus` gains `"rejected"`; `LedgerRow` gains `origin`, `edited_text`, `posted_url`, `acted_by`, `acted_at`. Tasks 10 and 12 rely on these names.

- [ ] **Step 1: Apply the migration**

```sql
alter table digest.fb_group_posts
  add column if not exists origin      text not null default 'schedule',
  add column if not exists edited_text text,
  add column if not exists posted_url  text,
  add column if not exists acted_by    text,
  add column if not exists acted_at    timestamptz;

-- The existing CHECK does not know about 'rejected'; an insert would 23514 without this.
alter table digest.fb_group_posts drop constraint if exists fb_group_posts_status_chk;
alter table digest.fb_group_posts add constraint fb_group_posts_status_chk
  check (status = any (array['draft','offered','posted','rejected','skipped','blocked']));

comment on column digest.fb_group_posts.origin is
  'schedule = the Mon/Wed/Fri run, admin = generated from /admin/stories';
comment on column digest.fb_group_posts.edited_text is
  'What a human made it. What was posted is coalesce(edited_text, draft_text).';
```

- [ ] **Step 2: Verify against live**

```sql
select column_name from information_schema.columns
 where table_schema = 'digest' and table_name = 'fb_group_posts'
   and column_name in ('origin','edited_text','posted_url','acted_by','acted_at');
select count(*) from digest.fb_group_posts where origin = 'schedule';
```

Expected: 5 rows, and 14 (every existing row correctly attributed to the schedule).

- [ ] **Step 3: Re-export the SQL layer**

In the Scorecard repo: `python3 scripts/db_export_schema.py`, review the `db/tables.sql` diff (five columns and the new constraint, nothing else), and commit. Skipping this fires the #65 drift alarm.

- [ ] **Step 4: Update the types and commit**

In `src/lib/fbstory/types.ts` add `"rejected"` to `LedgerStatus` and the five optional fields to `LedgerRow`, with the `rejected` comment explaining it is a human verdict and `skipped` is a system release.

```bash
git add src/lib/fbstory/types.ts
git commit -m "feat(fbstory): the ledger records who acted, what they changed and where it went"
```

---

### Task 10: A system release stops looking like a human verdict

This is #5 AC 6 and it is the regression that started all of this.

**Files:**
- Modify: `src/lib/fbstory/ledger.ts`, `src/lib/fbstory/rank.ts`
- Test: `src/lib/fbstory/rank.test.ts`, `src/lib/fbstory/ledger.test.ts`

- [ ] **Step 1: Write the failing tests**

```ts
// append to src/lib/fbstory/rank.test.ts
it("shows a human rejection to the ranker and hides a system release", () => {
  const rows = [
    row({ chat_name: "MDS TikTok", status: "rejected", why_picked: "tool chatter", skip_reason: "not enough substance" }),
    row({ chat_name: "MDS Retail", status: "skipped", skip_reason: "Slack post failed: channel_not_found" }),
  ];
  const prompt = buildRankPrompt([cand({})], rows, new Map(), []);
  expect(prompt).toContain("not enough substance");
  expect(prompt).not.toContain("Slack post failed");
  expect(prompt).not.toContain("MDS Retail");
});
```

```ts
// append to src/lib/fbstory/ledger.test.ts
it("never re-offers a story a human rejected", () => {
  const told = [row({ story_key: "chatA:m0", status: "rejected", message_ids: ["m0"] })];
  expect(isAlreadyTold(told, "chatA:m0", ["m0"])).toMatch(/already told/);
});

it("keeps a system release eligible", () => {
  const told = [row({ story_key: "chatA:m0", status: "skipped", message_ids: ["m0"] })];
  expect(isAlreadyTold(told, "chatA:m0", ["m0"])).toBeNull();
});
```

Use each file's existing `row(...)` / `cand(...)` helper; add one matching the fixtures already in that file if it has none.

- [ ] **Step 2: Run them and watch them fail**

Run: `npm test -- src/lib/fbstory/rank.test.ts src/lib/fbstory/ledger.test.ts`
Expected: FAIL — the release still appears in the prompt, and a rejected story is still offerable.

- [ ] **Step 3: Implement**

`ledger.ts`: `const TOLD: LedgerStatus[] = ["draft", "posted", "rejected"];` with a comment saying a human verdict is final while a system release is not.

`rank.ts`: change the skipped section to filter on `status === "rejected"` and reword its heading, and add a comment recording why:

```ts
  // Only a human verdict teaches anything. `skipped` is a SYSTEM release — a Slack
  // failure, or a row freed by hand — and it used to land here under "rejected by a
  // human". On 2026-09-02 a release note reading "Eugene rated this the best story
  // so far" was read as Eugene's verdict and the ranker re-picked that chat, saying
  // so in its own reasoning. Releases reach the prompt nowhere.
  const rejected = recent.filter((r) => r.status === "rejected");
```

- [ ] **Step 4: Run and commit**

Run: `npm test`
Expected: PASS.

```bash
git add src/lib/fbstory/ledger.ts src/lib/fbstory/rank.ts src/lib/fbstory/rank.test.ts src/lib/fbstory/ledger.test.ts
git commit -m "fix(fbstory): only a human rejection teaches the ranker"
```

---

### Task 11: An edit is checked before it is stored

**Files:**
- Modify: `src/lib/fbstory/pipeline.ts` (add `editStory`)
- Test: `src/lib/fbstory/pipeline.test.ts`

**Interfaces:**
- Consumes: `loadThreadByIds` from Task 7, `getLedgerRow` from `ledger.ts`.
- Produces: `editStory(storyKey: string, text: string, actor: string): Promise<{ ok: true } | { ok: false; reason: string }>`.

- [ ] **Step 1: Write the failing test**

```ts
// append to src/lib/fbstory/pipeline.test.ts
import { editStory } from "./pipeline";

it("refuses an edit that quotes a member verbatim", async () => {
  vi.mocked(getLedgerRow).mockResolvedValue({
    story_key: "chatA:m0", chat_id: "chatA", chat_name: "MDS DTC/Shopify",
    window_start: "2026-09-05", window_end: "2026-09-05", message_ids: ["m0"],
    draft_text: "fine", why_picked: "", confidence: null, status: "offered", skip_reason: null,
  });
  vi.mocked(loadThreadByIds).mockResolvedValue({
    ...thread,
    messages: [{ ...thread.messages[0], text: "we moved off Gorgias and cut the bill from eighty grand to five" }],
  });
  const res = await editStory("chatA:m0", "They said we moved off Gorgias and cut the bill from eighty grand to five.", "andy@mds.co");
  expect(res.ok).toBe(false);
  if (!res.ok) expect(res.reason).toMatch(/consecutive words verbatim/);
});

it("saves a clean paraphrase", async () => {
  const res = await editStory("chatA:m0", "The move away from that helpdesk took the bill down sharply.", "andy@mds.co");
  expect(res.ok).toBe(true);
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/pipeline.test.ts`
Expected: FAIL, `editStory is not a function`.

- [ ] **Step 3: Implement the edit**

```ts
// src/lib/fbstory/pipeline.ts
/** A human's edit, checked exactly as a model's draft is. Eugene can already edit
 *  freely in the Facebook composer where nothing checks anything — this is the
 *  first time an edited post is checked at all, so it is stricter than the status
 *  quo, not looser. */
export async function editStory(
  storyKey: string,
  text: string,
  actor: string,
): Promise<{ ok: true } | { ok: false; reason: string }> {
  const row = await getLedgerRow(storyKey);
  if (!row) return { ok: false, reason: `no story ${storyKey}` };
  const thread = await loadThreadByIds(row);
  const clean = stripMarkdown(text).trim();
  if (!clean) return { ok: false, reason: "an empty post cannot be saved" };
  // members_named is what the writer declared; an edit may drop a name but never
  // adds one the gate has not already resolved to a real member.
  const gate = checkDraft({ post_text: clean, members_named: [] }, thread, new Set(thread.member_names));
  if (!gate.ok) return { ok: false, reason: gate.reason };
  await sbRequest(`fb_group_posts?story_key=eq.${encodeURIComponent(storyKey)}`, {
    method: "PATCH",
    body: { edited_text: clean, acted_by: actor, acted_at: new Date().toISOString() },
    prefer: "return=minimal",
  });
  return { ok: true };
}
```

- [ ] **Step 4: Run and commit**

Run: `npm test`
Expected: PASS.

```bash
git add src/lib/fbstory/pipeline.ts src/lib/fbstory/pipeline.test.ts
git commit -m "feat(fbstory): an edited post is checked against the real conversation"
```

---

### Task 12: The five staff-gated routes

**Files:**
- Create: `src/app/api/admin/fbstory/generate/route.ts`, `.../rewrite/route.ts`, `.../edit/route.ts`, `.../reject/route.ts`, `.../post/route.ts`
- Create: `src/lib/fbstory/admin-actions.ts` (`rejectStory`, `markPosted`, `parseFbPostId`)
- Test: `src/lib/fbstory/admin-actions.test.ts`

**Interfaces:**
- Consumes: `makeStories`, `claimStories`, `rewriteStory`, `editStory` from Tasks 5–11.
- Produces: `parseFbPostId(url: string): string | null`, `rejectStory(storyKey, reason, actor)`, `markPosted(storyKey, url, actor)`.

- [ ] **Step 1: Write the failing test**

```ts
// src/lib/fbstory/admin-actions.test.ts
import { describe, it, expect } from "vitest";
import { parseFbPostId } from "./admin-actions";

describe("parseFbPostId", () => {
  it("reads a group post id, with or without a trailing slash", () => {
    expect(parseFbPostId("https://www.facebook.com/groups/milliondollarsellers/posts/27114645448212266/")).toBe("27114645448212266");
    expect(parseFbPostId("https://www.facebook.com/groups/milliondollarsellers/posts/27114645448212266")).toBe("27114645448212266");
  });
  it("returns null for anything else", () => {
    expect(parseFbPostId("https://example.com/x")).toBeNull();
    expect(parseFbPostId("")).toBeNull();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npm test -- src/lib/fbstory/admin-actions.test.ts`
Expected: FAIL, cannot resolve `./admin-actions`.

- [ ] **Step 3: Implement the actions**

```ts
// src/lib/fbstory/admin-actions.ts
import { sbRequest } from "@/lib/supabase";

/** The id in a group post URL, so the story can be joined to digest.fb_posts and
 *  its comments. Anything that is not a group post URL is refused rather than
 *  stored — a wrong link is worse than no link. */
export function parseFbPostId(url: string): string | null {
  const m = /facebook\.com\/groups\/[^/]+\/posts\/(\d+)/.exec(url.trim());
  return m ? m[1] : null;
}

export async function rejectStory(storyKey: string, reason: string, actor: string): Promise<void> {
  await sbRequest(`fb_group_posts?story_key=eq.${encodeURIComponent(storyKey)}`, {
    method: "PATCH",
    body: { status: "rejected", skip_reason: reason, acted_by: actor, acted_at: new Date().toISOString() },
    prefer: "return=minimal",
  });
}

export async function markPosted(storyKey: string, url: string | null, actor: string): Promise<void> {
  const now = new Date().toISOString();
  await sbRequest(`fb_group_posts?story_key=eq.${encodeURIComponent(storyKey)}`, {
    method: "PATCH",
    body: { status: "posted", posted_at: now, posted_url: url, acted_by: actor, acted_at: now },
    prefer: "return=minimal",
  });
}
```

- [ ] **Step 4: Implement the routes**

Every route follows `src/app/api/admin/fb-post/route.ts` exactly — same session read, same `isStaffEmail` check, same JSON error shapes. `reject` requires a non-empty reason and returns 400 without one. `post` accepts an absent or empty `url`, but rejects a present one that `parseFbPostId` cannot read. `generate` calls `makeStories({ days: config.fbStory.lookbackDays, max: body.max ?? 3, chatIds, date, excludeStoryKeys })` then `claimStories`, and returns `{ made, rejected, none }` — it never touches Slack.

```ts
// src/app/api/admin/fbstory/reject/route.ts
import { NextRequest, NextResponse } from "next/server";
import { readSessionCookie } from "@/lib/session";
import { isStaffEmail } from "@/lib/staff-otp";
import { rejectStory } from "@/lib/fbstory/admin-actions";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const sess = await readSessionCookie();
  const email = (sess?.email || "").trim().toLowerCase();
  if (!email || !isStaffEmail(email)) return NextResponse.json({ error: "forbidden" }, { status: 403 });

  let body: { story_key?: string; reason?: string };
  try { body = await req.json(); } catch { return NextResponse.json({ error: "bad json" }, { status: 400 }); }

  const storyKey = (body.story_key || "").trim();
  const reason = (body.reason || "").trim();
  if (!storyKey) return NextResponse.json({ error: "story_key required" }, { status: 400 });
  // A reason is the only feedback the ranker ever gets. A one-click reject would
  // teach it nothing, which is how the old skip list became useless.
  if (!reason) return NextResponse.json({ error: "a reason is required" }, { status: 400 });

  await rejectStory(storyKey, reason, email);
  return NextResponse.json({ ok: true });
}
```

```ts
// src/app/api/admin/fbstory/generate/route.ts
import { NextRequest, NextResponse } from "next/server";
import { readSessionCookie } from "@/lib/session";
import { isStaffEmail } from "@/lib/staff-otp";
import { config } from "@/lib/config";
import { makeStories, claimStories } from "@/lib/fbstory/pipeline";

export const dynamic = "force-dynamic";
export const maxDuration = 120; // two model calls, same ceiling as the scheduled route

export async function POST(req: NextRequest) {
  const sess = await readSessionCookie();
  const email = (sess?.email || "").trim().toLowerCase();
  if (!email || !isStaffEmail(email)) return NextResponse.json({ error: "forbidden" }, { status: 403 });

  let body: { chat_ids?: string[]; date?: string; max?: number; exclude_story_keys?: string[] };
  try { body = await req.json(); } catch { return NextResponse.json({ error: "bad json" }, { status: 400 }); }

  if (body.date && !/^\d{4}-\d{2}-\d{2}$/.test(body.date)) {
    return NextResponse.json({ error: "date must be YYYY-MM-DD" }, { status: 400 });
  }
  const max = Math.min(Math.max(body.max ?? 3, 1), 3);

  const { made, rejected, none } = await makeStories({
    days: config.fbStory.lookbackDays,
    max,
    chatIds: body.chat_ids,
    date: body.date,
    excludeStoryKeys: body.exclude_story_keys,
  });
  if (made.length === 0) return NextResponse.json({ ok: true, made: [], rejected, none });

  // Claimed exactly as the schedule claims: the ledger row is written before
  // anyone sees the story, so a second run cannot offer the same thing twice.
  const claimed = await claimStories(made);
  return NextResponse.json({
    ok: true,
    made: claimed.claimed.map((o) => ({
      story_key: o.thread.story_key, chat_name: o.thread.chat_name,
      window_start: o.thread.window_start, window_end: o.thread.window_end,
      signals: o.signals, why: o.pick.why, post_text: o.draft.post_text, tag_line: o.tagLine,
    })),
    rejected: [...rejected, ...claimed.rejected],
  });
}
```

`rewrite`, `edit` and `post` are the same 12 lines of session check and JSON parse as `reject` above, then one call: `rewriteStory(story_key)`, `editStory(story_key, text, email)`, `markPosted(story_key, url, email)`. `rewrite` and `edit` return `{ ok: false, reason }` with status 200 when the privacy check refuses — a blocked edit is a normal outcome, not a server error. `post` returns 400 when `url` is present but `parseFbPostId` returns null.

- [ ] **Step 5: Prove the gate locally**

Run: `npm test && npm run dev`, then:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:3000/api/admin/fbstory/reject -H 'content-type: application/json' -d '{"story_key":"x","reason":"y"}'
```

Expected: `403` with no session cookie. Every one of the five routes must return 403 unauthenticated — check all five before committing.

- [ ] **Step 6: Commit**

```bash
git add src/lib/fbstory/admin-actions.ts src/lib/fbstory/admin-actions.test.ts src/app/api/admin/fbstory
git commit -m "feat(fbstory): staff-gated generate, rewrite, edit, reject and mark-posted"
```

---

# Phase 3 — Registration

### Task 13: The tool exists in the storefront and in Tools Health

The screen's components wait for the design. Its route, its card and its health row do not, and having them first means the design has somewhere to land.

**Files:**
- Create: `src/app/admin/(tools)/stories/page.tsx` (server component: reads the ledger, renders `ToolHeader` and a plain list)
- Modify: `src/lib/tools/storefront-tools.ts`, `src/components/tools/ToolCover.tsx`, `src/lib/tools-health/registry.ts`

- [ ] **Step 1: Add the health registry row**

```ts
// src/lib/tools-health/registry.ts
{ id: "wa-fb-stories", name: "WA → FB Stories", domain: "WhatsApp", platform: "n8n",
  platformId: "iX7cEFrCW5apa7CS", trigger: "scheduled", schedule: "Mon/Wed/Fri 9am ET",
  healthCheck: "run status",
  desc: "Picks the week's best WhatsApp conversation, writes it up and posts a copy-ready card to Slack.",
  docUrl: DOC + "docs/2531q-97677/2531q-60217", live: true },
```

Without this the card reads NOT YET MONITORED, which is why Personas' does.

- [ ] **Step 2: Add the storefront entry**

Append to `STOREFRONT_TOOLS` in `src/lib/tools/storefront-tools.ts`, with `id: "stories"` added to `ToolCoverId` and cover art from the design pass:

```ts
{
  id: "stories",
  name: "WA Stories",
  tagline: "The week's best WhatsApp conversation, written up for the Facebook group.",
  meta: "RAN 9:00AM · MON/WED/FRI",
  badge: "new",
  url: "/admin/stories",
  keywords: ["facebook", "post", "story", "whatsapp", "share", "group", "draft", "paste", "publish"],
  doc: {
    what: "Turns one WhatsApp conversation into a ready-to-paste Facebook group post, three times a week, and records which one was actually posted.",
    when: "When you want to post to the group and would rather start from something real than a blank box, or when you want to know whether the pilot is working.",
    sources: ["digest.summaries", "digest.wa_messages", "anthropic", "n8n · Mon/Wed/Fri 9am ET"],
    wrong: "If a story reads thin, check the signals line under it — it says how many people spoke and whether a question got answered. A quiet week genuinely produces less; the pipeline is allowed to return nothing.",
    related: ["whatsapp", "facebook"],
    how: [
      "Three times a week the pipeline reads the last seven days of chat summaries and ranks the conversations against each other.",
      "It writes the best few as plain-text posts, checks each one for quotes and for names that are not members, and posts them to Slack as options.",
      "You copy one into the Facebook group by hand — Meta removed API publishing for groups in 2024 — then mark it posted here.",
    ],
    faq: [
      ["Why can it not post to Facebook itself?", "Meta removed Groups API publishing in 2024. No credential exists that could do it, so the paste is permanent."],
      ["Why are members never quoted?", "The rule is named and paraphrased: members get credit, their exact words stay in the chat. It is enforced in code, and it blocks a draft that reuses eight consecutive words."],
      ["Can I write about any chat?", "Any except Centurion 20M+ and Credit Card & Travel Hacks. The first is a revenue-gated tier and posting it gives away what members pay for."],
    ],
  },
},
```

- [ ] **Step 3: Add the route**

Scaffolding for the design to land on, not the design. No new components — `KIT.md` is explicit
that a screen growing its own header, table, tile or popup is rejected at review.

```tsx
// src/app/admin/(tools)/stories/page.tsx
import { ToolHeader } from "@/components/tools/ToolHeader";
import { loadRecentLedger } from "@/lib/fbstory/ledger";

export const dynamic = "force-dynamic";

export default async function StoriesPage() {
  const rows = await loadRecentLedger(60);
  return (
    <>
      <ToolHeader name="WA Stories" onHelp={undefined} />
      <main style={{ padding: 24 }}>
        {rows.length === 0 ? (
          <p>No stories yet. The next run is Monday, Wednesday or Friday at 9am ET.</p>
        ) : (
          <ul>
            {rows.map((r) => (
              <li key={r.story_key}>
                {r.chat_name} · {r.window_start} · {r.status}
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  );
}
```

Read `src/app/admin/(tools)/whatsapp/page.tsx` first — `KIT.md` names it the reviewed reference
for how a tool screen is wired, including how `ToolHelpProvider` supplies `onHelp`.

- [ ] **Step 4: Verify in the browser**

Start the dev server and check `/admin` shows the new card with a live eyebrow rather than NOT YET MONITORED, and that `/admin/stories` lists the ledger rows. Take a screenshot for the ticket.

- [ ] **Step 5: Run everything and commit**

Run: `npm test && npx next build`
Expected: PASS and a clean build.

```bash
git add src/lib/tools/storefront-tools.ts src/lib/tools-health/registry.ts src/components/tools/ToolCover.tsx "src/app/admin/(tools)/stories"
git commit -m "feat(admin): register the WA Stories tool"
```

---

## Done means

- `npm test` green, `npx next build` clean.
- The scheduled Mon/Wed/Fri card is byte-identical in shape to today's — proven by a live dry run before and after.
- A story built from a chosen chat, a rejection with a reason, a refused edit and a mark-posted with a real Facebook link, all four demonstrated live and quoted in the ticket close.
- `db/` re-exported and committed; the #65 drift alarm silent.
- `FB_BACKLOG.md` #5 closed with before/after numbers; the new tool's ticket opened and closed with the same format.
- `WA_FB_STORY_POSTS.md`, `SESSION_LOG_MISC.md`, the `SESSION_LOG.md` index line and the memory entry all updated in the same branch.
