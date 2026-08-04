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

## STATE 2026-08-03: RELEASE 3 COMPLETE · SPRINT 3 OPEN

**Prod `89ee3632`.** Release 3 shipped and closed the same day: #40 retrieval-RRF + #41 identity
stamping + #39 attribution (promoted by Andy) plus #45/#46/#42/#47/#44 database-side.
**THE SMOKE: 3.6% → 1.7%** (173 judged · 164 pass / 6 partial / 3 fail).
**#43 RE-AUDIT: architecture 6/10 → 8/10** — retrieval 3→8 (HNSW idx_scan **0 → 1,098**),
identity 6→8 (conversations 100% stamped), semantic 8→9, event log 0→live (15,437 rows),
graph 0→started (159,940 edges), gate 9→10 (202 checks), grants unchanged.
**#49 handbook shipped** (`OLIVIA_HANDBOOK.md`, 733 lines) and **ClickUp `2531q-103317` rebuilt as
its copy** (TOC + 18 chapter pages + `99 · ARCHIVE`).

**THE BOARD IS NOW `OLIVIA_SPRINT_3.md`** — goal = **make Olivia personal**.
S1: **#52** (follow-up topic binding) + **#29 v1** (THE PERSONALIZATION LAYER — 5 lanes personal)
are **both staged + proven 2026-08-03, awaiting ONE promote** ·
**#51** (members-lane fabrication — she invented "Lori Barzvi") · **#53** (fact-gate false clamp,
filed 2026-08-03 with a full reproduction) · **#50** (entity dossiers).
Everything shipped in Releases 1-3 is in `OLIVIA_BACKLOG_ARCHIVE.md`.

## NEXT SESSION

0. **⛳ WAITING ON ANDY: one promote now carries #52 + #29 + #51.** Staging `5b86e6b4` holds the
   follow-up topic binding (#52) + the personalization layer v1 (#29, 5 lanes) + the members-lane
   hardening (#51: typed not-found · past-member framing · role-claim flag · name-the-names;
   5/5 fake names honest, gate 224 GREEN). Prod is still `89ee3632`. Andy said "not promoting
   yet — more features first" (2026-08-03), so staging accumulates;
   `python3 scripts/olivia_wf.py promote` when he calls it. Test chat (staging by default):
   digest.mds.co/admin/olivia/test.
1. **#53** (fact-gate false clamp) — filed with a full reproduction (exec 63490); the biggest
   remaining defect class (a grounded answer binned costs a member a whole real answer).
2. **#50** (entity dossiers — pairs with #29's member side for the fit score), and #29's
   open sub-steps (research memo · retrieval-authority slot · "people like Mo").
3. NOTE for the next smoke: **Q3124's bank truth was CORRECTED** (Lori Barzvi = real past
   member; expect = former-member framing, not not-found) — `eval_bank_smoke.json`, backup
   `.bak-51-q3124`.
3. Andy's side, standing: **GROUPOS_PAT** · **Circleback details** · **does an event
   description/agenda field exist anywhere we are not syncing?**
4. Release notes are the final stage of the sprint — `OLIVIA_RELEASE_NOTES.md`, I draft, Andy posts.

## Watch-outs (standing)
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
