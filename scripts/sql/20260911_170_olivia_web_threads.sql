-- #170 — the running summary of one Millie web thread. Written ONLY by mds-digest-web
-- (Team + Public turns); the n8n graph never touches this table. service_role only.
create table if not exists digest.olivia_web_threads (
  thread_id          text primary key,
  asker_email        text not null,
  mode               text not null check (mode in ('team','public')),
  title              text,
  summary            text not null default '',
  summary_through_id bigint not null default 0,
  turns              int not null default 0,
  updated_at         timestamptz not null default now()
);
create index if not exists olivia_web_threads_asker_idx on digest.olivia_web_threads (asker_email, updated_at desc);
alter table digest.olivia_web_threads enable row level security;
revoke all on digest.olivia_web_threads from public, anon, authenticated;
grant select, insert, update on digest.olivia_web_threads to service_role;
comment on table digest.olivia_web_threads is
  '#170 running summary per Millie web thread (mode team|public). summary_through_id = last olivia_web_messages.id folded in. No RLS policy exists: service_role only, by design.';
