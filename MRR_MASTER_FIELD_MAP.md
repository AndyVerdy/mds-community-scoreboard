> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MRR Master Field Map — v1.2

**Date:** 2026-06-12 (updated end of day) · **Author:** Claude session w/ Andy · **Team copy:** ClickUp doc "MDS MRR Source of Truth" (Operations space)

## Change log — 2026-06-12 (what is now LIVE)
- **4 new Members fields created** w/ descriptions, renamed to convention: `Recovered Date (Stripe)`, `Scheduled Cancel Date (Stripe)`, `Collection Paused (Stripe)`, `MRR-Effect Bucket` (human-set). Legacy `Failed Payment Date` / `Last Successful Payment` renamed with `(Stripe)` suffix. 7 reused legacy fields got descriptions.
- **n8n "MDS Stripe → AT: Payment Dates Ingestion (v1)"** (`30OyMumvZsQIAMo8`) ACTIVE — daily 12:30 UTC, 3-day window; webhook `stripe-payment-ingest` accepts `{lookbackDays:N}`. v1.1: live-sub guard (June Lai bug). v1.2: membership-products-only filter (7 product IDs). Never overwrites manual Lapsed dates. Slack summary → #automation-tests.
- **Backfills done** (90d + 400d): Last Successful Payment 323 · Failed 64 · Recovered 25 · Sched Cancel 5 · Paused 3 · Lapsed +9 (1 false positive cleared). Blank Last Successful Payment on active member = never invoiced in Stripe yet (migrated, WA history).
- **Dual-sub sweep (all 680 paid subs): 1 case account-wide** (June Lai — 2× $1,200 non-membership zombies from Nov 2024, still invoicing; *Andy/Tina to cancel in Stripe*). Make sync 4472150 confirmed: drops events for unknown sub IDs; no automation cancels replaced subs — discovery step (§3.1) is the structural fix.
- **5 fossil fields renamed `zzz DEPRECATED — …`** (New Renewal Date ×2, Year ×2, Day (Stripe)) — hardcoded 2020/21 years. **DELETION ON HOLD: Andy saw syncs touching them; team must be notified first.** Renewal date source of truth = `Stripe Next Invoice Date` (699/712 active), with `Scheduled Cancel Date (Stripe)` override.
- **Onboardings Auto-Feed** (`m94lQxcXACs6rFJx`) ACTIVE since this morning (new-member rows + Slack card).

**Open decisions:** lapse-date convention (failure date vs failure+30 — auto-writes currently +30) · `Lapsed Payment Date` rename y/n · Payment Events table delete vs keep (parked, empty) · MRR-Effect Bucket auto-suggest build · section D (first-invoice facts for Josefina) · discovery step build · field deletions after team notice.

---

*(Original plan below — sections 1–5 as reviewed by Andy.)*
**Principle (Andy):** Pull data ONCE into ONE place — the **Members table** (`tblfwOSROSHfuYUxv`, base `appou5JVr0WIrioWS`). Every other table, view, and report consumes it via links/lookups/formulas. No per-view automations.

**Population numbers** below are from a live pull of all 5,447 Members records on 2026-06-12. "Active" = 712 records with status Current Member / New Member / Pending Group Entrance / Not Renewing / Soft Removed.

---

## 1. Who asked for what (requirements → traceability)

| Requester | Ask | Where stated |
|---|---|---|
| Anita | Weekly: new past-due (moment of failure), unpaid=churn @30d, recovered (moment paid), avg days to recovery, removed/canceled in buckets w/ dates | CU 86dufq8gz thread, June 1 — *"build a report in Stripe or AT, I would need help"* |
| Eugene | MRR = active subs − intro discounts; churn = 30+ days past due; every negative-MRR event classified (cancel / coupon / prepay / transfer / refund / prorated / non-renewal); payment mechanics separated from reason codes; definitions written | CU 86dufq8gz threads May 19–23, June 1 |
| Josefina | Billed-MRR view from AT: member, date paid in Stripe, date sub started, discount $ on 1st payment, frequency, amount | CU 86dx88hew |
| Ian | MRR counts when paid; dashboard = truth (post-phantoms); discounts reduce MRR; 30-day grace | Slack MRR DM, May 8–18 |
| Anita (exits) | Score at exit, app activity, engagement red flags per churned member | CU 86e17gm49 comment May 28 |
| Sashani/ops | New-member tracker fields (lead source, DC, promo, paid) | Payments Tracker sheet → Onboardings table |

---

## 2. Field inventory — Members table

### A. Stripe identity / linkage — ✅ healthy, one gap
| Field | Source | Population | Action |
|---|---|---|---|
| Stripe Customer ID | sync | 705/712 active | — |
| Stripe Subscription ID | sync (manual seed) | 704/712 | **Gap: discovery.** Sync only refreshes known IDs; new joiners need manual paste (Tina Audit 1). 7 active members have none (incl. Steven Zhou — sub exists: `sub_1TceWFHUXQT2RuDUo7ttTfoi`; Lie Li = invoice case). |
| Stripe Customer Name / Email, Mismatch formula | sync | w/ sub ID | — (Tina Audit 2) |
| Helper: Sub ID (Last Synced), Last Synced At, Sync Error | sync | w/ sub ID | — |

### B. Subscription state — ✅ healthy (where A exists)
| Field | Source | Action |
|---|---|---|
| Stripe Subscription Status | sync | — |
| Stripe Product Name / Price Name / Amount / Billing Cycle / Interval (+count) | sync | — |
| Stripe Next Invoice Date / Amount | sync | — |
| Stripe MRR / Stripe ARR (formulas) | derived | — |
| stripe event log (rich text) | manual today | ingestion appends one line per event here (audit trail in-record) |

### C. Payment EVENTS — ❌ the core gap. Fuels Anita's entire report.

> **Dunning state machine (per OUR Stripe settings, confirmed by Andy 2026-06-12):** failure → sub `past_due` (still in MRR) → Smart Retry 8× within 1 month → at 30 days incomplete → sub marked **`unpaid`** (drops from Stripe MRR; sub is NOT canceled and no `cancel_at` is set). Therefore: `Scheduled Cancel Date` = VOLUNTARY cancels only (member requested, cancel-at-period-end); involuntary churn = the `past_due`→`unpaid` transition, which lands exactly on the team's 30-day rule → **`Lapsed Payment Date` is automatable from that transition** (today Tina sets it by hand). `unpaid` subs sit indefinitely ("leave invoice as-is") = lapsed-but-recoverable; a later payment = recovery-after-lapse, reported separately.
| Field | Exists? | Population (active) | Needed source |
|---|---|---|---|
| Failed Payment Date | yes | **8** | Stripe `invoice.payment_failed` → write date |
| Last Successful Payment | yes | **1** | Stripe `invoice.paid` → write date |
| Past Due Since | ~~dropped~~ | — | = current-cycle Failed Payment Date; no field |
| **Recovered Date** | **NEW (1/4)** | — | `invoice.paid` after a failure in same cycle |
| Days to Recovery | ~~dropped as Members field~~ | — | computed in Payment Events table / report |
| Lapsed Payment Date (= agreed MRR-loss date) | yes | 3 active / 159 historical | failure + 30d unresolved (was 14 — history question open) |
| Requested to Cancel Date | yes | manual (52 total) | human (Tina) — keep manual |
| **Scheduled Cancel Date** | **NEW (2/4)** | — | Stripe `cancel_at` (fixes Erik Freeman counted-early case) |
| **Collection Paused flag** | **NEW (3/4)** | — | Stripe `pause_collection` (Gustavo case) |

> **Field budget (Members table): exactly 4 new fields** — Recovered Date, Scheduled Cancel Date, Collection Paused, MRR-Effect Bucket (E). Zero new lookups/rollups. Minimal variant = 2 (drop Scheduled Cancel + Collection Paused to events-table-only visibility). All other plan items reuse existing empty fields; `Subscription Started Date` is an in-place type conversion, not a new field.

### D. Money facts at joining — for Josefina + Onboardings lookups
| Field | Exists? | Population (active) | Needed source |
|---|---|---|---|
| Payment Date (first paid) | yes | **5** | first paid invoice of first sub |
| Subscription Started Date | yes — but **text type** | 41 | sub `start_date`; migrate to date field |
| Discount 1ST Payment | yes | 41 | first invoice discount/coupon $ |
| Membership Fee chain → Membership Fee (Used) / For Dashboard | yes (Dec cleanup) | OK | unchanged |
| Subscription Source (GHL/Stripe), GHL Subscription ID | yes | legacy | freeze |

### E. Exit / churn classification — fields exist, partially populated; one NEW
| Field | Status |
|---|---|
| Initial Reason Code / Final Reason / Removal Reason (Code) | exist; Anita populated for 2026 audit (66) — Tina maintains |
| Member Removed Date, Days Failed→Exit | exist |
| **MRR-Effect Bucket** (Eugene's: cancellation / coupon / prepay-discount / transfer / refund / prorated refund / non-renewal / artifact) | **NEW singleSelect (4/4)** — keeps payment mechanics separate from reason codes, kills artifact churns (PGE cancel/recreate — Vanessa Fan, Adam Varner) |
| Replaced Member, Tina's Notes | exist |

### F. Engagement at exit — mostly exists
| Field | Status |
|---|---|
| Score Card at time of removal | exists, sparse — populate at exit (SOP step) |
| Event/virtual/FB/WA engagement fields + AI summaries | exist (audit view) |
| App activity (recordings watched, downloads) | **no source** — needs GroupOS dev endpoint (known gap) |

### G. Derived metrics (no new ingestion once C lands)
Weekly recovered MRR · avg days to recovery · churn per Eugene (30d past due) · MRR for Removed · removed/canceled buckets w/ dates — all become views/rollups over C+E.

---

## 3. Storage: Members-only (decided 2026-06-12)
- **Members table = the single place.** Existing empty fields + the 4 new ones. All views/lookups read here — Members Stripe view, Onboardings lookups, Tina/Anita views.
- **No events table** (created then dropped by Andy's call — Andy deletes "Payment Events" `tblTyotSKEamwSX28` in the UI; API can't delete tables). Weekly movement = filters on the Members date fields (Failed / Recovered / Lapsed / Removed / Requested-to-Cancel within last 7 days). Avg-days-to-recovery computed by the report at run time — no field.
- **History/archive = the weekly report output itself** (posted to CU/Slack). Deep re-audits of past periods come from Stripe exports/Sigma, as today. Trade-off accepted: AT holds current cycle only.

## The ONE ingestion (design sketch)
Extend the existing Stripe→AT sync (don't add parallel automations):
1. **Discovery** — daily: new/active Stripe subs not matched to a Member → match by customer email; exact match auto-writes Customer+Sub ID; no-match → human-review card (handles Zhou-style email differences).
2. **Refresh** — existing behavior, unchanged.
3. **Events** — daily: invoices paid/failed + subscription `cancel_at` / `pause_collection` for known customers → write C-fields + append `stripe event log`.
4. **First-invoice facts** — on first successful invoice: Payment Date, Discount 1ST Payment, Subscription Started Date (D).

Consumers (read-only, zero own automations): Onboardings table (lookups — already wired) · Members Stripe view · Anita's weekly report (view/interface over C+E) · Josefina's billed-MRR view (D+B) · KPI rollups (G).

## 4. Backfill order (after map sign-off)
1. 7 missing sub IDs (Zhou known; rest matched by email, mismatches to Andy). Ulrich dupe-merge decision.
2. C-fields for active members from Stripe invoice history (90 days back covers Anita's current report; deeper = optional).
3. D-fields for 2026 joiners (71+12 onboarding rows cross-check).

## 5. Open decisions (Andy/team)
- 14d→30d history: re-state old lapsed dates or annotate epoch?
- `Subscription Started Date` text→date migration timing.
- Where does the human enter Requested-to-Cancel — keep Members field as today? (yes, proposed)
- MRR-Effect Bucket values final wording (Eugene's list + "artifact / not churn").
- App-activity endpoint request to GroupOS team — who files it.
