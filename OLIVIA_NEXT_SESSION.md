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

## NEXT SESSION — orders (2026-08-01 early close)

1. **Andy's plan: complete several more tickets, then ONE BIG PUSH + BIG SMOKE TEST** — no
   promote until he says "we are done". Release 2 so far: eval fix batch · #23 cuts · #5
   counting · #33 early-feedback + links · #6 chapters · #7 people search. **At the push: run THE BIG SMOKE
   (`OLIVIA_SMOKE_CHECKLIST.md` top section — fresh comments capture · coverage matrix ≥5 Qs per
   update point (`OLIVIA_BIG_SMOKE_MATRIX.md`, build first) · FULL bank + smoke suite · #14 feel
   ACs · #32 spend + fair Kimi retest · the 5-check list) and paste results into the session log.**
2. **ANDY'S GOAL: close the WHOLE backlog, one big release, one huge smoke test.** S2 is now
   EMPTY. Open: S3 #10 shareable facts (S) · #11 payment wording (S) · #12 public revenue
   (needs his ranking ruling) · #13 outage alarm (M) · #14 conversational (L) · #15 pipeline
   (L) · #29 dossier research (L) · #32 cost (M) · S4 #16-#20. #10 + #11 + #13 CLOSED — suggest #32 cost (Kimi retest + report to Pavel) → #12 (needs your ranking ruling) → #14.
3. Standing: MDS-Life ruling (Q3088 expect) · **whale ruling** (live chapter TTM sums can out one
   member's scale — NorthTex $930M sum / $806M one member; ON today per site precedent) ·
   **schedule the FOUR derivation jobs nightly** (`olivia_derive_niches.py` ·
   `olivia_label_questions.py` · `sync_chapter_pages.py` · `embed_member_profiles.py`) ·
   chapter POLICY answers need the team's written source (#18) · extend content_stats
   (distinct-authors-by-source) · FULL run on the new bank (3101-3112) when Andy calls runs
   back on · #29 signal inventory rows 1-2 (app event logging + GROUPOS_PAT) = Andy's
   action-this-week list.

## State (2026-08-01 early close)
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
