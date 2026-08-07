#!/usr/bin/env python3
"""Read-only: exact map of Zoom recordings -> GroupOS videos.

GroupOS stores the original Zoom filename in video_url, e.g.
    uploads/content-archive/videos/1786034085413-GMT20260805-160238_Recording_1920x1080.mp4
`GMT<YYYYMMDD>-<HHMMSS>` is the Zoom recording_start in UTC, so the join is exact —
no title or duration guessing. Falls back to a +/-3 min window for re-encodes.
"""
import glob
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

from zoom_probe import CTX
from zoom_attendance_horizon import token

TR = ("/Users/Born/.claude/projects/-Users-Born-Scorecard/"
      "30708aa2-83da-40a7-924d-34290bd41cb7/tool-results/")
OUT = ("/private/tmp/claude-501/-Users-Born-Scorecard/"
       "30708aa2-83da-40a7-924d-34290bd41cb7/scratchpad/zoom_groupos_map.json")

GMT = re.compile(r"GMT(\d{8})-(\d{6})")
MEMBER = re.compile(r"mogul|expert call|channel call|chapter .*call|wmds|large catalog"
                    r"|advisory council|resellers", re.I)
INTERNAL = re.compile(r"huddle|l-10|all-team|leadership|check-in|moderator|1:1|sync", re.I)


def load_videos():
    out, seen = [], set()
    for path in sorted(glob.glob(TR + "mcp-b64230e2-*-videos_list-*.txt")):
        try:
            d = json.load(open(path))
        except Exception:
            continue
        for v in d.get("items", []):
            if v["id"] in seen:
                continue
            seen.add(v["id"])
            m = GMT.search(v.get("video_url") or "")
            v["_stamp"] = (datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
                           if m else None)
            out.append(v)
    return out


def zoom_recordings():
    tok = token()
    out = []
    for m in range(1, 9):
        last = date(2026, m + 1, 1) - timedelta(days=1)
        url = ("https://api.zoom.us/v2/accounts/me/recordings?"
               + urllib.parse.urlencode({"from": f"2026-{m:02d}-01",
                                         "to": last.isoformat(), "page_size": 300}))
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            d = json.loads(r.read())
        for mt in d.get("meetings", []):
            files = mt.get("recording_files", [])
            starts = {f.get("recording_start") for f in files if f.get("recording_start")}
            types = {f.get("file_type") for f in files}
            topic = mt.get("topic", "")
            out.append({"date": mt["start_time"][:10], "uuid": mt["uuid"],
                        "topic": topic, "duration_min": mt.get("duration"),
                        "transcript": "TRANSCRIPT" in types,
                        "member": bool(MEMBER.search(topic)) and not INTERNAL.search(topic),
                        "_stamps": [datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") for s in starts]})
    return sorted(out, key=lambda c: c["date"])


def main():
    calls, videos = zoom_recordings(), load_videos()
    member = [c for c in calls if c["member"]]
    stamped = [v for v in videos if v["_stamp"]]
    print(f"Zoom 2026 recorded calls           : {len(calls)}  ({len(member)} member-facing)")
    print(f"GroupOS 2026 videos                : {len(videos)}  ({len(stamped)} carry a Zoom filename)\n")

    used, rows = set(), []
    for c in calls:
        hit, how = None, None
        for v in stamped:
            if v["id"] in used:
                continue
            for s in c["_stamps"]:
                delta = abs((v["_stamp"] - s).total_seconds())
                if delta == 0:
                    hit, how = v, "exact"
                    break
                if delta <= 180 and not hit:
                    hit, how = v, "±3min"
            if how == "exact":
                break
        if hit:
            used.add(hit["id"])
        rows.append({"date": c["date"], "topic": c["topic"], "uuid": c["uuid"],
                     "member": c["member"], "transcript": c["transcript"],
                     "video_id": hit["id"] if hit else None,
                     "video_title": hit.get("title") if hit else None,
                     "match": how})

    mm = [r for r in rows if r["member"]]
    hit_m = [r for r in mm if r["video_id"]]
    print(f"MEMBER-FACING CALLS MAPPED: {len(hit_m)}/{len(mm)} = {len(hit_m)/len(mm)*100:.0f}%")
    print(f"  exact filename match: {sum(1 for r in hit_m if r['match']=='exact')}")
    print(f"  within 3 min        : {sum(1 for r in hit_m if r['match']=='±3min')}")
    with_t = [r for r in hit_m if r["transcript"]]
    print(f"  of those, with a Zoom transcript ready to attach: {len(with_t)}\n")

    print("UNMAPPED MEMBER CALLS (no GroupOS video found):")
    for r in mm:
        if not r["video_id"]:
            print(f"   {r['date']}  {r['topic'][:62]}")

    left = [v for v in stamped if v["id"] not in used]
    print(f"\nGroupOS videos with a Zoom filename but no 2026 call matched: {len(left)}")
    for v in left[:8]:
        print(f"   {v['_stamp']:%Y-%m-%d %H:%M}  {v.get('title','')[:60]}")
    print(f"GroupOS videos with no Zoom filename at all (uploaded elsewhere): "
          f"{len(videos) - len(stamped)}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rows, open(OUT, "w"), indent=1)
    print(f"\nmapping -> {OUT}")


if __name__ == "__main__":
    main()
