> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDSonly Census — Analysis (for the merge)

**[MDSonly - Annual Census Master](https://admin.typeform.com/form/DXs5mhZn/create)** — 32 questions, **7 matrices**, 1,060 responses. Deep ops/supply-chain/team form. Response % = share of the 1,060 that answered.

This form is almost entirely **operational and census-unique** — the reference forms (App v3 / Honorary / Summit) don't cover any of it, so there are no "fresher version" adoptions here (unlike Standard). The work is: **kill/trim the 7 matrices**, **dedupe the few overlaps with the [Standard census](https://admin.typeform.com/form/I409BFlj/create)**, and **tag stable vs. annual** for Eugene's screening model.

## Per-question table

| # | MDSonly question | Type | Resp % | Overlaps Standard? | Stable/Annual | Recommendation |
|---|---|---|---|---|---|---|
| 1 | Full name | short_text | 86% | **YES** | — | **DEDUPE** — single instance in merged form |
| 2 | Email | email | 86% | **YES** | — | **DEDUPE** |
| 3 | Current involvement in e-commerce | MC (7) | 62% | no | Stable | KEEP — filters exited members |
| 4 | Warehousing types (FBA/3PL/In-house) | MC multi | 87% | no | Stable | KEEP |
| 5 | **Marketing initiatives** (8 ch. × in-house/agency/freelancer) | **MATRIX** | 98% | no | Stable | ⚑ trim rows (drop TV/Podcast/Radio — mostly N/A); matrix strategy below |
| 6 | **Business ops handling** (8 areas × same) | **MATRIX** | 98% | no | Stable | ⚑ keep, trim; matrix strategy below |
| 7 | How do you source products? | MC multi | 87% | no | Stable | KEEP |
| 8 | **Manufacturing locations** (9 countries × %) | **MATRIX** | 98% | no | Stable | ⚑ simplify → top-5 countries + Other; convert to %-per-selected |
| 9 | Other manufacturing locations (cond.) | long_text | 20% | no | Stable | KEEP (conditional on "Other") |
| 10 | Avg cost per CBM (last 12mo) | number | 61% | no | **Annual** | KEEP |
| 11 | Avg production time | number | 61% | no | Annual | KEEP |
| 12 | Avg shipping time | number | 61% | no | Annual | KEEP |
| 13 | Customer orders shipped | number | 98% | no | Annual | KEEP |
| 14 | Containers imported | number | 98% | no | Annual | KEEP |
| 15 | Products launched last 12mo | number | 98% | no | Annual | KEEP |
| 16 | New products planned next 12mo | number | 98% | no | Annual | KEEP |
| 17 | **Selling focus next 12mo** (11 ch. × intent) | **MATRIX** | 61% | no | Annual | ⚑ simplify channels; matrix strategy below |
| 18 | Full-time W-2/1099 employees | number | 98% | no | Annual | KEEP |
| 19 | Part-time contractors | number | 98% | no | Annual | KEEP |
| 20 | VAs / offshore employees | number | 98% | no | Annual | KEEP |
| 21 | Staff locations (10 countries) | MC multi | ~64% | no | Stable | KEEP → simplify (drop Australia 1% / Africa 2%) |
| 22 | **Team positions & pay** (12 roles × pay bands) | **MATRIX** | 98% | no | Stable | ⚑ simplify → key roles; matrix strategy below |
| 23 | Other essential positions? | short_text | 98% | no | Stable | **DROP** — mostly Yes/No noise (question invites y/n, not a role) |
| 24 | #1 team-building suggestion | long_text | 98% | no | Annual | KEEP |
| 25 | Use EOS/Traction? | MC (2) | 98% | no | Stable | KEEP |
| 26 | How do you implement EOS? (cond.) | MC (3) | 31% | no | Stable | KEEP (gated on EOS=Yes) |
| 27 | **Business change YoY** (6 metrics × % bands) | **MATRIX** | **20%** | no | Annual | ⚑ **DROP or trim to Revenue/Margin** — only 20% fill it |
| 28 | **Revenue % by business category** (10 cats × % bands) | **MATRIX** | **20%** | no | Annual | ⚑ **DROP** (or power-user only) — 20%, very complex |
| 29 | New business venture? | long_text | 21% | no | Annual | **DROP** — 21%, not actionable |
| 30 | Currently investing in? | long_text | 21% | no | Annual | **DROP** — 21% |
| 31 | How can MDS be a better resource? | long_text | 21% | **YES** (Standard 86%) | Annual | **DEDUPE** — use Standard's version |
| 32 | Gsuite email (doc access) | email | 100% | no | — | KEEP (operational) |

## Matrix strategy (the 7)
- **DROP 2 low-signal (20%):** Business-change YoY (Q27) and Revenue-%-by-category (Q28) — poor response, high complexity. (Keep a trimmed 3-metric YoY only if leadership wants it.)
- **The 4 high-response 2-D matrices** (Marketing Q5, Ops Q6, Team-pay Q22, Manufacturing Q8) are genuinely two-dimensional (row × in-house/agency/pay-band/%). They don't linearize into single questions without exploding the count (8+8+12+9 = 37 sub-questions). Recommendation: **keep them as matrices but trim each to high-signal rows** — killing the *grid UX* fully (like we did for the channel %) isn't clean here. **This is the main open decision for MDSonly.**
- **Selling-focus (Q17, 61%):** simplify to the ~5 channels that matter (Amazon US/EU, DTC, Walmart, Wholesale); keep the intent columns.

## Merge notes (MDSonly → the new Standard-based form)
- **Dedupe (skip in merge):** Full name, Email, "How can MDS be better" (Standard's versions win — higher response, better wording).
- **Everything else is additive** — MDSonly brings the ops/supply-chain/team depth the Standard census doesn't have.
- **Fits Eugene's screening model cleanly:** the *stable* blocks (warehousing, sourcing, manufacturing, team structure/pay, EOS, staff locations) gate behind "has your ops/team changed?"; the *annual* blocks (CBM/times, orders, containers, products launched/planned, employee counts, selling focus) always show.
- After dropping (Q23, Q27, Q28, Q29, Q30) + deduping (Q1, Q2, Q31): MDSonly contributes **~24 net-new questions** to the merged form.
