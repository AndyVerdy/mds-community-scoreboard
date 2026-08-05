#!/usr/bin/env python3
"""MDS Assistant "What's new" — WhatsApp Business TEMPLATE: create, check, and (only when
explicitly asked) broadcast.

WHY A TEMPLATE: free-form WhatsApp messages only reach a member whose 24-hour window is open.
Almost every member's is closed, so a broadcast MUST go out as a Meta-approved template.

USAGE
  python3 scripts/olivia_broadcast_template.py create   --waba <WABA_ID>   # submit for approval
  python3 scripts/olivia_broadcast_template.py status   --waba <WABA_ID>   # APPROVED / PENDING / REJECTED
  python3 scripts/olivia_broadcast_template.py preview                     # print the body, char count
  python3 scripts/olivia_broadcast_template.py send --to 17866578153       # ONE test send
  python3 scripts/olivia_broadcast_template.py send --all --confirm SEND   # the real broadcast

The WABA id is in Meta Business Manager → WhatsApp Accounts → (account) → the id under its name,
or in the WhatsApp API Setup screen. The system-user token here cannot enumerate it.

BEFORE THE REAL BROADCAST — read this:
  * MARKETING category. Meta throttles marketing per user (error 131049 has hit MDS before) and
    charges per marketing conversation. Utility category is NOT available for a product update.
  * Only send to members who have messaged the assistant at least once. Blasting people who never
    opted in is what drops the number's quality rating (currently GREEN) and risks a block.
  * --all paces at 5 messages/second and stops on the first hard error.
  * Nothing sends without --confirm SEND. There is no default-yes path.
"""
import argparse, json, subprocess, sys, time

ENV = "/Users/Born/mds-digest-web/.env.local"
SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
TEMPLATE_NAME = "mds_assistant_whats_new_aug2026"
LANG = "en_US"

BODY = """*MDS Assistant — what's new*

*Tap instead of type* — yes/no questions now come with buttons.

*Reports get confirmed first* — I read your words back and file only when you tap Send it.

*Recommendations you'd actually pick* — events, videos, partners and chats are judged against what you're working on, not just listed.

*Accurate partner rankings* — "most reviews", "highest rated", "most claimed" now sort the whole directory.

*Your MDS credit* — ask "how much MDS credit do I have?"

*Find members anywhere* — "who's in Germany?", "who's in the Balkans?", "who's in the Southern states?"

*Follow-ups stay on topic* — ask about lenders, then "how about on Facebook?" and you'll still get lenders.

*Straighter answers* — fewer holding messages, fewer refusals, no invented people.

Just reply here to try it."""

FOOTER = "Reply STOP to mute these updates"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k}")


def curl(method, url, token, body=None, extra=None):
    cmd = ["curl", "-sS", "-X", method, url, "-H", f"Authorization: Bearer {token}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    cmd += extra or []
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[:400]}


def payload():
    return {
        "name": TEMPLATE_NAME,
        "language": LANG,
        "category": "MARKETING",
        "components": [
            {"type": "BODY", "text": BODY},
            {"type": "FOOTER", "text": FOOTER},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["create", "status", "preview", "send"])
    ap.add_argument("--waba", help="WhatsApp Business Account id (Meta Business Manager)")
    ap.add_argument("--to", help="single recipient, digits only")
    ap.add_argument("--all", action="store_true", help="every member who has messaged the assistant")
    ap.add_argument("--confirm", default="", help="type SEND to actually send")
    a = ap.parse_args()

    if a.action == "preview":
        print(BODY)
        print(f"\n--- body {len(BODY)} chars (Meta limit 1024) · footer {len(FOOTER)}/60 ---")
        print("VALID" if len(BODY) <= 1024 and len(FOOTER) <= 60 else "TOO LONG — trim before submitting")
        return

    tok = env("META_WA_TOKEN")
    pnid = env("META_WA_PHONE_NUMBER_ID")

    if a.action == "create":
        if not a.waba:
            sys.exit("--waba required (Meta Business Manager → WhatsApp Accounts)")
        assert len(BODY) <= 1024, f"body is {len(BODY)} chars, limit 1024"
        r = curl("POST", f"https://graph.facebook.com/v22.0/{a.waba}/message_templates", tok, payload())
        print(json.dumps(r, indent=1)[:800])
        return

    if a.action == "status":
        if not a.waba:
            sys.exit("--waba required")
        r = curl("GET", f"https://graph.facebook.com/v22.0/{a.waba}/message_templates"
                        f"?name={TEMPLATE_NAME}&fields=name,status,category,rejected_reason", tok)
        print(json.dumps(r, indent=1)[:800])
        return

    # ---- send ----
    if a.confirm != "SEND":
        sys.exit("refusing to send without --confirm SEND")
    key = env("SUPABASE_SECRET_KEY")
    if a.to:
        targets = [a.to]
    elif a.all:
        # THE AUDIENCE (Andy 2026-08-04: "only to people who used it"): members who have actually
        # sent the assistant a message, minus anyone who opted out, minus the probe number.
        # This is the whole opt-in population — 25 people, not the 748-member roster.
        rows = curl("GET", f"{SUPA}/rpc/olivia_broadcast_audience", key, {},
                    extra=["-H", f"apikey: {key}", "-H", "Accept-Profile: digest",
                           "-H", "Content-Profile: digest"])
        if isinstance(rows, dict) and rows.get("code"):
            sys.exit(f"audience lookup failed: {json.dumps(rows)[:300]}")
        targets = [r["phone"] for r in rows]
        print(f"AUDIENCE — {len(targets)} members who have used the assistant:")
        for r in rows:
            print(f"   {r['full_name']:<24} {r['turns']:>4} turns · last {r['last_use']}")
        print()
    else:
        sys.exit("--to <phone> or --all")

    sent = 0
    for i, phone in enumerate(targets, 1):
        body = {"messaging_product": "whatsapp", "to": phone, "type": "template",
                "template": {"name": TEMPLATE_NAME, "language": {"code": LANG}}}
        r = curl("POST", f"https://graph.facebook.com/v22.0/{pnid}/messages", tok, body)
        if r.get("error"):
            print(f"STOPPED at {i}/{len(targets)} ({phone}): {json.dumps(r['error'])[:200]}")
            break
        sent += 1
        if i % 25 == 0:
            print(f"  {i}/{len(targets)} sent")
        time.sleep(0.2)
    print(f"done — {sent} sent")


if __name__ == "__main__":
    main()
