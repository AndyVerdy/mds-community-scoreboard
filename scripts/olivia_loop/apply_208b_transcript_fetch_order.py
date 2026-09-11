#!/usr/bin/env python3
"""#208 lap 2 — the transcript fetch was being overwritten two lines later (STAGING only).

The prod proof after the promote caught it: Q7901 ("a speaker spoke about Trybe - what was the
context?") still denied the Singapore sessions mention it, and the stored plan showed
`raw_params = {p_terms: [], p_sources: ['fb_post'], p_limit: 0}` - the videos lane's own empty
second fetch, not the transcript search #208 set. The block had been inserted directly after
`if (_callType) …`, and the lane resets raw_op/raw_params a few lines further down, so the
assignment never survived.

It passed 4/4 on staging for the wrong reason: `sources_used` shows the agent called
content_search three times on its own and happened to find the passage once. That is exactly the
variance this ticket exists to remove - a deterministic fetch is the point.

Fix: move the block BELOW the reset, so it is the last word on the videos lane's second fetch.
No logic changes - the same regex, the same spelling variants, verified in node against the exact
question text (saidAsk true, terms ["trybe","tribe"]).
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
STAGING_ID = "bqHstPDi84uOhTCJ"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", "X-N8N-API-KEY: " + KEY,
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


RESET = ("  raw_op = 'content_search';\n"
         "  raw_params = { p_phone: mem.to, p_terms: [], p_sources: ['fb_post'], p_limit: 0 };\n"
         "} else if (intent === 'community') {")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    node = next(n for n in nodes if n["name"] == "Plan Request")
    code = node["parameters"]["jsCode"]
    before = len(code)

    # 1. lift the block out of its current place
    start = code.find("  // #190 Q5097 (2026-09-11):")
    if start < 0:
        print("ABORT: #208 block not found", file=sys.stderr)
        return 2
    end = code.find("\n  }\n", code.find("raw_params = { p_phone: mem.to, p_terms: _tt", start))
    if end < 0:
        print("ABORT: could not find the end of the #208 block", file=sys.stderr)
        return 2
    end += len("\n  }\n")
    block = code[start:end]
    if "_saidAsk" not in block or "call_transcript" not in block:
        print("ABORT: lifted the wrong span", file=sys.stderr)
        return 2
    code = code[:start] + code[end:]

    # 2. put it back AFTER the lane's own reset, where nothing can overwrite it
    if code.count(RESET) != 1:
        print(f"ABORT: videos-lane reset anchor x{code.count(RESET)}", file=sys.stderr)
        return 2
    moved = ("  raw_op = 'content_search';\n"
             "  raw_params = { p_phone: mem.to, p_terms: [], p_sources: ['fb_post'], p_limit: 0 };\n"
             + block.rstrip("\n") + "\n"
             "} else if (intent === 'community') {")
    code = code.replace(RESET, moved)

    node["parameters"]["jsCode"] = code
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print(f"Plan Request: {before} -> {len(code)} chars (block moved below the reset)")
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
