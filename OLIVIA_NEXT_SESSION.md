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
> single-question staging probes. **Propose + WAIT** = any eval RUN (TEST ≤50 / FULL). **Andy
> runs** = `promote` · prod edits (emergency rollback excepted). The session classifier blocks
> lock/promote for me — Andy runs both in his terminal (proven 2026-08-03; `lock` worked again
> later that day — try it, fall back to Andy if blocked).
> **Vocabulary: "gate 202" = 202 safety CHECKS (free) · RUN = firing the eval bank · PROBE = one question.**

## STATE 2026-08-11 (evening): SPRINT 3 OPEN · PROD `e5d57236` — #75 LIVE · #80 STAGED

**#80 (offer binding) is BUILT + STAGED + PROVEN on `dcc75770`; prod has the SQL half only.**
The migration (`video_search_v2` + `p_video_id` + `summary` column) is live in the DB; the
Answer Seed changes (OFFER ACCEPTED binding + DELIVER WHAT YOU OFFERED + OFFER SPARINGLY) wait
on the promote. Staging diff vs prod = Answer Seed only. Gate 246 exit-0 (as Ian).
**Andy: promote, then one prod spot-probe of offer→Yes. After promote, re-measure the offer
rate on a week of traffic (baseline 26% of llm answers).** Plan + full evidence:
`docs/superpowers/plans/2026-08-11-80-offer-binding.md` · board ticket #80.

## STATE 2026-08-11 (later, superseded): PROD `e5d57236` — #75 IS LIVE

**PROMOTED 15:07 UTC (Andy's chat order, run via me):** prod `ebe7244b` → **`e5d57236`** (69
nodes, +`Extract Raw Event`+`Store Raw Event` as the FIRST webhook branch). Gate ran INSIDE the
promote as Ian (`OLIVIA_GATE_PHONE=16196077048` — new env knob in `olivia_wf.py`, added because
the default probe aborts on Andy's channels_present row). **Prod canary exit 0** (raw + feedback
rows landed, self-cleaned); health pings store 0 rows. Raw store now records ALL prod message
events — signal 8 arms itself once 14 days of history exist.

## STATE 2026-08-11 (earlier, superseded): #75 STAGED, AWAITING PROMOTE

**#75 (reactions) is BUILT + STAGED + PROVEN, prod has none of it.** Staging `289a9656` carries
two new nodes (`Extract Raw Event` → `Store Raw Event`) as the FIRST webhook branch; diff vs prod
= exactly those two. Raw store `digest.olivia_webhook_events` + health signals 7/8 + canary
script are live (SQL side ships without promote). Gate **246 exit-0**. Commit `02cf62d`.
**Andy: `lock` → `promote`, then `python3 scripts/olivia_reaction_canary.py` (prod), expect exit 0.**

**Board caught up 2026-08-11:** #77 shipped UNLOGGED on Aug 10 (`b227682` — identity separated
from chat presence, 559 → 732 reachable, 0 regressed); #62 closed, #63 moved out, #78 filed —
the 08-08..10 sessions wrote commits but no stream-log entries.

⚠️ **Gate default probe currently ABORTS: Andy's `digest.members` row lost `channels_present`**
(was populated Aug 10 00:43 when #77's gate ran green; `[]` today; 49 rows empty incl. 2 real
members). Run the gate as `--phone 16196077048` (Ian) until the upstream digest/roster sync is
fixed — that writer is the WA digest project's, not Olivia's. Flagged in the board's open
questions; Andy to rule where it gets fixed.

**Open S1 after the promote:** #78 · #61 · #64 · #66 · #72 · #73 · #76 · #80 · #68. Nightly eval
2026-08-10: 220 judged, 7.7% fail (Andy: acceptable for now — #76's new bank is the priority).

---

## STATE 2026-08-07 (superseded): SPRINT 3 OPEN · PROD `ebe7244b` — #20, #70 AND #70c ARE LIVE

> **Prod moved twice on 2026-08-07.** 20:44 UTC `f6b54620` → `7fe60761` (#20 + #70). Then **23:09
> UTC `7fe60761` → `ebe7244b`** — Andy's own promote, label `70c-recency-and-buttons`, two nodes
> (`Format Reply`, `Answer Seed`), snapshots either side in `olivia_snapshots/`. **`ebe7244b` is
> current.** Source: `scripts/olivia_loop/apply_70c_recency_and_buttons.py`.

**Promoted 2026-08-07 20:44 UTC** (`f6b54620` → `7fe60761`, 65 nodes, gate green inside the
promote, snapshots either side in `olivia_snapshots/`). Verified in the prod node: `form_stats`
×6 · `WHO HANDLES WHAT` · `- CALLS (#70)` · `ADVICE ASKS CHECK THE LIBRARY` ·
`Want a quick summary?` · `WHO WAS IN THE AUDIENCE IS NEVER ANSWERED`, each exactly once.

**#20 is CLOSED except P2.** Census coverage 64 → **79 of 96** questions · cross-form mapping
22 → **55** keys · **personas read the forms warehouse** (752 rebuilt, 462 of the 489 members with
answers draw on them) and a new submission now moves the fingerprint, so it self-updates.

**#70 ZOOM is LIVE.** 254 calls · 4,348 attendance rows (**stored, never shown**) · 65 transcripts
/ 3,116 chunks embedded · 65 summaries · video dossiers 7.8 → 14.4 topics · weekly chain on
launchd + a Sunday scheduled task for the GroupOS fetch.

**Gate 232 → 243 exit-0**, now covering the Zoom surfaces (anon denied on `calls`,
`call_attendance`, `zoom_name_alias`; transcripts always cite `app.mds.co`; restricted chunks
excluded).

⛔ **NOTHING FROM 2026-08-07 IS COMMITTED** — ~15 new scripts, 8 files in `scripts/sql/`, the gate
edit, and `ingest_videos.py` in mds-digest-web are all working-tree. Commit before anything else.

### THE ONE THING BLOCKED ON ANDY
**#20 P2 — the 13 free-text census answers** (biggest challenge, what worked best, strongest
expertise, how MDS impacted you) into `content_items`: searchable and quotable like application
answers, or owner-only? Everything else in #20 is done.

### Known and deliberately left
- 4 member calls have no published video — checked individually, genuinely unpublished.
- **Speakers on only 413 of 1,024 videos**, so speaker-name search misses 60% of the library.
- `videos_weekly_check.py` imports `map_video` from the UNTRACKED `mds-digest-web` repo.
- 961 videos have no summary BY DESIGN: no transcript, and a GroupOS blurb is not a summary.
- Forms → expertise ledger was built, measured, REVERTED (substring matching is unsound: `ai`
  matches inside "Em(ai)l"). Needs #68's canonical_key → topic map.

## NEXT SESSION — SPRINT 3 IS STILL OPEN (Andy 2026-08-04: "sprint is not over")

**Prod `163d175b`.** Eleven tickets live: #52 follow-up binding · #53 fact-gate
calibration · #51 members lane · #54 geo (country/region/list) · #55 credits · #56 partner
rankings · #29 personalization v1 · #50 entity dossiers (all four kinds) · #38 buttons ·
#57 report confirm-step + quoted-reply binding · **#57b** (report confirm stops clean, form→from).
Gate 224 exit-0; snapshots at every promote.

### THE SMOKE RUNS AT SPRINT COMPLETION, NOT BEFORE (Andy's ruling)
The fresh bank is built and stored — do NOT fire it early. **Fired set 110** (organic 96),
including the 34 new organics **3140–3173**: every uncleared 👎, both of Etienne's filed reports,
Ian's partner-ranking trio and Eugene's lender pair verbatim. Retirement is mechanised
(`retired: true`; `OLIVIA_EVAL_ALL=1` for a full 212 regression sweep). Multi-turn rows fire by
hand: **3141 · 3144 · 3147 · 3150 · 3151 · 3154 · 3162**. Docs: `OLIVIA_EVAL_LIST_2026-08-04.md`;
snapshots in `eval_bank_snapshots/` (the tools folder has no git history).

### 2026-08-05 — the board is down to ONE unblocked ticket
Andy's rulings: **#18 BLOCKED** ("we dont have data") · **#19 → S4** ("skip it") · **#35 → S4** ·
**#20 → S2 but BLOCKED** ("census is not done yet… we need to launch the form first"). #17 and #36
were already blocked on his side.

**#57b is LIVE** — prod `163d175b`, gate green at promote, verified against the prod node itself
(the typo harness re-run there: 20/20). #54's holding-delay was already at 30s.

### 2026-08-05 (later) — #58 SHIPPED · #59 filed · every build ticket is now blocked or S4
**#58 is CLOSED and live on both surfaces** — cancelled registrations no longer count. One
chokepoint view `digest.event_registrations_live` (drops `ticket_status` Unconfirmed + No Show),
ten reader functions repointed mechanically, the writers keep the raw ledger. **35 members × 36
member-event pairs** stopped being told they are attending a cancelled event; 0 members lost a live
ticket. Gate 224 exit-0. **Pure SQL — no n8n node changed, so there is nothing to promote.**

**#59 is also CLOSED** — the dossier annotation joined `entity_dossier` on the display name; 27 event
names and 12 partner names carry >1 dossier, so the join fanned out (Summit Singapore twice,
Riverbend twice). Both lanes now take one dossier per row (`lateral … limit 1`) and join back on
**ordinality**, events keyed on the event record. All 27 + all 12 names swept clean; partner ranking
8/8 identical; gate 224 exit-0. SQL only.

**#60 is also CLOSED** — the Canceled phase was correct (Andy: admins cancel drafts); the bug was
the sync's substring fallback renaming the Speaker's Lunch into "MDS Summit Singapore". Fix: one app
event enriches ONE catalog row (mds-digest-web `9abc8fc`, losers' `app_*` NULLed) + health **signal 5**
`catalog-duplicate-event` on the 5-min alarm. 0 dup pairs in 1,422 rows. **Phase rule written:**
browse = Registration Open/Confirmed only; named asks answer Canceled/Postponed honestly with the
true phase; Tentative/Awaiting Feedback invisible everywhere.

### 2026-08-06 — #20 UNBLOCKED, and its foundation already exists
The census LAUNCHED (17 real submissions night one, all synced to AT + member-linked via new Make
scenario 4860042) and the **forms warehouse shipped**: `digest.form_responses` (2,276 submissions
across census 2026 + app v3 + honorary + both legacy censuses, 90% member-stamped) + view
`form_answers_latest` (latest answer per member×form×ref, `submitted_at` = decay axis) + gate 226.
**Andy's rules are in memory `project_mds_forms_warehouse`** — recency wins · conditional gaps ≠ No
· raw answers OWNER-ONLY (silent personalization fine, aggregates fine incl. chapter/region slices
with small-cell suppression). **#20's remaining build = the Olivia side**: owner-gated lane
("what did I say on my census"), dossier/persona consumption, aggregate answers.

### NEXT SESSION = REVIEW #20, THEN PROMOTE (Andy 2026-08-06)
**#20 is BUILT + STAGED + probe-proven on staging `9b14c44c`; prod is `f6b54620` and has NONE of
it.** Next session opens by REVIEWING #20 — not by starting new work. Review = re-read the ticket's
ACs, re-run `scripts/qa_form_stats.py` (last: 1,857 checks, 0 fails) + the leak gate (232, exit-0),
re-probe the three classes that failed and were fixed (pay bands · staff location/Philippines ·
chapter percentages), then promote if all green.

**#20's open AC:** personas/dossier consumption of census answers (P1 attributes overlay, P2
census long-text into `content_items` — needs Andy's exposure ruling, P3 dossier section). Decide
whether that ships before the promote or as a follow-up.

⛔ **The Airtable forms-structure discussion (new tables, Answers table, sandbox base
`appE6FkiVESss5mbZ`) is NOT sprint work** — Andy 2026-08-06. It belongs to the census/forms project,
not Olivia. Do not let it re-enter the sprint.

### Pick up here (after the #20 review)
1. **#20 · Census into the warehouse is UNBLOCKED and half-done** (data layer live; Olivia lane +
   dossier wiring remain). Everything else is blocked (#18 data · #17 GROUPOS_PAT · #36 Circleback),
   S4, or a smoke-time measurement (#32, #14, #34). Next move is #20 or the **sprint-close
   ritual**: smoke → #32 + #14 measured → #34 → release notes.
2. **#20 IS waiting to promote** — staging `9b14c44c` vs prod `f6b54620`. Nothing else pending.
3. **Andy's side:** post the release note (`OLIVIA_RELEASE_NOTES_2026-08-04.md`, WhatsApp AND
   ClickUp syntax) · two AT country records are wrong (`NE` row is Haarlem/Netherlands, `ZW` row
   is Zug/Switzerland) · standing: GROUPOS_PAT · Circleback · does an event description/agenda
   field exist anywhere we are not syncing?
4. **Sprint close ritual** (when the tickets are done): smoke → archive closed tickets to
   `OLIVIA_BACKLOG_ARCHIVE.md` → open `OLIVIA_SPRINT_4.md` with open tickets only → regenerate
   the ClickUp handbook copy → release notes are the FINAL stage. Skill: `mds-sprint-ritual`.

### Broadcast state (2026-08-04)
Template `mds_assistant_whats_new_aug2026` (id 27016348374704952) is **APPROVED** on WABA
`1575708577606583`. Fired to the 25-member audience: **8 landed, 17 blocked by Meta 131049**
(per-user MARKETING cap across all businesses — not our content, no charge, number still GREEN).
**Do not retry the 17 immediately.** Andy's own number is excluded from the audience by design.

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
