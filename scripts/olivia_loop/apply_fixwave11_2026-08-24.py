#!/usr/bin/env python3
"""Fixwave 11 — repair the wave-9 regression in Answer Seed.

Wave 9 rewrote the `clip` helper to delegate to `clipSafe`:
    line 17  const clip = (s, n) => ... clipSafe(s, n) ...
    line 21  const text = clip(r.text, 1500);      <-- called here
    line 35  const clipSafe = (s, n) => {...}      <-- initialised 18 lines LATER
`clipSafe` is a const, so calling `clip` at line 21 hits the temporal dead zone:
"Cannot access 'clipSafe' before initialization". Every turn whose preload reaches line 21
errored — 89 of 255 turns in the overnight run, ~8 hours of a broken staging build.

Why it got through: the leak gate exercises RPCs and routes, not this node, and my single
post-apply probe ("who lives in Austin") happens to take a path that never reaches line 21.
One probe is not verification.

Fix: hoist the clipSafe definition ABOVE the first use. Nothing else changes.

  python3 scripts/olivia_loop/apply_fixwave11_2026-08-24.py [--dry]
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

def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    seed = nodes["Answer Seed"]; c = seed["parameters"]["jsCode"]

    CLIPSAFE = """const clipSafe = (s, n) => {
  if (s.length <= n) return s;
  let cut = s.slice(0, n);
  // never end inside a URL: if the tail after the last space starts a link, drop that fragment
  const sp = cut.lastIndexOf(' ');
  const tail = sp === -1 ? cut : cut.slice(sp + 1);
  if (/^https?:\\/\\//i.test(tail) && !/\\s/.test(s.slice(n, n + 1))) {
    cut = sp === -1 ? '' : cut.slice(0, sp);
  }
  return cut + '\\u2026';
};
"""
    assert c.count(CLIPSAFE) == 1, f"clipSafe block anchor drift ({c.count(CLIPSAFE)}x)"
    CLIP = """const clip = (s, n) => { s = String(s); return s.length > n ? clipSafe(s, n) : s; };"""
    assert c.count(CLIP) == 1, f"clip anchor drift ({c.count(CLIP)}x)"

    i_safe, i_clip = c.index(CLIPSAFE), c.index(CLIP)
    assert i_safe > i_clip, "already hoisted — nothing to do"

    # remove it from where it is, and re-insert immediately before the first use
    c = c.replace(CLIPSAFE, "", 1)
    c = c.replace(CLIP, "// fixwave 11: clipSafe is HOISTED here because `clip` below calls it and\n"
                        "// the first call site sits ~4 lines further down — as a const it was still in\n"
                        "// the temporal dead zone there, which hard-errored every turn that reached it.\n"
                        + CLIPSAFE + CLIP, 1)
    assert c.index(CLIPSAFE) < c.index(CLIP), "hoist failed"
    node_check(c, "Answer Seed")
    seed["parameters"]["jsCode"] = c

    if dry:
        print("DRY RUN — clipSafe hoisted above its first use, node --check clean.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    ac = {n["name"]: n for n in after["nodes"]}["Answer Seed"]["parameters"]["jsCode"]
    assert ac.index("const clipSafe") < ac.index("const clip ="), "hoist did not persist"
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
