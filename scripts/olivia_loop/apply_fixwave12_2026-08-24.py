#!/usr/bin/env python3
"""Fixwave 12 — the clusters still failing after waves 7-11 (94/169 = 56% passing).

Built from hand-grading all 169 re-run answers, not from the original grader notes.

  S6 · TOOL ERROR IS NOT "NOTHING ON FILE" (the canned-clamp class, 8 of 75 fails).
       "I looked into that, but I couldn't verify enough..." is the Gate Verdict's hard-stop
       after 2 failed regenerations. Re-probing those questions live answers them correctly, so
       the block is INTERMITTENT — a tool that timed out or errored yields empty evidence, the
       draft cannot be supported, the gate blocks twice, and the member gets a canned non-answer
       for a question Millie can actually answer. Answer Merge already stamps `tool_error` into
       the body; nothing ever told her what to DO with it. Now it does, and it must never be
       reported as an absence.

  S7 · A PEOPLE LIST STATES ITS TRUE TOTAL, or says plainly it cannot (7 fails: 6078, 6079,
       6318, 6503, 6217, 6274-class). "here are 10, likely more out there" is not a total.
       member_match_v2 returns rows with no count, so when the payload cannot support a total
       she must say the list is a sample and offer to narrow — never imply completeness and
       never invent "likely more".

  R5 · THE CAPABILITY CARD IS FOR A FIRST HELLO ONLY (6002, 6190). "What data do you have?" and
       "what data points do you have" both got the welcome menu instead of an honest inventory.

  R6 · NEVER NARRATE A FAILING LOOKUP (6024 said "the search itself is glitching"; 6275 named
       the internal `find` filter to a member).

  R7 · SENSITIVE: a death or an allegation is not restated, sourced or linked (6288, 6289 both
       refused in words and then linked the thread anyway).

  G2 · the fake-acknowledgement gate missed "Yep, I did see it!" (6424) and "Yep, that's
       confirmed real ... I'd already replied to him" (6425). Widened, re-audited.

  python3 scripts/olivia_loop/apply_fixwave12_2026-08-24.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="): return l.split("=", 1)[1].strip()
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

    # ---- Answer Merge: S6 tool-error honesty + S7 no-total honesty -------------------
    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]
    anchor = """        // S5 (fixwave 10) — a people list handed back AT the cap is a SAMPLE, not the set, and"""
    stamps = """        // S7 (fixwave 12) — a people list with no count field in the payload cannot state a true
        // total, and "here are 10, likely more out there" is a guess dressed as one. Say it is a
        // sample and offer to narrow; never imply the list is everyone.
        const _ppl12 = _arr8.filter(x => x && typeof x === 'object' && (x.full_name || x.name));
        const _hasTotal = _p8 && typeof _p8 === 'object' && !Array.isArray(_p8)
          && ['total','matched_total','total_going','count'].some(k => _p8[k] != null);
        if (_ppl12.length >= 3 && !_hasTotal) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this payload carries ' + _ppl12.length
            + ' people and NO total count. You therefore do not know how many match overall. Say '
            + 'plainly that this is a sample of who matched (not the full set) and offer to narrow '
            + 'by niche, city or chapter. Do NOT state or estimate a total, and do not write '
            + '"likely more" as if it were one.';
        }
"""
    cm = sub(cm, anchor, stamps + anchor, "merge S7 no-total stamp")

    err_anchor = """    // The member's literal message — several stamps below need to know what was actually asked."""
    err_stamp = """    // S6 (fixwave 12) — A TOOL ERROR IS NOT AN ABSENCE. Answer Merge already stamps tool_error
    // into the body when a call fails or times out, but nothing told her how to report it, so a
    // failed lookup read to her exactly like "nothing on file" — and the draft that followed could
    // not be supported, the gate blocked it twice, and the member got the canned "I couldn't
    // verify enough" for a question she can actually answer (proved by re-probing those questions
    // live, where they answer correctly). This is the timeout-looks-like-no-data trap.
    try {
      const _err12 = (() => { try { const b = JSON.parse(body); return b && b.tool_error === true ? b : null; } catch (e) { return null; } })();
      if (_err12) {
        body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this lookup FAILED — it did not come back '
          + 'empty, it errored. You do NOT know whether anything is on file. Never say there is '
          + 'nothing on file, that you found nothing, or that coverage is empty on the strength of '
          + 'this. Say plainly that the lookup did not come back this time and offer to try again, '
          + 'and answer from any OTHER evidence in this turn that did succeed.';
      }
    } catch (e) {}
"""
    cm = sub(cm, err_anchor, err_stamp + err_anchor, "merge S6 tool-error stamp")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    # ---- Answer Seed: R5 welcome card · R6 no failing-lookup narration · R7 sensitive -
    seed = nodes["Answer Seed"]; cs = seed["parameters"]["jsCode"]
    anchor_s = """  'ASK ONE CLARIFIER INSTEAD OF GUESSING - BUT ONLY WHEN THE EVIDENCE CANNOT SETTLE IT."""
    rules = """  'THE CAPABILITY CARD IS A FIRST HELLO, NOT AN ANSWER. If someone asks what data you have, what you can see, what your sources are, or what you know - that is a real question and it wants a real inventory: the chats THEY are in (chats are scoped to them, everything else is community-wide), the Facebook group, member profiles, events, partner deals, the video library and its year boundary, forms. Say what is thin and what you cannot reach. Never answer it with the greeting menu of example prompts.',
  'NEVER NARRATE A LOOKUP, WORKING OR BROKEN. Do not tell a member a search is glitching, slow, not going through, or came back oddly, and never name an internal filter or tool. If a lookup failed, say you could not get it this time and offer to retry - that is the whole sentence.',
  'SENSITIVE - A DEATH, A CRIME OR AN ALLEGATION IS NOT YOURS TO CARRY. If a question involves someone dying, being accused, arrested, sued or called a scammer, you do not confirm it, deny it, repeat what was said, name who said it, or link the thread - not even to be helpful, and not even when the member clearly already knows. One plain line that it is not yours to speak to, and stop. Linking the post IS restating it.',
"""
    cs = sub(cs, anchor_s, rules + anchor_s, "seed wave-12 rules")
    node_check(cs, "Answer Seed"); seed["parameters"]["jsCode"] = cs

    # ---- Gate Verdict: G2 widen fake-ack ---------------------------------------------
    gv = nodes["Gate Verdict"]; cg = gv["parameters"]["jsCode"]
    old_g = """const FAKE_ACK_RE = /\\byep,? got it\\b|\\bi can see it\\b|(sorry|apologi[sz]e[sd]?|my apologies)[^.!?]{0,30}\\bconfusion\\b|\\bmy mistake\\b/i;"""
    new_g = """// fixwave 12 (G2): 6424 opened "Yep, I did see it!" and 6425 "Yep, that's confirmed real …
// I'd already replied to him directly" — both claim an action or a sighting nothing supports, and
// both walked past the wave-9 pattern. Now matches the CLAIM shape (yep/yes + saw/got/received,
// and "I already replied/answered"), not one fixed phrase. Re-audited over all 602 bank C answers.
const FAKE_ACK_RE = /\\byep,? (got it|i did|that's)\\b|\\bi (can|did) see it\\b|(sorry|apologi[sz]e[sd]?|my apologies)[^.!?]{0,30}\\bconfusion\\b|\\bmy mistake\\b|\\bi(?:'ve|'d| had| have)? ?already (replied|responded|answered)\\b/i;"""
    cg = sub(cg, old_g, new_g, "gate G2 pattern")
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
    assert "S6 (fixwave 12)" in n2["Answer Merge"]["parameters"]["jsCode"]
    assert "S7 (fixwave 12)" in n2["Answer Merge"]["parameters"]["jsCode"]
    assert "CAPABILITY CARD IS A FIRST HELLO" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "fixwave 12 (G2)" in n2["Gate Verdict"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
