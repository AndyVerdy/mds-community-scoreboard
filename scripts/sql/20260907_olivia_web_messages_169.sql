-- scripts/sql/20260907_olivia_web_messages_169.sql
-- #169 — conversations held through the admin web door. NEVER olivia_messages:
-- that table is keyed by phone, is what the daily review reads as real member
-- conversations, and is where the probe member's WhatsApp history lives.
create table if not exists digest.olivia_web_messages (
  id            bigserial primary key,
  thread_id     text        not null,
  asker_email   text        not null,
  mode          text        not null check (mode in ('test','public','team')),
  target        text        not null check (target in ('staging','prod')),
  role          text        not null check (role in ('member','olivia')),
  text          text,
  answer_md     text,
  notes         jsonb       not null default '[]'::jsonb,
  sources       jsonb       not null default '[]'::jsonb,
  evidence_classes jsonb    not null default '{}'::jsonb,
  route         text,
  plan          jsonb,
  wamid         text,
  latency_ms    integer,
  metrics       jsonb,
  model         text,
  created_at    timestamptz not null default now()
);
comment on table digest.olivia_web_messages is
  '#169 admin web chat turns (test/public/team modes), keyed by staff email + thread. Never member WhatsApp traffic.';
create index if not exists olivia_web_messages_thread_idx on digest.olivia_web_messages (thread_id, created_at desc);
create index if not exists olivia_web_messages_asker_idx  on digest.olivia_web_messages (asker_email, created_at desc);
alter table digest.olivia_web_messages enable row level security;
revoke all on digest.olivia_web_messages from anon, authenticated;
grant select, insert on digest.olivia_web_messages to service_role;
grant usage, select on sequence digest.olivia_web_messages_id_seq to service_role;
