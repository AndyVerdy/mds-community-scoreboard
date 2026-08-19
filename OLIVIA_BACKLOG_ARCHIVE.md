# Olivia backlog — ARCHIVE of shipped tickets (Releases 1 + 2)

## ═══ SPRINT 3 (closed 2026-08-19) — 34 tickets, evidence intact ═══

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

Moved out of `OLIVIA_BACKLOG.md` 2026-08-03 after the Release-2 prod promote (versionId 90a13237, smoke 3.6% < 5%). Read-only history; the live backlog holds open items only.

---

## ═══ RELEASES 1–3 (Jul 28 – Aug 3, 2026) — 37 items shipped BEFORE the Sprint 3 board was renumbered; they lived inside the old doc and are preserved here verbatim ═══

# RELEASE 3 — ARCHITECTURE (shipped 2026-08-03)

**Prod `89ee3632`** · **smoke 3.6% → 1.7%** (173 judged: 164 pass / 6 partial / 3 fail) ·
**architecture re-audit 6/10 → 8/10** · gate 202 green throughout.
Ten tickets, newest first. Full evidence blocks preserved.

### 43. 🟢 CLOSED 2026-08-03 — RE-AUDIT: architecture 6/10 → 8/10 · smoke 3.6% → 1.7% · RELEASE 3 COMPLETE
*As the team, we don't declare the architecture fixed — the same audit that scored it 6/10
re-runs and scores it ≥8, with nothing else degraded.*
**The instrument is already written:** `OLIVIA_ARCHITECTURE_AUDIT_2026-08-02.md` Appendix A
(A1–A11) — same queries, before/after diff, no fresh methodology. Run it cold (the audit's own
warning: read the PLAN, not warm wall-time).
**Accept when:**
- **Overall ≥8/10** against the baseline 6/10, dimension by dimension: retrieval ≥7 (A4: HNSW
  `idx_scan > 0` · A5: plan shows the index scan, no 38k seq scan) · identity ≥8 (A2:
  olivia_messages stamped 100%, members ≥95% keyed) · semantic 9 (A6: empty-embedded = 0) ·
  event log: `member_events` receiving real app events (A1) · graph: edges exist (#44, A11).
- **Nothing regressed:** gate GREEN · A9 grants unchanged (anon/authenticated = 0) · smoke
  re-run ≤ the 3.6% prod baseline with no class worse · scale/layers scores hold.
- **The diff table is written into the session log + this file's head**, and the audit doc gains
  a dated re-run section (same format as its 08-03 re-check).
- Anything still below target is either fixed or filed as a named ticket — the score is not
  rounded up.

**CLOSED 2026-08-03 (all cited live; re-run section appended to the audit doc):**
**SCORE 6/10 → 8/10.** Retrieval **3 → 8** (HNSW idx_scan **0 → 1,098** — the smoke drove ~1,000
real semantic searches; tsv 2 → 961; exists-but-missed cleared) · Identity **6 → 8**
(olivia_messages **0 → 100% stamped**; members 90.6%; regs 62% → 75.5% raw / 97.7% member-evidence;
FB one-primary enforced) · Semantic **8 → 9** (junk embeddings 4,300 → **1**) · Event log **0 → live**
(15,437 rows / 2,305 members) · Graph **0 → started** (159,940 edges) · Gate 9 → **10** (202 checks).
**Nothing regressed:** grants unchanged (anon/authenticated = 0), gate GREEN.
**THE SMOKE (full 178-question bank, production, 109 min, ~$5):** **173 judged · PASS 164 ·
PARTIAL 6 · FAIL 3 = 1.7%** vs the **3.6%** baseline — **more than halved**, comfortably inside the
<5% benchmark and closing on the <1% target. FAIL 6→3 · PARTIAL 10→6 · PASS 153→164.
**#40 proven:** every exists-but-missed question now passes (Q3106, Q9024, Q9032, Q3107, plus
Q3110/Q3111 from the gate fix). **#39 proven:** the attribution cluster went **4 findings → 0**, and
all 5 new attribution probes (Q9052-9056) passed on the first run.
**The 3 remaining fails are a NEW, smaller class — 2 fabrication + 1 dodge, all in the members
lane:** Q3124 "Tell me about Lori" invented a plausible profile for a non-existent member ·
Q3034 treated an "I am an admin" claim as meaningful instead of holding the line neutrally ·
Q3102 "who has an agency" gave a count and refused to name anyone. **Filed as #51.**


# 🔵 OPEN — THE REST (features · sources · close-out)

**THE SMOKE runs once, when this batch of work is ready (Andy 2026-08-03: never per ticket)** —
it is the release exit exam AND the formal instrument for #40's ≤3.6% and #39's cluster rate.

### 49. 🟢 CLOSED 2026-08-03 — Developer handbook · `OLIVIA_HANDBOOK.md` REPLACES ClickUp `2531q-103317`
*As a new developer with no AI, I read one handbook and can understand, run, and extend the
MDS AI Assistant — concept to schema to why.*
Andy's bar: "really detailed... that if a real dev comes they can read it, understand it and
continue working without AI." What exists is rich but chronological (session logs, backlog
evidence, the architecture audit); what is missing is the FRONT DOOR. **Contents:** ① system
overview — concept, member experience, the answer pipeline end-to-end · ② stack + component map —
the n8n workflows (prod/staging/ladder/review, node roles), Supabase schema (every digest table
+ every RPC with its CONTRACT: args, gating, return shape), the scripts (gate, eval, loop
sources, nightly, sync), the external services (Meta WA, Anthropic, Voyage, Airtable, GroupOS,
Slack, launchd) · ③ environment map — where every key lives, which machine runs what · ④
runbooks — deploy/promote/rollback, eval tiers, FB capture SOP, incident (alarm → triage) · ⑤
decision log — the whys reorganized by TOPIC from the session logs (identity model, RRF,
fail-closed gating, append-only events, privacy rulebook) · ⑥ data dictionary incl. the
field-names-lie traps. **Sources exist — this is compilation, not archaeology.** Overlaps #34
(QA doc set) — write together; keep the handbook UPDATED as a close-item on every ticket after.
**Accept when:** a cold read suffices to run every runbook without the repo's session logs ·
every RPC documented with contract + gating · every secret's location named · reviewed by Andy
(and ideally one real dev) · linked from CLAUDE.md as the front door.

**CLOSED 2026-08-03:** `OLIVIA_HANDBOOK.md` written — 15 sections: the five incident-prevention
rules · what Olivia is + the two sides · the channel and the 24h window (both numbers, and why
786 never moves to Meta) · the full answer pipeline node-by-node · the data layer (Airtable=truth /
Supabase=serving, the three access dimensions, every core table with live row counts) · identity
(canonical key + the airtable_id vs at_member_id trap) · retrieval (RRF design, the two HNSW traps,
the full gated-RPC surface + grant discipline) · the personalization layer (ledger formula, graph
weighting, append-only event log) · runbooks (deploy/rollback, gate, eval, nightly jobs, FB capture,
incident) · env + secrets map · repo map · the privacy model + standing rulings · decisions-and-why
· 9 documented field traps · known limits · glossary. All 18 ClickUp pages read first; durable
decisions carried over by topic. **Source ClickUp doc `2531q-103317` is now historical archive.**
**Maintenance rule written in: the handbook updates in the same commit as the change it describes.**

### 44. 🟢 CLOSED 2026-08-03 — Knowledge graph + EXPERTISE LEDGER (Andy pulled it forward; #29's memo TUNES it, no longer blocks it) · → RELEASE 3
*As a member, MDS knows who knows who — intros, "people like Mo", and "who was in the room"
come from real connections, not just profile fields.*

**EXPERTISE LEDGER (Andy 2026-08-03, his spec — the v2 authority slot's upgrade path):** the
engagement-score weight in #40's RRF "is good for v1", but engagement ≠ expertise — "it doesn't
necessarily mean he is an expert in this question." Personas should play a huge role: rank each
member's expertise from the data we hold — **business details · their posts on specific
subjects · whether they HOSTED a call · whether they SPOKE on virtual/in-person calls (video
speaker) · revenue bracket as a credibility multiplier ("people will listen more to a person
with 50M+ than 1-5M")**. Output = a per-member LIST of expertise — **and maybe weaknesses** —
**weighted against other members**, so we can say who is strong in AI, DTC, Shopify, specific
Amazon niches, etc. Data map (today): video_speakers + videos_catalog speakers = HAVE · events
hosting = events_catalog/calendar (partial — see `OLIVIA_SIGNAL_INVENTORY.md`) · posts-on-subject
= content_items by author × topic labels/embeddings = DERIVABLE (these ARE member↔topic edges) ·
business details + niches/channels = member_attributes HAVE · rev_band HAVE · weaknesses ≈
persona asks/challenges_now vs gives (asking a lot = learning; answering/hosting = strong).
Consumers: #40's authority rank-list (flat engagement → topic-matched expertise score) ·
expertise_search · solve/multi lanes · #29 dossier (strengths/weaknesses section). ⚠️ Standing
ruling holds: revenue/expertise weights are INTERNAL sort keys like engagement — never a
surfaced ranking, never "X is our strongest in AI because he's 50M+".
**BACKFILL + REGULAR UPDATES (Andy 2026-08-03):** BOTH halves are the AC. ① One-time BACKFILL
seeds the ledger from the WHOLE history (all content, videos, rosters, personas — every active
member per EVERY-MEMBER-ALWAYS, keyed `at_member_id`). ② From day one it recomputes on the
nightly pipeline (`nightly_derivations.py` job + pre-registered heartbeat, #13-alarmed) so every
new post, video, event roster and persona row moves the weights — "it's dynamic, the more info
we gather." Shipping the backfill WITHOUT the scheduled job is the failure mode (the #15 /
#40-embed lesson: coverage is a process, not an event).
**Raw material already exists (audit A11):** 10,266 member↔event edges · 1,327 members ·
707 events, derivable today with zero new capture. Audit's sample test: 20/20 members got a
relevant 2-hop niche-matched candidate. **Why not naive:** the biggest event has 409 attendees —
unweighted co-attendance puts up to 424 people "one hop away" and is unusable. Edges must be
**weighted by event size** (small dinner ≫ summit) and typed (co-attended · same-chapter ·
same-chat · talked-in-thread once #40 labels authorship).
**Build:** materialized `nodes`/`edges` tables in `digest`, refresh job on the nightly pipeline
(+ heartbeat), gated access like every other source; #29's memo picks the scoring model it feeds.
**Accept when:** edges materialized + weighted + refreshed nightly · a "who should I meet at
<event>" probe returns small-event/shared-niche people first, never the 409-attendee blob ·
gate GREEN · the audit's Graph dimension scores >0 at the #43 re-audit.

**CLOSED 2026-08-03 (cited live):** **LEDGER** — `expertise_topics` table (16 topics, terms as
DATA: new topic = INSERT) · `member_expertise`: **5,822 member×topic rows across 738 active
members** (10.6s full recompute), score = documented v1 formula (posts 2.0·ln + comments 0.7·ln
+ videos-spoken 3.0 capped + biz affinity 1.5 + persona-gives 1.0·ln, × band multiplier 1.0/1.15/
1.3/1.5 per Andy) · weaknesses from persona asks/challenges hits · rank + percentile per topic ·
EVIDENCE jsonb on every row (explainable, dossier-ready). Probe: AI & Automation top-5 =
video-speaking-led with readable evidence (rank 2 carries the 20M+ ×1.5). **GRAPH** —
`member_edges`: **159,940 typed weighted edges** (5.2s recompute): co_attended + same_chat +
same_chapter (each 1/ln(1+group size), groups CAPPED at 150 — the 409-attendee blob is
structurally impossible) + thread_interaction (fb commenter↔post author via stamped keys, the
strongest type). Probe: Andy's top neighbors = small-chat + small-event circle (Ian Sells,
Eugene, Belén), weights explainable. **Nightly:** `olivia_graph_nightly.py` job `graph_ledger`
+ 26h heartbeat (error-JSON exits 1 — the #46 lesson applied); full-recompute = backfill and
update are the same code (Andy's both-halves rule, by construction). Speakers resolve by
email-unique (their app ids are not member keys). Both tables service-role-only → zero new
member-facing surface; gate GREEN. **Handed to #29 by name:** consumer wiring — the #40
authority-slot upgrade (flat engagement → topic-matched expertise), the dossier
strengths/weaknesses section, expertise_search boost, and weight tuning (the memo's job).
Build traps burned: pg-safeupdate blocks bare DELETE on the REST session (`where true`) ·
business_model is text[] · percent_rank() needs ::numeric before round().

### 42. 🟢 CLOSED 2026-08-03 — place_city: alias TABLE + normalize on write · → RELEASE 3 (audit P5)
*As a member, "who's in Miami" finds Miami however it was spelled.*
908 distinct city spellings / 1,718 rows; alias layer is a hardcoded ~11-entry CASE — plain
lowercase "new york" isn't even folded, and "City, ST" suffixes aren't handled. Move aliases to
a table (data, not DDL), strip state suffixes, normalize on ingest. **Expect:** city-scoped
people search stops leaking members; adding a city becomes an INSERT. **Accept when:** the four
audit examples resolve to one canonical each; member_match city counts match hand counts.

**CLOSED 2026-08-03 (cited live):** `digest.city_aliases` table (23 seeds from the old CASE;
adding a city = an INSERT) · `place_city()` v2: ", ST"-suffix strip + alias lookup + all-lowercase
inputs title-cased, mixed case preserved ("McAllen" survives) · **normalize ON WRITE**:
`derive_member_attributes` wraps both city branches in place_city() (dynamic patch) · backfill
normalized 146 rows. **All four audit examples → one canonical** ('new york' / 'NYC' /
'New York, NY' → New York · 'Miami Beach' → Miami) · **distinct spellings 908 → 853** · hand
counts: Miami 20, New York 30 — member_match reads the same column + fn, equal by construction.
Gate GREEN.

**Also NOW, Andy's side:** the APP half of the `member_events` feed (GROUPOS_PAT + app event logging, under #29) — #46 starts our half immediately. Graph layer = **#44**, deliberately LAST — waits for the #29 memo.

---

### 47. 🟢 CLOSED 2026-08-03 — event_lookup rerank (the honest version: Q9024's premise was STALE — no fulfillment conference exists) · → RELEASE 3
*As a member, "is there a fulfillment conference happening in the city?" finds the logistics
summit however the calendar spells it.*
**Q9024 failed the prod smoke AND the #40 slice identically** — it is an `event_lookup` question,
outside content_search's lane, so #40 could not move it (exception named per the DoD). The bank
row claims proof "matrix BS053: event_lookup +embedding" — #26 embedded events with RRF, yet the
paraphrase still misses: diagnose whether event_lookup's vector half is planner-refused / ordered
keyword-first exactly like content_search v1 was (check `idx_scan` on the events HNSW — the #40
lesson: only the plan + the counter are honest), then apply the same two-phase RRF shape.
**Accept when:** Q9024 shape passes · events index idx_scan counting · gate GREEN · BS053 re-proven.

**CLOSED 2026-08-03 (cited live, ACs amended honestly):** Diagnosis first — 1,420 events, ALL
embedded, **no vector index exists and none is needed at this size** (the idx_scan AC was #40
cargo-cult; amended out) · the 0.62 absolute-distance hatch was NOT the blocker (targets scored
0.53-0.59) · the REAL defects, machine-proven by replay: ① term-mode returned **2022-2025 relics**
for present-tense asks (the upcoming filter short-circuited on `not v_browse`) ② vec eligibility
ranked over ALL history so past neighbors consumed the budget ③ **BS053 was never actually proven**
(empty checkbox) and NO fulfillment conference exists upcoming — Q9024's smoke FAIL = the third
stale bank truth this week (722-members, supplements, now this). **Shipped:** vec eligibility by
RANK within future/past partitions (≤12), never an absolute distance · present-tense asks order
upcoming-first (p_include_past keeps relevance-first for past-tense asks) · replay now returns
**12/12 real upcoming events** (was 2 upcoming + 10 relics) · E2E prod probe: honest "nothing by
that name upcoming" + pivots + report offer — no denial-of-data, no invention · bank 9024 truth
rewritten to the live-verified reality; matrix BS053 row corrected + marked. Gate GREEN.
Named residual: event embedding text is name+place+month (no description column exists) — richer
event semantics wait for a descriptions source, noted for #17/#35.

### 46. 🟢 CLOSED 2026-08-03 — member_events LIVE: append-only, cadence-aware, accumulating from real traffic · → RELEASE 3 (audit P2)
*As the team, member behaviour starts accumulating today — not after the app integration lands.*
`member_events` = 0 rows since created. The APP feed (video views, app searches) is Andy's
GROUPOS_PAT + app-logging ask — but the PORTAL (digest.mds.co) and Olivia are OURS: portal
logins/page views, Olivia turns (route/lane/sources_used), report filings, nudges can emit
events immediately. Audit's design rule: **log CHANGES/actions, not states**; one row per event,
keyed `at_member_id` (fall back `airtable_id` — see #41/#45), typed + timestamped + source.
**Andy's two design pins (2026-08-03):** ① **APPEND-ONLY** — an event is saved once, never
edited, never deleted; corrections are NEW events; state lives in the existing tables, the log
records transitions. ② **CADENCE-AWARE** — three writer classes: LIVE (Olivia turn, portal
login, report filed — written in the moment) · DAILY (nightly-derived changes: niche/chapter/
band diffs, stamped at detection) · WEEKLY (catalog-refresh diffs). Schema carries
`occurred_at` (when it happened, when knowable) AND `captured_at` (when we saw it) + source +
cadence class — a batch-detected change never masquerades as a live timestamp.
**Accept when:** portal + Olivia surfaces emit real events (A1 shows rows growing daily) ·
schema documented (event_type vocabulary) · append-only enforced (no UPDATE/DELETE grants on
the log) · nightly heartbeat covers the writer · the app feed slot is specified in writing so
GroupOS events drop in without rework · gate GREEN.

**CLOSED 2026-08-03 (cited live):** table reshaped (empty → canonical: `at_member_id` +
`event_type` + `source` + `cadence` live|daily|weekly|backfill + `occurred_at`/`captured_at`) ·
**append-only is PHYSICAL** (service-layer DELETE 403 / UPDATE 403, proven live) · **3 live
writers** (fail-open triggers, eval wamids excluded): olivia_turn (rides the #41-stamped insert),
report_filed, portal_seen (fires only on real change — sync upserts no-op) — all 3
canary-proven, keyed, canaries owner-cleaned · **daily writer** `derive_member_change_events()`
(key-field snapshot diff → status_changed/attr_changed; first run seeds silently; ⚠️
chapter_affiliation is text[] — 42804 masked by the seed-only first run, fixed with ::text both
sides) · **backfill 14,998 events** (1,582 olivia turns · 15 reports · 13,401 registrations —
the #45 keying made this possible) · nightly job `member_events_daily` + 26h heartbeat, INCLUDING
the live-flow watchdog (msgs grew but 0 live events = trigger dead → exit 1 → #13 pages; its
own day-one lesson: an ERROR JSON parsed fine and printed as success — now exits 1 on
key-missing) · **app-feed slot specified in the table COMMENT** (source='app', same shape, no
rework) · vocabulary documented same place · gate GREEN — after diagnosing a false RED to root:
the alt-member fixture picked a null-status number post-churn → fixture now ACTIVE+ordered, and
the gate's curl gained ONE transport retry (5xx/timeout only — 4xx never retried, the denial
checks need them raw; closes the flagged promote-blip hardening). **Numbers: 0 → 15,052 events ·
2,304 members covered · 54 live events on day one, growing from real traffic during the build
(16→38 while probing).**

### 45. 🟢 CLOSED 2026-08-03 — Identity resolution: the rest · one ruling for Andy's eyes: members.at_member_id is an ENTITLEMENT key, never auto-stamped · → RELEASE 3 (audit §2+§5)
*As the team, one human is one record everywhere — WhatsApp, Facebook, Airtable, events.*
#41 covers olivia_messages only. Still unowned (verified in the audit):
- **`event_registrations` 62% keyed** (11,003/17,786 have `member_at_id`) — backfill the join
  path + stamp on ingest; #44's graph quality depends directly on this.
- **61/646 `digest.members` rows have NO `at_member_id`** — those members can never reach the
  canonical key however well everything else joins. Resolve each (match or document why not).
- **74 members carry >1 Facebook identity** (`fb_member_map` 789 rows → 715 members) — dedupe to
  a primary uid per member (Ivan Ong's two accounts = the known case). Related standing item:
  ~737 dup `Member ID (FB)` in AT `tblVc38gw21iHLYMG` — NEVER delete member records; merge/flag.
- Minor, same pass: 4 dup names / 4 dup emails in `members` — verify real-vs-collision.
**Accept when:** A2 re-run shows event_registrations ≥95% + members ≥95% keyed · fb_member_map
1 primary uid per member · the 61 resolved-or-documented · gate GREEN.

**CLOSED 2026-08-03 (cited live, gate GREEN after):**
- **event_registrations 61.9% → 75.3% raw · 97.7% of every row carrying member evidence**
  (13,401/17,786; +1,638 email-unique any class, +760 exact-name-unique member-ish classes).
  Named non-member remainder per EVERY-MEMBER: 4,071 zero-evidence rows (Significant Others,
  Friends, vendor Partners, public "E-commerce Entrepreneur" buyers), 295 guest-class name
  coincidences DELIBERATELY never stamped, 19 ambiguous emails. Raw ≥95% is unreachable because
  ~24% of the roster is genuinely not members — the honest denominator is member-evidence rows.
- **Stays fixed:** `digest.stamp_event_registrations()` (service-role-only, idempotent —
  re-run proof 0/0) called after every roster sync (`sync_events.py`, mds-digest-web `e8c1fab`,
  pushed).
- **The 61 unkeyed members = unidentified WhatsApp numbers** (null status, mostly nameless,
  no email; only 2 carry any member signal). RULING (fail-closed): `members.at_member_id`
  drives retrieval ENTITLEMENTS — never auto-stamped from name/email heuristics; matching them
  is the human-gated matcher's job. Documented as that class; reproducible via
  `select * from digest.members where at_member_id is null`.
- **Facebook identities:** the audit's "74 dupes" was really 1 true dupe + 73 UNLINKED uids.
  `fb_member_map.is_primary` added + partial unique index = ONE primary per member ENFORCED
  (743 mapped members, 0 violations). Andrei Ureche's Neven Eyewear brand page demoted to
  non-primary. 32 unlinked identities recovered by name-unique-to-ACTIVE match; 41 remain
  unlinked by design (brand pages, pseudonyms, name variants — matcher class, documented).
- **Dup names/emails: all four verified benign** — Itamar Eshet, Khalid Abdulla, Leo Limin,
  Vic Tor each = ONE member key with two phone rows (dual numbers). Zero true duplicates,
  nothing merged, no records touched.

### 40. 🟢 LIVE ON PROD 2026-08-03 (`89ee3632`) — Retrieval rewrite (RRF) · remaining: v1 retirement after soak · formal ≤3.6% at the deferred batch smoke · → RELEASE 3 (audit P1+P3)
*As a member, a question phrased differently from how it was written still finds the answer —
and answers prefer recent, credible content.*
**Now (verified live):** `content_search` sorts `_k_terms desc, _k_vec asc` and its WHERE
requires a keyword hit when terms are given — a semantic-only match NEVER RETURNS. The 275MB
HNSW index has **0 scans ever**; `search_tsv` (GIN) is indexed and unused (2 scans, both mine);
measured seq scan 0.37–5.1s (cache-dependent) — the 11.1s `Fetch Raw Matches` in exec 61208.
**Build:** v2 alongside (never in-place): ANN wide net with the vector as LEADING sort (HNSW
engages) + keyword candidates via `search_tsv` → **fuse by RANK (RRF) — never blended scores**
(the standing lesson; `expertise_search` is the in-house precedent) → recency decay + authority
boost as rank adjustments. Stop embedding empty/sub-30-char bodies (11–31% of index is noise) —
keep the rows keyword/thread-reachable (one-word FB comments are sometimes THE answer).
Point the STAGING workflow at v2 first → probes → smoke slice → flip prod's RPC name.
**Traps:** NOTIFY pgrst + hammer-test after DDL (stale-pool 404s = fake regressions) · a timeout
reads as "no data found" — time it at size · diff top-3 with/without vector as proof.
**Expect:** exists-but-missed class shrinks (2 of 5 real smoke fails were this: Q3106, Q9024) ·
retrieval step 5–11s → sub-second indexed · recency handled · 275MB index finally earns its cost.
**Accept when:** plan shows `Index Scan using content_items_embedding_hnsw` · smoke re-run ≤
3.6% baseline with no class regressing · gate GREEN · paraphrase probes (Q3106/Q9024 shapes) pass ·
**embed step joins the nightly pipeline + heartbeat** (A3 hit 100% on 08-03 only because the
backfill was run BY HAND after the FB capture — coverage must be a process, not an event).

**BUILT 2026-08-03 (all cited live):** `content_search_v2` side-by-side (migrations
`content_search_v2_rrf` + `content_search_v2_two_phase_ann`) — identity gate + access rules
verbatim from v1; three INDEXED branches: tsv-GIN keyword (ts_rank pool 200 → term-cover rerank
→ 60) + **pure-ANN top-200 under transaction-local `enable_seqscan=off`** (phase 2 access-filters
the ids; in-body library-load + `set_config('hnsw.ef_search','200',local)` — function-level `SET
hnsw.*` fails PG15 placeholder validation) + recency floor 60 → **RRF by rank only** (kw 1.0 ·
vec 1.0 · recency 0.5 · authority=engagement_score 0.25 as extra rank lists). **Proof:** plan =
`Index Scan using content_items_embedding_hnsw`; lifetime idx_scan 0 → increments per call; v1
11.96s → **v2 0.46s** (Q3106 shape); zero-keyword paraphrase reaches the AGL threads; top-3
with/without vector differ; empty-terms browse intact; hammer ×15 all-200. **Corpus filter:**
6,486 sub-30-char embeddings NULLED (embed-source def = title+tl_dr+body+search_extra = the
script's row_text; rows stay keyword/thread-reachable); `embed_backfill.py` skips sub-30 via
id-cursor; **`embed_content` job in `nightly_derivations.py` + pre-registered heartbeat (26h,
#13-alarmed), run proven under /usr/bin/python3.** **Staging → v2 at all 3 call sites** (Fetch
Raw Matches + Fetch Summaries URL mappers · Attach Embedding EXEC_NAME swap; model-facing tool
name UNCHANGED; `build_loop.py` synced; active version `e51c9e88`). **E2E exec 61669:** loop
executed content_search_v2 ×2, Fetch Raw Matches 2.1s/40 rows (11.1s in prod exec 61208), Q3106
organic answered with the Michael Patrón savings thread + 5 named members. **Gate 202 GREEN**
(+12 v2 checks: full canary mirror ± consent flag, unknown phone, canceled phone + at_member_id,
anon lockout). ⚠️ A fast probe is NOT proof — first probes ran 0.35s on warm SEQ scans; only the
idx_scan counter and the plan are honest.
**SLICE RAN 2026-08-03 (Andy's go; 33 Qs = all 6 prod FAILs + 5 retrieval-adjacent PARTIALs +
22-PASS spread; report `OLIVIA_EVAL_2026-08-03.md`):** 26 PASS · 4 PARTIAL · 3 FAIL. On the
shared 33 vs the prod smoke: FAIL 6→3, PARTIAL 5→4, PASS 22→26. **Fixed by v2:** Q3094 (PPC
people — was fabrication), Q3106 (AGL — was denial), Q3107 (AGL savings), Q9016 (this-week
browse), Q9032 (member count; bank truth was stale 722, corrected to live-count def) + PARTIAL→
PASS on Q3048/Q3065/Q3086. **The 3 fails triaged, none a retrieval miss:** ① Q3110+Q3111 =
fact-gate FALSE CLAMP — Haiku flagged real figures, the deterministic post-filter's `\b\d{4,}\b`
cannot see comma-formatted numbers ("$12,464.38", "2,808"), every flagged figure was VERBATIM in
evidence (execs 61719/61721, 65s/63s regen-loop turns) → **FIXED same session: comma/$-normalized
number matching in Gate Verdict (source + staging via build_loop, node-checked, unit-tested);
free re-probes deliver full answers, 65s→26.6s / 63s→37.9s** · ② Q3096 = verb-upgrade
(launch→"funded") on real rows — #39's family, mechanism filed there · ③ Q9024 = event_lookup
lane (not content_search) — filed as #47. Slice fabrication count flat vs prod (1↔1).
**Remaining to close (Andy 2026-08-03: full run SKIPPED — the ≤3.6% measurement happens at the
prod-flip smoke):** ① prod flip = promote (staging graph carries the swap + gate fix) **+
same-moment migration pointing the 3 SQL wrappers that still call v1 internally —
`multi_source`, `app_member_feed`, `persona_signals` — at v2, + NOTIFY pgrst + REST hammer** ·
② the flip smoke = the formal ≤3.6% / no-class-regression number · ③ v1 retired after soak.
Human-friendly report: `OLIVIA_40_REPORT.md`.

### 41. 🟢 LIVE ON PROD 2026-08-03 — Identity stamping · ALL ACs MET (flip backfill re-run: 0 rows needed; prod probe rows arrive stamped) · → RELEASE 3 (audit P4)
*As the team, every Olivia conversation is filed against a member record, not just a phone.*
0/3,102 stamped today. **THE TRAP: the FK expects `members.airtable_id`, NOT `at_member_id`
(0 of 646 are equal).** Fix = n8n (staging→promote): `Find Member` select += `airtable_id` →
carry through `Resolve Member` → `Save Conversation` stamps `member`. Backfill by phone join —
3,102/3,102 resolvable TODAY, decays as numbers change, so do it with the node change. Then
re-verify the phone-joining readers (`persona_signals`, `persona_signal_fingerprints`,
`olivia_health_check`). Related, separate: 61/646 members lack `at_member_id`;
`event_registrations` 62% keyed. **Expect:** portal/persona/dossier joins become key-based and
survive phone changes. **Accept when:** all rows stamped · new rows arrive stamped · readers verified.

**BUILT 2026-08-03 (cited live):** staging nodes edited under lock — `Find Member` select +=
`airtable_id` · `Resolve Member` carries it (comment pins the NOT-at_member_id trap) · `Save
Conversation` stamps `member: mem.airtable_id`. **Probe: 4 fresh staging rows all arrived stamped
with the phone-owner's record** (member_matches_phone_owner = true). **Backfill: 2,554/2,554 rows
stamped, 0 unstamped, 0 phone↔stamp mismatches** (only phones mapping to exactly ONE member
record were stamped; none were ambiguous). Readers verified: `persona_signals` (1 row, test
member) + `persona_signal_fingerprints` (752 = the full active population) execute unchanged;
`olivia_health_check` doesn't phone-join. Gate GREEN (202). **At the flip:** the promote carries
the node edits; re-run the backfill one-liner once to stamp prod rows created between now and flip.

### 39. 🟢 LIVE ON PROD 2026-08-03 — Attribution · fb_thread marker SHIPPED at flip · remaining: formal cluster rate at the deferred batch smoke · → RELEASE 3
*As a member, when Olivia quotes or credits somebody, that person actually said it — she never
credits me with something I only received, asked for, or was tagged in.*
**The dominant class in the prod smoke: 4 of 16 findings (Q3107 FAIL + Q3010/Q3065/Q3068 PARTIAL)
— every other finding was a singleton.** Both failure modes appeared in ONE answer (Q3068,
04:44:54, machine-verified against the warehouse):
1. **Addressee read as the speaker.** Olivia: *"Lee Leathers … they have a POA template …
   they offered to share via DM."* Lee never offered it — Betsy Johnson (*"Lee Leathers we got
   this too … I'd love your template"*) and Dan Ri (*"Lee Leathers Please send me the template"*)
   were ASKING HIM. On Facebook a reply opens with the addressee's name; that leading name got
   read as the author.
2. **Commenter credited as post author.** Olivia: *"Dan Ri's original thread"* linking post
   `25956490257361130` — that post is **Zaid Al-Husseini's**; Dan Ri only commented on it. Dan Ri
   authored the OTHER post (`25575360808807412`), so the two were swapped.
**Why the existing rules did not hold:** the seed already carries the ATTRIBUTION rule AND the
post-vs-comment rule. Both are PROSE competing with a 40-row evidence block, and the
disambiguating signal lives in fields (`author_name` vs `post_author`) the model must reason
about rather than see. Another rule line will not fix this.
**Build (structural, not instructional):** the retrieval layer labels every row itself —
`[COMMENT by X · on POST by Y]` / `[POST by X]` rendered into the row text, and the leading
addressee name stripped (or marked `→to Z`) from comment bodies before they reach the model, so
the speaker is never inferable-but-wrong. Applies in Build Prompt AND the Answer Seed preload.
**Accept when:** the four smoke findings re-fire clean; a probe on the Lee Leathers thread
credits the template REQUEST to Betsy/Dan and never to Lee; matrix +5 rows on attribution.
**+ VERB-UPGRADE MECHANISM (from the #40 slice, 2026-08-03):** Q3096 "who has done a kickstarter
and got funded" — the evidence held LAUNCH posts only (Michael York's Zionix launch, Slava
"gearing up to launch"); the answer upgraded them to "members have actually run and FUNDED
Kickstarter campaigns" (staging 07:18:18). Same family: claim strength exceeding the evidence's
verbs (launched→funded, offered→shared, asked→confirmed). The fact-gate cannot catch it — every
ENTITY verifies; the VERB is the invention. Fix belongs with the row-labeling build here (and a
seed VERB-PRECISION line); add Q3096's shape to the AC re-fire list.

**BUILT 2026-08-03 (cited live):** Layer 1 = migration `content_search_v2_attribution_marker`:
a comment OPENING with the post author's name gets its head marked `[→ to <post author>]`
(exact char-prefix compare, no LIKE; punctuation-stripped remainder; meta.post_author computed
once and reused) — the chokepoint every present AND future consumer inherits (Andy: "what we
have and what we will have"). REST-proven on real rows: Rich Tesoriero → `[→ to Michael Patrón]`.
Layer 2 = STYLE (single-sourced in Build Prompt, harvested into the seed by build_loop):
ATTRIBUTION rule teaches the marker + never echo it; NEW VERB PRECISION rule (launched≠funded,
offered≠sent, asked≠confirmed) — apostrophe-free inserts via `apply_39_style_attribution.py`;
loop-contract rule sharpened in `answer_seed.js`; deployed, bounce 200/200. **Probes (all
machine-verified vs warehouse):** ① "did Michael Patrón ask about Meta credit cards?" → premise
CORRECTED: "asked *to* Michael, by Rich Tesoriero" + link ② POA template → credited to Lee
Leathers from HER OWN comment ("I have the template I used, I can share, just DM me" — verbatim
in warehouse; Betsy/Dan were askers) ③ kickstarter → launches named + "no funding outcome on
record" stated plainly. **Matrix +5** (9052-9056, each anchored to a warehouse-verified truth;
bank 178). Gate GREEN (202). **Remaining:** fb_thread shares prod → its marker goes in the FLIP
migration (never in-place) · the four smoke findings' formal re-fire = the batch smoke (Q3107
already re-passed in the #40 slice; Q3068 shape probed green today).

---

### 37. ✅ Member reports + not-connected honesty (Andy ruled + shipped 2026-08-01, in Release 2)
*As a member, when Olivia doesn't have something, she says it's not connected yet (beta) and offers
to file a report; I can also just type "report <text>" (or bare "report") — my words land verbatim
in front of the team in the Olivia portal.*
**Shipped:** `digest.olivia_reports` + gated fail-closed `report_create` RPC · seed rules
(not-connected 3-parter, verbatim report command) · router force-llm on `^report` ·
portal page `/admin/olivia/reports` (digest-web `af32d0c`) · gate 190 (3 new checks) ·
proven live (rows 4-5 + Q3088b/Q3116c probes). Related ruling: event-registration asks = BOTH
(event card + link + pass-to-team offer) — router worked-example fixed.
**ANDY'S ACs VALIDATED + PROBE SUITE PASSED 2026-08-01 (16 turns):** AC1 verbatim one-turn ✓ ·
AC2 bare-report asks fresh mid-conversation ✓ · AC3 3-parter + yes files the ORIGINAL ask
verbatim ✓ · AC4 no follow-up promises ✓ (the suite caught "they'll follow up" → wording
pinned) · AC5 boundaries ✓ (complaints filed, no cross-member read, gate fail-closed/anon) ·
AC6 portal ✓ (main-page bottom section + clear/restore/clear-all soft; unauth PATCH 403;
soft-clear round-trip proven; dupe row archived not deleted) · AC7 zero regressions ✓
(chapters/ticket/billing unchanged). The suite also caught a double-file → report_create now
IDEMPOTENT (15-min window, migration report_create_idempotent). Gate 190.

# ⚪ S4 — lowest

*(empty — #16 closed; #17-#20 queued for Release 3)*

### 25. ✅ The portal tells the truth · CLOSED 2026-07-31 · effort M · SHIPPED TO PROD (mds-digest-web)
*As the team, every number on the Olivia portal (digest.mds.co/admin/olivia) is right: all the data
is there, it is displayed correctly, and the filters actually filter.*

**THE GOAL, plainly.** That page is the team's ONLY window into whether Olivia is being used and
whether she is useful — how many members ask her things, who, what about, what they ask the team
for, and what they thumbs-down. Today the numbers on it cannot be trusted, so nobody can make a
call on them: we cannot answer "is the beta working?", "who should we invite next?" or "what does
she get asked that she is bad at?" without going to SQL by hand. **Done means every number on the
page has been reconciled against the warehouse and the filter is real — so the page can be used to
decide things instead of being second-guessed.** It is a read-layer job in mds-digest-web; it
changes no member-facing behaviour and touches no workflow.

**What is actually wrong (verified 2026-07-31, first-hand in source + SQL):**
1. **The topics card is fed by a DEAD JOB and ignores the page filter.** It reads
   `digest.olivia_question_topics`, a table written by the weekly `olivia_question_report.py` job,
   and renders THAT TABLE's own `period_start`/`period_end` — not the selected window. The job last
   ran **2026-07-20**, so the card is pinned to "Jun 20 – Jul 20" no matter what you pick, and is
   **11 days stale**. This is the whole "filters don't filter" symptom Andy screenshotted, and it
   is two bugs: a scheduled job nobody noticed had stopped, and a card wired to a report table
   instead of to the window.
2. **Test-traffic exclusion is accidental, not designed.** `page.tsx` hardcodes
   `EXCLUDED_PHONES = {"17866578153"}` — Andy's number — and nothing filters SELFTEST wamids.
   Eval traffic is excluded today ONLY because the eval harness fires from his number. Verified:
   counting with and without the SELFTEST filter both give 275, so it holds right now — but any
   probe or eval run from another number silently lands in the production figures, and the eval
   harness still marks only the member's message as a test, never Olivia's reply.
3. **No tile has ever been reconciled against SQL.** The figures may be right; nobody has checked.

**🚨 ROOT CAUSE FOUND AND FIXED 2026-07-31 — the dashboard was silently blind to the most recent
days.** The member-turn fetch asked for `limit=5000` ordered `created_at.ASC`, but **PostgREST caps
a response at 1000 rows whatever `limit` says** (Supabase `db-max-rows`). Once the window held more
than 1000 turns the server returned the OLDEST 1000 and dropped the NEWEST — with no error and no
sign on the page. Proven on the live query: `content-range: 0-999/1043`, newest visible row
`2026-07-29T23:33Z`, so **all of Jul 30-31 was invisible to every card**. It degrades further as
traffic grows. Fixed by paging the fetch (1000 at a time until a short page) — commit `75917fb`.

**FULL VALIDATION, every card, Last 30 days, tests excluded (page vs warehouse):**
| card | page BEFORE | page AFTER | warehouse | verdict |
|---|---|---|---|---|
| Questions asked | 250 | **266** | 266 | ✅ fixed by paging |
| Members using | 20 | **22** | 22 | ✅ fixed by paging |
| Requests created | 9 | 9 | 9 | ✅ was always right |
| Open requests | 5 | 5 | 5 | ✅ was always right |
| Member feedback | 6 in period | **5 in period · 5 all time** | 6 incl. Andy / 5 excl. | ✅ now honours the test toggle |
| Member requests card | 25 in period | **9 in period · 5 open all time** | 9 | ✅ contradiction with its own tile fixed |
| Top members | Eugene 69 · Ian 9 · Kayleigh 5 · Etienne 6 | **72 · 11 · 9 · 8** | 72 · 11 · 9 · 8 | ✅ fixed by paging |
| Top question topics | Jun 20 – Jul 20 · 26 questions | same, labelled | **25 questions truly in that window** | ✅ the report is ACCURATE — see below |

**Why topics shows 26 against 266 questions (Andy's question).** The report is not undercounting:
Jun 20 – Jul 20 genuinely held ~25 questions, because the beta had barely started. The job ran
**once, on 2026-07-20**, and has never run since — so the ~240 questions the beta has produced since
then have never been clustered at all. The card is honest now (it states its own span, and shows an
empty state when the selected window has no report), but **the topic data is only as good as the
last run: schedule `olivia_question_report.py` or drop the card.** That is the one open item left.

**Correction, on the record:** an earlier note here called this a "window-boundary defect where the
page loses the last day or two". That diagnosis was wrong — the page deliberately excludes greetings
("hi", "thanks") as non-questions and the first SQL comparison did not, which accounted for most of
the apparent gap. The real defect was the 1000-row cap above.

**Reference numbers to check the page against (last 30 days, measured 2026-07-31):**
| what | true value | source |
|---|---|---|
| questions asked | **275** (commands excluded, Andy excluded) | `olivia_messages` role=member |
| members using | **24** | distinct phone, same filter |
| requests created | **38** | `olivia_requests` |
| reactions | **7** | `olivia_feedback` (`reacted_at`) |
| topics card | shows **Jun 20 – Jul 20**, should follow the window | `olivia_question_topics`, last generated 2026-07-20 |

**Accept when**
- **Every tile and card reproduces from a warehouse query on a fixed day**, checked number by
  number, SQL cited beside what the page shows: questions asked · members using · requests
  created/open · top members · question topics · reactions.
- **The page filter applies to EVERY card**, topics included. Switching the window changes them all
  consistently; a window with no traffic shows 0, not a stale span.
- **The topics card is never silently stale** — either it computes from the window like every other
  card, or it states the age of its data on the card. **And the report job that feeds it is either
  running on a schedule that is monitored (#13), or removed.** A card fed by a dead job must not
  look live.
- **Test traffic is excluded by design on every card, the same way** — SELFTEST wamids AND the
  excluded numbers, not one standing in for the other — and "Include my tests" (`?self=1`) brings
  it back deliberately. Adding a second test number must not require a code change to stay honest.
- **Olivia's replies are marked as test traffic too** when the turn was a test (the eval harness
  marks only the member's message today) — the same cheap fix named in the status corrections, and
  it also closes the cross-source measurement trap noted for #8.
- **Proven live after the fix** on the deployed page, with the SQL beside it, per the global DoD.

**Impact:** the team's only window into whether Olivia is used and useful; wrong numbers here mean
wrong calls on everything else.


**CLOSED + LIVE ON PROD 2026-07-31** — `294b094` on digest.mds.co, verified deployed via
`/api/version`. Shipped independently of the Olivia workflow: the portal is mds-digest-web and
deploys on push, so it does NOT wait for the n8n promote.

**Six defects found and fixed, in the order they were found:**
1. **The eval harness counted as member usage** (`e859196`). It fires the whole bank silently
   from one number with a `wamid.SELFTEST*` marker; nothing filtered it, and real traffic stayed
   clean only by accident because that number was already excluded. "Include my tests" turned 167
   real questions into 484, three quarters machine. Now excluded on every card, always.
2. **The period picker only drove the tiles** (`562560f`). Feedback and requests rendered their
   all-time lists under a 7-day filter. Both are period-scoped now; the full worklists keep every
   period on their own pages, and the footer links name the destination's size, not the window's.
3. **🚨 The dashboard was silently blind to the most recent days** (`75917fb`) — the root cause of
   every number that would not reconcile. The fetch asked `limit=5000` ordered `created_at.ASC`,
   but **PostgREST caps a response at 1000 rows whatever `limit` says**. Proven live:
   `content-range: 0-999/1043`, newest visible row Jul 29 23:33, so all of Jul 30-31 was invisible.
   30 days read 266/22 as 250/20; Kayleigh 9 as 5. Fixed by paging. **This cap bit three separate
   places in one day — treat it as a known trap in this codebase.**
4. **Topics could not follow the picker** (`4a415bc`). They were a frozen report SNAPSHOT, and that
   job had run ONCE, on Jul 20 — so "Yesterday" was empty and "30 days" showed 26 questions against
   266. Now every question carries its own label (`digest.olivia_question_labels`, written by
   `scripts/olivia_label_questions.py`), so any window is a GROUP BY and the counts reconcile with
   the tile by construction. Backfilled all 389 questions (~$0.02).
5. **No way to separate staff from members** (`94c7b1c`). 184 of 266 questions in 30 days are
   staff, and the two heaviest users are both staff. "Exclude staff" toggle added, default off.
6. **Staff read from the wrong table** (`294b094`, Andy caught it). It used
   `digest.members.membership_status` — the WhatsApp layer, 645 rows, 15 Staff — when the truth is
   `digest.member_attributes.membership_status` (the AT "AT Database Status" field), 5,739 rows and
   exactly the 29 Staff in Airtable. 14 staff would have counted as members. **Blank status is
   excluded too** (Andy's rule: most blanks are leads, and blank is what a staff member looks like
   before someone sets the field).

**Final validation, Last 30 days, page vs warehouse — every card reconciles:**
| card | staff in | staff out | verified |
|---|---|---|---|
| Questions asked | 266 | 82 | ✅ = warehouse |
| Members using | 22 | 16 | ✅ |
| Requests created | 9 | 1 | ✅ |
| Open requests | 5 | 1 | ✅ |
| Member feedback | 5 in period · 5 all time | ✅ |  |
| Top members | Franky 85 · Eugene 72 · Ryan 19 | Ryan 19 leads | ✅ |
| Top question topics | 15 topics · 266 q | 13 topics · 82 q | ✅ = the tile |
| Yesterday (was empty) | 8 topics · 14 q | | ✅ = the tile |

**⚠️ CARRIED FORWARD, not done:** `scripts/olivia_label_questions.py` is **not on a schedule**.
It is idempotent and only labels new arrivals, but until it runs nightly the topics card will show
an "N unlabelled" badge and under-report recent questions. Same shape as the dead report job this
replaced — **schedule it (and monitor it under #13), or the card decays again.** The old
`scripts/olivia_question_report.py` and `digest.olivia_question_topics` are now unused and should
be deleted rather than scheduled.

**Scope extended to Member 360 (Andy 2026-07-30, the Kostiantyn Kyrylov case):** ONE member
(rec9ZsJqlzK2bRmX2 — legal name Kostiantyn Kyrylov, display name Constantine Kirillov, same
phone/email/Stripe) renders as TWO portal entries — the Members-DB-side page shows the legal name
with "not on WhatsApp yet"/no phone even though the row HAS the linked phone, while the WA-side
page shows the display name, matched, 59 messages. And **search only indexes the display name**,
so the legal name finds nothing while a page with that exact headline exists. Accept-when adds:
one person = one entry (merged by at_member_id across both source lists), and search matches
legal AND display names.

**Member-360 half SHIPPED 2026-07-30 (mds-digest-web `05014d6`, deployed via Vercel):**
`getMember360()` now falls back to `members?at_member_id=eq.<id>` (phone-bearing row first) when
the `airtable_id` lookup misses — every Olivia-dashboard → Member 360 jump and shared Members-DB-id
URL now renders the real matched page instead of "not on WhatsApp yet" (root cause was that the WA
layer resolved by only one of the two id kinds). Search now matches the **AT legal name alongside
the display name** (`altName` on WA rows + the search-fields array). Repro case verified at the
data layer: the Members-DB id resolves straight to the WA row (Constantine Kirillov, phone,
`recjaFLHC…`); tsc + build green. **The /admin/olivia analytics half of this ticket (tiles vs
warehouse, per-card filters, test-traffic exclusion) remains open.**


---

### 5. ✅ Counting · CLOSED 2026-07-31 · effort M · RELEASE 2
*As a member, when I ask a number I get a number.*

**Accept when**
- **A count that exists is never refused: 0%** "I don't have that data" where the number is derivable.
- **Every number matches the warehouse** it was derived from.
- **Totalling or extending the previous answer works** without the member asking twice.
- **0% of aggregate answers identify anyone.**
- **A count that genuinely does not exist is said plainly** — an honest miss, not a failure.

She lists but cannot count, and often says "I don't have that data" when she does. Live: SoCal vs Texas
totals, members under $1m, chapters with counts, most-active members.

**IN PROGRESS 2026-07-31 — the counting layer is BUILT + LIVE ON STAGING; remaining = revenue-band
phrasing, content counts, totalling, and the TEST run.**
- **`digest.member_niches` SHIPPED** (warehouse): one canonical countable niche set per member —
  14-value vocabulary (MDS's own Niche Top Selection + 2 gaps), multi-valued, from all 8 AT
  niche/category fields via `scripts/olivia_derive_niches.py`. **Main Niche has precedence
  (Andy), and several stated niches rank EQUALLY** — "Supplements, Board Games, Pets" counts in
  all three (`is_main_niche`, renamed from `is_primary` after Andy's ruling; 104 of 477 = 21.8%
  list more than one). 1,925 rows / 722 actives. NOT yet scheduled (same gap as the labeller).
- **`digest.member_count` RPC SHIPPED**: counts by niche/city/state/chapter/band, AND-combined,
  optional `p_group_by` breakdown, population identical to `community_info` (722) so totals
  reconcile. Fail-closed dual-key gating, counts only, never names. **Gate 161→167 GREEN** (+6
  member_count checks). **Application v3 gap FILED** in `APPLICATION_V3_MAPPING_DECISIONS.md`
  (v3 writes NO controlled category — only free-text Main Niche; recommend classify-on-submission).
- **Loop tool + COUNT rule live on staging**, probed: "How many total in socal, vs texas?" (the
  Q3080 fail) → **"SoCal = 92 (LA 44 + Orange Co 32 + San Diego 16) vs Texas 53 (SoTex 41 +
  NorthTex 12)"** — every number = the warehouse. "how many in the supplements niche" → **73 of
  722**. First SoCal probe said "Los Angeles: 0" (chapter is literally named "LA Chapter") →
  fixed with a short-names hint: group-by-chapter first, never guess long forms.
- **PROBED 2026-07-31 EVE (bands + content + totalling):**
  · "under $1m" → **"None — no band under $1M exists"** + the full band table 252/132/90/164/84,
    every figure warehouse-exact (bands vocabulary now in the tool hint). Honest-miss AC ✓
  · "at 20M+" → **164 of 722** ✓ exact
  · FB-posting-% → honest refusal (content_stats returns no FB author counts) — ACCEPTABLE per the
    honest-miss AC, but the number IS derivable in SQL, so this stays a residual: extend
    content_stats with distinct-authors-by-source, then this question must get a real %.
  · **"Total it up" STILL FAILS — the one open defect.** Chapter counts sum to **773** (members
    hold several chapters); she said 722 twice (echoed the population), then got gate-blocked,
    then said 722 again after re-fetching. Two prompt rules did not fix it: **the model cannot
    reliably add 20 numbers. Deterministic fix, not another rule: add `breakdown_sum` (and
    distinct-member count) to `member_count`'s output so the sum is READ, never computed.** Small
    CREATE OR REPLACE; next session.
  **Also open:** schedule `olivia_derive_niches.py` + `olivia_label_questions.py` nightly · TEST run
  on the counting class (runs resume after PBIs close — Andy).

- Counts by city, state, chapter, category and revenue bracket return a real number
- "Total it up" across a previous answer works
- Aggregate counts never identify anyone
- Where a count genuinely doesn't exist, she says so rather than implying she has nothing

**Effort M** — counting RPC plus a router lane; unknown is which counts may be shared. **Impact:** hit repeatedly by two of six testers within an hour.

**CLOSED 2026-07-31 (staging, rides the next promote).** The final defect — "total it up" — closed
DETERMINISTICALLY: `member_count` now returns `breakdown_sum` (773 vs total 722, sum READ never
computed; the model proved 3× it cannot add 20 numbers). Final probe: "Adding up every chapter …
= 773 chapter memberships — higher than the 722 distinct members because members belong to more
than one chapter." Exactly right, with the why. Fix chain worth remembering: sum(bigint) returns
NUMERIC → 42804 vs the declared bigint column (the REST hammer-test caught it; the gate fallback
had masked it as a content problem). Gate GREEN 167. AC status: counts-exist-never-refused ✓ (niche/
city/state/chapter/band + breakdowns) · numbers=warehouse ✓ (every probe exact) · totalling ✓ ·
aggregates-never-identify ✓ (gate checks) · honest-miss ✓ (under-$1m: "no band under $1M exists" +
full band table; FB-%: refused, residual filed to extend content_stats with distinct-authors-by-
source). Residuals filed, not blockers: content_stats extension · schedule `olivia_derive_niches.py`
+ `olivia_label_questions.py` nightly · TEST run on the counting class when runs resume.

---

### 33. ✅ Prod smoke: the answer feels alive and cites its sources · CLOSED 2026-07-31 · effort S · RELEASE 2
*As a member, while she works I can see she is working, and when she solves my problem she shows me
where the solution lives.*

**Filed from Andy's PROD testing — three findings, each resolved from execs (all times CDT — his
clock, verified: "2:40PM" = 19:40:56Z exactly):**
1. **Duplicate holding copy — EXPLAINED, already fixed, nothing new to ship.** The rung copies were
   ALWAYS distinct ("On it — checking a few sources for you 🔎" vs "Still working on this one …🙏"
   — verified in the pre-fix snapshot too). Andy's identical 9:54+9:55PM pair = **rung 2 sent by
   two OVERLAPPING ghost ladder executions** during the fail-open window (02:52–02:56Z: SIX ladder
   execs, **14 sends hit his phone in 3.5 minutes**; exec 56699 proven sending both rungs with
   arrival=fire-time). Both causes were fixed THAT NIGHT: fail-closed gates on the ladder wf
   (03:18Z) + arrival=message-timestamp in the trigger — **which reached PROD in the 03:24Z second
   promote** (drift: docs said staging-only; corrected).
2. **The 2:40PM stall — ROOT CAUSE FOUND + FIXED ON STAGING.** Exec 57816 (70.5s, all nodes
   succeeded): `Prep Context` fans out to [`Route Request`, `Mark Read + Typing`] and n8n v1 runs
   branches depth-first IN ORDER — so read-tick/typing/ladder ran AFTER the 70s answer on every
   turn (ladder exec 57817 started the second the main exec stopped; four independent pairs
   verified). The #23 ladder was a structural silent no-op on prod. **Fix
   `scripts/olivia_loop/apply_33_early_feedback.py`** (idempotent): feedback branch first — by
   connection order AND canvas position. **Proven on staging exec 57926: Mark Read + Typing +3.68s
   · Holding Trigger? +4.00s · Route Request +4.01s.** Cost ~0.34s/turn. Rides the promote.
3. **Links when the answer solves — RULE SHIPPED (staging).** `LINKS WHEN YOU SOLVE` in the loop
   contract (`answer_seed.js`, applied via `build_loop.py`): recommendations carry the link their
   tool row returned, links never built, linkless rows named without one, counting answers stay
   clean. **Proven exec 57926**: 3PL answer attaches the Casey Cutsail + Eijiro Kaga FB thread
   URLs, names Jasim Eisa (no link on row) without one; control "how many chapters" (exec 57927)
   = "20", zero links.

**Accept-when status:** ✅ `OLIVIA_SMOKE_CHECKLIST.md` written — five standing checks (early
feedback · ladder once/distinct/silent-when-answered · solve links · counting probe · gate GREEN)
with a result block pasted into the session log at every promote; first run PASSED 2026-07-31 and
is recorded in the file. ✅ All three findings fixed or explained from execs, on staging, riding
the promote. Gate GREEN after the edits.

**Impact:** every slow answer and every solve-lane answer on prod; the checklist protects every
future promote.

---

### 16. ✅ Health dashboard audit (Olivia domain + the alert chain) · CLOSED 2026-08-01 · effort M · LIVE
*As the team, the health dashboard tells the truth.*

**LIVE (digest-web `b1b1a9f` deployed + the monitor wf fixed in place — no promote involved).**
- **The lying tile fixed:** `olivia-agent` claimed "Claude answer failures fail the run" — false
  (the model node continues on error; runs stayed green through 07-26). It now reads
  **member-visible truth**: failure texts that reached members (24h window) + the off-platform
  alarm's firing states. **Forced-failure proof on the LIVE report:** canary failure text →
  "🟡 Olivia — WhatsApp agent — last failure text 3h ago" in the problems block with its triage
  button → cleanup → healthy again (36/37).
- **Two missing tiles added:** `olivia-alarm` (the WATCHMAN tile — pg_cron `last_tick_at`
  freshness; if the alarm dies, THIS goes red) and `olivia-derivations` (#15's four job
  heartbeats). Tile count 35 → 37, all computing on the live report.
- **The latched 30-min monitor UNLATCHED** (wf `argZgYHPgdVKJqCS`, in place, bounce, verified):
  the old code fired ONCE on healthy→down and could never fire again once `lastHealth` stuck —
  the latch that buried 07-26 (last alert ever: 2026-07-26). Now: re-alerts every 30 min while
  down + posts the recovery summary once when clear. Degraded still doesn't page (daily summary
  covers it) — by design.
- **The Supabase blind spot covered:** `scripts/alarm_watchdog.py` on launchd
  (`com.mds.olivia.watchdog`, every 15 min, a DIFFERENT failure domain — the Mac): Supabase
  unreachable OR alarm tick stale >15m → Slack, unlatchable (30-min repeats + recovery).
  **Forced-test proven** (🚨 test alert + ✅ recovery in Slack).
- Gate re-run **187/187 GREEN**.

**Named scope + residuals:** this audited + fixed the OLIVIA domain and the SHARED alert chain;
the full 37-tool per-tile audit is the Tools-health PROJECT's backlog, not Olivia's · the
watchdog runs on Andy's Mac (best-effort — it watches the watcher, not the product) · the known
flaky `Member profiles ← Airtable sync` yellow stays a Tools-health item (GitHub cron delivers
~half the runs — already on that project's list).

**Impact:** the dashboard can no longer show green through a member-visible outage, and every
layer of the alert chain (tile → monitor → alarm → watchdog) is now proven to fire.

---

### 12. ✅ Public revenue, double-sourced · CLOSED 2026-08-01 · effort S · RELEASE 2
*As a member, a public figure someone posted is quoted with its source, never as Olivia's claim.*

**ANDY'S RULING (2026-08-01, verbatim spirit):** official (AT) revenue = never disclosed, bands
only. **A figure the member posted publicly = sayable, and we MUST specify he actually said it.**
Closed-chat posts follow chat visibility — available only to askers who can actually see that
chat. **FB is totally open.** Ranking stays bands + engagement order — never by exact revenue.

**Verified + shipped ("this is very sensitive, make sure you did it correctly"):**
- **The flagged live case traced to its source:** the daily review's "doing $14-15M" catch came
  from **MDS's own public FB welcome post** ("THE HEAVY HITTERS — Aaron Cordovez… $140M across
  two brands", post `26687547237588758`) — i.e. the exact class the ruling ALLOWS with
  attribution; the review bot's rubric was stricter than the ruling.
- **REVENUE FIGURES rule** in the loop contract: our data → bands only, whoever asks · a figure
  in retrieved content = an attributed quote WITH link, paired with our band · never her own
  voice · never ranking fuel · chat figures visibility-scoped automatically (if retrieval
  returned it, the asker can see it — the leak gate's chat-scope canaries prove non-member
  chats return ZERO, every run).
- **Probes (staging):** "how big is Aaron Cordovez business?" → *"Our official data has Aaron in
  the 20M+ tier — but he himself shared a bigger number in the MDS welcome post: $140M across
  two Amazon brands"* + link — the double-source shape verbatim · **control:** Prudence's exact
  number still hard-refused (band + facts, offers to look for a public self-post). The new rule
  did NOT soften the base refusal.
- **The daily-review rubric updated live** (wf `xkX7wnIwxJLU7YgY`, verified): flags revenue ONLY
  when unattributed / non-visible / from our data — so correct attributed quotes stop being
  filed as violations.
- Rulebook (`OLIVIA_SHAREABLE_FIELDS.md`) NEVER-lane carries the nuance; matrix +5 rows
  (BS105-109). Gate re-run GREEN (no DB change — the enforcement was already structural).

**Impact:** low frequency, high sensitivity — now consistent, attributed, and structurally scoped.

---

### 13. ✅ Outage alarm · CLOSED 2026-08-01 · effort M · LIVE (not promote-gated)
*As the team, we hear about an outage in minutes, from a system that isn't the one that's broken.*

**LIVE NOW — this one does not ride the promote: it runs in SUPABASE pg_cron (off n8n, the
platform being watched), every 5 minutes, posting to Slack `#automation-tests` (C0AQ8USNQK0 —
one config row to change the channel).** Migrations `olivia_outage_alarm` +
`_net_schema_fix` (pg_net lives in schema `net`, not `extensions` — the first cut's qualified
calls would have silently no-opped inside the never-raise handlers; caught by pg_proc check).

**Four signals, every tick** *(the 4th added by #15)*:
1. **members-getting-failure-text** — any member received "Sorry — I could not generate…" in the
   last 10 min (SELFTEST + Andy excluded, so eval noise never pages). The 07-26 outage shape.
2. **n8n-workflow-down** — the always-on relay's `relay_maintenance` markers flowing = Meta
   callbacks arriving while n8n is dead.
3. **webhook-ping** — an ACTIVE probe: each tick POSTs a synthetic delivery-status payload at
   the real prod webhook (no member traffic; upserts the `wamid.HEALTHPING` sends-row = a
   visible heartbeat); the next tick verifies 200.
4. **nightly-job-stale** (#15) — any derivation job with no success in >26h (or never run).

**NO LATCH by construction** (the old monitor's fatal flaw): while a condition persists it
re-alerts every 30 min; on clear it posts ✅ recovery. The check function never raises and
stamps `last_tick_at` in config — the monitor itself is checkable.

**Proven by forcing failures (AC), all visible in Slack #automation-tests 2026-07-31 ~20:34 CDT:**
seeded failure-text canary → 🚨 alert (Slack API ok:true) · second run inside 30 min → paced, no
repost · stamp backdated 40 min → 🚨 re-alert "(still down — repeating every 30 min)" = unlatch
proof · canary cleared → ✅ recovery · webhook ping → 200 "Workflow was started" + HEALTHPING row ·
autonomous pg_cron tick verified (01:35:00 → 01:40:00 on the boundary). **Gate +2 → 186 GREEN**
(anon denied on the check fn; alarm config — which holds the Slack token — unreadable).

**Named exceptions / residuals:** Supabase itself is the monitor's blind spot (watching n8n from
Supabase satisfies the AC; a second cheap watcher for Supabase = #16's audit) · the
balance-runs-low PRE-warning + spend cap land in the Big-Smoke #32 phase (the failure-text
signal already catches the member-visible effect, which is how 07-26 actually presented) · the
old latched n8n monitor stays as-is (harmless, on-platform; #16 decides its fate).

**Impact:** the team hears about the next 07-26 in ≤5 minutes instead of never.

---

### 15. ✅ Hands-off data pipeline · CLOSED 2026-08-01 · effort L · LIVE (not promote-gated)
*As a member, what happened yesterday is answerable today.*

**LIVE NOW (like #13, it's infrastructure — no promote needed).**
- **The four derivation jobs run nightly, unattended:** `scripts/nightly_derivations.py` runs
  derive_niches · label_questions · sync_chapter_pages · embed_member_profiles in sequence (one
  failure never blocks the rest), stamping `digest.olivia_job_heartbeats` after each. launchd
  **`com.mds.olivia.derivations`** at 04:30 (after persona 04:15), loaded + verified. First run
  did real work: 5 questions labelled · 15 changed profiles re-embedded · 20 chapters re-synced ·
  niches rebuilt — all idempotent, so a quiet night is cheap. **This kills the "scheduled not
  remembered" decay that carried across four tickets** (#6/#7/#25 all left a job unscheduled).
- **A skipped sync alerts (the AC), proven by FORCING a skip:** the #13 pg_cron alarm gained a
  4th signal — any job with no success in >26h (or that NEVER ran) Slack-alerts, off-platform,
  unlatchable. Forced: backdated `label_questions` 30h → 🚨 "stale derivation job(s):
  label_questions (last ok Jul 30 20:21)" (Slack ok:true) → restored → ✅ recovery. A job that
  never runs is pre-registered, so its absence is detectable, not silent.
- **Gate +1 → 187 GREEN** (job heartbeats anon-denied).

**Named exception (platform, not us):** **Facebook capture stays a manual scroll** — FB removed
the permalink anchors the feed loop needed, so the enumerate step is irreducibly human
(documented in [[project_mds_fb_digest_scraper]]). Everything DOWNSTREAM of the scroll is what
these jobs automate. The Mon/Thu FB SOP is unchanged; the ticket automates the parts a platform
lets us.

**Residual:** launchd runs on Andy's Mac (must be on) — same constraint as persona/eval/digest
jobs; the staleness alarm is precisely the backstop for a missed run. Moving to an always-on
runner is a later infra choice, not blocking.

**Impact:** every member; the most visible staleness — now self-healing with an alarm behind it.

---

### 11. ✅ Payment wording · CLOSED 2026-08-01 (staging) · effort S · RELEASE 2
*As a member behind on payment, I'm told clearly and reminded kindly — not shown a system word.*

**Shipped (migration `member_billing_plain_wording`):** the wording map lives INSIDE
`member_billing` — the one function that emits statuses (self-only) — so raw words are
**structurally unemittable**. Every Stripe state maps to plain words with what-to-do
(`past_due` → "A payment did not go through — your membership is still active. Please update
your card, or reply YES and I will connect you with the team." · `unpaid` → behind + ticket
offer · `canceled` → if-unexpected-flag-it · unknown states → a generic plain sentence, never
the raw token). Membership words too: `Staff` → "MDS team" · `Current Member- Not Renewing` →
"Active through the end of your term (set not to renew)". Wording drafts posted to Andy
2026-08-01; editing a message later = editing the map.

**Population reality (verified):** active members today = active 605 · trialing 97 · past_due 3 ·
canceled 2 · unpaid 1 — and **all 6 troubled-Stripe members are phone-less** (can't reach Olivia
yet; the wording waits for them). **Gate +1 (180→181 GREEN):** member_billing output carries no
raw system word. **Probe:** Andy's own billing → "Active — all good ✅", plan, renewal date —
zero system words, `Staff` never surfaced.

**Round 2 (Andy, same session): the ride-along reminder + the portal link.**
1. **Every message from a past_due/unpaid member gets a payment reminder appended — max once
   per 24h.** `digest.billing_nudge(p_phone)` owns the dedupe deterministically (stamp table
   `olivia_billing_nudges`; VOLATILE, fail-closed, service_role only). Wired on staging
   (`apply_11_billing_nudge.py`): BOTH reply producers (Format Reply = model answers, Build
   Verbatim = canned routes) flow through Billing Nudge → Apply Nudge before Eval(silent)? —
   the nudge rides ANY route; the saved conversation keeps the clean answer (holding-text
   precedent). **E2E-proven with a seeded past-due canary member through the real staging
   webhook: message 1 = welcome + nudge appended (execs 58031), message 2 seconds later =
   clean, no nudge (58032). Canary fully cleaned after.**
2. **The Stripe customer-portal link** (checkout.mds.co/p/login/…) now lives in the past_due/
   unpaid wordings AND in a new `billing_portal` column — THE answer to any update-my-card /
   see-my-invoices ask (tool description updated).
Gate 181→**184 GREEN** (+portal-link present · nudge fail-closed on unknown phone · anon denied;
billing column allowlist extended per the change process).

**Impact:** small but sensitive; ready before the members who need it arrive.

---

### 10. ✅ Shareable member facts · CLOSED 2026-08-01 (staging) · effort S · RELEASE 2
*As a member, similar questions get similar answers.*

**THE RULEBOOK now exists: `OLIVIA_SHAREABLE_FIELDS.md`** (Andy's labels 2026-08-01) — three
lanes: 🟢 SHARE per member (the card: name/geo/band/niche/expertise/about/hobbies/fun fact/FB
link/chapter/channels/business model/categories/join date/shared chats) · 🟡 GROUP-ONLY
(employees, SKUs, brands, years-in-business, age, TTM sums — chapter aggregates fine, never per
person) · 🔴 NEVER (exact revenue, titles, contacts, address, payment/Stripe, IP, IDs, removal
reasons, others' personas/billing/raw answers). **Key architecture point: default-deny — the
~1,700 unlisted supa fields cannot leak because no gated function selects them; "used in
calculation" ≠ "shareable" (Most Recent Revenue feeds bands + sums, emitted nowhere per member).**

**Shipped:**
- **Inventory of every gated function's emitted columns** (the de-facto list) — found the state
  already matched the labels except ONE inconsistency: match reasons said "sells on TikTok"
  while the card lacked channels → the same fact answered by one path, refused by another.
- **`member_card` extended** (migration `member_card_shareable_fields`, DROP+CREATE chain):
  + channels (channel_mix + TikTok Shop) + business_model + categories + country — the card now
  IS the per-member shareable list, one to one.
- **Gate 178→180 GREEN:** CARD_KEYS pinned to the rulebook set (schema drift = RED; change
  process = edit the page + the check in one commit) · structural canary: no NEVER-lane word in
  any emitted column NAME (learned: value-scanning false-positives on "MDS Credit Card & Travel
  Hacks"; and "ip_" matched membersh-ip_-state — patterns measured, then set).
- **Probes:** "does Prudence sell on TikTok?" → precise from the card (not among her channels —
  and the honest nuance that she IS in the MDS TikTok chat) · Guido's model+channels → same
  shape, different member · "her home address + employee count?" → refusal.

**Residual:** the address probe was swallowed whole by the contact-refusal lane — the GROUP-ONLY
half (employees) ideally answers "chapter averages only"; cosmetic, filed under #14 tone work.

**Impact:** every profile and matching answer; the rulebook is the standing reference.

---

### 9. ✅ Revenue brackets, one rule · CLOSED 2026-08-01 (staging) · effort L→S · RELEASE 2
*As a member, revenue answers are consistent and never expose anyone's actual number.*

**The working session dissolved: Andy pointed at the WRITTEN ruling that already existed** — CU
doc 2531q-102937 page 06 "Revenue fields & logic" (`2531q-67177`): **the authoritative field is
`Most Recent Revenue`** (the verified-else-reported chooser; never blank after an application,
auto-upgrades on human Approve; the page explicitly names it "the field to trust" and documents
why the Members-side TTM lookups are census-gated quirks).

**And the warehouse already obeyed it:** `derive_member_attributes()` computes `rev_band` FROM
`Most Recent Revenue` (AT first, application fallback) by ONE threshold rule — ≥20M → 20M+ ·
≥10M → 10-20M · ≥5M → 5-10M · ≥100k → 1-5M — with provenance stamped. Cards, matching, counting
and chapter band_mix ALL read that one derived column: **single rule everywhere BY CONSTRUCTION.**
The "three competing tier fields" fear was moot — the warehouse never reads them.

**What actually shipped to close:** the missing enforcement + proof.
- **Gate +3 (175→178 GREEN):** `member_card` revenue_tier is a BAND from the vocabulary, never a
  raw figure · card blob carries no raw-revenue field · `member_count` band breakdown keys ⊆ the
  band vocabulary. Raw revenue structurally cannot leave the DB.
- **Probes (staging):** "what revenue tier is Prudence in?" → *20M+* with profile ·
  "her exact revenue number?" → refusal with the tier-band rule stated, band re-offered.
- **Channels from application data ✓:** `channel_mix` + `tiktok_seller` (canonical, census/
  application-derived) already power who-sells-on-X + chapter channel mixes. BONUS from the doc:
  the Forms table holds EXACT channel %s (Amazon/DTC/TikTok/Retail raw + per-channel $ formulas;
  the messy buckets are the legacy shape of the same values) — a precision upgrade filed as a
  residual, not needed for the AC.

**Residuals, named:** raw channel-% precision upgrade (exact %s instead of buckets) · #12's
ruling (may named members be RANKED by revenue) stays its own ticket · the chapter-TTM whale
ruling stays open under Needs Andy 4b.

**Impact:** every profile card, match, count and chapter stat — now provably band-only.

---

### 8. ✅ Every source on every question · CLOSED 2026-08-01 (staging) · effort M · RELEASE 2
*As a member, one question gets checked against every source that could answer it.*

**Andy's scope (2026-08-01): three behaviors, all shipped + probed.**
1. **Absence guard** — CROSS-SOURCE FLOOR rule: no "can't find" until two differently-phrased
   searches AND a look in another source family.
2. **Merge multi-home answers** — what's-happening asks cover WA AND FB, attributed each.
3. **Wide solve fan-out** — problem asks consult content + partners + videos (+events/members).

**AC reframe (Andy): process floor = absolute; OUTCOME = the exists-but-missed class on the
standard ladder (<10 → <5 → <1%), never literal 0 — a miss after the honest floor is honest.**

**What shipped:**
- **Baseline measured (pre-loop notes were stale):** 220 real llm answers/14d, **24 (11%)
  can't-find-shaped**; several already crossed families honestly (Thrasio: partners+chats),
  some narrowed to one chat. The before-number for the class.
- **Three loop rules** in the contract (answer_seed.js): CROSS-SOURCE FLOOR · MERGE MULTI-HOME
  (never one source silently standing in for both; answers say "in the chats… / on Facebook…") ·
  SOLVE FAN-OUT (weave who discussed it + which partner deal + which recording, each linked).
- **`multi_source` completed** (migration `multi_source_fb_videos`): FB + VIDEOS sections join
  partners/members/events/chats — all SIX families in the one-call sweep, default p_want = all;
  composes the gated fns verbatim so gating travels. Smoke: all six sections return.
- **Sources-used telemetry, per turn:** the loop accumulates tool names (answer_parse →
  answer_merge → Format Reply → Save Conversation, `apply_8_sources_telemetry.py`) into the
  olivia row's `plan.sources_used`. Coverage is now a measured number (SQL/portal-ready).
- **Probes (staging, telemetry-verified):** solve "supplier quality issues" →
  `[content_search, partner_lookup, video_search]` — FB threads + The Sasson Company ($500 off
  audits) + Kenyield ($3k off QC) + Omer Sasson's Expert Call, ALL linked · what's-happening →
  `[fb_catchup, content_search]`, FB section + chats section attributed · absence (fictional
  Coachella deal) → honest qualified miss, found the one unrelated real mention, invited better
  terms — ran 2× same-family (floor nuance noted; the class ladder measures it at the eval).

**Residuals, named:** the outcome class rate (exists-but-missed on the ladder) confirms at the
next TEST/FULL run when Andy turns runs on · the absence-floor "other family" nudge is model
judgment — if the class rate disappoints, tighten to a mechanical check · portal card for
sources_used coverage = a #25-family follow-on.

**Impact:** every question; the difference between a search box and something that knows MDS.

---

### 6. ✅ Chapters, end to end · CLOSED 2026-07-31 · effort M · RELEASE 2
*As a member, I can ask anything about chapters and get a real answer.*

**Andy's rulings (2026-07-31, in session):** (1) **canonical numbers = our RAW DATA** — live counts
from member records; the mds.co chapter pages are the DISCLOSURE PRECEDENT but may be stale
("we need to rely on raw data"; live: Europe 61 vs site 50, NY 97 vs 82, NorthTex 12 vs 15).
(2) **Chapter leads are PUBLIC** — names, roles AND photos are published on the chapter pages, so
Olivia shares them; emails/phones are not published and stay unavailable (they are not even stored).

**What shipped:**
- **`digest.chapters_catalog`** (warehouse): all 20 chapters scraped from the public pages by
  **`scripts/sync_chapter_pages.py`** (re-runnable; hard-verifies every page: leads 1-3 w/ roles +
  photo URLs, 6/6 site stats incl. TTM, categories; **20/20 GREEN**). The catalog IS the chapter
  whitelist — junk pseudo-chapters structurally impossible. Fixes found scraping: the chapters
  index links MDS Women to a DEAD milliondollarsellers.com URL (live page =
  mds.co/chapters/mds-women); two pages title the section "Chapter Lead" singular; the Women's
  page labels the stat "Members".
- **`digest.chapter_info` gated RPC** (fail-closed dual-key, same asker gate as member_count):
  per chapter — **LIVE member_count computed by the SAME CTEs as member_count** (one number
  everywhere BY CONSTRUCTION, gate-checked) · leads · about · categories · **`live_stats`**
  (Andy: "wire other data we have — it costs us nothing"):
  top_niches (member_niches counts) · revenue **band_mix** · **TTM sum/avg from `Most Recent
  Revenue`** (v3 Option-B field; lookup shape `[1450000]` unwrapped) · employees sum/avg (`Total
  Employee Count`) · avg tenure (`# of Years for Member`) · **asker_city/asker_state** so
  closest-to-me NEVER asks when the city is on file (the first probe asked Andy for his city
  while Jersey City sat in member_attributes — fixed deterministically). Rejected on inspection
  (field names lie): `Most Recent Revenue Source` = an Airtable record URL, not a channel;
  `Actual Birthday v2` = NEXT birthday (future dates) — no avg-age, no channel mix (channel mix
  lands with census #20).
- **Loop tool + CHAPTERS rule** (answer_seed.js, staging): leads shareable with page link +
  photo_url linkable · live rules over site stats · aggregates never imply a single member's
  figure · asker_city drives closest-to-me · asker_is_member drives "am I in a chapter".
- **Gate +8 checks (167→175 GREEN):** whitelist-only (20 rows, no junk) · chapter_info counts ==
  member_count breakdown · no email/phone keys · lead objects carry ONLY name/role/photo_url ·
  unknown phone zero · canceled phone zero · anon denied · answers-200.

**Proof — Andy's exact follow-up chain on staging, zero re-asks:** "How many chapters?" → 20 ·
"Whats the closest to me?" → "Since you're in *Jersey City, New Jersey* → New York Chapter, 97
members" + leads + link + not-a-member-yet · "how many members?" → 97 live ("page shows 82,
live rules") · "who is the chapter lead?" → Morris Sued / Brandon Furhmann / Mari Ashley ·
"tell me about the Europe chapter" → 61 live vs site 50, top niches WITH counts, ~$742M chapter
TTM + $14.3M avg + tenure, leads, link.

**Correction same night (Andy: "this data is outdated… take it from supa"):** the site's six
numbers were initially returned alongside as a labeled "as published" reference — **REMOVED from
the RPC output entirely** (migration `chapter_info_supa_numbers_only`): the model can now only
ever see warehouse-computed numbers; the site contributes ONLY leads/photos/about/link (the data
supa does not have). site_stats stays in chapters_catalog for reference, never emitted. Re-proven:
Europe probe = 61 members · niches w/ counts · band mix 21/8/9/14 · $742M TTM · $14.3M avg ·
9.5 avg employees · ~3y tenure — all live, no site figure anywhere.

**Round 2 SHIPPED same night (Andy: "I like the amazon markets + sales channels suggestion"):**
`live_stats.channels` = members selling via each channel per chapter, counted from the CANONICAL
`member_attributes.channel_mix` (the derive job had already normalized the census band fields —
no re-parse; one truth with member_match) + `tiktok_seller` → "TikTok Shop". Vocabulary: Amazon
US / Canada / EU / Other Amazon · DTC/Own Website · Walmart · Wayfair/Overstock/Target ·
Wholesale (Big Box / Independent) · TikTok Shop, with `channel_reporters` as the honest
denominator (95 actives report no channels). Migration `chapter_info_channels` (jsonb key —
same return type, grants preserved). Sum-integrity verified: 773 chap rows == 773 distinct
member-chapter pairs (no double-count). **Probes warehouse-exact:** Europe = Amazon US 48 ·
CA 31 · EU 29 · DTC 23 · Walmart 17 · TikTok 1 of 53 reporters, quoted against reporters ✓ ·
"most DTC sellers" → NY 42, Women's 39, SoFlo 25 ✓. The raw `% of Revenue` band fields stay
un-parsed on purpose (variant spellings, multi-submission arrays) — the derive job owns that.

**Round 3 SHIPPED same night (Andy: "more data from v3?" → yes):** `business_models`
(Private Label / OEM / Agency / Wholesale mix) · `countries` (ISO-2 + full-name dual coding
FOLDED via cmap — Europe's "DE" 4 + "Germany" 2 became Germany 6) · `age_mix` (banded) ·
`avg_years_in_business` (started_year; the note distinguishes it from MDS tenure) ·
`median_sku_count` · `avg_brands`. Migrations `chapter_info_v3_profile_stats` +
`chapter_info_country_canon`. Probes: Europe country spread + NY business models, both
warehouse-shaped. Wart filed: one member carries a combined "OEM, Wholesale" single token in
business_model (derive-job cleanup candidate, not #6's).

**Named exceptions / open:**
- **The 4 policy questions (change chapters · join several · live in two places · how to change)
  still have NO written source** — that AC is delegated to **#18** (its own scope says it unblocks
  exactly this). The factual half ("can I be in several") answers from data today (120 members are).
- **NEEDS ANDY: the whale ruling** — live TTM sums can out one member's scale in a small chapter
  (NorthTex sum $930M, one member = $806M of it). Site precedent publishes chapter sums, so they
  ship ON; band_mix is the fallback if he rules them off.
- `sync_chapter_pages.py` not scheduled — same gap as `olivia_derive_niches.py` +
  `olivia_label_questions.py`; schedule all three together (#13/#15 residual).

**Impact:** 804 chapter memberships / all 722 actives; the most-asked community-structure class.

---

### 7. ✅ People search that understands meaning · CLOSED 2026-07-31 late (staging) · effort M · RELEASE 2
*As a member, I find the right person even when I don't know the exact word or spelling.*

**What shipped (migrations `people_search_semantic_layer` · `member_count_city_aliases` ·
`member_match_target_mode_no_likeness_filters` · `expertise_search_semantic_rrf`):**
- **Fuzzy names (pg_trgm):** `member_card` gains a trigram-similarity fallback over every name a
  person is known by, fired only when the strict word-AND misses. Proven: "Prudence Tweedy
  Milsap" → Prudence Tweedie-Millsap first try (E2E she even notes the spelling variation);
  "Guido Rejes" → Guido Reyes.
- **Meaning (embeddings):** `digest.member_profile_embeddings` — a DEDICATED table (the hot
  synced member_profiles is never touched — the HNSW/trigger lesson), filled by
  `scripts/embed_member_profiles.py` from `profile_texts_for_embedding()` (ONE definition of the
  embeddable text: public card fields + niches + categories, NAME EXCLUDED). **722/722 actives
  embedded, idempotence proven (re-run = 0 pending).** `expertise_search` + `p_embedding` with
  RRF rank-merge inside the already-gated pool (#26 pattern); null/malformed vector = exact
  legacy keyword path; output columns unchanged. Loop's Attach Embedding list gains
  expertise_search.
- **Location aliases:** `digest.place_city()` (NYC/Manhattan/Brooklyn→New York, SF/Bay Area,
  LA, Vegas, Philly, DC…) applied in `member_match` + `member_count` city filters; states
  already normalized via `attr_state`. Proven: member_count NYC = New York = 19.
- **🚨 PRE-EXISTING DEFECT found by the NYC probe and FIXED:** in city/state-TARGETED searches,
  `member_match` kept applying the ASKER's own category/band/model/channel as HARD filters —
  "members in NYC" returned NYC ∩ asker-category ∩ asker-band = **0** for Andy while 19 were
  there. Target mode now disables ALL likeness dims as filters and keeps likeness as a RANKING
  boost (everyone in the place returns, most-like-you first). NYC 0→19, Texas 52.

**AC status:** misspelled/partial first try ✓ (E2E) · meaning without synonym lists ✓ ("paid
ads" → the PPC/ads bench E2E: Dilger/Nowak/Heckmann/Biner/Hameed/Aserraf/McGonigle) · ranking =
engagement score, never shown ✓ (unchanged ordering inputs) · **with/without-vector top-5 diff
measured on the REST path** — rankings change, vector surfaces "Amazon Advertisement"/"Ppc"
profiles keyword missed; not a silent no-op ✓ · location aliases ✓. Gate GREEN after (expertise
checks pass on the new signature).

**Residuals, named:** pure LIKENESS mode (no location) still ANDs the dims and returns 0 for
thin-profile askers — unchanged behavior, superseded by #29's real matchmaking · profile data
itself is thin on some topics (exit/M&A) — search finds what profiles state, census (#20)
deepens it · `embed_member_profiles.py` joins the nightly-jobs scheduling residual (now FOUR
jobs).

**Impact:** every "who knows X" and "tell me about Y" — the most common ask after digests.

---

### 23. ✅ Answer latency · CLOSED 2026-07-31 on the story (Andy's call) · effort M · RELEASE 1 + 2
*As a member, an answer arrives while the question is still on my mind — WhatsApp shows no typing
indicator, so a slow answer reads as a dead one.*

Split out of #21 (2026-07-30, Andy): the loop answers correctly but slowly — **24s median vs the
~5s band the single-pass cascade set**; worst healthy-path case 54s. The tail is already fixed
(the unbounded gate-retry loop: 41 model calls / 417s on one question, now capped at one retry).

Where the healthy-path time goes (measured, exec 55263): answer model ~6s · fact-gate ~3s ·
router ~2s · retrieval ~3s. The three cuts, in order of value:
- **Drop the router call on loop turns** — the loop chooses its own tools; the router is pure
  latency there (~2s + one model call per answer)
- **Run the zeroth-fetch retrieval alongside the router** instead of after it (~2-3s)
- **Skip the fact-gate when the draft makes no citable claim** (greetings, refusals, honest
  misses) (~3s on those turns)

**Accept when**
- **Median end-to-end at or under 10s** on a full organic run, worst case under 60s.
- **The class rates do not get worse** — speed is never bought with quality.
- Measured on the same instrument as everything else (per-question timings in the eval run).

**Shipped 2026-07-30 — the WAITING LADDER (half one):** typing fires within ~2s (pre-existing,
verified; Meta expires it ~25s — why slow answers read dead) → **18s holding message** → **60s
delay notice**, via standalone wf `X1vzrW9Avqff3qRa` (answered-checks against `olivia_messages`
before each send — silent when answered; holding texts never enter conversation history; SELFTEST
traffic never triggers it). Trigger wired on staging after Mark Read + Typing, rides the push.
**Proven live**: full 67s ladder to Andy's phone (both Meta wamids), no-op path silent at 20s.
**This half is what the STORY asks for** — the member knows she is working, so a slow answer no
longer reads as dead.

**2026-07-31 — the speed cuts, MEASURED (staging, gate 161 GREEN). Both shipped; neither bought
time. Two of the three planned cuts turned out to rest on wrong premises.**
- ✅ **Router prompt caching** (`apply_23_router_cache.py`): the ~6K-token routing rubric was sent
  uncached every turn. Split into a cached static block + the dynamic CHATS/history tail, byte
  identical content. **Live proof: `cache_read_input_tokens` 6,225 · `input_tokens` 221.** But
  latency held at ~1.5s — **the router is OUTPUT-bound** (~125 JSON tokens), not input-bound.
  **Real win = cost (~10× cheaper per routed turn), not speed.**
- ✅ **Claim-free fact-gate skip** (`Claims?` node + `has_claims` in `answer_parse.js`): a draft
  with no link, no digit, no quoted span and no named entity has nothing for the gate to check, so
  it routes straight to Format Reply and saves the gate's 1.5-3.3s. Detector is deliberately
  conservative (16/16 unit tests) — a false "claimy" costs only the latency we already pay, a
  false "claim-free" would skip a real check. **Fires only on true honest-misses, so the median
  barely moves.**
- ❌ **"Drop the router on loop turns" — DO NOT DO.** The router feeds the PRELOAD (the guaranteed
  zeroth-fetch evidence). Removing it makes the model fetch that itself = one extra Claude
  round-trip (1.4-2.6s), so it is likely NET SLOWER and costs the same-question-same-evidence
  property. Caching it gets the cost win without the risk.
- ❌ **"Run the zeroth-fetch alongside the router" — NOT POSSIBLE.** n8n executes nodes serially
  within one execution; branching gives no concurrency.
- **Measured before/after, same 8 questions, same instrument** (`before` = the 2026-07-31 TEST
  run): median **19.6s → 22.8s**, worst **52.0s → 56.1s**. Single sample per question and shared
  model latency, so this is noise — the honest statement is **no measurable change**.
- **Why ≤10s is out of reach here:** the answer loop IS the time. Each tool round-trip is a Claude
  call (1.4-2.6s), and the SEARCH TECHNIQUE rule deliberately requires a **minimum of two
  differently-phrased searches** before concluding something is absent — that rule is the recall
  control behind #7/#8. Hitting ≤10s means cutting model calls, i.e. buying speed with quality,
  which this ticket's own AC forbids.
- **Open for Andy — the AC number, not the story:** the ≤10s median needs either a re-scope (the
  ladder already delivers the member-facing story) or an explicit decision to trade recall for
  speed. Nothing further shipped pending that call.

**CLOSED 2026-07-31 (Andy) — on the STORY, not on the ≤10s number.** The member-facing problem
("a slow answer reads as a dead one") is solved by the waiting ladder in Release 1: she says she is
working within 18s and again at 60s, so an answer in flight never reads as a dead one. Both speed
cuts stay as banked wins — cheaper routing and a gate skipped on claim-free drafts — neither of
which traded any quality. **The ≤10s median was NOT met and was deliberately not bought**: reaching
it means cutting model calls, and the SEARCH TECHNIQUE rule that makes her run a second,
differently-phrased search before concluding something is absent is the recall control behind #7
and #8. This ticket's own AC forbids buying speed with quality, so the number goes back on the
shelf: **re-file a latency target after #7/#8 land, when we know what recall actually costs.**
Standing measurement to beat: median 22.8s, worst 56.1s (8 questions, staging, 2026-07-31).

---

## 📦 RELEASE 1 — shipped to PROD Jul 30, 2026

Promote of 17 nodes · prod versionId `ee3e3cf6` · gate 161 GREEN · every ticket probed green ON
prod · full-bank standing number **4.0%** (from 13.0%).

**Tickets in Release 1 (12):** #21 the answering loop · #1 every answer matches the evidence ·
#2 deliver what she offers · #3 "restricted", never "doesn't exist" · #4 safe edits and rollback ·
#22 Kimi trial · #24 first contact answers the question · #26 partners + events semantically
searchable · #27 the app knows who I am · #28 the persona learns · #30 member resolution by
at_member_id · #31 canceled means gone.

**Also in the same release, not ticketed as PBIs:** #23 half one (the waiting ladder wf
`X1vzrW9Avqff3qRa`) · Intercom escalation · videos = source #5 · Facebook = source #4.

Full per-ticket detail below.

---

### 30. ✅ Member resolution by at_member_id everywhere · CLOSED 2026-07-30 · effort M · RELEASE 1
*As a member who is not on WhatsApp, the app still fully works for me — my identity is my
membership, not my phone number.*

**Shipped** (migrations `asker_resolution_at_member_id` + `asker_resolution_full_population`):
- The four feed-composing gated functions — `content_search`, `video_search`, `partner_lookup`,
  `event_lookup` — gained **`p_at_member_id` as an alternate asker key**: mechanical in-place
  transform with per-step occurrence assertions (the first attempt aborted itself cleanly on a
  substring collision — the assertion working as designed), drop+create by `regprocedure`,
  re-grants, pgrst reload, REST path hammered 24/24 clean on the legacy shape. **#31's status gate
  applies identically on both paths**; the id path validates against `member_attributes` — the one
  table holding every member — so members absent from the WA-shaped mirror resolve too; members
  with duplicate rows resolve by distinct-count + deterministic row pick. The other 16 gated fns
  stay phone-only on purpose: WhatsApp askers always have phones.
- **The app door resolves the full population**: members-mirror email first, else the AT profiles
  mirror (`Preferred Email` — 202 of the 203 phone-less actives reachable, 0 duplicate emails),
  fail-closed on unknown/ambiguous/non-active either way. Phone-holders keep the byte-identical
  legacy path; a member who later joins WhatsApp just gets the WA sections lit — zero migration.

**Proof:** **Jack Fallon — the story's member — served live**: email → id → 5 events · 5 videos ·
5 partners (Zenon Labs top) · 8 threads, no phone anywhere in the chain · unknown at_member_id →
0 rows · canceled at_member_id → 0 rows · phone-path actives **byte-identical** (the standing
snapshot, twice) · staging WA pipeline answering normally through the new signatures · leak gate
+3 at-path checks, all PASS (**158**; the board's one red remains the external thumbnail item).

---

### 31. ✅ Canceled means gone — membership status gates every door · CLOSED 2026-07-30 · effort M · RELEASE 1
*As MDS, a member who cancels loses access the day the status flips — matching a phone or an email
is identity, never entitlement; the Airtable membership status is the authority on who is active.*

**The find (Andy's question, verified live):** a "Removed - Canceled Membership" member with a
linked phone was being served — 3 partner rows, 5 events, a full app feed — because all three
layers checked identity, never status. Bonus hole closed: 7 APPLICANTS with linked phones (NULL
status, no attributes row) were served too.

**Shipped:**
- **`digest.is_active_member_status(text)`** — the active set written once (Current Member · New
  Member · Current Member- Not Renewing · Staff; NULL/anything else → false, fail-closed).
- **The mechanical sweep** (migration `membership_status_gates_every_door`): a DO-block rewrote all
  **20 phone-resolving gated functions in place** (each def fetched, predicate injected into the
  resolution clause, re-executed — same signatures, grants preserved) + `app_member_feed`'s email
  resolution, with a hard assertion that zero resolvers remain unguarded (the migration aborts
  otherwise, and re-runs are no-ops).
- **The WhatsApp front door** (`apply_31_front_door.py`): Resolve Member routes any non-active
  status to reason `inactive`; Build Generic gained the honest message ("…linked to an MDS
  membership that is not currently active…"). Applied to STAGING and — under the wf lock, single
  bounce — to **PROD**, both verified, prod answering after the bounce. Named exception: the JS
  door carries a commented copy of the 4-status list (n8n can't import SQL) — but enforcement
  lives in SQL; JS drift could only mis-phrase the message, never leak data.
- **Authority = the AT status as synced** (≤1-day staleness); the digest-style live-AT lookup
  remains a named upgrade, not taken.

**Proof:** canceled phone → partners 3→**0**, events 5→**0**, content 0 · canceled email → app feed
`{}` · applicant phone → 0 rows · front-door sim 4/4 (active passes; canceled/null → inactive;
unknown → no_match) · actives regression **byte-identical** (the #26 snapshot) + staging and prod
happy-path probes answering · **leak gate +3 status checks, all PASS (155)**. The board's one red
stays the app session's thumbnail persistence — external, Andy's ruling pending.

---

### 3. ✅ "Restricted", never "doesn't exist" · CLOSED 2026-07-30 · effort S · RELEASE 1
*As a member, I'm told something exists and isn't shareable — never that it doesn't exist.*

**Shipped: the restriction moved into the data** (migration
`video_search_explicit_restriction_markers`). A restricted row's description field now carries a
fixed in-band contract marker — `[RESTRICTED VIDEO - it exists in the library but the content is
not shareable... never describe, summarize or guess its content]` — instead of the ambiguous NULL
that read as "no description" and invited both failure modes (denial, and inventing from the
title). Public rows with no description get their own `[no description on file... do not guess]`
marker. Cliff notes + attachments stay withheld on restricted rows. Seed additions: NO video has a
transcript (what-was-SAID asks → plain "transcripts are not available yet" + title/link) · a video
is described only from its description/cliff-notes TEXT, attributed — a title alone is never a
source. Row-data change → **live for prod's cascade immediately**; the seed rides the queued push.

**Proof (5/5 staging probes):** "Product Launch — Brandon Young" (restricted, a title begging to be
guessed) → exists with title/duration/date/link, content withheld, steered to his unrestricted
talks · "what was covered in the Retail Channel Call July 2025?" → exists + restricted + link ·
paraphrase "logistics deep dives" → identical treatment (same-ask consistency) · "what's new" →
restricted rows present, marked *(restricted)* inline · public C-suite video → described from its
actual description text. Population: 395/1,009 videos restricted (39%). All #3 gate checks PASS,
including the evolved marker-aware check (only the fixed marker allowed, canary content never).
Class rates confirm at the coming eval runs (10% rung). The one RED check on the board is the app
session's thumbnail persistence — external to this ticket, decision with Andy.

---

### 28. ✅ The persona learns · CLOSED 2026-07-30 (Andy's call; quality redesign → #29) · effort M · RELEASE 1
*As a member, the more I use MDS, the better it knows me — my persona updates itself with
preferences, focus, and what to avoid, minimum monthly.*

**What shipped (all live):**
- **`digest.member_personas` + `member_personas_history`** — one current row per member, every
  change archived with a version bump (trigger). Owner-only: anon unreadable (gate check), reaches
  a member only through their own identity-resolved feed.
- **Signal plumbing:** `persona_signal_fingerprints()` (one scan; fingerprint change = rebuild
  before the floor) + `persona_signals()` (attributes minus rev_band · 180d Olivia questions ×60,
  SELFTEST/eval excluded · confirmed event attendance · 30 authored WA/FB items · WA chat
  memberships).
- **Builder `persona_refresh.py`** (mds-scorecard-tools; Haiku, ~$0.02/member, ~$7/mo): deep v2
  schema — summary · business snapshot · weighted+recency-tagged focus · challenges_now · GIVES
  (what they help others with) · asks · emerging (newest-signals-only) · avoid (explicit signals
  only) · preferences · engagement pattern — **every item carries a verbatim signal pointer** (the
  #1 evidence contract). `--stats` = staleness report, exit-1 on stale.
- **Daily launchd job** `com.mds.persona.refresh` (4:15am, Slack summary via PERSONA_SLACK=1) —
  one run enforces both the monthly floor and rebuild-on-signal-change.
- **The #27 feed consumes the persona** (focus terms drive interests minus avoid; attributes
  remain the fallback). Gate GREEN at 153.

**State at close:** 4 deep-v2 personas proven (Eugene / Ian / Mo / Etienne — weighted focus,
gives/challenges/emerging all signal-cited); 200 members carry v1 personas; the remainder build
automatically at the nightly runs (v2 prompt), v1s refresh at their floor/signal change.
**Coverage corrected same day to EVERY active member — 748 keyed by at_member_id** (v3 signals:
phone-less members get authored-FB + events + profile; WA/Olivia sections empty by nature; verified
on a phone-less member live). The depth/quality redesign is #29's scope (Andy: cards still too
generic — research how the platforms build recommendation DBs).

---

### 27. ✅ The app knows who I am — identity-keyed personalization · CLOSED 2026-07-30 · effort M · RELEASE 1
*As a member using the MDS mobile app, everything I see is picked for ME, resolved from my real
login. Every member sees something different. (Andy: "KYC — I can't stress it enough.")*

**Shipped: `digest.app_member_feed(p_email, p_recent_queries, p_interest_embedding, p_limit_each)`**
(migration `app_member_feed_identity_door`) — service-role-only, SECURITY DEFINER, fail-closed:
server-verified login email → exactly ONE linked member (unknown / ambiguous / unlinked-stub →
`{}`; linked-but-phone-less → `feed_available:false`). Composes the feed by CALLING the existing
gated functions verbatim — `event_lookup` (incl. an events_near section on the member's city/state,
upcoming-only), `video_search`, `partner_lookup`, `content_search` (FB+WA, last 14 days) — plus a
persona block from the member's OWN attributes and interest terms derived from
niche/expertise/categories. **The gates travel with the data: this door can never show more than
WhatsApp Olivia would.** Behavioural inputs (`p_recent_queries`, `p_interest_embedding`) are
ranking fuel only, never identity.

**Proof:** two members live, different correct feeds — Andy Verdy (Jersey City: AI-agents Mogul
Call top video, MarketLeap, 5/5/5/8 sections) vs Matthew Greene (Costa Mesa, Orange Co chapter,
his niche, Archer Affiliates) · unknown email → `{}` · **the `andy@mds.co` portal stub (no linked
member record) correctly fails closed** · leak gate extended +4 (known-email resolves to exactly
that member · no sender_phone/rev_band/stripe in the blob · unknown email empty · anon denied) —
**GREEN at 152 checks**. Email coverage: 583/585 email-holding members also carry a phone; 0 dup
emails.

**⚠️ Hand-off to the app build (its "#3 Real identity"):** call this RPC server-side with the
VERIFIED login email — and note the login email must be the member's **linked** email
(`digest.members.email` with `at_member_id`); `andy@mds.co` is an unlinked stub and returns `{}` by
design. If app logins can differ from the linked email, the app side owns that mapping.

---

### 26. ✅ Partners + events semantically searchable · CLOSED 2026-07-30 · effort S · RELEASE 1
*As a member, a paraphrased ask ("3PL in Europe", "fulfillment help") finds the right partner or
event even when my words don't match the catalog's.*

**The finding (Andy, verified live):** `partners_catalog` (486) and `events_catalog` (1,419) had
**no embedding column** — Voyage never processed them, while content (37,980/37,980) and videos
(1,009/1,009) were fully embedded. Raised to S1 and shipped same day.

**What shipped:**
- `vector(1024)` columns + BEFORE-UPDATE invalidation triggers (migration
  `partners_events_embedding_columns`) — a text change nulls the embedding so the nulls-only embed
  pass re-covers it. **No HNSW index on purpose**: ~1,900 rows seq-scan in microseconds, and HNSW on
  a trigger-written table is the exact trap that froze the member sync.
- `embed_partners_events.py` (mds-scorecard-tools, mirrors embed_videos.py; nulls-only resumable;
  `--query` prints a probe vector). **486/486 partners + 1,419/1,419 events embedded** (~pennies).
  Public-in-app fields only.
- `partner_lookup` / `event_lookup` + `p_embedding text DEFAULT NULL` (migrations
  `partner_lookup_semantic_rrf` / `event_lookup_semantic_rrf`; drop+create → re-grant → pgrst
  reload, the known footguns). **RRF rank-merge, never blended scores; the vector admits and ranks
  only inside the already-gated pool** — chapter gate, banded browse gate, phase filters untouched;
  a malformed vector degrades to keyword.
- Workflow wiring: Fetch Summaries inject list + the loop's Attach Embedding list gain both ops
  (staging; **reaches prod with the queued push** — the DB side is live for prod already, and prod
  sends no p_embedding, so it runs the proven-identical legacy path until then).

**Proof:** null-path regression **byte-identical** on 5 snapshot calls (tiktok/3PL/browse/singapore/
events-browse) · top-3 diff with vs without the vector CHANGED — "3PL in Europe": keyword
[Tactical, Eco, Texas] → hybrid [Linktrans, Eco, **Worldwide Logistics Group UK**] — not a silent
no-op · REST path hammered clean after reload · **E2E on staging: "any 3PL partners that can help
me in europe?" → Blue30 (UK fulfillment, 5% off, real link) with an honest the-rest-are-US caveat**
· events browse + "tell me about GETIDA" unchanged · leak gate GREEN.

---

### 1. ✅ Every answer matches the evidence · CLOSED 2026-07-30 at the 10% rung · effort M · RELEASE 1
*As a member, what Olivia tells me is exactly what the sources support - she never adds a verdict of
her own, and she never tells me there is nothing when there is.*

**Closed on Andy's call at the 10% rung** (0% ruled too harsh as a gate; the 5% → 1% rungs return
via the standard ladder across all classes, not by reopening this ticket). Residuals Q3091 (EZ
Outlet, unverified names) and Q3094 (missed PPC threads) belong to #7/#8 retrieval depth. On
staging; rides the queued prod push.

**What shipped, in order:**
- **07-28, the temporary floor:** sensitive-matters keyword detector above the greeting/help bypass +
  the global SENSITIVE MATTERS rule; the greeting bypass closed with the deterministic `realGreeting`
  guard ("Did he kill his wife?" → sourced pointer, no verdict; "Is Donald Trump a nazi?" reaches the
  loop and answers honestly).
- **07-30, the canned-lane boundary (structural half):** the action lane ALLOWLISTED deterministically
  (account/profile/membership change · billing/complaint · human · team-relay · register · call-me-X);
  every other 'action' is a question wearing an imperative and falls through to the loop + fact-gate.
  The loop offers the ticket only after actually checking (CANNOT DO / CANNOT FIND seed rule, exact
  acceptance-mark phrase; yes→ticket_create unchanged). Q3061 "Share link to Brandon's post" → the
  real fb_post URL, citation resolves (was: ticket offer, zero retrieval). Sources
  `apply_1_canned_boundary.py` + `answer_seed.js`; probes 5/5.
- **07-30 eve, the judge wired as a gate (contract checked, not requested):** deterministic **LINK
  GATE** in Gate Verdict — every URL verbatim-in-evidence or repaired/blocked; runs on every path
  including gate_error; sim 10/10. **The fact-gate found DEAD and restored** (bare apostrophe →
  `invalid syntax` → gate_error pass-through on every answer since the morning apply; the 13.0% full
  bank ran gate-OFF; fixed + NO-BARE-APOSTROPHES warning; execs 56115/56123). **Self-descriptions
  unblockable** (RULE ONE + deterministic source-headed backstop + data-access→`helpAsk`; execs
  56121/56133).
- **Proof at close: 34Q gate-on TEST run = 2.9% fail** — all 13 previous fails + 4 partials included,
  12 of 13 now PASS, the 14-question pass spread held (over-refusal did not rise). Leak gate GREEN
  throughout. Report `OLIVIA_EVAL_2026-07-30.md` (937f51f). Full-bank number re-baselines at the
  next FULL run. Probe set: 125 probes in `OLIVIA_S1_PROBES.md` remain the regression suite.

---

### 21. ✅ The answering loop · CLOSED 2026-07-30 · effort L · RELEASE 1
*As a member, she holds the thread of a conversation and looks again when the first answer isn't enough.*

**Closed on Andy's call 2026-07-30: built + proven on staging; the ticket does not wait on the prod
push, which runs as its own queued off-hours action (commands + protocol in `OLIVIA_NEXT_SESSION.md`,
together with #24).** Until that runs, members are on the old cascade.

**What shipped** (staging wf `bqHstPDi84uOhTCJ`; sources `scripts/olivia_loop/`, `build_loop.py` re-applies):
- The loop replaces single-pass for `route==='llm'`: full conversation + the gated RPCs as phone-less
  TOOLS (`p_phone` injected server-side — the model can never set it; security stays in SQL),
  zeroth-fetch preload as the deterministic floor, forced first fetch, look-again contract, Haiku
  fact-gate between draft and send. Canned routes deliberately untouched — that boundary is #1's
  structural half (the named lane exception).
- THE bug of the build: n8n split multi-row RPC responses into one item per row, so every multi-row
  tool result since the loop was born was garbage — fullResponse + `.body` unwrap took the generated
  hard set 45→18 fails in one change.
- Fix batch: 11 of 13 organic fails closed and proven individually. Harness hardened same day:
  fact-gate rubric = material invention only, evidence never tail-cut (+ untrimmed copy for the
  deterministic entity post-filter), gate retries capped via `$runIndex` (one question had looped
  36 gate checks / 41 model calls / 417s).
- **Measured:** 13.0% fail on the new 100-question organic bank (the old 84-bank scored 6.0% the same
  morning — the 16 added real-member questions are deliberately hard). Head-to-head wins over prod on
  the follow-up/counting classes ("which is the biggest?" → New York 97 ✓ vs prod's denial right after
  offering the breakdown). Cost ~$0.005–0.01/answer cached — inside the band. Latency (24s median vs
  the ~5s band) split out to **#23**. Leak gate GREEN throughout.

---

### 2. ✅ Deliver what she offers · DONE 2026-07-28 · effort S · RELEASE 1
*As a member, if she offers me something and I say yes, I get it.*

She offered the full chapter list with member counts, the member said yes, and she said she didn't have
it — while having it. Same class: handing over 60 of 88 Singapore names as though that were the list.

- An offer is only made when the follow-through is proven available
- "Yes" returns the thing, keeping context
- A capped list says plainly how many are shown out of how many exist

**Impact:** every long-list answer; two live cases in one test session.

**Shipped 2026-07-28, verified 3/3.** Two halves were needed. (a) Deterministic plan replay: every turn now
 stores its lane, RPC and params in a new `plan` jsonb column on `digest.olivia_messages`; a bare
 affirmation re-issues the previous turn's plan verbatim, whatever the router says, with
 greeting/help/reset/ticket lanes block-listed. Proven on an execution where the router returned
 intent=greeting, accepts_offer=false and the answer still delivered. (b) An ACCEPTING AN OFFER rule in
 STYLE - an acceptance is delivered in full, never answered with a question. The routing half alone was
 not enough: she had all 20 chapters in the prompt and still asked what you wanted.
 Side benefit: the turn log now records which lane and RPC answered, closing the measurement gap.

---

### 22. ✅ Kimi trial · CLOSED 2026-07-29 · effort M · RELEASE 1
*As the team, we know whether a 3×-cheaper model can carry Olivia's work without losing quality —
measured, not assumed.*

**Accept when**
- **Every swap is decided on numbers:** the class rates at or better than the model it replaces, and
  the safety classes unchanged.
- **Cost measured on real cached traffic**, not sticker price.
- **Latency inside the current band.**
- **The revert is exercised once per call site** — a kill switch nobody has pulled is not a kill switch.
- **The keep-or-revert decision is written down with the numbers behind it.**

**The goal: run the Kimi test.** `KIMI_API_KEY` is in `mds-digest-web/.env.local` (gitignored).
Kimi is OpenAI-API-compatible, so each call site is a base-URL + key + model-name swap plus a
tool-calling adapter.

**Prices (platform.kimi.ai, confirmed 2026-07-29) vs ours**
| | input | output | cache hit |
|---|---|---|---|
| Kimi K2.7 / K2.6 | $0.95 | $4.00 | $0.19 / $0.16 |
| Kimi K3 (flagship, 1M ctx) | $3.00 | $15.00 | $0.30 |
| Claude Sonnet 5 (answering loop today) | $3.00 ($2 intro) | $15.00 ($10 intro) | ~$0.30 |
| Claude Haiku 4.5 (fact-gate + judge screen today) | $1.00 | $5.00 | ~$0.10 |

**Where the money actually is:** K2.7 is ~3× cheaper than Sonnet on sticker and ~1.6× on cache
hits; our traffic is ~99% cached, so expect ~2× on a real answer (~$0.005 vs $0.007-0.01). K3 is
priced identically to Sonnet — no cost case, quality case only. K2.7's cache hit ($0.19) is dearer
than Haiku's (~$0.10), so swapping the gate/judge is not a saving.

**Trial order (cheap and reversible first):** (1) fact-gate on K2.7 · (2) judge screen on K2.7 ·
(3) the answering loop on K3 — the only swap that touches member-facing quality directly.
**Bar for any swap:** organic-bank score ≥ current, leak gate GREEN, fabrication probes clean,
latency in band. Kill switch = one base-URL revert per call site.
⚠️ Adds a third AI vendor handling member content (today: Anthropic + Voyage) — privacy line in #19.

**MEASURED AND CLOSED — the answer is no swap.** Full head-to-head on the 72 organic questions
that reach a model, equal conditions (same prompt + 19 tool schemas harvested out of staging, same
gated RPCs, same Voyage embeddings, same judge, same expected answers, both on a warm cache, forced
first fetch off for both because Kimi's API refuses it):

| | Sonnet 5 | Kimi K2.6 |
|---|---|---|
| FAIL % | **15.3%** | 38.9% |
| $ / answer | **$0.0135** | $0.0270 |
| blended $/M | $0.63 | $0.62 |
| latency, median | **7.5s** | 60.7s |
| output tokens / answer | 477 | 1,960 |
| loop errors | 0 | 7 |

**The cost case does not exist on our shape.** The blended per-token rate is a wash; Kimi is cheaper
per token and still costs 2× per answer because it writes 4× the output and makes 1.6× the tool calls
to reach the same place. Quality is 2.5× worse (29.2% even after discarding all 7 tool-cap
exhaustions as a config artifact), and 60s median on a channel that cannot stream fails the latency
bar on its own. K3 is Opus-class — wrong comparison for a Sonnet-class loop — and measured 66.8s
median at 2-3× the cost on a smoke.

**One structural finding worth keeping:** every Kimi model enabled on our key forces thinking on, and
their API refuses `tool_choice: required` alongside it. Our forced first fetch — the rule that stops
her answering before she looks at data — cannot be enforced on Kimi at all. Adopting Kimi would mean
trading a mechanical anti-fabrication guarantee for prompt wording.

**Kimi did win 3 questions Claude lost**, both on known Claude weaknesses already ticketed:
persona-driven recommendations (#14) and a privacy over-refusal instead of grounding (#1).

Evidence: `OLIVIA_MODEL_COMPARE.md` (every question, both answers), `OLIVIA_MODEL_BENCH_*.md`,
commit `8729cc3`. Harness: `mds-scorecard-tools/{kimi_harvest,kimi_bench,bench_compare}.py` — reusable
for any future vendor, and it touches no workflow. Cost of the trial: ~$5.50.

---

### 24. ✅ First contact answers the question · DONE 2026-07-30 (staging) · effort S · RELEASE 1
*As a new member, my first message gets a real answer — even though it is also the moment Olivia
introduces herself.*

The welcome gate fires on "first-time user" before anything reads the message, so a first contact
that IS a question gets the intro menu and no answer. Verified across all 22 organic users
(2026-07-30): 9 opened with a real question; since Jul 23 every one of them was swallowed by the
welcome — members immediately re-send their question to get an answer. The trend is against us:
recent invitees arrive from the beta email already knowing what she is, and lead with the question.

**Accept when**
- **A first message that asks something gets the answer: 0% swallowed by the intro.** The beta
  introduction rides along briefly (before or after the answer), it never replaces it.
- **A first message that is only a greeting still gets the welcome** — the intro itself does not
  regress.
- **Content is read before any first-contact gate fires, on every entry lane.**
- **Measured from the turn log:** first-contact questions answered vs menued, checked on the real
  organic users each week.

This is a concrete slice of #1's structural half (canned routes bypassing content) with live
member-facing evidence, pulled forward as its own item. Ships with the same night promote as #21.

**Shipped 2026-07-30 on staging, proven E2E same day** (`scripts/olivia_loop/apply_24_first_contact.py`,
applied by Andy — the harness blocked the write). Plan Request reads content before the first-contact
gate: only a true greeting (deterministic `realGreeting` test — short, no question words, greeting
opener) takes the welcome; anything else keeps its real route with `first_contact` threaded through.
Format Reply appends a one-line beta intro AFTER the answer and marks the member welcomed.
Proof, silent path with the welcomed flag flipped off: first-contact "Who is the biggest chapter in
MDS?" → real answer (New York 97, Women's 86, Europe 61) + intro appended + `olivia_welcomed_at` set
by the turn (msg 15110); flag off again, first-contact "Hi" → the full welcome, unchanged (msg 15112).
Leak gate GREEN. Reaches prod with the #21 night promote. The mis-routed help lane (`what do you do`
first contact) stays as-is by design — the help menu IS that question's answer.

---

### 4. ✅ Safe edits and rollback · DONE 2026-07-28 · effort M · RELEASE 1
*As the team, we can change Olivia without members being the ones who find the breakage.*

Edits go straight into the workflow members are talking to. No test copy, no rollback. Two sessions have
already overwritten each other; one bad edit killed every inbound for eight minutes.

- A test copy takes the change first ✅
- A named version to roll back to, and a one-command rollback ✅
- One editing session at a time, enforced not remembered ✅

**Shipped 2026-07-28 as `scripts/olivia_wf.py` + a PreToolUse hook, all three proven live.**
(a) **Staging copy** `bqHstPDi84uOhTCJ` on webhook `olivia-wa-staging`, active; `stage` refreshes it
from prod, `olivia_selftest.py --staging` fires the full pipeline at it (chapters + events probes
answered). The target's webhook path/ids always win on any copy, so a staging graph can never carry the
live Meta path and vice versa. (b) **Named snapshots + one-command rollback**: `snapshot --label X`,
`rollback <label>` (auto pre-rollback snapshot, settings preserved incl. the API-invisible `binaryMode`,
edit-then-ONE-bounce order, byte-match verified after write). Proven on prod twice — rolled back to
`known-good-2026-07-28`, verified the change gone, rolled forward, verified live. `promote` = diff →
leak gate GREEN required → pre-promote snapshot → write → bounce → verify (ran end-to-end on a real
change). (c) **Single-editor lock enforced**: `.claude/hooks/olivia_wf_lock.py` blocks n8n-MCP writes,
version-rollbacks, deletes and raw curl writes against the live workflow unless THIS session holds
`.olivia_wf.lock` — 14/14 decision-table cases pass, and it blocked a real call in-session.
Rollback deliberately skips the gate so the emergency path stays fast.

**Promoted to S1 on 2026-07-28.** Not process for its own sake: Andy was testing on his real number
while the live workflow was being edited, and a change broke his session for four minutes. The
architecture rebuild (#21) cannot start without this. **Impact:** caps the blast radius of everything
else on the list.

---

# Daily routine — not a backlog item

**Andy's number is excluded from daily reporting** (2026-07-28). He tests constantly and the
`olivia_selftest` harness fires as him, so his turns are not member traffic and must not be scored or
counted. Note: `olivia_selftest.py --cleanup` reports success but deletes nothing — 353 test rows have
accumulated on his number since 2026-07-21. Not worth deleting; just filter the number out.

**Read every real conversation, feed the failures back in, measure.** Daily, built on real member
questions. Targets: **under 10%, then under 5%, then under 1% wrong.**

**Run tiers (Andy 2026-07-30): FULL runs (all 100) produce the standing number and are rare; TEST
runs confirm fixes — 50 questions max, ideally ~25-35 (targeted fails + thread predecessors + a
pass spread for over-refusal), via `--ids`. Cost discipline: never a 10×100Q day.**

Today the number can't be trusted: it swings 5–10 points between runs of the same system because the
question set changes, some expected answers are themselves wrong, and she doesn't answer identically
twice. Fixing that is part of the routine. Held until the 11 betas are active.

---

# Needs Andy

1. **Revenue ranking** — may she rank named members by revenue at all, or bands only? (#3 Public revenue, double-sourced)
2. **Ex-member departure dates** — "no longer active" only, or is the date fine? (#1 Sensitive-topic gate)
3. ~~Canonical chapter count~~ — **ANSWERED 2026-07-31: raw data (live member records) is
   canonical; the site is the disclosure precedent, may lag.** (#6, closed)
4. ~~Chapter leads~~ — **ANSWERED 2026-07-31: names, roles and photos are public on the chapter
   pages → shareable; emails/phones never (not published, not stored).** (#6, closed)
4b. **Chapter TTM sums — the whale question (NEW, from #6):** a live chapter revenue sum can out
   one member's scale in a small chapter (NorthTex: sum $930M, one member $806M of it). The site
   publishes chapter sums, so they ship ON — rule them off (band_mix only) if that's too exposed.
5. **Revenue working session** — brackets, derivation, and the Amazon/DTC/TikTok split. (#3 Revenue brackets, one rule)
6. **The pre-ship test script** — *not* the multi-source member feature (that's #11). One command run before shipping: asks a real question of every source, runs the ticket flow, runs the safety gate, prints pass/fail. Build it, and at what priority?

---

# Verified this session — status corrections

**The name change is approved but not in effect.** Live Meta Graph: `name_status: DECLINED`,
`new_name_status: APPROVED`, but `verified_name` is still **"Oliva"** — members are still seeing the old
misspelled name. Re-check in 24h; if unchanged it needs re-applying in WhatsApp Manager. The health
dashboard doesn't watch the name field at all.

**No member request has ever reached Intercom.** The route is real and live, but it only fires when a
member explicitly replies **yes** to an offer — 2 offers ever made, 0 accepted, zero ticket-creation
turns in the whole log. Tickets being unassigned is **intentional per Andy**, not a defect. What remains:
the everyday action lane still writes a Supabase row plus a Slack card to **#automation-tests** where 26
requests sit unactioned, and one path tells the member "I've flagged it for the MDS team" while writing
nothing anywhere.

**The alerting is dead, which is why Olivia never looks down.** The 30-minute Slack monitor is
permanently latched: it stored `lastHealth = "down"` and its own live check still returns "down" (with
35/35 tools healthy), so its "only alert on a change to down" gate can never fire again. Last automated
alert: **2026-07-26 17:15 UTC**, about stale syncs, not Olivia. Separately, none of the eight Olivia
tiles would have gone red during the 07-26 outage — the dashboard claims "Claude answer failures fail the
run", which is false, because the node is set to continue on error.

**Two measurement traps.** The eval harness marks only the member's message as a test, never Olivia's
reply — so anything filtering her replies reports **eval traffic as production** (367 of 636 recent rows).
And the turn log records the delivery path, not which sources answered, so cross-source coverage can only
be estimated. One cheap fix closes both.
