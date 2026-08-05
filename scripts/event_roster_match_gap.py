#!/usr/bin/env python3
"""#48 part ② — SIZE the Airtable-side matcher gap before touching the live Make scenario.

Make scenario 4270329 ("Event Roster Match to Member") links a new roster row to a member with a
single Airtable search:  {{1.Email}} = {Preferred Email}
So a member who bought with any OTHER address never links at capture, and the row sits blank
until someone backfills it — which is exactly the debt #48's part ① just paid off.

This script asks the honest question rather than assuming the answer: of the links the warehouse
recovered and we just wrote back, HOW MANY would that formula have caught on its own? The
remainder is the gap, broken down by which member email field would have caught it.

Read-only. Nothing is written anywhere.
"""
import json
import subprocess
import sys
import time

ENV = "/Users/Born/mds-digest-web/.env.local"
AT_BASE = "appou5JVr0WIrioWS"
T_ROSTER = "tblfTLRfAqBhBZlc4"
T_MEMBERS = "tblfwOSROSHfuYUxv"
APPLIED = "scripts/event_roster_writeback_applied.log"
SB_REST = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"

F_PREFERRED = "Preferred Email"
F_STRIPE = "Stripe Customer Email"
F_ASSOC = "Associated Emails (Admin)"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("missing " + k)


def curl(args, tries=4):
    for attempt in range(tries):
        r = subprocess.run(["curl", "-sS", "--max-time", "120"] + args,
                           capture_output=True, text=True)
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"error": {"type": "unparseable"}}
        err = out.get("error") if isinstance(out, dict) else None
        if err and str(err.get("type", "")).lower() in ("request_rate_too_high", "unparseable"):
            time.sleep(1.0 + attempt)
            continue
        return out
    return out


def at_list(pat, table, fields):
    rows, offset = [], None
    while True:
        url = "https://api.airtable.com/v0/%s/%s?pageSize=100" % (AT_BASE, table)
        for f in fields:
            url += "&fields%5B%5D=" + f.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
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


def reg_emails(key):
    """roster_record_id -> the email the ORDER carried (what the Make trigger hands the search)."""
    out, offset = {}, 0
    while True:
        url = (SB_REST + "/event_registrations?select=roster_record_id,email"
               "&email=not.is.null&limit=1000&offset=%d" % offset)
        d = curl([url, "-H", "apikey: " + key, "-H", "Authorization: Bearer " + key,
                  "-H", "Accept-Profile: digest"])
        if not isinstance(d, list):
            sys.exit("Supabase read failed: " + str(d)[:300])
        for row in d:
            if row.get("roster_record_id") and row.get("email"):
                out[row["roster_record_id"]] = row["email"].strip().lower()
        if len(d) < 1000:
            return out
        offset += 1000


def main():
    pat, sbkey = env("AIRTABLE_PAT"), env("SUPABASE_SECRET_KEY")

    applied = []
    for line in open(APPLIED):
        parts = line.strip().split("\t")
        if len(parts) == 2:
            applied.append((parts[0], parts[1]))
    print("links written by #48 part ①: %d" % len(applied))

    print("reading Members emails…")
    members = {}
    for r in at_list(pat, T_MEMBERS, [F_PREFERRED, F_STRIPE, F_ASSOC]):
        f = r.get("fields") or {}
        members[r["id"]] = {
            "pref": (f.get(F_PREFERRED) or "").strip().lower(),
            "stripe": (f.get(F_STRIPE) or "").strip().lower(),
            "assoc": (f.get(F_ASSOC) or "").lower(),
        }
    print("reading order emails…")
    order_email = reg_emails(sbkey)

    caught_pref = caught_stripe = caught_assoc = no_email = uncatchable = 0
    for rid, mid in applied:
        em = order_email.get(rid)
        m = members.get(mid)
        if not em:
            no_email += 1
        elif not m:
            uncatchable += 1
        elif em == m["pref"]:
            caught_pref += 1
        elif em and em == m["stripe"]:
            caught_stripe += 1
        elif em and em in m["assoc"]:
            caught_assoc += 1
        else:
            uncatchable += 1

    total = len(applied)
    print("")
    print("Would the LIVE formula ({Preferred Email} only) have caught these at capture?")
    print("  YES — Preferred Email           : %5d  (%.1f%%)" % (caught_pref, 100.0 * caught_pref / max(total, 1)))
    print("  no  — Stripe Customer Email     : %5d" % caught_stripe)
    print("  no  — Associated Emails (Admin) : %5d" % caught_assoc)
    print("  no  — order carried NO email    : %5d  (name-matched by the warehouse only)" % no_email)
    print("  no  — no email field matches    : %5d  (different address entirely)" % uncatchable)
    gap = total - caught_pref
    print("")
    print("GAP: %d of %d (%.1f%%) could not link at capture today." % (gap, total, 100.0 * gap / max(total, 1)))
    print("Adding Stripe + Associated to the search would close %d of them (%.1f%% of the gap)."
          % (caught_stripe + caught_assoc, 100.0 * (caught_stripe + caught_assoc) / max(gap, 1)))
    print("The rest need a non-email signal — they are the name-matched and different-address rows,")
    print("which is warehouse work, not a formula change.")


if __name__ == "__main__":
    main()
