# Bank B — the regression net for everything built after 2026-08-16

`eval_bank_B_2026-08-23.json` · 52 organic questions · window **2026-08-16 → 2026-08-23** · LOCKED
(ticket **#119**). Bank A (`eval_bank_100_2026-08-16.json`, 100 Qs, 07-19→08-16) is unchanged and
still the older net; this one covers only what shipped after it froze.

Every question is a **real member ask, verbatim**, with its real asker and date, pulled from
`digest.olivia_messages` (`role='member'`, no SELFTEST, no resets). `expect` comes from the
tickets' ACs and rulings — never from what she actually replied.

## Coverage

| class | Qs | what it holds the line on (source tickets) |
|---|---|---|
| `SCHEDULE` | 8 | #85 schedule lane · **#114** venue-day "today" + Task 2b (rest of the venue-day, not 3 items) |
| `REGISTRATION_WHO_TO_MEET` | 9 | **#96** ≤10 names + true total · **#98** gate on the asker's own registration row · #95 equalizer · **#106** staff never in a member-facing list · #107 the closing intro offer |
| `INTROS` | 1 | **#97** consent-first (no number without a yes) · #107d pilot = Summit attendee + phone |
| `TRANSCRIPTS` | 7 | **#101** transcripts + entitlement (R6) · the 2026-08-22 answer rules (quote + speaker + timestamp IN the answer; never "transcripts unavailable") · #104 on the adjacent pair |
| `SPEAKERS` | 3 | **#103** one identity per speaker · agenda-sourced speaker lineups |
| `OFFER_BINDING` | 7 | **#112** (+#80): affirmative with a quantifier/typo binds to the offer and delivers ALL offered items; no pending offer = normal planning |
| `FINDER` | 8 | **#108** R1–R10 + the 🟢/🟡/🔴 field registry (union with reasons · chat rule R10 · revenue band vs exact) |
| `MILLIE_NAME` | 3 | Millie rename (queue ④) · #107 PS placement |
| `QUALITY_FIXES` | 6 | #86 reminders (venue-zone anchoring, corrections) · #94 ledger-backed guest picks · the 2026-08-22 RULE ZERO gate fix (clarifying questions are not "unverifiable") · R9 no scores/ranks |
| **total** | **52** | |

Multi-turn sequences (`seq`, fire adjacent, no reset between): `lisa` (identity claim must not
unlock names) · `cashfees` (#104 adjacency) · `tiktok` ("yes booth") · `storage` (bare "yes") ·
`helium` (a decline is not an affirmative) · `reseller` (Belén's 4-turn finder thread) · `ramon`
(revenue band vs exact) · `mogul`, `nightout`.

## Who asked

Source pool: **213** organic asks from **23** askers in the window — **179 staff / 34 members**.
Bank B takes **52** of them: **42 staff** (Andy 19 · Jerome 6 · Belén 5 · Sashani 5 · Eugene 4 ·
Ian 1 · Juancho 1 · Brian 1) and **10 members** (Jamie Graham 4 · Douglas Patrick Iske 2 ·
Tracy Lin 2 · Tamkin Collins 1 · Anjie Liu 1). Staff asks count as organic — bank A was built the
same way — but the skew is real and worth saying out loud: most of the post-08-16 traffic is the
team testing before the Summit.

## No organic asks yet (not fabricated)

- **#99 "show me the rest"** for who-to-meet — no continuation ask in this window (bank A holds the original).
- **#107's Yes → intro picker** — the offers went out 08-22/23 and nobody has replied yet; template
  and list taps are not `olivia_messages` rows at all (they live in `olivia_webhook_events`), so
  there is no organic turn to take. INTROS therefore holds 1 question.
- **#109** requester-side notices (accept · decline · 7-day lapse) — system sends, never a member ask.
- **#105** webhook signature — invisible to a member.
- **#103's in-transcript letter→name mapping** — nobody organically asked "who said X in video Y";
  the three `SPEAKERS` questions are event-agenda lineups, and in-transcript attribution is
  exercised only through 5019 (the quote must carry its speaker).
- **Finder phase 2/3** (content/video/partner/event filters, #116) — not shipped, so Ian's
  "who are the partners there and what are their offers" was deliberately left out.

## Run it, score it

```bash
python3 scripts/run_eval_100.py --bank eval_bank_B_2026-08-23.json --dry-run    # 62 turns, fires nothing
python3 scripts/run_eval_100.py --bank eval_bank_B_2026-08-23.json --staging    # the real run
```

`--bank` defaults to the 100-question bank, so bank A runs exactly as before.

- **Run it AFTER bank A, never beside it** — one probe member, one conversation state.
- Score like `OLIVIA_SMOKE_2026-08-21.md`: pair each Q with the reply, judge against `expect`
  (PASS / PARTIAL / FAIL), **re-verify every non-PASS by hand**, then write
  `OLIVIA_SMOKE_BANK_B_<date>.md` with per-class results and before/after numbers.
- `soft: true` = the ruling allows latitude; judge intent, not wording.
- Don't reorder: `seq` questions must stay adjacent, and the bare affirmatives only mean anything
  in the position they sit in (the standalone "Yes" fires first in its class, straight after a
  reset, precisely because there must be no pending offer).
- **Locked.** Questions are never edited or invented; retiring always-passing questions is a
  sprint-close ritual, not an in-run edit.
