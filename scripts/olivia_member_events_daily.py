#!/usr/bin/env python3
"""#46 — the DAILY half of the member-events log, plus the live-flow watchdog.

1. Calls digest.derive_member_change_events(): diffs member_attributes against the key-field
   snapshot and emits attr_changed / status_changed events (cadence 'daily', stamped at
   detection — a batch-detected change never pretends to be a live timestamp).
2. LIVE-FLOW ASSERTION: if olivia_messages grew in the last 24h but zero olivia_turn events
   were captured, the live trigger is dead — exit 1 so the heartbeat goes stale-with-error
   and the #13 alarm pages. Silence must never look like success.

Runs under nightly_derivations.py (job 'member_events_daily'). Python 3.9-safe, stdlib only.
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"


def env():
    v = {}
    for line in open(ENV):
        if "=" in line and not line.startswith("#"):
            k, val = line.strip().split("=", 1)
            v[k.strip()] = val.strip().strip('"').strip("'")
    return v


def sb(method, path, key, body=None):
    cmd = ["curl", "-sS", "-m", "120", "-X", method, BASE + "/" + path,
           "-H", "apikey: " + key, "-H", "Authorization: Bearer " + key,
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json", "-H", "Prefer: count=exact"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r


def count(path, key):
    r = subprocess.run(["curl", "-sS", "-m", "60", "-I", "-X", "GET", BASE + "/" + path,
                        "-H", "apikey: " + key, "-H", "Authorization: Bearer " + key,
                        "-H", "Accept-Profile: digest", "-H", "Prefer: count=exact",
                        "-H", "Range: 0-0"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.lower().startswith("content-range:"):
            return int(line.rsplit("/", 1)[-1].strip())
    return -1


def main():
    key = env()["SUPABASE_SECRET_KEY"]
    r = sb("POST", "rpc/derive_member_change_events", key, {})
    try:
        out = json.loads(r.stdout)
    except Exception:
        print("derive failed (non-JSON): " + r.stdout[:200])
        sys.exit(1)
    # an ERROR response is valid JSON too — never mistake it for success (bit us on day one:
    # a 42804 error printed as 'changes None' and exited 0)
    if not isinstance(out, dict) or "change_events" not in out:
        print("derive errored: " + r.stdout[:200])
        sys.exit(1)
    # live-flow watchdog (real traffic only; eval wamids never write events by design)
    import datetime
    since = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    msgs = count("olivia_messages?role=eq.olivia&created_at=gte." + since
                 + "&wamid=not.like.wamid.SELFTEST*", key)
    evts = count("member_events?event_type=eq.olivia_turn&cadence=eq.live&captured_at=gte." + since, key)
    ok = not (msgs > 0 and evts == 0)
    print("done — changes " + str(out.get("change_events")) + ", seed " + str(out.get("first_run_seed"))
          + ", live-flow 24h: msgs " + str(msgs) + " / events " + str(evts)
          + ("" if ok else "  LIVE TRIGGER DEAD"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
