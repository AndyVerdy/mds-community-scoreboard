#!/usr/bin/env python3
"""
Olivia self-test harness — fires a question bank at the LIVE webhook as the probe
member, then pulls her actual replies from digest.olivia_messages for scoring.

⚠️ Replies DELIVER to the probe member's WhatsApp when their 24h window is open —
tell them first. Every run pollutes their transcript; pass --cleanup afterwards to
delete the test turns/claims/sends (their real turns are untouched: deletion is
bounded by this run's SELFTEST wamid timestamps).

Usage:
  python3 scripts/olivia_selftest.py                # fire the bank (~4 min), then print Q→A
  python3 scripts/olivia_selftest.py --cleanup      # delete this run's test rows
  python3 scripts/olivia_selftest.py --questions "who is around me?" "new question"
  python3 scripts/olivia_selftest.py --staging --questions "reset" "<q>"
                                # fire at the STAGING copy (scripts/olivia_wf.py) —
                                # the required path before promoting any edit

Scoring is human/Claude work — read the printed transcript against the expectations
in SESSION_LOG (groups: digests verbatim · search+quotes · follow-ups/reset · people
near/like · destination · traits/audience · self/chats · gates-must-refuse-honestly).
"""
import argparse
import json
import subprocess
import sys
import time

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
WEBHOOK = "https://mdsco.app.n8n.cloud/webhook/olivia-wa-live"
STAGING_WEBHOOK = "https://mdsco.app.n8n.cloud/webhook/olivia-wa-staging"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
PROBE_PHONE = "17866578153"  # Andy — the only member whose phone may be simulated
MARK = "wamid.SELFTEST"
TARGET_WEBHOOK = WEBHOOK  # overridden by --staging

BANK = [
    ("weekly digest for MDS Supplements", 8),
    ("what happened in MDS Logistics yesterday", 10),
    ("what are people saying about tariffs?", 22),
    ("what about in the retail chat?", 22),
    ("new question", 6),
    ("who is around me?", 20),
    ("who is around me in my niche?", 20),
    ("im going to miami next month, who should i meet there?", 20),
    ("who sells on walmart?", 20),
    ("planning a dinner for supplements sellers in new york, who should i invite?", 22),
    ("what is nasir's revenue?", 20),
    ("does rich reister sell on tiktok?", 22),
    ("what do you know about me?", 8),
    ("what did I write on my application?", 8),
    ("new question", 6),
    # events group (source #2, added 2026-07-20; full 28-question bank lives in
    # SESSION_LOG 2026-07-20 late — this is the standing representative subset)
    ("any events coming up?", 20),
    ("im planning to visit new york - when should i go? i want to hit some mds events", 22),
    ("im really into tiktok shop right now, any events for me?", 22),
    ("who is going to the tiktok dinner in new york?", 20),
    ("how many spots are left for the tiktok dinner?", 20),
    ("can i bring my wife to the puerto rico dinner?", 20),
    ("what events am i registered for?", 20),
    ("have i been to inspire before?", 20),
    ("is the new york chapter dinner in july still happening?", 20),
    ("what is the centurion summit? can i join?", 22),
    ("new question", 6),
]


def load_key():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_SECRET_KEY"]


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


def fire(text, tag):
    ts = int(time.time())
    payload = {"entry": [{"changes": [{"value": {
        "messaging_product": "whatsapp",
        "metadata": {"display_phone_number": "19453965415", "phone_number_id": "1306956855827812"},
        "contacts": [{"profile": {"name": "Andy"}, "wa_id": PROBE_PHONE}],
        "messages": [{"from": PROBE_PHONE, "id": f"{MARK}_{tag}_{ts}",
                      "timestamp": str(ts), "type": "text", "text": {"body": text}}]},
        "field": "messages"}]}]}
    p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", TARGET_WEBHOOK,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return p.stdout


def last_id(key):
    """Newest olivia_messages id for the probe member (0 when the thread is empty)."""
    rows = curl("GET", f"{BASE}/olivia_messages?phone=eq.{PROBE_PHONE}"
                       f"&order=id.desc&limit=1&select=id", key)
    return rows[0]["id"] if rows else 0


def wait_persisted(key, baseline, timeout, text=None):
    """Block until THIS turn's own reply is in digest.olivia_messages.

    Fixed 2026-08-03 (#52): the harness paced by sleep(20), so any answer slower than that
    fired the next question while Save Conversation was still running — the next turn then
    read INCOMPLETE history (no prev_plan) and manufactured a phantom failure. Multi-turn
    probes are the whole proof for follow-up binding, so the pacing has to wait on
    PERSISTENCE. Returns seconds waited, or -1 on timeout (reported, never silent).

    Fixed 2026-08-23 (#119 bank B): "any olivia row newer than baseline" is NOT this turn's
    reply — the nightly eval (`olivia_eval.py --nightly`, launchd 03:30 ET) writes to the SAME
    probe phone, so its replies satisfied the check and the harness raced ahead. Every bank-B
    turn reported a uniform ~3.1s "persisted" (one poll tick) while real answers take 6-20s,
    and follow-ups fired before the offer they had to bind to existed — manufacturing exactly
    the phantom failures #52 was written to prevent. The wait now finds THIS turn's own member
    row (by text, newer than baseline) and waits for the olivia row that follows IT.
    """
    t0 = time.time()
    want = (text or "").strip()
    while time.time() - t0 < timeout:
        time.sleep(3)
        rows = curl("GET", f"{BASE}/olivia_messages?phone=eq.{PROBE_PHONE}"
                           f"&id=gt.{baseline}&order=id.asc&limit=200&select=id,role,text", key) or []
        mine = next((r for r in rows if r["role"] == "member" and (r["text"] or "").strip() == want), None)
        if mine is None:
            continue                      # our own question has not even landed yet
        reply = next((r for r in rows if r["role"] == "olivia" and r["id"] > mine["id"]), None)
        if reply:
            return round(time.time() - t0, 1)
    return -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleanup", action="store_true", help="delete this run's test rows and exit")
    ap.add_argument("--questions", nargs="+", help="override the question bank")
    ap.add_argument("--staging", action="store_true",
                    help="fire at the STAGING copy (scripts/olivia_wf.py stage) instead of live")
    ap.add_argument("--timeout", type=int, default=180,
                    help="max seconds to wait for a turn to persist before moving on")
    args = ap.parse_args()
    key = load_key()

    global TARGET_WEBHOOK
    TARGET_WEBHOOK = STAGING_WEBHOOK if args.staging else WEBHOOK
    print(f"target: {TARGET_WEBHOOK}")

    if args.cleanup:
        curl("POST", f"{BASE}/rpc/", key)  # no-op keepalive
        # bounded by SELFTEST claim timestamps — real member turns are untouched
        subprocess.run(["curl", "-s", "-X", "DELETE",
            f"{BASE}/olivia_messages?phone=eq.{PROBE_PHONE}&created_at=gte." +
            json.dumps(curl("GET", f"{BASE}/olivia_seen?wamid=like.{MARK}*&select=seen_at&order=seen_at.asc&limit=1", key)[0]["seen_at"]).strip('"'),
            "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
            "-H", "Content-Profile: digest"], capture_output=True, text=True)
        curl("DELETE", f"{BASE}/olivia_seen?wamid=like.{MARK}*", key)
        print("cleanup done (bounded by this run's SELFTEST timestamps)")
        return

    bank = [(q, 20) for q in args.questions] if args.questions else BANK
    print(f"firing {len(bank)} questions as {PROBE_PHONE[:4]}… (replies deliver to their phone)")
    for i, (text, _wait) in enumerate(bank):
        baseline = last_id(key)
        code = fire(text, f"Q{i:02d}")
        took = wait_persisted(key, baseline, args.timeout, text)
        mark = f"{took}s" if took >= 0 else f"NOT PERSISTED in {args.timeout}s"
        print(f"  Q{i:02d} [{code}] {mark:>22}  {text[:60]}", flush=True)

    time.sleep(5)
    rows = curl("GET", f"{BASE}/olivia_messages?phone=eq.{PROBE_PHONE}"
                f"&order=id.desc&limit={len(bank)*2 + 4}&select=role,route,text", key)
    print("\n=== TRANSCRIPT (newest first) ===")
    for r in rows or []:
        who = "M" if r["role"] == "member" else "O"
        print(f"\n[{who}·{r['route']}] {r['text'][:900]}")


if __name__ == "__main__":
    main()
