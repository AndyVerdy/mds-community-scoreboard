#!/usr/bin/env python3
"""#169 web door on STAGING: second webhook feeding the same chain; Web? fork after Eval (silent)?.
  python3 scripts/olivia_loop/apply_169_web_door.py            # edits STAGING, one bounce

Fix round 1 (2026-09-07): the first version of this script gave `Web Inbound (POST)`
`responseMode: "responseNode"` and terminated the web branch in a `respondToWebhook`-type
`Respond Web` node. That node is graph-reachable from `WA Inbound (POST)` too (the pipeline is
shared up to `Eval (silent)?`, forking only at `Web?`), and n8n's webhook-response validator runs
on the static graph at trigger time — it doesn't know a real WhatsApp turn takes `Web?`'s false
branch and never reaches `Respond Web`; it only sees a `respondToWebhook` node reachable from a
webhook that isn't itself in `responseNode` mode, and refuses to run at all ("Unused Respond to
Webhook node found in the workflow"). Every WhatsApp-shaped POST to staging 500'd, unconditionally
(confirmed live: execs 137578/137581, failing at the trigger before `Log Inbound` ever ran).
Fixed by removing the only `respondToWebhook`-type node from the graph: `Web Inbound (POST)` now
uses `responseMode: "lastNode"` (`responseData: "firstEntryJson"`), and the web branch ends in a
plain Code node, `Web Response`, after `Save Web (Supabase)` — `lastNode` mode answers the HTTP
caller with that node's first output item JSON. No `respondToWebhook` node exists anywhere on the
graph, so `WA Inbound (POST)` has nothing to trip on.
"""
import json, os, subprocess, sys, tempfile, time
STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
PROBE_PHONE = "17866578153"   # retrieval principal for web turns until Team mode (#169 spec)
SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")
BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")

def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None: cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None, capture_output=True, text=True)
    return json.loads(r.stdout)

def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f: f.write(code); p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True); os.unlink(p)
    return r.returncode == 0, r.stderr

# ---- 1. Log Inbound: accept the web shape (inserted at the very top of the node) ----
LOG_INBOUND_OLD = "const j = $input.item.json;\nconst b = (j && j.body) ? j.body : j;\n"
LOG_INBOUND_NEW = LOG_INBOUND_OLD + r"""
// #169 WEB DOOR. A web turn arrives on 'Web Inbound (POST)' as {web:true, asker_email, asker_name, mode,
// target, text, thread_id}. Normalise it into the SAME shape a WhatsApp text produces so every
// downstream $('Log Inbound') reference keeps working. Two things are decided HERE, never by the
// caller: the retrieval principal (the probe member phone, until Team mode) and the wamid prefix
// 'wamid.SELFTEST_WEB_' that sends the turn down Eval (silent)? — a web turn can never reach Meta.
if (b && b.web === true) {
  const _mode = ['test', 'public', 'team'].indexOf(String(b.mode)) >= 0 ? String(b.mode) : 'test';
  const _text = String(b.text || '').trim();
  if (!_text) return null;
  const _wamid = 'wamid.SELFTEST_WEB_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  // Log Inbound runs in n8n's "Run Once for Each Item" mode (verified against every other
  // branch of this same function, e.g. the WhatsApp return at the bottom): the per-item
  // contract there is a BARE { json: {...} } (or null to drop the item), never an array —
  // an array-wrapped return here fails n8n's own item-shape validation with "A 'json'
  // property isn't an object" (caught live on staging 2026-09-07, execs 137565/137566,
  // both zero-length 200s — fixed before any answer-shaped probe response was ever seen).
  return { json: {
    from: '17866578153', to: '17866578153', wamid: _wamid, text: _text, name: String(b.asker_name || 'MDS staff'),
    from_is_uid: false, channel: 'web', asker_email: String(b.asker_email || '').toLowerCase(), mode: _mode,
    target: String(b.target || 'staging'), thread_id: String(b.thread_id || ('t_' + Date.now())), t_web0: Date.now(),
  } };
}
"""

# ---- 2. Load Recent Turns: web threads read their own table ----
LRT_OLD = "=https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/olivia_messages?phone=eq.{{ $('Resolve Member').first().json.to }}&created_at=gte.{{ new Date(Date.now() - 86400000).toISOString() }}&select=role,text,route,plan,created_at,wamid&order=created_at.desc,id.desc&limit=16"
# Web threads keep their memory whatever their age (Andy 2026-09-07: "and it carries the history?" — yes): no 24h
# cut for the web table, only the same 16-turn cap Prep Context already applies (each turn trimmed to 500 chars).
LRT_NEW = ("={{ $('Log Inbound').first().json.channel === 'web' "
           "? 'https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/olivia_web_messages?thread_id=eq.' + encodeURIComponent($('Log Inbound').first().json.thread_id) + '&select=role,text,route,plan,created_at,wamid&order=created_at.desc,id.desc&limit=16' "
           ": 'https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/olivia_messages?phone=eq.' + $('Resolve Member').first().json.to + '&created_at=gte.' + new Date(Date.now() - 86400000).toISOString() + '&select=role,text,route,plan,created_at,wamid&order=created_at.desc,id.desc&limit=16' }}")

# ---- 3. New nodes ----
FORMAT_WEB = r"""
// FORMAT WEB (#169). Markdown for the admin page — the WhatsApp formatter already ran for the
// silent path; we ignore its output and take the model text as the answer loop left it.
const inb = $('Log Inbound').first().json;
let text = '';
try {
  if ($('Gate Verdict').isExecuted) text = ($('Gate Verdict').first().json.content || []).map(c => c && c.text ? c.text : '').join('');
  else if ($('Answer Parse').isExecuted) text = String($('Answer Parse').first().json.answer_text || '');
  else if ($('Build Verbatim Digest').isExecuted) text = String($('Build Verbatim Digest').first().json.reply || '');
} catch (e) { text = ''; }
text = String(text || '').replace(/\s*\[SEND_(IMAGE|FILE):[^\]]*\]/gi, '').trim();
if (!text) text = 'Sorry — I could not generate an answer just now.';
// Public Verify (when it ran) replaces the text and adds notes/sources; otherwise empty.
let notes = [], sources = [], evidence_classes = {}, refused = false, redactions = [];
try {
  if ($('Public Verify').isExecuted) {
    const pv = $('Public Verify').first().json;
    text = String(pv.text || text); notes = pv.notes || []; sources = pv.sources || [];
    evidence_classes = pv.evidence_classes || {}; refused = pv.refused === true; redactions = pv.redactions || [];
  }
} catch (e) {}
// Source chips for the page (design pack: "Recorded call · 3 Facebook threads · #ppc channel · 2 partner records"):
// counts of evidence rows by source, from the tool results of THIS turn — never asserted.
let source_summary = {};
try {
  const msgs = $('Answer Parse').isExecuted ? ($('Answer Parse').first().json.messages || []) : [];
  for (const m of msgs) {
    if (!m || m.role !== 'user' || !Array.isArray(m.content)) continue;
    for (const c of m.content) {
      if (!c || c.type !== 'tool_result') continue;
      let rows = null; try { rows = JSON.parse(typeof c.content === 'string' ? c.content : JSON.stringify(c.content)); } catch (e) { rows = null; }
      for (const r of (Array.isArray(rows) ? rows : [])) { const k = String((r && (r.source || r.kind)) || 'other'); source_summary[k] = (source_summary[k] || 0) + 1; }
    }
  }
} catch (e) { source_summary = {}; }
let metrics = null, plan = null, route = null;
try { metrics = $('Answer Parse').isExecuted ? $('Answer Parse').first().json.metrics : null; } catch (e) {}
try { const p = $('Plan Request').first().json; route = p.route || null; plan = p.op ? { op: p.op, params: p.params || {}, period: p.period || null } : null; } catch (e) {}
return [{ json: {
  ok: true, thread_id: inb.thread_id, mode: inb.mode, target: inb.target, asker_email: inb.asker_email,
  question: inb.text, wamid: inb.wamid, answer_md: text, notes, sources, evidence_classes, refused, redactions, source_summary,
  route, plan, metrics, latency_ms: Date.now() - Number(inb.t_web0 || Date.now()),
  model: (inb.mode === 'public' ? 'claude-sonnet-5 + claude-haiku-4-5-20251001' : 'claude-sonnet-5'),
} }];
"""

SAVE_WEB_BODY = ("={{ (() => { const f = $('Format Web').first().json; const base = { thread_id: f.thread_id, asker_email: f.asker_email, "
                 "mode: f.mode, target: f.target, route: f.route, plan: f.plan, wamid: f.wamid, "
                 # PostgREST bulk-inserts an array of objects as ONE statement and rejects it ("All object keys
                 # must match") unless every object carries the identical key set — caught live on staging
                 # 2026-09-07 (exec 137568: pipeline ran end-to-end, Save Web (Supabase) 400'd on this). The
                 # member row has no answer, so its olivia-only columns are filled with the SAME value the
                 # column's own default would give it (jsonb NOT NULL columns get their empty literal, nullable
                 # columns get null) — Object.assign then overrides only what each role actually differs on.
                 "answer_md: null, notes: [], sources: [], evidence_classes: {}, latency_ms: null, metrics: null, model: null, "
                 "redactions: [], source_summary: {} }; "
                 "return JSON.stringify([ Object.assign({}, base, { role: 'member', text: f.question }), "
                 "Object.assign({}, base, { role: 'olivia', text: f.answer_md, answer_md: f.answer_md, notes: f.notes, sources: f.sources, "
                 "evidence_classes: f.evidence_classes, latency_ms: f.latency_ms, metrics: f.metrics, model: f.model, "
                 "redactions: f.redactions || [], source_summary: f.source_summary || {} }) ]); })() }}")

WEB_RESPONSE = r"""
// WEB RESPONSE (#169 fix round 1). Terminal node of the web branch — Web Inbound (POST) uses
// responseMode:"lastNode" with responseData:"firstEntryJson", so whatever THIS node returns as
// its first item IS the HTTP response body. No respondToWebhook node exists anywhere on this
// graph (see the module docstring for why one broke the WhatsApp path).
const f = $('Format Web').first().json;
// Save Web (Supabase) posts a 2-row array with Prefer: return=representation; PostgREST returns
// that as a JSON array, and n8n's httpRequest node splits a JSON-array response body into ONE
// ITEM PER ROW rather than one item holding the array (confirmed live on staging 2026-09-07,
// exec 137570: 2 items, id 1 role=member + id 2 role=olivia) — so every item reaching this node
// via $input must be collected, not just "the current item".
const rows = $input.all().map(i => i.json);
const turn = rows.find(r => r && r.role === 'olivia');
return [{ json: {
  ok: true, thread_id: f.thread_id, turn_id: turn ? turn.id : null, mode: f.mode, answer_md: f.answer_md,
  notes: f.notes, sources: f.sources, evidence_classes: f.evidence_classes, refused: f.refused,
  redactions: f.redactions || [], source_summary: f.source_summary || {}, latency_ms: f.latency_ms, metrics: f.metrics,
} }];
"""

def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    # header-auth credential id, by name
    creds = api("GET", "/credentials?limit=250").get("data", [])
    cred = next((c for c in creds if c["name"] == "Olivia Web Secret"), None)
    if not cred: sys.exit("create the 'Olivia Web Secret' httpHeaderAuth credential first (Task 5 step 1)")
    # The Supabase service header credential Save Conversation / Load Recent Turns already use (verified on the
    # staging graph 2026-09-07): id QHLDE4VHvm8jrVds, name "Supabase secret (digest mirror)". Match by exact name.
    sb = next(c for c in creds if c["type"] == "httpHeaderAuth" and c["name"] == "Supabase secret (digest mirror)")

    li = nodes["Log Inbound"]["parameters"]["jsCode"]
    assert li.count(LOG_INBOUND_OLD) == 1, "Log Inbound anchor not unique"
    nodes["Log Inbound"]["parameters"]["jsCode"] = li.replace(LOG_INBOUND_OLD, LOG_INBOUND_NEW)
    assert nodes["Load Recent Turns"]["parameters"]["url"] == LRT_OLD, "Load Recent Turns url drifted — re-read it"
    nodes["Load Recent Turns"]["parameters"]["url"] = LRT_NEW

    for code in (nodes["Log Inbound"]["parameters"]["jsCode"], FORMAT_WEB, WEB_RESPONSE):
        ok, err = node_check(code.replace("$('", "x('").replace("$input", "xinput").replace("$json", "xjson"))
        if not ok: sys.exit(err)

    x0, y0 = nodes["Eval (silent)?"]["position"]
    new_nodes = [
      {"name": "Web Inbound (POST)", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [x0 - 3200, y0 + 600],
       # lastNode/firstEntryJson (not responseNode+respondToWebhook) — see module docstring, fix round 1.
       "parameters": {"path": "olivia-web-staging", "httpMethod": "POST", "responseMode": "lastNode", "responseData": "firstEntryJson", "authentication": "headerAuth", "options": {}},
       "credentials": {"httpHeaderAuth": {"id": cred["id"], "name": cred["name"]}}},
      {"name": "Web?", "type": "n8n-nodes-base.if", "typeVersion": 2, "position": [x0 + 220, y0 + 200],
       "parameters": {"conditions": {"combinator": "and", "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                      "conditions": [{"id": "is_web", "leftValue": "={{ String($('Log Inbound').first().json.channel || '') }}", "operator": {"operation": "equals", "type": "string"}, "rightValue": "web"}]}, "options": {}}},
      {"name": "Format Web", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [x0 + 660, y0 + 200], "parameters": {"jsCode": FORMAT_WEB}},
      {"name": "Save Web (Supabase)", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [x0 + 880, y0 + 200],
       "parameters": {"method": "POST", "url": f"{SUPA}/olivia_web_messages", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                      "sendHeaders": True, "headerParameters": {"parameters": [{"name": "Content-Profile", "value": "digest"}, {"name": "Prefer", "value": "return=representation"}]},
                      "sendBody": True, "specifyBody": "json", "jsonBody": SAVE_WEB_BODY, "options": {}},
       "credentials": {"httpHeaderAuth": {"id": sb["id"], "name": sb["name"]}}},
      {"name": "Web Response", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [x0 + 1100, y0 + 200],
       "parameters": {"jsCode": WEB_RESPONSE}},
    ]
    wf["nodes"].extend(new_nodes)
    conn = wf["connections"]
    # web webhook feeds the same chain as the WA webhook (Log Inbound only — the raw-event/status/reaction
    # branches are WhatsApp-only and would misparse a web payload)
    conn["Web Inbound (POST)"] = {"main": [[{"node": "Log Inbound", "type": "main", "index": 0}]]}
    # Eval (silent)? true-output used to go straight to Save Conversation; it now goes through Web?
    assert conn["Eval (silent)?"]["main"][0] == [{"node": "Save Conversation", "type": "main", "index": 0}], "Eval wiring drifted"
    conn["Eval (silent)?"]["main"][0] = [{"node": "Web?", "type": "main", "index": 0}]
    conn["Web?"] = {"main": [[{"node": "Format Web", "type": "main", "index": 0}],          # true  → web path (Task 6 inserts Public? before Format Web)
                             [{"node": "Save Conversation", "type": "main", "index": 0}]]}   # false → WhatsApp silent path as before
    conn["Format Web"] = {"main": [[{"node": "Save Web (Supabase)", "type": "main", "index": 0}]]}
    conn["Save Web (Supabase)"] = {"main": [[{"node": "Web Response", "type": "main", "index": 0}]]}
    # Web Response is terminal — no connection leaves it. lastNode mode reads its first output item.

    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings", "staticData") if k in wf}
    api("PUT", f"/workflows/{STAGING_ID}", body)
    api("POST", f"/workflows/{STAGING_ID}/deactivate"); time.sleep(1); api("POST", f"/workflows/{STAGING_ID}/activate")
    print("staging updated + bounced: web door in place")

if __name__ == "__main__":
    main()
