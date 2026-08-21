# Defect report — incoming webhooks not testable on pre-prod

**Ticket:** `86e2bjq8x` — Incoming Webhooks for default Profile fields (Address, Tags, Events registered)
**Status on ticket:** deployed to pre-prod
**Reported by:** Andy · 2026-08-20
**Severity:** S1 for the QA pass — blocks the manual test checklist entirely

---

## Summary

The feature cannot be tested on pre-prod. The integration and its token are set up correctly,
but the integration has no web address, so there is nothing for a sending tool to call.

Doina assigned this to me to test. I set up the connection exactly as described in the test
instructions, got a working token, and then had nowhere to send anything.

---

## Environment

| | |
|---|---|
| Environment | Pre-prod — `https://vl223.groupos-test.co` |
| Integration | `andy` — `6a868ae0bdab79b87256579c` |
| State | Active · Receiving · Member profile · never called |
| Token | `pat_pub_KghZ…` — PAT "Incoming endpoint: andy", Active, expires Nov 17 2026 |
| Fields enabled | Address, Tags, Events registered |
| **Web address** | **absent** |

---

## What happens

On the integration's Setup panel:

> **Web address** — Not configured for this environment

And in **Share setup details**, the panel intended to be handed to whoever wires up the
sending tool:

> **No web address configured**
> This environment has no web address configured yet. Contact support before connecting a tool.

That panel is described in the UI as self-sufficient — *"Anyone wiring up the integration can
work from it"* — but it cannot be acted on, because the one thing the other end needs is the
one thing missing.

## Confirmation that the address is genuinely absent

This was checked before reporting, in case it was a rendering issue rather than a missing
configuration value:

1. **Pre-prod is a CloudFront distribution that refuses POST.** Any POST to a non-API path on
   `vl223.groupos-test.co` returns:
   > 403 — This distribution is not configured to allow the HTTP request method that was used
   > for this request. The distribution supports only cachable requests.

   So the ingest endpoint was never expected to live on that host.

2. **No ingest route exists on either origin.** 25 candidate paths were tried under
   `vl223.groupos-test.co/api/v1/*`, `/api/*`, `/ingest/*`, and on the real API origin
   `api.groupos-test.co` (44.240.58.166). Every one returned 404.

3. **There is no separate ingest host.** `ingest.`, `hooks.`, `gateway.`, `in.` and
   `events.groupos-test.co` all CNAME to the same wildcard CloudFront distribution
   (`d37inoairifeby.cloudfront.net`) — none is a distinct service.

Conclusion: the gateway base URL is unset for this environment, rather than hidden or
misrendered.

---

## What we need

1. **The pre-prod ingest URL**, or the environment variable set so the UI renders it. Either
   unblocks the test immediately — the sending side is already built and waiting on that one
   value.

2. **Document the auth scheme in the Share setup details panel.** Separate from the outage
   above, and worth fixing regardless: the panel gives the token but never says how to present
   it. `Authorization: Bearer <token>`? A custom header? Whoever configures Airtable, Zapier or
   n8n has to guess. The example message shows the body in full but the request headers not at
   all. Adding the header line to that example would make the panel genuinely complete.

---

## Two smaller notes from setting it up

- The **Integrations page does not render on direct navigation.** Loading
  `/integrations` or `/integrations/receiving/<id>` straight from the address bar gives an
  empty content area with only the sidebar; the content appears only after clicking
  **Integrations** in the sidebar. Worth a look — deep links and refreshes will hit this.

- The **staging test community and the pre-prod community are different places.** The
  verification note on the ticket cites community `pavel` on staging; this connection is on
  `vl223` on pre-prod. Anyone repeating your staging verification on pre-prod will need a
  member that exists in `vl223`, so it would help to name one in the test instructions.

---

## Ready on our side

The Airtable sender, a curl one-liner, and the full test checklist (tags + address first, then
events registered) are written and waiting. The only unfilled value is the URL — one line
changes and we run the whole checklist the same day.
