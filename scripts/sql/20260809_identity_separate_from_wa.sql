-- #77 — separate IDENTITY from WhatsApp membership.
--
-- The bug: every retrieval function answered "who is asking?" with
--     select ... from digest.members m where m.phone = p_phone and is_active(m.membership_status)
-- and digest.members only holds people who appear in a synced WhatsApp chat. An active member who
-- has never been in a tracked chat had no row, so the guard found nothing and Olivia refused them
-- everything — not just chat content, but events, partners, their own member card. Membership was
-- being inferred from a channel.
--
-- The fix, in three parts:
--   1. digest.member_phones      — every known phone per member, from the Airtable profile
--                                  (Preferred Phone Number, WhatsApp Number) plus members.phone,
--                                  normalised to the last 10 digits.
--   2. digest.member_phone_index — the same thing materialised, because member_phones re-parses
--                                  jsonb across ~5,900 profiles and resolve_asker() timed out at
--                                  the top of every call. Refreshed by refresh_member_phone_index().
--                                  FAIL-CLOSED: a phone that maps to more than one member is left
--                                  out entirely rather than resolved to a guess.
--   3. digest.member_identity    — digest.members UNION ALL a synthetic row per active member who
--                                  has no members row. channels_present = '{}' for those, so chat
--                                  visibility is unchanged: they are identified, not admitted.
--
-- Status still comes from member_attributes at query time (LIVE, never a copy), so a cancellation
-- takes effect on the next question.
--
-- Applied as migrations on 2026-08-09; this file is the readable record. The authoritative text of
-- every object is the export in db/ (scripts/db_export_schema.py).

-- ── 1. every known phone per member ──────────────────────────────────────────────────────────
create or replace view digest.member_phones as
with raw as (
  select ma.at_member_id, 'at_preferred' src, ma.at_fields->>'Preferred Phone Number' phone
    from digest.member_attributes ma
  union all
  select ma.at_member_id, 'at_whatsapp', ma.at_fields->>'WhatsApp Number'
    from digest.member_attributes ma
  union all
  select m.at_member_id, 'wa_members', m.phone
    from digest.members m where m.at_member_id is not null
)
select at_member_id, src source, right(regexp_replace(phone, '\D', '', 'g'), 10) phone10
  from raw
 where phone is not null
   and length(regexp_replace(phone, '\D', '', 'g')) >= 10;

-- ── 2. the indexed form resolve_asker() actually reads ───────────────────────────────────────
create table if not exists digest.member_phone_index (
  phone10       text primary key,
  at_member_id  text not null,
  source        text,
  refreshed_at  timestamptz not null default now()
);

-- Uniqueness is judged over ACTIVE members only, and that detail is the whole design.
--
-- The first cut refused any phone owned by more than one at_member_id, and that cost 60 active
-- members their access — people who worked before #77. A regression, not a tightening.
--
-- Measured live: of 230 ambiguous phones, 136 are duplicate records of one person and 94 are
-- different people, but ZERO have more than one ACTIVE owner. Every collision is
-- active-vs-inactive or a duplicate row, so the mistaken-identity leak cannot occur once
-- uniqueness is computed over actives: there is no second live person to be confused with.
--
-- Still fail-closed where it counts: two ACTIVE members on one number leaves that number out of
-- the index entirely, resolving to nobody. This is strictly safer than the code #77 replaced,
-- which did `where m.phone = p_phone ... limit 1` and answered as whichever row Postgres returned.
create or replace function digest.refresh_member_phone_index()
returns integer language plpgsql security definer set search_path = digest, public as $$
declare n integer;
begin
  with active_owner as (
    select p.phone10, p.at_member_id, min(p.source) source
      from digest.member_phones p
      join digest.member_attributes ma on ma.at_member_id = p.at_member_id
     where digest.is_active_member_status(ma.membership_status)
     group by p.phone10, p.at_member_id
  ),
  unambiguous as (
    select phone10, min(at_member_id) at_member_id, min(source) source
      from active_owner
     group by phone10
    having count(distinct at_member_id) = 1
  ),
  upserted as (
    insert into digest.member_phone_index (phone10, at_member_id, source, refreshed_at)
    select phone10, at_member_id, source, now() from unambiguous
    on conflict (phone10) do update
      set at_member_id = excluded.at_member_id,
          source       = excluded.source,
          refreshed_at = now()
    returning 1
  )
  select count(*) into n from upserted;

  -- drop numbers that no longer belong to exactly one active member (cancelled, phone changed,
  -- or a second active member appeared on the same number)
  delete from digest.member_phone_index i
   where not exists (
     select 1 from digest.member_phones p
       join digest.member_attributes ma on ma.at_member_id = p.at_member_id
      where p.phone10 = i.phone10
        and p.at_member_id = i.at_member_id
        and digest.is_active_member_status(ma.membership_status));
  return n;
end $$;

-- Refreshed in-database every 15 minutes, matching the Airtable -> digest.members mirror
-- (n8n Oy7RYcgLfDYhrPvw), so a member is answerable within 15 minutes of their phone landing in
-- Airtable. A full rebuild measured 544 ms over 3,867 phones. pg_cron and not launchd on purpose:
-- identity must not depend on a laptop being awake.
select cron.schedule('member-phone-index', '*/15 * * * *',
                     $$select digest.refresh_member_phone_index()$$);
-- digest.olivia_health_check() signal 6 alarms if the index has not refreshed in 60 minutes —
-- a dead refresher locks new members out silently, which is the exact bug #77 exists to fix.

create or replace function digest.resolve_asker(p_phone text)
returns text language sql stable security definer set search_path = digest, public as $$
  select i.at_member_id
    from digest.member_phone_index i
    join digest.member_attributes ma on ma.at_member_id = i.at_member_id
   where i.phone10 = right(regexp_replace(coalesce(p_phone, ''), '\D', '', 'g'), 10)
     and digest.is_active_member_status(ma.membership_status)
   limit 1;
$$;

-- ── 3. identity = WA rows + actives who have no WA row ───────────────────────────────────────
create or replace view digest.member_identity as
select m.at_member_id, m.phone, m.name, m.membership_status, m.channels_present, false is_synthetic
  from digest.members m
union all
select ma.at_member_id, i.phone10, ma.full_name, ma.membership_status,
       '{}'::text[],                       -- in no tracked chat: identified, not admitted
       true
  from digest.member_phone_index i
  join digest.member_attributes ma on ma.at_member_id = i.at_member_id
 where digest.is_active_member_status(ma.membership_status)
   and not exists (select 1 from digest.members m where m.at_member_id = ma.at_member_id);

-- ── 4. point every asker guard at identity, not at the WA table ──────────────────────────────
-- Done in place with pg_get_functiondef + regexp_replace across all digest functions rather than
-- by retyping 44 bodies. Two passes were needed: the first matched only alias `m`, and so did the
-- verification query, which is why it reported "0 left" while nine functions using aliases `mz`
-- and `r` were still resolving by phone. The end-state assertion below is alias-agnostic and is
-- the check that matters — it aborts the migration rather than reporting a false green.
do $rewrite$
declare r record; src text; newsrc text; n int := 0; leftover int; who text;
begin
  for r in
    select p.oid, p.proname from pg_proc p
    join pg_namespace ns on ns.oid = p.pronamespace
    where ns.nspname = 'digest' and p.prokind = 'f'
      and pg_get_functiondef(p.oid) ~ '\w+\.phone = p_phone'
    order by p.proname
  loop
    src := pg_get_functiondef(r.oid);
    newsrc := regexp_replace(src,
      'from digest\.members (\w+)(\s+)where \1\.phone = p_phone and digest\.is_active_member_status\(\1\.membership_status\)',
      'from digest.member_identity \1\2where \1.at_member_id = digest.resolve_asker(p_phone) and digest.is_active_member_status(\1.membership_status)',
      'g');
    newsrc := regexp_replace(newsrc,
      'from digest\.members (\w+)(\s+)where \(case when p_at_member_id is not null then \1\.at_member_id = p_at_member_id else \1\.phone = p_phone end\)',
      'from digest.member_identity \1\2where (case when p_at_member_id is not null then \1.at_member_id = p_at_member_id else \1.at_member_id = digest.resolve_asker(p_phone) end)',
      'g');
    newsrc := regexp_replace(newsrc, '(\w+)\.phone = p_phone',
                             '\1.at_member_id = digest.resolve_asker(p_phone)', 'g');
    if newsrc <> src then execute newsrc; n := n + 1; end if;
  end loop;

  select count(*), string_agg(p.proname, ', ') into leftover, who
  from pg_proc p join pg_namespace ns on ns.oid = p.pronamespace
  where ns.nspname = 'digest' and p.prokind = 'f'
    and pg_get_functiondef(p.oid) ~ '\w+\.phone = p_phone';
  raise notice '#77: % rewritten, % left', n, leftover;
  if leftover > 0 then
    raise exception '#77 still resolving by phone in: % — aborting', who;
  end if;
end
$rewrite$;
