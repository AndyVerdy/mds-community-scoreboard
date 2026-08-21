#!/usr/bin/env python3
"""Respell the bot's name Mille -> Millie (Andy 2026-08-21, display name "MDS Millie").

Touches the same four staging nodes #91 named (Build Prompt, Answer Seed,
Build Generic, Build Verbatim Digest), replacing the bare token 'Mille' with
'Millie' — collision-safe: no existing string contains 'Mille' as part of a
longer word, and 'Millie' does not contain 'Mille'. Expected counts asserted
per node; node --check on every changed node; ONE deactivate/activate bounce.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
EXPECT = {"Build Prompt": 3, "Answer Seed": 3,
          "Build Generic": 3, "Build Verbatim Digest": 3}


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


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    changed = 0
    for n in wf["nodes"]:
        if n["name"] not in EXPECT:
            continue
        code = n["parameters"].get("jsCode", "")
        cnt = code.count("Mille")
        if cnt != EXPECT[n["name"]]:
            sys.exit(f"ABORT {n['name']}: expected {EXPECT[n['name']]} 'Mille', found {cnt}")
        new = code.replace("Mille", "Millie")
        ok, err = node_check(new)
        if not ok:
            sys.exit(f"ABORT {n['name']}: node --check failed\n{err}")
        n["parameters"]["jsCode"] = new
        changed += 1
        print(f"  {n['name']}: {cnt} replaced, node --check OK")
    if changed != 4:
        sys.exit(f"ABORT: expected 4 nodes changed, got {changed}")

    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok")
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"))


if __name__ == "__main__":
    main()
