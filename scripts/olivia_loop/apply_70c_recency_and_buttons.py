#!/usr/bin/env python3
"""#70c — two bugs from a real prod WhatsApp session (Andy, 2026-08-07 17:34).

BUG 1 — "what was the last mogul call" answered with the SOS call from 20 May; the latest is
Dorian Gorski, 5 Aug. Root cause (isolated, both hypotheses tested): the 5 Aug video is NOT
hidden — a direct query returns it — but a "last/latest X" question is decided by DATE while
`video_search` only ranked by text/vector match. `mogul call` put a 2023 video literally titled
"Mogul Call — TikTok Expert Call" first; the newest call is titled about databases and matched
those two words weakly, so it never appeared. The SQL now takes `p_call_type` + `p_order` —
this teaches the loop they exist, which is the half that SQL cannot do.

BUG 2 — the yes/no buttons vanished. #38 was never broken: `Format Reply` attaches buttons only
when the text contains "reply YES" or the ticket phrase, and the message was 540 chars (well
under the 1024 cap) with neither. My summary offer says "Want a quick summary?" — a new offer
shape nothing had been taught to recognise. Same class of mistake as the lane itself: the
capability existed, nothing connected the new case to it.

The detector is widened to a SMALL, explicit set of offer phrasings anchored at the END of the
message, where offers actually sit — not "any question mark", which would put buttons on half
of Olivia's replies.
"""
import json, subprocess, sys, tempfile, os

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


def patch(text, old, new, where, marker):
    """Idempotence keys on a STABLE marker, never on the whole payload — comparing the full new
    string is what silently inserted the CALLS rule twice earlier today."""
    if marker in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


# ---- BUG 1: teach the loop the two new params -----------------------------------------
OLD_SCHEMA = ("input_schema: S({ p_query: str('topic, speaker or title words'), "
              "p_limit: num('max videos') }, ['p_query']) },")

NEW_SCHEMA = ("input_schema: S({ p_query: str('topic, speaker or title words - OMIT for a "
              "latest/browse ask'), p_call_type: str('mogul | expert | channel | chapter - "
              "filters to that kind of call'), p_order: str('recent = newest first, for "
              "last/latest/most-recent asks'), p_limit: num('max videos') }, []) },")

# NO APOSTROPHES in rule text: the seed builds rules as SINGLE-quoted JS.
OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"

NEW_RULE = ("  '- LATEST IS A DATE QUESTION (#70): \"what was the last/latest/most recent mogul call\" "
            "is answered by DATE, not by how well text matches. Call video_search with "
            "p_call_type (mogul | expert | channel | chapter) and p_order=recent, and leave "
            "p_query EMPTY. Using p_query for these returns the best keyword match, which is "
            "usually an old video whose title happens to contain the words - that is how the SOS "
            "call from May was once given as the latest Mogul Call.',\n")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed, OLD_SCHEMA, NEW_SCHEMA, "video_search: p_call_type + p_order", "p_call_type")
    seed = patch(seed, OLD_RULE_TAIL, NEW_RULE + OLD_RULE_TAIL,
                 "rules: latest is a date question", "LATEST IS A DATE QUESTION")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    # ---- BUG 2: the button detector only knew one offer phrasing ------------------------
    fr = nodes["Format Reply"]["parameters"]["jsCode"]
    OLD_OFFER = ("const hasOffer = /reply\\s+YES\\b/i.test(text) || "
                 "text.toLowerCase().indexOf('open a ticket with the mds team') !== -1;")
    NEW_OFFER = (
        "  // #70c: buttons were never broken - they only ever fired on \"reply YES\" or the\n"
        "  // ticket phrase. New offer shapes (\"Want a quick summary?\") matched neither, so a\n"
        "  // 540-char reply well under the 1024 cap went out as plain text. Widened to a SMALL,\n"
        "  // explicit set of offers anchored at the END of the message, where offers sit -\n"
        "  // deliberately NOT \"ends with a question mark\", which would button half her replies.\n"
        "  const OFFER_TAIL = /(want (a|the) quick summary|want me to|want the (link|details|rest)|"
        "would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\\?\\s*$/i;\n"
        "  const hasOffer = /reply\\s+YES\\b/i.test(text) "
        "|| text.toLowerCase().indexOf('open a ticket with the mds team') !== -1 "
        "|| OFFER_TAIL.test(text.trim());")
    fr = patch(fr, OLD_OFFER, NEW_OFFER, "Format Reply: offer detector", "OFFER_TAIL")
    nodes["Format Reply"]["parameters"]["jsCode"] = fr

    for label, code in (("Answer Seed", seed), ("Format Reply", fr)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(code)
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED on {label}:\n{chk.stderr}"
    print("node --check: OK (both nodes)")

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    s2 = n2["Answer Seed"]["parameters"]["jsCode"]
    f2 = n2["Format Reply"]["parameters"]["jsCode"]
    print("VERIFY", "p_call_type:", s2.count("p_call_type"), "· date rule:",
          s2.count("LATEST IS A DATE QUESTION"), "· OFFER_TAIL:", f2.count("OFFER_TAIL"),
          "· active:", wf2.get("active"), "· version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
