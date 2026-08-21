#!/usr/bin/env python3
"""#101 — apply hand-written summaries to videos_catalog.

  python3 scripts/apply_video_summaries.py summaries.json [--dry-run]

Input: {"<video_id>": "<summary text>", ...}. Guards: refuses to touch a video whose
summary_source is already 'transcript' with a non-null summary (the #70 set stays
untouched); sets summary_source='transcript' and embedding=null so the nightly
re-embeds the row; search_tsv is a STORED column and recomputes itself.
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def supa(method, path, body=None):
    cmd = ["curl", "-s", "-m", "60", "-X", method, f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json", "-H", "Prefer: return=representation"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    val = json.loads(out) if out.strip() else []
    if isinstance(val, dict) and "code" in val:
        sys.exit(f"{method} {path} error: {val}")
    return val


dry = "--dry-run" in sys.argv
summaries = json.load(open(sys.argv[1]))
print(f"summaries in file: {len(summaries)}")

done = skip = 0
for vid, text in summaries.items():
    cur = supa("GET", f"videos_catalog?select=summary,summary_source&video_id=eq.{vid}")
    if not cur:
        sys.exit(f"STOP: {vid} not in catalog")
    if cur[0]["summary"] is not None:
        skip += 1
        continue
    if dry:
        done += 1
        continue
    r = supa("PATCH", f"videos_catalog?video_id=eq.{vid}",
             {"summary": text, "summary_source": "transcript", "embedding": None})
    if not r or r[0].get("summary") != text:
        sys.exit(f"STOP: {vid} patch did not stick")
    done += 1

print(f"{'would write' if dry else 'written'}: {done} · skipped (already summarised): {skip}")
