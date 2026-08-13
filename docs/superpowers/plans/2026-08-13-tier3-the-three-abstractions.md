# Tier 3 — The Three Abstractions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the three shared models the warehouse never had, so a new data source costs rows and a loader instead of ~15 bespoke functions.

**Architecture:** Each abstraction ships behind a compatibility layer. The new table is built and backfilled, a view preserves the old shape, consumers move one at a time with output diffed before and after, and only when every consumer is migrated and parity is proven does the old object get dropped. No task drops anything in the same session it creates its replacement.

**Tech Stack:** Postgres 17 (Supabase), PL/pgSQL, `scripts/olivia_leak_gate.py`, `scripts/db_export_schema.py`.

## Global Constraints

> ⚠️ **READ THE RISK REGISTER FIRST:** `docs/superpowers/specs/2026-08-13-digest-schema-risk-register.md` §3.
> Task 2 carries **R1, the only risk in the whole programme whose damage cannot be rolled back**.
> Three corrections: the visibility baseline must cover **every active member**, not 20; results must
> be reported **per `rule_type`** so an owner-rule regression cannot hide inside a public-rule
> majority; and because `can_see` is `SECURITY DEFINER` and takes `at_member_id` as an argument,
> **every call site must derive that id from `resolve_asker`, never from member-supplied input** —
> otherwise it is a direct IDOR.

- **Tiers 1 and 2 must be complete.** This plan assumes foreign keys exist and the two `rec` key spaces are already separated. Building a link table on unenforced keys reproduces the original problem in a new table.
- **Supabase project id:** `nadtudwuwjhckotrngzn`. Schema: `digest`.
- **🔴 THE PROD PULSE RUNS BEFORE AND AFTER EVERY STEP**, and inside Task 2 before and after **every individual consumer migration**. `python3 scripts/prod_pulse.py` — exit 1 means STOP. Re-baseline at the start of the tier.
- **Gate exit 0 before and after every task**, and additionally **before and after every consumer migration inside Task 2** — that task moves the privacy boundary.
- **Re-export after every DDL**; commit the `db/` diff with the change.
- **`DROP FUNCTION` re-grants EXECUTE to PUBLIC.** Every drop-and-recreate carries its `revoke all … from public, anon, authenticated`.
- **Parity before deletion.** An old object is dropped only after its replacement has produced byte-identical output on a recorded sample.
- **Never delete a member record.** Migration never removes rows representing a person, even a duplicate.
- **One task, one commit.** Task 2 additionally commits per consumer migrated.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| migration + `db/functions/resolve_asker.sql` | `digest.member_link` — every external identity → `at_member_id` | 1 |
| `db/views/member_link_compat.sql` | Preserves `fb_member_map` / `zoom_name_alias` / `member_phone_index` shapes | 1 |
| migration + `db/functions/can_see.sql` (new) | Audience as data | 2 |
| 10 read-path functions | Migrated to `can_see` one at a time | 2 |
| migration + `db/views/participation_compat.sql` | `digest.participation` — person × entity × role | 3 |

---

### Task 1: `member_link` — one table for every external identity

**Files:**
- Create: `digest.member_link` (migration), `db/views/member_link_compat.sql`
- Modify: `db/functions/resolve_asker.sql`, `refresh_member_phone_index.sql`, `zoom_resolve_attendance.sql`, `fb_link_content.sql`

**Interfaces:**
- Produces: `digest.member_link(source text, external_id text, at_member_id text, method text, confidence numeric, bound_at timestamptz, primary key (source, external_id))` with a foreign key on `at_member_id → member_profiles`. Tasks 2 and 3 both read it.

**Background:** identity binding has three shapes today — a bridge table (`fb_member_map`), a bridge column (`members.at_member_id`), and fuzzy stamps (`zoom_name_alias`, `stamp_form_responses`). Fourteen identity keys exist across four formats. Match rate ranges from 36% (Zoom) to 100% (video speakers) and nothing watches it.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier3_task1_link_table.sql
select to_regclass('digest.member_link') is not null as exists,
       coalesce((select count(distinct source) from digest.member_link), 0) as sources;
-- EXPECTED AFTER FIX: true, >= 5
```

- [ ] **Step 2: Create the table**

Migration name: `tier3_member_link_20260813`

```sql
create table digest.member_link (
  source        text not null,
  external_id   text not null,
  at_member_id  text not null references digest.member_profiles(at_member_id) on delete cascade,
  method        text not null,
  confidence    numeric not null default 1.0,
  bound_at      timestamptz not null default now(),
  primary key (source, external_id),
  constraint member_link_source_known check (source in
    ('phone','fb_uid','zoom_name','groupos_user','app_user','wa_airtable_id','typeform_email')),
  constraint member_link_method_known check (method in
    ('exact','normalized','email','fuzzy_name','manual')),
  constraint member_link_confidence_range check (confidence > 0 and confidence <= 1.0)
);
create index member_link_member_idx on digest.member_link (at_member_id);
revoke all on table digest.member_link from public, anon, authenticated;
grant select, insert, update, delete on table digest.member_link to service_role;
comment on table digest.member_link is
  'Every external identity that resolves to a member, in one place. A new data
   source adds ROWS here, not a new bridge table. method/confidence make fuzzy
   bindings auditable -- previously a 4-character surname stem match was
   indistinguishable from an exact one. Tier 3 Task 1.';
```

`method` and `confidence` are the point: `zoom_resolve_attendance` currently binds on a first name plus a four-character surname stem, gated only by `count(*)=1`, and the result is stored identically to an exact phone match. After this, a fuzzy binding is visible as fuzzy.

- [ ] **Step 3: Backfill from all five existing sources**

```sql
insert into digest.member_link (source, external_id, at_member_id, method, confidence)
select 'phone', i.phone10, i.at_member_id, 'normalized', 1.0
from digest.member_phone_index i
on conflict (source, external_id) do nothing;

insert into digest.member_link (source, external_id, at_member_id, method, confidence)
select 'fb_uid', f.fb_uid, f.at_member_id, 'exact', 1.0
from digest.fb_member_map f where f.at_member_id is not null
on conflict (source, external_id) do nothing;

insert into digest.member_link (source, external_id, at_member_id, method, confidence)
select 'zoom_name', z.name_folded, z.at_member_id, 'fuzzy_name', 0.7
from digest.zoom_name_alias z where z.at_member_id is not null
on conflict (source, external_id) do nothing;

insert into digest.member_link (source, external_id, at_member_id, method, confidence)
select 'wa_airtable_id', m.airtable_id, m.at_member_id, 'exact', 1.0
from digest.members m where m.at_member_id is not null
on conflict (source, external_id) do nothing;

-- video_speakers, if Tier 1 Task 8 resolved them by email
insert into digest.member_link (source, external_id, at_member_id, method, confidence)
select 'groupos_user', v.groupos_user_id, v.at_member_id, 'email', 0.9
from digest.video_speakers v where v.at_member_id is not null
on conflict (source, external_id) do nothing;
```

- [ ] **Step 4: Verify counts against the sources**

```sql
select source, count(*) from digest.member_link group by 1 order by 1;
-- Compare against: member_phone_index rows, fb_member_map non-null (716),
-- zoom_name_alias non-null, members with at_member_id (605), video_speakers linked.
-- Any shortfall means a conflict swallowed a row -- investigate before proceeding.
```

- [ ] **Step 5: Add the compatibility view and repoint `resolve_asker`**

```sql
create or replace view digest.member_link_compat_phone as
select external_id as phone10, at_member_id from digest.member_link where source='phone';
```

Rewrite `resolve_asker` to read `member_link` directly. Keep its signature and return type identical. Then prove parity across every known phone:

```sql
select count(*) as disagreements
from digest.member_phone_index i
where digest.resolve_asker(i.phone10) is distinct from i.at_member_id;
-- EXPECTED: 0
```

- [ ] **Step 6: Make match rate a watched number**

```sql
create or replace view digest.member_link_coverage as
select 'zoom' as lane,
       count(*) filter (where at_member_id is not null)::numeric / nullif(count(*),0) as rate
from digest.call_attendance
union all
select 'forms',
       count(*) filter (where member_at_id is not null)::numeric / nullif(count(*),0)
from digest.form_responses
union all
select 'events',
       count(*) filter (where member_at_id is not null)::numeric / nullif(count(*),0)
from digest.event_registrations;
```

Add a health signal that fires when any lane drops more than 5 percentage points below its recorded baseline (Zoom 36%, forms 41%, events 76%). Silent decay in match rate is currently invisible; this is what makes it loud.

- [ ] **Step 7: Migrate the remaining resolvers, one commit each**

`refresh_member_phone_index` writes `member_link` instead of `member_phone_index`; `zoom_resolve_attendance` writes `member_link` with `method='fuzzy_name'`; `fb_link_content` reads `member_link` instead of `fb_member_map`. After each, re-run that lane's parity check.

- [ ] **Step 8: Retire the old tables — only after parity holds for a full week**

Do **not** drop `fb_member_map`, `zoom_name_alias` or `member_phone_index` in the same session. Leave them, stop writing them, and confirm for seven days that no job errors and no coverage regression appears. Then drop, in a separate commit.

- [ ] **Step 9: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier3_task1_link_table.sql
git commit -m "feat: member_link -- one table for every external identity

Three binding shapes (bridge table, bridge column, fuzzy stamp) across 14 keys
become one table with method and confidence, so a 4-character surname-stem match
is no longer stored identically to an exact phone match. Match rate per lane is
now queryable and alarmed.

Old tables left in place, no longer written; retirement is a separate commit after
a week of parity.
Gate 253 exit 0."
```

---

### Task 2: Audience as data

**Files:**
- Create: `digest.audience_rule` (migration), `db/functions/can_see.sql`
- Modify: `content_search`, `content_search_v2`, `content_lookup`, `content_stats`, `fb_catchup`, `fb_thread`, `content_ingest_summary`, `content_ingest_wa_message`, `derive_member_attributes`, `fb_link_content`

**Interfaces:**
- Produces: `digest.can_see(p_at_member_id text, p_item_id bigint) returns boolean`, and `digest.visible_content(p_at_member_id text)` returning the filtered row set. Every read path consumes one of these.

**Background:** `access_rule` is a jsonb blob with 4 hardcoded types interpreted independently in **10 functions**. A chapter-restricted virtual event is a fifth type — meaning 10 edits, all of which must be right, on the privacy boundary. `fb_catchup` already diverges from its siblings.

**This task moves the privacy boundary. It carries the highest risk in the entire plan.** Every step runs the gate; no consumer moves without a before/after diff on a recorded sample.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier3_task2_one_access_chokepoint.sql
select count(*) as functions_interpreting_access_rule
from pg_proc where pronamespace='digest'::regnamespace
  and pg_get_functiondef(oid) like '%access_rule->>%'
  and proname not in ('can_see','visible_content');
-- EXPECTED AFTER FIX: 0
```

- [ ] **Step 2: Run it and confirm it fails**

Expected now: **10**. List them; they are the migration checklist.

- [ ] **Step 3: Record the ground truth before changing anything**

For a representative set of 20 members × the full content table, capture exactly what each can see today:

```sql
create table digest._tier3_visibility_baseline as
select p.at_member_id, ci.id as content_id
from (select at_member_id from digest.member_attributes
      where digest.is_active_member_status(membership_status) limit 20) p
cross join digest.content_items ci
where ci.access_rule->>'type' = 'public'
   or (ci.access_rule->>'type' = 'owner' and ci.access_rule->>'member' = p.at_member_id);
select count(*) from digest._tier3_visibility_baseline;
```

Every migrated consumer is diffed against this. **A visibility change in either direction is a failure** — showing less breaks the product, showing more is a leak.

- [ ] **Step 4: Build the rule table and the chokepoint**

Migration name: `tier3_audience_rules_20260813`

```sql
create table digest.audience_rule (
  rule_id     bigserial primary key,
  rule_type   text not null check (rule_type in
                ('public','owner','chat_member','fb_group','chapter_member','tier_member')),
  chapter     text references digest.chapters_catalog(chapter) on delete cascade,
  chat_id     text references digest.chats(chat_id) on delete cascade,
  owner_id    text references digest.member_profiles(at_member_id) on delete cascade,
  note        text,
  constraint audience_rule_shape check (
    case rule_type
      when 'public'         then chapter is null and chat_id is null and owner_id is null
      when 'owner'          then owner_id is not null and chapter is null and chat_id is null
      when 'chat_member'    then chat_id  is not null and chapter is null and owner_id is null
      when 'chapter_member' then chapter  is not null and chat_id is null and owner_id is null
      else true
    end)
);
revoke all on table digest.audience_rule from public, anon, authenticated;
grant select, insert, update, delete on table digest.audience_rule to service_role;

alter table digest.content_items add column audience_rule_id bigint
  references digest.audience_rule(rule_id) on delete restrict;
```

`chapter_member` is the type your chapter-restricted virtual event needs. It exists here as a row and a FK, not as a fifth branch in ten functions.

```sql
create or replace function digest.can_see(p_at_member_id text, p_item_id bigint)
returns boolean
language sql
stable
security definer
set search_path to 'digest', 'public'
as $$
  select exists (
    select 1
    from digest.content_items ci
    join digest.audience_rule r on r.rule_id = ci.audience_rule_id
    where ci.id = p_item_id
      and ci.sensitivity <> 'never_surface'
      and case r.rule_type
        when 'public' then true
        when 'owner'  then r.owner_id = p_at_member_id
        when 'chat_member' then exists (
          select 1 from digest.members m
          where m.at_member_id = p_at_member_id
            and r.chat_id = any(m.channels_present))
        when 'fb_group' then exists (
          select 1 from digest.member_link l
          where l.at_member_id = p_at_member_id and l.source = 'fb_uid')
        when 'chapter_member' then exists (
          select 1 from digest.member_attributes a
          where a.at_member_id = p_at_member_id
            and r.chapter = any(a.chapter_affiliation))
        else false
      end);
$$;
revoke all on function digest.can_see(text, bigint) from public, anon, authenticated;
grant execute on function digest.can_see(text, bigint) to service_role;
```

- [ ] **Step 5: Backfill rules from the existing jsonb**

```sql
insert into digest.audience_rule (rule_type, note) values ('public','backfilled 2026-08-13');
update digest.content_items ci set audience_rule_id =
  (select rule_id from digest.audience_rule where rule_type='public' limit 1)
where ci.access_rule->>'type' = 'public';

insert into digest.audience_rule (rule_type, owner_id, note)
select distinct 'owner', ci.access_rule->>'member', 'backfilled 2026-08-13'
from digest.content_items ci
where ci.access_rule->>'type' = 'owner'
  and exists (select 1 from digest.member_profiles p
              where p.at_member_id = ci.access_rule->>'member');

update digest.content_items ci set audience_rule_id = r.rule_id
from digest.audience_rule r
where ci.access_rule->>'type' = 'owner'
  and r.rule_type = 'owner' and r.owner_id = ci.access_rule->>'member';
```

Repeat for `chat_member` (keyed on `chat_id`) and `fb_group`. Then confirm **every** row has a rule:

```sql
select count(*) from digest.content_items where audience_rule_id is null;
-- EXPECTED: 0. Any row without a rule would become invisible -- stop if non-zero.
```

- [ ] **Step 6: Prove `can_see` matches the baseline exactly**

```sql
select count(*) as disagreements
from digest._tier3_visibility_baseline b
where digest.can_see(b.at_member_id, b.content_id) is not true;
-- EXPECTED: 0

select count(*) as newly_visible
from (select at_member_id from digest.member_attributes
      where digest.is_active_member_status(membership_status) limit 20) p
cross join digest.content_items ci
where digest.can_see(p.at_member_id, ci.id)
  and not exists (select 1 from digest._tier3_visibility_baseline b
                  where b.at_member_id = p.at_member_id and b.content_id = ci.id);
-- EXPECTED: 0. Anything above 0 is a leak. Do not proceed.
```

- [ ] **Step 7: Migrate the ten consumers, one commit each**

In this order, least to most exposed: `content_stats`, `fb_thread`, `fb_catchup`, `content_lookup`, `derive_member_attributes`, the two `content_ingest_*`, `fb_link_content`, `content_search`, `content_search_v2`.

After **each** one: re-run the Step 6 disagreement and leak checks, run the gate, commit. `fb_catchup` gets special attention — it is the one that already diverged, hardcoding `type='public'` with no `restricted` handling.

- [ ] **Step 8: Drop the jsonb column only after all ten are migrated**

Separate commit, separate session. Keep `access_rule` in place, unread, for a week first.

- [ ] **Step 9: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier3_task2_one_access_chokepoint.sql
git commit -m "feat: audience as data -- one can_see chokepoint replaces 10 jsonb branches

A fifth access type meant 10 edits on the privacy boundary. Now it is a row.
chapter_member added, which is what a chapter-restricted event needs.

Visibility diffed against a 20-member baseline after every consumer migration:
0 disagreements, 0 newly-visible rows.
Gate 253 exit 0."
```

---

### Task 3: Participation as one table

**Files:**
- Create: `digest.participation` (migration), `db/views/participation_compat.sql`
- Modify: readers of `video_speakers`, `call_attendance`, `event_registrations`, `partner_reviews`

**Interfaces:**
- Produces: `digest.participation(person_id, at_member_id, entity_kind, entity_id, role, occurred_at, source)` — one row per person-did-a-thing-to-an-entity.

**Background:** *spoke at*, *attended*, *authored*, *reviewed*, *registered for* are five separate implementations of one idea, and two of them (`video_speakers.member_record_id`, `partner_reviews.app_user_id`) resolve to nobody. Each also re-solves the member-or-not-a-member problem independently. `event_registrations` is the busiest table involved and #58's `event_registrations_live` chokepoint view lives on it — that view's semantics must survive.

- [ ] **Step 1: Write the failing assertion**

```sql
-- tests/assertions/tier3_task3_participation.sql
select to_regclass('digest.participation') is not null as exists,
       coalesce((select count(distinct role) from digest.participation), 0) as roles;
-- EXPECTED AFTER FIX: true, >= 4
```

- [ ] **Step 2: Create the table**

Migration name: `tier3_participation_20260813`

```sql
create table digest.participation (
  id           bigserial primary key,
  at_member_id text references digest.member_profiles(at_member_id) on delete no action,
  person_name  text,
  entity_kind  text not null check (entity_kind in ('event','video','call','partner','post')),
  entity_id    text not null,
  role         text not null check (role in
                 ('speaker','attendee','author','reviewer','registrant')),
  status       text,
  occurred_at  timestamptz,
  source       text not null,
  created_at   timestamptz not null default now(),
  unique (entity_kind, entity_id, role, coalesce(at_member_id, person_name))
);
create index participation_member_idx on digest.participation (at_member_id);
create index participation_entity_idx on digest.participation (entity_kind, entity_id);
revoke all on table digest.participation from public, anon, authenticated;
grant select, insert, update, delete on table digest.participation to service_role;
comment on table digest.participation is
  'One row per person-did-a-thing-to-an-entity. at_member_id nullable BY DESIGN --
   a speaker or attendee who is not a member is a real participant, carried by
   person_name. Replaces five separate implementations. Tier 3 Task 3.';
```

`at_member_id` nullable with `person_name` as the fallback is the direct answer to the speaker case: a non-member speaker is a first-class participant, not a failed match.

- [ ] **Step 3: Backfill all four sources**

```sql
insert into digest.participation (at_member_id, person_name, entity_kind, entity_id, role, occurred_at, source)
select s.at_member_id, s.display_name, 'video', v.video_id, 'speaker', s.joined_at, 'groupos'
from digest.videos_catalog v
join digest.video_speakers s on s.user_id = any(v.speaker_ids)
on conflict do nothing;

insert into digest.participation (at_member_id, person_name, entity_kind, entity_id, role, occurred_at, source)
select a.at_member_id, a.display_name, 'call', a.call_uuid, 'attendee', null, 'zoom'
from digest.call_attendance a
on conflict do nothing;

insert into digest.participation (at_member_id, person_name, entity_kind, entity_id, role, status, occurred_at, source)
select r.member_at_id, r.full_name, 'event', r.event_at_id, 'registrant', r.ticket_status, null, 'airtable_roster'
from digest.event_registrations r
on conflict do nothing;

insert into digest.participation (at_member_id, person_name, entity_kind, entity_id, role, occurred_at, source)
select null, null, 'partner', pr.partner_id, 'reviewer', null, 'groupos'
from digest.partner_reviews pr
on conflict do nothing;
```

The speaker join goes through the `text[]` — `video_speakers.user_id = any(videos_catalog.speaker_ids)`. Measured 2026-08-13: **472 speaker-video pairs, all 234 speakers matched, across 408 videos**. A speaker appearing on two videos is two participation rows, which is correct. If the insert yields materially fewer than 472, the `on conflict` clause is collapsing legitimate pairs — check the unique constraint before assuming it is deduplication.

- [ ] **Step 4: Verify row counts against sources**

```sql
select role, count(*) from digest.participation group by 1 order by 1;
-- EXPECTED: speaker 472 (234 speakers across 408 videos), attendee 4348,
-- registrant 17985, reviewer 928. Shortfalls mean the unique constraint collapsed
-- rows -- investigate whether that is correct deduplication or data loss.
```

- [ ] **Step 5: Preserve `event_registrations_live` semantics**

#58's rule: cancelled registrations (`ticket_status` Unconfirmed or No Show) never count as attendance. That rule must survive:

```sql
create or replace view digest.participation_live as
select * from digest.participation
where role <> 'registrant'
   or coalesce(status,'') not in ('Unconfirmed','No Show');
```

Prove parity against the existing view:

```sql
select count(*) as disagreements from (
  select event_at_id, member_at_id from digest.event_registrations_live
  except
  select entity_id, at_member_id from digest.participation_live
  where role='registrant' and entity_kind='event') x;
-- EXPECTED: 0
```

- [ ] **Step 6: Migrate readers one at a time**

`event_who`, `member_dossier_v2`, `event_lookup_v3`, the Zoom attendance readers. After each, diff its output against a recorded pre-change sample. Attendance remains **stored, never shown** — the standing Zoom rule survives the refactor.

- [ ] **Step 7: Retire the old tables after a week of parity**

Same discipline as Task 1: stop writing them, wait seven days, confirm no job errors and no output change, then drop in a separate commit.

- [ ] **Step 8: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py
python3 scripts/db_export_schema.py
git add db/ tests/assertions/tier3_task3_participation.sql
git commit -m "feat: participation -- one table for speaker, attendee, author, reviewer, registrant

Five implementations of one idea, two of which resolved to nobody. at_member_id is
nullable by design: a non-member speaker is a real participant, not a failed match.
#58's cancelled-registration rule preserved and parity-proven.

Gate 253 exit 0."
```

---

## Definition of Done for Tier 3

- [ ] All three assertion queries pass.
- [ ] `member_link` covers every source; match rate per lane is queryable and alarmed.
- [ ] `can_see` is the only interpreter of audience rules; the visibility baseline shows **0 disagreements and 0 newly-visible rows**.
- [ ] `participation` carries all four sources with #58's semantics preserved.
- [ ] A new source can be added by writing a loader plus rows — demonstrate it by adding one real source end to end (GroupOS documents is the queued candidate) and recording how many new functions it required. **The target is zero.**
- [ ] Old tables retired only after a week of parity, in separate commits.
- [ ] Gate exit 0; `git diff db/` empty after a fresh export.
- [ ] `SESSION_LOG_OLIVIA.md` entry and `SESSION_LOG.md` index line written.
