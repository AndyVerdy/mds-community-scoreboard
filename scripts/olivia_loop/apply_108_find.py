#!/usr/bin/env python3
"""#108 — the finder tool, plus the event_who routing fix.

Three edits, one PUT, one bounce (STAGING only):
  Answer Tool  url + body gain a `find` branch -> /api/olivia/find, and every event_who call now
               carries op='people' (without it the schedule route falls through to op='next' and
               answers a people question with the public agenda — proven live 2026-08-22).
  Answer Seed  the `find` tool declaration (before multi_source)
  Answer Seed  one routing rule: filter-shaped people questions call find.
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
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


TOOL_DECL = (
    "  { name: 'find', description: 'FIND MEMBERS WITH FILTERS THAT COMBINE (#108). Build a WHERE tree: "
    "{all:[...]} = AND, {any:[...]} = OR, {not:{...}} = exclude, nesting freely; leaves are {field: value} "
    "and a LIST value means any-of. Fields: segment (what kind of seller: reseller | private label | brand "
    "owner | agency | oem | supplements | tiktok | dtc | retail | large sku | under 30), chat (chat name), "
    "event (event name words), city, state, country, chapter, band (1-5M | 5-10M | 10-20M | 20M+), niche, "
    "category, expertise (words in their expertise text), sku_min / brands_min / years_selling_min "
    "(numbers), age_band (20s|30s|40s|50+). Examples: resellers coming to the Summit = "
    "{all:[{segment:\\'reseller\\'},{event:\\'Summit Singapore\\'}]}; resellers OR supplement sellers = "
    "{segment:[\\'reseller\\',\\'supplements\\']}; resellers who ALSO sell supplements = "
    "{all:[{segment:\\'reseller\\'},{segment:\\'supplements\\'}]}; in Spain or Portugal but not in the TikTok "
    "chat = {all:[{any:[{country:\\'Spain\\'},{country:\\'Portugal\\'}]},{not:{chat:\\'MDS TikTok\\'}}]}. A "
    "segment is recognised from EVERY signal at once - declared business model, chat membership, profile "
    "flags - so a reseller is anyone in the MDS Resellers chat OR declaring wholesale on a form. Every person "
    "returns with the REASONS they matched, in the order asked - say them exactly as given; the tool names a "
    "chat only to its own members, never add a chat name yourself. ret=people gives names (max 10, with the "
    "true total), count gives the number, breakdown with group_by gives counts per value. To NARROW a previous "
    "answer, wrap where_echo from the last result: {all:[<where_echo>, {new condition}]}. Group-only fields "
    "(sku_min, brands_min, years_selling_min, age_band, large sku, under 30) return COUNTS ONLY - correct, not "
    "an error. Event names are returned only to someone registered for that event. NOT for meaning-based "
    "searches of what someone knows (expertise_search) and NOT yet for what was said (content_search, "
    "video_search).',\n"
    "    input_schema: S({ where: { type: 'object', description: 'the filter tree - see the examples; at least "
    "one condition' }, ret: str('people | count | breakdown'), "
    "group_by: str('country | state | city | band | niche | business_model | chat | chapter'), "
    "limit: num('max names, default 10') }, ['where']) },\n"
)

RULE = (
    "  '- FILTERED PEOPLE QUESTIONS GO TO find (#108): any who-is / who-is-coming question naming a GROUP - a "
    "chat, a kind of seller (resellers, agencies, private label, supplements, tiktok), a country, a chapter, a "
    "revenue band, an event roster, or several at once - is a FILTER question, not a topic search. Build the "
    "where tree from what the member actually said (and = all, or = any, except = not), call find, and say each "
    "person\\'s reasons exactly as the tool gave them - it names a chat only to that chat\\'s members, so never "
    "add one yourself. A follow-up that narrows (\\'of those, who is in Europe\\') wraps the last where_echo in "
    "an all with the new condition. When the tool returns a count with no names, that is the privacy rule "
    "doing its job: give the number, do not apologise, do not explain internals. Never answer a filter question "
    "by sampling topics, and never claim the listed names are everyone when the total is bigger.',\n"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    at = nodes["Answer Tool"]["parameters"]
    if "api/olivia/find" in at["url"]:
        print("Answer Tool: already wired")
    else:
        anchor = ("String($json.tool_name||'').startsWith('event_') ? "
                  "'https://digest.mds.co/api/olivia/schedule'")
        assert at["url"].count(anchor) == 1, f"Answer Tool url drifted:\n{at['url'][:300]}"
        at["url"] = at["url"].replace(
            anchor, "String($json.tool_name||'') === 'find' ? 'https://digest.mds.co/api/olivia/find' : " + anchor)

        body = at["jsonBody"]
        body_anchor = ("(String($json.tool_name||'').startsWith('event_') || "
                       "String($json.tool_name||'') === 'org_docs')")
        assert body.count(body_anchor) == 1, "Answer Tool body anchor not found"
        body = body.replace(body_anchor, body_anchor[:-1] + " || String($json.tool_name||'') === 'find')")
        phone_merge = "{ phone: $('Resolve Member').first().json.to }"
        assert body.count(phone_merge) == 1, "phone-merge shape drifted"
        body = body.replace(phone_merge,
            "Object.assign({ phone: $('Resolve Member').first().json.to }, "
            "String($json.tool_name||'') === 'event_who' ? { op: 'people' } : {})")
        at["jsonBody"] = body
        print("Answer Tool: find branch + event_who op='people'")

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    if "name: 'find'" in seed:
        print("Answer Seed: already declared")
    else:
        anchor = "  { name: 'multi_source',"
        assert seed.count(anchor) == 1, "multi_source anchor not found"
        seed = seed.replace(anchor, TOOL_DECL + anchor)
        rule_anchor = "  '- POLICY COMES FROM WRITTEN DOCUMENTS (#18)"
        assert seed.count(rule_anchor) == 1, "rule anchor not found"
        seed = seed.replace(rule_anchor, RULE + rule_anchor)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(seed); tmp = fh.name
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
    assert "api/olivia/find" in n2["Answer Tool"]["parameters"]["url"]
    assert "op: 'people'" in n2["Answer Tool"]["parameters"]["jsonBody"]
    assert "name: 'find'" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "FILTERED PEOPLE QUESTIONS GO TO find (#108)" in n2["Answer Seed"]["parameters"]["jsCode"]
    print(f"verified · staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
