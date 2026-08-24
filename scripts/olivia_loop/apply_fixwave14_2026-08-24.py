#!/usr/bin/env python3
"""Fixwave 14 — Andy's removed-member ruling, 2026-08-24.

"Past members should be findable. Past members have WA and FB history; they might be in videos
and so on. But you should not count them if someone asks for info about MDS members when they are
implying current members. This is also true for chapters — we can't count chapter revenue based on
current members." And then: "I don't want to disclose leave dates or reasons why he left."

So the rule is three-part, and only one part needed building:
  · FINDABLE — already true, and the bank C expects that demanded "no profile at all" for a
    removed member are WRONG against this ruling. Those three (6080/6272/6277) are expect errors,
    not defects.
  · NEVER COUNTED — already true, verified live before changing anything: member_count returns
    724 (current only, 519 removed records excluded) and chapter_info New York returns 99, which
    is exactly the current-member count for that chapter, so chapter revenue averages already run
    on current members only. No change made.
  · LEAVE DATE AND REASON NEVER DISCLOSED — the reason was already 🔴; the DATE was not.
    digest.member_card handed it out and answers read "joined Nov 2022, left Feb 2026". Blanked at
    source (the left_date column stays in the shape, always null) — done in SQL, this wave adds the
    model-side rule so she cannot reconstruct it from a farewell post or a thread instead.

  python3 scripts/olivia_loop/apply_fixwave14_2026-08-24.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="): return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)

BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")

def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None: cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code); tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")

def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    seed = nodes["Answer Seed"]; cs = seed["parameters"]["jsCode"]

    anchor = """  'THE CAPABILITY CARD IS A FIRST HELLO, NOT AN ANSWER."""
    rule = """  'A PAST MEMBER IS FINDABLE - WHEN AND WHY THEY LEFT IS NOT (Andy 2026-08-24). Someone who has left MDS is still a real person whose record we hold: give their card, their history, their posts, the calls and videos they are in, exactly as you would for anyone. What you never give is the DATE they left or the REASON. Do not say "left in March", do not work it out from a farewell post, a thread, or the last time they appear, and do not hint at it ("their membership ended around..."). "They are no longer an active member" is the entire statement, and if pushed, that is still the entire statement. And they are never COUNTED: when a question is about MDS members, a chapter, a niche or any average, the population is CURRENT members only.',
"""
    assert cs.count(anchor) == 1, f"anchor drift ({cs.count(anchor)}x)"
    cs = cs.replace(anchor, rule + anchor, 1)
    node_check(cs, "Answer Seed"); seed["parameters"]["jsCode"] = cs

    if dry:
        print("DRY RUN — anchor hit, node --check clean.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    assert "A PAST MEMBER IS FINDABLE" in {n["name"]: n for n in after["nodes"]}["Answer Seed"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
