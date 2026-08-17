#!/usr/bin/env python3
"""D1 - chapter questions have no lane in the router. Apply to STAGING (bqHstPDi84uOhTCJ).

Andy, live 2026-08-13, and a real member (Jerome Acevedo) on 2026-08-15:
  "what chapter should i join"            -> route=chats, answered with WhatsApp chats
  "I meant MDS Chapter"                   -> route=chats, byte-identical repeat
  "Could you point me towards the Texas chapter?"  -> same class

Root cause: the word "chapter" appears NOWHERE in the Route Request system prompt. Its
17 intents include chats ("which chats exist or which they could join") and community
("MDS itself: how many members, how big"). A chapter question matches the only lane that
knows the word JOIN, and the correction re-classifies identically because nothing in the
prompt distinguishes a chapter from a chat.

Fix: teach the router the distinction and send chapter questions to "community", which
already reaches digest.chapter_info and produced the correct answer for "how many chapters
are in MDS?" (20 chapters, nearest chapter, leads, page link).

Not a new intent: community already works end to end, so this is a prompt-only change with
no downstream node to touch.

NO APOSTROPHES in inserted text - the prompt lives inside a JS single-quoted string and an
unescaped quote has broken this workflow twice before.

Idempotent: asserts each anchor appears exactly once, aborts without writing otherwise.
"""
import json
import subprocess
import sys

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
NODE = "Route Request"
MARK = "CHAPTER IS NOT A CHAT"


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


# --- anchors, exactly as they appear after JSON-parsing the workflow -------------
A_CHATS = '- "chats" = which chats exist or which they could join.'
A_COMMUNITY = '- "community" = MDS itself: how many members, how big, how many chats/events.'
A_EXAMPLE = '"what other chats can I join?" -> {"intent":"chats"'
A_PRECEDENCE = "history only fills in missing details):"

# --- replacements ---------------------------------------------------------------
R_CHATS = ('- "chats" = which WHATSAPP chats exist or which they could join. '
           'NEVER a chapter question - see CHAPTER IS NOT A CHAT above.')

R_COMMUNITY = ('- "community" = MDS itself: how many members, how big, how many chats/events - '
               'AND EVERY QUESTION ABOUT CHAPTERS (which one to join, which one is nearest, who '
               'leads one, how many exist, what happens at them, which one the member is in).')

CHAPTER_RULE = (
    "\\n- CHAPTER IS NOT A CHAT. An MDS CHAPTER is a real-world group with a president, a page "
    "on mds.co and in-person meetings - New York, SoTex, Europe, Asia Pacific, LA, Chicago, "
    "Pacific Northwest and the rest (20 of them). A CHAT is a WhatsApp group. ANY question that "
    "names a chapter, or asks which chapter to join, which is nearest, who leads one, how many "
    "exist, or what happens at them, is \\\"community\\\" - NEVER \\\"chats\\\" - EVEN WHEN IT "
    "USES THE WORD JOIN. The word join on its own does not mean chats. So \\\"what chapter should "
    "i join\\\", \\\"point me towards the Texas chapter\\\", \\\"which chapter am I in\\\" and "
    "\\\"who runs the New York chapter\\\" are ALL community. If the member corrects you with "
    "\\\"I meant the chapter\\\" or \\\"I meant MDS Chapter\\\", that correction is community too "
    "- do not repeat the chat list."
)

EXAMPLE = (
    '"what chapter should i join" -> {"intent":"community","chat":null,"period":null,'
    '"date_hint":null,"search_terms":[],"match_dims":[],"match_city":null,"match_state":null,'
    '"member_name":null,"expertise_query":null,"event_virtual":null,"event_past":false,'
    '"followup":false}\\n'
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf.get("nodes") or sys.exit(f"no nodes in staging: {str(wf)[:300]}")
    node = next((n for n in nodes if n.get("name") == NODE), None)
    if node is None:
        sys.exit(f"node {NODE!r} not found")

    body = node["parameters"]["jsonBody"]

    if MARK in body:
        print("already applied - no change")
        return 0

    for label, anchor in (("chats def", A_CHATS), ("community def", A_COMMUNITY),
                          ("chats example", A_EXAMPLE), ("lane precedence", A_PRECEDENCE)):
        if body.count(anchor) != 1:
            sys.exit(f"anchor {label!r} appears {body.count(anchor)} times, expected 1 - ABORT")

    new = body
    new = new.replace(A_PRECEDENCE, A_PRECEDENCE + CHAPTER_RULE, 1)
    new = new.replace(A_CHATS, R_CHATS, 1)
    new = new.replace(A_COMMUNITY, R_COMMUNITY, 1)
    new = new.replace(A_EXAMPLE, EXAMPLE + A_EXAMPLE, 1)

    # a raw apostrophe inside the single-quoted JS prompt would break the node
    inserted = CHAPTER_RULE + EXAMPLE + R_CHATS + R_COMMUNITY
    if "'" in inserted:
        sys.exit("ABORT: inserted text contains a raw apostrophe")

    node["parameters"]["jsonBody"] = new

    payload = {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings", {})}
    res = api("PUT", f"/workflows/{STAGING_ID}", payload)
    if not res.get("id"):
        sys.exit(f"PUT failed: {str(res)[:400]}")

    check = api("GET", f"/workflows/{STAGING_ID}")
    cnode = next(n for n in check["nodes"] if n["name"] == NODE)
    ok = MARK in cnode["parameters"]["jsonBody"]
    print(f"staging updated: {len(check['nodes'])} nodes · chapter rule present = {ok}")
    print(f"prompt grew {len(body)} -> {len(cnode['parameters']['jsonBody'])} chars")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
