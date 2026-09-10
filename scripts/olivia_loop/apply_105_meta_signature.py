#!/usr/bin/env python3
"""#105 — verify Meta's X-Hub-Signature-256 on every inbound WhatsApp delivery.

Idempotent, marker-guarded, one GET and one PUT. Re-run it after any staging overwrite.

WHAT IT BUILDS, and why it is five nodes rather than the one the ticket imagined.
The ticket assumed a Code node could read the app secret. It cannot: on this n8n Cloud
plan `$env` and `$vars` both read empty, `$secrets` is undefined, and the Variables page
404s. So the secret lives in Supabase Vault and `digest.meta_signature_ok()` does the
comparison. Reaching it costs an HTTP node, and an HTTP node replaces the item, so the
original webhook item has to be restored before the four existing successors run.

    WA Inbound (POST)
      -> Signature Inputs        (Code)  raw bytes out of the binary property + the header
      -> Verify Signature        (HTTP)  digest.meta_signature_ok(raw, signature)
      -> Signed?                 (IF)    true / false
           true  -> Inbound Verified (Code)  hands back the ORIGINAL webhook item
                      -> Extract Raw Event / Log Inbound / Parse Delivery Status / Parse Reaction
           false -> Drop Forged Inbound (Slack)   one line, names the reason and the source IP

The raw bytes matter and the parsed body will not do: Meta signs what it sent, and
re-serialising a parsed body produces different bytes. Turning on the webhook's rawBody
option does NOT disturb `json.body` — it adds the original bytes alongside, in the item's
binary property — so the four successors see exactly what they see today. That was proven
on a throwaway workflow before this was written.

The Ask Millie web door is untouched by construction. `Web Inbound (POST)` is a separate
webhook whose single edge goes straight into `Log Inbound`, so it never crosses this chain.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import olivia_wf as w  # noqa: E402

MARKER = "#105 meta-signature"
SUPABASE_RPC = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/meta_signature_ok"
SUPABASE_CRED = {"httpHeaderAuth": {"id": "QHLDE4VHvm8jrVds", "name": "Supabase secret (digest mirror)"}}
SLACK_CRED = {"slackApi": {"id": "4hldQsthzpT5hv9V", "name": "MDS Review Agent (Slack bot)"}}
SLACK_CHANNEL = {"__rl": True, "cachedResultName": "automation-tests", "mode": "id", "value": "C0AQ8USNQK0"}

GUARD = "WA Inbound (POST)"
DOWNSTREAM = ["Extract Raw Event", "Log Inbound", "Parse Delivery Status", "Parse Reaction"]

INPUTS_JS = """// """ + MARKER + """: pull out what the verifier needs, and nothing else.
// The RAW BYTES are the point. Meta signs the bytes it sent; JSON.stringify of the parsed
// body is a different byte string and would never verify. The webhook's rawBody option
// puts the originals in the item's binary property, base64, leaving json.body parsed for
// everyone downstream.
const it = $input.item;
const j = it.json || {};
const headers = j.headers || {};

let raw = null;
try {
  const bin = it.binary && it.binary.data;
  if (bin && bin.data) raw = Buffer.from(bin.data, 'base64').toString('utf8');
} catch (e) {}

let signature = null;
for (const k of Object.keys(headers)) {
  if (k.toLowerCase() === 'x-hub-signature-256') {
    const v = headers[k];
    if (typeof v === 'string' && v.length) signature = v;
    break;
  }
}

// Cloudflare sits in front of n8n, so the real caller is cf-connecting-ip; the rest are
// fallbacks for a direct hit.
const ip = headers['cf-connecting-ip']
  || (typeof headers['x-forwarded-for'] === 'string' ? headers['x-forwarded-for'].split(',')[0].trim() : null)
  || headers['x-real-ip'] || null;

return { json: { raw, signature, ip } };
"""

VERIFIED_JS = """// """ + MARKER + """: the signature held. Hand back the ORIGINAL webhook item.
// The HTTP node above replaced the item with the verifier's answer, and everything
// downstream of here expects the webhook's own shape (json.body, json.headers). Reading it
// from the webhook node itself keeps those four nodes untouched by this ticket.
return { json: $('""" + GUARD + """').item.json };
"""


def build_nodes(pos):
    x, y = pos
    return [
        {
            "id": "sig-inputs-105",
            "name": "Signature Inputs",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [x, y],
            "parameters": {"jsCode": INPUTS_JS},
        },
        {
            "id": "sig-verify-105",
            "name": "Verify Signature (Supabase)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [x + 200, y],
            "parameters": {
                "method": "POST",
                "url": SUPABASE_RPC,
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Content-Profile", "value": "digest"}]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ p_raw: $json.raw, p_signature: $json.signature }) }}",
                "options": {"timeout": 10000},
            },
            "credentials": SUPABASE_CRED,
            # A verifier that cannot be reached must DROP, not wave traffic through. onError
            # continues so the IF below sees a falsy ok and takes the false branch.
            "onError": "continueRegularOutput",
        },
        {
            "id": "sig-if-105",
            "name": "Signed?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [x + 400, y],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                    "combinator": "and",
                    "conditions": [
                        {
                            "id": "signed-105",
                            "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                            "leftValue": "={{ $json.ok === true }}",
                            "rightValue": "",
                        }
                    ],
                },
                "looseTypeValidation": True,
                "options": {},
            },
        },
        {
            "id": "sig-ok-105",
            "name": "Inbound Verified",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [x + 600, y - 100],
            "parameters": {"jsCode": VERIFIED_JS},
        },
        {
            "id": "sig-drop-105",
            "name": "Drop Forged Inbound (Slack)",
            "type": "n8n-nodes-base.slack",
            "typeVersion": 2.3,
            "position": [x + 600, y + 120],
            "parameters": {
                "select": "channel",
                "channelId": SLACK_CHANNEL,
                "resource": "message",
                "operation": "post",
                "messageType": "text",
                "otherOptions": {"includeLinkToWorkflow": True},
                "text": "=\U0001f6d1 *Unverified WhatsApp delivery dropped* (#105)\n"
                        "Reason: `{{ $json.reason || 'unreachable-verifier' }}`  ·  "
                        "From: `{{ $('Signature Inputs').item.json.ip || 'unknown' }}`  ·  "
                        "Signature: `{{ $('Signature Inputs').item.json.signature || 'none sent' }}`\n"
                        "_Nothing downstream ran. A real Meta delivery always carries a valid "
                        "X-Hub-Signature-256; if these are genuine, check META_APP_SECRET in Vault._",
            },
            "credentials": SLACK_CRED,
        },
    ]


def main():
    apply = "--apply" in sys.argv
    target = "staging"
    for i, a in enumerate(sys.argv):
        if a == "--target" and i + 1 < len(sys.argv):
            target = sys.argv[i + 1]
    if not apply:
        print("dry run (pass --apply to write). Target:", target)

    wid = w.resolve_id(target)
    g = w.fetch(wid)
    names = {n["name"] for n in g["nodes"]}

    if "Verify Signature (Supabase)" in names:
        print("already applied — nothing to do")
        return 0

    guard = next((n for n in g["nodes"] if n["name"] == GUARD), None)
    if guard is None:
        print("FATAL: no %r node" % GUARD)
        return 1

    missing = [d for d in DOWNSTREAM if d not in names]
    if missing:
        print("FATAL: expected successors missing:", missing)
        return 1

    # 1. the raw bytes. Without this the binary property is absent and every delivery
    #    fails as missing_body.
    guard.setdefault("parameters", {}).setdefault("options", {})["rawBody"] = True

    # 2. the new chain, placed under the webhook node
    gx, gy = guard.get("position", [0, 0])
    g["nodes"].extend(build_nodes([gx + 180, gy + 320]))

    # 3. rewire: everything WA Inbound fed now hangs off Inbound Verified instead
    conns = g["connections"]
    existing = conns.get(GUARD, {}).get("main", [[]])
    moved = [c for branch in existing for c in (branch or [])]
    kept = [c for c in moved if c["node"] in DOWNSTREAM]
    if len(kept) != len(moved):
        print("FATAL: %r feeds something unexpected: %s" % (GUARD, [c["node"] for c in moved]))
        return 1

    conns[GUARD] = {"main": [[{"node": "Signature Inputs", "type": "main", "index": 0}]]}
    conns["Signature Inputs"] = {"main": [[{"node": "Verify Signature (Supabase)", "type": "main", "index": 0}]]}
    conns["Verify Signature (Supabase)"] = {"main": [[{"node": "Signed?", "type": "main", "index": 0}]]}
    conns["Signed?"] = {"main": [
        [{"node": "Inbound Verified", "type": "main", "index": 0}],
        [{"node": "Drop Forged Inbound (Slack)", "type": "main", "index": 0}],
    ]}
    conns["Inbound Verified"] = {"main": [kept]}

    print("rawBody on %r: %s" % (GUARD, guard["parameters"]["options"]["rawBody"]))
    print("moved behind the check:", [c["node"] for c in kept])

    if not apply:
        print("dry run complete — no write")
        return 0

    w.put_graph(wid, g, g.get("name"), g.get("settings"))
    print("PUT ok")
    w.bounce(wid)
    print("bounced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
