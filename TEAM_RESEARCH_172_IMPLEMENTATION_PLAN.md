# #172 Team Research Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Team target on Ask Millie that answers any staff question over the Supabase warehouse with no member gates, through a Claude tool loop with a read-only SQL tool, a schema catalog and an ungated semantic search, attributed to the staff session and logged with every query it ran.

**Architecture:** One new Next.js route in `mds-digest-web` (`POST /api/admin/millie/research`) runs the loop in-process and streams NDJSON (poll fallback decided by a live probe). One migration in the Scorecard repo creates a NOLOGIN read-only role, a deny-list view over `member_profiles`, and `digest.team_sql`, a SECURITY DEFINER RPC owned by that role that forces a read-only transaction. Millie's n8n workflow is not edited; the leak gate proves it.

**Tech Stack:** Next 16.2.4 / React 19 / TypeScript / vitest 4 (`npm test`) in `mds-digest-web`; `@anthropic-ai/sdk` 0.100.1 (`claude-sonnet-5`); PostgreSQL 17.6 on Supabase (`nadtudwuwjhckotrngzn`) reached only through PostgREST with `SUPABASE_SECRET_KEY`; pgvector 0.8; Voyage `voyage-3.5-lite` (1024); Python 3 for the Scorecard-side checks and the leak gate.

## Global Constraints

- **Two repos, two branches, never `main`.** Scorecard: `git fetch origin && git switch -c 172-team-research-<yyyymmdd> origin/main` (or a worktree under `.claude/worktrees/`). `mds-digest-web`: same pattern; **a merge to `main` there IS the deploy — there is no staging tier.** Sequence merges between proof runs: a deploy kills in-flight turns.
- **SQL is live on prod the moment it is applied.** `CREATE OR REPLACE` only, never `DROP` (DROP discards the ACL). After ANY migration: `python3 scripts/db_export_schema.py`, commit `db/`.
- **The leak gate must be GREEN before anything ships**, read by exit code: `python3 scripts/olivia_leak_gate.py; echo EXIT=$?` — never `| tail`.
- **Never edit the n8n workflows** (`12wj6h1TWqb0d4Dq` prod, `bqHstPDi84uOhTCJ` staging) in this ticket. A gate check pins the prod graph hash.
- **Supabase only.** Nothing under `src/lib/millie/team/**` or the route may call Airtable; a runtime fetch spy asserts it.
- **The asker is always the session cookie**, never the request body. `MILLIE_TEAM_ASKERS` unset = 403 for everyone.
- **Render env vars: CHECK before add, then Manual Deploy → Deploy latest commit** (saving an env var does not reliably redeploy).
- **Anthropic key name is `CENTURION_ANTHROPIC_API_KEY`** (never bare `ANTHROPIC_API_KEY`). Model id `claude-sonnet-5`, no date suffix. Thinking OFF by default.
- **Proof artefacts carry member data**: references, answers and filled placeholders stay outside git and off ClickUp. Only numbers go on the board.
- **Docs ride the same branch as the work**: `OLIVIA_SPRINT_4.md` (#172 block), `OLIVIA_HANDBOOK.md` §3 / §4.3 / §6.2 / §11, `OLIVIA_SHAREABLE_FIELDS.md` (Team column), `SESSION_LOG_OLIVIA.md` + one line in `SESSION_LOG.md`.
- **Day 0 (Andy) gates Milestone A:** migration go · rulebook ruling · Render env (`MILLIE_TEAM_ASKERS`, `VOYAGE_API_KEY`, `NODE_VERSION`) · placeholders · two-three staff validate the twenty questions. See `TEAM_RESEARCH_172_DESIGN.md` §9.

---

## File structure

**Scorecard repo (`/Users/Born/Scorecard`, branch `172-team-research-<yyyymmdd>`)**
- Create `scripts/sql/20260911_team_sql_172.sql` — role, grants, deny-list view, `digest.team_sql`. One file, idempotent.
- Create `scripts/sql/20260911_team_sql_172_policies_fallback.sql` — variant (b) if `CREATE ROLE … BYPASSRLS` is refused.
- Create `scripts/test_172_team_sql.py` — the nine behavioural checks against the live RPC (Milestone A gate).
- Modify `scripts/olivia_leak_gate.py` — section "— #172 team research —" with seven checks.
- Regenerate `db/` (`db/functions/team_sql.sql`, `db/views/member_profiles_team.sql`, `db/grants.sql`, `db/rls.sql`).
- Modify the docs listed in Global Constraints.

**`mds-digest-web` (`/Users/Born/mds-digest-web`, branch `172-team-research-<yyyymmdd>`)**
- Modify `package.json` — `engines.node`.
- Modify `src/lib/config.ts` — `millie.teamAskers`, `millie.teamDailyTurns`, `millie.teamDailyUsd`, `millie.voyageApiKey`.
- Create `src/app/api/admin/millie/research/probe/route.ts` — Milestone A throwaway heartbeat route; deleted in the Milestone B merge.
- Create `src/lib/millie/team/sql-guard.ts` (+ `.test.ts`) — pure SELECT-only pre-check.
- Create `src/lib/millie/team/pricing.ts` (+ `.test.ts`) — usage → USD.
- Create `src/lib/millie/team/catalog.generated.json` + `scripts/gen-team-catalog.mjs` — generated table/column index from `information_schema` + comments.
- Create `src/lib/millie/team/catalog.ts` (+ `.test.ts`) — rules block + index + `describeTable()` / `searchCatalog()`.
- Create `src/lib/millie/team/tools.ts` (+ `.test.ts`) — tool definitions and runners: `sql_query`, `schema_catalog`, `semantic_search`.
- Create `src/lib/millie/team/log.ts` (+ `.test.ts`) — the two rows, per-lap and final PATCH, daily budget read.
- Create `src/lib/millie/team/loop.ts` (+ `.test.ts`) — the tool loop with injected client, caps, events, cache layout.
- Create `src/lib/millie/team/footer.ts` (+ `.test.ts`) — "Data as of" + `no_rows`.
- Create `src/lib/millie/team/gate.ts` (+ `.test.ts`) — pure request gate (session → staff → allowlist → budget → thread mode).
- Create `src/app/api/admin/millie/research/route.ts` — the route.
- Modify `src/components/tools/ask-millie/chat-model.ts` (+ `.test.ts`) — NDJSON event parsing, trail shaping.
- Create `src/components/tools/ask-millie/Trail.tsx` — the "Queries run" panel.
- Modify `src/components/tools/ask-millie/AskMillie.tsx` — Team unlock, research fetch, stream reader, poll fallback, trail.
- Modify `src/lib/tools/ask-millie-help.ts` — the Team section.
- Modify `src/app/api/admin/millie/chat/route.ts` — comment only: the 400 for `team` stays (Team never goes through the n8n door).

**Outside git**
- `~/mds-team-proof/questions.json`, `references/`, `runs/` — the twenty questions with placeholders, frozen reference SELECTs, turn captures.

---

# Milestone A — "Is it doable" (half a day, no UI)

### Task A1: The migration and its behavioural checks

**Files:**
- Create: `scripts/sql/20260911_team_sql_172.sql`
- Create: `scripts/sql/20260911_team_sql_172_policies_fallback.sql`
- Create: `scripts/test_172_team_sql.py`

**Interfaces:**
- Produces: `digest.team_sql(p_sql text, p_max_rows int default 200) returns jsonb` — `{rows: [...], row_count: n, truncated: bool}` on success; on failure PostgREST returns HTTP 400 with `{code, message, details, hint}` (the verbatim Postgres error). Role `millie_team_ro`. View `digest.member_profiles_team`.

- [x] **Step 1: Write the failing check script**

```python
#!/usr/bin/env python3
"""#172 team_sql contract — `python3 scripts/test_172_team_sql.py`.

Nine live checks through PostgREST with the service key against digest.team_sql, the
read-only SQL surface of Team research mode. Every one is a security property or a
trap the design named; the first run (before the migration) must fail on all nine.
"""
import json, subprocess, sys, time

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")
ANON = env("SUPABASE_ANON_KEY") if any(l.startswith("SUPABASE_ANON_KEY=") for l in open(ENV)) else ""


def team_sql(sql, key=KEY, max_rows=200, timeout=90):
    t0 = time.time()
    p = subprocess.run(
        ["curl", "-sS", "-m", str(timeout), "-w", "\n%{http_code}", "-X", "POST", f"{BASE}/rpc/team_sql",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
         "-H", "Content-Type: application/json",
         "--data-binary", json.dumps({"p_sql": sql, "p_max_rows": max_rows})],
        capture_output=True, text=True)
    raw, _, code = p.stdout.rpartition("\n")
    try:
        body = json.loads(raw) if raw.strip() else None
    except json.JSONDecodeError:
        body = raw[:300]
    return int(code or 0), body, round(time.time() - t0, 1)


fails = 0


def check(label, ok, detail):
    global fails
    if not ok:
        fails += 1
    print(f"{'ok  ' if ok else 'FAIL'}  {label}: {detail}")


st, b, _ = team_sql("select count(*) as n from digest.member_attributes")
check("1 reads a table (member_attributes count)", st == 200 and isinstance(b, dict) and b.get("rows", [{}])[0].get("n") == 5759, f"{st} {str(b)[:120]}")

st, b, _ = team_sql("insert into digest.chats(chat_id, chat_name) values ('gate-172','gate-172')")
msg = json.dumps(b) if b else ""
check("2 INSERT is refused by the read-only transaction (25006) or by privilege (42501)", st == 400 and ("25006" in msg or "42501" in msg), f"{st} {msg[:160]}")

st, b, _ = team_sql("select * from digest.content_delete_summary(-1)")
msg = json.dumps(b) if b else ""
check("3 a PUBLIC-executable writer function cannot write through the tool", st == 400, f"{st} {msg[:160]}")

st, b, _ = team_sql("select 1; select 2")
check("4 a second statement is a syntax error", st == 400, f"{st} {json.dumps(b)[:120] if b else ''}")

st, b, _ = team_sql("select * from vault.decrypted_secrets limit 1")
msg = json.dumps(b) if b else ""
check("5 vault is dark (42501 or 3F000)", st == 400 and ("42501" in msg or "3F000" in msg), f"{st} {msg[:120]}")

st, b, _ = team_sql("select otp_code_hash from digest.members limit 1")
msg = json.dumps(b) if b else ""
check("6 OTP hash columns are dark (42501)", st == 400 and "42501" in msg, f"{st} {msg[:120]}")

st, b, _ = team_sql("select id from digest.olivia_web_messages limit 1")
msg = json.dumps(b) if b else ""
check("7 olivia_web_messages is dark (42501)", st == 400 and "42501" in msg, f"{st} {msg[:120]}")

st, b, secs = team_sql("select pg_sleep(55), 1 as one", timeout=120)
print(f"      pg_sleep(55) → HTTP {st} after {secs}s (records the HTTP-edge cap; 200 or a timeout are both facts)")
check("8 a long query is either answered or cut with an HTTP status, never silent", st != 0, f"{st}")

st, b, _ = team_sql("select 1 as one", key=ANON or "x")
check("9 anon key is refused", st in (401, 403, 404), f"{st}")

st, b, _ = team_sql("select at_member_id from digest.member_profiles limit 1")
msg = json.dumps(b) if b else ""
check("10 member_profiles TABLE is dark; the view is the door", st == 400 and "42501" in msg, f"{st} {msg[:120]}")

st, b, _ = team_sql("select count(*) as n from digest.member_profiles_team where at_fields ? 'Removal Reason'")
check("11 the deny-list view drops 'Removal Reason' from at_fields", st == 200 and b.get("rows", [{}])[0].get("n") == 0, f"{st} {str(b)[:120]}")

st, b, _ = team_sql("select count(*) as n from digest.member_profiles_team where at_fields ? 'Most Recent Revenue'")
check("12 the deny-list view keeps 'Most Recent Revenue' (the category #172 opens)", st == 200 and (b.get("rows", [{}])[0].get("n") or 0) > 900, f"{st} {str(b)[:120]}")

st, b, _ = team_sql("select id from digest.content_items order by id limit 500", max_rows=200)
check("13 LIMIT wrapper: 500 asked, 200 returned, truncated=true", st == 200 and b.get("row_count") == 200 and b.get("truncated") is True, f"{st} {str(b)[:80]}")

print("all green" if not fails else f"{fails} failing")
sys.exit(1 if fails else 0)
```

- [x] **Step 2: Run it to verify it fails**

Run: `python3 scripts/test_172_team_sql.py; echo EXIT=$?`
Expected: every check FAIL with HTTP 404 (`Could not find the function digest.team_sql`) and `EXIT=1`.

- [x] **Step 3: Write the migration**

```sql
-- scripts/sql/20260911_team_sql_172.sql  (#172 Team research mode — the read-only SQL surface)
--
-- Andy 2026-09-10: staff get answers to ANY question over the warehouse, no member gates, Supabase only.
-- That needs a query tool nobody wrote in advance. Its safety lives HERE, in a role and a function, never
-- in a prompt: a NOLOGIN read-only role, a SECURITY DEFINER runner OWNED by that role that forces a
-- read-only transaction, a deny-list view over member_profiles so the 🔴 items #172 never opened
-- (removal reasons, LTV, internal notes, lead scoring) cannot be selected, and no privilege at all on
-- olivia_web_messages (other askers' Team answers) or the two OTP hash columns.
--
-- Idempotent. CREATE OR REPLACE only (DROP discards the ACL). Live on prod the moment it is applied.
-- Re-export db/ afterwards: python3 scripts/db_export_schema.py

-- 1. the role. BYPASSRLS because 33 digest tables have RLS ON with ZERO policies: a non-bypass role would
--    read zero rows silently, and a timeout/empty result looks exactly like "no data". Live 2026-09-10:
--    PG 17.6, postgres holds CREATEROLE + BYPASSRLS, so a CREATEROLE role may grant an attribute it holds.
--    If this statement is refused, apply 20260911_team_sql_172_policies_fallback.sql instead of it.
do $do$
begin
  if not exists (select 1 from pg_roles where rolname = 'millie_team_ro') then
    create role millie_team_ro nologin bypassrls;
  end if;
end $do$;

-- postgres must be a member to hand the function to the role (PG16+: membership WITH SET).
grant millie_team_ro to postgres with set true;

grant usage on schema digest, event, extensions to millie_team_ro;

-- 2. what the role may read: everything in digest + event ...
grant select on all tables in schema digest to millie_team_ro;
grant select on all tables in schema event to millie_team_ro;
-- ... except: other askers' Team answers, the raw member_profiles table (the view below is the door),
--     and the two OTP hash columns on members (column-list grant generated from the live column set).
revoke all on digest.olivia_web_messages from millie_team_ro;
revoke all on digest.member_profiles from millie_team_ro;
revoke all on digest.members from millie_team_ro;
do $do$
declare cols text;
begin
  select string_agg(quote_ident(column_name), ', ' order by ordinal_position) into cols
  from information_schema.columns
  where table_schema = 'digest' and table_name = 'members'
    and column_name not in ('otp_code_hash', 'delivery_otp_hash');
  execute format('grant select (%s) on digest.members to millie_team_ro', cols);
end $do$;

-- 3. the deny-list view (#172 AC 4, the "Team mode column", as SQL not prose). Keeps the three categories
--    #172 opens — exact revenue, contact details, Stripe/billing — and drops the at_fields keys that stay
--    closed. Runs as its owner (postgres), which is why the role needs no grant on the table itself.
create or replace view digest.member_profiles_team as
select
  p.at_member_id, p.full_name, p.email, p.status, p.plan_name, p.subscription_status, p.subscription_started,
  p.join_date, p.paid_date, p.next_renewal, p.next_renewal_amount, p.scheduled_cancel, p.collection_paused,
  p.mrr, p.membership_fee, p.billing_cycle, p.stripe_customer_id, p.stripe_subscription_id,
  p.engagement_score, p.score_breakdown, p.score_updated,
  (select coalesce(jsonb_object_agg(e.k, e.v), '{}'::jsonb)
     from jsonb_each(coalesce(p.at_fields, '{}'::jsonb)) as e(k, v)
    where e.k !~* '(removal|reason|ltv|score ?card|member score|notes|lead scor|budget)') as at_fields,
  p.application, p.application_at, p.synced_at, p.application_form,
  p.lifetime_paid, p.lifetime_paid_first_payment, p.lifetime_paid_payments, p.lifetime_paid_synced_at,
  p.rough_benchmark_paid, p.lifetime_paid_vs_benchmark_pct
from digest.member_profiles p;
comment on view digest.member_profiles_team is
  '#172 Team research: member_profiles with the at_fields keys that stay closed in Team mode removed (removal reasons, LTV, internal notes, lead scoring). The read-only role reads this, never the table.';
grant select on digest.member_profiles_team to millie_team_ro;

-- 4. the runner. SECURITY DEFINER + OWNER millie_team_ro = the body runs AS the read-only role.
--    transaction_read_only is forced for the rest of the PostgREST transaction so that even a
--    PUBLIC-executable SECURITY DEFINER writer (31 such functions exist today) cannot write from inside
--    a query. The LIMIT wrapper makes a second statement a syntax error and bounds the payload.
create or replace function digest.team_sql(p_sql text, p_max_rows integer default 200)
returns jsonb
language plpgsql
security definer
set search_path to 'digest', 'event', 'pg_temp'
as $function$
declare
  v_cap integer := greatest(1, least(coalesce(p_max_rows, 200), 500));
  v_rows jsonb;
  v_n integer;
begin
  perform set_config('transaction_read_only', 'on', true);
  perform set_config('statement_timeout', '55000', true);
  if p_sql is null or p_sql !~* '^\s*(select|with|values)\M' then
    raise exception 'team_sql: only a single SELECT / WITH / VALUES statement is allowed'
      using errcode = '42501';
  end if;
  execute format(
    'select coalesce(jsonb_agg(t), ''[]''::jsonb) from (select * from (%s) q limit %s) t',
    rtrim(p_sql, E' \n\t;'), v_cap + 1
  ) into v_rows;
  v_n := jsonb_array_length(v_rows);
  return jsonb_build_object(
    'rows', case when v_n > v_cap
                 then (select coalesce(jsonb_agg(e), '[]'::jsonb)
                         from (select e from jsonb_array_elements(v_rows) with ordinality as x(e, i)
                               where x.i <= v_cap) s)
                 else v_rows end,
    'row_count', least(v_n, v_cap),
    'truncated', v_n > v_cap
  );
end
$function$;

alter function digest.team_sql(text, integer) owner to millie_team_ro;
revoke all on function digest.team_sql(text, integer) from public;
grant execute on function digest.team_sql(text, integer) to service_role;
comment on function digest.team_sql(text, integer) is
  '#172 Team research: one read-only SELECT over digest+event as millie_team_ro, LIMIT-wrapped, read-only transaction forced. service_role only. Returns {rows,row_count,truncated}.';

notify pgrst, 'reload schema';
```

- [x] **Step 4: Write the fallback (only applied if Step 5 refuses `BYPASSRLS`)**

```sql
-- scripts/sql/20260911_team_sql_172_policies_fallback.sql
-- Variant (b): the role without BYPASSRLS plus one permissive SELECT policy per RLS-enabled table,
-- enumerated from pg_class at apply time (live: 33 digest tables, 0 event tables — never hard-code).
-- Apply INSTEAD of section 1 of the main file, then the main file's sections 2-4.
do $do$
declare r record;
begin
  if not exists (select 1 from pg_roles where rolname = 'millie_team_ro') then
    create role millie_team_ro nologin;
  end if;
  for r in
    select n.nspname, c.relname
    from pg_class c join pg_namespace n on n.oid = c.relnamespace
    where c.relkind = 'r' and c.relrowsecurity and n.nspname in ('digest', 'event')
  loop
    execute format('drop policy if exists team_ro_read on %I.%I', r.nspname, r.relname);
    execute format('create policy team_ro_read on %I.%I for select to millie_team_ro using (true)', r.nspname, r.relname);
  end loop;
end $do$;
```

- [x] **Step 5: Apply the migration to prod** (Andy's Day-0 go in hand). Through the Supabase MCP `execute_sql` or `psql` if a DSN exists — paste the file's contents as one statement batch. If `create role … bypassrls` errors, apply the fallback file first, then re-run the main file (its `do` block skips the existing role).

- [x] **Step 6: Run the check script to verify it passes**

Run: `python3 scripts/test_172_team_sql.py; echo EXIT=$?`
Expected: checks 1–7 and 9–13 `ok`; check 8 prints the observed HTTP status and seconds for `pg_sleep(55)` — **write that number into the session log**; `EXIT=0`. If check 2 fails with a write succeeding, STOP: the read-only forcing does not bind inside PostgREST's transaction — escalate to Andy with the fallback (a LOGIN role with `rolconfig default_transaction_read_only=on` reached over a direct connection, which is the agent-service design), and do not proceed to the route.

- [x] **Step 7: Re-export the schema and commit**

```bash
python3 scripts/db_export_schema.py
git add scripts/sql/20260911_team_sql_172.sql scripts/sql/20260911_team_sql_172_policies_fallback.sql scripts/test_172_team_sql.py db/
git commit -m "#172: millie_team_ro, member_profiles_team, digest.team_sql — the read-only SQL surface, proven live"
```

### Task A2: Seven leak-gate checks

**Files:**
- Modify: `scripts/olivia_leak_gate.py` (append a section before the final `print()` / `if failures:` block at the tail)

**Interfaces:**
- Consumes: `check(name, ok, detail)`, `curl(method, url, key, body, profile_hdr)`, `rpc(fn, params, key)`, `load_env()`, `key`, `ANON_KEY`, `BASE` — all already defined in the gate.

- [x] **Step 1: Add the section (it must FAIL against a database without the migration — run it once on a branch checkout that points at a fresh snapshot is not possible, so the negative controls below are the proof the checks bite: each check has a control that asserts the *opposite* privilege on a role that must hold it)**

```python
    # ---------------------------------------------------------------------------------------------
    # 15. #172 Team research mode: the read-only SQL surface is service_role-only, runs as
    #     millie_team_ro, cannot write, cannot see OTP hashes or other askers' Team answers, and the
    #     WhatsApp graph is byte-identical to the pre-ticket snapshot. Every positive check has a
    #     negative control so a wrong query cannot pass by accident.
    # ---------------------------------------------------------------------------------------------
    print()
    print("— #172 team research: read-only surface, role reach, graph untouched —")
    st, _b = rpc("team_sql", {"p_sql": "select 1 as one"}, ANON_KEY)
    check("#172 anon denied on team_sql", st in (401, 403, 404), f"status {st}")
    st, _b = rpc("team_sql", {"p_sql": "select 1 as one"}, key)
    check("#172 service_role executes team_sql (control)", st == 200 and isinstance(_b, dict) and _b.get("row_count") == 1, f"status {st} body {str(_b)[:80]}")
    st, _b = rpc("team_sql", {"p_sql": "insert into digest.chats(chat_id, chat_name) values ('gate-172','gate-172')"}, key)
    _msg = json.dumps(_b) if _b else ""
    check("#172 team_sql refuses a write (25006 read-only or 42501)", st == 400 and ("25006" in _msg or "42501" in _msg), f"status {st} {_msg[:120]}")
    st, _b = rpc("team_sql", {"p_sql": "select 1; select 2"}, key)
    check("#172 team_sql refuses a second statement", st == 400, f"status {st}")
    st, _b = rpc("team_sql", {"p_sql": "select otp_code_hash from digest.members limit 1"}, key)
    check("#172 OTP hash columns are dark to the role", st == 400 and "42501" in (json.dumps(_b) if _b else ""), f"status {st}")
    st, _b = rpc("team_sql", {"p_sql": "select id from digest.olivia_web_messages limit 1"}, key)
    check("#172 olivia_web_messages is dark to the role", st == 400 and "42501" in (json.dumps(_b) if _b else ""), f"status {st}")
    st, _b = rpc("team_sql", {"p_sql": "select at_member_id from digest.member_profiles limit 1"}, key)
    check("#172 member_profiles TABLE is dark to the role (the deny-list view is the door)", st == 400 and "42501" in (json.dumps(_b) if _b else ""), f"status {st}")
    st, _b = rpc("team_sql", {"p_sql": "select count(*) as n from digest.member_profiles_team where at_fields ? 'Removal Reason' or at_fields ? 'Member LTV (Membership)'"}, key)
    check("#172 deny-list view carries no closed key", st == 200 and _b.get("rows", [{}])[0].get("n") == 0, f"status {st} {str(_b)[:80]}")
    # views run as their owner and bypass table grants: none the role can read may reference the dark things
    st, _v = rpc("team_sql", {"p_sql": "select schemaname||'.'||viewname as v from pg_views where schemaname in ('digest','event') and (definition ilike '%otp_code_hash%' or definition ilike '%delivery_otp_hash%' or definition ilike '%olivia_web_messages%')"}, key)
    check("#172 no readable view re-opens OTP hashes or olivia_web_messages", st == 200 and _v.get("row_count") == 0, f"status {st} rows {str(_v)[:120]}")
    st, _o = rpc("team_sql", {"p_sql": "select pg_get_userbyid(proowner) as owner, (select count(*) from aclexplode(proacl) a join pg_roles r on r.oid=a.grantee where r.rolname in ('anon','authenticated') or a.grantee=0) as public_grants from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='digest' and p.proname='team_sql'"}, key)
    _row = (_o or {}).get("rows", [{}])[0] if isinstance(_o, dict) else {}
    check("#172 team_sql is owned by millie_team_ro and holds no PUBLIC/anon/authenticated EXECUTE", st == 200 and _row.get("owner") == "millie_team_ro" and _row.get("public_grants") == 0, f"status {st} {_row}")
    # the WhatsApp graph is untouched: neither export mentions the new surface, and prod's hash equals the pre-ticket snapshot
    _n8n = load_env(); _snap_path = os.path.join(os.path.dirname(__file__), "..", "olivia_snapshots", "prod_pre_172.sha256")
    for _wid, _label in (("12wj6h1TWqb0d4Dq", "prod"), ("bqHstPDi84uOhTCJ", "staging")):
        _wf = subprocess.run(["curl", "-s", "-m", "60", f"{_n8n['N8N_API_URL'].rstrip('/')}/api/v1/workflows/{_wid}", "-H", f"X-N8N-API-KEY: {_n8n['N8N_API_KEY']}"], capture_output=True, text=True).stdout
        check(f"#172 {_label} workflow export contains neither team_sql nor the research route", "team_sql" not in _wf and "/api/admin/millie/research" not in _wf, "found a reference")
        if _label == "prod":
            try:
                _graph = json.loads(_wf); _canon = json.dumps({"nodes": _graph.get("nodes"), "connections": _graph.get("connections")}, sort_keys=True)
                _h = hashlib.sha256(_canon.encode()).hexdigest()
                _want = open(_snap_path).read().strip() if os.path.exists(_snap_path) else ""
                check("#172 prod graph hash equals the pre-ticket snapshot (olivia_snapshots/prod_pre_172.sha256)", _want != "" and _h == _want, f"live {_h[:12]} vs snapshot {_want[:12] or 'MISSING — write it with: python3 scripts/olivia_wf.py hash > olivia_snapshots/prod_pre_172.sha256'}")
            except (ValueError, TypeError) as _e:
                check("#172 prod graph hash equals the pre-ticket snapshot", False, f"could not hash the export: {_e!r}")
```

Add `import hashlib` and `import os` to the gate's imports if not already present (grep first: `grep -n "^import" scripts/olivia_leak_gate.py`).

- [x] **Step 2: Write the pre-ticket prod hash** (the snapshot the check compares against; taken BEFORE any other change this ticket makes)

```bash
python3 - <<'PY'
import json, hashlib, subprocess
env = {l.split('=',1)[0]: l.split('=',1)[1].strip().strip('"') for l in open('/Users/Born/mds-digest-web/.env.local') if '=' in l and not l.startswith('#')}
wf = subprocess.run(["curl","-s","-m","60",f"{env['N8N_API_URL'].rstrip('/')}/api/v1/workflows/12wj6h1TWqb0d4Dq","-H",f"X-N8N-API-KEY: {env['N8N_API_KEY']}"],capture_output=True,text=True).stdout
g = json.loads(wf); canon = json.dumps({"nodes": g["nodes"], "connections": g["connections"]}, sort_keys=True)
open('olivia_snapshots/prod_pre_172.sha256','w').write(hashlib.sha256(canon.encode()).hexdigest()+"\n"); print("written")
PY
```

- [x] **Step 3: Run the gate, exit code read directly**

Run: `python3 scripts/olivia_leak_gate.py > /tmp/gate172.txt 2>&1; echo EXIT=$?; grep -c "^  FAIL" /tmp/gate172.txt`
Expected: `EXIT=0`, `0` failures, the new section printing thirteen PASS lines (previous total 346 + 13).

- [x] **Step 4: Commit**

```bash
git add scripts/olivia_leak_gate.py olivia_snapshots/prod_pre_172.sha256
git commit -m "#172 gate: the read-only surface is service_role-only, runs as millie_team_ro, cannot write, and the WhatsApp graph is pinned"
```

### Task A3: Transport probe on Render

**Files:**
- Create: `src/app/api/admin/millie/research/probe/route.ts` (mds-digest-web; deleted in Milestone B's final merge)
- Modify: `package.json` (add `"engines": { "node": ">=22 <25" }`)

**Interfaces:**
- Produces: the three numbers the design needs — heartbeat stream held for N s, silent response held for M s, through `digest.mds.co`.

- [x] **Step 1: Write the probe route** (no test: throwaway, staff-cookie gated, measurement only)

```ts
// src/app/api/admin/millie/research/probe/route.ts — #172 Milestone A, THROWAWAY.
// Answers one question the repo cannot: does Render + its edge keep a slow response alive through
// digest.mds.co? ?secs=N streams one heartbeat line every 5 s for N seconds; ?shape=silent&secs=N
// sends nothing for N seconds then one line. Staff cookie only. Delete in the Milestone B merge.
import { NextRequest, NextResponse } from "next/server";
import { readSessionCookie } from "@/lib/session";
import { isStaffEmail } from "@/lib/staff-otp";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const sess = await readSessionCookie();
  const email = (sess?.email || "").trim().toLowerCase();
  if (!email || !isStaffEmail(email)) return NextResponse.json({ error: "forbidden" }, { status: 403 });
  const params = new URL(req.url).searchParams;
  const secs = Math.min(900, Math.max(5, Number(params.get("secs") || 300)));
  const silent = params.get("shape") === "silent";
  const enc = new TextEncoder();
  const started = Date.now();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const tick = () => {
        const t = Math.round((Date.now() - started) / 1000);
        if (t >= secs) { controller.enqueue(enc.encode(`{"done":true,"secs":${t}}\n`)); controller.close(); return; }
        if (!silent) controller.enqueue(enc.encode(`{"hb":${t}}\n`));
        setTimeout(tick, silent ? Math.min(1000, (secs - t) * 1000) : 5000);
      };
      controller.enqueue(enc.encode(`{"started":true,"secs":${secs},"shape":"${silent ? "silent" : "heartbeat"}"}\n`));
      setTimeout(tick, silent ? 1000 : 5000);
    },
  });
  return new Response(stream, { headers: { "Content-Type": "application/x-ndjson", "Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no" } });
}
```

- [x] **Step 2: Pin Node** — in `package.json` add `"engines": { "node": ">=22 <25" }`; in Render, Andy adds `NODE_VERSION=22` (check-before-add) and redeploys. Run `npm run build` locally to confirm the build is unaffected.

- [x] **Step 3: Merge to `main` (= deploy)** on `mds-digest-web`, then confirm `curl -s https://digest.mds.co/api/version` shows the new sha.

- [x] **Step 4: Measure through the real edge, with the real cookie** (export the staff cookie value from the browser's devtools once; never commit it)

```bash
COOKIE='mds_digest_session=<value>'
for spec in "secs=300" "secs=600" "shape=silent&secs=180"; do
  echo "== $spec"; ( time curl -sN -H "Cookie: $COOKIE" "https://digest.mds.co/api/admin/millie/research/probe?$spec" | tail -2 ) 2>&1 | tail -5
done
```

Also open `https://digest.mds.co/api/admin/millie/research/probe?secs=300` in the admin browser tab and confirm lines arrive progressively (the fetch reader through the admin layout is what the client will use).

- [x] **Step 5: Record the numbers** in `SESSION_LOG_OLIVIA.md` as "heartbeat stream held N s, silent held M s through digest.mds.co, browser reader progressive: yes/no". Decision rule: heartbeat ≥ 300 s → **stream** transport in Task B9; < 300 s → **poll** transport (Task B9's fallback branch becomes the primary path).

### Task A4: The five-question spike (throwaway, TDD exception — a prototype, per the skill's stated exception; nothing from it is kept)

**Files:**
- Create outside git: `~/mds-team-proof/spike.mjs`, `~/mds-team-proof/references/`

- [x] **Step 1: Write the spike** — a local Node script using the installed SDK from `mds-digest-web/node_modules`: system prompt = a first-cut rules block (the eight canonical rules in Task B4) + the table index for `member_attributes`, `member_profiles_team`, `members`, `events_catalog`, `event_registrations_live`, `wa_messages`, `content_items`, `calls`, `call_attendance`, `member_identity`; one tool `sql_query` calling `rpc/team_sql` with the service key; manual `client.messages.stream()` loop, 15 laps, thinking off, `cache_control` on the last system block; prints per lap `usage` (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`), the tool calls, and the final answer.

- [x] **Step 2: Freeze five references** — for Q1 (member profile), Q4 (members per chapter + 90-day delta), Q9 (lowest fill rate next 30 days), Q18 (most recent revenue for a member), Q20 (failed payment / non-active Stripe): write the reference SELECT, run it through the Supabase MCP, save `references/Qn.json` with `{sql, rows, ran_at}`.

- [x] **Step 3: Run the five questions immediately after each reference** and save `runs/Qn.json` with `{answer, tool_calls, laps, wall_ms, usage_per_lap, cost_usd}`.

- [x] **Step 4: Score** — exact match on the reference values (Q1 fields, Q4 counts, Q9 table, Q18 figure+date+tier, Q20 set). Record: exact N/5, Q18 and Q20 answered via SQL yes/no, `cache_read_input_tokens > 0` on lap 2 for every multi-lap turn yes/no, p50 wall, mean cost.

- [x] **Step 5: The Milestone A verdict, one message to Andy** — the nine-check result, the transport numbers, the five scores. **Doable =** 13/13 checks · heartbeat ≥ 300 s · ≥ 4/5 exact · Q18 + Q20 via SQL · cache hit on lap 2 · p50 < 90 s · mean cost < $0.30. Any miss names its fallback before Milestone B starts.

---

# Milestone B — the tool, the proof (two days)

### Task B1: Config — allowlist (fail-closed), budgets, Voyage

**Files:**
- Modify: `src/lib/config.ts` (the `millie:` block, ~line 233)
- Test: `src/lib/millie/team/config.test.ts`

**Interfaces:**
- Produces: `config.millie.teamAskers: string[]`, `config.millie.teamDailyTurns: number` (default 40), `config.millie.teamDailyUsd: number` (default 10), `config.millie.voyageApiKey: string`, `config.millie.researchModel: string` (default `"claude-sonnet-5"`); helper `parseAskers(raw: string | undefined): string[]` exported from `src/lib/millie/team/config.ts`.

- [ ] **Step 1: Write the failing test**

```ts
// src/lib/millie/team/config.test.ts
import { describe, expect, it } from "vitest";
import { parseAskers, parseBudget } from "./config";

describe("MILLIE_TEAM_ASKERS parsing is fail-closed", () => {
  it("an unset variable is an empty list, so nobody is allowed", () => {
    expect(parseAskers(undefined)).toEqual([]);
    expect(parseAskers("")).toEqual([]);
    expect(parseAskers("  ,  ")).toEqual([]);
  });
  it("lower-cases, trims and drops blanks", () => {
    expect(parseAskers(" Andy@MDS.co, eugene@mds.co ,,")).toEqual(["andy@mds.co", "eugene@mds.co"]);
  });
});

describe("daily budgets", () => {
  it("defaults when unset and refuses nonsense", () => {
    expect(parseBudget(undefined, 40)).toBe(40);
    expect(parseBudget("abc", 40)).toBe(40);
    expect(parseBudget("0", 40)).toBe(40);
    expect(parseBudget("12", 40)).toBe(12);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/lib/millie/team/config.test.ts`
Expected: FAIL — `Cannot find module './config'`.

- [ ] **Step 3: Write the helpers and wire config**

```ts
// src/lib/millie/team/config.ts — #172: the allowlist is FAIL-CLOSED. An unset MILLIE_TEAM_ASKERS is an
// empty list, which the route turns into 403 for every staff session, so an everything-access surface
// is never gated by the @mds.co suffix alone.
export function parseAskers(raw: string | undefined): string[] {
  return (raw || "").split(",").map((e) => e.trim().toLowerCase()).filter(Boolean);
}

export function parseBudget(raw: string | undefined, fallback: number): number {
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}
```

In `src/lib/config.ts`, extend the `millie` block:

```ts
  millie: {
    webSecret: process.env.OLIVIA_WEB_SECRET || "",
    webhookStaging: process.env.OLIVIA_WEB_WEBHOOK_STAGING || "https://mdsco.app.n8n.cloud/webhook/olivia-web-staging",
    webhookLive: process.env.OLIVIA_WEB_WEBHOOK_LIVE || "https://mdsco.app.n8n.cloud/webhook/olivia-web-live",
    // #172 Team research mode. teamAskers is FAIL-CLOSED (unset = nobody); the budgets are per asker per UTC day.
    teamAskers: parseAskers(process.env.MILLIE_TEAM_ASKERS),
    teamDailyTurns: parseBudget(process.env.MILLIE_TEAM_DAILY_TURNS, 40),
    teamDailyUsd: parseBudget(process.env.MILLIE_TEAM_DAILY_USD, 10),
    researchModel: process.env.MILLIE_TEAM_MODEL || "claude-sonnet-5",
    voyageApiKey: process.env.VOYAGE_API_KEY || "",
  },
```

with `import { parseAskers, parseBudget } from "@/lib/millie/team/config";` at the top of `config.ts`.

- [ ] **Step 4: Run test to verify it passes** — `npx vitest run src/lib/millie/team/config.test.ts` → PASS. Then `npm test` → all green, `npx tsc --noEmit` clean.

- [ ] **Step 5: Commit** — `git add src/lib/config.ts src/lib/millie/team/config.ts src/lib/millie/team/config.test.ts && git commit -m "#172: fail-closed team allowlist, per-asker daily budgets, Voyage key"`

### Task B2: SQL guard (pure pre-check, never the boundary)

**Files:**
- Create: `src/lib/millie/team/sql-guard.ts`, `src/lib/millie/team/sql-guard.test.ts`

**Interfaces:**
- Produces: `guardSql(sql: string): { ok: true; sql: string } | { ok: false; reason: string }`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import { guardSql } from "./sql-guard";

describe("guardSql — a fast pre-check; the database is the real boundary", () => {
  it("accepts one SELECT and strips a trailing semicolon and comments", () => {
    expect(guardSql("select 1 as one; -- done")).toEqual({ ok: true, sql: "select 1 as one" });
    expect(guardSql("WITH x AS (select 1) select * from x")).toMatchObject({ ok: true });
  });
  it("refuses anything that is not SELECT/WITH/VALUES", () => {
    expect(guardSql("delete from digest.chats")).toMatchObject({ ok: false });
    expect(guardSql("insert into digest.chats values (1)")).toMatchObject({ ok: false });
    expect(guardSql("  update digest.members set phone = 1")).toMatchObject({ ok: false });
  });
  it("refuses a second statement, dollar quoting and top-level DDL/DML keywords", () => {
    expect(guardSql("select 1; select 2")).toMatchObject({ ok: false });
    expect(guardSql("select $$x$$")).toMatchObject({ ok: false });
    expect(guardSql("select 1 union all select 2 ; drop table t")).toMatchObject({ ok: false });
    expect(guardSql("select * from digest.chats where chat_name = 'a; b'")).toMatchObject({ ok: true });
  });
  it("refuses empty input", () => {
    expect(guardSql("   ")).toMatchObject({ ok: false });
  });
});
```

- [ ] **Step 2: Run to verify it fails** — `npx vitest run src/lib/millie/team/sql-guard.test.ts` → FAIL (module missing).

- [ ] **Step 3: Implement**

```ts
// src/lib/millie/team/sql-guard.ts — #172. A cheap pre-check so the model gets a readable reason
// instead of a Postgres error for the common mistakes. It is NOT the security boundary: that is
// millie_team_ro's SELECT-only privileges and digest.team_sql's forced read-only transaction.
const LEADING = /^(select|with|values)\b/i;
const FORBIDDEN = /\b(insert|update|delete|merge|truncate|drop|alter|create|grant|revoke|copy|vacuum|analyze|refresh|call|do|set|reset|listen|notify|lock|begin|commit|rollback|savepoint|prepare|execute|deallocate|security|into)\b/i;

function stripComments(s: string): string {
  return s.replace(/\/\*[\s\S]*?\*\//g, " ").replace(/--[^\n]*/g, " ");
}

/** Removes single-quoted string literals so keyword/semicolon checks only see structure. */
function withoutStrings(s: string): string {
  return s.replace(/'(?:[^']|'')*'/g, "''");
}

export function guardSql(sql: string): { ok: true; sql: string } | { ok: false; reason: string } {
  const cleaned = stripComments(sql).trim().replace(/;+\s*$/, "").trim();
  if (!cleaned) return { ok: false, reason: "empty query" };
  if (!LEADING.test(cleaned)) return { ok: false, reason: "only a single SELECT / WITH / VALUES is allowed" };
  const structural = withoutStrings(cleaned);
  if (structural.includes(";")) return { ok: false, reason: "one statement only — no ';'" };
  if (structural.includes("$$") || /\$[a-z_]*\$/i.test(structural)) return { ok: false, reason: "dollar quoting is not allowed" };
  if (FORBIDDEN.test(structural)) return { ok: false, reason: "a write or DDL keyword is present; this tool is read-only" };
  return { ok: true, sql: cleaned };
}
```

- [ ] **Step 4: Run to verify it passes** — PASS. Note the `into` keyword refuses `select … into`; a false positive on a column named `into` is acceptable for a pre-check (the model sees the reason and rewrites).

- [ ] **Step 5: Commit** — `git commit -am "#172: sql-guard pre-check (pure, tested)"` after `git add src/lib/millie/team/sql-guard.ts src/lib/millie/team/sql-guard.test.ts`.

### Task B3: Pricing (usage → USD)

**Files:**
- Create: `src/lib/millie/team/pricing.ts`, `src/lib/millie/team/pricing.test.ts`

**Interfaces:**
- Produces: `type Usage = { input_tokens: number; output_tokens: number; cache_read_input_tokens?: number; cache_creation_input_tokens?: number }`, `costUsd(model: string, u: Usage): number`, `sumUsage(a: Usage, b: Usage): Usage`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import { costUsd, sumUsage } from "./pricing";

describe("costUsd", () => {
  it("prices Sonnet 5 at $2 in / $10 out per MTok, cache read 0.1x, cache write 1.25x", () => {
    expect(costUsd("claude-sonnet-5", { input_tokens: 1_000_000, output_tokens: 0 })).toBeCloseTo(2, 6);
    expect(costUsd("claude-sonnet-5", { input_tokens: 0, output_tokens: 1_000_000 })).toBeCloseTo(10, 6);
    expect(costUsd("claude-sonnet-5", { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 1_000_000 })).toBeCloseTo(0.2, 6);
    expect(costUsd("claude-sonnet-5", { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 1_000_000 })).toBeCloseTo(2.5, 6);
  });
  it("prices Opus 5 at $5 / $25 and unknown models at Opus rates (never under-count)", () => {
    expect(costUsd("claude-opus-5", { input_tokens: 1_000_000, output_tokens: 1_000_000 })).toBeCloseTo(30, 6);
    expect(costUsd("claude-mystery", { input_tokens: 1_000_000, output_tokens: 0 })).toBeCloseTo(5, 6);
  });
});

describe("sumUsage", () => {
  it("adds every counter, treating absent cache counters as zero", () => {
    expect(sumUsage({ input_tokens: 1, output_tokens: 2 }, { input_tokens: 3, output_tokens: 4, cache_read_input_tokens: 5 }))
      .toEqual({ input_tokens: 4, output_tokens: 6, cache_read_input_tokens: 5, cache_creation_input_tokens: 0 });
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Implement**

```ts
// src/lib/millie/team/pricing.ts — #172. Per-lap usage → USD, stored in metrics.cost_usd on the log row
// so the proof and #32 read cost off the same row the rail reads. Prices per MTok (claude-api skill,
// 2026-06): Sonnet 5 $2/$10, Opus 5 $5/$25; cache read ≈ 0.1× input, cache write (5-min) ≈ 1.25× input.
export type Usage = { input_tokens: number; output_tokens: number; cache_read_input_tokens?: number; cache_creation_input_tokens?: number };

const PRICES: Record<string, { in: number; out: number }> = {
  "claude-sonnet-5": { in: 2, out: 10 },
  "claude-opus-5": { in: 5, out: 25 },
};

export function costUsd(model: string, u: Usage): number {
  const p = PRICES[model] ?? PRICES["claude-opus-5"]; // unknown → the dearer rate, never an under-count
  const M = 1_000_000;
  return (u.input_tokens / M) * p.in + (u.output_tokens / M) * p.out
    + ((u.cache_read_input_tokens ?? 0) / M) * p.in * 0.1
    + ((u.cache_creation_input_tokens ?? 0) / M) * p.in * 1.25;
}

export function sumUsage(a: Usage, b: Usage): Required<Usage> {
  return {
    input_tokens: a.input_tokens + b.input_tokens,
    output_tokens: a.output_tokens + b.output_tokens,
    cache_read_input_tokens: (a.cache_read_input_tokens ?? 0) + (b.cache_read_input_tokens ?? 0),
    cache_creation_input_tokens: (a.cache_creation_input_tokens ?? 0) + (b.cache_creation_input_tokens ?? 0),
  };
}
```

- [ ] **Step 4: Run to verify it passes**, then commit: `git add src/lib/millie/team/pricing.ts src/lib/millie/team/pricing.test.ts && git commit -m "#172: pricing (pure, tested)"`.

### Task B4: The schema catalog (generated index + hand-written rules)

**Files:**
- Create: `scripts/gen-team-catalog.mjs` (mds-digest-web, run locally, read-only)
- Create: `src/lib/millie/team/catalog.generated.json`
- Create: `src/lib/millie/team/catalog.ts`, `src/lib/millie/team/catalog.test.ts`

**Interfaces:**
- Produces: `CATALOG_SYSTEM_TEXT: string` (byte-stable), `describeTable(name: string): string | null`, `searchCatalog(q: string): string[]` (table.column or `at_fields:Key` hits), `RULES: string`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import { CATALOG_SYSTEM_TEXT, RULES, describeTable, searchCatalog } from "./catalog";

describe("the schema catalog", () => {
  it("is byte-stable across imports (prompt cache depends on it)", () => {
    expect(CATALOG_SYSTEM_TEXT).toBe(CATALOG_SYSTEM_TEXT.slice());
    expect(CATALOG_SYSTEM_TEXT.length).toBeGreaterThan(4000);
  });
  it("carries the eight canonical rules by name", () => {
    for (const rule of ["member_attributes", "Current Member", "events_catalog", "not_a_real_event", "event_registrations_live", "registration_status_v2", "member_identity", "synced_at", "LIMIT", "pct"]) {
      expect(RULES).toContain(rule);
    }
  });
  it("describes a table with its columns and comment, and knows the deny-list view", () => {
    expect(describeTable("digest.member_attributes")).toContain("membership_status");
    expect(describeTable("digest.member_profiles_team")).toContain("at_fields");
    expect(describeTable("digest.member_profiles")).toBeNull(); // the TABLE is not readable in Team mode
    expect(describeTable("digest.olivia_web_messages")).toBeNull();
  });
  it("finds at_fields keys and columns by search, and never lists a denied key", () => {
    expect(searchCatalog("revenue").some((h) => h.includes("Most Recent Revenue"))).toBe(true);
    expect(searchCatalog("removal")).toEqual([]);
    expect(searchCatalog("ltv")).toEqual([]);
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Write the generator and run it once**

```js
// scripts/gen-team-catalog.mjs — #172. Read-only. Writes src/lib/millie/team/catalog.generated.json from
// information_schema + table comments THROUGH digest.team_sql (so it can only ever see what the role sees).
// Run: node scripts/gen-team-catalog.mjs   (needs SUPABASE_URL + SUPABASE_SECRET_KEY in .env.local)
import fs from "node:fs";
const env = Object.fromEntries(fs.readFileSync(".env.local", "utf8").split("\n").filter((l) => l.includes("=") && !l.startsWith("#")).map((l) => { const i = l.indexOf("="); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^["']|["']$/g, "")]; }));
const BASE = env.SUPABASE_URL.replace(/\/$/, "") + "/rest/v1";
async function teamSql(p_sql, p_max_rows = 500) {
  const r = await fetch(`${BASE}/rpc/team_sql`, { method: "POST", headers: { apikey: env.SUPABASE_SECRET_KEY, Authorization: `Bearer ${env.SUPABASE_SECRET_KEY}`, "Accept-Profile": "digest", "Content-Profile": "digest", "Content-Type": "application/json" }, body: JSON.stringify({ p_sql, p_max_rows }) });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return (await r.json()).rows;
}
const tables = await teamSql(`select n.nspname as schema, c.relname as name, c.relkind as kind, obj_description(c.oid, 'pg_class') as comment from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname in ('digest','event') and c.relkind in ('r','v','m') and has_table_privilege('millie_team_ro', c.oid, 'SELECT') order by 1, 2`);
const columns = await teamSql(`select table_schema as schema, table_name as name, column_name as col, data_type as type, ordinal_position as pos from information_schema.columns where table_schema in ('digest','event') order by 1,2,5`, 5000);
const atKeys = await teamSql(`select name, field_type from digest.at_field_catalog where name !~* '(removal|reason|ltv|score ?card|member score|notes|lead scor|budget)' order by position`, 2000);
const out = { generated_at: new Date().toISOString().slice(0, 10), tables: tables.map((t) => ({ ...t, columns: columns.filter((c) => c.schema === t.schema && c.name === t.name).map((c) => `${c.col}:${c.type}`) })), at_fields_keys: atKeys.map((k) => k.name) };
fs.writeFileSync("src/lib/millie/team/catalog.generated.json", JSON.stringify(out, null, 1) + "\n");
console.log(`tables ${out.tables.length}, at_fields keys ${out.at_fields_keys.length}`);
```

Run: `node scripts/gen-team-catalog.mjs` → prints counts (expect ~95 tables/views the role can read, ~790 keys). Because `has_table_privilege('millie_team_ro', …)` filters, `member_profiles`, `olivia_web_messages` are absent and `member_profiles_team` is present — the test relies on that.

- [ ] **Step 4: Write the catalog module**

```ts
// src/lib/millie/team/catalog.ts — #172. The system-prompt catalog: a hand-written RULES block (the traps
// every previous session paid for) plus a generated index. Byte-stable on purpose: it sits in the cached
// system block, and any per-request text here would silently invalidate the prompt cache every lap.
import generated from "./catalog.generated.json";

type GenTable = { schema: string; name: string; kind: string; comment: string | null; columns: string[] };
const TABLES: GenTable[] = (generated as { tables: GenTable[] }).tables;
const AT_KEYS: string[] = (generated as { at_fields_keys: string[] }).at_fields_keys;

export const RULES = [
  "RULES — every one of these was learned the hard way; follow them before you write SQL.",
  "1. 'members' means digest.member_attributes (5,759 rows, one per Airtable member record). digest.members (689 rows) is the WhatsApp-keyed table. Join on at_member_id.",
  "2. A CURRENT member has membership_status in ('Current Member','New Member'); the data also contains 'Current Member- Paused ' with a trailing space — use trim(). Exclude 'Staff','Team User' and every 'Removed - %' status from member counts and lists unless the question is about them.",
  "3. Events live in digest.events_catalog; ignore rows where not_a_real_event is not null. Registrations live in digest.event_registrations_live (NEVER event_registrations). 'Is X registered for Y' is answered by select * from digest.registration_status_v2(<at_member_id>, <event at_record_id>) — has_ticket is the roster answer, is_attending the GroupOS answer.",
  "4. digest.wa_messages.sender_member is an Airtable record id; bridge it to at_member_id through digest.member_identity (airtable_id ↔ at_member_id). Facebook authors bridge through digest.fb_member_map (author_uid → member), which covers 809 authors of 4,266 posts — say so when a count depends on it.",
  "5. digest.call_attendance links only ~36% of rows to an at_member_id. Any per-member call figure undercounts; state it.",
  "6. member_profiles is NOT readable in this mode; digest.member_profiles_team is (same columns, at_fields minus closed keys). Exact revenue: at_fields->>'Most Recent Revenue', 'Most Recent Revenue Source', 'Most Recent Revenue Date', 'Total TTM Revenue', 'Annual Revenue Tier - Numerical'. Billing: subscription_status, mrr, next_renewal, next_renewal_amount, scheduled_cancel, collection_paused, stripe_customer_id, plus at_fields 'Failed Payment Date (Stripe)', 'Stripe Subscription Status'. Contact: digest.members.phone/email, member_profiles_team.email, at_fields 'Preferred Email', 'Preferred Phone Number'.",
  "7. Percentages: columns named pct are 0..1; personas_stats.value is 0..100. Say which you used.",
  "8. Freshness: every mirror carries synced_at (member_profiles_team.synced_at, event_registrations_live.synced_at, events_catalog.synced_at); wa_messages.sent_at and fb_posts.created_time are event times. Quote the age when it matters. Airtable is never read live here.",
  "9. Always LIMIT. The tool returns at most 200 rows and marks truncated=true; aggregate in SQL rather than paging. Prefer count(*)/group by over pulling rows to count them.",
  "10. Full-text search: content_items.search_tsv @@ websearch_to_tsquery('english', $q) over tl_dr+body+search_extra; kinds: wa_message, fb_post, fb_comment, call_transcript, application, video. For meaning rather than words use the semantic_search tool.",
  "11. Say what you did not find. Never claim MDS does not track something until you have searched the catalog for the column.",
].join("\n");

function line(t: GenTable): string {
  const cols = t.columns.map((c) => c.split(":")[0]).join(", ");
  return `${t.schema}.${t.name} (${t.kind === "r" ? "table" : "view"}) — ${t.comment ?? "no comment"} — columns: ${cols}`;
}

const INDEX = TABLES.map(line).join("\n");
const KEYS = `at_fields keys readable in Team mode (${AT_KEYS.length}): ${AT_KEYS.join(" | ")}`;

export const CATALOG_SYSTEM_TEXT = [RULES, "", "TABLES (schemas digest, event):", INDEX, "", KEYS].join("\n");

export function describeTable(name: string): string | null {
  const [schema, bare] = name.includes(".") ? name.split(".", 2) : ["digest", name];
  const t = TABLES.find((x) => x.schema === schema && x.name === bare);
  if (!t) return null;
  return `${t.schema}.${t.name}\n${t.comment ?? ""}\n${t.columns.map((c) => "  " + c.replace(":", "  ")).join("\n")}`;
}

export function searchCatalog(q: string): string[] {
  const needle = q.trim().toLowerCase();
  if (!needle) return [];
  const hits: string[] = [];
  for (const t of TABLES) for (const c of t.columns) if (c.toLowerCase().includes(needle)) hits.push(`${t.schema}.${t.name}.${c.split(":")[0]}`);
  for (const k of AT_KEYS) if (k.toLowerCase().includes(needle)) hits.push(`at_fields:${k}`);
  return hits.slice(0, 60);
}
```

Add `"resolveJsonModule": true` to `tsconfig.json` `compilerOptions` if it is not already set (check with `grep resolveJsonModule tsconfig.json`).

- [ ] **Step 5: Run to verify it passes** — `npx vitest run src/lib/millie/team/catalog.test.ts` → PASS. `npx tsc --noEmit` clean.

- [ ] **Step 6: Commit** — `git add scripts/gen-team-catalog.mjs src/lib/millie/team/catalog.generated.json src/lib/millie/team/catalog.ts src/lib/millie/team/catalog.test.ts tsconfig.json && git commit -m "#172: schema catalog — generated index through the role's own eyes, hand-written rules"`.

### Task B5: Tools — definitions and runners

**Files:**
- Create: `src/lib/millie/team/tools.ts`, `src/lib/millie/team/tools.test.ts`

**Interfaces:**
- Consumes: `guardSql` (B2), `describeTable`/`searchCatalog` (B4), `sbRequest` (`@/lib/supabase`), `config.millie.voyageApiKey` (B1).
- Produces: `TOOLS: Anthropic.Tool[]` (sorted by name, byte-stable), `type ToolCall = { id: string; name: string; input: unknown }`, `type TrailStep = { n: number; tool: "sql" | "catalog" | "semantic"; sql?: string; input?: unknown; rows?: number; ms: number; truncated?: boolean; error?: string }`, `runTool(call: ToolCall, n: number, deps?: ToolDeps): Promise<{ result: string; step: TrailStep; is_error: boolean }>`, `type ToolDeps = { teamSql: (sql: string, maxRows: number) => Promise<TeamSqlResult>; embed: (q: string) => Promise<number[] | null> }`, `defaultDeps()`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it, vi } from "vitest";
import { TOOLS, runTool, type ToolDeps } from "./tools";

const deps = (over: Partial<ToolDeps> = {}): ToolDeps => ({
  teamSql: vi.fn(async (sql: string) => ({ rows: [{ n: 5759 }], row_count: 1, truncated: false })),
  embed: vi.fn(async () => Array.from({ length: 1024 }, (_, i) => (i % 7) / 10)),
  ...over,
});

describe("TOOLS", () => {
  it("is sorted by name and names exactly the three tools", () => {
    expect(TOOLS.map((t) => t.name)).toEqual(["schema_catalog", "semantic_search", "sql_query"]);
  });
});

describe("sql_query", () => {
  it("runs a guarded SELECT and returns rows plus a trail step", async () => {
    const d = deps();
    const r = await runTool({ id: "t1", name: "sql_query", input: { sql: "select count(*) as n from digest.member_attributes;" } }, 1, d);
    expect(d.teamSql).toHaveBeenCalledWith("select count(*) as n from digest.member_attributes", 200);
    expect(r.is_error).toBe(false);
    expect(JSON.parse(r.result)).toMatchObject({ row_count: 1, rows: [{ n: 5759 }] });
    expect(r.step).toMatchObject({ n: 1, tool: "sql", rows: 1, truncated: false });
  });
  it("refuses a write before it reaches the database, as a tool error the model can read", async () => {
    const d = deps();
    const r = await runTool({ id: "t2", name: "sql_query", input: { sql: "delete from digest.chats" } }, 2, d);
    expect(d.teamSql).not.toHaveBeenCalled();
    expect(r.is_error).toBe(true);
    expect(r.result).toContain("read-only");
  });
  it("passes a Postgres error through verbatim so the model can repair the query", async () => {
    const d = deps({ teamSql: vi.fn(async () => { throw new Error('Supabase 400: {"code":"42703","message":"column x does not exist"}'); }) });
    const r = await runTool({ id: "t3", name: "sql_query", input: { sql: "select x from digest.chats" } }, 3, d);
    expect(r.is_error).toBe(true);
    expect(r.result).toContain("42703");
    expect(r.step.error).toContain("42703");
  });
  it("truncates a huge payload at 48 KB and says so", async () => {
    const big = Array.from({ length: 200 }, (_, i) => ({ i, body: "x".repeat(600) }));
    const d = deps({ teamSql: vi.fn(async () => ({ rows: big, row_count: 200, truncated: true })) });
    const r = await runTool({ id: "t4", name: "sql_query", input: { sql: "select body from digest.content_items" } }, 4, d);
    expect(r.result.length).toBeLessThan(50_000);
    expect(r.result).toContain("payload truncated");
  });
});

describe("schema_catalog", () => {
  it("describes a table or searches names, with no I/O", async () => {
    const d = deps();
    const r = await runTool({ id: "c1", name: "schema_catalog", input: { table: "digest.member_attributes" } }, 5, d);
    expect(r.result).toContain("membership_status");
    expect(d.teamSql).not.toHaveBeenCalled();
    const s = await runTool({ id: "c2", name: "schema_catalog", input: { search: "revenue" } }, 6, d);
    expect(s.result).toContain("Most Recent Revenue");
  });
});

describe("semantic_search", () => {
  it("embeds, then runs the fixed pgvector query through team_sql as one SELECT", async () => {
    const d = deps({ teamSql: vi.fn(async (sql: string) => { expect(sql).toMatch(/^select /i); expect(sql).toContain("operator(extensions.<=>)"); expect(sql).not.toContain(";"); return { rows: [{ id: 1, source: "wa_message", snippet: "PPC", score: 0.9 }], row_count: 1, truncated: false }; }) });
    const r = await runTool({ id: "s1", name: "semantic_search", input: { query: "amazon ppc bids", sources: ["wa_message"], limit: 10 } }, 7, d);
    expect(d.embed).toHaveBeenCalledWith("amazon ppc bids");
    expect(r.is_error).toBe(false);
    expect(r.step).toMatchObject({ tool: "semantic", rows: 1 });
  });
  it("degrades to a visible flag when no embedding is available", async () => {
    const d = deps({ embed: vi.fn(async () => null) });
    const r = await runTool({ id: "s2", name: "semantic_search", input: { query: "ppc" } }, 8, d);
    expect(r.is_error).toBe(true);
    expect(r.result).toContain("vector lane OFF");
    expect(d.teamSql).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Implement**

```ts
// src/lib/millie/team/tools.ts — #172. The three tools of Team research mode and how each is run.
// sql_query and semantic_search reach the database ONLY through digest.team_sql (service key over
// PostgREST), which runs as the read-only role; schema_catalog never leaves this process.
import type Anthropic from "@anthropic-ai/sdk";
import { config } from "@/lib/config";
import { sbRequest } from "@/lib/supabase";
import { guardSql } from "./sql-guard";
import { describeTable, searchCatalog } from "./catalog";

export type TeamSqlResult = { rows: unknown[]; row_count: number; truncated: boolean };
export type ToolCall = { id: string; name: string; input: unknown };
export type TrailStep = { n: number; tool: "sql" | "catalog" | "semantic"; sql?: string; input?: unknown; rows?: number; ms: number; truncated?: boolean; error?: string };
export type ToolDeps = { teamSql: (sql: string, maxRows: number) => Promise<TeamSqlResult>; embed: (q: string) => Promise<number[] | null> };

const MAX_ROWS = 200;
const MAX_PAYLOAD = 48_000;
const SEMANTIC_SOURCES = ["wa_message", "fb_post", "fb_comment", "call_transcript", "application", "video"];

export const TOOLS: Anthropic.Tool[] = [
  {
    name: "schema_catalog",
    description: "Describe one table/view of the warehouse (columns, comment) or search column and at_fields key names. No database call. Use it before guessing a column.",
    input_schema: { type: "object", properties: { table: { type: "string", description: "schema.table, e.g. digest.member_attributes" }, search: { type: "string", description: "a word to find in column or at_fields key names" } } },
  },
  {
    name: "semantic_search",
    description: "Meaning-based search over member content (WhatsApp, Facebook posts and comments, call transcripts, applications, videos) using embeddings. Returns snippets with source, date, url and a similarity score. Ungated in Team mode. Prefer sql_query full-text when the words themselves matter.",
    input_schema: { type: "object", properties: { query: { type: "string" }, sources: { type: "array", items: { type: "string", enum: SEMANTIC_SOURCES } }, limit: { type: "integer", minimum: 1, maximum: 40 } }, required: ["query"] },
  },
  {
    name: "sql_query",
    description: "Run ONE read-only SELECT/WITH over schemas digest and event. Returns up to 200 rows as JSON plus row_count and truncated; on failure returns the verbatim Postgres error so you can repair the query. Always LIMIT; aggregate in SQL.",
    input_schema: { type: "object", properties: { sql: { type: "string" }, max_rows: { type: "integer", minimum: 1, maximum: 200 } }, required: ["sql"] },
  },
].sort((a, b) => a.name.localeCompare(b.name));

export async function teamSqlViaPostgrest(sql: string, maxRows: number): Promise<TeamSqlResult> {
  return sbRequest<TeamSqlResult>("rpc/team_sql", { method: "POST", body: { p_sql: sql, p_max_rows: maxRows } });
}

/** The same Voyage call api/olivia/kb/route.ts makes: voyage-3.5-lite, 1024 dims, query input type. */
export async function embedWithVoyage(q: string): Promise<number[] | null> {
  const key = config.millie.voyageApiKey;
  if (!key) return null;
  const r = await fetch("https://api.voyageai.com/v1/embeddings", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "voyage-3.5-lite", input: [q], input_type: "query", output_dimension: 1024 }),
    signal: AbortSignal.timeout(20_000),
  });
  const d = (await r.json().catch(() => ({}))) as { data?: Array<{ embedding: number[] }> };
  return d.data?.[0]?.embedding ?? null;
}

export const defaultDeps = (): ToolDeps => ({ teamSql: teamSqlViaPostgrest, embed: embedWithVoyage });

function clip(s: string): string {
  return s.length > MAX_PAYLOAD ? s.slice(0, MAX_PAYLOAD) + `\n… payload truncated at ${MAX_PAYLOAD} chars — narrow the query (select fewer columns, aggregate, or LIMIT lower).` : s;
}

function errorText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export async function runTool(call: ToolCall, n: number, deps: ToolDeps = defaultDeps()): Promise<{ result: string; step: TrailStep; is_error: boolean }> {
  const t0 = Date.now();
  const input = (call.input && typeof call.input === "object" ? call.input : {}) as Record<string, unknown>;

  if (call.name === "schema_catalog") {
    const table = typeof input.table === "string" ? input.table : "";
    const search = typeof input.search === "string" ? input.search : "";
    const text = table ? (describeTable(table) ?? `no readable table ${table} in Team mode`) : searchCatalog(search).join("\n") || "no match";
    return { result: text, step: { n, tool: "catalog", input: { table, search }, ms: Date.now() - t0 }, is_error: false };
  }

  if (call.name === "sql_query") {
    const g = guardSql(typeof input.sql === "string" ? input.sql : "");
    if (!g.ok) return { result: `refused before the database: ${g.reason}. This tool is read-only and takes one SELECT.`, step: { n, tool: "sql", sql: String(input.sql ?? ""), ms: Date.now() - t0, error: g.reason }, is_error: true };
    const maxRows = Math.min(MAX_ROWS, Math.max(1, Number(input.max_rows) || MAX_ROWS));
    try {
      const r = await deps.teamSql(g.sql, maxRows);
      const body = clip(JSON.stringify({ row_count: r.row_count, truncated: r.truncated, rows: r.rows }));
      return { result: body, step: { n, tool: "sql", sql: g.sql, rows: r.row_count, truncated: r.truncated, ms: Date.now() - t0 }, is_error: false };
    } catch (e) {
      const msg = errorText(e);
      return { result: `query failed: ${msg}`, step: { n, tool: "sql", sql: g.sql, ms: Date.now() - t0, error: msg }, is_error: true };
    }
  }

  if (call.name === "semantic_search") {
    const query = typeof input.query === "string" ? input.query.trim() : "";
    const sources = Array.isArray(input.sources) ? input.sources.filter((s): s is string => typeof s === "string" && SEMANTIC_SOURCES.includes(s)) : [];
    const limit = Math.min(40, Math.max(1, Number(input.limit) || 20));
    const vec = query ? await deps.embed(query) : null;
    if (!vec) return { result: "vector lane OFF — no embedding available (VOYAGE_API_KEY missing or the embed failed). Use sql_query full-text: content_items.search_tsv @@ websearch_to_tsquery('english', <words>).", step: { n, tool: "semantic", input: { query, sources, limit }, ms: Date.now() - t0, error: "vector lane OFF" }, is_error: true };
    const vlit = `'[${vec.map((x) => Number(x).toFixed(6)).join(",")}]'::extensions.vector(1024)`;
    const srcFilter = sources.length ? ` and source in (${sources.map((s) => `'${s}'`).join(",")})` : "";
    const sql = `select id, source, kind, title, left(coalesce(tl_dr, body), 400) as snippet, occurred_at, url, round((1 - (embedding operator(extensions.<=>) ${vlit}))::numeric, 4) as score from digest.content_items where embedding is not null${srcFilter} order by embedding operator(extensions.<=>) ${vlit} limit ${limit}`;
    try {
      const r = await deps.teamSql(sql, limit);
      return { result: clip(JSON.stringify({ row_count: r.row_count, rows: r.rows })), step: { n, tool: "semantic", input: { query, sources, limit }, rows: r.row_count, ms: Date.now() - t0 }, is_error: false };
    } catch (e) {
      const msg = errorText(e);
      return { result: `semantic search failed: ${msg}`, step: { n, tool: "semantic", input: { query, sources, limit }, ms: Date.now() - t0, error: msg }, is_error: true };
    }
  }

  return { result: `unknown tool ${call.name}`, step: { n, tool: "sql", ms: Date.now() - t0, error: "unknown tool" }, is_error: true };
}
```

- [ ] **Step 4: Run to verify it passes** — PASS; `npx tsc --noEmit` clean. (The role needs `USAGE` on schema `extensions` for `operator(extensions.<=>)` — the migration grants it.)

- [ ] **Step 5: Commit** — `git add src/lib/millie/team/tools.ts src/lib/millie/team/tools.test.ts && git commit -m "#172: the three tools — sql_query, schema_catalog, semantic_search"`.

### Task B6: The turn log (two rows, per-lap and final PATCH, daily budget)

**Files:**
- Create: `src/lib/millie/team/log.ts`, `src/lib/millie/team/log.test.ts`

**Interfaces:**
- Consumes: `sbRequest`, `TrailStep` (B5), `Usage` (B3).
- Produces: `openTurn(args: { askerEmail: string; threadId: string; text: string; ackAt: string | null }): Promise<{ questionId: number; answerId: number }>`, `patchTrail(answerId: number, sources: TrailStep[], plan: unknown[]): Promise<void>`, `closeTurn(answerId: number, final: { answer_md: string; sources: TrailStep[]; plan: unknown[]; metrics: TurnMetrics; model: string; latency_ms: number; notes: string[] }): Promise<void>`, `type TurnMetrics = { model: string; thinking: boolean; laps: number; wall_ms: number; input_tokens: number; output_tokens: number; cache_read_tokens: number; cache_write_tokens: number; cost_usd: number; cut: string | null; transport: "stream" | "poll" }`, `dailySpend(askerEmail: string, dayIso: string): Promise<{ turns: number; usd: number }>`, `threadMode(askerEmail: string, threadId: string): Promise<string | null>`.

- [ ] **Step 1: Write the failing test**

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";
const { sbRequest } = vi.hoisted(() => ({ sbRequest: vi.fn() }));
vi.mock("@/lib/supabase", () => ({ sbRequest, isSupabaseConfigured: () => true }));
import { openTurn, patchTrail, closeTurn, dailySpend, threadMode } from "./log";

beforeEach(() => sbRequest.mockReset());

describe("openTurn", () => {
  it("inserts the question row and an answer placeholder, both mode=team, asker from the argument only", async () => {
    sbRequest.mockResolvedValueOnce([{ id: 101 }]).mockResolvedValueOnce([{ id: 102 }]);
    const r = await openTurn({ askerEmail: "andy@mds.co", threadId: "t_abc", text: "how many members?", ackAt: "2026-09-11T10:00:00Z" });
    expect(r).toEqual({ questionId: 101, answerId: 102 });
    const [path1, init1] = sbRequest.mock.calls[0];
    expect(path1).toBe("olivia_web_messages");
    expect(init1.method).toBe("POST");
    expect(init1.prefer).toBe("return=representation");
    expect(init1.body).toMatchObject({ thread_id: "t_abc", asker_email: "andy@mds.co", mode: "team", target: "prod", role: "member", text: "how many members?", route: "team-research" });
    const [, init2] = sbRequest.mock.calls[1];
    expect(init2.body).toMatchObject({ role: "olivia", mode: "team", answer_md: null, notes: ["running", "ack:2026-09-11T10:00:00Z"] });
  });
});

describe("patchTrail / closeTurn", () => {
  it("PATCHes the answer row by id with the trail, then with the final fields", async () => {
    sbRequest.mockResolvedValue(undefined);
    await patchTrail(102, [{ n: 1, tool: "sql", sql: "select 1", rows: 1, ms: 12 }], [{ lap: 1, tool_calls: 1 }]);
    expect(sbRequest.mock.calls[0][0]).toBe("olivia_web_messages?id=eq.102");
    expect(sbRequest.mock.calls[0][1]).toMatchObject({ method: "PATCH", prefer: "return=minimal" });
    await closeTurn(102, { answer_md: "one", sources: [], plan: [], metrics: { model: "claude-sonnet-5", thinking: false, laps: 1, wall_ms: 900, input_tokens: 10, output_tokens: 5, cache_read_tokens: 0, cache_write_tokens: 0, cost_usd: 0.0001, cut: null, transport: "stream" }, model: "claude-sonnet-5", latency_ms: 900, notes: ["ack:x"] });
    expect(sbRequest.mock.calls[1][1].body).toMatchObject({ answer_md: "one", model: "claude-sonnet-5", latency_ms: 900 });
  });
});

describe("dailySpend / threadMode", () => {
  it("sums today's team turns and cost for one asker", async () => {
    sbRequest.mockResolvedValueOnce([{ metrics: { cost_usd: 0.1 } }, { metrics: { cost_usd: 0.25 } }, { metrics: null }]);
    expect(await dailySpend("andy@mds.co", "2026-09-11")).toEqual({ turns: 3, usd: 0.35 });
    expect(sbRequest.mock.calls[0][0]).toContain("asker_email=eq.andy%40mds.co");
    expect(sbRequest.mock.calls[0][0]).toContain("mode=eq.team");
    expect(sbRequest.mock.calls[0][0]).toContain("created_at=gte.2026-09-11T00:00:00Z");
  });
  it("reports the mode of an existing thread, or null when it has no rows", async () => {
    sbRequest.mockResolvedValueOnce([{ mode: "public" }]);
    expect(await threadMode("andy@mds.co", "t_old")).toBe("public");
    sbRequest.mockResolvedValueOnce([]);
    expect(await threadMode("andy@mds.co", "t_new")).toBeNull();
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Implement**

```ts
// src/lib/millie/team/log.ts — #172. Every Team turn is two rows in digest.olivia_web_messages, the same
// table the web door writes, so the sessions rail, GET thread and Clear work unchanged. The asker is
// whatever the ROUTE resolved from the session — this module never reads a request. Nothing here touches
// digest.olivia_messages (the member WhatsApp log) and no wamid is minted.
import { sbRequest } from "@/lib/supabase";
import type { TrailStep } from "./tools";

export type TurnMetrics = { model: string; thinking: boolean; laps: number; wall_ms: number; input_tokens: number; output_tokens: number; cache_read_tokens: number; cache_write_tokens: number; cost_usd: number; cut: string | null; transport: "stream" | "poll" };

const TABLE = "olivia_web_messages";

export async function openTurn(a: { askerEmail: string; threadId: string; text: string; ackAt: string | null }): Promise<{ questionId: number; answerId: number }> {
  const base = { thread_id: a.threadId, asker_email: a.askerEmail, mode: "team", target: "prod", route: "team-research" };
  const q = await sbRequest<Array<{ id: number }>>(TABLE, { method: "POST", prefer: "return=representation", body: { ...base, role: "member", text: a.text } });
  const notes = ["running", ...(a.ackAt ? [`ack:${a.ackAt}`] : [])];
  const ans = await sbRequest<Array<{ id: number }>>(TABLE, { method: "POST", prefer: "return=representation", body: { ...base, role: "olivia", text: null, answer_md: null, notes, sources: [], plan: [] } });
  return { questionId: q[0].id, answerId: ans[0].id };
}

export async function patchTrail(answerId: number, sources: TrailStep[], plan: unknown[]): Promise<void> {
  await sbRequest<void>(`${TABLE}?id=eq.${answerId}`, { method: "PATCH", prefer: "return=minimal", body: { sources, plan } });
}

export async function closeTurn(answerId: number, f: { answer_md: string; sources: TrailStep[]; plan: unknown[]; metrics: TurnMetrics; model: string; latency_ms: number; notes: string[] }): Promise<void> {
  await sbRequest<void>(`${TABLE}?id=eq.${answerId}`, { method: "PATCH", prefer: "return=minimal", body: { answer_md: f.answer_md, sources: f.sources, plan: f.plan, metrics: f.metrics, model: f.model, latency_ms: f.latency_ms, notes: f.notes } });
}

/** Today's Team turns and USD for one asker (UTC day). Feeds the per-asker budget in the route gate. */
export async function dailySpend(askerEmail: string, dayIso: string): Promise<{ turns: number; usd: number }> {
  const rows = await sbRequest<Array<{ metrics: { cost_usd?: number } | null }>>(
    `${TABLE}?select=metrics&asker_email=eq.${encodeURIComponent(askerEmail)}&mode=eq.team&role=eq.olivia&created_at=gte.${dayIso}T00:00:00Z&limit=1000`,
  );
  const usd = rows.reduce((s, r) => s + (Number(r.metrics?.cost_usd) || 0), 0);
  return { turns: rows.length, usd: Math.round(usd * 10000) / 10000 };
}

/** The mode of an existing thread (its first row), or null for a brand-new thread id. */
export async function threadMode(askerEmail: string, threadId: string): Promise<string | null> {
  const rows = await sbRequest<Array<{ mode: string }>>(
    `${TABLE}?select=mode&asker_email=eq.${encodeURIComponent(askerEmail)}&thread_id=eq.${encodeURIComponent(threadId)}&order=id.asc&limit=1`,
  );
  return rows[0]?.mode ?? null;
}
```

- [ ] **Step 4: Run to verify it passes**, `npx tsc --noEmit` clean, then commit: `git add src/lib/millie/team/log.ts src/lib/millie/team/log.test.ts && git commit -m "#172: turn log — two rows, per-lap trail, daily spend"`.

### Task B7: The loop (injected client, caps, cache layout, events)

**Files:**
- Create: `src/lib/millie/team/loop.ts`, `src/lib/millie/team/loop.test.ts`

**Interfaces:**
- Consumes: `TOOLS`, `runTool`, `ToolDeps`, `TrailStep` (B5); `costUsd`, `sumUsage`, `Usage` (B3); `CATALOG_SYSTEM_TEXT` (B4).
- Produces: `type LoopEvent = { type: "started" } | { type: "tool_call"; n: number; name: string; input: unknown } | { type: "tool_result"; step: TrailStep } | { type: "text"; delta: string } | { type: "lap"; lap: number; usage: Usage; cache_read: number }`, `runResearchLoop(args: { question: string; askerEmail: string; history: Array<{ role: "user" | "assistant"; content: string }>; model: string; thinking?: boolean; client: LoopClient; deps?: ToolDeps; onEvent: (e: LoopEvent) => void; onTrail: (sources: TrailStep[], plan: unknown[]) => Promise<void>; signal?: AbortSignal }): Promise<{ answer: string; sources: TrailStep[]; plan: unknown[]; laps: number; usage: Required<Usage>; cost_usd: number; cut: string | null }>`, `type LoopClient = { stream: (params: Anthropic.MessageCreateParamsStreaming) => MessageStreamLike }` where `MessageStreamLike` exposes `[Symbol.asyncIterator]()` over raw stream events and `finalMessage(): Promise<Anthropic.Message>` — the shape of `client.messages.stream()` in SDK 0.100.1.

- [ ] **Step 1: Write the failing test** (a fake client that scripts two laps: a tool call, then a final text; plus the Airtable runtime spy)

```ts
import { describe, expect, it, vi } from "vitest";
vi.mock("@/lib/supabase", () => ({ sbRequest: vi.fn(), isSupabaseConfigured: () => true }));
import { runResearchLoop, type LoopClient, type LoopEvent } from "./loop";
import type { ToolDeps } from "./tools";

type Msg = { role: "assistant"; content: Array<{ type: "text"; text: string } | { type: "tool_use"; id: string; name: string; input: unknown }>; stop_reason: "tool_use" | "end_turn"; usage: { input_tokens: number; output_tokens: number; cache_read_input_tokens?: number; cache_creation_input_tokens?: number } };

function fakeClient(script: Msg[], seen: unknown[] = []): LoopClient {
  let i = 0;
  return {
    stream: (params) => {
      seen.push(params);
      const msg = script[Math.min(i++, script.length - 1)];
      const events = msg.content.flatMap((b) => b.type === "text" ? [{ type: "content_block_delta", delta: { type: "text_delta", text: b.text } }] : []);
      return {
        async *[Symbol.asyncIterator]() { for (const e of events) yield e as never; },
        finalMessage: async () => msg as never,
      };
    },
  };
}

const deps: ToolDeps = { teamSql: vi.fn(async () => ({ rows: [{ n: 602 }], row_count: 1, truncated: false })), embed: vi.fn(async () => null) };

describe("runResearchLoop", () => {
  it("runs a tool lap then answers, emitting the trail and accounting usage", async () => {
    const seen: unknown[] = [];
    const client = fakeClient([
      { role: "assistant", content: [{ type: "tool_use", id: "tu1", name: "sql_query", input: { sql: "select count(*) as n from digest.member_attributes where membership_status='Current Member'" } }], stop_reason: "tool_use", usage: { input_tokens: 9000, output_tokens: 80, cache_creation_input_tokens: 8000 } },
      { role: "assistant", content: [{ type: "text", text: "602 current members." }], stop_reason: "end_turn", usage: { input_tokens: 400, output_tokens: 20, cache_read_input_tokens: 8000 } },
    ], seen);
    const events: LoopEvent[] = []; const trails: number[] = [];
    const r = await runResearchLoop({ question: "how many current members?", askerEmail: "andy@mds.co", history: [], model: "claude-sonnet-5", client, deps, onEvent: (e) => events.push(e), onTrail: async (s) => { trails.push(s.length); } });
    expect(r.answer).toBe("602 current members.");
    expect(r.laps).toBe(2);
    expect(r.sources).toHaveLength(1);
    expect(r.sources[0]).toMatchObject({ tool: "sql", rows: 1 });
    expect(trails).toEqual([1]);
    expect(r.usage.cache_read_input_tokens).toBe(8000);
    expect(r.cost_usd).toBeGreaterThan(0);
    expect(events.map((e) => e.type)).toEqual(["started", "tool_call", "tool_result", "lap", "text", "lap"]);
    // cache layout: tools sorted, system = [catalog+rules with cache_control], per-request text in messages only
    const p = seen[0] as { tools: Array<{ name: string }>; system: Array<{ text: string; cache_control?: unknown }>; messages: Array<{ role: string }> };
    expect(p.tools.map((t) => t.name)).toEqual(["schema_catalog", "semantic_search", "sql_query"]);
    expect(p.system[p.system.length - 1].cache_control).toEqual({ type: "ephemeral" });
    expect(p.system.map((s) => s.text).join("")).not.toContain("andy@mds.co");
    expect(JSON.stringify(p.messages)).toContain("andy@mds.co");
    // second lap carries the tool_result back in ONE user message
    const p2 = seen[1] as { messages: Array<{ role: string; content: unknown }> };
    expect(p2.messages[p2.messages.length - 1]).toMatchObject({ role: "user" });
    expect(JSON.stringify(p2.messages[p2.messages.length - 1].content)).toContain("tool_result");
  });

  it("stops at the lap cap and reports the cut", async () => {
    const client = fakeClient([{ role: "assistant", content: [{ type: "tool_use", id: "x", name: "schema_catalog", input: { search: "a" } }], stop_reason: "tool_use", usage: { input_tokens: 1, output_tokens: 1 } }]);
    const r = await runResearchLoop({ question: "q", askerEmail: "a@mds.co", history: [], model: "claude-sonnet-5", client, deps, onEvent: () => {}, onTrail: async () => {}, maxLaps: 3 });
    expect(r.laps).toBe(3);
    expect(r.cut).toBe("lap_cap");
    expect(r.answer).toContain("stopped");
  });

  it("never calls Airtable during a whole turn (runtime spy, not an import rule)", async () => {
    const hosts: string[] = [];
    const spy = vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => { hosts.push(new URL(String(input)).host); return new Response("{}", { status: 200 }); });
    const client = fakeClient([{ role: "assistant", content: [{ type: "text", text: "done" }], stop_reason: "end_turn", usage: { input_tokens: 1, output_tokens: 1 } }]);
    await runResearchLoop({ question: "q", askerEmail: "a@mds.co", history: [], model: "claude-sonnet-5", client, deps, onEvent: () => {}, onTrail: async () => {} });
    expect(hosts.filter((h) => h.endsWith("airtable.com"))).toEqual([]);
    spy.mockRestore();
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Implement**

```ts
// src/lib/millie/team/loop.ts — #172. A manual tool-use loop over client.messages.stream() (SDK 0.100.1).
// The client is INJECTED so the loop is testable without the network and so the route decides the model.
// Caps: laps, wall clock, output tokens, per-tool abort. Prompt-cache layout: tools (sorted) → system
// [catalog + rules, cache_control on the last block] → messages (asker, date, question, history) — nothing
// per-request ever enters the system block, or every lap pays full price.
import type Anthropic from "@anthropic-ai/sdk";
import { CATALOG_SYSTEM_TEXT } from "./catalog";
import { costUsd, sumUsage, type Usage } from "./pricing";
import { TOOLS, defaultDeps, runTool, type ToolDeps, type TrailStep } from "./tools";

export type LoopEvent =
  | { type: "started" }
  | { type: "tool_call"; n: number; name: string; input: unknown }
  | { type: "tool_result"; step: TrailStep }
  | { type: "text"; delta: string }
  | { type: "lap"; lap: number; usage: Usage; cache_read: number };

export type MessageStreamLike = AsyncIterable<Anthropic.MessageStreamEvent> & { finalMessage(): Promise<Anthropic.Message> };
export type LoopClient = { stream: (params: Anthropic.MessageCreateParamsStreaming) => MessageStreamLike };

const BEHAVIOUR = [
  "You are Millie in TEAM RESEARCH mode for MDS staff. There are no member gates here: answer from everything in the warehouse, exact figures included.",
  "Work like an analyst: look up the catalog before guessing a column, write one SELECT at a time, read the error and repair, aggregate in SQL, and stop when the question is answered.",
  "Every figure you state must come from a query you ran this turn. Name the table it came from. If a query returned no rows, say so — never fill a gap from memory.",
  "Quote the data's age when it matters (synced_at, sent_at, created_time). Airtable is not read live.",
  "Answer in plain Markdown for a colleague: the answer first, then the evidence, short.",
].join("\n");

export async function runResearchLoop(a: {
  question: string; askerEmail: string; history: Array<{ role: "user" | "assistant"; content: string }>;
  model: string; thinking?: boolean; client: LoopClient; deps?: ToolDeps;
  onEvent: (e: LoopEvent) => void; onTrail: (sources: TrailStep[], plan: unknown[]) => Promise<void>;
  signal?: AbortSignal; maxLaps?: number; wallMs?: number; now?: () => number;
}): Promise<{ answer: string; sources: TrailStep[]; plan: unknown[]; laps: number; usage: Required<Usage>; cost_usd: number; cut: string | null }> {
  const deps = a.deps ?? defaultDeps();
  const now = a.now ?? Date.now;
  const maxLaps = a.maxLaps ?? 15;
  const wallMs = a.wallMs ?? 8 * 60_000;
  const t0 = now();
  const sources: TrailStep[] = [];
  const plan: Array<{ lap: number; tool_calls: number }> = [];
  let usage: Required<Usage> = { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 };
  let cut: string | null = null;
  let answer = "";
  let n = 0;

  const system: Anthropic.TextBlockParam[] = [
    { type: "text", text: BEHAVIOUR },
    { type: "text", text: CATALOG_SYSTEM_TEXT, cache_control: { type: "ephemeral" } },
  ];
  const messages: Anthropic.MessageParam[] = [
    ...a.history.map((h) => ({ role: h.role, content: h.content }) as Anthropic.MessageParam),
    { role: "user", content: `Asker: ${a.askerEmail}\nToday (UTC): ${new Date(t0).toISOString().slice(0, 10)}\n\nQuestion: ${a.question}` },
  ];

  a.onEvent({ type: "started" });
  for (let lap = 1; lap <= maxLaps; lap++) {
    if (a.signal?.aborted) { cut = "aborted"; break; }
    if (now() - t0 > wallMs) { cut = "wall_cap"; break; }
    const params: Anthropic.MessageCreateParamsStreaming = {
      model: a.model, max_tokens: 8000, stream: true, system, tools: TOOLS, messages,
      ...(a.thinking ? { thinking: { type: "adaptive" } } : {}),
    };
    const stream = a.client.stream(params);
    let lapText = "";
    for await (const ev of stream) {
      if (ev.type === "content_block_delta" && ev.delta.type === "text_delta") { lapText += ev.delta.text; a.onEvent({ type: "text", delta: ev.delta.text }); }
    }
    const msg = await stream.finalMessage();
    const lapUsage: Usage = { input_tokens: msg.usage.input_tokens, output_tokens: msg.usage.output_tokens, cache_read_input_tokens: msg.usage.cache_read_input_tokens ?? 0, cache_creation_input_tokens: msg.usage.cache_creation_input_tokens ?? 0 };
    usage = sumUsage(usage, lapUsage);
    const toolUses = msg.content.filter((b): b is Anthropic.ToolUseBlock => b.type === "tool_use");
    plan.push({ lap, tool_calls: toolUses.length });
    messages.push({ role: "assistant", content: msg.content });
    if (msg.stop_reason !== "tool_use" || toolUses.length === 0) {
      answer = lapText || msg.content.filter((b): b is Anthropic.TextBlock => b.type === "text").map((b) => b.text).join("");
      a.onEvent({ type: "lap", lap, usage: lapUsage, cache_read: lapUsage.cache_read_input_tokens ?? 0 });
      if (msg.stop_reason === "max_tokens") cut = "max_tokens";
      break;
    }
    const results: Anthropic.ToolResultBlockParam[] = [];
    for (const tu of toolUses) {
      n += 1;
      a.onEvent({ type: "tool_call", n, name: tu.name, input: tu.input });
      const r = await runTool({ id: tu.id, name: tu.name, input: tu.input }, n, deps);
      sources.push(r.step);
      a.onEvent({ type: "tool_result", step: r.step });
      results.push({ type: "tool_result", tool_use_id: tu.id, content: r.result, ...(r.is_error ? { is_error: true } : {}) });
    }
    await a.onTrail(sources, plan);
    messages.push({ role: "user", content: results });
    a.onEvent({ type: "lap", lap, usage: lapUsage, cache_read: lapUsage.cache_read_input_tokens ?? 0 });
    if (lap === maxLaps) cut = "lap_cap";
  }
  if (!answer) answer = `I stopped before finishing (${cut ?? "no answer"}). The queries I ran are in the trail; ask a narrower question or continue from them.`;
  return { answer, sources, plan, laps: plan.length, usage, cost_usd: Math.round(costUsd(a.model, usage) * 10000) / 10000, cut };
}
```

- [ ] **Step 4: Run to verify it passes** — `npx vitest run src/lib/millie/team/loop.test.ts` → PASS; `npx tsc --noEmit` clean (adjust the `Anthropic` type imports to the SDK's exported names if `MessageStreamEvent`/`TextBlockParam` differ in 0.100.1: check `node_modules/@anthropic-ai/sdk/resources/messages/messages.d.ts`).

- [ ] **Step 5: Commit** — `git add src/lib/millie/team/loop.ts src/lib/millie/team/loop.test.ts && git commit -m "#172: the research loop — injected client, caps, cache layout, trail events, Airtable runtime spy"`.

### Task B8: Answer guards — "Data as of" footer and the no-rows flag

**Files:**
- Create: `src/lib/millie/team/footer.ts`, `src/lib/millie/team/footer.test.ts`

**Interfaces:**
- Consumes: `TrailStep` (B5), `ToolDeps.teamSql`.
- Produces: `dataAsOf(teamSql: ToolDeps["teamSql"]): Promise<string>` (a Markdown line), `noRowsFlag(answer: string, sources: TrailStep[]): boolean`, `FRESHNESS_SQL: string`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it, vi } from "vitest";
import { FRESHNESS_SQL, dataAsOf, noRowsFlag } from "./footer";

describe("dataAsOf", () => {
  it("renders the four mirror ages from one fixed query", async () => {
    const teamSql = vi.fn(async (sql: string) => { expect(sql).toBe(FRESHNESS_SQL); return { rows: [{ members: "2026-09-11T02:10:00+00:00", events: "2026-09-11T09:17:00+00:00", whatsapp: "2026-09-11T10:02:00+00:00", facebook: "2026-09-10T21:03:00+00:00" }], row_count: 1, truncated: false }; });
    const line = await dataAsOf(teamSql);
    expect(line).toContain("Data as of");
    expect(line).toContain("members 2026-09-11 02:10Z");
    expect(line).toContain("facebook 2026-09-10 21:03Z");
  });
  it("degrades to a plain sentence when the query fails", async () => {
    const line = await dataAsOf(vi.fn(async () => { throw new Error("boom"); }));
    expect(line).toContain("freshness unknown");
  });
});

describe("noRowsFlag", () => {
  const ok = [{ n: 1, tool: "sql" as const, rows: 3, ms: 5 }];
  const empty = [{ n: 1, tool: "sql" as const, rows: 0, ms: 5 }];
  it("flags an answer that states numbers or lists without a query that returned rows", () => {
    expect(noRowsFlag("There are 602 current members.", empty)).toBe(true);
    expect(noRowsFlag("- Alice\n- Bob", [])).toBe(true);
  });
  it("does not flag when a query returned rows, or when the answer has no numbers or list", () => {
    expect(noRowsFlag("There are 602 current members.", ok)).toBe(false);
    expect(noRowsFlag("I could not find that.", empty)).toBe(false);
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Implement**

```ts
// src/lib/millie/team/footer.ts — #172. Two guards the ROUTE applies to every answer, so they hold even
// on the turn the model forgets: the mirrors' ages, and a visible flag when an answer states numbers
// without a single query having returned rows (the "a timeout looks like no data" trap).
import type { ToolDeps, TrailStep } from "./tools";

export const FRESHNESS_SQL =
  "select (select max(synced_at) from digest.member_profiles_team) as members, (select max(synced_at) from digest.events_catalog) as events, (select max(sent_at) from digest.wa_messages) as whatsapp, (select max(created_time) from digest.fb_posts) as facebook";

function stamp(v: unknown): string {
  const d = new Date(String(v ?? ""));
  return Number.isNaN(d.getTime()) ? "unknown" : d.toISOString().slice(0, 16).replace("T", " ") + "Z";
}

export async function dataAsOf(teamSql: ToolDeps["teamSql"]): Promise<string> {
  try {
    const r = await teamSql(FRESHNESS_SQL, 1);
    const row = (r.rows[0] ?? {}) as Record<string, unknown>;
    return `_Data as of — members ${stamp(row.members)} · events ${stamp(row.events)} · whatsapp ${stamp(row.whatsapp)} · facebook ${stamp(row.facebook)}. Supabase mirror; Airtable not read live._`;
  } catch {
    return "_Data as of — freshness unknown (the freshness query failed)._";
  }
}

export function noRowsFlag(answer: string, sources: TrailStep[]): boolean {
  const anyRows = sources.some((s) => (s.tool === "sql" || s.tool === "semantic") && (s.rows ?? 0) > 0);
  if (anyRows) return false;
  const hasNumber = /\d/.test(answer);
  const hasList = /^\s*([-*•]|\d+\.)\s+/m.test(answer);
  return hasNumber || hasList;
}
```

- [ ] **Step 4: Run to verify it passes**, then commit: `git add src/lib/millie/team/footer.ts src/lib/millie/team/footer.test.ts && git commit -m "#172: data-as-of footer and the no-rows flag (code, not prompt)"`.

### Task B9: The request gate and the route

**Files:**
- Create: `src/lib/millie/team/gate.ts`, `src/lib/millie/team/gate.test.ts`
- Create: `src/app/api/admin/millie/research/route.ts`

**Interfaces:**
- Consumes: `readSessionCookie`, `isStaffEmail`, `config.millie.*` (B1), `dailySpend`/`threadMode`/`openTurn`/`patchTrail`/`closeTurn` (B6), `runResearchLoop` (B7), `dataAsOf`/`noRowsFlag` (B8), `defaultDeps` (B5), `MAX_TEXT` (`@/lib/millie/web-chat`).
- Produces: `gateRequest(input: { email: string | null; askers: string[]; text: string; threadId: string; existingMode: string | null; spend: { turns: number; usd: number }; limits: { turns: number; usd: number } }): { ok: true } | { ok: false; status: number; error: string }` (pure); the route's NDJSON event contract: one JSON object per line — `{type:"started",turn_id,thread_id,transport}` · `{type:"tool_call",n,name,input}` · `{type:"tool_result",step}` · `{type:"text",delta}` · `{type:"hb",t}` · `{type:"answer",...DoorResponse-shaped}` · `{type:"done"}`; or, in poll transport, an immediate JSON body `{turn_id, thread_id, poll:true}`.

- [ ] **Step 1: Write the failing gate test**

```ts
import { describe, expect, it } from "vitest";
import { gateRequest } from "./gate";

const base = { email: "andy@mds.co", askers: ["andy@mds.co"], text: "how many members?", threadId: "t_abc", existingMode: null, spend: { turns: 0, usd: 0 }, limits: { turns: 40, usd: 10 } };

describe("gateRequest — order: session → staff → allowlist → text → thread → budget", () => {
  it("403 without a session or for a non-staff email", () => {
    expect(gateRequest({ ...base, email: null })).toEqual({ ok: false, status: 403, error: "forbidden" });
    expect(gateRequest({ ...base, email: "someone@gmail.com" })).toEqual({ ok: false, status: 403, error: "forbidden" });
  });
  it("403 when the allowlist is empty or does not name the asker (fail-closed)", () => {
    expect(gateRequest({ ...base, askers: [] })).toMatchObject({ ok: false, status: 403 });
    expect(gateRequest({ ...base, askers: ["eugene@mds.co"] })).toMatchObject({ ok: false, status: 403 });
  });
  it("400 on empty, oversize or malformed input", () => {
    expect(gateRequest({ ...base, text: "  " })).toMatchObject({ ok: false, status: 400 });
    expect(gateRequest({ ...base, text: "x".repeat(2001) })).toMatchObject({ ok: false, status: 400 });
    expect(gateRequest({ ...base, threadId: "bad id!" })).toMatchObject({ ok: false, status: 400 });
  });
  it("409 when the thread already belongs to another mode (modes never mix)", () => {
    expect(gateRequest({ ...base, existingMode: "public" })).toMatchObject({ ok: false, status: 409 });
    expect(gateRequest({ ...base, existingMode: "team" })).toEqual({ ok: true });
  });
  it("429 when today's turns or spend are at the limit, with the numbers in the message", () => {
    const r = gateRequest({ ...base, spend: { turns: 40, usd: 1 } });
    expect(r).toMatchObject({ ok: false, status: 429 });
    expect((r as { error: string }).error).toContain("40");
    expect(gateRequest({ ...base, spend: { turns: 3, usd: 10.5 } })).toMatchObject({ ok: false, status: 429 });
  });
  it("passes a well-formed request from an allowed asker", () => {
    expect(gateRequest(base)).toEqual({ ok: true });
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Implement the gate**

```ts
// src/lib/millie/team/gate.ts — #172. The request gate as a pure function so every refusal is a test,
// in the order that matters: identity, staff, allowlist (fail-closed), input, thread mode, budget.
import { isStaffEmail } from "@/lib/staff-otp";
import { MAX_TEXT } from "@/lib/millie/web-chat";

export const THREAD_ID = /^[A-Za-z0-9_-]{1,64}$/;

export function gateRequest(i: { email: string | null; askers: string[]; text: string; threadId: string; existingMode: string | null; spend: { turns: number; usd: number }; limits: { turns: number; usd: number } }): { ok: true } | { ok: false; status: number; error: string } {
  const email = (i.email || "").trim().toLowerCase();
  if (!email || !isStaffEmail(email)) return { ok: false, status: 403, error: "forbidden" };
  if (!i.askers.includes(email)) return { ok: false, status: 403, error: "Team research is not enabled for this account" };
  const text = i.text.trim();
  if (!text) return { ok: false, status: 400, error: "empty message" };
  if (text.length > MAX_TEXT) return { ok: false, status: 400, error: "message too long" };
  if (!THREAD_ID.test(i.threadId)) return { ok: false, status: 400, error: "bad thread_id" };
  if (i.existingMode !== null && i.existingMode !== "team") return { ok: false, status: 409, error: "this thread is not a Team thread — start a new session" };
  if (i.spend.turns >= i.limits.turns) return { ok: false, status: 429, error: `daily limit reached: ${i.spend.turns} of ${i.limits.turns} Team turns today` };
  if (i.spend.usd >= i.limits.usd) return { ok: false, status: 429, error: `daily budget reached: $${i.spend.usd.toFixed(2)} of $${i.limits.usd} today` };
  return { ok: true };
}
```

- [ ] **Step 4: Run to verify it passes**, then commit: `git add src/lib/millie/team/gate.ts src/lib/millie/team/gate.test.ts && git commit -m "#172: the request gate, pure and tested"`.

- [ ] **Step 5: Write the route** (no unit test — it is wiring; its behaviour is proven live in Step 7)

```ts
// src/app/api/admin/millie/research/route.ts — #172 Team research mode.
//
//   POST /api/admin/millie/research  { text, thread_id?, ack_at? }
//     → NDJSON stream (Content-Type application/x-ndjson): started · tool_call · tool_result · text · hb · answer · done
//     → or, when MILLIE_TEAM_TRANSPORT=poll, an immediate { turn_id, thread_id, poll: true } while the loop
//       continues detached and the client polls GET /api/admin/millie/chat?thread_id=
//
// The asker is ALWAYS the session. The n8n door is never called from here: Team mode is a second runtime
// beside Millie, and /api/admin/millie/chat keeps returning 400 for target=team.
import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import { readSessionCookie } from "@/lib/session";
import { config } from "@/lib/config";
import { gateRequest } from "@/lib/millie/team/gate";
import { closeTurn, dailySpend, openTurn, patchTrail, threadMode, type TurnMetrics } from "@/lib/millie/team/log";
import { runResearchLoop, type LoopEvent } from "@/lib/millie/team/loop";
import { dataAsOf, noRowsFlag } from "@/lib/millie/team/footer";
import { defaultDeps } from "@/lib/millie/team/tools";
import { readThread } from "@/lib/millie/web-chat";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 600; // decorative under `next start` on Render; the loop's own wall cap is 8 min

const TRANSPORT: "stream" | "poll" = process.env.MILLIE_TEAM_TRANSPORT === "poll" ? "poll" : "stream";
const HB_MS = 10_000;

export async function POST(req: NextRequest) {
  const sess = await readSessionCookie();
  const email = (sess?.email || "").trim().toLowerCase();
  let body: { text?: unknown; thread_id?: unknown; ack_at?: unknown };
  try { body = await req.json(); } catch { return NextResponse.json({ error: "bad json" }, { status: 400 }); }
  const text = typeof body.text === "string" ? body.text.trim() : "";
  const threadId = typeof body.thread_id === "string" && body.thread_id ? body.thread_id : `t_${Date.now().toString(36)}`;
  const ackAt = typeof body.ack_at === "string" ? body.ack_at : null;
  const day = new Date().toISOString().slice(0, 10);

  const existingMode = email ? await threadMode(email, threadId).catch(() => null) : null;
  const spend = email ? await dailySpend(email, day).catch(() => ({ turns: 0, usd: 0 })) : { turns: 0, usd: 0 };
  const gate = gateRequest({ email: email || null, askers: config.millie.teamAskers, text, threadId, existingMode, spend, limits: { turns: config.millie.teamDailyTurns, usd: config.millie.teamDailyUsd } });
  if (!gate.ok) return NextResponse.json({ error: gate.error }, { status: gate.status });
  if (!config.centurion.anthropicApiKey) return NextResponse.json({ error: "research model not configured" }, { status: 503 });

  const history = (await readThread(email, threadId).catch(() => [])).flatMap((t) => t.role === "member" ? [{ role: "user" as const, content: t.text || "" }] : t.answer_md ? [{ role: "assistant" as const, content: t.answer_md }] : []).slice(-16);
  const { answerId } = await openTurn({ askerEmail: email, threadId, text, ackAt });
  const client = new Anthropic({ apiKey: config.centurion.anthropicApiKey, maxRetries: 2 });
  const model = config.millie.researchModel;
  const deps = defaultDeps();
  const t0 = Date.now();

  const run = async (emit: (e: Record<string, unknown>) => void) => {
    let cutReason: string | null = null;
    let result: Awaited<ReturnType<typeof runResearchLoop>> | null = null;
    try {
      result = await runResearchLoop({
        question: text, askerEmail: email, history, model, client: { stream: (p) => client.messages.stream(p) }, deps,
        onEvent: (e: LoopEvent) => emit(e as unknown as Record<string, unknown>),
        onTrail: (sources, plan) => patchTrail(answerId, sources, plan).catch(() => undefined),
        signal: req.signal,
      });
      cutReason = result.cut;
    } catch (e) {
      cutReason = `error:${e instanceof Error ? e.message.slice(0, 120) : "unknown"}`;
    }
    const sources = result?.sources ?? [];
    const flagged = result ? noRowsFlag(result.answer, sources) : false;
    const footer = await dataAsOf(deps.teamSql);
    const answerMd = (result ? result.answer : "The research turn failed before an answer.") + (flagged ? "\n\n⚠ No query returned rows — verify before use." : "") + "\n\n" + footer;
    const notes = ["team", ...(ackAt ? [`ack:${ackAt}`] : []), ...(cutReason ? [`cut:${cutReason}`] : []), ...(flagged ? ["no_rows"] : [])];
    const metrics: TurnMetrics = {
      model, thinking: false, laps: result?.laps ?? 0, wall_ms: Date.now() - t0,
      input_tokens: result?.usage.input_tokens ?? 0, output_tokens: result?.usage.output_tokens ?? 0,
      cache_read_tokens: result?.usage.cache_read_input_tokens ?? 0, cache_write_tokens: result?.usage.cache_creation_input_tokens ?? 0,
      cost_usd: result?.cost_usd ?? 0, cut: cutReason, transport: TRANSPORT,
    };
    await closeTurn(answerId, { answer_md: answerMd, sources, plan: result?.plan ?? [], metrics, model, latency_ms: metrics.wall_ms, notes }).catch(() => undefined);
    emit({ type: "answer", ok: !cutReason?.startsWith("error:"), thread_id: threadId, turn_id: answerId, mode: "team", answer_md: answerMd, notes, sources, evidence_classes: {}, refused: false, redactions: [], source_summary: { sql: sources.filter((s) => s.tool === "sql").length, semantic: sources.filter((s) => s.tool === "semantic").length }, latency_ms: metrics.wall_ms, metrics });
    emit({ type: "done" });
  };

  if (TRANSPORT === "poll") {
    void run(() => undefined); // detached; per-lap PATCHes persist the trail, the client polls the thread
    return NextResponse.json({ turn_id: answerId, thread_id: threadId, poll: true });
  }

  const enc = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      let closed = false;
      const write = (o: Record<string, unknown>) => { if (!closed) controller.enqueue(enc.encode(JSON.stringify(o) + "\n")); };
      const hb = setInterval(() => write({ type: "hb", t: Math.round((Date.now() - t0) / 1000) }), HB_MS);
      write({ type: "started", turn_id: answerId, thread_id: threadId, transport: "stream" });
      run(write).finally(() => { clearInterval(hb); closed = true; controller.close(); });
    },
  });
  return new Response(stream, { headers: { "Content-Type": "application/x-ndjson", "Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no" } });
}
```

- [ ] **Step 6: Type-check and test** — `npx tsc --noEmit` clean, `npm test` green, `npm run lint` clean.

- [ ] **Step 7: Live proof of the route (after the client in B10 — or with curl now):** merge to `main`, confirm `/api/version`, then with the staff cookie:

```bash
curl -sN -H "Cookie: mds_digest_session=<value>" -H "Content-Type: application/json" \
  -d '{"text":"How many current members do we have per chapter?","thread_id":"t_proof1","ack_at":"2026-09-11T10:00:00Z"}' \
  https://digest.mds.co/api/admin/millie/research | head -40
```
Expected: `started`, `tool_call`, `tool_result`, `hb` lines, an `answer` with the footer, `done`. Then in Supabase: `select id, role, mode, asker_email, notes, metrics->>'cost_usd', jsonb_array_length(sources) from digest.olivia_web_messages where thread_id='t_proof1' order by id` → two rows, `mode='team'`, asker = your email, cost > 0, sources count = the tool calls you saw. A non-allowlisted staff account must get 403; no cookie must get 403.

- [ ] **Step 8: Commit** — `git add src/app/api/admin/millie/research/route.ts && git commit -m "#172: the research route — gate, two log rows, NDJSON stream with heartbeats, poll transport"`.

### Task B10: The client — Team unlock, stream reader, trail panel

**Files:**
- Modify: `src/components/tools/ask-millie/chat-model.ts` (add NDJSON parsing + trail types) and `chat-model.test.ts` (create if absent)
- Create: `src/components/tools/ask-millie/Trail.tsx`
- Modify: `src/components/tools/ask-millie/AskMillie.tsx`
- Modify: `src/lib/tools/ask-millie-help.ts`
- Modify: `src/lib/millie/web-chat.ts` (`ChatTurn`/`WebTurn` gain optional `trail`)

**Interfaces:**
- Consumes: the route's NDJSON contract (B9), `TrailStep` shape (B5).
- Produces: `parseNdjsonChunk(buffer: string, chunk: string): { lines: unknown[]; rest: string }`, `applyResearchEvent(turn: ChatTurn, ev: ResearchEvent): ChatTurn`, `type ResearchEvent = { type: string; [k: string]: unknown }`, `trailFromSources(sources: unknown[]): TrailStep[]` (sources may be legacy `string[]` for non-team turns → `[]`).

- [ ] **Step 1: Write the failing test**

```ts
// src/components/tools/ask-millie/chat-model.test.ts
import { describe, expect, it } from "vitest";
import { applyResearchEvent, parseNdjsonChunk, trailFromSources, type ChatTurn } from "./chat-model";

const turn: ChatTurn = { id: -1, question: "q", answer_md: "", notes: [], sources: [], refused: false, redactions: [], source_summary: {}, at: "2026-09-11T00:00:00Z", trail: [] };

describe("parseNdjsonChunk", () => {
  it("yields complete lines and keeps the partial tail", () => {
    const a = parseNdjsonChunk("", '{"type":"started"}\n{"type":"te');
    expect(a.lines).toEqual([{ type: "started" }]);
    expect(a.rest).toBe('{"type":"te');
    const b = parseNdjsonChunk(a.rest, 'xt","delta":"hi"}\n');
    expect(b.lines).toEqual([{ type: "text", delta: "hi" }]);
    expect(b.rest).toBe("");
  });
  it("skips blank and malformed lines without throwing", () => {
    expect(parseNdjsonChunk("", "\n{bad\n{\"type\":\"hb\",\"t\":10}\n").lines).toEqual([{ type: "hb", t: 10 }]);
  });
});

describe("applyResearchEvent", () => {
  it("appends text deltas, records tool steps, and takes the final answer", () => {
    let t = applyResearchEvent(turn, { type: "text", delta: "60" });
    t = applyResearchEvent(t, { type: "text", delta: "2 members" });
    expect(t.answer_md).toBe("602 members");
    t = applyResearchEvent(t, { type: "tool_result", step: { n: 1, tool: "sql", sql: "select 1", rows: 1, ms: 9 } });
    expect(t.trail).toHaveLength(1);
    t = applyResearchEvent(t, { type: "answer", turn_id: 55, answer_md: "602 members\n\n_Data as of…_", notes: ["team"], sources: [{ n: 1, tool: "sql", sql: "select 1", rows: 1, ms: 9 }], source_summary: { sql: 1 } });
    expect(t.id).toBe(55);
    expect(t.answer_md).toContain("Data as of");
    expect(t.trail).toHaveLength(1);
  });
});

describe("trailFromSources", () => {
  it("reads a Team row's sources as trail steps and a legacy string[] as none", () => {
    expect(trailFromSources([{ n: 1, tool: "sql", sql: "select 1", ms: 1 }])).toHaveLength(1);
    expect(trailFromSources(["https://example.com"])).toEqual([]);
  });
});
```

- [ ] **Step 2: Run to verify it fails** — the three exports do not exist.

- [ ] **Step 3: Implement in `chat-model.ts`** (add at the end; extend `ChatTurn` with `trail?: TrailStep[]` and `shapeTurns` to set `last.trail = trailFromSources(r.sources ?? [])`)

```ts
export type TrailStep = { n: number; tool: "sql" | "catalog" | "semantic"; sql?: string; input?: unknown; rows?: number; ms: number; truncated?: boolean; error?: string };
export type ResearchEvent = { type: string; [k: string]: unknown };

export function parseNdjsonChunk(buffer: string, chunk: string): { lines: unknown[]; rest: string } {
  const all = buffer + chunk;
  const parts = all.split("\n");
  const rest = parts.pop() ?? "";
  const lines: unknown[] = [];
  for (const p of parts) {
    const s = p.trim();
    if (!s) continue;
    try { lines.push(JSON.parse(s)); } catch { /* a torn line is dropped; the final `answer` event carries the whole truth */ }
  }
  return { lines, rest };
}

export function trailFromSources(sources: unknown[]): TrailStep[] {
  return sources.filter((s): s is TrailStep => !!s && typeof s === "object" && typeof (s as TrailStep).tool === "string");
}

export function applyResearchEvent(t: ChatTurn, ev: ResearchEvent): ChatTurn {
  switch (ev.type) {
    case "text": return { ...t, answer_md: (t.answer_md ?? "") + String(ev.delta ?? "") };
    case "tool_result": return { ...t, trail: [...(t.trail ?? []), ev.step as TrailStep] };
    case "answer": return {
      ...t,
      id: typeof ev.turn_id === "number" ? ev.turn_id : t.id,
      answer_md: String(ev.answer_md ?? t.answer_md ?? ""),
      notes: Array.isArray(ev.notes) ? (ev.notes as string[]) : t.notes,
      source_summary: (ev.source_summary as Record<string, number>) ?? t.source_summary,
      trail: trailFromSources(Array.isArray(ev.sources) ? (ev.sources as unknown[]) : []),
    };
    default: return t;
  }
}
```

In `src/lib/millie/web-chat.ts` change `WebTurn.sources` to `sources: unknown[]` (Team rows carry objects, other rows strings) and keep `ChatTurn.sources: string[]` for chips by filtering strings in `shapeTurns`: `last.sources = (r.sources ?? []).filter((s): s is string => typeof s === "string"); last.trail = trailFromSources(r.sources ?? []);`.

- [ ] **Step 4: Run to verify it passes** — `npx vitest run src/components/tools/ask-millie/chat-model.test.ts` → PASS.

- [ ] **Step 5: The Trail panel**

```tsx
// src/components/tools/ask-millie/Trail.tsx — #172. "Queries run": the trail beneath a Team answer.
// It renders the SAME array the log row stores (sources), so screen and log cannot disagree.
"use client";
import { useState } from "react";
import type { TrailStep } from "./chat-model";

export function Trail({ steps }: { steps: TrailStep[] }): React.ReactElement | null {
  const [open, setOpen] = useState<number | null>(null);
  if (!steps.length) return null;
  return (
    <div style={{ marginTop: 10, border: "1px solid var(--hairline)", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ padding: "6px 10px", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.1em", color: "var(--ink-3)", background: "var(--surface-2)" }}>
        QUERIES RUN · {steps.length}
      </div>
      {steps.map((s) => (
        <div key={s.n} style={{ borderTop: "1px solid var(--hairline)" }}>
          <button type="button" onClick={() => setOpen(open === s.n ? null : s.n)} style={{ width: "100%", textAlign: "left", padding: "6px 10px", background: "transparent", border: "none", cursor: "pointer", fontFamily: "inherit", fontSize: 12.5, color: s.error ? "var(--warning)" : "var(--ink-2)" }}>
            #{s.n} {s.tool}{s.rows != null ? ` · ${s.rows} rows` : ""}{s.truncated ? " · truncated" : ""} · {s.ms} ms{s.error ? ` · ${s.error.slice(0, 80)}` : ""}
          </button>
          {open === s.n && (
            <pre style={{ margin: 0, padding: "8px 10px", fontSize: 11.5, whiteSpace: "pre-wrap", background: "var(--surface-3)", fontFamily: "var(--font-mono)" }}>
              {s.sql ?? JSON.stringify(s.input, null, 1)}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 6: Wire `AskMillie.tsx`** — the exact edits:
  1. `const API = "/api/admin/millie/chat";` → add `const RESEARCH_API = "/api/admin/millie/research";`.
  2. `TARGET_COPY.team`: `body` → "Unrestricted — MDS team only. Reads closed WhatsApp groups, private call transcripts, member records and partner terms, and it will name people. Never paste it anywhere outside the team." ; `placeholder` → "Ask the warehouse anything — it will show every query it ran…" ; `empty` → "Every Team answer carries the queries it ran. Read the notice, acknowledge, then ask."
  3. Line ~826 `const disabled = t === "team";` → `const disabled = false;` and drop the `title={disabled ? …}`.
  4. `pickTarget` (line ~408): remove `t === "team" ||` from the early return so Team is selectable; the existing "new session when the thread has answers" logic already enforces modes-never-mix client-side.
  5. `canSend` (line ~430): remove `&& session.target !== "team"`.
  6. Acknowledgement per browser session: on mount, `try { if (sessionStorage.getItem("millie.team.ack")) setAcked((a) => ({ ...a, team: true })); } catch {}`; in the ack button's `onClick`, when `session.target === "team"`, also `try { sessionStorage.setItem("millie.team.ack", new Date().toISOString()); } catch {}`.
  7. In `send()`: if `session.target === "team"`, POST to `RESEARCH_API` with `{ text, thread_id: sentOn, ack_at: sessionStorage.getItem("millie.team.ack") }` and, when `res.headers.get("content-type")?.includes("application/x-ndjson")`, read the body with `getReader()` + `parseNdjsonChunk`, holding a pending `ChatTurn` in state (`id: -(prev.length+1)`, `trail: []`) that `applyResearchEvent` updates on every line; on `answer` replace it, on `done` settle the request; when the response is JSON with `poll: true`, poll `GET ${API}?thread_id=${sentOn}` every 2 s until the last olivia row has `answer_md`, then `setTurns(shapeTurns(body.turns))`. Any non-2xx → the existing `setError` path with the body's `error`.
  8. Render `<Trail steps={turn.trail ?? []} />` under a Team answer's Markdown, above the copy button; the Team copy button copies the answer + "\n\nQueries run:\n" + each step's SQL.
  9. `listThreads` stays unchanged (it already maps `mode==='team'` → the Team target).

- [ ] **Step 7: Help copy** — in `src/lib/tools/ask-millie-help.ts`: change the overview sentence "MDS Team, the unrestricted one, is not switched on yet." to "MDS Team answers from the whole warehouse with no member gates, runs its own research loop rather than the WhatsApp workflow, and shows every query it ran beneath the answer."; replace the FAQ "WHY IS MDS TEAM GREYED OUT?" with "WHAT DOES TEAM MODE READ?" → "Everything in the Supabase warehouse, exact revenue, contact details and billing included, except a short list that stays closed: removal reasons, lifetime value, internal notes, lead scoring. It reads a copy, not Airtable live — the footer says how old the copy is. Every turn is logged under your email with the queries it ran."

- [ ] **Step 8: Verify in the browser** — `npm run build` clean; run locally against `.env.local` with your own email in `MILLIE_TEAM_ASKERS`; open `/admin/ask-millie?target=team`; the amber notice locks the composer; acknowledge; ask "How many current members per chapter?"; watch the trail fill and the answer stream; reload the page and confirm the thread reloads with the same trail (byte-equal to the log row's `sources`). Then merge to `main` (deploy) and repeat once on `digest.mds.co`.

- [ ] **Step 9: Commit** — `git add -A src/components/tools/ask-millie src/lib/tools/ask-millie-help.ts src/lib/millie/web-chat.ts && git commit -m "#172: Team target unlocked — notice + acknowledge, research stream, queries-run trail, poll fallback"`.

### Task B11: The twenty-question proof, then docs and side tickets

**Files:**
- Outside git: `~/mds-team-proof/questions.json`, `references/Q*.json`, `runs/Q*.json`, `scores.md`
- Modify (Scorecard): `OLIVIA_SPRINT_4.md` (#172 block), `OLIVIA_HANDBOOK.md` §3 / §4.3 / §6.2 / §11 / §13, `OLIVIA_SHAREABLE_FIELDS.md` (Team column), `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md`
- Delete (mds-digest-web): `src/app/api/admin/millie/research/probe/route.ts`

- [ ] **Step 1: The questions** — the twenty in `TEAM_RESEARCH_172_DESIGN.md` §8 come from the questions reader; write them to `questions.json` with `<member>` / `<event>` placeholders, the tables each needs, the expected shape and the scoring rule. Have two or three staff read them; record every swap in `scores.md` ("N of 20 replaced by staff").

- [ ] **Step 2: References, back-to-back with the runs** — for each question: write the reference SELECT, run it through the Supabase MCP (read-only), save `{sql, rows, ran_at}`; **immediately** POST the same question through the route with your own staff cookie (never Andy's) via a small runner that captures the `answer` event and the log row's `metrics`. Q3, Q14, Q15 references are hand-verified (the `sender_member` ↔ `at_member_id` bridge and `fb_member_map` coverage were never proven by a join). Q11–Q13 (semantic) get four-judge PASS/PARTIAL/FAIL with hand re-verification of every non-PASS, per `OLIVIA_SMOKE_2026-08-21.md`.

- [ ] **Step 3: Score** — mechanical for Q1–Q9, Q14–Q20 (exact counts, set equality, top-N overlap, required caveat present); re-execute every logged SQL through `team_sql` (every one must run); validate every quoted snippet by position in its source row; pull `metrics` for all twenty; assert `cache_read_tokens > 0` on lap 2 for every multi-lap turn; run the leak gate (exit code). **Bar:** PASS ≥ 16/20 · Q18/Q19/Q20 PASS via `sql_query` · 0 fabricated sources · 20/20 logged with asker + cost + laps · p50 < 90 s · p95 < 5 min · mean cost < $0.30. Every cap hit or cut is recorded with its partial trail as a transport finding.

- [ ] **Step 4: Delete the probe route**, `npm test` + `npm run build` green, merge to `main`.

- [ ] **Step 5: Docs on the same branch** — `OLIVIA_SPRINT_4.md` #172: story unchanged, the AC table (1 exact revenue/contact/billing facts returned — Q18–Q20 · 2 anonymous/member/WhatsApp gain nothing — the 13 gate checks · 3 disclaimer acknowledged per session, every turn stored with asker + mode — the log rows · 4 the Team column — `member_profiles_team`), before/after (0 Team turns → 20 logged; `400 "Team mode ships with #172"` → live behind the allowlist), the proof numbers, the deferred list with triggers (design §10). `OLIVIA_HANDBOOK.md`: §3 a "Team lane = the Render route, not the n8n door" paragraph; §4.3 rows for `millie_team_ro`, `team_sql`, `member_profiles_team`; §6.2 grant table; §11 the ruling row (Team = SQL + catalog + semantic over the deny-list view); §13 the traps learned (set_config binding, views run as owner, the HTTP-edge cap number from A1 check 8). `OLIVIA_SHAREABLE_FIELDS.md`: the Team column — opens exact revenue, contacts, Stripe/billing; keeps closed removal reasons, LTV, internal notes, lead scoring, enforced by the view + gate. Stream log entry + one index line. File the four side tickets from design §11.

- [ ] **Step 6: Close** — Scorecard branch merged to `main` (`git switch main && git pull --ff-only && git merge --no-ff <branch> && git push`), Andy gets one short message: results, the AC checklist, before/after, the deferred list, the MCP follow-on ticket number.

---

## Self-review

**Spec coverage.** Runtime beside Millie (B7, B9) · three tools (B5) · identity from session + fail-closed allowlist (B1, B9) · per-asker budget (B6, B9) · two log rows + per-lap trail + trail rendered = log (B6, B10) · read-only role, deny-list view, `team_sql`, no OTP/olivia_web_messages (A1) · views-run-as-owner check, graph pinned, no new EXECUTE beyond PUBLIC, service_role-only (A2) · Supabase-only proven at runtime (B7 test) · footer + no_rows (B8, B9) · transport probe and poll fallback (A3, B9) · disclaimer, Copy (internal), modes never mix (B9 gate + B10) · Milestone A verdict (A4) · twenty-question proof, bar, artefacts outside git (B11) · docs and side tickets (B11) · Day 0 asks (Global Constraints, design §9). Gap noted: the MCP door and Public-mode team principal are deferred by design, not planned here.

**Placeholder scan.** No TBD/TODO. Every code step carries the code. The only "outside git" items are the proof artefacts, deliberately.

**Type consistency.** `TrailStep` is defined once in `tools.ts` (server) and mirrored by name in `chat-model.ts` (client) with the same fields; `TurnMetrics` in `log.ts` is what the route writes and the `answer` event carries; `LoopClient.stream` matches `client.messages.stream(params)`; `gateRequest`'s input matches what the route assembles; `dailySpend(email, dayIso)` and `threadMode(email, threadId)` are called with those signatures in the route; `parseAskers`/`parseBudget` are imported into `config.ts` from `@/lib/millie/team/config`.
