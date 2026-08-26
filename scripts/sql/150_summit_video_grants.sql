-- #150 (Andy 2026-08-26): "Restrict them to summit attendees and staff."
--
-- Grants every video of ONE event to that event's attendees plus staff. Idempotent and
-- additive-only: rows already present are skipped, nothing is deleted. RERUN THIS after
-- each new batch of Summit videos lands — a video uploaded tomorrow has no grants until
-- a rerun (or an automated wrapper) writes them.
--
-- Attendee = the ticket roster (the #147 authority's source) OR the GroupOS door list,
-- so a speaker, partner or guest who was in the room is not shut out of the session
-- they were part of. Staff = digest.is_internal_record.
--
-- video_access's unique key is (video_id, lower(btrim(email))) and email is NOT NULL,
-- so grantees are deduped by email (duplicate member records share emails — #147) and
-- the one grantee with no email anywhere on file cannot be granted; the query below
-- reports rather than silently skips them (2026-08-26: exactly 1 of 179, a partner
-- door-list row with no member profile).
--
-- Usage: set the two ids, run the INSERT, then the report.

-- === the grant ===
with summit_videos as (
  select video_id from digest.videos_catalog
  where deleted_at is null
    and event_ids @> array['689cfd00f1f12d7791cf9525']   -- GroupOS event id
),
grantees as (
  select distinct member_at_id as at_member_id, 'event'::text src
    from digest.event_registrations_live
   where event_at_id = 'recrATwhUDA55iQN5'               -- Airtable event record
     and member_at_id is not null
  union
  select distinct p.at_member_id, 'event'
    from event.attendees a join event.people p on p.id = a.person_id
   where a.event_id = '689cfd00f1f12d7791cf9525' and p.at_member_id is not null
  union
  select at_member_id, 'staff' from digest.member_attributes
   where digest.is_internal_record(membership_status)
),
with_email as (
  select g.at_member_id, g.src, nullif(lower(btrim(mp.email)), '') email
  from grantees g
  left join digest.member_profiles mp on mp.at_member_id = g.at_member_id
),
picked as (
  select distinct on (email) at_member_id, src, email
  from with_email where email is not null
  order by email, src, at_member_id
)
insert into digest.video_access (video_id, at_member_id, email, source, added_at)
select v.video_id, p.at_member_id, p.email, p.src, now()
from summit_videos v
cross join picked p
where not exists (
  select 1 from digest.video_access x
  where x.video_id = v.video_id and lower(btrim(x.email)) = p.email
);

-- === the report: who could NOT be granted (no email anywhere) ===
-- select g.at_member_id from ( ...grantees... ) g
--   left join digest.member_profiles mp on mp.at_member_id = g.at_member_id
--  where nullif(lower(btrim(mp.email)), '') is null;
