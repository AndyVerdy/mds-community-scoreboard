# GroupOS → MDS: Partners integration — what is still outstanding

**From:** Andy (MDS) · **For:** Andrii (GroupOS MCP/API) · **Date:** 2026-09-03
Follow-up to `GROUPOS_PARTNERS_INTEGRATION_REQUEST.md` (2026-07-21). Original request numbering
kept; new findings start at **Request 7**.

**Method.** Measured on 2026-09-03 against 114 partner records pulled via `partners_list`, plus
targeted `partners_get`, `partner_categories_list`, `community_partner_reviews_list` and
bracketed-window probes. Auth: `whoami` → `tier: "public"`, `pat_id: null`.

---

## Acceptance scorecard from the original doc

| # | Test | Result |
|---|---|---|
| 1 | `curl` with a PAT pulls all published partners in one pass | **Fail** — no PAT issued |
| 2 | Pausing a partner shows in the next `updated_after` delta with its new status | **Pass** |
| 3 | The two bracketed records return, or are gone from `total` | **Fail** — both still unfetchable |
| 4 | Categories resolve to names for every `category_ref_id` in use | **Pass** |
| 5 | G10 Fulfillment's payload carries website / Facebook / LinkedIn | **Pass** |
| 6 | A new review is discoverable in one delta-shaped call | **Pass** |

Four of six. Two remain, and one of them is the main ask.

---

## What shipped — with thanks

**Request 5 was implemented exactly as written.** We pulled the named record,
`6a5dfe668a427b8944ac8cb6` (G10 Fulfillment):

```
contact_info: { contact_name: null, phone_number: null, email: null,
                website:  "https://g10fulfillment.com/",
                facebook: "https://www.facebook.com/G10Fulfillment",
                linkedin: "https://www.linkedin.com/company/81892762/" }
```

The three member-useful links are exposed and the three private fields stay null. That is the
split we offered, honoured precisely. Across 114 partners: website **114/114**, LinkedIn 102,
Facebook 77.

**Request 4 shipped, plus more than we asked for.** `partner_categories_list` returns 18 named
categories, and every `category_ref_id` in use resolves. You also added
`partner_subcategories_list`, which we had not requested and which covers the 45 distinct
`subcategory_ref_ids` we were carrying as opaque ids.

**Request 2's reviews half shipped as the best of the three options.**
`community_partner_reviews_list(created_after=…)` returned 20 reviews in a single call, each with
`partner_id`, `rating`, `text`, `created_at`, and a cursor. That replaces ~110 per-partner polls a
day with one call. `user_id` is null on most rows, which is fine for our use.

**Request 2's status half works.** Paused partners now appear in `updated_after` deltas carrying
`status: "paused"` — verified on `651d3e7c08ae15d71a2af81c` (Webgility).

**Request 6's first item shipped.** `page_url` is present on 114/114.

---

## Request 1 · 🔴 Service token (PAT) — still the main ask, still not delivered

`whoami` still returns `tier: "public"`, `pat_id: null`. Every read path remains MCP-only, which
means a Claude session, which means model tokens.

**What that cost on this run alone:** tonight's partner sync took **11 paginated MCP calls** and
still finished **7 records short** of the 94 the API reported for our window — not because of any
GroupOS fault, but because the final page of each query is small enough to be returned inline to
the model instead of to a file our loader can read. A plain HTTP client has no such problem.

This is unchanged from July: read-only, same scope as the current community token, one daily run,
a few hundred requests/day worst case. `partners_list`, `partners_get`, `partner_reviews_list`,
`partner_offer_clicks_list`. No write scopes.

Everything else in this document is a nice-to-have next to this one.

---

## Request 3 · 🔴 The two unfetchable records — not fixed, and the failure has changed shape

Both bracketed windows from the original doc still fail. They no longer time out; they now return
**truncated JSON**:

| Window | Result |
|---|---|
| `created_after=2023-10-04T10:23:30Z` · `created_before=2023-10-04T10:24:00Z` | `Invalid JSON: EOF while parsing a string at line 1 column 1044` |
| `created_after=2024-08-13T07:33:00Z` · `created_before=2024-08-15T08:22:17Z` | `Invalid JSON: EOF while parsing a string at line 1 column 3095` |

**Control, run immediately afterwards** — the adjacent window
`created_after=2023-10-04T10:24:00Z` · `created_before=2023-10-04T10:30:00Z` returned **5 partners
instantly**, including *Outlinematic* (`created_at 2023-10-04T10:24:26.970Z`), the exact neighbour
named in the original doc. So the fault is still those two records specifically, not the date range,
the endpoint, or the tier.

**Why the new symptom is good news:** *"EOF while parsing a string"* means the response is being cut
**mid-string**, at a deterministic offset, rather than never arriving. That is consistent with the
oversized-or-corrupt `description` we suspected in July, and it should be reproducible server-side
by serializing those two rows in isolation.

**Ask:** find the two rows by that method and either repair the field or soft-delete them. `id` and
`name` are still unknowable from outside — no response carrying either record has ever arrived.

---

## Request 2 · 🟠 Deletions — still unverified from our tier

`include_deleted: true` returns `Bad Request Exception`. We cannot tell whether that is the tier
rejection described in the original doc or a parameter-shape problem on our side, so we are not
claiming it as a gap — only that after two attempts we still cannot see a deletion.

**Ask:** confirm whether a deleted partner is discoverable at community tier by any means. `id` +
`deleted_at` in the `updated_after` delta is all we need; we do not need `include_deleted` itself.
Without it our copy accumulates rows that no longer exist upstream and nothing signals it.

---

## Request 7 · 🟠 NEW — `sort` breaks pagination

Identical query, identical window, different `sort`:

| Query | Records returned |
|---|---|
| `updated_after=2026-08-23` (default sort) | **94** |
| `updated_after=2026-08-23`, `sort=name:asc` | **42** |

The sorted variant terminates early with `has_more: false` while less than half the matching rows
have been returned. The cursor appears to be keyed on the default ordering and to stop making sense
once a different sort is applied.

**Consequence:** a paginated sorted query silently returns a subset. Nothing in the response says
so — `has_more: false` is indistinguishable from a complete result. Any integrator paging with a
`sort` will under-read and never know.

**Ask:** make the cursor consistent with the active sort, or reject `sort` together with `cursor`
so the failure is loud instead of silent. We hit this while working around the small-final-page
problem in Request 1, and we now treat only the **first** page of any sorted query as trustworthy.

---

## Request 6 · 🟢 Duplicates — ours to fix, recorded so it is not waiting on you

*Riverbend Consulting* still exists as two separate published records. This was always MDS-side
cleanup; it is listed here only so the original Request 6 can be closed on your end.

---

## Acceptance — how we would verify each remaining item

1. A PAT pulls every published partner over plain HTTP, paginated, in one pass, no model tokens.
2. A deleted test partner appears in the next `updated_after` delta with `deleted_at` set.
3. Both bracketed windows return rows like any other, or `total` drops accordingly.
4. `partners_list?sort=name:asc` paged to exhaustion returns the same record count as the default
   sort over the same window.
