#!/usr/bin/env python3
"""Fixwave 9 — the bugs the 50-question tranche exposed in waves 7 and 8 themselves.

The tranche fixed 23/50. The misses were not mostly bad rules — they were rules that
NEVER EXECUTED. Two mechanical faults, both in Answer Merge:

  M1 · EVERY stamp parses the already-truncated `body`.
       Order of operations in Answer Merge is: build `body` -> squeeze rows -> blunt-slice at
       CAP (26000) -> then the stamps run `JSON.parse(body)`. On any payload over CAP the blunt
       slice leaves invalid JSON, the parse throws, and the stamp silently no-ops. So wave 7's
       names-cap stamp and ALL FOUR wave-8 stamps only ever fired on SMALL results — while the
       cases they exist for (an 11-name list, a long partner set, a big post list) are precisely
       the large ones. Measured: counts/cap 0/3, freshness 1/4, partner 1/3 in the tranche.
       FIX: stamps read the ORIGINAL object `r`, which is in scope and never truncated.

  M2 · clipSafe covers the first-pass trim but NOT the large-payload path.
       clipSafe() is correctly wired into rowTrim/compact, which is why ellipsis URLs improved
       4 -> 3. But when body exceeds CAP the halving squeeze re-serialises every row with a raw
       `v.slice(0, cut) + '…'`, and the final backstop blunt-slices the whole string. Both cut
       mid-URL, which is the surviving ellipsis-link source (6378, 6428).
       FIX: the squeeze never touches a url/link-shaped field at all, and uses clipSafe for the
       rest; the blunt backstop cuts on a whitespace boundary so it cannot end inside a link.

  Plus the two defects in wave 8 that the tranche caught:
  G1 · the fake-acknowledgement gate matched "sorry for the confusion" but 6097 said
       "I apologize for the confusion" and walked straight through. Widened, re-audited.
  R4 · the ask-one-clarifier rule caused a regression: 6182 asked "which Fernando?" when the
       evidence already disambiguated it. Tightened to forbid exactly that.

  python3 scripts/olivia_loop/apply_fixwave9_2026-08-24.py [--dry]
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

    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]

    # ---- M2a · the halving squeeze must never cut inside a link ----------------------
    old_sq = """          for (const k of Object.keys(row)) {
            const v = row[k];
            o[k] = (typeof v === 'string' && v.length > cut) ? v.slice(0, cut) + '…' : v;
          }"""
    new_sq = """          for (const k of Object.keys(row)) {
            const v = row[k];
            // fixwave 9 (M2): this squeeze only runs on payloads over CAP — exactly the big
            // result sets — and it used to blunt-slice EVERY string field, links included, which
            // is where '…/posts/262399…' came from. A url/link field is never the bulk of a row,
            // so it is exempt outright; everything else goes through clipSafe, which refuses to
            // end a cut inside a link.
            if (typeof v === 'string' && v.length > cut) {
              o[k] = /(^|_)url$|link$|permalink|href/i.test(k) ? v : clipSafe(v, cut);
            } else { o[k] = v; }
          }"""
    cm = sub(cm, old_sq, new_sq, "merge halving squeeze")

    # ---- M2b · the blunt backstop cuts on a whitespace boundary ----------------------
    old_bl = """  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]"';"""
    new_bl = """  if (body.length > CAP) {
    // fixwave 9 (M2): the impossible-case backstop still blunt-sliced mid-token, so it could end
    // inside a URL. Back up to the last whitespace before the cap first.
    let _cut = body.slice(0, CAP);
    const _sp = _cut.lastIndexOf(' ');
    if (_sp > CAP * 0.9) { _cut = _cut.slice(0, _sp); }
    body = _cut + ' …[truncated — narrow the query for more]"';
  }"""
    cm = sub(cm, old_bl, new_bl, "merge blunt backstop")

    # ---- M1 · stamps read the ORIGINAL object, never the truncated string ------------
    # one shared, never-truncated view of the rows, defined before the first stamp uses it
    old_w7 = """      const _rows7 = (() => { try { const b = JSON.parse(body); 
        return Array.isArray(b) ? b : (Array.isArray(b.people) ? b.people : (Array.isArray(b.members) ? b.members : null)); } catch (e) { return null; } })();"""
    new_w7 = """      // fixwave 9 (M1): read `r`, the ORIGINAL tool result. This used to JSON.parse(body),
      // which by this point may have been squeezed and blunt-sliced past valid JSON — so on
      // every payload over CAP the parse threw and this stamp silently did nothing, which is
      // exactly the case (a long people list) it was written for.
      const _rows7 = (() => {
        const b = r;
        if (Array.isArray(b)) return b;
        if (b && typeof b === 'object') {
          return Array.isArray(b.people) ? b.people : (Array.isArray(b.members) ? b.members : null);
        }
        return null;
      })();"""
    cm = sub(cm, old_w7, new_w7, "wave7 cap stamp source")

    old_w8 = """      const _p8 = (() => { try { return JSON.parse(body); } catch (e) { return null; } })();"""
    new_w8 = """      const _p8 = r;   // fixwave 9 (M1): the original object, not the truncated body string"""
    cm = sub(cm, old_w8, new_w8, "wave8 stamp source")

    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    # ---- M2c · Answer Seed's second clipper -----------------------------------------
    seed = nodes["Answer Seed"]; cs = seed["parameters"]["jsCode"]
    old_clip = """const clip = (s, n) => { s = String(s); return s.length > n ? s.slice(0, n) + '…' : s; };"""
    new_clip = """const clip = (s, n) => { s = String(s); return s.length > n ? clipSafe(s, n) : s; };  // fixwave 9 (M2): route the second clipper through clipSafe too — it was still cutting inside links"""
    cs = sub(cs, old_clip, new_clip, "seed clip helper")

    # ---- R4 · the clarifier rule caused 6182 ----------------------------------------
    old_r4 = """  'ASK ONE CLARIFIER INSTEAD OF GUESSING. When the ask genuinely has two readings and the answers differ - a word that names both a person and a brand, "the change" with two changes in play, an ambiguous pronoun - ask ONE short question and stop. Do not guess the reading and answer at length, and do not ask a clarifier you can resolve yourself from the evidence in front of you. One question, then wait.',"""
    new_r4 = """  'ASK ONE CLARIFIER INSTEAD OF GUESSING - BUT ONLY WHEN THE EVIDENCE CANNOT SETTLE IT. First try to settle the ambiguity yourself: if the conversation just named one of the candidates, or only one of them fits what was being discussed, that is your answer - use it and say which one you took it to mean. Two people sharing a first name is NOT a reason to ask when the thread was already about one of them. Only when the readings genuinely differ AND nothing in the turn or the evidence picks between them do you ask ONE short question and stop. Never guess silently and answer at length either.',"""
    cs = sub(cs, old_r4, new_r4, "seed R4 clarifier rule")
    node_check(cs, "Answer Seed"); seed["parameters"]["jsCode"] = cs

    # ---- G1 · widen the fake-acknowledgement pattern ---------------------------------
    gv = nodes["Gate Verdict"]; cg = gv["parameters"]["jsCode"]
    old_g1 = """const FAKE_ACK_RE = /\\byep,? got it\\b|\\bi can see it\\b|you'?re right,? sorry|sorry for the confusion/i;"""
    new_g1 = """// fixwave 9 (G1): 6097 answered "You're right, and I apologize for the confusion" and walked
// straight through the wave-8 pattern, which only knew "sorry for the confusion". The apology
// verb and the concession are now matched independently of each other's wording. A bare
// "you're right" was tried and REJECTED by the audit: it false-fired on 6160, where agreeing
// was correct. Re-audited over all 602: fires twice, both real fails, zero false positives.
const FAKE_ACK_RE = /\\byep,? got it\\b|\\bi can see it\\b|(sorry|apologi[sz]e[sd]?|my apologies)[^.!?]{0,30}\\bconfusion\\b|\\bmy mistake\\b/i;"""
    cg = sub(cg, old_g1, new_g1, "gate G1 pattern")
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
    am = n2["Answer Merge"]["parameters"]["jsCode"]
    assert "fixwave 9 (M1)" in am and "fixwave 9 (M2)" in am
    # comments mention JSON.parse(body) when describing the fix — check only real code lines
    _code = [l for l in am.split("\n") if "JSON.parse(body)" in l and not l.strip().startswith("//")]
    assert not _code, f"a stamp still parses the truncated body: {_code[:1]}"
    assert "ONLY WHEN THE EVIDENCE CANNOT SETTLE IT" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "apologi[sz]" in n2["Gate Verdict"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
