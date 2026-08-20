# Mille in-app widget (POC) — an Intercom-style messenger for the MDS mobile app

**Date:** 2026-08-20 · **Status:** design approved by Andy, not yet built · **Scope:** proof of concept only

Andy's reference is Intercom's in-app messenger: a launcher inside the app, a panel that slides up
over it, one continuous thread, close and you are back where you were. The goal of this POC is to
prove Mille answers inside a mobile app **without building a chat**. The app integrates one widget;
every chat behaviour lives on our side.

**Nothing in Mille changes.** No workflow edit, no migration, no prompt or seed change, no new
retrieval path — the widget is a new surface on the pipe that is already live. **The POC target is
the Swift app** (`mds-ios-app`, source in hand, distributable via Andy's Apple developer account).
The Flutter app is the destination once the POC earns it, and needs nothing different: the same URL
in the same kind of WebView.

## 1. What already exists (verified live 2026-08-20)

| Piece | State |
|---|---|
| `POST /api/olivia/ask` on `digest.mds.co` | **Live.** Bearer secret, `{question, target}` in, `{answer, route, target, wamid}` out. Measured this session: **HTTP 200 in 24.8s**, correct Summit answer, `route: "llm"`, `target: prod`. |
| `POST /api/olivia/test-chat` + `/admin/olivia/test` | Live admin chat page — same pipe, admin-cookie gated, staging/prod toggle. The widget reuses this logic. |
| `OliviaClient.swift` (mds-ios-app) | Already points at `/api/olivia/ask`, **on by default**. Secret is compiled into the binary. |
| `digest.olivia_messages` | Thread key is **`phone`**. There is no `channel` column — app turns and WhatsApp turns share one history. |
| Silent branch | A `wamid.SELFTEST*` prefix routes the turn down the workflow's `Eval (silent)?` path: saved to `olivia_messages`, **never sent via Meta**. |
| Member gate | All 20 retrieval RPCs gate on `is_active_member_status()`, resolved from the asker's phone. |

## 2. Decisions Andy made in this session

1. **POC only.** No identity plumbing, no member matching.
2. **Impersonate Andy.** The asking identity is server-side and fixed; it is never a request parameter.
3. **Shared memory is accepted.** Widget turns land in Andy's existing thread and become context for
   his WhatsApp chat, exactly as the admin test chat does today.
4. **One thread.** No Messages list — the panel opens straight into the conversation.
5. **In-app, not a browser.** The panel is presented inside the app; no address bar, no app switch.
6. **The app must not carry a chat implementation.** Widget in, everything else ours.

## 3. Architecture

```
Flutter/Swift app
  └─ launcher button → modal sheet (full height)
       └─ WebView → https://digest.mds.co/widget/mille?k=<WIDGET_TOKEN>
                      ├─ GET  /api/olivia/widget/history   (cookie auth)
                      └─ POST /api/olivia/widget/message   (cookie auth)
                                └─ n8n prod webhook (SELFTEST wamid, silent)
                                     └─ digest.olivia_messages ← polled for the reply
```

Three units, each independently testable:

**`/widget/mille` (page).** Validates `k` against `OLIVIA_WIDGET_TOKEN`, sets a short-lived httpOnly
session cookie, renders the messenger: greeting header (`Hi Andy 👋` + avatars), conversation,
input, close button. Mobile-first, dark and light, `noindex`. Consumes nothing but its two API
routes; produces no secrets to client JS.

**`POST /api/olivia/widget/message`.** Cookie-authorised. Body `{question}`. Fires the prod webhook
with a `wamid.SELFTEST_WIDGET_*` id and the fixed probe identity, polls `olivia_messages` for this
turn's reply, returns `{answer, route, wamid}` or `504` past the poll budget. Identity and the n8n
URL are server-side constants — the client cannot choose either.

**`GET /api/olivia/widget/history?limit=30`.** Cookie-authorised. Returns the recent turns of the
thread so the panel opens on a live conversation rather than a blank box.

**App side (both platforms).** One launcher button, one modal sheet, one WebView. No message
models, no networking, no chat state. Wording, layout and behaviour change on our deploy — no app
release.

## 4. Auth model

The widget token is held by the app and exchanged for an httpOnly cookie on first load, so no secret
is readable from page JavaScript. **This is POC-grade, and the spec says so plainly:** anyone holding
the URL token can chat as Andy, the same exposure the compiled Swift secret already carries. It is
acceptable because the identity is Andy's own and the token is rotatable from env. Before any member
sees this, the token is replaced by real identity (app login → member → phone), which is out of scope
here.

## 5. Latency and error handling

She takes **~25s typical, 50s server cap**. The panel therefore shows an explicit "Mille is
thinking…" state from the moment of send, keeps the input usable, and on `504` renders her timeout
line with a **Retry** that re-sends the same question. Network failure renders the same way. No
holding-message ladder, no fake streaming — the answer arrives whole.

## 6. Acceptance criteria

- The panel opens **inside** the app as a modal sheet — no external browser, no address bar.
- It opens on existing history, not an empty screen.
- A question sent from the panel returns her answer in the panel; measured round-trip recorded.
- The thinking state is visible for the whole wait; a `504` offers Retry and the retry succeeds.
- **Nothing reaches WhatsApp:** for every widget `wamid`, `digest.olivia_sends` has no row.
- An invalid or missing token gets `401` and no page.
- Proven in the Swift app first, on a TestFlight build. Flutter is not a POC acceptance criterion —
  the same URL in the same kind of WebView is all it will need.
- Leak gate `scripts/olivia_leak_gate.py` EXIT 0 (the widget adds a surface, not a retrieval path).

## 7. Explicitly out of scope

Per-user identity and matching · a Messages list or multiple threads · a `channel` column splitting
app history from WhatsApp history · images and quick-reply buttons · push notifications · streaming ·
rate limiting · any member other than Andy.

## 8. Traps this design must not re-learn

- **A `wamid.SELFTEST` prefix is what keeps the turn silent.** Lose the prefix and the widget starts
  sending real WhatsApp messages to Andy's phone.
- **The identity must never become a request parameter.** It is the only thing standing between a
  POC token and another member's data.
- **PostgREST reads `+` in a query string as a space** — Z-suffix any timestamp filter.
- **A 200 from the webhook is not an answer**; the answer only exists once it appears in
  `olivia_messages`. Poll, never assume.
