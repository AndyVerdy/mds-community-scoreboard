#!/usr/bin/env python3
"""Fixwave 4 — 2026-08-23. The last six graded failures on STAGING (bqHstPDi84uOhTCJ,
versionId 4e025c16). PROD 12wj6h1TWqb0d4Dq is never touched.

Evidence: .superpowers/sdd/2026-08-22-finder/eval/rerun3_pairs.json (+ rerun2_pairs.json for the
before/after of the two the previous wave was accused of breaking).

  1. A4077 — the wave-3 #1c coverage repair appended the SUMMIT registration link to an answer
     about Amazon Accelerate and the Commerce Roundtable, and a retrieval-narration sentence
     ("That query pulled up the Singapore Summit schedule instead") sailed through the internals
     check. TWO Gate Verdict causes, both fixed here:
       (a) #1c's owner test was 70%-of-the-long-words. "MDS Summit Singapore" matched because the
           draft happened to contain "Singapore" and "Summit" — in the sentence narrating the
           WRONG tool result. The owner must now be NAMED (whole phrase, or the same words
           contiguous in another order).
       (b) the internals mask treated a bare apostrophe as a quote delimiter, so "aren't … you'd"
           swallowed the offending sentence; and the check had no pattern for narration that names
           no backend word at all. Mask fixed, narration patterns added.
  2. B5049 — NOT a wave-3 regression. Proven: the tool args are byte-identical between run 2
     (exec 101306, found) and run 3 (exec 101491, not found); the public-agenda fallback still
     works for the same unregistered probe member ("welcome dinner" -> found:true, viewing
     "public agenda"); and the Night Out activity is simply GONE from the 37-row Summit agenda
     (Tue 25 Aug 22:30 now reads "Explore Singapore Beyond the Summit"). It survives as its own
     catalog row — "MDS Summit Singapore Night Out", rec4SEDr6vYnwzxwT, Tue Aug 25 22:30, RSVP
     https://luma.com/SingaporeNightOut — which is the standing Night-Out-is-not-the-Summit trap.
     So the fix is the fallback the required behaviour actually needs: Plan Request spends the
     SECOND preload slot on the events catalog for a reminder ask, Answer Seed renders the rule,
     and Answer Merge stamps the tool's own miss with what to do next.
  3. A4100 — member_dossier_v2 returns kind=membership / label=status ("Staff"). The tenure answer
     never said it. Answer Seed schema + a deterministic Gate Verdict STATUS check.
  4. A4095 — the three-day digest ended "...Registration: ht...". Build Verbatim Digest cut at
     exactly 3900 characters. It now drops whole blank-line-separated blocks from the end and says
     it was shortened; the WhatsApp budget is unchanged.
  5. A4080 — every tracked TikTok-agency partner carries review_count 0 (read live today, and the
     count IS already in the payload — no RPC change needed). A partner nobody has reviewed is
     UNTESTED, not endorsed. Answer Seed rule + a deterministic Gate Verdict UNTESTED check.
  6. B5050 — the correction bound to the right activity but re-asked for its name and gave the
     wrong reason. Answer Merge stamps the registration-blocked reminder result with the binding.

Five nodes, ONE PUT, ONE deactivate->activate bounce, re-GET + assert.
Every anchor is asserted count == 1 and NEVER loosened: 0 means the node drifted -> STOP.
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


def sub(hay, old, new, label):
    one(hay, old, label)
    return hay.replace(old, new, 1)


# ══════════════════ 1 · Gate Verdict — the #1c owner must be NAMED (A4077) ══════════════════

GV_FIELDCOV_ANCHOR = "let fieldCoverage = 0;"

GV_NAMED_HELPER = r"""// A4077 (fixwave 4, 2026-08-23). #1c decided a URL "belongs" to the answer when 70% of its
// owner's long words appeared ANYWHERE in the draft. On "Is accelerate or commerce roundtable
// better to attend" the owner was "MDS Summit Singapore" and the draft contained "Singapore" and
// "Summit" — inside the sentence narrating the wrong tool result — so the Summit's registration
// link was pinned to an answer about Amazon Accelerate and the Commerce Roundtable (exec 101466).
// A bag of words is not a name. To carry an entity's URL the answer has to NAME the entity: its
// whole name as a phrase, or exactly the same words contiguous in another order ("the MDS
// Singapore Summit"). Nothing looser. Shared with the partner check below, which needs the same
// question asked of a company name.
const _nameInAnswer = function (nm, hay) {
  const w = function (s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(' ')
      .filter(function (x) { return x.length > 1; });
  };
  const ow = w(nm);
  if (!ow.length || ow.length > 9) { return false; }
  const aw = w(hay);
  if ((' ' + aw.join(' ') + ' ').indexOf(' ' + ow.join(' ') + ' ') !== -1) { return true; }
  if (ow.length < 2) { return false; }
  const key = ow.slice().sort().join(' ');
  for (let i = 0; i + ow.length <= aw.length; i++) {
    if (aw.slice(i, i + ow.length).sort().join(' ') === key) { return true; }
  }
  return false;
};
let fieldCoverage = 0;"""

GV_OWNERNAMED_ANCHOR = """  const ownerNamed = function (nm) {
    const h = answerText.toLowerCase();
    const ws = String(nm).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ')
      .filter(function (w) { return w.length >= 4; });
    if (!ws.length) { return false; }
    return ws.filter(function (w) { return h.indexOf(w) !== -1; }).length >= Math.ceil(0.7 * ws.length);
  };"""

GV_OWNERNAMED_NEW = """  const ownerNamed = function (nm) { return _nameInAnswer(nm, answerText); };"""


# ═══════════ 2 · Gate Verdict — the internals check missed the narration (A4077) ═══════════

GV_MASK_ANCHOR = ("  const masked = answerText.replace("
                  "/[\"'\\u201c\\u201d\\u2018\\u2019][^\"'\\u201c\\u201d\\u2018\\u2019]{4,}"
                  "[\"'\\u201c\\u201d\\u2018\\u2019]/g, ' ');")

GV_MASK_NEW = r"""  // fixwave 4: the mask treated a bare apostrophe as a quote delimiter, so in the live A4077 draft
  // the span from "aren't" to "you'd" was blanked — taking the words "schedule tool" with it — and
  // the check passed a reply that opens by narrating the retrieval (exec 101466, gate: pass). Only
  // real quotation marks mask now: double quotes, curly doubles, and a single quote that stands
  // OUTSIDE a word. The apostrophe in "aren't" is no longer a quote.
  const masked = answerText
    .replace(/["\u201c][^"\u201c\u201d]{4,}["\u201d]/g, ' ')
    .replace(/(^|[\s(\[])['\u2018][^'\u2018\u2019]{4,}['\u2019](?=[\s.,;:!?)\]]|$)/g, ' ');"""

GV_FOUND_ANCHOR = "  const found = hard.concat(soft.length ? ['tool/rows retrieval narration'] : []);"

GV_FOUND_NEW = r"""  // fixwave 4 — NARRATION OF THE RETRIEVAL ITSELF. "That query pulled up the Singapore Summit
  // schedule instead — let me get the actual details … since those two aren't part of the Summit
  // schedule tool." Not one backend identifier in it, and the whole opening is still a story about
  // how the answer was fetched. The member never hears that story: what was searched, what came
  // back, what missed. Bounded to retrieval subjects so a real product sentence ("Helium 10 is the
  // tool most members use", "Anthony came back with a fix") is untouched, and the member's own
  // quoted spans are already masked out above.
  const NARR = [
    /\b(?:that|this|the|those|these|both|my|your|it)\b[^.!?\n]{0,30}\b(?:quer(?:y|ies)|searches|search|lookups?|tools?|preload(?:ed)?|evidence)\b[^.!?\n]{0,60}\b(?:pulled|returned|came back|surfaced|brought back|gave me|showed)\b/i,
    /\b(?:quer(?:y|ies)|searches|search|lookups?|tools?)\b[^.!?\n]{0,30}\bpulled up\b/i,
    /\b(?:schedule|search|lookup|event|events|partner|partners|video|videos|member|dossier|digest)\s+tool\b/i,
    /\b(?:it|that|this|the (?:search|query|lookup|tool|data|evidence|results?))\s+came back\s+(?:with|empty|blank|clean|nothing)\b/i,
    /\b(?:i|we)\s+(?:ran|called|queried|fetched|pulled)\s+(?:the|a|an|another|my)\b[^.!?\n]{0,40}\b(?:tool|query|lookup|search|endpoint|rpc)\b/i
  ];
  const narr = NARR.filter(function (re) { return re.test(masked); });
  const found = hard.concat(soft.length ? ['tool/rows retrieval narration'] : [],
    narr.length ? ['narrating how the answer was fetched'] : []);"""


# ═════ 3 · Gate Verdict — two new deterministic policy checks (A4100 status, A4080 untested) ═════

GV_CLAIMS_ANCHOR = "const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"

GV_CLAIMS_NEW = r"""// (5) THE ASKER'S OWN STATUS IS HALF OF THEIR OWN TENURE ANSWER (A4100, fixwave 4). The join date
// is right now that member_dossier_v2 returns the membership rows ("You joined MDS on February 8,
// 2023") — but this asker is MDS STAFF, and an answer about how long they have been a member that
// calls them an ordinary member is wrong about the one thing the question is about. Their own
// record, so it is theirs to be told. Deterministic: the question is about their own membership,
// the evidence carries a status, the status is not a plain member value, the draft never says it.
try {
  // First person REQUIRED: "how long has Nasir been a member" is somebody else's tenure and this
  // status belongs to the asker. The membership-rows test below is the second lock on that.
  const selfTenure = /\b(?:i|me|my|i(?:'|\u2019)ve|ive)\b/i.test(_memberMsg)
    && (/\b(?:how long|since when)\b[^?]{0,60}\b(?:member|membership|joined|join)\b/i.test(_memberMsg)
      || /\bwhen did i (?:join|become)\b/i.test(_memberMsg)
      || /\b(?:am i|what(?:'|\u2019)?s my)\b[^?]{0,40}\b(?:membership|member status|still a member)\b/i.test(_memberMsg)
      || /\bmy membership\b[^?]{0,40}\b(?:status|since|start(?:ed)?)\b/i.test(_memberMsg));
  const hasMembership = /\\?"kind\\?"\s*:\s*\\?"membership\\?"/.test(evRaw);
  const sm = evRaw.match(/\\?"label\\?"\s*:\s*\\?"status\\?"\s*,\s*\\?"detail\\?"\s*:\s*\\?"([^"\\]{2,40})/);
  const st = (hasMembership && sm) ? String(sm[1]).trim() : null;
  if (selfTenure && st && !/^(?:current member|new member)$/i.test(st)
      && answerText.toLowerCase().indexOf(st.toLowerCase()) === -1) {
    policyClaims.push('STATUS: this member\u2019s own record says their membership status is "' + st
      + '" — not a plain member — and they just asked about their own membership. Say it in the '
      + 'reply: give the join date AND that they are ' + st + '. It is their own record, so it is '
      + 'theirs to be told; do not describe them as an ordinary member.');
  }
} catch (e) {}

// (6) A PARTNER NOBODY HAS REVIEWED IS UNTESTED, NOT ENDORSED (A4080, fixwave 4). partner_lookup
// returns review_count on every row, and every tracked TikTok-agency partner carries 0 (read live
// 2026-08-23). The draft offered three of them as "vetted partner deals" with member perks, which
// reads as an endorsement MDS members have never actually given. #50's never-say-weak rule does
// not cover this: "nobody has reviewed this yet" is not a rating, it is the absence of one, and
// the member is entitled to it. Only names the answer actually gives are counted.
try {
  if (evRaw.indexOf('partner_url') !== -1 && evRaw.indexOf('review_count') !== -1) {
    const PNM = /\\?"name\\?"\s*:\s*\\?"([^"\\]{2,80})/g;
    const PRC = /\\?"review_count\\?"\s*:\s*(\d{1,6})/g;
    const pn = []; let pm = null, pg = 0;
    while ((pm = PNM.exec(evRaw)) !== null && pg++ < 400) { pn.push({ at: pm.index, name: pm[1] }); }
    const nameBefore = function (idx) {
      let best = null;
      for (let i = 0; i < pn.length; i++) {
        if (pn[i].at > idx) { break; }
        if (idx - pn[i].at < 2000) { best = pn[i].name; }
      }
      return best;
    };
    const zero = []; let rc = null, rg = 0;
    while ((rc = PRC.exec(evRaw)) !== null && rg++ < 400) {
      if (Number(rc[1]) !== 0) { continue; }
      const n0 = nameBefore(rc.index);
      if (n0 && zero.indexOf(n0) === -1 && _nameInAnswer(n0, answerText)) { zero.push(n0); }
    }
    const caveat = /\b(?:no (?:member )?reviews?|no reviews yet|nobody (?:has )?review|un(?:tested|reviewed|proven)|not (?:yet )?reviewed|no member feedback|no ratings? yet|no feedback (?:yet|on file))\b/i;
    if (zero.length && !caveat.test(answerText)) {
      policyClaims.push('UNTESTED: ' + zero.slice(0, 6).join(', ') + ' '
        + (zero.length > 1 ? 'have' : 'has') + ' ZERO member reviews in the partner directory, and '
        + 'your draft presents ' + (zero.length > 1 ? 'them' : 'it') + ' like an endorsement. Name '
        + 'the untested ones as untested — no member reviews on file yet — and keep them clearly '
        + 'apart from the ones members actually vouched for in the chats or on Facebook. Never '
        + 'invent praise for a partner nobody has reviewed.');
    }
  }
} catch (e) {}

const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"""


# ═══ 4 · Answer Merge — stamp the schedule tool's own miss / refusal (B5049, B5050) ═══

AM_ANCHOR = """  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]"';
  return { type: 'tool_result', tool_use_id: req.tool_use_id, content: body };"""

AM_NEW = r"""  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]"';
  // B5049 / B5050 (fixwave 4, 2026-08-23). Two shapes the prompt kept losing, both read off the
  // tool's OWN answer so they fire every time, on the turn, with no extra gate lap:
  //  · op=where/remind MISSED. "Not on the agenda" is not "MDS does not have it". The Summit
  //    agenda holds the Summit's own programme; MDS side events are SEPARATE catalog rows (the
  //    Night Out is rec4SEDr6vYnwzxwT with its own luma RSVP, and it left the agenda entirely on
  //    2026-08-23). She told the member it does not exist and asked them to rename it (exec
  //    101491) — the one thing the standing Night-Out-is-not-the-Summit trap forbids.
  //  · op=remind REFUSED because they are not registered. The activity is already identified; the
  //    reminder is the only thing refused. Re-asking for the name re-opens a question that was
  //    answered a turn earlier, and blames the wrong thing (exec 101493).
  try {
    const _tn = String(req.tool_name || '');
    if (_tn === 'event_schedule' && r && typeof r === 'object' && !Array.isArray(r)) {
      const _a = typeof req.tool_args === 'string' ? JSON.parse(req.tool_args || '{}') : (req.tool_args || {});
      const _op = String(_a.op || '');
      const _q = String(_a.q || '').trim().slice(0, 80);
      const _note = String(r.note || '');
      let _hint = null;
      if (r.ok === false && /registered attendee/i.test(_note)) {
        _hint = 'MILLIE — DETERMINISTIC NOTE: the activity is already identified'
          + (_q ? ' ("' + _q + '")' : '') + ' and the ONLY thing refused here is the reminder. The '
          + 'reason is registration, not a missing activity. Say exactly that, keep the activity\'s '
          + 'name, day and start time in the reply, give its RSVP or registration link, and do NOT '
          + 'ask the member to name it again — they already named it.';
      } else if (_q && (_op === 'where' || _op === 'remind' || _op === 'speaker') && r.found === false) {
        _hint = 'MILLIE — DETERMINISTIC NOTE: not on the agenda is NOT "MDS does not have it". MDS '
          + 'side events — the Night Out, the Pre-Event Dinner, the Speaker\'s and Women\'s Lunches, '
          + 'a Mastermind — are their OWN events, separate rows from the Summit, so they never show '
          + 'up on the Summit agenda. The preloaded evidence on this turn already carries the events '
          + 'catalog: look there for "' + _q + '" and, if it is there, answer with its name, its day '
          + 'and start time in the venue\'s timezone, and its RSVP/registration link. Do not tell the '
          + 'member it does not exist, and do not ask them to rename it.';
      }
      if (_hint) { body = body + NL + _hint; }
    }
  } catch (e) {}
  return { type: 'tool_result', tool_use_id: req.tool_use_id, content: body };"""


# ═══ 5 · Plan Request — spend the second preload slot on the catalog for a reminder ask ═══

PR_OVERRIDE_ANCHOR = """
// Organic-review overrides (Andy 2026-07-29): these classes must reach the LOOP.
if (intent === 'action' && /register/i.test(rawText || '')) { route = 'llm'; }
if (/recommend|suggest/i.test(rawText || '') && (/\\bcalls?\\b/i.test(rawText || '')) && route !== 'llm') { route = 'llm'; }
"""

PR_REMIND_NEW = PR_OVERRIDE_ANCHOR + r"""
// B5049 / B5050 REMINDER LANE (fixwave 4, 2026-08-23). "remind me about night out in 5 min"
// planned a content_search for the words "remind" and "night" — nothing about the event at all —
// so when the schedule tool missed on the agenda there was nothing else in the turn and she told
// the member the activity does not exist. MDS side events are their own catalog rows (the Night
// Out is rec4SEDr6vYnwzxwT, RSVP luma.com/SingaporeNightOut) and only event_lookup can see them.
// The SECOND preload slot is free on this turn, so spend it on the catalog whenever the member
// asks to be reminded about something they NAMED. The correction turn ("no, in 5 min from now")
// carries no name at all: it reuses the terms the previous plan stored, which Save Conversation
// already persists on plan.raw_params — no new state, no new channel.
let remindSubject = null;
try {
  const _rTxt = String(rawText || '');
  const _isRem = /\bremind(?:er|ers)?\b/i.test(_rTxt);
  // "N minutes BEFORE <thing>" keeps its tail; a trailing "in N min" and everything after it goes.
  let _subj = _rTxt
    .replace(/\b\d+\s*(?:m|min|mins|minute|minutes|h|hr|hrs|hour|hours|day|days)\s*(?:before|prior to|ahead of)\b/ig, ' ')
    .replace(/\b\d+\s*(?:m|min|mins|minute|minutes|h|hr|hrs|hour|hours|day|days)\b[\s\S]*$/i, ' ')
    .replace(/\b(?:can|could|would|will|please|pls|you|your|i|me|my|us)\b/ig, ' ')
    .replace(/\bremind(?:er|ers)?\b/ig, ' ')
    .replace(/\b(?:about|of|for|on|to|the|a|an)\b/ig, ' ')
    .replace(/\b(?:in|at|before|prior|ahead|from now|right now|now|today|tomorrow|tonight|later)\b/ig, ' ')
    .replace(/[^A-Za-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (_subj.length < 3) { _subj = ''; }
  const _pp = ctx.prev_plan;
  const _prevRem = (_pp && _pp.raw_op === 'event_lookup' && _pp.raw_params
    && Array.isArray(_pp.raw_params.p_terms) && _pp.raw_params.p_terms.length)
    ? _pp.raw_params.p_terms : null;
  if (_isRem && _subj) { remindSubject = _subj; }
  else if ((_isRem || (followup && _rTxt.length <= 60)) && _prevRem) { remindSubject = _prevRem.join(' '); }
  if (remindSubject) {
    raw_op = 'event_lookup';
    raw_params = { p_phone: mem.to, p_terms: [remindSubject], p_limit: 6 };
  }
} catch (e) { remindSubject = null; }
"""

PR_RET_ANCHOR = "route: route, intent: intent, focus_chat: chat, offer_bind: offerBind, period: planPeriod,"
PR_RET_NEW = ("route: route, intent: intent, focus_chat: chat, offer_bind: offerBind, "
              "remind_subject: remindSubject, period: planPeriod,")


# ══════════════════════════════════ 6 · Answer Seed ══════════════════════════════════

AS_ROLENOTE_ANCHOR = """      + 'do not reference or lean on the claimed role in the reply. Verification happens outside this chat.' + NL + NL;
  }
} catch (e) {}"""

AS_REMINDNOTE_NEW = AS_ROLENOTE_ANCHOR + r"""
// B5049 / B5050 (fixwave 4, 2026-08-23): Plan Request has already put the events catalog for the
// named thing into the preloaded evidence. This note is what makes her look there instead of
// treating the Summit agenda as the whole world.
// LAP 3 (exec 101577): the first wording said only "never re-label the hour UTC" and she dropped
// the start time from the answer altogether — worse than a wrong label — so the note now demands
// the time outright. The reasoning stays HERE, in the code; the member-facing prompt below carries
// the instruction only, never a bug number or an execution id.
let remindNote = '';
try {
  if (plan.remind_subject) {
    remindNote = 'REMINDER ASK — the member named "' + String(plan.remind_subject).slice(0, 80)
      + '". The events CATALOG for those words is already in the preloaded evidence below, because '
      + 'the Summit agenda only holds the Summit\u2019s own programme: MDS side events (the Night Out, '
      + 'the Pre-Event Dinner, the Speaker\u2019s and Women\u2019s Lunches, a Mastermind) are SEPARATE '
      + 'events with their own RSVP link and never appear on that agenda. So if event_schedule '
      + 'cannot find it, that is NOT proof MDS does not have it — answer from the catalog row: its '
      + 'name, its day and ALWAYS its START TIME. The catalog prints the hour as the event itself '
      + 'lists it, for its own location: give it in 12-hour form and name the venue\u2019s timezone '
      + 'when the schedule result names one ("10:30 pm Singapore time"); if you are not sure of the '
      + 'zone, still give the hour and call it the local time at the venue. Leaving the time out is '
      + 'worse than labelling it. Then its RSVP/registration link. Never ask '
      + 'the member to rename the thing they just named. If the REMINDER itself cannot be set '
      + 'because they are not registered, say that plainly as the reason and say nothing about the '
      + 'activity being missing.' + NL + NL;
  }
} catch (e) {}"""

AS_FINALUSER_ANCHOR = """const finalUser = askerLine + (preload
  ? roleNote + meCtx + 'PRELOADED EVIDENCE — a deterministic search already ran for this exact message; treat it as your first tool result:' + NL + preload + NL + NL + 'MEMBER MESSAGE:' + NL + current
  : roleNote + current);"""

AS_FINALUSER_NEW = """const finalUser = askerLine + (preload
  ? roleNote + remindNote + meCtx + 'PRELOADED EVIDENCE — a deterministic search already ran for this exact message; treat it as your first tool result:' + NL + preload + NL + NL + 'MEMBER MESSAGE:' + NL + current
  : roleNote + remindNote + current);"""

AS_DOSSIER_ANCHOR = ("{ name: 'member_dossier', description: 'What MDS knows about THE ASKER "
                     "themselves: their profile, chats, activity, events. Use for \"what do you "
                     "know about me / my application\".',")

AS_DOSSIER_NEW = ("{ name: 'member_dossier', description: 'What MDS knows about THE ASKER "
                  "themselves: their profile, chats, activity, events. Use for \"what do you "
                  "know about me / my application\". CARRIES THEIR OWN MEMBERSHIP ROWS (A4100): "
                  "kind=\"membership\" with label=\"member_since\" (the real join date) and "
                  "label=\"status\". A question about how long they have been a member, or about "
                  "their own membership, is answered with BOTH - the join date AND the status. A "
                  "status that is not \"Current Member\" (Staff, for instance) is the more "
                  "important half and it is their own record, so say it plainly; never round it "
                  "down to \"a member\".',")

AS_JUDGMENT_ANCHOR = ("'- RECOMMEND AS JUDGMENT (#50): when a tool row carries fit_reason or "
                      "strength_note, fold them into the recommendation in plain words (\"worth "
                      "it for you - heavy on logistics, and one of the most-watched sessions\"). "
                      "Never recite engagement numbers or scores; never say a video/event/partner "
                      "is weak, poorly rated or badly attended - if it ranks low, it simply "
                      "appears lower or not at all.',")

AS_JUDGMENT_NEW = AS_JUDGMENT_ANCHOR + (
    "\n  '- UNTESTED IS NOT WEAK (A4080, 2026-08-23): partner rows carry review_count. A "
    "review_count of 0 means NOBODY in MDS has reviewed that partner yet - say so beside the name "
    "(\"no member reviews on file yet\") and never dress it up as vetted, proven, trusted or "
    "member-loved. That is not a rating and #50 does not cover it: it is the absence of one, and "
    "the member is entitled to it before they spend money. Partners members actually vouched for "
    "in the chats or on Facebook are a DIFFERENT list - keep the two apart and say which is which.',")


# ═══════════ 7 · Build Verbatim Digest — cut at a boundary, and say it was cut (A4095) ═══════════

BV_ANCHOR = """const link = (plan.chat_links || {})[r.meta.chat_name];
const tail = link ? (NL + NL + 'Open the chat: ' + link) : '';
if ((out + tail).length > 3900) { out = out.slice(0, 3900 - tail.length) + '...'; }
out += tail;"""

BV_NEW = r"""const link = (plan.chat_links || {})[r.meta.chat_name];
const tail = link ? (NL + NL + 'Open the chat: ' + link) : '';
// A4095 (fixwave 4, 2026-08-23). The old guard sliced at exactly 3900 characters, so the three-day
// Centurion digest ended "…Registration: ht…" — a half-typed URL in the middle of a sentence, which
// reads as a broken answer rather than a shortened one. WhatsApp's 4096-character limit is real and
// the budget does not move; what changes is WHERE the cut lands and that the cut is admitted. Drop
// whole blank-line-separated blocks from the END first (oldest content, each self-contained), then
// fall back to the last line break, and only ever break on whitespace — never mid-word.
if ((out + tail).length > 3900) {
  const NN = NL + NL;
  const note = NN + '_Shortened to fit WhatsApp - the oldest part is cut. Ask me about one day for the rest._';
  const room = 3900 - tail.length - note.length;
  const parts = out.split(NN);
  while (parts.length > 1 && parts.join(NN).length > room) { parts.pop(); }
  let cut = parts.join(NN);
  if (cut.length > room) {
    cut = cut.slice(0, room);
    const lb = cut.lastIndexOf(NL);
    cut = lb > room * 0.5 ? cut.slice(0, lb) : cut.replace(/\s+\S*$/, '');
  }
  out = cut.replace(/\s+$/, '') + note;
}
out += tail;"""


# ══════ 8 · LAP 2 — what the first probe run showed (2026-08-23, exec 101546 / 101562) ══════
# Lap 1 killed the foreign link and the missing-activity answer. Two things survived it:
#   · the narration paraphrased around the new patterns — "That TOOL GRABBED the Summit schedule
#     instead" uses no verb the check knew, so the gate passed it (exec 101546);
#   · the Night Out answers picked up the SUMMIT registration link, because "MDS Summit Singapore
#     Night Out" CONTAINS "MDS Summit Singapore" and the answer therefore named both (exec 101562).

GV_NARR_TAIL_ANCHOR = r"""    /\b(?:i|we)\s+(?:ran|called|queried|fetched|pulled)\s+(?:the|a|an|another|my)\b[^.!?\n]{0,40}\b(?:tool|query|lookup|search|endpoint|rpc)\b/i
  ];"""

GV_NARR_TAIL_NEW = r"""    /\b(?:i|we)\s+(?:ran|called|queried|fetched|pulled)\s+(?:the|a|an|another|my)\b[^.!?\n]{0,40}\b(?:tool|query|lookup|search|endpoint|rpc)\b/i,
    // LAP 2: a retrieval noun under a determiner, doing something. "That tool GRABBED the Summit
    // schedule" (exec 101546) walked past the verb list above; enumerating verbs one live probe at
    // a time is the losing game, so the shape is what is matched now — determiner + tool/query/
    // lookup/search/evidence + an action. The verb set stays explicit so "the tool SAVED them
    // hours" and "Helium 10 is the tool most members use" are still ordinary product sentences,
    // and the determiner requirement leaves "one AI tool, uses CLI instead" alone.
    /\b(?:that|this|the|those|these|both|my)\b(?:\s+\w+){0,2}\s+(?:quer(?:y|ies)|search(?:es)?|lookups?|tools?|preload|evidence)\s+(?:just |already |only |actually |apparently |first )?(?:pulled|grabbed|returned|surfaced|fetched|loaded|landed|matched|picked|produced|delivered|handed|showed|gave|came|got|brought|brings?|returns?|pulls?|grabs?|hits?|shows?)\b/i,
    /\b(?:that|this|the|those|these|both|my)\s+(?:\w+\s+){0,2}(?:quer(?:y|ies)|search(?:es)?|lookups?|tools?|preload(?:ed)?|evidence)\b[^.!?\n]{0,50}\b(?:instead|by mistake|not what you (?:need|asked|wanted)|wrong (?:one|tool|result|event|thing))\b/i
  ];"""

GV_OWNERNAMED2_ANCHOR = "  const ownerNamed = function (nm) { return _nameInAnswer(nm, answerText); };"

GV_OWNERNAMED2_NEW = r"""  // LAP 2 (B5049, exec 101562): "MDS Summit Singapore Night Out" is its OWN event and its name
  // CONTAINS the Summit's, so an answer entirely about the Night Out named the Summit too and the
  // repair pinned the Summit's registration link to it. That is the standing Night-Out-is-not-the-
  // Summit trap arriving at the link repair. When a LONGER owner from the same evidence is also
  // named, the shorter one is not what this answer is about and its URL does not belong here.
  const _ownerFlat = function (s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); };
  const ownerNamed = function (nm) {
    if (!_nameInAnswer(nm, answerText)) { return false; }
    const me = _ownerFlat(nm);
    for (let i = 0; i < owners.length; i++) {
      const other = _ownerFlat(owners[i].name);
      if (other.length > me.length && (' ' + other + ' ').indexOf(' ' + me + ' ') !== -1
          && _nameInAnswer(owners[i].name, answerText)) { return false; }
    }
    return true;
  };"""

AM_LAP2_ANCHOR = """      if (_hint) { body = body + NL + _hint; }
    }
  } catch (e) {}"""

AM_LAP2_NEW = r"""      if (_hint) { body = body + NL + _hint; }
    }
    // LAP 2 (A4077, exec 101546). Attach Embedding remaps event_lookup -> event_lookup_v3, and
    // Answer Tool routes every tool whose name starts with "event_" to the SCHEDULE endpoint — so
    // while a live event is running the model's catalog search answers with that event's own
    // schedule. That payload is LOAD-BEARING and stays: it is where "When is the MDS Singapore
    // Summit?" gets its dates, venue and registration link (exec 101463), which the catalog row
    // cannot give (it reads "already happened"). What has to stop is the model telling the member
    // about the mismatch — "That tool grabbed the Summit schedule instead". Naming it here, once,
    // on the turn, is cheaper and steadier than a gate regeneration lap.
    if ((_tn === 'event_lookup_v3' || _tn === 'event_lookup_v2' || _tn === 'event_lookup')
        && r && typeof r === 'object' && !Array.isArray(r)
        && (r.viewing || r.next_scope || r.activities || r.day_label)) {
      body = body + NL + 'MILLIE — DETERMINISTIC NOTE: while an MDS event is running, this call '
        + 'answers with THAT event\'s own schedule rather than a catalog search. That is expected, '
        + 'it is not a mistake, and it is not news the member needs. Use it if it helps the answer; '
        + 'otherwise ignore it silently and answer from the PRELOADED EVIDENCE you were already '
        + 'given this turn, which carries the events list. Never tell the member which tool '
        + 'returned what, that something came back "instead" or "by mistake", or anything else '
        + 'about how the answer was fetched — just answer the question.';
    }
  } catch (e) {}"""


# ═══════════════════════════════════ apply ═══════════════════════════════════

def transform(nodes):
    seen = {}
    for n in nodes:
        p = n.get("parameters") or {}
        name = n["name"]

        if name == "Gate Verdict":
            c = p["jsCode"]
            c = sub(c, GV_FIELDCOV_ANCHOR, GV_NAMED_HELPER, "GV fieldCoverage decl")
            c = sub(c, GV_OWNERNAMED_ANCHOR, GV_OWNERNAMED_NEW, "GV ownerNamed body")
            c = sub(c, GV_MASK_ANCHOR, GV_MASK_NEW, "GV internals mask")
            c = sub(c, GV_FOUND_ANCHOR, GV_FOUND_NEW, "GV internals found")
            c = sub(c, GV_CLAIMS_ANCHOR, GV_CLAIMS_NEW, "GV claims concat")
            # lap 2
            c = sub(c, GV_NARR_TAIL_ANCHOR, GV_NARR_TAIL_NEW, "GV NARR tail (lap2)")
            c = sub(c, GV_OWNERNAMED2_ANCHOR, GV_OWNERNAMED2_NEW, "GV ownerNamed longer-owner (lap2)")
            node_check(c, "Gate Verdict")
            p["jsCode"] = c
            seen["Gate Verdict"] = True

        elif name == "Answer Merge":
            c = p["jsCode"]
            c = sub(c, AM_ANCHOR, AM_NEW, "AM tool_result return")
            c = sub(c, AM_LAP2_ANCHOR, AM_LAP2_NEW, "AM event_lookup schedule note (lap2)")
            node_check(c, "Answer Merge")
            p["jsCode"] = c
            seen["Answer Merge"] = True

        elif name == "Plan Request":
            c = p["jsCode"]
            c = sub(c, PR_OVERRIDE_ANCHOR, PR_REMIND_NEW, "PR organic overrides")
            c = sub(c, PR_RET_ANCHOR, PR_RET_NEW, "PR chat return")
            node_check(c, "Plan Request")
            p["jsCode"] = c
            seen["Plan Request"] = True

        elif name == "Answer Seed":
            c = p["jsCode"]
            c = sub(c, AS_ROLENOTE_ANCHOR, AS_REMINDNOTE_NEW, "AS roleNote tail")
            c = sub(c, AS_FINALUSER_ANCHOR, AS_FINALUSER_NEW, "AS finalUser")
            c = sub(c, AS_DOSSIER_ANCHOR, AS_DOSSIER_NEW, "AS member_dossier schema")
            c = sub(c, AS_JUDGMENT_ANCHOR, AS_JUDGMENT_NEW, "AS #50 judgment rule")
            node_check(c, "Answer Seed")
            p["jsCode"] = c
            seen["Answer Seed"] = True

        elif name == "Build Verbatim Digest":
            c = p["jsCode"]
            c = sub(c, BV_ANCHOR, BV_NEW, "BV verbatim tail")
            node_check(c, "Build Verbatim Digest")
            p["jsCode"] = c
            seen["Build Verbatim Digest"] = True

    for want in ("Gate Verdict", "Answer Merge", "Plan Request", "Answer Seed", "Build Verbatim Digest"):
        assert seen.get(want), f"node not found in graph: {want}"
    return nodes


POST = [
    ("Gate Verdict", "const _nameInAnswer = function (nm, hay) {", 1),
    ("Gate Verdict", "if (!_nameInAnswer(nm, answerText)) { return false; }", 1),
    ("Gate Verdict", "Math.ceil(0.7 * ws.length)", 0),          # the bag-of-words test is GONE
    ("Gate Verdict", "narrating how the answer was fetched", 1),
    ("Gate Verdict", "const NARR = [", 1),
    ("Gate Verdict", "policyClaims.push('STATUS:", 1),
    ("Gate Verdict", "policyClaims.push('UNTESTED:", 1),
    ("Gate Verdict", "const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);", 1),
    ("Answer Merge", "MILLIE — DETERMINISTIC NOTE: the activity is already identified", 1),
    ("Answer Merge", "MILLIE — DETERMINISTIC NOTE: not on the agenda is NOT", 1),
    ("Plan Request", "let remindSubject = null;", 1),
    ("Plan Request", "raw_op = 'event_lookup';", 1),
    ("Plan Request", "remind_subject: remindSubject", 1),
    ("Answer Seed", "let remindNote = '';", 1),
    ("Answer Seed", "roleNote + remindNote + meCtx", 1),
    ("Answer Seed", "roleNote + remindNote + current", 1),
    ("Answer Seed", "CARRIES THEIR OWN MEMBERSHIP ROWS (A4100)", 1),
    ("Answer Seed", "UNTESTED IS NOT WEAK (A4080", 1),
    ("Build Verbatim Digest", "Shortened to fit WhatsApp", 1),
    ("Build Verbatim Digest", "out = out.slice(0, 3900 - tail.length) + '...';", 0),
    # lap 2
    ("Gate Verdict", "const _ownerFlat = function (s) {", 1),
    ("Gate Verdict", "|preload|evidence)\\s+(?:just |already |only |actually |apparently |first )?", 1),
    ("Answer Merge", "while an MDS event is running, this call", 1),
    # lap 3
    ("Answer Seed", "ALWAYS its START TIME", 1),
]


def verify(nodes):
    idx = {n["name"]: n for n in nodes}
    bad = []
    for name, needle, want in POST:
        got = (idx[name].get("parameters") or {}).get("jsCode", "").count(needle)
        if got != want:
            bad.append(f"{name}: {needle[:60]!r} expected {want}, got {got}")
    assert not bad, "POST-PUT ASSERTIONS FAILED:\n  " + "\n  ".join(bad)
    print(f"  post-PUT assertions OK ({len(POST)} conditions)")


def main():
    assert STAGING_ID != PROD_ID
    # --from <snapshot.json>: build the final graph from a PRISTINE pre-fixwave4 snapshot instead of
    # from the live GET. Needed because this wave shipped in two laps: lap 2's anchors sit on text
    # lap 1 introduced, so a second run against the already-lap-1 graph would have to LOOSEN lap 1's
    # anchors to survive, and an anchor is never loosened. Building from the snapshot keeps every
    # anchor asserted count==1 and still writes ONE PUT and ONE bounce. The result is byte-identical
    # to a single clean run, which is what the dry run against the same snapshot proves.
    src = None
    if "--from" in sys.argv:
        src = sys.argv[sys.argv.index("--from") + 1]
    if src:
        wf = json.load(open(src))
        live = api("GET", f"/workflows/{STAGING_ID}")
        print(f"SOURCE       {src}  (snapshot versionId {wf.get('versionId')})")
        print(f"GET staging  versionId={live.get('versionId')}  nodes={len(live['nodes'])}  active={live.get('active')}")
        assert len(wf["nodes"]) == len(live["nodes"]), "snapshot/live node count differs — STOP"
        wf["name"] = live["name"]
        wf["connections"] = live["connections"]
        wf["settings"] = live.get("settings") or {}
    else:
        wf = api("GET", f"/workflows/{STAGING_ID}")
        print(f"GET staging  versionId={wf.get('versionId')}  nodes={len(wf['nodes'])}  active={wf.get('active')}")

    nodes = transform(wf["nodes"])
    verify(nodes)   # assert the in-memory graph BEFORE it is written

    payload = {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}}
    put = api("PUT", f"/workflows/{STAGING_ID}", payload)
    assert put.get("id") == STAGING_ID, f"PUT failed: {json.dumps(put)[:400]}"
    print(f"PUT ok       versionId={put.get('versionId')}")

    # edit -> ONE deactivate+activate bounce (never deactivate first as a separate step)
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    act = api("POST", f"/workflows/{STAGING_ID}/activate")
    print(f"bounced      active={act.get('active')}")

    back = api("GET", f"/workflows/{STAGING_ID}")
    verify(back["nodes"])
    print(f"re-GET ok    versionId={back.get('versionId')}  active={back.get('active')}")
    print("\nFIXWAVE 4 APPLIED — staging only. Prod", PROD_ID, "untouched.")


if __name__ == "__main__":
    main()
