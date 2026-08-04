#!/usr/bin/env python3
"""#38 Interactive buttons — apply to STAGING (bqHstPDi84uOhTCJ).

Story: yes/no offers become TAP BUTTONS; the billing-portal link becomes a CTA-URL button.
Three edits:
  1. Log Inbound: accept type='interactive' — a button tap becomes the member's text
     (button title; ids prefixed 'txt:' override), so taps ride the existing YES flow.
  2. Format Reply: when the reply carries the ticket-offer sentence and fits WA's 1024-char
     interactive body cap -> reply buttons [Yes / No thanks]; when the only strong CTA is the
     billing portal link -> cta_url button. Emits `interactive` alongside reply.
  3. Send Reply (Meta): payload switches to type=interactive when present.
Eval/silent path never reaches Send Reply — unchanged. Real-device tap proof happens at
promote (probes ride the silent path by design).
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


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # 1. inbound taps become text
    li = nodes["Log Inbound"]["parameters"]["jsCode"]
    li = patch(li,
        "if (!msg || msg.type !== 'text') return null;\n"
        "const name = (contact && contact.profile && contact.profile.name) || null;\n"
        "const text = (msg.text && msg.text.body) || '';",
        "// #38: a BUTTON TAP is a message too - the tapped title becomes the member's text\n"
        "// (ids prefixed 'txt:' carry an explicit payload), so taps ride the existing flows\n"
        "// (the Yes button literally says Yes and the YES flow just works).\n"
        "if (!msg || (msg.type !== 'text' && msg.type !== 'interactive')) return null;\n"
        "const name = (contact && contact.profile && contact.profile.name) || null;\n"
        "let text = (msg.text && msg.text.body) || '';\n"
        "if (msg.type === 'interactive') {\n"
        "  const br = msg.interactive && (msg.interactive.button_reply || msg.interactive.list_reply);\n"
        "  if (!br) return null;\n"
        "  text = (String(br.id || '').indexOf('txt:') === 0) ? String(br.id).slice(4) : String(br.title || '');\n"
        "  if (!text) return null;\n"
        "}",
        "Log Inbound interactive")
    nodes["Log Inbound"]["parameters"]["jsCode"] = li

    # 2. Format Reply builds the interactive object
    fr = nodes["Format Reply"]["parameters"]["jsCode"]
    fr = patch(fr,
        "return [{ json: { to: to, reply: text, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone, sources_used: sourcesUsed } }];",
        "// #38: offer-shaped replies become TAP BUTTONS; the billing-portal link becomes a\n"
        "// CTA-URL button. WA caps interactive bodies at 1024 chars - longer replies stay text.\n"
        "let interactive = null;\n"
        "try {\n"
        "  const PORTAL = 'https://checkout.mds.co/p/login/8wM5l70XvaBC6Ji000';\n"
        "  const hasOffer = /reply\\s+YES\\b/i.test(text) || text.toLowerCase().indexOf('open a ticket with the mds team') !== -1;\n"
        "  if (hasOffer && text.length <= 1024 && !imagePostId && !sendFileKey) {\n"
        "    interactive = { type: 'button', body: { text: text },\n"
        "      action: { buttons: [\n"
        "        { type: 'reply', reply: { id: 'txt:Yes', title: 'Yes' } },\n"
        "        { type: 'reply', reply: { id: 'txt:No thanks', title: 'No thanks' } } ] } };\n"
        "  } else if (text.indexOf(PORTAL) !== -1 && !imagePostId && !sendFileKey) {\n"
        "    const stripped = text.split(PORTAL).join('').replace(/[ \\t]*\\n[ \\t]*\\n[ \\t]*\\n+/g, String.fromCharCode(10)+String.fromCharCode(10)).trim();\n"
        "    if (stripped.length <= 1024 && stripped.length > 0) {\n"
        "      interactive = { type: 'cta_url', body: { text: stripped },\n"
        "        action: { name: 'cta_url', parameters: { display_text: 'Open billing portal', url: PORTAL } } };\n"
        "    }\n"
        "  }\n"
        "} catch (e) { interactive = null; }\n"
        "return [{ json: { to: to, reply: text, interactive: interactive, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone, sources_used: sourcesUsed } }];",
        "Format Reply interactive")
    nodes["Format Reply"]["parameters"]["jsCode"] = fr

    # 3. Send Reply payload
    sr = nodes["Send Reply (Meta)"]["parameters"]
    sr["jsonBody"] = patch(sr["jsonBody"],
        "={{ JSON.stringify($json.image_url ? { messaging_product: 'whatsapp', to: $json.to, type: 'image', image: { link: $json.image_url, caption: $json.reply } } : { messaging_product: 'whatsapp', to: $json.to, type: 'text', text: { body: $json.reply } }) }}",
        "={{ JSON.stringify($json.image_url ? { messaging_product: 'whatsapp', to: $json.to, type: 'image', image: { link: $json.image_url, caption: $json.reply } } : ($json.interactive ? { messaging_product: 'whatsapp', to: $json.to, type: 'interactive', interactive: $json.interactive } : { messaging_product: 'whatsapp', to: $json.to, type: 'text', text: { body: $json.reply } })) }}",
        "Send Reply interactive branch")

    for name in ("Log Inbound", "Format Reply"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(nodes[name]["parameters"]["jsCode"])
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"{name}: {chk.stderr}"
    print("node --check OK x2")

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
          "inbound:", "button_reply" in n2["Log Inbound"]["parameters"]["jsCode"],
          "format:", "cta_url" in n2["Format Reply"]["parameters"]["jsCode"],
          "send:", "$json.interactive" in n2["Send Reply (Meta)"]["parameters"]["jsonBody"],
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
