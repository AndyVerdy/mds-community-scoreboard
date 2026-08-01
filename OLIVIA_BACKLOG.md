> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.


# Olivia — backlog

Rebuilt 2026-07-28 as stories. **S1 = highest priority, S4 = lowest.** Within each group, **smallest
first** — quick wins before the big ones.
Source: 219 raw items swept from every Olivia doc + the live request queue, deduped; five live
verifications run this session (results at the bottom).

**Effort** = dependencies + unknowns combined. S = known change, contained. M = touches a shared path
or has one real unknown. L = needs data or a decision we don't have yet.
**Impact** = members actually affected. Active membership 722; beta today is 4 testers + 11 invited.

---

**Severity key:** 🔴 S1 highest · 🟡 S2 · 🔵 S3 · ⚪ S4 lowest · ✅ done (bottom).

---

## RELEASE 2 — what we are working on <!-- keep current; the promote moment IS the release ship -->

**In progress on STAGING, ship date TBD.** Nothing here is on prod; it ALL rides the next
`promote`, which Andy runs. *(Release 1 = shipped Jul 30, ticket list at the bottom under
✅ Completed.)*
- ✅ on staging, proven: **eval fix batch 2026-07-31** — fact-gate member-question clamp 500→2000 +
  RULE TWO + URL-id post-filter + keep-supported regen (Q3091) · `content_search` `post_author` on
  comment rows + ATTRIBUTION rule (Q3078/Q3036) · `member_dossier` leads with persona (Q3004) —
  TEST 27Q = 0 FAIL, gate 161. *(SQL migrations are already live in the shared DB — the n8n graph
  half is what waits for promote.)*
- ⚠️ DRIFT CORRECTED 2026-07-31 (late): the **holding-trigger fix (arrival = message timestamp) is
  ALREADY LIVE ON PROD** — it rode the SECOND promote that night (03:24Z; prod `updatedAt`
  03:24:30, untouched since; fixed code read directly from the prod `Holding Trigger?` node, and
  every prod ladder exec today is a clean silent no-op). Earlier notes calling it staging-only were
  stale.
- ✅ **#23 answer latency — CLOSED 2026-07-31 on the story.** Router prompt caching (6,225
  tokens/turn now cache-read, proven exec 57677) + claim-free fact-gate skip (`Claims?`).
  ≤10s median NOT met and deliberately not bought — re-file a latency target after #7/#8.
- ✅ on staging, proven: **#5 counting** (`member_niches` + `member_count` w/ breakdown_sum + loop
  tool) · **#33 prod smoke** (early-feedback branch reorder + links-when-solving rule +
  `OLIVIA_SMOKE_CHECKLIST.md`) · **#6 chapters** (chapters_catalog 20/20 scraped + chapter_info
  w/ live counts == member_count + live_stats + asker_city; Andy's chain probe zero re-asks;
  gate 175).
- 🔨 NEXT: **promote on Andy's go** — **run `OLIVIA_SMOKE_CHECKLIST.md` on staging first, paste
  the result block in the session log.** Then #7 people search. Bank 3101-3112 swap is
  release-independent (eval instrument, not shipped code); FULL run on the new bank comes after
  these PBIs close.

**Rule:** every ✅ at the bottom is filed under its release; anything shipped after Jul 30 is
Release 2 = staging-only until the next promote.

---

## Definition of Done — one list, applies to EVERY item

Written once, true for everything that ships. Per-item conditions live under each story as
**Accept when**.

- **The failure class is counted, before and after.** A rate on the class, not a hand-picked question
  that passed. The bank is the instrument for the class rate — the headline score stays the daily
  routine, never a release gate.
- **No class is traded for another.** The rates it was not aiming at do not get worse.
- **The safety gate is GREEN** wherever retrieval or data access changed.
- **Proven on the live system**, with the evidence cited — execution id, SQL result or gate output.
  Never "should work".
- **Every lane it touches, or the exceptions are named in writing.** A route that skips the change is
  a hole, not a detail.
- **Written down the same session:** what shipped, what was measured, what is still open.

**Target ladder for every rate below:** under 10%, then under 5%, then under 1% wrong.

**EVERY MEMBER, ALWAYS (Andy 2026-07-30):** a data job's population is ALL active members, keyed by
`at_member_id` from `member_attributes` (748 today incl. Staff) — never "members with a
phone/WhatsApp". Phone, email, WA are channels and resolution keys, not the population; members not
on WA today may join tomorrow and their data must already be there. A job that genuinely must cover
a subset names the subset and the reason in writing. (Caught 2026-07-30: personas silently cut 203
phone-less actives; fixed same day.)

---

# 🔴 S1 — highest

*(no open S1 items — #21, #1, #26, #27, #28, #31 all closed 2026-07-30.)*

---

---

# 🟡 S2


# 🔵 S3

### 12. 🔵 Public revenue, double-sourced · S3 · effort S
*As a member, a public figure someone posted is quoted with its source, never as Olivia's claim.*

**Accept when**
- **Your ruling lands first:** may named members be ranked by revenue at all, or bands only.
- **Every figure carries the source it came from: 0% in her own voice.**
- **A member with no public figure gets the bracket only.**

Andy's rule: publicly-posted figures are fair game, double-sourced — "my data puts him in this bracket;
he also said in this post that…".

- Any figure carries the post or chat it came from
- Bracket and public figure presented together, both attributed
- **Blocked on:** whether a *ranking* of named members by revenue is allowed at all

**Impact:** low frequency, high sensitivity in a room of senior sellers.

### 13. ✅ Outage alarm · CLOSED 2026-08-01 · effort M · LIVE (not promote-gated)
*As the team, we hear about an outage in minutes, from a system that isn't the one that's broken.*

**LIVE NOW — this one does not ride the promote: it runs in SUPABASE pg_cron (off n8n, the
platform being watched), every 5 minutes, posting to Slack `#automation-tests` (C0AQ8USNQK0 —
one config row to change the channel).** Migrations `olivia_outage_alarm` +
`_net_schema_fix` (pg_net lives in schema `net`, not `extensions` — the first cut's qualified
calls would have silently no-opped inside the never-raise handlers; caught by pg_proc check).

**Three signals, every tick:**
1. **members-getting-failure-text** — any member received "Sorry — I could not generate…" in the
   last 10 min (SELFTEST + Andy excluded, so eval noise never pages). This is what the 07-26
   balance outage looked like to members.
2. **n8n-workflow-down** — the always-on relay's `relay_maintenance` markers flowing = Meta
   callbacks arriving while n8n is dead.
3. **webhook-ping** — an ACTIVE probe: each tick POSTs a synthetic delivery-status payload at
   the real prod webhook (no member traffic; upserts the `wamid.HEALTHPING` sends-row = a
   visible heartbeat); the next tick verifies 200.

**NO LATCH by construction** (the old monitor's fatal flaw): while a condition persists it
re-alerts every 30 min; on clear it posts ✅ recovery. The check function never raises and
stamps `last_tick_at` in config — the monitor itself is checkable.

**Proven by forcing failures (AC), all visible in Slack #automation-tests 2026-07-31 ~20:34 CDT:**
seeded failure-text canary → 🚨 alert (Slack API ok:true) · second run inside 30 min → paced, no
repost · stamp backdated 40 min → 🚨 re-alert "(still down — repeating every 30 min)" = unlatch
proof · canary cleared → ✅ recovery · webhook ping → 200 "Workflow was started" + HEALTHPING row ·
autonomous pg_cron tick verified. **Gate +2 → 186 GREEN** (anon denied on the check fn; alarm
config — which holds the Slack token — unreadable).

**Named exceptions / residuals:** Supabase itself is the monitor's blind spot (watching n8n from
Supabase satisfies the AC; a second cheap watcher for Supabase = #16's audit) · the
balance-runs-low PRE-warning + spend cap land in **#32** (the failure-text signal already catches
the member-visible effect, which is how 07-26 actually presented) · the old latched n8n monitor
stays as-is (harmless, on-platform; #16 decides its fate).

**Impact:** the team hears about the next 07-26 in ≤5 minutes instead of never.

---

### 32. 🔵 What Olivia costs, measured and controlled · S3 · effort M · **DEFERRED TO THE BIG-SMOKE PHASE (Andy 2026-08-01: measure spend there, give Kimi a fair retest chance and try to improve things — not a standalone ticket now)**
*As the team, we know what Olivia costs to run per answer and per month, we get told before a bill
surprises us, and we can prove a cost change actually landed.*

Nothing in the backlog has ever owned running cost. What exists is scattered and none of it
measures PRODUCTION: the eval runner has a daily spend cap + ledger (`.eval_spend.json`, built
after the $161 incident), #22 priced Kimi against Claude on a bench, and per-answer figures were
estimated inside #21 and #23. **We have never measured a real month of member traffic**, and the
2026-07-31 router-caching win is arithmetic off published prices, not a number anyone verified.

**What we used to spend (measured, sources named)**
| when | figure | source |
|---|---|---|
| pre-2026-07-29 loop | **$0.035 / answer** | #21 before its 3 cache breakpoints + Haiku fact-gate |
| after cache breakpoints (2026-07-29) | **$0.007-0.010 / answer**, ~99% cached | #21 close |
| head-to-head bench (2026-07-29) | **$0.0135 / answer** Sonnet 5 · $0.0270 Kimi K2.6 | #22, equal conditions |
| one FULL 100-Q eval run | **~$3.05** | 2026-07-30 full-bank run |
| a bad day of eval iteration | **~$35** (11 runs) · worst logged day **$40.60** (07-28) | `.eval_spend.json` |
| the incident that forced the cap | **$161 in one day** | 2026-07-26 |
| eval spend, last 6 logged days | 11.22 · 9.46 · 40.60 · 11.69 · 9.52 · 6.71 | `.eval_spend.json` |

**What we expect to spend (projection — the first job of this ticket is to replace it with a
measurement)**
- Real member traffic today: **275 questions / 30 days from 24 members = ~9.2 questions a day**
  (SELFTEST and Andy's number excluded).
- At the bench's $0.0135/answer that is **~$0.12/day, ~$3.70/month** of member-facing spend.
  Olivia's production cost is currently *rounding error next to the eval runs* — the eval line
  (~$10-40 on an active day) is where the money actually goes.
- **At full membership** (748 actives) at the same ~11 questions/member/month: ~8,200 answers/month
  → **~$110/month**. That is the number to design for, and the reason the router caching matters.
- **Router caching (2026-07-31, #23)**: 6,225 of ~6,450 routing tokens now served from cache
  (proven live, exec 57677). ~10× cheaper on that block *inside the 5-min cache window*; a lone
  message after a gap pays a cache WRITE at ~1.25×. Net effect on sparse beta traffic is UNVERIFIED
  — bursts win, isolated messages lose slightly.

**Accept when**
- **A real per-answer and per-month cost, measured from production traffic**, not sticker price —
  the token counters are already in every exec (`in_tok`/`out_tok`/`cache_w`/`cache_r` ride the
  loop state and land in `metrics`); the job is to persist and total them, split
  **member traffic vs eval traffic** so one never hides the other.
- **The router-caching claim is settled with a number** — cached vs uncached cost per routed turn
  on real traffic, including how often the 5-min window is actually hit. If sparse traffic makes it
  a net loss, say so and revert it.
- **A spike alarm exists and has fired once in a test** — a day over a threshold reaches a human.
  A $161 day must never again be discovered afterwards. (Alarm plumbing overlaps #13.)
- **RETEST KIMI.** #22 closed as no-swap on 2026-07-29 with real numbers (Kimi 38.9% FAIL vs 15.3%,
  60.7s median vs 7.5s, 2× the cost per answer despite a cheaper token rate — it wrote 4× the output
  and made 1.6× the tool calls). That verdict has a shelf life: **re-run the bench when a new Kimi
  generation ships or at the next quarter, whichever comes first**, and re-run it on the harness
  that already exists — `mds-scorecard-tools/{kimi_harvest,kimi_bench,bench_compare}.py`, which
  touches no workflow and cost ~$5.50 last time. Same bar as #22: organic-bank score ≥ current,
  leak gate GREEN, latency in band, kill switch exercised. **Two blockers to re-check first, they
  killed it last time regardless of price:** every Kimi model on our key forces thinking on, and
  their API refuses `tool_choice: required` alongside it — so our forced first fetch, the mechanical
  rule that stops her answering before she looks at data, cannot be enforced at all. If that is
  still true, the retest ends there and no price justifies the swap.
- **Written down with the numbers**, per the global DoD.
- **REPORTED TO PAVEL.** The finished numbers go to Pavel, not just into this repo — measured
  per-answer and per-month cost, member vs eval split, the router-caching verdict, the projection
  at full membership, and the Kimi retest outcome. Andy sends it (drafts get confirmed before
  anything goes out, per [[feedback_confirm_before_sending_messages]]).

**Impact:** no member sees this, but an unmeasured bill is how a pilot dies. Cheap to do — the
counters already exist.

---

### 29. 🔵 Matchmaking & recommendations, built like the platforms build them · S3 · effort L
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

### 14. 🔵 Conversational, not robotic · S3 · **→ BIG-SMOKE ACCEPTANCE CRITERIA (Andy 2026-08-01: not a build ticket — its ACs are checked AT the smoke test: follow-up class rate on the FULL run · capped-answer-continues · uses-what-she-knows · Andy's own feel verdict; anything still robotic becomes a named fix then).** Written 2026-07-28 about the pre-loop system; the loop + #2/#5/#6/#7/#8 absorbed the concrete bullets
*As a member, it follows what I mean, keeps context, and reads like someone who knows MDS.*

**Accept when**
- **Follow-ups carry the thread** — at or under the current target rung for the class, with the member
  never repeating themselves.
- **A capped answer continues on request.**
- **She uses what she already knows about the asker without being asked for it.**
- **"I don't have that" appears only where nothing exists.**

Andy's own read: "it feels like a bot very restricted to me."

- Follow-ups keep the thread — "yes", "what about Austin", "total it up" work without repeating myself
- One capped answer isn't the end of the conversation
- She uses what she knows about me without being asked
- Fewer "I don't have that" walls, more "here's what I do have"

**Effort L** — cuts across routing, retrieval and prompt; hardest to define done. Needs its own session on what good looks like. **Impact:** every member, every conversation — the difference between used and abandoned.

### 15. 🔵 Hands-off data pipeline · S3 · effort L
*As a member, what happened yesterday is answerable today.*

**Accept when**
- **A full capture cycle runs with nobody touching it.**
- **Content is searchable the day it lands.**
- **A skipped sync alerts** — proven by forcing a skip.
- **Manual steps per week: 0.**

Facebook still needs a manual scroll twice a week; the member-profile sync sits on a scheduler known to
skip runs and was dead three days; new Facebook posts aren't searchable until two manual steps run.
**Also (verified 2026-07-30): Voyage embedding of new content is a MANUAL step** — `embed_backfill.py`
(nulls-only, resumable) runs by hand in the capture SOP; skip it and new posts silently lose the
semantic layer (keyword FTS still works) until the next run. Today: 958 new rows / 0 unembedded, so
the SOP held — but "searchable the day it lands" must include the embedding, scheduled not remembered.

- Facebook capture runs without a person
- The member sync runs on a reliable trigger and alerts when it doesn't
- New posts searchable the day they land

**Effort L** — the Facebook half fights a platform that keeps changing. **Impact:** every member; the most visible staleness.

---

---

# ⚪ S4 — lowest

### 16. ⚪ Health dashboard audit · S4 · effort M
*As the team, the health dashboard tells the truth.*

**Accept when**
- **Every tile: break the thing, the tile goes red, and a person receives it.** A tile that cannot go
  red is the defect.
- **A failure inside a step never passes as a healthy run.**

Andy: "I don't think it's working. I haven't seen Olivia down." **Confirmed — it isn't.** Every tile
audited: does it go red when the thing is actually broken, and does anyone receive it. Overlaps #13.

**Impact:** indirect; it's how we find out about everything else.

### 17. ⚪ Auto-refresh videos and partners · S4 · effort M
*As a member, new recordings and deals show up without anyone importing them.*

**Accept when**
- **Blocked until the GroupOS key exists.**
- **New videos and deals appear without an import**, and data older than a day alerts.
- **The requirements are handed over, the security exposure included**, and it is fixed or owned in writing.

13 videos landed in a week and none surfaced in any catch-up; partner data sits on a frozen snapshot.
Needs the GroupOS key. Includes sending GroupOS the 13-item requirements doc — one of which is a live
security exposure: restricted decks are publicly downloadable.

**Effort M** — blocked on a key we don't have. **Impact:** everyone asking what's new; the security item is urgent on its own terms.

### 18. ⚪ How-MDS-works answers · S4 · effort M
*As a member, I get the real answer about Squads, programs and joining a chat.*

**Accept when**
- **Every recurring how-MDS-works question has a written answer from the team.**
- **Each answers consistently across phrasings and cites that source.**
- **They stop arriving as support requests.**

From the team's own documents rather than inferred from chat chatter. Also unblocks the chapter policy
questions in #9.

**Effort M** — the work is someone writing the answers; loading them is straightforward. **Impact:** all 722; every one of these currently becomes a support request.

### 19. ⚪ Privacy: share, keep, delete · S4 · effort M
*As a member, I know what's stored about me and can have it removed.*

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

### 20. ⚪ Census into the warehouse · S4 · effort L
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

### 34. 🏁 Finalize the QA doc set — THE LAST TICKET, runs after everything else · effort M
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
- **THE BIG SMOKE has actually run** — one full pass, results pasted into the session log, class
  rates on the ladder, #14 feel verdict + #32 cost/Kimi done — and the 5-check gate is GREEN.
- **Anything the smoke surfaces is either fixed or filed** before the promote.

**Impact:** this is the gate between "backlog closed" and "one big release" — it's how we know
the release is actually safe to ship, not just that the tickets are marked done.

---

---

# ✅ Completed

## 📦 RELEASE 2 — on STAGING, not yet promoted

Ships to prod at the next `promote` (Andy runs it). Everything below is live on staging and gate
GREEN 161, and nothing here is on prod yet.

**Tickets closed into Release 2 (9):** #23 answer latency (closed on the story — the ladder half
shipped in Release 1, the speed cuts in Release 2) · **#5 counting** (member_niches + member_count
RPC + loop tool; breakdown_sum closes total-it-up deterministically) · **#33 prod smoke**
(early-feedback branch reorder + links-when-solving rule + the standing pre-promote smoke
checklist `OLIVIA_SMOKE_CHECKLIST.md`) · **#6 chapters, end to end** · **#7 people search that
understands meaning** (pg_trgm names + profile embeddings w/ RRF + place aliases + the
member_match target-mode fix) · **#8 every source on every question** (cross-source floor +
merge + solve fan-out rules · multi_source all six families · per-turn sources_used telemetry) · **#9 revenue brackets, one rule** (ruling = CU page 06: Most Recent
Revenue authoritative; rev_band already derives from it by one threshold rule; gate now enforces
band-only outputs) · **#10 shareable member facts** (`OLIVIA_SHAREABLE_FIELDS.md` rulebook ·
card = the per-member list incl. channels/model/categories/country · gate pins the column set) · **#11 payment wording** (map inside member_billing —
raw system words structurally unemittable).

**Shipped to PROD separately (not part of the n8n promote):** #25 the portal tells the truth —
mds-digest-web `294b094`, live on digest.mds.co 2026-07-31. The portal deploys on push and never
waits for the workflow promote.

**Also staged, not ticketed as PBIs:** the eval fix batch 2026-07-31 (fact-gate clamp + RULE TWO,
`content_search` `post_author`, `member_dossier` persona) · the holding-trigger fix (arrival =
message timestamp).

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

