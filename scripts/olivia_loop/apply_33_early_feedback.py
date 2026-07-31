#!/usr/bin/env python3
"""#33 — read tick, typing and the holding ladder must fire BEFORE the answer, not after it.

THE DEFECT (prod, found from Andy's 2:40PM stall, exec 57816 + ladder 57817): Prep Context
fans out to [Route Request, Mark Read + Typing]. n8n executionOrder v1 runs branches
depth-first in order, so the ENTIRE answer path (router -> retrieval -> loop -> gate ->
send, 70s on that exec) completed before Mark Read + Typing and Fire Holding Timer ever
ran — the ladder exec started the same second the main exec stopped, four independent
pairs verified (57816/57817 · 57824/57825 · 57780/57781 · 57831/57833). Result: no read
tick, no typing, no holding message during the whole wait; the #23 ladder is a silent
no-op on every prod turn (it fires after the answer, the answered-check sees the answer,
it exits).

THE FIX: make the feedback branch run FIRST. Two levers, both applied (whichever rule
n8n v1 uses for branch order, the probe decides):
  1. connection order — Mark Read + Typing before Route Request in Prep Context's output
  2. canvas position — the feedback chain lifted ABOVE Route Request (v1 orders branches
     top-to-bottom by node position)
Cost: Mark Read (~0.3s) + Holding Trigger? (0ms) + Fire Holding Timer (~0.2s, webhook
responds onReceived; 4s timeout, onError continue) before routing starts. ~0.5s added
to every matched turn, buying feedback within ~2s of the inbound.

STAGING ONLY. Idempotent: asserts before writing, exits 0 if already applied.
"""
import json, subprocess, sys

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

NEW_POS = {
    "Mark Read + Typing": [1120, 230],
    "Holding Trigger?": [1240, 230],
    "Fire Holding Timer": [1360, 230],
}


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
assert wf.get("id") == STAGING_ID, str(wf)[:300]

pc = wf["connections"].get("Prep Context", {}).get("main", [[]])[0]
targets = [c["node"] for c in pc]
assert sorted(targets) == ["Mark Read + Typing", "Route Request"], f"unexpected Prep Context fan-out: {targets}"

route_pos = next(n["position"] for n in wf["nodes"] if n["name"] == "Route Request")
already = targets[0] == "Mark Read + Typing" and all(
    next(n["position"] for n in wf["nodes"] if n["name"] == k) == v for k, v in NEW_POS.items())
if already:
    print("already applied")
    sys.exit(0)

# lever 1: connection order — feedback branch first
wf["connections"]["Prep Context"]["main"][0] = sorted(
    pc, key=lambda c: 0 if c["node"] == "Mark Read + Typing" else 1)

# lever 2: canvas position — feedback chain above Route Request (y 230 < 368)
for n in wf["nodes"]:
    if n["name"] in NEW_POS:
        n["position"] = NEW_POS[n["name"]]
assert all(NEW_POS[k][1] < route_pos[1] for k in NEW_POS)

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
pc2 = [c["node"] for c in wf2["connections"]["Prep Context"]["main"][0]]
pos2 = {n["name"]: n["position"] for n in wf2["nodes"] if n["name"] in NEW_POS}
print(f"VERIFY order:{pc2} positions:{pos2} active:{wf2.get('active')}")
assert pc2[0] == "Mark Read + Typing" and pos2 == NEW_POS
