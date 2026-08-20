#!/usr/bin/env python3
"""#97 POC — the brokered-intro consent template: create, check.

WHY: a consent ask must reach the TARGET member, whose 24h window is almost always
closed — so it has to be a Meta-approved template. This is the whole POC step 1:
submit it, see what category Meta gives it. UTILITY is the goal; if Meta's
classifier flips it to MARKETING (allow_category_change=true, so it approves
instead of rejecting), the send path inherits the per-user marketing cap
(error 131049 — hit MDS on 2026-08-04) and we decide with that fact on the table.

No send path in this script ON PURPOSE. Nothing messages anyone until Andy rules
the full flow. (Sibling: olivia_broadcast_template.py, the pattern source.)

USAGE
  python3 scripts/olivia_intro_template.py preview
  python3 scripts/olivia_intro_template.py create   # submit for Meta review
  python3 scripts/olivia_intro_template.py status   # APPROVED / PENDING / REJECTED + category
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
WABA = "1575708577606583"
TEMPLATE_NAME = "mds_intro_request"
LANG = "en_US"

# {{1}} target first name · {{2}} requester full name · {{3}} topic
BODY = ("Hi {{1}}, fellow MDS member {{2}} asked for an introduction to you "
        "about {{3}}. Should I connect you two? Your contact details are shared "
        "only if you accept.")
FOOTER = "MDS member introductions"
BUTTONS = ["Accept intro", "Decline"]
EXAMPLE = ["Eugene", "Andy Verdy", "3PL & logistics"]


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"missing {k} in {ENV}")


def curl(method, url, tok, body=None):
    cmd = ["curl", "-sS", "-X", method, url, "-H", f"Authorization: Bearer {tok}",
           "-H", "Content-Type: application/json", "--max-time", "60"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"error": {"raw": r.stdout[:300]}}


def payload():
    return {
        "name": TEMPLATE_NAME,
        "language": LANG,
        "category": "UTILITY",
        "allow_category_change": True,  # approve-as-marketing beats a rejection: we learn either way
        "components": [
            {"type": "BODY", "text": BODY,
             "example": {"body_text": [EXAMPLE]}},
            {"type": "FOOTER", "text": FOOTER},
            {"type": "BUTTONS", "buttons": [
                {"type": "QUICK_REPLY", "text": b} for b in BUTTONS]},
        ],
    }


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if action == "preview":
        print(BODY, "\n")
        print(f"body {len(BODY)}/1024 · footer {len(FOOTER)}/60 · buttons {BUTTONS}")
        print("example:", dict(zip(["target", "requester", "topic"], EXAMPLE)))
        return
    tok = env("META_WA_TOKEN")
    if action == "create":
        r = curl("POST", f"https://graph.facebook.com/v22.0/{WABA}/message_templates",
                 tok, payload())
        print(json.dumps(r, indent=1)[:800])
        return
    if action == "status":
        r = curl("GET", f"https://graph.facebook.com/v22.0/{WABA}/message_templates"
                        f"?name={TEMPLATE_NAME}&fields=name,status,category,rejected_reason", tok)
        print(json.dumps(r, indent=1)[:800])
        return
    sys.exit("action must be preview | create | status")


if __name__ == "__main__":
    main()
