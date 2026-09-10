#!/usr/bin/env python3
"""#64 — run any job and stamp its heartbeat, so a job that dies stops doing it silently.

    python3 scripts/run_with_heartbeat.py <job-name> <max-age-hours> -- <command...>

Five launchd jobs stamp nothing: `olivia-eval`, `persona.refresh`, `wa.dailydigest`, `watchdog`
and `scorecard.heartbeat`. If any of them stops, the only trace is the mtime of a log file that a
human would have to think to look at. That is the failure mode #64 exists for, and the night of
2026-09-10 hit it three times.

Everything needed to fix it already exists: `digest.olivia_job_heartbeats` plus the pg_cron alarm
that fires when `last_success_at` falls behind `max_age_hours`. A job only has to write a row. This
wrapper writes it for jobs that were never taught to, without editing the jobs themselves — which
matters because two of them live in `mds-scorecard-tools/`, a directory that is not a git
repository.

Exit code is the child's, unchanged, so launchd still sees the truth.
"""
import json
import subprocess
import sys

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"


def key():
    for line in open(ENV_PATH):
        if line.startswith("SUPABASE_SECRET_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"no SUPABASE_SECRET_KEY in {ENV_PATH}")


def stamp(job, max_age_hours, ok, detail):
    row = {"job": job, "last_run_at": "now()", "status": "ok" if ok else "error",
           "max_age_hours": max_age_hours, "detail": detail[:500]}
    if ok:
        row["last_success_at"] = "now()"
    k = key()
    subprocess.run(
        ["curl", "-sS", "--max-time", "30", "-X", "POST",
         f"{BASE}/olivia_job_heartbeats?on_conflict=job",
         "-H", f"apikey: {k}", "-H", f"Authorization: Bearer {k}",
         "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
         "-H", "Prefer: resolution=merge-duplicates,return=minimal",
         "--data-binary", json.dumps([row])],
        capture_output=True, text=True)


def main(argv):
    if len(argv) < 4 or "--" not in argv:
        sys.exit(__doc__)
    job = argv[1]
    try:
        max_age = int(argv[2])
    except ValueError:
        sys.exit("max-age-hours must be a whole number of hours")
    cmd = argv[argv.index("--") + 1:]
    if not cmd:
        sys.exit("no command after --")

    r = subprocess.run(cmd, capture_output=True, text=True)
    # The child's own output still goes to the launchd log, unchanged.
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)

    ok = r.returncode == 0
    # On failure prefer stderr: the error is the whole point of the detail field, and
    # `stdout or stderr` throws it away whenever the job printed any progress at all.
    src = ((r.stderr or r.stdout) if not ok else (r.stdout or r.stderr)) or ""
    tail = src.strip().splitlines()
    detail = (tail[-1] if tail else f"exit {r.returncode}")
    stamp(job, max_age, ok, detail)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
