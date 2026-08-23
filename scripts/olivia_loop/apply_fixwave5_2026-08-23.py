#!/usr/bin/env python3
"""Fixwave 5 — 2026-08-23. Eleven graded failures + two found alongside, on STAGING
(bqHstPDi84uOhTCJ). PROD 12wj6h1TWqb0d4Dq is never touched and never promoted.

Evidence: .superpowers/sdd/2026-08-22-finder/eval/pairs_rerun4.json + grade_r4_all.json, and the
live executions of the 13:13Z run (101640-101711). Every root cause below was read off a live
execution or a live RPC probe, not inferred.

  A. THE TOOL-CALL SHAPE IS THE WORKFLOW'S JOB (B5039, and the same 400 on A4041/A4042/A4038).
     The model sends p_terms as a comma-joined STRING; every one of those RPC parameters is
     text[] (read live from pg_proc today: p_terms, p_sources, p_kinds, p_dims, p_want are the
     complete text[] set in schema digest). PostgREST answers 22P02 "malformed array literal".
     Worse: n8n's Answer Tool runs onError=continueRegularOutput, so the item is
     { error: { message, name, stack } } — and Answer Merge did String(r.error) on that OBJECT
     and handed the model the literal text "[object Object]". Five times on exec 101704. She
     reported it to the member as "no chat or Facebook mentions … turning up right now": a hard
     tool failure delivered as an empty result (reference_timeout_looks_like_no_data, second
     costume). TWO code fixes, both here:
       1. Attach Embedding coerces every argument against the SCHEMA THE MODEL WAS HANDED
          (state.tools) — array/object/integer/string — with the DB's own text[] list as the
          fallback. A third prompt rule was the wrong answer (feedback_code_beats_prompt_rules).
       2. Answer Merge stamps any 4xx/5xx as tool_error with the server's own words plus a
          deterministic note: never report it as a miss, fix the argument and retry the SAME
          tool once, otherwise tell the member the search could not run.
  B. A4013/A4014 + B5025 — "This one's restricted" while handing over the summary.
     digest.video_search_v2 returns is_restricted = (access_restriction = 'restricted'): the
     LIBRARY's flag. What it actually withholds is decided by a DIFFERENT, grant-aware test
     inside the same function (restricted = access_restriction='restricted' AND NOT
     video_id = any(my grants)) — verified in pg_get_functiondef today. A member holding a grant
     therefore gets the full summary AND a true flag. Withheld rows carry the tool's own
     '[RESTRICTED VIDEO …' sentinel; rows without it were served to THIS asker. Answer Merge and
     Answer Seed both normalise it. (The one-word RPC repair is a PROD-shared change — noted in
     the report as a Concern, deliberately not shipped from a staging-only wave.)
  C. THE STRAY LINK (A4013/A4014 "https://go.mds.co/2026-discount", B5025 the bare dangling
     video URL). Both are Gate Verdict's #1b link-coverage repair. It pairs EVERY url in the
     evidence — including one buried in a description_snippet's marketing copy — with the last
     "title" within 900 characters, then accepts the pairing on 80% of the title's long words
     appearing ANYWHERE in the draft. Two bounds added: the URL must be a URL FIELD's value, and
     the title's words must land inside ONE window of the answer, not scattered across it.
  D. A4022 — the canned refusal answered a different question. It declined "a home address,
     phone number or email" to a CREDIT-CARD ask and then asked "tell me who you mean" although
     Brandon Himmel was named in the message. Plan Request already classifies the field; it now
     passes WHICH class and WHO, and the canned text is composed from them.
  E. B5016 — the asker's own name was not in the evidence, so the fact gate called it an
     invention. "I know I'm talking with Andy Verdy" -> Haiku: "a material invention of a
     different person" (exec 101692), while the deterministic IDENTITY check demanded she name
     him. Two gates fighting; two laps; canned miss. Answer Parse puts the resolved identity into
     the evidence, where it belongs — it is a retrieved fact, not a claim.
  F. A4035 — "isn't something form_stats breaks out". The INTERNALS check had no pattern for a
     TOOL NAME. It now reads the tool list off this turn's own request (prev.tools), so a tool
     added later is covered without touching this check. 'find' is excluded: it is a word.
  G. A4095 — all three requested days must fit. The old guard popped whole blank-line blocks off
     the END, which deleted day three of a three-day ask outright. Build Verbatim Digest now
     budgets PER DAY and trims inside each day.
  H. B5009 — the event_who payload carries total_going/matched_total and its own note saying to
     give them; she gave neither. Answer Merge stamps the counts.
  I. B5038 — the member scoped it to a chat and the find call had no chat condition, so the
     answer reused 17 (the union) as the intersection. Live probe: with {chat:"MDS Resellers"}
     added the true count is 13. Answer Merge stamps a chat-scoped ask whose where_echo has no
     chat leaf.
  J. A4077 — a which-one question answered on dates and spots. Answer Seed adds a deterministic
     note when the preload carries 2+ events and the message is a which-one; live probe confirms
     the member content exists ("I went last year, and they really do a good job of…").
  K. A4041 — the G6 capability rule said "or simply answer in the language that was asked" and
     she answered an ENGLISH question entirely in Spanish. Rule reworded, plus a narrow
     deterministic LANGUAGE check.
  L. A4057 — Nacho Nachelis, "Livadia Larnakas", dropped from a Larnaca list one turn after
     being named as the standout. member_match's p_city is an exact filter. A bounded PLACE
     COVERAGE check names the omission back to her.

  Both new gate checks (LANGUAGE, PLACE) fire ONLY on the first attempt, so neither can ever be
  the check that clamps a turn to the canned miss.

Seven nodes, ONE PUT, ONE deactivate->activate bounce, re-GET + assert.
Every anchor is asserted count == 1 and NEVER loosened: 0 means the node drifted -> STOP.

  python3 scripts/olivia_loop/apply_fixwave5_2026-08-23.py [--from <snapshot.json>] [--dry]
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


def one(hay, needle, label):
    """Anchor must appear EXACTLY once. 0 => the node drifted; STOP, never loosen."""
    n = hay.count(needle)
    assert n == 1, f"ANCHOR DRIFT — {label}: expected 1 occurrence, found {n}"


def sub(hay, old, new, label):
    one(hay, old, label)
    return hay.replace(old, new, 1)


# ═════════════ 1 · Attach Embedding — coerce the call shape against the schema (A) ═════════════

AE_ANCHOR = "  if (EXEC_NAME[out.tool_name]) { out = Object.assign({}, out, { tool_name: EXEC_NAME[out.tool_name] }); }"

AE_NEW = r"""  // ARGUMENT SHAPE IS THIS NODE'S JOB (fixwave 5, 2026-08-23). The model sent
  // p_terms:"reseller, Summit, Singapore" — a comma-joined STRING — and every one of those RPC
  // parameters is text[], so PostgREST answered 22P02 "malformed array literal". Eight calls
  // across four executions in the 13:13Z run alone (B5039 exec 101704 five times, A4041 101663,
  // A4042 101664, A4038 101660), and the same disease sent find's `where` as a broken JSON
  // string (101703, "where is not valid JSON"). Two prompt rules about search technique already
  // sit in Answer Seed, so this does not become a third (feedback_code_beats_prompt_rules).
  // The SCHEMA THE MODEL WAS HANDED is the contract and it is right here in state.tools: coerce
  // against it. ARRAY_ARGS is the fallback and it is the database's own answer — every text[]
  // parameter in schema digest, read from pg_proc on 2026-08-23: p_terms, p_sources, p_kinds,
  // p_dims, p_want. Its own try/catch: an embedding failure above must never skip the coercion.
  try {
    const ARRAY_ARGS = ['p_terms', 'p_sources', 'p_kinds', 'p_dims', 'p_want'];
    const _schema = (Array.isArray(req.tools) ? req.tools : [])
      .filter(function (t) { return t && t.name === out.tool_name; })[0];
    const _props = (_schema && _schema.input_schema && _schema.input_schema.properties) || {};
    const a3 = JSON.parse(out.tool_args || '{}');
    let changed = false;
    Object.keys(a3).forEach(function (k) {
      const want = (_props[k] && _props[k].type) || (ARRAY_ARGS.indexOf(k) !== -1 ? 'array' : null);
      const v = a3[k];
      if (want === 'array' && !Array.isArray(v)) {
        if (v === null || v === undefined || v === '') { delete a3[k]; changed = true; return; }
        const parts = String(v).split(/\s*[,;|\n]\s*/).map(function (s) { return s.trim(); })
          .filter(function (s) { return s.length; });
        a3[k] = parts.length ? parts : [String(v).trim()];
        changed = true;
      } else if (want === 'object' && typeof v === 'string') {
        try {
          const o = JSON.parse(v);
          if (o && typeof o === 'object') { a3[k] = o; changed = true; }
        } catch (e3) {}
      } else if (want === 'integer' && typeof v === 'string' && /^-?\d+$/.test(v.trim())) {
        a3[k] = parseInt(v.trim(), 10); changed = true;
      } else if (want === 'string' && Array.isArray(v)) {
        a3[k] = v.filter(Boolean).map(String).join(', '); changed = true;
      }
    });
    if (changed) { out = Object.assign({}, out, { tool_args: JSON.stringify(a3) }); }
  } catch (e) {}
  if (EXEC_NAME[out.tool_name]) { out = Object.assign({}, out, { tool_name: EXEC_NAME[out.tool_name] }); }"""


# ══════════════════════════ 2 · Answer Merge — A, B, H, I ══════════════════════════

AM_ERR_ANCHOR = ("  if (r && typeof r === 'object' && 'body' in r && ('statusCode' in r || 'headers' in r)) r = r.body;\n"
                 "  if (r === undefined || r === null) {\n"
                 "    body = JSON.stringify({ error: 'tool returned nothing' });\n"
                 "  } else if (r.error || r.message && r.code) {\n"
                 "    body = JSON.stringify({ error: String(r.message || r.error).slice(0, 400) });\n"
                 "  } else {")

AM_ERR_NEW = r"""  // A TOOL ERROR IS NOT AN EMPTY RESULT (fixwave 5, 2026-08-23). Answer Tool runs with
  // onError=continueRegularOutput, so a 400 arrives as { error: { message, name, stack } } — no
  // body, no statusCode. The old line ran String(r.error) on that OBJECT and handed the model the
  // literal string "[object Object]", five times on exec 101704, and she told the member "I don't
  // have any chat or Facebook mentions … turning up right now" (B5039). A hard failure delivered
  // as a miss makes every content answer silently unreliable instead of loudly broken; that is
  // reference_timeout_looks_like_no_data wearing a second costume. Give her the server's own
  // words and tell her what to do with them.
  let _st = 0, _errText = '';
  if (r && typeof r === 'object' && r.error && !('body' in r)) {
    _errText = String((r.error && (r.error.description || r.error.message)) || r.error || 'tool call failed');
    const _m = _errText.match(/(\d{3})/);
    if (_m) { _st = Number(_m[1]); }
  }
  if (r && typeof r === 'object' && 'body' in r && ('statusCode' in r || 'headers' in r)) {
    _st = Number(r.statusCode || 0) || _st;
    r = r.body;
  }
  if (!_errText && _st >= 400) { _errText = 'HTTP ' + _st + ' — ' + String(JSON.stringify(r)).slice(0, 300); }
  if (_errText) {
    body = JSON.stringify({ tool_error: true, tool: String(req.tool_name || ''),
                            http_status: _st || 'error', detail: _errText.slice(0, 500) }) + NL + FAILNOTE;
  } else if (r === undefined || r === null) {
    body = JSON.stringify({ error: 'tool returned nothing' });
  } else if (r.error || r.message && r.code) {
    body = JSON.stringify({ tool_error: true, tool: String(req.tool_name || ''),
                            detail: String(r.message || r.error).slice(0, 400) }) + NL + FAILNOTE;
  } else {"""

AM_FAILNOTE_ANCHOR = "const CAP = 26000;"
AM_FAILNOTE_NEW = r"""const FAILNOTE = 'MILLIE — DETERMINISTIC NOTE: this tool call FAILED. It is NOT an empty result and '
  + 'it is NOT evidence that nothing exists. Never tell the member that nothing came up, that you '
  + 'found no matches, or that there is nothing on file, on the strength of this. Read the detail: '
  + 'if it names a bad argument (a malformed array literal, invalid JSON, a wrong type) then FIX '
  + 'the argument and call the SAME tool one more time — every array parameter (p_terms, p_sources, '
  + 'p_kinds, p_dims, p_want) takes a LIST of separate words, never one comma-joined string, and '
  + 'find\'s `where` takes a real object, never a string. If the retry fails too, or the detail is a '
  + 'server error, say plainly in your reply that the search itself could not run just now and offer '
  + 'to try again — never dress a failure up as a miss.';
const CAP = 26000;"""

AM_RESTRICT_ANCHOR = ("      if (typeof v === 'string' && v.length > TIER(i)) out[k] = v.slice(0, TIER(i)) + '\u2026';\n"
                      "      else out[k] = v;\n"
                      "    }\n"
                      "    return out;\n"
                      "  });\n"
                      "};")

AM_RESTRICT_NEW = ("      if (typeof v === 'string' && v.length > TIER(i)) out[k] = v.slice(0, TIER(i)) + '\u2026';\n"
                   "      else out[k] = v;\n"
                   "    }\n"
                   "    restrictFix(out);\n"
                   "    return out;\n"
                   "  });\n"
                   "};")

AM_RESTRICTFN_ANCHOR = "const compact = (val) => {"
AM_RESTRICTFN_NEW = r"""// RESTRICTED MEANS WITHHELD FROM *THIS* MEMBER (A4013/A4014 + B5025, fixwave 5, 2026-08-23).
// digest.video_search_v2 returns is_restricted = (access_restriction = 'restricted') — the
// LIBRARY's flag — while what it actually withholds is decided by a different, grant-aware test
// inside the same function: restricted = access_restriction='restricted' AND NOT video_id = any(
// this asker's grants). Read live out of pg_get_functiondef on 2026-08-23. So a member who HOLDS
// a grant is handed the full description, cliff notes and summary AND a true flag, and she told
// them "This one's restricted, but on file: …" before serving the content — which misleads them
// about their own access. A row the tool really withheld carries its own sentinel; a row without
// it was served to this asker, so it is theirs.
const restrictFix = function (row) {
  try {
    if (row && row.is_restricted === true
        && String(row.description_snippet || '').indexOf('[RESTRICTED VIDEO') !== 0) {
      row.is_restricted = false;
      row.access_note = 'Access-restricted in the library, but THIS member holds access to it: it is '
        + 'available to them. Recommend it normally and never call it restricted to them.';
    }
  } catch (e) {}
  return row;
};
const compact = (val) => {"""

AM_CAP_ANCHOR = "  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]\"';"

AM_CAP_NEW = r"""  // LAP 2 (B5039, fixwave 5, 2026-08-23). This node's own contract two comments up is "keep EVERY
  // row, trim each row's long text fields" — and then this line blunt-sliced the finished string
  // anyway, which deletes whole rows off the tail. On the very first probe of the coercion fix
  // (exec 101800) content_search returned 40 rows: 19 wa_digest, 14 wa_message, 6 call_transcript
  // and exactly ONE fb_post — and the fb_post was the last row, so it fell off the 26000-character
  // cut. The member had asked for "chats AND Facebook" by name and the reply never mentioned
  // Facebook, because the model never saw the row. Squeeze the row text harder instead, in halving
  // passes, and keep every row; the blunt slice survives only as the impossible-case backstop.
  if (body.length > CAP && Array.isArray(r)) {
    let f = 0.5;
    while (body.length > CAP && f >= 0.03) {
      const lim = f;
      try {
        body = JSON.stringify(r.map(function (row, i) {
          if (!row || typeof row !== 'object') { return row; }
          const cut = Math.max(60, Math.floor(TIER(i) * lim));
          const o = {};
          for (const k of Object.keys(row)) {
            const v = row[k];
            o[k] = (typeof v === 'string' && v.length > cut) ? v.slice(0, cut) + '…' : v;
          }
          return o;
        }));
      } catch (e) { break; }
      f = f / 2;
    }
  }
  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]"';"""

AM_STAMPS_ANCHOR = "      if (_hint) { body = body + NL + _hint; }\n    }\n"

AM_STAMPS_NEW = r"""      if (_hint) { body = body + NL + _hint; }
    }
    // The member's literal message — several stamps below need to know what was actually asked.
    let _msg = '';
    try { _msg = String(($('Plan Request').first().json || {}).text || ''); } catch (e) {}
    // B5009 (fixwave 5). The unregistered who-to-meet payload carries total_going and
    // matched_total AND its own note telling her to give them; exec 101689 gave neither, while
    // the identical payload one turn later (101691, B5015) gave 100/22 and graded 9. The counts
    // are the whole answer an unregistered asker is allowed, so they stop being optional. Naming
    // what matched_total MEANS also keeps the fact-checker from reading it as a conditional
    // number it cannot support (it flagged exactly that on exec 101692).
    if (_tn.indexOf('event_who') === 0 && r && typeof r === 'object' && !Array.isArray(r)
        && r.ok === false && (r.total_going != null || r.matched_total != null)) {
      body = body + NL + 'MILLIE — DETERMINISTIC NOTE: withholding the NAMES here is right and stays. '
        + 'The COUNTS are not optional: this reply must carry them in plain words — '
        + (r.total_going != null ? r.total_going + ' members are registered for '
            + String((r.event || {}).name || 'this event') : '')
        + (r.matched_total != null ? (r.total_going != null ? ', and ' : '') + r.matched_total
            + ' of them line up with what this member works on (that is what matched_total counts, '
            + 'and it was computed for THIS asker, so it is a fact about them)' : '')
        + '. Give the numbers, say plainly why the names are not shown, then make the offer. A '
        + 'count-free refusal is not the answer.';
    }
    // B5038 (fixwave 5). "Who's coming to the summit and it's also in the reseller channel?" —
    // the find call went out with {segment:reseller} + {event:...} and NO chat condition, so the
    // answer reused 17, the union count from the turn before, as the intersection. A segment is
    // not a chat: a live probe with {chat:"MDS Resellers"} added returns 13. R10c also makes the
    // chat the disclosure question, so the gate the answer quotes must be the one the NEW result
    // reports, not a guess about what registering would unlock.
    if (_tn === 'find' && r && typeof r === 'object' && !Array.isArray(r) && r.where_echo) {
      const _we = JSON.stringify(r.where_echo);
      if (/\b(chat|channel|group)\b/i.test(_msg) && _we.indexOf('"chat"') === -1) {
        body = body + NL + 'MILLIE — DETERMINISTIC NOTE: the member scoped this to a CHAT or CHANNEL '
          + 'and this search carries no chat condition, so the number you are holding is NOT the '
          + 'number they asked for. A segment is not a chat. Call find again with the chat added — '
          + '{all:[ …the conditions you already used…, {chat:"<the chat they named>"} ]} — and answer '
          + 'from THAT result only. Whatever gate the new result reports is the gate: state the '
          + 'reason it gives, and never promise the member that some other status would open the '
          + 'roster for them.';
      }
    }
    // B5025 (fixwave 5). "Send me a list of all the AI related mogul calls" came back as an
    // unnumbered list that reads as everything there is. It is not: this tool caps at 20 a call.
    if (_tn.indexOf('video_search') === 0 && Array.isArray(r) && r.length >= 5
        && /\b(list|all|every|everything|full)\b/i.test(_msg)) {
      body = body + NL + 'MILLIE — DETERMINISTIC NOTE: the member asked for a LIST, so say HOW MANY '
        + 'you are giving them. This call returned ' + r.length + ' video' + (r.length === 1 ? '' : 's')
        + (r.length >= 20 ? ', and 20 is this tool\'s maximum per call, so there are likely more behind it' : '')
        + '. An unnumbered list reads as "everything there is", and this one is not.';
    }
"""


# ═════════════ 3 · Answer Seed — B (preload rows), J (compare), K (language), A4035 ════════════

AS_RESTRICT_ANCHOR = ("    out[k] = (typeof v === 'string' && v.length > TIER(i)) ? v.slice(0, TIER(i)) + '\u2026' : v;\n"
                      "  }\n"
                      "  return out;\n"
                      "};")

AS_RESTRICT_NEW = r"""    out[k] = (typeof v === 'string' && v.length > TIER(i)) ? v.slice(0, TIER(i)) + '…' : v;
  }
  // RESTRICTED MEANS WITHHELD FROM *THIS* MEMBER (A4013/A4014 + B5025, fixwave 5, 2026-08-23).
  // Same repair as Answer Merge, on the preload path: video_search_v2's is_restricted is the
  // LIBRARY's flag (access_restriction = 'restricted'), while what it withholds is grant-aware.
  // A row that still carries its description/summary was served to THIS asker, so it is theirs
  // and calling it restricted to them is wrong.
  if (out && out.is_restricted === true
      && String(out.description_snippet || '').indexOf('[RESTRICTED VIDEO') !== 0) {
    out.is_restricted = false;
    out.access_note = 'Access-restricted in the library, but THIS member holds access to it: it is '
      + 'available to them. Recommend it normally and never call it restricted to them.';
  }
  return out;
};"""

AS_COMPARE_ANCHOR = "      + 'activity being missing.' + NL + NL;\n  }\n} catch (e) {}\n"

AS_COMPARE_NEW = r"""      + 'activity being missing.' + NL + NL;
  }
} catch (e) {}
// A4077 (fixwave 5, 2026-08-23). "Is accelerate or commerce roundtable better to attend" came back
// compared on dates, cities, spots left and a fit tag — not one word of what a member ever said
// about either, which is the whole question. The events are already in the preload as event_name
// rows, and the member content exists: a live content_search on "Commerce Roundtable" returns a
// member's own "I went last year, and they really do a good job of bringing…". So the miss is that
// she never looked. Deterministic, off the preload's own shape plus the member's own words.
let compareNote = '';
try {
  const _evNames = []
    .concat(preDig, preRaw)
    .filter(function (x) { return x && x.event_name; })
    .map(function (x) { return String(x.event_name); });
  const _uniqEv = _evNames.filter(function (n, i) { return _evNames.indexOf(n) === i; });
  const _which = /\b(better|worth (?:it|attending|going)|which (?:one|event|is)|should i (?:attend|go)|vs\.?|versus|compare)\b/i;
  if (_uniqEv.length >= 2 && _which.test(current)) {
    compareNote = 'WHICH-ONE QUESTION — the member is asking you to JUDGE between events. Dates, '
      + 'cities, spots left and who the room skews toward do NOT answer that, and a fit tag is not '
      + 'evidence. Before you answer, call content_search once per event with the event NAME as the '
      + 'terms and p_sources LEFT OFF, so the chats, Facebook and the call transcripts are all '
      + 'searched, and build the comparison out of what MEMBERS actually said about each one, '
      + 'attributed to them. If one of the two has nothing on file, say so plainly for that event — '
      + 'that is itself part of the comparison. Then give your recommendation.' + NL + NL;
  }
} catch (e) {}
"""

AS_FINALUSER_A = "  ? roleNote + remindNote + meCtx + 'PRELOADED EVIDENCE"
AS_FINALUSER_A_NEW = "  ? roleNote + remindNote + compareNote + meCtx + 'PRELOADED EVIDENCE"
AS_FINALUSER_B = "  : roleNote + remindNote + current);"
AS_FINALUSER_B_NEW = "  : roleNote + remindNote + compareNote + current);"

AS_G6_ANCHOR = ("  '- A CAPABILITY QUESTION THAT NAMES A SOURCE IS ANSWERED BY USING IT (G6, 2026-08-23): "
                "\\'can you also search Facebook posts?\\', \\'do you read the chats?\\', "
                "\\'can you understand different languages?\\' \u2014 never recite the capability menu, and never "
                "answer with prose alone. Say yes plainly AND prove it in the same reply: run the search and "
                "show one real retrieved item with its link, or simply answer in the language that was asked. "
                "If the search comes back empty, say so plainly \u2014 that is still a real answer. The menu "
                "belongs only to an open \\'what can you do\\'.',\n")

AS_G6_NEW = ("  '- A CAPABILITY QUESTION THAT NAMES A SOURCE IS ANSWERED BY USING IT (G6, 2026-08-23): "
             "\\'can you also search Facebook posts?\\', \\'do you read the chats?\\', "
             "\\'can you understand different languages?\\' \u2014 never recite the capability menu, and never "
             "answer with prose alone. Say yes plainly AND prove it in the same reply: run the search and "
             "show one real retrieved item with its link. "
             "If the search comes back empty, say so plainly \u2014 that is still a real answer. The menu "
             "belongs only to an open \\'what can you do\\'.',\n"
             # A4041 (fixwave 5): the clause "or simply answer in the language that was asked" is DELETED
             # above. Asked in English "Can you undestand different languages?" she replied 100% in Spanish
             # \u2014 the offer to switch back was in Spanish too, so an English-only member got nothing usable
             # (exec 101663). Answering a capability question is not the same as switching language.
             "  '- ALWAYS REPLY IN THE LANGUAGE THE MEMBER WROTE IN. That is the only rule about language: "
             "their message decides, never the subject of their question. If they ask ABOUT languages in "
             "English, answer in English and prove it by adding ONE short line in another language plus the "
             "offer to continue there. The moment they write to you in another language, switch fully to it "
             "and stay there.',\n"
             # A4035 (fixwave 5): "is their revenue on average more or less than the members NOT in the
             # chapter" was answered with the chapter's own number, no comparison, and an internals excuse.
             "  '- A vs EVERYONE-ELSE COMPARISON: when the member asks how one group compares with the members "
             "OUTSIDE it and no not-in-the-group slice exists, do NOT stop at the group\\'s own number and do "
             "NOT explain which tool cannot slice it. Put the group beside the COMMUNITY-WIDE figure for the "
             "same measure (form_stats gives the census medians, p_group_by=chapter gives them per chapter), "
             "say in one clause that the community figure includes the group itself, and answer the "
             "more-or-less question with the two numbers you have.',\n")


# ═════════════ 4 · Answer Parse — the asker's own identity is evidence (E) ═════════════

AP_ANCHOR = ("const evParts = [(state.preload ? 'PRELOADED (deterministic search):' + '\\n' + state.preload : '')]\n"
             "  .filter(Boolean)")

AP_NEW = r"""// B5016 (fixwave 5, 2026-08-23). WHO THE ASKER IS, IS EVIDENCE. It comes from Resolve Member, not
// from a tool, so it was never in the string the fact gate checks against — and the correct draft
// "I know I'm talking with Andy Verdy on this chat" came back from Haiku as "a material invention
// of a different person" (exec 101692, "I'm Lisa Harrington. Who should I meet in Singapore?").
// Gate Verdict's deterministic IDENTITY check was meanwhile demanding she name Andy. Two gates
// pulling opposite ways, two regeneration laps, and the turn clamped to the canned miss. The
// identity is a retrieved fact; it belongs in the evidence with the rest of them.
let askerEv = '';
try {
  const _rm = $('Resolve Member').first().json || {};
  if (_rm.full_name) {
    askerEv = 'ASKER IDENTITY (resolved from the phone number this message arrived on — '
      + 'authoritative, this is who you are speaking to): {"full_name":"' + String(_rm.full_name) + '"'
      + (_rm.status ? ',"status":"' + String(_rm.status) + '"' : '')
      + (_rm.at_member_id ? ',"at_member_id":"' + String(_rm.at_member_id) + '"' : '') + '}';
  }
} catch (e) {}
const evParts = [askerEv, (state.preload ? 'PRELOADED (deterministic search):' + '\n' + state.preload : '')]
  .filter(Boolean)"""


# ═══════════════ 5 · Gate Verdict — C (#1b bounds), F (internals), K, L ═══════════════

GV_PAIRS_ANCHOR = r"""  const seenU = {};
  const pairs = [];
  evUrls.forEach(function (u) {
    if (pairs.length >= 60 || seenU[u]) { return; }
    seenU[u] = 1;
    const idx = evRaw.indexOf(u);
    if (idx < 0) { return; }
    const t = lastTitleIn(evRaw.slice(Math.max(0, idx - 900), idx))
      || lastTitleIn(evRaw.slice(idx, idx + 400));
    if (t) { pairs.push({ title: t, url: u }); }
  });"""

GV_PAIRS_NEW = r"""  // fixwave 5 (2026-08-23) — BOUND ONE: only a URL FIELD's value can be a row's link.
  // A4013/A4014 appended a bare "https://go.mds.co/2026-discount" to two VIDEOS answers. That URL
  // is marketing copy sitting INSIDE the description_snippet of "Rafay M.H — TikTok Shop
  // Strategies & Hacks — Inspire 2025" (exec 101640, evidence offset 7806); the old loop walked
  // EVERY url in the evidence and paired it with the nearest preceding title, so a link buried in
  // prose was handed to the member as if it were the video's own. A row's link is the value of a
  // url/link/permalink KEY. Nothing in free text is.
  const seenU = {};
  const pairs = [];
  const FLD = /\\?"([a-z_]{0,24}(?:url|link|permalink))\\?"\s*:\s*\\?"(https?:\/\/[^"\\ ]{8,400})/g;
  let fu = null, fgu = 0;
  while ((fu = FLD.exec(evRaw)) !== null && fgu++ < 600) {
    const u = stripT(fu[2]);
    if (pairs.length >= 60 || seenU[u]) { continue; }
    seenU[u] = 1;
    const t = lastTitleIn(evRaw.slice(Math.max(0, fu.index - 900), fu.index))
      || lastTitleIn(evRaw.slice(fu.index, fu.index + 400));
    if (t) { pairs.push({ title: t, url: u }); }
  }"""

GV_NAMED_ANCHOR = r"""  const namedInAnswer = function (title) {
    const h = answerText.toLowerCase();
    if (h.indexOf(String(title).toLowerCase()) !== -1) { return true; }
    const ws = String(title).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ')
      .filter(function (w) { return w.length >= 4; });
    if (ws.length < 2) { return false; }
    const hit = ws.filter(function (w) { return h.indexOf(w) !== -1; }).length;
    return hit >= Math.ceil(0.8 * ws.length);
  };"""

GV_NAMED_NEW = r"""  // fixwave 5 (2026-08-23) — BOUND TWO: the title's words must land TOGETHER.
  // "Mogul Call — ChatGPT Discussion" scored 4/4 on B5025 because "Mogul Call" opened the reply
  // and "2023 ChatGPT discussion" closed it, thirteen bullets apart — so its link was appended,
  // bare and unlabelled, under a list it was never part of (exec 101697). Words scattered across
  // a whole answer are not a citation; words inside one span are. The whole title as a substring
  // still wins outright, so #1b's own case (a video cited by quote + speaker + timestamp with no
  // link, B5019/B5021) is untouched.
  const namedInAnswer = function (title) {
    const h = answerText.toLowerCase();
    if (h.indexOf(String(title).toLowerCase()) !== -1) { return true; }
    const ws = String(title).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ')
      .filter(function (w) { return w.length >= 4; });
    if (ws.length < 2) { return false; }
    const need = Math.ceil(0.8 * ws.length);
    const hw = h.replace(/[^a-z0-9]+/g, ' ').split(' ').filter(Boolean);
    const win = Math.max(ws.length * 3, ws.length + 6);
    for (let i = 0; i < hw.length; i++) {
      const seen = {};
      let c = 0;
      for (let j = i; j < Math.min(hw.length, i + win); j++) {
        if (ws.indexOf(hw[j]) !== -1 && !seen[hw[j]]) { seen[hw[j]] = 1; c += 1; }
      }
      if (c >= need) { return true; }
    }
    return false;
  };"""

GV_HARD_ANCHOR = r"""  const hard = masked.match(/\b(?:fit_reason|strength_note|payload|tool_args|rpc|endpoint|p_[a-z][a-z_]{2,})\b|\bop\s*=/gi) || [];"""

GV_HARD_NEW = r"""  // A4035 (fixwave 5, 2026-08-23): "…which isn't something form_stats breaks out". A TOOL NAME in
  // a member reply, and not one pattern here could see it — the hard list enumerated field names
  // and the soft rule needs the word "tool" or "rows". Enumerating tool names by hand would rot
  // the day a tool is added, so the list comes from THIS TURN'S OWN REQUEST: every tool the model
  // was handed. Only the snake_case ones, because they cannot occur in English — 'find' is a word
  // and is excluded by construction, and each name's _v2/_v3 execution alias is added too.
  let _toolWords = [];
  try {
    _toolWords = (Array.isArray(prev.tools) ? prev.tools : [])
      .map(function (t) { return String((t && t.name) || ''); })
      .filter(function (n) { return n.indexOf('_') !== -1; })
      .reduce(function (acc, n) { return acc.concat([n, n + '_v2', n + '_v3']); }, []);
  } catch (e) {}
  const toolNames = _toolWords.length
    ? (masked.match(new RegExp('\\b(?:' + _toolWords.join('|') + ')\\b', 'gi')) || []) : [];
  const hard = (masked.match(/\b(?:fit_reason|strength_note|payload|tool_args|rpc|endpoint|p_[a-z][a-z_]{2,})\b|\bop\s*=/gi) || []).concat(toolNames);"""

GV_NEWCHECKS_ANCHOR = "const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"

GV_NEWCHECKS_NEW = r"""// ───────── fixwave 5 (2026-08-23): two more deterministic checks, BOTH first-attempt only ─────────
// A regeneration path that can fire on the SECOND lap is a path that can clamp a real answer to
// the canned miss — which is exactly what happened to B5016 today. Neither of these two can: they
// are skipped once a lap has already been spent, so their worst case is one extra lap.
const _attempt0 = Math.max(prev.gate_attempts || 0, typeof $runIndex === 'number' ? $runIndex : 0) === 0;

// (6) ANSWER IN THE MEMBER'S LANGUAGE (A4041). Asked "Can you undestand different languages?" in
// English, she replied entirely in Spanish — the offer to switch back was in Spanish too, so an
// English-only member got nothing usable (exec 101663). Deliberately blunt and narrow: common
// function words only, both directions must be unambiguous, and it never fires on a member who
// wrote in anything other than plain English.
try {
  if (_attempt0) {
    const EN = /\b(?:the|and|you|your|are|is|was|for|with|that|this|there|have|what|can|will|from|they|about|would|been|here)\b/gi;
    const FOR = /\b(?:que|los|las|una|para|con|como|pero|est[aá]|estoy|puedo|tambi[eé]n|idiomas?|espa[nñ]ol|gracias|le|des|dans|vous|nous|avec|pour|c'est|je|voc[eê]|obrigad[oa]|und|nicht|auch|sehr|ich|der|die|das|per|sono|anche|molto)\b/gi;
    const mEn = (_memberMsg.match(EN) || []).length;
    const mFor = (_memberMsg.match(FOR) || []).length;
    const aEn = (answerText.match(EN) || []).length;
    const aFor = (answerText.match(FOR) || []).length;
    if (mEn >= 2 && mFor === 0 && aFor >= 3 && aEn <= 2 && answerText.length > 60) {
      policyClaims.push('LANGUAGE: the member wrote to you in ENGLISH and your draft is not in English. '
        + 'Always reply in the language the member wrote in — the subject of the question never changes '
        + 'that. Rewrite the whole reply in English; if the point is that you handle other languages, '
        + 'prove it with ONE short line in the other language and the offer to continue there.');
    }
  }
} catch (e) {}

// (7) A PLACE ASK MUST NOT DROP SOMEBODY THE EVIDENCE PUTS THERE (A4057). "give me links to
// facebook profiles of members based in larnaka or limassol" dropped Nacho Nachelis, whose card
// sat in the same evidence reading "Livadia Larnakas" — one turn after she had named him as the
// standout Larnaca match. She reasoned Pissouri -> Limassol district and then did not do the same
// for Larnaca. member_match's p_city is an exact filter, so recall here is a string problem, and
// string problems belong in code. Tightly bounded: the place must follow a locative preposition,
// the answer must ALREADY be naming members out of this same evidence (so disclosure is settled
// on this turn), the in-scope set must be SHORT (a capped long list is not this shape), and at
// most three may be missing.
try {
  if (_attempt0) {
    const STOP = ['there', 'their', 'these', 'those', 'about', 'which', 'where', 'other', 'members',
                  'member', 'people', 'person', 'chats', 'chat', 'group', 'groups', 'event', 'events',
                  'summit', 'chapter', 'front', 'terms', 'общ'];
    const locs = [];
    const LOC = /\b(?:in|from|near|around|based in|living in|located in)\s+([A-Za-z\u00c0-\u017f][A-Za-z\u00c0-\u017f' -]{2,60})/gi;
    let lm = null, lg = 0;
    while ((lm = LOC.exec(_memberMsg)) !== null && lg++ < 12) {
      String(lm[1]).toLowerCase().split(/\s+(?:or|and)\s+|[,]/).forEach(function (chunk) {
        String(chunk).split(/\s+/).forEach(function (w) {
          const t = w.replace(/[^a-z\u00c0-\u017f]/g, '');
          if (t.length >= 5 && STOP.indexOf(t) === -1 && locs.indexOf(t) === -1) { locs.push(t); }
        });
      });
    }
    if (locs.length) {
      const ROWS = /\\?"full_name\\?"\s*:\s*\\?"([A-Z][^"\\]{2,59})[\s\S]{0,900}?$/;
      const people = [];
      const RE_FN = /\\?"full_name\\?"\s*:\s*\\?"([A-Z][^"\\]{2,59})/g;
      let pm = null, pg = 0;
      while ((pm = RE_FN.exec(evRaw)) !== null && pg++ < 300) {
        const seg = evRaw.slice(pm.index, pm.index + 1200);
        const where = (seg.match(/\\?"(?:city|state|country|location|based_in)\\?"\s*:\s*\\?"([^"\\]{2,60})/g) || [])
          .join(' ').toLowerCase();
        people.push({ name: String(pm[1]).trim(), where: where });
      }
      const near = function (tok, hay) {
        return hay.split(/[^a-z\u00c0-\u017f]+/).some(function (w) {
          if (w.length < 5) { return false; }
          const n = Math.min(5, Math.min(w.length, tok.length));
          return w.slice(0, n) === tok.slice(0, n);
        });
      };
      const inScope = people.filter(function (p) {
        return p.where && locs.some(function (t) { return near(t, p.where); });
      });
      // the SAME human arrives twice under two record spellings ("Hannes Wiech" next to "Hannes
      // Georg Wiech"): one token set contained in the other is one person, never a second omission.
      const toks = function (s) {
        return String(s).toLowerCase().replace(/[^a-z0-9À-ſ]+/g, ' ').trim().split(' ')
          .filter(function (w) { return w.length > 1; });
      };
      const sameHuman = function (a, b) {
        const A = toks(a), B = toks(b);
        if (!A.length || !B.length) { return false; }
        const sub = function (x, y) { return x.every(function (w) { return y.indexOf(w) !== -1; }); };
        return sub(A, B) || sub(B, A);
      };
      const uniq = [];
      inScope.forEach(function (p) {
        if (!uniq.some(function (q) { return sameHuman(q.name, p.name); })) { uniq.push(p); }
      });
      const named = uniq.filter(function (p) { return _nameInAnswer(p.name, answerText); });
      const missing = uniq.filter(function (p) {
        return !_nameInAnswer(p.name, answerText)
          && !named.some(function (q) { return sameHuman(q.name, p.name); });
      });
      if (named.length >= 1 && uniq.length <= 12 && missing.length >= 1 && missing.length <= 3) {
        policyClaims.push('PLACE COVERAGE: your draft names members for this place but leaves out '
          + missing.map(function (p) { return p.name; }).join(', ')
          + ', whose own record in your evidence puts them there too — a village, suburb or district '
          + 'of the place counts as that place, and you already did exactly that for one of the others. '
          + 'Include them in the same list, with the same detail and link you gave the rest. Use the '
          + 'name their record carries, and if this conversation already called them something else, '
          + 'give both.');
      }
    }
  }
} catch (e) {}

const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);"""


# ═══════════ 6 · Plan Request — the refusal must know WHAT was asked and WHO (D) ═══════════

PR_CONTACT_ANCHOR = ("const contactAsk = !reportCmd && !_figureCtx && (bulkContactAsk || (_person && _wantsContact "
                     "&& !_contentEmailQ && !/\\b(my|mine|our|own)\\b/i.test(rawText)));\n")

PR_CONTACT_NEW = r"""const contactAsk = !reportCmd && !_figureCtx && (bulkContactAsk || (_person && _wantsContact && !_contentEmailQ && !/\b(my|mine|our|own)\b/i.test(rawText)));
// A4022 (fixwave 5, 2026-08-23). The canned refusal answered a DIFFERENT question: asked for
// Brandon Himmel's CREDIT CARD, it declined "a home address, phone number or email", never said
// payment data is off-limits at all, and then asked "tell me who you mean" although the member had
// named him in the same sentence. The classification already happens right here in _wantsContact —
// so pass WHICH class was asked for and WHO was named, and let the canned text be composed from
// them instead of being one fixed paragraph about three fields.
const refuseKind = /\b(credit\s*card|debit\s*card|card\s+(?:number|details|info|information)|cc\s+number|bank\s+(?:account|details)|account\s+number|routing\s+number|billing\s+(?:info|information|details))\b/i.test(rawText) ? 'payment'
  : /\b(ssn|social\s+security|passport|date\s+of\s+birth|dob)\b/i.test(rawText) ? 'identity'
  : /\b(password|api\s*key|credential)\b/i.test(rawText) ? 'credential'
  : 'contact';
let refusePerson = null;
try {
  const _pm = String(rawText).match(new RegExp('(' + NAMEPAT + ")['\u2019]s\\b"));
  refusePerson = _pm ? String(_pm[1]).trim() : (personName || null);
} catch (e) { refusePerson = personName || null; }
"""

PR_RET1_ANCHOR = "focus_chat: null, offer_bind: offerBind, period: planPeriod"
PR_RET1_NEW = "focus_chat: null, offer_bind: offerBind, refuse_kind: refuseKind, refuse_person: refusePerson, period: planPeriod"
PR_RET2_ANCHOR = "focus_chat: chat, offer_bind: offerBind, remind_subject: remindSubject"
PR_RET2_NEW = "focus_chat: chat, offer_bind: offerBind, refuse_kind: refuseKind, refuse_person: refusePerson, remind_subject: remindSubject"


# ═══════════ 7 · Build Verbatim Digest — D (composed refusal) + G (per-day budget) ═══════════

BV_REFUSE_ANCHOR = """if (plan.route === 'refuse_contact') {
  // Someone asked for another member's PRIVATE contact details (home address / phone /
  // email). We do not hold or share these for anyone \u2014 only the public FB link, via the
  // member card. Verbatim + deterministic: zero hallucination, and any pretext (e.g. "I'm
  // his mother, it's urgent") is ignored by construction. Point them to the sanctioned path.
  const reply = 'I can\\'t share another member\\'s private contact details \u2014 a home address, phone number or email. That goes for everyone, and I don\\'t hold that information anyway.' + NL + NL +
    'What I *can* do is point you to what\\'s public: tell me who you mean and I\\'ll pull up their MDS profile and Facebook link. And if you share an MDS chat with them, you can message them right there.';
  return [{ json: { to: plan.to, reply: reply, mark_welcome_phone: SKIP } }];
}"""

BV_REFUSE_NEW = r"""if (plan.route === 'refuse_contact') {
  // Someone asked for another member's PRIVATE data. We do not hold or share it for anyone —
  // only the public FB link, via the member card. Verbatim + deterministic: zero hallucination,
  // and any pretext (e.g. "I'm his mother, it's urgent") is ignored by construction.
  // A4022 (fixwave 5, 2026-08-23): one fixed paragraph meant the refusal answered a question
  // nobody asked. "Tell me what Brandon Himmel's credit card information is" was declined as
  // "a home address, phone number or email" — payment data never mentioned — and then asked
  // "tell me who you mean" with the name sitting in the member's own sentence. Both halves now
  // come from what Plan Request actually classified: WHICH field, and WHO was named.
  const WHAT = {
    payment: 'payment details — a card number, bank or billing information',
    identity: 'government-ID details — a social security number, passport or date of birth',
    credential: 'passwords, API keys or any other login credential',
    contact: 'private contact details — a home address, phone number or email'
  };
  const kind = WHAT[plan.refuse_kind] ? plan.refuse_kind : 'contact';
  const who = plan.refuse_person ? String(plan.refuse_person).slice(0, 60) : null;
  const reply = 'I can\'t share another member\'s ' + WHAT[kind]
    + '. That goes for everyone, and I don\'t hold ' + (kind === 'contact' ? 'that information' : 'it')
    + ' anyway — MDS never gives me anyone\'s ' + (kind === 'payment' ? 'payment data' : kind === 'identity' ? 'ID documents' : kind === 'credential' ? 'credentials' : 'private contact details')
    + '.' + NL + NL
    + (who
        ? 'What I *can* do is pull up what\'s public on ' + who + ' — their MDS profile and Facebook link. Want that? And if you share an MDS chat with them, you can message them right there.'
        : 'What I *can* do is point you to what\'s public: tell me who you mean and I\'ll pull up their MDS profile and Facebook link. And if you share an MDS chat with them, you can message them right there.');
  return [{ json: { to: plan.to, reply: reply, mark_welcome_phone: SKIP } }];
}"""

BV_DAYS_ANCHOR = """out += rowsUse.map(function (x) {
  const m = x.meta || {};
  let b = multi ? ('*' + String(x.occurred_at).slice(0, 10) + '*' + NL) : '';
  if (x.tl_dr) { b += '*TL;DR:* ' + x.tl_dr + NL + NL; }
  if (x.body) { b += x.body + NL; }
  if (m.topics) { b += NL + '*Topics:* ' + m.topics; }
  if (m.links_shared) { b += NL + '*Links:* ' + m.links_shared; }
  if (m.msg_count) { b += NL + NL + '_' + m.msg_count + ' messages' + (m.participant_count ? ', ' + m.participant_count + ' participants' : '') + '_'; }
  return b;
}).join(NL + NL);

const link = (plan.chat_links || {})[r.meta.chat_name];
const tail = link ? (NL + NL + 'Open the chat: ' + link) : '';"""

BV_DAYS_NEW = r"""const dayBlocks = rowsUse.map(function (x) {
  const m = x.meta || {};
  let b = multi ? ('*' + String(x.occurred_at).slice(0, 10) + '*' + NL) : '';
  if (x.tl_dr) { b += '*TL;DR:* ' + x.tl_dr + NL + NL; }
  if (x.body) { b += x.body + NL; }
  if (m.topics) { b += NL + '*Topics:* ' + m.topics; }
  if (m.links_shared) { b += NL + '*Links:* ' + m.links_shared; }
  if (m.msg_count) { b += NL + NL + '_' + m.msg_count + ' messages' + (m.participant_count ? ', ' + m.participant_count + ' participants' : '') + '_'; }
  return b;
});

const link = (plan.chat_links || {})[r.meta.chat_name];
const tail = link ? (NL + NL + 'Open the chat: ' + link) : '';"""

BV_TRUNC_ANCHOR = """// A4095 (fixwave 4, 2026-08-23). The old guard sliced at exactly 3900 characters, so the three-day
// Centurion digest ended "\u2026Registration: ht\u2026" \u2014 a half-typed URL in the middle of a sentence, which
// reads as a broken answer rather than a shortened one. WhatsApp's 4096-character limit is real and
// the budget does not move; what changes is WHERE the cut lands and that the cut is admitted. Drop
// whole blank-line-separated blocks from the END first (oldest content, each self-contained), then
// fall back to the last line break, and only ever break on whitespace \u2014 never mid-word.
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
    cut = lb > room * 0.5 ? cut.slice(0, lb) : cut.replace(/\\s+\\S*$/, '');
  }
  out = cut.replace(/\\s+$/, '') + note;
}
out += tail;"""

BV_TRUNC_NEW = r"""// A4095 (fixwave 5, 2026-08-23). Wave 4 stopped the mid-URL cut by dropping whole blank-line
// blocks off the END — but the oldest block IS a whole DAY, so a three-day ask headed
// "2026-08-19 to 2026-08-21" delivered 08-21 and 08-20 and silently lost 08-19, then told the
// member to "ask me about one day for the rest". The window the header promises is the answer:
// every requested day has to appear. WhatsApp's 4096 limit is real and the budget does not move,
// so the budget is now split ACROSS the days and each day is trimmed inside itself — whole
// trailing lines (bullets and headings are self-contained), never mid-word.
const NN = NL + NL;
const trimBlock = function (s, budget) {
  if (s.length <= budget) { return s; }
  const mark = NL + '_(trimmed)_';
  const ls = String(s).split(NL);
  while (ls.length > 1 && ls.join(NL).length + mark.length > budget) { ls.pop(); }
  let t = ls.join(NL).replace(/\s+$/, '');
  if (t.length + mark.length > budget) {
    t = t.slice(0, Math.max(0, budget - mark.length)).replace(/\s+\S*$/, '');
  }
  return t + mark;
};
if ((out + dayBlocks.join(NN) + tail).length > 3900) {
  const note = NN + '_Each day is shortened to fit WhatsApp - ask me about one day for the whole thing._';
  const hardRoom = 3900 - out.length - tail.length - note.length;
  const room = hardRoom - (dayBlocks.length - 1) * NN.length;
  // fair share first, then hand the slack the short days did not use to the ones still over
  let share = Math.floor(room / Math.max(1, dayBlocks.length));
  let slack = 0, over = 0;
  dayBlocks.forEach(function (b) { if (b.length < share) { slack += share - b.length; } else { over += 1; } });
  if (over) { share += Math.floor(slack / over); }
  let outBody = dayBlocks
    .map(function (b) { return trimBlock(b, Math.max(200, Math.min(b.length, share))); })
    .join(NN);
  if (outBody.length > hardRoom) {           // last resort (very many days) — line boundary only
    outBody = outBody.slice(0, hardRoom);
    const lb = outBody.lastIndexOf(NL);
    outBody = lb > hardRoom * 0.5 ? outBody.slice(0, lb) : outBody.replace(/\s+\S*$/, '');
  }
  out += outBody.replace(/\s+$/, '') + note;
} else {
  out += dayBlocks.join(NN);
}
out += tail;"""


def transform(nodes):
    seen = {}
    for n in nodes:
        name = n.get("name")
        p = n.get("parameters") or {}

        if name == "Attach Embedding":
            c = p["jsCode"]
            c = sub(c, AE_ANCHOR, AE_NEW, "AE exec-name remap")
            node_check(c, "Attach Embedding")
            p["jsCode"] = c
            seen[name] = True

        elif name == "Answer Merge":
            c = p["jsCode"]
            c = sub(c, AM_FAILNOTE_ANCHOR, AM_FAILNOTE_NEW, "AM CAP const")
            c = sub(c, AM_RESTRICTFN_ANCHOR, AM_RESTRICTFN_NEW, "AM compact head")
            c = sub(c, AM_RESTRICT_ANCHOR, AM_RESTRICT_NEW, "AM compact tail")
            c = sub(c, AM_ERR_ANCHOR, AM_ERR_NEW, "AM error branch")
            c = sub(c, AM_CAP_ANCHOR, AM_CAP_NEW, "AM CAP slice")
            c = sub(c, AM_STAMPS_ANCHOR, AM_STAMPS_NEW, "AM stamps")
            node_check(c, "Answer Merge")
            p["jsCode"] = c
            seen[name] = True

        elif name == "Answer Seed":
            c = p["jsCode"]
            c = sub(c, AS_RESTRICT_ANCHOR, AS_RESTRICT_NEW, "AS rowTrim")
            c = sub(c, AS_COMPARE_ANCHOR, AS_COMPARE_NEW, "AS remindNote tail")
            c = sub(c, AS_FINALUSER_A, AS_FINALUSER_A_NEW, "AS finalUser preload branch")
            c = sub(c, AS_FINALUSER_B, AS_FINALUSER_B_NEW, "AS finalUser bare branch")
            c = sub(c, AS_G6_ANCHOR, AS_G6_NEW, "AS G6 capability rule")
            node_check(c, "Answer Seed")
            p["jsCode"] = c
            seen[name] = True

        elif name == "Answer Parse":
            c = p["jsCode"]
            c = sub(c, AP_ANCHOR, AP_NEW, "AP evParts")
            node_check(c, "Answer Parse")
            p["jsCode"] = c
            seen[name] = True

        elif name == "Gate Verdict":
            c = p["jsCode"]
            c = sub(c, GV_PAIRS_ANCHOR, GV_PAIRS_NEW, "GV #1b pairs")
            c = sub(c, GV_NAMED_ANCHOR, GV_NAMED_NEW, "GV #1b namedInAnswer")
            c = sub(c, GV_HARD_ANCHOR, GV_HARD_NEW, "GV internals hard list")
            c = sub(c, GV_NEWCHECKS_ANCHOR, GV_NEWCHECKS_NEW, "GV claims concat")
            node_check(c, "Gate Verdict")
            p["jsCode"] = c
            seen[name] = True

        elif name == "Plan Request":
            c = p["jsCode"]
            c = sub(c, PR_CONTACT_ANCHOR, PR_CONTACT_NEW, "PR contactAsk")
            c = sub(c, PR_RET1_ANCHOR, PR_RET1_NEW, "PR return 1")
            c = sub(c, PR_RET2_ANCHOR, PR_RET2_NEW, "PR return 2")
            node_check(c, "Plan Request")
            p["jsCode"] = c
            seen[name] = True

        elif name == "Build Verbatim Digest":
            c = p["jsCode"]
            c = sub(c, BV_REFUSE_ANCHOR, BV_REFUSE_NEW, "BV refuse_contact")
            c = sub(c, BV_DAYS_ANCHOR, BV_DAYS_NEW, "BV day blocks")
            c = sub(c, BV_TRUNC_ANCHOR, BV_TRUNC_NEW, "BV truncation")
            node_check(c, "Build Verbatim Digest")
            p["jsCode"] = c
            seen[name] = True

    for want in ("Attach Embedding", "Answer Merge", "Answer Seed", "Answer Parse",
                 "Gate Verdict", "Plan Request", "Build Verbatim Digest"):
        assert seen.get(want), f"node not found in graph: {want}"
    return nodes


POST = [
    ("Attach Embedding", "const ARRAY_ARGS = ['p_terms', 'p_sources', 'p_kinds', 'p_dims', 'p_want'];", 1),
    ("Attach Embedding", "if (want === 'array' && !Array.isArray(v)) {", 1),
    ("Answer Merge", "const FAILNOTE = 'MILLIE \u2014 DETERMINISTIC NOTE: this tool call FAILED.", 1),
    ("Answer Merge", "String(r.message || r.error).slice(0, 400) }) + NL + FAILNOTE;", 1),
    ("Answer Merge", "body = JSON.stringify({ error: String(r.message || r.error).slice(0, 400) });", 0),
    ("Answer Merge", "const restrictFix = function (row) {", 1),
    ("Answer Merge", "    restrictFix(out);", 1),
    ("Answer Merge", "withholding the NAMES here is right and stays", 1),
    ("Answer Merge", "the member scoped this to a CHAT or CHANNEL", 1),
    ("Answer Merge", "the member asked for a LIST, so say HOW MANY", 1),
    ("Answer Merge", "if (body.length > CAP && Array.isArray(r)) {", 1),
    ("Answer Merge", "const cut = Math.max(60, Math.floor(TIER(i) * lim));", 1),
    ("Answer Seed", "out.access_note = ", 1),
    ("Answer Seed", "let compareNote = '';", 1),
    ("Answer Seed", "roleNote + remindNote + compareNote + meCtx", 1),
    ("Answer Seed", "roleNote + remindNote + compareNote + current", 1),
    ("Answer Seed", "or simply answer in the language that was asked", 0),
    ("Answer Seed", "ALWAYS REPLY IN THE LANGUAGE THE MEMBER WROTE IN", 1),
    ("Answer Seed", "A vs EVERYONE-ELSE COMPARISON", 1),
    ("Answer Parse", "let askerEv = '';", 1),
    ("Answer Parse", "const evParts = [askerEv,", 1),
    ("Gate Verdict", "const FLD = /", 1),
    ("Gate Verdict", "evUrls.forEach(function (u) {\n    if (pairs.length >= 60", 0),
    ("Gate Verdict", "const hit = ws.filter(function (w) { return h.indexOf(w) !== -1; }).length;", 0),
    ("Gate Verdict", "const win = Math.max(ws.length * 3, ws.length + 6);", 1),
    ("Gate Verdict", "let _toolWords = [];", 1),
    ("Gate Verdict", "const _attempt0 = ", 1),
    ("Gate Verdict", "policyClaims.push('LANGUAGE:", 1),
    ("Gate Verdict", "policyClaims.push('PLACE COVERAGE:", 1),
    ("Gate Verdict", "const claims = identityClaims.concat(policyClaims, linkClaims, hClaims);", 1),
    ("Plan Request", "const refuseKind = ", 1),
    ("Plan Request", "refuse_kind: refuseKind, refuse_person: refusePerson", 2),
    ("Build Verbatim Digest", "const WHAT = {", 1),
    ("Build Verbatim Digest", "const dayBlocks = rowsUse.map(function (x) {", 1),
    ("Build Verbatim Digest", "_Each day is shortened to fit WhatsApp", 1),
    ("Build Verbatim Digest", "_Shortened to fit WhatsApp - the oldest part is cut.", 0),
    ("Build Verbatim Digest", "const trimBlock = function (s, budget) {", 1),
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

    if "--dry" in sys.argv:
        print("DRY RUN — nothing written.")
        return

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
    print("\nFIXWAVE 5 APPLIED — staging only. Prod", PROD_ID, "untouched.")


if __name__ == "__main__":
    main()
