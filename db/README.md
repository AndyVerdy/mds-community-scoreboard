# `db/` — the SQL layer, in git

**Generated. Never hand-edit anything in this tree.**

104 Postgres functions run Olivia's retrieval, her access gating, the stats and the
small-cell suppression. Until 2026-08-07 they existed only inside the live Supabase
database: no diff, no review, no history, no restore path independent of the DB. This
tree is the second copy (#65).

| Path | What |
|---|---|
| `functions/` | one file per `digest` function, exact `pg_get_functiondef` output — 104 |
| `views/` | views and materialized views — 8 |
| `triggers.sql` | every trigger, `pg_get_triggerdef` — 18 |
| `policies.sql` | every RLS policy — currently none, and that zero is the record |
| `grants.sql` | who may execute / read / write what: the security boundary |
| `rls.sql` | the row-level-security flag per table |
| `tables.sql` | columns, constraints and indexes — the restore path |

## The workflow

Changes still flow **DB → repo**. Apply your migration, then:

```bash
python3 scripts/db_export_schema.py        # DB -> files
git diff db/                               # this is your code review
git add db && git commit
```

To ask whether the repo and the live database still agree:

```bash
python3 scripts/db_export_schema.py --check   # exit 0 = in sync, exit 1 = drift
```

`com.mds.db.drift` runs that check daily at 05:40 and alerts Slack on drift
(log: `scripts/db_drift.log`). A drift alert means someone changed the database out of
band — re-export, read the diff, and find out who and why before committing it.

**Applying files back to the database (repo → DB) is NOT wired up** — it is the only
direction that can break production and needs its own proof plan and a rehearsed
rollback. Do not improvise it.

## How the export reaches the database

There is no direct-Postgres path from this machine (no psql, no psycopg, no DB password,
no Management-API PAT), and PostgREST cannot read `pg_catalog`. So one read-only function
— `digest.schema_source()`, added 2026-08-07 — hands the exporter the DDL text. It is
STABLE, security INVOKER, returns no member data, and only `service_role` may call it
(anon: `401 permission denied`, asserted by the leak gate).
