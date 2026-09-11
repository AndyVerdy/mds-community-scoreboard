#!/usr/bin/env python3
"""#204 — an exact revenue figure never rides as a bare fact next to a person (STAGING only).

What happened, twice: a real member turn on 2026-09-04 (olivia_messages 62689) and #190's exam
question 5043 both produced "I did find Joshua Asquith, a UK beauty brand owner (£14.5M/yr)".

The figure itself is legitimately quotable - it is in MDS's OWN public welcome post
(content_items 133718, 2026-07-29, "a UK beauty brand doing £14.5M a year"). What the rulebook
forbids is the SHAPE: OLIVIA_SHAREABLE_FIELDS.md allows such a figure "ONLY as an attributed quote
with its link, paired with our band, never in Olivia's own voice". A bare parenthetical is exactly
the forbidden form, and the leak gate cannot see it - the number arrived as content, so no
retrieval rule was broken. The broken rule is a rendering rule, so the fix is in rendering.

Two layers, because a prompt rule alone is a hope (feedback_code_beats_prompt_rules):
  1. Build Prompt - the standing instruction: bands are ours, figures are quotes.
  2. Format Reply - a deterministic strip of the one shape that actually shipped: a parenthetical
     that is NOTHING BUT a money amount, on a line carrying no source link. Prose figures with a
     cited source (booth costs $1,158) are untouched, and so is any parenthetical with a link.
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


PROMPT_RULE = (
    "'HONESTY: Use ONLY the data provided in this message. Never guess, invent or infer facts, "
    "names, numbers, dates or links. If the answer is not here, say so plainly and, when useful, "
    "point them where they could find it.',"
)
PROMPT_RULE_NEW = PROMPT_RULE + (
    "\n  'REVENUE IS A BAND, NEVER A FIGURE (#204): never write an exact revenue or sales amount "
    "next to a member as a fact - not as a parenthetical, not as an aside, not \"doing X a year\". "
    "What we hold per member is the BAND (1-5M / 5-10M / 10-20M / 20M+); say the band. If a member "
    "or MDS POSTED a figure publicly and that post is in the evidence below, you may QUOTE it - in "
    "their words, named, with its link - never in your own voice and never as a bare number after "
    "their name.',"
)

FORMAT_ANCHOR = "const im = text.match(/\\[SEND_IMAGE:\\s*([0-9]{6,25})\\s*\\]/i);"
FORMAT_NEW = FORMAT_ANCHOR + """
// #204 (2026-09-11) — a money amount in a bare parenthetical next to a person is the one shape
// that actually leaked: "Joshua Asquith, a UK beauty brand owner (£14.5M/yr)" reached a member on
// 2026-09-04 and again in #190's exam. The figure was public, but the rulebook allows it only as
// an attributed quote WITH its link, paired with our band. Strip only that shape, and only when
// the line carries no source link — a cited figure, and any figure in ordinary prose, is untouched.
text = text.replace(
  /\\s*[\\(\\[]\\s*(?:approx\\.?|about|around|roughly|~)?\\s*[$£€]\\s?\\d[\\d.,]*\\s*(?:k|m|mm|bn|b)?\\+?\\s*(?:\\/\\s*(?:yr|year|mo|month)|\\s*(?:a|per)\\s+(?:yr|year|mo|month)|\\s+in\\s+(?:annual\\s+)?(?:revenue|sales))?\\s*[\\)\\]]/gi,
  function (m, off, s) {
    const ls = s.lastIndexOf(String.fromCharCode(10), off) + 1;
    let le = s.indexOf(String.fromCharCode(10), off);
    if (le < 0) { le = s.length; }
    return /https?:\\/\\//.test(s.slice(ls, le)) ? m : '';
  });"""


def patch(node, edits, label):
    code = node["parameters"]["jsCode"]
    before = len(code)
    for old, new in edits:
        n = code.count(old)
        if n != 1:
            print(f"ABORT [{label}]: anchor x{n}, expected 1:\n  {old[:110]}…", file=sys.stderr)
            sys.exit(2)
        code = code.replace(old, new)
    node["parameters"]["jsCode"] = code
    print(f"{label}: {before} -> {len(code)} chars")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    patch(next(n for n in nodes if n["name"] == "Build Prompt"), [(PROMPT_RULE, PROMPT_RULE_NEW)], "Build Prompt")
    patch(next(n for n in nodes if n["name"] == "Format Reply"), [(FORMAT_ANCHOR, FORMAT_NEW)], "Format Reply")
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
