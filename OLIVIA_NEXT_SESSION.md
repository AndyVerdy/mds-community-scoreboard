> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.

# Olivia — next session

> ⛔ **THIS DOC IS THE STANDING ROUTINE, NOT THIS SESSION'S GO** (Andy 2026-07-29, tiers clarified
> by him 2026-07-31). Read it, verify against live, then work within these tiers:
> - **Fine without asking:** read-only diagnosis (execs / SQL / graphs) · the LEAK GATE
>   (`olivia_leak_gate.py` — free SQL safety checks, zero questions, zero model calls) · staging
>   edits under the `olivia_wf.py` lock protocol · single-question STAGING PROBES (selftest,
>   ~a cent each, a handful per session).
> - **Propose to Andy and WAIT:** any eval RUN — TEST (≤50 Qs) or FULL (100 Qs) — or anything
>   else paid at scale.
> - **Andy runs it himself:** `promote` · prod edits (emergency rollback protocol excepted).
>
> **Vocabulary — status lines must never blur these: "gate 167" = 167 safety CHECKS (free), never
> 167 questions · a "RUN" = firing the eval bank · a "PROBE" = one question at staging.**

**Read `OLIVIA_BACKLOG.md` first** — every item carries **Accept when** criteria under one global
DoD; the judge files failures into 8 classes mapped to tickets.

**Session open (Andy 2026-07-31): after reading the docs + verifying live, SUGGEST which
ticket(s) this session should take — ticket NUMBER + STORY — and let Andy pick before diving in.**

## NEXT SESSION — THE RELEASE RUN (Andy's orders, 2026-08-01 close)

> ⛔ **SESSION-OPEN OVERRIDE (Andy, said after 3 sessions in a row got this wrong): do NOT
> launch the daily routine at session start.** No eval runs, no daily-review kicks, no
> routine probes "to verify the morning". A major release is in flight — the ONLY ticket is
> #34, so skip the suggest-tickets step too. Open the docs, verify live is quiet, and go
> straight to Big Smoke prep.

**The backlog is CLOSED (pre-smoke). This session = #34: finalize the QA docs, then run THE BIG
SMOKE — ON STAGE FIRST (Andy confirmed 2026-08-01)** — prod still runs the old build, so stage
is where discovery happens; prod only confirms.

**Benchmark (Andy 2026-08-01): failure rate < 5% on the complete smoke.** That is the release
gate. (The <1% inaccuracy bar stays the long-term program goal measured by the nightly eval.)

**State of mind: WHEN something fails, not IF.** Failures are the expected output of the smoke;
the plan below is a loop, and we go around it as many times as it takes — back to stage, fix,
re-release, whatever it costs — until the benchmark holds.

1. **Prep (free):** reconcile the 3 QA docs (`OLIVIA_QA_CHECKLIST` = method ·
   `OLIVIA_BIG_SMOKE_MATRIX` = questions, ≥5 per update point, fill expected values ·
   `OLIVIA_SMOKE_CHECKLIST` = phases/gate) · fresh FB comments capture (Phase 0 — needs Andy's
   manual scroll) · gate 187 GREEN.
2. **SMOKE ON STAGE (paid — propose scope + cost, WAIT for Andy's GO):** full matrix + FULL
   bank + #14 feel ACs, with #32 spend metering + the fair Kimi comparison alongside.
3. **Triage:** every failure filed into the 8 judge classes; count the failure rate.
4. **FIX LOOP (stage, under the `olivia_wf.py` lock):** fix → gate → re-run the FAILED slice →
   when all slices pass, ONE full clean re-run must show **<5%**. Loop until it does.
5. **Andy promotes** (his terminal, never mine).
6. **PROD re-verification:** condensed smoke on prod (the 5-check list + a sample of matrix
   questions per source family) — must hold <5% too. A prod-only failure = emergency rollback
   protocol, fix on stage, next promote.
7. **POST-RELEASE (only after 6 is green) — two deliverables, in order:**
   a. **Release notes for PRODUCTION RELEASES 1 + 2** (R1 was never announced). Written for
      humans; audience = the team + beta testers (more candor than end-users get). Format:
      list ALL updates, grouped; **draft → Andy validates → Andy posts** (never post it myself).
   b. **Backlog archive:** released items move to an archive section/file; `OLIVIA_BACKLOG.md`
      keeps ONLY open items (Release 3 queue + standing rulings).

Standing (unchanged, none block the smoke): MDS-Life ruling (Q3088) · whale ruling (chapter TTM
sums) · #18 needs the team's written policy source · #29 rows 1-2 = Andy's action-this-week
(app event logging + GROUPOS_PAT) · weekly GroupOS refresh SOP (heartbeat-paged).

## State (2026-08-01 early close)
- **CATALOG REFRESH RUN + WEEKLY TEMP SOP (Andy).** Via the GroupOS connection in-session:
  **+13 videos** (1,009→1,022, all embedded — incl. the restricted Prue TikTok video, findable
  with restriction enforced) · **partners FULLY parity-checked 08-01**: full 494-sweep-diff = 0
  deletions / 0 missed / 0 review drift; 6 new partners' categories filled the AUTHORITATIVE way
  (`ingest_partners.py --map-categories` — AT join first, co-occurrence only as fallback; it
  corrected 5 of 6 SQL guesses); 492/492 embedded. Heartbeats `videos_refresh`/`partners_refresh`
  (max_age 8 days) → the staleness alarm PAGES if a week is missed. **WEEKLY SOP: run the refresh
  in-session each week** (list since last sync → upsert → `--map-categories` → embed scripts →
  heartbeats; every ~month do the FULL sweep-diff for deletions). Known gaps: reviews TEXTS not
  re-pulled (counts verified 0-drift) · **2 API-unfetchable "poison" partners** (created-at windows
  2023-10-04T10:23:29–38Z, 2024-08-13T08:18:01–08:21:46Z — published in the app, invisible to the
  API, Olivia can't know them; recheck weekly). #17 proper → Release 3 (needs GROUPOS_PAT).
- **RELEASE 3 QUEUE FILED:** #29 (the big one) · #17 · #18 · #19 · #20 · **#35 documents source
  (GroupOS MCP endpoints)** · **#36 Circleback source (BLOCKED: details from Andy)**.
- **REMAINING FOR THIS RELEASE: #34 + THE BIG SMOKE. That's it.**
- **#16 HEALTH AUDIT CLOSED — LIVE.** The lying olivia-agent tile now reads member-visible truth
  (failure texts + alarm state; run status lies via continueOnError) — FORCED-proven on the live
  report (canary → 🟡 flagged → clean). +2 tiles: watchman (pg_cron tick) + derivations
  (heartbeats), 35→37. The latched 30-min monitor UNLATCHED in place (30-min repeats + recovery;
  the latch that buried 07-26). Supabase blind spot → Mac watchdog every 15 min
  (`alarm_watchdog.py`, forced-test proven). digest-web `b1b1a9f`. Gate 187. Scope note: full
  37-tool audit = the Tools-health PROJECT; this fixed the Olivia domain + shared alert chain.
- **#12 PUBLIC REVENUE CLOSED (Andy's ruling in session).** Official data = bands only, always.
  A figure the member/page POSTED = quotable WITH attribution + link, paired with our band; FB
  fully open; chat figures visibility-scoped structurally (retrieval can't return non-member
  chats — gate canaries prove it). The review-flagged "$14-15M" case traced to MDS's OWN public
  FB welcome post (the ALLOWED class). REVENUE FIGURES rule in the loop + rulebook nuance +
  review-bot rubric updated LIVE (wf xkX7wnIwxJLU7YgY). Probes: Aaron = band + attributed $140M
  quote + link; Prudence exact still hard-refused. Matrix +5 (BS105-109).
- **#15 HANDS-OFF PIPELINE CLOSED — LIVE (not promote-gated).** `nightly_derivations.py` runs the
  four jobs (niches · labels · chapter-pages · member-embeddings) via launchd
  `com.mds.olivia.derivations` 04:30, heartbeats to `olivia_job_heartbeats`; the #13 alarm gained
  a 4th signal — any job stale >26h (or never-run) → Slack, off-platform, unlatchable. Forced-skip
  proven (backdated label_questions 30h → 🚨 → restore → ✅). Kills the "scheduled not remembered"
  decay across #6/#7/#25. Gate 187. Named exception: FB scroll stays MANUAL (platform removed
  anchors); downstream is what's automated.
- **QA STRUCTURE BUILT (Andy: "check everything, research how"):** `OLIVIA_QA_CHECKLIST.md`
  (A–I, grounded in OWASP LLM-Top-10 2025 + 2026 eval practice; per-category example→expected
  answer table) + **`OLIVIA_BIG_SMOKE_MATRIX.md` (~85 questions, every backlog update point ≥5,
  expected + proving SQL, anchor facts verified live).** The Big Smoke = one full pass. **#34 FILED = the LAST ticket:
  finalize/reconcile the three docs + grow the matrix ≥5 rows per ticket closed after 08-01 +
  run the Big Smoke — the gate between 'backlog closed' and 'one big release'.**
- **#13 OUTAGE ALARM CLOSED — LIVE NOW (not promote-gated).** Supabase pg_cron every 5 min (off
  n8n), Slack #automation-tests (C0AQ8USNQK0, one config row to change). 3 signals:
  failure-text-to-members (eval noise excluded) · relay maintenance markers (n8n dead) · active
  webhook ping (HEALTHPING heartbeat row). NO LATCH: re-alerts every 30 min while down, ✅
  recovery on clear; never-raise + self-heartbeat `last_tick_at`. Forced-failure proof ALL
  visible in Slack (~20:34 CDT): alert → paced → backdated re-alert → recovery; ping 200;
  autonomous tick on the :35:00 boundary. Gate 186. ⚠️ pg_net lives in schema `net` (not
  extensions) — silent-no-op trap caught. Residuals: balance PRE-warning + cap → #32; Supabase
  blind spot + old latched monitor → #16.
- **#11 PAYMENT WORDING CLOSED (staging, Release 2).** Wording map INSIDE member_billing (raw
  words structurally unemittable; unknown states → generic plain sentence). Drafts posted to
  Andy. Population: past_due 3 / unpaid 1 / canceled 2 — ALL phone-less today (wording waits for
  them). Gate 184 GREEN. Probe: Andy's billing plain, `Staff` → "MDS team". **Round 2: ride-along
  payment reminder (any route, once per 24h — billing_nudge RPC + stamp table, E2E-proven with
  a canary past-due member, execs 58031/58032) + the Stripe portal link in wordings and as
  `billing_portal`.**
- **#10 SHAREABLE FACTS CLOSED (staging, Release 2).** `OLIVIA_SHAREABLE_FIELDS.md` = THE
  rulebook (SHARE / GROUP-ONLY / NEVER + default-deny for the ~1,700 unlisted fields).
  member_card extended with channels/business_model/categories/country (the one inconsistency);
  gate pins CARD_KEYS to the page + column-name canary — **180/180 GREEN**. Probes: TikTok
  channels precise · same shape across members · address refused.
- **#9 REVENUE CLOSED (staging, Release 2).** The working session dissolved — Andy pointed at CU
  page `2531q-67177`: **authoritative = `Most Recent Revenue`** (verified-else-reported), and
  `derive_member_attributes()` ALREADY derives rev_band from it by one threshold rule (provenance
  stamped) — single rule everywhere by construction. Shipped the enforcement: **gate +3 (178
  GREEN)** — card revenue_tier band-only · no raw-revenue field in card blob · count band keys ⊆
  vocabulary. Probes: tier answered (*20M+*), exact refused with the rule. Residuals: exact
  channel-% upgrade (Forms raw fields) · #12 ranking ruling · whale ruling.
- **#8 EVERY SOURCE CLOSED (staging, Release 2).** Three behaviors per Andy's scope: cross-source
  floor before any "can't find" · merge multi-home answers (WA+FB attributed) · wide solve
  fan-out. AC reframe (his call): process floor absolute, outcome = the exists-but-missed class
  on the ladder, never literal 0. Shipped: 3 loop rules · `multi_source` + FB + VIDEOS (all six
  families, one call) · **per-turn `plan.sources_used` telemetry** (loop → Format Reply → Save
  Conversation, `apply_8_sources_telemetry.py`). Baseline: 220 llm answers/14d, 24 (11%)
  can't-find-shaped. Probes telemetry-verified: solve = [content, partner, video] w/ Sasson +
  Kenyield deals + Omer Sasson's Expert Call all linked · merge = FB + chats sections · absence
  = honest qualified miss (2× same-family — floor nuance for the eval). Gate 175/175.
- **#7 PEOPLE SEARCH CLOSED (staging, Release 2).** Fuzzy names via pg_trgm on `member_card`
  (word_similarity > 0.62 fallback — thresholds MEASURED: typos 0.75-0.80 pass, "Jon Snow"
  0.556 + junk 0.26-0.32 miss; the gate caught my first 0.25 version surfacing wrong people —
  fixed, full matrix green). Meaning via `member_profile_embeddings` (DEDICATED table, 722/722
  embedded by `scripts/embed_member_profiles.py`, idempotent) + `expertise_search` p_embedding
  RRF (with/without diff proven). Place aliases via `digest.place_city` in member_match +
  member_count (NYC = New York = 19). **🚨 Pre-existing member_match defect found + fixed:
  city/state-targeted searches were ANDing the asker's own category/band as filters — "members
  in NYC" = 0 for Andy while 19 were there; likeness is now a ranking boost in target mode.**
  E2E probes: misspelled Prudence resolves w/ card · "paid ads" → the PPC bench · NYC → the
  New York members. Gate GREEN (result in the session log).
- **#6 CHAPTERS CLOSED (staging, Release 2).** Andy's rulings in session: counts = RAW DATA (live
  member records; the public mds.co chapter pages are the disclosure precedent, may lag) · leads
  PUBLIC (names/roles/photos are on the pages; emails never — not stored). Shipped:
  `digest.chapters_catalog` (20/20 pages scraped + hard-verified by `scripts/sync_chapter_pages.py`;
  the catalog IS the whitelist) + `digest.chapter_info` (live counts by the SAME CTEs as
  member_count — one number everywhere by construction — + leads + site_stats + `live_stats`:
  top_niches, band_mix, TTM sum/avg from `Most Recent Revenue`, employees, tenure + asker_city so
  closest-to-me never asks when the city is on file) + loop tool + CHAPTERS rule. **Gate 175/175
  GREEN.** Proof = Andy's exact chain, zero re-asks (chapters 20 → closest = NY from Jersey City →
  97 live → leads Morris/Brandon/Mari → Europe deep-dive w/ live aggregates). Field traps
  documented: `Most Recent Revenue Source` = record URL (not channel) · `Actual Birthday v2` =
  NEXT birthday. Open: whale ruling · policy source (#18) · scrape not scheduled.
- **#33 CLOSED (staging, Release 2).** The 2:40PM stall root-caused: n8n v1 ran the
  Mark Read + Typing → ladder branch AFTER the whole answer (exec 57816, 70.5s, ladder exec
  started as the main exec stopped) — read tick/typing/ladder were structurally dead on every
  prod turn. Fixed by branch order (`apply_33_early_feedback.py`), proven exec 57926 (MRT +3.68s,
  before Route Request). The 9:54/9:55PM duplicate = ghost rung-2s from the KNOWN fail-open
  window (14 sends in 3.5min, exec 56699), fixed that same night — rung copies were always
  distinct. `LINKS WHEN YOU SOLVE` rule shipped in the loop contract, proven exec 57926 (FB
  thread URLs attached) with clean counting control (57927). `OLIVIA_SMOKE_CHECKLIST.md` written,
  first run PASSED, gate **167/167 GREEN**.
- **⚠️ DRIFT CORRECTED: the holding-trigger fix (arrival = message timestamp) is LIVE ON PROD** —
  it rode the SECOND promote that night (03:24Z; prod `updatedAt` 03:24:30, untouched since;
  verified in the prod node + today's ladder execs all silent no-ops). Prod version = the 03:24Z
  promote, NOT `ee3e3cf6` (that was the 01:54Z first promote; same 4.0% bank state).
- **STAGING carries Release 2, all proven:** eval fix batch (fact-gate clamp+RULE TWO ·
  content_search post_author · dossier persona) · #23 cuts (router caching = cost not speed ·
  claim-free gate skip) · #5 counting (`member_niches` 14-canon multi-valued, stated niches
  EQUAL · `member_count` RPC w/ breakdown_sum — sums READ, never computed) · #33 (feedback-first
  branch order + links rule). **Gate 167 GREEN.**
- **Earlier same day: #23 + #25 + #5 closed; #25 LIVE ON PROD** (mds-digest-web `294b094`) ·
  #32 cost-control filed · bank swapped (3101-3112 in, backup `.bak-preswap-0731`), NO run fired.
- **Warehouse adds (shared DB, additive):** `member_niches` · `olivia_question_labels` ·
  `member_count` · portal fixes live on prod (eval-traffic exclusion, pagination — PostgREST caps
  at 1000 rows ALWAYS, page everything — topics per-question labels, Exclude-staff toggle; staff =
  `member_attributes` AT mirror 29, NEVER `digest.members`; blank status ≠ member).
- **Neither derivation job is scheduled yet** (niches + question labels) — decay risk, in #33/#5
  residuals.
- **Watch:** promote is Andy-run · MDS-Life ruling open · "Oliva" display name · ClickUp doc stale.

## The daily routine
- **Run tiers (Andy 2026-07-30): FULL vs TEST.** A FULL run (all 100) produces the standing number —
  rare, never for fix confirmation. A TEST run confirms a change: **50 max, ideally ~25-35** — the
  fails/partials the fix targets + their thread predecessors + a pass spread across sources (the
  over-refusal check). `olivia_eval.py --fire --score --staging --ids <list>` **with
  `OLIVIA_EVAL_BANK=eval_bank_organic.json` or it silently fires 0**. Never 10×100Q days.
- ONE paid organic run per session, AFTER free diagnosis + fix batch + free probes. Expectations
  name the SQL that proves them. Retirement: 3 consecutive passes + class still covered → replace
  same day, bank stays 100.
- Runs wait per-reply (~50 min full bank) — never fixed sleeps. The eval progress output can look
  like a stalled prompt to task monitors — it is per-reply pacing, don't kill it.
- Reset between probes; `--cleanup` deletes nothing; leak gate GREEN (161) before anything ships.
- Andy's number excluded from reporting; probes reset his thread — warn him first. Before firing a
  backdated-arrival ladder test, check the latest olivia-row time (my bad assumption cost 3 stray
  texts to Andy).

## Open with Andy
- **MDS Life** (now also eval-fail Q3088): data gap vs wrong name — his call on the canned truth.
- **👎 alerts**: reactions land in `olivia_feedback` and nobody is told. Wire to Slack?
- `member_match` category values: 'Apparel' filter misses the real 'Clothing & Accessories' (#7/#10).
- Adam's Hector answers near-contradicted ("MDS special pricing, 137 claimed" vs "no discount code
  listed") — partner-card discount semantics worth a ruling.
- Constantine got one "Sorry — I could not generate an answer" (07-29 20:35) — infra turn, exec
  worth a look.
- Still owed: revenue ranking · ex-member departure dates · canonical chapter count · chapter
  leads · Intercom ticket #215475264324071 · "Oliva" display name · health alerting latched.
