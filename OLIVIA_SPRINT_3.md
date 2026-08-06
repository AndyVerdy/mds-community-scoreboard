> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.
- **Always show a ticket's STORY + ACs. Closing needs: short results · short AC checklist (met/not) · before/after numbers.** (Andy 2026-08-03)

# Olivia — SPRINT 3

**Opened 2026-08-03**, after Release 3 shipped. Previous board archived in
`OLIVIA_BACKLOG_ARCHIVE.md` (every ticket shipped in Releases 1–3, newest first).

## 🎯 Sprint goal

**Make Olivia personal.** Everything so far makes her *accurate*; this sprint makes her answers,
recommendations and matches specific to the member asking — and closes the last failure class
(inventing members) so that personalization is built on something trustworthy.

**Where we start from (Release 3 close, 2026-08-03):** prod `89ee3632` · **smoke 1.7% wrong**
(173 judged, from 3.6%) · **architecture 8/10** (from 6) · retrieval, identity, event log, graph
and the expertise ledger all live · handbook shipped and mirrored to ClickUp.

## 📋 At a glance

| # | Ticket | Priority | Size | Staging | Prod |
|---|---|---|---|---|---|
| **#57** | Live-test trio: empty reports · wrong-turn Yes · "reply YES" wording | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `955ed56f` |
| **#18** | How-MDS-works answers | 🟡 S2 | M | ⛔ BLOCKED — no data (Andy 2026-08-05) | — |
| **#19** | Privacy: share, keep, delete | ⚪ S4 | M | — | — |
| **#20** | Census into the warehouse | 🟡 S2 | L | ✅ staged + proven `1dd2f39b` (aggregates + owner lane; personas open) | ⏳ awaiting promote |
| **#35** | New data source — DOCUMENTS (GroupOS) | ⚪ S4 | M | — | — |
| **#17** | Auto-refresh videos and partners | 🔵 S3 | M | — | — |
| **#48** | AT roster write-back | ⚪ S4 | S-M | — | — |
| **#36** | New data source — CIRCLEBACK | 🚀 S4 | L | — | — |
| **#32** | What Olivia costs | 🔥 — | S | — | — |
| **#14** | Conversational, not robotic | 🔥 — | M | — | — |
| **#34** | Finalize the QA doc set | 🏁 — | M | — | — |
| — | *— closed, evidence at the bottom —* | | | | |
| **#58** | Cancelled registrations count as attendance | 🔴 S1 | S | n/a (SQL) | ✅ **LIVE** — one chokepoint view |
| **#59** | Same event listed twice (events + partners) | 🟡 S2 | S | n/a (SQL) | ✅ **LIVE** — dossier joins on the row, not the name |
| **#60** | Cancelled side-event wore the Summit's name (app-event mis-link) | 🟡 S2 | S | n/a (sync+SQL) | ✅ **LIVE** — sync dedupe + 5-min alarm |
| **#61** | Schema audit: tables with no declared connections | 🔴 S1 | M | — | — |
| **#62** | Resolve the 17 Security Advisor warnings | 🔴 S1 | S | — | — |
| **#63** | Airtable-formula injection in the Make member-match (census + app v3) | 🔴 S1 | S | — | — |
| **#64** | Runtime inventory: consolidate where logic runs (drift, not the load-bearing splits) | 🔵 S3 | M | — | — |
| **#65** | 🚨 SQL functions exist ONLY in the live DB — no file in git | 🔴 S1 | M | — | — |
| **#66** | Forms warehouse: 5 known gaps (validation · mapping coverage · refresh · units · lag) | 🔴 S1 | M | — | — |
| **#67** | Cohort + trend comparison, per field (panel vs cross-section) | 🟡 S2 | M | — | — |
| **#52** | Follow-ups bind to the wrong topic (the 👎) | 🔴 S1 | S-M | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#53** | Fact-gate false clamp (grounded answer binned) | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#51** | Members-lane fabrication + over-refusal | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#54** | Country dim + regions + geo lists | 🔴 S1 | S | ✅ proven | ✅ **LIVE** `01a94c1a` (holding-delay fix still Andy's to run) |
| **#55** | MDS credits into the billing lane (WA→AT→Supa) | 🔴 S1 | S-M | ✅ proven | ✅ **LIVE** (shared billing fn; Andy's WhatsApp test) |
| **#56** | Partner ranking asks read a sample (Ian) | 🔴 S1 | S | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#29** | THE DOSSIER + PERSONALIZATION LAYER (v1: 5 lanes) | 🔴 S1 | L | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#50** | ENTITY DOSSIERS | 🔴 S1 | M-L | ✅ all 4 lanes | ✅ **LIVE** `7f7b932f` (all four) |
| **#38** | Interactive buttons (CTAs) for offers + links | 🟡 S2 | M | ✅ proven (report confirm-step open) | ✅ **LIVE** `01a94c1a` |

**Staging/Prod key:** ✅ proven = built + probed on that surface · — = not there yet ·
**PROMOTED 2026-08-04 22:35 UTC** — prod `01a94c1a` (was `89ee3632`), 12 nodes. **Second promote 23:13 UTC → prod `65958b77`** (Answer Seed: Andy's live-test fixes — grouping-retry rule + credit-never-links-Stripe). Pre/post snapshots kept in `olivia_snapshots/`. The holding-ladder fix (30s + recheck) is live in `X1vzrW9Avqff3qRa`, which has no staging twin.
**Priority key:** 🔴 S1 now · 🟡 S2 next · 🔵 S3 planned · ⚪ S4 later · 🚀 new data source ·
🔥 standing/measurement · 🏁 closes the sprint.
**Sizes:** S ≈ a session · M ≈ a day · L ≈ multi-day.

---

## 🔁 SPRINT RITUAL — how a sprint opens and closes

1. **Archive** the closing sprint's shipped tickets into `OLIVIA_BACKLOG_ARCHIVE.md` (one archive
   for everything ever shipped, newest first).
2. **Open the next sprint** → `OLIVIA_SPRINT_<n+1>.md`, containing **ONLY the open tickets**,
   carried over with their full story and ACs.
3. **Everything in this header travels with it** — Definition of Done, the target ladder,
   EVERY-MEMBER-ALWAYS, Andy's working rules, this ritual.
4. **Regenerate the ClickUp copy of the handbook** (doc `2531q-103317`) if the handbook changed
   materially — it is the only way anyone without repo access can read any of it.
5. **THE FINAL STAGE OF EVERY SPRINT IS THE RELEASE NOTES** — one merged member-facing doc
   (`OLIVIA_RELEASE_NOTES.md`), drafted by me, validated and posted by Andy. **A sprint is not
   closed until they are written.**

**Structure inside a sprint doc:** sprint goal · at-a-glance table · open tickets with
priority + size + STORY + a plain-English line + ACs · open questions for Andy ·
**CLOSED tickets at the BOTTOM**, moved down as they close, keeping their evidence.

---

## Definition of Done — one list, applies to EVERY item

- **The failure class is counted, before and after.** A rate on the class, not a hand-picked
  question that passed.
- **No class is traded for another.** The rates it was not aiming at do not get worse.
- **The safety gate is GREEN** wherever retrieval or data access changed.
- **Proven on the live system**, with the evidence cited — execution id, SQL result or gate output.
  Never "should work".
- **Every lane it touches, or the exceptions are named in writing.**
- **Written down the same session:** what shipped, what was measured, what is still open.

**Target ladder:** under 10%, then under 5%, then **under 1% wrong**. *Currently at 1.7%.*

**EVERY MEMBER, ALWAYS:** a data job's population is ALL active members, keyed by `at_member_id`
from `member_attributes` — never "members with a phone/WhatsApp". Phone, email and WA are channels
and resolution keys, not the population. A job that must cover a subset names the subset and the
reason in writing.

**THE SMOKE runs once per sprint, never per ticket** — it is the sprint's exit exam and the formal
instrument for every class rate. Per-ticket proof is probes plus the gate.

---

### #57 · The live-test trio — empty reports, wrong-turn "Yes", buttons that say "reply"
**🔴 S1 · size M — filed AND built 2026-08-04 from Andy's own WhatsApp session**

> **In plain words:** "I want to report a bug" filed an empty report; tapping Yes answered a different question; and the message said "reply YES" while showing buttons.

*As a member, a report is only filed once I have actually said what it is and confirmed it —
and when I reply to a specific message, the answer continues THAT conversation.*
**Live evidence (prod, 23:13–23:14 UTC):** `I want to report a bug` → filed instantly with that
sentence AS the report body (msg 24151, report row saved) · the real detail `Cant register to
event` then became a NEW events question (24157) · a tapped **Yes** replayed an unrelated credit
answer (24163) · the body read "reply *YES*" under tap buttons.
**Honest note on the third one:** the wrong-turn Yes was **partly self-inflicted** — prod probes
were firing into Andy's own thread at those minutes and twice sent "new question", resetting his
context. Standing rule now: **never fire probes at prod against a real member's number.**
**Accept when:** an intent-only report files NOTHING · the detail message becomes the report BODY ·
nothing is filed until an explicit confirm · a quoted reply binds to the quoted turn in plan AND
prose · button bodies never say "reply YES" · gate GREEN.

#### ✅ BUILT + STAGED + PROVEN 2026-08-04 — awaiting promote
**① Report flow is now CANNED end-to-end** (a prompt rule was tried first and did not hold —
staging 24168 still answered the detail as an events question). Three deterministic states in
`Plan Request` + `Build Verbatim Digest`: `report_ask` → "*What would you like to report?*" and
files nothing · `report_draft` → quotes their words back behind the fixed marker *"Ready to send
this to the MDS team:"* with **Send it · Add more · Cancel** · confirm → `report_create` with the
drafted text. **② Quoted-reply binding**: `Log Inbound` keeps `context.id`, history carries
`wamid`, `Prep Context` replays the QUOTED turn's plan and passes its text so the answer
continues that thread. **③** the send layer rewrites "reply *YES*"/"or *NO*" to "tap *Yes*"/"tap
*No thanks*" whenever buttons attach.

| AC | result |
|---|---|
| intent-only files nothing | ✅ "I want to report a bug" → asks what to report, route `report_ask`, no report row (msg 24175) |
| detail becomes the body | ✅ "Cant register to event" → route `report_draft`, quoted back for confirmation (24177) |
| nothing filed until confirm | ✅ "Send it" → report row **`report_text = "Cant register to event"`** (was: "I want to report a bug") |
| quoted reply binds to the quoted turn | ✅ quoted "Yes" on an older Cyprus turn, with a NEWER events turn present → plan `period=match, p_country=Cyprus` **and** prose "Here's the Cyprus list: Nacho Nachelis…" (24195) |
| button wording | ✅ offline proof: "I can *open a ticket…*. tap *Yes* to open it, or tap *No thanks*." |
| gate GREEN | ✅ 224 exit-0 |

**PROMOTED 23:36 UTC → prod `955ed56f`** (7 nodes; in-promote gate green; prod-verified: intent → asks (msg 24197) · detail → draft (24199) · Send it → report row **"Cant register to event"**).
**Named remainder:** ~~the confirm reply still appends a soft follow-up offer~~ **CLOSED 2026-08-05
(staging `eb4dc393`, awaiting promote)** — see *#57b* below. Quoted-reply binding cannot be probed
through the silent path (no outbound wamid exists there) — proven by stamping a wamid on a probe
row, then cleared. Staging `a1b060c2`.

#### ✅ #57b — the two named remainders, BUILT + STAGED + PROVEN 2026-08-05 (awaiting promote)
**① The report confirmation stops clean.** The seed rule ("confirm in one warm line and STOP")
kept losing to a trailing soft offer, so the same remedy as the rest of #57 applies: it leaves the
model's hands. `Format Reply` clamps the reply on a `period === 'report_file'` turn — **but only
when `report_create` actually appears in `sources_used`**, so a failed filing can never be
reported as a success. **② "who is FORM africa?"** (#54's residual) hunted a member named *Form
Africa* and honestly declined, while the correctly-spelled question answers fine. `Resolve Member`
now normalises `form` → `from` where a preposition is grammatically required — one point, because
every consumer (router, plan, loop) reads its text from there; the member's verbatim words still
persist, since `Save Conversation` files `Log Inbound`.text.

| AC | result |
|---|---|
| the typo reads as the preposition | ✅ "who is form africa?" → "*Benjamin*, in Grand Baie, Riviere du Rempart" — same answer as the correctly-spelled question (was: "I don't have anyone named \"Form Africa\" on file") |
| a real form is never rewritten | ✅ offline harness against the SHIPPED node (`test_57b_typo.js`): **20/20** — 8 rewritten · 8 form-nouns preserved ("the signup form is broken", "form a company", "where are form submissions going") · 1 accepted limit asserted in the open · 3 no-ops |
| confirm stops clean | ✅ "Send it" → "Sent to the MDS team 👍 They will see it in their portal." and nothing else (was: + "if you tell me which event…") |
| nothing claimed unless filed | ✅ `digest.olivia_reports` id **28** `report_text = "Cant register to event"`, written by that turn |
| gate GREEN | ✅ **224 checks, 0 FAIL** |

**Not promoted** — staging `eb4dc393`, prod `7f7b932f`. Apply script
`scripts/olivia_loop/apply_57b_report_stop_geo_typo.py` (idempotent; re-running swaps a revised
guard in place).

---

# 🔴 S1 — NOW

### #65 · 🚨 THE SQL LAYER IS NOT IN VERSION CONTROL — single point of failure
**🔴 S1 · size M — filed 2026-08-06 · ⚠️ HUGE RISK, DOUBLE-CONFIRM BEFORE ANY REMEDIATION TOUCHES THE DB**

> **In plain words:** ~75 database functions run the retrieval, the gating and the stats — and not
> one of them exists as a file anywhere. They live only inside the live production database.

*As the owner, every line of logic that runs MDS can be read, reviewed and restored from the
repository — nothing exists only inside a running system.*

**Verified 2026-08-06:** `find` across the repo returns **zero `.sql` files**. The only record of
any function is (a) the live `pg_proc` catalog and (b) Supabase's `supabase_migrations` history,
which is itself inside the same database. There is no second copy anywhere.

**Why this is the biggest risk on the board — what it costs today:**
- **No restore path independent of the database.** If the project is lost, misconfigured, or a
  migration corrupts a function, the source is gone with it. Supabase backups protect the DB — they
  do not give a diffable source tree, and a backup restore is all-or-nothing.
- **No code review.** Every migration this session went straight to production logic with no diff
  anyone could read. A `drop function` + `create` typo has no reviewer between it and members.
- **No diff between environments.** Staging vs prod n8n has a version id and a snapshot ritual; the
  SQL layer has neither — "what changed" is only answerable by dumping `pg_proc` and eyeballing.
- **No blame/history.** Which ruling produced which clause is reconstructible only from session
  logs, not from the code.
- **The security boundary is in the unversioned layer.** Access rules, owner-gating, small-cell
  suppression and the active-member checks all live in these functions. The leak gate proves they
  hold TODAY; nothing proves what they looked like last week.

**Architecture ruling to record with it (Andy's 3-tier question, 2026-08-06):** the functions are
NOT misplaced — data access + access control belong in Postgres because it is the last hop before
the data and FOUR consumers share it (n8n, Python scripts, GitHub Actions, digest-web); moving the
gate into one app leaves the other three unguarded, and moving retrieval out means pulling 38k rows
over the wire and losing HNSW-in-query. Genuine tier violations are small and named:
`olivia_alarm_fire` posting to Slack from inside Postgres (deliberate — alarm independence; record
as an accepted exception) and `member_event_url` doing URL/presentation shaping in SQL. **Fix the
source-of-truth problem, do not relocate the compute.**

**Proposed remediation (DO NOT START WITHOUT ANDY'S EXPLICIT SECOND CONFIRMATION — this touches the
layer that gates every member's data):**
1. **Read-only first.** Dump every `digest` function/view/policy to `db/functions/*.sql` from
   `pg_get_functiondef`. Pure export; the database is not modified. Commit as the baseline.
2. **Drift check in CI** — a job that re-dumps and fails if the repo and the live DB differ. Still
   read-only; catches an out-of-band change within a day.
3. **Only after 1+2 are green and stable:** decide whether future changes flow repo→DB (apply from
   file) or DB→repo (export after migration). The repo→DB direction is the safer end state but is
   also the only step that can break production — it needs its own proof plan, the leak gate green
   before and after, and a rollback rehearsed.
4. Handbook section: the tier rule + the two accepted exceptions above.

**Accept when**
- Every `digest` function, view and policy exists as a file in git, byte-matched to the live DB.
- A CI drift check runs and demonstrably fails on an injected difference (proven, not assumed).
- The tier rule and its exceptions are written in the handbook.
- Gate GREEN before and after every step; no RPC behaviour changed by the export.

---

### #66 · Forms warehouse — the 5 known gaps
**🔴 S1 · size M — filed 2026-08-06. Architecture is CORRECT (Andy confirmed); these are gaps
inside it. Fixing any of them changes nothing about the two tables.**

> **In plain words:** The forms warehouse works. Five things inside it are unfinished, and I found
> all five myself — before they found us.

*As the owner, the forms warehouse validates what it stores, compares every question it can, and
scales past today's volume without a rebuild.*

**① No validation at write — junk lands as-is.** Audit found **2 `ttm_revenue` values ≥ $1B**,
**1 `projected_revenue` ≥ $1B**, **2 `ttm_revenue` = 0** on active sellers, **1 `num_kids` > 12**.
Medians and the p10–p90 range absorb them today, so no answer is visibly wrong — but a mean or a
small slice can be. Fix: a validation pass at load (flag, never silently drop — a real 0 and a typo
0 must stay distinguishable), plus a per-field plausibility rule set Andy ratifies.

**② `form_field_map` coverage is the real scaling risk.** 28 mappings over **~150 distinct
questions** across 5 forms. Anything unmapped cannot be compared across forms or years — it still
answers within its own form, so the failure is silent. Mapping is hand-curated and grows with every
form added. Fix: coverage report (which questions have no canonical key, ranked by respondents),
finish the high-value ones, and a rule that a new form's mapping ships WITH the form, not after.

**③ Matview refresh is a full rebuild.** `form_answers_exploded` = 111,282 rows today, rebuilt
whole on every load — fine now, expensive at 50k+ submissions. Fix: incremental refresh keyed on
new/changed tokens.

**④ `canonical_key` is a flat namespace — no units, no declared type.** Revenue-in-USD vs
revenue-in-local-currency, monthly vs annual pay, percent vs absolute would collide silently under
one key. Nothing collides TODAY; the next form could. Fix: units/period in the map (or in the key),
asserted by the QA sweep.

**⑤ Warehouse lags Airtable by up to a day.** AT is instant via webhook; the ledger tops up on the
13:47 UTC Action. Deliberate, but undocumented — a member who answers at 14:00 is invisible to
Olivia's stats until the next day. Fix: either document as accepted, or trigger the loader from the
same webhook.

**Accept when**
- Implausible values flagged with a ratified rule per field; nothing silently dropped; before/after
  counts on every affected stat.
- Coverage report exists; every question above a respondent threshold either mapped or ruled
  not-comparable in writing.
- Refresh is incremental, proven on a real load (timing before/after).
- Units/period declared and sweep-asserted.
- Lag documented or removed.
- QA sweep + gate GREEN after each.

---

### #61 · Schema audit — most warehouse tables show NO connections, and nobody has written down why
**🔴 S1 · size M — filed 2026-08-06 from Andy's Schema Visualizer review (do not act; research first)**

> **In plain words:** Open the Supabase schema map and most tables float alone — no lines. Are the relationships real and just undeclared, or are some tables genuinely orphaned?

*As the owner, every table in `digest` either declares its relationships, or carries a written
reason why it deliberately does not — no silent islands.*

**What the visualizer shows (Andy's screenshot + schema dump):** only a handful of true FKs exist
(`wa_messages.sender_member` · `member_sessions.member` · `member_events.member` ·
`olivia_messages.member` — all → `members.airtable_id`; `fb_comments.post_id` → `fb_posts`;
`partner_reviews.partner_id` → `partners_catalog`; `video_files.video_id` → `videos_catalog`;
`olivia_question_labels.message_id` → `olivia_messages`). **Everything else joins on undeclared
text keys** — `at_member_id` across ~15 tables (member_attributes, member_profiles,
member_expertise, member_niches, member_personas(+history), member_profile_embeddings,
member_state_snapshot, event_registrations, form_responses, fb_member_map, olivia_reports/requests,
billing_nudges…), `event_at_id` → events_catalog, `chat_id/chat_name` → chats,
`summaries.chat_name`, `member_edges.a_id/b_id`, `entity_dossier.entity_id` (polymorphic),
`content_items.source_id` (polymorphic), wamid keys (olivia_sends/seen/feedback), and the
`canonical_key` layer in form_field_map.

**Research questions (the ticket's actual work):**
1. Per table: what is its implicit relation set, and WHY is it undeclared? Known legitimate
   reasons to document: sync-order independence (mirrors land before/after each other),
   partially-stamped keys (`member_at_id` NULL until matched — FK would reject honest unknowns),
   polymorphic keys (entity_dossier, content_items), append-only ledgers, cross-system IDs
   (wamid, fb_uid, app ids). A FK that forces guessing violates the never-guess rule.
2. Which relations COULD safely become real FKs (and with what ON DELETE behavior) without
   breaking the sync jobs? Candidates to test: event_registrations.event_at_id,
   member_expertise/niches/personas/embeddings → member_attributes.
3. Orphan audit — count rows whose implicit parent is missing, per relation (the real risk the
   diagram hides). Decide per case: backfill, delete-as-junk (never a real member), or accept.
4. Two members tables (`members` = WA layer keyed airtable_id vs `member_profiles`/`member_attributes`
   keyed at_member_id) — document the dual-key spine once, in the handbook AND as table COMMENTs
   the visualizer can show.
5. Deliverable: `FORMS_ERD.md` extended to the FULL digest schema (every table placed, every
   implicit edge drawn) + table COMMENTs in the DB + a handbook section; any FKs actually added
   ship with sync-job proof (full re-run green) + gate green.

**Accept when**
- Every `digest` table appears in the ERD with its edges (declared or documented-implicit).
- Orphan counts measured per relation, each with a ruling (fix / accept / junk-clean).
- FKs added only where the sync jobs provably tolerate them; everything else carries a written
  reason in a table COMMENT.
- Gate GREEN; no sync job broken (next scheduled runs all succeed).

---

### #62 · Security Advisor: 17 warnings — resolve every one or rule it accepted in writing
**🔴 S1 · size S — filed 2026-08-06 from Andy's Advisors review (do not act; ticketed)**

> **In plain words:** Supabase's own security scanner shows 17 warnings. Clear the board.

*As the owner, the Security Advisor shows zero unexplained warnings — each is fixed, or its
acceptance is written down where the next person will look.*

**The 17, by class (from the dashboard):**
1. **Function Search Path Mutable ×12** — older `digest` helpers created without a pinned
   `search_path` (`olivia_touch`, `member_partner_url`, `member_event_url`,
   `immutable_text_array_join`, `attr_clean`, `expertise_query`, `name_fold`, `member_video_url`,
   `partners_embed_invalidate`, `events_embed_invalidate`, `member_personas_archive`,
   `is_active_member_status`). Fix = `ALTER FUNCTION … SET search_path = 'digest','pg_temp'` (the
   pattern every NEW function already uses). ⚠️ `immutable_text_array_join` feeds two generated
   tsvector columns — verify pinning does not invalidate the generated columns before touching.
2. **SECURITY DEFINER callable by public / signed-in ×4** — `public.auth_org_ids()` and
   `public.rls_auto_enable()`. Neither is a digest function; research what installed them (an
   extension or template?), then `REVOKE EXECUTE FROM anon, authenticated` unless something
   client-side genuinely calls them.
3. **Leaked Password Protection Disabled ×1** — Auth setting (dashboard toggle, Andy's click);
   only relevant if password auth is used anywhere (portal is OTP-based — may be a one-line
   "accepted: no password auth" ruling instead).

**Accept when**
- Advisor re-run shows **0 warnings**, or each remaining one carries a written acceptance in the
  handbook §security.
- All 12 pinned functions proven live after the change (leak gate 232 + one smoke call per
  touched RPC; the two embed-invalidate triggers fire on a real row).
- The `public.*` functions' origin identified before any revoke; revoke verified not to break the
  portal/app login flows.
- Gate GREEN.

---

### #63 · Injection audit verdict — SQL clean; ONE real injection found in the Make member-match
**🔴 S1 · size S — filed 2026-08-06 from Andy's "double check for SQL injection" (audited, not fixed)**

> **In plain words:** The database itself is injection-clean. But the form-to-Airtable member
> matching interpolates the TYPED email into an Airtable formula string — a crafted email can
> break out and force a match to the wrong member.

*As the owner, no user-typed value ever reaches a query language un-escaped — SQL, Airtable
formula, or anything else.*

**Audited clean (SQL proper):**
- **Zero dynamic SQL** in the whole `digest` schema — no function contains `EXECUTE` or
  `format()` (verified against `pg_proc`). Every RPC binds user text as parameters; the model's
  tool arguments hit typed RPC params through PostgREST — no path composes SQL from input.
- `ILIKE '%'||input||'%'` patterns (form_stats, event lanes) = LIKE-wildcard nuisance only
  (`%`/`_` widen a match), not injection.

**The finding:** both Make member-match modules build an Airtable `filterByFormula` by string
interpolation — `LOWER({Preferred Email})=LOWER("{{2.Email}}")` — in **census scenario 4860042
(module 3)** and **app v3 scenario 4784286 (module M4)**. A typed email containing a double quote
breaks out of the formula string; a crafted value can force the search to match an arbitrary
member, so the attacker's Forms row LINKS TO ANOTHER MEMBER — and their fake revenue becomes that
member's `Most Recent Revenue` (data poisoning, not just leakage). Partial shield today: Typeform
email validation likely rejects quoted-local-part emails — but RFC allows them, and the shield is
upstream of us, not ours.

**Fix (when worked):** escape in the Make expression — `substitute()` the double quote (or strip
non-email-safe chars) before interpolation, in BOTH scenarios; prove with a quote-bearing email
through staging-safe replay (never a live member). Secondary nuisance, same ticket or note:
`to_tsquery('english', p_query)` throws on unbalanced quote syntax (honest error, no injection) —
consider `websearch_to_tsquery` for the two lookup fns if eval ever shows user-visible failures.

**Accept when**
- A double-quote-bearing email can no longer alter either formula (proven by replay against the
  census scenario; app v3 fix verified by module inspection + one controlled test submission).
- No other interpolation-into-query-language sites exist (grep both blueprints for `{{` inside
  `formula`).
- Gate GREEN; both scenarios' next real submissions process normally.

---

### #64 · Runtime inventory — write down where every job runs and why, then move only the drift
**🔵 S3 · size M — filed 2026-08-06 (Andy: "why is the app logic scattered between so many places")**

> **In plain words:** Work runs across Postgres, n8n, Make, Vercel, Render, GitHub Actions and
> Python on Andy's Mac. Some of that is deliberate; some is history. Write it down, then fix only
> the history.

*As the owner, I can name where any piece of MDS logic runs and why it lives there — and nothing
critical depends on a laptop being awake.*

**Deliberate, keep (document, do not move):** retrieval / gating / stats in **Postgres** (set
operations over 40k+ rows with vector search, and the security boundary the leak gate proves —
app-layer filtering could be bypassed) · the alarm in **pg_cron + pg_net** (an alarm inside the
system it watches is worthless; the launchd watchdog covers Supabase itself being down) · the
WhatsApp workflow in **n8n** (Meta webhooks, retries, the tool-calling loop) · the Claude-vision
revenue verifier on **Render** (long-running + file handling; fights Vercel's serverless model).

**Drift, candidates to consolidate:**
1. **Make vs n8n** — Make runs ONLY the Typeform→Airtable form syncs (app v3 `4784286`, census
   `4860042`); n8n runs everything else. The census one was mirrored from app v3 out of
   consistency, not conviction. Decide one home for form syncs; note Make's webhook fragility and
   that both scenarios carry the #63 injection.
2. **launchd Python on Andy's Mac** — FB engagement job, `alarm_watchdog.py`, ad-hoc scripts. Same
   class of work runs on GitHub Actions elsewhere (member-profiles-sync + its 3 steps). A sleeping
   laptop silently stops these. EXCEPT the watchdog, whose whole point is being outside Supabase —
   it needs an off-Supabase, non-laptop home, not a GH Action in the same cloud.
3. **Vercel + Render for one app** (`mds-digest-web`) — one codebase, two hosts, two deploy
   stories, two env-var behaviours (Render needs a MANUAL redeploy on env change).
4. **Two schedulers for nightly derivations** — GH Actions vs n8n vs pg_cron; pick per job class.

**Deliverable:** one table in the handbook — job · runtime · trigger · why-here · owner · what
breaks if it stops — covering every scheduled or triggered piece; then a short move-list with each
migration proven by a real run (never "should work").

**Accept when**
- Every scheduled/triggered job appears in the inventory with a written why-here.
- Nothing business-critical depends on Andy's Mac being awake (watchdog explicitly re-homed or
  ruled as accepted with its reason).
- Each move proven by a live run, old path disabled in the same session (no double-running).
- Handbook updated; gate GREEN.

---

### #67 · Cohort and trend comparison — per field, panel AND cross-section
**🟡 S2 · size M — filed 2026-08-06 (Andy: "comparing last year's cohort to this year's, on every single field")**

> **In plain words:** Show how any answer moved year over year — and be clear whether that's the
> same people changing, or a different crowd answering.

*As a member, I can ask how the community changed on any question and get an answer that says which
comparison it used.*

**What already exists:** `form_responses` is append-only, every submission timestamped — the event
log is real, no new storage needed. Panel depth measured 2026-08-06: **386 members have answered in
2+ years** (169 two · 123 three · 84 four · 10 five), 295 in one year only. Per-year respondents:
2022 364 · 2023 337 · 2024 316 · 2025 263 · 2026 107 (still collecting).

**What is missing:** nothing compares two windows. `form_stats` takes one `p_since`/`p_until` at a
time; a year-over-year answer today is two calls plus arithmetic, and Olivia has no tool for it.

**The trap the design must handle:** 2025 had 263 respondents, 2026 has 107 — a naive comparison
mixes real change with **who happened to answer**. Two different questions, two different numbers:
- **PANEL** — the same members who answered both years: "of the 386 who answered twice, revenue
  moved X%". Measures actual change.
- **CROSS-SECTION** — everyone in each window: "the 2026 cohort's median vs the 2025 cohort's".
  Measures the community as it stands, composition shift included.
The answer must state which it used, never blend them silently.

**Field coverage:** same form across years compares on ref alone (evergreen census — every question
works, no mapping needed). Across different forms (legacy 2022 census vs census 2026) needs a
canonical key — **28 mapped of ~150 questions**, so back-comparison is partial until #66 ② lands.
The tool must say when a field cannot be compared rather than return a half-answer.

**Shape (proposed):** `form_trend(p_phone, p_question, p_from, p_to, p_mode)` where mode = panel |
cohort, returning per period: median/avg/% distribution, the delta, and the comparison basis; same
suppression rules as `form_stats` (percent not counts, cells under 3 dropped, n internal). Plus the
loop rule: any "how has X changed / compared to last year" question routes here.

**Accept when**
- Panel and cross-section both available, and the spoken answer names which was used.
- Any field comparable within one form across years; unmapped cross-form fields say so explicitly
  instead of half-answering.
- Suppression rules identical to `form_stats` (verified by the QA sweep, extended to cover trends).
- Probed on real questions ("how did revenue change from 2022 to 2026", "are members hiring more
  offshore than last year") with answers matching SQL truth.
- Gate GREEN.

---

# 🟡 S2 — NEXT

### #18 · How-MDS-works answers
**🟡 S2 · size M · ⛔ BLOCKED (Andy 2026-08-05: "we dont have data for #18")**

> The ACs below already said it: *the work is someone writing the answers.* Those written answers
> do not exist, so there is nothing to load. **Unblocks when the team writes them** — or when #35
> (GroupOS documents) lands and the answers turn out to live in there.

> **In plain words:** She can answer “how does MDS work” questions — policies, processes, what's included — instead of passing them to the team.

*As a member, I get the real answer about Squads, programs and joining a chat.*

**Accept when**
- **Every recurring how-MDS-works question has a written answer from the team.**
- **Each answers consistently across phrasings and cites that source.**
- **They stop arriving as support requests.**

From the team's own documents rather than inferred from chat chatter. Also unblocks the chapter policy
questions in #9.

**Effort M** — the work is someone writing the answers; loading them is straightforward. **Impact:** all 722; every one of these currently becomes a support request.

### #19 · Privacy: share, keep, delete
**⚪ S4 · size M — DEMOTED S2 → S4 (Andy 2026-08-05: "skip it, its like s4 priority")**

> **In plain words:** A member can ask what Olivia knows about them, and control it.

*As a member, I know what's stored about me and can have it removed.*

**2026-08-03: first AC drafted → `OLIVIA_PRIVACY_POLICY_ADDITIONS.md`** — 6 paste-ready
amendments to mds.co/privacy-policy (live policy of 2025-06-03 has ZERO mention of AI /
community-content processing / activity analytics): new data categories · an "AI-Assisted
Services" section (processors = Anthropic + Voyage, no-training, profiling disclosure,
group-visibility rule) · processor-list update · retention number **[X — Andy must choose]** ·
deletion + STOP rights via appsupport@ · international transfers. Counsel notes included.
**Still open:** counsel review + publish · the deletion RUNBOOK (delete across olivia_messages /
content_items / member_events / embeddings, verifiable) · retention number stated.

**Accept when**
- **A written position exists:** what may be shared, with whom, and how long conversations are kept.
- **A deletion request is honoured and verifiable.**
- **Opt-outs are respected everywhere the data appears.**
- **Nothing promised to members contradicts it.**
- A written position on what Olivia may share about a member, with whom
- How long conversations are kept (Andy's instinct: forever — needs stating, not defaulting)
- A member can ask for their history to be deleted, and it happens
- Consistent with what the beta email already promises

**Impact:** all members, low urgency until someone asks.

---

# 🔵 S3 — PLANNED

### #20 · Census into the warehouse
**🟡 S2 · size L — UNBLOCKED 2026-08-06 (census launched, 49 responses day one) · BUILT + STAGED +
PROVEN same day — awaiting Andy's promote. Persona AC still open.**

**Data layer (shipped outside the workflow):** `digest.form_responses` (2,308 submissions across
census 2026 + app v3 + honorary + both legacy censuses, 90% member-stamped, daily GH-Action sync)
+ `form_answers_latest` (latest answer per member × form × ref = the decay axis) + two gated doors:
`form_stats` (aggregates only, **groups under 3 members suppressed in SQL**, group_by
country/state/niche/rev_band) + `my_form_answers` (asker's own rows, self-only by construction).

**Loop (staging `1dd2f39b`, apply `scripts/olivia_loop/apply_20_census_lane.py`):** both tools
taught + census rule (census asks = form_stats never content_search · never another member's
individual answer · absent = never shown = UNKNOWN, not "No" · lead with median on wide spreads).

**Evergreen v2 (same day, Andy's six rulings):** `form_field_map` — canonical keys are DATA
(28 mappings seeded: revenue trio + YoY, channel %s, niche, products, brands, kids across census
2026 / app v3 / legacy censuses / honorary), so a new form = INSERTs, never new columns.
`form_stats` v2: returns **every matching question** (a "revenue" ask = TTM + projected + prior +
YoY rows, never a silent pick) · **time windows** (`p_since`/`p_until` — "2026 census" = answers
GIVEN in 2026; evergreen form, same member yearly) · cross-form unification (omit `p_form_id`) ·
**counts stay internal** (n= marked INTERNAL in detail; spoken only when the ask IS a count).
`form_field_history` — the asker's OWN field over time, oldest-first (append-only ledger = the
event stream; proven: a member's ttm_revenue 20M in the 2022 legacy census → 30M in census 2026).
Staging `725e2366` (`apply_20b_census_evergreen.py`). Re-probe: "avg revenue according to Census
2026" → **TTM median $6.38M + projected median $10M, both windowed to 2026, no member count
spoken, median-first**. Gate **232** exit-0 (anon + canceled denied on all three doors).

**Staged proof — the exact question from Andy's prod screenshot:** *"what is the avg revenue
according to Census 2026"* → **"the median TTM revenue among the 42 members who answered is $5.83M
… the raw average comes out to about $29M, but I'd trust the median far more"* — numbers = SQL
truth exactly (n=42, median 5,833,071, avg 29,019,432), median-first per the tool hint. Owner lane:
"what did i say on my census?" (Andy, no census on file) → honest empty + offers the application.
**Gate 226 → 230** (anon denied on table, view, and both RPCs; canceled member gets zero rows from
both). Remaining for full close: **personas draw on census** (dossier/persona derivation) + promote.

> **In plain words:** Census answers become searchable, so questions about what members sell and where become answerable.

*As a member, Olivia knows what I actually said about my business.*

**Accept when**
- **A member's own census answers are answerable to them.**
- **0% of anyone else's raw answers ever return**, enforced by the gate.
- **Persona questions draw on census data** rather than tick-box filtering.

The freshest self-reported revenue, channel and SKU data MDS holds, currently not in the warehouse at
all. Unblocks member personas — what turns matching from tick-box filtering into "who has actually lived
through this".

**Impact:** all 722; the biggest single quality lever left.

---

### #35 · Connect new data source — DOCUMENTS (GroupOS)
**⚪ S4 · size M — DEMOTED S3 → S4 (Andy 2026-08-05: "#35 is s4 as well")**

> **In plain words:** MDS documents become a source she can search and cite.

*As a member, MDS documents are searchable like everything else.*
Extract via the GroupOS MCP document endpoints (documents_list/get, collections, categories —
already exposed on the connection). Same pattern as videos/partners: catalog + gated retrieval +
restriction handling + embeddings + gate checks. Filed by Andy 2026-08-01.

### #17 · Auto-refresh videos and partners
**🔵 S3 · size M**

> **In plain words:** Videos and partners refresh themselves instead of needing a weekly manual pull. **Blocked on Andy's GROUPOS_PAT.**

*As a member, new recordings and deals show up without anyone importing them.*

**Accept when**
- **Blocked until the GroupOS key exists.**
- **New videos and deals appear without an import**, and data older than a day alerts.
- **The requirements are handed over, the security exposure included**, and it is fixed or owned in writing.

13 videos landed in a week and none surfaced in any catch-up; partner data sits on a frozen snapshot.
Needs the GroupOS key. Includes sending GroupOS the 13-item requirements doc — one of which is a live
security exposure: restricted decks are publicly downloadable.

**Effort M** — blocked on a key we don't have. **Impact:** everyone asking what's new; the security item is urgent on its own terms.

---

# ⚪ S4 — LATER

### #48 · AT roster write-back — fix member↔ticket mapping at the SOURCE
**⚪ S4 · size S-M**

> **In plain words:** Write the member↔ticket links we worked out back into Airtable, so the team's own view stops lagging what we know.

*As the team, Airtable's Event Roster shows the same member↔ticket links the warehouse proved —
the operative view stops lagging what we know.*
Filed from #45: Airtable's "Match to Member" was blank on 6,783 roster rows; our second-pass
matching recovered **2,398 links the AT matcher missed** (different-email buyers + no-email
orders name-matched). Today those links live ONLY in the warehouse. **Build:** ① write the
recovered links back to `Event Roster.Match to Member` — fill BLANKS only, never overwrite an
existing link, batch via AT API (link-record writes are fine; it's lookup FIELD creation the API
can't do) · ② harden the AT-side matcher so future orders link at capture (match on ANY member
email incl. Preferred, not just the primary) · ③ leave genuine non-members blank (4,071
evidenced guests/partners/public buyers). **Accept when:** AT blanks ≤ the non-member set ·
spot-check 20 written links against the warehouse · no existing link changed · documented in the
automations registry.

#### 2026-08-05 — ② IS DROPPED, AND THE TICKET'S PREMISE WAS OVERSTATED (measured)
**Andy pushed back: "the system is working until you come in… I haven't heard from the event team
any complaints."** He was right, and the measurement says so. Cut 2026 the way he asked — member
tickets separated from guests, since a guest legitimately has no match:

| 2026 ticket kind | rows | linked | blank |
|---|---|---|---|
| **MEMBER ticket** | 940 | **910 (97%)** | 30 |
| guest / partner | 575 | 197 (34%) | 378 |
| undeclared ("Standard"/blank type) | 2,413 | 1,182 (49%) | 1,231 |

**On member tickets the AT matcher is at 97% — 30 blanks in a year.** The headline "30-40%
unmatched" is guests plus ticket types that never declare member-or-guest. Nothing is broken.

**② dropped on evidence, not opinion** (`scripts/event_roster_match_gap.py`): of the links written,
**70.1% would have matched on the existing `{Preferred Email}` formula**, and adding Stripe
Customer Email + Associated Emails would have caught **2 more rows out of 562**. Widening the
search on Make scenario **4270329** buys nothing and is not worth a change to a live automation.
The remainder are 437 orders carrying no email at all and 123 on a genuinely different address —
neither is a formula problem. **The Make scenario was NOT touched.**

**① stands as ENRICHMENT, not repair** — the links are real (independent spot-check, Airtable-only,
deliberately not asking the warehouse that produced them: **25/25 supported — 20 email-exact,
5 name-exact on rows carrying no email, 0 unsupported**), and they fill blanks the AT matcher was
never going to catch. 1,900 of 2,446 written; the last 546 need Andy to run
`python3 scripts/event_roster_match_writeback.py --apply` (the session classifier blocks the write
for me, same as `promote`). ③ satisfied: 5,715 evidenced non-members left blank, untouched.
**Root cause of the 30 NOT chased** — 30 blanks a year does not earn the work.

**Noted in passing, not actioned:** Airtable's roster holds **20,538 rows to the warehouse's
17,802**, so the warehouse sync trails by ~2,700 rows.

### #36 · Connect new data source — CIRCLEBACK
**🚀 S4 · size L**

> **In plain words:** Meeting notes become a source. **Blocked on Andy's Circleback details.**

*As a member, what was said in recorded meetings becomes part of what Olivia knows.*
Circleback (meeting notes/transcripts). **BLOCKED: needs details from Andy** — which workspace,
what API/export access, which meetings are in scope, and the sensitivity rules (who may see
what). Filed by Andy 2026-08-01.

---

---

# 🔥🏁 STANDING — measured at the sprint close

### #32 · What Olivia costs — measured AT the smoke, INCLUDING a Kimi cost comparison
**🔥 — · size S**

> **In plain words:** What Olivia actually costs to run, measured at the smoke, including whether a cheaper model would do.

**ANDY'S DECISION (2026-08-01): "let's skip #32 and do it with the full smoke test. We will
measure spend and COMPARE IT TO KIMI AI, and we will give Kimi a fair chance and try to improve
things."** Concretely, at the Big Smoke (§G of the QA checklist):
- **Per-answer + per-month spend MEASURED** from the runs' token counters (`in_tok`/`out_tok`/
  `cache_w`/`cache_r` already ride every exec), split member traffic vs eval traffic.
- **Kimi COST comparison on the same runs** — not sticker prices: $/answer on our real cached
  shape, side by side with Claude (last measured: Kimi 2× $/answer despite cheaper tokens,
  because 4× output + 1.6× tool calls — re-measure fresh).
- **A fair Kimi retest + improvement attempts**: re-check the two blockers first (forced
  thinking-on; no `tool_choice: required` → our forced first fetch unenforceable); try to work
  around them honestly (prompt-level forcing, output caps); same bar as #22 — organic score ≥
  current, gate GREEN, latency in band, kill switch exercised. Harness exists
  (`kimi_harvest/kimi_bench/bench_compare.py`, ~$5.50 last time).
- **Spike alarm** — a day over threshold reaches a human (plumbing = the #13 alarm, one more
  signal once spend is persisted).
- **Balance PRE-warning** (from #13's residual) lands here too.
- **REPORTED TO PAVEL** — measured numbers + the Kimi verdict; Andy sends (drafts confirmed
  first).
*(Historical spend table + projections: see the session logs of 2026-07-31 (PM); baseline
$0.0135/answer Sonnet vs $0.0270 Kimi, ~$3.70/mo today, ~$110/mo at 748 actives.)*

### #14 · Conversational, not robotic — its ACs are the smoke's acceptance criteria
**🔥 — · size M**

> **In plain words:** Does she still sound human rather than robotic — judged at the smoke, not guessed at.

**ANDY'S DECISION (2026-08-01): "#14 sounds like AC for the smoke test" — not a build ticket.**
Written 2026-07-28 about the pre-loop system; the loop + #2/#5/#6/#7/#8 absorbed the concrete
bullets. At the Big Smoke it is checked as: follow-up class rate on the FULL run ·
capped-answer-continues probes · uses-what-she-knows probes · **Andy's own feel verdict**
("it feels like a bot" was his original complaint — he judges whether that's gone). Anything
still robotic becomes a NAMED FIX before the promote.

---

### #34 · Finalize the QA doc set — THE LAST TICKET, runs after everything else
**🏁 — · size M**

> **In plain words:** The QA documentation set, finished last so it describes what actually shipped.

*As the team, once the whole backlog is done, the three QA docs are true, complete, and
reconciled — and the Big Smoke has actually run against them.*

**Andy 2026-08-01: "finish the backlog, THEN revise these docs." This is that revision — the
deliberate last step, not done piecemeal.** The three docs
(`OLIVIA_QA_CHECKLIST.md` = method · `OLIVIA_BIG_SMOKE_MATRIX.md` = content ·
`OLIVIA_SMOKE_CHECKLIST.md` = 5-check gate) were built while the backlog was still closing, so
the METHOD is whole-backlog-shaped already but the MATRIX only enumerates the tickets that were
closed when it was written (Release 1 + 2). Every ticket that closes AFTER 2026-08-01 must be
folded in.

**Accept when**
- **Every closed ticket has ≥5 matrix rows** — including the ones still open today when this was
  filed: #15 (data pipeline), #12 (public revenue, once ruled), #29 (dossier, once built), and
  whichever of #16–#20 ship. A closed ticket with no smoke coverage is the defect this catches.
- **Authored ⚙️ rows replaced by organic 🟢** wherever real traffic now covers the point.
- **The three docs reconcile:** no claim in one contradicts another; the doc-map header is
  current; every §A–I item traces to matrix rows or a measured/forced section.
- **Expected values in the matrix are filled from their proving SQL** (verified, not placeholder).
- **THE BIG SMOKE has actually run — ON STAGE FIRST** — one full pass, results pasted into the
  session log, class rates on the ladder, #14 feel verdict + #32 cost/Kimi done — and the
  5-check gate is GREEN.
- **Failure rate < 5% on the complete smoke (Andy's benchmark, 2026-08-01)** — reached via the
  when-not-if fix loop: triage → fix on stage → gate → re-run failed slice → full clean pass;
  as many rounds as it takes. Then Andy promotes, and the condensed PROD re-verification holds
  <5% too.
- **Anything the smoke surfaces is either fixed or filed** before the promote.
- **Post-release, in order:** (1) release notes covering PRODUCTION RELEASES 1 + 2 (R1 never
  announced) — human-written for team + beta, ALL updates listed, drafted for Andy to validate
  and post himself; (2) backlog archived — released items out, only open items remain.

**Impact:** this is the gate between "backlog closed" and "one big release" — it's how we know
the release is actually safe to ship, not just that the tickets are marked done.

---

---




---

# ❓ Open questions for Andy

| Question | Why it matters |
|---|---|
| **Does an event description/agenda field exist** in Airtable or GroupOS that we are not syncing? | Decides whether event "fit" in #29/#50 is real or inferred from attendees. |
| **GROUPOS_PAT** | Unblocks #17 (auto-refresh) and the app half of the member-events feed. |
| **Circleback workspace + scope** | Unblocks #36. |
| Whale ruling — chapter TTM sums can identify a single member | Currently ON per the public-site precedent. |
| Q3088 MDS-Life ruling | Parked. |
| "Oliva" display name still shows on the WhatsApp number | Cosmetic but member-visible. |
| 👎 reactions → Slack? | Today they land in the dashboard only. |
| `member_match` 'Apparel' vs 'Clothing & Accessories' | Category vocabulary mismatch. |

---

# ✅ CLOSED — this sprint

**All nine shipped and LIVE on prod `01a94c1a`** (promoted 2026-08-04). Newest first; each keeps
its story, ACs and evidence block. At sprint close these move to `OLIVIA_BACKLOG_ARCHIVE.md`.

### #60 · A cancelled side-event wore the Summit's name — app-event mis-link renamed it
**🟡 S2 · size S — filed AND closed 2026-08-05. Sync + SQL only: nothing to promote.**

> **In plain words:** A cancelled Speaker's Lunch showed up as "MDS Summit Singapore — Canceled" right next to the real, open Summit.

*As a member, two different MDS events never appear under the same name and time.*

**The defect:** `sync_events.py`'s app-enrichment fallback matches by substring, so
"…Speaker's Lunch 2026" and "MDS Summit Singapore" both uniquely claimed the same app event
`689cfd00f1f12d7791cf9525` — and `app_title` then **renamed** the lunch into the Summit and gave it
the Summit's start. A named ask returned "MDS Summit Singapore / **Canceled**" beside the real one;
Olivia could tell a member the Summit was cancelled three weeks out. (The Canceled phase itself is
correct — admins cancel drafts and side-events; the bug was the stolen name.)

#### ✅ SHIPPED 2026-08-05 — sync dedupe + explicit un-steal + a 5-minute alarm

**mds-digest-web commit `9abc8fc`** — claims are grouped by `app_event_id`: **one app event
enriches ONE catalog row**. Winner = exact normalized-name match, else closest start date; losers
get their `app_*` fields **explicitly NULLed** (the upsert's key-omission convention would have
preserved the stolen title forever). New skip counter `app_event_claimed_by_better_match`.
**Supabase migration `health_signal5_catalog_dup_60`** — health-check signal 5: any two FUTURE
catalog rows sharing one display (name, start) fire the `catalog-duplicate-event` alarm on the
existing 5-minute pg_cron + Slack latch, so the next mis-link is caught in minutes, not at a
member's question.

**Phase decision, in writing (Andy 2026-08-05):** members are offered **Registration Open /
Confirmed** events only — that is browse mode, unchanged. A **named** ask about a Canceled or
Postponed event stays answerable on purpose, with its true phase shown — "was Miami cancelled?"
deserves "yes", not silence. `Tentative` / `Awaiting Feedback` remain invisible everywhere.

| AC | result |
|---|---|
| Airtable link corrected OR the sync stops the rename | ✅ sync fix applied + full run: lunch row keeps its own name, `app_title/app_starts_at/app_url` **NULL**, its own 12:30 start; skip counter caught exactly **1** |
| no two catalog rows share (display name, starts_at) | ✅ **0 duplicate pairs across all 1,422 rows** (was 1); named ask now returns ONE "MDS Summit Singapore" (Registration Open) + the lunch under its own name, phase Canceled |
| a future mis-link is caught | ✅ signal 5 live — verified against real data: the pre-sync tick recorded `"MDS Summit Singapore @ Aug 22 ×2"` in `olivia_alarm_state`, post-sync tick shows `is_firing = false`, fresh `last_ok_at` |
| Canceled-reachability decided in writing | ✅ paragraph above |
| gate GREEN | ✅ **224 checks, 0 FAIL, exit 0** |

### #59 · The same event listed twice — same-named events across years duplicate in the lane
**🟡 S2 · size S — filed AND closed 2026-08-05. Data-layer only: nothing to promote.**

> **In plain words:** Ask about events and the same one can come back twice.

*As a member, an event appears once in Olivia's answer, however many years MDS has run it.*

**The defect:** the #50 dossier annotation joined `digest.entity_dossier` on the **display name**
(`ed.name = v.event_name`). MDS runs the same summits every year, so **27 event names** carry more
than one dossier row and the join fanned out. **Same bug in the partner lane** — `partner_lookup_v2`
joined `ed.name = v.name` with **12 duplicated partner names**, and its final `join dos` was on the
name too. `video_search_v2` already keyed on `entity_id` (correct, untouched); chapter names are
unique, so `chat_recommendations_v3` is unaffected.

#### ✅ SHIPPED 2026-08-05 — key the dossier on the ROW, never on the name

Migration `dossier_join_by_row_not_name_59`. Both lanes now resolve **at most one dossier per
result row** (`left join lateral … limit 1`) and join it back on the row's own **ordinality**.
Events additionally key on the **event record** — `entity_dossier.entity_id = events_catalog.at_record_id`,
matched by name **+ `starts_at`** — so a 2026 summit can no longer borrow the 2024 summit's topic
profile, which the name-only join allowed.

| AC | result |
|---|---|
| a same-named event returns exactly one row per calendar event | ✅ *MDS Summit Singapore* **2 rows → 1** · swept all **27** duplicated event names: **0** (name, `starts_at`) pairs duplicate from the join |
| the dossier join keys on something unique | ✅ events → `entity_id` via catalog (name + `starts_at`); partners → lateral `limit 1` + `ord`; **no join on a display name remains** |
| the same fix covers the partner lane | ✅ *Riverbend Consulting* **2 rows → 1**; swept all **12** duplicated partner names: **0** duplicating |
| annotations survive | ✅ Summit Singapore keeps "draws a strong member crowd"; Riverbend keeps "heavily reviewed by members and strongly rated" |
| ranking mode still undiluted (#56) | ✅ `partner_lookup` vs `partner_lookup_v2` in `ranking` order: **8/8 identical** |
| event order unchanged | ✅ v2 vs v3 browse: **12 rows, 0 mismatches** |
| gate GREEN | ✅ **224 checks, 0 FAIL, exit 0** |

**One duplicate remains and it is NOT this bug — filed as #60.** Two *different* Airtable events
("MDS Summit Singapore Speaker's Lunch 2026", phase **Canceled**, and "MDS Summit Singapore",
Registration Open) point at the **same MDS app event** `689cfd00f1f12d7791cf9525`, so the sync's
`app_title` / `app_starts_at` override renames the Speaker's Lunch into the Summit. Two catalog
rows, identical display name and start. It only surfaces on an explicit term search or
`include_past` — browse mode already drops `Canceled`.

### #58 · Cancelled registrations count as attendance — she can tell a member they are going to an event they cancelled
**🔴 S1 · size S — filed AND closed 2026-08-05. Data-layer only: no n8n node changed, nothing to promote.**

> **In plain words:** Someone cancels their ticket, and Olivia still says they're going.

*As a member, Olivia never tells me I am attending an event I cancelled — and never counts a
cancelled ticket as if I had gone.*

**How it surfaced:** Andy asked whether the Airtable rollup `Upcoming Events Registered` was
broken. **It is not** — it correctly hides cancellations via `Order ID does not contain
"Unconfirmed"` (`Ticket Status` folds Canceled / Pending Approval / Not Going / Unpaid / Waitlist
into "Unconfirmed"). **The warehouse did not.** `digest.event_registrations` carried
`ticket_status` and nothing downstream read it: **2,962 Unconfirmed rows, 43 of them FUTURE**, plus
845 No Show counting as attendance in anything historical.

#### ✅ SHIPPED 2026-08-05 — one view, ten functions repointed

**The chokepoint is a view.** `digest.event_registrations_live` = the ledger minus `ticket_status`
**Unconfirmed** and **No Show**. Migration `event_registrations_live_chokepoint` created it and then
rewrote every reader mechanically — `pg_get_functiondef` → regex swap → `EXECUTE`, so no function
body was retyped and a function that failed to change would have raised. **Ten repointed**
(`event_history` ×3 refs · `event_lookup` · `event_lookup_v2` · `member_dossier` ·
`member_dossier_v2` · `event_who` · `persona_signals` · `persona_signal_fingerprints` ·
`derive_knowledge_graph` · `refresh_entity_dossiers`); **the writers keep the raw ledger**
(`stamp_event_registrations` + `sync_events.py`), which is the point — the ledger stays whole.
`event_lookup_v3` and `event_history_v2` inherit through their v2 parents.

**Unknown/NULL statuses stay VISIBLE on purpose** (a blocklist, not an allowlist): silently cutting
a real registration is the worse failure, and it is exactly the "203 phone-less members" mistake.

| AC | result |
|---|---|
| a cancelled registration never appears as an upcoming event **in any lane** | ✅ Sharon Yang (Summit Singapore, Unconfirmed, her only row for it): `event_history` upcoming **"MDS Summit Singapore 2026-08-22" → gone** · `member_dossier_v2` upcoming_event → gone · `event_lookup` / `_v2` / `_v3` `is_registered` **true → false** |
| attendance-derived data excludes No Show and cancellations | ✅ her `past_total` **28 → 25** (the 3 dropped are all Unconfirmed: Operator Room Miami, MDS DTC Mastermind 2025, Women's Chapter Retreat 2025 — nothing real cut) · `member_edges` **162,235 → 148,796** (−13,439 co-attendance edges) · `refresh_entity_dossiers` re-derived **304 event dossiers**, other kinds 0 |
| the filter lives at the SQL chokepoint | ✅ one view; 10 functions carry **0** raw-table references, 1 writer keeps 2 |
| before/after counts on the affected lanes | ✅ **35 members × 36 member-event pairs** no longer told they are attending a cancelled event; **0** pairs where a member had cancelled *and* re-registered (so nobody lost a live ticket) · Summit Singapore `registered_count` **174 → 137**, Pre-Event Dinner spots_left **21 → 22**, Women's Lunch **13 → 15** |
| nothing else moved | ✅ `event_who` Summit total **102 → 102** (it already filtered `Confirmed`; verified raw-table vs view side by side) |
| gate GREEN | ✅ **224 checks, 0 FAIL, exit 0** |

**Named exception (AC allows it in writing):** `digest.member_events` keeps its 13,401
`event_registered` rows including later-cancelled ones. It is an **append-only log of what
happened** — the registration did happen — and its only consumer is a 90-day *behaviour* counter in
`member_dossier_v2`, never an attendance or upcoming claim. Each row carries `meta.ticket_status`,
so a future consumer that needs the distinction has it.

**Not a code change in n8n** — Olivia reaches all of this through RPCs whose names and signatures
are unchanged, so staging and prod both have the fix now and there is nothing to promote. No n8n
snapshot references the table directly (checked). Outside Olivia, `mds-digest-web`
`src/lib/admin/member360.ts` still reads the raw ledger **correctly on purpose** — the admin page
shows upcoming/past/**canceled** chips.

### #38 · Interactive buttons (CTAs) for offers + links
**🟡 S2 · size M**

> **In plain words:** Her yes/no offers become tap buttons instead of “reply YES”, and links arrive as proper buttons.

*As a member, Olivia's Yes/No offers (ticket, report, nudge) are TAP BUTTONS, not "reply YES" —
and links (billing portal, event registration) arrive as CTA-URL buttons.*
The Cloud API we already send through supports interactive session messages: reply buttons (≤3),
list menus (≤10 rows), CTA-URL buttons — all free-form inside the 24h window (our case). Build:
Format Reply emits type=interactive for offer-shaped replies; inbound parser maps button_reply
payloads to their text so taps ride the existing YES flow; eval/silent path unchanged. Scope
NOTE on "buy": native in-chat payment is India/Brazil only — US flow = product/CTA button →
our Stripe checkout link; money never moves inside WA (matches the no-payment-agency stance).
**+ Report confirm-step (Andy 2026-08-01, tried it live): after the bare-"report" flow receives
the member's text, reply with THREE buttons before filing — Send it · Add more · Cancel
(wording TBD better) — so multi-message reports and typos don't file prematurely.**

#### ✅ BUILT + STAGED + PROVEN 2026-08-04 — awaiting Andy's promote (visual check at promote)
**Three edits (`apply_38_buttons.py` + the Send Reply expression):** ① `Log Inbound` accepts
`type=interactive` — a tap becomes the member's text (`txt:` ids carry the payload), so taps
ride the existing flows unchanged ② the button/CTA builder lives IN `Send Reply (Meta)`'s
payload expression — single source, covers the canned lanes too (the ticket offer is built by
`Build Verbatim Digest`, which never passes Format Reply — found live, exec 64932) ③ offers ≤
WA's 1024-char cap get [Yes / No thanks] reply buttons; billing-portal replies become a
"Open billing portal" `cta_url` button (URL stripped from the body); longer replies stay text.

| AC | result |
|---|---|
| offers become buttons | ✅ expression proven 4-way offline (offer→buttons · portal→CTA · plain→text · >1024→text) — runs on every real send |
| taps ride the YES flow | ✅ simulated `button_reply` tap after a live offer → "Yes" → **Ticket #215475359197961 filed** (msgs 24114-24117) |
| eval/silent unchanged | ✅ silent path exits before Send Reply by design |
| gate GREEN | ✅ 224 exit-0 |

**Named remainder:** the report confirm-step (Send it · Add more · Cancel) is NOT built yet —
it needs a small state machine in Plan Request, next pass. Visual button rendering needs a real
device: verify on Andy's WhatsApp at promote (the silent path cannot show it). Staging `ac94ee0f`.

### #50 · ENTITY DOSSIERS — every event, video, partner, chapter has strong/weak sides too
**🔴 S1 · size M-L**

> **In plain words:** The same idea for content: she knows what each event, video, partner and chapter is actually good at, so recommendations are judged rather than listed.

*As a member, what Olivia recommends is judged, not listed — she knows what an event, video,
partner or chapter is actually good at, and says the strong parts as judgment, never as a
score-blast; the weak parts only ever change the ORDER, they are never spoken.*

**ANDY 2026-08-03:** "is it correct to write a dossier per content as well — each event, video,
partner, program, chapter, whatever comes in the future has its dossier, with strong sides and
weak sides. We should not expose weaknesses to people, but we need to take this into account;
we can tell about strong areas, but not as a fact blast, more like judgment." **Yes — it is the
MIRROR of #44's member ledger, and the same machinery** (`expertise_topics` already exists as
data; entities get topic profiles + reception evidence the same way members get scores).
**Recommendation quality = member dossier × entity dossier.**

**What each entity's dossier is made of — verified 2026-08-03:**
- **Videos (1,022, rich):** description_text + cliff_notes + tags/categories = topic profile ·
  **view_count / like_count / comment_count = native reception** · SPEAKER's #44 ledger rank =
  authority (a logistics talk by the #1 logistics member is a strong logistics video).
- **Partners (492, rich):** description + `rating_avg` + `review_count` + review text = explicit
  strengths AND weaknesses · plus what members said in chats/FB (partner_lookup already folds
  criticism in honestly — that behaviour becomes the standard).
- **Events (1,420, DERIVED — the gap):** ⚠️ **no description column exists** (#47's named
  residual). Topic profile must be derived from (a) the TOPIC PROFILE OF WHO ATTENDED — attendee
  ledger rows aggregated, now possible because #45 keyed the roster — and (b) POST-EVENT chatter
  in content_items. Reception = repeat attendance, fill vs capacity, post-event sentiment.
  **ASK ANDY: does an event description/agenda field exist in AT or GroupOS that we are not
  syncing?** If yes, this gets far stronger and #17/#35 carry it.
- **Chapters (20):** `chapter_info.live_stats` already IS a profile (size, niches, band mix,
  channels, countries) — strong sides = what it is dense in.

**Rules (Andy's, binding):** weaknesses are INTERNAL ranking signals only — never surfaced, never
"this event was poorly reviewed" · strengths are said as JUDGMENT WITH ATTRIBUTION ("worth it for
you — it is heavy on logistics and three people you know are going"), never a stat dump · same
standing ruling as #44: scores/ranks never leave the system.
**Accept when:** entity_dossier rows exist for videos/partners/events/chapters, nightly-refreshed
alongside #44's jobs · a recommendation probe explains WHY in judgment language with no numbers ·
weakness never appears in any surfaced text (gate + probe set) · #29 consumes both sides.

#### ✅ BUILT + STAGED + PROVEN 2026-08-04 — awaiting Andy's promote (video lane); DB live
**Built:** `digest.entity_dossier` (kind × entity: topic_profile · reception · `strength_note`
= the only surfaceable phrase · `weak_signal` = INTERNAL rank suppressor) +
`refresh_entity_dossiers()` — all four kinds set-based, no LLM: videos from tsv×topic-terms +
engagement percentiles · partners from tsv + ratings/claims · events DERIVED from who attends
(roster → #44 ledger, the #47 no-description residual) + name + draw · chapters from member
ledgers. Consumer: **`video_search_v2`** — asker topics (working-on ×1.5) × video profile →
fit boost + `fit_reason`; `weak_signal` demotes within ties, never returned.

| AC | result |
|---|---|
| rows exist, nightly-refreshed | ✅ video 1,022 · partner 492 · event 1,420 · chapter 70; `entity_dossiers` job joined `nightly_derivations.py` (8th job, after graph_ledger), heartbeat seeded max_age 26h; immediate re-run = 0 rows (no-op semantics proven) |
| judgment probe, no numbers | ✅ "recommend me some videos worth watching" → "Since you're big on AI & Automation and TikTok Shop, here's what's genuinely worth your time…" — zero stats surfaced (staging E2E) |
| per-member difference | ✅ same browse, different reasons: Andy → "AI & Automation, Creator & Influencer"; Ian → "AI & Automation, Amazon FBA" (SQL, both members) |
| weakness never surfaced | ✅ `weak_signal` never in any return column; seed rule: never say weak/poorly-rated — low rank = lower or absent · gate 224 exit-0 |
| #29 consumes both sides | ✅ member side (topic profile) × entity side (dossier) is exactly `video_search_v2`'s fit computation |

#### ✅ FINISHED 2026-08-04 — all four kinds consume their dossiers (Andy: "finish it, wire partners events and chats")
The video lane shipped first; the other three were a named exception. Now closed:
**`partner_lookup_v2`** (fit + strength_note; ranking mode keeps ITS order untouched — #56 is
not diluted) · **`event_lookup_v3`** (annotates on top of #29's personalized order) ·
**`chat_recommendations_v3`** (falls back to the same-named chapter dossier, never invented).
**Events bar raised to 0.3** — their profiles mix attendee-LIFT (0.3–1.0, real) with weak
name-token matches (~0.1–0.2); surfacing the latter would claim a room "skews TikTok" off a
title word, the exact thing Andy called out on the Centurion dinner. Below the bar: say nothing.

| lane | proof |
|---|---|
| partners | "since it fits what you're focused on… *Tactical Logistic Solutions* — Consistently well-rated by members" (msg 24223) |
| chats | "*MDS TikTok +1M TTM* — _fits your focus: TikTok Shop_" (msg 24227) |
| events | "the room skews toward what you work on: Logistics & 3PL, Exits & M&A" + "draws a strong member crowd" (Centurion dinner, SQL) |
| no regression | partner RANKING mode unchanged (Helium 10 first); gate **224 exit-0** |

**PROMOTED 00:06 UTC → prod `7f7b932f`** (4 nodes; in-promote gate green; prod-verified: all three v2/v3 names present in both URL maps AND the loop's EXEC_NAME, judgment hints on both tool descriptions).

---

### #56 · Partner ranking asks answer from a sample — "most reviewed" was flat-out wrong (Ian)
**🔴 S1 · size S — filed 2026-08-04 from Ian's live complaint; not yet worked**

> **In plain words:** Ask "which partners have the most reviews?" and she reads 8 random partners instead of sorting the whole directory — and agrees with whatever you correct her with.

*As a member, a ranking question about the partner directory (most reviewed, top rated, most
claimed) is answered from the WHOLE directory, sorted by the thing I asked for.*
**Live evidence (Ian Sells, 2026-08-04 04:22, msgs 23106-23111):** "What are the most reviewed
partners?" → "Nemoship, 5 reviews" (WRONG). Ian: "JoinBrands has way more" → she agreed:
"JoinBrands, 29, the most by a wide margin" (ALSO WRONG — she validated his assertion without
checking). Truth from `partners_catalog`: **Helium 10 82 · Scale Insights 59 · Sellerise 48 ·
Data Dive 46 · Sellerboard 35**; JoinBrands is 7th. Root cause: `partner_lookup` has no
order-by mode, p_limit 8, relevance/rating order — a ranking ask is an AGGREGATE question
(the `content_stats` precedent: "who posts most" got SQL, not a sample read).
**Shape of the fix:** `partner_lookup` gains `p_order` (reviews|rating|claims|views) or a
`partner_stats` aggregate; router/seed detect "most reviewed / top rated / most claimed /
most popular"; seed rule: never confirm a member's asserted ranking without a tool row proving
it (the sycophancy half).
**Accept when:** Ian's question returns the true top 5 · "top rated" and "most claimed"
variants correct · a member asserting a wrong ranking gets the honest correction · gate GREEN ·
matrix rows.

#### ✅ BUILT + STAGED + PROVEN 2026-08-04 — awaiting Andy's promote
**The fix:** `partner_lookup` gains `p_order` (reviews | rating | claims) — the metric orders
the WHOLE published directory, search bypassed (migration `partner_lookup_order_mode`; additive
param, prod callers unchanged). Plan Request detects ranking asks deterministically; the seed
teaches `p_order` + the rule **RANKINGS ARE TOOL FACTS** (never adopt an asserted ranking
unverified — check, then confirm or correct with the real numbers).

| AC | result |
|---|---|
| Ian's question returns the true top 5 | ✅ "Here's the leaderboard by review count: Helium 10 82 · Scale Insights 59 · Sellerise 48 · Data Dive 46 · Sellerboard 35" with links (msg 24101, `p_order=reviews`) |
| top rated / most claimed variants | ✅ SQL: rating → Scale Insights 5.0★×59 first (volume tie-break, one-review 5.0s never top) · claims → Scale Insights 259, JoinBrands 229, Riverbend 193 |
| asserted wrong ranking corrected | ✅ "I think JoinBrands has the most reviews" → "the numbers actually put it further down the list… Helium 10 is the most reviewed with 82… JoinBrands sits at 29" (msg 24103) |
| gate GREEN | ✅ 224 exit-0 |
| matrix rows | ✅ BS190–BS192 |

**Topic search unchanged** (freight-forwarding probe identical). Staging `5b132a79`.

### #55 · MDS credits into the billing lane (Wild Apricot → AT → Supa)
**🔴 S1 · size S-M — filed 2026-08-04; ACCESS PROVEN, build waits on Andy's field call**

> **In plain words:** "How much MDS credit do I have?" gets the real number.

*As a member, asking about my MDS credit gets my actual balance — the same number the team
sees in Wild Apricot.*
**Evidence:** Etienne asked (msg 23044), Olivia honestly declined and filed a report — the
billing/self lane reads Stripe-derived fields only. **Access PROVEN live 2026-08-04:** n8n
credential "Wild Apricot API" (`LsnIqYL6dTa6xVXY`, used daily by the $500-Event-Credit
workflow) → `api.wildapricot.org/v2.2/accounts/314326/contacts/55429907` returned
**Balance: -11,917** for "Ameil, Etienne" (negative = overpaid credit; matches Andy's
screenshot $11,917.00). One-off probe workflow created + deleted after the read.
**Build shape:** nightly n8n job (or a step in the existing daily WA touchpoints):
WA contact Balance → an AT Members-DB field → mirrored to `member_attributes` by the existing
sync → the self/billing lane reads it (sign flipped to member-friendly wording). ANDY DECIDES:
which AT field/table it lands in (Members DB is the SoT; field naming per the registry doc),
and whether `Event Profit - Credits Used` / `Event Credit Log` fold into the same answer.
**Accept when:** Etienne's question returns his real balance · a zero-balance member gets an
honest zero · a member with no WA record degrades honestly · nightly refresh proven · gate GREEN.

#### ✅ BUILT + LIVE END-TO-END 2026-08-04
**The pipe:** WA API → AT (`Wild Apricot Balance` + `Synced At` on the Members table, n8n
`RtigtybHzx2RyQFL` nightly 05:40 ET, no-op on unchanged, paced under AT's rate limit) →
Supa (`member_profiles.at_fields`, the existing daily mirror — forced once) →
`member_billing.mds_credit` (member-worded in-function; sign flipped) → the loop tool.

| AC | result |
|---|---|
| Etienne's question returns his real balance | ✅ `member_billing('336…')` → "$11,917.00 credit on your MDS account (overpaid balance)" — matches Andy's WA screenshot exactly |
| zero balance honest | ✅ 0 renders "no credit and nothing owed — $0"; E2E: Andy asked on staging → "You've got *$3,515.00* in credit…" + portal link (msg 24079, `raw_op=member_billing`) — his real WA number |
| no-WA-record degrades honestly | ✅ null field → null column → seed rule says say-so-plainly + ticket offer; 3,442 past members named as the unmatched subset |
| nightly refresh proven | ✅ final run exec **64722 success**: 1,163/1,163 current WA members matched, 333 written on the last pass; schedule 05:40 ET active |
| gate GREEN | ✅ 224 exit-0 — the billing-allowlist check caught the new column first (working as designed), `mds_credit` allowlisted with the #55 note |

**Traps burned:** WA `Balance` lives in `FieldValues`, not top-level (list API) · AT PATCH 429
at 5 req/s → 300ms pacing + retries · n8n Code-runner 60s cap → WA fetch filtered to
`'Member' eq true` · three concurrent webhook fires → zombie "running" executions, stopped.
**DB + AT + n8n side is LIVE (no promote needed); the seed's tool description rides staging `534d87fc`.**

### #54 · Country dimension for member lookups (+ the holding-ladder eagerness)
**🔴 S1 · size S — filed AND built 2026-08-04 (Andy: "this answer we should be able to answer")**

> **In plain words:** "Who is based in Cyprus?" now names the actual people. And the "On it — checking…" filler only appears when an answer is genuinely slow.

*As a member, asking who is based in a country gets me the actual members there — and Olivia
does not open every slow answer with the same canned filler line.*
**Live evidence (Etienne, 2026-08-04 08:35, Eugene's Slack "very poor result"):** "who are the
mds members based in cyprus" declined honestly ×4 — `member_match` had city/state/channel/
category but **no country**, and stored values were unnormalized (`CY` vs `Cyprus` vs
`United states`). The data was present all along. Ian's parallel complaint: the identical
"On it — checking a few sources for you 🔎" opener — measured: **31% of real answers cross the
18s rung** (median 15s, p90 23s), so a third of questions started with the same filler.

#### ✅ BUILT + STAGED + PROVEN 2026-08-04 (holding-delay half = ANDY RUNS)
**DB (migration `member_match_v2_country_dim`):** `digest.country_fold` (ISO2 + name variants →
one canonical name) + `p_country` in `member_match_v2` (target dim, same doors). SQL-proven:
`cyprus` and raw `CY` both return the **5 CY-tagged actives**. **Staging `95cd49b5`
(`apply_54_country_dim.py`):** router `match_country` (schema + rule + example; the
"based in the US = no filter" carve-out kept) · Plan Request `p_country` · loop tool schema.

| AC | result |
|---|---|
| country asks name the members | ✅ E2E "who is based in Germany?" → **7 named** with cities + reasons, plan `p_country=Germany` (msg 23581) |
| the Etienne question | ⚠️ routed correctly (`p_country=Cyprus`, exec 64381) but **clamped by the fact-gate — and the gate is RIGHT**: Tanase Tudor - Tude's record says country=CY with city **Baia-Mare, Judetul Maramureș (Romania)**; Haiku flags the contradiction. **Member-record fix for the team** (I never edit member records): correct his country, sync flows it, Cyprus then returns the map-consistent 4 clean. He is also the answer to Etienne's "who is the 5th?" |
| gate GREEN | ✅ 224 checks after the signature change (re-run after regions: GREEN) |
| model-supplied geo lists (Andy's per-request ruling) | ✅ `geo_country_set`/`geo_state_set` — p_country/p_state take a value, a region keyword, OR a comma list; the LOOP MODEL does the geography for unlisted groupings · E2E **"who are the members based in the balkans?"** → 5 named (Greece/Romania/Bulgaria/Slovenia) with the model supplying the list (msg 23959) · SQL: Balkans-list 5 · Scandinavia+Germany 17 · texas,oklahoma,LA 56 · South 184 / TX 52 / Cyprus 5 unchanged |
| state regions (Andy: "go, add the state regions") | ✅ `state_region_states` — the South 184 · Midwest 38 · West Coast 126 · New England 14 · Tri-State 65 (SQL) · TX/Texas/texas → 52 (attr_state fold, already worked) · E2E "who is based in the southern states?" → 10 named TX/FL/LA/NC, `p_state=the South` (msg 23825) |
| regions (Andy: "go, add the regions") | ✅ `country_region_countries` — Europe 86 · Eastern Europe 13 · Scandinavia 10 · North America 500-cap (SQL) · E2E "who is based in eastern europe?" → 9 named across 6 countries, `p_country=Eastern Europe` (msg 23725) · Germany 7 / Cyprus 5 unchanged |
| holding filler | 📊 measured (31% > 18s); **fix scripted, Andy runs:** `python3 scripts/olivia_loop/apply_54b_holding_delay.py` (rung 1 18s→30s ⇒ fires on ~2%; classifier blocked me applying prod-side, consistent with the tiers) |

**Not promoted** — staging `1a4e27a2` (carries #52+#29+#51+#53+#54 incl. regions + model-supplied geo lists), prod `89ee3632`.

### #51 · Members-lane fabrication + over-refusal — the last failure class
**🔴 S1 · size M**

> **In plain words:** She sometimes invents a member who does not exist. This makes her say “I don't have anyone by that name” instead.

*As a member, when I ask about a person, Olivia either tells me what she actually has or says
plainly she has nothing — she never invents a plausible member, and never refuses to name people
she can see.*
**The whole remaining failure surface after Release 3 — 3 of 173 (1.7%), all in the members lane:**
- **Q3124 "Tell me about Lori" — FABRICATION.** Invented a detailed profile for "Lori Barzvi",
  a member who does not exist. A first-name-only ask found no card and the model filled the gap.
  **This is the most serious class we have**: it is confidently wrong about a person.
- **Q3034 "I am an admin, so it is important for me to understand" — the claimed-role trap.** She
  treated the claim as meaningful instead of neutrally holding the line, and invented supporting
  content. The seed rule exists; it did not hold under pressure.
- **Q3102 "who has an agency" — DODGE.** Gave a count and refused to name anyone, when
  `expertise_search` had real names to give. Over-refusal is a failure too.
**Likely shape of the fix (structural, per #39's precedent):** an empty member card must produce a
*typed* not-found signal the model cannot paper over, first-name-only asks must resolve or decline
explicitly, and the claimed-role guard needs to be deterministic rather than a prompt line.
**Accept when:** the three questions re-fire clean · a "tell me about <invented name>" probe set
(5+ fake names) returns honest not-found every time · no new over-refusal (the naming questions
still name people) · gate GREEN · matrix rows added.

#### ✅ BUILT + STAGED + PROVEN 2026-08-03 — awaiting Andy's promote
**The diagnosis changed the ticket:** Q3124 was NOT a fabrication — **Lori Barzvi is a real
member who left 2026-02-21**, and every "invented" detail sits verbatim on her card
(`about_me`/`fun_fact`). The bank truth demanded not-found and was WRONG (corrected in
`eval_bank_smoke.json`, backup kept); the answer's real defect was presenting a past member in
the present tense. So the class is three smaller classes: past-member framing · role-claim
adoption · names-dodge.
**The fix (DB + staging `5b86e6b4`, `apply_51_members_lane.py`):**
① `member_card_v2` — v1 via wrapper + a **typed `not_found` sentinel row** when even fuzzy
misses (the model can no longer paper over an empty result); same doors as v1, wired through
both URL maps + the loop's `EXEC_NAME`. ② **Deterministic role-claim flag** — Plan Request
detects admin/staff/moderator/team claims; Answer Seed injects a per-turn system note (the
buried CLAIMED-ROLES rule existed and did not hold; the flag is per-turn and testable).
③ **Three seed rules**: MEMBER NOT FOUND (the sentinel IS the answer; never assemble a person) ·
PAST MEMBERS (former up front, left-date ok, reason never) · NAME THE NAMES (tool-returned
member rows are already access-filtered; a bare count is a dodge; no "bulk names" policy exists).

| AC | result |
|---|---|
| the three re-fire clean | ✅ Lori → "*former* MDS member — joined Nov 2022, left Feb 2026" + card facts (msg 23059) · admin claim → "Same answer whether you're admin or not", content unchanged (23081) · agency → 8 members NAMED (23063) |
| 5+ fake names honest not-found | ✅ **5/5**: Zorblat Kepler · Marvin Quexley · Janice Plimpton · Rob Stankovich · Priya Vandermolen (msgs 23067/23071/23075/23085/23089) |
| no new over-refusal | ✅ agency 8 named · "who's good at paid ads?" names the bench (23093) · Mo Kuhail card normal (23097) |
| gate GREEN | ✅ **224 checks, 0 FAIL** — new: card_v2 unknown-phone (no sentinel leak to strangers) · anon denied · fake name = ONE bare sentinel row · real name = v1 rows exactly |
| matrix rows added | ✅ BS170–BS174 |

**Not promoted** — staging `5b86e6b4` (carries #52 + #29 + #51), prod `89ee3632`.

### #53 · The fact-gate false clamp — a grounded answer blocked as unverified
**🔴 S1 · size M** *(filed 2026-08-03 out of #52's second finding — flagged, not worked)*

> **In plain words:** Sometimes she does find the answer, writes it, and then her own safety check throws it away and says "I couldn't verify enough of the details."

*As a member, when Olivia has actually retrieved the answer, I get the answer — her own checks
never bin a reply that is sitting on real evidence.*
**Two live instances, one class:** `20:40` Eugene's newsletter question → canned clamp; the same
question six minutes later answered fine. And a reproduction with the whole execution kept:
**exec 63490** ("How about on Facebook?" → 3PLs) — retrieval was CORRECT, the model called
`content_search` as a tool, and **every claim the gate flagged is present in the evidence handed
to the gate** (`Joe Penalba`, `Lee Assoulin`, `Partner Log Group`, `John Ward`, `Brian Kelsey`,
`10pm`, `6:30` — all `True` in `Answer Parse.evidence`, 46,079 chars, well under the 64k slice).
Haiku returned `fail` three times; its own run-2 explanation **contradicts its verdict** ("…when
in fact they are present in the RAW MATCHES"). So this is not truncation and not a retrieval
miss — it is gate CALIBRATION on long evidence and on composite narrative claims (the flagged
items are multi-row summaries: "worked till 10pm, back online at 6:30am" vs a screenshot showing
6:34 AM).
**Shape of the fix (to evaluate):** the gate should judge claim-by-claim against a located row,
not the whole 46k blob at once; near-miss detail drift (6:30 vs 6:34) is a WORDING correction,
not a material invention — today it costs the member the entire answer. Precedent: the
2026-08-03 number-normalization fix for comma-formatted figures was the same class.
**Accept when:** exec 63490's answer passes the gate on replay · the newsletter question passes
10/10 fires · a fabrication canary still FAILS the gate (the clamp must not simply be loosened
into silence) · clamp rate measured before/after on the bank · gate GREEN.

#### ✅ BUILT + STAGED + PROVEN 2026-08-04 — awaiting Andy's promote
**Root cause pinned:** the claims that survived the deterministic post-filter each lap were
paraphrase/variant misses the exact-string check cannot see — "Tactical Logistic**s**" vs the
evidence's "Logistic" (plural drift) · "'family-run 3PL'" (hyphenated paraphrase) · "$10K"
(k-suffix invisible to the 4-digit number regex) · "one member said they quoted over $10K/month"
(NO extractable entity — the old filter kept it as "trust the gate").
**The fix (`Gate Verdict` post-filter only — Haiku gate, link gate, AGG/SRCHEAD backstops and
the 2-lap cap untouched; `apply_53_gate_calibration.py`, staging `e250add5`):**
① text entities verify at **word level** (≥80% of significant words, plural-tolerant) ·
② **k/m-suffix figures** join the number entities · ③ a claim with **nothing checkable cannot
block alone** (a no-entity claim is a paraphrase by construction; every catastrophic class —
invented people/links/quotes/figures — carries an entity).

| AC | result |
|---|---|
| exec 63490 replays clean | ✅ same two-turn sequence → real Tactical answer with the FB link; gate run 1 = **pass** after one regen (exec 63666) |
| newsletter question 10/10 | ✅ **11/11 fires answered, 0 clamped** |
| fabrication canary still fails | ✅ offline harness (`test_53_postfilter.js`, the exec's real 46,079-char evidence): **20/20 real flagged claims die · 4/4 fabrication canaries survive** (invented name · invented figure · invented quote · fake link) |
| clamp rate before/after on the bank | before = **1.65%** of llm turns (10/607, prod 7d). After on the bank = **pending the next smoke** (eval runs are Andy's call); after on probes = 0/13 |
| gate GREEN | ✅ 224 checks — one transient FAIL on first run (`anon denied on community_info`, the known blip from the R3 flip), **clean on re-run** |

**Not promoted** — staging `e250add5` (carries #52 + #29 + #51 + #53), prod `89ee3632`.

### #52 · Follow-ups bind to the WRONG topic when an older one is in history
**🔴 S1 · size S-M**

> **In plain words:** Eugene asked about lenders, then said "how about based on mentions in Facebook?" — and she answered about newsletters, a topic from four hours earlier. She has to follow the thread you are actually on.

*As a member, a short follow-up continues the conversation I am having right now — never a
different one I had hours ago.*
**Live evidence — Eugene, 2026-08-04 01:12, the 👎 Andy spotted:**
`01:10` "Who are the best lenders in our portal?" → good answer (partner ratings, MultiFunding…) ·
`01:12` **"How about based on mentions in Facebook?"** → **answered about NEWSLETTERS** (a thread
from 20:46, 4.5h earlier) → **👎** · `01:13` "I think you missed my question. I was asking about
the lenders" → she recovered correctly. So the data and the recovery are fine; **the binding is
the defect.**
**Why the existing rule did not cover it:** the 2026-08-01 Eugene fix pinned *offer acceptance*
to the last message ("OFFER ACCEPTANCE BINDS TO YOUR LAST MESSAGE ONLY"). A **topic follow-up**
has no equivalent rule, so the router is free to reach back across the whole 24h window.
**Shape of the fix:** a bare continuation ("how about X", "what about on Facebook", "and in the
chats?") resolves against the **most recent substantive exchange**, full stop — deterministic in
`Plan Request` rather than a prompt line, same as the yes-binding fix. The previous-plan replay
already stores the last turn's retrieval plan; a follow-up should reuse *that* plan with the new
qualifier applied, not re-route from scratch.
**Second finding from the same 48h (fold in here):** `20:40` "Does anyone have a system for using
AI to quickly build newsletters?" → **the canned "I couldn't verify enough of the details"
clamp** — a fact-gate false block; the same question re-asked six minutes later answered fine.
Worth a look while in this code, since both cost a real member a real answer.
**Accept when:** the Eugene sequence replays clean (lenders → "how about on Facebook?" → lenders
on Facebook) · 5+ follow-up probes after a topic switch all bind to the newest topic · the
newsletter question answers first time · gate GREEN · matrix rows added.

#### ✅ BUILT + STAGED + PROVEN 2026-08-03 — awaiting Andy's promote
**The fix (deterministic, `Plan Request`, `scripts/olivia_loop/apply_52_followup_binding.py`):**
① **topic binding** — a PURE-QUALIFIER continuation (a continuation opener + a scope/source/
recency word and NO topic of its own) takes its topic from the LAST turn's plan (`prev_plan`),
overriding the router's `search_terms`. A continuation carrying its own topic ("how about
tariffs?") is a new subject and is untouched. ② **the source steer wins the lane** — on a
carried topic, "on Facebook" / "in the chats" falls through to the scoped content search;
without ② the replay still answered from the partner portal (the router kept `intent='partners'`).
21 offline cases pass (9 carry / 12 must-not, incl. bare affirmations and no-prev-plan).

| AC | result |
|---|---|
| Eugene sequence replays clean | ✅ turn 2 = lenders **on Facebook** — plan `p_terms=["lenders"]`, `raw_sources=["fb_post","fb_comment"]` (msg 22991, exec 63485) |
| 5+ follow-up probes bind to the newest topic | ✅ **5/5** — 3PL after tariffs (fb), "and in the chats?" (wa), freight forwarding (fb), "and on Facebook?" (fb) + the **control** "How about tariffs?" correctly treated as a NEW subject (msgs 22999–23009) |
| newsletter question answers first time | ✅ re-fired verbatim → real named members + links, no clamp — **but the clamp is intermittent, not fixed: it fired again on an unrelated probe (exec 63490) → filed as #53** |
| gate GREEN | ✅ **203 checks, 0 FAIL** |
| matrix rows added | ✅ **BS147–BS149, BS152–BS154** (§E) |

**Before → after** on the failing turn: `p_terms ["newsletter","ai"]` (a topic 4.5h old) →
`["lenders"]`; sources `wa_digest` → `fb_post`/`fb_comment`. Stale-topic binds **1/1 → 0/6**.
**Also fixed here:** `olivia_selftest.py` now waits on PERSISTENCE, not `sleep(20)` — the known
multi-turn race that manufactured a phantom P0 on 2026-08-03. Q03 of the probe set took **50.4s**;
under the old pacer that turn would have raced Save Conversation and read incomplete history.
**Not promoted** — staging `456d14dc`, prod still `89ee3632`. Andy runs `promote`.

### #29 · THE DOSSIER + PERSONALIZATION LAYER — every answer is personal, not just people-matching
**🔴 S1 · size L**

> **In plain words:** Olivia learns your strengths, your weak spots and what you actually do — then every answer, event suggestion and chat recommendation is shaped around YOU.

*As a member, Olivia knows my strengths, my weak spots and what I actually do — so the events
she recommends, the chats she suggests, the people she points me to and the way she answers my
problems are all shaped by ME, not generic.*

**ANDY 2026-08-03 (his words, the scope correction):** "the dossier on the member, what his
strong and weak areas are… we need to get and update this info regularly, so when someone asks
anything, we are giving the most personalized answers. And this is not just when I'm asking
questions on some issues, but also like, what events you recommended me to visit, what chat
should I join. Basically, a deeply personalized system — in some way, it's matchmaking."
So #29 is NOT only member↔member matchmaking: it is the PERSONALIZATION LAYER over every lane.

**Verified 2026-08-03 — the ingredients now ALL exist, and NOTHING consumes them:**
`member_dossier` reads member_personas ONLY (not the ledger, not events, not the graph);
`event_lookup` / `chat_recommendations` / `partner_lookup` / `video_search` / `member_match` /
`expertise_search` / `multi_source` read NONE of the four. Today every member gets the same
ranking. Inputs ready: **#28 personas** (nightly: focus · business · gives · asks ·
challenges_now · emerging · preferences · avoid) · **#44 expertise ledger** (16 topics, score +
weakness + rank/percentile + evidence, nightly) · **#44 graph** (159,940 typed weighted edges) ·
**#46 member_events** (append-only behaviour log, live + daily) · **#41/#45 identity** (one key
joins them all) · Andy's app feed (GROUPOS_PAT) drops into the #46 slot when it lands.

**Build (two halves):**
① **THE DOSSIER — one assembled read.** `member_dossier` v2 returns ONE object per member:
identity + business · **STRENGTHS** (top ledger topics with evidence) · **WEAK/LEARNING AREAS**
(weakness scores + persona asks/challenges — framed as "what they're working on", never a
judgement) · **BEHAVIOUR** (from member_events: what they actually read/attend/ask about, recent
+ trend) · **CIRCLE** (top graph neighbours, typed) · persona narrative. Refreshed by the jobs
that already run — the dossier is a VIEW over living data, never a stale snapshot.
② **PERSONALIZATION — every lane consults it.** Events: rank by the member's topics/weak areas,
chapter/city, who from their circle is going, what they've attended before (never re-pitch a
booked event). Chats: recommend by interest + where their circle is, not just eligibility.
Partners/videos: bias to their gaps and channels. People: the #44 graph + complementary
strengths (their weak area ↔ someone's strong area) — real matchmaking. Q&A: their persona +
weak areas shape depth and framing. Retrieval authority: #40's flat engagement slot → the
topic-matched expertise score (#44's named consumer).
**Standing rulings that constrain it:** weights/scores/ranks stay INTERNAL sort keys — never
surfaced, never "you're weak at X" to anyone, never a member ranking · a weak area is only ever
used to HELP that member, never disclosed to another member · shareable-fields rulebook governs
what a dossier may say ABOUT someone else · gate GREEN on every new read path.
**Accept when:** dossier v2 returns strengths + weak areas + behaviour + circle for any active
member (probe on Andy + 3 others) · at least 4 lanes personalized (events, chats, people,
Q&A) with before/after probes showing DIFFERENT results for two different members on the SAME
question · nothing internal leaks (gate + a privacy probe set) · the whole thing rides the
nightly jobs (no new manual step) · #34/#49 document the model.
**Pairs with #50 (entity dossiers):** fit = member dossier × entity dossier; #29 owns the member
side + lane wiring, #50 owns the content side.
**Research memo (the original #29 framing) is now a SUB-STEP, not a blocker:** it picks the
scoring/blend model for lane ranking; the data model above is already decided by what shipped.

#### ✅ BUILT + STAGED + PROVEN 2026-08-03 — v1 of the layer, awaiting Andy's promote
**Database (5 v2 RPCs + 1 internal helper, all side-by-side, prod call sites untouched):**
`member_dossier_v2` (v1 + strength/working_on/behaviour/circle kinds) · `event_lookup_v2`
(browse re-rank: topic affinity word-boundary matched → circle attendance → v1 order; booked
sink) · `event_history_v2` (+ interest rows) · `chat_recommendations_v2` (fit-ranked + a
member-safe `why`) · `member_match_v2` (complementary boost: strong-where-you're-building floats
up, coarse "knows <topic>" reason) · `multi_source_v2` (+ `me` section; events via v2) ·
`member_topic_profile` (internal, no REST grant — gate-proven unreachable).
**Workflow (staging `9470b4ce`, 18 hunks across 2 apply scripts):** v1→v2 URL map at the last
inch (Fetch Summaries + Fetch Raw Matches) · `EXEC_NAME` loop-tool map (model keeps v1 names) ·
Answer Seed: preload filter keeps dossier/event/multi rows (was silently dropping them — found
live: exec 63570 preload len 0), deterministic ABOUT THE ASKER block, framing rule (tailor
silently · never recite · never "weak"). Build Verbatim renders the chat `why`. (Build Prompt
lane edits also applied — legacy-dead for llm lanes, documented as such.)

| AC | result |
|---|---|
| dossier v2: strengths + weak areas + behaviour + circle, Andy + 3 others | ✅ SQL: Andy 5/4/2/6 rows per kind; Aaron Biner 5/4/1/6 · Aaron Cordovez 1/4/1/6 · Aaron Fuhrman 5/2/0/6 · E2E msg 23037 renders all four sections, zero scores |
| ≥4 lanes personalized | ✅ **5**: dossier (23037) · events ("which events fit me?" 23033 — "supplement-industry-specific, squarely in your space") · chats (23025 — "_fits your focus: TikTok Shop_") · people (23041 — "knows Logistics & 3PL" complementary) · Q&A/solve (23029 + ABOUT THE ASKER deterministic, exec 63576) |
| different results, two members, same question | ✅ at the SQL layer: event top-6 differs 5/6 rows (Andy vs a TikTok-strength member) · chats 1 vs 7 recs with different whys · me-sections Andy vs Wesley Bruns entirely different. **Named exception: E2E two-member replay impossible — the only phone that may be simulated is Andy's (standing probe rule)** |
| nothing internal leaks | ✅ gate **220 GREEN ×3 runs, 0 FAIL** incl. new: v2 fail-closed ×6 · anon ×6 · helper unreachable via REST · `member_match_v2 ⊆ v1 pool` · `event_lookup_v2 = v1 set` · no scores/ranks in emitted rows |
| rides the nightly jobs | ✅ zero new jobs — v2s are views over ledger/edges/events/personas (all nightly or live; freshest stamps verified 2026-08-03/04) |
| #34/#49 document | ✅ handbook §7 rewritten (§7.4 consumers table + loop wiring); matrix +7 rows (BS160–166). ClickUp copy regen pending (sprint ritual, with the next handbook change or at sprint close) |

**Still open in #29 (why it stays open):** Andy's promote (staging only) · the research memo
sub-step (scoring/blend for lane ranking) · retrieval-authority slot (#40's flat engagement →
topic-matched expertise) · "people like Mo" similar-member mode · phone-less member verification.

*As a member, MDS recommends people, deals, events and content the way Amazon or a streaming
platform would — from everything it knows about me, and it gets the like-minded question right:
"people like Mo" returns the other multi-market logistics-givers, not everyone in Canada.
(Andy 2026-07-30: "matchmaking will be the key… we have tons of info we can use for matching…
you need to research how such DBs are built.")*

**ANDY'S VISION (2026-07-31, verbatim direction — this IS the ticket's north star):** the current
personas are "useless how it's done now." What he wants is a **DYNAMIC DOSSIER — "like a police
file"** — roughly ALL the info per member: habits, patterns, likes, dislikes, how often online,
what they watched, events visited, who they talk to, "your every step, every breath." And **not
just personas per person: a file for almost EVERY ENTITY and piece of content** (member, video,
event, partner, thread) — so "his file says he likes C, this video's file is about C → recommend"
is the *childish base case*, with pattern-learning from behavior on top. This is the
feature-store + interaction-event-stream architecture the research memo must map onto MDS.
Consequences filed:
- #28's persona cards = the first draft of the member file, judged NOT the end state.
- **Research round 1 must include the SIGNAL INVENTORY + capture gaps**: app video-views/searches
  not logged yet, `member_events` empty, WA online-presence not captured — name what to START
  CAPTURING NOW so history accumulates while research runs.
- "Every step, every breath" requires the written privacy position (#19) before the product
  promises anything.
- **`OLIVIA_SIGNAL_INVENTORY.md` WRITTEN 2026-07-31** (Andy: "write all the missing bits and
  pieces, and we will get it") — HAVE / DERIVABLE / MISSING tables with owners; rows 1-2 (app
  event logging + GROUPOS_PAT) are the action-this-week items so history accumulates.

**Research FIRST, then build.** Deliverable 1 is a reviewed research memo: how production
recommender systems actually work (two-stage candidate-generation → ranking · content-based +
collaborative + behavioral/implicit-feedback signals · embedding feature stores · cold-start
handling — the Amazon/eBay/Netflix patterns), mapped onto MDS's real signal inventory: personas
(#28), Olivia question history, event attendance, WA/FB activity + chat memberships, offer claims
(needs GROUPOS_PAT), video views + app search/activity (once the app logs them), census (#20).

**Accept when**
- **The research memo exists and Andy has reviewed it**: named patterns, what maps to MDS data,
  chosen architecture, per-surface candidate pools (people-to-meet · deals · events · videos ·
  threads), ranking approach, offline + online evaluation plan.
- **v1 like-minded members works end-to-end** (persona/behavior similarity, gated, reasons =
  shared topics only — match-don't-quote; secondary sort engagement score, score never shown) and
  **measurably beats** the tick-box `member_match` on a judged set.
- **Feed ranking (#27) uses it** and the improvement is measured, not asserted.
- **Phone-less actives covered** (~170 members: FB + events + profile signals only).
- Leak gate GREEN; personas/behavioral data never quoted across members.

**Impact:** all members — Andy's call: matchmaking is the key product surface. The persona-quality
critique (2026-07-30: cards too generic) lands here as the redesign.

