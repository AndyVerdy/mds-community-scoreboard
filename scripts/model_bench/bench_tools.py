#!/usr/bin/env python3
"""Tool execution for the model bench — a Python mirror of the workflow's tool layer.

Mirrors, in order, what the live graph does between a model's tool call and the tool_result
it gets back (prod snapshot 2026-09-02, nodes Answer Parse → Voyage Embed → Attach Embedding
→ Answer Tool → Answer Merge):
  1. p_phone injected from the asker (Answer Parse) — never model-settable
  2. Voyage embedding attached for the vector tools (Voyage Embed + Attach Embedding)
  3. content_search always includes call_transcript unless chat-scoped (Attach Embedding)
  4. argument coercion against the schema the model was handed (Attach Embedding)
  5. model-facing name → executed RPC name (Attach Embedding EXEC_NAME)
  6. routing: digest.mds.co app routes for org_docs / member_intro / find / event_*,
     Supabase RPC for everything else (Answer Tool)
  7. result → tool_result body: the tool_error + FAILNOTE shape, per-row tiered trimming with
     clipSafe + restrictFix, the over-CAP halving squeeze, the 26K backstop (Answer Merge)
NOT mirrored, by controller decision: Answer Merge's S1–S16 evidence stamps (node lines ~160-535).
Write-capable tools are STUBBED (see write_stub): member_intro, report_create and
event_schedule op=remind/unremind all reach a real member or the MDS team.
When the graph changes, this file changes with it — re-extract the nodes and re-run the tests.
"""
import json, re, subprocess

SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
VOYAGE = "https://api.voyageai.com/v1/embeddings"
APP = "https://digest.mds.co/api/olivia"
# Attach Embedding — EXEC_NAME. The JS object literal repeats two keys; the LAST value wins.
EXEC_NAME = {"content_search": "content_search_v2", "member_dossier": "member_dossier_v2",
             "event_history": "event_history_v2", "member_match": "member_match_v2",
             "multi_source": "multi_source_v2", "member_card": "member_card_v2",
             "video_search": "video_search_v2", "partner_lookup": "partner_lookup_v2",
             "event_lookup": "event_lookup_v3", "chat_recommendations": "chat_recommendations_v3"}
EMBED_TOOLS = ("content_search", "video_search", "partner_lookup", "event_lookup", "expertise_search")
ARRAY_ARGS = ("p_terms", "p_sources", "p_kinds", "p_dims", "p_want")   # every text[] param in schema digest
TIER = lambda i: 1600 if i < 5 else (500 if i < 15 else 220)
CAP = 26000
SPLIT = re.compile(r"\s*[,;|\n]\s*")
TRUNC = ' …[truncated — narrow the query for more]"'
STATUS_MARK = "\n__HTTP_STATUS__"
# Answer Merge lines 13-21, verbatim. A tool ERROR is not an empty result: without this note the
# model reports a 500 to the member as "nothing came up" (B5039, fixwave 5).
FAILNOTE = (
    "MILLIE — DETERMINISTIC NOTE: this tool call FAILED. It is NOT an empty result and it is NOT "
    "evidence that nothing exists. Never tell the member that nothing came up, that you found no "
    "matches, or that there is nothing on file, on the strength of this. Read the detail: if it "
    "names a bad argument (a malformed array literal, invalid JSON, a wrong type) then FIX the "
    "argument and call the SAME tool one more time — every array parameter (p_terms, p_sources, "
    "p_kinds, p_dims, p_want) takes a LIST of separate words, never one comma-joined string, and "
    "find's `where` takes a real object, never a string. If the retry fails too, or the detail is "
    "a server error, say plainly in your reply that the search itself could not run just now and "
    "offer to try again — never dress a failure up as a miss.")
URLISH = re.compile(r"(^|_)url$|link$|permalink|href", re.I)
SCHEME = re.compile(r"^https?://", re.I)


def _j(v):
    """JSON.stringify's exact output shape: no separator padding, non-ASCII left raw. The padding
    is not cosmetic — it moved the 26K CAP boundary by 200 chars on a 100-row result."""
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def post(url, headers, body, timeout=45):
    """POST → (http_status, parsed_body).

    The STATUS is half the answer. Answer Tool runs with fullResponse, so Answer Merge sees a 401
    or a 500 even when the body is not a JSON {"error": …} — and turns it into a tool_error. Read
    only the body and an auth failure or an HTML 502 page reads to the model as an empty result.
    status is 0 when curl never completed a request (transport failure).
    """
    cmd = ["curl", "-sS", "-X", "POST", url, "--max-time", str(timeout),
           "-w", STATUS_MARK + "%{http_code}", "--data-binary", "@-"]
    for h, v in headers.items():
        cmd += ["-H", f"{h}: {v}"]
    r = subprocess.run(cmd, input=_j(body), capture_output=True, text=True)
    raw, status = r.stdout, 0
    if STATUS_MARK in raw:
        raw, _, tail = raw.rpartition(STATUS_MARK)
        tail = tail.strip()
        status = int(tail) if tail.isdigit() and tail != "000" else 0
    try:
        return status, json.loads(raw)
    except Exception:
        return status, {"error": (raw or r.stderr or "no response").strip()[:300]}


def voyage_query(args):
    """The embedded string, exactly as the Voyage Embed node builds it:
        const q = a.p_query || (Array.isArray(a.p_terms) ? a.p_terms.join(' ') : '');
        input: [String(q).slice(0, 400) || '(empty)']
    A STRING p_terms is NOT char-joined (the node's Array.isArray guard), and a blank query is
    embedded as the literal '(empty)' — the node always calls Voyage, so the bench must too."""
    a = args or {}
    q = a.get("p_query")
    if not q:
        terms = a.get("p_terms")
        q = " ".join(str(t) for t in terms) if isinstance(terms, list) else ""
    return str(q)[:400] or "(empty)"


def voyage_embed(args, key):
    _st, d = post(VOYAGE, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                  {"model": "voyage-3.5-lite", "input": [voyage_query(args)], "input_type": "query",
                   "output_dimension": 1024}, timeout=10)      # the node: options.timeout 10000
    try:
        return d["data"][0]["embedding"]
    except Exception:
        return None                        # embed failures degrade to keyword search, as in the node


def transcript_rule(name, args):
    """content_search always searches call transcripts unless the ask is chat-scoped."""
    if name != "content_search":
        return args
    src = args.get("p_sources")
    if isinstance(src, list) and src and "call_transcript" not in src and not args.get("p_chat"):
        return {**args, "p_sources": src + ["call_transcript"]}
    return args


def coerce_args(name, args, tools):
    """Coerce every argument against the schema the model was handed; ARRAY_ARGS is the fallback."""
    schema = next((t for t in tools or [] if t.get("name") == name), None)
    props = ((schema or {}).get("input_schema") or {}).get("properties") or {}
    out = {}
    for k, v in args.items():
        want = (props.get(k) or {}).get("type") or ("array" if k in ARRAY_ARGS else None)
        if want == "array" and not isinstance(v, list):
            if v is None or v == "":
                continue
            parts = [s.strip() for s in SPLIT.split(str(v)) if s.strip()]
            out[k] = parts or [str(v).strip()]
        elif want == "object" and isinstance(v, str):
            try:
                o = json.loads(v)
                out[k] = o if isinstance(o, (dict, list)) else v
            except Exception:
                out[k] = v
        elif want == "integer" and isinstance(v, str) and re.fullmatch(r"-?\d+", v.strip()):
            out[k] = int(v.strip())
        elif want == "string" and isinstance(v, list):
            out[k] = ", ".join(str(x) for x in v if x)
        else:
            out[k] = v
    return out


def route(name, args, phone):
    """(url, body) exactly as Answer Tool builds them. `name` is the MODEL-facing name.

    Answer Tool's jsonBody: member_intro gets {op:'request', phone}; event_* / org_docs / find all
    get {phone} (plus {op:'people'} for event_who); everything else posts tool_args untouched."""
    if name == "member_intro":
        return f"{APP}/intro", {**args, "op": "request", "phone": phone}
    if name == "org_docs":
        return f"{APP}/kb", {**args, "phone": phone}
    if name == "find":
        return f"{APP}/find", {**args, "phone": phone}
    if name.startswith("event_"):
        extra = {"phone": phone}
        if name == "event_who":
            extra["op"] = "people"
        return f"{APP}/schedule", {**args, **extra}
    return f"{SUPA}/rpc/{EXEC_NAME.get(name, name)}", args


def clip_safe(s, n):
    """Answer Merge ~24-34 — trim to n chars, but never end inside a URL."""
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(" ")
    tail = cut if sp == -1 else cut[sp + 1:]
    if SCHEME.match(tail) and not re.search(r"\s", s[n:n + 1]):
        cut = "" if sp == -1 else cut[:sp]
    return cut + "…"


def restrict_fix(row):
    """Answer Merge ~45-58 — a row this asker was SERVED carries no restriction vocabulary.

    video_search_v2 returns the LIBRARY's is_restricted flag while withholding on a grant-aware
    test; a row the tool really withheld carries its own '[RESTRICTED VIDEO' sentinel. Without
    this she says "this one's restricted, but on file: …" and then serves it (B5025)."""
    if (isinstance(row, dict) and row.get("is_restricted") is True
            and not str(row.get("description_snippet") or "").startswith("[RESTRICTED VIDEO")):
        row.pop("is_restricted", None)
        row.pop("access_note", None)
    return row


def compact(val):
    """Keep EVERY row, trim long text fields by rank tier — never truncate rows."""
    if not isinstance(val, list):
        return val
    out = []
    for i, row in enumerate(val):
        if not isinstance(row, dict):
            out.append(row)
            continue
        out.append(restrict_fix({k: (clip_safe(v, TIER(i)) if isinstance(v, str) and len(v) > TIER(i) else v)
                                 for k, v in row.items()}))
    return out


def _squeeze_row(row, i, f):
    """One halving pass over one row (Answer Merge ~122-138). url/link fields are exempt outright;
    everything else goes through clip_safe. NOTE: the live node does NOT re-apply restrictFix in
    the squeeze — mirrored as-is so the bench shows the model what prod would show it."""
    if not isinstance(row, dict):
        return row
    cut = max(60, int(TIER(i) * f))
    o = {}
    for k, v in row.items():
        if isinstance(v, str) and len(v) > cut:
            o[k] = v if URLISH.search(k) else clip_safe(v, cut)
        else:
            o[k] = v
    return o


def _dump(v):
    try:
        return _j(v)
    except Exception:
        return str(v)


def result_body(r, tool="", http_status=0):
    """The tool_result body, as Answer Merge builds it (node lines ~73-150).

    A TOOL ERROR IS NOT AN EMPTY RESULT: a failure is handed over as
    {tool_error, tool, http_status, detail} + the FAILNOTE, never as {"error": …} that reads
    like a miss. Over CAP the row text is squeezed in halving passes so EVERY row survives;
    the blunt slice is only the impossible-case backstop."""
    st = int(http_status or 0)
    err_text = ""
    # transport failure — curl never got an HTTP response. Live analogue: n8n's onError item
    # { error: { message } } with no body/statusCode (Answer Merge ~88-92).
    if not st and isinstance(r, dict) and r.get("error") and "body" not in r:
        e = r.get("error")
        err_text = str((e.get("description") or e.get("message")) if isinstance(e, dict) else e) or "tool call failed"
        m = re.search(r"(\d{3})", err_text)
        if m:
            st = int(m.group(1))
    if isinstance(r, dict) and "body" in r and ("statusCode" in r or "headers" in r):
        st = int(r.get("statusCode") or 0) or st
        r = r.get("body")
    if not err_text and st >= 400:                       # Answer Merge ~97
        err_text = f"HTTP {st} — " + _dump(r)[:300]
    if err_text:
        return _j({"tool_error": True, "tool": str(tool or ""),
                   "http_status": st or "error", "detail": err_text[:500]}) + "\n" + FAILNOTE
    if r is None:
        body = _j({"error": "tool returned nothing"})
    elif isinstance(r, dict) and (r.get("error") or (r.get("message") and r.get("code"))):
        return _j({"tool_error": True, "tool": str(tool or ""),
                   "detail": str(r.get("message") or r.get("error"))[:400]}) + "\n" + FAILNOTE
    else:
        try:
            body = _j(compact(r))
        except Exception:
            body = '"unserializable result"'
    if len(body) > CAP and isinstance(r, list):          # Answer Merge ~117-142
        f = 0.5
        while len(body) > CAP and f >= 0.03:
            try:
                body = _j([_squeeze_row(row, i, f) for i, row in enumerate(r)])
            except Exception:
                break
            f = f / 2
    if len(body) > CAP:                                  # Answer Merge ~143-150
        cut = body[:CAP]
        sp = cut.rfind(" ")
        if sp > CAP * 0.9:
            cut = cut[:sp]
        body = cut + TRUNC
    return body


def write_stub(name, args):
    """Tools that WRITE outside the warehouse are never executed by the bench — the reason, in
    the tool's own result, so the model can still answer around it.

    · member_intro op:'request' messages a real member.
    · report_create INSERTs into digest.olivia_reports and its trigger writes member_events —
      a bench run would file a pile of fake reports at the MDS team.
    · event_schedule op=remind/unremind creates (or cancels) a real reminder, which later fires
      a real WhatsApp send.
    Every other tool executes for real against the warehouse, exactly as the workflow does."""
    if name == "member_intro":
        return _j({"error": "member_intro is disabled in the bench — op:'request' would "
                            "message a real member"})
    if name == "report_create":
        return _j({"error": "report_create is disabled in the bench — it would file a real report "
                            "to the MDS team (digest.olivia_reports insert, and its trigger writes "
                            "member_events)"})
    op = str((args or {}).get("op") or "")
    if name == "event_schedule" and op in ("remind", "unremind"):
        return _j({"error": f"event_schedule op={op} is disabled in the bench — it would create "
                            "or cancel a real reminder that later sends a real WhatsApp message"})
    return None


def run_tool(name, args, tools, keys, phone):
    """One tool call, start to finish, the way the graph runs it. Returns the tool_result body."""
    a = dict(args or {})
    a["p_phone"] = phone                   # SECURITY: injected here, never model-settable
    stub = write_stub(name, a)
    if stub:
        return stub
    if name in EMBED_TOOLS:
        emb = voyage_embed(a, keys["voyage"])
        if emb:
            a["p_embedding"] = _j(emb)
    a = transcript_rule(name, a)
    a = coerce_args(name, a, tools)
    url, body = route(name, a, phone)
    headers = {"apikey": keys["supa"], "Authorization": f"Bearer {keys['supa']}",
               "Accept-Profile": "digest", "Content-Profile": "digest",
               "Content-Type": "application/json", "X-Olivia-Secret": keys["olivia_secret"]}
    status, r = post(url, headers, body, timeout=30)
    return result_body(r, tool=name, http_status=status)
