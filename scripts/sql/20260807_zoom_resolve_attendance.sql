-- Applied to Supabase (digest schema) 2026-08-07 as migrations
--   zoom_resolve_attendance
--   zoom_resolve_attendance_tiers
--   zoom_resolve_attendance_exclude_bots
-- Filed here after a code review flagged that the most safety-critical logic in #70 existed
-- ONLY in the live database (#65's exact failure mode). This file is the current definition.
--
-- WHY THIS IS CONSERVATIVE BY DESIGN. Zoom holds no email for link-joiners — 7 of 765 distinct
-- display names carry one, always the host — so a display name is the only key there is. That
-- is precisely why attendance is STORED, NEVER SHOWN (Andy 2026-08-07): a wrong name would be
-- a wrong claim about a member. Resolution lives in zoom_name_alias rather than being baked
-- into attendance rows, so one human decision re-resolves the whole year on the next run.
--
-- Tiers:
--   bot      not a person at all — AI notetakers (Otter, Circleback, Fireflies, read.ai,
--            MeetGeek) and the host account. 138 names / 1,089 rows, excluded from the
--            resolution rate AND from anything downstream, or they would become co_attended
--            edges and member_events for people who do not exist.
--   auto     whole folded name == exactly one active member's folded full name
--   partial  first+last token match, or first name plus the last token's 4-character stem
--
-- Single-token names ("Adi", "Holly", "Matt") are NEVER auto-resolved: 232 of the 306
-- unmatched names are single words.
--
-- MEASURED, not estimated (2026-08-07): 4,348 attendance rows · 3,259 person rows ·
-- 1,670 resolved = 51.2% of person rows. 378 names remain for human review; the queue is
-- top-heavy, so clearing the top 25 reaches 66% and the top 60 reaches 75%.

create or replace function digest.zoom_resolve_attendance()
 returns jsonb
 language plpgsql
 security definer
 set search_path to 'digest', 'pg_temp'
as $function$
declare v_bot int; v_auto int; v_p1 int; v_p2 int; v_rows int;
        v_person int; v_res int;
begin
  create temp table _m on commit drop as
  select ma.at_member_id,
         regexp_replace(regexp_replace(
           lower(translate(ma.full_name,
             'ÁÀÂÄÃÅáàâäãåÉÈÊËéèêëÍÌÎÏíìîïÓÒÔÖÕóòôöõÚÙÛÜúùûüÑñÇç',
             'AAAAAAaaaaaaEEEEeeeeIIIIiiiiOOOOOoooooUUUUuuuuNnCc')),
           '[^a-z0-9 ]', ' ', 'g'), '\s+', ' ', 'g') as folded
  from digest.member_attributes ma
  where digest.is_active_member_status(ma.membership_status)
    and nullif(trim(coalesce(ma.full_name, '')), '') is not null;

  -- tier 0: not a person — AI notetakers and the host account
  insert into digest.zoom_name_alias (name_folded, at_member_id, confidence, decided_by, note)
  select distinct a.name_folded, null, 'bot', 'zoom_resolve_attendance', 'notetaker or host account'
  from digest.call_attendance a
  where a.name_folded ~* '(notetaker|note taker|circleback|fireflies|otter|fathom|timeless|companion|read ai|sembly|recorder|assistant|meeting buddy|\mai\M)'
     or a.name_folded ~* '^(contact mds|discover mds|tomi mds|belen mds)'
  on conflict (name_folded) do nothing;
  get diagnostics v_bot = row_count;

  create temp table _n on commit drop as
  select distinct a.name_folded as f from digest.call_attendance a
  where not exists (select 1 from digest.zoom_name_alias z where z.name_folded = a.name_folded);

  insert into digest.zoom_name_alias (name_folded, at_member_id, confidence, decided_by)
  select n.f, min(m.at_member_id), 'auto', 'zoom_resolve_attendance'
  from _n n join _m m on m.folded = n.f
  group by n.f having count(*) = 1
  on conflict (name_folded) do nothing;
  get diagnostics v_auto = row_count;

  insert into digest.zoom_name_alias (name_folded, at_member_id, confidence, decided_by, note)
  select n.f, min(m.at_member_id), 'partial', 'zoom_resolve_attendance', 'first+last token'
  from _n n
  join _m m on split_part(m.folded, ' ', 1) = split_part(n.f, ' ', 1)
           and split_part(m.folded, ' ', array_length(string_to_array(m.folded, ' '), 1))
             = split_part(n.f, ' ', array_length(string_to_array(n.f, ' '), 1))
  where array_length(string_to_array(n.f, ' '), 1) >= 2
    and not exists (select 1 from digest.zoom_name_alias z where z.name_folded = n.f)
  group by n.f having count(*) = 1
  on conflict (name_folded) do nothing;
  get diagnostics v_p1 = row_count;

  insert into digest.zoom_name_alias (name_folded, at_member_id, confidence, decided_by, note)
  select n.f, min(m.at_member_id), 'partial', 'zoom_resolve_attendance', 'first name + last-token stem'
  from _n n
  join _m m on m.folded like split_part(n.f, ' ', 1) || ' %'
           and length(split_part(n.f, ' ', array_length(string_to_array(n.f, ' '), 1))) >= 4
           and position(left(split_part(n.f, ' ', array_length(string_to_array(n.f, ' '), 1)), 4) in m.folded) > 0
  where array_length(string_to_array(n.f, ' '), 1) >= 2
    and not exists (select 1 from digest.zoom_name_alias z where z.name_folded = n.f)
  group by n.f having count(*) = 1
  on conflict (name_folded) do nothing;
  get diagnostics v_p2 = row_count;

  -- Only 'auto' and human decisions are stamped onto attendance rows. A 'partial' is a GUESS —
  -- it stays in the alias table as a review queue and is deliberately NOT written here, so
  -- personalization can never treat a guessed identity as a confirmed one. (Tightened after
  -- code review 2026-08-07: previously every alias was stamped regardless of confidence.)
  update digest.call_attendance a
     set at_member_id = z.at_member_id
    from digest.zoom_name_alias z
   where z.name_folded = a.name_folded
     and z.confidence in ('auto', 'human')
     and a.at_member_id is distinct from z.at_member_id;
  get diagnostics v_rows = row_count;

  -- the rate that matters is over PEOPLE, not over rows a bot generated
  select count(*), count(*) filter (where a.at_member_id is not null)
    into v_person, v_res
  from digest.call_attendance a
  left join digest.zoom_name_alias z on z.name_folded = a.name_folded
  where coalesce(z.confidence, '') <> 'bot';

  return jsonb_build_object('bot_names', v_bot, 'alias_exact', v_auto,
    'alias_first_last', v_p1, 'alias_stem', v_p2, 'rows_stamped', v_rows,
    'person_rows', v_person, 'resolved', v_res,
    'resolved_pct', round(100.0 * v_res / nullif(v_person, 0), 1));
end $function$;

-- Applied 2026-08-07 as migration videos_catalog_summary.
-- The raw transcript is for SEARCH; the summary is what a member is SHOWN when the video is
-- recommended. summary_source records which tier produced it so a description-derived blurb is
-- never mistaken for content we actually heard.
alter table digest.videos_catalog add column if not exists summary text;
alter table digest.videos_catalog add column if not exists summary_source text;

notify pgrst, 'reload schema';
