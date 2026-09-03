#!/usr/bin/env python3
"""#70/#17 — weekly check for NEW and CHANGED GroupOS videos, 2026 only.

Why this exists as a two-part job: the GroupOS MCP only runs inside a Claude session, so a
cron script cannot call it. Until GROUPOS_PAT lands (#17), a scheduled Claude session does the
one thing only it can do — dump the 2026 listing to a file — and this script does everything
else headlessly: diff it against the warehouse, upsert what moved, then run the Zoom chain so a
newly published call gets its transcript, embeddings and dossier in the same pass.

Scope is 2026 (Andy 2026-08-07): ~152 videos, two MCP pages, instead of re-reading all 1,024.

  python3 scripts/videos_weekly_check.py <dump.json>            # report only
  python3 scripts/videos_weekly_check.py <dump.json> --apply    # upsert + run the chain
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, "/Users/Born/mds-digest-web/scripts")
from zoom_backfill import ENV_SB, env, sb            # noqa: E402
from ingest_videos import map_video                  # noqa: E402  (single source of the row shape)

# Fields whose change actually matters downstream. A view count ticking up is not a content
# change and must not trigger a re-embed of the whole video.
WATCH = ("title", "description_text", "cliff_notes", "status", "access_restriction",
         "zoom_recording_stamp", "category_names", "tag_names", "speaker_ids", "event_ids")

JOB = "videos_refresh"
MAX_AGE_HOURS = 192          # weekly cadence + buffer; matches the row the alarm reads


def heartbeat(key, status, detail):
    """Stamp digest.olivia_job_heartbeats. Called on EVERY completed run, moved or not."""
    row = {"job": JOB, "last_run_at": "now()", "status": status,
           "detail": detail[:500], "max_age_hours": MAX_AGE_HOURS}
    # Only stamp success — sending the key with a failure would overwrite "when did this last
    # work" at the exact moment you need it. Same rule as zoom_weekly.py.
    if status == "ok":
        row["last_success_at"] = "now()"
    sb("POST", "olivia_job_heartbeats?on_conflict=job", key, [row],
       "resolution=merge-duplicates,return=minimal")


def load_dump(path):
    d = json.loads(open(path).read())
    items = d["items"] if isinstance(d, dict) and "items" in d else d
    return [v for v in items if isinstance(v, dict) and v.get("id")]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    apply = "--apply" in sys.argv
    key = env(ENV_SB)["SUPABASE_SECRET_KEY"]

    incoming = load_dump(args[0])
    print(f"dump: {len(incoming)} videos")

    # PostgREST caps a response at 1000 rows regardless of the limit asked for, so the old
    # single-shot `limit=5000` silently returned only the first 1000 of 1,079 catalogue rows.
    # Every video outside that first page looked absent, was reported NEW on every run, and was
    # re-upserted and re-embedded for nothing. Page it, the way partners_weekly_check.py does.
    cols = ",".join(("video_id",) + WATCH)
    have, off = {}, 0
    while True:
        page = sb("GET", f"videos_catalog?select={cols}&limit=1000&offset={off}", key)
        have.update({r["video_id"]: r for r in page})
        if len(page) < 1000:
            break
        off += 1000

    new, changed, rows = [], [], []
    for v in incoming:
        row, why = map_video(v)
        if not row:
            continue
        cur = have.get(row["video_id"])
        if not cur:
            new.append(row)
        else:
            diff = [f for f in WATCH if json.dumps(cur.get(f), sort_keys=True)
                                     != json.dumps(row.get(f), sort_keys=True)]
            if diff:
                changed.append((row, diff))
        rows.append(row)

    print(f"NEW: {len(new)}")
    for r in new[:20]:
        print(f"   + {r['video_id']} {r['title'][:64]}")
    print(f"CHANGED: {len(changed)}")
    for r, diff in changed[:20]:
        print(f"   ~ {r['video_id']} {r['title'][:48]} — {', '.join(diff)}")

    if not apply:
        print("REPORT ONLY — pass --apply to upsert and run the Zoom chain")
        return 0
    if not (new or changed):
        # A clean check IS a successful run. Stamping only when something moved is why
        # videos_refresh sat "stale since Aug 01" through several good runs and the alarm
        # could never clear — the monitor could not tell a healthy no-op from a dead job.
        heartbeat(key, "ok", f"checked {len(incoming)} videos, nothing moved")
        print("nothing moved — chain not run (heartbeat stamped)")
        return 0

    touched = new + [r for r, _ in changed]
    # A changed row must lose its vector: the chain embeds "videos with no vector (new or
    # re-summarised)", and merge-duplicates leaves an untouched column alone. Without this the
    # 173 videos that gained cliff notes on 2026-09-02 kept vectors built from title +
    # description only, and plain-language search never saw the notes.
    for r in touched:
        r["embedding"] = None
    for i in range(0, len(touched), 100):
        sb("POST", "videos_catalog?on_conflict=video_id", key, touched[i:i + 100],
           "resolution=merge-duplicates,return=minimal")
    print(f"  upserted: {len(touched)}")
    heartbeat(key, "ok", f"{len(new)} new, {len(changed)} changed, {len(touched)} upserted")

    # A new or re-published video may be the first time a call becomes citable, so the chain
    # runs in the same pass: link -> transcript -> embed -> dossier.
    p = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "zoom_weekly.py")],
                       capture_output=True, text=True)
    print(p.stdout.strip()[-1200:])
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
