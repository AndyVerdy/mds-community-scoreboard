# WA Stories — phased delivery

**Date:** 2026-09-08
**Design:** `WA Stories.dc.html` + `WA-STORIES-LOGIC.md` (Andy, 2026-09-08, in the export zip)
**Spec:** `2026-09-07-wa-stories-admin-tool-design.md` · **Task detail:** `2026-09-07-wa-stories-admin-tool.md`

Andy's instruction: deliver in phases, trim the complex parts, work locally first. This document is
the split. Each phase is a ticket that ships and is proved on its own.

## Where the design and the running system disagree

Found by checking `WA-STORIES-LOGIC.md` against live. None of these are design mistakes — they are
things the design could not know. Fix the copy, or the system, before building on them.

| The doc says | Live reality | What to do |
|---|---|---|
| Runs fire **06:00 ET** | n8n `iX7cEFrCW5apa7CS` is `0 9 * * 1,3,5` — **09:00 ET**. The screenshot's chips read `RUN 06:00` | Change the screen's copy, or move the cron. Andy's call |
| A run reads **the last three days** | `FB_STORY_LOOKBACK_DAYS` defaults to **7** | Copy fix, unless we want 3 |
| **One call to rank, one to write** | One rank call, then **one write call per story** — three writes for three options | Copy fix. Matters because Generate's cost is four model calls, not two |
| Stories belong to a **run** with an id, a sequence and an off-schedule flag | **There is no run in the data.** Rows are grouped only by `created_at` | Real gap — add `run_id`. Backfill is safe: the 8 existing runs each land inside 0.42s |
| States are `available` / `posted` / `rejected` | Also `blocked` (the privacy gate refused it) and `skipped` (a system release) | Decide what the screen does with those two. Recommendation below |
| Reject needs a reason | Matches the spec, and the doc adds a floor of **8 characters** | Take the floor |
| **Put it back on offer** un-rejects a story | Not in the spec | Take it — it is one route and it makes a required reason safe to type |
| Generate takes a **date range** | The spec had chats plus one optional day | Take the range. It replaces `date` with `from`/`to` |
| Generate shows **per-chat message volume for the range** before you run it | No endpoint exists for that | New read. It is what makes a refusal legible in advance |

On `blocked` and `skipped`: keep them off the Stories tab and out of run chips. A story the gate
refused was never offered to anyone, and a system release is bookkeeping. Both belong in Reports
later, if anywhere. Say so on screen nowhere — silence is correct for a state the reader cannot act on.

## The phases

### Phase 0 — #5, the wrong 24 hours

Already specified as Tasks 1–4 of `2026-09-07-wa-stories-admin-tool.md`. The ranker chooses a
conversation from a digest day, the writer fetches a UTC calendar day, and the two overlap by 13
hours. Nine of the eleven stories offered since the rebuild were written from a different message set
than the one ranked; one was written from a single message.

**Why first:** every later phase displays, generates or reports on these stories. A screen showing a
post built from one message is a nicer view of the same bug.

**Out:** nothing. It is four tasks and it closes a filed S2 ticket.

---

### Phase 1 — Read and record

The screen, with no model calls anywhere in it. This is the phase that closes the loop: `posted_at`
is null on all 14 rows today, so nobody can say what reached Facebook.

**In:**
- `run_id` on `digest.fb_group_posts`, set by the pipeline, backfilled by grouping `created_at`.
- The rest of the ledger columns and the `rejected` status (Task 9 of the task plan).
- `/admin/stories`, Stories tab: run strip with Latest, `‹ ›`, chips and All N runs; story rows with
  the post text, the right rail (chat, measured, why, tag when posting); archive presentation past 21 days.
- **Copy the post** — the preamble is dimmed on screen and included in the copy.
- **Mark posted**, link optional, and *paste or replace the link later*.
- **Reject** with a reason of 8 characters or more, and **Put it back on offer**.
- Storefront card and the Tools Health row.

**Out:** Generate, Reports, results read-back, Edit, Rewrite, Find another. Every one of those is a
model call, a new endpoint or a third-party read; none is needed to record what happened.

**Proved by:** marking one real story posted with its Facebook link, rejecting one with a reason,
putting it back, and a SQL read showing `posted_at`, `posted_url`, `acted_by` and `run_id` populated.

---

### Phase 2 — Generate

**In:** the pipeline extraction (Tasks 5–8), the date range, the chat picker with per-chat volumes for
that range, the refusal path that returns real counts and records nothing, and the off-schedule run
filed with its own timestamp.

**Out:** still no Reports, no results, no Edit or Rewrite.

**Note on cost:** a Generate is one rank call plus one write call per story — up to four model calls,
not the two the design doc assumes.

---

### Phase 3 — Edit, Rewrite, Find another

**In:** `loadThreadByIds`, `rewriteStory`, `editStory` with the privacy check on save (Tasks 7 and 11),
and the three routes. The check names the offending run of words back to the editor.

**Out:** Reports and results.

---

### Phase 4 — Results and Reports

The two things Andy named as trimmable, together and last.

**In:** parse `posted_url`, join `digest.fb_posts` and count `digest.fb_comments` for comments and time
to first comment; reactions and reach render as `NOT CAPTURED`, never as zero. The Reports tab with
month pills, the posted and rejected tables, sorting and paging.

**Why last:** it answers "did the pilot work", which needs posted stories with links to exist first.
Phase 1 starts collecting them.

## Working locally

`npm run dev` in `mds-digest-web`. Two things to know before touching a button:

- **There is no local database.** Local dev reads and writes the live `digest` schema, so Mark posted
  and Reject on a real story are real. Test writes belong on a throwaway ledger row, or on a story
  already rejected.
- **Local dev has no admin session** unless you sign in through the OTP flow. The admin layout
  redirects and every write route returns 403 without an `@mds.co` session — that is the behaviour to
  verify first, not to work around.
- The scheduled route stays safe to exercise with `?dry=1`, which computes a real pick and writes nothing.
- Merging to `main` in `mds-digest-web` **is** the production deploy. Local proof, then merge.
