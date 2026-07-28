> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Member fields — review sheet for Andy

**Purpose:** decide, field by field, what Olivia may SHARE with another member. Built 2026-07-26 from
the live `digest.member_attributes` table. System/plumbing columns are excluded (listed at the bottom
so you can see nothing was hidden).

**Coverage = % of the 608 rows whose `membership_status = 'Current Member'`** — not % of all 5,737
rows. That distinction matters: 4,421 rows have a BLANK status and are near-empty ghosts, which is why
an earlier count of mine said "13% have a title" when the real figure for actual members is 57%.

**How to use:** put `YES` or `NO` in the Decision column. Anything marked YES gets added to
`member_card` + the leak gate in one change.

> ✅ **Dedup rule (Andy, 2026-07-26 — confirmed live, ALREADY ENFORCED).** Duplicates are EXPECTED.
> Resolve them by `AT Database Status`: the real row has a non-empty status, the ghost is blank.
> Verified on Adam Ackerman (Current Member → Orange Co Chapter / CEO / 2015; blank twin → all null).
> Applying the rule drops duplicate names from **304 → 15**.
>
> **`member_card` already does this** — it filters
> `membership_status in ('Current Member','New Member','Pending Group Entrance','Current Member- Not Renewing','Staff')`,
> so the 4,421 blank ghosts never reach a profile lookup. Live check: `member_card('Adam Ackerman')`
> returns exactly ONE row, the populated one (Costa Mesa · Orange Co Chapter · 1-5M).
> *(An earlier draft of this file claimed the filter was missing. That was wrong — corrected here.)*

---

## Already shared today (Eugene FINAL, 2026-07-20)

| Field | Coverage | Notes |
|---|---|---|
| `full_name` | 100% | |
| `city` / `state` | 98% | already public via matches |
| `rev_band` | 88% | **band only** — exact revenue never |
| `main_niche` | 76% | |
| `expertise` | 86% | |
| `fun_fact` | 52% | |
| `chapter_affiliation` | 100% | public per 2026-07-22 ruling |
| About Me · Facebook Profile Link | — | held outside this table |

---

## PENDING YOUR DECISION — the three that caused eval failures

| Field | Coverage | Example | Why it came up | Decision |
|---|---|---|---|---|
| `title` | **57%** | Dana E. Mavros → "President" | Eval asks "what is X's title" — currently refused | |
| `started_year` | **57%** | Adam Ackerman → 2015 | "What year did X start their business" | |
| `business_model` | **91%** | "Private Label", "OEM Design & Development" | "What business model does X run" | |

Data verified correct against eval ground truth for both examples.

---

## NOT currently shared — worth a decision either way

| Field | Coverage | What it is | My read | Decision |
|---|---|---|---|---|
| `country` | 99% | country | Low risk — city/state already public | |
| `categories` | 95% | product categories (array) | Low risk — close to `main_niche`, already public | |
| `sku_count` | 96% | number of SKUs | Business-size signal, adjacent to revenue | |
| `brands_count` | 96% | number of brands | Same | |
| `large_sku` | 100% | derived flag | Derived from `sku_count` — follow that decision | |
| `channel_mix` | 92% | Amazon / Walmart / DTC / TikTok | **Currently a structural refusal.** But "who sells on TikTok" already works via match — worth reconciling | |
| `tiktok_seller` | 100% | derived flag | Derived from `channel_mix` — follow that decision | |
| `sells_supplements` | 100% | derived flag | Derived from `categories` | |

---

## Recommend NO — do not surface

| Field | Coverage | Why |
|---|---|---|
| `age_band` | 92% | Age. Currently refused; keep refused. |
| `under_30` | 92% | Derived from age — same. |
| `membership_status` | — | **NEVER.** Values include `Removed - For Cause`, `Declined Applicant`, `Dead Lead`. Telling one member why another left is the single worst leak available here. It is a JOIN KEY ONLY. |

---

## Excluded as system/plumbing (listed for completeness)

`at_member_id` (Airtable record key) · `chapter_ids` (machine key behind `chapter_affiliation`,
immune to name drift) · `provenance` (jsonb audit of where each value came from) · `refreshed_at`
(sync timestamp).

---

## Status-value reference (why the dedup rule works)

Of 5,737 rows only **1,316** carry a status; 4,421 are blank ghosts.

| Status | Rows | has title |
|---|---|---|
| Current Member | 608 | 57% |
| Removed - Canceled Membership | 278 | 68% |
| Removed - For Cause | 142 | 32% |
| New Member | 105 | 96% |
| Removed Applicant | 69 | 32% |
| Staff | 29 | 7% |
| *(11 smaller statuses)* | 85 | — |

Note "Current Member- Paused", "Current Member- Not Renewing", "Current Member- Soft Removed" and
`Declined Applicant ` carry **trailing/inconsistent spacing** in Airtable — match on prefix, never on
exact string equality.
