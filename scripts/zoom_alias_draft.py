#!/usr/bin/env python3
"""Draft the Zoom display-name -> member alias list. READ-ONLY: reads Supabase over
REST and the collected Zoom attendee names, writes one reviewable CSV locally.
Nothing is written to Supabase, Airtable, GroupOS or Zoom.

Confidence tiers
  exact      one member whose full name equals the Zoom name           -> auto-accept
  ambiguous  several members share that name                           -> human picks
  partial    unique first+last or unique prefix/nickname hit           -> human confirms
  none       no candidate (incl. single-word names, bots, guests)      -> leave unresolved
"""
import csv
import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict

ENV = "/Users/Born/mds-digest-web/.env.local"
SB_REST = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
SCRATCH = ("/private/tmp/claude-501/-Users-Born-Scorecard/"
           "30708aa2-83da-40a7-924d-34290bd41cb7/scratchpad")
NAMES = SCRATCH + "/zoom_attendee_names.json"
OUT = SCRATCH + "/zoom_alias_draft.csv"

BOT = re.compile(r"notetaker|circleback|fireflies|otter|fathom|timeless|companion|read\.ai"
                 r"|note taker|sembly|recorder|assistant|meeting buddy|\bai\b", re.I)
STAFF_HINT = re.compile(r"contact mds|discover mds|tomi mds|belen mds", re.I)


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("missing " + k)


def sb(path, params):
    key = env("SUPABASE_SECRET_KEY")
    url = SB_REST + path + "?" + params
    r = subprocess.run(["curl", "-sS", "--max-time", "120", url,
                        "-H", "apikey: " + key, "-H", "Authorization: Bearer " + key,
                        "-H", "Accept-Profile: digest"],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        sys.exit("supabase read failed: " + r.stdout[:200] + r.stderr[:200])


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return " ".join(s.split())


def main():
    members, offset = [], 0
    while True:
        page = sb("/member_attributes",
                  f"select=at_member_id,full_name,membership_status,country"
                  f"&limit=1000&offset={offset}")
        if not isinstance(page, list):
            sys.exit("unexpected: " + str(page)[:200])
        members += page
        if len(page) < 1000:
            break
        offset += 1000
    members = [m for m in members if m.get("full_name")]
    RANK = {"Current Member": 0, "New Member": 1, "Current Member- Not Renewing": 2,
            "Current Member- Paused ": 2, "Staff": 3, "Team User": 3}

    def prefer(cands):
        """Keep only the best-status candidates — a live member beats a removed applicant."""
        if not cands:
            return cands
        best = min(RANK.get(c.get("membership_status"), 9) for c in cands)
        return [c for c in cands if RANK.get(c.get("membership_status"), 9) == best]
    print(f"members loaded: {len(members)}")

    by_full, by_first_last, by_first = defaultdict(list), defaultdict(list), defaultdict(list)
    for m in members:
        f = fold(m["full_name"])
        if not f:
            continue
        by_full[f].append(m)
        parts = f.split()
        if len(parts) >= 2:
            by_first_last[(parts[0], parts[-1])].append(m)
        by_first[parts[0]].append(m)

    zoom = json.load(open(NAMES))
    print(f"zoom names: {len(zoom)}")

    rows = []
    for z in sorted(zoom, key=lambda r: -r["calls"]):
        name, calls = z["name"], z["calls"]
        f = fold(name)
        parts = f.split()
        kind, cands = "none", []

        if BOT.search(name) or STAFF_HINT.search(name):
            kind = "bot_or_host"
        elif f in by_full:
            cands = prefer(by_full[f])
            kind = "exact" if len(cands) == 1 else "ambiguous"
        elif len(parts) >= 2 and (parts[0], parts[-1]) in by_first_last:
            cands = prefer(by_first_last[(parts[0], parts[-1])])
            kind = "partial" if len(cands) == 1 else "ambiguous"
        elif len(parts) >= 2:
            pref = [m for m in members if fold(m["full_name"]).startswith(parts[0] + " ")
                    and parts[-1][:4] and parts[-1][:4] in fold(m["full_name"])]
            pref = prefer(pref)
            if len(pref) == 1:
                cands, kind = pref, "partial"
            elif len(pref) > 1:
                cands, kind = pref[:4], "ambiguous"
        elif len(parts) == 1 and parts[0] in by_first:
            cands = prefer(by_first[parts[0]])
            kind = "single_word_ambiguous" if len(cands) > 1 else "partial"

        best = cands[0] if len(cands) == 1 else None
        rows.append({
            "zoom_name": name,
            "calls": calls,
            "confidence": kind,
            "member_name": best["full_name"] if best else "",
            "at_member_id": best["at_member_id"] if best else "",
            "membership_status": best["membership_status"] if best else "",
            "candidates": " | ".join(f"{c['full_name']} [{c.get('membership_status') or '-'}]"
                                     for c in cands[:5]) if not best else "",
            "decision": "",
        })

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    tally = defaultdict(int)
    call_tally = defaultdict(int)
    for r in rows:
        tally[r["confidence"]] += 1
        call_tally[r["confidence"]] += r["calls"]
    print(f"\n{'tier':<24}{'names':>7}{'attendance rows':>18}")
    for k in sorted(tally, key=lambda x: -call_tally[x]):
        print(f"{k:<24}{tally[k]:>7}{call_tally[k]:>18}")
    auto = call_tally["exact"] + call_tally["partial"]
    total = sum(v for k, v in call_tally.items() if k != "bot_or_host")
    print(f"\nattendance rows auto-resolved: {auto}/{total} = {auto/total*100:.0f}% "
          f"(bots/host excluded)")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
