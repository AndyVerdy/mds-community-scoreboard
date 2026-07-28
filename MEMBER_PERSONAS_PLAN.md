> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Member personas — plan

**Andy's definition (2026-07-26), verbatim intent:** *"A persona is when we take all the facts with no
gaps and write an internal note. This thing should be updated regularly, based on the forms, the events
he participated in, and every bit of information. Especially form. Evaluate every member across all the
data we have and create personas. Keep it updated."*

So: **not a field dump.** A written, synthesised internal note per member, refreshed as the source data
moves.

**Why it matters right now:** Eugene asked for "for me" personalisation **twice in three days** —
*"Recommend some calls for me to attend"* and *"What's been the top relevant topics **for me** in
Facebook this week"* — and got generic answers both times. The lanes that answer those receive only his
**location and past registrations**. Niche, categories, channels, business model, expertise and chapter
never reach them, even though we hold all of it.

---

## 1. Raw material — verified live 2026-07-26

| Input | Coverage | Notes |
|---|---|---|
| Application answers (`member_profiles.application`) | **452** of 742 | avg **6,782 chars** of prose — the richest single source |
| Airtable fields (`member_profiles.at_fields`) | **742** | avg **451 populated fields** per member |
| Structured attributes (`member_attributes`) | 608 Current Members | niche, categories, channels, business model, rev band, expertise, chapter |
| Event registrations | **17,748** rows | what they actually show up to |
| Own chat + FB activity | 908 members with activity · 16,551 FB rows | what they actually talk about |
| **Census forms** | **735 filled — NOT SYNCED** | ⚠️ see §2 |

---

## 2. ⚠️ Prerequisite — the census is missing

`MEMBER_ATTRIBUTES_SOURCE_MAP.md` §gaps: *"Census forms (735 filled, Forms table) are not in Supa yet.
Likely fresher than application answers for revenue/channels/SKUs."*

Andy singled out forms. The census is the freshest self-reported data we have and it is the one input
absent from the warehouse. **Personas built before it lands will be stale in exactly the dimension he
cares most about**, and every one will need regenerating afterwards.

**Recommendation: sync the census first, or accept a known-stale v1 and budget a full regeneration.**

---

## 3. Design

**Storage** — `digest.member_personas`

| column | purpose |
|---|---|
| `at_member_id` | PK, joins everything |
| `persona_note` | the written note (target 250–400 words) |
| `persona_embedding` | `vector(1024)`, voyage-3.5-lite — makes personas semantically matchable |
| `facts` | jsonb of the structured claims behind the prose, each with its source field |
| `sources_hash` | hash of every input; changes ⇒ regeneration due |
| `generated_at`, `model` | provenance |

**What the note contains:** who they are and what they sell · business model and channels · scale
(band only, never exact revenue) · what they are *good at* and what they *ask about* · which chats and
events they actually show up to · chapter and location · open threads (what they were recently working
on). Written as prose an MDS team member would recognise, not a form.

**Hard rule — `no gaps` means say the gap.** Where a field is missing the note says so explicitly
("no census on file; revenue band from the 2024 application"). A persona that quietly omits unknowns is
worse than none, because downstream ranking will treat silence as absence.

**Generation:** one LLM call per member over the assembled inputs. Haiku is sufficient — this is
summarisation over supplied facts, not reasoning.

**Refresh:** nightly job recomputes `sources_hash` per member and regenerates only the changed ones.
Full rebuild only on a prompt change or a new source (e.g. census landing).

---

## 4. Cost — measured, not guessed

Per member: ~5k input tokens (application excerpt + attribute block + activity sample + event history),
~800 output.

| model | per member | all 742 | nightly refresh (~20 changed) |
|---|---|---|---|
| Haiku 4.5 | ~$0.009 | **~$7** | ~$0.20 |
| Sonnet 5 | ~$0.027 | ~$20 | ~$0.55 |

Cheap enough that cost is not the constraint. **The `$15/day` eval spend guard applies — a full rebuild
must run deliberately, not inside a nightly.**

---

## 5. 🔒 Personas are INTERNAL — never emitted

Andy's word was **"internal note"**, and that has to be enforced, not assumed.

A persona synthesises revenue, application answers and staff-visible context into one paragraph. It is
**retrieval and ranking fuel only**:

- ✅ Rank events / partners / FB posts for relevance to this member
- ✅ Semantic member-to-member matching (persona embeddings)
- ✅ Help Olivia decide what to look for
- ❌ **Never** quoted, paraphrased or shown to any member — including the member it describes
- ❌ Never a `member_card` field

**Leak-gate checks required before any use:** persona text never appears in an answer; the persona RPC
is `service_role` only; anon denied; and a persona for member A is unreachable while answering member B.
Matches the existing surfacing policy — personas contain far more than the six public directory fields.

---

## 6. What it unlocks

| question | today | with personas |
|---|---|---|
| *"Recommend some calls for me to attend"* | calendar, unranked | ranked to Private Label / Kitchen / Supplements / Big-Box wholesale |
| *"Top relevant topics for me in Facebook this week"* | newest posts | posts weighted to his categories and channels |
| *"Any partner deals for me"* | generic list | filtered to his channels and scale |
| *"Who should I meet"* | filter-matched | semantically matched on persona, not just city + niche |

---

## 7. Sequencing

1. **Sync the census** (§2) — or explicitly accept a stale v1
2. Build `member_personas` + the generation script; run on **20 members** and have Andy read them —
   the note has to be recognisably right before spending on 742
3. Full generation (~$7) + embeddings
4. Leak-gate checks (§5) **GREEN** before anything reads a persona
5. Wire into ranking one lane at a time, starting with the FB catch-up — it is the one a real member
   asked for, twice

**Not started.** This document is a proposal, not a status.
