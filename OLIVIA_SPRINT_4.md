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
| **#112** | 🔗 Offer→answer binding | 🔴 S1 | S | ✅ exact failing sequence returns BOTH summaries | ✅ **CLOSED 2026-08-22** — the #80 binding existed; its ACCEPT_RE end-anchor made "yes booth" miss. Fix: affirmative may carry a quantifier/typo (both·booth·all·either·that one) while a topic word still routes normally; binding now covers EVERY offered video, not just the last. Prod `e175c5a3`, gate 0 |
| **#104** | Adjacent-turn topic lag | 🔴 S1 | S-M | ✅ **VERIFIED: rerun of all 3 original fail-chains with recreated adjacency = 3/3 on-topic PASS** | ⛔ rides the Millie promote — **root cause: FC caught all 3, Gate Verdict pass-postfilter neutralized the catch (topic-mismatch is not a fact-claim); fix = off_topic field in FC rubric + non-filterable in Gate Verdict (regenerate, cap 2). Probe: exact failing sequence now on-topic, off_topic field live in FC output, gate 263/exit 0. Bonus same session: load_speakers.py --rescan (guest-becomes-member promotion in place, 27 checked/0 due)** |
| **#105** | 🔐 Verify Meta's webhook signature (`X-Hub-Signature-256`) on every inbound — filed from #97's final review (Andy OK 2026-08-22) | 🟡 S2 | S | — | ⏸ next session, BEFORE any wide intros announcement |
| **#106** | 🙈 Staff / non-member records must never surface in member-facing lists (event_who names, who-to-meet, intro picker) — Andy 2026-08-22: "make sure I'm not searchable" | 🟡 S2 | S | SQL-verified exposure map | ✅ **LIVE 2026-08-24** (SQL, prod-shared) — 5 `#106` checks in the leak gate pass: `member_card`, `member_card_v2`, `expertise_search`, `member_match_v2`, finder |
| **#107** | 🗣️ Millie-only self-name (Format Reply PS still says Olivia) + who-to-meet ends with "connect you with one of them?" Yes/No buttons → Yes = intro picker (Andy 2026-08-22: "Millie and only Millie — official name"; "ask if he would like to connect… if yes provide a list") | 🔴 S1 | S-M | — | ✅ **PROMOTED 2026-08-22 ~05:24Z (Andy) — prod `8f48fdb8`**: Millie PS (prepended when button-eligible) · who-to-meet ends with the exact offer + Yes/No buttons (96779) · Yes → member_intro, no plan replay (review caught the 500-char-trim defeat → `last_olivia_intro_offer` flag, proven 96864) · non-attendee no offer (96787) · gate 267 EXIT 0 |
| **#109** | 📨 Requester-side intro notices must be TEMPLATES (accept / decline / 7-day lapse) — free-form text dies outside the 24h window (Meta 131047); found 2026-08-22 when Andy questioned the lapse promise | 🔴 S1 | S-M | n/a (route — no staging tier) | ✅ **SHIPPED 2026-09-01** `cae87c1` — `src/lib/intro-notices.ts` + template-first route with free-form fallback; 15 unit tests incl. a standing guard that no requester path can be text, 144/144 on main; live sweep probe expired=1 failed=0, lapse notice accepted by Meta (wamid …9B34A86B928F28CF3C). ⚠️ closed-window delivery not yet observed (probe requester's window was open) · lapsed template is MARKETING, so 131049 can still cap it |
| **#110** | 🧾 Intro-tap turns are not saved to conversation history — `Save Conversation` on the intro-tap path errors on a `$('Resolve Member')` reference (swallowed by onError); SQL-proven zero rows for tap turns; no member impact, no effect on no-replay flag | 🟡 S2 | S | SQL + exec 97071 | ⏸ next session |
| **#111** | 🎯 Who-to-meet results swing with the model's free-text topic query (Aaron: q="Retail, PPC, Amazon Ads, Sourcing, AI Automation" → 7 matches; q="Amazon PPC, Retail & Wholesale, Credit Cards & Travel Hacks, AI & Automation, Sourcing & Suppliers" → 1) — matcher should use the asker's own ledger topics deterministically + alias-normalize free text (execs 97152 vs 97286, same day) | 🟡 S2 | S-M | exec diff | ⏸ next session (or fold into #102) |
| **#108** | 👥 The Finder — one composable filter tool, every data layer (Belen's reseller question: Millie named brand owners, missed the 3 real resellers) | 🟡 S2 | M | ✅ proven (gate 292 EXIT 0, 26 finder checks) | ✅ **BUILT 2026-08-23 — READY FOR PROMOTE (Andy)** — 17 Summit resellers / 122 community, reasons per person, disclosure engine R1-R10 holding — full block below |
| **#113** | 🔄 Summit event refresh — the whole event (activities, sessions, rooms, access, rosters) reloads from a GroupOS export, removals included | 🔴 S1 | M | ✅ LOADED 2026-08-23 from the 09:52Z scan: activities 50→86 · access edges 180→227 · grants 183→698 · full descriptions; idempotent; self-test 7/8 | ✅ CLOSED — live lane serves the new day one |
| **#114** | 🕐 "Today at the Summit" must resolve in the VENUE's zone, not US Eastern (Ian Sells, Singapore, got Saturday on his Sunday) | 🔴 S1 | S | ✅ route live (`9d0ec41`) · seed PROMOTED `bbd597b7` 2026-08-23 02:49 ET · prod probe Sunday/Monday + full day | ✅ CLOSED — Andy tested on WhatsApp 2026-08-23 (ET afternoon, Singapore already on the next day): correct |
| **#115** | 🌍 Country/state normalised at derive time (`country_fold` in `derive_member_attributes`) + 4 WA-layer "resellers" with non-current AT status + 8 corrupt `OEM…'Wholesale…` business-model rows — data hygiene found building #108 | 🟡 S2 | S | — | ⏸ next session |
| **#116** | 🔎 Finder phase 2 (content + video: `return: content` / `videos`, who-leaves as author/speaker constraint, speaker/year/category filters, `speaker_of`) + phase 3 (events/partners/forms; retire `member_match` / `member_count` / the schedule matcher) — spec §6 | 🟡 S2 | L | — | ⏸ own plan |
| **#117** | 🧹 `olivia_selftest.py --cleanup` doesn't delete probe message rows, only `olivia_seen` — found during #108 staging probes | 🟡 S2 | S | — | ⏸ next session |
| **#118** | 🗺️ `event_who`'s `op=people` returns a ranked/personalized subset (#99 behavior), not a flat roster, for a plain "who is coming" ask — found during #108 staging probes | 🟡 S2 | S | — | ⏸ next session |
| **#119** | 🧪 Bank B — a second eval bank for everything built since the 100-question bank was frozen (2026-08-16): schedule + venue-day, Summit registration & who-to-meet, intros, 2025-26 transcripts/quotes, speakers, offer binding, the finder — ORGANIC questions only (real member asks from `olivia_messages` since 08-16), `expect` from the tickets' ACs/rulings, sized by the questions not padded; runner gets `--bank`; first staging run scored against the tickets' truth | 🟡 S2 | M | ticket ACs + `olivia_question_labels` | 🔨 building 2026-08-23 (Andy: "file #119, do it while bank A runs") |
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
| **#125** | 🚫 "Not currently active" is sent to ACTIVE members whose number simply isn't linked (Shyam Murali, live at the Summit launch) | 🔴 S1 | S | ✅ proven `01c8670d` — execs 110321/110322/110324 | ✅ **PROMOTED 2026-08-25** `c20c1811` — prod execs **110345** (unlinked, new copy) + **110346** (inactive, unchanged); gate 306 EXIT 0; 53 false claims → 0 |
| **#147** | 🔀 "Is this member registered?" answered twice by two sources that disagree (agenda says yes, who-to-meet says no) | 🔴 S1 | M | n/a (SQL) | ⏸ **PAUSED mid-ticket 2026-08-25 — HALF LIVE**: measured 36 disagreements (S1 confirmed); `member_alias_ids` + `registration_status` + `is_registered` shipped and `event_who` wired (130 → 145 registered, 15 recognised, 0 lost, gate 306 EXIT 0). BLOCKED on Andy's choice of authority shape; event resolver + schedule route not started |
| **#146** | 🔇 A member who hides their WhatsApp number is invisible — silent drop, no answer, no error (Danson Hui) | 🔴 S1 | M | ✅ built + probed | ✅ **PROMOTED 2026-08-25** `64995b68` — Danson live. Remainders open: silent-drop alarm · hidden-number history keyed by the opaque id · ~~refusal path bypasses the SELFTEST silent gate~~ **fixed under #125** |
| **#145** | 🧪 No-regression re-run of the 319 already-passing bank C questions — the last gate before the promote | 🔴 S1 | S | ✅ 319 graded, 8 regressions fixed | ✅ **CLOSED + PROMOTED 2026-08-25** — 311/319 hold (97.5%); links 654→808, dead links 5→0, dates 641→862, route changes 0; prod `8bb0827d` |
| **#148** | 🧊 The WA members mirror never reconciles — 12 rows Airtable stopped returning are frozen forever (oldest 2026-08-05), no freshness signal | 🟡 S3 | S | — | ⏸ filed 2026-08-25 |
| **#126** | 🧾 WA mirror leaves `at_member_id` NULL although the AT record carries `source_member_id` | 🟡 S3 | XS | n/a (audit) | ✅ **CLOSED 2026-08-25 — NOT REPRODUCIBLE**: field map proven correct against mirror exec 110330; all 57/671 NULLs are genuinely unmatched. Audit found 11 matched members with no `AT Database Status` (Airtable-side, Andy/ops) and the stale-row gap, filed as #148 |
| **#149** | 🗣️ Two real answers were wrong in shape — a live event called finished, a yes/no answered with machinery | 🔴 S1 | M | ✅ staging turns 52883/52885 | ✅ **PROMOTED 2026-08-26** `7abb9fc9` (rules+clamp) · route `eventPhase` pushed `102bf14` (Render deploys on push) |
| **#150** | 🔒 Summit videos restricted with ZERO `video_access` rows — nobody could be entitled | 🔴 S1 | S | n/a (SQL) | ✅ **CLOSED 2026-08-26** (Andy: attendees + staff) — 1,225 grants (7×175), rerunnable `scripts/sql/150_summit_video_grants.sql`; `is_restricted` now means restricted FOR the asker (video_search + v2); staging turn 52889 answers Tamar content; gate 306 EXIT 0 |
| **#151** | 🎯 Video answers ignore the member — Inspire volunteered, no count, no tailoring, follow-up fled the list + dangling old-event links (Andy, prod 52891/52893/52935/52941/52951) | 🔴 S1 | S | ✅ probe wave 8/8 · orphan-strip unit 6/6 | ✅ **PROMOTED 2026-08-26** `06df948a` — prod turn 52959: 1 link, Denver gone; gate 306 EXIT 0 |
| **#152** | ⏱️ `refresh_entity_dossiers` statement-timeout — `zoom_weekly` heartbeat error, last success 2026-08-07; video chain exits 1 every run (found by scorecard-df) | 🟡 S2 | S | — | ⏸ filed 2026-08-28 |
| **#154** | 🔗 People she names carry NO link — `member_match_v2` / `expertise_search` return no url column at all | 🔴 S1 | S-M | ✅ proven `e55a45c6` — 4/4 and 10/10 linked; gate 312/0 | ✅ **LIVE 2026-09-02** prod `d40a837d` (seed) + Render `8f368b3` (finder) — prod probe 5/5 linked, live finder 5/5 linked; 718/741 actives resolve |
| **#155** | 💬 A chat quote carries its own message link, and "what should I know" is not a capability tour | 🟡 S2 | M | — | — |
| **#153** | 🎯 Intent probes: ranking had no recency, stated facts refused (3/4 screenshot probes failed) | 🔴 S1 | S | ✅ **3/3 FIXED + PROVEN** `0faa9be5` — decay live (SQL), seed rule staged; gate 306 EXIT 0 | ✅ **PROMOTED 2026-08-26** `15ff4978` — verified 2026-08-28: prod/staging graphs identical (only webhook path differs), gate 306 PASS · 0 FAIL · EXIT 0; re-embed of 7 still awaits Andy |
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

### #119 · Bank B — a regression bank for everything built after the 100-question bank froze
**🟡 S2 · size M — filed 2026-08-23 (Andy, during the #108 close: "wow. old… we need one more bank around everything we built since then").**

> **In plain words:** the 100-question bank (`eval_bank_100_2026-08-16.json`) holds organic asks from 2026-07-19 → 08-16. Everything since — the Summit schedule lane and venue-day "today", registration-gated who-to-meet, brokered intros, the 2025-26 transcripts with quotes + timestamps, speaker matching, offer binding, the finder — has no regression net. A change can break any of it and the bank would not notice.

*As the team, I have a second bank — organic member questions only — that exercises every capability shipped since 2026-08-16, so a promote can be checked against the new behaviour the way the first bank checks the old.*

**Rules it inherits (Andy, #76 / 08-16):** bank = ORGANIC questions only (real member asks from `digest.olivia_messages`, SELFTEST/probe rows excluded), LOCKED once written; size = what the questions justify (not padded to 100, not trimmed to 30); retire always-passing questions at sprint close; snapshots of the bank file are kept.

**Build:** pull real member asks 2026-08-16 → today · dedupe · classify into the new capability areas (schedule/venue-day · Summit registration & who-to-meet · intros · transcripts/quotes/timestamps · speakers · offer binding · finder/filters · Millie name) using `olivia_question_labels` where it has them · pick the asks that exercise each area · write `expect` from the tickets' ACs and rulings (never invented) · same schema as the 100 bank (`id, class, q, expect, soft, asker, first_asked, seq, regression, retired`) · `scripts/run_eval_100.py --bank <file>` so either bank runs unchanged · first run on STAGING after bank A, scored like the 08-21 smoke (judges against `expect`, non-PASS re-verified by hand).

**Accept when:** bank file committed (`eval_bank_B_2026-08-23.json`) · every question is a real member ask with its `first_asked` date · every new capability area has ≥ 3 questions or an honest "no organic asks yet" note · runner takes `--bank` · one full staging run scored and written up (`OLIVIA_SMOKE_BANK_B_<date>.md`) · no question duplicates bank A.

### #112 · Offer→answer binding — a short "yes" must land on what she just offered
**🔴 S1 · size S — filed + CLOSED 2026-08-22 · ⚠️ renumbered from #108 on 2026-08-22: the parallel #97/#107 session had already issued #105-#111, so my #108 collided with its "attendees ∩ chat membership" ticket. Both entries survived; this one moved to the next free number. LESSON: two sessions on one board must claim numbers from the CURRENT max, not from memory.**

**Story:** *As a member, when Mille offers "want a quick summary of either one?" and I reply "yes"
(or "both", or a typo of it), I get those summaries — not a fresh search that answers something
I never asked.*

**The miss, verbatim (prod, 2026-08-22):** after a good cold-start answer offering summaries of
two videos, Andy replied `yes booth` (typo for "both"). First the Fact Check blocked it three
times as off_topic and he got the canned "couldn't verify" line; after that gate bug was fixed
(RULE ZERO now exempts short affirmatives and clarifying questions — SHIPPED, prod
`e3b4e171`), the answer became WORSE in kind: she re-searched from scratch and returned a story
about Fred McKinnon's brand getting zero GMV — confident, well-sourced, and not the question.

**Root cause:** nothing binds a follow-up affirmative to the offer that preceded it. The offer is
free text in the reply; the next turn re-plans from the raw fragment.

**The pattern to copy:** #99 solved the identical shape for who-to-meet ("show me the rest") by
putting a continuation note IN THE TOOL RESULT rather than trusting the prompt. Same here: when an
answer offers specific items, persist their ids with the turn; a short affirmative resolves
against them in CODE (no re-search), and only falls back to a fresh plan when there is no pending
offer. Three prompt rules have now failed on adjacent-turn behaviour (#104 x1, this x2) —
[[feedback_code_beats_prompt_rules]] says the third one moves into code.

**ACs:** offer records its item ids · "yes"/"both"/"that one"/typos resolve to them without a new
search · no pending offer = normal planning · #104 protection unaffected · probe = the exact
`yes booth` sequence returns the two summaries.

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

**Done 2026-08-22 (Andy: "submit the templates now, logic later"):** `scripts/olivia_intro_templates_109.py create` → three templates submitted — **all APPROVED (verified live 2026-08-22 via `status`)**; ⚠️ `mds_intro_lapsed` came back as **MARKETING**, not UTILITY, so it is subject to the per-user marketing cap (131049) and needs a fallback path: `mds_intro_accepted` ("Good news: {{1}} accepted your intro request — message them on WhatsApp at {{2}} to start the conversation." — Meta forbids wa.me links in buttons AND in example params, and leading/trailing variables; the phone number is passed as text, WhatsApp auto-links it) · `mds_intro_declined` ("No connection with {{1}} yet — I'll let you know if that changes.") · `mds_intro_lapsed` ("I didn't get a response from {{1}} this week, so I've let it rest. Want me to try again later — or introduce you to someone else on {{2}} instead?"). Check: `python3 scripts/olivia_intro_templates_109.py status`.

**Build (next session):** route `/api/olivia/intro` — every requester-side send (accept link, decline line, sweep lapse line) goes out as the matching template (params: target first name, phone digits / topic); keep free-form only for the TARGET's in-window replies; map 131047 → template fallback if any free-form path remains; the sweep's claim/retry logic already tolerates a failed send. Gate: add a check that no requester notice path is free-form. Probe: backdated lapse row for Andy with his window CLOSED (>24h since his last message) → template delivered.

**Accept when:** templates APPROVED · accept/decline/lapse notices delivered to a requester whose window is closed (olivia_sends `delivered`) · gate GREEN · promote (route only — no workflow change).

#### ✅ SHIPPED 2026-09-01 — Render `cae87c1` (push to main deploys; no workflow change)

**What changed.** `src/lib/intro-notices.ts` builds the three approved templates; `/api/olivia/intro` sends the
template FIRST on all three requester notices (accept · decline · sweep lapse) and only falls back to the old
free-form wording when a template send returns no wamid. The TARGET's own reply stays free-form on purpose —
they just tapped, their window is open.

**Traps encoded in the builder, each from a real incident:** every param is collapsed to a single line and can
never be empty (Meta approves an example with newlines then refuses every send, 132018 — the Summit announcement
burned a template version on this); the phone travels as bare digits because a `wa.me` link inside a template
variable is refused.

**Proof.** 15 new unit tests written failing first, incl. a standing guard that reads the route and fails if
anything ever builds a `type:"text"` send addressed to `reqPhone`; 144/144 on main, `tsc --noEmit` clean.
Deployed sha verified live at `/api/version` 20:38:46Z. Live sweep against prod on a backdated pending row:
`{"ok":true,"expired":1,"failed":0,"skipped":0}`, lapse notice accepted by Meta
(`wamid.HBgLMTc4NjY1NzgxNTMVAgARGBI5QjM0QTg2QjkyOEYyOENGM0MA`, status `sent`), probe row deleted afterwards.

**AC status:** templates APPROVED ✅ (accepted/declined UTILITY, lapsed MARKETING) · no requester path is
free-form ✅ (guard test) · gate GREEN ✅ (306/0 this session) · promote ✅. **NOT met: delivery observed to a
requester whose window is CLOSED** — the probe requester's window was open, so the closed-window case rests on
templates being exempt from the 24h rule rather than on an observed send. Re-probe once >24h have passed since
Andy last messaged Millie, or let the first real lapse prove it.

**Remainder:** `mds_intro_lapsed` is MARKETING, so a member who has had many marketing sends that week can still
have the lapse notice capped (131049); the free-form fallback only rescues that case when their window is open.

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

### #155 · A quote from a chat carries that message's own link, and "what should I know" is not a tour
**🟡 S2 · size M — filed 2026-09-02, split out of #138 after the 9-id re-run.**

> **In plain words:** when she quotes what someone said in a chat, or names a tool people talked about,
> the member cannot open the message it came from. And "what should I know in MDS" still answers with a
> tour of what she can do instead of what is actually happening.

*As a member, anything Millie quotes or names from a conversation, I can open — and when I ask what I should know, I get what is live right now, dated, not a menu of her features.*

**Evidence (2026-09-02, re-run against prod):** #6007 "best tools for TikTok shop launch" named 7 tools and
linked 2, while its evidence carried ~67 link fields. #6064 named 3 items, linked 1, evidence carried ~107.
#6031 "what info should I know in mds" returned a capability tour — chats, the Facebook group, the video
library — with no dates and no links on any item.

**Why the obvious fix does not work (proven, do not repeat it):** a Gate Verdict repair that attaches the
link from the row an item came from cannot bind these, because the tool or quote is named inside the message
BODY while the row's identity fields carry only the chat and the author. Matching bodies instead attached two
wrong links on prod and forced a rollback the same day (execs 127539, 127638; #138 close block). The binding
has to happen where the item is chosen — in the seed/answer loop, which knows which row it is quoting — not
after the fact in the gate.

**Shape of the fix:** two parts. (a) The answer loop carries the source row's link with each quoted item, so
the link travels with the claim instead of being reconstructed later. (b) The "what should I know / what is
live" class answers from recent retrieved items with their dates and links, and is not allowed to answer with
a capability list.

**Accept when:** a chat-sourced quote ships with its own message link ✅ · a named tool ships with the message
that named it ✅ · "what should I know in MDS" returns dated, linked, real items and no capability tour ✅ ·
re-run of #6007 · #6064 · #6031 against prod grades pass ✅ · gate GREEN.

### #153 · Intent questions failed on ranking and stated facts — the screenshot probes, run down
**🔴 S1 · size S — filed 2026-08-28 from the 4-question probe table Andy screenshotted (source session unknown; scorecard-df disclaims it). 3 of 4 failed on prod.**

*As a member asking by PROBLEM ("how do I tell early a senior hire isn't working out?"), I get the
freshest session that answers it — and a figure a town hall stated out loud is never "no tally exists".*

**Root causes, one per miss:**
1. **Whatnot lost to Milan TikTok** — `video_search_v2`'s fusion had ZERO recency weight: a 2025
   video with equal topical match tied or beat a running-Summit one. Same disease as #151, second
   entrance (Andy: "basically the same case… relevancy suffering, since it was last year summit").
2. **Khalid lost to an older playbook** — his video is one of the 7 embedded while restricted
   (metadata-only vectors; re-embed pending Andy's go with scorecard-df).
3. **Event count refused** — the model routed to the events catalog, found no tally, and refused
   while the Town Hall transcript states ~200 events / 50+ cities out loud. It also attached a
   REGISTRATION link to an event that had already wrapped.

**Fixes:** `video_search_v2` time-decay (the #102 slice): +0.006 <60d, +0.003 <180d in the
query-fusion order — bounded (RRF legs max 0.0164) so it reorders near-ties, never lifts junk ·
Answer Seed rule "A STATED FACT BEATS A MISSING TALLY" (search content before refusing a figure;
cite as reported-not-counted; never a registration link on an ended event).

#### ✅ FIXED + PROVEN ON STAGING 2026-08-28 — 3/3 through the workflow
| probe | before (prod) | after (staging) |
|---|---|---|
| live-selling intent | Milan TikTok content | ✅ Iske's Whatnot session, real quote ("We don't want to be the QVC brand"), exec-verified |
| senior-hire intent | Jasim Eisa's older playbook | ✅ Khalid's Leadership Layer, $62K + fraud case + 30-day system — fixed by decay alone, before any re-embed |
| event count | "I don't have one single tally" + register link on a wrapped event | ✅ "close to 200 events, across over 50 cities… 55 members helping lead" cited *per the Town Hall*, explicitly a reported figure, video link attached |

Gate **306 PASS · 0 FAIL · EXIT 0** after the decay. Probe rows cleaned (8 + 4). Staging `0faa9be5`;
the decay itself is prod-shared SQL and already live. **The seed rule PROMOTED with `15ff4978`** —
re-verified 2026-08-28: `olivia_wf.py diff prod staging` = identical bar the webhook path, gate 306/0.
**Remainder:** the 7 metadata-only re-embeds (scorecard-df executes on Andy's go) · the cited
timestamp read "(at 00:00:00)" because early chunks carry start_sec 0 — cosmetic, filed under #103's
umbrella rather than new.

### #152 · `refresh_entity_dossiers` times out — dossiers 20 days stale for every new video

#### ✅ FIXED + VERIFIED LIVE 2026-09-02 (health triage of the 🔴 "nightly derivations" tile)
**Root cause:** the RPC ran through PostgREST as `service_role`, whose role-level `statement_timeout` is **60s**
(`pg_roles.rolconfig`); the refresh legitimately scans 53k `content_items` × 51 topics with `ts_rank` and needs
longer. Every night since 2026-08-20 it was cancelled at 60s (`57014`), and because `last_success_at` then sat past
its 26h `max_age_hours`, the derivations tile has been RED for 13 days on this job alone.
**Fix:** migration `refresh_entity_dossiers_statement_timeout_152` — `alter function digest.refresh_entity_dossiers()
set statement_timeout = '900s'` (a function-level GUC, applied on entry; the role ceiling stays 60s for everything
else). No DROP, no body change.
**Verified with a forced live run of the whole nightly chain** (`scripts/nightly_derivations.py`, 14:53–15:00Z):
`OK entity_dossiers: entity dossiers refreshed: video=7, partner=0, event=358, chapter=55 [87s]` — 87s, i.e. exactly
the class the 60s ceiling was killing. All 8 jobs green in the same run.
**Also found:** a manual RPC call made while the chain's own refresh was running died on `55P03 lock timeout` (8s
role lock_timeout, two concurrent refreshes) — expected; never run two at once.

**🟡 S2 · size S — filed 2026-08-28, found by the video-update session (scorecard-df) and handed over.**

> **In plain words:** the job that builds each video's topic fingerprint dies on a database timeout
> every night, and has not succeeded since 2026-08-07. New videos still get fingerprints from a
> different nightly path, but the refresh that keeps EXISTING ones current is dead, and the video
> update chain exits 1 every run because of it.

*As a member, the recommendations engine knows what every video is about, including the ones that
changed since it first looked.*

Evidence: `zoom_transcripts.py` → `rpc/refresh_entity_dossiers` fails with `{"code":"57014",
"canceling statement due to statement timeout"}` on every `videos_weekly_check.py --apply` run;
`zoom_weekly` heartbeat `error`, `last_success_at = 2026-08-07`. All 16 Summit videos DO carry
dossier rows (verified 2026-08-28), so the gap is refresh, not creation.

**Shape of the fix:** the function does too much in one statement for PostgREST's timeout — batch it
(refresh N stalest per call, loop from the script), or run it as several bounded statements.
**Accept when:** the RPC completes inside the timeout on a full backlog ✅ · `zoom_weekly` heartbeat
green with `last_success_at` current ✅ · the chain exits 0 ✅ · gate GREEN.

### #151 · Video answers ignore the member: Inspire volunteered, no count, no tailoring, and a follow-up that fled the list
**🔴 S1 · size S — filed 2026-08-26 from Andy's WhatsApp (prod turns 52891/52893, 04:48-04:50Z), four complaints in his words.**

*As a member asking about Summit videos, I get the CURRENT event's sessions, told how many exist, picked for me — and a follow-up about that list stays on that list.*

**The four, from the saved plans:**
1. **Inspire volunteered unasked.** "do you have videos from summit" was answered with 5 Singapore
   sessions plus a paragraph of Inspire 2026 content. Older events are offered, never served.
2. **No recency contract.** Many summits exist; latest is the subject, back catalog on request.
3. **"Plenty" where a number belongs.** 7 sessions were up; she listed 5, said "plenty", no count,
   no pick-rule, no tailoring to the asker.
4. **Follow-up fled the list.** `pending_offer` carried `kind: video, 5 ids`; "what would you
   recommend for me" one turn later routed `content_lookup`+dossier and answered APAC/cash-flow
   life advice. #112 binds ACCEPTS ("yes", "both") — a QUESTION ranging over the offered list is a
   new class.

**Fix (staging `a366a5e8`+):** three Answer Seed rules — a question about a just-offered list stays
in that list · the latest event is the subject, older on request · a video list states its count and
its pick rule. **Accept when:** Andy's exact chain answers right on staging · speaker/session/worth-
watching/subject probes pass · gate GREEN.

#### ✅ BUILT + PROVEN ON STAGING 2026-08-26 — awaiting Andy's promote (rides the same graph as #149)
**Three layers, because the prompt-only version half-failed on its first probe:**
- **3 Answer Seed rules** — a question about a just-offered list stays in that list · the latest event
  is the subject, older on request · a video list states its count and its pick rule.
- **`event_total` on `video_search_v2`** (DROP + re-grant, service_role only — the ACL rule): every row
  now carries how many published videos its whole event has, so the count is a fact the tool states,
  never rows-returned. First probe said "8" (rows), the truth was 7.
- **Tool description** teaches the event-name query: bare `summit` keyword-ranks Milan/Denver ABOVE the
  current event (measured: top-8 keyword-only = zero Singapore rows); `singapore summit` returns all 7.

| complaint | after |
|---|---|
| Inspire volunteered | ✅ probes serve Singapore only; older events appear only as history for a named speaker |
| no recency preference | ✅ current event is the subject in all 8 probes |
| "plenty", no count, no tailoring | ✅ "Yes — 7 sessions are up so far" twice in a row, `p_query='singapore summit'` both times, picks tailored to asker focus |
| follow-up fled the list | ✅ "what would you recommend for me" now returns 3 Summit videos with per-pick reasons (was: APAC/cash-flow life advice) |

**Probe wave 8/8 pass** (availability · recommend chain · speaker by subject · speaker by name ·
worth-watching · subject · session name · 3-bullet summary), the first c1 shape-flake diagnosed to the
keyword ranking and killed at the tool layer. Gate **306 PASS · 0 FAIL · EXIT 0**. Probe rows cleaned
(26 messages, 13 seen). `db/` re-exported. **Bank D grew to 26 questions** (quote-timestamp class:
exact quotes + `start_sec` timestamps verified present, 15 distinct starts on Tamar's 16 chunks).

**#151b — the dangling-link tail (same night):** three prod turns (52935, 52941, 52951) ended with an old Denver Town Hall URL nobody named — once after the closing question, once as the second of two stacked bare URLs. One seed-rule attempt did not hold, so per the code-beats-prompt rule it moved into `Format Reply`: a URL-only line whose neighbour above is another URL-only line or ends with '?' is a structural orphan; trailing orphans are dropped repeatedly. Unit 6/6 (titled link, Register:, venue+map all survive) · staging exec 113211 one link · **prod turn 52959 after promote `06df948a`: 1 link, Denver absent** · gate 306 EXIT 0.

### #150 · Summit videos restricted with no entitlement list — and the restricted flag contradicted the grant
**🔴 S1 · size S — filed and CLOSED 2026-08-26. Andy's ruling: "For now, videos are not accessible. Restrict them to summit attendees and staff."**

*As a Summit attendee, the sessions I sat in are mine to search, quote and get takeaways from; everyone else knows they exist and no more.*

**Two defects, one ticket:**
1. All 7 Singapore sessions were `access_restriction='restricted'` with **zero** `video_access`
   rows — restricted with no entitlement list means nobody can ever be granted, so every content
   question dead-ended even for people in the room.
2. Proving the fix exposed a second: `video_search` / `video_search_v2` computed per-asker
   entitlement (`f.restricted`) correctly for every CONTENT column, then reported the raw
   `access_restriction` in the `is_restricted` flag — an entitled asker got the content AND a flag
   telling the model not to quote it. Staging turn 52887: content in hand, *"I can't pull direct
   quotes"*.

**The fix:** 1,225 grants (7 videos × 175 grantees) — attendee = ticket roster OR GroupOS door
list (a speaker is not shut out of their own session) plus staff, deduped by email because
duplicate member records share emails (#147) and `(video_id, lower(email))` is the unique key.
Additive-only, rerunnable: `scripts/sql/150_summit_video_grants.sql` — **RERUN when each new video
batch lands.** The flag migration makes `is_restricted` mean restricted FOR THIS ASKER; the gate
check asserting the old contradiction updated, the Andy 2026-07-26 unentitled-asker ruling intact.

| AC | result |
|---|---|
| attendees + staff can get content | ✅ staging turn **52889**: Tamar's seven playbooks answered from the summary, entitled asker |
| everyone else: exists only | ✅ gate line "restricted video IS returned, flagged is_restricted" PASS; negative control (Ward Gahan et al, 0 grants) |
| speakers/partners/guests keep their own sessions | ✅ door list unioned into grantees (140 ids) |
| gate GREEN | ✅ **306 PASS · 0 FAIL · EXIT 0** |

**Named, not skipped:** 1 of 179 grantees has no email anywhere on file (a partner door-list row
with no member profile) and cannot hold a grant until one exists — `video_access.email` is NOT NULL.
**The other 39 restricted-zero-grant videos** (46 minus the 7 fixed) are pre-Summit stock and stay
as they are; they were never Summit sessions.

### #149 · Two real answers Andy got were wrong in shape — a live event called finished, and a yes/no question answered with machinery
**🔴 S1 · size M — filed 2026-08-26 from Andy's own WhatsApp screenshots (turns 52879 and 52881, phone ending 0106).**

> **In plain words:** he asked what the takeaways from the Summit were and got a list of session
> titles that opened by telling him the Summit was over — it was not, it had six hours to run. Then
> he asked whether we have the transcripts, a plain yes or no, and got a paragraph about a detail
> that "did not check out against MDS data" and an invitation to ask for "a narrower slice".

*As a member, I get an answer to the question I asked, in words that mean something to me, and she
never tells me an event I am standing in has finished.*

**The four defects, from the saved turns and not the screenshots:**
1. **A live event declared over.** At 2026-08-26 03:36Z the reply opened *"Since we're now past the
   Summit (it's Wednesday, the final day, at the venue)"* — self-contradictory, and false: the Summit
   ran to 2026-08-26 10:00Z. **Root cause:** `/api/olivia/schedule` handed the model `starts_on` and
   `ends_on` as date labels and left it to work out whether the event had finished. It got it wrong.
2. **A content question answered with the agenda.** "Takeaways" asks what was SAID; she returned
   titles, times and rooms, and the one honest sentence — *"Once those sessions sync into the library
   I can pull the actual transcript"* — was the last line of 1,364 characters.
3. **Venue and Google Maps boilerplate** rode along on a question that had nothing to do with location.
4. **The gate's clamp swallowed a yes/no question.** Plan shows `op: video_search` over a degenerate
   `content_search` (`p_limit: 0`, `p_terms: []`); after two regenerations `Gate Verdict` replaced the
   whole answer with its canned line, which never says yes or no and speaks in machinery.
   **Audited before touching it (the standing rule): the clamp has fired 3 times in 6,017 answers —
   "who are the mds members based in cyprus", a TikTok GMV-ads question, and this one. Zero of the
   three were correct withholds.**

**Accept when:** the two screenshot questions answer correctly on staging ✅ · a live event is never
called finished ✅ · an availability question leads with the yes/no ✅ · the clamp still withholds, but
in member language ✅ · gate GREEN.

#### ✅ FIXED + PROVEN ON STAGING 2026-08-26 — awaiting Andy's promote (and one push, see below)
**The fix, structural rather than a prompt patch where it could be:**
- **`eventPhase()` in `mds-digest-web/src/lib/schedule-day.ts`** — the phase is a fact the code holds,
  so the code states it. Returns `phase` (before · running · final_day · ended), `is_over`, `day_of`,
  `day_count` and a `status_line`, all counted in the VENUE's zone (the same reason #114 moved
  "today" there). An event with no end instant is never declared over. Wired into every schedule
  answer's `event` block. **7 new tests, written failing first; 366/366 pass repo-wide, `tsc` clean.**
- **`Gate Verdict` clamp copy** — the withhold is unchanged and just as strict; only what the member
  reads changes. No more "did not check out against MDS data" or "a narrower slice (one name, one
  chat, one date range)".
- **Five standing rules in `Answer Seed`** — a video reaches the library before its transcript does ·
  "do you have X" is a yes or no answered from what is on file · what was said is not what was
  scheduled · the event phase is handed to you, never inferred · the venue block rides only on
  location questions. The existing RECORDINGS coverage rule claimed *every* 2025-26 video is
  transcribed, which is false while a just-finished event is still processing — amended to point at
  the in-progress rule.

| AC | result |
|---|---|
| the takeaways question answers correctly | ✅ staging turn **52883** leads with where things stand, lists the 7 sessions with links, **no venue block, no map** |
| a live event is never called finished | ✅ same turn: *"Since the event is still running (it's Wednesday afternoon in Singapore, the final day)"* |
| an availability question leads with the yes/no | ✅ staging turn **52885** opens *"Right now — no, not yet."* then gives all 7 recordings with links |
| the clamp still withholds, in member language | ✅ new copy in `Gate Verdict`, `node --check` clean, withhold path untouched |
| gate GREEN | ⏳ to run before the promote |

**Before → after** on the two questions Andy actually asked: a false "we're now past the Summit" and a
canned non-answer, replaced by an accurate phase statement and a leading yes/no. Staging carries the
workflow half; **the `eventPhase` route half is committed but NOT pushed — `mds-digest-web` has no
staging tier and a push to `main` deploys, so it waits for Andy's go.**

**⛔ FOUND WHILE PROVING THIS, AND IT BLOCKS THE REST — filed as #150.** All 7 Singapore sessions are
`access_restriction = 'restricted'` with **ZERO rows in `digest.video_access`**. Restricted with no
entitlement list means nobody can ever be granted them — so once transcripts finish, Millie still
cannot summarise or quote a single Summit session, for any member, including the people who were in
the room. Every question class Andy named (a speaker, a session name, sessions worth watching, a
subject) dead-ends on this. 46 of the 415 restricted videos are in the same state.

### #147 · "Is this member registered?" is answered twice, by two sources, and they disagree
**🔴 S1 · size M — filed 2026-08-25 from Andy's own case at 01:38-02:12 (WhatsApp screenshots).**

> **In plain words:** the agenda lane and the who-to-meet lane each work out for themselves whether you
> are registered. They use different keys, different rules and different sync clocks, so one can say yes
> while the other says no — in the same conversation, a minute apart.

*As a member, one answer decides whether I am at an event, and every lane gives me the same answer.*

**What Andy actually saw:** "next activities in singapore" returned his correct Summit day, and one minute
later "who should i meet there?" replied *"our records show you're not registered for the Summit yet"*.

**The two authorities:**
| lane | source | key | rule |
|---|---|---|---|
| schedule / venue-day | `event.attendees` + `event.people` (GroupOS export, #113) | `event.people.at_member_id`, matched by REGISTRATION EMAIL | any attendee row counts |
| who-to-meet / attendee names (#96/#98) | `digest.event_registrations_live` (Airtable roster mirror) | roster `Match to Member` | `Confirmed` only — the view drops `Unconfirmed` and `No Show` |

**Three separate ways one person splits across them, all seen tonight on ONE member:**
1. **Duplicate member records.** Andy exists as `recCUUw8iiUnJjac1` (Staff, what his phone resolves to),
   `recMocKvJHoWuteHv` (no status, what the GroupOS roster matched by email) and `reccPuFFDGu75MP5e`
   (Pending 1st Interview, what the Airtable roster row links). Chip Ge had the same shape (#146 note).
2. **The alias bridge exists and is not used.** `digest.member_email_alias` already maps
   `andy@milliondollarsellers.com → recCUUw8iiUnJjac1` (approved), and `load_event_graph.py` resolves
   people by matching the registration email against `member_profiles.email` only — so it lands on the
   duplicate and never consults the alias.
3. **Sync clocks differ.** GroupOS refreshes hourly; the roster mirror's newest `synced_at` for that row
   was **2026-07-20**, over a month stale, so a source-of-truth correction does not reach the gate.

**Shape of the fix — do NOT merge the datasets.** They do two different jobs (operational agenda vs the
commercial ticket record) and merging them costs a migration for nothing. Instead: ONE
`digest.is_registered(p_member, p_event)` that every gated lane calls, with the Airtable roster as the
authority, the alias bridge underneath so a duplicate record cannot split a person, and the ticket-status
rule stated in exactly one place. Then the schedule lane, `event_who`, the intro picker and the who-to-meet
matcher all inherit the same answer.

**MEASURE FIRST — the ticket is sized by this number, not by tonight's anecdote:** for the Summit, count
the members the two sources disagree about (in `event.attendees` but not in `event_registrations_live`,
and the reverse). Three means file-and-move-on; thirty means members are silently losing who-to-meet right
now and it is S1 today.

**SECOND HALF OF THE SAME BUG — the event resolver matches on WORDS IN THE TITLE, not on where or when
the event is** (measured 2026-08-25, `digest.event_who`):

```
event_who('singapore') → MDS Summit Singapore      ✅ the city is in the name
event_who('vegas')     → Las Vegas Chapter Dinner Feb 2025   ❌ a PAST event
event_who('las vegas') → Las Vegas Chapter Dinner Feb 2025   ❌ same
event_who('inspire')   → MDS Inspire 2027           ✅ (44 on the live roster)
```

`MDS Inspire 2027` is in Las Vegas, but the city is not in its title, so **"who should I meet in Vegas"
can never reach it** — it lands on a 2025 chapter dinner instead. Whether the asker is registered for
Inspire is irrelevant: the event never resolves. Singapore only works this week by the accident that the
host city is in the event's name, and even then the event answer DISPLACES the place answer (the 9 members
who actually live in Singapore go unmentioned).

**So the resolver needs the same treatment as the registration check:** resolve an event from its
LOCATION and DATE, not from words in its title, and prefer live-or-upcoming over past. A place question
then has a defensible bridge — "you asked about Vegas, and Inspire 2027 is there in March" — instead of
matching a dinner from three years ago.

**Accept when:** one function answers the question and every gated lane calls it ✅ · a member with
duplicate records resolves the same way in both lanes ✅ · the disagreement count for the Summit is
reported before and after ✅ · roster staleness is visible (a freshness signal, not a silent month) ✅ ·
gate GREEN.

#### ⏸ PAUSED 2026-08-25 mid-ticket (Andy: "let's pause it and switch subjects") — HALF IS LIVE ON PROD

**Measured first, as the ticket demanded — and it is above the S1 line it set.** For the Summit
(`recrATwhUDA55iQN5` / GroupOS `689cfd00f1f12d7791cf9525`): 140 GroupOS attendees carry an
`at_member_id`, 130 members sit on the roster, **117 agree — 23 GroupOS-only and 13 roster-only, so
36 members got a different answer depending which lane they asked.** The ticket's own rule ("thirty
means S1 today") applies.

**SHIPPED AND LIVE (SQL is prod-shared — these are already serving members):**
- `digest.member_alias_ids(p_member)` — every member-record id belonging to one person, via the
  shared emails in `member_email_alias`. On Andy it returns **four** records
  (`recCUUw8iiUnJjac1`, `recMocKvJHoWuteHv`, `reccPuFFDGu75MP5e`, `recupMCtkTwbpbUKB`) — the ticket
  knew of three.
- `digest.registration_status(p_member, p_event)` — THE authority: roster as the source, alias bridge
  underneath, ticket-status rule in one place, and it reports `roster_synced_at` +
  `roster_stale_days` so a stale snapshot can never gate someone silently (the ticket's freshness AC).
- `digest.is_registered(p_member, p_event)` — the thin boolean wrapper every lane calls.
- `digest.event_who` now calls the authority instead of its own inline
  `member_at_id = v_atid`, and its `is_me` / #106 self-carve-out matches on the whole alias set, so a
  duplicate record no longer makes a member invisible to themselves in their own list.

**Before → after, measured over the 153 people involved:** the old inline check called 130 registered;
the authority calls **145 — 15 members newly recognised, 0 lost.** Andy's three (four) records now all
answer identically (`is_registered = false`, matched_via null), which is the ticket's duplicate-record
AC and keeps the leak gate's non-attendee control intact. **Gate 306 PASS · 0 FAIL · EXIT 0** after
the change. `db/` re-exported.

**⛔ THE OPEN DECISION — this is where it paused, and it needs Andy.** The ticket says the roster is
THE authority everywhere. Measured, that strips the personal agenda from people who attend without a
member ticket. The 8 GroupOS-only attendees are: **Andy Verdy** (Member — the deliberate gate control),
**Chip Ge** and **TK DecodeUp** (Member), **Anita Petrov** (Partners Team), **Chirag Singla**
(Partner, Speaker), **Tamar Yaniv** (Speaker), **Christopher Murphy** and **Joe Stark** (Guests).
Three options were put to Andy:
1. **Roster authoritative everywhere** (the ticket as written) — all 8 drop to the public agenda.
2. **One function, two facets (recommended)** — `registration_status` reports `has_ticket` (roster;
   gates who-to-meet + attendee names) AND `is_attending` (GroupOS; drives the agenda). Every lane
   reads the same function so no two can contradict, a speaker keeps their schedule and still gets no
   name list, and the gate stays green.
3. **Union** — nothing is lost, but Andy becomes an attendee and the leak gate goes RED.

**STILL NOT STARTED — the ticket's second half:** the event resolver matches WORDS IN THE TITLE
(`event_who`'s `bool_and(c.name ilike '%'||w||'%')`), so `event_who('vegas')` lands on the Feb 2025
chapter dinner and **Inspire 2027 is unreachable from the word Vegas** even though it is in Las Vegas.
Resolve from LOCATION + DATE, preferring live-or-upcoming over past. Unblocked by the decision above.

**Also not started:** wiring the schedule/venue-day lane
(`mds-digest-web/src/app/api/olivia/schedule/route.ts`, `registered = myTypes.size > 0` at line ~315)
to the authority. That repo has NO staging tier — a push to `main` deploys — so it waits for the
decision and an explicit go.

**Do not touch Airtable to fix this (Andy 2026-08-25):** it is the source of truth and he tests against it.
Corrections that need the source get raised with him or ops, never written by the agent.

### #146 · A member who hides their WhatsApp number becomes INVISIBLE — she never answers, and nothing errors
**🔴 S1 · size M — filed 2026-08-25 from Danson Hui's report (Doina, Slack), diagnosed the same night.**

> **In plain words:** WhatsApp now lets people hide their phone number. Meta then sends us a name and an
> anonymous id instead. Millie looks members up by number, finds nothing, and says nothing at all.

*As a member, when WhatsApp hides my number, Millie still knows who I am and still answers me — and if she
truly cannot tell who is writing, she says so instead of leaving me on read.*

**Evidence (prod, 2026-08-25):** Danson Hui sent two messages at 10:58 and 10:59 Singapore time. Both are in
`digest.olivia_seen` — `02:58:48Z` and `02:59:06Z`, **`phone` NULL** — so they reached us. The wamid decodes
to `CA.1068099432261958`: a country-prefixed opaque user id, no number. Nothing was written to
`olivia_messages`, nothing reached `olivia_webhook_events` (0 rows there have a null sender), no execution
errored. A silent drop. Andy's read confirmed it from the other side: as a group admin he sees Danson's
name but not his number.

**The same minute proves the working shape.** Yaron's inbound carried BOTH:
`contacts[0].wa_id = 972523626299` AND `contacts[0].user_id = "IL.1870095880636693"`, message
`from = 972523626299`, `from_user_id = "IL.1870095880636693"`. Number present → answered normally.

**Scale:** **546** inbounds carry `from_user_id` since 2026-08-11 · **107** distinct user ids seen, and all
107 pair one-to-one with a phone we already know. Danson's id has NEVER arrived with a phone (0 rows), so he
is the case the pairing cannot solve on its own. This grows as Meta rolls the privacy setting out.

**Shape of the fix:**
1. `digest.member_wa_ids` — the opaque id as a SECOND identity key beside the phone.
2. Backfill from the 546 inbounds that carry both — 107 members mapped with nobody lifting a finger.
3. Resolve on the id when the number is absent; the phone stays authoritative when present.
4. For an id we have never paired (Danson): ask ONCE — "I cannot tell who this is, what is the email on
   your MDS account?" — link it, and he is known from then on.
5. **Never stay silent.** An unresolvable inbound gets an honest answer, never nothing.

**Accept when:** a member with a hidden number gets a real answer ✅ · the 107 known pairs resolve without
any member action ✅ · an unknown id gets the ask-once path, not silence ✅ · the phone path is unchanged for
everyone else ✅ · gate GREEN · a silent-drop alarm exists so this class can never be invisible again.

#### 🔨 #146 IN PROGRESS 2026-08-25 — data half DONE, graph half on staging, one hard limit found

**The mechanism, exactly** (prod execs `109524` / `109525`): `Log Inbound` reads only `msg.from`. Meta sent
Danson's inbound with no `from` at all — only `contacts[0].user_id` / `from_user_id` = `CA.1068099432261958`
— so `from` was undefined, `Find Member`'s body `{{ JSON.stringify({ p_phone: $json.from }) }}` serialised
to **`{}`**, PostgREST answered **PGRST202 404** ("function digest.olivia_front_door without parameters"),
and the execution ERRORED after 435ms. No reply, no `olivia_messages` row, no `olivia_webhook_events` row.

**Shipped to the database (prod-shared, additive, nothing dropped):**
- `digest.member_wa_ids` — the opaque id as a second identity key. Backfilled from the inbounds that
  carried BOTH keys: **107 ids stored, 91 mapped to an active member**; an id ever seen against two
  numbers is left out rather than guessed (same fail-closed rule as `member_phone_index`).
- `digest.resolve_asker_by_uid()` — active statuses only; identity is still never entitlement.
- `digest.olivia_front_door_v2(p_phone, p_user_id)` — phone first, the id consulted ONLY when the phone
  resolves to nobody. Verified: phone path 1 row · uid path 1 row · both-null 0 rows · unknown uid 0 rows.
  The 1-arg `olivia_front_door` is untouched.

**On staging `faa34845`** (`438cddcb` → `88d15b65` → `faa34845`, snapshot `…050427Z_pre-146`):
`Log Inbound` reads the id and never emits a turn without a usable sender · `Find Member` calls v2 with
BOTH parameters always present, so the body can never serialise to `{}` again · `Resolve Member` replies on
the member's REAL phone · an unpaired id gets `unknown_uid` and the ask-once line, not "I cannot match this
number" (a lie when no number was sent) · `Send Reply (Meta)` no longer kills the turn on a bad recipient.

**Verified on staging:** mapped hidden-number inbound → identified as the right member, reply addressed to
`17866578153`, execution success (`109977`) · normal phone inbound → unchanged (`109974`) · unknown id →
`unknown_uid` + the ask-once text built (`109973`).

**⚠️ THE HARD LIMIT: Meta will not accept the opaque id as a RECIPIENT.** Sending to
`CA.1068099432261958` returns **131009 "The phone number is malformed"**. So for a hidden-number member we
have never paired, there is no number to reply to and the ask-once message cannot be delivered at all.
**Danson has to be linked out of band** — the team gets his number, or he messages once from a visible
number. Everyone in the 107 is fine: we identify them by id and reply on the number we already hold.

**Open, and filed here rather than glossed:** conversation history for a hidden-number member is keyed by
the id, so it does not join their phone-keyed history · the unmatched path does NOT honour the SELFTEST
silent gate — my probe attempted a real Meta send (rejected, nothing delivered, but with a valid recipient
it would have messaged a member) · not promoted, staging only.

### #145 · No-regression re-run of the 319 bank C questions that were already PASSING — the last gate before the promote
**🔴 S1 · size S — filed 2026-08-25 (Andy's close call 2026-08-24: "re-run the 319 already-passing, then promote").**

> **In plain words:** yesterday measured only the 192 failures. Nobody has checked what nineteen waves
> of rules, stamps, gate checks and nine SQL changes did to the 319 answers that were already good.

*As a member on WhatsApp during Summit week, the promote that ships 155 new passes must not quietly
cost me an answer that already worked.*

**Why it is real, not caution for its own sake:** two questions regressed inside the fail set in the last
round alone (6500 and 6267 got worse), and wave 9 broke staging outright for eight hours — 89 of 255 turns
errored behind a single green probe. Staging `daf8ec82` carries waves 7-19; prod `bbd597b7` carries none of
them. The head-to-head that read stage 91% vs prod 87% predates every wave and is stale.

**Shape of the work:** a stratified sample of the 319, sampled at THREAD level so no follow-up is graded
without its antecedent (that alone would manufacture false regressions), fired at staging with the same
runner the bank used, graded by hand on the same strict scale (no 7; ≥8 pass), each graded answer compared
against its own 2026-08-23 verdict. **All 319, fired in two parts** (one probe phone, threads must stay
adjacent, so the parts run back to back — never in parallel): `eval_bankC_pass_sample_2026-08-25.json`
(134 graded, 209 questions / 247 turns — stratified, all 16 classes, rare classes whole) then
`eval_bankC_pass_rest_2026-08-25.json` (the other 185, 218 questions / 252 turns). 499 turns total.
Thread tails past the last graded turn are trimmed; thread heads are kept, because a follow-up graded
without its antecedent scores a false regression.

**Accept when:** all 319 previously-passing questions re-run on staging ✅ · every one graded against its own
prior verdict ✅ · regressions listed by id with the before/after text, never a summary rate alone ✅ ·
execution status checked for the whole run, not one probe ✅ · leak gate GREEN with its exit code read
directly ✅ · then, and only then, the promote is put to Andy.

#### 📊 #145 MEASURED 2026-08-25 — all 319 re-run, 311 hold (97.5%)

| | build | graded | hold | regressions |
|---|---|---|---|---|
| part 1 | `daf8ec82` | 134 | 131 | 6083 · 6213 · 6219 — **fixed in wave 20, verified** |
| part 2 | `fec9a04b` | 185 | 180 | 6105 · 6200 · 6353 · 7052 · 6088 — **open** |
| **total** | | **319** | **311 = 97.5%** | 5 standing |

**Mechanically across all 319, 08-23 → now:** links **654 → 808** · dead links **5 → 0** · dates cited
**641 → 862** · route changes **0**. Runs: 499 turns, 0 dropped, 0 non-200, and **no staging execution
error since 2026-08-24T16:11Z** — the five came out of SUCCESSFUL executions, not crashes.

**The five still open, by cluster:**
- **Canned non-answer where the evidence exists (3).** 6105 "Sorry — I could not generate an answer just
  now." · 7052 and 6353 "I couldn't verify enough of the details against MDS data". 6353's bar names this
  exactly: "a third polite decline is the failure." **6052 answered the identical Cuttable question
  correctly in the same run**, so this fires nondeterministically, not on a class.
- **Follow-up binding (2).** 6200 answers a nudge on an open thread with "I don't see a specific message
  from you waiting on a reply anywhere" — the thread is discarded. 6088 binds a referent-less "they" to an
  unrelated edamame quote instead of saying it has no referent (the 08-23 answer said exactly that).

**Passed with a watch, not regressions:** 6435 + 6448 scheme-less `app.mds.co/...` links · 6139 + 6457
unlabelled trailing video links · 7022 + 6174 narrate their own search to the member · 6259 offers a
title-filtered search · 6297 adds a city the earlier spellings lacked · 6240 names posts without links ·
6193 reads "lately" as partners not chats · 6102 drops cities and the self-declared caveat · 6420 still
introduces herself as "Olivia" (identical to 08-23 — pre-existing, and #107 says Millie only).

**Artefacts:** `eval_bankC_pass_sample_2026-08-25.json` + `eval_bankC_pass_rest_2026-08-25.json` (banks) ·
`bankC_pass145_staging_2026-08-25.txt` + `bankC_pass145b_staging_2026-08-25.txt` (runs) · `pairs145.json`
+ `pairs145b.json` (pairing) · `grades145_full319.json` (every verdict with its reason) · `cmp145.json` +
`cmp145b.json` (the mechanical diff).

#### 🔧 FIXWAVE 20 — the three regressions found by part 1, fixed and verified on staging 2026-08-25

Staging `daf8ec82` → **`fec9a04b`** (snapshot `staging_2026-08-25T021944Z_pre-wave20`), apply script
`scripts/olivia_loop/apply_fixwave20_2026-08-25.py`. Each fix targets the mechanism, not the symptom.

| was | root cause | fix | verified |
|---|---|---|---|
| **6083** vouched on a fitness question (9 → fail) | the TRUST & CHARACTER rule enumerates a CLOSED list of asks — "trust, work with, hire or pay". A role-suitability ask is outside it, so the rule never engaged | trigger is now the SHAPE of the ask (any judgment of a person's fitness or quality), and a hedged verdict ("just my read", "could make him a good fit") is named as the same breach | *"isn't something I can judge … that kind of call about a person isn't mine to make"*, then observable facts only |
| **6213** shipped a link it retracted in the same sentence (8 → fail) | S1/S14 count only the rows that HAVE a url and then demand a link per cited item; a WhatsApp digest has none, so it borrowed an unrelated real permalink (post `10009755805794497`, 2025-10-07) | **S16** counts the rows with NO url and says those get named without one — "cite one that does" was reading as "find any url in this payload" | one takeaway, digests dated Aug 3-24, named members, zero borrowed links, zero retraction |
| **6219** invented a correction of itself (8 → fail) | the counting rule says reconcile a differing number and say why, but never says attribute it to its SOURCE — so she attributed it to herself | **G9** (Gate Verdict, deterministic): a self-correction sentence naming a number that appears nowhere in the conversation regenerates | *"California and Texas together: 156 members — 105 … plus 51 … (statewide counts, added up)"* |

**G9 audit before enabling** (standing rule): run over all 602 bank C answers PLUS the 134 part-1 answers,
each hit checked against its real `olivia_messages` history — 3 sentence-level hits, the history condition
kills 2 (6050 "Top 5 members", 6015 "Helium 10"), **1 fires: 6219, the real fail. Zero false positives.**

**Controls that had to survive, and did:** 6247 grounded PE correction (5 links, no invented correction) ·
6015 top-five by review count (5 partner links) · 6435 partner perks (4 links) · 6112 single item with its
own link · 6218 the counts that feed 6219. Run: 20/20 turns, 0 non-200, 0 dropped, **newest staging
execution error still 2026-08-24T16:11Z — nothing from this build.**

### #138 · Every cited item ships with its OWN link and date — 9 bank C fails
**🔴 S1 · size M — filed 2026-08-24 from the bank C loop (155/192 fixed; this is the largest thing left).**

> **In plain words:** she names six threads and links one, or names posts with no dates. The member
> cannot tell which parts they can go and check.

*As a member, anything Millie names I can open — every item carries its own link and its own date.*

**IDs:** 6031 · 6066 · 6150 · 6342 · 6007 · 6331 · 6028 · 6064 · 6236
**Why it is still open:** a prompt rule was written for this FOUR times (waves 8, 12, 16, 18) and it does
not hold. The last attempt (S14) counts the rows carrying urls and states the requirement per item; it
still ships answers with one link for five items. Ellipsis-truncated links ARE fixed (32 → 0, wave 9) —
this is presence, not truncation.
**Next thing to try, and it is not another rule:** a Gate Verdict check — if the evidence carried N urls
and the draft names N items with 0-1 links, regenerate. That is deterministic and auditable. It was not
built today only because the two refusal-gate regexes I audited fired on more correct answers than
wrong ones, and I stopped before adding a third unaudited gate late at night.
**Watch out:** 6342 also scored 2 for a separate reason now fixed (#137 record-id leak).

#### 🔎 2026-09-02 — RE-RUN OF THE 9 IDS AGAINST PROD: the symptom is REAL, and a gate cannot fix it

All 9 ticket ids re-fired against prod with their conversation context restored (32 turns, probe rows cleaned).
Graded against each id's recorded `expect` — one grader (me), not the six-grader panel that produced the
original scores.

| id | verdict | why |
|---|---|---|
| 6150 | ✅ pass | 4 brokers, 4 links, attributed (Bill Sterry / Scott Deetz), partner terms + ratings, no valuation advice |
| 6331 | ✅ pass | found the FB thread, served its 4 videos each with its own link and who recommended it |
| 6066 | ✅ pass | member card, revenue as a BAND, states plainly no Facebook link is on his card |
| 6342 | 🟡 borderline | 3 items dated, honest that the bodies are not retrievable; no links, but those rows carry none |
| 6007 | ❌ fail | 7 tools named, 2 linked — attribution good, links missing on 5 |
| 6028 | ❌ fail | 3 member names, no evidence quotes, no dates, no links, and the "no Target flag" caveat is not stated |
| 6031 | ❌ fail | still a capability tour; hot topics carry neither links nor dates |
| 6064 | ❌ fail (criterion) | 3 items, 1 link, no dates — otherwise honest and correctly refuses the character read |
| 6236 | — n/a | the antecedent turn answered differently this run, so the follow-up is not the same test |

**So the ticket is real: 4 clear fails, 3 passes, 1 borderline. My earlier "premise looks stale" read was wrong**
— it came from 22 random recent drafts, most of which are not citation-heavy answers. The 9 ids target exactly
the classes that still fail.

**But the repair does not fix them, and would add a wrong link.** Run against each failing answer's own evidence:

| id | evidence link-fields | repair attaches |
|---|---|---|
| 6007 | ~67 | **0** — the tool names live inside chat message BODIES; identity matching cannot bind them |
| 6064 | ~107 | **0** — same |
| 6028 | **0** | 0 — nothing to attach |
| 6031 | ~15 | **1, and it is WRONG** — "*The video library* — every Mogul Call…" got a specific Whatnot video url |

**Three different causes, none of them gate-shaped:**
1. **Retrieval gap.** `member_match_v2` and `expertise_search` return **no url column at all** (checked in
   `pg_get_function_result`) — a people list can never be linked. Fix belongs in the RPCs: give member rows
   their profile link.
2. **Binding gap.** For tools and quotes drawn from chat bodies, the url sits on a row whose identity fields do
   not name the item. Matching bodies instead is what produced the two wrong links that forced today's rollback.
3. **Wrong-shape answer.** 6031 is a capability tour; no link repair makes it the "what is live right now" read
   the bar asks for.

**Verdict: the link-repair approach is the wrong instrument and stays unshipped** (code + 28 tests in the repo).
#138 should be split: a retrieval ticket for (1), and a seed/drafting ticket for (2)+(3).

#### 🔎 2026-09-02 (after the rollback) — BOTH defects fixed, and the TICKET'S PREMISE now looks stale

**Fix 1 — who wrote a row is not what it is.** `author_name` / `post_author` are out of the identity match.
That was the prod defect: a WhatsApp row with `title:null` carried author_name + post_author both "Brandon
Himmel", cleared the two-token bar with no runner-up, and lent its permalink to an unrelated Brandon Himmel
quote (exec 127539).

**Fix 2 — no window fallback at all.** The re-audit produced a second wrong link: `https://kos.com`, a url
sitting inside Zenon Labs' own *description text*, attached as though it were their page (exec 127638). That
evidence contains **zero** link fields, so JSON parsing found no rows and the old text-window fallback took
over. A row now lends a link only from an explicit link FIELD; evidence without one has no link to give. The
unit fixtures were rewritten from invented pipe-delimited lines to the JSON shape the loop really passes —
the fake shape is what hid this.

**28 unit tests, all green. Third re-audit: 31 real drafts, 0 repairs, 0 wrong.**

**But: the symptom is no longer observable in production.** Over 22 unique recent drafts, 8 name three or more
items and the MEDIAN multi-item answer carries **3 links**. Exactly one draft matched the ticket's shape (6
items, 0 links) — and its evidence contains **zero urls** (a capability overview: chats, the Facebook group,
the video library). Nothing to link. That is the false-positive class the count-gate would have punished.

**Recommendation: do not ship the repair.** It is safe but fires zero times, and today proved that every line
of gate code carries risk. What #138 needs instead is a re-measurement: re-run its 9 ids plus the multi-item
classes against current prod and grade them. The bank C failures date from 23 Aug, before wave 9's clipSafe
and the S14 rule; if they pass now, close #138 as fixed by other work. The implementation and its tests stay
in the repo, unshipped, ready if the symptom returns.

**Constraint discovered today: n8n keeps roughly ONE DAY of executions.** The audit corpus shrank from 65 to
31 drafts within hours, so any evidence-based audit must be run and acted on the same day, or it must capture
its own corpus first.

#### ⛔ PROMOTED AND ROLLED BACK 2026-09-02 — NOT shipped (prod is back on `f2f4e9b8`)

**The ticket's own proposal was audited and REJECTED before a line of it shipped.** Across all 602 bank C
answers, the count rule ("names N items, carries ≤1 link") fires on more CORRECT answers than wrong ones at
every setting: ≥3 bullets/≤1 link = 116 fires, **65 on passing answers** vs 51 on failing, catching 3 of the 9;
the widest variant, 154 fires / 79 on passes / 4 of 9. It cannot tell "should have linked" from "there is no
link to give" — members, chapters and chats have no url. Shipping it would have regenerated dozens of good
answers to fix at most four bad ones, the same failure as the two refusal-gate regexes rejected on 2026-08-24.

**What shipped instead — per-item, deterministic, REPAIR not regenerate.** For each item line the draft names,
find the retrieved row it came from; if that row carried a url the draft dropped, attach it to that line. No
second model lap, so a good answer can never be clamped. Silence beats a wrong link: no match, a weak match
(<2 shared identity words) or a close one (<2 clear of the runner-up) all leave the line untouched.

**Two audit rounds against REAL prod evidence, both of which changed the code:**
- Round 1 (window matching): 65 drafts → 4 repairs, and **2 were wrong** — a Summit line-up post whose BODY
  listed half the speakers lent its url to "Brandon Himmel shared…" and to "Nathan Ross's teardown" (exec
  126957). Also pasted JSON tails (`","matched_rank":0.03`) into the answer, because `\S+` does not end a url
  in a JSON blob.
- Round 2 (structured rows, identity fields only, url cut at the delimiter): **64 drafts → 2 repairs, both
  verified correct against their source rows** (Douglas Iske → the Whatnot session whose TOPICS state the
  $175K/month run rate; "Retail needs its own playbook" → the Retail/Channel Call video). Zero wrong.

**Proof.** 24 unit tests written failing first (`scripts/olivia_loop/test_138_link_repair.js`, run with
`node`); the node code is the same logic inlined into Gate Verdict, best-effort inside a try/catch so it can
never break the send path. Staging probe: `gate: pass-postfilter`, no `gate_error`, correct no-op on an answer
that already carried a link per item. Prod probe after promote: exec 127624 `gate: pass`. Leak gate 306 PASS /
0 FAIL / EXIT 0 at promote.

**⛔ THE PROMOTE WAS WRONG AND WAS REVERTED WITHIN 5 MINUTES.** Promoted `c00987cd` 02:09Z, rolled back to
`f2f4e9b8` 02:14Z. Both prod probes had been no-ops (the model already linked every item), so "it works on
prod" was never actually tested — the verification that should have run first is running the LIVE node's own
bytes over real drafts. Doing that found the defect: on the 30 drafts still in n8n retention, prod's code fired
once and **the link was wrong**. A Brandon Himmel quote about SQP reports was given the permalink of a
different comment BY Brandon Himmel about damaged units in the rain (exec 127539).

**Root cause:** the identity fields matched on include `author_name` / `post_author`, so ANY row written by a
person the draft names can win the match. For content rows the author is not identity — the topic is.

**Fix before the next attempt:** exclude author-ish fields from the match, or require at least one non-person
token (title/topic word) to overlap before a row can be chosen; then re-audit against a corpus large enough to
mean something. The earlier "2 of 2 correct" was 2 fires — far too few to have claimed precision from, and that
corpus has since aged out of n8n's retention.

**AC status:** deterministic and auditable ✅ · never clamps a correct answer ✅ (repair, not regeneration) ·
gate GREEN ✅ · **shipped ❌ — reverted, still open**. The missing-DATES half stays disabled.

### #139 · A named partner ships with its recorded offer and its page — 5 bank C fails
**🔴 S1 · size S-M — filed 2026-08-24.**

> **In plain words:** she says "Jones Cosman CPA" or "Trainadz" and stops. The MDS deal — the reason
> a member asked her rather than Google — is on the same row and does not come out.

*As a member, when Millie names a partner I get the actual MDS offer and the link to claim it.*

**IDs:** 6075 · 7008 · 7018 · 7043 · 6301
**Why it is still open:** S2 (wave 8) and S15 (wave 18) both stamp the requirement off the payload. The
offers ARE in the rows. Note #135 fixed the related-but-different problem of the right partner not
ranking at all.

### #140 · A refusal names the REAL gate — no invented policy, no false capability denial — 6 fails
**🔴 S1 · size M — filed 2026-08-24.**

> **In plain words:** "I don't share who attended", "that list is held back for privacy reasons", "I
> have no way to see who's registered". All three are false: a registered member DOES get attendee
> names, and she can check registrations.

*As a member, when Millie withholds something she tells me which rule is holding it and how to get in.*

**IDs:** 6266 · 6267 · 6498 · 6356 · 6222 · 6361
**Why it is still open:** rules R2, R9, R14 and stamps S11, S13 all target this. **A phrasing gate was
tried and rejected on evidence:** both candidate regexes, audited over all 602 answers, fired on MORE
correct refusals than wrong ones — "I can't check that" is right when the thing genuinely is not
available. The discriminator is whether the payload holds the thing, which is why S13 is evidence-keyed
— and it still is not landing.

### #141 · "Not on file" when it is on file — 3 bank C fails
**🟡 S2 · size S — filed 2026-08-24.**
**IDs:** 6499 · 6500 (Fred's firearms brand — TLO Outdoors is in his own public Facebook post; she has
quoted the post and the product name "TLO Gun Sling" but never the business name) · 6471 (StoreClaw's
Summit session is on the agenda; she answers with the product blurb).
**Note:** 6500 REGRESSED in the last round — it now denies the firearms business outright where it
previously surfaced the product. Worth diffing the two answers before changing anything.

### #142 · The gate's hard-stop clamp answers real questions with a canned line — 3 fails
**🟡 S2 · size M — filed 2026-08-24. Deliberately not touched.**

> **In plain words:** after two failed regenerations `Gate Verdict` discards the draft and sends "I
> couldn't verify enough of the details against MDS data". For an out-of-scope question ("how high can
> a ball jump") a friendly one-line decline is the right answer and it never survives.

**IDs:** 6093 · 6483 · 7045
**Why it is still open — read this before touching it:** the clamp fires when claims genuinely WERE
raised, so it is doing its job; weakening it trades a safety backstop for three questions. Re-probing
these answers them correctly, so the block is INTERMITTENT (a timed-out tool leaves the draft
unsupported). Wave 12's S6 fixed the tool-error half — canned answers went 8 → 3 — and this is the
remainder.

### #143 · A follow-up binds to the wrong thing, or loses the thread — 3 fails
**🟡 S2 · size S — filed 2026-08-24.**
**IDs:** 6095 (names the 20M+ chat now but not its verification bar or application route) · 6201 (gives
the profile instead of the WhatsApp footprint) · 6349 ("yes please" restates the credit balance instead
of acting on the offer she just made).

### #144 · 2027 events answered wrong — BLOCKED on #123
**🔴 S1 — filed 2026-08-24. Cannot be fixed until #123 lands.**
**IDs:** 6370 · 6372 · 6400. The 2027 events the bar wants (Centurion Summit California, Summit Cancun)
live in the events CATALOG, and every `event_*` call is misrouted to the schedule endpoint (#123), so
the catalog is unreachable. No prompt change can reach them.

### #132 · "What can you do / what data do you have" — answer with CAPABILITY, and guide instead of dead-ending
**🟡 S2 · size M — filed 2026-08-24 (Andy, after reviewing three drafted answers: "I don't like these
answers, but I like the idea").**

> **In plain words:** today this question gets a fixed marketing card. The honest-inventory version I
> drafted was worse in a different way — it read like a list of data sources and it told a brand-new
> member what she *couldn't* see, which lands as "you're screwed" rather than help.

*As a member — especially a new one — when I ask what Millie can do, I hear what she can DO for me and
where to start, not an inventory of tables and not a list of what I'm locked out of.*

**Andy's direction (2026-08-24), verbatim in substance:**
- **Lead with capability, not sources.** She gives personalised answers, helps you find and connect with
  the right members, surfaces deals, events, calls — say THAT. The data list is the footnote.
- **Never present chat access as a dead end.** "I can read the chats you're in" is fine; "you're not in
  that one" as a full stop is not. For someone who just joined: *you haven't had a chance to explore
  yet — here's what MDS offers, here's the chat list, the chapters, and what's worth joining.*
- **Point outward:** the WhatsApp chat list, chapters, events — the things they could go get.

**Why it is not just a prompt tweak:** the turn is routed `help` in `Plan Request` and the help lane
bypasses the answer prompt entirely, so no seed rule can reach it (proved 2026-08-24 — fixwave 13 was
written to re-route it and REVERTED on finding the routing is deliberate, documented in the node from
2026-07-30: *"data-ACCESS phrasings are capability questions - the canned help list IS the answer"*,
added because the generated answer kept being blocked by the fact-gate). So this needs either a better
CARD (still deterministic, but capability-led and new-member aware) or a generated answer fed real
evidence rows so the gate has something to check. The evidence exists and is cheap: the asker's own
chats, their join date, their event count, the live chat/chapter lists.

**Accept when:** a brand-new member (e.g. Luke Li, joined 2026-08-19, 6 chats, 0 events) gets an answer
that leads with what she can do for him and points him at the chat list and chapters · a long-tenured
member (e.g. Mo Kuhail, 12 chats, 34 events) gets the same shape with his own footing reflected · no
answer frames a chat the asker is not in as a dead end · bank C 6002 and 6190 pass · gate GREEN.

### #106 · Staff and non-member records never surface in member-facing lists
**🟡 S2 · size S — filed 2026-08-22 (Andy, during #97's prod E2E: "I don't want people to see me as an attendee… make sure I'm not searchable. Verify in Supa, don't trust your memory")**

> **In plain words:** Andy's working record is `membership_status='Staff'`; the search lanes already exclude it, but the EVENT lanes don't — anyone registered for the same event can see him in attendee-name lists, and who-to-meet once recommended him to a member.

*As staff (or any non-member record), I never appear in a member-facing list — search, attendee names, who-to-meet, or the intro picker.*

**Verified in Supabase 2026-08-22 (not memory):** `member_match_v2` / `expertise_search` / `member_card` filter `membership_status in ('Current Member','New Member','Pending Group Entrance','Current Member- Not Renewing')` → Andy (Staff, `recCUUw8iiUnJjac1`) and his second record "Andy Ve" (`reccPuFFDGu75MP5e`, 'Pending 1st Interview', no phone) are **excluded from search**. **Not filtered:** `event_who` (attendee names for registered askers; reads `event_registrations_live` + members), the route's who-to-meet `people` op (reads `event.attendees`/`event.people` — no status filter) and chapter-name slice, and the #97 intro picker/eligibility (no status filter). Exposure found: Andy is live-registered for **4 past events** (Summit Denver 2024, Inspire 2025, Prosper 2025, Austin afterparty Apr 2026 — both records) → visible in those events' attendee-name lists to their registered askers; `olivia_recommendations` shows he was recommended ONCE (to Lucas Santic, lane `event_people`, 2026-08-20) — via the leftover `event.people` test row `test-andy-8153` (Summit roster). **Purged same session:** `test-andy-8153` (+ its `event.attendees` row). Summit: no registration for either record.

**Fix (next session):** one rule applied in three places — exclude non-member statuses (at minimum 'Staff', 'Pending 1st Interview', and any non-current status) from `event_who` names (SQL, CREATE OR REPLACE) · the route's `people` op + chapter-name slice (mds-digest-web) · the intro route's candidate/eligibility set. Counts (`total_going`) stay the census. Gate: add a check that a Staff record never appears in `event_who` names or the intro picker. Optional data hygiene: the 4 past-event registrations are real and harmless once the lanes filter.

**Accept when:** Staff record absent from event_who names for an event he's registered to (probe with a registered asker) · absent from who-to-meet · absent from the intro picker · gate GREEN · promote.

#### ✅ #106 CLOSED 2026-08-24 — SQL layer LIVE · route layer BUILT, NOT DEPLOYED (needs Andy's push)
**Trigger:** Eugene 2026-08-24 00:11 — *"Courtney and me come up as a suggestions for who to meet at
summit need to filter out the team. Look at the test chat for Ben Anderson as example."* Andy: *"add this
fix as well … but its search logic, make sure to apply it."*

**Reproduced first, not assumed:** `digest.olivia_recommendations` **6690/6691**, 2026-08-24 05:09:37Z,
lane `event_people`, asker Ben Anderson → Courtney Lee + Eugene Khayman, both `membership_status='Staff'`.

**ROOT CAUSE — one predicate doing two jobs.** `digest.is_active_member_status()` answers *"may this
person USE Millie?"* and correctly includes `'Staff'` (34 functions depend on it for exactly that —
narrowing it would lock the team out). Nothing answered *"may this record be SHOWN to a member?"*: only
`member_match_v2`/`expertise_search` carried a hand-copied literal allowlist that happens to exclude
Staff, `member_card` listed `'Staff'` in its own subject allowlist, and `event_who` + the who-to-meet
lane + the intro picker had no status filter at all. **A missing predicate, not a wrong one.**

**Shipped — SQL, live now** (`scripts/sql/20260824_106_internal_records_never_subjects.sql`, CREATE OR
REPLACE + `notify pgrst` each): new SSOT `digest.is_internal_record()` (Staff + Team User, btrim-safe) ·
`event_who` excludes internal records from NAMES, keeps the asker's own `is_me` row, `v_total` untouched
so the count stays the census · `member_card` excludes them on BOTH the exact-match and fuzzy-fallback
CTEs (the fuzzy path let a near-miss spelling walk past the first guard), with a self-carve-out so you
keep your OWN card; `member_card_v2` inherits it.

**Built — route, NOT deployed** (mds-digest-web; a push to `main` deploys to prod, so it waits for Andy):
who-to-meet candidates in `schedule/route.ts` now apply the existing tested `isMemberFacing()` (R8) that
the same file already used for `total_going` and the #108 finder route already used — this lane was the
only one that never did · `intro/route.ts` gains a TARGET-side `memberFacingSubset`, applied to both the
picker and the named-target path, while the REQUESTER gate stays registration-only so staff can still ask.

**Before → after (live numbers):** 33 internal records (30 Staff + 3 Team User) · Summit who-to-meet 140
attendees → **99 candidates, 41 excluded, 5 of them Staff** (Courtney Lee, Doina Chilat, Eugene Khayman,
Fernanda Arguelles, Ion Nederita — Eugene spotted 2 of the 5) · **6 Staff hold Confirmed Summit
registrations** and were eligible for `event_who` names; **153 Staff-confirmed registrations across all
events** · `member_card_v2` returned a FULL Staff profile (city, revenue tier, niche, about-me, FB link,
chapter, 9 chats) labelled `membership_state:'current'` → now `not_found`.

**AC checklist — ALL MET, route DEPLOYED 2026-08-24 (`/api/version` = `aff8941`):**
· Staff absent from `event_who` names for an event he's registered to ✅ — probed as registered member
  Aaron Biner: 10 names, 0 internal, `total_going` 116; and as registered STAFF Belén Gallardo: her own
  `is_me` row present, no other Staff name.
· Absent from who-to-meet ✅ — probed live on the DEPLOYED route as Aaron Biner: 8 names, **0 Staff**,
  matched_total 45.
· Absent from the intro picker ✅ — probed live as **Ben Anderson, the member from Eugene's report**,
  who has 8 recommendations in 30 days of which **2 are Staff**: picker returns no Staff, and the
  named-target path answers *"I can't set that one up — Courtney isn't available for intros."* The
  refusal never says "staff", so it does not disclose the record. Both probes send-free (picker is
  pure reads; named target used `dry_run`, which returns before any send).
· Gate GREEN ✅ **297 checks, 0 failures, EXIT 0** (+4 #106 checks). mds-digest-web `tsc` clean,
  **359/359 vitest** on the rebased base.

**The intro exposure was real and specific:** Courtney Lee is Staff, has a phone AND is Summit-registered
— so pre-fix she was a fully eligible intro target for Ben, and an accepted tap would have released her
number to him. Eugene Khayman is Staff with a phone but is NOT Summit-registered, so the registration
gate already excluded him from intros; his exposure was who-to-meet only.

**Shipped:** Scorecard `7e99584` (board + SQL record) · mds-digest-web `aff8941` on `main`, rebased onto
the five #122/#124 commits it was behind (`scorecard-cf` confirmed no overlap with the who-to-meet
region before the push). The ride-along commit is `d25fd52` (finder gate-reporting, the other session's).
**Andy approved the push; the SQL half was already live.**

**Found alongside, NOT chased (flagged for priority):** ① `'Current Member- Paused '` carries a trailing
space in the live data while every allowlist spells it without one, so those 3 members are silently
excluded from `member_card`'s subject set ② the never-were-members classes (`Removed Applicant` 70,
`Declined Applicant ` 20, `Dead Lead` 20, `Pending 1st Interview` 13, `Pending Application` 1) are out of
scope for "the team" but sit in the same subject position.

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

### #108 · The Finder — one lane, composable filters, every data layer
**🟡 S2 · size M — filed 2026-08-22 (Belen's reseller question) · design approved by Andy 2026-08-22, widened twice the same day · ✅ BUILT + PROVEN ON STAGING 2026-08-23 (gate 292 checks EXIT 0) — PROMOTE IS ANDY'S**

> **In plain words:** Belen asked which resellers are coming to the Summit. Millie named brand
> owners and missed the three real resellers. Two causes, both verified live 2026-08-22: no tool
> could filter by chat membership or business model — every tool carried its own hand-picked
> parameter list, so "reseller" arrived as topic words matched against self-written text — and
> `event_who` was misrouted: it sent only `p_event`+`p_limit` (no `op`), so the schedule route fell
> through to its default `op="next"` and returned the public agenda instead of attendees.

*As a member, I can ask for people by any combination of filters — what someone does, where they
are, which chat they're in, which event they're attending — narrow it further in my next message,
and get real matches with the reason each one matched, without ever being shown something I'm not
allowed to see.*

**Andy's rulings (spec `docs/superpowers/specs/2026-08-22-finder-design.md`):** the union — chat
membership OR declared business model — with the reason shown per person, never one signal silently
standing in for the other · **one tool, not two** ("what if I need a combination of member filters
on top of content?") · **cover all data layers**, and filtering power and disclosure are separate
axes — revenue is usable as a filter, never disclosed · **the request is a boolean TREE** (all / any
/ not, list = any-of — "like IFTTT") · **R10**: chat membership is a signal Millie may use for
anyone, but a chat is named only to its own members (restricted chats).

**What shipped (mds-digest-web, main, live on Render — 11 commits `f3aa2ab..600ce8a`):**
- `src/lib/finder-fields.ts` — the field registry; every filterable field classed 🟢 show / 🟡
  aggregate (never printable beside a name) / 🔴 internal (never filterable, never returned).
- `src/lib/finder.ts` — tree normalise + evaluate with reasons-as-proof; ten concepts (reseller ·
  private label · brand owner · agency · oem · supplements · tiktok · dtc · retail · large sku ·
  under 30); the disclosure engine (R1-R10); a class-aware parser with a closed allowlist (unknown
  field → 400; a 🔴 field → 400; a what-group leaf → `400 not served yet` so the model falls back to
  `content_search` / `video_search` honestly instead of a silently widened answer). 57
  finder-specific tests (`finder.test.ts`, vitest) · full repo suite 101/101.
- `src/app/api/olivia/find/route.ts` — `POST /api/olivia/find`; member-layer population 735 actives;
  event rosters; geo folding via the SQL SSOT (`geo_country_set` / `geo_state_set` / `country_fold`)
  added in a fix round after the first staging probe found "Europe" resolving to zero matches.
- Staging: workflow `bqHstPDi84uOhTCJ` versionId `a49047ac` (snapshots `pre-108` / `108-applied` /
  `108-find`) — Answer Tool routes the `find` tool to the route and `event_who` now carries
  `op:'people'`; Answer Seed declares the `find` tool + its routing rule. Apply script
  `scripts/olivia_loop/apply_108_find.py` (`8e92919`); canary `scripts/one_shots/canary_108.py`
  (`62fd6b3`).
- Gate `scripts/olivia_leak_gate.py`: **292 checks, EXIT 0**, 26 finder checks proving R1-R10
  non-vacuously (commits `ece7233`, `7211445`, `9994d95`, `8ca2c9b`).
- Live GRANT applied (`geo_state_set` was 403ing — `EXECUTE` missing on `attr_state`), recorded
  `scripts/sql/20260823_grant_attr_state_service_role.sql`.
- **PROD: #114 promoted ALONE by Andy 2026-08-23 06:48Z (versionId `bbd597b7`)** — staging was then
  rebuilt from prod (+#114) and no longer carries #108. #108 is re-applied to staging next
  (`apply_108_find.py`), re-probed/gated/snapshotted, and Andy promotes #108 separately.
- **Staging re-applied after the #114-only promote** — versionId `4321f06a` (snapshots
  `pre-108-reapply` / `108-reapplied` / `108-final`), #114 seed edits intact. Re-probes: exec
  `100210` (17 named), `100212` (Europe → 1), `100278` (breakdown by country, 5 buckets = 17,
  `people:[]`, reply reports counts not names). Parser robustness (`mds-digest-web` main,
  `0c46d42` + `d3fe132`): a multi-field object (`{segment,event}`) now validates as an implicit
  `all` instead of 400ing ("leaf holds exactly one field"), `where` may arrive as a JSON string,
  and `group_by` with no `return`/`ret` now defaults to `breakdown` — closing the two distinct
  LLM tool-call flakes found re-proving this ticket.

**Before → after:** before — a topic-sample tool named brand owners and missed all three real
resellers. After — **17** resellers registered for the Summit (of 102 attendees in the member
population), **122** community-wide (of 735 actives), every person carrying the reasons they
matched; "of those, who is in Europe?" → **1** (Joshua Asquith, United Kingdom) — the first probe
answered "none" until the geo-folding fix landed; "group them by country" → 5 clean buckets summing
to 17, full country names throughout. *(The spec's first baseline — 99 community / 21 Summit — was a
WhatsApp-layer count on `digest.members`; Task 5 corrected it to the member layer,
`member_attributes`, the canonical population — [[feedback_every_member_always]].)*

**AC checklist (spec §2):**
1. Summit resellers, union + reasons — **MET** (staging execs 100024/100094, total 17)
2. Community set, no event — **MET** (exec 100017, 121 live-probed / 122 canonical (SQL))
3. Follow-up narrows the same tree — **MET** after the geo fix (exec 100095, Europe → 1)
4. Breakdown, no invented names — **MET** (exec 100096, 5 country buckets)
5. `event_who` reaches attendees, not the agenda — **MET** (exec 100032; `op=people` returns the
   matched/ranked #99-style subset, not a flat roster — filed as #118)
6. Disclosure engine holds — **MET** (gate 24/24 incl. R10 via a non-staff member; exec 100031
   `sku_min` → counts only, no names)
7. Gate EXIT 0 + staging proof — **MET**; **promote — PENDING Andy**

**Follow-ups filed:** #115 (geo/data hygiene) · #116 (finder phase 2 content+video, phase 3
events/partners/forms — spec §6, own plan) · #117 (`--cleanup` leaves message rows) · #118
(`event_who` flat roster). Not filed as new tickets: **#111** should close as a side effect of the
concept map — verify against its own executions · **#106** stays open for lanes outside the finder ·
**#32** carries the uncached-answer-node finding, unaffected by this ticket.

**Plan/spec:** `docs/superpowers/specs/2026-08-22-finder-design.md` · SDD ledger
`.superpowers/sdd/2026-08-22-finder/progress.md` (10 tasks, each built + independently reviewed; 8
fix rounds in total (Tasks 3/4/5: one each · Task 9: three · the Task 8 geo fix: two)).

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

**THE PLAN OF RECORD (Andy 2026-08-24: "File it. We will target it after all is done" — i.e. after
the bank C loop closes). Current measured shape: ~$0.04 light answer / ~$0.15 heavy thread (bank C
counters, 24-turn sample: mean $0.125 answer-loop + 20-30% overhead) → ~$180–400/mo at full member
traffic, ~$110 per full-bank eval. Five levers, impact-ordered:**
1. **Split lap 1** — the forced first fetch becomes a tiny call (question + tool schemas only,
   ~2–3k tokens, `tool_choice any`); the big seed rides only the `auto` laps so `tool_choice` never
   flips against the cached prefix. Captures the proven −38% without the retrieval loss that killed
   the first attempt. Gate: A/B on retrieval (tool-call distribution per question vs baseline) +
   smoke tranche. Est −30–40%/answer.
2. **Regeneration + Fact Check hygiene** — regen laps re-bill the whole context (wave-7 checks are
   first-attempt-only for this reason); Fact Check writes a measured 8.4K speculative cache block it
   never reads (exec 102221) — cache it properly or drop its `cache_control`. Est −5–10%.
3. **Prefix diet** — the 31,696-token static prefix rides every lap ($0.30/MTok reads + full
   rewrite on every cold 5-min-TTL start); rules grew wave by wave and overlap. Consolidate; make
   lane-specific rules conditional on the lane. Quality-gated by the smoke tranche. Est −10–15%.
4. **Daily smoke tranche (~100 q)** — daily eval ~$15–20 instead of ~$110; the 602-question bank
   only before promotes. (Also filed on #124's follow-up.)
5. **Kimi comparison** — bank C's counters are the Claude side; one ~$6 `kimi_harvest/kimi_bench`
   run gives the Kimi side. Decision data only.
**Target after 1–3: roughly HALF per answer (~$0.02 light / $0.06–0.08 heavy → ~$90–200/mo).
Sequence: bank C loop closes → lever 1 (A/B-gated) → 2 → 3; 4 and 5 whenever convenient.**

**REVERTED same night (staging `f31b8c83`) — the A/B Andy ordered caught a retrieval loss: under
constant `auto`, questions that always retrieved (TikTok-agency: 2 calls, who-to-meet: 1) answered
from preload with ZERO tool calls, and the identical-request retry reproduces the same no-tool
choice. The forced `any` on lap 1 is what guarantees retrieval on lazy questions, so the cache
saving genuinely conflicts with it. Follow-up design to try: a stripped-down forced lap 1 (tiny
prompt + `any`) whose only job is choosing the first fetch, then `auto` laps carry the big seed
with stable caching. Measurement + root cause below stand.**

**SHIPPED 2026-08-23 (cache half, staging `470d635b`, commit `0b6fae3`): the invalidator was
`tool_choice` flipping `any`→`auto` between lap 1 and lap 2** — Anthropic invalidates the messages
cache when it changes, so lap 1's write (the whole seed, 1.3–8.8K tokens) was never read and every
turn boundary paid again. Measured before (execs 102219/102221): lap2 `cache_r` flat at the static
31,696 while rewriting lap1's content. Fix: `tool_choice: {type:'auto'}` constant; the forced first
fetch moved into CODE (Answer Parse `$runIndex===0` no-tool → one identical retry via the new
`First-Fetch Retry?` IF lane). After (execs 102745/102746/102752): lap2 `cache_r = lap1 r+w` —
extension works; same thread turn $0.115 → $0.071; single turn $0.036. Gate 292 EXIT 0.
⚠️ Watch at the bank-C run: one probe made 2 tool calls where the pre-patch run made 6 and wrongly
said Hannes Wiech has no Facebook link (his card carries `facebook_link`) — if `auto` reduced
tool-thoroughness at scale, revert is the one-line ternary. Also noted: Fact Check writes a
speculative 8.4K cache block it rarely reads back — left alone, one variable at a time.
Remaining for this ticket: fleet-level $/answer from the bank-C counters + the Kimi comparison.**

**FINDING 2026-08-22 (from the #108 design pass, verified against the prod snapshot
`prod_2026-08-22T210014Z`): the ANSWER node pays full price on every turn — it has NO prompt
caching.** `Answer Claude` and `Ask Claude` (both `claude-sonnet-5`, `max_tokens` 2000) carry no
`cache_control`; `Route Request` and `Fact Check` (both `claude-haiku-4-5`) do. So the stable
prefix — system prompt + the ~24 KB tool block (~6K tokens) — is billed as fresh input on every
single answer, where cached reads cost ~0.1×. The prefix is exactly the shape caching is built for:
frozen text, deterministic tool order, volatile content (the member's question and history) last.
Actions for this ticket: (a) measure the real per-turn input split with `count_tokens` before and
after, (b) add one `cache_control` breakpoint after the tool block, (c) verify with
`usage.cache_read_input_tokens` > 0 on turn 2 — if it stays 0, hunt the invalidator (a timestamp or
unsorted JSON in the prefix). Sizing against the existing baseline ($0.0135/answer, ~$110/mo at 748
actives): the savings land on the input half only, so treat "up to ~90% of prefix input" as the
ceiling, not the headline, until (a) is measured. Related: #108's `member_find` tool adds ~1.5 KB
(~400 tokens) to that same uncached block — ~$8-11/mo at 230-430 messages/day — which caching would
make ~free.

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

### #120 · Loader hardening after the #113 refresh (report cap · edge labels · reconcile test · in-place role edit)
**🟡 S3 · size S — filed 2026-08-23 from #113's final review.** The refresh loader works and is proven,
but four rough edges remain: the diff report prints every added row (525 lines last run; a first load of
a new event would print thousands) — cap per table with "… and N more"; added/removed EDGE lines label
their parent with the pre-write name, so a renamed activity reads under its old name; the reconcile /
`delete_stale` path has no unit test (a fake `rest` asserting the URLs per pk arity and that `dry=True`
issues none would have caught the unmeasured delete count); and `attendees` upserting on its natural key
does not cover the case where GroupOS edits a role IN PLACE (same `_id`, new `participant_type_id`) —
that would 409 on the PK and exit mid-upsert. Fix: delete natural-key-stale attendees before the
attendees upsert, or catch and explain the PK collision.

### #121 · `db/` does not cover the `event` schema — the Summit tables have no reviewable restore path
**🟡 S3 · size S — filed 2026-08-23.** `digest.schema_source()` introspects the `digest` schema only, so
`db/tables.sql` contains zero `event.*` objects and the #113 migration
(`event_events_load_provenance_20260822`) exists **only in the live database** — no diff, no review, no
restore path, which is exactly what #65 built `db/` to prevent. Extend the exporter to the `event`
schema and commit the resulting baseline. (Also to confirm while there: `db/grants.sql` gained
`grant execute on function digest.attr_state(text) to service_role` from unrelated live drift — someone
must say it was intended rather than inherit it silently.)

### #122 · "Explore Singapore Beyond the Summit" is four daily copies, so a name lookup answers with the first
**🟢 S4 · size XS — filed 2026-08-23.** GroupOS models the evening free-time block as one activity per
day (22–25 Aug). `op=where q="explore singapore"` matches the earliest copy, so a member asking on Monday
is told about Saturday. Same behaviour in `event_lane.py` and the deployed route (verified). Fix: when a
name matches several activities, answer with the one on the venue's today (or the next upcoming) and say
it runs every evening.

Same block of activities: the **Tue 25 Aug 22:30 Night Out row vanished from the agenda** on
2026-08-23 (`op=agenda` went to 37 activities; the row is gone, the catalog row `rec4SEDr6vYnwzxwT`
survives). Check whether it was renamed into one of these daily copies on purpose or lost upstream.

### #127 · RETRACTED as filed → folded into the #108/#124 epic as a wave-8 labeling rule
**Filed 2026-08-24 as "video_search_v2 serves restricted content (one-word RPC fix, prod-shared, needs
Andy's go)" — WRONG PREMISE, retracted same night after a live doorman test.** Verified with a
grant-less member against a genuinely restricted video: the shared RPC WITHHOLDS content and returns a
`[RESTRICTED VIDEO — never describe its content]` sentinel. No leak exists on prod or stage. The two
launch videos (9007/9026) are `access_restriction: public` in the catalog — Millie shared PUBLIC
content while wrongly LABELING it restricted (the sentinel from a different, restricted item in the
same evidence smeared onto the public one). Real fix (wave 8, epic): the restricted label in an answer
must come from that row's own `access_restriction`, never inferred from neighbours; probe with the two
verbatim launch questions. Nothing ships to prod; no Andy-gate needed. Lesson: [[reference_timeout_looks_like_no_data]]-class — verify the mechanism before shipping the diagnosis.

### #125 · "Not currently active" is sent to ACTIVE members whose number simply isn't linked
**🔴 S1 · size S — filed 2026-08-24, live at the Summit launch (Shyam Murali, +91 99406 69944).**

*As an active member texting Millie from a number the system hasn't linked yet, I'm told how to get
connected — never that my membership is inactive.*

**What happened:** Shyam Murali (Current Member, Chennai) texted during the on-stage launch and got
"this number is linked to an MDS membership that is not currently active." The truth: his WA-layer row
carried no membership status because the number wasn't linked. The refusal copy asserts a FACT about
his membership that is false and mildly insulting — at launch, to a paying member.
**Fix:** split the non-member path in `Resolve Member` (prod #31 block): (a) row found but status
empty/unlinked → "this number isn't connected to a member record yet — reply with the email on your
MDS account and the team will link it" (+ optionally auto-file a ticket row); (b) status genuinely
inactive → the current wording. Never claim "not active" unless the status field SAYS an inactive value.
**Repair path proven live 2026-08-24 02:00Z:** number added on the Members DB record (Andy) → the WA
record's `AT Database Status` lookup resolved → `Supabase Mirror (Members)` (15-min schedule, run
103880) wrote `membership_status: Current Member` into `digest.members` → the gate's ACTIVE check now
passes. **Accept when:** unlinked-number path sends the connect copy · inactive path unchanged ·
probe both classes on staging · gate EXIT 0.

#### ✅ CLOSED — PROMOTED 2026-08-25, prod `c20c1811` (Andy's go)
**The fix:** an absent status is the ABSENCE of the fact, not the negative of it. `Resolve Member`
now trims `membership_status` and returns a fourth reason, `unlinked`, when nothing is there;
`!ACTIVE.includes(...)` keeps the `inactive` reason for a status that actually carries an inactive
value. `Build Generic` gained the matching copy — it names the missing link and asks for the email
on their MDS account, and never mentions their membership state. **Enabling fix, same edit:**
`Build Generic` went straight to `Send Reply (Meta)`, bypassing the SELFTEST silent gate — the
remainder already filed under #146 — so this path could not be probed without messaging a real
person. It is now wired `Build Generic → Eval (silent)? → Send Reply (Meta)`, the same shape the
answer path uses; `Save Conversation` already no-ops on `matched !== true`, so nothing else changed.

| AC | result |
|---|---|
| unlinked-number path sends the connect copy | ✅ staging exec **110321** — `reason: "unlinked"`, reply = *"This number is not connected to an MDS member record yet… Reply with the email on your MDS account"*; the string "not currently active" is absent |
| inactive path unchanged | ✅ staging exec **110322** — `reason: "inactive"`, reply byte-identical to the copy that shipped before |
| probe both classes on staging | ✅ both above, plus exec **110324** proving an ACTIVE member (Staff) still reaches the full answer path, `Build Generic` never runs |
| gate EXIT 0 | ✅ **306 PASS · 0 FAIL · EXIT 0** after the change |
| no probe reached a phone | ✅ all three execs stop at `Eval (silent)?` output 0 — `Send Reply (Meta)` never executed; probe rows cleaned (`olivia_messages` 51968/51969, three `olivia_seen`) |

**Before → after** on the class the ticket aimed at: **53** `digest.members` rows carry a phone and
NO membership status; before the fix all 53 were told their membership "is not currently active",
after it 0 are. **21 of the 53 carry real member signal** (in MDS WhatsApp chats and/or already
linked to a member record) — Tomas Calonge (18 chats) and Mouad Errafik (12) are the clearest.
Regression test `scripts/tests/test_front_door_copy.py` (12 tests) runs the REAL node code out of the
live graph, so it cannot drift from what is deployed: **6 failed before the fix, 12/12 pass after.**
Staging `01c8670d` → **prod `c20c1811`**. Re-verified ON PROD after the bounce: exec **110345** `reason: "unlinked"` with the new copy, exec **110346** `reason: "inactive"` with the copy unchanged, `Send Reply (Meta)` never executed in either — the silent gate holds on prod too.

**Remainder, not fixed here:** the 53 still cannot use Millie — the repair is linking the number on
the Members DB record, which is Airtable and therefore Andy's or ops' to make, never the agent's
(2026-08-25 rule). The list of 21 is in the session log. `Current Member- Paused ` (2 rows, trailing
space) is not in `ACTIVE` and keeps the inactive copy — correct today, flagged to #115 as hygiene.

### #148 · The WA members mirror never reconciles — 12 rows Airtable stopped returning are frozen forever
**🟡 S3 · size S — filed 2026-08-25 from #126's audit.**

> **In plain words:** the mirror copies Airtable's WA member records into Supabase every 15 minutes,
> but it only ever adds and updates. When a record stops coming back from Airtable, its Supabase copy
> just stays — saying whatever it said the last time it was seen, and nothing anywhere says so.

*As a member, the system never answers me out of a record it stopped being able to check.*

`Recent Members (Airtable)` returned **659** rows in exec **110330**; `digest.members` holds **671**.
The 12-row gap has been widening quietly: the oldest untouched row last synced **2026-08-05**, twenty
days ago, and one of them is a COMPLETE row (name, status, `at_member_id`) that the front door will
happily match a phone against and treat as current. There is no delete path, no tombstone, and no
freshness signal — the failure `reference_mirror_freshness_signal` describes, and the same shape
#113's loader already solved for the event graph with an FK-safe reconcile.

**Shape of the fix:** every row a run touches is already stamped (`synced_at`); after each run, mark
the rows the fetch did NOT return — a `stale_since` column beats deleting, because a row that vanishes
for one bad Airtable call must never delete a member. The front door and the member lanes then skip
rows stale beyond a threshold, and `prod_pulse.py` reports the count instead of nobody noticing for
twenty days.

**Accept when:** rows absent from a run are marked, not silently kept ✅ · a one-run Airtable failure
cannot mark everything stale ✅ · stale count is visible in `prod_pulse.py` ✅ · the 12 current rows
are triaged (matched-and-current vs genuinely gone) ✅ · gate GREEN.

### #126 · WA mirror leaves `at_member_id` NULL although the AT record carries `source_member_id`
**🟡 S3 · size XS — filed 2026-08-24 (found under #125).** `Supabase Mirror (Members)`
(`Oy7RYcgLfDYhrPvw`) maps `at_member_id: f.source_member_id`, yet Shyam's row synced at 02:00:48 with
`membership_status` updated and `at_member_id` still NULL while the AT WA record has
`source_member_id = recTmVnVkcX7VJnMu` (matcher-set since 2026-07-24). Likely the mirror's Airtable
fetch omits that field, or change-detection skips it. Also his `crm_member_id` points at a dead record
(`recEbqcLdtM7aXV9z`) — and the canonical-key rule says at_member_id, never crm_member_id. Audit how
many of the ~646 mirror rows have NULL `at_member_id`, fix the field map, re-sync.

#### ✅ CLOSED 2026-08-25 — NOT REPRODUCIBLE; the audit it asked for found a different defect
**The diagnosis changed the ticket, so that first.** The field map was never wrong. `Recent Members
(Airtable)` fetches with no field restriction and returns `source_member_id` as a plain string
(mirror exec **110330**, e.g. `rec07yNXtfgc1JN1j → "recPUoaPTUiTtTT0P"`), and
`at_member_id: f.source_member_id ? String(...) : null` carries it. **Shyam's row today reads
`at_member_id = recTmVnVkcX7VJnMu`** — exactly the value the ticket said never arrived. It was sync
lag on 08-24, not an omitted field.

**The audit the ticket asked for, over all 671 rows:**

| `at_member_id` | `membership_status` | rows | not in the last Airtable fetch |
|---|---|---|---|
| present | present | 603 | 1 |
| present | **missing** | **11** | 0 |
| **missing** | **missing** | 57 | 11 |

**Zero rows have `at_member_id` missing while anything else about the member resolved** — all 57 also
have no `Member Full Name` lookup, meaning their Airtable WA record carries no `Member` link at all.
NULL is the correct, honest value for every one of them.

| AC | result |
|---|---|
| audit how many mirror rows have NULL `at_member_id` | ✅ 57 of 671 (8.5%), and all 57 are genuinely unmatched numbers |
| fix the field map | ✅ **no change needed** — proven correct against the live fetch, not read off the code |
| re-sync | ✅ n/a — 660 of 671 rows re-synced at 08:15:49Z on the normal 15-minute schedule |
| `crm_member_id` is not used as an identity key | ✅ it appears only as a passthrough column in `db/views/member_identity.sql`; no lane reads it |

**What the audit DID find, both named rather than folded away:**
1. **11 matched members carry no `AT Database Status`** — they have a `Member` link and an
   `at_member_id`, but the status lookup is empty, so `digest.members.membership_status` is NULL and
   they land on #125's new unlinked copy. Clearest: **Tomas Calonge** (18 chats), **Mouad Errafik**
   (12), **Palak Raniwala** (6), **Chris Murphy** and **Oran Mochly** (4). This is an Airtable-side
   correction — the linked member record, or the lookup — so it is Andy's or ops' to make.
2. **12 rows Airtable no longer returns** (11 of the 57 plus 1 complete row; oldest sync 2026-08-05)
   are frozen in `digest.members` forever: the mirror upserts and never reconciles, and nothing
   surfaces the staleness. **Filed as #148.**

### #124 · Bank C — a 400-question organic bank built on conversations, recommendations and expertise
**🔴 S1 · size L — filed 2026-08-23 (Andy: "we tested only 100 questions. Which is nothing in the grand scheme… I don't feel confident promoting anything yet").**

> **In plain words:** banks A and B are 100 and ~50 single questions. Real members ask in threads, they ask
> for recommendations, and they ask who is good at what — and none of that is properly measured. Bank C is
> built from what members actually wrote, kept as conversations, and weighted toward the two areas where
> being wrong costs trust.

*As the team, I have an organic bank large enough and shaped enough that a green run on it is real
evidence Millie is safe to promote — covering multi-turn follow-ups, recommendations, and
expertise/"who is good at what", not just isolated one-shot questions.*

**Why now (Andy, 2026-08-23):** "Since we applied the new logic, I need nothing less than great results."
Recommendations — "failing there means losing trust." Expertise — "in our community connections are
everything." Millie's own inbox is thin only because **she has not been announced yet**, so low volume is
not a quality signal and must not be read as one.

**Source (measured live, 2026-08-23):** 610 organic member asks to Millie · 551 after a junk filter ·
**423 never used by bank A or B** · 187 conversations of which **82 are multi-turn** (318 asks). Community
corpus `digest.content_items` = **54,764 items**, containing 2,007 "recommend", 1,331 "looking for",
284 "suggestion", 215 "experience with", 186 "anyone know", 80 "any good".

**Build — two tiers, both organic, never reworded by the author:**
- **Tier 1 — asked to Millie.** The 423 unused asks, minus the ungradeable. Every multi-turn thread stays
  intact and in order as a `seq`, so a follow-up is tested as a follow-up.
- **Tier 2 — asked to the community.** Real recommendation and expertise/connection questions harvested
  from `content_items`, taken as the member wrote them. Where a question needs its lead-in to make sense,
  the lead-in becomes a preceding turn (which adds follow-up coverage).
- `expect` written from the tickets, ACs, rulings and the live data — **never invented**. Many tier-2
  threads already contain the community's own answer, so the bar is often "surface what members said".
- Same schema as A and B (`id, class, q, expect, soft, asker, first_asked, seq, regression, retired`),
  ids in the **6xxx** range, runnable via `scripts/run_eval_100.py --bank`.
- The bank's topical mix must match the real mix of what members historically ask, so it measures the
  product members use rather than the one we imagine.

**Inherited rules (Andy, #76 / #119):** ORGANIC questions only · LOCKED once written · size = what the
questions justify · retire always-passing questions at sprint close · snapshots kept · no duplicates with
bank A or B.

**Accept when:** `eval_bank_C_2026-08-23.json` committed with ~400 questions · every question is a real
member sentence with its source and date · ≥ 82 multi-turn threads preserved as `seq` · recommendations
and expertise each ≥ 40 questions · all 7 asks from the last 24h included · zero duplicates against A or B ·
one full STAGING run scored on the strict 1-10 scale (no 7; 8-10 pass) and written up as
`OLIVIA_SMOKE_BANK_C_<date>.md` · run time recorded honestly.

### #123 · `event_lookup` never reaches the events catalog — every `event_*` call is sent to the schedule endpoint
**🟡 S2 · size M — filed 2026-08-23 from the #108 fix-wave-4 review.**

> **In plain words:** Millie has two different sources for events — the *schedule* of the event you are
> attending, and the *catalog* of every MDS event past and future. She can only reach the first one. Ask
> her about an event that is not on your Summit agenda and she gets the Summit's agenda back instead.

*As a member, when I ask about an MDS event that is not on my current agenda — a side event, a past
summit, next quarter's roundtable — I get that event's details, not the schedule of the event I happen
to be registered for.*

**What is wrong (verified live on staging `bqHstPDi84uOhTCJ`, 2026-08-23):** `Attach Embedding`'s
`EXEC_NAME` map rewrites `event_lookup → event_lookup_v2`, and `Answer Tool` then routes **anything**
whose `tool_name` starts with `event_` to `https://digest.mds.co/api/olivia/schedule` — the catalog RPC
is never called. The schedule endpoint ignores `p_terms` and answers with the live event's agenda.
`event_history_v2` has the same fate. The clean fix was proven to work in wave 4 (`event_lookup_v3` with
`p_phone` plus the model's own argument shape returns the right rows) and **deliberately not shipped**.

**Why it was not just fixed:** bank question A4071 currently passes *because of* the misroute. The
catalog's own row for the running Summit reads *"THIS EVENT HAS ALREADY HAPPENED"* and carries no
registration link, so routing correctly today would regress a passing item. The catalog's
`start_display` / `reg_link` for an in-progress event must be sorted out first.

**Fold in while there:** `event_lookup_v3` prints `(time as listed: 22:30 UTC)` for an on-site side
event that the agenda correctly shows as `10:30 pm Singapore time`. The seed now forces the venue's zone
in the answer, so the wrong label is contained — but it is one prompt away from reaching a member.

**Accept when:** an `event_lookup` call reaches the catalog RPC and returns catalog rows · the running
event's catalog row shows a correct start and a live registration link (no "already happened") · A4071
still passes for the right reason, from the right source · a side event asked about by name answers from
the catalog with its own RSVP link · `event_history` reaches its RPC too · gate EXIT 0.

### #113 · Summit event refresh — reload the whole event from a GroupOS export, removals included
**🔴 S1 · size M — filed + built + loaded 2026-08-23.**

> **In plain words:** the loader only ever ADDED and UPDATED. Anything GroupOS removed or re-gated
> since the first load (2026-08-17) stayed in the database and kept gating what members could see —
> and the schedule Millie served was three weeks stale: old names, no new rooms, 200-character
> description stubs.

*As a Summit attendee asking Millie, I get the current run-of-show, rooms, access lists and rosters —
whatever GroupOS holds now — not the snapshot from the first load.*

**Built:** `scripts/load_event_graph.py` became a true refresh — a name-level diff report printed
before any write (`--dry-run` writes nothing), a reconcile that deletes rows the export no longer
contains in FK-safe order (`event.people` never), an export-freshness guard against the live
registrations ledger, a pending-reminder cascade warning, `--no-reconcile` / `--new-event` flags, and
provenance columns (`event.events.source_scanned_at` / `loaded_at`, migration
`event_events_load_provenance_20260822`). First unit tests under `scripts/tests/` (44).

**ACs:**
1. `--dry-run` prints added / changed / removed by NAME for every table — ✅.
2. A run removes what the export removed — ✅ deleted: activity_audience 49 · activity_person_grants 10 ·
   session_speakers 12 · sessions 11 · activities 1 ("Women's Lunch - Register NOW") · attendees 20,
   every count matching its dry-run prediction.
3. Export freshness is checked and stale exports are named — ✅ (it caught the file handed over on
   08-22 as a 17-Aug scan missing four registrants; the 09:52Z scan reported "export is current").
4. `event_lane.py --self-test` passes after the load — ✅ re-derived from the data: plain Member 7,
   Women's Lunch grantee 8, the +1 invariant intact.
5. Live lane proof — ✅ `{"op":"day","at":"today"}` on prod returns *Sunday 23 August* with Arrive &
   Check-In to the Hotel at 3PM · Early Mixer · Event Check-in & Swag Bag Pick-Up · Welcome Reception ·
   Meet N' Speed · Welcome Dinner · Explore Singapore Beyond the Summit; Women's Lunch and Event
   Partner Check-in correctly hidden from a non-invited member; speakers 30.
6. Runbook in the handbook — ✅ §4.9 (commands, flags, provenance semantics, six traps).

**Two real bugs the run exposed, both stopped safely with nothing deleted, both fixed and proven:**
GroupOS recreates an attendee document when a role changes (new id, same natural key) → 409 on
`attendees`; fixed by upserting on the natural key, while `participant_types` (whose id IS
FK-referenced) now REFUSES a recreated role instead. And request bodies were passed to `curl` as an
argv element → macOS ARG_MAX (~1 MB) blew up on a 92 KB activity description; bodies now go on stdin.
A third defect was caught before the load: Apple's Python 3.9 rejects the 2-digit fractional seconds
PostgREST returns, which faked 31 "changed" rows and broke idempotency.

**Final review (opus) + one fix wave, all re-reviewed clean:** a loader SKIP is never treated as an
export removal (a data-entry slip would have deleted a live activity and CASCADEd its access rules);
three reads that silently swallowed an HTTP failure now fail loud (one of them would have NULLed all
234 `at_member_id` links); paging is deterministically ordered (698 grant rows, unstable past 1000);
delete counts are measured, not assumed; loading a second event is refused without `--new-event`.

**CLOSE — before → after (2026-08-23):** activities **50 → 86** · sessions 31 → 26 · attendees 178 →
199 · people 199 → 234 · locations 18 → 27 · participant_types 6 → 7 (`MDS`) · activity_audience
**180 → 227** · activity_person_grants **183 → 698** · session_speakers 35 → 34 · check_ins 22 → 151 ·
orders 138 → 144 · rooms 6 · faqs 19 · tickets 25 · reminders 0. Descriptions: 200-char stubs → full
bodies (86 activities, 26 sessions). A repeat dry-run reports `+0 ~0 -0` everywhere. Backup of the
pre-load state kept for the session in the scratchpad.

**Follow-ups filed:** #120 (loader hardening: report cap, edge labels use the planned name, a unit test
for the reconcile path, the attendees in-place-edit PK case) · #121 (`db/` does not cover the `event`
schema, so this migration has no reviewable restore path — extend `schema_source()`) · #122 ("Explore
Singapore Beyond the Summit" exists as four daily copies, so a name lookup answers with the first one).

### #114 · "Today at the Summit" must resolve in the venue's zone, not US Eastern
**🔴 S1 · size S — filed + built 2026-08-22/23 (Ian Sells, Singapore, asked "what's happening at the summit today?" on his Sunday and got Saturday's list).**

> **In plain words:** the seed anchors TODAY on US Eastern, and the `event_schedule` tool
> description told the model to compute `at=YYYY-MM-DD` itself for the `day` op — so for roughly
> half of every day, while the Singapore venue is already on tomorrow's date, "today" answers came
> out a day stale.

*As Ian in Singapore on Sunday, "what's happening today" returns Sunday.*

**Fixed in two layers.** mds-digest-web (Tasks 1-2, LIVE prod, 2026-08-22): the schedule route
resolves `at=today|tomorrow|yesterday|<weekday>|YYYY-MM-DD` in the event's own timezone
(`src/lib/schedule-day.ts`) and every response now carries `now_at_venue`; the `day` op also
returns `day`/`day_label`/`resolved_from`. Olivia (Task 3, STAGING `bqHstPDi84uOhTCJ`, 2026-08-23):
the `Answer Seed` node's `event_schedule` tool description now tells the model to pass the WORD for
today/tomorrow/yesterday/a weekday, never a date it computed; the TODAY anchor line now carves out
an explicit venue exception; a new bullet spells out the today/tomorrow/weekday case by name,
citing Ian's miss. `scripts/olivia_loop/apply_114_venue_today.py` — 3 exact-string edits (each
verified to occur exactly once), `node --check`, one bounce. First applied on top of #108's
concurrent staging edit; Andy chose to promote **#114 only**, so staging was re-built from prod
(snapshot `staging_2026-08-23T064414Z_108-plus-114-applied` keeps the combined graph), the 3 edits
re-applied, gate re-run (PASSED, EXIT 0), `diff prod staging` = `Answer Seed` + the two webhook
nodes only — then **promoted 2026-08-23 02:49 ET (prod versionId `bbd597b7`)**, lock released,
staging handed back to #108.

**Task 2b (added after Andy's live test, 2026-08-23):** asked "what's happening at the summit today"
at 12:42 pm SGT, the model called `op=next` (exec 99999) and the route's hard `slice(0,3)` hid half
the day (Early Mixer · Check-in · Welcome Reception). `next` now returns the **rest of the venue-day**
when more than three remain, else the classic next three (`pickNext`; answer carries `next_scope`,
`day`, `day_label`, `asked_day`, `remaining_today`) — mds-digest-web `95eea25`, proven on Andy's
phone at 14:16 SGT (4 remaining: Check-in, Welcome Reception, Meet N' Speed, Welcome Dinner). Final
whole-branch review fix wave `9d0ec41` (live): `next` labels the ITEMS' day when it reaches into
tomorrow (`asked_day` kept), `now_at_venue` wins the spread, impossible explicit dates fall back to
venue-today, boundary tests; 24 resolver tests, suite 105/105.

**ACs:**
1. Route resolves relative words in the venue's own zone (vitest) — ✅ Task 2 (mds-digest-web).
2. `now_at_venue` rides every `event_schedule` answer — ✅ Task 2.
3. The seed passes the word, never a computed date — ✅ staging: exec 100110
   `tool_args={"op":"day","at":"today","p_phone":"17866578153"}`, exec 100111
   `tool_args={"op":"day","at":"tomorrow","p_phone":"17866578153"}` — literal words, not dates.
4. Live proof while ET and the venue's calendar date DISAGREE — ✅ **CLOSED: Andy tested it himself on
   WhatsApp on 2026-08-23 in the ET afternoon (Singapore already on the next calendar day) and reported
   it working.** Original pending note kept below for the record. The probe below ran
   ~2026-08-23 06:26Z (≈02:26am ET), when US-Eastern and Singapore (SGT, UTC+8) both already read
   "Sunday 23 August" — it proves the seed passes the word and the answer opens with the venue's
   day, but not the disagreeing-date case (needs the 12:00-23:59 ET window, when SGT has already
   rolled to the next day). Tracked here, not blocking this ticket's staging work.
5. Staging reply opens with the venue's day, not a US-Eastern-anchored one — ✅ probed:
   "What's happening at the summit today?" → opens *Sunday, Aug 23* (day-one activities: Arrivals,
   Early Mixer, Event Check-in & Swag Bag Pick-Up, Welcome Reception, Meet N' Speed, Welcome
   Dinner); "What's on tomorrow?" → opens "Here's Monday's lineup: *Monday, 24 August*".
6. Promote — ✅ Andy, 2026-08-23 02:49 ET (prod versionId `bbd597b7`; snapshots
   `prod_2026-08-23T064801Z_pre-promote` / `064805Z_post-promote`); lock released 02:53 ET.

**Evidence:** apply script — `Answer Seed: 3 replacements, node --check OK` / `PUT ok` / `bounce ok,
active: True`. Gate (#114-only graph) — `GATE PASSED — retrieval refuses everything it must refuse.`,
EXIT 0. Diff before promote — `changed: ['Answer Seed', 'WA Inbound (POST)', 'WA Verify (GET)']`
(the two webhook nodes always differ prod/staging); after promote `diff prod staging` = webhook
nodes only. Staging probe (executions 100110/100111) and **prod probe after promote** (executions
100159/100160): "What's happening at the summit today?" → *"It's Sunday, 23 August at the Summit in
Singapore — kickoff day!"* + the full day 9:00 am Arrivals … 7:00 pm Welcome Dinner,
`tool_args {"op":"day","at":"today"}`; "What's on tomorrow?" → *Monday, Aug 24* 7:30 am … 5:05 pm,
`{"op":"day","at":"tomorrow"}`. Route curls on prod: `at=2026-08-22T23:00:00-04:00` (Ian's exact
instant) → `2026-08-23 Sunday`; bare `2026-08-22` → Saturday (a member naming a date is honoured);
`at=2026-08-23T12:30:00-04:00` → `2026-08-24 Monday`; `at=2026-13-45` → `resolved_from: fallback`.

**CLOSE (2026-08-23 03:15 ET) — before → after:** "what's happening today" on Sunday 11:30 SGT:
**Saturday's 3 pre-event items → Sunday's full day (6 for a plain Member)**; same question at 12:42
SGT: **3 items (hard cap) → the rest of the day (4–5)**; day resolution: **model-computed US-Eastern
date → venue-zone word resolved in code** (execs 100159/100160 carry `at:"today"/"tomorrow"`).
ACs 1–3, 5, 6 ✅ · AC 4 ⏳ the only open item: one WhatsApp "what's happening at the summit today"
between 12:00 and 23:59 ET (venue already on the next day) must open with the venue's day — unit tests
pin the math, the Ian-replay curl proves the route, the model link is what this last probe covers.
Virtual events deliberately out of scope (member's zone is unknown by design).

## ✅ CLOSED (Sprint 4)

### #154 · Every person she names can be opened — member and expertise rows carry no link at all
**🔴 S1 · size S-M — filed 2026-09-02, split out of #138 after the 9-id re-run.**

> **In plain words:** when she lists people, none of the names can be clicked. Not because she drops
> the link — because the tools that find people do not return one.

*As a member, every person Millie names comes with a way to reach or check them — her profile, her Facebook, something I can open.*

**Evidence (2026-09-02, re-run of bank C #6028 against prod):** "top 3 members for selling on Target"
returned Tracey Larner, Alexander Malamud and Zal Shemtov — three names, no dates, no links, no quotes.
The evidence blob behind that answer contains **zero link fields**. Checked at the source with
`pg_get_function_result`: `digest.member_match_v2` and `digest.expertise_search` declare **no url column
whatsoever**; `member_card_v2` carries only `facebook_link`, and only for a single member. No gate, prompt
rule or repair can attach a link that retrieval never returned — this is why four prompt rules (waves
8/12/16/18) and a Gate Verdict repair all failed on this class.

**Shape of the fix:** the people-returning RPCs return a per-row link — the member's app profile URL,
falling back to their Facebook link — the same way `video_search_v2` returns `video_url` and
`partner_lookup_v2` returns `partner_url`. Retrieval layer, not the prompt. Respect #106 (staff never
surface) and the disclosure rules: a link is only a pointer, never contact detail.

**Accept when:** `member_match_v2` · `expertise_search` · the finder's people rows each return a link
column ✅ · a live people-list answer names three members and every one carries its own link ✅ ·
no staff record gains a link ✅ · gate GREEN · `db/` re-exported after the migration.

#### ✅ CLOSED 2026-09-02 — prod `d40a837d` (Andy: "do all the pushes") · finder live on Render `8f368b3`
**The fix:** migration `people_lanes_link_154` (+ `member_link_normalise_154`): `digest.member_link(at_member_id)`
is the ONE definition of a member's link — the profile's own Facebook url, else the FB-engagement map's vanity
url, else `profile.php?id=<uid>`, normalised to `https://www.facebook.com/…`; never a phone, email or record id.
`member_match_v2` and `expertise_search` now return it as `link` (RETURNS TABLE changed → DROP + CREATE with the
exact grants restored: postgres + service_role, public revoked — verified in `proacl`). View `digest.member_links`
exposes the same helper for app routes; the finder (`mds-digest-web` commit, awaiting push) emits `link` on every
person row. Staging `e55a45c6` (re-staged from prod so ONLY the seed edit rides; the rolled-back #138 block is gone): the two tool descriptions tell the model to put each link on that person's line.

| AC | result |
|---|---|
| `member_match_v2` · `expertise_search` · the finder's people rows each return a link column | ✅ both RPCs (gate checks "rows carry a link column"), finder route emits `link` (252/252 tests, `tsc` clean) — finder live only after the push |
| a live people-list answer names three members and every one carries its own link | ✅ staging probes 03:40Z: "who should I talk to about Amazon PPC?" → 4 members, 4 links, one per line; "which members are in Texas?" → 10 members, 10 links |
| no staff record gains a link | ✅ existing #106 checks still pass; links are computed on rows the lanes already filtered |
| gate GREEN | ✅ 312 PASS · 0 FAIL · EXIT 0 (7 new #154 checks: link column present, facebook.com only, no phone/email/record id beside it, ≥80% resolve) |
| `db/` re-exported after the migration | ✅ `db/functions/member_link.sql`, `db/views/member_links.sql`, both lanes, grants |

**Before → after** on the class (#6028 "top 3 members for selling on Target"): 3 names, 0 links → the same lanes
now carry a link on **718 of 741** active members (23 have neither a profile link nor an FB-map row — those rows
return `link: null`, which the model leaves unlinked rather than inventing). 18 profile links arrived as
`m.`/`web.`/no-scheme/upper-case variants and are normalised; 0 non-canonical remain.

**On prod after the promote:** "who should I talk to about Amazon PPC?" → 5 members, each with their own Facebook link on their own line (03:49Z). **Finder live:** POST `/api/olivia/find` (Texas, people) → 5 rows, 5 carry `link`. Gate re-ran GREEN inside the promote.

**Remainder:** the 23 unlinked actives are a data gap in Airtable (no Facebook Profile Link) — ops, not code.


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

