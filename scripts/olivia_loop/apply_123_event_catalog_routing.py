#!/usr/bin/env python3
"""#123: route the event tools by NAME, so event_lookup reaches the events catalog — STAGING.

Verified on prod 22d81380, 2026-09-10. `Answer Tool` picks its URL with
`String($json.tool_name||'').startsWith('event_')`, so EVERY event tool lands on
https://digest.mds.co/api/olivia/schedule. That route never reads p_terms (it parses only
op/phone/q/at/event_id/lead/in_minutes) and always loads the newest row in the `event`
schema — today MDS Summit Singapore, which ended 2026-08-26. So a question about any other
event gets an over-event's agenda back, and Millie says she cannot find it. Reproduced live:
"what time does the SoFlo Chapter TikTok Tour Afterparty start?" -> "I'm not finding a
'SoFlo Chapter TikTok Tour Afterparty' on file anywhere", while
digest.event_lookup_v3(...['SoFlo Chapter TikTok Tour Afterparty']...) returns it:
2025-11-13 18:30, Miami.

Two of the four event tools are schedule-backed and must keep that route:
  event_schedule  the Summit run-of-show, op=agenda/next/where/recommend/partners/remind...
  event_who       one event's attendees, sent as op=people
The other two are catalog RPCs and must fall through to PostgREST:
  event_lookup  -> event_lookup_v3   (Attach Embedding's EXEC_NAME already renames it)
  event_history -> event_history_v2  (same)
Both are granted to service_role, like content_search_v2 which already goes this way, and
`Answer Parse` puts p_phone into every tool_args, so the RPC path needs no phone injection.

  python3 scripts/olivia_loop/apply_123_event_catalog_routing.py --dry-run DIR
  python3 scripts/olivia_loop/apply_123_event_catalog_routing.py            # edits STAGING, one bounce

Idempotent: the node is skipped once its url names event_schedule explicitly.
"""
import json, os, subprocess, sys

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
NODE = "Answer Tool"
TOOL = "String($json.tool_name||'')"
PREFIX_TEST = f"{TOOL}.startsWith('event_')"
NAME_TEST = f"{TOOL} === 'event_schedule' || {TOOL} === 'event_who'"


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


def patch(params):
    """url: the prefix branch becomes the two schedule-backed names.
       jsonBody: the same swap inside the phone-injection test."""
    if "'event_schedule'" in params.get("url", ""):
        return params, False
    for field in ("url", "jsonBody"):
        val = params[field]
        c = val.count(PREFIX_TEST)
        if c != 1:
            sys.exit(f"ABORT {NODE}.{field}: expected 1 occurrence of the prefix test, found {c}")
        # url has it bare inside a ternary chain; jsonBody has it first in an OR chain.
        # Parenthesise so precedence cannot change either expression's meaning.
        params[field] = val.replace(PREFIX_TEST, f"({NAME_TEST})")
    return params, True


def main():
    dry = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run" else None
    wf = api("GET", f"/workflows/{STAGING_ID}")
    if wf.get("id") != STAGING_ID:
        sys.exit(f"GET failed: {json.dumps(wf)[:300]}")
    print(f"staging {STAGING_ID} versionId {wf.get('versionId')} nodes {len(wf['nodes'])}")
    node = next((n for n in wf["nodes"] if n["name"] == NODE), None)
    if node is None:
        sys.exit(f"ABORT: node {NODE} not found")
    params, changed = patch(node["parameters"])
    if not changed:
        print(f"  {NODE}: already routes by name, skipped")
        if not dry:
            return
    else:
        node["parameters"] = params
        print(f"  {NODE}: url + jsonBody now route event_schedule/event_who to the schedule "
              f"endpoint; event_lookup/event_history fall through to rpc/")
    if dry:
        os.makedirs(dry, exist_ok=True)
        for field in ("url", "jsonBody"):
            p = os.path.join(dry, f"Answer_Tool.{field}.txt")
            open(p, "w").write(params[field] + "\n")
            print(f"  wrote {p}")
        print("dry run: nothing written to n8n")
        return
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok, versionId", r.get("versionId"))
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"))


if __name__ == "__main__":
    main()
