-- scripts/sql/20260908_public_gate_name_index_orgs_169.sql  (#169, fix round 5)
--
-- The name index is a list of PEOPLE. Its only filter was "at least 5 characters and contains a
-- space", so every ORGANISATION row sitting in members / member_attributes / speakers came through
-- with the people. Review finding (2026-09-08, confirmed against the live index): MDS Community,
-- MDS Partners, MDS Programs, MDS Member, MDS Chapters, MDS Test, Systems MDS, Andy MDS.
--
-- Because redact() matches full names case-insensitively, this mangled ordinary public copy — not an
-- odd row here and there:
--     "Ask the MDS Community about it; MDS Partners can help."
--       -> "Ask the a member about it; a seller in the community can help."
--     "the MDS community is generous"        ->  "the a member is generous"
-- Millie writes "the MDS community" constantly, so it fired on a large share of public answers and
-- published broken sentences.
--
-- Two shapes cover every proven row: MDS as the FIRST token and MDS as the LAST token. The exclusion
-- lives HERE and only here — public_gate.js deliberately masks whatever the index hands it, so the
-- RPC is the single guard and there is nothing to keep in sync on the module side.
create or replace function digest.public_gate_name_index()
returns table(name text, kind text)
language sql stable security definer set search_path = digest, pg_temp as $$
  select distinct trim(n) as name, k as kind from (
    select full_name as n, 'member' as k from digest.members            where full_name is not null
    union all
    select full_name,       'member'      from digest.member_attributes where full_name is not null
    union all
    select display_name,    'speaker'     from digest.speakers          where display_name is not null and kind = 'member'
  ) x
  where length(trim(n)) >= 5 and position(' ' in trim(n)) > 0   -- two-word names only; single words over-match
    and trim(n) not ilike 'MDS %'    -- org rows: MDS Community / Partners / Programs / Member / Chapters / Test
    and trim(n) not ilike '% MDS';   -- org rows: Systems MDS / Andy MDS
$$;
revoke all on function digest.public_gate_name_index() from public, anon, authenticated;
grant execute on function digest.public_gate_name_index() to service_role;
