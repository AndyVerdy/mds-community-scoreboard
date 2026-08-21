#!/usr/bin/env python3
"""Purge stale "there are no transcripts" denials after the 2025 AAI load (2026-08-21).

Truth now: EVERY library video from 2025 and 2026 is transcript-searchable (Zoom
where it exists, AssemblyAI elsewhere — virtual AND in-person). Pre-2025: none.
Six stale strings across Build Prompt / Answer Seed / Build Verbatim Digest still
said otherwise (the capability-denial class, again). Exact-string replacements,
expected counts asserted, node --check per changed node, ONE bounce.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
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
    return json.loads(r.stdout)


EDITS = {
    "Build Prompt": [
        ("'- You CANNOT see inside any recording — there are no transcripts. "
         "For \"what did X say about Y\", say plainly you cannot search inside "
         "recordings yet, point them at the video, and never paraphrase the "
         "description as if it were what was said.',",
         "'- RECORDINGS: every library video from 2025 and 2026 has a searchable "
         "transcript — for \"what did X say about Y\", search the transcripts, "
         "quote what was said, and point to the exact moment (chunks carry "
         "timestamps). Videos before 2025 have no transcripts: say that boundary "
         "plainly, point them at the video, and never paraphrase the description "
         "as if it were what was said.',"),
        ("You still cannot say what was SAID inside any recording (there are no "
         "transcripts), and a calendar row alone is still not proof the session ran.",
         "If the recording is in the library (2025-2026), its transcript is "
         "searchable and you CAN say what was said, with the moment it happened; "
         "a calendar row alone is still not proof the session ran."),
    ],
    "Build Verbatim Digest": [
        ("// search INSIDE them. We cannot: there are no transcripts. We find the "
         "call and send its deck.",
         "// search INSIDE them. 2025-2026 recordings ARE transcript-searchable "
         "now; older ones we find and send the deck."),
        ("'There are no transcripts yet, so I cannot tell you what was *said* "
         "inside a video.' + NL + NL +",
         "'I can search inside 2025-2026 call recordings — ask what was said "
         "and I will point you to the moment it happened.' + NL + NL +"),
    ],
    "Answer Seed": [
        ("'RECORDINGS & VIDEOS - COVERAGE BOUNDARY (D2). You CAN search inside "
         "call transcripts, but only where they exist, and the limits are "
         "specific: transcripts cover VIRTUAL calls from 2026 onward - Mogul "
         "Calls, Channel Calls, Expert Calls. There are NO transcripts for "
         "anything published before January 2026 (872 of 1,033 videos), and NONE "
         "for in-person recordings - Summits, Masterminds and chapter events.",
         "'RECORDINGS & VIDEOS - COVERAGE BOUNDARY (D2). You CAN search inside "
         "call transcripts where they exist, and the boundary is by YEAR: every "
         "library video from 2025 and 2026 is transcribed - virtual calls AND "
         "in-person sessions (Summits, Masterminds, Inspires, chapter events). "
         "There are NO transcripts for anything published before January 2025 "
         "(about 640 of 1,033 videos)."),
        ("'- CALLS (#70): 2026 calls carry full transcripts.",
         "'- CALLS (#70): 2025 and 2026 calls carry full transcripts."),
        ("Calls before 2026 have no transcript: say the recording exists and "
         "stop, never guess its contents.",
         "Calls before 2025 have no transcript: say the recording exists and "
         "stop, never guess its contents."),
    ],
}


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    changed = 0
    for n in wf["nodes"]:
        if n["name"] not in EDITS:
            continue
        code = n["parameters"]["jsCode"]
        for old, new in EDITS[n["name"]]:
            c = code.count(old)
            if c != 1:
                sys.exit(f"ABORT {n['name']}: expected 1 occurrence, found {c}\n  {old[:90]}")
            code = code.replace(old, new)
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {n['name']}: node --check failed\n{err}")
        n["parameters"]["jsCode"] = code
        changed += 1
        print(f"  {n['name']}: {len(EDITS[n['name']])} replacements, node --check OK")
    if changed != 3:
        sys.exit(f"ABORT: expected 3 nodes changed, got {changed}")
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok")
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"))


if __name__ == "__main__":
    main()
