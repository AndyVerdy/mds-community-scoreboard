#!/usr/bin/env python3
"""Harvest the EXACT model input for each organic question out of n8n execution history.

Free: reads execution data only, writes nothing to any workflow. For each question it
recovers what Claude was actually handed — the system prompt, the 18 tool schemas, and the
preloaded evidence from the cascade's deterministic retrieval — so a different model can be
given byte-identical input and the comparison is the model, nothing else.

History is kept: sequence questions are fired adjacent, and their prior turns are the input.

  python3 kimi_harvest.py --since 2026-09-02T14:05 --until 2026-09-02T15:35 \
      --bank /Users/Born/Scorecard/eval_bank_100_2026-08-16.json --out kimi_seeds_2026-09-02.json
"""
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "/Users/Born/mds-digest-web/.env.local"
STAGING_ID = "bqHstPDi84uOhTCJ"
DEFAULT_BANK = "/Users/Born/Scorecard/eval_bank_100_2026-08-16.json"   # the LOCKED 100 bank


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(path):
    r = subprocess.run(["curl", "-sS", f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
                        "--max-time", "120"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def node_out(data, name):
    """First output item's json for a node, from an execution's runData."""
    try:
        runs = data["resultData"]["runData"][name]
        return runs[0]["data"]["main"][0][0]["json"]
    except Exception:
        return None


def _text(c):
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def _strip(blocks):
    return [{k: v for k, v in b.items() if k != "cache_control"} if isinstance(b, dict) else b for b in blocks]


def seed_from_execution(data, q):
    """The exact model input of one execution — (seed, None) or (None, reason).
    History is KEPT: sequence questions are fired adjacent on staging, and the prior turns are
    the whole point of them. Only the cache marks come off; the loops put their own back."""
    seed = node_out(data, "Answer Seed")
    if not seed or not seed.get("tools"):
        return None, "no_seed"                         # canned lane — never entered the loop
    msgs = seed.get("messages") or []
    if not msgs or msgs[-1].get("role") != "user":
        return None, "no_seed"
    messages = [{"role": m["role"], "content": _strip(m["content"]) if isinstance(m["content"], list) else m["content"]}
                for m in msgs]
    return {"id": q["id"], "class": q.get("class"), "q": q["q"], "expect": q.get("expect"),
            "soft": q.get("soft"), "seq": q.get("seq"), "phone": seed.get("to"),
            "system": _text(seed["system"]), "tools": _strip(seed["tools"]), "messages": messages,
            "user": _text(msgs[-1]["content"]), "history_turns": len(msgs) - 1}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="ISO, e.g. 2026-09-02T14:05")
    ap.add_argument("--until", required=True)
    ap.add_argument("--bank", default=DEFAULT_BANK)
    ap.add_argument("--workflow", default=STAGING_ID)
    ap.add_argument("--out", default=os.path.join(HERE, "kimi_seeds.json"))
    a = ap.parse_args()

    questions = json.load(open(a.bank))["questions"]
    by_text = {}
    for q in questions:                                # a bank may repeat a text across sequences
        by_text.setdefault(q["q"].strip(), []).append(q)

    ids, cursor = [], None
    while True:
        page = api(f"/executions?workflowId={a.workflow}&limit=100" + (f"&cursor={cursor}" if cursor else ""))
        if not page or not page.get("data"):
            break
        stop = False
        for e in page["data"]:
            st = (e.get("startedAt") or "")[:16]
            if st < a.since:
                stop = True
                continue
            if st <= a.until:
                ids.append(e["id"])
        cursor = page.get("nextCursor")
        if stop or not cursor:
            break
    print(f"{len(ids)} executions in window", flush=True)

    seeds, reasons, skipped = [], {}, {"not_in_bank": 0, "no_inbound": 0}
    for n, eid in enumerate(sorted(ids, key=int)):      # chronological, so repeats pair in order
        d = api(f"/executions/{eid}?includeData=true")
        data = (d or {}).get("data")
        if not data:
            continue
        inb = node_out(data, "Log Inbound")
        if not inb or not inb.get("text"):
            skipped["no_inbound"] += 1
            continue
        cands = by_text.get(inb["text"].strip()) or []
        q = next((c for c in cands if c["id"] not in reasons and c["id"] not in {s["id"] for s in seeds}), None)
        if not q:
            skipped["not_in_bank"] += 1
            continue
        seed, why = seed_from_execution(data, q)
        if seed:
            seed["exec"] = eid
            seeds.append(seed)
        else:
            reasons[q["id"]] = why
        if (n + 1) % 20 == 0:
            print(f"  scanned {n+1}/{len(ids)} · {len(seeds)} seeds", flush=True)

    have = {s["id"] for s in seeds}
    missing = [{"id": q["id"], "q": q["q"], "reason": reasons.get(q["id"], "not_fired")}
               for q in questions if q["id"] not in have]
    json.dump({"harvested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "source_workflow": a.workflow, "bank": a.bank, "seeds": seeds, "missing": missing},
              open(a.out, "w"), indent=1)
    print(f"\n{len(seeds)}/{len(questions)} seeds -> {a.out}  "
          f"({len(seeds[0]['tools']) if seeds else 0} tool schemas, system "
          f"{len(seeds[0]['system']) if seeds else 0} chars, "
          f"{sum(1 for s in seeds if s['history_turns'])} with history)")
    print(f"skipped: {skipped}")
    for m in missing:
        print(f"  MISSING Q{m['id']} [{m['reason']}] {m['q'][:70]}")


if __name__ == "__main__":
    main()
