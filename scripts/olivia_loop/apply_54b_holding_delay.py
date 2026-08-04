#!/usr/bin/env python3
"""#54b Holding rung-1 delay 18s -> 30s (PROD side workflow X1vzrW9Avqff3qRa — ANDY RUNS).

Ian, 2026-08-04: "Why is the ai respond always the same — On it — checking a few sources
for you". Measured on the last 202 real prod answers: median 15s, and 31% cross the 18s
rung — a third of all questions open with the identical holding line. At 30s it fires on
~2% (genuinely slow answers only). The 42s gap to rung 2 is unchanged (delay notice now
at ~72s; p100 observed was <60s, so rung 2 stays rare).

One field: the "Wait 18s" node amount 18 -> 30 (node NAME kept — connections bind by name);
workflow display name updated to match. Idempotent.

Run:  python3 scripts/olivia_loop/apply_54b_holding_delay.py
"""
import json, subprocess, sys

WF_ID = "X1vzrW9Avqff3qRa"
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


wf = api("GET", f"/workflows/{WF_ID}")
n = next(x for x in wf["nodes"] if x["name"] == "Wait 18s")
if n["parameters"].get("amount") == 30:
    print("already 30s — nothing to do")
    sys.exit(0)
assert n["parameters"].get("amount") == 18, f"unexpected amount: {n['parameters']}"
n["parameters"]["amount"] = 30

body = {"name": wf["name"].replace("18s holding", "30s holding"),
        "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                     if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                              "saveDataErrorExecution", "saveDataSuccessExecution",
                              "saveExecutionProgress", "saveManualExecutions", "timezone")}}
r = api("PUT", f"/workflows/{WF_ID}", body)
assert r.get("id"), f"PUT failed: {str(r)[:300]}"
api("POST", f"/workflows/{WF_ID}/deactivate")
api("POST", f"/workflows/{WF_ID}/activate")

wf2 = api("GET", f"/workflows/{WF_ID}")
n2 = next(x for x in wf2["nodes"] if x["name"] == "Wait 18s")
print(f"VERIFY amount: {n2['parameters']['amount']} | name: {wf2['name']} | active: {wf2.get('active')}")
