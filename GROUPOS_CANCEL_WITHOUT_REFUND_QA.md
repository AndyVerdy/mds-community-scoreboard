# Test report — cancel a paid ticket without a refund, pre-prod

**Ticket:** `86e2t7834` — Admin: cancel a paid ticket without issuing a refund (pre-prod release 1.2.1; MDS-API #5493/#5494, MDS-APP #8297/#8298)
**Tested by:** Claude for Andy · 2026-09-03 05:03–05:17 UTC · pre-prod `vl223.groupos-test.co`
**Outcome: PASS (Andy, 2026-09-03) — evidence comment `90170248134663` on the ticket; AC 2/5/6/8/9 handed to the dev team.** Detail: **everything reachable from the admin UI passes** — the no-refund cancel releases the seat with $0 moving, the order reads Cancelled, the reason is enforced client-side, notify defaults off, and the webhook carries `reason paid_ticket.cancelled_no_refund` / `type no_refund` with no `ticket.refunded` after it. Four criteria could not be run from here (AC 2 Stripe, AC 6 multi-ticket order, AC 8 PAT, AC 9 audit record) and need the dev team's own check. Two observations worth a look at the end.

## Fixture

Order `#6a8614ebdc47075a29116304` (Andrii Matiushenko, event "Untitled Event (Feb 13 2026 21:46)" `698f718db50bfd00e6e781f1`, started Aug 26 so its refund window is closed), transaction #3 = the last Succeeded $100 General Admission ticket (purchase `6a8ef5fa478f4c4209fcc541`, transaction `6a8ef5fa478f4c4209fcc53f`, Stripe intent `pi_3U8hfyLQNMR2DnJW1zW5FWBC`). Same integration as the `86e25hmj1` report for webhook evidence ("Maks WH - Approvals test", endpoint dead → every delivery "Gave up" on 404; the history modal payload is the proof).

Before: Tickets page — sold 1/200, cancelled 0, General Admission 1/100, net sales $100.00. Attendee list — **already empty** ("No attendees yet") and Dashboard "Recent registrations" empty, although tx #3 was still Succeeded (see observation 2).

## What was run

| # | Step | When (UTC) | Result |
|---|---|---|---|
| 1 | Admin → Orders → Order details → cancel icon on tx #3 | 05:03 | Dialog "Cancel ticket?" with refund mode **Refund in full ($100.00 returned)** / **Cancel without refund ($0.00 returned, the community keeps the payment)** — offered on an event past its refund window (**AC 11**) |
| 2 | Select "Cancel without refund" | 05:03 | Banner "No money will move — $100.00 will not be returned. The seat goes back to inventory and the member loses event access." Reason becomes required ("Stored on the audit record. The member never sees it."), three one-tap reasons, notify-by-email checkbox **unchecked by default** |
| 3 | Confirm with a blank reason | 05:03:09 | Blocked client-side: "A reason is required to cancel without a refund." No request sent (**AC 7**, client layer; the server 400 was not exercised, see Not run) |
| 4 | Confirm with reason "QA 86e2t7834 no-refund cancellation test (Andy, pre-prod)", notify unticked | **05:11:13** | `POST /api/event/payment/refundPurchaseTicket/6a8ef5fa478f4c4209fcc541` → 200 `{"status":true,"message":"Ticket was removed successfully!"}` at 05:11:13.990. Toast "Ticket cancelled without a refund". Tx #3 badge → **Cancelled** (**AC 1**). Payment breakdown unchanged: refunded amount still -$300.00, net $90.40 — no money moved (**AC 2 as far as the UI shows**) |
| 5 | Tickets page after | 05:12 | Sold 0/200, **Cancelled tickets 1**, General Admission 0/100 (**AC 3**), net sales $0.00 (observation 1) |
| 6 | Attendee list after | 05:12 | Still "No attendees yet" — consistent with AC 4, but it was already empty before the test, so no delta (observation 2) |
| 7 | Orders list after | 05:12 | Row shows Tickets 0, Amount $0.00, status still "Partial payment refund initiated" (driven by tx #1's pending refund) — a no-refund cancel is not distinguishable at list level on this mixed order |
| 8 | Webhook | 05:11:14 | `ticket.cancelled` first attempt one second after the click (`whd_e61664ef-1b39-4580-8174-4c9819defedb`, then two retries, "Gave up" on the dead endpoint). **No `ticket.refunded` followed** (checked at 05:16:43, five minutes later; the refund pair on the earlier full refund had arrived within three seconds) |
| 9 | Regression, full refund (**AC 10**) | 03:08 (earlier session) | Tx #4 refunded in full through the same dialog: `ticket.cancelled` + `ticket.refunded`, Stripe refund initiated — unchanged behaviour |

## Webhook payload (no-refund)

```json
"cancellation": {
  "reason": "paid_ticket.cancelled_no_refund",
  "type": "no_refund",
  "refundAmount": 0,
  "cancelledBy": "admin",
  "cancellationDate": "2026-09-03T05:11:14.230Z"
},
"triggerEntity": { "type": "ticket.cancelled", "id": "6a8ef5fa478f4c4209fcc541" },
"tickets": [{ "name": "General Admission", "type": "PAID", "quantity": 1,
             "unitPrice": "$100.00", "totalPrice": "$100.00", "status": "cancelled" }],
"totalPaid": "$0.00", "orderAmount": "$0.00", "processingFee": "$3.20",
"paymentIntentId": "pi_3U8hfyLQNMR2DnJW1zW5FWBC", "timestamp": "2026-09-03T05:11:14.465Z"
```

Same 27 top-level keys as every other `ticket.cancelled`. Andy's comment 3 is met: same webhook, `refundAmount` present, `type` says with or without refund. The order-level `totalPaid` / `orderAmount` read `$0.00` for a $100 ticket — the same S2 already filed on `86e25hmj1`; here it means a consumer cannot see the amount kept except through `tickets[].totalPrice`.

## Acceptance criteria

| AC | Verdict |
|---|---|
| 1 Cancelled, not Refunded | **met** — tx #3 "Cancelled", toast, `tickets[0].status: "cancelled"` |
| 2 No Stripe refund object / no `ticket_Payment_Refund` doc | **not verified** — needs the Stripe test dashboard and Mongo; the UI shows no money moved |
| 3 Seat returns (`availableQuantity` +1) | **met** — 1/100 → 0/100, cancelled tickets 0 → 1 |
| 4 Member leaves the attendee list, loses access | **inconclusive** — list was already empty before the test; access not checkable without Andrii's login |
| 5 No email | **not verified** — Andrii's inbox; notify checkbox was unticked |
| 6 Order-level cancel takes every ticket | **not run** — no order with two Succeeded paid tickets exists, and I don't buy with a card |
| 7 No reason → 400 | **met at the client** ("A reason is required…", no request); server-side 400 not exercised |
| 8 PAT-authenticated call rejected | **not run** — my tooling refuses to send a token in a request; PR #5493 ships `MDS-API auth surface — PAT invariant` (no PAT-shaped auth provider exists). One curl from a human settles it, see below |
| 9 Audit record with admin, reason, amount | **not verified** — `event_cancellation_audits` in Mongo |
| 10 Full refund unchanged | **met** — tx #4 earlier tonight |
| 11 Works past the refund window | **met** — event started Aug 26, option offered and executed |
| Andy 1 refund-or-not choice | **met** |
| Andy 2 optional notify email, generic | **met** in the dialog (default off); email content not seen |
| Andy 3 same webhook + refund amount + cancellation type | **met** |

AC 8, for whoever has a pre-prod PAT (expected: 401/403, and the purchase untouched):

```bash
curl -sS -X POST "https://vl223.groupos-test.co/api/event/payment/refundPurchaseTicket/<a Succeeded purchase id>" \
  -H "Authorization: Bearer <pre-prod PAT>" -H "Content-Type: application/json" \
  -d '{"skipRefund":true,"notifyMember":false,"refundNote":"AC8 probe"}' -w '\nHTTP %{http_code}\n'
```

## Observations

1. **Tickets page "Net sales" drops to $0.00 after a no-refund cancel.** The community kept $100, but the Tickets page (and the General Admission row) report $0.00 net sales once the ticket is cancelled. Reporting only; the order's payment breakdown still shows the money. Worth deciding what "net sales" should mean for kept money.
2. **Attendee list was empty while a Succeeded paid ticket still existed.** Before this test Andrii had tx #3 Succeeded, yet the attendee list and "Recent registrations" were empty. The ticket's rule is "attendee soft-deleted when the user has no other succeeded payment intent for the event". Either the earlier full refund of tx #4 (03:08 UTC) removed him despite tx #3, or he was never listed after re-buying on Aug 26 — I could not see the state before 03:08. Needs a look in Mongo (`attendees` for user `69d8b9a400b256a2fa73972c`, event `698f718db50bfd00e6e781f1`).
3. Orders list status is the aggregate of the order's purchases, so on a mixed order the no-refund cancel is invisible at list level (row shows 0 tickets / $0.00 / "Partial payment refund initiated"). Fine for single-purchase orders; a design question for mixed ones.

## State left on pre-prod

Order `#6a8614ebdc47075a29116304` now has no Succeeded ticket: #1 refund initiated (Aug 19), #2 refunded, #4 refunded (tonight, full refund), #3 cancelled without refund (tonight, reason "QA 86e2t7834 no-refund cancellation test (Andy, pre-prod)"). No further paid fixture exists on pre-prod; a new paid purchase (card) is needed before anyone can rerun AC 6 or the member-paid path.
