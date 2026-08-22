# Brokered Intros (#97) — what was built, how it works, and what is proven

## 1. What this feature is, in one breath

Today Mille can tell a member who they should meet. What she could not do is make the introduction. This ticket gives her that power — safely. A member says "connect me with her", Mille goes and asks the other person first, and only if that person taps Accept does anyone's phone number move. No yes, no number. Ever.

## 2. Walk through it with a real example

Lisa Harrington messages Mille: "Who should I meet in Singapore?"

That question is handled by the who-to-meet logic that already existed before this ticket: Mille ranks the attendees by how well they match Lisa's focus areas; among equally good matches she favors members who joined MDS in the last year and people Lisa has no shared activity with yet, and rotates names so nobody is recommended to everyone — then shows Lisa a handful — say Tracy Lin, Wei Lin, and three others. Every one of those names is written into a recommendation log: "on this date, Mille recommended Tracy Lin to Lisa".

Now the new part. Lisa writes: "connect me with Tracy Lin about 3PL."

Mille recognises that as an intro request and calls the new intro tool. Before anything is sent, the tool checks a chain of rules, in this order:

- Is Lisa a recognised member? Yes.
- Is Lisa eligible? Eligible means two things, both locked by you today: she actually uses Mille (real messages on record), and she is registered for the Summit. If she is not registered, she hears: "Intros are running as a Summit-attendee pilot right now — I'll open them up more widely after Singapore. In the meantime I can still tell you who's worth meeting." (Your correction from tonight — registration is effectively closed, so she never invites anyone to register.)
- Did Mille actually recommend Tracy to Lisa in the last 30 days? This is a hard rule: Lisa can only ask for intros to people Mille herself recommended to her. She can never talk Mille into pinging an arbitrary member.
- Is Tracy eligible too — a Mille user AND a Summit attendee? If not: "I can't set that one up — intros are Summit-locked for now and Tracy isn't on my Summit intro list. Want me to suggest another attendee on 3PL?"
- Has Tracy already declined Lisa before? A decline is final. Lisa would hear "No connection with Tracy yet — I'll let you know if that changes", and nothing is sent to Tracy again, ever.
- Is there already a pending request between them? Then Mille says it's already out.
- Does Lisa already have three requests waiting? Three is the cap per person.
- Has Tracy already received three intro requests this week from anyone? Three is the cap per target, so nobody gets spammed.
- Does Tracy have a phone number on record? If not, Lisa hears an honest "I can't reach Tracy on WhatsApp — want someone else, or should I pass this to the MDS team to intro by email?" And the attempt is logged as unreachable, so a phone-less member is never silently skipped.

Only when every check passes does Mille send Tracy an approved WhatsApp template: "Hi Tracy, fellow MDS member Lisa Harrington asked for an introduction to you about 3PL. Should I connect you two? Your contact details are shared only if you accept." — with two buttons, Accept intro and Decline. Lisa is told: "asked Tracy for their ok — I'll tell you the moment they respond. They see your name and the topic, nothing else."

Then three things can happen.

Tracy taps Accept. Tracy gets "Great — you're connected with Lisa Harrington. Start the conversation: wa.me/…" with Lisa's number. Lisa gets "Tracy accepted your intro request — start the conversation: wa.me/…" with Tracy's number. That is the only moment in the entire flow where a phone number appears anywhere.

Tracy taps Decline. Tracy hears "No problem — I won't share your details, and they'll simply hear the intro didn't happen." Lisa hears "No connection with Tracy yet — I'll let you know if that changes." Lisa never learns that Tracy said no, and that pair is closed for good.

Tracy never answers. After seven days the request quietly lapses — Tracy gets zero reminders — and Lisa hears "I didn't get a response from Tracy this week, so I've let it rest. Want me to try again later — or introduce you to someone else on 3PL?" Lisa may try again later.

If Lisa had said only "connect me with one of the people you recommended", without a name, Mille shows her the last people she recommended and asks which one. Lisa answers with the name and the same flow runs.

## 3. The rules, as a list, so nothing is missed

Consent first, always. Targets only from the asker's own recommendation log, 30 days. One pick is one request. Caps: three pending per requester, three pings per target per week. Decline is final and never revealed. Silence expires at seven days, retryable, zero reminders to the target. Unreachable members are told honestly, never skipped. Eligibility, locked today: both sides must be Mille users and Summit registrants; the "used Mille in the last 30 days" idea is parked. And your ruling from tonight: Accept is final — if someone taps Accept and later taps Decline, the links are already out, so the late tap is acknowledged ("that intro was already accepted, you're already connected") and recorded, but nothing reverses.

## 4. What was actually built in those hours — seven steps

Step one, the ledger. The intro table in the warehouse learned a status for "couldn't reach this person" and a column for why each request ended: a tap, the seven-day sweep, no phone, not on WhatsApp, or a send failure.

Step two, the brain. One API endpoint on our digest server owns every rule above. Request, pick-list, tap handling, and the seven-day sweep all live in that one file, in code, in git. Nothing about intros lives in a prompt where it could drift, and nothing lives in the database where it could be bypassed.

Step three, proof without risk. I hit that endpoint with every scenario — no name given, a name given in dry-run, caps full, previously declined, an unrelated tap, an empty sweep — and confirmed nobody real got messaged and no phone number leaked into any reply.

Step four, the ears. When Tracy taps Accept on her phone, that tap has to reach the brain, not the chatbot. On the way I found a real bug: the workflow was throwing those template taps away entirely — which is why Eugene's Decline from the proof of concept was never processed. Now every Accept or Decline is intercepted before the language model ever sees it, and ordinary messages flow exactly as before.

Step five, the mouth. Mille was taught the intro tool, so "connect us" in chat triggers the real flow instead of her improvising. Her instructions also say, in so many words, never to output a phone number or a wa.me link herself — only the intro flow may share contact, and only after the other member accepts.

Step six, the janitor. The every-minute reminder job also expires seven-day-silent requests and tells the requester the honest line.

Step seven, the paperwork. Three new checks in the leak gate — our automatic safety test — now run every time: the intro endpoint refuses anyone without the secret; an unknown phone gets nothing; and a dry-run request can never contain a phone number or a link. The handbook describes the whole flow.

## 5. What is validated, with the numbers

Every step was built by one agent and reviewed by a different, independent agent before the next began, and anything the reviewer flagged was fixed and re-reviewed. Here is what each proof actually showed.

The endpoint tests: nine of ten scenarios passed on the live server and the tenth was proven by database query; zero real messages were sent during the whole test — the outgoing-message count stayed flat — and the database was restored to exactly its starting state, checked independently by the reviewer.

The tap branch on staging: a crafted Accept tap was swallowed before the model — zero chatbot turns for it, the ledger flipped to accepted, and two confirmation texts arrived on your phone, both showing "delivered" in the delivery log, not just "sent". A plain "hello" went down the normal path untouched.

The bug fix on inbound messages was checked against the full history of webhook events: every template button tap the system has ever received was an intro tap, and the existing Yes / No-thanks buttons use a different message shape and were not affected.

The intro tool on staging: "connect me with Tracy Lin" produced a real tool call with her name, the endpoint answered, and — because I had pre-seeded a decline for that pair as a safety brake — the request was refused before any send. That proved the whole chain end to end with a real name and zero messages to anyone.

The sweep: a test request backdated eight days was expired on the very next minute tick and the honest expiry line landed on your phone, delivered.

The safety gate: 263 checks before, 266 after, all passing, exit code zero.

## 6. What the final review found, and where we are now

At the end, a senior review agent went over everything as a whole, with the privacy invariant as its headline. Its verdict: strong build, not ready to promote yet, three must-fix items.

First and most important: when a tap came in, the endpoint matched it to the target's newest pending request instead of to the specific request that was tapped. If two people had asked Tracy at once, her yes to Lisa could have been credited to the other person. The fix is small — WhatsApp tells us exactly which message a tap replies to, and we already capture that — so taps are now bound to the exact request.

Second: Eugene's real sequence from the proof of concept — Accept, then Decline four minutes later — had no defined behaviour. Your ruling tonight settles it: accept is final, late taps are acknowledged and logged, never handed to the chatbot. Eugene's old row has been set to declined, his last word, so it won't send you a misleading "no response" message next week.

Third: one workflow node would have errored instead of failing gracefully if our server was ever unreachable, losing the tap. Fixed to fail open, and being probed by deliberately pointing the workflow at a dead address.

Plus ten smaller hardening items — picking the right phone when a member has two records, guarding against self-intros, sanitising the topic text a member types, stopping the sweep from overlapping itself, and so on. All of that is in one fix pass that is running as this is written, followed by one more scoped review.

## 7. What is live right now, and what is waiting

Live on production: the endpoint, the ledger changes, and the sweep tick. But they are inert for members, because the production workflow does not yet have the intro tool or the tap branch — those are on staging only. So today no member can start or receive an intro, and nothing changes for anyone until you run promote.

Waiting on you, after the fix pass and its review: one promote command, which moves the tap branch and the intro tool to production together — they must go together, because the tool without the ears would create requests nobody could answer. Then one real tap on a phone is the last proof.

## 8. Known, deliberately left for later

Two pre-existing phrasing collisions: "connect me with someone" gets routed to the talk-to-a-human lane by an older rule, while "connect me with a name" works — a small follow-up. The pick-list is sent as plain text rather than a tappable WhatsApp list; answering by name works and is proven. And a new ticket, #105: the webhook that receives WhatsApp messages should verify Meta's signature so nobody can forge a message — more important now that a forged Accept would mean something, though the exact-request binding already makes that very hard. That ships next session, before any wide announcement.
