#!/usr/bin/env python3
"""Merge the six `expect`-written shards into eval_bank_C_2026-08-23.json, ordered so the runner
inserts as few reset turns as possible: grouped by class, every multi-turn thread kept contiguous
and in order. Validates before writing — a bank with a hole in it is worse than no bank.
"""
import json, os, sys
from collections import Counter, defaultdict

REPO = "/Users/Born/Scorecard"
SCR = "/private/tmp/claude-501/-Users-Born-Scorecard/d7c6c01a-5cbb-42e4-83d3-d31df36f5d0d/scratchpad"
OUT = f"{REPO}/eval_bank_C_2026-08-23.json"

qs = []
for i in range(6):
    p = f"{SCR}/bankc/done{i}.json"
    if not os.path.exists(p):
        sys.exit(f"missing shard output: {p}")
    qs += json.load(open(p))

skel = {(q["tier"], q["id"]): q for q in json.load(open(f"{SCR}/eval_bank_C_skeleton.json"))["questions"]}
seen, problems = set(), []
for q in qs:
    k = (q["tier"], q["id"])
    if k in seen:
        problems.append(f"duplicate id {k}")
    seen.add(k)
    if k not in skel:
        problems.append(f"unknown id {k}")
    elif q["q"].strip() != skel[k]["q"].strip():
        problems.append(f"id {k}: question text was REWORDED — not allowed")
    if not (q.get("expect") or "").strip():
        problems.append(f"id {q['id']}: empty expect")
    if not (q.get("class") or "").strip():
        problems.append(f"id {q['id']}: empty class")
missing = set(skel) - seen
if missing:
    problems.append(f"{len(missing)} questions never came back: {sorted(missing)[:12]}")

# no duplicates against bank A or B
used = set()
for f in ("eval_bank_100_2026-08-16.json", "eval_bank_B_2026-08-23.json"):
    for x in json.load(open(f"{REPO}/{f}"))["questions"]:
        used.add(x["q"].strip().lower())
# exact duplicates of bank A/B: seq lead-ins become context_only, solos are DROPPED (reported)
import re as _re
def _norm(t): return _re.sub(r'\W+', ' ', t.lower()).strip()
usedn = {_norm(u) for u in used}
dropped_ab, seen_solo = [], set()
kept = []
for q in qs:
    n = _norm(q["q"])
    if n in usedn and not q.get("context_only"):
        if q.get("seq"):
            q["context_only"] = True          # thread lead-in: keep for context, ungraded
        else:
            dropped_ab.append(q["id"]); continue
    if not q.get("seq"):
        if n in seen_solo:
            dropped_ab.append(q["id"]); continue
        seen_solo.add(n)
    kept.append(q)
qs = kept
# tier-2 ids move to 7001+ so they can never collide with tier-1 (6001+)
for q in qs:
    if q["tier"] == 2:
        q["id"] += 500

if problems:
    print("VALIDATION FAILED:")
    for p in problems[:25]:
        print("  ·", p)
    sys.exit(1)

# ---- order: by class, threads contiguous and in seq_pos order ----
groups = defaultdict(list)
for q in qs:
    groups[q["seq"] or f"solo-{q['id']}"].append(q)
for k in groups:
    groups[k].sort(key=lambda q: (q.get("seq_pos") if q.get("seq_pos") is not None else 0, q["id"]))
ordered = []
for k in sorted(groups, key=lambda k: (groups[k][0]["class"], groups[k][0]["id"])):
    ordered += groups[k]

bank = {"name": "eval_bank_C", "built": "2026-08-23", "ticket": "#124",
        "rules": ["organic member sentences only, never reworded", "locked once written",
                  "no duplicates with bank A or B",
                  "tier 1 = asked to Millie, whole conversations kept in order",
                  "tier 2 = asked to the community (Millie is not announced yet, so her own inbox "
                  "is thin in recommendations and expertise)"],
        "questions": ordered}
json.dump(bank, open(OUT, "w"), indent=1, ensure_ascii=False)

seqs = {q["seq"] for q in ordered if q["seq"]}
print(f"WROTE {OUT} · dropped as A/B or intra-bank duplicates: {len(dropped_ab)} {dropped_ab[:12]}")
print(f"  questions {len(ordered)} · tier1 {sum(1 for q in ordered if q['tier']==1)} "
      f"· tier2 {sum(1 for q in ordered if q['tier']==2)} · multi-turn threads {len(seqs)}")
print(f"  classes: {Counter(q['class'] for q in ordered).most_common()}")
print(f"  RECOMMENDATION {sum(1 for q in ordered if q['class']=='RECOMMENDATION')} · "
      f"EXPERTISE {sum(1 for q in ordered if q['class']=='EXPERTISE')} · "
      f"FOLLOWUP {sum(1 for q in ordered if q['class']=='FOLLOWUP')}")
print(f"  last-24h asks: {sum(1 for q in ordered if q['first_asked'] >= '2026-08-22' and q['tier']==1)}")
