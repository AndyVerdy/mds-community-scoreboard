-- Applied to Supabase (digest schema) 2026-08-07 as migrations
--   form_field_map_cross_form_pass_a_exact_text
--   form_field_map_cross_form_pass_b_semantic
--   form_field_map_pass_b_fix_two_refs
-- Kept in git because the SQL layer otherwise lives only in the live DB (ticket #65).
--
-- WHY (Andy, 2026-08-07): personas must read FORMS, not just the census, and when several
-- forms carry the same field the newest answer has to win — revenue moves every year.
-- form_windowed already does latest-wins (`distinct on (member_at_id, canonical_key)
-- order by submitted_at desc`), but it can only unify fields that SHARE a canonical key.
-- Before this: 284 canonical keys across the 5 profile forms, only 22 spanning >1 form.
-- After:      247 canonical keys, 55 spanning >1 form. form_field_map 27 -> 78 rows.

-- ---------------------------------------------------------------- pass A (mechanical)
-- Two questions whose wording is byte-identical after lowercasing and stripping punctuation
-- are the same question. Target key prefers the census-2026 slug, then any readable slug over
-- a UUID/Airtable ref, then the most answers. Home-address fields (Country, City/Town,
-- State/Region, Zip) are deliberately NOT mapped — they belong in member_attributes, not in
-- the answer stats surface.
with prof as (
  select e.canonical_key, e.ref, e.form_id, e.question, e.member_at_id
  from digest.form_answers_exploded e
  join digest.form_scope s on s.form_id = e.form_id and s.scope = 'profile'
),
k as (
  select canonical_key, ref, form_id,
         regexp_replace(regexp_replace(lower(coalesce(min(question),'')),'[^a-z0-9 ]','','g'),'\s+',' ','g') as qn,
         count(distinct member_at_id) as members
  from prof group by canonical_key, ref, form_id
),
grp as (
  select qn from k
  where qn <> '' and qn not in ('country','citytown','stateregionprovince','zippost code','zippostcode')
  group by qn having count(distinct canonical_key) > 1
),
ranked as (
  select k.*, row_number() over (
    partition by k.qn
    order by (k.form_id = 'DFeK5yop') desc,
             (k.canonical_key !~ '^[0-9a-f]{8}-[0-9a-f]{4}-') desc,
             (k.canonical_key !~ '_fld[A-Za-z0-9]+$') desc,
             k.members desc) as rn
  from k join grp using (qn)
),
target as (
  select r.*, first_value(r.canonical_key) over (partition by r.qn order by r.rn) as tgt
  from ranked r
)
insert into digest.form_field_map (form_id, ref, canonical_key, note)
select t.form_id, t.ref, t.tgt, 'pass A: identical wording across forms (2026-08-07)'
from target t
where t.canonical_key <> t.tgt
on conflict (form_id, ref) do update
  set canonical_key = excluded.canonical_key, note = excluded.note;

-- ---------------------------------------------------------------- pass B (read by hand)
-- Same question, different wording. Only merged where the question, the answer axis and the
-- answer shape all match. Deliberately NOT merged, because the axis differs and blending
-- would produce an answer that is true of neither form:
--   · pay bands — census 2026 asks generic seniority (Director/Manager/Lead/Admin), the legacy
--     census asks named roles (Bookkeeper, Paid Media Buyer, Amazon Advertising Manager…)
--   · manufacturing — 2026 is one multi-select + per-country %, legacy is a choice per country
--   · selling focus — 2026 multi-select, legacy one choice per channel
--   · employees — 2026 is one combined headcount, legacy splits full-time / part-time / VA
--   · EOS — 2026 asks "and how", legacy is yes/no with implementation as a separate question
insert into digest.form_field_map (form_id, ref, canonical_key, note) values
 ('DXs5mhZn','00a265d9-b5b1-474e-95f3-652de64128b8','mkt_amazon_ads',    'pass B: == census 2026 mkt_matrix_r0 Amazon Advertising'),
 ('DFeK5yop','mkt_matrix_r0',                        'mkt_amazon_ads',    'pass B'),
 ('DXs5mhZn','8caa326c-1605-435d-88bd-9c1826a06448','mkt_google_ads',    'pass B: Google/Youtube Ads == census 2026 Google Ads'),
 ('DFeK5yop','mkt_matrix_r2',                        'mkt_google_ads',    'pass B'),
 ('DXs5mhZn','bfb81588-4aa1-42dd-bb4d-384a8336342a','mkt_email_sms',     'pass B: SMS/Email Marketing'),
 ('DFeK5yop','mkt_matrix_r4',                        'mkt_email_sms',     'pass B'),
 ('DXs5mhZn','05f07c65-20b2-44a7-8c36-02339d55d5f6','mkt_pr_influencers','pass B: PR/Influencers'),
 ('DFeK5yop','mkt_matrix_r5',                        'mkt_pr_influencers','pass B'),
 ('DXs5mhZn','2ebcfa76-53cd-4104-93c6-c3e06efd26d9','ops_bookkeeping',      'pass B: Bookkeeping'),
 ('DFeK5yop','ops_matrix_r3',                        'ops_bookkeeping',      'pass B'),
 ('DXs5mhZn','17af9975-1519-4a16-9d8f-433615aea4c1','ops_customer_service', 'pass B: Customer Service'),
 ('DFeK5yop','ops_matrix_r2',                        'ops_customer_service', 'pass B'),
 ('DXs5mhZn','ab4c3624-5db2-4333-969f-ef7c99cd05b1','ops_graphic_design',   'pass B: Graphic Design'),
 ('DFeK5yop','ops_matrix_r5',                        'ops_graphic_design',   'pass B'),
 ('DXs5mhZn','a93dd3d3-8a53-4a40-8209-67f91f9d5507','ops_product_dev',      'pass B: Product Development'),
 ('DFeK5yop','ops_matrix_r0',                        'ops_product_dev',      'pass B'),
 ('DXs5mhZn','c0497ccf-a311-4f27-81a5-7c6616c6a910','ops_product_launches', 'pass B: New Product Launches == Product Launches'),
 ('DFeK5yop','ops_matrix_r1',                        'ops_product_launches', 'pass B'),
 ('DXs5mhZn','26a207ea-7a1f-4e06-ad4d-a54cbeab3a01','ops_dev_software',     'pass B: Web Design/Software == Dev / Software'),
 ('DFeK5yop','ops_matrix_r6',                        'ops_dev_software',     'pass B'),
 ('DXs5mhZn','61d2e66b-40b9-4ba0-805e-0577cc6d5f0f','ops_marketplace_mgmt', 'pass B: Marketplace Listing Creation == Marketplace Mgmt'),
 ('DFeK5yop','ops_matrix_r4',                        'ops_marketplace_mgmt', 'pass B'),
 ('I409BFlj','2e6298b5-64ad-46a8-89fb-5929f574b39b','ux_rating',      'pass B: MDS systems UX rating, longer legacy wording'),
 ('I409BFlj','d37bd6af-0788-4f55-b33e-9a02b2f441b2','benefits_rank',  'pass B: rank member benefits'),
 ('I409BFlj','51f3def0-b3ec-4c6e-b9ef-7387fa209a89','competitive_adv','pass B: competitive advantage'),
 ('I409BFlj','06214136-a7b0-4d7d-b0e6-00e3fe549b4f','industries_20',  'pass B: time spent outside the core ecom business')
on conflict (form_id, ref) do update
  set canonical_key = excluded.canonical_key, note = excluded.note;

-- Guard worth re-running after any future mapping pass: a ref that matches no real field is
-- a silent no-op, not an error. Two pass-B rows were written from a truncated listing and
-- caught this way.
--   select count(*) from digest.form_field_map m
--   where not exists (select 1 from digest.form_responses fr
--                     where fr.form_id = m.form_id and fr.answers ? m.ref);

select digest.refresh_form_answers();
