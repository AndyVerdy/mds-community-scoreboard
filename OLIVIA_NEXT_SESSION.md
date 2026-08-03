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

## STATE 2026-08-03 END-OF-DAY: R3 ARCHITECTURE COMPLETE except the re-audit

**Prod `89ee3632`** (Andy promoted ~08:23Z; batch #40 retrieval-RRF + #41 stamping + #39
attribution; flip companions applied: wrappers→v2, fb_thread marker, hammer 200s, re-backfill).
**Closed same day, DB-side:** #45 identity-rest (regs 61.9→75.3% raw / 97.7% member-evidence;
entitlement ruling: members.at_member_id NEVER auto-stamped) · #46 member_events (append-only
physical, 3 live triggers + daily diff, 0→15,052 events/2,304 members, live-flow watchdog) ·
#42 place_city (alias TABLE, 908→853 spellings, write-normalized) · #47 event_lookup rerank
(rank-eligibility partitioned future/past, upcoming-first; Q9024 premise was STALE — third
stale bank truth fixed) · **#44 pulled forward by Andy and CLOSED**: expertise ledger 5,822
rows/738 members (16 data-table topics, evidence jsonb, band multiplier) + knowledge graph
159,940 edges (150-cap, thread_interaction), nightly `graph_ledger` job. Gate 202 GREEN all
day (+ hardened: transport retry 5xx-only, deterministic active fixture). Nightly now runs
8 jobs. Tickets #48 (AT write-back) + #49 (developer handbook) filed in THE REST.

## NEXT SESSION

1. **#43 — the re-audit** (architecture board's last item): re-run
   `OLIVIA_ARCHITECTURE_AUDIT_2026-08-02.md` Appendix A, score ≥8/10 vs baseline 6/10 —
   retrieval 3→? · identity 6→? · events 0→live · graph 0→live. Runs WITH #34 at release close.
2. **THE SMOKE** (deferred by Andy: once per batch, never per ticket) = the release exit exam +
   the formal #40 ≤3.6% and #39 attribution-cluster numbers. Propose + WAIT (paid run).
3. Then THE REST in order: #38 buttons → #29 matchmaking/dossier (best-fed ticket now: events +
   ledger + graph + stamped identities; consumer wiring of #44 lives HERE by name) → sources.
4. Andy's side, standing: GROUPOS_PAT + app event logging (the app slot in member_events is
   specified and waiting).

**Traps burned today (don't re-trip):** PG15 blocks function-level SET hnsw.* → in-body
set_config(local, fail-open) · planner refuses fused-branch ANN → two-phase pure-ANN ·
fast probe ≠ proof (only the plan + idx_scan counter) · pg-safeupdate needs `where true` on
REST DELETEs · chapter_affiliation + business_model are text[] · percent_rank needs ::numeric ·
data-modifying-CTE counts read the PRE-update snapshot · error-shaped JSON parses fine — check
keys, never just json.loads · gate fixtures must be ACTIVE + ordered.

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
