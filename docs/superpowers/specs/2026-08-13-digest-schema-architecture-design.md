# Design — `digest` schema architecture, costed in three tiers

**Date:** 2026-08-13 · **Status:** awaiting tier decision · **Executor:** me, session by session
**Research this rests on:** `OLIVIA_SCHEMA_RESEARCH_2026-08-13.md` (commit `ce966e2`)

Andy asked for a costed plan covering all three tiers before choosing one. This is that document.
It is not a recommendation to do everything — §7 says where I would stop.

---

## 1. The problem, in one paragraph

Two member-identity spaces (`members.airtable_id`, 659 rows and `member_profiles.at_member_id`,
5,931 rows) are both formatted `rec` + 14 characters with **zero overlap**, and nothing in the
database distinguishes them. Thirteen foreign keys exist across 58 tables, so nothing rejects a
value from the wrong space. `content_items.meta->>'sender_member'` carries **both** types — one per
source — and every consumer joins on one of them, which is why the Facebook interaction graph does
not exist and 88% of expertise evidence is missing. The same absence of declared structure lets 51
fabricated chapter entities exist, and means each new data source re-implements identity binding,
access rules and participation from scratch.

## 2. What we are optimising for

In priority order, from Andy's own framing across this conversation:

1. **Nothing silently wrong.** A bad write should fail, not be absorbed and answered from.
2. **Someone else can read it.** The external developer's reaction is the acceptance test.
3. **The next ten sources are cheap.** Chapter-restricted events, GroupOS documents, Circleback.

Explicitly *not* a goal: query speed. Foreign keys do not make reads faster (they cost a little on
write). Separate index work is noted in §6 but is not part of any tier.

## 3. Correction carried into this design

Earlier I proposed a Postgres **domain type per `rec` space** so the two keys could never be
assigned to each other. That is weaker than I claimed: domains over the same base type remain
assignable through `text`, and since both keys share a format, the CHECK would be identical for
both and separate nothing. **Foreign keys are the enforcement** — a FK to
`member_profiles(at_member_id)` rejects an `airtable_id` because the value is not there. The plan
below relies on FKs, not domains.

---

## 4. Tier 1 — fix what is live and wrong

No schema changes. Data and function-body corrections only.

| # | Work | Effort | Risk |
|---|---|---|---|
| 1.1 | **Chapter dossiers.** `refresh_entity_dossiers.sql:215` splits the multi-select with `regexp_split_to_table` (copying `chapter_info.sql:103-105`), excludes `Chapter Leads`, deletes the 51 fabricated rows, re-runs. Also corrects the 20 real rows, which currently under-count by excluding 118 multi-chapter members. | 0.5 session | **Low** — dossiers rebuild from source; nothing member-facing reads chapters today |
| 1.2 | **`sender_member` key mismatch.** Pick one key (recommend `at_member_id`, the canonical one), rewrite `fb_link_content.sql:22`, backfill 13,450 `wa_message` rows to match, re-run `derive_knowledge_graph` and `derive_member_expertise`. | 1 session + verify | **Medium** — expertise scores will change (improve) for the first time; needs an eval check, not just a gate run |
| 1.3 | **17 unreachable members.** Diagnose why they have no `member_phone_index` row, fix the cause in `refresh_member_phone_index` or upstream. | 0.5 session | Low |
| 1.4 | **`multi_source_v2` stale routing** → `event_lookup_v3`, `partner_lookup_v2`. Pure SQL, no promote. | 0.5 session | Low — staging probe then apply |
| 1.5 | **`video_speakers.member_record_id`** holds GroupOS 24-hex, resolves to nothing. Either add a resolver or rename the column honestly. | 0.5 session | Low |
| 1.6 | Correct the 31 `COMMENT ON COLUMN` statements that §3 of the research proved wrong. | 0.25 session | None |

**Tier 1 total: ~3 sessions.**

**If we stop here:** the data is correct and Olivia gets back a capability she was built with. The
*structure* is untouched — your developer opens the visualizer and has the identical reaction. The
next data source still costs ~15 functions.

---

## 5. Tier 2 — declare the structure that already holds

Everything in Tier 1, plus:

| # | Work | Effort | Risk |
|---|---|---|---|
| 2.1 | **Foreign keys on the 7 simple relations** — `event_registrations.event_at_id`, `member_edges.a_id/b_id`, `wa_messages.chat_id`, `summaries.chat_id`, `fb_post_images.post_id`, `olivia_feedback.wamid`. `ADD CONSTRAINT … NOT VALID` (instant, no scan, no lock), then `VALIDATE CONSTRAINT` separately. Each preceded by reading its loader for insert order. | 1.5 sessions | **Low** — all measured at 0 orphans; `NOT VALID` protects new writes immediately |
| 2.2 | **Foreign keys on the 18 `at_member_id` tables** → `member_profiles`. Same two-step. These sit under the busiest write paths (persona rebuild, event sync, Olivia's own log), so each loader gets read first. This is the step that makes the §1 bug class unwritable. | 2.5 sessions | **Medium** — the constraint itself is safe; the risk is a loader that inserts a child before its parent lands, which only reading them reveals |
| 2.3 | **`entity_dossier` becomes enforceable.** Four nullable typed columns with a CHECK that exactly one is set, each with its own FK — or four small tables. Rewrite `refresh_entity_dossiers` and 5 readers. | 1.5 sessions | Medium — touches a table 3 lanes read |
| 2.4 | **A `forms` registry.** New table keyed `form_id` (name, scope, population, active/retired, first/last submission, whether it collects an identifier), backfilled from `form_responses` ∪ `form_scope` ∪ `form_population`. FK the 5 orphaned `form_id` columns to it. Resolves the 48 forms whose `form_name` is just the id. | 1 session | Low |
| 2.5 | **`NOT NULL` on business-critical columns** where the data already supports it (currently 43% of columns). | 0.5 session | Low |
| 2.6 | **`form_scope` becomes a chokepoint view**, the #58 treatment — one object instead of a join repeated in 6 places and skipped in 3. | 0.5 session | Low |

**Tier 2 total: ~7.5 sessions** (cumulative ~10.5).

**Not included, needs its own ruling:** RLS policies. 26 tables have RLS enabled with **zero
policies**; the grant layer is the entire boundary today. Adding real policies is defence in depth
and would take ~2 sessions, but it changes the security model and should be an explicit decision,
not a line item.

**If we stop here:** the visualizer shows a real map, a new developer can read the model, and the
wrong-key class of bug becomes impossible to write. Each new source still re-implements identity
binding, access rules and participation — so source #8 is cheaper, but not cheap.

---

## 6. Tier 3 — the three abstractions

Everything above, plus the structural change that flattens the 107→1000 curve. Phased; each phase
ships and proves before the next starts.

| # | Work | Effort | Risk |
|---|---|---|---|
| 3.1 | **One link table.** `member_link(source, external_id, at_member_id, method, confidence, bound_at)`. Absorbs `fb_member_map`, `zoom_name_alias`, `member_phone_index`, `video_speakers.member_record_id`, `partner_reviews.app_user_id`. Resolvers rewritten to one lookup. Match rate per source becomes a queryable number — and then an alarm. | 3.5 sessions | **High** — identity is load-bearing everywhere; done behind a compatibility view, old tables retired only after parity is proven |
| 3.2 | **Audience as data.** One `can_see(member, item)` chokepoint replacing the `access_rule` jsonb branch currently duplicated across **10 functions** with 4 hardcoded types. A chapter-restricted event becomes a row, not a fifth branch in ten places. | 3.5 sessions | **High** — this *is* the privacy boundary. Gate must be green at every step; no phase lands without it |
| 3.3 | **Participation as one table.** `participation(person, entity_kind, entity_id, role, …)` covering speaker / attendee / author / reviewer / registrant — five implementations of one idea today, two of which resolve to nothing. Handles the member-or-not-a-member case once. | 4.5 sessions | **High** — `event_registrations` is the busiest table and #58's chokepoint view lives on it |

**Tier 3 total: ~11.5 sessions** (cumulative ~22).

**If we stop here:** your chapter-restricted-virtual-event-with-speakers example is a loader plus
configuration. New sources add rows, not functions.

---

## 7. Sequencing, proof, and what I would actually do

**Every step, without exception:** leak gate green (253 checks) before and after · live proof cited
(SQL result, gate output, probe) · one concern per session · rollback stated before the change.
Schema changes go in as `NOT VALID` first so protection starts immediately and validation is a
separate, interruptible step.

**My recommendation: commit to Tier 1 now, then Tier 2, and decide Tier 3 after Tier 2 finishes.**

Tier 1 is not optional — it is live wrong data and lost capability, and it is cheap. Tier 2 is the
one that answers your developer, and its early steps (2.1) are genuinely low-risk. The reason to
decide Tier 3 *after* Tier 2 rather than now: **Tier 2 measures how brittle the loaders actually
are.** Reading 25 loaders for insert-order safety tells us what Tier 3 would really cost far better
than any estimate I can write today. If the loaders turn out clean, Tier 3 gets cheaper than 11.5
sessions; if they are tangled, we will know before committing months.

**Competing sprint work, stated honestly:** the board carries six other S1 tickets, including #72
(load test before the Mille demo). Tier 2 alone is ~7.5 sessions and will displace them. That
trade-off is Andy's, not mine.

---

## 8. Open questions this design does not settle

1. **RLS policies — yes or no?** (§5, not costed into any tier.)
2. **Unmatchable rows.** 8,036 unstamped form responses and 2,779 unresolved Zoom attendees are
   honest unknowns. Recommendation: **nullable** FKs — a NULL stays legal, a *wrong* value becomes
   impossible. Needs confirmation.
3. **Which key survives long-term?** This design enforces `at_member_id` as canonical (the code
   already votes 59 functions to 14). The alternative — promoting `airtable_id` — is defensible but
   would invert more code. Answering this closes the question the 2026-08-02 audit left open.
4. **Does `members` eventually merge into `member_profiles`?** Not proposed here; it would remove
   the dual-key problem at the root but touches the entire WhatsApp layer.
