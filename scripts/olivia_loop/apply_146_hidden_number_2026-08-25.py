#!/usr/bin/env python3
"""#146 — a member who hides their WhatsApp number must still be answered.

MECHANISM, from prod executions 109524 and 109525 (2026-08-25, Danson Hui's two messages):
Meta delivered the inbound with NO `messages[0].from` — the sender arrived only as the opaque
`contacts[0].user_id` / `messages[0].from_user_id` = "CA.1068099432261958", because WhatsApp now lets a
member hide their number (Andy, as a group admin, sees his name but not his number).

  Log Inbound            → returned an item with `from` UNDEFINED (it reads msg.from and nothing else)
  Intro Tap Detected?    → routed it correctly to output 1
  Find Member            → body is `{{ JSON.stringify({ p_phone: $json.from }) }}`; with `from`
                           undefined that serialises to **{}**, so PostgREST answered
                           PGRST202 404 "function digest.olivia_front_door without parameters"
  execution              → ERROR after 435ms. No reply, no olivia_messages row, nothing in
                           olivia_webhook_events. Silence, twice.

The SQL half is already applied (migrations wa_user_id_second_identity_key and
olivia_front_door_v2_uid_fallback): digest.member_wa_ids (107 ids, 91 mapped),
digest.resolve_asker_by_uid(), digest.olivia_front_door_v2(p_phone, p_user_id) — phone first, the id
consulted only when the phone resolves to nobody, verified 1 row on each path and 0 rows on both-null.

THIS SCRIPT is the graph half, staging only:
  1. Log Inbound  — read the opaque id, and never emit an item without a usable sender. `from` carries
     the phone when there is one and the opaque id when there is not (Meta accepts that id as the
     recipient too, so replies still route), plus `wa_user_id` for the resolver and `from_is_uid` so
     downstream can tell the difference.
  2. Find Member  — calls olivia_front_door_v2 with BOTH parameters, always present, so the body can
     never serialise to {} again whatever arrives.
  3. Resolve Member — a sender we cannot pair gets reason 'unknown_uid' instead of a generic no_match.
  4. Build Generic — 'unknown_uid' gets the ask-once line rather than "I cannot match this number",
     which would be a lie: there is no number to match.

  python3 scripts/olivia_loop/apply_146_hidden_number_2026-08-25.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code)
        tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")


def sub(hay, old, new, label):
    assert hay.count(old) == 1, f"anchor drift: {label} ({hay.count(old)}x)"
    return hay.replace(old, new)


# ---- 1. Log Inbound ---------------------------------------------------------------------
LI_OLD = ("const quoted = (msg.context && msg.context.id) ? String(msg.context.id) : null;\n"
          "return { json: { event: 'inbound message', from: msg.from, name: name, type: msg.type, "
          "text: String(text).trim(), timestamp: msg.timestamp, wamid: msg.id, quoted_wamid: quoted } };")

LI_NEW = """const quoted = (msg.context && msg.context.id) ? String(msg.context.id) : null;
// #146 (2026-08-25): WhatsApp now lets a member HIDE their number. Meta then sends the inbound with no
// msg.from at all — the sender arrives only as an opaque country-prefixed id (msg.from_user_id /
// contacts[0].user_id, e.g. "CA.1068099432261958"). Reading msg.from alone left `from` undefined, and
// Find Member's body serialised to {} → PGRST202 404 → the execution errored and the member got
// SILENCE (Danson Hui, prod execs 109524/109525). Never emit a turn without a usable sender.
const _uid = msg.from_user_id || (contact && contact.user_id) || null;
const _rawFrom = msg.from || (contact && contact.wa_id) || null;
const _digits = String(_rawFrom || '').replace(/\\D/g, '');
const _isPhone = _digits.length >= 8 && _digits.length <= 15;
// `from` keeps carrying the phone when there is one. When there is not, it carries the opaque id —
// Meta accepts that id as a recipient, so the reply still routes, and olivia_front_door_v2 tries the
// phone first and only then the id, so a real number is never overridden.
const _from = _isPhone ? _digits : (_uid ? String(_uid) : null);
if (!_from) return null;   // nothing we could ever answer or reply to
return { json: { event: 'inbound message', from: _from, wa_user_id: _uid, from_is_uid: !_isPhone,
                 name: name, type: msg.type, text: String(text).trim(), timestamp: msg.timestamp,
                 wamid: msg.id, quoted_wamid: quoted } };"""

# ---- 3. Resolve Member ------------------------------------------------------------------
RM_OLD = ("if (rows.length !== 1) {\n"
          "  return [{ json: { matched: false, to: inbound.from, reason: rows.length === 0 ? 'no_match' "
          ": 'ambiguous', text: askText } }];\n}")

RM_NEW = """if (rows.length !== 1) {
  // #146: distinguish "we have never paired this hidden-number sender" from "this number is unknown".
  // Telling someone their NUMBER is not on file is a lie when WhatsApp never sent us a number.
  const _uidOnly = rows.length === 0 && inbound.from_is_uid === true;
  return [{ json: { matched: false, to: inbound.from, text: askText,
                    reason: _uidOnly ? 'unknown_uid' : (rows.length === 0 ? 'no_match' : 'ambiguous') } }];
}"""

# ---- 4. Build Generic -------------------------------------------------------------------
BG_OLD = """const reply = (m.reason === 'ambiguous')"""

BG_NEW = """const reply = (m.reason === 'unknown_uid')
  // #146: WhatsApp is hiding this member's number, so there is no number to match. Ask once, link them,
  // and they are known from then on. Never claim their number is not on file — we were never sent one.
  ? 'Hi! I am Millie, the MDS AI assistant. WhatsApp is not sharing your phone number with me, so I '
    + 'cannot tell which MDS member you are yet. Reply with the email on your MDS account and the team '
    + 'can link it — after that I will recognise you here every time.'
  : (m.reason === 'ambiguous')"""


def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    print(f"staging versionId {wf.get('versionId')} · {len(wf['nodes'])} nodes")
    nodes = {n["name"]: n for n in wf["nodes"]}

    li = nodes["Log Inbound"]
    c = sub(li["parameters"]["jsCode"], LI_OLD, LI_NEW, "Log Inbound sender")
    node_check(c, "Log Inbound")
    li["parameters"]["jsCode"] = c

    rm = nodes["Resolve Member"]
    c = sub(rm["parameters"]["jsCode"], RM_OLD, RM_NEW, "Resolve Member unknown_uid")
    node_check(c, "Resolve Member")
    rm["parameters"]["jsCode"] = c

    bg = nodes["Build Generic"]
    c = sub(bg["parameters"]["jsCode"], BG_OLD, BG_NEW, "Build Generic ask-once")
    node_check(c, "Build Generic")
    bg["parameters"]["jsCode"] = c

    fm = nodes["Find Member"]
    fm["parameters"]["url"] = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/olivia_front_door_v2"
    fm["parameters"]["jsonBody"] = ("={{ JSON.stringify({ p_phone: ($json.from_is_uid ? null : ($json.from || null)),"
                                    " p_user_id: ($json.wa_user_id || null) }) }}")
    print("  Find Member -> olivia_front_door_v2, body always carries both parameters")

    if dry:
        print("DRY RUN — nothing written")
        return 0

    payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
               "settings": wf.get("settings") or {}}
    out = api("PUT", f"/workflows/{STAGING}", payload)
    print("applied · new versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
