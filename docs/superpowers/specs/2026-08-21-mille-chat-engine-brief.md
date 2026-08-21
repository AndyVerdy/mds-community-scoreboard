# Mille chat engine — decision brief for the CTO call

**Date:** 2026-08-21 · **Feeds:** the "how does Mille get into the app" brainstorm (Andy + CTO + Andrey Sr.)
**Origin:** CTO reviewed the POC widget, opened DevTools, and named the gap precisely: the client polls
every 2.5s until Mille answers — *"legitimate for a POC, never for production."* His verdict: two modules
are missing — a **chat engine** (async delivery) and a **client integration** (SDK or API). This brief is
the researched answer to both.

## The recommendation in one paragraph

**Build the chat engine on Supabase Realtime; don't buy an SDK; don't build a mobile SDK.** Messages
already live in our Postgres (`digest.olivia_messages`, written by the n8n workflow). A database trigger
(`realtime.send()`) broadcasts each new row to a **private channel per member** the moment it commits —
push, not poll. Supabase ships first-party client libraries for **JS (the web widget), Swift, and Flutter**,
so the app team subscribes to one channel with ~10 lines and builds their own UI against our API — exactly
the integration shape the CTO preferred ("share your API, we authenticate as an app, we tell you who the
request is from"). Marginal cost ≈ $0 (we're already on Supabase; Pro-tier Realtime = 500 concurrent
connections, 5M messages/month — 750 members chatting with one bot doesn't dent it).

## Why not the alternatives

| Option | Verdict | Why |
|---|---|---|
| **Keep polling** | ❌ | N clients × ~20 requests per answer. The CTO's exact objection, and #72's load risk squared. |
| **Buy chat SDK (Stream/Sendbird)** | ❌ | Best products, wrong economics + wrong architecture: floors are $349–499/mo for 5–10k MAU (we have ~750), and **their cloud becomes the system of record** — messages leave the warehouse that retrieval, eval, and the leak gate are built on. Sendbird caps retention at 6 months and gates export behind higher tiers. |
| **Twilio Conversations** | ❌ | Cheap (~$38/mo) but no official Flutter SDK, no UI kit, and the product is branded "(classic)" — stagnation signal. DIY everything on a fading platform. |
| **PubNub** | ❌ | On Flutter it's pub/sub transport only — we'd hand-build the chat layer anyway, so it buys nothing over Supabase. |
| **Intercom as the chat** | ⚠️ viable fallback | Already paid for; an external AI *can* answer as a teammate (webhook → our backend → Conversations API reply; Fin not required). But conversations then live in Intercom's cloud, UX is their support-inbox, and Flutter support is community-only. Keep as plan B if we decide not to own the client at all. |
| **Write our own mobile SDK** | ❌ | The CTO is right: a generated SDK "with holes" is worse than no SDK. The app team integrates the API directly. |

## What the chat engine v1 actually is (small — the pieces mostly exist)

1. **Send** — `POST /api/olivia/widget/messages` (exists). Returns immediately; the answer arrives by push.
2. **Push** — new: DB trigger on `digest.olivia_messages` → `realtime.send()` → private channel
   `mille:{member}`. Clients subscribe (supabase-js / supabase-swift / supabase_flutter). Auth: our API
   mints a short-lived Realtime JWT per session — RLS on `realtime.messages` restricts each member to
   their own channel. No new infra, no sockets on Render.
3. **Catch-up** — `GET /api/olivia/widget/messages?after=<id>` (exists). Broadcast is at-most-once, so on
   every (re)subscribe the client runs one catch-up query — this is the standard Supabase pattern, and it
   makes app-backgrounding/reconnects lossless. The table stays the source of truth.
4. **Identity** — per the agreed model: the app's backend authenticates with an app token and passes the
   member identifier; their MongoDB ID gets synced onto our member records once for exact matching
   (fallback: email). Identity resolution stays server-side on our end; the phone the RPCs key on never
   leaves us.
5. **Docs** — extend the live Swagger (digest.mds.co/olivia-docs) with the subscribe contract + a Flutter
   snippet. That page plus the token is the whole "SDK".

The web widget switches to the same channel (drops its polling), so web and app ride one mechanism.

**Not in v1:** delivery/read states, typing indicator sent to Mille, push notifications (APNs/FCM),
offline outbox. All addable on the same rails; push notifications are the first one worth its cost.

## Effort and sequencing

Realtime trigger + channel auth + widget switch ≈ 1–2 sessions. Identity mapping (Mongo ID sync +
per-member threads — replaces the single hardcoded identity) is the real ticket, and it is the same work
#74-adjacent identity plumbing already on the board. Proposal: file **chat engine v1** as one ticket with
the two halves (transport · identity), sequence it against #97 build and #72 load test at the next
priority call. The load test then measures the REAL transport, not the poll loop.
