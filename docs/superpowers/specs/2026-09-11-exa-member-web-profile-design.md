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

Exa sells search, but the part that matters here is a structured entity layer sitting under the
index. A company or person result carries names, titles, headcount, headquarters, founding year,
industry, work history, education and web-traffic history as **fields**, not as prose to be scraped.

**LinkedIn is one source among many, and not the important one.** A single search on one member with
LinkedIn excluded returned six different kinds of page: the brand's own founding story, a press
release, a lender's customer case study explaining how the company finances inventory, Exa's
structured company record, Exa's structured person record, and a completely unrelated factory. The
company record alone carried facts no MDS system holds: the legal entity **Suit Up Brands LLC**,
16 employees, a Newport Beach address, six months of web-traffic history, and the fact that Happy
Innovations is the brand house behind Happy Nuts, Happy Curves and Happy Soles.

**Exa keeps stable entity IDs.** People and companies have permanent identifiers
(`exa.ai/library/organization/…`, `exa.ai/library/person/…`). This matters more than it sounds: it
gives the company nodes in the graph a real key instead of a company-name string. Matching on a name
string is exactly how the Hector founder got attached to the wrong company.

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

The wrong-person risk is the whole risk, and the sweep above put a number on it: **three of ten
results were the wrong entity** when the only anchor was a brand name.

LinkedIn is not special as a *source*; it is special as an *anchor*, because it is a URL the member
handed us themselves, so reading it cannot return somebody else. Everything the sweep finds beyond
that URL has to earn its place by corroboration.

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
| ~~`role`~~ | — | **dropped.** A member has many roles over time; they live as dated edges |
| ~~`company`~~ | — | **dropped.** Ian Sells has eight. One column cannot hold that |
| `headline` | text | the one-line self-description the source shows, verbatim, not parsed |
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

## Web presence — the second collection

**Andy 2026-09-11: "we want to see this person's presence on the web, like news articles (unless it's
his personal blogs or websites), any public info, podcast, youtube, anything that can help us."**

This is a different question from the profile read and gets its own collection.

| collection | asks | source | endpoint |
| --- | --- | --- | --- |
| 1. Profile | where do they work, what do they run | their own LinkedIn or brand site | Contents, $1 / 1k |
| 2. Presence | what has the world said about them | third parties only | Search, $7 / 1k |

### What a sweep on a well-known member actually returns

Andy ran one on Ian Sells on 2026-09-11. Ten results, **$0.007**, and the shape of the answer is
not a profile row. It is a dossier:

| source | class | what it carried |
| --- | --- | --- |
| LinkedIn entity | profile | Founder & CEO of MDS since Jan 2016, Solvolt, SDSU |
| Equilar ExecAtlas | executive database | "sold 2 multi million dollar amazon brands", RebateKey, Elite Seller |
| amzsummits.com speaker page | **expertise evidence** | conference speaker bio, managed $10M+ on Amazon in 2018 |
| success.ai | aggregator | work history across five companies, plus a masked work email |
| Authority Magazine, Medium, 2021 | long-form interview | full biography, two exits, $30M managed |
| joinbrands.com/about-us | company page | **COO & Co-Founder**, alongside Leo Limin and Johan Geuze |
| freeup.net podcast, 2019 | **podcast transcript** | the origin story of MDS in his own words |
| three LinkedIn posts, 2024-2026 | own content | dated, quotable |

**Three corrections to this design fall out of that, and they matter.**

**1. A member has many companies, not one.** Ian appears with MDS, JoinBrands, RebateKey,
EliteSeller, Pixelfy.me, Dev Salsa, eComPartners.co and Solvolt. A single `company` column on
`member_web_profile` is simply the wrong shape. The companies belong in `web_edges`, many per
member, which the graph section already allows — but the profile table must stop pretending there
is one answer.

**2. Facts are time-scoped, and sources disagree because time passed.** LinkedIn says Founder & CEO
of MDS. The JoinBrands about-page says COO & Co-Founder. The 2021 Medium interview says CEO of
RebateKey. **All three are true, at different times.** Exa's `workHistory` carries `from` and `to`
dates, so every `works_at` and `founded` edge stores them, and "current" is *derived* from a null
`to`, never stored as the only value. Without this, `member_fact_conflicts` would raise false alarms
on every member who has ever changed roles.

**3. Speaker pages and podcasts are the expertise evidence the system lacks.** The amzsummits
speaker page and the freeup podcast are exactly the public, third-party, non-self-reported signal
that `member_expertise` has zero of today. They are classed `speaking` in
`member_web_presence` and are the strongest candidate input for stage D.

**One rule added from the same sweep: no contact data.** Aggregator sites such as success.ai and
Equilar return work emails and phone numbers. **Those fields are dropped at extraction and never
stored**, regardless of `raw` retention. We do not need them, and harvesting a member's contact
details from a data broker is not something this system should start doing.

**Third-party only, enforced in the query, not by hand.** Exclude the member's own domains, taken
from `Brand(s) URL / Name(s)`, `Own Website & % of Revenue` and `Storefront - Census`; exclude Exa's
`personal site` category. Include news, publications, podcasts, video and company records. Date floor
2023-01-01, so a decade of noise does not arrive with the signal.

**What a real sweep returns, measured 2026-09-11 on one member with LinkedIn excluded.** Ten results,
six distinct source types, cost $0.017 including page summaries:

| source type | example | what it gave us |
| --- | --- | --- |
| brand's own story page | `myhappynuts.com/pages/our-story` | founding story, four founders |
| press release | einpresswire, 2025-06-04 | a product launch |
| lender case study | Wayflyer customer story | how the company finances inventory |
| structured company record | Exa entity `57m0gbzgjp6` | legal entity Suit Up Brands LLC, 16 employees, address, 6 months of web traffic, the brand-house structure |
| structured person record | Exa entity `xfb2twbsslj` | work history and education as fields |
| PR wire, separate search | PR Newswire 2025-09-13 | *"Matthew Greene, CEO of Happy Innovations"* launching a third brand |

Not one of those is LinkedIn, and none of it is in our warehouse today.

**The same sweep also proved the risk.** Three of the ten results were the wrong entity entirely: a
nut factory in Chiba Prefecture, a Vietnamese corporate-gifting company whose founder is also listed
as "Founder/CEO at Happy Nuts", and a Dubai business called Gourmet Happy Nuts LLC. **A 30% collision
rate on a single common brand name is the #5068 failure reproducing in front of us**, and it is the
reason corroboration below is mandatory rather than a nicety.

**New table `digest.member_web_presence`:** `at_member_id`, `url`, `domain`, `title`, `published_at`,
`kind` (`news` \| `podcast` \| `video` \| `publication` \| **`speaking`** \| `company_page` \|
`aggregator`), `summary`, `corroborated_by`, `confidence`, `raw`, `fetched_at`. Each row also
becomes a `featured_in` edge in `web_edges`. `speaking` is the class that carries conference speaker
pages and podcast appearances, and it is the one stage D will care about.

**The risk is name collision, and it is handled by corroboration, not by hope.** A member with a
common name pulls the wrong person's press. A hit counts only when the page also mentions a company
or brand we already hold for that member; that company name goes in `corroborated_by`.
Uncorroborated hits are stored at `confidence < 1` and are never surfaced to a member or fed to any
score. This is the same discipline that #5068 lacked.

**Why this collection matters more than the profile in the long run.** It is the only class of
evidence in the entire system that is public, third-party and not self-reported, which makes it the
honest input for any future proficiency signal. That is stage D, and it still has to beat
`expertise_truth` before it ships.

**Cost:** $0.017 for the measured single-member sweep including summaries, so about **$12.50** for
all 733 members in one pass.

## The knowledge graph

**Andy 2026-09-11: "We need to make sure we have a proper knowledge graph. That all is related."**
Agreed, and the probe shows the current graph cannot express any of it.

### What the graph actually is today

`digest.member_edges` holds 139,967 rows and exactly three edge types, every one of them
member-to-member co-presence:

| edge_type | rows | distinct a-nodes |
| --- | --- | --- |
| `co_attended` | 95,049 | 1,559 |
| `same_chat` | 24,368 | 360 |
| `same_chapter` | 20,550 | 685 |

`digest.entity_dossier` holds 3,121 entities across four kinds: event 1,457, video 1,084,
partner 509, chapter 71. **There is no company node and no member node anywhere in the graph.**

So the graph answers one question, "who was in the same room", and cannot answer "who works where",
"who founded what", "which company owns this product" or "which two members are colleagues".

### Why that is exactly why #5068 failed

Hector is the in-house technology of an agency, Neon Digital Media. The founder Exa returns for
Hector is that agency's founder. Without a company-to-company edge there is no way to say "the
person founded the parent, not the product", so any answer about Hector's founder is a coin flip.
The empty `people` column is the symptom. The missing edge is the cause.

### Two hard constraints found in the code

1. **`derive_knowledge_graph()` begins with `delete from digest.member_edges where true;`** and
   rebuilds nightly. Any Exa-derived edge written into `member_edges` is destroyed on the next run.
   Web edges therefore need their own table.
2. **The graph's fourth edge type is dead.** The function also inserts `thread_interaction`, the
   Facebook commenter-to-author edge, and the live table contains **zero** of them. The insert joins
   `digest.members.airtable_id = content_items.meta->>'sender_member'`, which matches 0 rows;
   joining on `at_member_id` matches 13,407 comments, and on `member_profiles.at_member_id` 15,503.
   This is the `airtable_id` vs `at_member_id` trap named in handbook chapter 07. **Found alongside,
   not fixed here** — see "Found alongside" below.

### Design: one graph to query, two tables to write

**New table `digest.web_edges`.** Typed, namespaced, additive, and never touched by the nightly
rebuild.

| column | type | notes |
| --- | --- | --- |
| `a_id` / `a_kind` | text | `member` \| `company` \| `partner` \| `external` |
| `b_id` / `b_kind` | text | same |
| `edge_type` | text | see below |
| `valid_from` / `valid_to` | date | **from the source's own dates; a null `valid_to` is what "current" means.** Without this, three true statements about Ian Sells read as a three-way conflict |
| `weight` | numeric | |
| `evidence` | jsonb | |
| `source_url` | text | required, same rule as the profile table |
| `fetched_at` | timestamptz | |
| `confidence` | numeric | 1.0 for a member-supplied URL |

**New table `digest.web_entity`** gives companies a node at last: `entity_id` (**Exa's stable
identifier**, e.g. `57m0gbzgjp6`, not a name string), `kind`, `name`, `legal_name`, `domain`,
`linkedin_url`, `industry`, `headcount`, `hq`, `web_traffic`, `raw`, `source_url`, `fetched_at`.
A separate table rather than a new `entity_dossier` kind, so no existing loader changes behaviour.

**Key on Exa's entity ID whenever there is one.** Every previous attempt in this system to relate a
company to a person matched on the company NAME, which is what put Hector's founder on the wrong
company and what pulled three unrelated businesses into a ten-result sweep. An entity ID does not
collide.

**But the ID is not always there, and the spec must not pretend otherwise.** In the Matt Greene
sweep, Happy Innovations came back with `id: https://exa.ai/library/organization/57m0gbzgjp6`. In
the Ian Sells sweep, every `workHistory` entry carried `"company": {"id": null, "name": …}`. So the
key is a three-step ladder, recorded per row in `entity_key_source`:

1. Exa entity ID, when present — no collision possible.
2. The company's own domain, when the payload carries one.
3. Name plus corroboration, at `confidence < 1`, never surfaced and never scored.

**Edge types phase 1 can produce, all straight out of the Exa payload:**

| edge_type | from | to | proven in the probe by |
| --- | --- | --- | --- |
| `works_at` | member | company | Goldsmith to Lone Star Merchandising Group |
| `founded` | member | company | Matthew Greene to Happy Innovations |
| `previously_at` | member | company | Goldsmith to Daily Steals, 2012-2014 |
| `colleague_of` | member | member | Casey Ames and Amelia Ames, both at Harkla |
| `owns_brand` | member | company | Casey Ames to Harkla |
| `parent_of` | company | company | **Neon Digital Media to Hector, the #5068 fix** |
| `featured_in` | member | external | the Amazon Seller Spotlight on Happy Innovations |

`colleague_of` is worth calling out: it is the first member-to-member edge in the system that means
something other than "was in the same room", and it costs nothing extra to derive.

**One graph to read: `digest.knowledge_graph`,** a view that UNIONs `member_edges` and `web_edges`
into a single surface with a `source` column saying which side a row came from. Consumers query one
place. The nightly rebuild keeps owning its own table and cannot wipe the web side.

**Rollback stays one line per table.** Dropping `web_edges`, `web_entity` and the view returns the
graph byte-identical to today.

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
7. `digest.web_entity` and `digest.web_edges` exist and are populated, and `digest.knowledge_graph`
   returns both sides in one query. Report edge counts by `edge_type`.
8. **The `parent_of` edge exists for Hector and its parent agency**, and a SQL read of the graph
   returns the founder attached to the parent rather than the product. This is the #5068 fix stated
   as a graph query, not as a prose answer.
9. `derive_knowledge_graph()` runs after the load and `digest.web_edges` still holds every row.
   Proven by a count before and after, not by reading the function.
9b. `digest.member_web_presence` is populated, and **zero rows carry a domain the member owns**,
   proven by SQL against their own brand and website fields. Report how many members got at least
   one third-party hit, and how many of those hits are corroborated.
9c. **Every company node records how it was keyed.** Zero rows in `web_entity` with a null
   `entity_key_source`, and the split across the three ladder steps is reported, not assumed.
   Name-keyed rows all sit at `confidence < 1`.
9e. **Role edges carry dates.** Every `works_at` and `founded` edge has a `from` date where the
   source gave one, and "current" is derived from a null `to`. Proven on Ian Sells, whose three
   sources disagree only because they describe different periods: none of those three may appear
   in `member_fact_conflicts` as a conflict.
9f. **No contact data is stored.** Zero email addresses and zero phone numbers anywhere in
   `member_web_profile`, `member_web_presence` or `web_entity`, including inside `raw`. Proven by
   a regex scan over the stored rows.
9d. **The collision rate is measured, not assumed.** Re-run the Matt Greene sweep through the
   corroboration rule: the three known wrong entities (the Chiba factory, the Vietnamese gifting
   company, Gourmet Happy Nuts LLC) must all be rejected or stored below full confidence.
10. `python3 scripts/olivia_leak_gate.py` GREEN, exit 0, before anything merges.
11. Millie's answers are unchanged. No gated function is modified on this ticket. Proven by a prod
    probe on a member question before and after, returning the same answer.

## Found alongside, not fixed here

**The knowledge graph's `thread_interaction` edge has never produced a row.**
`digest.derive_knowledge_graph()` inserts it by joining
`digest.members.airtable_id = content_items.meta->>'sender_member'`. That join matches **0** rows.
Joining on `at_member_id` matches **13,407** fb comments; on `member_profiles.at_member_id`,
**15,503**. The live table holds `co_attended`, `same_chat` and `same_chapter` only.

Effect: the only edge in the graph that records members actually interacting, rather than being
booked into the same room, is silently absent, and every consumer of `member_edges`
(`member_dossier_v2`, `chat_recommendations_v2`, `event_lookup_v2`) has been reading a graph with
that dimension missing. No existing ticket covers it; #158 touches `member_edges` only for foreign
keys. **Flagged for priority evaluation, per the standing rule that issues found alongside are not
the job.**

## Out of scope, explicitly

- Phase 2, the 269 members with no LinkedIn URL and the 101 unreachable partners.
- Any change to `member_card_v3` or any other gated function.
- Any change to `persona_refresh.py`.
- Any change to `derive_member_expertise()` or to `member_profile_embeddings`.
- Exa Monitors.
- Any write to Airtable.

## Open questions for Andy

1. ~~**Retention of `raw`.**~~ **Decided by Andy 2026-09-11: keep the raw payload.** Every
   extraction is re-runnable without paying again, and the graph below can be rebuilt from it
   without a refetch.
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
