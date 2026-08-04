#!/usr/bin/env python3
"""#54 Country dimension for member lookups — apply to STAGING (bqHstPDi84uOhTCJ).

Etienne (Europe chapter head), live 2026-08-04 08:35: "who are the mds members based in
cyprus" — unanswerable four times, honestly declined, report filed. The data was present
all along (5 active Cyprus members once country values are folded: CY vs Cyprus).
DB side is shipped (migration member_match_v2_country_dim: digest.country_fold + p_country
in member_match_v2, proven: cyprus/CY both return the 5). This wires the lanes:

- Route Request: match_country in the schema, the country rule (US carve-out kept), one example.
- Plan Request: match branch passes p_country.
- Answer Seed: member_match tool schema + description gain the country filter.

Idempotent: anchors asserted, hunks skip when applied. No apostrophes in injected prompt text.
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

    # ── Route Request prompt ────────────────────────────────────────────────
    rr = nodes["Route Request"]["parameters"]["jsonBody"]
    rr = patch(rr,
        '"match_state":<FULL US state name or null>,"match_channel"',
        '"match_state":<FULL US state name or null>,"match_country":<country name or null>,"match_channel"',
        "Route Request schema match_country")
    rr = patch(rr,
        'For a NAMED place set match_city/match_state. "based in the US" or "in America" = country-wide: '
        'leave match_city AND match_state null and do NOT include "city"/"state" in match_dims.',
        'For a NAMED place set match_city/match_state; for a COUNTRY ("members in Cyprus", "based in '
        'Germany", "who is in Israel?") set match_country to the full country name. EXCEPTION - "based '
        'in the US" or "in America" = leave match_city, match_state AND match_country ALL null and do '
        'NOT include "city"/"state" in match_dims (most members are US; a US filter means everyone).',
        "Route Request country rule")
    rr = patch(rr,
        '\\n"any MDS meetups near Dallas?"',
        '\\n"who are the mds members based in cyprus?" -> {"intent":"match","chat":null,"period":null,'
        '"date_hint":null,"search_terms":[],"match_dims":[],"match_city":null,"match_state":null,'
        '"match_country":"Cyprus","member_name":null,"expertise_query":null,"event_virtual":null,'
        '"event_past":false,"followup":false}'
        '\\n"any MDS meetups near Dallas?"',
        "Route Request cyprus example")
    nodes["Route Request"]["parameters"]["jsonBody"] = rr

    # ── Plan Request match branch ───────────────────────────────────────────
    pr = nodes["Plan Request"]["parameters"]["jsCode"]
    pr = patch(pr,
        "  const tgtCategory = (typeof p.match_category === 'string' && p.match_category.trim()) ? p.match_category.trim().slice(0, 60) : null;\n"
        "  const absolute = tgtCity || tgtState || tgtChannel || tgtCategory;",
        "  const tgtCategory = (typeof p.match_category === 'string' && p.match_category.trim()) ? p.match_category.trim().slice(0, 60) : null;\n"
        "  // #54 (Etienne, live 2026-08-04): country is a first-class place filter - the warehouse\n"
        "  // held all 5 Cyprus members while the lane had no way to ask for them.\n"
        "  const tgtCountry = (typeof p.match_country === 'string' && p.match_country.trim()) ? p.match_country.trim().slice(0, 60) : null;\n"
        "  const absolute = tgtCity || tgtState || tgtChannel || tgtCategory || tgtCountry;",
        "Plan Request tgtCountry")
    pr = patch(pr,
        "  if (tgtCategory) { params.p_category = tgtCategory; }",
        "  if (tgtCategory) { params.p_category = tgtCategory; }\n"
        "  if (tgtCountry) { params.p_country = tgtCountry; }",
        "Plan Request p_country param")
    nodes["Plan Request"]["parameters"]["jsCode"] = pr

    # ── Answer Seed member_match tool ───────────────────────────────────────
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed,
        "{ name: 'member_match', description: 'Find members BY ATTRIBUTE: city/state/category/revenue-band/channel.",
        "{ name: 'member_match', description: 'Find members BY ATTRIBUTE: city/state/COUNTRY/category/revenue-band/channel.",
        "Answer Seed member_match description")
    seed = patch(seed,
        "p_state: str('state filter'), p_channel: str('sales channel filter')",
        "p_state: str('state filter'), p_country: str('country filter, e.g. Cyprus, Germany - use for any non-US country ask'), p_channel: str('sales channel filter')",
        "Answer Seed member_match p_country")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    for name in ("Plan Request", "Answer Seed"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(nodes[name]["parameters"]["jsCode"])
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED on {name}:\n{chk.stderr}"
    print("node --check: OK (2 code nodes)")

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
          "router:", "match_country" in n2["Route Request"]["parameters"]["jsonBody"],
          "plan:", "p_country = tgtCountry" in n2["Plan Request"]["parameters"]["jsCode"],
          "seed:", "p_country: str('country filter" in n2["Answer Seed"]["parameters"]["jsCode"],
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
