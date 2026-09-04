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

### #4 · 🎯 The partner judge is inconsistent inside a batch — "Hector Ai" disappears · 🟡 S3

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

---

## CLOSED

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
