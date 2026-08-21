#!/usr/bin/env python3
"""#103 — verify the speaker identity space (v2: LIBRARY coverage, not field coverage)."""
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


speakers = supa_all("speakers?select=speaker_id,canonical,kind,at_member_id,partner_id,note",
                    "speaker_id")
links = supa_all("video_speaker_links?select=video_id,speaker_id", "video_id")
plinks = supa_all("video_partner_links?select=video_id,partner_id", "video_id")
vids = supa_all("videos_catalog?select=video_id,app_created_at&deleted_at=is.null",
                "video_id")

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
junk = {s["speaker_id"] for s in speakers if str(s.get("note") or "").startswith("junk_label")}
check("links resolve", all(l["speaker_id"] in sids for l in links), f"{len(links)} links")
check("junk unlinked", all(l["speaker_id"] not in junk for l in links),
      f"{len(junk)} junk_label rows, 0 links allowed")

linked = {l["video_id"] for l in links}
by_year = {}
for v in vids:
    y = (v["app_created_at"] or "")[:4]
    t, c = by_year.get(y, (0, 0))
    by_year[y] = (t + 1, c + (1 if v["video_id"] in linked else 0))
t25, c25 = by_year.get("2025", (0, 0))
t26, c26 = by_year.get("2026", (0, 0))
tot = sum(t for t, _ in by_year.values())
cov = sum(c for _, c in by_year.values())
check("library coverage 2025", c25 * 100 >= t25 * 75, f"{c25}/{t25} ({100*c25//max(t25,1)}%; floor 75%)")
check("library coverage 2026", c26 * 100 >= t26 * 70, f"{c26}/{t26} ({100*c26//max(t26,1)}%; floor 70%)")
check("library coverage ALL", cov * 100 >= tot * 70, f"{cov}/{tot} ({100*cov//max(tot,1)}%; floor 70%)")

members = supa_all("member_attributes?select=at_member_id", "at_member_id")
mset = {m["at_member_id"] for m in members}
check("member links exist",
      all(s["at_member_id"] in mset for s in speakers if s["kind"] == "member"),
      f"{kinds.get('member', 0)} member links, all resolve")

by = [s for s in speakers if s["canonical"] == "brandon young"]
bl = [l for l in links if by and l["speaker_id"] == by[0]["speaker_id"]]
check("brandon young one entity", len(by) == 1 and len(bl) >= 9,
      f"{len(by)} entity, {len(bl)} video links")

pvids = {p["video_id"] for p in plinks}
check("partner sessions linked", len(plinks) >= 80,
      f"{len(plinks)} video-partner links across {len(pvids)} videos")

n = 10 - len(FAILS)
print(f"\n{len(FAILS)} FAIL / {n} PASS")
sys.exit(1 if FAILS else 0)
