# MDS Assistant — What's New

Everything below is live on production as of 3 August 2026.

---

## Finding things

- **Ask in your own words.** Search understands *meaning*, not just matching words — "anyone used
  Amazon's own freight service?" finds the AGL threads even though nobody wrote it that way. Same
  for people: skills and topics match without the exact keyword, and misspelled names resolve.
- **One question, every source.** Chats, the Facebook group, the member directory, events, partner
  deals and the video library — combined into one answer, each source labelled so you know where
  something came from.
- **Recent and credible first.** Between two matching threads, the newer one and the one from an
  established contributor come first. Anything older than a couple of months is dated so you know
  when it's from.
- **Links included.** Every person, thread, partner, event or video it recommends comes with its
  link.
- **Screenshot text is searchable.** What a posted chart or screenshot actually says is part of
  search.
- **Cities match however they're written.** "NYC", "New York, NY" and "new york" are one place.

## Getting answers

- **Your first message gets answered.** The welcome intro rides along after the answer instead of
  replacing it.
- **"Yes" delivers.** Accepting an offer gives you exactly what was just offered, bound to the
  assistant's most recent message.
- **Live feedback while you wait.** Read receipt and typing indicator within seconds, plus a short
  heads-up if an answer is taking longer.
- **Fast.** Median response time is down substantially, and the search step itself went from up to
  twelve seconds to under one.

## Accuracy

- **Quotes go to the right person.** On Facebook, replies usually start with the name of the person
  being answered — that name used to get read as the speaker. Fixed: if Betsy replies to Lee, the
  words are Betsy's. It also won't overstate a source: "launched a Kickstarter" never becomes "got
  funded".
- **Every claim is checked** against the records it retrieved before the message is sent, and every
  link has to match a real record.
- **Restricted content is named as restricted**, with its title and link — never silently hidden,
  never described.

## The community, in numbers

- **Chapters, live.** All 20 chapters with current member counts, leads, and the closest one to you.
- **Real counting.** Members by niche, state, chapter or revenue band are computed in the database
  with breakdowns — not estimated.
- **Events: asking about now returns now.** Present-tense event questions used to surface events
  from 2022–2025; they now return what's actually coming up, and a paraphrased ask reaches the
  right event however the calendar spells it.

## Your own account

- **Everything in one answer.** Plan, renewal date, next invoice and amount together, plus a direct
  billing-portal link.
- **Reports.** Type `report` + anything — it's filed to the team portal in your own words.
- **Tickets.** For requests that need a human, it offers to open a ticket with the MDS team and
  files it on your yes, with a ticket number.

---

## Under the hood (team)

- The Facebook group is in the warehouse — posts, comments and in-image text, all searchable.
- **Every conversation is filed against a member record**, not just a phone number, so history
  survives a number change and everything built on it joins reliably. Event sign-ups are connected
  to members the same way, and re-connect themselves on every sync.
- **A member activity log is accumulating** — append-only, nothing ever edited or deleted, with an
  alarm if it stops recording.
- **New, not yet visible to members: an expertise map and a connection graph.** Every member scored
  across 16 topics from what they've posted, presented and built, with the evidence attached, plus
  160,000 weighted connections mapping who genuinely knows whom. This is the foundation for
  personalized recommendations.
- Nightly data pipeline and an independent outage alarm, both heartbeat-monitored.
- Deploys go staging → promote with snapshots and one-command rollback; a 202-check safety gate
  runs before every ship.

## Known limits

- **Recommendations aren't personalized yet** — the expertise map exists, but answers don't use it
  yet. That's the next major piece of work.
- No transcripts yet — it finds the call and its deck, not what was said inside.
- The live calls calendar (Mogul / Expert / Channel Calls) isn't connected yet.
- Tap buttons are next; offers are "reply YES" today.

---

**Last full test against production: 169 questions — 153 passed, 10 partial, 6 failed (3.6%).**
The newest search and accuracy work landed after that run; its own full test is scheduled.

**React 👍 or 👎 to any answer** — it lands directly in the team's dashboard.
