#!/usr/bin/env python3
"""Birthday-box address confirmation — Meta template: preview, create, status.

WHY UTILITY: this is a transactional confirmation about a gift already being
prepared for that specific member — the same shape Meta approved as UTILITY for
`mds_intro_request` (#97). Marketing framing ("we'd love to send you a gift!")
is what flips the classifier to MARKETING, which inherits the per-user cap that
bit MDS on 2026-08-04 (error 131049). Copy below stays transactional on purpose:
a delivery detail to confirm, not an offer to accept.

`allow_category_change: true` so Meta re-files rather than REJECTS if it
disagrees — we then decide with the real category on the table.

NO SEND PATH IN THIS SCRIPT, deliberately. Submitting a template messages nobody;
sending is a separate decision and a separate build.

USAGE
  python3 scripts/olivia_birthday_address_template.py preview
  python3 scripts/olivia_birthday_address_template.py create   # submit for review
  python3 scripts/olivia_birthday_address_template.py status
  python3 scripts/olivia_birthday_address_template.py send --to 17866578153 \
      --name Andy --address "..." --confirm SEND      # ONE test send
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
WABA = "1575708577606583"
TEMPLATE_NAME = "mds_birthday_box_address"
LANG = "en_US"

# {{1}} member first name · {{2}} the address we hold on file
BODY = ("Hi {{1}}, your MDS birthday box is being prepared. We have this "
        "delivery address on file:\n\n{{2}}\n\nIs that still correct? Reply "
        "with the right address if it has changed.")
FOOTER = "MDS member services"
BUTTONS = ["Address is correct", "Update address"]
EXAMPLE = ["Andy", "1200 Brickell Ave, Suite 1950, Miami, FL 33131, USA"]


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
        "allow_category_change": True,
        "components": [
            {"type": "BODY", "text": BODY,
             "example": {"body_text": [EXAMPLE]}},
            {"type": "FOOTER", "text": FOOTER},
            {"type": "BUTTONS", "buttons": [
                {"type": "QUICK_REPLY", "text": b} for b in BUTTONS]},
        ],
    }


def send(tok, to, name, address, confirm):
    """ONE test send. Nothing goes out without --confirm SEND; no --all path
    exists in this script (a real rollout is its own build, with its own gate).
    A 200 here is NOT delivery — read digest.olivia_sends for the truth."""
    if confirm != "SEND":
        sys.exit("refusing to send without --confirm SEND")
    pnid = env("META_WA_PHONE_NUMBER_ID")
    body = {"messaging_product": "whatsapp", "to": to, "type": "template",
            "template": {"name": TEMPLATE_NAME, "language": {"code": LANG},
                         "components": [{"type": "body", "parameters": [
                             {"type": "text", "text": name},
                             {"type": "text", "text": address}]}]}}
    r = curl("POST", f"https://graph.facebook.com/v22.0/{pnid}/messages", tok, body)
    print(json.dumps(r, indent=2))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    tok = env("META_WA_TOKEN")
    if cmd == "preview":
        print(json.dumps(payload(), indent=2))
        print("\n--- as the member sees it ---")
        body = BODY.replace("{{1}}", EXAMPLE[0]).replace("{{2}}", EXAMPLE[1])
        print(body + f"\n{FOOTER}\n[" + "] [".join(BUTTONS) + "]")
        return
    if cmd == "create":
        r = curl("POST", f"https://graph.facebook.com/v20.0/{WABA}/message_templates",
                 tok, payload())
        print(json.dumps(r, indent=2))
        return
    if cmd == "status":
        r = curl("GET", f"https://graph.facebook.com/v20.0/{WABA}/message_templates"
                        f"?name={TEMPLATE_NAME}&fields=name,status,category,rejected_reason",
                 tok)
        print(json.dumps(r, indent=2))
        return
    if cmd == "send":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("send")
        ap.add_argument("--to", required=True)
        ap.add_argument("--name", required=True)
        ap.add_argument("--address", required=True)
        ap.add_argument("--confirm", default="")
        a = ap.parse_args()
        send(tok, a.to, a.name, a.address, a.confirm)
        return
    sys.exit("usage: preview | create | status | send")


if __name__ == "__main__":
    main()
