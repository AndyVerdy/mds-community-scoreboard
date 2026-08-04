#!/usr/bin/env python3
"""#29 Personalization layer — apply to STAGING (bqHstPDi84uOhTCJ).

Wires the #29 v2 RPCs (member_dossier_v2 · event_lookup_v2 · event_history_v2 ·
chat_recommendations_v2 · member_match_v2 · multi_source_v2) into the workflow and
teaches the prompts to use what they return. Execution-layer swap, #40's pattern:
the MODEL and Plan Request keep the v1 names; the last inch maps them to v2.

1. Fetch Summaries + Fetch Raw Matches — URL map v1→v2 (op and raw_op).
2. Attach Embedding — EXEC_NAME map extended (loop tool calls execute v2).
3. Build Prompt:
   dossier  — renders strengths / working-on / behaviour / circle, framed warmly.
   solve    — ABOUT THE ASKER block (me section) + a personalize rule.
   multi    — same.
   events   — MEMBER CONTEXT gains their interest topics; recommend rule reads them.
4. Build Verbatim Digest (chats) — renders the personal why line per recommendation.

Idempotent: every hunk asserts its anchor and skips when already applied.
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


V2MAP_JS = ("({content_search:'content_search_v2',member_dossier:'member_dossier_v2',"
            "event_lookup:'event_lookup_v2',event_history:'event_history_v2',"
            "chat_recommendations:'chat_recommendations_v2',member_match:'member_match_v2',"
            "multi_source:'multi_source_v2'})")


def patch(text, old, new, where):
    if new in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x, expected 1 — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ── 1. the two fetch URLs ────────────────────────────────────────────────
    fs = nodes["Fetch Summaries"]["parameters"]
    fs["url"] = patch(fs["url"],
        "((o) => o === 'content_search' ? 'content_search_v2' : o)($('Plan Request').first().json.op)",
        "((o) => " + V2MAP_JS + "[o] || o)($('Plan Request').first().json.op)",
        "Fetch Summaries url")

    fr = nodes["Fetch Raw Matches"]["parameters"]
    fr["url"] = patch(fr["url"],
        "((o) => o === 'content_search' ? 'content_search_v2' : o)($('Plan Request').first().json.raw_op || 'content_search')",
        "((o) => " + V2MAP_JS + "[o] || o)($('Plan Request').first().json.raw_op || 'content_search')",
        "Fetch Raw Matches url")

    # ── 2. loop tools execute v2 (model keeps the v1 names) ──────────────────
    ae = nodes["Attach Embedding"]["parameters"]
    ae["jsCode"] = patch(ae["jsCode"],
        "const EXEC_NAME = { content_search: 'content_search_v2' };",
        "const EXEC_NAME = { content_search: 'content_search_v2', member_dossier: 'member_dossier_v2', "
        "event_lookup: 'event_lookup_v2', event_history: 'event_history_v2', "
        "chat_recommendations: 'chat_recommendations_v2', member_match: 'member_match_v2', "
        "multi_source: 'multi_source_v2' };",
        "Attach Embedding EXEC_NAME")

    # ── 3. Build Prompt ──────────────────────────────────────────────────────
    bp = nodes["Build Prompt"]["parameters"]["jsCode"]

    # dossier: collect the #29 kinds
    bp = patch(bp,
        "  const pastEv = dos.filter(function (d) { return d.kind === 'past_event'; });\n  const lines = [];",
        "  const pastEv = dos.filter(function (d) { return d.kind === 'past_event'; });\n"
        "  // #29: the assembled dossier — strengths, what they are building, behaviour, circle\n"
        "  const dStr = dos.filter(function (d) { return d.kind === 'strength'; });\n"
        "  const dWork = dos.filter(function (d) { return d.kind === 'working_on'; });\n"
        "  const dBeh = dos.filter(function (d) { return d.kind === 'behaviour'; });\n"
        "  const dCirc = dos.filter(function (d) { return d.kind === 'circle'; });\n"
        "  const lines = [];",
        "Build Prompt dossier collect")

    bp = patch(bp,
        "  if (pastEv.length) { lines.push('PAST EVENT REGISTRATIONS:' + NL + pastEv.map(function (e) { return '- ' + e.label + ' (' + e.detail + ')'; }).join(NL)); }\n  const activity = lines.join(NL + NL);",
        "  if (pastEv.length) { lines.push('PAST EVENT REGISTRATIONS:' + NL + pastEv.map(function (e) { return '- ' + e.label + ' (' + e.detail + ')'; }).join(NL)); }\n"
        "  if (dStr.length) { lines.push('STRENGTHS (from their MDS profile + activity):' + NL + dStr.map(function (s) { return '- ' + s.label + (s.detail ? ' - ' + s.detail : ''); }).join(NL)); }\n"
        "  if (dWork.length) { lines.push('WHAT THEY ARE BUILDING UP RIGHT NOW:' + NL + dWork.map(function (s) { return '- ' + s.label + (s.detail ? ' - ' + s.detail : ''); }).join(NL)); }\n"
        "  if (dBeh.length) { lines.push('HOW THEY USE MDS (their own activity, last 90 days):' + NL + dBeh.map(function (b) { return '- ' + b.label + ': ' + b.detail; }).join(NL)); }\n"
        "  if (dCirc.length) { lines.push('PEOPLE THEY CROSS PATHS WITH MOST (shared chats and events):' + NL + dCirc.map(function (c) { return '- ' + c.label + ' (' + c.detail + ')'; }).join(NL)); }\n"
        "  const activity = lines.join(NL + NL);",
        "Build Prompt dossier render")

    bp = patch(bp,
        "    '- Their events: upcoming registrations (\"you are booked for...\") and a feel for their history (\"you have been to X, Y and Z\").',",
        "    '- Their events: upcoming registrations (\"you are booked for...\") and a feel for their history (\"you have been to X, Y and Z\").',\n"
        "    '- #29: their strengths (\"your corner of MDS\") and what they are building up - frame building-up areas warmly as CURRENT FOCUS, never as weakness, never as a judgement, never with numbers.',\n"
        "    '- The people they cross paths with most, naturally (\"you keep running into...\") - shared chats and events only, nothing private.',",
        "Build Prompt dossier shape")

    # solve: ABOUT THE ASKER
    bp = patch(bp,
        "  const sd = ($('Fetch Summaries').first() || {}).json || {};\n  const partners = Array.isArray(sd.partners) ? sd.partners : [];",
        "  const sd = ($('Fetch Summaries').first() || {}).json || {};\n"
        "  // #29: the asker's own context rides the multi_source_v2 payload\n"
        "  const meS = sd.me || null;\n"
        "  const meBlock = meS ? [\n"
        "    (meS.focus ? '- ' + meS.focus : null),\n"
        "    (Array.isArray(meS.strengths) && meS.strengths.length ? '- strong ground: ' + meS.strengths.slice(0, 5).join(', ') : null),\n"
        "    (Array.isArray(meS.working_on) && meS.working_on.length ? '- building up right now: ' + meS.working_on.slice(0, 4).join(', ') : null),\n"
        "    ((meS.city || meS.state) ? '- based in: ' + [meS.city, meS.state].filter(Boolean).join(', ') : null)\n"
        "  ].filter(Boolean).join(NL) : '';\n"
        "  const partners = Array.isArray(sd.partners) ? sd.partners : [];",
        "Build Prompt solve me-collect")

    bp = patch(bp,
        "    '- Keep it tight: a couple of lines per source, end with an offer to go deeper.',\n    '',\n    'MEMBER: ' + (plan.full_name || 'unknown')\n  ].join(NL);\n  let user = 'PROBLEM/ASK: ' + plan.text",
        "    '- Keep it tight: a couple of lines per source, end with an offer to go deeper.',\n"
        "    '- PERSONALIZE: if an ABOUT THE ASKER section appears, use it to PICK and FRAME the help that fits their situation (their level, focus, location). Never recite the profile back, never say \"according to your profile\", and never call any area weak - a building-up area is simply what they are focused on now.',\n"
        "    '',\n    'MEMBER: ' + (plan.full_name || 'unknown')\n  ].join(NL);\n"
        "  let user = (meBlock ? 'ABOUT THE ASKER (their own MDS profile - for tailoring only, never recite):' + NL + meBlock + NL + NL : '') + 'PROBLEM/ASK: ' + plan.text",
        "Build Prompt solve me-render")

    # multi: same pattern
    bp = patch(bp,
        "  const d = ($('Fetch Summaries').first() || {}).json || {};\n  const mPartners = Array.isArray(d.partners) ? d.partners : [];",
        "  const d = ($('Fetch Summaries').first() || {}).json || {};\n"
        "  // #29: the asker's own context rides the multi_source_v2 payload\n"
        "  const meM = d.me || null;\n"
        "  const meMBlock = meM ? [\n"
        "    (meM.focus ? '- ' + meM.focus : null),\n"
        "    (Array.isArray(meM.strengths) && meM.strengths.length ? '- strong ground: ' + meM.strengths.slice(0, 5).join(', ') : null),\n"
        "    (Array.isArray(meM.working_on) && meM.working_on.length ? '- building up right now: ' + meM.working_on.slice(0, 4).join(', ') : null),\n"
        "    ((meM.city || meM.state) ? '- based in: ' + [meM.city, meM.state].filter(Boolean).join(', ') : null)\n"
        "  ].filter(Boolean).join(NL) : '';\n"
        "  const mPartners = Array.isArray(d.partners) ? d.partners : [];",
        "Build Prompt multi me-collect")

    bp = patch(bp,
        "    '- LENGTH: this covers a lot of ground — up to ~1300 characters is fine, but stay skimmable and end with an offer to go deeper on any one thread.',",
        "    '- LENGTH: this covers a lot of ground — up to ~1300 characters is fine, but stay skimmable and end with an offer to go deeper on any one thread.',\n"
        "    '- PERSONALIZE: if an ABOUT THE ASKER section appears, use it to PICK and FRAME what fits their situation (their level, focus, location). Never recite the profile back, never say \"according to your profile\", and never call any area weak - a building-up area is simply what they are focused on now.',",
        "Build Prompt multi rule")

    bp = patch(bp,
        "  let user = 'THEIR ASK: ' + plan.text + NL + NL +\n    'PEOPLE TO TALK TO",
        "  let user = (meMBlock ? 'ABOUT THE ASKER (their own MDS profile - for tailoring only, never recite):' + NL + meMBlock + NL + NL : '') + 'THEIR ASK: ' + plan.text + NL + NL +\n    'PEOPLE TO TALK TO",
        "Build Prompt multi me-render")

    # events: interests into MEMBER CONTEXT + the recommend rule reads them
    bp = patch(bp,
        "  const pastTotal = hist.find(function (h) { return h.kind === 'past_total'; });\n  const ctxLines = [];",
        "  const pastTotal = hist.find(function (h) { return h.kind === 'past_total'; });\n"
        "  // #29: their interest topics (event_history_v2 kind=interest) personalize recommendations\n"
        "  const interests = hist.filter(function (h) { return h.kind === 'interest'; });\n"
        "  const ctxLines = [];",
        "Build Prompt events interests-collect")

    bp = patch(bp,
        "  const memberCtx = ctxLines.join(NL);",
        "  if (interests.length) { ctxLines.push('Their interests (from their MDS profile + activity): ' + interests.map(function (i) { return i.label; }).join(', ')); }\n"
        "  const memberCtx = ctxLines.join(NL);",
        "Build Prompt events interests-render")

    bp = patch(bp,
        "    '- RECOMMENDING (\"which events fit me\", \"when should I visit X\"): weigh their history and their interests from THIS conversation.",
        "    '- RECOMMENDING (\"which events fit me\", \"when should I visit X\"): weigh their history, THEIR INTERESTS in MEMBER CONTEXT, and their interests from THIS conversation. The list below is already ordered with their interests in mind - lead with what fits THEM and say naturally why it fits (\"given you are deep in TikTok right now...\"). Never mention rankings or scores.",
        "Build Prompt events recommend-rule")

    nodes["Build Prompt"]["parameters"]["jsCode"] = bp

    # ── 4. Build Verbatim Digest: the personal why per chat rec ──────────────
    bv = nodes["Build Verbatim Digest"]["parameters"]["jsCode"]
    bv = patch(bv,
        "    out += NL + '• *' + r.chat_name + '*';",
        "    out += NL + '• *' + r.chat_name + '*';\n"
        "    if (r.why) { out += NL + '  _' + r.why + '_'; }  // #29: the personal reason, member-safe",
        "Build Verbatim chats why")
    nodes["Build Verbatim Digest"]["parameters"]["jsCode"] = bv

    # ── syntax check every touched code node ─────────────────────────────────
    for name in ("Attach Embedding", "Build Prompt", "Build Verbatim Digest"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(nodes[name]["parameters"]["jsCode"])
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED on {name}:\n{chk.stderr}"
    print("node --check: OK (3 code nodes)")

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
    print("VERIFY",
          "fs:", "member_dossier_v2" in n2["Fetch Summaries"]["parameters"]["url"],
          "fr:", "member_dossier_v2" in n2["Fetch Raw Matches"]["parameters"]["url"],
          "ae:", "multi_source_v2" in n2["Attach Embedding"]["parameters"]["jsCode"],
          "bp:", n2["Build Prompt"]["parameters"]["jsCode"].count("#29"),
          "bv:", "#29" in n2["Build Verbatim Digest"]["parameters"]["jsCode"],
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
