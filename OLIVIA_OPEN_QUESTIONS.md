> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia — Events / Attendees: Questions & Fixes

> Opened 2026-07-23. Goal: correct attendee info for events. Chain: **AT Event Roster `tblfTLRfAqBhBZlc4`**
> → **Supabase `digest.event_registrations`** → **`event_who` / `event_lookup`** → Olivia.

## ✅ Answered by the events team (2026-07-23)

- **Confirmed-attendee rule = `Ticket Status = Confirmed` AND `Ticket for` ∈ {`MDS Member`, `MDS Member's Business Guest`}.**
  ("No Show" is a **bug** — team will investigate — so it's excluded, not counted.)
- **`Venue Capacity` = the event capacity.** So spots-left = capacity − confirmed, *when the field is set*
  (it's blank on some events, incl. the main Summit → then Olivia must not invent a number).
- Reference: **MDS Summit Singapore = 81 confirmed members** (165 roster rows → drop 37 Unconfirmed + 8 No-Show + 13 MDS Team + 20 partners + other plus-ones).

## 🐞 Bugs caught in live testing (2026-07-23) — the "why"

1. **"60+" instead of ~81.** `event_who` returns a *name list hard-capped at 60* and **no count**; its prompt says "60 rows shown → say 60+". It never computes the real number, and it doesn't filter to confirmed members. → should return the true confirmed count (81).
2. **Guest question punted to the team.** "can i bring guests to summit?" routed to the **`action`** lane ("passed to the MDS team") — but the answer is in the data: **Summit = "Open to Guests"**. A guest-**policy** question was misread as a "do something" request. → route guest-policy questions to the **events** lane (which already renders the policy).
3. **"Got it 👍 …" is unnatural.** For a *question*, "Got it, passed to the team" reads like a task-ack ("got what?"). → (a) questions shouldn't land in `action`; (b) when something genuinely can't be answered, the copy should read "I don't have that one — I've flagged it for the team," not "Got it."

## ✅ Built + verified LIVE (2026-07-23)

- **B1 — Guest-policy routing DONE.** `Plan Request` `guestAsk` detector → routes "can I bring a guest / +1 / my wife to [event]" to the **events** lane, which answers from `guests_policy`. Verified: Summit = "Open to Guests" → Olivia can now say yes. (routing sim: 4 guest phrasings → events; regressions unchanged.)
- **B2 — Attendee count DONE.** `Ticket Status` + `Ticket for` synced into `event_registrations` (migration `event_registrations_ticket_status_for` + `ROSTER_FIELDS`; 17,744 rows backfilled). `event_who` now returns Confirmed + Member/Business-Guest only, with the **true total** (`total_going`). **Verified: Summit = 81** (names filtered, no staff/partners). Prompt leads with the exact number; "60+" instruction removed.
- **B3 — Spots-left DONE.** `event_lookup` `regs` CTE now counts only confirmed members/guests; `spots_left` = `venue_capacity` − confirmed, **only when capacity is set** (Summit blank → null → no number; Women's Lunch cap 20 → 20). Chapter gate re-verified intact.
- **B4 — Action ack DONE.** No more "Got it 👍"; now "That's one for the MDS team rather than something I can do myself yet — I've flagged it… _Passed along:_ …". Guest questions no longer fall into this lane.
- **Leak gate green** (+2 checks: Unconfirmed member and Confirmed Staff proven excluded from names AND the total). `event_who` grants restored after the drop+create.
- ⚠️ **Durability:** `sync_events.py` is edited locally + ran once (backfill complete). **Commit + push it to `mds-digest-web`** so the daily sync keeps populating the two fields for new registrations.

## 📋 Still with the events team (data hygiene, not code)

- Fill blank **Venue Capacity** (incl. the main Summit) — needed for spots-left.
- **"No Show" bug** on future events (team investigating).
- **Missing Chapter link** — "New York Chapter Pickle & Padel Social July 2026" is hidden until tagged.
- Who owns keeping `Ticket Status` / `Ticket for` current (freshness = trust).

## 🐞 Sync durability + duplicate-record findings (2026-07-24)

- ✅ **`sync_events.py` committed + pushed** (mds-digest-web `9d8cd65`) — the daily sync now carries
  `Ticket Status`/`Ticket for` durably. The one day it ran the old script (Jul 24 15:16 UTC) left
  **4 registrations with null `ticket_status`**; healed by a re-run same day.
- 🚨 **Eugene has TWO Members-DB records, and Olivia told him he isn't registered for the Summit.**
  His WhatsApp phone resolves to **"Yevgeniy Khayman" (Staff)** — but his Singapore Summit
  registration (Confirmed, Super Early Bird, ticket for "MDS Team", ordered 2026-05-28 via MDS App)
  is linked to a **second record "Eugene Khayman" (no status)**. So "what am I registered for" shows
  his 71 old regs (Staff record) but not Singapore, and Olivia even suggested he register for it.
  Same duplicate-record class as Ian Sells. **Fix = Members-DB cleanup (Andy/team — never edited by
  Olivia builds):** merge/point the roster's Match-to-Member at the phone-linked record.
  Note: his ticket is "MDS Team", so per the attendee rule he'd still be excluded from *counts* —
  correct — but his OWN registration list should show it once the record link is fixed.
- ℹ️ Members-DB `full_name` for Eugene = "Yevgeniy" — he asked Olivia "Call me Eugene please"
  (request queued for the team). A durable preferred-name field is the correction-lane write-back
  item; in-session the LLM already adapted from history.
