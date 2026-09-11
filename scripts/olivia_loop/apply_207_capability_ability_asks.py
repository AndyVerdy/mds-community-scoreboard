#!/usr/bin/env python3
"""#190 Q5008 — an ABILITY question about Millie herself is answered from the capability list.

"Are you able to do daily reminders or routines?" was planned as `content_lookup` over the WhatsApp
digests — a question about Millie answered from member content — and she improvised: first the exam
answer overclaimed reminders "for any event or call", then the re-probe answered about the Singapore
Summit having wrapped. Neither is the truth, which is narrow and knowable: reminders exist only for
Summit schedule items, and there are no recurring routines and no monitoring.

The existing `helpAsk` detector already routes capability questions to the CURATED list (#79) —
it simply had no pattern for "are you able to <assistant mechanic>". Two edits:
  1. helpAsk gains that pattern, deliberately scoped to assistant-MECHANIC verbs (remind, notify,
     alert, monitor, schedule, automate, integrate...). Content verbs (find, search, show, tell)
     are excluded, so "can you find me a member in Miami" keeps its own lane.
  2. the curated list gains the one line it was missing, so the answer is the truth rather than a
     guess: Summit-schedule reminders only, no recurring routines, no watching.
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
STAGING_ID = "bqHstPDi84uOhTCJ"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", "X-N8N-API-KEY: " + KEY,
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


PLAN_ANCHOR = "  || /\\bwho are you\\b/i.test(rawText);"
PLAN_NEW = """  || /\\bwho are you\\b/i.test(rawText)
  // #190 Q5008 (2026-09-11): an ABILITY question about Millie's own mechanics — "are you able to do
  // daily reminders or routines?" — was planned as a digest browse and answered by improvising a
  // capability. The curated list is the answer here too. Scoped to assistant MECHANICS on purpose:
  // remind/notify/monitor/schedule/automate, never find/search/show/tell, so "can you find me a
  // member in Miami" keeps its own lane. A named subject ("remind me about the dinner") is a real
  // reminder ask and is excluded — this fires only on the bare can-you-do-X question.
  || (/\\b(are|can|could|do) you\\b[\\s\\S]{0,24}\\b(able to|capable of|support|handle|do|set ?up|offer)?\\b[\\s\\S]{0,24}\\b(remind(?:er|ers|ing)?|routines?|notif(?:y|ication|ications)|alerts?|monitor(?:ing)?|watch(?:ing)? for|schedul(?:e|ing)|automat(?:e|ion)|integrat(?:e|ion)|subscribe)\\b/i.test(rawText)
      && !/\\b(remind me|at \\d|in \\d|tomorrow|tonight|about the)\\b/i.test(rawText));"""

HELP_ANCHOR = "    '⚠️ *I’m in early beta.* I’ll get things wrong sometimes. React 👍 or 👎 to any answer — that helps me improve.',"
HELP_NEW = """    '*What I can’t do*',
    '',
    'I can remind you about *Summit schedule items* — nothing else. No daily reminders, no recurring routines, no watching a thread or a listing for changes, and no changes to your account or billing. For those, say the word and I’ll open a ticket with the MDS team.',
    '',
""" + HELP_ANCHOR


def patch(node, edits, label):
    code = node["parameters"]["jsCode"]
    before = len(code)
    for old, new in edits:
        n = code.count(old)
        if n != 1:
            print(f"ABORT [{label}]: anchor x{n}, expected 1:\n  {old[:110]}…", file=sys.stderr)
            sys.exit(2)
        code = code.replace(old, new)
    node["parameters"]["jsCode"] = code
    print(f"{label}: {before} -> {len(code)} chars")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    patch(next(n for n in nodes if n["name"] == "Plan Request"), [(PLAN_ANCHOR, PLAN_NEW)], "Plan Request")
    patch(next(n for n in nodes if n["name"] == "Build Verbatim Digest"), [(HELP_ANCHOR, HELP_NEW)], "Build Verbatim Digest")
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
