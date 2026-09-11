#!/usr/bin/env python3
"""
#199 — seeds four digest.content_items rows for the scan_content proof
(scripts/olivia_199_scan_direct.ts + olivia_team_probe.ts, in the mds-digest-web worktree).

Four REAL Inspire 2026 attendees (verified live 2026-09-11 via
digest.event_registrations joined to digest.events_catalog on event_at_id =
at_record_id — the brief's guessed `e.at_id` column does not exist; the real
PK is `at_record_id` — then joined to digest.member_profiles_team so each id
resolves to a real member):

  rec00zt4nbb6LdmC2  Ward Gahan
  rec05lSD6p6ElrsIZ  BJ Wright
  rec077pootHBidody  Sofia Tamez
  rec0ERr7rc82WeArG  Jake Ryan

Each gets one digest.content_items row: source='wa_message', kind='seed-199',
occurred_at 3 days ago (well within the last 30), meta={"seed":"199",
"at_member_id":<id>} — the shape scan_content's example SELECT joins on
(c.meta->>'at_member_id'). NOTE: live wa_message rows key the author under
meta->>'sender_member', not meta->>'at_member_id' — no production row carries
an 'at_member_id' key (verified: `content_items where meta ? 'at_member_id'`
returns zero rows across all sources). So these four seeded rows are the ONLY
rows in the table that will ever match the AC1 example SELECT's join/filter;
"scanned = their real rows + 4" in the brief does not apply — real matching
rows do not exist under this meta shape.

access_rule is NOT NULL with no default; team_sql (SECURITY DEFINER, no
access_rule filtering) doesn't care about its content, so a placeholder that
matches the real wa_message shape is used. sensitivity defaults to 'normal'
and is left off. id is GENERATED ALWAYS AS IDENTITY — never supplied.

Idempotent: every run (seed or --cleanup) first deletes kind='seed-199' rows.

Usage:
  python3 scripts/olivia_199_seed.py            # idempotent seed, prints inserted ids
  python3 scripts/olivia_199_seed.py --cleanup  # delete all kind='seed-199' rows, print count
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
KIND = "seed-199"

MEMBERS = [
    ("rec00zt4nbb6LdmC2", "Ward Gahan"),
    ("rec05lSD6p6ElrsIZ", "BJ Wright"),
    ("rec077pootHBidody", "Sofia Tamez"),
    ("rec0ERr7rc82WeArG", "Jake Ryan"),
]

BODIES = [
    "Honestly leaning towards moving to Miami by January, the chapter there is strong.",
    "We might relocate to Miami next year — schools are the open question.",
    "Miami move is happening, signed the lease yesterday.",
    "Toying with a Miami relocation but nothing decided.",
]


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_URL"], env["SUPABASE_SECRET_KEY"]


SB_URL, SB_KEY = load_env()
BASE = f"{SB_URL}/rest/v1"


def sb(method, path, body=None, prefer=None):
    cmd = [
        "curl", "-s", "-X", method, f"{BASE}/{path}",
        "-H", f"apikey: {SB_KEY}", "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Profile: digest", "-H", "Accept-Profile: digest",
        "-H", "Content-Type: application/json",
    ]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"curl failed: {p.stderr}")
    try:
        return json.loads(p.stdout) if p.stdout.strip() else None
    except json.JSONDecodeError:
        return p.stdout


def build_rows():
    base = datetime.now(timezone.utc) - timedelta(days=3)
    rows = []
    for i, ((at_member_id, name), body) in enumerate(zip(MEMBERS, BODIES)):
        occurred_at = (base + timedelta(minutes=5 * i)).isoformat()
        rows.append({
            "source": "wa_message",
            "kind": KIND,
            "source_id": f"seed-199-{i}",
            "title": None,
            "tl_dr": None,
            "body": body,
            "occurred_at": occurred_at,
            "url": None,
            "access_rule": {"chat": "seed-199", "type": "chat_member"},
            "search_extra": None,
            "meta": {"seed": "199", "at_member_id": at_member_id, "member_name": name},
        })
    return rows


def delete_existing():
    rows = sb(
        "DELETE",
        f"content_items?kind=eq.{KIND}",
        prefer="return=representation",
    )
    n = len(rows or [])
    print(f"  deleted {n} content_items row(s) with kind='{KIND}'")
    return n


def seed():
    print("cleaning up any existing seed-199 rows (idempotent) ...")
    delete_existing()

    print("inserting 4 content_items rows for seed-199 ...")
    rows = build_rows()
    inserted = sb("POST", "content_items", body=rows, prefer="return=representation") or []
    ids = [r["id"] for r in inserted]
    print(f"  inserted {len(inserted)} row(s), ids: {ids}")
    for r in inserted:
        print(f"    id={r['id']} at_member_id={r['meta'].get('at_member_id')} member={r['meta'].get('member_name')} occurred_at={r['occurred_at']}")

    # Independent read-back verification via PostgREST (not the insert response).
    check = sb("GET", f"content_items?select=id,meta,occurred_at&kind=eq.{KIND}&order=id.asc") or []
    ok = "OK" if len(check) == 4 else "MISMATCH"
    print(f"  verify: {len(check)} rows with kind='{KIND}' (expected 4) [{ok}]")


def cleanup():
    print("--cleanup: deleting all seed-199 rows ...")
    n = delete_existing()
    print(f"cleanup done: {n} row(s) deleted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleanup", action="store_true", help="delete all seed-199 rows and exit")
    args = ap.parse_args()
    if args.cleanup:
        cleanup()
    else:
        seed()


if __name__ == "__main__":
    main()
