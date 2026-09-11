-- #211 read views. No SECURITY DEFINER, no gated function: Millie cannot reach these.

create or replace view digest.member_web_profile_current as
select distinct on (at_member_id) *
from digest.member_web_profile
order by at_member_id, fetched_at desc;

-- One graph to query; two tables to write. member_edges is deleted whole and rebuilt nightly by
-- derive_knowledge_graph(), so web edges must never live in it.
create or replace view digest.knowledge_graph as
select a_id, 'member'::text as a_kind, b_id, 'member'::text as b_kind,
       edge_type, null::date as valid_from, null::date as valid_to,
       weight, evidence, 'member_edges'::text as source
from digest.member_edges
union all
select a_id, a_kind, b_id, b_kind, edge_type, valid_from, valid_to,
       weight, evidence, 'web_edges'::text as source
from digest.web_edges;

-- The double-check. It compares and never merges; a member's own answer is untouched.
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
where c.location is not null
  and coalesce(mp.at_fields->>'City','') <> ''
  and lower(c.location) not like '%'||lower(mp.at_fields->>'City')||'%'
union all
select e.a_id, mp.full_name, 'company'::text,
       mp.at_fields->>'Brand Name',
       e.evidence->>'company_name',
       e.source_url, e.fetched_at
from digest.web_edges e
join digest.member_profiles mp on mp.at_member_id = e.a_id
where e.a_kind = 'member'
  and e.edge_type in ('works_at','founded')
  and e.valid_to is null                      -- only CURRENT roles can conflict with a current claim
  and coalesce(mp.at_fields->>'Brand Name','') <> ''
  and position(lower(e.evidence->>'company_name') in lower(mp.at_fields->>'Brand Name')) = 0;

grant select on digest.member_web_profile_current, digest.knowledge_graph,
                digest.member_fact_conflicts to postgres, service_role;
revoke all on digest.member_web_profile_current, digest.knowledge_graph,
              digest.member_fact_conflicts from public, anon, authenticated;
