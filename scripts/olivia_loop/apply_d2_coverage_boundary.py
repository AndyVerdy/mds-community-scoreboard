#!/usr/bin/env python3
"""D2 - a gap is reported without the boundary that explains it. STAGING (bqHstPDi84uOhTCJ).

Root cause is NOT the model generalising. The Answer Seed carries a stale pre-#70 rule
that says, in as many words, that transcripts do not exist:

  'RECORDINGS & VIDEOS: You cannot search INSIDE call recordings or videos yet - that
   capability is coming. ...'

#70 shipped transcripts in August 2026 and added a contradicting rule 38 lines later
('CALLS (#70): 2026 calls carry full transcripts'). The stale rule was never removed, so
the Answer Seed contradicts itself and she quoted the false half almost verbatim:
"full transcripts aren't something I have access to (that capability isn't live yet)".

Measured coverage, 2026-08-16 - two real boundaries, both confirmed:
  1. Nothing before 2026-01-05  -> 872 of 1,033 videos, zero transcripts (Zoom starts there)
  2. No in-person formats       -> Summit 0/18, Mastermind 0/23, Chapter Event 2/13 in 2026
  Virtual 2026 calls: Expert 5/5, Mogul 23/28, Channel 29/41.

Andy's ruling: the boundary must travel with the gap, for videos AND for Facebook. Her
Aug 14 answer about the Amazon Ranking Mastery call (2025-10-03, genuinely no transcript)
was CORRECT - the explanation was not.

Two edits:
  1. Replace the stale RECORDINGS & VIDEOS rule with the true coverage boundary.
  2. Add a FRESHNESS rule so a recency answer carries its sync cadence.

NO APOSTROPHES in inserted text - the rules live in single-quoted JS strings.
Idempotent: asserts the anchor appears exactly once, aborts without writing otherwise.
"""
import json
import subprocess
import sys

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
NODE = "Answer Seed"
MARK = "COVERAGE BOUNDARY (D2)"


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
        sys.exit(f"empty response from {method} {path}: {r.stderr[:300]}")
    return json.loads(r.stdout)


STALE = (
    "  'RECORDINGS & VIDEOS: You cannot search INSIDE call recordings or videos yet - that "
    "capability is coming. BUT announcements, topics, dates and recaps of calls (Mogul Calls, "
    "Expert Calls, webinars) DO live in the chats and Facebook posts provided below - ANSWER "
    "those from the data like any other question (what was the call about, who ran it, when). "
    "Only refuse when they want the recording CONTENT itself (a replay, what was said "
    "minute-to-minute, the video file) - then say plainly you cannot look inside recordings yet, "
    "never implying you searched them.'"
)

REPLACEMENT = (
    "  'RECORDINGS & VIDEOS - COVERAGE BOUNDARY (D2). You CAN search inside call transcripts, but "
    "only where they exist, and the limits are specific: transcripts cover VIRTUAL calls from 2026 "
    "onward - Mogul Calls, Channel Calls, Expert Calls. There are NO transcripts for anything "
    "published before January 2026 (872 of 1,033 videos), and NONE for in-person recordings - "
    "Summits, Masterminds and chapter events. NEVER say the capability is coming, not live, or not "
    "available yet - that is false and it tells the member to stop asking. When a specific call has "
    "no transcript, say WHICH boundary it fell outside and what you can still do: the video link, "
    "what the call covered, and an offer to search the calls that ARE transcribed. Announcements, "
    "topics, dates and recaps of calls also live in the chats and Facebook posts below - answer "
    "those from the data like any other question. Never imply you searched a transcript you do not "
    "have.',"          # <- TRAILING COMMA. Its absence broke staging on 2026-08-16: two adjacent
                        #    JS string literals is a syntax error, the node threw on every LLM turn,
                        #    and only `reset` (which never reaches this node) kept answering.
)

FRESHNESS = (
    "\n  'FRESHNESS TRAVELS WITH RECENCY (D2). Sources refresh on different clocks and a bare date "
    "reads as broken. WhatsApp is current. Facebook syncs periodically rather than continuously, so "
    "whenever you give a newest-post date or say nothing recent was found on Facebook, say that it "
    "syncs periodically and give the date you actually hold. Call transcripts land on a weekly job. "
    "State the cadence in one short clause - never apologise for it, never speculate about when the "
    "next sync runs, and NEVER describe internal data problems, placeholder rows or test entries to "
    "a member.',"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf.get("nodes") or sys.exit("no nodes in staging")
    node = next((n for n in nodes if n.get("name") == NODE), None)
    if node is None:
        sys.exit(f"node {NODE!r} not found")

    code = node["parameters"]["jsCode"]

    if MARK in code:
        print("already applied - no change")
        return 0

    if code.count(STALE) != 1:
        sys.exit(f"stale RECORDINGS rule found {code.count(STALE)} times, expected 1 - ABORT")

    new = code.replace(STALE, REPLACEMENT + FRESHNESS, 1)

    # HARD PRECONDITION: the edited body must PARSE before it is written.
    # 2026-08-16: a missing comma between two string literals shipped to staging and every
    # LLM turn threw for ~15 minutes. The apostrophe check that stood here was theatre --
    # it inspected quotes and never asked whether the result was valid JavaScript.
    # `node --check` answers that in one second. It is not optional.
    import os
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write("function __seed(){\n" + new + "\n}\n")
        probe = fh.name
    chk = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
    os.unlink(probe)
    if chk.returncode != 0:
        sys.exit("ABORT - edited Answer Seed does not parse, nothing written:\n"
                 + chk.stderr[:800])
    print("node --check: PASS")

    node["parameters"]["jsCode"] = new
    payload = {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings", {})}
    res = api("PUT", f"/workflows/{STAGING_ID}", payload)
    if not res.get("id"):
        sys.exit(f"PUT failed: {str(res)[:400]}")

    check = api("GET", f"/workflows/{STAGING_ID}")
    cnode = next(n for n in check["nodes"] if n["name"] == NODE)
    got = cnode["parameters"]["jsCode"]
    ok = MARK in got and "that capability is coming" not in got
    print(f"staging updated · coverage rule present = {MARK in got} · "
          f"stale claim gone = {'that capability is coming' not in got}")
    print(f"Answer Seed {len(code)} -> {len(got)} chars")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
