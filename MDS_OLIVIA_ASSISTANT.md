# MDS Olivia — Personal AI Assistant (Master Doc)

> **Owner:** Eugene · **Build:** Andy · **Status:** **Olivia ANSWERS LIVE on WhatsApp (2026‑07‑16)** — used
> by 3 real people (Andy, Ian Sells, Eugene Khayman) on the member‑initiated link.
> Channel: real number +1 945‑396‑5415, published, business‑verified (§8b). Agent: POC v2 on WA digests
> only — verbatim pulls, full‑history search, per‑member entitlements (§8c). Data: `wa_messages` backfilled
> 0 → **10,209**, conversations now stored in `digest.olivia_messages` (§8d). **The digest portal's login OTP
> also runs on this number now — Twilio is out (§8e).**
> **Still: nothing captures group messages going forward, and no session memory — see §9.**
> This is the canonical doc. It **supersedes and consolidates** the two source files from Eugene
> (V1 Pilot Sprint Plan + V2 Process) and locks every decision from the 2026‑07‑13 working session —
> including things discussed live but never written down (speed, DBs, build‑vs‑buy, access control).
> Verify against live systems (n8n / Airtable / Supabase / Render), not this doc.

**Source files (Eugene):** `~/Downloads/MDS-Olivia-V1-Pilot-Sprint-Plan.docx` · `~/Downloads/PROCESS-V2.md`
**Related:** MDS Video Platform CU doc `2531q-98637` (the `mds-ai-bot` backend + iOS search live here).

---

## 1 · Overview & Vision

**Olivia = a personal AI assistant for MDS members.** She does two things:

- **Side A — Proactive weekly push:** each week, pick 2–3 genuinely relevant items *for this member*
  (a video, a chat, a member to meet, an event, a partner offer). Remember what was already sent →
  never repeat. **Skip the week entirely if nothing is genuinely relevant.**
- **Side B — Reactive agent (Q&A):** the member asks a question, gets an answer. Question types,
  simplest → hardest: structured lookup ("next event in NY?") · open‑ended topic ("what's happening
  with AI?") · **member matchmaking** ("who knows about X?" → suggest + optionally make an intro) ·
  partner offers.

**Core answering principle (Eugene):** the agent's job is **not to *be* the answer — it's to route to
an MDS resource.** Every answer = a short TL;DR + up to ~3 MDS places to go look.

**Who it's for:** MDS members. Long‑term the foundation is SaaS‑ready but that's not being built now.

**Relationship to the existing stack:** Olivia is a **new channel on top of things that already exist** —
the WhatsApp digest pipeline, the video platform + transcripts, and the iOS app's Claude search agent.
It reuses those; it does not rebuild them.

---

## 2 · Channel & Initiation (locked)

### The rule that dictates everything
On WhatsApp's official API you can only **freely message someone within 24h of *their* last message
to you**. To message cold (or after 24h) you need a **pre‑approved Meta template**.

### Decisions
- **Whapi collects, Meta chats.** Whapi reads the **group** chats for the digest (Meta's Cloud API
  structurally *cannot* read WhatsApp groups). Olivia's **1:1 DMs run on Meta Cloud API**, on a **NEW
  dedicated business number**.
- **`+1 786‑657‑8153` never moves to Meta.** It's the group‑reading number on Whapi; putting it on
  Meta would make the digest permanently impossible. Keep it on Whapi forever.
- **Member‑initiated (overrides Eugene's V1 "MDS sends first").** The member messages Olivia first;
  her welcome is her **first reply**, not a cold outbound. Why: no template ever needed, consent is
  built in, the 24h window opens naturally, and it kills the "new number DMing you = phishing" feel.
- **How members know what to do:** a **click‑to‑chat link** (`wa.me/<number>?text=Hi`) opens WhatsApp
  with the message pre‑typed — they just hit send, and Olivia's reply does the onboarding. For the
  pilot: a warm personal nudge with that link to 5–10 members. For scale: same link in an in‑group
  announcement (from the known number), the onboarding email/call, and a QR at events.
- **Proactive weekly (Side A) is later** and needs Meta‑approved templates.

---

## 3 · Build Order & Strategy (locked)

**Order: ① Data structure → ② Web agent → ③ WhatsApp bot.**

- **① Data structure first** — the real foundation, and channel‑independent (same brain whether it
  ends up on web or WhatsApp). This is a **separate planning session** (it's big).
- **② Web agent second** — the low‑risk proving ground: no ban risk, no Meta template approval, no
  BSP onboarding wait, reaches everyone (not just WhatsApp users), and you can just open it and watch
  it work. Same brain as the iOS app; web is mostly putting that brain on a surface you can iterate on.
- **③ WhatsApp bot last** — a thin channel wrapper around a brain that's already proven; highest
  friction + ban risk, so it goes last. (The Meta POC below is that last step, done early just to
  de‑risk it.)

This matches Eugene's own "Side B first" build order.

---

## 4 · The Data Layer — the real hard problem (locked)

The bot is easy. The hard, risky work is the data. Proven live in the session: answering one
question — *"last event in Canada, who was there, anyone over $10M/yr?"* — required hopping **GroupOS**
(event + attendee roster) → **Airtable Members DB** (revenue), joining by email, and it surfaced
scattered data, **contradicting revenue fields** (a $4M member tagged "10–20M"), duplicate records,
staff mixed with members, and no access gating. A bot answers only as well as the data underneath.

**The data layer is THREE problems, not one:**

1. **Canonical source + freshness** — one agreed system‑of‑record per source (events, revenue,
   videos, members, partners, programs), the fields the agent may read, and how fresh each is.
   *(Eugene's §3. Member data alone is scattered across 3+ Airtable bases; the real one is the
   **Members DB `appou5JVr0WIrioWS`** — the phone→member link already exists via `source_member_id`.)*
2. **Entitlements / plan‑ & content‑level access** — what is *this member's plan* allowed to see?
   Not just tier‑level: a **specific event or a specific video can be restricted**. The agent must
   answer **as the asking member**, never as an admin, and filter per query.
3. **Personal‑data sensitivity** — even for content a member *can* access, some facts about *others*
   are confidential and must **never** be surfaced: **income/revenue**, contact details, private
   business info, who‑said‑what. (A live community concern already exists about members being publicly
   named without consent.)

**Rule (from Eugene + Andy):** the agent only reads sources that have been **cleaned + defined +
access‑tagged**. Undefined source = the agent acts as if it doesn't exist. No crawling raw bases.

### Where the data lives → Supabase
- **Airtable stays the source of truth** (curated, low‑volume, ~5 req/s — not a query engine).
- **Supabase becomes the serving layer**: a pre‑processed, **indexed, access‑aware** store fed from
  AT + GroupOS + content, with **each item's access rule and sensitivity attached per row**.
- Airtable **cannot** do fast, per‑item, permission‑filtered lookups at scale; Postgres/Supabase
  (indexed, an access column per row) is built for exactly that.

---

## 5 · Speed & Performance (discussed live — locked)

- **Why a naive bot is slow:** answering live means hunting across systems + joining at question‑time
  (the 5‑minute treasure hunt). **Google is milliseconds because it indexed everything *ahead of
  time*** — the query is a lookup against a ready structure.
- **The fix = do the slow work at *ingest* time, not answer time.** A background job (like the
  automations we already run) gathers + stitches + tags all the data **once**, into one indexed
  Supabase store. Then any question is a fast lookup.
- **You do NOT predict questions — you organize the *data*.** (Prep the ingredients, not the dishes;
  index the pages, not the searches.) The one real boundary is which **sources** are prepped; each new
  source unlocks a category of questions.
- **Realistic latency:** expect **ChatGPT‑speed (~a few seconds)** per answer — NOT Google‑instant
  (there's an LLM reasoning in the loop). Keep it fast by: consolidated data (ms lookup) + fixed query
  tools (no live schema‑hunting) + short answers. **Streaming** (words appear as written) makes web
  *feel* instant — a quiet point for **web‑first** (WhatsApp can't stream).
- We already run a mini version of "process ahead of time": the members mirror job copies Airtable →
  Supabase every 15 min so the portal reads fast. Olivia is that idea, extended.

---

## 6 · The Model — Build vs Buy (discussed live — locked)

- **Do NOT build/train our own model.** That's hundreds of millions of dollars, a research team, and
  years — rebuilding what Anthropic/OpenAI/Google already did. Never makes sense for MDS.
- **Two layers of the AI world:** Layer 1 = the few giants who train the brains (the "millions").
  Layer 2 = **everyone else** (Slack AI, ClickUp AI, Cursor, the video‑gen startups, **and Olivia**) —
  they *rent* a Layer‑1 brain via API and wrap it with **their own data + product**, paying cents per
  request. That's 99% of the AI tools appearing daily.
- **So Olivia is a Layer‑2 product** ("an AI product like Slack AI," on top of Claude). The moat is the
  **data + access layer + product** — not the model. Exactly why the hard part is the data (§4).
- **Model = Claude API + RAG on our data.** "Your own AI" = **Claude (rented brain) + our data + our
  prompt + our access rules.** Fine‑tuning exists (Anthropic offers it) but we almost certainly don't
  need it — RAG gets us there without the cost/lock‑in.
- **Reuse the iOS brain — don't rebuild it.** The reactive agent already exists: **`mds-ai-bot`**
  (Render Flask, RAG over video transcripts + WA digests + legacy Otter in one ChromaDB, Claude
  synthesis) at **`POST /api/ask`** (`{question}` → `{answer, sources, confidence}`). The iOS app is
  just a front‑end calling it. Olivia calls the same endpoint.

---

## 7 · Identity, Memory & Privacy (locked)

- **Identity:** reuse the matcher's canonical output — WA `source_member_id` (the Members‑DB rec‑id) +
  the admin‑editable `WhatsApp Number (Verified)`. **Do NOT add a 5th phone field.**
- **Hard‑fail on ambiguous match.** Members‑DB data is dirty (typo'd phones, dup records sharing a
  phone, ~69 of 515 senders match nobody). A wrong match → Olivia recites *another* founder's business
  in a private DM = a trust/confidentiality incident. Phone ≠ exactly one member → generic reply + flag.
- **Conversation memory → Supabase `digest.wa_messages`** (already modeled, empty), NOT Airtable
  (5 req/s → 429). History is a **parse/backfill of existing Airtable `Summaries.source_messages_json`**
  (recoverable ~2.5mo). **Gated on Andy's retention/privacy decision** (still open).
- **Privacy inversion:** the digest deliberately anonymizes ("a member"); Olivia de‑anonymizes into a
  private DM. Fine for the member's *own* data; **never** reveal others'. Pick the policy before Sprint 1.
- **⚠️ Access‑control gap (critical):** today `/api/ask` has **no per‑member gating** — it returns all
  public videos + all WA digests to *any* authenticated member (the M10 gap). This **must** be built
  before Olivia is used with real members, or she'll leak restricted content.

---

## 8 · POC Results — 2026‑07‑13 (what we proved)

Built a **standalone** n8n workflow (`Af2atRScbYSOTYbC`, "do‑not‑merge") + a throwaway Meta app. **Touched
nothing existing.** Proven end‑to‑end:

- **Send works** — Meta Cloud API `hello_world` template (cold‑start opener) + free‑text (once the
  member replies, inside the 24h window). Both delivered to Andy's WhatsApp.
- **The real agent loop works** — inbound message → fetch a bot token (runtime) → **`/api/ask`** →
  real sourced Claude answer → WhatsApp reply. Verified with real questions ("AI automations",
  "Claude Fable") — answers pulled from actual MDS WA groups + video sessions with real member names.
- **Webhook shape:** GET verify (echoes `hub.challenge`) + POST inbound (parse → token → ask → format
  → send). Token obtained via the bot's own **OTP login** (`/api/auth/request-code` + `/verify`).

### Known limits / caveats
- **Real inbound is blocked while the app is unpublished** — Meta only delivers *test* webhooks in
  Development mode. Making a member's typed message flow through needs the app **published + business
  verification** (= production, days‑to‑weeks). The loop was proven by simulating the inbound.
- **This entire POC account is DISPOSABLE** — Andy's personal Facebook + `tangowithw@gmail.com` +
  personal WhatsApp number. **Production = a new business Meta account + dedicated number + published,
  verified app.** Do not reuse this account.
- Temp 24h Meta token; `n8n` active‑workflow edits need **deactivate+reactivate** to reload the webhook.
- **Cleanup pending:** the POC n8n workflow + the OTP `AuthSessions` row (`olivia-poc`… / tangowithw)
  can be removed when we move to production.

---

## 8b · Production Channel — LIVE (2026‑07‑16) · supersedes §8

**Gate 1 (production Meta) is DONE.** All four channel acceptance criteria closed on a **real number**:
app live · admin/API send works · auto‑send via API works · **a real typed member reply is received and logged**.

### Live assets
| Thing | Value |
|---|---|
| App | **MDS Community** `955961257089837` — **PUBLISHED / Live** |
| Business | `319492488643119` |
| WABA | `1575708577606583` ("Oliva") |
| Number | **+1 945‑396‑5415** — Connected, quality High, display name "Oliva" (in review) |
| Phone Number ID | `1306956855827812` |
| Business Verification | **COMPLETE** · Payment **Added** |
| n8n workflow | `12wj6h1TWqb0d4Dq` — ACTIVE, 10 nodes, standalone |
| Webhook | `https://mdsco.app.n8n.cloud/webhook/olivia-wa-live` · verify token `mds-olivia-verify` |
| Token | n8n **Header Auth credential** `XKqRew9l9061A7jG` — **not** hardcoded |

**Abandoned:** the free test number (+1 555 155‑4295 / pnid `1203578386172635` / WABA `1358627259704555`).
It sits on a **different WABA** — a token minted for one WABA cannot touch the other.

**Timeline correction:** business verification was assumed to be the days‑to‑weeks long pole. **It took one day.**
The channel is no longer the bottleneck — the data layer is.

### 🔑 The big lesson: receiving needs FOUR things, sending needs one
Each shows green on its own screen while the chain is silently broken. There is **no error** anywhere — messages
get double ticks and simply never arrive.

1. Callback URL verified (GET echoes `hub.challenge`)
2. **App published** — Development mode delivers **zero** production data, *explicitly including from app
   admins/developers/testers* (Meta's own banner). ⚠️ §8's original claim was **right**; a "correction" made
   during this session saying dev‑mode inbound works for allow‑listed users was **wrong**.
3. **App subscribed to the WABA** — `POST /{WABA_ID}/subscribed_apps`. Ours was **empty** → silent drop.
4. **`messages` webhook field subscribed** — every field defaults to **Unsubscribed**; separate from step 1.

**Sending needs none of 2–4** — that asymmetry is what makes this confusing.
**Diagnosis order for "sent, double ticks, nothing arrives" → check 3 and 4 first.**

### Gotchas
- The **dev‑site** API Setup "Generate token" for a *registered real number* mints a **permanent** token.
  A business‑side **System User is NOT required** (it's the "having trouble?" fallback).
- n8n Header Auth credential: **`Name` = the HTTP header name = `Authorization`** (not a label);
  **`Value` = `Bearer <token>`** — the `Bearer ` prefix is mandatory (omitting it → "Authorization failed").
- n8n **auto‑selects an existing** Header Auth credential (e.g. "Supabase secret") — explicitly Create New.
- `"Object with ID X does not exist / missing permissions"` = wrong ID, **or** token from a different app/WABA,
  **or** a brand‑new test number not yet provisioned (~1 min).

### Proven
- Send — exec `36007` → `message_status: accepted`
- **Real inbound** — exec `36019` → `{event:"inbound message", from:"17866578153", name:"Andy", text:"Hi", …}`

### Deliberately NOT built
The workflow **only logs** inbound — no reply, no `/api/ask`, no agent. That is per the AC ("we don't react yet").
`hello_world` is a throwaway template. Old POC `Af2atRScbYSOTYbC` still contains a plaintext Airtable PAT +
dead Meta token → **cleanup candidate**.

---

## 8c · Olivia POC v2 — LIVE (2026‑07‑16) · digests only

**She answers real questions on WhatsApp today.** Workflow **`12wj6h1TWqb0d4Dq`** (26 nodes, ACTIVE,
standalone, do‑not‑merge). **`/api/ask` is NOT used** — Andy's call: it blends the live WA digests with a
**stale video library** (300 Otter transcripts + a few random videos loaded months ago, link accuracy
unverified). A confidently wrong video answer in a private DM is the trust incident §4 warns about. So
Olivia reads **one clean source**: WA digests. That is §4's rule applied — *an undefined source does not
exist to her*.

### The chain
`Log Inbound` (drops non‑text: our own sends generate status callbacks) → `Find Member` → `Resolve Member`
(**hard‑fail** unless exactly 1 match) → `Matched?` → `Route Request` (**Haiku**, JSON) → `Fetch Chat Links`
→ `Plan Request` (deterministic) → `Fetch Summaries` (scoped query) → `Verbatim?` → either
`Build Verbatim Digest` (**no LLM**) or `Build Prompt` → `Ask Claude` (Sonnet) → `Send Reply`.
`Touch Olivia Stats` hangs parallel off `Matched?` so counting never delays or breaks a reply.

### Routing — pull what exists, generate only what doesn't (Andy's rule)
| Member says | Route | Claude sees digests? |
|---|---|---|
| "hi" (first ever) | static intro + image | **no** |
| "hi" (since) | static one‑liner | **no** |
| "digest/what's new in AI chat" | **stored weekly, verbatim** | **no** |
| "…in AI chat yesterday" | **stored daily, verbatim** | **no** |
| "monthly digest for X" | generated from 30d of dailies | yes — not stored |
| "what's new around claude fable" | **searches ALL history** | yes — only matches |
| vague question | last 7d fallback | yes |

**Why Haiku routes:** keyword matching was brittle — "what **was happening**" ≠ "what happened", and
"what's new" wasn't matched at all. Haiku reads **only the member's sentence + their chat list** (~500 tok)
and returns `{intent, chat, period, date_hint, search_terms}`. **It never sees digest content.** Code then
decides everything; the router advises. Ambiguous period on a digest → **weekly** (Andy).

**Search beats time‑windows — proved with numbers:** "fable" appears in **26 daily digests all‑time** but
only **5 in a 7‑day window**. The old window silently missed **81%** and would answer "I don't see anything
about that" — a *wrong* answer, not a missing one. Search also uses **less** context (26 rows ≈ 18K chars vs
a 7‑day slab ≈ 64K).

### Entitlements
Everything is filtered to the member's **`channels_present`**: chat list, links, search results, and the
router's own output (it may only name a chat they're in; `Plan Request` clamps it). The intro's example chat
is their **busiest**, computed live — an earlier hardcoded "MDS AI & Automations" broke this very rule.
⚠️ **Filter‑after‑fetch, not filter‑at‑query:** search *fetches* rows from chats they're not in, then drops
them in code. One line in `Build Prompt` is the whole gate. The unified index (§9.7) fixes this properly.

### Engagement (Andy asked for it in the WA DB)
Counted in Supabase per message (`digest.olivia_touch()` — a function, so concurrent messages can't lose a
count), synced **daily** to **WA DB Members `tbli8B589iNbsGF0Z`** by n8n **`BfLqFlwzBBe0LgMy`** (7:30am ET,
batches of 10). **Never per‑message to Airtable** — 5 req/s SoT, and hot writes churn the 15‑min mirror
(that's what caused the 429 storm). Fields: `Olivia Interactions` / `Olivia Last Active` / `Olivia Welcomed`.
⚠️ Three identically‑named **orphan fields** were created on Members DB `tblfwOSROSHfuYUxv` by mistake —
nothing writes them, and **Airtable's API cannot delete fields** (UI only).

**Meta is a pipe, not a database.** Confirmed live: `conversation_analytics` allows only
`{UNKNOWN, PHONE, COUNTRY, CONVERSATION_TYPE, CONVERSATION_DIRECTION, CONVERSATION_CATEGORY}` — **no
per‑contact dimension exists**. Webhooks fire once; unstored = gone. Hence our own counters.

### `olivia_intro` template — APPROVED
Image header + `{{1}}` name, `{{2}}` chat count, `{{3}}` busiest chat. Category **MARKETING** (per‑user
limits + opt‑out apply — fine for a pilot, a real delivery risk at 500). Send with
`scratchpad/send_olivia_intro.py <phone> [--name X] [--send]` (dry‑run default) — it hard‑fails on ambiguous
identity and **stamps `olivia_welcomed_at`**, so the member's reply gets the short greeting instead of the
poster twice. **Sent to Ian Sells 2026‑07‑17 00:02.**
Gotchas: media header needs the **Resumable Upload API** (`Authorization: OAuth`, not Bearer) → handle;
`{{1}}` **collides with n8n's `{{ }}`** so build payloads in a Code node; template text **freezes** at approval.

---

## 8d · Data layer — `wa_messages` backfilled (2026‑07‑16)

**`digest.wa_messages`: 0 → 10,209 rows.** Apr 23 → today · 6,169 with text · 375 senders · 17 chats.
**Exact quotes now exist and join to real full names** (the digest writes "Daniel"; the message layer gives
"Daniel Crackower" — because we attribute by **phone**, not by trusting prose).

- Script `scratchpad/backfill_wa_messages.py` (dry‑run default). **Idempotent** — PK is the Whapi message id.
- `sender_member` → FK `digest.members.airtable_id`; unresolved phones become NULL (25 LID senders have no phone).
- **Truncation verified, not assumed:** `source_messages_json = JSON.stringify(...).slice(0,95000)` broke
  **10 of 1,105 rows (0.9%)** — 9 in AI & Automations, 1 in TikTok. A **string‑aware** scanner (braces inside
  message bodies fool a naive one) recovered **1,178 messages** from those 10 days.
- **⚠️ CORRECTION 2026‑07‑17: the earlier "nothing was ever lost" claim here was WRONG.** Measured against
  Airtable's own pre‑slice `msg_count`: **366 text messages on those 10 days never made it into
  `source_messages_json` at all** — the slice cut them at write time, so no parser could recover them.
  They exist only in `raw_log` (untruncated, but names‑not‑phones and no message ids) or via a Whapi
  re‑fetch of those 10 chat‑days, if Whapi retention reaches April. Andy has not asked for recovery.
- **The 95K slice exists because Airtable has a long‑text limit. Supabase doesn't** — once the digest writes
  here, truncation stops being necessary at all.

**✅ FORWARD CAPTURE SHIPPED 2026‑07‑17 — the decay is stopped.** (Digest‑project change, `qo3qzeVtprhTW88F`.)
`Prep Claude Request` now also builds a **`wa_messages` array (one row per message, NOT sliced)** and a new
node **`Save WA Messages (Supabase)`** upserts it to `digest.wa_messages` (`on_conflict=id`,
`resolution=merge-duplicates`) — PK = Whapi message id, so re‑runs never duplicate. **The 95K slice was not
ported**: it stays on the Airtable write only, because that's the only thing that needs it.

- **Verified before going live, not asserted:** the patched code was replayed against real exec `35803` data —
  it reproduced the backfill's rows **byte‑for‑byte** (44/44 rows, all fields + timestamp, 0 divergence).
  The PostgREST payload, the empty‑array case (11 of 18 chats are quiet on a normal day), a NULL
  `sender_member`, and the `{{ $json.wa_messages }}` binding were each proven against the live table
  (in a throwaway workflow, since deleted). Nothing new was written by any test.
- **No gap:** the window is a rolling 24h (`from = now-24h`), and runs are 24h apart, so each chat's windows
  tile exactly. The first capture run (7am ET 2026‑07‑17) resumes precisely where the backfill snapshot ends.
- **`sender_member` is NULL when unmatched** — it's FK'd to `digest.members`, and a bad id would fail the batch.
- **⚠️ It soft‑fails on purpose** (`onError: continueRegularOutput`, 3 retries): this node must never be able
  to take down the member‑facing daily email. **Airtable still holds the raw**, so a failed write is
  *recoverable* (re‑run the backfill), not lost. **The cost: a capture failure is currently silent.**
  Before the Airtable raw writes are retired ("later" per Andy), this needs a real freshness alert.

**Framing correction (Andy, load‑bearing):** the who‑said‑what question was recorded for weeks as "blocked on
Andy's privacy decision". **It never was.** The doc already decided *we must process who said what*. The open
question is only the **security mechanism** in Supabase — access is the same `channels_present` gate Olivia
already enforces (*she can never tell you anything you couldn't scroll up and read yourself*). Retention
window is still genuinely undecided.

### Also new
- **`digest.chats`** — 18 chats, 17 invite links, chat_ids. Single source of truth for "open the chat" links.
  ⚠️ The portal still hardcodes the same map in `mds-digest-web/src/lib/whatsapp.ts` → **will drift**.
- **`digest.members`** — `olivia_welcomed_at`, `olivia_interactions`, `olivia_last_used_at` (Olivia‑owned;
  the mirror doesn't write them).

---

## 8e · Digest‑portal login now runs on this number (2026‑07‑16) — and that's a coupling

**Twilio is out of the login path.** `mds_login_code` (AUTHENTICATION template) is APPROVED and the portal
sends the OTP over WhatsApp. Shipped in `mds-digest-web` PR #7 → merged to main.

- **Why it works where marketing didn't:** AUTHENTICATION templates are **exempt from the per‑user
  marketing suppression** (error 131049) that silently killed Ian's intro. They're built to be sent cold.
- **Why it unblocks you:** phone login was stuck behind **Twilio A2P registration**. Every MDS member is on
  WhatsApp by definition, so this sidesteps Twilio entirely.
- **Approved instantly** — Meta fixes the wording (`<CODE> is your verification code` + copy‑code button),
  so there's nothing to review. You cannot customise the text.
- **Code:** `src/lib/whatsapp-otp.ts` (new) · `api/request-otp` prefers WhatsApp, **falls back to SMS**.
  Env vars are deliberately **NOT** in `config.ts`'s `required` list — that list throws at boot, so a deploy
  without them would take the portal down. Unset ⇒ SMS ⇒ behaves exactly as before.
  Needs on Render: `META_WA_TOKEN`, `META_WA_PHONE_NUMBER_ID=1306956855827812` (**no auto‑redeploy on env change**).
- **Verified live:** route → `{"ok":true,"channel":"whatsapp"}` · Meta → `status=delivered` · portal stored
  `otp_code_hash`. Not inferred — driven end to end.
- **Also fixed a silent login bug:** the phone input stripped non‑digits and prepended `+`, so a US member
  typing `7866578153` became **`+7866578153` — a RUSSIAN number** matching nobody, surfacing as "member not
  found" rather than an error. Any 7–15 digit string counted as valid. Now `libphonenumber-js`: formats as
  you type, auto‑detects country from `+`, validates for real, caps at **15 digits (E.164 max)**, and shows
  *"Sending to +1 786 657 8153 · US"* before you commit.

### ⚠️ One number now carries BOTH Olivia and login. Fine today; know the failure modes.

| Risk | Why it bites |
|---|---|
| **STOP is per‑number** | A member who finds Olivia annoying and replies STOP **also blocks their own login codes**. They'd be locked out of the portal by opting out of a chatbot — and would never connect the two. |
| **Quality rating is per‑number** | Olivia is chatty and optional; login is critical infrastructure. Blocks/reports against *her* degrade the rating that *OTP delivery* depends on. |
| **Messaging limits are shared** | Olivia's conversations consume the same per‑number tier as authentication. |
| **Ban blast radius** | Lose the number and you lose the assistant **and** every member's ability to log in, at once. |
| **Display name is DECLINED** | `name_status: DECLINED` — codes currently arrive from a bare **+1 945‑396‑5415**, which is exactly the shape of a phishing OTP. Worse for auth than for chat. |

**Verdict: acceptable now** — pilot volume, 3 users, low risk, and one number is simpler. **Split before scale:**
login is the thing that must never break, and it should not share a reputation with an experimental assistant.
Cheapest split later = a second number for auth only; the portal already isolates sending in
`src/lib/whatsapp-otp.ts`, so it's a config change, not a rewrite.

**Immediate:** resubmit the display name (likely rejected because "Oliva" doesn't match the verified business —
try "MDS" / "Million Dollar Sellers"). A named sender helps chat and matters more for auth.

---

## 8f · The `content_items` unified index — LIVE (2026‑07‑20) · Olivia's only retrieval, forever

The data platform §4 called for now exists. **`digest.content_items`** = one access‑tagged index
row per item across all sources (source, kind, source_id, title, tl_dr, body, occurred_at, url,
**`access_rule` jsonb**, **`sensitivity`** enum, search_extra, meta jsonb, search_tsv). RLS on from
birth, service‑role only.

**Sensitivity is DATA, not prompt politeness (Andy's ruling):**
- `never_surface` — exact addresses, phones/emails, revenue figures, application hard‑gate fields.
  Retrieval NEVER returns these rows, even with every other flag in the caller's favor.
- `restricted` — member↔member intros needing consent. Excluded by default; returned only with an
  explicit `p_include_restricted` (the future consent path — nothing passes it today).
- `normal` — subject only to `access_rule`.

**Access rules are baked per row at ingest** (`{"type":"chat_member","chat":X}` for both current
sources; `{"type":"public"}` supported). **Unknown rule type = DENY, fail closed** — a future
source with a new rule shape is invisible until `content_search`/`content_lookup` learn the rule,
which is §4's "undefined source = the agent acts as if it doesn't exist" made mechanical.

**Retrieval = exactly two Postgres functions, forever:** `digest.content_search()` (terms,
sources, kinds, chat, since, limit) and `digest.content_lookup()` (source, kind, chat, date
filters, order). Both resolve the asking member **server‑side from `p_phone`** (unknown or
ambiguous phone → zero rows), enforce sensitivity + access **in SQL**, live‑join `sender_name`
(name fixes propagate to historic quotes), and never emit `sender_phone`. anon/authenticated are
revoked on both. Olivia's n8n workflow calls them as PostgREST RPCs and **can no longer compose an
ungated query** — the digest search's filter‑after‑fetch (the last one) is dead.

**Ingest is DB triggers on the source tables** (`summaries`, `wa_messages`) plus an idempotent
backfill — the existing summaries mirror and the digest's per‑message upsert keep the index fresh
with zero workflow changes. Source tables stay SoT; the index is derived. 1,276 digests + 10,429
messages at cutover, counts exact.

**The test held: adding the index changed retrieval, adding a source never will.** Rewire touched
5 nodes (`Plan Request` emits op+params; the two fetch nodes are RPC POSTs; the two build nodes
read the canonical shape). Behavior verified identical before/after: SQL row‑set diffs on all 7
route shapes; live exec diffs (system prompt + quotes block byte‑identical, verbatim reply
byte‑identical); `scripts/verify_content_items_equivalence.py` green across 3 real members. One
deliberate improvement: when the old 80‑row search cap bound, it wasted slots on unentitled chats
then post‑filtered — the index returns entitled‑only rows (a 1‑chat member went from 16 → 26
usable rows, every legacy row still present, zero unentitled).

**The red‑team leak gate exists and is THE gate: `scripts/olivia_leak_gate.py`** (Scorecard repo).
18 checks against the live functions: canaries at every sensitivity tier and entitlement shape
(never_surface hidden even with the consent flag · restricted hidden by default · unentitled chat
hidden · unknown/malformed access_rule denied · unknown phone = zero rows · no `sender_phone`
anywhere · wa_message meta keys allowlisted · anon key rejected on both RPCs · canaries cleaned
up). **No future source ships until the gate passes with that source's rows in the index.**
Andy's order remains: applications (hard gates) → events → videos.

---

## 8g · Events — source #2 LIVE (2026‑07‑20) · AT catalog, gated RPCs, match‑don't‑quote applied

> **⚙ 2026‑07‑22 update — CHAPTER GATE.** `event_lookup` now enforces Debbie's access rule: a
> chapter event is visible **only to that chapter's members**; Public → all; non‑chapter → all;
> `Open to Guests` adds a +1 but never widens the chapter gate. Match key = **Chapters record‑links**
> (`member_attributes.chapter_ids` ∩ `events_catalog.chapter_ids`), synced from AT Members "Chapter
> Affiliation"/"Link to Chapters" and the Events **`Chapter`** field (NOT `Chapter Area` — blank‑prone,
> dropped). An event that looks like a chapter event (style='Chapter' or name mentions "Chapter") but
> has **no `Chapter` link tagged** is **fail‑closed** (hidden from all until the events team tags it).
> Postponed/Canceled excluded from upcoming. **Field allowlist is HARD** — only the ~14 member‑safe
> Events fields are synced; every admin/finance/PII field (Partner Revenue Goal, Var/Fixed Budget,
> Partner Revenue Actual, Min/Max Member+Attendee Goals, Event Roster Link, Managed By, Host, Clickup)
> is never requested from Airtable, never in Supabase, never emitted. Leak gate = 114 (chapter event
> hidden from a non‑chapter member + no admin field in output). Migrations `member_attributes_chapter_fields`,
> `events_catalog_chapter_ids`, `event_lookup_chapter_gate`(+`_failclosed`).

**SoT (Andy's ruling + Debbie's flow):** every event is born in the **Airtable Events table**;
`Event Planning Status (Phase)` Tentative → Confirmed → **Registration Open** (the only
registerable state) → Postponed/Canceled. The app (GroupOS) + Luma are registration surfaces;
the **Event Roster** table is the per‑registration ledger (record‑linked member↔event, fed live
by the app — read the WHOLE table, its views filter). `Guests?` = audience rule
(MDSonly / Open to Guests / Public Event). Descriptions live nowhere pullable (flagged; Andy
checking the app API) — answers ride on title/date/city/audience/price/spots, and titles carry
the topic.

**Data:** `digest.events_catalog` (junk/Tentative/dup‑guarded; app‑joined rows carry tz‑correct
times + marketing titles + app URLs; Virtual always displays AT wall time "as listed") +
`digest.event_registrations` (member‑linked + guest rows; guests never surface). Daily sync =
second step of member‑profiles‑sync (PR #17). Spots left = `Venue Capacity` − live roster count.

**Retrieval = two more gated RPCs, same contract as everything else** (asker resolved from
phone in SQL, fail closed, anon revoked): **`event_lookup`** — per‑asker annotated catalog
(is_registered / can_register / sanitized reg_link — `/admin/` URLs never emitted / guests
policy / spots_left / audience_hint; banded 20M+/50M+/100M+/Centurion events omitted from
browse for non‑qualifying askers, describe‑only on direct ask, exactly like
chat_recommendations). **`event_who`** — member names + city/state ONLY (token‑AND event match,
guest registrations structurally excluded, banded rosters gated, is_me flag). Router intents
`events` + `eventwho`; prompt rules: dates verbatim, postponed/canceled truthful and never
recommended, already‑registered acknowledged, tier stated but never "you qualify/don't".

**Gate = 57 checks green** (Tentative canary invisible · banded browse+roster gating proven
with a real non‑20M asker · guest exclusion · output shape allowlist · anon denied on RPCs and
tables · cleanup). Live‑verified on the real webhook incl. Andy's vision example: *"who is
going to the tiktok dinner?" → all 10 registered members with cities.*

---

## 8h · Member-data exposure settled + the people layer (2026‑07‑20 night)

**The exposure policy, as it evolved in one day (audit trail matters):**
1. *Match, don't quote* (Andy, afternoon) — all member data = matching fuel; only people-lists surface.
2. *No attendee names* (Eugene, first reading) — who-lists became aggregates only.
3. **FINAL — "public-in-the-app = shareable" (Eugene):** whatever a member can already see in
   the app/directory, Olivia may share. Everything else keeps the honest-boundary refusal.

**What that unlocked, all live + gate-proven (77 checks):**
- **`member_card(p_phone, p_member)`** — the SIX directory-public fields for a named member:
  Facebook Profile Link · About Me · **revenue TIER** (band only — exact figures never exist on
  this path; "tiers are as specific as it gets") · Main Niche · Area of Expertise · Hobbies
  (+ name/city/state/fun fact). Statuses: 4 active + Staff (Ian/Eugene resolve). Junk guards:
  FB link must be a real facebook.com URL; N/A-filler nulled. Router intent `membercard`.
  Cards render as PROSE dossiers, never field dumps.
- **`shared_chats`** on the card = the intersection of the ASKER's chats with the target's —
  exactly what the asker could see in their own WhatsApp groups; the target's other chats are
  never emitted (gate: shared ⊆ asker's own). "How many chats am I sharing with Guido?" → "4:
  AI & Automations, Centurion 20M+, Mogul Call announcements, Trading."
- **Who-is-going lists = names again** (`event_who` v4: names + state, state rendered only for
  location questions; guests and tier-gated rosters still excluded in SQL).
- **`member_dossier(p_phone)`** — "what do you know about me" is a written dossier from the
  member's OWN data: profile + application + their active chats (30d counts) + their own recent
  messages + their events. Own data only; no path to anyone else's.
- **`community_info(p_phone)`** — exact community stats ("how many members are in MDS?" → 714
  active members; chats; upcoming events). Was previously unanswerable.
- **WhatsApp formatting**: Format Reply converts markdown `**bold**` → WA `*bold*` on all routes.

**Events layer, completed same night:** full-history ledger (1,406 events → 2018; 17,733
registrations), Member 360 Events section (upcoming + past, per-event grouping), history-aware
recommendations via `event_history` (asker city + own registrations → "near me", trip planning,
"have I been to Inspire?"), rollup-field validation (the four Members-DB event rollups carry
stamped verdicts in their Airtable descriptions; pipelines read the roster ledger, never the
rollups), AT record fixes (admin links → member URLs; `digest.member_event_url()` = the one
place encoding the URL structure — custom slugs will change it).

---

## 8i · Partners — source #3 LIVE (2026‑07‑21) · GroupOS app directory → Supa

**Andy's call:** partners before virtual events; copy to Supa, never live‑MCP passthrough
(n8n can't reach the MCP; MCP `q` is substring‑only; gated‑RPC architecture is non‑negotiable).

- **SoT = the GroupOS app partner directory** (community `67011d987a2a81b28438a3d8`), read via the
  GroupOS MCP. The AT partner tables (326‑field ops pipeline, W‑9s, payments) stay internal.
- **Scope: published only (488)** — paused (120) / drafts (5) are invisible in the app ⇒ don't
  exist for Olivia ("public‑in‑the‑app = shareable" applied to partners).
- **`digest.partners_catalog` 486 rows** (488 minus 2 API‑unfetchable "poison" records — a real
  GroupOS bug, bracketed to the minute, Andy reports it) · **`digest.partner_reviews` 922 rows =
  exact sum of review_counts**. RLS from birth, anon revoked, service‑role only.
- **Fields per partner:** name · description (FULLY in the API — verified byte‑identical to the
  app page, unlike events) · `offer_value` (the deal label; redemption details live on the app
  page only) · categories (opaque ids + **names**: AT "Associated Categories" name‑join 398/486,
  confident co‑occurrence id‑map for the rest → 97% named) · rating/review_count/claim_count ·
  featured/fresh_deal · access_restriction per row (all 486 = public today; non‑public rows are
  structurally invisible = fail closed).
- **Reviews:** member review text is public‑in‑the‑app ⇒ quotable; reviewer identity is NOT
  (app_user_id stored for provenance, never emitted; Olivia never names/guesses reviewers).
- **`partner_lookup(p_phone, p_query, p_limit)`** — the only partners retrieval: asker resolved
  from phone (fail closed), FTS over name+offer+categories+description through the same
  `expertise_query()` ecom‑synonym expander, browse mode (featured→fresh→claims) when no query,
  3 recent reviews attached per row, **dedupes the app's 12 duplicate‑name pairs** (best record
  per name; the dups themselves = team cleanup in the app). `member_partner_url()` =
  `app.mds.co/partners/{id}` choke point (pattern confirmed by Andy).
- **Router intent `partners`** (+`partner_query`), Plan/Build wiring, company‑vs‑person contrast
  ("tell me about HiveHQ" = partner; "…about Mo Kuhail" = member card). **Gate 84 → 100 checks**
  (non‑public/paused canaries invisible, output allowlist, reviewer‑identity hygiene, anon
  lockout, URL shape). Live‑fired: "any partner deals for tiktok sellers?" → Reacher (5/5,
  offer, app link) + First Media follow‑up.
- **Refresh = the wart:** no `GROUPOS_PAT` ⇒ this snapshot was pulled through the MCP by four
  background agents (~1.4M tokens, one‑time) around the poison records. With a PAT it becomes a
  ~2‑minute curl step in member‑profiles‑sync. **The PAT is now the top infra ask.**
  Refresh runbook: re‑pull via MCP (bracket the poison windows) → `ingest_partners.py --partners`
  / `--reviews` → `--map-categories` → gate green.

## 9 · Open Decisions & Next Steps

> **⚠️ UPDATED 2026‑07‑16 — read §8c/§8d first; items 1–3 below are partly overtaken.**
> Gate 1 done. WA digests are effectively defined as source #1 *by having been built*.
> **The bottleneck is no longer the channel — it's the data.**
>
> **⚠️ 2026‑07‑20: this ranked list is DONE except validation — superseded by the FULL WORKLIST in
> `OLIVIA_NEXT_SESSION.md` (A core · B data platform/content_items · C security & leak prevention ·
> D proactive layer · E waiting-on-Andy). Next big block = `content_items` with sensitivity as data.**
>
> **Ranked, most urgent first:**
> 1. ~~**Forward capture into `wa_messages`** — *active decay*.~~ **✅ SHIPPED 2026‑07‑17 (§8d),
>    running healthy since (freshness tile on tools-health).**
> 2. **Validate the POC** — router, search, links, both greetings: live and largely untested by Andy.
> 3. **Session memory (24h)** — approved, not built. **The router needs history too**, not just the answer —
>    "what about yesterday?" is unroutable without it. Needs **no** privacy call: it's the member's own DM
>    turns, auto‑expiring — *not* the group archive. These were always two different asks sharing one table.
> 4. **Wire Olivia to `wa_messages`** — 10,209 messages and every exact quote sit there unused.
> 5. ~~**Idempotency**~~ **✅ SHIPPED 2026‑07‑17.** New table `digest.olivia_seen` (wamid PK) + two nodes in
>    the workflow: `Log Inbound` → **`Claim Message (dedupe)`** (insert wamid, `ignore-duplicates`,
>    atomic — two simultaneous retries can't both win) → **`Drop Duplicates`** (empty claim = retry → stop;
>    claim *error* passes through = fail‑open, dedupe can never silence Olivia) → `Find Member`.
>    **Proven live:** identical payload fired twice at the production webhook — exec `36406` answered,
>    exec `36407` stopped at the gate (no member lookup, no Claude, no send); 1 claim row despite 2 fires.
>    Status callbacks bypass the gate (verified — Meta's real failed‑delivery callback processed normally).
>    Trade‑off: claim happens *before* the reply, so a crash mid‑processing eats that message (at‑most‑once).
>    Right call for a chat assistant; the member just asks again.
> 6. **Read receipt / "working on it"** — 10s of silence reads as broken.
> 7. ~~**The unified `content_items` index**~~ **✅ SHIPPED 2026‑07‑20 (§8f).** One access‑tagged
>    table, two retrieval functions forever, sensitivity + access enforced in SQL (fail closed),
>    ingest by triggers, behavior verified identical, red‑team leak gate green
>    (`scripts/olivia_leak_gate.py` = the pre‑ship gate for every future source).
> 8. **STOP handling** — required by §9.4 below; currently does nothing.
>
> **Waiting on Andy:** retention window · access‑denied wording ("that's not one of your chats" vs
> act‑like‑it‑doesn't‑exist — today it's an accidental *fallthrough*: she says "I don't have that", which is
> leak‑free but confusing) · **Eugene Khayman's record says "Yevgeniy"**, so Olivia greets him by a name he
> doesn't use — `full_name` is mirror‑owned, so it must be fixed in **Airtable**, and it may be a
> *preferred‑name* gap rather than a typo.
>
> **Loose ends:** old POC `Af2atRScbYSOTYbC` holds a **plaintext Airtable PAT** → delete · 3 orphan Olivia
> fields on Members DB `tblfwOSROSHfuYUxv` (**Airtable's API can't delete fields**) · digest prompt fixes
> (names + staff recaps) spawned separately · greeting costs ~4s because Haiku classifies "hi" ·
> *MDS 2026 New Members* has no invite link and no captured messages.

1. ~~**Data‑layer planning session** (the real next step) — cover all three: canonical source+freshness,
   entitlements, sensitivity — per source. Do NOT start channel work before this.~~ **Partly done for WA by
   building it (§8c/§8d).** Events, revenue, videos, partners, programs remain undefined — and item 7 above
   is the shape they must land in.
2. ~~**Retention / privacy call** — approve storing who‑said‑what per member → unlocks the `wa_messages`
   backfill (Olivia's memory).~~ **Mis‑framed — corrected 2026‑07‑16 (§8d).** The decision was already made
   in this doc; it was never blocked on Andy. **Backfill DONE (10,209 rows).** Only the **retention window**
   is genuinely open.
3. **Access control** — build per‑member gating into the serving layer / `/api/ask` (M10). Blocker.
4. **Positioning / naming (Eugene §5):** introduce as an **AI assistant** (disclosure that it's AI is
   required); **STOP only stops the weekly push, never the agent** (avoid pre‑blocking).
5. ~~**Production channel:** new business Meta account + BSP/provider choice + dedicated number + publish
   + business verification.~~ **✅ DONE 2026‑07‑16 — see §8b.** Real number +1 945‑396‑5415 live, app published,
   business verified, send + real inbound proven. **The channel is no longer the bottleneck.**
6. **Then build:** web agent first (reuse `/api/ask`, personalized per logged‑in member) → WhatsApp last.

---

## 10 · Source docs (Eugene) — incorporated

- **V1 Pilot Sprint Plan** (`~/Downloads/MDS-Olivia-V1-Pilot-Sprint-Plan.docx`) — 5–10 member pilot,
  Coexistence on a warmed number, hand‑curated picks, STOP + human‑pause, "AI assistant" disclosure,
  Airtable Conversation Log + Pilot Picks + system‑prompt skeleton. **Overridden where noted:** channel
  (new Meta number, not Coexistence on the shared number), initiation (member‑initiated), memory store
  (Supabase not Airtable), identity (reuse matcher, no 5th field).
- **V2 Process** (`~/Downloads/PROCESS-V2.md`) — the full‑picture doc: the two sides, the "route to a
  resource" principle, the 8 data sources + "define one at a time," the naming/opt‑out trap, build
  order (Side B first). **Note:** its "this repo with Workflows A/B/C" is Eugene (non‑technical)
  describing what he imagines from the real pieces (digests + video transcripts + the iOS Claude agent) —
  there is no literal Olivia repo; the reactive agent already exists as `mds-ai-bot /api/ask`.

## 11 · Change log

- **2026‑07‑21 (d)** — **Answer‑quality overhaul + SCALABLE multi‑source.** Global **STYLE block**
  (one voice/emoji/formatting/honesty section prepended to all 11 modes — friendly & upbeat, rare
  functional emoji; the single place to tune voice). **`help`, `solve`, `multi` promoted to router
  intents** (regex backstop kept): "what can you do" reliably lists capabilities; problem/advice
  questions ("should I hire X or Y", "what are my options") fan out. **`solve` lane** (partner +
  chats) and **named‑company partner cross‑reference** ("tell me about GETIDA" → 4.9★ deal + the
  chats' skepticism + alternatives, balanced). **`digest.multi_source(p_phone,p_query,p_terms,
  p_city,p_want[])`** — scalable server‑side fan‑out returning {partners,members,events,chats},
  composing the existing GATED functions (gating preserved, fail‑closed); the `multi` lane weaves
  broad launch/expand answers; **adding a source later = one branch here + one Build Prompt block,
  ZERO n8n changes.** **Gate 100 → 111.** Verified: 51‑Q E2E (10/10 after fixes) + 12‑Q multi‑source
  test (flawless — pet/EU/TikTok/Walmart/beauty launches all fanned out; cross‑lane follow‑up
  resolved; guards held; zero leaks/hallucinations). Also: **capability‑list must stay current with
  every new source** (standing rule) · self billing/plan/price/**chapters** (public) · beta dashboard
  (top members, per‑member logs, request context+log‑link to Slack) · **always‑on relay** in front of
  the webhook (Meta callback flipped to it) after an 8.5h dead‑webhook incident + monitor tiles.
- **2026‑07‑21 (c)** — **Beta launched (Eugene's testers) + dashboard beta-ops + self-serve billing/chapters.**
  Real usage: Eugene 31 q, Ian 3, Belén 1–2. Shipped: self subscription/plan/price + join date +
  **public chapters** (`member_billing`, `community_info` chapter counts, `member_card` +chapter;
  gate 100→107); Olivia dashboard = **top-members** list (Andy excluded from all stats) → **focused
  per-member log page** `/admin/olivia/member/{id}` (oldest/newest toggle) replacing the noisy
  360 deep-link; **action-requests now carry conversation context + member-log link** to Slack
  (`olivia_requests.context`, `at_member_id` passthrough). **Display name "MDS Olivia" = APPROVED.**
  **NEW top source request (Andy): a KNOWLEDGE BASE** — CS documentation + resource lists + events/
  community FAQs, to offload the team; lands as `content_items` sensitivity=normal, all-members,
  quote-OK (the easy security case); open question = where the content lives. CU-ticket-per-request
  = wanted, deferred on Andy adding a ClickUp credential in n8n. GROUPOS_PAT parked (Andrii slow) →
  partners refresh stays the weekly manual MCP pull.
- **2026‑07‑21 (b)** — **8.5h dead‑webhook incident → always‑on relay + monitor checks.**
  My deactivate‑first wiring left the workflow OFF 03:32→14:20 UTC; Eugene's 9:30 ET message
  hit Meta 404s and vanished tracelessly (unrecoverable). NEW RULE: edit the ACTIVE workflow,
  then ONE deactivate+reactivate bounce call (~1s). Shipped Andy's protective ask: **relay**
  `digest.mds.co/api/olivia/webhook` (mds‑digest‑web `1a96549`) — Meta's callback now points
  there (Andy flipped it, E2E‑verified incl. organic Meta callbacks); forwards raw to n8n;
  n8n dead ⇒ rate‑limited "upgrading, try again shortly" text (marker =
  `conversation_origin='relay_maintenance'` — status markers get overwritten by delivery
  callbacks within ~1s, observed) + **502 so Meta retries until n8n recovers** (olivia_seen
  dedupes ⇒ late answer, never lost). Health tool: +2 tiles (webhook‑liveness no‑op probe —
  404 = inactive = red; inbound‑silence 12h/24h), feeding tile page + 30‑min Slack monitor.
  Same day: router fix — bare affirmations ("sure") after an offer = followup keeping the
  previous intent, NEVER greeting; offer‑less/TBA partners never lead deals answers;
  partner‑search precision pass (strict‑AND rank bonus + reimbursements/insurance/funding/IP
  synonym groups) after a 17‑question fuzzy bank — gate re‑run 100/100.
- **2026‑07‑21** — **PARTNERS live as source #3 (§8i).** GroupOS app directory → Supa (Andy: Supa
  over live MCP). 486/488 published partners + 922/922 reviews, categories NAMED via AT join
  (97%), `partner_lookup` gated RPC w/ dup‑dedupe + reviews_sample, router intent `partners`,
  **gate 84 → 100**, live‑fired ("tiktok deals" → Reacher + offer + app link). Found + bracketed
  **2 GroupOS API poison records** (any page containing them times out — Andy to report) and
  **12 duplicate partner pairs** in the app directory (team cleanup). Ingest was 4 background
  agents ~1.4M tokens (one‑time, no PAT); **GROUPOS_PAT now the top infra ask** — makes refresh
  a 2‑min curl in member‑profiles‑sync. Mid‑run self‑inflicted outage: the category migration
  revoked EXECUTE on the tsv helper fn → agent upserts died 42501 until re‑granted (lesson:
  generated‑column helper fns need service_role EXECUTE). Tags: exist on partners but empty
  community‑wide; skipped by design.
- **2026‑07‑20 (h)** — **Semantic expertise matching LIVE + two post‑outage automation triages.**
  **`expertise_search(p_phone, query)`** — "who knows PPC / is good at sourcing / can help with
  logistics / who should I talk to about exits". Postgres FTS over members' public free‑text
  (Area of Expertise 623 · About Me 497 · Main Niche 466 · fun fact) with an ecommerce synonym
  expansion (`expertise_query()`: PPC↔advertising↔ads↔Google Ads, sourcing↔supplier↔China,
  logistics↔3PL↔fulfillment, exit↔M&A↔aggregator, …). **No embedding vendor** (Andy: MDS doesn't
  use OpenAI; pgvector/Voyage is the future upgrade). Gated like everything else (asker from
  phone, members‑only, fail‑closed, coarse: name + city/state + public expertise snippet). Router
  intent `expertise` — and "who should I talk to about X" upgraded from chat‑search to expertise
  matching. Live‑verified: PPC→Kyle Dilger/Larry Huang(Amazon PPC)/Aaron Biner; China sourcing→
  Cameron Walker (based in Suzhou); logistics→Monse Lozano/AJ Losey. **Gate 77→84 checks.**
  Also: quota outage (n8n hit its monthly execution cap ~21:00 UTC; Andy upgraded, recovery
  proven) → triaged two broken automations: Platform‑Health‑Slack FIXED (13:00 UTC trigger
  collision — moved 30‑min peek to :15/:45 + retry); Event Registration Sync = dead hardcoded
  OpenAI key since June 23 (enrichment layer, Olivia unaffected) — left alone per Andy.
- **2026‑07‑20 (g)** — **Exposure policy FINAL + the people layer (§8h).** Eugene's ruling landed as
  "public-in-the-app = shareable": who-lists = names again (`event_who` v4) · **`member_card`** (six
  public fields, prose dossier style, junk guards, Staff included) · **`shared_chats`** (asker∩target
  only, gate-enforced) · **`member_dossier`** (own-data dossier for "what do you know about me") ·
  **`community_info`** ("how many members?" → exact) · markdown→WhatsApp bold fix on all routes.
  Live-verified largely on Andy's OWN phone tests (Guido Reyes card + 4 shared chats). Flags: Ian
  Sells's Staff record = test junk (real data on a null-status dup — Members-DB merge for the team).
  **Gate 57 → 77 checks.** ⚠️ n8n: patchNodeField works on jsCode, never on expression fields.
- **2026‑07‑20 (f)** — **Events completed: full history + history-aware recommendations + validation.**
  Ledger horizon removed (1,406 events → 2018; 17,733 registrations; PR #20); Member 360 Events
  section (upcoming + full past, ticket ×N; PR #19); `event_history` RPC feeds MEMBER CONTEXT →
  near-me/trip-planning/own-history answers; 28-question sweep found + fixed 5 routing/prompt
  defects (incl. the missing TODAY date anchor). **Rollup validation (Andy's challenge):** the four
  Members-DB event rollups ride one link with hidden filters — `All` undercounts 953 members, `Last`
  wrong 24%, `Attended` unvalidatable, `Upcoming` 99.3% OK; verdicts STAMPED into the AT field
  descriptions (new standing rule: validate canonical/legacy derived fields against the raw ledger,
  then stamp). Mo Kuhail's "broken" example was actually correct. AT fixes written: 2 admin links →
  member URLs, 2 empty member links filled; `member_event_url()` = the URL-structure choke point
  (custom slugs coming). `community stats`/`how-many-members` gap closed in (g).
- **2026‑07‑20 (e)** — **EVENTS live as source #2 (§8g).** SoT settled with Andy + a Debbie
  huddle: AT Events table = catalog (phases; Registration Open = alive; `Guests?` = audience),
  Event Roster = registration ledger (whole table, never a view — the "roster is dead" read was
  a view artifact, corrected), app/Luma = surfaces; descriptions pullable nowhere (flagged).
  Shipped: `events_catalog` + `event_registrations` + daily sync step (PR #17) ·
  `event_lookup`/`event_who` gated RPCs (admin‑URL sanitization, banded‑event omission, guest
  exclusion, spots‑left) · gate 40→**57 checks** · router `events`/`eventwho` + prompt modes ·
  live‑verified incl. "who is going to the tiktok dinner?" → all 10 members; test rows cleaned.
  Live testing caught + fixed: app's midnight virtual‑call times (AT wall time wins for
  Virtual), bool_and NULL‑token bug (postponed NY dinner was hijacking "tiktok dinner"),
  phrase→token matching, an `/admin/` reg link in AT, backslash‑regex transport mangling (all
  regexes now POSIX classes). Data‑quality flags for the events team: Puerto Rico admin link ·
  Trading call date drift (app Jul 20 vs AT Jul 21) · TikTok dinner Reg Open w/o member link.
- **2026‑07‑20 (d)** — **Service layer + insights day: action lane, chat info, analytics, portal — plus a
  13‑fix hardening loop from live testing.** Andy live‑tested from his phone and I ran autonomous sweeps
  (14 + 45 questions via `scripts/olivia_selftest.py`, replies read from the transcript, test rows always
  cleaned): destination matching (Dallas→Nasir + Texas bench; state normalization fixed TX/Texas/Tx),
  metro awareness (Plano ≠ Houston — LLM curates geography over a 60‑row pool), trait audiences ("DTC
  sellers to invite" = people request), honest‑boundary refusals (never fake ignorance — "his info to
  share, not mine" + redirect), self‑questions get real answers (no card dumps; stored figures never
  shown even to the member), no fake promises anywhere (correction lane copy is now purely factual),
  session‑memory trim 240→500 (she once denied her own words), WhatsApp‑length rule with expand offers.
  **New organs:** `action` intent → `digest.olivia_requests` + Slack #automation‑tests notify + honest
  "passed to the team" ack (E2E‑verified by reading the channel — a silent channel‑name miss was caught
  that way) · `chat_info()` + `chatinfo` intent (requirements/monthly calls/zoom from `digest.chats`;
  zoom only for members of the chat, gated chats hand out verification forms — the sweep's worst finding,
  her denying the Large SKU requirement, is dead) · question‑topic analytics
  (`scripts/olivia_question_report.py` → `olivia_question_topics`; location/networking = #1 real topic) ·
  **portal `/admin/olivia`** (PRs #14+#15, Overview design language: period picker, delta cards, trend,
  topics snapshot, requests queue with status editing). Leak gate now **40 checks**. Ops: member_profiles
  `synced_at` trigger‑stamped (stale‑badge bug was stamps, not data) · sync cron 13:30→**13:47 UTC**
  (PR #16 — congested GH slot never fired). **Next session: EVENTS as source #2** (see
  `OLIVIA_NEXT_SESSION.md` — SoT identification first, attendance‑exposure ruling from Andy, gate before
  prompt).
- **2026‑07‑20 (c)** — **Applications LIVE under MATCH‑DON'T‑QUOTE — persona cards, member matching, chat recommendations; gate now 32 checks, green.** Andy's rulings: all member data = matching fuel by default, classification controls only what surfaces; yes/no bisection refused structurally (no per‑person attribute operation exists — `member_match` takes only the asker and returns names + coarse reasons); match fuel pre‑coarsened (`member_attributes`: rev_band/under_30/categories/channel_mix… — exact revenue and birthdate never leave `member_profiles`). Shipped: `APPLICATION_SOURCE_CLASSIFICATION.md` (197 fields classified, default‑deny whitelist, approved) · `MEMBER_ATTRIBUTES_SOURCE_MAP.md` (Members‑table‑first per field — the 291‑vs‑711 City lesson) · channel requirements from Andy's sheet loaded into `digest.chats` (5 verification‑gated) · `member_attributes` (5,706, trigger‑refreshed) · owner‑gated persona cards (5,706) + application answers (746) in `content_items` with the new `{"type":"owner"}` rule · `member_match()` + `chat_recommendations()` (non‑qualifying gated chats OMITTED — a "you don't qualify" row would leak the band) · Olivia router +3 intents (match/chats/profile), live‑verified on all routes incl. a byte‑identical digest regression. Gaps: TikTok recs off until its verification form syncs; Real Estate describe‑only (no data field); semantic free‑text matching = next matcher layer.
- **2026‑07‑20 (b)** — **`content_items` unified index LIVE (§8f) — worklist B shipped with C built in.**
  `digest.content_items` (access_rule jsonb + sensitivity enum as DATA, RLS from birth) · ingest =
  triggers on `summaries`/`wa_messages` + exact backfill (1,276 + 10,429) · retrieval = the two
  functions `content_search`/`content_lookup` (member resolved server‑side from phone, fail closed;
  never_surface never returned; restricted needs an explicit flag; unknown access‑rule type denied;
  `sender_phone` never emitted; anon revoked) · Olivia rewired to the RPCs (5 nodes), behavior
  verified identical before/after (SQL diffs + live exec diffs, verbatim reply byte‑identical);
  the digest search's filter‑after‑fetch is dead — entitled‑only rows now fill the cap. Red‑team
  leak gate `scripts/olivia_leak_gate.py` (18 checks) green = the pre‑ship gate for every future
  source; equivalence harness `scripts/verify_content_items_equivalence.py` green. No new sources
  ingested — applications/events/videos still wait on Andy, each gated on the leak suite.
- **2026‑07‑19/20** — **POC v3: raw search + session memory + reset + STOP + typing (workflow now 36
  nodes, renamed "…v3").** Specific questions search `wa_messages` (all history, entitlement enforced
  at‑query, sender names via phone join) alongside digests — quotes are ground truth. Router sees the
  member's last 24h of turns and resolves follow‑ups into standalone queries (default = fresh unless the
  message can't stand alone); "new question"/"next question"/"reset" wipe context deterministically.
  STOP/START on `members.olivia_optout_at` (ack tells members login codes still arrive; muted = total
  silence); every inbound gets mark‑read + typing (gated off for opted‑out). `Save Conversation` moved
  after the send and now stores the sent wamid → per‑turn delivery badges work. **E2E verified via
  transcript + executions; delivery of simulated‑inbound tests fails by design (131047 — fake webhooks
  don't open Meta's 24h window; real member messages do).** Also: 6‑tile Olivia section on tools‑health
  (agent, Meta token+quality, delivery, raw‑capture freshness, AT‑sync freshness, engagement sync) feeding
  the Slack monitor; `member_profiles` daily GitHub‑Action sync armed (first run success 2026‑07‑20).
  **Andy's rulings:** Eugene's consultant deck is NOT a spec ("not devs" — never align the build to it);
  sensitivity gates become a first‑class workstream ("who is around you: fine — exact addresses: never"),
  enforced as data in the coming `content_items` index. Full worklist lives in `OLIVIA_NEXT_SESSION.md`.
- **2026‑07‑17 (b)** — **Webhook idempotency SHIPPED (§9.5).** `digest.olivia_seen` + atomic claim‑then‑process
  in `12wj6h1TWqb0d4Dq` (31 nodes now). Meta retries no longer produce duplicate replies or double Claude
  spend. Proven by firing the same payload twice at the live webhook: second fire stopped at the gate.
  Fail‑open on claim errors. Also: **Andy confirmed the prompt stays hardcoded in n8n** — Airtable's
  `system_prompt`/`user_prompt`/`prompt_version` fields are provenance stamps, not controls (nothing reads
  them back; all 1,105 daily rows carry identical v5 text). Raw‑data audit: Supabase `wa_messages` = exactly
  what Airtable holds (10,209 = 10,209, id‑level diff, 0 missing either way); **366 text messages on 10 busy
  days were lost at write time by the 95K slice** (9 of 10 days = AI & Automations) — recoverable only via
  Whapi re‑fetch or nameless `raw_log`. The doc's earlier "nothing was lost" claim was wrong and is hereby
  corrected: the salvage recovered everything *the sliced field still contained*, not everything.
- **2026‑07‑17** — **Forward capture SHIPPED — `wa_messages` is no longer a decaying snapshot (§8d).**
  Digest `qo3qzeVtprhTW88F`: `Prep Claude Request` now builds unsliced per‑message rows; new node
  `Save WA Messages (Supabase)` upserts them to `digest.wa_messages` on the Whapi message id. The 95K slice
  was **not** ported — it stays on the Airtable write, the only place that needs it. Airtable keeps its copy
  as a human view and a recovery backstop, but **Supabase is now the system of record for raw messages.**
  Proven before going live by replaying the patched code against real exec `35803`: **44/44 rows identical to
  the backfill, 0 divergence**; empty‑array, NULL‑FK and expression‑binding cases each verified against the
  live table; nothing new written by any test. Windows tile with no gap. **Confirm the 7am ET run.**
- **2026‑07‑16 (late)** — **Real members using it + portal login moved to WhatsApp (§8e).**
  **Ian Sells and Eugene Khayman both reached Olivia via the member‑initiated link and got real answers** —
  Eugene's "who should I talk to about selling in Target?" surfaced threads from **16 Jun and 30 Apr** with
  names + links, which the old 7‑day window would have missed entirely; asked to rank "the smartest person on
  AI", she **refused to invent a list**. **The cold template to Ian FAILED (131049)** — Meta suppresses
  marketing to non‑engaged users — while **the link worked twice, unprompted**. That settles the doc's
  member‑initiated decision empirically: cold marketing is not slower, it is *actively blocked*.
  Built: **delivery-status capture** (`digest.olivia_sends` — we were blind to failures and I wrongly told
  Andy Ian's message delivered, reading a lagging dashboard over the per-message event sitting in our own
  webhook), **conversation history** (`digest.olivia_messages`, both turns + route), **engagement counters**
  synced daily to **WA DB Members**, first-contact always gets the intro. **Portal OTP now on WhatsApp**
  (PR #7 merged), Twilio out, plus a silent login bug fixed (US numbers were becoming Russian ones).
  ⚠️ Logged the **one-number coupling** risk (§8e): STOP on Olivia would also kill a member's login codes.
- **2026‑07‑16 (later)** — **Olivia POC v2 LIVE (§8c) + `wa_messages` backfilled (§8d).**
  Dropped `/api/ask` (stale video library would poison answers) → **WA digests only**, the one clean source.
  Haiku router + deterministic plan; **stored digests pulled verbatim, no tokens**; monthly generated;
  **topic questions search all 2.5 months** (proved: "fable" = 26 digests all‑time vs **5** in the old 7‑day
  window — it was silently missing 81% *and* using more context). Entitlements on `channels_present`
  throughout. `digest.chats` (links, SoT). Engagement counted in Supabase → synced daily to **WA DB Members**
  by `BfLqFlwzBBe0LgMy`. `olivia_intro` template APPROVED, sent to **Ian Sells**.
  **`wa_messages` 0 → 10,209** (Apr 23→today); truncation verified as **0.9%** and **fully recovered**
  (1,178 messages salvaged; `raw_log` was never truncated).
  **Corrected the record:** who‑said‑what was never blocked on Andy — the doc had already decided it.
  **Left undone and decaying: nothing writes `wa_messages` going forward.**
- **2026‑07‑16** — **Production channel LIVE (§8b).** Real number +1 945‑396‑5415 on WABA `1575708577606583`,
  app "MDS Community" `955961257089837` published, business verification complete (took **one day**, not weeks).
  All 4 channel ACs closed: send (exec `36007`) + **real typed inbound** (exec `36019`). New standalone n8n
  workflow `12wj6h1TWqb0d4Dq` (logs inbound only, no agent). Documented the **four‑part receive chain**
  (verify → publish → `subscribed_apps` → `messages` field) — the two silent failures were #3 and #4.
  Corrected §8's dev‑mode claim back to the original (pessimistic) reading: it was right.
  Gate 1 done; **gate 2 (M10) and gate 3 (data layer) untouched — the data layer is now the bottleneck.**
- **2026‑07‑13** — Doc created. Locked all decisions from the working session (channel, initiation,
  build order, data layer, speed, model, identity/memory/privacy). Meta send + real `/api/ask` agent
  POC proven end‑to‑end (throwaway account). Incorporated Eugene's V1 + V2 docs.
