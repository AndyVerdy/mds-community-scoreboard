#!/usr/bin/env python3
"""#202 + #203 — when the member NAMES something, answer about that thing (STAGING only).

Both failures in #190's exam are the same shape from two lanes:

  #202  "how do i join the supplements channel" -> `chat_recommendations` ran with NO query at all,
        so the named chat was dropped and MDS TikTok was recommended instead. MDS Supplements is
        verification-gated and `chat_info` already returns its gate, its requirement and its join
        link - the lane simply was never asked. Member report #34 ("the link doesn't work?") sits
        in the same lane.

  #203  "How I become a member of mds9?" -> "I'm not familiar with anything called MDS9", answered
        out of `community_info` + `org_docs`, neither of which can see the events calendar, where
        MDS 9 has FOUR events (and the library twelve sessions). That is the deny-from-silence
        class: one lane's silence spoken as the record's silence.

Both fixes are deterministic routing, in code, not a prompt rule (feedback_code_beats_prompt_rules)
- and both reuse a lane that already exists and already renders.

Literal replaces, anchors asserted unique (never regex: a `$` is a backreference in re.sub).
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


EDITS = [
    # #202 — a named chat is answered about, not replaced by recommendations
    ("""} else if (intent === 'chats') {
  route = 'chats'; planPeriod = 'chats';
  op = 'chat_recommendations';
  params = { p_phone: mem.to };""",
     """} else if (intent === 'chats') {
  route = 'chats'; planPeriod = 'chats';
  op = 'chat_recommendations';
  params = { p_phone: mem.to };
  // #202 (2026-09-11): "how do i join the supplements channel" NAMED a chat and got a list of
  // OTHER chats - the recommender runs with no query, so the name was dropped and MDS TikTok was
  // offered. The router's p.chat is not reliable here, so match the text against the real chat
  // directory this node already holds (linkRows), ignoring the shared "MDS" prefix. Only a real
  // chat name hijacks the lane; "what chats should I join" still recommends.
  const _namedChat = (function () {
    const t = ' ' + String(rawText || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ') + ' ';
    let best = null;
    (linkRows || []).forEach(function (r) {
      const full = String(r.chat_name || '');
      const key = full.toLowerCase().replace(/^mds\\s+/, '').replace(/[^a-z0-9]+/g, ' ').trim();
      if (key.length < 4) { return; }
      if (t.indexOf(' ' + key + ' ') !== -1 && (!best || key.length > best.key.length)) {
        best = { name: full, key: key };
      }
    });
    return best ? best.name : (rawChat || null);
  })();
  if (_namedChat) {
    route = 'llm'; planPeriod = 'chatinfo';
    op = 'chat_info';
    params = { p_phone: mem.to, p_chat: _namedChat };
  }"""),

    # #203 — a named MDS programme goes to the lane that can see programmes
    ("""} else if (intent === 'community') {
  route = 'llm'; planPeriod = 'community';
  op = 'community_info';
  params = { p_phone: mem.to };""",
     """} else if (intent === 'community') {
  route = 'llm'; planPeriod = 'community';
  op = 'community_info';
  params = { p_phone: mem.to };
  // #203 (2026-09-11): "How I become a member of mds9?" -> "I'm not familiar with anything called
  // MDS9". community_info returns community NUMBERS and org_docs is a document library; neither
  // can see the events calendar, where MDS 9 has four events (100M+ Mastermind Dec 2026, BFCM
  // Strategy Dinner, Michelin Dinner, the August call) and the library twelve sessions. A lane's
  // silence is not the record's silence: a question naming an MDS programme goes to the events
  // lane, which knows it exists and renders it.
  const _prog = String(rawText || '').match(/\\bmds\\s?-?\\s?(\\d{1,2})\\b/i);
  if (_prog) {
    route = 'llm'; planPeriod = 'events';
    op = 'event_lookup';
    params = { p_phone: mem.to, p_limit: 12, p_include_past: true,
               p_terms: ['MDS ' + _prog[1], 'MDS' + _prog[1]] };
  }"""),
]


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    node = next(n for n in nodes if n["name"] == "Plan Request")
    code = node["parameters"]["jsCode"]
    before = len(code)
    for old, new in EDITS:
        n = code.count(old)
        if n != 1:
            print(f"ABORT: anchor x{n}, expected 1:\n  {old[:120]}…", file=sys.stderr)
            return 2
        code = code.replace(old, new)
    node["parameters"]["jsCode"] = code
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print(f"Plan Request: {before} -> {len(code)} chars ({len(EDITS)} edits)")
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
