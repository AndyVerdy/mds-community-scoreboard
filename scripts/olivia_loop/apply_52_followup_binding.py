#!/usr/bin/env python3
"""#52 Follow-ups bind to the MOST RECENT topic — apply to STAGING (bqHstPDi84uOhTCJ).

Eugene, live 2026-08-04 01:12 (the thumbs-down Andy spotted):
  01:10 "Who are the best lenders in our portal?"      -> good answer (partner_lookup)
  01:12 "How about based on mentions in Facebook?"     -> answered about NEWSLETTERS,
        a topic from 20:46, 4.5h earlier                  p_terms ["newsletter","ai"]  👎
  01:13 "I think you missed my question..."            -> recovered correctly

The router prompt ALREADY says "resolve pronouns against the MOST RECENT exchange". Like the
BARE AFFIRMATIONS rule before it, a Haiku prompt line does not hold against a 24h history
window — so the binding becomes deterministic state, exactly as the yes-binding did.

Plan Request: a PURE-QUALIFIER continuation ("how about on Facebook?", "and in the chats?",
"what about that?") — a continuation opener plus a scope/source/recency word and NO topic of
its own — takes its topic from the LAST turn's plan (Prep Context's prev_plan), overriding the
router's search_terms. A continuation that carries its own topic ("how about tariffs?") is a
new subject and is left untouched.

Idempotent: safe to re-run; asserts before the replace and aborts without writing.
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


MARK = "#52 TOPIC CONTINUATION BINDING"
MARK2 = "#52 (part 2): a pure-qualifier continuation that names a SOURCE"

ANCHOR = "const STOPW = new Set(["

ANCHOR2 = "if (p.source === 'chats') { wantFb = false; }"

BLOCK2 = """
// #52 (part 2): a pure-qualifier continuation that names a SOURCE changes WHERE to look, not
// WHAT — and no lane except the content search can honour it. The router keeps the PREVIOUS
// lane instead (staging replay 2026-08-03: with the topic bound correctly, "how about based on
// mentions in Facebook?" still came back intent='partners' — the portal ratings a second time,
// no Facebook in it). So on a carried topic the SOURCE STEER WINS THE LANE: fall through to the
// scoped content search. Only ever reached when cont_topic fired, i.e. the member supplied no
// topic of their own, so no real subject can be demoted by this.
if (cont_topic && (wantFb || wantWa)) { intent = 'question'; if (wantFb && !wantWa) { chat = null; } }"""

BLOCK = """// #52 TOPIC CONTINUATION BINDING (Eugene, live 2026-08-04 01:12 - the thumbs-down). He asked
// "Who are the best lenders in our portal?", got a good answer, then said "How about based on
// mentions in Facebook?" and was answered about NEWSLETTERS - the topic of an exchange 4.5h
// earlier. The router prompt ALREADY carries "resolve against the MOST RECENT exchange"; the
// router is Haiku and does not hold it against a 24h history window - the same lesson as the
// BARE AFFIRMATIONS rule, which is why the yes-binding became persisted STATE. So does this.
// A PURE-QUALIFIER continuation - a continuation opener plus a scope/source/recency word and
// NO topic of its own - takes its topic from the LAST turn's plan, whatever the router said.
// A continuation that DOES carry a topic ("how about tariffs?") is a new subject, untouched.
// The LANE still follows the current wording (LANE PRECEDENCE): "how about on Facebook" stays
// an FB-scoped search, it just searches for the RIGHT thing.
const CONT_OPEN = /^(?:and|but|so|ok(?:ay)?|now)?[\\s,]*(?:how|what|where|who|any(?:thing)?)?\\s*about\\b|^(?:and|but|also|what|how)[\\s,]+(?:in|on|from|via)\\b|^same\\s+(?:question|thing|but|for)\\b/i;
// Every word that describes WHERE/WHEN to look rather than WHAT to look for. What survives is
// the topic; nothing surviving means the member changed only the scope, not the subject.
const CONT_SCOPE = /\\b(and|but|so|ok|okay|now|how|what|where|who|which|about|if|same|question|thing|for|in|on|from|via|at|of|to|the|a|an|our|my|their|its|this|that|these|those|based|only|just|instead|also|other|others|else|more|any|anything|please|can|could|would|should|do|does|did|is|are|was|were|has|have|had|been|it|they|them|there|here|facebook|fb|group|whatsapp|whats|chat|chats|dm|dms|mds|portal|app|mention|mentions|mentioned|post|posts|posted|comment|comments|thread|threads|message|messages|said|say|says|saying|talk|talked|talking|discuss|discussed|discussion|week|weeks|month|months|day|days|year|years|today|yesterday|recent|recently|lately|new|latest|last|past|previous)\\b/g;
let cont_topic = null;
if (!bareAffirm && ctx.prev_plan) {
  const _c = rawText.replace(/[?!.]+$/, '').trim();
  if (_c.split(/\\s+/).length <= 8 && CONT_OPEN.test(_c)) {
    const residue = _c.toLowerCase().replace(/[^a-z0-9 ]+/g, ' ')
      .replace(CONT_SCOPE, ' ').split(/\\s+/)
      .filter(function (w) { return w.length >= 3; });
    if (!residue.length) {
      // The topic of the previous plan, wherever that lane keeps it.
      const _pv = ctx.prev_plan.params || {};
      const _rv = ctx.prev_plan.raw_params || {};
      let carried = [];
      if (Array.isArray(_pv.p_terms) && _pv.p_terms.length) { carried = _pv.p_terms; }
      else if (_pv.p_query) { carried = [_pv.p_query]; }
      else if (_pv.p_member) { carried = [_pv.p_member]; }
      else if (_pv.p_category) { carried = [_pv.p_category]; }
      else if (Array.isArray(_rv.p_terms) && _rv.p_terms.length) { carried = _rv.p_terms; }
      carried = carried.map(function (t) { return String(t || '').toLowerCase().trim(); })
        .filter(function (t) { return t.length >= 2; }).slice(0, 3);
      if (carried.length) { cont_topic = carried; p.search_terms = carried; followup = true; }
    }
  }
}

"""


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    pr = nodes["Plan Request"]["parameters"]["jsCode"]

    if MARK in pr:
        print("Plan Request already patched")
    else:
        assert pr.count(ANCHOR) == 1, f"anchor found {pr.count(ANCHOR)}x, expected 1 — aborting"
        assert "const bareAffirm" in pr, "bareAffirm missing — aborting"
        assert "ctx.prev_plan" in pr, "prev_plan missing — aborting"
        # bareAffirm and ctx must both be in scope ABOVE the insertion point
        assert pr.index("const bareAffirm") < pr.index(ANCHOR), "bareAffirm declared after anchor"
        pr = pr.replace(ANCHOR, BLOCK + ANCHOR)
        # cont_topic rides the return payload so probes can prove the binding fired
        assert pr.count("search_terms: terms, followup: followup") == 2, "expected 2 return sites"
        pr = pr.replace("search_terms: terms, followup: followup",
                        "search_terms: terms, cont_topic: cont_topic, followup: followup")
        nodes["Plan Request"]["parameters"]["jsCode"] = pr
        print("Plan Request patched (part 1: topic binding)")

    if MARK2 in pr:
        print("Plan Request already patched (part 2)")
    else:
        assert pr.count(ANCHOR2) == 1, f"anchor2 found {pr.count(ANCHOR2)}x, expected 1 — aborting"
        assert pr.index(ANCHOR) < pr.index(ANCHOR2), "cont_topic declared after its use"
        pr = pr.replace(ANCHOR2, ANCHOR2 + BLOCK2)
        nodes["Plan Request"]["parameters"]["jsCode"] = pr
        print("Plan Request patched (part 2: source steer wins the lane)")

    # syntax check the whole node body before it goes anywhere near n8n
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(nodes["Plan Request"]["parameters"]["jsCode"])
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

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    pr2 = next(n for n in wf2["nodes"] if n["name"] == "Plan Request")["parameters"]["jsCode"]
    print(f"VERIFY mark:{MARK in pr2} cont_topic_x2:{pr2.count('cont_topic: cont_topic') == 2} "
          f"active:{wf2.get('active')} version:{wf2.get('versionId', '')[:8]}")


if __name__ == "__main__":
    main()
