> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS MCP — Per-Endpoint QA Checklist

**Every one of the 66 `mcp__groupos__*` tools individually called** against MDS (`67011d987a2a81b28438a3d8`) on 2026-06-11, read-only PAT. Legend: ✅ responds OK · 🔒 correctly scope-denied (403) · ⚠️ responds but issue · N/A untestable (no data/id) · 🐞 data bug.

**Totals:** 66 tools · **0 down** · 58 ✅ · 3 🔒 (scope-enforced, correct) · 2 ⚠️ (pages bloat) · 3 N/A (empty collections).

## Modules captured (36 resource families)
meta(health, whoami) · communities · members · group_members · groups · subscriptions · tiers · roles · collaborators · events · ticket_types · ticket_addons · **orders** · invoices · refunds · partners · videos · documents · document_categories · document_collections · document_content_types · posts · comments · channels · announcements · news · pages · menus · tags · application_forms · calendar_connections · access_resources · webhooks · webhook_deliveries · my_profile · my_notifications · my_collaborator_invitations

---

## Full checklist

| # | Tool | Status | Evidence / total | Notes |
|---|------|--------|------------------|-------|
| 1 | health | ✅ | `{status:ok}` | liveness |
| 2 | whoami | ✅ | 27 `:read` scopes, tier public | read-only confirmed |
| 3 | communities_get | ✅ / 🔒 | bound OK; non-bound → 403 | ⚠️ leaks `comet_chat` `Salted__` blob |
| 4 | members_list | ✅ | total 3,443 | 🔒 cross-tenant → 403 |
| 5 | members_get | ✅ | Ian Sells | 🐞 `last_seen_at` wrong; no address/geo |
| 6 | group_members_list | ✅ | Asia Pacific 1/1 | user `display_name` blank |
| 7 | groups_list | ✅ | total 38 | `created_by` null (`created_by_missing`) |
| 8 | groups_get | ✅ | Asia Pacific Chapter | parity w/ list |
| 9 | subscriptions_list | ✅ | total 3,078 | status/Stripe-id/period dates |
| 10 | subscriptions_get | ✅ | one sub | ⚠️ epoch-int timestamps |
| 11 | tiers_list | ✅ | total 55 | real prices, TRUE cents; many test/legacy tiers |
| 12 | tiers_get | ✅ | Basic Plan | |
| 13 | roles_list | ✅ | total 7 | |
| 14 | roles_get | ✅ | Editor | |
| 15 | collaborators_list | ✅ | total 224 | ⚠️ `user` expansion often null/blank (`inviter_unknown`) |
| 16 | collaborators_get | ✅ | one collab | ⚠️ `user:null` |
| 17 | events_list | ✅ | total 675 | `ticket_summary` null in list |
| 18 | events_get | ✅ | AI Mastermind | ✓ richer: `ticket_summary` + `attendee_count:19` |
| 19 | ticket_types_list | ✅ | 5 tiers | sold + price |
| 20 | ticket_types_get | ✅ | Member $395 | `price_cents` 39500 (true cents — fixed) |
| 21 | ticket_addons_list | ✅ | 2 add-ons | |
| 22 | ticket_addons_get | ✅ | Dinner $150 | 🐞 `quantity_sold:0` despite sales |
| 23 | **orders_list** | ✅ | AI event 19 orders/$5,935 | per-`event_id`/`user_id`; NEW endpoint |
| 24 | **orders_get** | ✅ | Danson order | line items + abandoned-attempt audit trail |
| 25 | invoices_list | ✅ | 4 (AI event) | manual orders only |
| 26 | invoices_get | ✅ | `creation_type:"M"` | confirms manual subset |
| 27 | refunds_list | ✅ | total 107 | full Stripe refund/charge detail, per-user |
| 28 | refunds_get | ✅ | one refund | |
| 29 | partners_list | ✅ | total ~592 | 🐞 `review_count:0` vs UI 32; UI search bug (UI-side) |
| 30 | partners_get | ✅ | Riverbend | aggregate only (no per-viewer/claimer) |
| 31 | videos_list | ✅ | total 973 | |
| 32 | videos_get | ✅ | TikTok Cold Start, `view_count:846` | adds `dislike_count`; aggregate only |
| 33 | documents_list | ✅ | total 589 | default `status=Public` |
| 34 | documents_get | ✅ | Matthew Greene PDF | aggregate only (no per-viewer/downloader) |
| 35 | document_categories_list | ✅ | 38 categories | ⚠️ **bare array** envelope |
| 36 | document_collections_list | ✅ | total 0 (empty) | |
| 37 | document_collections_get | N/A | no id (empty collection) | endpoint not exercisable |
| 38 | document_content_types_list | ✅ | 14 types | ⚠️ **bare array** envelope |
| 39 | posts_list | ✅ | total 11 | tiny feed, mostly 2023 test; `author_user_id` present |
| 40 | posts_get | ✅ | "Hello World!" `comment_count:3` | |
| 41 | comments_list | ⚠️🐞 | returns **0** for post w/ `comment_count:3` | counter↔collection drift |
| 42 | comments_get | N/A | no comment id retrievable (list returns 0) | |
| 43 | channels_list | ✅ | total 91 | `member_count` populated (108, 62) |
| 44 | channels_get | ✅ | AI & Automations | |
| 45 | announcements_list | ✅ | total 224 | sent/clicks aggregates |
| 46 | announcements_get | ✅ | one announcement | aggregate only (no per-recipient) |
| 47 | news_list | ✅ | total 353 | HTML-heavy bodies |
| 48 | news_get | ✅ | Member Map news | |
| 49 | pages_list | ⚠️ | exceeds token cap at limit=3 | AI-unusable |
| 50 | pages_get | ⚠️ | **single page = 207,163 chars** → over cap | html+json+blocks triple-store; AI-unusable |
| 51 | menus_list | ✅ | total 24 | |
| 52 | menus_get | ✅ | TikTok Hub | submenus inline |
| 53 | tags_list | ✅ | total 240 | `slug` null (`slug_backfilled`) |
| 54 | tags_get | ✅ | one tag | |
| 55 | application_forms_list | ✅ | forms w/ field definitions | **definitions only** |
| 56 | application_forms_get | ✅ | AI NY Mastermind | **no responses** (questions only) |
| 57 | calendar_connections_list | ✅ | 1 google conn | ⚠️ token expired 05-21, `last_sync_at:null` (stale) |
| 58 | calendar_connections_get | ✅ | google | OAuth token redacted ✓ |
| 59 | access_resources_list | ✅ | total 6 | `community_id` empty (`tenancy_not_yet_enforced`) |
| 60 | webhooks_list | 🔒 | 403 requires `webhooks:admin` | scope-enforced ✓ (was a leak in session 1) |
| 61 | webhooks_get | 🔒 | 403 requires `webhooks:admin` | scope-enforced ✓ |
| 62 | webhook_deliveries_list | 🔒 | 403 requires `webhooks:admin` | scope-enforced ✓ |
| 63 | my_profile_get | ✅ | principal "MDS Community" | `created_at` 1970 epoch-zero |
| 64 | my_notifications_list | ✅ | total 0 (empty) | principal-scoped |
| 65 | my_notifications_get | N/A | no id (empty inbox) | |
| 66 | my_collaborator_invitations_list | ✅ | total 0 (empty) | principal-scoped |

---

## Negative / security tests (separate from the 66)
| Test | Result |
|---|---|
| Bad ObjectId (`orders_get`, `invoices_get`…) | ✅ clean `{error:not_found, resource, id}` |
| Cross-tenant `community_id` (members/communities) | ✅ `403 "community_id does not match the token's bound community"` |
| Scope-gated tools without scope (webhooks ×3) | ✅ `403 "requires webhooks:admin"` |
| OAuth tokens / webhook secrets | ✅ redacted (`has_refresh_token`, `secret_hint`) |

## Issues surfaced (rolled up)
- 🐞 `members.last_seen_at` wrong · `comments_list` returns 0 vs `comment_count` · `ticket_addons.quantity_sold` 0 vs sales · partner `review_count` 0 vs UI 32 · `collaborators` user-expansion null.
- ⚠️ `pages_list`/`pages_get` exceed token cap (bloat) · bare-array envelopes (doc categories/content_types) · epoch-vs-ISO timestamps (subscriptions) · `communities_get` `comet_chat` leak · stale calendar connection.
- ❌ Capability gaps: no per-member activity/views · no form **responses** · no sessions/presence · no member geo · no API-usage metering. (Full analysis: `GROUPOS_MCP_ANALYSIS.md`.)
- 🟢 Fixed this session: `price_cents`→cents · `orders_list` (revenue) · webhooks scope enforcement.
