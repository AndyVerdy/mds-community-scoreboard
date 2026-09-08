-- scripts/sql/20260907_public_gate_rpcs_169.sql  (#169)
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
  where length(trim(n)) >= 5 and position(' ' in trim(n)) > 0;   -- two-word names only; single words over-match
$$;
revoke all on function digest.public_gate_name_index() from public, anon, authenticated;
grant execute on function digest.public_gate_name_index() to service_role;

create or replace function digest.public_gate_classify(p_urls text[], p_source_ids text[])
returns table(key text, klass text, source text)
language sql stable security definer set search_path = digest, pg_temp as $$
  -- content rows: by url, then by source_id
  select c.url as key,
         case when c.access_rule->>'type' = 'public' and coalesce(c.sensitivity,'normal') = 'normal' then 'public' else 'closed' end,
         'content:' || c.source
  from digest.content_items c where c.url = any(coalesce(p_urls, '{}'))
  union all
  select c.source_id, case when c.access_rule->>'type' = 'public' and coalesce(c.sensitivity,'normal') = 'normal' then 'public' else 'closed' end, 'content:' || c.source
  from digest.content_items c where c.source_id = any(coalesce(p_source_ids, '{}'))
  union all
  -- partners: the directory is public
  -- #169 (verified 2026-09-07): partners_catalog has no partner_url column (only logo_url, an image).
  -- partner_lookup_v2 / partner_lookup both derive their `partner_url` output via
  -- digest.member_partner_url(partner_id), so we build the same key here rather than inventing a column.
  select digest.member_partner_url(p.partner_id), 'public', 'partner' from digest.partners_catalog p
  where p.status = 'published' and digest.member_partner_url(p.partner_id) = any(coalesce(p_urls, '{}'))
  union all
  -- events: public only with a public page (or the app flag)
  select coalesce(e.public_page_url, e.app_url), case when e.public_page_url is not null or e.app_is_public then 'public' else 'closed' end, 'event'
  from digest.events_catalog e
  where coalesce(e.public_page_url, e.app_url) = any(coalesce(p_urls, '{}'))
  union all
  -- videos: by video id passed as a source id
  select v.video_id::text, case when v.access_restriction = 'public' then 'public' else 'closed' end, 'video'
  from digest.videos_catalog v where v.video_id::text = any(coalesce(p_source_ids, '{}'));
$$;
revoke all on function digest.public_gate_classify(text[], text[]) from public, anon, authenticated;
grant execute on function digest.public_gate_classify(text[], text[]) to service_role;
