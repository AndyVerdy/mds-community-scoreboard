> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Start every session by invoking `/caveman`.** It is the default output mode — governs style, never content.
- **Working a task, invoke `/using-superpowers` first.** The relevant skill goes BEFORE any action — even clarifying questions, exploring, or reading files. Process skills lead (brainstorming · systematic-debugging), implementation follows; announce it and follow it exactly.
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
| **#61** | 🏗️ Schema audit: tables with no declared connections *(research + orphan audit + COMMENTs SHIPPED 2026-08-12; FK-constraint follow-up filed)* | 🔴 S1 | M | n/a (SQL) | ✅ audit shipped |
| **#64** | 🏗️ Runtime inventory: where every job runs — failure mode is silence | 🔴 S1 | M | — | — |
| **#66** | Forms warehouse: 4 remaining gaps (validation · refresh · units · lag) | 🔴 S1 | M | — | — |
| **#72** | 🚦 LOAD TEST — **NOW the announcement, not the Mille demo. Biggest open risk; never run** | 🔴 S1 | M | — | — |
| **#73** | Connect the useful forms to Olivia — she reads 5 of 161 | 🔴 S1 | M | — | — |
| **#68** | 🔑 Canonical question dictionary + mapping at scale | 🔴 S1 | L | — | — |
| **#18** | How-MDS-works answers | 🟡 S2 | M | ✅ first slice proven `6581548e` | ✅ **first slice LIVE** `f3850dd7` (prod probes: FAQ cited; no-doc honest) — open for more docs |
| **#94** | 🧠 Expertise Ledger v2 — the living skill sheet (Eugene #2 finale) | 🔴 S1 | M | — | 📋 **PLANNED** — plan approved, execution-mode pick pending |
| **#95** | Equalizer for the members lane (`member_match`) — Eugene's "Moe ×12" lived here | 🔴 S1 | S | — | — |
| **#96** | Attendee-name disclosure — Eugene's ≤10-names cap | 🟡 S2 | S | — | ⛔ Andy confirming with Eugene |
| **#97** | Brokered intros — "message the person she recommends", consent-first | 🟡 S2 | M | — | ⛔ Andy's ruling + utility template |
| **#92** | Event selection for a multi-event world — she must pick the RIGHT schedule | 🟡 S2 | S | — | ⏸ waits for event #2's export |
| **#67** | Cohort + trend comparison, per field (panel vs cross-section) | 🟡 S2 | M | — | — |
| **#74** | Identity: 51% of form submissions belong to nobody | 🟡 S2 | M | — | — |
| **#17** | Auto-refresh videos and partners | 🔵 S3 | M | — | — |
| **#71** | "Virtual event" vs "call" vs "recording" — two contradicting "latest" answers | 🔵 S3 | M | — | — |
| **#48** | AT roster write-back | ⚪ S4 | S-M | — | — |
| **#19** | Privacy: share, keep, delete | ⚪ S4 | M | — | — |
| **#35** | New data source — DOCUMENTS (GroupOS) | ⚪ S4 | M | — | — |
| **#36** | New data source — CIRCLEBACK | 🚀 S4 | L | — | — |
| **#32** | What Olivia costs | 🔥 — | S | — | — |
| **#14** | Conversational, not robotic | 🔥 — | M | — | — |
| **#34** | Finalize the QA doc set | 🏁 — | M | — | — |
| — | *— CLOSED / LIVE / MOVED — evidence in the ticket bodies below —* | | | | |
| **#93** | Who-to-meet favors NEW faces (Eugene) | 🔴 S1 | S | n/a (endpoint) | ✅ **CLOSED 2026-08-19** — `1316c9c`; probe: "newer to MDS (joined this June), no crossover yet" |
| **#86** | Reminders — remind / reminders / unremind + sender + DELIVERY | 🔴 S1 | M | ✅ proven | ✅ **CLOSED 2026-08-19** — story proven on Andy's phone: sent 05:55:08, read 05:55:11; sender now every minute |
| **#76** | New eval bank — 100 organic questions | 🔴 S1 | M | ✅ built | ✅ **CLOSED 2026-08-19** (built 08-16, baseline 96% recorded 08-17; row never flipped) |
| **#88** | Partner profiles — event-specific, linked to the directory | 🟡 S2 | M | ✅ proven `4ca0b46d` | ✅ **LIVE** `aec2db47` (prod probe: Summit offer + partner page) |
| **#91** | She is Mille — identity across all five reply surfaces | 🔴 S1 | S | ✅ proven `273253bc` | ✅ **LIVE** `aec2db47` (prod probe: intro leads with Mille) |
| **#89** | Two rosters disagree about who is at the Summit | 🔴 S1 | M | n/a (loader+SQL) | ✅ **CLOSED 2026-08-18** — gap = identity, ledger complete; matched 124→170; single count source documented |
| **#90** | The chats mirror stopped syncing — she hands out dead invite links | 🔴 S1 | S | n/a (mirror) | ✅ **CLOSED 2026-08-18** — hourly n8n `RpEbU47SpMVsbwqg`, diff 0, 3h alarm |
| **#87** | "Who should I meet" returns people who aren't going | 🟡 S2 | S | ✅ proven | ✅ **LIVE** `74f0572a` (7/7 attending) |
| **#85** | 🚀 Summit schedule lane — activities, sessions, rooms, venues, audiences | 🔴 S1 | L | ✅ proven | ✅ **LIVE** `d6761eb4` (prod probes) |
| **#84** | Pre-announcement answer quality — chapter routing, transcript boundary, event phase rule, capability denial | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `5a12a2d1` (prod probe ×3) |
| **#82** | Flagship events (Summit, Inspire) carry what-they-are + who-is-in-the-room | 🔴 S1 | M | ✅ proven `2ecf4e62` | ✅ **LIVE** `e988a6a3` (prod probe) |
| **#81** | People + stats lanes answer what we have the data for (fit_reason, gender split) | 🔴 S1 | M | ✅ proven `3d5f2b1b` | ✅ **LIVE** `fd957034` (prod probe: named + reasons) |
| **#79** | Intro message rewritten — MDS AI assistant, early beta, current capabilities | 🔵 S3 | S | ✅ proven `d839a024` | ✅ **LIVE** `c59fd3ff` (byte-identical to approved copy) |
| **#80** | Offer binding: accepted offers deliver the teased video (+ offer rules) | 🔴 S1 | M | ✅ proven `dcc75770` | ✅ **LIVE** `c59fd3ff` (prod probe: `video_search`) |
| **#75** | Reactions raw store + canary + alarms | 🔴 S1 | S | ✅ proven `289a9656` | ✅ **LIVE** `e5d57236` (prod canary exit 0) |
| **#77** | Identity: active member usable without a WA chat row (559→732 reachable) | 🔴 S1 | S | n/a (SQL) | ✅ **CLOSED 2026-08-10** `b227682` |
| **#54** | Country dim + regions + geo lists | 🔴 S1 | S | ✅ proven | ✅ **LIVE** `01a94c1a` (holding-delay fix still Andy's to run) |
| **#56** | Partner ranking asks read a sample (Ian) | 🔴 S1 | S | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#58** | Cancelled registrations count as attendance | 🔴 S1 | S | n/a (SQL) | ✅ **LIVE** — one chokepoint view |
| **#62** | 🏗️ Resolve the 17 Security Advisor warnings | 🔴 S1 | S | n/a (SQL) | ✅ **CLOSED 2026-08-10** — 18 WARN → 2 accepted survivors |
| **#63** | 🏗️ Airtable-formula injection in the Make member-match (census + app v3) | 🔴 S1 | S | — | ➡️ **MOVED to the TF mapping/matching set (Andy 2026-08-10)** — not an Olivia task |
| **#52** | Follow-ups bind to the wrong topic (the 👎) | 🔴 S1 | S-M | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#55** | MDS credits into the billing lane (WA→AT→Supa) | 🔴 S1 | S-M | ✅ proven | ✅ **LIVE** (shared billing fn; Andy's WhatsApp test) |
| **#51** | Members-lane fabrication + over-refusal | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#53** | Fact-gate false clamp (grounded answer binned) | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#57** | Live-test trio: empty reports · wrong-turn Yes · "reply YES" wording | 🔴 S1 | M | ✅ proven | ✅ **LIVE** `955ed56f` |
| **#65** | 🚨 SQL functions exist ONLY in the live DB — no file in git | 🔴 S1 | M | n/a (SQL) | ✅ **CLOSED** — 118 files in `db/`, daily drift check proven |
| **#50** | ENTITY DOSSIERS | 🔴 S1 | M-L | ✅ all 4 lanes | ✅ **LIVE** `7f7b932f` (all four) |
| **#29** | THE DOSSIER + PERSONALIZATION LAYER (v1: 5 lanes) | 🔴 S1 | L | ✅ proven | ✅ **LIVE** `01a94c1a` |
| **#70** | 🚀 New data source — ZOOM CALLS (attendance · transcripts · schedule) | 🔴 S1 | L | ✅ proven | ✅ **LIVE** `7fe60761` |
| **#59** | Same event listed twice (events + partners) | 🟡 S2 | S | n/a (SQL) | ✅ **LIVE** — dossier joins on the row, not the name |
| **#60** | Cancelled side-event wore the Summit's name (app-event mis-link) | 🟡 S2 | S | n/a (sync+SQL) | ✅ **LIVE** — sync dedupe + 5-min alarm |
| **#38** | Interactive buttons (CTAs) for offers + links | 🟡 S2 | M | ✅ proven (report confirm-step open) | ✅ **LIVE** `01a94c1a` |
| **#20** | Census into the warehouse | 🟡 S2 | L | ✅ proven | ✅ **LIVE** `7fe60761` (only P2 exposure ruling open) |

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

> 📣 **Release-notes step also re-reads Olivia's intro/help copy** (#79, Andy 2026-08-11):
> the capability list is CURATED, never generated — so shipping a member-facing feature
> means checking whether the intro still tells the truth. It went stale for three releases.

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

### #88 · Partner profiles — event-specific, and nowhere in the warehouse
**🟡 S2 · size M — filed 2026-08-18**

> **In plain words:** partners have a rich profile at each event — offer, company, description, contact — and Olivia holds none of it.

*As a member, I ask what a partner does and what they're offering at this Summit, and get their actual offer rather than silence.*

A Partner attendee carries a profile the other types don't: display name, company, profession, description, **MDSOnly offer + instructions**, contact name, picture, LinkedIn. It is **event-specific** — the same person can be a Partner with an offer at one event and a plain Member at another. Singapore has no partners loaded yet (Member 116 · Speaker 29 · Staff 11 · Guest 23), so the shape is known only from another event's admin screen. Five of the fields already ride on the attendee row in the export (`description`, `offer`, `contact_name`, `partner_order`, `private_profile`); the rest don't serialise with no partner present.

**Shape of the fix:** `event.attendee_profiles`, 1:1 on `event.attendees` — the profile hangs off the attendee row, never off `people`, because it is per event and per type.

**Accept when:** partner profile loads and answers "what does X offer at this Summit" · **passcode never enters the warehouse** — it is a credential · booth staff are rows, not names typed into the description, or "which partner is Rob Torti with" stays unanswerable · gate GREEN.

#### ✅ LIVE 2026-08-19 — prod `aec2db47` (promoted with #91, gate green inside; prod probe: Summit offer + team + partner page)
**The source moved:** the GroupOS export still carries no partners (24h behind), so Andy fed the
AT "APP" view CSV directly — **11 companies · 20 people**, full member-facing profiles.

**The build:** migration `event_partner_profiles_20260819` — `event.partner_profiles` (one row per
company per event: description, snapshot, both offers, redeem instructions, contact, categories) +
`event.partner_people` (people as ROWS: name, role, ticket type) · loader
`scripts/load_partner_profiles.py` (idempotent, richest-value merge per company, categories
enriched from the view dump, refuses <8 companies) · **`partners` op** on `/api/olivia/schedule`
(mds-digest-web `d1924be`, deployed + verified on prod endpoint) · Answer Seed declares the op +
one routing rule (event asks = op=partners; `partner_lookup` stays the year-round directory).

| AC | result |
|---|---|
| answers "what does X offer at this Summit" | ✅ staging probe: StoreClaw → *"2 months free if you sign up while you're there — on top of their standing MDS deal"* + what they do + exact redeem path |
| passcode never enters the warehouse | ✅ loader ingests only the member-facing columns — no passcode, QR, form-URL, or ops fields exist in either table |
| booth staff are rows | ✅ `partner_people` 20 rows; probe *"which partner is Emily Wang with?"* → *"StoreClaw.Ai — BD Manager, alongside Oc Dai and Steven Zhou"* |
| gate GREEN | ✅ exit 0 · probe rows cleaned |

**Before → after:** partner questions about the Summit had NOTHING (0 rows anywhere) → 11
companies, 20 people, list + full-profile + person-lookup all proven on staging `4ca0b46d`.

**Directory link (Andy 2026-08-19):** every Summit partner that exists in the year-round directory
is LINKED — `directory_partner_id` FK to `partners_catalog` (migration
`event_partner_directory_link_20260819`), **11 of 11 matched**, loader re-derives it on every run
(normalized names; Live + most-claimed wins on catalog dups), and the op returns `partner_page`
(mds-digest-web `6188b9e`, verified on prod endpoint after a PostgREST schema reload).

**Path-separation probe matrix (Andy's ask, all four on staging, quotes verbatim):**
| ask | lane | answer |
|---|---|---|
| "is there a deal from StoreClaw?" (general) | `partner_lookup` directory | *"1 month free + 20% + 5% off Ultra"* + directory link — **no Summit offer** |
| "what does StoreClaw offer at the summit?" | `event_schedule op=partners` | *"Summit-only offer: 2 months free… (standing MDS deal outside the event is 1 month free + 25% off ULTRA)"* + team + partner page |
| "what special offers do partners have at the summit?" | event lane, list | all 11, each with its event offer |
| chain follow-up "tell me more about Hector" | event context held | *"Summit-only offer: … free for 1 month"* + *"Standing MDS deal"* labeled apart + on-site people |
| "tell me about StoreClaw" (general about-ask) | content sources | answered from the July 22 Mogul Call — **zero Summit-offer bleed** |

She labels *"Summit-only offer"* vs *"standing MDS deal"* unprompted — the separation Andy asked
to verify holds in both directions. Gate exit 0 after every pass.

**ATTENDEE-ONLY (Andy's ruling, 2026-08-19, LIVE `e55d991`):** event-specific offers are for
people ON the roster — a non-attendee member gets the company, the standing directory offer and
the partner page, with *"the event-specific offer is reserved for registered attendees"*; the
Summit offer, redeem path and on-site contact are stripped in the ROUTE, not by a prompt rule.
Proven both sides on the deployed endpoint. My first cut read the wrong variable (the browse
fallback grants every non-attendee a Member VIEW, so `myTypes` is never empty) — caught because
the "slow deploy" was actually the gate never firing; `/api/version` told the truth. Same build:
**12 reserved activities now carry `reservation_required` + the booking URL** (`1024014`) — the
flags were loaded since #85 and never surfaced.
**Named remainders:** categories missing on CrediLinq (absent in the view) · Trellis has no contact
block in the CSV · when the GroupOS export gains partner attendees (Andy: likely a "partner's team"
attendee type), link `partner_people` to `event.attendees` by email — 11 of 20 already appear there
as manual Speaker/Guest adds, 9 do not. **Promote carries #91 + #88 together** — staging holds both.

---

### #86 · Reminders — "remind me 30 minutes before"
**🔴 S1 · size M — built 2026-08-18, NOT DELIVERING**

> **In plain words:** a member asks to be reminded before something, and is.

*As an attendee, I say "remind me 30 minutes before the Welcome Dinner" and a message arrives in time to walk there.*

Today she computes the time correctly and then says she cannot send it — honest, but the capability is missing. GroupOS has a per-activity "Notify reminder to user" toggle, so ours must not double up with it.

**Shape of the fix:** store the reminder against the person and the thing, never against a wall-clock string; a scheduled sender reads what is due.

**Accept when:** a member can set, list and cancel a reminder in conversation · it arrives before the thing starts · absolute asks confirm the zone back · nothing is promised that cannot be delivered · gate GREEN.

#### 🟨 LIVE 2026-08-18 — prod `74f0572a`, but nothing is delivered yet
**The build:** `event.reminders` (migration `event_reminders_20260818`) — FK to the person and to the activity **or** session, one pending reminder per person per thing per moment so asking twice is idempotent. Ops `remind` / `reminders` / `unremind` on the schedule endpoint. `scripts/olivia_reminder_sender.py` — free-form inside the member's 24-hour window, utility template outside it.

| AC | result |
|---|---|
| set / list / cancel in conversation | ✅ live on prod — *"I'll remind you at 6:30 pm Singapore time, 30 minutes before the Welcome Dinner"*, lists, cancels |
| arrives before the thing starts | 🟨 **sender SCHEDULED 2026-08-18** — n8n workflow `QhJw46Mr7LAP8fdz` ("Olivia — Reminder Sender"), every 5 min from the cloud (survives this Mac sleeping through Summit week; launchd was blocked for me anyway). First tick exec **86839** 23:15:07 UTC: stale sweep ran, 0 due, stopped clean in 790 ms. Template `mds_summit_reminder` **APPROVED**. **Remaining proof: a reminder landing on a phone** — the pending test reminder (…8153, fires Aug 23 10:30 UTC) is the arranged test, or Andy asks "remind me in 5 min" any time |
| relative asks work | ✅ `in_minutes` computed server-side — **the model has no clock**: asked for "in 5 min" it sent a timestamp four hours stale and the endpoint correctly refused it as past |
| absolute asks confirm the zone | ✅ *"I'll remind you at 8:00 PM Singapore time"* — rule live on prod |
| nothing promised that cannot be delivered | ✅ non-attendee refused · unmatched name says so · past moment answers with the real start time · late reminders marked failed rather than sent |
| gate GREEN | ✅ passed inside the `d6761eb4` promote (schema only; no retrieval change) |

**Proof:** `remind "welcome dinner" lead 30` → *Welcome Dinner starts Sun 23 Aug 7:00 pm, remind at 6:30 pm Singapore time*; list shows both, `unremind` drops one. Sender dry-run against a real due row: *"⏰ Welcome Dinner starts in 30 minutes — Pool, Ritz-Carlton."*

#### ✅ STORY PROVEN 2026-08-19 05:55 UTC — the reminder ARRIVED on Andy's phone
Andy asked *"singapore remind me about the welcome dinner in 5 minutes"* (12:44 AM CDT). She booked
now+5 (the idempotency MOVED his existing Welcome-Dinner reminder to the new moment — one pending
per person per thing, as designed). The sender's 05:55:08 tick sent it; the ledger shows the wamid
and **delivery status `read` at 05:55:11 — three seconds after send**; his screenshot shows
*"⏰ Welcome Dinner starts at 7:00 PM Singapore time — Pool, Ritz-Carlton."* Honest wording, real
start time, days before the event (the never-refuse-a-valid-time rule doing its job).
**Total latency was ~10 min** (+5 to the due moment, one 10-second tick miss, +5 to the next tick)
— Andy called it, so the sender now runs **EVERY MINUTE** (`QhJw46Mr7LAP8fdz` renamed to match):
worst case after due ≈ 1 min. Reminders remain SCHEDULE-ANCHORED by design — her refusal of
freestanding "remind me to check fb" is correct behavior (new ticket if ever wanted).

**The sender is scheduled (2026-08-18):** n8n `QhJw46Mr7LAP8fdz`, a faithful port of `olivia_reminder_sender.py` (7 nodes: stale sweep → due query → 24h-window check → text-or-template send → outcome PATCH), reusing the prod workflow's own Meta + Supabase credentials. n8n over launchd because reminders must survive this Mac sleeping during Summit week; the script stays as the manual/dry-run tool. The template was submitted from here and is **APPROVED** — the WABA id (`1575708577606583`) was in the workflow's own *Subscribe App to WABA* node all along, after I asked Andy for it three times. **Left: the arrival itself** — pending test reminder fires Aug 23 10:30 UTC at …8153, or a "remind me in 5 min" ask proves it any day.

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

### #78 · Typeform recovery — I deleted 250 forms; 96 lost their responses and live collection points went dead
**🔴 S1 · size M · filed 2026-08-10 — DEADLINE: Singapore Summit in 10 days**

> **In plain words:** Members and sponsors are clicking links that no longer exist, and we are finding out through complaints.

*As a sponsor filling in the Singapore company form, my link works and my submission is recorded.*

**What happened:** on 2026-08-08 I deleted 250 Typeforms via the API as a "prune" of low-response
forms. API deletes are permanent and bypass the trash. Andy's ruling after the fact:
**never delete from Typeform — it is a source of record** (memory `feedback_never_delete_typeform`;
prune scripts removed in `1aa0951`).

**The damage, all 250 accounted for** — [TYPEFORM_LOSS_REGISTER.md](TYPEFORM_LOSS_REGISTER.md):
129 had zero responses · 24 have their data safe in `digest.form_responses` · 1 partial ·
**96 lost 465 responses with no copy anywhere.** 2026 breakdown in
[TYPEFORM_2026_LOSSES.md](TYPEFORM_2026_LOSSES.md): 12 forms/58 replies confirmed 2026 and safe,
18 forms/101 replies certainly 2026 and gone, 78 forms/364 replies undatable.

**Two forms were still actively collecting when deleted** — Singapore Company Information (last
reply Aug 6) and Singapore Hack Contest (Aug 5). Work queue:
[TYPEFORM_RECOVERY_QUEUE.md](TYPEFORM_RECOVERY_QUEUE.md).

**Done so far:** Company Information rebuilt as **`GljwvNGO`** — 10 fields matching the backup on
title/type/required/choices/ref, logic byte-identical, public page HTTP 200. Two of its seven
surviving responses re-entered and verified through the Responses API, tagged with hidden
`restored=true` + their true original dates.

**Four traps for whoever finishes it:**
- **A rebuild gets a NEW form id.** Old links stay dead in Webflow, GHL, WhatsApp and the app —
  none of which are greppable from this repo. Rebuilding is half the job; re-sharing is the rest.
- **Responses cannot be imported.** The Responses API is GET and DELETE only; the only POSTs
  generate media files. Restoring data means re-entering it by hand through the live form.
- **`submitted_at` is server-set** and cannot be backdated, so every restored row reads today.
  The hidden `original_submitted_at` is the only thing distinguishing a restored row from a fresh
  signature — and these forms carry legal acknowledgements, so that distinction matters.
- **The harness blocks `PUT /forms/{id}`** (create works, edit does not) and the browser pane
  collapses to a 0×0 viewport mid-session. Form edits go through
  `scripts/typeform_add_hidden_fields.sh` for Andy to run.

**Accept when** the recovery queue is empty · every rebuilt form is in
`scripts/typeform_never_delete.txt` · all 7 Singapore Company Information responses are re-entered
and verified field-for-field against the CSV via the Responses API · the 3 orphaned Channel Call
Opt-ins (Accelerator, Large SKU, Resellers — the only 3 of 16 channels with no live opt-in) are
back · someone has re-shared the new links wherever the old ones were published.

---

## 🏗️ ARCHITECTURE & AUDIT — ⭐ START HERE (Andy 2026-08-08)

> ⭐ **Andy's call: these four run before any feature work.** #62 and #63 are both size S —
> the quickest way to open a session. #63 is a live injection hole, so it is the one with a
> clock on it.

Four tickets, ahead of feature work. #65 closed tonight and every one of these was made
sharper by what it exposed: logic living in one place only, checks that pass for the wrong
reason, and jobs whose failure mode is silence.

### #61 · Schema audit — most warehouse tables show NO connections, and nobody has written down why

#### ⬛ ADDED 2026-08-08 — three concrete violations found while doing #65 and #68

1. **TWO competing mapping tables for one job.** `digest.form_field_map` (form+ref → canonical_key,
   56 rows, Olivia's) and `digest.form_question_map` (form+question → concept, 1,314 rows across 114
   forms, the trend-report agent's) both answer "which canonical field is this question". Textbook
   SSOT violation; #68 resolves it by pinning one and retiring the other.
2. **The form-scope wall is a convention repeated five times, not a chokepoint.** `form_windowed`,
   `my_form_answers`, `form_field_history`, `persona_signals` and `persona_signal_fingerprints` each
   inner-join `form_scope` themselves. A sixth consumer written without it exposes all 156
   non-scoped forms. #58 solved this exact class for events with one view; forms never got the same
   treatment. #68 Task 1 adds `digest.form_reach`.
3. **The FB linker exists in no file and no function.** `load_feed.py` fills `digest.fb_posts`, but
   the INSERT that moves those rows into `content_items` — the thing that makes them searchable — is
   raw SQL typed by hand each run. It **silently never ran once**, hiding four days of data. Same
   class #65 fixed for the other 104 functions; this one is not even in the database to export.

#### ✅ 2026-08-11 — violation #3 CLOSED (violations #1 & #2 route to #68)
FB linker is now the committed DB function `digest.fb_link_content()` (`db/functions/fb_link_content.sql`,
commit `5fff683`): links posts/comments → `content_items`, stamps image `storage_path`, folds image
OCR/description → `search_extra`. Runs every load via `load_feed.py` AND wired into the autopilot
`auto_import.py:process_feed()` (feed+comments+images→embed on every `~/Downloads` drop, launchd
`com.mds.scorecard.autoimport`). Proven searchable: `content_search_v2(['TACOS'])` returns posts whose
"TACOS" lives only inside a spreadsheet screenshot (`body_has_tacos=false`). SOP
`/Users/Born/mds-scorecard-tools/FB_PIPELINE.md`; full write-up `SESSION_LOG_SCORECARD.md` 2026-08-11.
**Remaining #61 = the schema-audit deliverable** (full-digest ERD, orphan audit per relation, safe-FK
rulings, dual-key spine documented as table COMMENTs + handbook) — untouched.

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

#### ✅ 2026-08-12 — research done, orphan audit measured, 30 COMMENTs shipped; FK-adding filed as follow-up

**Result: zero true orphans found.** Every implicit relation checked (18 `at_member_id` joins + 7
other high-fan-out relations) came back 0 orphans against its correct parent. The audit's real find
was a wrong assumption, not missing data: **`member_profiles.at_member_id` is the true root, not
`member_attributes`** — checking against `member_attributes` throws false positives (187/134/29/11
across four tables) because `member_attributes` is a derived, narrower persona subset
(0 `member_attributes` rows fall outside `member_profiles`, confirmed). Non-zero counts elsewhere
(`fb_comments`/`fb_posts.author_uid` 248/207, `olivia_sends.wamid` 317, `olivia_seen.wamid` 59) are
not orphans — non-member FB authors and proactive/broadcast sends legitimately have no parent row,
now written down as the reason.

The `members`↔`member_profiles` crosswalk (research question 4) already exists as
`digest.member_identity` (#77) — no new object needed, just cited.

**Shipped:** `FORMS_ERD.md` §3 (full digest schema — 58 tables, 13 declared FKs + 31 audited
implicit columns, orphan table, polymorphic-key rulings) · migration
`digest_schema_audit_comments_20260812` (31 `COMMENT ON COLUMN`, metadata only, no lock) · gate
253 exit-0 before and after.

**Deliberately not shipped:** FK constraints. 25 relations are orphan-clean today (18 at_member_id
+ 7 others) but "safe" needs each loader read for insert order, not just a point-in-time count —
that's follow-up work, named explicitly in FORMS_ERD.md §3.5, not silently dropped.

**AC checklist:** every table in the ERD with edges — met · orphans measured per relation with a
ruling — met, 0 true orphans · FKs added only where provably safe — not met by design, candidates
named for a follow-up · gate green, no sync job broken — met (COMMENT-only migration).

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

#### ✅ CLOSED 2026-08-10 — prod `39009a6`
**Live advisor was 18 WARN, not 17** (`pct_from_answer` was added since filing). **18 → 2.**

| Class | Was | Now | How |
|---|---|---|---|
| Function Search Path Mutable | 13 | **0** | `ALTER FUNCTION … SET search_path='digest','pg_temp'` on all 13 (migration `olivia_62_pin_function_search_path`). ALTER not REPLACE → IMMUTABLE + generated columns preserved. |
| SECURITY DEFINER anon-executable | 2 | **0** | `REVOKE EXECUTE … FROM public` on `auth_org_ids` + `rls_auto_enable`. Role-level revoke was a no-op — the grant was the default PUBLIC grant. |
| SECURITY DEFINER authenticated-executable | 2 | **1 (accepted)** | `rls_auto_enable` cleared; `auth_org_ids` kept for `authenticated` — RLS policy `self_read_org_members` needs it. |
| Leaked Password Protection | 1 | **1 (Andy's toggle)** | Auth dashboard setting, belongs to the password-based public app. |

**AC checklist:** ✅ 0 warnings *or written acceptance* — 16 fixed, **2 accepted in handbook §12** ·
✅ 13 pinned functions proven live (497 partner + 1032 video tsv rows, 0 nulls; both embed-invalidate
triggers fired on a live self-update, no embedding wiped; all 13 called directly, resolve) · ✅
`public.*` origin identified (shared-app multi-tenant RLS helper + an event-trigger fn) **before**
revoke; revoke verified not to break the RLS policy (authenticated kept) · ✅ **leak gate 246 exit 0**
before and after · ✅ `db/` re-exported, 121 files byte-match, drift IN SYNC.

**Left for Andy (both accepted, not blockers):** enable Leaked-Password-Protection in the Auth
dashboard if the public-schema app should have it · the 28 INFO `rls_enabled_no_policy` are the
secure state (service_role-only, anon denied) — *why* RLS is on them is #61/#64, not this ticket.

---

### #63 · Injection audit verdict — SQL clean; ONE real injection found in the Make member-match

> ➡️ **MOVED OFF THE OLIVIA BOARD 2026-08-10 (Andy).** This is a **Typeform mapping/matching**
> task, not Olivia — it belongs with the TF field-mapping set (#68 canonical dictionary, #74 form
> identity), where "how we match members" is the actual subject. Olivia only inherits the result.
> **Read-only findings captured, nothing acted on:** the injection reproduces live (payload
> `" & {Preferred Email} & "` makes the filter always-true and returns a real member); a sweep of
> all 171 Make scenarios found **68 interpolated query sites** (110 unread on 429s), so the fix is a
> pipeline-wide sweep, not two modules. A fix script + blueprint backups exist locally
> (`scripts/fix_make_formula_injection.py`, `scripts/make_backups/`) but were never applied.
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

#### ⬛ ADDED 2026-08-08 — the failure mode is always silence

- **26 of the loader's 114 form ids pointed at forms deleted from Typeform.** `fetch_form` gets an
  error body, `d.get("items") or []` yields nothing, and the run prints "0 completed" — forever.
  Fixed to 88, but the lesson stands: **a dead job here looks identical to an idle one.**
- **Eight launchd plists exist only on Andy's Mac and in no repo** — the same single-copy risk #65
  just fixed for SQL, one layer up. Only the new `com.mds.db.drift` is tracked.
- **Thirteen channel-call opt-in forms collect into nothing** — members sign up for call reminders,
  the responses reach no warehouse table and no workflow anyone can find. Either wire them up or
  retire them; right now the signup is a dead letter.
- **Typeform deletions are permanent and bypass the trash.** 245 forms were deleted on 2026-08-07
  before that was understood. Rule recorded: **Typeform is a source of record — prune the loader
  config or `form_scope`, never the source.**
**🔴 S1 · size M — filed 2026-08-06 (Andy: "why is the app logic scattered between so many places")**

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


### #70 · 🚀 New data source — ZOOM CALLS (attendance · transcripts · schedule)
**🔴 S1 · size L — filed 2026-08-06 · research COMPLETE, build NOT started**

#### ✅ 2026-08-07 — BUILT, PROBED, PROMOTED (prod `7fe60761`)

| AC | result |
|---|---|
| `digest.calls` holds every 2026 call, loaders idempotent | ✅ 254 calls · re-runs change 0 rows |
| `call_attendance` ~2,000 rows across the member calls | ✅ **4,348** rows, all 90 calls |
| ≥95% of published member calls carry `groupos_video_id` | ⚠️ **85 of 90** — the other 5: 4 genuinely unpublished, 1 recovered late |
| ≥60% of attendance rows resolve to a member | ❌ **48.1%** of person rows — the honest number; `partial` guesses are a review queue, not stamped |
| transcript chunks searchable with the right access_rule | ✅ 3,116 chunks, all embedded, restricted follow the video |
| a probe returns the passage WITH the video link | ✅ and on natural questions, not just named-call asks |
| nightly/weekly job heartbeats and alarms when stale | ✅ `com.mds.zoom.weekly` + `zoom_weekly` heartbeat (**degraded** while GROUPOS_PAT is missing) |
| gate GREEN | ✅ **232 → 243**, now covering attendance + transcripts |

**Andy's rulings:** ① transcripts vectorized to drive VIDEO suggestions; quote and link the
LIBRARY video, never Zoom ② **attendance STORED, NEVER SHOWN** ③ summaries short and scannable
(one lead line + 4-5 labelled bullets, WhatsApp bold).

**The filename join was fragile and it had already cost us.** Andy: *"what if someone changes the
file name?"* — right. Fallback added on signals a rename cannot destroy (same-week publish,
duration within 3 min, title overlap, unique candidate only). It **recovered 2 renamed files**,
Craig Brockie and the AppLovin Expert Call, both previously counted as "never published". A
detector now separates "unpublished" from "we missed it".

**A third of "attendance" was never a person** — 138 AI-notetaker and host names, 1,089 rows,
which would have become `co_attended` edges for people who do not exist.

**The lane took four things and the first three alone changed nothing:** title-rank as a fourth
RRF list in `content_search_v2` (`dorian gorski` 0 → 6 transcript rows) · `videos_catalog.search_tsv`
indexes the SUMMARY at weight B · tool descriptions · **and the rule that advice-shaped asks run
`video_search` alongside the chats**. Same lesson as #20: describing a tool is not telling her to
use it.

**Code review found 5 Criticals, all real:** TLS verification silently OFF in the launchd job
(`/usr/bin/python3` has no certifi, so credentials went over an unverified connection) ·
`videos_weekly_check.py` had never once run · **Zoom URLs stored on 253/253 `calls.raw` rows** ·
`zoom_resolve_attendance` existed only in the live DB · **the gate had zero coverage of the new
surfaces**. All fixed. Separately the gate caught a concurrent session resetting `video_search`'s
ACL, leaving **anon able to call it**.

**Still open:** speakers on only 413 of 1,024 videos · 4 calls with no published recording ·
`map_video` imported from an untracked repo.

> **In plain words:** Olivia can see that a call happened and that a video exists. She cannot see
> who was in the room or a single word that was said. Zoom holds both, and we now have the API key
> that reads them.

*As a member, Olivia knows which calls I actually attend and what was said inside them — so she
answers "what did they say about TikTok Shop on the last mogul call", points me to the minute of the
video that covers it, and stops recommending the channel call I never miss.*

This closes three of the handbook's own §14 limits verbatim: **"No transcripts. Olivia finds a call
and its deck, never what was said inside it."** · **"The live calls calendar (Mogul / Expert /
Channel Calls) is not connected."** · and it supplies the missing event *description*, since a
transcript is the richest description a call has.

#### What the research established (all verified live 2026-08-06, nothing written anywhere)

**Access.** A Server-to-Server OAuth app (**"Mille"**, created by owner Ian Sells) is live; creds in
`/Users/Born/Scorecard/.env.zoom` (gitignored). Token exchange, scopes and every endpoint below were
proven with `scripts/zoom_probe.py`. All 395 member-facing calls in 5 years were hosted by the single
account `contact@milliondollarsellers.com`.

**Three different history depths — this shapes the whole design:**

| Data | Endpoint | Reach | 2026 volume |
|---|---|---|---|
| Calls + recordings + MP4/M4A | `/accounts/me/recordings` (1-month windows) | **2020-05-26 →** | 253 recorded, **90 member-facing** |
| Transcripts (VTT, speaker-labelled) | `/meetings/{uuid}/recordings` → `TRANSCRIPT` | **2026 only** (Zoom transcription switched on ~Jan 2026; 0 before) | **165**, of which 63 on mapped member calls |
| Attendance | `/report/…/participants` = `/metrics/…/participants` (identical counts) | **~13 months, ROLLING** — Jun 2025 ✅, May 2025 `12702 a year ago`, 2024 `3001 does not exist` | ~2,000 rows over 90 calls |
| Forward schedule | `/users/{id}/upcoming_meetings` + `type=scheduled` | forward | 43 member occurrences / 17 series |

**The video join is exact, not fuzzy.** GroupOS stores Zoom's original filename in `video_url`
(`…1786034085413-GMT20260805-160238_Recording_1920x1080.mp4`); `GMT<YYYYMMDD>-<HHMMSS>` is the Zoom
`recording_start` in UTC. **82 of 90 member calls matched by exact filename, 0 needed a ±3-min
window, 0 orphans the other way.** The 8 unmatched are genuine publishing gaps (18 Feb Leslie Eisen
hotseat, 18 Feb Rockies, 2 Apr Advisory Council, 21 May Logistics, 3 Jun Craig Brockie, 20 Jul Large
Catalog Sellers, 21 Jul AppLovin, 31 Jul Accelerator). Title and duration matching were tried first
and are **rejected** — nearly every call runs ~55 min, so duration paired Dorian Gorski with a
CAC/LTV video; the two-hop event join only reached 48%.

**Identity is the hard part, and registration is ruled out (Andy 2026-08-06: "this is an expensive
cost. so no reg").** Verified: `approval_type=2` on every call and `/registrants` returns
*"Registration has not been enabled"*, so Zoom holds **no email** for link-joiners — **7 of 765
distinct names (0.9%) carry one, always the host**. `participant_uuid` exists only on the dashboard
endpoint and is per-meeting, so it is **not** a stable person key. Matching is therefore by display
name against `member_attributes`, measured on the real 12-month set: **67% of attendance rows
auto-resolve** (279 exact + 102 partial), 58 names need one human decision, 306 names never match
(232 are single-word: `Adi`, `Holly`, `Matt`, `Scott`). Draft alias sheet already produced
(`scripts/zoom_alias_draft.py` → `zoom_alias_draft.csv`, 765 names ranked by call count).
Frequent unresolved names worth a human eye: **Reinaldo Pelaez (36 calls)**, Sriram Ponvel (21),
Bogdan Lupu (14), Fazlul Karim (13), Holly (12).

**Scope ruling (Andy 2026-08-06): 2026 only.** That drops the AssemblyAI backfill of ~1,400
pre-2026 recordings entirely — 2026 transcripts already exist as Zoom VTTs, so this ticket costs no
transcription spend.

**Shape of the fix** — three tables in `digest`, files-first because of #65:
- **`calls`** — one row per Zoom meeting UUID: topic, derived `call_type` (mogul / expert / channel /
  chapter), host, actual start+end, duration, participant_count, `has_recording`, `has_transcript`,
  `groupos_video_id` (filename join), raw payload jsonb. Ingest all 253 with an `is_member_facing`
  flag, not just the 90 — cheap now, avoids a re-pull.
- **`call_attendance`** — one row per join: call_uuid, display_name, folded name, join/leave,
  seconds, nullable `at_member_id`. **Never keyed on the video** — 8 calls have no video, and
  attendance exists whether or not anything was published.
- **`zoom_name_alias`** — folded display name → `at_member_id` + confidence + who decided.
  Resolution lives here, never baked into attendance rows, so one new alias re-resolves all of 2026
  for free.
- **Transcripts** land as `content_items` rows (chunked, embedded, `access_rule` + `sensitivity`)
  so `content_search_v2` finds them with no new engine, plus the raw VTT kept against the call.
- **Attendance also feeds `member_events`** (append-only, `cadence='backfill'` then `'daily'`) and
  `co_attended` edges in `member_edges` — the personalization layer already reads both.

**What we do next, in order:**
1. **Andy's two rulings below** — nothing is built until the sensitivity ruling lands.
2. **DDL as files** (`sql/` in this repo, applied via migration) — the three tables + indexes.
3. **Backfill 2026:** calls (253) → attendance (~2,000 rows, 90 calls) → the 82 video links →
   transcripts (63 member calls) chunked + embedded into `content_items`.
4. **Alias review pass** — Andy or Kat clears the 58-name queue once; unresolved rows still load.
5. **Nightly job** (launchd + heartbeat, same pattern as the other 5): yesterday's calls,
   participants, new VTTs, alias re-resolve. Attendance ages out of Zoom on a rolling window, so
   this is what stops the loss becoming permanent.
6. **Olivia lanes** — transcript search inside `content_search_v2`, "what did I attend" in the
   member's own dossier, and the calls calendar answering "when is the next mogul call".

**Accept when:**
- `digest.calls` holds every 2026 call (253) with `is_member_facing` correct on the 90; every table's
  DDL exists as a file in the repo (#65's rule) · re-running any loader changes 0 rows (idempotent).
- `call_attendance` holds ~2,000 rows across the 90 member calls; **spot-checked against the Zoom
  report API for 3 calls, exact row-count match**.
- ≥95% of published 2026 member calls carry their `groupos_video_id` (today's measured join: 82/90 =
  91%, the other 8 have no video to link).
- ≥60% of attendance rows resolve to an `at_member_id` on first load (measured today: 67%), and the
  unresolved remainder is still queryable by name.
- Transcript chunks are searchable through `content_search_v2` with the correct `access_rule`, and a
  probe of the form *"what was said about X on the <date> mogul call"* returns the passage **with the
  video link**.
- The nightly job stamps `olivia_job_heartbeats` and alarms when stale · **gate GREEN (224+)** ·
  matrix rows added.

**Named non-goals:** pre-2026 anything (scope ruling) · AssemblyAI transcription · turning on Zoom
registration · surfacing attendance counts or rankings to members (§7.3's internal-sort-key rule
applies unchanged).

---

### #68 · 🔑 Canonical question dictionary — make mapping scale before the form count does
**🔴 S1 · size L — filed 2026-08-06 (Andy: "mapping becomes a paramount task… this number will go up rapidly")**

> **In plain words:** Questions asking the same thing on different forms must resolve to one field —
> and that has to keep working when we have twenty forms, not five.

*As the owner, any concept the community answers about — revenue, staff, margin, tools — reads as
ONE field no matter which form or year it came from, and adding a form does not create mapping debt.*

#### ⬛ RE-MEASURED 2026-08-08 — the ticket got smaller AND bigger. Plan: `docs/superpowers/plans/2026-08-08-canonical-question-dictionary-v2.md` (v1 superseded — it assumed scope was fixed at 5 forms)

**Smaller, because the dictionary already exists and is not ours.** `digest.form_concept` (81
concepts carrying label/family/value_kind/window_note — the type/units/period this ticket asked
for), `concept_rule` (80 prioritised regexes), `form_question_map` (1,314 questions across 114
forms) and `member_fact` (56,876 member×concept×year rows, 2020→2026) were built by the
trend-report agent. **Do not build a second dictionary — converge on that one and PIN it**, because
it is regenerated from regex rules another team owns and a rule edit would silently change Olivia's
answers.

**Bigger, because the real gap is on the forms she already reads.** Of the **350 questions across
Olivia's five forms, 149 are linked — 43%.** Per form:

| form | questions | linked | |
|---|---|---|---|
| MDS Annual Census 2026 | 96 | 65 | 68% |
| Standard – Annual Census (legacy) | 63 | 31 | 49% |
| MDSonly – Census Master (legacy) | 89 | 28 | 31% |
| **New Member Application v3** | 61 | **16** | **26%** |
| Honorary Member Application | 41 | 9 | 22% |

**201 unlinked questions**, and the worst offender is app v3 — the newest, most structured form,
where three-quarters of what an applicant tells us reaches no canonical field.

**Rules settled with Andy 2026-08-07/08:**
- **Canonical namespace = the LIVE forms** (census 2026, app v3, honorary). Legacy maps *into* it;
  a legacy-only question stays history-only and never becomes a key.
- **Nothing decays and nothing is deleted.** Every answer is a timestamped event; the canonical
  value is the newest by `submitted_at` — never by upload order. Load an old form tomorrow and a
  newer census answer still wins.
- **Axis mismatch groups but never merges** (bands vs figures; per-country columns vs one
  multi-select). Say which years can actually be compared.
- **Nothing auto-applies.** The matcher emits a RANKED list of 5; a human picks, says none, or
  opens a new key. Evidence: trigram ranked the correct match for "formal title" **third**, losing
  to "what is your main niche?" by 0.01 — lexical similarity is noise at that range, so Voyage
  embeddings rank and trigram is only a recall net.
- **Matrix rows collapse to their PARENT before matching** — legacy stored "Where do you
  manufacture? (China)" as 8 sibling columns; matching per-ref made trigram pick an arbitrary
  sibling in 21 of 39 cases.
- **21 mappings already ratified by Andy** (2 exact, 12 near, 7 from the weak list).

**Old measurement, kept for the record — 2026-08-06:** **25 of 316 form-questions mapped — 8%.** 291
unmapped, **184 of those with 50+ respondents**. Unmapped answers ARE processed (they key on their
own ref, appear in the catalog, answer normally — 94 of the 100 askable questions today are
unmapped). The ONLY thing missing is cross-form/cross-year unification: legacy census revenue and
census-2026 revenue stay two streams instead of one, and the failure is SILENT — a half-answer, not
an error.

**Why this compounds:** check-in forms, Inspire check-ins, last year's check-ins and historical
forms are all queued to load. Each adds 40–85 questions. Hand-curation is O(n) forever and drifts.

**The shape that makes it tractable — the work is NOT 700 mappings:**
1. **Concept dictionary (~40–60 keys), not per-question mapping.** Most questions are single-form
   and never need a key. What recurs is a small stable set: revenue family, channel splits, niche,
   products, brands, staff/team, margin/COGS, kids, tools, financing. Dictionary carries name +
   description + **type + units + period** (kills #66④: "revenue USD" cannot collide with
   "revenue local", "pay monthly" cannot collide with "pay annual").
2. **Coverage report as a standing instrument** — every question split into *needs a key* (concept
   appears on 2+ forms) vs *single-form, none needed*, ranked by respondents. Without this split the
   291 looks like 291 units of work when it is likely a few dozen.
3. **Assisted matching, human ratification.** Propose candidates with `pg_trgm` (installed) +
   Voyage embeddings (in the stack) so "What do you pay a Manager per month?" matches `pay_manager`
   with no shared words. **PROPOSAL ONLY — never auto-apply.** A wrong merge silently fuses two
   different concepts, which is worse than unmapped, and violates the never-guess rule.
4. **Upstream fix — the real leverage.** New forms pick questions FROM the dictionary at build time
   (same ref, same wording, declared units), so mapping cost on arrival is zero. Retro-mapping is
   cleanup; the dictionary is what stops it recurring. Needs Eugene in the loop.

**Accept when**
- Dictionary exists with type/units/period per concept, in the DB and documented.
- Coverage report separates needs-a-key from single-form; every needs-a-key question above a
  respondent threshold is either mapped or ruled not-comparable in writing.
- Assisted proposals produce a ratification queue; nothing enters `form_field_map` unratified.
- A cross-form question proves it end to end (revenue 2022 → 2026 as one stream, and a newly mapped
  concept like staff location or pay bands doing the same).
- Form-design rule written into the census/forms docs so the next form ships WITH its mappings.
- QA sweep extended to assert units/period; gate GREEN.

---

### #66 · Forms warehouse — the remaining gaps (mapping split out to #68)
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

**② MOVED TO #68** — measured properly it is 25 mapped of 316 form-questions (8%), and Andy
ruled it paramount. Now its own S1 ticket with the dictionary + assisted-matching design.

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

### #93 · Who-to-meet favors NEW faces — novelty beats familiarity
**🔴 S1 · size S — filed 2026-08-19 from Eugene's beta report (Andy: "agree, we can do it")**

> **In plain words:** "who should I meet" was handing an OG his oldest friends; it should hand him people he has NOT met — especially newer members.

*As a long-time member, "who should I meet at the Summit" surfaces people I don't already know — newer members first — because meeting my old friends needs no assistant.*

Eugene, verbatim: *"it needs to prioritize newer members, giving you newer members that you
haven't met instead of older members because it's sending older members here and I know all of
them. I feel like it's gonna do the same for others."*

**Shape of the fix:** two REAL signals into the `people` op ranking — `digest.member_edges`
(observed co-engagement asker↔candidate, 141k edges: heavy tie = downrank, no edge = boost) and
`member_profiles.join_date` (joined ≤12 months = boost). Reasons quote the signals; never invented.

**Accept when:** an asker with heavy ties sees new faces ranked above old friends · rows carry
honest labels ("joined <month year>", "no shared chats or events on record") · a new member's
results stay sensible (their whole world is new faces) · gate GREEN · before/after on Eugene-class
asker recorded.

#### ✅ CLOSED 2026-08-19 — endpoint `1316c9c`, nothing to promote (no n8n change)
**The fix:** the `people` op ranks with two real signals on top of topic overlap —
`member_edges` co-engagement with the asker (heavy tie = log-damped downrank; NO edge = boost) and
`join_date` (≤12 months = boost). Every row carries its honest label; the note tells the model the
ranking philosophy.

| AC | result |
|---|---|
| new faces above old friends | ✅ direct op check (test asker with heavy ties): three no-edge strangers lead; Neeme Roos — the morning's #2 — dropped to 7th |
| honest labels on rows | ✅ `newer_member: "joined Jun 2026"` (only when true) · `connection: "no shared chats or events on record"` / `"you two already share activity"` |
| full loop verbalizes the reasons | ✅ Mille: *"Michelle Xu — newer to MDS (joined this June) and you don't have crossover yet — a good chance to make a fresh connection"* |
| new member's results stay sensible | ✅ structural: for a no-edge asker every candidate gets the same +1, ranking falls back to overlap |
| gate GREEN | ✅ exit 0 |

**Before → after (same asker, same day):** Alex Bonilla / Neeme Roos / Brandon Himmel — all
already-connected — led the list → three genuine strangers + a June-2026 joiner lead, connections
labeled. **Watch at scale:** join-date coverage is 977 of the roster; attendee sets skew veteran,
so the newer_member label appears only when real.

#### ✅ REVISED same day to the WRITTEN recommendation logic (Andy's correction) — `3ce77c7`
My first cut could rank a weak-match stranger above a strong-match expert — violating
proficiency-first. Now aligned with handbook §7.1: **PRIMARY = expertise-ledger percentile** on
the matched topics (mapped via `expertise_topics.terms` curated aliases; ledger-uncovered
candidates cap at a mid-low tier), **tiers = deciles** ("several matches" = same decile), and only
inside a tier: **member value** (`engagement_score`) ± **the EQUALIZER** (new
`digest.olivia_recommendations` log — every recommendation recorded fire-and-forget; hard 30-day
per-asker no-repeat, soft 7-day global exposure spread) ± the #93 novelty terms. Scores stay
internal (§7.3).
**Equalizer proven live:** two identical asks seconds apart returned **zero overlapping names** —
run 1 (Wei Lin, Igor Chernyavskiy, Sam Uloho…) logged, run 2 fully reshuffled. Gate exit 0.
**Named remainder:** the log + equalizer cover the EVENT people lane; Eugene's Moe repeats came
mostly from the general members lane (`member_match`) — extending the equalizer there is the next
slice of his item 3.

---

### #94 · Expertise Ledger v2 — the living skill sheet
**🔴 S1 · size M — filed 2026-08-19 · spec + taxonomy Andy-APPROVED · 📋 PLAN: `docs/superpowers/plans/2026-08-19-expertise-ledger-v2.md`**

> **In plain words:** every member — new, silent, or loud — gets an honest per-skill score, on skills the community actually discusses, and proven expertise never rots to zero.

*As a member, "who knows X" and "who should I meet" see the REAL me — what I declared, what I spoke about, what my posts earned — not just how loudly I chat.*

Andy's rulings, binding: activity keeps its teeth · speaking strongest (3.0×) · engagement bonus `1+ln(1+reactions)/4` · forms floor ×1.2 · decay half-lives 12mo activity / 24mo speaking · **floor = 40% of all-time peak** · taxonomy 18 parents + 34 corpus-born subtopics (Claude-vs-GPT merged; Real Estate Investing + Credit Cards & Travel Hacks added) · subtopics graduate via quarterly density re-checks.

**Accept when:** the plan's 4 tasks land · verify script all-PASS (silent members gain; floor holds; Andy top-quartile Intl Expansion; speaker outranks same-profile non-speaker) · who-to-meet matches on a subtopic with zero code changes · gate GREEN · before/after: distinct scoreable members recorded.

---

### #95 · Equalizer for the members lane — "Moe ×12" lived in `member_match`
**🔴 S1 · size S — filed 2026-08-19 (Eugene: "they've mentioned Moe to me at least a dozen times")**

> **In plain words:** the general "who should I talk to" lane still recommends the same person forever; the event lane already stopped.

*As a member, I don't get the same name every time — and our most active members don't get buried in DMs because every answer points at them.*

The `olivia_recommendations` log + equalizer (hard 30d per-asker no-repeat, soft 7d global spread) shipped on the EVENT people op with zero-overlap proof. `member_match` — where Eugene's dozen actually happened — still ranks statically.

**Accept when:** member_match reads AND writes the recommendation log · two identical member-lane asks return different names · the log carries lane='member_match' rows · gate GREEN.

---

### #96 · Attendee-name disclosure — the ≤10-names cap
**🟡 S2 · size S — filed 2026-08-19 · ⛔ BLOCKED: Andy confirming the rule with Eugene**

> **In plain words:** Eugene proposed she may name up to ~10 attendees of an event; today she gives counts only.

*As a member, "who from APAC is at the Summit" gets a short named list, not just a number.*

Eugene, verbatim: *"the AI will not share more than 10 names of who's attending an event but it could share information like who's attending. It just needs to be limited."* This reverses the July aggregates-only ruling (gate asserts `full_name` ABSENT from `event_who`), so it ships only on the confirmed ruling. The chapter-count code path (`people` op, `chapter` param) is already built to return the capped list the day the ruling lands — members-only, no numbers attached, gate check flipped accordingly.

**Accept when:** Andy+Eugene's rule recorded on this ticket · capped named list on chapter/roster asks · cap enforced in CODE · gate updated + GREEN.

---

### #97 · Brokered intros — message the person she recommends
**🟡 S2 · size M — filed 2026-08-19 · ⛔ BLOCKED: Andy's ruling ("lets think of it") + utility template**

> **In plain words:** after "you should meet X", one tap should start that conversation — without ever handing out phone numbers.

*As a member, when Mille recommends someone, I can say "connect us" — she asks THEM first, and only a yes opens the thread.*

Eugene, verbatim: *"It might be also cool to just have an ability to message the person that it recommends… it can just open up a WhatsApp thread with their number."* A wa.me link IS the number — never. The buildable shape: consent-first broker — Mille messages the target ("Eugene would like to connect about 3PL — ok?"), a yes shares the link both ways; outside the 24h window this needs ONE approved utility template.

**Accept when:** Andy's ruling recorded · consent flow live (no number leaves without the target's yes) · out-of-window template approved · declines are final and polite · gate GREEN.

---

### #92 · Event selection for a multi-event world — she must pick the RIGHT schedule
**🟡 S2 · size S — filed 2026-08-19 (Andy: "we connected singapore, but we will have more") · ⏸ builds when event #2's export exists**

> **In plain words:** with two events loaded, "what's on?" must answer about the right one — today she can't choose at all.

*As a member, my schedule, reminder and partner questions land on the event I mean — named or implied — never on whichever event happens to sort last.*

The whole event schema is already multi-event (everything keys on `event_id`; the loader loads any
export alongside). What is missing is CHOICE: the lane defaults to the latest-starting event and
the model never passes an event id, so a second export would silently steal every default answer.

**Shape of the fix:** resolve the event from the question when named (match against `event.events`
titles), else a default rule — nearest-upcoming, or the event the asker is registered for (Andy
picks which); reminders inherit the same resolution.

**Accept when:** a named ask answers about that event · an unnamed ask follows the ruled default ·
reminders anchor to the resolved event · Singapore behavior unchanged with one event loaded · gate GREEN.

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

### #72 · LOAD TEST before the Mille demo — 100 people at once, on a system that has never seen 6
**🔴 S1 · size M — filed 2026-08-07 (Andy: "in 2 weeks we present Mille, we might get 100 people using it")**

> **In plain words:** Olivia has never had more than five people message her in the same minute. In
> two weeks she may get a hundred, in a room, watching.

*As a member in that room, I message Olivia during the demo and get a normal answer in a normal
time — not a two-minute silence, not a holding message, not an error.*

**Measured 2026-08-07 — the gap between today's load and demo load is two orders of magnitude:**

| | today | demo |
|---|---|---|
| real member turns | **544 in 30 days** (963 more were eval traffic) | ~100 people, minutes |
| distinct askers | **35 in 30 days** | ~100 at once |
| busiest real minute ever | **5 turns** | plausibly 30–50 |
| minutes with ≥3 real turns | **19, ever** | continuous |

**We currently cannot measure the thing we are about to stress: `digest.olivia_messages.latency_ms`
is NULL on all 1,505 rows.** The column exists and nothing has ever written to it. Every latency
number we quote (median 22.8s, worst 56.1s, from #23) came from hand-timed staging probes, 8
questions. A load test without per-turn timing produces an anecdote, not a result — **fixing the
telemetry is step one of this ticket, not a nice-to-have.**

**Where it will break first — each of these is a hypothesis the test must confirm or kill:**
1. **n8n Cloud production-execution concurrency.** The limit for our plan is not written down
   anywhere. Past it, executions QUEUE: the member sees nothing, then everything at once.
   Related known ceilings: Code node dies at 60s, webhook cut at 100s.
2. **The holding ladder amplifies congestion.** Every turn slower than 18s fires extra executions
   (rung 1, then 60s rung 2) — so the system spends MORE capacity exactly when it has least. This
   is a feedback loop and it has never been tested under contention.
3. **Anthropic rate limits.** One turn = router + up to 5 tool rounds + the Haiku fact-gate. A
   hundred concurrent turns is a burst of several hundred calls; 429s inside the loop are untested.
4. **Supabase**: HNSW vector search per turn plus the PostgREST connection pool.
5. **Meta WhatsApp throughput** on the number, and the fact that every attendee must message FIRST
   (member-initiated) — so the arrival pattern is a spike, not a ramp.

**Shape of the fix**
- **Instrument first**: populate `latency_ms` on every turn, and record queue-wait separately from
  answer time — a queued turn and a slow turn need different fixes and look identical today.
- **A repeatable load script** (`scripts/olivia_loadtest.py`) firing N synthetic turns at STAGING at
  a controlled arrival rate, reusing the `SELFTEST` wamid convention so nothing reaches a real
  member and eval traffic stays separable. Ramp 5 → 25 → 50 → 100 concurrent; report p50/p95/max,
  error rate, and executions queued at each step.
- **Never at prod against real numbers** — the standing rule. Staging, or a dedicated test number.
- **Find the knee, then decide**: raise the n8n concurrency, throttle admissions with an honest
  "I'm busy, one moment" instead of silence, or cap the demo audience. The decision is Andy's; the
  number is this ticket's job.

**Accept when**
- `latency_ms` is populated on 100% of new turns, queue-wait recorded separately.
- The load script exists, is committed, and runs against staging on one command.
- p50/p95/max and error rate are reported at 5 / 25 / 50 / 100 concurrent, with the knee named.
- The holding-ladder amplification is measured at load, not assumed.
- Each of the five failure hypotheses is confirmed or ruled out **in writing**.
- A go/no-go for the demo with a number behind it — plus the mitigation if it is no-go.
- Gate GREEN (nothing here changes retrieval, but the run touches the live stack).

**⚠️ Flagged, not folded in — needs Andy's ruling.** A demo audience is not necessarily the member
roster, and identity hard-fails by design: `is_active_member_status()` gates all 20 RPCs, so a
non-member gets refused. **If Mille attendees are not in the Members DB, load is irrelevant — every
one of them gets a refusal.** Cheaper to check than the load test, and it decides whether this
ticket is even the right one. Cost is not a concern at this scale (~$0.007–0.01/answer, so 100
people ≈ $1), but #32's spike alarm should be on before the room fills.

---

### #73 · Connect the useful forms to Olivia — she reads 5 of 161
**🔴 S1 · size M — filed 2026-08-08**

> **In plain words:** 88 forms sync into Supabase every day. Olivia can read five of them.

*As a member, when Olivia answers about me she draws on everything I have ever told MDS on a form —
not just the census.*

**Measured 2026-08-08:** Typeform holds **187** forms · **88 sync to Supabase daily** ·
`digest.form_responses` holds **161 forms / 13,601 rows** · **Olivia reads 5 forms / 2,370 rows —
17%**. Every candidate below is ALREADY synced daily, so connecting one is a single row in
`digest.form_scope`, not an ingest job.

| form | id | questions | members | verdict |
|---|---|---|---|---|
| Prior Member – MDS Only Access | `VM6vgL` | 87 | 265 | **add** — full profile questionnaire, scanned clean of sensitive fields |
| New Member – MDS Only Access | `lDqob4vD` | 54 | 203 | **add** — same family, still recent |
| Membership Wrap-Up | `QR2XKFyx` | 7 | 75 | **add** — current; members describing their year |
| Centurion 20M+ | `IaKWKysS` | 3 | 95 | add — but its revenue answer is an EXACT figure and must stay band-only when spoken |
| MDS Summit Singapore Check-In | `w3kCjPAK` | 63 | 73 | ⛔ **HOLD** — see below |

**⛔ Why Singapore is blocked, and what it exposes about the model.** That form holds **42 passport
numbers, 43 passport expiry dates, 44 passport places of issue, 45 dates of birth, 44 home
addresses** and city/country of birth. `form_scope` is a **whole-form** switch: adding it would put
government IDs one RPC away through `my_form_answers` and countable in `form_stats`. Andy's standing
rulebook already puts address and government IDs in 🔴 NEVER. **`form_scope` needs question-level
scoping — an allowlist of refs — before any event form joins.** Roughly 15 of its 63 questions are
the business info actually worth having.

**Shape of the fix**
- Add the three clean forms to `form_scope` as `profile`; verify personas rebuild (the fingerprint
  should move on its own — confirm, do not assume).
- Extend `form_scope` with per-ref scoping, then admit Singapore's business questions only.
- Pin the Centurion revenue rule the same way `Most Recent Revenue` is pinned: informs silently,
  never spoken as a figure.

**Accept when**
- The three forms are readable by the owner lane and feed personas; 468 more members have profile
  answers reaching Olivia.
- Per-question scoping exists and is gate-checked; Singapore's passport/DOB/address block is proven
  unreachable by a canary.
- Centurion revenue proven band-only in a probe.
- Gate GREEN · counts before/after recorded.

---

### #74 · Identity: half of every form submission belongs to nobody
**🟡 S2 · size M — filed 2026-08-08**

> **In plain words:** 4,617 of 9,089 form submissions are not attached to any member, so whatever
> those people said cannot inform anything.

*As a member, what I filled in three years ago under a different email still counts as mine.*

**Measured 2026-08-07:**
- **4,617 of 9,089 responses (51%) are unstamped.** `stamp_form_responses()` matches on
  exact-unique **email only**.
- An email waterfall across all five known email fields (`Preferred Email`, Stripe, Gsuite, Slack,
  `members.email`) recovers just **75** more.
- **Phone is the real lever: 23 forms collect one, 3,927 responses carry one, 772 match a member** —
  roughly ten times what email adds, and `stamp_form_responses()` never looks at phone.
- **`Aliases` is populated but thin** — 2,379 members have the field, only **569** carry a variant
  that differs from the full name. "Mo Kuhail" has no "Mohamed Kuhail".
- **2,871 responses carry no identifier at all** — no email, no phone, no name, no hidden field.
  No matcher can ever resolve those; that is a capture problem, not a matching one.

**Design rule, from Andy 2026-08-07 — do not conflate these:**
- **Known names / emails / phones** = an internal MATCHING set. Never rendered, never spoken.
- **Preferred / display name** = how the member wants to be addressed. `Profile Name Cleaned`.
  Never fed from aliases. An alias reaching output is a defect, same class as showing a legal name.

**Shape of the fix:** a `member_identity` table holding every known email, phone and name variant
per member, populated from the Airtable mirror; `stamp_form_responses()` matches email → phone →
exact name, with fuzzy name requiring a second signal (city). Upstream: hidden fields or a required
identifier on forms we control, which is the only thing that touches the 2,871.

**Accept when** stamped share rises from 49% with the new signals counted before/after · no fuzzy
match applied on name alone · an alias never appears in output (gate check) · the unresolvable
remainder is stated in writing rather than chased.

---

### #76 · New eval bank — 100 questions from real member traffic
**🔴 S1 · size M — filed 2026-08-10 · ⚠️ RESIZED 2026-08-16 (Andy: "We need to keep our question bank at 100 relevant questions. not 30, not 220. 100"). The original 150 target is superseded — 100 is the standing number.**

> **In plain words:** The bank should be what members actually ask, not what we imagined they would.

*As the owner, the quality number I trust is measured on real questions, so improving it improves the product members touch.*

**Where we are:** nightly eval runs 220 judged, **7.7% fail (Aug 9), 6.8% (Aug 8)** against a <1%
target. Andy 2026-08-10: **7.7% is acceptable for now** — the bank is the priority, not the rate.
Six questions failed both nights (Q2090, Q2096, Q2110, Q2130, Q2138, Q2142) so there is a real
persistent class inside that number, but the instrument is what gets rebuilt first.

**Source material is already there:** 1,513 member turns in 30 days · 544 of them real (the rest
eval traffic) · 35 distinct askers · `digest.olivia_question_labels` classifies each one · the 6 👎
in `olivia_feedback` are the highest-value rows in the whole dataset.

**Rules that hold (standing):**
- **ORGANIC only.** Generated questions may only deepen a pattern that already appeared organically,
  and only if necessary.
- **Retirement is part of it** — a bank that only grows stops being an instrument. `retired: true`,
  canary floor 3 per class.
- **Snapshot before and after** into `eval_bank_snapshots/` — `mds-scorecard-tools` has no git.
- **Class coverage preserved**: AT_PROFILE · CROSS · DECLINE · EVENT · FB · FORM · GEN · PARTNER ·
  REAL · VIDEO · WA_DIGEST · WA_RAW.

**Accept when** **100** questions, every one traceable to a real member turn (phone + wamid + date) ·
every uncleared 👎 included · ground truth written from the warehouse, not from Olivia's answer ·
class distribution matches real traffic rather than the old bank's shape · the retired set named
with its reason · one baseline run on the new bank, its rate recorded as the new starting number.

#### ✅ CLOSED 2026-08-19 — done since 08-16/17, the board row was never flipped (Andy caught it)
**The build (2026-08-16):** `eval_bank_100_2026-08-16.json` — in GIT at the repo root (stronger
than the snapshot rule it replaced; a copy now also sits in `eval_bank_snapshots/`), built by
`scripts/build_eval_bank_100.py`, fired by `scripts/run_eval_100.py [--staging]`.

| AC | result |
|---|---|
| exactly 100 questions | ✅ 100 (verified today by direct count) |
| traceable to a real member turn | ✅ every row carries `asker` + `first_asked` (27 members, 07-18..08-16); the wamid join lives in the builder via `olivia_question_labels` — names+dates on rows, not raw wamids |
| every uncleared 👎 included | ✅ per the 08-16 build; the 27 regression rows all pass |
| ground truth from the warehouse | ✅ `expect` written from live facts (08-16 session: "facts verified live") |
| class distribution matches real traffic | ✅ 11 classes from the labels taxonomy (PEOPLE 18 · SAFETY 14 · CONTENT 12 · VIDEOS 9 · STATS 9 · CHAPTERS 8 · CAPABILITY 8 · EVENTS 7 · PARTNERS 7 · FRESHNESS 4 · PROFILE 4) |
| retired set named | ✅ retirement mechanized (`retired: true`); the superseded 150/212 banks named in the snapshot README |
| baseline run recorded | ✅ 2026-08-17: **96% clean, 27/27 regressions pass** — the standing start number |

**Before → after:** 220-question inherited bank at 7.7% fail → 100 organic questions, baseline 96%
clean. **Note kept separate:** the pre-announcement re-run of the 100 against prod is
announcement prep / sprint-close, not this ticket.

---

# 🟡 S2 — NEXT

### #18 · How-MDS-works answers
**🟡 S2 · size M · ⏳ UNBLOCKED 2026-08-19 — first slice BUILT + STAGED + PROVEN, awaiting promote**

> Was blocked 2026-08-05 ("we dont have data"). **Andy delivered the first three team documents
> 2026-08-19** and the org knowledge library shipped around them.

#### ✅ FIRST SLICE LIVE 2026-08-19 — prod `f3850dd7` (promoted on Andy's order; prod probes: refund cited per the FAQ, chapter ask honestly doc-less)
**The build:** `digest.docs` + `doc_entries` (migration `org_docs_library_20260819`) — audience
FAIL-CLOSED to staff, event scoping, supersession, tsv GIN, voyage-3.5-lite/1024 · loader
`scripts/load_org_docs.py` (heading FAQs, three-column table FAQs with measured column bands, SOP
sections; dry-run review; dedup keeps longest) · **first load: Summit FAQ 20 qa (member) · Ticket
Requests FAQ 18 qa (member) · Chapter Assignment SOP 9 sections (STAFF — dark to members)** ·
`/api/olivia/kb` lane (hybrid RRF: cosine + tsv-with-OR-fallback; **similarity floor 0.45,
measured**: legit 0.55–0.69, strays 0.41, off-corpus 0.37; degradation is loud; empty is honest) ·
`org_docs` tool wired into `Answer Tool` dispatch + seed rule (policy from documents, numbers from
structured tools, cite the document).
**Fixed on the way:** empty-corpus 5-min cache poisoning (stale PostgREST worker) · websearch AND
missing natural questions · silent vector-lane death — **VOYAGE_API_KEY added to the Render env by
Andy** (it had never existed there; only Mac scripts and n8n ever called Voyage).
**Probes through Mille (staging):** refund policy quoted + cited *"straight from the event FAQ"* ·
kids answered *"per the event FAQ"* · chapter ask → *"no written team document"* — the staff SOP
correctly invisible + honest-empty rule live. Off-corpus canary ("what colour is the moon") →
honest empty. Gate exit 0.
**Andy's phone test found the shape of the next problem (2026-08-19):** the chapter question got
"no written documentation" + an OFFER to "explain the assignment process in detail" — an offer she
could only fill by inventing. Fixed both ways, promoted `4725e6f1`, prod-verified: ① seed rule —
an empty org_docs result forbids offering a detailed explanation (report offer only); ② the
member-safe half of the staff SOP became a CURATED doc — `docs/org_docs/chapter_assignment_member_faq.md`
(in git, Andy-approved), loaded as member FAQ #4 (3 qa). Prod now answers "per the Chapter
assignment FAQ": by-address assignment · $1,200/yr additional chapters + criteria + chapter@mds.co
· Women's Chapter non-geographic. The SOP itself stays staff-dark and unnamed. **The pattern for
every future SOP: internal doc loads staff, a curated member digest goes in git, Andy approves.**
**Remaining for full close:** more team docs as they arrive (the ACs want EVERY recurring
question covered) · "they stop arriving as support requests" is measured over time, not tonight.

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

### #71 · "Virtual event", "call", "recording" — three words, three systems, two contradicting answers
**🔵 S3 · size M — filed 2026-08-07 from Andy's own WhatsApp session (18:11–18:13 local)**

> **In plain words:** Andy asked for the last virtual event and got February. He asked for the last
> Mogul Call — the same kind of thing — and got August. Both in the same breath, both confident.

*As a member, when I ask about a call, Olivia knows whether I mean the session that happened, the
recording of it, or the one coming up — and she never gives me two different "latest" answers in
one conversation.*

**The transcript (verbatim, 2026-08-07):**
- *"what was the last vitrual event"* → **"The most recent virtual event on record is the Mogul Call
  with Peter-Paul Maan, held Wed Feb 4, 2026."** Plus: *"our live events calendar isn't fully
  connected here yet, so there could be newer virtual sessions."*
- *"and what was the last mogul call"* → **"The latest Mogul Call … was published August 5, 2026:
  … with Dorian Gorski"** (restricted, so she fell back to Guido Reyes, July 29).

**Measured 2026-08-07 — the calendar is NOT disconnected, the lane filters it out:**
`digest.events_catalog` holds **"Mogul Call with Dorian Gorski", event_type Virtual, 2026-08-05**.
The right answer was one row away. But of **634 Virtual events, 615 have `phase = NULL`**; only 8
are `Registration Open` (newest **2026-07-15**) and 8 `Confirmed` (newest 2025-10-23). The events
lane surfaces the phase-stamped slice only (#60's browse rule), so a **past-tense** question got
answered from a set built for **upcoming** browsing → February.

**Three systems describe the same real-world thing, and nothing says which is authoritative:**

| System | What it holds | Latest mogul call |
|---|---|---|
| `digest.events_catalog` | the scheduled event (Airtable + app) | 2026-08-05 Dorian Gorski |
| `digest.videos_catalog` | the published recording | 2026-08-05 (restricted) |
| `digest.calls` (#70) | the Zoom meeting itself — 33 mogul, 38 channel, 6 expert, 4 chapter | 2026-08-05 |

**Two defects, one root:**
1. **The contradiction** — whichever word the member happens to use decides which system answers,
   and the systems disagree by six months.
2. **The false excuse is worse than the wrong date.** *"our live events calendar isn't fully
   connected here yet"* is not true. She invented an infrastructure explanation for her own filter,
   and offered to file a report about it. A member would repeat that to the team.

**Shape of the fix (structural, not a prompt line):**
- **Write the vocabulary down first — this is the ticket's real deliverable.** What IS a virtual
  event vs a call vs a recording; which of the three is authoritative for *when it happened*, for
  *what was said*, and for *how to attend*. Needs Andy's ruling; the rest follows mechanically.
- **Tense decides the source, not the noun.** Past-tense ("last / most recent / was there a")
  answers from what actually happened; future-tense answers from the browse set. Today `phase` is
  doing both jobs and only works for one.
- **One answer per real-world thing.** The Aug 5 Dorian Gorski call is one event with a recording,
  not two competing rows — join the three systems on the call the way #70 already joins video ↔ Zoom.
- **A restricted RECORDING must not hide the EVENT.** The event is on the public events page; only
  its content is restricted. Today the restriction on the video pushed the answer back to July 29.
- **Ban the fabricated infrastructure excuse.** If a lane filtered something out, she says she is
  not sure, never invents a reason about our plumbing.

**Accept when**
- The three terms are defined in the handbook, with the authoritative source named per question type.
- "What was the last virtual event" and "what was the last mogul call" return the **same** call on
  the same day — proven on both phrasings, plus "what's the next virtual event" still answering
  from the upcoming set.
- The 615 phase-less virtual events are reachable for past-tense asks, or ruled out in writing.
- A restricted recording no longer suppresses its event; the event is named, the content is not.
- No answer claims a system "isn't connected" unless a health signal says so.
- Gate GREEN · matrix rows added for both phrasings and the restricted-recording case.

---

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

#### 2026-08-07 — COVERAGE MEASURED, then two defects fixed (Andy: "are we processing all 80ish questions")
The honest count was **64 of 96** census-2026 questions answerable and correctly labelled. Two
defects, both fixed and proven:
- **① 13 matrix rows had no question at all.** Typeform sends matrix rows with `"q": ""` — the
  question lives on the matrix parent — and the loader only recursed into `group` fields, so
  form_stats aggregated them into labels like `" — Inhouse" 64.2%`. A percentage with no question
  attached is a wrong-answer generator, not a gap. `sync_form_responses.fetch_titles` now composes
  the two (`How do you handle each of these areas? (Bookkeeping)`), re-synced across all 64 forms:
  **0 blank labels in 125,014 rows**, the legacy census matrix rows picked up labels too.
- **② Two questions were killed by a false positive in the PII filter.** The exploded view drops
  any question whose text matches `website`, which caught *DTC / your own website* revenue share
  and the *MDS systems UX rating* — 837 answers across 3 forms. Numeric answers now bypass the
  text heuristic (a number cannot be PII), and **the same pass closed a real leak: phone_number
  and url answers were reaching the stats layer** (20 refs, raw phone numbers and LinkedIn URLs) —
  those types are excluded outright now.
- **Follow-through:** composing the matrix label put "Email" into a legit topic, so
  "what's Sherman's email" began matching a marketing stat (no PII, but nonsense). Identity words
  are now query-side stop-words in `form_stats`; topical asks still resolve.
- **Tool pick:** the data alone did not answer — a probe for bookkeeping/customer service came back
  from chat anecdotes. The census topic map in the form_stats description now names the matrix and
  rating topics (`apply_20f_matrix_topics.py`, staging `4b851e05`).

| | before | after |
|---|---|---|
| census-2026 questions askable + correctly labelled | 64 / 96 | **79 / 96** |
| blank question labels, whole warehouse | 13 refs | **0** |
| phone/url answers in the stats layer | 20 refs | **0** |
| QA sweep | 1,857 checks / 0 fails | **1,872 checks / 0 fails** |
| leak gate | 232 exit-0 | **232 exit-0** |

The remaining 17: **13 free-text** (P2 — blocked on Andy's exposure ruling) + **4 PII by design**
(email, phone, full_name, brand_names). Staging probes: bookkeeping **61% in-house / 36% agency**
census-led then chat color (SQL 60.7 / 36.1) · DTC **median 5%, avg 15%** median-first. SQL kept in
`scripts/sql/` (partial answer to #65). ⚠️ A concurrent Trend-Report session added
`digest.form_scope` mid-session, pinning Olivia to the 5 profile forms — Olivia's answers unchanged.

#### 2026-08-07 (later) — AC③ CLOSED: personas read the FORMS warehouse, and keep themselves current
Andy: *"we need to wire it to forms, not just census… if several forms impact the same question we
must use the latest one — e.g. revenue constantly changing."*

**Why it had never happened:** connecting a source to personas takes TWO edits and the census had
neither. `persona_signal_fingerprints` decides WHEN a persona rebuilds (it hashed only
`member_attributes.refreshed_at`, Olivia questions, event attendance, FB posts — so filling in the
census left the hash identical and no rebuild fired) and `persona_signals` decides WHAT the
derivation sees (a forced rebuild would not have shown the answers anyway).

**① The dictionary first.** `form_windowed` already does latest-wins (`distinct on (member_at_id,
canonical_key) order by submitted_at desc`) but can only unify fields that SHARE a canonical key,
and only **22 of 284** keys spanned more than one form. Two mapping passes — A mechanical
(identical wording after normalising), B read by hand (the marketing matrix, the ops matrix, UX
rating, benefits rank, competitive advantage, industries) — took it to **55 of 247**;
`form_field_map` 27 → 78. Deliberately NOT merged, axis differs: pay bands (2026 seniority vs
legacy named roles) · manufacturing · selling focus · employees · EOS. Two pass-B refs written from
a truncated listing matched nothing and were caught by a guard query — silent no-ops, now in the file.

**② The wiring.** `persona_signals` gained `self_reported` (own latest answer per canonical field,
every profile-scope form, free-text excluded pending the P2 exposure ruling) and the fingerprint
gained a forms term, so a new submission now marks that member stale on its own. Personas stay
owner-scoped — `member_dossier`, `member_dossier_v2` and `multi_source_v2`'s `me` block all resolve
to the ASKER — which is what keeps this inside "silent personalization fine, raw answers owner-only".

| | before | after |
|---|---|---|
| canonical keys spanning >1 form | 22 / 284 | **55 / 247** |
| personas drawing on forms | 0 | **462 of the 489 members who have answers (94.5%)** |
| persona_signals payload | 21.8k chars · 2.4s | **14.3k chars · 0.5s** |
| full rebuild wall-clock | 5h (29s each, serial) | **~50 min (5 workers)** |
| rebuild result | — | **752 rebuilt · 0 failed · 0 missing · 0 stale** |

**Three pre-existing bugs found by doing it:** `max_tokens: 3500` truncated the richest members'
JSON mid-object and the parser could only say "no valid JSON" — that was the standing *missing: 3*
(now 6000) · the builder was fully serial · `sb()` returns `[]` on an empty curl response, which
reads as "this member has no signals" with no retry — at 8 workers the pool saturated and **228
members were skipped as if they had no data**. Retry-with-backoff added, workers 8 → 5.

Sample, unprompted: *"Runs lean (4 FT staff), handles bookkeeping/CS/listings in-house, outsources
creative/design"* · *"9 FT + 8 PT staff + 5 VAs across Eastern Europe, Western Europe, China,
Pakistan… ~200 containers annually"*. Revenue figures still absent per the standing rule.

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

### #91 · She is Mille — identity across all five reply surfaces
**🔴 S1 · size S — filed AND built 2026-08-18 (Andy: "make her reply to Mille")**

> **In plain words:** the assistant got a name the same night its number did — she introduces herself as Mille and answers when you call her that.

*As a member, the assistant I talk to is Mille — she says so, and she responds when I address her by name.*

The product was named tonight: display name "MDS Mille" submitted to Meta (PENDING_REVIEW, watcher
`a1ViYr5FT7iePdN9` alerts on the ruling). Five surfaces carried "the MDS AI Assistant": the system
identity line (`Build Prompt` + `Answer Seed`), the three unidentified/inactive greetings
(`Build Generic`), and the #79 curated intro + beta blurb (`Build Verbatim Digest`).

**Accept when:** the intro leads with Mille · "who are you"/"are you Mille" answer as Mille on both
the help and LLM lanes · the say-you-are-an-AI honesty clause survives · NO-member-names rule
survives (renamed from "no names" — she has one now) · `node --check` on every changed node ·
gate GREEN.

#### ✅ LIVE 2026-08-19 — prod `aec2db47` (promoted with #88; prod probe: intro leads *"Hi 👋 I'm \*Mille\* — the MDS AI assistant."*)
**The fix:** `scripts/olivia_loop/apply_91_mille_identity.py` — exact-string replacements on the
five surfaces, apostrophe-free additions, `node --check` per node, one PUT, one bounce.

| AC | result |
|---|---|
| intro leads with Mille | ✅ staging probe (help route): *"Hi 👋 I'm \*Mille\* — the MDS AI assistant."* |
| answers to the name on the LLM lane | ✅ "mille, are you there? whats your name?" → *"Hey Andy, yep I'm here! 👋 I'm Mille — your MDS AI assistant."* |
| AI-honesty clause survives | ✅ identity line keeps "If asked, say plainly that you are an AI assistant" verbatim |
| no-member-names rule survives | ✅ comment renamed to "NO MEMBER names"; member-name rules untouched |
| node --check every changed node | ✅ 4 nodes, all OK before the PUT |
| gate GREEN | ✅ exit 0 · probe rows cleaned |

**Before → after:** "I'm the MDS AI assistant" (nameless) → named Mille on all five surfaces;
old identity string verified gone on re-read. Staging `273253bc`; prod untouched.
**Andy: promote when ready** (`python3 scripts/olivia_wf.py lock` → `promote`). Note: until Meta
approves "MDS Mille", the WhatsApp header still shows "MDS AI Assistant" next to her saying Mille —
promote now or after the name flips, your call.

---

# ❓ Open questions for Andy

- **(2026-08-11, found working #75 — flagged, not chased) Your `digest.members` row lost
  `channels_present` sometime after Aug 10 00:43** (the #77 gate ran green on it then; today it is
  `[]`, which both empties your own digest lanes and aborts the leak gate's default probe — this
  session's gate ran as Ian instead, 246 exit-0). 49 rows total sit empty, incl. 2 real members.
  The writer is the upstream digest/roster sync (WA digest project, not Olivia). Who should fix it,
  and is a ticket wanted here or there?

| Question | Why it matters |
|---|---|
| **#89 — Airtable data only you can fix:** ① 4 speaker roster rows link to **Max Mikhaylenko's** member record (Ephraim Ausch, Meher Patel, Jeremy Allen, Scott Deetz) ② dup member-record pairs: Brian Williams, Henrik Fjerdingen, Rebeca Rosas, Ryan Bastuba, **Eugene ×9** ③ the standing 151-vs-108 ruling (all tickets vs confirmed members — which number does a member hear?) | ① mis-attributes four speakers' registrations ② each dup splits one person across two ids in every join ③ the last "same question, same number" gap — single SOURCE is now enforced, the FILTER is a product call |
| **#90 — should Accelerator and MDS 2026 New Members be verification-gated?** Both carry a `required_form` in Airtable but are ungated in the mirror (curated field, deliberately not flipped by me) | If yes, Olivia currently hands their raw invite to anyone who asks instead of the form. One-word change each once ruled. |
| **#70 — how sensitive is a call transcript?** `public` to members like the video already is, or does some class need `restricted`? | **Blocks #70's build.** Members speak candidly about their businesses on these calls; the access rule decides what `content_search_v2` may return. Same shape as #20's exposure ruling. |
| **#70 — may Olivia say WHO attended a call?** | `event_who` sets precedent for registered events, but Zoom attendance is unregistered and name-matched at 67% confidence — a wrong name is a wrong claim about a member. |
| **#70 — does this supersede #36 (Circleback)?** | Both are "meeting notes become a source". Zoom already gives speaker-labelled transcripts for 2026; #36 stays blocked on details we may no longer need. |
| **Does an event description/agenda field exist** in Airtable or GroupOS that we are not syncing? | Decides whether event "fit" in #29/#50 is real or inferred from attendees. **#70 partly answers this** — a transcript is the richest description a call has. |
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

### #89 · Two rosters disagree about who is at our own event
**🔴 S1 · size M — filed 2026-08-18 · closed 2026-08-18**

> **In plain words:** ask how many people are coming to the Summit and the answer depends on which lane happens to run.

*As a member, whatever I ask about who is at the Summit, I get one number — the true one.*

**Accept when:** the 7-person gap is explained row by row, not estimated · one roster answers "who is
coming" and the other is documented as ticketing-only · a member asking the same question two ways
gets the same number · gate GREEN.

#### ✅ CLOSED 2026-08-18 — gap explained to the last name; single count source verified + documented; loader matching rebuilt
**The diagnosis changed the ticket twice.** ① The feared two-number split does not exist
structurally: **zero `digest.*` functions read `event.attendees`** — every member-facing count
already comes from the registrations ledger; the schedule endpoint only gates rooms and matches
people, it emits no headcount. ② The gap is not attendance — it is **identity**: the same humans
sit on both rosters under different member records.

**The row-by-row ledger** (156-vs-149 compared live-ticket ROWS to distinct PEOPLE; the real
member-level diff was 121 vs 124, overlap 109):
- **4 speaker registrations mislinked to Max Mikhaylenko's member record** in the AT roster
  (Ephraim Ausch, Meher Patel, Jeremy Allen, Scott Deetz) — one bad link, five people wrong.
- **4 duplicate member-record pairs**: Brian Williams, Henrik Fjerdingen, Rebeca/Rebecca Rosas,
  Ryan Bastuba — registrations link one record, the export the other. **Eugene is a nine-record
  cluster** ("Eugene Khayman" ×2, "Yevgeniy Khayman" ×2, "Euge khay"…).
- **Courtney Lee's export row was linked to a Members-DB record named "Test Test"** (it owns
  courtney@mds.co).
- **26 attendee-people carried no member link at all** — GroupOS emails differ from Members-DB
  emails (Eugene, Jonathan Jesper, Lee Lim, Ryan Bastuba, Steven Zhou, Kal twice…).
- True absences from the Aug-17 export: **Sheng Zheng + Ginny Lo ordered after the cut**, six more
  (Mayank, Fahim, Vincent, Krishna, Shaurya, Brianna) await the fresh export already asked of the dev.
- Att-only legits: manually-added speakers/guests/staff without member tickets, plus junk
  identities ("Andy (test)", "MDS Community", "TK DecodeUp").

**The fix:** `load_event_graph.py` member matching rebuilt as a conservative three-rung ladder —
exact profile email → registration-ledger email bridge (rejected when several emails claim one
member id: the Max signature, or on a name-token mismatch) → unique full-name; a rung-1 hit whose
profile names someone else falls through instead of linking (the Test-Test class); suspects logged,
never guessed. Two of my own bugs caught in dry-run: the profile fetch trusted one request
(PostgREST hard-caps 1000 rows — the memory literally warns this) and the name guard vetoed
NULL-named profiles. Authority documented **in the schema itself**: migration
`event_roster_authority_comments_20260818` stamps `event.attendees` "ROOM ROSTER, NEVER A
HEADCOUNT", `event_registrations_live` "THE member-facing attendance source". `db/` re-exported.

| AC | result |
|---|---|
| gap explained row by row | ✅ every name accounted for (ledger above) — identity faults, export lag, manual adds; nothing estimated |
| one roster answers "who is coming", the other documented | ✅ inverted from the filing but true: registrations_live = counts (verified: 0 digest fns read attendees), attendees = gating/matching — stamped as table comments |
| same question two ways = same number | 🟨 single SOURCE now guaranteed + documented. The remaining split is one FILTER ruling inside registrations — `event_lookup` 151 all tickets vs `event_who` 108 confirmed members — **Andy's product call, flagged since 2026-08-12, re-flagged below** |
| gate GREEN | ✅ exit 0 |

**Before → after:** people matched to a member 124 → **170 of 199** (email 165 + registration
bridge 2 + unique name 3); attendee-members 124 → 127; overlap 109 → 110; Courtney freed from
"Test Test"; unlinked attendee-people 26 → 23 (orgs/vendors + nickname cases Kat/Chip + Eugene's
dup cluster — all named, none guessed).
**Andy's list (data he owns):** re-link the 4 speaker roster rows off Max's record · merge or mark
the dup pairs (Brian, Henrik, Rebeca, Ryan, Eugene ×9 — NEVER deleted by me, rule) · the 151-vs-108
ruling · fresh export covers the last 6 + late orders.

### #90 · The chats mirror stopped syncing — she hands out dead invite links
**🔴 S1 · size S — filed 2026-08-18 · closed 2026-08-18**

> **In plain words:** a member asks to join a chat, taps the link she sends, and it doesn't work.

*As a member, every link Olivia gives me opens the thing it says it opens.*

Live on prod 2026-08-18, closing a weekly-digest answer: *"Open the chat:*
`https://chat.whatsapp.com/H6TszwtiJ2SEk1FRIc5pEb`*"* — dead. WhatsApp had regenerated the invite;
Airtable had the current one the whole time. Every `digest.chats` row carried `updated_at
2026-07-29`; measured that day as 29 AT chats vs 19 mirror rows, 3 invite links wrong (those three
hand-fixed for the demo).

**Accept when**
- `digest.chats` matches Airtable on count and on every `invite_url`, proven by a diff, not a glance.
- The sync runs on a schedule and `updated_at` moves.
- **Staleness alarms** — tools-health flags it when the newest row ages past its cadence, the way an
  Airtable-freshness check already works elsewhere.
- Gate GREEN.

#### ✅ CLOSED 2026-08-18 — mirror built, first run proven, alarm wired
**The diagnosis changed the ticket:** the sync did not stop — **it never existed.** `digest.chats`
was a ONE-TIME hand load from the pilot's Channels .xlsx on 2026-07-29 (every row one timestamp, to
the second); no workflow, script, or Action ever wrote it again. The "29 in Airtable" counted 13
inactive junk rows (Milan/Inspire event chats, dups, "Whapi test" — all linkless); the true source
set is **18 active chats**, and the mirror even held a 19th ghost ("MDS TikTok +1M TTM") that exists
in no Airtable row at all.

**The fix:** n8n **`RpEbU47SpMVsbwqg` "MDS WA Digest - Supabase Mirror (Chats)"** — hourly, the
exact sibling of the Members/Summaries mirrors: AT search `{active}=1` → map → upsert
`merge-duplicates` → delete rows not in the active set → heartbeat. Airtable owns the LINK fields
(invite, zoom, opt-in, verification-form URL, chat_id); `verification_required` /
`requirement_text` / `call_schedule` / `moderators` are curated, absent from the payload, untouched.
Two guards: <15 rows from AT → throw (a flaky read must never become a mass delete); any failure
skips the heartbeat so the alarm pages.

| AC | result |
|---|---|
| matches Airtable on count + every invite_url, proven by diff | ✅ field-by-field diff vs a fresh AT pull: **18 = 18, DIFFS: 0** (invite, zoom, opt-in, verification form, chat_id all byte-equal) |
| sync on a schedule, updated_at moves | ✅ first tick exec **86853** (23:30:46 UTC, 3.6 s): 18 upserted, ghost deleted, all 18 rows stamped — after three frozen weeks. Schedule flipped 5-min → hourly after the proof, single bounce |
| staleness alarms | ✅ heartbeat `chats_mirror` (`max_age_hours: 3`) in `digest.olivia_job_heartbeats` — **signal 4** on the existing 5-min pg_cron alarm covers it; one freshness pattern, as filed |
| gate GREEN | ✅ exit 0 (checked as exit code, not tail) |

**Before → after:** frozen since 2026-07-29 / 19 rows incl. 1 ghost / 2 stale opt-in forms +
1 changed SEO zoom undetected → hourly sync, 18 = 18, diff 0, 3-hour alarm.
**Named remainders:** the mirror also FIXED live drift the hand-patch missed (Large SKU + Resellers
opt-in forms, SEO zoom, Under-30 zoom). Flagged for Andy, deliberately not flipped by me:
**Accelerator and MDS 2026 New Members carry a `required_form` in Airtable but are not gated in the
mirror** — if they should verify like Centurion/TikTok, that is a one-word curated change each.
FB image capture (the ticket's "related" note) stays open — different pipeline, not this ticket.

### #87 · "Who should I meet" returned people who aren't going
**🟡 S2 · size S**

> **In plain words:** she recommends people to seek out at the Summit who aren't attending it.

*As an attendee, when I ask who to seek out at this event, everyone she names is actually there.*

Twice, on Andy's own phone. First: Steve Parisi, Ryan Mayberry, Dan Schaefer, Garland Sullivan and
others with genuine reasons — **4 of the 8 checked had no attendee row.** Then, worse: asked *"who
should I meet on summit?"* she opened with *"nobody registers for a session, so I can't tell you
who'll be in a given room"* and answered a **people** question with a **list of sessions**.

#### ✅ BUILT + PROVEN + PROMOTED 2026-08-18 — prod `74f0572a`
**The fix:** a `people` op on the schedule endpoint. Everyone returned holds an attendee row for
THIS event; matching is on the asker's own expertise and categories (or topics passed in `q`), and
the reason is the overlap itself. Commits `ccdf31b`, `8fcae8e`.

| AC | result |
|---|---|
| every person named has an attendee row | ✅ **7 of 7** — Alex Bonilla, Neeme Roos, Brandon Himmel, Daniel Meredith, Louisa Li, David Stark, Mo Kuhail, checked against `event.attendees` |
| a member asking with no event in mind still gets the unfiltered match | ✅ the members lane is untouched |
| never claims someone will be at a session | ✅ the response carries it explicitly, and it is a footnote not an opener |
| no "I can't" opener | ✅ leads with names |
| gate GREEN | ✅ passed inside the promote |

**Before → after**, same question, same phone: **4 of 8 not attending → 7 of 7 attending.**

**Two flaws caught in testing:** Alex Bonilla appeared twice because he holds a Speaker row *and* a
Member row (now merged, shown as "Member + Speaker"), and splitting topics on `&` and `/` shattered
*"Health/ Beauty/ & Supplements (Consumables)"* into three fragments that read like debris.

**Remainder:** 143 of the attendees resolve to a member record and 101 carry expertise, so a
newcomer with a thin profile matches on little. Not fixed, and not worth fixing until it bites.

---

### #85 · 🚀 Summit schedule — she had no idea what happens at our own event
**🔴 S1 · size L**

> **In plain words:** a member at the Summit asks what's next, where it is and who's speaking, and gets the real answer — in Singapore time, with a map.

*As an attendee, I ask Olivia anything about the schedule and she answers from the schedule.*

She had **no schedule at all**. Every Summit answer came from people talking *about* the event — Eugene Khayman's Facebook announcement, Charles Chakkalo's walkthrough — or from `events_catalog`, whose `start_at` holds a Singapore wall-clock stamped as UTC. Live on prod 2026-08-17: *"The main Summit kicks off Sunday, Aug 23 at **6:00 AM** local time"* (eight hours wrong) and *"the first standalone activity I can see is the **Women's Lunch**"* — which is Staff-only and should never have been offered to a member.

**Shape of the fix:** a real schedule in the warehouse, and the visibility rule written once outside the database.

**Accept when:** next / where / who speaks / whole day / speaker roster all answer from the schedule · audience respected per member · times are true instants in the venue's zone · addresses + map links · refuses honestly · gate GREEN.

#### ✅ BUILT + PROVEN + PROMOTED 2026-08-18 — prod `d6761eb4`
**The fix:** new **`event` schema** — 15 tables, 25 FKs (5 composite so a child can never point at a parent in another event), **no views, no functions**; policy lives outside the DB (Andy's ruling). Loaded from the GroupOS export by `scripts/load_event_graph.py`. The lane is **`POST /api/olivia/schedule` in mds-digest-web**, not an RPC — `Answer Tool` gained one URL branch for `event_*` tool names, no new nodes. Migrations `event_schema_20260817`, `event_composite_fks_and_grants_20260817`, `event_people_member_fk_20260817`.

| AC | result |
|---|---|
| next / where / who speaks / whole day / roster answer from the schedule | ✅ 10 ops live: `agenda · next · day · where · speaker · speakers · recommend` (+3 reminder ops in #86) |
| audience respected per member | ✅ **plain Member day one = 6** (Brian Williams); **Women's Lunch grantee = 7** (Kimberly Cruickshanks); Staff-only rows never surfaced |
| times are true instants, rendered in the venue's zone | ✅ *"Welcome Dinner — Sun 23 Aug, 7:00 pm Singapore time"*; loader stores instants, keeps raw strings in `source_*` for audit |
| addresses + exact map links | ✅ 18/18 locations carry address + lat/lng + `place_id`; links are place deep-links, not text searches |
| refuses honestly | ✅ *"no activity matching that name is on this person's schedule"* · Pre-Event Dinner (Staff + 36 grantees) correctly withheld · *"I don't have a distance figure — the schedule tool gives addresses and map links, not travel distances"* |
| recommend by subject, never popularity | ✅ *"TikTok"* → 3 sessions with their own subject lines and speakers; **31/31 sessions carry a complete `short_description`**, 30/31 have every speaker resolved to a real member |
| gate GREEN | ✅ PASSED inside both promotes (`58b4ed37`, `d6761eb4`), snapshots either side |

**Before → after**, same question, same phone:
| | before (prod `5a12a2d1`) | after (prod `d6761eb4`) |
|---|---|---|
| *when is the first workshop* | *"Per Eugene's breakdown, deep dives fall on Monday — I don't have an exact clock time"* | *Deep, Dive, & Dash & Workshops — Mon 24 Aug, 10:20 am Singapore time, Grand Ballroom · Alex Bonilla, Brandon Himmel, Jonathan Jewett* |
| *where is the Welcome Dinner* | not found | *Pool, Ritz-Carlton · Sun 23 Aug 7:00 pm · address + map* |
| *where is Junior Ballroom 1* | *"doesn't show up on your schedule"* | *the Ritz-Carlton, Marina Bay — 8 sessions run in there* |

**Six bugs found by probing, five of them mine:** a tool declared with `args` instead of `input_schema` (broke the answer loop — `node --check` passes because it is valid JS and the wrong *shape*) · `Object.assign` on a JSON **string**, which destroyed `op`/`q` and made the model look wrong when it had sent the right call all along · exact-substring matching that missed *Pre-Event* and *Check-in* on a hyphen · a location swallowing a room query · a string-surgery reorder that nested the venue branch inside the room branch · the `q`-fallback swallowing ops that own their own `q`. **The lesson twice over: code beats instructions** — two rounds of prompt rules chased a symptom that reading the execution settled in one call.

**Remainders, named not buried:** two rosters disagree (156 registrations vs 149 attendees) · CÉ LA VI missing from the export, so some of the 13 venue-less activities may be export gaps · long descriptions truncated at 201 chars · Brandon Himmel's Aug 26 session is orphaned, so invisible to everyone · `member_match` doesn't know about `event.attendees` · 5 of 20 probe questions unfired (13, 14, 15, 17, 18) · the date-first layout is committed both sides and unverified.

---

### #84 · Pre-announcement answer quality — four defects a real member could hit

**🔴 S1 · size M — filed + shipped 2026-08-17 · ✅ LIVE prod `5a12a2d1`**

> **In plain words:** One week before the announcement, four things she said were wrong or
> unusable. Two of them a real member had already hit.

*As a member, when she cannot answer something I want the real reason, not an invented one — and
when she can answer, she should not tell me she cannot.*

**Found by:** the 30-question smoke (`OLIVIA_SMOKE_2026-08-14_BANK.md`) and the 100-question run.

| | defect | root cause | fix |
|---|---|---|---|
| **D1** | "what chapter should i join" answered with WhatsApp chats; the correction repeated it byte-identically | **the router had no chapter lane** — "chapter" appeared nowhere in its prompt, so the question matched `chats` ("which they could join") | CHAPTER IS NOT A CHAT rule at the top of LANE PRECEDENCE; chapters route to `community`, which already reached `chapter_info` |
| **D2** | "full transcripts aren't something I have access to (that capability isn't live yet)" | **the Answer Seed contradicted itself** — a pre-#70 rule 38 lines from #70's own "2026 calls carry full transcripts" | replaced with the measured boundary: virtual 2026 only, none pre-2026-01-05, none in-person. "not live" banned |
| **D3** | told a member our data holds "Untitled Event" and "for test" | 98 shells created when someone registers on the events site and no event matches | `not_a_real_event` mark, `events_catalog_live` chokepoint, **upcoming narrowed to `Registration Open` only** (Andy's rule) |
| **F1** | "I don't have gender tracked as a census question" while citing census gender medians two questions later | #81's cross-cut rule was scoped to "breaking an existing figure down", so a standalone count never triggered | **one general rule**: never claim MDS does not track something until the tool that would hold it has been called |

**Results** · 100-question run on the candidate: **98/102 clean (96%)**, all 27 regression rows
pass, **zero `chats` routes in 102 answers**. Prior: 90% on the 30-question smoke, 7.7% fail on the
Aug 10 nightly of 220.

**AC checklist** · chapter questions route to chapters — met (8/8, prod probe) · transcript gaps
state the real boundary — met (prod probe names Oct 2025 / 2026-onward) · no internal data
described to a member — met (0 leaks) · she stops denying data she holds — met (89 female, and
D2 did not over-correct) · gate green — met, exit 0 inside the promote · pulse green — met, before
and after.

**Deliberately not fixed** · **F2** she declines "how many cities have events since July 2025",
which IS answerable — the D3 fix traded a leak for a miss. **F3** "that schedule isn't connected to
me yet" is TRUE (no forward call schedule exists) but is the invented-infrastructure phrasing Andy
objected to after the Dorian Gorski incident. Both pre-existing, neither caused by this work.

**Open for Andy** · rule on the women's-chapter revenue cross-tab (compliant — aggregates, n=91,
self-flags its average-vs-median mismatch — but concludes women trend lower than men).

---

### #82 · The biggest events have no dossier — the builder asks "what is this about?" when it should ask "what is this?"
**🔴 S1 · size M — filed 2026-08-12 (Andy: "summit is poor… missing dossier for Summit or Inspire is genuinely bad")**

> **In plain words:** The Summit and Inspire are the two biggest things MDS does, and Olivia
> knew less about them than about a one-hour call.

*As a member, when I ask about the Summit or Inspire I learn what kind of event it is, what
actually happens there, and who is in the room.*

**Measured 2026-08-11:** `MDS Summit Singapore` had `topic_profile {}`, `audience null`, 116
registrations. Topics are kept only at **lift ≥ 1.3** over the community baseline and the
Summit's best was **Sourcing & Suppliers at 1.29** — discarding International Expansion
(**55 members**), Amazon FBA (41), Walmart · DTC & Shopify · Hiring & Team · Logistics & 3PL
(38 each), Supplements (36). A flagship mirrors the community by definition, so lift can never
fire. **Andy's framing decided the design:** a Summit is not topic-specific, so the answer is
not a better topic vector — it is a different question.

**Accept when** asking what the Summit is returns members-only + four days + a real format
element + a room fact with a count · the same for Inspire · a one-hour call still reads as a
topic (lift model untouched) · the room reports counts, never scores · gate GREEN · verified in
the prod node.

#### ✅ BUILT + STAGED + PROVEN 2026-08-12 — awaiting Andy's promote
**The fix, in three layers:** ① `digest.event_series_profile` — curated identity + format for the
two series, from the pages Andy linked (`scripts/seed_event_series.py`). ② `refresh_entity_dossiers`
gains a flagship branch filling `reception->'room'` from **headcount**; lift untouched for topical
events. ③ `event_lookup_v3` returns `what_it_is` + `room`. Plus one Answer Seed rule. Commits
`a6f43af` · `82d0437` · `25f4ae6` · staging `2ecf4e62`.

| AC | result |
|---|---|
| what the Summit is | ✅ *"members-only, runs four days, built for deep peer-to-peer connection rather than sit-and-listen panels… 151 registered… the room skews heavily toward International Expansion (55 members), plus Amazon FBA, Walmart, DTC & Shopify, Hiring & Team, Logistics & 3PL… mostly US, Australia, Canada, Singapore, Thailand, spanning 1-5M up through 20M+"* (#31079) |
| the same for Inspire | ✅ *"the flagship open MDS conference — 400+ seven-to-nine-figure ecommerce founders across Amazon, TikTok Shop and DTC, now in its fifth year… open publicly (not members-only)"* (#31085) |
| a one-hour call still reads as a topic | ✅ Pre-Event Dinner keeps its lift profile (Sourcing & Suppliers 0.654, DTC & Shopify 0.578) with `has_room=false`; last Mogul Call unchanged and its summary still binds (#31089/#31091) |
| the room reports counts, never scores | ✅ gate **247 → 249 exit-0**: room carries only `{topic, members}` ints, and exactly ONE row of twelve carries a room |
| verified in the prod node | ✅ **PROMOTED 2026-08-12 20:51 UTC** `fd957034` to **`e988a6a3`**, gate green inside (DEFAULT probe). Prod: *"the biggest MDS gathering of the year — a members-only, four-day event built for real peer-to-peer depth rather than sitting through panels… International Expansion (57) leads the pack… Logistics & 3PL (41)"*, `sources_used=[event_lookup]`. Topical regression: last Mogul Call unchanged |

**Before → after:** `topic_profile {}` and "draws a strong member crowd" → what it is, how it runs,
and 55/41/38/36 members by topic with country and revenue spread.

**Two data faults found while verifying and fixed before shipping:** countries were double-coded
(`US` 29 + `United States` 23 as separate rows) → `digest.country_fold`, which `chapter_info`
already used: **United States 52**. Niches mixed two taxonomies and fragmented (`Supplements` 3 /
`supplements` 3 / `Health-Beauty-Supplements` 4 in a 117-person room) → categories unnested and
folded on punctuation/spacing/"and": **Housewares 27+9 = the true 36**.

**The plan's own assumption was wrong and the plan caught it:** `style='Main'` is not a flagship
flag — it also marks the Night Out, both Pre-Event Dinners, the Women's and Speaker's Lunches,
"Wim Hoff Experience at MDS Inspire" and the separate Centurion Summit. Headcount cannot separate
them either (Inspire 2027 has 44 confirmed and is still filling, against the Pre-Event Dinner's
33). The NAME does, so `exclude_pattern` is stored as data: **14 flagships kept, all 7 side events
dropped**.

**Closed during #82 (2026-08-12):** four digest functions were anon-callable — `fb_link_content`,
`olivia_touch`, `rebuild_question_map`, `zoom_resolve_attendance`. They read nothing back (void or
a jsonb job summary) so it was never a leak, but each WRITES or runs heavy work, so anyone holding
the public anon key could trigger it repeatedly. Same root cause as the two leaks of 2026-08-11:
Postgres grants EXECUTE to PUBLIC by default and nothing had ever revoked it. Revoked, service_role
re-granted, verified anon 401 ×4 and `olivia_touch` still 204 as service_role. **Gate 249 → 253**
with a check per function, so a new job function cannot arrive open unnoticed. The pure helpers
(`country_fold`, `en_rank`, `term_cover`, `geo_*`, `pct_from_answer`, `profile_rank`,
`state_region_states`, `country_region_countries`) are deliberately left open — they take arguments,
touch no table, return a computed value.

**Named remainder — flagged, not chased:** one event now reports **three different counts** in
adjacent turns — 151 (`event_lookup` registered_count, all ticket types), 117 (dossier
`member_registrations`), 108 (`event_who` confirmed members only). Each is internally correct and
the seed already carries a COUNT WORDING rule; putting them side by side is what made it visible.
Worth its own ticket.

---

### #81 · She declines the question she was built for — and calls missing joins "I can't"
**🔴 S1 · size M — filed 2026-08-11 (Andy, from two live WhatsApp sessions; he rated follow-ups 3/10)**

> **In plain words:** Ask "who should I talk to at the Summit?" and she says ranking people isn't
> something she can judge — then lists people by country. Ask her to split a census percentage by
> men vs women and she says it isn't tracked. Both are things we have the data for.

*As a member, when I ask who is worth my time or how a number breaks down, I get the answer and the
reason — not an apology.*

**Measured 2026-08-11:** `event_who` returned `full_name` + `state` and nothing else, while **98 of
the 108 Summit registrants carry a live topic profile** · `form_stats` grouped by
country/state/niche/rev_band/chapter but **not gender**, though the split computes in one join ·
**no rule forbids ranking members** — the refusal was emergent from an empty tool ·
`entity_dossier` holds **0** rows of `kind='member'`.

**Shape of the fix:** fit computed AT QUERY TIME per asker (the `video_search_v2` `fit_reason`
pattern), not a static match graph — the same roster must read differently for different askers.
Plus rules that forbid presenting a thin tool result as a personal limit.

**Accept when** the two failing sequences are replayed and answered · three-people asks return three
named people each with a non-location reason · a breakdown by gender returns real figures · a
correct decline still happens once and is never repeated on a later turn · no roster reply dumps
more than 12 names · fit never shows a score · gate GREEN · verified in the prod node.

#### ✅ BUILT + STAGED + PROVEN 2026-08-11 — awaiting Andy's promote
**The fix, in three layers:** ① `event_who` gained `fit_reason` / `niche` / `city` / `channels`,
fit computed per asker at query time (`scripts/sql/event_who_81.sql`). Two drafts were measured and
REJECTED first: raw topic overlap fires on all 108 (everyone shares 2–5 topics), and splitting by
kind still qualified 90+. The discriminator is weight **relative to this roster** (percent_rank, top
quartile) — self-normalising across event sizes. ② `form_stats` gained `gender` grouping, and choice
rows now carry `n` so the model prefers the 550-respondent question over the 20-respondent one.
③ Answer Seed: six rules — WHO SHOULD I TALK TO · NEVER CALL A DATA GAP A LIMIT · DECLINE ONCE ·
LONG ROSTERS · CROSS-CUT STATS · ANSWER IN THE FRAME ASKED. Staging `670fdc57`; a seventh rule (LOCATION IS NOT A LABEL — Andy: the niche earns its bracket, the city does not) shipped in `3d5f2b1b`.

| AC | result |
|---|---|
| both failing sequences replayed and answered | ✅ "who is the best match to me?" → **"Top of the pack for you is Alex Bonilla (Supplements, Costa Mesa CA) — strong match on AI & Automation and Hiring & Team"** (#31005) · "break down this 20%, M vs W?" → **women 25% / men 32% no kids** (#31025) |
| three-people asks return three, each with a non-location reason | ✅ #31007: Alex Bonilla · Neeme Roos · Daniel Meredith, each with the topic overlap named, no disclaimer |
| a breakdown by gender returns real figures | ✅ `form_stats p_group_by=gender`, verified against `form_windowed` (the tool's own source) |
| a correct decline happens once, never repeated | ✅ #31037 still declines the matchmaking ask; the next turn (#31033) answers the member count with **no re-litigation** |
| no roster reply dumps more than 12 names | ✅ #31003: 5 named with reasons + 7 grouped + the total + one offer, out of 108 |
| fit never shows a score | ✅ gate check #81 (shape test: known opener, no %, no decimal — a naive no-digits test false-fires on "3PL") |
| gate GREEN | ✅ **247 exit-0** |
| verified in the prod node | ✅ **PROMOTED 2026-08-11 23:42 UTC** `c59fd3ff` → **`fd957034`**, gate green inside. Prod probe: *"Top pick for you at the Singapore Summit is Mo Kuhail — strong on Logistics & 3PL and International Expansion"* + two more, `sources_used=[event_who]` |

**Before → after** on Andy's own words: *"I really can't rank people or tell you who you must talk
to"* → three names with reasons. *"that breakdown isn't something I can split by gender"* → the
split. Niche coverage on the roster 29 → 60 of 60 returned rows; 30 names carry a different reason
for Ian than for Andy, which is the proof that fit is per-asker and not a static label.

**🚨 Found and fixed during this ticket — a leak I introduced.** `DROP FUNCTION` discards the ACL and
Postgres re-grants EXECUTE to PUBLIC on CREATE, so both DROP+CREATE migrations left their RPC
anon-callable: `event_who` (minutes) and **`video_search_v2` (#80, ~6h, on PROD)** — roster names/
cities/niches and video summaries. No phones, emails or revenue (other gate checks held). Both
revoked and re-granted service_role-only; anon 401, service_role 200. **Runbook rule now: after a
DROP, granting is not enough — REVOKE from public/anon/authenticated too.** Andy's call whether the
window needs any disclosure.

**Named remainders:** 10 of the 108 roster carry no fit_reason — all MDS Team or no member record ·
28 digest functions are anon-executable (24 trigger-only or pure helpers, 4 callable maintenance
writes: `fb_link_content`, `olivia_touch`, `rebuild_question_map`, `zoom_resolve_attendance`) —
pre-existing, #62's lane · the 50-question follow-up eval set is deliberately deferred to after this
promote, since building the instrument mid-change bakes in today's behaviour (#76 owns the rebuild).

---

### #79 · Olivia's intro goes stale as we ship features — keep it current, don't auto-generate it
**🔵 S3 · size S — filed 2026-08-10 (Andy)**

> **In plain words:** Olivia's first hello lists what she can do. We keep adding capabilities
> (census, calls, events, partners…) and the intro doesn't move — so a new member's first
> impression is already out of date.

*As a member messaging Olivia for the first time, her intro reflects what she can actually do
today — not a frozen list from launch.*

**Design call (Andy asked: dynamic, or overdesign?): keep it CURATED, don't auto-generate it.**
An intro is warm, deliberate copy with a voice; generating it from whatever features exist produces
a changelog, leaks internal or half-shipped capabilities into a member's first impression, and loses
the tone. The fix is a **cadence, not a generator**: the intro is hand-written against a short list
of member-facing capabilities, and that list is reviewed whenever a member-facing feature ships
(fold it into the sprint-close / release-notes step). A middle option — a tiny hand-maintained
capability list the message renders from — stays available if we ever want it, but full
auto-generation is ruled **overdesign** unless Andy decides otherwise.

**Accept when**
- The intro reflects the current member-facing capabilities — nothing stale, nothing missing.
- The dynamic-vs-curated decision is recorded (default: curated + a review cadence).
- A cadence exists so it can't silently drift again (a line in the sprint-close ritual or release notes).
- Shipped in the prod workflow, gate green, verified in the prod node.

#### ✅ SHIPPED + LIVE 2026-08-11 — prod `c59fd3ff`
**The fix:** the intro was frozen at launch and had gone FALSE — it still said *"Not yet: what was
*said* inside a recording (no transcripts)"* months after #70 put transcripts and summaries live,
and never mentioned census stats, credits, chapters or bug reports. Rewritten with Andy line by
line and shipped to the `help` route (`Build Verbatim Digest`, apply script
`scripts/olivia_loop/apply_79_help_message.py`).

| AC | result |
|---|---|
| reflects current member-facing capabilities | ✅ calls/videos, census responses, applications, chapters, credits, bug reports all present; the false no-transcripts claim gone |
| dynamic-vs-curated decision recorded | ✅ **CURATED** — a generator writes a changelog and leaks half-shipped work into a first impression; recorded in the ticket and in the node comment |
| a cadence exists so it cannot drift again | ✅ re-read at every sprint close / release-notes step (sprint ritual header) |
| shipped in the prod workflow, gate green, verified in the prod node | ✅ promote gate GREEN · **prod probe #30973 byte-identical (1,217 chars) to the copy Andy approved on WhatsApp** (delivered, `olivia_sends` status=delivered) |

**Andy's rules captured in the copy:** identity is *the MDS AI assistant*, never a person · no
member names anywhere · WhatsApp bold is a SINGLE asterisk · early beta stated next to the 👍/👎 ask
(the #75 signal) · revenue-limit line dropped · personalization described honestly, not overclaimed.
Every example phrasing probe-proven first — *"what % of members sell on TikTok?"* → `form_stats`
(89%, median 3%) · *"who leads the NY chapter?"* → `chapter_info` (3 leads + link).

---

### #80 · Olivia over-suggests a next step — and doesn't deliver what it teases
**🔴 S1 · size M — filed 2026-08-10 (Andy, from his own digest.mds.co session)**

> **In plain words:** Almost every reply ends with "Want a quick summary?" / "Want me to…?" — and
> when you say yes, you get something generic, not the thing it teased. The constant suggesting is
> annoying, and the follow-through doesn't match the offer.

*As a member, Olivia only offers a next step when it's genuinely useful — and when I accept, she
delivers exactly what she offered, not a different or generic answer.*

**From Andy's session:** she offered a summary of a specific SEO library video ("Want a quick summary
of it?"); on "Yes" she summarised the community thread's aspect-ratio debate instead of the video —
teased X, delivered Y. Two problems to separate: (1) the follow-up prompt fires too often
(cut it back to when it adds value), and (2) when accepted, the answer must resolve the exact thing
offered (bind the "Yes" to the teased subject, not the last topic in context).

**Accept when**
- The follow-up suggestion appears only when it genuinely helps, not on every turn.
- Accepting an offer delivers the offered thing (the video summary, not the thread) — measured on the
  cases that failed.
- No class traded: normal answers don't get worse. Gate green; verified in the prod node.

#### ✅ BUILT + STAGED + PROVEN 2026-08-11 — awaiting Andy's promote
**The fix:** offer binding made deterministic. ① `video_search_v2` — the RPC the loop's
`video_search` tool actually executes — gained `p_video_id` (exact-row fetch) and a `summary`
return column: **it returned NO summary before, so an accepted offer could never be delivered
from the video itself** (migration `video_search_v2_p_video_id_summary_80`, generator
`scripts/sql/gen_video_search_v2_80.py`). ② Answer Seed only (apply script
`scripts/olivia_loop/apply_80_offer_binding.py`): deterministic OFFER ACCEPTED detection (prev
turn ends in an offer + links `app.mds.co/videos/<id>` + member accepts → binding injected at
the head of the preload evidence), `p_video_id` in the tool schema, and two rules — DELIVER
WHAT YOU OFFERED · OFFER SPARINGLY. Commits `1d2ce03` + `1825ce4`.

| AC | result |
|---|---|
| accepting delivers the offered thing, measured on the failed cases | ✅ BEFORE (staging, same graph as prod): bare-Yes re-ran the thread, `sources=['content_search']` (#30847) · AFTER: offer→"Yes" → **summary of the teased SEO call, `sources=['video_search']`** (#30871); offer→"Can you summarize key points" → same binding (#30865) — both of the week's failing variants (#28131/#28133/#29905 · #29907) now deliver |
| follow-up suggestion only when it genuinely helps | ✅ the redundant/either-or class is dead in probes: the "just-delivered summary re-offered as an either/or" shape (#30853 BEFORE) did not recur; closes now offer only a NOT-yet-delivered next step (#30865 offers the full video). ⚠️ honest remainder: a self-contained count answer still closed with a drill-down offer (#30881) — the offer RATE is a traffic statistic; baseline 26% of llm answers, re-measure on a week of prod traffic after promote |
| no class traded, gate green, verified in prod node | ✅ "last mogul call" still date-correct (Dorian Aug 5) and its "yes" summarizes THAT call (#30875/#30877; the video is now `public` — restriction lifted upstream, restricted path untouched) · gate **246 exit-0** (as Ian) · prod-node verify = the promote step |

**Before → after** on the failing class: 3/3 accepted video offers delivered thread chatter
(week of Aug 4–11) → **0 failures in a 12-sequence / 19-follow-up battery** (staging `dcc75770`,
msgs #30884–30957): all 8 accepted video offers delivered the bound video via `video_search`
(incl. the two exact prod-failure shapes #28130/#28132 replayed — SEQ3/SEQ4), ordinal binding
("summarize the first one") correct on videos AND partners, "and the UK specifically?" drill-down
not hijacked, chat-scope + events follow-ups clean. Mechanism confirmed in the execution args:
`p_video_id` present on the inspected accepts (execs 75346/75349). Named remainder: either/or
offer tails still appear (~3 of 12 closes) — OFFER SPARINGLY killed the redundant re-offer class,
the rate itself is re-measured on a week of prod traffic.
**PROMOTED 2026-08-11 20:09 UTC** (Andy's order): prod `e5d57236` → **`c59fd3ff`**, gate green
inside the promote (as Ian), graph matches staging, snapshots either side. **Prod probe: offer→"Yes"
delivered the bound call summary, `sources_used=['video_search']` (#30979).**

---

### #75 · Reactions may be silently dead — nothing logs one before it is parsed
**🔴 S1 · size S — filed 2026-08-10**

> **In plain words:** 👍/👎 is the only signal a member gives us for free, and we cannot tell whether we are still receiving them.

*As the team, a member's thumbs-down always reaches the review queue — and if the path breaks we find out that day, not six weeks later.*

**Measured 2026-08-10:** `digest.olivia_feedback` holds **10 reactions all-time — 6 👎, 4 👍**, spanning
2026-07-24 → **2026-08-04**. **Zero in the six days since.** Prod was promoted twice on Aug 4
(22:35, 23:13 UTC) and twice more after. At the observed 3.7% reaction rate over ~78 answers since,
roughly 3 were expected. Zero is not proof, but "reactions stop the same day as a promote, silence
ever after" is the shape of a broken parse.

**Why we cannot answer it today — the actual defect.** Nothing records a reaction before the
Parse Reaction node handles it: no rows in `olivia_messages`, no raw inbound webhook store on the
Olivia side (`wa_messages` is the digest/Whapi system). **A dropped reaction leaves no trace
anywhere**, so the count can never be verified. Same class as the heartbeat that never stamped and
the linker that never ran: the failure mode is silence.

**Shape of the fix**
- Persist every inbound Meta webhook payload (or at minimum every `reaction` event) before parsing,
  so a parse failure is visible as a gap between raw and parsed.
- One canary: react from a test number, assert `olivia_feedback` gains the row. **Never against a
  real member's number.**
- Heartbeat/alarm on the reaction path — "0 reactions in 14 days" should page, not pass quietly.

**Accept when** a raw store exists and is gate-checked · the canary proves round-trip · the 6-day
gap is explained as either broken (fixed, with a reaction landing after) or genuinely quiet (with
the raw log showing zero arrived) · no claim of "working" without one of those two.

#### ✅ BUILT + STAGED + PROVEN 2026-08-11 — awaiting Andy's promote
**The fix:** raw store `digest.olivia_webhook_events` (every inbound MESSAGE event persisted
verbatim BEFORE any parse; statuses excluded — `olivia_sends` has them, and the 5-min health ping
is statuses-only) + two staging nodes wired as the FIRST webhook branch (v1 depth-first order, so
the payload outlives a throwing parse) + `scripts/olivia_reaction_canary.py` + health signals 7
(reaction-parse-gap) and 8 (reaction-silence-14d). Commit `02cf62d`; apply script
`scripts/olivia_loop/apply_75_raw_webhook_store.py`.

| AC | result |
|---|---|
| a raw store exists and is gate-checked | ✅ table live; gate 245 → **246 exit-0**, `anon key denied on olivia_webhook_events (#75)` PASS |
| the canary proves round-trip | ✅ staging canary exit 0: raw row OK + feedback row OK + cleanup OK (silent — a reaction never generates a reply) |
| the 6-day gap explained, broken or quiet | ✅ **quiet, with live proof of both hops**: a synthetic reaction at the PROD webhook landed in `olivia_feedback` in seconds (parse alive) · delivery statuses arrive daily on the same webhook+field (subscription alive) · ~40 real answers since Aug 4 ⇒ expectation ≈1.5 reactions, zero observed is plausible. The raw log starts today — the historical week itself is unrecoverable, which is precisely the defect this ticket removes |
| alarm on the path | ✅ signal 7 fires on raw-without-feedback after 15 min (join proven to bite: 0 real / 1 broken); signal 8 pages on 14-day arrival silence, quiet until the store has 14 days of history |
| no "working" claim without proof | ✅ every claim above cites a live check from this session |

**Before → after:** a dropped reaction left no trace anywhere → every message event is on disk
before parsing, a gap pages within the hour, arrival silence pages at 14 days.
Staging `289a9656` (69 nodes, +`Extract Raw Event`+`Store Raw Event`, diff vs prod = exactly these).
**PROMOTED 2026-08-11 15:07 UTC (Andy's order, run via me): prod `ebe7244b` → `e5d57236`**, 2 nodes,
gate green inside the promote (as Ian via `OLIVIA_GATE_PHONE`), snapshots either side in
`olivia_snapshots/`. Prod verified: fan-out `['Extract Raw Event', 'Log Inbound', 'Parse Delivery
Status', 'Parse Reaction']` · **prod canary exit 0** (raw + feedback rows, self-cleaned) · health
pings since promote stored **0 rows** (statuses excluded, live-confirmed).

---

### #77 · 183 members are unreachable by Olivia for no good reason — AT has their phone, the WA layer does not
**🔴 S1 · size S — filed 2026-08-10 · DEMO BLOCKER for #72**

> **In plain words:** One in four active members would get "I don't know you", and we already have their phone number.

*As a member at the Mille announcement, I message Olivia and she knows who I am.*

**Measured 2026-08-10:** 751 active members · **559 reachable** (phone in `digest.members`) ·
**192 not**. Of those 192, **183 already carry a Preferred Phone Number in Airtable** — the number
never reached the WA layer that `is_active_member_status()` and every RPC resolve against. Only
**9 genuinely have no phone anywhere** (2 New Members, 7 Staff). So this is a sync gap, not a
collection problem, and it is ~25% of the room at any member event.

**Two traps for whoever builds it:**
- **AT phone formats are inconsistent** — `3852166681`, `+13602596458`, `12053442149` all present,
  plus junk (`"0"`). Normalise to the WA format Olivia matches on; drop junk rather than insert it.
- **`digest.members` is the identity layer.** A wrong number there means one member reads another
  member's data — the worst failure this system has. Scripted backfill with a dry run Andy reads,
  never an ad-hoc insert. `members.airtable_id` is NOT NULL.

**⛔ Access gating rides on this table.** Every gated RPC calls
`is_active_member_status(m.membership_status)` against `digest.members` — a COPY of the roster, not
the live status. Verified 2026-08-10: 596 matched rows, **0 mismatches**, so nothing leaks today.
Backfilling 183 rows means 183 more copies: each inserted row must carry the correct
`membership_status` and stay synced, or the backfill manufactures the exact stale-access leak that
does not currently exist. Andy 2026-08-10: **only active members may use Olivia.** The four active
statuses are Current Member · New Member · Current Member- Not Renewing · Staff.

**Accept when** reachable rises from 559 with the before/after counted · every inserted number
normalised and no junk written · a spot-check proves 5 backfilled members resolve to themselves and
not to anyone else · the 9 with no phone are listed for the team to chase · gate GREEN.

#### ✅ CLOSED — shipped 2026-08-10 00:43 in commit `b227682` (session went unlogged; board caught up 2026-08-11)
**The fix (bigger than the backfill):** identity separated from chat presence — `member_phones`
(every known phone per member, normalised) · `member_phone_index` (materialised, pg_cron every
15 min, 544 ms) · `resolve_asker()` (indexed, status read LIVE from `member_attributes`) ·
`member_identity` (members + a synthetic row per active member with no WA row — identified, not
admitted). 53 retrieval functions repointed; two rewrite passes (first missed aliases `mz`/`r`;
end-state assertion now alias-agnostic). Health signal 6 pages if the refresher stops.

| AC | result |
|---|---|
| reachable rises from 559, counted | ✅ **559 → 732** of 751 active · newly unblocked **173** · regressed **0** |
| numbers normalised, no junk | ✅ normalised to last-10; junk dropped |
| spot-check resolves to self | ✅ Keith Gipson (active, no WA row): member_card 1 · events 5 · partners 3 · chat 0; WA member unchanged; unknown number 0. Ambiguity judged over ACTIVE only — zero phones with >1 active owner |
| the phone-less listed | ✅ 19 with no phone anywhere (commit body) |
| gate GREEN | ✅ 245/245 exit-0 · db/ re-exported, 121 files byte-match |

---

### #65 · 🚨 THE SQL LAYER IS NOT IN VERSION CONTROL — single point of failure
**🔴 S1 · size M — filed 2026-08-06 · CLOSED 2026-08-07**

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

---

**CLOSED 2026-08-07** — 0 → 118 files. Every `digest` function (104), view (8), trigger (18),
grant, RLS flag and table/index DDL now exists in `db/`, byte-matched to the live database.

| AC | Verdict |
|---|---|
| Every function, view and policy is a file in git, byte-matched | ✅ **met** — 118 files (`fe3be75`); md5 computed *inside Postgres* matched the bytes on disk for `content_search_v2`, `form_stats`, `member_card_v2`. Policies: zero exist, and the file records that zero. |
| CI drift check demonstrably fails on an injected difference | ✅ **met** — both directions. Repo edit → `DIFFERS functions/member_card_v2.sql`, exit 1. Live `drift_canary()` → `MISSING FROM GIT` + the grants diff, exit 1. Green again after each, working tree clean. |
| Tier rule + exceptions in the handbook | ✅ **met** — §12, with `olivia_alarm_fire` (Slack from inside Postgres, deliberate) and `member_event_url` (URL shaping in SQL) named as accepted exceptions. |
| Gate GREEN before and after; no RPC behaviour changed | ✅ **met** — 243 exit-0 before, 243 after the DDL, **245** after the two new checks. The only DDL was one added read-only function; nothing existing was altered. |

**Before → after:** source files **0 → 118** · restore path **none → `db/`** · an out-of-band
`create or replace` detected **never → within 24h** (`com.mds.db.drift`, 05:40 daily, Slack-alerting,
forced run proven under `/usr/bin/python3`) · gate **243 → 245** · handbook function count corrected
**~75 → 104**, gate count **202 → 245**.

**How it reaches the DB:** one read-only `digest.schema_source()` — STABLE, security INVOKER, DDL
text only, `service_role` only (anon: `401 permission denied`, now a gate check). There is no
psql/psycopg/DB-password/PAT on this machine, so PostgREST is the only path and it cannot read
`pg_catalog` without a function.

**Found while doing it, NOT chased (flagged for priority):** `digest.chapters_catalog` has RLS
**enabled with zero policies** — belongs to #62/#61, not here. Eight other launchd plists exist only
on Andy's Mac and in no repo — the same class of risk this ticket just fixed, and #64's lane.

**Remaining, for Andy to rule:** the repo→DB direction (apply-from-file). It is the only step that
can break production, so it stays out until it has its own proof plan and a rehearsed rollback.

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

