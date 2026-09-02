#!/usr/bin/env python3
"""#103 rung E — named PARTICIPANTS from Zoom transcript cues.

  python3 scripts/load_participants.py [--dry-run]

Zoom chunks (provenance null, #70) carry real display names per utterance
("Dorian Gorski: ..."). For each Zoom-covered video: collect cue names, sum an
approximate talk share (chunk seconds split by each person's line count inside
the chunk), resolve each name through the same evidence ladder as the loader,
and link with role='participant' — group calls have participants, not headline
speakers (Andy 2026-08-21). A name already linked on that video as
role='speaker' only gains talk_seconds, it is not duplicated. Junk-guarded,
idempotent, review-not-guess.
"""
import argparse, csv, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_speakers import (World, canon, supa, supa_all, upsert_speaker)  # noqa: E402

CUE = re.compile(r"^([A-Za-z][A-Za-z.'’\- ]{2,40}?):\s", re.M)
# Review CSVs live under ~/mds_transcripts/review/, NOT ~/Downloads: launchd has no TCC grant for
# Downloads, so the Monday zoom_weekly chain died on PermissionError writing here every week from
# 2026-08-07 (health triage 2026-09-02). A manual run from Terminal never showed it.
REVIEW = os.path.expanduser("~/mds_transcripts/review/mds_participant_review.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    w = World()
    link_rows = supa_all(
        "video_speaker_links?select=video_id,speaker_id,role,talk_seconds", "video_id")
    have = {(l["video_id"], l["speaker_id"]) for l in link_rows}

    chunks = supa_all(
        "content_items?select=body,meta&source=eq.call_transcript"
        "&meta-%3E%3Eprovenance=is.null", "id")
    per_video = {}
    for c in chunks:
        m = c.get("meta") or {}
        vid = m.get("video_id")
        if not vid:
            continue
        dur = max(int(m.get("end_sec") or 0) - int(m.get("start_sec") or 0), 0)
        names = CUE.findall(c.get("body") or "")
        if not names:
            continue
        share = dur / len(names) if names else 0
        agg = per_video.setdefault(vid, {})
        for n in names:
            n = re.sub(r"\s+", " ", n).strip()
            agg[n] = agg.get(n, 0) + share

    print(f"zoom-covered videos with named cues: {len(per_video)}")
    new_links, updates, review = [], 0, []
    conflicts = []
    for vid, agg in per_video.items():
        for nm, secs in agg.items():
            c = canon(nm)
            if not c or c in w.junk or len(c.split()) < 2:
                continue
            kind, at, pid, note = w.classify_from_name(nm)
            sp = upsert_speaker(w, nm, kind, at, pid, f"zoom_cue:{note}", None,
                                args.dry_run, conflicts)
            if not sp:
                continue
            if kind == "unresolved":
                review.append((nm, "zoom cue, ambiguous", vid))
            if (vid, sp) in have:
                if not args.dry_run:
                    supa("PATCH",
                         f"video_speaker_links?video_id=eq.{vid}&speaker_id=eq.{sp}"
                         "&talk_seconds=is.null",
                         {"talk_seconds": int(secs)}, prefer="return=minimal")
                updates += 1
            else:
                new_links.append({"video_id": vid, "speaker_id": sp,
                                  "source": "zoom_cue", "role": "participant",
                                  "talk_seconds": int(secs)})
                have.add((vid, sp))

    print(f"participant links to add: {len(new_links)} · talk_seconds set on "
          f"existing: {updates} · review rows: {len(review)}")
    if args.dry_run:
        for l in new_links[:12]:
            print("  ", l["video_id"], l["speaker_id"], l["talk_seconds"], "s")
        print("DRY RUN — no writes")
        return
    for i in range(0, len(new_links), 500):
        supa("POST", "video_speaker_links", new_links[i:i + 500],
             prefer="return=minimal")
    print(f"inserted: {len(new_links)}")
    if review:
        with open(REVIEW, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["name", "detail", "video_id"])
            wr.writerows(review)
        print(f"review file: {REVIEW} ({len(review)} rows)")


if __name__ == "__main__":
    main()
