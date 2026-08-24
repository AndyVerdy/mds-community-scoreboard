#!/usr/bin/env python3
"""Fixwave 6 — 2026-08-23. The six graded failures left after wave 5, on STAGING
(bqHstPDi84uOhTCJ). PROD 12wj6h1TWqb0d4Dq is never touched and never promoted.

Evidence: .superpowers/sdd/2026-08-22-finder/eval/pairs_rerun5.json + grade_r5_all.json, the live
executions of the 09:4xZ run, and live PostgREST / find-endpoint probes taken today. Every root
cause below was read off a live payload, never inferred.

  A. CONTINUITY IS STATE, AND IT WAS NEVER RECORDED (B5037, A4057, B5017 — three symptoms, one
     disease). Nothing carries the FACTS a turn resolved into the next turn. The conversation text
     is there, but the model re-derives instead of narrowing, and every deterministic check in Gate
     Verdict only ever sees THIS turn's evidence:
       · B5037 gave "17 resellers registered" and one turn later pasted 100/22 from event_who,
         calling 22 "the reseller-relevant overlap". Wave 5's own event_who counts stamp (shipped
         for B5009) is what put those numbers in front of her — the regression 9 -> 5 is that stamp
         firing on a thread whose number was already settled.
       · A4057 dropped Nacho Nachelis and Jan Krapp, both named by her OWN previous turn, because
         member_match's p_city is exact and did not return them again. Wave 5's PLACE COVERAGE
         check could not save it: it reads evRaw, and last turn's rows are not in evRaw.
       · B5017 promised the asker's own record and delivered a Summit registration line, because
         the turn stayed bound to the event lane the thread started in.
     FIX, in code, in three places:
       1. Format Reply records `turn_state` on every turn — the where/total/gate of the last
          filtered people-search, and the people this reply ACTUALLY NAMED with the place each
          record carries. Privacy: only what she already said is recorded, so replaying it can
          never widen a disclosure.
       2. Prep Context carries it forward on the same `plan` channel prev_plan/prev_offer ride.
       3. Answer Seed replays it into the PRELOAD — which is also what Answer Parse puts into
          evidence_full, so PLACE COVERAGE finally sees the rows it was written for.
     Plus: the event_who stamp now names the thread's own number and forbids re-labelling
     matched_total as the count of a group discussed earlier; and Plan Request routes a
     self-profile ask ("tell me what you know about me", anywhere in the message, not anchored)
     straight to member_dossier so the record is in the evidence whatever lane the thread was in.

  B. HONEST COUNTS AND NO INTERNALS NARRATION (B5025, and B5017's "The event view I pulled").
     "I pulled 20" while listing 15 is wave 5's own video_search stamp being obeyed literally: it
     told her the call returned 20 and that 20 is the tool's maximum. Reworded: state the number
     you LIST, say "showing X of N" when you list fewer, and say nothing about pulls, batches or
     per-call maximums. Plus a deterministic COUNT HONESTY check — the stated delivered-count and
     the rendered bullet count must agree — and the INTERNALS narration list widened by SHAPE (a
     first-person retrieval verb, a relative-clause "the X I pulled", retrieval-budget talk),
     never by another literal string. Swept over 219 graded answers: narration fires 8 times, all
     of them real narration; COUNT HONESTY fires exactly once, on the defect.
     And the "access-restricted title" that still printed the title and the link: wave 5 turned the
     flag off and left an access_note EXPLAINING why — she paraphrased the note. A row this member
     can see now carries no restriction field and no note at all; there is nothing left to
     paraphrase. (call_type decides what a Mogul Call is, not the title: no title filter is added.)

  C. RECENCY IS NOT RELEVANCE (A4018). She answered "what's your most recent date for facebook
     posts" from an engagement-ranked payload. Live ground truth re-verified today against
     digest.content_items: newest fb_post is 2026-08-22T15:14:27Z, Michael Patron (then 08-22
     03:58 Jonathan Jesper, 08-22 03:49 Duncan Brown, then Alex Mills 08-21). No new RPC is
     needed: content_search with NO terms returns newest-first (probed today, v1 and v2). So Plan
     Request detects the freshness shape deterministically and sends the ZEROTH FETCH with no
     terms, and Answer Seed computes the max(occurred_at) per source IN CODE and hands her the
     line. The model is never asked to spot the maximum. Detector swept over all 152 distinct
     graded questions: it fires on A4018 and nothing else.

  D. THE FALSE UNLOCK PROMISE (B5038, and B5037's tail). "That list only opens up once your own
     Summit registration is confirmed on our end" is a promise about what a status change would
     open. More than one gate can be shut at once and the reply is told only one of them, so the
     promise is unkeepable by construction. Two edits: a find result that withheld names now
     carries a deterministic note forbidding any such promise, and a Gate Verdict check catches the
     shape anyway (the sanctioned "want me to flag/verify it with the MDS team" offer is exempt).
     The endpoint half — /api/olivia/find reporting only the FIRST active gate — is staged on a
     local branch in mds-digest-web and is NOT pushed: that repo deploys to prod on push.

Eight nodes, ONE PUT, ONE deactivate->activate bounce, re-GET + assert.
Every anchor is asserted count == N and NEVER loosened: a miss means the node drifted -> STOP.

  python3 scripts/olivia_loop/apply_fixwave6_2026-08-23.py [--from <snapshot.json>] [--dry]
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
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code)
        tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED for {label}:\n{chk.stderr}"
    print(f"  node --check OK ({label})")


def one(hay, needle, label, n=1):
    """Anchor must appear EXACTLY n times. A miss => the node drifted; STOP, never loosen."""
    got = hay.count(needle)
    assert got == n, f"ANCHOR DRIFT — {label}: expected {n} occurrence(s), found {got}"


def sub(hay, old, new, label, n=1):
    one(hay, old, label, n)
    return hay.replace(old, new, n)


# ═══════════ 1 · Format Reply — record what this turn resolved (A, the root) ═══════════

FR_ANCHOR = ("return [{ json: { to: to, reply: text, interactive: interactive, followup_interactive: "
             "followupInteractive, image_post_id: imagePostId, send_file_key: sendFileKey, "
             "mark_welcome_phone: markPhone, sources_used: sourcesUsed, pending_offer: pendingOffer } }];")

FR_NEW = r"""// CONTINUITY IS STATE (fixwave 6, 2026-08-23). Three of the six graded failures are one disease:
// the NEXT turn throws away what this turn just established. B5037 abandoned the thread's own "17
// resellers" and pasted 22 from a different search one turn later. A4057 dropped Nacho Nachelis and
// Jan Krapp — both named in the immediately preceding reply — because member_match's p_city is an
// exact filter and did not return them again. B5017 promised the asker's own record and delivered a
// registration line. The conversation TEXT is already in the prompt and it is not enough: the model
// re-derives instead of narrowing, and every deterministic check in Gate Verdict only ever sees
// THIS turn's evidence, so none of them can notice a contradiction with the last one. So the facts
// a turn actually resolved are recorded HERE, on the turn, on the same `plan` channel pending_offer
// already rides (Save Conversation -> olivia_messages.plan -> Prep Context -> Answer Seed).
// PRIVACY: only what this reply ALREADY SAID is recorded. A person the gate withheld is never
// written down, so replaying the block on the next turn can never widen a disclosure.
let turnState = null;
try {
  const ev = $('Answer Parse').isExecuted ? String($('Answer Parse').first().json.evidence_full || '') : '';
  const said = String(text || '');
  if (ev && said) {
    const st = {};
    // (a) THE LAST FILTERED PEOPLE-SEARCH. #108's follow-up contract is "wrap where_echo from the
    // last result" — but where_echo lived and died inside one turn, so a follow-up had nothing to
    // wrap and re-derived a fresh set instead. Recorded with its true total and the gate it
    // reported, because the number is exactly what B5037 threw away.
    const wk = '"where_echo":';
    const wi = ev.lastIndexOf(wk);
    if (wi !== -1) {
      const from = wi + wk.length;
      let depth = 0, end = -1;
      for (let i = from; i < ev.length && i < from + 4000; i++) {
        const c = ev.charAt(i);
        if (c === '{') { depth += 1; }
        else if (c === '}') { depth -= 1; if (depth === 0) { end = i + 1; break; } }
        else if (depth === 0 && c !== ' ' && c !== '\\') { break; }   // null / not an object
      }
      let where = null;
      if (end > 0) { try { where = JSON.parse(ev.slice(from, end)); } catch (e) { where = null; } }
      if (where && typeof where === 'object') {
        const around = ev.slice(Math.max(0, wi - 1500), wi + 2500);
        const tm = around.match(/"total"\s*:\s*(\d{1,6})/);
        const dm = around.match(/"disclosure"\s*:\s*"([a-z_]+)"/);
        st.find = { where: where, total: tm ? Number(tm[1]) : null, gate: dm ? dm[1] : null };
      }
    }
    // (b) THE PEOPLE THIS REPLY NAMED, each with the place their own record carries — the exact
    // rows A4057's follow-up needed and did not have. A bare `name` key is chats/events/partners
    // too, so it only counts inside a find people row (which always carries `reasons`).
    const norm = function (s) {
      return String(s).toLowerCase().replace(/[^a-z0-9\u00c0-\u017f]+/g, ' ').trim();
    };
    const saidN = ' ' + norm(said) + ' ';
    const inReply = function (n) {
      const t = norm(n).split(' ').filter(function (w) { return w.length > 1; });
      if (!t.length) { return false; }
      if (saidN.indexOf(' ' + t.join(' ') + ' ') !== -1) { return true; }
      return t.length >= 2 && saidN.indexOf(' ' + t[0] + ' ') !== -1
        && saidN.indexOf(' ' + t[t.length - 1] + ' ') !== -1;
    };
    const people = [];
    const RE_N = /\\?"(full_name|display_name|member_name|name)\\?"\s*:\s*\\?"([A-Z][^"\\]{2,59})/g;
    let nm = null, guard = 0;
    while ((nm = RE_N.exec(ev)) !== null && guard++ < 500 && people.length < 14) {
      const who = String(nm[2]).trim();
      // The window must stop at the NEXT person or a compact array of rows —
      // [{"full_name":…,"city":…},{…}] is exactly the live shape — bleeds the following
      // record's city into this one's.
      let stopAt = ev.length;
      const NX = /\\?"(?:full_name|display_name|member_name|name)\\?"\s*:/g;
      NX.lastIndex = nm.index + 1;
      const nx = NX.exec(ev);
      if (nx) { stopAt = nx.index; }
      const seg = ev.slice(nm.index, Math.min(stopAt, nm.index + 900));
      if (nm[1] === 'name' && (seg.indexOf('"reasons"') === -1 || who.indexOf(' ') === -1)) { continue; }
      if (!inReply(who)) { continue; }
      if (people.some(function (q) { return norm(q.full_name) === norm(who); })) { continue; }
      const f = function (k) {
        const m = seg.match(new RegExp('\\\\?"' + k + '\\\\?"\\s*:\\s*\\\\?"([^"\\\\]{2,60})'));
        return m ? m[1] : null;
      };
      const lk = seg.match(/https?:\/\/(?:www\.)?facebook\.com\/[^\s"\\)\]]+/);
      const row = { full_name: who };
      ['city', 'state', 'country'].forEach(function (k) { const v = f(k); if (v) { row[k] = v; } });
      if (lk) { row.link = lk[0]; }
      people.push(row);
    }
    if (people.length) { st.people = people; }
    if (st.find || st.people) {
      // bounded: this rides on a database row alongside the plan, never unbounded
      if (JSON.stringify(st).length > 3000 && st.people) { st.people = st.people.slice(0, 8); }
      turnState = st;
    }
  }
} catch (e) { turnState = null; }
return [{ json: { to: to, reply: text, interactive: interactive, followup_interactive: followupInteractive, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone, sources_used: sourcesUsed, pending_offer: pendingOffer, turn_state: turnState } }];"""


def patch_format_reply(code):
    return sub(code, FR_ANCHOR, FR_NEW, "Format Reply / return")


# ═══════════ 2 · Save Conversation — persist turn_state on the olivia row ═══════════

SC_ANCHOR = ("try { const po = src.pending_offer; if (po) { plan = Object.assign(plan || {}, "
             "{ pending_offer: po }); } } catch (e) {}")
SC_NEW = (SC_ANCHOR
          + " try { const ts = src.turn_state; if (ts) { plan = Object.assign(plan || {}, "
            "{ turn_state: ts }); } } catch (e) {}")


# ═══════════ 3 · Prep Context — carry it forward ═══════════

PC_1_OLD = "let prev_offer = null;"
PC_1_NEW = ("let prev_offer = null;\n"
            "// #fixwave6 CONTINUITY: the facts the previous turn RESOLVED (its people-search and the\n"
            "// people it actually named), recorded by Format Reply on that turn. Same NO_REPLAY guard,\n"
            "// same channel as prev_plan/prev_offer — a follow-up narrows this set instead of\n"
            "// re-deriving one, and Answer Seed replays it into the evidence.\n"
            "let prev_state = null;")

PC_2_OLD = ("      && NO_REPLAY.indexOf(String(lastOlivia.route || '')) === -1) { prev_offer = pl.pending_offer; }")
PC_2_NEW = (PC_2_OLD + "\n"
            "  if (pl && typeof pl === 'object' && pl.turn_state\n"
            "      && NO_REPLAY.indexOf(String(lastOlivia.route || '')) === -1) { prev_state = pl.turn_state; }")

PC_3_OLD = ("if (quoted_plan) { prev_plan = quoted_plan; if (quoted_plan.pending_offer) "
            "{ prev_offer = quoted_plan.pending_offer; } }")
PC_3_NEW = ("if (quoted_plan) { prev_plan = quoted_plan; if (quoted_plan.pending_offer) "
            "{ prev_offer = quoted_plan.pending_offer; } if (quoted_plan.turn_state) "
            "{ prev_state = quoted_plan.turn_state; } }")

PC_4_OLD = "prev_plan: prev_plan, prev_offer: prev_offer,"
PC_4_NEW = "prev_plan: prev_plan, prev_offer: prev_offer, prev_state: prev_state,"


def patch_prep_context(code):
    code = sub(code, PC_1_OLD, PC_1_NEW, "Prep Context / prev_state decl")
    code = sub(code, PC_2_OLD, PC_2_NEW, "Prep Context / read turn_state")
    code = sub(code, PC_3_OLD, PC_3_NEW, "Prep Context / quoted plan")
    code = sub(code, PC_4_OLD, PC_4_NEW, "Prep Context / return")
    return code


# ═══════════ 4 · Plan Request — freshness, self-profile, prev_state pass-through ═══════════

PR_FLAGS_ANCHOR = ("const STOPW = new Set(['the', 'and', 'new', 'what', 'chat', 'mds', 'about', "
                   "'any', 'all', 'sentiment', 'consensus', 'opinion', 'thoughts']);")

PR_FLAGS_NEW = r"""// A4018 — RECENCY IS NOT RELEVANCE (fixwave 6, 2026-08-23). "what's your most recent date for
// facebook posts" was answered off an engagement-ranked payload: she named Alex Mills, 21 Aug, while
// digest.content_items' newest fb_post (read live today) is 2026-08-22T15:14:27Z, Michael Patron —
// with two more 22 Aug posts above the Alex Mills row. A freshness question is not a topic question
// and can never be answered by a ranking: it has to be answered by SORTING ON TIME. No new RPC is
// needed — content_search with NO terms returns newest-first (probed live today on v1 and v2) — so
// this only has to recognise the shape and steer the zeroth fetch. Deliberately narrow, and it has
// to be: it must never swallow "what are the latest videos" (a library question) or "what's the
// latest on tariffs" (a topic). Three conditions together: a recency word, a data/date word, and
// NOTHING left in the message except source words. Swept over all 152 distinct graded questions —
// it fires on A4018 and on nothing else.
const FRESH_SRC = { facebook: 'fb_post', fb: 'fb_post', post: 'fb_post', posts: 'fb_post', group: 'fb_post',
  comment: 'fb_comment', comments: 'fb_comment', chat: 'wa_message', chats: 'wa_message',
  whatsapp: 'wa_message', message: 'wa_message', messages: 'wa_message', digest: 'wa_digest',
  digests: 'wa_digest', call: 'call_transcript', calls: 'call_transcript',
  transcript: 'call_transcript', transcripts: 'call_transcript' };
const FRESH_STOP = ['what', 'whats', 'is', 'are', 'the', 'your', 'you', 'do', 'does', 'done', 'have',
  'has', 'on', 'for', 'in', 'of', 'me', 'my', 'a', 'an', 'how', 'when', 'most', 'recent', 'latest',
  'newest', 'last', 'up', 'to', 'date', 'dates', 'data', 'got', 'go', 'back', 'far', 'and', 'or',
  'there', 'can', 'tell', 'give', 'know', 'about', 'it', 'with', 'from', 'see', 'hold', 'held',
  'still', 'only', 'been', 'sync', 'synced', 'syncing', 'updated', 'update', 'refresh', 'refreshed',
  'current', 'coverage', 'yet', 'right', 'now', 'today', 'information', 'info', 'anything', 'item',
  'items', 'entry', 'entries', 'record', 'records', 'please', 'thanks', 's', 't'];
const freshSources = (function () {
  const t = String(rawText || '').toLowerCase();
  if (!/\b(?:most recent|latest|newest|how recent|how current|how up[- ]?to[- ]?date|how fresh|how old|how far back|last)\b/.test(t)) { return null; }
  if (!/\b(?:date|dates|data|sync(?:ed|ing)?|updated?|up[- ]?to[- ]?date|refresh(?:ed)?|coverage)\b/.test(t)) { return null; }
  const toks = t.replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter(Boolean)
    .filter(function (w) { return FRESH_STOP.indexOf(w) === -1; });
  if (!toks.length) { return null; }
  const src = [];
  for (let i = 0; i < toks.length; i++) {
    const s = FRESH_SRC[toks[i]];
    if (!s) { return null; }                       // a real topic word — not a freshness question
    if (src.indexOf(s) === -1) { src.push(s); }
  }
  return src;
})();
// B5017 — "I'm Lisa Harrington. Tell me what you know about me" promised the asker's own record and
// delivered "not registered for Singapore" plus "just ask me directly". The turn stayed bound to the
// event lane the thread had started in, so the dossier was never fetched and the answer had nothing
// else to give. The existing profile branch's genericCard regex is anchored at ^, so any prefix (an
// identity claim, a greeting, a correction) walks straight past it. This one is not anchored, does
// not depend on the router's intent, and makes the record part of the deterministic evidence
// whatever lane the thread is in. Swept over all 152 distinct graded questions: two fires, both of
// them a member asking what is held on them.
const selfProfileAsk = /\b(?:know|have|hold|got|tell)\b[^.?!]{0,40}\babout me\b/i.test(rawText)
  || /\bwhat (?:do|have) you (?:know|have|got|hold)\b[^.?!]{0,25}\bon me\b/i.test(rawText)
  || /\bwhat(?:'|\u2019)?s on my (?:record|profile|file)\b/i.test(rawText)
  || /\b(?:tell|show) me (?:everything |all )?(?:you know|about myself|my (?:profile|record|file))\b/i.test(rawText);
""" + PR_FLAGS_ANCHOR

PR_BRANCH_ANCHOR = "} else if (offerBind) {"
PR_BRANCH_NEW = r"""} else if (freshSources) {
  // The zeroth fetch becomes a TIME-SORTED pull: no terms, no embedding, so content_search_v2
  // returns the newest rows for the source the member named. Answer Seed then computes the newest
  // date per source IN CODE — the model is never asked to spot a maximum in a list.
  route = 'llm'; planPeriod = 'freshness'; intent = 'question';
  op = 'content_search';
  params = { p_phone: mem.to, p_terms: [], p_sources: freshSources, p_limit: 3 };
  raw_op = 'content_search';
  raw_params = { p_phone: mem.to, p_terms: [], p_sources: freshSources, p_limit: 6, no_embed: true };
} else if (selfProfileAsk) {
  // Mirrors the profile lane's genericCard branch exactly — same op/params shape, same dossier —
  // but reachable from inside a thread that started somewhere else.
  route = 'llm'; planPeriod = 'dossier'; intent = 'profile';
  raw_op = 'member_dossier';
  params = { p_phone: mem.to, p_source: 'application', p_limit: 5 };
  raw_params = { p_phone: mem.to };
} else if (offerBind) {"""

PR_RET_OLD = "chat_links: chatLinks, links_loaded: linkRows.length } }];"
PR_RET_NEW = ("chat_links: chatLinks, links_loaded: linkRows.length, "
              "prev_state: ctx.prev_state || null, self_profile: !!selfProfileAsk, "
              "fresh_sources: freshSources } }];")


def patch_plan_request(code):
    code = sub(code, PR_FLAGS_ANCHOR, PR_FLAGS_NEW, "Plan Request / flags")
    code = sub(code, PR_BRANCH_ANCHOR, PR_BRANCH_NEW, "Plan Request / cascade")
    code = sub(code, PR_RET_OLD, PR_RET_NEW, "Plan Request / returns", 2)
    return code


# ═══════════ 5 · Answer Seed — replay continuity, compute freshness, drop the access note ═══════

AS_RESTRICT_OLD = """  if (out && out.is_restricted === true
      && String(out.description_snippet || '').indexOf('[RESTRICTED VIDEO') !== 0) {
    out.is_restricted = false;
    out.access_note = 'Access-restricted in the library, but THIS member holds access to it: it is '
      + 'available to them. Recommend it normally and never call it restricted to them.';
  }"""
AS_RESTRICT_NEW = """  // fixwave 6 (B5025): wave 5 turned the flag off and left an access_note EXPLAINING why — and
  // she paraphrased the note straight into the reply ("access-restricted title, but you hold
  // access") and then printed that title and its link anyway. A row this member can actually see
  // needs no access vocabulary at all, so the field and the note are simply removed. There is
  // nothing left to paraphrase.
  if (out && out.is_restricted === true
      && String(out.description_snippet || '').indexOf('[RESTRICTED VIDEO') !== 0) {
    delete out.is_restricted;
    delete out.access_note;
  }"""

AS_CONT_ANCHOR = "let preload = offer_ctx;"
AS_CONT_NEW = r"""// CONTINUITY — REPLAY WHAT THE PREVIOUS TURN RESOLVED (fixwave 6, 2026-08-23). Format Reply
// recorded it on that turn; this renders it back as EVIDENCE. Two things follow from putting it in
// `preload` rather than in a loose prompt line: the model gets the rows it needs to narrow instead
// of re-deriving, and Answer Parse copies preload into evidence_full — so Gate Verdict's PLACE
// COVERAGE check, which reads evRaw and therefore could never see last turn's rows, finally can.
// Nothing here was withheld from this member: Format Reply only records what she already said.
let cont_ctx = '';
try {
  const ps = plan.prev_state;
  if (ps && (ps.find || (ps.people && ps.people.length))) {
    const bits = ['CONTINUITY — WHAT YOUR PREVIOUS TURN ALREADY RESOLVED FOR THIS MEMBER (recorded '
      + 'on that turn; every line below is something you have already told them):'];
    if (ps.people && ps.people.length) {
      bits.push('· People you already named, each with the place their own record carries: '
        + JSON.stringify(ps.people.slice(0, 14)));
    }
    if (ps.find) {
      bits.push('· Your last filtered people-search: where = ' + JSON.stringify(ps.find.where)
        + (ps.find.total != null ? ' · true total = ' + ps.find.total : '')
        + (ps.find.gate ? ' · gate = ' + ps.find.gate : '') + '.');
    }
    bits.push('Treat this message as a FOLLOW-UP unless it plainly changes the subject. NARROW the '
      + 'set above rather than re-deriving one: for find, call it again as {all:[<the where above>, '
      + '<the new condition>]} and answer from THAT result. Everyone listed above is already '
      + 'established in this conversation, so if their own record satisfies what the member just '
      + 'asked for they BELONG in this answer - leaving one out contradicts your own last message, '
      + 'and a village, suburb or district of a place counts as that place. A number this thread '
      + 'has already given still stands: never replace it with a count from a different search, and '
      + 'if a new number is about a different set, say plainly which is which.');
    cont_ctx = bits.join(NL);
  }
} catch (e) {}
let preload = [cont_ctx, offer_ctx].filter(Boolean).join(NL + NL);"""

AS_CONT2_OLD = "  preload = (offer_ctx ? offer_ctx + NL + NL : '') + parts.join(NL);"
AS_CONT2_NEW = ("  preload = [cont_ctx, offer_ctx].filter(Boolean)\n"
                "    .map(function (s) { return s + NL + NL; }).join('') + parts.join(NL);")

AS_FINAL_ANCHOR = "const finalUser = askerLine + (preload"
AS_FINAL_NEW = r"""// A4018 (fixwave 6). The freshness ANSWER is computed here, in code, from the time-sorted zeroth
// fetch Plan Request just steered — max(occurred_at) per source. She is handed the date; she is
// never asked to find it in a list, which is the step that failed.
let freshNote = '';
try {
  if (plan.period === 'freshness') {
    const FLABEL = { fb_post: 'Facebook posts', fb_comment: 'Facebook comments',
      wa_message: 'the WhatsApp chats', wa_digest: 'the chat digests',
      call_transcript: 'call transcripts' };
    const best = {};
    preRaw.concat(preDig).forEach(function (r) {
      if (!r || !r.occurred_at || !r.source) { return; }
      const s = String(r.source);
      if (!best[s] || String(r.occurred_at) > String(best[s].occurred_at)) { best[s] = r; }
    });
    const flines = Object.keys(best).map(function (s) {
      const r = best[s];
      const who = (r.meta && (r.meta.author || r.meta.author_name)) || null;
      return '\u00b7 ' + (FLABEL[s] || s) + ' \u2014 newest item on file: '
        + String(r.occurred_at).slice(0, 10) + (who ? ', by ' + who : '')
        + (r.body ? ' (\u201c' + String(r.body).replace(/\s+/g, ' ').slice(0, 70) + '\u2026\u201d)' : '');
    });
    if (flines.length) {
      freshNote = 'FRESHNESS ASK \u2014 the member is asking how recent your data is, not about a '
        + 'topic. The lines below were computed by sorting a fresh pull on TIME; they are the '
        + 'answer:' + NL + flines.join(NL) + NL + 'Give that date (and the author, if one is shown) '
        + 'exactly as it stands, and keep the honest caveat that syncing runs periodically rather '
        + 'than live. Do not answer this from any other search and do not go looking for a newer '
        + 'one: a topic or engagement ranking cannot tell you what is newest.' + NL + NL;
    }
  }
} catch (e) {}
// B5017 (fixwave 6). "Tell me what you know about me" got a Summit-registration line and "just ask
// me directly" — she promised the record and then deferred it. Plan Request has put the dossier in
// the preload; this says what the answer owes.
let selfNote = '';
try {
  if (plan.self_profile) {
    selfNote = 'SELF-PROFILE ASK \u2014 the member is asking what you hold on THEM. Their own record '
      + 'is in the preloaded evidence below: answer from it, with the concrete facts on file - their '
      + 'name and status, when they joined, where they are based, what they sell, the chats they are '
      + 'in, the events on their record, what they have been active on lately. Registration status '
      + 'for any single event is at most ONE line and is never the whole answer. Never close by '
      + 'telling them to ask you for it: they just did ask.' + NL + NL;
  }
} catch (e) {}
const finalUser = askerLine + freshNote + selfNote + (preload"""


def patch_answer_seed(code):
    code = sub(code, AS_RESTRICT_OLD, AS_RESTRICT_NEW, "Answer Seed / restrict note")
    code = sub(code, AS_CONT_ANCHOR, AS_CONT_NEW, "Answer Seed / preload init")
    code = sub(code, AS_CONT2_OLD, AS_CONT2_NEW, "Answer Seed / preload compose")
    code = sub(code, AS_FINAL_ANCHOR, AS_FINAL_NEW, "Answer Seed / finalUser")
    return code


# ═══════════ 6 · Answer Merge — the stamps that caused the regressions ═══════════

AM_RESTRICT_OLD = """    if (row && row.is_restricted === true
        && String(row.description_snippet || '').indexOf('[RESTRICTED VIDEO') !== 0) {
      row.is_restricted = false;
      row.access_note = 'Access-restricted in the library, but THIS member holds access to it: it is '
        + 'available to them. Recommend it normally and never call it restricted to them.';
    }"""
AM_RESTRICT_NEW = """    // fixwave 6 (B5025): wave 5 turned the flag off and left an access_note EXPLAINING why. She
    // paraphrased it — "(access-restricted title, but you hold access)" — and printed the title and
    // the link underneath it anyway. A row this member can see needs no access vocabulary at all,
    // so the field and the note are removed outright: there is nothing left to paraphrase.
    if (row && row.is_restricted === true
        && String(row.description_snippet || '').indexOf('[RESTRICTED VIDEO') !== 0) {
      delete row.is_restricted;
      delete row.access_note;
    }"""

AM_EVENTWHO_OLD = """        + '. Give the numbers, say plainly why the names are not shown, then make the offer. A '
        + 'count-free refusal is not the answer.';"""
AM_EVENTWHO_NEW = r"""        + '. Give the numbers, say plainly why the names are not shown, then make the offer. A '
        + 'count-free refusal is not the answer.'
        // fixwave 6 (B5037, the 9 -> 5 regression THIS stamp caused). One turn after she told this
        // member "17 resellers are registered", the stamp put 100 and 22 in front of her and she
        // pasted them over it, calling 22 "the reseller-relevant overlap". They count different
        // sets. The thread's own number is state now, so name it here rather than hoping.
        + (function () {
          try {
            const _ps = ($('Plan Request').first().json || {}).prev_state;
            if (_ps && _ps.find && _ps.find.total != null) {
              return ' NOTE: this conversation has ALREADY established a different number from a '
                + 'different search \u2014 ' + _ps.find.total + ' for '
                + JSON.stringify(_ps.find.where) + '. That number stands, it is NOT total_going and '
                + 'it is NOT matched_total, and you must not quietly replace it.';
            }
          } catch (e) {}
          return '';
        })()
        + ' matched_total is the overlap with THIS asker\u2019s own focus areas and nothing else: '
        + 'never re-label it as the count of a group named earlier in this conversation \u2014 not a '
        + 'kind of seller, not a chat, not a niche, not a country.';"""

AM_VIDEO_OLD = """      body = body + NL + 'MILLIE — DETERMINISTIC NOTE: the member asked for a LIST, so say HOW MANY '
        + 'you are giving them. This call returned ' + r.length + ' video' + (r.length === 1 ? '' : 's')
        + (r.length >= 20 ? ', and 20 is this tool\\'s maximum per call, so there are likely more behind it' : '')
        + '. An unnumbered list reads as "everything there is", and this one is not.';"""
AM_VIDEO_NEW = r"""      // fixwave 6 (B5025): the wave-5 wording of this stamp is what produced "I pulled 20" above a
      // list of 15, and "that's this search's max per pull" — it handed her a number and a cap and
      // she reported both. The number a reply states must be the number the reply LISTS, and the
      // machinery is never the member's business.
      body = body + NL + 'MILLIE — DETERMINISTIC NOTE: the member asked for a LIST, so say how many '
        + 'you are giving them — and the number you SAY must be the number you actually LIST. This '
        + 'search returned ' + r.length + ' item' + (r.length === 1 ? '' : 's') + ': if you list all '
        + 'of them say ' + r.length + ', and if you leave any out say "showing X of ' + r.length
        + '" with X the number you really wrote out. Never state a count you did not list. Say '
        + 'NOTHING about the pull, the search, the batch or any per-call maximum — that is machinery, '
        + 'not an answer'
        + (r.length >= 20 ? '; "there may be more in the library" is the member-facing way to say it' : '')
        + '. An unnumbered list reads as "everything there is", and this one is not.';"""

AM_FIND_OLD = """          + 'from THAT result only. Whatever gate the new result reports is the gate: state the '
          + 'reason it gives, and never promise the member that some other status would open the '
          + 'roster for them.';
      }
    }"""
AM_FIND_NEW = r"""          + 'from THAT result only. Whatever gate the new result reports is the gate: state the '
          + 'reason it gives, and never promise the member that some other status would open the '
          + 'roster for them.';
      }
      // fixwave 6 (B5038, and B5037's tail). "That list only opens up once your own Summit
      // registration is confirmed on our end" is a promise about what a status change would open.
      // The endpoint reports only the FIRST gate that fired, so more than one rule can be holding
      // the same list shut while the reply is told about one of them — which makes the promise
      // unkeepable by construction, whichever gate she happens to have been handed. This fires on
      // ANY find result that withheld names, so the shape cannot come back through another gate.
      if (r.disclosure && String(r.disclosure) !== 'green' && Number(r.shown || 0) === 0) {
        body = body + NL + 'MILLIE — DETERMINISTIC NOTE: names are withheld on this result. Give the '
          + 'true total and the reason this result itself reports, in plain member words, and stop '
          + 'there. Do NOT tell them that registering for an event, joining a chat, confirming a '
          + 'status or anything else would open the list: more than one rule can be holding it shut '
          + 'and you are only told about one of them, so any such sentence is a promise you cannot '
          + 'keep. Offering to flag it with the MDS team is fine; saying what that would unlock is '
          + 'not.';
      }
    }"""


def patch_answer_merge(code):
    code = sub(code, AM_RESTRICT_OLD, AM_RESTRICT_NEW, "Answer Merge / restrictFix")
    code = sub(code, AM_EVENTWHO_OLD, AM_EVENTWHO_NEW, "Answer Merge / event_who stamp")
    code = sub(code, AM_VIDEO_OLD, AM_VIDEO_NEW, "Answer Merge / video list stamp")
    code = sub(code, AM_FIND_OLD, AM_FIND_NEW, "Answer Merge / find stamp")
    return code


# ═══════════ 7 · Gate Verdict — narration by shape, count honesty, the false promise ═════════

GV_NARR_OLD = ("""    /\\b(?:that|this|the|those|these|both|my)\\s+(?:\\w+\\s+){0,2}"""
               """(?:quer(?:y|ies)|search(?:es)?|lookups?|tools?|preload(?:ed)?|evidence)\\b"""
               """[^.!?\\n]{0,50}\\b(?:instead|by mistake|not what you (?:need|asked|wanted)|"""
               """wrong (?:one|tool|result|event|thing))\\b/i
  ];""")
GV_NARR_NEW = ("""    /\\b(?:that|this|the|those|these|both|my)\\s+(?:\\w+\\s+){0,2}"""
               """(?:quer(?:y|ies)|search(?:es)?|lookups?|tools?|preload(?:ed)?|evidence)\\b"""
               """[^.!?\\n]{0,50}\\b(?:instead|by mistake|not what you (?:need|asked|wanted)|"""
               """wrong (?:one|tool|result|event|thing))\\b/i,
    // fixwave 6: widened by SHAPE, not by another literal string. Two phrasings walked past every
    // pattern above — "I pulled 20" (B5025) and "The event view I pulled confirms…" (B5017) — and
    // neither contains a noun from the retrieval list, because the retrieval word is the VERB. So
    // the verb is what is matched: first person doing a retrieval, or a relative clause hanging a
    // retrieval off any noun at all, or talk about the retrieval's own budget. Swept over 219
    // graded answers: 8 fires, every one of them a real piece of narration.
    /\\bI\\s+(?:just |only |already |also |first )?(?:pulled|ran|queried|fetched|scanned|grabbed|surfaced|loaded)\\b(?!\\s+(?:together|into|out|through|across|up on))/i,
    /\\b(?:the|this|that|these|those|my|your)\\s+(?:\\w+\\s+){0,3}I\\s+(?:just |only |already )?(?:pulled|ran|queried|fetched|searched|scanned|grabbed|loaded|checked|looked up)\\b/i,
    /\\bper\\s+(?:pull|call|query|request|batch)\\b/i,
    /\\bthis\\s+(?:search|query|lookup|pull|call|batch|view)(?:'|\\u2019)s\\b/i,
    /\\b(?:max(?:imum)?|cap|limit)\\b[^.!?\\n]{0,25}\\bper\\b[^.!?\\n]{0,15}\\b(?:pull|call|query|search|batch)\\b/i
  ];""")

GV_NEW_CHECKS = r"""// (8) THE NUMBER YOU STATE IS THE NUMBER YOU LIST (B5025 — "I pulled 20" above fifteen bullets).
// Both numbers are read out of the draft itself, so honesty here stops being something to remember
// and becomes something the send path checks. Only a DELIVERY claim counts ("here are N", "I found
// N", "showing N") — a population figure like "100 members are registered" is a different sentence
// and is deliberately not matched. An honest "showing 15 of 20" is accepted as-is.
try {
  if (_attempt0) {
    const BULLET = /^\s*(?:[\u2022\u2023\u25cf\u25aa\u00b7]|[-\u2013]\s|\d{1,2}[.)])\s*\S/;
    const _ls = answerText.split(/\n/);
    const bullets = _ls.filter(function (l) { return BULLET.test(l); }).length;
    if (bullets >= 3) {
      let head = answerText;
      for (let i = 0; i < _ls.length; i++) {
        if (BULLET.test(_ls[i])) { head = _ls.slice(0, i).join(' '); break; }
      }
      const honest = head.match(/\b(\d{1,3})\s*(?:of|out of)\s*(?:the\s*)?(\d{1,3})\b/);
      if (!(honest && Number(honest[1]) === bullets)) {
        const dm = head.match(/\b(?:here are|here\u2019s|here's|below are|these are|i pulled|i found|i\u2019ve got|i've got|i have|listing|showing|i\u2019m showing|i'm showing)\s+(?:the\s+|all\s+|you\s+)?(\d{1,3})\b/i);
        const claimed = dm ? Number(dm[1]) : 0;
        if (claimed >= 3 && claimed <= 200 && claimed !== bullets) {
          policyClaims.push('COUNT: your draft says "' + dm[0].trim() + '" and then lists ' + bullets
            + '. The number you state must be the number you actually write out. Either list all '
            + claimed + ', or say plainly that you are showing ' + bullets + ' of ' + claimed
            + '. Do not describe the search, the batch or any per-call limit while you fix it.');
        }
      }
    }
  }
} catch (e) {}

// (9) NEVER PROMISE THAT A STATUS CHANGE WOULD OPEN THE LIST (B5038, and B5037's closing line).
// "That list only opens up once your own Summit registration is confirmed on our end" is a promise
// about a future disclosure. The finder reports only the FIRST gate that fired, so a second rule
// can be holding the same list shut while the reply is told about one of them — the promise is
// unkeepable by construction, whichever gate she was handed. Clause-level, so one sanctioned offer
// in a sentence cannot shelter a promise bolted onto its tail; and the sanctioned offer itself —
// "want me to flag or verify that with the MDS team" — is exempt, because correcting a possibly
// wrong record is a real thing she can do.
try {
  if (_attempt0) {
    const UNLOCK = [
      /\b(?:list|names|roster|who'?s[- ]who|view|match(?:ed|es)? list)\b[^.!?\n]{0,60}\b(?:opens?(?: up)?|becomes? visible|unlocks?|gets? unlocked)\b/i,
      /\b(?:opens?(?: up)?|becomes? visible|unlocks?)\b[^.!?\n]{0,60}\bonce\b[^.!?\n]{0,60}\b(?:registration|registered|confirmed|sorted|on the list)\b/i,
      /\bif you (?:register|sign up|get registered|are registered|join)\b[^.!?\n]{0,80}\b(?:names?|list|roster|who'?s[- ]who|attendees?)\b/i,
      /\bonce (?:you'?re|your|that'?s|it'?s)\b[^.!?\n]{0,50}\b(?:registered|registration|confirmed|sorted)\b[^.!?\n]{0,80}\b(?:names?|list|roster|who'?s[- ]who|share|show|pull)\b/i
    ];
    const SANCTIONED = /\b(?:flag|verify|check|confirm)\b[^.!?\n]{0,50}\b(?:MDS team|the team|with the team)\b/i;
    const clauses = answerText.split(/[.!?\n]+|,\s+(?:and|but|so|then)\s+|;\s*/);
    const bad = [];
    clauses.forEach(function (c) {
      if (SANCTIONED.test(c)) { return; }
      if (UNLOCK.some(function (re) { return re.test(c); })) { bad.push(c.trim().slice(0, 90)); }
    });
    if (bad.length) {
      policyClaims.push('PROMISE: your draft tells the member what would open the list to them — "'
        + bad[0] + '". Never say that registering, joining, confirming a status or anything else '
        + 'would unlock names: more than one rule can be holding the same list shut and you are only '
        + 'told about one of them, so it is a promise you cannot keep. Give the true count, say '
        + 'plainly that you cannot show the names and the reason you were given, and stop. Offering '
        + 'to flag or verify it with the MDS team is fine — saying what that would unlock is not.');
    }
  }
} catch (e) {}

const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"""

GV_CLAIMS_ANCHOR = "const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"

# PLACE COVERAGE reads each person's place out of a 1200-char window that begins at their name —
# and a compact array of member rows is the live evidence shape, so the window ran straight into
# the NEXT record and borrowed its city. Replaying the A4057 draft with the continuity block in
# evidence, that named a third person (Nicosia) as missing from a Larnaca/Limassol list. The window
# now stops at the next person.
GV_WINDOW_OLD = """        const seg = evRaw.slice(pm.index, pm.index + 1200);"""
GV_WINDOW_NEW = """        // fixwave 6: stop at the NEXT person. The live evidence shape is a compact array of rows
        // ([{"full_name":…,"city":…},{…}]), so a fixed-length window borrows the following
        // record's city and puts somebody in a place their own record never mentions.
        let _stop = evRaw.length;
        const _NX = /\\\\?"(?:full_name|member_name|display_name)\\\\?"\\s*:/g;
        _NX.lastIndex = pm.index + 1;
        const _nx = _NX.exec(evRaw);
        if (_nx) { _stop = _nx.index; }
        const seg = evRaw.slice(pm.index, Math.min(_stop, pm.index + 1200));"""


def patch_gate_verdict(code):
    code = sub(code, GV_NARR_OLD, GV_NARR_NEW, "Gate Verdict / NARR")
    code = sub(code, GV_WINDOW_OLD, GV_WINDOW_NEW, "Gate Verdict / PLACE window")
    code = sub(code, GV_CLAIMS_ANCHOR, GV_NEW_CHECKS, "Gate Verdict / new checks")
    return code


# ═══════════════════════════════ driver ═══════════════════════════════

CODE_PATCHES = {
    "Format Reply": patch_format_reply,
    "Prep Context": patch_prep_context,
    "Plan Request": patch_plan_request,
    "Answer Seed": patch_answer_seed,
    "Answer Merge": patch_answer_merge,
    "Gate Verdict": patch_gate_verdict,
}

# post-PUT assertions: (node, substring, expected count)
ASSERTS = [
    ("Format Reply", "turn_state: turnState", 1),
    ("Format Reply", "CONTINUITY IS STATE (fixwave 6", 1),
    ("Prep Context", "prev_state: prev_state", 1),
    ("Plan Request", "planPeriod = 'freshness'", 1),
    ("Plan Request", "const selfProfileAsk =", 1),
    ("Plan Request", "prev_state: ctx.prev_state || null", 2),
    ("Answer Seed", "let cont_ctx = ''", 1),
    ("Answer Seed", "FRESHNESS ASK", 1),
    ("Answer Seed", "SELF-PROFILE ASK", 1),
    ("Answer Seed", "delete out.access_note", 1),
    ("Answer Seed", "access_note = 'Access-restricted", 0),
    ("Answer Merge", "delete row.access_note", 1),
    ("Answer Merge", "access_note = 'Access-restricted", 0),
    ("Answer Merge", "names are withheld on this result", 1),
    ("Answer Merge", "the number you SAY must be the number you actually LIST", 1),
    ("Answer Merge", "this tool\\'s maximum per call", 0),
    ("Answer Merge", "ALREADY established a different number", 1),
    ("Gate Verdict", "COUNT: your draft says", 1),
    ("Gate Verdict", "PROMISE: your draft tells the member", 1),
    ("Gate Verdict", "widened by SHAPE", 1),
    ("Gate Verdict", "stop at the NEXT person", 1),
    ("Format Reply", "stop at the NEXT person", 1),
]


def main():
    args = sys.argv[1:]
    dry = "--dry" in args
    src = None
    if "--from" in args:
        src = args[args.index("--from") + 1]

    if src:
        wf = json.load(open(src))
        print(f"source: snapshot {src}")
    else:
        wf = api("GET", f"/workflows/{STAGING_ID}")
        print(f"source: LIVE staging {STAGING_ID} · versionId {wf.get('versionId')}")
    assert wf.get("id") == STAGING_ID or src, "refusing: not the staging workflow"

    by_name = {n["name"]: n for n in wf["nodes"]}
    for name, fn in CODE_PATCHES.items():
        node = by_name.get(name)
        assert node, f"missing node {name}"
        code = node["parameters"].get("jsCode")
        assert isinstance(code, str), f"{name} has no jsCode"
        new = fn(code)
        assert new != code, f"{name}: patch produced no change"
        node_check(new, name)
        node["parameters"]["jsCode"] = new
        print(f"  patched {name}  ({len(code)} -> {len(new)} chars)")

    # Save Conversation is an httpRequest node — its body is an n8n expression, not jsCode.
    sc = by_name.get("Save Conversation")
    assert sc, "missing node Save Conversation"
    jb = sc["parameters"]["jsonBody"]
    sc["parameters"]["jsonBody"] = sub(jb, SC_ANCHOR, SC_NEW, "Save Conversation / plan")
    print("  patched Save Conversation (jsonBody expression)")

    if dry:
        out = "/private/tmp/claude-501/-Users-Born-Scorecard/d7c6c01a-5cbb-42e4-83d3-d31df36f5d0d/scratchpad/wf_fixwave6_dry.json"
        json.dump(wf, open(out, "w"), indent=1)
        print(f"DRY RUN — nothing written to n8n. Patched graph at {out}")
        return

    payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
               "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                            if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                     "saveDataErrorExecution", "saveDataSuccessExecution",
                                     "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    res = api("PUT", f"/workflows/{STAGING_ID}", payload)
    assert res.get("id") == STAGING_ID, f"PUT failed: {json.dumps(res)[:400]}"
    print(f"PUT ok · new versionId {res.get('versionId')}")

    # ONE bounce, never deactivate-first as a separate step
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    act = api("POST", f"/workflows/{STAGING_ID}/activate")
    print(f"bounced · active={act.get('active')}")

    got = api("GET", f"/workflows/{STAGING_ID}")
    gmap = {n["name"]: n for n in got["nodes"]}
    bad = 0
    for name, needle, want in ASSERTS:
        body = gmap[name]["parameters"].get("jsCode") or gmap[name]["parameters"].get("jsonBody") or ""
        got_n = body.count(needle)
        ok = got_n == want
        bad += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: {needle[:52]!r} x{got_n} (want {want})")
    assert "turn_state: ts" in gmap["Save Conversation"]["parameters"]["jsonBody"], "Save Conversation assert failed"
    print("  OK   Save Conversation: turn_state persisted")
    assert bad == 0, f"{bad} post-PUT assertions failed"
    print(f"ALL ASSERTIONS PASSED · staging versionId {got.get('versionId')}")


if __name__ == "__main__":
    main()
