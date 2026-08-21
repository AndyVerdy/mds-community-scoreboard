#!/usr/bin/env python3
"""#70 — the weekly Zoom chain. One job, run by launchd, that keeps calls current.

    new video lands -> catalog carries its video_url -> the GMT<date>-<time> stamp inside it
    identifies the Zoom call -> pull that call's transcript -> embed -> refresh the video's
    dossier so it describes what was SAID, not the blurb it was announced with.

Two triggers on purpose, because they expire differently:

  ATTENDANCE is time-critical and independent of publishing. Zoom drops participant records
  after a ~13-month rolling window, and 8 of the 90 member calls have no published video at
  all — so attendance is swept every run whether or not anything was published. A week not run
  is a week eventually lost for good.

  TRANSCRIPTS + DOSSIERS hang off the video, because Andy's ruling is that Olivia quotes a
  passage and points at the LIBRARY video. No video, nothing to cite, nothing to ingest.

The video-catalog sync needs GROUPOS_PAT: the GroupOS MCP only runs inside a Claude session, so
a headless job cannot call it. Without the key this job still does the whole Zoom half and says
plainly that the catalog may be stale — it does not pretend to be complete.

  python3 scripts/zoom_weekly.py [--dry]
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from zoom_backfill import ENV_SB, env, sb  # noqa: E402

JOB = "zoom_weekly"
MAX_AGE_HOURS = 24 * 9          # weekly cadence + 2 days of slack before the alarm fires


def run(label, args):
    t = time.time()
    p = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    tail = [l for l in p.stdout.strip().splitlines() if l.strip()][-3:]
    print(f"— {label} ({round(time.time()-t)}s, exit {p.returncode})")
    for l in tail:
        print("   " + l)
    if p.returncode != 0:
        print("   STDERR:", (p.stderr or "").strip()[-400:])
    return p.returncode == 0, "\n".join(tail)


def heartbeat(key, status, detail):
    row = {"job": JOB, "last_run_at": "now()", "status": status,
           "detail": detail[:500], "max_age_hours": MAX_AGE_HOURS}
    # Only STAMP success — never send the key otherwise. Sending None UPDATEs the column to
    # NULL, destroying "when did this last work" at the exact moment you need it.
    if status == "ok":
        row["last_success_at"] = "now()"
    sb("POST", "olivia_job_heartbeats?on_conflict=job", key, [row],
       "resolution=merge-duplicates,return=minimal")


def main():
    dry = "--dry" in sys.argv
    e = env(ENV_SB)
    key = e["SUPABASE_SECRET_KEY"]
    notes, ok_all = [], True

    # 1. video catalog. Needs a headless key; the MCP path cannot run from cron.
    if e.get("GROUPOS_PAT"):
        if dry:
            # ingest_videos.py has NO argv parsing — passing --dry did nothing and it would
            # have synced for real. A dry run must not touch the catalogue.
            print("— videos: would sync (skipped: --dry)")
            notes.append("videos: dry")
            ok = True
        else:
            ok, out = run("videos: GroupOS -> videos_catalog",
                          [os.path.join(ROOT, "..", "mds-digest-web", "scripts", "ingest_videos.py")])
            notes.append("videos synced")
        ok_all &= ok
    else:
        newest = sb("GET", "videos_catalog?select=app_created_at&order=app_created_at.desc&limit=1", key)
        stale = (newest or [{}])[0].get("app_created_at", "?")[:10]
        print(f"— videos: SKIPPED, no GROUPOS_PAT. Catalog newest video is {stale}; any call "
              f"published after that cannot be linked or transcribed yet (#17).")
        notes.append(f"videos NOT synced (no GROUPOS_PAT, catalog newest {stale})")

    # 2. calls + attendance. Runs every time — attendance ages out of Zoom.
    ok, out = run("zoom: calls + attendance", [os.path.join(ROOT, "scripts", "zoom_backfill.py")]
                  + ([] if dry else ["--apply"]))
    ok_all &= ok
    notes.append(out.splitlines()[0] if out else "")

    # 3. transcripts for calls whose video is now published -> content_items -> dossier refresh
    ok, out = run("zoom: transcripts -> content_items -> dossiers",
                  [os.path.join(ROOT, "scripts", "zoom_transcripts.py")] + ([] if dry else ["--apply"]))
    ok_all &= ok
    notes.append(out.splitlines()[0] if out else "")

    # 4. summaries for any newly-transcribed call, which also clears their stale vectors
    ok, out = run("summaries: transcript -> videos_catalog.summary",
                  [os.path.join(ROOT, "scripts", "video_summaries.py")] + ([] if dry else ["--apply"]))
    ok_all &= ok

    # 4.5 speaker identity (#103, 2026-08-21): every new video gets its speakers linked
    #     (id join -> names -> title/description -> partner sessions), yesterday's guests
    #     get promoted if they joined, and Zoom-named cues become participant links with
    #     talk_seconds. All three are idempotent diff-before-insert loaders.
    ok, out = run("speakers: link new videos (rungs A-D)",
                  [os.path.join(ROOT, "scripts", "load_speakers.py")]
                  + (["--dry-run"] if dry else []))
    ok_all &= ok
    ok, out = run("speakers: promote guests who became members",
                  [os.path.join(ROOT, "scripts", "load_speakers.py"), "--rescan"]
                  + (["--dry-run"] if dry else []))
    ok_all &= ok
    ok, out = run("speakers: Zoom cue participants + talk time",
                  [os.path.join(ROOT, "scripts", "load_participants.py")]
                  + (["--dry-run"] if dry else []))
    ok_all &= ok

    # 5. embed what is new. TWO corpora, and the video one was in no schedule at all — so a
    #    summary written last week was keyword-searchable but semantically invisible.
    if dry:
        print("— embed: would embed new content_items + videos (skipped: --dry)")
    else:
        ok, out = run("embed: new content_items",
                      ["/Users/Born/mds-scorecard-tools/embed_backfill.py"])
        ok_all &= ok
        ok, out = run("embed: videos with no vector (new or re-summarised)",
                      ["/Users/Born/mds-scorecard-tools/embed_videos.py"])
        ok_all &= ok

    if dry:
        print("DRY RUN — no heartbeat written")
        return 0
    # A job that can never do half its work is not "ok". Without GROUPOS_PAT the video sync
    # cannot run headlessly, so the run is DEGRADED — visible to the alarm without anyone
    # having to read `detail`.
    status = "error" if not ok_all else ("degraded" if not e.get("GROUPOS_PAT") else "ok")
    heartbeat(key, status, " · ".join(n for n in notes if n))
    print("heartbeat:", status)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
