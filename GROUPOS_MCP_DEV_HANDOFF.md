> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS MCP — QA Hand-off for Dev (complete)

**What:** full QA of the GroupOS MCP (`api.groupos-staging.co/v1/mcp`).
**How:** all **66** `groupos` tools individually exercised on **2026-06-11**, read-only PAT (`pat_pub_*`, 27 `:read` scopes) bound to **MDS** `67011d987a2a81b28438a3d8`, cross-checked vs the staging admin UI (`mds.groupos-staging.co`).
**Single source of truth** — supersedes `GROUPOS_MCP_QA.md` / `…_ANALYSIS.md` / `…_CHECKLIST.md`.

**Contents:** §1 Summary · §2 Use-case results (every question) · §3 Module fidelity (UI↔MCP) · §4 Defect register · §5 Fixed · §6 Security tests · §7 66-tool coverage · §8 Activity-stream spec.

---

## 1. Summary
Secure, well-built **read-only data API**. Security + financial/transactional layer are strong; correctness good. 3 issues found mid-QA were already fixed. **The one strategic gap (P0): no per-member activity layer** — the API knows *what exists*, *how popular in total*, and *who transacted*, but never *who consumed what* (views/watches/opens/reads/clicks/sessions). All metrics are **lifetime-only** (no time windows). This blocks every engagement question below.

| Area | Grade |
|---|---|
| Security / auth | A — read-only, scope-enforced, tenant-isolated, secrets redacted |
| Financial/transactional | A — orders/refunds/subscriptions/tiers, per-member queryable |
| Correctness / fidelity | B+ — UI-validated; few stale counters |
| Consistency | B− — timestamp/envelope/naming drift |
| AI-consumability | C+ — clean errors/pagination; `pages_*` over size cap |
| **Engagement analytics** | **D — transactional only, no activity layer** |

---

## 2. Use-case results — every question tested
Verdict: ✅ supported · ⚠️ partial/unreliable · ❌ not possible. (Root cause for most ❌ = GOS-1, no activity layer.)

| # | Business question (case) | Verdict | Evidence / why |
|---|---|---|---|
| 1 | Email for a member (Ian Sells) | ✅ | `members_list(q)` → `iansells@gmail.com` |
| 2 | Member "last seen online" | ⚠️ | `members.last_seen_at` exists but **wrong** (Ian: MCP Nov 14 '24 vs UI Jan 16 '25, predates join) → GOS-2 |
| 3 | Event sales / tickets sold / dates (AI Mastermind) | ✅ | dates + 20/43 sold + per-tier prices via `events_get`/`ticket_types_list`; revenue **$5,935** via `orders_list` |
| 4 | Did member X buy a ticket? (Danson Hui) | ✅ | `orders_list(user_id)` → $545 order. *(Note: `invoices_list` alone gave a false-negative — manual orders only.)* |
| 5 | Look up an order # (`6a26db72…`) | ✅ | `orders_get` resolves it (Danson's order). *(`invoices_get` 404s — different collection.)* |
| 6 | Tickets sold count / types / add-ons | ✅ | `ticket_types_list` (5 tiers) + `ticket_addons_list` (2 add-ons, $150) |
| 7 | **Form responses** / who answered "dietary = gluten-free" | ❌ | `application_forms_*` return **questions only**; no responses/respondents → GOS-3 |
| 8 | Most-engaged members (video+partner+event+doc opens, 30d) | ❌ | no per-member consumption + no time window → GOS-1 |
| 9 | Avg events visited per member | ⚠️ | possible for **purchases** via `orders_list(user_id)`; *attendance/opens* not tracked |
| 10 | Who opened an event but didn't buy | ❌ | no per-member event page-views → GOS-1 |
| 11 | Last watched video / total watch time / % complete | ❌ | videos expose only aggregate `view_count`; no sessions/duration → GOS-1 |
| 12 | Who watched / liked / commented most (past weeks) | ❌ | aggregate-only + lifetime (no window) → GOS-1 |
| 13 | Who viewed a partner but didn't claim | ❌(⚠️) | only the **count** is derivable (`page_view_count − claim_count`, e.g. Riverbend 252−119=133); identities ❌ |
| 14 | Who left a 1–2★ review and didn't claim | ❌ | no per-review data/author; partner `review_count` also broken (GOS-6) |
| 15 | Notifications: sent / clicks / who clicked | ✅ / ✅ / ❌ | `recipient_count` + `read_count` (57/5 = 8.77%) ✅; *who* clicked ❌ (aggregate only) |
| 16 | Documents: who viewed / who downloaded | ❌ | only aggregate `views_count`/`download_count`; `owner` = uploader, not viewer → GOS-1 |
| 17 | Number of sessions / avg session length | ❌ | no session/presence data anywhere |
| 18 | Live "online now" count | ❌ | UI shows it (e.g. 7); not in MCP |
| 19 | Members-Map usage / how many used it | ❌ | no map endpoint; no member `address`/geo (UI Map = 551 placed) |
| 20 | How many API calls (usage/metering) | ❌ | no usage/rate-limit endpoint |
| 21 | Per-member engagement card / "engaged vs stale" | ❌ | needs presence + consumption per member → GOS-1. Thin transactional card (events bought, $ spent, tenure/tier) is buildable; consumption + recency are not |
| 22 | MRR / revenue / active-by-tier | ✅ | `subscriptions_list`(3,078) × `tiers_list`(55, real prices) join |
| 23 | Refunds / financial reconciliation | ✅ | `refunds_list` (107, full Stripe refund/charge detail, per-user) |

**Takeaway:** transactional/financial questions (3,4,5,6,22,23) and aggregate stats (15-sent/clicks) work. Everything about **how a member uses the app** (8,10,11,12,13,14,16,17,18,21) is blocked by GOS-1. Form responses (7) by GOS-3.

---

## 3. Module fidelity — UI vs MCP (each module)
All record-level spot-checks matched the UI exactly; count gaps are filter/scope differences, not data loss.

| Module | MCP | UI | Match? |
|---|---|---|---|
| **Members** | active-M 2,097 / all-edges 3,443 | "Members" tab 840 | ⚠️ different populations (tab vs `member_type=M`) — define before comparing |
| Members — Ian profile | first/last/display/email | same | ✅ |
| Members — Ian last_seen | Nov 14 '24 | Jan 16 '25 | ❌ GOS-2 |
| **Videos** | 973 · view_count 997, 845 | 972 · 997, 845 | ✅ counts match (off-by-1 = 0-view video) |
| **Partners** | 592 · TestParty 2 views/4 claims | 594 · 2/4 | ✅ (UI search bug is UI-side); `review_count` 0 vs **32** ❌ GOS-6 |
| **Documents** | 589 (Public default) · top-3 views/dl | 592 (all) · 3/0, 2/0, 2/0 | ✅ data matches |
| **Events** | AI Mastermind 20/43; tiers Host 2/2·Member 11/15 $395·AllStar 1/10 $95·Standard 5/15·Lite 1/1 $595 | identical | ✅ |
| Events — revenue | `orders` 19 = **$5,935** | Net sales $5,935 | ✅ (via `orders_list`, not `invoices`) |
| **Notifications** | 224 · 1/0, 57/5, 1/1 | 224 · same (8.77%) | ✅ |

---

## 4. Defect & gap register (file these)
Severity: **P0** strategic · **P1** blocks use · **P2** data/leak · **P3** polish. Repro = MCP call.

**P0 — GOS-1 · No per-member activity layer** *(feature)* — see §2 (cases 8,10,11,12,16,17,18,21) and §8 for the fix.

**P1**
- **GOS-2 · `members.last_seen_at` wrong.** `members_get(…6791ea053b8debd23a9b5bdb)` → `2024-11-14`; UI Jan 16 2025; predates `joined_at`. Re-point to real activity source.
- **GOS-3 · No form-responses endpoint.** `application_forms_*` = definitions only. Add `form_responses_list(form_id, field_id?, value?)` → respondent + answers.
- **GOS-4 · `pages_*` over size cap.** `pages_get(…67bf51e203c6ce78877ab9fa)` = **207,163 chars** (one page); `pages_list` fails at limit=3. Cause: `html_content` + full `json_content` AST + `blocks[]` (HTML duplicated). Drop json/blocks from responses; add projection.

- **GOS-18 · No `user_id` → member resolution.** *(found 2026-06-11 while testing cross-module chains)* `orders`/`refunds`/`subscriptions` reference buyers by `user_id`, but `members_get(user_id)` → `not_found` (expects member_id) and `members_list` has **no user_id filter** — so resolving "who bought this?" requires paginating all 3,443 members client-side. Breaks attendee-roster names (EVT-4/5) and every order-first chain (X-1, X-3 in `GROUPOS_MCP_TEST_CASES.md`). **Fix: add `user_id` filter to `members_list`** (or accept user_id in `members_get`). Small change, big unlock.

- **GOS-19 · No check-in data — PROVEN with populated data (MDS Inspire 2026, `67ec27fb9f41efcff94364d0`).** The flagship event's Check-ins page shows **"Checked in 313 of 376"** with per-person rows (name, email, **attendee type**, check-in count "1 of 1"). The MCP returns for the same event: `attendee_count: 449`, **1 junk order (`status:"unknown"`, qty 0)**, **0 ticket types** — i.e. **313 real check-ins are 100% unreachable**. This is the attendance signal the member scorecard needs (+30 pts), live in production data today. **Fix:** `checkins_list(event_id)` → user_id + attendee_type + checked_in_at; or check-in state on an attendees endpoint (see GOS-21).
- **GOS-21 · Attendee roster invisible — manually-added attendees are NOT orders.** *(2026-06-11, Inspire)* The UI Attendee list shows **436 attendees** (names, emails, **companies**, attendee types Member/Speaker/**Partners/Partners Team**, registration type "Manually added", per-row status) — but `orders_list(event)` returns **1 row** (status `"unknown"`) and `ticket_types_list` returns **0**. So for any event with manual/external registration the entire roster has no MCP surface. Also: **three conflicting counts** for one event (UI attendee list 436 · check-ins page 376 · MCP `attendee_count` 449) — define the canonical attendee count. **Fix:** `attendees_list(event_id)` → user_id/email, attendee_type, company, registration_type, status, check-in state. (This endpoint would subsume GOS-19 and unblock the X-1 partner-attendee chain — "attendee type Partners" is literally a column in this UI.) Related: order `status:"unknown"` exists in the wild yet `orders_list` has no status filter; `ticket_platform:"external"` (Luma) events have zero ticket/order data.
- **GOS-20 · Approval requests invisible — even the EMPTY state is unaskable.** *(2026-06-11, verified on a live approval-configured event)* Toronto Chapter Boardroom June 2026 (`6a26fa3da645c561db6441cc`) has two tickets with **`requires_approval: true`** (flag verified working via MCP — config IS visible). But the approval **queue** cannot be queried at all: no approvals endpoint, no `orders_list` status filter — so an integrator can't even retrieve **"0 pending requests"**; the question itself doesn't exist. (Empty-but-queryable ≠ missing capability — today they're indistinguishable.) Two surfaces affected: ① **subscription/tier approvals** (Members → "All subscription submissions": name, Tier, Form name, Status — no MCP counterpart) and ② **event-ticket approvals** (MDS's intent-collection workflow: approval ticket, nobody approved, the pending queue IS the data). **Also found: `ticket_types` carries NO linked-form reference** — the UI shows "Linked form: Template – Chapt…" per ticket, the MCP payload has no such field, so the ticket→form linkage the approval decision depends on is also invisible. **Fix:** `approval_requests_list(scope, event_id?, status?)` → applicant user_id + requested_at + status; add `linked_form_id` to ticket_types; (+ form-response link once GOS-3 ships). *Verification boundary: config flag + unaskable-queue are proven; how a PENDING request serializes (some order status vs. absent entirely) is unverified — no test request was submitted. Dev can close that last gap by submitting one and checking `orders_list`.*

**P2**
- **GOS-5 · `comments_list` returns 0** where `posts_get(…640977c3…).comment_count = 3`. Counter↔collection drift; `comments_get` unreachable.
- **GOS-6 · Partner `review_count`/`rating_count` = 0** while UI shows 32 (Riverbend `651fa13408ae15d71a2d5f2d`). `rating_avg` ok.
- **GOS-7 · `ticket_addons.quantity_sold` = 0** despite add-on sales in `orders` (`addon_amount_cents:15000`).
- **GOS-8 · `communities_get` leaks** encrypted `comet_chat.region`/`app_id` (`Salted__` blobs). Decrypt or omit.
- **GOS-9 · `collaborators_*` `user` null/blank** (224 rows, `inviter_unknown`) — can't identify collaborators.
- **GOS-10 · OAuth fallback over-scopes** — consent requests `*:write`, `webhooks:admin`, `admin:impersonate`, `platform:admin` for a read-only tool. Scope the OAuth client to read.

**P3**
- **GOS-11 · Timestamps** — `subscriptions`/`tiers` epoch ints vs ISO elsewhere. Standardize ISO.
- **GOS-12 · Envelopes** — `document_categories_list`/`document_content_types_list` return bare arrays; others `{items,…}`.
- **GOS-13 · Naming** — notif `read_count` shown as "Clicks"; `members.subscription_id` = internal ObjectId not Stripe `sub_…`.
- **GOS-14 · `events_list` nulls `ticket_summary`/`attendee_count`** that `events_get` populates.
- **GOS-15 · Stale calendar connection** — `token_expires_at` past, `needs_reconnect:false`, `last_sync_at:null`.
- **GOS-16 · Data hygiene (not MCP):** 55 tiers incl. test/deprecated; test partners/forms in prod; a live `ticket.purchased` webhook failing 404; "Stripe customer deleted" banner.
- **GOS-17 · Payload weight** — raw HTML + ~90-URL galleries in lists; no `fields=` projection.

**Capability gaps (fold into GOS-1):** per-member "who" for videos/documents/partners/notifications; sessions/presence; member geo/Map data; API-usage metering; time-windowed metrics. **Also (verified 2026-06-11):** news items carry **no engagement counters at all** (no views/reads/clicks — verified on live records); event objects lack the **page-view/unique-visitor** counters the UI dashboard shows (261/77); no member↔partner link field (can't identify "partner-type" attendees); no sort-by-engagement on videos/docs; no `event_id` filter on videos/docs.

> **Scenario catalog:** `GROUPOS_MCP_TEST_CASES.md` — 60 realistic admin scenarios across all 9 modules + cross-module chains (26 ✅ · 14 ⚠️ · 20 ❌), each mapped to the tickets above.

---

## 5. Already fixed this session — verify & close
1. **`price_cents` dollars → true cents.** `ticket_types.price_cents` was `395`, now **`39500`** ($395); matches `orders`/`invoices.amount_cents`.
2. **`invoices_list` gap → `orders_list`/`orders_get` shipped.** `orders_list(event)` = complete 19 orders / $5,935 (vs 4 invoices / $1,880). Use `orders_*` for revenue/attendees.
3. **Webhooks scope-bypass fixed.** `webhooks_*` + `webhook_deliveries_list` now `403 requires webhooks:admin`.

---

## 6. Security & negative tests — all PASS
| Test | Result |
|---|---|
| Read-only enforcement | ✅ only `:read` scopes |
| Scope enforcement | ✅ webhooks ×3 → 403 |
| Tenancy isolation | ✅ non-bound `community_id` → 403 |
| Bad ObjectId | ✅ clean `not_found` |
| Secret redaction | ✅ OAuth tokens hidden; webhook `secret_hint` only |

---

## 7. Coverage — 66 tools, 0 down
✅ OK · 🔒 correctly 403 (scope) · ⚠️ responds w/ issue · N/A no data.

| Tool | St | Tool | St | Tool | St |
|---|---|---|---|---|---|
| health | ✅ | ticket_types_list | ✅ | news_list | ✅ |
| whoami | ✅ | ticket_types_get | ✅ | news_get | ✅ |
| communities_get | ✅ | ticket_addons_list | ✅ | pages_list | ⚠️ |
| members_list | ✅ | ticket_addons_get | ✅ | pages_get | ⚠️ |
| members_get | ✅ | orders_list | ✅ | menus_list | ✅ |
| group_members_list | ✅ | orders_get | ✅ | menus_get | ✅ |
| groups_list | ✅ | invoices_list | ✅ | tags_list | ✅ |
| groups_get | ✅ | invoices_get | ✅ | tags_get | ✅ |
| subscriptions_list | ✅ | refunds_list | ✅ | application_forms_list | ✅ |
| subscriptions_get | ✅ | refunds_get | ✅ | application_forms_get | ✅ |
| tiers_list | ✅ | partners_list | ✅ | calendar_connections_list | ✅ |
| tiers_get | ✅ | partners_get | ✅ | calendar_connections_get | ✅ |
| roles_list | ✅ | videos_list | ✅ | access_resources_list | ✅ |
| roles_get | ✅ | videos_get | ✅ | webhooks_list | 🔒 |
| collaborators_list | ✅ | documents_list | ✅ | webhooks_get | 🔒 |
| collaborators_get | ✅ | documents_get | ✅ | webhook_deliveries_list | 🔒 |
| events_list | ✅ | document_categories_list | ✅ | my_profile_get | ✅ |
| events_get | ✅ | document_collections_list | ✅ | my_notifications_list | ✅ |
| posts_list | ✅ | document_collections_get | N/A | my_notifications_get | N/A |
| posts_get | ✅ | document_content_types_list | ✅ | my_collaborator_invitations_list | ✅ |
| comments_list | ⚠️ | channels_list | ✅ | announcements_list | ✅ |
| comments_get | N/A | channels_get | ✅ | announcements_get | ✅ |

⚠️ `comments_list`(GOS-5), `pages_*`(GOS-4). N/A = empty collection (no id).

---

## 8. Fix spec for GOS-1 — per-member activity stream
**Table** `member_activity`: `member_id, user_id, action ∈ {video_view, video_like, video_comment, doc_view, doc_download, partner_view, partner_claim, partner_review, news_read, notification_click, page_view, login}, object_type, object_id, value? (duration_sec | stars | amount), occurred_at`.
**Endpoint** `activity_list(community_id, user_id?, action?, object_type?, since?, until?, cursor?, with_total?)`.

Delivers reliable **last-active**, **consumption breadth/depth**, **time-windowed** metrics, **engaged-vs-stale** segmentation, and the full **member engagement card** — composed with existing `orders`/`refunds`/`subscriptions` (transactional) + `members`/`tiers` (lifecycle). Single highest-ROI addition.
