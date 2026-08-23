#!/usr/bin/env python3
"""Assemble bank C from the two harvests. Emits the bank skeleton — every field except `expect`,
which is written afterwards from the tickets, ACs, rulings and live data (never invented).

ids: 6000+ tier 1 (asked to Millie), 6500+ tier 2 (asked to the community).
"""
import json, os, re
from collections import defaultdict

REPO = "/Users/Born/Scorecard"
SCR = "/private/tmp/claude-501/-Users-Born-Scorecard/d7c6c01a-5cbb-42e4-83d3-d31df36f5d0d/scratchpad"
T2_PER_CLASS = 50

t1 = json.load(open(f"{SCR}/bank_c_tier1.json"))
t2 = json.load(open(f"{SCR}/bank_c_tier2.json"))

# ---------- tier 1: whole conversations, in order ----------
convs = defaultdict(list)
for r in t1:
    convs[r["conv"]].append(r)
qs, nid = [], 6000
for cid in sorted(convs):
    turns = sorted(convs[cid], key=lambda r: r["pos"])
    seq = f"c{cid}" if len(turns) > 1 else None
    for r in turns:
        nid += 1
        qs.append({"id": nid, "class": None, "q": r["q"], "expect": None, "soft": None,
                   "asker": None, "first_asked": (r["asked_at"] or "")[:10], "seq": seq,
                   "seq_pos": r["pos"] if seq else None,
                   "tier": 1, "src": "olivia_messages", "src_id": r["msg_id"],
                   "context_only": not r["is_new"], "regression": False, "retired": False})

# ---------- tier 2: diverse pick per class ----------
STOP = set("the a an is are do does did any anyone someone what which who how for with and or to of "
           "in on at my our your this that has have had can could would should i we you it be been "
           "here there from about your you're im i'm".split())


def topic(q):
    w = [x for x in re.findall(r"[a-zA-Z][a-zA-Z'&/-]{2,}", q.lower()) if x not in STOP]
    return w[0] if w else "misc"


def pick(cls, n):
    pool = sorted([p for p in t2 if p["cls"] == cls],
                  key=lambda p: (p.get("asked_at") or ""), reverse=True)
    buckets = defaultdict(list)
    for p in pool:
        buckets[topic(p["q"])].append(p)
    out, order = [], sorted(buckets, key=lambda k: -len(buckets[k]))
    while len(out) < n and any(buckets[k] for k in order):
        for k in order:                       # round-robin across topics = diversity, not one theme
            if buckets[k] and len(out) < n:
                out.append(buckets[k].pop(0))
    return out


nid = 6500
for cls in ("RECOMMENDATION", "EXPERTISE"):
    for p in pick(cls, T2_PER_CLASS):
        nid += 1
        qs.append({"id": nid, "class": cls, "q": p["q"], "expect": None, "soft": None,
                   "asker": None, "first_asked": (p.get("asked_at") or "")[:10], "seq": None,
                   "seq_pos": None, "tier": 2, "src": p["source"], "src_id": p["src_id"],
                   "chat": p.get("chat"), "access": p.get("access"),
                   "context_only": False, "regression": False, "retired": False})

bank = {"name": "eval_bank_C", "built": "2026-08-23", "ticket": "#124",
        "rules": ["organic member sentences only, never reworded",
                  "locked once written", "no duplicates with bank A or B",
                  "tier 1 = asked to Millie, whole conversations kept in order",
                  "tier 2 = asked to the community (Millie is not announced yet, so her own inbox is "
                  "thin in recommendations and expertise)"],
        "questions": qs}
json.dump(bank, open(f"{SCR}/eval_bank_C_skeleton.json", "w"), indent=1, ensure_ascii=False)

t1q = [q for q in qs if q["tier"] == 1]
print(f"total {len(qs)} · tier1 {len(t1q)} (context-only {sum(1 for q in t1q if q['context_only'])}) "
      f"· tier2 {sum(1 for q in qs if q['tier']==2)}")
print(f"multi-turn seqs: {len({q['seq'] for q in qs if q['seq']})}")
print(f"asks from the last 24h: {sum(1 for q in qs if q['first_asked'] >= '2026-08-22' and q['tier']==1)}")
