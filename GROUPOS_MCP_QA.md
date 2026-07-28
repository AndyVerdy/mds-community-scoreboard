> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS MCP — QA Report (UI ↔ MCP verification)

**Owner:** Andy (AI power-user QA) · **MCP:** in-house GroupOS MCP server · **Started:** 2026-06-08
**Method:** open each module in the **staging admin UI** → read the real values → run the matching **MCP** call → compare. Only **UI-verified** findings are marked confirmed. Staging data may be incomplete, so "empty/zero" is NOT assumed to be a bug until the UI confirms it.

> ⚠️ This doc is a living artifact. The dev team will append results as testing continues.
> **Status legend:** ✅ confirmed match · ❌ confirmed defect · ⚠️ semantic/gap (not necessarily a bug) · ❓ open question, needs definition · 🧩 code/schema-level (env-independent)

## Summary (first pass — 2026-06-08)
**Environment:** ✅ MCP and staging UI confirmed to read the **same database**.

| Module | Record-level data | Notable finding |
|---|---|---|
| Members | ✅ profile fields match | ❌ `last_seen_at` wrong (UI Jan 16 '25 vs MCP Nov 14 '24); gaps: `migrated`, address, trial-status not in MCP; ❓ count 840 vs 2097 |
| Videos | ✅ `view_count` matches (997, 845) | ❓ count 972 vs 973 (off-by-1) |
| Partners | ✅ views/claims match (TestParty 2/4) | ❌ **UI** search broken on full names (MCP search OK); ❓ count 594 vs 592 |
| Documents | ✅ views/downloads match (top 3) | ℹ️ MCP defaults to `status=Public` (589 vs 592) |
| Events | ✅ tickets 20/43 + per-tier match; ✅ `orders_list` = full $5,935 | ✅ `price_cents` now true cents (39500) — **FIXED**; ✅ `invoices_list` gap **RESOLVED** by `orders_list` |
| Notifications | ✅ sent/clicks match exactly | ⚠️ MCP `read_count` labeled "Clicks" in UI |

**Top priorities:** (1) ✅ **RESOLVED 2026-06-11** — `invoices_list` revenue gap fixed by new **`orders_list`** (use it, not invoices). (2) ✅ **RESOLVED 2026-06-11** — `price_cents` now true cents (39500). (3) 🔴 still open: `members.last_seen_at` is wrong; 🧩 webhooks-scope question (§8); ❌ **no per-member activity layer** (forms responses, partner claims/reviews, video/notification "who", sessions, maps) — see §10.
**Not bugs (verified):** most count gaps are filter/scope differences; staging "empty" states were load delays (waited + reconfirmed each).

---

## 0. Environment — VERIFIED same data source
The MCP and the staging UI read the **same database**:
- **Matt Demirel** (`info@lotsofdeals.org`), whom MCP reports as **joined today (2026-06-08)**, is present in the staging UI → not a stale clone.
- **Ulrich Kratz** (`ulrich@unybrands.com`, Standard App) matches exactly in both.
- Ian Sells' UI edit URL is `/admin/commu-members/edit/6494e3c0bae4b2c07d780259` = his MCP `user_id`.
- 🧩 **Caveat to verify with team:** MCP `communities_get.subdomain_url` = `https://mds.groupos.co` (the **prod** URL) even though the data is staging. Cosmetic/config mislabel — confirm the field is intentional.

---

## 1. Members module

### ✅/❌ Record-level — Ian Sells (member `6791ea053b8debd23a9b5bdb`, user `6494e3c0bae4b2c07d780259`)
| Field | Staging UI | MCP | Verdict |
|---|---|---|---|
| First / Last / Display | Ian / Sells / Ian Sells | same | ✅ |
| Preferred email | iansells@gmail.com | iansells@gmail.com | ✅ |
| Joined | Jan 31, 2025 | `2025-01-31` | ✅ |
| **Last seen** | **Jan 16, 2025** | **`2024-11-14`** | ❌ **DEFECT — disagree ~2 months; MCP value also predates Joined** |
| Migrated | Jan 23, 2025 | *(no field)* | ❌ **GAP — MCP exposes no `migrated` date** |
| Status | Trialing | `active` | ⚠️ MCP `status` = lifecycle (active/blocked/removed); UI "Trialing" = billing status, **not exposed by MCP** |
| Address | San Diego, CA, USA | *(no field)* | ❌ **GAP — MCP member record omits address/location** (note: Members Map feature relies on this) |
| Stripe customer | cus_RdK08D10INDLpy | (via subscription) | ✅ |
| Subscription | sub_1QkKT6HUXQT2RuDUYCX7CQoc | MCP `subscription_id` is internal ObjectId `6791ea31…`, **not** the Stripe `sub_…` id | ⚠️ different identifier than UI shows |

### ❓ Member COUNT — open, needs definition before judging
| Population | Count |
|---|---|
| Staging UI — "Members" tab | **840** |
| MCP — `member_type=M` + `status=active` | **2,097** |
| MCP — all member edges (no filter) | **3,443** |

These three measure different populations. The UI "Members" tab may = paid/active app members, while MCP `member_type=M` counts all active member edges. **Do NOT call a bug yet** — pending: map UI tabs (Lead Users / Guest / Invited / Deleted / Blocked) to MCP `member_type` (CU/GU/CO) and reconcile.

---

## 2. Videos module — ✅ mostly PASS
**Statistics page (lifetime):** 972 videos · 39,439 views · 340 likes · 6 dislikes · 37 comments · 10,293 unique views.

### ✅ Per-video `view_count` — matches UI exactly
| Video | UI "Views" | MCP `view_count` | Verdict |
|---|---|---|---|
| DTC Growth Strategies Using TikTok (Apr 2026) | 997 | 997 | ✅ |
| TikTok Cold Start — Alex Bonilla — Milan | 845 | 845 | ✅ |

- MCP `view_count` = the UI **"Views"** total column (not "Unique views" 10,293, not Mobile+Web sum). Integrity confirmed on 2 records.
- ❓ **Video count off-by-one:** UI stats header = **972**; MCP total (all + `status=published`) = **973**. Likely the one brand-new 0-view video ("Resellers Channel Call May 2026") not yet in the stats table — confirm it's just catalog-count vs stats-count, not a real drop.
- ℹ️ UI-internal quirk (not MCP): video #2 Mobile(0)+Web(841) = 841 ≠ "Views" 845. The 4-view gap is UI-side; MCP correctly matches the 845 total.
## 3. Partners module — ✅ data PASS · ❌ UI search bug
### ✅ Engagement fields — match UI exactly
| Partner | UI Views / Claims | MCP `page_view_count` / `claim_count` | Verdict |
|---|---|---|---|
| TestParty (test partner, created Jun 1 2026) | 2 / 4 | 2 / 4 | ✅ exact (also reconfirms same env) |
- Mapping confirmed: UI **Views** = `page_view_count`, **Claims** = `claim_count`, **Rating** = `rating_avg`, **Reviews** = `review_count`.
- FBA Private Market MCP = 152 views / 26 claims; row-level UI cross-check blocked by the search bug below, but field mapping already validated via TestParty.

### ❌ UI partner search is broken (this is a UI defect, not MCP)
- Typing the exact name **"FBA Private Market"** → dropdown shows **"No search results"**; selecting it filters to **"146 partners"** of unrelated records (loose full-text OR-match), never the actual partner.
- Typing **"FBA"** → dropdown correctly lists "FBA Private Market" + "MyFBAPrep".
- **MCP `q="FBA Private Market"` returned the partner correctly** → MCP search is more reliable than the UI search here.

### ❓ Partner count — off by 2
UI "All partners" = **594** vs MCP total = **592**. Likely 2 partners in a state MCP's default excludes — to confirm (not yet a bug).
## 4. Documents module — ✅ PASS
### ✅ Top 3 documents (date_uploaded desc) — match UI exactly
| Document (owner) | UI Views / Downloads | MCP `views_count` / `download_count` | Verdict |
|---|---|---|---|
| How I'm Preparing to Sell… (Matthew Greene) | 3 / 0 | 3 / 0 | ✅ |
| $40m brand: TikTok… (Michael Corrigan) | 2 / 0 | 2 / 0 | ✅ |
| $60M to $100M… (Jan Krapp) | 2 / 0 | 2 / 0 | ✅ |
- Order, owner names, and counts all match. UI **Views**=`views_count`, **Downloads**=`download_count`, **Likes**=`likes_count`, **Comments**=`comments_count`.
- ℹ️ Count: UI "All documents" = **592** vs MCP = **589**. Explained — `documents_list` **defaults to `status=Public`** (589 public); UI shows all statuses (592). 3 non-public docs = the gap. Not a bug, but worth documenting the default so integrators don't under-count.
## 5. Events module — ✅ ticket data PASS · ✅ revenue (orders_list) + price_cents both FIXED
**Event:** MDS AI Mastermind June 2026 (`69f4feeab4b637ab9f4bc8a6`). Dates Jun 11 2026 10:00 AM–09:00 PM, NYC — all match MCP. ✅

### ✅ Per-tier tickets — match MCP exactly
| Tier | UI Sold | UI Price | MCP `quantity_sold` | MCP `price_cents` | Verdict |
|---|---|---|---|---|---|
| Host | 2/2 | Free | 2/2 | 0 | ✅ |
| MDS Member | 11/15 | **$395.00** | 11/15 | **395** | ✅ sold matches; **price proves $ not ¢** |
| All Star Member | 1/10 | $95.00 | 1/10 | 95 | ✅ |
| Standard Plan | 5/15 | Free | 5/15 | 0 | ✅ |
| MDS Lite | 1/1 | $595.00 | 1/1 | 595 | ✅ |
- **Total tickets sold 20/43** matches MCP sum exactly.

### ✅ RESOLVED (2026-06-11) — `price_cents` was dollars, now true cents
Session 1 (pre-reconnect): `ticket_types.price_cents` = **395** ($395 as whole dollars — a 100× trap). **Re-checked 2026-06-11: now `39500`** (= $395.00, true cents), matching the order/invoice `amount_cents` (39500) and consistent with add-ons (`15000` = $150). Fixed alongside the `orders_list` ship.

### ❌ CONFIRMED — `invoices_list` is INCOMPLETE (under-reports revenue)
UI event dashboard: **Tickets sold 20** = "**Sold on Groupos: 16** · **manual: 4**"; **Net sales $5,935.00** ("including manual orders **$1,880.00**").
- MCP `invoices_list(event_id)` returned **only the 4 manual orders = $1,880** — the **16 Groupos-checkout sales ($4,055) are entirely absent.**
- An MCP consumer reading event revenue from `invoices_list` under-reports this event by **~68%** ($1,880 of $5,935). Looks like `invoices_list` only exposes the manual/admin-invoice collection, not self-serve checkout orders. **High priority** — needs a complete orders/sales endpoint or a documented caveat.
- _(This also resolves session-1's "20 sold but only 4 invoices" puzzle — it was never comped tickets; the MCP endpoint simply omits Groupos-checkout sales.)_

### ✅ RESOLVED (2026-06-11) — new `orders_list` / `orders_get` endpoints shipped
A new **`orders_list`** endpoint now returns the COMPLETE order set. AI Mastermind: **19 orders / 20 tickets** (one order qty 2), summed `ticket_value_cents + addon_amount_cents` = **$5,935.00** — matches the UI Net sales **exactly**. The 4 null-`stripe_payment_intent_id` orders with value>0 = the **$1,880 manual** subset that `invoices_list` returned. So:
- **Use `orders_list` (not `invoices_list`) for event revenue/attendees.** `invoices_list` = manual/admin invoices only.
- Each order carries `payment.{stripe_payment_intent_id, status, quantity, ticket_value_cents, addon_amount_cents, stripe_amount_cents}`.
- **Correction to a prior finding:** "Danson Hui hasn't purchased a ticket" (asserted earlier from `invoices_list`) was **WRONG**. Order `6a26db72a645c561db627f69` (user `6494e341…fd2c` = Danson) is a **$545 Stripe-paid** order (Member $395 + dinner $150), succeeded Jun 8. This is also the "order #6a26db72" that earlier returned `not_found` on `invoices_get` — `orders_get` resolves it now. **Lesson: the incomplete endpoint produced a real false-negative about a specific member.**

### ❓ Event count — scope difference
UI "All events" (Default view) = **21** (upcoming) vs MCP `events_list` total = **675** (all lifetime incl. past). Align filters before comparing; not a bug.
### ℹ️ Triple-check note
The dashboard first rendered "Total collected $0.00 / 0 sold" — that was a **load state**; after waiting it showed the correct $5,935 / 20. Correctly *not* reported as a bug.
## 6. Notifications module — ✅ PASS
- ✅ **Count:** UI **224** = MCP `announcements_list` **224**.
- ✅ Per-notification (created desc) match exactly:
| Notification | UI Sent / Clicks / Rate | MCP `recipient_count` / `read_count` | Verdict |
|---|---|---|---|
| SOS – Save Our Sellers (May 27) | 1 / — / — | 1 / 0 | ✅ |
| Complete Check In Form – MDS Inspire (Mar 8) | 57 / 5 / 8.77% | 57 / 5 | ✅ (5/57 = 8.77%) |
| Complete Check In Form (Mar 8) | 1 / 1 / 100% | 1 / 1 | ✅ |
- Mapping: UI **Sent** = `recipient_count`, UI **Clicks** = `read_count`. ⚠️ Naming: MCP calls it `read_count` but the UI labels it **"Clicks"** — values identical, but confirm whether the metric is *reads* or *clicks* (the label mismatch could mislead integrators).

## 7. Profile info — ✅ PASS
Ian Sells' profile editor (§1): First / Last / Display / Preferred email all match MCP. Only **address** (San Diego, CA, USA), **migrated** date, and **trial/billing status** are present in the UI but **absent from the MCP member record** (logged in §1).

---

## 8. 🧩 Code/schema-level findings (env-independent — evident from MCP responses, pending dev confirmation)
These don't need UI data; they're visible in the MCP output shape itself. Listed for the dev team; each still to be acknowledged/triaged.
- **`pricing.price_cents`** — was dollars (395 in session 1), ✅ **FIXED 2026-06-11** to true cents (39500). See §5/§11.
- **Webhooks scope** — `webhooks_list` + `webhook_deliveries_list` returned admin data (Make/Zapier URLs, delivery logs) although the PAT lists **no `webhooks:admin` scope** in `whoami`. Possible missing scope enforcement OR `whoami` under-reports. **Highest-priority item to confirm with the auth owner.**
- **`communities_get`** returns garbled encrypted `comet_chat.region`/`app_id` (`"Salted__…"`).
- **Inconsistent list envelopes** — `document_categories_list` / `document_content_types_list` return a bare array; every other list returns `{items,next_cursor,has_more,total}`.
- **Inconsistent timestamps** — `subscriptions` use epoch-seconds ints; rest of API uses ISO-8601 strings.
- **`collaborators_list`** — all rows return empty `user_id` / `user:null` (can't identify collaborators).
- **`pages_list` payload bloat** — each page returns `html_content` + full `json_content` AST + duplicated `blocks[]`; `limit=3` exceeds the response size cap (hard failure). _To revisit once Pages UI is checked._

## 9. ⚙️ Operational note (not an MCP bug)
`webhook_deliveries` shows a live `ticket.purchased.v1` delivery to subscription `6a0f5d5a…` failing **HTTP 404** (dead Make endpoint) — an event-registration sync is currently broken.

## 10. Per-member / engagement analytics — what's possible (running, 2026-06-11)
Recurring user need: "**who** did X" (watched / viewed / claimed / reviewed / attended). Core finding: the MCP exposes **aggregate-per-content counters**, not **per-member activity** — with one new exception.

- ✅ **EXCEPTION — events:** `orders_list(user_id=…)` returns a member's purchase history across events (verified: Danson = 6 orders, incl. a $3,995 one). So **events-purchased-per-member**, **attendee rosters**, and **spend-per-member** are now doable.
- ❌ **Partners — both requested queries are BLOCKED.** `partners_list/get` return only scalars (`page_view_count`, `claim_count`, `review_count`, `rating_avg`); no per-member arrays, and there is **no reviews endpoint**.
  - *"Who viewed but didn't claim"* → only the **count** is derivable (`page_view_count − claim_count`; e.g. Riverbend 252−119 = **133**, Scale Insights 82, Carbon6 160). Identities are not available.
  - *"Who left 1–2★ and didn't claim"* → **fully blocked** — no per-review data, author, or rating filter.
  - 🐞 **Bug:** partner `review_count`/`rating_count` come back **0** in the MCP but the UI shows **32** reviews (Riverbend). Aggregate review count is broken (`rating_avg` 4.6 is correct; flagged `rating_stringified`).
  - **To unlock:** add `partner_claims_list` (who claimed), `partner_reviews_list` (reviewer + stars + text), per-member view events — the partners-domain analog of `orders_list`.
- ❌ **Videos — "who watched / liked / commented the most (past weeks)" all BLOCKED.** `videos_list/get` return only scalars (`view_count`, `like_count`, `comment_count`); no per-member watchers/likers, no watch sessions or watch-time. No video-comments endpoint (`comments_list` is POST-scoped, needs a `post_id`). **Double blocker:** counts are **lifetime** — no time window (`created_after` filters video *upload* date, not views), so "past weeks" can't be expressed.
  - Adjacent thing that DOES work: community **posts/comments** carry `author_user_id` + timestamp → a *post-feed* "top poster/commenter" leaderboard is doable (just not for videos).
  - **To unlock:** `video_views_list` (who / when / duration), `video_likes_list`, `video_comments_list` — with date filters.
- ⚠️/❌ **Sessions & presence (members):**
  - *Last seen online* → `members.last_seen_at` exists and is sortable (`last_seen_at:asc/desc`), but the data is **unreliable** (§1: Ian MCP Nov 14 '24 vs UI Jan 16 '25, predates join). The UI's live "online now" count (e.g. 7) is **not** in the MCP.
  - *Number of sessions* → ❌ not exposed (no session-count field, no sessions endpoint).
  - *Average session length* → ❌ not exposed (no session-duration data).
  - **To unlock:** a `sessions_list` / session-analytics endpoint (login events with start/end timestamps) — currently absent.
- ✅/❌ **Notifications (mixed):** *Sent* (`recipient_count`) and *Clicks* (`read_count`) are ✅ exposed + validated (e.g. 57 sent / 5 clicks = 8.77%). But *who clicked / who received* → ❌ both `announcements_list` AND `announcements_get` return only aggregates (verified — GET adds no per-recipient array); `my_notifications_list` is the authenticated principal's own only. So: **how-many yes, who no.** ⚠️ field is `read_count` but UI labels it "Clicks."
- ❌ **Form responses — BLOCKED (big one).** `application_forms_list/get` return form **definitions only** (the `fields`/questions). Verified the real "AI NY - Mastermind" form incl. the field *"Please list any dietary restrictions, allergies, or mobility needs."* But there is **no form-responses/submissions endpoint** — zero submitted answers, zero respondent identities. So *"who answered question X with value Y"* (e.g. dietary = Gluten Free) is **impossible via MCP** — must export from UI. To unlock: `form_responses_list` (respondent + per-field answers, filterable by field/value).
- ❌ **Members Map usage:** no map endpoint, no member location/geo in `members_*`, no usage metric (UI shows 551 members placed; MCP exposes none). To unlock: surface member `address`/lat-lng + (optionally) map-view events.
- ❌ **API-usage / metering:** MCP exposes no request-count, rate-limit-usage, or call-analytics endpoint. "How many API calls" is not answerable.
- ❌ **Documents — "who viewed / who downloaded" BLOCKED.** Verified `documents_list` AND `documents_get` (detail view) both return only aggregate scalars (`views_count`, `download_count`, `likes_count`, `comments_count`, `save_count`, `share_count`). Only person field = `owner` (uploader); `access.user_ids` = who's *allowed*, not who engaged. No per-member viewer/downloader endpoint. UI "Downloaded documents" tab not exposed. Counts ✅ (validated §4), who ❌.

## 11. ✅ Events — additional endpoints (verified 2026-06-11)
- `orders_list/get` ✅ (see §5) · `ticket_types_list` ✅ (per-tier sold + price) · `ticket_addons_list` ✅ (add-on name, price, capacity).
- 🐞 **Add-on `quantity_sold` = 0** despite add-on sales present in `orders` (addon_amount_cents 15000) — counter not wired to actual sales.
- ✅ **`price_cents` unit bug FIXED (re-checked live 2026-06-11):** `ticket_types.price_cents` = **39500** (= $395, TRUE cents), consistent with `ticket_addons` = **15000** (= $150). Both endpoints now use true cents; matches order/invoice `amount_cents`. The original P1 "price_cents = dollars" (was 395) is **resolved** — supersedes §5/§8.
- `application_forms_list` = form definitions (questions/choices) only — useful for reading the *form*, not the *responses* (see §10).
