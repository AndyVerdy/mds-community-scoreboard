#!/usr/bin/env python3
"""
#170 — seeds the three olivia_web_messages/olivia_web_threads threads the long-thread-memory
proof (scripts/olivia_170_proof.ts, in the mds-digest-web worktree) reads:

  t_170_long  110 rows, alternating member/olivia. Row 3 (member) states an MRR reporting
              decision ("paid date, not invoice date"); row 4 (olivia) confirms it. Rows
              5-110 are varied filler (Miami members, Singapore summit agenda, partner
              offers, video library, WhatsApp digests) so the fold has real prose to summarise.
  t_170_mid   20 rows, same alternating shape, filler only — no decision.
  t_170_fresh 0 rows seeded — the thread id is used bare for the fresh-thread proof run.

Idempotent: every run (seed or --cleanup) first deletes these three thread ids from both
digest.olivia_web_messages and digest.olivia_web_threads.

Every seeded row carries an EXPLICIT created_at starting three days ago and advancing two
minutes per row, so none of it lands on today (UTC) — the Team route's per-day budget
(`dailySpend`) counts today's `olivia` rows, and seeding must never spend it.

Usage:
  python3 scripts/olivia_170_seed_thread.py            # idempotent seed
  python3 scripts/olivia_170_seed_thread.py --cleanup  # delete all three threads, print counts
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
ASKER_EMAIL = "andy@mds.co"
THREAD_LONG = "t_170_long"
THREAD_MID = "t_170_mid"
THREAD_FRESH = "t_170_fresh"
THREADS = [THREAD_LONG, THREAD_MID, THREAD_FRESH]

DECISION_Q = "Let's agree on this now: we report MRR on the paid date, not the invoice date."
DECISION_A = "Agreed and noted: MRR is reported on the paid date, not the invoice date."

# Five unrelated topics, cycled with a per-row note so every row is distinct prose — long
# enough (question >= 80 chars, answer >= 160 chars) that the Haiku fold has something real
# to compress, short enough to keep 110 rows fast to seed.
TOPICS = [
    (
        "Which members in the Miami area have been most active in the community this month, "
        "and should we consider organizing a regional meetup there soon?",
        "Looking at the engagement data, there are roughly a dozen highly active members based "
        "in the Miami area right now, spanning ecommerce, supplements and logistics niches. A "
        "regional meetup could work well given the density, and a few of them have already "
        "expressed interest in an informal happy hour before the end of the quarter.",
    ),
    (
        "Can you walk me through where things stand with the Singapore summit agenda, including "
        "which sessions are confirmed and which speakers still need to be locked in?",
        "The Singapore summit agenda has the opening keynote and two panel sessions confirmed, "
        "covering supply chain resilience and cross-border ecommerce strategy. Three additional "
        "breakout sessions are still pending speaker confirmation, and check-in logistics for the "
        "venue are being finalized separately with the local events team.",
    ),
    (
        "What partner offers are currently live for members, and are there any that seem to be "
        "underperforming or need a refresh to stay relevant this quarter?",
        "There are currently several partner offers live across logistics, software tooling and "
        "financing categories. A couple of the older offers have seen declining click-through over "
        "the last quarter and are good candidates for a refresh, or for renegotiating terms "
        "with the partner before the next renewal window.",
    ),
    (
        "How is the video library being used by members lately, and are there any topics or "
        "formats that seem to be resonating more than others right now?",
        "The video library continues to get steady traffic, with shorter tactical videos on "
        "specific growth channels outperforming the longer panel recordings. Members seem to "
        "prefer content they can act on quickly, which is worth keeping in mind when planning "
        "which sessions to cut down for the archive next month.",
    ),
    (
        "What does the WhatsApp digest cadence look like right now, and have there been any "
        "issues with delivery or member engagement with it recently?",
        "The WhatsApp digest is going out on its usual schedule with no delivery issues reported "
        "recently. Engagement has been steady, with most members opening it within a few hours "
        "of send, though a small number have asked about adjusting the frequency down to a "
        "couple of times a week instead of daily.",
    ),
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


def filler_pair(i):
    q, a = TOPICS[i % len(TOPICS)]
    q = f"{q} (seed-170 note #{i})"
    a = f"{a} (seed-170 reference #{i})"
    assert len(q) >= 80, f"row {i}: question too short ({len(q)} chars)"
    assert len(a) >= 160, f"row {i}: answer too short ({len(a)} chars)"
    return q, a


def build_rows(thread_id, n, decision_at=None):
    """decision_at: 1-based row index of the member decision row (e.g. 3), or None for filler-only."""
    base = datetime.now(timezone.utc) - timedelta(days=3)
    rows = []
    for i in range(1, n + 1):
        created_at = (base + timedelta(minutes=2 * (i - 1))).isoformat()
        is_member = i % 2 == 1  # row 1 = member, alternating
        role = "member" if is_member else "olivia"
        if decision_at and i == decision_at:
            text = DECISION_Q
        elif decision_at and i == decision_at + 1:
            text = DECISION_A
        else:
            q, a = filler_pair(i)
            text = q if is_member else a
        # A PostgREST bulk insert (array body) requires every object to carry the SAME key
        # set (PGRST102 "All object keys must match") — and a single POST per thread is what
        # keeps global `id` assignment in exact row order (1..n), which is what makes
        # "row 94 of 110" a meaningful position. So every row carries all six shared keys;
        # only the value differs by role.
        row = {
            "thread_id": thread_id, "asker_email": ASKER_EMAIL, "mode": "team", "target": "prod",
            "role": role, "route": "team-research", "created_at": created_at,
            "text": text if role == "member" else None,
            "answer_md": None if role == "member" else text,
            "notes": [] if role == "member" else ["seed-170"],
            "sources": [],
            "plan": None if role == "member" else [],
        }
        rows.append(row)
    return rows


def delete_existing():
    for t in THREADS:
        msgs = sb(
            "DELETE",
            f"olivia_web_messages?thread_id=eq.{t}&asker_email=eq.{ASKER_EMAIL}",
            prefer="return=representation",
        )
        thr = sb("DELETE", f"olivia_web_threads?thread_id=eq.{t}", prefer="return=representation")
        n_msgs = len(msgs or [])
        n_thr = len(thr or [])
        print(f"  {t}: deleted {n_msgs} olivia_web_messages row(s), {n_thr} olivia_web_threads row(s)")


def seed():
    print("cleaning up any existing t_170_* rows (idempotent) ...")
    delete_existing()

    print("inserting t_170_long (110 rows, decision at rows 3-4) ...")
    long_rows = build_rows(THREAD_LONG, 110, decision_at=3)
    inserted_long = sb(
        "POST", "olivia_web_messages", body=long_rows, prefer="return=representation,resolution=merge-duplicates"
    )
    print(f"  inserted {len(inserted_long or [])} rows for {THREAD_LONG}")

    print("inserting t_170_mid (20 rows, filler only) ...")
    mid_rows = build_rows(THREAD_MID, 20, decision_at=None)
    inserted_mid = sb(
        "POST", "olivia_web_messages", body=mid_rows, prefer="return=representation,resolution=merge-duplicates"
    )
    print(f"  inserted {len(inserted_mid or [])} rows for {THREAD_MID}")

    print(f"{THREAD_FRESH}: nothing seeded (used bare in the proof run)")

    # Row-count + backdating sanity check via PostgREST itself (a second, independent read
    # from the SQL check the operator runs separately).
    for t, expect in ((THREAD_LONG, 110), (THREAD_MID, 20)):
        rows = sb(
            "GET",
            f"olivia_web_messages?select=id,created_at&thread_id=eq.{t}&asker_email=eq.{ASKER_EMAIL}&order=id.asc",
        ) or []
        n = len(rows)
        first_ca = rows[0]["created_at"] if rows else None
        last_ca = rows[-1]["created_at"] if rows else None
        ok = "OK" if n == expect else "MISMATCH"
        print(f"  verify {t}: {n} rows (expected {expect}) [{ok}] created_at {first_ca} .. {last_ca}")


def cleanup():
    print("--cleanup: deleting all t_170_* rows ...")
    delete_existing()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleanup", action="store_true", help="delete all three seed threads and exit")
    args = ap.parse_args()
    if args.cleanup:
        cleanup()
    else:
        seed()


if __name__ == "__main__":
    main()
