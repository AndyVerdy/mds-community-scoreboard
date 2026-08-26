# Test report — incoming webhooks, pre-prod

**Ticket:** `86e2bjq8x` — Incoming Webhooks for default Profile fields (Address, Tags, Events registered)
**Tested by:** Andy · 2026-08-26 · pre-prod `vl223.groupos-test.co`
**Verdict: Address and Tags pass.** Three UI issues below, none blocking.

---

## What was tested

Connection `andy`, writing to member `staging123@groupos.com` ("Andy on the map").

| # | Test | Result |
|---|---|---|
| 1 | No token | `401 Missing or malformed Authorization header` |
| 2 | Bad token | `401 Invalid, expired, or revoked token.` |
| 3 | Email matching no member | `202 accepted:true`, silent no-op, flagged for a second look |
| 4 | Address + tags on a real member | `202 {"accepted":["address","tags"],"ignored":[]}` |
| 5 | Replace — one tag sent where two existed | previous tags removed, address untouched |
| 6 | Dedupe — same message id resent | `202 deduped:true`, not re-applied |
| 7 | Unknown field `phone` | `400 Unrecognized key(s) in object: 'phone'` |

Address went in as the one-line string `1 Infinite Loop, Cupertino, CA 95014, USA` and came
back split into street / city / state / ZIP / country, with the map flag intact — Dallas TX
75204 → Cupertino CA 95014. Google normalisation runs on ingested values exactly as it does on
a manual edit, which was the open question on the ticket. Tags went 0 → 2 → 1.

Test 5 followed by test 6 is worth calling out as a pair: the replace left one tag, then the
deduped replay of the earlier two-tag message correctly did **not** put the old tags back.
Dedupe genuinely blocks re-application rather than just suppressing the response.

Both gaps from the earlier draft of this report are now fixed — the web address is populated
and the Share-setup-details panel documents `Authorization: Bearer <token>`, including that a
bare token is rejected. Good addition; that was the one thing the panel needed to be usable
by whoever wires up the other end.

---

## Issues found

### 1. Message history does not refresh — it reports zero while the header reports messages

On an integration's detail page, the Message history section shows `All 0` and the empty state
*"Nothing has arrived yet — This integration has never been called"* while the same page's own
header says the integration has messages. Seen on both connections: `AMAT Testing` showed
6 messages in the header and "never been called" in the history; `andy` did the same
immediately after a successful send.

A full page reload fixes it. Not a data problem — the history is stored correctly, it just
doesn't fetch on mount or after a send.

This one is worth prioritising: someone testing a new connection sends their first message,
sees "This integration has never been called", and reasonably concludes it failed. That is
exactly the moment the page needs to be right.

### 2. "Show those messages" doesn't change the time filter

The amber banner *"N messages need a second look"* has a **Show those messages** button. The
history's time filter is fixed at **Last 24 hours**, and the button does not widen it. So when
the flagged messages are older than a day — `AMAT Testing`'s were 5 days old — clicking it
reveals nothing, and there is no visible way to reach them.

### 3. Blank page on direct navigation or refresh

Loading `/integrations`, `/integrations/receiving`, or `/integrations/receiving/<id>` directly
in the address bar renders the sidebar with an empty content area. Content only appears after
clicking **Integrations** in the sidebar. Same on refresh. This breaks bookmarks, shared links,
and browser reload — and the setup instructions tell admins to send people a link.

---

## Not yet tested

Events registered, including the attendee-list side effect when an event name matches a real
event, and the `#%$*^` delimited-string path from an actual Airtable formula field. Both are
next.
