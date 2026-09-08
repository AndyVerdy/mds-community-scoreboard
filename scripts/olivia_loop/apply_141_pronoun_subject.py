#!/usr/bin/env python3
"""#141: a bare third-person follow-up keeps the previous turn's person — apply to STAGING (on top of #143).

Verified still present 2026-09-08 00:39Z (staging eb99c336 → aa649e7b, bank C 6500, exec 137838): after two
turns about Fred McKinnon ("Where is Fred based…", "What is Fred's business brand name?"), "What is his
firearms business called?" was planned as a topic search for "fred firearms"; the evidence filled with
Tamkin Collins's firearms posts, the model rebound "his" to her and told the member "nothing on file ties
Fred to a firearms brand" — while Fred's own posts ("My brand is outdoor hunting/firearm/tactical gear…",
content_items 104754 / 105132) never came back because nothing scoped the search to him.

  Plan Request  pronounSubject(rawText, prevPlan): a message of ≤16 words carrying a third-person pronoun
                and no new capitalised name returns the person the previous plan was about (p_member of a
                member-card turn, p_author of an author-scoped search). On a content_search plan the raw
                search is scoped to that author (p_author) and their name leads the digest terms, so their
                own posts are in front of the model and the seed's ANSWER THE THING ON THE TABLE rule has
                something to bind to. Pure function; test_141_pronoun_subject.js runs it.

  python3 scripts/olivia_loop/apply_141_pronoun_subject.py --dry-run DIR
  python3 scripts/olivia_loop/apply_141_pronoun_subject.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries the #141 marker; requires #143 (its anchor).
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#141"
NODE = "Plan Request"


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


FUNC = r"""// #141 PRONOUN FOLLOW-UP KEEPS THE PERSON (staging exec 137838, 2026-09-08). After two turns about Fred
// McKinnon, "What is his firearms business called?" ran a topic search for "fred firearms", the evidence
// filled with another member's firearms posts, and "his" was rebound to her. A short third-person
// follow-up with no new name keeps the person the previous plan was about. Pure function;
// scripts/olivia_loop/test_141_pronoun_subject.js runs it against this node's own bytes.
function pronounSubject(rawText, prevPlan) {
  const t = String(rawText || '').trim();
  if (!t || t.split(/\s+/).filter(Boolean).length > 16) { return null; }
  if (!/\b(he|him|his|she|her|hers|they|them|their|theirs)\b/i.test(t)) { return null; }
  const NOTNAME = /^(I|MDS|TikTok|Amazon|Facebook|Shopify|Summit|Singapore|Inspire|WhatsApp|TTS|PPC|FBA|SQP|Zoom|Walmart|Google|Meta|Claude|Instagram|YouTube|Etsy|eBay|Target|Costco|Prime|Vine|Slack)$/i;
  const toks = t.replace(/[^A-Za-z’' -]+/g, ' ').trim().split(/\s+/);
  for (let i = 1; i < toks.length; i++) {
    const w = toks[i].replace(/[’']s$/, '');
    if (/^[A-Z][a-z]/.test(w) && !NOTNAME.test(w)) { return null; }
  }
  const p = (prevPlan && typeof prevPlan === 'object' && prevPlan.params && typeof prevPlan.params === 'object') ? prevPlan.params : null;
  if (!p) { return null; }
  const who = String(p.p_member || p.p_author || '').trim();
  if (!who || !/^[A-Za-z][A-Za-z’'.-]+(\s+[A-Za-z][A-Za-z’'.-]+){1,3}$/.test(who)) { return null; }
  return who;
}
"""

CARRY = (
    "// #141: a bare third-person follow-up keeps the previous plan's person — scope the raw search to them and\n"
    "// lead the digest terms with their name, so their own posts are in front of the model.\n"
    "try {\n"
    "  const _pronounWho = pronounSubject(rawText, ctx.prev_plan);\n"
    "  if (_pronounWho && op === 'content_search' && raw_op === 'content_search') {\n"
    "    raw_params = Object.assign({}, raw_params, { p_author: _pronounWho });\n"
    "    const _pt = Array.isArray(params.p_terms) ? params.p_terms.slice() : [];\n"
    "    if (_pt.indexOf(_pronounWho) === -1) { _pt.unshift(_pronounWho); }\n"
    "    params = Object.assign({}, params, { p_terms: _pt });\n"
    "    followup = true;\n"
    "  }\n"
    "} catch (e) {}\n"
)

RET1 = "return [{ json: { first_contact: first_contact, ticket_ask: ticketAsk, window_days: askWindowDays, all_sources: allSources, not_in_chat: notInChat, route: route, intent: intent, focus_chat: null, offer_bind: offerBind,"
RET2 = "return [{ json: { first_contact: first_contact, ticket_ask: ticketAsk, window_days: askWindowDays, all_sources: allSources, not_in_chat: notInChat, route: route, intent: intent, focus_chat: chat, offer_bind: offerBind,"

EDITS = [
    ("// #143 FOLLOW-UP GUARDS (bank C 6095 / 6349", FUNC + "// #143 FOLLOW-UP GUARDS (bank C 6095 / 6349"),
    (RET1, CARRY + RET1),
    (RET2, CARRY + RET2),
]


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def patch_code(code):
    if MARK in code:
        return code, False
    if "#143" not in code:
        sys.exit(f"ABORT {NODE}: #143 not present — apply #143 first")
    for old, new in EDITS:
        c = code.count(old)
        if c != 1:
            sys.exit(f"ABORT {NODE}: expected 1 occurrence, found {c}\n  {old[:100]!r}")
        code = code.replace(old, new)
    return code, True


def main():
    dry = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run" else None
    wf = api("GET", f"/workflows/{STAGING_ID}")
    if wf.get("id") != STAGING_ID:
        sys.exit(f"GET failed: {json.dumps(wf)[:300]}")
    print(f"staging {STAGING_ID} versionId {wf.get('versionId')} nodes {len(wf['nodes'])}")
    node = next((n for n in wf["nodes"] if n["name"] == NODE), None)
    if node is None:
        sys.exit(f"ABORT: node {NODE} not found")
    code, changed = patch_code(node["parameters"]["jsCode"])
    if changed:
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {NODE}: node --check failed\n{err}")
        node["parameters"]["jsCode"] = code
        print(f"  {NODE}: pronounSubject() + carry (2 returns), node --check OK")
    else:
        print(f"  {NODE}: already carries {MARK}, skipped")
    if dry:
        os.makedirs(dry, exist_ok=True)
        path = os.path.join(dry, "Plan_Request.js")
        open(path, "w").write(code)
        print(f"  wrote {path}\ndry run: nothing written to n8n")
        return
    if not changed:
        print("nothing to do")
        return
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok, versionId", r.get("versionId"))
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"))


if __name__ == "__main__":
    main()
