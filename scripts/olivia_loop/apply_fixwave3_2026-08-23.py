#!/usr/bin/env python3
"""Fixwave 3 — 2026-08-23. The five survivors of the previous wave, re-confirmed on staging
versionId 10357dea. STAGING ONLY (bqHstPDi84uOhTCJ); prod 12wj6h1TWqb0d4Dq is never touched.

Spec: .superpowers/sdd/2026-08-22-finder/eval/fixplan.md (## G4, ## G5, ## G7)
Evidence: .superpowers/sdd/2026-08-22-finder/eval/rerun2_pairs.json

  1. OFFER BINDING BECOMES PERSISTED STATE (A4014, #112 AC #1 — never built; a fourth
     acceptance regex shipped instead). Format Reply records the items an answer put in front
     of the member; Save Conversation persists them on the olivia row's `plan` (the channel
     prev_plan already rides); Prep Context hands them back as ctx.prev_offer; Plan Request
     resolves the acceptance against that list and emits plan.offer_bind; Answer Seed RENDERS
     the decision and its four acceptance regexes are DELETED.
  2. ELEMENT COVERAGE (A4071, B5039). Gate Verdict gains a URL-FIELD coverage repair
     (registration_url / event_url / url whose owner the answer names) and a deterministic
     "the member named two sources and you used one" regeneration.
  3. GATED REFUSAL MUST NOT LIST NAMES (B5015). Gate Verdict blocks a lap when a tool result
     carries an event/chat/aggregate denial and the reply still carries >=3 member names.
  4. NO INTERNAL VOCABULARY (A4077). Gate Verdict regenerates on backend words outside the
     member's own quoted text.
  5. ADJACENT-TURN REFERENT (A4061, B5017). Plan Request gains an explicit-anaphor arm on the
     continuation carry; Answer Seed + Gate Verdict require a declined identity claim to go on
     and ANSWER for the real asker.

Folded in from the data-side agent's live findings (same wave, same PUT):
  6. B5025 — video_search_v2.p_call_type works and the model never sent it. The tool schema's
     allowed values are replaced with the ones that actually exist in videos_catalog.call_type
     (read live), and Plan Request sets the filter IN CODE on the videos lane.
  7. A4095 — the verbatim digest lane asked for p_limit 1 and read rows[0] while digest.summaries
     held every day of the asked window. Plan Request passes an explicit day count through and
     Build Verbatim Digest concatenates the rows and labels the window it actually covers.

Seven nodes, ONE PUT, ONE deactivate->activate bounce, re-GET + assert.
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


def expr_check(expr, label):
    """n8n expression '={{ <js> }}' — syntax-check the JS inside the braces."""
    inner = expr.strip()
    assert inner.startswith("={{") and inner.endswith("}}"), f"{label}: not an n8n expression"
    node_check("const _x = " + inner[3:-2] + ";", label)


def one(hay, needle, label):
    """Anchor must appear EXACTLY once. 0 => the node drifted; STOP, never loosen."""
    n = hay.count(needle)
    assert n == 1, f"ANCHOR DRIFT — {label}: expected 1 occurrence, found {n}"


# ══════════════════════════ 1 · Prep Context — carry the offer ══════════════════════════

PC_DECL_ANCHOR = "let prev_plan = null;"
PC_DECL_NEW = """let prev_plan = null;
// #112 (G4, 2026-08-23): the OFFER the previous turn made, as persisted state alongside the plan.
let prev_offer = null;"""

PC_READ_ANCHOR = """  const pl = lastOlivia ? lastOlivia.plan : null;
  if (pl && typeof pl === 'object' && pl.op && NO_REPLAY.indexOf(String(lastOlivia.route || '')) === -1) {
    prev_plan = pl;
  }"""
PC_READ_NEW = """  const pl = lastOlivia ? lastOlivia.plan : null;
  // #112: read the pending offer INDEPENDENTLY of pl.op — an answer can offer items on a turn
  // whose plan carried no replayable op, and the binding must still resolve. Same NO_REPLAY guard.
  if (pl && typeof pl === 'object' && pl.pending_offer
      && NO_REPLAY.indexOf(String(lastOlivia.route || '')) === -1) { prev_offer = pl.pending_offer; }
  if (pl && typeof pl === 'object' && pl.op && NO_REPLAY.indexOf(String(lastOlivia.route || '')) === -1) {
    prev_plan = pl;
  }"""

PC_QUOTED_ANCHOR = "if (quoted_plan) { prev_plan = quoted_plan; }"
PC_QUOTED_NEW = ("if (quoted_plan) { prev_plan = quoted_plan; "
                 "if (quoted_plan.pending_offer) { prev_offer = quoted_plan.pending_offer; } }")

PC_RET_ANCHOR = "prev_plan: prev_plan, last_olivia_intro_offer: last_olivia_intro_offer } }];"
PC_RET_NEW = ("prev_plan: prev_plan, prev_offer: prev_offer, "
              "last_olivia_intro_offer: last_olivia_intro_offer } }];")


# ══════════════════════ 2 · Format Reply — record the offered items ══════════════════════

FR_RET_ANCHOR = ("return [{ json: { to: to, reply: text, interactive: interactive, "
                 "followup_interactive: followupInteractive, image_post_id: imagePostId, "
                 "send_file_key: sendFileKey, mark_welcome_phone: markPhone, "
                 "sources_used: sourcesUsed } }];")

FR_PENDING = r"""// #112 OFFER BINDING AS STATE (G4, 2026-08-23). #112's own AC #1 — "the offer records its item
// ids in code" — was never built; a FOURTH acceptance regex shipped into Answer Seed instead, and
// the next turn still re-searched (A4014: EIGHT videos offered, two delivered plus titles nobody
// offered). The items this reply actually put in front of the member are recorded HERE, on the
// turn. Save Conversation persists them on the olivia row's `plan` — the same channel prev_plan
// already rides — and Plan Request resolves the next turn's acceptance against THIS list.
// Recorded whenever the reply names items, not only when a phrase-matched offer is detected: the
// ACCEPTANCE side is what gates the bind, so an offer-shape test here would only re-import the
// fragility that broke this four times. Ticket and intro offers are deliberately excluded — they
// have their own two-step lanes (ticketYes / #107 member_intro picker) that must keep winning.
let pendingOffer = null;
try {
  const NLc = String.fromCharCode(10);
  const offerText = String(text || '') + (followupInteractive && followupInteractive.body
    ? NLc + String(followupInteractive.body.text || '') : '');
  const isTicket = offerText.toLowerCase().indexOf('open a ticket with the mds team') !== -1;
  const isIntro = /would you like me to connect you with one of them\?/i.test(offerText);
  if (!isTicket && !isIntro) {
    const uniq = function (a) { return a.filter(function (v, i) { return v && a.indexOf(v) === i; }); };
    const vids = uniq((offerText.match(/app\.mds\.co\/videos\/[a-f0-9]{24}/gi) || [])
      .map(function (u) { return String(u).split('/').pop().toLowerCase(); })).slice(0, 12);
    const posts = uniq((offerText.match(/facebook\.com\/groups\/\d+\/posts\/\d{6,25}/gi) || [])
      .map(function (u) { return String(u).split('/').pop(); })).slice(0, 12);
    // WhatsApp bold is how every item card in her replies names its item.
    const titles = uniq((offerText.match(/\*([^*\n]{6,120})\*/g) || [])
      .map(function (s) { return s.slice(1, -1).trim(); })).slice(0, 12);
    // The deliverable the offer sentence itself named ("Want a quick summary?" -> summary). The
    // member echoing HER OWN word is a state-derived acceptance signal, not a hand-written yes-list.
    let nouns = [];
    const lastLine = String(offerText).trim().split(NLc).pop() || '';
    if (/\?\s*$/.test(lastLine)) {
      const SKIP = { want: 1, would: 1, like: 1, shall: 1, should: 1, there: 1, these: 1, those: 1,
        about: 1, which: 1, quick: 1, their: 1, other: 1, them: 1, that: 1, this: 1, some: 1,
        from: 1, with: 1, your: 1, could: 1, might: 1 };
      nouns = uniq(lastLine.toLowerCase().replace(/[^a-z ]+/g, ' ').split(/\s+/)
        .filter(function (w) { return w.length >= 5 && !SKIP[w]; })).slice(0, 6);
    }
    const ids = vids.length ? vids : posts;
    if (ids.length || titles.length) {
      pendingOffer = { kind: vids.length ? 'video' : (posts.length ? 'thread' : 'list'),
        ids: ids, titles: titles, nouns: nouns, count: (ids.length || titles.length) };
    }
  }
} catch (e) { pendingOffer = null; }
"""

FR_RET_NEW = ("return [{ json: { to: to, reply: text, interactive: interactive, "
              "followup_interactive: followupInteractive, image_post_id: imagePostId, "
              "send_file_key: sendFileKey, mark_welcome_phone: markPhone, "
              "sources_used: sourcesUsed, pending_offer: pendingOffer } }];")


# ═════════════════════ 3 · Save Conversation — persist it on `plan` ═════════════════════

SC_ANCHOR = ("try { const su = src.sources_used; if (su && su.length) "
             "{ plan = Object.assign(plan || {}, { sources_used: su }); } } catch (e) {}")
SC_NEW = (SC_ANCHOR + " try { const po = src.pending_offer; if (po) "
          "{ plan = Object.assign(plan || {}, { pending_offer: po }); } } catch (e) {}")


# ═══════════════ 4 · Plan Request — resolve the acceptance against the list ═══════════════

PR_BIND_ANCHOR = ("const introOfferPending = (ctx.last_olivia_intro_offer === true) "
                  "|| _lastOlivia.toLowerCase().indexOf(INTRO_OFFER_MARK) !== -1;")

PR_BIND_NEW = PR_BIND_ANCHOR + r"""

// #112 OFFER BINDING — PERSISTED STATE, NOT A FIFTH REGEX (G4, 2026-08-23). #112's AC #1 said the
// offer must record its item ids IN CODE; a fourth acceptance regex shipped into Answer Seed and
// A4014 still failed (eight videos offered, four ids the model picked itself, two delivered).
// Format Reply now records the items each answer presented, Save Conversation persists them, and
// Prep Context hands them back as ctx.prev_offer. WHO decides the acceptance: the ROUTER
// (p.accepts_offer — it sees the message AND the history; the same signal ticketYes already
// trusts), with the existing bareAffirm as a deterministic floor and, third, the member echoing a
// word out of HER OWN offer sentence (state, not a yes-list). WHICH items is never decided by the
// wording: the stored list decides, a quantifier only selects inside it. No stored offer -> every
// branch below behaves exactly as before (#112 AC 3).
const _po = (ctx.prev_offer && typeof ctx.prev_offer === 'object') ? ctx.prev_offer : null;
const _poIds = (_po && Array.isArray(_po.ids)) ? _po.ids.filter(Boolean).map(String) : [];
const _poTitles = (_po && Array.isArray(_po.titles)) ? _po.titles.filter(Boolean).map(String) : [];
const _poList = _poIds.length ? _poIds : _poTitles;
const _poN = _poList.length;
const _poTrim = String(rawText || '').trim();
// bounded: a short, non-interrogative message that repeats a word from her own offer sentence.
const _poEcho = !!_po && Array.isArray(_po.nouns)
  && _poTrim.split(/\s+/).filter(Boolean).length <= 16 && !/\?$/.test(_poTrim)
  && _po.nouns.some(function (w) {
    // stem, so her "summary" recognises their "summaries" (and the other way round)
    const c = String(w).replace(/[^a-z]/gi, '').toLowerCase();
    if (c.length < 5) { return false; }
    const stem = c.replace(/(?:ies|ys|es|s|y)$/, '');
    if (stem.length < 4) { return false; }
    return new RegExp('\\b' + stem + '(?:y|ies|es|s)?\\b', 'i').test(_poTrim);
  });
const offerYes = !!_poN && !ticketYes && !introOfferPending && (_saidYes || bareAffirm || _poEcho);
// Default is EVERY item offered — "answering one of two reads as a miss" (#108). A quantifier or
// an ordinal narrows it; nothing else does.
const _poPick = (function () {
  const t = _poTrim.toLowerCase();
  const all = []; for (let i = 0; i < _poN; i++) { all.push(i); }
  if (!_poN) { return all; }
  if (/\b(?:1st|first)\b/.test(t)) { return [0]; }
  if (/\b(?:2nd|second)\b/.test(t)) { return _poN > 1 ? [1] : [0]; }
  if (/\b(?:3rd|third)\b/.test(t)) { return _poN > 2 ? [2] : all; }
  if (/\blast\b/.test(t)) { return [_poN - 1]; }
  const nm = t.match(/\b(two|three|four|five|[2-9])\b/);
  if (nm) {
    const k = ({ two: 2, three: 3, four: 4, five: 5 })[nm[1]] || parseInt(nm[1], 10);
    if (k > 0 && k < _poN) { return all.slice(0, k); }
  }
  return all;
})();
const offerBind = offerYes ? {
  kind: String(_po.kind || 'list'),
  ids: _poIds.length ? _poPick.map(function (i) { return _poIds[i]; }).filter(Boolean) : [],
  titles: _poIds.length ? _poTitles.slice(0, 12)
    : _poPick.map(function (i) { return _poTitles[i]; }).filter(Boolean),
  offered: _poN
} : null;"""

PR_BRANCH_ANCHOR = ("} else if (bareAffirm && ctx.has_history && ctx.prev_plan "
                    "&& ctx.prev_plan.op && !introOfferPending) {")
PR_BRANCH_NEW = """} else if (offerBind) {
  // #112: deliver EXACTLY the items the previous turn offered. The ids come from persisted state,
  // so the answer cannot wander onto an item nobody offered and cannot silently drop one. Checked
  // BEFORE the plan-replay branch: replaying the previous search plan is precisely the "re-search
  // the topic" behaviour this ticket exists to kill. The zeroth fetch pulls the first bound video
  // so the loop always holds one summary; Answer Seed's OFFER ACCEPTED block tells it to fetch the
  // rest by id. introOfferPending / ticketYes keep their precedence (#112 AC 4).
  route = 'llm'; planPeriod = 'offer_bound'; intent = 'question'; followup = true;
  raw_op = 'content_search';
  raw_params = { p_phone: mem.to, p_terms: [], p_sources: ['wa_message'], p_limit: 0, no_embed: true };
  if (offerBind.kind === 'video' && offerBind.ids.length) {
    op = 'video_search';
    params = { p_phone: mem.to, p_video_id: offerBind.ids[0], p_query: null, p_limit: 1 };
  } else {
    op = 'content_lookup';
    params = { p_phone: mem.to, p_source: 'wa_digest', p_kind: 'daily', p_limit: 0 };
  }
""" + PR_BRANCH_ANCHOR

PR_CONT_ANCHOR = """let cont_topic = null;
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
}"""

PR_CONT_NEW = """let cont_topic = null;
// The topic of the previous plan, wherever that lane keeps it. One reader, two arms below.
const _prevTopic = function () {
  const _pv = (ctx.prev_plan && ctx.prev_plan.params) || {};
  const _rv = (ctx.prev_plan && ctx.prev_plan.raw_params) || {};
  let carried = [];
  if (Array.isArray(_pv.p_terms) && _pv.p_terms.length) { carried = _pv.p_terms; }
  else if (_pv.p_query) { carried = [_pv.p_query]; }
  else if (_pv.p_member) { carried = [_pv.p_member]; }
  else if (_pv.p_category) { carried = [_pv.p_category]; }
  else if (Array.isArray(_rv.p_terms) && _rv.p_terms.length) { carried = _rv.p_terms; }
  return carried.map(function (t) { return String(t || '').toLowerCase().trim(); })
    .filter(function (t) { return t.length >= 2; }).slice(0, 3);
};
if (!bareAffirm && ctx.prev_plan) {
  const _c = rawText.replace(/[?!.]+$/, '').trim();
  if (_c.split(/\\s+/).length <= 8 && CONT_OPEN.test(_c)) {
    const residue = _c.toLowerCase().replace(/[^a-z0-9 ]+/g, ' ')
      .replace(CONT_SCOPE, ' ').split(/\\s+/)
      .filter(function (w) { return w.length >= 3; });
    if (!residue.length) {
      const carried = _prevTopic();
      if (carried.length) { cont_topic = carried; p.search_terms = carried; followup = true; }
    }
  }
}
// G7 (2026-08-23): an EXPLICIT ANAPHOR — "on this topic", "that thread", "the same subject" — is
// the member pointing at the previous turn by name, and CONT_OPEN never had an arm for it. A4061
// ("give me 3 members to get on a call with on this topic", exec 100397, adjacent turn, same
// thread) stalled with "I don't want to guess which thread you mean" while the previous turn's
// plan held the topic. Unlike the pure-qualifier arm this one needs no <=8-word cap and no empty
// residue: the anaphor IS the referent, whatever else the sentence asks for. LANE PRECEDENCE is
// untouched — only the SUBJECT is carried, the current wording still picks the lane.
const CONT_ANAPHOR = /\\b(?:this|that|the same)\\s+(?:topic|thread|subject|one|issue|discussion|conversation)\\b/i;
if (!cont_topic && !bareAffirm && ctx.prev_plan && CONT_ANAPHOR.test(rawText)) {
  const carriedA = _prevTopic();
  if (carriedA.length) { cont_topic = carriedA; p.search_terms = carriedA; followup = true; }
}"""

PR_RET1_ANCHOR = "route: route, intent: intent, focus_chat: null, period: planPeriod,"
PR_RET1_NEW = "route: route, intent: intent, focus_chat: null, offer_bind: offerBind, period: planPeriod,"
PR_RET2_ANCHOR = "route: route, intent: intent, focus_chat: chat, period: planPeriod,"
PR_RET2_NEW = "route: route, intent: intent, focus_chat: chat, offer_bind: offerBind, period: planPeriod,"


# ════════════════ 5 · Answer Seed — render the decision, delete the regexes ════════════════

AS_OFFER_ANCHOR = r"""// #80 OFFER BINDING. The failing sessions (ans #28131/#28133/#29905) re-searched the
// TOPIC on a bare acceptance and delivered chat chatter instead of the teased video -
// whose transcript summary sat unread in videos_catalog. Deterministic detection:
// previous Olivia turn ends in an offer AND links a library video AND the member is
// accepting -> inject the binding as evidence the loop cannot miss.
// #108 (2026-08-22): the end-anchor made 'yes booth' (Andy's typo for 'yes both') miss, and
// the loop re-searched into an unrelated member's story. A QUANTIFIER or a typo of one may
// follow the affirmative; a real topic word may not, so 'yes tariffs' still routes normally.
const ACCEPT_TAIL = '(\\s+(both|booth|bofh|all|either|one|that one|the first|the second|of them|please|thanks|thank you|pls|ty))*';
const ACCEPT_RE = new RegExp('^(yes|yes please|yep|yeah|sure|ok|okay|sounds good|go ahead|please do|do it|summar(y|ize|ise)( key points| it)?|key points( please)?|can you summar(y|ize|ise)[^?]{0,40}[?]?)' + ACCEPT_TAIL + '[!. ]*$', 'i');
const OFFER_TAIL_RE = /(want (a|the) quick summary|want me to|want the (link|details|rest)|would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\?\s*$/i;
let offer_ctx = '';
try {
  let lastO = null;
  for (let i = rows.length - 1; i >= 0 && !lastO; i--) { if (rows[i].role !== 'member') lastO = rows[i]; }
  const lt = lastO ? String(lastO.text || '') : '';
  const links = lt.match(/app\.mds\.co\/videos\/([a-f0-9]{24})/gi) || [];
  if (OFFER_TAIL_RE.test(lt.trim()) && links.length && ACCEPT_RE.test(current)) {
    // #108: bind ALL videos the offer linked, not just the last one - "either one" and
    // "yes both" are answered from two, and answering one of two reads as a miss.
    const vids = links.map(function (u) { return String(u).split('/').pop(); })
      .filter(function (v, i, a) { return a.indexOf(v) === i; }).slice(0, 3);
    const wantsAll = /\b(both|booth|bofh|all|either)\b/i.test(current) || vids.length === 1;
    const list = wantsAll ? vids : [vids[vids.length - 1]];
    offer_ctx = 'OFFER ACCEPTED: your previous message offered ' + (vids.length > 1
        ? 'these library videos: ' + vids.join(', ') : 'the library video ' + vids[0])
      + ' and the member just accepted' + (wantsAll && vids.length > 1 ? ' ALL of them' : '')
      + '. Call video_search with p_video_id for EACH of: ' + list.join(', ')
      + ' and answer from their summary fields. Do NOT re-search the topic and do NOT answer '
      + 'about anyone else - the member asked for these, nothing more. Community threads may '
      + 'only supplement, clearly separated.';
  }
} catch (e) {}"""

AS_OFFER_NEW = r"""// #112 OFFER BINDING — THE BIND IS STATE NOW (G4, 2026-08-23). Plan Request decides it from the
// items Format Reply recorded on the previous turn (Save Conversation -> plan.pending_offer ->
// ctx.prev_offer -> plan.offer_bind). The four acceptance regexes that used to live here are
// DELETED: they were the hand-written yes-list Plan Request's own comment forbids, they capped the
// bind at three videos, they required a video LINK (a thread offer could never bind at all), and
// the fourth one still missed "Yes give me some summaries because that's a lot to watch" (A4014,
// exec 100321 — eight offered, four ids the model chose itself, two delivered). This block only
// RENDERS the decision; an empty offer_bind leaves the turn exactly as it was.
let offer_ctx = '';
try {
  const ob = plan.offer_bind;
  const obIds = (ob && Array.isArray(ob.ids)) ? ob.ids.filter(Boolean) : [];
  const obTitles = (ob && Array.isArray(ob.titles)) ? ob.titles.filter(Boolean) : [];
  if (ob && (obIds.length || obTitles.length)) {
    const n = obIds.length || obTitles.length;
    offer_ctx = 'OFFER ACCEPTED (deterministic — these are the items your PREVIOUS message put in '
      + 'front of the member, recorded on that turn): the member is accepting exactly these ' + n
      + ' item(s) and nothing else: ' + (obIds.length ? obIds.join(', ') : obTitles.join(' | ')) + '.'
      + (ob.kind === 'video' ? ' Call video_search with p_video_id for EVERY id listed above — one call each — and answer from their summary fields.' : '')
      + (ob.kind === 'thread' ? ' Call fb_thread with p_post_id for EVERY id listed above and answer from those threads.' : '')
      + ' Deliver ALL of them: a partial set reads as a miss. Do NOT run a fresh topic search, do'
      + ' NOT introduce any item that is not on this list, and if one of them has nothing on file'
      + ' say so for that item BY NAME. Community threads may only supplement, clearly separated.'
      + (obIds.length && obTitles.length ? ' Titles offered, in order: ' + obTitles.join(' | ') + '.' : '');
  }
} catch (e) {}"""

AS_ASKER_ANCHOR = ("  + 'record in the second person, never greet the asker by their name.' + NL + NL;")
AS_ASKER_NEW = (
    "  + 'record in the second person, never greet the asker by their name. B5017 (2026-08-23): "
    "when you decline a typed identity claim, DO NOT STOP AT THE DECLINE and do not merely OFFER "
    "to look the real asker up — in the SAME reply go on and answer the question for '\n"
    "  + (mem.full_name || 'the asker') + ' from their own record.' + NL + NL;")


# ═══════════════════════════════ 6 · Gate Verdict ═══════════════════════════════

GV_1B_TAIL_ANCHOR = """    linkCoverage = add.length;
  }
} catch (e) {}
"""

GV_1C = r"""    linkCoverage = add.length;
  }
} catch (e) {}

// #1c ELEMENT-COVERAGE REPAIR — URL FIELDS (G5, 2026-08-23). #1b pairs a URL with a `title` sitting
// next to it in the evidence. The schedule route answers an EVENT-level question with a block keyed
// `event` that carries BOTH `event_url` and `registration_url` (shipped and verified live today) —
// and the reply still gave only a maps link (A4071, "When is the MDS Singapore Summit?"). A URL
// field belonging to the subject the answer is about IS part of the answer. Same contract as #1b:
// the URL is copied verbatim out of the evidence, so the link gate's invariant survives by
// construction; repair, never block; cap 2; registration link first; inserted before a trailing
// offer question. Bound: the owner name next to the field must be named in the answer.
let fieldCoverage = 0;
try {
  const OWNER = /\\?"(?:event|event_name|title|name|full_name)\\?"\s*:\s*\\?"([^"\\]{4,120})/g;
  const FIELD = /\\?"(registration_url|event_url|url|app_url|public_page_url)\\?"\s*:\s*\\?"(https?:\/\/[^"\\ ]{8,400})/g;
  const owners = [];
  let om = null, og = 0;
  while ((om = OWNER.exec(evRaw)) !== null && og++ < 800) { owners.push({ at: om.index, name: om[1] }); }
  const ownerBefore = function (idx) {
    let best = null;
    for (let i = 0; i < owners.length; i++) {
      if (owners[i].at > idx) { break; }
      if (idx - owners[i].at < 1500) { best = owners[i].name; }
    }
    return best;
  };
  const ownerNamed = function (nm) {
    const h = answerText.toLowerCase();
    const ws = String(nm).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ')
      .filter(function (w) { return w.length >= 4; });
    if (!ws.length) { return false; }
    return ws.filter(function (w) { return h.indexOf(w) !== -1; }).length >= Math.ceil(0.7 * ws.length);
  };
  const cands = [];
  let fm2 = null, fg = 0;
  while ((fm2 = FIELD.exec(evRaw)) !== null && fg++ < 600) {
    const u = stripT(fm2[2]);
    if (answerText.indexOf(u) !== -1) { continue; }
    if (cands.some(function (x) { return x.url === u; })) { continue; }
    const own = ownerBefore(fm2.index);
    if (!own || !ownerNamed(own)) { continue; }
    cands.push({ url: u, reg: fm2[1] === 'registration_url' });
  }
  const addF = cands.filter(function (x) { return x.reg; })
    .concat(cands.filter(function (x) { return !x.reg; })).slice(0, 2);
  if (addF.length) {
    const ls = answerText.replace(/\s+$/, '').split(NL);
    let at2 = ls.length;
    for (let i = ls.length - 1; i >= 0 && i >= ls.length - 3; i--) {
      if (/(want|would you like|shall i|should i)\b[^?]{0,90}\?\s*$/i.test(ls[i])) { at2 = i; }
    }
    ls.splice(at2, 0, addF.map(function (x) { return (x.reg ? 'Register: ' : '') + x.url; }).join(NL));
    answerText = ls.join(NL);
    fieldCoverage = addF.length;
  }
} catch (e) {}
"""

GV_EVFIRST_ANCHOR = """const _evFirst = [];
const RE_PERSON = /\\\\?"(?:full_name|member_name|display_name)\\\\?"\\s*:\\s*\\\\?"([A-Z][^"\\\\]{2,59})/g;
let _mp = null, _guard = 0;
while ((_mp = RE_PERSON.exec(evRaw)) !== null && _guard++ < 400) {
  const f = _firstOf(_mp[1]);
  if (!_selfName(f) && _evFirst.indexOf(f) === -1) { _evFirst.push(f); }
}"""

GV_EVFIRST_NEW = """const _evFirst = [];
// B5015 (2026-08-23): the FULL names too — the gated-refusal check below needs to count how many
// real member names a reply carries, and a first name alone is too loose to count on.
const _evFull = [];
const RE_PERSON = /\\\\?"(?:full_name|member_name|display_name)\\\\?"\\s*:\\s*\\\\?"([A-Z][^"\\\\]{2,59})/g;
let _mp = null, _guard = 0;
while ((_mp = RE_PERSON.exec(evRaw)) !== null && _guard++ < 400) {
  const f = _firstOf(_mp[1]);
  const _fn = String(_mp[1]).trim();
  if (!_selfName(f) && _evFirst.indexOf(f) === -1) { _evFirst.push(f); }
  if (!_selfName(f) && _evFull.indexOf(_fn) === -1) { _evFull.push(_fn); }
}"""

GV_CLAIMS_ANCHOR = "const claims = identityClaims.concat(linkClaims, hClaims);"

GV_POLICY = r"""// ───────── DETERMINISTIC POLICY CHECKS (2026-08-23) ─────────
// Three behaviours prompt rules kept losing, each read off THIS turn's own tool payloads. They
// ride the normal regeneration path with an explicit instruction (the attempts cap still applies).
const policyClaims = [];

// (1) A GATED REFUSAL MUST NOT THEN LIST NAMES (B5015, live). "You're not registered for the
// Singapore Summit, so I can't pull a personalized attendee match — but here are members in
// Singapore worth knowing: Adi Ong, Brian Quach, John Cho, Kevan Soh, Ivan Ong, Leslie Chong,
// Samuel Loo, Ryan Ong." SIX of those eight are on the Summit roster: the event gate was satisfied
// and then defeated by re-labelling the same people as a city list. If ANY tool result this turn
// carries an event/chat/aggregate denial, the reply may carry the count and an offer — no names.
try {
  const denied = /\\?"disclosure\\?"\s*:\s*\\?"(?:event|chat|aggregate)\\?"/.test(evRaw)
    || /this person is not registered for/i.test(evRaw)
    || /no attendee list is shown/i.test(evRaw)
    || /never name an attendee here/i.test(evRaw);
  if (denied) {
    const named = _evFull.filter(function (fn) {
      return fn.indexOf(' ') !== -1 && answerText.indexOf(fn) !== -1;
    });
    if (named.length >= 3) {
      policyClaims.push('GATE: the gate refused names for this turn and your draft names '
        + named.length + ' members (' + named.slice(0, 8).join(', ') + '). Give the COUNT and the '
        + 'offer, and name NOBODY — do not re-label the same people as a city, niche, chapter or '
        + '"worth knowing" list. State the reason plainly and offer to flag it with the MDS team.');
    }
  }
} catch (e) {}

// (2) NO INTERNAL VOCABULARY (A4077, live: "Both of those tools pulled the Singapore Summit by
// mistake… No fit_reason came back on this one"). Backend words never belong in a member reply.
// Whole-word, case-insensitive, and the member's own QUOTED text is masked out first so quoting
// somebody who said "great tool" is untouched. tool/tools/rows are the only ambiguous ones — a
// member-facing "tool" is a real product word — so they count only inside a sentence that ALSO
// narrates retrieval AND refers to them as hers, which is exactly the failure shape.
try {
  const masked = answerText.replace(/["'\u201c\u201d\u2018\u2019][^"'\u201c\u201d\u2018\u2019]{4,}["'\u201c\u201d\u2018\u2019]/g, ' ');
  const hard = masked.match(/\b(?:fit_reason|strength_note|payload|tool_args|rpc|endpoint|p_[a-z][a-z_]{2,})\b|\bop\s*=/gi) || [];
  const RETRIEVAL = /\b(?:pulled|returned|came back|call(?:ed|ing)?|ran|quer(?:y|ied)|fetch(?:ed)?|preload(?:ed)?|evidence|results?)\b/i;
  const MINE = /\b(?:i|my|those|these|both)\b/i;
  const soft = masked.split(/[.!?\n]+/).filter(function (s) {
    return /\b(?:tools?|rows)\b/i.test(s) && RETRIEVAL.test(s) && MINE.test(s);
  });
  const found = hard.concat(soft.length ? ['tool/rows retrieval narration'] : []);
  if (found.length) {
    policyClaims.push('INTERNALS: your draft names backend machinery (' + found.slice(0, 5).join(', ')
      + '). Say it in member words; never name internals — no tools, rows, payloads, endpoints, '
      + 'RPCs, parameter names, fit_reason or strength_note, and never narrate what you searched, '
      + 'what a tool returned or that something was pulled "by mistake". Just answer.');
  }
} catch (e) {}

// (3) THE MEMBER NAMED TWO SOURCES AND THE REPLY USED ONE (B5039: "Search chats AND Facebook for
// resellers attending the summit" — exec 100735 returned both, the answer cited only the WhatsApp
// chat and the Facebook half of the ask was never addressed or declined). Deterministic: the
// sources the member NAMED, intersected with what the evidence actually holds, minus what the
// reply actually shows. Only fires when the payload really carries the missing source.
try {
  const mq = _memberMsg.toLowerCase();
  const SRC = [
    { ask: /\b(?:facebook|fb|the group)\b/, say: 'Facebook (the MDS group)',
      ev: /\\?"source\\?"\s*:\s*\\?"fb_(?:post|comment)|facebook\.com\/groups\//i,
      shown: /facebook|fb\.com/i },
    { ask: /\b(?:chats?|whatsapp)\b/, say: 'the WhatsApp chats',
      ev: /\\?"source\\?"\s*:\s*\\?"wa_(?:message|digest)/i,
      shown: /\b(?:chat|chats|whatsapp)\b/i },
    { ask: /\b(?:calls?|videos?|library|recordings?)\b/, say: 'the call / video library',
      ev: /\\?"source\\?"\s*:\s*\\?"call_transcript|app\.mds\.co\/videos\//i,
      shown: /app\.mds\.co\/videos\/|\b(?:call|calls|video|videos|library)\b/i }
  ];
  const asked = SRC.filter(function (s) { return s.ask.test(mq); });
  if (asked.length >= 2) {
    const missing = asked.filter(function (s) { return s.ev.test(evRaw) && !s.shown.test(answerText); });
    if (missing.length && missing.length < asked.length) {
      const miss = missing.map(function (s) { return s.say; }).join(' and ');
      policyClaims.push('MISSING SOURCE: the member asked you to search '
        + asked.map(function (s) { return s.say; }).join(' AND ')
        + ', and your draft uses only some of them. Your tool results DO contain ' + miss
        + ' rows for this turn — quote and link at least one from ' + miss
        + ', in its own clearly labelled part of the reply, or say plainly you found nothing there.');
    }
  }
} catch (e) {}

// (4) A DECLINED IDENTITY CLAIM MUST STILL ANSWER FOR THE REAL ASKER (B5017). The decline itself is
// now correct and stays; what failed is the SHAPE — she declined the typed name and then only
// OFFERED to look up the account she is actually talking to ("if you'd like to know what's on file
// for the account you're actually messaging from, I'm happy to pull that up"). Naming whose account
// it is, is the cheapest deterministic proof that the reply answered rather than deferred.
try {
  if (_idOther && /\b(?:about me|know about me|who am i|my (?:own )?(?:record|profile|account|details))\b/i.test(_memberMsg)) {
    const hasAsker = !!_askerFirst && (answerText.toLowerCase().indexOf(_askerFirst) !== -1
      || (_askerName && answerText.indexOf(_askerName) !== -1));
    if (!hasAsker) {
      policyClaims.push('IDENTITY-ANSWER: declining the typed name "' + _idOther + '" is right — keep '
        + 'it. But then ANSWER the question for the real asker in the SAME reply: you are speaking to '
        + (_askerName || 'this member') + ', so say whose account this is and give what is on file for '
        + 'them (call member_dossier). Declining and only OFFERING to look them up is not an answer.');
    }
  }
} catch (e) {}

const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"""

# ═════ 7 · B5025 · the call-type filter exists and the model never passes it ═════
# digest.video_search_v2's p_call_type filters correctly (proved both ways through PostgREST:
# unfiltered 'tiktok' -> Channel Call + Mastermind; p_call_type='mogul' -> Mogul Call only). The
# live execution never sent it, so a Chapter Event and a Channel Kick-Off were folded into a list
# titled "Mogul Calls". Two edits: the schema stops lying about the allowed values (read live from
# videos_catalog.call_type, 1,034 rows: Mogul Call 201 · Summit 146 · Mastermind 135 · Chapter
# Event 94 · Channel Call 81 · Expert Call 52 · Coaching Call 5 · Hot Seat 4 · Workshop Call 3 ·
# Town Hall 2 · 311 null), and Plan Request sets the filter IN CODE on the videos lane so the
# deterministic preload is already type-correct whatever the model does.

AS_CALLTYPE_ANCHOR = ("p_call_type: str('mogul | expert | channel | chapter "
                      "- filters to that kind of call')")
AS_CALLTYPE_NEW = (
    "p_call_type: str('THE call-type filter - PASS IT whenever the question names a kind of call, "
    "or the list you give back will silently mix kinds (B5025: a Chapter Event and a Channel "
    "Kick-Off came back inside a list titled Mogul Calls). Matched case-insensitively against "
    "videos_catalog.call_type; the values that exist are EXACTLY: Mogul Call, Expert Call, "
    "Channel Call, Chapter Event, Mastermind, Summit, Coaching Call, Hot Seat, Workshop Call, "
    "Town Hall. Some library videos carry no call type at all, so a type-filtered list is "
    "narrower than the library - say so rather than implying it is everything.')")

AS_CALLTYPE2_ANCHOR = ("Call video_search with p_call_type (mogul | expert | channel | chapter) "
                       "and p_order=recent")
AS_CALLTYPE2_NEW = ("Call video_search with p_call_type (one of the real values: Mogul Call, "
                    "Expert Call, Channel Call, Chapter Event, Mastermind, Summit, Coaching Call, "
                    "Hot Seat, Workshop Call, Town Hall) and p_order=recent")

PR_VIDEOS_ANCHOR = """  const vTerms = terms.filter(function (t) { return !VWORDS[t]; });
  params = { p_phone: mem.to, p_query: vTerms.length ? vTerms.join(' ') : null, p_limit: 8 };"""
PR_VIDEOS_NEW = """  const vTerms = terms.filter(function (t) { return !VWORDS[t]; });
  params = { p_phone: mem.to, p_query: vTerms.length ? vTerms.join(' ') : null, p_limit: 8 };
  // B5025 (2026-08-23): p_call_type WORKS (probed live, both ways) and the model simply never sent
  // it, so "Mogul Calls only" could not be honoured and a Chapter Event and a Channel Kick-Off got
  // into the list. The tool schema is fixed too, but a rule that must fire every time belongs in
  // code: when the question names a call TYPE, the deterministic preload is filtered here.
  const _callType = (function () {
    const t = String(rawText || '');
    const M = [['Mogul Call', /\\bmogul\\b/i], ['Expert Call', /\\bexpert\\s+calls?\\b/i],
      ['Channel Call', /\\bchannel\\s+(?:calls?|kick)/i], ['Chapter Event', /\\bchapter\\s+(?:events?|calls?|sessions?)\\b/i],
      ['Mastermind', /\\bmasterminds?\\b/i], ['Hot Seat', /\\bhot\\s?seats?\\b/i],
      ['Workshop Call', /\\bworkshops?\\b/i], ['Coaching Call', /\\bcoaching\\s+calls?\\b/i],
      ['Town Hall', /\\btown\\s+halls?\\b/i]];
    for (let i = 0; i < M.length; i++) { if (M[i][1].test(t)) { return M[i][0]; } }
    return null;
  })();
  if (_callType) { params.p_call_type = _callType; }"""


# ══════ 8 · A4095 · the verbatim digest lane ignores the asked window ══════
# digest.summaries already holds a daily row per day of the window; the lane asked for p_limit 1
# and Build Verbatim Digest read rows[0], so "the last 3 days in <chat>" came back as one day
# labelled with one date.

PR_VERBATIM_ANCHOR = """  route = 'verbatim';
  params = { p_phone: mem.to, p_source: 'wa_digest', p_kind: period, p_chat: chat, p_limit: 1 };
  if (dateHint === 'yesterday') { params.p_until = day(1); }
  if (dateHint === 'today') { params.p_on = day(0); }"""
PR_VERBATIM_NEW = """  route = 'verbatim';
  params = { p_phone: mem.to, p_source: 'wa_digest', p_kind: period, p_chat: chat, p_limit: 1 };
  if (dateHint === 'yesterday') { params.p_until = day(1); }
  if (dateHint === 'today') { params.p_on = day(0); }
  // A4095 (2026-08-23): a NAMED multi-day window ("the last 3 days in MDS Logistics") pulled ONE
  // daily row and labelled the reply with a single date, while digest.summaries held every day of
  // it. Only an EXPLICIT day count widens the pull - askWindowDays defaults to 7, and a plain
  // "digest for <chat>" must keep returning the one digest it always returned.
  const _vw = String(rawText || '').match(/\\b(?:last|past|previous)\\s+(\\d{1,2})\\s*(?:day|days|d)\\b/i);
  const _vDays = _vw ? Math.max(2, Math.min(14, parseInt(_vw[1], 10))) : 0;
  if (period === 'daily' && _vDays > 1) {
    params.p_limit = _vDays;
    params.p_since = day(_vDays);
    delete params.p_on;
  }"""

BVD_ANCHOR = """const r = rows[0];
const rDate = String(r.occurred_at).slice(0, 10);
let out = '*' + r.meta.chat_name + '* - ' + r.kind + ' digest (' + rDate + ')' + NL + NL;
// If they asked for a specific day we don't have yet, say which one they're getting
// (yesterday's digest is only produced by the next morning's run).
const wantDate = plan.date_hint === 'today' ? new Date().toISOString().slice(0, 10)
  : plan.date_hint === 'yesterday' ? new Date(Date.now() - 864e5).toISOString().slice(0, 10) : null;
if (wantDate && rDate !== wantDate) {
  out = '_No digest for that day yet - latest I have is ' + rDate + ':_' + NL + NL + out;
}
if (r.tl_dr) { out += '*TL;DR:* ' + r.tl_dr + NL + NL; }
if (r.body) { out += r.body + NL; }
if (r.meta.topics) { out += NL + '*Topics:* ' + r.meta.topics; }
if (r.meta.links_shared) { out += NL + '*Links:* ' + r.meta.links_shared; }
if (r.meta.msg_count) { out += NL + NL + '_' + r.meta.msg_count + ' messages' + (r.meta.participant_count ? ', ' + r.meta.participant_count + ' participants' : '') + '_'; }"""

BVD_NEW = """// A4095 (2026-08-23): this lane read rows[0] and stamped the reply with ONE date even when the
// member had asked for a window ("the last 3 days"). Plan Request now asks digest.summaries for
// the whole window; concatenate every row that came back and label the answer with the window it
// ACTUALLY covers - including saying so when fewer days exist than were asked for.
const askedDays = Math.max(1, Math.min(14, Number((plan.params || {}).p_limit) || 1));
const rowsUse = rows.slice(0, askedDays);
const multi = rowsUse.length > 1;
const r = rowsUse[0];
const rDate = String(r.occurred_at).slice(0, 10);
const dates = rowsUse.map(function (x) { return String(x.occurred_at).slice(0, 10); });
let out = '*' + r.meta.chat_name + '* - ' + r.kind + ' digest ('
  + (multi ? dates[dates.length - 1] + ' to ' + dates[0] : rDate) + ')' + NL + NL;
if (multi && askedDays > rowsUse.length) {
  out += '_You asked for ' + askedDays + ' days; ' + rowsUse.length + ' of them have a digest on file._' + NL + NL;
}
// If they asked for a specific day we don't have yet, say which one they're getting
// (yesterday's digest is only produced by the next morning's run).
const wantDate = plan.date_hint === 'today' ? new Date().toISOString().slice(0, 10)
  : plan.date_hint === 'yesterday' ? new Date(Date.now() - 864e5).toISOString().slice(0, 10) : null;
if (!multi && wantDate && rDate !== wantDate) {
  out = '_No digest for that day yet - latest I have is ' + rDate + ':_' + NL + NL + out;
}
out += rowsUse.map(function (x) {
  const m = x.meta || {};
  let b = multi ? ('*' + String(x.occurred_at).slice(0, 10) + '*' + NL) : '';
  if (x.tl_dr) { b += '*TL;DR:* ' + x.tl_dr + NL + NL; }
  if (x.body) { b += x.body + NL; }
  if (m.topics) { b += NL + '*Topics:* ' + m.topics; }
  if (m.links_shared) { b += NL + '*Links:* ' + m.links_shared; }
  if (m.msg_count) { b += NL + NL + '_' + m.msg_count + ' messages' + (m.participant_count ? ', ' + m.participant_count + ' participants' : '') + '_'; }
  return b;
}).join(NL + NL);"""


PR_PSINCE_ANCHOR = """  if (period === 'daily' && _vDays > 1) {
    params.p_limit = _vDays;
    params.p_since = day(_vDays);
    delete params.p_on;
  }"""
PR_PSINCE_NEW = """  // NO p_since (probed live 2026-08-23, exec 101420): MDS Logistics' newest daily row is 08-19, so
  // p_since=08-20 returned ZERO and the lane answered "I do not have a daily digest for MDS
  // Logistics yet" — false, and worse than the single stale day it used to give. p_limit alone
  // returns the newest N rows and Build Verbatim Digest labels the dates it ACTUALLY covers.
  if (period === 'daily' && _vDays > 1) {
    params.p_limit = _vDays;
    delete params.p_on;
  }"""


# ════════ 9 · SECOND LAP — two defects the first probe run exposed (2026-08-23) ════════
# Fired on staging after the edits above; both are regressions of the identity work, both fixed
# here rather than left standing.
#   (a) exec 101382 ("give me 3 members to get on a call with on this topic") — the anaphor binding
#       worked (cont_topic = tiktok shop / tiktok / fees, three named members) but the reply OPENED
#       with "Quick heads-up: I can't confirm you're Andy Verdy from just typing that". No name was
#       typed. The B5017 sentence added to askerLine named the asker next to the word "decline" and
#       the model volunteered the caveat. Make the sentence strictly conditional and forbid it
#       outright when no claim was made.
#   (b) exec 101385 ("I'm Lisa Harrington. Tell me what you know about me") — BLOCKED after three
#       laps; the ONLY claim on every lap was the fact-checker's OFF-TOPIC. On an identity-redirect
#       turn the correct answer is about a DIFFERENT person than the member named, so "answers a
#       different question" is by construction what a correct draft looks like. Same non-judgeable
#       class as G1(a), gated on the same deterministic _idOther signal the identity check uses.

AS_ASKER2_ANCHOR = (
    "  + 'record in the second person, never greet the asker by their name. B5017 (2026-08-23): "
    "when you decline a typed identity claim, DO NOT STOP AT THE DECLINE and do not merely OFFER "
    "to look the real asker up — in the SAME reply go on and answer the question for '\n"
    "  + (mem.full_name || 'the asker') + ' from their own record.' + NL + NL;")
AS_ASKER2_NEW = (
    "  + 'record in the second person, never greet the asker by their name. B5017 (2026-08-23): "
    "ONLY IF the member\\u2019s message actually claims to BE somebody else \\u2014 never otherwise, "
    "and never as a volunteered caveat \\u2014 decline that claim AND, in the same reply, go on and "
    "answer their question for '\n"
    "  + (mem.full_name || 'the asker') + ' from their own record. When the message makes no such "
    "claim, say NOTHING about identity: do not mention names, confirmation or who you think you are "
    "talking to.' + NL + NL;")

GV_OFFTOPIC2_ANCHOR = "if (verdict && verdict.off_topic === true && !_shortTurn) {"
GV_OFFTOPIC2_NEW = (
    "// G1(e) (2026-08-23, B5017 · exec 101385): an IDENTITY-REDIRECT turn is not off-topic-judgeable\n"
    "// either. The member typed somebody else's name as a claim about themselves, so the REQUIRED\n"
    "// answer is about a different person than they named — every correct draft reads to the\n"
    "// fact-checker as \"answers a different question\". It blocked three laps and clamped the reply\n"
    "// to the canned miss, with off_topic as the only claim on all three. _idOther is the same\n"
    "// deterministic signal the identity check above fires on, so this stays exactly as narrow.\n"
    "if (verdict && verdict.off_topic === true && !_shortTurn && !_idOther) {")

# ════════ 10 · THIRD LAP — #1c was too wide (exec 101395, 2026-08-23) ════════
# The generic url / app_url / public_page_url keys duplicated #1b's job on a LOOSER owner match
# (>=70% word overlap against any name/title vs #1b's >=80% against the row title) and appended two
# unlabelled bare links to the tail of a chat-content answer. #1b already covers an item's own url
# with the tighter test; #1c exists for the EVENT-level fields #1b cannot see. Narrow it to those.
GV_FIELDKEYS_ANCHOR = ("  const FIELD = /\\\\?\"(registration_url|event_url|url|app_url|public_page_url)"
                       "\\\\?\"\\s*:\\s*\\\\?\"(https?:\\/\\/[^\"\\\\ ]{8,400})/g;")
GV_FIELDKEYS_NEW = ("  // narrowed 2026-08-23 (exec 101395): registration_url / event_url ONLY. The generic url\n"
                    "  // keys duplicated #1b on a looser owner match and appended bare unlabelled links.\n"
                    "  const FIELD = /\\\\?\"(registration_url|event_url)"
                    "\\\\?\"\\s*:\\s*\\\\?\"(https?:\\/\\/[^\"\\\\ ]{8,400})/g;")

GV_EXTRA_ANCHOR = "  if (linkCoverage) { extra.link_coverage = linkCoverage; }"
GV_EXTRA_NEW = ("  if (linkCoverage) { extra.link_coverage = linkCoverage; }\n"
                "  if (fieldCoverage) { extra.field_coverage = fieldCoverage; }")


# ═══════════════════════════════════ apply ═══════════════════════════════════

def transform(nodes):
    """Pure string work on the node code. Every anchor asserted exactly once."""
    touched = []

    # ── Prep Context ──────────────────────────────────────────────────────────
    pc = nodes["Prep Context"]["parameters"]["jsCode"]
    if "prev_offer" in pc:
        print("Prep Context: already applied")
    else:
        one(pc, PC_DECL_ANCHOR, "Prep Context prev_plan decl")
        pc = pc.replace(PC_DECL_ANCHOR, PC_DECL_NEW)
        one(pc, PC_READ_ANCHOR, "Prep Context plan read")
        pc = pc.replace(PC_READ_ANCHOR, PC_READ_NEW)
        one(pc, PC_QUOTED_ANCHOR, "Prep Context quoted_plan")
        pc = pc.replace(PC_QUOTED_ANCHOR, PC_QUOTED_NEW)
        one(pc, PC_RET_ANCHOR, "Prep Context return")
        pc = pc.replace(PC_RET_ANCHOR, PC_RET_NEW)
        node_check(pc, "Prep Context")
        nodes["Prep Context"]["parameters"]["jsCode"] = pc
        touched.append("Prep Context")

    # ── Format Reply ──────────────────────────────────────────────────────────
    fr = nodes["Format Reply"]["parameters"]["jsCode"]
    if "pendingOffer" in fr:
        print("Format Reply: already applied")
    else:
        one(fr, FR_RET_ANCHOR, "Format Reply return")
        fr = fr.replace(FR_RET_ANCHOR, FR_PENDING + FR_RET_NEW)
        node_check(fr, "Format Reply")
        nodes["Format Reply"]["parameters"]["jsCode"] = fr
        touched.append("Format Reply")

    # ── Save Conversation (an n8n expression, not a Code node) ────────────────
    sc = nodes["Save Conversation"]["parameters"]["jsonBody"]
    if "pending_offer" in sc:
        print("Save Conversation: already applied")
    else:
        one(sc, SC_ANCHOR, "Save Conversation sources_used")
        sc = sc.replace(SC_ANCHOR, SC_NEW)
        expr_check(sc, "Save Conversation")
        nodes["Save Conversation"]["parameters"]["jsonBody"] = sc
        touched.append("Save Conversation")

    # ── Plan Request ──────────────────────────────────────────────────────────
    pr = nodes["Plan Request"]["parameters"]["jsCode"]
    if "offerBind" in pr:
        print("Plan Request: already applied")
    else:
        one(pr, PR_BIND_ANCHOR, "Plan Request introOfferPending")
        pr = pr.replace(PR_BIND_ANCHOR, PR_BIND_NEW)
        one(pr, PR_BRANCH_ANCHOR, "Plan Request bareAffirm replay branch")
        pr = pr.replace(PR_BRANCH_ANCHOR, PR_BRANCH_NEW)
        one(pr, PR_CONT_ANCHOR, "Plan Request cont_topic block")
        pr = pr.replace(PR_CONT_ANCHOR, PR_CONT_NEW)
        one(pr, PR_RET1_ANCHOR, "Plan Request return #1")
        pr = pr.replace(PR_RET1_ANCHOR, PR_RET1_NEW)
        one(pr, PR_RET2_ANCHOR, "Plan Request return #2")
        pr = pr.replace(PR_RET2_ANCHOR, PR_RET2_NEW)
        one(pr, PR_VIDEOS_ANCHOR, "Plan Request videos lane params")
        pr = pr.replace(PR_VIDEOS_ANCHOR, PR_VIDEOS_NEW)
        one(pr, PR_VERBATIM_ANCHOR, "Plan Request verbatim lane params")
        pr = pr.replace(PR_VERBATIM_ANCHOR, PR_VERBATIM_NEW)
        node_check(pr, "Plan Request")
        nodes["Plan Request"]["parameters"]["jsCode"] = pr
        touched.append("Plan Request")

    # ── Answer Seed ───────────────────────────────────────────────────────────
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    if "plan.offer_bind" in seed:
        print("Answer Seed: already applied")
    else:
        one(seed, AS_OFFER_ANCHOR, "Answer Seed #80/#108 offer block")
        seed = seed.replace(AS_OFFER_ANCHOR, AS_OFFER_NEW)
        assert "ACCEPT_RE" not in seed, "ACCEPT_RE survived the replacement"
        assert "OFFER_TAIL_RE" not in seed, "OFFER_TAIL_RE survived the replacement"
        one(seed, AS_ASKER_ANCHOR, "Answer Seed askerLine tail")
        seed = seed.replace(AS_ASKER_ANCHOR, AS_ASKER_NEW)
        one(seed, AS_CALLTYPE_ANCHOR, "Answer Seed video_search p_call_type")
        seed = seed.replace(AS_CALLTYPE_ANCHOR, AS_CALLTYPE_NEW)
        one(seed, AS_CALLTYPE2_ANCHOR, "Answer Seed LATEST-IS-A-DATE p_call_type")
        seed = seed.replace(AS_CALLTYPE2_ANCHOR, AS_CALLTYPE2_NEW)
        node_check(seed, "Answer Seed")
        nodes["Answer Seed"]["parameters"]["jsCode"] = seed
        touched.append("Answer Seed")

    # ── Build Verbatim Digest ─────────────────────────────────────────────────
    bvd = nodes["Build Verbatim Digest"]["parameters"]["jsCode"]
    if "rowsUse" in bvd:
        print("Build Verbatim Digest: already applied")
    else:
        one(bvd, BVD_ANCHOR, "Build Verbatim Digest rows[0] block")
        bvd = bvd.replace(BVD_ANCHOR, BVD_NEW)
        node_check(bvd, "Build Verbatim Digest")
        nodes["Build Verbatim Digest"]["parameters"]["jsCode"] = bvd
        touched.append("Build Verbatim Digest")

    # ── Gate Verdict ──────────────────────────────────────────────────────────
    gv = nodes["Gate Verdict"]["parameters"]["jsCode"]
    if "policyClaims" in gv:
        print("Gate Verdict: already applied")
    else:
        one(gv, GV_1B_TAIL_ANCHOR, "Gate Verdict #1b tail")
        gv = gv.replace(GV_1B_TAIL_ANCHOR, GV_1C)
        one(gv, GV_EVFIRST_ANCHOR, "Gate Verdict _evFirst loop")
        gv = gv.replace(GV_EVFIRST_ANCHOR, GV_EVFIRST_NEW)
        one(gv, GV_CLAIMS_ANCHOR, "Gate Verdict claims assembly")
        gv = gv.replace(GV_CLAIMS_ANCHOR, GV_POLICY)
        one(gv, GV_EXTRA_ANCHOR, "Gate Verdict extra.link_coverage")
        gv = gv.replace(GV_EXTRA_ANCHOR, GV_EXTRA_NEW)
        node_check(gv, "Gate Verdict")
        nodes["Gate Verdict"]["parameters"]["jsCode"] = gv
        touched.append("Gate Verdict")

    # ── SECOND LAP: the two regressions the first staging probe run exposed ───
    seed2 = nodes["Answer Seed"]["parameters"]["jsCode"]
    if "never as a volunteered caveat" in seed2:
        print("Answer Seed (2nd lap): already applied")
    else:
        one(seed2, AS_ASKER2_ANCHOR, "Answer Seed B5017 sentence")
        seed2 = seed2.replace(AS_ASKER2_ANCHOR, AS_ASKER2_NEW)
        node_check(seed2, "Answer Seed (2nd lap)")
        nodes["Answer Seed"]["parameters"]["jsCode"] = seed2
        if "Answer Seed" not in touched:
            touched.append("Answer Seed")

    # ── FOURTH LAP: p_since on the verbatim window made an empty window LIE ───
    pr4 = nodes["Plan Request"]["parameters"]["jsCode"]
    if "NO p_since (probed live 2026-08-23, exec 101420)" in pr4:
        print("Plan Request (4th lap): already applied")
    elif "params.p_since = day(_vDays);" in pr4:
        one(pr4, PR_PSINCE_ANCHOR, "Plan Request verbatim p_since")
        pr4 = pr4.replace(PR_PSINCE_ANCHOR, PR_PSINCE_NEW)
        node_check(pr4, "Plan Request (4th lap)")
        nodes["Plan Request"]["parameters"]["jsCode"] = pr4
        if "Plan Request" not in touched:
            touched.append("Plan Request")

    gv3 = nodes["Gate Verdict"]["parameters"]["jsCode"]
    if "narrowed 2026-08-23 (exec 101395)" in gv3:
        print("Gate Verdict (3rd lap): already applied")
    else:
        one(gv3, GV_FIELDKEYS_ANCHOR, "Gate Verdict #1c FIELD keys")
        gv3 = gv3.replace(GV_FIELDKEYS_ANCHOR, GV_FIELDKEYS_NEW)
        node_check(gv3, "Gate Verdict (3rd lap)")
        nodes["Gate Verdict"]["parameters"]["jsCode"] = gv3
        if "Gate Verdict" not in touched:
            touched.append("Gate Verdict")

    gv2 = nodes["Gate Verdict"]["parameters"]["jsCode"]
    if "G1(e)" in gv2:
        print("Gate Verdict (2nd lap): already applied")
    else:
        one(gv2, GV_OFFTOPIC2_ANCHOR, "Gate Verdict off_topic push")
        gv2 = gv2.replace(GV_OFFTOPIC2_ANCHOR, GV_OFFTOPIC2_NEW)
        node_check(gv2, "Gate Verdict (2nd lap)")
        nodes["Gate Verdict"]["parameters"]["jsCode"] = gv2
        if "Gate Verdict" not in touched:
            touched.append("Gate Verdict")

    return touched


CHECKS = [
    ("PC prev_offer read", "Prep Context", "jsCode", "prev_offer = pl.pending_offer"),
    ("PC prev_offer returned", "Prep Context", "jsCode", "prev_offer: prev_offer,"),
    ("FR records items", "Format Reply", "jsCode", "pendingOffer = { kind:"),
    ("FR returns pending_offer", "Format Reply", "jsCode", "pending_offer: pendingOffer } }];"),
    ("SC persists pending_offer", "Save Conversation", "jsonBody", "{ pending_offer: po }"),
    ("PR offerBind computed", "Plan Request", "jsCode", "const offerBind = offerYes ?"),
    ("PR offer branch", "Plan Request", "jsCode", "} else if (offerBind) {"),
    ("PR offer_bound period", "Plan Request", "jsCode", "planPeriod = 'offer_bound'"),
    ("PR anaphor arm", "Plan Request", "jsCode", "const CONT_ANAPHOR ="),
    ("PR _prevTopic helper", "Plan Request", "jsCode", "const _prevTopic = function ()"),
    ("PR offer_bind on return", "Plan Request", "jsCode", "offer_bind: offerBind, period: planPeriod,"),
    ("AS renders offer_bind", "Answer Seed", "jsCode", "const ob = plan.offer_bind;"),
    ("AS ACCEPT_RE deleted", "Answer Seed", "jsCode", None),
    ("AS OFFER_TAIL_RE deleted", "Answer Seed", "jsCode", None),
    ("AS identity answer shape", "Answer Seed", "jsCode",
     "decline that claim AND, in the same reply, go on and answer their question for"),
    ("GV field coverage", "Gate Verdict", "jsCode", "let fieldCoverage = 0;"),
    ("GV _evFull", "Gate Verdict", "jsCode", "const _evFull = [];"),
    ("GV gated-denial name block", "Gate Verdict", "jsCode", "the gate refused names for this turn"),
    ("GV internals scrub", "Gate Verdict", "jsCode", "INTERNALS: your draft names backend machinery"),
    ("GV missing source", "Gate Verdict", "jsCode", "MISSING SOURCE: the member asked you to search"),
    ("GV identity-answer", "Gate Verdict", "jsCode", "IDENTITY-ANSWER: declining the typed name"),
    ("GV claims include policy", "Gate Verdict", "jsCode",
     "identityClaims.concat(policyClaims, linkClaims, hClaims)"),
    ("GV extra.field_coverage", "Gate Verdict", "jsCode", "extra.field_coverage = fieldCoverage"),
    ("AS p_call_type real values", "Answer Seed", "jsCode",
     "Mogul Call, Expert Call, Channel Call, Chapter Event, Mastermind, Summit"),
    ("AS p_call_type lie gone", "Answer Seed", "jsCode", None),
    ("PR sets p_call_type", "Plan Request", "jsCode", "if (_callType) { params.p_call_type = _callType; }"),
    ("PR verbatim window", "Plan Request", "jsCode", "if (period === 'daily' && _vDays > 1) {"),
    ("BVD concatenates rows", "Build Verbatim Digest", "jsCode", "const rowsUse = rows.slice(0, askedDays);"),
    ("BVD labels the window", "Build Verbatim Digest", "jsCode",
     "dates[dates.length - 1] + ' to ' + dates[0]"),
    ("AS identity caveat conditional", "Answer Seed", "jsCode", "never as a volunteered caveat"),
    ("GV off_topic exempts identity redirect", "Gate Verdict", "jsCode",
     "!_shortTurn && !_idOther"),
    ("GV #1c narrowed to event URL fields", "Gate Verdict", "jsCode",
     'const FIELD = /\\\\?"(registration_url|event_url)\\\\?"'),
    ("PR verbatim window has no p_since", "Plan Request", "jsCode", None),
]


def verify(nodes):
    bad = []
    for name, node, key, needle in CHECKS:
        code = nodes[node]["parameters"][key]
        if needle is None:                     # deletion assertions
            gone = {"AS ACCEPT_RE deleted": "ACCEPT_RE",
                    "AS OFFER_TAIL_RE deleted": "OFFER_TAIL_RE",
                    "AS p_call_type lie gone": "mogul | expert | channel | chapter",
                    "PR verbatim window has no p_since": "params.p_since = day(_vDays);"}[name]
            ok = gone not in code
        else:
            ok = needle in code
        if not ok:
            bad.append(name)
    return bad


def main():
    assert STAGING_ID != PROD_ID
    wf = api("GET", f"/workflows/{STAGING_ID}")
    assert wf.get("id") == STAGING_ID, f"GET failed / wrong workflow: {str(wf)[:200]}"
    assert "STAGING" in wf.get("name", ""), f"refusing to edit {wf.get('name')!r}"
    nodes = {n["name"]: n for n in wf["nodes"]}

    touched = transform(nodes)
    print("nodes edited:", ", ".join(touched) or "(none)")

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

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    bad = verify(n2)
    assert not bad, f"POST-PUT VERIFY FAILED: {bad}"
    for name, _n, _k, _v in CHECKS:
        print(f"  ✓ {name}")
    print(f"active: {wf2.get('active')} · staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
