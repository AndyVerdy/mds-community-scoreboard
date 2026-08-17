#!/usr/bin/env python3
"""F1 - she denies data she holds. Apply to STAGING (bqHstPDi84uOhTCJ).

The 100-question run, 2026-08-17:
  "How many females are in MDS?"
  -> "I don't have gender tracked as a census question, so I can't give you a
      breakdown ... it's just not something members report on our forms."

Live: male 521, female 89, unspecified 112 -- `community_info` returns gender_split
directly, and #81 shipped form_stats p_group_by=gender. She contradicted herself two
questions later by citing "Community census by gender" medians.

Why the existing rule missed it: the #81 CROSS-CUT STATS rule is scoped to "Breaking an
existing figure down by any of those". "How many females are in MDS?" is a STANDALONE
COUNT, not a breakdown, so it never triggered.

This is the THIRD instance of one class:
  D2  "transcripts aren't live yet"          -> 65 videos had them
  F3  "that schedule isn't connected to me"  -> true, but the same reflex
  F1  "gender isn't tracked"                 -> 610 members have it

So the fix is GENERAL, not another special case. Special-casing gender would leave the
next denial to be discovered by a member.

NO APOSTROPHES in inserted text - the rules are single-quoted JS strings.
`node --check` is a hard precondition (a missing comma broke staging on 2026-08-16).
"""
import json
import os
import subprocess
import sys
import tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
NODE = "Answer Seed"
MARK = "NEVER CLAIM WE DO NOT TRACK SOMETHING (F1)"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}",
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json",
           "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    if not r.stdout.strip():
        sys.exit(f"empty response from {method} {path}")
    return json.loads(r.stdout)


ANCHOR = ("  '- CROSS-CUT STATS (#81): form_stats slices by country, state, niche, rev_band, "
          "chapter AND gender. Breaking an existing figure down by any of those is a normal "
          "question - call form_stats with p_group_by instead of saying the split is not tracked. "
          "The tool suppresses small groups itself, so quote what it returns and nothing more.',")

NEW_RULE = (
    "\n  '- NEVER CLAIM WE DO NOT TRACK SOMETHING (F1). Saying MDS does not track, hold, collect "
    "or have a field for something is a statement about our systems, and you are repeatedly wrong "
    "about it - you have told members transcripts were not live (65 calls had them), that the call "
    "schedule was not connected, and that gender was not tracked (610 members have it). Before any "
    "sentence of that shape, CALL THE TOOL THAT WOULD HOLD IT. If the tool returns nothing, say "
    "the search came back empty for that question - which is a fact about this lookup. Never "
    "upgrade an empty result into a claim about what MDS collects, and never say a capability is "
    "coming, not live, or not connected. Demographic COUNTS are answerable, not only breakdowns: "
    "how many women, how many men, how many members in a country or band. community_info carries "
    "gender_split (male, female, unspecified) with its own self-reported caveat; form_stats slices "
    "any figure by gender, country, state, niche, rev_band or chapter. Quote the caveat the tool "
    "gives you and nothing more.',"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    node = next((n for n in nodes if n.get("name") == NODE), None)
    if node is None:
        sys.exit(f"node {NODE!r} not found")
    code = node["parameters"]["jsCode"]

    if MARK in code:
        print("already applied - no change")
        return 0
    if code.count(ANCHOR) != 1:
        sys.exit(f"anchor found {code.count(ANCHOR)} times, expected 1 - ABORT")

    new = code.replace(ANCHOR, ANCHOR + NEW_RULE, 1)

    if "'" in NEW_RULE.replace("\n  '- NEVER", "", 1).replace("nothing more.',", "", 1):
        sys.exit("ABORT: raw apostrophe in inserted text")

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write("function __seed(){\n" + new + "\n}\n")
        probe = fh.name
    chk = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
    os.unlink(probe)
    if chk.returncode != 0:
        sys.exit("ABORT - does not parse, nothing written:\n" + chk.stderr[:800])
    print("node --check: PASS")

    node["parameters"]["jsCode"] = new
    res = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings", {})})
    if not res.get("id"):
        sys.exit(f"PUT failed: {str(res)[:400]}")

    check = api("GET", f"/workflows/{STAGING_ID}")
    got = next(n for n in check["nodes"] if n["name"] == NODE)["parameters"]["jsCode"]
    print(f"staging updated · rule present = {MARK in got} · {len(code)} -> {len(got)} chars")
    return 0 if MARK in got else 1


if __name__ == "__main__":
    sys.exit(main())
