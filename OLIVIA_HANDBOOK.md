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

### 1.1 The stack — every tool, and what it is there for

| Layer | Technology | Specifics |
|---|---|---|
| **Orchestration** | **n8n Cloud** (`mdsco.app.n8n.cloud`) | 4 workflows: production `12wj6h1TWqb0d4Dq` (67 nodes) · staging `bqHstPDi84uOhTCJ` · holding ladder `X1vzrW9Avqff3qRa` · daily review `xkX7wnIwxJLU7YgY`. Edited via the public API (`N8N_API_KEY`), never the UI, so changes are diffable and snapshotable. |
| **Database** | **Supabase Postgres 15**, project `nadtudwuwjhckotrngzn`, schema `digest` | 43 tables, ~75 functions. Extensions in use: **`vector` 0.8.0** (pgvector/HNSW), **`pg_cron` 1.6.4** (the health alarm, every 5 min), **`pg_net` 0.20.0** (Slack calls from inside Postgres), **`pg_trgm` 1.6** (fuzzy name matching), `pgcrypto`, `uuid-ossp`. |
| **API surface** | **PostgREST** (Supabase REST) | Everything is `POST /rest/v1/rpc/<function>` with the `service_role` key and `Content-Profile: digest`. No ORM, no direct Postgres connections from n8n. |
| **Answer model** | **Anthropic `claude-sonnet-5`** | The answering loop, tool-calling, thinking **disabled**, 3 prompt-cache breakpoints (tools, system, moving message mark). |
| **Router + fact gate** | **Anthropic `claude-haiku-4-5`** | Intent routing (cached ~6.2K-token prompt) and the evidence check. Cheap, fast, replaceable. |
| **Embeddings** | **Voyage `voyage-3.5-lite`**, 1024 dimensions | Query-time and document-time. Chosen over OpenAI by ruling. |
| **Member channel** | **Meta WhatsApp Cloud API v22.0** | Phone-number id `1306956855827812`, WABA `1575708577606583`. Text, image and document sends; read receipts and typing indicators. |
| **Group capture** | **Whapi** | Reads the WhatsApp *group* chats for the digest — the Cloud API cannot. Separate number, separate vendor, deliberately. |
| **Systems of record** | **Airtable** | Members DB `appou5JVr0WIrioWS`; Events base `appYa7blqkHazLMYf` (Event Roster `tblfTLRfAqBhBZlc4`). |
| **Catalog source** | **GroupOS** (MCP today) | Videos, partners, documents. A `GROUPOS_PAT` would turn the weekly manual refresh into a scheduled pull. |
| **Portal / web** | **`mds-digest-web`** — Next.js on **Render** | `digest.mds.co`: member portal, admin dashboards (`/admin/olivia`), the Olivia test window, the ticket endpoint Olivia calls. |
| **Scheduling** | **launchd** on Andy's Mac | 5 jobs (§8.4). Not a server — the staleness alarms exist precisely because this machine can be asleep. |
| **Alerting** | **Slack** `#automation-tests` (`C0AQ8USNQK0`) via the MDS-Verifier bot | Alarm fires from pg_cron→pg_net (independent of n8n), plus a launchd watchdog outside Supabase. |
| **Sync jobs** | **GitHub Actions** | `member-profiles-sync` (daily), `events-catalog-hourly` (hourly, self-healing). |
| **Facebook capture** | **Chrome extension** (v0.82) | Manual scroll + comments pass — the one irreducibly human step (§8.5). |
| **File storage** | **Supabase Storage** | `fb-images` (public bucket, for image sends), `video-files` (private, signed URLs valid 1h). |
| **Scripting** | **Python 3, stdlib only**, shelling out to `curl` | No virtualenv, no dependencies, no ORM — deliberately. Scheduled scripts must run under **Apple's `/usr/bin/python3` (3.9)**, which is why no modern syntax is used. |
| **Version control** | **git** (this repo) + workflow snapshots | `olivia_snapshots/` holds pre/post-promote JSON of the production graph. |

**Why so much of it is "just SQL and curl":** every layer that could hold state or fail silently was
deliberately pushed into Postgres, where it is inspectable, transactional and gate-testable. n8n
holds orchestration only; the scripts are thin.

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

## Appendix A — RPC reference (contracts)

Every function below is `SECURITY DEFINER`, granted **only to `service_role`**, and resolves the
asker itself. **Universal gating**, unless noted: the caller is identified by `p_phone` (or
`p_at_member_id` where offered); **exactly one ACTIVE member must match** or the function returns
zero rows. `access_rule` and `sensitivity` filters are applied inside every content-touching query.

| Function | Arguments | Returns | Gating & notes |
|---|---|---|---|
| `content_search_v2` | `p_phone, p_terms text[], p_sources text[], p_kinds text[], p_chat, p_since date, p_limit int, p_include_restricted bool, p_author, p_embedding, p_at_member_id` | `TABLE(source, kind, source_id, title, tl_dr, body, occurred_at, url, sensitivity, meta jsonb, search_extra)` | **VOLATILE** (sets HNSW GUCs transaction-locally). RRF over keyword+ANN+recency+authority. Access rules + sensitivity enforced in all three branches. Emits `[→ to X]` addressee markers and `meta.post_author`. |
| `content_search` | identical | identical | **v1, retained during soak.** Keyword-gated; semantic-only rows never return. Do not build on it. |
| `content_lookup` | `p_phone, p_source, p_kind, p_chat, p_since, p_on, p_until, p_order_by, p_limit, p_include_restricted` | `TABLE(source, kind, source_id, title, tl_dr, body, occurred_at, url, sensitivity, meta)` | Date-window browse, no scoring. The tool for "what happened on/around X". |
| `content_stats` | `p_phone, p_metric, p_terms text[], p_sources text[], p_since, p_limit` | `TABLE(label, value numeric, detail)` | Aggregates over the whole corpus. `p_metric`: `messages\|posts\|authors\|by_chat\|by_author`. Never sample-counted. |
| `fb_catchup` | `p_phone, p_since date, p_limit` | same shape as `content_search_v2` | Facebook recency browse ranked by **discussion volume**, not pure recency. |
| `fb_thread` | `p_phone, p_author, p_terms text[], p_post_id, p_limit_comments` | `TABLE(kind, author, body, occurred_at, url, image_text, post_id)` | Whole-thread pull (post + ≤60 replies). Public FB rows only. Carries the `[→ to X]` marker. |
| `member_card` | `p_phone, p_member` | `TABLE(full_name, city, state, country, revenue_tier, niche, expertise, about_me, hobbies, fun_fact, facebook_link, chapter, channels[], business_model[], categories[], shared_chats[], membership_state, joined, left_date)` | **The shareable-fields allowlist in code form** — the gate pins this column list. Revenue is a *tier*, never a figure. Fuzzy name resolution (pg_trgm, word_similarity > 0.62). |
| `member_match` | `p_phone, p_dims text[], p_limit, p_city, p_state, p_channel, p_category` | `TABLE(full_name, city, state, reasons text[])` | Attribute matching. Returns **coarse reasons only** — never raw values. City comparisons go through `place_city()`. |
| `expertise_search` | `p_phone, p_query, p_limit, p_embedding` | `TABLE(full_name, city, state, expertise, niche, matched_text, matched_rank)` | Keyword + embedding fused by **RRF** (the in-house precedent for `content_search_v2`). `matched_text` is the public profile snippet that matched. Ordered by engagement score after relevance. |
| `member_count` | `p_phone, p_niche, p_city, p_state, p_chapter, p_band, p_main_only, p_group_by, p_at_member_id` | `TABLE(total bigint, breakdown jsonb, breakdown_sum bigint, population bigint, note)` | Counting only — never names. `breakdown_sum` exists because members hold several chapters/niches, so the parts legitimately exceed the whole. |
| `member_dossier` | `p_phone` | `TABLE(kind, label, detail)` | **Self only.** Profile + active chats + recent own messages + event registrations. Reads personas; does **not** yet read the expertise ledger, graph or event log. |
| `member_billing` | `p_phone` | `TABLE(membership_status, plan_name, plan_price, subscription_status, billing_interval, monthly_amount, annual_payment, member_since, year_joined, next_renewal, chapter, next_invoice_date, next_invoice_amount, payment_frequency, membership_fee, billing_portal)` | **Self only.** The only status-emitting function; every state maps to plain member-facing words inside it, so raw system codes are structurally unemittable. |
| `billing_nudge` | `p_phone` | `TABLE(nudge)` | **VOLATILE** — stamps `olivia_billing_nudges` so a past-due reminder rides at most once per 24h. Sent text only; saved history stays clean. |
| `event_lookup` | `p_phone, p_terms text[], p_city, p_virtual bool, p_include_past bool, p_limit, p_embedding, p_at_member_id` | `TABLE(event_name, starts_at, start_display, event_type, phase, city, guests_policy, chapter, audience_hint, is_registered, can_register, reg_link, guest_reg_link, spots_left, registered_count, event_url)` | Chapter-gated (record-link overlap; untagged chapter events **fail closed**). Registration-open only unless `p_include_past`. Rank-based vector eligibility partitioned future/past. |
| `event_who` | `p_phone, p_event, p_limit` | `TABLE(event_name, starts_at, full_name, state, is_me, total_going)` | **Confirmed attendees only** (`Ticket Status='Confirmed'` and `Ticket for` ∈ member classes). `total_going` is the true count; the name list may be a 60-row sample. |
| `event_history` | `p_phone` | `TABLE(kind, label, detail)` | **Self only.** Past + upcoming registrations, plus the asker's own city (used by other lanes). |
| `chapter_info` | `p_phone, p_at_member_id, p_chapter` | `TABLE(chapter, member_count, asker_is_member, leads jsonb, about, categories[], live_stats jsonb, page_url, geo, region, asker_city, asker_state, note)` | Counts computed by the **same CTEs as `member_count`** — one number everywhere by construction. `live_stats` are chapter **aggregates** only. Leads are public (names, roles, photos); their contact details do not exist in the data. |
| `community_info` | `p_phone` | `TABLE(active_members, whatsapp_chats, upcoming_events, chapters, chapter_breakdown jsonb, gender_split jsonb)` | Community-level numbers. Gender is approximate and must be presented with the not-everyone-reports caveat. |
| `partner_lookup` | `p_phone, p_query, p_limit, p_embedding, p_at_member_id` | `TABLE(name, offer_value, description_snippet, categories[], rating_avg, review_count, claim_count, featured, fresh_deal, partner_url, reviews_sample jsonb, matched_rank)` | Reviews are real member reviews — quotable, never attributed to a name. |
| `video_search` | `p_phone, p_query, p_limit, p_embedding, p_at_member_id` | `TABLE(title, call_type, speakers[], description_snippet, cliff_notes_snippet, attachments jsonb, duration, categories[], tags[], published_at, video_url, matched_rank, is_restricted)` | **Restricted videos return metadata only** — title and date, never description, cliff notes or attachments. They are listed, never denied. |
| `video_file_for_send` | `p_phone, p_file_key` | `TABLE(file_name, storage_object, file_kind, video_title)` | Re-validates the key server-side (public video, allowed kind, our bucket) — a hallucinated key for a restricted deck cannot send. |
| `multi_source` | `p_phone, p_query, p_terms text[], p_city, p_want text[]` | `jsonb` (one key per family) | One-shot fan-out across partners / members / events / chats / Facebook / videos. A new source = one branch here + one prompt block. |
| `chat_info` | `p_phone, p_chat` | `TABLE(chat_name, is_member, verification_required, requirement, call_schedule, zoom_link, moderators, join_link)` | Gated chats return the **verification form**, never a raw invite, to non-members. Zoom links only for chats the asker is in. |
| `chat_recommendations` | `p_phone` | `TABLE(chat_name, verification_required, requirement, qualifies, join_link)` | Excludes chats they are in and gated chats they do not qualify for — absence stays ambiguous (a "you do not qualify" line would leak). |
| `report_create` | `p_phone, p_text, p_context` | `TABLE(ok, report_id, note)` | **VOLATILE.** Files a member report verbatim. Idempotent within a short window (double-file protection). |
| `app_member_feed` | `p_email, p_recent_queries text[], p_interest_embedding, p_limit_each` | `jsonb` | **The app's door.** Identity by email; the app must send the LINKED member email. Fail-closed: unknown or inactive email returns `{}`. |
| `persona_signals` | `p_at_member_id` | `jsonb` | Signal bundle used by the nightly persona builder. Not member-facing. |

**Non-gated helpers** you will see referenced: `is_active_member_status()`, `place_city()`,
`name_fold()`, `member_event_url()`, `member_video_url()`, `member_partner_url()`,
`content_like_escape()`, `attr_clean()`. **Derivation functions** (service-role, run by the nightly
pipeline): `derive_member_attributes()`, `derive_member_expertise()`, `derive_knowledge_graph()`,
`derive_member_change_events()`, `stamp_event_registrations()`, `refresh_all_member_attributes()`,
`profile_texts_for_embedding()`. **Ops:** `olivia_health_check()`, `olivia_alarm_fire()`,
`olivia_touch()`.

---

## Appendix B — Database reference

### B.1 Core table shapes

```sql
-- THE SEARCH INDEX (38,711 rows)
content_items(
  id bigint, source text, kind text, source_id text,      -- source: wa_message|wa_digest|fb_post|fb_comment|application
  title text, tl_dr text, body text, search_extra text,   -- search_extra carries OCR'd image text after an [IMAGE TEXT] marker
  occurred_at timestamptz, url text,
  access_rule jsonb,          -- {type: public|chat_member|owner|fb_group, chat?, member?}  UNKNOWN TYPE = DENIED
  sensitivity content_sensitivity,  -- normal | restricted | never_surface
  meta jsonb,                 -- chat_name, sender_member, author_name, post_id, msg_count, topics…
  search_tsv tsvector,        -- GIN indexed
  embedding vector(1024),     -- HNSW indexed (cosine); NULL for sub-30-char rows by design
  ingested_at timestamptz)

-- THE MEMBER POPULATION (5,740 rows) — canonical key at_member_id
member_attributes(
  at_member_id text PK, full_name, membership_status, city, state, country,
  rev_band,                    -- 1-5M | 5-10M | 10-20M | 20M+  (the ONLY revenue representation)
  under_30 bool, age_band, categories text[], sells_supplements bool,
  business_model text[], channel_mix text[], sku_count int, large_sku bool,
  brands_count int, started_year int, title, expertise, main_niche, fun_fact,
  tiktok_seller bool, provenance jsonb, chapter_affiliation text[], chapter_ids text[],
  refreshed_at timestamptz)

-- THE WHATSAPP CHANNEL LAYER (646 rows) — NOT the population
members(
  airtable_id text PK,        -- what olivia_messages.member points at
  at_member_id text,          -- the canonical key; NULL for 61 unidentified numbers (never auto-stamped)
  phone, email, full_name, name, membership_status,
  channels_present text[],    -- which WhatsApp chats they are in = the chat_member entitlement
  olivia_welcomed_at, olivia_optout_at, olivia_interactions, olivia_last_used_at,
  portal_last_seen_at, msgs_7d, msgs_30d, otp_* , delivery_* …)

-- CONVERSATION (2,424 rows)
olivia_messages(id, phone, member,      -- member = members.airtable_id (FK)
  role text,                            -- 'member' | 'olivia'
  text, wamid, route, focus_chat, latency_ms, created_at,
  plan jsonb)                           -- the retrieval plan; replayed when the member says "yes"

-- BEHAVIOUR LOG (15,071 rows) — APPEND ONLY, no UPDATE/DELETE grant exists
member_events(id, at_member_id, member, event_type, source,
  cadence text,                          -- live | daily | weekly | backfill
  occurred_at timestamptz, captured_at timestamptz, meta jsonb)

-- EXPERTISE LEDGER (5,822 rows)  ·  KNOWLEDGE GRAPH (159,940 rows)
member_expertise(at_member_id, topic, score, rank_in_topic, pct, weakness_score, evidence jsonb, refreshed_at)
member_edges(a_id, b_id, edge_type, weight, evidence jsonb, refreshed_at)  -- CHECK (a_id < b_id)
expertise_topics(topic PK, terms text[])   -- topics are DATA; a new topic is an INSERT

-- REGISTRATION LEDGER (17,795 rows)
event_registrations(roster_record_id PK, event_at_id, member_at_id, email, full_name,
  order_date, ticket_type, ticket_status,  -- Confirmed | Unconfirmed | No Show
  ticket_for text[],                       -- MDS Member | Significant Other | Partner | …
  source, app_event_id, app_user_id, synced_at)
```

### B.2 Indexes that matter

| Index | Table | Purpose |
|---|---|---|
| `content_items_embedding_hnsw` | `content_items` | 275 MB HNSW (cosine). **Only reachable when the ANN operator is the leading sort of its own query** — see §6.1. |
| `content_items_tsv_idx` | `content_items` | GIN on `search_tsv` — the keyword branch. |
| `content_items_source_id_uq` | `content_items` | Idempotent ingest (35M+ scans — the hottest index in the system). |
| `videos_catalog_embedding_hnsw` / `videos_catalog_search_idx` | `videos_catalog` | Video semantic + keyword search. |
| `partners_catalog_tsv_idx` | `partners_catalog` | Partner keyword search. |
| `member_expertise_topic_rank_idx` | `member_expertise` | "Top N in topic X". |
| `fb_member_map_one_primary` | `fb_member_map` | **Partial UNIQUE** — enforces exactly one primary Facebook identity per member. |

### B.3 Triggers (18) — what fires automatically

| Table | Trigger | Effect |
|---|---|---|
| `wa_messages`, `summaries` | `content_items_ingest` / `content_items_delete` | Mirrors WhatsApp messages and digests into the search index automatically. **This is why the index is never manually populated for WA.** |
| `member_profiles` | `member_attributes_derive` | Re-derives the member attribute row on any profile change (the entire derived layer hangs off this). |
| `member_profiles`, `members`, `member_attributes` | `propagate_display_name`, `fill_display_name` | Display name = Members-DB "Profile Name Cleaned", propagated at write time. |
| `member_attributes` | `member_attributes_fill_chapter` | Chapter ids ← chapter affiliation. |
| `member_personas` | `member_personas_archive` | Every persona rewrite archives the previous version. |
| `olivia_messages` | `member_event_olivia_turn` | Writes a `member_events` row per real answer (eval traffic excluded). Fail-open. |
| `olivia_reports` | `member_event_report` | Same, for filed reports. |
| `members` | `member_event_portal_seen` | Fires only when `portal_last_seen_at` actually changes. |
| `events_catalog`, `partners_catalog` | `*_embed_invalidate` | Clears the embedding when the text changes, so the nightly re-embed picks it up. |
| `member_sessions` | `member_sessions_rollup` | Session counters. |

### B.4 pg_cron

| Job | Schedule | What |
|---|---|---|
| `olivia-health` | `*/5 * * * *` | The outage alarm — runs **inside Postgres**, so it still fires when n8n is down. Signals: members receiving failure text · workflow-down markers · an active webhook ping. Re-alerts every 30 min while firing, posts recovery on clear, and stamps its own heartbeat. |

> ⚠️ `pg_net` installs into schema **`net`**, not `extensions`. Unqualified calls inside exception
> handlers fail silently — check `pg_proc` before assuming a function exists.

---

## Appendix C — The production workflow, node by node

`12wj6h1TWqb0d4Dq`, 67 nodes. Grouped by role:

| Group | Nodes | Notes |
|---|---|---|
| **Entry** | `WA Verify (GET)`, `Respond Challenge`, `WA Inbound (POST)` | Meta webhook verification + the single inbound entry point. |
| **Dedupe** | `Log Inbound` → `Claim Message (dedupe)` → `Drop Duplicates` | Non-text events branch off. Claim writes to `olivia_seen`; fails **open**. |
| **Identity** | `Find Member` → `Resolve Member` → `Matched?` | Exactly-one-active-member or the generic path. Carries `airtable_id` (for stamping) and `at_member_id`. |
| **Context** | `Load Recent Turns` → `Prep Context` | 24h history, cut at "reset", plus the previous retrieval plan for "yes" replay. |
| **Fast feedback** | `Mark Read + Typing` → `Holding Trigger?` → `Fire Holding Timer` | **Wired FIRST in the fan-out on purpose** — n8n v1 runs branches depth-first, so this must precede routing or the read receipt lands *after* the answer. |
| **Routing** | `Touch Olivia Stats`, `Route Request` (Haiku), `Fetch Chat Links`, `Plan Request` | `Plan Request` is the deterministic brain: ~40 overrides that outrank the router. |
| **Retrieval** | `Embed Query` (Voyage) → `Fetch Summaries` → `Fetch Raw Matches` → `Verbatim?` | The "zeroth fetch", preloaded as guaranteed evidence. Both fetch nodes map `content_search` → `content_search_v2` at the last inch. |
| **Canned lanes** | `Build Verbatim Digest` | Greeting, help, chats, opt-in/out, reset, ticket offer/create, contact refusal, verbatim digests — **no model call at all**. |
| **The loop** | `Answer Seed` → `Answer Claude` → `Answer Parse` → `Answer Done?` → (`Voyage Embed` → `Attach Embedding` → `Answer Tool` → `Answer Merge` → back) | Max 5 rounds. `Answer Parse` injects `p_phone`; `Attach Embedding` swaps the execution name to v2. |
| **Fact gate** | `Claims?` → `Fact Check` (Haiku) → `Gate Verdict` → `Gate OK?` | Claim-free replies skip it. One regeneration allowed, then an honest refusal. Deterministic link gate + post-filters run inside `Gate Verdict`. |
| **Delivery** | `Format Reply` → `Billing Nudge` → `Apply Nudge` → `Eval (silent)?` → `Send Reply (Meta)` | The eval branch skips Meta entirely. `Format Reply` converts markdown to WhatsApp formatting and extracts `[SEND_IMAGE:]` / `[SEND_FILE:]` markers. |
| **Persistence** | `Save Conversation`, `Mark Welcomed`, `Set Olivia Opt-State` | Both turns saved with plan + member stamp. |
| **Attachments** | `Image To Send?` → `Fetch Post Images` → `Build Image Sends` → `Send Image (Meta)`; `File To Send?` → `Fetch Sendable File` → `Sign File URL` → `Send Document (Meta)` | File keys are re-validated server-side before any send. |
| **Team actions** | `Action?` → `Log Request (Supabase)` → `Notify Team (Slack)` | Only fires for genuine action requests, with conversation context and a member-log link. |
| **Side channels** | `Parse Delivery Status` → `Save Delivery Status`; `Parse Reaction` → `Save Feedback (Supabase)` | Meta reports delivery once and never lets you query it back — dropping these is how "delivered" beliefs go wrong. 👍/👎 reactions are the teaching signal. |
| **Manual utilities** | `Send Test (Manual)`, `Config`, `Send Message (Meta)`, `Fix Subscription (Manual)`, `Subscribe App to WABA`, `Check WABA Subscription` | Operator tools, not part of the answer path. |
| **Legacy** | `Build Prompt`, `Ask Claude`, `Build Generic` | The pre-loop single-shot path. `Build Prompt` still owns the **single global STYLE block** that `build_loop.py` harvests into the loop seed — edit style there, not in two places. |

---

*Maintenance rule: this handbook is updated in the same commit as the change it describes. If you
learned something the hard way, §13 is where it goes.*
