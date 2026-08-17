-- MDS event schema — normalized, foreign-keyed, logic-free.
--
-- Design rules (Andy, 2026-08-17):
--   * every table is connected by a real FOREIGN KEY, not a naming convention
--   * NO business logic in the database: no visibility RPCs, no computed views.
--     PostgREST resource embedding does the joins; the caller decides the rules.
--   * timestamps are TRUE instants. The source carries local wall-clock strings
--     with no zone ("08-23-2026" + "02:30 PM"); the loader converts using
--     events.timezone and keeps the raw strings for audit, never for reading.
--   * soft-deleted source rows (isDelete) are NOT imported.
--
-- Source: GroupOS prod export, event 689cfd00f1f12d7791cf9525.

create schema if not exists event;

-- ---------------------------------------------------------------- events
create table event.events (
  id                text primary key,               -- GroupOS ObjectId
  title             text not null,
  slug              text,
  timezone          text not null,                  -- IANA, e.g. Asia/Singapore
  starts_at         timestamptz,
  ends_at           timestamptz,
  status            text,
  city              text,
  country           text,
  short_description text,
  long_description  text,
  url               text,
  synced_at         timestamptz not null default now()
);

-- ------------------------------------------------------ participant types
-- Per event. The same word means a different row for a different event.
create table event.participant_types (
  id         text primary key,
  event_id   text not null references event.events(id) on delete cascade,
  role       text not null,                          -- Member | Guest | Speaker | Partner | Partners Team | Staff
  is_default boolean not null default false,
  unique (event_id, role)
);

-- ---------------------------------------------------------------- people
-- A human, independent of any event. Email is the identity key.
create table event.people (
  id            text primary key,                    -- GroupOS user ObjectId
  name          text,
  email         text not null,                       -- citext is not installed; uniqueness is case-insensitive below
  city          text,
  country       text,
  at_member_id  text,                                -- MDS member, resolved by the loader; NULL for non-members
  synced_at     timestamptz not null default now()
);
create unique index people_email_lower_key on event.people (lower(email));
create index on event.people (at_member_id) where at_member_id is not null;

-- ------------------------------------------------------------- attendees
-- One row per (person, event, type). A person holding two types at one event
-- is two rows and ONE human — headcount is count(distinct person_id).
create table event.attendees (
  id                  text primary key,
  event_id            text not null references event.events(id)            on delete cascade,
  person_id           text not null references event.people(id)            on delete restrict,
  participant_type_id text not null references event.participant_types(id) on delete restrict,
  is_manually_added   boolean,
  registered_at       timestamptz,
  unique (event_id, person_id, participant_type_id)
);
create index on event.attendees (event_id, person_id);

-- ---------------------------------------------------------------- places
-- Locations are venues with a street address. Rooms are subdivisions of one.
create table event.locations (
  id          text primary key,
  event_id    text not null references event.events(id) on delete cascade,
  name        text not null,
  address     text,
  city        text,
  country     text,
  postal_code text,
  latitude    numeric,
  longitude   numeric,
  place_id    text,                                   -- Google Places
  image_url   text,
  is_visible  boolean not null default true
);

create table event.rooms (
  id          text primary key,
  event_id    text not null references event.events(id)    on delete cascade,
  location_id text not null references event.locations(id) on delete restrict,
  name        text not null,
  sort_order  integer
);
create index on event.rooms (location_id);

-- ------------------------------------------------------------- activities
create table event.activities (
  id                 text primary key,
  event_id           text not null references event.events(id)    on delete cascade,
  location_id        text          references event.locations(id) on delete set null,  -- 19 of 50 have none
  name               text not null,
  short_description  text,
  long_description   text,
  starts_at          timestamptz not null,
  ends_at            timestamptz not null,
  status             text not null,                   -- published | paused
  is_check_in_allowed boolean not null default false,
  is_reserved        boolean not null default false,
  reserved_url       text,
  icon_url           text,
  notify_schedule_at timestamptz,                     -- GroupOS's own reminder
  source_date        text not null,                   -- raw "08-23-2026", audit only
  source_start_time  text not null,                   -- raw "02:30 PM",   audit only
  source_end_time    text not null,
  constraint activities_end_after_start check (ends_at > starts_at)
);
create index on event.activities (event_id, starts_at);
create index on event.activities (location_id);

-- Grant by type. Union with activity_person_grants; unchecked is not a deny.
create table event.activity_audience (
  activity_id         text not null references event.activities(id)        on delete cascade,
  participant_type_id text not null references event.participant_types(id) on delete cascade,
  primary key (activity_id, participant_type_id)
);
create index on event.activity_audience (participant_type_id);

-- Grant by named person — the admin's "Select rule" list.
create table event.activity_person_grants (
  activity_id text not null references event.activities(id) on delete cascade,
  person_id   text not null references event.people(id)     on delete cascade,
  primary key (activity_id, person_id)
);
create index on event.activity_person_grants (person_id);

-- --------------------------------------------------------------- sessions
-- A presentation inside an activity. Several run in parallel in one room by
-- design (Focus Groups), so overlap here is never a conflict.
create table event.sessions (
  id                text primary key,
  event_id          text not null references event.events(id)     on delete cascade,
  activity_id       text          references event.activities(id) on delete set null,  -- NULL = no audience, never surface
  room_id           text          references event.rooms(id)      on delete set null,
  title             text not null,
  short_description text,
  long_description  text,
  starts_at         timestamptz not null,
  ends_at           timestamptz not null,
  source_date       text not null,
  source_start_time text not null,
  source_end_time   text not null,
  constraint sessions_end_after_start check (ends_at > starts_at)
);
create index on event.sessions (event_id, starts_at);
create index on event.sessions (activity_id);

create table event.session_speakers (
  session_id text not null references event.sessions(id) on delete cascade,
  person_id  text not null references event.people(id)   on delete restrict,
  primary key (session_id, person_id)
);
create index on event.session_speakers (person_id);

-- --------------------------------------------------------------- check-ins
create table event.check_ins (
  id            text primary key,
  event_id      text not null references event.events(id)     on delete cascade,
  person_id     text not null references event.people(id)     on delete restrict,
  activity_id   text          references event.activities(id) on delete set null,
  kind          text,
  status        text,
  checked_in_at timestamptz
);
create index on event.check_ins (event_id, person_id);

-- -------------------------------------------------------------------- faq
create table event.faqs (
  id         text primary key,
  event_id   text not null references event.events(id) on delete cascade,
  question   text not null,
  answer     text,
  sort_order integer
);

-- -------------------------------------------------------- tickets / orders
create table event.tickets (
  id                 text primary key,
  event_id           text not null references event.events(id) on delete cascade,
  name               text not null,
  kind               text,
  base_price_cents   integer,
  quantity           integer,
  available_quantity integer
);

create table event.orders (
  id         text primary key,
  event_id   text not null references event.events(id) on delete cascade,
  person_id  text not null references event.people(id) on delete restrict,
  created_at timestamptz
);
create index on event.orders (event_id, person_id);

-- ------------------------------------------------------------------ access
-- Anonymous must never reach any of this. The service role reads it; the
-- caller applies the visibility rule:
--   visible(person, activity) =
--       exists attendee(person, event) with a type in activity_audience
--    OR exists activity_person_grants(activity, person)
revoke all on all tables in schema event from public, anon, authenticated;
alter default privileges in schema event revoke all on tables from public, anon, authenticated;
