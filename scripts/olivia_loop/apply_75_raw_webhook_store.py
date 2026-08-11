#!/usr/bin/env python3
"""#75 — persist every inbound Meta MESSAGE event before any parse touches it.

digest.olivia_feedback held 10 reactions all-time and then went silent for 7 days; nothing
could say whether reactions stopped arriving or stopped being parsed, because a dropped
reaction left no trace anywhere (the same silent failure mode as the heartbeat that never
stamped). A synthetic reaction canary (2026-08-11) proved the prod parse path ALIVE, and
daily delivery statuses prove the Meta subscription alive — but only a raw store makes that
distinction observable at any later date.

The fix: two nodes on the webhook fan-out, wired as the FIRST branch (n8n v1 runs fan-out
branches depth-first in order — raw persistence must complete before any parse can throw):

  Extract Raw Event  (code)  — passes any payload carrying value.messages (text, interactive,
                               reaction, media...); statuses return null (they are already
                               persisted in digest.olivia_sends, and the 5-min health ping is
                               statuses-only, so the store stays free of ping noise).
  Store Raw Event (Supabase) — POST to digest.olivia_webhook_events, onError=continue so a
                               Supabase outage can never block answering.
"""
import json, os, subprocess, sys, tempfile

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


EXTRACT_JS = """// #75: persist the raw event BEFORE any parse. Statuses (incl. the 5-min health
// ping) return null - they are already persisted in digest.olivia_sends.
const j = $input.item.json;
const b = (j && j.body) ? j.body : j;
const val = b && b.entry && b.entry[0] && b.entry[0].changes && b.entry[0].changes[0] && b.entry[0].changes[0].value;
const msg = val && val.messages && val.messages[0];
if (!msg) return null;
return { json: {
  msg_type: String(msg.type || 'unknown'),
  from_phone: msg.from || null,
  wamid: msg.id || null,
  payload: b
} };"""

EXTRACT_NODE = {
    "id": "extract_raw_event",
    "name": "Extract Raw Event",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [240, 820],
    "parameters": {"mode": "runOnceForEachItem", "jsCode": EXTRACT_JS},
}

STORE_NODE = {
    "id": "store_raw_event",
    "name": "Store Raw Event (Supabase)",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [480, 820],
    "parameters": {
        "method": "POST",
        "url": "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/olivia_webhook_events",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Content-Type", "value": "application/json"},
            {"name": "Content-Profile", "value": "digest"},
            {"name": "Prefer", "value": "return=minimal"},
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": ("={{ JSON.stringify({ msg_type: $json.msg_type, from_phone: $json.from_phone, "
                     "wamid: $json.wamid, payload: $json.payload }) }}"),
        "options": {},
    },
    "credentials": {"httpHeaderAuth": {"id": "QHLDE4VHvm8jrVds",
                                       "name": "Supabase secret (digest mirror)"}},
    "onError": "continueRegularOutput",
    "retryOnFail": True,
    "maxTries": 2,
    "waitBetweenTries": 2000,
}


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    names = [n["name"] for n in wf["nodes"]]

    if "Extract Raw Event" in names:
        print("already applied — Extract Raw Event exists")
    else:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(EXTRACT_JS)
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
        print("node --check: OK")

        wf["nodes"].append(EXTRACT_NODE)
        wf["nodes"].append(STORE_NODE)

        fan = wf["connections"]["WA Inbound (POST)"]["main"][0]
        got = [c["node"] for c in fan]
        assert got == ["Log Inbound", "Parse Delivery Status", "Parse Reaction"], \
            f"unexpected fan-out {got} — aborting"
        # raw store runs FIRST (v1 depth-first branch order): the payload is on disk
        # before any parse gets the chance to throw it away.
        fan.insert(0, {"node": "Extract Raw Event", "type": "main", "index": 0})
        wf["connections"]["Extract Raw Event"] = {
            "main": [[{"node": "Store Raw Event (Supabase)", "type": "main", "index": 0}]]}

        body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
                "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                             if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                      "saveDataErrorExecution", "saveDataSuccessExecution",
                                      "saveExecutionProgress", "saveManualExecutions", "timezone")}}
        r = api("PUT", f"/workflows/{STAGING_ID}", body)
        assert r.get("id"), f"PUT failed: {str(r)[:300]}"
        api("POST", f"/workflows/{STAGING_ID}/deactivate")
        api("POST", f"/workflows/{STAGING_ID}/activate")
        print("PUT + bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = [n["name"] for n in wf2["nodes"]]
    fan2 = [c["node"] for c in wf2["connections"]["WA Inbound (POST)"]["main"][0]]
    assert "Extract Raw Event" in n2 and "Store Raw Event (Supabase)" in n2, "nodes missing after PUT"
    assert fan2[0] == "Extract Raw Event", f"raw branch is not first: {fan2}"
    print(f"verified: {len(wf2['nodes'])} nodes · fan-out order {fan2}")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
