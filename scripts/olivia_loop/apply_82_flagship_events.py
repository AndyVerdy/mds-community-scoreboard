#!/usr/bin/env python3
"""#82 — a Summit is a ROOM, a Channel Call is a TOPIC. Teach the loop the difference.

Andy, 2026-08-11: "summits and Inspire are not topic-specific… missing dossier for Summit or
Inspire is genuinely bad." He was right about both halves. The dossier builder keeps a topic
only at lift >= 1.3 over the community baseline; a flagship draws a representative slice of
MDS, so lift is ~1.0 on everything and the profile computed to {} — the Singapore Summit's
best was Sourcing & Suppliers at 1.29, discarding International Expansion (55 members),
Amazon FBA (41), Walmart / DTC & Shopify / Hiring & Team / Logistics & 3PL (38 each).

The SQL side now supplies both halves: event_series_profile.what_it_is (what kind of event it
is and how it runs, curated from the public mds.co pages) and entity_dossier.reception->'room'
(who is registered, counted by topic, category, revenue band and country). This script teaches
the loop to use them, and to stop treating a flagship as if it were about a subject.

Two patches, Answer Seed ONLY.
"""
import json, os, subprocess, sys, tempfile

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


def patch(text, old, new, where, marker):
    if marker in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


# ---- A: the tool description ------------------------------------------------------------
OLD_EL = ("{ name: 'event_lookup', description: 'JUDGED (#50): rows may carry fit_reason (who "
          "the room skews toward) and strength_note (how it draws) - use as judgment, never "
          "numbers. Upcoming MDS events (registration-open). Filter by topic terms, city, "
          "virtual. p_include_past for history questions.',")
NEW_EL = ("{ name: 'event_lookup', description: 'JUDGED (#50): rows may carry fit_reason (who "
          "the room skews toward) and strength_note (how it draws) - use as judgment, never "
          "numbers. Upcoming MDS events (registration-open). Filter by topic terms, city, "
          "virtual. p_include_past for history questions. FLAGSHIPS (#82): a Summit or Inspire "
          "row also carries what_it_is (what kind of event it is and how it runs) and room "
          "(who is registered, counted by topic, category, revenue band and country). A row "
          "without those two is an ordinary event - answer it the way you always have.',")

# ---- B: the rule --------------------------------------------------------------------------
OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"
NEW_RULE = (
    "  '- FLAGSHIP EVENTS ARE ROOMS (#82): a Summit or an Inspire is not about a topic, it is a "
    "room. When asked what one is, lead with what_it_is and the format it runs, then say who is "
    "actually registered using the counts in room - 55 people working on international expansion, "
    "38 scaling teams. Those numbers are member COUNTS and may be spoken. Never claim a flagship "
    "is about a subject, and never present a missing topic profile as not knowing what the event "
    "is. A one-hour call IS about a topic - describe those exactly as before.',\n"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]

    seed = patch(seed, OLD_EL, NEW_EL, "event_lookup schema",
                 "what_it_is (what kind of event")
    seed = patch(seed, OLD_RULE_TAIL, NEW_RULE + OLD_RULE_TAIL, "rule: flagships are rooms",
                 "FLAGSHIP EVENTS ARE ROOMS")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED on Answer Seed:\n{chk.stderr}"
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
    print("PUT + bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    s2 = {n["name"]: n for n in wf2["nodes"]}["Answer Seed"]["parameters"]["jsCode"]
    for marker in ("what_it_is (what kind of event", "FLAGSHIP EVENTS ARE ROOMS"):
        assert marker in s2, f"marker {marker!r} missing after PUT"
        print(f"  verified: {marker!r}")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
