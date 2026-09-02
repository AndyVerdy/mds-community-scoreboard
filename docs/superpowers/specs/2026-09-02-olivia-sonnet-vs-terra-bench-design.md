# Olivia — Claude Sonnet 5 vs GPT-5.6 Terra, price + quality, prod untouched

**Date:** 2026-09-02 · **Ticket:** #156 on `OLIVIA_SPRINT_4.md` · **Status:** design approved by Andy (chat, 2026-09-02), spec pending his review.

## Goal

Answer the same 100 member questions with Claude Sonnet 5 (prod's model) and OpenAI GPT-5.6 Terra
under identical conditions, and report cost per answer and judged quality side by side, so Andy can
decide on the vendor from data. The running product is not changed, edited, or slowed at any point.

## Story

*As the owner paying Olivia's API bill, I want the same 100 member questions answered by Claude
Sonnet 5 and GPT-5.6 Terra under identical conditions, with cost per answer and judged quality side
by side, so I can decide on the vendor from data, without any change to the running product.*

## Decisions already taken (Andy, 2026-09-02)

| Decision | Choice |
|---|---|
| GPT model | `gpt-5.6-terra` — OpenAI's mid tier ($2 in / $0.20 cached / $12 out per 1M), the Sonnet 5 slot. Sol ($4/$20) is the Opus peer, Luna ($0.20/$1.20) the Haiku peer. |
| Claude model | `claude-sonnet-5`, exactly as prod runs it (thinking off). |
| Question bank | The LOCKED 100-question organic bank, `eval_bank_100_2026-08-16.json`. Not a new bank. |
| Judge | Dual: every answer graded by Sonnet 5 AND by Terra with the identical rubric. Primary number = Sonnet judge (comparable to all past runs). Terra judge = bias check; disagreements listed per question. |
| Where it runs | The standalone bench harness on this Mac (`~/mds-scorecard-tools/kimi_bench.py`), the script that ran the July Kimi comparison. Not inside n8n. |
| Staging use | One silent run of the bank at the staging webhook to harvest seeds. Prod never sees bench traffic. |
| Port to n8n | Not in this ticket. Only if Terra wins does the answer-loop port become the next ticket, with a full through-workflow eval before any promote. |

## How the comparison stays honest

The n8n workflow has three parts; the bench treats each differently:

1. **Before the model** — identity resolve, router, persona, the deterministic preload cascade,
   the system prompt with every rule, the 19 tool schemas. **Replayed byte-identical.** The harvester
   reads the exact `Answer Seed` request body out of each staging execution and hands that same body
   to both vendors. Nothing here is re-implemented.
2. **The model loop** — model picks a tool, we call the Supabase RPC with the same key, feed the
   result back, up to 5 laps (`Answer Merge` behaviour). **Re-implemented in the script**, ~60 lines,
   validated against staging in the Kimi bench. Same RPCs, same key, same Voyage embeddings.
3. **After the model** — `Gate Verdict` clamp, `Fact Check`, link repair, WhatsApp formatting.
   **Not run for either vendor.** Model-independent post-processing; the clamp fired 3 times in
   6,017 answers.

Fairness rules, all stated in the report:
- Same prompt, tools, evidence, RPCs, embeddings, judge rubric.
- Both measured **warm**: 2 passes per vendor, pass 1 warms the prompt cache, pass 2 is scored.
- Forced first fetch (`tool_choice: any` on lap 1) on BOTH — OpenAI supports `tool_choice: "required"`,
  so unlike Kimi there is parity.
- Claude runs `thinking: disabled` (as prod). Terra runs its default reasoning effort (`medium`);
  its reasoning tokens bill as output and are reported separately. A `low`/`none` pass is one flag
  if cost turns out to be the question.
- Known bias, reported not corrected: the prompt is Claude-tuned (rules written against Claude's habits).
- List prices, today's, no intro discounts: Sonnet 5 $2 / $0.20 cache read / $2.50 cache write / $10 out;
  Terra $2 / $0.20 cached / $12 out. The harness's stale Sonnet prices ($3/$15) are corrected.

## Steps

1. **Pre-flight.** `olivia_wf.py status` + `diff prod staging` — staging must equal prod except the
   webhook paths (checked 2026-09-02 03:45Z: identical, prod `d40a837d`, staging `e55a45c6`, lock free).
   Confirm the Anthropic key has credit (a 5-token call) and the OpenAI key reaches `gpt-5.6-terra`
   (`GET /v1/models` — confirmed 2026-09-02).
2. **Harvest run on staging.** Take the `olivia_wf.py lock` for the duration (reason: "#156 harvest —
   no graph edits, occupying staging for 100 silent turns"), fire the locked bank with
   `python3 scripts/run_eval_100.py --staging` (silent mode, no WhatsApp sends), release the lock,
   re-run `diff prod staging` to prove staging was not changed. Tell the peer session via SendMessage.
3. **Harvest seeds.** `kimi_harvest.py --since <start> --until <end>` reads those executions and
   writes `kimi_seeds.json`: per question the `Answer Seed` system prompt, tool schemas, and the
   message array. Target 100/100; any miss is listed with its reason (canned lane never enters the
   loop, so a question that never reaches `Answer Seed` cannot be benched and is reported as such).
4. **Bench.** `kimi_bench.py --model claude-sonnet-5 --passes 2` then
   `kimi_bench.py --model gpt-5.6-terra --passes 2`, 3 workers each (OpenAI key is likely tier 1:
   500K TPM). Each writes `OLIVIA_MODEL_BENCH_<model>_<HHMM>.md/.json` in the repo.
5. **Dual judge** inside the bench: each answer graded by `claude-sonnet-5` and by `gpt-5.6-terra`
   with the same rubric (`olivia_eval.judge_one`), both verdicts stored on the row.
6. **Compare report** `OLIVIA_MODEL_COMPARE_2026-09-02.md` via `bench_compare.py`: headline table
   (fail % per judge, PASS/PARTIAL/FAIL, $/answer steady-state and cold, median + max latency,
   model time, output tokens, model calls per answer, loop errors, judge disagreements), then every
   question with both answers and both verdicts side by side — the July report's layout.
7. **Close.** AC table with proofs, before/after numbers (July: Sonnet 15.3% fail / $0.0135), stream
   log + index line, handoff, memory line. Andy rotates the OpenAI key (it was pasted into chat).

## Harness changes

| File | Change |
|---|---|
| `kimi_harvest.py` | Bank path → the repo's locked bank. Match by question text as today. For `seq` questions keep the full `messages` array from `Answer Seed` (real prior turns), not only the last user block. Configurable `--workflow` (staging id default). |
| `kimi_bench.py` | Add `gpt-5.6-terra` to `PRICES` (`api: "openai"`, in 2.00 / out 12.00 / cache_r 0.20 / cache_w 0). Generalise `loop_kimi` into an OpenAI-compatible loop taking URL + key; OpenAI body uses `max_completion_tokens` and `tool_choice: "required"` on lap 1; `usage.prompt_tokens_details.cached_tokens` → `cache_r`, `completion_tokens_details.reasoning_tokens` recorded separately. Fix Sonnet 5 prices. 429/5xx backoff with retry (3 tries). Seeds with history: Anthropic loop sends the array as-is; OpenAI loop converts Anthropic blocks (text / tool_use / tool_result) to chat-completions shape. Dual judge: two verdict columns; `--judges` default `claude-sonnet-5,gpt-5.6-terra`. |
| `olivia_eval.py` | `judge_one` gets an OpenAI path (same rubric text, same JSON verdict contract) selected by model id. No change to the daily eval's default judge. |
| `bench_compare.py` | Read both verdict columns; add the disagreement section and the reasoning-token column. |
| `.env.local` (mds-digest-web, git-ignored) | `OPENAI_API_KEY` — stored 2026-09-02. |

No n8n workflow, no Supabase object, no repo doc other than the board/log/handoff is changed.

## Acceptance criteria

| AC | Proof required |
|---|---|
| (a) 100/100 seeds harvested from ONE staging run; prod execution log shows no bench traffic | harvest stdout count; `diff prod staging` identical before and after; prod exec ids in the window all real inbound |
| (b) Both models run warm (pass 2 scored), 0 loop errors — or every error listed with the API's message | bench headers: cache reads > 0 on pass 2, "Loop errors: 0" |
| (c) $/answer steady-state and cold per model, from real usage counters at today's list prices | bench headers + `PRICES` table in the report |
| (d) Fail % from the Sonnet judge, cross-checked by the Terra judge, disagreements listed | compare report headline + disagreement section |
| (e) One compare report with all 100 answer pairs | `OLIVIA_MODEL_COMPARE_2026-09-02.md` in the repo |
| (f) Staging left as found, lock released | `olivia_wf.py status` LOCK free; diff identical |

## Cost + time

Roughly $30–50: harvest run ~$5–10 (Claude on staging), bench ~$15–30 (2 vendors × 2 passes),
judges ~$6 (400 verdicts). About 2 hours wall clock. Actuals go in the close block.

## Risks and how they are handled

- **OpenAI rate limits (new key, probably tier 1, 500K TPM):** 3 workers, backoff on 429, a pass
  can be resumed by `--ids`.
- **Sequence questions (20/100):** history carried from the staging run; if a sequence's earlier
  turn is missing from the execution data, the question is benched single-turn and flagged.
- **Canned-lane questions never reach `Answer Seed`:** cannot be benched by construction; listed,
  not silently dropped. The July harvest skipped questions for this reason too; the report shows the true n.
- **Terra output shape:** chat completions returns tool calls with JSON-string arguments; parsed
  with `json.loads`, never string-matched. An empty `content` with no tool call is an error row.
- **Judge bias both ways:** two judges, primary stays Sonnet for comparability; disagreements are
  the reading list for Andy, not auto-resolved.
- **Peer session on staging today:** lock held during the harvest run, SendMessage before and after,
  no graph edits by this ticket.
- **Key hygiene:** the OpenAI key was pasted into chat; Andy rotates it after the run.

## Out of scope

Porting the answer loop to OpenAI inside n8n · Luna / Sol runs · prompt re-tuning for GPT ·
changing the daily eval's judge · any promote.
