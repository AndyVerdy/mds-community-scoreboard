#!/usr/bin/env python3
"""#142 (6483): the IDENTITY second-person rule stands down when the draft already refused the typed name —
apply to STAGING (on top of #139).

Verified 2026-09-08 00:46Z (staging aa649e7b, bank C 6483, exec 137871): "I'm Ivan Ong. What sessions are a
must for me at the Singapore summit?" — all three drafts did the right thing ("I can't take a typed name as
identification, so I'm answering from your own record, Andy"), but the SECOND-PERSON THIRD-PARTY rule fires on
any "your record / profile / business" while a name was typed, so the turn regenerated three times and the
clamp shipped "I could not confirm…". The rule stays for the Lisa failure (the draft personalises FOR the
typed name) and stands down when the draft names the real asker or explicitly refuses the typed name. The
clamp itself is untouched (#142 stays "deliberately not touched"); this is one rule's precision.

  Gate Verdict  secondPersonAboutOther(answerText, askerFirst, idOther) — pure function replacing the inline
                test; scripts/olivia_loop/test_142_identity_precision.js runs it against this node's bytes.

  python3 scripts/olivia_loop/apply_142_identity_precision.py --dry-run DIR
  python3 scripts/olivia_loop/apply_142_identity_precision.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries the "#142" marker; the anchor is the inline rule.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#142"
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


FUNC = r"""// #142 (6483, exec 137871): the second-person rule below fired on drafts that had already refused the typed
// name ("I can't take a typed name as identification, so I'm answering from your own record, Andy") and the
// turn clamped after three laps. It stands down when the draft names the real asker or refuses the typed
// name; the Lisa failure (personalising FOR the typed name) still fires. Pure function; test_142 runs it.
function secondPersonAboutOther(answerText, askerFirst, idOther) {
  const a = String(answerText || '');
  if (!idOther) { return false; }
  if (!/\byour\s+(profile|record|business|niche|revenue|company|brand|store|city|products?)\b/i.test(a)) { return false; }
  const first = String(askerFirst || '').trim();
  if (first && new RegExp('(^|[^A-Za-z])' + first.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![A-Za-z])', 'i').test(a)) { return false; }
  if (/\b(can.?t|cannot|won.?t|not able to|unable to|do not|don.?t)\s+(take|accept|use|treat)\b[^.!?]{0,50}\b(name|identification|identity)\b/i.test(a)) { return false; }
  return true;
}
"""

OLD = "  if (_idOther && /\\byour\\s+(profile|record|business|niche|revenue|company|brand|store|city|products?)\\b/i.test(answerText)) {"
NEW = "  if (secondPersonAboutOther(answerText, _askerFirst, _idOther)) { // #142: stands down when the draft refused the name"

# the function goes right before the identity block's own marker comment
ANCHOR = "// IDENTITY BINDING (2026-08-23, live defect)."


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def patch_code(code):
    if "secondPersonAboutOther" in code:
        return code, False
    for old in (OLD, ANCHOR):
        c = code.count(old)
        if c != 1:
            sys.exit(f"ABORT {NODE}: expected 1 occurrence, found {c}\n  {old[:100]!r}")
    code = code.replace(ANCHOR, FUNC + ANCHOR).replace(OLD, NEW)
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
        print(f"  {NODE}: secondPersonAboutOther() in, inline rule replaced, node --check OK")
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
