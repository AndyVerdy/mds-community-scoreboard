alter table digest.olivia_web_messages add column if not exists redactions jsonb not null default '[]'::jsonb;
alter table digest.olivia_web_messages add column if not exists source_summary jsonb not null default '{}'::jsonb;
comment on column digest.olivia_web_messages.redactions is '#169 Public Gate: [{kind: name|link|quote, detail, replaced_with}] for the GATED strip';
comment on column digest.olivia_web_messages.source_summary is '#169 evidence rows of the turn counted by source, for the source chips';
