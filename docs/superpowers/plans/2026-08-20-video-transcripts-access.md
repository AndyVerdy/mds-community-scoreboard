# Video Transcripts + Real Access Gating (#101) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load the 96 AssemblyAI transcripts Zoom never covered into `content_items`, write their 96 missing summaries, and gate restricted video content on the real per-member audience lists.

**Architecture:** A new `digest.video_access` table is loaded from the GroupOS audience export (`real_match` rows only), resolving emails through `digest.resolve_member_by_email()` (#100). The transcript loader converts AssemblyAI JSON into the cue shape `zoom_transcripts.py`'s `chunk()` already consumes and writes `content_items` rows in #70's exact shape — public chunks `{"type":"public"}`, restricted chunks `{"type":"video_access","video_id":…}`. `content_search_v2` learns that one rule type; `video_search` gates its restricted treatment on the same table. Embedding rides the existing `embed_backfill.py` process.

**Tech Stack:** Postgres (Supabase `nadtudwuwjhckotrngzn`, schema `digest`), Python 3 + curl against PostgREST (house pattern), `mds-scorecard-tools/embed_backfill.py` for vectors.

## Global Constraints

- Credentials from `/Users/Born/mds-digest-web/.env.local` (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`). Never hardcode, never print.
- **`CREATE OR REPLACE`, never `DROP`** — a drop resets EXECUTE to PUBLIC. Capture each function's current definition into `scratchpad` before replacing it.
- After any migration: `python3 scripts/db_export_schema.py` → `git diff db/` → commit.
- Gate before ship: `python3 scripts/olivia_leak_gate.py` exit 0 — never piped through `tail`.
- After any RPC DDL: `notify pgrst, 'reload schema'` then hammer the REST path ×3.
- The 65 Zoom-covered videos are never touched: the loader hard-skips any `video_id` that already has `call_transcript` chunks, and AC1 checksums the pre-existing 3,116 rows.
- `panel_only` audience rows never load — filter on `real_match` non-empty, structurally.
- Emails resolve only via `digest.resolve_member_by_email()`; a raw email comparison is a plan violation.
- Transcript JSON dir: `/Users/Born/mds_transcripts/2026/` (moved from Downloads as Task 3 step 1).
- Scripts are idempotent with `--dry-run`; re-runs change zero rows.

---

## File Structure

| File | Responsibility |
|---|---|
| migration `video_access_20260820` | The `digest.video_access` table |
| `scripts/load_video_access.py` | Audience CSV → `video_access`; resolve, report, idempotent |
| migration `video_search_entitlement_20260820` | `video_search` gates restricted treatment per asker |
| migration `content_search_v2_video_access_20260820` | The one new `access_rule` type |
| `scripts/aai_transcripts.py` | AssemblyAI JSON → `chunk()` → `content_items` (the 96 only) |
| `scripts/verify_video_access.py` | #101's ACs as pass/fail checks, exit 0/1 |
| `scripts/olivia_leak_gate.py` (modify) | 4 new checks: entitled / unentitled / inactive-entitled / anon |

---

### Task 1: `digest.video_access` + loader

**Files:**
- Migration: `video_access_20260820`
- Create: `scripts/load_video_access.py`
- Create: `scripts/verify_video_access.py`

**Interfaces:**
- Produces: `digest.video_access(video_id text, at_member_id text, email text, source text, added_at timestamptz)` — `at_member_id` NULL when unresolvable; unique on `(video_id, lower(btrim(email)))`.
- Produces: `python3 scripts/load_video_access.py <pairs.csv> [--dry-run]`.

- [ ] **Step 1: Failing check** — `scripts/verify_video_access.py`, house pattern (copy the env/get/rpc helpers from `scripts/verify_member_aliases.py`, including the `Err` wrapper), first checks:

```python
va = get("video_access?select=video_id&limit=1")
check("video_access exists", isinstance(va, list), f"got {type(va).__name__}")
```

Run → FAIL (dict).

- [ ] **Step 2: Migration**

```sql
create table if not exists digest.video_access (
  video_id     text not null,
  at_member_id text,               -- NULL = grant seen, member unresolvable today
  email        text not null,
  source       text not null,      -- the rule that matched: event/user/tier/plan/tag (+ combos)
  added_at     timestamptz not null default now()
);
create unique index if not exists video_access_uq
  on digest.video_access (video_id, lower(btrim(email)));
create index if not exists video_access_member_idx
  on digest.video_access (at_member_id) where at_member_id is not null;
comment on table digest.video_access is
  '#101 Who may see each RESTRICTED GroupOS video. Loaded from the dev''s read-path mirror export
   (mds_video_audience_pairs.csv), real_match rows ONLY — panel_only rows are admin-panel phantoms
   (63 fixed test/staff subscriptions) and must never load. at_member_id via
   digest.resolve_member_by_email(); NULL = unresolvable, kept so the grant activates the day the
   alias/membership lands. Public videos are not listed (everyone sees them).';
alter table digest.video_access enable row level security;
```

- [ ] **Step 3: Loader** — `scripts/load_video_access.py`: read pairs CSV; keep rows where `real_match` non-empty; dedupe on `(video_id, email)`; resolve each distinct email once via the RPC; build rows; diff against stored `(video_id, lower(email))` pairs (same reason as #100 — the unique index is an expression, PostgREST cannot ON CONFLICT it); insert only new. Print: rows kept vs `panel_only` dropped, distinct emails, resolved / unresolved counts, per-source counts. `--dry-run` writes nothing.

- [ ] **Step 4: Run** — dry-run, then real. Expected ≈34,253 real rows → ≈33k after (video,email) dedupe; unresolved ≈11%. Then extend verify:

```python
check("real rows only", ..., "0 rows whose email is in the 63-phantom pool")   # probe 3 yopmail addresses
check("resolved share", resolved/total >= 0.85, ...)
check("rerun inserts zero", ...)                                              # run loader again, count unchanged
```

- [ ] **Step 5: Commit** — loader + verify + `db/` re-export.

---

### Task 2: `video_search` + `content_search_v2` learn entitlement

**Files:**
- Capture current defs: `pg_get_functiondef` of both → scratchpad files (rollback = paste back).
- Migrations: `video_search_entitlement_20260820`, `content_search_v2_video_access_20260820`

**Interfaces:**
- `video_search`: same signature and return TABLE. Change is internal: compute `v_entitled` = set of video_ids in `video_access` for the resolved asker; a restricted row IN that set gets the full treatment (description, cliff notes, summary, attachments) and matches on the full `search_tsv`; a restricted row NOT in it keeps today's exact safe behaviour (safe_tsv match, marker string, NULL content).
- `content_search_v2`: in the access filter where `access_rule->>'type'` is evaluated, add ONE branch: `when 'video_access' then exists (select 1 from digest.video_access va where va.video_id = ci.access_rule->>'video_id' and va.at_member_id = v_asker)`. Unknown types stay DENIED.

- [ ] **Step 1: Capture** both defs into scratchpad; note the marker string verbatim.
- [ ] **Step 2: Apply `video_search` migration.** After: `notify pgrst`; probe ×3.
- [ ] **Step 3: Apply `content_search_v2` migration.** Preserve the two burned-in traps (pure ANN top-200 branch with `enable_seqscan=off`; `set_config` not function-level SET). The edit touches ONLY the access-filter CASE.
- [ ] **Step 4: Probes** (as Andy's at_member_id, who is Staff and on the audience lists; and as a member NOT on a chosen video's list): entitled sees summary/full match; unentitled sees marker; both proven by SQL result before any load.
- [ ] **Step 5: Gate** — add the four #101 checks to `scripts/olivia_leak_gate.py` (unentitled → no restricted summary/chunk; inactive-entitled → nothing; anon → nothing; entitled+active → chunk visible). Run full gate → exit 0. Re-export `db/`, commit.

---

### Task 3: The transcript load (the 96)

**Files:**
- Create: `scripts/aai_transcripts.py`
- Modify: `scripts/verify_video_access.py` (chunk checks)

**Interfaces:**
- Consumes: `chunk()`, `hhmmss()` imported from `scripts/zoom_transcripts.py` (verbatim reuse — no copy).
- Produces: `content_items` rows, `source='call_transcript'`, `source_id='<video_id>#<n>'`, `meta.provenance='assemblyai'`.

- [ ] **Step 1: Move the JSON** — `mkdir -p /Users/Born/mds_transcripts && mv /Users/Born/Downloads/mds_transcripts_2026 /Users/Born/mds_transcripts/2026`; count 161.
- [ ] **Step 2: Baseline checksum** — store md5 over the ordered `(source_id, md5(body))` of the existing 3,116 Zoom chunks (scratchpad file); AC1 compares after.
- [ ] **Step 3: Loader** — `scripts/aai_transcripts.py [--dir …] [--apply]`:
  - skip any video_id with existing chunks (the 65) — printed, counted;
  - adapter: `utterances[] → [(start_ms/1000, end_ms/1000, 'Speaker '+speaker, text)]` then `chunk()`;
  - row shape exactly #70's, except `access_rule` per §7.2 of the spec and `search_extra` = the video's `call_type` or first tag;
  - upsert `on_conflict=source,source_id` merge-duplicates (real composite columns — PostgREST CAN infer this one, unlike the expression indexes);
  - end by calling `rpc/refresh_entity_dossiers` exactly as `zoom_transcripts.py` does.
- [ ] **Step 4: Dry-run, apply.** Expected ≈2,500–3,500 new chunks for ≈96 videos (55.2 hr at ~1 chunk/2.5 min).
- [ ] **Step 5: Embed** — run `/Users/Born/mds-scorecard-tools/embed_backfill.py`; then verify 0 unembedded `call_transcript` rows (over-30-chars rule respected).
- [ ] **Step 6: Verify + checksum** — extend `verify_video_access.py`: 96 videos with provenance-assemblyai chunks; 65 Zoom videos' checksum unchanged; access_rule/sensitivity join vs catalog = 0 mismatches; source_id collisions 0. Commit.

---

### Task 4: The 96 summaries (in-session, no metered API)

- [ ] **Step 1:** For each of the 96 (batches of ~8): read the transcript text, write the summary in #70's ruled format — one lead line + 4–5 labelled bullets, WhatsApp bold (`*label:* text`) — PATCH `videos_catalog` `{summary, summary_source:'transcript', embedding: null}` (null embedding so the nightly re-embeds the row; `search_tsv` is STORED and recomputes itself).
- [ ] **Step 2:** Verify: 161/161 2026 videos have a summary; the 65 pre-existing untouched (compare a stored checksum of their summaries taken before Step 1).
- [ ] **Step 3:** Run `/Users/Born/mds-scorecard-tools/embed_backfill.py` video leg (same call `zoom_weekly.py` makes) → 0 videos without vectors. Commit anything script-side.

---

### Task 5: Close

- [ ] Gate full run → exit 0. `db/` clean or committed.
- [ ] **The Eugene probe** — `video_search('best TikTok cold start videos')` before/after table: the Bonilla Beginners Panel (has transcript+summary) must now outrank or at least join the thin Milan title-match. Recorded in the close block honestly either way.
- [ ] Close block on the board: results, AC checklist met/not, before/after numbers (chunks 3,116→N; videos with transcripts 65→161; summaries 65→161; restricted searchable-by-entitled 0→70+6).
- [ ] Handbook: §4 videos row + §6 note on the `video_access` rule type. Spec status flipped to shipped.
- [ ] Stream log entry + one index line (session close protocol).

## Out of scope
- 2025 videos (next ticket, same machinery).
- Speaker naming (A/B/C stays); chapters.
- The ranking defect from Eugene's report beyond the probe (intent-vs-title is its own ticket if the probe still fails).
- Wiring `resolve_member_by_email` into other RPCs.
