> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.
- **Always show a ticket's STORY + ACs. Closing needs: short results · short AC checklist (met/not) · before/after numbers.** (Andy 2026-08-03)

# Olivia — next session

> ⛔ **Standing tiers (Andy 2026-07-29/31): Fine without asking** = read-only diagnosis · the LEAK
> GATE (`scripts/olivia_leak_gate.py`, free) · staging edits under the `olivia_wf.py` lock ·
> single-question staging probes. **Propose + WAIT** = any eval RUN (TEST ≤50 / FULL) · **and
> STARTING ANY TICKET (Andy 2026-08-19): a new session opens with the briefing — next ticket
> NUMBER + NAME + STORY — and waits for the go. "Continue working on Olivia" = show the briefing,
> not start. Standing orders/approved plans order the queue; they never start it.** **Andy
> runs** = `promote` · prod edits (emergency rollback excepted). The session classifier blocks
> lock/promote for me — Andy runs both in his terminal (proven 2026-08-03; `lock` worked again
> later that day — try it, fall back to Andy if blocked).
> **Vocabulary: "gate 202" = 202 safety CHECKS (free) · RUN = firing the eval bank · PROBE = one question.**
> **New standing traps (2026-08-20):** ① TWO Summit-named catalog rows — "MDS Summit Singapore
> **Night Out**" (side event) vs the real `recrATwhUDA55iQN5`; naive name-matching grabs the wrong
> one ② template quick-reply taps arrive `msg_type='button'` and are NOT in `olivia_messages` —
> only `olivia_webhook_events` has them ③ audits opt out of equalizer logging via the
> `X-Olivia-Audit` header (never a p_limit heuristic — that silenced a real lane) ④ the E2E
> canary pattern: temp registration row, probe, DELETE same session.

## STATE 2026-08-20 LATE (SESSION CLOSED — VIDEO DAY): PROD untouched; all ships = SQL fns + data loads.
**#100 CLOSED (identity aliases) · #101 CLOSED (video transcripts + real access gating) · gate GREEN at close (263 checks, exit 0, run 7× today).**

### What shipped tonight (all verified live)
- **#100:** `digest.member_email_alias` (5,763 rows; sources preferred/stripe/admin_field/name_match_approved)
  + `resolve_member_by_email()` (active-record-preferring; NULL on ambiguity). 29 approved aliases written to
  **Airtable FIRST** (Members DB `appou5JVr0WIrioWS`/`tblfwOSROSHfuYUxv` — ⚠️ the env's AIRTABLE_BASE_ID is the
  WhatsApp DB, wrong base for this), then mirrored. Audience resolution 634→704 active; the 10 known email
  mismatches 0/10→10/10. **`Pending Group Entrance` now counts as active** (753→754; Current+New+Pending = 718
  = Andy's export exactly).
- **#101:** AssemblyAI transcripts for **ALL 161 videos of 2026** ($26.23, `~/mds_transcripts/2026/`) →
  **2,730 chunks across the 96 videos Zoom never reached** (`meta.provenance='assemblyai'`; #70's 65 Zoom
  videos untouched, checksum identical). **`digest.video_access` = 34,236 REAL grants** (real_match only —
  panel rows are phantoms, 42 yopmail). `content_search_v2` learned the `video_access` access_rule type;
  `video_search` gates restricted treatment per asker (attachments stay PUBLIC-only — file_key leak caught).
  **96 summaries written in-session** (161/161 `summary_source='transcript'`), everything embedded
  (restricted videos embed METADATA ONLY — vector branch cannot leak). Proof: entitled asker retrieved a
  RESTRICTED TikTok-Mastermind passage at 00:05:01, timestamped. Quote ruling (Andy): quote/summarize/TLDR/
  exact-words yes — **full transcripts never**.

### THE QUEUE (Andy 2026-08-20, session close — in this order)
1. **2025 transcript batch** — same machinery (`scripts/aai_transcripts.py` + `apply_video_summaries.py`).
   ~233 videos / 145.6 hr ≈ **$33 AAI**. **Prereq: fresh presigned export from Andy's dev** (current links
   expire 2026-08-27; `04_presign.py --days 7 --year 2025`). Load video_access for 2025 restricted from the
   same pairs file (already covers all years — 375 videos). Summaries in-session again, no API.
2. **Smoke-test batch of questions, focused on the EUGENE CASE** — "best TikTok cold start videos" served the
   thin Milan title-match over the transcript-rich Beginners Panel. Content now exists (transcript chunks
   reachable); the remaining gap is intent-vs-title RANKING in `video_search` + whether the answering layer
   should show more than one video (Eugene: "maybe it should show more than one"). Overlaps #71's vocabulary
   work — read #71 before touching ranking.
3. **Members' connection tasks — #97 brokered intros build** (screenshot proof on file: template intro
   accepted end-to-end, wa.me links both ways, POC list-picker rounds "Pick a member" working). Plan pinned:
   `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`. Still blocked on Andy's Vercel env
   (META_WA_* onto mds-digest-web) + execution-mode pick.
4. **Rename the bot to "Millie"** (Andy's wording at close). ⚠️ The name submitted to Meta is **"MDS Mille"**
   (`PENDING_REVIEW`; watcher n8n `a1ViYr5FT7iePdN9` hourly). If Andy wants "Millie" specifically, the Meta
   submission may need to change — confirm spelling with him BEFORE the 14-day re-register window burns.
   When live: DELETE the watcher, queue the #79 copy rewording pass.

### Standing next-session rules (unchanged)
Open with the briefing (ticket NUMBER + NAME + STORY) and WAIT for the go. Verify against live before new
work. Gate before any ship. #72 LOAD TEST still never run — it remains the biggest open risk before any
announcement.

### New traps from tonight (do not relearn)
- **PostgREST pages are UNSTABLE without `order=`** — an unordered limit/offset walk returned 3,116 rows but
  only 43 of 65 distinct videos. Every pagination gets an order key.
- **Expression indexes can't ON CONFLICT via PostgREST** — loaders diff-before-insert (twice today).
- **Verify Airtable writes against Airtable itself** — `member_profiles` mirrors on its own schedule and lags.
- **The gate's restricted-transcript check is now GRANT-BOUNDED** (restricted chunks only for granted videos),
  not blanket exclusion — that is the #101 invariant, don't "fix" it back.
- **`member_identity` holds 57 NULL-`at_member_id` rows** (one `phone='sam'`) — recorded, not chased.

---
### (previous close, for context)
## STATE 2026-08-20 (SESSION CLOSED): PROD `060701be` — nothing awaits promotion; all of tonight's
## ships live in SQL functions + the digest.mds.co route (no workflow nodes touched).
**Eugene's four: #94 #95 #96 #98 #99 CLOSED · #97 POC proven + plan pinned · smoke 50/50 addressed.**

### 🔬 Eugene-arc smoke (50 Qs, RUN on Andy's go) — `OLIVIA_SMOKE_EUGENE_ARC.md` has the full table
47/50 · A 18/18 · B 12/12 after TWO in-run #95 fixes (audit header `36e1d7d` — the p_limit
heuristic had silenced logging on the plan lane; LRU cycling `0b4b418` — exhausted pools froze) ·
C 12/14 · D 5/6. **#98 CLOSED same session** (`179f6c0` — registrations-ledger authority on BOTH people branches;
re-probed clean). **#99 CLOSED** (note-in-tool; E2E proven via a temporary canary registration, deleted after —
"show me the rest" now re-calls and serves fresh ranked people). **⚠️ Andy: who-to-meet stays
OFF for your phone until you register for the Summit for real** — the canary was test-only. Wording flags → #14. Count drift
157-vs-113 = THE COUNT RULING resurfaced live. **Ian Sells ACCEPTED the real intro** (#3
accepted, links both ways); Eugene's still pending — the sweep/expiry rules are in the #97 plan.

### ⚠️ Board: **`OLIVIA_SPRINT_4.md`** (22 open tickets). **Two sprint-close items still await
Andy:** ① the SMOKE RUN on the 100-bank (the exit exam — proposed, his go) ② validate + post
`OLIVIA_RELEASE_NOTES_2026-08-19.md`.

### ✅ #94 Expertise Ledger v2 — CLOSED 2026-08-19 (this session)
Warehouse-side only (no prod workflow edit, nothing to promote): taxonomy 16→**51 topics**
(18 parents + 33 subs), derive v2.1 live (decay 12/24mo · engagement bonus · forms ×1.2 ·
40%-peak floor — floor proven by live inflate/restore), **594 members scoreable on forms alone**,
verify `scripts/verify_expertise_v2.py` **9/9 PASS**, gate EXIT 0, nightly RPC path re-run clean
(11s). Same-day catch: the substring trap re-opened by short terms (`'vat'`/`'str'`) — biz+persona
CTEs now tsquery-match. Full close block on the board. Commits `0ce7ebe`·`a1250eb`·`8d70f10`.

### ✅ #95 Equalizer for the advice lanes — CLOSED 2026-08-19 (same session, Andy's go)
The execution log showed Eugene-shaped topic asks route to **expertise_search**, so BOTH advice
lanes got the equalizer (member_match_v2 + expertise_search; multi_source/_v2 went VOLATILE to
inherit it). Proof: identical repeated asks 8/8 → 0/8 shared names (REST) and disjoint sets on
the staging workflow path; log carries member_match + expertise_search lanes; gate EXIT 0.
Commit `a31a45b`, close block on the board. ⚠️ Andy's asker row carries the probe history — his
own next real "who knows X" rotates past those names for up to 30d (correct, remember at demos).

### ✅ #96 Attendee-name disclosure — CLOSED 2026-08-20 (Andy ruled it live in-session)
**The rule now in force:** attendee-name lists cap at **10** (display cap — filters/counts always
run over the whole ledger); NAMES require the asker's own registration for THAT event
(registrations ledger = the authority, never `event.people` — Andy's test row exposed that trap
on the live route, fixed same hour); non-attendees get counts/aggregates only. `event_who`
migration + route `3e77774`/`08d42fc`, gate +3 checks EXIT 0, E2E probed both sides. Supersedes
2026-07-20 any-member-sees-names.

### 🔨 #97 Brokered intros — POC PROVEN E2E 2026-08-20 (Andy: "lets try to make a POC and then decide")
Template `mds_intro_request` **APPROVED as UTILITY** (no marketing cap on consent asks). Full
loop ran on Andy's number: `olivia_intros` pending → template delivered → Andy tapped **Accept
intro** → watcher flipped the ledger → links both ways, all `delivered` in `olivia_sends`.
Tools: `scripts/olivia_intro_template.py` (create/status) · `scripts/olivia_intro_poc.py`
(request/watch/status, HARD-LIMITED to the test number). **Findings for the real build:**
template button taps = `msg_type='button'`, NOT persisted to `olivia_messages` (only
`olivia_webhook_events` has them; Mille also answers the tap text as a message — the workflow
needs an intro-tap branch) · plus-is-space on ledger timestamps. **Full ship waits on Andy's
rulings:** conversation intent ("connect us") + workflow branch · per-target rate cap · expiry ·
decline wording · seed copy.

### NEXT SESSION OPENS HERE — brief Andy, WAIT for his go (the ⛔ rule above)
**Queue front: #97 BUILD** (plan `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`,
rulings locked, POC proven, Ian's real accept on record) — **blocked on Andy's Vercel env prereq**
(META_WA_TOKEN + META_WA_PHONE_NUMBER_ID onto mds-digest-web, then redeploy) + execution-mode pick.
**Next unblocked: #72 LOAD TEST** (sprint goal: it runs BEFORE the announcement; never run).
1. **Andy's desk:** #97 Vercel env + execution-mode pick · **register himself for the Summit**
   (restores his who-to-meet demos — canary was test-only) · THE COUNT RULING (157-vs-113 shown
   live in one conversation) · sprint-close pair still open: 100-bank exit exam (his go) + post
   `OLIVIA_RELEASE_NOTES_2026-08-19.md` · Eugene's intro tap still pending (ledger #2; check
   `python3 scripts/olivia_intro_poc.py status`) · Mille name watcher (`a1ViYr5FT7iePdN9`) ·
   THE COUNT RULING (recommendation: 98 active members, one `event_registered_members` view) ·
   Eugene's Members-DB record pin (9-record cluster) · "MDS Mille" re-register when the watcher
   fires (PIN, 14-day window) · #72 LOAD TEST before the announcement.

### DO THIS FIRST
1. ~~Schedule the reminder sender~~ **DONE 2026-08-18: n8n `QhJw46Mr7LAP8fdz` ("Olivia — Reminder
   Sender"), every 5 min.** First tick exec 86839 (23:15 UTC): stale sweep ran, 0 due, clean stop.
   Faithful port of `olivia_reminder_sender.py` (script stays the manual/dry-run tool); chosen over
   launchd so reminders survive the Mac sleeping — and launchctl is classifier-blocked for me anyway.
   **DELIVERY PROVEN 2026-08-19 05:55 UTC:** Andy's live ask arrived on his phone — sent 05:55:08,
   `read` 05:55:11 in `olivia_sends`. Sender cadence now **EVERY MINUTE** (Andy: 10-min total lag
   too long for minute-level asks). #86 CLOSED.
2. ~~Re-register the number~~ **DONE 2026-08-18 (Andy ran it): the number is "MDS AI Assistant".**
   `POST /register` with the two-step PIN returned success; live API now shows `verified_name:
   "MDS AI Assistant"`, `name_status: APPROVED`, CONNECTED/GREEN. "Oliva" is gone. Existing threads
   may show the cached old name for a while; new threads are correct. Andy holds the PIN (password
   manager — deliberately not written down here).
   **→ NEXT NAME ALREADY SUBMITTED (Andy's call, same night): "MDS Mille" is `PENDING_REVIEW`.**
   When it approves there are **14 days to re-register** (same `POST /register` + Andy's PIN) or the
   approval lapses and must be resubmitted. Check `new_name_status` at session start:
   `GET /1306956855827812?fields=verified_name,name_status,new_display_name,new_name_status`.
   **Watcher live:** n8n `a1ViYr5FT7iePdN9` (hourly, TEMPORARY) — WhatsApps Andy's test number on
   APPROVED/DECLINED, nags hourly until re-registered, silent while pending. Limit: free-form send
   needs Andy's 24h window on …8153 open. **DELETE the watcher once Mille is live.** When the name
   flips, queue Andy's rewording pass on the intro/self-references (#79 curated copy says "the MDS
   AI assistant").
3. **Multi-event note (Andy 2026-08-19: "we will have more" schedules):** the event schema and all
   lanes are already multi-event (everything keys on `event_id`; the loader loads any export
   alongside). ONE decision waits for event #2: the lane's no-event-named default is
   latest-starting — switch to nearest-upcoming or asker's-registration when a second event loads.
   Nothing to build until then. Reminders stay schedule-anchored BY DESIGN (her refusal of
   freestanding "remind me to check fb" is correct behavior); freestanding reminders = a new
   ticket if Andy ever wants them.
4. **Ask the dev for a fresh export** — CÉ LA VI is in the admin's 19 locations but not our 18, so
   some of the 13 venue-less activities may be export gaps. Same dump un-truncates long descriptions.

### Two things NO probe can verify — test on a phone
`Eval (silent)?` routes SELFTEST traffic to `Save Conversation` and never reaches `Send Reply (Meta)`,
and both the image and reminder-delivery branches hang off that send. So:
- **images** — "show me the Summit theme post Eugene shared" must be tried on a real phone
- **reminder delivery** — likewise, once the sender is scheduled

### The demo set (nine questions, verified on prod)
Broad reading recs · full day one · which sessions suit me · who speaks Monday · where is X + map ·
show me the theme post (image) · weekly digest (summaries) · remind me (set/list/cancel) · who should
I meet (#87). Buttons need a complaint she has **not** already handled — she will not re-offer.

### The lesson this session kept teaching
**Code beats instructions.** Three prompt rules failed on images, four on reminder timing. Both were
fixed in one commit each once the work moved into the tool. And **read the execution before
theorising** — it settled in one call what rule-writing chased for rounds, twice.

### Open tickets, awaiting priority
- ~~#90~~ **CLOSED 2026-08-18: the sync never existed** (one-time xlsx load 2026-07-29, nothing ever
  wrote the table again). Now: n8n **`RpEbU47SpMVsbwqg`** hourly mirror (sibling of Members/
  Summaries), AT `{active}=1` = 18 chats, **diff 0** field-by-field, ghost row deleted, heartbeat
  `chats_mirror` (3h) under signal 4. Curated columns untouched. **Andy ruling queued:** Accelerator
  + 2026 New Members carry `required_form` in AT but are ungated in the mirror.
- ~~#89~~ **CLOSED 2026-08-18: the gap was IDENTITY, not attendance.** Zero digest fns read
  `event.attendees` (counts were single-sourced all along — now stamped as table comments,
  migration `event_roster_authority_comments_20260818`). Loader matching rebuilt (3-rung ladder):
  people matched 124→**170 of 199**, Courtney freed from a "Test Test" record. **Andy's list on the
  board:** 4 speaker roster rows linked to Max Mikhaylenko's record · dup member pairs (Brian,
  Henrik, Rebeca, Ryan, Eugene ×9) · the 151-vs-108 filter ruling. Fresh export covers the last 6
  absentees + late orders.
- **#88** 🟡 partner profiles — event-specific and type-specific; `event.attendee_profiles` designed,
  not built. Passcode never enters the warehouse.
- **#86** 🔴 sender now scheduled (n8n `QhJw46Mr7LAP8fdz`) — open only for the arrival proof on a
  real phone (Aug 23 test reminder, or an ad-hoc "remind me in 5 min").

**Closed today:** #85 (schedule lane) and #87 (who to meet — 4 of 8 not attending → **7 of 7**).
Both keep their evidence in `OLIVIA_SPRINT_3.md`; they move to `OLIVIA_BACKLOG_ARCHIVE.md` at
SPRINT close, not session close.

### Known and deliberately left
- Brandon Himmel's Aug 26 session has no parent activity → no audience → invisible to everyone.
- 5 of the 20 probe questions unfired: 13, 14, 15, 17, 18.
- `test-andy-8153` is a test row in `event.people` — remove when done testing.
- #72 load test still shelved (design only, nothing built).

### Traps in the export, all handled by the loader — do not re-learn them
- **41 of 91 activities are Milan 2025 leftovers** carrying `isDelete`. The event was cloned.
- **The `member`/`speaker`/`partner`/`guest` booleans are stale** and all false on records whose
  `accessRoles` grants three roles. `accessRoles` governs.
- **`event.timeZone` is a display label**, not IANA. Times are local wall-clock with no offset —
  which is exactly how `events_catalog.start_at` ended up 8 hours wrong.

## Watch-outs (standing)
- **NEVER fire probes at PROD against a real member's number.** On 2026-08-04 prod probes ran
  into Andy's own thread mid-test and twice sent "new question", resetting his context and
  stealing a button tap. Staging only, or a dedicated test number.
- **A 200 from Meta's `/messages` is NOT delivery.** The truth arrives asynchronously on the
  status webhook — read `digest.olivia_sends` before claiming reach (17 of 25 broadcast
  messages failed with 131049 *after* the API accepted every one).
- ~~`olivia_selftest.py` paces by sleep(20)~~ **FIXED 2026-08-03 (#52):** it now polls
  `olivia_messages` for THIS turn's reply before firing the next (`--timeout`, default 180s) and
  prints the wait — a probe in the #52 set took **50.4s** and would have raced the old pacer.
  Real-member echo: two messages <2s apart hit the same race in the workflow itself — known,
  low-frequency, still just a note.
- **FB capture SOP: rewrite `extension/seed_ids.json` from the capture file EVERY run** — 4c
  falls back to it silently (localStorage dies on tab close); a stale seed = comments for the
  wrong days. Backup pattern: `.bak-<date>`.
- Eval wamids `SELFTEST_MANU*` are not cleaned by `--cleanup`; Andy's thread carries test turns
  (accepted). Seed edits get a node syntax check BEFORE build_loop (apostrophes, twice).

## The daily routine (unchanged)
- Runs: FULL (all bank) rare; TEST = 25–35 targeted; `OLIVIA_EVAL_BANK=eval_bank_organic.json`
  or it fires 0. ONE paid run per session, after free diagnosis + probes. Retirement: 3 passes.
- Runs pace per-reply — the quiet stretches are NOT a stall; never kill the run.
- Reset between probes; gate GREEN before anything ships; Andy's number excluded from reporting.

## Open with Andy
- Q3088 MDS-Life ruling (parked) · whale ruling (chapter TTM sums) · "Oliva" display name ·
  member_match 'Apparel' vs 'Clothing & Accessories' · 👎 reactions → Slack? · bank truth fixes
  (722→723 members; supplements count drifts) · ClickUp doc refresh pending.
