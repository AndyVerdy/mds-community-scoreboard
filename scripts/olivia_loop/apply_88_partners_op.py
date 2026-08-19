#!/usr/bin/env python3
"""#88 — declare the schedule lane's `partners` op in the Answer Seed.

Three exact-string edits, Answer Seed only (the endpoint half shipped in
mds-digest-web d1924be):
  1. the op enum gains `partners`
  2. the event_schedule description gains the partners clause (before `remind (`)
  3. one routing rule: event-scoped partner asks go op=partners; partner_lookup
     stays the year-round directory

Apostrophe-free additions; node --check before the PUT; one bounce.
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


EDITS = [
    ("op: str('agenda | next | day | where | speaker | speakers | recommend | people | remind | reminders | unremind')",
     "op: str('agenda | next | day | where | speaker | speakers | recommend | people | partners | remind | reminders | unremind')"),
    ("remind (SET a reminder - q is the activity or session",
     "partners (THE EVENT PARTNERS — who they are and what they offer AT THIS EVENT: empty q lists every partner with a teaser; q with a company or person name returns the full profile — the event offer, the standing MDS offer, how to redeem, contact, and the people they brought), "
     "remind (SET a reminder - q is the activity or session"),
    ("q: str('activity name for where, person name for speaker')",
     "q: str('activity name for where, person name for speaker, company or person name for partners')"),
    ("  '- REMINDERS ARE REAL NOW.",
     "  '- PARTNERS AT THE EVENT (#88): who are the partners / what does <company> offer here / which partner is <person> with, asked about the Summit, is event_schedule op=partners — q names one company or person for the full profile, empty q lists them. Lead with the offer and how to redeem it. partner_lookup stays the year-round directory for deals by need; the event ask is answered from the event roster.',\n"
     "  '- REMINDERS ARE REAL NOW."),
]


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    code = nodes["Answer Seed"]["parameters"]["jsCode"]

    if "op=partners" in code:
        print("already applied")
        return
    for old, new in EDITS:
        got = code.count(old)
        assert got == 1, f"anchor found {got}x, expected 1:\n  {old[:100]}"
        code = code.replace(old, new)

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
    print("node --check: OK")
    nodes["Answer Seed"]["parameters"]["jsCode"] = code

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")
    print("PUT + one bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    c2 = {n["name"]: n for n in wf2["nodes"]}["Answer Seed"]["parameters"]["jsCode"]
    for marker in ("| partners |", "THE EVENT PARTNERS", "PARTNERS AT THE EVENT (#88)"):
        assert marker in c2, f"marker {marker!r} missing after PUT"
        print(f"  verified: {marker!r}")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
