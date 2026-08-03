# Olivia — Developer Handbook

**The MDS AI Assistant: what it is, how it works, how to run it, and why it is built this way.**

> **This document replaces the ClickUp doc "MDS Olivia — Assistant" (`2531q-103317`).** That doc
> was the POC-era design record (July 2026). Everything durable from it lives here, re-organised
> by topic instead of by date. The ClickUp doc stays as a historical archive; **this file is the
> source of truth.** Day-by-day history lives in `SESSION_LOG_OLIVIA.md`; open work lives in the
> current sprint doc.
>
> **Written for a developer with no prior context and no AI assistant.** If something here is not
> enough to act on, that is a bug in this document — fix it in the same commit as your change.
>
> **Last verified against live systems: 2026-08-03.** Every number in here was queried, not
> remembered. Re-verify before trusting anything older than a few weeks.

---

## 0. Read this first — the five rules that prevent incidents

1. **Verify against live systems, never against docs.** Including this one. Every "it works" claim
   needs an execution id, a SQL result, or gate output.
2. **The safety gate is not optional.** `python3 scripts/olivia_leak_gate.py` (202 checks, free,
   ~3 min) must be GREEN before anything ships. It runs after *every* change to a retrieval
   function.
3. **Never edit the production workflow directly.** Edit staging → test → promote. The promote
   script enforces this (see §8.1).
4. **Retrieval is fail-closed by construction.** Every gated function resolves the asker from
   their phone/member-id and returns *zero rows* if identity is ambiguous. Security lives in SQL,
   never in a prompt.
5. **A member must never be told something untrue about another member.** This outranks
   helpfulness. When in doubt the system says less.

---

## 1. What Olivia is

**A personal AI assistant for MDS members, on WhatsApp.** A member sends a message; Olivia answers
from MDS's own data — the WhatsApp chats, the Facebook group, the member directory, events,
partner deals and the video library.

**The founding principle (Eugene, still true):** *the assistant's job is not to **be** the answer —
it is to route the member to an MDS resource.* A short answer plus the thread, the person, the
partner page or the video that actually holds it. This is why every recommendation carries its
link.

**Two sides were designed. One is built.**
- **Side B — reactive Q&A: BUILT.** The member asks, Olivia answers.
- **Side A — proactive weekly push:** 2–3 genuinely relevant items per member per week, skipping
  the week when nothing is relevant. **Not built.** Blocked on Meta message templates (see §2.2)
  and on the personalization layer (see §7).

**What it is not:** it is not a model we trained. Olivia is a "Layer 2" product — it rents Claude
and wraps it in MDS's data, access rules and product. The moat is the data layer, which is why
most of this handbook is about data.

---

## 2. The channel

### 2.1 Two numbers, two purposes — do not confuse them

| Number | Platform | Purpose | Rule |
|---|---|---|---|
| **+1 945-396-5415** | Meta WhatsApp Cloud API | Olivia's 1:1 DMs | The assistant. |
| **+1 786-657-8153** | Whapi | Reads the **group** chats for the digest | **Never move this to Meta.** Meta's Cloud API structurally cannot read WhatsApp groups; moving it would permanently kill the digest pipeline. |

### 2.2 The 24-hour window (this dictates the product)

On WhatsApp's official API you may message a person freely only **within 24 hours of their last
message to you**. Outside that window you need a **pre-approved Meta template**.

Consequences, all deliberate:
- **Member-initiated.** The member messages Olivia first; her welcome is her first *reply*. No
  template needed, consent is built in, and the window opens naturally.
- Members are onboarded with a click-to-chat link (`wa.me/<number>?text=Hi`).
- **The proactive weekly push needs templates** — that is the real blocker on Side A, not the code.
- Marketing-style cold templates were rejected by Meta (error 131049). Simulated inbound messages
  (the eval harness) do **not** open a real 24h window (error 131047).

---

## 3. How an answer happens — the pipeline

A member's message travels through the **production n8n workflow** (`12wj6h1TWqb0d4Dq`, 67 nodes).
The path, in order:

1. **Webhook** receives the Meta callback. Non-text events (delivery statuses, reactions) branch
   off immediately to their own handlers.
2. **Claim Message (dedupe)** — writes the WhatsApp message id to `digest.olivia_seen`. Meta
   retries deliveries; a claimed id is dropped. Fails *open* (a rare double reply beats silence).
3. **Find Member / Resolve Member** — looks the phone up in `digest.members`. **Exactly one active
   member must match**, or the conversation takes the generic non-member path. This is the
   identity hard-fail (§5).
4. **Prep Context** — loads the last 24h of conversation turns, cut at any explicit "reset", plus
   the previous turn's retrieval plan (so "yes" can be replayed).
5. **Route Request** (Claude Haiku) — classifies the message into an intent. Cheap and cached.
6. **Plan Request** (code, deterministic) — turns the router's guess into a concrete plan: which
   RPC, which parameters. This node also holds ~40 deterministic overrides that outrank the router
   (private-contact refusal, sensitive-matters, bare affirmations, report command, guest policy…).
   **Read this node before changing routing behaviour.**
7. **Embed Query** (Voyage) → **Fetch Summaries** + **Fetch Raw Matches** — the deterministic
   "zeroth fetch". Its rows are preloaded as guaranteed evidence.
8. **Verbatim? branch** — canned/no-model routes (greeting, help, chats list, ticket offer,
   refusals) answer from hard-coded text and skip the model entirely.
9. **The answering loop** (`Answer Seed → Answer Claude → Answer Parse → Answer Tool → Answer
   Merge → …`, max 5 rounds) — Claude Sonnet with the gated RPCs exposed as **tools**. The model
   decides what to fetch and may look again. **`p_phone` is injected server-side in Answer Parse;
   the tool schemas deliberately have no phone parameter the model could set.**
10. **Claims? → Fact Check → Gate Verdict** — a Haiku fact-gate compares the draft against the
    evidence actually retrieved this turn. Claim-free replies skip it. Unsupported claims trigger
    one regeneration; a second failure returns an honest "I could not verify this". A deterministic
    **link gate** additionally requires every URL to appear verbatim in the evidence.
11. **Format Reply → Billing Nudge → Eval (silent)? → Send Reply (Meta)** — WhatsApp formatting,
    an optional once-per-24h billing reminder, then either a real send or (for eval traffic) a
    silent path that skips Meta entirely.
12. **Save Conversation** — both turns are written to `digest.olivia_messages`, stamped with the
    member record and the retrieval plan.

**Two side workflows:**
- **Holding ladder** (`X1vzrW9Avqff3qRa`) — fires on inbound, sends "on it" / "still working" if an
  answer is slow. Fail-closed: it checks whether the answer already landed before each rung.
- **Daily review** (`xkX7wnIwxJLU7YgY`) — 17:00 ET, Claude reviews the last 24h of real
  conversations and posts findings to Slack `#automation-tests`.

---

## 4. The data layer

### 4.1 The founding decision

**Airtable is the system of record. Supabase is the serving layer.** Airtable is curated but slow
(~5 requests/second) and cannot do permission-filtered lookups at scale. Everything Olivia reads is
mirrored into Postgres, pre-processed and access-tagged **at ingest time**, so answering is a fast
indexed lookup rather than a live hunt across systems.

**Corollary rule:** *the assistant only reads sources that have been cleaned, defined and
access-tagged. An undefined source does not exist to her.* No crawling raw bases.

### 4.2 Where everything lives

- **Supabase project `nadtudwuwjhckotrngzn`, schema `digest`** — 43 tables, ~75 functions.
- **Airtable Members DB `appou5JVr0WIrioWS`** — the member system of record.
- **Airtable Events base `appYa7blqkHazLMYf`** — events catalog + Event Roster (`tblfTLRfAqBhBZlc4`).
- **GroupOS** — videos, partners, app events (read via MCP today; a `GROUPOS_PAT` would make it a
  scheduled pull).

### 4.3 The core tables

| Table | Rows (2026-08-03) | What it is |
|---|---|---|
| `content_items` | 38,711 | **The unified search index.** Every searchable thing — WhatsApp messages, chat digests, Facebook posts and comments, application answers — one row each, with `access_rule`, `sensitivity`, a full-text vector and a 1024-dim embedding. |
| `member_edges` | 159,940 | The knowledge graph: typed, weighted member↔member connections. |
| `event_registrations` | 17,795 | The registration ledger, keyed to members. |
| `member_events` | 15,071 | **Append-only** behaviour log (see §7.3). |
| `member_expertise` | 5,822 | The expertise ledger: member × topic scores with evidence. |
| `member_attributes` | 5,740 | The derived member profile — the canonical member population. |
| `member_profiles` | 5,840 | Raw Airtable field mirror (`at_fields` jsonb). |
| `members` | 646 | **The WhatsApp channel layer** — phone → member. Not the population. |
| `events_catalog` / `videos_catalog` / `partners_catalog` | 1,420 / 1,022 / 492 | Source catalogs. |
| `olivia_messages` | 2,424 | Conversation history, stamped with the member record. |

> ⚠️ **`digest.members` is the WhatsApp layer; `digest.member_attributes` is the member
> population.** Confusing the two has caused repeated bugs — most notably staff counts. Anything
> that reasons about "members" reads `member_attributes`.

### 4.4 The three access dimensions (mechanical, never prompt-based)

1. **Canonical source + freshness** — one agreed system of record per source.
2. **Entitlements** — `access_rule` jsonb per row. Types: `public`, `chat_member` (the asker must
   be in that chat), `owner` (the asker must be that member), `fb_group`. **An unknown rule type is
   DENIED** — new access types fail closed by default.
3. **Sensitivity** — a `sensitivity` column: `normal`, `restricted` (returned only with an explicit
   consent flag), `never_surface` (never returned, under any flag).

All three are enforced inside the SQL functions, per query, resolved from the asker. They are not
instructions the model could ignore.

---

## 5. Identity — one human, one key

**The canonical key is `at_member_id`** (the Airtable Members-DB record id, mirrored to
`member_attributes`). Phone numbers, emails, WhatsApp numbers and Facebook accounts are **routes
that resolve to it**, never identities in themselves.

**One nuance that bites everyone once:** `digest.olivia_messages.member` holds
`digest.members.airtable_id`, *not* `at_member_id` — they are different columns of the same record
and **zero of 646 are equal**. The foreign key demands `airtable_id`. Check which one a table wants
before joining.

**The rules:**
- **Hard-fail on ambiguity.** A phone matching zero or several members gets a generic reply. A
  wrong match would mean reciting another founder's business into a private DM.
- **Identity is not entitlement.** Matching a phone is separate from being an *active* member;
  cancelled and removed members are refused data everywhere (`is_active_member_status()`).
- **`members.at_member_id` is never auto-stamped from name/email guesses.** It controls what data a
  phone can retrieve; ~61 unidentified WhatsApp numbers wait for a human matcher rather than an
  algorithm. Registrations and Facebook identities *are* auto-matched — they do not grant access.
- Every Olivia conversation is stamped with its member record at write time; event registrations
  are re-keyed after every roster sync (`stamp_event_registrations()`).

---

## 6. Retrieval — how search actually works

### 6.1 `content_search_v2` (the current engine)

Three **independently indexed** candidate branches, fused by **rank** (Reciprocal Rank Fusion),
never by blended scores:

| Branch | Mechanism | Weight |
|---|---|---|
| Keyword | GIN index on `search_tsv`, top 200 by `ts_rank_cd`, re-ranked by term coverage → 60 | 1.0 |
| Meaning | **Pure ANN top-200 over the HNSW index**, then access-filtered | 1.0 |
| Recency | `occurred_at` index, top 60 | 0.5 |
| Authority | Author's engagement score as an extra rank list | 0.25 |

**Why rank-fusion and not scores:** keyword rank and vector distance are incomparable scales. A
tiered sort makes the vector a silent no-op — which is exactly the bug v1 had for months (the
275MB vector index had *zero* scans in its lifetime).

**Two traps burned in, do not re-trip:**
- The ANN branch must run as a **separate pure top-200 query** with `enable_seqscan=off` set
  transaction-locally. Fused into the main query, the planner mis-estimates rows and refuses the
  index — and a warm sequential scan *looks fast* while the index is never used. **Proof is the
  query plan plus the `idx_scan` counter, never wall-clock time.**
- PostgreSQL 15 rejects function-level `SET hnsw.*` (placeholder GUC validation). Load the vector
  library in-body first, then `set_config(..., true)`, wrapped fail-open.

**Attribution marking:** a Facebook comment whose body begins with the post author's name is a
*reply to* that person. `content_search_v2` marks it `[→ to <name>]` at the SQL layer, so the model
is told who is speaking rather than guessing. Same marker in `fb_thread`.

**Corpus hygiene:** rows whose embed-source text is under 30 characters are deliberately left
unembedded (6,486 of them) — they stay keyword- and thread-reachable but do not pollute meaning
search.

### 6.2 The gated RPC surface

Every function Olivia can call is `SECURITY DEFINER`, granted **only to `service_role`**, and
resolves the asker itself. The main ones:

| Function | Purpose |
|---|---|
| `content_search_v2` / `content_search` | The search engine (v2 current; v1 retained until soak completes) |
| `content_lookup` | Date-window browse instead of term search |
| `content_stats` | Counting over the whole corpus |
| `fb_catchup` / `fb_thread` | Facebook recency browse / full thread pull |
| `member_card` | One member's public profile card |
| `member_match` | Members by attribute (city/state/category/band/channel) |
| `expertise_search` | Members by what they know (keyword + embedding, RRF) |
| `member_count` | Counting members by attribute, with breakdowns |
| `member_dossier` / `member_billing` | The asker's own record / own billing |
| `event_lookup` / `event_who` / `event_history` | Events, attendees, own registrations |
| `chapter_info` / `community_info` | Chapters with live stats / community numbers |
| `partner_lookup` / `video_search` / `video_file_for_send` | Partner deals / video library / file sending |
| `multi_source` | One-shot fan-out across all six source families |
| `chat_info` / `chat_recommendations` | Chat metadata / which chats to join |
| `report_create` | Files a member report |

**Grant discipline:** `DROP FUNCTION` + `CREATE` **resets the EXECUTE grant to PUBLIC** — meaning
anon could call it. Always `revoke all … from public` and re-grant to `service_role` after a
drop+create. `CREATE OR REPLACE` preserves grants; prefer it. The leak gate checks this.

**After any RPC DDL:** `notify pgrst, 'reload schema'` and then hammer the REST path — stale
connection-pool caches produce *intermittent* 404s that look exactly like a quality regression.

---

## 7. The personalization data (built, not yet consumed)

Three layers exist and refresh nightly. **No answer uses them yet** — wiring them into the lanes is
the next major piece of work.

### 7.1 Expertise ledger — `member_expertise`
Every active member scored across 16 topics (topics live in the `expertise_topics` **table** — a
new topic is an INSERT, not a code change). Score formula, v1:

```
(2.0·ln(1+posts) + 0.7·ln(1+comments) + 3.0·min(videos_spoken,5)
  + 1.5·business_affinity + 1.0·ln(1+persona_gives))
  × revenue band multiplier (1-5M 1.0 · 5-10M 1.15 · 10-20M 1.3 · 20M+ 1.5)
```
Weakness score = `ln(1 + persona asks/challenges hits)`. Every row carries an `evidence` jsonb so
any score can be explained. Rank and percentile are computed per topic.

### 7.2 Knowledge graph — `member_edges`
Typed weighted member↔member edges: `co_attended`, `same_chat`, `same_chapter` (each weighted
`1/ln(1+group size)`, and **groups larger than 150 are excluded** — a 409-attendee summit is not a
connection), plus `thread_interaction` (Facebook commenter ↔ post author, the strongest signal).

### 7.3 Behaviour log — `member_events`
**Append-only. Nothing is ever edited or deleted** — corrections are new events, and the service
role physically has no UPDATE or DELETE grant. Every row carries `occurred_at` (when it happened)
*and* `captured_at` (when we saw it) plus a `cadence` (`live` / `daily` / `weekly` / `backfill`),
so a nightly-detected change can never masquerade as a live one. Live writers are fail-open
triggers: an event-logging failure must never break the member's answer.

**Rulings that constrain all three:** scores, ranks and weights are **internal sort keys** — never
surfaced to a member, never used to rank members publicly. A weak area may only ever be used to
help that member, never disclosed to another.

---

## 8. Runbooks

### 8.1 Deploying a change to Olivia

```bash
cd /Users/Born/Scorecard
python3 scripts/olivia_wf.py lock --reason "<why>"   # single-editor lock
# edit the STAGING workflow (bqHstPDi84uOhTCJ) — never prod
python3 scripts/olivia_selftest.py --staging --questions "reset" "<a real question>"
python3 scripts/olivia_leak_gate.py                  # must print GATE PASSED
python3 scripts/olivia_wf.py promote                 # diff → gate → snapshot → write → bounce → byte-verify
python3 scripts/olivia_wf.py unlock
```

- `promote` refuses to write unless the gate is green. It snapshots production first
  (`olivia_snapshots/`), then bounces the workflow **once**.
- **Rollback:** `python3 scripts/olivia_wf.py rollback <snapshot-label>` (skips the gate — it is the
  emergency path). Proven twice on live production.
- **n8n rule:** edit the ACTIVE workflow, then do **one** `[{deactivateWorkflow},{activateWorkflow}]`
  bounce. **Never deactivate before editing** — that caused an 8.5-hour dead-webhook outage.
- **No bare apostrophes in n8n expressions** — they produce invalid syntax that fails *silently*
  (the fact-gate was dead for a full day this way).

### 8.2 The safety gate

```bash
python3 scripts/olivia_leak_gate.py     # 202 checks, ~3 min, free
```
It inserts canary rows with every access rule and sensitivity, asks the real RPCs for them as
several different members, and asserts what must *not* come back. It also verifies anon lockout,
cancelled-member refusal, field allowlists and grant hygiene, then cleans up after itself.
**Green before every ship. No exceptions.**

### 8.3 Quality evaluation

```bash
cd /Users/Born/mds-scorecard-tools
OLIVIA_EVAL_BANK=eval_bank_smoke.json python3 olivia_eval.py --fire --staging --ids 3106,9024,...
OLIVIA_EVAL_BANK=eval_bank_smoke.json python3 olivia_eval.py --score
```
- The bank is **organic questions real members asked** — generated questions were retired.
- Eval traffic uses `wamid.SELFTEST*` ids: the workflow answers fully but **skips the Meta send**.
- Runs pace one question at a time and look stalled for minutes. **Never kill a run.**
- Baseline: 169 questions, 3.6% wrong (2026-08-03, production).
- ⚠️ `olivia_selftest.py` paces with a fixed 20-second sleep; an answer slower than that races the
  conversation save and produces phantom multi-turn failures. Fix it to wait on persistence.

### 8.4 Nightly jobs (launchd, on Andy's Mac)

| launchd job | What runs |
|---|---|
| `com.mds.olivia.derivations` (04:30) | `nightly_derivations.py` — 8 jobs: niches, question labels, chapter pages, member-profile embeddings, content embeddings, member-event diffs, expertise ledger + knowledge graph |
| `com.mds.persona.refresh` (04:15) | `persona_refresh.py` — rebuilds member personas |
| `com.mds.olivia-eval` (03:30) | the nightly eval run |
| `com.mds.olivia.watchdog` (every 15 min) | `alarm_watchdog.py` — watches the alarm system from *outside* Supabase |

Every job stamps `digest.olivia_job_heartbeats`. A job that goes stale (>26h, or >192h for weekly
catalog refreshes) triggers the Slack alarm. **Prove any scheduled script under `/usr/bin/python3`**
— launchd uses Apple's Python 3.9, which is not your shell's Python.

### 8.5 Facebook capture (the one irreducibly manual step)

Facebook removed permalink anchors, so the scroll/enumerate step is manual (Chrome extension).
**Rewrite `extension/seed_ids.json` from the capture file on every run** — it falls back silently
to a stale seed and pulls comments for the wrong days. Then:
`load_feed.py → download_images.py → vision_decode.py → upload_images.py → linker SQL → embed_backfill.py`.

### 8.6 Incident response

1. Read the actual error first — `n8n_executions` for the failing run, `get_logs` for Supabase.
   Never theorise before reading the error text.
2. A **timeout looks exactly like "no data found"**. Time the query at increasing input sizes
   before blaming ranking, embeddings or the schema cache.
3. Health signals: the alarm (pg_cron, every 5 min, Slack `#automation-tests`), the watchdog
   (launchd, covers the case where Supabase itself is down), and the tools-health dashboard.
4. Rollback is one command (§8.1) and takes seconds. Use it early.

---

## 9. Environment and secrets

**All keys live in `/Users/Born/mds-digest-web/.env.local`** (not in this repo). Scripts read it
directly. Names you will need:

| Variable | Used for |
|---|---|
| `SUPABASE_URL`, `SUPABASE_SECRET_KEY` | Everything database-side (service role) |
| `N8N_API_KEY` | Workflow read/write |
| `VOYAGE_API_KEY` | Embeddings (`voyage-3.5-lite`, 1024 dimensions) |
| `CENTURION_ANTHROPIC_API_KEY` | Claude for scripts (eval judging, personas) |
| `AIRTABLE_PAT` | Airtable syncs |
| `HEALTH_REPORT_SECRET`, `QA_LOGIN_SECRET` | Health report / QA login |

⚠️ **`ANTHROPIC_API_KEY` is exported empty by some tooling** — that is why script keys are
namespaced (`CENTURION_ANTHROPIC_API_KEY`). Never rely on the bare name.

**Models in use:** `claude-sonnet-5` (answers), `claude-haiku-4-5` (router + fact gate),
`voyage-3.5-lite` (embeddings). Thinking is **disabled** on the n8n Claude calls — enabled thinking
consumed the whole token budget and members received "Sorry — I could not generate an answer".

---

## 10. Repository map

```
/Users/Born/Scorecard/                  ← this repo (Olivia + Scorecard + docs)
  OLIVIA_HANDBOOK.md                    ← you are here
  OLIVIA_BACKLOG.md / OLIVIA_SPRINT_*.md  ← open work
  SESSION_LOG_OLIVIA.md                 ← day-by-day history (append-only)
  OLIVIA_ARCHITECTURE_AUDIT_*.md        ← the architecture scorecard + its SQL
  OLIVIA_RELEASE_NOTES.md               ← member-facing notes (Andy posts them)
  OLIVIA_SHAREABLE_FIELDS.md            ← the privacy rulebook (see §11)
  scripts/
    olivia_wf.py                        ← stage / promote / rollback / snapshot / lock
    olivia_leak_gate.py                 ← the 202-check safety gate
    olivia_selftest.py                  ← fire questions through a workflow
    nightly_derivations.py              ← the 8-job nightly pipeline
    olivia_loop/                        ← the answering-loop source (build_loop.py re-applies)
    alarm_watchdog.py, sync_chapter_pages.py, olivia_*.py
/Users/Born/mds-scorecard-tools/        ← eval harness + ingestion tools
    olivia_eval.py, eval_bank_*.json, embed_backfill.py, persona_refresh.py, load_feed.py …
/Users/Born/mds-digest-web/             ← the portal (Next.js, Render) + .env.local + sync scripts
```

**Separate repos are separate.** `mds-ai-bot` and `mds-digest-web` are their own projects; never
edit one while working the other.

---

## 11. The privacy model

`OLIVIA_SHAREABLE_FIELDS.md` is the binding rulebook. Summary:

- 🟢 **Shareable per member:** the member-card fields — name, city/state, chapter, niche, expertise,
  about, fun fact, revenue **tier/band**, sales channels, business model, Facebook link.
- 🟡 **Group-only:** employees, SKUs, brands, years in business, age, revenue sums — as chapter or
  community **aggregates**, never per member.
- 🔴 **Never:** exact revenue, job titles, contact details (email/phone/address), payment and Stripe
  data, internal ids, removal reasons, another member's persona or billing.

**Default-deny:** roughly 1,700 unlisted Supabase fields cannot leak because no gated function
selects them. "Used in a calculation" is not "shareable".

**Standing rulings:**
- **Public-in-the-app = shareable** (Eugene, final) — anything a member can already see in the MDS
  app about another member may surface. Everything else keeps the structural refusal.
- **Revenue:** our data yields **bands only**, always. A figure the member or an MDS page *posted
  publicly* may be repeated **as an attributed quote with its link**, never in Olivia's own voice,
  never as a ranking key.
- **Sensitive matters** (a death, a crime, a lawsuit, "is X a scam"): she never answers the question
  or restates the claim — she says it is not hers to speak to, links where it was discussed, stops.
- **Trust and character:** she has no vetting data and never vouches for anyone.
- **Chapters are public**; chapter events are gated by chapter membership, and a chapter-styled
  event with no chapter link **fails closed** (hidden from everyone until tagged).
- **Never delete a member record.** Merge or flag; only genuine test junk is removed.

---

## 12. Decisions and why (the durable ones)

| Decision | Why |
|---|---|
| **Rent the model, never train one** | Training is hundreds of millions of dollars and a research team. Olivia is a Layer-2 product: rented brain + our data + our access rules. |
| **Process at ingest, not at answer time** | Google is fast because it indexed ahead of time. Joining data live is the "five-minute treasure hunt". Organise the *data*, do not try to predict questions. |
| **Airtable = truth, Supabase = serving** | Airtable is curated but rate-limited and cannot do per-item permission filtering at scale. |
| **Security in SQL, not in prompts** | A prompt rule is a suggestion; a fail-closed function is a guarantee. Every retrieval function resolves the asker itself. |
| **Member-initiated conversations** | Removes the template requirement, builds in consent, opens the 24h window naturally, and avoids the "unknown number DMing you" feel. |
| **Hard-fail on ambiguous identity** | A wrong match means reciting another founder's business into a private DM. |
| **The model gets tools, not a single shot** | The original one-pass router — one lane, one retrieval, no second look — was the root cause behind whole classes of failure. The loop can look again. |
| **Fuse by rank (RRF), never blended scores** | Keyword rank and vector distance are incomparable; blending silently disables one of them. |
| **Organic eval bank only** | Generated questions can be overfitted and do not reflect what members actually ask. |
| **One smoke test per batch, not per ticket** | The full run is slow and paid; per-ticket proof is probes plus the gate. |
| **Coverage is a process, never an event** | Anything hand-run rots. Every derivation is a scheduled job with a heartbeat and an alarm. |

---

## 13. Field traps (real bugs, documented so they do not recur)

- **Airtable field names lie.** Read the field description or formula before trusting one. "WA" in
  the Partner Portal means *Wild Apricot*, not WhatsApp. `Most Recent Revenue Source` is a record
  URL, not a channel. `Actual Birthday v2` is the *next* birthday. `Subscription Status` is null
  everywhere — the live one is `Stripe Subscription Status`.
- **PostgREST caps responses at 1,000 rows** regardless of `limit`. Always paginate. This bit three
  different places in one day; an ascending sort silently returned the *oldest* thousand.
- **Airtable search flattens, get nests** (the n8n v2 node shapes differ).
- **`chapter_affiliation` and `business_model` are `text[]`**, not text.
- **`percent_rank()` returns double precision** — cast before `round()`.
- **Data-modifying CTEs read the pre-update snapshot** — verify counts with a fresh query.
- **Error-shaped JSON parses fine.** Check for expected keys; never treat "it parsed" as success.
- **Supabase's safe-update guard blocks bare `DELETE`** over REST — use `where true` for a
  deliberate full-table refresh.
- **n8n v1 fan-out branches run depth-first in order** — a feedback branch listed second runs only
  after the entire first branch. Wire the fast branch first; prove it with per-node start times.

---

## 14. Known limits (2026-08-03)

- **Recommendations are not personalized yet.** The ledger, graph and event log exist; no lane
  reads them.
- **No transcripts.** Olivia finds a call and its deck, never what was said inside it.
- **The live calls calendar** (Mogul / Expert / Channel Calls) is not connected.
- **Events have no description field anywhere in the pipeline** — event topic matching is inferred
  from names, attendees and post-event chatter.
- **Tap buttons** are not built; offers are "reply YES".
- **The proactive weekly push** needs Meta templates.
- **Facebook capture is manual** (platform limitation).
- **Portal login OTP shares Olivia's number** — if that number is ever blocked, logins break too.
  Splitting login onto its own number is standing hygiene work.
- **The nightly jobs run on a Mac via launchd** — they need that machine awake. The staleness
  alarms are the backstop.

---

## 15. Glossary

| Term | Meaning |
|---|---|
| **The gate** | `olivia_leak_gate.py`, 202 automated safety checks. "Gate 202" means 202 *checks*, not questions. |
| **Probe** | One question fired through a workflow. Free-ish, no approval needed. |
| **Run** | Firing the eval bank (dozens to hundreds of questions). Costs money; needs approval. |
| **The smoke** | The full 169-question run used as a release exit exam. |
| **Lane / route** | Which retrieval path a question takes (events, partners, membercard, llm…). |
| **The loop** | The tool-calling answering loop (Answer Seed → … → Gate Verdict). |
| **Fact gate** | The Haiku check comparing a draft answer against retrieved evidence. |
| **Promote** | Copying the staging workflow to production via `olivia_wf.py`. |

---

*Maintenance rule: this handbook is updated in the same commit as the change it describes. If you
learned something the hard way, §13 is where it goes.*
