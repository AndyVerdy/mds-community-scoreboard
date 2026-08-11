-- #81 — event_who carries the facts a member needs to judge WHO to talk to.
--
-- BEFORE: the roster returned full_name + state and nothing else, so "who is the best
-- match for me?" had nothing to answer from. Olivia declined as though ranking people
-- were a policy limit ("that's not something I can judge") and then listed people by
-- country. On the real Summit roster (108, this function's own ticket_for + status
-- filter) 98 carry a live topic profile; none of it reached the lane.
--
-- FIT IS COMPUTED AT QUERY TIME against the asker's own topic profile — the pattern
-- video_search_v2 already uses for fit_reason — so the same roster reads differently
-- for different askers and there is no static match table to go stale. Proven: of 59
-- names on both Andy's and Ian's rosters, 54 carry a DIFFERENT reason.
--
-- TWO MEASUREMENTS SHAPED THIS (2026-08-11), both from rejected first drafts:
--   1. Raw topic overlap fires on EVERYONE — every attendee shares 2-5 topics with the
--      asker, so "shares your focus on X" was true of all 108 and therefore worthless.
--   2. Splitting by kind (can-help / both-know) still qualified 94 and 90 of 108.
--   The discriminator is WEIGHT RELATIVE TO THIS ROSTER: percent_rank over the event,
--   top quartile only. Self-normalising, so it works for a 12-person dinner and a
--   1,000-person summit without a tuned constant. 25 of 97 now carry a reason, and the
--   top of Andy's list is Mo Kuhail and Alex Bonilla — the latter being the member it
--   took him four turns of forcing to surface.
--
-- SCORE IS NEVER RETURNED. The model gets a REASON in words; rank, weight and
-- percentile stay inside this function (standing rule: score never shown).
CREATE OR REPLACE FUNCTION digest.event_who(p_phone text, p_event text, p_limit integer DEFAULT 60)
 RETURNS TABLE(event_name text, starts_at timestamp with time zone, full_name text, state text, is_me boolean, total_going integer, city text, niche text, channels text[], fit_reason text, shared_topics text[])
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'digest', 'pg_temp'
AS $function$
declare
  v_n int; v_atid text; v_is_20m boolean := false;
  v_event_id text; v_event_name text; v_banded boolean;
  v_me_city text; v_me_niche text; v_total int;
begin
  if nullif(trim(coalesce(p_event,'')),'') is null then return; end if;
  select case when digest.resolve_asker(p_phone) is not null then 1 else 0 end into v_n;
  if v_n <> 1 then return; end if;
  select digest.resolve_asker(p_phone) into v_atid;
  if v_atid is not null then
    select coalesce(ma.rev_band = '20M+', false), ma.city, ma.main_niche into v_is_20m, v_me_city, v_me_niche
      from digest.member_attributes ma where ma.at_member_id = v_atid;
    v_is_20m := coalesce(v_is_20m, false);
  end if;

  select c.at_record_id, coalesce(c.app_title, c.name),
         (c.name ~* '([0-9]{2,3}M[+]|centurion)')
    into v_event_id, v_event_name, v_banded
  from digest.events_catalog c
  where coalesce(c.phase,'') not in ('Tentative','Awaiting Feedback')
    and (select bool_and(c.name ilike '%'||w||'%'
                          or coalesce(c.app_title,'') ilike '%'||w||'%')
           from regexp_split_to_table(trim(p_event), '[[:space:]]+') w)
  order by (coalesce(c.app_starts_at, c.start_at) >= now()) desc,
           case c.phase when 'Registration Open' then 0 when 'Confirmed' then 1 else 2 end,
           length(c.name) asc,
           coalesce(c.app_starts_at, c.start_at) asc
  limit 1;
  if v_event_id is null then return; end if;
  if v_banded and not v_is_20m then return; end if;

  select (count(distinct r.member_at_id) filter (where r.member_at_id is not null)
          + count(*) filter (where r.member_at_id is null))::int
    into v_total
  from digest.event_registrations_live r
  where r.event_at_id = v_event_id
    and r.ticket_status = 'Confirmed'
    and r.ticket_for && array['MDS Member','MDS Member''s Business Guest','MDS Team'];

  return query
  with me as (
    select t.topic, t.sort_score, t.is_strength, t.is_working_on
      from digest.member_topic_profile(v_atid) t
  ), conf as (
    select distinct r.member_at_id
    from digest.event_registrations_live r
    where r.event_at_id = v_event_id
      and r.member_at_id is not null
      and r.ticket_status = 'Confirmed'
      and r.ticket_for && array['MDS Member','MDS Member''s Business Guest','MDS Team']
  ), ov as (
    -- strongest topic overlap per attendee, phrased by KIND: someone strong in what the
    -- asker is working on is a different (better) reason to talk than a shared interest.
    select c.member_at_id as mid,
           max(o.w) as best_w,
           (array_agg(o.topic order by o.w desc))[1:2] as top_topics,
           (array_agg(o.kind  order by o.w desc))[1]   as top_kind
    from conf c
    cross join lateral (
      select t.topic,
             (m.sort_score + t.sort_score)
               * case when m.is_working_on or t.is_working_on then 1.5 else 1.0 end as w,
             case when m.is_working_on and t.is_strength then 'can help you with'
                  when m.is_strength   and t.is_strength then 'you both know'
                  else 'shares your interest in' end as kind
      from digest.member_topic_profile(c.member_at_id) t
      join me m on m.topic = t.topic
    ) o
    group by 1
  ), ranked as (
    select ov.*, percent_rank() over (order by ov.best_w) as pr from ov
  )
  select v_event_name,
         (select coalesce(c2.app_starts_at, c2.start_at) from digest.events_catalog c2
           where c2.at_record_id = v_event_id),
         coalesce(ma.full_name, mp.full_name),
         ma.state,
         (conf.member_at_id = v_atid),
         v_total,
         ma.city,
         -- main_niche is sparse (66 of the 108 Summit roster); categories[1] is the same
         -- kind of fact and lifts coverage to 90. An attendee with no niche shown is a
         -- member the asker cannot judge, which is the defect this ticket exists to fix.
         coalesce(ma.main_niche, ma.categories[1]),
         (select array_agg(ch) from unnest(coalesce(ma.channel_mix, '{}'::text[])) ch),
         case when rk.pr >= 0.75 and rk.top_kind is not null
              then rk.top_kind || ' ' || array_to_string(rk.top_topics, ' and ') end,
         rk.top_topics
  from conf
  left join digest.member_attributes ma on ma.at_member_id = conf.member_at_id
  left join digest.member_profiles mp on mp.at_member_id = conf.member_at_id
  left join ranked rk on rk.mid = conf.member_at_id
  where coalesce(ma.full_name, mp.full_name) is not null
  order by (conf.member_at_id = v_atid) desc,
           coalesce(rk.best_w, 0) desc,
           (lower(coalesce(ma.main_niche,'')) = lower(coalesce(v_me_niche,''))) desc,
           (lower(coalesce(ma.city,'')) = lower(coalesce(v_me_city,''))) desc,
           coalesce(ma.full_name, mp.full_name)
  limit least(greatest(coalesce(p_limit, 60), 1), 60);
end $function$;

notify pgrst, 'reload schema';
