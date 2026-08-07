#!/usr/bin/env python3
"""How far back does Zoom expose attendance via API, per endpoint?

Tries both participant endpoints against known mogul-call UUIDs spanning 2022-2026:
  /report/meetings/{uuid}/participants     (report:read:list_meeting_participants:admin)
  /metrics/meetings/{uuid}/participants    (dashboard:read:list_meeting_participants:admin)
"""
import json
import urllib.parse
import urllib.request

from zoom_probe import CTX, load_env  # reuse token plumbing

import base64

SAMPLES = [
    ("2026-08-05", "PVSocYR9SNCxxjGCWongXw==", "Mogul Call with Dorian Gorski"),
    ("2026-03-25", "xJVEpOqeT36qIZjY16hYlQ==", "MDS Inspire Top Takeaways"),
    ("2025-08-13", "S0yLEEh6TjGcRgau8T0/3A==", "Mogul Call with Euka AI"),
    ("2024-08-28", "Y4D0hRIWTPim9vMV9hI9Gw==", "Mogul Call with Yev Marusenko"),
    ("2024-08-14", "F1FD5rNiR/OtBRxWm4uryQ==", "Mogul Call with Ben Arneberg"),
    ("2023-08-23", "6Ac4ZsveS3anE8eA71XVbw==", "Mogul Call With Matteo Lombardi"),
    ("2023-08-09", "McZScJppSpGX00Dozrucmw==", "Mogul Call with David Ghiyam"),
    ("2022-09-14", "cI/auw7TTw6G5vdxkT9ssg==", "Mogul Call with Adam Weiler"),
]


def token():
    env = load_env()
    basic = base64.b64encode(
        f"{env['ZOOM_CLIENT_ID']}:{env['ZOOM_CLIENT_SECRET']}".encode()
    ).decode()
    url = ("https://zoom.us/oauth/token?grant_type=account_credentials&account_id="
           + urllib.parse.quote(env["ZOOM_ACCOUNT_ID"]))
    req = urllib.request.Request(url, data=b"", headers={"Authorization": "Basic " + basic})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return json.loads(r.read())["access_token"]


def get(url, tok, params):
    url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
            return {"_err": f"{e.code} {body.get('message', '')[:80]}"}
        except Exception:
            return {"_err": str(e.code)}


def main():
    tok = token()
    print(f"{'date':<12} {'dashboard':<28} {'report':<28} topic")
    for date, uuid, topic in SAMPLES:
        enc = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
        d = get(f"https://api.zoom.us/v2/metrics/meetings/{enc}/participants",
                tok, {"type": "past", "page_size": 300})
        r = get(f"https://api.zoom.us/v2/report/meetings/{enc}/participants",
                tok, {"page_size": 300})
        ds = d.get("_err") or f"{d.get('total_records')} rows"
        rs = r.get("_err") or f"{r.get('total_records')} rows"
        print(f"{date:<12} {ds:<28} {rs:<28} {topic}")


if __name__ == "__main__":
    main()
