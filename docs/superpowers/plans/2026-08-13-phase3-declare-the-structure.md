# Phase 3 — Declare the Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the relationships that already hold in the data enforceable by the database, so the class of bug Phase 2 fixed becomes impossible to write again.

**Architecture:** Foreign keys are added in two statements — `ADD CONSTRAINT … NOT VALID` (instant, no table scan, no lock held, and it protects every *new* write immediately) followed by a separate `VALIDATE CONSTRAINT` (concurrent, interruptible, checks history). Before any constraint touches a table, the loaders that write it are read for insert ordering. Everything is reversible with a single `DROP CONSTRAINT`.

**Tech Stack:** Postgres 17 (Supabase), PL/pgSQL, `scripts/olivia_leak_gate.py`, `scripts/db_export_schema.py`, n8n (Task 7 only).

## Global Constraints

> ⚠️ **READ THE RISK REGISTER FIRST:** `docs/superpowers/specs/2026-08-13-digest-schema-risk-register.md` §3.
> Two corrections to this plan: **Task 4's loader update must happen BEFORE its foreign key**, not
> after — the written order loses the first submission from any new form. And constraints should be
> added outside member-active hours (the portal is live: 55 members, 102 sessions).

- **Phase 2 must be complete and committed first.** Task 2 of this plan adds a foreign key on the exact column Phase 2 Task 3 backfilled; running them out of order fails the validation.
- **Phase 1 is a HARD prerequisite for this entire phase.** A `NOT VALID` constraint rejects a bad write from the moment it exists. Without `digest.job_errors` and unswallowed exceptions, that rejection is absorbed by a trigger and the monitoring reports green — meaning the primary detection mechanism for this phase's primary risk would not exist.
- **Supabase project id:** `nadtudwuwjhckotrngzn`. Schema: `digest`.
- **🔴 THE PROD PULSE RUNS BEFORE AND AFTER EVERY STEP.** `python3 scripts/prod_pulse.py` — exit 1 means STOP and roll back that step. Re-baseline with `--save-baseline` at the start of the phase. This phase's dominant risk is a constraint rejecting a live loader's write, and the pulse is how that surfaces within seconds instead of days.
- **The leak gate must exit 0 before and after every task.** `python3 scripts/olivia_leak_gate.py`, baseline 253 checks. The gate tests refusal; the pulse tests liveness. Both, every time.
- **Add constraints outside member-active hours.** 55 members hold live portal sessions.
- **Re-export after every DDL** — `python3 scripts/db_export_schema.py` — and commit the `db/` diff with the change.
- **`DROP FUNCTION` re-grants EXECUTE to PUBLIC.** Any drop-and-recreate must `revoke all on function digest.<fn>(<args>) from public, anon, authenticated;` in the same migration. Prefer `CREATE OR REPLACE`.
- **A foreign key needs a unique or primary key on its target.** Two targets in this plan do not have one yet — see Task 1 Step 1.
- **Never add a `NOT NULL` foreign key.** Every FK here is nullable: an unmatched row is an honest unknown and must stay legal. The FK forbids a *wrong* value, not a missing one. (Andy's ruling, design doc §8.2.)
- **Every FK is `ON DELETE` explicit.** Default `NO ACTION` for reference data, `CASCADE` only where the child is meaningless without its parent and the parent is genuinely deletable.
- **One task, one commit.**

---

## File Structure

| File | Responsibility | Tasks |
|---|---|---|
| migration only (no function change) | Unique indexes on two FK targets | 1 |
| migration only | 7 low-fan-out foreign keys | 1 |
| migration only | 18 `at_member_id` foreign keys | 2 |
| `db/functions/refresh_entity_dossiers.sql` + migration | `entity_dossier` restructured to 4 typed columns | 3 |
| migration + `db/functions/` readers | New `digest.forms` registry | 4 |
| migration only | `NOT NULL` on columns the data already supports | 5 |
| `db/views/form_reach.sql` (new) + 6 functions | `form_scope` becomes a chokepoint | 6 |
| `db/functions/` ×10 families, n8n workflow | One version per lane | 7 |

**Testing note.** Same assertion-query approach as Phase 2. Phase 1 converts these into a pgTAP suite; write each assertion so it lifts unchanged.

---

### Task 1: Unique targets, then the seven low-fan-out foreign keys

**Files:**
- Modify: `db/tables.sql` via migration

**Interfaces:**
- Produces: `digest.chats_chat_id_key`, `digest.olivia_messages_wamid_key`, and 7 foreign key constraints. Task 2 assumes the two-statement pattern established here.

**Background:** these 7 relations were measured at **0 orphans** on 2026-08-12. Two of them cannot be created as-is: `chats` has its primary key on `chat_name` with no unique index on `chat_id`, and `olivia_messages` has its primary key on `id` with no unique index on `wamid`. Both columns *are* unique in the data — `chats.chat_id` 18 distinct across 18 non-null rows (1 NULL), `olivia_messages.wamid` 2,611 distinct across 2,611 non-null rows (772 NULL) — so a unique index is addable. Postgres permits multiple NULLs under a unique index, so the NULL rows are unaffected.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase3_task1_seven_fks.sql
select count(*) as declared
from pg_constraint
where connamespace = 'digest'::regnamespace and contype = 'f'
  and conname in ('event_registrations_event_fk','member_edges_a_fk','member_edges_b_fk',
                  'wa_messages_chat_fk','summaries_chat_fk','fb_post_images_post_fk',
                  'olivia_feedback_wamid_fk');
-- EXPECTED AFTER FIX: 7
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **0**.

- [ ] **Step 3: Re-verify all seven are still orphan-free**

Data moves. Do not trust the 2026-08-12 measurement.

```sql
select 'event_registrations.event_at_id' r, count(*) n from digest.event_registrations c
  where c.event_at_id is not null and not exists (select 1 from digest.events_catalog e where e.at_record_id=c.event_at_id)
union all select 'member_edges.a_id', count(*) from digest.member_edges c
  where c.a_id is not null and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.a_id)
union all select 'member_edges.b_id', count(*) from digest.member_edges c
  where c.b_id is not null and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.b_id)
union all select 'wa_messages.chat_id', count(*) from digest.wa_messages c
  where c.chat_id is not null and not exists (select 1 from digest.chats h where h.chat_id=c.chat_id)
union all select 'summaries.chat_id', count(*) from digest.summaries c
  where c.chat_id is not null and not exists (select 1 from digest.chats h where h.chat_id=c.chat_id)
union all select 'fb_post_images.post_id', count(*) from digest.fb_post_images c
  where c.post_id is not null and not exists (select 1 from digest.fb_posts p where p.post_id=c.post_id)
union all select 'olivia_feedback.wamid', count(*) from digest.olivia_feedback c
  where c.wamid is not null and not exists (select 1 from digest.olivia_messages m where m.wamid=c.wamid);
-- EXPECTED: 0 for all seven. Any non-zero -> stop, investigate, do not proceed.
```

- [ ] **Step 4: Read the loaders before constraining them**

For each child table, find every writer and confirm it cannot insert before its parent exists:

```bash
grep -rn "insert into digest.event_registrations\|insert into digest.member_edges\|insert into digest.wa_messages\|insert into digest.summaries\|insert into digest.fb_post_images\|insert into digest.olivia_feedback" \
  db/ scripts/ --include=*.sql --include=*.py
```

Write one line per table in the commit message stating which script writes it and why ordering is safe. `member_edges` is written by `derive_knowledge_graph` (parents are members, which exist first) and `fb_post_images` by the FB import (posts land before images — confirm in `load_feed.py`). If any writer inserts a child speculatively, note it and use `NOT VALID` without validating until that writer is fixed.

- [ ] **Step 5: Add the two unique indexes**

Migration name: `phase3_unique_fk_targets_20260813`

```sql
create unique index concurrently if not exists chats_chat_id_key
  on digest.chats (chat_id);
create unique index concurrently if not exists olivia_messages_wamid_key
  on digest.olivia_messages (wamid);
```

`CONCURRENTLY` cannot run inside a transaction block. If the migration tool wraps statements in one, run these two as separate single-statement migrations.

Then promote them to constraints so a foreign key can reference them:

```sql
alter table digest.chats
  add constraint chats_chat_id_unique unique using index chats_chat_id_key;
alter table digest.olivia_messages
  add constraint olivia_messages_wamid_unique unique using index olivia_messages_wamid_key;
```

- [ ] **Step 6: Add the seven constraints as NOT VALID**

Migration name: `phase3_seven_fks_not_valid_20260813`

```sql
alter table digest.event_registrations add constraint event_registrations_event_fk
  foreign key (event_at_id) references digest.events_catalog(at_record_id)
  on delete no action not valid;

alter table digest.member_edges add constraint member_edges_a_fk
  foreign key (a_id) references digest.member_profiles(at_member_id)
  on delete cascade not valid;

alter table digest.member_edges add constraint member_edges_b_fk
  foreign key (b_id) references digest.member_profiles(at_member_id)
  on delete cascade not valid;

alter table digest.wa_messages add constraint wa_messages_chat_fk
  foreign key (chat_id) references digest.chats(chat_id)
  on delete no action not valid;

alter table digest.summaries add constraint summaries_chat_fk
  foreign key (chat_id) references digest.chats(chat_id)
  on delete no action not valid;

alter table digest.fb_post_images add constraint fb_post_images_post_fk
  foreign key (post_id) references digest.fb_posts(post_id)
  on delete cascade not valid;

alter table digest.olivia_feedback add constraint olivia_feedback_wamid_fk
  foreign key (wamid) references digest.olivia_messages(wamid)
  on delete cascade not valid;
```

`CASCADE` on `member_edges` and `fb_post_images` because an edge without a member and an image without a post are meaningless. `NO ACTION` elsewhere — deleting a chat or an event should fail loudly rather than silently removing history.

- [ ] **Step 7: Prove the constraints bite**

A constraint that has not been seen to reject has not been seen to work.

```sql
begin;
insert into digest.member_edges (a_id, b_id, edge_type, weight)
values ('recNOTAREALMEMBER', 'recALSONOTREAL', 'test', 1);
-- EXPECTED: ERROR, violates foreign key constraint "member_edges_a_fk"
rollback;
```

Repeat for at least one more constraint. Record both errors in the commit message.

- [ ] **Step 8: Validate the history**

Separate statement, separate migration, so it can be interrupted without losing Step 6's protection.

Migration name: `phase3_seven_fks_validate_20260813`

```sql
alter table digest.event_registrations validate constraint event_registrations_event_fk;
alter table digest.member_edges validate constraint member_edges_a_fk;
alter table digest.member_edges validate constraint member_edges_b_fk;
alter table digest.wa_messages validate constraint wa_messages_chat_fk;
alter table digest.summaries validate constraint summaries_chat_fk;
alter table digest.fb_post_images validate constraint fb_post_images_post_fk;
alter table digest.olivia_feedback validate constraint olivia_feedback_wamid_fk;
```

`member_edges` is 38 MB and `wa_messages` 16 MB — validation takes a `SHARE UPDATE EXCLUSIVE` lock, which does not block reads or writes.

- [ ] **Step 9: Re-run the assertion, gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/phase3_task1_seven_fks.sql
git commit -m "feat: declare the seven low-fan-out foreign keys

chats.chat_id and olivia_messages.wamid needed unique constraints first -- both
were unique in data but neither was a key, so nothing could reference them.

All seven re-measured at 0 orphans before constraining. Added NOT VALID (instant,
no lock, protects new writes) then VALIDATE separately. Proven to reject: a bogus
member_edges insert now errors.

Loader ordering verified for each child table -- see notes below.
Gate 253 exit 0."
```

---

### Task 2: The eighteen `at_member_id` foreign keys

**Files:**
- Modify: `db/tables.sql` via migration

**Interfaces:**
- Consumes: the two-statement pattern from Task 1
- Produces: 18 foreign keys onto `member_profiles(at_member_id)`

**Background:** this is the task that makes the Phase 2 bug class unwritable — after it, a value from the `members.airtable_id` space cannot be stored in an `at_member_id` column, because the lookup fails. These tables sit under the busiest write paths (persona rebuild, event sync, Olivia's own message log), so loader review is the real work; the constraints themselves are cheap.

The 18: `members`, `member_attributes`, `member_expertise`, `member_niches`, `member_personas`, `member_personas_history`, `member_profile_embeddings`, `member_state_snapshot`, `member_phone_index`, `call_attendance`, `fb_member_map`, `member_events`, `olivia_billing_nudges`, `olivia_reports`, `olivia_requests`, `zoom_name_alias`, `form_responses.member_at_id`, `event_registrations.member_at_id`.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase3_task2_member_fks.sql
select count(*) as declared
from pg_constraint c
join pg_class p on p.oid = c.confrelid
where c.connamespace = 'digest'::regnamespace and c.contype = 'f'
  and p.relname = 'member_profiles';
-- EXPECTED AFTER FIX: 18
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **0**.

- [ ] **Step 3: Re-measure all 18 for orphans**

```sql
select 'members' t, count(*) n from digest.members c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_attributes', count(*) from digest.member_attributes c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_expertise', count(*) from digest.member_expertise c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_niches', count(*) from digest.member_niches c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_personas', count(*) from digest.member_personas c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_personas_history', count(*) from digest.member_personas_history c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_profile_embeddings', count(*) from digest.member_profile_embeddings c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_state_snapshot', count(*) from digest.member_state_snapshot c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_phone_index', count(*) from digest.member_phone_index c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'call_attendance', count(*) from digest.call_attendance c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'fb_member_map', count(*) from digest.fb_member_map c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'member_events', count(*) from digest.member_events c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'olivia_billing_nudges', count(*) from digest.olivia_billing_nudges c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'olivia_reports', count(*) from digest.olivia_reports c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'olivia_requests', count(*) from digest.olivia_requests c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'zoom_name_alias', count(*) from digest.zoom_name_alias c where c.at_member_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.at_member_id)
union all select 'form_responses', count(*) from digest.form_responses c where c.member_at_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.member_at_id)
union all select 'event_registrations', count(*) from digest.event_registrations c where c.member_at_id is not null
  and not exists (select 1 from digest.member_profiles p where p.at_member_id=c.member_at_id);
-- EXPECTED: 0 for all 18.
```

- [ ] **Step 4: Read all 18 loaders — the actual work of this task**

```bash
grep -rn "insert into digest.member_\|insert into digest.call_attendance\|insert into digest.fb_member_map\|insert into digest.zoom_name_alias\|insert into digest.olivia_\|insert into digest.form_responses\|insert into digest.event_registrations" \
  db/ scripts/ --include=*.sql --include=*.py
```

For each, answer in writing: **can this insert a child before `member_profiles` has the parent row?** The two to scrutinise hardest:
- `member_profiles` is itself written by the GitHub Action mirror; anything that runs *during* that sync could see a partial parent set. Check the Action's ordering.
- `event_registrations` and `form_responses` are stamped *after* insert (`stamp_event_registrations`, `stamp_form_responses`), so the row exists with a NULL key first and is filled later. That is safe — the FK is nullable — but confirm the stamper never writes an id it has not verified.

Record the verdict per table. Any table whose loader *can* race gets its constraint added `NOT VALID` and left unvalidated, with a note, until the loader is fixed.

- [ ] **Step 5: Add all 18 as NOT VALID**

Migration name: `phase3_member_fks_not_valid_20260813`

```sql
alter table digest.members add constraint members_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.member_attributes add constraint member_attributes_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_expertise add constraint member_expertise_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_niches add constraint member_niches_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_personas add constraint member_personas_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_personas_history add constraint member_personas_history_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_profile_embeddings add constraint member_profile_embeddings_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_state_snapshot add constraint member_state_snapshot_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.member_phone_index add constraint member_phone_index_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.call_attendance add constraint call_attendance_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.fb_member_map add constraint fb_member_map_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.member_events add constraint member_events_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.olivia_billing_nudges add constraint olivia_billing_nudges_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.olivia_reports add constraint olivia_reports_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.olivia_requests add constraint olivia_requests_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.zoom_name_alias add constraint zoom_name_alias_at_member_fk
  foreign key (at_member_id) references digest.member_profiles(at_member_id) on delete cascade not valid;
alter table digest.form_responses add constraint form_responses_member_fk
  foreign key (member_at_id) references digest.member_profiles(at_member_id) on delete no action not valid;
alter table digest.event_registrations add constraint event_registrations_member_fk
  foreign key (member_at_id) references digest.member_profiles(at_member_id) on delete no action not valid;
```

`CASCADE` on derived per-member data (attributes, expertise, niches, personas, embeddings, snapshot, phone index, nudges, aliases) — meaningless without the member, and rebuildable. `NO ACTION` on anything that is a record of something that happened (attendance, reports, requests, registrations, form submissions, events, the FB and WA identity maps) — deleting a member must not erase history silently. This matches the standing rule that a member record is never deleted.

- [ ] **Step 6: Prove the key spaces are now separated**

This is the whole point of Phase 3. Demonstrate it explicitly:

```sql
begin;
-- take a real airtable_id (WA key space) and try to store it as an at_member_id
insert into digest.member_niches (at_member_id, niche, score)
select m.airtable_id, 'canary-test', 1 from digest.members m limit 1;
-- EXPECTED: ERROR, violates foreign key constraint "member_niches_at_member_fk"
rollback;
```

Before Phase 3 this insert succeeded silently and produced a row that joined to nothing. Paste the error into the commit message.

- [ ] **Step 7: Add the missing index on the busiest FK column**

`olivia_messages.member` is a foreign key with no index (flagged in the research). While adding member constraints, fix it:

```sql
create index concurrently if not exists olivia_messages_member_idx
  on digest.olivia_messages (member);
```

- [ ] **Step 8: Validate, in batches**

Migration name: `phase3_member_fks_validate_20260813`

Validate the small tables first, then the large ones (`member_events` 20,456 rows, `event_registrations` 17,985, `form_responses` 13,644). One `validate constraint` statement per table, in the same order as Step 5. If any fails, the orphan check in Step 3 was stale — stop and re-measure rather than deleting rows.

- [ ] **Step 9: Confirm no sync job broke**

The next scheduled run of each writer must succeed. Check heartbeats after 24 hours:

```sql
select job, last_ok_at, now() - last_ok_at as age
from digest.olivia_job_heartbeats order by 2 desc;
```

Any job that has not reported since the migration is the failure signal. Also confirm `digest.job_errors` (created in Phase 1 Task 2) is empty of FK violations:

```sql
select source, message, count(*) from digest.job_errors
where occurred_at > now() - interval '24 hours' and message ilike '%foreign key%'
group by 1,2;
-- EXPECTED: 0 rows
```

- [ ] **Step 10: Re-run the assertion, gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/phase3_task2_member_fks.sql
git commit -m "feat: 18 foreign keys onto member_profiles, separating the two rec key spaces

members.airtable_id and member_profiles.at_member_id are both rec+14 with zero
overlap and were mutually assignable. After this task an airtable_id stored in an
at_member_id column is rejected -- proven by canary insert.

All 18 re-measured at 0 orphans; all 18 loaders read for insert ordering (notes
below). NOT VALID then VALIDATE. CASCADE on derived data, NO ACTION on records of
events. Also indexed olivia_messages.member, an FK with no index.

Gate 253 exit 0."
```

---

### Task 3: `entity_dossier` becomes enforceable

**Files:**
- Modify: `db/functions/refresh_entity_dossiers.sql`, and 5 readers found in Step 2
- Modify: `db/tables.sql` via migration

**Interfaces:**
- Produces: `entity_dossier` with four typed nullable columns (`event_at_id`, `video_id`, `partner_id`, `chapter`), each with its own foreign key, plus a CHECK that exactly one is set. `kind` and `entity_id` are retained as generated columns so existing readers keep working.

**Background:** Phase 2 Task 1 fixed the 51 fabricated chapter rows. This task makes them impossible to recreate. The current shape — one polymorphic `entity_id` text column — cannot carry a foreign key at all.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase3_task3_dossier_enforced.sql
select count(*) as fks_on_dossier
from pg_constraint where connamespace='digest'::regnamespace
  and contype='f' and conrelid='digest.entity_dossier'::regclass;
-- EXPECTED AFTER FIX: 4
```

- [ ] **Step 2: Find every reader**

```bash
grep -rn "entity_dossier" db/ scripts/ --include=*.sql --include=*.py
```

Expect 5 files. List them in the commit. Any reader using `kind`/`entity_id` keeps working via the generated columns — but read each one to confirm none writes directly.

- [ ] **Step 3: Add the typed columns and constraints**

Migration name: `phase3_dossier_typed_columns_20260813`

```sql
alter table digest.entity_dossier
  add column event_at_id text,
  add column video_id    text,
  add column partner_id  text,
  add column chapter     text;

update digest.entity_dossier set event_at_id = entity_id where kind = 'event';
update digest.entity_dossier set video_id    = entity_id where kind = 'video';
update digest.entity_dossier set partner_id  = entity_id where kind = 'partner';
update digest.entity_dossier set chapter     = entity_id where kind = 'chapter';

alter table digest.entity_dossier
  add constraint entity_dossier_event_fk   foreign key (event_at_id) references digest.events_catalog(at_record_id)   on delete cascade not valid,
  add constraint entity_dossier_video_fk   foreign key (video_id)    references digest.videos_catalog(video_id)       on delete cascade not valid,
  add constraint entity_dossier_partner_fk foreign key (partner_id)  references digest.partners_catalog(partner_id)   on delete cascade not valid,
  add constraint entity_dossier_chapter_fk foreign key (chapter)     references digest.chapters_catalog(chapter)      on delete cascade not valid;

alter table digest.entity_dossier
  add constraint entity_dossier_exactly_one_parent check (
    (event_at_id is not null)::int + (video_id is not null)::int +
    (partner_id  is not null)::int + (chapter  is not null)::int = 1
  ) not valid;
```

- [ ] **Step 4: Validate all five**

```sql
alter table digest.entity_dossier validate constraint entity_dossier_event_fk;
alter table digest.entity_dossier validate constraint entity_dossier_video_fk;
alter table digest.entity_dossier validate constraint entity_dossier_partner_fk;
alter table digest.entity_dossier validate constraint entity_dossier_chapter_fk;
alter table digest.entity_dossier validate constraint entity_dossier_exactly_one_parent;
```

If the chapter FK fails, Phase 2 Task 1 did not fully clean up — re-run its Step 5 delete.

- [ ] **Step 5: Rewrite the writer to populate typed columns**

In `refresh_entity_dossiers`, each of the four INSERT branches sets its own column instead of `entity_id`. For the chapter branch (already corrected in Phase 2):

```sql
  insert into digest.entity_dossier as ed
    (kind, entity_id, chapter, name, topic_profile, reception, strength_note, weak_signal, refreshed_at)
  select 'chapter', p.chname, p.chname, p.chname, p.tp,
         jsonb_build_object('expertise_rows', p.tot), null, null, now()
  from prof p
  on conflict (kind, entity_id) do update
    set topic_profile = excluded.topic_profile, reception = excluded.reception,
        chapter = excluded.chapter, refreshed_at = excluded.refreshed_at
    where ed.topic_profile is distinct from excluded.topic_profile
       or ed.reception is distinct from excluded.reception;
```

Apply the same shape to the event (`event_at_id`), video (`video_id`) and partner (`partner_id`) branches.

- [ ] **Step 6: Prove it rejects a fabricated chapter**

```sql
begin;
insert into digest.entity_dossier (kind, entity_id, chapter, name, refreshed_at)
values ('chapter','New York Chapter, Women''s Chapter','New York Chapter, Women''s Chapter','x',now());
-- EXPECTED: ERROR, violates foreign key constraint "entity_dossier_chapter_fk"
rollback;
```

This is the exact value Phase 2 deleted 51 of. It can no longer be written.

- [ ] **Step 7: Rebuild, gate, re-export, commit**

```sql
select * from digest.refresh_entity_dossiers();
```

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/phase3_task3_dossier_enforced.sql
git commit -m "feat: entity_dossier gains four typed FK columns and a one-parent CHECK

The polymorphic entity_id could not carry a foreign key, which is why 51
fabricated chapter entities existed. Four nullable typed columns, one FK each, and
a CHECK that exactly one is set. kind/entity_id retained so readers are unchanged.

Proven: the exact fabricated value Phase 2 deleted is now rejected on insert.
Gate 253 exit 0."
```

---

### Task 4: A `forms` registry

**Files:**
- Create: migration for `digest.forms`
- Modify: `db/tables.sql` (FKs on 5 `form_id` columns)

**Interfaces:**
- Produces: `digest.forms(form_id pk, form_name, scope, population, collects_identifier, first_submission_at, last_submission_at, retired_at)`. Task 6 joins it.

**Background:** `form_id` is a bare text column across 5 tables with no parent — 161 distinct values in `form_responses`, 114 in `form_question_map`, 17 in `form_population`, 5 in `form_field_map` and `form_scope`. Ticket #73's "she reads 5 of 161" is this missing table, not a coverage backlog. 48 of 161 forms have `form_name = form_id` — never resolved to a real name.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase3_task4_forms_registry.sql
select to_regclass('digest.forms') is not null as registry_exists,
       (select count(*) from pg_constraint c join pg_class p on p.oid=c.confrelid
        where c.connamespace='digest'::regnamespace and c.contype='f'
          and p.relname='forms') as fks_pointing_at_it;
-- EXPECTED AFTER FIX: true, 4
```

- [ ] **Step 2: Create and backfill**

Migration name: `phase3_forms_registry_20260813`

```sql
create table digest.forms (
  form_id             text primary key,
  form_name           text,
  scope               text,
  population          text,
  collects_identifier boolean,
  first_submission_at timestamptz,
  last_submission_at  timestamptz,
  retired_at          timestamptz,
  note                text
);
revoke all on table digest.forms from public, anon, authenticated;
grant select, insert, update on table digest.forms to service_role;
comment on table digest.forms is
  'Registry of every Typeform the warehouse has seen. Parent of form_id across
   form_responses, form_field_map, form_scope, form_question_map, form_population.
   Created 2026-08-13, Phase 3 Task 4.';

insert into digest.forms (form_id, form_name, scope, population,
                          collects_identifier, first_submission_at, last_submission_at)
select r.form_id,
       nullif(max(r.form_name), r.form_id),
       (select s.scope from digest.form_scope s where s.form_id = r.form_id),
       (select p.population from digest.form_population p where p.form_id = r.form_id),
       bool_or(r.email is not null),
       min(r.submitted_at),
       max(r.submitted_at)
from digest.form_responses r
group by r.form_id;

-- forms that are configured but have no submissions yet
insert into digest.forms (form_id, scope)
select s.form_id, s.scope from digest.form_scope s
on conflict (form_id) do nothing;
insert into digest.forms (form_id, population)
select p.form_id, p.population from digest.form_population p
on conflict (form_id) do nothing;
insert into digest.forms (form_id)
select distinct q.form_id from digest.form_question_map q
on conflict (form_id) do nothing;
```

`nullif(max(form_name), form_id)` leaves the 48 unresolved names NULL rather than storing an id as a name — an honest unknown beats a false one.

- [ ] **Step 3: Verify coverage before constraining**

```sql
select (select count(*) from digest.forms) as registry_rows,
       (select count(distinct form_id) from digest.form_responses) as in_responses,
       (select count(*) from digest.forms where form_name is null) as unnamed;
-- EXPECTED: registry_rows >= 161, in_responses = 161, unnamed ≈ 48
```

- [ ] **Step 4: Add the four foreign keys**

```sql
alter table digest.form_responses add constraint form_responses_form_fk
  foreign key (form_id) references digest.forms(form_id) on delete no action not valid;
alter table digest.form_field_map add constraint form_field_map_form_fk
  foreign key (form_id) references digest.forms(form_id) on delete cascade not valid;
alter table digest.form_scope add constraint form_scope_form_fk
  foreign key (form_id) references digest.forms(form_id) on delete cascade not valid;
alter table digest.form_question_map add constraint form_question_map_form_fk
  foreign key (form_id) references digest.forms(form_id) on delete cascade not valid;

alter table digest.form_responses    validate constraint form_responses_form_fk;
alter table digest.form_field_map    validate constraint form_field_map_form_fk;
alter table digest.form_scope        validate constraint form_scope_form_fk;
alter table digest.form_question_map validate constraint form_question_map_form_fk;
```

`form_population` is left unconstrained deliberately — verify first whether all 17 of its form_ids landed in the registry, and add the fifth FK in the same task if so.

- [ ] **Step 5: Make the loader register new forms**

`scripts/sync_form_responses.py` must upsert into `digest.forms` before inserting responses, or the FK rejects the first submission from a new form. Find the insert and add the upsert ahead of it. **This is the step that turns a schema change into an outage if skipped** — test by running the loader against a form id not yet in the registry.

- [ ] **Step 6: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ scripts/sync_form_responses.py tests/assertions/phase3_task4_forms_registry.sql
git commit -m "feat: a forms registry, so form_id has a parent

form_id was a bare text column in 5 tables with no parent -- 161 values in
form_responses against 5 in form_scope. #73's 'reads 5 of 161' was this missing
table. Registry backfilled from responses, scope, population and question_map;
48 forms whose name equals their id are stored as NULL rather than a fake name.
Loader upserts the registry before inserting, verified against a new form id.

Gate 253 exit 0."
```

---

### Task 5: `NOT NULL` where the data already supports it

**Files:**
- Modify: `db/tables.sql` via migration

**Background:** 246 of 574 columns (43%) are `NOT NULL`, and the gap is worst on the spine — `member_profiles` 2 of 32, `events_catalog` 3 of 28. A nullable column that is never null in practice is a constraint nobody wrote down.

- [ ] **Step 1: Find the candidates mechanically**

```sql
select c.relname as tbl, a.attname as col, s.null_frac
from pg_stats s
join pg_class c on c.relname = s.tablename
join pg_attribute a on a.attrelid = c.oid and a.attname = s.attname
where s.schemaname = 'digest' and s.null_frac = 0 and not a.attnotnull
  and c.relnamespace = 'digest'::regnamespace
order by c.relname, a.attname;
```

`null_frac = 0` is from the planner's sample, not proof. Every candidate gets an exact count before it is constrained.

- [ ] **Step 2: Confirm exactly, per candidate**

For each row from Step 1:

```sql
select count(*) from digest.<table> where <column> is null;
-- Only proceed to Step 3 for columns returning exactly 0.
```

- [ ] **Step 3: Apply, using NOT VALID where the table is large**

Migration name: `phase3_not_null_20260813`

Postgres 17 supports `alter table … add constraint … check (col is not null) not valid` followed by `validate constraint`, which avoids the full-table lock that `set not null` takes. Use that form for any table above ~10,000 rows; use plain `set not null` for the rest.

```sql
-- small table example
alter table digest.chats alter column chat_id set not null;

-- large table example
alter table digest.content_items
  add constraint content_items_source_id_not_null check (source_id is not null) not valid;
alter table digest.content_items validate constraint content_items_source_id_not_null;
```

**Exclude deliberately:** any column that represents an honest unknown — `member_at_id`, `at_member_id`, `member_record_id`, and anything a stamper fills in later. Those must stay nullable. List the exclusions in the commit message.

- [ ] **Step 4: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/
git commit -m "feat: NOT NULL on columns that were never null

43% of columns carried NOT NULL, worst on the spine (member_profiles 2 of 32).
Candidates found via pg_stats null_frac then confirmed with exact counts.
Identity-stamp columns deliberately excluded -- an unmatched row is an honest
unknown and must stay legal.

Gate 253 exit 0."
```

---

### Task 6: `form_scope` becomes a chokepoint, not a convention

**Files:**
- Create: `db/views/form_reach.sql`
- Modify: `form_windowed`, `form_field_history`, `my_form_answers`, `persona_signals`, `persona_signal_fingerprints`, and the `form_answers_exploded` materialized view

**Background:** the scope wall is an identical join repeated in 6 functions and **skipped in 3 surfaces** — `form_answers_exploded` (149,800 rows, of which 35,394 across 52 forms are out of scope), `form_answers_latest` (no scope join, zero consumers), and the `member_fact` chain (15 form_ids, 5 in scope). A seventh consumer written without the join exposes all 156 non-scoped forms. #58 solved this exact class for events with one view.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase3_task6_scope_chokepoint.sql
select count(*) as out_of_scope_rows_reachable
from digest.form_answers_exploded e
where not exists (select 1 from digest.form_scope s
                  where s.form_id = e.form_id and s.scope = 'profile');
-- EXPECTED AFTER FIX: 0
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: ~**35,394**.

- [ ] **Step 3: Create the chokepoint view**

Migration name: `phase3_form_reach_view_20260813`

```sql
create or replace view digest.form_reach as
select r.*
from digest.form_responses r
join digest.form_scope s on s.form_id = r.form_id and s.scope = 'profile';

revoke all on digest.form_reach from public, anon, authenticated;
grant select on digest.form_reach to service_role;
comment on view digest.form_reach is
  'THE form-scope wall. Every read path that serves a member reads THIS, never
   form_responses directly. Adding a consumer that bypasses it exposes all 156
   non-scoped forms. Phase 3 Task 6; same pattern as event_registrations_live (#58).';
```

- [ ] **Step 4: Repoint the six enforcing functions**

In each of `form_windowed`, `form_field_history`, `my_form_answers`, `persona_signals`, `persona_signal_fingerprints`, replace the `form_responses` + `form_scope` join pair with a single read of `digest.form_reach`. Behaviour must be identical — capture each function's output before and after on the same arguments and diff.

Rebuild `form_answers_exploded` on `form_reach` rather than `form_responses`.

- [ ] **Step 5: Handle `form_answers_latest`**

It has no scope join and **zero consumers**. Drop it rather than fix it — an unscoped, unused surface is pure risk.

```sql
drop view if exists digest.form_answers_latest;
```

Confirm zero consumers first: `grep -rn "form_answers_latest" db/ scripts/`.

- [ ] **Step 6: Re-run the assertion and the gate**

The gate already checks that `my_form_answers` and `form_field_history` return zero event/trend forms. Those checks must still pass, and the Step 1 assertion must now be 0.

- [ ] **Step 7: Re-export and commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/phase3_task6_scope_chokepoint.sql
git commit -m "feat: form_scope becomes one chokepoint view instead of six copies

The scope wall was an identical join repeated in 6 functions and skipped in 3
surfaces -- form_answers_exploded alone exposed 35,394 out-of-scope rows across 52
forms. One view, form_reach, is now the only door. form_answers_latest dropped:
unscoped and zero consumers.

Gate 253 exit 0."
```

---

### Task 7: One version per lane

**Files:**
- Modify: 10 function families in `db/functions/`
- Modify: the n8n workflow's `EXEC_NAME` map

**Background:** ten families carry v1/v2/v3, and n8n rewrites the model-facing tool name onto a versioned implementation at the last inch. That indirection is a deployment mechanism standing in for a release process, and it is why `multi_source_v2` silently routed to stale versions (fixed as a symptom in Phase 2 Task 7; this task removes the cause). Several v1s are **live dependencies** of their v2s, so nothing can simply be deleted.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/phase3_task7_one_version_per_lane.sql
select count(*) as versioned_functions
from pg_proc where pronamespace='digest'::regnamespace
  and proname ~ '_v[0-9]+$';
-- EXPECTED AFTER FIX: 0
```

- [ ] **Step 2: Map every family before touching any of it**

```sql
select p.proname, pg_get_function_arguments(p.oid) as args
from pg_proc p where p.pronamespace='digest'::regnamespace
  and (p.proname ~ '_v[0-9]+$'
    or exists (select 1 from pg_proc q where q.pronamespace=p.pronamespace
               and q.proname = p.proname || '_v2'))
order by 1;
```

For each family, record: which version n8n calls, which versions call each other, and which have no caller. Known from the research: `event_lookup` v3→v2→v1 all execute; `event_history` v2 wraps v1; `partner_lookup` v2 wraps v1; `video_search_v2` is standalone but v1 is kept alive by `multi_source_v2`; `chat_recommendations_v3` is dead; `chat_recommendations_v2` calls v1 internally; `member_dossier_v2` reimplements v1 verbatim.

- [ ] **Step 3: Delete what is provably dead first**

```sql
drop function if exists digest.chat_recommendations_v3(text);
```

Confirm zero callers first (`grep -rn "chat_recommendations_v3" db/ scripts/`; it appears only in docs and grants). Deleting a dead function is the safest possible start and validates the process.

- [ ] **Step 4: Collapse one family, end to end, as the pattern**

Take `partner_lookup` (v2 wraps v1, two files, low traffic). Inline v1's body into v2, rename v2 to `partner_lookup`, drop the old v1.

Because this is a `DROP` + `CREATE`, the migration **must** include:

```sql
revoke all on function digest.partner_lookup(<exact args>) from public, anon, authenticated;
grant execute on function digest.partner_lookup(<exact args>) to service_role;
```

Omitting that ships an anon-callable function. It has happened twice.

- [ ] **Step 5: Probe before and after on the same question**

```sql
select * from digest.partner_lookup(p_phone := '<test number>', p_terms := array['reimbursements']);
```
The answer must be byte-identical to the pre-change v2 output. Diff it.

- [ ] **Step 6: Repeat Steps 4–5 for the remaining families**

In ascending order of traffic, so the riskiest is done with the most practice: `chat_recommendations`, `member_dossier`, `event_history`, `partner_lookup` (done), `video_search`, `member_match`, `member_card`, `multi_source`, `event_lookup`, `content_search`. `content_search` is last — it is the highest-traffic function in the system.

- [ ] **Step 7: Remove the `EXEC_NAME` indirection from n8n**

Once every family has one implementation, the tool name equals the function name and the map is dead weight. Edit the **active** workflow, then bounce with a single `[{deactivateWorkflow},{activateWorkflow}]` call — never deactivate first. Snapshot the workflow before and after into `olivia_snapshots/`.

- [ ] **Step 8: Full gate, targeted eval, commit**

This task changes what the assistant calls for every question, so the gate is necessary but not sufficient. Run a targeted eval (25–35 questions) spanning every collapsed lane and compare against the last nightly. **Get Andy's approval before firing — eval runs cost money.**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/phase3_task7_one_version_per_lane.sql
git commit -m "refactor: one implementation per lane, EXEC_NAME indirection removed

Ten families carried v1/v2/v3 with n8n rewriting the tool name at the last inch --
a deployment mechanism standing in for a release process, and the cause of the
stale routing Phase 2 fixed as a symptom. Collapsed lowest-traffic first;
content_search last. Every DROP+CREATE carries its revoke.

Eval: <before>% -> <after>% on <n> questions.
Gate 253 exit 0."
```

---

## Definition of Done for Phase 3

- [ ] All seven assertion queries pass.
- [ ] **25 foreign keys declared and validated** (7 + 18), plus 4 on `entity_dossier` and 4 on `forms` = 33 total, against 13 at the start.
- [ ] The canary insert in Task 2 Step 6 is proven to fail — an `airtable_id` can no longer be stored as an `at_member_id`.
- [ ] `python3 scripts/olivia_leak_gate.py` exits 0.
- [ ] `git diff db/` is empty after a fresh export.
- [ ] Every scheduled job has reported a successful run since the last migration, and `digest.job_errors` holds no foreign-key violations.
- [ ] Supabase's schema visualizer shows a connected graph — the acceptance test the external developer will actually apply.
- [ ] `SESSION_LOG_OLIVIA.md` entry and `SESSION_LOG.md` index line written.
