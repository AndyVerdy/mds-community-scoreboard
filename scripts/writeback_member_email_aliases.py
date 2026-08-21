#!/usr/bin/env python3
"""#100 — write approved aliases back to Airtable, then mirror them locally.

  python3 scripts/writeback_member_email_aliases.py review.csv [--dry-run]

Airtable's "Associated Emails (Admin)" on the Members DB is the SYSTEM OF RECORD.
digest.member_email_alias is its mirror, so Airtable is written first and re-read to
confirm the value persisted before anything is written locally. Any failure stops the
run — a half-written alias set is worse than none.

Format: every one of the 8 pre-existing values holds a single address, so there is no
multi-value precedent in the data. New addresses are appended on their own line.
"""
import argparse, csv, json, subprocess, sys, time

ENV = "/Users/Born/mds-digest-web/.env.local"
FIELD = "Associated Emails (Admin)"
SEPARATOR = "\n"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


SUPA = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
SKEY = env("SUPABASE_SECRET_KEY")
ATPAT = env("AIRTABLE_PAT")

# NOT the env's AIRTABLE_BASE_ID / AIRTABLE_MEMBERS_TABLE_ID — those point at the
# "MDS WhatsApp DB" base (appT9TVZWhv7io4CN). The Members DB is a different base, and
# "Associated Emails (Admin)" lives on its Members table, confirmed via the meta API.
BASE_ID = "appou5JVr0WIrioWS"      # MDS Member Database
TABLE_ID = "tblfwOSROSHfuYUxv"     # Members (796 fields)


def curl(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    if not out.strip():
        return {}
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"request failed: {out[:400]}")


def at_get(rec):
    r = curl(["curl", "-s", "-m", "60",
              f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}/{rec}",
              "-H", f"Authorization: Bearer {ATPAT}"])
    if "error" in r:
        sys.exit(f"STOP: reading {rec} failed: {r['error']}")
    return r.get("fields", {}).get(FIELD, "") or ""


def at_patch(rec, value):
    r = curl(["curl", "-s", "-m", "60", "-X", "PATCH",
              f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}/{rec}",
              "-H", f"Authorization: Bearer {ATPAT}",
              "-H", "Content-Type: application/json",
              "--data-binary", json.dumps({"fields": {FIELD: value}})])
    if "error" in r:
        sys.exit(f"STOP: patching {rec} failed: {r['error']}")
    return r


def supa_insert(rows):
    curl(["curl", "-s", "-m", "120", "-X", "POST", f"{SUPA}/member_email_alias",
          "-H", f"Authorization: Bearer {SKEY}", "-H", f"apikey: {SKEY}",
          "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
          "-H", "Content-Type: application/json", "-H", "Prefer: return=minimal",
          "--data-binary", json.dumps(rows)])


ap = argparse.ArgumentParser()
ap.add_argument("review_csv")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

approved = [r for r in csv.DictReader(open(args.review_csv))
            if (r.get("approve") or "").strip().lower() in ("y", "yes", "true", "1")]
if not approved:
    sys.exit("no rows marked approve=yes — nothing to do")

print(f"base {BASE_ID} table {TABLE_ID} · {len(approved)} approved rows\n")

done = []
for r in approved:
    rec = r["target_at_member_id"]
    addr = r["alias_email"].strip().lower()
    cur = at_get(rec)
    if addr in cur.lower():
        print(f"  = {r['target_name']:24s} {addr}  already present")
        done.append({"at_member_id": rec, "email": addr, "source": "name_match_approved"})
        continue
    new = (cur.rstrip() + SEPARATOR + addr) if cur.strip() else addr
    print(f"  {'DRY ' if args.dry_run else '+ '}{r['target_name']:24s} {addr}")
    print(f"        before {cur!r}")
    print(f"        after  {new!r}")
    if args.dry_run:
        continue
    at_patch(rec, new)
    time.sleep(0.25)                       # Airtable allows 5 requests/second per base
    back = at_get(rec)
    if addr not in back.lower():
        sys.exit(f"STOP: {rec} did not persist {addr}; field is now {back!r}")
    done.append({"at_member_id": rec, "email": addr, "source": "name_match_approved"})

if args.dry_run:
    print("\ndry run — nothing written")
else:
    supa_insert(done)
    print(f"\nwrote {len(done)} aliases to Airtable and mirrored them locally")
