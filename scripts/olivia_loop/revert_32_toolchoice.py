#!/usr/bin/env python3
"""Revert #32's tool_choice change ONLY (staging): constant {type:'auto'} -> the original
per-lap ternary. Keeps the First-Fetch Retry? lane in place — with 'any' forced on lap 1 the
guard can never fire, so it is dead but harmless, and removing it would churn the graph twice.

  python3 scripts/olivia_loop/revert_32_toolchoice.py [--dry]
"""
import json, subprocess, sys

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)

BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")

def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    ac = next(n for n in wf["nodes"] if n["name"] == "Answer Claude")
    body = ac["parameters"]["jsonBody"]
    new = "tool_choice: { type: 'auto' }"
    old = "tool_choice: ($json.iter === 0 ? { type: 'any' } : undefined)"
    assert body.count(new) == 1, f"anchor drift: found {body.count(new)}x"
    ac["parameters"]["jsonBody"] = body.replace(new, old)
    if dry:
        print("DRY RUN — anchor hit, no write."); return
    payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
               "settings": wf.get("settings") or {}}
    r = api("PUT", f"/workflows/{STAGING}", payload)
    assert r.get("id") == STAGING, f"PUT failed: {json.dumps(r)[:300]}"
    assert api("POST", f"/workflows/{STAGING}/deactivate", {}).get("active") is False
    assert api("POST", f"/workflows/{STAGING}/activate", {}).get("active") is True
    back = api("GET", f"/workflows/{STAGING}")
    assert old in next(n for n in back["nodes"] if n["name"] == "Answer Claude")["parameters"]["jsonBody"]
    print(f"REVERTED + bounced. versionId {back.get('versionId')}")

if __name__ == "__main__":
    main()
