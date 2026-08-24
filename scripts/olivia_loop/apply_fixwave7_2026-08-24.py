#!/usr/bin/env python3
"""Fixwave 7 — bank C clusters 1, 2, 5, 6 (drafted DURING the run, applied only after turn 690).
STAGING bqHstPDi84uOhTCJ only. Cluster 3 (all-sources coverage) is deliberately NOT here — it
needs its own design pass. Cluster 4 was a measurement artifact (no change).

  1 · links (seed STYLE bullet — first prompt rule for this behaviour; audit showed a code check
      would false-positive on venue+maps and question-naming-the-link shapes)
  2 · names cap + exact counts (Answer Merge deterministic stamp — code, not prompt)
  5 · internals narration by SHAPE (Gate Verdict, first-attempt-only; audited: 2 fires in 380,
      both real)
  6 · follow-up contradiction (Answer Merge stamp off turn_state — code, not prompt)

  python3 scripts/olivia_loop/apply_fixwave7_2026-08-24.py [--dry]
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

    # ---- 1 · Answer Seed: link-placement STYLE bullet --------------------------------
    seed = nodes["Answer Seed"]; c = seed["parameters"]["jsCode"]
    anchor1 = ("never speculate about when the next sync runs, and NEVER describe internal data "
               "problems, placeholder rows or test entries to a member.',")
    bullet = anchor1 + """
  'LINKS sit WITH their sentence: on the same line ("Register: <url>") or directly under the line that names them (a venue line then its maps link is fine). NEVER end a reply with a link no sentence introduced, never stack a second bare link under an unrelated one, and if a link has no sentence naming it, drop the link. When you cite a post, thread or video BY NAME and its link is in the evidence, include that link - never offer "want me to pull the link?" for a link you are holding. Never emit a URL containing an ellipsis (a link display-shortened in the evidence is not a link - use the url field or leave it out). A stated count must equal what you actually listed - never "20+" when the evidence says 18, never a numbered list that stops early.',
  'SHARING RULE (Andy 2026-08-24): if the asker could find it themselves - it is public, or it lives in a chat they belong to - you may share it, whatever kind of info it is, contact details and self-stated revenue included. ALWAYS name the source ("per <who> in <where>, <when>"): quoted material without its source is a defect. What OUR RECORDS hold still follows the field rules (exact revenue from records stays internal even when the band is shareable) - the carve-out is only for what people SAID on surfaces the asker can see.',"""
    c = sub(c, anchor1, bullet, "seed link bullet")
    node_check(c, "Answer Seed"); seed["parameters"]["jsCode"] = c

    # ---- 2+6 · Answer Merge: names-cap stamp + turn_state contradiction stamp --------
    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]
    anchor2 = "// The member's literal message — several stamps below need to know what was actually asked."
    stamps = """// fixwave 7 (bank C clusters 2+6): names cap + exact counts + thread-number consistency.
    try {
      const _rows7 = (() => { try { const b = JSON.parse(body); 
        return Array.isArray(b) ? b : (Array.isArray(b.people) ? b.people : (Array.isArray(b.members) ? b.members : null)); } catch (e) { return null; } })();
      if (_rows7 && _rows7.length > 10 && _rows7.every(x => x && (x.full_name || x.name))) {
        body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this list has ' + _rows7.length
          + ' people. Name AT MOST 10 and state the true total (' + _rows7.length
          + ') in plain words. Never exceed ten names, never approximate the total.';
      }
      const _ts7 = (() => { try { return ($('Prep Context').first().json || {}).prev_state || null; } catch (e) { return null; } })();
      if (_ts7 && _ts7.find && _ts7.find.total != null) {
        body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this conversation already established the number '
          + _ts7.find.total + ' for the filtered group (' + JSON.stringify(_ts7.find.where || {}).slice(0, 120)
          + '). If this reply gives a different number for that same group, either keep '
          + _ts7.find.total + ' or begin with an explicit correction ("Correcting what I said earlier: ..."). Never silently swap it, and never re-label a different measurement as this one.';
      }
    } catch (e) {}
    """ + anchor2
    cm = sub(cm, anchor2, stamps, "merge stamps")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    # ---- 5 · Gate Verdict: narration SHAPE check (first-attempt-only zone) -----------
    gv = nodes["Gate Verdict"]; cg = gv["parameters"]["jsCode"]
    anchor3 = "const _attempt0 = Math.max(prev.gate_attempts || 0, typeof $runIndex === 'number' ? $runIndex : 0) === 0;"
    shape = anchor3 + """

// fixwave 7 (bank C cluster 5, 3rd strike -> shape not patterns; audited 2/380 fires, both real):
// a sentence whose subject is backend machinery + a returns/came-back verb is narration.
try {
  const _txt7 = String(answerText || '');
  const _shape7 = /(\\b(the|my|our|a|that|this)\\s+(search\\s+)?(tool|query|lookup|directory|preload(?:ed)?\\s+search)\\b[^.\\n]{0,40}\\b(returns?|returned|comes? back|came back|pulled|gave|came up|kept giving|is coming back|empty on its end|only covers|can (see|retrieve|search))\\b)|(\\b(in|from) my (results|search)\\b)|(\\bwhat I can retrieve\\b)|(\\bsearchable here\\b)|(\\bmy search only\\b)|(\\b(in|from) what I(?:'m| am| can)? ?(?:pull|retriev|access)\\w*\\b)/i;
  if (_attempt0 && _shape7.test(_txt7)) {
    policyClaims.push('INTERNALS-SHAPE: the draft describes how the answer was obtained ("'
      + (_txt7.match(_shape7) || [''])[0].slice(0, 60)
      + '"). Deliver the facts in member words; never describe machinery or retrieval.');
  }
} catch (e) {}"""
    cg = sub(cg, anchor3, shape, "gate shape check")
    node_check(cg, "Gate Verdict"); gv["parameters"]["jsCode"] = cg

    if dry: print("DRY RUN — all anchors hit, node --check clean on 3 nodes."); return
    payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
               "settings": wf.get("settings") or {}}
    r = api("PUT", f"/workflows/{STAGING}", payload)
    assert r.get("id") == STAGING, f"PUT failed: {json.dumps(r)[:300]}"
    assert api("POST", f"/workflows/{STAGING}/deactivate", {}).get("active") is False
    assert api("POST", f"/workflows/{STAGING}/activate", {}).get("active") is True
    back = api("GET", f"/workflows/{STAGING}")
    assert "LINKS sit WITH their sentence" in next(n for n in back["nodes"] if n["name"]=="Answer Seed")["parameters"]["jsCode"]
    assert "INTERNALS-SHAPE" in next(n for n in back["nodes"] if n["name"]=="Gate Verdict")["parameters"]["jsCode"]
    print(f"APPLIED + bounced. versionId {back.get('versionId')}")

if __name__ == "__main__":
    main()
