-- #82 — what a flagship event IS. Two species of event share one dossier builder: a
-- Channel Call is a TOPIC (the lift model describes it well), a Summit is a ROOM (asking
-- "what is this about" returns {} because the room mirrors the community). This table
-- holds the identity and format half, curated from the public mds.co pages.
--
-- CURATED, not scraped: two bespoke marketing pages, copy that changes rarely, and Andy's
-- #79 ruling that member-facing copy is written rather than generated. source_url and
-- refreshed_at are stored so the text can be re-checked against the page.
create table digest.event_series_profile (
  series        text primary key,
  match_pattern text not null,
  -- style='Main' is NOT a flagship flag: the Night Out, the Pre-Event Dinners, the Women's
  -- and Speaker's Lunches, "Wim Hoff Experience at MDS Inspire" and the separate Centurion
  -- Summit all carry it too. Headcount cannot separate them either (Inspire 2027 has 44
  -- confirmed and still filling, against the Pre-Event Dinner's 33). The NAME does: every
  -- side event carries a qualifier. Kept as data so it is reviewable.
  exclude_pattern text,
  what_it_is    text not null,
  format_notes  text[] not null default '{}',
  audience      text,
  source_url    text,
  refreshed_at  timestamptz not null default now()
);
revoke all on digest.event_series_profile from anon, authenticated;
