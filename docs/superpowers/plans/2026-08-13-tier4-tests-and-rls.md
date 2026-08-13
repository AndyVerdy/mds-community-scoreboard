# Tier 4 — Tests and RLS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the SQL layer a test suite below the eval bank, and decide RLS properly rather than leaving 26 tables with row-level security switched on and no rules inside it.

**Architecture:** pgTAP runs inside the database, so the tests live next to what they test and run in CI without a live assistant. Every assertion query written in Tiers 1–3 lifts into it unchanged. RLS is handled second and separately, because it changes the security model and needs an explicit decision, not a migration.

**Tech Stack:** Postgres 17 (Supabase), pgTAP, GitHub Actions, `scripts/olivia_leak_gate.py`.

## Global Constraints

- **This tier is order-independent from Tiers 1–3, and better done early.** It is written last because it is the smallest, not because it is least important. Every finding this week — the key mismatch, the stale routing, the 51 fabricated chapters — survived because nothing below the eval bank tests logic. Running Task 1 *before* Tier 2 would make Tier 2 materially safer.
- **Supabase project id:** `nadtudwuwjhckotrngzn`. Schema: `digest`.
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

### Task 1: A pgTAP suite

**Files:**
- Create: `db/tests/identity.sql`, `db/tests/integrity.sql`, `db/tests/access.sql`, `db/tests/derivations.sql`
- Create: `scripts/run_db_tests.py`, `.github/workflows/db-tests.yml`

**Interfaces:**
- Produces: `python3 scripts/run_db_tests.py` — exits 0 when every test passes, non-zero with the failing test names otherwise.

**Background:** the leak gate's 253 checks verify outputs and permissions, never logic. That is why `content_items.meta.sender_member` could carry two key spaces for months, why `multi_source_v2` routed to stale versions unnoticed, and why 51 fabricated chapter entities sat in a table nobody queried. Below the eval bank — slow, and costing money per run — there is nothing.

- [ ] **Step 1: Write the failing test — a runner that does not exist yet**

```bash
python3 scripts/run_db_tests.py
```
Expected: `No such file or directory`. That is the starting failure.

- [ ] **Step 2: Install pgTAP**

Migration name: `tier4_pgtap_20260813`

```sql
create schema if not exists tap;
create extension if not exists pgtap with schema tap;
revoke all on schema tap from public, anon, authenticated;
grant usage on schema tap to service_role;
```

Own schema, not `public` — pgTAP adds ~100 functions and they should not sit next to application code.

- [ ] **Step 3: Write the first real test, and see it fail**

`db/tests/identity.sql` — start with the bug that started all of this:

```sql
begin;
select tap.plan(3);

-- The two rec key spaces must stay disjoint.
select tap.is(
  (select count(*)::int from digest.members m
   where exists (select 1 from digest.member_profiles p where p.at_member_id = m.airtable_id)),
  0,
  'members.airtable_id and member_profiles.at_member_id are disjoint key spaces');

-- Every sender_member must resolve against the canonical table.
select tap.is(
  (select count(*)::int from digest.content_items ci
   where ci.meta ? 'sender_member'
     and not exists (select 1 from digest.member_profiles p
                     where p.at_member_id = ci.meta->>'sender_member')),
  0,
  'every content_items.sender_member resolves to member_profiles');

-- resolve_asker returns the canonical key for a known phone.
select tap.isnt(
  (select digest.resolve_asker((select phone10 from digest.member_phone_index limit 1))),
  null,
  'resolve_asker resolves a known phone');

select * from tap.finish();
rollback;
```

Run it before Tier 1 is applied and the second test **fails** — 13,450 WhatsApp rows do not resolve. That is the proof the suite works. A test that has never been seen to fail has not been seen to work.

- [ ] **Step 4: Write the runner**

`scripts/run_db_tests.py`:

```python
#!/usr/bin/env python3
"""Run every db/tests/*.sql pgTAP file. Exit non-zero if any test fails.

Each file wraps itself in begin/rollback, so nothing touches production data.
"""
import glob
import os
import sys

import psycopg2  # noqa: F401  (import guarded below for environments without it)


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("SUPABASE_DB_URL not set", file=sys.stderr)
        return 2

    failures = []
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    for path in sorted(glob.glob("db/tests/*.sql")):
        with open(path) as fh:
            sql = fh.read()
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = [r[0] for r in cur.fetchall() if r and r[0]]
        bad = [r for r in rows if r.startswith("not ok")]
        status = "FAIL" if bad else "ok"
        print(f"{status:4}  {path}  ({len(rows)} assertions)")
        for line in bad:
            print(f"      {line}")
        failures.extend(bad)

    conn.close()
    print(f"\n{len(failures)} failing assertion(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```

The repo has no live database password available to this environment (noted in the #65 write-up), so the runner reads `SUPABASE_DB_URL` from the environment and is intended to run in CI and on Andy's machine — not from an agent session.

- [ ] **Step 5: Run it and watch the known-bad test fail**

```bash
SUPABASE_DB_URL=... python3 scripts/run_db_tests.py
```
Expected before Tier 1: `FAIL  db/tests/identity.sql` with the sender_member assertion listed. Record the output.

- [ ] **Step 6: Lift every Tier 1–3 assertion into the suite**

| file | assertions lifted from |
|---|---|
| `db/tests/identity.sql` | Tier 1 Tasks 2, 3, 6; Tier 3 Task 1 |
| `db/tests/integrity.sql` | Tier 1 Task 1; Tier 2 Tasks 1, 2, 3, 4, 5 |
| `db/tests/access.sql` | Tier 2 Task 6; Tier 3 Task 2 |
| `db/tests/derivations.sql` | Tier 1 Tasks 5, 7, 10 |

Each keeps its original SQL; only the wrapper changes. Update `tap.plan(n)` per file.

- [ ] **Step 7: Add regression tests for every bug found this week**

One test per finding, named for it, so none can recur silently:

```sql
-- db/tests/integrity.sql (excerpt)
select tap.is(
  (select count(*)::int from digest.entity_dossier d
   where d.kind='chapter'
     and not exists (select 1 from digest.chapters_catalog c where c.chapter = d.entity_id)),
  0, 'no fabricated chapter dossiers (regression: 51 found 2026-08-13)');

select tap.is(
  (select count(*)::int from pg_proc
   where pronamespace='digest'::regnamespace
     and pg_get_functiondef(oid) ~* 'exception\s+when\s+others\s+then\s+null'),
  0, 'no function swallows every error (regression: 11 found 2026-08-13)');

select tap.is(
  (select count(*)::int from pg_proc
   where pronamespace='digest'::regnamespace and proname='multi_source_v2'
     and pg_get_functiondef(oid) like '%event_lookup_v2%'),
  0, 'multi_source_v2 does not route to stale versions (regression: found 2026-08-13)');
```

- [ ] **Step 8: Wire CI**

`.github/workflows/db-tests.yml`:

```yaml
name: db tests
on:
  push:
    paths: ['db/**', 'scripts/run_db_tests.py']
  pull_request:
    paths: ['db/**']
jobs:
  pgtap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install psycopg2-binary
      - run: python3 scripts/run_db_tests.py
        env:
          SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
```

Andy adds the `SUPABASE_DB_URL` secret — an agent session must not handle the database password.

- [ ] **Step 9: Prove CI catches a real regression**

Open a throwaway branch, reintroduce one bug deliberately (point `multi_source_v2` back at `event_lookup_v2`), push, and confirm the workflow fails. Revert. **A CI job that has never gone red is decoration.**

- [ ] **Step 10: Commit**

```bash
git add db/tests/ scripts/run_db_tests.py .github/workflows/db-tests.yml
git commit -m "feat: pgTAP suite -- the layer between the leak gate and the eval bank

The gate checks outputs and permissions, never logic, which is why the
sender_member key mismatch, the stale multi_source_v2 routing and 51 fabricated
chapter dossiers all survived until someone looked. Every Tier 1-3 assertion lifts
in unchanged, plus a named regression test per bug found this week.

Proven to fail: reintroduced the stale-routing bug on a branch and CI went red."
```

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
   disabled 2026-08-13 after an explicit ruling. See the Tier 4 plan.';
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

The `content_items` policy reuses `can_see` from Tier 3 Task 2 — which is the argument for doing Tier 3 first: without it, the policy would duplicate the four-branch jsonb logic and immediately drift from the functions.

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

## Definition of Done for Tier 4

- [ ] `python3 scripts/run_db_tests.py` exits 0 locally and in CI.
- [ ] CI has been **observed going red** on a deliberately reintroduced bug, then green again.
- [ ] Every assertion from Tiers 1–3 is in the suite, plus one named regression test per bug found on 2026-08-13.
- [ ] RLS has an explicit written ruling from Andy, and the database matches it — no table is left with RLS enabled and no policies.
- [ ] The leak gate still exits 0; it is unchanged and remains the outside-in security check.
- [ ] `SESSION_LOG_OLIVIA.md` entry and `SESSION_LOG.md` index line written.
