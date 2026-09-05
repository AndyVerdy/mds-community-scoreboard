# #163 phase 1 — a truth set for the expertise ledger

**Goal:** decide whether the ledger finds the *right* people, before changing a single weight. No formula
change ships in this phase.

**Why this order (Andy, 2026-09-04):** the ledger has never been checked against anything. The verifier
tests mechanics, not accuracy, so every tuning argument today is taste. Build a ruler first, then tune.

**What we already proved (analysis in `OLIVIA_SPRINT_4.md` §#163):** the displayed number is a rank
percentile (uniform by construction: median 50, ~41% at 60+ in all 18 categories); the "strong" bar sits
at the median score; one video pays 3.0 linear points in every topic it mentions (4.6 topics average, up
to 17), which manufactures the omni-experts; 27 members are "strong" in 14-18 of 18 categories.

## Task 1 — proxy truth we already hold (SQL only, no crawling)

Two sources, both are humans naming a person for a topic:

1. **Community mentions.** A member asks "who knows X", replies name a person. `digest.content_items`
   (FB posts + comments) + `digest.fb_posts` thread structure; match member names the way
   `partner_scan.py` matches partner names (full name, then first+last within the same thread), attach
   the topic(s) of the question via `expertise_topics.terms` on the parent post.
2. **Speaker picks.** `digest.videos_catalog.speaker_ids` + the video's own topic match: MDS put this
   person on stage for this subject.

Write both into one new table (migration `expertise_truth_163`, service_role only, `create or replace`
style, never DROP):

```sql
digest.expertise_truth(
  topic text, at_member_id text, source text,           -- community_mention | speaker | web
  weight numeric, url text, occurred_at date,
  evidence jsonb, captured_at timestamptz default now(),
  primary key (topic, at_member_id, source, coalesce(url,''))
)
```

**Acceptance:** ≥ 300 rows across ≥ 12 topics; 20 rows spot-checked by hand against the source thread or
video; zero rows whose `at_member_id` does not resolve to an active member.

## Task 2 — the web test (the only source that can prove we are BLIND)

**Cohort, exactly 101 members:** the 61 who hold our 18 top-10 slots, plus a control group of 40 drawn at
random from members whose best category value is under 20. The control group is the point: if quiet
members turn out to have topic credentials, the formula measures the wrong thing.

**Method (reuse #160's pattern):** `scripts/partner_web_crawl.py` → a member variant; search brand + name;
extraction by cheap Claude Code subagents against a written spec, ~25 members each.

**Count only third-party placements** — podcast guest spots, conference sessions outside MDS, being quoted
in an article, paid teaching. **Never self-published claims**; every brand site says it does PPC, logistics
and AI, and counting those re-inflates the exact breadth problem we are fixing.

**Identity gate:** brand AND (city OR niche) must match, else discard; store `confidence` and the URL.
Old appearances decay like our own activity (24-month half-life, same as speaking).

**Acceptance:** every kept row has a URL a human can open; a 20-row hand audit finds zero wrong-person
matches; the control group is searched with the same effort as the top group (no thumb on the scale).

## Task 3 — measure, and report before touching anything

Per topic, against the truth set:

- **precision@10**: of our top 10, how many the truth set also names.
- **coverage**: of the people the truth set names for a topic, how many we place at 60+.
- **the blindness number**: how many control-group members hold a third-party placement in a topic where
  we score them under 20.

Report as a markdown table in `docs/` with the three numbers per topic and the overall. **Go/no-go on the
formula work is decided from this table, not from taste.**

## Task 4 — only then, the formula (each change measured twice)

In order of expected effect, every one re-measured against the truth set AND Millie's eval bank (the ledger
feeds her advice lanes, not just Personas):

1. Share each artifact's credit across the topics it matches; log-scale videos.
   (Simulated 2026-09-04: distinct members in the 180 top-10 slots 60 → 87; members top-10 in 5+
   categories 15 → 7; Bryce Alderson 11 → 2 while the writers hold or rise.)
2. Absolute strength in `personas_stats` instead of the rank percentile; "strong" additionally requires
   evidence beyond a form answer. Keep `member_expertise.pct` untouched — Millie tiers on it.
3. Credit topic dominance, not mention (`ts_rank` share instead of a boolean match).
4. Revisit the category-blind revenue multiplier (1.5× on Legal & IP for a 20M seller).
5. A monthly snapshot table, so "change over time" and a rising badge become possible at all.

## Constraints

- Read-only against Airtable; nothing written there, ever.
- New SQL objects: `security definer`, `search_path = digest, pg_temp`, service_role only, exported to `db/`.
- Crawled facts are public professional information, stored in Supabase, never surfaced to members.
- One branch per session; the app repo's `main` is a Render deploy.
