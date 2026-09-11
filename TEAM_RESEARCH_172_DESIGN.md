# #172 · Team research mode — design (2026-09-10)

> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

**Ruling this design rests on (Andy, 2026-09-10):** *"we should provide answers to all the questions, no
gates. Ideally, it should be similar to the result if I ask you [Claude with MCPs]"* · *"team chat where
our team can get a full access with the semantic layer where we can see who is asking"* · *"Millie … is
answering from supa, not AT. supa is faster, and has more data"* · "Team chat through Millie first" (the
MCP is a second door later, its own ticket).

**How this was produced.** Five read-only investigators (web app, database contract, rulebook + tickets,
runtime, the question set), three independent designs, three judges, one synthesis, one completeness
critic — 13 agents, every claim below carries a file:line or a live SQL result behind it in the run
transcript. The critic's findings are folded in and marked **(critic)** where they changed the design.

---

## 1. What it is

A **Team target** on the existing Ask Millie tool (`/admin/ask-millie?target=team`) that answers a staff
question from **everything in the Supabase warehouse, with no member gates**, by running a Claude tool
loop **inside `mds-digest-web` on Render** — not inside the n8n graph. The loop has three tools: a
read-only SQL tool on its own database role, a schema catalog, and an ungated semantic search over the
same warehouse. Every turn is attributed to the staff session that asked it, logged with every query it
ran, and rendered with that trail beside the answer.

Millie for members (the n8n workflow, prod `12wj6h1TWqb0d4Dq`) is **not touched**. The leak gate proves
the WhatsApp, member and anonymous paths gain nothing.

## 2. Why not "Millie with the gates off"

Millie answers from about twenty fixed functions, each a named column set; a question about a field no
function selects cannot be answered, by design (`OLIVIA_SHAREABLE_FIELDS.md`, "never-by-construction").
"Like asking Claude" needs a query tool that composes what nobody wrote in advance, ten to forty tool
calls with reasoning between them, and minutes of wall time. n8n Cloud cannot host that: a Code node dies
at 60 s, the webhook is cut at ~100 s, and the web door's own route aborts at 85 s. So the research loop
is a **second runtime beside Millie**, reusing her door's identity, her log table and her UI.

## 3. Architecture

```
browser  /admin/ask-millie?target=team
   │  POST /api/admin/millie/research  { text, thread_id, ack_at }     (staff cookie)
   ▼
route.ts  gate → budget → insert 2 log rows → loop → NDJSON stream (hb every 10 s) → final PATCH
   │
loop.ts   claude-sonnet-5, manual messages.stream() tool loop, caps 15 laps / 8 min / 8k out
   │            ├── sql_query        → sbRequest('rpc/team_sql')   runs AS millie_team_ro, read-only txn
   │            ├── schema_catalog   → static module (no I/O)
   │            └── semantic_search  → Voyage embed → rpc/team_sql  pgvector <=> over content_items etc.
   ▼
digest.olivia_web_messages   mode='team' · asker_email = session · sources = the trail · metrics = cost
```

**Request path.** `readSessionCookie()` → `isStaffEmail()` → email ∈ `MILLIE_TEAM_ASKERS` (fail-closed:
unset = nobody) → per-asker daily budget (turns and USD, from the log table) → thread mode guard (a
`thread_id` whose rows are not `mode='team'` is refused) → two rows inserted before the loop (question +
answer placeholder) → the loop streams NDJSON events (`started`, `tool_call`, `tool_result`, `text`,
`answer`, `done`, `hb`) → after every tool result the answer row's `sources`/`plan` are PATCHed (a deploy
that kills the turn leaves a visible partial trail) → the final PATCH writes `answer_md` (with the
code-computed "Data as of" footer), `metrics` (tokens, cost, laps, wall, cut reason, transport), `model`,
`latency_ms`, `notes`.

**Transport.** Streaming has no precedent in this app and nothing has ever been observed completing after
~125 s through `digest.mds.co`. Milestone A measures it with a throwaway heartbeat route. If a
heartbeat-only stream holds ≥ 300 s: stream. If not: the route returns `{turn_id, poll:true}` at once, the
loop continues as a detached promise, per-lap PATCHes persist the trail, and the client polls the existing
`GET /api/admin/millie/chat?thread_id=` every 2 s. Same rows, same UI.

## 4. Tools

| tool | what | safety |
|---|---|---|
| `sql_query(sql, max_rows≤200)` | one SELECT/WITH over schemas `digest` + `event`; returns rows, `row_count`, `ms`, `truncated`, or the verbatim Postgres error so the model can repair the query | runs as **`millie_team_ro`** inside `digest.team_sql` (SECURITY DEFINER, owner = the role): `transaction_read_only` forced on, LIMIT wrapper, second statement = syntax error, SELECT-only privileges, no `pg_read_all_data`, USAGE on `digest`/`event`/`extensions` only |
| `schema_catalog(table?, search?)` | the curated description of one table, or a search over column and `at_fields` key names | static module, names and comments only |
| `semantic_search(query, sources?, limit≤40)` | Voyage `voyage-3.5-lite` (1024) embeds the query — the same call `api/olivia/kb/route.ts` makes — then a fixed SQL over `content_items` / `videos_catalog` / `partners_catalog` ordered by `embedding <=> $vec`, run through `team_sql` | ungated by design (Team mode), Supabase only, no member principal; degrades to a visible "vector lane OFF" flag when `VOYAGE_API_KEY` is absent, and the model falls back to `search_tsv` full-text in `sql_query` |

**(critic) `ask_millie` is out.** It would have run every call as a prod n8n execution on the probe
member — firing `Touch Olivia Stats` and reachable to `Mark Welcomed`, burning the shared n8n quota, and
returning member-gated evidence in a mode whose whole point is no gates. The semantic layer is served
ungated by `semantic_search` + full-text instead. Typed wrappers for the `p_phone` functions are deferred
for the same reason: they gate inside.

## 5. Identity, logging, budget

- **Asker = the session, always.** Cookie `mds_digest_session` (HS256, issued after the OTP ticket) →
  `isStaffEmail` (`@mds.co`) → `config.millie.teamAskers` allowlist parsed as `(env || "").split(",")…
  filter(Boolean)` so an unset variable is an **empty list and a 403 for everyone**. `ADMIN_EMAILS` /
  `checkAdminAccess()` stay unused: they read Airtable.
- **Every turn = two rows** in `digest.olivia_web_messages` (`mode='team'`, `target='prod'`, `route=
  'team-research'`), written with the service key: the member row before the loop, the olivia row as a
  placeholder then PATCHed per lap and at the end. The trail the screen shows **is** the `sources` array
  of that row (byte-equal is an acceptance check). Nothing is written to `digest.olivia_messages`, no
  wamid is minted, no `member_events` trigger fires — the daily review never sees Team traffic.
- **(critic) Per-asker daily budget**, enforced before a turn starts: `MILLIE_TEAM_DAILY_TURNS` (default
  40) and `MILLIE_TEAM_DAILY_USD` (default 10) summed from today's `metrics.cost_usd` for that email;
  over either → 429 with the numbers.
- **Disclaimer.** The amber notice from the design pack ("Unrestricted — MDS team only … Never paste it
  anywhere outside the team.") with **I understand**, composer locked until acknowledged, once per browser
  session; the acknowledgement time is stamped `ack:<iso>` into the first Team turn's `notes`. The copy
  button reads **Copy (internal)**. Switching target inside a thread that has answers mints a new thread
  (client), and the route refuses a thread whose rows are not `mode='team'` (server).

## 6. Safety model — in SQL and roles, not in the prompt

1. **The role.** `millie_team_ro` NOLOGIN, BYPASSRLS (33 `digest` tables have RLS on with zero
   policies, so a non-bypass role would read zero rows silently — live 2026-09-10: PG 17.6, `postgres`
   holds CREATEROLE + BYPASSRLS, so this is expected to succeed; a policies fallback is pre-written).
   USAGE on `digest`, `event`, `extensions`. SELECT on every table and view in `digest`/`event` **except**:
   `digest.olivia_web_messages` (no privilege at all — staff must not read other askers' Team answers
   through the tool), `digest.members` (column list omitting `otp_code_hash`, `delivery_otp_hash`), and
   `digest.member_profiles` (no table grant; see 2). No `pg_read_all_data`. No EXECUTE grants beyond what
   PUBLIC already holds.
2. **(critic) The deny-list view is structural, from day one.** `digest.member_profiles_team` = every
   column of `member_profiles` with `at_fields` filtered to drop keys matching
   `removal | reason | ltv | score ?card | member score | notes | lead scor | budget` — the 🔴 items #172
   never opened (removal reasons, LTV, internal notes, lead scoring). The three categories #172 does open
   (exact revenue, contact details, Stripe/billing) stay. The role reads the view, never the table. This
   is #172 AC 4's "Team mode column", written as a view rather than a prompt rule.
3. **(critic) Views run as their owner** and bypass table grants, so a gate check scans every view the
   role can read for `otp_code_hash`, `delivery_otp_hash`, `olivia_web_messages` — none today, and a future
   one goes red.
4. **`digest.team_sql`** owned by the role, `REVOKE ALL FROM PUBLIC`, `GRANT EXECUTE TO service_role`
   only. Body: `set_config('transaction_read_only','on',true)` → SELECT-only regex pre-check → `EXECUTE
   format('select coalesce(jsonb_agg(t),''[]'') from (select * from (%s) q limit %s) t', …)`. The read-only
   transaction is what neutralises the 31 PUBLIC-executable functions the role inherits (some are
   SECURITY DEFINER writers). Whether `set_config` binds inside a PostgREST transaction is **unverified
   (critic)** — it is the first Milestone A check and a merge blocker: `INSERT` → SQLSTATE `25006`.
5. **Unreachable from WhatsApp/member/anon (#172 AC 2).** `team_sql` is service_role-only, so the
   PUBLIC hole cannot reach it; the route accepts only the staff cookie (n8n cannot hold one); no n8n
   node changes, no function body changes. Gate checks pin: ACL, owner, role grants, the live read-only
   error, "neither workflow export contains `team_sql` or `/api/admin/millie/research`", and the prod
   workflow hash equals the pre-ticket snapshot.
6. **(critic) Supabase only, proven at runtime.** A static "no import of `@/lib/airtable` under
   `src/lib/millie/team/**`" is vacuous (`supabase.ts` itself imports it). The loop test stubs global
   `fetch`, runs a whole Team turn with a fake Anthropic client and a fake `team_sql`, and asserts zero
   requests to `api.airtable.com`.
7. **Two code guards on the answer, never the model's job:** the "Data as of" footer from one fixed
   query (max `synced_at` / `created_time` / `sent_at` of the four live mirrors), and a `no_rows` flag +
   visible warning when an answer carries numbers or a list but no query returned rows — the "a timeout
   looks like no data" trap made visible.

## 7. Cost and latency (estimates until Milestone A measures them)

Sonnet 5 ($2 / $10 per MTok, cache read ≈ $0.20, write ≈ $2.50), thinking off by default, system prompt
≈ 6–9k tokens (catalog index + rules) cached from lap 2 — `cache_read_input_tokens > 0` on lap 2 is an
acceptance check for every multi-lap turn. Typical turn ≈ $0.08, heavy ≈ $0.25, ceiling ≈ $0.50 at the
15-lap cap — 4–12× a member answer, now measured per row. Latency p50 ≈ 45–90 s, p95 ≈ 3–5 min, wall cap
8 min. The effective SQL cap is service_role's 60 s statement_timeout; the Supabase HTTP edge's own cap
for a long RPC is **unread (critic)** and is measured in Milestone A with `pg_sleep(55)`.

## 8. The proof — two milestones, numbers before opinions

**Milestone A — "is it doable", half a day, no UI.** (1) The migration on prod + nine curl checks
through `/rest/v1/rpc/team_sql` (count = 5,759 members; INSERT → 25006; a writer function → error;
`select 1; select 2` → syntax error; `vault`/`auth` → 42501; `otp_code_hash` → 42501;
`olivia_web_messages` → 42501; `pg_sleep(55)` → the recorded cut; anon key → 401/403). (2) A throwaway
heartbeat route merged and read with `curl -N` through `digest.mds.co`: heartbeat 300 s, heartbeat 600 s,
silent 180 s. (3) A local Node script (installed SDK 0.100.1, `claude-sonnet-5`, `sql_query` only,
catalog v0) answers Q1, Q4, Q9, Q18, Q20 against reference SELECTs frozen in the same minute, recording
laps, wall, cost and `cache_read` on lap 2. **Doable =** 9/9 checks, heartbeat ≥ 300 s, ≥ 4/5 exact,
Q18 and Q20 answered via SQL, cache hit on lap 2, p50 < 90 s, mean cost < $0.30. Any miss names its
fallback (policies variant, poll transport, LOGIN role) before a line of route code is written.

**Milestone B — the tool, two days.** Route + loop + tools + log + client + catalog v1 + gate checks +
docs, then the twenty questions (`Q1–Q20`, drafted from the shapes staff and members actually ask;
**(critic)** two or three staff validate them on Day 0 and every swap is recorded) scored against
reference SELECTs frozen in the same minute: mechanical layer for counts/sets/top-N, four judges +
hand re-verification for the semantic three (Q11–Q13). **Bar:** PASS ≥ 16/20 · Q18, Q19, Q20 PASS via
`sql_query` (the #172 headline: succeeds where every gated function would refuse) · 0 fabricated
sources · every logged query re-executes · 20/20 turns logged with asker, cost, laps · cache hit on lap 2
· p50 < 90 s · p95 < 5 min · mean cost < $0.30. Proof artefacts carry member data and stay outside git.

## 9. Day 0 — what only Andy can do (each is minutes)

1. **The migration go.** SQL is live on prod the moment it is applied; role + view + `team_sql` + grants
   in one file, `CREATE OR REPLACE` only.
2. **(critic) The rulebook ruling in writing:** Team mode reads through a read-only SQL surface over the
   deny-list view instead of fixed column sets. `OLIVIA_SHAREABLE_FIELDS.md` gains the Team column: the
   three categories open; removal reasons, LTV, internal notes, lead scoring stay closed by the view.
3. **Render env, check-before-add, then Manual Deploy:** `MILLIE_TEAM_ASKERS` (the proof participants),
   `VOYAGE_API_KEY` (present in `api/olivia/kb` code, presence on Render unknown), `NODE_VERSION` pinned
   (nothing pins Node today; local is 25, Render's default depends on service age).
4. **Placeholders** for Q1–Q3, Q14, Q17–Q19 (a member, an event), sent outside the repo.
5. **Two or three staff** read the twenty questions and swap the ones they would never ask.

## 10. Deferred, with the trigger that would bring each back

Typed wrappers for `p_phone` functions (trigger: a semantic question `semantic_search` + FTS cannot
answer) · a durable job runner / Render Background Worker + `pg` driver (trigger: cut turns in the proof)
· per-user persistent acknowledgement (trigger: Andy asks for it) · a child table for per-step trails
(trigger: `sources` jsonb exceeds ~200 KB on a real turn) · a research-only PostgREST role/JWT separate
from service_role (trigger: the MCP door) · **the MCP door itself** — the same principal on a second
transport, filed as its own ticket after Milestone B · Public mode switching to the team principal
(#172's last sentence) — it changes the Public Gate's inputs and gets its own ticket.

## 11. Side findings filed as their own tickets, not chased here

31 of 138 `digest` functions are EXECUTE-able by anon/authenticated, including SECURITY DEFINER writers
(`content_delete_*`, `content_ingest_*`, `olivia_front_door_v2`) while PostgREST exposes `digest` ·
`db/README.md` says 104 functions, `db/` holds 138 · `db/rls.sql` lists 40 RLS tables, live has 33 ·
the "before Vercel cuts us" comment in `chat/route.ts` is stale (the app is on Render).
