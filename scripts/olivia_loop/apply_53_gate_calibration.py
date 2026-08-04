#!/usr/bin/env python3
"""#53 Fact-gate false clamp — post-filter calibration (apply to STAGING).

exec 63490 proved the class: retrieval CORRECT, every flagged claim present in
the evidence handed to the gate, Haiku failed it 3×, the member got the canned
"couldn't verify". The claims that SURVIVED the deterministic post-filter each
lap were paraphrase/variant misses the exact-string check cannot see:
  - "Tactical Logistic Solutions" vs draft "Logistics" (plural drift)
  - "'family-run 3PL'" (hyphenated paraphrase of evidence wording)
  - "$10K/month" (k-suffix figure invisible to the 4-digit number regex)
  - "one member said they quoted over $10K/month" (NO extractable entity at
    all — the old filter kept it as "trust the gate")

Three Gate Verdict changes, all in the post-filter (the Haiku gate, link gate,
AGG/SRCHEAD backstops and the 2-lap cap stay untouched):
  1. Text entities verify at WORD level: ≥80% of significant words (≥4 chars,
     letter-led, plural-tolerant) present in the evidence — spelling/plural/
     hyphen variants of REAL content verify; invented names still fail.
  2. Figure entities include k/m-suffix forms ("10K", "1.5M").
  3. A claim with NOTHING checkable cannot block alone — a no-entity claim is
     a paraphrase by construction; the catastrophic classes (invented people/
     links/quotes/figures) always carry an entity.

Offline proof (t53.js, the exec's real 46,079-char evidence): 20/20 real
flagged claims die · 4/4 fabrication canaries survive.

Idempotent: anchors asserted, hunks skip when applied.
"""
import json, subprocess, sys, tempfile, os

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


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


def patch(text, old, new, where):
    if new in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    gv = nodes["Gate Verdict"]["parameters"]["jsCode"]

    # 1. word-level helpers, right after evNum
    gv = patch(gv,
        "const evNum = ev.replace(/[,$]/g, '');",
        "const evNum = ev.replace(/[,$]/g, '');\n"
        "// #53 (exec 63490): the surviving false-positives were paraphrase/variant misses the\n"
        "// exact-string check cannot see (Logistic vs Logistics, family-run, $10K). Text entities\n"
        "// now verify at WORD level: >=80% of significant words (>=4 chars, letter-led,\n"
        "// plural-tolerant) present in the evidence. Invented names/figures still fail - their\n"
        "// words are in no evidence however formatted.\n"
        "const evWords = new Set(ev.replace(/[^a-z0-9]+/g, ' ').split(' ').filter(Boolean));\n"
        "const wordInEv = function (w) {\n"
        "  if (evWords.has(w)) return true;\n"
        "  if (evWords.has(w + 's')) return true;\n"
        "  if (w.length >= 5 && w.charAt(w.length - 1) === 's' && evWords.has(w.slice(0, -1))) return true;\n"
        "  return false;\n"
        "};\n"
        "const textEntityInEv = function (e) {\n"
        "  const s = String(e).toLowerCase().trim();\n"
        "  if (ev.includes(s)) return true;\n"
        "  const words = s.replace(/[^a-z0-9]+/g, ' ').split(' ')\n"
        "    .filter(function (w) { return w.length >= 4 && /^[a-z]/.test(w); });\n"
        "  if (!words.length) return false;\n"
        "  const hits = words.filter(wordInEv).length;\n"
        "  return hits >= Math.ceil(0.8 * words.length);\n"
        "};",
        "Gate Verdict word-level helpers")

    # 2. k/m-suffix figures join the number entities
    gv = patch(gv,
        "  const nums = (String(s).replace(/[,$]/g, '').match(/\\b\\d{4,}(?:\\.\\d+)?\\b/g) || []);",
        "  const nums = (String(s).replace(/[,$]/g, '').match(/\\b\\d{4,}(?:\\.\\d+)?\\b/g) || [])\n"
        "    // #53: k/m-suffix figures (\"10K\", \"1.5M\") were invisible to the 4-digit regex\n"
        "    .concat((String(s).replace(/[,$]/g, '').match(/\\b\\d+(?:\\.\\d+)?[km]\\b/gi) || []).map(function (n) { return n.toLowerCase(); }));",
        "Gate Verdict k/m figures")

    # 3. the claim filter: no-entity claims cannot block; text goes word-level
    gv = patch(gv,
        "  hClaims = (verdict.unsupported || []).filter(c => {\n"
        "    const ents = entitiesOf(c);\n"
        "    if (!ents.length) return true;                       // nothing checkable — trust the gate\n"
        "    return !ents.every(e => /^https?:\\/\\//.test(String(e))\n"
        "      ? idInEv(e)\n"
        "      : (/^[\\d.]+$/.test(String(e))\n"
        "          ? evNum.includes(String(e))\n"
        "          : ev.includes(String(e).toLowerCase().trim())));\n"
        "  });",
        "  hClaims = (verdict.unsupported || []).filter(c => {\n"
        "    const ents = entitiesOf(c);\n"
        "    // #53: a claim with NOTHING checkable is a paraphrase by construction (\"one member\n"
        "    // said they quoted over $10K/month\") - it cannot block alone; the catastrophic\n"
        "    // classes (invented people/links/quotes/figures) always carry an entity.\n"
        "    if (!ents.length) return false;\n"
        "    return !ents.every(e => /^https?:\\/\\//.test(String(e))\n"
        "      ? idInEv(e)\n"
        "      : (/^[\\d.]+[km]?$/i.test(String(e))\n"
        "          ? evNum.includes(String(e).toLowerCase())\n"
        "          : textEntityInEv(e)));\n"
        "  });",
        "Gate Verdict claim filter")

    # 4. the AGG filter's text check goes word-level too (same miss class)
    gv = patch(gv,
        "  const nonNum = entitiesOf(s).filter(e => !/^[\\d.]+$/.test(String(e)));\n"
        "  return !nonNum.every(e => /^https?:\\/\\//.test(String(e))\n"
        "    ? idInEv(e)\n"
        "    : ev.includes(String(e).toLowerCase().trim()));",
        "  const nonNum = entitiesOf(s).filter(e => !/^[\\d.]+[km]?$/i.test(String(e)));\n"
        "  return !nonNum.every(e => /^https?:\\/\\//.test(String(e))\n"
        "    ? idInEv(e)\n"
        "    : textEntityInEv(e));   // #53: word-level, same miss class",
        "Gate Verdict AGG filter")

    nodes["Gate Verdict"]["parameters"]["jsCode"] = gv

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(gv)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
    print("node --check: OK")

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    g2 = next(n for n in wf2["nodes"] if n["name"] == "Gate Verdict")["parameters"]["jsCode"]
    print("VERIFY helpers:", "textEntityInEv" in g2,
          "km:", "[km]\\b" in g2 or "[km]" in g2,
          "noent:", "cannot block alone" in g2,
          "agg:", "word-level, same miss class" in g2,
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
