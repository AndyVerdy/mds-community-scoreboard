#!/usr/bin/env python3
"""Model bench for Olivia's answering loop — same questions, same data, same judges.

Replays the harvested seeds (kimi_harvest.py) through the SAME tool loop the workflow runs,
against any vendor. Nothing is mocked: the system prompt and tool schemas are the ones the
workflow built, the tools call the same gated Supabase RPCs and app routes with the same keys
(bench_tools.py mirrors the graph's tool layer), embeddings come from the same Voyage model,
and the answers are graded by the same judges against the same expected answers. The only
variable is the model. No n8n workflow is touched.

  python3 kimi_bench.py --model claude-sonnet-5 --passes 2 --seeds kimi_seeds_2026-09-02.json
  python3 kimi_bench.py --model gpt-5.6-terra --effort medium --passes 2 --workers 3 --seeds …
  python3 kimi_bench.py --model gpt-5.6-terra --effort none   --passes 2 --workers 3 --seeds …

Report -> /Users/Born/Scorecard/OLIVIA_MODEL_BENCH_<tag>_<HHMM>.md  (+ .json beside it)
"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

import bench_tools as bt

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "/Users/Born/mds-digest-web/.env.local"
REPORT_DIR = "/Users/Born/Scorecard"
PROBE = "17866578153"                      # fallback asker when a seed carries no phone
ANTHROPIC = "https://api.anthropic.com/v1/messages"
OPENAI = "https://api.openai.com/v1/responses"      # chat completions refuses tools + reasoning on Terra
MAX_ITER, MAX_TOKENS = 5, 2000            # the graph: max_iter 5, max_tokens 2000
# Models that reason inside the output budget need room for the reasoning AND the answer, or
# the comparison measures the budget, not the model (Kimi truncated 13/72 answers, 2026-07-30).
THINKING_FORCED_TOKENS = 8000
RETRY_SLEEP = (5, 15, 30)

# $ per 1M tokens — list prices on 2026-09-02, no intro discounts, so vendors compare like for like.
# OpenAI charges nothing for cache writes; Anthropic bills them at 1.25× input.
PRICES = {
    "claude-sonnet-5":  {"api": "anthropic", "in": 2.00, "out": 10.00, "cache_r": 0.20, "cache_w": 2.50},
    "claude-haiku-4-5-20251001": {"api": "anthropic", "in": 1.00, "out": 5.00, "cache_r": 0.10, "cache_w": 1.25},
    "gpt-5.6-terra":    {"api": "openai", "in": 2.00, "out": 12.00, "cache_r": 0.20, "cache_w": 0.0},
}


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


K = {}
PARITY = False
MODEL_SECS = {}


def run_tag(model, effort):
    """Report name: the model, plus the effort for vendors where it is a real setting."""
    return f"{model}-{effort}" if PRICES[model]["api"] == "openai" else model


def new_metrics():
    # `truncated` counts model calls that hit the output budget (Anthropic stop_reason max_tokens,
    # OpenAI status incomplete). A truncated call is not a wrong answer — it is a MEASUREMENT of
    # the budget, and the two vendors do not run the same budget (see max_output_tokens below).
    return {"in": 0, "out": 0, "cache_r": 0, "cache_w": 0, "reasoning": 0, "calls": 0, "iters": 0,
            "truncated": 0}


def add_anthropic_usage(m, u):
    m["in"] += u.get("input_tokens", 0) or 0
    m["out"] += u.get("output_tokens", 0) or 0
    m["cache_r"] += u.get("cache_read_input_tokens", 0) or 0
    m["cache_w"] += u.get("cache_creation_input_tokens", 0) or 0
    m["calls"] += 1


def add_openai_usage(m, u):
    """Responses API usage: cached tokens are a subset of input_tokens; reasoning is a subset
    of output_tokens (billed as output — kept in `out`, reported separately as `reasoning`)."""
    cached = (u.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0
    m["in"] += max(0, (u.get("input_tokens", 0) or 0) - cached)
    m["cache_r"] += cached
    m["out"] += u.get("output_tokens", 0) or 0
    m["reasoning"] += (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0) or 0
    m["calls"] += 1


def retryable(d):
    """429 / overload / 5xx / transport — never a 400 (a bad request is a bug, not a blip)."""
    err = d.get("error") if isinstance(d, dict) else None
    if not err:
        return False
    if isinstance(err, str):
        return True                                            # transport: curl text, no JSON
    kind = f"{err.get('type', '')} {err.get('code', '')}"
    return any(k in kind for k in ("rate_limit", "overloaded", "server_error", "api_error", "timeout"))


def post(url, headers, body, timeout=180):
    return bt.post(url, headers, body, timeout)          # -> (http_status, parsed_body)


def _err(d):
    return str(d.get("error") if isinstance(d, dict) else d)[:80]


def post_retry(url, headers, body, timeout=180):
    """-> (http_status, parsed_body). The status comes back with the body now, so a 429 or a 502
    whose body is an HTML page (not JSON) is still recognised as retryable."""
    st, d = post(url, headers, body, timeout)
    for wait in RETRY_SLEEP:
        if not (retryable(d) or st in (408, 429) or st >= 500):
            return st, d
        print(f"    retry in {wait}s: HTTP {st or '-'} {_err(d)}", flush=True)
        time.sleep(wait)
        st, d = post(url, headers, body, timeout)
    return st, d


def run_tool(name, args, seed):
    return bt.run_tool(name, args, seed["tools"], K, seed.get("phone") or PROBE)


# ---------------------------------------------------------------- message shapes
def anthropic_messages(seed):
    """The harvested array as-is, with the graph's moving cache mark on the last user block."""
    msgs = seed.get("messages") or [{"role": "user", "content": seed["user"]}]
    msgs = [{"role": m["role"], "content": m["content"]} for m in msgs]
    last = msgs[-1]["content"]
    blocks = [dict(b) for b in last] if isinstance(last, list) else [{"type": "text", "text": last}]
    blocks[-1]["cache_control"] = {"type": "ephemeral"}
    msgs[-1] = {"role": "user", "content": blocks}
    return msgs


def responses_input(seed):
    """Same turns for the Responses API: text only (history turns are text, so nothing is lost)."""
    items = []
    for m in seed.get("messages") or [{"role": "user", "content": seed["user"]}]:
        c = m["content"]
        text = c if isinstance(c, str) else "\n".join(
            b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        items.append({"role": m["role"], "content": text})
    return items


def responses_tools(tools):
    return [{"type": "function", "name": t["name"], "description": t.get("description", ""),
             "parameters": t["input_schema"]} for t in tools]


# ---------------------------------------------------------------- the loop, per vendor
def loop_anthropic(seed, model):
    """Anthropic caching is EXPLICIT — the graph marks system, the last tool schema and a
    moving message breakpoint. Same three breakpoints as the Answer Claude node."""
    msgs = anthropic_messages(seed)
    system = [{"type": "text", "text": seed["system"], "cache_control": {"type": "ephemeral"}}]
    tools = [dict(t) for t in seed["tools"]]
    tools[-1]["cache_control"] = {"type": "ephemeral"}
    m = new_metrics()
    # MAX_ITER + 1 model calls, as the graph runs it: Answer Parse gates the tool branch on
    # `state.iter < state.max_iter`, so five tool ROUNDS are followed by a sixth call that answers
    # (finalize(text || 'Sorry…')). Looping MAX_ITER times instead ran the tools on call 5 — real
    # Supabase spend — then threw the results away and scored the row as an error.
    for it in range(MAX_ITER + 1):
        body = {"model": model, "max_tokens": MAX_TOKENS, "thinking": {"type": "disabled"},
                "system": system, "tools": tools, "messages": msgs}
        if it == 0 and not PARITY:
            body["tool_choice"] = {"type": "any"}        # forced first fetch, as the graph does
        _t = time.time()
        _st, d = post_retry(ANTHROPIC, {"x-api-key": K["anthropic"], "anthropic-version": "2023-06-01",
                                        "content-type": "application/json"}, body)
        MODEL_SECS[seed["id"]] = MODEL_SECS.get(seed["id"], 0.0) + (time.time() - _t)
        add_anthropic_usage(m, d.get("usage") or {})
        content = d.get("content")
        if not isinstance(content, list):
            return f"[API ERROR] {str(d)[:200]}", m
        stop = d.get("stop_reason")
        if stop == "max_tokens":
            m["truncated"] += 1
        uses = [c for c in content if c.get("type") == "tool_use"]
        if stop == "tool_use" and uses and m["iters"] < MAX_ITER:
            m["iters"] += 1
            stripped = [{"role": x["role"], "content": (
                [{k: v for k, v in b.items() if k != "cache_control"} for b in x["content"]]
                if isinstance(x["content"], list) else x["content"])} for x in msgs]
            results = [{"type": "tool_result", "tool_use_id": t["id"],
                        "content": run_tool(t["name"], t.get("input"), seed)} for t in uses]
            results[-1]["cache_control"] = {"type": "ephemeral"}
            msgs = stripped + [{"role": "assistant", "content": content},
                               {"role": "user", "content": results}]
            continue
        text = "".join(c.get("text", "") for c in content if c.get("type") == "text").strip()
        if not text:
            # an empty content with no usable tool call is an ERROR row, never a scored answer
            why = ("max_tokens — truncated before any text" if stop == "max_tokens"
                   else "tool_use at the iteration cap" if uses else "no text block in the reply")
            return f"[EMPTY ANSWER] status={stop} reason={why}", m
        return text, m
    return "[no final answer inside iteration cap]", m          # unreachable: the last lap answers


def loop_openai(seed, model, effort):
    """Same loop on the Responses API. Stateless replay (store:false): every output item —
    reasoning items included, encrypted — goes back into the next request, then the tool
    outputs. OpenAI's prompt cache is automatic on a stable prefix, so no cache marks."""
    tools = responses_tools(seed["tools"])
    inp = responses_input(seed)
    m = new_metrics()
    for it in range(MAX_ITER + 1):                       # see loop_anthropic: 5 tool rounds + answer
        body = {"model": model, "instructions": seed["system"], "input": inp, "tools": tools,
                "tool_choice": "auto" if (it or PARITY) else "required",
                "max_output_tokens": MAX_TOKENS if effort == "none" else THINKING_FORCED_TOKENS,
                "reasoning": {"effort": effort}, "store": False,
                "include": ["reasoning.encrypted_content"]}
        _t = time.time()
        _st, d = post_retry(OPENAI, {"Authorization": f"Bearer {K['openai']}", "Content-Type": "application/json"}, body)
        MODEL_SECS[seed["id"]] = MODEL_SECS.get(seed["id"], 0.0) + (time.time() - _t)
        add_openai_usage(m, d.get("usage") or {})
        out = d.get("output")
        if not isinstance(out, list):
            return f"[API ERROR] {str(d)[:200]}", m
        incomplete = (d.get("incomplete_details") or {}).get("reason")
        if d.get("status") == "incomplete" or incomplete:
            m["truncated"] += 1
        calls = [o for o in out if o.get("type") == "function_call"]
        if calls and m["iters"] < MAX_ITER:
            m["iters"] += 1
            inp = inp + out
            for c in calls:
                try:
                    args = json.loads(c.get("arguments") or "{}")
                except Exception:
                    args = {}
                inp.append({"type": "function_call_output", "call_id": c["call_id"],
                            "output": run_tool(c["name"], args, seed)})
            continue
        text = "".join(p.get("text", "") for o in out if o.get("type") == "message"
                       for p in (o.get("content") or []) if p.get("type") == "output_text").strip()
        if not text:
            why = incomplete or ("function_call at the iteration cap" if calls else "no output_text")
            return f"[EMPTY ANSWER] status={d.get('status')} reason={why}", m
        return text, m
    return "[no final answer inside iteration cap]", m          # unreachable: the last lap answers


def loop_error_verdict(answer):
    """A row that never produced an answer is an ERROR, not a FAIL.

    The judge grades "[API ERROR] … 429" and "[no final answer inside iteration cap]" as FAIL,
    which hands the fail % to whichever vendor had the worse hour on its API rather than the
    worse model. Loop errors keep their own line in the report instead."""
    if str(answer or "").startswith("["):
        return {"verdict": "ERROR", "reason": "loop error — not graded", "fail_class": None}
    return None


def cost(model, m):
    p = PRICES[model]
    return (m["in"] * p["in"] + m["out"] * p["out"]
            + m["cache_r"] * p["cache_r"] + m["cache_w"] * p["cache_w"]) / 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(PRICES))
    ap.add_argument("--effort", default="medium", choices=["none", "low", "medium", "high"],
                    help="OpenAI reasoning effort (ignored for other vendors). 'none' = parity with "
                         "prod's thinking-off Claude; 'medium' = OpenAI's default")
    ap.add_argument("--seeds", default=os.path.join(HERE, "kimi_seeds.json"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids", help="comma-separated question ids")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-judge", action="store_true", help="answers only, no grading spend")
    ap.add_argument("--judges", default="claude-sonnet-5,gpt-5.6-terra",
                    help="comma-separated judge models; the FIRST is the primary verdict")
    ap.add_argument("--passes", type=int, default=1,
                    help="run the set N times and report the LAST pass — pass 1 warms the cache so "
                         "neither vendor is measured cold while the other is warm")
    ap.add_argument("--parity", action="store_true",
                    help="drop the forced first fetch for EVERY model")
    a = ap.parse_args()

    global PARITY
    PARITY = a.parity
    e = {}
    for line in open(ENV):
        if "=" in line and not line.startswith("#"):
            k_, v_ = line.strip().split("=", 1)
            e[k_] = v_
    K.update({"anthropic": e["CENTURION_ANTHROPIC_API_KEY"], "openai": e.get("OPENAI_API_KEY", ""),
              "supa": e["SUPABASE_SECRET_KEY"],
              "voyage": e["VOYAGE_API_KEY"],
              "olivia_secret": e.get("OLIVIA_SCHEDULE_SECRET") or e.get("OLIVIA_IOS_SECRET", "")})

    seeds = json.load(open(a.seeds))["seeds"]
    if a.ids:
        want = {int(x) for x in a.ids.split(",")}
        seeds = [s for s in seeds if s["id"] in want]
    if a.limit:
        seeds = seeds[:a.limit]
    api = PRICES[a.model]["api"]
    tag = run_tag(a.model, a.effort)
    # the output budget is NOT the same for both vendors: a model that reasons inside the output
    # count needs room for the reasoning AND the answer. Recorded so the compare can say so.
    budget = MAX_TOKENS if api == "anthropic" or a.effort == "none" else THINKING_FORCED_TOKENS
    runner = (lambda s: loop_anthropic(s, a.model)) if api == "anthropic" else (lambda s: loop_openai(s, a.model, a.effort))
    print(f"BENCH {tag} ({api}) · {len(seeds)} questions · {a.workers} parallel · seeds {os.path.basename(a.seeds)}", flush=True)

    def one(s):
        t0 = time.time()
        MODEL_SECS[s["id"]] = 0.0
        ans, m = runner(s)
        return {"id": s["id"], "class": s.get("class"), "q": s["q"], "answer": ans,
                "secs": round(time.time() - t0, 1),
                "model_secs": round(MODEL_SECS.get(s["id"], 0.0), 1), "metrics": m,
                "cost": round(cost(a.model, m), 5)}

    for p_i in range(a.passes):
        with ThreadPoolExecutor(max_workers=a.workers) as pool:
            rows = list(pool.map(one, seeds))
        if p_i + 1 < a.passes:
            warm = sum(r["metrics"]["cache_r"] for r in rows)
            print(f"  -- pass {p_i+1}/{a.passes} done (cache reads {warm:,}) — warming, not scored",
                  flush=True)
    for r in rows:
        flag = "ERR" if r["answer"].startswith("[") else "ok "
        print(f"  Q{r['id']} {flag} {r['secs']:5.1f}s ${r['cost']:.4f} "
              f"{r['metrics']['calls']}c/{r['metrics']['iters']}t {r['q'][:44]}", flush=True)

    judges = [] if a.no_judge else [j.strip() for j in a.judges.split(",") if j.strip()]
    if judges:
        sys.path.insert(0, HERE)
        import olivia_eval as oe
        by_id = {s["id"]: s for s in seeds}

        def judge(jm, r):
            err = loop_error_verdict(r["answer"])
            if err:
                return err
            q = by_id[r["id"]]
            if PRICES.get(jm, {}).get("api") == "openai":
                return oe.judge_one_openai(K["openai"], q, r["answer"], model=jm, sbkey=K["supa"])
            return oe.judge_one(K["anthropic"], q, r["answer"], model=jm, sbkey=K["supa"])

        for jm in judges:
            print(f"judging with {jm}…", flush=True)
            with ThreadPoolExecutor(max_workers=8) as pool:
                vs = list(pool.map(lambda r: judge(jm, r), rows))
            for r, v in zip(rows, vs):
                r.setdefault("verdicts", {})[jm] = v
        for r in rows:                                   # primary = the first judge
            v = r["verdicts"][judges[0]]
            r["verdict"], r["reason"], r["fail_class"] = v.get("verdict"), v.get("reason"), v.get("fail_class")

    ok = [r for r in rows if not r["answer"].startswith("[")]
    scored = [r for r in rows if r.get("verdict") in ("PASS", "PARTIAL", "FAIL")]
    fails = [r for r in scored if r["verdict"] == "FAIL"]
    parts = [r for r in scored if r["verdict"] == "PARTIAL"]
    spend = sum(r["cost"] for r in rows)
    tot = {k: sum(r["metrics"].get(k, 0) for r in rows)
           for k in ("in", "out", "cache_r", "cache_w", "calls", "reasoning", "truncated")}
    # steady state = what production pays once the prefix is warm: cache reads, fresh input and
    # output only. Cache WRITES are a one-off per prefix; charging them per answer (and this bench
    # runs questions in parallel, so every worker writes its own copy) overstates cost several fold.
    p = PRICES[a.model]
    steady = (tot["in"] * p["in"] + tot["out"] * p["out"] + tot["cache_r"] * p["cache_r"]) / 1e6
    n = max(1, len(rows))

    def judge_summary(jm):
        vs = [r.get("verdicts", {}).get(jm, {}).get("verdict") for r in rows]
        return (f"- **{jm} judge:** PASS {vs.count('PASS')} · PARTIAL {vs.count('PARTIAL')} · "
                f"FAIL {vs.count('FAIL')} · ERROR {len(vs) - vs.count('PASS') - vs.count('PARTIAL') - vs.count('FAIL')}\n")
    head = (f"# Model bench — {tag} — {len(rows)} questions\n\n"
            f"- **Answer quality:** " + (f"{len(scored)} judged · PASS {len(scored)-len(fails)-len(parts)}"
                                        f" · PARTIAL {len(parts)} · **FAIL {len(fails)} "
                                        f"({100.0*len(fails)/max(1,len(scored)):.1f}%)**"
                                        if scored else "not judged") + "\n"
            f"- **Cost:** ${spend:.4f} total · ${spend/n:.5f} per answer cold · "
            f"**${steady/n:.5f} per answer steady-state** (warm prefix, cache-write excluded — "
            f"the number production actually pays; list prices, no intro discount)\n"
            f"- **Latency:** median {sorted(r['secs'] for r in rows)[len(rows)//2]:.1f}s · "
            f"max {max(r['secs'] for r in rows):.1f}s\n"
            f"- **Tokens:** fresh in {tot['in']:,} · cached in {tot['cache_r']:,} "
            f"({100.0*tot['cache_r']/max(1,tot['in']+tot['cache_r']):.0f}% cached) · out {tot['out']:,} · "
            f"{tot['calls']} model calls ({tot['calls']/n:.1f} per answer)\n"
            f"- **Reasoning tokens:** {tot['reasoning']:,} ({tot['reasoning']/n:.0f} per answer, inside the output count)\n"
            f"- **Effort:** {a.effort if api == 'openai' else 'n/a (thinking disabled, as prod)'}\n"
            f"- **Blended rate:** ${1e6*steady/max(1,tot['in']+tot['cache_r']+tot['out']):.2f} per "
            f"1M tokens (all tokens, cache discounts included — comparable to the console's own number)\n"
            f"- **Model time vs tool time:** model "
            f"{sum(r['model_secs'] for r in rows)/n:.1f}s per answer, rest is Supabase/Voyage "
            f"(identical infrastructure for both vendors)\n"
            f"- **Output budget:** {budget:,} "
            f"({'max_tokens' if api == 'anthropic' else 'max_output_tokens'}) · "
            f"truncated calls {tot['truncated']}\n"
            f"- **Forced first fetch:** {'DISABLED for parity' if PARITY else 'per model'}\n"
            f"- **Warm-up passes:** {a.passes} ({'warm' if a.passes > 1 else 'COLD — no warming pass'})\n"
            f"- **Loop errors:** {len(rows)-len(ok)}\n")
    head += "".join(judge_summary(jm) for jm in judges)
    lines = [head]
    for r in rows:
        if r.get("verdict") in ("FAIL", "PARTIAL") or r["answer"].startswith("["):
            lines.append(f"- **{r.get('verdict') or 'ERROR'}** Q{r['id']} [{r['class']}] {r['q']}\n"
                         f"  - {r.get('reason') or r['answer'][:160]}")
    stamp = time.strftime("%Y%m%d-%H%M")   # DATE + time: an HHMM-only stamp sorts a July run on
                                           # top of today's (bench_compare.newest picked 2250)
    base = os.path.join(REPORT_DIR, f"OLIVIA_MODEL_BENCH_{tag}_{stamp}")
    open(base + ".md", "w").write("\n".join(lines) + "\n")
    json.dump({"model": a.model, "tag": tag, "effort": a.effort if api == "openai" else None,
               "seeds": os.path.basename(a.seeds), "judges": judges,
               "max_output_tokens": budget, "passes": a.passes, "parity": PARITY,
               "rows": rows}, open(base + ".json", "w"), indent=1)
    print("\n" + head)
    print(f"report -> {base}.md")


if __name__ == "__main__":
    main()
