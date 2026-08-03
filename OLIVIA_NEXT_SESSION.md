> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.

# Olivia — next session

> ⛔ **Standing tiers (Andy 2026-07-29/31): Fine without asking** = read-only diagnosis · the LEAK
> GATE (`scripts/olivia_leak_gate.py`, free) · staging edits under the `olivia_wf.py` lock ·
> single-question staging probes. **Propose + WAIT** = any eval RUN (TEST ≤50 / FULL). **Andy
> runs** = `promote` · prod edits (emergency rollback excepted). The session classifier blocks
> lock/promote for me — Andy runs both in his terminal (proven 2026-08-03).
> **Vocabulary: "gate 190" = 190 safety CHECKS (free) · RUN = firing the eval bank · PROBE = one question.**

## STATE: RELEASES 1+2 ARE LIVE ON PROD (2026-08-03)

Andy promoted 03:54Z — versionId `90a13237`, 67 nodes, graph==staging, gate 190 ran inside the
promote. Prod re-verified: 5-check PASS, Eugene yes-binding + ticket-capability + report feature
all proven on prod, then the **full Big Smoke ran ON PROD: 169 judged · 3.6% FAIL < the 5%
benchmark** (1 of 6 fails was stale bank truth — live 723 vs bank 722; fix the bank row). Pre/post
promote snapshots in `olivia_snapshots/`; rollback = `olivia_wf.py rollback <snapshot>`.

## NEXT SESSION = #40 — Retrieval rewrite (Release 3 = ARCHITECTURE)

**Read `OLIVIA_BACKLOG.md` first** — open-items-only, 19 tickets in working order, audit
scorecard on top (audit swept twice — #43/#44/#45/#46 filed from the gaps; audit doc has a
2026-08-03 addendum closing its read-time-model check). **Release-3 exit = `OLIVIA_ARCHITECTURE_AUDIT_2026-08-02.md` Appendix A
re-scores ≥8/10 (baseline 6/10)** — retrieval 3→≥7 (#40), identity 6→≥8 (#41), the rest hold.

**#40 story:** *a question phrased differently from how it was written still finds the answer —
and answers prefer recent, credible content.* Verified live: `content_search` requires a keyword
hit when terms are given (semantic-only rows NEVER return), HNSW 275MB / 0 scans, retrieval step
0.4–11s. **Build:** `content_search_v2` SIDE-BY-SIDE (never in-place) → ANN wide net (vector as
LEADING sort) + `search_tsv` keyword candidates → **RRF, never blended scores** → recency decay +
authority boost → stop embedding empty/sub-30-char rows (keep them keyword/thread-reachable).
Point the STAGING workflow at v2 → probes → TEST slice (propose to Andy first) → Andy flips prod.
**Traps:** NOTIFY pgrst + hammer-test after DDL · a timeout reads as "no data found" · one-word
FB comments are sometimes THE answer — never delete rows, only unembed. **Then #41 same week**
(identity stamping — the FK wants `airtable_id` NOT `at_member_id`; backfill losslessness decays).

Working order after: #45 identity-rest → #39 attribution (v2 returns author/post_author labels —
makes #39 nearly free) → #46 member_events (our surfaces) → #42 place_city → R3 features
(#38, #29, #44 graph after #29's memo …) → close-out #32/#14/**#43 RE-AUDIT ≥8/10**/#34.
**Andy's side this week:** `member_events` feed (GROUPOS_PAT + app event logging) — the only
irreversible daily loss. **Release notes `OLIVIA_RELEASE_NOTES_R1_R2.md` = DRAFTED, waiting on
Andy to validate + post** (never posted by me).

## Watch-outs (new this session)
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
