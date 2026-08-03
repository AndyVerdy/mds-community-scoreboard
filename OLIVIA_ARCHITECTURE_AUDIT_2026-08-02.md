# MDS Assistant — Architecture Audit (run against live systems, 2026-08-02)

Executes the audit specified in `MDS-Data-Architecture-Guide.md` §10 and the developer
questions in §12. **All checks read-only. Nothing was written or altered.**

Where a check could only be answered by reading code rather than data, that is stated.
**Appendix A holds the exact SQL for every number in this document** — re-run it after any
release to get a straight before/after diff rather than a fresh audit.

---

## Verdict

| | |
|---|---|
| **Architecture shape** | **Sound.** The four-layer separation is real — per-source gated RPCs assembled at query time, not one embedding blob. |
| **Scale** | **Non-issue, by a wider margin than the guide assumes.** Real growth is ~36× below the guide's worst case. |
| **Data quality** | **Better than assumed.** Graded against active members, 59% of profile fields are authoritative — not "majority bad". |
| **Retrieval** | **The real problem.** The vector index has never been used, a third of the index is noise, and recency/authority are absent. |

The failure is not where the guide predicted. Volume and schema are fine. Retrieval quality
is where the system is losing.

### Re-check after the 2026-08-03 production release

All 11 queries in Appendix A re-run. The release shipped — Olivia traffic rose ~30%
(2,378 → 3,102 messages, latest today) — but **no audit finding moved.**

| Check | 08-02 | 08-03 |
|---|---|---|
| `member_events` (event log) | 0 rows | **0 rows** |
| `content_items_embedding_hnsw` | 270 MB, **0 scans** | 275 MB, **0 scans** |
| `content_search` sort clause | `_k_terms → _k_vec → occurred_at` | **byte-identical** |
| `olivia_messages` stamped to a member | 0 / 2,378 | **0 / 3,102** |
| `event_registrations` keyed | 62% | 62% |
| `members` with `at_member_id` | 585 / 646 | 585 / 646 |
| Corpus under 30 chars | 11,998 (31%) | 12,080 (31%) |
| Empty bodies embedded | 4,300 | 4,300 |
| City spellings / rows | 908 / 1,718 | 908 / 1,718 |
| Airtable field grade | 447 / 180 / 136 | identical |
| Embedded coverage | 99.2% | **100%** ✅ |
| Gate — anon/authenticated grants | 0 | **0** ✅ |

Two genuine wins: the embedding backfill completed, and the access gate survived a large
promote with no grant leakage — the thing most likely to slip during a release.

Everything else compounded rather than held: 724 more conversations filed with no member
ID, and the unused vector index grew another 5 MB.

---

## 1. Scale projection (§10 C+D)

Growth annualised from the trailing 30 days:

| Source | Rows now | Last 30d | Projected/yr | 5-yr total |
|---|---|---|---|---|
| `content_items` (all sources) | 38,352 | 11,606 | ~139,000 | ~735,000 |
| `wa_messages` | 12,412 | 3,399 | ~41,000 | ~217,000 |
| `olivia_messages` | 2,378 | 2,378 | ~29,000 | ~145,000 |
| `fb_comments` | 13,318 | 1,474 | ~18,000 | ~95,000 |
| `fb_posts` | 3,912 | 237 | ~2,800 | ~18,000 |
| `event_registrations` | 17,786 | 221 | ~2,700 | ~31,000 |

**The guide's worst case was ~1.5M/yr for WhatsApp alone. Actual is ~41k/yr — 36× lower.**
The estimate assumed 1,000 messages per chat per week; the real figure is ~785 per week
across *all* chats combined.

At the current rate `content_items` reaches the guide's 10M "something" threshold in
roughly **70 years**. At 10× growth, ~7 years. **No table has a volume trajectory worth
planning around.**

The one exception is the source that isn't being captured at all — see §2.

---

## 2. Layer-by-layer

| Layer | Measured | Verdict |
|---|---|---|
| **Event log** | `member_events` = **0 rows** (table exists, correct shape, never written) | **FAIL** |
| **State / identity** | `at_member_id`: `member_attributes`/`member_niches`/`member_profiles` 100% · `wa_messages` 99% · `fb_activity` 94% · **`members` 585/646 = 91%** · **`event_registrations` 62%** · **`olivia_messages` 0/2,378** | **PARTIAL** |
| **Semantic** | 37,980 / 38,274 embedded = **99.2%**; catalogs 100%; 722 member-profile embeddings | **PASS (coverage)** |
| **Graph** | No `nodes`/`edges`. Implicit only: **10,266** member↔event edges, 1,327 members, 707 events | **NOT BUILT** |
| **Gate** | `digest` readable by **`service_role` only** — `anon`/`authenticated` have SELECT on **zero** tables | **PASS** |

**The event log is the irreversible one.** App behaviour — what a member opened, viewed,
clicked — is the only stream with a real volume trajectory *and* the only one being lost
daily. Everything else is recoverable from source tables.

---

## 3. Retrieval — the actual defect

### 3.1 The vector index has never been used

| Index | Size | `idx_scan` |
|---|---|---|
| `content_items_embedding_hnsw` | **270 MB** | **0** |
| `videos_catalog_embedding_hnsw` | 8.3 MB | **0** |
| `content_items_tsv_idx` | 9.3 MB | **0** |

Cause is the final line of `digest.content_search`:

```sql
order by _k_terms desc, _k_vec asc, ci.occurred_at desc, ci.id desc
```

Keyword-hit count leads; vector distance is a tiebreaker. HNSW is only reachable when the
ANN operator is the **leading** sort key, so this query shape structurally forbids the
index. Not a tuning problem. The keyword half uses `ilike '%term%'` over `concat_ws(...)`,
which cannot use the GIN index either — `search_tsv` exists, is indexed, and is never read.

**Measured plan:** sequential scan over all 38,328 rows, **5,123 ms** — and that is
*without* the vector distance, the access-rule JSONB predicates, the members join, or the
`fb_comment` correlated subquery the real function also runs.

> ⚠️ **Read the plan, not the wall time.** Re-measured 2026-08-03: **371 ms** — *identical
> plan*, same seq scan of every row, same 38,639 sub-plan executions. The only difference is
> cache state (`hit=7565 read=1238` cold vs `hit=8845 read=0` warm). Real latency swings
> **0.37 – 5.1 s** with nothing else changing. Do not conclude "it's fast now" from a warm
> run — the pass condition is `Index Scan using content_items_embedding_hnsw` appearing in
> the plan, never a millisecond figure.

This index has been pure cost: its write amplification is what took the member-profiles
sync down for three days, and it has never served a read.

### 3.2 A third of the index is noise

Chunking is **one row per message** — no topic-splitting, no conversational windows.

| Slice | Count |
|---|---|
| `wa_message/text` | 7,432 @ **24 words** avg |
| `fb_comment/comment` | 13,977 @ 23 words avg |
| **Empty body, embedded anyway** | **4,300 (11% of index)** |
| **Under 30 characters** | **11,998 (31% of index)** |

The 4,300 empty-bodied rows are WhatsApp reactions, system and `unknown` messages. They
carry vectors and compete in similarity search. `wa_digest` daily/weekly rows (581 / 1,801
chars) are the only real aggregation in the corpus.

### 3.3 Recency and authority are absent

In `content_search` the sort is keyword count → vector distance → `occurred_at`. Recency is
the **third** key, so it only separates rows already tied on the first two. The
"confident answer from two years ago" problem is unhandled.

There is **no authority term at all** — no reputation score, no domain match, nothing about
who said it. The relevancy ticket is at zero, not partially built.

---

## 4. Data quality — the Airtable triage (§9, §10 A+B)

**17 bases** (15 full access, 2 interface-only). Three untouched since 2024 — graveyard
candidates on the staleness signal alone:

| Base | Last viewed |
|---|---|
| New member flow Interface | 2024-05-08 |
| Untitled Base | 2024-08-26 |
| Softr Application Sync | 2024-09-13 |

**Field-level grade.** Computed from `member_profiles.at_fields`, the live mirror of the
member base — no Airtable API calls needed.

Graded against the **752 active member profiles** (the population that matters):

| Grade | Fields | Share |
|---|---|---|
| **Authoritative** (≥50% filled) | **447** | 59% |
| Salvageable (10–50%) | 180 | 24% |
| Graveyard (<10%) | 136 | 18% |
| **Total** | 763 | |

**This contradicts the "majority is bad" premise — in a good way.** Graded across all 5,820
mirrored profile rows it *looks* far worse (only 196 of 774 fields ≥50% filled), but that
population is diluted by non-member records. Against active members the core profile is
well-populated, and only 18% is genuinely dead.

The sprawl across bases and views may still be poor. The member profile — the thing that
actually feeds the assistant — is not.

---

## 5. Entity resolution (§6)

**Member identity is clean.** 646 members: 4 duplicate names, **0** duplicate phones,
4 duplicate emails.

**Facebook identity is not.** `fb_member_map` holds 789 rows resolving to 715 distinct
members — **74 members carry more than one FB identity.**

**Place resolution is the weak point.** **908 distinct city spellings across 1,718 rows.**
Real variants, verbatim:

- `new york | New york | New York | NEW YORK`
- `Brooklyn | BROOKLYN | Brooklyn, New York | Brooklyn, NY`
- `miami | Miami | MIAMI | Miami,FL`
- `los angeles | los Angeles | Los Angeles | LOS ANGELES`

`digest.place_city()` is the alias layer — a hardcoded `CASE` with ~11 entries. It correctly
folds `nyc`/`manhattan`/`brooklyn`/`queens` → `New York`, but **plain `new york` is not in
its list**, so the canonical target itself survives in four spellings. Three structural gaps:

1. The alias list is **code, not data** — adding a city requires a DDL migration.
2. It does not handle `"City, State"` suffixes (`Miami,FL`, `Brooklyn, NY`, `Shenzhen, China`).
3. There is **no layer-2 resolution** (embedding similarity + context) at all.

---

## 6. Developer questions answered (§12)

| # | Question | Answer |
|---|---|---|
| 1 | Which embedding model? | **Voyage `voyage-3.5-lite` only.** No OpenAI embedding model referenced anywhere in the repo. |
| 2 | Same model both ends? | **Dimensionally consistent** — all five vector columns are `vector(1024)`, matching voyage-3.5-lite. Read-time model is passed in by n8n; confirming the call site requires reading the workflow. **Only remaining code-side check.** |
| 3 | Where do vectors live? | pgvector inside Supabase, schema `digest`. |
| 4 | Cost of switching models? | Re-embed everything — 38,274 content items + 722 profiles + 2,934 catalog rows. |
| 5 | Model name in config or hardcoded? | Referenced in repo scripts; not a DB-answerable check. |
| 6 | Vector index present? | **Present and never used.** See §3.1 — this is the finding. |
| 7 | Regular indexes on filtered columns? | **Healthy.** `members` shows 44M index scans vs 88k sequential; `content_items` 35M vs 7.5k. No seq-scan-heavy table outside the `content_search` path. |
| 8 | Row count last tested at? | Not answerable from the DB. Measured now: 5,123 ms at 38k rows. |
| 9 | Index tuned for accuracy or speed? | Moot — it is never used. Built with default `m`/`ef_construction`, `vector_cosine_ops`. |

**Index hygiene overall:** 82 indexes, 6 never scanned (288 MB). Three of those six are the
ones above; the rest are trivial.

`events_catalog` (1,420), `partners_catalog` (492) and `member_profile_embeddings` (722)
have no vector index — **correct at those row counts.** That is §5's "index by usage" working
as intended, not a gap.

---

## 7. Fields vs vectors (§3) — pass

`digest.profile_texts_for_embedding()` embeds only language: expertise, About Me, main
niche, fun fact, niches, categories. **No revenue, no SKU count, no numbers.** The rule is
being followed correctly.

---

## 8. What this audit did not cover

- **Read-time embedding model call site** — needs the n8n workflow, not the DB (§12 Q2).
- **Table-by-table enumeration of all 17 Airtable bases** — audited at base level plus a
  deep field-level grade on the member base. The other 14 have not been graded.
- **The separate `mds-ai-bot` stack** (ChromaDB, not pgvector). If a second embedding model
  exists at MDS it is there — a different store entirely, which is the benign
  "separate indexes" case, but worth one confirmation.

---

## 9. Priority order

1. **`content_search` retrieval** — rewrite as retrieve-then-re-rank: wide ANN net using the
   HNSW index, then blend meaning + recency + authority. Fixes the dead index, the 5s scan,
   the absent recency, and creates the seam for the relevancy ticket. One change, four wins.
2. **Start the event log.** `member_events` is the only irreversible loss. Log changes, not
   states.
3. **Filter the corpus.** Stop embedding empty and sub-30-character bodies; that is 11% of
   the index removed for free, 31% with a threshold.
4. **Stamp `at_member_id` on ingest** — `olivia_messages` (0%), `event_registrations` (62%),
   `members` (91%).
5. **Move `place_city` aliases from code to a table** and normalise on write.
6. Graph layer — materialised edges weighted by event size. See the separate graph test:
   20 of 20 sampled members returned a 2-hop niche-matched candidate, but unweighted
   co-attendance puts up to 424 of 1,327 people one hop away and is unusable without the weight.

---

## 10. Worked ticket spec — priority 4, `olivia_messages` identity

Written out in full as the template for how the other five should be specified. Each of the
remaining priorities needs this same treatment before it is handed to anyone: exact object,
exact current state, the trap, the verify query, and the pass condition.

**Object:** `digest.olivia_messages.member` — `text`, nullable, no default.

**Current state:** 3,102 rows, **0 populated**, spanning 2026-07-17 → 2026-08-03. Every
conversation Olivia has ever had is filed against a phone number with no member attached.

**⚠️ The trap.** There is a foreign key:

```
olivia_messages_member_fkey FOREIGN KEY (member) REFERENCES digest.members(airtable_id)
```

The column expects **`members.airtable_id`**, *not* `at_member_id`. These are two different
Airtable record IDs from different bases — **0 of 646 members have them equal**
(`airtable_id` is the WhatsApp-layer record, `at_member_id` is the Members DB record).
Writing `at_member_id` into this column fails the FK. Stamp `airtable_id`; the canonical
`at_member_id` is then one join away on `digest.members`.

**Where the write lives.** **No RPC inserts this table.** Only three functions reference it
and all three read: `olivia_health_check`, `persona_signals`,
`persona_signal_fingerprints`. The insert is a direct write from n8n (prod workflow
`12wj6h1TWqb0d4Dq`) — that node is what must set `member`.

**Backfill is safe today and will not stay safe.** All 25 distinct phones resolve cleanly,
**0 unresolvable rows**. Deterministic and lossless right now; that breaks the moment a
member joins without a phone on file or changes number.

```sql
-- verify (read-only) — expect 3102 / 3102
select count(*) total, count(mm.airtable_id) resolvable
from digest.olivia_messages om
left join digest.members mm on mm.phone = om.phone;
```

**Pass condition:** `count(*) filter (where member is not null) = count(*)` on
`digest.olivia_messages`, and new rows arriving stamped without a backfill.

**Two things to check while in there:** `persona_signals` and
`persona_signal_fingerprints` consume this table and currently resolve members by phone
join — re-verify both after stamping. And **61 of 646 rows in `digest.members` have no
`at_member_id` at all**, so even once `member` is stamped those 61 members cannot reach the
canonical key. Separate gap, same area.

---

## Appendix A — the queries

All read-only. Re-run after a release and diff against the numbers above.
Baseline captured **2026-08-02**, `digest` schema, 46 tables / 116,161 rows.

**A1 · Event log + table inventory**
```sql
select count(*) digest_tables, sum(n_live_tup) total_rows,
       count(*) filter (where n_live_tup = 0) empty_tables,
       string_agg(relname, ', ' order by relname) filter (where n_live_tup = 0) which_empty
from pg_stat_user_tables where schemaname='digest';
-- baseline: 38 tables, 116,134 rows, 2 empty (member_events, olivia_billing_nudges)
```

**A2 · Identity coverage — the canonical key on every ingest path**
```sql
select 'fb_activity' t, count(*) n, count(at_member_id) keyed from digest.fb_activity
union all select 'member_niches',       count(*), count(at_member_id)   from digest.member_niches
union all select 'member_attributes',   count(*), count(at_member_id)   from digest.member_attributes
union all select 'member_profiles',     count(*), count(at_member_id)   from digest.member_profiles
union all select 'members',             count(*), count(at_member_id)   from digest.members
union all select 'event_registrations', count(*), count(member_at_id)   from digest.event_registrations
union all select 'wa_messages',         count(*), count(sender_member)  from digest.wa_messages
union all select 'olivia_messages',     count(*), count(member)         from digest.olivia_messages
union all select 'member_events',       count(*), count(member)         from digest.member_events
order by 1;
-- baseline: members 585/646 · event_registrations 11,003/17,786 · olivia_messages 0/2,378
```

**A3 · Semantic coverage**
```sql
select 'content_items' t, count(*) n, count(embedding) emb from digest.content_items
union all select 'events_catalog',            count(*), count(embedding) from digest.events_catalog
union all select 'partners_catalog',          count(*), count(embedding) from digest.partners_catalog
union all select 'videos_catalog',            count(*), count(embedding) from digest.videos_catalog
union all select 'member_profile_embeddings', count(*), count(embedding) from digest.member_profile_embeddings;
-- baseline: content_items 37,980/38,274 = 99.2%; catalogs 100%; profiles 722
```

**A4 · THE ONE THAT MATTERS — is the vector index actually used?**
```sql
select relname tbl, indexrelname idx, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) size
from pg_stat_user_indexes
where schemaname='digest' and idx_scan = 0
order by pg_relation_size(indexrelid) desc;
-- baseline: content_items_embedding_hnsw 270 MB / 0 scans
--           videos_catalog_embedding_hnsw 8.3 MB / 0 scans
--           content_items_tsv_idx 9.3 MB / 0 scans
-- PASS CONDITION after the fix: content_items_embedding_hnsw idx_scan > 0
```

**A5 · Retrieval latency — the 5-second scan**
```sql
explain (analyze, buffers)
select ci.id,
 (select count(*) from unnest(array['logistics','3pl']) t
   where concat_ws(' ', ci.tl_dr, ci.body, ci.search_extra) ilike '%'||t||'%') as k_terms
from digest.content_items ci
where ci.sensitivity <> 'never_surface'
order by k_terms desc, ci.occurred_at desc
limit 40;
-- baseline: Seq Scan, 38,328 rows, Execution Time 5,123 ms
-- also re-read the sort clause:  select pg_get_functiondef(oid) from pg_proc
--   where proname='content_search' and pronamespace='digest'::regnamespace;
```

**A6 · Corpus noise — chunking quality**
```sql
select
 count(*) filter (where coalesce(trim(body),'')='' and embedding is not null) empty_but_embedded,
 count(*) filter (where length(coalesce(body,'')) < 30 and embedding is not null) under30_embedded,
 count(*) total
from digest.content_items;
-- baseline: 4,300 empty (11%) · 11,998 under-30-char (31%) of 38,274
```

**A7 · Airtable field triage — graded against ACTIVE members only**
```sql
with act as (
  select mp.at_fields from digest.member_profiles mp
  join digest.member_attributes ma on ma.at_member_id = mp.at_member_id
  where digest.is_active_member_status(ma.membership_status)
), tot as (select count(*) n from act),
kv as (
  select key, count(*) filter (where value is not null
        and value::text <> 'null' and btrim(value::text,'"') <> '' and value::text <> '[]') filled
  from act, lateral jsonb_each(act.at_fields) group by key
)
select (select n from tot) active_profiles, count(*) fields_seen,
  count(*) filter (where filled::numeric/(select n from tot) >= 0.5)              authoritative,
  count(*) filter (where filled::numeric/(select n from tot) between 0.1 and 0.4999) salvageable,
  count(*) filter (where filled::numeric/(select n from tot) < 0.1)               graveyard
from kv;
-- baseline: 752 profiles · 763 fields · 447 authoritative / 180 salvageable / 136 graveyard
-- NB: grading across all 5,820 mirrored rows is misleading — non-member records dilute it.
```

**A8 · Entity resolution**
```sql
select
 (select count(*) from digest.members) members_total,
 (select count(*) from (select lower(trim(coalesce(full_name,name))) n from digest.members
    where coalesce(full_name,name) is not null group by 1 having count(*)>1) z) dup_names,
 (select count(*) from (select phone from digest.members where phone is not null
    group by 1 having count(*)>1) z) dup_phones,
 (select count(*) from digest.fb_member_map) fb_map_rows,
 (select count(distinct at_member_id) from digest.fb_member_map) fb_map_members,
 (select count(distinct city) from digest.member_attributes where city is not null) distinct_cities,
 (select count(*) from digest.member_attributes where city is not null) rows_with_city;
-- baseline: 646 members · 4 dup names · 0 dup phones
--           fb_member_map 789 rows → 715 members (74 with multiple FB identities)
--           908 distinct city spellings across 1,718 rows
```

**A9 · Access gate — nothing but service_role may read**
```sql
select grantee, count(distinct table_name) tables_readable
from information_schema.role_table_grants
where table_schema='digest' and privilege_type='SELECT'
  and grantee in ('anon','authenticated','service_role','PUBLIC')
group by grantee order by 2 desc;
-- baseline: service_role 39 · anon 0 · authenticated 0
-- REGRESSION ALERT: any row for anon/authenticated/PUBLIC is a finding.
```

**A10 · Growth rate → scale projection**
```sql
select 'wa_messages' src, count(*) total,
   count(*) filter (where sent_at > now()-interval '30 days') d30 from digest.wa_messages
union all select 'content_items', count(*),
   count(*) filter (where occurred_at > now()-interval '30 days') from digest.content_items
union all select 'olivia_messages', count(*),
   count(*) filter (where created_at > now()-interval '30 days') from digest.olivia_messages
union all select 'fb_comments', count(*),
   count(*) filter (where created_time > now()-interval '30 days') from digest.fb_comments;
-- baseline/30d: content_items 11,606 · wa_messages 3,399 · olivia_messages 2,378 · fb_comments 1,474
-- annualise ×12. Flag any source trending past ~800k/yr.
```

**A11 · Graph readiness (derived, nothing stored)**
```sql
with reg as (select distinct member_at_id m, event_at_id e from digest.event_registrations
             where member_at_id is not null and event_at_id is not null)
select (select count(*) from reg) member_event_edges,
       (select count(distinct m) from reg) members_in_graph,
       (select count(distinct e) from reg) events_in_graph,
       (select max(c) from (select e, count(*) c from reg group by e) z) biggest_event;
-- baseline: 10,266 edges · 1,327 members · 707 events · biggest event 409 attendees
-- The 409-attendee event is why raw co-attendance is unusable: weight edges by event size.
```
