#!/usr/bin/env python3
"""#26 — Fetch Summaries passes the query embedding to partner_lookup / event_lookup
(STAGING bqHstPDi84uOhTCJ).

The cascade already embeds every question once (Embed Query) and injects p_embedding for
video_search only. partner_lookup and event_lookup now accept p_embedding too (migrations
partner_lookup_semantic_rrf / event_lookup_semantic_rrf) — add them to the inject list.
The raw path never calls these two ops, so Fetch Raw Matches is untouched; the loop's
Attach Embedding list is handled by build_loop.py.

Idempotent: asserts before replacing, aborts without writing. Whole-graph PUT — never
patchNodeField on a $-dense expression (the $n-expansion trap).
"""
import json, subprocess, sys

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}",
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json",
           "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


wf = api("GET", f"/workflows/{STAGING_ID}")
nodes = {n["name"]: n for n in wf["nodes"]}
fs = nodes["Fetch Summaries"]["parameters"]["jsonBody"]

OLD = "if (pl.op === 'video_search' && eq && eq.data && eq.data[0] && eq.data[0].embedding)"
NEW = "if (['video_search','partner_lookup','event_lookup'].includes(pl.op) && eq && eq.data && eq.data[0] && eq.data[0].embedding)"

if NEW in fs:
    print("Fetch Summaries already patched")
else:
    assert fs.count(OLD) == 1, "video_search inject anchor not found exactly once — aborting"
    nodes["Fetch Summaries"]["parameters"]["jsonBody"] = fs.replace(OLD, NEW)
    print("Fetch Summaries patched")

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                     if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                               "saveDataErrorExecution", "saveDataSuccessExecution",
                               "saveExecutionProgress", "saveManualExecutions", "timezone")}}
r = api("PUT", f"/workflows/{STAGING_ID}", body)
assert r.get("id"), f"PUT failed: {str(r)[:300]}"
api("POST", f"/workflows/{STAGING_ID}/deactivate")
api("POST", f"/workflows/{STAGING_ID}/activate")

wf2 = api("GET", f"/workflows/{STAGING_ID}")
fs2 = next(n for n in wf2["nodes"] if n["name"] == "Fetch Summaries")["parameters"]["jsonBody"]
print(f"VERIFY inject:{(NEW in fs2)} active:{wf2.get('active')}")
