> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.

# Olivia — backlog (open items only)

Releases 1+2 SHIPPED to prod 2026-08-03 (versionId `90a13237` · prod smoke 3.6% < 5%).
Everything shipped lives in `OLIVIA_BACKLOG_ARCHIVE.md` — nothing completed appears here.
**Order below = the working order (Andy 2026-08-03: architecture first).**

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

---

# 🔴 NOW — architecture (Release 3 IS this — Andy 2026-08-03)

**Source of truth: `OLIVIA_ARCHITECTURE_AUDIT_2026-08-02.md`** — Appendix A holds the exact
SQL behind every number; **re-run it after each ticket for the before/after diff**. Regression
instrument = the 169-question smoke bank (prod baseline 2026-08-03: **3.6%**).

**Release-3 exit = ticket #43: the audit RE-RUNS and re-scores ≥8/10** (baseline 2026-08-03: **6/10**):

| Dimension | Now | Target | Moved by |
|---|---|---|---|
| Retrieval quality | **3** | ≥7 | **#40** |
| Identity resolution | **6** | ≥8 | **#41 + #45** (reg 62%→95%, 61 unkeyed, FB dupes) |
| Semantic coverage | 8 | 9 | #40's corpus filter (junk out of the index) |
| Event log | **0** | feed live | **#46** (portal+Olivia now) + Andy's app feed (GROUPOS_PAT) |
| Graph | 0 | starts | **#44** (weighted edges; opens after #29's memo, LAST) |
| Scale 10 · Gate 9 · Layers 8 | — | hold | every ticket: gate GREEN + A9 unchanged |


### 40. 🟡 BUILT + STAGED 2026-08-03 — Retrieval rewrite (RRF) · remaining: smoke slice (Andy's go) + prod flip · → RELEASE 3 (audit P1+P3)
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
**Remaining to close:** ① smoke/TEST slice ≤ 3.6% with no class regressing (eval RUN = propose
+ Andy's go) · ② prod flip = promote (the staging graph carries the swap) **+ same-moment
migration pointing the 3 SQL wrappers that still call v1 internally — `multi_source`,
`app_member_feed`, `persona_signals` — at v2, + NOTIFY pgrst + REST hammer** · ③ v1 retired
after soak.

### 41. 🔴 Identity stamping — olivia_messages.member + ingest paths · effort S · → RELEASE 3 (audit P4, Andy's worked spec)
*As the team, every Olivia conversation is filed against a member record, not just a phone.*
0/3,102 stamped today. **THE TRAP: the FK expects `members.airtable_id`, NOT `at_member_id`
(0 of 646 are equal).** Fix = n8n (staging→promote): `Find Member` select += `airtable_id` →
carry through `Resolve Member` → `Save Conversation` stamps `member`. Backfill by phone join —
3,102/3,102 resolvable TODAY, decays as numbers change, so do it with the node change. Then
re-verify the phone-joining readers (`persona_signals`, `persona_signal_fingerprints`,
`olivia_health_check`). Related, separate: 61/646 members lack `at_member_id`;
`event_registrations` 62% keyed. **Expect:** portal/persona/dossier joins become key-based and
survive phone changes. **Accept when:** all rows stamped · new rows arrive stamped · readers verified.

### 45. 🟡 Identity resolution — the rest of the dimension · effort M · → RELEASE 3 (audit §2+§5; #43 needs it to score identity ≥8)
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

### 39. 🔴 Attribution: never put words in a member's mouth · effort M · → RELEASE 3 (from the PROD Big Smoke 2026-08-03)
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

### 46. 🔴 member_events — start writing from surfaces we control · effort S · → RELEASE 3 (audit P2; stops part of the irreversible loss NOW)
*As the team, member behaviour starts accumulating today — not after the app integration lands.*
`member_events` = 0 rows since created. The APP feed (video views, app searches) is Andy's
GROUPOS_PAT + app-logging ask — but the PORTAL (digest.mds.co) and Olivia are OURS: portal
logins/page views, Olivia turns (route/lane/sources_used), report filings, nudges can emit
events immediately. Audit's design rule: **log CHANGES/actions, not states**; one row per event,
keyed `at_member_id` (fall back `airtable_id` — see #41/#45), typed + timestamped + source.
**Accept when:** portal + Olivia surfaces emit real events (A1 shows rows growing daily) ·
schema documented (event_type vocabulary) · nightly heartbeat covers the writer · the app feed
slot is specified in writing so GroupOS events drop in without rework · gate GREEN.

### 42. 🟡 place_city: aliases to a TABLE + normalize on write · effort S · → RELEASE 3 (audit P5)
*As a member, "who's in Miami" finds Miami however it was spelled.*
908 distinct city spellings / 1,718 rows; alias layer is a hardcoded ~11-entry CASE — plain
lowercase "new york" isn't even folded, and "City, ST" suffixes aren't handled. Move aliases to
a table (data, not DDL), strip state suffixes, normalize on ingest. **Expect:** city-scoped
people search stops leaking members; adding a city becomes an INSERT. **Accept when:** the four
audit examples resolve to one canonical each; member_match city counts match hand counts.

**Also NOW, Andy's side:** the APP half of the `member_events` feed (GROUPOS_PAT + app event logging, under #29) — #46 starts our half immediately. Graph layer = **#44**, deliberately LAST — waits for the #29 memo.

---

---

# 🔵 NEXT — Release 3 features

### 38. 🔵 Interactive buttons (CTAs) for offers + links · effort M · → RELEASE 3 (from Andy's WABA question 2026-08-01)
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

### 29. 🔵 Matchmaking & recommendations, built like the platforms build them · S3 · effort L · **→ RELEASE 3 (Andy 2026-08-01: "this is a huge one" — not part of this push; the research memo opens Release 3. His signal asks — app event logging + GROUPOS_PAT — still run THIS week so history accumulates)**
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

### 44. 🔵 Knowledge graph — weighted member↔entity edges · effort M-L · → RELEASE 3, LAST (audit P6; opens AFTER #29's research memo)
*As a member, MDS knows who knows who — intros, "people like Mo", and "who was in the room"
come from real connections, not just profile fields.*
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

### 17. ⚪ Auto-refresh videos and partners · S4 · effort M · **→ RELEASE 3 (Andy 2026-08-01; still blocked on GROUPOS_PAT). TEMP SOLUTION NOW: WEEKLY refresh via the GroupOS connection in-session (videos + partners diff-upsert), heartbeat-backed so the staleness alarm pages if a week is missed; first refresh run 2026-08-01**
*As a member, new recordings and deals show up without anyone importing them.*

**Accept when**
- **Blocked until the GroupOS key exists.**
- **New videos and deals appear without an import**, and data older than a day alerts.
- **The requirements are handed over, the security exposure included**, and it is fixed or owned in writing.

13 videos landed in a week and none surfaced in any catch-up; partner data sits on a frozen snapshot.
Needs the GroupOS key. Includes sending GroupOS the 13-item requirements doc — one of which is a live
security exposure: restricted decks are publicly downloadable.

**Effort M** — blocked on a key we don't have. **Impact:** everyone asking what's new; the security item is urgent on its own terms.

### 18. ⚪ How-MDS-works answers · S4 · effort M · **→ RELEASE 3 (Andy 2026-08-01)**
*As a member, I get the real answer about Squads, programs and joining a chat.*

**Accept when**
- **Every recurring how-MDS-works question has a written answer from the team.**
- **Each answers consistently across phrasings and cites that source.**
- **They stop arriving as support requests.**

From the team's own documents rather than inferred from chat chatter. Also unblocks the chapter policy
questions in #9.

**Effort M** — the work is someone writing the answers; loading them is straightforward. **Impact:** all 722; every one of these currently becomes a support request.

### 19. ⚪ Privacy: share, keep, delete · S4 · effort M · **→ RELEASE 3 (Andy 2026-08-01)**
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

### 20. ⚪ Census into the warehouse · S4 · effort L · **→ RELEASE 3 (Andy 2026-08-01)**
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

### 35. 🚀 Connect new data source — DOCUMENTS (GroupOS) · S3 · Release 3
*As a member, MDS documents are searchable like everything else.*
Extract via the GroupOS MCP document endpoints (documents_list/get, collections, categories —
already exposed on the connection). Same pattern as videos/partners: catalog + gated retrieval +
restriction handling + embeddings + gate checks. Filed by Andy 2026-08-01.

### 36. 🚀 Connect new data source — CIRCLEBACK · S3 · effort L · Release 3
*As a member, what was said in recorded meetings becomes part of what Olivia knows.*
Circleback (meeting notes/transcripts). **BLOCKED: needs details from Andy** — which workspace,
what API/export access, which meetings are in scope, and the sensitivity rules (who may see
what). Filed by Andy 2026-08-01.

---

---

# 🏁 CLOSE-OUT — standing tickets that end the release cycle

### 32. 🔥 What Olivia costs — measured AT the smoke, INCLUDING a Kimi cost comparison
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

### 14. 🔥 Conversational, not robotic — its ACs are the smoke's acceptance criteria
**ANDY'S DECISION (2026-08-01): "#14 sounds like AC for the smoke test" — not a build ticket.**
Written 2026-07-28 about the pre-loop system; the loop + #2/#5/#6/#7/#8 absorbed the concrete
bullets. At the Big Smoke it is checked as: follow-up class rate on the FULL run ·
capped-answer-continues probes · uses-what-she-knows probes · **Andy's own feel verdict**
("it feels like a bot" was his original complaint — he judges whether that's gone). Anything
still robotic becomes a NAMED FIX before the promote.

---

### 43. 🏁 RE-AUDIT after Release 3 — prove the architecture moved · effort S · runs WITH #34 at the release close
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

---

