#!/usr/bin/env python3
"""#101 follow-up — submit a year's videos to AssemblyAI from the presigned export.

  ASSEMBLYAI_API_KEY=... python3 scripts/aai_submit.py --year 2025 [--limit N] [--dry-run]

Persistent version of the ad-hoc 2026 batch runner (2026-08-20: 161/161, $26.23,
zero failures). Reads Andy's dev export (mds_videos_all_signed.csv), submits each
video's presigned download_link with speaker_labels=true, polls to completion, and
saves the FULL payload plus an `_mds` block to ~/mds_transcripts/<year>/<video_id>.json
— the exact shape scripts/aai_transcripts.py ingests.

Resume-safe: a video whose JSON already exists in the output dir is skipped, so a
killed run just gets re-invoked. Presigned links are method-specific: GET works,
HEAD returns 403 — never "verify" a link with HEAD.
"""
import argparse, csv, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.assemblyai.com/v2/transcript"
CSV_DEFAULT = "/Users/Born/Downloads/mds_videos_all_signed.csv"
OUT_BASE = "/Users/Born/mds_transcripts"
MDS_FIELDS = ("video_id", "title", "event_name", "upload_date", "duration",
              "access", "s3_key")


def api(method, url, key, body=None):
    # curl, not urllib: the framework Python has no local cert store on this Mac
    # (SSL: CERTIFICATE_VERIFY_FAILED) — same reason every repo script shells out.
    cmd = ["curl", "-sS", "-m", "120", "-X", method, url,
           "-H", f"authorization: {key}", "-H", "content-type: application/json"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    for attempt in range(5):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except json.JSONDecodeError:
                pass
        if attempt == 4:
            raise RuntimeError(f"{method} {url.split('?')[0]}: "
                               f"{(r.stderr or r.stdout)[:200]}")
        time.sleep(5 * (attempt + 1))


def run_one(row, key, outdir):
    vid = row["video_id"]
    sub = api("POST", API, key, {"audio_url": row["download_link"],
                                 "speaker_labels": True})
    tid = sub["id"]
    while True:
        doc = api("GET", f"{API}/{tid}", key)
        if doc["status"] == "completed":
            break
        if doc["status"] == "error":
            return vid, None, doc.get("error", "unknown error")
        time.sleep(15)
    doc["_mds"] = {k: row.get(k, "") for k in MDS_FIELDS}
    tmp = os.path.join(outdir, f".{vid}.tmp")
    with open(tmp, "w") as f:
        json.dump(doc, f)
    os.replace(tmp, os.path.join(outdir, f"{vid}.json"))
    return vid, doc.get("audio_duration") or 0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", required=True)
    ap.add_argument("--csv", default=CSV_DEFAULT)
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not key:
        env_local = "/Users/Born/mds-digest-web/.env.local"
        for l in open(env_local):
            if l.startswith("ASSEMBLYAI_API_KEY="):
                key = l.split("=", 1)[1].strip()
    if not key and not args.dry_run:
        sys.exit("missing ASSEMBLYAI_API_KEY (env or mds-digest-web/.env.local)")

    outdir = os.path.join(OUT_BASE, args.year)
    os.makedirs(outdir, exist_ok=True)
    have = {f[:-5] for f in os.listdir(outdir) if f.endswith(".json")}

    rows = [r for r in csv.DictReader(open(args.csv))
            if r["upload_year"] == args.year]
    todo = [r for r in rows if r["video_id"] not in have]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{args.year}: {len(rows)} videos in export · {len(have)} already done · "
          f"submitting {len(todo)}")
    if args.dry_run:
        for r in todo[:5]:
            print(f"  would submit {r['video_id']} {r['title'][:60]}")
        return

    done, secs, errors = 0, 0, []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(run_one, r, key, outdir): r for r in todo}
        for fut in as_completed(futs):
            vid, dur, err = fut.result()
            if err:
                errors.append((vid, err))
                print(f"  ERROR {vid}: {err}")
            else:
                done += 1
                secs += dur
                print(f"  {done}/{len(todo)} {vid} · {dur/60:.0f} min")
    hrs = secs / 3600
    print(f"\ndone: {done} · errors: {len(errors)} · {hrs:.1f} hr audio · "
          f"~${hrs * 0.23:.2f} · wall {(time.time() - t0)/60:.0f} min")
    if errors:
        print("failed:", ", ".join(v for v, _ in errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
