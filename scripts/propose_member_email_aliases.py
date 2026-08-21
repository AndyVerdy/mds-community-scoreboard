#!/usr/bin/env python3
"""#100 — propose email aliases by name match. GRANTS NOTHING.

  python3 scripts/propose_member_email_aliases.py mds_video_audience_pairs.csv --out review.csv

Takes a GroupOS audience export, keeps only rows with a REAL match (a panel_only row is an
admin-panel phantom that grants nothing in the app), and finds the addresses that do not
reach an ACTIVE member today. Two ways that happens:

  unresolved        no member record carries the address at all
  dormant           the address resolves, but to a duplicate record whose membership
                    status is NULL — resolution succeeds and access still fails

For each, it looks for exactly one ACTIVE member with the same folded full name and writes
a proposal row. Proposing an alias against the ACTIVE record is the whole point: writing it
against the dormant twin would resolve and still be denied.

'andy test' matches a real member record. That is why this writes a CSV and never a row.
"""
import argparse, csv, json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
ACTIVE = ("Current Member", "New Member", "Current Member- Not Renewing",
          "Staff", "Pending Group Entrance")


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def get_all(table, select, order):
    rows, offset = [], 0
    while True:
        cmd = ["curl", "-s", "-m", "120",
               f"{BASE}/{table}?select={select}&order={order}&limit=1000&offset={offset}",
               "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
               "-H", "Accept-Profile: digest"]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            page = json.loads(out)
        except Exception:
            sys.exit(f"GET {table} failed: {out[:300]}")
        if not isinstance(page, list):
            sys.exit(f"GET {table} error: {str(page)[:300]}")
        rows += page
        if len(page) < 1000:
            return rows
        offset += 1000


def fold(s):
    return " ".join((s or "").lower().split())


ap = argparse.ArgumentParser()
ap.add_argument("pairs_csv")
ap.add_argument("--out", required=True)
args = ap.parse_args()

# --- the warehouse side -------------------------------------------------------
alias = get_all("member_email_alias", "at_member_id,email", "at_member_id")
attrs = get_all("member_attributes", "at_member_id,membership_status", "at_member_id")
profs = get_all("member_profiles", "at_member_id,full_name,email", "at_member_id")

status = {a["at_member_id"]: a["membership_status"] for a in attrs}
name_of = {p["at_member_id"]: p.get("full_name") for p in profs}
email_of = {p["at_member_id"]: p.get("email") for p in profs}

by_email = {}
for a in alias:
    by_email.setdefault((a["email"] or "").strip().lower(), set()).add(a["at_member_id"])

active_by_name = {}
for p in profs:
    if status.get(p["at_member_id"]) in ACTIVE:
        active_by_name.setdefault(fold(p.get("full_name")), []).append(p["at_member_id"])


def resolve(email):
    """Mirror of digest.resolve_member_by_email. The SQL function stays authoritative;
    this is only used to decide what to PROPOSE."""
    hits = by_email.get(email, set())
    if len(hits) == 1:
        return next(iter(hits))
    act = [h for h in hits if status.get(h) in ACTIVE]
    return act[0] if len(act) == 1 else None


# --- the audience side --------------------------------------------------------
rows = [r for r in csv.DictReader(open(args.pairs_csv)) if r.get("real_match")]
counts, names = {}, {}
for r in rows:
    e = (r.get("email") or "").strip().lower()
    if not e:
        continue
    counts[e] = counts.get(e, 0) + 1
    names.setdefault(e, r.get("name") or "")

out, stats = [], {"reaches_active": 0, "unresolved": 0, "dormant": 0, "proposed": 0}
for e, n in sorted(names.items()):
    mid = resolve(e)
    if mid and status.get(mid) in ACTIVE:
        stats["reaches_active"] += 1
        continue
    why = "dormant" if mid else "unresolved"
    stats[why] += 1
    cands = active_by_name.get(fold(n), [])
    if len(cands) != 1:
        continue
    target = cands[0]
    if target == mid:
        continue
    stats["proposed"] += 1
    out.append({
        "target_at_member_id": target,
        "target_name": name_of.get(target),
        "target_email": email_of.get(target),
        "target_status": status.get(target),
        "alias_email": e,
        "alias_name_in_groupos": n,
        "today": f"{why}" + (f" -> {mid} ({status.get(mid)})" if mid else ""),
        "videos": counts[e],
        "approve": "",
    })

with open(args.out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["target_at_member_id", "target_name", "target_email",
                                      "target_status", "alias_email", "alias_name_in_groupos",
                                      "today", "videos", "approve"])
    w.writeheader()
    w.writerows(sorted(out, key=lambda r: -r["videos"]))

print(f"audience addresses      : {len(names)}")
print(f"  already reach an active member: {stats['reaches_active']}")
print(f"  resolve to a dormant record   : {stats['dormant']}")
print(f"  resolve to nothing            : {stats['unresolved']}")
print(f"proposals written       : {stats['proposed']} -> {args.out}")
print("Nothing was written to the database. Mark approve=yes and run the write-back.")
