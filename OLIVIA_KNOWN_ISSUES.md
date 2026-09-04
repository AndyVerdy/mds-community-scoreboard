# Olivia — Known issues (the standing list)

**What this is:** the curated overview of everything known to be wrong, missing or structurally weak
in Millie, in one place, in priority order. `OLIVIA_SPRINT_4.md` stays the ticket truth (stories,
ACs, evidence); this page is the map across it. ClickUp page `19 · Known issues` of doc
`2531q-103317` is the generated copy — rewrite it from this file when this file changes.
**Last rebuilt: 2026-09-04** (with the handbook re-verification of the same day).

---

## 1. Architecture and structure — the program, in order

The external architecture review (2026-09-02) found two things: logic lives in several places
including the database, and most tables are not connected. Items 1–3 are those findings; 4–6 are
the runtime consolidation that #64 carried as bullets; 7–8 the data layer; 9–11 hardening.
**NEW** = to be split out of #64 and filed on Andy's "file".

| # | Work package | Ticket | Story | Scope | Status |
|---|---|---|---|---|---|
| 1 | **Runtime inventory** | #64 (the deliverable only) | As the owner, I can name where any piece of MDS logic runs and why. | One table — job · runtime · trigger · why-here · owner · what breaks if it stops — across Postgres, n8n, Make, Render, GitHub Actions, the Mac. Drives 3–6. | Open, S1. The 2026-09-02 estate survey is the raw material (n8n 68 workflows, Make 171/68 active, launchd 9, GH 2, Render cron 1, 33 Render routes). |
| 2 | **Decisions out of SQL** (data ≠ logic) | NEW (from the #64 amendment of 2026-09-02) | No decision rule has two definitions. | Classify the 116 `digest` functions as read vs decision; each decision (active status, "restricted for this asker", time decay, disclosure, matching policy, "is registered") moves into the Render route that owns its lane; the RPC shrinks to a plain read; every moved lane carries unit tests + a bank re-run; the handbook lists where every rule lives. Retrieval, gating and stats STAY in Postgres. | First slice #147 (one definition of "registered"), second the #125 status rule. |
| 3 | **Schema integrity** | #158 + #61 remainder + #121 | Every row about a member points at one member record the database enforces; a broken join shows on the health card within a day. | Declared spine `member_profiles.at_member_id`; FKs on the 20 owned tables (RESTRICT on ledgers, never CASCADE on a mirror); mirrors documented FK-free; the wrong key on `olivia_messages.member` (audit §5.1) retired; nightly orphan check + heartbeat + tile; the ERD and table COMMENTs; `db/` covering the `event` schema. | #158 open S2 (Andy "go") · #61 remainder open · #121 open S3. Live: 75 tables, 17 with any FK. |
| 4 | **Nothing runs on the Mac** | NEW (#64 item 2) | Nothing business-critical depends on a laptop being awake. | Move the six Olivia launchd jobs, the persona refresh and the Sunday Claude task to a server — one scheduler class per job (pg_cron for in-DB alarms, Render cron for scripts, n8n for webhook-adjacent); the watchdog re-homed outside Supabase and off the laptop; the GroupOS refresh needs a `GROUPOS_PAT` to stop being a Claude session; the Facebook extension is the accepted exception. Each move proven by a live run, old path disabled the same session. | Not started. 8 plists exist in no repo. |
| 5 | **One web host per app** | NEW (#64 item 3) | One codebase, one host, one deploy story, one env-var story. | mds-digest-web stays on Render (verified origin); retire any Vercel deployment of it; inventory what Vercel still runs (Skill Base, the Centurion verifier, the email CNAME) and move or document each. | Not started; premise partly stale (Vercel runs nothing of Millie's). |
| 6 | **One automation home (Make → n8n)** | NEW (#64 item 1, corrected) | One creation path for a member row. | Make runs the membership/billing core (68 active scenarios), not "two Typeform syncs"; three carriers can CREATE a member row; the chapter-intro scenario `4717952` is OFF since June. Inventory, then migrate in order, starting with the two Typeform syncs that carry the #63 injection. | Not started; system map 2026-09-02 is the evidence. |
| 7 | **Every mirror reconciles and shows its age** | #148 + the mirror rule | Never answered out of a record we stopped being able to check. | `stale_since` on the WA members mirror (12 rows frozen since 2026-08-05), front door and lanes skip stale rows, the pulse reports the count; the same freshness + gate-check pattern on every mirror (chats #90, partners/events vectors #159, videos, members). | #148 open S3. |
| 8 | **Forms warehouse as one source of truth** | #68 + #66 + #73 | Any concept the community answers about reads as ONE field whatever form or year; adding a form creates no mapping debt. | Pin the existing dictionary (`form_concept`), retire `form_field_map`; the `form_reach` chokepoint view (the scope wall is repeated in five functions); validation at write (flag, never drop); incremental matview; then the 156 forms she does not read. | All open S1; plan `docs/superpowers/plans/2026-08-08-canonical-question-dictionary-v2.md`. |
| 9 | **Observability** | #72 + #32 + the alarm lag | 100 members at once get a normal answer in a normal time, and every answer has a cost and a latency. | `latency_ms` telemetry first (NULL on every row), then the load test (n8n concurrency, the holding ladder's feedback loop), tokens per answer persisted, spike + balance alarms, the outage alarm's 69-minute lag fixed. | #72 open S1 never run · #32 open · lag unfiled. |
| 10 | **The relay verifies Meta's signature** | #105 | No forged inbound reaches the front door. | `X-Hub-Signature-256` on every inbound at the relay. | Open S2; before any wide intros announcement. |
| 11 | **The finder absorbs the remaining lanes** | #116 | One lane, one tree, one disclosure engine for people, content, videos, events, partners. | Phases 2/3 of the finder; retires `member_match`, `member_count` and the schedule matcher. | Open S2, size L, own plan. |

---

## 2. Open defects and gaps on the board (2026-09-04)

**Answer quality — the bank C residue** (602 organic questions: 466/511 correct after the fix
loop; what is left is ticketed):
- **#139** 🔴 a named partner ships with its recorded offer and its page (5 fails) · **#140** 🔴 a
  refusal names the REAL gate — no invented policy, no false capability denial (6) · **#141** 🟡
  "not on file" when it is on file (3) · **#142** 🟡 the gate's hard-stop clamp answers real
  questions with a canned line (3; deliberately untouched) · **#143** 🟡 a follow-up binds to the
  wrong thing or loses the thread (3) · **#144** 🔴 2027 events answered wrong — blocked on #123 ·
  **#124** 🔴 the bank C epic itself (open until the residue closes).
- **#155** 🟡 a chat quote carries its own message link, and "what should I know" is not a
  capability tour (the #138 split) · **#111** 🟡 who-to-meet results swing with the model's
  free-text topic query · **#118** 🟡 `op=people` returns a ranked subset, not a roster, for a
  plain "who is coming" · **#71** 🔵 "virtual event" vs "call" vs "recording" — two contradicting
  "latest" answers · **#14** conversational, not robotic.
- The nightly eval reads **10.9% fail (24 of 220) on 2026-09-04** against the <1% target; worst
  classes `false_denial` and `wrong_fact`.

**Routing and lanes:**
- **#123** 🟡 `event_lookup` never reaches the events catalog — every `event_*` call is sent to
  the schedule endpoint (filed from the #108 review; #144 waits on it).
- **#92** 🟡 event selection for a multi-event world — waits for event #2's export.
- **#116** 🟡 finder phases 2/3 · **#18** 🟡 how-MDS-works answers, open for more team docs.

**Data layer:**
- **#147** 🔴 PAUSED — registration status answered by two sources that disagree (36 members);
  half the fix is live; the authority shape is Andy's call.
- **#148** 🟡 the WA members mirror never reconciles · **#115** 🟡 country/state and business-model
  hygiene (`country_fold` at derive time, 8 corrupt rows, 4 non-current "resellers") · **#74** 🟡
  51% of form submissions belong to nobody · **#67** 🟡 cohort + trend comparison per field ·
  **#73** 🔴 she reads 5 of 161 forms · **#66** / **#68** 🔴 forms warehouse gaps + the dictionary.
- **#120** 🟡 loader hardening after the #113 refresh · **#121** 🟡 `db/` does not cover the
  `event` schema · **#122** 🟢 "Explore Singapore" is four daily copies.
- **#17** 🔵 auto-refresh videos and partners (needs a `GROUPOS_PAT`) · **#35** ⚪ documents as a
  source (GroupOS) · **#36** 🚀 Circleback as a source · **#48** ⚪ Airtable roster write-back ·
  **#19** ⚪ privacy: share, keep, delete.
- Unfiled: **re-chunk the oversized transcript rows** — 1,423 chunks over 4,000 chars, 581 in
  restricted videos (found 2026-08-27; the producer is fixed, the rows are not).

**Channel and Meta:**
- **#105** 🟡 webhook signature not verified · **#110** 🟡 intro-tap turns are not saved to
  conversation history · **#109** closed, but delivery of a requester notice through a CLOSED
  window has not been observed live · the **display name** still reads "MDS AI Assistant" ("MDS
  Mille" pending since 2026-08-19 blocks "MDS Millie") · **Side A** needs a transactional v4
  template (the videos wave lost 50 of 94 to marketing caps) · **#146** remainders: hidden-number
  history keyed by the opaque id; a first contact from a hidden number still needs a human pairing.
- A by-name intro ask outside the Summit gets the stale Summit picker (2026-09-02, unfiled).

**Operations and the quality process:**
- **#72** 🔴 load test never run · **#32** cost per answer not instrumented · **#152** 🟡
  `refresh_entity_dossiers` statement timeout — fixed in the 2026-09-02 triage (900s ceiling), ticket
  not closed · **#117** 🟡 `olivia_selftest.py --cleanup` leaves probe message rows · **#119** 🟡
  bank B (the regression net for everything after 08-16) still being written · **#34** the QA doc
  set · **#157** 🟡 the vendor call on the Sonnet-vs-Terra bench · **#61** / **#64** / **#158** (§1).
- `prod_pulse.py` cries wolf on a stale baseline (re-save per tier) · the ClickUp handbook copy
  regenerates by hand only · the July POC workflow `Af2atRScbYSOTYbC` and the display-name watcher
  `a1ViYr5FT7iePdN9` are still active (by design; retire when done).

---

## 3. Found alongside, not yet filed

| Found | Where / when | What it is |
|---|---|---|
| The alarm's lag | 2026-09-02 outage | `olivia-health` fired 69 minutes after the first failed answer. Threshold or window is too loose for a total outage. |
| Service topics missing from the taxonomy | #160, 2026-09-03 | The 51-topic ledger has no Accounting / Tax / Legal topics, so a bookkeeping partner's strengths read as marketplaces. |
| Founder ↔ partner mention matching | #160, 2026-09-03 | `fb_partner_mentions` matches on the partner NAME only — 22 "Mudit" comments never reach Prosperlytics. |
| Complaints never reach a recommendation | #160, 2026-09-03 | A partner's `weak_signal` comes from directory star ratings only (<3.5); FB/WA complaints are invisible to ranking. |
| 100 partner sites unreadable | #160, 2026-09-03 | 71 unreachable + 29 JS-only sites got no web profile; a browser-based fallback would cover most. |
| Eight partner links land on forms | #160, 2026-09-03 | Tracking links resolve to Typeform/Airtable/Calendly pages, not the partner (New Amazon Account, VAA Philippines, Buy with Prime, Graphic Rhythm …) — GroupOS-side fix. |
| Two Prosperlytics rows in the directory | #160, 2026-09-03 | `651f9c…` (5 reviews) vs `6763ad…` — directory hygiene, GroupOS-side. |
| The Make premise in #64 is wrong | System map, 2026-09-02 | Make runs the membership/billing core; three carriers can CREATE a member row; chapter-intro `4717952` OFF since June (item 6 of §1). |
| 8 launchd plists exist in no repo | #64, 2026-08-08 | Same single-copy risk #65 fixed for SQL, one layer up (item 4 of §1). |
| 8 actives have no GroupOS account · 5 sweep emails resolve to nobody | Entitlement sweep, 2026-09-03 | They get no video grants at all; the five emails are listed in the 2026-09-03 log entry. |
| 38 of the 2023 event recordings are visible to one admin account only | Entitlement sweep, 2026-09-03 | If members should see them, that is a GroupOS-side rule change. |
| 16 Summit videos read `public` in GroupOS · 7 metadata-only videos await re-embed | 2026-08-28 | Andy's desk. |
| The Sunday 30 Aug scheduled video task left no trace | Health triage, 2026-09-02 | Cause unknown; the 06 Sep run must write a dump or the 11-page fetch is done by hand. |
| GitHub starts the 13:47 UTC cron 3.5–6 h late | Health triage, 2026-09-02 | Deadline widened; consider n8n `workflow_dispatch`. |

---

## 4. Waiting on Andy (decisions, not work)

1. **#147** — the registration authority shape (recommended: one function, two facets).
2. The 16 Summit videos still `public` in GroupOS, and the 7 metadata-only re-embeds.
3. A transactional v4 template for the 50 members the videos wave never reached.
4. **#157** — stay on Claude, port the loop to OpenAI, or re-test.
5. Rotate the OpenAI key pasted into chat on 2026-09-02.
6. "MDS Millie" at Meta when the pending review's verdict arrives (watcher armed).
7. "File" for §1 items 2, 4, 5, 6 — they go on the board with story + ACs and #64 is cut to item 1.

---

## 5. How this page is maintained

Rebuild it whenever a ticket in §1–§2 closes or a §3 finding is filed; stamp the date at the top;
rewrite ClickUp page 19 from it in the same session. The board keeps the evidence; this page keeps
the shape.
