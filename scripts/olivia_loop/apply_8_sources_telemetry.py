#!/usr/bin/env python3
"""#8 — persist which source families each turn consulted (STAGING).

The loop now accumulates `sources_used` (tool names per round, answer_parse.js) and threads
it through answer_merge.js. This script wires the last leg:
  1. Format Reply passes `sources_used` through from Answer Parse's final item.
  2. Save Conversation stores it inside the olivia row's `plan` jsonb (plan.sources_used),
     so per-turn coverage is a measured number (SQL: plan->'sources_used').

Idempotent: asserts anchors, exits 0 if already applied. Python string ops on a full-graph
PUT — no patchNodeField $-expansion trap.
"""
import json, subprocess, sys

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


wf = api("GET", f"/workflows/{STAGING_ID}")
nodes = {n["name"]: n for n in wf["nodes"]}
changed = False

# --- 1. Format Reply: pass sources_used through ---
fr = nodes["Format Reply"]["parameters"]["jsCode"]
if "sources_used" not in fr:
    a1 = "const to = $('Answer Parse').isExecuted ? $('Answer Parse').first().json.to : $('Build Prompt').first().json.to;"
    assert a1 in fr, "Format Reply `to` anchor missing"
    fr = fr.replace(a1, a1 + "\nconst sourcesUsed = $('Answer Parse').isExecuted ? ($('Answer Parse').first().json.sources_used || null) : null;", 1)
    a2 = "return [{ json: { to: to, reply: text, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone } }];"
    assert a2 in fr, "Format Reply return anchor missing"
    fr = fr.replace(a2, "return [{ json: { to: to, reply: text, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone, sources_used: sourcesUsed } }];", 1)
    nodes["Format Reply"]["parameters"]["jsCode"] = fr
    changed = True

# --- 2. Save Conversation: plan.sources_used on the olivia row ---
sc = nodes["Save Conversation"]["parameters"]["jsonBody"]
if "sources_used" not in sc:
    a3 = "catch (e) { plan = null; }"
    assert a3 in sc, "Save Conversation plan anchor missing"
    fix = ("catch (e) { plan = null; } "
           "try { const su = src.sources_used; if (su && su.length) "
           "{ plan = Object.assign(plan || {}, { sources_used: su }); } } catch (e) {}")
    sc = sc.replace(a3, fix, 1)
    nodes["Save Conversation"]["parameters"]["jsonBody"] = sc
    changed = True

if not changed:
    print("already applied")
    sys.exit(0)

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
ok1 = "sources_used" in n2["Format Reply"]["parameters"]["jsCode"]
ok2 = "sources_used" in n2["Save Conversation"]["parameters"]["jsonBody"]
print(f"VERIFY format_reply:{ok1} save_conversation:{ok2} active:{wf2.get('active')}")
assert ok1 and ok2
