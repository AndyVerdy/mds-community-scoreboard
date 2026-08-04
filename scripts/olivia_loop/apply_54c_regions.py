#!/usr/bin/env python3
"""#54c Regions ride the country filter — apply to STAGING (Andy: "go, add the regions").

DB shipped (migration member_match_v2_region_groups): country_region_countries expands
Europe / Eastern Europe / North America / Scandinavia / Asia / Middle East / Latin America /
Oceania to country sets inside member_match_v2 (single country = one-element set).
SQL-proven: Europe 86 · Eastern Europe 13 · Scandinavia 10 · Germany still 7 · Cyprus still 5.
This teaches the router + loop tool that regions are valid match_country values.
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
        'for a COUNTRY ("members in Cyprus", "based in '
        'Germany", "who is in Israel?") set match_country to the full country name.',
        'for a COUNTRY ("members in Cyprus", "based in '
        'Germany", "who is in Israel?") set match_country to the full country name; a REGION works '
        'the same way - "who is in Europe / Eastern Europe / North America / Scandinavia / Asia / '
        'the Middle East / Latin America?" -> match_country = that region name.',
        "Route Request region rule")
    nodes["Route Request"]["parameters"]["jsonBody"] = rr

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed,
        "p_country: str('country filter, e.g. Cyprus, Germany - use for any non-US country ask')",
        "p_country: str('country OR region filter, e.g. Cyprus, Germany, Europe, Eastern Europe, "
        "North America, Scandinavia - use for any non-US country or region ask')",
        "Answer Seed p_country regions")
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
          "router:", "a REGION works" in n2["Route Request"]["parameters"]["jsonBody"],
          "seed:", "country OR region filter" in n2["Answer Seed"]["parameters"]["jsCode"],
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
