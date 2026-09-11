# Olivia — Developer Handbook

**The MDS AI Assistant — member-facing name "Millie": what it is, how it works, how to run it, and why it is built this way.**

> **This document replaces the ClickUp doc "MDS Olivia — Assistant" (`2531q-103317`).** That doc
> was the POC-era design record (July 2026). Everything durable from it lives here, re-organised
> by topic instead of by date. The ClickUp doc stays as a historical archive; **this file is the
> source of truth.** Day-by-day history lives in `SESSION_LOG_OLIVIA.md`; open work lives in the
> current sprint doc.
>
> **ClickUp copy:** doc `2531q-103317` now mirrors this handbook — a TOC page plus one page per
> chapter (01-18) and `99 · ARCHIVE` holding the consolidated July-2026 design record. **The copy
> is generated from this file; regenerate it when this file changes materially** (it is the only
> way non-repo readers can see any of this). Repo wins on any disagreement.
>
> **Written for a developer with no prior context and no AI assistant.** If something here is not
> enough to act on, that is a bug in this document — fix it in the same commit as your change.
>
> **Last verified against live systems: 2026-09-04** (n8n graph, Supabase counts, Meta templates and
> display name, launchd, GitHub Actions, Render routes, the gate — 323 checks, EXIT 0). Every number
> in here was queried, not remembered. Re-verify before trusting anything older than a few weeks.

---

## 0. Read this first — the five rules that prevent incidents

1. **Verify against live systems, never against docs.** Including this one. Every "it works" claim
   needs an execution id, a SQL result, or gate output.
2. **The safety gate is not optional.** `python3 scripts/olivia_leak_gate.py` (323 checks on
   2026-09-04 — the count grows with every ship, say "gate green"; free, ~3 min) must be GREEN
   before anything ships. It runs after *every* change to a retrieval function. Read the exit
   code, never `| tail`.
3. **Never edit the production workflow directly.** Edit staging → test → promote. The promote
   script enforces this (see §8.1).
4. **Retrieval is fail-closed by construction.** Every gated function resolves the asker from
   their phone/member-id and returns *zero rows* if identity is ambiguous. Security lives in SQL,
   never in a prompt.
5. **A member must never be told something untrue about another member.** This outranks
   helpfulness. When in doubt the system says less.

---

## 1. What Olivia is

**A personal AI assistant for MDS members, on WhatsApp — her member-facing name is "Millie"**
(ruled 2026-08-21, announced on stage at the Singapore Summit 2026-08-24; "Olivia" survives as the
name of the project, the workflow and every table). A member sends a message; she answers from
MDS's own data — the WhatsApp chats, the Facebook group, the member directory, events and the
Summit run-of-show, partner deals and partner websites, the video library with its transcripts,
the team's own written docs, and the member's own form answers. As of 2026-09-04: 143 members have
talked to her (1,385 real turns), 62 of them in the last seven days.

**The founding principle (Eugene, still true):** *the assistant's job is not to **be** the answer —
it is to route the member to an MDS resource.* A short answer plus the thread, the person, the
partner page or the video that actually holds it. This is why every recommendation carries its
link.

**Two sides were designed. One is built.**
- **Side B — reactive Q&A: BUILT and live** — including personalized recommendations (§7),
  the composable finder (§6.3), consent-first member introductions (§8.7) and the Summit lane (§4.9).
- **Side A — proactive weekly push:** 2–3 genuinely relevant items per member per week, skipping
  the week when nothing is relevant. **Not built.** The personalization layer now exists; the
  blocker is the channel: a push needs a Meta template, and Meta classifies personalized copy as
  MARKETING, which its per-user caps then drop (the one broadcast tried so far — the Summit-videos
  wave of 2026-08-28 — was accepted 94/94 and delivered 44; §2.2).

### 1.1 The stack — every tool, and what it is there for

| Layer | Technology | Specifics |
|---|---|---|
| **Orchestration** | **n8n Cloud** (`mdsco.app.n8n.cloud` — 69 workflows on the account, 50 active) | Olivia's: production **`12wj6h1TWqb0d4Dq`** (**80 nodes**, versionId `30fd7e6f`, webhook path `olivia-wa-live`) · staging `bqHstPDi84uOhTCJ` (`olivia-wa-staging`; Meta must never point here) · holding timer `X1vzrW9Avqff3qRa` · daily beta review `xkX7wnIwxJLU7YgY` (17:00 ET → Slack) · reminder sender `QhJw46Mr7LAP8fdz` (**hourly**; its last node is the #97 intro-expiry sweep) · display-name watcher `a1ViYr5FT7iePdN9` (temporary, still armed) · engagement → WA DB members `BfLqFlwzBBe0LgMy` (daily 07:30 ET). The July POC `Af2atRScbYSOTYbC` is still active and stays standalone. Edited via the public API (`N8N_API_KEY`) under the `olivia_wf.py` lock, never the UI, so changes are diffable and snapshotable (183 snapshots). |
| **Front door (relay)** | **`digest.mds.co/api/olivia/webhook`** (mds-digest-web on Render) | **Meta's callback URL points HERE, not at n8n** (since 2026-07-21, after the 8.5-hour dead-webhook incident). Normal times: pure passthrough. n8n dead (workflow off, execution cap, cloud outage): one canned "upgrading, try again shortly" text per member per 15 min, a `status='maintenance'` row in `olivia_sends`, and **502 so Meta retries** — the question is answered late, never lost (`olivia_seen` dedupes the retry). |
| **Database** | **Supabase Postgres 17.6**, project `nadtudwuwjhckotrngzn` | Schema `digest`: **75 tables, 16 views, 116 functions** (exported to `db/`, #65, daily drift alarm) + schema `event`: 18 tables, 33 FKs, no views, no functions. Extensions: **`vector` 0.8.0** (pgvector/HNSW), **`pg_cron` 1.6.4** (`olivia-health` every 5 min + `member-phone-index` every 15 min), **`pg_net` 0.20.0** (Slack from inside Postgres), **`pg_trgm` 1.6** (fuzzy names), `pgcrypto` 1.3, `uuid-ossp` 1.1. |
| **API surface** | **PostgREST** (Supabase REST) | Everything is `POST /rest/v1/rpc/<function>` with the `service_role` key and `Content-Profile: digest`. No ORM, no direct Postgres connections from n8n. |
| **Route lanes** | **`mds-digest-web`** — Next.js on **Render**, `digest.mds.co` (live `37ddd39`; a push to `main` IS the deploy) | Policy in git, not SQL (decision 2026-08-17): `/api/olivia/schedule` (Summit lane: schedule · next · where · speakers · sessions · recommend · people/who-to-meet · reminders) · `/kb` (org docs, #18) · `/intro` (brokered intros, #97) · `/find` (the finder, #108) · `/webhook` (the relay above) · `/ticket` (escalation → Intercom, which 403-blocks n8n's IP). Admin/test: `/test-chat`, `/feedback`, `/reports`, `/requests`; the in-app widget `/widget/enter` + `/widget/messages`; the iOS Knowledge-Base app `/ask` + `/feed`. Auth on the lanes: `X-Olivia-Secret`. |
| **Answer model** | **Anthropic `claude-sonnet-5`** | `Answer Claude`: tool-calling loop (≤5 rounds, 29 tools), `max_tokens` 2000, thinking **disabled**, 3 prompt-cache breakpoints (tools, system, moving message mark). Benched against GPT-5.6 Terra 2026-09-02 (#156): 5.4% fail / $0.0211 per answer vs 3.3% / $0.0310 — vendor call open as #157, nothing ported. |
| **Router + fact gate** | **Anthropic `claude-haiku-4-5-20251001`** | Intent routing (cached ~6.2K-token prompt) and the evidence check. Cheap, fast, replaceable. |
| **Embeddings** | **Voyage `voyage-3.5-lite`**, 1024 dimensions | Query-time and document-time (content, member profiles, videos, partners — whose text includes the partner's web profile since #160 — events). Chosen over OpenAI by ruling. Render holds its own `VOYAGE_API_KEY` for the kb lane. |
| **Member channel** | **Meta WhatsApp Cloud API v22.0** | Phone-number id `1306956855827812`, WABA `1575708577606583`, display name **"MDS AI Assistant"** (APPROVED, quality GREEN; a new name has sat PENDING_REVIEW since 2026-08-19 — §2.3). Text, image, document, template, button and interactive-list sends; read receipts; typing indicators. 12 approved MDS templates (§2.2). |
| **Group capture** | **Whapi** | Reads the WhatsApp *group* chats for the digest — the Cloud API cannot. Separate number, separate vendor, deliberately. |
| **Systems of record** | **Airtable** | Members DB `appou5JVr0WIrioWS`; Events base `appYa7blqkHazLMYf` (Event Roster `tblfTLRfAqBhBZlc4`). Never written by Olivia's code (Andy 2026-08-25). |
| **Catalog source** | **GroupOS**, via its MCP only | Videos, partners, the Summit export, documents. The MCP runs only inside a Claude session, so the **weekly scheduled Claude task `groupos-videos-weekly`** (Sunday) is the refresh: video dump → `videos_weekly_check.py --apply` · `partners_weekly_check.py --apply` (+ web-profile crawl for new/changed partners) · the per-member `videos_list(for_user_id)` entitlement sweep when a new restricted video appears. There is still no `GROUPOS_PAT`; `zoom_weekly` reports `degraded` for that reason every Monday and that is its normal state. |
| **Transcripts** | **Zoom** cloud recordings + **AssemblyAI** | `zoom_weekly.py` (Monday) pulls Zoom transcripts with real names per cue; `aai_submit.py --local` (ffmpeg → AAI `/v2/upload`) covers in-person/hybrid rooms where speakers stay `Speaker A/B/C`. Coverage: all 2025 + 2026 videos and the 16 Summit Singapore talks (§14). |
| **Scheduling** | **launchd** on Andy's Mac + one scheduled Claude task | 9 `com.mds.*` jobs, 6 of them Olivia's (§8.4) + `groupos-videos-weekly`. Not a server — the staleness alarms exist precisely because this machine can be asleep (and launchd cannot write `~/Downloads`, §13). |
| **Alerting** | **Slack** `#automation-tests` (`C0AQ8USNQK0`) via the MDS-Verifier bot | Alarm fires from pg_cron→pg_net (independent of n8n), plus a launchd watchdog outside Supabase, plus the tools-health dashboard and its 08:00 card (`digest.mds.co/admin`). |
| **Sync jobs** | **GitHub Actions** (mds-digest-web) | `member-profiles-sync` (13:47 UTC daily — profiles backfill, events layer incl. registrations, raw Typeform forms ledger; GitHub often starts it 3.5–6 h late) · `events-catalog-hourly` (:17, self-healing). |
| **Facebook capture** | **Chrome extension** (v1.13, full autopilot) | Daily insights + humanized auto-scroll + comment pass, one owned tab; ingest is autopilot on the download drop (`auto_import.py`). The Insights xlsx leg still needs a human click when Facebook's SPA stalls — the one irreducibly human step (§8.5). |
| **File storage** | **Supabase Storage** | `fb-images` (public bucket, for image sends), `video-files` (private, signed URLs valid 1h). |
| **Scripting** | **Python 3, stdlib only**, shelling out to `curl` | No virtualenv, no dependencies, no ORM — deliberately. Scheduled scripts must run under **Apple's `/usr/bin/python3` (3.9)**, which is why no modern syntax is used. The only OpenAI use anywhere is the model-bench harness (`~/mds-scorecard-tools`, snapshot in `scripts/model_bench/`). |
| **Version control** | **git** (this repo) + workflow snapshots | `olivia_snapshots/` holds pre/post-promote JSON of the production graph; `db/` holds the exported SQL layer. One branch per session, never a commit on `main` (Andy 2026-09-02). |

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
- Simulated inbound messages (the eval harness, `wamid.SELFTEST*`) do **not** open a real 24h
  window (error 131047).

**Approved templates (Meta, read live 2026-09-04 — the WABA's whole vocabulary):**

| Template | Category | Used for |
|---|---|---|
| `mds_summit_reminder` | UTILITY | #86 event reminders outside the window (the hourly reminder sender) |
| `mds_intro_request` | UTILITY | #97 consent ask to the intro target: "‹member› asked for an introduction…" + Accept/Decline buttons |
| `mds_intro_accepted` / `mds_intro_declined` | UTILITY | #109 requester notices — free-form text dies outside the 24h window (131047), so these ride templates first, text only as fallback |
| `mds_intro_lapsed` | MARKETING (Meta reclassified it) | #109 seven-day lapse notice — can still be capped by 131049 |
| `mds_login_code` | AUTHENTICATION | The portal's login OTP — same number as Millie (§14) |
| `mds_birthday_box_address` | UTILITY | Birthday-box address ask |
| `mds_summit_videos_live_v2` / `_v3` | MARKETING | The 2026-08-28 Summit-videos wave: 94/94 accepted by the API, **44 delivered, 50 dropped** on 131049 (marketing frequency cap) and 130472 (experiment holdout) |
| `mds_assistant_whats_new_aug2026`, `olivia_update_aug_2026`, `olivia_intro` | MARKETING | Release broadcasts (`olivia_intro` is the July one that died on 131049) |

**Template lessons, burned in three submissions deep (2026-08-28):** **the COPY decides the
category, not the flag** — Meta reclassified UTILITY → MARKETING on v1, v2 and v3 of the videos
template even with `allow_category_change:false`; personalized "picked for you" reads as
promotion. **No newlines inside template VARIABLES** (132018 — Meta approved the example, then
refused every send). **Approved ≠ sendable: test-send before any wave.** **A 200 from
`/messages` is never delivery** — the truth arrives asynchronously on the status webhook into
`digest.olivia_sends`; always read it back. The open recommendation for the next wave is a strictly
transactional v4 ("the recordings from your event are available" + button), with the
personalization moving to Millie when the member taps in.

### 2.3 The display name

The number's verified name is **"MDS AI Assistant"** (APPROVED; quality rating GREEN). **"MDS
Mille"** — the misspelling submitted before the name was ruled — has been **PENDING_REVIEW at Meta
since 2026-08-19**; Meta refuses a second submission while one is pending (error 2388362, no
cancel API). The hourly watcher `a1ViYr5FT7iePdN9` WhatsApps Andy the moment it flips. **Standing
plan:** on the verdict do NOT re-register "Mille" — submit **"MDS Millie"**, re-register within the
14-day window (6-digit PIN), then delete the watcher. She already calls herself Millie everywhere
(12 strings across 4 nodes; the fact-check lane names her in RULE ONE and `community_info` returns
`assistant_name`, because Haiku once vetoed her own name as an unsupported claim — exec 93640).

### 2.4 Interactive messages

Yes/no offers are **tap buttons** (#38). Pick-one-of-N — "which of these should I introduce you
to?" — is the native **interactive list** (≤10 rows, exactly the recommendation cap); the reply
carries the row `id`, so resolution is by id, never by parsing a typed name (#107b). A body over
1024 characters cannot carry buttons, so the buttons go out as a **follow-up message**
(`Followup Interactive?` → `Send Followup Interactive (Meta)`); suggestions are never filtered or
shortened to make room (Andy, #107b). Template quick-reply taps arrive as `msg_type='button'` and
list taps as `interactive/list_reply`; the intro ones are intercepted by `Intro Tap?` **before the
LLM lane** (#97, in prod since 2026-08-22), everything else flows through normally.

---

## 3. How an answer happens — the pipeline

> **Team research mode is NOT this pipeline (#172, live 2026-09-10).** The `MDS Team` target of Ask Millie is a second
> runtime beside Millie: `POST /api/admin/millie/research` in `mds-digest-web` (Render) runs a `claude-sonnet-5` tool loop
> in-process — `sql_query` → `digest.team_sql` as the read-only role, `schema_catalog` (static), `semantic_search`
> (Voyage + pgvector through the same RPC) — streams NDJSON to the page, and writes two `olivia_web_messages` rows per turn
> (`mode='team'`, `route='team-research'`, the query trail as `sources`, cost and laps in `metrics`). The n8n graph is never
> called for a Team turn (`/api/admin/millie/chat` still returns 400 for `target=team`), there are no member gates, and the
> asker is always the staff session, on a FAIL-CLOSED allowlist (`MILLIE_TEAM_ASKERS`). Everything below describes Millie's
> own pipeline for members and the three other Ask Millie targets.

A member's message travels through the **production n8n workflow** (`12wj6h1TWqb0d4Dq`, 80 nodes —
Appendix C). The path, in order:

1. **The relay, then the webhook.** Meta's callback lands on `digest.mds.co/api/olivia/webhook`
   (Render), which forwards the payload untouched to `WA Inbound (POST)`; if n8n is dead it sends
   the canned "upgrading" line and returns 502 so Meta retries (§1.1). Inside the workflow the
   **raw-event store branch runs FIRST** (#75): every inbound message event — text, interactive,
   reaction, media, template-button tap — is persisted verbatim to `digest.olivia_webhook_events`
   *before any parse can throw*. Delivery statuses and reactions then branch to their own handlers.
2. **Claim Message (dedupe)** — writes the WhatsApp message id to `digest.olivia_seen`. Meta
   retries deliveries; a claimed id is dropped. Fails *open* (a rare double reply beats silence).
2b. **Intro Tap? (#97)** — an *Accept intro* / *Decline* button tap or an `intro_pick_*` list tap is
   swallowed here and POSTed to the intro route (`op:'tap'` / `'pick'`), which replies directly
   (`Build Intro Reply` → `Send Reply`); a stale or unrelated tap comes back `handled:false`,
   `Restore Original Message` puts the pre-tap message back, and the turn continues as if the
   branch did not exist. These taps never reach the LLM lane.
3. **Find Member / Resolve Member** — `olivia_front_door_v2(p_phone, p_user_id)` looks the sender
   up in `digest.members` by phone **or**, when WhatsApp hides the number, by the opaque sender id
   through `digest.member_wa_ids` (#146, §8.8). Four outcomes: matched · **unlinked** (an active
   member whose number is not linked yet — asked for the email on their MDS account, #125; never
   told they are inactive) · inactive · unknown. **Exactly one active member must match**, or the
   conversation takes the generic non-member path (`Build Generic`). This is the identity
   hard-fail (§5).
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
   Merge → …`, max 5 rounds) — Claude Sonnet with 29 gated **tools**. The model decides what to
   fetch and may look again; `First-Fetch Retry?` forces a retrieval when the first round tried to
   answer without one. **`p_phone` is injected server-side in Answer Parse; the tool schemas
   deliberately have no phone parameter the model could set.** `Answer Tool` dispatches by name:
   **every `event_*` tool** (`event_schedule`, `event_who` with `op:'people'`, and — by the same
   prefix match — `event_lookup` and `event_history`, which therefore never reach the catalog RPCs
   from the loop: **#123**, open) → the schedule route · `org_docs` → the kb route · `member_intro`
   → the intro route · `find` → the finder route — all on `digest.mds.co`, policy in git — and
   everything else → the Supabase RPC of the same name, where `Attach Embedding`'s `EXEC_NAME` map
   swaps the model's v1 names for the live executions (`content_search_v2`, `member_card_v2`,
   `member_match_v2`, `member_dossier_v2`, `chat_recommendations_v3`, `multi_source_v2`,
   `video_search_v2`, `partner_lookup_v2`; its `event_lookup_v3` / `event_history_v2` entries are
   reached only by the plan lane's zeroth fetch).
10. **Claims? → Fact Check → Gate Verdict** — a Haiku fact-gate compares the draft against the
    evidence actually retrieved this turn. Claim-free replies skip it. Unsupported claims trigger
    one regeneration; a second failure returns an honest "I could not verify this". A deterministic
    **link gate** additionally requires every URL to appear verbatim in the evidence.
11. **Format Reply → Billing Nudge → Eval (silent)? → Send Reply (Meta) → Followup
    Interactive?** — WhatsApp formatting (markdown → WhatsApp, `[SEND_IMAGE:]` / `[SEND_FILE:]`
    markers extracted, dangling orphan links stripped), an optional once-per-24h billing reminder,
    then either a real send or (for eval traffic, `wamid.SELFTEST*`) a silent path that skips Meta
    entirely. Buttons or a list picker that could not ride the body go out as a follow-up message.
12. **Save Conversation** — both turns are written to `digest.olivia_messages`, stamped with the
    member record and the retrieval plan (known gap #110: intro-tap turns are not saved).

**The web door (#169, 2026-09-08).** A second entrance on the same graph for the admin portal's *Ask Millie*
tool: `Web Inbound (POST)` (path `olivia-web-live` / `-staging`, header-auth credential `Olivia Web Secret`,
`responseMode: lastNode`) feeds `Log Inbound`, whose web branch normalises `{web:true, asker_email, mode, target,
text, thread_id}` into the WhatsApp shape — the retrieval principal is the probe member phone, set INSIDE the
node, and the wamid is generated as `wamid.SELFTEST_WEB_…`, so a web turn always takes the silent branch and can
never reach `Send Reply (Meta)`. `Load Recent Turns` reads `olivia_web_messages` by `thread_id` for web turns
(16-turn cap, no 24 h cut). After `Eval (silent)?` a `Web?` fork runs `Public?` → **Public Gate** (Public mode
only: `Classify Evidence (Supabase)` + `Fetch Name Index (Supabase)` → `Public Inputs` → `Public Redact` →
`Public Smooth (Claude)` [one Haiku call] → `Public Verify`) → `Format Web` → `Save Web (Supabase)` → `Web
Response` (a code node; **never a `respondToWebhook` node on this fork — one reachable from `WA Inbound (POST)`
500s every WhatsApp turn**). The deterministic gate lives in `scripts/olivia_loop/public_gate.js` and is embedded
verbatim; a name survives a public answer only when an OPEN evidence row of the turn contains it (open = what
EVERY member can see — decided per row off the restriction spine, #176; unknown is still closed), and a leftover
name or a new link after smoothing is repaired and, if it survives a second pass, fails the turn closed. Applied by
`scripts/olivia_loop/apply_169_web_door.py` + `apply_169_public_gate.py` (idempotent, staging first).

**Side workflows:**
- **Holding ladder** (`X1vzrW9Avqff3qRa`) — fires on inbound, sends "on it" / "still working" if an
  answer is slow. Fail-closed: it checks whether the answer already landed before each rung. Wired
  BEFORE routing in the fan-out (branch order is depth-first in n8n v1).
- **Daily review** (`xkX7wnIwxJLU7YgY`) — 17:00 ET, Claude reviews the last 24h of real
  conversations and posts findings to Slack `#automation-tests`.
- **Reminder sender** (`QhJw46Mr7LAP8fdz`) — **hourly**: marks stale sends failed, fetches due
  reminders, checks open windows, sends free-form in-window or the `mds_summit_reminder` template
  outside, records the outcome — then runs the **intro sweep** (`/api/olivia/intro op:'sweep'`,
  `onError: continueRegularOutput`) that expires 7-day-old pending intros.

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

- **Supabase project `nadtudwuwjhckotrngzn`** (Postgres 17.6) — schema `digest` (75 tables, 16 views, 116 functions) + schema `event` (18 tables, 33 FKs — the Summit run-of-show). Counts 2026-09-04.
- **Airtable Members DB `appou5JVr0WIrioWS`** — the member system of record.
- **Airtable Events base `appYa7blqkHazLMYf`** — events catalog + Event Roster (`tblfTLRfAqBhBZlc4`).
- **GroupOS** — videos, partners, app events (read via MCP today; a `GROUPOS_PAT` would make it a
  scheduled pull).

### 4.3 The core tables

| Table | Rows (2026-09-04) | What it is |
|---|---|---|
| `content_items` | 57,586 (48,502 embedded) | **The unified search index.** Every searchable thing — WhatsApp messages, chat digests, Facebook posts and comments, application answers, video transcript chunks — one row each, with `access_rule`, `sensitivity`, a full-text vector and a 1024-dim embedding (8,814 sub-30-char rows are unembedded by design). |
| `member_edges` | 145,449 | The knowledge graph: typed, weighted member↔member connections (rebuilt nightly — the count moves both ways). |
| `event_registrations` | 18,295 | The raw registration ledger, keyed to members. **Only the sync + `stamp_event_registrations()` may read it.** |
| `event_registrations_live` (view) | 14,380 | **#58 chokepoint — every reader uses this.** Drops `ticket_status` **Unconfirmed** (Airtable's fold of Canceled / Pending Approval / Not Going / Unpaid / Waitlist) and **No Show**. Unknown/NULL statuses stay visible on purpose: silently dropping a real registration is the worse failure. Since #96/#98 also the attendee-ACCESS authority. |
| `member_events` | 36,076 | **Append-only** behaviour log (see §7.3). |
| `member_expertise` | 16,630 | The expertise ledger v2: 742 members × 51 topics with evidence. |
| `member_attributes` | 5,757 (756 active) | The derived member profile — the canonical member population. |
| `member_profiles` | 6,037 | Raw Airtable field mirror (`at_fields` jsonb). |
| `member_profiles_team` (view) | 6,113 (2026-09-10) | **#172 the deny-list view — the ONLY way Team research mode reads member profiles.** Every `member_profiles` column, with the `at_fields` keys that stay closed in Team mode removed by regex (`removal · reason · ltv · score card · member score · notes · lead scor · budget` → 29 keys on 2026-09-10). Read by `millie_team_ro`, which holds no privilege on the table itself. The Team column of `OLIVIA_SHAREABLE_FIELDS.md` is this view written as prose. |
| `members` | 680 (617 linked) | **The WhatsApp channel layer** — phone → member. Not the population. |
| `member_wa_ids` | 108 | **#146:** opaque WhatsApp sender id → phone, for members who hide their number. Learned automatically when id and number arrive together; paired by hand (`olivia_link_wa_id.py`) when only the id does. |
| `member_email_alias` | 5,763 | **#100:** every address known to belong to a member, with its evidence (§4.10). |
| `events_catalog` / `videos_catalog` / `partners_catalog` | 1,452 / 1,083 / 511 | Source catalogs (hourly events; weekly videos + partners through the GroupOS task). Every published partner and event carries a vector (#159 — 75 partners were dark for a month because the invalidate trigger had no rebuild). All 2025–2026 videos carry a transcript-derived `summary`. |
| `olivia_sends` | 2,233 | **Delivery truth.** Every outbound send with the status Meta reports back asynchronously (`delivered`, `read`, `failed` + error code, `maintenance` from the relay). A 200 from `/messages` is not in here as delivery. |
| `partner_web_profile` | 506 | **#160** what each partner says on its OWN website (partner-stated, never member judgment): `summary`, `services[]`, `markets[]`, `pricing`, `people` jsonb (founders/leaders → `speakers.affiliation_partner_id` by name), `profile` jsonb, `crawl_status` (405 ok · 71 unreachable · 29 JS-only). Crawl `scripts/partner_web_crawl.py` → Sonnet extraction (`OLIVIA_PARTNER_WEB_EXTRACT.md`) → `scripts/load_partner_web_profiles.py --apply`. Refreshed by the weekly GroupOS task (step 4b). |
| `member_photos` | 639 | **#161** one cached portrait per active member in Storage bucket `member-photos` (320 px JPEG): `public_url`, `source` (`groupos` · `Picture URL` · `Headshots` · `Photo`), `width`, `fetched_at`. Written nightly by `cache_member_photos.py` (GroupOS avatar first, Airtable attachments ≥ 120 px second, none → initials tile). The Personas pages read ONLY this — never an Airtable attachment URL (they expire). 121 of 760 have no source yet; Facebook capture is a follow-up ticket. |
| `video_speaker_letters` | 270 | **#103 letter-mapping.** AAI transcripts hear voices as letters (Speaker A/B/C); this maps video+letter → speaker entity where evidence allows — `confidence` = self_intro · first_name_unique · solo_dominant. Loader `scripts/load_letter_map.py` (ASR guard: a heard name never mints an entity, it fuzzy-matches that video's own speakers, else review CSV). Unmapped letters stay letters BY DESIGN — a wrong name on a quote is worse than no name. |
| `speakers` / `speaker_aliases` / `video_speaker_links` / `video_partner_links` | 471 / — / ~1,250 / 129 | **#103 speaker identity space (2026-08-21).** One entity per human/company (`canonical` unique = "same means same"); `kind` member·partner·guest·unresolved; members EMAIL-evidenced (GroupOS mirror → `resolve_member_by_email`). Links carry `role` (speaker · participant · moderator) + `talk_seconds` (Zoom cue share) and `source` = evidence rung (speaker_ids · catalog · title_known · title_position · desc_known · desc_lead · zoom_cue). `video_partner_links` = partner sessions (video↔partner). Loaders: `load_speakers.py` (rungs A–D + `--rescan` guest→member promotion, `--coverage`), `load_participants.py` (Zoom cues). Run weekly by `zoom_weekly.py` step 4.5. ⚠️ `digest.video_speakers` is the pre-existing GroupOS speaker-USER mirror (234 rows, email = matching key; `member_record_id` is GroupOS-internal, never an AT id) — evidence source, not the identity store. Zoom transcripts carry REAL NAMES per cue; AAI = Speaker A/B/C (letter-mapping + frame-OCR = open rungs). |
| `video_access` | 44,972 | **#101/#150: who may see each RESTRICTED GroupOS video.** Sources: the dev's read-path mirror export (`real_match` rows only), Andy's CSV exports, the #150 Summit grants (attendees + staff, `scripts/sql/150_summit_video_grants.sql`) and, since 2026-09-03, the per-member `videos_list(for_user_id)` sweep (`source='api'`, 7,936 rows, loader `video_access_from_sweep.py`). **All 424 restricted videos carry grants (0 uncovered).** `at_member_id` via `resolve_member_by_email()`; NULL = unresolvable, kept so the grant activates when the alias lands (93 rows). |
| `olivia_webhook_events` | 16,005 | **#75:** every inbound MESSAGE event persisted verbatim BEFORE any parse (text/interactive/reaction/media; statuses excluded). The only place template quick-reply **button** taps land — the workflow does not persist `msg_type='button'` into `olivia_messages`. |
| `olivia_recommendations` | 20,192 | **The equalizer's memory (#93/#95):** every name she recommends, per asker + lane. Read by all recommendation lanes (30d per-asker downrank · 7d global spread · LRU cycling). |
| `olivia_intros` | 6 | **#97 consent ledger (live since 2026-08-22):** pending → accepted / declined / expired / unreachable; no number moves before `accepted`. One intro has run end-to-end in the wild (Ben Anderson → Dat Le, 2026-08-31, accepted in 1h51m). |
| `docs` / `doc_entries` | 4 / 50 | **#18 org knowledge library** — team documents (FAQs, SOPs), audience fail-closed to staff, served by the `/api/olivia/kb` route. |
| `olivia_messages` | 12,981 (1,385 real member turns from 143 members) | Conversation history, stamped with the member record; the rest is eval/probe traffic (`wamid.SELFTEST*`). |
| `olivia_web_messages` | new (#169) | **Admin web chat turns** (Ask Millie: modes `test` · `public` · `team`), keyed by `thread_id` + staff `asker_email`; carries `answer_md`, `notes`, `sources`, `evidence_classes`, `redactions`, `source_summary`, `metrics`. service_role only, RLS on. Never member WhatsApp traffic — the daily review must not read it. |

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

### 4.9 The Summit schedule — the `event` schema (#85, 2026-08-18)

The run-of-show for a live event: what happens, where, when, who speaks and **who may see it**.
Loaded from a GroupOS export by `scripts/load_event_graph.py` — idempotent **and reconciling**
(#113, 2026-08-23): a run makes the `event` schema EQUAL the export for that event. Rows the export no
longer contains are deleted in FK-safe order (children first; **`event.people` never**), so an unticked
audience box or a cancelled activity actually disappears instead of gating forever.

**Refresh runbook**

```bash
python3 scripts/load_event_graph.py ~/Downloads/<export>.json --dry-run   # GETs only, writes nothing
python3 scripts/load_event_graph.py ~/Downloads/<export>.json             # report -> upsert -> reconcile -> after-counts
python3 scripts/event_lane.py --self-test                                  # golden invariant must pass
```

The report names rows, never ids (`~ Closing Dinner: starts_at Tue 25 Aug 18:03 -> 18:30`). Read the
`- ` (removal) lines **and** any `!! skipping` lines before a real run. Flags: `--no-reconcile` upserts
only and deliberately leaves `loaded_at` unstamped; `--new-event` is required to create a second event
graph (without it an unknown event id is refused — see trap 6).

**Provenance:** `event.events.source_scanned_at` = the `_meta.scannedAt` of the loaded export;
`loaded_at` = the last time a full upsert **and** reconcile completed. `loaded_at` older than
`source_scanned_at` means deletions are still outstanding.

```
events ─┬─ activities ── activity_audience → participant_types
        │       ├── activity_person_grants → people
        │       └── sessions ── session_speakers → people
        ├─ locations ── rooms
        ├─ attendees (event, person, type)      ← type is PER EVENT, never a property of the person
        ├─ reminders (#86)
        └─ faqs · tickets · orders · check_ins
```

**Eighteen tables, 33 foreign keys, no views and no functions** (2026-09-04; live counts after the
#113 refresh: 86 activities · 234 people · 199 attendees · 0 pending reminders). `event.people.at_member_id`
is a real FK to `digest.member_profiles`, so an attendee resolves to an MDS member where the link holds
and stays NULL where it does not (guests, external speakers).

**Registration status has two sources that can disagree (#147, PAUSED 2026-08-25 on Andy's
authority call).** The agenda (`event.attendees`, from the GroupOS export) and who-to-meet
(`event_registrations_live`, from the Airtable roster) answered "am I registered?" differently for
36 members. Shipped so far: `member_alias_ids()` (duplicate-record folding), `registration_status()`
and `is_registered()`, and `event_who` reads them (130 → 145 registered, 15 recognised, 0 lost).
Not started: the event resolver and the schedule route. Until ruled, one function with two facets is
the recommended shape.

**The visibility rule lives OUTSIDE the database** — see §12. Written once, in the route:

```
visible(person, activity) =
     (person's participant types AT THIS EVENT) ∩ (activity's audience) ≠ ∅
  OR person is on the activity's grant list
```

An unchecked participant box means *not invited*, never *must not know*: it blocks only somebody
whose **every** type is unchecked. Khalid Abdulla holds a Speaker row and a Member row; Focus Groups
has Speaker unchecked and Member checked, and he gets in on Member.

**Golden test** (`scripts/event_lane.py --self-test`): after the 2026-08-23 refresh a plain Member
sees **7** activities on day one and the Women's Lunch grantee **8**. **The invariant is the test, not
the integers** — the grantee sees exactly one more than a grant-less Member, and it is the Women's
Lunch. When a refresh moves the numbers, re-derive them from the data, state what changed in GroupOS,
and update the script and this section in the same commit.

**Six traps in the export and the loader — do not re-learn them:**
1. **Milan leftovers.** The event was cloned from Milan 2025; 41 of 91 activities carry `isDelete`.
   Import them and she serves last year's Italian agenda.
2. **The legacy audience booleans lie.** `member`/`speaker`/`partner`/`guest` are all `false` on
   records whose `accessRoles` grants three roles. **`accessRoles` governs.**
3. **`timeZone` is a display label, not IANA** — `"(UTC+08:00) Asia/Singapore Singapore Standard
   Time"`. Times ship as local wall-clock strings with no offset, which is exactly how
   `digest.events_catalog.start_at` ended up eight hours wrong. The loader extracts and validates
   the IANA zone, stores true instants, and keeps the raw strings in `source_*` for audit only.
4. **A "new" export can be an old scan.** The file handed over on 2026-08-22 was a 17-Aug scan — four
   of the five people who registered 18–21 Aug were missing. The freshness guard compares
   `_meta.scannedAt` with `digest.event_registrations_live` and names anyone who registered later; a
   `!!` line there means the export cannot know those people. Get a fresh scan, do not load.
5. **GroupOS recreates a document when a role changes** — new `_id`, same natural key. `attendees`
   therefore upserts on `on_conflict=event_id,person_id,participant_type_id` and its `id` is rewritten;
   that is safe **only because nothing FK-references `event.attendees.id`** (verified 2026-08-23).
   `participant_types` is the opposite: its `id` IS referenced (`attendees` RESTRICT,
   `activity_audience` CASCADE), so a recreated role **aborts the run before any write**, naming role,
   old id and new id. Recovery: re-point the children to the new id, then re-run — never rewrite the
   type's `id`.
6. **One export = one event.** The lane serves `events?order=starts_at.desc&limit=1` when no
   `event_id` is passed, so loading a later-starting event would silently become the schedule Millie
   answers from. An unknown event id is refused unless `--new-event` is passed. Check the
   `event <id> · <title>` line before proceeding.

**Two limits the loader hit in production (2026-08-23), both fixed — do not undo them:** request bodies
go to `curl` on **stdin** (`--data-binary @-`), never as an argv element (macOS ARG_MAX ~1 MB; one
activity's `long_description` was 92 KB and the batch serialised to ~1 MB), and `datetime.fromisoformat`
under Apple's Python 3.9 rejects the 2-digit fractional seconds PostgREST returns (`.79`), so `_instant`
normalises the fraction — without it every re-run reported phantom "changed" rows.

**A loader SKIP is not an export removal.** Rows the loader cannot build (unparseable time, `end <=
start`, an attendee whose person or role does not resolve) are printed and **protected** from the
reconcile — otherwise one GroupOS data-entry slip would delete a live activity together with its
audience, grants and reminders by CASCADE.

**Reminders (#86).** `event.reminders` hangs off the person and the activity or session, never a
wall-clock string. Three ways to say when, and only two can be trusted to the model:
`in_minutes` (computed server-side), `lead` (minutes before the start) and `at` (a resolved
instant). **The model does not know the current time** — asked for "in 5 minutes" it produced a
timestamp four hours stale, so anything relative is computed here. Delivery: free-form inside the
member's 24-hour window, the approved `mds_summit_reminder` UTILITY template outside it.

**Who to meet (#87).** The `people` op matches the asker against **`event.attendees`**, never the
whole member roster — matching across all 748 sent an attendee to find somebody in Florida. It says
nothing about which room anyone will be in, because nobody registers for a session.

**One roster per question (#89).** **Headcounts and "who is coming" read
`digest.event_registrations_live`** — the live-synced ticket ledger — and nothing else;
**`event.attendees` is the ROOM roster**, used only to gate audiences and match people, refreshed
only when a new GroupOS export is loaded, and never a headcount source (as of 2026-08-18 zero
`digest.*` functions read it — both facts stamped as table comments in migration
`event_roster_authority_comments_20260818`). `event.people.at_member_id` is resolved by the
loader's three-rung ladder (profile email → registration-email bridge → unique name, conservative;
suspects logged, never guessed) — 170 of 199 Summit people linked; the remainder are orgs, vendors,
nickname cases and Members-DB duplicate records, listed on the #89 ticket for Andy.

**Timezones (Andy, 2026-08-17):** never stored — it breaks the moment someone travels. WhatsApp
sends an instant, never a zone. In-person answers always use the venue's zone, named; a virtual
session carries the content's zone *and* the member's saved-location zone.

**"Today" is the venue's day (#114, 2026-08-22/23 — promoted `bbd597b7`).** The model anchors on US
Eastern; the Summit venue is 12 hours ahead, so for half of every day "today" is already tomorrow
there. The schedule route resolves `at=today|tomorrow|yesterday|<weekday>|YYYY-MM-DD|instant` in the
event's zone (`mds-digest-web/src/lib/schedule-day.ts`, pure + vitest) and returns `now_at_venue` on
every answer; the seed tells the model to pass the word, never a computed date. **`next` is the rest of
the venue-day** when more than three activities remain, else the classic next three reaching into
tomorrow (`pickNext`; the answer carries `next_scope`, `day`/`day_label` = the day of the items listed,
`asked_day`, `remaining_today`) — a hard cap of 3 once made a half-day look like the whole day. A
member naming a date (`at=2026-08-22`) is still honoured; an impossible date falls back to venue-today
(`resolved_from: fallback`). Virtual events are not covered — the member's zone is unknown by design.
Test harness note: `olivia_selftest.py` turns are silent (no Meta send) — proof lives in the
executions, Andy sees it only by texting Millie himself.

### 4.10 Email aliases — one member, all their known addresses (#100, 2026-08-20)

A member's GroupOS grants, registrations and payments do not all use the Airtable Preferred
Email. `digest.member_email_alias` holds every address known to belong to a member, with the
evidence in `source`: `preferred` (Members-DB Preferred Email) · `stripe` (Stripe Customer
Email — a payment record) · `admin_field` (Airtable "Associated Emails (Admin)") ·
`name_match_approved` (a name match a human approved). A bare name match is not in the CHECK
vocabulary — it cannot be inserted; `scripts/propose_member_email_aliases.py` writes a review
CSV and `scripts/writeback_member_email_aliases.py` applies approvals to **Airtable first**
(the system of record), re-reads to confirm, then mirrors.

**The single entry point is `digest.resolve_member_by_email(p_email)`.** It prefers the
active record: one record wins outright; several records sharing the address with exactly
one ACTIVE resolve to it; anything else returns NULL rather than guessing which human owns
the address. That rule exists because MDS holds duplicate records for the same person — 49
addresses sit on more than one record. Do not match emails against `member_profiles.email`
directly in new code; go through the resolver.

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
- **A hidden number is still an identity (#146).** WhatsApp lets a member hide their number; Meta
  then delivers only an opaque id (`CA.1068…`). `digest.member_wa_ids` pairs id → phone; the front
  door (`olivia_front_door_v2`) resolves either. Pairing is automatic when both arrive together
  and **human-confirmed** otherwise (§8.8) — the wrong pairing hands someone another member's chats.
- **An absent status is not an inactive membership (#125).** A paying member whose number is not
  linked yet is `unlinked`, gets asked for the email on their MDS account, and is never told their
  membership is inactive (53 members were getting that false claim; now 0).
- **The doorman counts members, not phones (#128).** `resolve_asker` once refused any member with
  two numbers on file; a member with two phone rows is one member.
- **Attendee access (#96/#98) is registration-based, never presence-based:** whether an asker may
  see an event's attendee names is checked against `event_registrations_live` for THAT event.
  `event.people` is data — it carries staff and test rows (a test row once granted names on the
  live route; that class is closed).
- **Known identity debt (Andy's desk):** duplicate member-record clusters in the Members DB (the
  #147 disagreement, two records sharing one email colliding in #150's grants). Never deleted by
  us — the never-delete-a-member rule stands; duplicates are merged or flagged by Andy only.

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
unembedded (8,814 of them on 2026-09-04) — they stay keyword- and thread-reachable but do not
pollute meaning search. Daily "No activity" digest stubs are excluded from the index entirely.
The HNSW index is 376 MB and has 26,305 recorded scans — the v1-era zero is history.

**Recency in fusion (#153 + the #102 slice, 2026-08-26):** video ranking carries a bounded decay
(+0.006 under 60 days, +0.003 under 180; an RRF leg maxes at 0.0164, so it reorders near-ties and
cannot lift junk) — a 2025 talk no longer ties a running-Summit one.

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
| `public_gate_classify` / `public_gate_name_index` | **#169 Public Gate** — classify a turn's evidence keys (urls / source ids) as `public` or `closed`. **Public = OPEN TO EVERY MDS MEMBER; closed = restricted to SOME members. The line is per ROW, off the restriction spine, never per source type (#176 correction 2, 2026-09-08 — this reverses BOTH fix round 3 and the first #176 pass).** Andy: *"public means all members, but not people outside the MDS; restricted means this content is restricted to some members. Facebook is open source; it's public by definition. The only restricted sources are some WA chats (you should know it) and some videos (we have the spine with restriction rules)."* **Public (open)** = `fb_post` / `fb_comment` · `wa_message` / `wa_digest` whose `access_rule->>'chat'` joins a `digest.chats` row with `verification_required = false` (12 of 18 chats) · `call_transcript` whose recording — found by the `app.mds.co/videos/<24 hex>` in the row's OWN url — has `videos_catalog.access_restriction = 'public'` · the video library by id **and** by that link, same column · published partner listings via `member_partner_url` (guarded by `status = 'published'` + `access_restriction = 'public'`) · events by `public_page_url` **and** by `app_url`. All content branches keep `sensitivity = 'normal'` as a secondary fail-closed guard — it is load-bearing on 401 transcript rows where the two spines disagree, and the more restrictive of the two wins. **Closed (restricted)** = a `verification_required` chat (Centurion 20M+, Large SKU, Real Estate, Supplements, TikTok) · a `restricted` recording and its transcripts · `application` · **unknown**: a NULL `verification_required` (MDS 2026 New Members), a chat name absent from `digest.chats`, a transcript with no recording, a key no evidence row produced. A restricted source may still INFORM an answer: paraphrase only, no names, no verbatim quotes, said so in the notes. The `source` column names the REASON (`wa:open` · `wa:verified` · `wa:unknown` · `wa:unknown-chat` · `transcript:public` · `transcript:restricted` · `video:public` · `video:restricted` · `content:fb_post` · `partner` · `event`) and `scripts/olivia_leak_gate.py` asserts on it. **Trap:** join a transcript to its recording by the row's URL, not its `source_id` — 3,204 of 13,507 transcript source_ids are a base64 call id (`37yVhe+qTbaVUssWHoYOsQ==#41`), not `<24 hex>#<chunk>`; the url is right on all 13,507. **Trap:** a transcript's own url IS its recording's `app.mds.co/videos/<id>` link, so one key comes back from two branches; they agree now (both read the same `videos_catalog` row) and `Public Redact` still collapses duplicate keys most-restrictively. The member/speaker name index (two-word names ≥ 5 chars; organisation rows `MDS %` / `% MDS` and placeholder rows — a digit, an `@`, a `test`/`testing` token, or an English function word as the first token — excluded; **5,320 people, 2026-09-08**) is what the redaction pass masks against; the module (`scripts/olivia_loop/public_gate.js`) matches with unicode-aware boundaries after NFC + invisible-character normalisation on both sides, masks variants (ALL CAPS, middle initial, hyphen/space, possessive, LONE first names ≥ 4 chars), strips every non-public link, and `Public Verify` repairs or refuses anything that survives. Called only by the workflow's Public Gate nodes. **Trap:** these are shared Postgres functions — a redefinition is live on PROD the moment it is applied; it does not ride staging → promote and has no snapshot (rollback = re-apply the previous body from `db/functions/`). |
| `expertise_search` | Members by what they know (keyword + embedding, RRF) |
| `member_count` | Counting members by attribute, with breakdowns |
| `member_dossier` / `member_billing` | The asker's own record / own billing |
| `event_lookup` / `event_who` / `event_history` | Events, attendees, own registrations |
| `chapter_info` / `community_info` | Chapters with live stats / community numbers |
| `partner_lookup` / `video_search` / `video_file_for_send` | Partner deals / video library / file sending |
| `multi_source` | One-shot fan-out across all six source families |
| `chat_info` / `chat_recommendations` | Chat metadata / which **WhatsApp chats** to join. **A CHAPTER is not a chat** — chapter questions route to `community` (#84 D1); the router had no chapter lane at all until 2026-08-17 |
| `report_create` | Files a member report |
| `form_field_history` / `my_form_answers` | The asker's OWN form answers (census, application, check-ins): one field across time / one form's answers. Self only |
| `find` | Composable member filters — one lane, every data layer (#108). **A route, not an RPC** — `POST /api/olivia/find` (§6.3) |
| `event_schedule` | The Summit lane — schedule · next · where · speakers · sessions · recommend · people · reminders. **A route** — `/api/olivia/schedule` (§4.9) |
| `member_intro` | "Connect me with …" — consent-first brokered intros. **A route** — `/api/olivia/intro` (§8.7) |
| `org_docs` | The team's own written docs (FAQs, SOPs). **A route** — `/api/olivia/kb` (#18) |

That is the model's view: **29 tool names** (Answer Seed, 2026-09-04). The executions behind them
are the `_v2`/`_v3` functions (`EXEC_NAME` map, §3 step 9); the model keeps the v1 names. ⚠️ The
four `event_*` names all go to the schedule route by prefix match, so from the loop `event_lookup`
and `event_history` answer from the `event` schema, never from the events catalog RPCs — **#123**
(open; #144's wrong 2027-event answers wait on it).
What the v2/v3 layer adds, beyond personalization (§7): **`link` on every named person** (#154 —
`digest.member_link()` is the ONE definition of a member's link, 718 of 741 actives resolve),
`event_lookup_v3` (`what_it_is`, `room`), `chat_recommendations_v3` (`why`, `strength_note`),
`video_search_v2` (`is_restricted` = restricted **for this asker** (#150), `event_total` = the
event's real session count (#151), `summary`, `p_call_type` / `p_order` / `p_video_id`),
`partner_lookup_v2` (`fit_reason`, `event_offer*`, and the #160 web fields).

**Grant discipline:** `DROP FUNCTION` + `CREATE` **resets the EXECUTE grant to PUBLIC** — meaning
anon could call it. Always `revoke all … from public` and re-grant to `service_role` after a
drop+create. `CREATE OR REPLACE` preserves grants; prefer it. The leak gate checks this.

**After any RPC DDL:** `notify pgrst, 'reload schema'` and then hammer the REST path — stale
connection-pool caches produce *intermittent* 404s that look exactly like a quality regression.

**The Team research surface (#172, live on prod 2026-09-10) — NOT part of Olivia's tool set.**
`digest.team_sql(p_sql, p_max_rows)` runs one `SELECT`/`WITH`/`VALUES` over `digest` + `event` **as the
NOLOGIN role `millie_team_ro`** (SECURITY DEFINER, owned by that role), forces `transaction_read_only`
for the rest of the PostgREST transaction (proven: `net.http_post` → `25006`), wraps the query in
`select * from (…) q limit N+1` (a second statement is a syntax error; a data-modifying CTE dies at
`0A000`), returns `{rows,row_count,truncated}` or the verbatim Postgres error, and is executable by
`service_role` only. The role reads every table and view in the two schemas EXCEPT `member_profiles`
(→ the `member_profiles_team` view), `olivia_web_messages`, the OTP hash columns on `members` and
`token_hash` on `member_sessions`; it holds no CREATE, no `pg_read_all_data`, no USAGE on `vault` /
`auth` / `storage`, and cannot execute the secret-returning functions. It is the SQL tool of the Team
research loop that lives in `mds-digest-web` (§3's callout), never reachable from the n8n graph — 21
`#172` gate checks pin all of this plus the prod graph hash. Migration
`scripts/sql/20260911_team_sql_172.sql` (+ `…172b`: the ONE private EXECUTE grant, `is_active_member_status(text)`, because
`member_identity` and `member_phones` call it and a function inside a view runs as the caller; the gate pins that set exactly);
proof `scripts/test_172_team_sql.py` (20 live checks). `member_links` is dark to the role (#197): its helper reads the raw table.

**The `video_access` rule type (#101, 2026-08-20).** Transcript chunks from a RESTRICTED video carry
`access_rule = {"type":"video_access","video_id":…}` with `sensitivity='restricted'`.
`content_search_v2` returns them ONLY when `digest.video_access` grants that video to the resolved
asker — the consent flag alone does not expose them, and every other reader fails closed on the
unknown type. `video_search` gates the same way: entitled → full treatment (description, cliff
notes, summary, full-tsv matching, no downrank); not entitled → title/speakers/date/link + the
restricted marker. Attachments stay a PUBLIC-video feature even for entitled askers
(`video_file_for_send` validates public-only, and surfacing them leaked the raw `file_key`).
Andy's quote ruling: quote, summarize, TLDR, answer "what exactly did he say" — never a full
transcript; the ~1,400-char chunk is the largest retrievable unit and no lane concatenates.
⚠️ **That last clause is the ruling's whole safety argument, and for older rows it is NOT TRUE.**
`chunk()` sized passages between cues but never split a single oversized cue, and AssemblyAI returns
a whole talk as ONE utterance when it hears one speaker. Found 2026-08-27: 1,423 chunks over 4,000
chars, worst 40,934 — including **581 chunks across 138 RESTRICTED videos, worst 23,632**, where one
chunk is most of a talk. The access gate is unaffected (an unentitled asker still gets nothing, gate
green) but an ENTITLED asker can retrieve far more than the ruling intends. The producer is fixed
(`split_long_cues()` in `zoom_transcripts.py` — sentence-bounded, timestamps interpolated by character
offset); **re-chunking the existing rows is still open.**
Restricted videos embed METADATA ONLY (`embed_videos.py`), so the vector branch cannot leak content.
Transcript coverage: Zoom (#70) where Zoom hosted; AssemblyAI (`meta.provenance='assemblyai'`,
`scripts/aai_transcripts.py`) for the in-person/hybrid videos it never reached — speakers
stay `Speaker A/B/C`, never guessed names.

### 6.3 `find` — one lane, composable filters, every data layer (#108)

Every other lane in this chapter is a Postgres RPC; `find` is not — it is a Next.js route,
`POST https://digest.mds.co/api/olivia/find` (mds-digest-web), header `X-Olivia-Secret`, reads only
through PostgREST and **writes nothing**. It exists because filters did not compose: "resellers
coming to the Summit" needs chat membership AND business model AND event attendance in one request,
and no RPC above ever took more than a handful of fixed parameters.

**The request is a boolean tree** (Andy: "filters with groups and conditions, like IFTTT"). Groups:
`all` = AND, `any` = OR, `not` = exclude; a leaf is `{field: value}`; a list value is any-of
(`{"segment":["reseller","supplements"]}` = either). Trees nest to depth 4, cap at 20 leaves, and
must carry at least one leaf — there is no whole-database dump. The response echoes the normalised
tree as `where_echo`; a follow-up narrows by wrapping it in one more `all` — no server-side session.
Every matched person carries `reasons`: the leaves of the tree that were actually true for them, so
"in MDS Resellers" / "Spain" / "attending MDS Summit Singapore" are exactly what they matched, in
the tree's own order.

**Validation is closed and class-aware.** An unknown field is `400 unknown filter`; a 🔴 field is
rejected even as a filter; `business_model` as a raw leaf is `400 … use segment`; a what-group leaf
(terms, sources, chat content, …) is `400 not served yet` in phase 1, so the model falls back to
`content_search` / `video_search` honestly instead of silently widening the answer.

**The disclosure engine — filtering and showing are different rights.** Every field carries one
class: 🟢 **show** (filterable, groupable, printable beside a name — the member-card set, plus chat
membership and event attendance) · 🟡 **aggregate** (filterable and groupable, never beside a name —
SKU count, brands, employees, age, revenue, activity) · 🔴 **internal** (never filterable, never
returned — exact revenue, email, phone, Stripe, internal ids). Ten rules enforce it: R1 only 🟢/🟡
may filter · R2 any active 🟡 filter forces counts/breakdown, never names · R3 reasons quote 🟢 only
· R4 buckets under 3 report "fewer than 3" under a 🟡 filter · R5 event names need the asker
registered for EVERY named event · R6 respects `video_access` · R7 defers to the existing
content-gate path · R8 excludes Staff/removed/unknown-status from names AND totals · R9 ≤10 names +
the true total, no score/rank, asker never their own match, deterministic order, writes nothing ·
**R10 (chats, Andy's ruling)** — chat membership is a signal Millie may use for ANYONE deciding who
matches a concept, but a chat is only ever *named* to its own members; a direct `chat:` filter by a
non-member returns counts/breakdowns only, never names; what is said in a chat still goes through R7.

**Concept signals** are recognised from every declared/behavioural source at once, OR-ed together
(the reason names whichever signal fired, subject to R10):

| segment | signals | class |
|---|---|---|
| reseller | biz model (Wholesale/Arbitrage · Wholesale, Resale & Dropshipping) OR chat *MDS Resellers* | 🟢 |
| private label / brand owner | biz model (Private Label · Own Brand) | 🟢 |
| agency | biz model (Brand Mgmt/Agency) | 🟢 |
| oem | biz model (OEM Design & Development) | 🟢 |
| supplements / tiktok / dtc / retail | chat *MDS Supplements/TikTok/DTC/Retail* OR the matching profile flag | 🟢 |
| large sku / under 30 | chat *MDS Large SKU/Under 30* OR the SKU-count/age attribute | 🟡 counts only |

**Data caveats to say, not hide:** business model is self-declared and as old as the member's last
form; chat membership is *behaviour*, so a brand owner can sit in *MDS Resellers* to watch; the
label vocabulary is dirty (legacy + app-v3 sets, plus 8 rows where two labels were joined by a stray
apostrophe); and **five** catalog rows match "Summit Singapore" (the Summit itself plus Night Out,
Speaker's Lunch, Women's Lunch, Pre-Event Dinner) — resolution prefers the exact name, then the
shortest, and always echoes what it picked.

Phase 1 (2026-08-23) serves `return: people | count | breakdown` and the field registry above.
Phase 2/3 (own plans, #116) add `content | videos | events | partners` through the same tree,
registry, engine and gate — that reuse is the whole reason `find` is one lane. Full spec:
`docs/superpowers/specs/2026-08-22-finder-design.md`.

**Trap:** `rpc/geo_country_set` / `geo_state_set` / `country_fold` are the geo SSOT; `geo_state_set`
needs EXECUTE on nested `digest.attr_state` for `service_role` (granted 2026-08-23,
`scripts/sql/20260823_grant_attr_state_service_role.sql`); the gate's two geo checks make a lost
grant loud.

---

## 7. The personalization data — and the lanes that consume it (#29)

Three layers exist and refresh nightly. **Since #29 (staged 2026-08-03) the lanes consume them**
through side-by-side v2 RPCs — v1 stays untouched; the workflow's last-inch v1→v2 name map (the
same execution-layer swap as `content_search_v2`) decides which runs, so prod flips only at
promote.

### 7.1 Expertise ledger — `member_expertise`
Every active member scored across **18 parent topics + 33 subtopics** (topics live in the
`expertise_topics` **table** — a new topic is an INSERT, not a code change; a subtopic is a row
with `parent` set, and it flows into every consumer automatically because they all read
`expertise_topics.terms`). Subtopics graduate via the quarterly evidence-density check (Andy
2026-08-19): a subtopic exists only when real members can be ranked on it. Score formula, **v2
(shipped 2026-08-19, #94)**:

```
(2.0·ln(1+posts) + 0.7·ln(1+comments) + 3.0·min(videos_spoken,5)
  + 1.5·business_affinity + 1.0·ln(1+persona_gives) + 1.2·ln(1+form_hits))
  × revenue band multiplier (1-5M 1.0 · 5-10M 1.15 · 10-20M 1.3 · 20M+ 1.5)
```
where **activity decays** (each conversation item weighs `exp(-age/17.312mo)` — 12-month
half-life), **speaking decays slower** (each video weighs by a 24-month half-life),
**reactions amplify a post** (`posts` counts each post as `1 + ln(1+reactions)/4`),
**forms are the floor for silent members** (`form_hits` = distinct latest-form answers matching
the topic's terms — 594 members are scoreable on forms alone), and the final score
**floors at 40% of the member's all-time `peak_score`** — decayed activity fades rank, never
erases proven expertise (`peak_floor_applied` appears in evidence when the floor holds a row up).
Weakness score = `ln(1 + persona asks/challenges hits)`. Every row carries an `evidence` jsonb so
any score can be explained. Rank and percentile are computed per topic.

**Matching rule (the substring trap, twice now):** every component — content, videos, forms, biz
affinity, persona — matches through `phraseto_tsquery` on `expertise_topics.terms`. Never bare
`ilike '%term%'`: `'ai' in Em(ai)l` (2026-08-07) and `'vat' in Pri(vat)e Label` + `'str' in
industrial/strategy` (2026-08-19, caught same-day: 722/748 members scored on Real Estate
Investing) are the two class incidents. Verifier: `scripts/verify_expertise_v2.py` (9 checks,
exit 1 on any fail).

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

**Recommendation model (Andy, 2026-08-19):** the written logic is proficiency FIRST (ledger
percentile on the matched topics, deciles = tiers), member VALUE (`engagement_score`) only among
tier-equals — **on the ADVICE lane** (`member_match`: "who can help me with X"). The **MEET lane**
(event `people` op: "who should I meet") inverts: novelty + the equalizer first, proficiency
tiebreaks. The **equalizer** = `digest.olivia_recommendations` (every recommended name logged):
hard 30-day per-asker no-repeat + soft 7-day global spread, so no member gets buried in DMs for
being excellent. **Since #95 (2026-08-19/20) the equalizer covers the ADVICE lanes too:**
`member_match_v2` (repeats sink below fresh names of the same match tier) and `expertise_search`
(relevance stays primary — RRF ×0.6 on a 30d repeat, 7d exposure damps only the engagement
tiebreak). Two smoke-caught refinements (2026-08-20): **audits opt out via the `X-Olivia-Audit`
header** (read from PostgREST `request.headers` — the earlier `p_limit>30` heuristic silenced
logging on the real plan lane, which calls with limit 60) and **LRU cycling** — among repeats the
least-recently-recommended name leads, so an exhausted pool rotates instead of freezing (every
shown name re-logs to advance the cycle; the gate's rpc() sends the audit header and never writes).
`multi_source`/`_v2` are VOLATILE so their members sections inherit rotation. All four write
`olivia_recommendations` with their lane name. A matcher sample is never a census — presence counts come from the registrations
ledger via the `chapter` param. **Ledger v2 SHIPPED 2026-08-19** (§7.1 above is the live
formula); plan preserved at `docs/superpowers/plans/2026-08-19-expertise-ledger-v2.md`.

### 7.4 The consumers (#29) — one dossier, five personalized lanes

`digest.member_topic_profile(atid)` (internal, no REST grant) turns a member's ledger rows into
matchable topic words; everything below reads it. All v2s are `SECURITY DEFINER`, ACL
`{postgres, service_role}`, and the gate proves each one fails closed (unknown/canceled phone,
anon) **plus** that personalization never widens access (`member_match_v2 ⊆ v1 pool`,
`event_lookup_v2 = v1 set re-ranked`).

| lane | function | what personalizes |
|---|---|---|
| dossier | `member_dossier_v2` | v1 + `strength` (top ledger topics, evidence-worded) · `working_on` (framed "building up", never "weak") · `behaviour` (90d event-log counts) · `circle` (top graph neighbours, typed) |
| events | `event_lookup_v2` | BROWSE re-rank: topic affinity (word-boundary match on name/audience/chapter) → circle attendance → v1 order; booked events sink, never re-pitched. Specific asks keep v1/#47 order |
| events ctx | `event_history_v2` | v1 + `interest` rows so the prompt argues fits from THEIR topics |
| chats | `chat_recommendations_v2` | eligibility identical to v1; order = topic fit → circle presence; new `why` column ("fits your focus: …") rendered in the canned list |
| people | `member_match_v2` | v1 body + complementary boost: candidates strong where the asker is building up float up, with the coarse reason "knows <topic>" |
| Q&A (solve/multi) | `multi_source_v2` | v1 + a `me` section (persona summary, strengths, working-on, location); its events call uses `event_lookup_v2` |

**The loop is the only llm answering path** (Build Prompt is legacy for llm lanes). Answer Seed
therefore does three things: its preload filter keeps dossier-shaped rows, event rows and the
multi_source jsonb (before #29 it silently dropped them); when the zeroth fetch carries `me` it
renders a deterministic **ABOUT THE ASKER** block into the seed user message; and the
persona-driven rule adds the framing constraints (tailor silently · never recite · never call an
area weak). Loop tool calls execute the v2s via the `EXEC_NAME` map in Attach Embedding — the
model keeps the v1 names.

### 7.5 Brokered intros (#97) — a sixth consumer, outside the lane table

`digest.olivia_intros` reads the **equalizer log** (`olivia_recommendations`, §7.3) as its
candidate filter: a member can only be introduced to someone Olivia actually recommended to
*them*, in the last 30 days — never a cold match. It is not a `_v2` RPC lane like the five above
(it writes, has its own state machine, and its own eligibility gate on top of the recommendation
filter), so it keeps its own runbook entry rather than a row in the table: **§8.7**.

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
python3 scripts/olivia_leak_gate.py     # 345 checks (2026-09-08, +9 web door / Public Gate: secret · no Meta send · no olivia_messages write · module embed fresh on the SHIP target · Public path wired · strict 401/403; +13 from #176 correction 2: both sides of the restriction spine + the paged name index), ~3 min, free — run it again AFTER a promote to re-assert prod (check 4 judges staging first)
```
It inserts canary rows with every access rule and sensitivity, asks the real RPCs for them as
several different members, and asserts what must *not* come back. It also verifies anon lockout,
cancelled-member refusal, field allowlists, grant hygiene, the #96 attendee cap, the finder's
R1–R10, the #97 no-number-before-accept half, Staff invisibility (#106), the `link` columns (#154)
and that every published partner/event carries a vector (#159 — rows synced in the last 30h are
exempt, they wait for the nightly embed), then cleans up after itself. Its `rpc()` sends
`X-Olivia-Audit`, so gate runs never rotate anyone's recommendation state. **Green before every
ship. No exceptions. Read the exit code, never `| tail`.** 26 route checks need `digest.mds.co` to
resolve — from Andy's Mac it sometimes SERVFAILs; point them at `mds-digest-web.onrender.com` then.

Its twin is `scripts/prod_pulse.py` — read-only, directional against a saved baseline: the gate
proves retrieval REFUSES, the pulse proves she still ANSWERS (row counts not falling, RPCs
responding, failed sends not rising). Run it before and after risky steps; exit 1 = stop. Re-save
the baseline (`--save-baseline`) at the start of each tier, or nightly rebuilds (the graph) and old
send failures read as regressions — as they did on 2026-09-04.

### 8.2b After ANY migration: re-export the SQL layer (#65)

```bash
python3 scripts/db_export_schema.py     # DB -> files
git diff db/                            # this is your code review
git add db && git commit
```

`com.mds.db.drift` (daily 05:40) runs `--check --alert` and shouts in Slack when the repo and the
live database disagree. Log: `scripts/db_drift.log`. **A drift alert means someone changed the
database out of band** — re-export, read the diff, and find out who and why before committing it.
Applying files back to the database (repo → DB) is deliberately not wired up.

### 8.3 Quality evaluation

```bash
cd /Users/Born/mds-scorecard-tools
OLIVIA_EVAL_BANK=eval_bank_smoke.json python3 olivia_eval.py --fire --staging --ids 3106,9024,...
OLIVIA_EVAL_BANK=eval_bank_smoke.json python3 olivia_eval.py --score
```
- The banks are **organic questions real members asked** — generated questions were retired.
  Four exist: the **locked 100** (`eval_bank_100_2026-08-16.json`, `scripts/run_eval_100.py` — the
  sprint exit exam, a ruling: "not 30, not 220. 100"; it must also SHRINK, always-passing questions
  retire) · **bank C** (602 organic asks through the Summit week, 2026-08-23/24 — 192 defects found,
  155 fixed, the fix-loop that shaped waves 7–21) · **bank D** (30 Summit-video questions, 10
  classes, 2026-08-28) · **bank B** (#119, the regression net for everything built after 08-16 —
  still being written).
- **The nightly eval** (`com.mds.olivia-eval`, 03:30) fires `eval_bank_v2.json` at the LIVE
  webhook and writes `OLIVIA_EVAL_<date>.md` with per-source health and failure classes. 2026-09-04:
  220 judged · 194 pass · 24 fail (10.9%) against Andy's target of **<1% inaccurate**; worst
  classes `false_denial` and `wrong_fact`. It is the daily routine, never a release gate.
- Eval traffic uses `wamid.SELFTEST*` ids: the workflow answers fully but **skips the Meta send**.
- Runs pace one question at a time and look stalled for minutes. **Never kill a run.**
- **Eval RUNs are propose-and-wait** (they cost money); probes (single questions) are free.
- Model comparisons run OUTSIDE n8n through the bench harness (`kimi_harvest.py` → `kimi_bench.py`
  → `bench_compare.py`; `bench_tools.py` must mirror the live `Attach Embedding` / `Answer Tool` /
  `Answer Merge` nodes — re-extract from the prod snapshot first). #156 (2026-09-02): Sonnet 5 5.4%
  fail / $0.0211 per answer · GPT-5.6 Terra medium 3.3% / $0.0310 · Terra none 7.6% / $0.0237.
- ⚠️ `olivia_selftest.py` paces with a fixed 20-second sleep; an answer slower than that races the
  conversation save and produces phantom multi-turn failures. Fix it to wait on persistence.

### 8.4 Nightly jobs (launchd, on Andy's Mac)

| launchd job | What runs |
|---|---|
| `com.mds.olivia.derivations` (04:30) | `nightly_derivations.py` — **11 steps**, each with its own heartbeat: `derive_niches` · `label_questions` · `sync_chapter_pages` · `cache_member_photos` (#161) · `embed_member_profiles` · `embed_content` (`~/mds-scorecard-tools/embed_backfill.py`) · `embed_catalogs` (#159 — partners + events, nulls only) · `member_events_daily` · `graph_ledger` (expertise ledger v2 + knowledge graph) · `entity_dossiers` · `persona_blurbs` (#161, Haiku blurbs for the Personas sheet) (`refresh_entity_dossiers()`, 900s ceiling since #152) |
| `com.mds.persona.refresh` (04:15) | `persona_refresh.py` — rebuilds member personas |
| `com.mds.olivia-eval` (03:30) | `olivia_eval.py --nightly` — the daily eval (§8.3) |
| `com.mds.olivia.watchdog` (every 15 min) | `alarm_watchdog.py` — watches the alarm system from *outside* Supabase |
| `com.mds.db.drift` (05:40) | `db_export_schema.py --check --alert` — fails and alerts Slack when `db/` and the live SQL layer disagree (#65) |
| `com.mds.zoom.weekly` (Monday 05:15) | `zoom_weekly.py` — Zoom transcripts → chunks → speaker/participant links (`load_speakers.py`, `load_participants.py`) → dossiers; review CSVs go to `~/mds_transcripts/review/` (launchd cannot write `~/Downloads`). `degraded` = "videos NOT synced (no GROUPOS_PAT)" is its normal, stamped state |
| Claude scheduled task `groupos-videos-weekly` (Sunday) | The GroupOS MCP only runs inside a Claude session: video dump → `videos_weekly_check.py --apply` · `partners_weekly_check.py --apply` (+ crawl/extract/load web profiles for new or changed partners, `OLIVIA_PARTNER_WEB_EXTRACT.md`) · the per-member entitlement sweep when a new restricted video appears (`video_access_from_sweep.py`) |

The other three `com.mds.*` jobs on the Mac are not Olivia's (`scorecard.autoimport` = the Facebook
ingest watcher, `scorecard.heartbeat`, `wa.dailydigest`). Two GitHub Actions (§1.1) and the
`chats_mirror` job (every 3h, #90) complete the picture.

**15 jobs stamp `digest.olivia_job_heartbeats`** (#161 added `cache_member_photos` and `persona_blurbs`, 30 h) (`max_age_hours`: 26 nightly · 192 weekly catalogs ·
216 zoom · 3 chats). Stale or `error` = the Slack alarm and a red tile on the 08:00 card. All 13 were
green on 2026-09-04. **Prove any scheduled script under `/usr/bin/python3`** — launchd uses Apple's
Python 3.9, which is not your shell's Python — and never let one write under `~/Downloads`.

### 8.5 Facebook capture (the one irreducibly manual step)

Extension v1.13 runs full autopilot: daily Insights + humanized auto-scroll + comment pass in one
owned tab (roster weekly; `seed_ids.json` auto-written from the DB), and the drop in `~/Downloads`
triggers `auto_import.py` (`load_feed.py → download_images.py → vision_decode.py → upload_images.py →
linker SQL → embed_backfill.py`, plus the nightly classifier). Facebook renders no permalink anchor
for recent posts, so posts are fingerprinted by body text and reach is read from the DOM. The
Insights xlsx leg (the Scorecard's engagement scores) still stalls on Facebook's SPA and then needs
Andy to click "Capture Insights" — the one irreducibly human step. The two legs are separate tiles
on the health card (`fb-capture` vs `fb-engagement`). Manual scroll = deep backfills only.

### 8.6 Incident response

1. Read the actual error first — `n8n_executions` for the failing run, `get_logs` for Supabase.
   Never theorise before reading the error text.
2. A **timeout looks exactly like "no data found"**. Time the query at increasing input sizes
   before blaming ranking, embeddings or the schema cache.
3. Health signals: the alarm (pg_cron, every 5 min, Slack `#automation-tests`), the watchdog
   (launchd, covers the case where Supabase itself is down), and the tools-health dashboard.
4. Rollback is one command (§8.1) and takes seconds. Use it early.

### 8.7 Brokered intros (#97)

One route owns the whole flow: `POST https://digest.mds.co/api/olivia/intro`
(`src/app/api/olivia/intro/route.ts`, mds-digest-web) — secret-gated the same door as `/schedule`
(`X-Olivia-Secret` or `Authorization: Bearer`, `OLIVIA_SCHEDULE_SECRET` → `OLIVIA_IOS_SECRET`).
Policy lives in the route, in git, never in the DB. State machine: `digest.olivia_intros` (`id,
requester_at_id, target_at_id, topic, status, consent_wamid, created_at, decided_at,
decided_reason`), `status` CHECKed to `pending/accepted/declined/expired/unreachable`, one unique
partial index capping the table at one `pending` row per requester→target pair.

Four ops, one body shape (`{op, phone, ...}`):

| op | trigger | does |
|---|---|---|
| `request` | `member_intro` tool (the loop, via Answer Tool — Appendix C) or a typed target-name reply | resolves the target from the asker's last-30d equalizer recommendations (§7.5); no single unambiguous match → returns `pick` (≤10 rows, most-recently-recommended first) instead of sending anything |
| `pick` | WhatsApp interactive-LIST tap, `tap_id = intro_pick_<at_member_id>` | re-enters `request` with that member as the unambiguous target — same function, same JSON contract |
| `tap` | WhatsApp button tap, `tap_text = Accept intro / Decline` | resolves the asker's newest `pending` row where they are the target, PATCHes `status`, messages both sides the verdict |
| `sweep` | n8n cron tick (piggybacks the every-minute `Olivia — Reminder Sender`, `QhJw46Mr7LAP8fdz`, `onError: continueRegularOutput`) | expires `pending` rows older than 7 days: notifies the requester THEN marks `expired` — never the reverse, so a mid-row throw just leaves it `pending` for the next tick to retry (worst case one duplicate notice, never a silently stranded row) |

**Rulings (Andy — enforced in the route, not in prompt text):**
- **Eligibility (#107d, 2026-08-22 — supersedes the 08-21 "both sides Millie users" lock):** the
  target must be a **Summit attendee with a phone on file** (`event_registrations_live`,
  `SUMMIT_EVENT_ID = recrATwhUDA55iQN5` — never name-match the events catalog). The Millie-user
  requirement was dropped on both sides after a confirmed attendee got the pilot refusal. The
  picker pre-filters to eligible candidates only, so a tap never lands on a refusal the pick itself
  should have screened out; picker rows read top-2 expertise topics · speaker · city, and the list
  is never filtered or shortened (#107b).
- **Consent-first:** no phone number and no `wa.me` link reaches either side before
  `status='accepted'`. The request-lane half (no digits / no `wa.me` before accept) is proven
  live on every gate run (checks 13.1–13.3, §8.2). The accept-before-link ordering in `op:'tap'`
  is enforced in code — `route.ts`'s PATCH to `status='accepted'` runs before either of the two
  `waSend()` calls — and is not gate-exercised.
- **Caps:** 3 pending requests per requester · 3 pings per target per rolling 7 days.
- **Decline is final:** a declined requester→target pair is refused forever, no retry — checked
  before any cap or reachability logic.
- **7-day expiry, zero reminders:** a `pending` row outstanding past 7 days is swept (`sweep`
  above); Olivia never nags either side while a request is open.
- **Unreachable, every-member-always:** a target with no phone on file gets a real
  `status='unreachable'` row, never a silent skip, and the asker is told plainly with a
  human-routed alternative offered.

**Tap interception, before the LLM** (in prod since 2026-08-22, `7e4be40a`; E2E proven exec 96653:
Accept tap → row accepted → two texts delivered, zero LLM rows): eight nodes between
`Drop Duplicates` and `Find Member` (Appendix C, **Intro taps** row) — `Intro Tap?` flags an
Accept/Decline button or an `intro_pick_*` list tap; `Intro Route (HTTP)` POSTs `op:'tap'`/`'pick'`
and either replies directly (`handled:true` → `Build Intro Reply` → the silent-or-Meta send) or
`Restore Original Message` puts the pre-tap text back and `Find Member` sees exactly what it would
have seen (`handled:false` — an unrelated or stale tap keeps working through the normal lane).
Wired **first** in the fan-out (v1 branch-order rule, §13). The loop reaches the same route through
the `member_intro` tool in the Answer Tool name-dispatch table (Appendix C, "The loop" row), mapped
to `{op:'request', phone}`; the who-to-meet answer ends with the exact offer "Would you like me to
connect you with one of them?" + Yes/No buttons, and Yes opens the list picker (#107).

**Requester notices are templates (#109, 2026-09-01):** `src/lib/intro-notices.ts` sends
`mds_intro_accepted` / `mds_intro_declined` / `mds_intro_lapsed` first and falls back to free-form
only when the template send returns no wamid; a standing unit test guarantees no requester path can
be a plain text send. Closed-window delivery has not yet been observed live (the probe requester's
window was open).

**Known gaps:** intro-tap turns are not saved to `olivia_messages` (#110 — `Save Conversation`
references `$('Resolve Member')` on that path, swallowed by onError); a by-name intro ask outside
the Summit picker still gets the stale Summit picker (flagged 2026-09-02, no ticket yet).
**Usage so far:** 6 ledger rows; 13 explicit offers → 1 yes; one intro completed end-to-end.

---

### 8.8 A member says "Millie is not answering" — the hidden-number runbook (#146, 2026-08-25)

WhatsApp now lets a member hide their phone number. When they do, Meta delivers their message with **no
number at all** — only an opaque country-prefixed id such as `CA.1068099432261958` (Danson Hui, prod execs
`109524`/`109525`). Millie identifies members by phone, so before this was handled the turn died in
`Find Member` with PGRST202 and the member got **silence**: no answer, no `olivia_messages` row, nothing
in `olivia_webhook_events`. If someone reports she ignored them, this is the first thing to rule out.

**1. Look for a phone-less inbound around when they wrote.**

```
python3 scripts/olivia_link_wa_id.py --find --since 2026-08-25T02:50:00Z
```

It reads `digest.olivia_seen` for rows where `phone is null`, decodes the sender id out of the wamid, and
says whether each is already linked. Nothing there means the cause is something else — check
`resolve_asker`, then the front door, then executions.

**2. Confirm WHO it is with a human.** The id is an identity: pairing the wrong one hands someone another
member's chats. Meta gives us their WhatsApp profile name, which is a hint, never proof.

**3. Link it.**

```
python3 scripts/olivia_link_wa_id.py --uid CA.1068099432261958 --phone 14169033267
```

It refuses unless the phone already resolves to an ACTIVE member — it connects an id to a member who is
already there, it can never create membership — then prints `resolve_asker_by_uid` and the
`olivia_front_door_v2` row count so the link is proven rather than assumed. `--list` shows every pairing,
`--unlink <id>` removes a bad one.

**What happens automatically, and what does not.** Any member whose number IS visible pairs itself: the id
and the number arrive together and `digest.member_wa_ids` learns it (107 learned this way at launch). Only
first contact from a member whose number is hidden needs a human. **Whapi cannot help here** — it reports
plain phone numbers from the group chats, never the Cloud-API id; the two are different namespaces.

**The limit to say out loud: we cannot reply to an unpaired hidden-number sender.** Meta rejects the
opaque id as a recipient — `131009 "The phone number is malformed"`. Millie composes the honest ask-once
line, but it cannot be delivered until the pairing exists, so the pairing has to come from our side (this
runbook) or from the member messaging once with their number visible. Once paired, replies go to the real
number we hold and everything works normally.

## 9. Environment and secrets

**All keys live in `/Users/Born/mds-digest-web/.env.local`** (not in this repo). Scripts read it
directly. Names you will need:

| Variable | Used for |
|---|---|
| `SUPABASE_URL`, `SUPABASE_SECRET_KEY` | Everything database-side (service role) |
| `N8N_API_KEY` | Workflow read/write |
| `VOYAGE_API_KEY` | Embeddings (`voyage-3.5-lite`, 1024 dimensions) — Render holds its own copy for the kb lane (it silently had none until #18) |
| `CENTURION_ANTHROPIC_API_KEY` | Claude for scripts (eval judging, personas, partner-profile extraction) |
| `AIRTABLE_PAT` | Airtable reads (syncs). Olivia's code never writes Airtable |
| `META_WA_TOKEN`, `META_WA_PHONE_NUMBER_ID` | WhatsApp sends from scripts (announcement waves, template create/status); Render holds its own copy for the intro and reminder routes |
| `WHAPI_TOKEN` | The group-reading number (digest pipeline) |
| `ASSEMBLYAI_API_KEY` | In-person/hybrid transcripts (`aai_submit.py`) |
| `OPENAI_API_KEY` | The model bench only (#156). ⚠️ pasted into chat 2026-09-02 — rotate |
| `HEALTH_REPORT_SECRET`, `QA_LOGIN_SECRET` | Health report / QA login. ⚠️ the local `HEALTH_REPORT_SECRET` ≠ Render's (403) — verify deploys via `/api/version` and the 08:00 card |
| *(Render only)* `OLIVIA_SCHEDULE_SECRET` → `OLIVIA_IOS_SECRET` | The route lanes' auth (`X-Olivia-Secret` or `Authorization: Bearer`) |

⚠️ **`ANTHROPIC_API_KEY` is exported empty by some tooling** — that is why script keys are
namespaced (`CENTURION_ANTHROPIC_API_KEY`). Never rely on the bare name. Vercel runs nothing of
Millie's — the web tier is Render.

**Models in use:** `claude-sonnet-5` (answers), `claude-haiku-4-5-20251001` (router + fact gate),
`voyage-3.5-lite` (embeddings). Thinking is **disabled** on the n8n Claude calls — enabled thinking
consumed the whole token budget and members received "Sorry — I could not generate an answer".
Billing is the one failure the model cannot route around: on 2026-09-02 the org's credit read
"too low" for 1h38m while the console showed $99.75 — a fresh $20 purchase unstuck it; the
member-facing copy now names the reason when it IS billing (Answer Parse).

---

## 10. Repository map

```
/Users/Born/Scorecard/                  ← this repo (Olivia + Scorecard + docs)
  OLIVIA_HANDBOOK.md                    ← you are here (the ClickUp doc 2531q-103317 mirrors it)
  OLIVIA_SPRINT_4.md                    ← the open board (opened 2026-08-19); OLIVIA_BACKLOG_ARCHIVE.md = closed tickets
  OLIVIA_NEXT_SESSION.md                ← the handoff: state, queue, Andy's desk
  OLIVIA_KNOWN_ISSUES.md                ← the standing known-issues list: the architecture program, open defects, unfiled findings (ClickUp page 19)
  SESSION_LOG_OLIVIA.md                 ← day-by-day history (append-only); SESSION_LOG.md = the cross-project index
  OLIVIA_SHAREABLE_FIELDS.md            ← the privacy rulebook (see §11)
  OLIVIA_EVAL_<date>.md                 ← the nightly eval report; OLIVIA_MODEL_COMPARE_2026-09-02.md = the #156 bench
  OLIVIA_BANK_*.md / eval_bank_*.json   ← the eval banks (locked 100 · C · D · B in progress)
  OLIVIA_PARTNER_WEB_EXTRACT.md         ← the #160 partner-site extraction spec
  OLIVIA_ARCHITECTURE_AUDIT_*.md        ← the architecture scorecard + its SQL
  OLIVIA_RELEASE_NOTES.md               ← member-facing notes (Andy posts them)
  docs/superpowers/specs/ · plans/      ← designs and approved plans (finder, intros, venue-day …)
  db/                                   ← THE SQL LAYER IN GIT (#65) — generated, never hand-edit
    functions/ (116) views/ (17) triggers.sql policies.sql grants.sql rls.sql tables.sql
  olivia_snapshots/                     ← pre/post-promote prod + staging JSON (183)
  scripts/
    olivia_wf.py                        ← stage / promote / rollback / snapshot / diff / lock / status
    olivia_leak_gate.py                 ← the 323-check safety gate (refusal)
    prod_pulse.py                       ← the liveness check (does she still ANSWER?) — exit 1 = stop
    run_eval_100.py                     ← fires the locked 100 bank (or --bank <file>)
    db_export_schema.py                 ← DB → db/ export + the drift check (#65)
    olivia_selftest.py                  ← fire questions through a workflow (silent turns)
    nightly_derivations.py              ← the 11-step nightly pipeline (#161 added cache_member_photos · persona_blurbs)
    zoom_weekly.py · zoom_transcripts.py · aai_submit.py · aai_transcripts.py   ← transcripts
    load_speakers.py · load_participants.py · load_letter_map.py                ← speaker identity (#103)
    videos_weekly_check.py · partners_weekly_check.py · embed_partners_events.py ← weekly catalogs (#17/#159)
    partner_web_crawl.py · load_partner_web_profiles.py                           ← partner web profiles (#160)
    cache_member_photos.py · persona_blurbs.py                                    ← MDS Personas staff tool feeds (#161): Storage portraits · 2–3 sentence blurbs (Haiku)
    video_access_from_sweep.py · load_video_access.py                             ← restricted-video grants (#101/#150)
    load_event_graph.py · event_lane.py                                           ← the Summit run-of-show (#85/#113)
    olivia_link_wa_id.py                                                          ← hidden-number pairing (#146)
    announce_summit_videos.py · olivia_*_template.py                              ← broadcast waves + Meta templates
    olivia_loop/                        ← the answering-loop source (build_loop.py + apply_* seed edits)
    olivia_loop/apply_169_web_door.py · apply_169_public_gate.py   ← #169: the web door + Public Gate nodes (idempotent, staging first)
    olivia_loop/public_gate.js (+ public_gate.test.mjs)            ← #169: the deterministic redaction module embedded in the gate nodes (node --test)
    model_bench/                        ← snapshot of the bench harness (#156)
    tests/                              ← unit tests that run the REAL node code out of the live graph
    alarm_watchdog.py, sync_chapter_pages.py, olivia_*.py
/Users/Born/mds-scorecard-tools/        ← eval harness + ingestion tools (NOT a git repo)
    olivia_eval.py, eval_bank_*.json, embed_backfill.py, embed_videos.py, persona_refresh.py,
    kimi_harvest.py, kimi_bench.py, bench_compare.py, bench_tools.py, load_feed.py, auto_import.py …
/Users/Born/mds-digest-web/             ← the portal (Next.js, Render) + .env.local + the route lanes
  src/app/api/olivia/{schedule,kb,intro,find,webhook,ticket,…}/route.ts
  src/lib/{finder.ts,finder-fields.ts,schedule-day.ts,intro-notices.ts}
  .github/workflows/                    ← member-profiles-sync · events-catalog-hourly
```

**Separate repos are separate.** `mds-ai-bot` and `mds-digest-web` are their own projects; never
edit one while working the other.

---

## 11. The privacy model

> **Ruling row — Team research mode (#172, Andy 2026-09-10: "answers to all the questions, no gates").** Staff on the
> `MILLIE_TEAM_ASKERS` allowlist read the warehouse through a read-only SQL surface plus a catalog and an ungated
> semantic search, over the deny-list view `member_profiles_team`: exact revenue, contact details and Stripe/billing
> OPEN; removal reasons, LTV, internal notes and lead scoring CLOSED in SQL (`OLIVIA_SHAREABLE_FIELDS.md`, Team column —
> Andy's signature pending on birthdays and five removal-date keys). Every Team turn is logged under the asker's email
> with the queries it ran, behind a per-browser-session acknowledgement of the "never paste it outside the team" notice.
> Nothing in this section changes for members: Millie's member, WhatsApp and Public paths reach none of it (gate-pinned).

> **Visibility ruling (Andy, 2026-08-24) — reads on top of R1–R10:** the asker's own access defines
> shareability. Public info carries no privacy expectation. Restricted-chat content — all field
> types, contacts and self-stated revenue included — is shareable to that chat's members. Rule of
> thumb: *"if someone asking the question can theoretically find an answer themselves, we can share
> it."* Exact revenue from OUR RECORDS stays internal; a member's own visible statement of it is
> quotable. **Every quoted fact names its source** — quoting without attribution is a defect.
> (Seed rule ships with fixwave 7; bank C expects 6047/6050/6137/6258/6382/6420 amended same day.)


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
- **Public mode (#176 — Andy, 2026-09-08): "Public" = OPEN TO EVERY MEMBER. "Restricted" = open to only SOME
  members. The line is per ROW, off the restriction spine the database already carries — never per source type.**
  *"public means all members, but not people outside the MDS; restricted means this content is restricted to some
  members. Facebook is open source; it's public by definition. The only restricted sources are some WA chats (you
  should know it) and some videos (we have the spine with restriction rules)."* Two buckets:
  - **Open** — Facebook group posts and comments · WhatsApp messages and digests whose chat is **not**
    `digest.chats.verification_required` (12 of 18 chats) · call transcripts and videos whose recording is
    `digest.videos_catalog.access_restriction = 'public'` (655 of 1,084) · published partner listings and their
    pages · events and their pages. Named, **quoted and linked freely** — a group link is one we want in the
    answer ("3 fb links that we can share"), and so is a public recording's `app.mds.co/videos/<id>`.
  - **Restricted** — WhatsApp in a `verification_required` chat (MDS Centurion 20M+, Large SKU, Real Estate,
    Supplements, TikTok) · transcripts and videos of a `restricted` recording (mastermind / chapter / coaching
    cohort) · applications. They may still INFORM the answer; no exact detail crosses into it — no names, no
    verbatim quotes, no identifying specifics. Paraphrase only, and say so in the notes.

  A row that cannot be classified stays restricted — **unknown is still closed**: a chat whose
  `verification_required` is NULL (MDS 2026 New Members), a chat name not in `digest.chats`, a transcript with no
  recording. Retrieval runs wide (the probe member's access until Team mode), the output is gated: a name no OPEN
  row of the turn backs becomes a role phrase, restricted sources are paraphrased and named in the notes, and a
  leftover name or a new link after smoothing is repaired (#176 D2) or, on a second pass, refused. Single-word
  member names stay unmasked by design ("leave it"). Team mode (#172) = everything, behind a disclaimer — a later
  ticket.
  **Superseded twice:** #169 built this as "safe to leave MDS" — world-public sources only, the Facebook group
  treated as closed (wrong AUDIENCE). The first #176 pass fixed the audience but kept a source-type allowlist and
  so closed all 18,363 WhatsApp rows and all 13,507 transcript rows wholesale (wrong GRANULARITY). See §13 traps 5
  and 6 and the `public_gate_classify` row in §6.2.
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
- **Attendee-name disclosure (#96 — Andy + Eugene, 2026-08-20):** names go **only to askers
  registered for that event** (the registrations ledger, on every branch); non-attendees get true
  counts and one matching offer, with no mention that names exist. **The cap is 10 names per
  answer — a DISPLAY cap, never a processing cap**: filters and counts run over the whole ledger,
  ordering is fit-based, so the 10 shown are the best 10.
- **Filtering and showing are different rights (#108, §6.3):** 🟢 fields may be printed beside a
  name, 🟡 fields may only ever filter or aggregate, 🔴 fields do neither; a chat is named only to
  its own members (R10); Staff and removed records never appear in names or totals (R8/#106 —
  Andy: "make sure I'm not searchable").
- **Brokered intros are consent-first (#97):** a `wa.me` link IS the phone number. Nothing moves in
  either direction until the target taps Accept; declines are final and never revealed ("no
  connection yet"); silence expires quietly after 7 days with zero reminders.
- **Scores, ranks, percentiles are internal** — never shown, never confirmed to exist.
- **Refusals are quiet:** count-then-stop, one plain-sentence decline if pushed, never internals,
  never "unavailable/withheld/pending".
- **Never delete a member record.** Merge or flag; only genuine test junk is removed.

**How it is enforced — structurally, never by prompt:** the shareable-fields list is the literal
column list of `member_card` (the gate pins it); attendee gating is a registration check inside
`event_who`, the schedule route and the finder; sensitivity, access rules and `video_access`
filter inside every content query; the fact gate blocks unsupported claims; the link gate blocks
unretrieved URLs; the 323-check leak gate proves all of it on every ship.

---

## 12. Decisions and why (the durable ones)

| Decision | Why |
|---|---|
| **Rent the model, never train one** | Training is hundreds of millions of dollars and a research team. Olivia is a Layer-2 product: rented brain + our data + our access rules. |
| **Process at ingest, not at answer time** | Google is fast because it indexed ahead of time. Joining data live is the "five-minute treasure hunt". Organise the *data*, do not try to predict questions. |
| **Airtable = truth, Supabase = serving** | Airtable is curated but rate-limited and cannot do per-item permission filtering at scale. |
| **New lanes are app routes, not RPCs** (2026-08-17) | Retrieval belongs in SQL; POLICY does not. The 20 existing tools are Postgres functions, so "why did she say that" is answered by reading SQL — #65 was that bill arriving. New capabilities put tables + FKs in Supabase and the rule in `mds-digest-web`, in git, reviewed. `Answer Tool` routes `event_*` names to the endpoint via a URL expression; no new nodes. |
| **The schedule wins** (2026-08-17) | Whatever `event_schedule` returns is the answer. Other lanes only when it has nothing, and say so. Never blend, never contradict — and never build a schedule answer from a Facebook post, which is how "Monday, Aug 24" got invented. |
| **Never invent a reason** (2026-08-17) | A recommendation cites only what the tool returned. "Given your Exits & M&A focus" on a TikTok mastermind is a fabrication even when the event is real. A headcount is not a recommendation: "56 members work on International Expansion" is true for everybody who asks. |
| **Security in SQL, not in prompts** | A prompt rule is a suggestion; a fail-closed function is a guarantee. Every retrieval function resolves the asker itself. |
| **Member-initiated conversations** | Removes the template requirement, builds in consent, opens the 24h window naturally, and avoids the "unknown number DMing you" feel. |
| **Hard-fail on ambiguous identity** | A wrong match means reciting another founder's business into a private DM. |
| **The model gets tools, not a single shot** | The original one-pass router — one lane, one retrieval, no second look — was the root cause behind whole classes of failure. The loop can look again. |
| **Fuse by rank (RRF), never blended scores** | Keyword rank and vector distance are incomparable; blending silently disables one of them. |
| **Upcoming events = `Registration Open` ONLY** | Andy 2026-08-17. `Confirmed` is a planning state, not an offer a member can act on. PAST questions may check any status, and a NAMED ask about a Canceled/Postponed event still answers honestly with its true phase (#60). Note `phase IS NULL` is NORMAL, not junk — 292 null-phase events carry 4,019 real member registrations. |
| **Never claim MDS does not track something** | Until the tool that would hold it has been called. Three instances shipped to members (transcripts, call schedule, gender); two were the model obeying a STALE RULE, not hallucinating. Shipping a capability means retiring the rule that denied it. |
| **Organic eval bank only** | Generated questions can be overfitted and do not reflect what members actually ask. |
| **One smoke test per batch, not per ticket** | The full run is slow and paid; per-ticket proof is probes plus the gate. |
| **Coverage is a process, never an event** | Anything hand-run rots. Every derivation is a scheduled job with a heartbeat and an alarm. |
| **Every mirror needs a freshness signal** (2026-08-18) | `digest.chats` rotted for three weeks and she sent a dead invite link; 75 partners sat without a vector for a month (#159). A mirror whose rows share one `updated_at` is a mirror nobody is watching — `max(updated_at)` + row count vs source, and a gate check. |
| **Code beats prompt rules** (2026-08-18) | Two failed rules on one behaviour = move it into the tool. Applied to "show me the rest" (#99, the instruction travels inside the tool result), offer→answer binding (#112), the off-topic gate (#104), the assistant's own name (the fact-check vetoed it until `community_info` returned it). |
| **Read the execution before theorising** | One look at the actual tool call settled what rounds of rule-writing chased — the equalizer bug (exec 90494, plan lane calls with `p_limit` 60), the transcript denials, Prosperlytics missing (a NULL vector, exec 131231). |
| **The 10-name cap is a DISPLAY cap** (Andy 2026-08-20, #96) | "We can totally process this info… just keep the list short." Filters and counts run over the whole ledger; only the shown list is capped. |
| **Intros are consent-first** (Andy 2026-08-20, #97) · **eligibility = attendee + phone** (2026-08-22, #107d) · **suggestions are never filtered or shortened** (#107b) | No number moves without the target's Accept; declines final and never revealed; silence expires without reminders; unreachable gets an honest line + team escalation. The "both sides must be Millie users" rule was dropped after a confirmed attendee got the pilot refusal. |
| **Audits announce themselves** (2026-08-20, #95) | The gate sends `X-Olivia-Audit`; equalizer functions skip their log write. Never infer "this is an audit" from call shape — the `p_limit` heuristic silenced a real lane. |
| **One name: Millie** (Andy 2026-08-21/22) | "Millie and only Millie — official name." Every string, the fact-check rubric and `community_info.assistant_name` say it; the Meta display name follows when the pending review clears (§2.3). |
| **The visibility ruling** (Andy 2026-08-24) | The asker's own access defines shareability: public info carries no privacy expectation; restricted-chat content is shareable to that chat's members; "if someone asking can theoretically find the answer themselves, we can share it"; exact revenue from OUR records stays internal, a member's own visible statement is quotable; **every quoted fact names its source.** |
| **Quote, summarize, TLDR — never a full transcript** (Andy, #101) | The ~1,400-char chunk is the largest retrievable unit and no lane concatenates (the older oversized-cue rows are the known exception, §6.2). Speaker letters stay letters when unmapped (#103) — a wrong name on a quote is worse than no name. |
| **An absent status is not an inactive membership** (#125) | "We do not know your status yet" and "your membership is not active" are different sentences; the first asks for the email on the member's MDS account. |
| **Restricted-video entitlement = attendees + staff** (Andy, #150) and the entitlement is swept from GroupOS, not assumed (2026-09-03) | A restricted video with no grant list is invisible to everyone (fail-closed), so every new restricted video needs the per-member `videos_list(for_user_id)` pass; `is_restricted` means restricted FOR the asker. |
| **A stated fact beats a missing tally; recency is a bounded tiebreak** (#153, #102 slice) | A figure the Town Hall states out loud is answered, not refused for lack of a count; a running event's talk outranks last year's near-tie, never junk. |
| **Every named person carries a link, defined once** (#154) | `digest.member_link()` is the ONE definition (profile FB url → FB-map vanity → `profile.php?id`); both people lanes and the finder return it. |
| **The template category is decided by the copy** (2026-08-28) | Meta reclassified UTILITY → MARKETING three submissions running, flag or no flag. Transactional copy first, personalization after the tap. |
| **Verify the live node's own bytes over real drafts before claiming a gate change works** (#138, 2026-09-02) | A per-item link repair passed 28 unit tests and its own audits, then attached a wrong link on prod within minutes; rolled back in 5, split into #154 (done) and #155. n8n keeps ~1 day of executions, so the audit must run the same day. |
| **Retrieval, gating and stats stay in Postgres; DECISIONS move to routes** (#64 amendment, 2026-09-02) | The 116 functions are the boundary shared by four consumers; what does not belong there is policy — the first slice is #147's registration authority. |
| **One branch per session, never a commit on `main`; two agents share the repo through the `olivia_wf.py` lock and own-ticket doc sections** (Andy 2026-09-02, CLAUDE.md) | A push of `main` can then never publish another session's unfinished work. |
| **Partner web profiles are partner-stated; reviews stay the verdict layer** (#160) | What a site says about itself is framed as such; the founder↔partner link comes from the site's people, never overwritten once set. |
| **Stay on Claude until #157 is decided** (bench 2026-09-02) | Terra-medium wins quality by 2 questions on the Sonnet judge, loses on price (+47%) and latency (2×); nothing ported. |
| **The data-access tier lives in Postgres — and stays there** | See below. |

### The data-access tier lives in Postgres — and that is deliberate (2026-08-07, #65)

Data access and access control belong in Postgres because it is the last hop before the data, and
**four consumers share it**: n8n, the Python scripts, the GitHub Actions and digest-web. Moving the
gate into one application leaves the other three unguarded; moving retrieval out means pulling 38k
rows over the wire and losing HNSW-in-query. So the 104 functions are not misplaced logic — they
are the boundary.

What #65 fixed was not the placement but the **source of truth**: the functions now exist as files
in `db/`, exported from the live database, with a daily drift check. Changes flow **DB → repo**;
repo → DB is deliberately not wired up.

**Two accepted tier exceptions, named rather than pretended away:**
- `olivia_alarm_fire` posts to Slack from inside Postgres (via `pg_net`). On purpose — the alarm
  must survive n8n being the thing that is down.
- `member_event_url` does URL/presentation shaping in SQL. A genuine violation, small, and cheaper
  where it is than duplicated across four consumers.

### Security Advisor — the board, and the two accepted survivors (2026-08-10, #62)

Supabase's Security Advisor was at **18 WARN**. #62 cleared 16 and wrote down the 2 that remain by
design, so the next person reading the dashboard knows they are known, not missed.

**Fixed:**
- **13 × Function Search Path Mutable** — every flagged `digest` helper now pins
  `search_path = 'digest', 'pg_temp'` (the house style, 76 functions already used it). Applied with
  `ALTER FUNCTION`, never `CREATE OR REPLACE`, so `immutable_text_array_join` kept its IMMUTABLE
  volatility and the STORED generated `search_tsv` columns on `partners_catalog`/`videos_catalog`
  that depend on it stayed valid (proven: 497 + 1032 rows, 0 nulls, both embed-invalidate triggers
  fired on a live self-update without wiping an embedding).
- **3 × Public-executable SECURITY DEFINER** — `public.auth_org_ids()` (anon) and
  `public.rls_auto_enable()` (anon + authenticated). Both are the *shared public-schema app's*
  objects, not Olivia's. The grant reaching `anon` was the default **PUBLIC** grant, so revoking the
  roles was a no-op until we `REVOKE … FROM public`.

**Two accepted survivors (written here per the ticket, not fixed):**
- **`public.auth_org_ids()` executable by `authenticated`** — *required.* The RLS policy
  `self_read_org_members` on `public.organization_members` calls it for the authenticated role; a
  revoke there breaks that app's row security. `anon` was removed; `authenticated` + `service_role`
  keep their explicit grants.
- **Leaked Password Protection disabled** — an Auth dashboard toggle, not SQL, and it belongs to the
  password-based public-schema app (Olivia's portal is OTP). **Andy's call to enable**; left as-is
  until then.

**Not a warning, but noted:** 28 `digest` tables show INFO `rls_enabled_no_policy`. For a
service_role-only schema that is the **secure** state — RLS-enabled-no-policy denies anon and
authenticated by default and `service_role` bypasses; the leak gate proves anon is refused. Accepted
as defense-in-depth. (Why RLS is enabled on them at all, and by what, is #61/#64 territory, not #62.)

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
- **A relative day computed by the model is wrong at any venue east of Eastern.** Ian Sells
  (Singapore, Sunday 11:30) got Saturday's list on 2026-08-22 (#114) — resolve relative days in
  code, in the venue zone, never in the model's head.
- **A `+` in a PostgREST URL query is a SPACE.** Send `Z`-suffixed timestamps or every date filter
  silently matches nothing (bit twice).
- **`DROP FUNCTION` discards the ACL** — the fresh CREATE re-grants EXECUTE to PUBLIC (anon could
  call it). `CREATE OR REPLACE` only; a RETURNS TABLE change that needs DROP + CREATE re-grants
  postgres + service_role and revokes public in the same migration. Then **`NOTIFY pgrst, 'reload
  schema'`** — stale pool caches produce intermittent 404s that look like a quality regression.
- **A STABLE function cannot call a writing function** — when the equalizer started logging, the
  STABLE `multi_source*` wrappers broke with a misleading 405; they dropped to VOLATILE.
- **A timeout looks exactly like "no data found"** — time the query at rising input sizes before
  blaming ranking or embeddings; `service_role` carries a 60-second statement timeout, which
  silently cancelled the dossier refresh every night for 13 days (#152 — fixed with a
  function-level `SET statement_timeout`).
- **`pg_net` installs into schema `net`** — unqualified calls inside exception handlers fail silently.
- **No bare apostrophes in n8n expressions** (invalid syntax that fails *silently* — the fact gate
  was dead a full day) and **`node --check` before ANY seed write** (a missing comma between two JS
  strings broke staging for 15 minutes).
- **n8n keeps about one day of executions** — an audit over live drafts must run and land the same
  day (#138's corpus shrank 65 → 31 within hours).
- **n8n Cloud's execution quota takes PROD down** — every inbound dies in 50 ms at the trigger
  ("Execution limit reached", 2026-08-28 04:57–05:10Z). Billing-side fix only; the relay's 502
  makes Meta retry so the questions arrive late instead of never.
- **"Credit balance is too low" with a positive balance** — Anthropic refused every key for 1h38m
  on 2026-09-02 while the console showed $99.75; a fresh $20 purchase unstuck it.
- **A 200 from Meta `/messages` is NOT delivery** — read `digest.olivia_sends`. 131049 = per-user
  marketing cap · 130472 = experiment holdout · 131026 = not on WhatsApp · 131047 = closed window ·
  132018 = newline inside a template variable · 131009 = a hidden-number id used as a recipient ·
  2388362 = a display-name submission while one is pending.
- **A member can hide their WhatsApp number** — Meta then sends only an opaque id and refuses it as
  a recipient; the turn used to die silently in `Find Member` (#146, §8.8).
- **Template quick-reply taps are `msg_type='button'`** — not persisted to `olivia_messages`; only
  `olivia_webhook_events` holds them. List taps (`interactive/list_reply`) flow normally and resolve
  by row `id`, never by parsing the title.
- **`event.people` is data, never an access key** — it carries staff/test rows (one granted attendee
  names on the live route, #98). Access = the registrations ledger.
- **Audit detection by call shape is a bug** — the `p_limit>30` heuristic silenced equalizer logging
  on the plan lane (limit 60). Audits send `X-Olivia-Audit`.
- **Substring matching on short terms** — `'ai' in Em(ai)l`, `'vat' in Pri(vat)e Label`, `'str' in
  industrial`. Topic matching goes through `phraseto_tsquery` on curated terms, never bare `ilike`.
- **Five catalog rows match "Summit Singapore"** (the Summit, Night Out, Speaker's Lunch, Women's
  Lunch, Pre-Event Dinner) — resolve by `app_event_id` or prefer the exact then the shortest name,
  and always echo what was picked. The bare word `summit` keyword-ranks Milan/Denver above the
  running event (#151 — the tool description says so now).
- **The chunker never split an oversized cue** — AssemblyAI returns a whole talk as one utterance
  when it hears one speaker: 1,423 chunks over 4,000 chars, 581 of them in restricted videos
  (2026-08-27). Producer fixed (`split_long_cues()`); re-chunking the old rows is still open.
- **GroupOS traps:** the partners listing breaks on two records (Fathom, Onsite Support — fetch with
  `partners_get`, skip with cursor = base64(id)); a corrupt member record breaks any `members_list`
  page that contains it; `videos_list` accepts a typed `limit` up to 100 now (it once refused it —
  page until `has_more=false`); `cliff_notes` became a LIST on 2026-09-02; GroupOS recreates a
  document on a role change (new `_id`, same natural key); the Summit export handed over on
  2026-08-22 was a 17-Aug scan.
- **Apple's Python 3.9 rejects PostgREST's 2-digit fractional seconds** in `fromisoformat` (phantom
  "changed" rows), and **macOS ARG_MAX** kills a 1 MB curl body passed as an argument — request
  bodies go on stdin (`--data-binary @-`).
- **launchd cannot write `~/Downloads`** (TCC) — `zoom_weekly` died on it every Monday for 26 days.
  Headless jobs write under `~/mds_transcripts` or the repo.
- **A degraded run that never stamps its heartbeat is a red tile forever** — `zoom_weekly` without a
  `GROUPOS_PAT` is permanently degraded and must stamp anyway.
- **PostgREST caps at 1,000 rows** even in a weekly script — `videos_weekly_check` re-upserted and
  re-embedded 79 videos every run until it paged the catalogue read.
- **`digest.mds.co` can SERVFAIL from Andy's Mac** while public DNS resolves it — the gate's route
  checks then fail with status 0; use `mds-digest-web.onrender.com`.
- **`Answer Merge` stamps must read the payload shape the finder actually returns** (`r`, not a
  truncated body) — a stamp that reads the wrong field passes silently and the gate verdict
  neutralises the catch.
- **The repo's node copies go stale** — `answer_merge.js` in the repo was a 77-line copy of a
  ~550-line live node; extract from the prod snapshot before building anything on it.
- **The eval selftest paces on a fixed sleep** — an answer slower than 20 s races the conversation
  save and produces phantom multi-turn failures.
- **A synthetic fixture that passes immediately is the wrong test** — reproduce on the real blob
  (the #138 repair passed its fixtures and attached a wrong link on prod).

---

### Silent mirror decay (2026-08-18)

Two mirrors were found rotting the same day, both discovered only because a member saw a bad answer:

- **`digest.chats`** had not synced since 2026-07-29. She sent a **dead WhatsApp invite** while
  Airtable held the correct one. 29 chats in the source, 19 in the mirror, 3 wrong links (#90).
- **FB post images**: only ~28-31% of posts carry an image on our side, 21% in August. June's
  Member of the Month has none, which is why that answer had no graphic.

**The pattern:** a mirror whose rows all share one `updated_at` is a mirror nobody is watching.
Every mirror needs a freshness signal, not just a loader.

### A tool description that promises what the function does not return (2026-08-18)

`content_search`'s description told the model it returns "an image ref usable as [SEND_IMAGE: ref]".
It did not. So the model had to guess a post id and mostly declined — award graphics and agendas got
described instead of shown. **Three prompt rules failed before anyone checked the actual return
shape.** Both `content_search` and `content_search_v2` now return `meta.has_image`.

Two corollaries, both cost time:
- **The loop calls `content_search_v2`, not `content_search`.** Patching the wrong one looks
  identical to the fix not working. Read the execution's tool call.
- **Read the execution before theorising.** It settled in one call what rule-writing chased for
  rounds — twice in one session.

### The model has no clock (2026-08-18)

Asked to set a reminder "in 5 minutes", the model sent `at=17:23 UTC` when the true time was
21:40 UTC. The endpoint correctly refused a moment in the past, and she narrated the refusal as a
story about the event being a week away. **Never let the model compute an absolute time from a
relative ask** — pass the offset and do the arithmetic server-side.

### Two sessions, one host-level lock (2026-09-07)

`olivia_wf.py lock` records `user@host`. Two Claude sessions on Andy's Mac read as the same holder, so
the lock never separates them — and every apply script is GET → modify → PUT of the WHOLE node list,
so even non-overlapping node sets collide. The #169 session re-staged and PUT twice while the #174
session held the lock; #174's node edits were wiped both times and a probe run spent ten minutes
testing the wrong graph. **Before any staging PUT, message the peer session and wait for an explicit
"staging is yours"; hand it back with "staging is back" and the versionId; re-read the staging
`versionId` right before probing — a change mid-run means the graph under test changed.** Keep apply
scripts idempotent (a marker check) so a re-apply after an overwrite is one command.

### A gate repair that pairs by distance pairs with the wrong row (2026-09-07, #175)

`Gate Verdict`'s link-coverage repair paired each evidence URL with the last `title` in the 900 chars
before it. A top-5 evidence row carries up to 3,200 chars of snippets between its title and its
`video_url`, so the URL fell to the "after" fallback and took the NEXT row's title — a bare link to a
talk nobody named, under every video answer. **Pair fields by structure (the enclosing JSON object),
never by character distance**, and skip a candidate whose title matches a row the draft already links.

### A row is linked by ANY of its URLs, and a name is named inside ONE clause (2026-09-08, #175 lap 2)

Event rows carry two links for the same thing (`reg_link` `/s/events/u/…` and `event_url` `/events/u/…`;
Centurion's `go.mdsonly.co/…` and `/events/u/…`). The `Gate Verdict` #1c field repair checked only the
URL in hand, so a draft that linked every event by its registration link got the same rows' page links
appended bare (exec 137901). The same repair pinned "Register: …MDSSummitSingapore" to an answer about
2027 because its "same words, any order, contiguous" naming test ran across "…of Singapore:\n*MDS Summit
Cancun 2027*" — a colon, a line break and a bold title (exec 137902) — for a Summit that had already
ended. **Before appending a row's link, look at the whole row (`fieldRepairSkip()`: any of its own URLs
already in the draft = covered; `is_over` / `phase: ended` = never a registration line), and test a
name per line / clause (`_nameInAnswer`), never across punctuation.**

### An author-scoped full-text search is ranked by the terms — generic words bury the answer (2026-09-08, #141 lap 2)

`content_search_v2` with `p_author` returns the person's items with the term hits first; terms decide
the order, not the membership. With `[firearms, business, brand]` Fred McKinnon's firearm posts fell out
of the top 40 (every post of his mentions a brand or a business); with `[firearms]` alone the TLO
Outdoors post ranks first. The router is not deterministic either: the same follow-up ran as a topic
search one run (exec 137838) and as a member card the next (exec 137893), and the card lane never saw
his posts at all. **When a pronoun follow-up keeps a person, scope the raw search to them on every lane
that runs a raw fetch and rank with the message's DISTINCTIVE words only (`pronounTopicTerms()` —
stop list plus generic business words removed); a stemmed full-text index needs no singular/plural
variants, and `hunting/firearm/tactical` is one path token to the parser, so a term can miss a row
that visibly contains it.**

### The saved plan omits `offer_bind` — audit a bind in the execution, not the row (2026-09-08, #174)

`digest.olivia_messages.plan` carries the op and its params but **not** `offer_bind`. Andy's live turn 65943
reads `plan->'offer_bind' = null` while execution 138168 shows `{mode:'drilldown', named:[…]}` — an auditor
working from SQL alone would conclude the #174 drill-down never fires. The row's tell is the resulting
params (`p_video_id` set, `p_query` null); the authority is the `Plan Request` node output in the execution.

### JavaScript `\b` is ASCII-only — a name-masking gate fails OPEN on it (2026-09-08, #169)

`public_gate.js` masks member names out of public answers with `new RegExp('\\b' + name + '\\b', 'i')`, in four
places (the backed-name test, the mask, the first-name replace, and the leftover-name verify that is supposed to
fail closed). `\b` is a boundary between an ASCII word char and a non-word char, so a name whose FIRST or LAST
character is not ASCII never matches: **"Émile Dupont" is neither masked nor caught**, while "José Núñez"
(accent in the middle) is fine. Verified on the shipped module 2026-09-08; 23 of 5,847 `member_profiles` rows
have a boundary-evading name, and they are wider than Latin accents — "Øun Thaih", "航 杨", math-alphanumerics
(𝕸𝖊𝖍𝖆𝖗), Khmer and Arabic rows, and one name ending in a variation selector (U+FE0F). **A masking or
redaction regex must be Unicode-aware (`/u` with `\p{L}` lookarounds) and every call site must get the same
treatment — a verify built on the same broken boundary passes exactly what the mask missed.** Fix owned by
#169; the door is header-authenticated and its page had not shipped, so there was no exposure.

### #169 Public Gate — six traps from the ship night (2026-09-08; traps 5 and 6 added by #176)

1. **JS `\b` is ASCII-only.** `new RegExp('\\b' + name + '\\b', 'i')` never matches a name whose first or last
   character is non-ASCII ("Émile Dupont", "航 杨明", "𝕸𝖊𝖍𝖆𝖗 𝕾𝖎𝖓𝖌𝖍", a trailing U+FE0F) — 23 live index rows passed
   both the mask and the verify, fail-OPEN, until the whole-branch review caught it. Rule: every name match goes
   through one shared `boundedRe()` (`(?<![\p{L}\p{N}_])…(?![\p{L}\p{N}_])`, flag `u`) after normalising BOTH the
   index name and the text (NFC, strip U+FE0F / U+200B–U+200D / U+2060 / U+FEFF, collapse whitespace). Also: `\p{Lu}`
   case-folds under the `iu` flag pair — a "capitalised token" pattern must be compiled without `i`.
2. **A script without argparse treats `--help` as "run".** `apply_169_public_gate.py --help` rewrote staging (under
   the lock, staging only). Every apply script takes `--dry-run DIR` (GET + patched graph to disk, no write) and
   `--apply` (the live PUT + bounce); read a script's docstring before running it at all.
3. **SQL functions do not ride the promote.** `public_gate_name_index()` was redefined live to drop organisation rows;
   that changed prod at once, with no snapshot. Graph changes have `olivia_wf.py` snapshots; SQL changes have
   `db/functions/` as the only rollback source — say which kind a fix is in the ticket.
4. **Gate check 4 judges the ship target.** It compares the embedded module on STAGING (what is about to ship) with
   the file and reports a stale PROD only informationally, so a pre-promote run stays green; the price is that prod
   drift no longer reddens the gate on its own — run the gate once more right after every promote.
5. **The world-public reading of "Public mode" was WRONG (#176, 2026-09-08).** #169 built Public mode as "safe to
   leave MDS" — a person could be named only when a source the open INTERNET can already see backed the name — so
   the MDS Facebook group, the app's library and everything else internal classified `closed`. Wrong audience: a
   public answer is posted **into the members-only MDS Facebook group**, so its readers are MDS members, and the
   only thing to hide is exact detail from a **restricted room** — which trap 6 then had to sharpen from a source
   type into a per-row test. Andy:
   *"the whole idea behind public is that we hiding exact details from restictat chats"*. Two tells the old reading
   never cohered: partner listings classified `public` while their url is `app.mds.co/partners/<id>` (a members'-app
   link — world-public and app-only at once), and `content_items.access_rule->>'type' = 'public'` was dismissed as
   "member-visible, not world-visible" when member-visible is exactly the right test. **Rule: name the AUDIENCE of a
   gated output before you write the gate.** A gate calibrated for the wrong reader over-masks silently — it looks
   fail-closed and green while publishing answers visibly worse than the ungated ones the same people already get.
6. **A SOURCE-TYPE allowlist is not an access rule (#176 correction 2, 2026-09-08).** Trap 5's fix opened the
   Facebook group, but kept #169's shape: an allowlist of open SOURCES, everything else closed. So it closed all
   18,363 WhatsApp rows and all 13,507 call-transcript rows wholesale — twelve open chats (the great majority of
   the WhatsApp corpus) and 8,022 chunks of recordings any member can open in the app. Andy: *"the only restricted
   sources are some WA chats … and some videos (we have the spine with restriction rules)."* The spine was already
   in the database and nobody read it: `digest.chats.verification_required` (5 true, 12 false, 1 NULL) and
   `digest.videos_catalog.access_restriction` (655 public, 429 restricted), with a call transcript inheriting the
   recording it was cut from. **Rule: before writing a gate, look for the access column the product already
   has.** A source TYPE is a guess at access; a restriction column IS access. Two corollaries proven here: join a
   transcript to its recording by the row's own URL (3,204 of 13,507 `source_id`s are a base64 call id, not
   `<24 hex>#<chunk>`), and when two restriction signals disagree — 401 rows where `sensitivity` and
   `access_restriction` differ — take the more restrictive one.



### #172 — six traps from the read-only SQL surface (2026-09-10)

6. **A view runs as its OWNER for the tables it reads, but a function it calls runs as the CALLER.** `member_identity`
   and `member_phones` are granted to the role, yet both died with `42501 permission denied for function
   is_active_member_status` until that pure helper got EXECUTE. Any grant like it is a widening of the surface: the gate
   pins the role's private EXECUTE set literally (`digest.is_active_member_status(p_status text)`) so the next one is a
   deliberate edit, not a quiet drift. A helper that reads a dark table (`member_link` → `member_profiles`) cannot be
   fixed this way — the view stays dark (#197).

1. **PostgREST maps SQLSTATEs to HTTP statuses:** `42501` → 403, `25006` → 405, `42P01` / `42883` → 404,
   everything else in `42*` / `0A*` / `3F*` → 400. A check that expects "400 for every refusal" passes on
   nothing. Assert the status AND the `code` in the body.
2. **`ALTER … OWNER TO role` requires the receiving role to hold CREATE on the schema** at that moment
   (PG 16+). Grant CREATE, hand over, revoke, and pin "no CREATE" in the gate — a read-only role must
   never keep it.
3. **A data-modifying CTE nested inside a subquery dies at `0A000`** ("must be at the top level") before
   any privilege or read-only check — so it proves nothing about `transaction_read_only`. The proof that
   binds is a PUBLIC-executable writer reached on privilege alone: pg_net's `net.http_post` enqueue is
   an INSERT, and the read-only check runs before the permission check → `25006`.
4. **Every PUBLIC-executable SECURITY DEFINER writer in `digest` is a trigger function** — not callable
   directly, so "call a writer through the tool" needs a real callable (see 3).
5. **Chrome DOWNLOADS `application/x-ndjson` instead of rendering it.** A streaming route cannot be
   measured by opening it in a tab; run a `fetch` reader inside a same-origin page (the admin page) and
   read its progress — that is the client's real path anyway.

## 14. Known limits (2026-09-04)

- **Transcripts cover 2025 and 2026, not before** (#70/#101, the 2025 batch 2026-08-21, the 16
  Summit Singapore talks 2026-08-27, the last 33 in-person talks 2026-09-04 — #162, 212/212 of 2026,
  444 of 1,086 library videos): Zoom where Zoom hosted, AssemblyAI for in-person/hybrid rooms
  where speakers stay `Speaker A/B/C` unless the #103 letter-mapping has evidence. Nothing before
  2025-01-01 (Andy: "not sure about <2024"). When a gap is reported the boundary travels with it —
  never "not live" or "coming". Old oversized chunks (§6.2) are still to be re-chunked; 7
  metadata-only Summit videos await Andy's re-embed ruling.
- **No forward calls calendar** — `digest.calls` holds past occurrences only. Say it as coverage,
  never as infrastructure.
- **Events have no description field anywhere in the pipeline** — topic matching is inferred from
  names, attendees and chatter (the `event` schema's Summit activities do carry descriptions).
- **The proactive weekly push (Side A) is not built** — and the channel fights it: Meta classifies
  personalized copy as MARKETING and drops half of a wave on per-user caps (§2.2). A transactional
  v4 template is the open recommendation.
- **The Meta display name still reads "MDS AI Assistant"** — "MDS Mille" pending since 2026-08-19
  blocks the "MDS Millie" submission (§2.3).
- **Registration has two disagreeing sources (#147, paused)** — 36 members answered differently by
  the agenda and by who-to-meet; half the fix is live, the authority shape is Andy's call.
- **A hidden-number member needs a human pairing on first contact (#146)** — and cannot be answered
  until paired (Meta refuses the opaque id as a recipient). 8 active members have no GroupOS
  account at all and get no video grants; 5 sweep emails resolve to nobody.
- **The quality bar is not met yet** — Andy's target is <1% inaccurate; the nightly eval reads
  10.9% on 2026-09-04 (24 of 220), led by `false_denial` and `wrong_fact`; bank C's fix-loop
  brought its own set from 62% to 91% correct.
- **#72 load test has never run** — the Summit day (120 questions) and the announcement wave were
  survived, not tested. Still the biggest open risk.
- **#32 cost instrumentation is absent in prod** — the bench measured $0.0211 per warm answer, but
  nothing logs tokens per answer; `latency_ms` is unreliable.
- **Facebook capture is manual at its root** (platform limitation; extension v1.13 autopilots the
  routine, the Insights export still stalls on Facebook's SPA and needs a click).
- **Portal login OTP shares Millie's number** — a block would break logins too.
- **The nightly and weekly jobs run on a Mac via launchd and a scheduled Claude task** — staleness
  alarms are the backstop; the GroupOS refresh cannot run headless until a `GROUPOS_PAT` exists.
- **The WA members mirror never reconciles (#148)** — 12 rows Airtable stopped returning are frozen;
  no freshness signal yet.
- **Intro-tap turns are not in conversation history (#110)**; a by-name intro ask outside the
  Summit gets the stale Summit picker.

*Superseded limits, kept so nobody re-learns them:* ~~recommendations are not personalized~~
(#29/#93–95) · ~~tap buttons are not built~~ (#38) · ~~no transcripts~~ (#70/#101 — the stale-rule
incident class) · ~~intros are POC-stage~~ (#97 live 2026-08-22) · ~~the count ruling~~ (folded
into #147) · ~~75 partners dark in meaning search~~ (#159).

---

## 15. Glossary

| Term | Meaning |
|---|---|
| **Millie** | Olivia's member-facing name (Andy 2026-08-21). "Olivia" stays the project, workflow and table name. |
| **The gate** | `olivia_leak_gate.py`, 313 automated safety checks on 2026-09-04 (count grows with every ship — say "gate green", the number moves). Checks, never questions. |
| **The pulse** | `prod_pulse.py` — read-only liveness twin of the gate (does she still answer?). |
| **Probe** | One question fired through a workflow (`olivia_selftest.py`, silent). Free, no approval needed. |
| **Run** | Firing an eval bank (dozens to hundreds of questions). Costs money; propose-and-wait. |
| **The smoke** | A scored multi-question run: the locked 100 bank at sprint completion (the exit exam), bank C/D, or a targeted set with per-question pass bars. |
| **The nightly eval** | `olivia_eval.py --nightly` → `OLIVIA_EVAL_<date>.md`. The daily routine, never a release gate. |
| **Lane / route** | Which retrieval path a question takes (events, partners, community, llm…). |
| **Route lane** | A capability living in `mds-digest-web` (policy in git) — schedule, kb, intro, find. |
| **The front door** | `Find Member` → `olivia_front_door_v2`: phone or hidden-number id → exactly one active member, or the generic path. |
| **The relay** | `digest.mds.co/api/olivia/webhook` — Meta's callback target; passthrough to n8n, 502-and-retry when n8n is dead. |
| **The loop** | The tool-calling answering loop (Answer Seed → … → Gate Verdict), ≤5 rounds, 29 tools. |
| **Fact gate** | The Haiku check comparing a draft answer against retrieved evidence; plus the deterministic link gate. |
| **The equalizer** | `olivia_recommendations` + the ranking rules that rotate recommendations (30d / 7d / LRU). |
| **ADVICE vs MEET lanes** | "Who can help me with X" (proficiency first) vs "who should I meet" (novelty first). |
| **The finder** | `POST /api/olivia/find` — boolean-tree member filters with the disclosure engine R1–R10. |
| **Canary** | A temporary clearly-marked row inserted to prove a flow, deleted the same session (the gate's REDTEAM rows). |
| **Promote** | Copying the staging workflow to production via `olivia_wf.py`. Andy runs it. |
| **Silent turn** | A `wamid.SELFTEST*` turn: fully answered and saved, never sent through Meta. |

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
| `member_match` | `p_phone, p_dims text[], p_limit, p_city, p_state, p_channel, p_category` | `TABLE(full_name, city, state, reasons text[])` | Attribute matching. Returns **coarse reasons only** — never raw values. City comparisons go through `place_city()`. v2 adds the complementary-topic boost + the #95 equalizer (30d hard downrank · 7d spread · LRU cycling · X-Olivia-Audit opt-out · logs to `olivia_recommendations`). |
| `expertise_search` | `p_phone, p_query, p_limit, p_embedding` | `TABLE(full_name, city, state, expertise, niche, matched_text, matched_rank)` | Keyword + embedding fused by **RRF**. `matched_text` is the public profile snippet that matched. **Equalizer (#95):** RRF ×0.6 on a 30d per-asker repeat; 7d exposure damps the engagement tiebreak; LRU cycling among repeats; logs every shown name to `olivia_recommendations` unless the caller sends `X-Olivia-Audit`. |
| `member_count` | `p_phone, p_niche, p_city, p_state, p_chapter, p_band, p_main_only, p_group_by, p_at_member_id` | `TABLE(total bigint, breakdown jsonb, breakdown_sum bigint, population bigint, note)` | Counting only — never names. `breakdown_sum` exists because members hold several chapters/niches, so the parts legitimately exceed the whole. |
| `member_dossier` | `p_phone` | `TABLE(kind, label, detail)` | **Self only.** Profile + active chats + recent own messages + event registrations. Reads personas; does **not** yet read the expertise ledger, graph or event log. |
| `member_billing` | `p_phone` | `TABLE(membership_status, plan_name, plan_price, subscription_status, billing_interval, monthly_amount, annual_payment, member_since, year_joined, next_renewal, chapter, next_invoice_date, next_invoice_amount, payment_frequency, membership_fee, billing_portal)` | **Self only.** The only status-emitting function; every state maps to plain member-facing words inside it, so raw system codes are structurally unemittable. |
| `billing_nudge` | `p_phone` | `TABLE(nudge)` | **VOLATILE** — stamps `olivia_billing_nudges` so a past-due reminder rides at most once per 24h. Sent text only; saved history stays clean. |
| `event_lookup` | `p_phone, p_terms text[], p_city, p_virtual bool, p_include_past bool, p_limit, p_embedding, p_at_member_id` | `TABLE(event_name, starts_at, start_display, event_type, phase, city, guests_policy, chapter, audience_hint, is_registered, can_register, reg_link, guest_reg_link, spots_left, registered_count, event_url)` | Chapter-gated (record-link overlap; untagged chapter events **fail closed**). **Phase rule (#60):** browse offers Registration Open/Confirmed only; a NAMED ask may return Canceled/Postponed with the true phase shown (honesty over silence); Tentative/Awaiting Feedback invisible everywhere. Rank-based vector eligibility partitioned future/past. |
| `event_who` | `p_phone, p_event, p_limit` | `TABLE(event_name, starts_at, full_name, state, is_me, total_going, city, niche, channels, fit_reason, shared_topics)` | **Confirmed attendees only** (`Ticket Status='Confirmed'` and `Ticket for` ∈ member classes). **#96 ruling (Andy+Eugene 2026-08-20):** names go to askers **registered for that event** only, **capped at 10** (display cap — ordering is fit-based, so the 10 are the best 10; filters/counts always run over the whole ledger). A non-attendee gets the aggregate row: true `total_going`, no names. Chapter slices (route `people` op): attendees get ≤10 names + the count; non-attendees the count only. Supersedes the 2026-07-20 any-member width. |
| `event_history` | `p_phone` | `TABLE(kind, label, detail)` | **Self only.** Past + upcoming registrations, plus the asker's own city (used by other lanes). |
| `chapter_info` | `p_phone, p_at_member_id, p_chapter` | `TABLE(chapter, member_count, asker_is_member, leads jsonb, about, categories[], live_stats jsonb, page_url, geo, region, asker_city, asker_state, note)` | Counts computed by the **same CTEs as `member_count`** — one number everywhere by construction. `live_stats` are chapter **aggregates** only. Leads are public (names, roles, photos); their contact details do not exist in the data. |
| `community_info` | `p_phone` | `TABLE(active_members, whatsapp_chats, upcoming_events, chapters, chapter_breakdown jsonb, gender_split jsonb)` | Community-level numbers. Gender is approximate and must be presented with the not-everyone-reports caveat. |
| `partner_lookup` | `p_phone, p_query, p_limit, p_embedding, p_at_member_id` | `TABLE(name, offer_value, description_snippet, categories[], rating_avg, review_count, claim_count, featured, fresh_deal, partner_url, reviews_sample jsonb, matched_rank)` | Reviews are real member reviews — quotable, never attributed to a name. |
| `partner_lookup_v2` | same + `p_order` | v1 columns + `fit_reason, strength_note, event_offer*` + **#160** `web_summary, web_people jsonb, web_pricing` (LEFT JOIN `partner_web_profile` where `crawl_status='ok'`) | The tool the loop calls. Web fields are what the partner's site says — the seed description tells the model to frame them so. A partner with no vector is invisible to the meaning lane (#159): `embed_catalogs` nightly + weekly re-embed keep it at 0. |
| `personas_library()` | — | one row per ACTIVE member: `id, name, status, city, joined, level, top jsonb, photo_url, msgs30, at_peak_count` | **#161 staff tool — no member gating** (staff sees everyone); reads `personas_stats` (view over `member_expertise` × `expertise_topics`: `value` = pct×100 (a rank percentile — median ~50, max 100 in every topic by construction), `peak` (a PROJECTION: `least(100, round(value × peak_score ÷ score))`, not a percentile the member ever held — the sheet no longer displays it), `badge` peak/holding/fading from real scores, `rank`; **#165 (2026-09-07) appended `score_today` = raw `score`, `score_peak` = raw `peak_score`, `pool` = members with a row in the topic, `topic_top` = max score in the topic, `topic_median` = median score in the topic (all 2dp; per-topic aggregates from one GROUP BY join — `percentile_cont` cannot be a window function). The sheet's bar is absolute on these: 0 → `topic_top`, fill `score_today`, tick `score_peak`, line `topic_median`; the percentile prints beneath as `51st · 19 of 38`.**) + `member_photos` |
| `personas_sheet(p_id)` | `at_member_id` | one jsonb: `member` (library row + niche/channels/since/title/summary/**blurb**/focus/gives_text/asks_text) · `stats[]` (all 51) · `asks[]` · `gives[]` (topics from persona evidence) | #161; `member` null = unknown id |
| `personas_cohort(p_stat)` | topic name | members with `value ≥ 60` on that stat, desc | #161 — superseded by v2 below, kept because a DROP would lose the ACL; nothing reads it |
| `personas_cohort_v2(p_stat)` | topic name | the same rows plus `rank` and `pool`, **ordered by rank** (`at_member_id` breaks a shared rank) | **#178** — v1 ordered on the ROUNDED percentile, which ties (four members at 100 in Logistics & 3PL), so the alphabet decided and the real #1 rendered third |
| `personas_ranks()` | — | per member `{topic: [rank, pool]}` | **#178** — what the rails and Top 10 sort on; same population and same ≥ 60 floor as `personas_strong()`, so the two maps carry the same keys |
| `personas_related(p_id)` | `at_member_id` | `similar[]` (cosine over the 18 category values, top 5, `pct`, `shared`) · `companions[]` (≥ 75 on the member's ask topics, top 5, `cover`, `shared`) | #161; never lists the member themselves; category-level asks only (detail-stat asks pending) |
| `personas_strong()` · `personas_fading()` · `personas_topic_peaks()` | — | per member `strong jsonb` (categories ≥ 60) · per member `fading_count` · per topic `strong_count, peak_count` | #161 rails, Browse-menu counts and hero copy — new functions instead of changing `personas_library`'s return type (a DROP would lose the ACL) |
| `video_search` | `p_phone, p_query, p_limit, p_embedding, p_at_member_id` | `TABLE(title, call_type, speakers[], description_snippet, cliff_notes_snippet, attachments jsonb, duration, categories[], tags[], published_at, video_url, matched_rank, is_restricted)` | **Restricted videos return metadata only** — title and date, never description, cliff notes or attachments. They are listed, never denied. |
| `video_file_for_send` | `p_phone, p_file_key` | `TABLE(file_name, storage_object, file_kind, video_title)` | Re-validates the key server-side (public video, allowed kind, our bucket) — a hallucinated key for a restricted deck cannot send. |
| `multi_source` | `p_phone, p_query, p_terms text[], p_city, p_want text[]` | `jsonb` (one key per family) | One-shot fan-out across partners / members / events / chats / Facebook / videos. A new source = one branch here + one prompt block. |
| `chat_info` | `p_phone, p_chat` | `TABLE(chat_name, is_member, verification_required, requirement, call_schedule, zoom_link, moderators, join_link)` | Gated chats return the **verification form**, never a raw invite, to non-members. Zoom links only for chats the asker is in. |
| `chat_recommendations` | `p_phone` | `TABLE(chat_name, verification_required, requirement, qualifies, join_link)` | Excludes chats they are in and gated chats they do not qualify for — absence stays ambiguous (a "you do not qualify" line would leak). |
| `report_create` | `p_phone, p_text, p_context` | `TABLE(ok, report_id, note)` | **VOLATILE.** Files a member report verbatim. Idempotent within a short window (double-file protection). |
| `app_member_feed` | `p_email, p_recent_queries text[], p_interest_embedding, p_limit_each` | `jsonb` | **The app's door.** Identity by email; the app must send the LINKED member email. Fail-closed: unknown or inactive email returns `{}`. |
| `persona_signals` | `p_at_member_id` | `jsonb` | Signal bundle used by the nightly persona builder. Not member-facing. |

**The v2/v3 executions the loop actually runs** (`EXEC_NAME`, §3 step 9 — signatures read live 2026-09-04):

| Function | Arguments | Returns | Gating & notes |
|---|---|---|---|
| `member_card_v2` | `p_phone, p_member` | v1 columns | The card the loop calls; same allowlist, pinned by the gate. |
| `member_match_v2` | `p_phone, p_dims text[] = {state,category,band}, p_limit 10, p_city, p_state, p_channel, p_category, p_country` | `TABLE(full_name, city, state, reasons text[], matched_total bigint, link)` | **VOLATILE** (equalizer log). Complementary-topic boost; `matched_total` = the census behind the sample; `link` (#154). |
| `expertise_search` | `p_phone, p_query, p_limit 12, p_embedding` | `TABLE(full_name, city, state, expertise, niche, matched_text, matched_rank real, link)` | **VOLATILE.** RRF keyword+embedding; equalizer ×0.6 on a 30d repeat; `link` (#154). |
| `member_dossier_v2` / `event_history_v2` | `p_phone` | `TABLE(kind, label, detail)` | Self only; v2 adds strengths / working-on / behaviour / circle and `interest` rows. |
| `event_lookup_v3` | v1 arguments (`p_limit 12`) | v1 columns + `fit_reason, strength_note, what_it_is, room jsonb` | Personalized browse order; the room/venue facts for a named event. |
| `chat_recommendations_v3` | `p_phone` | v1 columns + `why, strength_note` | Order = topic fit → circle presence; the `why` is rendered in the canned list. |
| `video_search_v2` | `p_phone, p_query, p_limit 8, p_embedding, p_at_member_id, p_call_type, p_order, p_video_id` | v1 columns + `is_restricted` (**for this asker**, #150) `, fit_reason, strength_note, summary, event_total` (#151) | Entitled → full treatment; not entitled → title/speakers/date/link + the restricted marker. Bounded recency in fusion (#153). |
| `partner_lookup_v2` | v1 + `p_order` | v1 columns + `fit_reason, strength_note, event_offer, event_offer_event, event_offer_contact, web_summary, web_people jsonb, web_pricing` | #160 web fields = what the partner's own site says (LEFT JOIN `partner_web_profile`, `crawl_status='ok'`). |
| `multi_source_v2` | `p_phone, p_query, p_terms text[], p_city, p_want text[] = {partners,members,events,chats,fb,videos}` | `jsonb` | **VOLATILE.** v1 + the asker's `me` section. |
| `form_field_history` / `my_form_answers` | `p_phone, p_field` / `p_phone, p_form_id` | `TABLE(canonical_key, answer, form_name, submitted_at)` / `TABLE(form_name, submitted_at, ref, question, answer)` | **Self only** — the asker's own form answers across time / per form. |
| `form_stats` | `p_phone, p_question, p_form_id, p_group_by, p_since, p_until` | `TABLE(label, value numeric, detail)` | Census/form aggregates: % distributions, no member counts, no-answers excluded, small cells suppressed. |

**Identity and plumbing functions** (not tools): `olivia_front_door_v2(p_phone, p_user_id)` — the
front door: phone OR opaque WhatsApp id → `{phone, full_name, membership_status, at_member_id,
airtable_id, channels_present, olivia_welcomed_at, olivia_optout_at}` · `resolve_asker` /
`resolve_asker_by_uid(p_user_id)` · `resolve_member_by_email(p_email)` (the single email entry
point, §4.10) · `member_alias_ids` / `registration_status` / `is_registered` (#147) ·
`member_link(p_at_member_id)` (#154) · `member_topic_profile(p_atid)` (internal, no REST grant) ·
`refresh_member_phone_index()` (pg_cron, every 15 min) · `refresh_entity_dossiers()` (nightly,
900s ceiling) · `geo_country_set` / `geo_state_set` / `country_fold` (the geo SSOT).

**The route lanes** (policy in git — `digest.mds.co`, auth `X-Olivia-Secret` / `Authorization: Bearer`):

| Lane | Ops | Notes |
|---|---|---|
| `/api/olivia/schedule` | schedule · next · where · speakers · sessions · recommend · people (who-to-meet + `chapter` census) · reminders set/list/cancel | The Summit lane (§4.9). `at=today\|tomorrow\|<weekday>\|date` resolved in the VENUE's zone, `now_at_venue` on every answer, `next` = the rest of the venue-day (#114); `eventPhase()` computed in the venue zone (#149). `people`: asker must be in the registrations ledger; ≤8 matches + `matched_total`; only shown names are logged to the equalizer. |
| `/api/olivia/kb` | `org_docs` search | Hybrid RRF (cosine + tsv), similarity floor 0.45, honest-empty, `degraded` flag when a lane is dark. Audience fail-closed to staff. |
| `/api/olivia/intro` | request · pick · tap · sweep | **LIVE since 2026-08-22** (§8.7): consent-first, eligibility = attendee + phone, caps 3/3, decline final, 7-day sweep from the hourly reminder sender, requester notices as templates (#109). |
| `/api/olivia/find` | `return: people \| count \| breakdown` over a boolean filter tree | **The finder (#108), phase 1** (§6.3): registry of 🟢/🟡/🔴 fields, ten disclosure rules, reasons per person, `link`, writes nothing. Phases 2/3 (#116) add content/videos/events/partners. |
| `/api/olivia/webhook` | GET verify · POST relay | Meta's callback target (§1.1). |
| `/api/olivia/ticket` | create | Escalation → Intercom ticket on the real member (Intercom 403-blocks n8n's IP). |

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
-- THE SEARCH INDEX (57,586 rows, 2026-09-04)
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

-- THE MEMBER POPULATION (5,757 rows; 756 active) — canonical key at_member_id
member_attributes(
  at_member_id text PK, full_name, membership_status, city, state, country,
  rev_band,                    -- 1-5M | 5-10M | 10-20M | 20M+  (the ONLY revenue representation)
  under_30 bool, age_band, categories text[], sells_supplements bool,
  business_model text[], channel_mix text[], sku_count int, large_sku bool,
  brands_count int, started_year int, title, expertise, main_niche, fun_fact,
  tiktok_seller bool, provenance jsonb, chapter_affiliation text[], chapter_ids text[],
  refreshed_at timestamptz)

-- THE WHATSAPP CHANNEL LAYER (680 rows, 617 linked) — NOT the population
members(
  airtable_id text PK,        -- what olivia_messages.member points at
  at_member_id text,          -- the canonical key; NULL for 63 unidentified numbers (never auto-stamped)
  phone, email, full_name, name, membership_status,
  channels_present text[],    -- which WhatsApp chats they are in = the chat_member entitlement
  olivia_welcomed_at, olivia_optout_at, olivia_interactions, olivia_last_used_at,
  portal_last_seen_at, msgs_7d, msgs_30d, otp_* , delivery_* …)

-- CONVERSATION (12,981 rows; 1,385 real member turns)
olivia_messages(id, phone, member,      -- member = members.airtable_id (FK)
  role text,                            -- 'member' | 'olivia'
  text, wamid, route, focus_chat, latency_ms, created_at,
  plan jsonb)                           -- the retrieval plan; replayed when the member says "yes"

-- BEHAVIOUR LOG (36,076 rows) — APPEND ONLY, no UPDATE/DELETE grant exists
member_events(id, at_member_id, member, event_type, source,
  cadence text,                          -- live | daily | weekly | backfill
  occurred_at timestamptz, captured_at timestamptz, meta jsonb)

-- EXPERTISE LEDGER v2 (16,630 rows)  ·  KNOWLEDGE GRAPH (145,449 rows)
member_expertise(at_member_id, topic, score, rank_in_topic, pct, weakness_score, evidence jsonb, refreshed_at)
member_edges(a_id, b_id, edge_type, weight, evidence jsonb, refreshed_at)  -- CHECK (a_id < b_id)
expertise_topics(topic PK, terms text[])   -- topics are DATA; a new topic is an INSERT

-- REGISTRATION LEDGER (18,295 rows; 14,380 live) — WRITERS ONLY (sync + stamp_event_registrations)
event_registrations(roster_record_id PK, event_at_id, member_at_id, email, full_name,
  order_date, ticket_type, ticket_status,  -- Confirmed | Unconfirmed | No Show | Partially Refunded
  ticket_for text[],                       -- MDS Member | Significant Other | Partner | …
  source, app_event_id, app_user_id, synced_at)

-- HIDDEN-NUMBER PAIRING (108 rows) — #146
member_wa_ids(user_id /* the opaque WhatsApp sender id, e.g. CA.1068… */, phone, at_member_id, source, created_at)

-- DELIVERY TRUTH (2,233 rows) — what Meta reported back, asynchronously
olivia_sends(id, phone, wamid, kind, status /* accepted|sent|delivered|read|failed|maintenance */, error_code, conversation_origin, created_at, updated_at)

-- PARTNER WEB PROFILES (506 rows; 405 crawl_status='ok') — #160, partner-stated
partner_web_profile(partner_id PK, summary, services text[], markets text[], pricing, people jsonb, profile jsonb, crawl_status, profile_hash, crawled_at)

-- #58 CHOKEPOINT — every reader goes through this view, never the table above.
-- A cancelled ticket is not an upcoming event, and a No Show is not attendance.
event_registrations_live = event_registrations
  WHERE ticket_status IS DISTINCT FROM 'Unconfirmed' AND IS DISTINCT FROM 'No Show'
```

### B.2 Indexes that matter

| Index | Table | Purpose |
|---|---|---|
| `content_items_embedding_hnsw` | `content_items` | 376 MB HNSW (cosine), 26,305 scans by 2026-09-04. **Only reachable when the ANN operator is the leading sort of its own query** — see §6.1. |
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
| `events_catalog`, `partners_catalog` | `*_embed_invalidate` | Clears the embedding when the text changes. Rebuilt by the nightly `embed_catalogs` step (`scripts/embed_partners_events.py`, nulls-only) and by `partners_weekly_check.py --apply` in the same pass (#159 — before 2026-09-03 nothing rebuilt it: 75 partners dark). |
| `member_profiles`, `members` | `member_profiles_stamp_synced`, `members_stamp_synced` | Freshness stamps on the two Airtable mirrors (`synced_at`) — the signal #148 will read. |
| `member_sessions` | `member_sessions_rollup` | Session counters. |

18 (table, trigger) pairs live on 2026-09-04 — the list above is complete.

### B.4 pg_cron

| Job | Schedule | What |
|---|---|---|
| `olivia-health` | `*/5 * * * *` | The outage alarm — runs **inside Postgres**, so it still fires when n8n is down. Signals: members receiving failure text · workflow-down markers (the relay's `maintenance` rows) · an active webhook ping. Re-alerts every 30 min while firing, posts recovery on clear, and stamps its own heartbeat. Known lag: it fired 69 min after the first failure of the 2026-09-02 credit outage. |
| `member-phone-index` | `*/15 * * * *` | `refresh_member_phone_index()` — the front door's phone lookup index (#128/#146). |

> ⚠️ `pg_net` installs into schema **`net`**, not `extensions`. Unqualified calls inside exception
> handlers fail silently — check `pg_proc` before assuming a function exists.

---

## Appendix C — The production workflow, node by node

`12wj6h1TWqb0d4Dq`, **80 nodes** (prod `30fd7e6f`, 2026-09-04; staging `bqHstPDi84uOhTCJ` carries the
identical graph on the other webhook path). Grouped by role:

| Group | Nodes | Notes |
|---|---|---|
| **Entry** | `WA Verify (GET)`, `Respond Challenge`, `WA Inbound (POST)` | Meta webhook verification + the single inbound entry point — reached through the Render relay (§1.1), never directly. Fan-out order off `WA Inbound`: `Extract Raw Event` · `Log Inbound` · `Parse Delivery Status` · `Parse Reaction`. |
| **Raw store (#75)** | `Extract Raw Event` → `Store Raw Event (Supabase)` | Wired FIRST — every inbound message event is on disk (`olivia_webhook_events`) before any parse can throw. |
| **Dedupe** | `Log Inbound` → `Claim Message (dedupe)` → `Drop Duplicates` | Non-text events branch off. Claim writes to `olivia_seen`; fails **open**. |
| **Intro taps (#97)** | `Intro Tap?` → `Intro Tap Detected?` → `Intro Route (HTTP)` → `Intro Handled?` → (`Intro Has Reply?` → `Build Intro Reply` → `Intro Eval (silent)?` → `Send Reply (Meta)` / `Save Conversation`) or (`Restore Original Message` → `Find Member`) | **In prod since 2026-08-22.** Accept/Decline button taps and `intro_pick_*` list taps resolve at the intro route and reply directly — never reach the LLM loop. `handled:false` restores the original message and falls through to `Find Member` unchanged. Ops + rulings: §8.7. |
| **Identity** | `Find Member` → `Resolve Member` → `Matched?` | `olivia_front_door_v2` by phone or hidden-number id (#146); exactly-one-active-member or the generic path (`Build Generic`, now wired through the silent gate so it can be probed). Four copies: matched · unlinked (#125) · inactive · unknown. Carries `airtable_id` (for stamping) and `at_member_id`. |
| **Context** | `Load Recent Turns` → `Prep Context` | 24h history, cut at "reset", plus the previous retrieval plan for "yes" replay and the previous turn's `pending_offer` (ids · bold titles · offer-line nouns · since #174 `items[{id,name}]`, the line she wrote for each offered video). The router sees each turn trimmed to 500 chars; the loop sees 1,500. `Prep Context` also emits `last_olivia_asks` (#143: did her last turn end with a question — read off the untrimmed row, like the intro-offer flag). |
| **Fast feedback** | `Mark Read + Typing` → `Holding Trigger?` → `Fire Holding Timer` | **Wired FIRST in the fan-out on purpose** — n8n v1 runs branches depth-first, so this must precede routing or the read receipt lands *after* the answer. |
| **Routing** | `Touch Olivia Stats`, `Route Request` (Haiku), `Fetch Chat Links`, `Plan Request` | `Plan Request` is the deterministic brain: ~40 overrides that outrank the router. Offer binding (#112) fires on the router's `accepts_offer`, a bare affirmation, an echo of her offer-line word, or — since #174 — `namedOfferItem()`: a message of ≤16 words naming one offered item by a capitalised word of its recorded line (speaker, product, title word), with a drill-down cue or two such words and no new-question opener; `offer_bind.mode` = `accept` or `drilldown`. **#143 guards:** a message opening a new question (any · who · when · how many · is there …) never reads as an echo acceptance; a bare ordinal ("the second one") after ≥2 offered items binds to that item as a drill-down; a yes after a turn whose last line asked nothing (`Prep Context.last_olivia_asks = false`, no recorded offer) takes the `nothing_pending` lane — the model is told to ask what they want, never to replay or claim an action; `ticketYes` also fires on `pending_offer.kind:'ticket'`. **#141:** `pronounSubject()` — a message of ≤16 words with a third-person pronoun and no new capitalised name keeps the person the previous plan was about (`p_member` of a member-card turn, `p_author` of an author-scoped search); on a content search the raw search is scoped to that author and their name leads the digest terms; since lap 2 (2026-09-08) the carry also covers the member-card lane and the raw search ranks the person's items by the message's DISTINCTIVE words only (`pronounTopicTerms()`, stop list + generic business words removed, max 4) — the raw search is full-text and generic terms bury the answer. **#144:** `eventsLaneCarry()` — a follow-up of ≤20 words after an `event_lookup` turn that names an event word or a year stays in the events lane with those terms (ticket and offer acceptances keep precedence). |
| **Retrieval** | `Embed Query` (Voyage) → `Fetch Summaries` → `Fetch Raw Matches` → `Verbatim?` | The "zeroth fetch", preloaded as guaranteed evidence. Both fetch nodes map `content_search` → `content_search_v2` at the last inch. |
| **Canned lanes** | `Build Verbatim Digest` | Greeting, help, chats, opt-in/out, reset, ticket offer/create, contact refusal, verbatim digests — **no model call at all**. |
| **The loop** | `Answer Seed` → `Answer Claude` → `Answer Parse` → `Answer Done?` → `First-Fetch Retry?` → (`Voyage Embed` → `Attach Embedding` → `Answer Tool` → `Answer Merge` → back) | Max 5 rounds, 29 tools, `max_tokens` 2000, thinking off. `Answer Parse` injects `p_phone` and names the reason when a failure IS billing; `First-Fetch Retry?` forces a retrieval when the first round answered without one (`retry_same`); `Attach Embedding` swaps the execution name to v2/v3 (`EXEC_NAME`). **`Answer Tool` dispatches by name:** every `event_*` name (prefix match — `event_schedule`, `event_who`, and also `event_lookup` / `event_history`, which never reach the catalog RPCs from the loop: #123) → the schedule route, `org_docs` → kb, `member_intro` → intro, `find` → find — all on digest.mds.co, policy in git — everything else → the Supabase RPC of the same name. |
| **Fact gate** | `Claims?` → `Fact Check` (Haiku) → `Gate Verdict` → `Gate OK?` | Claim-free replies, short affirmatives and clarifying questions skip it (RULE ZERO). One regeneration allowed, then an honest refusal; `off_topic` is a non-filterable verdict (#104). Deterministic link gate + post-filters run inside `Gate Verdict`; its clamp was audited over 6,017 answers before being softened (#149). The link-coverage repair (#1b) appends the URL of a row the draft names but does not link — since #175 paired per JSON row (`linkCoverageUrls()`), never by character distance, image keys excluded, duplicates of an already-linked title skipped; `link_coverage` on the output counts what it added. Since #139 a partner row (keys `name` · `offer_value` · `partner_url`, never `title`) is paired by its name and, when the draft names the partner without its link, the appended line is `Name (offer): page` — the offer text copied verbatim from the row. The #1c field repair (`registration_url` / `event_url`) since #175 lap 2 asks `fieldRepairSkip()` first — a row already linked by ANY of its own URLs is covered, a finished event (`is_over` / `phase: ended`) never gets a "Register:" line — and `_nameInAnswer` tests a name per line / clause, never across punctuation. **#142:** the IDENTITY second-person rule is `secondPersonAboutOther()` — it stands down when the draft names the real asker or explicitly refuses the typed name, and still fires when the draft personalises FOR the typed name. |
| **Delivery** | `Format Reply` → `Billing Nudge` → `Apply Nudge` → `Eval (silent)?` → `Send Reply (Meta)` → `Followup Interactive?` → `Send Followup Interactive (Meta)` | The eval branch skips Meta entirely. `Format Reply` converts markdown to WhatsApp formatting, extracts `[SEND_IMAGE:]` / `[SEND_FILE:]` markers, strips dangling orphan links and prepares `followup_interactive` (buttons or the list picker that could not ride a >1024-char body, #107). It also records the turn's `pending_offer` — video ids, bold titles (#143: only when the reply ends with an offer question, never a number — `*$3,615.00*` was once bound as an offer), the offer line's nouns, (#174) `items[{id,name}]`, the naming line above each video link, and (#143) `kind:'ticket'` when her last line offers in her own words to flag / file / raise / escalate something to the team — which Save Conversation persists on the row's `plan`. |
| **Persistence** | `Save Conversation`, `Mark Welcomed`, `Set Olivia Opt-State` | Both turns saved with plan + member stamp (gap #110: intro-tap turns). |
| **Attachments** | `Image To Send?` → `Fetch Post Images` → `Build Image Sends` → `Send Image (Meta)`; `File To Send?` → `Fetch Sendable File` → `Sign File URL` → `Send Document (Meta)` | File keys are re-validated server-side before any send. |
| **Team actions** | `Action?` → `Log Request (Supabase)` → `Notify Team (Slack)` | Only fires for genuine action requests, with conversation context and a member-log link. Also the escalation path the #97 "unreachable" flow reuses. |
| **Side channels** | `Parse Delivery Status` → `Save Delivery Status`; `Parse Reaction` → `Save Feedback (Supabase)` | Meta reports delivery once and never lets you query it back — dropping these is how "delivered" beliefs go wrong (`olivia_sends`). 👍/👎 reactions are the teaching signal (`olivia_feedback`). |
| **Manual utilities** | `Send Test (Manual)`, `Config`, `Send Message (Meta)`, `Fix Subscription (Manual)`, `Subscribe App to WABA`, `Check WABA Subscription` | Operator tools, not part of the answer path. |
| **Legacy** | `Build Prompt`, `Ask Claude`, `Build Generic` | The pre-loop single-shot path. `Build Prompt` still owns the **single global STYLE block** that `build_loop.py` harvests into the loop seed — edit style there, not in two places. |

---

*Maintenance rule: this handbook is updated in the same commit as the change it describes. If you
learned something the hard way, §13 is where it goes.*
