#!/usr/bin/env python3
"""#11 round 2 — the ride-along payment reminder (STAGING).

Andy 2026-08-01: a past_due/unpaid member gets a payment reminder appended to ANY answer,
max once per 24h. The once-per-day logic is deterministic in digest.billing_nudge(p_phone)
(stamp table); this script wires the delivery: both reply producers (Format Reply = model
answers, Build Verbatim Digest = canned routes) flow through Billing Nudge -> Apply Nudge
before Eval (silent)?. For the ~99% of members not past-due the RPC is a single indexed
lookup returning no rows. The nudge is appended to the SENT text only — the saved
conversation keeps the clean answer (same precedent as holding texts).

Idempotent: exits 0 if already wired.
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
if "Billing Nudge" in names:
    print("already wired")
    sys.exit(0)

SUPA_CRED = {"httpHeaderAuth": {"id": "QHLDE4VHvm8jrVds", "name": "Supabase secret (digest mirror)"}}

wf["nodes"].append({
    "id": "billing_nudge", "name": "Billing Nudge", "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2, "position": [2580, 560],
    "onError": "continueRegularOutput", "alwaysOutputData": True,
    "credentials": SUPA_CRED,
    "parameters": {
        "method": "POST",
        "url": "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/billing_nudge",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Content-Profile", "value": "digest"},
            {"name": "Content-Type", "value": "application/json"}]},
        "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ p_phone: $json.to }) }}",
        "options": {"timeout": 8000}},
})
wf["nodes"].append({
    "id": "apply_nudge", "name": "Apply Nudge", "type": "n8n-nodes-base.code", "typeVersion": 2,
    "position": [2580, 660],
    "parameters": {"jsCode": (
        "// #11: append the once-per-24h payment reminder when billing_nudge returned one.\n"
        "// The nudge rides the SENT text only; Save Conversation keeps the clean answer.\n"
        "const base = $('Format Reply').isExecuted ? $('Format Reply').first().json\n"
        "           : $('Build Verbatim Digest').first().json;\n"
        "let nud = '';\n"
        "try {\n"
        "  const r = $input.first().json;\n"
        "  nud = (r && (r.nudge || (Array.isArray(r) && r[0] && r[0].nudge))) || '';\n"
        "} catch (e) {}\n"
        "const out = Object.assign({}, base);\n"
        "if (nud && out.reply) {\n"
        "  const joined = out.reply + String.fromCharCode(10) + String.fromCharCode(10) + nud;\n"
        "  if (joined.length <= 3800) { out.reply = joined; }  // never truncate an answer for a nudge\n"
        "}\n"
        "return [{ json: out }];\n")},
})

conns = wf["connections"]

fr = conns["Format Reply"]["main"][0]
assert any(c["node"] == "Eval (silent)?" for c in fr), "Format Reply no longer feeds Eval?"
conns["Format Reply"]["main"][0] = [
    ({"node": "Billing Nudge", "type": "main", "index": 0} if c["node"] == "Eval (silent)?" else c)
    for c in fr]

bv = conns["Build Verbatim Digest"]["main"][0]
assert any(c["node"] == "Eval (silent)?" for c in bv), "Build Verbatim no longer feeds Eval?"
conns["Build Verbatim Digest"]["main"][0] = [
    ({"node": "Billing Nudge", "type": "main", "index": 0} if c["node"] == "Eval (silent)?" else c)
    for c in bv]

conns["Billing Nudge"] = {"main": [[{"node": "Apply Nudge", "type": "main", "index": 0}]]}
conns["Apply Nudge"] = {"main": [[{"node": "Eval (silent)?", "type": "main", "index": 0}]]}

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
c2 = wf2["connections"]
ok = ("Billing Nudge" in {n["name"] for n in wf2["nodes"]}
      and c2["Apply Nudge"]["main"][0][0]["node"] == "Eval (silent)?"
      and any(x["node"] == "Billing Nudge" for x in c2["Format Reply"]["main"][0])
      and any(x["node"] == "Billing Nudge" for x in c2["Build Verbatim Digest"]["main"][0]))
print(f"VERIFY wired:{ok} active:{wf2.get('active')} nodes:{len(wf2['nodes'])}")
assert ok
