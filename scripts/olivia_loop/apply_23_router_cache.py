#!/usr/bin/env python3
"""#23 speed cut 1 — cache the router's static rubric (STAGING).

The Route Request system prompt is ~10K tokens of lane rules and examples, and it was
being sent as ONE plain string, so Haiku reprocessed all of it on every single turn
(measured 1.4-1.7s per turn, execs 56874/56894). The tail of that string is dynamic
(the asker's CHATS + RECENT CONVERSATION), which is exactly why the whole thing could
never cache as written.

This splits `system` into the two-block shape Answer Seed already uses:
  [0] the static rubric  -> cache_control: ephemeral   (identical bytes every turn)
  [1] 'CHATS: ' + ...    -> uncached                   (per-member, per-turn)

The concatenation order and content are byte-identical to before, so the model sees the
same prompt and routes the same way — this is a transport change, not a behaviour change.

⚠️ The whole jsonBody is a single-quoted JS string inside ={{ }}: this script does string
surgery on anchors and NEVER re-escapes, so the existing \\' escaping is preserved. A bare
apostrophe introduced here would truncate the expression and silently disable the router
(the exact failure that killed the fact-gate on 2026-07-30).

Idempotent: re-running detects the cached shape and exits without writing.
"""
import json, subprocess, sys, time

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
    for _ in range(3):
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
rr = nodes["Route Request"]
body = rr["parameters"]["jsonBody"]

if "cache_control" in body:
    print("Route Request already carries a cache breakpoint — nothing to do.")
    sys.exit(0)

# --- anchors, all three must be unique ---
HEAD = "system: 'You are a request router"
SPLIT = "\\n\\nCHATS: ' + JSON.stringify("
TAIL = ": ''), messages: [{ role: 'user'"
for a in (HEAD, SPLIT, TAIL):
    if body.count(a) != 1:
        sys.exit(f"anchor not unique ({body.count(a)}x), aborting before any write: {a[:40]}")

new = body.replace(HEAD, "system: [{ type: 'text', text: 'You are a request router", 1)
new = new.replace(
    SPLIT,
    "', cache_control: { type: 'ephemeral' } }, { type: 'text', text: 'CHATS: ' + JSON.stringify(",
    1)
new = new.replace(TAIL, ": '') }], messages: [{ role: 'user'", 1)

# the rubric text itself must be untouched — compare with all the structural tokens removed
strip = lambda s: (s.replace("system: [{ type: 'text', text: '", "system: '")
                    .replace("', cache_control: { type: 'ephemeral' } }, { type: 'text', text: 'CHATS: '",
                             "\\n\\nCHATS: '")
                    .replace(": '') }], messages:", ": ''), messages:"))
assert strip(new) == body, "round-trip mismatch — the prompt text would change, aborting"

rr["parameters"]["jsonBody"] = new
payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                        if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                 "saveDataErrorExecution", "saveDataSuccessExecution",
                                 "saveExecutionProgress", "saveManualExecutions", "timezone")}}
c1, _ = api("PUT", f"/workflows/{STAGING_ID}", payload)
c2, _ = api("POST", f"/workflows/{STAGING_ID}/deactivate")
c3, _ = api("POST", f"/workflows/{STAGING_ID}/activate")
print(f"PUT {c1} · bounce {c2}/{c3}")

code, back = api("GET", f"/workflows/{STAGING_ID}")
live = {n["name"]: n for n in back["nodes"]}["Route Request"]["parameters"]["jsonBody"]
print("verified live:", "cache_control" in live and live == new)
