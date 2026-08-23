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

## STATE 2026-08-23 (#113 CLOSED — the Summit event is RELOADED from the 09:52Z scan and live)
**Millie now serves the current run-of-show.** `scripts/load_event_graph.py` is a true refresh (diff
report by name → upsert → FK-safe reconcile → provenance), loaded from
`~/Downloads/event_graph_20260823T0952Z.json` (`_meta.scannedAt` 2026-08-23T09:52:31.687Z, verified
fresh against the ledger). **activities 50→86 · sessions 31→26 · attendees 178→199 · people 199→234 ·
locations 18→27 · participant_types 6→7 (`MDS`) · activity_audience 180→227 · activity_person_grants
183→698 · check_ins 22→151 · orders 138→144**; deleted 49/10/12/11/1/20 exactly as predicted; a repeat
dry-run is `+0 ~0 -0`; `events.source_scanned_at` + `loaded_at` stamped. Golden self-test re-derived:
plain Member **7** on day one, Women's Lunch grantee **8** (the +1 invariant is the test, not the
integers). Live proof: `op=day at=today` returns *Sunday 23 August* with Arrive & Check-In to the Hotel
at 3PM … Explore Singapore Beyond the Summit; Women's Lunch / Event Partner Check-in stay hidden from a
non-invited member. Runbook + six traps in `OLIVIA_HANDBOOK.md` §4.9. Three real defects were found by
running it — 3.9 vs PostgREST fractional seconds (faked 31 "changed" rows), GroupOS recreating an
attendee document on a role change (409), and curl argv vs macOS ARG_MAX on a 92 KB description — plus
a final-review fix wave (a loader SKIP is never treated as an export removal; three silent-swallowed
reads now fail loud; ordered paging; measured delete counts; `--new-event` guard). **Follow-ups filed:
#120 loader hardening · #121 `db/` excludes the `event` schema · #122 "Explore Singapore" is four daily
copies.** Next refresh = one command; read the `- ` and `!! skipping` lines before the real run.

## STATE 2026-08-23 (#114 CLOSED except AC4 — venue-day "today" LIVE on prod; #113 waits for a fresh export)
**#114 "today at the Summit" (Ian Sells, Singapore, got Saturday on his Sunday) — fixed in two
layers and PROMOTED.** mds-digest-web LIVE (`/api/version` ≥ `9d0ec41`): the schedule route resolves
`at=today|tomorrow|yesterday|<weekday>|YYYY-MM-DD|instant` in the venue's own zone
(`src/lib/schedule-day.ts`, 24 vitest cases), every answer carries `now_at_venue`, `day` returns
`day`/`day_label`/`resolved_from`, and **`next` returns the rest of the venue-day** (Task 2b,
`95eea25` — Andy's 12:42 SGT test had shown `op=next` hiding half of Sunday behind a hard 3; fix wave
`9d0ec41` labels the items' day, keeps `asked_day`, falls back on impossible dates). Olivia prompt
**promoted by Andy 2026-08-23 02:49 ET (prod versionId `bbd597b7`)** — `apply_114_venue_today.py`: the
`event_schedule` tool description says pass the WORD (today/tomorrow/a weekday), the TODAY line carves
out the venue exception, one bullet names the case. Andy promoted **#114 only**: staging was re-built
from prod (combined snapshot `staging_2026-08-23T064414Z_108-plus-114-applied` kept), #108 re-applies
its own edit and gets its own promote. Prod probe after promote (execs 100159/100160): "what's
happening at the summit today" → *"It's Sunday, 23 August at the Summit in Singapore — kickoff day!"*
+ full day; "what's on tomorrow" → *Monday, Aug 24*; tool_args literal `at:"today"/"tomorrow"`.
**AC4 CLOSED (Andy tested on WhatsApp, 2026-08-23 ET afternoon, Singapore already on the next day: working).** #114 is fully closed. **#113 (whole-event refresh, plan
`docs/superpowers/plans/2026-08-22-summit-event-refresh.md`, 4 tasks, not started): waits for a
GENUINELY fresh GroupOS export — `event_graph (1).json` was a 17-Aug scan (`_meta.scannedAt`
2026-08-17T22:16Z; 4 of 5 people registered 18–21 Aug absent); Andy's live GroupOS already shows
renames ("Arrive & Check-In to the Hotel at 3PM"), Welcome Dinner at Pool, a new "Explore Singapore
Beyond the Summit" — none of that is in any file we hold.** Two-agent rule added to CLAUDE.md (lock =
the only mutex; own-ticket doc sections; last committer rebases; message the peer session).

## STATE 2026-08-23 (#108 The Finder BUILT + PROVEN ON STAGING; Andy: promote, then decide on the 100-Q bank)
**The Finder ships one composable filter tool covering every data layer** — `find`
(`POST /api/olivia/find`, mds-digest-web, code live on Render) wired into **STAGING**
`bqHstPDi84uOhTCJ` (versionId `a49047ac`, Answer Tool + Answer Seed; `event_who` now carries
`op:'people'`). Belen's "which resellers are coming to the Summit?" now answers **17** (of 102
Summit attendees) / **122** community-wide (of 735 actives), every person with reasons; a country
breakdown sums cleanly (5 buckets); the disclosure engine (R1-R10) holds — a 🟡 filter (e.g.
`sku_min`) returns counts only, a non-member's `chat:` filter never names anyone. Gate **292 checks
EXIT 0** (26 finder checks). Full close block + AC table on `OLIVIA_SPRINT_4.md` #108. **#114 already promoted alone** (Andy
2026-08-23 06:48Z, prod `bbd597b7`); staging was rebuilt from prod (+#114) and #108 re-applies next
(`apply_108_find.py`), then **Andy promotes #108 separately** (`python3 scripts/olivia_wf.py
promote`). Before that promote, Andy decides whether to run the
**100-question eval bank** first (recommended — the real risk is the model reaching for `find`
where `expertise_search`/`content_search` was the better tool). Follow-ups filed, not blocking:
**#115** (geo/business-model data hygiene) · **#116** (finder phase 2 content+video, phase 3
events/partners/forms — own plan) · **#117** (`--cleanup` leaves probe message rows) · **#118**
(`event_who` should return a flat roster). **Lock released** (staging free for the next session). Staging re-applied after the #114-only promote — versionId `4321f06a` (snapshots
`pre-108-reapply` / `108-reapplied` / `108-final`), #114 seed edits intact. Re-probes: exec
`100210` (17 named), `100212` (Europe → 1), `100278` (breakdown by country, 5 buckets = 17,
`people:[]`, reply reports counts not names). Parser robustness (`mds-digest-web` main,
`0c46d42` + `d3fe132`): a multi-field object (`{segment,event}`) now validates as an implicit
`all` instead of 400ing ("leaf holds exactly one field"), `where` may arrive as a JSON string,
and `group_by` with no `return`/`ret` now defaults to `breakdown` — closing the two distinct LLM
tool-call flakes found re-proving this ticket.

## STATE 2026-08-22 (SESSION CLOSED — #97 PROMOTED + PROD E2E PROVEN; #105/#106 filed)
**PROMOTED 04:11Z (Andy): prod `7e4be40a` (#97) → #107 ~05:24Z prod `8f48fdb8` → #107b/c ~07:10Z prod `25ceefe1` → #107e ~08:40Z prod `d9538ca6` (picker lead: "Here are the Summit attendees I've recommended to you that I can reach for an intro…"; route `d8f8250` title-case) → **#107d ~08:00Z prod `d2961c8d`: eligibility = Summit attendee + phone (Millie-user rule DROPPED both sides, Andy); picker rows = expertise · speaker · city; route `dd02a9b`** · post-Yes = WhatsApp LIST picker (route's exact ids) · suggestions NEVER filtered/shortened (Andy) · buttons always (≤1024 inline, >1024 follow-up button message) · first-contact PS first when offer present · intro-tap path silent-gated (SELFTEST). #109 templates **APPROVED** (accepted/declined UTILITY, lapsed MARKETING — verified live 2026-08-22) — route logic next session (free-form requester notices die outside 24h window). #110 filed (tap turns not saved to history). Belen's identity split fixed (registration + roster row → her Staff record) so she can use Summit lanes + intros. PROD E2E: exec 96653 Accept tap → row 13 accepted/tap → 2 texts delivered to Andy's phone, 0 LLM rows. Andy's visibility ask → #106 filed (SQL-verified: search lanes exclude Staff; event lanes don't; `test-andy-8153` purged). Andy's lock: `python3 scripts/olivia_wf.py unlock` when done.**

### (pre-promote state)
## STATE 2026-08-22 (pre-promote — #97 BUILT + REVIEWED)
**#97 brokered intros: 7/7 tasks + final whole-branch review + 2 fix waves, all re-reviewed clean.**
LIVE on prod: route `/api/olivia/intro` (mds-digest-web `535a23a`, Render) · `olivia_intros` v2 +
`late_taps` · `Intro Sweep` on Reminder Sender `QhJw46Mr7LAP8fdz` (minute tick, exec 96624 clean).
STAGING `bqHstPDi84uOhTCJ` carries the tap branch (C1 binds taps to `consent_wamid`, C3 fail-open)
+ `member_intro` tool — **PROMOTE = Andy (`python3 scripts/olivia_wf.py promote`, lock RELEASED),
T4+T5 together**, then one real tap E2E closes the ticket (Andy is NOT Summit-registered → canary
registration for his test, or an eligible member tests). Rulings 2026-08-22: accept-is-final ·
Eugene row 2 set `declined` (his last tap) · non-attendee wording = Summit-PILOT line, never
"register" · #105 webhook-signature ticket filed (Andy: file + ship as own ticket, next session,
before any wide announcement). Reports: `OLIVIA_97_BROKERED_INTROS_REPORT.md` (Andy, listenable) ·
`OLIVIA_97_INTROS_FOR_EUGENE.md` + `_SHORT` (4,587 chars) · artifact
https://claude.ai/code/artifact/446286fc-411e-4e78-981e-9e858efa81d2. Full close block on the board.
SDD ledger `.superpowers/sdd/2026-08-20-brokered-intros-full-build/progress.md` (gitignored scratch;
secrets scrubbed). ⚠️ Scorecard main has ~15 unpushed commits from 3 parallel agents (#103, MotM,
#97) — push is Andy's/next session's call. Lesson saved: check-first before "add env var"; doc
claims about where a credential lives get a live probe.

### NEXT SESSION QUEUE (brief Andy, WAIT for go)
1. **#109** requester-side notices as templates (check `python3 scripts/olivia_intro_templates_109.py status` → APPROVED first; then route change; before any announcement).
2. **#108** (filed) attendees ∩ chat membership / business model tool — Belen's 'resellers attending' questions were answered wrong; truth table in the 08-22 log.
3. **#106** Staff/non-member records never surface in member-facing lists (staff attendees like Belen must stay usable as requesters) · **#105** webhook signature · **#110** intro-tap history.
   (#97 CLOSED: promoted + prod E2E proven; release-notes line still to post at sprint close.)
3. #103 open rungs (other agent) · #102 brainstorm · Millie promote (rides the same promote) · smoke
   partials · <2024 transcripts decision · sprint-close pair.

### (previous state below)
## STATE 2026-08-21 EVE (SESSION PAUSED mid-ticket — Andy: "i need to go, pause")
**#97 BROKERED INTROS BUILD IN FLIGHT — 4.5 of 7 plan tasks done.** Eligibility LOCKED by Andy
("lock them as-is": both sides Millie users + Summit-registered `recrATwhUDA55iQN5`; <30d parked).
Prereq resolved: env was on RENDER all along (plan said Vercel — wrong; both META_WA_* pre-existed).
DONE+reviewed: T1 ledger v2 (migration `olivia_intros_v2_20260820`, commit `9f380b1`) · T2 route
`/api/olivia/intro` (mds-digest-web `e6f8b48` DEPLOYED, 16/16 rulings, sweep isolation +
recency picker) · T3 live matrix 9/10 PASS zero real sends, DB baseline restored, SELFTEST
not.like proven 280==280 · T4 staging tap branch (7 nodes + Log Inbound button fix — PROD DROPS
Accept/Decline taps TODAY incl. Eugene's POC reject; execs 96072/96082; blast radius proven safe).
T5 implementer DONE (member_intro tool live on staging, exec 96162 chain proof, gate 264 EXIT 0)
— **REVIEW PENDING** + 3 open concerns (Plan Request regex swallows "connect me with someone" ·
picker renders prose not LIST · send branch live-proof deferred to post-promote tap).
**RESUME: SDD ledger `.superpowers/sdd/2026-08-20-brokered-intros-full-build/progress.md`** —
dispatch T5 reviewer, then T6 sweep tick, T7 close. ⚠️ staging lock HELD (claude, expires
2026-08-22T01:25Z); staging carries T4+T5 UNPROMOTED; sweep of POC row 2 will message Andy the
expiry line once T6 ships past 2026-08-27. Andy's promote covers T4+T5, then ONE real tap E2E.

### (previous close below)
## STATE 2026-08-22 (SESSION CLOSED — transcripts reached the ANSWERS; 5 promotes, all verified)
**The day's theme: the 2025-26 transcripts were live in the database but the ANSWER LAYER never used
them. Four separate causes, each found by reading executions, each fixed and promoted.**

### What shipped to PROD today (5 promotes, each: diff → gate → promote → verify → snapshot)
1. **Dead denial rule killed** — Answer Seed still said *"NO video has a transcript: what-was-SAID-in-it
   questions get a plain 'transcripts are not available yet'"*. A FOURTH stale rule I missed on 08-21.
   Replaced with TRANSCRIPTS ARE SEARCHABLE (2025+2026) + concept-term routing + pre-2025 boundary.
2. **Quote/timestamp discipline** — NEVER OFFER TO FETCH WHAT YOU WERE ASKED FOR: a quote/where/what-
   exactly question carries the verbatim line + speaker label + timestamp IN the answer.
   Proof: Bryce Alderson's SKU-expansion passage quoted at **00:37:30**.
3. **`call_transcript` enforced IN CODE** (`Attach Embedding`) — the tool schema listed only chat/FB
   sources, so the model kept passing `p_sources` without transcripts; two prompt fixes failed, so the
   third moved into code ([[feedback_code_beats_prompt_rules]]). `p_chat`-scoped asks exempt (transcripts
   carry no chat_name and would pollute digests). + conflicting-sources rule (transcript vs chat both
   reported and attributed).
4. **Gate over-refusal fixed** — the `off_topic` field added for #104 blocked short affirmatives and
   CLARIFYING QUESTIONS; "yes booth" was blocked 3× and served a canned "couldn't verify". RULE ZERO now
   exempts both.
5. **#112 CLOSED** (filed as #108, renumbered — the parallel session had already issued #105-#111) — the #80 OFFER BINDING already existed; its ACCEPT_RE end-anchor made "yes booth"
   miss. Affirmative may now carry a quantifier/typo; binding delivers EVERY offered video.

### #103 speaker work (same session, warehouse-side)
Library coverage **40% → 87%** (2025 97%, 2026 98%). Rungs: speaker_ids id-join · names · title/description ·
partner sessions · Zoom cues (participants + talk_seconds) · **AAI letter-mapping** (270 letters,
`video_speaker_letters`) · **frame-OCR** (ffmpeg from presigned URLs, 388 frames, 123 role-aware links,
moderators from "Moderated by" cards). 578 entities / 321 members / 1,391 links. Review CSVs triaged with
Andy: partner contacts resolved (Meher→Hector, Nadav→CapEc, Ben→Superfuel), 10 ASR/spelling twins merged
via speaker_aliases, Brandon Fishman created as guest on Andy's ruling, 6 unknown names left unmapped.
**Andy's rule codified: a MEMBER is never switched to partner/guest — partner-ness lives in
`affiliation_partner_id`.**

### Templates
`mds_birthday_box_address` **APPROVED as UTILITY** (id 917599728064581) — sent to Andy's number, status
`sent`. ⚠️ The test exposed bad address data: Andy's street = "street", Ian Sells = "iasi, Cimişlia,
Moldova", Eugene Khayman has TWO records (one with a Miami address, one empty). A real send needs a
which-record-wins rule + a "no usable address" path. Button taps do nothing yet (no workflow branch).

### ⚠️ TICKET NUMBERING (two sessions, one board — 2026-08-22)
The parallel #97/#107 session issued **#105-#111** while this one was running; I filed my
offer-binding ticket as #108 from a stale max and collided with its "attendees ∩ chat membership"
ticket. Nothing was overwritten — both rows survived — and mine was renumbered to **#112**.
**Rule: claim the next number from the board's CURRENT max at the moment of filing, never from
memory or from the session's own start state.**

### OPEN (next session)
1. **Jasim-class within-video ranking** — chunks of one video share the video's date, so the tiebreak is
   arbitrary; asked for a quote from later in a call, retrieval returns the opening minutes. `content_search_v2`
   change, every lane uses it — Andy's go needed.
2. **#102 answer-layer wiring** — speaker/role/talk-time/partner tables exist and NO lane reads them.
   "How many videos is Bonilla in?" / "who spoke for Riverbend?" still unanswerable. Brainstorm first.
3. #103 leftovers: moderator inference · ~134 pre-2025 videos (same OCR/letter rungs) · affiliation backfill.
4. #72 LOAD TEST — still never run, still the biggest pre-announcement risk.
5. Airtable-side dup-record merges (Andy's, never-delete rule): Meher ×2, Nadav ×3, Ben ×2, Eugene ×9.

## STATE 2026-08-21 DAY (SESSION CLOSED — Andy drove speaker work; smoke settled at 95/100)
**Smoke rerun: 5 of 10 non-PASS flipped → 95/100 effective, 0 fails** (#104 fixed at the enforcement
layer: FC `off_topic` field + Gate Verdict non-filterable; all 3 original fail-chains reproduced
clean with recreated adjacency). Remaining 5 partials: 2 data-side (4070 women-events catalog gap ·
4038 links-grading) + 3 behavioral (4095 3-day window serves latest daily · 4010 wording shades to
denial · 4100 staff-vs-member distinction) — each ticket-size, none chased.

**#103 REOPENED (I closed it on a field-scoped metric — 413/413 measured the FIELD; Andy caught it)
then REBUILT: library coverage 40% → 81%** (2026 **91%**, 2025 78%). Full state on the board block.
The load-bearing facts: identity space = `speakers`/`speaker_aliases`/`video_speaker_links`
(+`video_partner_links`); evidence rungs A `speaker_ids`→GroupOS-id→email · B names · C
title/description · D partner sessions · E Zoom cues→PARTICIPANTS (`role`+`talk_seconds` — group
calls have participants, not headline speakers, Andy's ruling; moderator ≠ speaker, inference open).
**Zoom transcripts carry REAL NAMES per cue** (quote+name+timestamp proven E2E for entitled asker);
AAI = letters (letter-mapping + frame-OCR open). **418 pre-#101 Zoom chunks were unreachable even
for ENTITLED members** (sensitivity=restricted + rule=public) — migrated, proven both ways.
**Weekly `zoom_weekly.py` now runs the ladder + guest-promotion + participants every run** (step
4.5, full dry-run green). Review CSVs on Andy's desk: `mds_speaker_review.csv` (60 unresolved) +
`mds_participant_review.csv` (12).

### NEXT SESSION QUEUE (brief Andy, WAIT for go)
1. **#103 open rungs** — AAI letter→name mapping · frame-OCR name tags · moderator inference ·
   affiliation backfill · review-CSV triage with Andy.
2. **#102 brainstorm** (ranking: decay · speaker weight · Summit bonus · WA/FB/Video equalization ·
   dossier weighting speaker>participant>FB-post) — CAPTURED-NOT-LOCKED, starts as brainstorm.
3. **Millie promote still on Andy's desk** (one promote = rename + fact-check + boundary +
   timestamps + #104 net). Meta watcher plan unchanged (submit "MDS Millie" on verdict, never
   re-register Mille).
4. 5 smoke partials + 2 bank-truth fixes · <2024 transcripts decision (~$137) · sprint-close pair.

## STATE 2026-08-21 OVERNIGHT (SESSION RAN WHILE ANDY SLEPT — his order: "in the morning; I need to see all green")
**ALL GREEN. Queue ① 2025 transcripts DONE · ② big smoke DONE (bank 90/100 effective · slice 11/11) · ④ Millie CLOSED · #103 speaker sync BUILT+CLOSED same night · gate GREEN at every step (263 checks, exit 0, run 6+×).**

### What shipped overnight (all verified live, all commits on main)
- **2025 transcript batch:** 232/233 videos (1 skip = 10s silent teaser) · 144.8 hr · $33.42 AAI ·
  6,429 chunks (0 mismatches, Zoom untouched) · 232 summaries in-session via 8 parallel subagents ·
  embedded (restricted = metadata only) · entitlement probed both ways · `scripts/aai_submit.py` is
  the persistent batch runner (curl, resume-safe).
- **Millie (queue ④):** staging says Millie everywhere; "what is your name?" fixed at the SOURCE —
  the Fact Check lane was vetoing the name as an unsupported claim (RULE ONE now names her +
  `community_info.assistant_name`). Meta: "MDS Millie" CANNOT submit while "MDS Mille" is
  PENDING_REVIEW (no cancel API) — **when watcher `a1ViYr5FT7iePdN9` fires: do NOT re-register
  Mille; submit "MDS Millie", then Andy re-registers (PIN), promote staging, DELETE watcher.**
- **THE NIGHT'S BIGGEST CATCH: `video_search_v2` (the LIVE lane — the workflow remaps
  video_search→video_search_v2 in Fetch Summaries/Fetch Raw Matches/Attach Embedding) was NEVER
  patched by #101** — entitled members still got blanket [RESTRICTED] E2E. Fixed (grant-bounded,
  attachments stay public-only, is_restricted = the video's flag), both sides proven, migration
  `video_search_v2_grant_bounded_restricted_fix_20260821`. ⚠️ trap: v1 probes pass while v2 serves
  members — always probe THROUGH the workflow.
- **4 stale "no transcripts" prompt rules purged** (Build Prompt ×2, Verbatim ×2, Answer Seed
  boundary now "2025+2026 transcribed, pre-2025 not") + **timestamp-citation rule** (quote → "At
  00:16:37" next to the link; probe proven).
- **#103 CLOSED (filed and built same night, Andy's order):** `digest.speakers` 239 entities ·
  `video_speaker_links` 480 links (413/413 videos) · **212 members EMAIL-evidenced** via the
  GroupOS mirror (`digest.video_speakers` — pre-existing table, all 234 rows have email;
  `member_record_id` is GroupOS-internal, NOT an AT id) + #100 resolver · 24 guests · 3 unresolved
  in `~/Downloads/mds_speaker_review.csv` · verify 7/7 · plan `docs/superpowers/plans/2026-08-21-speaker-sync.md`.
- **Smoke (`OLIVIA_SMOKE_2026-08-21.md`):** bank 89/7/4 → 90 effective (one "fail" is CORRECT #96
  behavior, bank truth stale); 3 real fails = ONE defect → **#104 adjacent-turn topic lag** (filed,
  S1). Slice v2 (problem-first, Andy killed the name-anchored v1 as "BS Qs"): 11/11 right videos
  unprompted, speakers+roles, multi-source answers, zero transcript denials.

### ANDY'S MORNING DESK
1. **Millie promote** (staging → prod: rename + fact-check rule + transcript boundary + timestamp
   rule — one promote covers all).
2. #104 priority call (adjacent-turn lag — 3 smoke fails).
3. Speaker review CSV (3 names) + #102/#97/#103-extension brainstorms (all CAPTURED-NOT-LOCKED).
4. 2024-and-earlier transcripts decision ("Not sure about <2024") — ~$137 for 2018-2024 at AAI rates.
5. Sprint-close pair still open: release notes post + retirement pass.

### (previous close below)
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
   `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`. Still blocked on Andy's RENDER env (plan said Vercel — wrong; digest.mds.co = Render, verified 2026-08-21)
   (META_WA_* onto mds-digest-web) + execution-mode pick.
4. ~~Rename the bot to "Millie"~~ **CLOSED 2026-08-21** (close block on the board). Spelling ruled
   **"MDS Millie"**; staging says Millie everywhere (12 strings, 4 nodes) + fact-check veto fixed
   (RULE ONE + community_info.assistant_name — the checker had silently stripped the name). Meta:
   "MDS Millie" can't submit while "MDS Mille" is PENDING_REVIEW (no cancel API) — **when the
   watcher (`a1ViYr5FT7iePdN9`) fires: do NOT re-register Mille; submit "MDS Millie" instead**,
   then Andy re-registers (PIN), promote staging, DELETE the watcher.

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
rulings locked, POC proven, Ian's real accept on record) — **blocked on Andy's RENDER env prereq (service `mds-digest-web`, NOT Vercel)**
(META_WA_TOKEN + META_WA_PHONE_NUMBER_ID onto mds-digest-web, then redeploy) + execution-mode pick.
**Next unblocked: #72 LOAD TEST** (sprint goal: it runs BEFORE the announcement; never run).
1. **Andy's desk:** #97 RENDER env + execution-mode pick · **register himself for the Summit**
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
