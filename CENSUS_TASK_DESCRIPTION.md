> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Task: Rebuild the Annual Census to match New Member Application v3

## Issue
We run two legacy censuses, built years ago with dated questions, matrix grids, and unverified revenue:
- **[Standard - Annual Census](https://admin.typeform.com/form/I409BFlj/create)**
- **[MDSonly - Annual Census Master](https://admin.typeform.com/form/DXs5mhZn/create)**

Meanwhile the **[New Member Application v3](https://admin.typeform.com/form/FsVHzNN9/create)** modernized how we ask business & revenue questions. The censuses don't match that logic. Goal: rebuild them to the v3 standard. **Starting with the Standard Annual Census; MDSonly is next.**

## Research
Compared every legacy census question against the three newest forms:
- **[New Member Application v3](https://admin.typeform.com/form/FsVHzNN9/create)**
- **[Honorary Member Application](https://admin.typeform.com/form/mkUJqsfM/create)**
- **[MDS Summit Singapore 2026 – Check-In](https://admin.typeform.com/form/w3kCjPAK/create)**

Comparison tables (repo, `/Users/Born/Scorecard/`):
- `CENSUS_CROSSWALK.md` — every legacy question → new question → Airtable field, with real response rates
- `CENSUS_VS_REFERENCE_FORMS.md` — census questions vs the 3 newer forms (where a fresher version exists)
- `CENSUS_STANDARD_FIELD_MAP.md` — each question → its Airtable Forms field (sync map)
- `CENSUS_NEW_FORM_DESIGN.md` — new form structure + logic jumps
- `CENSUS_REVIEW_NOTES.md` — 19-item review punch-list

## New draft form
**[MDS Annual Census 2026 (v2)](https://admin.typeform.com/form/NENqozp9/create)** — ~70 questions, all optional while testing.

## Major changes
- **Matrix questions killed.** The channel-revenue grid → numeric % per channel with a live running total, gated so we only ask about channels you actually sell on (v3 pattern). *(MDSonly has 7 matrices — the big lift there.)*
- **Revenue routed to the shared pipeline.** Census revenue will feed the **same revenue field the application uses** (so "Most Recent Revenue" reflects it), replacing the old standalone census revenue field. Reported figure only — no screenshot/verification card for the census.
- Adopted fresher v3/Honorary wording + option sets (official role, "total revenue over past 12 months," business models, competitive advantages, activities).
- Restored missing question **descriptions + rating-scale labels** from the legacy form.
- Gated presumptive questions: "Do you have kids?" before kids Qs; "Do you attend Chapter events?" / "participate in a Squad?"; only-selected channels.
- Dropped redundant items (categories vs. main niche; stray "what have you been up to").

## Questionable decisions (need a call)
- **Member benefits: 11 separate rating questions vs. the old single ranking.** The drag-ranking was unusable on mobile, so we split it into 11 individual ratings in one section. Trade-off: keeps a score per benefit + year-over-year tracking, but adds length. Final scale format TBD (defaulted 1–5). **← main open question.**
- **Tool questions** (split-testing / PPC / reimbursement / 3PL / HR): vendor lists may be outdated — **@Eugene to confirm or refresh** the options.

## Next
Confirm the above → wire the Airtable sync (member-match by email → Members DB, revenue → shared pipeline) → restore required fields → publish.
