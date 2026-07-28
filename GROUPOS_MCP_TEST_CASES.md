> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS MCP — Admin Test Scenarios (full catalog)

**Purpose:** realistic requests admins will send through the MCP, for the dev team to build against. Each: admin request → tool path → verdict. Verdicts grounded in the 2026-06-08→11 QA session (all 66 tools exercised; UI cross-checked). ✅ supported · ⚠️ partial/workaround/unreliable · ❌ not possible (→ ticket in `GROUPOS_MCP_DEV_HANDOFF.md`).

**Score: 78 scenarios — 27 ✅ · 20 ⚠️ · 30 ❌ · 1 ⏸ not-run.** Pattern: transactional + catalog + aggregate asks pass; anything needing *who/when* fails (GOS-1 activity layer, GOS-3 form responses, GOS-18 user-id lookup, GOS-19 check-ins, GOS-20 approvals). ⏸ = test defined but not executable this session (repro left for dev).

---

## 1. Profiles / Members (PRO)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| PRO-1 | "Pull up [member]'s profile — email, tier, member type, join date." | `members_list(q)` → `members_get` | ✅ tested (Ian, Danson) |
| PRO-2 | "Who joined in the last 30 days? I want to run onboarding outreach." | `members_list(joined_after, sort joined_at)` | ✅ |
| PRO-3 | "Is [member] still active? When were they last in the app?" | `members_get.last_seen_at` | ⚠️ field present + sortable but **values wrong** (Ian: Nov '24 vs UI Jan '25, predates join) → GOS-2 |
| PRO-4 | "List all members on the [tier] plan." | `subscriptions_list(tier_id)` → user_ids | ✅ via subscriptions (members_list itself has no tier filter) |
| PRO-5 | "Get [member]'s full contact card — phone, address, socials." | `members_get.custom_fields` | ⚠️ fields exist but mostly empty; **address not exposed at all** (UI has it) |
| PRO-6 | "This order was bought by user `6494e341…` — who is that? Name and email." | `members_get(user_id)` → **not_found**; `members_list` has **no user_id filter** | ❌ **NEW DEFECT GOS-18** — no user_id→member resolution; reverse lookup requires paginating all 3,443 members client-side |

## 2. News module (NEW)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| NEW-1 | "What news is currently published?" | `news_list(status)` | ✅ (353 items) |
| NEW-2 | "Pull the [article] body — I want to reuse the copy." | `news_get` | ✅ (raw HTML) |
| NEW-3 | "Which banners are live in the carousel / sidebar right now?" | `news_list(kind, slot)` | ✅ |
| NEW-4 | "How did the [article] perform — views/reads?" | — | ❌ **news items carry NO engagement counters at all** (verified: no view/read/click fields) — worse than videos/docs which at least have aggregates |
| NEW-5 | "Who read the [announcement article]?" | — | ❌ GOS-1 |
| NEW-6 | "What news went out this month?" | `news_list(created_after)` | ✅ |

## 3. Partners module (PAR)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| PAR-1 | "Show the partner directory — names, offers, categories." | `partners_list` | ✅ (592) |
| PAR-2 | "Pull [partner]'s profile and current offer." | `partners_list(q)` / `partners_get` | ✅ (note: MCP `q` handles full names better than the admin UI search) |
| PAR-3 | "Which partners are featured / fresh deals right now?" | `partners_list(featured / fresh_deal)` | ✅ |
| PAR-4 | "Conversion check for [partner]: views vs claims." | `partners_get` counters | ⚠️ counts only (Riverbend 252 views − 119 claims = 133 gap); lifetime, no trend |
| PAR-5 | "Who claimed [partner]'s offer (and when)?" | — | ❌ no claims list/timestamps → GOS-1 |
| PAR-6 | "[Partner] got low ratings — show the 1–2★ reviews and who left them." | — | ❌ no reviews endpoint; aggregate `review_count` also broken (0 vs UI 32) → GOS-6 |

## 4. Documents module (DOC)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| DOC-1 | "Find the [Ojai Summit] decks." | `documents_list(q)` | ✅ (q covers fileName/description/ownerName) |
| DOC-2 | "Top documents by views/downloads this quarter." | `documents_list` | ⚠️ counters accurate but **no sort-by-engagement** (client-side over 589) and lifetime-only |
| DOC-3 | "Who viewed / who downloaded [document]?" | `documents_get` | ❌ aggregate counts only; `owner` = uploader → GOS-1 |
| DOC-4 | "What's sitting in Draft/Unlisted awaiting approval?" | `documents_list(status)` | ✅ (default is Public — remember to override) |
| DOC-5 | "All documents attached to [event] / in [category]." | `documents_list(category_id)`; event via `access.event_ids` | ⚠️ category filter ✅; **no event_id filter** (field exists per-record only) |

## 5. Events module (EVT)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| EVT-1 | "What's on the calendar next month?" | `events_list(from, to, status)` | ✅ (675 events) |
| EVT-2 | "Sales snapshot for [event]: revenue, tickets by tier, dates." | `events_get` + `ticket_types_list` + `orders_list(event_id)` | ✅ ($5,935 / 20-43 / per-tier — matches UI). Use `orders_list`, **not** `invoices_list` (manual-only) |
| EVT-3 | "Did [member] register for [event]?" | `members_list(q)` → `orders_list(user_id, event_id)` | ✅ (name-first direction works) |
| EVT-4 | "Give me the attendee roster with names/emails and what each bought." | `orders_list(event_id)` → buyer user_ids → ??? | ⚠️ purchases ✅ but **names/emails blocked by GOS-18** (no user_id→member lookup) |
| EVT-5 | "Refund history for [event] — who got money back?" | `refunds_list(event_id)` | ✅ (full Stripe refund/charge detail incl. user_id… same GOS-18 caveat for names) |
| EVT-6 | "How many dinner add-ons sold?" | `ticket_addons_get` / `orders` line items | ⚠️ `quantity_sold` stuck at 0 (GOS-7); workaround = count addon line items in orders |
| EVT-7 | "How many people viewed the [event] page — conversion to purchase?" | — | ❌ UI dashboard shows 261 views / 77 unique; **MCP event object has no page-view fields** |

## 6. Video module (VID)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| VID-1 | "List the [category] video library / what was uploaded this month." | `videos_list(category_id, created_after)` | ✅ (973) |
| VID-2 | "Stats for [video]: views, likes, comments." | `videos_get` | ✅ (view/like/dislike/comment counts — UI-accurate) |
| VID-3 | "Top 10 videos by views." | `videos_list` | ⚠️ no sort-by-views (only created_at) — paginate 973 + sort client-side |
| VID-4 | "Who watched [video]? Watch time? Completion?" | — | ❌ GOS-1 (no per-member watch data, no durations) |
| VID-5 | "What are the comments on [video]?" | — | ❌ no video-comments endpoint (`comments_list` is post-scoped only) |
| VID-6 | "All session recordings from [event]." | `videos.event_ids` field | ⚠️ field exists per-record; **no event_id filter** on videos_list |

## 7. Notifications module (NOT)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| NOT-1 | "What announcements went out this week?" | `announcements_list(created_after)` | ✅ (224 total) |
| NOT-2 | "Performance of the [push]: sent, clicks, CTR." | `announcements_get` | ✅ (57 / 5 / 8.77% — matches UI) |
| NOT-3 | "Our best-performing announcements ever." | `announcements_list(sort read_count:desc)` | ✅ (server-side sort exists) |
| NOT-4 | "What's in the draft/scheduled queue?" | `announcements_list(status)` | ✅ |
| NOT-5 | "Click list for retargeting — who clicked the [push]?" | — | ❌ aggregates only → GOS-1 |
| NOT-6 | "Did [member] receive/read the renewal reminder?" | — | ❌ per-recipient state not exposed (`my_notifications` = self only) |

## 8. Forms (FRM)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| FRM-1 | "What registration forms exist (for [event])?" | `application_forms_list` | ✅ |
| FRM-2 | "What questions are on the [form]?" | `application_forms_get` | ✅ (full field definitions, choices, required flags) |
| FRM-3 | "Audit: which forms ask about dietary restrictions?" | list + client-side field-label scan | ✅ (did exactly this) |
| FRM-4 | "How many submissions did [form] get?" | — | ❌ not even a count |
| FRM-5 | "Export all responses for [form]." | — | ❌ **no responses endpoint** → GOS-3 |
| FRM-6 | "Who answered 'dietary restrictions' with gluten-free?" | — | ❌ GOS-3 (the catering case — UI export is the only path) |

## 9. Members Map (MAP) — module has ZERO MCP surface

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| MAP-1 | "How many members are on the map?" | — | ❌ no endpoint (UI: 551) |
| MAP-2 | "Members near [city] — planning a local meetup." | — | ❌ no geo/address on member records |
| MAP-3 | "Who hasn't set their location? (840 members, 551 placed)" | — | ❌ |
| MAP-4 | "Is the map being used — opens/usage?" | — | ❌ |
| MAP-5 | "What's [member]'s city?" | — | ❌ UI profile has it; MCP omits it |

## 10. Cross-module chains (X)

| ID | Admin request | Chain | Verdict |
|---|---|---|---|
| **X-1** | **"Check [event]'s attendee list for attendee-type Partner, find that partner in the Partners module, then: how many claimed their offer after the event, and how many opened the partner page but didn't claim?"** *(Andy's scenario — live-tested)* | ① `orders_list(event_id)` → ② attendee type → ③ `partners_get` claims-after-date → ④ viewers-minus-claimers | ❌ **breaks at 3 of 4 steps.** ① roster of user_ids ✅ → ② ❌ no attendee-type/member↔partner linkage anywhere (member_type is only M/CO/CU/GU; partner records have no member/user ref; ticket types carry no "Partner" class) + GOS-18 blocks even resolving who the buyers are → ③ ❌ `claim_count` is a lifetime scalar, no timestamps, so "after the event" is inexpressible → ④ ❌ identities unavailable; only the count gap (252−119=133 for Riverbend). **Needs: GOS-1 (activity stream w/ timestamps), GOS-18 (user lookup), member↔partner link field.** |
| X-2 | "Prep me for [member]'s renewal call: profile, subscription status, events bought, refunds, posts." | `members_list(q)` → `subscriptions_list(user_id)` + `orders_list(user_id)` + `refunds_list(user_id)` + `posts_list(author_user_id)` | ✅ **live-tested on Danson** — profile + 2 subscriptions (free_trial, Stripe ids, period ends) + 6 orders + refunds. The flagship *working* chain (name-first only) |
| X-3 | "Event debrief: revenue + roster + which attendees were first-timers (joined <90d)." | `orders_list(event)` + member join dates | ⚠️ revenue ✅; roster→names and joined_at blocked by GOS-18 |
| X-4 | "We pushed [announcement] promoting [video] — did it move views?" | `announcements_get.read_count` + `videos_get.view_count` | ⚠️ aggregate-to-aggregate only; lifetime views = no before/after comparison |
| X-5 | "Partner ROI report for [partner]: profile, funnel, reviews, revenue influence." | `partners_get` + reviews + claims | ⚠️ profile + view/claim counts ✅; reviews ❌ (GOS-6), claim identities/timing ❌ (GOS-1) |
| X-6 | "Catering ops pack for [event]: roster + dinner add-ons + everyone's dietary answers." | orders + addons + forms | ⚠️ roster/add-ons ✅ (GOS-7/18 caveats); dietary ❌ (GOS-3) |
| X-7 | "Renewal-risk sweep: whose subscription ends this month, and were they active recently?" | `subscriptions_list` + activity | ⚠️ period-end is on the record (epoch int; no server filter — client-side over 3,078) ✅-ish; "active recently" ❌ (GOS-1/2) |

---

## 11. Member Scorecard (SCORE) — points rubric + decay
**Context:** MDS is building a member engagement scorecard fed by app data. Rubric: every activity earns points; **points decay** (suggested: ×0.5 per 90 days, or tiers 100% <30d · 50% 30–90d · 20% 90–180d · 0 after) so only currently-active members rank. **Decay requires a timestamp on every activity** — aggregate lifetime counters can never feed it.

### The rubric — and whether the MCP can feed each line today
| Activity (points, tune freely) | Data source | Feedable? |
|---|---|---|
| Register — in-person event (+20) | `orders_list` + `events.kind=in_person`, `created_at` | ✅ |
| Register — virtual event (+10) | same, `kind=virtual` | ✅ |
| Buy an add-on, e.g. dinner (+5) | `orders` line items (`item_type:TA`) | ✅ |
| **Attend / check in** (+30) | — | ❌ **GOS-19** — no check-in data anywhere |
| **Speak on a video** (+40) | `videos.speaker_ids` | ⚠️ **verified: populated on SOME videos** (Kim Cruickshank Mogul Call has a speaker_id; Brockie/Hadley speaker videos are empty) → feasible but data-entry-inconsistent + no speaker filter (client-scan 973) |
| Submit a document (+15) | `documents.owner_id` + `date_uploaded` | ✅ |
| Create a post (+5) | `posts_list(author_user_id)` + `created_at` | ✅ (feed near-empty in MDS today) |
| Comment (+3) | — | ❌ comments broken/post-scoped (GOS-5) |
| **Watch a video** (+2/video) | — | ❌ GOS-1 |
| Like a video (+1) | — | ❌ GOS-1 |
| Claim a partner offer (+5) | — | ❌ GOS-1 (count exists, who/when don't) |
| Leave a partner review (+8) | — | ❌ GOS-6 (no reviews endpoint) |
| Submit a form response (+5) | — | ❌ GOS-3 |
| App login / session (+1/day) | — | ❌ no sessions; `last_seen_at` broken (GOS-2) |
| Active subscription / renewal (+10/period) | `subscriptions_list` (status, period) | ✅ |
| Set Members-Map location (+5) | — | ❌ no geo exposure |

**Coverage: 6 of 16 rubric lines (~37%) feedable today** — and the three highest-signal lines (attend, watch, speak) are blocked or partial. The feedable core: **orders + documents + posts + subscriptions**, all timestamped → decay works for them.

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| SCORE-1 | "Compute [member]'s engagement score: event registrations + add-ons + documents submitted + posts." | `orders_list(user_id)` + `events_get(kind)` + docs by owner + `posts_list(author)` | ⚠️ **ran end-to-end live on Danson Hui (2026-06-11):** 6 orders ✅ + 0 posts ✅ + 0 documents ✅ + 2 subscriptions ✅ — score computable from real data for the transactional signals; consumption signals remain invisible |
| SCORE-2 | "Apply decay — full points <30d, half to 90d, fade to zero by 180d." | timestamps on orders/docs/posts/subs | ⚠️ ✅ for the feedable 6 lines (all timestamped); ❌ impossible for counter-based signals (no timestamps ever) |
| SCORE-3 | "Award +40 speaker points for anyone who spoke on a video this quarter." | `videos.speaker_ids` + `created_at` | ⚠️ field exists; empty in tested records, no filter — needs MDS to populate speakers + ideally a speaker_id filter |
| SCORE-4 | "Award watch points — 2 pts per video watched, capped 10/month." | — | ❌ GOS-1 |
| SCORE-5 | "Build the daily leaderboard: decayed score for ALL members, top 50." | community-wide `orders_list` (**verified: 1,878 orders, paginated**) + all docs (589) + posts + subs (3,078); aggregate client-side by user_id | ⚠️ feasible as a batch pipeline (~60+ paged calls); **names require full member dump** (GOS-18); consumption absent |
| SCORE-6 | "Flag stale members — zero activity in 60 days — for retention outreach." | — | ❌ only *transactional* inactivity is provable; a member who watches 50 videos but buys nothing looks identical to a ghost (GOS-1) |
| SCORE-7 | "Backfill 12 months of history into the scorecard." | orders/docs/posts/subs `created_at` | ⚠️ ✅ for the 6 feedable lines; ❌ for everything counter-based (lifetime totals can't be back-dated) |

## 12. Event check-ins (CHK)

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| CHK-1 | "Who registered for [event]?" | `orders_list(event_id)` | ✅ (user_ids + tickets; names blocked by GOS-18) |
| CHK-2 | "Who actually **checked in** at the door?" | — | ❌ **GOS-19 — PROVEN on populated data:** MDS Inspire 2026 Check-ins page = **"Checked in 313 of 376"**, per-person rows (name, email, attendee type, 1-of-1). Same event via MCP = `attendee_count:449` + **1 junk order (`status:"unknown"`)** + 0 ticket types. 313 real check-ins, zero reachable. Also exposed **GOS-21**: manually-added attendees aren't orders → whole roster (436 in UI) invisible; three conflicting counts (436/376/449) |
| CHK-3 | "No-show rate for [event] — registered vs checked in." | — | ❌ blocked by CHK-2 |
| CHK-4 | "Did [member] actually attend [event] (not just register)?" | — | ❌ — also the single most valuable missing scorecard signal (attendance ≠ registration) |

## 13. Ticket approvals / intent collection (APR)
**Context (real MDS workflow):** admin creates an event with one approval-required ticket and **never approves anyone** — the pending queue is used to *collect intent*; the admin reviews applicants + their form answers later and decides.

| ID | Admin request | Resolves to | Verdict |
|---|---|---|---|
| APR-1 | "List the pending approval requests for [event]'s ticket." | — | ❌ **GOS-20** — no approvals endpoint among the 66 tools; `orders_list` has **no status filter** (only succeeded orders observed). **UI-verified (2026-06-11): there are TWO approval surfaces** — Members→"Approval request" = **subscription/tier approvals** ("All subscription submissions": name, Tier, **Form name**, Status, Pending filter — 0 pending in staging) and per-ticket event approvals (`requires_approval` flag; no event in the sample uses it). **Neither surface is exposed via MCP** |
| APR-2 | "Pull everyone in the intent queue for [event] so we can decide later." | — | ❌ same gap — the entire intent-collection workflow is invisible to the MCP |
| APR-3 | "For each applicant, show their registration form answers so we can judge fit." | — | ❌ double-blocked: GOS-20 (no applicant list) + GOS-3 (no form responses) |
| APR-4 | "Which events/tickets have approval enabled?" | `ticket_types.requires_approval` | ⚠️ **flag verified LIVE** (Toronto Boardroom: 2 tickets `requires_approval:true` via MCP, matches UI badges) — but no global filter (iterate 675 events client-side), and **the ticket's linked form is NOT exposed** (UI shows "Linked form"; MCP payload has no form reference) |
| APR-5 | "Did we approve or reject [member]'s request for [event]?" | — | ❌ no approval state exposed (`invoices` draft/committed/rejected is the manual-invoice flow, not ticket approvals) |
| APR-6 | "How many pending approval requests does [event] have? (expect: zero)" | — | ❌ **the zero itself is unaskable** — verified on the live approval-configured event: no endpoint returns `{items:[], total:0}` for approvals; `orders_list` (4 succeeded, non-approval tier only) has no status filter. Empty state and missing capability are indistinguishable to the consumer |
| APR-7 | "A member just requested approval for [event]'s ticket — show me the new pending request." | — | ⏸ **NOT RUN** — required submitting a live test request; not possible this session. Open question: does a pending request surface as an order with some status (cf. the `"unknown"` ghost row on Inspire), or not at all? **Dev repro:** submit one request to Toronto Boardroom "General Admission" (`6a26fa3da645c561db6441cc`), then call `orders_list(event_id)` and diff. Prediction: invisible |

---

## What this catalog tells the dev team
1. **The working core** is transactional: members(by name) + subscriptions + orders + refunds + tiers — X-2 proves a full member-360 join works today.
2. **GOS-18 (new):** `orders`/`refunds`/`subscriptions` reference `user_id`, but nothing resolves a `user_id` → member (members_get wants member_id; members_list has no user_id filter). Add `user_id` to `members_list` filters — small fix, unblocks EVT-4/5, X-1③, X-3.
3. **GOS-1 (activity stream)** flips ~14 ❌ scenarios at once: NEW-5, PAR-5, DOC-3, VID-4, NOT-5/6, MAP-4, X-1③④, X-4, X-5, X-7, PRO-3 (reliable last-active).
4. **GOS-3 (form responses)** flips FRM-4/5/6 + X-6 — the catering/ops pack.
5. **Small adds with big lift:** sort-by-engagement on videos/docs (VID-3, DOC-2) · event_id filters on videos/docs (VID-6, DOC-5) · event page-view counters (EVT-7) · news engagement counters (NEW-4) · member address/geo (PRO-5, MAP-*) · member↔partner link (X-1②).
6. **The Scorecard is the forcing function (§11):** MDS is building a member scorecard NOW — only **6 of 16 rubric lines (~37%)** are feedable, and the three highest-value signals (attend, watch, speak) are blocked. **GOS-19 (check-ins)** and **GOS-20 (approval queue)** are whole UI features with zero MCP surface; GOS-1 + GOS-19 + populated `speaker_ids` would take the rubric to ~90%.
7. **Verified pipeline primitive:** community-wide `orders_list` works (1,878 orders, paginated) — the batch aggregation path for the scorecard exists today for transactional signals.
