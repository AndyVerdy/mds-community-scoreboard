> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# What Anita Needs — Membership Health Dashboards v2

Clean requirements from her PDF (`Past Due & Churned Dashboard.pdf`, 2026-07-28). Engineering detail = `MEMBERSHIP_HEALTH_DASHBOARD_V2_SPEC.md`. Live dashboard = interface `pbdbqK539jXDxiNWG` (base `appou5JVr0WIrioWS`).

**Split:** ✅ *Deliver now* (data exists) vs ❓ *Needs a decision* (4 open calls at the bottom).

---

## Dashboard 1 — SUMMARY (NEW: month + year-to-date rollups)

**Section 1 — This month, high level**
- Past Due $ **At Risk** (still outstanding)
- Removed/Canceled $ **Lost**
- **Recovered** $
- **Total of the three**
- \+ Upcoming $ at risk (from Not-Renewing)

**Section 2 — Failed this month, split** (actual amount owed, not MRR)
- **At Risk** (still outstanding): count + Σ amount owed
- **Recovered**: count + Σ recovered amount + **avg days to recover**
- **Total**: every failure this month + total $ at stake
- ⚖️ Rule: At Risk + Recovered + auto-resolved **must equal** the RAW failed count → *decision #1*

**Section 5 — Failed this YEAR** (month-by-month: May · June · July · …)
- Per month: # Lost · $ Lost · # Recovered · $ Recovered · $ at stake
- Needs stored monthly history → *decision #2*

---

## Dashboard 2 — PAST DUE (LIVE — enhance the existing "Now" page)

| Section | Rename | Columns to add | Status |
|---|---|---|---|
| Past due, live | — | Past Due Amount · Stripe ARR · Issue Type · Bucket | ARR ✅ · Issue Type + Bucket ❓ |
| Churned (Stripe unpaid, not removed) | — | Days Past Due · Past Due Amount · Stripe ARR | ✅ |
| Billing Mismatch | → **"Removed in Airtable, but Active in Stripe"** | none (past-due cols = N/A, they're paying) | ✅ |
| Current — Not Renewing | **"MRR at risk" → "Total Revenue at Risk"** | Renewal Amount · Days-until-Renewal · Renewal Date · AI Engagement Summary · Scorecard % | Renewal fields ✅ · Engagement + Scorecard % ❓ |

---

## ✅ Deliver now (no new plumbing)
- Every **rename** (mismatch section, "Total Revenue at Risk")
- **Past Due Amount** (= actual charge owed), **Days Past Due**, **Stripe ARR**
- **Renewal Amount / Date / Days-until-Renewal** (from Stripe Next Invoice)
- **Time-to-Recover** + average
- **At Risk / Recovered / Total** split (once decision #1 sets the blip rule)

## 🔒 Decisions (locked 2026-07-28)
1. **Blip rule → count everyone.** Same-day auto-retries still count as past-due→recovered ("past due for a minute is still past due"); the **Days Past Due** column gives context. Buckets sum to the full failed count — no 2-day exclusion here (that raw/judged split was for the Slack card, not this dashboard). Side effect: the separate "RAW 11" tile becomes redundant (At Risk + Recovered now = it).
2. **YTD history → backfill from Stripe** (May/June + full year), so "Failed this Year" shows real numbers.
3. **Issue Type → build now.** Stripe decline reason (`charge.failure_code` / `outcome.reason`) → Credit Card Declined / Insufficient funds / Expired Card. New AT field named with **"Stripe"** in the name + stamped description.
4. **Scorecard % → repurpose the legacy field.** Re-point `Member Score` (`fldvKqg4KQhRSBaz7`, only 3% filled) to the live scorecard % — link `fld3VlY5Zhf5LRalt` → `fldc4tEE6iuCsC3G2` (currently surfaced as "Member Score from scorecard" `fldB4szpjbQ9IeYb1`, 91% filled, e.g. `19.63%`). Rename properly + add description. *(Lookup reconfig = AT UI edit, not API. "Bucket" still undefined — pending Anita.)*

## 🔒 Terminology
- **At Risk** = still-outstanding past due (may still recover)
- **Lost** = removed/canceled only
- **Recovered** = failed→paid, any timeframe (same-day included)
- **$ figures** = actual charge owed (annual charge), **not** MRR; ARR is its own column
