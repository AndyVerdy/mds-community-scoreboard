#!/usr/bin/env python3
"""Bank C tier 2 — real RECOMMENDATION and EXPERTISE questions members asked the community.

Millie has not been announced, so her own inbox is thin in exactly the two areas that cost the most
trust when they fail. These are the same members asking the same kinds of questions, in their own
words, in the chats and on Facebook. Sentences are taken VERBATIM — never reworded.

Writes scratchpad/bank_c_tier2.json.
"""
import json, os, re, subprocess, importlib.util

REPO = "/Users/Born/Scorecard"
OUT = os.environ.get("BANKC_OUT", "/private/tmp/claude-501/-Users-Born-Scorecard/"
                     "d7c6c01a-5cbb-42e4-83d3-d31df36f5d0d/scratchpad")
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/"

spec = importlib.util.spec_from_file_location("g", f"{REPO}/scripts/olivia_leak_gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
KEY = g.load_key()

REC = re.compile(r'(?i)\b(recommend\w*|suggestions?|any good|worth it|which (one|of these)|'
                 r'looking for a|need a good|best (tool|agency|app|service|freelancer|3pl|lawyer|ca|va))\b')
EXP = re.compile(r'(?i)\b(anyone (know|here|used|tried|worked|done|have experience)|'
                 r'who (here|has|knows|is good|can help|does)|experience with|expert in|'
                 r'has anyone|does anyone|familiar with|dealt with)\b')
QSHAPE = re.compile(r'(?i)(\?|^(does|do|has|have|is|are|can|could|would|who|what|which|any|anyone|'
                    r'looking for|need|recommend))')
URLONLY = re.compile(r'^\s*https?://\S+\s*$')


def get(path):
    out = subprocess.run(["curl", "-s", BASE + path, "-H", "Accept-Profile: digest",
                          "-H", "apikey: " + KEY, "-H", "Authorization: Bearer " + KEY],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def usable(b):
    b = (b or "").strip()
    if not (25 <= len(b) <= 320):           # long enough to grade, short enough to be one ask
        return False
    if URLONLY.match(b) or b.count("\n") > 4:
        return False
    if not QSHAPE.search(b):
        return False
    return True


def main():
    seen, picked, last = set(), [], 0
    while True:
        rows = get("content_items?select=id,kind,source,body,occurred_at,access_rule,meta,url"
                   f"&source=in.(wa_message,fb_post,fb_comment)&kind=in.(text,post,comment)"
                   f"&id=gt.{last}&order=id.asc&limit=1000")
        if not rows:
            break
        last = rows[-1]["id"]
        for r in rows:
            b = (r["body"] or "").strip()
            if not usable(b):
                continue
            k = re.sub(r'\W+', ' ', b.lower()).strip()[:120]
            if k in seen:
                continue
            kind = "RECOMMENDATION" if REC.search(b) else ("EXPERTISE" if EXP.search(b) else None)
            if not kind:
                continue
            seen.add(k)
            ar = r.get("access_rule") or {}
            picked.append({"src_id": r["id"], "cls": kind, "q": b,
                           "asked_at": r.get("occurred_at"), "source": r["source"],
                           "chat": ar.get("chat"), "access": ar.get("type"), "url": r.get("url")})
        if len(rows) < 1000:
            break

    # never duplicate an existing bank
    used = set()
    for f in ("eval_bank_100_2026-08-16.json", "eval_bank_B_2026-08-23.json"):
        for q in json.load(open(f"{REPO}/{f}"))["questions"]:
            used.add(q["q"].strip().lower())
    picked = [p for p in picked if p["q"].strip().lower() not in used]

    os.makedirs(OUT, exist_ok=True)
    json.dump(picked, open(f"{OUT}/bank_c_tier2.json", "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(f"tier-2 candidates {len(picked)} · "
          f"{Counter(p['cls'] for p in picked).most_common()}")
    print("by source:", Counter(p["source"] for p in picked).most_common())
    print("restricted-chat sourced:", sum(1 for p in picked if p["access"] == "chat_member"))


if __name__ == "__main__":
    main()
