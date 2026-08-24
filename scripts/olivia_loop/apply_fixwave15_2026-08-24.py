#!/usr/bin/env python3
"""Fixwave 15 — the three largest remaining groups after wave 12 (59 fails left).

  S8 · STATE THE TRUE TOTAL. #134 just added matched_total to member_match_v2 (count(*) over (),
       computed before the LIMIT, so it is the real size of the match set — Austin 13, Miami 20,
       verified against ground truth). Wave 12's S7 told her to say "this is a sample" precisely
       BECAUSE no total existed; now one does, so she must give it: "here are 10 of 13". Seven
       fails hung on this (6217, 6078, 6094, 6301, 6318, 6503, 6460).

  G3 · fake acknowledgement, third pass. 6424 opened "Yep, saw it!" and 6425 "Yep, that response
       already went out to Oleg" — both slipped past wave 12's pattern, which knew "yep, got it",
       "yep, i did" and "yep, that's". Matching the SHAPE now: yep/yes + any perception or
       delivery verb. Re-audited over all 602.

  R8 · sensitive, second pass. Wave 12 stopped her LINKING a death thread; she still named who
       posted it and when ("shared by Mehmet Demirel back on July 18") and quoted a condolence.
       Naming the source is restating it.

  python3 scripts/olivia_loop/apply_fixwave15_2026-08-24.py [--dry]
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

    # ---- S8: state the true total, now that the payload carries one -----------------
    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]
    anchor = """        // S7 (fixwave 12) — a people list with no count field in the payload cannot state a true"""
    s8 = """        // S8 (fixwave 15) — the payload NOW carries the real total (#134 added matched_total to
        // member_match_v2, a window count taken before the cap). So the honest line is no longer
        // "this is a sample" — it is the actual number. This is the single biggest remaining
        // cluster: seven answers said "here are 10, likely more out there" with the true figure
        // sitting one field away.
        const _tot15 = (() => {
          const r0 = _arr8.find(x => x && typeof x === 'object' && x.matched_total != null);
          return r0 ? Number(r0.matched_total) : null;
        })();
        if (_tot15 != null && _arr8.length) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: ' + _tot15 + ' people match this in total'
            + (_tot15 > _arr8.length
                ? ' and you have been handed ' + _arr8.length + '. Say BOTH in plain words — "here are '
                  + _arr8.length + ' of ' + _tot15 + '" — and offer to narrow.'
                : ' and you have all of them. Say the number.')
            + ' Use THIS figure exactly; never round it, never say "likely more", and never imply '
            + 'the list is everyone when it is not.';
        }
"""
    cm = sub(cm, anchor, s8 + anchor, "merge S8 true-total stamp")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    # ---- R8: sensitive, do not name the source either --------------------------------
    seed = nodes["Answer Seed"]; cs = seed["parameters"]["jsCode"]
    old_r7 = "'SENSITIVE - A DEATH, A CRIME OR AN ALLEGATION IS NOT YOURS TO CARRY. If a question involves someone dying, being accused, arrested, sued or called a scammer, you do not confirm it, deny it, repeat what was said, name who said it, or link the thread - not even to be helpful, and not even when the member clearly already knows. One plain line that it is not yours to speak to, and stop. Linking the post IS restating it.',"
    new_r7 = "'SENSITIVE - A DEATH, A CRIME OR AN ALLEGATION IS NOT YOURS TO CARRY. If a question involves someone dying, being accused, arrested, sued or called a scammer, you do not confirm it, deny it, repeat what was said, name who said it or when, quote anyone about it, or link the thread - not even to be helpful, and not even when the member clearly already knows, and not as the second half of a sentence that began with a refusal. Naming the person who posted it, or the date, IS restating it, and so is \"others shared condolences\". The ENTIRE answer is one plain line that this is not yours to speak to, plus - only if it helps - who they could ask instead. Then stop.',"
    cs = sub(cs, old_r7, new_r7, "seed R8 sensitive")
    node_check(cs, "Answer Seed"); seed["parameters"]["jsCode"] = cs

    # ---- G3: fake acknowledgement, by shape ------------------------------------------
    gv = nodes["Gate Verdict"]; cg = gv["parameters"]["jsCode"]
    old_g = """const FAKE_ACK_RE = /\\byep,? (got it|i did|that's)\\b|\\bi (can|did) see it\\b|(sorry|apologi[sz]e[sd]?|my apologies)[^.!?]{0,30}\\bconfusion\\b|\\bmy mistake\\b|\\bi(?:'ve|'d| had| have)? ?already (replied|responded|answered)\\b/i;"""
    new_g = """// fixwave 15 (G3): third pass. "Yep, saw it!" (6424) and "Yep, that response already went out
// to Oleg" (6425) both slipped the wave-12 list, which knew only three yep-forms. Matched by SHAPE
// now — an affirmative opener followed by any perception or delivery verb — rather than by
// enumerating phrasings, which has now failed twice. "got it" was tried and REJECTED by the
// audit: it false-fired on 6068, "Yep, I've got it - I search the MDS Facebook group...", where
// it means understood, not received. Re-audited: 2 fires, both real fails, zero false positives.
const FAKE_ACK_RE = /\\b(yep|yes|yeah)\\b[^.!?]{0,25}\\b(saw it|see it|received|came through|went out|already (sent|replied|responded|answered))\\b|\\bi (can|did) see it\\b|(sorry|apologi[sz]e[sd]?|my apologies)[^.!?]{0,30}\\bconfusion\\b|\\bmy mistake\\b|\\bi(?:'ve|'d| had| have)? ?already (replied|responded|answered)\\b/i;"""
    cg = sub(cg, old_g, new_g, "gate G3 pattern")
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
    assert "S8 (fixwave 15)" in n2["Answer Merge"]["parameters"]["jsCode"]
    assert "fixwave 15 (G3)" in n2["Gate Verdict"]["parameters"]["jsCode"]
    assert "Naming the person who posted it" in n2["Answer Seed"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
