# Eval bank snapshots

`mds-scorecard-tools/` is **not a git repo**, so the canonical bank files there have no history.
These dated copies are the durable record. The live files stay canonical — edit those, then drop
a fresh snapshot here at every session close that changed the bank.

## 2026-08-04 — the retirement generation
- **organic** 134 questions · **96 fired** · 38 retired
- **smoke** 212 questions · **110 fired** · 102 retired
- **New this sweep: ids 3140–3173** (34 organic asks — every uncleared 👎, both of Etienne's
  filed reports, Ian's partner-ranking trio and Eugene's lender pair verbatim).
- **Retirement is now mechanised**: a question clean across every judged run carries
  `retired: true` and is not fired; `olivia_eval.py` fires non-retired only, `OLIVIA_EVAL_ALL=1`
  fires all 212 for a regression sweep. Canary floor of 3 per class so no catastrophic class
  (SENSITIVE, ATTRIBUTION, REPORTS) can ever go unwatched.
- Rows whose truth needs a live check say **"verify at run"** rather than carrying a guess.
- Multi-turn rows (fire by hand, they cannot survive the auto-reset):
  **3141 · 3144 · 3147 · 3150 · 3151 · 3154 · 3162**.
