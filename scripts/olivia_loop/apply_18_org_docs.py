#!/usr/bin/env python3
"""#18 — wire the org knowledge library into the loop.

Three edits, one PUT, one bounce:
  Answer Tool   url + body expressions gain the org_docs branch -> /api/olivia/kb
  Answer Seed   the org_docs tool declaration (before multi_source)
  Answer Seed   one routing rule: how-MDS-works / event-logistics POLICY asks call
                org_docs, answer FROM the written entry, cite the document, and an
                empty result means "no written answer exists yet" — never guessed.
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


URL_OLD = ("={{ String($json.tool_name||'').startsWith('event_') ? "
           "'https://digest.mds.co/api/olivia/schedule' : "
           "'https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/' + $json.tool_name }}")
URL_NEW = ("={{ String($json.tool_name||'') === 'org_docs' ? 'https://digest.mds.co/api/olivia/kb' : "
           "String($json.tool_name||'').startsWith('event_') ? "
           "'https://digest.mds.co/api/olivia/schedule' : "
           "'https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/' + $json.tool_name }}")

TOOL_DECL = ("  { name: 'org_docs', description: 'WRITTEN ANSWERS FROM MDS TEAM DOCUMENTS (#18) — "
             "THE source for how-MDS-works and event-logistics POLICY questions: refunds and "
             "cancellation, ticket and guest pricing policy, hotel policies, kid and guest rules, "
             "how programs and processes work. Each entry names its source document — CITE it. An "
             "empty result means no team document covers it: say plainly that no written answer "
             "exists yet, never guess policy.',\n"
             "    input_schema: S({ q: str('the question, in natural words') }) },\n")

RULE = ("  '- POLICY COMES FROM WRITTEN DOCUMENTS (#18): refund/cancellation terms, ticket and "
        "guest pricing POLICY, hotel rules, kid/guest rules, how a program works — call org_docs "
        "and answer FROM the returned entry, naming the source document. Live numbers that "
        "structured tools carry (headcounts, schedules, stats) still come from those tools, never "
        "from document prose. If org_docs returns empty, say no written answer exists yet — never "
        "invent policy.',\n")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    at = nodes["Answer Tool"]["parameters"]
    if "org_docs" in at["url"]:
        print("Answer Tool: already wired")
    else:
        assert at["url"] == URL_OLD, f"Answer Tool url drifted:\n{at['url'][:200]}"
        at["url"] = URL_NEW
        body = at["jsonBody"]
        anchor = "String($json.tool_name||'').startsWith('event_')"
        assert body.count(anchor) == 1, "body anchor not found"
        at["jsonBody"] = body.replace(
            anchor,
            "(String($json.tool_name||'').startsWith('event_') || String($json.tool_name||'') === 'org_docs')")
        print("Answer Tool: org_docs branch added (url + body)")

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    if "org_docs" in seed:
        print("Answer Seed: already declared")
    else:
        anchor = "  { name: 'multi_source',"
        assert seed.count(anchor) == 1, "multi_source anchor not found"
        seed = seed.replace(anchor, TOOL_DECL + anchor)
        rule_anchor = "  '- REMINDERS ARE REAL NOW."
        assert seed.count(rule_anchor) == 1, "rule anchor not found"
        seed = seed.replace(rule_anchor, RULE + rule_anchor)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(seed)
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
        nodes["Answer Seed"]["parameters"]["jsCode"] = seed
        print("Answer Seed: tool + rule added, node --check OK")

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")
    print("PUT + one bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    assert "org_docs" in n2["Answer Tool"]["parameters"]["url"]
    assert "org_docs" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "POLICY COMES FROM WRITTEN DOCUMENTS (#18)" in n2["Answer Seed"]["parameters"]["jsCode"]
    print(f"verified · staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
