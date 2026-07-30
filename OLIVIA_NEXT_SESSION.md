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

## State (2026-07-30 close)
- **#21 answering loop: CLOSED 2026-07-30 (Andy's call — built + proven on staging; the ticket does
  not wait on the prod push).** 11 of 13 organic fails fixed and proven individually. Standing
  full-bank number: **13.0% on the NEW 100-question bank** (the old 84 scored 6.0% the same morning —
  the 16 new real-member questions are deliberately hard). The prod push is its own queued action below.
- **#24 first-contact: SHIPPED on staging, closed.** Rides the same promote.
- **#1 boundary half: SHIPPED on staging 2026-07-30 PM** (action lane allowlisted, loop offers the
  ticket only after checking; probes 5/5, Q3061 closed, gate GREEN). Rides the same push.
- **#1 judge-as-gate: SHIPPED on staging 2026-07-30 eve** — deterministic LINK GATE (citations
  verbatim-in-evidence, id-rewrites auto-repaired, runs even on gate_error) + **the fact-gate was
  found DEAD since the morning apply (bare apostrophe → invalid syntax → gate_error pass-through on
  every answer, 13.0% ran gate-OFF) and restored** + self-descriptions unblockable (RULE ONE +
  deterministic backstop + data-access→helpAsk). Execs 56115/56123/56133. Rides the same push.
  #1 stays open on: rates to the rung (re-baseline needed — gate was off for the 13.0%) · per-lane
  coverage measured.
- **#25 filed (S2): the /admin/olivia portal tells the truth** (Andy's screenshots 2026-07-30 —
  stale topics-card window, unproven tiles, eval-marking pollution).
- **#22 Kimi: CLOSED, no swap** (22.2% vs 15.3% fail, 2x cost/answer, 8x latency, forced fetch
  impossible on Kimi). Bench harness reusable: `mds-scorecard-tools/kimi_bench.py`.
- **#23 latency: NEW S2** — 24s median vs ~5s band; cuts named in the ticket (router drop on loop
  turns, parallel retrieval, conditional gate).
- Prod still runs the old cascade **with the scrambled-history bug live** (created_at-only ordering).

## QUEUED: the prod push (#21 + #24 + the #1 boundary, together) — Andy's explicit go, off-hours ("we will do prod push later", 2026-07-30)
```
python3 scripts/olivia_wf.py lock --reason "promote #21 loop + #24 first-contact"
python3 scripts/olivia_wf.py promote        # diff -> leak gate -> snapshot -> write -> bounce -> verify
python3 scripts/olivia_wf.py unlock
```
Rollback: `python3 scripts/olivia_wf.py rollback <label>`. Andy's manual window:
digest.mds.co/admin/olivia/test (staging/prod toggle). **NEXT build work: #1 continues** — boundary
+ judge-as-gate both shipped 2026-07-30 (Q3061 closed, link gate live, fact-gate restored);
remaining inside #1: rates to the rung (**next organic run re-baselines — the 13.0% ran with the
fact-gate dead**), per-lane coverage measured.

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
