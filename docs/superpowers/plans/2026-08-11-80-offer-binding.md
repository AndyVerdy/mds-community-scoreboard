# #80 Offer Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a member accepts an offered video summary, Olivia delivers THAT video's stored summary — and she stops teasing a next step on every reply.

**Architecture:** Three layers, smallest change per layer. (1) SQL: `digest.video_search_v2` — the function the loop's `video_search` tool actually executes (Attach Embedding's EXEC map renames it) — gains `p_video_id` (exact-row fetch) and a `summary` return column (it currently returns NO summary, so a bound call could never deliver one). (2) n8n Answer Seed only: deterministic offer-binding context (previous Olivia turn ends in an offer + links `app.mds.co/videos/<id>` + current turn is an acceptance → inject an `OFFER ACCEPTED` line into the preload evidence block) plus two new rules (DELIVER WHAT YOU OFFERED · OFFER SPARINGLY) and the `p_video_id` tool-schema entry. (3) Proof: staging before/after probes on the exact failing shape, gate, board close. No Format Reply / Save Conversation changes — binding detection reads the stored message text, which is already verbatim in `olivia_messages`.

**Tech Stack:** Supabase Postgres (migrations via MCP `apply_migration`), n8n staging workflow `bqHstPDi84uOhTCJ` edited by a committed apply script (70c pattern), `scripts/olivia_selftest.py --staging` probes, `scripts/olivia_leak_gate.py`.

## Global Constraints

- Prod workflow `12wj6h1TWqb0d4Dq` is NEVER edited directly; staging + Andy's promote only. Lock via `python3 scripts/olivia_wf.py lock --reason "#80 offer binding"` before staging edits.
- Gate must run `--phone 16196077048` (Ian) — the default probe (Andy) aborts on his empty `channels_present` (upstream sync issue, open question on the board).
- NO apostrophes inside Answer Seed rule strings (rules are single-quoted JS — burned twice).
- NO bare apostrophes in n8n jsonBody expressions; `node --check` every edited Code node before PUT.
- After ANY migration: `python3 scripts/db_export_schema.py` then `--check` (exit 0) and commit `db/`.
- DROP+CREATE on a PostgREST RPC → `notify pgrst, 'reload schema'` + hammer the REST path until 200 (stale-pool 404s otherwise).
- Probes fire ONLY at `https://mdsco.app.n8n.cloud/webhook/olivia-wa-staging`, probe phone `17866578153`, wamids `wamid.SELFTEST*` (silent — never delivered).
- Reference failing cases (prod, week of 2026-08-04..11): answers #28131, #28133 (Andy WA), #29905, #29907 (Andy via digest.mds.co test window, identity …6303). Working comparator: #27225 (SOS call, `sources_used=['video_search']`).

---

### Task 1: `video_search_v2` — `p_video_id` param + `summary` return column

**Files:**
- Create: `scripts/sql/gen_video_search_v2_80.py` (migration generator — reads the byte-matched export, applies 4 exact edits, prints SQL)
- Modify (via migration): live `digest.video_search_v2` (source of truth export: `db/functions/video_search_v2.sql`)
- Modify (regenerated): `db/functions/video_search_v2.sql`, `db/grants.sql` (via `scripts/db_export_schema.py`)

**Interfaces:**
- Consumes: current signature `video_search_v2(p_phone text, p_query text, p_limit integer, p_embedding text, p_at_member_id text, p_call_type text, p_order text)`.
- Produces: signature + `p_video_id text DEFAULT NULL` (exact-row filter at the base CTE, restriction logic untouched) and RETURNS TABLE + trailing `summary text` (null when restricted). Task 3's tool schema and Task 4's probes rely on the REST name `video_search_v2` and the `summary` field.

- [ ] **Step 1: Failing test — REST call with `p_video_id` must fail today**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/video_search_v2",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_video_id":"6a502b215c9f55877277dcc4"})],
 capture_output=True,text=True)
print(r.stdout[:300])
EOF
```

Expected: PostgREST error `PGRST202` (no function matches — `p_video_id` is not a parameter yet). If this ALREADY succeeds, stop: the migration exists; skip to Step 6.

- [ ] **Step 2: Write the migration generator**

```python
#!/usr/bin/env python3
"""#80 — regenerate digest.video_search_v2 with p_video_id + a summary return column.

Reads the byte-matched export (db/functions/video_search_v2.sql), applies FOUR exact
edits, and prints the full migration SQL (DROP + CREATE + grants + pgrst reload).
Return-type changes require DROP; DROP on a PostgREST RPC requires the reload notify.
"""
SRC = "/Users/Born/Scorecard/db/functions/video_search_v2.sql"

body = open(SRC).read().split("\n", 1)[1]  # strip the GENERATED header line

edits = [
    # 1) signature: add p_video_id
    ("p_order text DEFAULT NULL::text)",
     "p_order text DEFAULT NULL::text, p_video_id text DEFAULT NULL::text)"),
    # 2) return table: trailing summary column
    ("is_restricted boolean, fit_reason text, strength_note text)",
     "is_restricted boolean, fit_reason text, strength_note text, summary text)"),
    # 3) base CTE: exact-id filter (published/deleted/restriction logic untouched)
    ("where v.status = 'published' and v.deleted_at is null",
     "where v.status = 'published' and v.deleted_at is null\n       and (p_video_id is null or v.video_id = p_video_id)"),
    # 4) final select: emit the summary (never for restricted videos)
    ("         f.snote\n    from fused f",
     "         f.snote,\n         case when f.restricted then null else f.summary end\n    from fused f"),
]
for old, new in edits:
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:60]!r}"
    body = body.replace(old, new)

print("drop function digest.video_search_v2(text, text, integer, text, text, text, text);")
print(body.rstrip() + ";")
print("""
grant execute on function digest.video_search_v2(p_phone text, p_query text, p_limit integer, p_embedding text, p_at_member_id text, p_call_type text, p_order text, p_video_id text) to postgres;
grant execute on function digest.video_search_v2(p_phone text, p_query text, p_limit integer, p_embedding text, p_at_member_id text, p_call_type text, p_order text, p_video_id text) to service_role;
notify pgrst, 'reload schema';""")
```

Save as `scripts/sql/gen_video_search_v2_80.py`, run `python3 scripts/sql/gen_video_search_v2_80.py > /tmp/mig80.sql` (all four asserts must pass), read the output once end-to-end.

- [ ] **Step 3: Apply the migration**

Apply via Supabase MCP `apply_migration` with name `video_search_v2_p_video_id_summary_80` and the generated SQL as the query.

- [ ] **Step 4: Hammer the REST path until the new signature answers (stale-pool guard)**

Re-run the Step 1 script up to 5 times (2s apart). Expected: JSON array with exactly 1 row — `title` = "How to Optimize Amazon Titles and Item Highlights for Mobile", `summary` non-null (~472 chars), `video_url` populated. No 404/PGRST202 on the final attempt.

- [ ] **Step 5: Regression — old call shapes unchanged**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
def rpc(body):
    r=subprocess.run(["curl","-s","-X","POST",
     "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/video_search_v2",
     "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
     "-H","Content-Type: application/json","-H","Content-Profile: digest",
     "-d",json.dumps(body)],capture_output=True,text=True)
    return json.loads(r.stdout)
a=rpc({"p_phone":"17866578153","p_query":"tiktok creator outreach","p_limit":3})
b=rpc({"p_phone":"17866578153","p_call_type":"mogul","p_order":"recent","p_limit":3})
c=rpc({"p_phone":"17866578153","p_video_id":"69cd325ef7c4559c1a708cfc"})
print("query-mode rows:",len(a),"| recent-mogul rows:",len(b),"| by-id summary len:",len((c[0].get("summary") or "")))
assert len(a)>=1 and len(b)>=1 and len(c)==1 and c[0]["summary"], "REGRESSION"
print("OK")
EOF
```

Expected: `OK`, by-id summary len ≈ 533.

- [ ] **Step 6: Re-export schema, verify byte-sync, commit**

```bash
python3 scripts/db_export_schema.py && python3 scripts/db_export_schema.py --check
```

Expected: `DB IN SYNC — 122 files byte-match the live database.` Then:

```bash
git add db/functions/video_search_v2.sql db/grants.sql scripts/sql/gen_video_search_v2_80.py
git commit -m "#80 video_search_v2: p_video_id exact fetch + summary return column"
```

---

### Task 2: BEFORE-probe — lock the failing shape on staging

**Files:**
- None modified. Uses `scripts/olivia_selftest.py --staging` (staging graph currently equals prod, so it reproduces the live defect).

**Interfaces:**
- Consumes: staging webhook `olivia-wa-staging`; `digest.olivia_messages` (`plan->sources_used`).
- Produces: recorded BEFORE evidence (message ids + `sources_used`) that Task 4 compares against.

- [ ] **Step 1: Take the lock**

```bash
python3 scripts/olivia_wf.py lock --reason "#80 offer binding"
```

Expected: `LOCK ACQUIRED`.

- [ ] **Step 2: Fire the failing 3-turn sequence at staging**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "what are people saying about amazon main image aspect ratio on mobile?" "Yes"
```

Expected printed transcript: turn 2 answers from community + (per the ADVICE ASKS rule) points at a library video with an offer tail; turn 3 ("Yes") answers with community/thread content again — the defect. If turn 2 offers NO video link, re-run turn 2 once with "how do people optimize amazon titles for mobile search?" — the assertion needs an offer that links a video.

- [ ] **Step 3: Record BEFORE evidence**

```sql
select id, role, left(text,120), plan->'sources_used' as sources
from digest.olivia_messages
where phone='17866578153' and wamid like '%SELFTEST%'
  and created_at > now() - interval '20 minutes'
order by id;
```

Run via Supabase MCP `execute_sql`. Record: the Yes-answer's id and `sources` (expected: `content_search` only, or missing `video_search`) into the session notes. This is the failing test for Task 3.

---

### Task 3: Answer Seed — offer binding context + p_video_id schema + two rules

**Files:**
- Create: `scripts/olivia_loop/apply_80_offer_binding.py`
- Modify (via that script): staging workflow `bqHstPDi84uOhTCJ`, node `Answer Seed` ONLY.

**Interfaces:**
- Consumes: Task 1's `p_video_id` parameter (schema text tells the model it exists); Answer Seed internals — `rows` (chronological turns, incl. text), `current` (member text), `preload` assembly.
- Produces: seed markers `OFFER ACCEPTED`, `DELIVER WHAT YOU OFFERED`, `OFFER SPARINGLY`, `p_video_id` — Task 4 asserts on behavior, Task 5's board block cites these markers verified in the staging node.

- [ ] **Step 1: Write the apply script**

Model on `scripts/olivia_loop/apply_70c_recency_and_buttons.py` (same `env`/`api`/`patch` helpers, same PUT + single deactivate/activate bounce + read-back verify; STAGING_ID `bqHstPDi84uOhTCJ`). Four patches, each with the 70c `patch()` idempotence contract (marker check → unique-anchor assert → replace):

**Patch A — tool schema gains p_video_id** (marker `p_video_id`):

```python
OLD_SCHEMA = ("input_schema: S({ p_query: str('topic, speaker or title words - OMIT for a "
              "latest/browse ask'), p_call_type: str('mogul | expert | channel | chapter - "
              "filters to that kind of call'), p_order: str('recent = newest first, for "
              "last/latest/most-recent asks'), p_limit: num('max videos') }, []) },")
NEW_SCHEMA = ("input_schema: S({ p_query: str('topic, speaker or title words - OMIT for a "
              "latest/browse ask'), p_call_type: str('mogul | expert | channel | chapter - "
              "filters to that kind of call'), p_order: str('recent = newest first, for "
              "last/latest/most-recent asks'), p_video_id: str('exact library video id from an "
              "app.mds.co/videos/<id> link - fetches THAT video with its summary; use it when "
              "delivering an offered or linked video'), p_limit: num('max videos') }, []) },")
```

**Patch B — offer-binding detection before the preload block** (marker `OFFER ACCEPTED`), anchored on the unique line `let preload = '';`:

```python
OLD_PRELOAD_DECL = "let preload = '';"
NEW_PRELOAD_DECL = '''// #80 OFFER BINDING. The failing sessions (ans #28131/#28133/#29905) re-searched the
// TOPIC on a bare acceptance and delivered chat chatter instead of the teased video -
// whose transcript summary sat unread in videos_catalog. Deterministic detection:
// previous Olivia turn ends in an offer AND links a library video AND the member is
// accepting -> inject the binding as evidence the loop cannot miss.
const ACCEPT_RE = /^(yes|yes please|yep|yeah|sure|ok|okay|sounds good|go ahead|please do|do it|summar(y|ize|ise)( key points| it)?|key points( please)?|can you summar(y|ize|ise)[^?]{0,40}[?]?)[!. ]*$/i;
const OFFER_TAIL_RE = /(want (a|the) quick summary|want me to|want the (link|details|rest)|would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\\?\\s*$/i;
let offer_ctx = '';
try {
  let lastO = null;
  for (let i = rows.length - 1; i >= 0 && !lastO; i--) { if (rows[i].role !== 'member') lastO = rows[i]; }
  const lt = lastO ? String(lastO.text || '') : '';
  const links = lt.match(/app\\.mds\\.co\\/videos\\/([a-f0-9]{24})/gi) || [];
  if (OFFER_TAIL_RE.test(lt.trim()) && links.length && ACCEPT_RE.test(current)) {
    const vid = String(links[links.length - 1]).split('/').pop();
    offer_ctx = 'OFFER ACCEPTED: your previous message offered the library video ' + vid
      + ' and the member just accepted. Call video_search with p_video_id set to ' + vid
      + ' and answer from its summary field. Community threads may only supplement, clearly separated.';
  }
} catch (e) {}
let preload = offer_ctx;'''
```

**Patch C — preload join keeps the binding when zeroth-fetch rows exist** (marker `offer_ctx ?`):

```python
OLD_JOIN = "  preload = parts.join(NL);"
NEW_JOIN = "  preload = (offer_ctx ? offer_ctx + NL + NL : '') + parts.join(NL);"
```

**Patch D — two rules before the standing tail rule** (marker `DELIVER WHAT YOU OFFERED`), anchored on the unique line:

```python
OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"
NEW_RULES = (
  "  '- DELIVER WHAT YOU OFFERED (#80): when the member accepts an offer (yes / sure / "
  "summarize it / key points) and your previous message linked a specific library video, "
  "the accepted thing IS the question. Call video_search with p_video_id set to the id "
  "from that link FIRST and answer from its summary field. Community threads may only "
  "supplement, clearly separated. If the video is restricted or summary is empty, say "
  "honestly what is on file - never substitute chat chatter for the video you teased.',\n"
  "  '- OFFER SPARINGLY (#80): end with an offer ONLY when it names ONE concrete thing you "
  "can produce next (a specific video summary, a specific thread, a specific list). Never "
  "offer two alternatives in one question - a Yes button cannot answer an either-or. A "
  "complete answer ends as a statement, not a tease.',\n"
)
# applied as: seed = patch(seed, OLD_RULE_TAIL, NEW_RULES + OLD_RULE_TAIL, ...)
```

Script tail (identical shape to 70c): `node --check` the patched seed via tempfile (abort on failure), PUT `{name, nodes, connections, settings-subset}`, deactivate/activate once, GET back and assert all four markers present exactly once each; print the staging `versionId`.

- [ ] **Step 2: Sanity-check the rule strings contain no apostrophes**

```bash
python3 - <<'EOF'
import re
src = open('scripts/olivia_loop/apply_80_offer_binding.py').read()
for name in ('NEW_RULES',):
    block = re.search(name + r" = \((.*?)\n\)", src, re.S).group(1)
    inner = ''.join(re.findall(r'"([^"]*)"', block))
    bad = [c for c in inner if c == chr(39)]
    print(name, 'apostrophes:', len(bad))
    assert not bad
print('OK')
EOF
```

Expected: `OK`.

- [ ] **Step 3: Apply to staging**

```bash
python3 scripts/olivia_loop/apply_80_offer_binding.py
```

Expected output: `node --check: OK`, `PUT + bounce done`, four `patched` lines (or `already applied` on re-run), new staging `versionId` printed. Record the versionId.

- [ ] **Step 4: Commit the apply script**

```bash
git add scripts/olivia_loop/apply_80_offer_binding.py
git commit -m "#80 staging: offer-binding context, p_video_id schema, two offer rules"
```

---

### Task 4: AFTER-probes — the failing shape now delivers the teased video

**Files:**
- None modified. `scripts/olivia_selftest.py --staging` + Supabase MCP `execute_sql`.

**Interfaces:**
- Consumes: Task 2's BEFORE evidence (ids + sources) and Task 3's staging build.
- Produces: AFTER evidence for Task 5's AC table (ids, `sources_used`, summary-content match).

- [ ] **Step 1: Re-fire the exact BEFORE sequence**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "what are people saying about amazon main image aspect ratio on mobile?" "Yes"
```

Expected transcript: turn 3 now delivers the teased video's summary (content recognizably from `videos_catalog.summary` — for `6a502b21…` that is title/mobile-search themes, not the Fabio HD thread rehash), with community content at most as a labeled supplement.

- [ ] **Step 2: Fire the "summarize key points" variant (#29907's shape)**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "how do people optimize amazon titles for mobile search?" "Can you summarize key points"
```

Expected: same binding — the summary of the linked video, not a thread re-summary.

- [ ] **Step 3: Assert with SQL, not eyeballs**

```sql
select id, role, left(text,160) as text, plan->'sources_used' as sources
from digest.olivia_messages
where phone='17866578153' and wamid like '%SELFTEST%'
  and created_at > now() - interval '30 minutes'
order by id;
```

Pass criteria per accepted-offer answer: `sources` contains `video_search` AND the text names the offered video's title or content (compare against `select left(summary,200) from digest.videos_catalog where video_id='<the offered id>'`). Record ids + sources into the session notes as the AFTER column.

- [ ] **Step 4: Regression probes — the two lanes that already worked**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "what was the last mogul call" "yes"
```

Expected: date-ordered latest Mogul Call (the #70c behavior intact), and the "yes" still summarizes THAT call. Then:

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "how many members are in MDS?"
```

Expected: a complete count answer that ends as a statement — no "Want me to…?" tail (OFFER SPARINGLY observed on a self-contained answer).

- [ ] **Step 5: Cleanup probe turns**

```bash
python3 scripts/olivia_selftest.py --cleanup
```

Expected: reports deletions for this run's SELFTEST rows.

---

### Task 5: Gate, board close, logs, handoff — promote stays Andy's

**Files:**
- Modify: `OLIVIA_SPRINT_3.md` (#80 → CLOSED with evidence block; at-a-glance row below the separator)
- Modify: `SESSION_LOG_OLIVIA.md` (prepend entry), `SESSION_LOG.md` (one index line), `OLIVIA_NEXT_SESSION.md` (state block: #80 staged, awaiting promote)

**Interfaces:**
- Consumes: BEFORE evidence (Task 2), AFTER evidence (Task 4), staging versionId (Task 3), gate count.
- Produces: the promote instruction for Andy: `OLIVIA_GATE_PHONE=16196077048 python3 scripts/olivia_wf.py promote` (or via me on his order), then one prod spot-probe of the offer→Yes shape.

- [ ] **Step 1: Gate — full run, exit code checked**

```bash
python3 scripts/olivia_leak_gate.py --phone 16196077048 > /tmp/gate80.log 2>&1; echo "EXIT=$?"; tail -3 /tmp/gate80.log
```

Expected: `EXIT=0`, `GATE PASSED`, 246 checks (`grep -c "  PASS" /tmp/gate80.log`).

- [ ] **Step 2: Board evidence block**

Append inside the #80 ticket, then move the whole ticket to ✅ CLOSED (top) and flip its at-a-glance row to `✅ proven <staging versionId> | ⏳ awaiting promote`:

```markdown
#### ✅ BUILT + STAGED + PROVEN <date> — awaiting Andy's promote
**The fix:** offer binding made deterministic — Answer Seed detects offer-tail + video link +
acceptance and injects OFFER ACCEPTED into the evidence block; video_search gained p_video_id +
a summary return column (video_search_v2 returned NO summary before — even a correct call could
not deliver one); two rules (DELIVER WHAT YOU OFFERED · OFFER SPARINGLY).

| AC | result |
|---|---|
| follow-up suggestion only when it helps | <self-contained probe answer ends w/o offer tail: msg id> |
| accepting delivers the offered thing, measured on the failed cases | <BEFORE id: sources=content_search only → AFTER id: sources incl video_search + summary content; both variants (Yes · summarize key points)> |
| no class traded, gate green, verified in the prod node | <regression probe ids · gate 246 exit-0 · prod verify pending promote> |

**Before → after** on the failing class: 3/3 accepted video offers delivered thread chatter
(week of Aug 4–11) → 0/2 on the same shape replayed (staging). Offer-tail baseline 26% of
llm answers — re-measure on the next week of traffic after promote.
```

(Fill every `<…>` with the recorded ids/numbers — none may survive into the commit.)

- [ ] **Step 3: Logs + handoff**

Prepend the dated entry to `SESSION_LOG_OLIVIA.md` (what shipped: migration name, apply script, staging versionId; what was verified: probe ids, gate; what is next: promote + prod spot-probe + offer-rate re-measure). One line to `SESSION_LOG.md`. Update `OLIVIA_NEXT_SESSION.md` state block: #80 staged `<versionId>`, prod still `e5d57236`, promote command for Andy.

- [ ] **Step 4: Commit + unlock**

```bash
git add OLIVIA_SPRINT_3.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md
git commit -m "#80 board close (staged, awaiting promote) + session logs"
python3 scripts/olivia_wf.py unlock
```

Expected: commit lands; `LOCK RELEASED`.

---

## Self-review notes

- Spec coverage: AC "suggestion only when helps" → Task 3 Patch D rule + Task 4 Step 4 probe (+ standing re-measure after promote, named in the board block — a one-week style rate cannot be fully proven pre-promote and is recorded as such, not claimed). AC "accepting delivers the offered thing, measured on failed cases" → Tasks 1–4 (both failing variants replayed). AC "no class traded, gate green, verified in prod node" → Task 4 Step 4 + Task 5 Step 1; prod-node verification is explicitly the promote step (Andy), matching how #75 closed.
- Types: `p_video_id text` consistent across migration, schema string, rules, probes. `summary text` appended LAST in RETURNS TABLE so existing positional consumers are unaffected.
- The `rows` variable consumed by Patch B exists in Answer Seed (`let rows = [];` head section, chronological after slice/reverse) — verified against the live node this session.
- Placeholders: the only `<…>` tokens are in the Task 5 evidence template and are explicitly required to be filled from recorded ids before commit.
