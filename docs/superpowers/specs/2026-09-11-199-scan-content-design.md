# Team research — `scan_content`: read every message of a member set for a trait — design

**Ticket:** #199 · **Repo:** `mds-digest-web` only (the Team runtime; no n8n edit, no new SQL function, no new
grant) · **Status:** design approved in conversation 2026-09-11, spec awaiting Andy's read.

## Goal

Staff ask a question about what a set of members has said anywhere — "who attended Inspire 2026 and is thinking of
moving to Miami", "who mentioned hiring a COO", "who sounds burned out" — and get a complete tally with names, dates
and quotes, not a sample. The question is never known in advance; Millie builds the row set for it herself, and the
tool reads every row. Cost is estimated before any reading, capped, and shown.

## What exists today (verified live 2026-09-11)

- Team research mode (#172) is a `claude-sonnet-5` tool loop in `src/lib/millie/team/` with four tools:
  `sql_query` (one read-only SELECT through `digest.team_sql`, which runs as the read-only role and returns at most
  **500 rows** per call), `schema_catalog`, `semantic_search`, and `web_thread_search` (#170). It finds a concept by
  words or by meaning and reads the hits. It does not read every message of a set.
- The corpus is complete: `digest.content_items` holds 59,904 rows (WhatsApp 17,750 · Facebook comments 16,454 ·
  call-transcript chunks 13,507 · applications 6,535 · Facebook posts 4,280 · digests 1,378), every row ≥ 30
  characters embedded except the day's lag. Each row carries `source`, `kind`, `body`, `occurred_at`, `url`,
  `meta` (with the author's `at_member_id` where known). Last 30 days of WhatsApp ≈ 4,100 rows.
- Andy's live scope check (2026-09-11): the Miami question ran 24 queries, 14 laps, 112 s, $0.87 and returned an
  honest no-match — because it searched, then read hits.
- Budgets already in force per asker per UTC day: `MILLIE_TEAM_DAILY_TURNS` (40) and `MILLIE_TEAM_DAILY_USD` (10),
  both read off `metrics.cost_usd` of the logged turns.

## Decisions (Andy, 2026-09-11, verbatim where quoted)

| # | Decision | Words |
|---|---|---|
| D1 | The tool must generalise: Millie analyses the question and builds the query herself; nothing per request | "we can't even predict these requests now. So is there a way to analyze the question and build custom DB queries?" |
| D2 | Cost is controlled, not just reported | "also, super important to control cost." |
| D3 | The row set comes from a SQL SELECT Millie writes, the same way she writes `sql_query` today | agreed in conversation ("SQL-in") |
| D4 | No partial tally is ever presented as complete | ticket AC 2 |

## Architecture

### The tool, as the model sees it

```
scan_content({
  sql: string,            // read-only SELECT returning: id, member, at_member_id, occurred_at, text, url, source
  question: string,       // the trait to judge each row for, as a yes/no question
  max_cost_usd?: number,  // default 2, hard ceiling 5 — only raised when the asker said so
})
→ {
  complete: boolean, scanned: number, total_rows: number, cost_usd: number, batches: number,
  refused?: "too_many_rows" | "over_budget", estimate?: { rows, est_cost_usd },
  members: [{ member, at_member_id, yes, unsure, no,
              quotes: [{ date, quote, url, source }] }],   // ≤ 3 quotes each, yes before unsure
  unattributed: { yes, unsure, no }                         // rows with no member
}
```

The description tells the model when to reach for it: a trait that no column holds, asked over a SET of people —
after the set has been chosen with SQL. It is not for questions a column answers (status, revenue band, city) and not
for "find a mention of X" (that is `sql_query` full-text or `semantic_search`).

### How a scan runs (`src/lib/millie/team/scan.ts`, new)

1. **Guard the SQL** with the existing `guardSql` (one SELECT/WITH, no writes), then probe its shape with
   `select * from (<sql>) q limit 1` through `team_sql`: the seven columns must be present; a missing one returns a
   tool error naming it, so the model repairs the query.
2. **Count and estimate** before reading anything: `select count(*) as n, coalesce(sum(length(text)),0) as chars
   from (<sql>) q`. Estimated cost = chars ÷ 4 tokens at the Haiku input price, plus ~20 output tokens per row, plus
   the rubric once per batch. If `n > 5,000` → refused `too_many_rows`; if the estimate exceeds `max_cost_usd` →
   refused `over_budget`, both returning the count and the estimate so the answer can say how to narrow the set.
   Nothing is read, nothing is charged.
3. **Page the rows** through `team_sql` in keyset pages of 500 (`… where id > <last> order by id limit 500`) —
   `team_sql`'s own cap, no new function. Rows with empty `text` are skipped and counted.
4. **Classify in batches of 40** with `claude-haiku-4-5`, four batches in flight at a time. Each batch is one call:
   a fixed system rubric (cache_control on it) + the question + the rows numbered 1..N. The model returns one JSON
   line per row: `{ "n": 1, "verdict": "yes" | "no" | "unsure", "quote": "…" }`. Rows are numbered locally and
   mapped back locally — never by echoed ids ([[reference_llm_judge_rewrites_echoed_ids]]). A quote is kept only if
   it is a verbatim substring of the row's text ([[reference_llm_judge_quotes_need_validation]]); otherwise the
   verdict stands and the quote is dropped. A batch that fails to parse is retried once, then counted as unscanned.
5. **Stop honestly.** A per-scan wall cap of 240 s (inside the loop's 8-minute cap): when it is hit, or a batch
   failed twice, the tally is returned with `complete: false` and the real `scanned` vs `total_rows`.
6. **Tally** per member: yes / unsure / no counts, the top three quotes (yes first, newest first), sorted by yes
   descending; rows without a member go to `unattributed`. The payload is clipped at the tools' 48,000-character cap
   like every other tool result.

### Cost, three layers

- **Before:** the estimate + `max_cost_usd` (default 2, ceiling 5) — a scan never starts without knowing its price.
- **During:** real usage is summed per batch (`costUsd("claude-haiku-4-5", usage)`, prices added to `pricing.ts`:
  $1 in / $5 out per MTok, cache read 0.1×, cache write 1.25×) and the scan aborts the moment the running cost passes
  `max_cost_usd` × 1.1 — returning `complete: false`.
- **After:** the scan's cost goes on its trail step (`TrailStep.cost_usd`) and the loop adds every tool step's cost
  into the turn's `cost_usd` (`loop.ts` today sums only the Sonnet usage). `metrics.cost_usd` therefore carries it,
  so the per-asker daily budget counts scans with no change to `gate.ts` or `dailySpend`.

Reference: 4,100 WhatsApp rows ≈ 300k input tokens ≈ $0.30 + $0.40 output ≈ **$0.70**; 103 batches, ~90 s at four
in flight.

### What the answer must say (behaviour rules, `loop.ts` BEHAVIOUR block)

- After a scan: the tally with names, quotes and dates, then one line "read N messages (M sources, date range), cost
  $X"; when `complete` is false: "read N of M messages — partial", never a total.
- After a refusal: the count and the estimate, and one concrete way to narrow (fewer people, a shorter window, one
  source), then wait — do not silently re-run a narrower scan.
- Choose the set with SQL first (attendees × their messages, a chapter × WhatsApp, applicants since a date); scan
  second; never scan the whole corpus for a question a column answers.

### The trail and the page

`TrailStep.tool` gains `"scan"`; the step carries `sql`, `rows` (scanned), `cost_usd`, `input: { question,
max_cost_usd }`, `error` on refusal. The Ask Millie trail renders it like a query step with its cost; the sources
popup shows the SQL. No other UI change.

### Isolation

The tool exists only in the Team tool set (`tools.ts`), like `web_thread_search`: the n8n graph never loads it, a
WhatsApp turn cannot reach it. The only database access is `team_sql` (read-only role, already granted): no new
function, no new grant, no n8n edit — the leak gate's #172 section is untouched.

## Error handling

| Case | Behaviour |
|---|---|
| SQL fails the guard or lacks a required column | tool error naming the problem; the model repairs and retries (as `sql_query` today) |
| `team_sql` errors on the count or a page | tool error with the verbatim Postgres message; nothing charged |
| Over 5,000 rows or over `max_cost_usd` | refused with count + estimate; nothing read |
| Haiku returns unparseable output for a batch | one retry, then the batch is unscanned; `complete: false` |
| Running cost passes the cap, or 240 s | stop; return the partial tally with `complete: false` |
| Quote not found verbatim in the row | quote dropped, verdict kept |

## Testing

Vitest beside the existing Team tests:

1. Column probe: a SELECT missing `text` returns an error naming `text`; nothing else runs.
2. Estimate: 6,000 rows → `too_many_rows`; 4,000 rows × 300 chars at the Haiku price → within 10 % of the hand
   figure; over `max_cost_usd` → `over_budget`; in both refusals the classifier is never called.
3. Paging: 1,250 rows arrive as three `team_sql` calls with `id >` cursors; a row with empty text is skipped and
   counted.
4. Classification: rows numbered 1..40 in the prompt; a verdict for `n: 7` maps to the seventh row; a quote that is
   not a substring is dropped; an unparseable batch is retried once then marked unscanned.
5. Cost: the trail step's `cost_usd` equals the summed batch usage at the Haiku price, and the loop's `cost_usd`
   equals Sonnet usage + tool costs.
6. Stop: a fake clock past 240 s returns `complete: false` with the rows scanned so far.
7. Tally: yes counts, ≤ 3 quotes per member ordered yes-first newest-first, unattributed rows separated.

## Proof for the acceptance criteria

| AC | How it is proven |
|---|---|
| 1 · Andy's example returns every attendee who said it, with quotes, dates and the count scanned | seed a known set: 6 real Inspire 2026 attendees (from `event_registrations`), 4 planted "moving to Miami" messages in a probe thread that the SQL selects alongside their real WhatsApp rows; the probe harness (`scripts/olivia_team_probe.ts`) asks the Miami question; the answer names exactly the planted four with their quotes and states the rows read; seed removed after |
| 2 · a scan it cannot finish says so | force `max_cost_usd: 0.05` on a 4,000-row set → refused with the estimate; force the wall cap to 5 s → `complete: false` and the answer says "read N of M — partial" |
| 3 · cost on the trail and in `metrics`; 30-day WhatsApp scan under $5 | a real 30-day WhatsApp scan through the harness: trail step `cost_usd`, `metrics.cost_usd` includes it, the number printed |
| 4 · leak gate #172 section green, no grant, no n8n edit | `scripts/olivia_leak_gate.py` exit 0; `db/` export unchanged; the graph JSON untouched |

## Out of scope

A structured filter language (D3 rules it out) · scanning sources outside `content_items` (form answers are
structured — SQL answers them) · pre-filtering by keyword or meaning before the read (that is what the tool exists
to avoid; it can be added later as an option if cost demands it) · Airtable payment history (the "past due more than
twice" probe needs a table the mirror does not hold — separate ticket) · the event-spend field trap found by the
probe (`Event Cost (Expense)` vs `Event Revenue` — separate ticket).
