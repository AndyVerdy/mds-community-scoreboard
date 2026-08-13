# Phase 5 — The RLS Ruling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the SQL layer a test suite below the eval bank, and decide RLS properly rather than leaving 26 tables with row-level security switched on and no rules inside it.

**Architecture:** pgTAP runs inside the database, so the tests live next to what they test and run in CI without a live assistant. Every assertion query written in Phases 1-4 lifts into it unchanged. RLS is handled second and separately, because it changes the security model and needs an explicit decision, not a migration.

**Tech Stack:** Postgres 17 (Supabase), pgTAP, GitHub Actions, `scripts/olivia_leak_gate.py`.

## Global Constraints

- **This phase is order-independent — it can be taken any time after Phase 1.** It is last because it is a decision, not a fix: nothing here repairs a present gap (see the note in Task 1 Step 1).
- **Supabase project id:** `nadtudwuwjhckotrngzn`. Schema: `digest`.
- **🔴 THE PROD PULSE RUNS BEFORE AND AFTER EVERY STEP.** `python3 scripts/prod_pulse.py` — exit 1 means STOP. Lower risk here than the other phases, but Task 2 can break the portal if a policy is wrong, and the pulse is what catches that.
- **Tests must never write to production data.** Every test runs inside a transaction that rolls back. A test that leaves a row behind is a failed test.
- **The leak gate stays.** pgTAP tests logic; the gate tests the security boundary from outside, as a real anon client. They are complements, not substitutes — do not fold one into the other.
- **`DROP FUNCTION` re-grants EXECUTE to PUBLIC.** Applies here too.
- **RLS is Andy's decision, not a default.** Task 2 Step 1 is a decision gate, not an implementation step.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| migration (extension) | pgTAP installed in its own schema | 1 |
| `db/tests/*.sql` | One test file per subject area | 1 |
| `scripts/run_db_tests.py` | Runner, exit non-zero on failure | 1 |
| `.github/workflows/db-tests.yml` | CI on every push touching `db/` | 1 |
| migration | RLS policies, if Andy rules yes | 2 |

---

> **The pgTAP suite that used to be Task 1 of this file has MOVED to Phase 1.** It is a
> prerequisite for everything, not a closing step. This file now contains only the RLS ruling.

---

### Task 2: Rule on RLS, then implement the ruling

**Files:**
- Modify: `db/rls.sql`, `db/policies.sql` via migration (only if the ruling is yes)

**Interfaces:**
- Produces: either policies on 26 tables, or a written ruling and the RLS flags turned **off** so the schema stops implying protection it does not provide.

**Background:** 26 tables have RLS enabled and **zero policies exist on any of the 58**. No table sets `FORCE ROW LEVEL SECURITY`, and `service_role` carries `BYPASSRLS`, so RLS is doing no work whatsoever. The grant layer is the entire boundary — and it does hold: `anon` and `authenticated` have zero privileges on every table, view and matview, verified live.

So this is not a live vulnerability. It is a schema that **looks** defended in a way it is not, which is its own hazard: the next person to read it will assume a protection that is absent.

- [ ] **Step 1: DECISION GATE — Andy rules, before any code**

Present these three options and get an explicit answer. Do not proceed on an assumption.

> ⚠️ **Measured 2026-08-13, and it reframes this decision:** `service_role` carries `BYPASSRLS`, and
> `anon`/`authenticated` **cannot log in at all** (`rolcanlogin = false`) and hold zero table
> privileges. Everything in the stack runs as `service_role`. So policies added today would protect
> **nothing** on the current architecture — they are preparation for a future in which the portal
> connects as `authenticated`, not remediation of a present gap. Cost options (b) and (c) as
> preparation, and weigh (a) accordingly. See risk register §3.

**(a) Turn RLS off on all 26 tables.** Honest: the grant layer is the boundary, and the schema stops implying otherwise. ~0.5 session. Risk: if a future client ever connects as `authenticated` rather than `service_role`, there is no second line of defence.

**(b) Write real policies on all 26.** Defence in depth: even a leaked `authenticated` token reads nothing it should not. ~2 sessions. Risk: policies that disagree with the function-level gating produce confusing double-filtering, and `service_role` bypasses them anyway so they are hard to test.

**(c) Policies on the member-data tables only**, RLS off elsewhere. The middle path: `members`, `member_profiles`, `member_attributes`, `content_items`, `wa_messages`, `form_responses` get policies; catalogs and config do not. ~1 session.

**Recommended: (c).** It puts a second line of defence exactly where a breach would matter — member data — without pretending a partners catalog needs row-level security. It also keeps the policy count small enough to test honestly.

- [ ] **Step 2: Write the failing test**

```sql
-- db/tests/access.sql (append)
select tap.is(
  (select count(*)::int from pg_class c
   where c.relnamespace='digest'::regnamespace and c.relkind='r'
     and c.relrowsecurity
     and not exists (select 1 from pg_policies p
                     where p.schemaname='digest' and p.tablename=c.relname)),
  0, 'no table has RLS enabled with zero policies');
```

Expected before the fix: **26**.

- [ ] **Step 3a (ruling a): disable RLS and record why**

```sql
do $$
declare t record;
begin
  for t in select c.relname from pg_class c
           where c.relnamespace='digest'::regnamespace and c.relkind='r' and c.relrowsecurity
  loop
    execute format('alter table digest.%I disable row level security', t.relname);
  end loop;
end $$;

comment on schema digest is
  'Access control is enforced by the GRANT layer and by SECURITY DEFINER functions,
   not by RLS. anon and authenticated hold zero table privileges. RLS was enabled on
   26 tables with zero policies, which implied a protection that did not exist;
   disabled 2026-08-13 after an explicit ruling. See the Phase 5 plan.';
```

- [ ] **Step 3b (ruling b or c): write the policies**

For each table in scope, a policy that matches what the functions already enforce. Member-owned data:

```sql
alter table digest.member_profiles force row level security;
create policy member_profiles_self on digest.member_profiles
  for select to authenticated
  using (at_member_id = current_setting('request.jwt.claims', true)::jsonb->>'at_member_id');

alter table digest.content_items force row level security;
create policy content_items_visible on digest.content_items
  for select to authenticated
  using (digest.can_see(
    current_setting('request.jwt.claims', true)::jsonb->>'at_member_id',
    id));
```

The `content_items` policy reuses `can_see` from Phase 4 Task 2 — which is the argument for doing Phase 4 first: without it, the policy would duplicate the four-branch jsonb logic and immediately drift from the functions.

`FORCE ROW LEVEL SECURITY` matters here: without it the table owner bypasses the policy and the test passes for the wrong reason.

- [ ] **Step 4: Prove the policy actually filters**

```sql
begin;
set local role authenticated;
set local request.jwt.claims = '{"at_member_id":"<a real member id>"}';
select count(*) from digest.member_profiles;
-- EXPECTED: 1, not 5931
rollback;
```

A policy that has not been observed to filter has not been observed to work.

- [ ] **Step 5: Confirm the service path is unaffected**

```bash
python3 scripts/olivia_leak_gate.py
```
All 253 checks must still pass — `service_role` carries `BYPASSRLS`, so nothing in the assistant's path should change. If a gate check fails, a policy is filtering something the service path needs.

- [ ] **Step 6: Re-run the test, re-export, commit**

```bash
python3 scripts/run_db_tests.py
python3 scripts/db_export_schema.py
git add db/ tests/
git commit -m "feat: rule on RLS and implement the ruling

26 tables had RLS enabled and zero policies existed across all 58 -- no FORCE, and
service_role holds BYPASSRLS, so RLS was doing no work while implying protection.
Not a live vulnerability (anon and authenticated hold zero table privileges) but a
schema that misleads its next reader.

Ruling: <a/b/c, and Andy's reasoning>.
Proven: <policy filters 5931 rows to 1 / RLS flags now off with the reason in the
schema comment>.
Gate 253 exit 0."
```

---

## Definition of Done for Phase 5

- [ ] `python3 scripts/run_db_tests.py` exits 0 locally and in CI.
- [ ] CI has been **observed going red** on a deliberately reintroduced bug, then green again.
- [ ] Every assertion from Phases 1-4 is in the suite, plus one named regression test per bug found on 2026-08-13.
- [ ] RLS has an explicit written ruling from Andy, and the database matches it — no table is left with RLS enabled and no policies.
- [ ] The leak gate still exits 0; it is unchanged and remains the outside-in security check.
- [ ] `SESSION_LOG_OLIVIA.md` entry and `SESSION_LOG.md` index line written.
