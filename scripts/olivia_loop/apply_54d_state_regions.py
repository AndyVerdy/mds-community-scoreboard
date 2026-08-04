#!/usr/bin/env python3
"""#54d US state regions — apply to STAGING (Andy: "go, add the state regions").

DB shipped (migration member_match_v2_state_regions): state_region_states expands
Southern states / the South / Southeast / Midwest / Northeast / New England / West Coast /
East Coast / Pacific Northwest / Southwest / Mountain West / Tri-State / DMV to state sets
inside member_match_v2 (single state = one-element set; attr_state still folds TX->Texas).
SQL-proven: South 184 · Midwest 38 · West Coast 126 · New England 14 · Tri-State 65 ·
Texas still 52 · Eastern Europe still 13.
This teaches the router + loop tool that US regions are valid match_state values.
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

    rr = nodes["Route Request"]["parameters"]["jsonBody"]
    rr = patch(rr,
        'always fill match_state with the FULL state name when known.',
        'always fill match_state with the FULL state name when known. A US REGION is also a valid '
        'match_state, passed as asked: "Southern states", "the South", "Southeast", "Midwest", '
        '"Northeast", "New England", "West Coast", "East Coast", "Pacific Northwest", "Southwest", '
        '"Mountain West", "Tri-State", "DMV" - "who is in the south?" -> match_state="the South".',
        "Route Request state-region rule")
    nodes["Route Request"]["parameters"]["jsonBody"] = rr

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed,
        "p_state: str('state filter')",
        "p_state: str('US state OR region filter - Texas or TX, or a region: Southern states, "
        "Midwest, New England, West Coast, East Coast, Tri-State, DMV')",
        "Answer Seed p_state regions")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
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
    n2 = {n["name"]: n for n in wf2["nodes"]}
    print("VERIFY",
          "router:", "A US REGION is also a valid" in n2["Route Request"]["parameters"]["jsonBody"],
          "seed:", "US state OR region filter" in n2["Answer Seed"]["parameters"]["jsCode"],
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
