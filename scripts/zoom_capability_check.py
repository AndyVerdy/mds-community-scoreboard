#!/usr/bin/env python3
"""What the current Zoom S2S scopes can actually do:
account-wide recording listing, per-meeting files, and VTT transcript fetch.
"""
import json
import urllib.parse
import urllib.request

from zoom_probe import CTX
from zoom_attendance_horizon import token


def get(url, tok, params=None, raw=False):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
            body = r.read()
            return body.decode("utf-8", "replace") if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        return {"_err": f"{e.code} {e.read().decode()[:150]}"}


def main():
    tok = token()

    acc = get("https://api.zoom.us/v2/accounts/me/recordings", tok,
              {"from": "2026-07-01", "to": "2026-07-31", "page_size": 30})
    if "_err" in acc:
        print("ACCOUNT RECORDINGS:", acc["_err"])
        return
    meetings = acc.get("meetings", [])
    print(f"ACCOUNT RECORDINGS Jul-2026: {acc.get('total_records')} meetings")
    mogul = [m for m in meetings if "mogul" in m.get("topic", "").lower()]
    print("  mogul calls:", ", ".join(f"{m['start_time'][:10]}" for m in mogul))

    if not mogul:
        return
    target = mogul[-1]
    enc = urllib.parse.quote(urllib.parse.quote(target["uuid"], safe=""), safe="")
    rec = get(f"https://api.zoom.us/v2/meetings/{enc}/recordings", tok)
    if "_err" in rec:
        print("MEETING RECORDINGS:", rec["_err"])
        return
    files = rec.get("recording_files", [])
    print(f"FILES for {target['topic']} ({target['start_time'][:10]}):",
          ", ".join(f.get("file_type", "?") for f in files))

    vtt = next((f for f in files if f.get("file_type") == "TRANSCRIPT"), None)
    if not vtt:
        print("TRANSCRIPT: none on this call (audio only — would need AAI)")
        return
    text = get(vtt["download_url"], tok, raw=True)
    if isinstance(text, dict):
        print("TRANSCRIPT fetch:", text["_err"])
    else:
        lines = [l for l in text.splitlines() if l and "-->" not in l and not l.isdigit()]
        print(f"TRANSCRIPT OK: {len(text)} chars, {len(lines)} caption lines")
        print("  first lines:", " / ".join(lines[1:4]))


if __name__ == "__main__":
    main()
