# MDS Assistant — What's New

---

# Release 3 — Search & Memory

Live on production 3 Aug 2026.

## What's new

- **Ask in your own words.** Search now understands *meaning*, not just matching words. "Anyone
  used Amazon's own freight service?" finds the AGL threads even though nobody wrote it that way.
  Before, questions phrased differently from the original post came back empty.
- **Recent and credible answers first.** Between two matching threads, the newer one and the one
  from an established contributor come first. Anything older than a couple of months is dated so
  you know when it's from.
- **Answers arrive faster.** The search step went from up to twelve seconds to under one.
- **Quotes go to the right person.** On Facebook, replies usually start with the name of the
  person being answered — that name used to get read as the speaker. Fixed: if Betsy replies to
  Lee, the words are Betsy's. It also no longer overstates what a post says — "launched a
  Kickstarter" never becomes "got funded".
- **Events: asking about now returns now.** Present-tense event questions used to surface events
  from 2022–2025. They now return what's actually coming up, and paraphrased asks reach the right
  event however the calendar spells it.
- **Cities match however they're written.** "NYC", "New York, NY" and "new york" are one place.

## Under the hood (team)

- **Every conversation is filed against a member record**, not just a phone number — so history
  survives a number change, and everything built on it joins reliably.
- **Event sign-ups are connected to members**: 62% → effectively all sign-ups that can belong to
  a member (the rest are genuinely guests, spouses and vendor partners). It re-connects itself on
  every sync.
- **A member activity log now exists and is accumulating** — append-only, nothing is ever edited
  or deleted, with an alarm if it ever stops recording.
- **New (not yet visible to members): an expertise map and a connection graph.** Every member is
  scored across 16 topics from what they've posted, presented and built, with the evidence
  attached; 160,000 weighted connections map who genuinely knows whom. This is the foundation for
  personalized recommendations — it isn't used in answers yet.
- Safety gate now at 202 checks, green before every ship.

## Known limits

- Recommendations aren't personalized yet — the expertise map exists but answers don't use it
  yet. That's the next major piece of work.
- Full end-to-end test for this release hasn't been run yet; last measured score is Release 2's
  (3.6% wrong out of 169 questions).
- No transcripts yet — it finds the call and its deck, not what was said inside.
- The live calls calendar (Mogul / Expert / Channel Calls) isn't connected yet.
- Tap buttons are still next; offers are "reply YES" today.

---

# Releases 1 & 2

Live on production 3 Aug 2026. Last full test against production: **169 questions — 153 passed,
10 partial, 6 failed (3.6%)**.

---

## What's new

- **Your first message gets answered.** The welcome intro rides along after the answer instead of
  replacing it.
- **"Yes" delivers.** Accepting an offer delivers exactly what was just offered, bound to the
  assistant's most recent message.
- **Live feedback while you wait.** Read receipt and typing indicator within seconds; a short
  heads-up if an answer is taking longer.
- **Faster answers.** Median response time down substantially.
- **One question, every source.** Chats, the Facebook group, the member directory, events,
  partner deals and the video library — combined into one answer, each source labelled.
- **Links included.** Every person, thread, partner, event or video it recommends comes with its
  link.
- **People search by meaning.** Skills and topics match without the exact keyword; misspelled
  names and city aliases (NYC → New York) resolve; the your-own-niche filter bug on city
  searches is fixed.
- **Chapters, live.** All 20 chapters with current member counts, leads, and the closest one to
  you.
- **Real counting.** Members by niche, state, chapter or revenue band are computed in the
  database, with breakdowns.
- **Your account in one answer.** Plan, renewal date, next invoice and amount together, plus a
  direct billing-portal link.
- **Reports.** Type `report` + anything — it's filed to the team portal in your own words.
- **Tickets.** For requests that need a human, it offers to open a ticket with the MDS team and
  files it on your yes, with a ticket number.
- **Restricted content is named as restricted**, with title and link.
- **Screenshot text is searchable.** What a posted chart or screenshot says is part of search.

## Under the hood (team)

- Every factual claim is checked against the retrieved records before sending; every link must
  match a retrieved record exactly.
- The Facebook group is in the warehouse — posts, comments and in-image text, searchable.
- Nightly data pipeline and an independent outage alarm, both heartbeat-monitored.
- Deploys go staging → promote with snapshots and one-command rollback; a 190-check safety gate
  runs before every ship.

## Known limits

- No transcripts yet — it finds the call and its deck, not what was said inside.
- The live calls calendar (Mogul / Expert / Channel Calls) isn't connected yet.
- Tap buttons are next; offers are "reply YES" today.
- ~~In threads, a quote can occasionally get credited to the wrong person~~ — **fixed in Release 3.**

---

**React 👍 or 👎 to any answer** — it lands directly in the team's dashboard.
