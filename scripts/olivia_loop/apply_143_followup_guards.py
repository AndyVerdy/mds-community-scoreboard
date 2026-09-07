#!/usr/bin/env python3
"""#143: four deterministic guards on offer binding — apply to STAGING (on top of #174 / #175).

Bank C 6349 (Etienne, 2026-08-04, rows 23044-23047): she offered "Want me to file this as a report so the
team can check…?" in her own words; `ticketYes` needs the seed's exact sentence, so "Yes please" replayed
the billing plan (bank re-run) or produced a claimed "Done — I've filed that" (live). Bank C 6095 shape
(staging 2026-09-07 exec 137656): "Is there any bigger revenue group" echo-bound on the word *revenue*
from her offer line and narrowed the people list instead of answering. Staging exec 137650: "Yes please"
after a billing answer bound to the bold `*$3,615.00*` as an offered item. Staging exec 137667: "the
second one" after a three-video list reached the model unbound.

  Plan Request  isNewQuestion()     the #174 opener guard applied to the echo signal too
                bareOrdinalPick()   "the second one" / "first" / "last" after >=2 offered items -> that item, drill-down
                ticketYes           also fires on pending_offer.kind:'ticket' (her own-words report offer) + a yes
  Format Reply  offerTitlesOf()     bold spans are offered titles only under an offer question, never a number
                ticketOfferLine()   records her own-words report/ticket offer as pending_offer.kind:'ticket'

Offline proof: scripts/olivia_loop/test_143_followup_guards.js <Plan-Request.js> <Format-Reply.js>

  python3 scripts/olivia_loop/apply_143_followup_guards.py --dry-run DIR   # patched nodes -> DIR/<node>.js, no write
  python3 scripts/olivia_loop/apply_143_followup_guards.py                 # edits STAGING, one bounce

Idempotent: a node already carrying the #143 marker is skipped; every `old` must occur exactly once.
Requires the #174 edits to be present (its anchors are #174 lines).
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#143"


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


PR_FUNCS = r"""// #143 FOLLOW-UP GUARDS (bank C 6095 / 6349 + staging 2026-09-07 execs 137650 / 137656 / 137667).
// A message that OPENS a new question is never an acceptance, however many offer words it shares
// with her last line ("Is there any bigger revenue group" echo-bound on *revenue*). Pure function;
// scripts/olivia_loop/test_143_followup_guards.js runs it against this node's own bytes.
function isNewQuestion(msg) {
  return /^(any|anyone|anything|who|whose|whom|when|where|why|how many|how much|how often|is there|are there|do you have|does|did|list|find|search|show me all)\b/i.test(String(msg || '').trim());
}
// A bare ordinal after an offer of n items picks that item ("the second one", "first", "the last
// one", "number 2"); anything with more words around it is left to the named / cue path. -1 = no pick.
function bareOrdinalPick(rawText, n) {
  const t = String(rawText || '').trim().toLowerCase().replace(/[.!?]+$/, '').trim();
  const m = t.match(/^(?:the |number |no\.? |#)?(1st|2nd|3rd|4th|5th|first|second|third|fourth|fifth|last|[1-5])(?: one| video| session| call| item)?(?: please| pls| plz)?$/);
  if (!m || !(n >= 2)) { return -1; }
  const w = m[1];
  const MAP = { '1st': 0, first: 0, '1': 0, '2nd': 1, second: 1, '2': 1, '3rd': 2, third: 2, '3': 2, '4th': 3, fourth: 3, '4': 3, '5th': 4, fifth: 4, '5': 4 };
  const i = w === 'last' ? n - 1 : MAP[w];
  return (typeof i === 'number' && i >= 0 && i < n) ? i : -1;
}
"""

FR_FUNCS = r"""// #143: a bold span is an offered TITLE only when the reply ENDS with an offer question — a bare
// affirmation binds whatever this records, and "*$3,615.00*" was once bound as an offer (exec 137650).
// Numbers, money and percentages never count. Pure function; test_143_followup_guards.js runs it.
function offerTitlesOf(offerText) {
  const text = String(offerText || '').trim();
  const lines = text.split(String.fromCharCode(10)).map(function (l) { return l.trim(); }).filter(Boolean);
  const last = lines.length ? lines[lines.length - 1] : '';
  if (!/\?\s*$/.test(last)) { return []; }
  const out = [];
  (text.match(/\*([^*\n]{6,120})\*/g) || []).forEach(function (s) {
    const t = s.slice(1, -1).trim();
    if (!t || out.indexOf(t) !== -1) { return; }
    if (/^[\s$€£¥\d.,%+\-–—:/]+$/.test(t)) { return; }
    if ((t.match(/[A-Za-z]/g) || []).length < 4) { return; }
    out.push(t);
  });
  return out.slice(0, 12);
}
// #143: her OWN-WORDS offer to file something with the team, on the reply's last line (bank C 6349:
// "Want me to file this as a report so the team can check…?"). Recorded as pending_offer.kind:'ticket'
// so a yes reaches the two-step ticket lane instead of a plan replay or a claimed "Done — I've filed that".
function ticketOfferLine(offerText) {
  const lines = String(offerText || '').trim().split(String.fromCharCode(10)).map(function (l) { return l.trim(); }).filter(Boolean);
  const last = lines.length ? lines[lines.length - 1] : '';
  if (!last) { return false; }
  if (last.toLowerCase().indexOf('open a ticket with the mds team') !== -1) { return true; }
  // question OR statement form ("Let me know if you'd like me to flag that request to them." — staging 137712)
  if (!/\b(want|would you like|shall i|should i|can i|do you want|let me know if|happy to|i can)\b/i.test(last)) { return false; }
  return /\b(file|log|raise|flag|escalate)\b[^.?!]{0,60}\b(report|ticket|issue|request)\b/i.test(last)
    || /\b(open|raise|file)\b[^.?!]{0,30}\b(ticket|issue)\b/i.test(last)
    || /\b(flag|pass|send|report|escalate)\b[^.?!]{0,60}\b(to|with)\s+(the\s+)?(team|them|mds)\b/i.test(last);
}
"""

# Stage 2 (2026-09-07 23:55Z): nodes that already carry the first #143 cut get the widened detector.
UPGRADE = {
    "Format Reply": [
        (r"""  if (last.toLowerCase().indexOf('open a ticket with the mds team') !== -1) { return true; }
  if (!/\?\s*$/.test(last)) { return false; }
  return /\b(want|would you like|shall i|should i|can i|do you want)\b[^?]{0,80}\b(file|open|log|raise|flag|pass|send|report)\b[^?]{0,60}\b(report|ticket|issue|team)\b/i.test(last);
}""",
         r"""  if (last.toLowerCase().indexOf('open a ticket with the mds team') !== -1) { return true; }
  // question OR statement form ("Let me know if you'd like me to flag that request to them." — staging 137712)
  if (!/\b(want|would you like|shall i|should i|can i|do you want|let me know if|happy to|i can)\b/i.test(last)) { return false; }
  return /\b(file|log|raise|flag|escalate)\b[^.?!]{0,60}\b(report|ticket|issue|request)\b/i.test(last)
    || /\b(open|raise|file)\b[^.?!]{0,30}\b(ticket|issue)\b/i.test(last)
    || /\b(flag|pass|send|report|escalate)\b[^.?!]{0,60}\b(to|with)\s+(the\s+)?(team|them|mds)\b/i.test(last);
}"""),
    ],
}

EDITS = {
    "Plan Request": [
        ('// #174 NAMED ITEM = DRILL-DOWN (Andy, prod 2026-09-07 turn 65490 / exec 137515). "Tell me more\n',
         PR_FUNCS + '// #174 NAMED ITEM = DRILL-DOWN (Andy, prod 2026-09-07 turn 65490 / exec 137515). "Tell me more\n'),
        ("const ticketYes = _saidYes && _lastOlivia.toLowerCase().indexOf(TICKET_OFFER_MARK) !== -1 && !!ticketAsk;",
         "// #143: her own-words report offer arrives as pending_offer.kind:'ticket' (Format Reply records it), so a\n"
         "// yes to it takes the two-step ticket lane whatever sentence she used.\n"
         "const _prevOfferKind = (ctx.prev_offer && typeof ctx.prev_offer === 'object') ? String(ctx.prev_offer.kind || '') : '';\n"
         "const ticketYes = (_saidYes && _lastOlivia.toLowerCase().indexOf(TICKET_OFFER_MARK) !== -1 && !!ticketAsk)\n"
         "  || ((_saidYes || bareAffirm) && _prevOfferKind === 'ticket' && !!ticketAsk);"),
        ("  && _poTrim.split(/\\s+/).filter(Boolean).length <= 16 && !/\\?$/.test(_poTrim)",
         "  && _poTrim.split(/\\s+/).filter(Boolean).length <= 16 && !/\\?$/.test(_poTrim) && !isNewQuestion(_poTrim) // #143"),
        ("const _poNamed = namedOfferItem(_po, _poTrim); // #174\n"
         "const offerYes = !!_poN && !ticketYes && !introOfferPending && (_saidYes || bareAffirm || _poEcho || !!_poNamed);",
         "const _poNamed = namedOfferItem(_po, _poTrim); // #174\n"
         "const _poOrd = (_poN >= 2) ? bareOrdinalPick(_poTrim, _poN) : -1; // #143: \"the second one\"\n"
         "const offerYes = !!_poN && !ticketYes && !introOfferPending && (_saidYes || bareAffirm || _poEcho || !!_poNamed || _poOrd >= 0);"),
        ("  // #174: a NAMED item selects itself, whatever quantifier the sentence also carries\n"
         "  if (_poNamed && _poNamed.ids.length) {",
         "  if (_poOrd >= 0) { return [_poOrd]; } // #143: a bare ordinal picks that item\n"
         "  // #174: a NAMED item selects itself, whatever quantifier the sentence also carries\n"
         "  if (_poNamed && _poNamed.ids.length) {"),
        ("  mode: _poNamed ? 'drilldown' : 'accept', // #174\n"
         "  named: _poNamed ? _poNamed.names.slice(0, 4) : []",
         "  mode: (_poNamed || _poOrd >= 0) ? 'drilldown' : 'accept', // #174 · #143 (ordinal)\n"
         "  named: _poNamed ? _poNamed.names.slice(0, 4)\n"
         "    : (_poOrd >= 0 && Array.isArray(_po.items)\n"
         "      ? _po.items.filter(function (it) { return it && it.id === _poIds[_poOrd] && it.name; }).map(function (it) { return it.name; }).slice(0, 1)\n"
         "      : [])"),
    ],
    "Format Reply": [
        ("// #174 NAMING LINES (Andy, prod 2026-09-07 turn 65490). The record below carries ids and bold\n",
         FR_FUNCS + "// #174 NAMING LINES (Andy, prod 2026-09-07 turn 65490). The record below carries ids and bold\n"),
        ("  const isTicket = offerText.toLowerCase().indexOf('open a ticket with the mds team') !== -1;\n"
         "  const isIntro = /would you like me to connect you with one of them\\?/i.test(offerText);\n"
         "  if (!isTicket && !isIntro) {",
         "  const ticketLine = ticketOfferLine(offerText); // #143: her own wording counts too\n"
         "  const isTicket = offerText.toLowerCase().indexOf('open a ticket with the mds team') !== -1 || ticketLine;\n"
         "  const isIntro = /would you like me to connect you with one of them\\?/i.test(offerText);\n"
         "  if (ticketLine && !isIntro) {\n"
         "    pendingOffer = { kind: 'ticket', ids: [], titles: [], nouns: [], count: 0 };\n"
         "  }\n"
         "  if (!isTicket && !isIntro) {"),
        ("    const titles = uniq((offerText.match(/\\*([^*\\n]{6,120})\\*/g) || [])\n"
         "      .map(function (s) { return s.slice(1, -1).trim(); })).slice(0, 12);",
         "    const titles = offerTitlesOf(offerText); // #143: only under an offer question, never a number"),
    ],
}


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def patch(wf):
    changed = []
    for n in wf["nodes"]:
        if n["name"] not in EDITS:
            continue
        code = n["parameters"]["jsCode"]
        if MARK in code:
            ups = UPGRADE.get(n["name"], [])
            hit = [(o, nw) for o, nw in ups if o in code]
            if not hit:
                print(f"  {n['name']}: already carries {MARK} (current cut), skipped")
                continue
            for old, new in hit:
                if code.count(old) != 1:
                    sys.exit(f"ABORT {n['name']}: upgrade anchor found {code.count(old)}x")
                code = code.replace(old, new)
            ok, err = node_check(code)
            if not ok:
                sys.exit(f"ABORT {n['name']}: node --check failed after upgrade\n{err}")
            n["parameters"]["jsCode"] = code
            changed.append(n["name"])
            print(f"  {n['name']}: {MARK} upgraded ({len(hit)} block), node --check OK")
            continue
        if "#174" not in code:
            sys.exit(f"ABORT {n['name']}: #174 not present — apply #174 first")
        for old, new in EDITS[n["name"]]:
            c = code.count(old)
            if c != 1:
                sys.exit(f"ABORT {n['name']}: expected 1 occurrence, found {c}\n  {old[:110]!r}")
            code = code.replace(old, new)
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {n['name']}: node --check failed\n{err}")
        n["parameters"]["jsCode"] = code
        changed.append(n["name"])
        print(f"  {n['name']}: {len(EDITS[n['name']])} replacements, node --check OK")
    return changed


def main():
    dry = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run" else None
    wf = api("GET", f"/workflows/{STAGING_ID}")
    if wf.get("id") != STAGING_ID:
        sys.exit(f"GET failed: {json.dumps(wf)[:300]}")
    print(f"staging {STAGING_ID} versionId {wf.get('versionId')} nodes {len(wf['nodes'])}")
    changed = patch(wf)
    if dry:
        os.makedirs(dry, exist_ok=True)
        for n in wf["nodes"]:
            if n["name"] in EDITS:
                path = os.path.join(dry, n["name"].replace(" ", "_") + ".js")
                open(path, "w").write(n["parameters"]["jsCode"])
                print(f"  wrote {path}")
        print("dry run: nothing written to n8n")
        return
    if not changed:
        print("nothing to do")
        return
    if not set(changed) <= set(EDITS.keys()):
        sys.exit(f"ABORT: unexpected nodes changed: {sorted(changed)}")
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
