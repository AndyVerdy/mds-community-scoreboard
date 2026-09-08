#!/usr/bin/env python3
"""#141 lap 2: the pronoun carry covers the member-card lane and ranks the person's items by the message's
DISTINCTIVE words — apply to STAGING (on top of #141 + #144).

Found while proving the batch on staging b39b31ab (2026-09-08 01:00Z, exec 137893): this time the router put
"What is his firearms business called?" on the MEMBER-CARD lane (`op: member_card`, `p_member: Fred McKinnon`),
so the #141 carry (content_search only) never ran; the card has no firearms and the raw fetch searched his
NAME as a term (20 items that mention him) — his own posts (content_items 103886 "TLO Outdoors", 104754
"outdoor hunting/firearm/tactical gear") never came back and she said "nothing on file".

The raw search (`content_search_v2`) is full-text with an author filter: with `p_author` set, the rows that
match the terms rank first and the rest of the person's items fill the limit. Terms decide the ranking —
with [firearms, business, brand] his firearm posts fell out of the top 40; with [firearms] alone the TLO
Outdoors post ranks first. So only the message's distinctive words go in.

  Plan Request  pronounTopicTerms(rawText)   the distinctive words of the message (stop list + generic words
                                              such as business / brand / called removed), max 4 — pure,
                                              test_141_pronoun_subject.js runs it against this node's bytes.
                CARRY (both return sites)     op content_search OR member_card, raw_op content_search:
                                              raw p_author = the person, raw p_terms = [person] + distinctive
                                              words (+ the router's own distinctive terms), p_limit ≥ 40,
                                              default sources; the digest terms keep leading with the name
                                              on the content_search lane (unchanged from #141).

  python3 scripts/olivia_loop/apply_141b_topic_carry.py --dry-run DIR
  python3 scripts/olivia_loop/apply_141b_topic_carry.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries pronounTopicTerms(); requires the #141 CARRY (its anchor).
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "pronounTopicTerms"
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


FUNC = r"""// #141 lap 2 (exec 137893): the router put "What is his firearms business called?" on the member-card lane;
// the card has no firearms, his own posts do. The raw search is full-text, so only the message's DISTINCTIVE
// words rank his items (generic words such as business / brand / called dilute the ranking — with them his
// firearm posts fell out of the top 40). Pure function; test_141_pronoun_subject.js runs it.
function pronounTopicTerms(rawText) {
  const STOP = /^(what|whats|which|where|when|whom|whose|does|doing|done|did|this|that|these|those|there|their|theirs|they|them|have|has|had|been|being|about|tell|told|know|knows|please|could|would|should|will|want|wants|need|needs|name|named|names|called|call|calls|business|businesses|company|companies|brand|brands|based|located|location|from|with|into|more|also|again|anything|something|everything|nothing|else|other|others|hers|said|says|post|posts|posted|share|shared|talk|talked|mention|mentioned|mentions|info|information|details|detail|kind|type|sort|thing|things|really|still|ever|like|likes|work|works|working|sell|sells|selling|sold|make|makes|making|product|products|store|stores|shop|shops|member|members|group|chat|chats|much|many|some|only|just|then|than|over|under|here|were|give|gives|gave|gets|people|person|someone|anyone|everyone|exactly|actually|currently|right|today|year|years|time|times|best|good|great|well|come|comes|coming|going|find|found|look|looks|looking|show|shows|list|lists|part|parts|role|roles|owns|owner|owners|runs|running|start|started|founded|founder|full|main|primary|current|since|before|after|while|until|because|maybe|perhaps|whether|either|neither|both|each|every|most|least|less|very|quite|rather|pretty|already|whatever|whichever|specifically|specific|general|generally|different|same|similar|sure|okay|thanks|thank)$/i;
  const out = [];
  const seen = {};
  String(rawText || '').toLowerCase().replace(/[’']/g, '').split(/[^a-z0-9]+/).forEach(function (w) {
    if (out.length >= 4 || w.length < 4 || seen[w] || STOP.test(w)) { return; }
    seen[w] = 1;
    out.push(w);
  });
  return out;
}
"""

CARRY_OLD = (
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

CARRY_NEW = (
    "// #141: a bare third-person follow-up keeps the previous plan's person — scope the raw search to them and\n"
    "// lead the digest terms with their name, so their own posts are in front of the model.\n"
    "// #141 lap 2 (exec 137893): the member-card lane too — the card has no \"firearms business\", his posts do.\n"
    "// The raw search is full-text: the person's items are ranked by the message's DISTINCTIVE words only.\n"
    "try {\n"
    "  const _pronounWho = pronounSubject(rawText, ctx.prev_plan);\n"
    "  if (_pronounWho && raw_op === 'content_search' && (op === 'content_search' || op === 'member_card')) {\n"
    "    const _rt = [_pronounWho].concat(pronounTopicTerms(rawText));\n"
    "    ((raw_params && Array.isArray(raw_params.p_terms)) ? raw_params.p_terms : []).forEach(function (t) {\n"
    "      if (_rt.length < 8 && pronounTopicTerms(t).length && _rt.indexOf(String(t)) === -1) { _rt.push(String(t)); }\n"
    "    });\n"
    "    raw_params = Object.assign({}, raw_params || {}, { p_author: _pronounWho, p_terms: _rt,\n"
    "      p_limit: Math.max(Number((raw_params || {}).p_limit) || 0, 40) });\n"
    "    if (!Array.isArray(raw_params.p_sources) || !raw_params.p_sources.length) { raw_params.p_sources = ['fb_post', 'fb_comment', 'wa_message']; }\n"
    "    if (op === 'content_search') {\n"
    "      const _pt = Array.isArray(params.p_terms) ? params.p_terms.slice() : [];\n"
    "      if (_pt.indexOf(_pronounWho) === -1) { _pt.unshift(_pronounWho); }\n"
    "      params = Object.assign({}, params, { p_terms: _pt });\n"
    "    }\n"
    "    followup = true;\n"
    "  }\n"
    "} catch (e) {}\n"
)

ANCHOR = "// #143 FOLLOW-UP GUARDS (bank C 6095 / 6349"


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
    if "pronounSubject" not in code:
        sys.exit(f"ABORT {NODE}: #141 not present — apply #141 first")
    c = code.count(ANCHOR)
    if c != 1:
        sys.exit(f"ABORT {NODE}: expected 1 anchor, found {c}")
    c = code.count(CARRY_OLD)
    if c != 2:
        sys.exit(f"ABORT {NODE}: expected the #141 CARRY at both return sites (2), found {c}")
    code = code.replace(ANCHOR, FUNC + ANCHOR).replace(CARRY_OLD, CARRY_NEW)
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
        print(f"  {NODE}: pronounTopicTerms() in, CARRY widened to the member-card lane (both return sites), node --check OK")
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
