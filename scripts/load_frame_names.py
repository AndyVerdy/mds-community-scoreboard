#!/usr/bin/env python3
"""#103 frame-OCR rung, loading half — on-screen names into speaker links.

  python3 scripts/load_frame_names.py <frame_names.json...> [--dry-run]

Input files: {"<video_id>": {"names":[{"name":..., "role":"onscreen|moderator|host"}],
"note": ...}} produced by the session-assisted frame readers. Zoom tile labels are
TYPED display names (not ASR), so an unknown full name may create a guest entity —
same trust level as the GroupOS mirror. Resolution per name:

  full name  -> standard ladder (member email/name -> partner -> guest-create)
  one token  -> exactly ONE known person (this video's links, then the member
                dictionary) whose FIRST name matches -> that person; else skip.

role: onscreen -> participant · moderator/host -> moderator. Idempotent.
"""
import json, sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from load_speakers import World, canon, supa, supa_all, upsert_speaker  # noqa: E402


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    w = World()
    have = {(l["video_id"], l["speaker_id"]) for l in supa_all(
        "video_speaker_links?select=video_id,speaker_id", "video_id")}
    links_by_video = {}
    for l in supa_all("video_speaker_links?select=video_id,speaker_id", "video_id"):
        links_by_video.setdefault(l["video_id"], set()).add(l["speaker_id"])
    spk_by_id = {s["speaker_id"]: s for s in w.speakers.values()}

    new, skipped, conflicts = [], [], []
    for f in files:
        for vid, entry in json.load(open(f)).items():
            for ordn, item in enumerate(entry.get("names") or []):
                nm = str(item.get("name") or "").strip()
                role = "moderator" if item.get("role") in ("moderator", "host") \
                       else "participant"
                c = canon(nm)
                if not c or c in w.junk:
                    continue
                sp = None
                if len(c.split()) >= 2:
                    ex = w.speakers.get(c)
                    if ex and ex["kind"] != "unresolved":
                        # already-resolved entity (e.g. Chad Drew fixed in review
                        # triage) wins over re-classification of a dup-record name
                        sp = ex["speaker_id"]
                        if (vid, sp) not in have:
                            new.append({"video_id": vid, "speaker_id": sp,
                                        "source": "frame_ocr", "role": role,
                                        "ordinal": ordn})
                            have.add((vid, sp))
                        continue
                    kind, at, pid, note = w.classify_from_name(nm)
                    if kind == "unresolved":
                        skipped.append((nm, "ambiguous", vid))
                        continue
                    if kind == "guest" and note == "no_match":
                        note = "frame_ocr_guest"
                    sp = upsert_speaker(w, nm, kind, at, pid, f"frame_ocr:{note}",
                                        None, dry, conflicts)
                else:
                    first = c
                    cands = {sid for sid in links_by_video.get(vid, set())
                             if spk_by_id.get(sid, {}).get("canonical", "")
                             .split()[0] == first}
                    if not cands:
                        full = {n for n in w.by_name if n.split()[0] == first}
                        ids = set()
                        for n in full:
                            active = [a for a in w.by_name[n]
                                      if w.statuses.get(a) in
                                      ("Current Member", "New Member",
                                       "Pending Group Entrance",
                                       "Current Member- Not Renewing")]
                            if len(active) == 1 and n in w.speakers:
                                ids.add(w.speakers[n]["speaker_id"])
                        cands = ids
                    if len(cands) == 1:
                        sp = cands.pop()
                    else:
                        skipped.append((nm, f"first-name {len(cands)} candidates", vid))
                        continue
                if sp and (vid, sp) not in have:
                    new.append({"video_id": vid, "speaker_id": sp,
                                "source": "frame_ocr", "role": role,
                                "ordinal": ordn})
                    have.add((vid, sp))

    print(f"new links: {len(new)} · skipped: {len(skipped)} · conflicts: {len(conflicts)}")
    for s in skipped[:15]:
        print("  skip:", s)
    if dry:
        print("DRY RUN — no writes")
        return
    for i in range(0, len(new), 500):
        supa("POST", "video_speaker_links", new[i:i + 500], prefer="return=minimal")
    print(f"inserted: {len(new)}")


if __name__ == "__main__":
    main()
