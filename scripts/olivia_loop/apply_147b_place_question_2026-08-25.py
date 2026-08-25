#!/usr/bin/env python3
"""Andy's complaint #2 — "who should i meet in singapore" answered with a refusal about the Summit.

WHAT HE GOT (2026-08-25 01:38, prod):
    "That "viewing: public agenda (not registered for this event)" note means I'm not seeing you as
     registered for the Summit, so I can't pull the personalized who-to-meet matcher for it.
     Here's what I can tell you instead: your interests lean heavily into Supplements, AI &
     Automation, International Expansion, and Logistics/3PL …"

Four separate faults in one reply:
  1. It quoted an INTERNAL field at him. `viewing` is set by the schedule route
     (mds-digest-web/src/app/api/olivia/schedule/route.ts:384) as "public agenda (not registered for
     this event)" — a sentence, so the model read it as prose and pasted it into the answer.
  2. It treated a question about a CITY as a question about the Summit. He asked who to meet in
     Singapore; 9 MDS members live there and the finder can name them with no event access at all.
  3. With the event lane gated, it substituted his own profile back at him — "your interests lean
     heavily into…" — which answers nothing.
  4. It never asked the one clarifier that would have settled it: the Summit, or members in the city.

This wave fixes 2, 3 and 4 in Answer Seed, and stops 1 from reaching a member by forbidding the quoting
of any scope/status field. The proper fix for 1 is one line in the web route (rename the value to a token
like `public_agenda` so it cannot read as prose) — that lives in another repo and ships on push, so it is
left for its own session.

  python3 scripts/olivia_loop/apply_147b_place_question_2026-08-25.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code)
        tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")


ANCHOR = ("  'A NUDGE IS NOT A SEARCH. \"did you see my message\", \"hello?\", \"you there?\", "
          "\"any update?\" carry no new question")

NEW = """  'A PLACE IS NOT AN EVENT. "who should I meet in Singapore", "anyone in Austin", "who is in Dubai" ask about a PLACE. Answer them from the member directory first - find with {city} or {country} - and name the members who are actually there, with the reasons they matched. An event happening in that city is an ADDITION when the asker is registered for it ("and at the Summit this week, X and Y are also there"), never a substitute and never a reason to refuse. If an event gate blocks the event half, the place half is still owed: give it. Only when the place genuinely has nobody on file do you say so plainly.',
  'A GATE ON ONE PART NEVER SILENCES THE REST. When a rule withholds part of an answer, deliver every part it does not cover, then name the withheld part in ONE line. Never fill the gap with facts about the ASKER - their niche, their interests, their focus areas - that is their own profile read back to them and answers nothing. If you cannot answer the question at all, ask ONE clarifier naming the two readings ("do you mean people at the Summit, or members based in Singapore?") and stop.',
  'NEVER QUOTE THE PLUMBING. Tool payloads carry scope and status fields for YOU, not for the member: viewing, gate, access, matched, reason, ok, total, cap, scope. Never repeat one in a reply, never put it in quotation marks, never build a sentence around it. Say what it MEANS in your own words to the member, or say nothing about it. A member reading "viewing: public agenda (not registered for this event)" is reading our machinery.',
""" + ANCHOR


def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    print(f"staging versionId {wf.get('versionId')} · {len(wf['nodes'])} nodes")
    seed = [n for n in wf["nodes"] if n["name"] == "Answer Seed"][0]
    c = seed["parameters"]["jsCode"]
    assert c.count(ANCHOR) == 1, f"anchor drift ({c.count(ANCHOR)}x)"
    c = c.replace(ANCHOR, NEW)
    node_check(c, "Answer Seed")
    seed["parameters"]["jsCode"] = c
    if dry:
        print("DRY RUN — nothing written")
        return 0
    out = api("PUT", f"/workflows/{STAGING}",
              {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("applied · new versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
