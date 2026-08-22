#!/usr/bin/env python3
"""#109 — submit the three requester-side intro templates to Meta (UTILITY) so the route can
notify a requester whose 24h window is closed (accept / decline / 7-day lapse). Idempotent-ish:
re-running re-submits only names that are absent. Usage:

  python3 scripts/olivia_intro_templates_109.py create   # submit all three
  python3 scripts/olivia_intro_templates_109.py status   # show their review status

Token/WABA mirror scripts/olivia_intro_template.py (the #97 consent template)."""
import json, os, subprocess, sys, tempfile

ENV = "/Users/Born/mds-digest-web/.env.local"
WABA = "1575708577606583"

def env():
    out = {}
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); out[k] = v.strip().strip('"').strip("'")
    return out

def curl(method, url, token, body=None):
    args = ["curl", "-s", "-X", method, url, "-H", f"Authorization: Bearer {token}"]
    path = None
    if body is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            tf.write(json.dumps(body)); path = tf.name
        args += ["-H", "Content-Type: application/json", "--data", f"@{path}"]
    r = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if path: os.unlink(path)
    try: return json.loads(r.stdout or "{}")
    except Exception: return {"raw": r.stdout}

TEMPLATES = [
    {"name": "mds_intro_accepted", "category": "UTILITY", "language": "en_US", "allow_category_change": True,
     # Meta rejects wa.me links in buttons AND in example params ("Direct links to WhatsApp aren't
     # allowed") — so the link is conveyed as the plain phone number, which WhatsApp auto-links.
     "components": [{"type": "BODY",
                     "text": "Good news: {{1}} accepted your intro request — message them on WhatsApp at {{2}} to start the conversation.",
                     "example": {"body_text": [["Tracy", "+1 415 555 0123"]]}}]},
    {"name": "mds_intro_declined", "category": "UTILITY", "language": "en_US", "allow_category_change": True,
     "components": [{"type": "BODY",
                     "text": "No connection with {{1}} yet — I'll let you know if that changes.",
                     "example": {"body_text": [["Tracy"]]}}]},
    {"name": "mds_intro_lapsed", "category": "UTILITY", "language": "en_US", "allow_category_change": True,
     "components": [{"type": "BODY",
                     "text": "I didn't get a response from {{1}} this week, so I've let it rest. Want me to try again later — or introduce you to someone else on {{2}} instead?",
                     "example": {"body_text": [["Tracy", "3PL logistics"]]}}]},
]

def main():
    cmd = (sys.argv[1:] or ["status"])[0]
    token = env()["META_WA_TOKEN"]
    existing = curl("GET", f"https://graph.facebook.com/v22.0/{WABA}/message_templates?fields=name,status,category,id&limit=200", token)
    have = {t["name"]: t for t in existing.get("data", [])}
    if cmd == "create":
        for t in TEMPLATES:
            if t["name"] in have:
                print(f"{t['name']}: already submitted → {have[t['name']].get('status')}"); continue
            r = curl("POST", f"https://graph.facebook.com/v22.0/{WABA}/message_templates", token, t)
            print(f"{t['name']}: {r.get('status') or r.get('error', {}).get('message') or r}")
    else:
        for t in TEMPLATES:
            h = have.get(t["name"])
            print(f"{t['name']}: {h.get('status') if h else 'NOT SUBMITTED'} ({h.get('category') if h else '-'})")

if __name__ == "__main__":
    main()
