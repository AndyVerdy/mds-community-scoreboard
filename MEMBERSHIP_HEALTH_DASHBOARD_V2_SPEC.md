> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Membership Health — Dashboard v2 Spec (Anita)

**NEXT TASK for `project_mds_membership_reporting`.** Source: Andy/Anita PDF `Past Due & Churned Dashboard .pdf` (2026-07-28, originally in ~/Downloads — screenshots confirmed readable). Builds on the live **"Membership Health"** interface `pbdbqK539jXDxiNWG` (base `appou5JVr0WIrioWS`). Defines **two** dashboards.

> ⚠️ Interface pages are edited **in the Airtable UI** (the MCP can only create/delete a page → editing = new URL). Add sections in the `/edit` builder; draft-until-Publish keeps the URL stable.

---

## Dashboard 1 — SUMMARY (period rollups) — NEW
A month + year-to-date rollup dashboard. Needs monthly *history* of failures/recoveries → sourced from the **Stripe year backfill** (decision #2). *(Earlier drafts called this a "Monthly KPI Snapshot table" — that name was mine, NOT in Anita's spec and never asked for. Dropped. Determine the actual store when building.)*

**Section 1 — High-level, this month:**
- Total Past Due Revenue $ Lost this month
- Total Removed/Canceled Revenue $ Lost this month
- Total Recovered Revenue $ (anywhere recovered)
- **Total of the three**
- \+ Total Revenue $ Lost *coming up* (from Current Member — Not Renewing)

**Section 2 — Past Due · Failed this month** (extend the existing "Failed this month — RAW" section: 11 / $5,008.33):
- **Lost:** still-outstanding count + Monthly Total Revenue Lost = **sum of Past Due Amount**. *(PDF screenshot: "Still Outstanding — 4 members (as of 7/27)", cols Name · Billing Cycle · Failed Payment Date · Days Past Due · **Actual Amount Owed**; Total At Risk $15,488.)*
- **Recovered:** recovered count + Monthly Total Revenue Recovered (sum of past-due amount that recovered) + **Average Days to Recovered**. *(screenshot: "Recovered — 4 members", + Recovered Date · Time to Recover; Total Recovered $11,992.)*
- **Total:** Total Month Revenue at Stake (Lost + Recovered) + total members in Lost+Recovered. *(screenshot: "Total July revenue at stake: $27,480".)*

**Section 5 — Failed this YEAR (YTD):** month-by-month (May · June · July · …), each with: Number Lost · Total Revenue Lost · Number Recovered · Total Revenue Recovered · Total at Stake for the month. → **needs monthly history** from the Stripe year backfill (decision #2).

---

## Dashboard 2 — PAST DUE (live) — ENHANCE existing "Now — live" (`pagxOoDRO6udzzqjC`)
- **Section 1 — Past due, live right now** (exists; count 5 / MRR $1,689.67): add **Monthly Total Revenue At Risk** (sum of Past Due Amount). Grid add: **Past Due Amount** · **Stripe ARR** · **Issue Type** [Credit Card Declined / Insufficient funds / Expired Card] · **Bucket**.
- **Section 2 — Churned (Stripe unpaid, not removed), live** (exists; 2 / $957.83): add Monthly Total Revenue Lost (sum Past Due Amount). Grid add: Days Past Due · Past Due Amount · Stripe ARR.
- **Section 3 — Removed in AT but Active in Stripe:** **RENAME the "Billing mismatch" section → "Removed in Airtable, but Active in Stripe"** (exists as the Billing Mismatch flag).
- **Section 4 — Current Not Renewing** (exists; 6 / $2,305.67): **rename "MRR at risk" → "Total Revenue at Risk."** Grid add: **AI Engagement Summary** · **Member Scorecard %** · **Renewal Amount** · **Days until Renewal** · **Renewal Date**.

---

## New data / engineering needed (before/with the build)
1. **Monthly history** for Dashboard 1's rollups — comes from the Stripe year backfill (decision #2). Decide the store when building (compute from the Stripe failed/recovered date + amount fields, vs a small monthly rollup). NOT a "KPI" table — that was invented framing, removed.
2. **Issue Type / decline reason** — NEW field: pull Stripe charge failure reason (`charge.failure_code` / `outcome.reason`) → Credit Card Declined / Insufficient funds / Expired Card. Needs ingestion work; **not in AT today**.
3. **Past Due Amount** on dashboard grids = `Stripe Amount` (Members) / `Amount Owed` (snapshot, `fld…` created this session) — already exists, just surface + sum it.
4. **Renewal Amount / Days until Renewal / Renewal Date** = `Stripe Next Invoice Amount` / `Stripe Next Invoice Date` (valid renewal date for active/good-standing subs only).
5. **AI Engagement Summary / Member Scorecard %** — cross-ref the FB-engagement / scorecard system (separate project).
6. **Average Days to Recovered / Time to Recover** = `Recovered Date (Stripe)` − `Failed Payment Date (Stripe)`.

*The PDF's screenshots are readable and show the exact tiles/columns Anita wants — mirror them.*
