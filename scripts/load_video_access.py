#!/usr/bin/env python3
"""#101 — load digest.video_access from the GroupOS audience export.

  python3 scripts/load_video_access.py mds_video_audience_pairs.csv [--dry-run]

Keeps ONLY rows with a non-empty real_match — panel_only rows are admin-panel phantoms
(the fixed 63-account test/staff pool, 42 of them yopmail) that grant nothing in the app.
Emails resolve through digest.resolve_member_by_email() (#100), never raw comparison; an
unresolvable email is stored with at_member_id NULL and reported, never dropped — the
grant activates the day the person's alias or membership lands.

Idempotent: diffs against stored (video_id, email) pairs before inserting. The unique
index is on an expression, which PostgREST cannot use as an ON CONFLICT target — same
lesson as #100's loader.
"""
import argparse, csv, json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


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
    val = json.loads(out)
    if isinstance(val, dict) and "code" in val and "message" in val:
        sys.exit(f"{method} {path} error: {val}")
    return val


def resolve(email):
    v = supa("POST", "rpc/resolve_member_by_email", {"p_email": email})
    return v if isinstance(v, str) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs_csv")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw = list(csv.DictReader(open(args.pairs_csv)))
    real = [r for r in raw if (r.get("real_match") or "").strip()]
    print(f"csv rows: {len(raw)} · real_match kept: {len(real)} · panel-only dropped: {len(raw) - len(real)}")

    # dedupe to one row per (video, email); keep the first rule string seen
    pairs = {}
    for r in real:
        e = (r.get("email") or "").strip().lower()
        if not e:
            continue
        pairs.setdefault((r["video_id"], e), r["real_match"])

    emails = sorted({e for (_, e) in pairs})
    print(f"grant pairs: {len(pairs)} · distinct emails: {len(emails)}")

    member = {}
    for e in emails:
        member[e] = resolve(e)
    resolved = sum(1 for e in emails if member[e])
    print(f"emails resolved via resolve_member_by_email: {resolved}/{len(emails)}"
          f" · unresolved: {len(emails) - resolved}")

    rows = [{"video_id": v, "at_member_id": member[e], "email": e, "source": src}
            for (v, e), src in sorted(pairs.items())]

    existing = set()
    offset = 0
    while True:
        page = supa("GET", "video_access?select=video_id,email"
                           f"&order=video_id,email&limit=1000&offset={offset}")
        existing |= {(r["video_id"], (r["email"] or "").strip().lower()) for r in page}
        if len(page) < 1000:
            break
        offset += 1000

    new = [r for r in rows if (r["video_id"], r["email"]) not in existing]
    print(f"already stored: {len(existing)} · new rows to insert: {len(new)}")

    if args.dry_run:
        print("dry run — nothing written")
        return
    if not new:
        print("nothing to do — already current")
        return
    for i in range(0, len(new), 1000):
        supa("POST", "video_access", new[i:i + 1000], prefer="return=minimal")
    print(f"inserted {len(new)}")


main()
