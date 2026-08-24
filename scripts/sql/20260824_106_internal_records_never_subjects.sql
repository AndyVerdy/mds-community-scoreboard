-- 2026-08-24 · #106 — applied live via Supabase MCP execute_sql the same day (CREATE OR REPLACE
-- only, never DROP; `notify pgrst, 'reload schema'` after each). This file is the repo record of
-- what was applied, not a re-runnable migration of anything else.
--
-- TRIGGER: Eugene, 2026-08-24 00:11 — "Courtney and me come up as a suggestions for who to meet at
-- summit need to filter out the team. Look at the test chat for Ben Anderson as example." Andy:
-- "add this fix as well ... but its search logic, make sure to apply it."
--
-- REPRODUCED, not assumed: digest.olivia_recommendations rows 6690/6691 (2026-08-24 05:09:37Z,
-- lane 'event_people', asker Ben Anderson recN0ejwtEsNEGrvu) recommended Courtney Lee
-- (recsI6y9O5BnvXEiQ, Staff) and Eugene Khayman (recvSgAirIbbo9Ylb, Staff).
--
-- ROOT CAUSE: one predicate was doing two different jobs.
--   * digest.is_active_member_status() answers "may this person USE Millie?" — the ACCESS
--     question. It correctly includes 'Staff' so the team can ask, and 34 functions depend on it
--     for exactly that. It must NOT change; narrowing it would lock the whole team out of Millie.
--   * Nothing answered "may this record be SHOWN to a member?" — the SUBJECT question. Only
--     member_match_v2 and expertise_search carried a hand-copied literal allowlist that happens to
--     exclude Staff. member_card reused the ACCESS predicate on the asker and listed 'Staff' in its
--     own subject allowlist; event_who, the schedule route's who-to-meet lane and the intro
--     picker applied no status filter at all.
-- So the fix is a MISSING predicate, not a wrong one.
--
-- LIVE EXPOSURE MEASURED BEFORE THE FIX:
--   * 33 internal records (30 'Staff' + 3 'Team User') in digest.member_attributes.
--   * MDS Summit Singapore who-to-meet: 140 attendees with a member id -> 99 member-facing,
--     41 excluded, of which 5 are Staff (Courtney Lee, Doina Chilat, Eugene Khayman,
--     Fernanda Arguelles, Ion Nederita). Eugene reported 2 of the 5.
--   * 6 Staff hold CONFIRMED Summit registrations and so were eligible for event_who NAME lists
--     (Courtney Lee, Doina Chilat, Brian A. Williams, Rebe Rosas S, Ion Nederita, Belen Gallardo);
--     153 Staff-confirmed registrations exist across all events.
--   * member_card_v2 returned a FULL profile for a Staff record (Eugene Khayman: city, revenue
--     tier, niche, about-me, Facebook link, chapter, 9 shared chats) labelled membership_state
--     'current' — i.e. Andy's "make sure I'm not searchable" was not actually true anywhere.

-- 1) The missing SUBJECT predicate. btrim guards the trailing-space statuses that exist live
--    ('Declined Applicant ', 'Current Member- Paused ').
create or replace function digest.is_internal_record(p_status text)
returns boolean
language sql
immutable
set search_path to 'digest', 'pg_temp'
as $$
  select btrim(coalesce(p_status, '')) in ('Staff', 'Team User')
$$;

-- 2) digest.event_who — internal records never appear in an attendee NAME list. Two deliberate
--    carve-outs: the asker still sees their OWN row (is_me), so a Staff asker keeps the "you're on
--    the books" answer that last session's Belen fix restored; and v_total is untouched, so the
--    count stays the registration census (which counts MDS Team tickets) per the #96/#98 ruling
--    that counts are the census and names are gated. Body otherwise reproduced verbatim; the only
--    change is the added condition in the final WHERE:
--        and (conf.member_at_id = v_atid
--             or not digest.is_internal_record(ma.membership_status))

-- 3) digest.member_card — internal records are never a SUBJECT for anyone else, on BOTH the
--    exact-match CTE and the fuzzy fallback CTE (a near-miss spelling otherwise walked straight
--    past the first guard). You always keep your OWN card, mirroring event_who's is_me carve-out —
--    without it a Staff member loses "what's on my profile", which the gate asserts. Removed
--    members stay visible on purpose: that is the removed-member profile answer, a different rule.
--    member_card_v2 delegates to member_card, so it inherits the fix and now returns its
--    'not_found' shape (name echoed, every profile field null) for an internal record.
--    The only change in each CTE is:
--        and (ma.at_member_id = v_atid
--             or not digest.is_internal_record(ma.membership_status))
--    plus a new `v_atid` declared and set from digest.resolve_asker(p_phone).

-- VERIFIED LIVE AFTER THE FIX:
--   * member_card_v2 as a member asker: Eugene Khayman -> not_found, Courtney Lee -> not_found,
--     control Aaron Biner (Current Member) -> full card, membership_state 'current'.
--   * event_who as a registered member (Aaron Biner) on 'Singapore summit': 10 names, 0 internal
--     records, total_going 116 unchanged.
--   * event_who as a registered STAFF asker (Belen Gallardo): 10 rows, her own is_me row present,
--     no other Staff name, total_going 116.
--   * scripts/olivia_leak_gate.py: 297 checks, 0 failures, EXIT 0 (adds 4 #106 checks).
