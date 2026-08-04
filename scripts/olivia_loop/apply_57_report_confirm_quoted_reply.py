#!/usr/bin/env python3
"""#57 Andy's live-test trio (2026-08-04) — apply to STAGING (bqHstPDi84uOhTCJ).

(1) REPORT CONFIRM-STEP. "I want to report a bug" filed an EMPTY report instantly, and the
    member's actual detail then became a new question. Now: an intent-only report asks what
    to report; when the text arrives Olivia DRAFTS it back behind a fixed marker and files
    only on Send it. Deterministic, mirroring the two-step ticket (TICKET_OFFER_MARK).
(2) QUOTED-REPLY BINDING. WhatsApp tells us exactly which message a reply quotes
    (`messages[0].context.id`) and we threw it away — so a tapped "Yes" bound to whatever
    turn happened to be last (live: it grabbed an unrelated answer). Now the quoted wamid
    picks the plan to replay.
(3) BUTTON WORDING. The body said "reply YES" while showing buttons. When buttons attach,
    the send layer rewrites reply-YES phrasing to tap-Yes.

Idempotent: anchors asserted, hunks skip when applied.
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
    assert old in text, f"{where}: anchor NOT FOUND"
    assert text.count(old) == 1, f"{where}: anchor x{text.count(old)}"
    print(f"  {where}: patched")
    return text.replace(old, new)


REPORT_MARK = "ready to send this to the mds team"


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ── (2a) Log Inbound: carry the quoted message id ────────────────────────
    li = nodes["Log Inbound"]["parameters"]["jsCode"]
    li = patch(li,
        "return { json: { event: 'inbound message', from: msg.from, name: name, type: msg.type, text: String(text).trim(), timestamp: msg.timestamp, wamid: msg.id } };",
        "// #57: WhatsApp tells us WHICH message this replies to. Ignoring it is why a tapped\n"
        "// 'Yes' could bind to an unrelated turn (live 2026-08-04).\n"
        "const quoted = (msg.context && msg.context.id) ? String(msg.context.id) : null;\n"
        "return { json: { event: 'inbound message', from: msg.from, name: name, type: msg.type, text: String(text).trim(), timestamp: msg.timestamp, wamid: msg.id, quoted_wamid: quoted } };",
        "Log Inbound quoted_wamid")
    nodes["Log Inbound"]["parameters"]["jsCode"] = li

    # ── (2b) history must carry wamid so the quote can be resolved ───────────
    lrt = nodes["Load Recent Turns"]["parameters"]
    lrt["url"] = patch(lrt["url"], "select=role,text,route,plan,created_at",
                       "select=role,text,route,plan,created_at,wamid",
                       "Load Recent Turns select wamid")

    # ── (2c) Prep Context: the quoted turn wins the replay ───────────────────
    pc = nodes["Prep Context"]["parameters"]["jsCode"]
    pc = patch(pc,
        "return [{ json: { has_history:",
        "// #57 QUOTED REPLY WINS. If the member replied to a specific message, replay THAT\n"
        "// turn's plan - not merely the newest one. This is what makes a tapped button\n"
        "// unambiguous even when other turns landed in between.\n"
        "let quoted_plan = null;\n"
        "try {\n"
        "  const qw = ($('Log Inbound').first().json || {}).quoted_wamid;\n"
        "  if (qw) {\n"
        "    const hit = rows.filter(function (r) { return r && r.wamid === qw && r.role === 'olivia'; })[0];\n"
        "    if (hit && hit.plan && typeof hit.plan === 'object' && hit.plan.op\n"
        "        && NO_REPLAY.indexOf(String(hit.route || '')) === -1) { quoted_plan = hit.plan; }\n"
        "  }\n"
        "} catch (e) {}\n"
        "if (quoted_plan) { prev_plan = quoted_plan; }\n"
        "return [{ json: { quoted_reply: !!quoted_plan, has_history:",
        "Prep Context quoted replay")
    nodes["Prep Context"]["parameters"]["jsCode"] = pc

    # ── (1) Plan Request: the report confirm-step, deterministic ─────────────
    pr = nodes["Plan Request"]["parameters"]["jsCode"]
    pr = patch(pr,
        "const reportCmd = /^\\s*report\\b/i.test(rawText);",
        "const reportCmd = /^\\s*report\\b/i.test(rawText);\n"
        "// #57 REPORT CONFIRM-STEP (Andy live 2026-08-04: \"I want to report a bug\" filed an EMPTY\n"
        "// report, and the member's real detail then became a new question). Two deterministic\n"
        "// states, mirroring the two-step ticket:\n"
        "//   reportIntent  = they SAY they want to report but gave no content yet -> ask, file nothing\n"
        "//   reportConfirm = her last turn drafted it behind REPORT_CONFIRM_MARK and they said send\n"
        "const REPORT_CONFIRM_MARK = '" + REPORT_MARK + "';\n"
        "const reportIntent = /^\\s*(i\\s+(want|need|would like|wanna)\\s+to\\s+)?(report|file|log|submit)\\s+(a|an|some)?\\s*(bug|issue|problem|report|feedback|complaint|something)?\\s*[.!?]*\\s*$/i.test(rawText)\n"
        "  || /^\\s*(can|could)\\s+i\\s+(report|file|submit)\\b[^?]{0,20}\\??\\s*$/i.test(rawText);\n"
        "const _lastOlLower = String((String(ctx.history_block || '').split(String.fromCharCode(10))\n"
        "  .filter(function (l) { return l.indexOf('Olivia: ') === 0; }).pop() || '')).toLowerCase();\n"
        "const _draftPending = _lastOlLower.indexOf(REPORT_CONFIRM_MARK) !== -1;\n"
        "const reportSend = _draftPending && /^\\s*(send it|send|yes|yep|yeah|ok|okay|confirm|file it|go ahead|do it)[.!\\s]*$/i.test(rawText);\n"
        "const reportMore = _draftPending && /^\\s*(add more|more|wait|hold on|not yet|edit)[.!\\s]*$/i.test(rawText);\n"
        "const reportCancel = _draftPending && /^\\s*(cancel|nevermind|never mind|no thanks|no|forget it|drop it)[.!\\s]*$/i.test(rawText);",
        "Plan Request report states")
    pr = patch(pr,
        "if (reportCmd) { route = 'llm'; }",
        "if (reportCmd || reportIntent || reportSend || reportMore || reportCancel) { route = 'llm'; }",
        "Plan Request report lane forced")
    assert pr.count("search_terms: terms, cont_topic: cont_topic, role_claim: roleClaim, followup: followup") == 2
    pr = pr.replace("search_terms: terms, cont_topic: cont_topic, role_claim: roleClaim, followup: followup",
                    "search_terms: terms, cont_topic: cont_topic, role_claim: roleClaim, "
                    "report_intent: reportIntent, report_send: reportSend, report_more: reportMore, "
                    "report_cancel: reportCancel, followup: followup")
    assert pr.count("report_intent: reportIntent") == 2, "report flags did not land on both returns"
    print("  Plan Request report flags in returns: patched (x2)")
    nodes["Plan Request"]["parameters"]["jsCode"] = pr

    # ── (1b) Answer Seed: the rule that drives the two states ───────────────
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed,
        "'- REPORT COMMAND:",
        "'- REPORT CONFIRM-STEP (#57, Andy live 2026-08-04): NEVER file a report that has no content. "
        "When the member only says they WANT to report something (report_intent), ask what they would "
        "like to report and file NOTHING. When you have their actual words, DO NOT file yet - reply with "
        "exactly \"Ready to send this to the MDS team:\" followed by their text in quotes, and let them "
        "confirm. On report_send call report_create with THAT drafted text verbatim; on report_more keep "
        "collecting and re-draft; on report_cancel drop it and say so plainly. Their detail message after "
        "a report intent is the REPORT BODY, never a new question.',\n  "
        "'- REPORT COMMAND:",
        "Answer Seed report confirm rule")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    # ── (1c)+(3) Send Reply: 3-button confirm + tap-wording ─────────────────
    sr = nodes["Send Reply (Meta)"]["parameters"]
    sr["jsonBody"] = patch(sr["jsonBody"],
        "   if (hasOffer) {",
        "   var isDraft = reply.toLowerCase().indexOf('" + REPORT_MARK + "') !== -1;"
        "   if (isDraft) {"
        "     inter = { type: 'button', body: { text: reply }, action: { buttons: ["
        "       { type: 'reply', reply: { id: 'txt:Send it', title: 'Send it' } },"
        "       { type: 'reply', reply: { id: 'txt:Add more', title: 'Add more' } },"
        "       { type: 'reply', reply: { id: 'txt:Cancel', title: 'Cancel' } } ] } };"
        "   } else if (hasOffer) {",
        "Send Reply 3-button confirm")
    sr["jsonBody"] = patch(sr["jsonBody"],
        " if (inter) { return { messaging_product: 'whatsapp', to: to, type: 'interactive', interactive: inter }; }",
        " if (inter) {"
        "   if (inter.body && typeof inter.body.text === 'string') {"
        "     inter.body.text = inter.body.text"
        "       .replace(/reply\\s*\\*?YES\\*?/gi, 'tap *Yes*')"
        "       .replace(/reply\\s*\\*?NO\\*?/gi, 'tap *No thanks*');"
        "   }"
        "   return { messaging_product: 'whatsapp', to: to, type: 'interactive', interactive: inter }; }",
        "Send Reply tap-wording")

    for name in ("Log Inbound", "Prep Context", "Plan Request", "Answer Seed"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(nodes[name]["parameters"]["jsCode"])
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"{name}: {chk.stderr}"
    print("node --check OK x4")

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
          "quoted:", "quoted_wamid" in n2["Log Inbound"]["parameters"]["jsCode"],
          "wamid_hist:", "wamid" in n2["Load Recent Turns"]["parameters"]["url"],
          "replay:", "quoted_plan" in n2["Prep Context"]["parameters"]["jsCode"],
          "states:", "reportSend" in n2["Plan Request"]["parameters"]["jsCode"],
          "3btn:", "Send it" in n2["Send Reply (Meta)"]["parameters"]["jsonBody"],
          "tapword:", "tap *Yes*" in n2["Send Reply (Meta)"]["parameters"]["jsonBody"],
          "| version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
