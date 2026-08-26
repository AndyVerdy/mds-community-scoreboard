#!/usr/bin/env python3
"""#101 follow-up — submit videos to AssemblyAI: presigned export OR local files.

  ASSEMBLYAI_API_KEY=... python3 scripts/aai_submit.py --year 2025 [--limit N] [--dry-run]
  ASSEMBLYAI_API_KEY=... python3 scripts/aai_submit.py --local ~/summit_sg [--dry-run]

LOCAL MODE (2026-08-25): the presigned export is a dependency on Andy's dev and its
links expire; when we hold the files we skip S3 entirely. Each file is stripped to
mono 16kHz audio with ffmpeg (a 500MB mp4 becomes ~40MB — transcription reads the
audio track only) and pushed to AAI's own /v2/upload, which hands back a private
URL to transcribe. Needs <dir>/manifest.json: [{"file": "x.mp4", "video_id": "..."}]
— the file->catalogue binding is stated, never guessed from a filename.

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
UPLOAD = "https://api.assemblyai.com/v2/upload"
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


def has_audio(path):
    """A silent video is a real case (the 2025 batch hit one) — detect it here so it
    reads as a skip, not as an ffmpeg 'output contains no stream' error."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def extract_audio(path, cachedir):
    """mp4 -> mono 16kHz m4a. Cached: a re-run after a killed batch re-uses it."""
    out = os.path.join(cachedir, os.path.basename(path) + ".m4a")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    if not has_audio(path):
        raise RuntimeError("no audio track (silent video) — nothing to transcribe")
    tmp = out + ".tmp.m4a"
    r = subprocess.run(["ffmpeg", "-nostdin", "-y", "-i", path, "-vn",
                        "-ac", "1", "-ar", "16000", "-c:a", "aac", "-b:a", "64k",
                        tmp], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-300:]}")
    os.replace(tmp, out)
    return out


def upload(path, key):
    """POST the bytes to AAI, get back a private URL. No S3, no expiry."""
    r = subprocess.run(["curl", "-sS", "-m", "3600", "-X", "POST", UPLOAD,
                        "-H", f"authorization: {key}",
                        "-H", "content-type: application/octet-stream",
                        "--data-binary", f"@{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"upload {os.path.basename(path)}: {r.stderr[:200]}")
    return json.loads(r.stdout)["upload_url"]


def transcribe(audio_url, key):
    """Submit + poll. Returns the completed payload, or raises."""
    tid = api("POST", API, key, {"audio_url": audio_url, "speaker_labels": True})["id"]
    while True:
        doc = api("GET", f"{API}/{tid}", key)
        if doc["status"] == "completed":
            return doc
        if doc["status"] == "error":
            raise RuntimeError(doc.get("error", "unknown error"))
        time.sleep(15)


def run_one_local(entry, key, outdir, cachedir):
    vid = entry["video_id"]
    try:
        audio = extract_audio(entry["path"], cachedir)
        doc = transcribe(upload(audio, key), key)
    except Exception as e:
        return vid, None, str(e)[:200]
    doc["_mds"] = {k: entry.get(k, "") for k in MDS_FIELDS}
    tmp = os.path.join(outdir, f".{vid}.tmp")
    with open(tmp, "w") as f:
        json.dump(doc, f)
    os.replace(tmp, os.path.join(outdir, f"{vid}.json"))
    return vid, doc.get("audio_duration") or 0, None


def catalog_meta(video_ids):
    """_mds block from the catalogue itself — never hand-typed titles."""
    envp = "/Users/Born/mds-digest-web/.env.local"
    vals = {}
    for l in open(envp):
        if "=" in l and not l.startswith("#"):
            k, _, v = l.partition("=")
            vals[k.strip()] = v.strip()
    ids = ",".join(video_ids)
    r = subprocess.run(["curl", "-s", "-m", "60",
                        f"{vals['SUPABASE_URL']}/rest/v1/videos_catalog"
                        f"?select=video_id,title,duration,access_restriction"
                        f"&video_id=in.({ids})",
                        "-H", f"apikey: {vals['SUPABASE_SECRET_KEY']}",
                        "-H", f"Authorization: Bearer {vals['SUPABASE_SECRET_KEY']}",
                        "-H", "Accept-Profile: digest"], capture_output=True, text=True)
    return {row["video_id"]: {"video_id": row["video_id"], "title": row["title"],
                              "duration": row["duration"],
                              "access": row["access_restriction"]}
            for row in json.loads(r.stdout)}


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


def run_local(args, key, outdir, have):
    root = os.path.expanduser(args.local)
    man = os.path.join(root, "manifest.json")
    if not os.path.exists(man):
        sys.exit(f"no manifest at {man} — needs [{{'file':..., 'video_id':...}}]")
    entries = json.load(open(man))

    for e in entries:
        e["path"] = os.path.join(root, e["file"])
        if not os.path.exists(e["path"]):
            sys.exit(f"missing file: {e['path']}")
    meta = catalog_meta([e["video_id"] for e in entries])
    unknown = [e["video_id"] for e in entries if e["video_id"] not in meta]
    if unknown:
        sys.exit(f"not in videos_catalog: {', '.join(unknown)} — ingest the catalogue first")
    for e in entries:
        e.update(meta[e["video_id"]])

    todo = [e for e in entries if e["video_id"] not in have]
    if args.limit:
        todo = todo[:args.limit]
    gb = sum(os.path.getsize(e["path"]) for e in todo) / 1e9
    print(f"{root}: {len(entries)} in manifest · {len(have)} already done · "
          f"submitting {len(todo)} ({gb:.1f} GB of video)")
    if args.dry_run:
        for e in todo:
            print(f"  would submit {e['video_id']} [{e['access']}] {e['title'][:60]}")
        return

    cachedir = os.path.join(outdir, "audio")
    os.makedirs(cachedir, exist_ok=True)
    done, secs, errors = 0, 0, []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [ex.submit(run_one_local, e, key, outdir, cachedir) for e in todo]
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


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--year", help="submit from the presigned export")
    g.add_argument("--local", metavar="DIR",
                   help="submit local files listed in DIR/manifest.json")
    ap.add_argument("--out", help="output dir (default ~/mds_transcripts/<year|basename>)")
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

    label = args.year or os.path.basename(os.path.normpath(args.local))
    outdir = args.out or os.path.join(OUT_BASE, label)
    os.makedirs(outdir, exist_ok=True)
    have = {f[:-5] for f in os.listdir(outdir) if f.endswith(".json")}

    if args.local:
        run_local(args, key, outdir, have)
        return

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
