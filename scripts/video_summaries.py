#!/usr/bin/env python3
"""#70 — a summary on EVERY video, so a recommendation can say what the video actually covers.

Andy 2026-08-07: "we need a raw transcript and search from it, but if someone got a video
recommendation we need a video summary. So summaries must be in every video."

Two tiers, and the tier is recorded so they are never confused:
  transcript  — written from what was SAID (the calls we have VTTs for). Costs a Haiku call.
  description — the GroupOS blurb, cleaned. Free, and honest about being marketing copy.

Idempotent: only writes videos whose summary is missing or whose tier can now be upgraded
(a description summary is replaced once a transcript arrives).

  python3 scripts/video_summaries.py            # counts only
  python3 scripts/video_summaries.py --apply [--limit N]
"""
import concurrent.futures
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from zoom_backfill import ENV_SB, env, sb, sb_all  # noqa: E402

API = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"
WORKERS = 6

SYSTEM = (
    "You write the summary of a recorded MDS community call for e-commerce founders, from its "
    "TRANSCRIPT. Olivia sends this in WhatsApp after asking 'want a quick summary?', so it must "
    "be SCANNABLE on a phone: short sentences, no long clause chains, no semicolons.\n\n"
    "Output EXACTLY this shape and nothing else:\n"
    "*Call covers:* <one line, what the session is about>\n\n"
    "*Key takeaways:*\n"
    "• *<2-4 word label>:* <the point, one short sentence>\n"
    "• *<2-4 word label>:* <the point, one short sentence>\n"
    "(3 to 5 bullets, ordered most useful first)\n\n"
    "Rules: single asterisks for bold — that is WhatsApp, not markdown. Keep each bullet under "
    "25 words. Concrete specifics (tools, numbers, tactics) over adjectives. Never invent "
    "anything the transcript does not say. Never mention the transcript, the recording, the "
    "summary or yourself. Never state revenue figures for a named person."
)


def haiku(akey, title, text):
    body = {"model": MODEL, "max_tokens": 400, "thinking": {"type": "disabled"},
            "system": SYSTEM,
            "messages": [{"role": "user",
                          "content": f"CALL: {title}\n\nTRANSCRIPT:\n{text[:60000]}"}]}
    for _ in (1, 2):
        p = subprocess.run(["curl", "-sS", "-m", "120", API,
                            "-H", "x-api-key: " + akey, "-H", "anthropic-version: 2023-06-01",
                            "-H", "Content-Type: application/json", "--data-binary", "@-"],
                           input=json.dumps(body), capture_output=True, text=True)
        try:
            d = json.loads(p.stdout)
            txt = "".join(c.get("text", "") for c in d.get("content", [])).strip()
            if len(txt) > 80:
                return txt
        except Exception:
            pass
    return None


def main():
    apply = "--apply" in sys.argv
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    e = env(ENV_SB)
    key, akey = e["SUPABASE_SECRET_KEY"], e["CENTURION_ANTHROPIC_API_KEY"]

    # PostgREST caps a response at 1000 rows whatever `limit` says — reading the catalogue in
    # one shot silently returned 1000 of 1024 and 22 of 63 transcript videos on the first run.
    vids = sb_all("videos_catalog?select=video_id,title,description_text,summary,summary_source"
                  "&deleted_at=is.null&status=eq.published&order=video_id", key)
    # the transcript-backed set: digest.calls (one row per Zoom call) PLUS every video that
    # carries call_transcript chunks from another producer (AssemblyAI, #101/#161). Reading
    # calls alone meant an AAI-transcribed video never got a transcript summary from this
    # step — every earlier batch had its summaries hand-written and applied separately.
    with_tr = {c["groupos_video_id"] for c in sb_all(
        "calls?select=groupos_video_id&has_transcript=is.true"
        "&groupos_video_id=not.is.null", key)} - {None}
    with_tr |= {c["video_id"] for c in sb_all(
        "content_items?select=video_id:meta->>video_id&source=eq.call_transcript"
        "&meta->>video_id=not.is.null&order=id", key)} - {None}

    need_tr = [v for v in vids if v["video_id"] in with_tr and v.get("summary_source") != "transcript"]
    need_desc = [v for v in vids if v["video_id"] not in with_tr and not (v.get("summary") or "").strip()]
    print(f"published videos: {len(vids)} · with transcript: {len(with_tr)}")
    print(f"  need a transcript summary : {len(need_tr)}")
    print(f"  need a description summary: {len(need_desc)}")
    if not apply:
        print("DRY RUN — pass --apply to write")
        return

    # NO description tier. A GroupOS blurb is a DESCRIPTION, not a summary of what was said —
    # Andy 2026-08-07 was explicit that short description, cliff notes, file text, transcript,
    # summary and persona are six different things and none stands in for another.

    todo = need_tr[:limit] if limit else need_tr
    if not todo:
        return

    def one(v):
        chunks = sb("GET", "content_items?select=body,meta&source=eq.call_transcript"
                           f"&meta->>video_id=eq.{v['video_id']}&order=id.asc&limit=200", key)
        text = "\n".join(c["body"] for c in chunks)
        if len(text) < 400:
            return None
        s = haiku(akey, v["title"], text)
        if not s:
            print(f"  FAIL {v['title'][:50]} (no summary returned)", flush=True)
            return None
        return {"video_id": v["video_id"], "summary": s, "summary_source": "transcript"}

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        out = [r for r in pool.map(one, todo) if r]
    for r in out:
        # embedding=None on purpose: search_tsv is a GENERATED column so the keyword index picks
        # the new summary up by itself, but the VECTOR does not — it was built before the summary
        # existed. Clearing it marks the row for embed_videos.py, which fills embedding IS NULL.
        # Without this the video is findable by keyword and invisible to semantic search.
        sb("PATCH", f"videos_catalog?video_id=eq.{r['video_id']}", key,
           {"summary": r["summary"], "summary_source": "transcript", "embedding": None},
           "return=minimal")
    print(f"  transcript summaries written: {len(out)} of {len(todo)}")


if __name__ == "__main__":
    main()
