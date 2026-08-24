#!/usr/bin/env python3
"""Fixwave 8 — the bank C clusters wave 7 does NOT cover, built from the id-by-id map
(fixmap_bankC_192.json: wave 7 covers 70 of the 192, wave 8 must cover 110).

Kept SEPARATE from wave 7 even though they apply together, so a regression is attributable
to one batch without unpicking the other.

  Answer Merge stamps (CODE — these clusters already had prompt rules that failed, and
  per Andy's "code beats prompt rules" a twice-failed rule moves into the tool):
    S1 · links + dates are ON the evidence (27 fails: "names the members but ships not one link")
    S2 · partner answers must carry the recorded offer + its app.mds.co link (11 fails)
    S3 · a tool that returned rows is never "nothing on file" (7 fails)
    S4 · freshness: name the newest item actually present (15 fails, shares the W8-B cluster)

  Gate Verdict (deterministic, FP-audited over all 602 bank C answers):
    G1 · fake acknowledgement — 2 fires, both real fails, ZERO false positives

  Answer Seed STYLE rules (genuinely new classes with no prior rule):
    R1 wrong referent on follow-up (17) · R2 refusal must name the real gate (11) ·
    R3 no silent narrowing (4) · R4 ask one clarifier instead of guessing (4)

  NOT in this wave, deliberately:
    · the removed-member severe (6080/6272/6277) — the bank C expects ("no profile at all,
      no dates, no link") contradict Andy's recorded 2026-07-26 ruling that past members ARE
      findable, which the leak gate still asserts. Needs Andy, not a guess.

  python3 scripts/olivia_loop/apply_fixwave8_2026-08-24.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)

BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")

def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None: cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code); tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")

def sub(hay, old, new, label):
    assert hay.count(old) == 1, f"anchor drift: {label} ({hay.count(old)}x)"
    return hay.replace(old, new)

def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ---- Answer Seed: four new STYLE rules -------------------------------------------
    seed = nodes["Answer Seed"]; c = seed["parameters"]["jsCode"]
    anchor_seed = ("  'SHARING RULE (Andy 2026-08-24): if the asker could find it themselves - it is "
                   "public, or it lives in a chat they belong to - you may share it, whatever kind of "
                   "info it is, contact details and self-stated revenue included.")
    assert c.count(anchor_seed) == 1, "seed SHARING RULE anchor drift"
    tail_start = c.index(anchor_seed)
    tail_end = c.index("\n].join(NL);", tail_start)
    sharing_rule = c[tail_start:tail_end]
    new_rules = sharing_rule + """
  'ANSWER THE THING ON THE TABLE. When the member says yes, "that one", "the second", "those", or corrects you, the subject is whatever YOU just put in front of them - not the newest item you can find and not a fresh search. Re-read your own previous turn, name that same subject back, and answer about IT. If their reply is a correction ("no, the Facebook one"), re-check THAT source before answering - never re-serve the same list with an excuse. If you genuinely cannot tell which item they mean, name the two candidates and ask which - never silently pick one.',
  'A REFUSAL NAMES THE REAL GATE. Never say a thing is "not something I share" as a blanket. Either you are holding it for a specific reason - they are not registered for that event, they are not in that chat, it is a private field - and you say WHICH, or the data simply is not on file and you say that instead. Never imply a status change will unlock something unless that single change is genuinely the only thing holding it, and if more than one gate is shut, say so. A correct refusal is specific; a vague one reads as a brush-off.',
  'NEVER NARROW A QUESTION SILENTLY. If they asked about the whole community and you can only answer for one chat, one event or one slice, say which slice you answered and what the wider picture would need. Give the real count for the population you actually used, and use the SAME population for every number in the reply - never quote 88 for a headcount and 87 for the percentage of the same group. If you cannot answer for the population they asked about, say that plainly instead of quietly answering a smaller one.',
  'ASK ONE CLARIFIER INSTEAD OF GUESSING. When the ask genuinely has two readings and the answers differ - a word that names both a person and a brand, "the change" with two changes in play, an ambiguous pronoun - ask ONE short question and stop. Do not guess the reading and answer at length, and do not ask a clarifier you can resolve yourself from the evidence in front of you. One question, then wait.',"""
    c = sub(c, sharing_rule, new_rules, "seed wave-8 STYLE rules")
    node_check(c, "Answer Seed"); seed["parameters"]["jsCode"] = c

    # ---- Answer Merge: four evidence-driven stamps -----------------------------------
    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]
    anchor_m = "    // The member's literal message — several stamps below need to know what was actually asked."
    stamps = """    // fixwave 8 (bank C): four stamps read off the EVIDENCE, not off phrasing. Each of these
    // clusters already had a STYLE rule that failed in the run, so per "code beats prompt rules"
    // the fact moves into the payload where the model cannot overlook it.
    try {
      const _p8 = (() => { try { return JSON.parse(body); } catch (e) { return null; } })();
      const _arr8 = Array.isArray(_p8) ? _p8
        : (_p8 && typeof _p8 === 'object'
            ? (['items','rows','posts','videos','results','people','members','partners','messages']
                .map(k => Array.isArray(_p8[k]) ? _p8[k] : null).filter(Boolean)[0] || null)
            : null);
      if (_arr8 && _arr8.length) {
        const DATEK = ['occurred_at','posted_at','created_at','date','sent_at','recorded_at','starts_at','published_at'];
        const _url = _arr8.filter(x => x && typeof x === 'object'
          && Object.keys(x).some(k => /(^|_)url$|link$|permalink/i.test(k) && x[k])).length;
        const _dated = _arr8.filter(x => x && typeof x === 'object'
          && DATEK.some(k => x[k])).length;
        // S1 — the single biggest cluster (27 of 192): items were named with no link and no date
        // while both sat in this payload.
        if (_url || _dated) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: of the ' + _arr8.length
            + ' items here, ' + _url + ' carry a link and ' + _dated + ' carry a date. Every item you '
            + 'cite must go out with ITS OWN link and ITS OWN date, taken from this payload — not the '
            + 'first item\\'s link reused, not a group/root URL standing in for a specific post. If an '
            + 'item you want to cite has neither, either cite one that does or say plainly that this '
            + 'one is undated/unlinked. Never present a list where only some entries are traceable.';
        }
        // S3 — "nothing on file" while the tool returned rows (7 of 192).
        body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this tool returned ' + _arr8.length
          + ' row(s). Do NOT answer that there is nothing on file, that you could not find anything, '
          + 'or that coverage is empty for this ask. If these rows are the wrong ones, say what they '
          + 'are and what is missing — never report them as nothing.';
        // S4 — freshness: name the newest thing actually present (part of the 15-fail cluster).
        const _dates8 = _arr8.map(x => {
          if (!x || typeof x !== 'object') return null;
          const k = DATEK.filter(k => x[k])[0]; return k ? String(x[k]).slice(0, 10) : null;
        }).filter(Boolean).sort();
        if (_dates8.length) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: the newest item here is dated '
            + _dates8[_dates8.length - 1] + ' and the oldest ' + _dates8[0]
            + '. If the member asked about a period ("last 6 months", "recently", "this week"), say '
            + 'which window these actually cover — never imply coverage past ' + _dates8[_dates8.length - 1] + '.';
        }
        // S2 — partner answers must carry the recorded offer AND its app.mds.co link (11 of 192).
        const _off8 = _arr8.filter(x => x && typeof x === 'object'
          && Object.keys(x).some(k => /offer|deal|discount|promo|benefit/i.test(k) && x[k])).length;
        if (_off8) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: ' + _off8 + ' of these carry a recorded '
            + 'MDS offer. When the member is looking for help this partner covers, give the offer in '
            + 'the partner\\'s own words AND its partner-page link — a partner named without its deal '
            + 'is an incomplete answer, and "members get a discount" is not the deal. If a partner '
            + 'here has no recorded offer, say so rather than implying one.';
        }
      }
    } catch (e) {}
"""
    cm = sub(cm, anchor_m, stamps + anchor_m, "merge wave-8 stamps")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    # ---- Gate Verdict: G1 fake acknowledgement --------------------------------------
    # FP-audited over all 602 bank C answers: 2 fires, BOTH real fails (6097, 6424), 0 FPs.
    gv = nodes["Gate Verdict"]; cg = gv["parameters"]["jsCode"]
    anchor_g = "if (!claims.length) {"
    assert cg.count(anchor_g) == 1, "gate anchor drift"
    g1 = """// fixwave 8 (G1) — FAKE ACKNOWLEDGEMENT. She opened turns with "Yep, got it — I can see it!"
// when nothing had arrived (6424), and conceded an error she never made while repeating the same
// claim (6097). Both read as pretending. Audited over all 602 bank C answers: this pattern fires
// twice and both are real fails — zero false positives — so it regenerates rather than warns.
const FAKE_ACK_RE = /\\byep,? got it\\b|\\bi can see it\\b|you'?re right,? sorry|sorry for the confusion/i;
try {
  if (FAKE_ACK_RE.test(String(answerText || ''))) {
    claims.push('FAKE ACKNOWLEDGEMENT: the draft claims to have received, seen or already handled '
      + 'something, or concedes a mistake, when nothing in this turn supports that. Drop the '
      + 'acknowledgement and answer only from what is actually here.');
  }
} catch (e) {}

"""
    cg = sub(cg, anchor_g, g1 + anchor_g, "gate G1 fake-ack")
    node_check(cg, "Gate Verdict"); gv["parameters"]["jsCode"] = cg

    if dry:
        print("DRY RUN — all anchors hit, node --check clean on 3 nodes.")
        return

    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    n2 = {n["name"]: n for n in after["nodes"]}
    assert "ANSWER THE THING ON THE TABLE" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "fixwave 8 (bank C)" in n2["Answer Merge"]["parameters"]["jsCode"]
    assert "FAKE_ACK_RE" in n2["Gate Verdict"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
