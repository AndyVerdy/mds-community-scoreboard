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

# Olivia — SPRINT 4 (opened 2026-08-19)

**Sprint goal:** ship announcement week safely. Eugene's four beta cases lead (#94 expertise
ledger v2 → #95 members-lane equalizer → #96 name-cap → #97 brokered intros), then the #72 LOAD
TEST before the announcement — the announcement IS the traffic event and it has never run. Where
we start from: prod `060701be` · gate green · 34 tickets shipped in Sprint 3 (archive) · Summit
Aug 23–26 · "MDS Mille" display name in Meta review.

## 🎯 STANDING ORDER (Andy 2026-08-19): Eugene's four beta cases are the FRONT of the queue — all S1
Work them in this order: **#94** (his item 2 — newer members) → **#95** (his item 3 — "Moe ×12") →
**#96** (his item 1 — the ≤10-names cap, unblocks on Andy+Eugene's confirm) → **#97** (his item 4 —
intros, unblocks on Andy's ruling). Every ticket carries Eugene's exact words as its origin.

## 🎯 QUEUE (Andy 2026-08-20 close): ~~① 2025 transcript batch~~ **① DONE 2026-08-21** (232/233 videos · 144.8 hr · $33.42 AAI · 6,429 chunks · 232 in-session summaries · embedded · gate 0 · entitlement probed both ways; the 1 skip = a 10-second silent teaser; no fresh export was needed — links alive to 08-27) → ~~② smoke~~ **② DONE 2026-08-21 overnight** (`OLIVIA_SMOKE_2026-08-21.md`: bank 90/100 effective · slice v2 11/11 videos found problem-first · timestamps now cited · Eugene case dead) → ③ #97 brokered-intros build (POC proven; matching restrictions LOCKED 2026-08-21 — see #97) → ~~④ rename bot to "Millie"~~ **④ CLOSED 2026-08-21** (close block below — staging says Millie, checker knows the name; Meta flip rides the watcher). **<2024 years: Andy undecided ("Not sure about <2024").**

## 📋 At a glance

| # | Ticket | Priority | Size | Staging | Prod |
|---|---|---|---|---|---|
| **#61** | 🏗️ Schema audit: tables with no declared connections *(research + orphan audit + COMMENTs SHIPPED 2026-08-12; FK-constraint follow-up filed)* | 🔴 S1 | M | n/a (SQL) | ✅ audit shipped |
| **#64** | 🏗️ Runtime inventory: where every job runs — failure mode is silence | 🔴 S1 | M | — | — |
| **#66** | Forms warehouse: 4 remaining gaps (validation · refresh · units · lag) | 🔴 S1 | M | — | — |
| **#100** | 🔑 Identity aliases — one member, all their known emails | 🔴 S1 | M | n/a (SQL) | ✅ **CLOSED 2026-08-20** — 5,763 aliases, resolver live, 12/12 verify, gate 0 |
| **#101** | 🎬 Video transcripts + real access gating | 🔴 S1 | L | n/a (SQL+data) | ✅ **CLOSED 2026-08-20** — 2,730 chunks, video_access live, gate 263/0 · NEXT: 2025 batch |
| **#72** | 🚦 LOAD TEST — **NOW the announcement, not the Mille demo. Biggest open risk; never run** | 🔴 S1 | M | — | — |
| **#73** | Connect the useful forms to Olivia — she reads 5 of 161 | 🔴 S1 | M | — | — |
| **#68** | 🔑 Canonical question dictionary + mapping at scale | 🔴 S1 | L | — | — |
| **#18** | How-MDS-works answers | 🟡 S2 | M | ✅ first slice proven `6581548e` | ✅ **first slice LIVE** `f3850dd7` (prod probes: FAQ cited; no-doc honest) — open for more docs |
| **#94** | 🧠 Expertise Ledger v2 — the living skill sheet (Eugene #2 finale) | 🔴 S1 | M | ✅ probed | ✅ **CLOSED 2026-08-19** — 51 topics live, verify 9/9, gate 0 |
| **#95** | Equalizer for the members lane — BOTH advice lanes wired | 🔴 S1 | S | ✅ probed ×2 | ✅ **CLOSED 2026-08-19** — repeat asks 8/8→0/8 shared, gate 0 |
| **#96** | Attendee-name disclosure — Eugene's ≤10-names cap | 🔴 S1 | S | ✅ E2E probed | ✅ **CLOSED 2026-08-20** — cap 10 in code, attendee-gated, gate 0 |
| **#97** | Brokered intros — "message the person she recommends", consent-first | 🔴 S1 | M | ✅ route matrix · staging taps/tool · fix-wave re-reviews | ✅ **BUILT 2026-08-22 — READY FOR PROMOTE (Andy); real tap E2E closes it** |
| **#98** | Who-to-meet gates on registrations ledger (smoke Q37) | 🔴 S1 | S | ✅ E2E re-probed | ✅ **CLOSED 2026-08-20** — ledger authority both branches |
| **#99** | "Show me the rest" for who-to-meet (smoke Q49) | 🟡 S2 | S | ✅ E2E via canary | ✅ **CLOSED 2026-08-20** — continuation note in-tool, fresh re-call proven |
| **#102** | 🎬 Video recommendation ranking — time decay · speaker weight · event bonus (Andy/Eugene Slack 2026-08-21) | 🟡 S2 | M | — | ⏸ AFTER the big smoke test |
| **#104** | Adjacent-turn topic lag | 🔴 S1 | S-M | ✅ **VERIFIED: rerun of all 3 original fail-chains with recreated adjacency = 3/3 on-topic PASS** | ⛔ rides the Millie promote — **root cause: FC caught all 3, Gate Verdict pass-postfilter neutralized the catch (topic-mismatch is not a fact-claim); fix = off_topic field in FC rubric + non-filterable in Gate Verdict (regenerate, cap 2). Probe: exact failing sequence now on-topic, off_topic field live in FC output, gate 263/exit 0. Bonus same session: load_speakers.py --rescan (guest-becomes-member promotion in place, 27 checked/0 due)** |
| **#105** | 🔐 Verify Meta's webhook signature (`X-Hub-Signature-256`) on every inbound — filed from #97's final review (Andy OK 2026-08-22) | 🟡 S2 | S | — | ⏸ next session, BEFORE any wide intros announcement |
| **#106** | 🙈 Staff / non-member records must never surface in member-facing lists (event_who names, who-to-meet, intro picker) — Andy 2026-08-22: "make sure I'm not searchable" | 🟡 S2 | S | SQL-verified exposure map | ⏸ next session (test row already purged) |
| **#107** | 🗣️ Millie-only self-name (Format Reply PS still says Olivia) + who-to-meet ends with "connect you with one of them?" Yes/No buttons → Yes = intro picker (Andy 2026-08-22: "Millie and only Millie — official name"; "ask if he would like to connect… if yes provide a list") | 🔴 S1 | S-M | — | ✅ **PROMOTED 2026-08-22 ~05:24Z (Andy) — prod `8f48fdb8`**: Millie PS (prepended when button-eligible) · who-to-meet ends with the exact offer + Yes/No buttons (96779) · Yes → member_intro, no plan replay (review caught the 500-char-trim defeat → `last_olivia_intro_offer` flag, proven 96864) · non-attendee no offer (96787) · gate 267 EXIT 0 |
| **#109** | 📨 Requester-side intro notices must be TEMPLATES (accept / decline / 7-day lapse) — free-form text dies outside the 24h window (Meta 131047); found 2026-08-22 when Andy questioned the lapse promise | 🔴 S1 | S-M | templates `mds_intro_accepted` · `mds_intro_declined` · `mds_intro_lapsed` SUBMITTED (PENDING) | ⏸ logic next session (Andy: "keep as is, suggestions logic first") — must ship before any announcement |
| **#110** | 🧾 Intro-tap turns are not saved to conversation history — `Save Conversation` on the intro-tap path errors on a `$('Resolve Member')` reference (swallowed by onError); SQL-proven zero rows for tap turns; no member impact, no effect on no-replay flag | 🟡 S2 | S | SQL + exec 97071 | ⏸ next session |
| **#111** | 🎯 Who-to-meet results swing with the model's free-text topic query (Aaron: q="Retail, PPC, Amazon Ads, Sourcing, AI Automation" → 7 matches; q="Amazon PPC, Retail & Wholesale, Credit Cards & Travel Hacks, AI & Automation, Sourcing & Suppliers" → 1) — matcher should use the asker's own ledger topics deterministically + alias-normalize free text (execs 97152 vs 97286, same day) | 🟡 S2 | S-M | exec diff | ⏸ next session (or fold into #102) |
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
| — | *— closed tickets live in `OLIVIA_BACKLOG_ARCHIVE.md` —* | | | | |

## 🔁 Sprint ritual + Definition of Done (travels with every sprint)
- **OPEN at the top, CLOSED at the bottom** — a ticket moves down the moment it closes, evidence intact.
- **Every claim cites live proof** (exec id · SQL result · message id · gate exit code). Not shipped = say not shipped.
- **DoD:** story served end-to-end · AC table met/not · before/after numbers · gate EXIT 0 (never `| tail`) · staging probed before promote · prod probed after · docs in the same commit.
- **EVERY MEMBER, ALWAYS:** data jobs cover all actives keyed by `at_member_id`; phone/WA is a channel, never the population.
- **The smoke runs ONCE per sprint, at completion — never per ticket.** Eval runs are propose-and-wait; the leak gate is free and mandatory.
- Close = archive to `OLIVIA_BACKLOG_ARCHIVE.md` → next sprint carries open tickets whole → ClickUp handbook copy refresh if changed → **release notes are the FINAL stage** (drafted by me, validated + posted by Andy).


### ✅ Queue item ④ · Rename the bot to "Millie" — CLOSED 2026-08-21
**Story:** Andy's close order 2026-08-20 — the bot becomes "Millie"; the Meta submission said
"MDS Mille", spelling had to be confirmed before the 14-day re-register window burned.
**Results:** spelling ruled **"MDS Millie"** (Andy, in-session) · staging respell Mille→Millie
across all 4 nodes / 12 strings (`apply_millie_respell.py`, node --check ×4, one bounce) · on the
way, a real bug: "what is your name?" answered NAMELESS because the **Fact Check lane vetoed the
name as an unsupported claim** (exec 93640: model said "I'm Millie", Haiku verdict
`unsupported: ["name is 'Millie'"] → fail`, retry dropped it — the same veto silently applied to
"Mille" before). Fixed code-first: checker RULE ONE now names her + `community_info` RPC returns
`assistant_name` (DROP+CREATE migration `community_info_assistant_name_millie_20260821`, ACL
verified postgres+service_role only). **Meta submission of "MDS Millie" is BLOCKED while "MDS
Mille" sits PENDING_REVIEW** (error 2388362, no cancel API) — standing plan: when the watcher
(`a1ViYr5FT7iePdN9`) fires on Mille's verdict, do NOT re-register — submit "MDS Millie" then
(10 changes/30d; unused approval lapses harmlessly). Watcher stays armed; delete only after
Millie is live.
**ACs:** spelling confirmed before window ✅ · self-intro copy says Millie ✅ (staging; prod =
Andy's promote) · name survives the fact-check lane ✅ · "MDS Millie" live at Meta ⏳ watcher-gated.
**Before/after:** help card "I'm *Mille*" → **"I'm *Millie*"** · "what is your name?" nameless →
**"I'm Millie 👋 — the MDS AI assistant"** (probed staging, rows cleaned) · gate 263 checks EXIT 0.

### #102 · Video recommendation ranking — how she picks WHICH videos to serve
**🟡 S2 · size M — filed 2026-08-21 from Andy's Slack ruling to Eugene · ⏸ sequenced AFTER the big smoke test**

> ⛔ **CAPTURED, NOT LOCKED (Andy 2026-08-21): confirm with Andy before applying ANY of this —
> the criteria below may change and the ticket starts with a BRAINSTORM session, not a build.**

**Story:** Eugene asked how transcripts are prioritized; Andy ruled the criteria. Ranking today is
relevance-only — the Eugene cold-start case showed a thin title-match outranking the
transcript-rich Beginners Panel. Recommendation order must reflect VALUE, not just match.

**Andy's criteria (Slack 2026-08-21, verbatim intent — exact values he decides after processing
is done):**
1. **Time decay, 100% of videos** — "videos should be valued less over time"; curve TBD after he
   sees the data.
2. **Speaker weight** — the dynamic score we already have (#94 expertise ledger: many criteria,
   itself decays over time).
3. **Bonus points for Summits and Inspires** (event-tier bonus).
4. *"Require more TF connections"* + *"Bonus points for counting during these events"* (Andy's
   words — Typeform-connection signal + event-window activity bonus; values with the rest).
5. **Source equalization (Andy 2026-08-21): suggestions must weigh WA, FB and VIDEOS as peers** —
   "videos are potentially the strongest content we have"; when a video contains the exact answer,
   recommend it and say WHERE it happened (chunk timestamps exist) and WHO was speaking (→ #103).

**Sequencing (Andy):** 2026 processed · 2025 in progress · <2024 undecided · **then big smoke
test → then this ticket** (exact values after processing done). Overlaps queue item ② (cold-start
ranking probe) and #71 vocabulary — read both before build.

### 🟡 #103 · Speaker matching — REOPENED then REBUILT 2026-08-21 (day session, Andy driving)
**State at close: library coverage 40% → 81%** (2025 78% · 2026 **91%**) · 471 entities (274 members
email-evidenced · 134 guests · 3 partners · 60 unresolved→review CSVs) · ~1,250 speaker links ·
**participants modeled** (`role`+`talk_seconds` from Zoom cues — 298 links, 65 videos; Alex Bonilla:
speaker×11, participant×3, 194 talk-min) · **partner dimension live** (`video_partner_links` 129 across
123 videos + `affiliation_partner_id` column, backfill open) · **418 pre-#101 Zoom chunks fixed**
(restricted+public-rule = unreachable even entitled; migrated, both sides proven: "Prue: I'll
brainstorm…" @00:12:10) · **weekly chain wired** (`zoom_weekly.py` step 4.5: ladder + rescan +
participants, dry-run green E2E). Extractor lessons: repeat speakers' names must not become topic
tokens (Dorian/Ian class) · junk profile rows must not donate name tokens ("tiktok shop", 70 stale
partner links purged) · 5 junk entities quarantined+guarded.
**OPEN rungs:** AAI letter→name mapping (2025 group calls) · frame-OCR name tags (Ershad & Prue case) ·
moderator inference · affiliation backfill (person→org, Riverbend trio) · dossier weighting
speaker>participant>FB-post (#102, confirm-first) · 60 unresolved + 12 cue-ambiguous in review CSVs.

### (original reopen note)
### 🔴 #103 · Speaker matching — **REOPENED 2026-08-21 (closed prematurely — my error)**
> **Why reopened (Andy caught it):** I scoped the build to ONE field (`speaker_names`) and closed on
> "413/413 linked", a metric that measures the FIELD, not the library. Real coverage: 2025 44/233,
> 2026 62/161. Four sources ignored: **`speaker_ids`** (452 videos, 285 ids, **234 join exactly to
> the GroupOS mirror's `user_id`** — an ID join existed while I did name-string matching),
> **`description_text`** (1,032/1,033 videos), **titles** (dash-pattern, deferred then forgotten),
> **`thumbnail_url`** (626 videos; "Ershad & Prue" is readable on the card). Also missed: the
> PARTNER dimension entirely (speaker→org and video→partner: Atom11, Riverbend Consulting both in
> `partners_catalog`) and preferred names (Prue = Prudence Tweedie-Millsap) though
> `speaker_aliases` was built for exactly that and left empty.

### (previous close block — evidence stands for what it covered)
### ✅ #103 Phase 1 · Speaker matching — closed 2026-08-21
**Story:** speakers become LINKED ENTITIES, not strings — members to their record, partners to
theirs, guests recorded; "same means same" across every appearance (Andy, in-session).
**Results:** `digest.speakers` (239 entities) + `digest.speaker_aliases` + `digest.video_speaker_links`
(480 links, 413/413 speaker-carrying videos). Ladder upgraded mid-build by a discovery: existing
`digest.video_speakers` = GroupOS speaker-USER mirror (234 accounts, all with email) — so linking is
EMAIL-evidenced through the #100 resolver, not name-guessed. **212 members linked** (Brandon Young
resolved as a member by his own email — one entity, 9 videos) · **24 guests recorded** (Alan Kishk,
AJ Patel, Isaac Medeiros title-derived from a "(unnamed)" row…) · **0 exact partner-name matches**
(the 1 GroupOS CO row had no partners_catalog name match — recorded as guest, honest) · **3 unresolved**
in `~/Downloads/mds_speaker_review.csv` (never guessed). `member_record_id` in the mirror proven
GroupOS-internal (0 AT matches) — email is the key, as the mirror's own comment says.
**ACs:** one entity per person ✅ (239/239 distinct canonicals) · members linked ✅ (212, all resolve
to member_attributes) · partners linked ✅ mechanism live, 0 current exact matches · guests recorded ✅
(24) · ambiguity to review, never guessed ✅ (3). **Before/after:** 0 links → 480 · raw strings → 
identity space. Verify `scripts/verify_speakers.py` **7/7 PASS** · gate 263 checks EXIT 0.
**Plan:** `docs/superpowers/plans/2026-08-21-speaker-sync.md`. Next (own tickets): letter→name
mapping inside transcripts · title-parsing for the 620 no-array videos · answer-layer wiring (#102).

### (original #103 filing, kept for the requirement text)
### #103 · Speaker matching — name who is talking inside a transcript
**🟡 S2 · size M — filed 2026-08-21 (Andy: "it's important to mention who was speaking… another task: to match the speaker") · ⏸ after smoke; brainstorm first**

**The honest data picture (verified):** transcripts do NOT carry names — AssemblyAI returns
diarized letters (`Speaker A/B/C`, avg 5.2 voices/video; #101 kept letters deliberately so a quote
is never misattributed to a member). Names live in: the video TITLE (most sessions), description,
`videos_catalog.speaker_names`, event metadata, and occasional in-transcript self-introductions
("As Ian said… I've been a member since 2017"). So: single-presenter videos can be named from
title/metadata with high confidence; panels/roundtables need a letter→name mapping ladder
(title order · self-intros · host introductions) with a confidence floor — below it, stay
"the speaker"/"a member". Never guess from voice.

**SCOPE EXTENSION (Andy 2026-08-21, same night): speakers become LINKED ENTITIES, not strings.**
"Same means same": one speaker identity across every appearance. Member speakers link to their
`at_member_id`; non-member speakers (guest speakers with repeat presences — e.g. Brandon Young —
and Partners) get a dedicated speaker/guest identity space. The same person must never be treated
as two people across videos. **Baseline measured 2026-08-21:** `videos_catalog.speaker_names` =
raw strings only — 413/1,033 videos carry names, 239 distinct raw names, 185 exact-match a member
record by full name, 54 don't (guests/partners/spelling drift); zero links exist today. The other
620 videos carry speakers only inside title/description text.

### #109 · Requester-side intro notices as templates (accept · decline · 7-day lapse)
**🔴 S1 · size S-M — filed 2026-08-22 (Andy: "if there's no answer in 7 days I'll let you know… I don't think it's working" — he was right).**

> **In plain words:** the consent ask to the TARGET is already a template, but every notice back to the REQUESTER (accepted + link · declined · lapsed after 7 days) is sent as free-form text — which Meta only delivers inside the requester's 24-hour window. A target tapping a day later, or the 7-day sweep, lands outside it → Meta rejects with 131047 and the requester hears nothing.

*As a requester, I always learn the outcome of my intro request — accepted (with the contact), declined, or lapsed — no matter when it happens.*

**Evidence:** `digest.olivia_sends` 2026-08-22 06:04Z — a requester-side refusal text to a member outside her window → `status=failed`, `error_code=131047 Re-engagement message`. The T6 sweep proof (exec 96352) passed only because Andy's own window was open.

**Done 2026-08-22 (Andy: "submit the templates now, logic later"):** `scripts/olivia_intro_templates_109.py create` → three UTILITY templates submitted, all **PENDING** review: `mds_intro_accepted` ("Good news: {{1}} accepted your intro request — message them on WhatsApp at {{2}} to start the conversation." — Meta forbids wa.me links in buttons AND in example params, and leading/trailing variables; the phone number is passed as text, WhatsApp auto-links it) · `mds_intro_declined` ("No connection with {{1}} yet — I'll let you know if that changes.") · `mds_intro_lapsed` ("I didn't get a response from {{1}} this week, so I've let it rest. Want me to try again later — or introduce you to someone else on {{2}} instead?"). Check: `python3 scripts/olivia_intro_templates_109.py status`.

**Build (next session):** route `/api/olivia/intro` — every requester-side send (accept link, decline line, sweep lapse line) goes out as the matching template (params: target first name, phone digits / topic); keep free-form only for the TARGET's in-window replies; map 131047 → template fallback if any free-form path remains; the sweep's claim/retry logic already tolerates a failed send. Gate: add a check that no requester notice path is free-form. Probe: backdated lapse row for Andy with his window CLOSED (>24h since his last message) → template delivered.

**Accept when:** templates APPROVED · accept/decline/lapse notices delivered to a requester whose window is closed (olivia_sends `delivered`) · gate GREEN · promote (route only — no workflow change).

### #107 · Millie-only self-name + who-to-meet closes with a Yes/No intro offer that opens the picker
**🔄 #107e (Andy ~08:15Z, "yes, go with that wording"): picker lead → "Here are the Summit attendees I've recommended to you that I can reach for an intro. Pick one…" (the list can include attendees from Millie's wider matching log that the answer didn't name — 'people I mentioned' was inaccurate); empty-pick fallback reworded; route title-cases all-lowercase names (`d8f8250`). Staged (exec 97408), gate EXIT 0 → **PROMOTED by Andy ~08:40Z, prod `d9538ca6`.**
**🔄 #107d (Andy 2026-08-22 ~07:40Z, after the Aaron/Tracy replay on his phone: "I hate this message. Want intros" + "WTF is Baby — Singapore"): eligibility = Summit attendee WITH a phone (the 'both sides Millie users' rule from 08-21 is DROPPED — it refused a confirmed attendee and made one-row lists) · picker rows = expertise topics · speaker · city (useful, not niche—city) · lead/section/fallback wording → "attending and reachable on WhatsApp" / "Summit attendees". Route `dd02a9b` LIVE + staging Format Reply/Seed → probes Aaron 6 rows / Tracy 10 rows (execs 97261-97267), gate EXIT 0, snapshot `staging_…075453Z_107d` → **PROMOTED by Andy ~08:00Z, prod `d2961c8d` (79 nodes)**. Cosmetic open: source-cased names ("samuel loo") in rows.**
**🔄 #107b/#107c (same night, Andy's corrections after seeing it on his phone):** ① the post-Yes step is a **WhatsApp LIST** (lead text → "Pick a member" → rows = route's exact pick ids; built by Format Reply from the member_intro tool response, never LLM-typed; empty pick → honest plain line) — Andy: "this was supposed to be the logic… our POC in screens". ② **Suggestions are NEVER filtered or shortened** — the #107 ~850-char cap was wrong ("Aaron's answer was great, Tracy is trash"); full rich answer (10-11 names proven), ending with the exact offer; **buttons always**: ≤1024 inline, >1024 → offer sent as a follow-up button message (`followup_interactive` → `Send Followup Interactive (Meta)`), saved turn re-appends the offer so the no-replay flag still fires. ③ Pick list stays filtered to eligible targets (Andy: "keep as is" — Millie-user rule kept) with the lead text explaining why not all; ④ incident fix: intro tap-reply path now has `Intro Eval (silent)?` (a SELFTEST probe reply had been handed to Meta for Tracy Lin — rejected 131047, nothing delivered; now impossible). Staged + probed (execs 96985/96986 list+guard · 97062 rich · 97069 no-replay+list · 97071 silent), gate EXIT 0, snapshots `staging_…064607Z_107c-rich-offer-silentgate` + `…065606Z_107c2-ps-offer` (PS-first with offer, any length; 4-combo unit test + live 97100 split) · pre-promote review: safe → **PROMOTED by Andy 2026-08-22 ~07:10Z — prod `25ceefe1`, 79 nodes** (Followup Interactive? · Send Followup Interactive (Meta) · Intro Eval (silent)? live).

**🔴 S1 · size S-M — filed 2026-08-22 (Andy, after seeing Aaron Biner's real reply on his phone): "She must call her Millie — Millie and only Millie, it's an official name" · "ask if he would like to connect with someone Yes/No button and if yes, then provide a list with who you would like to send a request" · "limit message if necessary".**

> **In plain words:** the first-contact PS still introduces her as Olivia (prod, Format Reply), and who-to-meet answers are too long and end in a statement, so the Yes/No buttons never appear — and nothing invites the member into the intro flow.

*As a member who just got who-to-meet names, I'm asked "Would you like me to connect you with one of them?" with Yes / No buttons; Yes shows me the list to pick from; Millie is the only name she ever uses for herself.*

**Verified on prod 2026-08-22 (Format Reply node, post-promote snapshot `prod_2026-08-22T041121Z`):** buttons fire only when the reply is ≤1,024 chars AND ends with a short offer matching `OFFER_TAIL` (e.g. "Would you like me to … ?", ≤80 chars to the "?") AND no image/file; the first-contact PS (`_PS: I am Olivia, the MDS assistant (beta)…_`) is appended AFTER the offer, breaking the tail; Aaron's real reply = 1,180 chars + PS → text only. Other "Olivia" strings in prod nodes are internal (comments, transcript labels `Olivia:` used by Plan Request parsing, Slack notify title, router system prompt).

**Build:** ① Format Reply: PS → Millie; when a reply is button-eligible, place the PS as the FIRST line (offer stays last) — never drop the buttons for the PS. ② Answer Seed: who-to-meet answers ≤ ~850 chars; when the asker is a registered attendee and ≥1 match was shown, END with exactly "Would you like me to connect you with one of them?"; never offer intros to non-attendees (pilot refusal); "Yes" after that offer → `member_intro` with no target → present the pick list + "Who would you like me to send a request to?"; a named answer → `member_intro{target_name}`. ③ Plan Request: make sure a bare "Yes" after the intro offer reaches the LLM lane (no plan replay of the people op). ④ Router system prompt "router for Olivia" → Millie; internal labels untouched (documented). Staging probes as a registered attendee (silent lane, cleanup): reply ≤1,024 + ends with the offer + `interactive.type='button'` in Format Reply output; "Yes" → member_intro picker call in the execution; name → request path (refused/dry by design, zero sends). Gate EXIT 0 · snapshot · Andy promotes.

**Accept when:** PS says Millie ✅ · attendee who-to-meet reply carries Yes/No buttons on a real phone ✅ · Yes → picker ✅ · non-attendee gets no intro offer ✅ · gate GREEN ✅.

### #106 · Staff and non-member records never surface in member-facing lists
**🟡 S2 · size S — filed 2026-08-22 (Andy, during #97's prod E2E: "I don't want people to see me as an attendee… make sure I'm not searchable. Verify in Supa, don't trust your memory")**

> **In plain words:** Andy's working record is `membership_status='Staff'`; the search lanes already exclude it, but the EVENT lanes don't — anyone registered for the same event can see him in attendee-name lists, and who-to-meet once recommended him to a member.

*As staff (or any non-member record), I never appear in a member-facing list — search, attendee names, who-to-meet, or the intro picker.*

**Verified in Supabase 2026-08-22 (not memory):** `member_match_v2` / `expertise_search` / `member_card` filter `membership_status in ('Current Member','New Member','Pending Group Entrance','Current Member- Not Renewing')` → Andy (Staff, `recCUUw8iiUnJjac1`) and his second record "Andy Ve" (`reccPuFFDGu75MP5e`, 'Pending 1st Interview', no phone) are **excluded from search**. **Not filtered:** `event_who` (attendee names for registered askers; reads `event_registrations_live` + members), the route's who-to-meet `people` op (reads `event.attendees`/`event.people` — no status filter) and chapter-name slice, and the #97 intro picker/eligibility (no status filter). Exposure found: Andy is live-registered for **4 past events** (Summit Denver 2024, Inspire 2025, Prosper 2025, Austin afterparty Apr 2026 — both records) → visible in those events' attendee-name lists to their registered askers; `olivia_recommendations` shows he was recommended ONCE (to Lucas Santic, lane `event_people`, 2026-08-20) — via the leftover `event.people` test row `test-andy-8153` (Summit roster). **Purged same session:** `test-andy-8153` (+ its `event.attendees` row). Summit: no registration for either record.

**Fix (next session):** one rule applied in three places — exclude non-member statuses (at minimum 'Staff', 'Pending 1st Interview', and any non-current status) from `event_who` names (SQL, CREATE OR REPLACE) · the route's `people` op + chapter-name slice (mds-digest-web) · the intro route's candidate/eligibility set. Counts (`total_going`) stay the census. Gate: add a check that a Staff record never appears in `event_who` names or the intro picker. Optional data hygiene: the 4 past-event registrations are real and harmless once the lanes filter.

**Accept when:** Staff record absent from event_who names for an event he's registered to (probe with a registered asker) · absent from who-to-meet · absent from the intro picker · gate GREEN · promote.

### #105 · Verify Meta's webhook signature on every inbound message
**🟡 S2 · size S — filed 2026-08-22 from #97's final whole-branch review (I7); Andy: "ok" to file + ship as its own ticket, not inside #97**

> **In plain words:** the n8n webhook that receives WhatsApp messages accepts ANY post from anyone — it never checks the delivery really came from Meta. Before intros, a forged post could only make Mille answer a fake question; now a forged "Accept intro" tap could release two members' numbers to each other. Meta signs every delivery; we ignore the signature.

*As the owner, every inbound the assistant acts on is provably from Meta — a forged webhook post is dropped before any node runs.*

**Spec (one Code node, first after `WA Inbound (POST)`, staging → promote):** compute `HMAC-SHA256(raw request body, META_APP_SECRET)`; compare constant-time to the `X-Hub-Signature-256` header (`sha256=<hex>`); mismatch/missing → return null (drop) + one Slack `Notify Team` line with the source IP; match → pass through unchanged. The app secret lives in n8n as a credential/env, never in node JS. Needs the RAW body (n8n webhook `rawBody` option) — verify the staging webhook node exposes it before writing the node. Probe: a crafted unsigned post (the exact T4/T5 probe technique) must now be dropped; a real member message must still flow; Meta's own deliveries carry the header (verify on a live event in `olivia_webhook_events` payload headers if persisted, else on the webhook node's input). Mitigation already shipped in #97: taps bind to the exact template wamid (`consent_wamid`), so a forged Accept without the real wamid does nothing.

**Accept when:** unsigned probe dropped (execution shows the drop, zero downstream nodes) · real inbound unaffected (one live turn) · selftest/probe tooling updated to sign its crafted posts (or use a staging-only bypass secret — Andy's call) · gate GREEN · promote.

### #97 · Brokered intros — message the person she recommends

#### ✅ #97 CLOSED 2026-08-22 — PROMOTED to prod (Andy, versionId `7e4be40a`, 76 nodes, gate passed in-promote, bounce 200/200) · PROD E2E TAP PROVEN
**Story:** *As a member, when Mille recommends someone, I can say "connect us" — she asks THEM first, and only a yes opens the thread.* No number leaves without the target's yes; a wa.me link IS the number.

**What shipped (plan `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`, 7 tasks, each built + independently reviewed):**
- **T1** ledger v2 — `olivia_intros` +`unreachable` status, +`decided_reason` (migration `olivia_intros_v2_20260820`, `9f380b1`).
- **T2** `/api/olivia/intro` (mds-digest-web `7c30682`+`e6f8b48`, DEPLOYED on Render — NOT Vercel; both META_WA_* env pre-existed) — ALL policy in one route: request → consent template · pick → 10-row picker, recency-ordered, eligible-only · tap → accept/decline · sweep → 7d expiry. Caps 3 pending/requester + 3 pings/target/7d · decline FINAL never revealed · unreachable (no phone / 131026 / send_failed) with every-member-always · **ELIGIBILITY locked by Andy 2026-08-21: both sides Millie users + Summit-registered `recrATwhUDA55iQN5`; <30d parked** · sweep = notify-before-expire, per-row isolation.
- **T3** live matrix 9/10 PASS, 0 real sends, DB restored to exact baseline (independently verified); doubled `not.like` SELFTEST filter proven 280==280; sweep no-op proven by SQL (live body came with T6).
- **T4** staging tap branch (7 nodes, ONE atomic version) — Accept/Decline template taps and `intro_pick_` list taps intercepted BEFORE the LLM lane. **Found + fixed: `Log Inbound` dropped ALL template button taps — prod never processed any Accept/Decline, including Eugene's POC reject.** Blast radius proven safe against full payload history (Yes/No-thanks = `interactive.button_reply`, untouched). Execs 96072 (tap swallowed, 0 LLM turn, 2 delivered sends to Andy only) · 96082 (plain text, normal lane).
- **T5** `member_intro` seed tool + Answer Tool map on staging — chain proven exec 96162 (tool call → route → real picker); type-a-name fallback proven with a REAL name via decline-guard (execs 96305/96307, `member_intro{target_name:'Tracy Lin'}`, 0 sends).
- **T6** `Intro Sweep` on the LIVE every-minute Reminder Sender `QhJw46Mr7LAP8fdz` (parallel off the trigger — the reminder chain short-circuits on empty ticks) — exec 96352 `{expired:1, failed:0}`, backdated row 10 flipped expired/sweep, Andy's phone `delivered`. POC script retired (`68abeaf`).
- **T7** gate 263 → **266** (+3 intro checks: no-secret 401 · unknown asker no pick/no send · dry-run named → no `\d{8,}`/no wa.me) EXIT 0 · handbook intro flow (`42bb2ce`, staging caveats in).
- **FINAL WHOLE-BRANCH REVIEW (opus) → "not ready" → FIX WAVE (route `5878787` + `938c175`, migration `olivia_intros_late_taps_20260822` / `2e7e05b`, staging nodes):** C1 taps now bind to the exact template (`consent_wamid` from WhatsApp's `context.id`; never newest-pending) — proven exec 96540 (two pending on one target, only the tapped one flipped) · C2 **Andy ruling: accept is final** — late taps swallowed with an explicit confirmation + `late_taps` audit, never the LLM (exec 96554) · no-context tap → `handled:false` → normal lane (96560) · C3 `Intro Handled?` fail-open `=== true` — route unreachable → no error, falls through (96573), restored → works (96586) · I1 ordered member lookup (5 dup-phone members) · I2 registered-first eligibility intersect (1000-row cap) · I3 topic sanitized + send_failed honest line · I4 waSend guarded · I5 pick-tap passes the id, never the dev note · I6 self-intro guard · I8 atomic sweep claim, limit 20 · M1-M3. Gate 267 EXIT 0. **Wording (Andy 2026-08-22): non-attendee requester hears the Summit-PILOT line — never an invitation to register.** POC row 2 (Andy→Eugene) set `declined` at Eugene's Decline tap time — his last word; no misleading expiry message.

**AC checklist:** Andy's ruling recorded ✅ (plan Global Constraints + eligibility lock) · consent flow live E2E on a phone ✅ **PROD: exec 96653 (04:17:36Z) — Accept tap on Andy's number, bound by `consent_wamid`, intercepted before the LLM (0 `olivia_messages` rows), ledger row 13 `accepted/tap`, both accept texts `delivered` to Andy's phone (04:17:41/42Z); status callbacks 96654-96661 clean; prod health pings green on the new graph (96646/96647)** · out-of-window template approved ✅ `mds_intro_request` UTILITY · declines final and polite ✅ (code + T3 step 4 + T5 real-name probe verbatim) · gate GREEN ✅ 267/267 EXIT 0 (post fix wave).

**Before → after:** POC = a script on Andy's Mac messaging one hard-coded test number, taps dropped by prod, no eligibility, no caps, no expiry → member-facing flow: 4 route ops · 7 rulings in code · 3 gate checks · every tap intercepted · sweep every minute · 0 → 10 ledger rows processed in build (all test rows cleaned; ids 1-3 baseline + row 10 sweep proof kept).

**Fix wave 2 (sweep, after the scoped re-review found 2 new Important): failed expiry-notice send keeps the row pending + retried (`failed` counted) · stale `sweeping` claims reclaimed after 10 min · `535a23a` deployed, live tick 96624 clean, re-review: ready.** Reports for Andy/Eugene: `OLIVIA_97_BROKERED_INTROS_REPORT.md` · `OLIVIA_97_INTROS_FOR_EUGENE.md` (+`_SHORT`, 4,587 chars) · artifact https://claude.ai/code/artifact/446286fc-411e-4e78-981e-9e858efa81d2. Follow-up filed: **#105** webhook signature.

**PROMOTED 2026-08-22 04:11Z by Andy** (15 nodes incl. the Millie/#104 set that rode along; pre/post snapshots `prod_2026-08-22T041116Z_pre-promote` / `…041121Z_post-promote`). Original instruction kept for the record: `python3 scripts/olivia_wf.py promote` — covers T4 + T5 in one (they MUST go together: the tool without the tap branch would create requests nobody could answer). Post-promote proof: (1) ask Mille "connect me with one of the people you recommended" → picker (prose) → name one → consent template lands on THEIR phone — pick a member you'd genuinely intro, or use your canary pattern; (2) an Accept tap on the target phone flips the ledger + links both ways. Lock is released at promote.

**Parked for Andy (follow-up tickets, not chased):** ① `Plan Request` trueAction regex steals "connect me with someone / a person" (routes to human-escalation) — named targets + "one of the people you recommended" proven fine ② picker renders as prose (no interactive-LIST builder in Format Reply); `intro_pick_` tap branch idle until LIST rendering exists ③ #105 webhook signature (filed) ④ accepted-as-is: caps read-then-check (non-atomic), `late_taps` read-modify-write under concurrent late taps, pre-existing pair-insert TOCTOU, plaintext secret header values in the two HTTP nodes (pre-existing pattern). Fixed in the fix wave, no longer open: hardcoded "3", dry-run unreachable write, self-intro, picker note leak, sweep overlap.

**🔴 S1 · size M — filed 2026-08-19 · 🔨 POC PROVEN · rulings LOCKED · 📋 PLAN: `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`**

**⚖️ MATCHING RESTRICTIONS — ✅ LOCKED AS-IS (Andy 2026-08-21: "lock them as-is, go"; build started same session, in the plan as the ELIGIBILITY Global Constraint):**
- **Both sides must be Millie users** (Eugene: "We shouldn't match members unless both are using
  Millie"; Andy's lock: "If I see that a person is in WA but he never uses Millie, he is out").
- **Sandbox first: Summit-locked** — introductions only between people attending the Summit
  (Eugene: sandbox to summit attendees; Andy: "yes. Possible to lock to Summit").
- **Parked criterion:** last-used <30d — "irrelevant for now, but might be relevant later" (Andy).
- **POC postscript:** Eugene tapped REJECT after the POC window — expected, no live listener
  (Andy in-thread); ledger row #2 still reads `pending`. The real build's tap watcher must run
  continuously and flip taps whenever they arrive (taps live only in `olivia_webhook_events`).

**POC PROVEN END-TO-END 2026-08-20 (commit `68fa789`):** template **APPROVED as UTILITY** (no
marketing cap on consent asks — the make-or-break unknown, settled). Full loop on the test
number: `olivia_intros` ledger row pending → template delivered (olivia_sends `delivered`) →
Andy tapped **Accept intro** on his phone → watcher caught the tap → ledger `accepted` → wa.me
links sent both ways (`delivered`). Findings the real build must carry: ① template quick-reply
taps arrive as `msg_type='button'` and are NOT persisted to `olivia_messages` — the workflow
branch must handle type='button' (today only the raw webhook store sees them, and Mille answers
the tap text as if it were a message) ② the plus-is-space trap on ledger timestamps.
**RULINGS LOCKED + PLAN WRITTEN 2026-08-20:** `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`
— caps 3-pending/requester + 3-pings/target/7d · decline FINAL never revealed · silence = 7d expiry,
retryable, zero reminders · unreachable = honest line + team-escalation offer · targets only from
the asker's 30d recommendation log · exact member-facing wording verbatim in the plan · tap branch
before the LLM lane · `member_intro` seed tool · sweep on the Reminder Sender tick.
**Prereq (Andy): META_WA_TOKEN + META_WA_PHONE_NUMBER_ID onto RENDER (service `mds-digest-web`, Environment tab + Manual Deploy — the plan said Vercel, wrong: digest.mds.co is Render-origin, verified 2026-08-21), then execution-mode pick.**

**POC step 1 (superseded by the above) — the consent template was submitted:** `mds_intro_request`
(id `1413344637359224`), submitted **UTILITY**, status **PENDING**, `allow_category_change=true`
(approve-as-marketing beats a rejection — either verdict is the POC's answer). Body: "Hi {{1}},
fellow MDS member {{2}} asked for an introduction to you about {{3}}. Should I connect you two?
Your contact details are shared only if you accept." + Accept intro / Decline buttons. Check:
`python3 scripts/olivia_intro_template.py status`. **If it approves as MARKETING, the 131049
per-user cap applies to consent asks — decision point for Andy.** No send path exists on purpose;
nothing messages anyone until the flow is ruled.

> **In plain words:** after "you should meet X", one tap should start that conversation — without ever handing out phone numbers.

*As a member, when Mille recommends someone, I can say "connect us" — she asks THEM first, and only a yes opens the thread.*

Eugene, verbatim: *"It might be also cool to just have an ability to message the person that it recommends… it can just open up a WhatsApp thread with their number."* A wa.me link IS the number — never. The buildable shape: consent-first broker — Mille messages the target ("Eugene would like to connect about 3PL — ok?"), a yes shares the link both ways; outside the 24h window this needs ONE approved utility template.

**Accept when:** Andy's ruling recorded · consent flow live (no number leaves without the target's yes) · out-of-window template approved · declines are final and polite · gate GREEN.

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

---

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

---

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

---

### #35 · Connect new data source — DOCUMENTS (GroupOS)
**⚪ S4 · size M — DEMOTED S3 → S4 (Andy 2026-08-05: "#35 is s4 as well")**

> **In plain words:** MDS documents become a source she can search and cite.

*As a member, MDS documents are searchable like everything else.*
Extract via the GroupOS MCP document endpoints (documents_list/get, collections, categories —
already exposed on the connection). Same pattern as videos/partners: catalog + gated retrieval +
restriction handling + embeddings + gate checks. Filed by Andy 2026-08-01.

---

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

---

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

---

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

### #100 · Identity aliases — one member, all their known emails
**🔴 S1 · size M — filed 2026-08-20 · ✅ CLOSED 2026-08-20 same session**

#### ✅ Close block (2026-08-20)

**Results.** `digest.member_email_alias` live: **5,763 rows** (5,717 preferred · 29
name_match_approved · 11 stripe · 6 admin_field). `digest.resolve_member_by_email()` is the
single entry point — active-record-preferring: a lone record wins outright, several records
with exactly one ACTIVE resolve to it, anything else returns NULL rather than guessing.
Andy approved all 29 proposals; written to Airtable FIRST (base `appou5JVr0WIrioWS`, table
`tblfwOSROSHfuYUxv`, field re-read after every PATCH), then mirrored. Verify
`scripts/verify_member_aliases.py` **12/12 PASS** · gate **exit 0** (3 runs) · `db/` re-exported.

| AC | result |
|---|---|
| 10 known cases resolve via the alias table | ✅ 10/10 — and to the **ACTIVE** record (was 3/10 before the write-back) |
| Bastuba (stripe) + Corrigan (admin field) resolve with no approval step | ✅ both — each address sits on 2 records (duplicate humans); resolver picks the active one |
| A name match never grants on its own | ✅ CHECK-constraint vocabulary has no bare `name_match`; proposer writes a CSV only |
| Airtable and the mirror agree after write-back | ✅ 29/29 read back off the Airtable record itself (not the lagging member_profiles mirror) |
| Re-running the backfill changes zero rows | ✅ loader diffs before insert (expression index ⇒ PostgREST can't do ON CONFLICT); 2 consecutive runs insert 0 |
| Gate GREEN | ✅ exit 0 |

**Before/after (the 1,171 GroupOS video-audience addresses):** resolve to a member
1,034 → **1,038** · resolve to an **ACTIVE** member 634 → **704** · the 10 known mismatch
cases 0/10 → **10/10**. Also shipped same session (Andy's ruling): `Pending Group Entrance`
counts as active — 753 → **754**, and Current+New+Pending = **718** = Andy's export exactly.

**Discovered en route, recorded not chased:** the alias table doubles as a duplicate-record
detector — **49 addresses sit on >1 member record** (27 with exactly one active, 21 with
none, 1 with two: `dominique@milliondollarsellers.com`). 5 addresses stay deliberately
unresolved because two records for the same human exist and neither is clearly primary
(Sam Simon, Mouzima Mousumi, Dominique Mohler, Shiva Tavakoli, and `tangowithw@gmail.com`
on a second Andy record). Feeds the standing dup-member cleanup on Andy's desk (#89 list).

---

**Original filing (for the record):**

> **In plain words:** A member whose Airtable email differs from the one GroupOS knows is invisible to
> every email match we run. We found ten of them, and five were people someone had *personally named*
> on a restricted video.

*As a member, the systems recognise me by any address I have ever used with MDS — so a video I was
explicitly granted, a registration I made under a work address, or a payment under a personal one all
resolve to the same me.*

**What we found (measured 2026-08-20, GroupOS audience export vs the Members DB):**
- 1,171 people hold real access to restricted videos. **650 are current or new members**, 384 resolve
  to a lapsed/removed/staff record, 137 resolve to nothing.
- Of the 718 current+new members, **68 appear in no restricted audience at all**. Name matching shows
  **10 of those 68 are the same person under a second address** — Michelle Xu, Michael Corrigan,
  Ryan Bastuba, Guido Reyes, Jason Ko, Michael Hartman, Kyle Goguen, June Lai, David Ghiyam, Justin Cao.
- **5 of the 10 are on the 15-person named-user list of one MDS9 Mastermind video.** Email-only
  matching would deny them a video a human granted them by hand.

**The field already exists and is unused.** Airtable has `Associated Emails (Admin)` (multilineText).
It is populated on **8 of 5,972** profiles — and one of those 8 is Michael Corrigan's
`michael@trtl.co.uk`, exactly the alias the name match found. So the concept is proven; nobody fills it.
In Supabase it survives only as a jsonb key on `member_profiles.at_fields`, read by nothing.

**Second evidence source, free:** `Stripe Customer Email` is populated on 827 profiles and differs from
Preferred Email on 10. One of those is Ryan Bastuba (`ryan@varify.com` vs `ryan@bastuba.com`) — a
payment record, so it needs no human approval.

**Shape of the fix**
- `digest.member_email_alias` — `at_member_id`, `email`, `source` (`preferred` | `stripe` |
  `admin_field` | `name_match_approved`), `added_at`. Unique on (`at_member_id`, lower(`email`)).
- Backfill from all three rungs. Name matches are **proposed, never auto-granted** — `andy test`
  matched a real member record, which is exactly the false positive that rule prevents.
- Approved aliases are written back to Airtable's `Associated Emails (Admin)`, which stays the human
  source of record; the table is its mirror, refreshed like every other member field.
- One resolver used everywhere an email is matched to a person, so this fixes identity generally and
  not just for videos.

**Accept when**
- The 10 known cases resolve to their member record through the alias table.
- Ryan Bastuba (stripe) and Michael Corrigan (admin field) resolve with **no human approval step**.
- A name match never grants on its own — it produces a review row, and `andy test` does not become a grant.
- Airtable and the mirror agree after a write-back, verified by re-reading the field.
- Re-running the backfill changes zero rows.
- Gate GREEN.

**Blocks:** the GroupOS video-access load
(`docs/superpowers/specs/2026-08-20-video-transcripts-assemblyai-design.md` §14). Gating on email
alone would ship the 10 wrongful denials on day one.

**Found alongside, not this ticket:** `digest.member_identity` holds **57 rows with a NULL
`at_member_id`** — no name, no membership status, several sitting in WhatsApp channels, and one with
`phone = 'sam'`. Same disease from the other end; wants its own look.

---

### #101 · Video transcripts + real access gating — the 96 videos Zoom never reached
**🔴 S1 · size L — filed 2026-08-20 · ✅ CLOSED 2026-08-20 same session · spec `docs/superpowers/specs/2026-08-20-video-transcripts-assemblyai-design.md`**

#### ✅ Close block (2026-08-20)

**Results.** All 161 2026 videos transcribed (AssemblyAI, $26.23, diarized) → **2,730 new chunks
across the 96 videos Zoom never reached**, loaded into `content_items` in #70's exact shape with
`meta.provenance='assemblyai'`; the 65 Zoom videos untouched (checksum `74552c6a` identical
before/after). **`digest.video_access` live: 34,236 real grants** (real_match only — the 63-account
panel-phantom pool provably absent), resolved via the #100 resolver. `content_search_v2` learned ONE
access_rule type (`video_access`, all three branches + the sensitivity line — the consent flag alone
no longer exposes a video chunk); `video_search` gates its restricted treatment per asker. **96
summaries written in-session** (#70 format, zero API spend) — 161/161 now carry
`summary_source='transcript'`; all chunks + all 96 videos embedded.

| AC | result |
|---|---|
| 96 gain chunks · 65 Zoom byte-identical | ✅ 2,730 chunks / 96 videos · checksum identical |
| provenance + real start_sec on every chunk | ✅ meta carries provenance/start_sec/timestamp |
| access_rule/sensitivity match catalog | ✅ join mismatches: 0 (26 public / 70 restricted) |
| video_access = real_match only, resolver-keyed | ✅ 34,236 rows · 3 panel-only probes = 0 rows · 1,038/1,171 resolve |
| entitled sees / unentitled walled / inactive+anon nothing | ✅ probed both ways + 8 gate checks (grant → visible → revoke → gone) |
| 96 summaries, 65 untouched | ✅ 161/161, source=transcript |
| all rows embedded | ✅ embed_backfill + embed_videos, 0 unembedded |
| CREATE OR REPLACE only, ACLs held | ✅ defs captured; EXECUTE service_role-only verified |
| gate GREEN | ✅ **263 checks, exit 0** — incl. the rewritten #101 invariant: restricted transcript chunks ONLY for granted videos |

**The Eugene probe (honest):** keyword-only `video_search` still ranks the thin Milan title-match
above the Beginners Panel — ranking is #71-adjacent work, not transcript work. BUT the real fix
shipped underneath: `content_search_v2` now returns the **restricted TikTok Mastermind passage at
00:05:01 saying "run the cold start playbook"** to an entitled asker, timestamped, provenance-marked.
The content exists to be found; intent-vs-title ranking is its own ticket.

**Spec §7.3 answered by the machinery itself:** `embed_videos.py` prints "70 restricted → metadata
only" — restricted videos embed METADATA ONLY, so the vector branch cannot leak content semantically.

**Traps burned in this build:** PostgREST pages are UNSTABLE without `order=` (an unordered walk
returned 3,116 rows but 43 of 65 distinct videos) · the #70-era gate check asserting blanket
restricted-exclusion was rewritten to the grant-bounded invariant · attachments stay a PUBLIC-video
feature even for entitled askers (surfacing them leaked the raw file_key; `video_file_for_send` is
public-only anyway).

**NEXT: 2025 videos** — Andy's ruling: same machinery, next batch (~233 videos / 145.6 hr ≈ $33 AAI).

---

**Original filing:**

> **In plain words:** 96 of the 161 2026 videos — the in-person boardrooms, masterminds, Inspire
> sessions — have no transcript anywhere. AssemblyAI already transcribed all 161 for $26.23; this
> loads the 96 into the search index, writes their 96 missing summaries, and gates restricted
> content on the real per-member audience lists instead of hiding it from everyone.

*As a member, when I ask "best TikTok cold start videos", Olivia searches what was actually SAID in
every 2026 video — and if the best answer sits in a room I was in, she quotes me the moment with a
timestamp; if it sits in a room I wasn't, she names the video and tells me it's restricted.*

**Accept when**
1. 96 videos gain chunks; the 65 Zoom videos byte-identical before/after (checksum).
2. Every new chunk carries `meta.provenance='assemblyai'` and a real `start_sec`.
3. Public chunks `{"type":"public"}`/`normal`; restricted chunks `{"type":"video_access"}`/`restricted`, zero mismatches vs `videos_catalog` by join.
4. `digest.video_access` loaded from `real_match` rows only — the 63-account panel phantom pool provably absent; grants resolve via `resolve_member_by_email`; unresolved stored with NULL member + reported.
5. An ENTITLED member's probe returns a restricted passage with timestamp + library link; an UNENTITLED member gets title/date/restricted marker and no content; an entitled-but-INACTIVE member gets nothing; anon gets nothing. All four in the gate.
6. 96 summaries written (#70 format), `summary_source='transcript'`, existing 65 untouched.
7. All new rows embedded (nightly `embed_backfill.py` path), 0 unembedded after the run.
8. `video_search` and `content_search_v2` changed by CREATE OR REPLACE only; prior defs captured; EXECUTE stays service_role-only.
9. Gate GREEN · `db/` re-exported · Eugene's cold-start question re-probed as the before/after.

---

## ✅ CLOSED (Sprint 4)

### #99 · "Show me the rest" is broken for who-to-meet
**🟡 S2 · size S — filed 2026-08-20 · ✅ CLOSED 2026-08-20 same session (code `179f6c0`, E2E via canary)**

> **In plain words:** after a who-to-meet list, "show me the rest" must RE-CALL the people op and
> chunk onward — she lost the referent and answered about arrival times.

*As a member, "show me the rest" continues the list I was just given.*

The seed's REVEALING-THE-REST rule names event_who/member_match but the people op result arrives
via the event_ tool route — the rule doesn't bind it. Now that #96 ships `matched_total`, the
continuation has a census to chunk against.

**Accept when:** who-to-meet → "show me the rest" re-calls the same op and serves the next chunk
(≤10) · staging probe proves it · no memory-recalled names · gate GREEN.

**CLOSE (2026-08-20).** Fix = the continuation instruction travels in the op's own note
(code beats prompt rules): "if the member asks for more/the rest, CALL THIS OP AGAIN — the
ranking rotates; never recite from an earlier turn; never answer with schedule logistics."
E2E proof used the gate's canary pattern: a TEMPORARY registration row for Andy on the real
Summit (`claudetest99_andy_temp` — first landed on the "Night Out" side event by mistake, the
route matched nothing; moved to `recrATwhUDA55iQN5`, the actual Summit), then the probe pair.
**AC checklist:** re-calls the same op ✅ (exec 90875: full people[] + note; the "rest" reply
carried Sam Hewitt — absent from call 1's eight, impossible without a fresh call) · next chunk
served ✅ ("Here's the rest of the roster… Wei Lin, Sam Hewitt") · no memory-recalled names ✅ ·
no logistics answer ✅ · canary deleted, zero residue (0 claudetest rows, 0 Andy rows) · gate
GREEN ✅. **Before → after:** "show me the rest" → arrival times ➜ fresh ranked people.

---

### #98 · Who-to-meet must gate on the registrations ledger — the test row leaked names
**🔴 S1 · size S — filed 2026-08-20 · ✅ CLOSED 2026-08-20 same session (Andy: "fix it")**

> **In plain words:** the topic-matched who-to-meet branch admits anyone with an `event.people`
> row — Andy's `test-andy-8153` test row got him real attendee names after #96 closed that door
> on the chapter branch.

*As a non-attendee, I get counts and offers — never attendee names, through any branch.*

The chapter branch already keys on `event_registrations_live` (the #89 authority, fixed at #96
ship). The topic branch still keys `personId` on `event.people`. Fix: same authority for both.
Decision folded in: **Andy's test row** — delete it, or register Andy properly (his demos need
who-to-meet to work on his phone; recommendation: register him for real).

**Accept when:** non-attendee "who in X is attending" gets count/offer only (smoke Q37 re-run
passes) · attendee behavior unchanged · Andy's demo path ruled (registered or accepted loss) ·
gate GREEN.

**CLOSE (2026-08-20, commit mds-digest-web `179f6c0`).** The topic-matched people branch now
requires the asker in `event_registrations_live` for THAT event — the same authority as every
count; `event.people` is data, never an access key. Registered members absent from the export
still work (member record supplies topics; self-exclusion by member id).
**AC checklist:** Q37 re-run passes ✅ (live route: Andy refused with the standard note; staging
E2E: zero attendee names, pivot to community-wide members — allowed lane) · attendee behavior
unchanged ✅ (registered member: matched_total 30, 8 shown, note intact) · Andy's demo path ruled
✅ (consequence accepted with "fix it": who-to-meet is OFF for Andy's phone until he registers
for the Summit — his action item) · gate GREEN ✅ EXIT 0.
**Before → after:** test-row holder got attendee names → refused; access authority event.people →
registrations ledger on BOTH branches.

---

### #96 · Attendee-name disclosure — the ≤10-names cap
**🔴 S1 · size S — filed 2026-08-19 · ✅ CLOSED 2026-08-20 (ruling recorded + shipped same session)**

> **In plain words:** Eugene proposed she may name up to ~10 attendees of an event; today she gives counts only.

**THE RULING (Andy + Eugene, 2026-08-20, recorded verbatim from Andy's session):** *"Agree with
Eugene. BUT we need to make sure i can process the data as attendee, not just 10 people — if i ask
about who in supplements, who in DTC i will get proper info. Need to identify who is asking, if
this is an attendee of this event or not. Attendees can get all the info, we just don't want to
list all the people in one message."* → cap 10 = DISPLAY cap, never a processing cap; asker's own
registration gates names; non-attendees keep counts/aggregates only (recorded assumption, Andy
saw the recommendation and did not veto). Supersedes 2026-07-20 any-member-sees-names.

*As a member, "who from APAC is at the Summit" gets a short named list, not just a number.*

Eugene, verbatim: *"the AI will not share more than 10 names of who's attending an event but it could share information like who's attending. It just needs to be limited."* This reverses the July aggregates-only ruling (gate asserts `full_name` ABSENT from `event_who`), so it ships only on the confirmed ruling. The chapter-count code path (`people` op, `chapter` param) is already built to return the capped list the day the ruling lands — members-only, no numbers attached, gate check flipped accordingly.

**Accept when:** Andy+Eugene's rule recorded on this ticket · capped named list on chapter/roster asks · cap enforced in CODE · gate updated + GREEN.

**CLOSE (2026-08-20).** Two surfaces, one rule. `event_who` (migration
`event_who_cap10_attendee_gate_20260820`): default+clamp 60→**10** (display cap — ordering stays
fit-based so the 10 are the best 10; `total_going` stays the true census), and NAMES now require
the asker's own registration in `event_registrations_live` — a non-attendee gets the aggregate
row (event · when · true count · null names). Route chapter slice (mds-digest-web `3e77774` +
fix `08d42fc`): a REGISTERED asker gets ≤10 matched names (engagement-ordered internally) beside
the count; non-attendees keep count-only with the quiet-decline note; who-to-meet now returns
`matched_total` (the census travels with the capped 8-sample) and logs only names actually shown.
**Live catch during ship:** the first gate keyed on `event.people` and Andy's `test-andy-8153`
test row was granted names on the live route — re-keyed to the registrations ledger (the #89
authority, same source as the count). Deploy raced one staging probe (old build listed names);
re-probe after the fix went live is the evidence below.

**AC checklist:** ruling recorded on the ticket ✅ (Andy verbatim, this session) · capped named
list on chapter/roster asks ✅ (live route: registered attendee → count 30 + exactly 10 names) ·
cap enforced in CODE ✅ (SQL clamp + route slice(0,10); asked event_who for 60 → got ≤10,
gate-asserted) · gate updated + GREEN ✅ (3 new checks: cap · non-attendee-count-only ·
attendee-names; EXIT 0).

**Before → after:** roster names to ANY member 60 → **attendees only, 10** · non-attendee roster
ask: 60 names → **count only** (live: Andy asked the Summit roster for 60 → 1 aggregate row,
total_going 113, zero names) · chapter slice for attendees: 0 names → **10 + census** (count 30 +
10 names live) · E2E staging (Andy, non-attendee): "30 members from Asia Pacific are registered…
Want me to match you up?" — count, zero names, no withholding mention.

---

### #95 · Equalizer for the members lane — "Moe ×12" lived in `member_match`
**🔴 S1 · size S — filed 2026-08-19 · ✅ CLOSED 2026-08-19 (Eugene: "they've mentioned Moe to me at least a dozen times")**

> **In plain words:** the general "who should I talk to" lane still recommends the same person forever; the event lane already stopped.

*As a member, I don't get the same name every time — and our most active members don't get buried in DMs because every answer points at them.*

The `olivia_recommendations` log + equalizer (hard 30d per-asker no-repeat, soft 7d global spread) shipped on the EVENT people op with zero-overlap proof. `member_match` — where Eugene's dozen actually happened — still ranks statically.

**Accept when:** member_match reads AND writes the recommendation log · two identical member-lane asks return different names · the log carries lane='member_match' rows · gate GREEN.

**CLOSE (2026-08-19).** Shipped as 4 migrations, one commit (`a31a45b`). The execution log
showed Eugene-shaped topic asks ("who should I talk to about supplements") route to
**expertise_search**, not member_match — so BOTH advice lanes got the equalizer:
`member_match_v2` (repeats sink below every fresh name of their match tier; audit-size calls
p_limit>30 never write the log — the gate's subset check uses 60) and `expertise_search`
(relevance stays primary: RRF ×0.6 on a 30d repeat, 7d community exposure damps only the
engagement tiebreak; 24h per-pair insert dedupe so gate runs don't inflate the log).
`multi_source`/`_v2` dropped STABLE→VOLATILE (a STABLE fn can't call the now-writing fns — the
gate caught that as a 405 mid-ship) so their members sections inherit rotation. Signatures
unchanged (new param = PostgREST overload ambiguity) · ACLs verified unchanged · NOTIFY pgrst
after every RPC change.

**AC checklist:** member_match reads AND writes the log ✅ (16 lane='member_match' rows from the
proof calls) · two identical member-lane asks return different names ✅ (REST: 8+8 fully disjoint;
workflow path on staging, same supplements question twice: Jay Hunter/Richard Lo/Yuriy Rubin set
→ Sam McInerney/Jason Pratt set, zero overlap) · log carries lane='member_match' rows ✅ (+
lane='expertise_search', beyond the AC) · gate GREEN ✅ EXIT 0.

**Before → after:** identical repeated ask, names shared between ask 1 and ask 2: **8/8 → 0/8**
(member_match) and **6/6 → 0/6** (expertise_search, three asks = 18 distinct on-topic names).
Concentration context (the before-pattern): top-20 members held 45% of all 487 top-10 expertise
slots — static ranking would have served them forever.

**Standing note:** Andy's own asker row now carries the probe history — HIS next real
"who knows supplements" rotates past the probe names for up to 30d. Correct behavior, worth
remembering before a demo.

---

### #94 · Expertise Ledger v2 — the living skill sheet
**🔴 S1 · size M — filed 2026-08-19 · ✅ CLOSED 2026-08-19 (shipped to the live warehouse; plan `docs/superpowers/plans/2026-08-19-expertise-ledger-v2.md`)**

> **In plain words:** every member — new, silent, or loud — gets an honest per-skill score, on skills the community actually discusses, and proven expertise never rots to zero.

*As a member, "who knows X" and "who should I meet" see the REAL me — what I declared, what I spoke about, what my posts earned — not just how loudly I chat.*

Eugene, verbatim (his item 2, the origin of this ticket): *"it needs to prioritize newer members, giving you newer members that you haven't met instead of older members because it's sending older members here and I know all of them. I feel like it's gonna do the same for others."* #93 shipped the ranking half; this ticket is the data half — without real scores for silent and new members, novelty ranking has nothing honest to rank.

Andy's rulings, binding: activity keeps its teeth · speaking strongest (3.0×) · engagement bonus `1+ln(1+reactions)/4` · forms floor ×1.2 · decay half-lives 12mo activity / 24mo speaking · **floor = 40% of all-time peak** · taxonomy 18 parents + 34 corpus-born subtopics (Claude-vs-GPT merged; Real Estate Investing + Credit Cards & Travel Hacks added) · subtopics graduate via quarterly density re-checks.

**Accept when:** the plan's 4 tasks land · verify script all-PASS (silent members gain; floor holds; Andy top-quartile Intl Expansion; speaker outranks same-profile non-speaker) · who-to-meet matches on a subtopic with zero code changes · gate GREEN · before/after: distinct scoreable members recorded.

**CLOSE (2026-08-19).** Shipped in 3 migrations + 1 script (commits `0ce7ebe` · `a1250eb` · `8d70f10`):
taxonomy 16 → **18 parents + 33 subtopics** (`expertise_taxonomy_v2_20260819`; 34th sub was the
Claude-vs-GPT merge, already folded into `AI tooling & agents`), `derive_member_expertise` v2
(decay 12/24mo half-lives · engagement `1+ln(1+reactions)/4` · forms ×1.2 · 40%-of-peak floor;
CREATE OR REPLACE, ACL unchanged `{postgres,service_role}`), and v2.1 same-day: the taxonomy's
short terms re-opened the substring class — `'str'`/`'vat'` inside strategy/Pri(vat)e-Label scored
722/748 members on Real Estate Investing — biz+persona CTEs now match via `phraseto_tsquery` like
every other component. Recompute runs on the real nightly RPC path (`olivia_graph_nightly.py`,
EXIT 0, 11s). Floor proven live: inflated a peak ×10 → score floored to exactly 0.4×peak with
`peak_floor_applied` in evidence, then restored.

**AC checklist:** plan's 4 tasks land ✅ (T1 taxonomy · T2 derive v2 · T3 verify · T4 probes+docs) ·
verify all-PASS ✅ (`scripts/verify_expertise_v2.py` **9/9**, incl. floor-holds, silent-members-gain,
speaker-outranks; the Andy-pct spot-check was replaced by structural checks — persona
self-description moved his rank, not a defect — speaker check kept: 36/36 speakers outrank every
non-speaker on their topic, worst pct 0.984) · who-to-meet matches a subtopic with zero code
changes ✅ (staging probe "deep into customs and tariffs" → Mo Kuhail, Supply Chain & Logistics,
via the new `Customs & duties` sub) · gate GREEN ✅ (EXIT 0; one gate fix: `rank` inside city
"Franklin Lakes" false-failed the scan — now word-bounded) · before/after ✅ below.

**Before → after:** topics 16 → **51** (18+33) · ledger rows 7,199 → **15,377** · rows ≥1
5,133 → **10,648** · members scoreable on FORMS ALONE 0 → **594** (impossible under v1: forms
weren't a component) · scored subtopics 0 → **31** (7,706 rows) · floor violations **0** ·
derive runtime 34s → **11s** (v1 34s; v2.0 32s; v2.1 word-matched 11s).

---

