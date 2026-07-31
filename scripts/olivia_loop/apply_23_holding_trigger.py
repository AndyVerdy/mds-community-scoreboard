#!/usr/bin/env python3
"""#23 — wire the holding timer into the answering path (STAGING bqHstPDi84uOhTCJ).

Mark Read + Typing already fires read + typing within ~2s (Meta expires typing at ~25s —
exactly why 24s answers read as dead). This adds a leaf branch after it: a tiny Code node
drops SELFTEST traffic (evals never get holding texts), then a fire-and-forget HTTP POST to
the standalone "Olivia Holding Timer" workflow (X1vzrW9Avqff3qRa: 18s holding message, 60s
delay notice, each skipped if the answer already landed in olivia_messages). The webhook
responds onReceived (~200ms) so the leaf never delays routing.

Idempotent: asserts before writing.
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
names = {n["name"] for n in wf["nodes"]}

if "Holding Trigger?" in names:
    print("already wired")
    sys.exit(0)

wf["nodes"].append({
    "id": "hold_gate", "name": "Holding Trigger?", "type": "n8n-nodes-base.code", "typeVersion": 2,
    "position": [1240, 640],
    "parameters": {"jsCode": (
        "// #23: only REAL member turns get a holding timer - eval/selftest traffic never does.\n"
        "const inbound = $('Log Inbound').first().json;\n"
        "if (String(inbound.wamid || '').includes('SELFTEST')) { return []; }\n"
        "// arrival = the MESSAGE's own timestamp, never now: Meta redelivers messages, and a\n"
        "// replay stamped with now opened a fresh holding window AFTER the answer had landed\n"
        "// (ghost On-it/Still-working texts, 2026-07-31). Anchored on the message time, the\n"
        "// answered-check sees the original answer and the replay ladder stays silent.\n"
        "const ts = Number(inbound.timestamp);\n"
        "const arrival = ts > 0 ? new Date(ts * 1000).toISOString() : new Date().toISOString();\n"
        "return [{ json: { to: inbound.from, arrival: arrival } }];\n")},
})
wf["nodes"].append({
    "id": "hold_fire", "name": "Fire Holding Timer", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
    "position": [1360, 640],
    "onError": "continueRegularOutput", "alwaysOutputData": True,
    "parameters": {"method": "POST",
                    "url": "https://mdsco.app.n8n.cloud/webhook/olivia-holding-timer",
                    "sendBody": True, "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify({ to: $json.to, arrival: $json.arrival }) }}",
                    "options": {"timeout": 4000}},
})
conns = wf["connections"]
mrt = conns.setdefault("Mark Read + Typing", {"main": [[]]})
if not mrt["main"] or mrt["main"][0] is None:
    mrt["main"] = [[]]
mrt["main"][0].append({"node": "Holding Trigger?", "type": "main", "index": 0})
conns["Holding Trigger?"] = {"main": [[{"node": "Fire Holding Timer", "type": "main", "index": 0}]]}

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": conns,
        "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                     if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                               "saveDataErrorExecution", "saveDataSuccessExecution",
                               "saveExecutionProgress", "saveManualExecutions", "timezone")}}
r = api("PUT", f"/workflows/{STAGING_ID}", body)
assert r.get("id"), f"PUT failed: {str(r)[:300]}"
api("POST", f"/workflows/{STAGING_ID}/deactivate")
api("POST", f"/workflows/{STAGING_ID}/activate")

wf2 = api("GET", f"/workflows/{STAGING_ID}")
n2 = {n["name"] for n in wf2["nodes"]}
print(f"VERIFY wired:{('Holding Trigger?' in n2 and 'Fire Holding Timer' in n2)} active:{wf2.get('active')} nodes:{len(n2)}")
