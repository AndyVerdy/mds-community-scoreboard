#!/usr/bin/env python3
"""#82 — flagship events carry the ROOM, not a topic vector.

The event branch keeps a topic only at lift >= 1.3 over the community baseline. A Summit
draws a representative slice of MDS, so lift is ~1.0 on everything and the profile computes
to {} — the Singapore Summit's best was Sourcing & Suppliers at 1.29. Measured 2026-08-11,
that discards International Expansion (55 members), Amazon FBA (41), Walmart / DTC &
Shopify / Hiring & Team / Logistics & 3PL (38 each), Supplements (36) and more.

Lift is the right question for a Channel Call and the wrong one for a Summit. So: keep lift
untouched, and for a flagship add a `room` block built from HEADCOUNT — what a member
actually wants ("55 people working on international expansion"), and speakable without any
score. Buckets under 3 members are suppressed, matching form_stats.

A flagship is defined by the SERIES JOIN, not by style: style='Main' also marks the Night
Out, both Pre-Event Dinners, the Women's and Speaker's Lunches, "Wim Hoff Experience at MDS
Inspire" and the separate Centurion Summit. event_series_profile carries match_pattern and
exclude_pattern; the join keeps 14 real flagships and drops all 7 side events.
"""
SRC = "/Users/Born/Scorecard/db/functions/refresh_entity_dossiers.sql"

body = open(SRC).read().split("\n", 1)[1]

OLD_CTES = """  ), namehits as ("""
NEW_CTES = """  ), flagship as (
    -- a room is described by who is in it, counted, never scored
    select r.eid,
           jsonb_build_object(
             'topics', coalesce((
                select jsonb_agg(jsonb_build_object('topic', x.topic, 'members', x.n)
                                 order by x.n desc)
                from (select e.topic, count(distinct r2.mid) n
                        from reg r2 join digest.member_expertise e on e.at_member_id = r2.mid
                       where r2.eid = r.eid and coalesce(e.weakness_score,0) = 0 and e.score > 0
                       group by e.topic having count(distinct r2.mid) >= 3
                       order by count(distinct r2.mid) desc limit 8) x), '[]'::jsonb),
             -- categories, not main_niche: main_niche is sparse AND mixing the two taxonomies
             -- produced nonsense (Supplements 3 / supplements 3 / Health-Beauty-Supplements 4
             -- as separate rows in a 117-person room). The fold strips punctuation, spacing and
             -- the word "and", merging "Housewares/ Office/ & Pet Products" with
             -- "Housewares/Office/Pet Products": 27 + 9 becomes the true 36.
             'niches', coalesce((
                select jsonb_agg(jsonb_build_object('niche', y.label, 'members', y.n)
                                 order by y.n desc)
                from (select (array_agg(cc.label order by length(cc.label)))[1] label,
                             count(distinct cc.mid) n
                        from (select r3.mid,
                                     regexp_replace(lower(trim(cat)), '[^a-z0-9]|and', '', 'g') key,
                                     trim(cat) label
                                from reg r3
                                join digest.member_attributes ma on ma.at_member_id = r3.mid
                                cross join lateral unnest(coalesce(ma.categories,'{}'::text[])) cat
                               where r3.eid = r.eid and nullif(trim(cat),'') is not null) cc
                       group by cc.key having count(distinct cc.mid) >= 3
                       order by count(distinct cc.mid) desc limit 6) y), '[]'::jsonb),
             'rev_bands', coalesce((
                select jsonb_object_agg(z.band, z.n)
                from (select ma.rev_band band, count(*) n
                        from reg r4 join digest.member_attributes ma on ma.at_member_id = r4.mid
                       where r4.eid = r.eid and ma.rev_band is not null
                       group by 1 having count(*) >= 3) z), '{}'::jsonb),
             'countries', coalesce((
                select jsonb_agg(jsonb_build_object('country', q.country, 'members', q.n)
                                 order by q.n desc)
                -- country_fold merges the ISO-2/full-name dual coding: US 29 + United States 23
                -- were two rows for one country until this, and chapter_info already folds them.
                from (select initcap(digest.country_fold(ma.country)) country, count(*) n
                        from reg r5 join digest.member_attributes ma on ma.at_member_id = r5.mid
                       where r5.eid = r.eid and ma.country is not null
                         and digest.country_fold(ma.country) is not null
                       group by 1 having count(*) >= 3
                       order by count(*) desc limit 6) q), '[]'::jsonb)
           ) room
    from (select distinct eid from reg) r
    join digest.events_catalog c2 on c2.at_record_id = r.eid
    join digest.event_series_profile sp
      on coalesce(c2.app_title, c2.name) ~* sp.match_pattern
     and coalesce(c2.app_title, c2.name) !~* coalesce(sp.exclude_pattern, '$^')
  ), namehits as ("""

OLD_RECEPTION = """         jsonb_build_object('member_registrations', coalesce(d.regs,0),
                            'audience', case when coalesce(d.regs,0) > 150 then 'flagship - draws the whole community, no topic skew'
                                             when ap.tp is not null then 'selective room - topics are lift over the community baseline'
                                             end),"""
NEW_RECEPTION = """         jsonb_build_object('member_registrations', coalesce(d.regs,0),
                            'audience', case when fl.room is not null then 'flagship - a room, not a topic: describe who is in it, never what it is about'
                                             when coalesce(d.regs,0) > 150 then 'flagship - draws the whole community, no topic skew'
                                             when ap.tp is not null then 'selective room - topics are lift over the community baseline'
                                             end)
           || case when fl.room is not null then jsonb_build_object('room', fl.room) else '{}'::jsonb end,"""

OLD_JOIN = """  from ev e3 left join attprof ap on ap.eid = e3.eid"""
NEW_JOIN = """  from ev e3 left join attprof ap on ap.eid = e3.eid
  left join flagship fl on fl.eid = e3.eid"""

for old, new in ((OLD_CTES, NEW_CTES), (OLD_RECEPTION, NEW_RECEPTION), (OLD_JOIN, NEW_JOIN)):
    if new in body:
        continue
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:70]!r}"
    body = body.replace(old, new)

print("CREATE OR REPLACE FUNCTION " + body.split("CREATE OR REPLACE FUNCTION", 1)[1].rstrip() + ";")
print("notify pgrst, 'reload schema';")
