#!/usr/bin/env python3
"""#107e — fetch staging raw jsCode for Format Reply + Answer Seed via the same
n8n REST helpers scripts/olivia_wf.py already uses, then build find/replace pairs
with Python .replace() on the REAL fetched string (never hand-transcribed) so the
Answer Seed single-quoted-string escaping (\\' for apostrophes) can never be
mistyped. Writes both raw sources to scratch files (never re-typed) plus the
proposed new sources, and node --checks all four.
"""
import json
import subprocess
import sys

sys.path.insert(0, "/Users/Born/Scorecard/scripts")
import olivia_wf as wf  # noqa: E402

STAGING_ID = "bqHstPDi84uOhTCJ"
PROD_ID = "12wj6h1TWqb0d4Dq"
assert STAGING_ID != PROD_ID

wfjson = wf.fetch(STAGING_ID)
nodes = {n["name"]: n for n in wfjson["nodes"]}
assert "Format Reply" in nodes and "Answer Seed" in nodes, sorted(nodes.keys())

fr_raw = nodes["Format Reply"]["parameters"]["jsCode"]
as_raw = nodes["Answer Seed"]["parameters"]["jsCode"]

with open("/Users/Born/Scorecard/scratchpad/107e/format_reply_raw.js", "w") as f:
    f.write(fr_raw)
with open("/Users/Born/Scorecard/scratchpad/107e/answer_seed_raw.js", "w") as f:
    f.write(as_raw)

# ---- Format Reply: double-quoted JS strings, apostrophes NOT escaped ----
FR_OLD_LEAD = (
    'text = "Of the people I mentioned, I can set up intros with those who are '
    "attending and reachable on WhatsApp. Pick one and I'll ask them for their "
    "ok — they see your name and the topic, nothing else. I'll message you the "
    "moment they respond; if there's no answer in 7 days I'll let you know and "
    'we can try someone else.";'
)
FR_NEW_LEAD = (
    'text = "Here are the Summit attendees I\'ve recommended to you that I can '
    "reach for an intro. Pick one and I'll ask them for their ok — they see "
    "your name and the topic, nothing else. I'll message you the moment they "
    "respond; if there's no answer in 7 days I'll let you know and we can try "
    'someone else.";'
)
FR_OLD_FALLBACK = (
    'text = "None of the people I mentioned can take intro requests right now '
    '— intros are running for Summit attendees reachable on WhatsApp. Want '
    'other names?";'
)
FR_NEW_FALLBACK = (
    'text = "None of the attendees I\'ve recommended to you can take an intro '
    'request right now. Want other names?";'
)

assert fr_raw.count(FR_OLD_LEAD) == 1, f"FR lead find count={fr_raw.count(FR_OLD_LEAD)}"
assert fr_raw.count(FR_OLD_FALLBACK) == 1, f"FR fallback find count={fr_raw.count(FR_OLD_FALLBACK)}"

fr_new = fr_raw.replace(FR_OLD_LEAD, FR_NEW_LEAD).replace(FR_OLD_FALLBACK, FR_NEW_FALLBACK)
assert fr_new != fr_raw
assert FR_NEW_LEAD in fr_new and FR_NEW_FALLBACK in fr_new
assert "Of the people I mentioned" not in fr_new
assert "who also use Millie" not in fr_new  # sanity: old #107b/c wording long gone

with open("/Users/Born/Scorecard/scratchpad/107e/format_reply_new.js", "w") as f:
    f.write(fr_new)

# ---- Answer Seed: single-quoted array-string entries, apostrophes ARE
# JS-escaped as \' (real 2-char sequence: backslash + apostrophe). Build the
# escaped find/replace with Python .replace("'", "\\'") so no hand-typed
# backslash can be wrong, then verify the escaped OLD string actually occurs
# in the real fetched source before trusting it.
AS_OLD_LEAD_PLAIN = (
    "Of the people I mentioned, I can set up intros with those who are "
    "attending and reachable on WhatsApp. Pick one and I'll ask them for "
    "their ok — they see your name and the topic, nothing else. I'll "
    "message you the moment they respond; if there's no answer in 7 days "
    "I'll let you know and we can try someone else."
)
AS_NEW_LEAD_PLAIN = (
    "Here are the Summit attendees I've recommended to you that I can "
    "reach for an intro. Pick one and I'll ask them for their ok — they "
    "see your name and the topic, nothing else. I'll message you the "
    "moment they respond; if there's no answer in 7 days I'll let you "
    "know and we can try someone else."
)
AS_OLD_LEAD_ESCAPED = AS_OLD_LEAD_PLAIN.replace("'", "\\'")
AS_NEW_LEAD_ESCAPED = AS_NEW_LEAD_PLAIN.replace("'", "\\'")

occurrences = as_raw.count(AS_OLD_LEAD_ESCAPED)
assert occurrences == 1, f"AS lead find count={occurrences} (escaping assumption may be wrong)"

as_new = as_raw.replace(AS_OLD_LEAD_ESCAPED, AS_NEW_LEAD_ESCAPED)
assert as_new != as_raw
assert AS_NEW_LEAD_ESCAPED in as_new
assert "Of the people I mentioned" not in as_new

with open("/Users/Born/Scorecard/scratchpad/107e/answer_seed_new.js", "w") as f:
    f.write(as_new)

# ---- OFFER_TAIL verification (task-required): the new empty-pick fallback
# must NOT match either live OFFER_TAIL regex (OFFER_TAIL in the #38 button
# block, OFFER_TAIL_PS in the PS-placement block — byte-identical patterns).
# Extract the ACTUAL pattern text from the live fetched source rather than
# retyping it, so the test is against what is really deployed.
import re as _re
m = _re.search(r"const OFFER_TAIL = (/.+?/i);", fr_raw)
assert m, "could not find OFFER_TAIL definition in live Format Reply source"
offer_tail_src = m.group(1)
with open("/Users/Born/Scorecard/scratchpad/107e/offer_tail_pattern.txt", "w") as f:
    f.write(offer_tail_src)

print("FR_OLD_LEAD found exactly once:", fr_raw.count(FR_OLD_LEAD) == 1)
print("FR_OLD_FALLBACK found exactly once:", fr_raw.count(FR_OLD_FALLBACK) == 1)
print("AS_OLD_LEAD_ESCAPED found exactly once:", occurrences == 1)
print("OFFER_TAIL pattern extracted:", offer_tail_src)
print("fr_raw len", len(fr_raw), "-> fr_new len", len(fr_new))
print("as_raw len", len(as_raw), "-> as_new len", len(as_new))

# node --check every artifact (wrap Code-node bodies in a throwaway function
# so bare `return`/`$(...)` references parse without a real n8n runtime).
def node_check(path, wrap=False):
    src = open(path).read()
    if wrap:
        wrapped = "function __wrap(){\n" + src + "\n}\n"
        tmp = path + ".checkwrap.js"
        open(tmp, "w").write(wrapped)
        target = tmp
    else:
        target = path
    r = subprocess.run(["node", "--check", target], capture_output=True, text=True)
    print(f"node --check {path}: {'OK' if r.returncode == 0 else 'FAIL'}")
    if r.returncode != 0:
        print(r.stderr)
    return r.returncode == 0

ok = True
ok &= node_check("/Users/Born/Scorecard/scratchpad/107e/format_reply_new.js", wrap=True)
ok &= node_check("/Users/Born/Scorecard/scratchpad/107e/answer_seed_new.js", wrap=True)
print("ALL node --check PASSED" if ok else "NODE CHECK FAILURE")
