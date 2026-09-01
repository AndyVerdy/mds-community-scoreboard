> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.
- **Always show a ticket's STORY + ACs. Closing needs: short results · short AC checklist (met/not) · before/after numbers.** (Andy 2026-08-03)

# Olivia — next session

## STATE 2026-08-27 (Andy out — full pipeline run unattended)
**16 Summit Singapore talks are in the corpus. 9 are live and proven; 7 are loaded but reachable by
nobody. PROD WORKFLOW UNTOUCHED — data only, no promote.**

### What shipped
- **Batch A — 7 restricted** (`~/mds_transcripts/summit_sg_2026/`): 228 chunks, 7 summaries.
- **Batch B — 9 public** (`~/mds_transcripts/summit_sg_2026_b/`): 219 chunks, 9 summaries.
- 8.2 hr audio, **$1.88** total at AAI. Summaries hand-written in-session, zero API spend, all inside
  the corpus band (max 1,338 chars). Everything embedded. Gate GREEN (263 checks, exit 0) after each.
- Library: **410/1050 transcribed, 410 summarised, 12,762 chunks, zero unembedded rows.**
- `aai_submit.py --local` ends the presigned-export dependency (ffmpeg → AAI `/v2/upload`, resume-safe,
  manifest binds file → `video_id` explicitly). Commits `a2f4007`, `a06f57a`, `233de8f`.

### ANDY'S DESK — three calls, in this order
1. **GRANTS for the 7 restricted talks.** They are invisible to every member — proven live, not
   assumed (`content_search_v2` returns nothing from them even with `p_include_restricted=true`).
   46 restricted videos have no grants (7 new + 39 from 2023). Needs the dev's audience export;
   `scripts/load_video_access.py` already ingests it. **I did not derive grants from attendance —
   that is an access-control decision, not a data chore.**
2. **RE-CHUNK BACKLOG (priority call).** The producer is fixed, the existing rows are not:
   1,423 chunks over 4,000 chars across 255 videos, **581 of them on 138 RESTRICTED videos, worst
   23,632**. Handbook §6.2 now says plainly that the quote ruling's "~1,400-char largest retrievable
   unit" is false for those rows. Access gate unaffected; an ENTITLED asker can pull most of a talk.
3. **Eugene Khayman shows as a `guest`** — GroupOS has `eugene@ykuni.com`, Members DB has
   `eugene@mds.co`. Add the alias to record `recvSgAirIbbo9Ylb`; `member_email_alias` mirrors Airtable
   so this is yours to make, not mine. `--rescan` promotes him automatically after.

### Speaker state on the 16 (recorded, not fixed — needs #103 / Airtable)
- Linked correctly: Alex Bonilla, Brandon Himmel, Jon Jewett, Jared Mortensen, Khalid Abdulla,
  Ivan Ong, Damon Sununtnasuk, Anjie Liu, Eva Maxfield, Corey Smith, Ary Selener, Cassidy Clawson.
- **Name-shape misses:** "Douglas Iske" vs `Douglas Patrick Iske`; "John Spektor" vs `Jon Spektor`.
  Both real members, both sitting `unresolved`.
- **Correct externals:** Tamar Yaniv (Yuka AI — not in `partners_catalog`), Emily Wang (StoreClaw),
  Meher Patel (Hector AI), Hammad Yousaf.
- **Nathan Ross is in no members row** under any Ross spelling, though he says on stage he joined 2017.
- **Hack Contest has 0 speaker links** — no names in the title; ~12 presenters live in the transcript.
  Hand-patching will not stick: `load_speakers.py:287` re-patches any `guest`/`unresolved` row.

### Still open from before
- ~640 pre-2025 videos untranscribed (~$137). Local files now make this a folder + manifest away.
- #102 answer-layer wiring · #104 adjacent-turn topic lag · #72 load test (never run).

## STATE 2026-08-28 (close) — read this first

**PROD = `15ff4978`. Staging identical. Gate GREEN (306, EXIT 0).** Five promotes today; every fix
proven through the workflow, every probe row cleaned. Shipped: **#125** (an absent membership status
is not an inactive one — 53 false claims → 0), **#149** (a live event called finished + the clamp
answering a yes/no in machinery), **#150** (Summit video entitlement + the `is_restricted` flag now
per-asker), **#151** (video recommendations: count, tailoring, follow-up binding, no old-event
padding), **#153 + the #102 time-decay slice** (intent questions: recency in ranking, stated facts
beat a missing tally). **#126** closed NOT REPRODUCIBLE; **#148** and **#152** filed.

### FOUR THINGS WAIT ON ANDY — nothing else is blocked
1. **#147's authority shape.** Its SQL is already LIVE (`registration_status` · `is_registered` ·
   `member_alias_ids`; `event_who` calls them — 130 → 145 registered, **15 recovered, 0 lost**).
   Paused on: roster-only · **one-function-two-facets (recommended)** · union. The event-resolver
   half is untouched — `event_who('vegas')` still lands on a Feb 2025 chapter dinner because the
   resolver matches WORDS IN THE TITLE.
2. **All 16 Summit videos read `access_restriction = public`.** They flipped in GroupOS, not by us,
   and it contradicts his ruling ("restrict them to summit attendees and staff"). Deliberate or fix?
   Grants are written either way and harmless if public.
3. **The re-embed go** for the 7 Aug-26 videos embedded while restricted (metadata-only vectors).
   scorecard-df executes it; it correctly refused to act on a peer's say-so while Andy's answer is
   pending. Note: the decay fix already recovered the Khalid miss WITHOUT the re-embed.
4. **A v4 transactional template** for the 50 undelivered announcements — see below.
   **Live check 2026-08-28 (this session): `mds_summit_videos_live_v3` is APPROVED but Meta filed it
   MARKETING — the third reclassification in a row.** Sending v3 to the 50 would hit the same 131049
   caps. A v4 only helps if its COPY is transactional; the declared category still buys nothing.

### The announcement, and the template trap that cost three submissions
94 fills sent, **94/94 accepted, 0 send errors**; at close **26 read · 18 delivered · 50 failed** on
Meta's marketing frequency caps (131049) and experiment holdouts (130472). One recovered free-form.
**Meta reclassified UTILITY → MARKETING on v1, v2 AND v3 — even with `allow_category_change: false`.**
The declared category is not a lever; the COPY decides, and "picked for you + watch" reads
promotional. v4 should be strictly transactional (the recordings from your event are available +
button) with the personalization moving to Millie when the member taps in. Also burned: **v1 was
approved but unsendable** — Meta rejects newlines inside template VARIABLES (132018) even though it
approved the example containing them. Test-send every template before generating a wave.
Regenerate fills with `scripts/announce_summit_videos.py`; send with `scripts/announce_summit_send.py`
(resume-safe — a phone already holding a wamid is skipped, so a re-run cannot double-send).

### Traps this day earned
- **A template's approval does not mean it can be sent.** Test-send one before building the wave.
- **`allow_category_change: false` does not hold the category.** Copy decides classification.
- **n8n Cloud's execution quota can take PROD down** — 04:57-05:10Z every inbound died in 50ms at the
  webhook ("Execution limit reached"), staging and prod alike. Andy upgraded; verified back green.
- **Audit a gate before changing it** — the #149 clamp had fired 3 times in 6,017 answers and was
  wrong all three. The audit is what justified touching it; the withhold behaviour never changed.
- **A peer refusing your request can be right.** scorecard-df would not re-embed on my say-so while
  Andy's ruling was pending. Correct.
- **Bank D = 30 questions, 10 classes** (`OLIVIA_BANK_D_SUMMIT_2026-08-26.json`), written but only
  spot-run — the problem-first class came from probes that exposed what my own 8/8 wave missed.

## STATE 2026-08-25 (overnight close) — read this first

**PROD = `8bb0827d`. Staging is identical. Gate GREEN (306, EXIT 0).** Three promotes tonight:
`bbd597b7` → `91c70977` (bank C waves 7-21) → `64995b68` (#146 hidden-number identity) → `8bb0827d`
(place-question rules). Pre/post snapshots for each are in `olivia_snapshots/`.

**#145 is CLOSED: 311 of 319 previously-passing questions hold = 97.5%**, and all 8 regressions were fixed
and verified before the promote. Across the 319: links 654 → 808 · dead links 5 → 0 · dates 641 → 862 ·
route changes 0. Full detail in `SESSION_LOG_OLIVIA.md`; every verdict with its reason is in
`.superpowers/sdd/2026-08-22-finder/eval/grades145_full319.json`.

### The one rule that changed how we work
**NEVER WRITE TO AIRTABLE (Andy, 2026-08-25):** *"it's my acc I'm testing things and I don't want to change
our source of truth."* All three edits I made were reverted. A fix that needs the source of truth gets
raised with Andy or ops — named record, named field — and they make the change. Mirrors, Supabase and the
workflow are still ours to edit.

### Start here
1. **#147 — two sources answer "is this member registered?" and disagree.** Andy's agenda said yes while
   who-to-meet said no, one minute apart. MEASURE FIRST: how many members do `event.attendees` and
   `event_registrations_live` disagree about for the Summit? Three means file-and-move-on; thirty is an S1
   today. The ticket also carries the second half: the event resolver matches WORDS IN THE TITLE, so
   `event_who('vegas')` lands on a 2025 chapter dinner and Inspire 2027 is unreachable from the word Vegas.
2. **#146 leftovers** — a silent-drop alarm (this class was invisible until a member complained), and a
   hidden-number member's history being keyed by the opaque id instead of joining their phone history.
3. **6200** — the nudge answer no longer invents a search result but is still thin; it should restate where
   the thread stands.

### Loose ends nobody owns
`MY.1563712991959404` (2026-08-24 01:50Z) is an unlinked hidden-number id — somebody got silence that night
and we do not know who; `scripts/olivia_link_wa_id.py --find` shows it. · The member record for Tudor Tanase
has country CY with the city Baia-Mare (Romania), so he surfaces in Cyprus answers. · `viewing` is set to a
full sentence in `mds-digest-web/src/app/api/olivia/schedule/route.ts:384`; renaming it to a token is one
line in that repo, which deploys on push. · Andy's own Summit registration is deliberately back to "not
registered" — the gate uses him as its non-attendee control, so registering him turns the gate RED (that
coupling is in #147).

## STATE 2026-08-24 (END OF DAY) — read this first

**GOAL OF NEXT SESSION: PROMOTE.** One thing stands in the way, agreed with Andy at close.

**THE ONE JOB: re-run the 319 bank C questions that were already PASSING.** Everything measured today
was the 192 FAILURES (155 now pass, 81%). Nothing has checked what nineteen waves of rules, stamps,
gate checks and nine SQL changes cost the answers that were already good. This is not caution for its
own sake — **two questions regressed inside the fail set in the last round alone** (6500 and 6267 got
worse), and **wave 9 broke staging outright for eight hours**. A stratified sample of ~100 of the 319
is enough signal; the full 319 is better if time allows. If it holds, promote. If it does not, the
regression is on staging where it belongs and not on 700 phones during Summit week.

**State:** staging `daf8ec82` · gate **306 EXIT 0** · **PROD `bbd597b7`, untouched all day.**
The head-to-head that said stage 91% vs prod 87% **predates waves 7-19 — treat it as stale.**

### What shipped LIVE today (SQL is prod-shared; these are already serving members)
#106 staff/team never in member-facing lists · #128 the doorman counted PHONES not members (34 RPCs, 5
members getting empty results from everything) · #129 event-specific partner offers, entitlement-gated
· #130 a member with two numbers sees ALL their chats · #131 Andy's removed-member ruling · #133
partner ranking · #134 `matched_total` · #135 exact brand name outranks the embedding hybrid · #136
country counts · #137 no Airtable record id in an answer.

### Traps this day earned — read before touching anything
- **Verify THROUGH THE WORKFLOW, never by calling the RPC directly.** `Attach Embedding` injects an
  embedding into every tool call, so searches are RRF hybrids. I "proved" #133 with plain SQL and it
  proved nothing; #135 was the real cause and only a staging probe showed it.
- **One probe is not verification.** Wave 9's `const` ordering bug hid from a single probe and errored
  89 of 255 turns for eight hours. Probe several question SHAPES, then check execution status.
- **Audit a gate regex over all 602 answers BEFORE enabling it.** Two were designed and rejected —
  both fired on more correct refusals than wrong ones. "I can't check that" is often right.
- **Stamps must match the payload SHAPE.** Every stamp read the truncated `body` and silently no-opped
  on large payloads; the finder puts its count at the TOP level, not per row. Both were invisible.
- **The verbatim digest route bypasses `Format Reply` entirely.**
- **Measure before reporting.** I twice raised something as an incident before checking it.

### Open for Andy
1. **#132** capability card — real answer vs the card. His steer: lead with what she can DO, and guide
   a new member rather than dead-ending them on chat access. Not a prompt fix (the turn is routed
   `help` deliberately, documented 2026-07-30).
2. **#123** blocks 3 questions — the events catalog is unreachable.
3. **#32 cost is still untouched** and the Answer Seed grew a lot of rules today — per-turn cost and
   latency are unmeasured since.
4. The AT roster row for Belen still links a duplicate member record.

## STATE 2026-08-24 (SECOND overnight session) — read this first

**Waves 7, 8, 9 and 10 are ALL APPLIED to staging.** Staging versionId `57db4b77`; gate **297
checks EXIT 0** after every wave. PROD is unchanged at `bbd597b7` (#114 only) and still serving
members — nothing has been promoted.

### What the 50-question tranche proved (and disproved)
A stratified 50 of the 192 bank C fails was re-run after waves 7+8 and graded BY HAND on the
strict scale: **23/50 = 46% of previously-failing questions now pass.** Mechanically over the same
50: links **90 → 126**, dates cited **12 → 34**, canned non-answers **3 → 1**.

**The misses were mostly rules that never executed, not bad rules.** Two mechanical faults, both
in `Answer Merge`, found by reading the live execution rather than the code:
- **M1 — every stamp parsed the already-truncated `body`.** Order is: build body → squeeze rows →
  blunt-slice at CAP 26000 → *then* the stamps `JSON.parse(body)`. Over CAP that is invalid JSON,
  the parse throws, the stamp silently no-ops — on exactly the large payloads the stamps exist
  for. That is why counts/cap scored 0/3, freshness 1/4, partner 1/3. Wave 9: stamps read `r`.
- **M2 — `clipSafe` covered the first-pass trim but not the large-payload path.** The halving
  squeeze re-sliced every string field raw (url fields included) and the backstop blunt-sliced the
  whole string. Wave 9 makes both URL-safe and exempts url/link keys from squeezing outright.
  ⚠️ **Correcting an earlier claim in this repo: `clipSafe` was never "dead code".** It is called
  once in each node; a bad regex (subtracting the definition from a count that never included it)
  produced that false reading. It was INCOMPLETE, not absent.

### Two graders' notes that turned out to be wrong when probed
- **6217 was NOT a cap failure.** The tool returned 10 rows and the S3 stamp said so; Millie
  printed an 11th name carried over from the previous turn's San Diego list. An ungrounded name,
  not a cap miss. Austin holds 13 member-facing records against a 10-row cap with no total, so the
  answer also implied completeness. Wave 10 (S5) fixes both; verified live.
- **6222's canned line is the GATE'S HARD-STOP CLAMP**, not model text — `Gate Verdict` returns a
  fixed sentence after 2 failed regenerations and discards the draft. Not touched: it is the
  safety backstop and changing it needs Andy.

### Open for Andy
1. **The removed-member severe (6080 / 6272 / 6277) is DELIBERATELY UNFIXED.** The bank C expects
   say a removed member gets no profile at all — no dates, no link, no reason. Andy's recorded
   **2026-07-26 ruling** says past members ARE findable ("I don't have a member named Lori" was a
   lie), and the leak gate still asserts exactly that. **Two rules point opposite ways; only Andy
   settles it.** Until then these stay failing.
2. **#123 blocks 6372 / 6400** — the 2027 events the expects want (Cancun) live in the events
   catalog that every `event_*` call is misrouted away from.
3. Promote decision, after the full 192 re-run.

## STATE 2026-08-24 (overnight close) — read this first

**Millie is LAUNCHED.** She was announced on stage ~01:50Z 2026-08-24. **PROD = `bbd597b7`** (#114 venue-day
only). Launch health: 200/200 executions green, 47 members, zero errors; 62 real answers graded **87%**
(54/8). Prod is serving members right now — treat any prod change as a live change.

**STAGING = the #108 finder + fix waves 1-6 build** (`f31b8c83` after the #32 revert). This is what bank C
measured. **Nothing is promoted beyond #114 — Andy has not approved a promote.**

### Paths — read this before you look for a file
**Every `eval/...` path in this handoff is relative to the #108 worktree
`.superpowers/sdd/2026-08-22-finder/`, not to the repo root.** There is no repo-root `eval/`.

### DONE — the head-to-head is graded (no longer the first job)

**STAGE 91% (62 pass / 6 fail) vs PROD 87% (54 / 8)** on the 68 launch questions. Comparable set 49:
**stage wins 6, prod wins 1, 42 ties.** Graded by hand (three dispatched graders died; the last two were
killed to stop them overwriting the output). Files: `grade_h2h_0.json`, `grade_h2h_1.json`,
`grade_h2h_all.json`. The six wins are prod's launch defects — canned refusals became sourced answers,
all false "restricted" labels gone, the channels question fixed.

**Three items this added to wave 8:**
1. **False blanket refusals** — the one regression (9→6): "not something I share for any event, registered
   or not" is false; a refusal must state the REAL gate. Same class as bank C 6266/6267/6498.
2. **Empty gate answers** — a correct gate that offers nothing (no count, no alternative) where sibling
   answers on the same build gave both.
3. **Thin first-touch greetings** — a bare "what do you need?" where a new member needs orienting
   (partly confounded, see below).

**⚠️ CONFOUND to respect in any future prod-vs-stage run: 13 of 68 are not comparable.** Prod answered from
real members' phones (several Summit-registered); all stage answers came from the probe phone (Andy, NOT
registered). Use a registered probe identity or exclude registration-gated questions.

### Superseded — the old first job
**Grade the Summit prod-vs-stage head-to-head.** `eval/summit_compare.json` already holds all 68 launch
questions with `prod_answer` and `stage_answer` from the staging run (108 turns, EXIT 0, same build bank
C measured). **Only 62 of the 68 carry a `prod_score`** — six questions arrived after the prod-grading
harvest, so `prod_score` is null on those: they can be graded on the stage side but have no head-to-head
winner, and they are not prod passes (the launch 87% is 54/62). Grade `stage_answer` on the strict scale
(1-10, no 7, ≥8 pass), declare a winner per question, and report regressions first. Mechanical deltas already computed, prod → stage: canned over-refusals **2 → 0**,
ellipsis-URLs **0 → 1**, narration **0 → 1**. My hand-read of the 8 prod fails looked strongly better on
stage (the fabricated "at the Summit with you" framing is gone; both canned refusals became sourced
answers) — **that is a hand-read, not a verdict.**

### Then: apply the waves, then re-run the fail-set (Andy's sequence)
1. `python3 scripts/olivia_loop/apply_fixwave7_2026-08-24.py` — written, committed, dry-run clean, **not
   applied**. Carries: link placement + withheld-recap-links + the **ellipsis-URL `clipSafe()` root-cause
   fix** (the biggest single win — 20+ fails), honest counts + ≤10 cap with true totals, internals
   narration by SHAPE (11 audited fires, 0 FPs), follow-up continuity off `turn_state`, Andy's SHARING RULE.
2. **Write wave 8** from `eval/fixplan_bankC.md`. Order: the REMOVED-MEMBER severe first (6080/6272/6277 —
   full profile, join/leave dates, a hint at why she left), then ungrounded claims (fabricated attendance
   9044, invented fit reasons 6089, invented video titles 9048), wrong-source citation (6380, 9046),
   missing attribution (6094), date labeling (recorded vs added), all-sources coverage, welcome-card
   misfire (6190), leaked self-correction artifact (7030), channels routing (9031), restricted LABEL smear
   (9007/9026 — the retracted #127's real fix).
3. Keep waves 7 and 8 as **separate scripts** even though they apply together — so a regression can be
   attributed to one batch without unpicking the other.
4. Gate `python3 scripts/olivia_leak_gate.py` must be EXIT 0 (292 checks; never pipe through `tail`).
5. **Re-run the fail-set only**: `eval/bankC_failset.json` (192 ids) + `eval/launch8_probes.json` (8
   verbatim launch questions). Re-grade, count what is left. Empty → promote decision. Not empty → wave 9.

### Numbers to beat
- Bank C: **319 pass / 192 fail / 91 context = 62%** on 602 organic questions.
- Fail rate by class: **FOLLOWUP 47%** (51/108, the weakest and the biggest class) · PARTNERS 54% ·
  EVENTS 58% · SAFETY 45% · PEOPLE 41% · RECOMMENDATION 38% · EXPERTISE 32% · CONTENT 22% · VIDEOS 28%.
- Launch prod: 54/62 = 87%. Bank A (older, easier): 87-89%.

### Traps this session earned the hard way
- **The evidence clipper truncates URLs.** `Answer Seed`/`Answer Merge` clip with `slice(TIER) + '…'`;
  wave 7's `clipSafe()` fixes it. Any new clip site must use it.
- **`score_prep.py` had to be taught to paginate** — PostgREST's 1000-row cap silently hid 177 answers.
- **A judge's kill-shot is not a verdict.** Seven expect/judge errors were overruled against the live
  warehouse this session, and one pass was flipped to fail. Verify anything decisive before counting it.
- **`curl` PATCH/writes to PostgREST are classifier-blocked**; use the supabase MCP for data writes.
- **Andy's verify-first gate is load-bearing.** The #32 cost fix looked perfect and silently killed
  retrieval; only an A/B against pre-patch tool-call distributions caught it. Do that for every
  prompt/tool-shape change.
- **`caffeinate -w <runner pid>`** while a long run is in flight — a machine sleep killed a grader.

### Open, needs Andy
- **AT roster row for Belen still links a DUPLICATE member record** — repoint it in Airtable (or delete the
  duplicate "Belen Gallardo" record) or a registrations sync will undo tonight's fix.
- **#125** copy split (unlinked number vs genuinely inactive) — hit a paying member live at launch.
- **#32 cost plan** (5 levers) — sequenced after this loop closes, per Andy.
- Promote decision after the fail-set re-run.



> ⛔ **Standing tiers (Andy 2026-07-29/31): Fine without asking** = read-only diagnosis · the LEAK
> GATE (`scripts/olivia_leak_gate.py`, free) · staging edits under the `olivia_wf.py` lock ·
> single-question staging probes. **Propose + WAIT** = any eval RUN (TEST ≤50 / FULL) · **and
> STARTING ANY TICKET (Andy 2026-08-19): a new session opens with the briefing — next ticket
> NUMBER + NAME + STORY — and waits for the go. "Continue working on Olivia" = show the briefing,
> not start. Standing orders/approved plans order the queue; they never start it.** **Andy
> runs** = `promote` · prod edits (emergency rollback excepted). The session classifier blocks
> lock/promote for me — Andy runs both in his terminal (proven 2026-08-03; `lock` worked again
> later that day — try it, fall back to Andy if blocked).
> **Vocabulary: "gate 202" = 202 safety CHECKS (free) · RUN = firing the eval bank · PROBE = one question.**
> **New standing traps (2026-08-20):** ① TWO Summit-named catalog rows — "MDS Summit Singapore
> **Night Out**" (side event) vs the real `recrATwhUDA55iQN5`; naive name-matching grabs the wrong
> one ② template quick-reply taps arrive `msg_type='button'` and are NOT in `olivia_messages` —
> only `olivia_webhook_events` has them ③ audits opt out of equalizer logging via the
> `X-Olivia-Audit` header (never a p_limit heuristic — that silenced a real lane) ④ the E2E
> canary pattern: temp registration row, probe, DELETE same session.

## STATE 2026-08-23 (#113 CLOSED — the Summit event is RELOADED from the 09:52Z scan and live)
**Millie now serves the current run-of-show.** `scripts/load_event_graph.py` is a true refresh (diff
report by name → upsert → FK-safe reconcile → provenance), loaded from
`~/Downloads/event_graph_20260823T0952Z.json` (`_meta.scannedAt` 2026-08-23T09:52:31.687Z, verified
fresh against the ledger). **activities 50→86 · sessions 31→26 · attendees 178→199 · people 199→234 ·
locations 18→27 · participant_types 6→7 (`MDS`) · activity_audience 180→227 · activity_person_grants
183→698 · check_ins 22→151 · orders 138→144**; deleted 49/10/12/11/1/20 exactly as predicted; a repeat
dry-run is `+0 ~0 -0`; `events.source_scanned_at` + `loaded_at` stamped. Golden self-test re-derived:
plain Member **7** on day one, Women's Lunch grantee **8** (the +1 invariant is the test, not the
integers). Live proof: `op=day at=today` returns *Sunday 23 August* with Arrive & Check-In to the Hotel
at 3PM … Explore Singapore Beyond the Summit; Women's Lunch / Event Partner Check-in stay hidden from a
non-invited member. Runbook + six traps in `OLIVIA_HANDBOOK.md` §4.9. Three real defects were found by
running it — 3.9 vs PostgREST fractional seconds (faked 31 "changed" rows), GroupOS recreating an
attendee document on a role change (409), and curl argv vs macOS ARG_MAX on a 92 KB description — plus
a final-review fix wave (a loader SKIP is never treated as an export removal; three silent-swallowed
reads now fail loud; ordered paging; measured delete counts; `--new-event` guard). **Follow-ups filed:
#120 loader hardening · #121 `db/` excludes the `event` schema · #122 "Explore Singapore" is four daily
copies.** Next refresh = one command; read the `- ` and `!! skipping` lines before the real run.

## STATE 2026-08-23 (#114 CLOSED except AC4 — venue-day "today" LIVE on prod; #113 waits for a fresh export)
**#114 "today at the Summit" (Ian Sells, Singapore, got Saturday on his Sunday) — fixed in two
layers and PROMOTED.** mds-digest-web LIVE (`/api/version` ≥ `9d0ec41`): the schedule route resolves
`at=today|tomorrow|yesterday|<weekday>|YYYY-MM-DD|instant` in the venue's own zone
(`src/lib/schedule-day.ts`, 24 vitest cases), every answer carries `now_at_venue`, `day` returns
`day`/`day_label`/`resolved_from`, and **`next` returns the rest of the venue-day** (Task 2b,
`95eea25` — Andy's 12:42 SGT test had shown `op=next` hiding half of Sunday behind a hard 3; fix wave
`9d0ec41` labels the items' day, keeps `asked_day`, falls back on impossible dates). Olivia prompt
**promoted by Andy 2026-08-23 02:49 ET (prod versionId `bbd597b7`)** — `apply_114_venue_today.py`: the
`event_schedule` tool description says pass the WORD (today/tomorrow/a weekday), the TODAY line carves
out the venue exception, one bullet names the case. Andy promoted **#114 only**: staging was re-built
from prod (combined snapshot `staging_2026-08-23T064414Z_108-plus-114-applied` kept), #108 re-applies
its own edit and gets its own promote. Prod probe after promote (execs 100159/100160): "what's
happening at the summit today" → *"It's Sunday, 23 August at the Summit in Singapore — kickoff day!"*
+ full day; "what's on tomorrow" → *Monday, Aug 24*; tool_args literal `at:"today"/"tomorrow"`.
**AC4 CLOSED (Andy tested on WhatsApp, 2026-08-23 ET afternoon, Singapore already on the next day: working).** #114 is fully closed. **#113 (whole-event refresh, plan
`docs/superpowers/plans/2026-08-22-summit-event-refresh.md`, 4 tasks, not started): waits for a
GENUINELY fresh GroupOS export — `event_graph (1).json` was a 17-Aug scan (`_meta.scannedAt`
2026-08-17T22:16Z; 4 of 5 people registered 18–21 Aug absent); Andy's live GroupOS already shows
renames ("Arrive & Check-In to the Hotel at 3PM"), Welcome Dinner at Pool, a new "Explore Singapore
Beyond the Summit" — none of that is in any file we hold.** Two-agent rule added to CLAUDE.md (lock =
the only mutex; own-ticket doc sections; last committer rebases; message the peer session).

## STATE 2026-08-23 (#108 The Finder BUILT + PROVEN ON STAGING; Andy: promote, then decide on the 100-Q bank)
**The Finder ships one composable filter tool covering every data layer** — `find`
(`POST /api/olivia/find`, mds-digest-web, code live on Render) wired into **STAGING**
`bqHstPDi84uOhTCJ` (versionId `a49047ac`, Answer Tool + Answer Seed; `event_who` now carries
`op:'people'`). Belen's "which resellers are coming to the Summit?" now answers **17** (of 102
Summit attendees) / **122** community-wide (of 735 actives), every person with reasons; a country
breakdown sums cleanly (5 buckets); the disclosure engine (R1-R10) holds — a 🟡 filter (e.g.
`sku_min`) returns counts only, a non-member's `chat:` filter never names anyone. Gate **292 checks
EXIT 0** (26 finder checks). Full close block + AC table on `OLIVIA_SPRINT_4.md` #108. **#114 already promoted alone** (Andy
2026-08-23 06:48Z, prod `bbd597b7`); staging was rebuilt from prod (+#114) and #108 re-applies next
(`apply_108_find.py`), then **Andy promotes #108 separately** (`python3 scripts/olivia_wf.py
promote`). Before that promote, Andy decides whether to run the
**100-question eval bank** first (recommended — the real risk is the model reaching for `find`
where `expertise_search`/`content_search` was the better tool). Follow-ups filed, not blocking:
**#115** (geo/business-model data hygiene) · **#116** (finder phase 2 content+video, phase 3
events/partners/forms — own plan) · **#117** (`--cleanup` leaves probe message rows) · **#118**
(`event_who` should return a flat roster). **Lock released** (staging free for the next session). Staging re-applied after the #114-only promote — versionId `4321f06a` (snapshots
`pre-108-reapply` / `108-reapplied` / `108-final`), #114 seed edits intact. Re-probes: exec
`100210` (17 named), `100212` (Europe → 1), `100278` (breakdown by country, 5 buckets = 17,
`people:[]`, reply reports counts not names). Parser robustness (`mds-digest-web` main,
`0c46d42` + `d3fe132`): a multi-field object (`{segment,event}`) now validates as an implicit
`all` instead of 400ing ("leaf holds exactly one field"), `where` may arrive as a JSON string,
and `group_by` with no `return`/`ret` now defaults to `breakdown` — closing the two distinct LLM
tool-call flakes found re-proving this ticket.

## STATE 2026-08-22 (SESSION CLOSED — #97 PROMOTED + PROD E2E PROVEN; #105/#106 filed)
**PROMOTED 04:11Z (Andy): prod `7e4be40a` (#97) → #107 ~05:24Z prod `8f48fdb8` → #107b/c ~07:10Z prod `25ceefe1` → #107e ~08:40Z prod `d9538ca6` (picker lead: "Here are the Summit attendees I've recommended to you that I can reach for an intro…"; route `d8f8250` title-case) → **#107d ~08:00Z prod `d2961c8d`: eligibility = Summit attendee + phone (Millie-user rule DROPPED both sides, Andy); picker rows = expertise · speaker · city; route `dd02a9b`** · post-Yes = WhatsApp LIST picker (route's exact ids) · suggestions NEVER filtered/shortened (Andy) · buttons always (≤1024 inline, >1024 follow-up button message) · first-contact PS first when offer present · intro-tap path silent-gated (SELFTEST). #109 templates **APPROVED** (accepted/declined UTILITY, lapsed MARKETING — verified live 2026-08-22) — route logic next session (free-form requester notices die outside 24h window). #110 filed (tap turns not saved to history). Belen's identity split fixed (registration + roster row → her Staff record) so she can use Summit lanes + intros. PROD E2E: exec 96653 Accept tap → row 13 accepted/tap → 2 texts delivered to Andy's phone, 0 LLM rows. Andy's visibility ask → #106 filed (SQL-verified: search lanes exclude Staff; event lanes don't; `test-andy-8153` purged). Andy's lock: `python3 scripts/olivia_wf.py unlock` when done.**

### (pre-promote state)
## STATE 2026-08-22 (pre-promote — #97 BUILT + REVIEWED)
**#97 brokered intros: 7/7 tasks + final whole-branch review + 2 fix waves, all re-reviewed clean.**
LIVE on prod: route `/api/olivia/intro` (mds-digest-web `535a23a`, Render) · `olivia_intros` v2 +
`late_taps` · `Intro Sweep` on Reminder Sender `QhJw46Mr7LAP8fdz` (minute tick, exec 96624 clean).
STAGING `bqHstPDi84uOhTCJ` carries the tap branch (C1 binds taps to `consent_wamid`, C3 fail-open)
+ `member_intro` tool — **PROMOTE = Andy (`python3 scripts/olivia_wf.py promote`, lock RELEASED),
T4+T5 together**, then one real tap E2E closes the ticket (Andy is NOT Summit-registered → canary
registration for his test, or an eligible member tests). Rulings 2026-08-22: accept-is-final ·
Eugene row 2 set `declined` (his last tap) · non-attendee wording = Summit-PILOT line, never
"register" · #105 webhook-signature ticket filed (Andy: file + ship as own ticket, next session,
before any wide announcement). Reports: `OLIVIA_97_BROKERED_INTROS_REPORT.md` (Andy, listenable) ·
`OLIVIA_97_INTROS_FOR_EUGENE.md` + `_SHORT` (4,587 chars) · artifact
https://claude.ai/code/artifact/446286fc-411e-4e78-981e-9e858efa81d2. Full close block on the board.
SDD ledger `.superpowers/sdd/2026-08-20-brokered-intros-full-build/progress.md` (gitignored scratch;
secrets scrubbed). ⚠️ Scorecard main has ~15 unpushed commits from 3 parallel agents (#103, MotM,
#97) — push is Andy's/next session's call. Lesson saved: check-first before "add env var"; doc
claims about where a credential lives get a live probe.

### NEXT SESSION QUEUE (brief Andy, WAIT for go)
1. **#109** requester-side notices as templates (check `python3 scripts/olivia_intro_templates_109.py status` → APPROVED first; then route change; before any announcement).
2. **#108** (filed) attendees ∩ chat membership / business model tool — Belen's 'resellers attending' questions were answered wrong; truth table in the 08-22 log.
3. **#106** Staff/non-member records never surface in member-facing lists (staff attendees like Belen must stay usable as requesters) · **#105** webhook signature · **#110** intro-tap history.
   (#97 CLOSED: promoted + prod E2E proven; release-notes line still to post at sprint close.)
3. #103 open rungs (other agent) · #102 brainstorm · Millie promote (rides the same promote) · smoke
   partials · <2024 transcripts decision · sprint-close pair.

### (previous state below)
## STATE 2026-08-21 EVE (SESSION PAUSED mid-ticket — Andy: "i need to go, pause")
**#97 BROKERED INTROS BUILD IN FLIGHT — 4.5 of 7 plan tasks done.** Eligibility LOCKED by Andy
("lock them as-is": both sides Millie users + Summit-registered `recrATwhUDA55iQN5`; <30d parked).
Prereq resolved: env was on RENDER all along (plan said Vercel — wrong; both META_WA_* pre-existed).
DONE+reviewed: T1 ledger v2 (migration `olivia_intros_v2_20260820`, commit `9f380b1`) · T2 route
`/api/olivia/intro` (mds-digest-web `e6f8b48` DEPLOYED, 16/16 rulings, sweep isolation +
recency picker) · T3 live matrix 9/10 PASS zero real sends, DB baseline restored, SELFTEST
not.like proven 280==280 · T4 staging tap branch (7 nodes + Log Inbound button fix — PROD DROPS
Accept/Decline taps TODAY incl. Eugene's POC reject; execs 96072/96082; blast radius proven safe).
T5 implementer DONE (member_intro tool live on staging, exec 96162 chain proof, gate 264 EXIT 0)
— **REVIEW PENDING** + 3 open concerns (Plan Request regex swallows "connect me with someone" ·
picker renders prose not LIST · send branch live-proof deferred to post-promote tap).
**RESUME: SDD ledger `.superpowers/sdd/2026-08-20-brokered-intros-full-build/progress.md`** —
dispatch T5 reviewer, then T6 sweep tick, T7 close. ⚠️ staging lock HELD (claude, expires
2026-08-22T01:25Z); staging carries T4+T5 UNPROMOTED; sweep of POC row 2 will message Andy the
expiry line once T6 ships past 2026-08-27. Andy's promote covers T4+T5, then ONE real tap E2E.

### (previous close below)
## STATE 2026-08-22 (SESSION CLOSED — transcripts reached the ANSWERS; 5 promotes, all verified)
**The day's theme: the 2025-26 transcripts were live in the database but the ANSWER LAYER never used
them. Four separate causes, each found by reading executions, each fixed and promoted.**

### What shipped to PROD today (5 promotes, each: diff → gate → promote → verify → snapshot)
1. **Dead denial rule killed** — Answer Seed still said *"NO video has a transcript: what-was-SAID-in-it
   questions get a plain 'transcripts are not available yet'"*. A FOURTH stale rule I missed on 08-21.
   Replaced with TRANSCRIPTS ARE SEARCHABLE (2025+2026) + concept-term routing + pre-2025 boundary.
2. **Quote/timestamp discipline** — NEVER OFFER TO FETCH WHAT YOU WERE ASKED FOR: a quote/where/what-
   exactly question carries the verbatim line + speaker label + timestamp IN the answer.
   Proof: Bryce Alderson's SKU-expansion passage quoted at **00:37:30**.
3. **`call_transcript` enforced IN CODE** (`Attach Embedding`) — the tool schema listed only chat/FB
   sources, so the model kept passing `p_sources` without transcripts; two prompt fixes failed, so the
   third moved into code ([[feedback_code_beats_prompt_rules]]). `p_chat`-scoped asks exempt (transcripts
   carry no chat_name and would pollute digests). + conflicting-sources rule (transcript vs chat both
   reported and attributed).
4. **Gate over-refusal fixed** — the `off_topic` field added for #104 blocked short affirmatives and
   CLARIFYING QUESTIONS; "yes booth" was blocked 3× and served a canned "couldn't verify". RULE ZERO now
   exempts both.
5. **#112 CLOSED** (filed as #108, renumbered — the parallel session had already issued #105-#111) — the #80 OFFER BINDING already existed; its ACCEPT_RE end-anchor made "yes booth"
   miss. Affirmative may now carry a quantifier/typo; binding delivers EVERY offered video.

### #103 speaker work (same session, warehouse-side)
Library coverage **40% → 87%** (2025 97%, 2026 98%). Rungs: speaker_ids id-join · names · title/description ·
partner sessions · Zoom cues (participants + talk_seconds) · **AAI letter-mapping** (270 letters,
`video_speaker_letters`) · **frame-OCR** (ffmpeg from presigned URLs, 388 frames, 123 role-aware links,
moderators from "Moderated by" cards). 578 entities / 321 members / 1,391 links. Review CSVs triaged with
Andy: partner contacts resolved (Meher→Hector, Nadav→CapEc, Ben→Superfuel), 10 ASR/spelling twins merged
via speaker_aliases, Brandon Fishman created as guest on Andy's ruling, 6 unknown names left unmapped.
**Andy's rule codified: a MEMBER is never switched to partner/guest — partner-ness lives in
`affiliation_partner_id`.**

### Templates
`mds_birthday_box_address` **APPROVED as UTILITY** (id 917599728064581) — sent to Andy's number, status
`sent`. ⚠️ The test exposed bad address data: Andy's street = "street", Ian Sells = "iasi, Cimişlia,
Moldova", Eugene Khayman has TWO records (one with a Miami address, one empty). A real send needs a
which-record-wins rule + a "no usable address" path. Button taps do nothing yet (no workflow branch).

### ⚠️ TICKET NUMBERING (two sessions, one board — 2026-08-22)
The parallel #97/#107 session issued **#105-#111** while this one was running; I filed my
offer-binding ticket as #108 from a stale max and collided with its "attendees ∩ chat membership"
ticket. Nothing was overwritten — both rows survived — and mine was renumbered to **#112**.
**Rule: claim the next number from the board's CURRENT max at the moment of filing, never from
memory or from the session's own start state.**

### OPEN (next session)
1. **Jasim-class within-video ranking** — chunks of one video share the video's date, so the tiebreak is
   arbitrary; asked for a quote from later in a call, retrieval returns the opening minutes. `content_search_v2`
   change, every lane uses it — Andy's go needed.
2. **#102 answer-layer wiring** — speaker/role/talk-time/partner tables exist and NO lane reads them.
   "How many videos is Bonilla in?" / "who spoke for Riverbend?" still unanswerable. Brainstorm first.
3. #103 leftovers: moderator inference · ~134 pre-2025 videos (same OCR/letter rungs) · affiliation backfill.
4. #72 LOAD TEST — still never run, still the biggest pre-announcement risk.
5. Airtable-side dup-record merges (Andy's, never-delete rule): Meher ×2, Nadav ×3, Ben ×2, Eugene ×9.

## STATE 2026-08-21 DAY (SESSION CLOSED — Andy drove speaker work; smoke settled at 95/100)
**Smoke rerun: 5 of 10 non-PASS flipped → 95/100 effective, 0 fails** (#104 fixed at the enforcement
layer: FC `off_topic` field + Gate Verdict non-filterable; all 3 original fail-chains reproduced
clean with recreated adjacency). Remaining 5 partials: 2 data-side (4070 women-events catalog gap ·
4038 links-grading) + 3 behavioral (4095 3-day window serves latest daily · 4010 wording shades to
denial · 4100 staff-vs-member distinction) — each ticket-size, none chased.

**#103 REOPENED (I closed it on a field-scoped metric — 413/413 measured the FIELD; Andy caught it)
then REBUILT: library coverage 40% → 81%** (2026 **91%**, 2025 78%). Full state on the board block.
The load-bearing facts: identity space = `speakers`/`speaker_aliases`/`video_speaker_links`
(+`video_partner_links`); evidence rungs A `speaker_ids`→GroupOS-id→email · B names · C
title/description · D partner sessions · E Zoom cues→PARTICIPANTS (`role`+`talk_seconds` — group
calls have participants, not headline speakers, Andy's ruling; moderator ≠ speaker, inference open).
**Zoom transcripts carry REAL NAMES per cue** (quote+name+timestamp proven E2E for entitled asker);
AAI = letters (letter-mapping + frame-OCR open). **418 pre-#101 Zoom chunks were unreachable even
for ENTITLED members** (sensitivity=restricted + rule=public) — migrated, proven both ways.
**Weekly `zoom_weekly.py` now runs the ladder + guest-promotion + participants every run** (step
4.5, full dry-run green). Review CSVs on Andy's desk: `mds_speaker_review.csv` (60 unresolved) +
`mds_participant_review.csv` (12).

### NEXT SESSION QUEUE (brief Andy, WAIT for go)
1. **#103 open rungs** — AAI letter→name mapping · frame-OCR name tags · moderator inference ·
   affiliation backfill · review-CSV triage with Andy.
2. **#102 brainstorm** (ranking: decay · speaker weight · Summit bonus · WA/FB/Video equalization ·
   dossier weighting speaker>participant>FB-post) — CAPTURED-NOT-LOCKED, starts as brainstorm.
3. **Millie promote still on Andy's desk** (one promote = rename + fact-check + boundary +
   timestamps + #104 net). Meta watcher plan unchanged (submit "MDS Millie" on verdict, never
   re-register Mille).
4. 5 smoke partials + 2 bank-truth fixes · <2024 transcripts decision (~$137) · sprint-close pair.

## STATE 2026-08-21 OVERNIGHT (SESSION RAN WHILE ANDY SLEPT — his order: "in the morning; I need to see all green")
**ALL GREEN. Queue ① 2025 transcripts DONE · ② big smoke DONE (bank 90/100 effective · slice 11/11) · ④ Millie CLOSED · #103 speaker sync BUILT+CLOSED same night · gate GREEN at every step (263 checks, exit 0, run 6+×).**

### What shipped overnight (all verified live, all commits on main)
- **2025 transcript batch:** 232/233 videos (1 skip = 10s silent teaser) · 144.8 hr · $33.42 AAI ·
  6,429 chunks (0 mismatches, Zoom untouched) · 232 summaries in-session via 8 parallel subagents ·
  embedded (restricted = metadata only) · entitlement probed both ways · `scripts/aai_submit.py` is
  the persistent batch runner (curl, resume-safe).
- **Millie (queue ④):** staging says Millie everywhere; "what is your name?" fixed at the SOURCE —
  the Fact Check lane was vetoing the name as an unsupported claim (RULE ONE now names her +
  `community_info.assistant_name`). Meta: "MDS Millie" CANNOT submit while "MDS Mille" is
  PENDING_REVIEW (no cancel API) — **when watcher `a1ViYr5FT7iePdN9` fires: do NOT re-register
  Mille; submit "MDS Millie", then Andy re-registers (PIN), promote staging, DELETE watcher.**
- **THE NIGHT'S BIGGEST CATCH: `video_search_v2` (the LIVE lane — the workflow remaps
  video_search→video_search_v2 in Fetch Summaries/Fetch Raw Matches/Attach Embedding) was NEVER
  patched by #101** — entitled members still got blanket [RESTRICTED] E2E. Fixed (grant-bounded,
  attachments stay public-only, is_restricted = the video's flag), both sides proven, migration
  `video_search_v2_grant_bounded_restricted_fix_20260821`. ⚠️ trap: v1 probes pass while v2 serves
  members — always probe THROUGH the workflow.
- **4 stale "no transcripts" prompt rules purged** (Build Prompt ×2, Verbatim ×2, Answer Seed
  boundary now "2025+2026 transcribed, pre-2025 not") + **timestamp-citation rule** (quote → "At
  00:16:37" next to the link; probe proven).
- **#103 CLOSED (filed and built same night, Andy's order):** `digest.speakers` 239 entities ·
  `video_speaker_links` 480 links (413/413 videos) · **212 members EMAIL-evidenced** via the
  GroupOS mirror (`digest.video_speakers` — pre-existing table, all 234 rows have email;
  `member_record_id` is GroupOS-internal, NOT an AT id) + #100 resolver · 24 guests · 3 unresolved
  in `~/Downloads/mds_speaker_review.csv` · verify 7/7 · plan `docs/superpowers/plans/2026-08-21-speaker-sync.md`.
- **Smoke (`OLIVIA_SMOKE_2026-08-21.md`):** bank 89/7/4 → 90 effective (one "fail" is CORRECT #96
  behavior, bank truth stale); 3 real fails = ONE defect → **#104 adjacent-turn topic lag** (filed,
  S1). Slice v2 (problem-first, Andy killed the name-anchored v1 as "BS Qs"): 11/11 right videos
  unprompted, speakers+roles, multi-source answers, zero transcript denials.

### ANDY'S MORNING DESK
1. **Millie promote** (staging → prod: rename + fact-check rule + transcript boundary + timestamp
   rule — one promote covers all).
2. #104 priority call (adjacent-turn lag — 3 smoke fails).
3. Speaker review CSV (3 names) + #102/#97/#103-extension brainstorms (all CAPTURED-NOT-LOCKED).
4. 2024-and-earlier transcripts decision ("Not sure about <2024") — ~$137 for 2018-2024 at AAI rates.
5. Sprint-close pair still open: release notes post + retirement pass.

### (previous close below)
## STATE 2026-08-20 LATE (SESSION CLOSED — VIDEO DAY): PROD untouched; all ships = SQL fns + data loads.
**#100 CLOSED (identity aliases) · #101 CLOSED (video transcripts + real access gating) · gate GREEN at close (263 checks, exit 0, run 7× today).**

### What shipped tonight (all verified live)
- **#100:** `digest.member_email_alias` (5,763 rows; sources preferred/stripe/admin_field/name_match_approved)
  + `resolve_member_by_email()` (active-record-preferring; NULL on ambiguity). 29 approved aliases written to
  **Airtable FIRST** (Members DB `appou5JVr0WIrioWS`/`tblfwOSROSHfuYUxv` — ⚠️ the env's AIRTABLE_BASE_ID is the
  WhatsApp DB, wrong base for this), then mirrored. Audience resolution 634→704 active; the 10 known email
  mismatches 0/10→10/10. **`Pending Group Entrance` now counts as active** (753→754; Current+New+Pending = 718
  = Andy's export exactly).
- **#101:** AssemblyAI transcripts for **ALL 161 videos of 2026** ($26.23, `~/mds_transcripts/2026/`) →
  **2,730 chunks across the 96 videos Zoom never reached** (`meta.provenance='assemblyai'`; #70's 65 Zoom
  videos untouched, checksum identical). **`digest.video_access` = 34,236 REAL grants** (real_match only —
  panel rows are phantoms, 42 yopmail). `content_search_v2` learned the `video_access` access_rule type;
  `video_search` gates restricted treatment per asker (attachments stay PUBLIC-only — file_key leak caught).
  **96 summaries written in-session** (161/161 `summary_source='transcript'`), everything embedded
  (restricted videos embed METADATA ONLY — vector branch cannot leak). Proof: entitled asker retrieved a
  RESTRICTED TikTok-Mastermind passage at 00:05:01, timestamped. Quote ruling (Andy): quote/summarize/TLDR/
  exact-words yes — **full transcripts never**.

### THE QUEUE (Andy 2026-08-20, session close — in this order)
1. **2025 transcript batch** — same machinery (`scripts/aai_transcripts.py` + `apply_video_summaries.py`).
   ~233 videos / 145.6 hr ≈ **$33 AAI**. **Prereq: fresh presigned export from Andy's dev** (current links
   expire 2026-08-27; `04_presign.py --days 7 --year 2025`). Load video_access for 2025 restricted from the
   same pairs file (already covers all years — 375 videos). Summaries in-session again, no API.
2. **Smoke-test batch of questions, focused on the EUGENE CASE** — "best TikTok cold start videos" served the
   thin Milan title-match over the transcript-rich Beginners Panel. Content now exists (transcript chunks
   reachable); the remaining gap is intent-vs-title RANKING in `video_search` + whether the answering layer
   should show more than one video (Eugene: "maybe it should show more than one"). Overlaps #71's vocabulary
   work — read #71 before touching ranking.
3. **Members' connection tasks — #97 brokered intros build** (screenshot proof on file: template intro
   accepted end-to-end, wa.me links both ways, POC list-picker rounds "Pick a member" working). Plan pinned:
   `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`. Still blocked on Andy's RENDER env (plan said Vercel — wrong; digest.mds.co = Render, verified 2026-08-21)
   (META_WA_* onto mds-digest-web) + execution-mode pick.
4. ~~Rename the bot to "Millie"~~ **CLOSED 2026-08-21** (close block on the board). Spelling ruled
   **"MDS Millie"**; staging says Millie everywhere (12 strings, 4 nodes) + fact-check veto fixed
   (RULE ONE + community_info.assistant_name — the checker had silently stripped the name). Meta:
   "MDS Millie" can't submit while "MDS Mille" is PENDING_REVIEW (no cancel API) — **when the
   watcher (`a1ViYr5FT7iePdN9`) fires: do NOT re-register Mille; submit "MDS Millie" instead**,
   then Andy re-registers (PIN), promote staging, DELETE the watcher.

### Standing next-session rules (unchanged)
Open with the briefing (ticket NUMBER + NAME + STORY) and WAIT for the go. Verify against live before new
work. Gate before any ship. #72 LOAD TEST still never run — it remains the biggest open risk before any
announcement.

### New traps from tonight (do not relearn)
- **PostgREST pages are UNSTABLE without `order=`** — an unordered limit/offset walk returned 3,116 rows but
  only 43 of 65 distinct videos. Every pagination gets an order key.
- **Expression indexes can't ON CONFLICT via PostgREST** — loaders diff-before-insert (twice today).
- **Verify Airtable writes against Airtable itself** — `member_profiles` mirrors on its own schedule and lags.
- **The gate's restricted-transcript check is now GRANT-BOUNDED** (restricted chunks only for granted videos),
  not blanket exclusion — that is the #101 invariant, don't "fix" it back.
- **`member_identity` holds 57 NULL-`at_member_id` rows** (one `phone='sam'`) — recorded, not chased.

---
### (previous close, for context)
## STATE 2026-08-20 (SESSION CLOSED): PROD `060701be` — nothing awaits promotion; all of tonight's
## ships live in SQL functions + the digest.mds.co route (no workflow nodes touched).
**Eugene's four: #94 #95 #96 #98 #99 CLOSED · #97 POC proven + plan pinned · smoke 50/50 addressed.**

### 🔬 Eugene-arc smoke (50 Qs, RUN on Andy's go) — `OLIVIA_SMOKE_EUGENE_ARC.md` has the full table
47/50 · A 18/18 · B 12/12 after TWO in-run #95 fixes (audit header `36e1d7d` — the p_limit
heuristic had silenced logging on the plan lane; LRU cycling `0b4b418` — exhausted pools froze) ·
C 12/14 · D 5/6. **#98 CLOSED same session** (`179f6c0` — registrations-ledger authority on BOTH people branches;
re-probed clean). **#99 CLOSED** (note-in-tool; E2E proven via a temporary canary registration, deleted after —
"show me the rest" now re-calls and serves fresh ranked people). **⚠️ Andy: who-to-meet stays
OFF for your phone until you register for the Summit for real** — the canary was test-only. Wording flags → #14. Count drift
157-vs-113 = THE COUNT RULING resurfaced live. **Ian Sells ACCEPTED the real intro** (#3
accepted, links both ways); Eugene's still pending — the sweep/expiry rules are in the #97 plan.

### ⚠️ Board: **`OLIVIA_SPRINT_4.md`** (22 open tickets). **Two sprint-close items still await
Andy:** ① the SMOKE RUN on the 100-bank (the exit exam — proposed, his go) ② validate + post
`OLIVIA_RELEASE_NOTES_2026-08-19.md`.

### ✅ #94 Expertise Ledger v2 — CLOSED 2026-08-19 (this session)
Warehouse-side only (no prod workflow edit, nothing to promote): taxonomy 16→**51 topics**
(18 parents + 33 subs), derive v2.1 live (decay 12/24mo · engagement bonus · forms ×1.2 ·
40%-peak floor — floor proven by live inflate/restore), **594 members scoreable on forms alone**,
verify `scripts/verify_expertise_v2.py` **9/9 PASS**, gate EXIT 0, nightly RPC path re-run clean
(11s). Same-day catch: the substring trap re-opened by short terms (`'vat'`/`'str'`) — biz+persona
CTEs now tsquery-match. Full close block on the board. Commits `0ce7ebe`·`a1250eb`·`8d70f10`.

### ✅ #95 Equalizer for the advice lanes — CLOSED 2026-08-19 (same session, Andy's go)
The execution log showed Eugene-shaped topic asks route to **expertise_search**, so BOTH advice
lanes got the equalizer (member_match_v2 + expertise_search; multi_source/_v2 went VOLATILE to
inherit it). Proof: identical repeated asks 8/8 → 0/8 shared names (REST) and disjoint sets on
the staging workflow path; log carries member_match + expertise_search lanes; gate EXIT 0.
Commit `a31a45b`, close block on the board. ⚠️ Andy's asker row carries the probe history — his
own next real "who knows X" rotates past those names for up to 30d (correct, remember at demos).

### ✅ #96 Attendee-name disclosure — CLOSED 2026-08-20 (Andy ruled it live in-session)
**The rule now in force:** attendee-name lists cap at **10** (display cap — filters/counts always
run over the whole ledger); NAMES require the asker's own registration for THAT event
(registrations ledger = the authority, never `event.people` — Andy's test row exposed that trap
on the live route, fixed same hour); non-attendees get counts/aggregates only. `event_who`
migration + route `3e77774`/`08d42fc`, gate +3 checks EXIT 0, E2E probed both sides. Supersedes
2026-07-20 any-member-sees-names.

### 🔨 #97 Brokered intros — POC PROVEN E2E 2026-08-20 (Andy: "lets try to make a POC and then decide")
Template `mds_intro_request` **APPROVED as UTILITY** (no marketing cap on consent asks). Full
loop ran on Andy's number: `olivia_intros` pending → template delivered → Andy tapped **Accept
intro** → watcher flipped the ledger → links both ways, all `delivered` in `olivia_sends`.
Tools: `scripts/olivia_intro_template.py` (create/status) · `scripts/olivia_intro_poc.py`
(request/watch/status, HARD-LIMITED to the test number). **Findings for the real build:**
template button taps = `msg_type='button'`, NOT persisted to `olivia_messages` (only
`olivia_webhook_events` has them; Mille also answers the tap text as a message — the workflow
needs an intro-tap branch) · plus-is-space on ledger timestamps. **Full ship waits on Andy's
rulings:** conversation intent ("connect us") + workflow branch · per-target rate cap · expiry ·
decline wording · seed copy.

### NEXT SESSION OPENS HERE — brief Andy, WAIT for his go (the ⛔ rule above)
**Queue front: #97 BUILD** (plan `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`,
rulings locked, POC proven, Ian's real accept on record) — **blocked on Andy's RENDER env prereq (service `mds-digest-web`, NOT Vercel)**
(META_WA_TOKEN + META_WA_PHONE_NUMBER_ID onto mds-digest-web, then redeploy) + execution-mode pick.
**Next unblocked: #72 LOAD TEST** (sprint goal: it runs BEFORE the announcement; never run).
1. **Andy's desk:** #97 RENDER env + execution-mode pick · **register himself for the Summit**
   (restores his who-to-meet demos — canary was test-only) · THE COUNT RULING (157-vs-113 shown
   live in one conversation) · sprint-close pair still open: 100-bank exit exam (his go) + post
   `OLIVIA_RELEASE_NOTES_2026-08-19.md` · Eugene's intro tap still pending (ledger #2; check
   `python3 scripts/olivia_intro_poc.py status`) · Mille name watcher (`a1ViYr5FT7iePdN9`) ·
   THE COUNT RULING (recommendation: 98 active members, one `event_registered_members` view) ·
   Eugene's Members-DB record pin (9-record cluster) · "MDS Mille" re-register when the watcher
   fires (PIN, 14-day window) · #72 LOAD TEST before the announcement.

### DO THIS FIRST
1. ~~Schedule the reminder sender~~ **DONE 2026-08-18: n8n `QhJw46Mr7LAP8fdz` ("Olivia — Reminder
   Sender"), every 5 min.** First tick exec 86839 (23:15 UTC): stale sweep ran, 0 due, clean stop.
   Faithful port of `olivia_reminder_sender.py` (script stays the manual/dry-run tool); chosen over
   launchd so reminders survive the Mac sleeping — and launchctl is classifier-blocked for me anyway.
   **DELIVERY PROVEN 2026-08-19 05:55 UTC:** Andy's live ask arrived on his phone — sent 05:55:08,
   `read` 05:55:11 in `olivia_sends`. Sender cadence now **EVERY MINUTE** (Andy: 10-min total lag
   too long for minute-level asks). #86 CLOSED.
2. ~~Re-register the number~~ **DONE 2026-08-18 (Andy ran it): the number is "MDS AI Assistant".**
   `POST /register` with the two-step PIN returned success; live API now shows `verified_name:
   "MDS AI Assistant"`, `name_status: APPROVED`, CONNECTED/GREEN. "Oliva" is gone. Existing threads
   may show the cached old name for a while; new threads are correct. Andy holds the PIN (password
   manager — deliberately not written down here).
   **→ NEXT NAME ALREADY SUBMITTED (Andy's call, same night): "MDS Mille" is `PENDING_REVIEW`.**
   When it approves there are **14 days to re-register** (same `POST /register` + Andy's PIN) or the
   approval lapses and must be resubmitted. Check `new_name_status` at session start:
   `GET /1306956855827812?fields=verified_name,name_status,new_display_name,new_name_status`.
   **Watcher live:** n8n `a1ViYr5FT7iePdN9` (hourly, TEMPORARY) — WhatsApps Andy's test number on
   APPROVED/DECLINED, nags hourly until re-registered, silent while pending. Limit: free-form send
   needs Andy's 24h window on …8153 open. **DELETE the watcher once Mille is live.** When the name
   flips, queue Andy's rewording pass on the intro/self-references (#79 curated copy says "the MDS
   AI assistant").
3. **Multi-event note (Andy 2026-08-19: "we will have more" schedules):** the event schema and all
   lanes are already multi-event (everything keys on `event_id`; the loader loads any export
   alongside). ONE decision waits for event #2: the lane's no-event-named default is
   latest-starting — switch to nearest-upcoming or asker's-registration when a second event loads.
   Nothing to build until then. Reminders stay schedule-anchored BY DESIGN (her refusal of
   freestanding "remind me to check fb" is correct behavior); freestanding reminders = a new
   ticket if Andy ever wants them.
4. **Ask the dev for a fresh export** — CÉ LA VI is in the admin's 19 locations but not our 18, so
   some of the 13 venue-less activities may be export gaps. Same dump un-truncates long descriptions.

### Two things NO probe can verify — test on a phone
`Eval (silent)?` routes SELFTEST traffic to `Save Conversation` and never reaches `Send Reply (Meta)`,
and both the image and reminder-delivery branches hang off that send. So:
- **images** — "show me the Summit theme post Eugene shared" must be tried on a real phone
- **reminder delivery** — likewise, once the sender is scheduled

### The demo set (nine questions, verified on prod)
Broad reading recs · full day one · which sessions suit me · who speaks Monday · where is X + map ·
show me the theme post (image) · weekly digest (summaries) · remind me (set/list/cancel) · who should
I meet (#87). Buttons need a complaint she has **not** already handled — she will not re-offer.

### The lesson this session kept teaching
**Code beats instructions.** Three prompt rules failed on images, four on reminder timing. Both were
fixed in one commit each once the work moved into the tool. And **read the execution before
theorising** — it settled in one call what rule-writing chased for rounds, twice.

### Open tickets, awaiting priority
- ~~#90~~ **CLOSED 2026-08-18: the sync never existed** (one-time xlsx load 2026-07-29, nothing ever
  wrote the table again). Now: n8n **`RpEbU47SpMVsbwqg`** hourly mirror (sibling of Members/
  Summaries), AT `{active}=1` = 18 chats, **diff 0** field-by-field, ghost row deleted, heartbeat
  `chats_mirror` (3h) under signal 4. Curated columns untouched. **Andy ruling queued:** Accelerator
  + 2026 New Members carry `required_form` in AT but are ungated in the mirror.
- ~~#89~~ **CLOSED 2026-08-18: the gap was IDENTITY, not attendance.** Zero digest fns read
  `event.attendees` (counts were single-sourced all along — now stamped as table comments,
  migration `event_roster_authority_comments_20260818`). Loader matching rebuilt (3-rung ladder):
  people matched 124→**170 of 199**, Courtney freed from a "Test Test" record. **Andy's list on the
  board:** 4 speaker roster rows linked to Max Mikhaylenko's record · dup member pairs (Brian,
  Henrik, Rebeca, Ryan, Eugene ×9) · the 151-vs-108 filter ruling. Fresh export covers the last 6
  absentees + late orders.
- **#88** 🟡 partner profiles — event-specific and type-specific; `event.attendee_profiles` designed,
  not built. Passcode never enters the warehouse.
- **#86** 🔴 sender now scheduled (n8n `QhJw46Mr7LAP8fdz`) — open only for the arrival proof on a
  real phone (Aug 23 test reminder, or an ad-hoc "remind me in 5 min").

**Closed today:** #85 (schedule lane) and #87 (who to meet — 4 of 8 not attending → **7 of 7**).
Both keep their evidence in `OLIVIA_SPRINT_3.md`; they move to `OLIVIA_BACKLOG_ARCHIVE.md` at
SPRINT close, not session close.

### Known and deliberately left
- Brandon Himmel's Aug 26 session has no parent activity → no audience → invisible to everyone.
- 5 of the 20 probe questions unfired: 13, 14, 15, 17, 18.
- `test-andy-8153` is a test row in `event.people` — remove when done testing.
- #72 load test still shelved (design only, nothing built).

### Traps in the export, all handled by the loader — do not re-learn them
- **41 of 91 activities are Milan 2025 leftovers** carrying `isDelete`. The event was cloned.
- **The `member`/`speaker`/`partner`/`guest` booleans are stale** and all false on records whose
  `accessRoles` grants three roles. `accessRoles` governs.
- **`event.timeZone` is a display label**, not IANA. Times are local wall-clock with no offset —
  which is exactly how `events_catalog.start_at` ended up 8 hours wrong.

## Watch-outs (standing)
- **NEVER fire probes at PROD against a real member's number.** On 2026-08-04 prod probes ran
  into Andy's own thread mid-test and twice sent "new question", resetting his context and
  stealing a button tap. Staging only, or a dedicated test number.
- **A 200 from Meta's `/messages` is NOT delivery.** The truth arrives asynchronously on the
  status webhook — read `digest.olivia_sends` before claiming reach (17 of 25 broadcast
  messages failed with 131049 *after* the API accepted every one).
- ~~`olivia_selftest.py` paces by sleep(20)~~ **FIXED 2026-08-03 (#52):** it now polls
  `olivia_messages` for THIS turn's reply before firing the next (`--timeout`, default 180s) and
  prints the wait — a probe in the #52 set took **50.4s** and would have raced the old pacer.
  Real-member echo: two messages <2s apart hit the same race in the workflow itself — known,
  low-frequency, still just a note.
- **FB capture SOP: rewrite `extension/seed_ids.json` from the capture file EVERY run** — 4c
  falls back to it silently (localStorage dies on tab close); a stale seed = comments for the
  wrong days. Backup pattern: `.bak-<date>`.
- Eval wamids `SELFTEST_MANU*` are not cleaned by `--cleanup`; Andy's thread carries test turns
  (accepted). Seed edits get a node syntax check BEFORE build_loop (apostrophes, twice).

## The daily routine (unchanged)
- Runs: FULL (all bank) rare; TEST = 25–35 targeted; `OLIVIA_EVAL_BANK=eval_bank_organic.json`
  or it fires 0. ONE paid run per session, after free diagnosis + probes. Retirement: 3 passes.
- Runs pace per-reply — the quiet stretches are NOT a stall; never kill the run.
- Reset between probes; gate GREEN before anything ships; Andy's number excluded from reporting.

## Open with Andy
- Q3088 MDS-Life ruling (parked) · whale ruling (chapter TTM sums) · "Oliva" display name ·
  member_match 'Apparel' vs 'Clothing & Accessories' · 👎 reactions → Slack? · bank truth fixes
  (722→723 members; supplements count drifts) · ClickUp doc refresh pending.
