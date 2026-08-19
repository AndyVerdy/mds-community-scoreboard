# Expertise Ledger v2 — The Living Skill Sheet (Eugene #2 finale) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every member — new, silent, or loud — carries an honest per-skill score, on a taxonomy born from real community discussion, with activity decay that never erases proven expertise.

**Architecture:** One nightly-derived table (`digest.member_expertise`) stays the single source of truth. Four scored component families: activity (kept, decayed), speaking (kept, strongest, slower decay), engagement bonus (new — FB reaction-weighted posts), forms floor (new — declared expertise from `form_answers_latest`). Taxonomy grows 16 → 18 parents + 30 subtopics (Andy-approved list, terms taken from the corpus's own labels). Consumers (who-to-meet #93, `expertise_search`) need **zero changes** — subtopics are just more `member_expertise` rows whose terms the existing mapping already reads.

**Tech Stack:** Postgres (Supabase) SQL migrations + one SECURITY DEFINER derive function · Python verification script (curl/REST like every sibling script) · leak gate.

## Global Constraints

- **CREATE OR REPLACE only for `derive_member_expertise` — NEVER DROP** (DROP discards the ACL and re-grants EXECUTE to PUBLIC; two live exposures 2026-08-12).
- **Scores, ranks, weights stay INTERNAL** (handbook §7.3) — no new REST exposure; nothing member-visible changes in this plan.
- Weights verbatim (Andy-approved): posts **2.0** · comments **0.7** · videos **3.0 (cap 5)** · biz affinity **1.5** · persona gives **1.0** · **forms 1.2 (new)** · × revenue band multiplier (1-5M 1.0 · 5-10M 1.15 · 10-20M 1.3 · 20M+ 1.5).
- Decay (Andy-approved): activity half-life **12 months**, speaking half-life **24 months**; **floor = 40% of the member's all-time peak per topic** — "proven expertise never drops to zero."
- Engagement bonus (Andy-approved): a post counts as `1 + ln(1+reactions)/4` posts (only FB posts carry reactions; 328 covered today, grows weekly).
- Taxonomy = exactly the Andy-approved list (Task 1) — including the two NEW parents Real Estate Investing and Credit Cards & Travel Hacks.
- Text→topic matching uses `phraseto_tsquery` / `expertise_topics.terms` **only** — never bare `ilike` substrings (the `'ai' in 'Em(ai)l'` revert, 2026-08-07).
- After every migration: `python3 scripts/db_export_schema.py` and commit `db/` (the #65 rule).
- Gate (`python3 scripts/olivia_leak_gate.py`) must EXIT 0 (check the exit code, never `| tail`).

---

### Task 1: Taxonomy migration — parents, subtopics, peak column

**Files:**
- Create: migration `expertise_taxonomy_v2_20260819` (via `mcp supabase apply_migration` or SQL editor)
- Modify: none
- Test: SQL assertions in Step 3

**Interfaces:**
- Produces: `digest.expertise_topics.parent text NULL` (NULL = parent/leaf topic; set = subtopic of that parent) · `digest.member_expertise.peak_score numeric NULL` · 32 new topic rows.
- Consumed by Task 2 (derive function reads all topics incl. subs) and by the existing #93 who-to-meet terms mapping (automatically).

- [ ] **Step 1: Apply the migration** (one migration, exactly this SQL):

```sql
-- Expertise Ledger v2 (Eugene #2 finale, Andy-approved 2026-08-19):
-- taxonomy 16 -> 18 parents + 30 subtopics born from the corpus's own labels,
-- and peak tracking so proven expertise can floor at 40% of its peak.
alter table digest.expertise_topics add column if not exists parent text;
alter table digest.member_expertise add column if not exists peak_score numeric;

comment on column digest.expertise_topics.parent is
  'NULL = top-level topic. Set = subtopic of that parent topic. Subtopics graduate from the quarterly evidence-density check (Andy 2026-08-19) — a subtopic exists only when real members can be ranked on it.';
comment on column digest.member_expertise.peak_score is
  'All-time peak score for this member x topic. The live score floors at 0.4 x peak — decayed activity fades rank, never erases proven expertise (Andy 2026-08-19).';

insert into digest.expertise_topics (topic, terms, parent) values
 -- NEW PARENTS (Andy: approved)
 ('Real Estate Investing',      array['real estate','rental property','syndication','str','airbnb investing'], null),
 ('Credit Cards & Travel Hacks',array['credit card','travel hack','points','miles','amex','chase sapphire'], null),
 -- AI & Automation
 ('AI tooling & agents',        array['claude','chatgpt','gpt','codex','mcp','ai agent','ai tool','cursor','openclaw'], 'AI & Automation'),
 ('Automation workflows',       array['automation','workflow','zapier','n8n','make.com'], 'AI & Automation'),
 -- Amazon FBA
 ('Listing optimization',       array['listing optimization','listing image','a+ content','bullet points','product title'], 'Amazon FBA'),
 ('SEO & keywords',             array['seo','keyword ranking','search rank','indexing'], 'Amazon FBA'),
 ('AWD / Amazon warehousing',   array['awd','amazon warehousing'], 'Amazon FBA'),
 ('FBA operations',             array['fba','fba fees','stranded inventory','ips score'], 'Amazon FBA'),
 ('Amazon US',                  array['amazon us','amazon.com','us marketplace'], 'Amazon FBA'),
 ('Amazon Canada',              array['amazon canada','amazon.ca'], 'Amazon FBA'),
 ('Amazon EU',                  array['amazon eu','amazon europe','amazon uk','amazon germany','amazon.de','amazon.co.uk'], 'Amazon FBA'),
 ('Amazon Japan',               array['amazon japan','amazon.co.jp'], 'Amazon FBA'),
 ('Amazon Australia',           array['amazon australia','amazon.com.au'], 'Amazon FBA'),
 -- Amazon PPC & Ads
 ('PPC',                        array['ppc','sponsored products','sponsored brands','acos','tacos','ad spend'], 'Amazon PPC & Ads'),
 ('Attribution',                array['attribution','amazon attribution'], 'Amazon PPC & Ads'),
 -- TikTok Shop
 ('Shop operations',            array['tiktok shop','tt shop','shop seller'], 'TikTok Shop'),
 ('GMV Max',                    array['gmv max'], 'TikTok Shop'),
 -- DTC & Shopify
 ('Shopify operations',         array['shopify','shopify store'], 'DTC & Shopify'),
 ('Subscriptions',              array['subscription','subscribe and save','recurring revenue'], 'DTC & Shopify'),
 ('Meta / social ads',          array['meta ads','facebook ads','instagram ads','social ads'], 'DTC & Shopify'),
 -- Logistics & 3PL
 ('Customs & duties',           array['customs','duty','tariff','hts code','de minimis'], 'Logistics & 3PL'),
 ('3PL warehousing',            array['3pl','warehouse','warehousing','prep center'], 'Logistics & 3PL'),
 ('Fulfillment',                array['fulfillment','last mile','shipping rates'], 'Logistics & 3PL'),
 -- Exits & M&A
 ('M&A general',                array['m&a','merger','acquisition','sell the business','exit'], 'Exits & M&A'),
 ('Aggregators',                array['aggregator','thrasio'], 'Exits & M&A'),
 ('Due diligence',              array['due diligence','loi','quality of earnings'], 'Exits & M&A'),
 -- Legal & IP
 ('Compliance',                 array['compliance','cpsc','prop 65','fda'], 'Legal & IP'),
 ('Trademarks',                 array['trademark','brand registry gating'], 'Legal & IP'),
 ('Patents',                    array['patent','utility patent','design patent'], 'Legal & IP'),
 -- Finance & Cash Flow
 ('Cash flow',                  array['cash flow','working capital','inventory financing'], 'Finance & Cash Flow'),
 ('Crypto & treasury',          array['crypto','bitcoin','stablecoin','treasury'], 'Finance & Cash Flow'),
 -- Creator & Influencer
 ('Affiliate marketing',        array['affiliate','affiliate marketing','joinbrands'], 'Creator & Influencer'),
 ('Creator outreach',           array['creator outreach','influencer outreach','creator seeding'], 'Creator & Influencer'),
 ('UGC',                        array['ugc','user generated content'], 'Creator & Influencer'),
 -- Retail & Wholesale
 ('Faire',                      array['faire'], 'Retail & Wholesale')
on conflict (topic) do nothing;
```

- [ ] **Step 2: Note the conflict target.** If `expertise_topics` has no unique constraint on `topic`, the migration fails on `on conflict` — in that case run `alter table digest.expertise_topics add constraint expertise_topics_topic_key unique (topic);` FIRST (inside the same migration), then the inserts.

- [ ] **Step 3: Assert the result:**

```sql
select
 (select count(*) from digest.expertise_topics where parent is null) as parents,   -- expect 18
 (select count(*) from digest.expertise_topics where parent is not null) as subs,  -- expect 34
 (select count(*) from digest.expertise_topics t where t.parent is not null
    and not exists (select 1 from digest.expertise_topics p where p.topic = t.parent)) as orphan_subs; -- expect 0
```
Expected: `parents=18, subs=34, orphan_subs=0`.

- [ ] **Step 4: Export the schema and commit:**

```bash
python3 scripts/db_export_schema.py
git add db/ && git commit -m "Expertise taxonomy v2: 18 parents + 34 subtopics + peak_score (Andy-approved list)"
```

---

### Task 2: `derive_member_expertise` v2 — decay, engagement bonus, forms floor, peak floor

**Files:**
- Modify: `digest.derive_member_expertise()` via migration `derive_member_expertise_v2_20260819` (**CREATE OR REPLACE — never DROP**)
- Reference: current body in `db/functions/derive_member_expertise.sql`
- Test: SQL assertions in Step 3, full recompute in Task 3

**Interfaces:**
- Consumes: `digest.expertise_topics(topic, terms, parent)` · `digest.content_items(search_tsv, occurred_at, meta, source, kind, source_id)` · `digest.fb_posts(post_id, reactions)` · `digest.videos_catalog(search_tsv, speaker_ids, app_created_at, deleted_at)` · `digest.video_speakers(user_id, email)` · `digest.member_profiles(at_fields)` · `digest.member_personas` · `digest.member_attributes(main_niche, business_model, categories, channel_mix, rev_band)` · `digest.form_answers_latest(member_at_id, value, answer_type)`
- Produces: `digest.member_expertise(at_member_id, topic, score, rank_in_topic, pct, weakness_score, evidence, peak_score, refreshed_at)` — same read shape as v1 plus `peak_score`; every consumer keeps working untouched.

- [ ] **Step 1: Read the CURRENT function first** (`db/functions/derive_member_expertise.sql`) — the v2 below keeps its structure (`term_q`, `content_hits`, `spk`, `video_agg`, `biz`, `persona_agg`, `scored`, final upsert) and changes only what is listed. Do not rewrite from memory; edit from the exported file.

- [ ] **Step 2: Apply the migration.** The five changes, exactly:

**(a) `content_hits` gains decay + engagement weights** — replace the per-item count with a weighted sum. Old rows counted; new rows weigh each item:

```sql
  content_hits as (
    select m.at_member_id, tq.topic, ci.id,
           bool_or(ci.source in ('fb_post') or ci.kind = 'post') as is_post,
           -- 12-month half-life on every conversation item
           exp( -extract(epoch from (now() - ci.occurred_at)) / (86400.0 * 365.25/12.0) / 17.312 ) as decay_w,
           -- reactions make a post count for more: 1 + ln(1+reactions)/4
           (1 + ln(1 + coalesce(fp.reactions, 0)) / 4.0) as engage_w
    from digest.content_items ci
    join digest.members m on m.airtable_id = coalesce(ci.meta->>'sender_member', ci.meta->>'member')
    left join digest.fb_posts fp on ci.source = 'fb_post' and fp.post_id = ci.source_id
    join term_q tq on ci.search_tsv @@ tq.q
    where m.at_member_id is not null
    group by m.at_member_id, tq.topic, ci.id, ci.occurred_at, fp.reactions
  ),
  content_agg as (
    select ch.at_member_id, ch.topic,
           sum(ch.decay_w * ch.engage_w) filter (where ch.is_post)     as posts,
           sum(ch.decay_w)               filter (where not ch.is_post) as comments
    from content_hits ch group by 1, 2
  ),
```
(`17.312 = 12/ln(2)` in months; the epoch expression converts age to months first. Keep the arithmetic exactly.)

**(b) `video_agg` gains slow decay** — 24-month half-life (`34.624 = 24/ln(2)`):

```sql
  video_agg as (
    select s.at_member_id, tq.topic,
           sum( exp( -extract(epoch from (now() - coalesce(v.app_created_at, now()))) / (86400.0 * 365.25/12.0) / 34.624 ) ) as vids
    from digest.videos_catalog v
    join term_q tq on v.search_tsv @@ tq.q
    join spk s on v.speaker_ids @> array[s.user_id]
    where v.deleted_at is null
    group by 1, 2
  ),
```

**(c) NEW `forms_agg` CTE** — declared expertise from the latest form answers, tsquery-matched (never ilike):

```sql
  forms_agg as (
    select fa.member_at_id as at_member_id, tq.topic, count(distinct fa.ref) as form_hits
    from digest.form_answers_latest fa
    join term_q tq on to_tsvector('english', coalesce(fa.value #>> '{}', '')) @@ tq.q
    where fa.answer_type in ('text','textarea','choice','choices')
    group by 1, 2
  ),
```

**(d) `scored` adds the forms component (1.2 weight) and the video cap moves to the weighted sum:**

```sql
      round((( 2.0 * ln(1 + coalesce(c.posts, 0))
             + 0.7 * ln(1 + coalesce(c.comments, 0))
             + 3.0 * least(coalesce(v.vids, 0), 5)
             + 1.5 * (case when b.at_member_id is not null then 1 else 0 end)
             + 1.0 * ln(1 + coalesce(p.gives, 0))
             + 1.2 * ln(1 + coalesce(f.form_hits, 0)) )
        * (case a.rev_band when '20M+' then 1.5 when '10-20M' then 1.3 when '5-10M' then 1.15 else 1.0 end))::numeric, 3) as score,
```
with `left join forms_agg f on f.at_member_id = a.at_member_id and f.topic = t.topic` added beside the existing joins, and `'form_hits', coalesce(f.form_hits, 0)` added into the `evidence` jsonb.

**(e) The final upsert applies the peak floor and updates the peak:**

```sql
  insert into digest.member_expertise
    (at_member_id, topic, score, weakness_score, evidence, refreshed_at, peak_score, rank_in_topic, pct)
  select s.at_member_id, s.topic,
         greatest(s.score, 0.4 * coalesce(me.peak_score, 0))            as score,
         s.weakness, s.evidence, now(),
         greatest(coalesce(me.peak_score, 0), s.score)                  as peak_score,
         ... (rank/pct exactly as v1 computes them, over the FLOORED score)
  from scored s
  left join digest.member_expertise me
    on me.at_member_id = s.at_member_id and me.topic = s.topic
  on conflict (at_member_id, topic) do update set ...
```
Adapt to v1's actual rank/pct mechanics (v1 computes rank/pct in a wrapper pass — keep that pass, feed it the floored score). If v1 truncates the table instead of upserting, change to upsert OR read peaks into a temp CTE before the truncate — **peaks must survive the rebuild**.

- [ ] **Step 3: Assert ACL unchanged** (the reason we never DROP):

```sql
select proacl from pg_proc p join pg_namespace n on n.oid=p.pronamespace
where n.nspname='digest' and p.proname='derive_member_expertise';
```
Expected: same value as before the migration (record it first).

- [ ] **Step 4: Export schema and commit:**

```bash
python3 scripts/db_export_schema.py
git diff db/functions/derive_member_expertise.sql   # review = the diff IS the review
git add db/ && git commit -m "derive_member_expertise v2: decay half-lives, engagement bonus, forms floor, 40%-peak floor"
```

---

### Task 3: Recompute + verification script

**Files:**
- Create: `scripts/verify_expertise_v2.py`
- Test: the script IS the test — it exits 1 on any failed assertion

**Interfaces:**
- Consumes: `digest.member_expertise` (v2 rows), REST via `SUPABASE_SECRET_KEY` from `/Users/Born/mds-digest-web/.env.local` (same env/helper pattern as `scripts/embed_member_profiles.py`).
- Produces: a printed before/after report (the ticket-close numbers) and exit code.

- [ ] **Step 1: Snapshot BEFORE numbers** (run before triggering the recompute):

```sql
select count(distinct at_member_id) as members_with_any_score,
       count(*) filter (where score >= 1) as rows_ge_1,
       count(distinct topic) as topics
from digest.member_expertise;
```
Record the three numbers in the session log — they are the "before".

- [ ] **Step 2: Trigger the recompute** the same way the nightly does (find the caller: `grep -n "derive_member_expertise" scripts/nightly_derivations.py` and run that path, or `select digest.derive_member_expertise();` if the function is the whole job).

- [ ] **Step 3: Write `scripts/verify_expertise_v2.py`** with these exact checks (docstring + REST helper copied from `embed_member_profiles.py`):

```python
CHECKS = [
  # (name, sql-ish REST assertion, expectation)
  ("topics present",       "expertise_topics count",                ">= 52"),
  ("subtopics scored",     "member_expertise rows on subtopics",    ">= 200 rows across >= 10 subtopics"),
  ("silent members gain",  "members whose ONLY components are forms/affinity now score > 0 on >= 1 topic", "> before count"),
  ("peak floor holds",     "no row where score < 0.4*peak_score - 0.001", "0 rows"),
  ("no rank regression",   "every topic with >= 5 members has contiguous rank 1..N", "true"),
  ("andy spot-check",      "Andy Verdy still ranks top-quartile Intl Expansion",     "pct >= 0.75"),
  ("speaker spot-check",   "a member with videos_spoken >= 3 outranks a same-profile member with 0 on that topic", "true"),
]
```
Implement each as a real REST query + assert; print a PASS/FAIL table; exit 1 on any FAIL.

- [ ] **Step 4: Run it:**

```bash
python3 scripts/verify_expertise_v2.py
```
Expected: all PASS. On FAIL: stop, diagnose against the v1 exported function, fix Task 2, re-run. Never proceed with a failing check.

- [ ] **Step 5: Gate + commit:**

```bash
python3 scripts/olivia_leak_gate.py; echo "EXIT=$?"   # expect EXIT=0
git add scripts/verify_expertise_v2.py && git commit -m "Expertise v2 verified: before/after + floor + spot checks"
```

---

### Task 4: Consumer probe + docs

**Files:**
- Modify: `OLIVIA_SPRINT_3.md` (ticket evidence), `OLIVIA_HANDBOOK.md` §7.1, `OLIVIA_NEXT_SESSION.md`, `SESSION_LOG_OLIVIA.md` + `SESSION_LOG.md` index line
- Test: staging probes (free tier)

**Interfaces:**
- Consumes: everything shipped above. No code changes here — this task PROVES the consumers pick the new rows up automatically.

- [ ] **Step 1: Probe who-to-meet through a subtopic** (staging, silent):

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "who should I meet at the summit? im deep into customs and tariffs"
```
Expected: named matches whose `why` includes customs/tariff terms — proving the terms of the NEW subtopic map the ask (the #93 code path reads `expertise_topics.terms`, so subs join with zero code).

- [ ] **Step 2: Probe expertise_search unchanged:**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "who knows GMV max?"
```
Expected: a real answer, no errors (the RPC's read shape did not change).

- [ ] **Step 3: Cleanup probes:** `python3 scripts/olivia_selftest.py --staging --cleanup`

- [ ] **Step 4: Update the docs** — handbook §7.1 gains: the v2 formula (weights + decay half-lives + floor verbatim from Global Constraints), the 18+34 taxonomy note and the graduation rule ("a subtopic exists only when the quarterly density check clears it"); board ticket gets the close block with the Task 3 before/after numbers; stream log entry + one index line.

- [ ] **Step 5: Commit:**

```bash
git add OLIVIA_SPRINT_3.md OLIVIA_HANDBOOK.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md
git commit -m "Expertise ledger v2 closed: living skill sheet — taxonomy, decay+floor, forms, engagement"
```

---

## Self-review (done at write time)

- Spec coverage: taxonomy (T1) · forms floor (T2c,d) · engagement bonus (T2a) · decay two half-lives (T2a,b) · 40%-peak floor (T2e) · never-DROP ACL (T2 constraint + step 3) · consumers untouched (T4) · before/after numbers (T3) — all mapped.
- Known unknowns made explicit instead of guessed: `on conflict` target existence (T1 step 2), v1's truncate-vs-upsert mechanics (T2e adaptation note), the nightly's caller (T3 step 2).
- Type consistency: `peak_score numeric`, `parent text`, `form_hits` in evidence — used identically across tasks.
