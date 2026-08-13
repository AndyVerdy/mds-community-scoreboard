# `digest` schema — research report (2026-08-13)

Commissioned by Andy after an external developer reviewed the Supabase schema visualizer and said
the near-total absence of declared relationships was "scary," and that changing it would be risky
but is better done now than later.

**Method.** Six parallel read-only passes over the exported SQL layer (`db/` — 107 functions, 10
views, 898 lines of table DDL, triggers, RLS, grants) plus live queries against project
`nadtudwuwjhckotrngzn`. Every number below was measured, not inferred. Where a finding came from a
sub-agent and I could not reproduce it myself, it is marked *unverified*.

---

## 1. How I understand the problem

Andy's position, as I now read it: we have many data domains — members, videos, partners, forms,
WhatsApp, Zoom, Facebook, with GroupOS documents and Circleback queued — a large amount of logic,
and almost nothing declared as connected. His examples were `member_profiles` not linked to
`member_attributes`, WhatsApp keyed to a *different* members table, and Facebook not linked to
members at all. His conclusion: "I've no clue how it's working."

**I agree with the diagnosis and I was wrong to answer it the way I first did.**

My first pass reported "zero true orphans" and framed the missing foreign keys as a documentation
gap. That was wrong in three separate ways:

1. **It measured the wrong population.** Every orphan check filtered `WHERE key IS NOT NULL`, so
   rows with no key at all were excluded from the result. Those are the majority in several tables.
2. **It skipped what it had already labelled.** I ruled `entity_dossier` "polymorphic, not
   FK-able" and never measured it. It contains 51 fabricated rows.
3. **It accepted the current shape as the constraint.** "Polymorphic keys cannot be foreign keys"
   is only true of *this* design. Four typed nullable columns with a CHECK, or four small tables,
   make them enforceable.

The external developer predicted I would defend the position. I did. The corrected finding is that
this is **not** a tidy-up job — there is live capability loss and live wrong data today.

**Where I'd refine his framing:** it is not that nothing is connected. Every domain *is* connected,
in code, inside ~107 hand-written SQL functions. What is missing is that none of it is **declared**,
so nothing verifies it and nothing draws it. The connections work until the day one of them
silently doesn't — and there is no mechanism that would tell us.

---

## 2. Root cause: two ID spaces that look identical

This single fact explains most of the rest.

| key space | rows | format | example |
|---|---:|---|---|
| `members.airtable_id` | 659 | `rec` + 14 chars | `rec07yNXtfgc1JN1j` |
| `member_profiles.at_member_id` | 5,931 | `rec` + 14 chars | `rec000kZfxAg2X7Qm` |
| **overlap between them** | **0** | — | — |

Two disjoint identifier spaces, from two different Airtable bases, that are **indistinguishable by
eye, by data type, and by regex**. Only the column they came from tells them apart.

Nothing in the database distinguishes them either. There is no domain type, no CHECK, and — for
almost every column that carries one — no foreign key. A developer reading this schema cannot tell
which key a `text` column holds without tracing the writer.

`members` is the WhatsApp/chat layer (659 rows, `airtable_id` PK, carries `at_member_id` as a
bridge column, 92% filled). `member_profiles` is the full Airtable mirror (5,931 rows) and is the
true root: `member_attributes` (5,744) is a derived subset with **0 rows** outside it. The
crosswalk between the two spaces already exists as the view `digest.member_identity` (shipped with
#77). The problem is not the absence of a bridge — it is that nothing forces anyone to use it.

---

## 3. Live defects found

### 3.1 One jsonb field holds both key types; every consumer joins on one of them

`content_items.meta->>'sender_member'`:

| source | rows | matches `members.airtable_id` | matches `at_member_id` |
|---|---:|---:|---:|
| `wa_message` | 13,450 | **13,450** | 0 |
| `fb_comment` | 14,102 | 0 | **14,075** |
| `fb_post` | 3,574 | 0 | **3,574** |

Perfectly disjoint. WhatsApp ingest writes `airtable_id`; `fb_link_content.sql:22` writes
`at_member_id`. Every consumer joins on `airtable_id`, so **17,676 Facebook rows match nothing** —
silently, with no error.

Measured consequences:

- **`member_edges` has no `thread_interaction` rows at all** — only `co_attended` (91,544),
  `same_chat` (40,329), `same_chapter` (19,887). The "who replies to whom on Facebook" graph was
  built and does not exist. *(`derive_knowledge_graph.sql:81-82`, inner join.)*
- **Expertise evidence survives on 833 of 6,801 `member_expertise` rows**, all WhatsApp. Facebook
  contributes nothing to what we believe a member is expert in. *(`derive_member_expertise.sql:29`.)*
- The authority ranking lane in `content_search_v2.sql:199-205` is a no-op for those rows.

A declared foreign key makes this class of bug unwritable. This is the strongest single argument
for the change.

### 3.2 51 of 71 chapter dossiers are fabricated entities

`refresh_entity_dossiers.sql:215` reads Airtable's `Chapter Affiliation` multi-select with `->>`,
which renders the JSON array as text; `attr_clean` strips the brackets, leaving one comma-joined
string that line :232 writes as both `entity_id` and `name`:

```
"New York Chapter, Women's Chapter"
"Asia Pacific Chapter, Women's Chapter, Chapter Leads"
```

`chapters_catalog` holds 20 real chapters. Two other functions reading the *same* field
(`chapter_info.sql:103-105`, `community_info.sql:17-20`) split it correctly with
`regexp_split_to_table` — this one branch does not.

Knock-on: **118 of 692 affiliated actives (17.1%) are multi-chapter**, so the 20 legitimate chapter
dossiers are also wrong — they aggregate single-affiliation members only.

Blast radius is currently zero: the only reader of `kind='chapter'` is
`chat_recommendations_v3`, which is dead code, and no `chats.chat_name` matches any chapter dossier
name anyway. Wrong data, not yet surfaced.

### 3.3 Rows with no key at all — the population my first pass excluded

| column | rows | no key |
|---|---:|---:|
| `call_attendance.at_member_id` | 4,348 | **2,779 (64%)** |
| `form_responses.member_at_id` | 13,644 | **8,036 (59%)** |
| `event_registrations.member_at_id` | 17,985 | **4,348 (24%)** |
| `fb_member_map.at_member_id` | 792 | 76 (10%) |
| `members.at_member_id` | 659 | 54 (8%) |
| `member_events.member` | 20,456 | **13,674 (67%)** |

`member_events` is the sharpest: its FK sits on `member` (the non-canonical key, 67% NULL) while
`at_member_id` is 100% populated and has no FK.

**Correction to my own framing of the forms number.** The 59% is not one failure — it splits:

| | rows | stamped | unstamped |
|---|---:|---:|---:|
| the 5 forms in `form_scope` | 2,396 | **2,159 (90%)** | 237 |
| the other 156 forms | 11,248 | 3,449 (31%) | 7,799 |

The forms Olivia actually reads are 90% matched. `stamp_form_responses` matches on exactly one
thing — `lower(at_fields->>'Preferred Email')`, and only when that resolves to a single member —
and is **already at fixpoint: 0 additional rows would stamp if it ran now.** Of the remainder,
2,686 have an email belonging to no member (prospects and non-members — correctly unstamped), 75
are blocked by the duplicate-email guard, and **5,275 have no email column at all** — the form
never collected an identifier, so those are unrecoverable rather than broken. Genuinely
recoverable: **242 rows** carrying a usable address in `raw->'hidden'->>'email'` that the stamper
never looks at, plus 67 reachable via other Airtable email fields.

Nothing schedules this stamping — no trigger, no cron; it runs only from
`scripts/load_forms_from_backup.py:80`.

### 3.4 17 active members are silently unreachable

They have no `member_phone_index` row, so `resolve_asker()` returns NULL and all ~40 gated
functions return zero rows — indistinguishable from "we have no data about you."

### 3.5 Personalization reads mostly test traffic

`member_events` holds **6,535 `olivia_turn` rows against 1,688 live assistant messages**. The
`olivia_messages` id sequence stands at ~32,005 with 3,377 rows live — roughly 28.6k deleted with
no cascade, leaving their events behind. **6,106 of 6,535 (93%) belong to Andy** — eval-harness
traffic. `member_dossier_v2.sql:82-89` reads exactly this table for its 90-day behaviour section.

### 3.6 The general question path runs stale versions

`multi_source_v2` calls `event_lookup_v2` and `partner_lookup` v1, so that lane misses #82's
flagship `room` and #50's partner `strength_note` — both shipped and verified through a different
entry point. *(Sub-agent finding; call sites confirmed in the exported SQL, live traffic split not
independently reproduced.)*

### 3.7 Other integrity gaps measured

- **890 of 14,889 `fb_comment` rows** key on `fb_comments.legacy_id` rather than `comment_id` —
  two id generations mixed in one column.
- **12 duplicate partner names** among 497; `partner_lookup_v2` joins the dossier by name, so
  those rows get an arbitrary dossier chosen by `refreshed_at`.
- **18 of 1,429 events carry an `app_event_id`; all 18 disagree with Airtable on start time**, 5
  on title. Every read does `coalesce(app_*, …)`, so GroupOS silently wins.
- `event_series_profile` joins by **regex** (`~*`) rather than by key.

---

## 4. What is genuinely clean

Not everything is broken, and the design should not throw these away.

- **25 relations have zero orphans** among rows that carry a key: all 18 `at_member_id` tables
  against `member_profiles`, plus `event_registrations.event_at_id`, `member_edges.a_id/b_id`,
  `wa_messages.chat_id`, `summaries.chat_id`, `fb_post_images.post_id`, `olivia_feedback.wamid`.
- **Three of four dossier kinds resolve exactly** — video 1032/1032, partner 497/497, event
  1429/1429. Only chapters are broken.
- **The vector index is now genuinely used** — 6,821 index scans on
  `content_items_embedding_hnsw`. The 2026-08-02 audit's "never used" finding is fixed by
  `content_search_v2`'s two-phase shape. 36,654 of 43,877 rows carry embeddings; all 7,223 without
  are non-text kinds.
- **The anon boundary holds.** `anon` and `authenticated` have **zero privileges** on all 58
  tables, 9 views and 1 matview. Proven live: `has_table_privilege('anon','digest.members','SELECT')`
  = false.

---

## 5. Declared structure — the numbers behind the empty diagram

| constraint | count |
|---|---:|
| primary keys | 58 / 58 tables |
| **foreign keys** | **13** (11 tables) |
| unique constraints | 6 |
| CHECK constraints | 10 (8 tables) |
| NOT NULL | 246 of 574 columns (43%) |

**36 of 58 tables have nothing beyond a primary key.** NOT NULL is thinnest exactly on the spine:
`member_profiles` 2 of 32 columns, `events_catalog` 3 of 28.

**39 tables use a single natural text primary key**, 8 of which are mutable business values that
break on an upstream rename: `chats.chat_name`, `chapters_catalog.chapter`,
`form_question_map.(form_id, question)`, `at_field_catalog.name`, `zoom_name_alias.name_folded`,
`event_series_profile.series`, `expertise_topics.topic`, `city_aliases.alias`.

**RLS is doing no work.** 26 tables have RLS enabled; **zero policies exist on any of the 58**. No
table sets FORCE ROW LEVEL SECURITY. The grant layer is the entire boundary — which currently
holds, but the RLS flags give a false impression of defence in depth.

**24 functions are EXECUTE-able by `public`.** 14 return `trigger` (not RPC-reachable through
PostgREST, though 9 of those are SECURITY DEFINER — the `DROP FUNCTION` ACL-residue pattern). **10
are directly anon-callable RPCs**, all SECURITY INVOKER pure transforms that touch no table
(`country_fold`, `en_rank`, `term_cover`, `geo_*`, `pct_from_answer`, `profile_rank`,
`state_region_states`, `country_region_countries`, `geo_country_unmatched`, `geo_state_set`). The
leak gate deliberately allows these; the exposure is real but carries no data.

**Index gaps on hot paths:** `members` shows 202,143 sequential scans / 127.5M tuples on 659 rows;
`content_items` 301.6M tuples via sequential scan. Every `text[]` join key
(`member_attributes.chapter_ids`, `events_catalog.chapter_ids`,
`videos_catalog.speaker_ids/category_ids/event_ids`) has **no GIN index anywhere**.
`videos_catalog_embedding_hnsw` (8.3 MB) has never been scanned.
`olivia_messages.member` is a foreign key with no index.

---

## 6. Where relationships live instead of the schema

Each source arrives with its own identity and is bound to `at_member_id` afterward, by three
different mechanisms — which is the readability problem stated precisely.

| lane | binding mechanism | linked |
|---|---|---:|
| video_speakers | direct column | 100% |
| WhatsApp | bridge **column** inside `members` | 92% |
| Facebook | bridge **table** (`fb_member_map`) | 90% |
| event_registrations | stamped column | 76% |
| partner_reviews | stamped column | 52% |
| form_responses | stamped column | 41% |
| Zoom call_attendance | fuzzy name match | **36%** |

Same job, three shapes, none declared. Fourteen distinct identity keys exist in total.

**Fuzzy binding sites** — where a wrong-person bug can occur: `resolve_asker` matches on the last
10 digits of a phone; `member_card` uses unanchored `LIKE` over seven concatenated name fields plus
a trigram fallback at 0.62; `zoom_resolve_attendance` falls back to first name plus a **4-character
last-name stem**, gated only by `count(*) = 1` — a unique-but-wrong match binds.

`crm_member_id` is dead — carried through one view, resolved by nothing. `app_user_id` and
`video_speakers.member_record_id` have no resolver at all.

**Fail-open error handling** compounds this. All three `member_events` triggers and all eight
health-check signals are wrapped in `exception when others then null` — a broken check reports
green. One signal is firing now: `nightly-job-stale` (`videos_refresh` 286h against a 192h cap).

---

## 6b. The forms warehouse — two maps, and a wall that is only a convention

**There is no `forms` table.** `form_id` is a bare text column across five tables with no parent:
161 distinct values in `form_responses`, 114 in `form_question_map`, 17 in `form_population`, and
**5** in `form_field_map` and `form_scope`. Ticket #73's "she reads 5 of 161" is not a coverage
backlog — it is a missing dimension table. The closest thing that exists is `form_scope` (already
keyed one row per form, and its `note` already holds the human name); the only object that knows
all 161 is `form_responses` itself, where `form_name` is denormalised across 13,644 rows and **48
of 161 forms have `form_name = form_id`** — never resolved to a real name.

**The two mapping tables are not redundant — they serve different lanes:**

| | `form_field_map` | `form_question_map` |
|---|---|---|
| key | `(form_id, ref)` | `(form_id, question)` — the question *text* |
| size | 78 rows / 5 forms | 1,314 rows / 114 forms |
| filled by | hand-curated | `rebuild_question_map()` regex |
| feeds | Olivia's member-facing reads | census/deck analytics |

Its real job is cross-generation aliasing: legacy censuses use Typeform auto-UUID refs, newer ones
author slugs, so `ttm_revenue` has to absorb `3a2bf717-…` and `number_2019revenue_fld…`. One
**can** subsume the other, but only in the `ref` direction: live, no ref carries more than one
question text, while **15 question texts span multiple refs** — so keying on the title silently
merges 15 distinct fields.

**`form_scope` is a convention repeated six times, not a chokepoint.** It is enforced by an
identical join in `form_windowed`, `form_field_history`, `my_form_answers`, `persona_signals`,
`persona_signal_fingerprints` (and `form_stats` inherits it). Three surfaces do not enforce it:

- `form_answers_exploded` (materialised view) — 149,800 rows across 57 forms, of which **35,394
  rows across 52 forms are out of scope**. The wall lives in the caller, not the object.
- `form_answers_latest` (view) — no scope join, and **zero consumers** anywhere. An unscoped,
  unused surface.
- the `member_fact` → `member_fact_num` → `member_fact_population` → `metric_lineage` chain — 15
  form_ids, only 5 in scope.

None of these are reachable by `anon` or `authenticated`, so this is an internal boundary question
rather than a live exposure. But `rebuild_question_map()` copies question *text* out of all 161
forms and only ever upserts — never deletes. Live proof it retains content whose source is gone:
four rows from form `dLxrg0RY` still carry question text naming individual people, whose responses
no longer exist.

**Fragility of the `answers` shape:** answers are an object keyed by Typeform `ref`, with the
question text snapshotted per response. Reordering questions is therefore harmless. **Renaming a
ref is fatal** — it breaks the `form_field_map` key and splits one member's history into two
canonical keys. Editing a title breaks `form_question_map` until `rebuild_question_map` reruns, and
`form_stats` displays `min(question)` — the lexicographically smallest title among every form
sharing that key.

---

## 7. What I got wrong, itemised

For the record, since the external review specifically predicted this:

| claim I made | reality |
|---|---|
| "Zero true orphans" | 51 fabricated chapter dossiers; the check excluded NULL keys, which are the majority in 3 tables |
| "`entity_dossier` is polymorphic, not FK-able" | Enforceable via typed columns + CHECK, or four tables. I never measured it |
| "The worst half of the problem is jobs on your Mac" | Wrong weighting. Those are FB-only. Andy corrected this |
| "This won't make anything faster" | Still true for FKs, but I missed that hot paths are seq-scanning 301M tuples and array joins have no GIN index |
| Framed the whole thing as documentation | It is live capability loss — the FB interaction graph does not exist |
| "59% of form submissions belong to nobody" | True as a raw count, misleading as a finding. The 5 forms Olivia actually reads are 90% matched; most of the rest never collected an identifier at all |

---

## 8. Open questions the design must settle

1. **Which key is canonical, and is it enforced?** The 2026-08-02 audit (§5.1) asked this and never
   got a ruling. The code has already voted: 59 of 107 functions use `at_member_id`, 14 use
   `airtable_id` and only 8 as a join key. Options: promote `at_member_id` to an enforced key with
   FKs, or demote it and make `airtable_id` canonical. The current split is the one indefensible
   state.
2. **Do the two `rec`-shaped spaces stay indistinguishable?** A Postgres domain type per space
   would make a wrong assignment a type error rather than a silent empty join.
3. **What happens to rows that cannot be matched?** 8,036 unstamped form responses and 2,779
   unresolved Zoom attendees are honest unknowns. A NOT NULL FK would reject them. A nullable FK
   accepts them but still forbids a *wrong* value — probably the right shape, but it needs a ruling.
4. **Is match rate a watched number?** 36%–100% across lanes today, with no alarm on any of it.
5. **Does a `forms` registry get created, and do the two mapping tables merge?** `form_id` has no
   parent table; merging is only safe in the `ref` direction (§6b). Related: should `form_scope`
   become a real chokepoint view — the `#58` treatment that fixed this exact class for events —
   rather than a join repeated in six places and skipped in three?
6. **Split logic out of Postgres, or keep it?** Andy raised this. Retrieval, gating and stats have
   a genuine reason to be in the database (set operations over 40k rows, and the security boundary
   the leak gate proves). Version routing, dead code and fail-open error handling do not.

---

## 9. Deliberately not covered

- The **n8n workflow, Make scenarios, Vercel/Render apps and launchd jobs** — that is ticket #64's
  runtime inventory, not this pass. Andy's correction stands: the launchd jobs are Facebook-only,
  one lane of many, and I over-weighted them earlier.
- **Airtable itself** — this pass audited the warehouse, not the 17 upstream bases that feed it.
- **No changes were made.** This is research. The only write this session was 31 `COMMENT ON
  COLUMN` statements (migration `digest_schema_audit_comments_20260812`), which are metadata and
  hold no lock. Several of those comments now need correcting in light of §3.
