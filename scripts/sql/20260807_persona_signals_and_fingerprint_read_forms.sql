-- Applied to Supabase (digest schema) 2026-08-07 as migrations
--   persona_signals_reads_forms
--   persona_fingerprint_includes_forms
--   persona_signals_compact_self_reported
--   persona_signals_keep_matrix_row_in_label
-- Kept in git because the SQL layer otherwise lives only in the live DB (ticket #65).
-- This file carries the CURRENT definition of both functions.
--
-- #20 AC③ — personas draw on the forms warehouse, not just tick-box attributes.
--
-- Two edits are needed to connect ANY source to personas, and the census had neither:
--   persona_signals            = what the nightly derivation SEES
--   persona_signal_fingerprints = what makes a member DUE for a rebuild
-- Before this, a member could fill in the whole census and their fingerprint stayed identical,
-- so no rebuild fired; and a forced rebuild would not have shown the model the answers anyway.
--
-- `self_reported` is the member's own latest answer per canonical field across every
-- profile-scope form, newest wins — so a staffing or cost answer from the 2026 census
-- supersedes the same field from a legacy census (digest.form_windowed's rule, applied here
-- directly against the matview so the SECURITY DEFINER wrapper cannot block inlining).
-- Free-text answers are EXCLUDED until Andy rules on exposure (#20 P2): structured answers
-- shape a persona silently, long-form answers are the ones that could be quoted back.
--
-- Personas are owner-scoped everywhere they surface (member_dossier / member_dossier_v2 /
-- multi_source_v2 'me' block all resolve to the ASKER), which is what makes this consistent
-- with the standing rule: silent personalization fine, raw answers owner-only.

create or replace function digest.persona_signals(p_at_member_id text)
 returns jsonb
 language plpgsql
 stable security definer
 set search_path to 'digest', 'pg_temp'
as $function$
declare
  v_phone text; v_name text; v_n int;
begin
  select count(*) into v_n from digest.member_attributes ma where ma.at_member_id = p_at_member_id;
  if v_n <> 1 then return '{}'::jsonb; end if;
  select ma.full_name into v_name from digest.member_attributes ma where ma.at_member_id = p_at_member_id;
  select min(m.phone) into v_phone from digest.members m
  where m.at_member_id = p_at_member_id and m.phone is not null;

  return jsonb_build_object(
    'name', v_name,
    'attributes', (select to_jsonb(ma) - 'rev_band' - 'provenance' - 'at_member_id'
                   from digest.member_attributes ma where ma.at_member_id = p_at_member_id),
    -- flat strings, not nested objects: the nested form was 82% of the whole payload and the
    -- caller truncates at 32k. Long questions keep head AND tail so the matrix row survives
    -- ("…what do you pay them monthly? (Bookkeeper)").
    'self_reported', (select coalesce(jsonb_agg(
                        case when length(f.question) > 88
                             then left(f.question, 50) || '…' || right(f.question, 36)
                             else f.question end
                        || ' = ' || left(f.ans, 80) || ' (' || f.submitted_at::date || ')'
                        order by f.canonical_key), '[]'::jsonb)
                      from (
                        select distinct on (e.canonical_key)
                               e.canonical_key, e.question, e.submitted_at,
                               case when jsonb_typeof(e.value) = 'array'
                                    then (select string_agg(x, ' / ')
                                          from jsonb_array_elements_text(e.value) x)
                                    else e.value #>> '{}' end as ans
                        from digest.form_answers_exploded e
                        join digest.form_scope s on s.form_id = e.form_id and s.scope = 'profile'
                        where e.member_at_id = p_at_member_id
                          and e.answer_type <> 'text'
                          and nullif(trim(coalesce(e.question, '')), '') is not null
                        order by e.canonical_key, e.submitted_at desc
                      ) f
                      where nullif(trim(coalesce(f.ans, '')), '') is not null),
    'wa_chats_member_of', (select to_jsonb(m.channels_present) from digest.members m
                           where m.at_member_id = p_at_member_id and m.phone = v_phone limit 1),
    'questions_180d', case when v_phone is null then '[]'::jsonb else
                      (select coalesce(jsonb_agg(jsonb_build_object(
                        'd', om.created_at::date, 'q', left(om.text, 200)) order by om.created_at desc), '[]'::jsonb)
                      from (select * from digest.olivia_messages om
                            where om.phone = v_phone and om.role = 'member'
                              and coalesce(om.wamid, '') not like '%SELFTEST%'
                              and om.created_at > now() - interval '180 days'
                            order by om.created_at desc limit 60) om) end,
    'events_attended', (select coalesce(jsonb_agg(jsonb_build_object(
                          'name', coalesce(ec.app_title, ec.name),
                          'when', coalesce(ec.app_starts_at, ec.start_at)::date) order by coalesce(ec.app_starts_at, ec.start_at) desc), '[]'::jsonb)
                        from (select * from digest.event_registrations_live r
                              join digest.events_catalog ec on ec.at_record_id = r.event_at_id
                              where r.member_at_id = p_at_member_id and r.ticket_status = 'Confirmed'
                              order by coalesce(ec.app_starts_at, ec.start_at) desc limit 15) ec),
    'authored_recent', case when v_phone is not null then
                        (select coalesce(jsonb_agg(jsonb_build_object(
                          'src', c.source, 'd', c.occurred_at::date,
                          't', left(coalesce(nullif(c.title, ''), c.body), 220))), '[]'::jsonb)
                        from digest.content_search_v2(p_phone => v_phone, p_terms => '{}'::text[],
                          p_author => v_name, p_sources => array['fb_post', 'fb_comment', 'wa_message'],
                          p_limit => 30) c)
                      else
                        (select coalesce(jsonb_agg(jsonb_build_object(
                          'src', x.src, 'd', x.d, 't', x.t)), '[]'::jsonb)
                         from (
                           select 'fb_post' as src, p.created_time::date as d, left(p.text, 220) as t
                           from digest.fb_posts p where p.author_name = v_name and p.text is not null
                           union all
                           select 'fb_comment', c.created_time::date, left(c.text, 220)
                           from digest.fb_comments c where c.author_name = v_name and c.text is not null
                           order by d desc nulls last
                           limit 30) x)
                      end
  );
end $function$;

create or replace function digest.persona_signal_fingerprints()
 returns table(member_at_id text, member_phone text, member_name text, fingerprint text)
 language sql
 stable security definer
 set search_path to 'digest', 'pg_temp'
as $function$
  with actives as (
    select ma.at_member_id as atid, ma.full_name as nm
    from digest.member_attributes ma
    where ma.membership_status in ('Current Member', 'New Member', 'Current Member- Not Renewing', 'Staff')
  ), ph as (
    select m.at_member_id as atid, min(m.phone) as phone
    from digest.members m where m.phone is not null and m.at_member_id is not null
    group by m.at_member_id
  ), q as (
    select om.phone as phx, count(*) as n, max(om.created_at) as mx
    from digest.olivia_messages om
    where om.role = 'member' and coalesce(om.wamid, '') not like '%SELFTEST%'
      and om.created_at > now() - interval '180 days'
    group by om.phone
  ), att as (
    select r.member_at_id as atid, count(*) as n, max(coalesce(ec.app_starts_at, ec.start_at)) as mx
    from digest.event_registrations_live r
    join digest.events_catalog ec on ec.at_record_id = r.event_at_id
    where r.ticket_status = 'Confirmed' and r.member_at_id is not null
    group by r.member_at_id
  ), fb as (
    select p.author_name as nm, count(*) as n, max(p.created_time) as mx
    from digest.fb_posts p
    where p.created_time > now() - interval '180 days'
    group by p.author_name
  ), fm as (
    -- profile-scope form answers: a new submission, a re-mapped field or a corrected answer
    -- all move this term, which is what makes the member due for a rebuild
    select e.member_at_id as atid, count(*) as n, max(e.submitted_at) as mx
    from digest.form_answers_exploded e
    join digest.form_scope s on s.form_id = e.form_id and s.scope = 'profile'
    where e.member_at_id is not null
    group by e.member_at_id
  )
  select a.atid, ph.phone, a.nm,
         md5(coalesce(ma.refreshed_at::text, '') || '|'
             || coalesce(q.n, 0)::text || '@' || coalesce(q.mx::text, '') || '|'
             || coalesce(att.n, 0)::text || '@' || coalesce(att.mx::text, '') || '|'
             || coalesce(fb.n, 0)::text || '@' || coalesce(fb.mx::text, '') || '|'
             || coalesce(fm.n, 0)::text || '@' || coalesce(fm.mx::text, ''))
  from actives a
  join digest.member_attributes ma on ma.at_member_id = a.atid
  left join ph on ph.atid = a.atid
  left join q on q.phx = ph.phone
  left join att on att.atid = a.atid
  left join fb on fb.nm = a.nm
  left join fm on fm.atid = a.atid
$function$;

notify pgrst, 'reload schema';
