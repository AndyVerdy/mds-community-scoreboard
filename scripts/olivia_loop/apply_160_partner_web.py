#!/usr/bin/env python3
"""#160: the partner_lookup tool description tells the model what the three new columns are.

partner_lookup_v2 now returns web_summary / web_people / web_pricing — what the partner says on
its OWN website (crawled + extracted under #160, table digest.partner_web_profile). The tool
result already carries the fields; this one edit in `Answer Seed` tells the model how to use
them: what the partner does, who runs it, what it costs — always as "their site says", never
as member judgment (reviews, FB and WA talk stay the verdict layer). One edit, `old` exactly
once (verified against prod d40a837d on 2026-09-03).

  python3 scripts/olivia_loop/apply_160_partner_web.py          # edits STAGING, one bounce
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


EDITS = {
    "Answer Seed": [
        ("MDS partner deals directory: search by need/company name, or browse featured. "
         "Returns deal, rating, reviews, link.'",
         "MDS partner deals directory: search by need/company name, or browse featured. "
         "Returns deal, rating, reviews, link. WEB PROFILE (#160): rows may carry web_summary "
         "(what the partner does, in its own words), web_people (founders/leaders named on its "
         "site) and web_pricing (its stated pricing) - crawled from the partner\\'s OWN website. "
         "Use them to say what a partner does, who runs it and what it costs, ALWAYS framed as "
         "what their site says; they are partner-stated, never member judgment - reviews and "
         "member comments remain the verdict. A founder named in web_people IS that partner: "
         "\\'Mudit\\' and \\'Prosperlytics\\' are one firm.'"),
    ],
}


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
        if n["name"] not in EDITS:
            continue
        code = n["parameters"]["jsCode"]
        for old, new in EDITS[n["name"]]:
            c = code.count(old)
            if c != 1:
                sys.exit(f"ABORT {n['name']}: expected 1 occurrence, found {c}\n  {old[:90]}")
            code = code.replace(old, new)
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {n['name']}: node --check failed\n{err}")
        n["parameters"]["jsCode"] = code
        changed += 1
        print(f"  {n['name']}: {len(EDITS[n['name']])} replacements, node --check OK")
    if changed != 1:
        sys.exit(f"ABORT: expected 1 node changed, got {changed}")
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
