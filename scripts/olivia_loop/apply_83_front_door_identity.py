#!/usr/bin/env python3
"""#83 — the front door resolves through the identity layer, not chat presence.

Jerome Acevedo (staff, valid record, resolve_asker resolves him fine) was told "I cannot
match this number to an MDS membership yet". So was Keith Gipson — the member #77 cited as
its own proof. The cause: #77 repointed 53 retrieval functions at the identity layer but was
a SQL-only ticket, so the n8n Find Member node still asked

    /rest/v1/members?phone=eq.<from>

and digest.members only holds people who appear in a synced WhatsApp chat. The rooms knew
who you were; the door did not.

Measured 2026-08-14: 734 active members reachable per the identity layer, 567 findable by
the door, **167 refused at hello**. Never caught because every automated probe fires as
17866578153, which HAS a members row — the failing path was never exercised.

This swaps Find Member onto digest.olivia_front_door(p_phone), which tries the exact-phone
match first (today's behaviour byte for byte) and only then resolves through resolve_asker.
Resolve Member is untouched: it still owns the active/inactive decision and its wording.

Proven before this script ran: 167/167 previously-blocked members now resolve, exactly one
row each, zero ambiguous; and all 649 members who already worked return an identical row —
same identity, same chat access.
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


OLD_URL = ("=https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/members?phone=eq.{{ $json.from }}"
           "&select=phone,full_name,name,membership_status,at_member_id,airtable_id,"
           "channels_present,olivia_welcomed_at,olivia_optout_at")
NEW_URL = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/olivia_front_door"


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    fm = nodes["Find Member"]
    p = fm["parameters"]

    if p.get("url") == NEW_URL and p.get("method") == "POST":
        print("  Find Member: already on the identity door")
    else:
        assert p.get("url") == OLD_URL, (
            f"Find Member url is not the expected pre-#83 value — aborting.\n  got: {p.get('url')[:160]}")
        # POST to the RPC; the phone WhatsApp sends goes in the body, not the query string,
        # so normalisation lives in SQL where the gate can test it.
        p["url"] = NEW_URL
        p["method"] = "POST"
        p["sendBody"] = True
        p["specifyBody"] = "json"
        p["jsonBody"] = "={{ JSON.stringify({ p_phone: $json.from }) }}"
        # the RPC needs Content-Profile to reach the digest schema; Accept-Profile alone is
        # a GET-side header and does nothing on a POST /rpc call.
        hp = p.setdefault("headerParameters", {}).setdefault("parameters", [])
        names = {h.get("name") for h in hp}
        if "Content-Profile" not in names:
            hp.append({"name": "Content-Profile", "value": "digest"})
        if "Content-Type" not in names:
            hp.append({"name": "Content-Type", "value": "application/json"})
        print("  Find Member: switched to digest.olivia_front_door")

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
    fm2 = {n["name"]: n for n in wf2["nodes"]}["Find Member"]["parameters"]
    assert fm2["url"] == NEW_URL and fm2["method"] == "POST", "node did not take"
    assert "p_phone" in fm2.get("jsonBody", ""), "phone not passed to the RPC"
    hdrs = {h["name"] for h in fm2["headerParameters"]["parameters"]}
    assert "Content-Profile" in hdrs, "Content-Profile missing — the RPC would 404"
    print(f"  verified: POST -> olivia_front_door, p_phone bound, Content-Profile set")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
