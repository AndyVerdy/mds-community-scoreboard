#!/usr/bin/env python3
"""#81 — form_stats can group by gender.

"Break down the no-kids 20% by men vs women" was answered "that isn't tracked
separately in the data I have". It IS: gender sits in member_profiles.at_fields
->>'Gender' (the same source community_info already quotes for the 89/521/111
split she gave two messages earlier) and kids in form_answers_latest.num_kids,
both keyed on at_member_id. The tool simply had no gender dimension, and the
model reported a missing dimension as missing data.

Real answer, computed directly 2026-08-11: women 9 of 42 report no kids (21%),
men 111 of 379 (29%). Small-cell suppression (having count >= 3) is untouched.

CREATE OR REPLACE, no DROP: neither the signature nor the return type changes,
so the RPC never leaves the PostgREST pool.
"""
SRC = "/Users/Born/Scorecard/db/functions/form_stats.sql"

body = open(SRC).read().split("\n", 1)[1]

GENDER_EXPR = ("case when lower(coalesce(nullif(trim(mpg.at_fields->>'Gender'),''),'unspecified')) "
               "in ('male','female') then lower(trim(mpg.at_fields->>'Gender')) "
               "else 'unspecified' end")

edits = [
    # numeric-question grouping: add the profiles join the gender arm needs
    ("      left join digest.member_attributes ma on ma.at_member_id = w2.member_at_id\n",
     "      left join digest.member_attributes ma on ma.at_member_id = w2.member_at_id\n"
     "      left join digest.member_profiles mpg on mpg.at_member_id = w2.member_at_id\n"),
    # ...and the arm itself
    ("        select case p_group_by when 'country' then ma.country when 'state' then ma.state\n"
     "                               when 'niche' then ma.main_niche when 'rev_band' then ma.rev_band\n"
     "                               else 'all' end grp",
     "        select case p_group_by when 'country' then ma.country when 'state' then ma.state\n"
     "                               when 'niche' then ma.main_niche when 'rev_band' then ma.rev_band\n"
     "                               when 'gender' then " + GENDER_EXPR + "\n"
     "                               else 'all' end grp"),
]
for old, new in edits:
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:70]!r}"
    body = body.replace(old, new)

print("CREATE OR REPLACE FUNCTION " + body.split("CREATE OR REPLACE FUNCTION", 1)[1].rstrip() + ";")
print("notify pgrst, 'reload schema';")
