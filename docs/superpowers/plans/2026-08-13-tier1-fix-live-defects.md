# Tier 1 — Fix Live Defects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the wrong data and lost capability that exist in production today, without changing the schema.

**Architecture:** Every task follows the same loop — write a SQL assertion that returns the *wrong* answer today, confirm it fails, apply a migration or function rewrite, confirm the assertion passes, run the leak gate, re-export `db/`, commit. No schema objects are added or dropped except where a task says so explicitly. All work is inside Supabase project `nadtudwuwjhckotrngzn`, schema `digest`.

**Tech Stack:** Postgres 17 (Supabase), PL/pgSQL, `scripts/olivia_leak_gate.py`, `scripts/db_export_schema.py`, n8n (one task only).

> ⚠️ **READ THE RISK REGISTER FIRST:** `docs/superpowers/specs/2026-08-13-digest-schema-risk-register.md`.
> It corrects the task order below. **Tasks 2–5 must run consumers-first, not writers-first** — the
> written order leaves a window in which author attribution is zero for *every* source, worse than
> production today. Register §2 gives the corrected sequence and the transitional join. The register
> also adds a required snapshot before Task 1's delete, and flags that Task 8's rename must grep the
> separate `mds-digest-web` repository. Task 10 (fail-loud) is a hard prerequisite for all of Tier 2.

## Global Constraints

- **Supabase project id:** `nadtudwuwjhckotrngzn`. Schema: `digest`.
- **The leak gate must exit 0 before and after every task.** Run: `python3 scripts/olivia_leak_gate.py`. Current baseline: **253 checks, exit 0**.
- **After any DDL or `CREATE OR REPLACE FUNCTION`, re-export the SQL layer** — `python3 scripts/db_export_schema.py` — and include the `db/` diff in the same commit. `git diff db/` is the review. (Rule from #65.)
- **`DROP FUNCTION` re-grants EXECUTE to PUBLIC on the fresh CREATE.** Any migration that drops and recreates a function MUST include `revoke all on function digest.<fn>(<args>) from public, anon, authenticated;` in the same migration. Two live exposures shipped this way on 2026-08-12. Prefer `CREATE OR REPLACE` (which preserves the ACL) wherever the signature is unchanged.
- **Never fire probes at production against a real member's phone number.** Use staging, or the dedicated test number.
- **`at_member_id` is canonical.** Where this plan changes an identity key, it moves *toward* `at_member_id` (`member_profiles` PK, 5,931 rows), never toward `members.airtable_id` (659 rows).
- **Migrations are applied via the Supabase MCP `apply_migration` tool**, named `<tier1_task_slug>_20260813`.
- **Commit after every task.** One task, one commit.

---

## File Structure

| File | Responsibility | Tasks |
|---|---|---|
| `db/functions/refresh_entity_dossiers.sql` | Rebuilds all 4 dossier kinds. Chapter branch is broken. | 1 |
| `db/functions/fb_link_content.sql` | Writes FB posts/comments into `content_items`. Writes `sender_member`. | 2 |
| `db/functions/content_ingest_wa_message.sql` | Trigger writing WA messages into `content_items`. Writes `sender_member`. | 2 |
| `db/functions/content_search.sql`, `content_search_v2.sql`, `content_lookup.sql`, `content_stats.sql` | Read `sender_member` for author attribution. Join the wrong table. | 4 |
| `db/functions/derive_member_expertise.sql`, `derive_knowledge_graph.sql` | Derive expertise and edges from `sender_member`. Join the wrong table. | 5 |
| `db/functions/refresh_member_phone_index.sql` | Builds the phone→member index. 17 actives missing. | 6 |
| `db/functions/multi_source_v2.sql` | Routes the general Q&A lane. Points at stale versions. | 7 |
| `db/tables.sql` (via migration) | `video_speakers.member_record_id` column comment/rename. | 8 |
| `db/tables.sql` (via migration) | The 31 audit COMMENTs, 4 of which are now wrong. | 9 |
| `db/triggers.sql`, `db/functions/tg_member_event_*.sql`, `olivia_health_check.sql` | Swallow all exceptions. | 10 |

**Testing note.** This codebase has no unit-test framework for SQL — the leak gate checks outputs and permissions, never logic. Tier 1 therefore uses **assertion queries** as its tests: a SELECT that returns a known-wrong value before the fix and a known-right one after. Tier 4 replaces these with pgTAP tests; each assertion query written here is designed to be liftable into that suite unchanged.

---

### Task 1: Chapter dossiers — split the multi-select instead of using it as a key

**Files:**
- Modify: `db/functions/refresh_entity_dossiers.sql:212-240` (the `ch` CTE and the chapter INSERT)
- Test: assertion query below

**Interfaces:**
- Consumes: `digest.attr_clean(text)`, `digest.member_expertise`, `digest.member_attributes`, `digest.member_profiles`, `digest.chapters_catalog`
- Produces: `digest.entity_dossier` rows with `kind='chapter'` whose `entity_id` is a single chapter name matching `chapters_catalog.chapter`

**Background:** line 215 reads the Airtable multi-select `Chapter Affiliation` with `->>`, which renders the JSON array as text. `attr_clean` strips the brackets, producing one comma-joined string (`"New York Chapter, Women's Chapter"`), which line 232 writes as both `entity_id` and `name`. `chapter_info.sql:102-106` reads the identical field correctly and is the pattern to copy.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task1_chapter_dossier.sql
-- Every chapter dossier must name a real chapter.
select count(*) as orphan_chapter_dossiers
from digest.entity_dossier d
where d.kind = 'chapter'
  and not exists (select 1 from digest.chapters_catalog c where c.chapter = d.entity_id);
-- EXPECTED AFTER FIX: 0
```

- [ ] **Step 2: Run it and confirm it fails**

Run the query above via the Supabase MCP `execute_sql` tool.
Expected now: **51**. Record the exact number in the commit message.

- [ ] **Step 3: Capture the before-state for the 20 real chapters**

```sql
select entity_id, (reception->>'expertise_rows')::int as rows_before
from digest.entity_dossier
where kind='chapter'
  and exists (select 1 from digest.chapters_catalog c where c.chapter = entity_id)
order by 1;
```
Save the output — Step 7 compares against it. These 20 currently under-count because members with more than one chapter were diverted into the fabricated combination rows.

- [ ] **Step 4: Apply the migration**

Migration name: `tier1_chapter_dossier_split_20260813`

```sql
create or replace function digest.refresh_entity_dossiers()
returns table(o_kind text, o_rows bigint)
language plpgsql
security definer
set search_path to 'digest', 'public', 'extensions'
as $function$
-- NOTE TO IMPLEMENTER: copy the CURRENT body verbatim from
-- db/functions/refresh_entity_dossiers.sql and replace ONLY the `ch` CTE
-- (currently lines 212-221) with the version below. The video, partner and
-- event branches are correct (0 orphans each) and must not be touched.
$function$;
```

The replacement `ch` CTE — note `cross join lateral regexp_split_to_table`, mirroring `chapter_info.sql:102-106`:

```sql
  with ch as (
    select ma.chapter as chname, e.topic, avg(e.score) ascore, count(*) n
    from (select ma2.at_member_id, trim(one) as chapter
          from digest.member_attributes ma2
          join digest.member_profiles mp on mp.at_member_id = ma2.at_member_id
          cross join lateral regexp_split_to_table(
            coalesce(digest.attr_clean(mp.at_fields->>'Chapter Affiliation'), ''),
            ',[[:space:]]*') one
          where digest.is_active_member_status(ma2.membership_status)
            and trim(one) not in ('', 'No Chapter Affiliation', 'Chapter Leads')) ma
    join digest.member_expertise e on e.at_member_id = ma.at_member_id
    where coalesce(e.weakness_score,0) = 0 and e.score > 0
    group by ma.chapter, e.topic
  ),
```

The chapter INSERT below it needs no change — it already reads `p.chname`.

- [ ] **Step 5: Delete the 51 fabricated rows**

The upsert will not remove them; they must go explicitly.

```sql
delete from digest.entity_dossier d
where d.kind = 'chapter'
  and not exists (select 1 from digest.chapters_catalog c where c.chapter = d.entity_id);
-- EXPECTED: DELETE 51
```

- [ ] **Step 6: Rebuild and re-run the assertion**

```sql
select * from digest.refresh_entity_dossiers();
```
Then re-run the Step 1 assertion. Expected: **0**.

- [ ] **Step 7: Confirm the 20 real chapters gained members**

Re-run the Step 3 query and diff against the saved output. Every row's `rows_before` should now be **greater than or equal to** its old value — 118 of 692 affiliated actives are multi-chapter and were previously excluded from all 20. A chapter that *lost* rows means the split is wrong; stop and investigate.

Also confirm no other kind regressed:

```sql
select kind, count(*) from digest.entity_dossier group by 1 order by 1;
-- EXPECTED: chapter <= 20, event 1429, partner 497, video 1032
```

- [ ] **Step 8: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task1_chapter_dossier.sql
git commit -m "fix: chapter dossiers keyed on a comma-joined multi-select

refresh_entity_dossiers read Chapter Affiliation with ->>, so a member in two
chapters produced a fabricated third entity. 51 of 71 chapter dossiers were not
real chapters. Split with regexp_split_to_table, matching chapter_info.

Before: 51 orphan chapter dossiers. After: 0.
Gate 253 exit 0."
```

---

### Task 2: Make `at_member_id` the only key written to `content_items.meta.sender_member`

**Files:**
- Modify: `db/functions/fb_link_content.sql:22` (comments branch) and `:10-15` (posts branch)
- Modify: `db/functions/content_ingest_wa_message.sql:27`
- Test: assertion query below

**Interfaces:**
- Consumes: `digest.fb_member_map(fb_uid, at_member_id)`, `digest.members(airtable_id, at_member_id)`
- Produces: `content_items.meta->>'sender_member'` holding `at_member_id` for **every** source. Tasks 3, 4 and 5 depend on this being true.

**Background:** today `wa_message` rows carry `members.airtable_id` (13,450 rows) while `fb_comment` and `fb_post` carry `at_member_id` (17,676 rows). The two key spaces are both `rec`+14 characters with zero overlap, so the mismatch is invisible. Every consumer joins `members.airtable_id`, so all 17,676 Facebook rows match nothing.

The posts branch of `fb_link_content` currently writes **no** `sender_member` at all (only `author_name`) — the 3,574 post rows that have one were populated by a hand-run backfill that exists in no tracked file. This task makes the function the single writer for both.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task2_sender_member_one_keyspace.sql
-- Every sender_member must resolve against the canonical member table.
select ci.source,
       count(*) as rows_with_sender,
       count(*) filter (where exists (
         select 1 from digest.member_profiles p
         where p.at_member_id = ci.meta->>'sender_member')) as resolves_canonical
from digest.content_items ci
where ci.meta ? 'sender_member'
group by 1 order by 1;
-- EXPECTED AFTER FIX: resolves_canonical = rows_with_sender for every source
--   (allowing the 48 known wa_message rows whose member has no at_member_id)
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: `fb_comment` 14,102 rows / 14,075 resolve · `fb_post` 3,574 / 3,574 · **`wa_message` 13,450 / 0**.

- [ ] **Step 3: Rewrite `fb_link_content` so posts also carry the key**

Migration name: `tier1_sender_member_canonical_writers_20260813`

Replace the posts INSERT (currently `fb_link_content.sql:10-16`) with:

```sql
  with ins as (
    insert into digest.content_items (source,kind,source_id,body,occurred_at,url,access_rule,sensitivity,meta)
    select 'fb_post','post',fp.post_id,fp.text,fp.created_time,
      'https://www.facebook.com/groups/699138040189700/posts/'||fp.post_id||'/',
      '{"type":"public"}'::jsonb,'normal',
      jsonb_build_object('author_name',fp.author_name,'sender_member',m.at_member_id)
    from digest.fb_posts fp
    left join digest.fb_member_map m on m.fb_uid = fp.author_uid
    on conflict (source,source_id) do nothing returning 1)
  select count(*) into p from ins;
```

The comments branch at line 22 already writes `m.at_member_id` and is correct — leave it unchanged.

- [ ] **Step 4: Rewrite the WA ingest trigger to translate to the canonical key**

`content_ingest_wa_message.sql:27` currently writes `new.sender_member`, which is `members.airtable_id` (the column is FK'd there). Translate it:

```sql
      'sender_member', (select m.at_member_id from digest.members m
                        where m.airtable_id = new.sender_member))))
```

Keep every other key in that `jsonb_build_object` exactly as-is — `scripts/olivia_leak_gate.py:66` asserts the allowlist `{chat_name, chat_id, sender_member, sender_name}` and will fail if a key is added or removed.

- [ ] **Step 5: Verify new writes are correct without touching history**

```sql
-- a WA message ingested after the change must now carry at_member_id
select ci.meta->>'sender_member' as key_written,
       exists (select 1 from digest.member_profiles p where p.at_member_id = ci.meta->>'sender_member') as canonical
from digest.content_items ci
where ci.source='wa_message'
order by ci.ingested_at desc limit 5;
```
Expected: `canonical = true`. If no new message has arrived, insert and roll back a canary rather than waiting.

- [ ] **Step 6: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task2_sender_member_one_keyspace.sql
git commit -m "fix: write at_member_id, not airtable_id, as content_items sender_member

content_items.meta.sender_member carried two disjoint rec-shaped key spaces --
airtable_id for WhatsApp, at_member_id for Facebook -- and every consumer joined
airtable_id, so 17,676 FB rows matched nothing. Writers now emit the canonical key
only. fb_link_content also becomes the single writer for post rows, which were
previously populated by an untracked hand-run backfill.

Backfill of existing rows is Task 3; consumers are repointed in Tasks 4 and 5.
Gate 253 exit 0."
```

---

### Task 3: Backfill the 13,450 historical WhatsApp rows

**Files:**
- Test: assertion query from Task 2

**Interfaces:**
- Consumes: the writers fixed in Task 2
- Produces: `content_items.meta->>'sender_member'` canonical for all history. Tasks 4 and 5 assume this.

**Background:** measured — 13,402 of 13,450 convert cleanly; **48 will become NULL** because their member row has no `at_member_id` (54 of 659 `members` rows lack one). That is a pre-existing identity gap, not damage from this change, and Task 6 covers its cause.

- [ ] **Step 1: Record the exact expected counts**

```sql
select count(*) as total,
       count(*) filter (where m.at_member_id is not null) as convertible,
       count(*) filter (where m.at_member_id is null) as will_null
from digest.content_items ci
join digest.members m on m.airtable_id = ci.meta->>'sender_member'
where ci.source='wa_message';
-- EXPECTED: 13450 / 13402 / 48
```

If these numbers differ from 13450/13402/48, stop — the data moved since planning and the migration needs re-checking.

- [ ] **Step 2: Snapshot the rows that will lose their key**

```sql
create table if not exists digest._tier1_task3_rollback as
select ci.id, ci.meta->>'sender_member' as old_sender_member
from digest.content_items ci
where ci.source='wa_message' and ci.meta ? 'sender_member';
select count(*) from digest._tier1_task3_rollback;  -- EXPECTED: 13450
```

This is the rollback path. Drop it only after Task 5 verifies.

- [ ] **Step 3: Apply the backfill**

Migration name: `tier1_backfill_wa_sender_member_20260813`

```sql
update digest.content_items ci
set meta = jsonb_set(ci.meta, '{sender_member}', to_jsonb(m.at_member_id))
from digest.members m
where ci.source = 'wa_message'
  and ci.meta->>'sender_member' = m.airtable_id
  and m.at_member_id is not null;
-- EXPECTED: UPDATE 13402

update digest.content_items ci
set meta = ci.meta - 'sender_member'
from digest.members m
where ci.source = 'wa_message'
  and ci.meta->>'sender_member' = m.airtable_id
  and m.at_member_id is null;
-- EXPECTED: UPDATE 48
```

The second statement removes the key rather than setting it to null — `content_lookup.sql:24` and `content_search.sql:44` both branch on `ci.meta ? 'sender_member'`, so a JSON null would read as "present but unresolvable" and change their output.

- [ ] **Step 4: Re-run the Task 2 assertion**

Expected: every source's `resolves_canonical` now equals `rows_with_sender`. `wa_message` total drops from 13,450 to 13,402.

- [ ] **Step 5: Confirm the leak-gate meta allowlist still holds**

```bash
python3 scripts/olivia_leak_gate.py
```
The WA meta allowlist check (`olivia_leak_gate.py:66`) must still pass — removing a key from 48 rows is legal, adding one is not.

- [ ] **Step 6: Commit**

```bash
git add tests/assertions/
git commit -m "fix: backfill 13,402 WhatsApp content rows to the canonical member key

13,450 wa_message rows carried members.airtable_id. 13,402 converted to
at_member_id; 48 had no canonical key and had sender_member removed rather than
nulled, because two readers branch on key presence. Rollback snapshot in
digest._tier1_task3_rollback until Task 5 verifies.

Gate 253 exit 0."
```

---

### Task 4: Repoint the four read paths at the canonical table

**Files:**
- Modify: `db/functions/content_search.sql:54`, `content_search_v2.sql` (author lane, ~:77-85 and the authority CTE ~:199-205), `content_lookup.sql:29`, `content_stats.sql:22`

**Interfaces:**
- Consumes: canonical `sender_member` from Tasks 2–3
- Produces: author attribution that resolves for all six sources. No signature changes — all four keep their existing arguments and return types.

**Background:** each of these joins `digest.members mm on mm.airtable_id = ci.meta->>'sender_member'`. After Task 3 that join matches nothing at all, so this task is **not optional** — skipping it turns a partial failure into a total one.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task4_author_resolves.sql
-- content_lookup must return an author for a Facebook post whose author is a member.
select count(*) as fb_rows_with_resolved_author
from digest.content_items ci
join digest.member_profiles p on p.at_member_id = ci.meta->>'sender_member'
where ci.source = 'fb_post';
-- EXPECTED: ~3574 (this is what the READ PATH should be able to see)
```

- [ ] **Step 2: Confirm the current join sees none of them**

```sql
select count(*) from digest.content_items ci
join digest.members m on m.airtable_id = ci.meta->>'sender_member'
where ci.source = 'fb_post';
-- EXPECTED NOW: 0   <-- this is the bug, in one line
```

- [ ] **Step 3: Apply the migration**

Migration name: `tier1_repoint_author_joins_20260813`

In all four functions, replace every occurrence of:

```sql
left join digest.members mm on mm.airtable_id = ci.meta->>'sender_member'
```

with:

```sql
left join digest.member_profiles mm on mm.at_member_id = ci.meta->>'sender_member'
```

**Column check before you write it:** `members` exposes `full_name` and `name`; `member_profiles` exposes `full_name` but **not** `name`. Any downstream reference to `mm.name` must become `mm.full_name`. `content_search.sql:44` and `content_lookup.sql:24` both reference these — read each line and adjust rather than blind-replacing.

Use `CREATE OR REPLACE FUNCTION` so the ACL is preserved. If any signature must change, add the revoke line from Global Constraints.

- [ ] **Step 4: Re-run both assertions**

Step 1 assertion: unchanged (~3,574). Step 2 query, rewritten against `member_profiles`: now ~3,574 rather than 0.

- [ ] **Step 5: Probe the live read path**

```sql
select count(*) from digest.content_search(
  p_phone := '<the dedicated test number>',
  p_terms := array['amazon'],
  p_author := '<a member known to post on Facebook>');
-- EXPECTED: > 0. Before this task it was 0 for every FB author.
```

- [ ] **Step 6: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task4_author_resolves.sql
git commit -m "fix: author attribution joins member_profiles, not the WA members table

Four read paths joined members.airtable_id against a sender_member that is now
canonical. Repointed to member_profiles.at_member_id. FB author attribution goes
from 0 resolvable rows to ~3,574.

Gate 253 exit 0."
```

---

### Task 5: Restore the interaction graph and Facebook expertise evidence

**Files:**
- Modify: `db/functions/derive_member_expertise.sql:29`, `db/functions/derive_knowledge_graph.sql:81-82`

**Interfaces:**
- Consumes: canonical `sender_member` (Tasks 2–3)
- Produces: `digest.member_edges` rows of `edge_type='thread_interaction'` (currently zero exist), and `member_expertise` rows carrying Facebook evidence

**Background:** `derive_knowledge_graph.sql:81-82` **inner** joins `members.airtable_id` on both sides of the commenter↔author pair, so `thread_interaction` edges have never been produced — live, `member_edges` holds only `co_attended` (91,544), `same_chat` (40,329) and `same_chapter` (19,887). `derive_member_expertise.sql:29` uses the same join, which is why content evidence survives on 833 of 6,801 expertise rows.

Measured: the corrected join yields **24,152 rows against today's 13,450** — an 80% increase in evidence.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task5_interaction_graph_exists.sql
select coalesce((select count(*) from digest.member_edges
                 where edge_type = 'thread_interaction'), 0) as thread_edges;
-- EXPECTED AFTER FIX: > 0
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **0**.

- [ ] **Step 3: Record before-state for expertise**

```sql
select count(*) as expertise_rows,
       count(*) filter (where evidence_count > 0) as with_evidence
from digest.member_expertise;
```
Record both. `with_evidence` is expected to rise; `expertise_rows` may also rise.

- [ ] **Step 4: Apply the migration**

Migration name: `tier1_repoint_derivations_20260813`

In `derive_member_expertise.sql:29`, replace:

```sql
    join digest.members m on m.airtable_id = coalesce(ci.meta->>'sender_member', ci.meta->>'member')
```

with:

```sql
    join digest.member_profiles m on m.at_member_id = coalesce(ci.meta->>'sender_member', ci.meta->>'member')
```

Then follow `m.` through the rest of that function — if it references `m.airtable_id` downstream (for example when writing `at_member_id`), it must now use `m.at_member_id` directly rather than translating.

In `derive_knowledge_graph.sql:81-82`, replace:

```sql
    join digest.members mc on mc.airtable_id = c.meta->>'sender_member'
    join digest.members mp on mp.airtable_id = p.meta->>'sender_member'
```

with:

```sql
    join digest.member_profiles mc on mc.at_member_id = c.meta->>'sender_member'
    join digest.member_profiles mp on mp.at_member_id = p.meta->>'sender_member'
```

and follow `mc.`/`mp.` downstream the same way — `member_edges.a_id`/`b_id` hold `at_member_id`, so any `mc.airtable_id` that was being translated can now be `mc.at_member_id`.

- [ ] **Step 5: Re-run the derivations**

```sql
select * from digest.derive_member_expertise();
select * from digest.derive_knowledge_graph();
```

- [ ] **Step 6: Re-run the assertion and record the deltas**

```sql
select edge_type, count(*) from digest.member_edges group by 1 order by 2 desc;
-- EXPECTED: thread_interaction now present and > 0
select count(*) as expertise_rows,
       count(*) filter (where evidence_count > 0) as with_evidence
from digest.member_expertise;
-- EXPECTED: with_evidence materially above the Step 3 figure (833 today)
```

- [ ] **Step 7: Check the eval, not just the gate**

Expertise scores change for the first time, which moves what Olivia says about who knows what. The gate does not test that.

Run a targeted eval (25–35 questions) on the expertise and people lanes and compare against the last nightly. **This costs money — get Andy's go-ahead before firing it** (standing rule: any eval RUN is propose-and-wait). Report pass rate before and after.

- [ ] **Step 8: Drop the rollback table, gate, re-export, commit**

```sql
drop table if exists digest._tier1_task3_rollback;
```

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task5_interaction_graph_exists.sql
git commit -m "fix: derivations read the canonical key, restoring the FB interaction graph

derive_knowledge_graph inner-joined members.airtable_id on both sides of the
commenter/author pair, so thread_interaction edges never existed.
derive_member_expertise had the same join, leaving content evidence on 833 of
6,801 rows. Both repointed to member_profiles.

Before: 0 thread_interaction edges, 13,450 joinable content rows.
After: <fill in> edges, 24,152 joinable rows.
Gate 253 exit 0."
```

---

### Task 6: The 17 active members with no phone-index row

**Files:**
- Modify: `db/functions/refresh_member_phone_index.sql` (only if the cause is there)
- Test: assertion query below

**Interfaces:**
- Consumes: `digest.member_phones` view, `digest.member_attributes`
- Produces: no signature change

**Background:** 17 active members have no `member_phone_index` row, so `resolve_asker()` returns NULL for them and all ~40 gated functions return zero rows — indistinguishable from "we have no data about you". `refresh_member_phone_index.sql:20-22,37-43` also silently drops any number owned by two active members (currently 0, so not the cause here).

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task6_actives_reachable.sql
select count(*) as actives_without_phone_index
from digest.member_attributes a
where digest.is_active_member_status(a.membership_status)
  and not exists (select 1 from digest.member_phone_index i
                  where i.at_member_id = a.at_member_id);
-- EXPECTED AFTER FIX: 0, or a documented number with a written reason
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **17**.

- [ ] **Step 3: Diagnose before fixing — do they have a phone at all?**

```sql
select a.at_member_id, a.full_name,
       nullif(trim(mp.at_fields->>'Preferred Phone Number'),'') as pref_phone,
       nullif(trim(mp.at_fields->>'WhatsApp Number'),'') as wa_phone,
       (select count(*) from digest.members m where m.at_member_id = a.at_member_id) as wa_layer_rows
from digest.member_attributes a
join digest.member_profiles mp on mp.at_member_id = a.at_member_id
where digest.is_active_member_status(a.membership_status)
  and not exists (select 1 from digest.member_phone_index i
                  where i.at_member_id = a.at_member_id);
```

This splits into two outcomes, and they need different fixes:
- **No phone in Airtable** → not a code bug. The fix is upstream data entry; record the 17 names for Andy and change nothing here. Update the assertion's expected value with the reason written in.
- **Phone present but not indexed** → a bug in `member_phones` or `refresh_member_phone_index`. Read both, find why the row is dropped, fix it.

- [ ] **Step 4: Apply whichever fix Step 3 indicates**

If it is a code bug, the migration is named `tier1_phone_index_coverage_20260813` and uses `CREATE OR REPLACE FUNCTION` so the ACL is preserved. If it is a data gap, there is no migration — proceed to Step 6 with the finding written up.

- [ ] **Step 5: Re-run the index and the assertion**

```sql
select * from digest.refresh_member_phone_index();
```
Then re-run the Step 1 assertion. Expected: 0, or the documented residual.

- [ ] **Step 6: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task6_actives_reachable.sql
git commit -m "fix: 17 active members were unreachable through resolve_asker

No member_phone_index row means resolve_asker returns NULL and ~40 gated
functions return zero rows -- identical to 'no data about you'.

Cause: <fill in from Step 3>. Before: 17. After: <fill in>.
Gate 253 exit 0."
```

---

### Task 7: `multi_source_v2` routes to current versions

**Files:**
- Modify: `db/functions/multi_source_v2.sql:33` (partner lane), `:53` (event lane)

**Interfaces:**
- Consumes: `digest.event_lookup_v3`, `digest.partner_lookup_v2`
- Produces: no signature change to `multi_source_v2` itself

**Background:** `multi_source_v2` calls `event_lookup_v2` and `partner_lookup` v1, so the general Q&A lane misses #82's flagship `room` and #50's partner `strength_note` — both shipped, verified, and live through a *different* entry point. Pure SQL; no n8n promote required.

**Argument-shape warning:** `event_lookup_v3` and `event_lookup_v2` do not take identical arguments — v3 added parameters when #82 shipped. Read both signatures before editing:

```sql
select p.proname, pg_get_function_arguments(p.oid)
from pg_proc p where p.pronamespace='digest'::regnamespace
  and p.proname in ('event_lookup_v2','event_lookup_v3','partner_lookup','partner_lookup_v2');
```

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task7_multi_source_routing.sql
select count(*) as stale_calls
from pg_proc p
where p.pronamespace = 'digest'::regnamespace
  and p.proname = 'multi_source_v2'
  and (pg_get_functiondef(p.oid) like '%event_lookup_v2%'
    or pg_get_functiondef(p.oid) ~ 'partner_lookup\s*\(');
-- EXPECTED AFTER FIX: 0
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **1**.

- [ ] **Step 3: Capture the before-answer for a flagship event**

```sql
select * from digest.multi_source_v2(
  p_phone := '<the dedicated test number>',
  p_query := 'what is the singapore summit');
```
Save it. The `room` field should be absent or empty — that is the symptom.

- [ ] **Step 4: Apply the migration**

Migration name: `tier1_multi_source_routing_20260813`

`CREATE OR REPLACE FUNCTION digest.multi_source_v2(...)` with the body copied verbatim from `db/functions/multi_source_v2.sql`, changing only:
- line 53: `digest.event_lookup_v2(` → `digest.event_lookup_v3(`, adjusting arguments to v3's signature as read in the warning above
- line 33: `digest.partner_lookup(` → `digest.partner_lookup_v2(`, same

- [ ] **Step 5: Re-run the assertion and the probe**

Step 1 assertion: **0**. Step 3 probe: the answer now carries the flagship `room` and the partner `strength_note`.

- [ ] **Step 6: Confirm the room contains counts only**

`#82`'s rule is that a room reports member counts, never a score, lift or percentile. The gate checks this for `event_lookup_v3` directly; confirm it holds through `multi_source_v2` too:

```bash
python3 scripts/olivia_leak_gate.py
```

- [ ] **Step 7: Re-export and commit**

```bash
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task7_multi_source_routing.sql
git commit -m "fix: multi_source_v2 called event_lookup_v2 and partner_lookup v1

The general Q&A lane missed #82 flagship rooms and #50 partner strength_note --
both live, but only through the named-entity entry point. Repointed to
event_lookup_v3 and partner_lookup_v2.

Gate 253 exit 0."
```

---

### Task 8: `video_speakers.member_record_id` holds GroupOS ids, not member records

**Files:**
- Modify: `db/tables.sql` via migration (comment or rename)

**Interfaces:**
- Produces: either a resolvable link or an honestly-named column. Tier 3 Task 3.1 folds this into the link table; this task stops it lying in the meantime.

**Background:** 234 rows, 100% populated, **0 resolve** to `member_profiles` or `members`. The values are GroupOS 24-hex (`678e26c37ce7948f82af3a3f`), not `rec`-shaped. A column named *member record id* contains no member record id — the same class as the Airtable field-naming trap in `reference_at_field_names_lie`.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task8_speaker_key_honest.sql
select count(*) as rec_shaped_values
from digest.video_speakers
where member_record_id ~ '^rec[A-Za-z0-9]{14}$';
-- Today: 0 of 234. The column name promises Airtable record ids and delivers
-- GroupOS 24-hex. EXPECTED AFTER FIX: the column is renamed, so this query
-- errors on a missing column -- which is the point.
```

- [ ] **Step 2: Check whether the ids resolve anywhere before renaming**

```sql
select v.member_record_id, v.display_name, v.email, v.member_type,
       (select count(*) from digest.member_profiles p
        where lower(p.email) = lower(v.email)) as email_match
from digest.video_speakers v limit 20;
```

If `email_match` is mostly 1, a resolver is achievable and worth more than a rename — the speakers *are* members, joined by the wrong column. If it is mostly 0, rename only.

- [ ] **Step 3a (if the emails resolve): add a real key column**

Migration name: `tier1_speaker_member_link_20260813`

```sql
alter table digest.video_speakers rename column member_record_id to groupos_user_id;
alter table digest.video_speakers add column at_member_id text;

update digest.video_speakers v
set at_member_id = p.at_member_id
from digest.member_profiles p
where lower(p.email) = lower(v.email) and v.email is not null;

comment on column digest.video_speakers.groupos_user_id is
  'GroupOS 24-hex user id, NOT an Airtable record id (renamed 2026-08-13, Tier 1 Task 8).';
comment on column digest.video_speakers.at_member_id is
  'Implicit FK -> member_profiles.at_member_id, resolved by email. Tier 3 folds this into the link table.';
```

- [ ] **Step 3b (if they do not resolve): rename only**

```sql
alter table digest.video_speakers rename column member_record_id to groupos_user_id;
comment on column digest.video_speakers.groupos_user_id is
  'GroupOS 24-hex user id, NOT an Airtable record id. 0 of 234 resolve to any
   member table (measured 2026-08-13). Renamed so the name stops promising a link
   that does not exist. Resolver is Tier 3 Task 3.1.';
```

- [ ] **Step 4: Find and fix every reader of the old name**

```bash
grep -rn "member_record_id" db/ scripts/ --include=*.sql --include=*.py
```
Every hit must be updated in the same migration or the same commit. A rename that leaves a reader behind is worse than the lie.

- [ ] **Step 5: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier1_task8_speaker_key_honest.sql
git commit -m "fix: video_speakers.member_record_id held GroupOS ids, not member records

234 rows, 100% populated, 0 resolving to any member table. Renamed to
groupos_user_id <and linked by email / and documented as unresolved>.

Gate 253 exit 0."
```

---

### Task 9: Correct the four column comments the research disproved

**Files:**
- Modify: `db/tables.sql` via migration

**Interfaces:**
- Produces: comments that match measured reality

**Background:** migration `digest_schema_audit_comments_20260812` shipped 31 `COMMENT ON COLUMN` statements. Four of them assert things the research disproved — most importantly that `entity_dossier.entity_id` cannot be a foreign key, when 51 of its chapter rows were fabricated precisely because nothing enforced it.

- [ ] **Step 1: Read the current comments**

```sql
select c.relname, a.attname, d.description
from pg_description d
join pg_attribute a on a.attrelid = d.objoid and a.attnum = d.objsubid
join pg_class c on c.oid = a.attrelid
where c.relnamespace = 'digest'::regnamespace and d.description ilike '%audit #61%'
order by 1,2;
```

- [ ] **Step 2: Apply the corrections**

Migration name: `tier1_correct_audit_comments_20260813`

```sql
comment on column digest.entity_dossier.entity_id is
  'Polymorphic key resolved by kind: event->events_catalog.at_record_id,
   video->videos_catalog.video_id, partner->partners_catalog.partner_id,
   chapter->chapters_catalog.chapter. Enforceable as four typed nullable columns
   with a CHECK, or four tables -- an earlier comment called it not-FK-able, which
   was wrong: 51 of 71 chapter rows were fabricated because nothing enforced it
   (fixed 2026-08-13, Tier 1 Task 1). Restructure is Tier 2 Task 2.3.';

comment on column digest.content_items.source_id is
  'Polymorphic key resolved by source. Measured 2026-08-13: fb_comment 13,999 of
   14,889 resolve on fb_comments.comment_id and the other 890 on
   fb_comments.legacy_id -- two id generations in one column. wa_message, fb_post,
   call_transcript, wa_digest and application all resolve fully.';

comment on column digest.form_responses.member_at_id is
  'Implicit FK -> member_profiles.at_member_id. NULL on 8,036 of 13,644 rows, but
   that number is misleading: the 5 forms in form_scope are 90% stamped, and 5,275
   of the unstamped rows come from forms that never collected an identifier.
   stamp_form_responses is at fixpoint -- rerunning it stamps nothing new.';

comment on column digest.members.at_member_id is
  'Bridge to member_profiles.at_member_id, the canonical key. NULL on 54 of 659
   rows. NOTE: members.airtable_id and member_profiles.at_member_id are BOTH
   rec+14 characters with ZERO overlap -- they are different key spaces that look
   identical. Only a foreign key distinguishes them; see the 2026-08-13 research
   report.';
```

- [ ] **Step 3: Verify all 31 still exist and 4 changed**

```sql
select count(*) from pg_description d
join pg_attribute a on a.attrelid = d.objoid and a.attnum = d.objsubid
join pg_class c on c.oid = a.attrelid
where c.relnamespace = 'digest'::regnamespace and d.description ilike '%audit #61%';
-- EXPECTED: 27 (the four rewritten comments no longer carry that marker)
```

- [ ] **Step 4: Re-export and commit**

```bash
python3 scripts/db_export_schema.py
git add db/
git commit -m "docs: correct four column comments the schema research disproved

The 2026-08-12 audit comments asserted entity_dossier.entity_id was not FK-able
and reported the forms NULL rate without its breakdown. Metadata only; no lock,
no behaviour change."
```

---

### Task 10: Fail-open becomes fail-loud

**Files:**
- Modify: `db/functions/tg_member_event_olivia_turn.sql`, `tg_member_event_portal_seen.sql`, `tg_member_event_report.sql`, `olivia_health_check.sql`

**Interfaces:**
- Produces: no signature changes. `olivia_health_check` gains a signal for its own internal failures.

**Background:** all three `member_events` triggers and all eight health-check signals wrap their body in `exception when others then null`. A broken health check therefore reports green, which makes every other "it's fine" in this system unfalsifiable. This is the highest-leverage task in Tier 1 and the reason it is last — the preceding tasks are safer to do while errors are still being swallowed.

**Risk:** a trigger that raises instead of swallowing can fail a write that currently succeeds. The triggers fire on `olivia_messages`, `member_sessions` and `olivia_reports` inserts — a raise there would break a live member conversation. So triggers **log and continue**; only the health check **raises**.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier1_task10_no_silent_swallow.sql
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

Migration name: `tier1_fail_loud_20260813`

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
   Written by triggers and the health check. Tier 1 Task 10.';
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
git add db/ tests/assertions/tier1_task10_no_silent_swallow.sql
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

## Definition of Done for Tier 1

- [ ] All ten assertion queries pass.
- [ ] `python3 scripts/olivia_leak_gate.py` exits 0 (253 checks or more).
- [ ] `git diff db/` is empty after a fresh `python3 scripts/db_export_schema.py` — the repo matches the live database.
- [ ] Before/after numbers recorded for: orphan chapter dossiers (51→0), `thread_interaction` edges (0→n), expertise rows with evidence (833→n), joinable content rows (13,450→24,152), actives without a phone index (17→n), error-swallowing functions (11→0).
- [ ] One targeted eval run compared against the previous nightly, with Andy's prior approval, because Task 5 changes what Olivia says about expertise.
- [ ] `SESSION_LOG_OLIVIA.md` carries the full entry and `SESSION_LOG.md` one index line.
