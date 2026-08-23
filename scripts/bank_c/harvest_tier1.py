#!/usr/bin/env python3
"""Bank C tier 1 — every gradeable organic ask members sent MILLIE that bank A/B never used,
kept inside its original conversation.

Writes scratchpad/bank_c_tier1.json: one record per ask with its conversation id and position,
so the builder can emit `seq` groups in order. Never rewords a member's sentence.
"""
import json, os, re, subprocess, importlib.util, datetime as dt

REPO = "/Users/Born/Scorecard"
OUT = os.environ.get("BANKC_OUT", "/private/tmp/claude-501/-Users-Born-Scorecard/"
                     "d7c6c01a-5cbb-42e4-83d3-d31df36f5d0d/scratchpad")
PROBE = "17866578153"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/"
GAP_SEC = 600          # same phone, <=10 min apart == one conversation

spec = importlib.util.spec_from_file_location("g", f"{REPO}/scripts/olivia_leak_gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
KEY = g.load_key()


def get(path):
    out = subprocess.run(["curl", "-s", BASE + path, "-H", "Accept-Profile: digest",
                          "-H", "apikey: " + KEY, "-H", "Authorization: Bearer " + KEY],
                         capture_output=True, text=True).stdout
    return json.loads(out)


JUNK = re.compile(r'(?i)^(hi|hello|hey|ok|okay|yes|no|yep|nope|sure|thanks?|thank you|ty|got it|'
                  r'👍|🙏|😂|k)[\s!.,]*$')


def ungradeable(t):
    t = (t or "").strip()
    if len(t) < 8 or JUNK.match(t):
        return True
    if not re.search(r'[a-zA-Z]{3}', t):        # emoji / numbers only
        return True
    return False


def main():
    rows, last = [], 0
    while True:
        b = get(f"olivia_messages?select=id,phone,text,created_at,route&role=eq.member"
                f"&phone=neq.{PROBE}&id=gt.{last}&order=id.asc&limit=1000")
        if not b:
            break
        rows += b; last = b[-1]["id"]
        if len(b) < 1000:
            break

    used = set()
    for f in ("eval_bank_100_2026-08-16.json", "eval_bank_B_2026-08-23.json"):
        for q in json.load(open(f"{REPO}/{f}"))["questions"]:
            used.add(q["q"].strip().lower())

    # conversations first, so a follow-up keeps its lead-in even when the lead-in is a bank A/B question
    byp = {}
    for r in sorted(rows, key=lambda r: r["id"]):
        byp.setdefault(r["phone"], []).append(r)
    convs = []
    for p, rs in byp.items():
        cur = [rs[0]]
        for a, b in zip(rs, rs[1:]):
            t1 = dt.datetime.fromisoformat(a["created_at"].replace("Z", "+00:00"))
            t2 = dt.datetime.fromisoformat(b["created_at"].replace("Z", "+00:00"))
            if (t2 - t1).total_seconds() <= GAP_SEC:
                cur.append(b)
            else:
                convs.append(cur)          # a NEW list every time -- appending `cur` and then
                cur = [b]                  # clearing it aliases every conversation to the last one
        convs.append(cur)

    out, cid = [], 0
    for c in convs:
        turns = [r for r in c if not ungradeable(r["text"])]
        if not turns:
            continue
        fresh = [r for r in turns if r["text"].strip().lower() not in used]
        if not fresh:                      # nothing new in this thread
            continue
        cid += 1
        for pos, r in enumerate(turns):    # keep the WHOLE thread, so context survives
            out.append({"conv": cid, "pos": pos, "n_turns": len(turns),
                        "msg_id": r["id"], "phone": r["phone"], "q": r["text"].strip(),
                        "asked_at": r["created_at"],
                        "is_new": r["text"].strip().lower() not in used})
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(f"{OUT}/bank_c_tier1.json", "w"), indent=1, ensure_ascii=False)
    multi = len({r["conv"] for r in out if r["n_turns"] > 1})
    print(f"conversations kept {cid} (multi-turn {multi}) · asks {len(out)} · "
          f"new {sum(1 for r in out if r['is_new'])} · context-only {sum(1 for r in out if not r['is_new'])}")
    last24 = [r for r in out if r["asked_at"] >= "2026-08-22T17:00:00" and r["is_new"]]
    print(f"new asks in the last 24h: {len(last24)}")


if __name__ == "__main__":
    main()
