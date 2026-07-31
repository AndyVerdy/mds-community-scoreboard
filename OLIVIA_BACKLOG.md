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

### 30. 🟡 Member resolution by at_member_id everywhere — phone is a channel, not the key · S2 · effort M
*As a member who is not on WhatsApp, the app still fully works for me — my identity is my
membership, not my phone number.*

**Not #31.** #31 (closed) keeps the wrong people OUT — status decides whether an identified person
is entitled. #30 lets the right people IN — the system must be able to IDENTIFY a member who has
no phone at all. Entitlement was fixed; identity is still phone-shaped.

**The walk-through:** every gated function answers "who is asking?" by looking up a phone — a
relic of Olivia being born on WhatsApp. A real case: an active member with no phone on record
(10 events attended, FB activity, a persona since #28) installs the app and logs in with his
email. The app door resolves email → member record fine — but to fetch his feed it calls the
gated functions, and each demands a phone as the asker key. He has none → `feed_available: false`
→ a paying member gets an empty app. Measured 2026-07-30: 203 of 748 actives (moves daily with
the sync; the class, not the number, is the point) — and every future member who installs the app
before ever touching WhatsApp joins the class.

**Accept when**
- The gated layer accepts `at_member_id` as the asker key — phone stays as a resolution PATH into
  the same shared lookup (WhatsApp unchanged), verified email is the other (the app). **#31's
  status gate applies identically on both paths.**
- A phone-less ACTIVE member gets a real feed from the app door, verified live.
- When that member later joins WhatsApp, the WA-dependent sections (chats, digests, Olivia
  history) light up with zero migration — entitlement semantics unchanged; chats-based
  entitlements are simply empty for members in no chats.
- Leak gate extended for the new path — unknown/ambiguous/canceled `at_member_id` → empty,
  fail-closed — and GREEN.
- Phone-path actives byte-identical (the standing regression snapshot).

**Impact:** ~200 active members today; every future app-first member.

### 23. 🟡 Answer latency · S2 · effort M
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


### 25. 🟡 The portal tells the truth · S2 · effort M
*As the team, every number on the Olivia portal (digest.mds.co/admin/olivia) is right: all the data
is there, it is displayed correctly, and the filters actually filter.*

**Reported by Andy 2026-07-30 with screenshots — the page is wrong today.** What the screenshots
already show, before any diagnosis:
- **Cards disagree on the window.** The page filter says "Last 30 days" and the tiles say 250
  questions / 20 members — while the Top-question-topics card renders its own stale span,
  "Jun 20 – Jul 20 · 26 questions". At least one card ignores the selected filter (the topics table
  only refreshes when the weekly report script runs — a card fed by a stale table reads as a broken
  filter).
- **Numbers unproven against the warehouse.** Top members claims Franky Farina 85 / Eugene 69
  questions in-period; none of the tiles has been reproduced by SQL.
- **A known pollution source is already on file** (status corrections below, 2026-07-28): the eval
  harness marks only the member's message as a test, never Olivia's reply — anything counting her
  replies reports eval traffic as production (367 of 636 recent rows at the time it was measured).

**Accept when**
- **Every tile and card reproduces from a warehouse query**, checked number by number on a fixed
  day: questions asked, members using, requests created/open, top members, question topics.
- **The page filter applies to every card.** Switching the window changes all of them consistently;
  0 cards on a private window.
- **Test traffic is excluded by default on every card the same way** — Andy's number, SELFTEST
  wamids, eval replies — and "Include my tests" brings it back deliberately.
- **Proven live after the fix**, the SQL cited beside what the page shows.

Lives in mds-digest-web (the read layer), not the workflow. Closing the eval-marking gap (mark her
replies too) is the same one-cheap-fix named in the status corrections — it also closes the
cross-source measurement trap noted for #8.

**Impact:** the team's only window into whether Olivia is used and useful; wrong numbers here mean
wrong calls on everything else.

### 5. 🟡 Counting · S2 · effort M
*As a member, when I ask a number I get a number.*

**Accept when**
- **A count that exists is never refused: 0%** "I don't have that data" where the number is derivable.
- **Every number matches the warehouse** it was derived from.
- **Totalling or extending the previous answer works** without the member asking twice.
- **0% of aggregate answers identify anyone.**
- **A count that genuinely does not exist is said plainly** — an honest miss, not a failure.

She lists but cannot count, and often says "I don't have that data" when she does. Live: SoCal vs Texas
totals, members under $1m, chapters with counts, most-active members.

- Counts by city, state, chapter, category and revenue bracket return a real number
- "Total it up" across a previous answer works
- Aggregate counts never identify anyone
- Where a count genuinely doesn't exist, she says so rather than implying she has nothing

**Effort M** — counting RPC plus a router lane; unknown is which counts may be shared. **Impact:** hit repeatedly by two of six testers within an hour.

### 6. 🟡 Chapters, end to end · S2 · effort M
*As a member, I can ask anything about chapters and get a real answer.*

**Accept when**
- **Your rulings land first:** the canonical count, and whether a lead's name — or email — is shareable.
  Nothing below is measurable until then.
- **One number everywhere.** Chapter counts agree with the canonical source in every answer that shows them.
- **Membership questions answer correctly for members with a chapter and for members without one.**
- **The policy questions have a written source and answers cite it: 0% inferred from chat chatter.**
- **The chapter list contains only real chapters.**

Verified: **member counts are already live** (all 20 chapters with counts), **chapter leads exist in
Airtable but are not exposed** (New York → Mari, Morris, Brandon), **"am I in a chapter" is answerable
but only 14% of members have one on record**, and the four policy questions — change chapters, join
several, live in two places, how do I change — have **no source anywhere**.

- How many members in each chapter, and who leads it
- Am I in a chapter; can I be in several (120 members already are)
- The policy answers get written down once and become answerable
- **Andy picks the canonical count first:** Airtable rollup says New York 94, live logic 97, raw field 116
- **Andy rules on chapter leads:** is a lead's name shareable, their email ever
- Needs a chapter whitelist — the raw field yields 36 "chapters" including Shopify, Amazon and Sponsor

**Impact:** 804 members have a chapter; the policy questions apply to all 722.

### 7. 🟡 People search that understands meaning · S2 · effort M
*As a member, I find the right person even when I don't know the exact word or spelling.*

**Accept when**
- **A misspelled or partial name resolves first try**, at or above the current target rung.
- **Meaning-based searches reach the right people** without a hand-maintained synonym list.
- **Ranking stays by engagement score and the score is never shown.**
- **Retrieval is compared with and without the semantic layer before it is trusted** — a silent no-op
  is not an improvement.

"Who's good at paid ads" cannot reach the PPC people. Prudence Tweedie-Millsap took four spellings.
There is no fuzzy matching installed at all — no `pg_trgm`, no member embeddings; only exact word
matching plus a hand-written synonym list.

- A misspelled or partial name resolves first try
- Synonyms work without anyone maintaining a list
- Member profiles embedded, same approach already used for content
- Still ranked by engagement score, never shown

**Effort M** — new extension plus an embedding pass over ~5,700 profiles; changes ranking behaviour. **Impact:** every "who knows X" and "tell me about Y" — the most common ask after digests.

### 8. 🟡 Every source on every question · S2 · effort M
*As a member, one question gets checked against every source that could answer it.*

**Accept when**
- **0% "I can't find that" where another source held the answer.**
- **Which sources answered is recorded per turn**, so coverage is a measured number rather than an estimate.
- **Fan-out is reached from ordinary member phrasing**, measured across the class — not from a fixed
  list of wordings.

Verified: Facebook + WhatsApp together is already the norm, but the true fan-out — partners, events,
members, videos — runs on roughly **1 answer in 12**. The fan-out function has **no Facebook section and
no videos section at all**, and its lanes sit low in the routing order, so "which member has…" is
answered from profiles alone and never fans out.

- Facebook and the video library join the fan-out
- The fan-out lanes are reachable from real phrasings, not four hard-coded ones
- Which sources answered each turn is recorded, so this stops being an estimate
- A member never gets "I can't find that" when another source had it

**Effort M** — extends an existing function, but touches routing order, shared with every lane. **Impact:** all members; it's the difference between a search box and something that knows MDS.

### 9. 🟡 Revenue brackets, one rule · S2 · effort L
*As a member, revenue answers are consistent and never expose anyone's actual number.*

**Accept when**
- **Your working session lands first:** one field named authoritative, in writing, with the reason.
- **A member's bracket is identical everywhere it appears** — card, match, count.
- **Raw revenue cannot leave the database**, enforced by the gate rather than by wording.
- **Channel questions answer consistently across phrasings.**

Most-recent revenue can never be exposed; brackets can. Either derive the bracket from most-recent
revenue or use the bracket field where it fits. Three competing tier fields exist, none confirmed. Same
audit is owed on **revenue sources** — Amazon, DTC, TikTok — which the application form already calculates.

- One field named authoritative, in writing, with the reason
- Bracket derived by a single rule everywhere: cards, matching, counting
- Raw revenue cannot leave the database — gate check
- "Who sells on TikTok" / "who's DTC" answer consistently from application data
- **Needs a working session with Andy before building**

**Impact:** every profile card, every match, every "who does X" answer.

---

---

# 🔵 S3

### 10. 🔵 Shareable member facts · S3 · effort S
*As a member, similar questions get similar answers.*

**Accept when**
- **One written list of shareable fields exists, and the gate blocks everything off it.**
- **The same field asked about different members is answered or refused identically: 0% inconsistency.**

Job title, years in business, business model, country, product categories, SKU and brand counts. Today
she refuses unevenly — "who sells on TikTok" works one way and is refused another.

- One approved list of shareable fields, applied everywhere
- Gate blocks everything off the list
- The sales-channel inconsistency resolved

**Impact:** every profile and matching answer.

### 11. 🔵 Payment wording · S3 · effort S
*As a member behind on payment, I'm told clearly and reminded kindly — not shown a system word.*

**Accept when**
- **0% of replies carry a raw system status or an internal one.**
- **Every status has approved wording**, and a member behind on payment is told plainly what to do.

Stripe's raw statuses reach members verbatim: `trialing`, `past_due`, `unpaid`, `canceled`. "Staff" has
also leaked as a membership status.

- `past_due` and `unpaid`: state it plainly, say what to do, keep the tone light
- Every status has approved wording; no raw system words reach anyone
- Internal statuses like Staff never surface

**Impact:** small but sensitive; 9 active members already carry broken Stripe records.

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

### 13. 🔵 Outage alarm · S3 · effort M
*As the team, we hear about an outage in minutes, from a system that isn't the one that's broken.*

**Accept when**
- **A real failure alerts within minutes**, from a system that is not the one being watched.
- **The alarm cannot latch** — repeated failures keep alerting.
- **A balance running low warns before members feel it**, and a spend cap exists.
- **Proven by forcing a failure**, never by reading configuration.

**Verified broken** — see status section. This is why Andy has never seen Olivia down.

- An alert fires the first time a member gets the failure text
- A warning before the AI account balance runs out; Olivia's own account, not a shared one
- The monitor doesn't run on the platform it watches, and cannot latch itself off
- A spend cap so one heavy user can't drain the budget

**Impact:** on 07-26 every member asking anything got a failure message and nobody knew. *(Recommend raising to S2 — same job as #16.)*

### 29. 🔵 Matchmaking & recommendations, built like the platforms build them · S3 · effort L
*As a member, MDS recommends people, deals, events and content the way Amazon or a streaming
platform would — from everything it knows about me, and it gets the like-minded question right:
"people like Mo" returns the other multi-market logistics-givers, not everyone in Canada.
(Andy 2026-07-30: "matchmaking will be the key… we have tons of info we can use for matching…
you need to research how such DBs are built.")*

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

### 14. 🔵 Conversational, not robotic · S3 · effort L
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

---

# ✅ Completed

### 31. ✅ Canceled means gone — membership status gates every door · CLOSED 2026-07-30 · effort M
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

### 3. ✅ "Restricted", never "doesn't exist" · CLOSED 2026-07-30 · effort S
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

### 28. ✅ The persona learns · CLOSED 2026-07-30 (Andy's call; quality redesign → #29) · effort M
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

### 27. ✅ The app knows who I am — identity-keyed personalization · CLOSED 2026-07-30 · effort M
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

### 26. ✅ Partners + events semantically searchable · CLOSED 2026-07-30 · effort S
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

### 1. ✅ Every answer matches the evidence · CLOSED 2026-07-30 at the 10% rung · effort M
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

### 21. ✅ The answering loop · CLOSED 2026-07-30 · effort L
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

### 2. ✅ Deliver what she offers · DONE 2026-07-28 · effort S
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

### 22. ✅ Kimi trial · CLOSED 2026-07-29 · effort M
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

### 24. ✅ First contact answers the question · DONE 2026-07-30 (staging) · effort S
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

### 4. ✅ Safe edits and rollback · DONE 2026-07-28 · effort M
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
3. **Canonical chapter count** — Airtable rollup, current-members logic, or raw field? They differ by 22 on New York. (#3 Chapters, end to end)
4. **Chapter leads** — is a lead's name shareable? Their email? (#3 Chapters, end to end)
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

