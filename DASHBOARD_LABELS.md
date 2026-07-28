# Membership Health dashboards — every title + description

Paste into the AT interface builder. Each **group**, each **card** (number tile), and each **grid** gets a title + description.

---

# DASHBOARD 1 — "Summary — month & year"  (`pagRUMnKpYEmjepVk`)

## GROUP 1 — This month — Total revenue moved
**Group description:** The headline number for the month — how much recurring revenue was *in motion* (jeopardized) this calendar month. Sums three buckets: still-outstanding past-due (LOST), removed/canceled, and recovered. It is a SUM (size of the problem), NOT a net — recovered money is added, not subtracted. Resets on the 1st.
- **Card — Total of the three** · *desc:* Sum of amount owed (Stripe Amount = actual per-cycle charge, not MRR) across everyone in this month's three buckets: still-outstanding + removed/canceled + recovered. Source: the "$ At Stake This Month" helper field. Recomputes live.

## GROUP 2 — Failed this month — RAW
**Group description:** Every membership payment that FAILED this calendar month — the raw reconciliation list, blips included (even same-day auto-retries). This is the superset; the judged split into LOST vs Recovered is the next two groups. Source: Stripe Failed Payment Date, refreshed daily.
- **Card — Failures this month** · *desc:* Count of members whose Stripe payment failed this calendar month. Includes ones that later recovered.
- **Card — Actual $ at stake** · *desc:* Sum of amount owed (Stripe Amount = actual per-cycle charge, NOT MRR). An annual member counts their full annual charge.
- **Grid — Who failed this month** · *desc:* One row per failed member, most recent failure first. Name · AT status · Stripe status · billing cycle · failed date · days past due · amount · recovered date (if it cleared).

## GROUP 3 — Still Outstanding — LOST
**Group description:** The subset of this month's failures that have NOT yet recovered — money currently at risk. Failed Payment Date this month AND Recovered Date empty. Live.
- **Card — Still outstanding** · *desc:* Count of this-month failures not yet recovered.
- **Card — Monthly revenue at risk** · *desc:* Sum of amount owed for the still-outstanding members.
- **Grid — Who's still outstanding** · *desc:* Most days-past-due first. Name · AT status · Stripe status · billing cycle · failed date · days past due · amount.

## GROUP 4 — Recovered this month
**Group description:** Failed payments that CLEARED this calendar month (Recovered Date this month), regardless of when they first failed. Includes same-day blips. Live.
- **Card — Recovered** · *desc:* Count of members whose failed payment cleared this calendar month.
- **Card — Revenue recovered** · *desc:* Sum of amount owed that recovered.
- **Card — Avg days to recover** · *desc:* Average Time to Recover (Recovered Date − Failed Payment Date, in days) across recovered members.
- **Grid — Who recovered** · *desc:* Most recent recovery first. Name · AT status · Stripe status · billing cycle · failed date · recovered date · time to recover · amount.

## GROUP 5 — Removed / Canceled this month
**Group description:** Members whose AT status became "Removed - Canceled Membership" this calendar month — fully churned, revenue lost. Live.
- **Card — Removed / Canceled this month** · *desc:* Count of members canceled this calendar month.
- **Card — Revenue lost (canceled)** · *desc:* Sum of their amount owed.
- **Grid — Who canceled** · *desc:* Most recent removal first. Name · AT status · Stripe status · plan · amount · removed date.

## GROUP 6 — Upcoming revenue at risk — Not Renewing
**Group description:** Active paying members in good standing who told us they will NOT renew at term end — the save-opportunity list. Membership in this list relies ENTIRELY on the AT Database Status field being kept current (stale statuses leak in). Live.
- **Card — Not renewing** · *desc:* Count with status "Current Member- Not Renewing".
- **Card — Total revenue at risk** · *desc:* Sum of amount owed (annual charge) — revenue that lapses if they don't renew.
- **Grid — Who's not renewing** · *desc:* Soonest term-end first. Name · AT status · Stripe status · renewal/term-end date · days until renewal (negative = term already passed) · amount · engagement score.

## GROUP 7 — Payment FAILURES this year — by month
**Group description:** Every membership invoice that FAILED in 2026, one row per failed invoice (a member appears multiple times if they failed repeatedly). Source: Stripe invoices, backfilled daily into the Payment Events table. Grouped by month for the trend.
- **Card — Failed payments (2026)** · *desc:* Count of failed invoices this year (invoice-level, not member-level).
- **Card — $ failed (2026)** · *desc:* Sum of the failed invoice amounts.
- **Grid — Failures by month** · *desc:* Grouped by month (newest first) with a $ subtotal per month. Event date · amount · Stripe customer.

## GROUP 8 — Payment RECOVERIES this year — by month
**Group description:** Failed invoices that LATER cleared, one row per recovered invoice. Compare to Failures above — the gap (failures − recoveries) = invoices/money never recovered this year.
- **Card — Recovered payments (2026)** · *desc:* Count of recovered invoices this year.
- **Card — $ recovered (2026)** · *desc:* Sum of the recovered invoice amounts.
- **Grid — Recoveries by month** · *desc:* Grouped by month with a $ subtotal. Event date · amount · Stripe customer.

---

# DASHBOARD 2 — "Past Due — live"  (`pagupx2DeEyVOgicc`)

## GROUP 1 — Past due — live
**Group description:** Members whose payment failed and Stripe is STILL retrying — recoverable right now. Excludes anyone already Removed in Airtable. Live (recomputed each run).
- **Card — Past due** · *desc:* Count with Stripe status "past_due", not Removed in AT.
- **Card — Total Revenue At Risk** · *desc:* Sum of amount owed (actual per-cycle charge, not MRR).
- **Grid — Who's past due** · *desc:* Most days-past-due first. Name · AT status · Stripe status · days past due · bucket · plan · amount · Stripe ARR · issue type (decline reason) · failed date · Stripe link.

## GROUP 2 — Churned — Stripe unpaid, still not removed
**Group description:** Stripe retried ~30 days and gave up (involuntary churn) — these members have ALREADY stopped paying but are still not marked Removed in Airtable. Needs AT cleanup. Live.
- **Card — Churned (unpaid)** · *desc:* Count with Stripe status "unpaid", not yet Removed in AT.
- **Card — Total Revenue Lost** · *desc:* Sum of amount owed across them.
- **Grid — Who's churned but not removed** · *desc:* Name · AT status · Stripe status · days past due · plan · amount · Stripe ARR · failed date · Stripe link.

## GROUP 3 — Removed in Airtable, but Active in Stripe
**Group description:** Marked Removed in Airtable but Stripe is STILL actively billing them >$0 — money leaking after removal. Fix: cancel the sub in Stripe or correct the AT status. Re-checked live every run (self-clears when fixed).
- **Card — Removed in AT, Active in Stripe** · *desc:* Count flagged by the Billing Mismatch check.
- **Card — Still billing / mo** · *desc:* Sum of what's still being charged after removal.
- **Grid — Fix these** · *desc:* Name · AT status · Stripe status · plan · amount · removed date · Stripe link.

## GROUP 4 — Current — Not Renewing
**Group description:** Active paying members who told us they won't renew at term end — save-opportunity list. Relies entirely on the AT Database Status field being current. Live.
- **Card — Not renewing** · *desc:* Count with status "Current Member- Not Renewing".
- **Card — Total Revenue at Risk** · *desc:* Sum of amount owed (annual charge) that lapses if they don't renew.
- **Grid — Who's not renewing** · *desc:* Soonest term-end first. Name · AT status · Stripe status · renewal/term-end date · days until renewal (negative = already passed) · amount · engagement score.
