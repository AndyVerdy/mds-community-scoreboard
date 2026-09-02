# Olivia model bench — versioned snapshot (2026-09-02, ticket #156)

The LIVE copy runs from `/Users/Born/mds-scorecard-tools/` (not a git repository); this folder is a
snapshot committed so the harness cannot be lost. `olivia_eval.py` (the daily eval, which carries the
shared judge `judge_prompt` / `judge_one` / `judge_one_openai`) is NOT copied — it is production code that
lives only in the tools folder.

Pipeline: `kimi_harvest.py` (exact `Answer Seed` bodies out of staging executions) → `kimi_bench.py`
(Anthropic loop as prod, OpenAI Responses loop, dual judge, per-run report) → `bench_compare.py`
(three-way report). `bench_tools.py` mirrors the live `Attach Embedding` / `Answer Tool` / `Answer Merge`
nodes and must be re-checked against the prod snapshot before any new bench (85 tests:
`python3 -m unittest discover -s tests`). Results: `OLIVIA_MODEL_COMPARE_2026-09-02.md`.
