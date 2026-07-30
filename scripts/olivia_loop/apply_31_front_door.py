#!/usr/bin/env python3
"""#31 front door — membership status gates the WhatsApp door (staging AND prod).

The SQL layer already refuses non-active members all data (migration
membership_status_gates_every_door); this patch makes the front door say so honestly:
Resolve Member routes any non-active status to the non-member path with reason='inactive',
and Build Generic gains the matching message. Identity is never entitlement.

  python3 apply_31_front_door.py staging
  python3 apply_31_front_door.py prod     # take the wf lock first (olivia_wf.py lock)

Idempotent: asserts anchors, aborts without writing.
"""
import json, subprocess, sys

IDS = {"staging": "bqHstPDi84uOhTCJ", "prod": "12wj6h1TWqb0d4Dq"}
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


target = sys.argv[1] if len(sys.argv) > 1 else ""
if target not in IDS:
    sys.exit("usage: apply_31_front_door.py staging|prod")
WF = IDS[target]

wf = api("GET", f"/workflows/{WF}")
nodes = {n["name"]: n for n in wf["nodes"]}

rm = nodes["Resolve Member"]["parameters"]["jsCode"]
RM_ANCHOR = "const m = rows[0];"
RM_GUARD = """const m = rows[0];
// #31 (2026-07-30): identity is never entitlement. Only an ACTIVE membership status passes -
// canceled/removed/applicant/unknown all take the non-member path (the SQL layer refuses them
// data regardless; this door gives the honest message instead of a hollow member experience).
const ACTIVE = ['Current Member', 'New Member', 'Current Member- Not Renewing', 'Staff'];
if (!ACTIVE.includes(m.membership_status)) {
  return [{ json: { matched: false, to: inbound.from, reason: 'inactive', text: inbound.text } }];
}"""
if "reason: 'inactive'" in rm:
    print(f"{target}: Resolve Member already patched")
else:
    assert rm.count(RM_ANCHOR) == 1, "Resolve Member anchor not found exactly once — aborting"
    nodes["Resolve Member"]["parameters"]["jsCode"] = rm.replace(RM_ANCHOR, RM_GUARD)
    print(f"{target}: Resolve Member patched")

bg = nodes["Build Generic"]["parameters"]["jsCode"]
BG_ANCHOR = "  : 'Hi! I am the MDS AI Assistant, here to help MDS members. I cannot match this number"
BG_NEW = """  : (m.reason === 'inactive')
  ? 'Hi! I am the MDS AI Assistant, here to help active MDS members. This number is linked to an MDS membership that is not currently active, so I cannot help here. If that seems wrong, the MDS team can sort it out.'
  : 'Hi! I am the MDS AI Assistant, here to help MDS members. I cannot match this number"""
if "reason === 'inactive'" in bg:
    print(f"{target}: Build Generic already patched")
else:
    assert bg.count(BG_ANCHOR) == 1, "Build Generic anchor not found exactly once — aborting"
    nodes["Build Generic"]["parameters"]["jsCode"] = bg.replace(BG_ANCHOR, BG_NEW)
    print(f"{target}: Build Generic patched")

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                     if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                               "saveDataErrorExecution", "saveDataSuccessExecution",
                               "saveExecutionProgress", "saveManualExecutions", "timezone")}}
r = api("PUT", f"/workflows/{WF}", body)
assert r.get("id"), f"PUT failed: {str(r)[:300]}"
api("POST", f"/workflows/{WF}/deactivate")
api("POST", f"/workflows/{WF}/activate")

wf2 = api("GET", f"/workflows/{WF}")
rm2 = next(n for n in wf2["nodes"] if n["name"] == "Resolve Member")["parameters"]["jsCode"]
bg2 = next(n for n in wf2["nodes"] if n["name"] == "Build Generic")["parameters"]["jsCode"]
print(f"VERIFY {target}: resolve_guard:{('inactive' in rm2)} generic_msg:{('not currently active' in bg2)} active:{wf2.get('active')}")
