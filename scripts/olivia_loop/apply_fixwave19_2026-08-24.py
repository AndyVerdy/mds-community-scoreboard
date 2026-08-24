#!/usr/bin/env python3
"""Fixwave 19 — an internal record id never appears in an answer.

Found while grading: one answer told a member "the messages authored by 'Andy Verdy' were tied to a
different member record than yours (recJnrYFuWhzom63H), not the Andy Verdy tied to this chat
(recCUUw8iiUnJjac1)". Airtable record ids are internal plumbing; a member has no use for them and
they expose the shape of the warehouse.

Scope, measured before building rather than after: 31 answers ever contained the string, but 30 of
those are legitimate registration links (events-details?recordId=...), which members need and which
must keep working. Exactly ONE is a bare id in prose, and it went to the probe number, not a member.
So this is a guard against recurrence, not an incident — and the guard has to be URL-aware or it
breaks every event link Millie sends.

  G8 · Gate Verdict: strip URLs, then any remaining record id regenerates the answer. Audited over
       all 602 bank C answers: 7 contain a record id, ALL 7 inside an events-details URL, so the
       URL-aware pattern fires on ZERO of them.
  F3 · Format Reply backstop: if one somehow survives the gate, redact it rather than ship it. The
       gate can be exhausted by the attempts cap; this cannot.

  python3 scripts/olivia_loop/apply_fixwave19_2026-08-24.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="): return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)

BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")

def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None: cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code); tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")

def sub(hay, old, new, label):
    assert hay.count(old) == 1, f"anchor drift: {label} ({hay.count(old)}x)"
    return hay.replace(old, new)

def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    gv = nodes["Gate Verdict"]; cg = gv["parameters"]["jsCode"]
    a_g = "if (!claims.length) {"
    g8 = """// fixwave 19 (G8) — an Airtable record id in the PROSE of an answer is internal plumbing leaking
// to a member. URLs are stripped first because events-details?recordId=... is a real registration
// link members need: of the 7 bank C answers containing a record id, all 7 are that link, and this
// pattern fires on none of them.
try {
  const _noUrls = String(answerText || '').replace(/https?:\\/\\/\\S+/g, ' ');
  if (/\\brec[A-Za-z0-9]{14,17}\\b/.test(_noUrls)) {
    claims.push('INTERNAL ID LEAK: the draft prints an Airtable record id to the member. Those are '
      + 'internal plumbing — never show one. Say who the person is by NAME, or say plainly that two '
      + 'records share a name, without exposing any id.');
  }
} catch (e) {}

"""
    cg = sub(cg, a_g, g8 + a_g, "G8 record id gate")
    node_check(cg, "Gate Verdict"); gv["parameters"]["jsCode"] = cg

    fr = nodes["Format Reply"]; cf = fr["parameters"]["jsCode"]
    a_f = """text = text.replace(/^\\s{0,3}#{1,6}\\s+(.+?)\\s*$/gm, '*$1*');"""
    f3 = a_f + """
// fixwave 19 (F3): last-ditch backstop for the same thing. The gate regenerates, but its attempts
// cap can be exhausted and the clamp path ships whatever it has — this cannot be exhausted. URLs
// are protected first so real events-details?recordId=... links survive untouched.
try {
  const _urls = [];
  let _t = text.replace(/https?:\\/\\/\\S+/g, function (u) { _urls.push(u); return '\\u0000' + (_urls.length - 1) + '\\u0000'; });
  _t = _t.replace(/\\brec[A-Za-z0-9]{14,17}\\b/g, '[internal id removed]');
  text = _t.replace(/\\u0000(\\d+)\\u0000/g, function (_m, i) { return _urls[Number(i)]; });
} catch (e) {}"""
    cf = sub(cf, a_f, f3, "F3 record id backstop")
    node_check(cf, "Format Reply"); fr["parameters"]["jsCode"] = cf

    if dry:
        print("DRY RUN — anchors hit, node --check clean on 2 nodes.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    n2 = {n["name"]: n for n in after["nodes"]}
    assert "fixwave 19 (G8)" in n2["Gate Verdict"]["parameters"]["jsCode"]
    assert "fixwave 19 (F3)" in n2["Format Reply"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
