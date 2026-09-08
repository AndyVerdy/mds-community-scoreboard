# Test report — empty-cart retry, form capture on checkout retry

**Ticket:** `86e2v989y` — Empty-cart retry, MDS-APP posts `ticketData: []`
**Tested by:** Claude for Andy · 2026-09-08 02:30–03:00 UTC · pre-prod `vl223.groupos-test.co` (community `69034d79599a70658c11755b`)
**Status when tested:** `deployed` (Andrii's comment says live on production; MDS-API PRs #5452/#5453/#5454 and MDS-APP #8267/#8268/#8269 are merged to staging, preprod and `Prod-groupos`)

**Verdict: FAIL.** The headline behaviour works on a clean checkout, but a member who re-registers for an event after their previous order was cancelled is never shown the application form, completes a succeeded registration with the required answer empty, and the answer that had been stored for them is replaced by "No answer". That is the same silent loss of member-submitted data the ticket exists to eliminate, on a retry path.

I verified that the fix is present on every branch, so pre-prod and production carry the same code here: `missingApplicationFormTicketIds` appears in `MDS-APP/src/Hooks/useEventSelectTicketActions.ts` and `MDS-API/controller/eventManagement/eventTicketPaymentControllerV2.js` on `staging`, `preprod`, `Prod-groupos` and `release/1.2.1`.

---

## Fixture

Built from scratch so nothing was inherited from earlier QA:

| | |
|---|---|
| Form | **QA form 86e2v989y** (`6a9f72932ba5f4c99352049d`) — one short-answer question "Dietary needs (QA 86e2v989y)", **required** |
| Event | **QA form gate 86e2v989y** (`6a9f774d2ba5f4c993520d78`) — online, Sep 12–15 2026, live |
| Ticket | **Gated Free Ticket** — free, visible to everyone, Application form on, linked form = QA form 86e2v989y |
| Member | VL 23 (`viktor.lymar+223@ardas.biz`), the signed-in account |

The ticket name renders as "General AdmissionGated Free Ticket" because the Add-ticket dialog pre-fills "General Admission" and my typing appended to it. That is a fixture artefact, not a defect.

## What was run

| # | Step | When (UTC) | Result |
|---|---|---|---|
| 1 | Member clicks **Complete registration** on the event page, first ever attempt | 02:51:18 | **Final details** page appears with the required question. **PASS** |
| 2 | Submit with the question blank | 02:51:50 | Blocked, inline error **"This field is required"**, no navigation. **PASS** (test case A, AC 5) |
| 3 | Fill "Vegetarian - QA 86e2v989y", continue, complete registration | 02:52:10 → 02:53:49 | Registered. Admin → Form responses → QA form 86e2v989y: **VL 23 · 1 of 1 · "Vegetarian - QA 86e2v989y"**. **PASS** |
| 4 | Abandon mid-checkout and return: navigate away at "Awaiting for payment", reopen the event, click Complete registration | 02:53 | **Form is presented again**, empty, and the blank submit is still refused. This is the fix's headline behaviour on an intent with no saved answers. **PASS** |
| 5 | Admin cancels the order (More → Refund all purchases → Cancel order, no refund, reason "QA 86e2v989y retry repro") | 02:56 | "Order cancelled without a refund" |
| 6 | **Member reopens the same event and clicks Complete registration** | 02:57:30 | Goes **straight to Checkout**. Banner "Cancelled order", line "Awaiting for payment", an "Edit Form" link — **the application form is never presented** (`input[placeholder="Type your answer here..."]` absent). **FAIL** |
| 7 | Member clicks Complete registration on that checkout | 02:57:48 | "Registration confirmed". Admin → Form responses: **1 response — VL 23 · 1 of 1 · "No answer"**, dated 02:57. The "Vegetarian" answer from step 3 is gone. **FAIL** |

Steps 6–7 reproduce a failure I first hit on an unrelated event (`6a98e708959c69fd82bc8ba4`, ticket "QA Free Ticket" linked to the same form) at 02:33 UTC, before building the clean fixture. Same shape both times.

---

## Findings

### 1. Re-registering onto a cancelled order skips the required form and blanks the stored answer — S2

Repro: live event, free ticket with an application form containing a required question → member registers and answers → an admin cancels the order → member reopens the event and clicks Complete registration.

Observed: the checkout is reached with no form step. The registration succeeds. The member's stored answer changes from a real value to "No answer", and the response count stays at 1, so there is no second row preserving the original. A form-gated ticket therefore ends up succeeded, non-deleted, with no usable response — the exact population the ticket's prod audit counted (~2,042 in 2026).

Two things make this worth fixing even though the trigger is an admin cancellation rather than a mobile-app order:
- The mechanism is the one named in the ticket: checkout re-uses the existing payment intent and returns without re-collecting answers.
- Data that a member had already provided is destroyed, not merely left absent.

### 2. Member event page still reads "Registered / Registration confirmed" after every purchase in the order is cancelled — S3

Seen on event `6a98e708959c69fd82bc8ba4` after an admin cancelled all three purchases. A reload did not clear it. The member cannot tell they no longer hold a ticket. Probably belongs to the cancellation work (`86e2t7834`) rather than this ticket, but it was reproducible and is recorded here.

### 3. The admin "Missing" recovery tool described in the ticket body is absent — not a defect

The ticket's own How-to-test steps 1–3 describe a "Missing" count per ticket sub-row and a dialog for entering responses on behalf of attendees. There is no Missing column anywhere on Form responses. Andy's comment on 2026-05-18 narrowed the work to the empty-cart retry only, and Andrii's completion comment does not claim the recovery tool, so I am recording this as descoped rather than missing.

---

## Acceptance criteria

| Andrii's case | Verdict |
|---|---|
| A. Required questions block a blank submit; filled answers are saved | **met** — steps 1–3 |
| B. Return to pay when answers are already saved: no re-ask, one ticket, one charge | **not tested** — needs a paid ticket and a card, which I do not use. The free-ticket equivalent (step 4) behaved correctly |
| C. Multi-ticket-type event: selection not wiped, total never doubles | **not tested** |
| D. Order and checkout pages show the right ticket count and total | **met for free tickets** — 1 x ticket, $0.00, single order throughout |
| Ticket AC 5. Normal first-time web checkout still refuses a blank form | **met** — step 2 |
| Ticket promise: returning with no saved answers re-shows the form | **met on an abandoned intent** (step 4), **fails on a cancelled order** (steps 6–7) |

## State left on pre-prod

- Form **QA form 86e2v989y** and event **QA form gate 86e2v989y** (`6a9f774d2ba5f4c993520d78`) created by me and left live, with one succeeded VL 23 registration whose answer reads "No answer".
- Event `6a98e708959c69fd82bc8ba4` ("QA webhook cancel test 86e25hmj1"): I linked the same form to "QA Free Ticket", added a second ticket type, created and marked paid a manual order for Andrii Matiushenko, and cancelled VL 23's order. Its Form responses shows one "No answer" row.
- Nothing was deleted.
