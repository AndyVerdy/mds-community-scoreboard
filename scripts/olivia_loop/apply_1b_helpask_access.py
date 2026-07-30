#!/usr/bin/env python3
"""#1 — data-ACCESS phrasings become deterministic helpAsk (STAGING bqHstPDi84uOhTCJ).

"What data do you have access to?" is a capability question: the canned help list IS the
answer, and the standing rule keeps that list current. Routed to the loop instead, the
answer is pure self-description, which the fact-gate then blocked on thin evidence
(exec 56121 — the Q3009 over-refusal class). Same shape as every #1 fix: serve the canned
lane exactly what it can serve, deterministically. me/my/our excluded so "what data do you
have on me" stays a profile ask.

Idempotent: asserts before replacing, aborts without writing.
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
pr = nodes["Plan Request"]["parameters"]["jsCode"]

OLD = "  || /\\bwhat (data( points?)?|info(rmation)?) do you (have|hold|track|keep)[?!.\\s]*$/i.test(rawText);"
NEW = """  || /\\bwhat (data( points?)?|info(rmation)?) do you (have|hold|track|keep)[?!.\\s]*$/i.test(rawText)
  // #1 (2026-07-30): data-ACCESS phrasings are capability questions - the canned help list IS
  // the answer (and the standing rule keeps it current). "What data do you have access to?"
  // reached the loop, whose self-describing answer the fact-gate then blocked (exec 56121).
  // me/my/our excluded so "what data do you have on me" stays a profile ask.
  || (/\\bwhat\\b[\\s\\S]{0,30}\\b(data|info(rmation)?|sources?)\\b[\\s\\S]{0,30}\\baccess\\b/i.test(rawText) && !/\\b(me|my|our)\\b/i.test(rawText))
  || (/\\bwhat (do|can) you (have )?access( to)?\\b/i.test(rawText) && !/\\b(me|my|our)\\b/i.test(rawText));"""

if "data-ACCESS phrasings are capability questions" in pr:
    print("Plan Request already patched")
else:
    assert pr.count(OLD) == 1, "helpAsk tail anchor not found exactly once — aborting"
    nodes["Plan Request"]["parameters"]["jsCode"] = pr.replace(OLD, NEW)
    print("Plan Request patched")

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
pr2 = next(n for n in wf2["nodes"] if n["name"] == "Plan Request")["parameters"]["jsCode"]
print(f"VERIFY access_helpask:{('data-ACCESS phrasings are capability questions' in pr2)} "
      f"boundary_kept:{('const trueAction =' in pr2)} active:{wf2.get('active')}")
