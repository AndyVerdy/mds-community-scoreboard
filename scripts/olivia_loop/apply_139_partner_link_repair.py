#!/usr/bin/env python3
"""#139: a named partner ships with its recorded offer and its page — apply to STAGING (on top of #175).

Verified still present 2026-09-08 00:33Z (staging eb99c336, bank C 6075 "What do people say about agencies
for tiktok"): five partners named — Media Labs, Social Tale, ScaleHouse, Zainith, The Media Elephant — with no
offer and no page, while 7018 / 7043 / 6301 did ship offers + pages. Two seed rules (S2 wave 8, S15 wave 18)
already failed on this; per code-beats-prompt the third attempt is code. Root cause in the gate's link
repair (#1b, per-row since #175): it pairs a URL with the row's `title`, and partner rows carry `name`,
`offer_value` and `partner_url` — so a named partner without its link was never repaired.

  Gate Verdict  linkCoverageUrls(): a row whose url key is `partner_url` is paired by its depth-0 `name`
                and, when the draft names the partner and omits its link, the repair appends ONE line
                "Name (offer_value): partner_url" — the offer text is copied verbatim from the row, so the
                link gate's invariant (every URL verbatim in evidence) and the fact gate's (every claim
                from evidence) both survive by construction. Video / thread rows unchanged (bare URL).

Offline proof: scripts/olivia_loop/test_175_link_pairing.js <Gate-Verdict.js>  (cases 15-19 are #139)

  python3 scripts/olivia_loop/apply_139_partner_link_repair.py --dry-run DIR
  python3 scripts/olivia_loop/apply_139_partner_link_repair.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries the #139 marker; requires the #175 function.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#139"
NODE = "Gate Verdict"
START = "function linkCoverageUrls(evRaw, answerText) {\n"
END = "  return add.map(function (p) { return p.url; });\n}\n"


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


NEW_FUNC = r"""function linkCoverageUrls(evRaw, answerText) {
  // #139 (2026-09-08): partner rows carry `name` + `offer_value` + `partner_url`, never `title`, so a named
  // partner without its link was never repaired (bank C 6075: five agencies, no offer, no page). A row whose
  // url key is partner_url is paired by its depth-0 name, and the repair line carries the offer verbatim.
  const ev = String(evRaw || '');
  const ans = String(answerText || '');
  const stripT = function (u) { return String(u).replace(/[)\]"'\u201d\u2019<>.,!?;:]+$/, ''); };
  const words = function (s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ').filter(function (w) { return w.length >= 4; });
  };
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
  const NAME = /\\?"name\\?"\s*:\s*\\?"([^"\\]{3,120})/;
  const OFFER = /\\?"offer_value\\?"\s*:\s*\\?"([^"\\]{2,160})/;
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
  const rowFlat = function (i) {
    const rs = rowStart(i), re = rowEnd(i);
    if (rs < 0 || re < 0 || re <= rs) { return null; }
    return depth0(ev.slice(rs, re + 1));
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
    const flat = rowFlat(fu.index);
    if (!flat) { continue; }
    const mt = flat.match(TITLE);
    if (mt) { pairs.push({ title: mt[1], url: u, partner: false, offer: null }); continue; }
    if (key === 'partner_url') {
      const mn = flat.match(NAME);
      if (!mn) { continue; }
      const mo = flat.match(OFFER);
      pairs.push({ title: mn[1], url: u, partner: true, offer: mo ? mo[1] : null });
    }
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
  return add.map(function (p) {
    if (!p.partner) { return p.url; }
    return p.title + (p.offer ? ' (' + p.offer + ')' : '') + ': ' + p.url;
  });
}
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
    if "#175" not in code:
        sys.exit(f"ABORT {NODE}: #175 not present — apply #175 first")
    s = code.find(START)
    e = code.find(END)
    if s < 0 or e < 0 or e <= s or code.count(START) != 1 or code.count(END) != 1:
        sys.exit(f"ABORT {NODE}: anchors not found exactly once (start={s}, end={e})")
    return code[:s] + NEW_FUNC + code[e + len(END):], True


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
        print(f"  {NODE}: linkCoverageUrls() replaced, node --check OK")
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
