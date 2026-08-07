#!/usr/bin/env python3
"""Read-only inventory of the whole Zoom history: how far back calls, recordings,
transcripts, videos and attendance actually reach. Writes nothing anywhere.

Sweeps /accounts/me/recordings one month at a time (Zoom caps the range at 1 month),
tallies member-facing calls, then probes attendance per month to find the real cutoff.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date

from zoom_probe import CTX
from zoom_attendance_horizon import token

MEMBER = re.compile(r"mogul|expert call|channel call|chapter .*call|wmds|large catalog"
                    r"|advisory council|resellers", re.I)
START = date(2021, 1, 1)
END = date(2026, 8, 6)


def get(url, tok, params=None, method="GET"):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok},
                                 method=method)
    try:
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            if method == "HEAD":
                return {"_status": r.status, "_len": r.headers.get("Content-Length")}
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_err": f"{e.code}", "_msg": e.read().decode()[:100]}


def months(a, b):
    y, m = a.year, a.month
    while (y, m) <= (b.year, b.month):
        first = date(y, m, 1)
        last = date(y + (m == 12), (m % 12) + 1, 1)
        yield first.isoformat(), (last.toordinal() - 1 and date.fromordinal(last.toordinal() - 1)).isoformat()
        y, m = y + (m == 12), (m % 12) + 1


def main():
    tok = token()

    users = get("https://api.zoom.us/v2/users", tok, {"page_size": 30})
    hosts = {u["id"]: u["email"] for u in users.get("users", [])}

    per_year = defaultdict(lambda: defaultdict(int))
    member_calls = []  # (date, uuid, topic, host_id, has_transcript, has_mp4)
    for frm, to in months(START, END):
        d = get("https://api.zoom.us/v2/accounts/me/recordings", tok,
                {"from": frm, "to": to, "page_size": 300})
        if "_err" in d:
            per_year[frm[:4]]["api_errors"] += 1
            continue
        y = frm[:4]
        for m in d.get("meetings", []):
            types = {f.get("file_type") for f in m.get("recording_files", [])}
            per_year[y]["recorded_calls"] += 1
            if "TRANSCRIPT" in types:
                per_year[y]["with_transcript"] += 1
            if "MP4" in types:
                per_year[y]["with_video"] += 1
            if MEMBER.search(m.get("topic", "")):
                per_year[y]["member_facing"] += 1
                if "TRANSCRIPT" in types:
                    per_year[y]["member_with_transcript"] += 1
                member_calls.append((m["start_time"][:10], m["uuid"], m["topic"],
                                     m.get("host_id"), "TRANSCRIPT" in types,
                                     "MP4" in types))

    print("=== RECORDINGS / TRANSCRIPTS / VIDEO, by year ===")
    print(f"{'year':<6}{'recorded':>9}{'member':>8}{'video':>7}{'transcript':>11}{'member+transcript':>19}")
    for y in sorted(per_year):
        r = per_year[y]
        print(f"{y:<6}{r['recorded_calls']:>9}{r['member_facing']:>8}{r['with_video']:>7}"
              f"{r['with_transcript']:>11}{r['member_with_transcript']:>19}")

    print("\n=== HOSTS of member-facing calls ===")
    hc = defaultdict(int)
    for _, _, _, hid, _, _ in member_calls:
        hc[hosts.get(hid, hid or "?")] += 1
    for h, n in sorted(hc.items(), key=lambda x: -x[1]):
        print(f"  {n:>4}  {h}")

    print("\n=== ATTENDANCE availability, one member call sampled per quarter ===")
    by_q = {}
    for d8, uuid, topic, _, _, _ in sorted(member_calls):
        q = f"{d8[:4]}Q{(int(d8[5:7]) - 1) // 3 + 1}"
        by_q.setdefault(q, (d8, uuid, topic))
    for q in sorted(by_q):
        d8, uuid, topic = by_q[q]
        enc = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
        rep = get(f"https://api.zoom.us/v2/report/meetings/{enc}/participants", tok,
                  {"page_size": 300})
        status = rep.get("_msg", "").strip()[:44] if "_err" in rep else f"{rep.get('total_records')} rows"
        print(f"  {q}  {d8}  {status:<46} {topic[:34]}")

    if member_calls:
        newest = sorted(member_calls)[-1]
        enc = urllib.parse.quote(urllib.parse.quote(newest[1], safe=""), safe="")
        rec = get(f"https://api.zoom.us/v2/meetings/{enc}/recordings", tok)
        mp4 = next((f for f in rec.get("recording_files", [])
                    if f.get("file_type") == "MP4"), None)
        if mp4:
            h = get(mp4["download_url"], tok, method="HEAD")
            size = h.get("_len")
            print(f"\n=== VIDEO ACCESS ===\n  HEAD on {newest[0]} MP4 -> HTTP {h.get('_status', h.get('_err'))}"
                  f", {int(size)/1e6:.0f} MB" if size else f"\n  HEAD -> {h}")


if __name__ == "__main__":
    main()
