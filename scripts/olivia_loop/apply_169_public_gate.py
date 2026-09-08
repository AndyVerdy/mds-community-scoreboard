#!/usr/bin/env python3
"""#169 Public Gate on STAGING: classify this turn's evidence, mask member names not backed by a
public row, smooth the redacted draft once with Haiku, re-verify deterministically, fail closed.
Inserted on the web fork between `Public?` (fed by `Web?`'s true output) and the existing
`Format Web` node (Task 5). `Public Verify`'s output is consumed by `Format Web`, which already
reads it via `$('Public Verify').isExecuted` (Task 5's `try{...}catch{}` guard) — a Test/Team-mode
turn skips this whole fork (`Public?` false -> straight to `Format Web`, exactly as it did before
this script ever ran).

  python3 scripts/olivia_loop/apply_169_public_gate.py                 # dry run (default): computes + prints the patch, no write
  python3 scripts/olivia_loop/apply_169_public_gate.py --dry-run DIR   # dry run, also writes DIR/staging_before.json + DIR/staging_after.json
  python3 scripts/olivia_loop/apply_169_public_gate.py --apply         # edits STAGING, one bounce

IDEMPOTENT: re-running this script GETs the graph fresh, and for each of the seven nodes below —
by exact name — UPDATES its type/typeVersion/position/parameters/credentials IN PLACE if the node
already exists, instead of appending a duplicate; every connection entry and `Web?`'s true-output
are unconditionally re-asserted either way. Safe to run after a manual/throwaway edit to one of
these nodes (e.g. proving fail-closed by hand-editing `Public Verify`) to restore the canonical
graph — see task-6-report.md.

Rules learned in Task 5 (2026-09-07), binding here (same skeleton: env/api/node_check/bounce
helpers, same credential-lookup pattern):
  1. GET the staging graph fresh and PUT on top of it — it carries other tickets' concurrent node
     edits (#174/#175 touched `Format Reply`, `Plan Request`, `Answer Seed`, `Gate Verdict` since
     Task 5 ran); never re-stage from prod, never rewrite those four nodes, never remove any node.
  2. No node of type `n8n-nodes-base.respondToWebhook` may be reachable from a webhook trigger — a
     reachable one 500s the WhatsApp inbound path unconditionally (Task 5's Bug 4, root-caused and
     fixed there). None of the nodes here are that type; a post-edit guard below also confirms the
     graph's only `respondToWebhook` node remains the pre-existing, disconnected `Respond Challenge`
     (Meta's GET challenge-response handshake).
  3. A Code node that runs once per item must return a bare object, not an array; a Code node
     running `runOnceForAllItems` (the v2 default — true for both Code nodes added here, matching
     `Format Web`'s own pattern) returns an array of `{ json: {...} }`.

BUG FOUND LIVE (2026-09-07, this task, same failure class as Task 5's probe-only bugs): the brief's
own wiring fanned `Public?`'s true output out to `Classify Evidence (Supabase)` and `Fetch Name
Index (Supabase)` in parallel, both feeding `Public Redact`'s single input directly — on the
(correct) assumption that n8n would wait for both branches before running the node they join into.
It does not: a plain node with two incoming connections into the same input runs as soon as EITHER
upstream neighbour delivers data, not when both have. Confirmed live on staging execution 137693:
`Classify Evidence (Supabase)` ran and produced output; `Public Redact` ran immediately after and
threw `ExpressionError: Node 'Fetch Name Index (Supabase)' hasn't been executed` — that node never
even started (absent from the execution's runData entirely), i.e. Public Redact jumped ahead of its
own second dependency. The brief's own `PUBLIC_REDACT` comment ("two httpRequest outputs merged by
'Public Inputs'") already names the fix — a real Merge node was evidently part of the original
design but dropped from the brief's node list/wiring by mistake. Restored here: `Public Inputs`
(`n8n-nodes-base.merge`, typeVersion 3.2, `mode: append`, `numberInputs: 2` — its own schema text is
explicit: "The node waits for all connected inputs to be executed"). `Classify Evidence (Supabase)`
feeds its input 1 (index 0), `Fetch Name Index (Supabase)` feeds its input 2 (index 1); `Public
Redact` still reads both named upstream nodes directly (`$('Classify Evidence (Supabase)').all()`,
`$('Fetch Name Index (Supabase)').all()`) rather than from `Public Inputs`' own (irrelevant, never
read) merged output — `Public Inputs` exists purely as a synchronization barrier, not a data source.
This makes seven new nodes, not six: one `if` (`Public?`), one `merge` (`Public Inputs`), two
`httpRequest`, two `code`. See task-6-report.md for the full empirical trail.

FIX ROUND 1 (2026-09-07, task review): two defects found in review, both fixed here.
  Important — `Fetch Name Index (Supabase)`'s pagination cap (`maxRequests`) was 10 (10,000 rows):
  comfortably above today's 5,394 rows, but a hard cap all the same, and nothing asserted the
  fetched count — if the index ever grew past it, this node would silently hand `Public Redact` a
  truncated `names` list and reintroduce the exact silent-truncation failure this node exists to
  prevent, just at a higher ceiling ("fails LOUD" was claimed in a comment but not actually
  enforced anywhere). Fixed two ways: (1) raised `maxRequests` to 50 (50,000 rows of headroom); (2)
  made the "fails loud" claim true — `Public Redact` now computes `index_incomplete` (the fetch
  came back empty, or landed exactly on the cap on a clean 1000-row page boundary) and includes it
  in its output; `Public Verify` now folds `red.index_incomplete === true` into `refused`, with its
  own note ('Refused: the member name index was incomplete, so no name could be vouched for.') so a
  truncated fetch fails the turn closed instead of silently under-masking.
  Minor — the pre-flight `check_code`/`check_expr` calls covered five of the six embedded
  expressions/code bodies but never the `Public?` IF-condition's own `leftValue` expression. Added a
  sixth `check_expr` call for it (now `PUBLIC_IF_LEFTVALUE`, a named constant instead of an inline
  string so the check and the node parameter can never drift apart).
See task-6-report.md's "Fix round 1" section for the live re-apply and probe trail.
"""
import argparse, json, os, subprocess, sys, tempfile, time

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
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
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None, capture_output=True, text=True)
    return json.loads(r.stdout)


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def check_code(label, code):
    """Code-node jsCode is plain multi-line JS; only n8n's own `$(...)` accessors aren't real
    identifiers to a bare `node --check`, so swap them for the same throwaway names Task 5 used."""
    safe = code.replace("$('", "x('").replace("$input", "xinput").replace("$json", "xjson")
    ok, err = node_check(safe)
    if not ok:
        sys.exit(f"NEEDS_CONTEXT: {label} does not parse:\n{err}")


def check_expr(label, expr):
    """expr is an n8n `={{ ... }}` single-line expression string. Strip the wrapper and check the
    inner JS parses standalone — same substitution trick as check_code()."""
    inner = expr.strip()
    if inner.startswith("={{"):
        inner = inner[3:]
    inner = inner.strip()
    if inner.endswith("}}"):
        inner = inner[:-2]
    check_code(label, inner.strip())


def bounce(workflow_id):
    """Edit first, THEN one deactivate+activate. Never deactivate before editing."""
    api("POST", f"/workflows/{workflow_id}/deactivate")
    time.sleep(1)
    api("POST", f"/workflows/{workflow_id}/activate")


# ---- embed the deterministic module verbatim (tests: node --test scripts/olivia_loop/public_gate.test.mjs, 8 green) ----
MOD = open(os.path.join(os.path.dirname(__file__), "public_gate.js")).read()
MOD = MOD.split("// --- PUBLIC_GATE_BEGIN ---")[1].split("// --- PUBLIC_GATE_END ---")[0]

PUBLIC_REDACT = MOD + r"""
// PUBLIC REDACT (#169) — deterministic. Input items: [0] classify rows, [1] name index rows (two httpRequest
// outputs merged by 'Public Inputs'). Output: the redacted draft + what was removed + the class map.
const ap = $('Answer Parse').first().json;
const draft = $('Gate Verdict').isExecuted
  ? ($('Gate Verdict').first().json.content || []).map(c => c && c.text ? c.text : '').join('')
  : String(ap.answer_text || '');
const classifyRows = $('Classify Evidence (Supabase)').all().map(i => i.json);
const nameRows = $('Fetch Name Index (Supabase)').all().map(i => i.json);
// Fail-closed guard (#169 review fix round 1): 'Fetch Name Index (Supabase)' pagination is bounded
// (maxRequests: 50, 50,000 rows). In plain words: an index that comes back EMPTY (indistinguishable
// here from a real outage — nobody being in the index looks the same as the fetch having failed),
// or one that ends EXACTLY on that 50,000 cap on a clean 1000-row page boundary (every single page
// came back full, so more members could exist just past the last page we fetched), both mean we
// cannot vouch that a given name is truly absent from the index — only that it wasn't in the part
// we saw. Either case must fail the turn CLOSED downstream (Public Verify reads this flag), never
// silently under-mask.
const INDEX_CAP = 50 * 1000;
const index_incomplete = nameRows.length === 0 || (nameRows.length >= INDEX_CAP && nameRows.length % 1000 === 0);
const classes = {};
// Most-RESTRICTIVE wins when one key comes back in several rows (Task 2 review): any 'closed' row closes the key.
for (const r of classifyRows) { if (r && r.key) classes[r.key] = (classes[r.key] === 'closed' || String(r.klass) !== 'public') ? 'closed' : 'public'; }
// Facebook content is not in content_items, so a Facebook URL gets NO classify row; rowClass() treats a missing
// key as closed — the private group stays closed by default, never by luck.
const ev = extractEvidenceRows(ap.messages);
const backed = backedNames(ev.rows, classes, nameRows);
// #169 review fix round 5 (I2): strip every closed-source link from the BODY before the name pass.
// redact() masked names but never removed a link, so a member-only video link, a private
// Facebook-group post or a WhatsApp invite that the draft carried was published verbatim (sources[]
// already excluded them — fix round 3 — but the body did not). Same class map the names are judged
// on; a url no evidence row produced is absent from it, and unknown = closed. redact() then parks
// the surviving (world-public) urls so the name pass cannot rewrite a /speakers/anna-lee slug.
const lk = redactLinks(draft, classes);
const red = redact(lk.text, nameRows, backed);
const closedSources = [...new Set(ev.rows.filter(r => rowClass(r, classes) === 'closed').map(r => r.source || 'text'))];
const publicUrls = [...new Set(ev.rows.filter(r => r.url && rowClass(r, classes) === 'public').map(r => r.url))];
return [{ json: { draft, text: red.text, removed: red.removed, removed_links: lk.removed, backed: [...backed], classes, closed_sources: closedSources, public_urls: publicUrls, names: nameRows.map(n => n.name), index_incomplete } }];
"""

PUBLIC_SMOOTH_BODY = ("={{ JSON.stringify({ model: 'claude-haiku-4-5-20251001', max_tokens: 900, thinking: { type: 'disabled' }, "
  "system: 'You edit a DRAFT for publication outside a private community. Some personal names were already replaced by role phrases (a member, a seller in the community, one of the speakers). "
  "Rules: never add a fact, a name, a number or a link that is not in the draft; fix grammar broken by the replacements; keep every URL exactly; "
  "a \"[link removed]\" marker is deliberate — leave it exactly as it is, and never invent a URL in its place; keep the meaning. "
  "Then write NOTES: one short line per source class listed under CLOSED SOURCES, in plain words, e.g. \"From a closed WhatsApp chat, paraphrased, no names.\" or \"From a call recording, paraphrased.\" — and one line per public URL under PUBLIC SOURCES, e.g. \"Public: MDS Summit schedule page.\". "
  "Return ONLY JSON: {\"text\": string, \"notes\": string[]}.', "
  "messages: [{ role: 'user', content: 'DRAFT:\\n' + $json.text + '\\n\\nCLOSED SOURCES: ' + JSON.stringify($json.closed_sources) + '\\nPUBLIC SOURCES: ' + JSON.stringify($json.public_urls) }] }) }}")

PUBLIC_VERIFY = MOD + r"""
// PUBLIC VERIFY (#169) — deterministic re-check after the smoother. Any unbacked name still present fails
// the turn CLOSED: the reader gets the refusal text and the notes, never the unredacted answer.
const red = $('Public Redact').first().json;
const resp = $input.first().json;
let out = null;
try { const t = (resp.content || []).filter(c => c.type === 'text').map(c => c.text).join(''); out = JSON.parse(t.replace(/^[^{]*/, '').replace(/[^}]*$/, '')); } catch (e) { out = null; }
const smoothed = out && typeof out.text === 'string' && out.text.trim() ? out.text : red.text;
const notes = out && Array.isArray(out.notes) ? out.notes.map(String) : [];
const names = (red.names || []).map(n => ({ name: n }));
const left = leftoverNames(smoothed, names, new Set(red.backed || []));
// the smoother may not add links: every URL in the output must have been in the redacted draft
const urlsIn = (red.text.match(/https?:\/\/\S+/g) || []);
const urlsOut = (smoothed.match(/https?:\/\/\S+/g) || []);
const newUrl = urlsOut.find(u => !urlsIn.includes(u));
// ...and it may not put a closed-source link back either (#169 review fix round 5, I2). Public Redact
// removed every non-public url from the body; if one is in the smoother's output, either it survived
// or Haiku reconstructed it. Same class map, unknown = closed, so a url nothing classified fails too.
const leftLinks = closedUrls(smoothed, red.classes || {});
// Fail-closed guard (#169 review fix round 1): red.index_incomplete (set by Public Redact) means the
// name-index fetch was empty or landed exactly on its pagination cap — we cannot vouch that ANY name
// is absent from it, so refuse regardless of what leftoverNames() happened to find in this draft.
const refused = left.length > 0 || !!newUrl || leftLinks.length > 0 || red.index_incomplete === true;
const text = refused
  ? 'I could not produce a public-safe version of this answer. The sources it rests on are closed, and a name or link from them would have leaked. Ask me the same thing in Test mode to read it internally.'
  : smoothed;
// Design pack (Ask Millie.dc.html, 2026-09-07): every public answer carries a GATED strip — "2 names masked ·
// 1 link removed · 1 quote paraphrased" — that opens a per-redaction list. Structured here, rendered by the page.
// The link rows are now the ones Public Redact DELETED on purpose (#169 review fix round 5, I2) —
// {kind:'link', detail: host+path, replaced_with:'[link removed]'} — not, as before, whichever urls
// Haiku happened to drop between the draft and its own output, which counted nothing the gate did.
const redactions = (red.removed || []).map(n => ({ kind: 'name', detail: n, replaced_with: 'a role phrase' }))
  .concat(red.removed_links || [])
  .concat((red.closed_sources || []).map(s => ({ kind: 'quote', detail: s, replaced_with: 'paraphrased, no names' })));
// index_incomplete is called out as its own, more specific note — a bad index is a different failure
// than a name/link that slipped through the smoother — the other two reasons keep the original note.
const refusalNote = red.index_incomplete === true
  ? 'Refused: the member name index was incomplete, so no name could be vouched for.'
  : 'Refused: a closed-source name or an unknown link survived the public pass.';
return [{ json: { text, notes: refused ? notes.concat([refusalNote]) : notes,
                  sources: red.public_urls || [], evidence_classes: red.classes || {}, refused, removed: red.removed || [], leftover: left,
                  leftover_links: leftLinks, redactions } }];
"""

MOD_ONE_LINE = " ".join(l.strip() for l in MOD.splitlines() if l.strip() and not l.strip().startswith("//"))
ok, err = node_check(MOD_ONE_LINE + " extractEvidenceRows([]);")
if not ok:
    sys.exit("MOD_ONE_LINE does not parse: " + err)

CLASSIFY_JSONBODY = ("={{ (() => { " + MOD_ONE_LINE + " const ev = extractEvidenceRows($('Answer Parse').first().json.messages); "
                      "return JSON.stringify({ p_urls: ev.urls.slice(0, 200), p_source_ids: ev.source_ids.slice(0, 200) }); })() }}")

# `digest.public_gate_name_index()` holds 5,394 rows, but PostgREST hard-caps ANY single response
# from this endpoint at 1000 (confirmed empirically 2026-09-07: a bare POST call, and even a POST
# with an explicit `Range: 0-9999` header, both come back `content-range: 0-999/5394` — the offset
# is silently ignored on POST). A single-call design (as a literal reading of the brief's own node
# spec would produce) would leave ~4,400 members' names — 81% of the index — NEVER checked by
# `backedNames`/`redact`/`leftoverNames`, since those functions only ever see the `names` list this
# node hands them: an unbacked name outside the fetched page would sail into a "public" answer
# completely unmasked, exactly the failure this whole ticket exists to prevent. Confirmed (same
# date) that GET, not POST, DOES honor `Range`/`Range-Unit: items` offset on this RPC (page 2 of
# `Range: 1000-1999` returns different rows than page 1; the tail page `5000-5999` correctly
# returns the last 394; a page past the end returns `[]`) — and `Load Recent Turns` already proves
# the exact same `Supabase secret (digest mirror)` credential + `Accept-Profile: digest` (not
# `Content-Profile`, which is for writes) works for a GET call on this graph. So this node runs as
# GET with the HTTP Request node's native "Update a Parameter in Each Request" pagination,
# incrementing a `Range` header by 1000 each page, stopping when a page comes back empty — n8n
# accumulates every page's split-out items into one combined output (`$pageCount` starts at 0 per
# n8n's own docs), giving `Public Redact` all 5,394 rows in the same `{name, kind}`-per-item shape
# the brief's code already expects from `$('Fetch Name Index (Supabase)').all()`.
#
# FIX ROUND 1 (2026-09-07 review): `limitPagesFetched`/`maxRequests` is a HARD CAP on this fetch,
# not a soft hint — the original `maxRequests: 10` (10,000 rows) comfortably covered today's 5,394
# rows, but if the index ever grew past the cap, this node would silently hand `Public Redact` a
# TRUNCATED `names` list, and any member past the last fetched page would never be checked by
# `backedNames`/`redact`/`leftoverNames` — the exact silent-truncation failure this node exists to
# prevent, just at a higher ceiling. The previous comment here claimed this "fails LOUD"; nothing
# actually asserted the fetched count, so it did not. Raised to `maxRequests: 50` (50,000 rows of
# headroom, ~9x today's size) AND made the claim true: `Public Redact` (below) now computes
# `index_incomplete` from `nameRows.length` — true when the fetch came back EMPTY (indistinguishable
# here from a real outage) or landed EXACTLY on the 50,000 cap on a clean 1000-row page boundary
# (every page came back full, so more members could exist past the last page fetched) — and
# `Public Verify` forces `refused: true` whenever that flag is set, with its own note. A truncated
# fetch now fails the turn closed instead of silently under-masking. Validated structurally with
# n8n-mcp `validate_node` (valid: true, 0 errors) before ever being written to staging.
NAME_INDEX_RANGE_EXPR = "={{ ($pageCount * 1000) + '-' + ($pageCount * 1000 + 999) }}"

# The `Public?` IF-node's own condition `leftValue` — named so the pre-flight `check_expr` call
# below and the node's own `parameters` can never drift apart (#169 review fix round 1: this
# expression previously had no syntax check at all).
PUBLIC_IF_LEFTVALUE = "={{ String($('Log Inbound').first().json.mode || '') }}"


def main():
    parser = argparse.ArgumentParser(
        description="#169 Public Gate on STAGING — insert/refresh the public-gate node chain (see module docstring).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", metavar="DIR", default=None,
                       help="compute the patched graph and print the summary; if DIR is given, also write "
                            "DIR/staging_before.json and DIR/staging_after.json. Never writes to n8n. Default when no flag is given.")
    mode.add_argument("--apply", action="store_true",
                       help="PUT the patched graph to STAGING and bounce the workflow — the live write.")
    args = parser.parse_args()

    wf = api("GET", f"/workflows/{STAGING_ID}")
    if not isinstance(wf, dict) or "nodes" not in wf:
        sys.exit(f"NEEDS_CONTEXT: GET /workflows/{STAGING_ID} did not return a graph: {str(wf)[:500]}")
    before_json = json.dumps(wf, indent=2)
    nodes = {n["name"]: n for n in wf["nodes"]}
    conn = wf["connections"]

    # ---- preconditions: fail closed on any drift from what Task 5 left behind ----
    required = ("Web?", "Web Response", "Format Web", "Save Web (Supabase)", "Fact Check", "Log Inbound", "Answer Parse")
    missing = [n for n in required if n not in nodes]
    if missing:
        sys.exit(f"NEEDS_CONTEXT: required node(s) missing from staging graph: {missing}")

    web_true = conn.get("Web?", {}).get("main", [[]])[0]
    PRE = [{"node": "Format Web", "type": "main", "index": 0}]
    POST = [{"node": "Public?", "type": "main", "index": 0}]
    if web_true not in (PRE, POST):
        sys.exit(f"NEEDS_CONTEXT: Web? true-output is {web_true!r}, expected {PRE!r} (fresh, pre-gate) "
                  f"or {POST!r} (gate already applied, idempotent re-run)")

    creds = api("GET", "/credentials?limit=250").get("data", [])
    sb = next((c for c in creds if c.get("type") == "httpHeaderAuth" and c.get("name") == "Supabase secret (digest mirror)"), None)
    if not sb:
        sys.exit("NEEDS_CONTEXT: credential 'Supabase secret (digest mirror)' (httpHeaderAuth) not found")
    if sb["id"] != "QHLDE4VHvm8jrVds":
        sys.exit(f"NEEDS_CONTEXT: 'Supabase secret (digest mirror)' id drifted to {sb['id']!r}, expected QHLDE4VHvm8jrVds")

    wx, wy = nodes["Web?"]["position"]

    # ---- pre-flight JS syntax checks (defense in depth; MOD_ONE_LINE's own check already ran at import time) ----
    check_expr("Public? condition leftValue", PUBLIC_IF_LEFTVALUE)  # #169 review fix round 1: was uncovered
    check_code("Public Redact", PUBLIC_REDACT)
    check_code("Public Verify", PUBLIC_VERIFY)
    check_expr("Classify Evidence (Supabase) jsonBody", CLASSIFY_JSONBODY)
    check_expr("Fetch Name Index (Supabase) pagination Range header", NAME_INDEX_RANGE_EXPR)
    check_expr("Public Smooth (Claude) jsonBody", PUBLIC_SMOOTH_BODY)

    new_nodes = [
        {"name": "Public?", "type": "n8n-nodes-base.if", "typeVersion": 2, "position": [wx + 220, wy - 200],
         "parameters": {"conditions": {"combinator": "and", "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
             "conditions": [{"id": "is_public", "leftValue": PUBLIC_IF_LEFTVALUE, "operator": {"operation": "equals", "type": "string"}, "rightValue": "public"}]}, "options": {}}},
        {"name": "Classify Evidence (Supabase)", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [wx + 440, wy - 320],
         "alwaysOutputData": True,
         "parameters": {"method": "POST", "url": f"{SUPA}/rpc/public_gate_classify", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
             "sendHeaders": True, "headerParameters": {"parameters": [{"name": "Content-Profile", "value": "digest"}]},
             "sendBody": True, "specifyBody": "json",
             "jsonBody": CLASSIFY_JSONBODY,
             "options": {"timeout": 20000}}, "credentials": {"httpHeaderAuth": {"id": sb["id"], "name": sb["name"]}}},
        {"name": "Fetch Name Index (Supabase)", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [wx + 440, wy - 80],
         "alwaysOutputData": True,
         "parameters": {"method": "GET", "url": f"{SUPA}/rpc/public_gate_name_index", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
             "sendHeaders": True, "headerParameters": {"parameters": [{"name": "Accept-Profile", "value": "digest"}, {"name": "Range-Unit", "value": "items"}]},
             "sendBody": False,
             "options": {"timeout": 20000, "pagination": {"pagination": {
                 "paginationMode": "updateAParameterInEachRequest",
                 "parameters": {"parameters": [{"type": "headers", "name": "Range", "value": NAME_INDEX_RANGE_EXPR}]},
                 "paginationCompleteWhen": "responseIsEmpty",
                 "limitPagesFetched": True, "maxRequests": 50, "requestInterval": 0,  # #169 fix round 1: 10 -> 50 (50,000-row headroom)
             }}}}, "credentials": {"httpHeaderAuth": {"id": sb["id"], "name": sb["name"]}}},
        # Synchronization barrier, not a data source — Public Redact reads both httpRequest nodes
        # above by NAME, never through this node's own (irrelevant) merged output. Restores the node
        # the brief's own PUBLIC_REDACT comment already names ("two httpRequest outputs merged by
        # 'Public Inputs'"); see the module docstring for the live execution (137693) that proved it
        # necessary. typeVersion 3.2 per n8n-mcp's own versionNotice for nodes-base.merge.
        {"name": "Public Inputs", "type": "n8n-nodes-base.merge", "typeVersion": 3.2, "position": [wx + 660, wy - 200],
         "parameters": {"mode": "append", "numberInputs": 2}},
        {"name": "Public Redact", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [wx + 880, wy - 200], "parameters": {"jsCode": PUBLIC_REDACT}},
        {"name": "Public Smooth (Claude)", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [wx + 1100, wy - 200],
         "parameters": {**nodes["Fact Check"]["parameters"], "jsonBody": PUBLIC_SMOOTH_BODY},
         "credentials": nodes["Fact Check"].get("credentials", {})},
        {"name": "Public Verify", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [wx + 1320, wy - 200], "parameters": {"jsCode": PUBLIC_VERIFY}},
    ]

    # ---- idempotent upsert: update existing nodes in place (by name); append only if truly new ----
    by_name = {n["name"]: n for n in wf["nodes"]}
    added, updated = [], []
    for nd in new_nodes:
        if nd["name"] in by_name:
            by_name[nd["name"]].update(nd)
            updated.append(nd["name"])
        else:
            wf["nodes"].append(nd)
            by_name[nd["name"]] = nd
            added.append(nd["name"])

    # ---- wiring: Web? true -> Public? ; Public? true -> Classify + Name Index (true parallel
    # fan-out, each fed directly by Public?'s single item so neither multiplies the other's item
    # count) -> Public Inputs (Merge, waits for both — see docstring) -> Public Redact (still reads
    # both httpRequest nodes by NAME, ignoring Public Inputs' own merged output) -> Smooth -> Verify
    # -> Format Web ; Public? false -> Format Web. Only Web?'s true output (index 0) is touched;
    # false (WhatsApp/silent, index 1) is left exactly as Task 5 wired it. Always re-asserted, so
    # this is idempotent too. ----
    conn["Web?"]["main"][0] = [{"node": "Public?", "type": "main", "index": 0}]
    conn["Public?"] = {"main": [[{"node": "Classify Evidence (Supabase)", "type": "main", "index": 0}, {"node": "Fetch Name Index (Supabase)", "type": "main", "index": 0}],
                                 [{"node": "Format Web", "type": "main", "index": 0}]]}
    conn["Classify Evidence (Supabase)"] = {"main": [[{"node": "Public Inputs", "type": "main", "index": 0}]]}
    conn["Fetch Name Index (Supabase)"] = {"main": [[{"node": "Public Inputs", "type": "main", "index": 1}]]}
    conn["Public Inputs"] = {"main": [[{"node": "Public Redact", "type": "main", "index": 0}]]}
    conn["Public Redact"] = {"main": [[{"node": "Public Smooth (Claude)", "type": "main", "index": 0}]]}
    conn["Public Smooth (Claude)"] = {"main": [[{"node": "Public Verify", "type": "main", "index": 0}]]}
    conn["Public Verify"] = {"main": [[{"node": "Format Web", "type": "main", "index": 0}]]}

    # ---- guard: the only respondToWebhook node anywhere on the graph must remain the pre-existing,
    # disconnected 'Respond Challenge' (Meta's GET handshake) — Task 5's Bug 4 must never recur ----
    rtw = sorted(n["name"] for n in wf["nodes"] if n.get("type") == "n8n-nodes-base.respondToWebhook")
    if rtw != ["Respond Challenge"]:
        sys.exit(f"NEEDS_CONTEXT: unexpected respondToWebhook node set after edit: {rtw} (expected only ['Respond Challenge'])")

    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings", "staticData") if k in wf}

    if not args.apply:
        if args.dry_run:
            os.makedirs(args.dry_run, exist_ok=True)
            before_path = os.path.join(args.dry_run, "staging_before.json")
            after_path = os.path.join(args.dry_run, "staging_after.json")
            open(before_path, "w").write(before_json)
            open(after_path, "w").write(json.dumps(body, indent=2))
            print(f"  wrote {before_path}")
            print(f"  wrote {after_path}")
        print(f"DRY RUN — public gate in place ({len(wf['nodes'])} nodes) — added {added}, updated {updated} (staging NOT written, no bounce)")
        return

    api("PUT", f"/workflows/{STAGING_ID}", body)
    bounce(STAGING_ID)
    print(f"staging updated + bounced: public gate in place ({len(wf['nodes'])} nodes) — added {added}, updated {updated}")


if __name__ == "__main__":
    main()
