> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS MCP — Deep QA Analysis

**Auditor:** Claude (acting QA) · **Subject:** in-house GroupOS MCP server (`api.groupos-staging.co/v1/mcp`)
**Token:** read-only PAT (`pat_pub_*`, tier `public`, 27 `:read` scopes), bound to **MDS** community `67011d987a2a81b28438a3d8`
**Date:** 2026-06-11 · **Method:** live MCP calls + staging admin UI cross-checks (`mds.groupos-staging.co`). Andy's test cases used as references; coverage extended across all reachable endpoints + cross-cutting dimensions.

---

## 0. Executive verdict
A **well-built, security-sound, read-only data API** over the community platform. It is **excellent for catalog + transactional + aggregate-metric data**, and the team is **actively improving it** (3 findings from earlier this session were already fixed). 

The **one structural gap** that blocks most "intelligence" use-cases: **there is no per-member activity/engagement layer.** The MCP knows *what content exists* and *how popular it is in total*, and *who transacted* (events/refunds/subscriptions) — but not *who consumed what, when* (views, watches, opens, reads, clicks, sessions). Every "who is engaged / who watched / who viewed but didn't act" question dead-ends here.

**Maturity scorecard (1–5):**
| Dimension | Score | Note |
|---|---|---|
| Security / auth | **5** | read-only, scope-enforced, tenant-isolated, secrets redacted |
| Correctness / fidelity | **4** | UI-validated across domains; a few stale counters |
| Consistency | **3** | unit/naming/envelope/timestamp inconsistencies |
| Coverage (read) | **4** | broad; missing per-member activity + form responses |
| AI-consumability | **3** | clean errors & pagination, but heavy payloads (pages_list fails the token cap) |
| Engagement analytics | **2** | transactional only; no activity layer |

---

## 1. Security & auth — ✅ strong (best-in-class for this surface)
| Test | Result |
|---|---|
| Read-only enforcement | ✅ token has only `:read` scopes; no write/admin observed |
| **Scope enforcement** | ✅ `webhooks_list` + `webhook_deliveries_list` → `403 forbidden, requires "webhooks:admin"` (**FIXED** — leaked in session 1) |
| **Tenancy isolation** | ✅ any endpoint with a non-bound `community_id` → `403 "community_id … does not match the token's bound community"` |
| Bad object id | ✅ clean `{error:"not_found", resource, id}` |
| Secret redaction | ✅ OAuth tokens never returned (calendar shows only `has_refresh_token`); webhook secrets show only `secret_hint` |
| Error envelope | ✅ consistent `{error, detail}` / `{error, resource, id}` shape across all failure modes |

**Residual security/privacy items:**
- 🟠 `communities_get` leaks **garbled encrypted `comet_chat.region`/`app_id`** (`"Salted__…"` OpenSSL blobs as broken UTF-8) — redact or omit.
- 🟠 **OAuth fallback over-scopes**: when a static PAT is rejected, `mcp-remote` initiates an OAuth flow requesting `…:write`, `webhooks:admin`, `admin:users:write`, `admin:impersonate`, `admin:migrations:write`, `platform:admin`. For a read-only tool the default consent set is dangerously broad — scope it down to read.

---

## 2. Coverage & completeness
**~40 read endpoints across ~33 families** (all list/get; no write — by design):
members, group_members, subscriptions, tiers, roles, collaborators, communities, events, ticket_types, ticket_addons, **orders**, invoices, refunds, partners, videos, documents (+categories/collections/content_types), posts, comments, channels, announcements, news, pages, menus, tags, forms (application_forms), calendar_connections, webhooks (+deliveries, admin-gated), access_resources, my_profile/my_notifications/my_collaborator_invitations, health, whoami.

**Notable missing capabilities (read):**
- ❌ **Per-member activity / events stream** (views, watches, opens, reads, clicks, sessions) — the big one (§6).
- ❌ **Form responses / submissions** — `application_forms_*` return question *definitions* only; no answers, no respondents.
- ❌ **Per-member "who" for content** — video views/likes/comments, doc views/downloads, partner views/claims/reviews, notification clicks: all aggregate-only.
- ❌ **Sessions / presence** — no session count/length; no live "online now."
- ❌ **Member geo / Members-Map data** — `members_*` expose no `address`/lat-lng (UI Map has 551 placed).
- ❌ **API-usage / metering** — no request counts or rate-limit usage.
- ❌ **Partner reviews list** — only `review_count`/`rating_avg` aggregates.

---

## 3. Correctness & fidelity (UI-validated)
All spot-checks matched the staging admin UI exactly:
- Video `view_count` (997, 845) · event tickets sold **20/43** + every per-tier price · document views/downloads (top-3) · notification `recipient_count`/`read_count` (57/5 = 8.77%) · member profile fields · order totals (**$5,935** = 19 orders, matches UI Net sales).

**Stale / wrong values found:**
- 🔴 `members.last_seen_at` **wrong** — UI "Last seen" Jan 16 '25 vs MCP Nov 14 '24, and predates `joined_at`. (Sortable but untrustworthy.)
- 🟠 partner `review_count`/`rating_count` = **0** while UI shows **32** (Riverbend). Aggregate review count broken (`rating_avg` ok).
- 🟠 `ticket_addons.quantity_sold` = **0** despite add-on sales present in `orders`. Counter not wired.

---

## 4. Consistency (schema-level)
- 🟠 **Timestamps inconsistent:** `subscriptions`/`tiers` use **epoch-seconds ints** (`current_period_end: 1760918399`); the rest of the API uses **ISO-8601 strings**.
- 🟠 **List envelopes inconsistent:** `document_categories_list` / `document_content_types_list` return a **bare array**; every other list returns `{items, next_cursor, has_more, total}`.
- 🟠 **Naming:** notifications `read_count` is labeled **"Clicks"** in the UI (read vs click ambiguity). `members.subscription_id` is an internal ObjectId while the UI shows the Stripe `sub_…`.
- 🟢 **Units now consistent** (post-fix): `ticket_types.price_cents` (39500), `ticket_addons.price_cents` (15000), `tiers.*_price_cents` (499700), `refunds.amount_cents` (60), `orders.*_cents` are **all true cents**. (Session-1's "price_cents = dollars" is **fixed**.)
- 🟢 ID formats consistent (24-char ObjectIds); pagination cursors consistent; filters/sorts behave.

---

## 5. AI-consumability
- 🔴 **`pages_list` exceeds the response token cap** even at `limit=3` — each page returns `html_content` + full `json_content` AST + a `blocks[]` array that duplicates the HTML. Effectively unusable for an LLM; use `get` per id.
- 🟠 **Raw HTML everywhere** — `description`/`body` fields ship full HTML (partners, videos, news, tiers, ticket types). Heavy on context; no plaintext alternative.
- 🟠 **No field projection** — no `fields=`/sparse-fieldset to trim payloads; `events_list` also ships ~90-URL `gallery` arrays per item.
- 🟢 Good: cursor pagination + `with_total` opt-in everywhere; rich, accurate tool descriptions; self-reported `_warnings` (`rating_stringified`, `currency_defaulted_usd`, `legacy_video_raw_url`, `tenancy_not_yet_enforced`, etc.); clean error envelope.

**Recommendation:** trim list payloads (strip/relocate HTML+JSON, drop galleries from list), add a `fields=` selector, and never return `json_content`/`blocks` in list mode.

---

## 6. The architectural gap — no per-member activity layer
This is the single highest-impact finding. Engagement intelligence needs *who did what, when*; the MCP exposes aggregate-per-content counters + transactional records only.

| Domain | Aggregate counts | Per-member "who" |
|---|---|---|
| Events / orders / refunds / subscriptions | ✅ | ✅ (`orders_list`/`refunds_list`/`subscriptions_list` by `user_id`) |
| Videos (views/likes/comments) | ✅ | ❌ |
| Documents (views/downloads) | ✅ | ❌ |
| Partners (views/claims/reviews) | ✅ | ❌ |
| Notifications (sent/clicks) | ✅ | ❌ |
| Forms | definitions only | ❌ responses |
| Sessions / presence / last-seen | ❌ / ⚠️broken | ❌ |
| Maps usage / API usage | ❌ | ❌ |

**Consequence:** member engagement cards, "engaged vs stale," "watched the most," "viewed-but-didn't-claim," "who answered dietary = gluten-free," cohort/funnel/retention — **all impossible today.** All counts are also **lifetime** (no time-window), so even aggregate "last 30 days" can't be expressed.

**The unlock (one foundational addition):** a per-member activity stream —
`(member_id, action, object_type, object_id, timestamp, [duration|value])` — logging views/watches/opens/reads/clicks. That single table + endpoint delivers last-active (reliable), consumption breadth/depth, time-windows, engaged-vs-stale, and the full engagement card. Plus `form_responses_list` and a `sessions_list`.

---

## 7. Defect register
**🟢 Fixed during this session (dev team shipped):**
1. `invoices_list` revenue gap → new **`orders_list`/`orders_get`** (complete orders; verified $5,935 / 19 orders).
2. `price_cents` dollars→**true cents** (39500).
3. **webhooks scope-bypass** → now `403`.

**🔴/🟠 Open:**
| # | Sev | Issue |
|---|---|---|
| 1 | 🔴 | No per-member activity layer (§6) — blocks all engagement analytics |
| 2 | 🔴 | `members.last_seen_at` wrong / predates join |
| 3 | 🟠 | No `form_responses` endpoint (definitions only) |
| 4 | 🟠 | `pages_list` payload exceeds token cap (AI-unusable) |
| 5 | 🟠 | `communities_get` leaks `comet_chat` `Salted__` encrypted blob |
| 6 | 🟠 | `collaborators_list` returns all rows with empty `user_id`/`user:null` (194 rows) |
| 7 | 🟠 | partner `review_count`/`rating_count` = 0 vs UI 32 |
| 8 | 🟠 | `ticket_addons.quantity_sold` = 0 despite sales |
| 9 | 🟡 | timestamp + envelope + naming inconsistencies (§4) |
| 10 | 🟡 | OAuth fallback requests platform-admin scopes (§1) |

**Data hygiene (not MCP bugs, but visible):** 55 tiers incl. many test/deprecated (`TestTest`, `Billing Test`, `123456789`, `Eugene ABC`); test partners/forms in prod (`COPY Ecompreneur`, `LAST NAMESSS`); a live `ticket.purchased` webhook failing HTTP 404; "Stripe customer is deleted" banner on staging.

---

## 8. Best-practices assessment
**Done well:** least-privilege read scopes · enforced scope checks · tenant isolation · secret redaction · consistent error envelope · cursor pagination + opt-in counts everywhere · honest `_warnings` self-reporting · clear tool descriptions · units now standardized to cents · active iteration on feedback.

**Lacking:** per-member activity layer · form responses · payload-size discipline / field projection · a few stale counters · one leaked encrypted field · cross-endpoint consistency (timestamps/envelopes/naming) · lifetime-only metrics (no time windows).

---

## 9. Prioritized recommendations
- **P0 — Activity stream.** Add a per-member event log + `activity_list(user_id?, action?, object_type?, since?, until?)`. Unlocks engagement cards, segmentation, funnels, "engaged vs stale," and fixes "last active" properly. Single highest ROI.
- **P1 —** `form_responses_list` (respondent + per-field answers, filterable by field/value) · fix `last_seen_at` · trim `pages_list`/list payloads + add `fields=` projection.
- **P2 —** per-domain "who" endpoints (video_views, doc_downloads, partner_claims, notification_clicks) *or* let the §P0 stream subsume them · fix `review_count`, `ticket_addons.quantity_sold`, `collaborators_list.user_id` · redact `comet_chat`.
- **P3 —** consistency cleanup (ISO timestamps everywhere, uniform list envelope, rename `read_count`↔"clicks") · time-windowed metric variants · purge test tiers/forms from prod.

---
*Companion log: `GROUPOS_MCP_QA.md` (per-endpoint UI↔MCP verification + §10 per-member gaps + §11 events).*
