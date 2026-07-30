#!/usr/bin/env python3
"""#24 First contact answers the question — apply to STAGING (bqHstPDi84uOhTCJ).

The welcome gate fired on "first-time user" before anything read the message, so a first
contact that IS a question got the intro menu and no answer (9 of 22 organic users opened
with a question; all swallowed since Jul 23). This makes the gate content-aware:

- Plan Request: only a TRUE greeting takes the welcome on first contact; any other first
  message keeps its real route, with `first_contact` threaded through both return sites.
- Format Reply: when `first_contact`, the answer goes out first and a one-line beta intro
  rides along after it; `mark_welcome_phone` is emitted so the member is marked welcomed.
- Format Reply -> Mark Welcomed connection added (the PATCH no-ops when the field is '').

Idempotent: safe to re-run; asserts before every replace and aborts without writing.
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

# ---- Plan Request ----
pr = nodes["Plan Request"]["parameters"]["jsCode"]
GATE_OLD = "if (!mem.welcomed_at) { intent = 'greeting'; chat = null; period = null; }"
GATE_NEW = """// #24 (2026-07-30): content is read BEFORE the first-contact gate. 9 of 22 organic users
// opened with a real question and every one since Jul 23 got the welcome menu instead of an
// answer. Only a true greeting takes the welcome; a first-contact QUESTION keeps its real
// route and the intro rides along in the reply (first_contact -> Format Reply).
if (!mem.welcomed_at && realGreeting) { intent = 'greeting'; chat = null; period = null; }
const first_contact = !mem.welcomed_at && !realGreeting;"""
if GATE_OLD in pr:
    pr = pr.replace(GATE_OLD, GATE_NEW)
    OLD637 = "} else if (intent === 'greeting' && (realGreeting || !mem.welcomed_at)) {"
    assert OLD637 in pr, "greeting-route condition not found"
    pr = pr.replace(OLD637, "} else if (intent === 'greeting' && realGreeting) {")
    assert pr.count("return [{ json: { ticket_ask: ticketAsk,") == 2, "expected exactly 2 return sites"
    pr = pr.replace("return [{ json: { ticket_ask: ticketAsk,",
                    "return [{ json: { first_contact: first_contact, ticket_ask: ticketAsk,")
    nodes["Plan Request"]["parameters"]["jsCode"] = pr
    print("Plan Request patched")
else:
    assert "first_contact" in pr, "gate line missing AND flag missing — unexpected state, aborting"
    print("Plan Request already patched")

# ---- Format Reply ----
fr = nodes["Format Reply"]["parameters"]["jsCode"]
RET_OLD = "return [{ json: { to: to, reply: text, image_post_id: imagePostId, send_file_key: sendFileKey } }];"
RET_NEW = """// #24: a first-contact QUESTION was answered above — the beta intro rides along after the
// answer instead of replacing it, and this turn marks the member welcomed.
let markPhone = '';
try {
  const pl = $('Plan Request').first().json;
  if (pl && pl.first_contact) {
    markPhone = to;
    const intro = String.fromCharCode(10) + String.fromCharCode(10) +
      '_PS: I am Olivia, the MDS assistant (beta). Ask me about the chats, the Facebook group, members, events, partner deals or the video library - anytime._';
    if (text.length + intro.length <= 3800) { text = text + intro; }
  }
} catch (e) {}
return [{ json: { to: to, reply: text, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone } }];"""
if RET_OLD in fr:
    nodes["Format Reply"]["parameters"]["jsCode"] = fr.replace(RET_OLD, RET_NEW)
    print("Format Reply patched")
else:
    assert "mark_welcome_phone" in fr, "Format Reply return not found — unexpected state, aborting"
    print("Format Reply already patched")

# ---- connection ----
conns = wf["connections"]
fr_out = conns.setdefault("Format Reply", {"main": [[]]})["main"][0]
if not any(x["node"] == "Mark Welcomed" for x in fr_out):
    fr_out.append({"node": "Mark Welcomed", "type": "main", "index": 0})
    print("Format Reply -> Mark Welcomed wired")

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
pr2 = next(n for n in wf2["nodes"] if n["name"] == "Plan Request")["parameters"]["jsCode"]
fr2 = next(n for n in wf2["nodes"] if n["name"] == "Format Reply")["parameters"]["jsCode"]
ok_conn = any(x["node"] == "Mark Welcomed" for x in wf2["connections"]["Format Reply"]["main"][0])
print(f"VERIFY gate:{('!mem.welcomed_at && realGreeting' in pr2)} "
      f"flag_x2:{pr2.count('first_contact: first_contact') == 2} "
      f"intro:{'PS: I am Olivia' in fr2} wired:{ok_conn}")
