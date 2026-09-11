#!/usr/bin/env python3
"""#190 Q5097 — "what did the speaker say about X" is answered FROM THE TRANSCRIPT (STAGING only).

"At MDs Singapore a speaker spoke about Trybe for social media. What was the context?" was planned
as a video_search over titles and descriptions, found no title containing "Trybe", and denied that
the Summit sessions mention it. They do: `content_search_v2(..., array['tribe'],
array['call_transcript'])` returns Brandon Himmel's *TikTok Mastermind - Singapore Summit 2026*
with the exact passage - creator content from TikTok Shop approved through the tool so the videos
flow into your Meta assets. Two separate gaps, both real:

  1. the videos lane never searched the TRANSCRIPTS, only titles/descriptions/cliff notes - and its
     second fetch was deliberately empty so she could not drift to chat mentions. A transcript is
     not a chat mention: it is the video's own words, which is exactly what was asked for.
  2. the word is spelled "Tribe" in the transcript. A stylised brand (Trybe, Lyft, Flickr) is
     written both ways by real people, so a proper-noun term search tries the obvious variants.

Fix: on a what-was-SAID question the videos lane fetches transcript chunks for the named thing
(with y<->i and ph/f variants), and Build Prompt renders them as quotable passages under a rule
that a quote is copied, never composed.
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


PLAN_ANCHOR = """  if (_callType) { params.p_call_type = _callType; }"""
PLAN_NEW = """  if (_callType) { params.p_call_type = _callType; }
  // #190 Q5097 (2026-09-11): "a speaker spoke about Trybe - what was the context?" searched video
  // TITLES and descriptions, found nothing, and denied the Summit sessions mention it. The word is
  // in the TRANSCRIPT (spelled "Tribe"), which this lane never searched - its second fetch was
  // held empty so she could not drift to chat mentions, but a transcript is the video's OWN words.
  // On a what-was-SAID question, fill that slot with transcript chunks for the named thing, and
  // try the obvious spellings: a stylised brand (Trybe/Tribe, Lyft/Lift) is written both ways.
  const _saidAsk = /\\b(said|say|says|saying|mention(?:s|ed)?|discuss(?:ed|es)?|talk(?:ed|s)? about|context|quote[ds]?|cover(?:ed|s)?)\\b/i.test(String(rawText || ''));
  if (_saidAsk) {
    const _variants = function (w) {
      const out = [w.toLowerCase()];
      [[/y/g, 'i'], [/i/g, 'y'], [/ph/g, 'f'], [/f/g, 'ph']].forEach(function (r) {
        const v = w.toLowerCase().replace(r[0], r[1]);
        if (v !== w.toLowerCase() && out.indexOf(v) === -1) { out.push(v); }
      });
      return out;
    };
    const _SKIP = /^(mds|the|this|that|what|when|where|who|why|how|and|but|for|with|about|summit|singapore|millie|olivia|i|a|an|it|they|he|she|we|you|speaker|video|call|session)$/i;
    const _caps = (String(rawText || '').match(/\\b[A-Z][A-Za-z0-9'&-]{2,}\\b/g) || [])
      .filter(function (w) { return !_SKIP.test(w); });
    const _tt = [];
    _caps.slice(0, 3).forEach(function (w) {
      _variants(w).forEach(function (v) { if (_tt.indexOf(v) === -1) { _tt.push(v); } });
    });
    if (_tt.length) {
      raw_op = 'content_search';
      raw_params = { p_phone: mem.to, p_terms: _tt, p_sources: ['call_transcript'],
                     p_limit: 8, no_embed: true };
    }
  }"""

BP_ANCHOR = """  const anyRestricted = vids.some(function (v) { return v.is_restricted; });
  const system = ["""
BP_NEW = """  const anyRestricted = vids.some(function (v) { return v.is_restricted; });
  // #190 Q5097: transcript passages for what the member NAMED (only fetched on a what-was-said
  // question). These are the session's own words, so they are quotable - and quoting is the whole
  // point of the ask. Restricted sessions never reach here: content_search_v2 gates them out.
  const trRows = ($('Fetch Raw Matches').isExecuted ? $('Fetch Raw Matches').all() : [])
    .map(i => i.json).filter(function (r) { return r && r.body && r.source === 'call_transcript'; });
  let trBlock = trRows.slice(0, 6).map(function (r) {
    let t = String(r.body).replace(/\\s+/g, ' ').trim();
    if (t.length > 900) { t = t.slice(0, 900) + '\\u2026'; }
    return '- [' + String(r.occurred_at).slice(0, 10) + '] ' + (r.title || 'a recorded session')
      + ': "' + t + '"';
  }).join(NL);
  if (trBlock.length > 6000) { trBlock = trBlock.slice(0, 6000) + NL + '\\u2026[more omitted]'; }
  const system = ["""

BP_RULE_ANCHOR = "    'MODE: MDS VIDEO LIBRARY. Below are recorded sessions from the MDS video library — the real catalogue, not links people pasted in chat. This IS the answer; do not fall back to chat or Facebook mentions of videos.',"
BP_RULE_NEW = BP_RULE_ANCHOR + """
    (trBlock ? 'TRANSCRIPT PASSAGES are included below for what the member named. They are the sessions\\u2019 OWN WORDS: answer the "what did they say / what was the context" part FROM them, quote the wording as it stands (a spelling may differ from the member\\u2019s - say so in passing rather than correcting them), and name the session it came from. Never compose a quote, and never say a session does not mention something when a passage below does.' : 'NO TRANSCRIPT PASSAGES were fetched for this question. If the member asks what was SAID inside a session, do not claim it was not mentioned - say you could not find it in what you can see of that session and offer the session itself.'),"""

BP_USER_ANCHOR = "  let user = 'VIDEO LIBRARY MATCHES'"
BP_USER_NEW = ("  let user = (trBlock ? 'WHAT WAS SAID IN THE SESSIONS (transcript passages, the sessions\u2019 own words):'"
               " + NL + trBlock + NL + NL : '') + 'VIDEO LIBRARY MATCHES'")


def patch(node, edits, label):
    code = node["parameters"]["jsCode"]
    before = len(code)
    for old, new in edits:
        n = code.count(old)
        if n != 1:
            print(f"ABORT [{label}]: anchor x{n}, expected 1:\n  {old[:110]}…", file=sys.stderr)
            sys.exit(2)
        code = code.replace(old, new)
    node["parameters"]["jsCode"] = code
    print(f"{label}: {before} -> {len(code)} chars")
    return code


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    patch(next(n for n in nodes if n["name"] == "Plan Request"), [(PLAN_ANCHOR, PLAN_NEW)], "Plan Request")
    bp = next(n for n in nodes if n["name"] == "Build Prompt")
    code = patch(bp, [(BP_ANCHOR, BP_NEW), (BP_RULE_ANCHOR, BP_RULE_NEW)], "Build Prompt")
    # attach the block to the user payload of the videos lane
    if code.count(BP_USER_ANCHOR) != 1:
        print(f"ABORT: videos-lane user anchor x{code.count(BP_USER_ANCHOR)}; block built but never rendered", file=sys.stderr)
        return 2
    code = code.replace(BP_USER_ANCHOR, BP_USER_NEW)
    bp["parameters"]["jsCode"] = code
    print("Build Prompt: transcript block wired into the videos user payload")
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
