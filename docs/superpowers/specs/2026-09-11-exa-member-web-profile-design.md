# #211 · Exa web profiles for members and partners — design

**Status:** design, not approved for build
**Date:** 2026-09-11
**Session:** the Exa.ai session (parallel to the #170 memory session)
**Branch:** `211-exa-web-profile-20260911`

---

## Story

*As a member asking Millie about another member or a partner, I get facts that are true today and
carry their source, because the profile behind them was checked against that person's own public
page instead of left empty or guessed.*

## Why this ticket exists

Three findings from the 2026-09-11 probe, all measured live, none from docs.

**1. Millie states unevidenced facts about members.** Michael Goldsmith (`rec5k8tMRPgD0jr2h`) has a
persona whose `summary` reads "Miami-based e-commerce founder" while its own evidence block says
"No self-reported or behavioral signals on product, model, or stage" and `what_they_sell:
"Unknown—no signals"`. His entire internal signal is four event registrations between 2018 and 2020.
"Miami" is an event city. "Founder" has no source at all. His own LinkedIn, whose URL we already
hold in Airtable, says Los Angeles Metro and Sales Manager / Product Development at Lone Star
Merchandising Group since February 2015. Handbook rule 5 says a member must never be told something
untrue about another member. This is that, today, in production.

**2. Proficiency is mostly self-report counted twice.** Evidence keys across all 17,868
`member_expertise` rows:

| key | rows | what it is |
| --- | --- | --- |
| `band_multiplier` | 17,868 | a scoring rule, not evidence |
| `persona_gives_hits` | 10,676 | derived from the persona, which Haiku wrote from the census form |
| `form_hits` | 7,424 | the census form |
| `persona_asks_hits` | 4,794 | same persona |
| `peak_floor_applied` | 2,377 | a scoring rule, not evidence |
| `biz_affinity` | 2,131 | derived |
| `comments` | 2,058 | observed behaviour |
| `videos_spoken` | 1,821 | observed behaviour |
| `posts` | **0** | weighted 2.0 and never populated (#163 finding, still open) |

Observed behaviour is 3,879 of the evidence rows. Public evidence is absent entirely. A member who
never filled the form but hosts a podcast, speaks at conferences and runs a 50-person company ranks
near zero.

**3. The partner `people` gap is measured and already caused a failure.** `digest.partner_web_profile`
holds 506 rows: 405 crawled ok, 71 unreachable, 29 empty, 1 with no website. `people` is empty on 281
of 506, and on 180 of the 405 that crawled successfully, because founders are on LinkedIn and not on
a marketing site. This is what made exam question #5068 ("Tell me about hector the ppc tool") credit
a partner to a person the evidence does not support.

## What Exa is, and why it is the right source

Exa sells search, but the part that matters here is a structured company and people layer built
largely from LinkedIn. A company result carries key executives with titles, headcount, headquarters,
founding year, industry, tech stack and recent public posts as fields, not as prose to be scraped.

This is the complement to #160, not a replacement. #160 crawls a partner's own website and extracts
with Sonnet, which can only ever learn what that site publishes and only when we already know the
URL. Exa needs no URL and reaches the pages a marketing site never contains.

**Measured coverage, three live probes on 2026-09-11:**

| probe | our data | Exa result |
| --- | --- | --- |
| Hector (`679a26b601681a357fc083cc`) | `people: []` | four named executives including a founder |
| StoreClaw (`6a1d6831c1394707852ef3f6`) | `people: []` | company found, **no executives** — a miss |
| Casey Ames (member, known answer) | brand `["Harkla"]` | exact match, plus title, city, headcount, a second brand we do not hold, two colleagues |
| Michael Goldsmith (member, empty persona) | all persona arrays empty | full current role, employer, location, 15-year history, skills |
| Matthew Greene (member, 40 expertise rows) | brand on file, ranked #2 in two topics | confirms title and company, adds headcount, HQ, industry, China presence, an Amazon feature |

**The pattern: Exa's value is inverse to how much we already know.** It barely moves a rich member
and rebuilds a poor one. That is the argument for scoping it at the members we know least about.

## Cost

Pay-as-you-go, no subscription, taken from Exa's own pricing page on 2026-09-11.

| endpoint | price | our use |
| --- | --- | --- |
| Contents | $1 / 1k pages | read a LinkedIn or brand URL we already hold |
| Search | $7 / 1k requests | find the member or partner when we hold no URL |
| Monitors | $15 / 1k requests | scheduled watch for new web events (not in phase 1) |

One full pass over 733 active members plus 506 partners is roughly $3 to $5. Weekly autopilot is
about $250 a year. Cost is not the constraint. Identity is.

## Identity, and the phase split

The wrong-person risk is the whole risk. It is removed entirely when we read a URL the member
themselves gave us.

| cohort | count | how identity is anchored | phase |
| --- | --- | --- | --- |
| actives with a real LinkedIn URL in Airtable | 464 | their own URL, zero ambiguity | 1 |
| actives with no company anchor **and** a LinkedIn URL | 96 (subset of the 464) | their own URL | 1, highest value |
| actives with no LinkedIn URL | 269 | name plus brand, ambiguous | 2 |
| actives with no company anchor **and** no LinkedIn URL | 64 | name only, most ambiguous | 2 |
| partners with a resolved URL | 405 | the site, then the company record | 1 |
| partners with no reachable site | 101 | name, ambiguous | 2 |

**Phase 2 does not ship on this ticket.** It needs a confidence gate and its own acceptance criteria,
because a name-only lookup is exactly the shape that produced #5068.

## Data layer

### New table: `digest.member_web_profile`

Additive. Nothing in `member_profiles`, `at_fields`, `member_personas` or `member_expertise` is ever
updated by this pipeline. Mirrors the column pattern of `partner_web_profile`, which has been live
since 2026-09-03.

| column | type | notes |
| --- | --- | --- |
| `at_member_id` | text | |
| `source_url` | text | the exact URL read; required |
| `source_kind` | text | `linkedin` \| `company_site` \| `search` |
| `fetch_status` | text | `ok` \| `unreachable` \| `empty` \| `no_source` |
| `fetched_at` | timestamptz | |
| `role` | text | |
| `company` | text | |
| `company_url` | text | |
| `location` | text | |
| `headcount` | text | banded as Exa returns it, never a false precision |
| `industry` | text | |
| `prior_roles` | jsonb | |
| `public_activity` | jsonb | features, talks, podcasts, posts, each with its own URL |
| `raw` | jsonb | the unmodified Exa payload |
| `source_hash` | text | change detection; unchanged pages cost nothing and rewrite nothing |
| `model` | text | the extracting model |
| `confidence` | numeric | 1.0 for a member-supplied URL, lower for a resolved one |
| `updated_at` | timestamptz | |

**Append-only.** Each fetch inserts a new row stamped `fetched_at`. Current state is a view over the
latest row per member. The table never overwrites its own history, the same way
`member_personas_history` already works.

**Provenance or it is not stored.** A field with no `source_url` is dropped, never guessed.

**Rollback is `DROP TABLE digest.member_web_profile`.** Nothing else changes, so the system returns
byte-identical to today.

### New view: `digest.member_fact_conflicts`

Compares what we hold against what the web says, per member, per field. It writes nothing and
merges nothing. A member's own census answer is never silently replaced. Goldsmith appears here on
day one with `location` and `role` in conflict.

### Partner side

The same fetch fills `partner_web_profile.people` for the 281 empty rows. No new table is needed
there; `people` is already an existing, already-empty column, so filling it is not a rewrite.

## How the data gets applied

Four consumers, shipped in order of blast radius. **Only stage A is in scope for this ticket.**

| stage | what changes | who sees it | proof required | in scope |
| --- | --- | --- | --- | --- |
| A | the table and the conflict view exist and are populated | staff, via SQL | row counts, conflict list, spot checks | **yes** |
| B | `member_card_v3` gains a labelled, cited web block | members | gate green, prod probe, #5068 re-fire | no, next ticket |
| C | `persona_refresh.py` takes the web profile as a third signal class, tagged `public` alongside #165's `self-reported` and `observed` | members | before and after on thin personas | no |
| D | web text enters `member_profile_embeddings`, and a web evidence key enters `derive_member_expertise()` | members, the Personas sheet, Millie's tiering | **must beat `digest.expertise_truth`** (609 rows, 42 topics, 146 members) | no |

**The rubric does not change on this ticket, and should not change on a hunch.** Adding an evidence
key to `derive_member_expertise()` rewrites the score on all 17,868 rows and moves every rank the
Personas sheet renders and every tier Millie reads off `member_expertise.pct`. #163 Task 1 already
built the instrument to judge that properly. A rubric change must beat the truth set, with before
and after numbers, on its own ticket.

**The one genuinely risky step, named.** The table is inert. The moment any of this becomes live to
a member is stage B, when a gated function is changed to read it, and the handbook's own trap says a
shared Postgres function is live on prod the instant it is applied, with no snapshot riding the
promote. Its rollback is re-applying the old function body. Stage A cannot reach a member at all.

## Autopilot

The weekly pattern already proven on partners by #160: fetch, hash, extract only what changed,
re-embed. A scheduled task, same shape as `groupos-videos-weekly`.

- Cadence: weekly.
- Change detection on `source_hash`, so an unchanged LinkedIn page costs one Contents call and
  writes no row.
- Never writes Airtable ([[feedback_never_write_to_airtable]]).
- Records a heartbeat so the derivations tile can see it, like the other 13 jobs.

Not in phase 1: Exa Monitors. It is the purpose-built product for watching web presence over time,
at $15 per 1k, and it is worth revisiting once stage B proves the data is used.

## Acceptance criteria

1. `digest.member_web_profile` exists, append-only, with the columns above, and **no UPDATE
   statement anywhere in the pipeline touches any pre-existing table**. Proven by reading the
   migration and the loader.
2. A full phase-1 pass populates rows for the 464 actives with a LinkedIn URL, with `fetch_status`
   accounted for on every one of them. Report: ok / unreachable / empty counts.
3. Every stored field carries a `source_url` and a `fetched_at`. Zero rows with a populated `role`
   or `company` and a null `source_url`. Proven by SQL.
4. `digest.member_fact_conflicts` returns a list, and Michael Goldsmith `rec5k8tMRPgD0jr2h` appears
   in it with `location` and `role` in conflict.
5. `partner_web_profile.people` is filled for a measured share of the 281 empty rows. Report the
   hit rate honestly, including the misses; StoreClaw is a known miss and must be reported as one.
6. The weekly job runs, stamps a heartbeat, and a second run within the same week writes zero new
   rows for unchanged pages.
7. `python3 scripts/olivia_leak_gate.py` GREEN, exit 0, before anything merges.
8. Millie's answers are unchanged. No gated function is modified on this ticket. Proven by a prod
   probe on a member question before and after, returning the same answer.

## Out of scope, explicitly

- Phase 2, the 269 members with no LinkedIn URL and the 101 unreachable partners.
- Any change to `member_card_v3` or any other gated function.
- Any change to `persona_refresh.py`.
- Any change to `derive_member_expertise()` or to `member_profile_embeddings`.
- Exa Monitors.
- Any write to Airtable.

## Open questions for Andy

1. **Retention of `raw`.** Storing Exa's unmodified payload makes every extraction re-runnable
   without paying again, and it also means we hold a copy of a member's LinkedIn profile in our
   warehouse. Keep it, or keep only the extracted fields?
2. **The persona fabrication is a separate defect.** Goldsmith's "Miami-based e-commerce founder"
   is wrong whether or not Exa is ever bought. File it as its own ticket now, or fold it into
   stage C?
3. **Staff-only or member-visible provenance at stage B.** When Millie eventually says a web fact,
   does she name LinkedIn as the source to the member, or cite it silently to staff only?

## Prior art in this repo

- `#160` — `digest.partner_web_profile`, the crawl-and-extract pattern this mirrors.
- `#165` — the `self-reported` / `observed` source tags on persona lines, which stage C extends.
- `#163` — `digest.expertise_truth`, the instrument any stage D rubric change must beat.
- `#201` — `member_card_v3`, which already returns brand name, so the stage B plumbing exists.
- `#5068` — the failure this ticket's partner half exists to fix.
