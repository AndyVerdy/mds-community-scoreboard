-- scripts/sql/20260908_public_gate_classify_app_url_169.sql  (#169, fix round 2)
-- The events branch keyed itself on `coalesce(public_page_url, app_url)` and matched p_urls against
-- that same coalesce. But `event_lookup` / `event_lookup_v2` / `event_lookup_v3` hand the answer loop
-- `event_url = coalesce(app_url, public_page_url)` — the OPPOSITE preference. So an event that has
-- BOTH columns filled reached the gate as its app_url and matched nothing here: no classify row, and
-- `rowClass()`'s documented default ("Unknown = closed") masked every speaker name on a genuinely
-- public event. Match BOTH columns instead, each keyed by the url that actually matched; the class
-- itself is unchanged (public when there is a public page, or the app flag says public).
-- Everything else in this function is byte-identical to 20260907_public_gate_rpcs_169.sql.
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
  -- events, by public page url: public only with a public page (or the app flag)
  select e.public_page_url, case when e.public_page_url is not null or e.app_is_public then 'public' else 'closed' end, 'event'
  from digest.events_catalog e
  where e.public_page_url = any(coalesce(p_urls, '{}'))
  union all
  -- events, by app url: the SAME event, keyed by the other column — this is the branch event_lookup*
  -- output actually lands on (fix round 2, #169)
  select e.app_url, case when e.public_page_url is not null or e.app_is_public then 'public' else 'closed' end, 'event'
  from digest.events_catalog e
  where e.app_url = any(coalesce(p_urls, '{}'))
  union all
  -- videos: by video id passed as a source id
  select v.video_id::text, case when v.access_restriction = 'public' then 'public' else 'closed' end, 'video'
  from digest.videos_catalog v where v.video_id::text = any(coalesce(p_source_ids, '{}'));
$$;
revoke all on function digest.public_gate_classify(text[], text[]) from public, anon, authenticated;
grant execute on function digest.public_gate_classify(text[], text[]) to service_role;
