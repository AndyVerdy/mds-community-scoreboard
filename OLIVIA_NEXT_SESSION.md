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

**Read `OLIVIA_BACKLOG.md` first** — every item carries **Accept when** criteria under one global
DoD; the judge files failures into 8 classes mapped to tickets.

## NEXT SESSION — orders (2026-07-31 close)

1. **#33 FIRST (S2, filed from Andy's prod tests):** pull the 2:40PM exec (2026-07-31) — ~2min
   stall with NO read tick / typing / holding message · check the 9:54+9:55PM duplicate holding
   pair against the KNOWN Meta-replay ghost (trigger fix is STAGED, unpromoted) · distinct copy
   for the two ladder rungs · links-when-solving rule · WRITE the pre-promote smoke checklist
   (its run result gets pasted into the session log every promote).
2. **#6 Chapters — blocked on Andy's rulings first:** canonical count (AT rollup 94 vs live 97 vs
   raw 116) · are chapter-lead names/emails shareable. Then whitelist + policy sources.
3. Standing: MDS-Life ruling (Q3088 expect) · schedule `olivia_derive_niches.py` +
   `olivia_label_questions.py` nightly · extend content_stats (distinct-authors-by-source) ·
   FULL run on the new bank (3101-3112) when Andy calls runs back on · promote when he says go
   (Release 2 bundle: fix batch · holding trigger · #23 cuts · #5 counting · #33 fixes).

## State (2026-07-31 session close)
- **CLOSED TODAY: #23 (on the story) · #25 (LIVE ON PROD, mds-digest-web `294b094`) · #5 counting
  (staging, Release 2).** #32 cost-control + #33 prod-smoke FILED. Bank swapped (3101-3112 in,
  backup `.bak-preswap-0731`), NO run fired.
- **STAGING carries Release 2, all proven:** eval fix batch (fact-gate clamp+RULE TWO ·
  content_search post_author · dossier persona) · holding-trigger fix · #23 cuts (router caching =
  cost not speed · claim-free gate skip) · #5 counting (`member_niches` 14-canon multi-valued,
  stated niches EQUAL · `member_count` RPC w/ breakdown_sum — sums READ, never computed).
  **Gate 167 GREEN.** Prod untouched since `ee3e3cf6` (4.0%).
- **Warehouse adds (shared DB, additive):** `member_niches` · `olivia_question_labels` ·
  `member_count` · portal fixes live on prod (eval-traffic exclusion, pagination — PostgREST caps
  at 1000 rows ALWAYS, page everything — topics per-question labels, Exclude-staff toggle; staff =
  `member_attributes` AT mirror 29, NEVER `digest.members`; blank status ≠ member).
- **Neither derivation job is scheduled yet** (niches + question labels) — decay risk, in #33/#5
  residuals.
- **Watch:** promote is Andy-run · MDS-Life ruling open · "Oliva" display name · ClickUp doc stale.

## The daily routine
- **Run tiers (Andy 2026-07-30): FULL vs TEST.** A FULL run (all 100) produces the standing number —
  rare, never for fix confirmation. A TEST run confirms a change: **50 max, ideally ~25-35** — the
  fails/partials the fix targets + their thread predecessors + a pass spread across sources (the
  over-refusal check). `olivia_eval.py --fire --score --staging --ids <list>` **with
  `OLIVIA_EVAL_BANK=eval_bank_organic.json` or it silently fires 0**. Never 10×100Q days.
- ONE paid organic run per session, AFTER free diagnosis + fix batch + free probes. Expectations
  name the SQL that proves them. Retirement: 3 consecutive passes + class still covered → replace
  same day, bank stays 100.
- Runs wait per-reply (~50 min full bank) — never fixed sleeps. The eval progress output can look
  like a stalled prompt to task monitors — it is per-reply pacing, don't kill it.
- Reset between probes; `--cleanup` deletes nothing; leak gate GREEN (161) before anything ships.
- Andy's number excluded from reporting; probes reset his thread — warn him first. Before firing a
  backdated-arrival ladder test, check the latest olivia-row time (my bad assumption cost 3 stray
  texts to Andy).

## Open with Andy
- **MDS Life** (now also eval-fail Q3088): data gap vs wrong name — his call on the canned truth.
- **👎 alerts**: reactions land in `olivia_feedback` and nobody is told. Wire to Slack?
- `member_match` category values: 'Apparel' filter misses the real 'Clothing & Accessories' (#7/#10).
- Adam's Hector answers near-contradicted ("MDS special pricing, 137 claimed" vs "no discount code
  listed") — partner-card discount semantics worth a ruling.
- Constantine got one "Sorry — I could not generate an answer" (07-29 20:35) — infra turn, exec
  worth a look.
- Still owed: revenue ranking · ex-member departure dates · canonical chapter count · chapter
  leads · Intercom ticket #215475264324071 · "Oliva" display name · health alerting latched.
