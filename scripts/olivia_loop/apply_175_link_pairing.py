#!/usr/bin/env python3
"""#175: the gate's link repair pairs a URL with ITS OWN ROW — apply to STAGING.

Andy's case 1 (prod 2026-09-07, execs 137508 / 137515): `Gate Verdict` #1b paired every evidence URL
with the last `title` in the 900 chars before it. A top-5 evidence row carries up to 3,200 chars of
snippets between its title and its video_url, so the URL fell to the "after" fallback and took the
NEXT row's title — and when that row was named and linked in the draft, the previous row's URL was
appended bare before the closing question (65ef9f07… under "Listing Optimisation Deep Dive",
63e5b874… under "How Brands Turn Failed Creative Tests…"). A restricted duplicate catalog row of a talk
the draft had already linked was appended too (67e4836b…, 8 of 10 title words).

One node, one block: the #1b pairing loop becomes `linkCoverageUrls(evRaw, answerText)` — the row is
the JSON object around the url field, its title the last one before the url inside that row (else the
first after it, for url-first rows), image/logo keys never pair, and a candidate whose title shares
80% of its words with a row the draft already links is a duplicate. Insertion (max 3, before a
trailing offer question) is unchanged.

Offline proof: scripts/olivia_loop/test_175_link_pairing.js <Gate-Verdict.js>

  python3 scripts/olivia_loop/apply_175_link_pairing.py --dry-run DIR   # patched node -> DIR/Gate_Verdict.js
  python3 scripts/olivia_loop/apply_175_link_pairing.py                 # edits STAGING, one bounce

Idempotent: a node already carrying the #175 marker is skipped; the old block is located between two
anchors and checked for its known lines before it is replaced.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#175"
NODE = "Gate Verdict"
START = "let linkCoverage = 0;\n"
END = "// #1c ELEMENT-COVERAGE REPAIR"
MUST_CONTAIN = ("Math.max(0, fu.index - 900)", "const namedInAnswer = function (title) {", "linkCoverage = add.length;")


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


NEW_BLOCK = r"""// #175 LINK-COVERAGE REPAIR, PAIRED PER ROW (Andy's case 1, 2026-09-07, execs 137508 / 137515). #1b
// paired every evidence URL with the last title in the 900 chars before it. A top-5 evidence row
// carries up to 3,200 chars of snippets between its title and its video_url, so the URL fell to the
// "after" fallback and took the NEXT row's title - and when that row was named and linked in the
// draft, the previous row's URL was appended bare (65ef9f07 under "Listing Optimisation Deep Dive",
// 63e5b874 under "How Brands Turn Failed Creative Tests"). A restricted duplicate catalog row of a
// talk the draft had already linked was appended too (67e4836b, 8 of 10 title words). Now: the row
// is the JSON object around the url field, its title is the last one before the url INSIDE that row
// (else the first after it inside the row - url-first shapes), image/logo keys never pair, and a
// candidate whose title shares 80% of its words with a row the draft already links is a duplicate.
// Same contract as #1b: the URL is copied verbatim out of the evidence, repair never block, max 3,
// inserted before a trailing offer question. A row whose shape the boundary scan cannot read (a
// nested object array before the url) pairs with nothing - a missing repair beats a wrong link.
// Pure function; scripts/olivia_loop/test_175_link_pairing.js runs it against this node's own bytes.
function linkCoverageUrls(evRaw, answerText) {
  const ev = String(evRaw || '');
  const ans = String(answerText || '');
  const stripT = function (u) { return String(u).replace(/[)\]"'\u201d\u2019<>.,!?;:]+$/, ''); };
  const words = function (s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ').filter(function (w) { return w.length >= 4; });
  };
  // the draft names a title when it holds it whole, or 80% of its long words inside one span
  const namedInAnswer = function (title) {
    const h = ans.toLowerCase();
    if (h.indexOf(String(title).toLowerCase()) !== -1) { return true; }
    const ws = words(title);
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
  };
  const sameTitle = function (a, b) {
    const wa = words(a), wb = words(b);
    if (wa.length < 2 || wb.length < 2) { return String(a).toLowerCase() === String(b).toLowerCase(); }
    const set = {}, seen = {};
    wa.forEach(function (w) { set[w] = 1; });
    let c = 0;
    wb.forEach(function (w) { if (set[w] && !seen[w]) { seen[w] = 1; c += 1; } });
    return c >= Math.ceil(0.8 * Math.min(wa.length, wb.length));
  };
  const FLD = /\\?"([a-z_]{0,24}(?:url|link|permalink))\\?"\s*:\s*\\?"(https?:\/\/[^"\\ ]{8,400})/g;
  const TITLE = /title\\?"\s*:\s*\\?"([^"\\]{6,120})/;
  // the row = the object around the url field, found by walking brackets outward (a nested
  // attachments:[{...}] array must not pass for a row boundary — it did on 684848cd, 2026-09-07)
  const rowStart = function (i) {
    let dO = 0, dA = 0;
    for (let k = i - 1; k >= 0 && i - k < 12000; k--) {
      const ch = ev.charAt(k);
      if (ch === '}') { dO += 1; }
      else if (ch === '{') { if (dO === 0 && dA === 0) { return k; } if (dO > 0) { dO -= 1; } }
      else if (ch === ']') { dA += 1; }
      else if (ch === '[') { if (dA > 0) { dA -= 1; } else { return -1; } }
    }
    return -1;
  };
  const rowEnd = function (i) {
    let dO = 0, dA = 0;
    for (let k = i; k < ev.length && k - i < 12000; k++) {
      const ch = ev.charAt(k);
      if (ch === '{') { dO += 1; }
      else if (ch === '}') { if (dO === 0 && dA === 0) { return k; } if (dO > 0) { dO -= 1; } }
      else if (ch === '[') { dA += 1; }
      else if (ch === ']') { if (dA > 0) { dA -= 1; } else { return -1; } }
    }
    return -1;
  };
  // the row's own fields sit at depth 0: blank out every nested object or array first
  const depth0 = function (row) {
    let out = '', d = 0;
    for (let k = 0; k < row.length; k++) {
      const ch = row.charAt(k);
      if (ch === '{' || ch === '[') { if (k > 0) { d += 1; } out += ' '; continue; }
      if (ch === '}' || ch === ']') { if (d > 0) { d -= 1; out += ' '; continue; } }
      out += d > 0 ? ' ' : ch;
    }
    return out;
  };
  const rowTitle = function (i) {
    const rs = rowStart(i), re = rowEnd(i);
    if (rs < 0 || re < 0 || re <= rs) { return null; }
    const mt = depth0(ev.slice(rs, re + 1)).match(TITLE);
    return mt ? mt[1] : null;
  };
  const seenU = {};
  const pairs = [];
  let fu = null, fgu = 0;
  FLD.lastIndex = 0;
  while ((fu = FLD.exec(ev)) !== null && fgu++ < 600) {
    const key = String(fu[1]).toLowerCase();
    const u = stripT(fu[2]);
    if (pairs.length >= 60 || seenU[u]) { continue; }
    seenU[u] = 1;
    if (/thumb|logo|image|photo|avatar|icon/.test(key) || /\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(u)) { continue; }
    const t = rowTitle(fu.index);
    if (t) { pairs.push({ title: t, url: u }); }
  }
  const linked = pairs.filter(function (p) { return ans.indexOf(p.url) !== -1; });
  const add = [];
  pairs.forEach(function (p) {
    if (add.length >= 3) { return; }
    if (ans.indexOf(p.url) !== -1) { return; }
    if (!namedInAnswer(p.title)) { return; }
    if (linked.some(function (l) { return sameTitle(l.title, p.title); })) { return; }
    if (add.some(function (q) { return sameTitle(q.title, p.title); })) { return; }
    add.push(p);
  });
  return add.map(function (p) { return p.url; });
}
let linkCoverage = 0;
try {
  const add = linkCoverageUrls(evRaw, answerText);
  if (add.length) {
    const lines = answerText.replace(/\s+$/, '').split(NL);
    let at = lines.length;
    for (let i = lines.length - 1; i >= 0 && i >= lines.length - 3; i--) {
      if (/(want|would you like|shall i|should i)\b[^?]{0,90}\?\s*$/i.test(lines[i])) { at = i; }
    }
    lines.splice(at, 0, add.join(NL));
    answerText = lines.join(NL);
    linkCoverage = add.length;
  }
} catch (e) {}

"""


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def patch_code(code):
    if MARK in code:
        return code, False
    s = code.find(START)
    e = code.find(END)
    if s < 0 or e < 0 or e <= s or code.count(START) != 1 or code.count(END) != 1:
        sys.exit(f"ABORT {NODE}: anchors not found exactly once (start={s}, end={e})")
    old = code[s:e]
    for must in MUST_CONTAIN:
        if must not in old:
            sys.exit(f"ABORT {NODE}: the block between the anchors does not contain {must!r}")
    if len(old) > 6000:
        sys.exit(f"ABORT {NODE}: block between anchors is {len(old)} chars, expected < 6000")
    return code[:s] + NEW_BLOCK + code[e:], True


def main():
    dry = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run" else None
    wf = api("GET", f"/workflows/{STAGING_ID}")
    if wf.get("id") != STAGING_ID:
        sys.exit(f"GET failed: {json.dumps(wf)[:300]}")
    print(f"staging {STAGING_ID} versionId {wf.get('versionId')} nodes {len(wf['nodes'])}")
    node = next((n for n in wf["nodes"] if n["name"] == NODE), None)
    if node is None:
        sys.exit(f"ABORT: node {NODE} not found")
    code, changed = patch_code(node["parameters"]["jsCode"])
    if changed:
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {NODE}: node --check failed\n{err}")
        node["parameters"]["jsCode"] = code
        print(f"  {NODE}: #1b block replaced, node --check OK")
    else:
        print(f"  {NODE}: already carries {MARK}, skipped")
    if dry:
        os.makedirs(dry, exist_ok=True)
        path = os.path.join(dry, "Gate_Verdict.js")
        open(path, "w").write(code)
        print(f"  wrote {path}\ndry run: nothing written to n8n")
        return
    if not changed:
        print("nothing to do")
        return
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
