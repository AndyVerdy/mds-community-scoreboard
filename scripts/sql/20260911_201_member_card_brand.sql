-- #201 (2026-09-11) — a member is findable by the BRAND they sell under.
--
-- Andy ruled the brand into the 🟢 SHARE column on 2026-09-11: "brand is public, add it to SHARE"
-- (it is on their own listings and in their own posts). Until now no gated function selected it —
-- `grep -rl "Brand Name" db/functions/` returned nothing — so "which member owns Stylia Beauty"
-- was answered "not in what MDS has on file" while `member_profiles.at_fields->>'Brand Name'`
-- said `["Stylia"]` for Lenny Joseph. That is #190's Q5060, and the whole class behind it.
--
-- CREATE OR REPLACE with an UNCHANGED signature and RETURNS TABLE: the ACL survives
-- (reference_drop_function_revokes_acl) and nothing in n8n has to change.
--
-- Matching rule, deliberately narrow — two rules only, proven against live on 2026-09-11:
--   1. the folded query EQUALS a brand           -> 100   ("NYK1" -> Joshua Asquith)
--   2. a brand appears as WHOLE WORDS in the query -> 80 + length  ("Stylia Beauty" -> Lenny Joseph)
-- A third rule (query is a substring of a brand) was written, tested and REMOVED: the bare word
-- "beauty" matched 12 members through it. With rules 1-2 only, "beauty" matches nobody, a person's
-- name ("Ivan Ong") matches nobody, and each brand query returns exactly one member.
-- Brands arrive as a JSON array in text (`["Stylia"]`) and repeat, so attr_clean() unwraps and the
-- list is split on commas; URLs are stripped before matching so `https`/`www`/`com` can never match.

CREATE OR REPLACE FUNCTION digest.member_card(p_phone text, p_member text)
 RETURNS TABLE(full_name text, city text, state text, country text, revenue_tier text, niche text, expertise text, about_me text, hobbies text, fun_fact text, facebook_link text, chapter text, channels text[], business_model text[], categories text[], shared_chats text[], membership_state text, joined date, left_date date)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'digest', 'pg_temp'
AS $function$
declare v_n int; v_my_chats text[]; v_atid text;
begin
  if nullif(trim(coalesce(p_member,'')),'') is null then return; end if;
  select case when digest.resolve_asker(p_phone) is not null then 1 else 0 end into v_n;
  if v_n < 1 then return; end if;
  select digest.resolve_asker(p_phone) into v_atid;
  select coalesce((select array_agg(distinct c) from digest.member_identity mu, unnest(coalesce(mu.channels_present, '{}')) c where mu.at_member_id = m.at_member_id and digest.is_active_member_status(mu.membership_status)), '{}') into v_my_chats
    from digest.member_identity m where m.at_member_id = digest.resolve_asker(p_phone) and digest.is_active_member_status(m.membership_status);

  return query
  with cand as (
    select ma.*, mp.at_fields, mp.join_date, mp.full_name as mp_name, tm.channels_present as t_chats,
           concat_ws(' ', ma.full_name, mp.full_name,
                     mp.at_fields->>'Full Name', mp.at_fields->>'Profile Name',
                     mp.at_fields->>'Profile Name Cleaned',
                     mp.at_fields->>'First Name', mp.at_fields->>'Last Name') as all_names,
           -- #201: the brands this member sells under, from the three fields that carry them.
           concat_ws(', ', digest.attr_clean(mp.at_fields->>'Brand Name'),
                           mp.at_fields->>'Brand(s) URL / Name(s)',
                           digest.attr_clean(mp.at_fields->>'Storefront - Census')) as all_brands,
           coalesce(nullif(trim(mp.at_fields->>'Full Name'), ''),
                    nullif(trim(mp.full_name), ''), ma.full_name) as best_name,
           case when ma.membership_status in ('Current Member','New Member','Pending Group Entrance',
                                             'Current Member- Not Renewing','Current Member- Paused',
                                             'Current Member- Soft Removed','Staff')
                then 'current' else 'past' end as m_state
      from digest.member_attributes ma
      join digest.member_profiles mp on mp.at_member_id = ma.at_member_id
      left join lateral (select m2.channels_present from digest.members m2
                          where m2.at_member_id = ma.at_member_id limit 1) tm on true
     where ma.membership_status in (
             'Current Member','New Member','Pending Group Entrance','Current Member- Not Renewing',
             'Current Member- Paused','Current Member- Soft Removed','Staff',
             'Removed - Canceled Membership','Removed - For Cause','Removed - Replaced with other Member')
       -- #106 (Andy 2026-08-22 "make sure I'm not searchable"): an internal record is never a
       -- SUBJECT for anyone ELSE. You always keep your OWN card — the same carve-out event_who
       -- makes for the is_me row — otherwise a Staff member loses "what's on my profile".
       and (ma.at_member_id = v_atid
            or not digest.is_internal_record(ma.membership_status))
  ), ranked as (
    select c.*,
           (select bool_and(digest.name_fold(c.all_names) like '%'||digest.name_fold(w)||'%')
              from regexp_split_to_table(trim(p_member), '[[:space:]]+') w) as name_hit,
           (select max(case
                         when b = digest.name_fold(trim(p_member)) then 100
                         when digest.name_fold(trim(p_member)) like b||' %'
                           or digest.name_fold(trim(p_member)) like '% '||b
                           or digest.name_fold(trim(p_member)) like '% '||b||' %' then 80 + length(b)
                       end)
              from regexp_split_to_table(digest.name_fold(c.all_brands), '\s*,\s*') raw,
                   lateral (select trim(regexp_replace(raw, '(https?://|www\.)[^ ]*', ' ', 'g')) as b) t
             where length(t.b) >= 3) as brand_hit
      from cand c
  )
  select c.best_name, c.city, c.state,
         nullif(trim(c.country), ''),
         c.rev_band,
         digest.attr_clean(c.at_fields->>'Main Niche'),
         digest.attr_clean(c.at_fields->>'Area of Expertise'),
         digest.attr_clean(c.at_fields->>'About Me'),
         digest.attr_clean(c.at_fields->>'Hobbies'),
         digest.attr_clean(c.at_fields->>'Interesting / Fun fact'),
         case when c.at_fields->>'Facebook Profile Link' ilike '%facebook.com%'
              then c.at_fields->>'Facebook Profile Link' end,
         nullif(digest.attr_clean(c.at_fields->>'Chapter Affiliation'), 'No Chapter Affiliation'),
         (coalesce(c.channel_mix, '{}'::text[])
            || case when c.tiktok_seller then array['TikTok Shop'] else '{}'::text[] end),
         coalesce(c.business_model, '{}'::text[]),
         coalesce(c.categories, '{}'::text[]),
         (select coalesce(array_agg(x order by x), '{}')
            from (select unnest(v_my_chats) intersect
                  select unnest(coalesce(c.t_chats, '{}'))) s(x)),
         c.m_state,
         c.join_date,
         case when c.m_state = 'past'
                   and c.at_fields->>'Member Removed Date' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
              then null::date end
    from ranked c
   where c.best_name is not null
     and (c.name_hit or c.brand_hit is not null)
   order by (digest.name_fold(c.best_name) = digest.name_fold(trim(p_member))) desc,
            coalesce(c.name_hit, false) desc,
            c.brand_hit desc nulls last,
            (c.m_state = 'current') desc,
            length(c.best_name) asc
   limit 3;

  if not found then
    return query
    with cand as (
      select ma.*, mp.at_fields, mp.join_date, tm.channels_present as t_chats,
             digest.name_fold(concat_ws(' ', ma.full_name, mp.full_name,
                       mp.at_fields->>'Full Name', mp.at_fields->>'Profile Name',
                       mp.at_fields->>'Profile Name Cleaned',
                       mp.at_fields->>'First Name', mp.at_fields->>'Last Name')) as folded_names,
             coalesce(nullif(trim(mp.at_fields->>'Full Name'), ''),
                      nullif(trim(mp.full_name), ''), ma.full_name) as best_name,
             case when ma.membership_status in ('Current Member','New Member','Pending Group Entrance',
                                               'Current Member- Not Renewing','Current Member- Paused',
                                               'Current Member- Soft Removed','Staff')
                  then 'current' else 'past' end as m_state
        from digest.member_attributes ma
        join digest.member_profiles mp on mp.at_member_id = ma.at_member_id
        left join lateral (select m2.channels_present from digest.members m2
                            where m2.at_member_id = ma.at_member_id limit 1) tm on true
       where ma.membership_status in (
               'Current Member','New Member','Pending Group Entrance','Current Member- Not Renewing',
               'Current Member- Paused','Current Member- Soft Removed','Staff',
               'Removed - Canceled Membership','Removed - For Cause','Removed - Replaced with other Member')
         -- #106: same rule on the fuzzy fallback — otherwise a near-miss spelling walks straight
         -- past the exact-match guard above and returns the internal record anyway.
         and (ma.at_member_id = v_atid
              or not digest.is_internal_record(ma.membership_status))
    )
    select c.best_name, c.city, c.state,
           nullif(trim(c.country), ''),
           c.rev_band,
           digest.attr_clean(c.at_fields->>'Main Niche'),
           digest.attr_clean(c.at_fields->>'Area of Expertise'),
           digest.attr_clean(c.at_fields->>'About Me'),
           digest.attr_clean(c.at_fields->>'Hobbies'),
           digest.attr_clean(c.at_fields->>'Interesting / Fun fact'),
           case when c.at_fields->>'Facebook Profile Link' ilike '%facebook.com%'
                then c.at_fields->>'Facebook Profile Link' end,
           nullif(digest.attr_clean(c.at_fields->>'Chapter Affiliation'), 'No Chapter Affiliation'),
           (coalesce(c.channel_mix, '{}'::text[])
              || case when c.tiktok_seller then array['TikTok Shop'] else '{}'::text[] end),
           coalesce(c.business_model, '{}'::text[]),
           coalesce(c.categories, '{}'::text[]),
           (select coalesce(array_agg(x order by x), '{}')
              from (select unnest(v_my_chats) intersect
                    select unnest(coalesce(c.t_chats, '{}'))) s(x)),
           c.m_state,
           c.join_date,
           case when c.m_state = 'past'
                     and c.at_fields->>'Member Removed Date' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
                then null::date end
      from cand c
     where c.best_name is not null
       and extensions.word_similarity(digest.name_fold(trim(p_member)), c.folded_names) > 0.62
     order by extensions.word_similarity(digest.name_fold(trim(p_member)), c.folded_names) desc,
              (c.m_state = 'current') desc,
              length(c.best_name) asc
     limit 3;
  end if;
end $function$;
