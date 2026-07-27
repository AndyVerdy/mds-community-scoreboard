# Conference Pass Upgrade — Smart Checkout System

## Problem
Generic payment link → members enter random emails/names → can't reliably match payments to Airtable member records.

## Solution
Web page with email lookup → Airtable match → Stripe Checkout with pre-filled customer info.

---

## Flow

```
Guest scans QR → upgrade.html → enters email
        ↓
  Make.com webhook
        ↓
  Search Airtable (Preferred Email)
        ↓
  ┌─────────────────────────────────────────┐
  │ Found + has Stripe Customer ID?         │
  ├──── YES ────────────┬──── NO ───────────┤
  │ Create Stripe       │ Return fallback   │
  │ Checkout Session    │ payment link URL  │
  │ with customer ID    │                   │
  │ pre-filled          │                   │
  └─────────────────────┴───────────────────┘
        ↓                       ↓
  Stripe Checkout        Generic payment link
  (name/email/card       (member types info
   pre-filled)            manually)
        ↓                       ↓
  Payment complete ──────────────┘
        ↓
  Existing Slack notification fires
```

---

## Components

### 1. Web Page (`upgrade.html`) — GitHub Pages
- Hosted at: `https://andyverdy.github.io/mds-community-scoreboard/upgrade.html`
- MDS dark branded theme (matches existing scoreboard)
- Simple form: "Enter your email to upgrade"
- Submits email to Make.com webhook via fetch()
- Receives JSON with redirect URL + member name
- If member found: "Hi Sarah! Redirecting to checkout..." → redirect
- If not found: "Redirecting to payment page..." → redirect to fallback link
- Shows success/canceled states via URL params (`?success=1`, `?canceled=1`)
- Mobile-first (QR scan = phone)

### 2. Make.com Scenario ("Conference Pass Upgrade — Email Lookup")
Located in Stripe folder (ID: 120693)

**Module 1: Custom Webhook**
- Receives POST `{email: "member@example.com"}`
- Returns JSON response

**Module 2: Airtable — Search Records**
- Base: `appou5JVr0WIrioWS`
- Table: `tblfwOSROSHfuYUxv` (Members)
- Search field: `Preferred Email` (`fldqP1um6hhif91aO`)
- Return fields: Full Name, Stripe Customer ID

**Module 3: Router**

- **Route A** — Member found + Stripe Customer ID exists:
  - Stripe HTTP request: Create Checkout Session
    - `customer`: cus_XXXXX from Airtable
    - `line_items[0][price]`: `price_1T7LMsHUXQT2RuDUD13Qfwrl` ($400)
    - `line_items[0][quantity]`: 1
    - `mode`: payment
    - `metadata[upgrade_type]`: "conference_pass"
    - `success_url`: upgrade.html?success=1
    - `cancel_url`: upgrade.html?canceled=1
  - Webhook Response: `{url: checkout_session.url, name: "Sarah Smith"}`

- **Route B** — Fallback (no member or no Stripe Customer ID):
  - Webhook Response: `{url: "https://checkout.mds.co/b/5kQ5kD49xayzf1f5SY3Ru00", name: null}`

### 3. Update Existing Slack Notification (Scenario 4593806)
Currently filters on `payment_link == plink_1T74ijHUXQT2RuDUO5omwbKW`.

Checkout Sessions created via API won't have a `payment_link` field → filter won't match.

**Fix**: Update filter to match EITHER:
- `object.payment_link == plink_1T74ijHUXQT2RuDUO5omwbKW` (fallback path)
- OR `object.metadata.upgrade_type == "conference_pass"` (checkout session path)

---

## Key Data

### Airtable Fields
| Field | ID | Purpose |
|---|---|---|
| Preferred Email | fldqP1um6hhif91aO | Email lookup |
| Full Name | fldYkS0TgeMAtIrU8 | Display greeting |
| Stripe Customer ID | fldPtQvVTjI6sjeg8 | Pre-fill Checkout |

### Stripe
| Item | Value |
|---|---|
| Product | Conference Pass Upgrade (prod_U5FCemaLbgjrAm) |
| Price | $400.00 (price_1T7LMsHUXQT2RuDUD13Qfwrl) |
| Fallback link | https://checkout.mds.co/b/5kQ5kD49xayzf1f5SY3Ru00 |

### Make.com Connections
| Service | Connection | ID |
|---|---|---|
| Stripe | Stripe Test | 2160520 |
| Slack | Andy (user) | 4689819 |
| Airtable | TBD (check available) | — |

---

## Build Order
1. Create `upgrade.html` — branded, mobile-first page with email form
2. Create Make.com webhook + scenario (lookup → router → checkout or fallback)
3. Update existing Slack notification filter for both paths
4. Test full flow end-to-end
5. Generate QR code for upgrade.html URL
