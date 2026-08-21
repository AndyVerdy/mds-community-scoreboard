#!/usr/bin/env python3
"""#103 — verify the speaker identity space. exit 0 = all PASS."""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")
FAILS = []


def supa_all(path, order):
    rows, off = [], 0
    while True:
        out = subprocess.run(
            ["curl", "-s", "-m", "120",
             f"{BASE}/{path}&order={order}&limit=1000&offset={off}",
             "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
             "-H", "Accept-Profile: digest"],
            capture_output=True, text=True).stdout
        page = json.loads(out)
        if isinstance(page, dict):
            sys.exit(f"GET {path}: {page}")
        rows += page
        if len(page) < 1000:
            return rows
        off += 1000


def check(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL':4}  {name} — {detail}")
    if not ok:
        FAILS.append(name)


speakers = supa_all(
    "speakers?select=speaker_id,canonical,kind,at_member_id,partner_id,note",
    "speaker_id")
links = supa_all("video_speaker_links?select=video_id,speaker_id", "video_id")
# speaker_names=not.is.null matches EMPTY arrays too — filter to non-empty client-side
vids = [v for v in supa_all(
    "videos_catalog?select=video_id,speaker_names&deleted_at=is.null"
    "&speaker_names=not.is.null", "video_id") if v.get("speaker_names")]

canons = [s["canonical"] for s in speakers]
check("same-means-same", len(canons) == len(set(canons)),
      f"{len(canons)} rows, {len(set(canons))} distinct canonicals")

kinds = {}
for s in speakers:
    kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
check("kind integrity",
      all((s["kind"] != "member" or s["at_member_id"]) and
          (s["kind"] != "partner" or s["partner_id"]) for s in speakers),
      f"kinds={kinds}")

sids = {s["speaker_id"] for s in speakers}
check("links resolve", all(l["speaker_id"] in sids for l in links),
      f"{len(links)} links")

linked_videos = {l["video_id"] for l in links}
cat_videos = {v["video_id"] for v in vids}
missing = cat_videos - linked_videos
check("video coverage", len(missing) == 0,
      f"{len(linked_videos)}/{len(cat_videos)} speaker-carrying videos linked"
      + (f" · missing {sorted(missing)[:3]}" if missing else ""))

members = supa_all("member_attributes?select=at_member_id", "at_member_id")
mset = {m["at_member_id"] for m in members}
check("member links exist",
      all(s["at_member_id"] in mset for s in speakers if s["kind"] == "member"),
      f"{kinds.get('member', 0)} member links, all resolve to member_attributes")

by = [s for s in speakers if s["canonical"] == "brandon young"]
bl = [l for l in links if by and l["speaker_id"] == by[0]["speaker_id"]]
check("brandon young one entity",
      len(by) == 1 and len(bl) >= 9 and by[0]["kind"] in ("member", "guest"),
      f"{len(by)} entity ({by[0]['kind'] if by else '-'}), {len(bl)} video links")

unres = kinds.get("unresolved", 0)
check("unresolved bounded", unres <= 35, f"{unres} awaiting review")

print(f"\n{len(FAILS)} FAIL / {7 - len(FAILS)} PASS")
sys.exit(1 if FAILS else 0)
