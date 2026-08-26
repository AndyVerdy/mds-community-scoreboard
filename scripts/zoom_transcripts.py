#!/usr/bin/env python3
"""#70 — Zoom VTT transcripts into digest.content_items, chunked and citable.

Andy's ruling (2026-08-07): transcripts are vectorized so they drive the best VIDEO
suggestions, and Olivia may QUOTE a passage and POINT to the video — the video in the
LIBRARY (app.mds.co/videos/<id>), never a Zoom URL. So a transcript is only ingested for a
call whose recording is actually published: without a library video there is nothing to cite.

Access follows the video, not the call: a chunk from a `restricted` video is stored with
sensitivity='restricted', which content_search excludes by default (the leak gate proves it).

Idempotent: upserts on (source, source_id) where source_id is '<call_uuid>#<chunk index>'.

  python3 scripts/zoom_transcripts.py            # dry run
  python3 scripts/zoom_transcripts.py --apply
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoom_backfill import CTX, env, sb, sb_all, zoom_get, zoom_token, ENV_SB   # noqa: E402

APP_VIDEO = "https://app.mds.co/videos/"
CHUNK_CHARS = 1400          # ~2-3 minutes of speech; big enough to hold an argument
OVERLAP_CUES = 2            # carry the last cues so a point split across chunks survives

TS = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})")
# A speaker label, not any short prefix before a colon: up to 4 capitalised-ish tokens and no
# sentence punctuation. Without this, "So here's the thing: we scaled" stored the speaker as
# "So here's the thing" — inside text Olivia may quote verbatim.
SPEAKER = re.compile(r"^([A-Z][^:,.!?]{0,38}):\s*(.+)$")


def secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_vtt(text):
    """VTT -> [(start_sec, end_sec, speaker, line)] — Zoom labels the speaker inline."""
    cues, start, end = [], None, None
    for raw in text.splitlines():
        line = raw.strip()
        m = TS.match(line)
        if m:
            start, end = secs(*m.groups()[:4]), secs(*m.groups()[4:])
            continue
        if not line or line == "WEBVTT" or line.isdigit() or start is None:
            continue
        sm = SPEAKER.match(line)
        cues.append((start, end, sm.group(1).strip() if sm else None,
                     sm.group(2).strip() if sm else line))
    return cues


def split_long_cues(cues):
    """Break a cue longer than CHUNK_CHARS into sentence-bounded pieces.

    Zoom cues are short, so this is a no-op there. AssemblyAI is the reason it exists:
    when diarisation finds a single speaker it can return the WHOLE talk as one
    utterance, and the grouping loop below only tests its size boundary between cues —
    so a 36-minute talk landed as one 35k-char chunk stamped 00:00:00 (found 2026-08-25,
    255 videos already affected). One embedding for a whole talk retrieves nothing
    precisely, and a citation that says 00:00:00 for everything is not a citation.

    Timestamps are interpolated by character offset across the cue's span. Speech rate
    is near enough to constant that this lands within seconds — and seconds-accurate
    beats a 36-minute span pointing at the start.
    """
    for start, end, speaker, text in cues:
        if len(text) <= CHUNK_CHARS:
            yield (start, end, speaker, text)
            continue
        span = max(end - start, 0.001)
        parts, cur = [], ""
        for sent in re.split(r"(?<=[.!?])\s+", text):
            if cur and len(cur) + len(sent) + 1 > CHUNK_CHARS:
                parts.append(cur)
                cur = sent
            else:
                cur = f"{cur} {sent}".strip()
        if cur:
            parts.append(cur)
        off = 0
        for part in parts:
            s0 = start + span * (off / len(text))
            off += len(part) + 1
            yield (s0, start + span * (min(off, len(text)) / len(text)), speaker, part)


def chunk(cues):
    """Group cues into passages, keeping the speaker turns and the start timestamp."""
    out, buf, buf_start, size = [], [], None, 0
    for c in split_long_cues(cues):
        if buf_start is None:
            buf_start = c[0]
        line = (f"{c[2]}: {c[3]}" if c[2] else c[3])
        buf.append((c, line))
        size += len(line) + 1
        if size >= CHUNK_CHARS:
            out.append((buf_start, buf[-1][0][1], "\n".join(x[1] for x in buf)))
            buf = buf[-OVERLAP_CUES:]
            buf_start = buf[0][0][0] if buf else None
            size = sum(len(x[1]) + 1 for x in buf)
    if buf and size > 120:      # trailing scraps of a few words are not worth a row
        tail = "\n".join(x[1] for x in buf)
        # the overlap carry-back can re-emit text the previous chunk already holds in
        # full — that is a duplicate row, not an overlap (64 such rows found 2026-08-25)
        if not (out and tail in out[-1][2]):
            out.append((buf_start, buf[-1][0][1], tail))
    return out


def hhmmss(t):
    return f"{int(t)//3600:02d}:{(int(t)%3600)//60:02d}:{int(t)%60:02d}"


def main():
    apply = "--apply" in sys.argv
    key = env(ENV_SB)["SUPABASE_SECRET_KEY"]
    tok = zoom_token()

    calls = sb("GET", "calls?select=call_uuid,topic,call_type,started_at,groupos_video_id"
                      "&is_member_facing=is.true&has_transcript=is.true"
                      "&groupos_video_id=not.is.null&order=started_at", key)
    vids = {v["video_id"]: v for v in sb_all(
        "videos_catalog?select=video_id,access_restriction,title&deleted_at=is.null", key)}
    # I12: only calls without chunks are fetched. Re-downloading 63 VTTs weekly was pure waste,
    # and any one expired URL aborted the run before a single row was written.
    have = {(r.get("meta") or {}).get("call_uuid")
            for r in sb_all("content_items?select=meta&source=eq.call_transcript", key)}
    todo = [c for c in calls if c["call_uuid"] not in have] if "--all" not in sys.argv else calls
    print(f"member calls with a transcript AND a published video: {len(calls)} · "
          f"needing ingest: {len(todo)} (--all to re-fetch every one)")

    rows, skipped, failed = [], 0, []
    for c in todo:
        enc = urllib.parse.quote(urllib.parse.quote(c["call_uuid"], safe=""), safe="")
        rec = zoom_get(f"https://api.zoom.us/v2/meetings/{enc}/recordings", tok)
        if "_err" in rec:
            skipped += 1
            continue
        f = next((x for x in rec.get("recording_files", [])
                  if x.get("file_type") == "TRANSCRIPT"), None)
        if not f:
            skipped += 1
            continue
        try:
            req = urllib.request.Request(f["download_url"],
                                         headers={"Authorization": "Bearer " + tok})
            with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
                vtt = r.read().decode("utf-8", "replace")
        except Exception as ex:
            # one dead download must not cost the whole batch — record it and keep going
            failed.append(f"{c['started_at'][:10]} {c['topic'][:40]}: {ex}")
            continue

        vid = vids.get(c["groupos_video_id"]) or {}
        restricted = (vid.get("access_restriction") or "restricted") != "public"
        pieces = chunk(parse_vtt(vtt))
        for i, (start, end, text) in enumerate(pieces):
            rows.append({
                "source": "call_transcript",
                "kind": "chunk",
                "source_id": f"{c['call_uuid']}#{i}",
                "title": c["topic"],
                "body": text,
                "occurred_at": c["started_at"],
                # ALWAYS the library video — never a Zoom link (Andy 2026-08-07)
                "url": APP_VIDEO + c["groupos_video_id"],
                "access_rule": {"type": "public"},
                "sensitivity": "restricted" if restricted else "normal",
                "search_extra": c["call_type"],
                "meta": {"call_uuid": c["call_uuid"], "video_id": c["groupos_video_id"],
                         "call_type": c["call_type"], "chunk": i,
                         "start_sec": int(start), "end_sec": int(end),
                         "timestamp": hhmmss(start)},
            })
        print(f"  {c['started_at'][:10]} {c['topic'][:52]:<52} {len(pieces):>3} chunks"
              f"{' [restricted]' if restricted else ''}")

    print(f"chunks: {len(rows)} · calls skipped (no transcript file): {skipped}"
          + (f" · DOWNLOAD FAILURES {len(failed)}" if failed else ""))
    for msg in failed:
        print("  ! " + msg)
    if not apply:
        print("DRY RUN — pass --apply to write")
        return

    for i in range(0, len(rows), 200):
        sb("POST", "content_items?on_conflict=source,source_id", key, rows[i:i + 200],
           "resolution=merge-duplicates,return=minimal")
    print(f"  upserted: {len(rows)}")

    # The content dossier updates AS SOON AS THE DATA ARRIVES (Andy 2026-08-07), not on the
    # nightly — a video's topic_profile is now built from what was said in it, so a transcript
    # that lands without this call would leave the dossier describing the old blurb.
    print("  entity dossiers:", ", ".join(
        f"{r['o_kind']}={r['o_rows']}" for r in sb("POST", "rpc/refresh_entity_dossiers", key, {})))


if __name__ == "__main__":
    main()
