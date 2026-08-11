#!/usr/bin/env python3
"""#80 — deliver what you offered, and stop offering on every turn.

Week of 2026-08-04..11, read turn by turn: three accepted "Want a quick summary?"
offers of a specific library video were answered with community-thread chatter
instead (ans #28131 / #28133 / #29905 — sources_used = content_search only), while
the teased videos each carried a transcript-sourced summary in videos_catalog that
video_search_v2 did not even return. The binding is stochastic: the same shape
sometimes works (#27225 SOS, staging #30853) and sometimes rebinds to the topic
(staging #30847). This script makes the good path deterministic.

Four patches, Answer Seed ONLY (one node, one PUT):
  A. tool schema: video_search gains p_video_id (the SQL side shipped in migration
     video_search_v2_p_video_id_summary_80 — exact-row fetch + summary column).
  B. offer-binding detection: previous Olivia turn ends in an offer AND links
     app.mds.co/videos/<id> AND the current member turn is an acceptance ->
     an OFFER ACCEPTED line is injected at the head of the preload evidence block.
  C. the preload join keeps that line when zeroth-fetch rows exist.
  D. two rules before the standing tail rule: DELIVER WHAT YOU OFFERED (#80) and
     OFFER SPARINGLY (#80). No apostrophes in rule text (single-quoted JS).
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


def patch(text, old, new, where, marker):
    """Idempotence keys on a STABLE marker, never on the whole payload."""
    if marker in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


# ---- A: tool schema gains p_video_id --------------------------------------------------
OLD_SCHEMA = ("input_schema: S({ p_query: str('topic, speaker or title words - OMIT for a "
              "latest/browse ask'), p_call_type: str('mogul | expert | channel | chapter - "
              "filters to that kind of call'), p_order: str('recent = newest first, for "
              "last/latest/most-recent asks'), p_limit: num('max videos') }, []) },")
NEW_SCHEMA = ("input_schema: S({ p_query: str('topic, speaker or title words - OMIT for a "
              "latest/browse ask'), p_call_type: str('mogul | expert | channel | chapter - "
              "filters to that kind of call'), p_order: str('recent = newest first, for "
              "last/latest/most-recent asks'), p_video_id: str('exact library video id from an "
              "app.mds.co/videos/<id> link - fetches THAT video with its summary; use it when "
              "delivering an offered or linked video'), p_limit: num('max videos') }, []) },")

# ---- B: offer-binding detection before the preload block ------------------------------
OLD_PRELOAD_DECL = "let preload = '';"
NEW_PRELOAD_DECL = '''// #80 OFFER BINDING. The failing sessions (ans #28131/#28133/#29905) re-searched the
// TOPIC on a bare acceptance and delivered chat chatter instead of the teased video -
// whose transcript summary sat unread in videos_catalog. Deterministic detection:
// previous Olivia turn ends in an offer AND links a library video AND the member is
// accepting -> inject the binding as evidence the loop cannot miss.
const ACCEPT_RE = /^(yes|yes please|yep|yeah|sure|ok|okay|sounds good|go ahead|please do|do it|summar(y|ize|ise)( key points| it)?|key points( please)?|can you summar(y|ize|ise)[^?]{0,40}[?]?)[!. ]*$/i;
const OFFER_TAIL_RE = /(want (a|the) quick summary|want me to|want the (link|details|rest)|would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\\?\\s*$/i;
let offer_ctx = '';
try {
  let lastO = null;
  for (let i = rows.length - 1; i >= 0 && !lastO; i--) { if (rows[i].role !== 'member') lastO = rows[i]; }
  const lt = lastO ? String(lastO.text || '') : '';
  const links = lt.match(/app\\.mds\\.co\\/videos\\/([a-f0-9]{24})/gi) || [];
  if (OFFER_TAIL_RE.test(lt.trim()) && links.length && ACCEPT_RE.test(current)) {
    const vid = String(links[links.length - 1]).split('/').pop();
    offer_ctx = 'OFFER ACCEPTED: your previous message offered the library video ' + vid
      + ' and the member just accepted. Call video_search with p_video_id set to ' + vid
      + ' and answer from its summary field. Community threads may only supplement, clearly separated.';
  }
} catch (e) {}
let preload = offer_ctx;'''

# ---- C: preload join keeps the binding when zeroth-fetch rows exist -------------------
OLD_JOIN = "  preload = parts.join(NL);"
NEW_JOIN = "  preload = (offer_ctx ? offer_ctx + NL + NL : '') + parts.join(NL);"

# ---- D: two rules before the standing tail rule ---------------------------------------
OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"
NEW_RULES = (
    "  '- DELIVER WHAT YOU OFFERED (#80): when the member accepts an offer (yes / sure / "
    "summarize it / key points) and your previous message linked a specific library video, "
    "the accepted thing IS the question. Call video_search with p_video_id set to the id "
    "from that link FIRST and answer from its summary field. Community threads may only "
    "supplement, clearly separated. If the video is restricted or summary is empty, say "
    "honestly what is on file - never substitute chat chatter for the video you teased.',\n"
    "  '- OFFER SPARINGLY (#80): end with an offer ONLY when it names ONE concrete thing you "
    "can produce next (a specific video summary, a specific thread, a specific list) that "
    "you have NOT already delivered. Never offer two alternatives in one question - a Yes "
    "button cannot answer an either-or. Never re-offer what this same reply already "
    "contains. A complete answer ends as a statement, not a tease.',\n"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed, OLD_SCHEMA, NEW_SCHEMA, "schema: p_video_id", "p_video_id")
    seed = patch(seed, OLD_PRELOAD_DECL, NEW_PRELOAD_DECL, "preload: offer binding", "OFFER ACCEPTED")
    seed = patch(seed, OLD_JOIN, NEW_JOIN, "preload: join keeps binding", "offer_ctx ?")
    seed = patch(seed, OLD_RULE_TAIL, NEW_RULES + OLD_RULE_TAIL, "rules: deliver + sparingly",
                 "DELIVER WHAT YOU OFFERED")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED on Answer Seed:\n{chk.stderr}"
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
    seed2 = {n["name"]: n for n in wf2["nodes"]}["Answer Seed"]["parameters"]["jsCode"]
    for marker in ("p_video_id", "OFFER ACCEPTED", "offer_ctx ?", "DELIVER WHAT YOU OFFERED",
                   "OFFER SPARINGLY"):
        c = seed2.count(marker)
        assert c >= 1, f"marker {marker!r} missing after PUT"
        print(f"  verified: {marker!r} x{c}")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
