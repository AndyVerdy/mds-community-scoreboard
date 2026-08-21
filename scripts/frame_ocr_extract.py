#!/usr/bin/env python3
"""#103 frame-OCR rung, extraction half — sample frames from presigned videos.

  python3 scripts/frame_ocr_extract.py <targets.json> <outdir> [--per-video 8]

For each target {video_id, dur, url}: pull N frames spread across 8%..92% of the
runtime with ffmpeg reading STRAIGHT from the presigned URL (S3 honors range
requests, so a seek fetches kilobytes, not the file). Frames land as
<outdir>/<video_id>__<mmss>.jpg, 960px wide — plenty for the Zoom name label.
The reading half is session-assisted (Claude eyes / reader agents), like the
thumbnail rung. Skips videos whose frames already exist.
"""
import json, os, subprocess, sys


def main():
    targets = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    per = int(sys.argv[sys.argv.index("--per-video") + 1]) if "--per-video" in sys.argv else 8
    os.makedirs(outdir, exist_ok=True)
    done = fail = 0
    for t in targets:
        vid, dur, url = t["video_id"], int(t.get("dur") or 0), t["url"]
        if dur < 120:
            dur = max(dur, 60)
        marks = [int(dur * (0.08 + 0.84 * i / max(per - 1, 1))) for i in range(per)]
        have = [f for f in os.listdir(outdir) if f.startswith(vid)]
        if len(have) >= per - 1:
            done += 1
            continue
        ok = 0
        for m in marks:
            out = f"{outdir}/{vid}__{m//60:03d}{m%60:02d}.jpg"
            if os.path.exists(out):
                ok += 1
                continue
            r = subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error",
                 "-ss", str(m), "-i", url, "-frames:v", "1",
                 "-vf", "scale=960:-2", "-q:v", "4", "-y", out],
                capture_output=True, text=True, timeout=120)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 5000:
                ok += 1
            elif os.path.exists(out):
                os.remove(out)
        if ok:
            done += 1
            print(f"  {vid} {ok}/{per} frames")
        else:
            fail += 1
            print(f"  {vid} FAILED")
    print(f"videos with frames: {done} · failed: {fail}")


if __name__ == "__main__":
    main()
