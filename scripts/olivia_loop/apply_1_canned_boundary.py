#!/usr/bin/env python3
"""#1 canned-lane boundary — apply to STAGING (bqHstPDi84uOhTCJ).

The action lane files tickets without ever touching data, so a DATA-shaped request the
router labeled 'action' was swallowed whole: "Share link to Brandon's post" got a ticket
offer with zero retrieval (Q3061, the standing proof). Structural rule, same shape as
realGreeting: the SIDE-EFFECT lane is ALLOWLISTED deterministically — a true team action
(account/profile/membership change, billing problem, complaint, wanting a human,
team-relay, registration, call-me-X) keeps the ticket lane; everything else routed
'action' is a question wearing an imperative and falls through to the loop, where
retrieval + the fact-gate decide. The loop offers the ticket itself only after actually
looking (CANNOT DO / CANNOT FIND rule in answer_seed.js — applied by build_loop.py, run
it first); the existing yes-detection reads the offer phrase from the history, so an
acceptance still creates the ticket.

Fail direction is deliberate: an allowlist miss reaches the loop and degrades to
offer-after-checking — never a silently lost ask.

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

pr = nodes["Plan Request"]["parameters"]["jsCode"]

ANCHOR = """if (intent === 'action' && ctx.has_history
    && /^(sure|yes|yeah|yep|ok|okay|please|yes please|go ahead|do it|why not|sounds good)[!. ]*$/i.test(rawText)) {
  intent = 'question';
}"""

BOUNDARY = ANCHOR + """

// #1 CANNED-LANE BOUNDARY (2026-07-30). The action lane files tickets without touching data,
// so a DATA-shaped request the router labeled 'action' was swallowed whole - "Share link to
// Brandon's post" got a ticket offer with zero retrieval (Q3061, the standing proof). The
// structural rule, same shape as realGreeting: the SIDE-EFFECT lane is ALLOWLISTED
// deterministically; everything else routed 'action' is a question wearing an imperative and
// falls through to the loop, where retrieval + the fact-gate decide - and the loop offers the
// ticket itself only after actually looking (CANNOT DO / CANNOT FIND seed rule; the existing
// yes-detection reads the offer phrase from her last turn, so acceptance still files it).
// Fail direction is deliberate: an allowlist miss reaches the loop and degrades to
// offer-after-checking - never a silently lost ask.
const trueAction =
  /\\b(update|change|correct|fix|edit|cancel|pause|renew|upgrade|downgrade|unsubscribe|delete|remove|add)\\b[\\s\\S]{0,40}\\b(my|profile|email|phone|address|name|membership|subscription|billing|card|account|info|photo|picture|preference|preferences)\\b/i.test(rawText)
  || /\\b(register|sign (me|us) up|rsvp)\\b/i.test(rawText)
  || /\\b(my|our)\\b[\\s\\S]{0,30}\\b(is wrong|is incorrect|is outdated|is broken|doesn'?t work|not working)\\b/i.test(rawText)
  || /\\b(complain|complaint|refund|charged (me )?(twice|wrong|incorrectly)|billing (issue|problem|error)|payment (issue|problem|failed))\\b/i.test(rawText)
  || /\\b(talk|speak|connect me|put me in touch) (to|with) (a |the )?(human|person|someone|real person|team|staff|support)\\b/i.test(rawText)
  || /\\b(feedback|suggestion|request) (for|to) (the )?(mds )?(team|staff)\\b/i.test(rawText)
  || /\\b(tell|let) the (mds )?(team|staff)\\b/i.test(rawText)
  || /\\bpass (this|that|it|my)\\b[\\s\\S]{0,24}\\b(on|along|to the team)\\b/i.test(rawText)
  || /\\b(call me|address me as|refer to me as)\\b/i.test(rawText);
if (intent === 'action' && !trueAction) {
  intent = 'question';
  if (!(Array.isArray(p.search_terms) && p.search_terms.length)) {
    p.search_terms = String(rawText).toLowerCase().replace(/[^a-z0-9 ]+/g, ' ')
      .replace(/\\b(share|send|show|give|get|pull|find|forward|resend|me|the|a|an|to|of|for|from|link|url|please|can|could|you|olivia)\\b/g, ' ')
      .split(/\\s+/).filter(function (w) { return w.length >= 3; }).slice(0, 3);
  }
}"""

if "const trueAction =" in pr:
    print("Plan Request already patched")
else:
    assert pr.count(ANCHOR) == 1, "affirm-demote anchor not found exactly once — aborting"
    pr = pr.replace(ANCHOR, BOUNDARY)
    nodes["Plan Request"]["parameters"]["jsCode"] = pr
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
print(f"VERIFY boundary:{('const trueAction =' in pr2)} "
      f"anchor_kept:{('sounds good' in pr2)} "
      f"active:{wf2.get('active')}")
