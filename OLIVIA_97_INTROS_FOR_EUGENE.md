# Brokered Intros — how Mille introduces members, and how it protects them

## 1. What this feature is, in one breath

Mille can already tell a member who they should meet. What she could not do is make the introduction. This feature gives her that power — safely. A member says "connect me with her", Mille goes and asks the other person first, and only if that person taps Accept does anyone's phone number move. No yes, no number. Ever.

## 2. Walk through it with an example

Lisa Harrington messages Mille: "Who should I meet in Singapore?"

Mille ranks the attendees by how well they match Lisa's focus areas; among equally good matches she favors members who joined MDS in the last year and people Lisa has no shared activity with yet, and rotates names so nobody is recommended to everyone — then shows Lisa a handful — say Tracy Lin, Wei Lin, and three others. Every one of those names is written into a recommendation log: "on this date, Mille recommended Tracy Lin to Lisa".

Now the new part. Lisa writes: "connect me with Tracy Lin about 3PL."

Mille recognises that as an intro request. Before anything is sent, she checks a chain of rules, in this order:

- Is Lisa a recognised member?
- Is Lisa eligible? During the pilot that means two things: she actually uses Mille, and she is a Summit attendee. If not, she hears: "Intros are running as a Summit-attendee pilot right now — I'll open them up more widely after Singapore. In the meantime I can still tell you who's worth meeting."
- Did Mille actually recommend Tracy to Lisa in the last 30 days? This is a hard rule: Lisa can only ask for intros to people Mille herself recommended to her. She can never talk Mille into pinging an arbitrary member.
- Is Tracy eligible too — a Mille user and a Summit attendee? If not: "I can't set that one up — intros are Summit-locked for now and Tracy isn't on my Summit intro list. Want me to suggest another attendee on 3PL?"
- Has Tracy already declined Lisa before? A decline is final. Lisa would hear "No connection with Tracy yet — I'll let you know if that changes", and nothing is sent to Tracy again.
- Is there already a pending request between them? Then Mille says it's already out.
- Does Lisa already have three requests waiting? Three is the cap per person.
- Has Tracy already received three intro requests this week, from anyone? Three is the cap per target, so nobody gets spammed.
- Does Tracy have a phone number on record? If not, Lisa hears an honest "I can't reach Tracy on WhatsApp — want someone else, or should I pass this to the MDS team to intro by email?"

Only when every check passes does Mille send Tracy an approved WhatsApp message: "Hi Tracy, fellow MDS member Lisa Harrington asked for an introduction to you about 3PL. Should I connect you two? Your contact details are shared only if you accept." — with two buttons, Accept intro and Decline. Lisa is told: "asked Tracy for their ok — I'll tell you the moment they respond. They see your name and the topic, nothing else."

Then three things can happen.

Tracy taps Accept. Tracy gets "Great — you're connected with Lisa Harrington. Start the conversation: wa.me/…" with Lisa's number. Lisa gets "Tracy accepted your intro request — start the conversation: wa.me/…" with Tracy's number. That is the only moment in the entire flow where a phone number appears anywhere.

Tracy taps Decline. Tracy hears "No problem — I won't share your details, and they'll simply hear the intro didn't happen." Lisa hears "No connection with Tracy yet — I'll let you know if that changes." Lisa never learns that Tracy said no, and that pair is closed.

Tracy never answers. After seven days the request quietly lapses — Tracy gets zero reminders — and Lisa hears "I didn't get a response from Tracy this week, so I've let it rest. Want me to try again later — or introduce you to someone else on 3PL?" Lisa may try again later.

If Lisa had said only "connect me with one of the people you recommended", without a name, Mille shows her the last people she recommended and asks which one. Lisa answers with the name and the same flow runs.

## 3. The rules, as a list

Consent first, always. Targets only from the asker's own recommendation log, 30 days. One pick is one request. Caps: three requests waiting per requester; three pings per target per week. Decline is final and never revealed. Silence expires at seven days, retryable, zero reminders to the target. Unreachable members are told honestly, never skipped. Eligibility during the pilot: both sides must be Mille users and Summit attendees. Accept is final — if someone taps Accept and later taps Decline, the links are already out; the late tap is acknowledged but nothing reverses.

## 4. What was built, in plain words

The ledger: every intro request is recorded with its outcome — accepted, declined, lapsed, or unreachable — and why.

The brain: one piece of code owns every rule above. Nothing about intros lives in a prompt where it could drift.

The ears: when Tracy taps Accept on her phone, that tap goes straight to the brain, not to the chatbot — so a tap is never "answered" as if it were a message.

The mouth: Mille was taught the intro tool, so "connect us" in chat triggers the real flow instead of her improvising. Her instructions say, in so many words, never to output a phone number or a wa.me link herself — only the intro flow may share contact, and only after the other member accepts.

The janitor: a background job expires seven-day-silent requests and tells the requester the honest line.

The safety net: automated checks run every time the system changes, including: the intro endpoint refuses anyone without the secret; an unknown phone gets nothing; and no reply can ever contain a phone number or a link before an accept.

## 5. What has been tested

Every scenario above was exercised against the live system without messaging any real member: no name given, a name given in dry-run, caps full, previously declined, an unrelated tap, an empty sweep — confirming no phone number leaks into any reply. An Accept tap was intercepted before the chatbot, flipped the ledger, and delivered both confirmation texts. "Connect me with Tracy Lin" produced a real tool call with her name and the correct refusal when a decline was on record. A request backdated eight days expired on the next tick and the honest expiry line was delivered. An independent review then checked the whole thing with one question — can a phone number ever move without a yes — and the items it raised were fixed before launch, including binding every tap to the exact request it answers, so a yes to one person can never be credited to another.

## 6. Known limits during the pilot

Summit attendees only for now. The pick-list arrives as plain text rather than a tappable list — answering with the name works. "Connect me with someone" may be read as asking for a human; naming a person, or saying "one of the people you recommended", always works.
