> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.


# Olivia — to-do

Short list. Detail lives in `OLIVIA_TODO_DETAIL.md` and `SESSION_LOG.md`.
**Every item ships only when it's tested — and the test goes into the regression suite.**

> **Answering Andy:** short and simple, ideally 1–4 paragraphs. Not one-liners, not walls of text.
> Lead with the answer; he asks for detail when he wants it.

Beta is LIVE. 11 members invited 2026-07-28.

---

## NOW

**1. Daily review of real member answers**
Read *every* answer from beta members each day, not just the 👎 ones. A wrong answer nobody flags is
the dangerous one. Build a simple daily digest of all conversations.

**2. Real-member eval**
Replace synthetic test questions with what members actually ask. Their real questions become the
regression bank.

**3. E2E + regression suite**
One command that proves the whole thing still works: every source, every lane, the ticket flow, the
gate. Run it before any change ships.

---

## NEXT

**4. Prioritise the Olivia backlog**
Sit down with the full list and rank it against what beta members actually hit.

**5. Auto-subscribe members to WhatsApp digests**
Sign members up to daily or weekly digests directly, and point them at the member digest portal.

**6. Weekly auto-refresh of videos and partners**
Call the GroupOS MCP on a schedule so new videos and partner deals appear without anyone doing it by
hand. New videos are currently invisible in catch-ups.

**7. Fix the Chrome scraper**
Facebook capture still needs a manual scroll every Monday and Thursday. It's the only human step left
in the pipeline and it breaks often.

---

## KNOWN GAPS (unfixed, members will hit these)

**8. Event registrations not verified**
"What am I registered for" reads Airtable rollups already known to be wrong. Same audit that fixed
billing is still owed here — and members will ask.

**9. Revenue tier / chapter fields unverified**
Three different revenue-tier fields exist. Nobody has confirmed which one is right.

**10. Stripe status wording**
Members are told "trialing", "past_due", "unpaid" verbatim. Decide the wording.

**11. Stale billing data is invisible**
Stripe only re-syncs when a subscription changes, so a figure can be silently out of date and Olivia
can't warn about it.

**12. Restricted videos**
Sometimes denies a video exists instead of saying it's restricted.

**13. New videos missing from catch-ups**
13 videos added last week, none surfaced.

---

## DECISIONS FOR ANDY

- Stripe status wording (item 10)
- Which revenue-tier field is authoritative (item 9)
- Send the GroupOS video requirements doc (13 items, ready)
- Census sync — 735 forms not connected; blocks member personas
