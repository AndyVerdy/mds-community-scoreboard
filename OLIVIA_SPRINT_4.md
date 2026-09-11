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

## 🔗 WORK THESE TOGETHER (Andy 2026-09-09: "we are following your plan")
Re-prioritised 2026-09-09 — open 46: **S1 5 · S2 14 · S3 18 · S4 6 · standing 3** (was S1 7 · S2 26 · S3 4 · S4 5).
Bar used: **S1** = a member or member-facing surface is wrong today, or we are exposed · **S2** = real defect, nobody
wrong right now · **S3** = worth doing, no pressure, or blocked on someone else · **S4** = no cost to leaving it.

| Cluster | Why together |
|---|---|
| **#105** *(alone — was "#105 + #97", corrected 2026-09-09)* | #97 needs no promote: it shipped 2026-08-22 (`7e4be40a`) and its seven intro nodes are on prod `15649d68`, verified live. So the pairing was built on a stale row. #105 stands on its own as the engineering: the WhatsApp webhook still accepts any POST from anyone and never verifies `X-Hub-Signature-256`. What waits on it is Andy's wide intros ANNOUNCEMENT, not a promote. Note the exposure is narrower than the old row implied — a forged intro Accept is already inert, because taps bind to the exact template `consent_wamid`; the real hole is unsigned inbound in general. |
| **#180 + #64** | `derive_niches` is one of the eight launchd plists that exist only on Andy's Mac and in no repo. Fixing #180 alone fixes one of eight. |
| **#116 before #111 / #118** | ✅ **OVERLAP CONFIRMED 2026-09-10, and it is DEFERRED, not immediate.** The finder spec names retiring `member_match` / `member_count` / `event_who` as an explicit **phase-1 NON-GOAL** (§ "Non-goals (phase 1)"), and puts retirement in phase 2-3 — i.e. **#116**, which is size **L** with no plan and no date. So **#108 does not throw #111 or #118 away**; #116 eventually will. Decide on that basis: patch them now and accept the rework when #116 lands, or schedule #116 first and skip both. |
| **#182 + #17** | One GroupOS PAT unblocks both; #17 is "stop pulling videos and partners by hand", so #182 alone means pulling by hand again next week. |
| **#184 → #185** | A hand edit for #184 reverts at the next re-embed — exactly what #185 exists to prevent. Build the smallest real mechanism, then apply it to the three keys. |
| **#68 → #66 → #73 (+ #74, #67)** | One forms epic: #66's mapping was split out to #68, #67 depends on #66, #73 needs the mapping, #74's orphans only matter once forms are wired. |
| **#179 + #181 + #183** | All `mds-digest-web`; one branch, one Render deploy. The stale `HEALTH_REPORT_SECRET` chore rides along. |
| **#158 vs #148 / #74** | All orphan problems, but #158 states mirrors stay FK-free on purpose and #148 IS a mirror — check the nightly orphan check reaches mirrors before merging them. |

**Blocked on Andy (2026-09-10 close):** **#172 Day-0** — migration go · rulebook ruling · Render env (`MILLIE_TEAM_ASKERS`, `VOYAGE_API_KEY`, `NODE_VERSION`) · placeholders · staff validate the 20 questions · GroupOS PAT (#182, #17) · Circleback details (#36) · #186's two-docs call · #118 with Eugene · #32's send. RULED today: #147 mirror · #184 hold for Eugene · #157 stay on Sonnet 5 · #71 recording · #190 = sprint-closure eval. #181's PAT exists (n8n credential pending, expires 2026-10-10).



## 🌙 OVERNIGHT TRIAGE 2026-09-10 — where the other tickets actually stand

Worked through the open list rather than only the ones I closed. **Nine closed** (#179 #105 #180 #183 #148 #115
#117 #187 #188), **#152 verified as already-fixed drift**, **#72 retired**, and the rest sorted below with what is
actually true today rather than what the row said.

**⛔ BLOCKED ON ANDY — nothing moves without these, and each is minutes of his time**
| # | the exact ask |
|---|---|
| **#181** | GitHub PAT with `actions:write`. Its symptom is live right now: the events catalog ~2h behind an hourly schedule is the amber tile on the health report. |
| **#182**, **#17** | One GroupOS PAT unblocks both. |
| **#184**, **#185** | Eugene's ruling on whether members' own posts are in scope, not just the two partner profiles. |
| **#36** | Circleback details. |
| **#157** | The Sonnet 5 vs GPT-5.6 vendor call — a decision, not a ticket. |
| **#32** | Rides the Big Smoke and reports to Pavel; Andy sends. |

**⚖️ NEEDS A PRODUCT RULING BEFORE ANY CODE — verified, not guessed**
- **#71** — re-probed tonight, still contradicting (above). What counts as a "call" spans two catalogs.
- **#118** — a plain "who is coming" returns a ranked, personalised subset. Touching it moves the **name-disclosure**
  rules Andy and Eugene set in #96, so it is not a solo change.
- **#148's lane-skipping** — refusing stale mirror rows changes **who Millie will answer**; a wrong threshold
  refuses real members. The rest of #148 shipped.

**🔎 RE-SCOPE BEFORE WORKING — the premise changed**
- **#74** — see the row: mostly non-members by design, and matching does not work (above).
- **#72** — RETIRED tonight; its measurement half is #187, closed.

**🧱 REAL WORK, NO BLOCKER, JUST SIZE** — #172 (L, team chat) · #170 (thread memory) · #173 (source trail) ·
#177 (Public answer under-names) · #116 → #111/#118 (the Finder retires the lanes they patch — confirm the overlap
first or the work is thrown away) · #68 → #66 → #73 (one forms epic) · #64 (runtime inventory — **tonight proved
why it matters**) · #158 (FKs) · #102 · #92 · #119 (Bank B) · #186 (roadmap, peer-owned).

**🪫 LOW VALUE / STALE FRAMING** — #14, #19, #34, #35, #48, #67 are bare rows with no story, no ACs and no recent
evidence. Worth a sweep with Andy to decide which still matter rather than carrying them.

**⚠️ Two things that will bite if left:** the Meta app secret is in a chat transcript and needs rotating, and
`derive_niches` refreezes on the next night the laptop lid is shut (`sudo pmset repeat wakeorpoweron MTWRFSU
04:25:00`).

## 📋 At a glance

| # | Ticket | Priority | Size | Staging | Prod |
|---|---|---|---|---|---|
| **#186** | 🅿️ **SPRINT 5** · 🗺️ Roadmap tool — a dev index and a live task list, both pulled from the repo, never hand-maintained (Andy 2026-09-09) | 🔵 S3 | M-L | — | — |
| **#184** | 🙈 Part 1 — unindex Tony Brink's post + MajestIQ/TraceFuse from Millie, nothing deleted for members ([CU `86e35hm1p`](https://app.clickup.com/t/86e35hm1p)) | 🔴 S1 | S | — | — |
| **#185** | 🚧 Part 2 — a general way to keep restricted content out of Millie: blacklist, detection, or both ([CU `86e35hm1p`](https://app.clickup.com/t/86e35hm1p)) | 🟡 S2 | M | — | — |
| **#179** | 🩺 A Make WARNING shows as a tool DOWN — `status !== 1` maps to error, so Guest Multi-Event is permanently red | 🔴 S1 | XS | n/a (app code) | ✅ **CLOSED 2026-09-09** — shipped `0fcb6df`, merged `6a31026`, live on Render (`/api/version`) |
| **#180** | 🩺 Millie's niche data frozen since 7 Sep — `derive_niches` times out on Anthropic after 3.5h, nightly | 🟡 S2 | S-M | n/a (launchd job) | ✅ **CLOSED 2026-09-10** — root cause was the Mac ASLEEP at 04:30, not the work. Data current, job resumable, tile fixed (`e7c18d9`). One thing left for Andy: a scheduled wake. |
| **#181** | 🅿️ **SPRINT 5** · Events catalog hourly on paper, four-hourly in fact — 9 of 13 intervals in the down band, 14/14 runs green | 🔵 S3 | S | n/a (GH Action) | ⛔ blocked: GitHub PAT `actions:write` (Andy) |
| **#182** | 🅿️ **SPRINT 5** · Five days of recordings invisible to Millie — `zoom_weekly` runs on time but skips videos, no `GROUPOS_PAT` | 🟡 S2 | S | n/a (weekly job) | ⛔ blocked: GroupOS PAT (Andy) |
| **#183** | 🛍️ Storefront reshuffles its tiles 10-15s after load and the PINNED band disappears (Andy 2026-09-09) | ⚪ S4 | S | n/a (web — Render, no staging tier) | ✅ **CLOSED 2026-09-10** — cause was NOT the health checks: pins load from localStorage after mount. `pinLayout()`, 6 tests, live `588ef08`. |
| **#189** | 🃏 The persona builder fails intermittently and cannot say why — 19 of 31 on 2026-09-09, reported only as "no valid JSON" | 🟡 S2 | S | n/a (launchd job) | ✅ **CLOSED 2026-09-10** — cause found and fixed: the answer parser broke on a stray brace after the JSON. 40/40 built, 0 failed. |
| **#190** | 🧪 The nightly eval is at **9.5% FAIL** against Andy's **<1%** bar — 21 of 220 on 2026-09-09 | 🔴 S1 | M | n/a (report) | ✅ **CLOSED 2026-09-11** — a fresh 100-question exam of real member asks (Andy: "do fresh 100"), fired at prod: **14% judged, 7% reproducing** after every failure was re-fired by hand. The nightly bank was overstating by ~2× (4 of 13 sticky fails were stale truths; 5 truths repaired). Failures named by mechanism → #201 #202 #203 #204 #205 #206. Triage `OLIVIA_EXAM_190_TRIAGE.md` |
| **#204** | 🔐 An exact revenue figure (£14.5M) reached a member in Millie's own voice — quotable, but only attributed with its link and paired with the band | 🔴 S1 | S | — | ✅ **CLOSED 2026-09-11 (overnight)** — SQL live on prod, graph staged for the promote; proof in the 🌙 OVERNIGHT block above. 4/4 probes |
| **#201** | 🕳️ She denies what we hold because the tool never returns the column — `view_count` absent from `video_search_v2`, **Brand Name** in no gated function at all | 🔴 S1 | M | — | ✅ **CLOSED 2026-09-11 (overnight)** — SQL live on prod, graph staged for the promote; proof in the 🌙 OVERNIGHT block above. 8/8 probes |
| **#203** | 🔀 One lane denies while another holds it — "MDS 9" is 4 events + a video set; "Trybe" is spelled "Tribe" in the transcript | 🟡 S2 | M | — | ✅ **CLOSED 2026-09-11 (overnight)** — SQL live on prod, graph staged for the promote; proof in the 🌙 OVERNIGHT block above. 4/4 probes |
| **#202** | 💬 "How do I join the supplements channel" ran the recommender with no query and offered TikTok instead | 🟡 S2 | S | — | ✅ **CLOSED 2026-09-11 (overnight)** — SQL live on prod, graph staged for the promote; proof in the 🌙 OVERNIGHT block above. 5/5 probes |
| **#205** | ✂️ A post ranked 4th is cut at 500 chars, so the fact at char 658 never reaches the model (the Advisory Council deadline) | 🟡 S2 | S | — | 📝 filed 2026-09-11 from #190's sticky-13 triage |
| **#206** | 📅 Coverage stated as a feeling — "the further back the thinner" instead of 4,283 posts, 2021-08-17 → 2026-09-10, 5 before 2025 | 🔵 S3 | XS | ✅ staged | ✅ **CLOSED 2026-09-11 (overnight)** — SQL live on prod, graph staged for the promote; proof in the 🌙 OVERNIGHT block above. 4/4 probes |
| **#210** | 🅿️ **SPRINT 5** · 🪪 She refuses a member their OWN job title — the never-share rule is not scoped to the subject, and the dossier lane volunteers the same fact | 🔵 S3 | XS | — | 📝 filed 2026-09-11 from the nightly (Q2096), confirmed live on prod `b31eadbb` 14:41Z: plan hit the application lane, the item says "Title: Head of Tech & Automation", the answer refused |
| **#207** | 🧭 An ability question about Millie herself ("are you able to do daily reminders?") answered by improvising a capability | 🟡 S2 | XS | ✅ staged | ✅ **CLOSED 2026-09-11 (overnight)** — routes to the curated list (#79), which now states what she cannot do; 4/4 probes |
| **#208** | 🎙️ "What did the speaker say about X" denied — the videos lane never searched the TRANSCRIPTS, and the word was spelled differently there | 🟡 S2 | S | ✅ staged | ✅ **CLOSED 2026-09-11 (overnight)** — transcript passages + spelling variants; 4/4 probes |
| **#191** | 🧪 The nightly eval is DEAD since this morning — #105's webhook secret 403s all 220 posts, no report for 2026-09-10 | 🔴 S1 | XS | n/a (local job) | ✅ **CLOSED 2026-09-10** — 25/25 posts `200` on the live webhook; 4 scripts fixed, a refused door now aborts loudly |
| **#123** | 🗺️ `event_lookup` never reaches the events catalog — every `event_*` call is prefix-routed to the Summit schedule endpoint | 🟡 S2 | M | ✅ proven `9d91109e` | ✅ **LIVE `b4db92d0`** (promoted 2026-09-10 17:56Z by Andy) — prod probe 68019, gate 346 EXIT 0 |
| **#188** | 🩺 One tile, two writers — "Member profiles ← Airtable sync" reported the events catalog's staleness under the member-profiles name | ⚪ S4 | XS | n/a (app code) | ✅ **CLOSED 2026-09-10** — the worse half now names its writer; 5 tests, live `2208d78`. |
| **#61** | 🏗️ Schema audit: tables with no declared connections *(research + orphan audit + COMMENTs SHIPPED 2026-08-12; FK-constraint follow-up filed)* | 🔴 S1 | M | n/a (SQL) | ✅ audit shipped |
| **#64** | 🏗️ Runtime inventory: where every job runs — failure mode is silence | 🟡 S2 | M | — | — 🟡 **INVENTORY DONE 2026-09-10 → `RUNTIME_INVENTORY.md`**, plists copied to `ops/launchd/`. **Headline: 7 of 9 jobs are scheduled 02:15–05:40, inside the window the laptop spends asleep** — that one fact produced #180. Five jobs have no heartbeat at all. `mds-scorecard-tools` is not a git repo. The moves that remain need Andy. |
| **#158** | 🏗️ Foreign keys on what we own + nightly orphan check *(the #61 follow-up; external architecture review 2026-09-02)* | 🔵 S3 | M | n/a (SQL) | — |
| **#66** | Forms warehouse: 4 remaining gaps (validation · refresh · units · lag) | 🔵 S3 | M | — | — |
| **#100** | 🔑 Identity aliases — one member, all their known emails | 🔴 S1 | M | n/a (SQL) | ✅ **CLOSED 2026-08-20** — 5,763 aliases, resolver live, 12/12 verify, gate 0 |
| **#101** | 🎬 Video transcripts + real access gating | 🔴 S1 | L | n/a (SQL+data) | ✅ **CLOSED 2026-08-20** — 2,730 chunks, video_access live, gate 263/0 · NEXT: 2025 batch |
| **#162** | 🎬 Transcripts for the 33 videos published 25 Aug–4 Sep (AI Mastermind · AI Scaling Live · Summit day 2) — AssemblyAI from the S3 links the dev opened 2026-09-04 | 🔴 S1 | S | n/a (data) | ✅ **CLOSED 2026-09-04** — 33/33 transcribed ($2.62), 697 chunks, 33 summaries, 5 new restricted videos → 44 grants each, 2026 = 212/212, E2E quote proven, gate 313/0 |
| **#72** | 🚦 LOAD TEST — 100 concurrent probes | ⚪ **RETIRED 2026-09-10** | M | — | ❌ **Andy: "I think this is an old ticket. I don't want to do a 100-probe."** Filed for a demo two weeks out; that demo was the August Summit and it has passed. The measurement half survives as **#187**. |
| **#187** | 🅿️ **SPRINT 5** · ⏱️ Millie has never recorded how long a turn takes — `latency_ms` is NULL on all 13,309 rows | 🔵 S3 | S | — | — ✅ **CLOSED 2026-09-10** — prod `22d81380`. First turn ever timed: **23,838 ms**. |
| **#73** | Connect the useful forms to Olivia — she reads 5 of 161 | 🔵 S3 | M | — | — |
| **#68** | 🔑 Canonical question dictionary + mapping at scale | 🔵 S3 | L | — | — |
| **#18** | How-MDS-works answers | 🟡 S2 | M | ✅ first slice proven `6581548e` | ✅ **first slice LIVE** `f3850dd7` (prod probes: FAQ cited; no-doc honest) — open for more docs |
| **#94** | 🧠 Expertise Ledger v2 — the living skill sheet (Eugene #2 finale) | 🔴 S1 | M | ✅ probed | ✅ **CLOSED 2026-08-19** — 51 topics live, verify 9/9, gate 0 |
| **#95** | Equalizer for the members lane — BOTH advice lanes wired | 🔴 S1 | S | ✅ probed ×2 | ✅ **CLOSED 2026-08-19** — repeat asks 8/8→0/8 shared, gate 0 |
| **#96** | Attendee-name disclosure — Eugene's ≤10-names cap | 🔴 S1 | S | ✅ E2E probed | ✅ **CLOSED 2026-08-20** — cap 10 in code, attendee-gated, gate 0 |
| **#97** | Brokered intros — "message the person she recommends", consent-first | 🔴 S1 | M | ✅ route matrix · staging taps/tool · fix-wave re-reviews | ✅ **CLOSED — PROMOTED 2026-08-22 by Andy (`7e4be40a`); prod E2E tap proven (exec 96653).** Verified live 2026-09-09: the 7 intro nodes are on prod `15649d68`. Open behind it is the wide intros ANNOUNCEMENT, which waits on #105 — not a promote. |
| **#98** | Who-to-meet gates on registrations ledger (smoke Q37) | 🔴 S1 | S | ✅ E2E re-probed | ✅ **CLOSED 2026-08-20** — ledger authority both branches |
| **#99** | "Show me the rest" for who-to-meet (smoke Q49) | 🟡 S2 | S | ✅ E2E via canary | ✅ **CLOSED 2026-08-20** — continuation note in-tool, fresh re-call proven |
| **#102** | 🎬 Video recommendation ranking — time decay · speaker weight · event bonus (Andy/Eugene Slack 2026-08-21) | 🔵 S3 | M | — | ⏸ AFTER the big smoke test |
| **#112** | 🔗 Offer→answer binding | 🔴 S1 | S | ✅ exact failing sequence returns BOTH summaries | ✅ **CLOSED 2026-08-22** — the #80 binding existed; its ACCEPT_RE end-anchor made "yes booth" miss. Fix: affirmative may carry a quantifier/typo (both·booth·all·either·that one) while a topic word still routes normally; binding now covers EVERY offered video, not just the last. Prod `e175c5a3`, gate 0 |
| **#104** | Adjacent-turn topic lag | 🔴 S1 | S-M | ✅ **VERIFIED: rerun of all 3 original fail-chains with recreated adjacency = 3/3 on-topic PASS** | ✅ **SHIPPED 2026-08-22** — it rode the Millie promote that same day, which the #97 block records at line 2399 ("15 nodes incl. the Millie/#104 set that rode along"). Verified live 2026-09-09: `off_topic` appears 22 times on prod `15649d68`. The "⛔ rides the Millie promote" note was stale by 18 days. **Root cause: FC caught all 3, Gate Verdict pass-postfilter neutralized the catch (topic-mismatch is not a fact-claim); fix = off_topic field in FC rubric + non-filterable in Gate Verdict (regenerate, cap 2). Probe: exact failing sequence now on-topic, off_topic field live in FC output, gate 263/exit 0. Bonus same session: load_speakers.py --rescan (guest-becomes-member promotion in place, 27 checked/0 due)** |
| **#105** | 🔐 Verify Meta's webhook signature (`X-Hub-Signature-256`) on every inbound — filed from #97's final review (Andy OK 2026-08-22) | 🔴 S1 | S | n/a (relay — Render) | ✅ **ENFORCING 2026-09-10 04:47Z** — live at the relay (`d5d6bff`). 3 genuine Meta deliveries verified `ok`, then the switch was flipped; a forged post now gets 403 and is never forwarded. |
| **#106** | 🙈 Staff / non-member records must never surface in member-facing lists (event_who names, who-to-meet, intro picker) — Andy 2026-08-22: "make sure I'm not searchable" | 🟡 S2 | S | SQL-verified exposure map | ✅ **LIVE 2026-08-24** (SQL, prod-shared) — 5 `#106` checks in the leak gate pass: `member_card`, `member_card_v2`, `expertise_search`, `member_match_v2`, finder |
| **#107** | 🗣️ Millie-only self-name (Format Reply PS still says Olivia) + who-to-meet ends with "connect you with one of them?" Yes/No buttons → Yes = intro picker (Andy 2026-08-22: "Millie and only Millie — official name"; "ask if he would like to connect… if yes provide a list") | 🔴 S1 | S-M | — | ✅ **PROMOTED 2026-08-22 ~05:24Z (Andy) — prod `8f48fdb8`**: Millie PS (prepended when button-eligible) · who-to-meet ends with the exact offer + Yes/No buttons (96779) · Yes → member_intro, no plan replay (review caught the 500-char-trim defeat → `last_olivia_intro_offer` flag, proven 96864) · non-attendee no offer (96787) · gate 267 EXIT 0 |
| **#109** | 📨 Requester-side intro notices must be TEMPLATES (accept / decline / 7-day lapse) — free-form text dies outside the 24h window (Meta 131047); found 2026-08-22 when Andy questioned the lapse promise | 🔴 S1 | S-M | n/a (route — no staging tier) | ✅ **SHIPPED 2026-09-01** `cae87c1` — `src/lib/intro-notices.ts` + template-first route with free-form fallback; 15 unit tests incl. a standing guard that no requester path can be text, 144/144 on main; live sweep probe expired=1 failed=0, lapse notice accepted by Meta (wamid …9B34A86B928F28CF3C). ⚠️ closed-window delivery not yet observed (probe requester's window was open) · lapsed template is MARKETING, so 131049 can still cap it |
| **#110** | 🧾 Intro-tap turns are not saved to conversation history — `Save Conversation` on the intro-tap path errors on a `$('Resolve Member')` reference (swallowed by onError); SQL-proven zero rows for tap turns; no member impact, no effect on no-replay flag | 🔵 S3 | S | SQL + exec 97071 | ⏸ next session |
| **#111** | 🎯 Who-to-meet results swing with the model's free-text topic query (Aaron: q="Retail, PPC, Amazon Ads, Sourcing, AI Automation" → 7 matches; q="Amazon PPC, Retail & Wholesale, Credit Cards & Travel Hacks, AI & Automation, Sourcing & Suppliers" → 1) — matcher should use the asker's own ledger topics deterministically + alias-normalize free text (execs 97152 vs 97286, same day) | 🟡 S2 | S-M | exec diff | ⏸ next session (or fold into #102) 🔎 **2026-09-10:** the lane it patches (`member_match`) survives #108 — retiring it is an explicit phase-1 non-goal — so this is **not** thrown away today. #116 (size L, unplanned) does retire it. Worth doing only if it hurts members now. |
| **#108** | 👥 The Finder — one composable filter tool, every data layer (Belen's reseller question: Millie named brand owners, missed the 3 real resellers) | 🟡 S2 | M | ✅ proven (gate 292 EXIT 0, 26 finder checks) | ✅ **BUILT 2026-08-23 — READY FOR PROMOTE (Andy)** · row re-verified against live 2026-09-09 and it is accurate: prod `15649d68` has no Finder — `member_finder`, `find_members` and the node name all return zero across the 92 nodes, and the only "finder" strings on prod are two code comments. — 17 Summit resellers / 122 community, reasons per person, disclosure engine R1-R10 holding — full block below |
| **#113** | 🔄 Summit event refresh — the whole event (activities, sessions, rooms, access, rosters) reloads from a GroupOS export, removals included | 🔴 S1 | M | ✅ LOADED 2026-08-23 from the 09:52Z scan: activities 50→86 · access edges 180→227 · grants 183→698 · full descriptions; idempotent; self-test 7/8 | ✅ CLOSED — live lane serves the new day one |
| **#114** | 🕐 "Today at the Summit" must resolve in the VENUE's zone, not US Eastern (Ian Sells, Singapore, got Saturday on his Sunday) | 🔴 S1 | S | ✅ route live (`9d0ec41`) · seed PROMOTED `bbd597b7` 2026-08-23 02:49 ET · prod probe Sunday/Monday + full day | ✅ CLOSED — Andy tested on WhatsApp 2026-08-23 (ET afternoon, Singapore already on the next day): correct |
| **#115** | 🌍 Country/state normalised at derive time (`country_fold` in `derive_member_attributes`) + 4 WA-layer "resellers" with non-current AT status + 8 corrupt `OEM…'Wholesale…` business-model rows — data hygiene found building #108 | 🔵 S3 | S | — | ⏸ next session ✅ **CLOSED 2026-09-10** — `IS` folded to Iceland, so 5 Israeli members were counted as Icelandic; fixed. 8 corrupt rows repaired at derive time, 0 left. The 38 non-current resellers were already excluded by the gate. |
| **#116** | 🔎 Finder phase 2 (content + video: `return: content` / `videos`, who-leaves as author/speaker constraint, speaker/year/category filters, `speaker_of`) + phase 3 (events/partners/forms; retire `member_match` / `member_count` / the schedule matcher) — spec §6 | 🔵 S3 | L | — | ⏸ own plan |
| **#117** | 🧹 `olivia_selftest.py --cleanup` doesn't delete probe message rows, only `olivia_seen` — found during #108 staging probes | ⚪ S4 | S | — | ⏸ next session ✅ **CLOSED 2026-09-10** — cause was `+` in a URL being a space, so the bound matched nothing; **5,104 probe turns had piled up**. Exact rule now, proven on a real-vs-probe pair. Purging the 5,104 backlog waits on Andy. |
| **#118** | 🗺️ `event_who`'s `op=people` returns a ranked/personalized subset (#99 behavior), not a flat roster, for a plain "who is coming" ask — found during #108 staging probes | 🟡 S2 | S | — | ⏸ next session 🔎 **2026-09-10:** same as #111 — `event_who` retirement is a phase-1 **non-goal**, so this is live work today, and #116 eventually supersedes it. ⚠️ Note it moves the **name-disclosure** rules Andy+Eugene set in #96, so it is not a solo change. |
| **#119** | 🧪 Bank B — a second eval bank for everything built since the 100-question bank was frozen (2026-08-16): schedule + venue-day, Summit registration & who-to-meet, intros, 2025-26 transcripts/quotes, speakers, offer binding, the finder — ORGANIC questions only (real member asks from `olivia_messages` since 08-16), `expect` from the tickets' ACs/rulings, sized by the questions not padded; runner gets `--bank`; first staging run scored against the tickets' truth | 🔵 S3 | M | ticket ACs + `olivia_question_labels` | 🔨 building 2026-08-23 (Andy: "file #119, do it while bank A runs") |
| **#92** | Event selection for a multi-event world — she must pick the RIGHT schedule | 🔵 S3 | S | — | ⏸ waits for event #2's export |
| **#67** | Cohort + trend comparison, per field (panel vs cross-section) | 🔵 S3 | M | — | — |
| **#74** | Identity: 51% of form submissions belong to nobody | 🔵 S3 | M | — | — 🔎 **RE-VERIFIED 2026-09-10, and the premise is mostly a category error.** 58.2% orphaned now (8,011 of 13,759), not 51% — but the 100%-orphan forms are *MDS Inspire 2024/2025*, *Best in Show* and raw public form ids, filled by **non-members**, and *Start your MDS journey* is the application form, 65% orphan **by definition**. Matching them up does not work either: only **108 of 8,011** are claimable via the alias resolver and **76 of those matches are ambiguous** (one email, several members). Re-scope before working. |
| **#17** | Auto-refresh videos and partners | 🔵 S3 | M | — | — |
| **#71** | "Virtual event" vs "call" vs "recording" — two contradicting "latest" answers | 🟡 S2 | M | — | — 🔎 **RE-VERIFIED 2026-09-10, still real.** Two silent probes, same minute: *"latest MDS virtual event"* → **MDS 9 Call, 14 Aug 2026** (events catalog); *"most recent MDS call"* → **a recording published 2 Sep 2026** (video library). Two sources, two "latest", three weeks apart, both plausible to a member. **Needs Andy's ruling on what "call" means across the two catalogs** before it can be fixed. |
| **#48** | AT roster write-back | ⚪ S4 | S-M | — | — |
| **#19** | Privacy: share, keep, delete | ⚪ S4 | M | — | — |
| **#35** | New data source — DOCUMENTS (GroupOS) | ⚪ S4 | M | — | — |
| **#36** | New data source — CIRCLEBACK | ⚪ S4 | L | — | — |
| **#32** | What Olivia costs | 🔥 — | S | — | — |
| **#14** | Conversational, not robotic | 🔥 — | M | — | — |
| **#34** | Finalize the QA doc set | 🏁 — | M | — | — |
| **#125** | 🚫 "Not currently active" is sent to ACTIVE members whose number simply isn't linked (Shyam Murali, live at the Summit launch) | 🔴 S1 | S | ✅ proven `01c8670d` — execs 110321/110322/110324 | ✅ **PROMOTED 2026-08-25** `c20c1811` — prod execs **110345** (unlinked, new copy) + **110346** (inactive, unchanged); gate 306 EXIT 0; 53 false claims → 0 |
| **#147** | 🔀 "Is this member registered?" answered twice by two sources that disagree (agenda says yes, who-to-meet says no) | 🔴 S1 | M | n/a (SQL) | ✅ **LIVE 2026-09-10** — `registration_status_v2` is the one authority (roster `has_ticket` gates, GroupOS `is_attending` drives the agenda, per Andy's ruling), `event_who` resolves on place as well as title, 13 + 5 contract checks green, gate 346 EXIT 0. ⏸ one lane left: the web schedule route (`mds-digest-web`, no staging tier — needs his go) |
| **#146** | 🔇 A member who hides their WhatsApp number is invisible — silent drop, no answer, no error (Danson Hui) | 🔴 S1 | M | ✅ built + probed | ✅ **PROMOTED 2026-08-25** `64995b68` — Danson live. Remainders open: silent-drop alarm · hidden-number history keyed by the opaque id · ~~refusal path bypasses the SELFTEST silent gate~~ **fixed under #125** |
| **#145** | 🧪 No-regression re-run of the 319 already-passing bank C questions — the last gate before the promote | 🔴 S1 | S | ✅ 319 graded, 8 regressions fixed | ✅ **CLOSED + PROMOTED 2026-08-25** — 311/319 hold (97.5%); links 654→808, dead links 5→0, dates 641→862, route changes 0; prod `8bb0827d` |
| **#148** | 🧊 The WA members mirror never reconciles — 12 rows Airtable stopped returning are frozen forever (oldest 2026-08-05), no freshness signal | 🔵 S3 | S | — | ⏸ filed 2026-08-25 ✅ **CLOSED 2026-09-10** — `stale_since` + `mark_stale_members()` (guarded), nightly job, `prod_pulse` reports it. **The 11 rows CAME BACK on their own** — absence is intermittent, not permanent. |
| **#126** | 🧾 WA mirror leaves `at_member_id` NULL although the AT record carries `source_member_id` | 🟡 S3 | XS | n/a (audit) | ✅ **CLOSED 2026-08-25 — NOT REPRODUCIBLE**: field map proven correct against mirror exec 110330; all 57/671 NULLs are genuinely unmatched. Audit found 11 matched members with no `AT Database Status` (Airtable-side, Andy/ops) and the stale-row gap, filed as #148 |
| **#149** | 🗣️ Two real answers were wrong in shape — a live event called finished, a yes/no answered with machinery | 🔴 S1 | M | ✅ staging turns 52883/52885 | ✅ **PROMOTED 2026-08-26** `7abb9fc9` (rules+clamp) · route `eventPhase` pushed `102bf14` (Render deploys on push) |
| **#150** | 🔒 Summit videos restricted with ZERO `video_access` rows — nobody could be entitled | 🔴 S1 | S | n/a (SQL) | ✅ **CLOSED 2026-08-26** (Andy: attendees + staff) — 1,225 grants (7×175), rerunnable `scripts/sql/150_summit_video_grants.sql`; `is_restricted` now means restricted FOR the asker (video_search + v2); staging turn 52889 answers Tamar content; gate 306 EXIT 0 |
| **#151** | 🎯 Video answers ignore the member — Inspire volunteered, no count, no tailoring, follow-up fled the list + dangling old-event links (Andy, prod 52891/52893/52935/52941/52951) | 🔴 S1 | S | ✅ probe wave 8/8 · orphan-strip unit 6/6 | ✅ **PROMOTED 2026-08-26** `06df948a` — prod turn 52959: 1 link, Denver gone; gate 306 EXIT 0 |
| **#152** | ⏱️ `refresh_entity_dossiers` statement-timeout — `zoom_weekly` heartbeat error, last success 2026-08-07; video chain exits 1 every run (found by scorecard-df) | 🟡 S2 | S | — | ⏸ filed 2026-08-28 ✅ **CLOSED 2026-09-02, row was stale — verified live 2026-09-10:** `refresh_entity_dossiers` carries `statement_timeout=900s` in `proconfig`, and the `entity_dossiers` heartbeat is `ok` on tonight's full nightly run. |
| **#154** | 🔗 People she names carry NO link — `member_match_v2` / `expertise_search` return no url column at all | 🔴 S1 | S-M | ✅ proven `e55a45c6` — 4/4 and 10/10 linked; gate 312/0 | ✅ **LIVE 2026-09-02** prod `d40a837d` (seed) + Render `8f368b3` (finder) — prod probe 5/5 linked, live finder 5/5 linked; 718/741 actives resolve |
| **#155** | 💬 A chat quote carries its own message link, and "what should I know" is not a capability tour | 🟡 S2 | M | — | — |
| **#153** | 🎯 Intent probes: ranking had no recency, stated facts refused (3/4 screenshot probes failed) | 🔴 S1 | S | ✅ **3/3 FIXED + PROVEN** `0faa9be5` — decay live (SQL), seed rule staged; gate 306 EXIT 0 | ✅ **PROMOTED 2026-08-26** `15ff4978` — verified 2026-08-28: prod/staging graphs identical (only webhook path differs), gate 306 PASS · 0 FAIL · EXIT 0; re-embed of 7 still awaits Andy |
| **#156** | 💸 Sonnet 5 vs GPT-5.6 Terra on the locked 100 bank — price + quality, dual judge, prod untouched (bench harness, no n8n) | 🟡 S2 | S | — (harvest run only, no edits) | ✅ **DELIVERED 2026-09-02** `OLIVIA_MODEL_COMPARE_2026-09-02.md` — Sonnet 5.4% / $0.0211 · Terra-medium 3.3% / $0.0310 · Terra-none 7.6% / $0.0237 (Sonnet judge); nothing promoted |
| **#157** | 🧑‍⚖️ Review the Sonnet 5 vs GPT-5.6 Terra bench (#156) — Andy's vendor call: stay on Claude, port to OpenAI, or re-test | 🔵 S3 | S | — (reading + decision) | — |
| **#159** | 🕳️ Partners and events go dark in meaning search — 75 partners without a vector (35% of reviews, 48% of claims), the weekly delta missed 28 of 142 changed partners (Prosperlytics 5.0★ never shown for "bookkeeping") | 🔴 S1 | S | n/a (data + scripts) | ✅ **CLOSED 2026-09-03** — 75 partners + 36 events re-embedded (dark 0/0), nightly `embed_catalogs` + weekly re-embed, gate +2 checks (313/0), `partner_lookup_v2("bookkeeping accounting")` → Prosperlytics #1 |
| **#160** | 🌐 Partner web profiles — crawl every partner site (services · pricing · people · proof) so Millie knows what a partner does and who runs it; founder ↔ partner link (Mudit Jain → Prosperlytics) | 🟡 S2 | M | ✅ staging `cefe0133` — probes: cost + who-runs-it answered from the site | ✅ **PROMOTED 2026-09-04 00:17Z (Andy: "promote") — prod `30fd7e6f`**, gate green in-promote, prod probe exec 131383: Shea's question → Prosperlytics 5.0★ first with site facts + pricing; 506 profiles, 1,173 people, 52 speakers linked, web text in the partner vectors |
| **#161** | 🎴 MDS Personas — staff library of members (library v2 · character sheet · cohort) on the persona + 51-stat ledger, Claude Design handoffs v1 + v2 | 🟡 S2 | L | ✅ built + reviewed LOCALLY | ✅ **SHIPPED 2026-09-04 (Andy: "lets promote personas")** — merged to `main` in both repos, Render deploy `e212bcf` — 3 screens live on `localhost:3000/personas`, 7 read-only RPCs, 639/760 portraits in Storage, 758/758 blurbs, gate 323/0, 359 tests, `npm run build` exit 0; 13 tasks + 5 feedback rounds + final review wave on `personas-20260904` (both repos); merge to main = Render deploy |
| **#163** | 🔢 Personas scoring review — what each number means (level · stat value · today/peak · rank), cohort floor 60 hides the tail, "peak floor applied", asks = gives overlap. Andy 2026-09-04: "the worst performer in each category never goes below 60" | 🔵 S3 | M | filed | 📝 filed 2026-09-04 (Andy: "file it, we will check these things later, the whole scoring system") — after #161 ships |
| **#164** | 🎨 Admin storefront + seven self-contained tools — split the shared nav bar into a launcher plus per-tool navigation, merge the three WhatsApp pages into one tabbed tool (design handoff `~/Downloads/design_handoff_mds_admin/`) | 🟡 S2 | L | n/a (web — Render, no staging tier) | ✅ **SHIPPED TO PROD 2026-09-07 00:19** — `mds-digest-web` `main` = `cfb3350`, Render live 00:22; 7 admin routes answer, `/dashboard` unaffected, all 12 retired URLs redirect; 91 commits, 200 files, 882 tests, `next build` clean. Open items (not blocking) in that repo's `docs/ADMIN_OPEN_ITEMS.md` |
| **#165** | 🃏 The Personas sheet does not explain itself — FOCUS / GIVES / ASKS carry no source, "In their words" is a model paraphrase, 11 silent categories hide in a grey footer, "Top 6" reads as a filter and is an expand control | 🟡 S2 | M | n/a (web — Render, no staging tier) | ✅ **SHIPPED — merged and live.** Verified live 2026-09-09: `mds-digest-web` main carries `18bac76` ("#165 self-reported vs observed tag on every persona line") and `https://digest.mds.co/api/version` returns `15700f2e`, a later commit on the same main. The "awaiting Andy's look before merge" note was stale. What shipped — all 18 categories as rows, provenance on every block (`docs/PERSONAS_FIELD_PROVENANCE.md`), "In their words" gone, "Top 6" → "Open top 6"; found 1,016 detail stats across 503 members that were unreachable; Ryan Pace's Member 360 correctly empty (Stripe sync lag); 892 tests, `next build` exit 0; open call: bar marker at 70 vs "60 is strong" copy |
| **#166** | 🔲 Personas and Digest have no tool switcher — every other tool got the header grid button in #164; these two never render `ToolHeader` | 🟡 S2 | S | n/a (web — Render, no staging tier) | ✅ **SHIPPED TO PROD 2026-09-07 (Andy: "166 is good, we can promote it")** — merge `b91f2a4`, confirmed live via `/api/version`; switcher in the Personas top bar and both Digest headers, `← All tools` link retired, 1–7 jumps with no storefront round trip; fixed on the way: dismiss layer shrunk to header height under `backdrop-filter`; 920 tests, `next build` exit 0; open call: two grid icons (switcher + Browse) in the Personas header |
| **#167** | 🔟 Team pulse survey — the rating popup where every number but 10 runs away from your cursor; design pack approved on sight, logic (when to ask, where answers land) agreed | 🟡 S2 | M | n/a (web — Render, no staging tier) | ✅ **SHIPPED TO PROD 2026-09-07 (Andy: "if u r sure, lets promote")** — merge `41da9e7`, confirmed live via `/api/version` 02:14 local; once per person ever (wave `survey_key`), from the 2nd login after `SURVEY_STARTED_AT` 2026-09-07, card centred (`Popup align="center"`, opt-in), `?pulse=1` for `SURVEY_TESTER_EMAILS` only (default Andy), `is_test` rows excluded everywhere, Team pulse results popup on the storefront, Slack `#automation-tests`; 1047 tests, 22/22 mutations killed, e2e script 32/32, `next build` exit 0; table holds 6 rows, all Andy's tests. **Roster fix same night (Andy: "no, its only people who r using now, but we have team of 30"): M = `member_attributes.membership_status = 'Staff'` (30 rows), not the 17 `@mds.co` portal logins — merge `491a968`, live 02:24 local, storefront reads 0 OF 30.** **Second-day rule (Andy: "go"): merge `e2d933d`, live 12:42 local — asked on the 2nd distinct UTC day the person opens `/admin` since launch, visits recorded in new `digest.admin_survey_visits` (RLS on, service_role only), `member_sessions` no longer read; 1068 tests, e2e 45/45, mutation 4/4 classes killed** |
| **#168** | 💬 Millie test chat back in the admin at a new address — `/admin/olivia/test` was retired by #164; component + API survived, only the page died | 🟡 S2 | S | n/a (web — Render, no staging tier) | ✅ **SHIPPED TO PROD 2026-09-07 13:20 local** — merge `48851e7`, confirmed via `/api/version`; `/admin/millie/chat` as a Chat tab in the Millie tool, `/admin/olivia/test` 307 → the chat (checked on prod), anon 307, API 403 anon / 200 staff; 1068 tests, `next build` exit 0; not restyled to the kit (legacy Tailwind look kept) |
| **#169** | 🚪 Millie web front door + Public mode — a real chat for staff (answer in the same request, own conversation table, real asker) and a Public mode whose answers may leave MDS: names only from public sources, notes on where each part came from | 🟡 S2 | L | staging first (`olivia-web` entry), gate +9 checks (323 → 332) | ✅ **SHIPPED 2026-09-08 (Andy: "finish the rest and report")** — workflow in three promotes: `f5e9ce5d` 02:16Z (door + Public Gate, one graph with #174 #175 #143 #139 #141 #142 #144) · `49d4a931` 03:14Z (partner rows back a name from the partner's own site only) · **`69665fc2` 04:20Z (hardened gate: unicode name boundaries, both-sides normalisation, variant + first-name masking, closed links stripped, org rows out of the name index, gate proves the Public path is wired)**; **web `mds-digest-web` main `1987a2e` live on Render 04:23:47Z** (Ask Millie storefront tool `/admin/ask-millie`; old chat URLs forward; polling chat deleted) + `1aad368` (picker stays put, 16px text, Andy's live review); prod probes: secret-less 403, test lane 14 s, Public lane 40.6 s with 3 names → roles + 1 FB link removed; gate 332/332; 41 module tests, 1,129 web tests · close block below |
| **#170** | 🧠 Millie web chat — long thread memory + many chats: running Haiku summary per thread, a `web_thread_search` tool for exact recall, sidebar of past chats with New chat | 🟡 S2 | M | staging first | 📝 filed 2026-09-07 (Andy: "File it, will do") — after #169 |
| **#171** | 📣 Public answer from the Facebook tool — for a post without an answer, generate a public-safe reply in a popup (Andy's design pending) | 🟡 S2 | M | n/a (web) + the #169 door | ✅ **SHIPPED 2026-09-08 — merge `50ff14b`** — "mark answered" wired to `POST /api/admin/fb-post` (optimistic + read-back); new Draft-an-answer modal on every post calls the #169 Public door with the WHOLE post text (new `GET /api/admin/fb-post-text` — `snippet` caps at 240 of up to 669 chars); Copy / Mark answered / Regenerate / Open in Ask Millie; greeting added client-side from the author's first name (never sent to the door); later fixes: no `[link removed]` litter, inline bullets → real lines, no standalone link list, a first-sentence name counts as a greeting (`22c8559`) |
| **#172** | 🔓 Team chat — everything-access mode for staff (exact revenue, contact details, Stripe/billing), now defined as a Team RESEARCH runtime beside Millie: SQL + catalog + semantic search, no gates, asker logged | 🔴 S1 | L | — | 📐 **DESIGNED + PLANNED 2026-09-10** — `TEAM_RESEARCH_172_DESIGN.md` + `_IMPLEMENTATION_PLAN.md` (`bc53a23`); **NEXT** once Andy's five Day-0 items land (design §9) |
| **#173** | 📡 Ask Millie — live source trail + token streaming: the design's "Reading WhatsApp channels · 38 chats ✓" steps and streamed answer text on one held request; needs a progress hook in the answer loop | 🟡 S2 | M | staging first | 📝 filed 2026-09-07 from the design pack README ("Streaming, not polling") — #169 ships an honest two-event stream (started · answer) first |
| **#174** | 🎯 A named item from her own list is a drill-down, not a new search — "Tell me more about Alex Chiru video" after a four-video list re-planned as a fresh speaker search (Andy's case 1, prod turn 65490 / exec 137515) | 🔴 S1 | S | ✅ **proven on staging `2d875cb3`** — Andy's exact chain exec 137664 `offer_bind.mode:'drilldown'`, speaker-named 137633, title-named 137645, "yes" 137637 unchanged, gate EXIT 0 | ✅ **LIVE `49d4a931`** (promoted 02:16Z as `f5e9ce5d`, one graph with #169; `49d4a931` = + #169 fix round 4) |
| **#175** | 🔗 The gate's link repair pins a URL to the wrong row — a bare, untitled link before the closing question on every video answer (Andy's case 1, execs 137508 / 137515) | 🟡 S2 | S | ✅ **proven on staging `2d875cb3`** — 14/14 unit on the live bytes, replay of execs 137508/137515 appends 0 (was 1 · 2), 0 appended links in 33 probe turns; lap 2 (the #1c event repair) proven on `c28fb532` | ✅ **LIVE `49d4a931`** (02:16Z, one graph) |
| **#143** | 🔁 A follow-up binds to the wrong thing, or loses the thread — four guards: no echo-bind on a new question, a bare ordinal is a drill-down, a bold number is never an offer, a yes to nothing asks what they want; her own-words report offer reaches the ticket lane (bank C 6095/6349 + tonight's probes) | 🟡 S2 | S | ✅ **proven on staging `eb99c336`** — execs 137713 · 137716 · 137720 · 137739, rows 65655 · 65661; 45/45 unit; gate EXIT 0 | ✅ **LIVE `49d4a931`** (02:16Z, one graph) |
| **#139** | 🤝 A named partner ships with its recorded offer and its page (bank C 6075: five agencies, no deal, no link) — `Gate Verdict` pairs `partner_url` rows by name; lap 2: a partner named in the member's own question is never appended | 🔴 S1 | S | ✅ **proven on staging `c28fb532`** — execs 137957 · 138004 (rows 65837 · 65879: seven partners, seven deals, seven pages); 33/33 unit; gate EXIT 0 | ✅ **LIVE `49d4a931`** (02:16Z, one graph) |
| **#141** | 🧭 "Not on file" when it is on file (bank C 6500: Fred's firearms brand) — `Plan Request` keeps the person of the previous turn on a pronoun follow-up, scopes the raw search to them and ranks it by the message's distinctive words | 🟡 S2 | S | ✅ **proven on staging `c28fb532`** — exec 138001 (row 65875) "Fred's brand is *TLO Outdoors*" with his post; 23/23 unit; gate EXIT 0 | ✅ **LIVE `49d4a931`** (02:16Z, one graph) |
| **#142** | 🚧 The identity second-person rule no longer clamps a draft that refused the typed name (bank C 6483) — `secondPersonAboutOther()`; the clamp itself untouched | 🟡 S2 | S | ✅ **proven on staging `c28fb532`** — execs 137904 · 137962 (rows 65795 · 65845) real answers, was the canned line (137871); 9/9 unit | ✅ **LIVE `49d4a931`** (02:16Z, one graph) |
| **#144** | 📅 A follow-up about events stays in the events lane (bank C 6372) — `eventsLaneCarry()`; the 2027 catalog is reachable since `event_lookup_v3` | 🔴 S1 | S | ✅ **proven on staging `c28fb532`** — execs 137902 · 137954 (rows 65791 · 65833) consistent with the turn before; 9/9 unit (the carry stood by, the router chose events itself) | ✅ **LIVE `49d4a931`** (02:16Z, one graph) |
| **#176** | 🔒 Public mode means MDS members, not the world — corrected scope: OPEN = group posts/comments, partner + event pages, non-verification WA chats, public-flagged recordings; RESTRICTED = the 5 verification chats, restricted recordings, applications | 🔴 S1 | M | n/a (SQL + module) | ✅ **PROMOTED 2026-09-08 — prod `15649d68`** — 30-probe eval found + fixed 5 defects (own-post author unbacked · refusal instead of a no-detail answer · unlabelled evidence read as closed · a 420k-regex/turn 500 → 151ms · a `normText` whitespace bug blamed on the Haiku rewrite); name index 64 junk rows out (5,384→5,320); same-question before/after Public: 1→6 paragraphs, 1→4 links, 0→4 quotes, 8→0 masked (ungated compare 7/6/3); module tests 15→107; gate 331→345 GREEN; migrations applied LIVE; PR #2 |
| **#177** | 🔓 Ask Millie's Public answer names nobody even when the group backs the name — Facebook draft named Adam Weiler + linked his session, Ask Millie wrote "a member"/"one seller" for the same evidence | 🟡 S2 | S-M | staging + gate + promote | 📝 filed 2026-09-08 (Andy: "lets file it") — after #176 |
| **#178** | 🥇 The Strong-in-X rails and the cohort page ranked by the rounded percentile, so the real #1 landed third — Eugene in Slack: "How come Mo isn't at the top of this list" | 🟡 S2 | S | n/a (web — Render, no staging tier) | ✅ **SHIPPED 2026-09-08** — rails, Top 10 and the cohort page order by rank; cards read `#1` / `Logistics & 3PL · #1 of 674`; Render `15700f2`, prod verified |
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

### #186 · 🅿️ SPRINT 5 · Roadmap — one place that shows the work, built from the repo rather than maintained by hand
**🔵 S3 · size M-L — filed 2026-09-09 · CARRIES TO SPRINT 5 (Andy: "build another tool - roadmap or something like this … 1 is for real human devs, 2 is for anyone on the team to stay on track").** Repo `mds-digest-web`, the eighth tool in the #164 storefront. Priority chosen by me, not by Andy.

> **In plain words:** two views on one page. A technical index a new developer can start from, and a live task list anyone on the team can read without asking Andy.

*As a new developer, I want one page that points me at every repo, schema and technical doc, so that I can start without a handover call. As anyone on the team, I want to see what is closed, in progress and scheduled, with the story behind each one, so that I do not have to ask what is happening.*

**Why it has to pull, not copy.** This repo alone holds **271 markdown docs** across a dozen unrelated projects (Census, GroupOS, Application v3, Olivia, MRR, TikTok, Singapore, Member 360, WA digest, tools-health, the Scorecard), plus 8 more in `mds-digest-web`, four session logs, and the `db/` schema export. Nobody will hand-maintain a second copy of that, and a stale index is worse than none. Andy: *"Ideally, if these somehow can be pulled automatically, so we dont need to update them separately."*

**Part 1 — the developer index.** Rendered from the repos at request time: `mds-community-scoreboard` and `mds-digest-web` (both `github.com/AndyVerdy/…`), their READMEs and handbooks, `OLIVIA_HANDBOOK.md` as Olivia's front door, `CLAUDE.md`, the `db/` schema export (tables, views, functions, grants, RLS), and per-project docs grouped by project rather than dumped alphabetically. Every entry carries a link straight to the file on GitHub and its last-commit date, so staleness is visible instead of assumed.

**Part 2 — the task list.** Built from the boards that already exist and are already canonical: `OLIVIA_SPRINT_4.md` (**92 tickets today — 45 open, 47 closed**), `OLIVIA_BACKLOG_ARCHIVE.md` (34 shipped, evidence intact), `FB_BACKLOG.md` (8). Each ticket shows its number, title, priority, size, story, acceptance criteria, current state and — for closed ones — the evidence block. Grouped closed · in progress · scheduled, exactly as Andy asked.

**The fork to decide before building — do not choose this in code.** The board is one large hand-written markdown file whose format has drifted (my own count of open tickets was wrong on the first pass because closed markers are written several different ways).
- **Parse it as-is** — no change to how sessions write, but the parser will keep breaking on formatting drift.
- **Give tickets structure** — frontmatter or one file per ticket, so the tool reads data instead of guessing. Robust, but it changes the sprint ritual and every session that writes to the board.
A parser that is wrong is worse than no tool, because people will trust it. This is Andy's call.

**Scope note.** The board covers Olivia and Facebook. The other projects in this repo have handoff docs but no ticket board, so part 2 starts Olivia-only and part 1 covers everything.

**Accept when:**
1. Both views live behind the existing staff gate as one tool in the storefront, consistent with #164.
2. Nothing is duplicated: every doc and every ticket is read from the repo at request time, and no copy is stored that could go stale.
3. Part 1 lists every repo and every project's docs, each with a working GitHub link and a last-commit date.
4. Part 2 shows all 92 current tickets with story, acceptance criteria and state, grouped closed · in progress · scheduled.
5. Ticket counts on the page match a manual count of the board on the same day — proven once, in writing.
6. The page degrades honestly: if a source cannot be read, it says so rather than showing a shorter list.
7. `tsc`, lint, tests and `next build` clean. Merge = Render deploy.

### #192 · `npm audit` on every Render build: 1 critical (Next.js 16.2.4), 8 high — bump and re-prove
**🟠 S2 · size S — filed 2026-09-10 from the #172 deploy log (Andy: "whats this 19 vulnerabilities").**

*As the owner, the web app runs on a Next.js without published DoS / middleware-bypass advisories, and the audit line on a build is
zero-critical.* The critical is `next` itself (two advisories); the highs are transitive (`sharp` direct, `postcss`, `undici`,
`js-yaml`, `brace-expansion`, `browserslist`, `fast-uri`, `ip-address`). None arrived with #172 (the lockfile last changed in
`b648d4c`). The middleware-bypass advisory does not open `/admin`: every admin layout and API route checks the session cookie
itself. Fix = `next` + `sharp` bumps, then `npm audit fix`, tests green, build green, one deploy. **Acceptance:** audit line shows 0
critical / 0 high on the Render build; 1,389 tests green; `/api/version` shows the new sha.

### #193 · Ask Millie: the header title hydrates from the client and React logs a hydration error on every load with a thread
**🟡 S3 · size XS — filed 2026-09-10 from the #172 local proof (Next dev overlay: `ToolHeader.tsx:185`, client "How many current…"
vs server "…").** Pre-existing (the shell title is set before hydration finishes). Cosmetic in prod (React regenerates the tree),
noisy in dev. *As a developer, opening a thread does not throw a hydration error.* **Acceptance:** no hydration error in the console
on `/admin/ask-millie` with a saved thread, on dev and prod.

### #194 · Revenue data quality: `Most Recent Revenue` holds implausible values and a test row
**🟡 S3 · size S — filed 2026-09-10 from a Team research answer (the model flagged it unprompted).** Five current members carry
`Most Recent Revenue` between $500,000,000 and $1,000,000,000 and a row named "andy v test" carries $1.2B. Airtable is the SoT, so
this is Andy's/ops' to correct; the mirror only copies it. *As staff, a "top members by revenue" question returns members, not
data-entry errors.* **Acceptance:** the test row is gone from the Members table; the five values are verified or corrected; the
Team answer to "top 5 by most recent revenue" names real figures.

### #195 · 31 of 138 `digest` functions are EXECUTE-able by anon/authenticated while PostgREST exposes `digest`
**🟠 S2 · size S — filed 2026-09-10 (design §11 of #172).** Includes SECURITY DEFINER trigger functions (`content_delete_*`,
`content_ingest_*`, `tg_member_event_*`) and `olivia_front_door_v2`. Trigger functions cannot be called directly, but the surface
is wider than the #62 revoke intended. *As the owner, only `service_role` may execute a `digest` function unless it is a deliberate
public helper.* **Acceptance:** a gate check lists every anon/authenticated-executable `digest` function against an explicit
allowlist; everything else revoked with `CREATE OR REPLACE`-safe grants; gate green.

### #196 · `db/` drift: README says 104 functions, `db/` holds 139; `db/rls.sql` lists 40 RLS tables, live has 33
**🟡 S3 · size XS — filed 2026-09-10 (design §11 of #172).** Housekeeping: regenerate the README counts from the export and make
`db_export_schema.py` write them; add the live RLS count to the drift check. Also the stale "before Vercel cuts us" comment in
`src/app/api/admin/millie/chat/route.ts` (the app is on Render) — one-line fix, ride along.

### #197 · `member_links` and any view that calls a raw-table helper are dark in Team mode
**🟡 S3 · size XS — filed 2026-09-10 from the #172 proof.** `digest.member_link(text)` reads `member_profiles` inside its body, so
`member_links` fails with 42501 for `millie_team_ro` even though the view itself is granted. Either point the helper at
`member_profiles_team` or document the view as Team-dark in the catalog. *As staff, a catalog table that is listed is readable.*
**Acceptance:** `select * from digest.member_links limit 1` through `team_sql` returns 200, or the catalog marks it dark.

### #198 · The MCP door: the Team research principal on a second transport (Andy: "why not to make api and our MCP so i can use
it with claude?")
**🟠 S2 · size M — filed 2026-09-10 (design §10 of #172, Andy's original ask).** Same role, same `team_sql`, same deny-list view
and log table, exposed as an MCP server (or an authenticated API) so Andy's Claude can ask the warehouse directly. Needs its own
identity story (a research-only PostgREST role or a bearer bound to a staff email), the same per-asker budget, and the same trail
in `olivia_web_messages`. *As Andy, I ask the warehouse from my own Claude and every query is logged under my name.* **Acceptance:**
one MCP tool call from Claude Desktop returns a Team answer with its trail; the log row carries the asker; the leak gate's `#172`
section stays green; WhatsApp/member/anon gain nothing.

## 🌙 OVERNIGHT 2026-09-11 — the #190 remediation: eight core fixes, SQL live, the graph staged for Andy's promote

**Andy's instruction at 00:50:** *"It's a 22% failure. There is no such thing as partial. Partial = fail … you will work
overnight and close tickets one by one … fix the core issue, not a specific question … reprobe the failed question plus 3
similar types of questions … I'm expecting <2% of issues unless we have core issues."* His three rulings before the work
started: **no full re-run of the 100 bank** · **new SQL functions may go live, the workflow stays staged for his promote** ·
**a member's brand is public — add it to the 🟢 SHARE column.**

**Where it landed: of the 22 (14 FAIL + 8 PARTIAL), 17 are addressed and 5 still fail — 5%, against his <2% bar.** Every fix was proven with the
failed question plus three siblings of the same shape, fired at staging.

| # | what was wrong | the CORE fix (not the question) | proof |
|---|---|---|---|
| **#201** | "top 5 most watched" denied a number we hold; "who owns Stylia Beauty" denied a field no tool selected | `video_search_v2` takes **`p_order=views`** and every row carries its count in `strength_note`; `member_card` resolves a **brand** to its owner and **`member_card_v3`** returns the brands so the answer can say it and the gate can verify it; the plan asks for the ranking instead of narrating arrival order | **8/8** |
| **#202** | a named chat was dropped and a different chat recommended | a chat named in the question routes to **`chat_info`** (its gate, its requirement, its join link), matched against the real chat directory; the recommender still runs when no chat is named | **5/5** incl. the not-a-member path and the recommender guard |
| **#203** | "MDS 9" denied by a lane that cannot see programmes | a named **MDS programme** routes to the events lane, which holds its four events | **4/4** |
| **#204** | an exact revenue figure in Millie's own voice, seen by a real member on 09-04 | the band rule in the prompt **and** a deterministic strip in `Format Reply` of a money-only parenthetical on an uncited line | **4/4** (band given, figure gone, cited quotes untouched) |
| **#206** | coverage described as a feeling | **`content_stats` gained a `coverage` metric** — per source: count, earliest, latest, how many predate 2025 — and coverage questions route to it | **4/4** |
| **#207** | "are you able to do daily reminders?" answered by improvising a capability | an **ability question about Millie's own mechanics** routes to the curated list (#79), which now states what she cannot do: Summit-schedule reminders only, no routines, no watching | **4/4** incl. the "can you find me a member in Miami" guard |
| **#208** | "what did the speaker say about Trybe?" denied it, while the transcript says **"Tribe"** | the videos lane fetches **transcript passages** for the named thing on a what-was-said question (its second fetch was empty by design), with **spelling variants** (y↔i, ph↔f), and renders them as quotable passages | **4/4** |
| — | Q5057 and Q5067 | **the bank was wrong, not Millie** — 5057 described Andy's own application record correctly; 5067's "2 months free" is in no tool row (`partner_lookup_v2` returns the standing *1 month FREE + 20% + 5% OFF ULTRA*, `event_offer` NULL). Both truths corrected | — |
| — | Q5032 · Q5061 | improved and passing on re-probe: the roster now returns a count and no names; a near-miss no longer offers an unrelated member | — |
| — | Q5041 · Q5044 · Q5087 · Q5094 | **flaky, not broken** — all four answered correctly on the hand re-fire before any change. Nothing was fixed for them and nothing needed to be | — |
| **#209** | four failures that seven new rules in the shared STYLE block did NOT move | **each rule moved into the lane that answers that shape**, and the one that was really an evidence problem got evidence: the digest block went from **12 rows × 400 chars to 20 × 700** | **5027 ✅** (both chats, every real topic) · **5061/5032 ✅** · geo **2/3** (Dallas and New Jersey now name members; the original zip question still refuses) · 5068 ✗ · 5098 ✗ |

**Regression guard before the promote:** eight previously-passing exam questions across every lane touched (videos, member,
chats, events, capability, partners, content) re-fired at staging: **7 PASS · 1 PARTIAL · 0 FAIL**, and the one partial is
the corrected-truth 5067. **Gate 367/0 exit 0** after the SQL. `db/` re-exported (164 files, +`member_card_v3`).

**⛔ STILL FAILING — 5 of 100 (5%).** #5011 (the zip-code question still refuses, though "within 50 miles of Dallas" and
"near me in New Jersey" now name members) · #5034 (no Montreal event and no widening to Toronto) · #5042 (expert names
beyond what the tool returned) · #5068 (a partner credited to a person the evidence does not support — Hector's
`web_people` is empty, so the right answer names nobody) · #5098 ("they" with no antecedent answered anyway).

**The core issue, and it is one thing.** None of the five is missing capability: in every case the tool already returned
what the answer needed. They are the model using its evidence loosely — and the night proved how far rules can carry that.
**Seven rules added to the shared STYLE block moved none of them. Moving the same rules into each answering lane moved
half.** The other half needs the answer to be ASSEMBLED from the returned rows rather than written around them — a design
change, not a night's patch. **That is the decision for Andy**, and it is what stands between 5% and his <2%.

**✅ PROMOTED 2026-09-11 14:33Z on Andy's word ("promote staging").** Prod n8n `12wj6h1TWqb0d4Dq` is now **`b31eadbb`**
(92 nodes, active, webhooks intact); the permanent graph hash pin `olivia_snapshots/prod_pre_172.sha256` was re-snapshotted
deliberately (`08013a8e…`) and the gate is **367/0 exit 0** against it. Roll-back: `olivia_snapshots/prod_2026-09-11T141737Z_pre-190-promote.json`.

**The promote caught a real defect in #208, which the staging proof had missed.** On prod, "a speaker spoke about Trybe"
still denied it — and the stored plan showed the videos lane's own empty second fetch
(`p_terms: [], p_sources: ['fb_post'], p_limit: 0`), not the transcript search. The block had been inserted a few lines
ABOVE that reset, so it never survived. It had passed 4/4 on staging **for the wrong reason**: `sources_used` shows the
model called `content_search` three times on its own and got lucky once — exactly the variance the deterministic fetch
exists to remove. Moved below the reset (`apply_208b_transcript_fetch_order.py`), re-proven on staging with the plan
inspected this time (`raw sources=['call_transcript'] terms=['trybe','tribe']`), promoted again.

**Live proof on prod after the promote:** "top 5 most watched mogul calls" → the real ranking with counts (264, 192, …) ·
"who owns Stylia Beauty" → Lenny Joseph · "are you able to do daily reminders" → the curated capability list · "a speaker
spoke about Trybe" → found in Brandon Himmel's TikTok Mastermind, *also written "Tribe"*, with the context. Probe rows
cleaned; lock released.

### #210 · 🅿️ SPRINT 5 · She refuses a member their OWN job title — the never-share rule is not scoped to other people

**🔵 S3 · size XS — filed 2026-09-11 from the nightly eval (Q2096), confirmed live on prod `b31eadbb` the same morning.**

> **In plain words:** ask "what is my title according to my membership application?" and she says she cannot share job
> titles, even your own. It is your own application, and the rulebook already says your own application answers are
> yours to see.

*As a member, my own application answers are mine — when I ask what I put on my own form, I get it back.*

**Proven live, not inferred** (prod, 2026-09-11 14:41Z, after the promote). The lane is right and the evidence is there:
the plan ran `content_lookup` with `p_source: 'application'`, and that item (`content_items` 13380, `access_rule
{type: owner, member: recCUUw8iiUnJjac1}`) literally reads *"Title: Head of Tech & Automation"*. The answer was:

> *"I'm not able to share job titles, even someone's own — that field stays out of what I hand back."*

**The cause is a rule that lost its subject.** `OLIVIA_SHAREABLE_FIELDS.md` lists **job titles** under 🔴 NEVER, and that
list is about **another member** — the same page carries the self-exception in writing: *"a member may see their OWN
billing, dossier, application answers (self-only functions, fail-closed)."* The refusal applies the other-person rule to
the asker's own record. **She is already inconsistent about it:** asked "tell me what you know about me" on the same
prod graph she answers *"Staff at MDS (Head of Tech & Automation)"* (re-fire 2026-09-11 05:25Z) — the same fact, given on
the dossier lane and refused on the application lane.

**Shape of the fix.** Scope the never-share wording to the SUBJECT, not the field: a job title is closed about *another
member* and open about *yourself*, exactly like billing and application answers. The self lanes (`my_form_answers`,
the `self`/`dossier` periods, `content_lookup p_source='application'`) already fail closed on identity, so the guard is
the lane, not the sentence.

**⚠️ Andy's call if he wants the opposite:** if job titles should stay closed even to the asker, then the DOSSIER lane is
the bug and the fix is to stop volunteering it there. One of the two has to change — today she both refuses it and
volunteers it, which is the worst of both.

**Accept when:** 1. "What is my title according to my membership application?" returns Head of Tech & Automation ✅
2. Asking for ANOTHER member's job title is still refused ✅ 3. The dossier lane and the application lane agree ✅
4. `OLIVIA_SHAREABLE_FIELDS.md` says which rules are subject-scoped, so the next field does not repeat this ✅
5. Gate GREEN, with a check that another member's title stays closed.

### #204 · An exact revenue figure reached a member in Millie's own voice

**🔴 S1 · size S — filed 2026-09-11 from #190's exam. A member has already seen it.**

> **In plain words:** the rulebook says a member's exact revenue may be repeated only as a quote, with its link, next
> to our band. Millie instead wrote the number as a plain fact about the person, in her own sentence.

*As a member, no answer ever states another member's exact revenue as a fact — even when the figure is public,
it arrives as a quote with its source, or as the band.*

**The evidence, twice.** A real member asked for an intro on **2026-09-04** and got *"I did find Joshua Asquith, a UK
beauty brand owner (£14.5M/yr)…"* (`olivia_messages` 62689). The exam reproduced the same shape on 2026-09-11 (Q5043).
The figure itself is legitimately quotable — it is in MDS's own public welcome post (`content_items` 133718,
2026-07-29, *"a UK beauty brand doing £14.5M a year"*) — and `OLIVIA_SHAREABLE_FIELDS.md` is explicit: quotable
**ONLY as an attributed quote with its link, paired with our band, never in Olivia's own voice**. A bare parenthetical
is exactly the forbidden shape. On a re-fire the clamp caught the turn, so it is **intermittent, not deterministic**.

**Why the gate did not catch it.** The leak gate probes our OWN revenue columns; this number came in as *content*, from
a public post, so nothing in the retrieval layer was violated. The rule that was broken is a rendering rule.

**Accept when:** 1. A revenue figure sourced from content appears only as an attributed quote with its link, or not at
all ✅ 2. The band still appears where we hold one ✅ 3. A gate check fires on a currency figure rendered adjacent to a
member name without a citation, using both 62689 and Q5043 as fixtures ✅ 4. No new over-refusal: the public quote is
still available to members who ask for it ✅ 5. Gate GREEN.

### #201 · Millie denies what we hold because the tool never returns the column

**🔴 S1 · size M — filed 2026-09-11 from #190's exam (2 of the 7 reproducing failures, and the biggest `false_denial` mechanism).**

> **In plain words:** twice she said "I don't have that" about something sitting in the database — not because search
> failed, but because the function's output list never had the column in it.

*As a member, when the warehouse holds the answer, the tool hands it over — a denial means we genuinely do not have it.*

**Two proven cases.**
- **`view_count`** — `digest.videos_catalog.view_count` is populated and `refresh_entity_dossiers` already reads it, but
  `digest.video_search_v2`'s `RETURNS TABLE` has no such column. Q5100 *"what are the top 5 most watched mogul calls"*
  → *"I don't have a view-count ranking"*, then an invented "members clearly engaged with" ordering. The real top 5 by
  views starts with *Amazon Ranking Mastery — Alex Chiru & Matt Altman* (264).
- **Brand Name** — `grep -rl "Brand Name" db/functions/` returns **nothing**, and `member_card_v2` emits a fixed
  19-column set with no brand. Q5060 *"which member owns Stylia Beauty"* → not found, while Lenny Joseph's profile
  carries `Brand Name = Stylia`.

**Shape of the fix.** Add `view_count` (and `like_count`) to the video tool's contract and let the ranking lane order by
it; add the member brand to the card and to whatever `find` searches, under the 🟢 SHARE column of the rulebook (a
brand a member sells under is public by construction — it is on their listings). **Then audit the other direction
once:** walk each gated function's RETURNS list against the columns its source table holds, and write down every field
we deliberately do not expose, so the next denial of this kind is a decision and not an oversight.

**Accept when:** 1. "Most watched" answers with real view counts ✅ 2. "Who owns <brand>" resolves from the profile
field ✅ 3. The audit table lands in the handbook (§6.2) — every gated function, the columns it withholds, and why ✅
4. Nothing new is exposed that the rulebook does not already permit; gate GREEN ✅

### #203 · One lane denies while another lane holds the answer

**🟡 S2 · size M — filed 2026-09-11 from #190's exam (2 of the 7).**

> **In plain words:** she asks one place, it is silent, and she reports that silence as "we don't have it" — while a
> different place in the same warehouse has it.

*As a member, "I can't find that" means the whole record was checked, not one shelf of it.*

**Two proven cases.** Q5071 *"how do I become a member of MDS 9"* → *"I'm not familiar with anything called MDS9"*,
answered from `community_info` + `org_docs`, while `events_catalog` holds **MDS 9 100M+ Mastermind Dec 2026**,
**MDS 9 BFCM Strategy Dinner Oct 2026**, **MDS 9 Michelin Dinner July 2026** and the library holds the July 2026
MDS9 Mastermind sessions. Q5097 *"a speaker at Singapore spoke about Trybe"* → denied in the transcripts, where the
word is spelled **"Tribe"** (Brandon Himmel's TikTok Mastermind, ~00:39) — she then supplied excellent Facebook and
WhatsApp context on Trybe, which makes the denial of the transcript hit worse, not better.

**Shape of the fix.** Two halves, and they are separable: (a) a denial about a NAMED thing must cost one more lookup
before it is spoken — if the name appears in `events_catalog`, `videos_catalog` or `partners_catalog`, the answer
cannot be "never heard of it"; (b) a proper-noun query should try close spellings (trigram) before concluding
absence. (b) alone fixes Trybe; (a) alone fixes MDS 9.

**Accept when:** 1. "MDS 9" returns the tier with its events and sessions ✅ 2. "Trybe" finds the Singapore transcript
hit ✅ 3. No new false positives: a genuinely absent name still gets an honest miss (Roman Khan, Herdr and Stash all
stay honest misses) ✅ 4. Gate GREEN.

### #202 · "How do I join <named chat>" recommends other chats instead

**🟡 S2 · size S — filed 2026-09-11 from #190's exam.**

*As a member, when I name the chat I want, I get that chat's joining rule — not a list of chats you think suit me.*

Q5022 *"how do i join the supplements channel"* planned `chat_recommendations` with **no query parameter at all**, so
the named chat was dropped and the answer offered *MDS TikTok 1M+ TTM*. MDS Supplements is verification-gated
(*"Member needs to sell supplements"*), its verification form is `form.typeform.com/to/j5JAS5sT` and its invite is
`chat.whatsapp.com/Hz94bAWIbLX5NBhLA32t46` — none of it reached the member. Note the real member report **#34**
("the link doesn't work?", John Cho, 2026-08-25) sits in the same lane.

**Accept when:** 1. A named chat in the question routes to that chat's own record ✅ 2. Gated chats state the gate and
give the form; open chats give the invite ✅ 3. The recommender still runs when no chat is named ✅ 4. Gate GREEN.

### #205 · A post's tail is cut by its rank, so the answer's fact never reaches the model

**🟡 S2 · size S — filed 2026-09-11 from #190's sticky-13 triage.**

*As a member, the fact I asked for is not lost because its post ranked fourth instead of third.*

`Build Prompt` renders Facebook hits on a tiered budget — **ranks 1-3 whole (1,600 chars), ranks 4-10 cut at 500, the
rest at 220**. Q2103 asks when Advisory Council applications close; Millie cites **the right post** (Eugene Khayman,
2026-05-13) and says no closing date is stated — because *"Applications close May 22, 2026"* sits at character **658**
of a 744-character post that ranked outside the top 3. This is the failure the tiered budget was invented to fix
(2026-07-25, bodies running 1,000-1,900 chars), only one tier lower down.

**Shape of the fix:** never truncate a post that is already short — a floor of ~1,000 chars for any hit inside the
top 10 costs a few hundred tokens and removes the whole class. Measure the prompt size before and after.

**Accept when:** 1. Q2103 answers May 22, 2026 ✅ 2. The FB block stays inside its overall cap (18,000 chars) ✅
3. The nightly's `false_denial` count does not rise ✅ 4. Gate GREEN.

### #206 · She describes her coverage instead of stating it

**🔵 S3 · size XS — filed 2026-09-11 from #190's exam.**

*As a member, when I ask how far back you can see, I get the dates.*

Q5047 *"can you do past posts on Facebook from many years ago?"* → *"the further back you go into 'many years ago'
territory, the thinner it gets"*. The answer is a number: **4,283 posts, 2021-08-17 → 2026-09-10, of which 5 predate
2025** (1,743 in 2025, 2,535 in 2026). Same shape as `reference_mirror_freshness_signal`: every mirror needs a
freshness signal the answer can quote. **Accept when:** a coverage question answers with the real window and counts,
and says plainly that pre-2025 is effectively absent.

### #200 · Team mode access without touching Render — any @mds.co in, offboarding, per-person usage and spend, super-admins only
**🟠 S2 · size M — filed 2026-09-11 (Andy: "I don't like the idea of adding people to render so the team can use it. We should
have a system that lets anyone on the MDS team use it, along with a way to offboard people. And we need a tracking mechanism on
how the team is using it, ideally how much they spent, and this should be gated for super admins only… phase 1 is to unlock for
any @mds.co, but I know it's scary").**

> **In plain words:** today a colleague gets Team mode only if Andy edits a Render setting and redeploys. Instead: every
> MDS staff login works by default, one switch turns a person off, and a page only super-admins can open shows who asked
> what and what it cost.

*As MDS staff, I open Ask Millie's Team tab and it works because I am @mds.co. As a super-admin, I see each person's turns
and spend for today and the last 30 days, I can switch anyone off (and back on) without a deploy, and nobody else can open
that page.*

**Phase 1 (Andy's call, deliberately):** the allowlist becomes "every @mds.co session" — `MILLIE_TEAM_ASKERS` turns into an
optional DENY list plus a kill switch (`MILLIE_TEAM_ENABLED=false` → 403 for all); per-asker daily budgets stay (40 turns /
$10, env-adjustable); every turn still logged with the asker. **Phase 2:** a `digest.team_access` table (email, enabled,
daily_turns, daily_usd, added_by, disabled_at, note) read by the gate at request time (no deploy to change it); an admin page
`/admin/millie/team-access` gated to `MILLIE_TEAM_ADMINS` (super-admins — a Render setting is acceptable for THAT short list) with
per-person turns / $ / last ask for today and 30 days straight from `olivia_web_messages.metrics`, enable/disable, per-person
budget override, CSV export. Offboarding = disable here; leaving MDS also kills the staff OTP login, so both layers close.
**Acceptance:** 1. A new @mds.co staff member uses Team mode with no deploy. 2. A disabled email gets 403 on the next turn. 3. A
super-admin sees per-person turns and spend (today / 30 d); any other staff gets 403 on the page. 4. The kill switch takes
effect on the next request. 5. Leak gate `#172` section green; nothing new for members/WhatsApp/anon.

### #199 · Team research: a `scan_content` tool — classify EVERY message of a member set for a fuzzy trait
**🟠 S2 · size M — filed 2026-09-11 (Andy: "file #199 the scan tool. but do not start it yet, lets finish our plan first").
PARKED — not started.** Depends on #172 (live).

> **In plain words:** today Team mode finds a concept by words and by meaning and reads the hits. To answer "who
> attended Inspire 2026 and is thinking of moving to Miami" for certain, it must READ every message of those people,
> not search for likely ones. That is a scan job with a classifier, not a bigger prompt.

*As MDS staff, I can ask a question about what a set of members has said anywhere (WhatsApp, Facebook, calls, forms) —
"who is thinking of relocating", "who mentioned hiring a COO", "who sounds burned out" — and get a complete tally with
the quotes, not a sample.*

**Shape (design, to confirm before build):** a fourth tool beside `sql_query` / `schema_catalog` / `semantic_search`:
`scan_content(filter: {members | chats | sources | since | until}, question: "<trait>", max_messages)` → the loop
selects the rows through `team_sql`, a small model (Haiku-class) classifies them in batches of ~50 with a fixed rubric
(yes / no / unsure + the quote), the tool returns the tally per member with quotes and the sample size; the trail step
records rows scanned and cost; the per-asker daily budget already caps it. Live measure 2026-09-11: the last 30 days of
WhatsApp ≈ 4,000 messages; one full-year scan of everything is tens of thousands of rows — the tool must say what it
scanned and refuse silently-partial answers. **Acceptance:** 1. Andy's example question returns every attendee who said
it, with quotes and dates, and the count of messages scanned. 2. A scan over a set the model cannot finish within the
budget says so (no partial tally presented as complete). 3. Cost per scan is on the trail and in `metrics`; a 30-day
WhatsApp scan costs under $5. 4. The leak gate's `#172` section stays green (no new grant, no n8n edit).

**✅ SHIPPED 2026-09-11 — web merge `9ade4b6` (Render, live).** Spec `docs/superpowers/specs/2026-09-11-199-scan-content-design.md`,
plan `docs/superpowers/plans/2026-09-11-199-scan-content.md`. No n8n edit, no new SQL function, no new grant.

*Results.* A fifth Team tool. Millie picks the rows by writing a read-only SELECT, exactly as she writes `sql_query`;
`scan_content` probes that SELECT's shape, COUNTS AND PRICES the set before reading a single row, refuses over 5,000 rows,
over the cost cap ($2 default, $5 ceiling) or on a non-unique `id`, pages through the existing `digest.team_sql` in 500s,
then reads EVERY row with `claude-haiku-4-5` (40 per call, four in flight) and returns a per-member tally with quotes
verified verbatim against the source text. It stops honestly on the wall clock, on the cost cap or on a failed batch, and
`complete:false` then carries the real `scanned` of `total_rows`. Tool costs now count in the turn's `cost_usd`, so the
per-asker daily budget binds them, and the trail shows each step's cost.

*Proof.* **AC 1 tool level:** four planted "moving to Miami" messages from real Inspire 2026 attendees, `complete:true`,
4/4 with verbatim quotes, $0.0008. **AC 1 end to end:** Andy's own question — the model built the 242-attendee set, called
`scan_content` once, returned 3 confirmed with quotes plus the deliberately hedged 4th flagged `unsure` and surfaced
anyway, "read 11 messages … cost $0.0019, complete: true", 6 laps, $0.121. *(That run pre-filtered on "Miami" before
scanning, so the TOOL-LEVEL proof is the one that demonstrates "reads every row"; the e2e run demonstrates routing.)*
**AC 2:** a 4,087-row set at `max_cost_usd 0.05` → `refused:"over_budget"` with the estimate, `cost_usd: 0`, nothing read;
a forced wall cap → `complete:false, scanned 1702 of 4087`. **AC 3:** a real 30-day WhatsApp scan, 2,541 rows, scan $0.35,
turn $0.5676, cost on the trail step and in `metrics` — under the $5 bar. **AC 4:** gate **exit 0**; no new function, no
grant, graph untouched. 1,425 tests green, tsc and eslint clean. ⚠️ `db_export_schema.py --check` exits 1 on FOREIGN drift
(`member_web_presence` / `web_edges` / `web_entity`, the parallel Exa.ai session) — #199 added no SQL; "gate green" here
does NOT mean the schema export is clean.

*What the proof changed in the product.* The first end-to-end run FAILED — 15 laps, `lap_cap`, no answer — because the
model was sampling the database to derive how a content row attributes to a member. That join was never written down.
`scan_content`'s description and the static catalog now carry it, and the next run took **6 laps**. While fixing it we
found the catalog's own claim about Facebook rows was false: `content_items.meta->>'sender_member'` is the WA Airtable id
for `wa_message` (17,611/17,611 via `member_identity`) but the **canonical `at_member_id`** for `fb_post`/`fb_comment`
(19,077/19,241 direct; **0/19,241** via `member_identity`). One key, two identity spaces, by source — now documented.

*ACs.* 1 ✅ · 2 ✅ · 3 ✅ · 4 ✅.

*Before / after.* Finding a trait over a set: search-then-read-the-hits (Andy's scope check: 24 queries, 14 laps, 112 s,
$0.87, honest no-match) → every message read, with a tally, quotes and the count scanned. A 30-day WhatsApp read costs
$0.35. Millie's answer now always states what it read and what it cost.

*Found alongside — not this ticket, flag for priority evaluation.* (a) **The event-spend field trap:** asked "who spent the
most on events", she answered from `Event Cost (Expense) - Last 12 Months` — what the event cost MDS — and declared no
all-time field exists, while `Event Revenue - All Time` sits in the catalog (Jake Ryan $183k, Brian Williams $155k).
(b) **No payment history in the mirror:** "past due more than twice in 6 months" cannot be answered exactly; the mirror
holds only the latest `Failed Payment Date (Stripe)` / `Recovered Date (Stripe)`, so she proxied from the weekly snapshot
and said so. (c) If `runResearchLoop` throws, the route logs `cost_usd: 0` — a crashed expensive turn charges nothing
against the daily budget (pre-existing from #172, higher stakes now).

### #191 · The nightly eval is dead — #105's webhook secret refuses all 220 posts
**🔴 S1 · size XS — filed 2026-09-10 from the #123 investigation.**

> **In plain words:** the nightly quality check stopped working this morning. It talks to Millie
> through the WhatsApp webhook, and that door now demands a secret it does not send, so every
> question is refused and there is no report for today.

*As the owner, the nightly eval keeps telling me where answer quality is, including on the mornings
after we harden something.*

**Evidence, from the job's own log (`/Users/Born/mds-scorecard-tools/olivia_eval.log`).** The run
that started `2026-09-10T08:30:05Z` fired 220 questions and logged **`[403]` NO REPLY in 120s on
every one — 180 posts, 0 with `[200]`** before it gave up; no `# Olivia eval — 2026-09-10` header
was ever written. The three previous runs (09-07, 09-08, 09-09) each logged **220 `[200]`** and
produced a report, so this is new today.

**Root cause.** #105 closed the n8n side door by putting header auth on the `WA Inbound (POST)`
node — prod `22d81380` carries `"authentication": "headerAuth"` with the credential
`Olivia Relay Secret` (`kKOzVnAzRFE0ZiVN`). The relay sends `X-Olivia-Relay: <relay_secret>`
(`n8nWebhookHeaders()` in `mds-digest-web/src/lib/meta-webhook-config.ts`), read from Supabase Vault
via `digest.meta_webhook_config()`, which returns `secret, enforce, relay_secret` with
`relay_secret` set and `enforce = true`. `olivia_eval.py` line 93 curls the live webhook with
`Content-Type` and nothing else. No header, no entry.

**Shape of the fix.** The eval sends the same header the relay sends, reading `relay_secret` from
`digest.meta_webhook_config()` at run start rather than holding a copy — so a rotation cannot
break it. The same one-line gap exists in any other local script that posts to the live webhook;
sweep for them (`olivia_selftest.py` is the first suspect) in the same pass. #105 stays as it is.

**Accept when:**
1. A nightly run posts 220 questions with `[200]`, not `[403]`, and writes its report.
2. The secret is read at run time from `meta_webhook_config()`, never pasted into the script.
3. Every other local script that posts to `olivia-wa-live` is checked in the same pass, and the
   ones that were broken are fixed or named as deliberately dead.
4. A 403 from the webhook makes the run FAIL LOUDLY — a Slack line — instead of a silent
   no-report morning.

#### ✅ CLOSED 2026-09-10 — the eval talks to Millie again, and a closed door can no longer be silent
**The fix:** `scripts/olivia_relay.py` is the single place that knows the door — it reads `relay_secret`
from the Vault-backed `digest.meta_webhook_config()` at call time and returns the curl args, so rotating
the secret cannot break the tools again. `olivia_eval.py` carries the same helper (it lives in the other
repo), and `smoke_manual_suite.py` imports it. Prod and staging share the `Olivia Relay Secret`
credential, so one header covers both targets. #105 was not touched.

| AC | result |
|---|---|
| a run posts its questions with `200`, not `403`, and writes its report | ✅ **25/25 `200`** on the live webhook, every one answered (`--fire --limit 25`, 2026-09-10 17:36Z). The full 220-question report is tonight's nightly at 03:30 — the harness is proven, the report itself is not yet written |
| the secret is read at run time, never pasted into a script | ✅ `meta_webhook_config()` per run; no secret in either repo |
| every other local script that posts to `olivia-wa-live` is checked in the same pass | ✅ four found, three were broken the same way and are fixed: `olivia_eval.py`, `olivia_selftest.py`, `olivia_reaction_canary.py`, `smoke_manual_suite.py`. `olivia_wf.py` only names webhook paths, it never posts |
| a 403 makes the run fail loudly instead of a silent no-report morning | ✅ three refusals in a row abort with a Slack line and exit code 2 |

**Before → after:** the 2026-09-10 08:30:05Z run logged **180 posts, every one `403`, zero answers, no
report**. The same path now answers: 25 of 25, 6.6-19s each. The three runs before the outage each logged
220 × `200`, which is what made this new rather than chronic.

**Found while sweeping, not fixed:** the spend ledger recorded **$6.71 for the dead run** — the preflight
books the spend before a single answer comes back, so an outage still spends the daily cap on paper. Not
filed; it costs nothing real and the cap is generous.

### #184 · Part 1 — take Tony's post and the two partner profiles out of Millie's reach, now
**🔴 S1 · size S — filed 2026-09-09 · CU [`86e35hm1p` — Response to Joe Nilsen (MajestIQ)](https://app.clickup.com/t/86e35hm1p) (Eugene Khayman → Andy).** Part 2 is #185.

> **In plain words:** one post and two partner profiles must stop coming back in Millie's answers, while staying exactly where they are for members.

*As MDS staff, I want Millie to stop surfacing this specific post and these two partners when a member asks about reviews, without anything being deleted anywhere else.*

**The request, verbatim (CU comment, Eugene → Andy, 2026-09-09):** "Andy from Millie, please remove that post, like Tony's post, so it doesn't get surfaced if anybody asks about reviews and stuff like that. It's not indexable. Can we unindex the post? and also unindex the partner profile."

**What already happened in the CU thread, and must not be repeated.** Juancho deleted MajestIQ and TraceFuse from Wild Apricot and Airtable and revised their MDS app profiles. Eugene reversed it: *"no, MajestIQ and TraceFuse should still be records in Wild Apricot and Airtable, and they should also be searchable in our app. Nothing should be deleted. We simply said that we would revise the profiles to not mention review manipulation."* Juancho then restored both. **Deleting is explicitly wrong here.** Eugene has asked Ian Sells and Anita Petrov to double-check it landed.

**The three things, verified live 2026-09-09.**
- **Tony Brink's post** `27155813964095414`, 2026-09-05, "Improving Star Rating – New Vendor Is Crushing It". In `digest.fb_posts`, mirrored to `digest.content_items` as `fb_post`, `embedding` populated — keyword and semantic retrieval both reach it. Eugene turned off commenting on it and is deliberately not deleting it.
- **MajestIQ** (`6a7ef5653e2bb7bb29849b61`) and **TraceFuse** (`671b2e4695467ac97883bcbb`) — both `status = published`, `access_restriction = public`, both carrying a `search_tsv` and an `embedding`, so `partner_lookup_v2` and the finder reach them.
- **Our mirror predates the revision.** The app profiles were revised on 2026-09-08. `partners_catalog.synced_at` is **2026-08-01** for TraceFuse and 2026-08-17 for MajestIQ; `partner_web_profile.crawled_at` is 2026-09-03 for both. TraceFuse's catalog row **and** its crawled profile still match review-removal language today. So even setting the unindex aside, Millie is holding the wording Eugene ordered removed.

**Shape of the fix.** Suppress the three keys at the retrieval layer, and separately re-sync the catalog and re-crawl both web profiles so the revised wording replaces the old text rather than sitting behind a flag. Nothing is deleted from Facebook, Wild Apricot, Airtable or the MDS app.

**Open question for Andy and Eugene — do not decide in code.** Eugene wrote "Tracefuse should receive similar treatment." Suppressing a partner's own profile is one thing; suppressing **members' own posts** about that partner is another, and there are at least five live ones (Maxwell Sigurdson-Scott 2026-08-28, Keith Mander 2026-08-04, Justin Beck 2026-04-14, Craig Brockie 2026-03-24, Eric Hulli 2025-12-09). This ticket covers the two partner profiles and Tony's single post only.

**Accept when:**
1. Post `27155813964095414` is returned by no Millie retrieval path — proven with the question that surfaced it, before and after.
2. MajestIQ and TraceFuse are returned by neither `partner_lookup_v2` nor the finder, proven with a real query vector.
3. The post is still live on Facebook; both partners are still records in Wild Apricot and Airtable and still searchable in the MDS app.
4. `partners_catalog` and `partner_web_profile` carry the post-revision text for both partners, with no review-removal wording left in either row.
5. A leak-gate check asserts none of the three keys appears in any answer's evidence.

### #185 · Part 2 — a general way to keep restricted content out of Millie: blacklist, detection, or both
**🟡 S2 · size M — filed 2026-09-09 · CU [`86e35hm1p`](https://app.clickup.com/t/86e35hm1p) (Andy 2026-09-09: "this is a two-part job. unindex post, and in general process of either blacklist things or teach bot on how to detect restricted content").** #184 is the one-off act; this is the capability.

> **In plain words:** doing this by hand once is fine. Doing it every time somebody flags something is not, so we need either a proper blacklist or a bot that recognises the topic itself.

*As MDS staff, I want a standing way to keep a class of content out of Millie's answers, so that the next flagged post does not need an engineer and does not silently come back.*

**Why a one-off is not enough.** Nothing in the schema suppresses retrieval today: `digest.fb_post_overrides` carries post type and answered state only. Flipping `partners_catalog.status` reverts at the next `partners_refresh` and would also pull the offer from members, which Eugene explicitly rejected. Any manual edit is undone by the nightly re-embed. So a hand fix quietly expires, which is the worst failure mode — it looks done.

**The fork to decide, with Andy and Eugene.**
- **Blacklist** — an explicit, auditable list of suppressed keys. Precise, reversible, no false positives, but only as good as who remembers to add to it.
- **Detection** — Millie recognises the restricted class itself (review manipulation, and whatever classes come next) and declines to surface it, list or no list. Catches the cases nobody flagged, and risks suppressing legitimate discussion. Note this is a **topic** rule, distinct from the #176 restriction spine, which is about who may see a source.
- Likely both: a list for what we know, detection for what we do not.

**Shape of the fix.** Whichever branch, it must be enforced once at the retrieval layer so every lane inherits it (content search, partner lookup, the finder, the Facebook draft tool, Ask Millie), survive the nightly re-embed and every catalog refresh, be reversible in one edit, carry who and why, and be visible to staff in the admin rather than living in a migration.

**Accept when:**
1. The fork above is decided in writing by Andy and Eugene before any code.
2. Adding a suppression is a staff action in the admin, not an engineering task.
3. A suppressed key survives a nightly re-embed and a `partners_refresh` run, proven by running both.
4. Lifting a suppression restores retrieval in the same edit.
5. Every entry records who, when and why, and the list is readable by staff.
6. The leak gate asserts the whole list, not one hand-picked key.
7. If detection ships, it is measured on a labelled set with its false-positive rate stated, not assumed.

### #179 · A Make WARNING shows as a tool DOWN on the health dashboard
**🔴 S1 · size XS — filed 2026-09-09 (health alert 13:15 UTC; Andy: "s1 sprint 5" → moved to Sprint 4, it is a one-liner).** Repo `mds-digest-web`.

> **In plain words:** Make has three run outcomes — success, warning, error. We treat everything that is not success as an error, so a warning lights the dashboard red.

*As MDS staff, I want a red tile to mean something is actually broken, so that I do not learn to ignore the health alert.*

**Evidence it is real.** "Guest Multi-Event Alert (3+ events)" (Make scenario `4676457`) has read DOWN since 2026-09-02. Its only execution that day returned `status: 2`, and Make's own execution-detail endpoint reports that execution as `"status": "WARNING"`. `src/lib/tools-health/make.ts` does `Number(log.status) === 1 ? "success" : "error"`, and `classifyMakeTool()` turns `"error"` into `down`. The scenario is Airtable-triggered on a guest's third Ecom registration, so no clean run is coming to clear it — the red is permanent and the Slack "3 down" count is inflated by it.

**Shape of the fix.** Map Make's status codes as Make defines them (1 success · 2 warning · 3 error) and give warning its own display state instead of collapsing it into failure. This touches every Make-backed tile, not just this one: Luma Manual Add, Slack → Luma, the Stripe subscription syncs.

**Accept when:**
1. Guest Multi-Event Alert is no longer `down`, with no change made to the scenario itself.
2. A Make execution with `status: 3` still renders `down`.
3. A `status: 2` execution renders `degraded` and the tile text says warning, not failed.
4. A unit test in `make.test.ts` covers all three codes.
5. `tsc`, lint, tests and `next build` clean. Merge = Render deploy, verified on `/api/version`.


#### ✅ #179 CLOSED 2026-09-09 — shipped `0fcb6df`, merged `6a31026`, live on Render

**Story:** *As MDS staff, I want a red tile to mean something is actually broken, so that I do not learn to ignore the health alert.*

**Root cause, from Make's own API reference rather than from the ticket.** Make grades a finished execution
with a number: "1 is for success, 2 is for warning, and 3 is for error", and the execution-detail endpoint
spells the same three out as SUCCESS / WARNING / ERROR. `make.ts` read that number as
`Number(log.status) === 1 ? "success" : "error"`, and `classifyMakeTool()` turned `"error"` into `down`.
Guest Multi-Event Alert (scenario `4676457`) has one execution in its whole life, `3f286739…` at
2026-09-02T13:11:43Z, graded 2. Make's detail endpoint calls it `"WARNING"`. Verified live this session, both
the numeric grade and the string.

**The fix.** `makeRunStatus()` maps the grades Make documents, and a warning gets its own display state:
amber, worded "warning" rather than "failed", counted as degraded rather than down. An unrecognised grade
still reads as an error on purpose — Make also has a RUNNING state and may add more, and a false green hides
a real failure, which is worse than a false red.

**Before → after, the shipped code run against the live Make API, same data through both versions:**

| | Guest Multi-Event Alert | other three Make tiles |
|---|---|---|
| before | `DOWN` · `✕ failed 7d ago` | Luma healthy · Slack→Luma healthy · Stripe syncs healthy |
| after | `DEGRADED` · `⚠ warning 7d ago` | identical, byte for byte |

**AC checklist:**
1. Guest Multi-Event no longer `down`, scenario untouched — ✅ live run reads `DEGRADED`; nothing was changed in Make.
2. A `status: 3` execution still renders `down` — ✅ unit test, and so does any grade we do not recognise.
3. A `status: 2` renders `degraded` and says warning, not failed — ✅ live text is `⚠ warning 7d ago`.
4. Unit test covering all three codes — ✅ `make.test.ts`, 13 tests, plus the unknown grade, the pipeline roll-up and the real Guest Multi-Event case.
5. `tsc`, lint, tests, `next build` clean; merge = Render deploy verified on `/api/version` — ✅ 1270 tests pass, tsc/eslint/build exit 0, `/api/version` = `6a31026`.

**✅ The rendered tile is now verified too** (2026-09-10 01:35). It could not be reached at first — the report
endpoint 403'd on the stale `HEALTH_REPORT_SECRET`, the chore the cluster already carried. That chore was fixed
the same night (the endpoint now also accepts a Vault-held secret, so aligning it needs no deploy), and the live
report reads:

```
🟡 *Guest Multi-Event Alert (3+ events)* — ⚠ warning 8d ago (Sep 02, 2026)
*39* tools · 🟢 37 healthy · 🟡 2 need attention · 🔴 0 down
```

Amber, worded "warning", and **the down count is no longer inflated by it**. The other amber tile is unrelated
(Member profiles ← Airtable sync).

**Found alongside, NOT chased, no ticket filed yet — two repo traps:**
- **`node_modules` is a broken symlink committed into `mds-digest-web`** (`0b932ce`, 2026-09-08, mode
  120000, target `../../../node_modules` which resolves to `/node_modules`). `next build` dies on it with
  "Symlink [project]/node_modules is invalid, it points out of the filesystem root", and a worktree created
  *inside* the repo inherits it. Render is unaffected because its `npm install` replaces it. Workaround
  that works: put the worktree OUTSIDE the repo, as the #178 session did — `/Users/Born/wt-179-make-warning`.
- **Make's `pg[limit]` caps below 100 and fails silently.** `?pg[limit]=100` returns an empty
  `scenarioLogs` array rather than an error; 50 returns 50. The health checker asks for 1, so it is
  unaffected, but any future census code would read "no runs" and call a live scenario unknown.

### #180 · Millie's niche data has been frozen since 7 Sep — the nightly derive times out
**🟡 S2 · size S-M — filed 2026-09-09 (health alert 13:15 UTC; Andy: "s2").** Runs on the Mac launchd job `com.mds.olivia.derivations`.

> **In plain words:** the nightly job that works out what each member does has been failing for two days, so anyone who joined or changed their niche since Sunday is missing from those answers.

*As a member, when I ask who works in a niche, I want the answer to include the people who joined or changed niche this week.*

**Evidence it is real.** `digest.olivia_job_heartbeats`: `derive_niches` last succeeded **2026-09-07 09:31:39 UTC**, 53h before this alert against a 26h limit. It ran again **2026-09-09 13:50:02 UTC** and failed, so this is live, not a stuck flag. Heartbeat detail: `anthropic failed after 3 tries: curl exit 28` — curl 28 is a timeout. The run length is **growing**: 9,345s on 08 Sep, **12,657s** on 09 Sep, so it burns three and a half hours before giving up, nightly, for nothing. `digest.member_niches` holds 1,930 rows over 694 members with `max(derived_at) = 2026-09-07 09:31`. It feeds `profile_texts_for_embedding()`, `member_count()` and `chapter_info()`.

**Shape of the fix.** Find why one call runs 3.5h before timing out — batch size, a missing page bound, or a retry that re-sends the whole set each time — then bound the work per call and make a partial run **commit what it finished** instead of discarding it. Structural, not a longer timeout.

**Also fix while in here (folded in, not its own ticket):** the derivations tile prints the *freshest* of its four job heartbeats, so a failing job displayed as "last success <1h ago" on 2026-09-09 and read as a contradiction. It must print the oldest failing job.

**Accept when:**
1. `derive_niches` completes and `last_success_at` advances.
2. `member_niches.derived_at` is same-day after a run.
3. One run finishes inside a stated wall-clock budget, and that budget is written into the job.
4. A timeout on one batch no longer discards the batches that already succeeded — proven by forcing a mid-run failure.
5. The derivations tile shows the oldest failing job's timestamp, not the freshest.


#### ✅ #180 CLOSED 2026-09-10 — the job was fine, the machine was asleep

**Story:** *As a member, when I ask who works in a niche, I want the answer to include the people who joined or changed niche this week.*

**The ticket's three hypotheses were all wrong.** It proposed batch size, a missing page bound, or a retry
re-sending the whole set. The real cause: `derive_niches` is scheduled for **04:30 on a laptop that is closed and
asleep**. macOS wakes ~8s an hour for maintenance, so the job starts, gets a few seconds, and the machine sleeps
mid-request. Evidence, `pmset -g log` for both failing nights: sleep at 03:17, then hourly DarkWakes of 8-9s,
straight through 04:30.

That one fact explains every oddity at once:
- **3.5 hours of wall clock for ten model calls** — each call is capped at 120s, so the work cannot cost that.
- **The runner's `timeout=1800` never firing** — it measures a monotonic clock, which stops during sleep on Darwin;
  the reported elapsed uses wall clock, which does not.
- **Other jobs in the same file showing wild times** — `cache_member_photos` at 5,749s against a normal 106s.
- Reproduced the opposite way: the same script, unchanged, **awake: 2m30s, exit 0, 1,907 rows**.

**What shipped.** A failed model call no longer `sys.exit`s the run; it returns and the run commits what it
finished. A wall-clock budget (default 1500s) stops it starting new batches. Committing partially is **not** "write
the dictionary as it stands": the write DELETEs a member's rows first, and step 1 fills that dictionary for
everyone from controlled categories while only step 2 adds what they typed themselves — so writing everyone after
batch 3 of 10 would delete the stated niches of the members in batches 4-10 and replace them with the thinner set.
`writable_ids()` commits exactly the members who needed no model call plus the batches that completed.
**Also fixed:** `nightly_derivations.py` hardcoded `REPO = /Users/Born/Scorecard`, a working tree sessions switch
branches in — so "the live nightly script" was whichever branch was checked out. It now resolves from its own
location.

**AC checklist:**
1. `derive_niches` completes and `last_success_at` advances — ✅ `2026-09-10 05:49:19`, detail `done [93s]`, status `ok`.
2. `member_niches.derived_at` same-day after a run — ✅ 1,936 rows / 697 members, freshest today.
3. One run inside a stated budget, written into the job — ✅ 93s against the 1500s default.
4. A timeout no longer discards finished batches, **proven by forcing a mid-run failure** — ✅ forced a stop after
   batch 1: **893 rows rewritten for the 391 members it finished, 1,013 rows left untouched for the other 306, no
   member lost.** Exit 1, so the heartbeat still says error — saved data must never look like a clean night.
5. The tile shows the oldest failing job, not the freshest — ✅ `summarizeDerivations()`, 8 tests, live `e7c18d9`.
   Confirmed on the live report the same night: the derivations tile is **green**, so it no longer appears among
   the amber ones at all.

**Before → after:** niche data 3 days stale, nightly burning 3.5h for nothing, tile reading "last success <1h ago"
beside a DOWN status → data current, run 93s, a cut-short run keeps its work, tile names the worst offender.

**⚠️ Left open, needs Andy — this WILL recur otherwise.** The machine must be awake at 04:30. That means
`sudo pmset repeat wakeorpoweron MTWRFSU 04:25:00`, which needs his password. Tonight's run only succeeded because
the Mac was awake. **Moving these jobs off the laptop is #64.**

### #181 · 🅿️ SPRINT 5 · The events catalog is hourly on paper and four-hourly in fact
**🔵 S3 · size S — filed 2026-09-09 · CARRIES TO SPRINT 5 (Andy: "s3 sprint 5"). BLOCKED on a credential only Andy can create.**

> **In plain words:** the tile that watches our events data goes red most nights while nothing is wrong, because GitHub does not run its hourly schedule hourly.

*As MDS staff, I want the events tile red only when the catalog is genuinely stale, so that a real events outage is visible instead of buried in noise.*

**Evidence it is real.** `events-catalog-hourly.yml` declares cron `17 * * * *`. The last 14 runs **all succeeded** and were delivered between 2.4h and 5.6h apart. Of those 13 intervals, measured against `freshnessHourly` (healthy <1.75h · degraded <3.5h · else down): **0 healthy, 4 degraded, 9 in the down band.** The same measurement on 2026-07-29 over 60 runs gave 41% healthy; it is now zero. `olivia-at-sync` shows the worse of its two legs, so this is what reds the "Member profiles ← Airtable sync" tile — member_profiles itself is healthy.

**Shape of the fix.** Stop depending on GitHub's scheduler. Trigger the workflow from n8n via the `workflow_dispatch` API (n8n's cron is punctual to the second) and keep the freshness check as the backstop. **Do NOT widen the freshness bands** — that would hide a genuinely 4h-stale catalog that Millie answers events from.

**Blocked on:** a GitHub PAT with `actions:write`, created by Andy, stored as an n8n credential.

**Accept when:**
1. n8n fires the workflow every hour and GitHub's own schedule is removed or ignored.
2. Over 24 consecutive runs, the median delivered interval is under 1.75h.
3. The tile's healthy band is unchanged.
4. A failed dispatch from n8n is itself visible, not silent.

### #182 · 🅿️ SPRINT 5 · Five days of recordings are invisible to Millie — `GROUPOS_PAT` is missing
**🟡 S2 · size S — filed 2026-09-09 · CARRIES TO SPRINT 5 (Andy: "we hve weekly job, so its fine? decide for me" — it is not fine, see below). BLOCKED on a credential only Andy can create.**

> **In plain words:** the weekly video sync runs on time but skips videos entirely, because the token it needs is not on the machine. The cadence is fine; the credential is missing.

*As a member, when I ask about a recent call or session, I want Millie to find the recording rather than answer as if it does not exist.*

**Evidence it is real.** `digest.olivia_job_heartbeats`: `zoom_weekly` has been `degraded` since **2026-09-07 10:22 UTC** with detail `videos NOT synced (no GROUPOS_PAT, catalog newest 2026-09-02)`. `digest.videos_catalog` holds 1,084 rows with `max(synced_at) = 2026-09-04 16:21 UTC`. The job's `max_age_hours` is 216, so **staleness alone will never flag this** — the degradation exists only inside the detail string, which is why it went unnoticed. Recordings published since 2026-09-02 cannot be cited, linked or transcribed. The Public gate treats an unknown video as restricted, so this fails safe rather than leaking.

**Shape of the fix.** Create the GroupOS token, place it on the host that runs `zoom_weekly`, and make a **missing credential fail the job loudly** instead of degrading quietly past a 9-day staleness window.

**Blocked on:** a GroupOS PAT, created by Andy.

**Accept when:**
1. `videos_catalog.synced_at` is same-day after a run.
2. Every recording published since 2026-09-02 is present in the catalog.
3. A missing credential makes the job **error**, not degrade — proven by unsetting the variable once.
4. New recordings carry a populated `access_restriction`.

### #183 · The admin storefront reshuffles its tiles 10-15s after load, and the pinned band disappears
**⚪ S4 · size S — filed 2026-09-09 (Andy: "when uploading storefront, I see that the page loads the content for 10-15 sec and then changes the tiles' order. s4").** Repo `mds-digest-web`, follow-up to #164.

> **In plain words:** the storefront draws one layout, then rearranges itself in front of you once the health checks come back.

*As MDS staff, I want the storefront to settle into its final layout on first paint, so that I do not click a tile that moves out from under me.*

**Evidence it is real.** Andy's two screenshots of `digest.mds.co/admin`, the same page seconds apart:
- **During load** — header reads `9 tools · checking health…`; a **PINNED** band is present, `3 pinned · ★ to unpin`, holding Digest, WhatsApp and Millie; below it `ALL TOOLS · 6 unpinned`. Every tile shows `CHECKING…`.
- **After health resolves** (`HEALTH CHECKED 10:59:07 AM`, `9 tools · 4 healthy`) — the **PINNED band is gone entirely**, the header now reads `ALL TOOLS · 9 unpinned`, and the tiles sit in a different order, with Millie moved from the pinned row down to the second row.

So it is not only the health labels arriving late: the **pinned set is shown during loading and absent afterwards**, which is what produces the visible reshuffle. Root cause not yet established — reproducing it is the first job, not assuming it.

**Shape of the fix.** Decide the tile order from state that is known at first paint, and let the health result fill labels in place without re-sorting. Whatever the pinned set is, it must be the same before and after the health fetch resolves.

**Accept when:**
1. The behaviour is reproduced and the cause named in the ticket before any fix.
2. Tile order and grouping are identical before and after the health checks resolve.
3. The pinned band does not appear and then vanish; the pinned count is stable across the load.
4. Health results still update the tiles in place.
5. `tsc`, lint, tests and `next build` clean. Merge = Render deploy.

### #174 · A named item from her own list is a drill-down, not a new search
**🔴 S1 · size S — filed 2026-09-07 (Andy's "poor answers check", case 1 — prod turns 65488–65491, execs 137508 / 137515).**

> **In plain words:** when she lists videos and the member picks one by name ("tell me more about the Alex Chiru video"), she must open THAT video — not run a new search for the name and hand back another list.

*As a member who just got a list from Millie, when I name one of its items, I get the substance of that one item from its summary and transcript — not another list.*

**The miss, verbatim (prod 2026-09-07 20:47Z):** after a four-video answer whose pending offer was recorded (ids `69853b…`, `67f6e83d…`, `6a8866c0…`, `63e5b874…`; offer line "Want me to dig into any one of these further?"), Andy: *"Tell me more about Alex Chiru video"*. Router: intent `videos`, `accepts_offer:false`, `followup:true`. Plan Request: `offer_bind:null` — binding fires only on a yes-word (router), a bare affirmation, or the member echoing a word of her offer line ("further"); naming an item is not a recognised shape. Plan: `video_search p_query:"alex chiru" p_limit:8`; the model then called `video_search "Alex Chiru listing optimization"` and wrote a three-video cluster with a one-line blurb, ending "Want a quick summary of any one of these?". The 75-Character Title Update video carries a 904-char transcript summary and 9,673 chars of cliff notes on file; neither was fetched. The router could not have bound it either: `history_block` trims each turn to 500 chars and the Alex Chiru bullet starts at char 829 of the previous answer. **Not a regression** — Search 2.0 changed retrieval, #112 (23 Aug) bound yes/both/ordinals, #151 bound "which one for me"; the named item was never a bound shape. Same class in real traffic 26 Aug: "Summarize the Orkun one" (53868) and "Summarize the design impactful ai based creatives presentation" (53870) both re-planned as fresh searches and got the "could not confirm" line; bank C **#143** (3 fails).

**Shape of the fix (code, per code-beats-prompt):** ① `Format Reply` records each offered video's NAMING LINE — the line she wrote above its link (title + speaker as the member saw it) — as `pending_offer.items[{id,name}]`; Save Conversation and Prep Context already carry the whole object · ② `Plan Request` fourth acceptance signal `namedOfferItem()`: a message of ≤16 words that names ONE offered item by a capitalised word unique to its line (Chiru · Orkun · Gullo · Intellivy · a title word), with a drill-down cue (more · about · summary · cover · expand …) or two such words and no new-question opener (any · who · when · how many · is there …), binds to THAT item; the existing bound path then does the rest (zeroth fetch `video_search p_video_id`, no topic search). Two items sharing the words → both bound · ③ `Answer Seed` DRILL-DOWN variant of the OFFER ACCEPTED block: one item, deliver its substance (what it covers · the takeaways for what they asked · who / when / how long · its one link), no list, no "want a summary?". Offline unit test `scripts/olivia_loop/test_174_named_item.js` runs against the shipped node code (30 cases incl. the false-bind guards).

**Accept when:** Andy's exact chain on staging answers about the 75-Character Title Update from its summary with ONE link (`6a8866c0…`), the saved plan carrying `period:'offer_bound'` + `video_search p_video_id=6a8866c0…` and the execution's Plan Request showing `offer_bind.mode:'drilldown'` · a "summarize the <speaker> one" probe binds · #112 probes unchanged (yes · both · the second) · no pending offer = planning unchanged · two items sharing the name → she names both and asks which · gate GREEN · promote.

#### ✅ BUILT + STAGED + PROVEN 2026-09-07 — awaiting Andy's promote (staging `2d875cb3` = #169 Task 5 + #174 + #175)
**The fix:** `scripts/olivia_loop/apply_174_named_item_drilldown.py` — Format Reply records `pending_offer.items[{id,name}]` (the line above each video link, title + speaker as the member saw it) · Plan Request `namedOfferItem()` as the fourth acceptance signal, `offer_bind.mode` = `drilldown` | `accept`, a named item selects itself in `_poPick` · Answer Seed DRILL-DOWN block (one item, its substance, one link, no re-offer). Offline: `test_174_named_item.js` 30/30 on the shipped bytes. Applied to staging three times — the first two were wiped by the #169 session's whole-graph PUTs (the lock is host-level, handbook §13); the third rode the handover protocol.

| AC | result |
|---|---|
| Andy's exact chain answers about the 75-Character Title Update from its summary with ONE link · saved plan `offer_bound` + `video_search p_video_id=6a8866c0…` · Plan Request `offer_bind.mode:'drilldown'` | ✅ staging exec **137664** (rows 65563–65565): title · Alex Chiru & Jamie Graham · Aug 21 2026 · 1:01:08 · what it covers · five takeaways · one link; `offer_bind {mode:'drilldown', ids:['6a8866c0…'], named:["Alex Chiru – Amazon's 75-Character Title Update…"]}` |
| a "summarize the <speaker> one" probe binds | ✅ "Summarize the Fabio one" → exec 137633 `drilldown` `67f6e83d…`, the full Fabio Gullo summary (row 65519) · "tell me more about the title update one" → exec 137645 `drilldown` `6a8866c0…` (row 65537) |
| #112 probes unchanged (yes · both · the second) | ✅ "yes" → exec 137637 `mode:'accept'`, 3 ids, three summaries delivered (row 65525) · **"the second one" alone was never code-bound, before or after** (exec 137667: no `offer_bind`; the answer was still the second item via the seed's ANSWER THE THING ON THE TABLE rule) — see remainder |
| no pending offer = planning unchanged | ✅ after a reset, "Tell me more about Alex Chiru video" → exec 137647 videos lane, `video_search "alex chiru"` (row 65541) |
| two items sharing the name → both bound, she asks which | ✅ unit (cases 27–28); not exercised live |
| gate GREEN | ✅ 324 checks, EXIT 0 (22:42Z) |
| promote | ✅ prod `f5e9ce5d` 02:16Z, then `49d4a931` 03:14Z |
| **PROVEN ON ANDY'S OWN LIVE TURN** (not a probe) | ✅ **exec 138168**, 2026-09-07 22:23 CT, two minutes after his screenshot question: *"Tell me more travis video"* → `offer_bind {mode:'drilldown', ids:['69853b20…'], offered:2, named:["How Brands Turn Failed Creative Tests… — Peter-Paul Maan & Travis Klabon (Intellivy), Mogul Call, Feb 2026"]}` → `video_search p_video_id=69853b20…` → the full rundown of that one call (row 65943, 1,657 chars). The bind came off **"Travis"**, a co-speaker's FIRST NAME sitting mid-line in the recorded offer item — the exact shape of Andy's case 1, now landing on his real usage |

**Auditing note (cost me a false negative tonight):** `digest.olivia_messages.plan` does **not** carry `offer_bind` — row 65943 reads `plan->'offer_bind' = null` while execution 138168 shows `mode:'drilldown'`. Read the EXECUTION when auditing a bind; the saved plan shows only the resulting op and params (`p_video_id` is the tell).

**Before → after** on the failing case: prod turn 65491 — a three-video cluster with a one-line blurb, two bare links, plan `video_search "alex chiru"` → staging row 65565 — the one video, its substance, one link, plan `offer_bound p_video_id`. The bank C 26 Aug shape ("Summarize the Orkun one") now binds by speaker name. Probe rows cleaned by id (64 rows), never `--cleanup`.
**Remainder, in writing:** a bare ordinal ("the second one") reaches the model unbound — pre-existing, #112 reads ordinals only as quantifiers inside an acceptance; both live runs still answered the right item. Candidate for #143. The router still sees each history turn trimmed to 500 chars — left alone, the deterministic bind made it moot.

### #175 · The gate's link repair pins a URL to the wrong row — a bare, untitled link on every video answer
**🟡 S2 · size S — filed 2026-09-07 (Andy's case 1, the two bare links; "check backlog for more cases, address them one by one").**

> **In plain words:** after she drafts an answer, a safety step adds links for videos she named but forgot to link. It pairs each link with the wrong video, so the member gets bare, unexplained links to talks she never mentioned.

*As a member, every link in Millie's reply sits under the sentence that names it — I never get a bare link to something she did not mention.*

**Evidence (prod 2026-09-07, replayed on the real evidence blobs):** `Gate Verdict` #1b pairs each evidence URL with the last `title` in the 900 chars BEFORE it; a top-5 evidence row carries up to 3,200 chars of snippets between its title and its `video_url`, so the URL falls to the "after" fallback and is paired with the NEXT row's title. When that next row is named and linked in the draft, the previous row's URL is appended bare, before the closing question. Exec 137515 appended `65ef9f07…` (Building a Listing…, Prue Millsap 2024) paired with "Listing Optimisation Deep Dive", and `67e4836b…` (the restricted duplicate catalog row of the Inspire 2025 talk the draft had already linked, 8 of 10 title words); exec 137508 appended `63e5b874…` (Why Split Test?, Anthony Nguyen 2022) paired with "How Brands Turn Failed Creative Tests…". `link_coverage` 2 and 1; every LLM answer of Andy's that day carried a bare link. Format Reply's orphan stripper only drops TRAILING orphans and #1b inserts before the closing question, so they survive. The model's own drafts had none.

**Shape of the fix:** pair a URL with ITS OWN ROW — the row is the JSON object around the url field (between `[{` / `},{` and the next `},{` / `}]`); its title is the last `title` before the url inside that row, else the first one after it inside the row (url-first shapes); thumbnail / logo / image keys never pair; a candidate whose title shares ≥80% of its words with a row the draft already links is a duplicate and is skipped. Extracted as `linkCoverageUrls(evRaw, answerText)` in `Gate Verdict`, unit-tested (`scripts/olivia_loop/test_175_link_pairing.js`: the case-1 shape, the duplicate, url-first rows, image keys, the cap, the B5019 shape that #1b exists for).

**Accept when:** the unit test passes on the shipped node bytes · replaying the exec 137508 / 137515 evidence + drafts appends 0 URLs · a named-but-unlinked video still gets its link (B5019/B5021 shape) · gate GREEN · promote (rides the #174 graph).

#### ✅ BUILT + STAGED + PROVEN 2026-09-07 — awaiting Andy's promote (rides staging `2d875cb3`)
**The fix:** `scripts/olivia_loop/apply_175_link_pairing.py` — Gate Verdict's #1b pairing loop becomes `linkCoverageUrls(evRaw, answerText)`: the row is the JSON object around the url field (a bracket-depth walk — a nested `attachments:[{…}]` array no longer passes for a boundary, which is exactly what hid the public 684848cd row), its title is the first depth-0 `title` inside that row, image/logo keys are skipped, and a candidate whose title shares ≥80% of its words with an already-linked row is a duplicate. Insertion unchanged (max 3, before a trailing offer question).

| AC | result |
|---|---|
| the unit test passes on the shipped node bytes | ✅ `test_175_link_pairing.js` 14/14 on the dry-run of the live staging node |
| replaying exec 137508 / 137515 evidence + drafts appends 0 URLs | ✅ 0 and 0 (was 1 and 2), the nested-attachments row and the restricted duplicate included |
| a named-but-unlinked video still gets its link (B5019/B5021) | ✅ unit cases 2 · 3 · 8 · 12 (title-first rows, url-first Facebook rows, a nested-attachments row) |
| gate GREEN | ✅ same run, EXIT 0 |
| promote | ⏳ with #174 |

**Before → after:** Andy's four LLM answers on 2026-09-07 carried 1 · 1 · 1 · 2 gate-appended bare links (`link_coverage` on the prod Gate Verdict outputs); the 33-turn staging run on `2d875cb3` carried **0** — `link_coverage` absent on every Gate Verdict output.

#### ✅ Lap 2 — the OTHER repair (#1c, `registration_url` / `event_url`) — BUILT + STAGED + PROVEN 2026-09-08 (staging `b82f752e` → `c28fb532`)
Found while proving the verification batch (01:00Z): #1b was clean, but the #1c field repair appended two bare event links under the 2027 events list (exec 137901, `field_coverage 2`) and pinned "Register: https://go.mdsonly.co/MDSSummitSingapore" + the Summit's page to an answer about 2027 (exec 137902). Two causes: (1) #1c checked only the URL in hand — the draft had linked every event by its `reg_link` (`/s/events/u/…`, `go.mdsonly.co/…`) and the same rows' `event_url` came out bare; (2) its naming test ("same words, any order, contiguous") ran across "…not a repeat of Singapore:\n*MDS Summit Cancun 2027*" — a colon, a line break and a bold title — for a Summit that had already ended (`is_over:true`, `phase:ended`).
**The fix:** `scripts/olivia_loop/apply_175b_event_repair_precision.py` — `_nameInAnswer` matches per line / clause, never across punctuation; new `fieldRepairSkip(evRaw, idx, answerText)` → `linked` (any URL of the same row is already in the draft) · `past` (a finished event never gets a "Register:" line) · `''`; #1c skips accordingly.

| AC | result |
|---|---|
| replaying execs 137901 / 137902 appends 0 | ✅ 0 and 0 (was 2 and 2) on the patched bytes |
| a named, unlinked, upcoming event still gets its page | ✅ exec 137953 (row 65831): Cancun 2027, "(registration not yet open)", its `event_url` appended once (`field_coverage 1`); Inspire / Niseko / Centurion linked by the draft, nothing duplicated |
| a finished Summit is never pinned to a 2027 answer | ✅ exec 137954 (row 65833): no Singapore lines (was "Register: …MDSSummitSingapore" + page in 137902) |
| unit | ✅ `test_175_link_pairing.js` 33/33 on the live bytes (11 lap-2 cases: the cross-boundary naming, the same-row link, the go.mdsonly.co reg link, the finished event, the maps_url that never counts, escaped-JSON evidence) |

**#139 lap 2 rides here too** (exec 137957): the directory carries a partner literally called "TikTok Shop" (offer "TBA"); asked "Which MDS partner agencies handle TikTok Shop…", the draft named five agencies with their deals and pages itself and the #139 repair appended "TikTok Shop (TBA): …" because the draft says "TikTok Shop" in every sentence — the member typed it. `apply_139b_partner_ask_guard.py`: `linkCoverageUrls(evRaw, answerText, askText)` — a partner named in the member's own message is the subject, never a recommendation. 3 unit cases (33/33).

### #161 · Transcripts for the 33 videos published 25 Aug–4 Sep — AssemblyAI, in-person rooms
**🔴 S1 · size S — filed 2026-09-04 (Andy: "we need to create transcripts for recently fetched videos").**

> **In plain words:** 33 recent talks are in the library but Olivia cannot quote a word of them.

*As a member, when I ask what Kevan Soh said about PPC negation or which AI Mastermind talk covered
inventory forecasting, Olivia quotes the talk with a timestamp and the library link, gated by my
entitlement.*
Evidence: fresh GroupOS listing 2026-09-04 = 212 videos in 2026, 50 published since 25 Aug; 17 carried
transcripts (16 Summit AAI batch of 25 Aug + Josh Hadley via Zoom), **33 had none** — 16 AI Mastermind
(restricted), 8 AI Scaling Live + 4 Summit day-2 (public), 5 of them brand-new uploads not even in the
catalog (weekly check: NEW 5, CHANGED 1). Andy's 30 S3 links returned `403 AccessDenied` for every
anonymous GET until the dev changed the bucket policy the same day (all 30 → 206 afterwards). These are
in-person rooms: no Zoom, AssemblyAI is the only producer (Andy: Otter PDFs are NOT a source).
**Shape of the fix:** catalog upsert from the fresh dump · `aai_submit.py --year 2026` on a CSV built
from the listing (`download_link` = the now-public S3 URL, `_mds` block from the catalog) ·
`aai_transcripts.py --apply` · `video_summaries.py` now counts chunk-backed videos as transcript-backed
(it read `digest.calls` only, so every AAI batch had hand-written summaries) · embed · entitlement sweep
for the 5 new restricted videos · gate.
**Accept when:** 33/33 carry `call_transcript` chunks, max chunk ≤ 4,000 chars, timestamps monotonic ·
33/33 have `summary_source='transcript'` and a vector (0 unembedded) · the 5 new restricted videos have
`video_access` rows (members-per-video > 0) · live probe through `content_search_v2`: an entitled asker
gets Kevan's quote with a timestamp + `app.mds.co/videos/6a95ecb56c44f146b77f4941`, an unentitled asker
gets nothing from an AI Mastermind talk · gate GREEN, exit 0.

### #119 · Bank B — a regression bank for everything built after the 100-question bank froze
**🔵 S3 · size M — filed 2026-08-23 (Andy, during the #108 close: "wow. old… we need one more bank around everything we built since then").**

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
**🔵 S3 · size M — filed 2026-08-21 from Andy's Slack ruling to Eugene · ⏸ sequenced AFTER the big smoke test**

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

### #157 · Review the Sonnet 5 vs GPT-5.6 Terra bench — the vendor call
**🔵 S3 · size S** · filed by Andy 2026-09-02 ("this task is completed; file S2 ticket to review it")

> **In plain words:** Andy reads the #156 comparison and rules whether Olivia stays on Claude, moves to OpenAI, or gets one more test first.

*As the owner paying Olivia's API bill, I want to review the 92-question comparison (`OLIVIA_MODEL_COMPARE_2026-09-02.md`: both judges, cost per answer, latency, the 42 judge disagreements, all answers side by side) and record a ruling, so the next ticket is either "stay", "port the answer loop to OpenAI", or "re-test with X".*
The data (#156 close block, Sonnet judge): Sonnet 5 **5.4%** fail / **$0.0211** / 10.1 s · Terra medium **3.3%** / **$0.0310** / 19.4 s · Terra none **7.6%** / **$0.0237** / 14.2 s. Terra judge: 13.0 / 9.8 / 13.0 — it fails honest-miss answers the rubric marks PASS, so read the disagreement section before the headline. Caveats: Claude-tuned prompt · Answer Merge evidence stamps and post-model gates not replicated · Terra-medium's 8,000 output budget vs 2,000.
**Shape of the work:** reading + a ruling, no code. Optional re-tests the harness already supports (`scripts/model_bench/README.md`): a GPT-shaped prompt variant re-run (~$12) · `gpt-5.6-luna` / `gpt-5.6-sol` runs · Terra at `low` effort · a second Sonnet run to measure judge noise.
**Accept when:** Andy's ruling is written on this ticket (stay / port / re-test with what) · if "port": a new ticket with story + ACs for the n8n answer-loop port (Responses API shape, full through-workflow eval before any promote, OpenAI tier raise for prod traffic) · the OpenAI key pasted into chat on 2026-09-02 is rotated.

### #161 · MDS Personas — a staff library of members: browse faces, open a character sheet, click a stat to find everyone strong in it

**✅ SHIPPED 2026-09-04.** Built locally first (Andy: "let's start with local first"), then promoted on his call: both repos merged to `main`, mds-digest-web `main` = Render deploy `e212bcf`. Live at `digest.mds.co/personas`, staff gate on every route.

**What shipped (branch `personas-20260904` in BOTH repos).** mds-digest-web: `/personas` Library v2 (sticky top bar · Browse mega-menu with live strength counts · 10-banner swipeable hero · 172×258 poster cards with hover preview · 13 rails, hidden scrollbars, hover arrows, lazy images + below-the-fold rails · search grid · staff gate) · `/personas/[id]` character sheet (portrait, blurb, focus, gives/asks mapped to stats, 18 categories + 33 detail stats as today/peak with at-peak/holding/fading, similar + companions, all collapsed by default, legend "?" popover, independent-scroll aside) · `/personas/stat/[key]` cohort (≥ 60, poster cards, one number) · states, phone layouts, light theme · 358 tests. Scorecard: `personas_stats` view + RPCs `personas_library/sheet/cohort/related/strong/fading/topic_peaks` (service_role only, exported to `db/`) · `member_photos` + Storage `member-photos` via nightly `cache_member_photos.py` (GroupOS avatar → Airtable ≥ 120 px → initials; 639/760, 121 no source) · `persona.blurb` via nightly `persona_blurbs.py` (Haiku 4.5, 758/758, ~$0.45) · gate +10 personas checks = 323/0.

**AC checklist.** Every active member opens (760) and all 51 stats render or are named silent — met · photos from Storage only, none from Airtable (gate check) — met · similar/companions match SQL (5 spot checks in review) — met · pixel review vs handoff at 1440/390 both themes — met (v1 + v2 screenshots in the SDD workspace) · anon refused on every route/RPC — met (gate). Before/after: 0 → 3 screens · photos 0 → 639 · blurbs 0 → 758 · gate 313 → 322.

**Andy's rules applied (2026-09-04, override the READMEs):** collapse all by default · compact legend + "?" popover · stats fonts +20% · aside scrolls on its own, scrollbar hidden · "MDS member since YYYY" everywhere · rails: no scrollbars, arrows on hover · hero 10 swipeable · one number per stat card, tooltips on badges · every number truthful (hero k = per-topic peaks, 164 → 92).

**Process (what the reviews caught).** 4 bugs in the plan's own code (blurb cap, peak rounding, real names in fixtures, hero substitute count), 1 real regression (loading.tsx turned 404s into 200s), 1 duplicate-DOM defect (Suspense fallback with its own top bar), and the final whole-branch review (Opus) found a production-build breaker nobody had exercised (module-scope `notFound()` on the dev components page — `npm run build` now exit 0), a false "joined this quarter" claim (90 of 121 New-Member rows were older), two hero sentences the SQL never checked, and a blurb heartbeat that could never go red. All fixed and re-reviewed. Ledger: `.superpowers/sdd/2026-09-04-mds-personas/progress.md`.

**Open, filed:** #163 scoring review (number semantics, strong = top 40% of scored members, cohort floor 60, asks∩gives, detail-stat asks never surface companions) · Facebook profile-photo capture in the FB extension runs (own ticket, Andy 2026-09-04) · GroupOS roster sweep only half done (72 avatars) · Playwright/Chromium-only verification.

**🟡 S2 · size L — filed 2026-09-04 after a brainstorm + 7 live drafts (artifact 0af65aff) and a Claude Design handoff (`~/Downloads/Member 360 Admin Design System.zip`).**

> **In plain words:** Member 360 is the audit view; nobody browses it. Andy wants a page that feels like a
> streaming library: one search bar, rows of faces, click a member and read a short friendly sheet with
> game-style stats (the 18 categories and 33 detail stats with their decay), click any stat and see who
> else is strong in it, plus who is similar and who would be a good companion.

*As MDS staff, I open Personas, find a member in seconds, understand them in twenty, and jump from any strength to the people who share it — without opening Member 360.*

**Decided:** staff only (scores visible) · all 758 actives · no A-vs-B compare · no archetype labels · all 51 stats
visible, silent ones named · asks/gives mapped to stats from the ledger evidence · badges at peak / holding / fading
(no rising until the ledger keeps history). Design is FINAL in the handoff (tokens, components, states, responsive).
Spec: `docs/superpowers/specs/2026-09-04-mds-personas-design.md` (data, RPCs, photo cache, blurb, gating).

**Accept when:** `/admin/personas`, `/admin/personas/[id]`, `/admin/personas/stat/[key]` live on Render behind the admin
gate · every active member opens and every one of the 51 stats renders or is named "no signal" · photos served from
Storage (nightly `cache_member_photos.py`), never from Airtable links · similar + companions computed in SQL and
spot-checked for 5 members · pixel review against the handoff at 1440 and 390 in both themes, all README states ·
anonymous requests to the routes and RPCs refused · `blurb` written by the persona job (fallback: summary sentences).

### #159 · Partners and events go dark in meaning search — 75 partners without a vector, and the weekly delta misses edits
**🔴 S1 · size S — filed 2026-09-03 (Shea Smith, 28 Aug: "Who should I use for bookkeeping?" — Prosperlytics, 5.0★ from 5 reviews, 51 claims, never appeared).**

> **In plain words:** when a partner edits their page, their search vector is wiped on purpose and nobody
> rebuilds it, so the meaning search cannot see them. The popular partners edit their pages, so the popular
> partners go dark: 74 of 496 in the lookup pool, holding 35% of all reviews and 48% of all claims. And the
> weekly GroupOS listing caught 114 of the 142 partners that changed between 3 Aug and 2 Sep.

*As a member, when I ask Millie for a partner, the best-rated partner for that need is in her list — a partner editing their own page cannot make them disappear.*

**Evidence (2026-09-03):** keyword lane ranks Prosperlytics #1 for "bookkeeping accounting" and the preload the
model saw listed it first; the `partner_lookup` call with the Voyage embedding attached returned 8 partners without it
(staging exec 131231, same graph as prod `d40a837d`). RRF gives a vectorless partner one list instead of two: 0.016 vs
0.030. `partners_embed_invalidate` nulls the vector on any name/description/offer/category change (#26, July); the
nightly `embed_content` step covers `content_items` only; `embed_partners_events.py` was a one-off in `~/mds-scorecard-tools`.
Handbook §B claimed "the nightly re-embed picks it up". Dark rows: partners 75 (since the 1 Aug sync), events 36.
Weekly delta: GroupOS `updated_after` works (direct call returns Prosperlytics); the scheduled session's paging stopped at 114.
The listing endpoint breaks on 2 records when they fall inside a page (Fathom, Onsite Support — `partners_get` serves both).

**Accept when:** 0 published-public partners and 0 events without a vector (backfill) ✅ · nightly chain step `embed_catalogs`
re-embeds both catalogs (heartbeat row) · `partners_weekly_check.py --apply` re-embeds NEW/CHANGED rows in the same pass ·
weekly task pages until `has_more=false`, checks `with_total` against rows fetched, window = last success − 3 days; the 28
missed partners caught up · gate check "published partner/event without vector = 0" · Shea's question on staging lists
Prosperlytics · handbook line corrected · SKILL.md of the scheduled task updated.

**Results 2026-09-03 (CLOSED, no promote needed — data + scripts only):** backfill `scripts/embed_partners_events.py` (moved from `~/mds-scorecard-tools`): partners 75 + events 36 embedded, dark 0/0 (SQL). Nightly `embed_catalogs` step in `nightly_derivations.py` (heartbeat seeded, max 26h). `partners_weekly_check.py --apply` re-embeds NEW/CHANGED in the same pass and fails loud. Gate +2 checks (partners/events without vector = 0; the gate's own `redteamevt_*` fixtures excluded) → 313 PASS · 0 FAIL · EXIT 0. Scheduled task SKILL.md: page until `has_more=false`, `with_total` check, window = last success − 3 days, the two records that break the listing endpoint named with the `partners_get` workaround. Handbook §B line corrected. **Proof through the RPC:** `partner_lookup_v2('bookkeeping accounting')` with a real Voyage query vector → Prosperlytics #1 (rank 0.0323); before: absent from the top 8 (staging exec 131231). Staging re-ask names Mudit/Prosperlytics first.
**AC checklist:** dark 0/0 ✅ · nightly step ✅ · weekly re-embed ✅ · paging + total ✅ (instructions; first real run = next Sunday) · gate check ✅ · Shea's question lists Prosperlytics ✅ · handbook ✅ · SKILL.md ✅. **Before/after:** dark partners 75 → 0 · events 36 → 0 · Prosperlytics rank for "bookkeeping accounting": absent → #1.

### #163 · Personas scoring review — what each number means, and why nobody looks below 60

**Story.** As MDS staff reading a member's Personas sheet or a "Strong in X" page, I want every number to mean one clear thing, so that I trust what I see and can explain it to a member. Andy, 2026-09-04, while reviewing #161: "we need to clarify what each number means" and "the worst performer in each category never goes below 60 — file it, we will check these things later, the whole scoring system".

**What we already know (2026-09-04).**
- The cohort page ("Strong in X") lists ONLY members at value ≥ 60 by design (spec: cohort = strong), sorted desc — so the last card on any cohort page is always ≥ 60. The full distribution lives in `digest.personas_stats` (`value` = community percentile 0–100 from `member_expertise.pct`) and the sheet shows the low values too (e.g. Listing optimization 11/28, Walmart 6/15).
- Two numbers on a stat-rail card: top-right = the member's LEVEL (mean of top-3 categories), bottom-left = the RAIL'S stat value. Same gold style, no label — confusing.
- Sheet numbers: `today/peak` per stat, badge (at peak · holding · fading = today vs 85% of peak), "Rank #n in the community" (rank_in_topic), level badge on the portrait, similar % = cosine over 18 category values.
- Browse-menu counts (v2 home, 2026-09-04): members ≥ 60 per category = 209 AI · 270 Logistics · 265 DTC · 243 Sourcing · 225 PPC of 760 — because `value` is a percentile among scored members, "strong" (≥ 60) is simply the top ~40% of whoever has any signal. A category with 675 scored members has ~270 "strong" members. Decide whether strong should be an absolute evidence bar instead.
- Ledger oddities to look at: evidence "peak floor applied" (peak_score floor for thin evidence); a member can be both ask and give on the same topic (Mo Kuhail: Amazon FBA); values are percentiles, so a category with few scored members still spreads 0–100.

**Analysis run 2026-09-04 (live ledger, Andy: "let's check the scoring system").**
- **The displayed number is a rank, not a strength.** `pct = 1 - percent_rank()` per topic, so every category is uniform by construction: median 50, p90 90, ~41% at 60+, in all 18. Andy's "nobody goes below 60" = the cohort filter sitting on a uniform scale.
- **The bar is near the median member.** Amazon FBA: value 60 = score 1.05 while the median score is 1.04 and the top is 20.50 (value 80 = 1.85). TikTok Shop: 60 = 2.47, 80 = 4.06, top 32.92. 276 of 3,434 "strong" rows (8%) have only a form answer as evidence; 92 of those sit at 80+.
- **Breadth is real and concentrated.** 103 of 742 scored members are strong in 10+ of 18 categories, 27 of them in 14-18 (averaging 13 categories at 80+); 289 are strong in 0-2. 61 distinct members hold the 180 top-10 slots, 24 hold the 54 top-3 slots.
- **The cause is the video channel.** Members strong in 14-18 categories carry video evidence on 56% of their topic rows vs 3% for the strong-in-1-5 group (conversation evidence is flat: 23% vs 7%). One video matches 4.6 topics on average and up to 17 of 18, and each video pays 3.0 points **linear** (cap 5 = 15) in every topic it touches while every other channel is logarithmic. Business text is not the culprit (1.6 topics avg, max 4); posts/comments average ~2 topics.
- **Fix 1 simulated on the live ledger** (share each artifact's credit across the topics it matches, log-scale videos): distinct members holding the 180 top-10 slots 60 → 87; members top-10 in 5+ categories 15 → 7; max categories for one member 11 → 8. Movers: Bryce Alderson 11 → 2, Saurabh Srivastava 8 → 0, Damon Sununtnasuk 7 → 0, Josh Hadley 8 → 2, while the writers hold or rise (Jonathan Jewett 7 → 8, Brandon Himmel 6 → 7, Corey Smith 4 → 5). Simulation swapped only the video term on the stored score and re-ranked the 18 parents; peak floor and the 33 detail stats untouched.
- **Assessment (Andy asked for the verdict).** The architecture is right: an explainable evidence ledger in SQL with decay and a peak floor. The inputs all measure *visibility*, not competence, so the output is a participation index presented as expertise. Three amplifiers: boolean matching pays a passing mention like a deep thread; the revenue multiplier is category-blind (1.5× on Legal & IP for a 20M seller); the percentile display throws away distance. And there is **no ground truth anywhere** — the verifier checks mechanics, not accuracy — so every tuning argument today is taste.
- **Agreed next step (Andy, 2026-09-04 evening): measure before tuning.** (1) Mine proxy truth we already hold: "who should I ask about X" threads (the community naming a person for a topic) and MDS speaker/panel assignments. (2) **Web test** on ~100 members: the 61 who hold our top-10 slots plus a control group of ~40 scoring near zero. Count only third-party placements (podcast guest spots, outside conference sessions, quotes, paid teaching) — never self-published claims, which would re-inflate breadth. Gate identity on brand + city, decay old appearances. If the control group is full of people with topic credits we scored at zero, the formula measures the wrong thing and weight tuning will not save it. Pattern and cost are known from #160 (506 partner sites via cheap subagents). (3) Only then the formula changes, each with before/after on the proxy set and on Millie's eval bank — the ledger feeds her advice lanes, not just Personas.
- **No history exists.** `derive_member_expertise()` deletes and rebuilds nightly; only `peak_score` survives. Change over time cannot be measured until a monthly snapshot table exists (also why there is no "rising" badge).

**Phase-1 plan (written 2026-09-04): `docs/superpowers/plans/2026-09-05-expertise-truth-set.md`** — truth table, 101-member web test with a control group, per-topic precision/coverage/blindness, then the formula work.

**Acceptance.**
1. One page (in `OLIVIA_HANDBOOK.md` or a `PERSONAS_NUMBERS.md`) defining each number in one sentence, with the SQL that produces it; the in-app "?" help on the sheet uses the same words.
2. Stat-rail cards label the two numbers (or drop one) — no unlabeled gold numbers.
3. A distribution report per category: members with signal, min / median / p90 / max of `value`, count ≥ 60 — reviewed with Andy; decision on the cohort floor (60 vs top-N vs show-all-with-signal).
4. Any change to the scoring itself (percentile method, peak floor, decay) is its own ticket with before/after on the eval bank.

### #164 · Admin storefront + seven self-contained tools

**🟡 S2 · size L — filed 2026-09-05 (Andy: "i also want to redesign our digest portal").**
**Owned by the `Digest Redesign` session, repo `mds-digest-web`.** The #163 session does not touch it.

**Story.** As an MDS admin landing on the admin surface, I want a storefront listing every tool and
letting me find the one that answers my question, and I want each tool to own its own navigation and
its own help, so that the surface teaches itself instead of making me hunt a shared nav bar I did not
build.

**Origin.** Design handoff `Admin tools storefront design.zip`, unzipped to
`~/Downloads/design_handoff_mds_admin/`. Seven high-fidelity HTML design references plus one brief per
screen. The references are prototypes, not production code — the job is to rebuild them in
mds-digest-web's own primitives, not to port inline styles.

**Scope.** Seven screens in the handoff's build order: Admin Storefront · tool covers · WhatsApp
(merges three existing pages into one tabbed tool) · Facebook Group · Member 360 · Millie · Tools
Health. `mds-digest-web` has no staging tier — a merge to `main` IS the Render deploy.

**Acceptance.**
1. The seven shared components are built during screen 1 and reused by every later screen, not
   regrown per screen: ToolHeader, HelpPanel, StatTile, DataTable, Popup, PeriodSelector, FilterPills.
   The handoff names this as the single biggest risk in the pack.
2. The interaction rules hold on every screen, because they are the design: clicking a number opens a
   popup over the page and never navigates away; every table sorts both directions; every list has an
   empty state; every count derives from the data and agrees with the table under it, including under
   an active filter; classifier chips are editable and a manual change is never overwritten by a later
   run.
3. One screen per session, seven sessions minimum. Each closes with its screen proven in the running
   app, not asserted.
4. The handoff's six open questions are answered by Andy before the screen that depends on each —
   endpoints per screen, the real Tools Health scope (header says 38, list holds 41), whether WhatsApp
   and Millie link out to Member 360 or keep scoped member views, the Millie rename reaching
   WhatsApp-facing copy, the merged WhatsApp tool name, and where per-admin pins and per-tool help
   docs live.
5. Old WhatsApp URLs redirect to the merged tool's tabs.

**Not in scope.** SOP videos do not exist yet — every help panel ships with the empty 16:9 slot. Tool
cover artwork is CSS, standing in for real illustrations that drop into the same slots later.

### #165 · The Personas sheet does not explain itself

**🟡 S2 · size M — filed 2026-09-07 (Andy, after reading Ryan Pace's sheet: "Basically, I feel like
it's a very cool page, but I have no clue what is going on" · "page should be clear so others can use
it. we need to revise the logic and make page cleaner").** Repo `mds-digest-web`; ticket detail in that
repo's `docs/PERSONAS_OPEN_QUESTIONS.md`.

**Story.** As MDS staff opening a member's Personas sheet, I want every block to say what it is and
where it came from, so that someone who has never seen the page can read a member without being told.

**What the source actually says (traced live 2026-09-07, answering the ticket's own open question).**
`digest.personas_sheet(p_id)` returns `focus`, `gives_text`, `asks_text`, `summary`, `blurb` and
`pattern` straight out of `digest.member_personas.persona`. That jsonb is written nightly by
`persona_refresh.py` (`~/mds-scorecard-tools`, launchd `com.mds.persona.refresh` 04:15) using Claude
Haiku 4.5 — 766 rows, newest built 2026-09-06. Its prompt weighs Millie questions from the last 90
days first, then authored WhatsApp and Facebook posts and comments, then confirmed event attendance,
then chat. **So FOCUS, GIVES and ASKS are inferred from behaviour, never member-stated** — which makes
the current "In their words:" heading over the gives/asks prose false. The chips are a different
thing under the same heading: `personas_stats` rows whose `evidence` carries `persona_gives_hits` /
`persona_asks_hits` (plus `weakness > 0` for asks), i.e. that same inferred text matched against the
taxonomy.

**Acceptance.**
1. FOCUS RIGHT NOW, GIVES and ASKS each name their source and meaning on screen. "In their words"
   goes or becomes honest.
2. The 11 silent categories render as ordinary zero rows, not the grey `No signal yet on: …` footer —
   Andy's explicit ask: a zero is data, and the sheet should be all 18 categories, not an edited 7.
3. "Top 6" renamed or reworked. It reads as a filter and is an expand control (`i < 6` decides how
   many rows start open); it never filters anything.
4. The ledger showing its working — the rank line, the evidence-channel counts, the nested zero
   sub-stats — moves behind the help layer instead of leading the read.
5. Field-by-field provenance written down in the repo; kit rules hold (every number derives from
   fetched data, every colour a token); `tsc`, lint, tests and `next build` all clean.

**Also settle.** Is Ryan Pace's Member 360 (`/admin/member360/recG2hA8WPuJJ873i`) broken or correctly
empty? Working hypothesis is correctly empty — a New Member who joined 2026-08-31 with no activity —
but Andy added a Stripe subscription id after the page was last read, so re-check rather than conclude
from the old render.

**Coordinate with #163**, which is reviewing whether these numbers are RIGHT. This ticket is whether a
reader can tell what they ARE. No formula ships from #163's current phase, so the numbers do not move
under this work.

**Handed to the scoring (#163) session 2026-09-07** (Andy: "transfer 165 updates to Scoring system
agent, ill work on it there"). The first build (`50c7a4a` on `165-personas-sheet-20260907`, unmerged)
covers ACs 1–5. Andy then read Corey Smith's live sheet and the ticket grew a sixth AC.

**Rulings 2026-09-07 (Andy, reading the live sheet).**
- *"all these bars mean nothing. The whole purpose of this thing is for me to see the current score,
  his max score, and what percentile he is at."* Traced live: the sheet showed **no raw score
  anywhere** — both numbers in a row like `40/59` were percentiles, and `personas_stats.peak` is
  **fabricated** (`LEAST(100, round(value × peak_score ÷ score))`, a projection, not a percentile the
  member ever held). A percentile's median is always 50 and its max always 100, so it cannot express
  distance: Corey's Attribution 36 vs Aggregators 51 looked like a modest gap while the real scores
  were 0.42 vs 1.41.
- *"use the median"* — the bar's reference line is the community median score for the topic. This
  supersedes the earlier "keep the line at 70" call, which was made before anyone knew the 70 is
  `left: "70%"` with a hardcoded label (`StatBar.tsx:34`) tied to no data.
- The two grid icons in the Personas header stay as they are ("Leave it").
- *"build it locally"* — nothing merges until Andy has looked at it.

**AC 6 (added 2026-09-07).** The stat bar is absolute: the axis runs from 0 to the topic's community
top, the fill is the member's score today, a tick marks their recorded peak score, and the reference
line is the community median. Each row prints score today over peak score, with the percentile and
`rank of pool` beneath (so "19 of 38" stops reading like "150 of 233"). The "60 and above is strong"
sentence goes and no new threshold is invented — whether a percentile is the right headline at all is
#163's call, measured before and after. Build: DB half `aa9953f` on `165-personas-numbers-20260907`
(`personas_stats` +`score_today, score_peak, pool, topic_top, topic_median`, append-only, every
pre-existing column byte-identical across all 16,932 rows, gate exit 0); web half on
`165-personas-sheet-20260907` — `98f40ba` absolute bar → `e57f874`, `d452061` copy → `04b2675` final-review
fix wave. **AC 6 BUILT + REVIEWED 2026-09-07, then superseded by phase 3 below and PROMOTED.** Opus whole-branch review: fit to merge
with fixes; the real one was a phone break (≤640px rule still sized for "100/100", score painted over the badge
on every row at 375px) — fixed, re-review measured 17.0 / 15.5px clear itself. tsc clean · vitest 900/900 ·
`npm run build` exit 0. Deferred on purpose: "0th" on 10 bottom rows · `pool` counts 349 zero-score rows the
copy calls "signal" (#163's wording) · `personas_sheet` ~89 ms · pre-existing name ellipsis at 375px.
**Phase 3 (same day, `aa47d70` + phone fix `f2975cb`) — Andy read phase 2 and could not** ("humans will not read
18.62/18.69 · 100th · 1 of 461 … median barely visible … these end arrows … no clue how to read it"). Approved from
an inline mockup: **rank is the headline (`#19` / `of 38`), raw numbers on hover, log-scale bar, one dashed
typical-member mark, no today marker, ghost only when fading, legend once.** Data untouched. Reviewed on Corey and
Ryan Pace (#182–#475, every fill/mark matches the formula); the review caught a phone regression (27 of 51 names
truncated, an empty grid row) — fixed to parity with 04b2675 (3 of 51, all pre-existing), re-review measured it.
901 tests, tsc clean, build 0. **PROMOTED 2026-09-07 (Andy: "lets promote it"): web `main` b44e2d7 → Render
`/api/version` b44e2d7 live; Scorecard `main` 4e111c1.** Rebased on the moved mains first; after the web rebase
crossed 11 commits (shared `personas.css`) the branch was re-verified: tsc clean, vitest 1087/1087, build exit 0.
Open follow-up, Andy's call: the dashed typical-member mark gets its own hover text — he asked what the line meant
after the legend had said it.
**Phase 4 (same day) — `self-reported` / `observed` tag on every persona line — LIVE, web `main` `18bac76`** (Andy:
"add self-reported vs observed labels on the card", after Luke Li's 3 gives all traced to a form). Classifier
`signalSource.ts` from the pointer's source word, per `;`-segment, hyphen-bounded, census-key fallback; legend per
section; one help sentence; chips untouched. Reviewed twice (30/30/30 hand audit; all 10,202 pointers re-run through a
port of the shipped code — splits digit-for-digit; the one precision bug, `post-scaling` matching `post`, fixed with
zero regression). Gives community-wide: 987 self-reported / 1,742 observed / 118 untagged. Merged `556b168`.
**Phase 5 — human sentence in the "Written from" hover — PARKED on `parked/165-sentence-hover-20260907` (mds-digest-web, = `bf1ab62`). DO NOT MERGE.** Working branch, worktree and dev server removed; anything under `parked/` is not in flight (`ff4f234`, `bf1ab62`): only ~26% of
pointer segments have enough structure to rewrite; two review rounds each surfaced a new free-prose shape and `bf1ab62`
garbles 7 bracketed-list values. Stopped on Andy's "pause". Real fix = structured pointer in the persona prompt.

**Findings that belong to #163, not here** (from the first build; reported, untouched): 1,016
detail-stat rows across 503 members score under a zero parent · the scorer weights posts highest (2.0)
but 0 of 16,762 ledger rows carry a posts evidence key, so the heaviest weight in the formula may be
dead · `personas_sheet`'s asks filter `or weakness > 0` is redundant (weakness = ln(1 + asks_hits); 0
disagreements) · the ticket's premise was half wrong — 2,407 of 4,960 focus signals cite the member's
own census/application answers, so the *signal* is often the member's words even though the *line* is
always the model's paraphrase.

### #166 · Personas and Digest have no tool switcher

**🟡 S2 · size S — filed 2026-09-07 (Andy, seeing the switcher list its own Personas row as "NO
PAGE").** Repo `mds-digest-web`; detail in that repo's `docs/ADMIN_OPEN_ITEMS.md`, "Navigation".

**Story.** As an MDS admin inside Personas or the Digest dashboard, I want the same grid button every
other tool has, so that I can move to another tool without bouncing off the storefront and picking
again.

**Why these two missed it.** #164 gave all seven tools a `ToolHeader` carrying `ToolSwitcher`. Personas
has its own top bar — it predates the redesign and lives outside the `(tools)` route group — and
Digest is `/dashboard`, the member portal. Personas has a `← All tools` link, which is the exact round
trip the switcher exists to remove. The switcher is one shared component
(`src/components/tools/ToolSwitcher.tsx`), so this is giving two headers access to it, not rebuilding it.

**Acceptance.**
1. The grid button appears in both headers and opens the same switcher the seven tools use.
2. Keyboard behaviour matches the seven: 1–7 to jump, Escape closes, current tool marked.
3. No kit primitive is rebuilt; every colour a token.
4. `tsc`, lint, tests and `next build` clean, and both headers proven in the running app.

### #170 · Millie web chat — long thread memory + many chats

**🟡 S2 · size M — filed 2026-09-07 (Andy: "File it, will do").** Depends on #169's door and table.

**Story.** As MDS staff, I want to keep several chats with Millie and come back to any of them, and I want her to
remember the whole thread — not just the last 16 turns — so that a long investigation can continue over days
without me re-explaining it, at a per-question cost that does not grow with the thread.

**Why it is not in #169.** Today's memory is the last 16 turns, 500 characters each, roughly 8,000 characters.
Andy: "if its just 8k or 24h window, then i se no purpose for this section." Real memory needs three pieces:
recent turns verbatim (as now) · a running Haiku summary of everything older, refreshed after each answer (≈ a tenth
of a cent per question, flat) · a `web_thread_search` tool she calls for exact earlier passages (costs only when
used). Plus the sidebar: threads per mode, titled by the first question, New chat.

**Acceptance.** 1. A thread of 100+ turns answers "what did we decide earlier about X?" correctly from the
summary or the tool. 2. Per-question cost on a long thread is within 10% of a fresh thread. 3. ~~Sidebar lists the
caller's own threads per mode, newest first; New chat starts one.~~ **ALREADY DELIVERED by #169 — see below.**
4. The tool is reachable only for web turns and only for the asker's own thread (server-injected `thread_id`, like
`p_phone`); gate proves WhatsApp turns cannot call it. 5. New table `digest.olivia_web_threads` (thread_id,
asker_email, mode, title, summary, updated_at), service_role only.

#### 📐 SCOPE CHECKED against live 2026-09-11 (Andy: *"this is already happening, or is the idea here different?"*) — **half of this ticket shipped, the other half has not started**

**Shipped, in #169, deliberately:** the sessions rail in the screenshot — New session, Search sessions, per-mode
grouping, a session count, and reopening a thread with its provenance intact. `src/lib/millie/web-chat.ts`
(`listThreads`) says so in its own comment: *"Millie's LONG memory of a thread (running summary + search tool)
stays #170; the rail itself ships here because the design is built around it."* It is derived from the caller's own
`olivia_web_messages` rows — no model call, no extra table. **So AC 3 is done and must not be rebuilt.**

**Not started — and this is the whole remaining ticket: MEMORY, not navigation.**
- The prod graph's `Load Recent Turns` reads **`limit=16`**. Sixteen turns is all Millie remembers of a thread.
- `/api/admin/millie/chat` sends the door **no history at all** beyond `thread_id` — the web side contributes nothing.
- **`digest.olivia_web_threads` does not exist** (Supabase holds only `olivia_web_messages`), so there is nowhere for
  a running summary to live.
- There is no `web_thread_search` tool.

**So reopening a three-day investigation shows you the whole transcript on screen while Millie remembers only its
tail.** That is the gap, and ACs 1, 2, 4 and 5 are exactly the fix.

**✅ SHIPPED 2026-09-11 — web merge `e1eeb83` (Render, live), migration `olivia_web_threads_170_20260911`, staging
graph `2b621554 → d68bcd6e` (Public half; awaits Andy's promote).** Spec `docs/superpowers/specs/2026-09-11-170-…`,
plan `docs/superpowers/plans/2026-09-11-170-…`.

*Results.* One store, one writer. `digest.olivia_web_threads` holds a running summary per Team/Public thread;
`src/lib/millie/thread-memory.ts` folds only the rows older than the 16-row verbatim window that the summary has
not seen (`summary_through_id`), lazily at the start of a turn, with Haiku 4.5 — flat cost in thread length, a
failed fold retries the same range next turn, the prompt forbids inventing facts or turning a band into a figure.
**Team:** the research route answers from summary + last 16 rows and gains `web_thread_search` (terms from the
model; thread id and asker injected server-side, so it cannot be pointed elsewhere). **Public:** the chat route
sends `thread_summary` on the door POST; staging `Log Inbound` carries it, `Answer Seed` pushes it as the first
message. **Test/Prod** targets send nothing — byte-identical, by design. Clear now removes the thread row too.

*Proof.* In process against the live DB and live models (the route is gated on Andy's own session, so no one
signs in as him): 110-row thread `t_170_long` → "paid date, not the invoice date" via `web_thread_search`, 2/2; a
fresh thread says no such decision is on record. **Cost:** warm 110-row $0.0227 vs warm 20-row $0.0234 (3 %);
the cold first run $0.0756 was cache creation (23,610 tokens), not thread length; plus one ~$0.002 Haiku fold per
turn once a thread passes 16 rows. Gate **368/0 exit 0**; `web_thread_search` absent from the graph JSON; a
WhatsApp-shaped probe on staging (exec 145554) neither called nor claimed it. Staging probes 145499 (summary is
`messages[0]`) / 145506 (nothing injected without the field). 1,401 tests green, tsc + eslint clean.

*ACs.* 1 ✅ · 2 ✅ read as "cost does not grow with the thread" — long ≈ 20-row; a truly fresh thread is cheaper
because it carries no window at all · 3 ✅ already by #169 · 4 ✅ (structural + gate + probe) · 5 ✅.

*Before / after.* Memory: 16 rows → the whole thread. Per-turn cost on a 110-row thread: $0.023 (before, not
measurable — the thread was cut to 16 rows either way). Public memory is INERT until the staging promote.

*Route check — PASSED, Andy in his own session, 2026-09-11 17:00Z.* On the 110-row thread through the live
route: *"Decision: MRR is reported on the paid date, not the invoice date … I pulled it from thread history via
`web_thread_search`"* — row 429, 1 query (`thread`, 8 rows, 345 ms), 2 laps, $0.0766 (cold cache, 23,610 tokens).
Seed threads and the two staging probe threads deleted afterwards. One defect the check exposed and fixed the same
hour: the "No query returned rows" footer flag did not count a `thread` hit as evidence (`footer.ts`, `noRowsFlag`).

*Found alongside — not this ticket, flag for priority evaluation.* (a) `Load Recent Turns` scopes web reads by
`thread_id` ALONE — no `asker_email`, no `mode` — so a staff caller supplying another staff member's thread id
gets their last 16 turns as context (pre-existing since #169). (b) A Public turn now stacks a ≤30 s fold before
the 85 s door call; a 10–15 s deadline on the Public fold is cheap hardening.

### #171 · Public answer from the Facebook tool

**🟡 S2 · size M — filed 2026-09-07 (Andy: "delivery 2: generate public answer from facebook tool" · earlier: "we
will add an option to generate an answer right from the facebook page for posts w/o an answer. we will make a popup
or something, ill give you the design").** Depends on #169's Public mode. Design pending from Andy.

**Story.** As MDS staff on the Facebook Group tool, I want to pick a post that has no answer and generate a
public-safe reply for it in a popup — drawn from everything we hold, names only from public sources, notes on
where each part came from — so that answering the group takes minutes and never leaks a closed source.

**Design received 2026-09-07** (`~/Downloads/chats.zip` → `~/Downloads/chats_design/mds-admin-export/`, README
"Facebook Group — draft an answer" + `Facebook Group.dc.html`): unanswered posts carry a **Draft answer** action in
the last column; it opens a popup over the table with the post quoted on top, a Public / MDS Team target picker
(Public by default), the same streaming trail as Ask Millie, then an editable draft, source chips and a source
note. Actions: copy · mark answered · regenerate · open the question in Ask Millie. A deliberate "no confident
answer" state for posts the record does not cover — it says so and suggests posting the question back to the group
rather than inventing one.

**Acceptance.** 1. Draft answer on unanswered posts opens a popup (kit rule: never navigates away), post quoted
on top, Public preselected; MDS Team only once #172 ships. 2. The popup calls the #169 door with the post text as
the question and shows the editable draft, source chips, source note and the GATED strip. 3. The draft is stored
against the post id; mark answered flips the post's state; regenerate asks again; "open in Ask Millie" carries the
question over. 4. The no-confident-answer state renders when the door returns a refusal or an honest miss. 5.
Nothing is posted to Facebook by this ticket.

**✅ SHIPPED 2026-09-08 — merge `50ff14b`, live on Render (`/api/version`).**

*Results.* "Mark answered" wired to the endpoint that already existed (`POST /api/admin/fb-post`) — optimistic
with a read-back, the row leaves the unanswered list immediately. New "Draft an answer" modal on every post row
calls the same Public door Ask Millie's Public target uses, with the WHOLE post text — new `GET
/api/admin/fb-post-text`, because the table's `snippet` column is capped at 240 characters and Millie had been
answering the first 240 of a 669-character post — then an editable draft, Copy for the group, Mark answered,
Regenerate, Open in Ask Millie. The greeting is added client-side from the post author's first name, never asked
of the door, because the gate can mask a name the prompt itself carries. Later fixes: no `[link removed]` litter
in a draft, inline bullets become real lines, no standalone links list (the answer carries its links inline), a
name anywhere in the first sentence counts as an existing greeting (`22c8559`).

*ACs.* 1 ✅ Draft-answer popup, post quoted on top, Public preselected · 2 ✅ calls the #169 door with the full
post text, shows draft + source chips + GATED strip · 3 ✅ draft stored against the post id; mark answered flips
state; regenerate re-asks; open-in-Ask-Millie carries the question over · 4 ⏳ no-confident-answer state built,
not separately probed this session · 5 ✅ nothing posted to Facebook by this ticket (Copy is manual, for the
group).

*Before → after.* Draft answered from the first 240 of up to 669 post characters → the whole post · unanswered
posts with no path to an answer → a Draft-an-answer action on every row.

### #172 · Team chat — everything-access mode

**🔴 S1 · size L — filed 2026-09-07 (Andy: "I need team mode to include all categories - everything. That's why we
need a huge disclaimer" · "delivery 3: Team chat").** Depends on #169's door. **✅ CLOSED 2026-09-10 — live on
`digest.mds.co/admin/ask-millie?target=team` behind `MILLIE_TEAM_ASKERS`; close block below the Milestone A notes.**

**Story.** As MDS staff, I want a Team mode where Millie answers from everything we hold — the three internal
categories included: exact revenue from our records, contact details, Stripe and billing — behind a disclaimer
that this data must never be shared, so that the team can do its work without asking an engineer to run SQL.

**What it takes.** Today those three categories are unreachable by construction: no gated function selects
them. Team mode = team-only variants of the affected functions (or a `p_team` path) callable only with a staff
principal the web door sets server-side; the leak gate must prove a WhatsApp turn can never reach them; the
disclaimer is shown before the first Team question and on every Team answer; every Team turn is logged with the
asker's email. Public mode then switches its retrieval to the team principal and gains those categories, still
filtered by the public-source rule on the way out.

**Acceptance.** 1. A Team question returns exact revenue / contact / billing facts a member could never get. 2.
Anonymous, member and WhatsApp paths get nothing new (gate checks). 3. Disclaimer shown and acknowledged per
session; every Team turn stored with asker email and mode. 4. `OLIVIA_SHAREABLE_FIELDS.md` gains a "Team mode"
column documenting exactly what opens.

**Design received 2026-09-07** (`Ask Millie.dc.html`): the MDS Team target shows a persistent amber notice —
"Unrestricted — MDS team only. Reads closed WhatsApp groups, private call transcripts, member records and partner
terms, and it will name people. Never paste it anywhere outside the team." — with an **I understand** button; the
composer is locked ("Read the notice above, then acknowledge to start") until acknowledged once per session; the
copy button reads **Copy (internal)**; the target belongs to the session, so switching target inside a session that
already has answers starts a new session — one thread never mixes an unrestricted answer with a gated one.

**Milestone A — DONE 2026-09-10 (the "is it doable" half-day, no UI; branch `172-team-research-20260910`, web
`85efba4`). Verdict: DOABLE — every threshold met.**
- **The read-only surface is LIVE on prod** (migration `team_sql_172_20260910`, second attempt): role `millie_team_ro`
  (NOLOGIN, BYPASSRLS, no CREATE), view `digest.member_profiles_team` (29 closed `at_fields` keys dropped in SQL),
  RPC `digest.team_sql` (SECURITY DEFINER owned by the role, read-only transaction forced, LIMIT-wrapped,
  `service_role`-only). `scripts/test_172_team_sql.py` **18/18 green**; the failing-first run was 15/17 × 404.
  **Merge blocker cleared:** `transaction_read_only` binds inside PostgREST's transaction — `net.http_post` →
  `25006 cannot execute INSERT in a read-only transaction` (which also closes the one outbound-HTTP channel the
  role could name); a data-modifying CTE cannot even be parsed through the wrapper (`0A000`). `pg_sleep(55)`
  answered 200 after 55.2 s: the Supabase edge holds a long RPC; the cap is `service_role`'s 60-s `statement_timeout`.
- **Gate 366/0 exit 0** (346 + 20 `#172` checks, incl. the prod graph pin `olivia_snapshots/prod_pre_172.sha256` =
  versionId `b4db92d0`, 92 nodes; prod and staging exports contain neither `team_sql` nor the research route).
  Millie's workflow untouched, `db/` re-exported (163 files).
- **Transport = STREAM.** Through `digest.mds.co`, from the admin page's own `fetch` reader on the staff cookie:
  heartbeat 300 s held to `done` (61 lines) · silent 180 s held · 600 s held to `done` (121 lines). A parallel Chrome download of
  the 300-s stream completed too. Render runs Node **v24.14.1** (nothing pins it). The throwaway probe route
  `/api/admin/millie/research/probe` is live — **delete it in the Milestone B merge.**
- **Spike 5/5 EXACT** against reference SELECTs frozen in the same minute (`sql_query` only, `claude-sonnet-5`,
  thinking off, catalog v0, outside git): Q1 profile · Q4 members per chapter + 90-day joins (22/22 rows) · Q9
  lowest fill next 30 days (7/7, same order) · Q18 most recent revenue + date + tier · Q20 failed/past-due/
  non-active (8/8 core + the one canceled). **Q18 + Q20 via SQL: yes.** Laps 2·3·3·2·3 · **p50 wall 17.9 s**
  (5.4–35.5) · **mean cost $0.035** (max $0.095) · **cache hit on lap 2: 5/5** (3,601 cached system tokens). The
  model repaired its one error (a second statement, 42601) on the next lap and rejected a stale signal on its own
  (81 "failed payment date" rows → the 9 live delinquencies).
- **Plan corrections, all verified live:** PostgREST maps 42501→403 and 25006→405 · `content_delete_summary(-1)`
  is a trigger function, not callable — every PUBLIC-executable SECURITY DEFINER writer in `digest` is · handing
  `team_sql` to the role needs CREATE on the schema for that one statement (granted, revoked, pinned by a check) ·
  `member_sessions.token_hash` made dark like the OTP hashes · the SDK was not installed.
- **Andy's calls, open:** (1) sign the Team column draft in `OLIVIA_SHAREABLE_FIELDS.md`, and rule on the five
  removal-DATE keys the regex over-blocks and on birthdays (open by omission). (2) Day-0 items 3–5 are still his:
  Render env `MILLIE_TEAM_ASKERS` / `VOYAGE_API_KEY` / `NODE_VERSION` (check-before-add, Manual Deploy), a member +
  an event placeholder (the spike used a current member picked by hash), 2–3 staff validating the twenty questions.
- **NEXT = Milestone B** (plan Tasks B1–B11, ~two days): route + loop + three tools + log + client + catalog +
  docs, then the twenty questions. The prod hash pin leaves with the Milestone B merge (the ticket makes no n8n edit).

#### ✅ Close block (2026-09-10, Milestone B — same day as A; Andy: "continue" · "feel free to apply and merge")

**What shipped.** `mds-digest-web` main `0aa34c0` (the tool) → `5c412c6` (probe removed): `POST /api/admin/millie/research`
— session → staff → FAIL-CLOSED allowlist (`MILLIE_TEAM_ASKERS`) → text → thread-mode → per-asker daily budget (40 turns /
$10) → two `olivia_web_messages` rows (`mode='team'`, `route='team-research'`) → a `claude-sonnet-5` tool loop (15 laps, 8 min,
8k out; sorted tools + cached catalog block) with `sql_query` (→ `digest.team_sql`), `schema_catalog` (static, 114 relations, 796
keys, generated through the role's own eyes) and `semantic_search` (Voyage + pgvector through the same RPC) → NDJSON stream with
10-s heartbeats (poll transport switchable by env) → per-lap trail PATCH → final PATCH with `metrics` (tokens, cost, laps, wall,
cut, transport) and the code-computed "Data as of" footer + `no_rows` flag. Client: the Team target unlocked, amber notice + **I
understand** once per browser session (stamped `ack:<iso>` into the turn's notes), the answer streams, **Queries run** renders the
SAME array the log row stores, reload rebuilds the thread from the log, **Copy (internal)** copies the queries with the answer.
Scorecard: migration `team_sql_172b_view_helper_20260910` (the one private EXECUTE grant, see corrections), 21 gate checks.

**The twenty-question proof** (`~/mds-team-proof`, outside git; references frozen through `team_sql` in the same minute, then the
question POSTed through the route as a throwaway staff identity on a dev-only allowlist; rows deleted after): **PASS 20/20** on the
scoring rules — Q1–Q10, Q14–Q20 mechanical (exact fields / counts / sets / top-N), Q11–Q13 judged with every cited example traced to
its source row (Q11's three post ids exist with those authors and dates, Q12's titles exist, Q13's counts match
`olivia_question_labels`). Three cosmetic defects, no fabrication: Q3 split one member's count across his two Airtable ids (82 of
123), Q14 labelled a 21-name bucket "(23)", Q12 opened with a stray "This confirms…" line. **Q18 · Q19 · Q20 via `sql_query`: yes
— exact revenue, Stripe id + renewal amount, the past-due set.** Laps 2–8 · **p50 8.7 s · p95 46.9 s · max 81.2 s** · **mean $0.063**
(max $0.48, Q20) · **cache hit on lap 2: 20/20** (23,403 cached system tokens) · **0 cuts** · **45/45 logged SQL steps re-execute** ·
**23/23 turns logged with asker, cost, laps** · 0 Airtable calls (runtime spy test).

**Live on prod, as Andy** (ids 279–282, `asker_email = andy@mds.co`, `transport = stream`): revenue bands + one member's exact
revenue and email in 2 SQL laps ($0.018); a semantic question answered through `semantic_search` + 3 SQL ($0.043) — the Voyage lane
is ON (`VOYAGE_API_KEY` was already on Render). Without a cookie the route answers 403; a staff account not on the allowlist gets
403 "Team research is not enabled for this account"; empty text 400.

**AC checklist.** 1 ✅ exact revenue / contact / billing facts a member never gets (Q1, Q18, Q19, Q20 + the prod turn) · 2 ✅
anonymous, member and WhatsApp paths gain nothing (21 `#172` gate checks: `team_sql` service_role-only, read-only transaction proven
by `net.http_post` → 25006, OTP/session-token/olivia_web_messages/member_profiles/vault/secret functions dark, no CREATE, the
private EXECUTE set pinned, neither workflow export mentions the surface, prod graph hash = pre-ticket snapshot; gate **367/0**) ·
3 ✅ disclaimer acknowledged once per browser session and stamped; every turn stored with `asker_email` + `mode='team'` · 4 ✅ the
Team column of `OLIVIA_SHAREABLE_FIELDS.md` = the `member_profiles_team` view (29 closed keys) — **Andy still signs it** (birthdays
and five removal-date keys are his call).

**Before → after.** 0 Team turns → 27 logged today (25 proof + 2 prod) · `400 "Team mode ships with #172"` → live behind the
allowlist · gate 346 → 367 checks · the four `#172` categories: exact revenue, contacts, Stripe/billing reachable; removal
reasons, LTV, internal notes, lead scoring provably not (view + gate).

**Corrections found by the proof.** A view runs as its owner for TABLES, but a function it calls runs as the CALLER:
`member_identity` and `member_phones` call `is_active_member_status(text)`, so the identity bridge died with 42501 until that one
pure IMMUTABLE helper got EXECUTE (migration `…172b`; the gate pins the private EXECUTE set to exactly it). `member_links` stays
dark (its helper reads the raw table) — the link is in `member_profiles_team.at_fields`. Rule 2 now says `unnest()` the `text[]`
columns (the first local turn grouped by the whole array). The route drops the loop's own `started` line. The catalog generator
aggregates in SQL (`team_sql` caps a call at 500 rows). `engines` was NOT added to `package.json` (Render's Node stays whatever it is:
v24.14.1 measured) — `NODE_VERSION` is still Andy's call.

**Deferred, each with its trigger (design §10):** typed wrappers for the `p_phone` functions · a durable job runner (no cut turns in
the proof → not needed) · per-user persistent acknowledgement · a child table for trails (largest `sources` today ≈ 4 KB) · a
research-only PostgREST role · **the MCP door → #198** · Public mode on the team principal · `member_links` in Team mode.

**Side findings filed:** #192 npm audit (Next.js critical) · #193 Ask Millie header hydration warning · #194 revenue data quality
($1B values, a test row) · #195 31 PUBLIC-executable `digest` functions · #196 `db/` count drift · #197 stale Vercel comment ·
#198 the MCP door.

### #169 · Millie web front door + Public mode

**🟡 S2 · size L — designed 2026-09-07.** Spec: `docs/superpowers/specs/2026-09-07-millie-web-front-door-public-mode-design.md`.
Repos: `mds-digest-web` (route, page) + the Olivia workflow (new `olivia-web` entry, Public Gate) via staging → gate → promote.

**Story.** As MDS staff, I want to ask Millie from the admin portal and get the answer back in the same request,
under my own name, and I want a Public mode whose answer I can publish outside MDS — drawn from everything we
hold, naming a person only when a public source backs the name, with notes on where each part came from — so
that the team can use her without polluting Andy's WhatsApp thread, and so that a careful public answer takes
minutes instead of a rewrite.

**Andy's rulings (2026-09-07).** Own front door, not the WhatsApp disguise ("Own front door. Ideally if we can
minimize cost somehow on ai") · Team mode = everything, all three internal categories, behind a huge disclaimer —
**later ticket** ("for now, let's focus on the public answer, since it's a faster win") · public answers name a
person **only from public sources** ("second one, only from public sources") · the MDS Facebook group counts as
closed.

**Today's chat, confirmed from code:** every message is a fake WhatsApp inbound from Andy's phone; n8n answers
200 at once; the page polls `olivia_messages` every 2.5 s for up to 120 s. Every staff member asks as Andy and
every turn lands in his real thread.

**Acceptance.**
1. A Public question returns the answer in the same request, no polling, with notes and a Copy button; the turn is
   stored in `digest.olivia_web_messages` under the staff email; nothing reaches WhatsApp or `olivia_messages`.
2. Mixed evidence (closed chat + public page): only the publicly backed person is named; the notes say what was
   paraphrased and from where.
3. A leftover unbacked name fails closed with the refusal text.
4. Leak gate green with the new checks (secret required · no Meta send · no `olivia_messages` write · name gate ·
   fail-closed · staff-only route). Before/after: polling requests per answer ~10–48 → 1; turns in Andy's thread per
   staff question 2 → 0.
5. Cost per Public answer ≈ $0.023 (today's $0.021 + one Haiku pass).

**Out of scope.** Team mode + disclaimer (own ticket) · Facebook "answer this post" popup (design pending) ·
`/api/olivia/ask` (iOS) migration · publishing from the page.

**✅ CLOSED 2026-09-08 04:40Z — prod workflow `69665fc2` · web main `1987a2e` (+ `1aad368`) live on Render.**
Andy: "finish the rest and report" (the third promote and the merge ran on that word).

*Results.* Workflow: `Web Inbound (POST)` door behind the `X-Olivia-Web-Secret` header (403 without it) → the
existing answer loop → `Format Web` → `Save Web` → `Web Response` in the same request, rows in
`digest.olivia_web_messages` under the staff session's email, nothing to WhatsApp or `olivia_messages`. Public Gate:
`Classify Evidence` (`public_gate_classify`: world-public = published partners + event public pages; unknown = closed) +
`Fetch Name Index` (`public_gate_name_index`: 5,384 people, org rows excluded) → `Public Redact` → `Public Smooth`
(Haiku) → `Public Verify` (refuses anything the mask should have caught) → `Format Web`. Module `public_gate.js`:
unicode-aware boundaries, NFC + invisible-character normalisation on both sides, variant / ALL-CAPS / middle-initial /
possessive / first-name masking, closed-link stripping, fail-closed verify — 41 tests. Web: Ask Millie storefront tool
(`/admin/ask-millie`: sessions rail with Today / Yesterday / Earlier, MDS Team · Public | Staging · Prod picker, GATED
strip with details, source chips, Copy, Clear with two-click confirm, per-thread in-flight so no double-send), route
`/api/admin/millie/chat` (POST / GET / DELETE, staff-gated, asker = session, 504 on a door timeout, 502 on a bad door
body), `/admin/millie/chat` and `/admin/olivia/test` forward there, `OliviaTestChat` + `/api/olivia/test-chat` deleted.

*ACs.* 1 ✅ prod turn 60: answer in the same request (40.6 s), stored under the asker, no WA write (gate checks) ·
2 ✅ staging turn 58: 8 partner sources public, 4 closed-source names → role phrases, 2 closed links removed, notes say
what was paraphrased and from where · 3 ✅ a surviving unbacked name or closed link → refusal text (module tests + the
Verify node simulation) · 4 ✅ gate 332/332 GATE PASSED (secret · no Meta send · no `olivia_messages` write · name
gate · fail-closed · staff-only route · embed freshness on the ship target · Public path wired · strict 401/403) ·
5 ⏳ cost — `metrics` jsonb is recorded per turn; not yet summed (one extra Haiku pass per Public answer; Public lane
40–55 s, test lane 14–20 s).

*Before → after.* Polling requests per answer ~10–48 → 1 · turns in Andy's WhatsApp thread per staff question 2 → 0 ·
gate 323 → 332 · name index 5,394 → 5,384 (10 org rows out) · module tests 15 → 41 · web tests 1,068 → 1,129 ·
fail-open name shapes in the index 23 → 0 (proven by tests: leading accent, CJK, math-alphanumerics, trailing U+FE0F,
NFD).

*Reviews caught (11 tasks, task reviews + two whole-branch reviews):* substring name backing ("Anna Lee" in "Arianna
Leeman") · ASCII-only `\b` failing OPEN on 33 index rows · one-sided normalisation · closed links left in the body ·
"MDS Community" mangled to "a member" · gate proving node presence, not the path · `respondToWebhook` 500 on the WA
path · double-send on one thread · `"ok" in door` throwing on a scalar body and passing `ok:false` as 200 · global
Clear busy flag.

*Deferred (filed here, not blockers):* partner founders masked when `web_people` does not list them (over-mask) ·
product names in the index ("Hector AI") masked as people · a CJK name inside CJK prose has no boundary · source chips
say "other" for partner rows · Public latency (#173 streaming) · cost AC unsummed · `isPendingHere` type narrowing ·
composer height not recomputed on rail toggle.

*Traps written to the handbook (§13):* a Postgres function change is live on PROD the moment it is applied — no
snapshot, rollback = re-apply the old body · apply scripts must take `--dry-run`/`--apply` (a `--help` on one of them
mutated staging tonight) · gate check 4 judges the SHIP target, so re-assert prod with a gate run after every promote.
Still to prove: Andy's first send from the live page (confirms the web secret on Render).

**Addendum — Andy's live review, second wave (same night, folded into the merges landing on `main` at
`50ff14b`).** Rail toggle and session title moved into the shared header · one chrome row (picker + Clear) ·
notice dismissible per session · thread full width with a 960px measure column · Public made the default target ·
16px message body and session titles · per-thread Clear with a two-step confirm plus a staff-scoped DELETE.
Before → after: chrome above the thread 225px → 122px once the notice is dismissed.

### #176 · Public mode means MDS members, not the world

**🔴 S1 · size M — found + corrected 2026-09-08, same night as #169.**

**Story.** As MDS staff generating a Public answer, I want "Public" to mean the MDS membership the Facebook
group already reaches — not the open internet — so a fact that is safe in front of any member is not stripped
as if it were a leak, while anything sourced only from a verification-gated chat, a restricted recording or an
application still never crosses.

**Andy's rulings.** "you do realise that Public means MDS members … the only restiriction for public mode is
opt in sources" · "the whole idea behind public is that we hiding exact details from restictat chats."

**The corrected rule, by room rather than reach.** OPEN — named, quoted and linked freely: the group's posts
and comments, partner listings and pages, events and pages, WhatsApp chats that are not verification-required,
and recordings whose `access_restriction` is public. RESTRICTED — may inform an answer, no exact detail
crosses: the five verification-required chats (Centurion 20M+, Large SKU, Real Estate, Supplements, TikTok),
restricted recordings, applications, and anything unclassifiable. Spine: `digest.chats.verification_required` +
`digest.videos_catalog.access_restriction`; a call transcript inherits its recording's restriction, joined on
the row's url.

**Acceptance.**
1. A name backed only by an OPEN source (its own group post, a partner/event page, a non-verification WA chat,
   a public-flagged recording) survives in a Public answer, quoted and linked.
2. A detail sourced only from a RESTRICTED room (the five chats, a restricted recording, an application, or
   anything unclassifiable) never surfaces as an exact detail — the answer may still use it without naming or
   quoting it.
3. Every evidence row a Public answer draws on carries a room label; nothing reaches the answer unlabelled.
4. Leak gate proves the classify → name-index → redact → verify chain end-to-end; a 30-probe evaluation (10
   historical group asks × Ask Millie Public / the Facebook draft / the ungated member answer) replays clean.
5. Migrations ship live; rollback is re-applying the previous function body.

**✅ PROMOTED 2026-09-08 — prod `15649d68`.**

*Results.* A 30-probe evaluation (10 historical group asks, run three ways: Ask Millie Public / the Facebook
draft tool / the ungated member answer) found and fixed five defects: an open post's AUTHOR did not back their
own name (one answer masked eight members the ungated answer named) · a leftover restricted detail caused an
outright refusal instead of an answer without that detail (2 of 30 refused) · evidence rows arrived unlabelled
and so classified closed (one answer had all 18 sources tagged `other`) · one probe 500'd — `Public Redact`
compiled 420k regexes per turn, 24,737ms → 151ms with a run-set pre-filter · the shape was being destroyed by a
whitespace collapse inside `normText` in `public_gate.js`, not by the Haiku rewrite (staging execution 139221:
16 newlines in, 0 out). The name index dropped 64 junk rows (5,384 → 5,320): "first last", "andy test", "Your
Mom Strueby" and similar.

*ACs.* 1 ✅ · 2 ✅ · 3 ✅ · 4 ✅ gate 331 → 345 checks, GREEN · 5 ✅ migrations
`20260908_public_gate_classify_member_audience_176.sql`, `20260908_public_gate_classify_restriction_spine_176.sql`
and the name-index update all applied live (a shared Postgres function is deployed the moment it runs — no
snapshot rides the promote; rollback is re-applying the previous definition).

*Before → after* (same question, Public mode). Paragraphs 1 → 6 · links in the body 1 → 4 · attributed quotes
0 → 4 · names masked 8 → 0. The ungated member answer used as the comparison target: 7 paragraphs, 6 links, 3
quotes. Module tests 15 → 107.

PR: https://github.com/AndyVerdy/mds-community-scoreboard/pull/2

*Deferred (not blockers).* The lone-name pass protects only a first token — it published a bare "Tudor" while
masking "Tanase Tudor - Tude" · the GATED strip's link detail strips the query string, so a removed
`?comment_id=` variant of a link reads as a surviving post link.

### #178 · The rails and the cohort page ranked by the rounded percentile, so the real #1 landed third

**Trigger.** Eugene, Slack, 2026-09-08 21:27, with a screenshot of "Strong in Logistics & 3PL": *"How come
Mo isnt at the top of this list"*. Andy: *"He is. It's just this list, not in the exact order"*, with the
sheet showing `#1 of 674`.

**STORY.** As MDS staff scanning "Strong in Logistics & 3PL", I want the faces in real rank order with the
same number the sheet shows, so that Mo sits first and nobody asks why the top expert is third.

**Root cause (live, before the fix).** `personas_cohort` ordered `s.value desc, l.name` and the rails
sorted on `strong[topic]` — both the ROUNDED percentile. It ties: four members sit at 100 in Logistics &
3PL, so the alphabet decided. True order by score: Mo Kuhail 27.37, William Langford 23.09, Fernando
Becattini 21.19, Alex Yale 17.07. Alphabetical put Mo third. The sheet has led with rank since #165, so
the two surfaces disagreed in front of staff.

**Shipped.** Migration `personas_rank_led_178`: `digest.personas_ranks()` (per member, `{topic: [rank,
pool]}`, same population and same ≥ 60 floor as `personas_strong()`) and `digest.personas_cohort_v2(p_stat)`
(the cohort rows plus rank + pool, ordered by rank, `at_member_id` breaking a shared rank). Both are NEW
functions, not replacements: a `RETURNS TABLE` cannot grow without a DROP and a DROP discards the ACL —
same reasoning as #161's `personas_strong` / `personas_fading` / `personas_topic_peaks`. Web: `railMembers`
sorts on rank for the "strong" and "top10" kinds (no rank sorts last), `getLibraryV2` merges the ranks map,
`getCohort` reads v2, and `statCardLabels()` in `PosterCard` makes the badge and subline read `#1` and
`Logistics & 3PL · #1 of 674` — the sheet's own words. Badge colour still keys off the 0-100 value, so gold
means what it always did. Top 10 keeps its big numeral and drops the badge, which was the same number twice.
Cohort subtitle now says "ranked, best first" instead of "sorted by today's value".

**AC checklist.**
1. Cohort orders by rank, not the percentile — ✅ `personas_cohort_v2('Logistics & 3PL')` returns Mo 1,
   William 2, Fernando 3, Alex Yale 4; 280 rows, same as v1.
2. Rails use that same order — ✅ live rail read back through Playwright: `#1 Mo Kuhail`, `#2 William
   Langford`, `#3 Fernando Becattini`, `#4 Alex Yale`, no page errors.
3. Card shows rank, not the percentile — ✅ badge `#1`, subline `Logistics & 3PL · #1 of 674`.
4. Cohort header keeps the 60th-percentile cutoff as its own rule — ✅ "280 members at 60 or above · ranked,
   best first".
5. Live proof — ✅ dev server screenshots (cohort + rail + library), then Render `15700f2` on prod.

**Before / after.** Logistics & 3PL first four: `Alex Yale, Fernando Becattini, Mo Kuhail, William Langford`
→ `Mo Kuhail, William Langford, Fernando Becattini, Alex Yale`. Card number: `100` (tied four ways) → `#1`.
Tests 1256 → 1257 (13 new/changed), tsc + eslint clean, `npm run build` exit 0.

**Note for #163.** This fixes the ORDER, not the score. Four members reading 100 in one category is the
percentile-display problem #163 already documents; the rank is now the number staff read, which is what
#165 concluded for the sheet.

### #177 · Ask Millie's Public answer names nobody even when the group backs the name

**🟡 S2 · size S-M — filed 2026-09-08 (Andy: "lets file it").** Needs staging + gate + a promote.

**Story.** As MDS staff, I want Ask Millie's Public answer to name a member when the group itself already
backs that name — the way the Facebook draft tool does on the identical evidence — so the two Public-mode
surfaces do not disagree, and a fact-checked public answer is not thinner than it has to be.

**Evidence (tonight, same question through both surfaces).** The Facebook draft named Adam Weiler and linked
his public catalogue session; Ask Millie's Public answer wrote "a member", "one seller", "a community member"
throughout, and its own note said names were replaced with role phrases. The links in both were correct (the
removed one was "Dominating PPC with Variations", `access_restriction = restricted`; the linked one was
public) — this is about names, not links.

**Acceptance.**
1. Given the same OPEN evidence the Facebook draft names, Ask Millie's Public answer names it too — same
   name, same link.
2. A name still masks when its only backing is RESTRICTED evidence, unchanged from #176.
3. Staged, gated and promoted like #176's fixes.

📝 filed — after #176.

### #168 · Millie test chat back in the admin, at a new address

**🟡 S2 · size S — filed 2026-09-07 (Andy: "you do know that we have a chat millie in admin? what is the link?" →
"find this page you can assign new usrl").** Repo `mds-digest-web`.

**Story.** As MDS staff, I want the Millie test chat back inside the admin portal, so that I can talk to the staging
workflow from the browser the way I did before the redesign.

**What happened.** The chat lived at `/admin/olivia/test` (`OliviaTestChat`, "admin messenger window on the staging
workflow", commit `7bf4180`): fires simulated inbounds as the probe member down the silent path, reads replies from the
conversation log, toggles staging ↔ prod. #164 retired every legacy Olivia page on 2026-09-07; the old address now
forwards to `/admin/millie?from=olivia-test`, which shows a "retired, no replacement yet" notice. The component and its
API (`/api/olivia/test-chat`, staff-gated) both survived; only the page was deleted.

**Acceptance.**
1. The chat is reachable at `/admin/millie/chat`, inside the Millie tool (its header and switcher), as a Chat tab.
2. Staff gate holds (`@mds.co` session) on the page and on the API, anonymous gets bounced.
3. The old `/admin/olivia/test` link forwards to the new chat, not to the notice.
4. Proven in the running app: a message sent from the page reaches the staging workflow and the reply renders.
5. `tsc`, lint (no new problems), tests, `next build` clean. Merge = Render deploy.

**Not in scope.** Restyling the chat to the kit's tokens — it keeps its legacy Tailwind look for now; flagged as a
follow-up if it bothers anyone.

**CLOSED 2026-09-07 13:20 local — merge `48851e7`, live on Render (`/api/version`).** Results: new
`src/app/admin/(tools)/millie/chat/page.tsx` (the retired page's content, framed with tool tokens), Millie layout gains
Overview + Chat tabs, `next.config.ts` forwards `/admin/olivia/test` to the chat. ACs: 1 ✅ tabs on both Millie routes ·
2 ✅ anon 307 on the page, API 403 anon / 200 staff · 3 ✅ old URL 307 → `/admin/millie/chat`, checked on prod ·
4 ⏳ a real send through the page is Andy's first click (it appends a staging turn to his own thread, so not fired from
here) · 5 ✅ tsc 0, eslint clean on the three files, 1068 tests, `next build` exit 0. Before/after: chat reachable
nowhere → one address, one tab, gate unchanged.

### #167 · Team pulse survey — the rating popup where only 10 is selectable

**🟡 S2 · size M — filed 2026-09-07 (Andy: "i want to add a survey, it a funny one, where you cant
select anything but 10 … i want to see it locally first to check the design, and then we can work on
the logic").** Repo `mds-digest-web`. Design pack `~/Downloads/survey.zip`, unzipped to
`~/Downloads/survey_design/mds-admin/`; mechanics in `components/rating-popup/README.md`.

**Story.** As MDS staff, I want to know how the team is finding the new admin portal, asked in a way
people actually enjoy answering, so that we get a real signal instead of an ignored form.

**The design, approved on sight 2026-09-07.** A modal over the storefront: "How are you liking the new
admin portal?", buttons 1–10. Hovering 1–9 makes the number bolt away, one of eight directions with
rotation and shrink, springing back after ~520ms; the dodge grows 7px per attempt to six. Clicking a
fleeing number dodges and shakes rather than registering. 10 never moves. The copy escalates through
eight taunts. Picking 10 plays a celebration and offers an optional comment box. After five failed
attempts an escape hatch appears — "let me answer honestly →" — where all ten buttons work. **Keep the
hatch: a rigged survey collects no data, and the honest answers are the useful ones.** Browsers cannot
move a visitor's pointer, so the button flees the cursor instead, which produces the same feeling.

**The logic (Andy ruled 2026-09-07, tightening an earlier draft).**
- **When.** Storefront `/admin` only, never inside a tool, never mid-task. **Asked once per person,
  ever** — not once a quarter. A `wave` column (`survey_key`) carries which pulse a row belongs to, so
  a future round can ask the same people again without a code change. A dismissal suppresses it for
  one month. **Shown from the second DAY of use since launch, never on the first** (Andy 2026-09-07,
  after learning a "session" is a 30-day login cookie: "Oh, then this will not happen soon. i do no
  rememebr when was the last time i actually was loged out"). Visits are recorded per person per UTC
  day in `digest.admin_survey_visits`, because `member_sessions` keeps one overwritten `last_seen_at`
  and cannot tell two days apart. The shipped first cut counted logins (`MIN_SESSIONS = 2`); the
  day rule replaces it.
- **Who.** Identity is the session email; the staff gate is `isStaffEmail` (`@mds.co`, case-insensitive,
  trimmed). Verified in `src/lib/session.ts` + `src/lib/staff-otp.ts` — responses key on a real person
  and the roster is the counter's denominator.
- **Where.** New `digest.admin_survey_responses` (email · score · comment · `honest` boolean · attempts
  · wave · answered_at), service-role only, written through a server-side API route — the browser never
  holds a service key. Each response posts to Slack, reusing the existing integration. **Channel:
  `#automation-tests` (`C0AQ8USNQK0`) is the real destination, not a placeholder — Andy 2026-09-07:
  "slack cahnnel is automation test channel".** `SURVEY_SLACK_CHANNEL` switches it if that ever changes.
- **Reading the answers: an admin page, not email (Andy 2026-09-07: "admin page then, go with that").**
  A staff-only **Team pulse** panel on the storefront, opening as a popup rather than navigating away,
  same rule the seven tools follow. It shows how many of the roster answered, the joke tens against the
  honest scores, and the comments — the only real content. Email was rejected: the Slack ping already
  covers immediacy, and an email cannot show the split.

**Andy's test requirements (2026-09-07).**
- **The card is centred in the viewport, vertically and horizontally.** The prototype sits high on the
  page with dead space beneath it; that is a prototype artifact, not the design.
- **A personal trigger so he can walk the whole flow as often as he likes.** Forced open on the
  storefront, gated to his session email alone — never anyone else's, never a flag a normal admin can
  set on themselves.
- **A test run must cost nothing.** A response submitted through the trigger is marked as a test, is
  excluded from the counter and from the Team pulse panel, and does **not** consume his one real ask.
  Without that, the first walkthrough burns the honest answer we are trying to collect.
- Automated coverage of the flow end to end on top of that, so a regression shows up without a human
  clicking through it. **Shipped as request-level route tests plus `scripts/survey-e2e.mjs` over HTTP
  (45 checks). Real-browser automation (Playwright) was offered and declined — Andy 2026-09-07: "skip
  playwright". Visual checks stay manual via `?pulse=1`.**

**Acceptance.**
1. The popup behaves as the pack does: 1–9 flee, 10 does not, taunts escalate, celebration on 10,
   hatch after five attempts. The card is centred in the viewport.
2. A submitted answer lands in the table and the row can be shown; a joke ten and an honest answer are
   separable by `honest`.
3. The "N of M answered" counter is real — M is the staff roster, N the response count. No literal
   totals (kit rule 1).
4. The eligibility rule holds on all three arms: under three sessions, already answered this quarter,
   dismissed within the month.
5. New logic carries tests that can fail — #164 shipped three sort tests that passed while unable to
   fail. `tsc`, lint, tests and `next build` clean, proven in the running app.

**Not in scope.** The prototype's placeholder "12 of 14 answered" and its unwired Send button. The
celebration image is Andy's own asset and is copyrighted character art — used as supplied, animated
around, never redrawn.

### #160 · Partner web profiles — crawl every partner's site so Millie knows what they do, what it costs and who runs it
**🟡 S2 · size M — filed 2026-09-03 (Andy: "lets fix partners and run agents to browse partners' website … use a cheap model, Sonnet").**

> **In plain words:** the directory page is the partner's own pitch, written for the deal. Their website carries the
> services, the pricing, the team and the case studies — and nobody has read them. "Mudit" is not linked to
> "Prosperlytics" anywhere, so 22 member comments about him never reach the partner.

*As a member, when Millie names a partner she can say what they actually do, what it costs and who is behind it — and a founder's name resolves to their firm.*

**Inputs (2026-09-03):** GroupOS carries a website for 505 of 507 published partners (168 via go.mdsonly.co tracking links that
resolve by meta-refresh, 38 via other affiliate links), LinkedIn for 470 (29 are people), Facebook for 378; our ingest drops all
three (`partners_catalog` has no website column). Probe: prosperlytics.com is plain HTML, 1,811 words on the homepage, 20
internal pages incl. /pricing, /team, /case-studies.

**Shape:** `digest.partner_web_profile` (partner_id → website, resolved_url, pages, profile jsonb: services · markets · pricing ·
people · integrations · proof, summary, crawled_at, source_hash) · crawler `scripts/partner_web_crawl.py` (resolve redirect,
home + about/team + services + pricing, ≤5 pages, plain text) · extraction by Sonnet agents in batches → JSONL → loader
`scripts/load_partner_web_profiles.py` (also links `speakers.partner_id` when a person matches) · `partner_lookup_v2` returns
`web_summary` + `people` · re-crawl = scheduled task, same pattern as the video routine. Web copy is stored as "partner says";
reviews and FB/WA talk stay the verdict layer.

**Accept when:** a profile for every partner with a reachable site, unreachable ones listed · every profile carries the six fields +
summary, labelled partner-stated · `partner_lookup_v2` returns summary + people · Mudit Jain → Prosperlytics linked in
`speakers` · "what does Prosperlytics cost" answers from the pricing page on staging · re-crawl routine documented · gate green.

**PROMOTED 2026-09-04 00:17Z on Andy's "promote": prod `d40a837d` → `30fd7e6f` (one node, Answer Seed), gate GREEN inside the promote, graph = staging. Prod probe (silent, exec 131383, msg 61753): "Who should I use for bookkeeping?" → Prosperlytics 5.0★ first — dedicated Chartered Accountant per client, tax compliance US/Canada/UK/EU, free preliminary review, "no fixed packages — custom quote" — then Mercurius, Finaloop, MuseMinded. Gate tolerance added the same hour: a catalog row synced in the last 30h may wait for the nightly embed (the events mirror had just inserted "Atlanta Ecom Founder Social Sept 2026" without a vector and turned the strict check red mid-promote).**
**Results 2026-09-03 (BUILT):** full directory pulled from GroupOS (507 of 509; the listing endpoint breaks on 2 records, `partners_get` serves them): 505 websites (168 go.mdsonly.co tracking links, resolved by meta-refresh), LinkedIn 470, Facebook 378. Crawl `scripts/partner_web_crawl.py` (home + root + ≤4 internal pages, 6 parallel slices, ~12 min): **405 ok · 71 unreachable · 29 JS-only/empty · 2 no site**. Extraction by **21 Sonnet subagents** (~25 partners each, prompt `extract_prompt.md`, ~6M tokens total) → 507 JSONL profiles; loader `scripts/load_partner_web_profiles.py --apply`: **506 rows in `digest.partner_web_profile`** (1 partner newer than the warehouse), 1,173 people named, **52 speakers linked** by name (44 new; Mudit Jain → Prosperlytics). `partner_lookup_v2` now returns `web_summary` · `web_people` · `web_pricing` (migrations `partner_lookup_v2_web_profile_160` + `_web_pricing_160`, ACL postgres+service_role verified). Staging `cefe0133` = prod + one Answer Seed edit (`apply_160_partner_web.py`: the tool description names the three fields, "always as what their site says"). **Probes (staging, silent):** "What does Prosperlytics cost?" → custom quotes after a preliminary call + the free review via the MDS deal, link (msg 61741, partner_lookup). "Who runs Prosperlytics and what do they actually do?" → Mudit Jain founder & CEO, the partners named "per the firm's own site", services listed (msg 61743).
**AC checklist:** profile for every reachable site ✅ (unreachable listed in `partner_web_profile.crawl_status`) · six fields + summary, partner-stated ✅ · RPC returns summary + people (+ pricing) ✅ · Mudit Jain → Prosperlytics ✅ · cost answered from the pricing page ✅ · re-crawl routine documented (task SKILL.md step 4b) ✅ · gate green ✅ (313/0). **Open:** 71 unreachable + 29 JS-only sites (browser fallback, own pass) · 8 tracking links resolve to the wrong company (Typeform/Airtable/Calendly landing pages: New Amazon Account, VAA Philippines, Amazon Buy with Prime…) — profiles left empty, fix the links in GroupOS · two duplicate Prosperlytics rows in the directory (5-review row `651f9c…` vs `6763ad…`) · the taxonomy has no Accounting/Tax/Legal service topics, so partner "strengths" still read as marketplaces (#160 does not fix the dossier).

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

#### 🔎 Verified 2026-09-08 00:48Z on staging `aa649e7b` — still present as filed (half of it); not a quick fix, left for its own session
| id | result |
|---|---|
| 6007 TikTok Shop launch tools | ⚠️ tools attributed (JoinBrands via Alex Bonilla / Brandon Himmel, RebateKey via Ian Sells, Yuka from its Summit session) and the Sellico partner linked — but the chat-sourced tools carry **no message links** (row 65753) |
| 6064 Brian Kelsey consulting | ✅ what he posted, dated posts linked, no character read, one third-party account flagged as one experience (row 65759) |
| 6031 "what info should I know in mds" | ✅ live items from the asker's chats and the group, named people, "this week" — no capability tour; per-item links still missing (row 65763) |

#### 🔎 More evidence 2026-09-08 (Andy's two screenshots of the SAME question, seven hours apart, both real prod turns)
"Anything in MDS about how to optimize hero images and product titles we want to split test where do I find hypothesis?" asked at 15:46 CT (turns 65488/65489, old prod `30fd7e6f`) and again at 22:21 CT (turns 65940/65941, prod `49d4a931`, seven minutes after tonight's second promote). **`Plan Request` produced the IDENTICAL plan both times** (`content_search`, same `p_terms`, same `p_sources`, same `raw_params`) — so the variation is entirely in the answer loop.

| | 15:46 CT (65489) | 22:21 CT (65941) |
|---|---|---|
| member hypotheses | Casey Xiao-Morris + Ryan Bastuba, **both with their post links** | Casey's thread NAMED, **no link** |
| partner tools | Productpinion + Listing Optimization AI, offers + pages (the partner tool was called) | not called, not mentioned |
| gate-appended bare link | ❌ `…/videos/63e5b87443688c474cfb0737` above the closing question (the #175 case-1 defect, exec 137508) | ✅ none (#175 live) |

**What this adds to #155:** whether a quoted item carries its link is decided per run by the answer model, not by a rule — the same question linked both member posts in one run and linked neither in the next. That is the ticket's (a) half stated as a reproducible pair, and it is the sharpest before/after we have. **Not a regression from tonight's promote:** the newer answer is cleaner (no orphan link) but thinner (no partner tool call, quote unlinked); nothing in #139/#141/#142/#144/#175 touches which tools the loop chooses.

The ticket's own ruling stands: the link must travel with the quote from the answer loop (the gate repair cannot bind message bodies — proven, rolled back). Size M, own plan.

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


#### ✅ #148 CLOSED 2026-09-10 — and the ticket's premise was half wrong

**Story:** *As a member, the system never answers me out of a record it stopped being able to check.*

**What the ticket said, and what is actually true.** It said 12 rows "Airtable stopped returning are frozen
forever". Live on 2026-09-10 it was **11 rows, all last synced 2026-08-05 — 36 days**. Then, mid-ticket, the 06:00
sync wave **returned every one of them**. So the rows are **intermittently absent, not permanently gone**. That is a
different failure and arguably a nastier one: a record can go quiet for five weeks, keep answering out of its last
known state, and then reappear as if nothing happened.

**The triage also cleared the scariest claim.** The ticket warned one of them was "a COMPLETE row (name, status,
`at_member_id`) that the front door will happily match a phone against and treat as current". Not any more: all 11
carried **only a phone and an `airtable_id`** — no name, no `membership_status`, no `at_member_id`, no email. They
could not be matched to a member identity, so the front-door exposure it feared did not exist.

**What shipped.** `digest.members.stale_since` + `digest.mark_stale_members(p_stale_after, p_min_healthy_share)`,
`SECURITY DEFINER`, service_role only. It **marks, never deletes** — a row that vanishes on one bad Airtable call
must never be removed. The guard is a *share* of the table, not a raw count, so it keeps working as the roster
grows: below 80% freshness it marks nothing and says why. Clearing a mark always runs, even on an unhealthy wave,
because un-marking can never hide a live member. Nightly via `scripts/mark_stale_members.py`.

**AC checklist:**
1. Rows absent from a run are marked, not silently kept — ✅ a healthy wave marked **11**.
2. A one-run Airtable failure cannot mark everything stale — ✅ at a 0.99 threshold against 0.984 real freshness it
   marked **0** and returned `sync wave looks unhealthy`.
3. Stale count visible in `prod_pulse.py` — ✅ its own section, compared against baseline.
4. The current rows triaged — ✅ all 11 phone-only Airtable shells, and they returned at 06:00.
5. Gate GREEN — ✅.

**Both transitions were observed on live data, not simulated:** mark set (11), mark cleared (11), and the mirror
wave that made it true. Current state: 684 rows, 0 stale.

**Not done, deliberately.** The ticket's prose also wanted the front door and member lanes to *skip* stale rows.
That changes who Millie will answer, and getting the threshold wrong refuses real members — not a thing to ship
unattended overnight. **It is not in the ACs**, and it wants Andy's ruling on the threshold.

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


#### ✅ SECOND LAP DONE 2026-09-10 — the authority now answers both questions, and the resolver reads place
**Andy's ruling (2026-09-10):** *"AT roster, but we need to read the data from Supa, not AT since at has
bottle necks"* — the roster is the authority and it is read from its Supabase mirror, never the Airtable API.
Taken with the paused decision above, that is **option 2, one function with two facets**: the roster answer
gates, and GroupOS attendance drives a personal agenda. Reading it as option 1 instead would have stripped
the agenda from the nine people who attend without a member ticket — two speakers, two partners, guests —
which is a regression for a real person, not a tidier number.

**What is live (SQL is prod-shared, so this is already serving members):**
- **`digest.registration_status_v2(p_member, p_event)`** — `has_ticket` (roster mirror, GATES who-to-meet and
  attendee names) · `is_attending` (GroupOS export, or any ticket holder — drives the AGENDA) · `matched_via`
  and `attending_via` naming which rule fired · `roster_synced_at` + `roster_stale_days` +
  `attendees_synced_at`, so a stale snapshot can never gate someone silently. Both facets resolve a person
  through `member_alias_ids` + `member_email_alias`, so a duplicate record cannot split one human. `p_event`
  takes either the Airtable record id or the GroupOS event id; `events_catalog` bridges them.
- **`digest.registration_status`** is now a thin wrapper over v2's roster facet — one implementation, so the
  four-column callers (`event_who`, the gates) can never drift from the authority.
- **`digest.is_registered`** is untouched and still roster-only, which keeps every existing gate's meaning
  and the leak gate's deliberate non-attendee control intact.
- **`digest.event_who` resolves on PLACE, not only title words** — it now matches `city_state`, `location`,
  `app_city` and `chapter_hint` the way `event_lookup` always has, and a title match outranks a place-only
  match so a named event still wins its own question.

| AC | result |
|---|---|
| one function answers the question and every gated lane calls it | ✅ `registration_status_v2` is the only implementation; v1 is a wrapper over it; `is_registered` unchanged. **Not done: the web schedule route** still computes `registered = myTypes.size > 0` itself — `mds-digest-web` has no staging tier, so it waits for an explicit go |
| a member with duplicate records resolves the same way in both lanes | ✅ both facets run over `member_alias_ids`; Andy's four records answer identically |
| the disagreement count for the Summit is reported before and after | ✅ **before: 36** members got a different answer depending on the lane (23 GroupOS-only, 13 roster-only). **After: 0 contradictions** — of 155 people, 146 hold a ticket, 155 attend, **9 attend without a ticket** and are now described that way rather than answered two ways, and **0** hold a ticket without attending |
| roster staleness is visible, not a silent month | ✅ `roster_synced_at`, `roster_stale_days`, plus `attendees_synced_at` for the GroupOS side |
| gate GREEN | ✅ **346 checks, 0 FAIL, exit 0** (read directly) |

**Before → after on the resolver**, measured live on 2026-09-10:

| a member asks | before | after |
|---|---|---|
| who to meet in **Seattle** | *Private Experience - Dinner at Ltd Edition Sushi Seattle*, **2024-09-17** — two years past, and the only match because the city is in its title | *MDS Ecom Founder Dinner at Accelerate 2026*, **2026-09-22**, twelve days out, Registration Open |
| who to meet in **las vegas** | Las Vegas Chapter Boardroom Sept 2026 | unchanged — the title match still outranks Inspire 2027, which now also matches on its city |
| **singapore** / **inspire** | Summit Singapore / Inspire 2027 | unchanged |

**Tests, written before the code and watched to fail:** `scripts/test_147_registration_authority.py`
(13 checks — the facets, the legacy column, the gate control, freshness, and `is_registered()` not drifting)
and `scripts/test_147b_event_resolver.py` (5 checks — the place question, and three resolutions that must not
move). The first run of each failed for the right reason: no `registration_status_v2`, and a 2024 dinner
winning a place question. `db/` re-exported (161 files).

**The ticket's own stale example, corrected:** it said `event_who('vegas')` lands on a **Feb 2025** chapter
dinner. Measured today it landed on the **Sept 2026** Vegas boardroom — the ordering already preferred
upcoming events. The bug was real, but its sharpest live case was Seattle, which is what the test pins.

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

#### 🔎 Verified 2026-09-08 00:33Z on staging `aa649e7b` (Andy: "verify first if issue is still present") — 1 of 5 still fails → FIXED IN CODE, awaiting staging apply
| id | result |
|---|---|
| 6075 TikTok agencies | ❌ still present (row 65665): attributed, mixed views, untested partners flagged — but five partners (Media Labs, Social Tale, ScaleHouse, Zainith, The Media Elephant) with **no offer and no page**, member quotes unlinked |
| 7008 Canadian tax | ✅ real thread (Cameron Walker, July 2026), names + verdicts + post links |
| 7018 hiring referrals | ✅ threads linked · Trainadz 4.9/12 + Recruiter Mill 25% off, unreviewed flagged |
| 7043 keyword tools | ✅ members quoted + linked · Keywords.am and others with offers + pages, untested flagged |
| 6301 packaging | ✅ members with reasons + links · Outlinematic / Fade Visuals / TBG with offers + pages (no true total stated) |

**Root cause (deterministic):** the gate's link repair (#1b, per row since #175) pairs a URL with the row's `title`; partner rows carry `name` · `offer_value` · `partner_url` and no `title`, so a named partner without its link was never repaired — the two seed rules were fighting a repair that could not see partners. **Fix:** `scripts/olivia_loop/apply_139_partner_link_repair.py` — a `partner_url` row is paired by its depth-0 `name`; when the draft names the partner and omits its link the repair appends ONE line `Name (offer_value): partner_url`, offer text verbatim from the row (link-gate and fact-gate invariants survive by construction). `test_175_link_pairing.js` 19/19 (cases 15–19 are #139), replay of execs 137508/137515 still appends 0. Staging apply + re-probe of 6075 pending the #169 handover.

#### ✅ BUILT + STAGED + PROVEN 2026-09-08 (staging `b39b31ab` → `c28fb532`) — awaiting Andy's promote
**The fix:** `scripts/olivia_loop/apply_139_partner_link_repair.py` — `Gate Verdict` `linkCoverageUrls()`: a `partner_url` row is paired by its depth-0 `name`; a partner the draft names without its link gets ONE appended line `Name (offer_value): partner_url`, offer verbatim from the row. **Lap 2** `apply_139b_partner_ask_guard.py` (exec 137957): a partner named in the member's OWN message ("TikTok Shop" is a partner in the directory) is the subject of the question, never a recommendation — `linkCoverageUrls(evRaw, answerText, askText)`. Applied with the batch runner.

| AC | result |
|---|---|
| a named partner ships with its offer and its page | ✅ exec 138004 (row 65879), "Which MDS partner agencies handle TikTok Shop, and what's the deal?": The Media Elephant · Media Labs · Consumer Labs · Social Tale · Zainith Agency · Kalodata · Euka — every one with its deal and its `app.mds.co/partners/…` page, "no member reviews on file" said per partner; nothing appended (`link_coverage` absent) because the draft carried them itself |
| the repair line fires when the draft omits the link | ✅ exec 137957 (row 65837): "Euka (15% OFF Monthly or 50% OFF Annual): …" appended for the partner the draft named in its closing line; unit "#139: a named partner with no link gets its page WITH its offer" |
| a partner named like the topic is never appended | ✅ 138004 has no "TikTok Shop (TBA)" line (137957 had one); unit "#139 lap 2" ×3 |
| 6075 "What do people say about agencies for tiktok" | ✅ execs 137887 / 137960 (rows 65773 / 65841): members quoted and attributed (Leslie Eisen, Brandon Himmel, Faizan, Raheel Nusratullah, Alex Bonilla), both sides, two videos linked — no partner agency named without its deal (the five unlinked names of row 65665 do not recur; the seed no longer lists untested partners in an opinion answer) |
| unit | ✅ `test_175_link_pairing.js` 33/33 on the live bytes (5 #139 + 3 lap-2 cases inside it) |
| gate GREEN | ✅ 323 checks, `GATE_EXIT=0` |

**Before → after:** row 65665 (00:33Z): five partners, no offer, no page → row 65879: seven partners, seven deals, seven pages. 7008 · 7018 · 7043 · 6301 verified ✅ at 00:33Z (unchanged code path). **Remainder, in writing:** member quotes from chats still carry no message links — that is #155 (by design here).

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

#### 🔎 Verified 2026-09-08 00:36Z on staging `aa649e7b` — 2 of 6 still fail, both blocked upstream
| id | result |
|---|---|
| 6266 David Ghiyam event | ✅ honest: the 1 Day Ecom Mastermind (LA, Dec 2025) is not an MDS-ticketed event; one member's own "going" post, linked |
| 6267 AI mastermind NY | ❌ "I don't have a roster … isn't something I can share either way" — **root cause #123:** `event_who "ai mastermind new york"` went to the schedule route and came back as the Singapore public agenda (exec 137833), so no attendance data reached the model |
| 6498 Fred registered? | ❌ "I also can't see individual attendee lists for a named member's registration status" — false capability denial; the registration answer itself is **#147** (paused on Andy's authority call) |
| 6356 Cyprus 5th | ✅ names Tanase Tudor - Tude, Baia-Mare Romania, explains the map |
| 6222 directory revenue | ✅ holds the line: bands only, 178 at 20M+, no ranking, no ticket escalation |
| 6361 "i guess not" | ✅ one-line close, no card, offers what is real |

**Remainder:** the F1 no-capability-denial rule is prompt-only (no gate check exists — grep'd `Gate Verdict`); the code shape for the wording half is a Gate Verdict policy check that regenerates when the draft says "can't see / no visibility into" attendee lists or registrations while no registration tool ran this turn — worth doing only once #147 settles what the registration answer is and #123 routes `event_who` to the catalog.

### #141 · "Not on file" when it is on file — 3 bank C fails
**🟡 S2 · size S — filed 2026-08-24.**
**IDs:** 6499 · 6500 (Fred's firearms brand — TLO Outdoors is in his own public Facebook post; she has
quoted the post and the product name "TLO Gun Sling" but never the business name) · 6471 (StoreClaw's
Summit session is on the agenda; she answers with the product blurb).
**Note:** 6500 REGRESSED in the last round — it now denies the firearms business outright where it
previously surfaced the product. Worth diffing the two answers before changing anything.

#### 🔎 Verified 2026-09-08 00:38Z on staging `aa649e7b` — 1 of 3 still fails → FIXED IN CODE, awaiting staging apply
| id | result |
|---|---|
| 6499 Fred's brand | ⚠️ n/a as chained: the opener ("any members in the fire arms niche?") found nobody (Fred's niche field is not firearms), so she answered "eComCatalyst" — his agency, sourced from two of his posts — not the firearms brand |
| 6500 "his firearms business" | ❌ still present (exec 137838): the plan searched "fred firearms" as a topic, the evidence filled with Tamkin Collins's firearms posts, and she rebound "his" to Tamkin — "nothing on file ties Fred to a firearms brand" — while his own posts (content_items 104754 "My brand is outdoor hunting/firearm/tactical gear… paracord gun sling", 105132) never came back |
| 6471 StoreClaw at the Summit | ✅ standing offer + event offer gated to registered attendees + people + page (the agenda slot is moot, the Summit is over) |

**Root cause:** nothing scoped the follow-up to the person of the previous turn. **Fix:** `scripts/olivia_loop/apply_141_pronoun_subject.py` — `Plan Request` `pronounSubject()`: a message of ≤16 words with a third-person pronoun and no new capitalised name keeps the person the previous plan was about (`p_member` of a member-card turn, `p_author` of an author-scoped search); on a content search the raw search is scoped to that author and their name leads the digest terms. `test_141_pronoun_subject.js` 12/12; #143 45/45 and #174 30/30 unchanged on the patched node. The "TLO Outdoors" name the bank cites is not in the warehouse text (his posts say "outdoor hunting/firearm/tactical gear", "gun sling") — the bar is his own posts, sourced.

#### ✅ BUILT + STAGED + PROVEN 2026-09-08 in three cuts (staging `b39b31ab` → `b82f752e` → `f4e40708` → `c28fb532`) — awaiting Andy's promote
**Correction first:** "TLO Outdoors" IS in the warehouse — content_items 103886, Fred's own Facebook post of 2026-01-09 ("…private label items on the TLO Outdoors brand name … in the hunting, firearm accessory, and tactical gear space"), 1,326 chars into a 7,417-char body. Nothing had ever put that post in front of the model.
**The fix, three laps:** `apply_141_pronoun_subject.py` (lap 1: `pronounSubject()` keeps the person of the previous plan; raw search scoped to them on the content-search lane) · `apply_141b_topic_carry.py` (lap 2, exec 137893: the router had put the follow-up on the MEMBER-CARD lane, where the carry never ran and the raw fetch searched his name as a term — the carry now covers `member_card` too and ranks by the message's DISTINCTIVE words, `pronounTopicTerms()`; lap 3, exec 137951: with `p_author` set the name as a term ranked forty comments that mention him above his own posts, so the TLO post sat past the preload cap — `pronounRawTerms()` builds raw `p_terms` from the distinctive words only, minus every piece of the name). Applied with the batch runner.

| AC | result |
|---|---|
| 6500 "What is his firearms business called?" names the business from his own post, sourced | ✅ exec 138001 (row 65875): raw `{p_author: "Fred McKinnon", p_terms: ["firearms"]}` → the TLO post ranks 2nd of 40, inside the 1,600-char tier → "Fred's brand is *TLO Outdoors* — he posted about it directly on Facebook … hunting, firearm accessory, and tactical gear space. Here's that post: …/posts/24579392111737625/" |
| "his" stays bound to Fred, never to another member's firearms posts | ✅ 138001 (and 137951, 137893 before it): no Tamkin Collins in the evidence or the answer (was exec 137838) |
| the previous two turns keep answering (6499 shape) | ✅ rows 65871 / 65873: St Simons Island, Georgia · *E-BusinessOnline* — unchanged |
| unit | ✅ `test_141_pronoun_subject.js` 23/23 on the live bytes (12 lap-1 · 7 lap-2 · 4 lap-3 cases) |
| gate GREEN | ✅ 323 checks, `GATE_EXIT=0` |

**Before → after:** "nothing on file ties Fred to a firearms brand" (137838, rebound to Tamkin) → "nothing on Fred McKinnon's profile about a firearms business" (137893, card lane) → "nothing points to firearms" (137951, name-ranked) → **"Fred's brand is *TLO Outdoors*"** with the post link (138001). **Remainder, in writing:** content_items 104754 ("outdoor hunting/firearm/tactical gear… paracord gun sling") is still unreachable by the term "firearm" — the full-text parser reads `hunting/firearm/tactical` as one path token (handbook §13); the TLO post carries the answer, so the ticket's bar is met without it. 6471 unchanged (✅ 00:38Z).

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

#### 🔎 Verified 2026-09-08 00:46Z on staging `aa649e7b` — 1 of 3 still clamps, and it is a rule false positive → FIXED IN CODE (the clamp itself untouched)
| id | result |
|---|---|
| 6093 "How high can a ball jump" | ✅ friendly one-liner out of scope, no clamp (row 65745) |
| 7045 "Which app do you recommend for this?" | ✅ names the missing antecedent, one clarifier (row 65747) |
| 6483 "I'm Ivan Ong. What sessions…" | ❌ clamped (exec 137871) — but every draft did the right thing ("I can't take a typed name as identification, so I'm answering from your own record, Andy"); the IDENTITY second-person rule fires on any "your record" while a name was typed, three laps, canned line |

**Fix (precision, not the clamp):** `scripts/olivia_loop/apply_142_identity_precision.py` — Gate Verdict `secondPersonAboutOther()`: the rule stands down when the draft names the real asker or explicitly refuses the typed name; the Lisa failure (personalising FOR the typed name) still fires. `test_142_identity_precision.js` 9/9. Staging apply + re-probe pending the #169 handover.

#### ✅ BUILT + STAGED + PROVEN 2026-09-08 (staging `b39b31ab` → `c28fb532`) — awaiting Andy's promote · the clamp itself untouched
**The fix:** `scripts/olivia_loop/apply_142_identity_precision.py` — `Gate Verdict` `secondPersonAboutOther()` replaces the inline IDENTITY second-person rule: it stands down when the draft names the real asker or explicitly refuses the typed name; personalising FOR the typed name (the Lisa failure) still fires. Applied with the batch runner (one PUT, one bounce).

| AC | result |
|---|---|
| 6483 ships a real answer, not the canned line | ✅ exec 137904 (row 65795): the lap-3 draft "Just so you know, I can't take a typed name as identification … Based on your profile interests (Amazon FBA …)" carries a typed name AND "your profile" — the old rule blocked exactly that shape (exec 137871); it passed. exec 137962 (row 65845): one lap, pass, real agenda |
| the Lisa shape still raises the claim | ✅ unit "Lisa failure still fires" — `test_142_identity_precision.js` 9/9 on the live bytes of every cut |
| 6093 · 7045 unchanged | ✅ verified 00:46Z (rows 65745 / 65747), no identity rule on their path, not re-fired |
| gate GREEN | ✅ 323 checks, `GATE_EXIT=0` |

**Before → after:** 6483 three laps → canned line (exec 137871) → a real answer (137904, 137962). **Remainder, in writing:** in 137904 laps 1–2 were failed by the Haiku fact check's OWN identity ruling ("the draft accepts 'Ivan Ong' as the member's identity" — on a draft that refused it); that is the clamp's intermittent half (size M) and is not touched here — the deterministic rule no longer adds a third failure on top of it.

### #143 · A follow-up binds to the wrong thing, or loses the thread — 3 fails
**🟡 S2 · size S — filed 2026-08-24 · scoped 2026-09-07 (night) from the original rows + tonight's staging probes (Andy: "check backlog for more cases, address them one by one").**
**IDs:** 6095 (names the 20M+ chat now but not its verification bar or application route) · 6201 (gives
the profile instead of the WhatsApp footprint) · 6349 ("yes please" restates the credit balance instead
of acting on the offer she just made).

> **In plain words:** four small ways a "yes" or a short follow-up lands on the wrong thing — all deterministic
> binding code, none of them the model.

*As a member, my short reply lands on what she just put in front of me: a yes to "file this with the team" files it,
"the second one" opens the second item, a new question is never mistaken for a yes, and a bold number is never treated
as something she offered.*

**What the original rows show (read 2026-09-07, `olivia_messages`):** 6349 = Etienne 2026-08-04 (23044–23047): she found no
credit balance and offered *"Want me to file this as a report so the team can check…?"* — her own wording, not the seed's
exact ticket sentence, so `ticketYes` (which needs `open a ticket with the mds team` in her last turn) never fired; the
bank re-run replayed the billing plan and restated the balance; the live turn claimed "Done — I've filed that" without a
ticket. 6095 = 2026-08-01 (17095–17098): the original run answered it RIGHT (route `chats`, the +1M TTM step-up chat with its
verification bar and Typeform); tonight's staging probe (exec 137656) echo-bound "Is there any bigger revenue group" on the
word *revenue* from her offer line ("narrow this list by niche or revenue band") — `_poEcho` only refuses a trailing "?" and
the member typed none — and narrowed the PEOPLE list by band instead. Tonight also: "How much MDS credit do I have?" → "Yes
please" (exec 137650) bound to the bold `*$3,615.00*` as an offered item (the #112 recorder counts every bold span, and a
bare affirmation binds whatever it recorded); and "the second one" after a three-video list (exec 137667) reached the model
unbound (ordinals are read only as quantifiers inside an acceptance) — the seed rule still answered the right item both times.
6201 is a LANE question (the dossier lane answers a from-WhatsApp ask with the profile) — out of this ticket, see the
handoff desk.

**Shape of the fix (code, four guards — `test_143_followup_guards.js` runs them against the shipped bytes):** ① `Plan Request`
`isNewQuestion()` — the #174 opener guard applied to the echo signal too: a message opening any/who/when/where/how many/is
there/… never binds as an acceptance · ② `Format Reply` records bold spans as offered titles only when the reply ENDS with an
offer question, and a numeric/currency bold never · ③ `Format Reply` records a report/ticket offer in her own words as
`pending_offer.kind:'ticket'` (the reply's last line offers to file/open/flag a report/ticket/issue); `Plan Request`'s
`ticketYes` accepts that kind on a yes, so the two-step ticket lane fires and the ticket is actually created · ④ `Plan
Request` `bareOrdinalPick()` — "the second one" / "first" / "the last one" after an offer of ≥2 items binds to that item as a
drill-down (same bound path as #174).

**Accept when:** staging chains — "How much MDS credit do I have?" → "Yes please" no longer binds to the balance (no offer:
answered as a nudge; with her ticket offer: a ticket row) · "…tiktok ballers" → "Is there any bigger revenue group" is not
echo-bound (fresh plan, the step-up chat or a clarifier) · a list then "the second one" → `offer_bind.mode:'drilldown'` on
the second item · #174 + #112 probes unchanged · gate GREEN · promote.

#### ✅ BUILT + STAGED + PROVEN 2026-09-08 00:14Z — awaiting Andy's promote (staging `eb99c336` = #169 Task 5+6 + #174 + #175 + #143)
**The fix:** `scripts/olivia_loop/apply_143_followup_guards.py` (idempotent, carries its own upgrade path — five cuts landed on staging tonight, each probed): `Plan Request` `isNewQuestion()` on the echo signal · `bareOrdinalPick()` · `ticketYes` on `pending_offer.kind:'ticket'` · a `nothing_pending` lane for a yes after a turn that asked nothing (`Prep Context.last_olivia_asks` — a trailing "?" OR a statement-form offer on the last line) · `Format Reply` `offerTitlesOf()` (bold is a title only under an offer question, never a number) + `ticketOfferLine()` (verb-based: flag / file / raise / escalate / open a ticket / pass on / let the team know) · `Answer Seed`: the exact ticket sentence is the ONLY way she offers to flag anything to the team, and she never claims a request was filed unless the ticket lane ran. Offline: `test_143_followup_guards.js` 45/45 on the shipped bytes, `test_174` 30/30 regression.

| AC | result |
|---|---|
| "How much MDS credit do I have?" → "Yes please" no longer binds to the balance | ✅ exec 137713: no `pending_offer` recorded (the bold `*$3,615.00*` is not a title) · exec 137739 (she asked nothing): `nothing_pending` → "Just to double check — what would you like me to do next?" · rows 65653/65655 (she offered "let me know if you'd like to put in a request"): no fake "Done" — a two-step ticket offer ending "reply YES and I'll file it with the MDS team" |
| "…tiktok ballers" → "Is there any bigger revenue group" is not echo-bound | ✅ execs 137716 and 137752: `offer_bind` absent, fresh `member_match` by band (the step-up chat vs people is a content preference, not binding — left) |
| a list then "the second one" → `offer_bind.mode:'drilldown'` on the second item | ✅ exec 137720: `drilldown ids:['69853b…']`, full Peter-Paul Maan summary (row 65589) |
| #174 + #112 probes unchanged | ✅ list + "yes" → exec 137746 `accept`, 3 ids · Andy's chain after a list without the Chiru video → videos lane (137723) · "How many MDS chapters" → "yes" → rows 65659/65661 delivered (offer question → bound as before) |
| gate GREEN | ✅ four runs tonight, last 00:14Z, EXIT 0 |
| promote | ⏳ Andy's call — one graph, four tickets |

**Before → after:** bank C 6349 shape: a yes to her own-words report offer → plan replay restating the balance (bank) / a fake "Done — I've filed that" (live 23047, and staging 65577 before the cut) → the two-step ticket lane, or an honest "what would you like me to do next?" when nothing was offered. 6095 shape: "Is there any bigger revenue group" echo-bound on *revenue* (137656) → fresh plan. Bare ordinal: unbound (137667) → drill-down (137720).
**Tried and reverted, in writing:** re-issuing the previous plan for a titles-only offer ("20 chapters … want the full list?" → yes) put the full `chapter_info` payload in front of the model — it is TRUNCATED in the evidence after 14 rows — so it invented the remaining names, the fact check failed twice and the clamp fired (exec 137759). The zero-fetch answer from memory is the lesser evil; **list-tool evidence clipping** is a found-alongside defect (unfiled). **Not exercised live:** `pending_offer.kind:'ticket'` → `ticket_create` end to end (her exact-sentence offer takes the older `TICKET_OFFER_MARK` path; unit cases 36–45 cover the own-words detector). 6201 (dossier lane on a from-WhatsApp ask) is out of this ticket.

### #144 · 2027 events answered wrong — BLOCKED on #123
**🔴 S1 — filed 2026-08-24. Cannot be fixed until #123 lands.**
**IDs:** 6370 · 6372 · 6400. The 2027 events the bar wants (Centurion Summit California, Summit Cancun)
live in the events CATALOG, and every `event_*` call is misrouted to the schedule endpoint (#123), so
the catalog is unreachable. No prompt change can reach them.

#### 🔎 Verified 2026-09-08 00:44Z on staging `aa649e7b` — the catalog IS reachable now (plan lane `event_lookup`); 1 of 3 still fails → FIXED IN CODE, awaiting staging apply
| id | result |
|---|---|
| 6370 2027 events | ✅ Inspire 2027 Las Vegas (Mar 22) · Niseko (Jan 22) · Centurion Summit California (Jun 2) · Summit Cancun (Sep 26) with links (row 65729) |
| 6372 "let me know when they announce the main meetup for 2027" | ❌ one turn later, planned as a content search: "I don't have anything announced yet for the main annual Summit in 2027" — contradicting her own previous turn (row 65731); honest about not pinging ✅ |
| 6400 Inspire 2027 details | ✅ date · city · registration open · 44 registered · link, consistent with the turn before (row 65737) |

**What changed since filing:** the zeroth fetch's `event_lookup_v3` reaches the events catalog, so 2027 events answer right on a fresh question; #123 (the loop's `event_*` dispatch to the schedule route) still bites `event_who` (see #140 · 6267). **Fix for 6372:** `scripts/olivia_loop/apply_144_events_lane_carry.py` — `Plan Request` `eventsLaneCarry()`: a follow-up of ≤20 words after an `event_lookup` turn that names an event word or a year stays in the events lane with those terms; ticket and offer acceptances keep precedence. `test_144_events_lane_carry.js` 9/9.

#### ✅ BUILT + STAGED + PROVEN 2026-09-08 (staging `b39b31ab` → `c28fb532`) — awaiting Andy's promote
**The fix:** `scripts/olivia_loop/apply_144_events_lane_carry.py` — `Plan Request` `eventsLaneCarry()`: a follow-up of ≤20 words after an `event_lookup` turn that names an event word or a year stays in the events lane, with the year and the event word added to the terms (ticket and offer acceptances keep precedence). Applied with the batch runner `apply_batch_139_142_141_144.py` (one PUT, one bounce).

| AC | result |
|---|---|
| 6372: one turn after the 2027 list, "Can you let me know when they announce the main meetup for 2027? This year is Singapore" stays in the events lane | ✅ exec 137902 (`op:event_lookup` · `intent:events` · `followup:true`) and exec 137954 (terms `2027 · announce · meetup · singapore`) |
| the answer agrees with her previous turn | ✅ rows 65791 and 65833: "Good news — it's already been announced! … *MDS Summit Cancun 2027* … September 26, 2027" (was "I don't have anything announced yet", row 65731) |
| 6370 keeps passing | ✅ rows 65789 / 65831 — Inspire · Niseko · Centurion Summit California · Summit Cancun 2027, each with its link (6400 not re-fired: same lane, unchanged) |
| unit | ✅ `test_144_events_lane_carry.js` 9/9 on the live bytes of every cut (`b39b31ab` · `b82f752e` · `f4e40708` · `c28fb532`) |
| gate GREEN | ✅ 323 checks, `GATE_EXIT=0` (01:29Z; a first run at 01:14Z, while the probe run was live, had one transient FAIL in the v1 consent check — re-run clean, no code between) |

**Before → after:** 6372 replayed as a content search and contradicted the turn before (row 65731) → events lane, same facts as the turn before (rows 65791, 65833). **Remainder, in writing:** the carry itself was not exercised live — the router chose `events` on both runs, so `eventsLaneCarry()` stood by; its path is proven offline (9/9) and stays as the deterministic backstop. #123 (`event_who` → the schedule route) is still open — see #140 · 6267.

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

#### 🔎 Verified 2026-09-08 00:50Z on staging `aa649e7b` — unchanged by design
6002 "What data do you have access to?" and 6190 "ok what data points do you have" both return the canned help card (route `help`, rows 65767/65769): sources named in member words, examples, no asker-specific scoping ("chats limited to yours, the rest community-wide") and no real gaps. Exactly the state the ticket describes; the fix is the capability-led card or an evidence-fed answer (size M). Not touched in this pass.

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
**🔴 S1 · size S — filed 2026-08-22 from #97's final whole-branch review (I7); Andy: "ok" to file + ship as its own ticket, not inside #97**

> **In plain words:** the n8n webhook that receives WhatsApp messages accepts ANY post from anyone — it never checks the delivery really came from Meta. Before intros, a forged post could only make Mille answer a fake question; now a forged "Accept intro" tap could release two members' numbers to each other. Meta signs every delivery; we ignore the signature.

*As the owner, every inbound the assistant acts on is provably from Meta — a forged webhook post is dropped before any node runs.*

**Spec (one Code node, first after `WA Inbound (POST)`, staging → promote):** compute `HMAC-SHA256(raw request body, META_APP_SECRET)`; compare constant-time to the `X-Hub-Signature-256` header (`sha256=<hex>`); mismatch/missing → return null (drop) + one Slack `Notify Team` line with the source IP; match → pass through unchanged. The app secret lives in n8n as a credential/env, never in node JS. Needs the RAW body (n8n webhook `rawBody` option) — verify the staging webhook node exposes it before writing the node. Probe: a crafted unsigned post (the exact T4/T5 probe technique) must now be dropped; a real member message must still flow; Meta's own deliveries carry the header (verify on a live event in `olivia_webhook_events` payload headers if persisted, else on the webhook node's input). Mitigation already shipped in #97: taps bind to the exact template wamid (`consent_wamid`), so a forged Accept without the real wamid does nothing.

**Accept when:** unsigned probe dropped (execution shows the drop, zero downstream nodes) · real inbound unaffected (one live turn) · selftest/probe tooling updated to sign its crafted posts (or use a staging-only bypass secret — Andy's call) · gate GREEN · promote.


#### ✅ #105 ENFORCING 2026-09-10 — a forged webhook post is refused before anything runs

**Story:** *As the owner, every inbound the assistant acts on is provably from Meta — a forged webhook post is dropped before any node runs.*

**The ticket's spec was wrong, and finding that out was most of the day.** It said "one Code node, first
after `WA Inbound (POST)`". Meta does not post to n8n. Its callback URL is the relay at
`digest.mds.co/api/olivia/webhook`, which forwards to n8n **without** the signature header — `OLIVIA_HANDBOOK.md`
line 72 has said so since 2026-07-21. Built to spec, promoted to prod `021bb4b6`, and **rolled back within
eight minutes**. Andy's own test message settled it: `user-agent: node`, forwarded via `74.220.48.55`, no
`x-hub-signature-256`. A check anywhere downstream of the relay sees no signature on ANY real delivery and
would refuse every member.

**Where it lives now.** The relay verifies the raw bytes it already reads. The app secret is in **Supabase
Vault**, the on-switch in an `olivia_alarm_config` row, both read through `digest.meta_webhook_config()` and
cached 5 minutes — so rotating the secret or enforcing needs **no deploy** and puts no plaintext in Render.
n8n could not hold it at all: `$env` and `$vars` read empty on this plan, `$secrets` is undefined, and the
Variables page 404s.

**Three stages, each pinned by a test.** No secret → forward. Secret, no enforce → verify, record, forward
(**where we are**). Enforce → refuse, 403 never 502, because 502 asks Meta to retry and a forgery must not be.
Enforcement is ignored without a secret, and an unreachable database degrades to "not configured" and forwards
— a blip must never become every member refused.

**AC checklist:**
1. Unsigned probe dropped, zero downstream — ✅ **live**: an unsigned post to the relay returns **403** and is never forwarded to n8n.
2. Real inbound unaffected — ✅ nothing is refused; a live relay post returned 200 and forwarded.
3. Probe tooling signs — ✅ **moot**: the health ping and uptime probe post to n8n directly and never touch the relay.
4. Gate GREEN — ✅ 346 checks, including the new `meta_signature.js` check.
5. Promote — ✅ deployed `d5d6bff`, enforcement ON (`meta_webhook_enforce = '1'`, 2026-09-10 04:47Z).

**How it was proven.** Andy sent one WhatsApp message; Meta's delivery and its status callbacks recorded
**`ok` × 3** in `digest.meta_webhook_verdicts` — genuine Meta traffic verifying against the Vault secret. Only then
was the switch flipped. An unsigned post to the relay now returns **403**. `missing_signature × 2` in the table is
my own two test posts, nothing legitimate.

**Rollback, no deploy:** `update digest.olivia_alarm_config set v = '0' where k = 'meta_webhook_enforce';` —
effective within the 5-minute config cache. Watch `digest.meta_webhook_verdicts`: a rising `mismatch` or
`missing_signature` alongside falling `ok` is the signal to flip it back.

**Dead end, do not retry:** Meta will not self-trigger a delivery — `subscriptions_sample` is "Unknown path
components" on v18/v19/v20/v21 even with an app token built inside Postgres.

**The side door is shut too (2026-09-10 05:22Z, prod `2b568155`).** Locking Meta's front door still left the n8n
webhook reachable directly by anyone who knew its URL, so a forgery could have skipped the signature check by
going straight there. `WA Inbound (POST)` now requires a shared secret (`X-Olivia-Relay`, n8n credential
`kKOzVnAzRFE0ZiVN`), minted into Vault as `OLIVIA_RELAY_SECRET` — its value was never printed or written to disk.

**Checking before locking found three more callers**, not one: the in-app widget, the iOS ask route, and the
webhook-liveness probe the health dashboard reads. Locking without them would have broken all three, and the
liveness tile would have gone red while probing a door that always said no. All four now go through one helper
(`n8nWebhookHeaders()`), and the health ping (a Postgres function) carries it too. **Senders first, then the lock**
— both halves were live and verified before `WA Inbound` started refusing.

**Proven on prod:** a direct post with no secret → **403** · health ping, liveness probe and a genuine
signature-verified delivery through the relay → all **200**, `X-Olivia-Relay` present, exec 141997/141996/141992.
`rawBody` removed from `WA Inbound` in the same promote — the signature check lives at the relay now and nothing
downstream reads the raw bytes.

**Artefacts:** `src/lib/meta-signature.ts` · `meta-webhook-config.ts` · the relay route, 21+7+4 tests written
before the code · `scripts/olivia_loop/meta_signature.js` + gate check · `digest.meta_signature_ok()` ·
`meta_webhook_config()` · `meta_webhook_record()` · `meta_webhook_verdicts`. Rollback point:
`olivia_snapshots/prod_2026-09-10T032618Z_pre-promote.json`.

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

### #187 · Millie has never recorded how long a turn takes
#### ✅ #187 CLOSED 2026-09-10 — the first turn this system has ever timed

**Story:** *As the owner, I can see how long Millie is taking to answer, so a slowdown shows up as a number instead of as a member complaint.*

**Before:** 13,309 turns, **0 with a latency**. Every figure this project had ever quoted — median 22.8s, worst
56.1s — came from eight hand-timed probes during #23.

**After:** `Save Conversation` records `latency_ms` on the answer row. Meta stamps the member's send in whole
seconds, so the number is the **member-perceived wait**, Meta's own delivery hop included, clamped at 0 because a
phone's clock can run ahead. The question row carries the key as null — latency belongs to the answer, not to the
asking.

**Live proof, staging then promoted:** a real turn measured **23,838 ms**, which lands on the 22.8s the hand-timed
probes had estimated. Prod `22d81380`, gate GREEN, probe rows removed.

**Caught on staging, and worth recording.** The first attempt added the key to the answer row only. PostgREST
rejects a bulk insert whose objects have different keys (`PGRST102 — All object keys must match`), so that version
saved **nothing at all** — it would have stopped every turn being recorded. Staging is why prod never saw it.

**Not in scope, from the retired #72:** queue wait as a separate number, and any load generation.

**🅿️ SPRINT 5 · 🔵 S3 · size S — filed 2026-09-10 (Andy: "move it to sprint 5 - s3"), carved out of the retired #72 (Andy: "I think this is an old ticket. I don't want to do a 100-probe.")**

> **In plain words:** we cannot answer "is Millie slower this week than last", because nothing has ever written down how long an answer took.

*As the owner, I can see how long Millie is taking to answer, so a slowdown shows up as a number instead of as a member complaint.*

**Verified live 2026-09-10:** `digest.olivia_messages` holds **13,309 turns and 0 with a `latency_ms`**, from
2026-07-17 to today. The column exists and nothing has ever written to it. Every latency figure this project has
ever quoted — median 22.8s, worst 56.1s — came from **eight hand-timed staging probes** during #23. The one live
number we do have is incidental: the web door returns `latency_ms` in its own response (22,756 ms on the #105
probe), and it is thrown away.

**Why it survived #72's retirement.** The load test was aimed at a demo that has since happened. This half is not:
it pays off on an ordinary Tuesday, it needs no load and no hundred of anything, and it turns any future
"how does she cope under pressure" question into a query rather than a project.

**Accept when:**
1. `latency_ms` is written on 100% of new turns, WhatsApp and web alike.
2. Queue wait is recorded separately from generation time — a turn that waited 30s and answered in 3 is a different
   problem from the reverse, and one number cannot tell them apart.
3. A single query returns p50, p95 and max over a window, and it is written down where the next session will find it.
4. Nothing in the answer path gets slower to measure it, and a failure to record can never fail a turn.
5. Gate GREEN.

**Not in scope, deliberately:** any load generation, any concurrency target, any go/no-go. Those were #72's and
they are retired with it.

### #72 · LOAD TEST before the Mille demo — 100 people at once, on a system that has never seen 6
**❌ RETIRED 2026-09-10 by Andy: "I think this is an old ticket. I don't want to do a 100-probe."** It was filed
for a demo two weeks out — the August Summit, which has been and gone — and the board later re-aimed it at the
announcement without re-examining whether a 100-probe run was still the right instrument. It is not. **The
telemetry half is carved out as #187 and is the part that still pays.** Everything below is kept for the
measurements, which are still the best picture of real load we have.

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
#### ⬛ ADDED 2026-09-02 — decisions out of SQL (external architecture review, first finding)

- The reviewer's first finding on our structure: **logic lives in several places, including the database.** The ruling
  below still stands — retrieval, gating and stats STAY in Postgres (set operations over 40k+ rows; the security boundary
  the leak gate proves). What moves is **decisions**: who counts as active, what "restricted" means, time decay,
  disclosure, matching policy, "is this member registered".
- **Work item:** inventory the 116 `digest` functions as *read* vs *decision*. Each decision moves into the Render route
  that owns its lane and the RPC shrinks to a plain read; n8n keeps calling the route (Andy's rule 2026-08-17: new lanes
  are app routes, not RPCs). **First slice = #147** (one definition of "registered"); second = activity status (#125's
  rule, the one that bit last).
- **Extra accept criteria:** no decision rule has two definitions (graph / SQL / TypeScript) · each moved lane carries unit
  tests + the bank re-run · the handbook lists where every rule lives. The schema side is #158.

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
**🔵 S3 · size M — filed 2026-08-06. Architecture is CORRECT (Andy confirmed); these are gaps
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
**🔵 S3 · size M — filed 2026-08-08**

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
**🔵 S3 · size L — filed 2026-08-06 (Andy: "mapping becomes a paramount task… this number will go up rapidly")**

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

### #158 · Foreign keys on what we own, and a nightly orphan check — the #61 follow-up
**🔵 S3 · size M — filed 2026-09-02 from the external architecture review (second finding: "the majority of tables are not connected") · Andy: "go"**

> **In plain words:** 73 tables, and only 17 carry a foreign key. 28 tables hold a member id; 25 of them are joined by
> convention, nothing in the database checks it. #61 proved the joins are clean TODAY (0 orphans). This ticket makes the
> database enforce the ones we own, writes down why the mirrors cannot be enforced, and watches all of them every night.

*As the owner, every row we create about a member points at one member record the database enforces, and a broken join
shows up on the health card within a day — never in a wrong answer months later.*

**Evidence (live 2026-09-02, information_schema):** 73 base tables · 17 with any FK (19 constraints) · 28 tables with a
member key column (`at_member_id` / phone / FB id), 25 of them with no FK at all · 116 functions · 16 views. #61 (2026-08-12)
measured 0 orphans across 18 `at_member_id` joins + 7 other relations and named the safe-FK candidates in `FORMS_ERD.md`
§3.5: 18 tables → `member_profiles.at_member_id`, `event_registrations.event_at_id → events_catalog.at_record_id`,
`member_edges.a_id/b_id → member_profiles`. It stopped short of adding them because "safe" needs each loader read for
insert order, not a point-in-time count. Past cost of convention-only joins: 737 duplicate FB member ids, `digest.members`
keyed per phone, an empty `member_events` nobody noticed.

**Shape of the fix:**
1. **Spine:** `member_profiles.at_member_id` is the declared root (#61's finding); `digest.member_identity` (#77) stays the
   crosswalk to the WA-layer `members` table — no new key.
2. **Constraints on what we own:** for each of the 20 candidates, read its loader for insert order, pick the `ON DELETE`
   rule (RESTRICT for ledgers such as olivia_messages/sends/intros; never CASCADE on a mirror), ship one migration per
   table group, each proven by a full loader re-run + the nightly chain + `zoom_weekly` green.
3. **Mirrors stay FK-free, on purpose:** Airtable, WhatsApp, Zoom, GroupOS and Facebook rows carry their source's id and
   the source does not guarantee integrity — every such column keeps (or gets) a `COMMENT` saying so (31 exist from #61).
4. **Nightly orphan check:** one job runs the #61 query set (orphans per implicit relation, owned AND mirror), stamps
   heartbeat `integrity_check`, and a tools-health row shows it (red on any orphan > 0 or a missed run).

**Accept when**
- Every owned table with a member/event key has its FK (list in the close block) · every mirror key column has a written reason.
- All loaders, the nightly chain and `zoom_weekly` run green twice after the constraints land; no job double-runs or fails on insert order.
- Heartbeat + tile live; a deliberately seeded orphan turns the tile red within a day and clears when removed.
- `db/` re-exported in the same commit as each migration · gate GREEN.

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
**🔵 S3 · size M — filed 2026-08-06 (Andy: "comparing last year's cohort to this year's, on every single field")**

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
**🔵 S3 · size M — filed 2026-08-08**

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
**🔵 S3 · size S — filed 2026-08-19 (Andy: "we connected singapore, but we will have more") · ⏸ builds when event #2's export exists**

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
**🟡 S2 · size M — filed 2026-08-07 from Andy's own WhatsApp session (18:11–18:13 local)**

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
**⚪ S4 · size L**

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


#### ✅ #115 CLOSED 2026-09-10 — one real wrong answer, one real corruption, one non-issue

**Story:** *As a member, the attributes Millie counts and matches me by are the ones I actually gave, spelled one way.*

**Part 1 — country. The ticket asked for a fold at derive time; that turns out not to be the problem.**
`member_count` and `member_match_v2` already call `digest.country_fold()` at query time, so `US` (2,216 rows) and
`United States` (454) have never been two different answers to a member. Folding at derive would be tidier, not
more correct.

**What WAS wrong, and it was answering members wrongly: `IS` folded to `iceland`.** Five members were counted and
matched as Icelandic. Every `IS` row carries an Israeli city or state — Jerusalem, Herzlia, Ness Ziona,
Rishon LeZion, state "Israel" — and there is no Icelandic member. Evidence beats the ISO table, and the function
already had this precedent: `ne` was mapped to netherlands for exactly the same reason in August. Also folded the
three values that are not countries at all (`N/A` ×11, `hello`, a settings URL) to NULL — unknown is honest.

**Part 2 — 8 corrupt business-model rows, real and now gone.** They carried a single array element that should be
two: `OEM Design & Development'Wholesale and/or Arbitrage`, an apostrophe where a delimiter belonged upstream.
`digest.attr_list()` now splits on **lowercase-apostrophe-uppercase only**, which that value matches and ordinary
apostrophes do not — proven: `Men's Health` and `L'Oreal` survive intact. The 8 stored rows were repaired to match;
**0 corrupt rows remain**, and the two real values now count 159 and 127 members.

**Part 3 — the "4 WA-layer resellers with non-current AT status" need no fix.** The two layers agree on every one,
and there are 38 non-current resellers in total, not 4. `digest.is_active_member_status()` returns **false for
every single one**, so none is reachable by a member-facing lane. The guard already does the job the ticket was
worried about.

**Before → after:** 5 members on the wrong continent · 8 rows carrying a value no filter could match → both fixed
at the source so the next derive keeps them fixed, gate GREEN.


#### ✅ #117 CLOSED 2026-09-10 — a `+` in a URL is a space, and it was guarding Andy's own history

**Story:** *As whoever runs the self-test, `--cleanup` removes the turns it created and nothing else.*

**Cause.** The cleanup hand-built a PostgREST URL carrying `created_at=gte.<timestamp>`, and a timestamp ends
`+00:00`. **A `+` in a URL query string IS A SPACE**, so the filter was malformed, matched nothing, and every run
printed "cleanup done" while deleting no messages at all. That trap is already written down in this project
(`reference_postgrest_plus_is_space`) — it bit its own tooling.

**It had piled up: 5,104 probe questions and 5,104 answers were sitting in `digest.olivia_messages`** — more than a
third of all 13,309 turns — plus 91 orphaned `olivia_seen` rows. Not neutral: `prod_pulse` and the outage alarm both
read that table to ask "is Millie answering".

**Sharper than the ticket said.** `PROBE_PHONE` is **Andy's own number** — "the only member whose phone may be
simulated" — so that bound was the only thing between the cleanup and his real conversation. Matching nothing was
the *lucky* failure; the same defect parsed differently deletes real member turns, and that cannot be undone.

**The fix removes the bound entirely.** `digest.selftest_cleanup(p_dry_run, p_phone)` identifies test turns exactly:
a probe question by its `wamid.SELFTEST…` wamid, which a real inbound can never carry; its answer by sitting between
that question and the next member row, since `id` is a sequence. `--cleanup` now **dry-runs by default** and needs
`--yes` to delete.

**Proven end to end on the hardest case** — a probe answer and a real answer side by side, both with no wamid:
| row | outcome |
|---|---|
| probe question (`wamid.SELFTEST_117PROOF`) | deleted |
| its answer, no wamid | deleted |
| REAL question (`wamid.HBgLREAL117`) | **survived** |
| its answer, no wamid | **survived** |

The 1:1 dry-run count across the whole table (5,104 questions ↔ 5,104 answers) corroborates the rule.

**⚠️ Left for Andy, deliberately.** Purging the 5,104-turn backlog is 10,208 irreversible deletions on his own
conversation history. The tool is fixed and proven; the one-time purge is his call:
`python3 scripts/olivia_selftest.py --cleanup --yes`.


#### ✅ #188 CLOSED 2026-09-10 — a tile that reported one writer under another's name

**🩺 ⚪ S4 · size XS — found 2026-09-10 while verifying #179's tile on the live health report.**

**Story:** *As MDS staff, when a tile says something is behind, the name on it is the thing that is behind.*

One tile covers TWO writers — `member_profiles` (daily) and `events_catalog` (hourly) — because one GitHub job
writes both and an events-only staleness is a real failure mode. It surfaced whichever half was worse, but only
that half's **timestamp**, under the tile's member-profiles **name**.

**Live at the moment it was found:** `member_profiles` 13.2h old and healthy, `events_catalog` ~2h old and
degraded, and the tile read *"Member profiles ← Airtable sync — last write 2h ago"*. Anyone acting on it would
check `member_profiles`, find it perfectly fresh, and never learn the events catalog was behind. Same family as
#180 — a headline that does not describe what it is reporting.

**Fix:** `worseOfSyncHalves()` names the writer in the line when the worse half is unhealthy, and says nothing
extra when both are fine. 5 tests written first. 1,345 pass, tsc/eslint/build clean, live `2208d78`.

**Worth knowing:** the amber itself is **not** a new problem — the events catalog running ~2h behind an hourly
schedule is **#181**, which is blocked on a GitHub PAT with `actions:write`. This ticket is only about the tile
telling the truth about which one it means.


#### ✅ #189 CLOSED 2026-09-10 — the persona builder could not say why it failed, so nobody knew

**🟡 S2 · size S — found 2026-09-10 doing #64's runtime inventory (`launchctl` said `com.mds.persona.refresh` last exited 1).**

**Story:** *As MDS staff, when the persona builder fails I can see why, and it does not fail for a reason we could have fixed months ago.*

**How bad it was.** The log's own history: `built 61 · failed 0` → `built 122 · failed 28` → `built 740 · failed 16`
→ **`built 12 · failed 19`** — a **61% failure rate** on the last real run, and 229 FAIL lines in the log overall.
Every one reported identically: *"builder returned no valid JSON"*.

**Why nobody knew the cause.** `haiku()` wrapped the whole call in `except Exception: pass`. An API error, a curl
timeout, a truncated answer and a genuinely unparseable one all came out as the same sentence. The failure was
**unobservable** — the same theme as #180 and #117 tonight.

**What it actually was, probed rather than guessed.** At the job's own concurrency of 5: the API is healthy, no
call errors, nothing truncates (output 1.9-3.6k against a 6,000 cap), and failures are **intermittent parse
failures on clean 200s**, about 1 in 20. The parser was
`json.loads(txt[txt.index("{"):txt.rindex("}")+1])` — which breaks the moment the model adds a closing sentence
containing a brace, or wraps the JSON in a fence and says something after it. `rindex` reaches past the object and
takes the stray brace with it.

**Fix.** A string- and escape-aware brace walker takes the **first complete** JSON object and ignores whatever
follows; and every failure now reports its real reason — `curl exit N`, `api overloaded_error: …`,
`truncated (raise max_tokens)`, `missing focus/summary`, or the unparseable text itself.

**Proof, old parser vs new, on the shapes that matter:**
| answer shape | old | new |
|---|---|---|
| plain object | ✅ | ✅ |
| fenced, prose after | ❌ | ✅ |
| prose after with a stray brace | ❌ | ✅ |
| braces inside strings / escaped quotes | ✅ | ✅ |
| no object / truncated | correctly fails | correctly fails |

**Live:** `persona_refresh.py --limit 40` → **built 40 · failed 0** (previous real run: 12 built, 19 failed), then
a full pass → **built 19 · failed 0**, ending `staleness after: missing 0 · older-than-35d 0`. **59 personas rebuilt
tonight, zero failures**, and the staleness backlog is clear. (The "759 due" in the fingerprint list is the active
roster, not the rebuild queue — only 59 were actually stale.)

**⚠️ Where this lives.** `/Users/Born/mds-scorecard-tools/` is **not a git repository** — `persona_refresh.py` and
`olivia_eval.py` are single-copy untracked files on Andy's Mac. A `.bak-20260910` was taken before editing. That
is a #64 finding in its own right and worse than the ticket's "eight plists exist only on Andy's Mac".


#### 📝 #190 · The nightly eval sits at 9.5% FAIL against Andy's <1% bar

**🔴 S1 · size M — filed 2026-09-10 from #64's inventory (`launchctl` said `com.mds.olivia-eval` last exited 1).**

**Story:** *As the owner, the eval tells me the answer quality is where I set it, and when it is not it tells me which failures to fix first.*

**The number:** 2026-09-09, **220 judged · PASS 195 · PARTIAL 4 · FAIL 21 = 9.5%**, against a **<1%** bar
(`feedback_olivia_quality_target_1pct`). Nearly ten times over.

**It is not diffuse — two classes are 86% of it:**
| class | fails | rate |
|---|---|---|
| `false_denial` — she says she cannot find what she has | **10** | 4.5% |
| `wrong_fact` | **8** | 3.6% |
| everything else (`no_answer`, `over_refusal`, `fabrication`) | 3 | 1.4% |

**And it clusters by source:** CROSS 31% · VIDEO 30% · EVENT 27% · WA_DIGEST 17%, while PARTNER, FORM, DECLINE and
REAL are all at **0%**. So the refusal behaviour and the partner lane are healthy; the multi-source and
catalog-backed lanes are not.

**🔴 Three of the 21 are ONE known bug, and I proved it rather than assuming.** All three EVENT failures are
`false_denial`, and every answer she denied is in `digest.events_catalog`:

| eval question | denied | the catalog holds |
|---|---|---|
| Q2040 what time the *SoFlo Chapter TikTok Tour Afterparty* starts | the time | **18:30**, 2025-11-13, Miami |
| Q2042 what type the *TikTok Shop (Verified Sellers) Channel Meetup* is | the type | **Virtual** |
| Q2023 where the *Billion Dollar Seller Summit Recommended Event* is | the place | **Kaua'i, Hawaii** |

That is **#123**: the four `event_*` tool names all route to the schedule route by prefix match, so `event_lookup`
and `event_history` answer from the Summit `event` schema and **never consult the events catalog**. The handbook
says so in §6.2. **#123 is worth more than its current priority** — it is 14% of the eval's failures on its own.

**Where to start:** #123 first (proven, 3 fails, already understood), then the CROSS class (5 fails, the worst
rate at 31%) which is multi-source retrieval, then VIDEO (3 fails, 30%).

#### ✅ CLOSED 2026-09-11 — a fresh 100-question exit exam, an honest number, and the failures named by mechanism

**Andy's call at the top of the session: "do fresh 100" — a new bank, not the old one.** Both banks were old: the
nightly `eval_bank_v2.json` was built 2026-07-25 (50 of its 220 machine-generated, 0 ever retired) and the locked 100
was frozen 2026-08-16 and last fired 08-23. Since 08-16 members asked **4,058 real questions** (141 askers) that no
bank had ever seen. **`eval_bank_exam_2026-09-11.json` is 100 of them** — deduped against both old banks, quota'd by
what members actually ask (TACTICS 14 · CHAT_CONTENT 13 · VIDEOS 12 · EXPERT 10 · MEMBER 10 · EVENTS 7 · CAPABILITY 8
· the rest 26), every truth verified in the warehouse the same day by five parallel read-only agents (238 SQL reads).

**Results.** Fired at PROD `b4db92d0`, 04:36–05:20Z: **100 judged · PASS 78 · PARTIAL 8 · FAIL 14 (14.0 %)**,
100/100 answered, every turn HTTP 200, $3.05. Then **every one of the 14 was re-fired and read by hand**:
**7 reproduce · 5 do not · 2 are the bank's own error** (5057 described Andy's own application record correctly;
5098 is a follow-up whose "they" the eval's reset deletes). **The honest defect rate is 7 %.**
Full triage: **`OLIVIA_EXAM_190_TRIAGE.md`**.

**The 7 are four mechanisms, and two of them are most of it.**
| mechanism | ids | what it is |
|---|---|---|
| ① a column we hold that no tool returns | 5100 · 5060 | `view_count` is in `videos_catalog` but not in `video_search_v2`'s RETURNS TABLE; **Brand Name** is in no gated function at all (`grep -rl "Brand Name" db/functions/` = nothing) → **#201** |
| ② one lane denies while another holds it | 5071 · 5097 | "MDS 9" is 4 events + a video set, denied by `community_info`; "Trybe" is spelled **"Tribe"** in the Singapore transcript → **#203** |
| ③ the wrong lane answers | 5022 | "how do i join the supplements channel" ran `chat_recommendations` with no query and recommended TikTok → **#202** |
| ④ coverage stated as a feeling | 5047 | "the further back the thinner" instead of 4,283 posts, 2021-08-17 → 2026-09-10, 5 predate 2025 → **#206** |

**Found alongside, NOT chased (Andy's rule):** **#204** — an exact revenue figure (£14.5M) reached an answer in
Millie's own voice, in the exam **and** in a real member conversation on 2026-09-04 (`olivia_messages` 62689). The
figure is public (MDS's own welcome post) so it is quotable, but only attributed with its link and paired with the
band. **S1, privacy.** · **#205** — `Build Prompt` cuts Facebook posts ranked 4-10 at 500 chars and the answer's fact
sat at char 658 (the Advisory Council deadline, Q2103).

**The nightly bank was overstating Millie by about 2×.** The 13 questions that failed three nights running were
re-probed on staging: 3 fixed by #123 · 1 passes now · **4 were stale or wrong truths** · 2 ambiguous questions ·
3 synthetic CROSS mash-ups that can only half-pass · **1 real defect (#205)**. All five bad v2 truths were rewritten
(snapshot `eval_bank_snapshots/eval_bank_v2_2026-09-11_truths-refreshed.json`), so tonight's 03:30 nightly is the
first run judged against truths that match the warehouse.

**AC checklist.**
| AC | result |
|---|---|
| 1. One valid full run on prod after #191's fix, report committed, number real | ✅ `OLIVIA_EVAL_2026-09-11.md` — 100/100 answered, 0 refusals (the 09-10 nightly had died 403 at 188 of 220) |
| 2. No FAIL is the bank lying — stale truths fixed | ✅ 5 v2 truths rewritten + 2 exam truths corrected; each named in the triage |
| 3. The sticky set triaged: every fail → a fix or a ticket, ranked by mechanism | ✅ 13 sticky + 14 exam fails, all classified; 5 tickets filed (#201-#206) |
| 4. Re-run below 9.5 % | ❌ **not met and not attempted** — nothing was fixed this session by design (the tickets are the fix), and the exam is a different, harder bank. Measured honestly instead: 14 % judged, **7 % reproducing**. |

**Before → after.** *Before:* one bank, 220 questions, 50 of them machine-written, truths from 2026-07-25, last valid
run 09-09 at 9.5 % — with no way to tell a Millie defect from a stale truth. *After:* a 100-question exam of real
member asks with same-day truths, **14 % judged / 7 % reproducing**, every failure named by mechanism and owned by a
ticket, and the nightly's own truths repaired. Gate **367/0 exit 0**, prod n8n `b4db92d0` untouched all session.

### #148 · The WA members mirror never reconciles — 12 rows Airtable stopped returning are frozen forever
**🔵 S3 · size S — filed 2026-08-25 from #126's audit.**

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

#### ✅ CLOSED 2026-09-10 — LIVE on prod `b4db92d0` (promoted 17:56Z, snapshot `prod_2026-09-10T175648Z_123-event-catalog-routing.json`)
**The fix:** `Answer Tool` routed by `String($json.tool_name||'').startsWith('event_')`, so all four event
tools landed on `https://digest.mds.co/api/olivia/schedule`. That route parses only
op/phone/q/at/event_id/lead/in_minutes — **`p_terms` is dropped** — and always loads
`events?order=starts_at.desc&limit=1` from the `event` schema, which today is the single row **MDS Summit
Singapore, ended 2026-08-26**. Every event question therefore got an over-event's agenda. Now the two
schedule-backed tools are named explicitly (`event_schedule`, `event_who`) and the two catalog tools fall
through to PostgREST, where `Attach Embedding`'s `EXEC_NAME` has always renamed them
(`event_lookup → event_lookup_v3`, `event_history → event_history_v2`); both are granted to `service_role`,
and `Answer Parse` already injects `p_phone`, so the RPC path needed nothing else.
`scripts/olivia_loop/apply_123_event_catalog_routing.py` (`--dry-run DIR` first), staging `9d91109e`.
An offline check of the patched expression routes all 8 tool names correctly.

**Fold-in, and it is LIVE now, not staged:** `digest.event_lookup` printed `(time as listed: 18:30 UTC)`
for rows with no `app_starts_at`, and the routing fix put that in a member answer as "6:30 PM UTC" for a
Miami evening event. The catalog stores the **listed clock time**, not a UTC instant, and only 19 of 1,455
rows carry `app_timezone`, so the honest fix is to claim no zone: `(time as listed: 18:30)`. Applied with
`CREATE OR REPLACE` (the ACL stays); a shared function is live on prod the moment it is applied, so this
half is already in front of members. Rollback is the inverse one-token replace.

| AC | result |
|---|---|
| an `event_lookup` call reaches the catalog RPC and returns catalog rows | ✅ staging turns 67946/67947 and the two before it — 3/3 of #190's EVENT failures now answered |
| the running event's catalog row shows a correct start and a live registration link (no "already happened") | ✅ "MDS Ecom Founder Dinner at Accelerate 2026" → Tue Sep 22 2026, 7:00 PM, Seattle, 32 spots left, member RSVP + guest luma link |
| A4071 still passes for the right reason, from the right source | ⚠️ **not testable as written** — A4071 is not in the live bank (`eval_bank_v2.json`). Its live equivalent is **2035** "What city is the MDS Summit being held in?", which now answers **MDS Summit Cancun 2027, Cancun, Mexico, Sep 26 2027** from the catalog. Correct today, since Singapore is past — but if the bank's stored truth still says Singapore, the judge will mark it FAIL. **Bank truth needs a look, the routing does not.** |
| a side event asked about by name answers from the catalog with its own RSVP link | ✅ same Accelerate dinner answer, both links |
| `event_history` reaches its RPC too | ✅ "what events am i registered for?" → the asker's own 4 past events, no upcoming, from `event_history_v2` |
| gate EXIT 0 | ✅ `scripts/olivia_leak_gate.py` — **346 checks, 0 FAIL, exit 0** (exit code read directly, not through `tail`) |

**Before → after** on the three EVENT failures from the 2026-09-09 eval:

| question | before (17:35Z) | after (17:40Z+) |
|---|---|---|
| what time does the SoFlo Chapter TikTok Tour Afterparty start | *"I'm not finding a 'SoFlo Chapter TikTok Tour Afterparty' on file anywhere"* | *"it took place Thursday, November 13, 2025 at 6:30 PM, in Miami, as part of the SoFlo Chapter"* |
| what type of event is the TikTok Shop (Verified Sellers) Channel Meetup | denied | *"was a virtual event — Thursday, November 7, 2024"* |
| where is the Billion Dollar Seller Summit Recommended Event | denied | *"held in Kaua'i, Hawaii — a past event, from Saturday, May 18, 2024"* plus its event page |

**Re-verified on prod after the promote (not on staging).** Turn 68019: *"The SoFlo Chapter TikTok Tour Afterparty already happened — it was Thu, Nov 13, 2025, listed at 6:30 PM, in Miami"* — the catalog row, and the zone claim gone with it. Second lane: *"The TikTok Shop (Verified Sellers) Channel Meetup was a Virtual event — Thu, Nov 7, 2024"* with its listing link. Gate re-run against prod: **346 checks, 0 FAIL, exit 0**.

**Left alone deliberately:** `Answer Merge` still carries the A4077 workaround that detects a schedule-shaped
payload coming back from an `event_lookup*` call and tells Millie not to narrate the mismatch. With routing
fixed it never fires; it stays as the tripwire if anyone re-broadens that route. The duplicate `event_lookup`
key in `Attach Embedding`'s `EXEC_NAME` literal (v2 then v3, last one wins) is untouched — it is confusing
but correct, and #123 is not the place to re-open that node.

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

### #162 · Transcripts for the 33 videos published 25 Aug–4 Sep — AssemblyAI, in-person rooms
**🔴 S1 · size S — filed 2026-09-04 (Andy: "we need to create transcripts for recently fetched videos").**

> **In plain words:** 33 recent talks are in the library but Olivia cannot quote a word of them.

*As a member, when I ask what Kevan Soh said about PPC negation or which AI Mastermind talk covered
inventory forecasting, Olivia quotes the talk with a timestamp and the library link, gated by my
entitlement.*
Evidence: fresh GroupOS listing 2026-09-04 = 212 videos in 2026, 50 published since 25 Aug; 17 carried
transcripts (16 Summit AAI batch of 25 Aug + Josh Hadley via Zoom), **33 had none** — 16 AI Mastermind
(restricted), 8 AI Scaling Live + 4 Summit day-2 (public), 5 of them brand-new uploads not even in the
catalog (weekly check: NEW 5, CHANGED 1). Andy's 30 S3 links returned `403 AccessDenied` for every
anonymous GET until the dev changed the bucket policy the same day (all 30 → 206 afterwards). These are
in-person rooms: no Zoom, AssemblyAI is the only producer (Andy: Otter PDFs are NOT a source).
**Shape of the fix:** catalog upsert from the fresh dump · `aai_submit.py --year 2026` on a CSV built
from the listing (`download_link` = the now-public S3 URL, `_mds` block from the catalog) ·
`aai_transcripts.py --apply` · `video_summaries.py` now counts chunk-backed videos as transcript-backed
(it read `digest.calls` only, so every AAI batch had hand-written summaries) · embed · entitlement sweep
for the 5 new restricted videos · gate.
**Accept when:** 33/33 carry `call_transcript` chunks, max chunk ≤ 4,000 chars, timestamps monotonic ·
33/33 have `summary_source='transcript'` and a vector (0 unembedded) · the 5 new restricted videos have
`video_access` rows (members-per-video > 0) · live probe through `content_search_v2`: an entitled asker
gets Kevan's quote with a timestamp + `app.mds.co/videos/6a95ecb56c44f146b77f4941`, an unentitled asker
gets nothing from an AI Mastermind talk · gate GREEN, exit 0.

#### ✅ BUILT + LOADED + PROVEN 2026-09-04 — warehouse only, no promote needed
**The fix:** catalog upsert from a fresh 212-video 2026 listing (5 NEW + 1 CHANGED) · `aai_submit.py --year 2026` on a CSV built
from the listing (`download_link` = the bare S3 URL — the dev opened `videos/*.mp4` to anonymous GET the same afternoon; every
link was `403 AccessDenied` before that) — 33/33, 11.4 hr audio, $2.62, 5 min wall, 0 errors · `aai_transcripts.py --dir
~/mds_transcripts/batch_20260904 --apply` (an isolated dir, so the 161 older 2026 files are NOT re-chunked with the new
`split_long_cues`) → 697 chunks · `video_summaries.py` now counts chunk-backed videos as transcript-backed (it read
`digest.calls` only, so every AAI batch needed hand-written summaries) → 33 Haiku summaries · embed 697 rows + 33 videos ·
AI-Mastermind entitlement sweep, TAG-FILTERED (`videos_list(for_user_id, tag_id=6a2c3eab1c4bb3440b9a6cf5,
created_after=2026-08-31)`: an empty result comes back inline, so 743 roster calls in 19 batches cost 44 files, not 743) →
44 entitled members × 21 AI-Mastermind videos, 508 new `video_access` rows.

| AC | result |
|---|---|
| 33/33 carry `call_transcript` chunks, max chunk ≤ 4,000 chars, timestamps monotonic | ✅ 33 videos · 697 chunks · 0 non-monotonic · 264 restricted chunks carry the `video_access` rule · **max chunk 4,202 chars** — one chunk over the 4,000 target, the same class as the 25 Aug batch's 4,163 (sentence-bounded split) |
| 33/33 have `summary_source='transcript'` and a vector, 0 unembedded | ✅ 33/33 transcript summaries · 0 unembedded chunks · 0 unembedded videos (21 restricted embed metadata only) |
| the 5 new restricted videos have `video_access` rows, members-per-video > 0 | ✅ 44 grants on each of the 5 · restricted published 429 → 429 with grants, **0 uncovered** |
| entitled asker gets the quote with timestamp + library link, unentitled gets nothing from an AI Mastermind talk | ✅ `content_search_v2` as Brynne (entitled): Tracy Lin "Inventory Forecasting" chunks at 00:06:35 / 00:05:00 · as Gahan (unentitled): 0 rows from that talk · Kevan (public): 7 of 10 rows, `app.mds.co/videos/6a95ecb56c44f146b77f4941` · **E2E through the LIVE workflow** (selftest, `olivia_messages` 62711): "the whitelisting is what I think is more valuable" at 00:19:23 / 00:21:16 + the library link, then the follow-up offer |
| gate GREEN, exit 0 | ✅ leak gate PASSED after the chunk load and again after the grant load — 313 PASS · 0 FAIL |

**Before → after:** 2026 videos with a transcript 179 → **212 of 212** · library 411 → **444 of 1,086** transcribed · chunks
12,810 → 13,507 · `video_access` 44,972 → 45,480 rows · cost $2.62.
**Remainders (named, not fixed):** 13 target members have no GroupOS account, so no grants can exist for them
(mariela@ · jesse@ · kaylon@ · jerome@ and one nameless Staff row; john.cho@nutraville.com · shiva@joonhaircare.com ·
rishi.manda28@gmail.com · vineet@shoplc.com · xxz5838@hotmail.com · nick@eaccountable.com · reed@amazonstart.com ·
jeng0304@hotmail.com) · eugene@milliondollarsellers.com resolves to no `at_member_id` (row kept with the email) · the sweep
shows **32 members whose earlier AI-Mastermind grants no longer hold in GroupOS** and 10 who gained access — rows are
additive, nothing was deleted; revoking is Andy's call · the opened bucket also makes RESTRICTED talks' mp4s (and their
Otter transcript PDFs) world-readable — GroupOS side, GOS-32 class, on Andy's desk.
**Mapping audit (same day):** vectors 33/33 · categories 33/33 · speaker links on 33/33 (26 members · 5 guests · 3 unresolved:
Lee Lim, Elias Tiong, Shaurya Ithikkat; Operator Panel 2 of 3 names) · partner links 7 (description mentions) · Luke Lim ↔ Scale
Insights affiliation unset (no people on the partner's web profile) · 9 videos without `event_ids` (GroupOS) · letter map run
after the transcripts: 29 letters → people, 7 stay letters.



### #156 · Sonnet 5 vs GPT-5.6 Terra on the locked 100 bank — price + quality, prod untouched
**🟡 S2 · size S** · spec `docs/superpowers/specs/2026-09-02-olivia-sonnet-vs-terra-bench-design.md`

> **In plain words:** Same 100 member questions, answered by Claude and by OpenAI's equivalent model, cost and quality side by side, so the vendor choice is data. Nothing in the running product changes.

*As the owner paying Olivia's API bill, I want the same 100 member questions answered by Claude Sonnet 5 and GPT-5.6 Terra under identical conditions, with cost per answer and judged quality side by side, so I can decide on the vendor from data, without any change to the running product.*
Filed by Andy 2026-09-02 ("i want to test OpenAI vs Anthropic … 100 questions … price, quality … without interrupting prod"). Decisions in chat: model = `gpt-5.6-terra` (OpenAI's mid tier, $2/$0.20/$12 — the Sonnet 5 slot); dual judge (Sonnet primary, Terra cross-check); bench harness first, n8n port only if Terra wins. Prior art: #22 (Kimi, July: Sonnet 15.3% fail / $0.0135 vs Kimi 22.2% / $0.0270) and #32 lever 5.
**Shape of the fix:** the existing bench harness (`~/mds-scorecard-tools/kimi_bench.py` + `kimi_harvest.py`) gets an OpenAI path. One silent run of the locked bank at STAGING (lock held, no graph edits) is harvested for the exact `Answer Seed` bodies; both vendors replay those bodies through the same tool loop, same RPCs, same embeddings, warm cache, forced first fetch on both; two judges grade every answer; one compare report. Post-model steps (clamp, fact check, link repair) not run for either — model-independent.
**Accept when:** (a) 100/100 seeds from ONE staging run, prod exec log shows no bench traffic · (b) both models run warm, 0 loop errors or every error listed · (c) $/answer steady-state + cold per model from real usage counters at today's list prices · (d) fail % from the Sonnet judge, cross-checked by the Terra judge, disagreements listed · (e) one compare report with all 100 answer pairs · (f) staging left as found (diff identical), lock released.

#### ✅ BUILT + RUN + REPORTED 2026-09-02 — decision data delivered, nothing promoted
**The work:** bench harness brought to the 2026-09-02 graph — `bench_tools.py` mirrors the LIVE `Attach Embedding` / `Answer Tool` / `Answer Merge` nodes (error shape + FAILNOTE, `clipSafe`, `restrictFix`, the over-cap halving squeeze, `_v2/_v3` remap, app-route routing, arg coercion; verified by a 28-case differential against the node JS, 0 mismatches) · `kimi_harvest.py` keeps sequence history · `kimi_bench.py` runs the Anthropic loop as prod (6 calls, 5 tool rounds, thinking off, forced first fetch) and an OpenAI **Responses API** loop (chat completions refuses tools with reasoning on Terra) · dual judge (`olivia_eval.judge_prompt` shared, `judge_one` untouched) · `bench_compare.py` three-way report. 85 unit tests. One silent bank run on STAGING (16:37–17:17Z, lock held, no edits, diff identical before/after) harvested 92/100 seeds; the 8 missing are canned lanes that never reach the model (Q4022 4025 4026 4027 safety · 4036 4037 capability · 4094 4095 digest). Each vendor ran 2 passes (pass 2 scored, warm cache), both judges graded every answer. Warehouse identical across all three runs (peer-confirmed: no embeds between 15:28Z and 19:35Z).

| | Sonnet 5 (prod) | Terra medium | Terra none |
|---|---|---|---|
| FAIL % (Sonnet judge) | **5.4%** (83/4/5) | **3.3%** (81/8/3) | **7.6%** (78/7/7) |
| FAIL % (Terra judge) | 13.0% (79/1/12) | 9.8% (82/1/9) | 13.0% (77/3/12) |
| judge disagreements | 16 | 13 | 13 |
| $ / answer, warm | **$0.0211** | **$0.0310** | **$0.0237** |
| latency, median | 10.1 s | 19.4 s | 14.2 s |
| model calls / output tokens per answer | 2.1 / 448 | 2.7 / 332 | 2.4 / 216 |

| AC | result |
|---|---|
| (a) 100/100 seeds from ONE staging run, prod exec log shows no bench traffic | 92/100 seeds (8 canned-lane, unbenchable by construction); prod window 16:37–17:17Z: 14 executions, 0 SELFTEST, 1 real member turn; staging diff webhook-only before and after |
| (b) both models run warm, 0 loop errors or every error listed | pass 2 scored with 95–100% cache reads; 0 loop errors, 0 truncated calls on all three runs — after 4 Terra-medium rows (Q4009 4017 4047 4080) that died on OpenAI's tier-1 500K-TPM limit were re-run alone and merged (`merged_reruns` in the JSON); 1 Terra-judge TPM error on Sonnet Q4062 re-judged (PASS) |
| (c) $/answer steady-state + cold per model at today's list prices | Sonnet $0.0211 warm / $0.0616 cold · Terra-medium $0.0310 · Terra-none $0.0237 (OpenAI has no cache-write charge, so warm = cold); prices in the report |
| (d) fail % Sonnet judge, cross-checked by Terra judge, disagreements listed | table above; `OLIVIA_MODEL_COMPARE_2026-09-02.md` § Judge disagreements (42 lines) — most are the Terra judge failing honest-miss answers the rubric marks PASS |
| (e) one compare report with all answer pairs | `OLIVIA_MODEL_COMPARE_2026-09-02.md` — 92 questions × 3 answers × 2 verdicts |
| (f) staging left as found, lock released | `olivia_wf.py status` LOCK free (17:18Z), diff webhook-only |

**Before → after:** July #22 (72-question organic bank, July prompt): Sonnet 15.3% fail / $0.0135 vs Kimi 22.2% / $0.0270 → today (locked 100 bank, 2026-09-02 prompt): Sonnet 5.4% / $0.0211 · Terra-medium 3.3% / $0.0310 · Terra-none 7.6% / $0.0237. Not the same bank or prompt as July. Spend ≈ $25 (bench $10.8 measured · judges ≈ $6 · smokes ≈ $1.5 · harvest run ≈ $6 estimated).
**Remainders, named:** the prompt is Claude-tuned (bias against Terra, not corrected) · Answer Merge's S1–S16 evidence stamps and its other deterministic notes are not replicated, so the absolute fail % is not the daily eval's · post-model gates (Fact Check, clamp, link repair) not run for either · a question that exhausts the 5 tool rounds counts as a loop error here where prod ships "Sorry…" (none occurred) · the Terra judge is stricter than the rubric on honest misses (reading list for Andy, not auto-resolved) · OpenAI tier 1 (500K TPM) throttled the Terra runs (2–3 workers, ~40 min per run) · an n8n port is a separate ticket if Terra is chosen · Andy rotates the OpenAI key pasted into chat on 2026-09-02 · harness lives in the unversioned `~/mds-scorecard-tools/` (snapshot committed under `scripts/model_bench/`).


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

