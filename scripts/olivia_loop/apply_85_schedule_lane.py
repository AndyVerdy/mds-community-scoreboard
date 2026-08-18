#!/usr/bin/env python3
"""#85 Summit schedule lane — apply to STAGING.

Two edits, no new nodes:

1. `Answer Tool` learns a second destination. Tools named event_* go to
   https://digest.mds.co/api/olivia/schedule (the logic lives there, in git,
   not in a Postgres function); everything else keeps posting to
   /rest/v1/rpc/<tool_name> exactly as before. The node's Supabase credential
   still signs Authorization, so the lane authenticates on X-Olivia-Secret.
   The asker's PHONE is injected by the node, never by the model — otherwise
   an LLM could ask for another member's schedule.

2. `Answer Seed` gains the tool and the timezone rules (Andy 2026-08-17):
   in-person answers are always in the venue's zone; virtual carries both the
   content's zone and the member's; a timezone is never stored because it
   breaks the moment someone travels.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
ENDPOINT = "https://digest.mds.co/api/olivia/schedule"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")
SECRET = env("OLIVIA_IOS_SECRET")


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


TOOLS_ADD = (
    "  { name: 'event_schedule', description: 'The MDS Summit Singapore SCHEDULE — the only source for what is on, "
    "where it is, and who speaks when. ops: next (the asker\\'s next few activities), day (everything on one date, "
    "p_at=YYYY-MM-DD), where (find one activity by name, p_q), speaker (when and where a named person speaks, p_q). "
    "Returns only what THIS member may see; an activity missing from the result is not on their schedule and is never "
    "described as something MDS does not have. Every time comes back already worded in the venue\\'s timezone — quote it "
    "as given, never convert it. where/speaker carry a street address and a maps_url: offer the map, do not paste raw "
    "coordinates. location_known=false means the venue is genuinely not recorded — say so plainly.', "
    "args: { op: 'next|day|where|speaker', q: 'search text for where/speaker', at: 'ISO date or datetime' } },\n"
)

RULE_ADD = (
    "  'SUMMIT SCHEDULE AND TIMEZONES (#85)',\n"
    "  '- Any question about what is happening at the Summit, when, where, or who is speaking goes to event_schedule. "
    "Never answer a schedule question from events_catalog or from memory.',\n"
    "  '- NEVER convert or restate a time in another zone. The tool returns the venue-local wording already; repeat it "
    "verbatim. For an IN-PERSON event the venue timezone is the only correct answer, even to someone asking from home — "
    "it is the time their alarm has to be set to.',\n"
    "  '- For a VIRTUAL session, give the time in the content timezone AND in the member\\'s own, and name both zones.',\n"
    "  '- We do not know where the asker is standing. WhatsApp sends an instant, never a zone, and a stored timezone "
    "would be wrong the moment they travel. So never guess their local time and never say \\'your time\\'.',\n"
    "  '- Reminders: a relative ask (in 30 minutes, an hour before) is fine as asked. An absolute ask confirms the zone "
    "back — \\'I will remind you at 8:00 PM Singapore time.\\'',\n"
    "  '- When the answer has a place, offer the map rather than reciting an address twice.',\n"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ---- 1. Answer Tool: second destination + injected phone + lane secret
    tool = nodes["Answer Tool"]["parameters"]
    tool["url"] = (
        "={{ String($json.tool_name||'').startsWith('event_') ? '" + ENDPOINT + "' : "
        "'https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/' + $json.tool_name }}"
    )
    tool["jsonBody"] = (
        "={{ String($json.tool_name||'').startsWith('event_') "
        "? JSON.stringify(Object.assign({}, $json.tool_args||{}, "
        "{ phone: $('Resolve Member').first().json.to })) "
        ": $json.tool_args }}"
    )
    hdrs = tool["headerParameters"]["parameters"]
    if not any(h["name"] == "X-Olivia-Secret" for h in hdrs):
        hdrs.append({"name": "X-Olivia-Secret", "value": SECRET})
        print("  Answer Tool: X-Olivia-Secret header added")
    print("  Answer Tool: url + body routed for event_*")

    # ---- 2. Answer Seed: tool + rules
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed, "  { name: 'multi_source', description:",
                 TOOLS_ADD + "  { name: 'multi_source', description:",
                 "Answer Seed tools: event_schedule")
    seed = patch(seed,
                 "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',",
                 RULE_ADD + "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',",
                 "Answer Seed rules: schedule + timezone")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    # node --check BEFORE the write — a missing comma between two JS strings
    # broke staging for 15 minutes on 2026-08-16.
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
    print("  node --check: OK")

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
    s2 = n2["Answer Seed"]["parameters"]["jsCode"]
    t2 = n2["Answer Tool"]["parameters"]
    print("VERIFY tool:", "'event_schedule'" in s2,
          "· rules:", "SUMMIT SCHEDULE AND TIMEZONES (#85)" in s2,
          "· routed:", ENDPOINT in t2["url"],
          "· secret hdr:", any(h["name"] == "X-Olivia-Secret" for h in t2["headerParameters"]["parameters"]),
          "· active:", wf2.get("active"), "· version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
