-- #147 · one answer to "is this member registered for this event"
--
-- Two lanes were each working it out for themselves. The schedule lane read the
-- GroupOS export (event.attendees, matched by registration email); who-to-meet read
-- the Airtable roster mirror (digest.event_registrations_live, matched by the roster's
-- Match to Member). Different keys, different rules, so one could say yes while the
-- other said no in the same conversation a minute apart (Andy, 2026-08-25 01:38-02:12).
--
-- Measured on the Summit before this shipped: 140 GroupOS attendees carry an
-- at_member_id, 130 members are on the roster, 117 agree — 23 in GroupOS only and
-- 13 on the roster only, so 36 members got a different answer depending on which
-- lane they happened to ask. Resolving both sides through the alias bridge that
-- already exists collapses 19 of those 36; the rest are genuine source differences.
--
-- The datasets are NOT merged: they do two different jobs (an operational agenda vs
-- the commercial ticket record) and merging them is a migration for nothing. Instead
-- the RULE lives here, once, and every gated lane calls it.
--
-- The Airtable roster is the authority. The alias bridge sits underneath it so a
-- member who exists as several records cannot be split in half by which record a
-- given lane happened to resolve.

-- ---------------------------------------------------------------- the authority
create or replace function digest.registration_status(p_member text, p_event text)
returns table (
  is_registered     boolean,
  matched_via       text,
  roster_synced_at  timestamptz,
  roster_stale_days integer
)
language sql
stable
security definer
set search_path to 'digest', 'pg_temp'
as $function$
  with me as (
    select nullif(btrim(p_member), '') as at_member_id
  ),
  -- every email we know for this person, from the alias bridge (#100, 5,763 rows)
  my_emails as (
    select distinct lower(btrim(a.email)) as email
      from digest.member_email_alias a, me
     where a.at_member_id = me.at_member_id
       and nullif(btrim(a.email), '') is not null
  ),
  -- and every member record that shares one of those emails: the duplicate records
  -- of the SAME person. This is the bridge the loaders never consulted.
  my_ids as (
    select at_member_id from me where at_member_id is not null
    union
    select distinct a.at_member_id
      from digest.member_email_alias a
     where lower(btrim(a.email)) in (select email from my_emails)
  ),
  -- the roster rows for this event. The _live view already drops Unconfirmed and
  -- No Show upstream, so any row it still carries is a live ticket — that is the
  -- ticket-status rule, stated here and nowhere else (#96: a member with a live
  -- ticket is planning around the event, so it is theirs).
  roster as (
    select r.member_at_id, lower(btrim(r.email)) as email, r.synced_at
      from digest.event_registrations_live r
     where r.event_at_id = nullif(btrim(p_event), '')
  ),
  hit as (
    select
      bool_or(r.member_at_id is not null
              and r.member_at_id = (select at_member_id from me))          as by_own_id,
      bool_or(r.member_at_id is not null
              and r.member_at_id in (select at_member_id from my_ids))     as by_alias_id,
      bool_or(r.email is not null and r.email in (select email from my_emails)) as by_email,
      max(r.synced_at)                                                     as synced_at
    from roster r
  )
  select
    coalesce(by_own_id or by_alias_id or by_email, false),
    case
      when coalesce(by_own_id, false)   then 'member_id'
      when coalesce(by_alias_id, false) then 'alias_member_id'
      when coalesce(by_email, false)    then 'alias_email'
    end,
    synced_at,
    case when synced_at is not null
         then greatest(0, extract(day from (now() - synced_at))::integer) end
  from hit
$function$;

comment on function digest.registration_status(text, text) is
  '#147 — THE registration authority. The Airtable roster is the source; the alias '
  'bridge resolves duplicate member records underneath it. Every gated lane calls '
  'this instead of writing its own check. Also reports how stale the roster mirror '
  'is, so a month-old snapshot can never gate a member silently.';

-- ------------------------------------------------------- the boolean every lane wants
-- A thin wrapper so the rule above stays the only place the rule is written.
create or replace function digest.is_registered(p_member text, p_event text)
returns boolean
language sql
stable
security definer
set search_path to 'digest', 'pg_temp'
as $function$
  select coalesce((select s.is_registered from digest.registration_status(p_member, p_event) s), false)
$function$;

comment on function digest.is_registered(text, text) is
  '#147 — boolean gate for a member against an event. Thin wrapper over '
  'digest.registration_status so the rule lives in exactly one place.';

grant execute on function digest.registration_status(text, text) to anon, authenticated, service_role;
grant execute on function digest.is_registered(text, text)       to anon, authenticated, service_role;
