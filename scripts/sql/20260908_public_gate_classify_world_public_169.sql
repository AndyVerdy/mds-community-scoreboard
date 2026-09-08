-- scripts/sql/20260908_public_gate_classify_world_public_169.sql  (#169, fix round 3)
--
-- Public here means the WORLD can already see it, not "every MDS member can".
--
-- Controller finding (2026-09-07, verified live): `content_items.access_rule->>'type' = 'public'`
-- means visible to every MDS member inside the app, NOT visible to the world — the rows carrying
-- it are `fb_post`/`fb_comment` (the PRIVATE Facebook group) and `call_transcript` (member-only
-- recordings on app.mds.co). `videos_catalog.access_restriction = 'public'` has the exact same
-- problem: it gates visibility INSIDE the members' app, not to the open internet. So the previous
-- classifier let Public mode name members off private-group posts and member-only call recordings,
-- and publish app.mds.co video links as "sources". Andy's rule for Public mode is "only from public
-- sources — what the world could already find". World-public today is exactly: the partner
-- directory (a public website) and events that carry a `public_page_url` (public event pages).
-- Everything else — WhatsApp, calls, videos in the members' app, the Facebook group, member
-- records — is closed for Public mode, regardless of what its internal access_rule/
-- access_restriction reads.
create or replace function digest.public_gate_classify(p_urls text[], p_source_ids text[])
returns table(key text, klass text, source text)
language sql stable security definer set search_path = digest, pg_temp as $$
  -- content rows: ALWAYS closed for Public mode (fb_post/fb_comment = the private Facebook group;
  -- call_transcript = a member-only recording). Keep returning them — by url, then by source_id —
  -- so the key comes back known-closed rather than absent; rowClass() would default an absent key
  -- to closed too, but an explicit row keeps the classification legible and auditable.
  select c.url as key, 'closed', 'content:' || c.source
  from digest.content_items c where c.url = any(coalesce(p_urls, '{}'))
  union all
  select c.source_id, 'closed', 'content:' || c.source
  from digest.content_items c where c.source_id = any(coalesce(p_source_ids, '{}'))
  union all
  -- partners: the directory is a public website
  -- #169 (verified 2026-09-07): partners_catalog has no partner_url column (only logo_url, an image).
  -- partner_lookup_v2 / partner_lookup both derive their `partner_url` output via
  -- digest.member_partner_url(partner_id), so we build the same key here rather than inventing a column.
  select digest.member_partner_url(p.partner_id), 'public', 'partner' from digest.partners_catalog p
  where p.status = 'published' and digest.member_partner_url(p.partner_id) = any(coalesce(p_urls, '{}'))
  union all
  -- events, by public page url: a public event page IS world-public.
  select e.public_page_url, 'public', 'event'
  from digest.events_catalog e
  where e.public_page_url = any(coalesce(p_urls, '{}'))
  union all
  -- events, by app url: the SAME event, keyed by the other column — this is the branch event_lookup*
  -- output actually lands on (fix round 2, #169). The app_url is a members'-app link, not a
  -- world-public one, so it is ALWAYS closed here regardless of public_page_url/app_is_public —
  -- an app flag is not world-public (fix round 3).
  select e.app_url, 'closed', 'event'
  from digest.events_catalog e
  where e.app_url = any(coalesce(p_urls, '{}'))
  union all
  -- videos: ALWAYS closed for Public mode. access_restriction gates visibility INSIDE the members'
  -- app (app.mds.co/videos/<id>); it says nothing about whether the WORLD can see it (fix round 3).
  select v.video_id::text, 'closed', 'video'
  from digest.videos_catalog v where v.video_id::text = any(coalesce(p_source_ids, '{}'));
$$;
revoke all on function digest.public_gate_classify(text[], text[]) from public, anon, authenticated;
grant execute on function digest.public_gate_classify(text[], text[]) to service_role;
