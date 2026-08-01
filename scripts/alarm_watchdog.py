#!/usr/bin/env python3
"""#16 — the watchman's watchman: covers the pg_cron alarm's blind spot (Supabase itself).

The #13 alarm lives IN Supabase — if Supabase (or pg_cron) dies, nothing watches Olivia.
This tiny watchdog runs from a different failure domain (launchd on the Mac, every 15 min):
  BAD = Supabase REST unreachable, OR the alarm's last_tick_at is stale (>15 min).
Alerts straight to Slack (bot token), unlatchable: re-alerts every 30 min while bad,
posts a recovery notice once when good again. State in ~/.olivia_watchdog_state.json.

Run: python3 scripts/alarm_watchdog.py [--test]   (--test forces one alert to prove delivery)
launchd: com.mds.olivia.watchdog, StartInterval 900.
"""
import json, os, subprocess, sys, time

ENV = "/Users/Born/mds-digest-web/.env.local"
STATE = os.path.expanduser("~/.olivia_watchdog_state.json")
CHANNEL = "C0AQ8USNQK0"
STALE_MIN = 15
REPEAT_MIN = 30


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


def slack(text):
    tok = env("CENTURION_SLACK_BOT_TOKEN")
    subprocess.run(
        ["curl", "-sS", "-X", "POST", "https://slack.com/api/chat.postMessage",
         "-H", f"Authorization: Bearer {tok}", "-H", "Content-Type: application/json",
         "--max-time", "20", "--data-binary", json.dumps({"channel": CHANNEL, "text": text})],
        capture_output=True, text=True)


def check():
    base = env("SUPABASE_URL").rstrip("/")
    key = env("SUPABASE_SECRET_KEY")
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "20",
         f"{base}/rest/v1/olivia_alarm_config?k=eq.last_tick_at&select=v",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Accept-Profile: digest"],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return False, "Supabase REST unreachable — the outage alarm is BLIND"
    try:
        rows = json.loads(r.stdout)
        tick = rows[0]["v"]
        from datetime import datetime, timezone
        import re as _re
        # launchd runs Apple's python 3.9 — its fromisoformat can't parse a bare '+00'
        # offset (needs +00:00) and is strict about fraction digits. This spammed
        # "alarm state unreadable" every 30 min for 13h (2026-08-01) while everything
        # was healthy. Normalize before parsing; never let FORMAT read as an outage.
        raw = tick.strip().replace(" ", "T").replace("Z", "+00:00")
        raw = _re.sub(r"([+-]\d{2})$", r"\1:00", raw)
        raw = _re.sub(r"\.(\d{1,6})(?=[+-]|$)", lambda m: "." + m.group(1).ljust(6, "0"), raw)
        t = datetime.fromisoformat(raw).astimezone(timezone.utc)
        age_min = (datetime.now(timezone.utc) - t).total_seconds() / 60
        if age_min > STALE_MIN:
            return False, f"pg_cron alarm last ticked {age_min:.0f}m ago — the watchman is DOWN"
        return True, f"alarm ticking ({age_min:.0f}m ago)"
    except Exception as e:
        return False, f"alarm state unreadable: {e}"


def main():
    st = {}
    try:
        st = json.load(open(STATE))
    except Exception:
        pass
    ok, detail = check()
    if "--test" in sys.argv:
        ok, detail = False, "TEST — forced failure to prove the watchdog's Slack path"
    now = time.time()
    if not ok:
        due = not st.get("lastAlertAt") or now - st["lastAlertAt"] > REPEAT_MIN * 60
        if not st.get("bad") or due:
            slack(f"🚨 *Olivia watchdog (Mac)* — {detail}"
                  + (" (still bad — repeating every 30 min)" if st.get("bad") else ""))
            st["lastAlertAt"] = now
        st["bad"] = True
    else:
        if st.get("bad"):
            slack("✅ *Olivia watchdog (Mac)* — Supabase + the pg_cron alarm are back")
        st = {"bad": False}
    json.dump(st, open(STATE, "w"))
    print(("OK " if ok else "BAD") + " — " + detail)


if __name__ == "__main__":
    main()
