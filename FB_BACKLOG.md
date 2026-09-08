> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Facebook stream — backlog

Covers the Facebook surfaces: group capture (`digest.fb_*`), the admin report tab
(`/admin/facebook`), and WA → FB story posts (`/api/fbstory/*`).

Structure: **OPEN — ARCHITECTURE** first, then **OPEN — THE REST**, then **CLOSED**.
A ticket's block moves between sections; it is never copied.

---

## OPEN — ARCHITECTURE

### #1 · 🔑 Facebook posts don't reach the member spine for 11 real members · 🔴 S1

**Story.** As MDS, we want every Facebook group post attributed to the member who wrote
it, so that engagement scoring, the admin report and the WhatsApp stories all credit the
right person — and so a member's activity is never invisible because of a missing join.

**Measured 2026-09-02 (live):** 284 posts in the last 30 days; **246 reach the member
spine (87%)** via `fb_member_map.at_member_id` → `member_profiles`. The 38 that don't come
from **13 distinct authors with no `fb_member_map` row at all**:

| Author | Posts (30d) |
|---|---|
| Dan Wills | 13 |
| Ivan Ong | 9 |
| Million Dollar Sellers | 4 · *not a person — the group's own account* |
| Mouad Errafik | 3 |
| EJ Ball · Matthew Verde · Mirzad De · Ruben Alikhanyan · Abe Indig · Tamkin Amin Collins · Ben Pearson · Chris Kjeldsen | 1 each |
| Anonymous member | 1 · *unresolvable by design — FB anonymous posting* |

So **11 real people**. EJ Ball is the diagnostic case: he IS a member with a Facebook
profile link on file, so the break is the FB-uid → member mapping, not the member record.

**Acceptance criteria**
1. Each of the 11 either resolves to an `at_member_id`, or is recorded with a stated
   reason why it cannot (e.g. no FB profile link in Airtable, duplicate/ambiguous uid).
2. "Million Dollar Sellers" and "Anonymous member" are classified explicitly as
   not-a-member rather than counted as misses, so coverage stops being flattered or
   penalised by them.
3. Coverage re-measured over the same 30-day window: before **246/284 (87%)**, after
   stated. Every author counted once.
4. The root cause is named per member — a missing `FB Profile Link` in Airtable is a
   different fix from a missing `fb_member_map` row, and the two need different owners.
5. **No Airtable writes by the agent.** Where the fix belongs in Airtable, name the record
   and the field and hand it to Andy or ops.

**Notes.** `fb_member_map` is the FB-capture stream's table. ⚠️ There are ~737 duplicate
`Member ID (FB)` values in Airtable `tblVc38gw21iHLYMG` (long-standing, uninvestigated) —
worth checking whether they overlap these 11 before hunting individually. Join against
`member_profiles`, **not** `digest.members`: the latter is the WhatsApp mirror and reports
a misleading 72%.

---

## OPEN — THE REST

### #5 · ⏱️ The story is written from the wrong 24 hours — the thread window is the UTC calendar day, the summary is a digest day · 🟠 S2

**Story.** As the person posting a WhatsApp story, I want the post written from the whole
conversation the ranker picked, so that a story never reads thinner than the chat it came
from — and never quietly blends in the previous day's conversation.

**Measured 2026-09-07 (live).** The ranker chooses from `digest.summaries`, whose `date` is a
*digest* day: the 06:05 CDT digest labels the previous 24 hours with the previous date (Slack:
"MDS Daily Digest · 2026-09-05" was posted 09-06 06:04 CDT), so summary `D` holds messages from
roughly `D 11:00 UTC` to `D+1 11:00 UTC` (DTC 09-05: 6 text messages on 09-05 18:00–23:59 UTC
plus 10 on 09-06 00:00–02:59 UTC = the summary's 16). `thread.ts` `loadThread` and `signals.ts`
then fetch `D 00:00:00Z`–`D 23:59:59Z`. The two overlap for 13 hours: the US evening (from
20:00 ET) is cut off and the previous digest day's morning is pulled in.

Of the 11 stories offered or drafted since the 2026-09-02 rebuild, **9 were written from a
message set that differs from the summarised conversation**; only Retail 09-04 (9 = 9) and
AI 08-28 (8 = 8) matched.

| Card | Chat · summary day | Summary msgs | Thread msgs | What the writer saw |
|---|---|---|---|---|
| 09-02 and 09-04, Option 2 | DTC/Shopify · 08-30 | 14 | **1** | EJ Ball's single Kendall message; the helpdesk conversation Eugene rated best sits at 08-31 06:00–08:00 UTC and never reached the writer |
| 09-07 Option 1 | DTC/Shopify · 09-05 | 16 | **8** | half the AOV/bundle exchange — the 10 messages after 00:00 UTC were cut, 2 from 09-05 03:00 UTC (the previous day) were added |
| 09-07 Option 2 | AI & Automations · 09-04 | 45 | **67** | the previous digest day's morning blended in |

The one-message Kendall "story" was offered twice as a five-paragraph post, with signals
reading `1 messages, 1 people`. Nothing after the thread is built checks that it is still a
conversation: `MIN_MSGS = 5` in `candidates.ts` applies to the summary row only. `pickRoot`
mints the story key from these messages, so the key — and dedupe — moves with the window too.

**Acceptance criteria**
1. The thread window and the signals window equal the summary window for that chat-day. The
   digest's real boundary is read from the digest workflow (`qo3qzeVtprhTW88F`), stated in the
   close, and defined ONCE, shared by `thread.ts` and `signals.ts`.
2. Re-measured on the 11 rows above with `?dry=1&asof=`: every thread's message ids fall inside
   its summary window; the DTC 08-30 pick builds the 14-message helpdesk thread and the DTC
   09-05 pick the 16-message AOV thread. Before **2 of 11** match, after stated.
3. A built thread with fewer than 5 text messages or fewer than 2 voices is never written or
   offered; the run says so in its Slack no-pick line.
4. Dedupe holds across the change: the two already-correct threads keep their story keys; the
   one-message row is released (`skipped`), not left `offered`.
5. Before/after drafts for the 09-07 DTC pick shown side by side in the close — the story, not
   just the counts.

---

### #6 · 🗣️ The ranker reads every `skipped` row as a human rejection · 🟡 S3

**Story.** As MDS, we want the ranker to learn only from what a human actually rejected, so
that a bookkeeping release or a Slack failure never teaches it that a story was bad — or good.

**Seen live 2026-09-04.** `rank.ts` lists every `skipped` ledger row in the prompt as
`picked for "…" — rejected because "<skip_reason>"`. The 2026-09-02 release of the helpdesk
story carried *"Released 2026-09-02: Eugene rated this the best story so far … Freed so the
current pipeline can rewrite it properly."* The ranker took it as instruction and re-picked
DTC 08-30, its `why_picked` ending *"Human already rated it the best story; needs the
rewrite."* — and the pick landed on the one-message thread (#5). `route.ts` writes `skipped`
for a Slack failure too (`Slack post failed: …`), which the next run would read the same way.

**Acceptance criteria**
1. A `skipped` row reaches the prompt only when a human skipped it (the #2 button path). System
   releases — a Slack failure, a manual release — carry a distinct marker (column or reason
   prefix, say which) and are left out.
2. Unit tests: a released row and a Slack-failed row are absent from the prompt; a human skip
   with its reason is present.
3. The two system-released rows already in the ledger are re-marked so the next run's prompt is
   clean, proven with a `?dry=1` run that logs or returns the prompt's rejection lines.

---

### #2 · 🔘 Give the story card its own Slack app so the buttons work · 🔵 S4

**Story.** As the person posting these, I want to click "Mark posted" or "Skip" on the
card, so the system records what actually went out and learns from what I reject —
instead of me pasting into Facebook and the ledger never finding out.

**Why it is off right now.** The card shipped with Open group / Mark posted / Skip. A URL
button with no `action_id` does **not** stop Slack delivering the click: Slack mints its own
id and POSTs to the Interactivity Request URL of the **app that owns the posting bot token**.
This card posts with the **MDS WA Approvals** token, so on 2026-09-01 Eugene clicking "Open
group" reached the WA Approvals handler, which read it as a join-request decision, defaulted
to reject, overwrote the card in place, and stamped `decision=rejected` onto Airtable
JoinRequests `recgrlkagHhDZH3Iv`. The Whapi call 400'd, so no member was actually rejected.
Slack allows **one callback URL per app**, and Centurion and Application already hold both of
ours — so any button on this card lands in someone else's system. The card is now inert by
design, with a test pinning it.

**Cost of leaving it.** Small: no one-click "Mark posted", and skip reasons never reach the
ranker, so rejecting a weak story teaches it nothing. Dedupe is unaffected — a story is
recorded the moment it is offered.

**Acceptance criteria**
1. A dedicated Slack app exists for this feature. **Andy creates it** — the agent does not
   create accounts.
2. `FB_STORY_SLACK_BOT_TOKEN` and `FB_STORY_SLACK_SIGNING_SECRET` set in Render, followed by
   a manual redeploy (a Render env change does not restart on its own).
3. Its Interactivity Request URL points at `/api/fbstory/interactivity`. **Centurion's and
   Application's URLs are verified untouched** — this is the step that can silently break
   another feature.
4. Buttons restored to `buildCardBlocks`, and the "contains NO interactive elements" test
   replaced by one asserting they carry *our* `action_id`s.
5. Proven live, not assumed: clicking **Mark posted** flips that ledger row to `posted`;
   **Skip** captures a reason that appears in the next run's ranker prompt.
6. Proven that the click no longer reaches WA Approvals — n8n `ib7g9bBddhzCbj4X` records no
   execution for it.

**Already built, nothing to write.** `/api/fbstory/interactivity` exists, handles both
buttons and the skip-reason modal, verifies the Slack signature via the shared
`src/lib/slack-verify.ts`, and returns 401 when no signing secret is configured. This ticket
is credentials and configuration, not code.

---

## CLOSED

### #4 · 🎯 The partner judge is inconsistent inside a batch — "Hector Ai" disappears · 🟡 S3 · ✅ CLOSED 2026-09-04

**Premise corrected by #3 (2026-09-04).** Part of "Hector disappears" was not a verdict at all:
the model echoed our mention ids with the `post:` prefix dropped, so its verdicts were orphaned
and the hit counted as unjudged. Fixed in #3 (mentions are numbered per batch). What remains is
real verdict variance: with ids fixed, a batch still judged TikTok Shop / Receive / Xorosoft /
Hector on Anita's post `not_about_partner` (only Euka and CrediLinq neutral) — re-measure AC 1
from that baseline.

**Story.** As an admin searching Partner mentions, I want a partner that is plainly named in a
post to appear, so that searching "Hector" returns the post that says "Hector: Integrate before
31st August and get Hector MCP free for 1 month."

**Where it stands.** Three real bugs were fixed on 2026-09-03 and this is what is left. The
prefilter now FINDS it — `partners()` makes the AI suffix optional, so the catalog's "Hector Ai"
matches the post's "Hector". Verified: that post produces 16 prefilter hits including Hector.
But `judge()` returns `not_about_partner` for it **inside a batch**, while a dedicated call on
the same post returns `neutral`. So the mention never reaches the table and the search stays
empty.

**Suspected cause, not yet proven.** In a batch the same 1,200-char post body is repeated once
per partner, each entry differing only by its `(partner: X)` header. That is a confusing prompt:
the model sees near-identical items and appears to answer about the post rather than about the
named partner. Batch size is now 8 and `max_tokens` 4,000, so truncation is no longer the cause.

**Acceptance criteria**
1. The failure is REPRODUCED and measured first, not guessed — run the same hits batched and
   unbatched and record how often the verdict differs. One trial is not evidence.
2. "Hector Ai" on post `27084374081239403` is judged a mention (neutral is correct — it is an
   offer listing, per #praise rules) and appears when searching "Hector" on `/admin/facebook`.
3. Whatever changes, the sponsor-listing rule holds: an offer announcement stays **neutral**,
   never praise (Andy 2026-09-03 — announcements stay in scope because their COMMENTS carry
   real sentiment).
4. No regression in noise: the 14-day scan stays near its current ~74 matches, and complaints
   already found (TraceFuse, Quartile, Wayward, Veeqo, Sellerboard, eCom Triage, Activate
   Talent) are still found.
5. If the fix is "send one partner per call", the cost is stated plainly before shipping it.

**Measured first (AC 1)** — `partner_judge_bench.py --days 5 --trials 3`, 43 prefilter hits, Anita's
offers post = 16 partners (all should be neutral), 3 known complaints in the window. Read-only.

| shape | calls | Anita's 16 | Hector | complaints kept | identical across trials |
|---|---|---|---|---|---|
| batched (before): 8 mentions per call, the post repeated once per partner | 6 | 14 not_about_partner · 2 neutral | not_about_partner | 3/3 | 43/43 — wrong the same way twice |
| single: 1 mention per call | 43 | 15–16 neutral | flips | 3/3 | 41/43 |
| grouped: 1 call per text, its partners listed | 23 | 16 neutral | neutral | 3/3 | 43/43 (3 trials) |
| **grouped8 (shipped): ≤8 texts per call, each with its partners** | **3** | **16 neutral** | **neutral** | **3/3** | **42/43 (3 trials)** |

The suspected cause was right and it was not random: repeating one 1,200-char post eight times with
only the `(partner: X)` header changing makes the model answer about the post. `temperature` is
deprecated for `claude-sonnet-5` (the API rejects it), so it was never a lever.

**Shipped 2026-09-04** (`partner_scan.py`, backup `.bak-pregrouped`): `group_hits()` /
`chunk_groups()` / `grouped_listing()` — each text shown once, partners numbered in one flat sequence
across the call, `TEXTS_PER_CALL = 8`; `judge()` takes a chunk of texts. Plus `settle()`: a verdict
that CHANGES a stored row is confirmed by a second independent call (one text per call); on
disagreement the stored verdict stands — borderline texts flip 1 call in 3 under any shape, and
without this a complaint would flicker off the admin tab and back. 18 unit tests green. Bench kept as
`partner_judge_bench.py`. Spec + plan under `docs/superpowers/`.

**Acceptance criteria**
1. ✅ Reproduced and measured — table above, 2–3 trials per shape.
2. ✅ `Hector Ai · neutral` on post `27084374081239403` (SQL, `found_at 2026-09-04 19:52Z`); the
   portal reads the table per request, so "Hector" is searchable with no deploy.
3. ✅ Anita's post: 16 rows, all neutral; the system prompt and its sponsor-listing rule are unchanged.
4. ✅ / ⚠️ 73 matches on the 14-day scan (was ~74). Complaints kept **8 of 9**: TraceFuse ×2, Quartile
   ×2, Wayward, Veeqo, Activate Talent, Linnworks. **Sellerboard (Norm Lanier, Aug 21) was re-judged
   neutral by two independent calls** — "beta MCP… pretty limited… but it's a start. I hate that I pay
   for both" flips 1 in 3 under either shape; Andy's call whether that is a complaint. eCom Triage
   (Aug 21 15:32Z) sits just outside the 14-day window and was not touched.
5. ✅ Cost stated: fewer calls than before (3 vs 6 on the 5-day window, 5 vs 10 on 14 days) plus one
   call per changed verdict (1–3 per run so far). Not one-partner-per-call.

**Before / after.** Hector rows 0 → 1. Anita's post 3 neutral → 16 neutral. Table 129 → 144 rows
(complaint 21 → 20, neutral 87 → 103, praise 21 → 21). Unjudged: 0 → 0. Daily run: the autopilot's
`--days 3` re-judges a row only during its first three days, so a settled row then stays put.

**Found alongside, not fixed:** `partners_catalog` holds two published rows named "Prosperlytics
Consultants" and two named "Riverbend Consulting", so Anita's post carries each twice. Catalog belongs
to the Olivia stream — flagged, not chased.

**Regression caught by Andy the same hour, fixed (`sane_quote()`).** Grouping several partners into one
call made the model answer with the partner's own NAME as the quote — the admin tab's "What they said"
column read "Hector Ai" instead of what Anita wrote (14 rows). Tightening it to "must appear in the
text" was not enough: the model then answered with a real but generic line from the top of the post
("Here's a list of their offerings for this Summit!"), which passed. The rule now keeps a model quote
only when it can be LOCATED in the text and sits within 300 chars of the mention (or names the partner);
otherwise the line that names the partner is used, trimmed to 200 chars, with markdown stripped. A quote
that is only the partner's name is never kept. 12 quote tests; a first attempt would have replaced good
quotes (TraceFuse's complaint, an elided A2X quote) and was caught in the dry run before applying.
New `--fix-quotes` repairs stored rows from the text alone — no model call, no re-judging, so nothing
flaps. Result: **21 quotes corrected, 143 of 144 rows now carry a real quote** (the 144th is a comment
whose entire text is the two words "Scale Insights").

**Pending live proof:** the 16:25 CDT autopilot (`--days 3 --apply`) is the first unattended run
with the grouped judge; read its `PARTNERS:` line in `auto_import.log`.

---

### #3 · ♻️ A rejected partner mention is never removed — the table only grows · 🟠 S2 · ✅ CLOSED 2026-09-04

**Story.** As MDS, we want `digest.fb_partner_mentions` to say what the CURRENT rules judge,
so that a verdict written under an old prompt cannot keep showing on the admin tab and in the
daily Slack card long after the scanner would reject it.

**What happened before.** `partner_scan.py` finished with
`supa_upsert(env, "fb_partner_mentions", "ref_kind,ref_id,partner_id", rows)` — it only ever
INSERTed or UPDATEd the rows it decided to write. A hit judged `not_about_partner` was skipped,
so a row that a previous run wrote as `praise` simply stayed. Same shape as the classifier's
`--apply` only labelling NULLs: **a rule change did not reach what was already stored.**
Seen live 2026-09-03: after the praise rule tightened, Anita Petrov's Summit post still carried
6 stale `praise` rows; they were deleted by hand.

**Shipped 2026-09-04** (`~/mds-scorecard-tools/partner_scan.py` + `load_feed.py`, not git-tracked;
backups `*.bak-prereconcile`). After judging, the scanner reconciles: a stored row whose text this
run re-read is deleted when the model re-judges it `not_about_partner`, or when the name no longer
matches any partner. Rows in a batch the model failed on, rows missing from a good reply, and rows
for partners no longer in the catalog are never deleted and are counted. The line
`🧹 removed N (a re-judged not_about_partner · b no longer match) · left c unjudged · d out of catalog`
lands in `auto_import.log`; dry run prints `would remove`. `supa_delete()` returns the deleted rows,
so the count is measured. `texts()` now pages, so `--days 30` is the backfill path. 12 unit tests in
`tests/test_partner_scan.py`. Spec + plan under `docs/superpowers/`. Runbook in `FB_PIPELINE.md`.

**Root cause found on the way.** The first proof run removed 4 rows and reported **15 unjudged** —
Anita's stale praise survived. A probe showed the model echoes our id with the `post:` prefix
dropped (`post:2708…:655e…` came back as `2708…:655e…`) on **16 of 16** items, orphaning every
verdict. Mentions are now numbered 1..N per batch (`listing_for()`) and mapped back
(`parse_verdicts()`); the second run left **0 unjudged**. This corrects #4's premise.

**Acceptance criteria**
1. ✅ A re-run makes the window match the current rules — the 5-day re-run removed 8 rows
   (7 stale praise on Anita's post + 1), listed one per line.
2. ✅ Scoped — rows older than the 5-day window: **27 before, 27 after** both apply runs (SQL).
3. ✅ Reported — `🧹 removed 8 (8 re-judged not_about_partner · 0 no longer match) · left 0 unjudged · 0 out of catalog`.
4. ✅ Praise / ⚠️ count — stale state recreated with the pre-rule copy (`partner_scan.py.bak-praiserule
   --days 5 --apply`: Anita 5 neutral + **7 praise**), then the new scanner: **0 praise, no hand SQL**.
   Ended at 2 neutral (3 after the 30-day pass), not 5: with ids fixed the batched judge calls
   TikTok Shop / Receive / Xorosoft on that post `not_about_partner`. That is #4's variance, not #3.
5. ✅ Backfill — `python3 partner_scan.py --days 30 --apply`: 1,931 texts, 199 hits, wrote 129,
   removed 2, 0 unjudged.

**Before / after.** Table **53 rows (9 complaint · 38 neutral · 6 praise) → 129 (21 · 87 · 21)** —
the 30-day pass reached posts back to Aug 5 that the scanner (born 2026-08-31 with a 14-day window)
had never read: 82 new mentions, complaints 9 → 21. Anita's post: 5 neutral + 7 stale praise → 3
neutral, 0 praise. Unjudged mentions in a 5-day run: 15 → 0. Hector rows: still 0 (→ #4).

**Pending live proof:** the first unattended run is the 16:25 CDT autopilot (`--days 3 --apply`);
its `PARTNERS:` line in `auto_import.log` should carry the `🧹` count.
