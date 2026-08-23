#!/usr/bin/env python3
"""#32 (cache half) — 2026-08-23. STAGING bqHstPDi84uOhTCJ only; PROD never touched.

ROOT CAUSE (measured on execs 102219/102221, per-lap usage): `Answer Claude` sent
  tool_choice: ($json.iter === 0 ? { type: 'any' } : undefined)
and Anthropic invalidates the MESSAGES cache whenever tool_choice changes. So lap 1's cache
write (the whole seed: history + preload, 1.3-8.8K tokens) could never be read by lap 2, and
every turn boundary paid the same penalty in reverse. Signature: lap2 cache_r stays at the
static 31,696 while lap2 rewrites lap1's content +delta; lap3 then reads lap2's snapshot fine.

FIX, one variable:
  1. tool_choice constant: { type: 'auto' } on every lap.
  2. The forced-first-fetch guarantee (the reason 'any' existed) moves into CODE:
     Answer Parse — on the FIRST parse of the execution ($runIndex === 0), a response with no
     tool call re-fires the identical request once via a new IF lane
     (Answer Done? false -> First-Fetch Retry? -> retry_same ? Answer Claude : Voyage Embed).
     The prefix is cached, so the retry is nearly free. One retry, then the answer stands.

  python3 scripts/olivia_loop/apply_32_cache_2026-08-23.py [--dry]
"""
import json, os, subprocess, sys, tempfile, copy

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
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code); tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED for {label}:\n{chk.stderr}"
    print(f"  node --check OK ({label})")


def sub(hay, old, new, label, n=1):
    assert hay.count(old) == n, f"anchor drift: {label} found {hay.count(old)}x, want {n}"
    return hay.replace(old, new)


def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ---- EDIT 1: Answer Claude — constant tool_choice ------------------------------
    ac = nodes["Answer Claude"]
    ac["parameters"]["jsonBody"] = sub(
        ac["parameters"]["jsonBody"],
        "tool_choice: ($json.iter === 0 ? { type: 'any' } : undefined)",
        "tool_choice: { type: 'auto' }",
        "Answer Claude tool_choice")

    # ---- EDIT 2: Answer Parse — code-level first-fetch guarantee --------------------
    ap = nodes["Answer Parse"]
    code = ap["parameters"]["jsCode"]
    anchor = "const toolUses = content.filter(c => c && c.type === 'tool_use');"
    guard = anchor + """
// #32: tool_choice is CONSTANT (auto) now -- flipping it between laps invalidated the messages
// cache and doubled the write bill. The forced first fetch that {type:'any'} used to guarantee
// is enforced here instead: the first parse of the execution ($runIndex 0) with no tool call
// re-fires the identical request once (the prefix is cached, so the retry is nearly free).
// One retry only; a second no-tool answer stands and Fact Check polices it as usual.
if ($runIndex === 0 && state.iter === 0 && toolUses.length === 0) {
  return [{ json: Object.assign({}, state, { done: false, retry_same: true }) }];
}"""
    code = sub(code, anchor, guard, "Answer Parse retry guard")
    node_check(code, "Answer Parse")
    ap["parameters"]["jsCode"] = code

    # ---- EDIT 3: new IF node between Answer Done?(false) and Voyage Embed ----------
    assert "First-Fetch Retry?" not in nodes, "node already exists"
    done_pos = nodes["Answer Done?"]["position"]
    newnode = {
        "id": "ff-retry-32", "name": "First-Fetch Retry?", "type": "n8n-nodes-base.if",
        "typeVersion": 2.2, "position": [done_pos[0] + 180, done_pos[1] + 120],
        "parameters": {"conditions": {"combinator": "and", "conditions": [{
            "id": "r1", "leftValue": "={{ $json.retry_same === true }}",
            "operator": {"operation": "true", "singleValue": True, "type": "boolean"},
            "rightValue": True}],
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2}},
            "options": {}}}
    wf["nodes"].append(newnode)

    conns = wf["connections"]
    false_branch = conns["Answer Done?"]["main"][1]
    assert false_branch == [{"node": "Voyage Embed", "type": "main", "index": 0}], \
        f"Answer Done? false branch drifted: {false_branch}"
    conns["Answer Done?"]["main"][1] = [{"node": "First-Fetch Retry?", "type": "main", "index": 0}]
    conns["First-Fetch Retry?"] = {"main": [
        [{"node": "Answer Claude", "type": "main", "index": 0}],   # true  -> retry same request
        [{"node": "Voyage Embed", "type": "main", "index": 0}],    # false -> normal tool path
    ]}

    if dry:
        print("DRY RUN — all anchors hit, node --check OK, no write."); return

    payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": conns,
               "settings": wf.get("settings") or {}}
    r = api("PUT", f"/workflows/{STAGING}", payload)
    assert r.get("id") == STAGING, f"PUT failed: {json.dumps(r)[:300]}"
    b = api("POST", f"/workflows/{STAGING}/deactivate", {})
    assert b.get("active") is False, "deactivate failed"
    b = api("POST", f"/workflows/{STAGING}/activate", {})
    assert b.get("active") is True, "activate failed"

    back = api("GET", f"/workflows/{STAGING}")
    names = {n["name"] for n in back["nodes"]}
    assert "First-Fetch Retry?" in names
    acb = next(n for n in back["nodes"] if n["name"] == "Answer Claude")
    assert "tool_choice: { type: 'auto' }" in acb["parameters"]["jsonBody"]
    assert "$runIndex === 0" in next(n for n in back["nodes"] if n["name"] == "Answer Parse")["parameters"]["jsCode"]
    print(f"APPLIED + bounced. nodes {len(back['nodes'])} · versionId {back.get('versionId')}")


if __name__ == "__main__":
    main()
