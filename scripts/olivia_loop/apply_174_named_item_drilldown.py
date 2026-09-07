#!/usr/bin/env python3
"""#174: a named item from her own list is a DRILL-DOWN, not a new search — apply to STAGING.

Andy, prod 2026-09-07 20:47Z (turns 65488-65491, execs 137508 / 137515): a four-video answer, then
"Tell me more about Alex Chiru video". Prep Context handed Plan Request the recorded offer (four
ids, titles, the offer word "further"), the router said accepts_offer:false, and the three
acceptance signals (router yes · bare affirmation · echo of her offer word) never covered a member
NAMING one of the items — so offer_bind stayed null, the videos lane ran `video_search "alex chiru"`,
and the model wrote another list. Three additive edits, one graph:

  Format Reply  — offerItemsOf(): pending_offer.items = the line she wrote above each video link
                  (title + speaker as the member saw it). Save Conversation and Prep Context already
                  carry the whole pending_offer object, so nothing else moves.
  Plan Request  — namedOfferItem(): fourth acceptance signal. A message of <=16 words that names an
                  offered item by a capitalised word of its line (speaker, product, title word), with
                  a drill-down cue or two such words and no new-question opener, binds to THAT item.
                  The existing bound path then does the rest (zeroth fetch video_search p_video_id,
                  no topic search). offer_bind gains mode:'drilldown' + named[].
  Answer Seed   — DRILL-DOWN variant of the OFFER ACCEPTED block: one item, deliver its substance.

Offline proof: scripts/olivia_loop/test_174_named_item.js <Format-Reply.js> <Plan-Request.js>

  python3 scripts/olivia_loop/apply_174_named_item_drilldown.py --dry-run DIR   # patched nodes -> DIR/<node>.js, no write
  python3 scripts/olivia_loop/apply_174_named_item_drilldown.py                 # edits STAGING, one bounce

Idempotent: a node already carrying the #174 marker is skipped; every `old` must occur exactly once.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#174"


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


FR_FUNC = r"""// #174 NAMING LINES (Andy, prod 2026-09-07 turn 65490). The record below carries ids and bold
// titles; "Tell me more about Alex Chiru video" names the SPEAKER, which lives only in the line she
// wrote for that video. Record that line for each offered video — the URL's own prose, else the
// nearest non-empty non-URL line above it — so Plan Request can bind a NAMED item on the next turn.
// Pure function; scripts/olivia_loop/test_174_named_item.js runs it against this node's own bytes.
function offerItemsOf(offerText, vids) {
  const out = [];
  const lines = String(offerText || '').split(String.fromCharCode(10));
  const clean = function (s) {
    return String(s || '').replace(/https?:\/\/\S+/g, ' ').replace(/\*/g, '')
      .replace(/^[\s\u2022\u00b7\-\u2013\u2014*]+/, '').replace(/[\s:\-\u2013\u2014]+$/, '')
      .replace(/\s+/g, ' ').trim().slice(0, 160);
  };
  (Array.isArray(vids) ? vids : []).forEach(function (id) {
    const key = 'app.mds.co/videos/' + String(id).toLowerCase();
    let li = -1;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().indexOf(key) !== -1) { li = i; break; }
    }
    if (li < 0) { return; }
    let name = clean(lines[li]);
    if (name.length < 6) {
      name = '';
      for (let j = li - 1; j >= 0 && j >= li - 3; j--) {
        const t = lines[j].trim();
        if (!t) { continue; }
        if (/^https?:\/\//.test(t)) { break; }
        name = clean(t);
        break;
      }
    }
    if (name.length >= 6) { out.push({ id: String(id).toLowerCase(), name: name }); }
  });
  return out;
}
"""

PR_FUNC = r"""// #174 NAMED ITEM = DRILL-DOWN (Andy, prod 2026-09-07 turn 65490 / exec 137515). "Tell me more
// about Alex Chiru video" one turn after a four-video list was re-planned as a fresh speaker search:
// the three signals below (router yes, bare affirmation, echo of her offer word) never covered a
// member NAMING one of the items. Format Reply now records the line she wrote for each video
// (pending_offer.items); a short message naming one of them by a capitalised word of its line — a
// speaker, a product, a title word — binds to THAT item. Precision over recall: it needs a
// drill-down cue (more / about / summary / cover ...) or two such words, a new-question opener
// (any / who / when / how many / is there ...) always wins, and a single word shared by several
// items binds nothing. Two items matched by the same two-plus words both bind; the seed asks which.
// Pure function; scripts/olivia_loop/test_174_named_item.js runs it against this node's own bytes.
function namedOfferItem(po, rawText) {
  const items = (po && Array.isArray(po.items)) ? po.items.filter(function (it) { return it && it.id && it.name; }) : [];
  const msg = String(rawText || '').trim();
  if (!items.length || !msg) { return null; }
  if (msg.split(/\s+/).filter(Boolean).length > 16) { return null; }
  if (/^(any|anyone|anything|who|whose|whom|when|where|why|how many|how much|how often|is there|are there|do you have|does|did|list|find|search|show me all)\b/i.test(msg)) { return null; }
  const norm = function (w) { return String(w).toLowerCase().replace(/[\u2019']s$/, '').replace(/[^a-z0-9]+/g, ''); };
  const SKIP = { the: 1, and: 1, for: 1, with: 1, from: 1, into: 1, jan: 1, feb: 1, mar: 1, apr: 1, may: 1, jun: 1, jul: 1,
    aug: 1, sep: 1, sept: 1, oct: 1, nov: 1, dec: 1, january: 1, february: 1, march: 1, april: 1, june: 1, july: 1,
    august: 1, september: 1, october: 1, november: 1, december: 1, monday: 1, tuesday: 1, wednesday: 1, thursday: 1,
    friday: 1, saturday: 1, sunday: 1, mogul: 1, call: 1, calls: 1, summit: 1, inspire: 1, mastermind: 1, channel: 1,
    chapter: 1, expert: 1, hot: 1, seat: 1, town: 1, hall: 1, video: 1, videos: 1, session: 1, sessions: 1,
    recording: 1, recap: 1, webinar: 1, mds: 1 };
  const STARTER = { how: 1, what: 1, why: 1, when: 1, where: 1, who: 1, the: 1, this: 1, that: 1, these: 1, those: 1,
    watch: 1, here: 1, want: 1, see: 1, tell: 1, read: 1, listen: 1, best: 1, top: 1, more: 1, new: 1, latest: 1,
    plus: 1, also: 1, and: 1, but: 1, for: 1, from: 1, in: 1, on: 1, at: 1, with: 1, a: 1, an: 1 };
  const msgSet = {};
  msg.replace(/[\u2019']s\b/g, '').toLowerCase().split(/[^a-z0-9]+/).forEach(function (w) { if (w.length >= 3) { msgSet[w] = 1; } });
  const hits = items.map(function (it, i) {
    const toks = String(it.name).match(/[A-Za-z][A-Za-z\u2019']*/g) || [];
    const seen = {};
    let n = 0;
    toks.forEach(function (t, k) {
      if (!/^[A-Z]/.test(t)) { return; }
      const w = norm(t);
      if (w.length < 3 || SKIP[w] || seen[w]) { return; }
      if (k === 0 && STARTER[w]) { return; }
      seen[w] = 1;
      if (msgSet[w]) { n += 1; }
    });
    return { i: i, n: n };
  }).filter(function (h) { return h.n > 0; });
  if (!hits.length) { return null; }
  const best = Math.max.apply(null, hits.map(function (h) { return h.n; }));
  const pick = hits.filter(function (h) { return h.n === best; });
  if (best < 2 && pick.length > 1) { return null; }
  if (pick.length > 2) { return null; }
  const cue = /\b(more|about|summar\w*|details?|cover\w*|expand|elaborate|explain|recap|takeaways?|tell me|what\W?s in|that one|this one|the \S+ one|the one)\b/i.test(msg);
  if (!cue && best < 2) { return null; }
  return { ids: pick.map(function (h) { return items[h.i].id; }), names: pick.map(function (h) { return items[h.i].name; }) };
}
"""

SEED_DRILL = (
    "    const named = (ob && Array.isArray(ob.named)) ? ob.named.filter(Boolean) : [];\n"
    "    if (ob.mode === 'drilldown' && obIds.length) {\n"
    "      // #174 (Andy, prod 2026-09-07 turn 65490): the member NAMED one of the offered items - this is the\n"
    "      // summary request, not an acceptance to re-offer. One item, its substance, its one link.\n"
    "      offer_ctx = 'DRILL-DOWN (deterministic - the member just NAMED ' + (obIds.length > 1 ? 'items' : 'one item')\n"
    "        + ' your PREVIOUS message put in front of them, recorded on that turn): '\n"
    "        + (named.length ? named.join(' | ') : obTitles.join(' | ')) + ' - id' + (obIds.length > 1 ? 's ' : ' ') + obIds.join(', ')\n"
    "        + '. This IS the summary request: do not offer a summary, DELIVER it. Call video_search with p_video_id for '\n"
    "        + (obIds.length > 1 ? 'each id' : 'that id') + ' and answer from that row: what the session covers, the three or four'\n"
    "        + ' takeaways that matter for what this member asked earlier in this conversation, who spoke, when it ran and how'\n"
    "        + ' long it is - then its ONE library link. This drill-down may run to about 1200 characters. Do NOT list other'\n"
    "        + ' videos, do NOT run a fresh topic search, do NOT ask which one when a single id is listed. Two ids listed ='\n"
    "        + ' their words fit both: name both in one line and ask which.';\n"
    "    } else\n"
)

EDITS = {
    "Format Reply": [
        ("let pendingOffer = null;\n",
         FR_FUNC + "let pendingOffer = null;\n"),
        ("        ids: ids, titles: titles, nouns: nouns, count: (ids.length || titles.length) };",
         "        ids: ids, titles: titles, nouns: nouns, count: (ids.length || titles.length),\n"
         "        items: offerItemsOf(offerText, vids) };"),
    ],
    "Plan Request": [
        ("const _po = (ctx.prev_offer && typeof ctx.prev_offer === 'object') ? ctx.prev_offer : null;",
         PR_FUNC + "const _po = (ctx.prev_offer && typeof ctx.prev_offer === 'object') ? ctx.prev_offer : null;"),
        ("const offerYes = !!_poN && !ticketYes && !introOfferPending && (_saidYes || bareAffirm || _poEcho);",
         "const _poNamed = namedOfferItem(_po, _poTrim); // #174\n"
         "const offerYes = !!_poN && !ticketYes && !introOfferPending && (_saidYes || bareAffirm || _poEcho || !!_poNamed);"),
        ("  const t = _poTrim.toLowerCase();\n"
         "  const all = []; for (let i = 0; i < _poN; i++) { all.push(i); }\n"
         "  if (!_poN) { return all; }",
         "  const t = _poTrim.toLowerCase();\n"
         "  const all = []; for (let i = 0; i < _poN; i++) { all.push(i); }\n"
         "  if (!_poN) { return all; }\n"
         "  // #174: a NAMED item selects itself, whatever quantifier the sentence also carries\n"
         "  if (_poNamed && _poNamed.ids.length) {\n"
         "    const _ni = _poNamed.ids.map(function (id) { return _poIds.indexOf(id); }).filter(function (i) { return i >= 0; });\n"
         "    if (_ni.length) { return _ni; }\n"
         "  }"),
        ("  offered: _poN\n} : null;",
         "  offered: _poN,\n"
         "  mode: _poNamed ? 'drilldown' : 'accept', // #174\n"
         "  named: _poNamed ? _poNamed.names.slice(0, 4) : []\n"
         "} : null;"),
    ],
    "Answer Seed": [
        ("    const n = obIds.length || obTitles.length;\n"
         "    offer_ctx = 'OFFER ACCEPTED (deterministic \u2014 these are the items your PREVIOUS message put in '",
         "    const n = obIds.length || obTitles.length;\n"
         + SEED_DRILL +
         "    offer_ctx = 'OFFER ACCEPTED (deterministic \u2014 these are the items your PREVIOUS message put in '"),
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
            print(f"  {n['name']}: already carries {MARK}, skipped")
            continue
        for old, new in EDITS[n["name"]]:
            c = code.count(old)
            if c != 1:
                sys.exit(f"ABORT {n['name']}: expected 1 occurrence, found {c}\n  {old[:100]!r}")
            code = code.replace(old, new)
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {n['name']}: node --check failed\n{err}")
        n["parameters"]["jsCode"] = code
        changed.append(n["name"])
        print(f"  {n['name']}: {len(EDITS[n['name']])} replacements, node --check OK")
    return changed


def main():
    dry = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run":
        dry = sys.argv[2]
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
    if sorted(changed) != sorted(EDITS.keys()):
        sys.exit(f"ABORT: expected {sorted(EDITS.keys())} changed, got {sorted(changed)}")
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
