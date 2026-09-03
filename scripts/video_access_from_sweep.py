#!/usr/bin/env python3
"""Load digest.video_access grants from a GroupOS per-member entitlement sweep.

Why this exists (Andy 2026-09-03: "all restrictions should be mapped properly to members
so we do not recommend videos I can't see"): the GroupOS MCP is the only thing that can
answer "may member M watch video V" — `videos_list(for_user_id=M, ...)` returns exactly the
videos M is entitled to. The MCP only runs inside a Claude session, so the weekly session
does the probing and writes one JSONL row per member:

    {"user_id": "<groupos user id>", "email": "<AT email>", "ids": ["<video_id>", ...]}

This script turns that file into grant rows. Same rules as load_video_access.py (#101):
emails resolve through digest.resolve_member_by_email(), an unresolvable email is stored
with at_member_id NULL and reported, rows are deduped against the stored (video_id, email)
pairs, and nothing is ever deleted.

  python3 scripts/video_access_from_sweep.py /tmp/sweep_aim.jsonl [--dry-run] [--source api]

Only restricted videos (per digest.videos_catalog) become grant rows; public ids in the sweep
are skipped. Resolving 700+ emails takes ~2 minutes — run it with a generous timeout.
"""
import argparse, json, subprocess, sys

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
    ap.add_argument("sweep_jsonl")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--source", default="api")
    args = ap.parse_args()

    rows_in = [json.loads(l) for l in open(args.sweep_jsonl) if l.strip()]
    unresolved_rows = [r for r in rows_in if r.get("ids") is None]
    if unresolved_rows:
        sys.exit(f"{len(unresolved_rows)} sweep rows have ids=None (probe not recorded) — fix the sweep first")

    # A sweep call returns everything the member may watch, public videos included. Only
    # restricted videos need a grant row — a public one is visible to everyone already, and
    # writing 600+ rows per public video would only bloat the table.
    restricted, off = set(), 0
    while True:
        page = supa("GET", "videos_catalog?select=video_id&access_restriction=eq.restricted"
                           f"&deleted_at=is.null&limit=1000&offset={off}")
        restricted |= {r["video_id"] for r in page}
        if len(page) < 1000:
            break
        off += 1000

    pairs, skipped_public = {}, 0
    for r in rows_in:
        e = (r.get("email") or "").strip().lower()
        if not e:
            continue
        for v in r["ids"]:
            if v not in restricted:
                skipped_public += 1
                continue
            pairs.setdefault((v, e), True)
    emails = sorted({e for (_, e) in pairs})
    print(f"sweep rows: {len(rows_in)} · members with access: {len(emails)} · grant pairs: {len(pairs)}"
          f" · public-video pairs skipped: {skipped_public}")

    member = {e: resolve(e) for e in emails}
    resolved = sum(1 for e in emails if member[e])
    print(f"emails resolved via resolve_member_by_email: {resolved}/{len(emails)}")
    for e in emails:
        if not member[e]:
            print(f"   unresolved (stored with at_member_id NULL): {e}")

    existing, offset = set(), 0
    while True:
        page = supa("GET", "video_access?select=video_id,email"
                           f"&order=video_id,email&limit=1000&offset={offset}")
        existing |= {(r["video_id"], (r["email"] or "").strip().lower()) for r in page}
        if len(page) < 1000:
            break
        offset += 1000

    new = [{"video_id": v, "at_member_id": member[e], "email": e, "source": args.source}
           for (v, e) in sorted(pairs) if (v, e) not in existing]
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
