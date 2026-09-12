#!/usr/bin/env python3
"""
#199 — seeds four digest.content_items rows for the scan_content proof
(scripts/olivia_199_scan_direct.ts + olivia_team_probe.ts, in the mds-digest-web worktree).

Fix round 1 (2026-09-11): the first version keyed the seed under
meta->>'at_member_id', which no production row ever uses (real wa_message
rows key the author under meta->>'sender_member' — verified: 17,611 of
17,611 content_items rows with a 'sender_member' meta key, zero with
'at_member_id'). That made AC1 end-to-end invisible to the model. Fixing the
key alone was not enough: `sender_member` is NOT the attendee's canonical
Members-table id either — it is a SEPARATE Airtable record id, from
digest.member_identity.airtable_id (a WA-identity mapping table), joined as
`member_identity.airtable_id = content_items.meta->>'sender_member'`
(verified: 17,611/17,611 real wa_message rows resolve via that join; 0
resolve via `member_identity.at_member_id = meta->>'sender_member'`). Of the
original four attendees, only Ward Gahan has a member_identity row — the
other three have never sent a linked WhatsApp message, so under EITHER id no
value would make them attributable via the real join path. Swapped in three
more real, confirmed Inspire 2026 attendees who do have a WA identity
mapping, kept Ward Gahan, kept all four message bodies unchanged.

Four REAL Inspire 2026 attendees (verified live 2026-09-11 via
digest.event_registrations joined to digest.events_catalog on event_at_id =
at_record_id — the brief's guessed `e.at_id` column does not exist; the real
PK is `at_record_id` — then joined to digest.member_profiles_team for a real
member, AND to digest.member_identity by at_member_id for a real WA identity):

  at_member_id        wa_identity (member_identity.airtable_id)   name
  rec00zt4nbb6LdmC2    recRDZuJxWu24HdBo                          Ward Gahan
  rec0T1V7UJMz9n6hH    recqVhcrnPBppqVJk                          Max Mikhaylenko
  rec1bCuc9X1LU6QjV    recQupPrlneoKfjJl                          Kayvon Tavakoli
  rec1PiOmfUxwkiBZz    recxVSAS11YmDdcSY                          Shinghi Detlefsen

Each gets one digest.content_items row: source='wa_message', kind='seed-199',
occurred_at 3 days ago (well within the last 30), meta={"chat_id":"seed-199",
"chat_name":"seed-199","sender_member":<wa_identity_id>} — mirroring the
exact 3-key shape real wa_message rows carry, with the real WA-identity id
(not the canonical member id) under 'sender_member', matching the live join
graph exactly.

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

# (at_member_id, wa_identity_id, name) — wa_identity_id is member_identity.airtable_id,
# the value real wa_message rows carry at meta->>'sender_member'.
MEMBERS = [
    ("rec00zt4nbb6LdmC2", "recRDZuJxWu24HdBo", "Ward Gahan"),
    ("rec0T1V7UJMz9n6hH", "recqVhcrnPBppqVJk", "Max Mikhaylenko"),
    ("rec1bCuc9X1LU6QjV", "recQupPrlneoKfjJl", "Kayvon Tavakoli"),
    ("rec1PiOmfUxwkiBZz", "recxVSAS11YmDdcSY", "Shinghi Detlefsen"),
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
    for i, ((at_member_id, wa_identity_id, name), body) in enumerate(zip(MEMBERS, BODIES)):
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
            # mirrors the exact 3-key shape real wa_message rows carry
            "meta": {"chat_id": "seed-199", "chat_name": "seed-199", "sender_member": wa_identity_id},
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
    name_by_wa_id = {wa_id: name for (_, wa_id, name) in MEMBERS}
    for r in inserted:
        wa_id = r["meta"].get("sender_member")
        print(f"    id={r['id']} sender_member={wa_id} member={name_by_wa_id.get(wa_id)} occurred_at={r['occurred_at']}")

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
