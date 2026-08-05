#!/usr/bin/env python3
"""Delete the 11 provably-junk rows from the WA DB Members table (appT9TVZWhv7io4CN /
tbli8B589iNbsGF0Z). Andy authorised removal of data I am sure is bad, 2026-08-05.

WHAT QUALIFIES (all four had to hold, checked live before the list was frozen):
  1. The row is in NO MDS chat — verified against all 55 Whapi groups / 702 participants.
  2. The phone value CANNOT be a phone number — 14+ digits, or not digits at all ('sam'),
     or Twilio's documented test number 15005550006.
  3. match_status = no_match, so nothing resolved to a member through it.
  4. ZERO record links on the row — nothing in Airtable points at it.

DELIBERATELY NOT INCLUDED, though they are also orphaned:
  · every real-shaped number (8-13 digits), including 2345068970128 — Nigeria's +234 makes it
    plausible, and a wrong delete of a real person costs far more than a leftover row.
  · the 16 orphans with match_status = matched — real members who left the chats. Clearing them
    would break the Scorecard join, which keys on source_member_id.

REVERSIBLE: every field of every row is in scripts/wa_db_deleted_rows_2026-08-05.json, written
before this list was frozen. Re-creating them is a POST of that file's `fields` objects.
(Record IDs would change; nothing links to these rows, so nothing depends on the old ids.)

Run:  python3 scripts/wa_db_delete_junk_rows.py --apply     (omit --apply for a dry run)
"""
import argparse
import json
import subprocess
import sys
import time

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE = "appT9TVZWhv7io4CN"
TABLE = "tbli8B589iNbsGF0Z"
BACKUP = "scripts/wa_db_deleted_rows_2026-08-05.json"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("missing " + k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    pat = env("AIRTABLE_PAT")

    rows = json.load(open(BACKUP))
    print("rows queued for deletion: %d\n" % len(rows))
    for r in rows:
        f = r.get("fields") or {}
        print("  %-18s %s  %s  msgs30=%s" % (str(f.get("phone"))[:17], r["id"],
                                             f.get("match_status"), f.get("msgs_30d", 0)))

    if not args.apply:
        print("\nDRY RUN — nothing deleted. Re-run with --apply.")
        return

    # Re-verify inertness at delete time: a link could have appeared since the list was frozen.
    for r in rows:
        cur = json.loads(subprocess.run(
            ["curl", "-sS", "-m", "60", "https://api.airtable.com/v0/%s/%s/%s" % (BASE, TABLE, r["id"]),
             "-H", "Authorization: Bearer " + pat], capture_output=True, text=True).stdout)
        f = cur.get("fields") or {}
        if "id" not in cur:
            print("  already gone: %s" % r["id"])
            continue
        links = [k for k, v in f.items() if isinstance(v, list) and v and str(v[0]).startswith("rec")]
        if links:
            sys.exit("ABORT — %s now has links %s. Re-audit before deleting." % (r["id"], links))
        if f.get("match_status") != "no_match":
            sys.exit("ABORT — %s is now '%s', not no_match." % (r["id"], f.get("match_status")))
        time.sleep(0.12)
    print("\nre-verified inert: no links, all still no_match")

    ids = [r["id"] for r in rows]
    deleted = []
    for i in range(0, len(ids), 10):
        chunk = ids[i:i + 10]
        url = ("https://api.airtable.com/v0/%s/%s?" % (BASE, TABLE)
               + "&".join("records[]=" + x for x in chunk))
        d = json.loads(subprocess.run(["curl", "-sS", "-m", "120", "-X", "DELETE", url,
                                       "-H", "Authorization: Bearer " + pat],
                                      capture_output=True, text=True).stdout)
        if "records" in d:
            deleted += [x["id"] for x in d["records"] if x.get("deleted")]
        else:
            print("  FAILED batch: %s" % str(d)[:200])
        time.sleep(0.3)

    still = []
    for x in ids:
        d = json.loads(subprocess.run(["curl", "-sS", "-m", "60",
                                       "https://api.airtable.com/v0/%s/%s/%s" % (BASE, TABLE, x),
                                       "-H", "Authorization: Bearer " + pat],
                                      capture_output=True, text=True).stdout)
        if "id" in d:
            still.append(x)
        time.sleep(0.1)
    print("\ndeleted: %d   still present: %d %s" % (len(deleted), len(still), still or ""))
    sys.exit(1 if still else 0)


if __name__ == "__main__":
    main()
