#!/usr/bin/env python3
"""#175 lap 2: the #1c FIELD repair (registration_url / event_url) pairs with its own row and its own segment —
apply to STAGING (on top of #139 + #142).

Found while proving the batch on staging b39b31ab (2026-09-08 01:00Z):
  exec 137901  "Has MDS announced any 2027 events?" — the draft linked every event by its reg_link
               (/s/events/u/…, go.mdsonly.co/…); #1c appended the SAME rows' event_url bare (two lines).
  exec 137902  "…when they announce the main meetup for 2027? This year is Singapore" — #1c pinned
               "Register: https://go.mdsonly.co/MDSSummitSingapore" + the Summit's page to an answer about
               2027 because "…not a repeat of Singapore:\\n*MDS Summit Cancun 2027*" read as naming
               "MDS Summit Singapore" (the re-ordered-words window ran across a colon, a line break and a
               bold title) — and that Summit had already ended (`"is_over":true`, `"phase":"ended"`).

  Gate Verdict  _nameInAnswer(nm, hay)   the words of a name are matched INSIDE one line / clause, never across
                fieldRepairSkip(evRaw, idx, answerText, nowMs)   'linked' when any URL of the same row is already
                in the draft · 'past' when the row is a finished event · '' otherwise. #1c skips 'linked'
                candidates and never adds a registration line for a 'past' row. Pure functions; test_175 runs both.

  python3 scripts/olivia_loop/apply_175b_event_repair_precision.py --dry-run DIR
  python3 scripts/olivia_loop/apply_175b_event_repair_precision.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries fieldRepairSkip(); the anchors are the shipped #1c bytes.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "fieldRepairSkip"
NODE = "Gate Verdict"


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


OLD_NAME = r"""const _nameInAnswer = function (nm, hay) {
  const w = function (s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(' ')
      .filter(function (x) { return x.length > 1; });
  };
  const ow = w(nm);
  if (!ow.length || ow.length > 9) { return false; }
  const aw = w(hay);
  if ((' ' + aw.join(' ') + ' ').indexOf(' ' + ow.join(' ') + ' ') !== -1) { return true; }
  if (ow.length < 2) { return false; }
  const key = ow.slice().sort().join(' ');
  for (let i = 0; i + ow.length <= aw.length; i++) {
    if (aw.slice(i, i + ow.length).sort().join(' ') === key) { return true; }
  }
  return false;
};
"""

NEW_NAME = r"""const _nameInAnswer = function (nm, hay) {
  // #175 lap 2 (exec 137902): "…not a repeat of Singapore:\n*MDS Summit Cancun 2027*" read as naming
  // "MDS Summit Singapore" — the re-ordered-words window ran across a colon, a line break and a bold
  // title. A name is named INSIDE one segment: the words are matched per line / clause, never across.
  const w = function (s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(' ')
      .filter(function (x) { return x.length > 1; });
  };
  const ow = w(nm);
  if (!ow.length || ow.length > 9) { return false; }
  const phrase = ' ' + ow.join(' ') + ' ';
  const key = ow.slice().sort().join(' ');
  const segs = String(hay || '').split(/[\n\r:;.,!?()\[\]*•—–|]+/);
  for (let s = 0; s < segs.length; s++) {
    const aw = w(segs[s]);
    if (aw.length < ow.length) { continue; }
    if ((' ' + aw.join(' ') + ' ').indexOf(phrase) !== -1) { return true; }
    if (ow.length < 2) { continue; }
    for (let i = 0; i + ow.length <= aw.length; i++) {
      if (aw.slice(i, i + ow.length).sort().join(' ') === key) { return true; }
    }
  }
  return false;
};
"""

FUNC = r"""// #175 lap 2 (execs 137901 / 137902): the #1c field repair appended a row's event_url when the draft already
// carried the SAME row's reg_link (Inspire: /s/events/u/… vs /events/u/…; Centurion: go.mdsonly.co vs
// /events/u/…), and pinned "Register: …" for a Summit that had already ended. A row already linked by any of
// its own URLs is covered; a finished event never gets a registration line. Pure function; test_175 runs it.
function fieldRepairSkip(evRaw, idx, answerText, nowMs) {
  const ev = String(evRaw || '');
  const ans = String(answerText || '');
  const now = typeof nowMs === 'number' ? nowMs : Date.now();
  let rs = -1, dO = 0, dA = 0;
  for (let k = idx - 1; k >= 0 && idx - k < 12000; k--) {
    const ch = ev.charAt(k);
    if (ch === '}') { dO += 1; }
    else if (ch === '{') { if (dO === 0 && dA === 0) { rs = k; break; } if (dO > 0) { dO -= 1; } }
    else if (ch === ']') { dA += 1; }
    else if (ch === '[') { if (dA > 0) { dA -= 1; } else { break; } }
  }
  if (rs < 0) { return ''; }
  let re = -1; dO = 0; dA = 0;
  for (let k = idx; k < ev.length && k - idx < 12000; k++) {
    const ch = ev.charAt(k);
    if (ch === '{') { dO += 1; }
    else if (ch === '}') { if (dO === 0 && dA === 0) { re = k; break; } if (dO > 0) { dO -= 1; } }
    else if (ch === '[') { dA += 1; }
    else if (ch === ']') { if (dA > 0) { dA -= 1; } else { break; } }
  }
  if (re < 0) { return ''; }
  const raw = ev.slice(rs, re + 1);
  let flat = '', d = 0;
  for (let k = 0; k < raw.length; k++) {
    const ch = raw.charAt(k);
    if (ch === '{' || ch === '[') { if (k > 0) { d += 1; } flat += ' '; continue; }
    if (ch === '}' || ch === ']') { if (d > 0) { d -= 1; flat += ' '; continue; } }
    flat += d > 0 ? ' ' : ch;
  }
  const U = /\\?"([a-z_]{0,24}(?:url|link|permalink))\\?"\s*:\s*\\?"(https?:\/\/[^"\\ ]{8,400})/g;
  let m = null, g = 0;
  while ((m = U.exec(flat)) !== null && g++ < 40) {
    if (/maps|thumb|logo|image|photo|avatar|icon/.test(m[1])) { continue; }
    const u = String(m[2]).replace(/[)\]"'\u201d\u2019<>.,!?;:]+$/, '');
    if (u && ans.indexOf(u) !== -1) { return 'linked'; }
  }
  if (/\\?"is_over\\?"\s*:\s*true/.test(flat)) { return 'past'; }
  if (/\\?"phase\\?"\s*:\s*\\?"(ended|past|completed|finished|cancelled|canceled)/i.test(flat)) { return 'past'; }
  if (/\\?"start_display\\?"\s*:\s*\\?"[^"\\]*-\s*past/i.test(flat)) { return 'past'; }
  if (/\\?"start_display\\?"\s*:\s*\\?"[^"\\]*upcoming/i.test(flat)) { return ''; }
  const sa = flat.match(/\\?"(?:ends_at|end_at|starts_at|start_at)\\?"\s*:\s*\\?"(\d{4}-\d{2}-\d{2}T[^"\\]{5,40})/);
  if (sa) {
    const t = Date.parse(sa[1]);
    if (!isNaN(t) && t < now - 6 * 36e5) { return 'past'; }
  }
  return '';
}
"""

ANCHOR_FUNC = "let fieldCoverage = 0;\n"

OLD_LOOP = "    const u = stripT(fm2[2]);\n    if (answerText.indexOf(u) !== -1) { continue; }\n"
NEW_LOOP = ("    const u = stripT(fm2[2]);\n    if (answerText.indexOf(u) !== -1) { continue; }\n"
            "    const _fsk = fieldRepairSkip(evRaw, fm2.index, answerText); // #175 lap 2: own row already linked / finished event\n"
            "    if (_fsk === 'linked' || (_fsk === 'past' && fm2[1] === 'registration_url')) { continue; }\n")


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
    for old in (OLD_NAME, ANCHOR_FUNC, OLD_LOOP):
        c = code.count(old)
        if c != 1:
            sys.exit(f"ABORT {NODE}: expected 1 occurrence, found {c}\n  {old[:100]!r}")
    code = code.replace(OLD_NAME, NEW_NAME).replace(ANCHOR_FUNC, FUNC + ANCHOR_FUNC).replace(OLD_LOOP, NEW_LOOP)
    return code, True


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
        print(f"  {NODE}: _nameInAnswer per-segment, fieldRepairSkip() in, #1c loop skips, node --check OK")
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
