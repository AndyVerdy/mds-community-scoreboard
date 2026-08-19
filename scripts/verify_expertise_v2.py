#!/usr/bin/env python3
"""#94 — verify the Expertise Ledger v2 (the living skill sheet).

Reads digest.member_expertise + digest.expertise_topics over REST (service key) and asserts
what v2 promised: the taxonomy landed, subtopics carry real rows, members whose only evidence
is a form answer are now scoreable, no score fell below 40% of its all-time peak, ranks are
sane, and speaking still wins. Prints the after-numbers used to close the ticket.

Scores/ranks are INTERNAL (handbook 7.3) — this script is a maintainer tool, nothing here is
member-visible.

Run:  python3 scripts/verify_expertise_v2.py      # exit 0 = all PASS, exit 1 = any FAIL
"""
import json, statistics, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
ANDY = "recCUUw8iiUnJjac1"          # the active Andy Verdy record (two dup rows carry no scores)
ANDY_TOPIC = "International Expansion"
FLOOR = 0.4                          # proven expertise never drops below 40% of its peak
EPS = 0.001


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("SUPABASE_URL").rstrip("/")
KEY = env("SUPABASE_SECRET_KEY")


def paged_get(path):
    out, offset = [], 0
    while True:  # PostgREST caps at 1000 whatever limit says — ALWAYS page
        r = subprocess.run(
            ["curl", "-sS", f"{BASE}/rest/v1/{path}&limit=1000&offset={offset}",
             "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
             "-H", "Accept-Profile: digest", "--max-time", "120"],
            capture_output=True, text=True)
        page = json.loads(r.stdout) if r.stdout.strip() else None
        if not isinstance(page, list):
            sys.exit(f"GET {path} failed: {str(page)[:300]}")
        out += page
        if len(page) < 1000:
            return out
        offset += 1000


topics = paged_get("expertise_topics?select=topic,parent,terms")
rows = paged_get("member_expertise?select=at_member_id,topic,score,peak_score,"
                 "rank_in_topic,pct,evidence")

parents = [t for t in topics if not t["parent"]]
subs = [t for t in topics if t["parent"]]
sub_names = {t["topic"] for t in subs}
names = {t["topic"] for t in topics}
results = []


def check(name, ok, detail):
    results.append((name, bool(ok), detail))


# 1 — taxonomy present
orphans = [t["topic"] for t in subs if t["parent"] not in names]
check("taxonomy present",
      len(parents) == 18 and len(subs) == 33 and not orphans,
      f"{len(parents)} parents, {len(subs)} subtopics, {len(orphans)} orphans")

# 2 — subtopics carry real rows
sub_rows = [r for r in rows if r["topic"] in sub_names]
sub_scored = {r["topic"] for r in sub_rows if float(r["score"] or 0) > 0}
check("subtopics scored",
      len(sub_rows) >= 200 and len(sub_scored) >= 10,
      f"{len(sub_rows)} rows across {len(sub_scored)} subtopics")

# 3 — silent members gain: forms are their ONLY evidence
other = ("posts", "comments", "videos_spoken", "biz_affinity", "persona_gives_hits")
forms_only = [r for r in rows
              if (r["evidence"] or {}).get("form_hits")
              and not any(k in (r["evidence"] or {}) for k in other)
              and float(r["score"] or 0) > 0]
check("silent members gain",
      len({r["at_member_id"] for r in forms_only}) > 0,
      f"{len({r['at_member_id'] for r in forms_only})} members scoreable on forms alone "
      f"({len(forms_only)} rows) — impossible under v1")

# 4 — the peak floor holds
violations = [r for r in rows
              if float(r["score"] or 0) < FLOOR * float(r["peak_score"] or 0) - EPS]
floored = [r for r in rows if (r["evidence"] or {}).get("peak_floor_applied")]
check("peak floor holds", not violations,
      f"{len(violations)} rows below 40% of peak; {len(floored)} rows currently held up by it")

# 5 — ranks are sane (rank() ties leave gaps, so: starts at 1, never exceeds the row count)
bad_rank = []
by_topic = {}
for r in rows:
    if r["rank_in_topic"] is not None:
        by_topic.setdefault(r["topic"], []).append(int(r["rank_in_topic"]))
for topic, rk in by_topic.items():
    if min(rk) != 1 or max(rk) > len(rk):
        bad_rank.append(topic)
check("ranks sane", not bad_rank,
      f"{len(by_topic)} ranked topics, {len(bad_rank)} broken")

# 6 — Andy spot-check: still top-quartile on International Expansion
andy = [r for r in rows if r["at_member_id"] == ANDY and r["topic"] == ANDY_TOPIC]
apct = float(andy[0]["pct"] or 0) if andy else 0.0
check("andy spot-check", bool(andy) and apct >= 0.75,
      f"pct={apct} on {ANDY_TOPIC}" if andy else "no row")

# 7 — speaking still wins: a speaker outranks a non-speaker on the same topic
spk = [r for r in rows if float((r["evidence"] or {}).get("videos_spoken") or 0) >= 3]
worst = min((float(r["pct"] or 0) for r in spk), default=0.0)
beats = []
for r in spk:
    peers = [p for p in rows
             if p["topic"] == r["topic"] and not (p["evidence"] or {}).get("videos_spoken")]
    if peers:
        beats.append(float(r["score"]) > max(float(p["score"]) for p in peers))
check("speaker spot-check", bool(spk) and worst >= 0.75 and all(beats),
      f"{len(spk)} speaker rows, worst pct={worst}, "
      f"{sum(beats)}/{len(beats)} outrank every non-speaker on their topic")

# ---- report -----------------------------------------------------------------
scored = [r for r in rows if float(r["score"] or 0) > 0]
print(f"AFTER: {len(rows)} rows · {len({r['at_member_id'] for r in rows})} members · "
      f"{len([r for r in rows if float(r['score'] or 0) >= 1])} rows score>=1 · "
      f"{len({r['topic'] for r in scored})} topics scored · "
      f"{len(topics)} topics in taxonomy ({len(parents)}+{len(subs)})")
print(f"{'CHECK':<24} {'RESULT':<6} DETAIL")
for name, ok, detail in results:
    print(f"{name:<24} {'PASS' if ok else 'FAIL':<6} {detail}")
fails = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
