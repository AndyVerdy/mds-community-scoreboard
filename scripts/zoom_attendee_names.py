#!/usr/bin/env python3
"""Read-only: collect distinct attendee identities across the last 12 months of
member-facing calls, so the name->member match rate can be measured.

Writes one JSON to the scratchpad. Prints counts only.
"""
import json
import os
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

from zoom_probe import CTX
from zoom_attendance_horizon import token

OUT = ("/private/tmp/claude-501/-Users-Born-Scorecard/"
       "30708aa2-83da-40a7-924d-34290bd41cb7/scratchpad/zoom_attendee_names.json")

MEMBER = re.compile(r"mogul|expert call|channel call|chapter .*call|wmds|large catalog"
                    r"|advisory council|resellers", re.I)
INTERNAL = re.compile(r"huddle|l-10|all-team|leadership|check-in|moderator|1:1|sync", re.I)
BOT = re.compile(r"notetaker|circleback|fireflies|otter|fathom|timeless|companion|read\.ai",
                 re.I)


def api(url, tok, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_err": e.code}


def main():
    tok = token()
    today = date(2026, 8, 6)
    calls = []
    for back in range(13):
        y, m = divmod((today.year * 12 + today.month - 1) - back, 12)
        m += 1
        last = (date(y, m + 1, 1) - timedelta(days=1)) if m < 12 else date(y, 12, 31)
        d = api("https://api.zoom.us/v2/accounts/me/recordings", tok,
                {"from": f"{y}-{m:02d}-01", "to": last.isoformat(), "page_size": 300})
        for mt in d.get("meetings", []):
            t = mt.get("topic", "")
            if MEMBER.search(t) and not INTERNAL.search(t):
                calls.append((mt["start_time"][:10], mt["uuid"], t))

    people = defaultdict(lambda: {"calls": 0, "emails": set(), "uuids": set()})
    ok = 0
    for d8, uuid, topic in calls:
        enc = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
        rep = api(f"https://api.zoom.us/v2/report/meetings/{enc}/participants", tok,
                  {"page_size": 300})
        if "_err" in rep:
            continue
        ok += 1
        seen = set()
        for p in rep.get("participants", []):
            name = " ".join((p.get("name") or "").split())
            if not name or BOT.search(name):
                continue
            key = name.lower()
            if key not in seen:
                seen.add(key)
                people[key]["calls"] += 1
            people[key]["name"] = name
            if p.get("user_email"):
                people[key]["emails"].add(p["user_email"].lower())
            if p.get("participant_uuid"):
                people[key]["uuids"].add(p["participant_uuid"])

    rows = [{"name": v["name"], "calls": v["calls"], "emails": sorted(v["emails"]),
             "n_uuids": len(v["uuids"])} for v in people.values()]
    rows.sort(key=lambda r: -r["calls"])
    with_mail = [r for r in rows if r["emails"]]
    print(f"member-facing calls found : {len(calls)}")
    print(f"calls with attendance data: {ok}")
    print(f"distinct attendee names   : {len(rows)}")
    print(f"names carrying an email   : {len(with_mail)} "
          f"({len(with_mail)/max(len(rows),1)*100:.1f}%)")
    print(f"names with a stable participant_uuid: "
          f"{sum(1 for r in rows if r['n_uuids'])}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rows, open(OUT, "w"), indent=1)
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
