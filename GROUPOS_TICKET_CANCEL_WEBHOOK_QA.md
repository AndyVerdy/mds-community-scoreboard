# Test report — `ticket.cancelled` webhook on admin cancellation, pre-prod

**Ticket:** `86e25hmj1` — Add ticket cancellation trigger (pre-prod release 1.2.1; MDS-API PR #5493, enabler PR #5383)
**Tested by:** Claude for Andy · 2026-09-03 03:08–03:36 UTC · pre-prod `vl223.groupos-test.co` (community `69034d79599a70658c11755b`)
**Verdict: the ticket's own claim PASSES** — an admin cancelling a **paid** ticket now fires `ticket.cancelled` two seconds later, with the documented shape (`cancellation.reason = "paid_ticket.cancelled"`, `cancelledBy = "admin"`). **Member-side parity could not be confirmed:** the pre-prod webhook delivery worker stopped processing jobs at ~03:17 UTC, and even a manual test event never produced a delivery. Finding 1 below.

What PR #5383 actually fixed (its own description): admin and member cancellations always ran the same code path; the real gap was **paid** tickets, which fired nothing at cancel time (only a `ticket.refunded` hours later, or never when the money came from invoice credit). So the decisive QA case is "admin cancels a paid ticket".

---

## Setup

- Evidence surface: Settings → Integrations → **Sending** → integration **Maks WH - Approvals test** (`6a0ca92af48d3ea279613b86`), subscribed to 13 event types including `ticket.purchased`, `ticket.refunded`, `ticket.cancelled`. Its endpoint (`a3c74fb5-….webhooksite.net`) answers HTTP 404, so every delivery ends as "Gave up" — that is pre-existing and irrelevant here: the delivery record and its **What we sent** payload in the history modal are the proof that the platform fired the event.
- Nothing new was configured on the integration. It was accidentally paused for about two minutes (~03:31–03:33 UTC) by a mis-click and re-activated ("Integration is active").
- Outgoing webhooks are served by the legacy API (`/api/webhooks`, `/api/webhooks/activity`, `/api/webhooks/history`) — admin-token protected; the UI modal was used instead of the API.

## What was run

| # | Step | When (UTC) | Result |
|---|---|---|---|
| 1 | **Admin cancels a PAID ticket, refund in full** — order `#6a8614ebdc47075a29116304` (Andrii Matiushenko, event "Untitled Event (Feb 13 2026 21:46)" `698f718db50bfd00e6e781f1`), transaction #4, $100 General Admission. Admin → Orders → Order details → refund icon → "Refund in full" → Refund payment | 03:08:29 | UI "Ticket successfully refunded"; tx #4 → Payment refund initiated. **`ticket.cancelled` delivery attempted 03:08:31** (`whd_69dee84e-ed87-476a-942b-92921645b1f6`), then **`ticket.refunded` 03:08:34** (`whd_135abf6c-1bd1-4760-8bd9-574a075fac77`). **PASS** |
| 2 | Baseline: admin cancels a FREE ticket — pre-existing delivery 2026-08-25 09:52:46 (Doina Chilat, event "Doina Testing") | — | Same 27 top-level keys as #1; `cancellation = {reason:"free_ticket.cancelled", cancelledBy:"admin", cancellationDate}` (pre-1.2.1 shape, no `type`/`refundAmount`) |
| 3 | Member (logged-in owner account "VL 23") registers for the free ticket on "San Diego Chapter Hike Feb 2026" | 03:15:28 | `ticket.purchased` delivery attempted 03:17:01 (90 s lag). Ticket shows **Non-cancelable** on the member side (event already started), so no member cancel there |
| 4 | **Member cancels a FREE ticket** on a new event "QA webhook cancel test 86e25hmj1" (`6a98e708959c69fd82bc8ba4`, online, Sep 12–13, ticket "QA Free Ticket" with *Allow cancellation* on, 1-day deadline). Registered 03:24:22 → order `#6a98e867959c69fd82bc8d43`; member "Cancel order" confirmed | 03:27:07 | UI "Order cancelled successfully"; admin Orders shows **Cancelled**. **No delivery record at all** — not for `ticket.purchased`, not for `ticket.cancelled`, and none for the event's `event.created` / `event.updated` either (checked until 03:36). **INCONCLUSIVE — see finding 1** |
| 5 | Integration actions → **Send test event** (job `c2715176-276a-4e58-99cb-5eaee7281944`, "expected within 1-5 seconds") | 03:34:10 | No delivery record by 03:36:21. Confirms the worker stall, not a cancel-path problem |

## Payload — admin, paid, refund (delivery 03:08:31 UTC)

```json
"cancellation": {
  "reason": "paid_ticket.cancelled",
  "type": "refund",
  "refundAmount": 100,
  "cancelledBy": "admin",
  "cancellationDate": "2026-09-03T03:08:31.104Z"
},
"triggerEntity": { "type": "ticket.cancelled", "id": "6a8f0e5a8f425f0f0616a34c" },
"tickets": [{ "name": "General Admission", "type": "PAID", "quantity": 1,
             "unitPrice": "$100.00", "totalPrice": "$100.00",
             "status": "payment_refund_initiated", "userParticipantId": "6a8ef5fae67048a727f0ef8c" }],
"totalPaid": "$0.00", "orderAmount": "$0.00", "processingFee": "$3.20",
"paymentIntentId": "pi_3U8jIcLQNMR2DnJW1e6EfHOD", "orderType": null, "tzSource": "event",
"timestamp": "2026-09-03T03:08:31.320Z", "webhookVersion": "1.0"
```

Top-level keys (27, identical to the free-ticket baseline): `orderDate, orderDateLocal, totalPaid, orderAmount, processingFee, paymentIntentId, user, purchaser, event, eventName, tickets, ticketTypes, ticketsSoldCount, addons, addonsList, addonsTotalPaid, formResponses, questionnaireAnswers, relation_id, timestamp, timestampLocal, tzSource, webhookVersion, orderType, triggerEntity, cancellation, deliveryId`. `user` is the participant (Andrii), `purchaser` the owner account that bought on his behalf — as documented.

The companion `ticket.refunded` (03:08:34) has its own shape: `refundDate, refundDateLocal, refundAmount, refundReason, user, purchaser, event, tickets, …, triggerEntity, deliveryId`.

---

## Findings

### 1. Pre-prod webhook delivery worker stalled at ~03:17 UTC (blocks the member-side check)

Last processed job: `ticket.purchased` attempted 03:17:01. Everything queued after it has **no delivery record whatsoever** (the history's *Queued* bucket stays 0, so the jobs are stuck before the history layer): `event.created` for the draft "Untitled Event" (~03:18), three `event.updated` saves, the QA event's `ticket.purchased` (03:24:22), the member `ticket.cancelled` (03:27:07) and the manual `test_webhook` (03:34:10, promised within 1–5 s). Needs a look at the consumer / message queue on pre-prod. The first job after the last good one is the `event.created` of a bare draft event (no location, no description) — if that payload build throws and kills the singleton consumer, it would explain the silence. The two-minute accidental pause (~03:31–03:33) came after the 03:24/03:27 jobs were already overdue and before the 03:34 test, so it does not explain the stall, but it is in the logs.

### 2. Paid cancellation payload reports `totalPaid: "$0.00"` and `orderAmount: "$0.00"` for a $100 ticket

`processingFee` is right ($3.20), `tickets[0].totalPrice` is right ($100.00) and `cancellation.refundAmount` is 100, but the two order-level amounts are zero. `docs/WEBHOOK_SYSTEM_README.md` shows real amounts in the cancellation example (`"$150.00"` / `"$135.00"`). A consumer keying on `totalPaid` sees a free order.

### 3. `ticket.refunded` says `refundAmount: 0`, `refundReason: "No reason provided"`, and has no `triggerEntity.id`

For a $100 refund initiated by the admin (reason left blank, which the dialog allows on a full refund). `triggerEntity` is `{ "type": "ticket.refunded" }` with no `id`, unlike every other event. Pre-existing path, not this ticket — but this pair is what every subscriber to both events receives.

### 4. Sending-integration detail opens with "All 0 — Nothing has been sent yet" while 32 deliveries exist

The history section does not fetch on mount; it fills in only after the time filter is touched (or a later navigation). Same behaviour as issue 1 in `GROUPOS_INGEST_DEFECT_REPORT.md`, now confirmed on the sending side. The list header count also lags the history (showed 31 while the history had 32).

### 5. Direct navigation to `/integrations/sending/<id>` renders the list frame with no rows

Issue 3 from the receiving report, unchanged. Reaching a detail page needs Settings → Integrations → Sending → row, every time.

### 6. (Unverified) member Order details listed three tickets for a one-ticket order

After registering on San Diego Chapter Hike, the member-side Order details page showed **three** "Free Guest Ticket / Non-cancelable" rows for my single-ticket order; the event has exactly three free registrations in total (Andrii, Doina, me). It looks like the page lists every registration of the event rather than the order's own. Seen once, not chased.

---

## State left on pre-prod

- Order `#6a8614ebdc47075a29116304` (Andrii): transaction #4 cancelled with a $100 Stripe test-mode refund initiated; transaction #3 untouched.
- Event "QA webhook cancel test 86e25hmj1" (`6a98e708959c69fd82bc8ba4`): **Paused**, one cancelled order. Delete it when the dev team has looked at finding 1 — I do not delete.
- Account "VL 23" holds a live free ticket on San Diego Chapter Hike (03:15 UTC); non-cancelable from the member side, cancel it from admin if it matters.
- Integration "Maks WH - Approvals test": Active.

## Not tested

- Member cancels a **paid** ticket (`cancelledBy: "user"` on the paid path) — needs a card purchase, which I don't perform.
- Cancel **without** refund (`paid_ticket.cancelled_no_refund`, ticket `86e2t7834` on the same release line).
- A fresh admin cancel of a free ticket on 1.2.1 (only the pre-1.2.1 baseline delivery exists) — blocked by finding 1 anyway.
