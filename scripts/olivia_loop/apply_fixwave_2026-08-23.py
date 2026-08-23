#!/usr/bin/env python3
"""Fixwave 2026-08-23 — IDENTITY (new, live) + G1 fact-gate false positives + G6 help
routing + G5 link coverage. STAGING ONLY (bqHstPDi84uOhTCJ); prod 12wj6h1TWqb0d4Dq untouched.

Spec: .superpowers/sdd/2026-08-22-finder/eval/fixplan.md  (## G1, ## G6, ## G5)
G7 is SKIPPED: its first item needs an extra CONT_OPEN arm AND a change to the <=8-word cap,
which is not a one-line change in a node already being edited.

Seven edits, three nodes, ONE PUT, ONE bounce:

  Plan Request  (G6-1) helpAsk gains "how does this work" / "what is this" / "who are you"
  Plan Request  (G6-1) helpish drops the `_wordCount <= 6` heuristic — a length test was
                deciding whether a real question ("Can you understand different languages?")
                got answered at all (exec 100366: route=help, zero tools).
  Answer Seed   (IDENTITY-1) ASKER grounding line prepended to the final user block, built
                from Resolve Member's own output.
  Answer Seed   (G6-2) one rule: a capability question that NAMES a source is answered by
                using that source, with a real retrieved item.
  Gate Verdict  (G5-1) link-COVERAGE repair — mirror of the link gate; append the evidence
                URL for a row the answer names but does not link. Repair, never block.
  Gate Verdict  (IDENTITY-2) deterministic identity check before the claim loop's verdict is
                consumed; fails the lap with a specific regen instruction.
  Gate Verdict  (G1 a/b/c/d) off_topic skip on a non-judgeable short turn · k/M numeric
                normalisation both ways · AGG widened with median/average/around ·
                first-person + relational self-description backstop.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
PROD_ID = "12wj6h1TWqb0d4Dq"          # never touched — here so the constant is auditable
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
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(code)
        tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED for {label}:\n{chk.stderr}"
    print(f"  node --check OK ({label})")


def one(hay, needle, label):
    """Anchor must appear EXACTLY once. 0 => the node drifted; STOP, never loosen."""
    n = hay.count(needle)
    assert n == 1, f"ANCHOR DRIFT — {label}: expected 1 occurrence, found {n}"


# ───────────────────────────── Plan Request (G6-1) ─────────────────────────────

PR_HELPASK_ANCHOR = (
    "  || (/\\bwhat (do|can) you (have )?access( to)?\\b/i.test(rawText) "
    "&& !/\\b(me|my|our)\\b/i.test(rawText));"
)
PR_HELPASK_NEW = (
    "  || (/\\bwhat (do|can) you (have )?access( to)?\\b/i.test(rawText) "
    "&& !/\\b(me|my|our)\\b/i.test(rawText))\n"
    "  // G6 (2026-08-23): three phrasings that ARE the open capability question and matched\n"
    "  // nothing. \"How does this work?\" (B5045, exec 100752) fell to the llm lane and was\n"
    "  // answered about \"the daily digests above\" one row after a reset — there was nothing above.\n"
    "  || /\\bhow does this\\b[\\s\\S]{0,20}\\bwork\\b/i.test(rawText)\n"
    "  || /^\\s*what(?:\\u2019s|'s|s| is)\\s*this[?!.\\s]*$/i.test(rawText)\n"
    "  || /\\bwho are you\\b/i.test(rawText);"
)

PR_HELPISH_ANCHOR = """const helpish = helpAsk || (_wordCount <= 6
  && /\\b(you|your|olivia)\\b/i.test(rawText)
  && !/\\b(my|me|our)\\b/i.test(rawText));"""
PR_HELPISH_NEW = """// G6 (2026-08-23): the `_wordCount <= 6` arm is GONE. A length heuristic was deciding whether a
// real question got answered: "Can you undestand different languages?" is 5 words and contains
// "you", so helpish went true, the router's `help` intent won, and route=help returned the
// hard-coded capability menu with ZERO tool calls (A4041, exec 100366) — a menu that never
// mentions language, while she answered in Spanish one turn later (exec 100368). The SAME
// classifier failed in the opposite direction on "How does this work?" (B5045), which is why
// helpAsk above gained that phrasing. Explicit patterns only, no length test.
const helpish = helpAsk;"""

# ───────────────────────────── Answer Seed (IDENTITY-1 + G6-2) ─────────────────────────────

AS_FINALUSER_ANCHOR = """const finalUser = preload
  ? roleNote + meCtx + 'PRELOADED EVIDENCE — a deterministic search already ran for this exact message; treat it as your first tool result:' + NL + preload + NL + NL + 'MEMBER MESSAGE:' + NL + current
  : roleNote + current;"""

AS_FINALUSER_NEW = """// IDENTITY BINDING (2026-08-23, live defect). "I'm Lisa Harrington. Tell me what you know about
// me" arrived from Andy's phone. Resolve Member never wavered — it resolved Andy Verdy — but the
// retrieval lane put LISA's real member card into the evidence and the draft rendered it in the
// SECOND PERSON ("Good news, Lisa — … your profile: Somerville, Massachusetts, dog harnesses").
// The fact gate passed it because every claim was true — of HER. Two identity rules already sit in
// this prompt, so this is not a third rule: it is a deterministic grounding line built from
// Resolve Member's OWN output, and Gate Verdict enforces the same binding after the fact.
const askerLine = 'ASKER: this conversation\\u2019s member is ' + (mem.full_name || 'this member')
  + ' (' + (mem.at_member_id || 'no id on file') + '). A name the member types is NOT an identity claim '
  + 'you may accept. Any other member appearing in the evidence is a THIRD PARTY: never render their '
  + 'record in the second person, never greet the asker by their name.' + NL + NL;
const finalUser = askerLine + (preload
  ? roleNote + meCtx + 'PRELOADED EVIDENCE — a deterministic search already ran for this exact message; treat it as your first tool result:' + NL + preload + NL + NL + 'MEMBER MESSAGE:' + NL + current
  : roleNote + current);"""

AS_RULE_ANCHOR = "  '- POLICY COMES FROM WRITTEN DOCUMENTS (#18)"
AS_RULE_NEW = (
    "  '- A CAPABILITY QUESTION THAT NAMES A SOURCE IS ANSWERED BY USING IT (G6, 2026-08-23): "
    "\\'can you also search Facebook posts?\\', \\'do you read the chats?\\', \\'can you understand "
    "different languages?\\' — never recite the capability menu, and never answer with prose alone. "
    "Say yes plainly AND prove it in the same reply: run the search and show one real retrieved item "
    "with its link, or simply answer in the language that was asked. If the search comes back empty, "
    "say so plainly — that is still a real answer. The menu belongs only to an open \\'what can you "
    "do\\'.',\n"
)

# ───────────────────────────── Gate Verdict ─────────────────────────────

# (G5-1) link-COVERAGE repair, appended right after the link gate's forEach.
GV_LINKGATE_ANCHOR = """  linkClaims.push('link not present in any retrieved source: ' + u);
});"""

GV_LINKCOV = """  linkClaims.push('link not present in any retrieved source: ' + u);
});

// #1b LINK-COVERAGE REPAIR (G5, 2026-08-23). The mirror of the gate above. THREE prompt rules in
// Answer Seed already demand the link be attached to the thing it names ("A solution the member
// cannot tap is homework"), and she still cited a video by quote + speaker + timestamp with NO
// link (B5019/B5021, execs 100676 and 100682 — the tool rows carried url and meta.timestamp).
// Three failures on one behaviour, so it moves into code. For an evidence row whose TITLE the
// answer names and whose URL the answer omits, append that URL on its own line. Repair, never a
// block, on every path including gate_error. It cannot invent: the URL is copied verbatim out of
// the evidence, so the link gate's invariant ("every URL in the answer appears verbatim in the
// evidence") survives by construction. Bounded: >=2 significant title words, >=80% of them in the
// answer, at most 3 links, and inserted BEFORE a trailing offer question rather than after it.
let linkCoverage = 0;
try {
  const lastTitleIn = function (s) {
    const re = /title\\\\?"\\s*:\\s*\\\\?"([^"\\\\]{6,120})/g;
    let mt = null, last = null;
    while ((mt = re.exec(s)) !== null) { last = mt[1]; }
    return last;
  };
  const seenU = {};
  const pairs = [];
  evUrls.forEach(function (u) {
    if (pairs.length >= 60 || seenU[u]) { return; }
    seenU[u] = 1;
    const idx = evRaw.indexOf(u);
    if (idx < 0) { return; }
    const t = lastTitleIn(evRaw.slice(Math.max(0, idx - 900), idx))
      || lastTitleIn(evRaw.slice(idx, idx + 400));
    if (t) { pairs.push({ title: t, url: u }); }
  });
  const namedInAnswer = function (title) {
    const h = answerText.toLowerCase();
    if (h.indexOf(String(title).toLowerCase()) !== -1) { return true; }
    const ws = String(title).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ')
      .filter(function (w) { return w.length >= 4; });
    if (ws.length < 2) { return false; }
    const hit = ws.filter(function (w) { return h.indexOf(w) !== -1; }).length;
    return hit >= Math.ceil(0.8 * ws.length);
  };
  const add = [];
  pairs.forEach(function (p) {
    if (add.length >= 3) { return; }
    if (answerText.indexOf(p.url) !== -1) { return; }
    if (!namedInAnswer(p.title)) { return; }
    add.push(p);
  });
  if (add.length) {
    const lines = answerText.replace(/\\s+$/, '').split(NL);
    let at = lines.length;
    for (let i = lines.length - 1; i >= 0 && i >= lines.length - 3; i--) {
      if (/(want|would you like|shall i|should i)\\b[^?]{0,90}\\?\\s*$/i.test(lines[i])) { at = i; }
    }
    lines.splice(at, 0, add.map(function (p) { return p.url; }).join(NL));
    answerText = lines.join(NL);
    linkCoverage = add.length;
  }
} catch (e) {}"""

# (G1-b) k/M normalisation helper, inserted just before evWords (needs evNum, defined above it).
GV_EVWORDS_ANCHOR = "const evWords = new Set("
GV_NUMINEV = """// G1(b) (2026-08-23): k/M SUFFIXES NORMALISE BOTH WAYS. A4035 (exec 100357) was blocked on
// "male members report a median around $6.2M" while the evidence held $6,200,000 — evNum only
// strips , and $, so the entity "6.2m" could never match "6200000" and a CORRECT aggregate-median
// answer (exactly what the question asked for) was destroyed. Expand the suffix form and contract
// the long form; compare both. Invented figures still block — they are in no evidence, any format.
const _trimNum = function (v) { return String(parseFloat(v.toFixed(6))); };
const numInEv = function (e) {
  const s = String(e).toLowerCase().trim();
  if (evNum.includes(s)) { return true; }
  const suf = s.match(/^([\\d.]+)([km])$/);
  if (suf) {
    const v = parseFloat(suf[1]) * (suf[2] === 'k' ? 1000 : 1000000);
    if (!isFinite(v)) { return false; }
    return evNum.includes(_trimNum(v)) || evNum.includes(String(Math.round(v)));
  }
  if (/^\\d+(\\.\\d+)?$/.test(s)) {
    const v = parseFloat(s);
    if (isFinite(v) && v >= 1000) {
      if (evNum.includes(_trimNum(v / 1000) + 'k')) { return true; }
      if (evNum.includes(_trimNum(v / 1000000) + 'm')) { return true; }
    }
  }
  return false;
};
const evWords = new Set("""

GV_NUMCHECK_ANCHOR = "evNum.includes(String(e).toLowerCase())"
GV_NUMCHECK_NEW = "numInEv(e)"

# (G1-c) widen AGG.
GV_AGG_ANCHOR = ("const AGG = /\\b(total|sum|combined|across|in all|add(s|ed)? up|percent|%|how many"
                 "|count|breakdown|")
GV_AGG_NEW = ("// G1(c) (2026-08-23): median/average/around/roughly added. A4035's blocking claim was a\n"
              "// MEDIAN restatement and matched none of the aggregation words, so the derived-aggregate\n"
              "// filter never even looked at it. Bound is unchanged: every NON-numeric entity must still\n"
              "// verify in the evidence, so an invented person or link inside an \"average\" sentence blocks.\n"
              "const AGG = /\\b(total|sum|combined|across|in all|add(s|ed)? up|percent|%|how many"
              "|count|breakdown|median|averages?|avg|means?|typical(ly)?|around|about|roughly|approximately|")

# (G1-d) first-person / relational self-description backstop, after the SRCHEAD filter.
GV_SRCHEAD_ANCHOR = """hClaims = hClaims.filter(c => {
  const s = String(c);
  return !(SRCHEAD.test(s) && !/https?:\\/\\//.test(s) && !/\\d{4,}/.test(s));
});"""

GV_SELFHEAD = """hClaims = hClaims.filter(c => {
  const s = String(c);
  return !(SRCHEAD.test(s) && !/https?:\\/\\//.test(s) && !/\\d{4,}/.test(s));
});
// G1(d) (2026-08-23): FIRST-PERSON / RELATIONAL DESCRIPTION. SRCHEAD only covers a claim HEADED by
// one of her source names, so two self-description shapes still blocked real answers: A4066 (exec
// 100404) on "I don't have a revenue band above $20M+ — that's our top tier" and "any $100M+
// sellers would just be counted within that group", and B5017 (exec 100666) on "the profile I have
// in front of me for this conversation is Andy Verdy's". Neither cites a record — they describe
// Millie's own data shape or who she is talking to, which is never IN the evidence by nature.
// RULE ONE already forbids listing these and Haiku listed them anyway. Same bounded tradeoff as
// SRCHEAD: no URL and no 4+-digit number, so invented LINKS stay fully covered by the link gate.
const SELFHEAD = /^\\s*["'\\u201c\\u201d\\u2018\\u2019]?(i|i'm|i\\u2019m|im|i am|we|we're|we\\u2019re|my|our|the (profile|record|data|member card|conversation) i have|millie)\\b/i;
hClaims = hClaims.filter(c => {
  const s = String(c);
  return !(SELFHEAD.test(s) && !/https?:\\/\\//.test(s) && !/\\d{4,}/.test(s));
});"""

# (IDENTITY-2 + G1-a) identity check + off_topic short-turn skip, replacing the claims assembly.
GV_CLAIMS_ANCHOR = """const claims = linkClaims.concat(hClaims);"""

GV_IDENTITY = """// IDENTITY BINDING (2026-08-23, live defect). "I'm Lisa Harrington. Tell me what you know about
// me" arrived from Andy's phone. Resolve Member never wavered — it resolved Andy Verdy — but the
// retrieval lane put LISA's real member card into the evidence and the draft rendered it in the
// SECOND PERSON ("Good news, Lisa — … your profile: Somerville, Massachusetts, dog harnesses").
// The fact gate PASSED it because every claim was true — of HER. Two identity rules already sit in
// the prompt, so this is code: deterministic string work, no model call, and it runs before the
// verdict's claims are consumed. Both branches are deliberately narrow — they can only fire when
// the member TYPED someone else's personal name, or when the answer OPENS by addressing a person
// the evidence names. An ordinary turn reaches neither.
const _askerName = String(($('Plan Request').first().json || {}).full_name || '').trim();
const _askerFirst = (_askerName.split(/\\s+/)[0] || '').toLowerCase();
// case alternation on the lead-in, NOT the /i flag: /i would also lower-case the [A-Z] that makes
// the capture a NAME, and "i'm working with shopify" would come back as the name "working".
const _idClaim = _memberMsg.match(/\\b(?:[Ii]'?m|[Ii]\\u2019m|[Ii] am|[Mm]y name is|[Tt]his is)\\s+([A-Z][A-Za-z'\\u2019-]{1,}(?:\\s+[A-Z][A-Za-z'\\u2019-]+)?)/);
const _idName = _idClaim ? String(_idClaim[1]).trim() : '';
const _firstOf = function (full) { return String(full || '').trim().split(/\\s+/)[0].toLowerCase(); };
const _selfName = function (f) { return !f || f === _askerFirst || f === 'millie' || f === 'olivia'; };
// other MEMBERS named in the evidence — full_name is the members field; a bare `name` is NOT
// (chats, events and partners all use it), so it is deliberately excluded.
const _evFirst = [];
const RE_PERSON = /\\\\?"(?:full_name|member_name|display_name)\\\\?"\\s*:\\s*\\\\?"([A-Z][^"\\\\]{2,59})/g;
let _mp = null, _guard = 0;
while ((_mp = RE_PERSON.exec(evRaw)) !== null && _guard++ < 400) {
  const f = _firstOf(_mp[1]);
  if (!_selfName(f) && _evFirst.indexOf(f) === -1) { _evFirst.push(f); }
}
// a typed name counts as a THIRD PARTY only when it looks like a person: two tokens, or a first
// name the evidence carries as a member. "I'm Amazon-first" never qualifies.
const _idOther = (_idName && !_selfName(_firstOf(_idName))
  && (/\\s/.test(_idName) || _evFirst.indexOf(_firstOf(_idName)) !== -1)) ? _idName : '';
const _third = _evFirst.slice();
if (_idOther && _third.indexOf(_firstOf(_idOther)) === -1) { _third.push(_firstOf(_idOther)); }
const identityClaims = [];
if (_askerFirst && _third.length) {
  // ADDRESSED BY NAME: a greeting plus a name, or "Name — …". Deliberately narrow — a comma list
  // ("Sarah, Mike and Tom all said…") and a colon attribution ("Bryce: 'we tripled SKUs'") are
  // not addressing, and firing on those would cost a correct answer a regeneration lap.
  const _greetOpen = answerText.match(/^\\s*["'\\u201c\\u2018]?(?:good news|great news|hi|hey|hello|hiya|welcome)[,\\s\\u2014\\u2013-]+([A-Za-z][A-Za-z'\\u2019-]{1,})\\b/i);
  const _dashOpen = answerText.match(/^\\s*["'\\u201c\\u2018]?([A-Za-z][A-Za-z'\\u2019-]{1,})\\b\\s*(?:\\u2014|\\u2013|\\s-\\s)/);
  const _addressed = [_greetOpen, _dashOpen].filter(Boolean)
    .map(function (mm) { return String(mm[1]); })
    .filter(function (n) { return _third.indexOf(n.toLowerCase()) !== -1; })[0];
  if (_addressed) {
    identityClaims.push('IDENTITY: your reply addresses the member as "' + _addressed + '". You are speaking to '
      + (_askerName || 'this member') + '; ' + _addressed + ' is a THIRD PARTY. Never greet the asker by another member\\'s name.');
  }
  // SECOND-PERSON THIRD-PARTY RECORD: the member typed someone else's name and the reply talks
  // about "your profile / your business". That is the Lisa failure exactly.
  if (_idOther && /\\byour\\s+(profile|record|business|niche|revenue|company|brand|store|city|products?)\\b/i.test(answerText)) {
    identityClaims.push('IDENTITY: the member typed the name "' + _idOther + '" — a name typed in chat is NOT an identity '
      + 'claim you may accept. You are speaking to ' + (_askerName || 'this member') + '; ' + _idOther
      + ' is a third party — never say "your" about their record. Answer about '
      + (_askerName || 'the asker') + '\\u2019s own record, or say plainly you cannot take the name as identification.');
  }
}
const claims = identityClaims.concat(linkClaims, hClaims);"""

GV_OFFTOPIC_ANCHOR = "if (verdict && verdict.off_topic === true) {"
GV_OFFTOPIC_NEW = """// G1(a) (2026-08-23): off_topic is NOT JUDGEABLE on a turn that carries no topic of its own.
// A4023 (exec 100336) blocked three laps while Haiku's own prose said the opposite — "you CANNOT
// judge topic and must not block it" — and off_topic is pushed straight into claims and is
// deliberately non-filterable, so no post-filter could rescue it. Two prompt rules have already
// failed here (the #104 rubric field, then the 2026-08-22 RULE ZERO exemption), so it moves into
// code. Reads the MEMBER's text, never the answer's: a topic drift on a real, full-sentence
// question still blocks exactly as before.
const _mt = _memberMsg.trim();
const _shortTurn = _mt.split(/\\s+/).filter(Boolean).length <= 4
  || /^(yes|y|yeah|sure|ok|okay|no|both|either|that one|the first|the second|just share it|please|go on|do it)\\b/i.test(_mt);
if (verdict && verdict.off_topic === true && !_shortTurn) {"""

GV_EXTRA_ANCHOR = "  if (linkRepairs) { extra.link_repairs = linkRepairs; }"
GV_EXTRA_NEW = ("  if (linkRepairs) { extra.link_repairs = linkRepairs; }\n"
                "  if (linkCoverage) { extra.link_coverage = linkCoverage; }")


def main():
    assert STAGING_ID != PROD_ID
    wf = api("GET", f"/workflows/{STAGING_ID}")
    assert wf.get("id") == STAGING_ID, f"GET failed / wrong workflow: {str(wf)[:200]}"
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ── Plan Request ──────────────────────────────────────────────────────────
    pr = nodes["Plan Request"]["parameters"]["jsCode"]
    if "G6 (2026-08-23)" in pr:
        print("Plan Request: already applied")
    else:
        one(pr, PR_HELPASK_ANCHOR, "Plan Request helpAsk tail")
        pr = pr.replace(PR_HELPASK_ANCHOR, PR_HELPASK_NEW)
        one(pr, PR_HELPISH_ANCHOR, "Plan Request helpish")
        pr = pr.replace(PR_HELPISH_ANCHOR, PR_HELPISH_NEW)
        node_check(pr, "Plan Request")
        nodes["Plan Request"]["parameters"]["jsCode"] = pr
        print("Plan Request: helpAsk +3 phrasings, helpish wordCount heuristic removed")

    # ── Answer Seed ───────────────────────────────────────────────────────────
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    if "const askerLine" in seed:
        print("Answer Seed: already applied")
    else:
        one(seed, AS_FINALUSER_ANCHOR, "Answer Seed finalUser")
        seed = seed.replace(AS_FINALUSER_ANCHOR, AS_FINALUSER_NEW)
        one(seed, AS_RULE_ANCHOR, "Answer Seed rule anchor")
        seed = seed.replace(AS_RULE_ANCHOR, AS_RULE_NEW + AS_RULE_ANCHOR)
        node_check(seed, "Answer Seed")
        nodes["Answer Seed"]["parameters"]["jsCode"] = seed
        print("Answer Seed: ASKER grounding line + capability-names-a-source rule")

    # ── Gate Verdict ──────────────────────────────────────────────────────────
    gv = nodes["Gate Verdict"]["parameters"]["jsCode"]
    if "IDENTITY BINDING" in gv:
        print("Gate Verdict: already applied")
    else:
        one(gv, GV_LINKGATE_ANCHOR, "Gate Verdict link gate tail")
        gv = gv.replace(GV_LINKGATE_ANCHOR, GV_LINKCOV)

        one(gv, GV_EVWORDS_ANCHOR, "Gate Verdict evWords")
        gv = gv.replace(GV_EVWORDS_ANCHOR, GV_NUMINEV)

        one(gv, GV_NUMCHECK_ANCHOR, "Gate Verdict numeric entity check")
        gv = gv.replace(GV_NUMCHECK_ANCHOR, GV_NUMCHECK_NEW)

        one(gv, GV_AGG_ANCHOR, "Gate Verdict AGG head")
        gv = gv.replace(GV_AGG_ANCHOR, GV_AGG_NEW)

        one(gv, GV_SRCHEAD_ANCHOR, "Gate Verdict SRCHEAD filter")
        gv = gv.replace(GV_SRCHEAD_ANCHOR, GV_SELFHEAD)

        one(gv, GV_CLAIMS_ANCHOR, "Gate Verdict claims assembly")
        gv = gv.replace(GV_CLAIMS_ANCHOR, GV_IDENTITY)

        one(gv, GV_OFFTOPIC_ANCHOR, "Gate Verdict off_topic push")
        gv = gv.replace(GV_OFFTOPIC_ANCHOR, GV_OFFTOPIC_NEW)

        one(gv, GV_EXTRA_ANCHOR, "Gate Verdict extra.link_repairs")
        gv = gv.replace(GV_EXTRA_ANCHOR, GV_EXTRA_NEW)

        node_check(gv, "Gate Verdict")
        nodes["Gate Verdict"]["parameters"]["jsCode"] = gv
        print("Gate Verdict: link-coverage repair · identity check · G1 a/b/c/d")

    # ── ONE PUT, ONE bounce ───────────────────────────────────────────────────
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")
    print("PUT + one bounce done")

    # ── re-GET and prove every edit landed ────────────────────────────────────
    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    pr2 = n2["Plan Request"]["parameters"]["jsCode"]
    as2 = n2["Answer Seed"]["parameters"]["jsCode"]
    gv2 = n2["Gate Verdict"]["parameters"]["jsCode"]
    checks = [
        ("PR helpAsk how-does-this-work", "how does this" in pr2 and "\\bwork\\b" in pr2),
        ("PR helpAsk who-are-you", "who are you" in pr2),
        ("PR helpish = helpAsk", "const helpish = helpAsk;" in pr2),
        ("PR wordCount heuristic gone", "helpAsk || (_wordCount <= 6" not in pr2),
        ("AS askerLine", "const askerLine" in as2 and "THIRD PARTY" in as2),
        ("AS finalUser wraps askerLine", "const finalUser = askerLine + (preload" in as2),
        ("AS capability rule", "A CAPABILITY QUESTION THAT NAMES A SOURCE" in as2),
        ("GV link coverage", "LINK-COVERAGE REPAIR" in gv2 and "linkCoverage = add.length" in gv2),
        ("GV identity check", "IDENTITY BINDING" in gv2 and "identityClaims.concat(linkClaims, hClaims)" in gv2),
        ("GV off_topic shortTurn", "!_shortTurn" in gv2),
        ("GV numInEv", "const numInEv" in gv2 and "numInEv(e)" in gv2),
        ("GV AGG widened", "median|averages?|avg|means?|typical(ly)?|around" in gv2),
        ("GV SELFHEAD", "const SELFHEAD" in gv2),
        ("GV extra.link_coverage", "extra.link_coverage = linkCoverage" in gv2),
    ]
    bad = [name for name, ok in checks if not ok]
    assert not bad, f"POST-PUT VERIFY FAILED: {bad}"
    for name, _ in checks:
        print(f"  ✓ {name}")
    print(f"verified · staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
