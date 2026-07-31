> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.

# Olivia — next session

> ⛔ **THIS DOC IS THE STANDING ROUTINE, NOT THIS SESSION'S GO.** Read it, verify against live, do
> FREE read-only diagnosis, then **propose the plan to Andy and WAIT.** Never fire a paid eval run,
> promote to prod, or touch a live system on this doc's authority. (Andy, 2026-07-29.)

**Read `OLIVIA_BACKLOG.md` first** — every item now carries **Accept when** criteria under one global
DoD; the judge files failures into 8 classes mapped to tickets. `SESSION_LOG.md` 2026-07-30 (top) has
the full detail.

## NEXT SESSION — Andy's orders (2026-07-30 close): PUSH, VERIFY EVERYTHING, FULL BANK

1. **PROD PUSH** (off-hours protocol — carries the staging graph: #21 loop + #24 first-contact +
   #1 boundary/gates + #26 wiring + #23 holding trigger + all seed rules):
   ```
   python3 scripts/olivia_wf.py lock --reason "prod push: staging graph promote"
   python3 scripts/olivia_wf.py promote     # diff -> leak gate GREEN required -> snapshot -> write -> bounce -> verify
   python3 scripts/olivia_wf.py unlock
   ```
   Rollback: `python3 scripts/olivia_wf.py rollback <label>`. ⚠️ The leak gate currently has ONE
   standing red (the app session's S3 thumbnails — Andy's ruling pending); resolve or consciously
   accept before promote since promote requires gate GREEN.
2. **VERIFY EVERY COMPLETED PBI ON PROD + prod not broken** — the per-ticket probe list:
   - #21/#24: "how many chapters" → follow-up "which is the biggest?" (loop signature) · a
     first-contact question on a fresh test flag → answered + intro appended.
   - #1: Q3061 "Share link to Brandon's post" → real resolving link · "Is Donald Trump a nazi?" →
     honest nothing · "update my email" → ticket offer · capability question → help list.
   - #3: "video about product launch by Brandon Young" → exists-restricted, no guessing ·
     "what's new in the video library" → restricted rows marked.
   - #26: "any 3PL partners that can help me in europe?" → Blue30-class answer.
   - #31: Tim Tierney's phone against 2-3 RPCs → zero rows; front-door sim already on prod.
   - #27/#30 (DB-level, already live): app_member_feed for andy.verdy1@gmail.com + Jack Fallon →
     both feeds correct; canceled email → {}.
   - #28: personas — nightly 4:15am should have built the remaining ~548; `persona_refresh.py
     --stats` → 0 missing/stale.
   - #23 ladder: fire the holding-timer webhook once with arrival=now → 18s + 60s messages.
3. **THE FULL 100-QUESTION RUN — THE SAME LOCKED BANK, NO NEW QUESTIONS** (Andy's explicit order,
   for comparability with staging):
   ```
   cd /Users/Born/mds-scorecard-tools && OLIVIA_EVAL_BANK=eval_bank_organic.json \
     python3 olivia_eval.py --cleanup && OLIVIA_EVAL_BANK=eval_bank_organic.json \
     python3 olivia_eval.py --fire --score        # PROD (no --staging) after the push
   ```
   Baseline for comparison: staging full-bank 13.0% (measured with the fact-gate DEAD) · the 34Q
   gate-on test run 2.9%. This run re-baselines the standing number with everything on.
4. Then: **#23 speed cuts** (the open half — router drop on loop turns, parallel zeroth-fetch,
   claim-free gate skip; ≤10s median AC).

## State (2026-07-30 close) — the big day: TEN closed
- **Closed:** #21 loop · #24 first-contact · #1 evidence contract (10% rung) · #22 Kimi (no swap) ·
  #26 partners+events embeddings · #27 app identity door (`app_member_feed`) · #28 living persona
  (daily 4:15am launchd; ~548 build tonight) · #3 restricted markers (live for prod already) ·
  #31 canceled-means-gone (status gates ALL doors; prod front door patched under lock) · #30
  at_member_id resolution (Jack Fallon proof). **Gate = 158 checks** (+1 standing red: thumbnails).
- **Open:** #23 latency (ladder shipped + proven; cuts remain) · #25 portal (Member-360 half
  SHIPPED in digest-web 05014d6 — dual-id resolution + legal-name search; olivia-analytics half
  open) · S2 queue #5 #6 #7 #8 #9 · #29 recsys research (S3) · S3/S4 as filed.
- **Standing rules landed today:** EVERY MEMBER ALWAYS (748 by at_member_id) · run tiers FULL vs
  TEST (`OLIVIA_EVAL_BANK=eval_bank_organic.json` or --ids silently fires 0) · #1 ladder at the
  10% rung · membership status = entitlement (`is_active_member_status`).
- **Watch:** persona nightly (4:15am, Slack summary) · the fact-gate apostrophe trap (NO bare
  apostrophes in n8n expressions) · two stray Intercom test tickets · "Oliva" display name ·
  Airtable MCP token dead · mds-scorecard-tools still not a git repo.

## The daily routine
- **Run tiers (Andy 2026-07-30): FULL vs TEST.** A FULL run (all 100) produces the standing number —
  rare, never for fix confirmation. A TEST run confirms a change: **50 max, ideally ~25-35** — the
  fails/partials the fix targets + their thread predecessors + a pass spread across sources (the
  over-refusal check). `olivia_eval.py --fire --score --staging --ids <list>`. Never 10×100Q days.
- ONE paid organic run per session, AFTER free diagnosis + fix batch + free probes. Bank =
  `eval_bank_organic.json` (**100 questions, LOCKED to real member turns**). Expectations name the
  SQL that proves them — 3 fixed-answer expects went stale in ONE day; never write frozen answers.
  Retirement: 3 consecutive passes + class still covered → replace same day, bank stays 100.
- Runs wait per-reply now (~50 min full bank) — never revert to fixed sleeps; overlap scrambles
  attribution and fakes fails.
- Reset between probes; `--cleanup` deletes nothing; leak gate GREEN (148) before anything ships.
- Andy's number excluded from reporting; probes reset his thread — warn him first.

## Open with Andy
- Does an **"MDS Life" chat** exist? (Kayleigh 👎 — we hold no chat by that name; data gap vs wrong name.)
- **👎 alerts**: reactions land in `olivia_feedback` and nobody is told. 2 of 4 reactions ever were
  real defects. Wire to Slack?
- `member_match` category values: 'Apparel' filter misses the real **'Clothing & Accessories'**
  Airtable value (#7/#10).
- Still owed from before: revenue ranking · ex-member departure dates · canonical chapter count ·
  chapter leads · Intercom ticket #215475264324071 · "Oliva" display name · health alerting latched.
