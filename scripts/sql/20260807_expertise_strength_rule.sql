-- Applied to Supabase (digest schema) 2026-08-07 as migrations
--   expertise_strength_rule_relative_to_weakness
--   dossier_strength_rule_matches_topic_profile
-- Kept in git because the SQL layer otherwise lives only in the live DB (ticket #65).
--
-- A topic counted as a strength ONLY when weakness_score was exactly 0, so one "asks" hit
-- disqualified it no matter how dominant. Mo Kuhail's top topic — Logistics & 3PL, score 22.8,
-- the channel he MODERATES — was filed under "working on" against a weakness of 1.9, and his
-- dossier listed neither Logistics nor Amazon FBA (his two biggest) as strengths at all.
--
-- Strength is now relative: score >= 2 x weakness. A topic can be BOTH a strength and something
-- they are working on, which is usually the truth for whatever someone engages with most. The
-- flag is deliberately permissive — ranking by score, capped at 5 in the dossier, does the
-- discriminating. member_dossier_v2 carried its own inline copy of the rule, so it moves too or
-- the same member reads differently depending on which function answered.
--
-- After, Mo's dossier: strengths = Logistics & 3PL · Amazon FBA · International Expansion ·
-- Sourcing & Suppliers · AI & Automation; working on = Logistics & 3PL · AI & Automation ·
-- Amazon PPC & Ads · Exits & M&A.

create or replace function digest.member_topic_profile(p_atid text)
 returns table(topic text, words text[], is_strength boolean, is_working_on boolean, sort_score numeric)
 language sql
 stable
 set search_path to 'digest', 'pg_temp'
as $function$
  select e.topic,
         (select array_agg(w) from (
            select w from unnest(string_to_array(lower(regexp_replace(e.topic, '[^a-zA-Z0-9]+', ' ', 'g')), ' ')) w
            where length(w) >= 3 or w = 'ai') s) as words,
         e.score > 0 and e.score >= 2 * coalesce(e.weakness_score, 0) as is_strength,
         coalesce(e.weakness_score, 0) > 0 as is_working_on,
         greatest(coalesce(e.score, 0), coalesce(e.weakness_score, 0)) as sort_score
  from digest.member_expertise e
  where e.at_member_id = p_atid and (e.score > 0 or coalesce(e.weakness_score, 0) > 0)
$function$;

-- member_dossier_v2: the strength section's predicate only.
--   was: and e.score > 0 and coalesce(e.weakness_score, 0) = 0
--   now: and e.score > 0 and e.score >= 2 * coalesce(e.weakness_score, 0)
do $mig$
declare d text;
begin
  d := pg_get_functiondef('digest.member_dossier_v2(text)'::regprocedure);
  if position('and coalesce(e.weakness_score, 0) = 0' in d) = 0 then
    raise exception 'strength predicate not found — member_dossier_v2 changed shape, aborted';
  end if;
  d := replace(d,
    'and coalesce(e.weakness_score, 0) = 0',
    'and e.score >= 2 * coalesce(e.weakness_score, 0)');
  execute d;
end
$mig$;

notify pgrst, 'reload schema';

-- ---------------------------------------------------------------------------------------
-- NOT SHIPPED, and why: linking form answers into the expertise ledger.
--
-- Tried it (migrations expertise_ledger_reads_forms, then two corrective passes), measured it
-- across all members, reverted it. Matching topic terms against question text by substring is
-- not sound:
--   · 'ai' matches inside "Em(ai)l" and "Ret(ai)l", so AI & Automation was denied by the
--     SMS/Email Marketing row (190 members), the team-positions grid (680) and the channel
--     grid (506)
--   · International Expansion was denied by "Where do you manufacture your products? (Europe)"
--     = N/A on 453 members — manufacturing in Europe says nothing about selling there
-- Each pass fixed one case and created another, which says the heuristic is wrong rather than
-- under-tuned. The correct shape is an explicit canonical_key -> topic map — the #68 dictionary
-- applied to topics. Until that exists the ledger keeps its previous definition, and the case
-- that started this stays open: Mo Kuhail carries DTC & Shopify while his census answer is
-- "No plans to sell on".
