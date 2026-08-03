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
    ("embed_member_profiles", [f"{REPO}/scripts/embed_member_profiles.py"]),
    # #40: content-corpus embeddings are a PROCESS, not a hand-run event (script skips
    # sub-30-char noise rows by design; lives in mds-scorecard-tools, reads its own env)
    ("embed_content",        ["/Users/Born/mds-scorecard-tools/embed_backfill.py"]),
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
            tail = (r.stdout or r.stderr or "").strip().splitlines()
            detail = (tail[-1] if tail else f"exit {r.returncode}") + f" [{time.time()-t0:.0f}s]"
        except Exception as e:
            ok, detail = False, f"runner error: {e}"
        overall_ok = overall_ok and ok
        stamp(job, ok, detail)
        print(f"{'OK ' if ok else 'ERR'} {job}: {detail}")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
