#!/usr/bin/env python3
"""#190 lap 3 — four remaining failures, fixed IN THEIR OWN LANE (STAGING only).

Lap 2 put seven rules in the shared STYLE block and four of them did not move the answer: a lane
with its own MODE rules follows those, and STYLE loses. So each rule here goes in the lane that
actually answers that question shape, and the one that is really an evidence problem gets more
evidence rather than more words.

  5011  "how many members live within 2 hours of 32250" -> refused outright. The MATCH lane already
        holds the whole Florida list and a rule telling it not to present far-away cities as nearby;
        faced with a radius it could not compute, it gave nothing at all. Rule goes in the match
        lane: no drive times, then the members in that city and its metro, then the wider offer.
  5068  "tell me about hector the ppc tool" -> credited to the wrong person. partner_lookup_v2
        RETURNS `web_people` (who the partner says runs it). Rule goes in the partners lane: people
        come from that field or not at all.
  5098  "is it true what they said..." with no antecedent -> answered anyway. Rule goes in the two
        search lanes, which is where a bare follow-up lands.
  5027  "bullet updates about the AI and DTC channels" -> most of the week's topics missing. This is
        not a wording problem: the chat block renders 12 rows at 400 chars. It gets 20 at 700.
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
STAGING_ID = "bqHstPDi84uOhTCJ"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", "X-N8N-API-KEY: " + KEY,
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


MATCH_ANCHOR = "    'RULES:',\n    '- THE LIST BELOW matches the FILTERS the system could apply"
MATCH_NEW = ("    'RULES:',\n"
             "    '- A DISTANCE ASK (#190 Q5011: \"within 2 hours of 32250\", \"near me\", \"x miles from\") IS STILL ANSWERED. "
             "There are no drive times and no radius - say that in one clause, then NAME the members in that place and its real "
             "metro from the list below, and offer the wider state list. Refusing outright is the wrong answer: they asked who is "
             "near them, and the list below knows who is in those cities. Never invent a radius count.',\n"
             "    '- THE LIST BELOW matches the FILTERS the system could apply")

PARTNERS_ANCHOR = "    '- Asked for a TOPIC (\"deals for 3PL\"): pick the 2-4 most relevant partners, one short line each (what they do + the offer). Never dump the whole list.',"
PARTNERS_NEW = (PARTNERS_ANCHOR + "\n"
                "    '- WHO RUNS IT COMES FROM web_people (#190 Q5068): name a founder, owner or person behind a partner ONLY from "
                "that partner row\\u2019s own people field. A name you remember from a call, a session or another partner is a "
                "different person - Hector was credited to the wrong founder that way. No people on the row means no name: say the "
                "partner page has the contact.',")

SEARCH_ANCHORS = [
    ("plan.period === 'search_all'", "search_all"),
    ("plan.period === 'search_chat'", "search_chat"),
]

# 5027 — one anchor covering the whole chat block, so the 400-char slice can only match this one
CHAT_BUDGET_OLD = """  let chatBlock = chatRows.slice(0, 12).map(function (r) {
    const cn = (r.meta && r.meta.chat_name) || 'a chat';
    let t = String(r.tl_dr || r.body).replace(/\\s+/g, ' ').trim();
    if (t.length > 400) { t = t.slice(0, 400) + '\u2026'; }"""
CHAT_BUDGET_NEW = """  // #190 Q5027 (2026-09-11): "bullet updates about the AI and DTC channels" missed most of the
  // week's topics - not a wording problem, an evidence one: 12 digest rows at 400 chars each is
  // about a third of a busy week. 20 at 700 costs a few thousand tokens and carries the topics.
  let chatBlock = chatRows.slice(0, 20).map(function (r) {
    const cn = (r.meta && r.meta.chat_name) || 'a chat';
    let t = String(r.tl_dr || r.body).replace(/\\s+/g, ' ').trim();
    if (t.length > 700) { t = t.slice(0, 700) + '\u2026'; }"""
CHAT_BUDGET = [(CHAT_BUDGET_OLD, CHAT_BUDGET_NEW)]


def patch(node, edits, label, allow_multi=False):
    code = node["parameters"]["jsCode"]
    before = len(code)
    for old, new in edits:
        n = code.count(old)
        if n != 1 and not allow_multi:
            print(f"ABORT [{label}]: anchor x{n}, expected 1:\n  {old[:110]}…", file=sys.stderr)
            sys.exit(2)
        if n == 0:
            print(f"ABORT [{label}]: anchor missing:\n  {old[:110]}…", file=sys.stderr)
            sys.exit(2)
        code = code.replace(old, new, 1)
    node["parameters"]["jsCode"] = code
    print(f"{label}: {before} -> {len(code)} chars ({len(edits)} edits)")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    bp = next(n for n in nodes if n["name"] == "Build Prompt")
    code = bp["parameters"]["jsCode"]

    edits = [(MATCH_ANCHOR, MATCH_NEW), (PARTNERS_ANCHOR, PARTNERS_NEW)]
    # 5098 — the referent rule, in the modeLines the two search lanes share
    search_anchor = ("    'If none of it actually answers their question, say so plainly.'];")
    search_new = ("    'If none of it actually answers their question, say so plainly.',\n"
                  "    'NO ANTECEDENT, NO ANSWER (#190 Q5098): if \\'they\\', \\'it\\', \\'that one\\' or \\'the call\\' in their "
                  "message has nothing to point at here or in the conversation so far, ask which one in a single line instead of "
                  "picking a likely source - they asked about something specific and you would be answering about something else.'];")
    if code.count(search_anchor) != 1:
        print(f"ABORT: search modeLines anchor x{code.count(search_anchor)}", file=sys.stderr)
        return 2
    edits.append((search_anchor, search_new))

    patch(bp, edits + CHAT_BUDGET, "Build Prompt")
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
