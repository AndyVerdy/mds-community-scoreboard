#!/usr/bin/env python3
"""#20f — the census topic map never mentioned the questions that were unreadable.

Fix ① gave the 13 matrix rows a real label ("How do you handle each of these areas?
(Bookkeeping)"), and fix ② brought back DTC revenue share and the MDS UX rating. The
data answers now — but the model still did not know those questions exist: a staging
probe for "how do members handle bookkeeping and customer service?" answered entirely
from chat anecdotes while the census held Bookkeeping 60.7% in-house.

So the topic map in the form_stats description gains the newly-readable topics.
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


OLD = "brands, products, kids."

NEW = ("brands, products, kids · WHO HANDLES WHAT — every marketing channel (Amazon Advertising, "
       "Meta, Google, TikTok, SMS/Email, PR/influencers) and every ops area (product development, "
       "launches, customer service, bookkeeping, marketplace management, graphic design, "
       "dev/software) answered in-house vs agency vs freelancer · DTC/own-website revenue share · "
       "how members rate MDS (systems/UX, visual branding, chapter events, NPS).")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed, OLD, NEW, "form_stats description: matrix + rating topics")
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
    s2 = next(n for n in wf2["nodes"] if n["name"] == "Answer Seed")["parameters"]["jsCode"]
    print("VERIFY", "topic map:", "WHO HANDLES WHAT" in s2,
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
