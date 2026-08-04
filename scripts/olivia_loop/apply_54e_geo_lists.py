#!/usr/bin/env python3
"""#54e Model-supplied geo lists — apply to STAGING (Andy's "calculated per request" ruling).

DB shipped (migrations member_match_v2_list_geo + member_match_v2_uses_geo_sets):
p_country/p_state accept a single value, a known region keyword, OR a comma-separated list —
each token expands independently. SQL-proven: "Greece, Bulgaria, Romania, Slovenia" 5 ·
"Scandinavia, Germany" 17 · "texas, oklahoma, LA" 56 · the South 184 / Texas 52 / Cyprus 5
unchanged. This teaches the LOOP MODEL to do the geography per request: an unlisted grouping
("the Balkans", "DACH", "the Gulf") becomes a model-written country list.
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

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed,
        "p_country: str('country OR region filter, e.g. Cyprus, Germany, Europe, Eastern Europe, "
        "North America, Scandinavia - use for any non-US country or region ask')",
        "p_country: str('country, region, OR comma-separated country list. Known regions (Europe, "
        "Eastern Europe, North America, Scandinavia, Asia, Middle East, Latin America) expand "
        "automatically. For any OTHER grouping, DO THE GEOGRAPHY YOURSELF and pass the countries: "
        "the Balkans -> Greece, Bulgaria, Romania, Slovenia; DACH -> Germany, Switzerland, Austria')",
        "Answer Seed p_country lists")
    seed = patch(seed,
        "p_state: str('US state OR region filter - Texas or TX, or a region: Southern states, "
        "Midwest, New England, West Coast, East Coast, Tri-State, DMV')",
        "p_state: str('US state, region, OR comma-separated state list. Known regions (Southern "
        "states, Midwest, New England, West Coast, East Coast, Tri-State, DMV) expand "
        "automatically; for any other grouping pass the states yourself: the Carolinas -> "
        "North Carolina, South Carolina')",
        "Answer Seed p_state lists")
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
    s2 = next(n for n in wf2["nodes"] if n["name"] == "Answer Seed")["parameters"]["jsCode"]
    print("VERIFY",
          "country:", "DO THE GEOGRAPHY YOURSELF" in s2,
          "state:", "the Carolinas" in s2,
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
