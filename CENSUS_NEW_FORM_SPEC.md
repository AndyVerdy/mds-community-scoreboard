> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# New MDS Census — Build Spec (v0.1 — for sign-off)

Rebuild of the census, app-v3 playbook. **Legacy forms untouched.** This spec = the **Standard-census content** cleaned; MDSonly-unique questions fold in as a later pass.

## Locked decisions
- One new merged form; start with Standard content.
- **Sync via Make** (not Typeform's native integration). Member matched by a **hidden `member_id`** carried in a personalized link — **not** the typed email (`if(answer; answer; hidden.member_id)` coalesce + `xxxxx` guard, like app v3).
- Revenue → write **`(NEW) Unverified Revenue`** + stamp `Form ID` + `Date Submitted` + link Member. **No screenshot, no verify card.**
- **Kill matrices.** All logic jumps **forward only**.
- New form writes to the **same Forms fields** (`tblblwPcgqhkPTVec`) per `CENSUS_STANDARD_FIELD_MAP.md`.

## Proposed section flow
0. **Hidden** (from link): `member_id`, `email` (fallback), `form_source`.
1. **Identity** — confirm name + email (prefilled).
2. **Business snapshot** — models · # brands · brand name(s) · # products · categories · main niche.
3. **Revenue** — TTM · projected FTM · channel % (matrix killed, see below) · plan-to-sell · sold?→when?→still-have-revenue? (conditional).
4. **Tools** — split-testing · PPC · reimbursement · 3PL · HR (top 5 + other).
5. **Growth** — goals · biggest challenge · growth plan · best thing that worked · most impactful tool · industries >20% time.
6. **MDS feedback** — rank benefits · call topics · NPS · community impact · how-to-improve · UX rating · tech enhancement · referrals.
7. **Programs** (gated) — Chapters / Programs / Squads: involved?→rate→see-more.
8. **Classification** — activities that describe you → explain (conditional).

## Question decisions (from `census_form_comparison.csv`)

**KEEP (→ same Forms field):** name, email, business models, # brands, brand name(s), # products, categories, main niche, TTM revenue, projected FTM, plan-to-sell, sold?/when/still-have, split-testing, PPC, reimbursement, 3PL, most-impactful tool, goals, biggest challenge, growth plan, best-thing, industries-20%, rank benefits, call topics, NPS, MDS impact, how-to-improve, UX rating, tech enhancement, referrals, chapters/programs/squads (gated), activities + explain.

**SIMPLIFY:**
- **Channel revenue matrix → killed** (see next section).
- **HR/hiring** 10 options → top 5 + Other.

**REMOVE (app already captures once, or low-value):**
- Formal title, day-to-day responsibilities, strongest expertise, competitive advantage, other knowledge-bases/groups — *one-time; the application owns these.*
- Kids age ranges, branding-feedback text — *low response.*
- **Borderline (confirm):** kids count (troll values), visual-branding rating (not annually critical).

## Channel revenue — killing the matrix
Today: 1 matrix, 9 channel rows, bucket values → 9 `… & % of Revenue` fields.

- **Option A (recommended — same AT fields):** replace the matrix with **5 single-select bucket questions** — Amazon US · Amazon EU · Walmart · DTC/Own Website · Wholesale — writing to the existing `… & % of Revenue` fields. Drop the rarely-used rows (Amazon Canada, Other Amazon, Wayfair/Target, Big-Box vs Indie split — all 70%+ "N/A").
- **Option B (app-consistent):** numeric **%** per channel with a live running-total (`pct_total`) + "Other %" remainder — needs new `% (raw)` AT fields like the app.

## Sync design (Make, mirrors scenario 4784286)
1. **Trigger:** new-submission webhook on the new form.
2. **Member match:** search Members by `hidden.member_id` (fallback typed email); skip if `xxxxx`.
3. **Create Forms row:** `Form ID` = *new value TBD* · `Date Submitted` · link Member · write mapped fields.
4. **Revenue:** `(NEW) Unverified Revenue` (not `Total TTM Revenue`) → flows to Most Recent Revenue as reported.

## Open for Andy
1. **Channel-% format** — Option A (same fields, buckets) or B (app-style numeric %)?
2. **New `Form ID` value** — e.g. "Annual Census 2026"? (drives Most-Recent-across-forms logic)
3. **Confirm REMOVE list** — esp. kids-count + visual-branding rating.
4. **Personalized link distribution** — how do members receive their `member_id` link (email? app?)?
