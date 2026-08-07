-- Applied to Supabase (digest schema) 2026-08-07 as migrations
--   20260807014950_form_answers_exploded_numeric_pii_exemption   (superseded by this file)
--   20260807015804_form_answers_exploded_type_level_pii_and_email_term
-- Kept in git because the SQL layer otherwise lives only in the live DB (ticket #65).
-- This file is the CURRENT definition of the matview.
--
-- #20 fix ②  the PII question-text heuristic dropped legitimate NUMERIC questions whose
--            wording merely contains "website" — DTC revenue share (54 answers on census
--            2026, 14 on app v3) and the MDS UX rating (53 + 723 on the legacy census).
--            A numeric answer cannot carry PII by construction, so the text heuristic now
--            applies only to non-numeric answers.
-- #20 fix ①  matrix rows now carry a composed label ("How do you handle each marketing
--            channel? (SMS/Email Marketing)"), which made one row hit the bare `email`
--            term. That term is tightened to identity phrasings in the same pass.
-- also       phone_number and url answers were reaching the stats layer through the text
--            heuristic (20 refs, including raw phone numbers and LinkedIn URLs). The answer
--            TYPE says what the value is, which beats guessing from the question wording —
--            so those types are excluded outright.

drop materialized view if exists digest.form_answers_exploded;

create materialized view digest.form_answers_exploded as
select fr.member_at_id,
       coalesce(m.canonical_key, a.key) as canonical_key,
       a.key                            as ref,
       fr.form_id,
       a.value ->> 'q'                  as question,
       a.value ->> 't'                  as answer_type,
       a.value -> 'v'                   as value,
       fr.submitted_at
from digest.form_responses fr
     cross join lateral jsonb_each(fr.answers) a(key, value)
     left join digest.form_field_map m
            on m.form_id = fr.form_id and m.ref = a.key
where fr.member_at_id is not null
  and a.key <> all (array['email','phone','full_name','brand_names'])
  and (a.value ->> 't') <> all (array['file_url','email','phone_number','url'])
  and (
        (a.value ->> 't') = 'number'
        or coalesce(a.value ->> 'q', '') !~* '(your (full )?name|your( [[:alnum:]-]+)? email|email address|birthdate|address|website|\mlink\M|social|instagram|facebook|company.?/?.?vendor|name of (your )?(brand|company|business|partner)|brand / company name|agree to|consent|confirm your information|commit to community)'
      );

create unique index form_answers_exploded_uq
  on digest.form_answers_exploded (member_at_id, form_id, ref, submitted_at);
create index form_answers_exploded_key
  on digest.form_answers_exploded (canonical_key, member_at_id, submitted_at desc);
create index form_answers_exploded_win
  on digest.form_answers_exploded (submitted_at, form_id);

revoke all on digest.form_answers_exploded from public;
grant select on digest.form_answers_exploded to service_role;

notify pgrst, 'reload schema';
