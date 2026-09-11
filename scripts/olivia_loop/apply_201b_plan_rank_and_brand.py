#!/usr/bin/env python3
"""#201 lap 2 — make the PLAN ask for what the tools now carry (STAGING only).

Lap 1 put the facts in the database (p_order=views, view counts in strength_note, member_card
resolving a brand, member_card_v3 returning the brands). The probe run showed two gaps that live
in the graph, not in SQL:

  A. "what are the most popular videos" came back as a page of rows in relevance order which the
     model then narrated AS a ranking — 395 views listed below 264. A ranking is a tool fact (#56),
     so the ORDER must be asked for deterministically, exactly as partner_lookup already does.
  B. "which member owns \"stylia beauty\"" sent p_member="millie verify member stylia beauty" —
     the router set no member_name and the fallback joins every search term, scaffolding included.
     A quoted phrase is the member's own answer to "which brand"; use it, and on an ownership ask
     strip the question words out of the fallback.
  C. member_card -> member_card_v3 in EXEC_NAME, so the evidence carries the brands and the
     fact-check gate can verify a brand claim instead of clamping it.

Literal replaces, each anchor asserted unique (reference_n8n_patchnodefield_dollar: never regex,
a `$` in an n8n expression is a backreference).
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


PLAN_EDITS = [
    # A — a most-watched ask is a RANKING, and a ranking is a tool fact (#56)
    ("  if (_callType) { params.p_call_type = _callType; }",
     """  if (_callType) { params.p_call_type = _callType; }
  // #201 (2026-09-11): "the top 5 most watched mogul calls" was answered from an UNRANKED page of
  // rows — nothing set p_order, so the model narrated arrival order and called it a ranking (395
  // views sat below 264). Same shape as the partner rankOrder above: decide it here, in code, and
  // let the tool sort. p_query must be EMPTY or the keyword rank fights the view order.
  const _viewRank = /\\b(most|top|highest|best)\\b[\\s\\S]{0,24}\\b(watch|watched|views?|viewed|popular)\\b/i.test(String(rawText || ''))
    || /\\b(views?|viewed|watched)\\b[\\s\\S]{0,16}\\b(most|top|highest)\\b/i.test(String(rawText || ''));
  if (_viewRank) {
    params.p_order = 'views';
    params.p_query = null;
    params.p_limit = Math.max(Number(params.p_limit) || 8, 10);
  }"""),

    # B — the brand in quotes IS the subject; scaffolding is not
    ("const mname = (typeof p.member_name === 'string' && p.member_name.trim()) ? p.member_name.trim().slice(0, 80) : terms.join(' ');",
     """const _quotedSubject = (function () {
    const m = String(rawText || '').match(/["\\u201c\\u201d']([^"\\u201c\\u201d']{3,60})["\\u201c\\u201d']/);
    return m ? m[1].trim() : null;
  })();
  // #201: only on an OWNERSHIP ask — "which member owns X", "who runs X", "the member behind X".
  // Elsewhere the raw terms are left exactly as they were: stripping question words out of
  // "who is the member of the month" would leave "month".
  const _ownershipAsk = /\\b(owns?|owner|runs?|behind)\\b/i.test(String(rawText || ''))
    || /\\bbrand\\b/i.test(String(rawText || ''));
  const _stripAsk = function (s) {
    return String(s || '').replace(/\\b(millie|olivia|hey|hi|hello|please|can|could|would|you|are|able|to|verify|check|confirm|know|which|who|whose|what|member|members|owns?|owner|runs?|behind|brand|brands|name|named|names|the|is|there|a|an|of|for|tell|me|about)\\b/gi, ' ')
      .replace(/\\s+/g, ' ').trim();
  };
  const mname = (typeof p.member_name === 'string' && p.member_name.trim())
    ? p.member_name.trim().slice(0, 80)
    : (_quotedSubject
       || (_ownershipAsk ? (_stripAsk(terms.join(' ')) || terms.join(' ')) : terms.join(' ')));"""),
]

# C — the card that carries the brands
EXEC_EDIT = ("member_card: 'member_card_v2'", "member_card: 'member_card_v3'")

SEED_EDIT = (
    "brands are public, the exact revenue behind them is never)",
    "brands are public, the exact revenue behind them is never). Every card comes back with a "
    "`brands` list when the member has one - name it when you are asked who is behind a brand, and "
    "never assert a brand the card did not return)",
)


def patch(node, edits, label):
    code = node["parameters"]["jsCode"]
    before = code
    for old, new in edits:
        n = code.count(old)
        if n != 1:
            print(f"ABORT [{label}]: anchor x{n}, expected 1:\n  {old[:100]}…", file=sys.stderr)
            sys.exit(2)
        code = code.replace(old, new)
    node["parameters"]["jsCode"] = code
    print(f"{label}: {len(before)} -> {len(code)} chars ({len(edits)} edits)")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    patch(next(n for n in nodes if n["name"] == "Plan Request"), PLAN_EDITS, "Plan Request")
    patch(next(n for n in nodes if n["name"] == "Attach Embedding"), [EXEC_EDIT], "Attach Embedding")
    patch(next(n for n in nodes if n["name"] == "Answer Seed"), [SEED_EDIT], "Answer Seed")
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
