#!/usr/bin/env python3
"""#15 hands-off pipeline — run the four Olivia derivation jobs nightly, stamp a heartbeat.

Runs each job as a subprocess (one failure never blocks the rest), records last_run/last_success/
status/detail into digest.olivia_job_heartbeats. The #13 pg_cron alarm (off-platform) reads that
table and Slack-alerts if any job goes stale (>26h) — so a SKIPPED run alerts, which is the AC.

All four are idempotent (process only new/changed rows), so a nightly run on quiet data is cheap.
Facebook capture is NOT here: FB removed the permalink anchors, so the scroll/enumerate step is
irreducibly manual (named exception in the ticket) — these are the downstream jobs that CAN run
unattended.

launchd: com.mds.olivia.derivations (nightly 04:30, after persona 04:15). Manual: python3 this.
"""
import json, subprocess, sys, time

REPO = "/Users/Born/Scorecard"
ENV = "/Users/Born/mds-digest-web/.env.local"

# (heartbeat job name, argv) — names match the rows seeded in the migration
JOBS = [
    ("derive_niches",        [f"{REPO}/scripts/olivia_derive_niches.py"]),
    ("label_questions",      [f"{REPO}/scripts/olivia_label_questions.py"]),
    ("sync_chapter_pages",   [f"{REPO}/scripts/sync_chapter_pages.py"]),
    # #161: nightly photo cache (GroupOS avatar -> Airtable attachment -> nothing/initials).
    # No --groupos-roster here: that dump only exists inside a Claude session (same reason
    # partners_weekly_check.py's dump is a separate manual step), so the nightly run is
    # Airtable-only; a session refreshes the GroupOS roster and re-runs with it periodically.
    ("cache_member_photos",  [f"{REPO}/scripts/cache_member_photos.py"]),
    ("embed_member_profiles", [f"{REPO}/scripts/embed_member_profiles.py"]),
    # #40: content-corpus embeddings are a PROCESS, not a hand-run event (script skips
    # sub-30-char noise rows by design; lives in mds-scorecard-tools, reads its own env)
    ("embed_content",        ["/Users/Born/mds-scorecard-tools/embed_backfill.py"]),
    # #159: partner/event catalogs — the *_embed_invalidate triggers NULL a vector on text change and
    # nothing rebuilt it (75 partners dark on 2026-09-03). Nulls-only, resumable, same Voyage model.
    ("embed_catalogs",       [f"{REPO}/scripts/embed_partners_events.py"]),
    # #46: daily member-event diffs + the live-trigger watchdog (exit 1 = trigger dead -> alarm)
    ("member_events_daily",  [f"{REPO}/scripts/olivia_member_events_daily.py"]),
    # #44: expertise ledger + knowledge graph, full recompute (backfill == update, by design)
    ("graph_ledger",         [f"{REPO}/scripts/olivia_graph_nightly.py"]),
    # #50: entity dossiers (video/partner/event/chapter) — after graph_ledger so event/chapter
    # profiles read tonight's fresh member_expertise rows
    ("entity_dossiers",      [f"{REPO}/scripts/olivia_entity_dossiers_nightly.py"]),
    # #161: card blurb (2-3 warm sentences) for every active member whose persona has a summary
    # and no blurb yet, or a blurb older than the persona's own built_at. personas_sheet() falls
    # back to the summary's own first sentences while blurb is missing.
    ("persona_blurbs",       [f"{REPO}/scripts/persona_blurbs.py"]),
]


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("SUPABASE_URL").rstrip("/")
KEY = env("SUPABASE_SECRET_KEY")


def stamp(job, ok, detail):
    row = {"job": job, "last_run_at": "now()", "status": "ok" if ok else "error",
           "detail": detail[:500]}
    if ok:
        row["last_success_at"] = "now()"
    subprocess.run(
        ["curl", "-sS", "-X", "POST", f"{BASE}/rest/v1/olivia_job_heartbeats?on_conflict=job",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
         "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
         "-H", "Prefer: resolution=merge-duplicates,return=minimal",
         "--data-binary", json.dumps([row])],
        capture_output=True, text=True)


def main():
    overall_ok = True
    for job, argv in JOBS:
        t0 = time.time()
        try:
            r = subprocess.run(["/usr/bin/python3"] + argv, cwd=REPO,
                               capture_output=True, text=True, timeout=1800)
            ok = r.returncode == 0
            # On FAILURE prefer stderr: `r.stdout or r.stderr` silently threw the error away
            # whenever the job had printed any progress at all. That is why the 2026-08-03
            # derive_niches failure was recorded as "batch 2/10 classified" — a progress line —
            # instead of the anthropic error that actually killed it, and the heartbeat told
            # whoever triaged it nothing. The error is the whole point of the detail field.
            src = ((r.stderr or r.stdout) if not ok else (r.stdout or r.stderr)) or ""
            tail = src.strip().splitlines()
            detail = (tail[-1] if tail else f"exit {r.returncode}") + f" [{time.time()-t0:.0f}s]"
        except Exception as e:
            ok, detail = False, f"runner error: {e}"
        overall_ok = overall_ok and ok
        stamp(job, ok, detail)
        print(f"{'OK ' if ok else 'ERR'} {job}: {detail}")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
