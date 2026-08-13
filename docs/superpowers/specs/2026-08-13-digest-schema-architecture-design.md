# Design — `digest` schema architecture, costed in five phases

**Date:** 2026-08-13 · **Status:** awaiting phase decision · **Executor:** me, session by session
**Research this rests on:** `OLIVIA_SCHEMA_RESEARCH_2026-08-13.md` (commit `ce966e2`)

Andy asked for a costed plan covering every phase before choosing where to stop. This is that document.
It is not a recommendation to do everything — §7 says where I would stop.

---

## 1. The problem

> **Revised 2026-08-13 after Andy pushed back that the first version was narrow. He was right.**
> The original paragraph led with the two `rec` key spaces and framed everything downstream of
> them. That presents the sharpest *symptom* as the root cause, and it caused this document to drop
> two fixes the research had already recommended (§5.7). Both are restored below.

**The warehouse has no shared model.** Each data source was added as a self-contained vertical —
its own identity binding, its own access rule, its own participation shape, its own lookup
functions — and nothing was ever generalised upward. Nothing is declared, so the database enforces
almost none of it, and nothing surfaces when a convention is broken.

That single cause has six measurable faces:

| face | evidence |
|---|---|
| **No identity model** | 14 identity keys in 4 formats; 3 different binding mechanisms (bridge table, bridge column, fuzzy stamp). Its sharpest instance: `members.airtable_id` and `member_profiles.at_member_id` are both `rec`+14 with **zero overlap**, and `content_items.meta->>'sender_member'` holds both — so 17,676 Facebook rows join to nothing, the FB interaction graph does not exist, and 88% of expertise evidence is missing |
| **No access model** | `access_rule` jsonb with 4 hardcoded types, interpreted independently in **10 functions**. A fifth rule type means 10 edits, all of which must be right |
| **No participation model** | speaker / attendee / author / reviewer / registrant — 5 implementations of "a person did a thing to an entity", 2 of which resolve to nothing |
| **Nothing declared** | 13 foreign keys and 10 CHECKs across 58 tables; **36 of 58 have nothing but a primary key**; 26 tables have RLS enabled with **zero policies** |
| **Failures are absorbed, not surfaced** | `exception when others then null` wraps all 3 `member_events` triggers and all 8 health-check signals — a broken check reports green. 51 fabricated chapter entities exist because nothing rejected them |
| **No release process for SQL** | 10 function families carry v1/v2/v3; an `EXEC_NAME` map in n8n rewrites tool names "at the last inch" to pick a version. That indirection is why `multi_source_v2` silently routes to stale implementations |

**Why it compounds:** every new source pays for all six again. That is the mechanism behind Andy's
"107 functions becomes 1000," and it is the reason a chapter-restricted event with speakers is a
project rather than a configuration change.

**Not caused by any of this, and therefore not fixed by it:** there is no test layer below the
end-to-end eval bank, which is slow and costs money per run. Noted as cross-cutting in §7.

## 2. What we are optimising for

In priority order, from Andy's own framing across this conversation:

1. **Nothing silently wrong.** A bad write should fail, not be absorbed and answered from.
2. **Someone else can read it.** The external developer's reaction is the acceptance test.
3. **The next ten sources are cheap.** Chapter-restricted events, GroupOS documents, Circleback.

Explicitly *not* a goal: query speed. Foreign keys do not make reads faster (they cost a little on
write). Separate index work is noted in §6 but is not part of any phase.

## 3. Correction carried into this design

Earlier I proposed a Postgres **domain type per `rec` space** so the two keys could never be
assigned to each other. That is weaker than I claimed: domains over the same base type remain
assignable through `text`, and since both keys share a format, the CHECK would be identical for
both and separate nothing. **Foreign keys are the enforcement** — a FK to
`member_profiles(at_member_id)` rejects an `airtable_id` because the value is not there. The plan
below relies on FKs, not domains.

---

## 4. Phase 2 — fix what is live and wrong

No schema changes. Data and function-body corrections only.

| # | Work | Effort | Risk |
|---|---|---|---|
| 2.1 | **Chapter dossiers.** `refresh_entity_dossiers.sql:215` splits the multi-select with `regexp_split_to_table` (copying `chapter_info.sql:103-105`), excludes `Chapter Leads`, deletes the 51 fabricated rows, re-runs. Also corrects the 20 real rows, which currently under-count by excluding 118 multi-chapter members. | 0.5 session | **Low** — dossiers rebuild from source; nothing member-facing reads chapters today |
| 2.2 | **`sender_member` key mismatch.** Pick one key (recommend `at_member_id`, the canonical one), rewrite `fb_link_content.sql:22`, backfill 13,450 `wa_message` rows to match, re-run `derive_knowledge_graph` and `derive_member_expertise`. | 1 session + verify | **Medium** — expertise scores will change (improve) for the first time; needs an eval check, not just a gate run |
| 2.3 | **17 unreachable members.** Diagnose why they have no `member_phone_index` row, fix the cause in `refresh_member_phone_index` or upstream. | 0.5 session | Low |
| 2.4 | **`multi_source_v2` stale routing** → `event_lookup_v3`, `partner_lookup_v2`. Pure SQL, no promote. | 0.5 session | Low — staging probe then apply |
| 2.5 | **`video_speakers.member_record_id`** holds GroupOS 24-hex, resolves to nothing. Either add a resolver or rename the column honestly. | 0.5 session | Low |
| 2.6 | Correct the 31 `COMMENT ON COLUMN` statements that §3 of the research proved wrong. | 0.25 session | None |
| 2.7 | **Fail-open becomes fail-loud.** Remove `exception when others then null` from the 3 `member_events` triggers and the 8 health-check signals; log and alarm instead. Today a broken health check reports green — the monitoring is unfalsifiable, which makes every other "it's fine" in this system unfalsifiable too. *(Restored — recommended in the research, dropped from the first draft of this plan.)* | 1 session | **Low–medium** — a trigger that starts raising instead of swallowing can fail a write that currently succeeds; each one gets a real error path, not a bare removal |

**Phase 2 total: ~4 sessions.**

**If we stop here:** the data is correct and Olivia gets back a capability she was built with. The
*structure* is untouched — your developer opens the visualizer and has the identical reaction. The
next data source still costs ~15 functions.

---

## 5. Phase 3 — declare the structure that already holds

Everything in Phase 2, plus:

| # | Work | Effort | Risk |
|---|---|---|---|
| 3.1 | **Foreign keys on the 7 simple relations** — `event_registrations.event_at_id`, `member_edges.a_id/b_id`, `wa_messages.chat_id`, `summaries.chat_id`, `fb_post_images.post_id`, `olivia_feedback.wamid`. `ADD CONSTRAINT … NOT VALID` (instant, no scan, no lock), then `VALIDATE CONSTRAINT` separately. Each preceded by reading its loader for insert order. | 1.5 sessions | **Low** — all measured at 0 orphans; `NOT VALID` protects new writes immediately |
| 3.2 | **Foreign keys on the 18 `at_member_id` tables** → `member_profiles`. Same two-step. These sit under the busiest write paths (persona rebuild, event sync, Olivia's own log), so each loader gets read first. This is the step that makes the §1 bug class unwritable. | 2.5 sessions | **Medium** — the constraint itself is safe; the risk is a loader that inserts a child before its parent lands, which only reading them reveals |
| 3.3 | **`entity_dossier` becomes enforceable.** Four nullable typed columns with a CHECK that exactly one is set, each with its own FK — or four small tables. Rewrite `refresh_entity_dossiers` and 5 readers. | 1.5 sessions | Medium — touches a table 3 lanes read |
| 3.4 | **A `forms` registry.** New table keyed `form_id` (name, scope, population, active/retired, first/last submission, whether it collects an identifier), backfilled from `form_responses` ∪ `form_scope` ∪ `form_population`. FK the 5 orphaned `form_id` columns to it. Resolves the 48 forms whose `form_name` is just the id. | 1 session | Low |
| 3.5 | **`NOT NULL` on business-critical columns** where the data already supports it (currently 43% of columns). | 0.5 session | Low |
| 3.6 | **`form_scope` becomes a chokepoint view**, the #58 treatment — one object instead of a join repeated in 6 places and skipped in 3. | 0.5 session | Low |
| 3.7 | **One version per lane.** Collapse the 10 v1/v2/v3 families to a single live implementation each, delete the dead ones (`chat_recommendations_v3`), and remove the `EXEC_NAME` indirection from n8n so the tool name *is* the function name. This is what makes §3.6-class stale-routing bugs impossible rather than merely fixed. *(Restored — recommended in the research, dropped from the first draft of this plan.)* | 1.5 sessions | **Medium** — several v1s are live dependencies of their v2s, so each family is untangled and probed separately; touches n8n, so it needs a promote |

**Phase 3 total: ~9 sessions** (cumulative ~13).

**Not included, needs its own ruling:** RLS policies. 26 tables have RLS enabled with **zero
policies**; the grant layer is the entire boundary today. Adding real policies is defence in depth
and would take ~2 sessions, but it changes the security model and should be an explicit decision,
not a line item.

**If we stop here:** the visualizer shows a real map, a new developer can read the model, and the
wrong-key class of bug becomes impossible to write. Each new source still re-implements identity
binding, access rules and participation — so source #8 is cheaper, but not cheap.

---

## 6. Phase 4 — the three abstractions

Everything above, plus the structural change that flattens the 107→1000 curve. Phased; each phase
ships and proves before the next starts.

| # | Work | Effort | Risk |
|---|---|---|---|
| 4.1 | **One link table.** `member_link(source, external_id, at_member_id, method, confidence, bound_at)`. Absorbs `fb_member_map`, `zoom_name_alias`, `member_phone_index`, `video_speakers.member_record_id`, `partner_reviews.app_user_id`. Resolvers rewritten to one lookup. Match rate per source becomes a queryable number — and then an alarm. | 3.5 sessions | **High** — identity is load-bearing everywhere; done behind a compatibility view, old tables retired only after parity is proven |
| 4.2 | **Audience as data.** One `can_see(member, item)` chokepoint replacing the `access_rule` jsonb branch currently duplicated across **10 functions** with 4 hardcoded types. A chapter-restricted event becomes a row, not a fifth branch in ten places. | 3.5 sessions | **High** — this *is* the privacy boundary. Gate must be green at every step; no phase lands without it |
| 4.3 | **Participation as one table.** `participation(person, entity_kind, entity_id, role, …)` covering speaker / attendee / author / reviewer / registrant — five implementations of one idea today, two of which resolve to nothing. Handles the member-or-not-a-member case once. | 4.5 sessions | **High** — `event_registrations` is the busiest table and #58's chokepoint view lives on it |

**Phase 4 total: ~11.5 sessions** (cumulative ~24.5).

**If we stop here:** your chapter-restricted-virtual-event-with-speakers example is a loader plus
configuration. New sources add rows, not functions.

---

## 7. Sequencing, proof, and what I would actually do

**Every step, without exception:** leak gate green (253 checks) before and after · live proof cited
(SQL result, gate output, probe) · one concern per session · rollback stated before the change.
Schema changes go in as `NOT VALID` first so protection starts immediately and validation is a
separate, interruptible step.

**My recommendation: commit to Phase 2 now, then Phase 3, and decide Phase 4 after Phase 3 finishes.**

Phase 2 is not optional — it is live wrong data and lost capability, and it is cheap. Phase 3 is the
one that answers your developer, and its early steps (2.1) are genuinely low-risk. The reason to
decide Phase 4 *after* Phase 3 rather than now: **Phase 3 measures how brittle the loaders actually
are.** Reading 25 loaders for insert-order safety tells us what Phase 4 would really cost far better
than any estimate I can write today. If the loaders turn out clean, Phase 4 gets cheaper than 11.5
sessions; if they are tangled, we will know before committing months.

**This became Phase 1: there was no test layer.** Below the end-to-end eval bank — slow, and
costing money per run — nothing verifies a SQL function. That is why the `sender_member` mismatch
survived, why `multi_source_v2` routed to stale versions unnoticed, and why the 51 fabricated
chapter rows were only found by someone looking. Every phase ships behind the leak gate, which
checks *outputs and permissions*, not *logic*. A real fix (pgTAP, or assertion tests per function
run in CI) is ~2 sessions and would make each phase safer. I have deliberately not folded it into a
phase originally because it is a decision about how we work, not about this schema — but it is the single
change most likely to stop the next one of these.

**Competing sprint work, stated honestly:** the board carries six other S1 tickets, including #72
(load test before the Mille demo). Phase 2 + Phase 3 is ~13 sessions and will displace them. That
trade-off is Andy's, not mine.

---

## 8. Open questions this design does not settle

1. **RLS policies — yes or no?** (Phase 5, and see the risk register: policies would protect nothing while everything runs as `service_role`.)
2. **Unmatchable rows.** 8,036 unstamped form responses and 2,779 unresolved Zoom attendees are
   honest unknowns. Recommendation: **nullable** FKs — a NULL stays legal, a *wrong* value becomes
   impossible. Needs confirmation.
3. **Which key survives long-term?** This design enforces `at_member_id` as canonical (the code
   already votes 59 functions to 14). The alternative — promoting `airtable_id` — is defensible but
   would invert more code. Answering this closes the question the 2026-08-02 audit left open.
4. **Does `members` eventually merge into `member_profiles`?** Not proposed here; it would remove
   the dual-key problem at the root but touches the entire WhatsApp layer.
