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

## STATE 2026-08-05: SPRINT 3 OPEN · PROD `163d175b` (#57b promoted; staging matches) · #58 shipped in SQL

**Sprint 3 goal = make Olivia personal.** Ten tickets closed and live (evidence at the BOTTOM of
`OLIVIA_SPRINT_3.md`); ten still open. Release 3 and everything before it is in
`OLIVIA_BACKLOG_ARCHIVE.md`. Entry point for the whole system: `OLIVIA_HANDBOOK.md`.

**Last measured quality: smoke 1.7% wrong** (173 judged, 2026-08-03) — that number predates all
ten of today's tickets, so it is stale in BOTH directions until the next smoke runs.

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

### Pick up here
1. **No unblocked build ticket remains.** #58, #59 and #60 all closed 2026-08-05, all data-layer,
   nothing awaiting promote. The rest is blocked (#18 data · #20 census form · #17 GROUPOS_PAT ·
   #36 Circleback), S4, or a smoke-time measurement (#32, #14, #34). Next move is an unblock from
   Andy or the **sprint-close ritual**: smoke → #32 + #14 measured → #34 → release notes.
2. **Nothing is waiting to promote** — staging and prod match, and #58 was data-layer only.
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
