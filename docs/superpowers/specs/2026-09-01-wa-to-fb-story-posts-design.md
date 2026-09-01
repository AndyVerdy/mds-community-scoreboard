# WA → FB Story Posts — Design

**Date:** 2026-09-01
**Project:** MDS WA Digest (sister project — keep separate from Engagement and Approvals)
**Status:** Design approved, not yet planned or built

## Problem

MDS members talk in 18 WhatsApp chats. The Facebook group is the one surface every
member sees. Good threads happen in WA and members who are not in that particular
chat never learn they happened.

The goal is a shared record: post to the FB group, regularly, about interesting things
that happened in the WA chats, so nobody misses the good stuff.

## Decisions

These were settled with Andy on 2026-09-01 and are inputs to the design, not open
questions.

| Decision | Choice |
|---|---|
| Destination | The private FB group `699138040189700` — members-only audience |
| Purpose | Nobody misses the good stuff; FB group as the shared record |
| Post shape | Story spotlight — one thread per post, 2–3 per week |
| Attribution | Named, paraphrased. Members credited by name, no verbatim quotes |
| Cadence rule | Ceiling, not a schedule. Quality-gated; a thin week posts less |
| Approval loop | Slack card in `#automation-tests` (`C0AQ8USNQK0`), Andy copies and pastes |
| Selection | Shortlist from summaries, write from raw messages |
| Runtime | Render, in `mds-digest-web` |

### Why a human posts

Meta removed Groups API publishing in 2024. There is no credential anywhere in the
repo or environment that can publish to a Facebook group, and none can be obtained.
The human paste is a hard constraint, not a shortcut — so the system is designed to
make that paste as cheap as possible rather than to work around it.

### Why Render rather than n8n

`mds-digest-web` already holds every credential this needs: `SUPABASE_URL` /
`SUPABASE_SECRET_KEY`, Slack bot tokens, and an Anthropic key. `/api/health/report`
is the same shape already working in production — a secret-gated GET with a `?dry=1`
mode that posts to Slack, driven by the n8n workflow `argZgYHPgdVKJqCS`
("MDS Platform Health → Slack"). This is a clone of a proven pattern.

Keeping the logic in Render also keeps it off the n8n execution quota, which took
production down for 13 minutes on 2026-08-28.

## Data

Everything this needs is already in the `digest` schema of Supabase project
`nadtudwuwjhckotrngzn`. No new ingestion, no Airtable reads, no Whapi calls.
Verified live 2026-09-01:

- `digest.summaries` — 2,194 rows, latest `2026-08-31`. 126 daily rows in the last
  7 days, which is exactly 18 chats × 7 days, so coverage is complete.
- `digest.wa_messages` — 16,004 rows, latest `2026-09-01 08:23 UTC`. Carries
  `reply_to`, `sender_member`, `sent_at`, `text`, `chat_id` — enough to reconstruct a
  thread.
- `digest.chats` — chat names and ids.
- `digest.members` — used to validate that a name in a draft is a real member.

Airtable stays read-only throughout. The ledger below lives in Supabase, which is a
layer we own.

## Architecture

One new route in `mds-digest-web`:

```
GET /api/fbstory/draft?secret=…[&dry=1][&days=7]
```

Secret-gated by `FB_STORY_SECRET` rather than an admin session, because a scheduler
calls it. Modelled directly on `src/app/api/health/report/route.ts`.

The trigger is a small n8n schedule workflow — Schedule node → HTTP Request GET —
firing Mon/Wed/Fri at 9am ET. n8n holds no logic and no prompt; if it is ever lost,
the route can be curled by hand.

### Modules

Each piece is separately testable and does one thing.

- `src/lib/fbstory/candidates.ts` — reads the last N days of daily summaries from
  Supabase, drops chats on the blocklist, drops story keys already in the ledger.
  Returns candidate summaries. No LLM.
- `src/lib/fbstory/rank.ts` — one Claude call. Input: candidate summaries plus recent
  skip reasons. Output: `{ chat_id, window_start, window_end, topic, why, confidence }`
  or `{ none: reason }`. It does not mint the story key — it works from summaries and
  has no message ids. No writing.
- `src/lib/fbstory/thread.ts` — given the winner, pulls that chat's raw messages for
  the window from `digest.wa_messages` and orders them into a thread using `reply_to`.
  Also mints the story key. No LLM.
- `src/lib/fbstory/write.ts` — one Claude call, structured output. Input: the thread.
  Output: `{ post_text, members_named: string[] }` — the post itself plus an explicit
  declaration of every member it credits, so the gate has something exact to check
  instead of guessing at capitalised words. Named, paraphrased, roughly 100–150 words,
  story arc, closing question to the group.
- `src/lib/fbstory/gate.ts` — deterministic privacy checks. No LLM. See below.
- `src/lib/fbstory/ledger.ts` — reads and writes `digest.fb_group_posts`.
- `src/lib/fbstory/slack.ts` — builds and posts the Slack card.

The route composes these and owns no logic of its own beyond ordering and error
handling.

## Flow

1. Load candidates. Last 7 days of daily summaries, minus blocklisted chats, minus
   story keys already in the ledger.
2. Rank. Claude returns one winner with a confidence, or `none`.
3. If `none`, or confidence is below `FB_STORY_MIN_CONFIDENCE` (default `0.7`): post a single quiet line to
   `#automation-tests` — "2026-09-03: nothing cleared the bar (18 chats, 4 active)" —
   and exit 200. **Silence must always mean broken, never quiet.** This is the
   deliberate cost of choosing a ceiling over a schedule.
4. Load the winning thread's raw messages and mint the story key. If that key is
   already in the ledger, stop and log — this is the authoritative dedupe check, and
   it is what makes "no story is told twice" true rather than approximate.
5. Write the post.
6. Run the privacy gate. A failed gate does not post a card; it logs the reason and
   writes a `blocked` ledger row so the failure is visible rather than silent.
7. Post the Slack card.
8. Write the ledger row with status `draft`.

## Privacy gate

Named-and-paraphrased is the rule most likely to become an actual incident if it
slips, so it is enforced in code and not in the prompt. Standing rule: two failed
prompt rules means the rule moves into the tool.

- **No verbatim quotes.** Reject the draft if any run of 8 or more words appears
  verbatim in a source message, compared case-insensitively with punctuation and
  whitespace normalised.
- **Real members only.** The gate checks the `members_named` list that `write.ts`
  declares, not capitalised words in the prose — a naive capitalisation scan would fire
  on every sentence opener and every brand like Zcash or MSTR. Two checks: every
  declared name must resolve to a member in `digest.members`, and no member name
  present in the source thread may appear in `post_text` without being declared. An
  unresolvable name blocks the draft rather than being silently stripped, because a
  hallucinated name means the write step went wrong.
- **Chat blocklist.** Chats excluded from this feature never reach the ranker. The
  list is a config constant in the repo, overridable by `FB_STORY_EXCLUDED_CHATS`,
  filtered in `candidates.ts` before any LLM sees the data. Airtable schema is not
  touched.

The blocklist ships empty — all 18 active chats are eligible. Excluding a chat later
is an env-var edit and a redeploy, not a code change.

## Ledger

New table `digest.fb_group_posts`:

| Column | Type | Note |
|---|---|---|
| `story_key` | text, primary key | `chat_id` + `:` + the id of the thread's root message. Anchored to a message rather than to a date window, so the same thread resurfacing in a later window resolves to the same key and cannot be told twice |
| `chat_id` | text | |
| `chat_name` | text | |
| `window_start`, `window_end` | date | The days the story was drawn from |
| `draft_text` | text | |
| `why_picked` | text | The ranker's reasoning, for tuning |
| `confidence` | numeric | |
| `status` | text | `draft` \| `posted` \| `skipped` \| `blocked` |
| `skip_reason` | text | Free text from the Slack Skip button |
| `created_at`, `posted_at` | timestamptz | |

Skipped rows and their reasons are fed back into the ranker prompt on later runs, so
rejecting a dud teaches the system rather than being thrown away.

## Slack card

Posted to `#automation-tests` (`C0AQ8USNQK0`) using the existing bot-token pattern in
this repo. The card carries:

- the draft in a code block, so it copies clean into the FB composer
- source chat, date window, and the ranker's one-line reason for picking it
- two buttons: **Mark posted** and **Skip**

Buttons hit `/api/fbstory/interactivity`, following the shape already working in
`src/app/api/centurion/interactivity/route.ts`. **Skip** opens a short reason prompt;
the reason lands in the ledger.

## Error handling

- Supabase or Anthropic failure: return 500 with the error, and post a failure line to
  `#automation-tests` so a broken run is as visible as a quiet one.
- Gate failure: 200, no card, `blocked` ledger row, reason logged.
- The route is idempotent per story key — the ledger's primary key means a double-fire
  cannot produce two cards for the same story.

## Testing

- `?dry=1` returns the ranked pick, the draft, and the gate result as JSON and posts
  nothing. This is the proof artifact for closing the ticket.
- Unit tests on `gate.ts` — the verbatim-run detector and the name resolver are pure
  functions with obvious cases.
- Unit test on `thread.ts` — `reply_to` ordering, including messages with no parent.
- A 30-day backfill run over existing summaries produces roughly a dozen sample drafts
  to read before Slack ever sees one.

## Out of scope

- Publishing to Facebook automatically. Not possible; see above.
- Posting to a public FB Page.
- A `digest.mds.co` admin UI for the queue. Slack is the surface.
- Weekly roundups. The shape is the story spotlight.
- Changing the existing daily or weekly WA digests in any way.

## Success criteria

- Runs Mon/Wed/Fri without a manual trigger.
- A run either produces a card or says out loud that it produced nothing.
- Drafts are pasteable with no edit more often than not.
- No draft has ever reached Slack containing a verbatim quote or a non-member name.
- No story is told twice.
