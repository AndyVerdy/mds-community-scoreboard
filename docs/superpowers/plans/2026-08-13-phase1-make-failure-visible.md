# Phase 1 — Make Failure Visible Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the two things that make every later phase detectable — a test suite below the eval bank, and error handling that does not swallow failures.

**Architecture:** Nothing in this phase changes application behaviour. Task 1 adds pgTAP and lifts every assertion from the later phases into it, so a regression fails in CI instead of in production. Task 2 removes `exception when others then null` from eleven functions, so a broken check reports broken instead of green. Both are prerequisites for Phase 3, whose dominant risk is a constraint silently rejecting a live write.

**Tech Stack:** Postgres 17 (Supabase), pgTAP, PL/pgSQL, GitHub Actions, `scripts/prod_pulse.py`, `scripts/olivia_leak_gate.py`, `scripts/db_export_schema.py`.

## Why this phase is first

The three defects found on 2026-08-13 — the `sender_member` key mismatch, `multi_source_v2` routing to stale versions, and 51 fabricated chapter dossiers — all survived because **nothing below the eval bank tests logic**, and because eleven functions swallow every error they hit. Phase 3 adds constraints that reject bad writes the moment they exist; without Task 2, that rejection is absorbed by a trigger and the monitoring stays green. Running any later phase before this one means the way you would notice its main risk does not exist yet.

## Global Constraints

- **🔴 THE PROD PULSE RUNS BEFORE AND AFTER EVERY STEP.** `python3 scripts/prod_pulse.py` — exit 1 means STOP and roll back that step. Re-baseline with `--save-baseline` at the start of the phase.
- **Supabase project id:** `nadtudwuwjhckotrngzn`. Schema: `digest`.
- **The leak gate must exit 0 before and after every task.** `python3 scripts/olivia_leak_gate.py`, baseline 253 checks.
- **Re-export after every DDL** — `python3 scripts/db_export_schema.py` — and commit the `db/` diff with the change.
- **`DROP FUNCTION` re-grants EXECUTE to PUBLIC.** Every drop-and-recreate carries `revoke all on function digest.<fn>(<args>) from public, anon, authenticated;` in the same migration. Prefer `CREATE OR REPLACE`.
- **Members are live.** 55 with active portal sessions; Olivia is answering on WhatsApp. Task 2 touches triggers that fire on live member activity — convert one trigger at a time.
- **One task, one commit.**

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

Migration name: `phase1_pgtap_20260813`

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

Run it before Phase 2 is applied and the second test **fails** — 13,450 WhatsApp rows do not resolve. That is the proof the suite works. A test that has never been seen to fail has not been seen to work.

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
Expected before Phase 2: `FAIL  db/tests/identity.sql` with the sender_member assertion listed. Record the output.

- [ ] **Step 6: Lift every Phases 1-4 assertion into the suite**

| file | assertions lifted from |
|---|---|
| `db/tests/identity.sql` | Phase 2 Tasks 2, 3, 6; Phase 4 Task 1 |
| `db/tests/integrity.sql` | Phase 2 Task 1; Phase 3 Tasks 1, 2, 3, 4, 5 |
| `db/tests/access.sql` | Phase 3 Task 6; Phase 4 Task 2 |
| `db/tests/derivations.sql` | Phase 2 Tasks 5, 7, 10 |

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
chapter dossiers all survived until someone looked. Every Phase 2-3 assertion lifts
in unchanged, plus a named regression test per bug found this week.

Proven to fail: reintroduced the stale-routing bug on a branch and CI went red."
```

---
### Task 2: Fail-open becomes fail-loud

**Files:**
- Modify: `db/functions/tg_member_event_olivia_turn.sql`, `tg_member_event_portal_seen.sql`, `tg_member_event_report.sql`, `olivia_health_check.sql`

**Interfaces:**
- Produces: no signature changes. `olivia_health_check` gains a signal for its own internal failures.

**Background:** all three `member_events` triggers and all eight health-check signals wrap their body in `exception when others then null`. A broken health check therefore reports green, which makes every other "it's fine" in this system unfalsifiable. This is the highest-leverage task in Phase 2 and the reason it is last — the preceding tasks are safer to do while errors are still being swallowed.

**Risk:** a trigger that raises instead of swallowing can fail a write that currently succeeds. The triggers fire on `olivia_messages`, `member_sessions` and `olivia_reports` inserts — a raise there would break a live member conversation. So triggers **log and continue**; only the health check **raises**.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase1_task2_no_silent_swallow.sql
select count(*) as functions_swallowing_all_errors
from pg_proc p
where p.pronamespace = 'digest'::regnamespace
  and pg_get_functiondef(p.oid) ~* 'exception\s+when\s+others\s+then\s+null';
-- EXPECTED AFTER FIX: 0
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **11** (3 triggers + 8 health signals). Record the exact list:

```sql
select p.proname from pg_proc p
where p.pronamespace = 'digest'::regnamespace
  and pg_get_functiondef(p.oid) ~* 'exception\s+when\s+others\s+then\s+null'
order by 1;
```

- [ ] **Step 3: Add a place for swallowed errors to go**

Migration name: `phase1_fail_loud_20260813`

```sql
create table if not exists digest.job_errors (
  id           bigserial primary key,
  source       text not null,
  sqlstate     text,
  message      text,
  context      jsonb,
  occurred_at  timestamptz not null default now()
);
revoke all on table digest.job_errors from public, anon, authenticated;
grant select, insert on table digest.job_errors to service_role;
grant usage, select on sequence digest.job_errors_id_seq to service_role;
comment on table digest.job_errors is
  'Errors that were previously swallowed by exception-when-others-then-null.
   Written by triggers and the health check. Phase 1 Task 2.';
```

- [ ] **Step 4: Convert the three triggers to log-and-continue**

For each of `tg_member_event_olivia_turn`, `tg_member_event_portal_seen`, `tg_member_event_report`, replace the handler. Copy each function body verbatim and change only its final block:

```sql
exception when others then
  insert into digest.job_errors (source, sqlstate, message, context)
  values (TG_NAME, SQLSTATE, SQLERRM,
          jsonb_build_object('table', TG_TABLE_NAME, 'op', TG_OP));
  return coalesce(NEW, OLD);
```

This keeps the write succeeding — the member conversation is never broken — but the failure now exists somewhere a human can find.

- [ ] **Step 5: Convert the eight health signals to raise**

In `olivia_health_check`, each of the eight signal blocks (lines 28, 38, 58, 69, 84, 96, 113, 130) carries `exception when others then null`. Replace each with:

```sql
exception when others then
  insert into digest.job_errors (source, sqlstate, message, context)
  values ('olivia_health_check:<signal-name>', SQLSTATE, SQLERRM, null);
  v_broken := v_broken + 1;
```

and declare `v_broken int := 0;` at the top. After the eighth signal, add a ninth signal that fires on `v_broken > 0`:

```sql
perform digest.olivia_alarm_fire(
  'health-check-broken',
  v_broken > 0,
  format('%s of 8 health signals raised an error and could not be evaluated', v_broken));
```

A health check that cannot evaluate itself now alarms instead of reporting green.

- [ ] **Step 6: Prove the new path bites**

Force one signal to fail and confirm it surfaces rather than passing silently:

```sql
-- temporarily point one signal at a non-existent relation, run the check,
-- then confirm BOTH of these are non-empty, and revert:
select * from digest.job_errors order by occurred_at desc limit 5;
select * from digest.olivia_alarm_state where alarm_key = 'health-check-broken';
```

A test that has not been seen to fail has not been seen to work.

- [ ] **Step 7: Re-run the assertion**

Expected: **0**.

- [ ] **Step 8: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/phase1_task2_no_silent_swallow.sql
git commit -m "fix: 11 functions swallowed every error; a broken health check reported green

Three member_events triggers and all eight health signals wrapped their bodies in
exception-when-others-then-null. Triggers now log to digest.job_errors and
continue -- a member conversation is never broken by an audit write. Health
signals log and increment a counter, and a ninth alarm fires when any signal
could not be evaluated.

Proven by forcing a signal to fail and observing both the job_errors row and the
health-check-broken alarm.

Before: 11 functions swallowing all errors. After: 0.
Gate 253 exit 0."
```

---

## Definition of Done for Phase 1

- [ ] `python3 scripts/run_db_tests.py` exits 0 locally and in CI.
- [ ] CI has been **observed going red** on a deliberately reintroduced bug, then green again.
- [ ] Every assertion from Phases 2–4 is in the suite, plus one named regression test per bug found on 2026-08-13.
- [ ] Zero functions match `exception when others then null` (was 11).
- [ ] `digest.job_errors` exists, is service_role-only, and has been proven to receive a forced failure.
- [ ] A ninth health signal fires when any other signal cannot be evaluated — proven by forcing one to fail.
- [ ] `prod_pulse.py` exits 0, and its `job_errors` warning is gone (the table now exists).
- [ ] Leak gate exits 0; `git diff db/` empty after a fresh export.
- [ ] `SESSION_LOG_OLIVIA.md` entry and `SESSION_LOG.md` index line written.
