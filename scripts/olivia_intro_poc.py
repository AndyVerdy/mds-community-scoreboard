#!/usr/bin/env python3
"""#97 POC — brokered intro, end to end on a test number.

The flow this mimics (consent-first, Andy's ruling pending on the full shape):
  1. `request` — ledger row born 'pending', the APPROVED template `mds_intro_request`
     goes to the TARGET (name, requester, topic). No number moves.
  2. The target taps *Accept intro* or *Decline* on their phone. The tap arrives on
     the production webhook like any message and lands in digest.olivia_messages.
  3. `watch` — polls for that tap. Accept: both sides get the wa.me link (the target
     just tapped, so their window is open; the requester asked, so theirs is too),
     row flips 'accepted'. Decline: row flips 'declined', requester is told softly —
     never "they said no".

⚠️ POC GUARD: sends are allowed ONLY to the test number (Andy's). The real flow —
who may request, rate caps per target, expiry, workflow branch on the button ids —
is Andy's ruling AFTER this proves the mechanics.

USAGE
  python3 scripts/olivia_intro_poc.py request --topic "brokered intros" --confirm SEND
  python3 scripts/olivia_intro_poc.py watch --id <ledger id> [--timeout 900]
  python3 scripts/olivia_intro_poc.py status
"""
import argparse
import json
import subprocess
import sys
import time

ENV = "/Users/Born/mds-digest-web/.env.local"
SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
GRAPH = "https://graph.facebook.com/v22.0"
TEMPLATE = "mds_intro_request"
LANG = "en_US"
TEST_PHONE = "17866578153"          # Andy — the only number this POC may message
TEST_AT_ID = "recCUUw8iiUnJjac1"    # his member record (requester AND target in the POC)
REQUESTER_LABEL = "MDS POC Test"    # what the template shows as the asking member
TARGET_FIRST = "Andy"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"missing {k} in {ENV}")


def curl(method, url, headers, body=None):
    cmd = ["curl", "-sS", "-X", method, url, "--max-time", "60",
           "-H", "Content-Type: application/json"]
    for h in headers:
        cmd += ["-H", h]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except Exception:
        return {"error": {"raw": r.stdout[:300]}}


def sb_headers(key):
    return [f"apikey: {key}", f"Authorization: Bearer {key}",
            "Accept-Profile: digest", "Content-Profile: digest"]


def wa_send(tok, pnid, body):
    return curl("POST", f"{GRAPH}/{pnid}/messages", [f"Authorization: Bearer {tok}"], body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["request", "watch", "status"])
    ap.add_argument("--topic", default="brokered intros")
    ap.add_argument("--id", type=int)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--confirm", default="")
    a = ap.parse_args()

    key = env("SUPABASE_SECRET_KEY")

    if a.action == "status":
        rows = curl("GET", f"{SUPA}/olivia_intros?select=*&order=id.desc&limit=10",
                    sb_headers(key))
        for r in rows if isinstance(rows, list) else []:
            print(f"#{r['id']}  {r['status']:<9} topic={r['topic']!r} "
                  f"created={r['created_at'][:19]} decided={str(r['decided_at'])[:19]}")
        return

    tok = env("META_WA_TOKEN")
    pnid = env("META_WA_PHONE_NUMBER_ID")

    if a.action == "request":
        if a.confirm != "SEND":
            sys.exit("refusing to send without --confirm SEND (this messages the test phone)")
        row = curl("POST", f"{SUPA}/olivia_intros", sb_headers(key) + ["Prefer: return=representation"],
                   [{"requester_at_id": TEST_AT_ID, "target_at_id": TEST_AT_ID, "topic": a.topic}])
        if not isinstance(row, list) or not row:
            sys.exit(f"ledger insert failed: {json.dumps(row)[:300]}")
        intro_id = row[0]["id"]
        body = {"messaging_product": "whatsapp", "to": TEST_PHONE, "type": "template",
                "template": {"name": TEMPLATE, "language": {"code": LANG}, "components": [
                    {"type": "body", "parameters": [
                        {"type": "text", "text": TARGET_FIRST},
                        {"type": "text", "text": REQUESTER_LABEL},
                        {"type": "text", "text": a.topic}]}]}}
        r = wa_send(tok, pnid, body)
        wamid = ((r.get("messages") or [{}])[0]).get("id")
        if not wamid:
            sys.exit(f"send failed: {json.dumps(r)[:300]}")
        curl("PATCH", f"{SUPA}/olivia_intros?id=eq.{intro_id}", sb_headers(key),
             {"consent_wamid": wamid})
        print(f"intro #{intro_id} pending — consent template sent, wamid {wamid}")
        print("REMEMBER: a 200 is not delivery — check digest.olivia_sends for the status.")
        print(f"next: python3 scripts/olivia_intro_poc.py watch --id {intro_id}")
        return

    if a.action == "watch":
        if not a.id:
            sys.exit("--id required")
        row = curl("GET", f"{SUPA}/olivia_intros?id=eq.{a.id}&select=*", sb_headers(key))
        if not isinstance(row, list) or not row:
            sys.exit("no such intro")
        # PostgREST: '+' in a URL query is a SPACE — send Z-suffixed timestamps
        sent_at = row[0]["created_at"].replace("+00:00", "Z")
        print(f"watching intro #{a.id} (sent {sent_at[:19]}) for the tap…")
        deadline = time.time() + a.timeout
        while time.time() < deadline:
            # POC finding (2026-08-20): template quick-reply taps arrive as
            # msg_type='button' and are NOT persisted into olivia_messages by the
            # workflow — the raw webhook store is the only place they land.
            msgs = curl("GET", f"{SUPA}/olivia_webhook_events?from_phone=eq.{TEST_PHONE}"
                               f"&msg_type=eq.button&received_at=gt.{sent_at}"
                               f"&select=payload,received_at"
                               f"&order=received_at.desc&limit=10", sb_headers(key))
            taps = []
            for m in (msgs if isinstance(msgs, list) else []):
                try:
                    btn = m["payload"]["entry"][0]["changes"][0]["value"]["messages"][0]["button"]
                    taps.append(btn.get("text", ""))
                except Exception:
                    continue
            taps = [t for t in taps if t.strip().lower() in ("accept intro", "decline")]
            if taps:
                tap = taps[0].strip().lower()
                verdict = "accepted" if tap == "accept intro" else "declined"
                curl("PATCH", f"{SUPA}/olivia_intros?id=eq.{a.id}", sb_headers(key),
                     {"status": verdict, "decided_at": "now()"})
                print(f"tap: {tap!r} → intro #{a.id} {verdict.upper()}")
                if verdict == "accepted":
                    # both sides get the link — POC: both are the test phone
                    for label, num in [("You're connected with " + REQUESTER_LABEL, TEST_PHONE),
                                       ("Andy accepted your intro request", TEST_PHONE)]:
                        wa_send(tok, pnid, {"messaging_product": "whatsapp", "to": TEST_PHONE,
                                "type": "text", "text": {"preview_url": False,
                                "body": f"{label} — start the conversation: wa.me/{num}"}})
                    print("links sent both ways (POC: both to the test phone)")
                else:
                    wa_send(tok, pnid, {"messaging_product": "whatsapp", "to": TEST_PHONE,
                            "type": "text", "text": {"preview_url": False,
                            "body": "POC requester notice: no connection yet — I'll let you know if that changes."}})
                    print("requester softly notified (never 'they said no')")
                return
            time.sleep(5)
        print("timeout — no tap seen; ledger row stays pending")
        sys.exit(1)


if __name__ == "__main__":
    main()
