#!/usr/bin/env python3
"""#39 attribution — STYLE layer (single-sourced in Build Prompt; build_loop.py harvests STYLE
from this node into the Answer Seed, so this edit feeds BOTH the legacy lanes and the loop).

Two changes, both in Build Prompt's STYLE block on STAGING:
  1. ATTRIBUTION rule teaches the new "[→ to NAME]" addressee marker (content_search_v2 now
     emits it when a comment opens with the post author's name) — and forbids echoing it.
  2. NEW VERB PRECISION rule — claims never stronger than the source verbs (launched≠funded,
     the Q3096 mechanism from the #40 slice).

Inserted text is deliberately APOSTROPHE-FREE (the standing n8n expression trap).
Run AFTER content_search_v2_attribution_marker migration, BEFORE build_loop.py.
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://mdsco.app.n8n.cloud/api/v1"
STAGING_ID = "bqHstPDi84uOhTCJ"

OLD_ATTR = ('Never credit a quote, number or opinion to a name that merely appears inside the text.')
NEW_ATTR = ('Never credit a quote, number or opinion to a name that merely appears inside the text. '
            'Some comment bodies BEGIN with an explicit marker "[→ to NAME]" - the system verified NAME '
            'is the ADDRESSEE (the post author being replied to); everything after the marker is spoken BY '
            'the listed author TO that person. Never repeat the marker in your visible reply.')

# VERB PRECISION rides directly after the ATTRIBUTION entry in the STYLE array.
ATTR_LINE_TAIL = "Never repeat the marker in your visible reply.',"
VERB_LINE = ("\n  'VERB PRECISION: never state a claim stronger than the source verbs. Launched never becomes "
             "funded; offered never becomes sent; asked never becomes confirmed; planning never becomes did. "
             "When the outcome is absent from the evidence, state only what is there (\"launched a Kickstarter "
             "- no funding outcome on record\").',")


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


KEY = env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-m", "60", "-X", method, f"{BASE}{path}",
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    bp = next(n for n in nodes if n["name"] == "Build Prompt")
    code = bp["parameters"]["jsCode"]

    if "[→ to NAME]" in code:
        print("already applied")
        return
    assert OLD_ATTR in code, "ATTRIBUTION anchor not found in Build Prompt"
    code = code.replace(OLD_ATTR, NEW_ATTR, 1)
    assert ATTR_LINE_TAIL in code, "post-replace tail anchor missing"
    code = code.replace(ATTR_LINE_TAIL, ATTR_LINE_TAIL + VERB_LINE, 1)
    bp["parameters"]["jsCode"] = code

    body = {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
            "settings": wf.get("settings", {})}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id") == STAGING_ID, f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r2 = api("POST", f"/workflows/{STAGING_ID}/activate")
    assert r2.get("active") is True, "reactivate failed"
    # read back
    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    bp2 = next(n for n in wf2["nodes"] if n["name"] == "Build Prompt")
    ok = "[→ to NAME]" in bp2["parameters"]["jsCode"] and "VERB PRECISION" in bp2["parameters"]["jsCode"]
    print("applied + verified:", ok)


if __name__ == "__main__":
    main()
