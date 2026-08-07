-- #70 · Zoom calls — attendance · transcripts · schedule. DDL, files-first per #65.
--
-- Andy's two rulings, 2026-08-07:
--   ① Transcripts are VECTORIZED so they drive the best video suggestions — the transcript is a
--      retrieval signal that leads a member to the right recording.
--   ② Attendance is STORED, NEVER SHOWN. It feeds member_events, co_attended edges and the
--      personalization layer; no lane, RPC or answer ever tells a member who was in a room.
--      Same shape as the standing rule that scores and ranks are internal sort keys.
--
-- Scope ruling (2026-08-06): 2026 only. No AssemblyAI backfill, no Zoom registration.

create table if not exists digest.calls (
  call_uuid          text primary key,            -- Zoom meeting UUID, stable per occurrence
  meeting_id         bigint,                      -- series id; repeats across occurrences
  topic              text,
  call_type          text,                        -- mogul | expert | channel | chapter | other
  host_email         text,
  started_at         timestamptz,
  ended_at           timestamptz,
  duration_min       int,
  participant_count  int,
  has_recording      boolean not null default false,
  has_transcript     boolean not null default false,
  is_member_facing   boolean not null default false,
  groupos_video_id   text,                        -- exact join on Zoom's GMT<date>-<time> filename
  recording_start    timestamptz,                 -- the value that filename encodes
  raw                jsonb,
  synced_at          timestamptz not null default now()
);
create index if not exists calls_started    on digest.calls (started_at desc);
create index if not exists calls_type       on digest.calls (call_type, started_at desc);
create index if not exists calls_video      on digest.calls (groupos_video_id) where groupos_video_id is not null;

comment on table digest.calls is
  '#70 One row per Zoom meeting occurrence. All 253 of 2026 are ingested, is_member_facing marks the 90 that are community calls — ingesting everything now avoids a re-pull later.';

-- Attendance is keyed on the CALL, never on the video: 8 member calls have no published
-- recording, and attendance is true whether or not anything was published.
create table if not exists digest.call_attendance (
  id            bigserial primary key,
  call_uuid     text not null references digest.calls(call_uuid) on delete cascade,
  display_name  text not null,                    -- exactly what Zoom reported
  name_folded   text not null,                    -- lowercased/stripped, the alias join key
  joined_at     timestamptz,
  left_at       timestamptz,
  seconds       int,
  at_member_id  text,                             -- resolved via zoom_name_alias, nullable
  synced_at     timestamptz not null default now(),
  unique (call_uuid, display_name, joined_at)     -- makes the loader idempotent
);
create index if not exists call_attendance_call   on digest.call_attendance (call_uuid);
create index if not exists call_attendance_member on digest.call_attendance (at_member_id) where at_member_id is not null;
create index if not exists call_attendance_folded on digest.call_attendance (name_folded);

comment on table digest.call_attendance is
  '#70 One row per join event. STORED, NEVER SHOWN (Andy 2026-08-07): feeds member_events, co_attended edges and personalization; no member-facing lane may report who attended a call. at_member_id is derived from zoom_name_alias and is re-resolvable — never treat it as the source of truth for identity.';

-- Resolution lives here and NOT baked into attendance rows, so one new alias re-resolves the
-- whole year for free. Zoom holds no email for link-joiners (7 of 765 names, always the host),
-- so display name is the only key there is — which is exactly why ② matters.
create table if not exists digest.zoom_name_alias (
  name_folded   text primary key,
  at_member_id  text,                             -- null = reviewed and genuinely not a member
  confidence    text not null default 'auto',     -- auto | partial | human
  decided_by    text,
  decided_at    timestamptz not null default now(),
  note          text
);
create index if not exists zoom_alias_member on digest.zoom_name_alias (at_member_id) where at_member_id is not null;

comment on table digest.zoom_name_alias is
  '#70 Folded Zoom display name -> member. confidence: auto (exact match), partial (needs review), human (a person decided). 67% of 2026 attendance rows resolve automatically; 306 names never match and 232 of those are single-word ("Adi", "Holly").';

revoke all on digest.calls, digest.call_attendance, digest.zoom_name_alias from public;
grant select on digest.calls, digest.call_attendance, digest.zoom_name_alias to service_role;

notify pgrst, 'reload schema';
