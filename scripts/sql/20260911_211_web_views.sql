-- #211 read views. No SECURITY DEFINER, no gated function: Millie cannot reach these.
--
-- Fix round 3 (review): three bugs in these views.
--   1. member_web_profile_current picked the newest row regardless of fetch_status, so a failed
--      re-fetch (all-null) silently replaced a good profile. Now a fetch_status='ok' row is always
--      preferred; only a member who has NEVER had an 'ok' row falls back to the newest row.
--   2. knowledge_graph dropped `confidence` and `source_url` from both halves of the union, making
--      the "confidence 0.7 name-keyed rows are never surfaced" rule unenforceable downstream —
--      member_edges has neither column, so its half projects null for both.
--   3. member_fact_conflicts compared a member's own Airtable value (`at_fields->>'field'`) against
--      the *text of the whole JSON value* — for a multi-select this is the array's literal text,
--      brackets and quotes included (e.g. `["Leafael"]`), which can never match a plain web value
--      via substring containment. Fixed to unnest every real shape (a genuine jsonb array, a jsonb
--      string that itself contains JSON-array text, or a plain jsonb string; null -> no values) and
--      flag a conflict only when NONE of the member's own values agree with the web value in either
--      direction (either name containing the other counts as agreement) — done identically for both
--      the location and the company branch.

create or replace view digest.member_web_profile_current as
select distinct on (at_member_id) *
from digest.member_web_profile
order by at_member_id, (fetch_status = 'ok') desc, fetched_at desc;

-- One graph to query; two tables to write. member_edges is deleted whole and rebuilt nightly by
-- derive_knowledge_graph(), so web edges must never live in it.
create or replace view digest.knowledge_graph as
select a_id, 'member'::text as a_kind, b_id, 'member'::text as b_kind,
       edge_type, null::date as valid_from, null::date as valid_to,
       weight, evidence, 'member_edges'::text as source,
       null::numeric as confidence, null::text as source_url
from digest.member_edges
union all
select a_id, a_kind, b_id, b_kind, edge_type, valid_from, valid_to,
       weight, evidence, 'web_edges'::text as source,
       confidence, source_url
from digest.web_edges;

-- The double-check. It compares and never merges; a member's own answer is untouched.
--
-- at_fields values arrive in three real shapes (measured live 2026-09-11, same shapes
-- scripts/exa_member_presence.py's _values() already had to handle): a genuine jsonb array (an
-- Airtable multi-select, e.g. "Brand Name": ["Leafael"]), a jsonb string whose text itself is a
-- JSON array literal, or a plain jsonb string. pg_input_is_valid (Postgres 16+; this database is
-- 17.6) lets the middle case be detected without risking a cast error on the many rows that are
-- simply plain text starting with something other than "[".
create or replace view digest.member_fact_conflicts as
select c.at_member_id,
       mp.full_name,
       'location'::text as field,
       mp.at_fields->>'City' as ours,
       c.location as web,
       c.source_url,
       c.fetched_at
from digest.member_web_profile_current c
join digest.member_profiles mp on mp.at_member_id = c.at_member_id
cross join lateral (
  select coalesce(array_agg(v) filter (where coalesce(v, '') <> ''), array[]::text[]) as vals
  from jsonb_array_elements_text(
    case
      when (mp.at_fields -> 'City') is null then '[]'::jsonb
      when jsonb_typeof(mp.at_fields -> 'City') = 'array' then mp.at_fields -> 'City'
      when jsonb_typeof(mp.at_fields -> 'City') = 'string'
           and left(mp.at_fields ->> 'City', 1) = '['
           and pg_input_is_valid(mp.at_fields ->> 'City', 'jsonb')
           and jsonb_typeof((mp.at_fields ->> 'City')::jsonb) = 'array'
        then (mp.at_fields ->> 'City')::jsonb
      else jsonb_build_array(mp.at_fields ->> 'City')
    end
  ) as v
) city_vals
where coalesce(c.location, '') <> ''
  and cardinality(city_vals.vals) > 0
  -- conflict only when NONE of the member's own City values agree (either direction) with the web value
  and not exists (
    select 1 from unnest(city_vals.vals) cv
    where position(lower(cv) in lower(c.location)) > 0
       or position(lower(c.location) in lower(cv)) > 0
  )
union all
select e.a_id, mp.full_name, 'company'::text,
       mp.at_fields->>'Brand Name',
       e.evidence->>'company_name',
       e.source_url, e.fetched_at
from digest.web_edges e
join digest.member_profiles mp on mp.at_member_id = e.a_id
cross join lateral (
  select coalesce(array_agg(v) filter (where coalesce(v, '') <> ''), array[]::text[]) as vals
  from jsonb_array_elements_text(
    case
      when (mp.at_fields -> 'Brand Name') is null then '[]'::jsonb
      when jsonb_typeof(mp.at_fields -> 'Brand Name') = 'array' then mp.at_fields -> 'Brand Name'
      when jsonb_typeof(mp.at_fields -> 'Brand Name') = 'string'
           and left(mp.at_fields ->> 'Brand Name', 1) = '['
           and pg_input_is_valid(mp.at_fields ->> 'Brand Name', 'jsonb')
           and jsonb_typeof((mp.at_fields ->> 'Brand Name')::jsonb) = 'array'
        then (mp.at_fields ->> 'Brand Name')::jsonb
      else jsonb_build_array(mp.at_fields ->> 'Brand Name')
    end
  ) as v
) brand_vals
where e.a_kind = 'member'
  and e.edge_type in ('works_at','founded')
  and e.valid_to is null                      -- only CURRENT roles can conflict with a current claim
  and coalesce(e.evidence->>'company_name','') <> ''
  and cardinality(brand_vals.vals) > 0
  -- conflict only when NONE of the member's own Brand Name values agree (either direction) with the web value
  and not exists (
    select 1 from unnest(brand_vals.vals) bv
    where position(lower(bv) in lower(e.evidence->>'company_name')) > 0
       or position(lower(e.evidence->>'company_name') in lower(bv)) > 0
  );

grant select on digest.member_web_profile_current, digest.knowledge_graph,
                digest.member_fact_conflicts to postgres, service_role;
revoke all on digest.member_web_profile_current, digest.knowledge_graph,
              digest.member_fact_conflicts from public, anon, authenticated;
