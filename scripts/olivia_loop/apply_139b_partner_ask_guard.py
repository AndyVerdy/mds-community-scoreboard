#!/usr/bin/env python3
"""#139 lap 2: a partner named like the member's own question is never appended — apply to STAGING (on top of #139).

Found while proving #139 on staging b82f752e (2026-09-08 01:19Z, exec 137957): "Which MDS partner agencies
handle TikTok Shop, and what's the deal?" — the draft named and linked five agencies itself, and the repair
appended "TikTok Shop (TBA): https://app.mds.co/partners/655e…" because the directory carries a partner
literally called "TikTok Shop" and the draft says "TikTok Shop" in every sentence: the member typed it.

  Gate Verdict  linkCoverageUrls(evRaw, answerText, askText)  — a partner row whose name the member typed
                themselves is the subject of the question, not a recommendation: skipped. The call site
                passes `_memberMsg`. Pure function; test_175_link_pairing.js runs it (cases "#139 lap 2").

  python3 scripts/olivia_loop/apply_139b_partner_ask_guard.py --dry-run DIR
  python3 scripts/olivia_loop/apply_139b_partner_ask_guard.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries the three-argument signature; requires #139 (its anchors).
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "function linkCoverageUrls(evRaw, answerText, askText) {"
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


EDITS = [
    ("function linkCoverageUrls(evRaw, answerText) {\n",
     "function linkCoverageUrls(evRaw, answerText, askText) {\n"
     "  // #139 lap 2 (exec 137957): a partner named like the member's own question (\"TikTok Shop\") is the subject\n"
     "  // of the question, not a recommendation — never appended.\n"
     "  const askLow = String(askText || '').toLowerCase();\n"),
    ("    if (key === 'partner_url') {\n      const mn = flat.match(NAME);\n      if (!mn) { continue; }\n",
     "    if (key === 'partner_url') {\n      const mn = flat.match(NAME);\n      if (!mn) { continue; }\n"
     "      if (askLow && askLow.indexOf(String(mn[1]).toLowerCase()) !== -1) { continue; }\n"),
    ("  const add = linkCoverageUrls(evRaw, answerText);\n",
     "  const add = linkCoverageUrls(evRaw, answerText, _memberMsg); // #139 lap 2: the member's own words are not a recommendation\n"),
]


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
    if "#139" not in code:
        sys.exit(f"ABORT {NODE}: #139 not present — apply #139 first")
    if "const _memberMsg = " not in code:
        sys.exit(f"ABORT {NODE}: _memberMsg not defined in this node")
    for old, new in EDITS:
        c = code.count(old)
        if c != 1:
            sys.exit(f"ABORT {NODE}: expected 1 occurrence, found {c}\n  {old[:100]!r}")
        code = code.replace(old, new)
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
        print(f"  {NODE}: linkCoverageUrls(evRaw, answerText, askText), partner rows named in the ask skipped, node --check OK")
    else:
        print(f"  {NODE}: already carries the askText signature, skipped")
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
