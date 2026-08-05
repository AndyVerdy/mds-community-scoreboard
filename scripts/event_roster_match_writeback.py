#!/usr/bin/env python3
"""#48 — write the member<->ticket links the WAREHOUSE proved back into Airtable's Event Roster.

Airtable's own matcher left `Match to Member` blank on thousands of roster rows; #45's second
pass (`stamp_event_registrations()`) recovered the links from different-email buyers and no-email
orders, and today they live ONLY in the warehouse. This closes that gap at the source, so the
team's operative view stops lagging what we know.

THE TWO RULES THIS SCRIPT EXISTS TO KEEP:
  1. BLANKS ONLY. A row that already carries a link is never touched — not re-linked, not
     re-ordered, not "corrected". Airtable is the team's working surface and their link wins.
  2. GENUINE NON-MEMBERS STAY BLANK. No member in the warehouse = nothing written. The
     evidenced guests/partners/public buyers are the expected remainder, not a failure.

Every link target is validated against the live Members table BEFORE anything is written, because
a single bad record id fails its whole PATCH batch and would leave the run half-applied.

  --dry-run   (DEFAULT) read everything, write nothing, print the plan
  --apply     perform the writes
  --limit N   write at most N rows (used for the spot-check batch)
Python 3.9-safe, stdlib only.
"""
import argparse
import json
import subprocess
import sys
import time

ENV = "/Users/Born/mds-digest-web/.env.local"
AT_BASE = "appou5JVr0WIrioWS"
T_ROSTER = "tblfTLRfAqBhBZlc4"
T_MEMBERS = "tblfwOSROSHfuYUxv"
F_MATCH = "Match to Member"
SB_REST = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("missing " + k)


def curl(args, tries=4):
    """AT throttles at 5 req/s and answers 429; retry with backoff rather than losing a batch."""
    for attempt in range(tries):
        r = subprocess.run(["curl", "-sS", "--max-time", "120"] + args,
                           capture_output=True, text=True)
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"error": {"type": "unparseable", "message": r.stdout[:200]}}
        err = out.get("error") if isinstance(out, dict) else None
        if err and str(err.get("type", "")).lower() in ("request_rate_too_high", "unparseable"):
            time.sleep(1.0 + attempt)
            continue
        return out
    return out


def at_list(pat, table, fields):
    """Page a whole table. `fields` empty = ids only (Airtable still returns the record id)."""
    rows, offset = [], None
    while True:
        url = "https://api.airtable.com/v0/%s/%s?pageSize=100" % (AT_BASE, table)
        for f in fields:
            url += "&fields%5B%5D=" + f.replace(" ", "%20")
        if offset:
            url += "&offset=" + offset
        d = curl([url, "-H", "Authorization: Bearer " + pat])
        if "records" not in d:
            sys.exit("Airtable read failed: " + str(d)[:300])
        rows.extend(d["records"])
        offset = d.get("offset")
        if not offset:
            return rows
        time.sleep(0.22)


def warehouse_pairs(key):
    """roster_record_id -> member_at_id, paged (PostgREST caps a response at 1000 rows)."""
    pairs, offset = {}, 0
    while True:
        url = (SB_REST + "/event_registrations?select=roster_record_id,member_at_id"
               "&member_at_id=not.is.null&limit=1000&offset=%d" % offset)
        d = curl([url, "-H", "apikey: " + key, "-H", "Authorization: Bearer " + key,
                  "-H", "Accept-Profile: digest"])
        if not isinstance(d, list):
            sys.exit("Supabase read failed: " + str(d)[:300])
        for row in d:
            if row.get("roster_record_id") and row.get("member_at_id"):
                pairs[row["roster_record_id"]] = row["member_at_id"]
        if len(d) < 1000:
            return pairs
        offset += 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="perform the writes")
    ap.add_argument("--limit", type=int, default=0, help="write at most N rows")
    args = ap.parse_args()

    pat = env("AIRTABLE_PAT")
    sbkey = env("SUPABASE_SECRET_KEY")

    print("reading Airtable Event Roster…")
    roster = at_list(pat, T_ROSTER, [F_MATCH])
    print("reading Airtable Members (link-target validation)…")
    member_ids = set(r["id"] for r in at_list(pat, T_MEMBERS, []))
    print("reading the warehouse…")
    pairs = warehouse_pairs(sbkey)

    linked = [r for r in roster if (r.get("fields") or {}).get(F_MATCH)]
    blank = [r for r in roster if not (r.get("fields") or {}).get(F_MATCH)]

    to_write, no_member, bad_target = [], 0, []
    for r in blank:
        mid = pairs.get(r["id"])
        if not mid:
            no_member += 1
        elif mid not in member_ids:
            bad_target.append((r["id"], mid))
        else:
            to_write.append((r["id"], mid))

    print("")
    print("roster rows            : %d" % len(roster))
    print("  already linked (skip): %d" % len(linked))
    print("  blank                : %d" % len(blank))
    print("    -> writable        : %d" % len(to_write))
    print("    -> no member       : %d   (evidenced non-members: guests, partners, public buyers)"
          % no_member)
    print("    -> stale target    : %d   (warehouse member id no longer in the Members table)"
          % len(bad_target))
    if bad_target:
        print("       e.g. " + ", ".join("%s->%s" % p for p in bad_target[:5]))
    print("members in AT          : %d" % len(member_ids))

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply (optionally --limit N).")
        for rid, mid in to_write[:5]:
            print("  would set %s  Match to Member = [%s]" % (rid, mid))
        return

    batch = to_write[:args.limit] if args.limit else to_write
    print("\nAPPLYING to %d rows…" % len(batch))
    # Every applied link is appended to an audit log: the spot-check needs to know exactly which
    # rows THIS script touched, and after the write they are indistinguishable from AT's own.
    audit = open("scripts/event_roster_writeback_applied.log", "a")
    written, failed = 0, []
    for i in range(0, len(batch), 10):
        chunk = batch[i:i + 10]
        body = {"records": [{"id": rid, "fields": {F_MATCH: [mid]}} for rid, mid in chunk],
                "typecast": False}
        d = curl(["-X", "PATCH", "https://api.airtable.com/v0/%s/%s" % (AT_BASE, T_ROSTER),
                  "-H", "Authorization: Bearer " + pat, "-H", "Content-Type: application/json",
                  "--data-binary", json.dumps(body)])
        if "records" in d:
            written += len(d["records"])
            for rid, mid in chunk:
                audit.write("%s\t%s\n" % (rid, mid))
            audit.flush()
        else:
            failed.append((chunk[0][0], str(d)[:160]))
        if (i // 10) % 20 == 0:
            print("  %d/%d" % (written, len(batch)))
        time.sleep(0.3)

    print("\nwritten: %d   failed batches: %d" % (written, len(failed)))
    for rid, msg in failed[:5]:
        print("  FAIL at %s: %s" % (rid, msg))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
