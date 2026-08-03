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

## STATE: R1+R2 LIVE ON PROD (`90a13237`) · #40 BUILT + STAGED 2026-08-03 (LATE)

Prod untouched since Andy's 03:54Z promote (Big Smoke on prod 169 · **3.6%** = the baseline).
**#40 shipped to STAGING same day:** `content_search_v2` side-by-side — tsv-GIN keyword + pure-ANN
top-200 (HNSW **plan-proven**, lifetime idx_scan 0 → counting) + recency floor → **RRF by rank**
(kw 1.0 · vec 1.0 · recency 0.5 · authority/engagement 0.25) · v1 12s → **v2 0.46s** on Q3106's
shape · 6,486 sub-30-char embeddings nulled (rows stay keyword-reachable) · `embed_content` joined
the nightly pipeline + 26h heartbeat (#13-alarmed) · staging executes v2 at all 3 call sites
(model-facing tool name unchanged; active version `e51c9e88`) · **E2E exec 61669** (loop ran v2 ×2,
Q3106 organic answered with the Michael Patrón thread) · **gate 202 GREEN** (+12 v2 checks).
Full detail: `OLIVIA_BACKLOG.md` #40 BUILT block + `SESSION_LOG_OLIVIA.md` 2026-08-03 (LATE).

## NEXT SESSION — close #40, then #41

1. **Propose the smoke/TEST slice to Andy** (eval RUN = his go): target = ≤ 3.6% with no class
   regressing; slice should hit the exists-but-missed shapes (Q3094/Q3106/Q9024) + a spread of
   content classes. On green → ask Andy to schedule the prod flip.
2. **Prod flip (Andy runs promote):** the staging graph carries the swap; **same moment**, apply
   the wrapper migration — `multi_source`, `app_member_feed`, `persona_signals` still call v1
   internally — + NOTIFY pgrst + REST hammer. Then re-run audit A1/A3 for the #43 diff.
3. **Then #41 identity stamping** (FK wants `airtable_id` NOT at_member_id, 0/646 equal; backfill
   losslessness decays — same week). Working order after: #45 → #39 (v2 already returns
   author/post_author labels — #39 nearly free) → #46 → #42.

**Release-3 exit unchanged:** `OLIVIA_ARCHITECTURE_AUDIT_2026-08-02.md` Appendix A re-scores
≥8/10 (baseline 6/10) — retrieval 3→≥7 (#40 moves it), identity 6→≥8 (#41+#45), rest hold.

**#40 traps burned (don't re-trip):** function-level `SET hnsw.*` = PG15 placeholder permission
error → in-body force-load + set_config(local, fail-open) · fused-branch ANN gets planner-refused
(row misestimate) → two-phase pure-ANN under local enable_seqscan=off · **a fast probe proves
nothing — first probes were 0.35s warm SEQ scans with idx_scan still 0; only the plan + the
counter are honest.**

## Watch-outs (standing)
- **`olivia_selftest.py` paces by sleep(20)** — an answer >20s races Save Conversation and the
  next probe reads INCOMPLETE history (manufactured a phantom yes-binding P0 on 2026-08-03). Fix
  it to wait on persistence before multi-turn probes. Real-member echo: two messages <2s apart
  hit the same race — known, low-frequency, filed as a note.
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
