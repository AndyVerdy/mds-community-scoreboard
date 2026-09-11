-- #211 phase 1: the web layer. Additive only; nothing pre-existing is altered.
-- Rollback: drop these four tables and the two views from 20260911_211_web_views.sql.

create table if not exists digest.member_web_profile (
  at_member_id   text not null,
  source_url     text not null,
  source_kind    text not null,          -- linkedin | company_site | search
  fetch_status   text not null,          -- ok | unreachable | empty | no_source
  fetched_at     timestamptz not null default now(),
  headline       text,                   -- the source's own one-line self-description, verbatim
  location       text,
  industry       text,
  headcount      text,                   -- banded exactly as the source gives it; never a false precision
  entity_id      text,                   -- Exa organization id for the primary employer, when present
  work_history   jsonb not null default '[]'::jsonb,
  education      jsonb not null default '[]'::jsonb,
  raw            jsonb,
  source_hash    text not null,
  model          text not null,
  confidence     numeric not null default 1.0,
  primary key (at_member_id, fetched_at)
);
comment on table digest.member_web_profile is
  '#211 append-only: one row per fetch. Current state = digest.member_web_profile_current.';

create index if not exists member_web_profile_member_idx
  on digest.member_web_profile (at_member_id, fetched_at desc);

create table if not exists digest.member_web_presence (
  at_member_id    text not null,
  url             text not null,
  domain          text not null,
  kind            text not null,   -- news | podcast | video | publication | speaking | company_page | aggregator
  title           text,
  published_at    date,
  summary         text,
  corroborated_by text,            -- the brand/company name that proved this is the right person
  confidence      numeric not null default 1.0,
  raw             jsonb,
  fetched_at      timestamptz not null default now(),
  primary key (at_member_id, url)
);

create index if not exists member_web_presence_kind_idx
  on digest.member_web_presence (at_member_id, kind);

create table if not exists digest.web_entity (
  entity_id         text primary key,   -- Exa id, else 'domain:<host>', else 'name:<slug>'
  entity_key_source text not null,      -- exa_id | domain | name
  kind              text not null,      -- company | person
  name              text not null,
  legal_name        text,
  domain            text,
  linkedin_url      text,
  industry          text,
  headcount         text,
  hq                text,
  web_traffic       jsonb,
  raw               jsonb,
  source_url        text not null,
  fetched_at        timestamptz not null default now(),
  confidence        numeric not null default 1.0
);

create table if not exists digest.web_edges (
  a_id        text not null,
  a_kind      text not null,    -- member | company | person | partner | external
  b_id        text not null,
  b_kind      text not null,
  edge_type   text not null,    -- works_at | founded | previously_at | colleague_of | owns_brand | parent_of | featured_in
  valid_from  date,
  valid_to    date,             -- null means current
  weight      numeric not null default 1.0,
  evidence    jsonb not null default '{}'::jsonb,
  source_url  text not null,
  fetched_at  timestamptz not null default now(),
  confidence  numeric not null default 1.0
);

-- A PRIMARY KEY may not contain an expression, and a plain unique index would let rows with a
-- null valid_from duplicate, because nulls are not equal to each other. NULLS NOT DISTINCT is
-- the correct construct and is available on this database (Postgres 17.6, checked 2026-09-11).
create unique index if not exists web_edges_uk on digest.web_edges
  (a_id, a_kind, b_id, b_kind, edge_type, valid_from) nulls not distinct;

create index if not exists web_edges_b_idx on digest.web_edges (b_id, b_kind, edge_type);
create index if not exists web_edges_type_idx on digest.web_edges (edge_type);

grant select, insert, update, delete on digest.member_web_profile  to postgres, service_role;
grant select, insert, update, delete on digest.member_web_presence to postgres, service_role;
grant select, insert, update, delete on digest.web_entity          to postgres, service_role;
grant select, insert, update, delete on digest.web_edges           to postgres, service_role;
revoke all on digest.member_web_profile, digest.member_web_presence,
              digest.web_entity, digest.web_edges from public, anon, authenticated;
