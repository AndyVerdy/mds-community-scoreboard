#!/usr/bin/env python3
"""Fixwave 17 — two shapes wave 16's stamps could not see.

 S12 · THE FINDER'S OWN SHAPE. 6217 is served by the #108 finder route, not member_match_v2, and
       its payload is {"total":13,"shown":10,"capped":true,"people":[...]} — the count sits at the
       TOP LEVEL, not on each row. So S8 (true total) and S9 (hard cap) both looked for a row field
       that is not there and silently did nothing, and she printed twelve names off a ten-person
       payload with the real total sitting one key away. The payload was right the whole time; the
       stamps could not read it. Now they can, and the "name only these" instruction rides with it
       because the two extra names were invented, not supplied.

 F2 · the verbatim digest route BYPASSES Format Reply entirely (Build Verbatim Digest goes straight
      to Mark Welcomed / Action? / Billing Nudge), so wave 16's heading strip never ran on it. That
      is why "## MDS Trading -- Week of 2026-08-17" and "### Macro Thesis" still went out with
      visible hashes. Same strip, applied where that text is actually built.

  python3 scripts/olivia_loop/apply_fixwave17_2026-08-24.py [--dry]
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

    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]
    a = """        // S9 (fixwave 16) — HARD CAP."""
    s12 = """        // S12 (fixwave 17) — the FINDER shape: the count is top-level, not per row.
        try {
          const _f = _p8;
          if (_f && typeof _f === 'object' && !Array.isArray(_f)
              && Array.isArray(_f.people) && _f.total != null) {
            const _shown = _f.shown != null ? Number(_f.shown) : _f.people.length;
            const _total = Number(_f.total);
            body = body + NL + 'MILLIE — DETERMINISTIC NOTE: ' + _total + ' people match in total and '
              + 'you have been handed ' + _f.people.length + '. '
              + (_total > _shown
                  ? 'Say both plainly — "here are ' + _shown + ' of ' + _total + '" — and offer to narrow. '
                  : 'Say the number. ')
              + 'Name ONLY the people in this payload: there are exactly ' + _f.people.length
              + ' of them and no others are available to you on this turn. Do not top the list up '
              + 'from an earlier turn, another city, or memory — that is how twelve names once came '
              + 'out of a ten-person list.';
          }
        } catch (e) {}
"""
    cm = sub(cm, a, s12 + a, "S12 finder shape")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    bv = nodes["Build Verbatim Digest"]; cb = bv["parameters"]["jsCode"]
    # strip markdown headings on the verbatim path, right before the node returns
    import re as _re
    m = _re.search(r"\nreturn \[\{", cb)
    assert m, "Build Verbatim Digest return anchor not found"
    inject = """
// fixwave 17 (F2): this route never touches Format Reply, so its heading strip never applied here
// and digests went out with literal "## Week of ..." / "### Macro Thesis". Same rule, applied at
// the point the text is actually built: drop the hashes, keep the emphasis WhatsApp understands.
try {
  if (typeof text === 'string') { text = text.replace(/^\\s{0,3}#{1,6}\\s+(.+?)\\s*$/gm, '*$1*'); }
} catch (e) {}
"""
    cb = cb[:m.start()] + inject + cb[m.start():]
    node_check(cb, "Build Verbatim Digest"); bv["parameters"]["jsCode"] = cb

    if dry:
        print("DRY RUN — anchors hit, node --check clean on 2 nodes.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    n2 = {n["name"]: n for n in after["nodes"]}
    assert "S12 (fixwave 17)" in n2["Answer Merge"]["parameters"]["jsCode"]
    assert "fixwave 17 (F2)" in n2["Build Verbatim Digest"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
