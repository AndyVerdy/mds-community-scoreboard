# Millie web front door + Public mode — design

**Ticket:** #169 · **Repos:** `mds-digest-web` (page, API route, table reads) + the Olivia n8n workflow (new
entry branch, Public gate) documented in this repo · **Status:** design approved in conversation 2026-09-07, spec
awaiting Andy's read.

## Goal

Give staff a real chat with Millie inside the admin portal — the answer comes back in the same request, under
the name of the person who asked — and add a **Public** mode whose answers may be published outside MDS:
generated from everything we hold, but naming a person only when a public source backs the name, with notes on
where each part came from.

## Why (what exists today, and what is wrong with it)

`/admin/millie/chat` (#168) is the retired `/admin/olivia/test` page put back. It works like this:

1. The page POSTs to `/api/olivia/test-chat`, which builds a **fake WhatsApp inbound from Andy's phone**
   (`PROBE_PHONE`, wamid prefixed `SELFTEST` so the workflow takes the silent path and never sends via Meta).
2. n8n answers `200` at once and does the work in the background.
3. The page **polls** `GET /api/olivia/test-chat?after=<id>` every 2.5 s for up to 120 s until the reply appears
   in `digest.olivia_messages`.

Consequences: every staff member asks **as Andy**; every turn lands in **Andy's real WhatsApp thread** as
context; replies arrive by polling; there is no notion of "who asked" or "which mode". Andy, 2026-09-07: "I'm
pretty sure it's a shitty chat that checks the answer every second after the request is sent. That's not how
chats are supposed to work." Confirmed from the code.

`/api/olivia/ask` (the iOS knowledge-base test endpoint) is the same pipe collapsed into one request and has the
same two flaws (probe identity, polling inside the request). It is untouched by this design and can be moved to
the new door later.

## Decisions (Andy, 2026-09-07, verbatim where quoted)

| # | Decision | Words |
|---|---|---|
| D1 | Build a web entrance of its own instead of keeping the WhatsApp disguise | "Own front door. Ideally if we can minimize cost somehow on ai" |
| D2 | Team mode = **everything**, all three internal categories included (exact revenue, contacts, Stripe/billing), behind a large disclaimer — **later ticket**, not this slice | "I need team mode to include all categories - everything. That's why we need a huge disclaimer. But for now, let's focus on the public answer, since it's a faster win." |
| D3 | Public answers may name a person **only when a public source backs the name** | "second one, only from public sources" |
| D4 | The chat itself is rebuilt "the right way" = synchronous reply, own conversation store, real asker; no chat platform, no polling | "Do we need to build our own chat system in right way?" → yes, as the front door |
| D5 | Order: door → Public → tabs/tile → Team (later) | agreed in conversation |

## Architecture

### The door (n8n)

A new webhook entry on the Olivia workflow, **`olivia-web`** (staging + prod copies, same as `olivia-wa-*`),
reachable only from the admin API: the request carries a shared secret header (`OLIVIA_WEB_SECRET`, Render env +
n8n credential); any call without it is dropped before the first node does work.

Payload: `{ asker_email, mode: "test" | "public" | "team", target: "staging" | "prod", text, thread_id? }`.

The branch:

1. **Web Auth + Parse** — verify the secret, normalise the payload, stamp `channel = "web"`.
2. **Resolve Asker (web)** — the asker is a **staff email** (`@mds.co`, same rule as the admin gate); no member
   lookup, no phone. The retrieval principal is set per mode (see *Retrieval identity*).
3. **Prep Context** — last 24 h of turns for `(asker_email, mode, thread_id)` from the new web table (not
   `olivia_messages`).
4. Then the **existing** nodes, unchanged: Route Request (Haiku) → Plan Request → Embed → zeroth fetch →
   Verbatim? → the Answer loop (Sonnet, 29 gated tools, ≤ 5 rounds) → Claims? → Fact Check → Gate Verdict →
   link gate.
5. **Public Gate** — Public mode only (below).
6. **Format (web)** — markdown kept as markdown; no WhatsApp formatting, no `[SEND_IMAGE:]` markers, no billing
   nudge, no interactive follow-ups.
7. **Save (web)** → **Respond to Webhook** with `{ answer_md, notes[], sources[], mode, latency_ms, cost_usd,
   thread_id, turn_id }` in the same request.

The WhatsApp branch is not modified. `Answer Parse` keeps injecting the principal server-side; the tool schemas
still carry no phone parameter the model could set.

### Retrieval identity (interim, until Team mode)

Public mode must draw on **everything we hold** (Andy). The gated RPCs resolve access from a member principal,
and staff have none. Until D2's everything-access SQL exists, the retrieval principal for Public (and for Test)
is the **probe member identity** — the widest structural access we have today, the same one the current chat
uses. What changes is the output: the Public Gate, not the retrieval. When Team mode lands, Public switches to
the team principal and the three internal categories enter retrieval, still filtered by the same public-source
rule on the way out.

Stated plainly for the record: in this slice a Public answer can draw on what Andy can see, not on exact
revenue, contacts or billing. Those arrive with Team mode.

### Public Gate (mechanical first, model second)

Every evidence row a tool returns already carries its access classification (`access_rule`: `public`,
`chat_member`, `fb_group`, `owner`; `sensitivity`). The Answer Merge nodes keep the evidence of the turn; the
Public Gate reads it.

1. **Deterministic name pass.** Collect every member name (and alias) from `digest.members` /
   `digest.member_attributes` / `speakers` that appears in the draft. For each, look for a **public** evidence
   row from this turn that contains the name: `access_rule = 'public'` and `sensitivity = 'normal'` — public
   event pages, the partner directory, speakers on **public** videos, a fact the member posted on a public MDS
   page. **The MDS Facebook group is private** (`fb_group`) and counts as closed. A name with no public backing
   is replaced with a role phrase ("a member", "a seller in the community", "one of the speakers"), in every
   occurrence, before any model sees the text.
2. **Haiku smoothing + notes.** One call on the redacted draft with the per-claim source classes: fix grammar
   broken by the replacements, never add facts, and produce `notes[]` — one line per claim group stating the
   source class in plain words: *"from a closed WhatsApp chat, paraphrased, no names"*, *"from a call
   recording, paraphrased"*, *"public: MDS Summit schedule page"*. `sources[]` lists the public URLs that survive
   the link gate.
3. **Verification.** A second deterministic pass re-scans the smoothed text: any unbacked member name still
   present fails the turn closed — the response is an honest *"I could not produce a public-safe version of this
   answer"* with the notes, never the unredacted text.

Quoted revenue figures, contact details and anything the existing rulebook (`OLIVIA_SHAREABLE_FIELDS.md`)
forbids stay forbidden — the Public Gate only ever narrows.

### Data

New table **`digest.olivia_web_messages`** (service_role only, RLS on, no policies):
`id, thread_id, asker_email, mode, target, role (user|assistant), text, answer_md, notes jsonb, sources jsonb,
evidence_classes jsonb, plan jsonb, latency_ms, cost_usd, model, created_at`. Additive migration, exported to
`db/`. Never `olivia_messages` (that table is keyed by phone and feeds the daily review of real member
conversations).

### API (mds-digest-web)

`POST /api/admin/millie/chat` — staff session required (`isStaffEmail`), body `{ mode, target, text, thread_id? }`;
the server adds `asker_email` from the cookie and the shared secret, calls `olivia-web`, stores nothing itself
(the workflow saves), returns the workflow's response. `maxDuration` 90 s (answers measured ~27 s; the fact gate
regeneration can double that). `GET /api/admin/millie/chat?thread_id=` — the thread's turns from the web table.
Anonymous: 403. The old `/api/olivia/test-chat` stays for the Test tab until the door proves itself, then Test
moves onto the door too and the old route is retired.

### Page

`/admin/millie/chat` (inside the Millie tool, #168) gains **mode tabs**: **Test** (today's member view), **Public**,
and later **Team** (rendered disabled with "coming" until D2 ships). Staging/prod stays a small switch in the
header. A turn shows: the question, the answer, a "working" state while the request is open (no polling), and
for Public the **notes** block under the answer plus a **Copy** button (answer + notes). Errors are sentences,
never internals. Styling: the kit's tokens; the legacy `OliviaTestChat` component is replaced, not wrapped.

### Cost

Today's answer: ≈ $0.021 (Sonnet loop, prompt-cached; Haiku router + fact check). Public adds one Haiku call on a
short draft: ≈ +$0.002. Nothing else is added; the deterministic passes are free. Reusing the loop is the whole
cost strategy — a second implementation would cost the same and drift.

### Safety, and what the leak gate must prove

- `olivia-web` without the secret → dropped, no model call (probe: 401/403 and no `olivia_web_messages` row).
- A web turn never reaches `Send Reply (Meta)`, never writes `olivia_messages`, never touches `olivia_seen`.
- Public Gate: a fixture turn whose evidence contains a closed-chat name and a public-page name yields a text
  with the second name and without the first, and the notes mention the closed source.
- Fail-closed: force a leftover name past the smoothing step → the turn returns the refusal text.
- The tool schemas still carry no principal parameter; `Answer Parse` injection unchanged (existing check).
- Staff-only: anonymous and member sessions get 403 on the admin route.

These become `olivia_leak_gate.py` checks and ship green before promote (non-negotiable per `CLAUDE.md`).

## Rollout

1. Table + migration + `db/` export. 2. Workflow branch on **staging** under the `olivia_wf.py` lock; probes on
staging; gate green; hand back the lock. 3. Admin route + page on a branch; local proof with a staff cookie
(never the QA login route with a real member). 4. Promote the workflow (Andy's word), merge the web branch
(= Render deploy). 5. Move the Test tab onto the door; retire `/api/olivia/test-chat`.

## Acceptance (the story's bar)

1. A staff member types a question in Public mode and gets the answer in the same request, no polling, with
   notes and a Copy button; the turn is stored under their email, not Andy's phone, and nothing appears in
   WhatsApp or `olivia_messages`.
2. On a question whose evidence mixes a closed chat and a public page, the answer names only the publicly
   backed person, and the notes say what was paraphrased and from where.
3. A forced leftover name fails closed with the refusal text.
4. Gate green with the new checks; before/after: polling requests per answer ~10–48 → 1; turns in Andy's
   WhatsApp thread per staff question 2 → 0.

## Out of scope (this slice)

Team mode and its everything-access SQL + disclaimer (D2, own ticket) · the Facebook "answer this post"
popup (Andy's design pending) · moving `/api/olivia/ask` (iOS) onto the door · restyling beyond the chat page ·
publishing anywhere from the page.

## Plan deviations (recorded when the plan was written, 2026-09-07)

Plan: `docs/superpowers/plans/2026-09-07-millie-web-front-door-public-mode.md`. Three small departures from the
text above, each chosen to reuse the existing chain instead of duplicating it:

- The web table stores `metrics jsonb` (the answer loop's token counts) instead of a `cost_usd` column; the
  ≈ $0.023 figure stays the estimate, computed from the counts when anyone needs dollars.
- A web turn passes through `Claim Message (dedupe)` like every other turn and therefore writes one
  `olivia_seen` row (unique wamid, harmless). The gate clause "never touches `olivia_seen`" is dropped; the two
  that matter stay: never `Send Reply (Meta)`, never `olivia_messages`.
- `Mark Read + Typing` still fires on the probe phone for web turns, exactly as the current test chat does.

## Open questions

None blocking. Two to confirm at plan time: the exact role phrases used for redacted names (proposed above) and
whether Public answers should be saved as candidates for later publishing (a `published_at` column is cheap to
add now, empty until item 4).
