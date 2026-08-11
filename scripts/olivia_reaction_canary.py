#!/usr/bin/env python3
"""#75 — reaction round-trip canary: prove the reaction path end-to-end, then clean up.

Fires a synthetic Meta reaction payload (probe phone, SELFTEST-marked target) at the
webhook and asserts BOTH persistence layers gained the row:

  digest.olivia_webhook_events  — the raw store (#75), written before any parse
  digest.olivia_feedback        — the parsed row (Parse Reaction -> Save Feedback)

A reaction generates NO reply (Log Inbound returns null for type='reaction'), so this is
silent — nothing is ever delivered to anyone. Cleanup deletes exactly this run's rows.

NOTE: the raw-store assertion only holds on a surface that HAS the #75 nodes. Until the
promote, that is staging (--staging); after it, prod too.

Usage:
  python3 scripts/olivia_reaction_canary.py             # prod webhook
  python3 scripts/olivia_reaction_canary.py --staging   # staging webhook
  python3 scripts/olivia_reaction_canary.py --cleanup   # delete ALL canary rows (both layers)

Exit 0 = both rows landed (or cleanup done) · exit 1 = a layer is dropping reactions.
"""
import json
import subprocess
import sys
import time

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
WEBHOOK = "https://mdsco.app.n8n.cloud/webhook/olivia-wa-live"
STAGING_WEBHOOK = "https://mdsco.app.n8n.cloud/webhook/olivia-wa-staging"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
PROBE_PHONE = "17866578153"  # Andy — the only member whose phone may be simulated
MARK = "wamid.SELFTEST_REACTCANARY"


def env(k):
    for l in open(ENV_PATH):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k} in {ENV_PATH}")


def curl(method, url, key, body=None):
    cmd = ["curl", "-s", "-X", method, url, "-H", f"apikey: {key}",
           "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(p.stdout) if p.stdout.strip() else None
    except json.JSONDecodeError:
        return p.stdout


def cleanup(key):
    for url in (f"{BASE}/olivia_feedback?wamid=like.*SELFTEST_REACTCANARY*",
                f"{BASE}/olivia_webhook_events?wamid=like.*reactcanary*",
                f"{BASE}/olivia_webhook_events?payload=like.*SELFTEST_REACTCANARY*"):
        curl("DELETE", url, key)
    print("canary rows deleted (feedback + raw store)")


def main():
    key = env("SUPABASE_SECRET_KEY")
    if "--cleanup" in sys.argv:
        cleanup(key)
        return

    target_webhook = STAGING_WEBHOOK if "--staging" in sys.argv else WEBHOOK
    ts = int(time.time())
    target = f"{MARK}_{ts}"          # the message being "reacted to" (feedback.wamid)
    event_id = f"reactcanary_{ts}"   # the reaction event's own id (raw store wamid)
    payload = {"entry": [{"changes": [{"value": {
        "messaging_product": "whatsapp",
        "metadata": {"display_phone_number": "19453965415", "phone_number_id": "1306956855827812"},
        "contacts": [{"profile": {"name": "Andy"}, "wa_id": PROBE_PHONE}],
        "messages": [{"from": PROBE_PHONE, "id": event_id, "timestamp": str(ts),
                      "type": "reaction",
                      "reaction": {"message_id": target, "emoji": "\U0001f44d"}}]},
        "field": "messages"}]}]}
    p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", target_webhook,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    print(f"webhook {target_webhook.rsplit('/', 1)[1]}: HTTP {p.stdout}")
    if p.stdout != "200":
        sys.exit("webhook did not accept the canary")

    ok_feedback = ok_raw = False
    for _ in range(15):
        time.sleep(2)
        if not ok_feedback:
            rows = curl("GET", f"{BASE}/olivia_feedback?wamid=eq.{target}&select=wamid,emoji", key)
            ok_feedback = bool(rows)
        if not ok_raw:
            rows = curl("GET", f"{BASE}/olivia_webhook_events?wamid=eq.{event_id}"
                               f"&select=id,msg_type", key)
            ok_raw = bool(rows)
        if ok_feedback and ok_raw:
            break

    print(f"raw store row:  {'OK' if ok_raw else 'MISSING'}")
    print(f"feedback row:   {'OK' if ok_feedback else 'MISSING'}")
    cleanup(key)
    if not (ok_feedback and ok_raw):
        sys.exit(1)
    print("reaction path GREEN end-to-end")


if __name__ == "__main__":
    main()
