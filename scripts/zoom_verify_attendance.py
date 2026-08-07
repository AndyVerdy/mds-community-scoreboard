#!/usr/bin/env python3
"""Verification only — no writes anywhere.

Cross-checks the Zoom report API against the attendee lists collected earlier from
the Zoom MCP (mogul_attendees.json), per call: unique people after bot/host removal,
plus how much identity the API adds (emails, per-person duration).
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from zoom_probe import CTX
from zoom_attendance_horizon import token

SCRATCH = ("/private/tmp/claude-501/-Users-Born-Scorecard/"
           "30708aa2-83da-40a7-924d-34290bd41cb7/scratchpad")
MCP_LISTS = os.path.join(SCRATCH, "mogul_attendees.json")
UUID_MAP = os.path.join(SCRATCH, "mogul_meetings.tsv")

BOT = re.compile(r"notetaker|circleback|fireflies|otter|fathom|timeless|companion|read\.ai",
                 re.I)
HOST = re.compile(r"^(contact mds|discover mds|tomi mds|belen mds)$|\(contact mds\)", re.I)


def clean(names):
    out = set()
    for n in names:
        n = " ".join(n.split())
        if n and not BOT.search(n) and not HOST.search(n):
            out.add(n.lower())
    return out


def get(url, tok, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_err": f"{e.code} {e.read().decode()[:120]}"}


def api_participants(tok, uuid):
    enc = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
    rows, npt, guard = [], "", 0
    while guard < 10:
        params = {"page_size": 300}
        if npt:
            params["next_page_token"] = npt
        d = get(f"https://api.zoom.us/v2/report/meetings/{enc}/participants", tok, params)
        if "_err" in d:
            return None, d["_err"]
        rows += d.get("participants", [])
        npt = d.get("next_page_token") or ""
        if not npt:
            break
        guard += 1
    return rows, None


def main():
    tok = token()
    mcp = json.load(open(MCP_LISTS))
    uuids = {}
    for line in open(UUID_MAP):
        date, mid, uuid, topic = line.rstrip("\n").split("\t")
        uuids[date] = uuid

    print(f"{'date':<11} {'MCP':>5} {'API':>5} {'API-only':>8} {'MCP-only':>8} "
          f"{'emails':>7}  topic")
    tot_m = tot_a = tot_mail = 0
    for call in mcp:
        iso = call["date"]
        uuid = uuids.get(iso)
        if not uuid:
            print(f"{iso:<11} {'-':>5} {'-':>5} {'':>8} {'':>8} {'':>7}  (no uuid on file)")
            continue
        rows, err = api_participants(tok, uuid)
        if err:
            print(f"{iso:<11} {len(clean(call['attendees'])):>5} {'ERR':>5}  {err}")
            continue
        api_names = clean(p.get("name", "") for p in rows)
        mcp_names = clean(call["attendees"])
        emails = {(p.get("user_email") or "").lower() for p in rows} - {""}
        tot_m += len(mcp_names)
        tot_a += len(api_names)
        tot_mail += len(emails)
        print(f"{iso:<11} {len(mcp_names):>5} {len(api_names):>5} "
              f"{len(api_names - mcp_names):>8} {len(mcp_names - api_names):>8} "
              f"{len(emails):>7}  {call['topic'][:38]}")
    print(f"{'TOTAL':<11} {tot_m:>5} {tot_a:>5} {'':>8} {'':>8} {tot_mail:>7}")


if __name__ == "__main__":
    main()
