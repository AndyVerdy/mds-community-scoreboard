#!/usr/bin/env python3
"""#100 — backfill digest.member_email_alias from the three evidenced rungs.

  python3 scripts/load_member_email_aliases.py [--dry-run]

Rungs, in order of authority:
  preferred     member_profiles.email                       — the Members-DB Preferred Email
  stripe        at_fields->>'Stripe Customer Email'         — a payment record
  admin_field   at_fields->>'Associated Emails (Admin)'     — recorded by an admin

Name matches are NOT loaded here. They are proposals — see
scripts/propose_member_email_aliases.py. A name match matched 'andy test' to a real
member record, which is why nothing inferred reaches this table without a human.

Idempotent: the unique index absorbs a re-insert, so a second run changes zero rows.
"""
import argparse, json, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
EMAIL_RE = re.compile(r"[^\s,;<>]+@[^\s,;<>]+\.[^\s,;<>]+")


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def supa(method, path, body=None, prefer=None):
    cmd = ["curl", "-s", "-m", "120", "-X", method, f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    if not out.strip():
        return []
    try:
        val = json.loads(out)
    except Exception:
        sys.exit(f"{method} {path} failed: {out[:300]}")
    if isinstance(val, dict) and "code" in val and "message" in val:
        sys.exit(f"{method} {path} error: {val}")
    return val


def fetch_profiles():
    rows, offset = [], 0
    while True:
        page = supa("GET", "member_profiles?select=at_member_id,email,at_fields"
                           f"&order=at_member_id&limit=1000&offset={offset}")
        rows += page
        if len(page) < 1000:
            return rows
        offset += 1000


def clean(v):
    return (v or "").strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    profiles = fetch_profiles()
    seen, rows = set(), []

    def add(mid, email, source):
        e = clean(email)
        if not e or "@" not in e:
            return
        key = (mid, e)
        if key in seen:          # first rung wins; preferred is added first
            return
        seen.add(key)
        rows.append({"at_member_id": mid, "email": e, "source": source})

    for p in profiles:
        mid = p.get("at_member_id")
        if not mid:
            continue
        f = p.get("at_fields") or {}
        add(mid, p.get("email"), "preferred")
        add(mid, f.get("Stripe Customer Email"), "stripe")
        for m in EMAIL_RE.findall(f.get("Associated Emails (Admin)") or ""):
            add(mid, m, "admin_field")

    counts = {}
    for r in rows:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    print(f"profiles read:        {len(profiles)}")
    print(f"alias rows derived:   {len(rows)}  {counts}")

    # Diff against what is already stored rather than relying on ON CONFLICT.
    # The unique index is on an EXPRESSION, (at_member_id, lower(btrim(email))), which
    # PostgREST cannot infer as a conflict target — so Prefer: resolution=ignore-duplicates
    # does not apply and a re-run raises 23505. Diffing here makes the loader idempotent
    # on its own terms, whatever the database can infer.
    existing, offset = set(), 0
    while True:
        page = supa("GET", "member_email_alias?select=at_member_id,email"
                           f"&order=at_member_id&limit=1000&offset={offset}")
        existing |= {(r["at_member_id"], clean(r["email"])) for r in page}
        if len(page) < 1000:
            break
        offset += 1000

    new = [r for r in rows if (r["at_member_id"], r["email"]) not in existing]
    print(f"already stored:       {len(existing)}")
    print(f"new rows to insert:   {len(new)}")

    if args.dry_run:
        print("dry run — nothing written")
        return

    if not new:
        print("nothing to do — already current")
        return

    for i in range(0, len(new), 500):
        supa("POST", "member_email_alias", new[i:i + 500], prefer="return=minimal")
    print(f"inserted {len(new)}")


main()
