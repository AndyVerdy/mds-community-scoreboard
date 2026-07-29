#!/usr/bin/env python3
"""Assemble the #21 answering loop onto the STAGING Olivia workflow.

Adds 7 nodes after Plan Request (route==='llm' branch only), leaves every
canned/deterministic route on its existing path, edits Format Reply's `to`
resolution, PUTs the graph back, bounces, and prints a diff summary.
Prod is untouched.
"""
import json, re, subprocess, sys, time

SCRATCH = "/private/tmp/claude-501/-Users-Born-Scorecard/3c099062-fce0-4904-a970-de366e21e940/scratchpad"
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
           "--connect-timeout", "20", "--max-time", "180", "-w", "\n%{http_code}"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    for attempt in range(3):
        r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                           capture_output=True, text=True)
        if r.returncode == 0:
            break
        time.sleep(3)
    body, _, code = r.stdout.rpartition("\n")
    return int(code), (json.loads(body) if body.strip() else None)

code, wf = api("GET", f"/workflows/{STAGING_ID}")
assert code == 200, wf
nodes = {n["name"]: n for n in wf["nodes"]}
conns = wf["connections"]

# ---- splice the proven STYLE block out of Build Prompt into Answer Seed ----
bp = nodes["Build Prompt"]["parameters"]["jsCode"]
m = re.search(r"(const STYLE = \[.*?\]\.join\(NL\);)", bp, re.S)
assert m, "STYLE block not found in Build Prompt"
style_src = m.group(1)

seed = open(f"{SCRATCH}/answer_seed.js").read()
seed = seed.replace(
    "const STYLE = $('Plan Request').first().json.__style_unused || null; // placeholder, replaced below\n", "")
assert "'__STYLE_BLOCK__'," in seed
seed = seed.replace("'__STYLE_BLOCK__',", "STYLE,")
# inject the STYLE const right before the SYSTEM assembly
anchor = "const today = new Date()"
assert anchor in seed
seed = seed.replace(anchor, style_src + "\n" + anchor)

parse = open(f"{SCRATCH}/answer_parse.js").read()
gatev = open(f"{SCRATCH}/gate_verdict.js").read()
merge = open(f"{SCRATCH}/answer_merge.js").read()

SUPA_CRED = {"httpHeaderAuth": {"id": "QHLDE4VHvm8jrVds", "name": "Supabase secret (digest mirror)"}}
ANTH_CRED = {"httpHeaderAuth": {"id": "p52LoFSxvkMgZ3F5", "name": "Anthropic API"}}

NEW = [
    {"id": "loop_route_if", "name": "Loop?", "type": "n8n-nodes-base.if", "typeVersion": 2.2,
     "position": [1900, 900], "parameters": {"conditions": {
         "options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "strict"},
         "combinator": "and",
         "conditions": [{"id": "r_llm", "leftValue": "={{ $('Plan Request').first().json.route }}",
                          "rightValue": "llm", "operator": {"type": "string", "operation": "equals"}}]},
         "options": {}}},
    {"id": "answer_seed", "name": "Answer Seed", "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [2100, 1050], "parameters": {"jsCode": seed}},
    {"id": "answer_claude", "name": "Answer Claude", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
     "position": [2300, 1050], "retryOnFail": True, "maxTries": 3, "waitBetweenTries": 2000,
     "onError": "continueRegularOutput", "credentials": ANTH_CRED,
     "parameters": {
         "method": "POST", "url": "https://api.anthropic.com/v1/messages",
         "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
         "sendHeaders": True,
         "headerParameters": {"parameters": [
             {"name": "anthropic-version", "value": "2023-06-01"},
             {"name": "content-type", "value": "application/json"}]},
         "sendBody": True, "specifyBody": "json",
         "jsonBody": "={{ JSON.stringify({ model: 'claude-sonnet-5', max_tokens: 2000, thinking: { type: 'disabled' }, system: $json.system, tools: $json.tools, tool_choice: ($json.iter === 0 ? { type: 'any' } : undefined), messages: $json.messages }) }}",
         "options": {"timeout": 120000}}},
    {"id": "answer_parse", "name": "Answer Parse", "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [2500, 1050], "parameters": {"jsCode": parse}},
    {"id": "answer_done_if", "name": "Answer Done?", "type": "n8n-nodes-base.if", "typeVersion": 2.2,
     "position": [2700, 1050], "parameters": {"conditions": {
         "options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"},
         "combinator": "and",
         "conditions": [{"id": "d1", "leftValue": "={{ $json.done }}", "rightValue": True,
                          "operator": {"type": "boolean", "operation": "true", "singleValue": True}}]},
         "options": {}}},
    {"id": "answer_tool", "name": "Answer Tool", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
     "position": [2700, 1250], "onError": "continueRegularOutput", "alwaysOutputData": True,
     "credentials": SUPA_CRED,
     "parameters": {
         "method": "POST",
         "url": "=https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/{{ $json.tool_name }}",
         "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
         "sendHeaders": True,
         "headerParameters": {"parameters": [
             {"name": "Content-Profile", "value": "digest"},
             {"name": "Accept-Profile", "value": "digest"},
             {"name": "Content-Type", "value": "application/json"}]},
         "sendBody": True, "specifyBody": "json",
         "jsonBody": "={{ $json.tool_args }}",
         "options": {"timeout": 30000}}},
    {"id": "answer_merge", "name": "Answer Merge", "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [2500, 1250], "parameters": {"jsCode": merge}},
    {"id": "voyage_embed", "name": "Voyage Embed", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
     "position": [2800, 1180], "onError": "continueRegularOutput", "alwaysOutputData": True,
     "credentials": {"httpHeaderAuth": {"id": "IYolME7EMwg3ySHS", "name": "Voyage API"}},
     "parameters": {
         "method": "POST", "url": "https://api.voyageai.com/v1/embeddings",
         "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
         "sendHeaders": True,
         "headerParameters": {"parameters": [{"name": "Content-Type", "value": "application/json"}]},
         "sendBody": True, "specifyBody": "json",
         "jsonBody": "={{ (() => { const a = JSON.parse($json.tool_args); const q = a.p_query || (Array.isArray(a.p_terms) ? a.p_terms.join(' ') : ''); return JSON.stringify({ model: 'voyage-3.5-lite', input: [String(q).slice(0, 400) || '(empty)'], input_type: 'query', output_dimension: 1024 }); })() }}",
         "options": {"timeout": 10000}}},
    {"id": "attach_embed", "name": "Attach Embedding", "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [2950, 1180], "parameters": {"jsCode": "// pair embeddings back onto the tool items by order; embed failures degrade to keyword search\nconst reqs = $('Answer Parse').all().map(i => i.json);\nconst resps = $input.all().map(i => i.json);\nreturn reqs.map((req, i) => {\n  const r = resps[i];\n  try {\n    const emb = r && r.data && r.data[0] && r.data[0].embedding;\n    if (emb && ['content_search','video_search'].includes(req.tool_name)) {\n      const a = JSON.parse(req.tool_args); a.p_embedding = JSON.stringify(emb);\n      return { json: Object.assign({}, req, { tool_args: JSON.stringify(a) }) };\n    }\n  } catch (e) {}\n  return { json: req };\n});"}},
    {"id": "fact_check", "name": "Fact Check", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
     "position": [2900, 1050], "retryOnFail": True, "maxTries": 2, "waitBetweenTries": 1500,
     "onError": "continueRegularOutput", "credentials": ANTH_CRED,
     "parameters": {
         "method": "POST", "url": "https://api.anthropic.com/v1/messages",
         "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
         "sendHeaders": True,
         "headerParameters": {"parameters": [
             {"name": "anthropic-version", "value": "2023-06-01"},
             {"name": "content-type", "value": "application/json"}]},
         "sendBody": True, "specifyBody": "json",
         "jsonBody": "={{ JSON.stringify({ model: 'claude-sonnet-5', max_tokens: 400, thinking: { type: 'disabled' }, system: 'You are a fact gate for an assistant that must never fabricate. Compare the DRAFT ANSWER against the EVIDENCE (raw tool results the assistant retrieved). List every concrete factual claim in the draft — a name, number, count, date, title, place, link or quote — that does not appear in or directly follow from the evidence. Greetings, offers, questions, advice framing and honest statements of not-knowing are not claims. Arithmetic over evidence numbers is supported. Output ONLY minified JSON: {\"unsupported\":[\"claim\",...],\"verdict\":\"pass\"} or {\"unsupported\":[...],\"verdict\":\"fail\"} — fail only when at least one concrete factual claim lacks support.', messages: [{ role: 'user', content: 'EVIDENCE:' + String.fromCharCode(10) + ($json.evidence || '(none)').slice(0, 40000) + String.fromCharCode(10) + String.fromCharCode(10) + 'DRAFT ANSWER:' + String.fromCharCode(10) + ($json.answer_text || '') }] }) }}",
         "options": {"timeout": 60000}}},
    {"id": "gate_verdict", "name": "Gate Verdict", "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [3100, 1050], "parameters": {"jsCode": gatev}},
    {"id": "gate_ok_if", "name": "Gate OK?", "type": "n8n-nodes-base.if", "typeVersion": 2.2,
     "position": [3300, 1050], "parameters": {"conditions": {
         "options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"},
         "combinator": "and",
         "conditions": [{"id": "g1", "leftValue": "={{ $json.done }}", "rightValue": True,
                          "operator": {"type": "boolean", "operation": "true", "singleValue": True}}]},
         "options": {}}},
]

# drop any previous iteration of these nodes, then add fresh
new_names = {n["name"] for n in NEW} | {"Embed?"}
wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in new_names] + NEW

# ---- rewire ----
# Plan Request now feeds Loop? ; Loop? true -> Answer Seed, false -> Embed Query
conns["Plan Request"] = {"main": [[{"node": "Loop?", "type": "main", "index": 0}]]}
conns["Loop?"] = {"main": [
    [{"node": "Answer Seed", "type": "main", "index": 0}],
    [{"node": "Embed Query", "type": "main", "index": 0}],
]}
conns["Answer Seed"] = {"main": [[{"node": "Answer Claude", "type": "main", "index": 0}]]}
conns["Answer Claude"] = {"main": [[{"node": "Answer Parse", "type": "main", "index": 0}]]}
conns["Answer Parse"] = {"main": [[{"node": "Answer Done?", "type": "main", "index": 0}]]}
conns["Answer Done?"] = {"main": [
    [{"node": "Fact Check", "type": "main", "index": 0}],
    [{"node": "Voyage Embed", "type": "main", "index": 0}],
]}
conns["Voyage Embed"] = {"main": [[{"node": "Attach Embedding", "type": "main", "index": 0}]]}
conns["Attach Embedding"] = {"main": [[{"node": "Answer Tool", "type": "main", "index": 0}]]}
conns["Fact Check"] = {"main": [[{"node": "Gate Verdict", "type": "main", "index": 0}]]}
conns["Gate Verdict"] = {"main": [[{"node": "Gate OK?", "type": "main", "index": 0}]]}
conns["Gate OK?"] = {"main": [
    [{"node": "Format Reply", "type": "main", "index": 0}],
    [{"node": "Answer Claude", "type": "main", "index": 0}],
]}
conns["Answer Tool"] = {"main": [[{"node": "Answer Merge", "type": "main", "index": 0}]]}
conns["Answer Merge"] = {"main": [[{"node": "Answer Claude", "type": "main", "index": 0}]]}

conns.pop("Embed?", None)   # stale key from the two-branch iteration

# ---- Format Reply: `to` comes from the loop when the loop answered ----
fr = nodes["Format Reply"]["parameters"]["jsCode"]
old_line = "const to = $('Build Prompt').first().json.to;"
new_line = ("const to = $('Answer Parse').isExecuted ? $('Answer Parse').first().json.to "
            ": $('Build Prompt').first().json.to;")
if old_line in fr:
    nodes["Format Reply"]["parameters"]["jsCode"] = fr.replace(old_line, new_line)
elif new_line not in fr:
    sys.exit("Format Reply `to` line not found — aborting before writing anything")

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": conns,
        "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                     if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                               "saveDataErrorExecution", "saveDataSuccessExecution",
                               "saveExecutionProgress", "saveManualExecutions", "timezone")}}
code, res = api("PUT", f"/workflows/{STAGING_ID}", body)
assert code == 200, (code, str(res)[:400])
c1, _ = api("POST", f"/workflows/{STAGING_ID}/deactivate")
c2, _ = api("POST", f"/workflows/{STAGING_ID}/activate")
print(f"PUT 200 · bounce {c1}/{c2}")

code, after = api("GET", f"/workflows/{STAGING_ID}")
names = [n["name"] for n in after["nodes"]]
print(f"staging now {len(names)} nodes; loop nodes present: "
      f"{[n for n in sorted(new_names) if n in names]}")
print("Plan Request ->", [x["node"] for x in after["connections"]["Plan Request"]["main"][0]])
