> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS → MDS: Partners data integration request

From: Andy (MDS) · For: Andrii (GroupOS MCP/API) · Date: 2026-07-21

## Context (why we ask)

MDS runs "Olivia" — a WhatsApp assistant for members. One of her data sources is the
**partner directory** (published partners: name, description, offer, categories, rating,
reviews, claim counts). Her runtime is n8n → Postgres: retrieval happens in SQL at answer
time (member-entitlement gating, full-text search with e-commerce synonyms, review joins,
per-name dedupe, <1s). That runtime **cannot call the MCP** — the MCP lives inside a Claude
session. So we keep a **synced read copy** of the published directory in our Postgres and
query that.

The copy is fine for us (POC ruling: it stays). The problem is **how it syncs**: today the
only read path is MCP → model context, which cost ~1.5M tokens and ~2h for a one-time pull
of 488 partners, and it goes stale with no signal when a partner is edited/paused.

We need a cheap, token-free sync path — not a new architecture.

## Requests

### 1. Service token (PAT) for plain REST — the main ask
A token with the same **read scope** as the current community MCP token
(community `67011d987a2a81b28438a3d8`), usable from a cron/CI via plain HTTP:
`partners_list`, `partners_get`, `partner_reviews_list`, `partner_offer_clicks_list`.
This alone turns our sync into a ~2-minute daily curl job with zero model tokens.
Read-only is all we want; no write scopes. Expected volume: one daily sync run,
worst case a few hundred requests/day — nothing continuous.

### 2. Deltas that include status transitions
`partners_list?updated_after=X` exists and covers edits. What deltas cannot show today:
- **published → paused/draft** transitions (the row just vanishes from the filtered list);
- **deletions** (invisible without `include_deleted`, which is rejected for our token tier).

Ask: make `updated_after` return rows whose **status changed** (with the new status), and
expose deletions minimally (`id` + `deleted_at` is enough). Then a copy converges daily
without full re-pulls. Webhooks would be nicer but are NOT required — daily delta polling
is enough for partner-directory churn.

Same question for **reviews**: `partner_reviews_list` is per-partner only, so finding new
reviews means re-polling every partner that has any (~110 calls/day today, growing). Either
a `created_after` filter on it, a community-wide reviews feed with `created_after`, or a
guarantee that a new review bumps the partner's `updated_at` (then the partner delta is the
trigger) — any one of the three works.

### 3. Bug: two unfetchable partner records (reproducible)
Any `partners_list` page containing either of these two records **times out
deterministically** (7/7 attempts, limits 15/10/2, both sort directions), while identical
queries excluding them return in seconds. Bracketed by `created_at`:

| # | created_at window | neighbors |
|---|---|---|
| 1 | 2023-10-04 between 10:23:30Z and 10:24:00Z | right after "Onsite Support by Threecolts" (10:22:10.829Z), before "Outlinematic" (10:24:26.970Z) |
| 2 | 2024-08-13 07:33:00.766Z → 2024-08-15 08:22:17.000Z | immediately after "Teamwork.com" (08:22:17.162Z) in created_at:desc order |

Id/name are unknowable from outside (no response carrying the record ever arrives).
Suspected oversized/corrupt description field. These two also broke MCP paging — we had to
bisect around them with date bounds. Published count: API total says 488; only 486 are
fetchable.

### 4. Categories endpoint
`category_ref_ids` / `subcategory_ref_ids` are opaque ObjectIds; no endpoint resolves them
to names. Ask: a `partner_categories_list` (id → name, parent) for the community. (Today we
reverse-engineer names by joining partner names against our Airtable — works for 97% but
it's a hack.)

### 5. Partner contact_info is stripped from the read API (data exists!)
`contact_info` comes back with **every subfield null on all 486 published partners** —
but the ADMIN panel shows the fields populated. Verified example: **G10 Fulfillment**
(`6a5dfe668a427b8944ac8cb6`) — admin shows contact name, phone, email,
`https://g10fulfillment.com/`, Facebook and LinkedIn; the API returns
`contact_info: {contact_name: null, phone_number: null, email: null, website: null,
facebook: null, linkedin: null}`. Either the community-tier read strips it or the
serializer never populates it.

Ask: expose at least **website / facebook / linkedin** on the community read (those are
member-useful and shown to members anyway). If contact name / phone / email are hidden
by design for partner privacy, that's fine — we only need the three public links.

### 6. Nice-to-haves (not blocking)
- The member-facing page URL (`https://app.mds.co/partners/{id}`) as an explicit payload
  field, so clients don't hardcode the URL pattern.
- Duplicate cleanup in the directory: 12 partner names exist twice as separate published
  records (e.g. Riverbend Consulting, Quiet Light, Prime Clicks, High Rock Accounting) —
  both copies are member-visible in the app.

## Explicitly NOT needed
- No realtime/webhooks (daily freshness is fine).
- No write access of any kind.
- No member-PII beyond what the current MCP token already returns.

## Acceptance (how we'd verify)
1. `curl` with the PAT pulls all published partners incl. full descriptions, paginated,
   in one pass, no timeouts.
2. Pausing a test partner shows up in the next `updated_after` delta with its new status.
3. The two bracketed records either return like any row or are gone from `total`.
4. Categories resolve to names for every `category_ref_id` in use.
5. G10 Fulfillment's read payload carries its website/Facebook/LinkedIn (matching admin).
6. A newly posted review is discoverable by one delta-shaped call (whichever variant of
   the reviews ask ships).
