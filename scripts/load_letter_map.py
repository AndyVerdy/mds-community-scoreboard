#!/usr/bin/env python3
"""#103 letter-mapping rung — AAI "Speaker A/B/C" -> real people, evidence-floored.

  python3 scripts/load_letter_map.py [--dry-run]

Sources: the local AAI payloads (~/mds_transcripts/2025 + 2026) — utterances carry
letter + text + ms timing. Three confidence rungs, nothing below them:

  self_intro         the letter says "I'm <Name>" / "my name is <Name>" in its first
                     6 utterances AND the name resolves through the speaker ladder
                     (member / GroupOS / existing entity). Full-name only.
  first_name_unique  a single-token self-intro ("I'm Leslie") where exactly ONE
                     speaker already linked to THAT video has that first name.
  solo_dominant      one letter holds >60% of talk time AND the video has exactly
                     one existing role='speaker' link — the titled presenter.

Writes digest.video_speaker_letters (quote attribution at answer time) and adds
video_speaker_links role='participant' with talk_seconds (real per-letter ms sums)
for mapped letters that aren't linked yet. Unmapped letters stay letters — a wrong
name on a quote is worse than no name. Idempotent: existing (video,letter) rows and
links are skipped. Measured base (2026-08-21): 393 AAI videos, 279 solo-dominant,
132 with self-intros.
"""
import argparse, csv, glob, json, os, re, sys


def lev(a, b):
    """Plain Levenshtein — names are short, O(len*len) is fine."""
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_speakers import World, canon, supa, supa_all, upsert_speaker  # noqa: E402

DIRS = ("/Users/Born/mds_transcripts/2025", "/Users/Born/mds_transcripts/2026")
INTRO = re.compile(r"\b(?:I'm|I am|my name is)\s+"
                   r"([A-Z][a-z'’\-]+(?:\s+[A-Z][A-Za-z'’\-]+){0,2})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    w = World()
    have_letters = {(r["video_id"], r["letter"]) for r in supa_all(
        "video_speaker_letters?select=video_id,letter", "video_id")}
    link_rows = supa_all(
        "video_speaker_links?select=video_id,speaker_id,role", "video_id")
    links_by_video = {}
    for l in link_rows:
        links_by_video.setdefault(l["video_id"], []).append(l)
    have_links = {(l["video_id"], l["speaker_id"]) for l in link_rows}
    spk_by_id = {s["speaker_id"]: s for s in w.speakers.values()}

    new_letters, new_links, conflicts, review = [], [], [], []
    stats = {"self_intro": 0, "first_name_unique": 0, "solo_dominant": 0,
             "skipped_unresolvable": 0}
    for d in DIRS:
        for f in sorted(glob.glob(d + "/*.json")):
            vid = os.path.basename(f)[:-5]
            doc = json.load(open(f))
            utts = doc.get("utterances") or []
            if not utts:
                continue
            talk, per = {}, {}
            for u in utts:
                talk[u["speaker"]] = talk.get(u["speaker"], 0) + (u["end"] - u["start"])
                per.setdefault(u["speaker"], []).append(u["text"])
            total = sum(talk.values()) or 1
            vlinks = links_by_video.get(vid, [])
            v_speakers = [spk_by_id.get(l["speaker_id"]) for l in vlinks]
            v_speakers = [s for s in v_speakers if s]

            mapped = {}
            for letter, texts in per.items():
                if (vid, letter) in have_letters or letter in mapped:
                    continue
                for t in texts[:6]:
                    m = INTRO.search(t)
                    if not m:
                        continue
                    name = m.group(1).strip()
                    if len(name.split()) >= 2:
                        kind, at, pid, note = w.classify_from_name(name)
                        if canon(name) in w.junk:
                            break
                        if kind == "unresolved":
                            stats["skipped_unresolvable"] += 1
                            break
                        if kind == "guest" and note == "no_match":
                            # ASR spelling ("Mo Kohel" for Mo Kuhail): NEVER mint a
                            # new entity from a heard name — fuzzy-match against the
                            # speakers already on THIS video, else review.
                            tgt = [sp2 for sp2 in v_speakers
                                   if lev(canon(name), sp2["canonical"]) <= 2]
                            if len({sp2["speaker_id"] for sp2 in tgt}) == 1:
                                mapped[letter] = (tgt[0]["speaker_id"],
                                                  "self_intro",
                                                  f"asr~{tgt[0]['canonical']}: {t[:90]}")
                            else:
                                stats["skipped_unresolvable"] += 1
                                review.append((name, "asr name, no fuzzy target", vid))
                            break
                        sp = upsert_speaker(w, name, kind, at, pid,
                                            f"letter_self_intro:{note}", None,
                                            args.dry_run, conflicts)
                        if sp:
                            mapped[letter] = (sp, "self_intro", t[:120])
                    else:
                        first = canon(name)
                        cands = [s for s in v_speakers
                                 if s["canonical"].split()[0] == first]
                        if len({s["speaker_id"] for s in cands}) == 1:
                            mapped[letter] = (cands[0]["speaker_id"],
                                              "first_name_unique", t[:120])
                    break

            # solo-dominant: one loud letter + exactly one titled speaker on the video
            dom = max(talk, key=talk.get)
            titled = [l for l in vlinks if l["role"] == "speaker"]
            if ((vid, dom) not in have_letters and dom not in mapped
                    and talk[dom] / total > 0.6
                    and len({l["speaker_id"] for l in titled}) == 1):
                mapped[dom] = (titled[0]["speaker_id"], "solo_dominant",
                               f"{100*talk[dom]//total}% of talk")

            for letter, (sp, conf, ev) in mapped.items():
                stats[conf] += 1
                new_letters.append({"video_id": vid, "letter": letter,
                                    "speaker_id": sp, "confidence": conf,
                                    "evidence": ev})
                if (vid, sp) not in have_links:
                    new_links.append({"video_id": vid, "speaker_id": sp,
                                      "source": "letter_map", "role": "participant",
                                      "talk_seconds": talk[letter] // 1000})
                    have_links.add((vid, sp))

    print(f"letter mappings: {len(new_letters)} · {stats}")
    print(f"new participant links: {len(new_links)} · conflicts: {len(conflicts)}")
    if args.dry_run:
        for r in new_letters[:12]:
            print(f"  {r['video_id'][:12]} {r['letter']} -> #{r['speaker_id']} "
                  f"({r['confidence']}) {r['evidence'][:60]}")
        print("DRY RUN — no writes")
        return
    for i in range(0, len(new_letters), 500):
        supa("POST", "video_speaker_letters", new_letters[i:i + 500],
             prefer="return=minimal")
    for i in range(0, len(new_links), 500):
        supa("POST", "video_speaker_links", new_links[i:i + 500],
             prefer="return=minimal")
    print(f"inserted: {len(new_letters)} letters · {len(new_links)} links")
    if review:
        pth = os.path.expanduser("~/Downloads/mds_letter_review.csv")
        with open(pth, "w", newline="") as fh:
            wr = csv.writer(fh)
            wr.writerow(["heard_name", "detail", "video_id"])
            wr.writerows(review)
        print(f"review file: {pth} ({len(review)} rows)")


if __name__ == "__main__":
    main()
