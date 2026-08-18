#!/usr/bin/env python3
"""#86 — deliver the reminders members asked for.

Reads event.reminders where status='pending' and remind_at has arrived, sends each
one on WhatsApp, and records the outcome. Designed to be run on a short schedule
(every 5 minutes is enough — a 30-minute lead has 30 minutes of slack).

  python3 scripts/olivia_reminder_sender.py --dry-run     # show what is due, send nothing
  python3 scripts/olivia_reminder_sender.py               # send what is due
  python3 scripts/olivia_reminder_sender.py --window 120  # widen the catch-up window

TWO WAYS A REMINDER CAN GO OUT, and the difference decides whether it arrives:

  * INSIDE the 24-hour window (they messaged Olivia in the last 24h) — a free-form
    text works and reads naturally.
  * OUTSIDE it — WhatsApp allows only an approved template. A reminder somebody
    explicitly asked for is a UTILITY template, not marketing, so the per-user
    marketing cap (error 131049, which blocked 17 of 25 on the 2026-08-04
    broadcast) does not apply. Until TEMPLATE_NAME is approved on the WABA this
    script marks those rows 'failed' with the reason rather than pretending.

A 200 from Meta is NOT delivery — see reference_wa_send_200_is_not_delivery. The
truth arrives later on the status webhook and lands in digest.olivia_sends; this
script records what it attempted, never that the member saw it.

Times are always rendered in the EVENT's timezone, never the member's. We do not
know where they are standing and a stored timezone would be wrong the moment they
travel (Andy's ruling, 2026-08-17).
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ENV = "/Users/Born/mds-digest-web/.env.local"
SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
TEMPLATE_NAME = "mds_summit_reminder"      # utility; submit + approve before this fires
LANG = "en_US"
GRAPH = "v22.0"


def iso(dt):
    """PostgREST reads these out of a URL query, where "+" means a space — so a
    "+00:00" offset silently becomes an invalid timestamp. Send Z."""
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


def curl(method, url, token, body=None, headers=()):
    cmd = ["curl", "-s", "-m", "45", "-X", method, url,
           "-H", f"Authorization: Bearer {token}", "-H", "Content-Type: application/json"]
    for h in headers:
        cmd += ["-H", h]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out or "{}")
    except json.JSONDecodeError:
        return {"_raw": out[:300]}


def supa(method, path, key, body=None, schema="event", prefer=None):
    headers = [f"apikey: {key}", f"Accept-Profile: {schema}", f"Content-Profile: {schema}"]
    if prefer:
        headers.append(f"Prefer: {prefer}")
    return curl(method, f"{SUPA}/{path}", key, body, headers)


def window_open(key, phone):
    """Free-form text only reaches a member whose 24h service window is open, which
    their own last inbound message opens."""
    since = iso(datetime.now(timezone.utc) - timedelta(hours=24))
    rows = supa("GET", f"olivia_messages?select=id&phone=eq.{phone}&role=eq.member"
                       f"&created_at=gte.{since}&limit=1", key, schema="digest")
    return isinstance(rows, list) and len(rows) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--window", type=int, default=60,
                    help="minutes of catch-up: a reminder more than this late is skipped, "
                         "because a 'starts in 30 minutes' text two hours afterwards is worse "
                         "than silence")
    args = ap.parse_args()

    key = env("SUPABASE_SECRET_KEY")
    token = env("META_WA_TOKEN")
    pnid = env("META_WA_PHONE_NUMBER_ID")

    now = datetime.now(timezone.utc)
    floor = iso(now - timedelta(minutes=args.window))
    due = supa("GET",
               "reminders?select=id,phone,person_id,remind_at,lead_minutes,activity_id,session_id,"
               "events(title,timezone),activities(name,starts_at,locations(name)),"
               "sessions(title,short_description,starts_at,rooms(name))"
               f"&status=eq.pending&remind_at=lte.{iso(now)}&remind_at=gte.{floor}"
               "&order=remind_at", key)
    if isinstance(due, dict):
        sys.exit(f"lookup failed: {json.dumps(due)[:300]}")

    stale = supa("GET", "reminders?select=id&status=eq.pending"
                        f"&remind_at=lt.{floor}", key)
    if isinstance(stale, list) and stale and not args.dry_run:
        supa("PATCH", f"reminders?id=in.({','.join(str(r['id']) for r in stale)})", key,
             {"status": "failed", "note": f"missed by more than {args.window} min"},
             prefer="return=minimal")
        print(f"{len(stale)} reminder(s) too late to send — marked failed, not sent")

    print(f"{len(due)} due")
    sent = failed = 0
    for r in due:
        ev = r.get("events") or {}
        tz = ev.get("timezone") or "Asia/Singapore"
        thing = r.get("activities") or r.get("sessions") or {}
        name = thing.get("name") or thing.get("title") or "your next session"
        where = ((thing.get("locations") or {}).get("name")
                 or (thing.get("rooms") or {}).get("name") or None)
        starts = thing.get("starts_at")
        when = (datetime.fromisoformat(starts).astimezone(ZoneInfo(tz))
                .strftime("%-I:%M %p") if starts else "shortly")
        city = tz.split("/")[-1].replace("_", " ")
        lead = r.get("lead_minutes")

        text = (f"⏰ *{name}* starts "
                + (f"in {lead} minutes" if lead else f"at {when} {city} time")
                + (f" — {where}" if where else "")
                + f".\n\n({when} {city} time)")

        if args.dry_run:
            print(f"  would send to {r['phone'][:6]}…  {text.splitlines()[0]}")
            continue

        if window_open(key, r["phone"]):
            body = {"messaging_product": "whatsapp", "to": r["phone"], "type": "text",
                    "text": {"body": text}}
        else:
            # Utility template. Two variables: what, and when.
            body = {"messaging_product": "whatsapp", "to": r["phone"], "type": "template",
                    "template": {"name": TEMPLATE_NAME, "language": {"code": LANG},
                                 "components": [{"type": "body", "parameters": [
                                     {"type": "text", "text": name},
                                     {"type": "text", "text": f"{when} {city} time"}]}]}}

        res = curl("POST", f"https://graph.facebook.com/{GRAPH}/{pnid}/messages", token, body)
        if res.get("error"):
            err = json.dumps(res["error"])[:200]
            supa("PATCH", f"reminders?id=eq.{r['id']}", key,
                 {"status": "failed", "note": err}, prefer="return=minimal")
            failed += 1
            print(f"  FAILED {name}: {err}")
            continue
        wamid = ((res.get("messages") or [{}])[0]).get("id")
        supa("PATCH", f"reminders?id=eq.{r['id']}", key,
             {"status": "sent", "sent_at": iso(datetime.now(timezone.utc)),
              "wamid": wamid}, prefer="return=minimal")
        sent += 1
        print(f"  sent {name} -> {r['phone'][:6]}…  wamid {str(wamid)[:24]}")

    print(f"done — {sent} sent, {failed} failed"
          + ("  (dry run, nothing sent)" if args.dry_run else ""))
    # Accepted is not delivered. Read digest.olivia_sends for the truth.
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
