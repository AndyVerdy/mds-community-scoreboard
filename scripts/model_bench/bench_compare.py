#!/usr/bin/env python3
"""Side-by-side of N bench runs: every question, every answer, both judges' verdicts.

  python3 bench_compare.py claude-sonnet-5 gpt-5.6-terra-medium gpt-5.6-terra-none \
      --out /Users/Born/Scorecard/OLIVIA_MODEL_COMPARE_2026-09-02.md
"""
import argparse, glob, json, os

from kimi_bench import PRICES

REPORT_DIR = "/Users/Born/Scorecard"
OK = ("PASS", "PARTIAL", "FAIL")
MARK = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "🔴"}


# kimi_bench stamps YYYYMMDD-HHMM. The old HHMM-only stamp sorted lexically, so a July run at
# 22:50 beat every run of today that finished before 22:50 — newest('claude-sonnet-5') really did
# return the 7-row 2026-07-29 file (no `tag`, no `judges`). Requiring the DATE in the glob keeps
# legacy files out of the comparison entirely; the `_` before it keeps `claude-sonnet-5` from
# matching `claude-sonnet-5-none`.
STAMP = "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]"


def newest(tag):
    files = sorted(glob.glob(os.path.join(REPORT_DIR, f"OLIVIA_MODEL_BENCH_{tag}_{STAMP}.json")))
    if not files:
        raise SystemExit(f"no bench json for {tag} (looking for "
                         f"OLIVIA_MODEL_BENCH_{tag}_YYYYMMDD-HHMM.json in {REPORT_DIR})")
    return json.load(open(files[-1])), os.path.basename(files[-1])


def _verdict(r, judge):
    return (r.get("verdicts") or {}).get(judge, {}).get("verdict") if judge else r.get("verdict")


def _steady(r, model):
    p = PRICES[model]
    m = r["metrics"]
    return (m["in"] * p["in"] + m["out"] * p["out"] + m["cache_r"] * p["cache_r"]) / 1e6


def stats(rows, model, judge=None):
    scored = [r for r in rows if _verdict(r, judge) in OK]
    fails = [r for r in scored if _verdict(r, judge) == "FAIL"]
    parts = [r for r in scored if _verdict(r, judge) == "PARTIAL"]
    n = max(1, len(rows))
    return {
        "n": len(rows), "scored": len(scored), "fails": len(fails), "parts": len(parts),
        "fail_pct": 100.0 * len(fails) / max(1, len(scored)),
        "cost": sum(r["cost"] for r in rows) / n,
        # steady state = what production pays on a warm prefix: cache reads + fresh input +
        # output, no cache writes (Anthropic books writes explicitly, OpenAI charges none —
        # raw totals would penalise Claude for a one-off it amortises in production).
        "steady": sum(_steady(r, model) for r in rows) / n,
        "secs": sorted(r["secs"] for r in rows)[len(rows) // 2],
        "model_secs": sum(r.get("model_secs", 0) for r in rows) / n,
        "out": sum(r["metrics"]["out"] for r in rows) / n,
        "reasoning": sum(r["metrics"].get("reasoning", 0) for r in rows) / n,
        "calls": sum(r["metrics"]["calls"] for r in rows) / n,
        "truncated": sum(r["metrics"].get("truncated", 0) for r in rows),
        "errors": len([r for r in rows if r["answer"].startswith("[")]),
    }


def disagreements(rows):
    out = []
    for r in rows:
        vs = {v.get("verdict") for v in (r.get("verdicts") or {}).values() if v.get("verdict") in OK}
        if len(vs) > 1:
            out.append(r)
    return out


def conditions_sentence(runs):
    """Warm-up and forced-first-fetch, READ OFF the envelopes — the report used to assert
    "WARM … forced first fetch on" whatever the run had actually done."""
    passes = [r.get("passes") for r in runs]
    parity = [r.get("parity") for r in runs]
    if all(isinstance(p, int) and p > 1 for p in passes):
        warm = "Every run was measured on a WARM prompt cache (a full unscored pass ran first)"
    elif all(p == 1 for p in passes):
        warm = "No warming pass ran (passes: 1), so each run met whatever cache state the API had"
    elif all(isinstance(p, int) for p in passes):
        warm = "Warm-up differs by run (" + ", ".join(f"{r['tag']}: {r.get('passes')}" for r in runs) + " passes)"
    else:
        warm = "Warm-up state is not recorded in every run envelope"
    if all(p is False for p in parity):
        ff = ", with the forced first fetch on for every run"
    elif all(p is True for p in parity):
        ff = ", with the forced first fetch DISABLED for parity"
    elif all(p is not None for p in parity):
        ff = ", but the forced first fetch was not set the same way in every run — see the table"
    else:
        ff = "; the forced-first-fetch setting is not recorded in every run envelope"
    return warm + ff + "."


def budget_sentence(runs):
    """The output budget is a second variable when it differs, and the reader is told so."""
    known = [r for r in runs if r.get("budget")]
    if not known:
        return "Output token budgets are not recorded in these run envelopes."
    if len(known) == len(runs) and len({r["budget"] for r in known}) == 1:
        return f"Both vendors ran the same output budget ({known[0]['budget']:,} tokens)."
    return ("Output token budgets DIFFER, so part of any output-token, latency or cost gap is the "
            "budget rather than the model: "
            + " · ".join(f"{r['tag']} {r['budget']:,}" for r in known)
            + ". A model that reasons inside its output count needs room for the reasoning AND "
              "the answer.")


def judge_cell(run, judge, stats_dict, cell_type="fail_pct"):
    """Return '—' if judge not in run's judges list or scored is 0; else formatted stat.

    cell_type: "fail_pct" returns **X.X%**, "counts" returns "P / PA / F"
    """
    if judge not in run.get("judges", []) or stats_dict.get("scored", 0) == 0:
        return "—"
    if cell_type == "fail_pct":
        return f"**{stats_dict['fail_pct']:.1f}%**"
    elif cell_type == "counts":
        s = stats_dict
        return f"{s['scored']-s['fails']-s['parts']} / {s['parts']} / {s['fails']}"
    return "—"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="+")
    ap.add_argument("--out", default=os.path.join(REPORT_DIR, "OLIVIA_MODEL_COMPARE.md"))
    a = ap.parse_args()

    runs = []
    for t in a.tags:
        d, f = newest(t)
        runs.append({"tag": t, "model": d["model"], "effort": d.get("effort"), "judges": d.get("judges") or [],
                     "budget": d.get("max_output_tokens"), "passes": d.get("passes"),
                     "parity": d.get("parity"),
                     "rows": d["rows"], "by_id": {r["id"]: r for r in d["rows"]}, "file": f})
    judges = []
    for run in runs:
        for j in run["judges"]:
            if j not in judges:
                judges.append(j)
    S = {run["tag"]: stats(run["rows"], run["model"]) for run in runs}
    SJ = {(run["tag"], j): stats(run["rows"], run["model"], judge=j) for run in runs for j in judges}
    D = {run["tag"]: disagreements(run["rows"]) for run in runs}

    hdr = "| | " + " | ".join(r["tag"] for r in runs) + " |"
    sep = "|---|" + "---|" * len(runs)
    def line(label, fn):
        return f"| {label} | " + " | ".join(fn(r) for r in runs) + " |"
    L = [f"# Model comparison — " + " vs ".join(r["tag"] for r in runs), "",
         "Same questions, same system prompt, same tool schemas, same Supabase RPCs and app routes, "
         "same Voyage embeddings, same judges, same expected answers. " + conditions_sentence(runs)
         + " The only variable is the model"
         + (" (and, for Terra, the reasoning effort)" if any(r["effort"] for r in runs) else "") + ". "
         + budget_sentence(runs)
         + " Answer Merge's S1–S16 evidence stamps are not replicated; absolute fail % is not "
           "comparable to the daily eval.",
         "", hdr, sep]
    for j in judges:
        L.append(line(f"**FAIL %** ({j} judge)", lambda r, judge=j: judge_cell(r, judge, SJ[(r['tag'], judge)], cell_type="fail_pct")))
        L.append(line(f"PASS / PARTIAL / FAIL ({j} judge)", lambda r, judge=j: judge_cell(r, judge, SJ[(r['tag'], judge)], cell_type="counts")))
    L += [line("judge disagreements", lambda r: str(len(D[r["tag"]]))),
          line("**$ per answer** (warm prefix)", lambda r: f"**${S[r['tag']]['steady']:.5f}**"),
          line("$ per answer, cold", lambda r: f"${S[r['tag']]['cost']:.5f}"),
          line("latency, median", lambda r: f"{S[r['tag']]['secs']:.1f}s"),
          line("model time per answer", lambda r: f"{S[r['tag']]['model_secs']:.1f}s"),
          line("output tokens per answer", lambda r: f"{S[r['tag']]['out']:.0f}"),
          line("reasoning tokens per answer", lambda r: f"{S[r['tag']]['reasoning']:.0f}"),
          line("model calls per answer", lambda r: f"{S[r['tag']]['calls']:.1f}"),
          line("loop errors", lambda r: str(S[r['tag']]['errors'])),
          line("truncated model calls", lambda r: str(S[r['tag']]['truncated'])),
          line("output token budget", lambda r: f"{r['budget']:,}" if r.get("budget") else "not recorded"),
          line("warm-up passes", lambda r: str(r["passes"]) if r.get("passes") is not None else "not recorded"),
          line("forced first fetch", lambda r: ("off (parity)" if r["parity"] else "on")
               if r.get("parity") is not None else "not recorded"),
          line("effort", lambda r: r["effort"] or "thinking off (prod)"),
          "", "Sources: " + " · ".join(f"`{r['file']}`" for r in runs), "",
          "Prices ($/1M): " + " · ".join(f"{m} in {p['in']} / out {p['out']} / cache read {p['cache_r']}"
                                          for m, p in PRICES.items() if m in {r['model'] for r in runs}),
          "", "---", "", "## Judge disagreements", ""]
    for run in runs:
        L.append(f"### {run['tag']} — {len(D[run['tag']])} question(s) where the judges differ")
        for r in D[run["tag"]]:
            vs = " · ".join(f"{j}: {r['verdicts'][j].get('verdict')} ({r['verdicts'][j].get('reason', '')})" for j in judges if j in r.get("verdicts", {}))
            L.append(f"- **Q{r['id']}** [{r.get('class', '')}] {r['q']} — {vs}")
        L.append("")
    L += ["---", "", "## Every question, every answer", ""]
    ids = sorted(set().union(*[set(run["by_id"]) for run in runs]))
    for qid in ids:
        any_row = next(run["by_id"][qid] for run in runs if qid in run["by_id"])
        L += [f"### Q{qid} · {any_row.get('class', '')}", f"**{any_row['q']}**", ""]
        for run in runs:
            r = run["by_id"].get(qid)
            if not r:
                L.append(f"**{run['tag']}** — not run")
                continue
            v = r.get("verdict") or ("ERROR" if r["answer"].startswith("[") else "—")
            L.append(f"**{run['tag']}** {MARK.get(v, '⚠️')} {v} · {r['secs']}s · ${r['cost']:.4f} · {r['metrics']['calls']} calls")
            for j in judges:
                jv = (r.get("verdicts") or {}).get(j)
                if jv:
                    L.append(f"> {j}: {jv.get('verdict')} — {jv.get('reason', '')}")
            L += ["", "```", (r["answer"] or "").strip()[:2000], "```", ""]
        L += ["---", ""]

    open(a.out, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:24]))
    print(f"\n-> {a.out}  ({' vs '.join(str(len(run['rows'])) for run in runs)} questions)")


if __name__ == "__main__":
    main()
