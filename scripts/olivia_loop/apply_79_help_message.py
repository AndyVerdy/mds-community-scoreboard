#!/usr/bin/env python3
"""#79 — the capability list a member sees, rewritten after three releases.

The shipped intro was frozen at launch and had gone false: it said "Not yet: what was
*said* inside a recording (no transcripts)" months after #70 put call transcripts and
summaries live, and it never mentioned census stats, credits, chapters or bug reports.

Andy's rules for this copy (2026-08-11, iterated with him line by line):
  - identity is "the MDS AI assistant" — not a person, not a name
  - NO member names anywhere (no greeting name, no example member)
  - WhatsApp bold is a SINGLE asterisk; ** renders literally
  - early beta is stated plainly, next to the 👍/👎 ask (the #75 teaching signal)
  - CURATED, never auto-generated: an intro is deliberate copy with a voice, and a
    generator produces a changelog that leaks half-shipped work into a first impression.
    Re-read at every sprint close / release-notes step — that cadence IS the fix for drift.

Every example phrasing is probe-proven on staging before shipping (2026-08-11):
"what % of members sell on TikTok?" -> form_stats (89%, median 3%) · "who leads the NY
chapter?" -> chapter_info (3 leads + link) · the rest carried over from the proven set.
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


START = "if (plan.route === 'help') {"
END = "  if (reply.length > 3900) { reply = reply.slice(0, 3900); }"

# NOTE: every apostrophe below is U+2019 (curly) and every quote U+201C/D, so the lines
# sit safely inside single-quoted JS. An ASCII apostrophe here would break the node —
# the assert at the bottom of build_block() enforces it.
LINES = [
    'Hi 👋 I’m the MDS AI assistant.',
    '',
    'I can answer questions using MDS content across WhatsApp chats, the Facebook group, '
    'calls, videos, the member directory, chapters, events, partner deals, census responses, '
    'and applications.',
    '',
    'Ask me anything you’d normally want to look up across MDS.',
    '',
    '*Catch up on what you missed*',
    '',
    '“what did I miss on Facebook this week?”',
    '“what are people saying about tariffs?”',
    '',
    '*Find the right person*',
    '',
    '“who’s in Austin?” · “who knows PPC?” · “who sells on Walmart?”',
    '',
    '*Learn from MDS*',
    '',
    '“what was the last Mogul Call?”',
    '“is there a video about hiring a C-suite?”',
    '',
    '*Use what your membership gives you*',
    '',
    '“any deals for 3PL?” · “what am I registered for?” · “how many credits do I have?”',
    '',
    '*Know the room*',
    '',
    '“how many members are in MDS?”',
    '“what % of members sell on TikTok?”',
    '',
    '*Answers that are relevant to you*',
    '',
    'When it’s useful, I’ll take what MDS already knows about you into account, so answers '
    'can be relevant to your business, interests, and situation — rather than giving everyone '
    'the same generic answer.',
    '',
    '⚠️ *I’m in early beta.* I’ll get things wrong sometimes. React 👍 or 👎 to any answer — '
    'that helps me improve.',
    '',
    'Something broken? Say *“I want to report a bug”* and I’ll write it up for the team.',
]

HEADER = """if (plan.route === 'help') {
  // #79 (2026-08-11): CURATED capability list, never auto-generated — a generator writes a
  // changelog and leaks half-shipped work into a member's first impression. Re-read at every
  // sprint close / release-notes step; that cadence is the fix for drift, not a generator.
  // Andy's rules: identity is "the MDS AI assistant", NO names, WhatsApp bold is ONE asterisk,
  // early beta stays. The old copy claimed "no transcripts" for months after #70 shipped them.
  let reply = [
"""


def build_block():
    body = "".join("    '" + l.replace("\\", "\\\\") + "'," + "\n" for l in LINES)
    block = HEADER + body + "  ].join(NL);\n"
    bad = [l for l in LINES if "'" in l]
    assert not bad, f"ASCII apostrophe would break the single-quoted JS: {bad}"
    return block


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    code = nodes["Build Verbatim Digest"]["parameters"]["jsCode"]

    if "the MDS AI assistant" in code:
        print("already applied — new help copy present")
    else:
        assert code.count(START) == 1, f"START anchor found {code.count(START)}x — aborting"
        i = code.index(START)
        j = code.index(END, i)
        assert j > i, "END anchor not found after START — aborting"
        old = code[i:j]
        assert "Here\\'s what I can help you with" in old or "what I can help you with" in old, \
            "the sliced region is not the help copy — aborting"
        code = code[:i] + build_block() + code[j:]
        nodes["Build Verbatim Digest"]["parameters"]["jsCode"] = code

        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(code)
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
        print("node --check: OK")

        body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
                "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                             if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                      "saveDataErrorExecution", "saveDataSuccessExecution",
                                      "saveExecutionProgress", "saveManualExecutions", "timezone")}}
        r = api("PUT", f"/workflows/{STAGING_ID}", body)
        assert r.get("id"), f"PUT failed: {str(r)[:300]}"
        api("POST", f"/workflows/{STAGING_ID}/deactivate")
        api("POST", f"/workflows/{STAGING_ID}/activate")
        print("PUT + bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    c2 = {n["name"]: n for n in wf2["nodes"]}["Build Verbatim Digest"]["parameters"]["jsCode"]
    for marker in ("the MDS AI assistant", "early beta", "Answers that are relevant to you",
                   "what % of members sell on TikTok"):
        assert marker in c2, f"marker {marker!r} missing after PUT"
        print(f"  verified: {marker!r}")
    # Check the MEMBER-FACING strings only — the comment above deliberately quotes the old
    # claim, and asserting on that substring tripped this check against itself once.
    assert "what I can help you with, " not in c2, "old name-greeting copy still present"
    assert "what was *said* inside a recording" not in c2, "old no-transcripts claim still present"
    print("  verified: old copy gone (name greeting + no-transcripts claim)")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
