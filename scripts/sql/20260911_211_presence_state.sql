-- #211 Task 6: digest.member_web_presence gained a corroboration_state column in the pass-2
-- (Task 5) extraction that this table's original DDL (20260911_211_web_layer.sql) predates.
-- Additive only against a table this same plan created a few commits ago.
-- Rollback: alter table digest.member_web_presence drop column if exists corroboration_state;

alter table digest.member_web_presence add column if not exists corroboration_state text;
comment on column digest.member_web_presence.corroboration_state is
  '#211 pass-2: corroborated | no_anchor | no_match. Only corroborated rows become featured_in edges.';
