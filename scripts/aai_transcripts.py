#!/usr/bin/env python3
"""#101 — AssemblyAI transcripts into digest.content_items, chunked and citable.

  python3 scripts/aai_transcripts.py [--dir /Users/Born/mds_transcripts/2026] [--apply]

Fills the gap #70's Zoom pipeline cannot reach: in-person boardrooms, masterminds,
Inspire sessions. Reuses chunk()/hhmmss() from zoom_transcripts.py verbatim; the only
new code is the adapter from AssemblyAI utterances to the cue shape.

Rules carried over from #70 and #101's spec:
- a video that already has call_transcript chunks is HARD-SKIPPED (Zoom stays source
  of truth where both exist; the 65 are never touched);
- url is ALWAYS the library video (app.mds.co/videos/<id>), never a source file;
- public video -> access_rule {"type":"public"}, sensitivity normal;
  restricted    -> access_rule {"type":"video_access","video_id":...}, sensitivity
  restricted — entitlement-gated by content_search_v2, unknown to every other reader;
- speakers stay 'Speaker A/B/C' — an unverified name on a quote would be a wrong claim
  about a member.

Idempotent: upserts on (source, source_id), source_id = '<video_id>#<chunk index>'.
"""
import argparse, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoom_transcripts import chunk, hhmmss   # noqa: E402  (reused verbatim)

ENV = "/Users/Born/mds-digest-web/.env.local"
APP_VIDEO = "https://app.mds.co/videos/"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def supa(method, path, body=None, prefer=None):
    cmd = ["curl", "-s", "-m", "180", "-X", method, f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    if not out.strip():
        return []
    val = json.loads(out)
    if isinstance(val, dict) and "code" in val and "message" in val:
        sys.exit(f"{method} {path} error: {val}")
    return val


def supa_all(path, order="id"):
    # ORDER IS MANDATORY: PostgREST pages are unstable without it — an unordered
    # limit/offset walk returned 3,116 rows but only 43 of 65 distinct videos.
    rows, offset = [], 0
    while True:
        page = supa("GET", f"{path}&order={order}&limit=1000&offset={offset}")
        rows += page
        if len(page) < 1000:
            return rows
        offset += 1000


def cues_from_aai(doc):
    """AssemblyAI utterances -> the cue shape chunk() consumes:
    (start_sec, end_sec, speaker, text)."""
    return [(u["start"] / 1000.0, u["end"] / 1000.0,
             f"Speaker {u['speaker']}", u["text"])
            for u in (doc.get("utterances") or [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="/Users/Born/mds_transcripts/2026")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    vids = {v["video_id"]: v for v in supa_all(
        "videos_catalog?select=video_id,title,call_type,tag_names,access_restriction,app_created_at"
        "&deleted_at=is.null", order="video_id")}
    have = {(r.get("meta") or {}).get("video_id")
            for r in supa_all("content_items?select=meta&source=eq.call_transcript")}

    files = sorted(f for f in os.listdir(args.dir) if f.endswith(".json"))
    print(f"transcript files: {len(files)} · videos already covered (Zoom): "
          f"{sum(1 for f in files if f[:-5] in have)}")

    rows, skipped_zoom, skipped_nocat = [], 0, 0
    for f in files:
        vid = f[:-5]
        if vid in have:
            skipped_zoom += 1
            continue
        v = vids.get(vid)
        if not v:
            skipped_nocat += 1
            print(f"  ! {vid} not in videos_catalog — skipped")
            continue
        doc = json.load(open(os.path.join(args.dir, f)))
        restricted = (v.get("access_restriction") or "restricted") != "public"
        pieces = chunk(cues_from_aai(doc))
        for i, (start, end, text) in enumerate(pieces):
            rows.append({
                "source": "call_transcript",
                "kind": "chunk",
                "source_id": f"{vid}#{i}",
                "title": v["title"],
                "body": text,
                "occurred_at": v["app_created_at"],
                "url": APP_VIDEO + vid,                       # ALWAYS the library video
                "access_rule": ({"type": "video_access", "video_id": vid}
                                if restricted else {"type": "public"}),
                "sensitivity": "restricted" if restricted else "normal",
                "search_extra": v.get("call_type") or ",".join(v.get("tag_names") or []),
                "meta": {"video_id": vid, "call_type": v.get("call_type"), "chunk": i,
                         "start_sec": int(start), "end_sec": int(end),
                         "timestamp": hhmmss(start), "provenance": "assemblyai"},
            })
        print(f"  {v['app_created_at'][:10]} {v['title'][:52]:<52} {len(pieces):>3} chunks"
              f"{' [restricted]' if restricted else ''}")

    print(f"chunks: {len(rows)} · zoom-covered skipped: {skipped_zoom}"
          f" · not in catalog: {skipped_nocat}")
    if not args.apply:
        print("DRY RUN — pass --apply to write")
        return

    for i in range(0, len(rows), 200):
        supa("POST", "content_items?on_conflict=source,source_id", rows[i:i + 200],
             prefer="resolution=merge-duplicates,return=minimal")
    print(f"  upserted: {len(rows)}")
    print("  entity dossiers:", ", ".join(
        f"{r['o_kind']}={r['o_rows']}"
        for r in supa("POST", "rpc/refresh_entity_dossiers", {})))


if __name__ == "__main__":
    main()
