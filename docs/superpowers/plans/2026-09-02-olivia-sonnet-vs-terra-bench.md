# Olivia — Sonnet 5 vs GPT-5.6 Terra Bench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Answer the locked 100-question Olivia bank with Claude Sonnet 5 and GPT-5.6 Terra under identical conditions, outside n8n, and produce one report with cost per answer and dual-judged quality side by side. Ticket #156, spec `docs/superpowers/specs/2026-09-02-olivia-sonnet-vs-terra-bench-design.md`.

**Architecture:** The existing bench harness in `/Users/Born/mds-scorecard-tools/` (`kimi_harvest.py` → `kimi_bench.py` → `bench_compare.py`, judge in `olivia_eval.py`) is brought up to the CURRENT workflow (prod snapshot 2026-09-02) and given an OpenAI path. One silent run of the bank on STAGING is harvested for the exact `Answer Seed` request bodies; both vendors replay those bodies through a Python mirror of the workflow's tool layer against the same Supabase RPCs and app routes; two judges grade every answer; one compare report lands in the Scorecard repo. No n8n graph is edited.

**Tech Stack:** Python 3.12 stdlib only (`curl` via subprocess, `unittest`), Anthropic Messages API, OpenAI Responses API (tools + reasoning; chat completions refuses tools with reasoning on Terra) and OpenAI chat completions (judge, no tools), Supabase PostgREST, Voyage embeddings, n8n REST API (read-only), `scripts/olivia_wf.py` (lock/diff), `scripts/run_eval_100.py` (fires the bank).

## Global Constraints

- **Prod is never touched.** No promote, no graph edit, no bench traffic at the prod webhook. Staging receives exactly one silent bank run; `diff prod staging` must be identical (except webhook path/webhookId) before and after.
- **Two agents, one repo:** hold `python3 scripts/olivia_wf.py lock` for the harvest run only, release the moment it ends, never force it. Re-read board/log right before every edit; commit only your own hunks.
- **Keys come from `/Users/Born/mds-digest-web/.env.local`** (git-ignored): `CENTURION_ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `SUPABASE_SECRET_KEY`, `VOYAGE_API_KEY`, `OLIVIA_SCHEDULE_SECRET` or `OLIVIA_IOS_SECRET` (the app-route secret; never print it), `N8N_API_URL`, `N8N_API_KEY`. Bare values only.
- **Models and list prices ($ per 1M tokens, 2026-09-02):** `claude-sonnet-5` in 2.00 / out 10.00 / cache read 0.20 / cache write 2.50 · `gpt-5.6-terra` in 2.00 / out 12.00 / cached in 0.20 / no write charge. Prod runs Sonnet 5 with `thinking: disabled`, `max_tokens: 2000`, `tool_choice: {type:'any'}` on lap 1, 5 laps max.
- **Terra runs:** `reasoning.effort` `medium` (OpenAI's default — the spec's primary) AND `none` (exact parity with prod's thinking-off; added after the API probe showed chat completions rejects tools with reasoning on). Both reported.
- **Judges:** `claude-sonnet-5` (primary, comparable with every past run) and `gpt-5.6-terra` (cross-check). Same rubric text. Disagreements listed per question, never auto-resolved.
- **`member_intro` is stubbed in the bench** — its `op:'request'` messages a real member. Everything else executes for real against the warehouse, exactly as the workflow does.
- **Probe identity:** the staging run fires as `17866578153` (Andy, the only phone that may be simulated, `scripts/olivia_selftest.py:33`); seeds carry `phone` from `Answer Seed.to` and the bench injects it as `p_phone`.
- **`/Users/Born/mds-scorecard-tools/` is NOT a git repository** (checked 2026-09-02). Code there is verified by its unittest suite, not by commits. Only the Scorecard repo (`/Users/Born/Scorecard`) gets commits: the plan, the board, the logs, the reports, the seeds copy.
- **Tests:** `cd /Users/Born/mds-scorecard-tools && python3 -m unittest discover -s tests -v`. No pytest on this Mac.
- **Every "it works" cites live proof** — exec ids, counts, file paths, exit codes.

---

## File map

| File | Responsibility |
|---|---|
| `mds-scorecard-tools/bench_tools.py` (create) | Python mirror of the workflow's tool layer: p_phone injection, Voyage embedding, transcript rule, schema coercion, `EXEC_NAME` remap, routing (Supabase RPC vs digest app routes), result body shaping. One function `run_tool(name, args, tools, keys, phone) -> str`. |
| `mds-scorecard-tools/tests/__init__.py` (create) | Makes `tests` a package for `unittest discover`. |
| `mds-scorecard-tools/tests/test_bench_tools.py` (create) | Pure-function tests for the tool layer. |
| `mds-scorecard-tools/kimi_harvest.py` (modify) | `seed_from_execution()` pure function + CLI flags `--bank --workflow --out`; keeps full history; records `phone`; lists missing bank ids with reasons. |
| `mds-scorecard-tools/tests/test_harvest.py` (create) | Tests `seed_from_execution` on a synthetic execution. |
| `mds-scorecard-tools/kimi_bench.py` (modify) | Model registry with current prices; Anthropic loop replays history; new OpenAI Responses loop with `--effort`; retry/backoff; `reasoning` metric; `--seeds`, `--judges`; dual-judge rows; report header. |
| `mds-scorecard-tools/tests/test_bench_loops.py` (create) | Tests message conversion, usage → metrics, cost math, retry classification. |
| `mds-scorecard-tools/olivia_eval.py` (modify) | `judge_prompt()` extracted (rubric unchanged); `judge_one()` (Anthropic) behaviour unchanged; new `judge_one_openai()` + `parse_openai_verdict()`. |
| `mds-scorecard-tools/tests/test_judge.py` (create) | Tests the rubric builder and the OpenAI verdict parser. |
| `mds-scorecard-tools/bench_compare.py` (modify) | N run tags, prices imported from `kimi_bench.PRICES`, per-judge rows, disagreement section, reasoning column, `--out`. |
| `mds-scorecard-tools/tests/test_compare.py` (create) | Tests `stats()` per judge and `disagreements()`. |
| `Scorecard/OLIVIA_MODEL_BENCH_<tag>_<HHMM>.md/.json` (output) | Per-run reports. |
| `Scorecard/OLIVIA_MODEL_COMPARE_2026-09-02.md` (output) | The deliverable. |
| `Scorecard/OLIVIA_SPRINT_4.md`, `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md`, `OLIVIA_NEXT_SESSION.md` (modify) | Close block, log entry, index line, handoff. |

---

### Task 1: `bench_tools.py` — the tool layer, mirrored from the live graph

**Files:**
- Create: `/Users/Born/mds-scorecard-tools/bench_tools.py`
- Create: `/Users/Born/mds-scorecard-tools/tests/__init__.py` (empty)
- Test: `/Users/Born/mds-scorecard-tools/tests/test_bench_tools.py`

**Interfaces:**
- Produces: `run_tool(name: str, args: dict, tools: list, keys: dict, phone: str) -> str` (a tool_result body string), `EXEC_NAME`, `EMBED_TOOLS`, `coerce_args(name, args, tools) -> dict`, `transcript_rule(name, args) -> dict`, `route(name, args, phone) -> (url, body)`, `result_body(r) -> str`, `compact(val)`, `post(url, headers, body, timeout=45) -> dict`.
- `keys` shape: `{"supa": str, "voyage": str, "olivia_secret": str}`.

Source of truth for every rule below: the prod snapshot `olivia_snapshots/prod_2026-09-02T034911Z_post-promote.json`, nodes `Answer Parse` (p_phone), `Voyage Embed`, `Attach Embedding` (embed list, transcript rule, coercion, `EXEC_NAME`), `Answer Tool` (routing, headers), `Answer Merge` (result body). Extract them with:

```bash
python3 - <<'EOF'
import json
g=json.load(open("olivia_snapshots/prod_2026-09-02T034911Z_post-promote.json"))
nodes=g.get("nodes") or g["graph"]["nodes"]
for n in nodes:
    if n["name"] in ("Attach Embedding","Answer Tool","Answer Merge"):
        p=n["parameters"]; print("=====",n["name"]); print(p.get("jsCode") or json.dumps({k:p[k] for k in ("url","jsonBody") if k in p},indent=1))
EOF
```

- [ ] **Step 1: Write the failing tests**

```python
# /Users/Born/mds-scorecard-tools/tests/test_bench_tools.py
import json, unittest
import bench_tools as bt

TOOLS = [
    {"name": "content_search", "input_schema": {"type": "object", "properties": {
        "p_query": {"type": "string"}, "p_terms": {"type": "array"}, "p_sources": {"type": "array"},
        "p_chat": {"type": "string"}}}},
    {"name": "find", "input_schema": {"type": "object", "properties": {
        "where": {"type": "object"}, "limit": {"type": "integer"}, "want": {"type": "string"}}}},
]


class ExecName(unittest.TestCase):
    def test_last_duplicate_key_wins_as_in_the_js_literal(self):
        self.assertEqual(bt.EXEC_NAME["event_lookup"], "event_lookup_v3")
        self.assertEqual(bt.EXEC_NAME["chat_recommendations"], "chat_recommendations_v3")
        self.assertEqual(bt.EXEC_NAME["content_search"], "content_search_v2")
        self.assertNotIn("expertise_search", bt.EXEC_NAME)


class TranscriptRule(unittest.TestCase):
    def test_appends_call_transcript(self):
        out = bt.transcript_rule("content_search", {"p_sources": ["wa_message"]})
        self.assertEqual(out["p_sources"], ["wa_message", "call_transcript"])

    def test_chat_scoped_untouched(self):
        a = {"p_sources": ["wa_message"], "p_chat": "MDS AI"}
        self.assertEqual(bt.transcript_rule("content_search", a), a)

    def test_no_sources_untouched_and_other_tools_untouched(self):
        self.assertEqual(bt.transcript_rule("content_search", {"p_query": "x"}), {"p_query": "x"})
        self.assertEqual(bt.transcript_rule("video_search", {"p_sources": ["a"]}), {"p_sources": ["a"]})


class Coerce(unittest.TestCase):
    def test_comma_string_becomes_array(self):
        out = bt.coerce_args("content_search", {"p_terms": "reseller, Summit; Singapore"}, TOOLS)
        self.assertEqual(out["p_terms"], ["reseller", "Summit", "Singapore"])

    def test_empty_array_arg_is_dropped(self):
        self.assertNotIn("p_terms", bt.coerce_args("content_search", {"p_terms": ""}, TOOLS))

    def test_array_arg_known_only_by_fallback_list(self):
        out = bt.coerce_args("member_match", {"p_want": "a|b"}, TOOLS)   # no schema for member_match
        self.assertEqual(out["p_want"], ["a", "b"])

    def test_object_string_parsed_and_bad_json_left_alone(self):
        out = bt.coerce_args("find", {"where": '{"state":"TX"}'}, TOOLS)
        self.assertEqual(out["where"], {"state": "TX"})
        out = bt.coerce_args("find", {"where": "not json"}, TOOLS)
        self.assertEqual(out["where"], "not json")

    def test_integer_string_and_list_to_string(self):
        out = bt.coerce_args("find", {"limit": " 12 ", "want": ["a", "", "b"]}, TOOLS)
        self.assertEqual(out["limit"], 12)
        self.assertEqual(out["want"], "a, b")

    def test_unknown_keys_pass_through(self):
        out = bt.coerce_args("find", {"p_phone": "1", "p_embedding": "[0.1]"}, TOOLS)
        self.assertEqual(out, {"p_phone": "1", "p_embedding": "[0.1]"})


class Route(unittest.TestCase):
    def test_supabase_rpc_uses_exec_name(self):
        url, body = bt.route("event_lookup", {"p_query": "x"}, "1786")
        self.assertEqual(url, "https://digest.mds.co/api/olivia/schedule")   # event_* goes to the app
        url, body = bt.route("member_match", {"p_state": "TX"}, "1786")
        self.assertEqual(url, bt.SUPA + "/rpc/member_match_v2")
        self.assertEqual(body, {"p_state": "TX"})

    def test_find_and_event_who_get_phone_and_op(self):
        url, body = bt.route("find", {"where": {}}, "1786")
        self.assertEqual((url, body["phone"]), ("https://digest.mds.co/api/olivia/find", "1786"))
        url, body = bt.route("event_who", {"p_event": "summit"}, "1786")
        self.assertEqual(body, {"p_event": "summit", "phone": "1786", "op": "people"})
        url, body = bt.route("event_schedule", {"op": "day"}, "1786")
        self.assertEqual(body, {"op": "day", "phone": "1786"})

    def test_org_docs_and_member_intro(self):
        self.assertEqual(bt.route("org_docs", {"q": "x"}, "1786"), ("https://digest.mds.co/api/olivia/kb", {"q": "x"}))
        url, body = bt.route("member_intro", {"target": "rec1"}, "1786")
        self.assertEqual((url, body["op"], body["phone"]), ("https://digest.mds.co/api/olivia/intro", "request", "1786"))


class ResultBody(unittest.TestCase):
    def test_error_shapes(self):
        self.assertEqual(json.loads(bt.result_body(None)), {"error": "tool returned nothing"})
        self.assertEqual(json.loads(bt.result_body({"code": "22P02", "message": "malformed array literal"})),
                         {"error": "malformed array literal"})
        self.assertEqual(json.loads(bt.result_body({"error": "boom"})), {"error": "boom"})

    def test_full_response_unwrapped(self):
        self.assertEqual(json.loads(bt.result_body({"statusCode": 200, "headers": {}, "body": [{"a": 1}]})), [{"a": 1}])

    def test_tiered_trim_keeps_every_row(self):
        rows = [{"t": "x" * 2000} for _ in range(20)]
        out = json.loads(bt.result_body(rows))
        self.assertEqual(len(out), 20)
        self.assertEqual(len(out[0]["t"]), 1601)     # 1600 + ellipsis
        self.assertEqual(len(out[6]["t"]), 501)
        self.assertEqual(len(out[19]["t"]), 221)

    def test_cap(self):
        body = bt.result_body([{"t": "y" * 1500} for _ in range(100)])   # 5×1500 + 10×501 + 85×221 ≈ 31K > CAP
        self.assertLessEqual(len(body), bt.CAP + 60)
        self.assertTrue(body.endswith('…[truncated — narrow the query for more]"'))


class RunToolStub(unittest.TestCase):
    def test_member_intro_never_leaves_the_machine(self):
        out = bt.run_tool("member_intro", {"target": "rec1"}, TOOLS, {"supa": "", "voyage": "", "olivia_secret": ""}, "1786")
        self.assertIn("member_intro is disabled in the bench", out)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/Born/mds-scorecard-tools && touch tests/__init__.py && python3 -m unittest tests.test_bench_tools -v 2>&1 | tail -3`
Expected: `ModuleNotFoundError: No module named 'bench_tools'`

- [ ] **Step 3: Write `bench_tools.py`**

```python
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
  7. result → tool_result body: error shape, per-row tiered trimming, 26K cap (Answer Merge)
member_intro is STUBBED: its op:'request' messages a real member. A bench never does that.
When the graph changes, this file changes with it — re-extract the three nodes and re-run the tests.
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


def post(url, headers, body, timeout=45):
    cmd = ["curl", "-sS", "-X", "POST", url, "--max-time", str(timeout), "--data-binary", "@-"]
    for h, v in headers.items():
        cmd += ["-H", f"{h}: {v}"]
    r = subprocess.run(cmd, input=json.dumps(body), capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"error": (r.stdout or r.stderr or "no response")[:300]}


def voyage_embed(args, key):
    q = args.get("p_query") or " ".join(args.get("p_terms") or [])
    if not str(q).strip():
        return None
    d = post(VOYAGE, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
             {"model": "voyage-3.5-lite", "input": [str(q)[:400]], "input_type": "query",
              "output_dimension": 1024}, timeout=20)
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
    """(url, body) exactly as Answer Tool builds them. `name` is the MODEL-facing name."""
    if name == "org_docs":
        return f"{APP}/kb", args
    if name == "member_intro":
        return f"{APP}/intro", {**args, "op": "request", "phone": phone}
    if name == "find":
        return f"{APP}/find", {**args, "phone": phone}
    if name.startswith("event_"):
        extra = {"phone": phone}
        if name == "event_who":
            extra["op"] = "people"
        return f"{APP}/schedule", {**args, **extra}
    return f"{SUPA}/rpc/{EXEC_NAME.get(name, name)}", args


def compact(val):
    """Keep EVERY row, trim long text fields by rank tier — never truncate rows."""
    if not isinstance(val, list):
        return val
    out = []
    for i, row in enumerate(val):
        if not isinstance(row, dict):
            out.append(row)
            continue
        out.append({k: (v[:TIER(i)] + "…" if isinstance(v, str) and len(v) > TIER(i) else v)
                    for k, v in row.items()})
    return out


def result_body(r):
    if isinstance(r, dict) and "body" in r and ("statusCode" in r or "headers" in r):
        r = r["body"]
    if r is None:
        body = json.dumps({"error": "tool returned nothing"})
    elif isinstance(r, dict) and (r.get("error") or (r.get("message") and r.get("code"))):
        body = json.dumps({"error": str(r.get("message") or r.get("error"))[:400]})
    else:
        try:
            body = json.dumps(compact(r), ensure_ascii=False)
        except Exception:
            body = '"unserializable result"'
    if len(body) > CAP:
        body = body[:CAP] + TRUNC
    return body


def run_tool(name, args, tools, keys, phone):
    """One tool call, start to finish, the way the graph runs it. Returns the tool_result body."""
    a = dict(args or {})
    a["p_phone"] = phone                   # SECURITY: injected here, never model-settable
    if name == "member_intro":
        return json.dumps({"error": "member_intro is disabled in the bench — op:'request' would message a real member"})
    if name in EMBED_TOOLS:
        emb = voyage_embed(a, keys["voyage"])
        if emb:
            a["p_embedding"] = json.dumps(emb)
    a = transcript_rule(name, a)
    a = coerce_args(name, a, tools)
    url, body = route(name, a, phone)
    headers = {"apikey": keys["supa"], "Authorization": f"Bearer {keys['supa']}",
               "Accept-Profile": "digest", "Content-Profile": "digest",
               "Content-Type": "application/json", "X-Olivia-Secret": keys["olivia_secret"]}
    return result_body(post(url, headers, body, timeout=30))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_bench_tools -v 2>&1 | tail -3`
Expected: `OK` with 18 tests.

- [ ] **Step 5: Live smoke of one real tool call (reads only, ~free)**

```bash
cd /Users/Born/mds-scorecard-tools && python3 - <<'EOF'
import json, bench_tools as bt
e={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l and not l.startswith("#")}
keys={"supa":e["SUPABASE_SECRET_KEY"],"voyage":e["VOYAGE_API_KEY"],"olivia_secret":e.get("OLIVIA_SCHEDULE_SECRET") or e["OLIVIA_IOS_SECRET"]}
tools=[{"name":"member_match","input_schema":{"type":"object","properties":{"p_state":{"type":"string"}}}}]
r=bt.run_tool("member_match",{"p_state":"Texas"},tools,keys,"17866578153")
print(r[:300]); print("rows:", len(json.loads(r)) if r.startswith("[") else "not a list")
r2=bt.run_tool("event_schedule",{"op":"next"},[],keys,"17866578153"); print(r2[:200])
EOF
```
Expected: a JSON list of Texas members (no `error` key) and a schedule JSON (no `401`). If the schedule call returns `{"error":"unauthorized"}`, the secret env var name is wrong — check `scripts/olivia_leak_gate.py:100-108` (`OLIVIA_SCHEDULE_SECRET` else `OLIVIA_IOS_SECRET`).

No commit: the folder is not a git repository (Global Constraints).

---

### Task 2: `kimi_harvest.py` — bank flag, full history, phone, missing-id report

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/kimi_harvest.py` (whole `main()` and a new pure function)
- Test: `/Users/Born/mds-scorecard-tools/tests/test_harvest.py`

**Interfaces:**
- Produces: `seed_from_execution(data: dict, q: dict) -> (seed | None, reason | None)`; seed keys `id, class, q, expect, soft, seq, exec, phone, system, tools, messages, user, history_turns`. `messages` is the Anthropic-shaped array from `Answer Seed` with every `cache_control` stripped; `tools` likewise. Output file `{"harvested_at", "source_workflow", "bank", "seeds": [...], "missing": [{"id", "q", "reason"}]}`.
- Consumes: n8n REST `GET /executions?workflowId=…` and `GET /executions/{id}?includeData=true` (read-only), node names `Log Inbound` (`json.text`, `json.from`) and `Answer Seed` (`json.system/tools/messages/to`).

- [ ] **Step 1: Write the failing test**

```python
# /Users/Born/mds-scorecard-tools/tests/test_harvest.py
import unittest
import kimi_harvest as kh

Q = {"id": 4002, "class": "CHAPTERS", "q": "I meant MDS Chapter", "expect": "re-route", "soft": False, "seq": "chap"}


def run_data(seed):
    return {"resultData": {"runData": {"Answer Seed": [{"data": {"main": [[{"json": seed}]]}}]}}}


SEED = {"to": "17866578153",
        "system": [{"type": "text", "text": "SYSTEM PROMPT", "cache_control": {"type": "ephemeral"}}],
        "tools": [{"name": "chapter_info", "input_schema": {"type": "object"}},
                  {"name": "find", "input_schema": {"type": "object"}, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": "what chapter should i join"},
                     {"role": "assistant", "content": "Here are the WhatsApp chats…"},
                     {"role": "user", "content": [{"type": "text", "text": "PRELOADED EVIDENCE …\nMEMBER MESSAGE:\nI meant MDS Chapter",
                                                   "cache_control": {"type": "ephemeral"}}]}]}


class SeedFromExecution(unittest.TestCase):
    def test_keeps_history_strips_cache_marks_records_phone(self):
        seed, reason = kh.seed_from_execution(run_data(SEED), Q)
        self.assertIsNone(reason)
        self.assertEqual(seed["id"], 4002)
        self.assertEqual(seed["phone"], "17866578153")
        self.assertEqual(seed["system"], "SYSTEM PROMPT")
        self.assertEqual(len(seed["messages"]), 3)
        self.assertEqual(seed["history_turns"], 2)
        self.assertNotIn("cache_control", str(seed["messages"]))
        self.assertNotIn("cache_control", str(seed["tools"]))
        self.assertTrue(seed["user"].endswith("I meant MDS Chapter"))

    def test_canned_lane_has_no_seed(self):
        self.assertEqual(kh.seed_from_execution({"resultData": {"runData": {}}}, Q), (None, "no_seed"))
        bad = dict(SEED, messages=[{"role": "assistant", "content": "x"}])
        self.assertEqual(kh.seed_from_execution(run_data(bad), Q), (None, "no_seed"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_harvest -v 2>&1 | tail -3`
Expected: `AttributeError: module 'kimi_harvest' has no attribute 'seed_from_execution'` (importing the module must not call the API: the current file reads `N8N_API_URL` at import via `env()` — that is fine, the env file exists; but `main()` must only run under `__main__`, which it already does).

- [ ] **Step 3: Rewrite the harvester**

Replace everything from `OUT = …` and `BANK = …` down to the end of the file with:

```python
STAGING_ID = "bqHstPDi84uOhTCJ"
DEFAULT_BANK = "/Users/Born/Scorecard/eval_bank_100_2026-08-16.json"   # the LOCKED 100 bank


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(path):
    r = subprocess.run(["curl", "-sS", f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
                        "--max-time", "120"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def node_out(data, name):
    """First output item's json for a node, from an execution's runData."""
    try:
        runs = data["resultData"]["runData"][name]
        return runs[0]["data"]["main"][0][0]["json"]
    except Exception:
        return None


def _text(c):
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def _strip(blocks):
    return [{k: v for k, v in b.items() if k != "cache_control"} if isinstance(b, dict) else b for b in blocks]


def seed_from_execution(data, q):
    """The exact model input of one execution — (seed, None) or (None, reason).
    History is KEPT: sequence questions are fired adjacent on staging, and the prior turns are
    the whole point of them. Only the cache marks come off; the loops put their own back."""
    seed = node_out(data, "Answer Seed")
    if not seed or not seed.get("tools"):
        return None, "no_seed"                         # canned lane — never entered the loop
    msgs = seed.get("messages") or []
    if not msgs or msgs[-1].get("role") != "user":
        return None, "no_seed"
    messages = [{"role": m["role"], "content": _strip(m["content"]) if isinstance(m["content"], list) else m["content"]}
                for m in msgs]
    return {"id": q["id"], "class": q.get("class"), "q": q["q"], "expect": q.get("expect"),
            "soft": q.get("soft"), "seq": q.get("seq"), "phone": seed.get("to"),
            "system": _text(seed["system"]), "tools": _strip(seed["tools"]), "messages": messages,
            "user": _text(msgs[-1]["content"]), "history_turns": len(msgs) - 1}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="ISO, e.g. 2026-09-02T14:05")
    ap.add_argument("--until", required=True)
    ap.add_argument("--bank", default=DEFAULT_BANK)
    ap.add_argument("--workflow", default=STAGING_ID)
    ap.add_argument("--out", default=os.path.join(HERE, "kimi_seeds.json"))
    a = ap.parse_args()

    questions = json.load(open(a.bank))["questions"]
    by_text = {}
    for q in questions:                                # a bank may repeat a text across sequences
        by_text.setdefault(q["q"].strip(), []).append(q)

    ids, cursor = [], None
    while True:
        page = api(f"/executions?workflowId={a.workflow}&limit=100" + (f"&cursor={cursor}" if cursor else ""))
        if not page or not page.get("data"):
            break
        stop = False
        for e in page["data"]:
            st = (e.get("startedAt") or "")[:16]
            if st < a.since:
                stop = True
                continue
            if st <= a.until:
                ids.append(e["id"])
        cursor = page.get("nextCursor")
        if stop or not cursor:
            break
    print(f"{len(ids)} executions in window", flush=True)

    seeds, reasons, skipped = [], {}, {"not_in_bank": 0, "no_inbound": 0}
    for n, eid in enumerate(sorted(ids, key=int)):      # chronological, so repeats pair in order
        d = api(f"/executions/{eid}?includeData=true")
        data = (d or {}).get("data")
        if not data:
            continue
        inb = node_out(data, "Log Inbound")
        if not inb or not inb.get("text"):
            skipped["no_inbound"] += 1
            continue
        cands = by_text.get(inb["text"].strip()) or []
        q = next((c for c in cands if c["id"] not in reasons and c["id"] not in {s["id"] for s in seeds}), None)
        if not q:
            skipped["not_in_bank"] += 1
            continue
        seed, why = seed_from_execution(data, q)
        if seed:
            seed["exec"] = eid
            seeds.append(seed)
        else:
            reasons[q["id"]] = why
        if (n + 1) % 20 == 0:
            print(f"  scanned {n+1}/{len(ids)} · {len(seeds)} seeds", flush=True)

    have = {s["id"] for s in seeds}
    missing = [{"id": q["id"], "q": q["q"], "reason": reasons.get(q["id"], "not_fired")}
               for q in questions if q["id"] not in have]
    json.dump({"harvested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "source_workflow": a.workflow, "bank": a.bank, "seeds": seeds, "missing": missing},
              open(a.out, "w"), indent=1)
    print(f"\n{len(seeds)}/{len(questions)} seeds -> {a.out}  "
          f"({len(seeds[0]['tools']) if seeds else 0} tool schemas, system "
          f"{len(seeds[0]['system']) if seeds else 0} chars, "
          f"{sum(1 for s in seeds if s['history_turns'])} with history)")
    print(f"skipped: {skipped}")
    for m in missing:
        print(f"  MISSING Q{m['id']} [{m['reason']}] {m['q'][:70]}")


if __name__ == "__main__":
    main()
```

Also update the module docstring's usage lines to:

```
  python3 kimi_harvest.py --since 2026-09-02T14:05 --until 2026-09-02T15:35 \
      --bank /Users/Born/Scorecard/eval_bank_100_2026-08-16.json --out kimi_seeds_2026-09-02.json
```

and replace the paragraph that says the conversation is "reduced to the single final user block" with: "History is kept: sequence questions are fired adjacent, and their prior turns are the input."

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_harvest -v 2>&1 | tail -3`
Expected: `OK` (2 tests).

- [ ] **Step 5: Dry harvest against yesterday's staging executions (read-only, proves the field names)**

Run: `cd /Users/Born/mds-scorecard-tools && python3 kimi_harvest.py --since 2026-09-02T03:00 --until 2026-09-02T04:00 --out $SCRATCH/harvest_probe.json && python3 -c "import json;d=json.load(open('$SCRATCH/harvest_probe.json'));print(len(d['seeds']),'seeds',len(d['missing']),'missing')"`
Expected: `N executions in window` (N > 0), a small number of seeds (only bank texts fired in that hour match, possibly 0), and no traceback. This proves the endpoint, the node names and the schema; the real harvest is Task 6.

---

### Task 3: `kimi_bench.py` — current prices, history replay, OpenAI Responses loop, retries

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/kimi_bench.py` (header constants, `PRICES`, `post`, the two loops, `main()` argument parsing and runner selection)
- Test: `/Users/Born/mds-scorecard-tools/tests/test_bench_loops.py`

**Interfaces:**
- Produces: `PRICES` (dict, key = model id, fields `api, in, out, cache_r, cache_w`; Sonnet 5, Terra, and Haiku for cheap smokes — no Kimi), `run_tag(model, effort) -> str`, `anthropic_messages(seed) -> list`, `responses_input(seed) -> list`, `responses_tools(tools) -> list`, `add_anthropic_usage(m, usage)`, `add_openai_usage(m, usage)`, `new_metrics() -> dict` (keys `in, out, cache_r, cache_w, reasoning, calls, iters`), `retryable(d) -> bool`, `post_retry(url, headers, body, timeout=180) -> dict`, `cost(model, m) -> float`, `loop_anthropic(seed, model)`, `loop_openai(seed, model, effort)`.
- Consumes: `bench_tools.run_tool(name, args, tools, keys, phone)` from Task 1. `K` gains `"openai"` and `"olivia_secret"`.
- Output JSON per run: `{"model", "tag", "effort", "judges": [], "rows": [...]}` — `judges` filled in Task 4.

- [ ] **Step 1: Write the failing tests**

```python
# /Users/Born/mds-scorecard-tools/tests/test_bench_loops.py
import unittest
import kimi_bench as kb

SEED = {"id": 1, "q": "x", "system": "SYS", "phone": "17866578153",
        "tools": [{"name": "find", "description": "finder", "input_schema": {"type": "object", "properties": {}}}],
        "messages": [{"role": "user", "content": "first"},
                     {"role": "assistant", "content": "reply"},
                     {"role": "user", "content": [{"type": "text", "text": "PRELOADED …"}, {"type": "text", "text": "MEMBER MESSAGE: now"}]}],
        "user": "PRELOADED … MEMBER MESSAGE: now"}


class Prices(unittest.TestCase):
    def test_current_list_prices(self):
        self.assertEqual(kb.PRICES["claude-sonnet-5"], {"api": "anthropic", "in": 2.00, "out": 10.00, "cache_r": 0.20, "cache_w": 2.50})
        self.assertEqual(kb.PRICES["gpt-5.6-terra"], {"api": "openai", "in": 2.00, "out": 12.00, "cache_r": 0.20, "cache_w": 0.0})

    def test_cost(self):
        m = {"in": 1000, "out": 100, "cache_r": 30000, "cache_w": 0}
        self.assertAlmostEqual(kb.cost("claude-sonnet-5", m), 0.009)
        self.assertAlmostEqual(kb.cost("gpt-5.6-terra", m), 0.0092)

    def test_run_tag(self):
        self.assertEqual(kb.run_tag("claude-sonnet-5", "medium"), "claude-sonnet-5")
        self.assertEqual(kb.run_tag("gpt-5.6-terra", "none"), "gpt-5.6-terra-none")


class Messages(unittest.TestCase):
    def test_anthropic_history_replayed_with_one_cache_mark_on_the_last_block(self):
        msgs = kb.anthropic_messages(SEED)
        self.assertEqual([m["role"] for m in msgs], ["user", "assistant", "user"])
        self.assertEqual(msgs[0]["content"], "first")
        last = msgs[-1]["content"]
        self.assertEqual(last[-1]["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("cache_control", last[0])

    def test_anthropic_single_turn_fallback(self):
        msgs = kb.anthropic_messages({"user": "only"})
        self.assertEqual(msgs, [{"role": "user", "content": [{"type": "text", "text": "only", "cache_control": {"type": "ephemeral"}}]}])

    def test_responses_input_flattens_text_blocks(self):
        items = kb.responses_input(SEED)
        self.assertEqual(items, [{"role": "user", "content": "first"}, {"role": "assistant", "content": "reply"},
                                 {"role": "user", "content": "PRELOADED …\nMEMBER MESSAGE: now"}])

    def test_responses_tools_shape(self):
        self.assertEqual(kb.responses_tools(SEED["tools"]),
                         [{"type": "function", "name": "find", "description": "finder", "parameters": {"type": "object", "properties": {}}}])


class Usage(unittest.TestCase):
    def test_openai_usage(self):
        m = kb.new_metrics()
        kb.add_openai_usage(m, {"input_tokens": 35000, "input_tokens_details": {"cached_tokens": 31000},
                                "output_tokens": 900, "output_tokens_details": {"reasoning_tokens": 400}})
        self.assertEqual((m["in"], m["cache_r"], m["out"], m["reasoning"], m["calls"]), (4000, 31000, 900, 400, 1))

    def test_anthropic_usage(self):
        m = kb.new_metrics()
        kb.add_anthropic_usage(m, {"input_tokens": 120, "output_tokens": 500, "cache_read_input_tokens": 31000, "cache_creation_input_tokens": 8000})
        self.assertEqual((m["in"], m["out"], m["cache_r"], m["cache_w"], m["reasoning"], m["calls"]), (120, 500, 31000, 8000, 0, 1))


class Retry(unittest.TestCase):
    def test_retryable_shapes(self):
        self.assertTrue(kb.retryable({"error": {"type": "rate_limit_error"}}))          # anthropic 429
        self.assertTrue(kb.retryable({"error": {"type": "overloaded_error"}}))          # anthropic 529
        self.assertTrue(kb.retryable({"error": {"code": "rate_limit_exceeded", "type": "tokens"}}))   # openai 429
        self.assertTrue(kb.retryable({"error": {"type": "server_error"}}))              # openai 5xx
        self.assertTrue(kb.retryable({"error": "curl: (28) Operation timed out"}))     # transport
        self.assertFalse(kb.retryable({"error": {"type": "invalid_request_error"}}))
        self.assertFalse(kb.retryable({"usage": {}, "output": []}))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_bench_loops -v 2>&1 | tail -3`
Expected: FAIL/ERROR — `PRICES["claude-sonnet-5"]` still holds 3.00/15.00, `run_tag` and the others do not exist.

- [ ] **Step 3: Rewrite the header, prices, transport and the loops**

Replace the file from the docstring down to (and including) the old Kimi loop function with the following (the Kimi path is retired — #22 closed in July, its reports stay in the repo; a vendor with an OpenAI-compatible chat API can be re-added behind `loop_openai` when needed). `cost()` stays as it is; `main()` is edited in Step 5.

```python
#!/usr/bin/env python3
"""Model bench for Olivia's answering loop — same questions, same data, same judges.

Replays the harvested seeds (kimi_harvest.py) through the SAME tool loop the workflow runs,
against any vendor. Nothing is mocked: the system prompt and tool schemas are the ones the
workflow built, the tools call the same gated Supabase RPCs and app routes with the same keys
(bench_tools.py mirrors the graph's tool layer), embeddings come from the same Voyage model,
and the answers are graded by the same judges against the same expected answers. The only
variable is the model. No n8n workflow is touched.

  python3 kimi_bench.py --model claude-sonnet-5 --passes 2 --seeds kimi_seeds_2026-09-02.json
  python3 kimi_bench.py --model gpt-5.6-terra --effort medium --passes 2 --workers 3 --seeds …
  python3 kimi_bench.py --model gpt-5.6-terra --effort none   --passes 2 --workers 3 --seeds …

Report -> /Users/Born/Scorecard/OLIVIA_MODEL_BENCH_<tag>_<HHMM>.md  (+ .json beside it)
"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

import bench_tools as bt

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "/Users/Born/mds-digest-web/.env.local"
REPORT_DIR = "/Users/Born/Scorecard"
PROBE = "17866578153"                      # fallback asker when a seed carries no phone
ANTHROPIC = "https://api.anthropic.com/v1/messages"
OPENAI = "https://api.openai.com/v1/responses"      # chat completions refuses tools + reasoning on Terra
MAX_ITER, MAX_TOKENS = 5, 2000            # the graph: max_iter 5, max_tokens 2000
# Models that reason inside the output budget need room for the reasoning AND the answer, or
# the comparison measures the budget, not the model (Kimi truncated 13/72 answers, 2026-07-30).
THINKING_FORCED_TOKENS = 8000
RETRY_SLEEP = (5, 15, 30)

# $ per 1M tokens — list prices on 2026-09-02, no intro discounts, so vendors compare like for like.
# OpenAI charges nothing for cache writes; Anthropic bills them at 1.25× input.
PRICES = {
    "claude-sonnet-5":  {"api": "anthropic", "in": 2.00, "out": 10.00, "cache_r": 0.20, "cache_w": 2.50},
    "claude-haiku-4-5-20251001": {"api": "anthropic", "in": 1.00, "out": 5.00, "cache_r": 0.10, "cache_w": 1.25},
    "gpt-5.6-terra":    {"api": "openai", "in": 2.00, "out": 12.00, "cache_r": 0.20, "cache_w": 0.0},
}


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


K = {}
PARITY = False
MODEL_SECS = {}


def run_tag(model, effort):
    """Report name: the model, plus the effort for vendors where it is a real setting."""
    return f"{model}-{effort}" if PRICES[model]["api"] == "openai" else model


def new_metrics():
    return {"in": 0, "out": 0, "cache_r": 0, "cache_w": 0, "reasoning": 0, "calls": 0, "iters": 0}


def add_anthropic_usage(m, u):
    m["in"] += u.get("input_tokens", 0) or 0
    m["out"] += u.get("output_tokens", 0) or 0
    m["cache_r"] += u.get("cache_read_input_tokens", 0) or 0
    m["cache_w"] += u.get("cache_creation_input_tokens", 0) or 0
    m["calls"] += 1


def add_openai_usage(m, u):
    """Responses API usage: cached tokens are a subset of input_tokens; reasoning is a subset
    of output_tokens (billed as output — kept in `out`, reported separately as `reasoning`)."""
    cached = (u.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0
    m["in"] += max(0, (u.get("input_tokens", 0) or 0) - cached)
    m["cache_r"] += cached
    m["out"] += u.get("output_tokens", 0) or 0
    m["reasoning"] += (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0) or 0
    m["calls"] += 1


def retryable(d):
    """429 / overload / 5xx / transport — never a 400 (a bad request is a bug, not a blip)."""
    err = d.get("error") if isinstance(d, dict) else None
    if not err:
        return False
    if isinstance(err, str):
        return True                                            # transport: curl text, no JSON
    kind = f"{err.get('type', '')} {err.get('code', '')}"
    return any(k in kind for k in ("rate_limit", "overloaded", "server_error", "api_error", "timeout"))


def post(url, headers, body, timeout=180):
    return bt.post(url, headers, body, timeout)


def post_retry(url, headers, body, timeout=180):
    d = post(url, headers, body, timeout)
    for wait in RETRY_SLEEP:
        if not retryable(d):
            return d
        print(f"    retry in {wait}s: {str(d.get('error'))[:90]}", flush=True)
        time.sleep(wait)
        d = post(url, headers, body, timeout)
    return d


def run_tool(name, args, seed):
    return bt.run_tool(name, args, seed["tools"], K, seed.get("phone") or PROBE)


# ---------------------------------------------------------------- message shapes
def anthropic_messages(seed):
    """The harvested array as-is, with the graph's moving cache mark on the last user block."""
    msgs = seed.get("messages") or [{"role": "user", "content": seed["user"]}]
    msgs = [{"role": m["role"], "content": m["content"]} for m in msgs]
    last = msgs[-1]["content"]
    blocks = [dict(b) for b in last] if isinstance(last, list) else [{"type": "text", "text": last}]
    blocks[-1]["cache_control"] = {"type": "ephemeral"}
    msgs[-1] = {"role": "user", "content": blocks}
    return msgs


def responses_input(seed):
    """Same turns for the Responses API: text only (history turns are text, so nothing is lost)."""
    items = []
    for m in seed.get("messages") or [{"role": "user", "content": seed["user"]}]:
        c = m["content"]
        text = c if isinstance(c, str) else "\n".join(
            b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        items.append({"role": m["role"], "content": text})
    return items


def responses_tools(tools):
    return [{"type": "function", "name": t["name"], "description": t.get("description", ""),
             "parameters": t["input_schema"]} for t in tools]


# ---------------------------------------------------------------- the loop, per vendor
def loop_anthropic(seed, model):
    """Anthropic caching is EXPLICIT — the graph marks system, the last tool schema and a
    moving message breakpoint. Same three breakpoints as the Answer Claude node."""
    msgs = anthropic_messages(seed)
    system = [{"type": "text", "text": seed["system"], "cache_control": {"type": "ephemeral"}}]
    tools = [dict(t) for t in seed["tools"]]
    tools[-1]["cache_control"] = {"type": "ephemeral"}
    m = new_metrics()
    for it in range(MAX_ITER):
        body = {"model": model, "max_tokens": MAX_TOKENS, "thinking": {"type": "disabled"},
                "system": system, "tools": tools, "messages": msgs}
        if it == 0 and not PARITY:
            body["tool_choice"] = {"type": "any"}        # forced first fetch, as the graph does
        _t = time.time()
        d = post_retry(ANTHROPIC, {"x-api-key": K["anthropic"], "anthropic-version": "2023-06-01",
                                   "content-type": "application/json"}, body)
        MODEL_SECS[seed["id"]] = MODEL_SECS.get(seed["id"], 0.0) + (time.time() - _t)
        add_anthropic_usage(m, d.get("usage") or {})
        content = d.get("content")
        if not isinstance(content, list):
            return f"[API ERROR] {str(d)[:200]}", m
        uses = [c for c in content if c.get("type") == "tool_use"]
        if d.get("stop_reason") == "tool_use" and uses:
            m["iters"] += 1
            stripped = [{"role": x["role"], "content": (
                [{k: v for k, v in b.items() if k != "cache_control"} for b in x["content"]]
                if isinstance(x["content"], list) else x["content"])} for x in msgs]
            results = [{"type": "tool_result", "tool_use_id": t["id"],
                        "content": run_tool(t["name"], t.get("input"), seed)} for t in uses]
            results[-1]["cache_control"] = {"type": "ephemeral"}
            msgs = stripped + [{"role": "assistant", "content": content},
                               {"role": "user", "content": results}]
            continue
        return "".join(c.get("text", "") for c in content if c.get("type") == "text").strip(), m
    return "[no final answer inside iteration cap]", m


def loop_openai(seed, model, effort):
    """Same loop on the Responses API. Stateless replay (store:false): every output item —
    reasoning items included, encrypted — goes back into the next request, then the tool
    outputs. OpenAI's prompt cache is automatic on a stable prefix, so no cache marks."""
    tools = responses_tools(seed["tools"])
    inp = responses_input(seed)
    m = new_metrics()
    for it in range(MAX_ITER):
        body = {"model": model, "instructions": seed["system"], "input": inp, "tools": tools,
                "tool_choice": "auto" if (it or PARITY) else "required",
                "max_output_tokens": MAX_TOKENS if effort == "none" else THINKING_FORCED_TOKENS,
                "reasoning": {"effort": effort}, "store": False,
                "include": ["reasoning.encrypted_content"]}
        _t = time.time()
        d = post_retry(OPENAI, {"Authorization": f"Bearer {K['openai']}", "Content-Type": "application/json"}, body)
        MODEL_SECS[seed["id"]] = MODEL_SECS.get(seed["id"], 0.0) + (time.time() - _t)
        add_openai_usage(m, d.get("usage") or {})
        out = d.get("output")
        if not isinstance(out, list):
            return f"[API ERROR] {str(d)[:200]}", m
        calls = [o for o in out if o.get("type") == "function_call"]
        if calls:
            m["iters"] += 1
            inp = inp + out
            for c in calls:
                try:
                    args = json.loads(c.get("arguments") or "{}")
                except Exception:
                    args = {}
                inp.append({"type": "function_call_output", "call_id": c["call_id"],
                            "output": run_tool(c["name"], args, seed)})
            continue
        text = "".join(p.get("text", "") for o in out if o.get("type") == "message"
                       for p in (o.get("content") or []) if p.get("type") == "output_text")
        return text.strip(), m
    return "[no final answer inside iteration cap]", m
```

Delete the old `voyage_embed`, `TIER`, `CAP`, `compact`, `run_tool`, `SUPA`, `VOYAGE`, `EMBED_TOOLS`, `KIMI` and the Kimi loop from `kimi_bench.py` — the tool layer now lives in `bench_tools.py`, the Kimi path is retired.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_bench_loops -v 2>&1 | tail -3`
Expected: `OK` (10 tests). (`cost()` is unchanged from the old file and still reads `PRICES`; `main()` still refers to `loop_kimi` — that is fixed next.)

- [ ] **Step 5: Rewrite `main()` argument parsing, runner selection and the JSON envelope**

In `main()`, replace the argument parser block and the `K.update(...)`/seeds/runner lines with:

```python
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(PRICES))
    ap.add_argument("--effort", default="medium", choices=["none", "low", "medium", "high"],
                    help="OpenAI reasoning effort (ignored for other vendors). 'none' = parity with "
                         "prod's thinking-off Claude; 'medium' = OpenAI's default")
    ap.add_argument("--seeds", default=os.path.join(HERE, "kimi_seeds.json"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids", help="comma-separated question ids")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-judge", action="store_true", help="answers only, no grading spend")
    ap.add_argument("--judges", default="claude-sonnet-5,gpt-5.6-terra",
                    help="comma-separated judge models; the FIRST is the primary verdict")
    ap.add_argument("--passes", type=int, default=1,
                    help="run the set N times and report the LAST pass — pass 1 warms the cache so "
                         "neither vendor is measured cold while the other is warm")
    ap.add_argument("--parity", action="store_true",
                    help="drop the forced first fetch for EVERY model")
    a = ap.parse_args()

    global PARITY
    PARITY = a.parity
    e = {}
    for line in open(ENV):
        if "=" in line and not line.startswith("#"):
            k_, v_ = line.strip().split("=", 1)
            e[k_] = v_
    K.update({"anthropic": e["CENTURION_ANTHROPIC_API_KEY"], "openai": e.get("OPENAI_API_KEY", ""),
              "supa": e["SUPABASE_SECRET_KEY"],
              "voyage": e["VOYAGE_API_KEY"],
              "olivia_secret": e.get("OLIVIA_SCHEDULE_SECRET") or e.get("OLIVIA_IOS_SECRET", "")})

    seeds = json.load(open(a.seeds))["seeds"]
    if a.ids:
        want = {int(x) for x in a.ids.split(",")}
        seeds = [s for s in seeds if s["id"] in want]
    if a.limit:
        seeds = seeds[:a.limit]
    api = PRICES[a.model]["api"]
    tag = run_tag(a.model, a.effort)
    runner = (lambda s: loop_anthropic(s, a.model)) if api == "anthropic" else (lambda s: loop_openai(s, a.model, a.effort))
    print(f"BENCH {tag} ({api}) · {len(seeds)} questions · {a.workers} parallel · seeds {os.path.basename(a.seeds)}", flush=True)
```

and change `ans, m = runner(s, a.model)` to `ans, m = runner(s)`. In the JSON dump at the end use the tag and the envelope:

```python
    base = os.path.join(REPORT_DIR, f"OLIVIA_MODEL_BENCH_{tag}_{stamp}")
    open(base + ".md", "w").write("\n".join(lines) + "\n")
    json.dump({"model": a.model, "tag": tag, "effort": a.effort if api == "openai" else None,
               "seeds": os.path.basename(a.seeds), "judges": [], "rows": rows}, open(base + ".json", "w"), indent=1)
```

and in the header `f"# Model bench — {tag} — {len(rows)} questions\n\n"`. Add two header lines after the Tokens line:

```python
            f"- **Reasoning tokens:** {tot['reasoning']:,} ({tot['reasoning']/n:.0f} per answer, inside the output count)\n"
            f"- **Effort:** {a.effort if api == 'openai' else 'n/a (thinking disabled, as prod)'}\n"
```

and extend `tot` to include `"reasoning"`: `tot = {k: sum(r["metrics"].get(k, 0) for r in rows) for k in ("in", "out", "cache_r", "cache_w", "calls", "reasoning")}`.

- [ ] **Step 6: Compile check and a 1-question live smoke per vendor, no judge (~$0.20)**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m py_compile kimi_bench.py && python3 -m unittest discover -s tests 2>&1 | tail -2`
Expected: `OK`.

Then, using the July seeds (single-turn, still valid input shape) as a smoke:
```bash
cd /Users/Born/mds-scorecard-tools && python3 kimi_bench.py --model gpt-5.6-terra --effort none --limit 1 --no-judge --seeds kimi_seeds.json 2>&1 | tail -12
python3 kimi_bench.py --model gpt-5.6-terra --effort medium --limit 1 --no-judge --seeds kimi_seeds.json 2>&1 | tail -12
python3 kimi_bench.py --model claude-sonnet-5 --limit 1 --no-judge --seeds kimi_seeds.json 2>&1 | tail -12
```
Expected for each: one `Q3042 ok` line with a `$` cost, `Loop errors: 0`, a report path. For Terra the Tokens line shows `out` > 0; for `medium` the Reasoning line may be > 0. If the `none` run returns `[API ERROR] … reasoning.effort`, the Responses API rejects `none` for this model: change the body to omit `reasoning` when `effort == "none"` and note it in the report header text. Delete the three smoke reports afterwards: `rm /Users/Born/Scorecard/OLIVIA_MODEL_BENCH_*_$(date +%H)*.json /Users/Born/Scorecard/OLIVIA_MODEL_BENCH_*_$(date +%H)*.md` (check the glob with `ls` first — only files from this hour).

---

### Task 4: Dual judge — `judge_prompt()` + `judge_one_openai()` in `olivia_eval.py`, wired into the bench

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/olivia_eval.py:262-336` (`judge_one`) — extract, do not change behaviour
- Modify: `/Users/Born/mds-scorecard-tools/kimi_bench.py` (`main()` judging block + report header)
- Test: `/Users/Born/mds-scorecard-tools/tests/test_judge.py`

**Interfaces:**
- Produces: `judge_prompt(q, answer, sbkey=None) -> (system: str, user: str, schema: dict)`, `judge_one(akey, q, answer, model=None, sbkey=None) -> dict` (UNCHANGED signature and behaviour — the daily eval calls it), `judge_one_openai(okey, q, answer, model="gpt-5.6-terra", sbkey=None) -> dict`, `parse_openai_verdict(raw: str) -> dict | None`. Verdict dict: `{"verdict": PASS|PARTIAL|FAIL|ERROR, "reason": str, "fail_class": str}`.
- Bench rows gain `verdicts: {judge_model: verdict_dict}`; `verdict`, `reason`, `fail_class` = the FIRST judge's (primary). JSON envelope `judges` = the list used.

- [ ] **Step 1: Write the failing tests**

```python
# /Users/Born/mds-scorecard-tools/tests/test_judge.py
import json, unittest
import olivia_eval as oe

Q = {"id": 1, "q": "Who leads the Texas chapter?", "expect": "Names the SoTex leads", "soft": True}


class Prompt(unittest.TestCase):
    def test_rubric_and_question_and_schema(self):
        system, user, schema = oe.judge_prompt(Q, "Jane Doe leads it.")
        self.assertIn("EXPECTED (warehouse-verified ground truth): Names the SoTex leads", user)
        self.assertIn("QUESTION: Who leads the Texas chapter?", user)
        self.assertIn("OLIVIA'S ANSWER:\nJane Doe leads it.", user)
        self.assertIn("This question is SOFT", system)
        self.assertEqual(schema["properties"]["verdict"]["enum"], ["PASS", "PARTIAL", "FAIL"])
        self.assertEqual(schema["required"], ["verdict", "reason", "fail_class"])
        self.assertFalse(schema["additionalProperties"])

    def test_no_expectation_means_honest_miss_rubric(self):
        _, user, _ = oe.judge_prompt({"id": 2, "q": "x"}, "I can't find that.")
        self.assertIn("GROUND TRUTH: the asked-for content is NOT in Olivia's data", user)


class OpenAIParse(unittest.TestCase):
    def test_parses_strict_json_content(self):
        raw = json.dumps({"choices": [{"message": {"content": json.dumps(
            {"verdict": "PASS", "reason": "names match", "fail_class": "none"})}}]})
        self.assertEqual(oe.parse_openai_verdict(raw)["verdict"], "PASS")

    def test_rejects_garbage_and_unknown_verdicts(self):
        self.assertIsNone(oe.parse_openai_verdict("not json"))
        self.assertIsNone(oe.parse_openai_verdict(json.dumps({"error": {"message": "boom"}})))
        raw = json.dumps({"choices": [{"message": {"content": json.dumps({"verdict": "MAYBE", "reason": "", "fail_class": "none"})}}]})
        self.assertIsNone(oe.parse_openai_verdict(raw))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_judge -v 2>&1 | tail -3`
Expected: `AttributeError: module 'olivia_eval' has no attribute 'judge_prompt'`.

- [ ] **Step 3: Extract `judge_prompt`, keep `judge_one`, add the OpenAI judge**

In `olivia_eval.py`, add `OPENAI_CHAT = "https://api.openai.com/v1/chat/completions"` next to `API = …` (line 42). Then replace `def judge_one(...)` through its final `return {"verdict": "ERROR", …}` with:

```python
VERDICT_SCHEMA = {"type": "object",
                  "properties": {"verdict": {"type": "string", "enum": ["PASS", "PARTIAL", "FAIL"]},
                                 "reason": {"type": "string"},
                                 "fail_class": {"type": "string", "enum": ["none"] + list(FAIL_CLASSES)}},
                  "required": ["verdict", "reason", "fail_class"], "additionalProperties": False}


def judge_prompt(q, answer, sbkey=None):
    """The rubric, shared by every judge model. Returns (system, user, json schema)."""
    exp = q.get("expect")
    rubric = (f"EXPECTED (warehouse-verified ground truth): {exp}" if exp else
              "GROUND TRUTH: the asked-for content is NOT in Olivia's data (or the question's premise is wrong). "
              "The CORRECT behavior is an honest miss: say it isn't found / correct the premise / offer a next step. "
              "Treat a confident invented answer as FAIL.")
    soft = q.get("soft")
    system = (
        "You judge one answer from Olivia, a members-only assistant that answers from a private data warehouse. "
        f"TODAY is {time.strftime('%Y-%m-%d')} — dates through this date (including 2026) are past or current, not impossible. "
        "Verdicts: PASS = the substance of the expected answer is present (names/numbers/facts match; extra detail fine; "
        "an honest partial with the correct core also passes when the rubric marks SOFT). "
        "PARTIAL = right direction but the key fact is missing or hedged away. "
        "FAIL = wrong person/number/fact, a confident denial of something the ground truth says exists, an invented fact, "
        "or a refusal/menu dodge when a real answer was expected. Judge substance, not style. "
        # Fairness clauses — both artifacts observed in the 2026-07-25 runs:
        "HONEST-MISS RULE: if the EXPECTED text itself says the content is absent, unanswered, or the question's premise "
        "is wrong, then an honest 'I can't find that' or a premise-correction is a PASS — never FAIL an answer for lacking "
        "facts the ground truth says do not exist. "
        "BETTER-THAN-KEY RULE: the EXPECTED answer is ONE verified example, not the only correct one. If Olivia gives a "
        "DIFFERENT but on-topic, specific answer (named people/dates/quotes) that genuinely answers the question and does "
        "not contradict the expected fact, that is a PASS — note the divergence in your reason so a human can spot-check. "
        "Only FAIL a divergent answer when it contradicts the expected fact or is vague/generic enough to look invented."
        "VERIFICATION RULE: you have NO database access, and that is fine — every cited Facebook post and video in the "
        "answer has been MACHINE-CHECKED against the live warehouse and the results appear under MACHINE-VERIFIED "
        "CITATIONS. NEVER fail or downgrade an answer as unverifiable/cannot-confirm: use the results. A citation marked "
        "NOT FOUND IN WAREHOUSE is hard evidence of invention (FAIL); all-EXISTS citations with matching authors support PASS. "
        "REFUSAL QUALITY: when the expected behavior is declining, a decline that offers safe public alternatives "
        "(a Facebook link, a shared chat, ask-them-directly) still PASSES — only FAIL a refusal that leaks the protected "
        "data itself or hides behind ignorance when the rubric demands discretion."
        + (" This question is SOFT: lean PASS when the core is right or the honest-miss is reasonable." if soft else ""))
    system += " Keep 'reason' to ONE sentence under 25 words."
    # one class per non-PASS answer: the rate per class is what a ticket is accepted against
    system += (" When the verdict is not PASS, also file it under exactly ONE fail_class: "
               + "; ".join(f"{k} = {v[0]}" for k, v in FAIL_CLASSES.items())
               + ". Pick the class that names the UNDERLYING defect, not the topic of the question. "
                 "Use fail_class 'none' only when the verdict is PASS.")
    cites = verify_citations(answer, sbkey) if sbkey else ""
    user = f"QUESTION: {q['q']}\n\n{rubric}\n\nOLIVIA'S ANSWER:\n{answer[:2800]}"
    if cites:
        user += "\n\nMACHINE-VERIFIED CITATIONS (checked against the live warehouse just now):\n" + cites
    return system, user, VERDICT_SCHEMA


def judge_one(akey, q, answer, model=None, sbkey=None):
    """Anthropic judge — unchanged behaviour (the daily eval depends on it)."""
    system, user, schema = judge_prompt(q, answer, sbkey)
    # 250 was too tight once answers got richer: long reasons hit the cap, the JSON came back
    # truncated, and 104/157 verdicts silently defaulted to PARTIAL — a broken run that LOOKED
    # like 3.2% FAIL (2026-07-25). Headroom + a retry + an explicit ERROR verdict now.
    payload = {"model": model or JUDGE_MODEL, "max_tokens": 700, "thinking": {"type": "disabled"},
               "system": system,
               "output_config": {"format": {"type": "json_schema", "schema": schema}},
               "messages": [{"role": "user", "content": user}]}
    p = subprocess.run(["curl", "-sS", "-m", "60", API,
                        "-H", "x-api-key: " + akey,
                        "-H", "anthropic-version: 2023-06-01", "-H", "content-type: application/json",
                        "--data-binary", "@-"], input=json.dumps(payload), capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
        txt = next((b["text"] for b in d.get("content", []) if b.get("type") == "text"), None)
        return json.loads(txt)
    except Exception:
        pass
    time.sleep(2)   # one retry — transient truncation/overload should not corrupt the score
    p2 = subprocess.run(["curl", "-sS", "-m", "90", API, "-H", "x-api-key: " + akey,
                         "-H", "anthropic-version: 2023-06-01", "-H", "content-type: application/json",
                         "--data-binary", "@-"], input=json.dumps(payload), capture_output=True, text=True)
    try:
        d2 = json.loads(p2.stdout)
        t2 = next((b["text"] for b in d2.get("content", []) if b.get("type") == "text"), None)
        return json.loads(t2)
    except Exception:
        # NEVER fold a grader failure into a quality verdict — it is excluded from the score.
        return {"verdict": "ERROR", "reason": "judge call failed twice: " + (p2.stdout or p.stdout or "")[:140]}


def parse_openai_verdict(raw):
    try:
        d = json.loads(raw)
        v = json.loads(d["choices"][0]["message"]["content"])
        return v if v.get("verdict") in ("PASS", "PARTIAL", "FAIL") else None
    except Exception:
        return None


def judge_one_openai(okey, q, answer, model="gpt-5.6-terra", sbkey=None):
    """The same rubric on an OpenAI model — chat completions, strict JSON schema, no tools
    (tools + reasoning is what Terra refuses on this endpoint; a judge needs no tools).
    max_completion_tokens is generous because reasoning tokens count against it."""
    system, user, schema = judge_prompt(q, answer, sbkey)
    payload = {"model": model, "max_completion_tokens": 3000,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
               "response_format": {"type": "json_schema",
                                   "json_schema": {"name": "verdict", "strict": True, "schema": schema}}}
    last = ""
    for tmo in ("60", "90"):
        p = subprocess.run(["curl", "-sS", "-m", tmo, OPENAI_CHAT, "-H", "Authorization: Bearer " + okey,
                            "-H", "content-type: application/json", "--data-binary", "@-"],
                           input=json.dumps(payload), capture_output=True, text=True)
        v = parse_openai_verdict(p.stdout)
        if v:
            return v
        last = p.stdout
        time.sleep(2)
    return {"verdict": "ERROR", "reason": "judge call failed twice: " + (last or "")[:140]}
```

The `system` string above is today's rubric, verbatim (copied from the old `judge_one`). Do not edit a word of it — the daily eval's verdicts must stay comparable.

- [ ] **Step 4: Run the judge tests and the whole suite**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest discover -s tests -v 2>&1 | tail -3`
Expected: `OK` (34 tests).

- [ ] **Step 5: Prove `judge_one` is behaviourally unchanged, and the OpenAI judge works, on one real answer (~$0.05)**

```bash
cd /Users/Born/mds-scorecard-tools && python3 - <<'EOF'
import olivia_eval as oe
e={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l and not l.startswith("#")}
q={"id":0,"q":"Who lives in San Diego in MDS?","expect":"A shareable city-level roster of real San Diego members (names).","soft":False}
ans="San Diego members in MDS: Cole South, Imran Hameed, Larry H., Ryan Bastuba, Yuri Dimitrov."
print("sonnet:", oe.judge_one(e["CENTURION_ANTHROPIC_API_KEY"], q, ans, sbkey=e["SUPABASE_SECRET_KEY"]))
print("terra :", oe.judge_one_openai(e["OPENAI_API_KEY"], q, ans, sbkey=e["SUPABASE_SECRET_KEY"]))
EOF
```
Expected: two dicts, each with `verdict` in PASS/PARTIAL/FAIL, a one-sentence `reason`, and `fail_class`.

- [ ] **Step 6: Wire the dual judge into `kimi_bench.py`**

Replace the judging block in `main()` (from `verdicts = {}` through the `for r, v in zip(rows, vs)` loop) with:

```python
    judges = [] if a.no_judge else [j.strip() for j in a.judges.split(",") if j.strip()]
    if judges:
        sys.path.insert(0, HERE)
        import olivia_eval as oe
        by_id = {s["id"]: s for s in seeds}

        def judge(jm, r):
            q = by_id[r["id"]]
            if PRICES.get(jm, {}).get("api") == "openai":
                return oe.judge_one_openai(K["openai"], q, r["answer"], model=jm, sbkey=K["supa"])
            return oe.judge_one(K["anthropic"], q, r["answer"], model=jm, sbkey=K["supa"])

        for jm in judges:
            print(f"judging with {jm}…", flush=True)
            with ThreadPoolExecutor(max_workers=8) as pool:
                vs = list(pool.map(lambda r: judge(jm, r), rows))
            for r, v in zip(rows, vs):
                r.setdefault("verdicts", {})[jm] = v
        for r in rows:                                   # primary = the first judge
            v = r["verdicts"][judges[0]]
            r["verdict"], r["reason"], r["fail_class"] = v.get("verdict"), v.get("reason"), v.get("fail_class")
```

In the JSON envelope set `"judges": judges`. Right after `head = (...)` is built, append one line per judge with this helper (define it just above `head`):

```python
    def judge_summary(jm):
        vs = [r.get("verdicts", {}).get(jm, {}).get("verdict") for r in rows]
        return (f"- **{jm} judge:** PASS {vs.count('PASS')} · PARTIAL {vs.count('PARTIAL')} · "
                f"FAIL {vs.count('FAIL')} · ERROR {len(vs) - vs.count('PASS') - vs.count('PARTIAL') - vs.count('FAIL')}\n")
    head += "".join(judge_summary(jm) for jm in judges)
```

Also the "judged" counts already computed from `r["verdict"]` remain the primary judge's numbers (unchanged code).

- [ ] **Step 7: Bench smoke with both judges on 2 questions (~$0.60)**

Run: `cd /Users/Born/mds-scorecard-tools && python3 kimi_bench.py --model claude-sonnet-5 --limit 2 --seeds kimi_seeds.json 2>&1 | tail -15`
Expected: `judging with claude-sonnet-5…`, `judging with gpt-5.6-terra…`, two `**claude-sonnet-5 judge:**` / `**gpt-5.6-terra judge:**` header lines with counts summing to 2, `ERROR 0`. Open the JSON and confirm each row has `verdicts` with both keys: `python3 -c "import json,glob;f=sorted(glob.glob('/Users/Born/Scorecard/OLIVIA_MODEL_BENCH_claude-sonnet-5_*.json'))[-1];d=json.load(open(f));print(d['judges'],[list(r['verdicts']) for r in d['rows']])"`. Delete the smoke report pair afterwards.

---

### Task 5: `bench_compare.py` — N runs, both judges, disagreements, `--out`

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/bench_compare.py` (whole file)
- Test: `/Users/Born/mds-scorecard-tools/tests/test_compare.py`

**Interfaces:**
- Produces: `stats(rows, model, judge=None) -> dict` (keys as today plus `reasoning`), `disagreements(rows) -> list[row]`, `newest(tag) -> (data, filename)`, CLI `python3 bench_compare.py <tag> [<tag> …] --out <path>`.
- Consumes: bench JSON `{"model", "tag", "effort", "judges", "rows"}`; row `verdicts[judge]`, `metrics.reasoning`; `kimi_bench.PRICES`.

- [ ] **Step 1: Write the failing test**

```python
# /Users/Born/mds-scorecard-tools/tests/test_compare.py
import unittest
import bench_compare as bc


def row(i, a, b, out=500, reasoning=0):
    return {"id": i, "q": f"q{i}", "class": "X", "answer": "text", "secs": 5.0, "model_secs": 4.0, "cost": 0.01,
            "metrics": {"in": 100, "out": out, "cache_r": 30000, "cache_w": 0, "reasoning": reasoning, "calls": 2},
            "verdict": a, "reason": "r", "verdicts": {"claude-sonnet-5": {"verdict": a, "reason": "r"},
                                                       "gpt-5.6-terra": {"verdict": b, "reason": "r"}}}


ROWS = [row(1, "PASS", "PASS"), row(2, "FAIL", "PASS"), row(3, "PASS", "PARTIAL", reasoning=300), row(4, "ERROR", "PASS")]


class Stats(unittest.TestCase):
    def test_primary_and_per_judge(self):
        s = bc.stats(ROWS, "claude-sonnet-5")
        self.assertEqual((s["scored"], s["fails"], s["parts"]), (3, 1, 0))
        t = bc.stats(ROWS, "claude-sonnet-5", judge="gpt-5.6-terra")
        self.assertEqual((t["scored"], t["fails"], t["parts"]), (4, 0, 1))
        self.assertAlmostEqual(s["steady"], (100 * 2.00 + 500 * 10.00 + 30000 * 0.20) / 1e6)
        self.assertEqual(s["reasoning"], 75.0)

    def test_disagreements_ignore_errors(self):
        self.assertEqual([r["id"] for r in bc.disagreements(ROWS)], [2, 3])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_compare -v 2>&1 | tail -3`
Expected: `TypeError: stats() got an unexpected keyword argument 'judge'` (or an AttributeError for `disagreements`).

- [ ] **Step 3: Rewrite `bench_compare.py`**

```python
#!/usr/bin/env python3
"""Side-by-side of N bench runs: every question, every answer, both judges' verdicts.

  python3 bench_compare.py claude-sonnet-5 gpt-5.6-terra-medium gpt-5.6-terra-none \
      --out /Users/Born/Scorecard/OLIVIA_MODEL_COMPARE_2026-09-02.md
"""
import argparse, glob, json, os

from kimi_bench import PRICES

REPORT_DIR = "/Users/Born/Scorecard"
OK = ("PASS", "PARTIAL", "FAIL")
MARK = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "🔴"}


def newest(tag):
    files = sorted(glob.glob(os.path.join(REPORT_DIR, f"OLIVIA_MODEL_BENCH_{tag}_[0-9][0-9][0-9][0-9].json")))
    if not files:
        raise SystemExit(f"no bench json for {tag}")
    return json.load(open(files[-1])), os.path.basename(files[-1])


def _verdict(r, judge):
    return (r.get("verdicts") or {}).get(judge, {}).get("verdict") if judge else r.get("verdict")


def _steady(r, model):
    p = PRICES[model]
    m = r["metrics"]
    return (m["in"] * p["in"] + m["out"] * p["out"] + m["cache_r"] * p["cache_r"]) / 1e6


def stats(rows, model, judge=None):
    scored = [r for r in rows if _verdict(r, judge) in OK]
    fails = [r for r in scored if _verdict(r, judge) == "FAIL"]
    parts = [r for r in scored if _verdict(r, judge) == "PARTIAL"]
    n = max(1, len(rows))
    return {
        "n": len(rows), "scored": len(scored), "fails": len(fails), "parts": len(parts),
        "fail_pct": 100.0 * len(fails) / max(1, len(scored)),
        "cost": sum(r["cost"] for r in rows) / n,
        # steady state = what production pays on a warm prefix: cache reads + fresh input +
        # output, no cache writes (Anthropic books writes explicitly, OpenAI charges none —
        # raw totals would penalise Claude for a one-off it amortises in production).
        "steady": sum(_steady(r, model) for r in rows) / n,
        "secs": sorted(r["secs"] for r in rows)[len(rows) // 2],
        "model_secs": sum(r.get("model_secs", 0) for r in rows) / n,
        "out": sum(r["metrics"]["out"] for r in rows) / n,
        "reasoning": sum(r["metrics"].get("reasoning", 0) for r in rows) / n,
        "calls": sum(r["metrics"]["calls"] for r in rows) / n,
        "errors": len([r for r in rows if r["answer"].startswith("[")]),
    }


def disagreements(rows):
    out = []
    for r in rows:
        vs = {v.get("verdict") for v in (r.get("verdicts") or {}).values() if v.get("verdict") in OK}
        if len(vs) > 1:
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="+")
    ap.add_argument("--out", default=os.path.join(REPORT_DIR, "OLIVIA_MODEL_COMPARE.md"))
    a = ap.parse_args()

    runs = []
    for t in a.tags:
        d, f = newest(t)
        runs.append({"tag": t, "model": d["model"], "effort": d.get("effort"), "judges": d.get("judges") or [],
                     "rows": d["rows"], "by_id": {r["id"]: r for r in d["rows"]}, "file": f})
    judges = []
    for run in runs:
        for j in run["judges"]:
            if j not in judges:
                judges.append(j)
    S = {run["tag"]: stats(run["rows"], run["model"]) for run in runs}
    SJ = {(run["tag"], j): stats(run["rows"], run["model"], judge=j) for run in runs for j in judges}
    D = {run["tag"]: disagreements(run["rows"]) for run in runs}

    hdr = "| | " + " | ".join(r["tag"] for r in runs) + " |"
    sep = "|---|" + "---|" * len(runs)
    def line(label, fn):
        return f"| {label} | " + " | ".join(fn(r) for r in runs) + " |"
    L = [f"# Model comparison — " + " vs ".join(r["tag"] for r in runs), "",
         "Same questions, same system prompt, same tool schemas, same Supabase RPCs and app routes, "
         "same Voyage embeddings, same judges, same expected answers. Every run measured on a WARM "
         "prompt cache (a full unscored pass ran first) with the forced first fetch on. The only "
         "variable is the model" + (" (and, for Terra, the reasoning effort)" if any(r["effort"] for r in runs) else "") + ".",
         "", hdr, sep]
    for j in judges:
        L.append(line(f"**FAIL %** ({j} judge)", lambda r: f"**{SJ[(r['tag'], j)]['fail_pct']:.1f}%**"))
        L.append(line(f"PASS / PARTIAL / FAIL ({j} judge)", lambda r: (lambda s: f"{s['scored']-s['fails']-s['parts']} / {s['parts']} / {s['fails']}")(SJ[(r['tag'], j)])))
    L += [line("judge disagreements", lambda r: str(len(D[r["tag"]]))),
          line("**$ per answer** (warm prefix)", lambda r: f"**${S[r['tag']]['steady']:.5f}**"),
          line("$ per answer, cold", lambda r: f"${S[r['tag']]['cost']:.5f}"),
          line("latency, median", lambda r: f"{S[r['tag']]['secs']:.1f}s"),
          line("model time per answer", lambda r: f"{S[r['tag']]['model_secs']:.1f}s"),
          line("output tokens per answer", lambda r: f"{S[r['tag']]['out']:.0f}"),
          line("reasoning tokens per answer", lambda r: f"{S[r['tag']]['reasoning']:.0f}"),
          line("model calls per answer", lambda r: f"{S[r['tag']]['calls']:.1f}"),
          line("loop errors", lambda r: str(S[r['tag']]['errors'])),
          line("effort", lambda r: r["effort"] or "thinking off (prod)"),
          "", "Sources: " + " · ".join(f"`{r['file']}`" for r in runs), "",
          "Prices ($/1M): " + " · ".join(f"{m} in {p['in']} / out {p['out']} / cache read {p['cache_r']}"
                                          for m, p in PRICES.items() if m in {r['model'] for r in runs}),
          "", "---", "", "## Judge disagreements", ""]
    for run in runs:
        L.append(f"### {run['tag']} — {len(D[run['tag']])} question(s) where the judges differ")
        for r in D[run["tag"]]:
            vs = " · ".join(f"{j}: {r['verdicts'][j].get('verdict')} ({r['verdicts'][j].get('reason', '')})" for j in judges if j in r.get("verdicts", {}))
            L.append(f"- **Q{r['id']}** [{r.get('class', '')}] {r['q']} — {vs}")
        L.append("")
    L += ["---", "", "## Every question, every answer", ""]
    ids = sorted(set().union(*[set(run["by_id"]) for run in runs]))
    for qid in ids:
        any_row = next(run["by_id"][qid] for run in runs if qid in run["by_id"])
        L += [f"### Q{qid} · {any_row.get('class', '')}", f"**{any_row['q']}**", ""]
        for run in runs:
            r = run["by_id"].get(qid)
            if not r:
                L.append(f"**{run['tag']}** — not run")
                continue
            v = r.get("verdict") or ("ERROR" if r["answer"].startswith("[") else "—")
            L.append(f"**{run['tag']}** {MARK.get(v, '⚠️')} {v} · {r['secs']}s · ${r['cost']:.4f} · {r['metrics']['calls']} calls")
            for j in judges:
                jv = (r.get("verdicts") or {}).get(j)
                if jv:
                    L.append(f"> {j}: {jv.get('verdict')} — {jv.get('reason', '')}")
            L += ["", "```", (r["answer"] or "").strip()[:2000], "```", ""]
        L += ["---", ""]

    open(a.out, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:24]))
    print(f"\n-> {a.out}  ({' vs '.join(str(len(run['rows'])) for run in runs)} questions)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest discover -s tests -v 2>&1 | tail -3`
Expected: `OK` (36 tests).

- [ ] **Step 5: Smoke the report on the July runs (no spend)**

Run: `cd /Users/Born/mds-scorecard-tools && python3 bench_compare.py claude-sonnet-5 --out $SCRATCH/compare_smoke.md | head -20`
Expected: a one-column header table with the July Sonnet numbers (15.3% fail; the $ rows now use the corrected prices, so they differ from the July doc — expected), `judge disagreements | 0` (July rows have no `verdicts`), the file written. (The July JSON has no `tag`/`judges` keys — `newest("claude-sonnet-5")` matches by filename and `d["model"]` is present; the Kimi run cannot be rendered any more because its prices left `PRICES` — expected.)

---

### Task 6: Pre-flight + the harvest run on staging (operational, ~90 min, ~$5–10)

**Files:**
- Read: `/Users/Born/Scorecard/scripts/olivia_wf.py`, `/Users/Born/Scorecard/scripts/run_eval_100.py`, `/Users/Born/Scorecard/scripts/olivia_selftest.py`
- Create: `/Users/Born/mds-scorecard-tools/kimi_seeds_2026-09-02.json`, copy to `/Users/Born/Scorecard/eval_bank_snapshots/seeds_2026-09-02_bank100.json`

**Interfaces:**
- Produces: the seeds file (Task 7 input), the harvest window `START`/`END` (UTC, `YYYY-MM-DDTHH:MM`), the staging exec id range, the prod exec list for AC (a).

- [ ] **Step 1: Pre-flight (read-only)**

```bash
cd /Users/Born/Scorecard && python3 scripts/olivia_wf.py status && python3 scripts/olivia_wf.py diff prod staging | tail -6
```
Expected: `LOCK  : free`; diff `changed : ['WA Inbound (POST)', 'WA Verify (GET)']` only (webhook path/webhookId). If anything else differs or the lock is held, STOP and report — do not stage from prod yourself unless Andy says so.

Key checks (5 tokens each):
```bash
K=$(grep "^CENTURION_ANTHROPIC_API_KEY=" /Users/Born/mds-digest-web/.env.local | cut -d= -f2-); curl -sS https://api.anthropic.com/v1/messages -H "x-api-key: $K" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model":"claude-haiku-4-5","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' | cut -c1-120
O=$(grep "^OPENAI_API_KEY=" /Users/Born/mds-digest-web/.env.local | cut -d= -f2-); curl -sS https://api.openai.com/v1/models/gpt-5.6-terra -H "Authorization: Bearer $O" | cut -c1-120
```
Expected: an Anthropic message JSON (not `credit balance is too low`) and `{"id": "gpt-5.6-terra", …}`.

- [ ] **Step 2: Take the lock and tell the peer**

```bash
cd /Users/Born/Scorecard && python3 scripts/olivia_wf.py lock --reason "#156 harvest run — no graph edits, 100 silent turns on staging, ~90 min"
```
Then `ListAgents`; if another Olivia session is listed, `SendMessage` it: "Holding the Olivia lock ~90 min for #156: firing the 100 bank at staging (silent), no graph edits. Will release and re-diff when done." If none is listed, write that in the session log instead.

- [ ] **Step 3: Fire the bank at staging, in the background, with the window recorded**

```bash
export SCRATCH=<this session's scratchpad directory>   # from the system prompt; every $SCRATCH below means this
cd /Users/Born/Scorecard && date -u +%Y-%m-%dT%H:%M > $SCRATCH/harvest_start && python3 scripts/run_eval_100.py --staging > $SCRATCH/harvest_run.log 2>&1; echo EXIT $? >> $SCRATCH/harvest_run.log; date -u +%Y-%m-%dT%H:%M > $SCRATCH/harvest_end
```
Run it with `run_in_background: true` (it takes 60–90 minutes: 100 questions + ~12 resets, each waiting for the reply). Monitor with `tail -3 $SCRATCH/harvest_run.log` every ~15 minutes; do not start Task 7 until `harvest_end` exists. The scratchpad path is the session's (`/private$SCRATCH/-Users-Born-Scorecard/<session>/scratchpad`) — substitute it for `$SCRATCH` above.

- [ ] **Step 4: Release the lock, prove staging unchanged**

```bash
cd /Users/Born/Scorecard && python3 scripts/olivia_wf.py diff prod staging | tail -6 && python3 scripts/olivia_wf.py unlock && python3 scripts/olivia_wf.py status | head -3
```
Expected: the same two webhook-only changes; `LOCK  : free`. SendMessage the peer "lock released" if one was told.

- [ ] **Step 5: Harvest**

```bash
cd /Users/Born/mds-scorecard-tools && python3 kimi_harvest.py --since $(cat $SCRATCH/harvest_start) --until $(cat $SCRATCH/harvest_end) --bank /Users/Born/Scorecard/eval_bank_100_2026-08-16.json --out kimi_seeds_2026-09-02.json 2>&1 | tail -25
```
Expected: `N/100 seeds -> kimi_seeds_2026-09-02.json (29 tool schemas, system ~76000 chars, ~20 with history)`, and a `MISSING` line per unharvested question with its reason (`no_seed` = canned lane, never reached the loop; `not_fired` = the selftest never sent it — check the run log). Record N and the missing list for the close block. Copy the seeds into the repo snapshot folder:
`cp kimi_seeds_2026-09-02.json /Users/Born/Scorecard/eval_bank_snapshots/seeds_2026-09-02_bank100.json`

- [ ] **Step 6: AC (a) proof — prod saw no bench traffic**

```bash
cd /Users/Born/Scorecard && python3 - <<'EOF'
import json,subprocess
e={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l and not l.startswith("#")}
import os; S=os.environ["SCRATCH"]
base=e["N8N_API_URL"].rstrip("/"); start=open(S+"/harvest_start").read().strip(); end=open(S+"/harvest_end").read().strip()
r=subprocess.run(["curl","-sS",f"{base}/api/v1/executions?workflowId=12wj6h1TWqb0d4Dq&limit=250","-H",f"X-N8N-API-KEY: {e['N8N_API_KEY']}"],capture_output=True,text=True)
ex=[x for x in json.loads(r.stdout)["data"] if start<=x["startedAt"][:16]<=end]
print(len(ex),"prod executions in the window; ids",ex[-1]["id"] if ex else None,"..",ex[0]["id"] if ex else None)
n=0
for x in ex[:250]:
    d=json.loads(subprocess.run(["curl","-sS",f"{base}/api/v1/executions/{x['id']}?includeData=true","-H",f"X-N8N-API-KEY: {e['N8N_API_KEY']}"],capture_output=True,text=True).stdout)
    rd=((d.get("data") or {}).get("resultData") or {}).get("runData") or {}
    li=(rd.get("Log Inbound") or [{}])[0].get("data",{}).get("main",[[{}]])[0][0].get("json",{})
    if str(li.get("wamid","")).startswith("wamid.SELFTEST"): n+=1
print("SELFTEST turns on PROD in the window:",n,"(must be 0 — the daily 05:05 eval is outside this window)")
EOF
```
Expected: `SELFTEST turns on PROD in the window: 0`. Record the prod exec id range.

- [ ] **Step 7: Clean the selftest rows on staging's tables**

`cd /Users/Born/Scorecard && python3 scripts/olivia_selftest.py --staging --cleanup` — Expected: `cleanup done (bounded by this run's SELFTEST timestamps)`.

- [ ] **Step 8: Commit the seeds snapshot**

```bash
cd /Users/Born/Scorecard && git add eval_bank_snapshots/seeds_2026-09-02_bank100.json && git commit -m "#156: seeds harvested from staging — locked 100 bank, exact Answer Seed bodies

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: The bench runs (operational, ~2 h wall clock, ~$25–35)

**Files:**
- Create (by the bench): `/Users/Born/Scorecard/OLIVIA_MODEL_BENCH_claude-sonnet-5_<HHMM>.{md,json}`, `…gpt-5.6-terra-medium_<HHMM>…`, `…gpt-5.6-terra-none_<HHMM>…`

**Interfaces:**
- Consumes: `kimi_seeds_2026-09-02.json`. Produces the three run tags for Task 8: `claude-sonnet-5`, `gpt-5.6-terra-medium`, `gpt-5.6-terra-none`.

- [ ] **Step 1: 2-question smoke per configuration on the NEW seeds, no judge (~$0.50)**

```bash
cd /Users/Born/mds-scorecard-tools && for cfg in "claude-sonnet-5" "gpt-5.6-terra --effort medium" "gpt-5.6-terra --effort none"; do python3 kimi_bench.py --model $cfg --limit 2 --no-judge --seeds kimi_seeds_2026-09-02.json 2>&1 | grep -E "^BENCH|^  Q|Loop errors|Tokens"; done
```
Expected: 6 `Q… ok` lines, `Loop errors: 0` three times, no `[API ERROR]`. If an OpenAI run shows `[API ERROR] … context_length` or `max_output_tokens`, stop and report — the 76K-char system prompt is ~20K tokens and must fit trivially, so that would be a body bug. Delete the six smoke report files (they carry this hour's HHMM stamp; `ls` first).

- [ ] **Step 2: Full runs, one at a time, in the background**

```bash
cd /Users/Born/mds-scorecard-tools && python3 kimi_bench.py --model claude-sonnet-5 --passes 2 --workers 4 --seeds kimi_seeds_2026-09-02.json > $SCRATCH/bench_sonnet.log 2>&1
```
Then, after it finishes (`tail -2` shows `report ->`):
```bash
cd /Users/Born/mds-scorecard-tools && python3 kimi_bench.py --model gpt-5.6-terra --effort medium --passes 2 --workers 3 --seeds kimi_seeds_2026-09-02.json > $SCRATCH/bench_terra_medium.log 2>&1
```
Then:
```bash
cd /Users/Born/mds-scorecard-tools && python3 kimi_bench.py --model gpt-5.6-terra --effort none --passes 2 --workers 3 --seeds kimi_seeds_2026-09-02.json > $SCRATCH/bench_terra_none.log 2>&1
```
Each run: pass 1 prints `-- pass 1/2 done (cache reads N)`; pass 2 prints the per-question lines, then the two judges, then the header. Expected per run: `Loop errors: 0` (or each error listed), `cached in … (>80% cached)` on the scored pass, both judge lines with `ERROR 0`. Retries print `retry in Ns: …` — a handful is fine; a wall of them means the OpenAI tier limit, so drop `--workers` to 2 and re-run that config.

- [ ] **Step 3: Sanity on the three JSONs**

```bash
cd /Users/Born/Scorecard && python3 - <<'EOF'
import json,glob
for tag in ("claude-sonnet-5","gpt-5.6-terra-medium","gpt-5.6-terra-none"):
    f=sorted(glob.glob(f"OLIVIA_MODEL_BENCH_{tag}_[0-9][0-9][0-9][0-9].json"))[-1]; d=json.load(open(f)); rows=d["rows"]
    err=[r["id"] for r in rows if r["answer"].startswith("[")]
    jerr={j:[r["id"] for r in rows if r["verdicts"][j]["verdict"]=="ERROR"] for j in d["judges"]}
    print(f, len(rows),"rows; loop errors",err,"; judge errors",jerr,"; cache_r>0:",sum(1 for r in rows if r["metrics"]["cache_r"]>0))
EOF
```
Expected: 3 files, N rows each (N = seeds harvested), empty error lists, `cache_r>0` = N (warm). Any judge `ERROR` ids: re-judge those rows by re-running the bench with `--ids <list>` for that model — no, that re-answers; instead note them in the close block as unscored (the compare excludes ERROR from fail %).

---

### Task 8: Compare report, close the ticket, logs, handoff

**Files:**
- Create: `/Users/Born/Scorecard/OLIVIA_MODEL_COMPARE_2026-09-02.md`
- Modify: `/Users/Born/Scorecard/OLIVIA_SPRINT_4.md` (#156 close block + table row), `/Users/Born/Scorecard/SESSION_LOG_OLIVIA.md` (prepend entry), `/Users/Born/Scorecard/SESSION_LOG.md` (one index line), `/Users/Born/Scorecard/OLIVIA_NEXT_SESSION.md` (state + Andy's desk), memory `project_mds_olivia_pilot.md` (one line)

- [ ] **Step 1: Build the report**

```bash
cd /Users/Born/mds-scorecard-tools && python3 bench_compare.py claude-sonnet-5 gpt-5.6-terra-medium gpt-5.6-terra-none --out /Users/Born/Scorecard/OLIVIA_MODEL_COMPARE_2026-09-02.md | head -24
```
Expected: the headline table with three columns, two FAIL % rows (one per judge), disagreement counts, $ rows, then `-> …OLIVIA_MODEL_COMPARE_2026-09-02.md (N vs N vs N questions)`.

- [ ] **Step 2: Read the disagreement section yourself** (`sed -n '/## Judge disagreements/,/## Every question/p' OLIVIA_MODEL_COMPARE_2026-09-02.md`) and put the count per run plus the 3–5 most telling question ids into the close block. Do not re-grade; Andy reads them.

- [ ] **Step 3: Close #156 on the board** (re-read the file first; the peer session edits it too). Append inside the ticket, then move the whole ticket to the CLOSED section and flip its table row (`Staging` → `— (harvest run only)`, `Prod` → `✅ decision data delivered <date>`):

```
#### ✅ BUILT + RUN + REPORTED 2026-09-02 — decision data, nothing promoted
**The work:** bench harness brought to the 2026-09-02 graph (`bench_tools.py` mirrors Attach Embedding / Answer Tool / Answer Merge; 36 unit tests green), OpenAI Responses loop + dual judge added; one silent bank run on staging harvested (execs <first>–<last>), replayed through Sonnet 5, Terra-medium, Terra-none, 2 passes each.

| AC | result |
|---|---|
| (a) 100/100 seeds from ONE staging run, prod exec log shows no bench traffic | <N>/100 seeds (missing: <ids + reasons>); prod window <start>–<end>: <M> real executions, 0 SELFTEST; staging diff identical before/after |
| (b) both models run warm, 0 loop errors or every error listed | Sonnet <e1> · Terra-medium <e2> · Terra-none <e3> loop errors; cache reads on the scored pass <pct>% |
| (c) $/answer steady-state + cold per model at today's list prices | Sonnet $<s>/$<c> · Terra-medium $<s>/$<c> · Terra-none $<s>/$<c> |
| (d) fail % Sonnet judge, cross-checked by Terra judge, disagreements listed | Sonnet judge: <a>% / <b>% / <c>% · Terra judge: <a'>% / <b'>% / <c'>% · disagreements <n1>/<n2>/<n3> (report §Judge disagreements) |
| (e) one compare report with all answer pairs | `OLIVIA_MODEL_COMPARE_2026-09-02.md` |
| (f) staging left as found, lock released | `olivia_wf.py status` LOCK free, diff webhook-only |
**Before → after:** July (#22): Sonnet 15.3% fail / $0.0135 vs Kimi 22.2% / $0.0270 → today: <one line>. Spend this ticket: $<total> (harvest <h> + bench <b> + judges <j>).
**Remainders:** the prompt is Claude-tuned (bias against Terra, not corrected) · post-model gates not run for either · an n8n port is a separate ticket if Terra is chosen · Andy rotates the OpenAI key (pasted into chat 2026-09-02).
```

- [ ] **Step 4: Logs, handoff, memory, commit**

Prepend a dated entry to `SESSION_LOG_OLIVIA.md` (what shipped: files, seed count, the headline numbers, spend, what Andy decides next), one line to the `SESSION_LOG.md` index, refresh the STATE block in `OLIVIA_NEXT_SESSION.md` (#156 delivered; Andy's desk: vendor call + key rotation), and one line in the memory file `project_mds_olivia_pilot.md` (bench harness lives in `mds-scorecard-tools`, `bench_tools.py` must track the graph's tool nodes; Terra needs the Responses API for tools + reasoning). Then:

```bash
cd /Users/Born/Scorecard && git add OLIVIA_MODEL_COMPARE_2026-09-02.md OLIVIA_MODEL_BENCH_claude-sonnet-5_*.md OLIVIA_MODEL_BENCH_claude-sonnet-5_*.json OLIVIA_MODEL_BENCH_gpt-5.6-terra-*.md OLIVIA_MODEL_BENCH_gpt-5.6-terra-*.json OLIVIA_SPRINT_4.md SESSION_LOG_OLIVIA.md SESSION_LOG.md OLIVIA_NEXT_SESSION.md && git commit -m "#156: Sonnet 5 vs GPT-5.6 Terra bench — compare report, close block, logs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
(Only this session's bench files: check `git status` for a peer's files first and leave them out.)

- [ ] **Step 5: Tell Andy** — the headline table (fail % per judge, $/answer, latency), the disagreement count, the spend, the report path, and the one open call: vendor decision (+ key rotation). No recommendation beyond the numbers unless asked.
