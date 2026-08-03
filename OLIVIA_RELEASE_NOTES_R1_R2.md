# Olivia — what's new
### Production Releases 1 & 2 · covering 28 Jul – 3 Aug 2026

*Draft for Andy. Audience: the MDS team + beta testers. Nothing here is posted until you've read every line.*

---

Olivia is the MDS assistant on WhatsApp. She's still in **beta** — a handful of you have been
using her daily and telling us when she gets it wrong, which is the entire point.

Release 1 went live 31 July and was never announced. Release 2 went live 3 August. This covers
both, plus the things running underneath that never needed a release.

**Where quality actually stands:** the last full test was 169 questions against production —
**153 passed, 10 partial, 6 failed (3.6%)**, and one of those six was our test data being out of
date rather than her being wrong. That's measured, not estimated. It is not perfect and we're not
going to pretend otherwise.

---

## What you'll notice

**She answers your first message now.** Before, a question sent as your opening line got the
welcome menu instead of an answer — nine of the first twenty-two people hit that. Now the answer
comes first and the intro rides along after it.

**"Yes" means yes.** If she offers something and you say yes, y, sure, ok — she delivers it. She
used to occasionally forget what she'd just offered, or answer a *different* offer from earlier
in the thread. Both are fixed, and the acceptance now binds strictly to her most recent message.

**She reads the room, then answers.** You get a read receipt and a typing indicator within about
three seconds, and if an answer is taking a while she says so rather than leaving you staring at
nothing. Previously that whole feedback path was firing *after* the answer, which meant it never
fired at all.

**She's faster.** Median answer time is down substantially, with the biggest cut coming from
skipping work that a given question doesn't need.

**She looks everywhere before saying she can't find something.** Your WhatsApp chats, the
Facebook group, the member directory, events, partner deals and the video library — a question
that spans several of those gets one woven answer instead of whichever source she happened to
check first. When she does come up empty she now tells you specifically what she looked for.

**She gives you the link.** When she names a person, thread, partner, event or video as the
answer, the link to it comes with it. A solution you can't tap is homework.

**Finding people works properly.** Search by meaning, not just keywords — "paid ads" finds the
PPC people. Misspelled names resolve. Cities understand their aliases (NYC, New York). And a
real bug is gone: searching for members in a city used to silently filter by *your* niche and
revenue band too, so "members in NYC" returned nothing while nineteen were sitting there.

**Chapters, answered from live data.** All 20 chapters, current member counts, who leads them,
and the closest one to you — without asking where you live if we already have it on file.

**Counting is counted, not guessed.** How many members in a niche, a state, a chapter, a revenue
band — computed in the database. Where numbers legitimately don't add up (members belong to more
than one chapter), she says why instead of quietly showing a wrong total.

**Your own account, in one answer.** Plan, renewal date, next invoice and amount together — not
one field at a time. Billing questions link straight to your billing portal.

**Reports.** Type `report` followed by anything and it goes to the MDS team's portal in your own
words. She'll never promise you a follow-up she can't see happen.

**She can open a ticket** with the MDS team when something genuinely needs a human — she offers,
you say yes, and it's filed with a ticket number.

**Restricted means restricted.** A video you may not have access to is named as existing and
restricted, not denied. Pretending we don't have something is worse than saying you can't open it.

**She won't put words in your mouth** — mostly. See the known issues below.

---

## What we won't do, on purpose

- **Exact revenue figures never leave the database.** Bands only, for everyone. If a member
  posted a number publicly themselves, she can quote it *with attribution and the link* — as
  their words, never as our data.
- **No private contact details.** No emails, phone numbers or addresses, for anyone, whatever
  the reason given.
- **No verdicts on people.** She won't tell you whether to trust, hire or pay someone.
- **Nothing on beliefs, orientation, politics or ethnicity.** Not tracked, never inferred.
- **Sensitive matters** — a death, a crime, a legal matter — get a link to where it was discussed
  and nothing else. No summary, no verdict.
- **Why someone left MDS** is never shared.
- **She only ever sees chats you're in.** Enforced in the database, not by asking her nicely.

---

## Underneath (for the team)

- **Every factual claim is checked against the evidence before it sends.** A second model
  compares the draft to what was actually retrieved; unsupported claims trigger a rewrite, and a
  claim that can't be grounded twice becomes an honest "I couldn't verify that." Every link must
  appear verbatim in a retrieved record or it doesn't go out.
- **The Facebook group is in the warehouse** — 3,906 posts and 14,265 comments, searchable
  including the text *inside* screenshots, which a vision pass reads.
- **The pipeline runs itself.** Four derivation jobs nightly, heartbeat-monitored.
- **Outage alarm.** Independent of the workflow it watches, checks every five minutes, alerts
  Slack, repeats until resolved, and can't be silently latched off. Proven by forcing a failure.
- **The admin portal shows the truth**, including answers she failed to deliver.
- **Membership status gates every door** — cancelled or removed means no member data, enforced in
  SQL rather than in a prompt.
- **Safe deploys.** Every change goes staging → test → promote, with a snapshot taken before each
  production write and a one-command rollback.
- **A 190-check safety gate** runs before anything ships. Red blocks the release, no exceptions.

---

## Known issues — the honest list

- **Attribution.** She sometimes credits a quote to the wrong person: on Facebook a reply often
  begins with the name of whoever is being replied to, and she can read that as the speaker. She
  can also credit a commenter as the author of the post. This was the single biggest cluster in
  the last test and it's the first ticket in the next release. If you see her put words in
  someone's mouth, that's this — please flag it.
- **She can't see inside recordings.** There are no transcripts. She'll find the call and send
  you its deck; she cannot tell you what was said in it.
- **The live calls calendar isn't connected** — Mogul, Expert and Channel Calls. She'll say so
  rather than guess.
- **No tap buttons yet.** Offers are still "reply YES". Buttons are built next.
- **She still misses things that are there.** Roughly one answer in thirty. When it happens she
  says she couldn't find it rather than inventing something — but a miss is still a miss, and
  telling us is the fastest way it gets fixed.
- **She can't change anything** — your profile, your billing, your registrations. She'll file a
  ticket for the team instead.

---

**React 👍 or 👎 to any answer.** It lands in the team's dashboard and it's the fastest signal we
get. Everything in the "what you'll notice" list above started as someone telling us she got it
wrong.
