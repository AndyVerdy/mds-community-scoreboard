# Brokered Intros — how Mille introduces members, safely

**In one breath.** Mille can already tell you who to meet. Now she can make the introduction — but she asks the other person first, and only if they tap Accept does any phone number move. No yes, no number.

**Example.** Lisa Harrington asks "Who should I meet in Singapore?" Mille ranks the Summit attendees by how well they match Lisa's focus areas; among equally good matches she favors members who joined MDS in the last year and people Lisa has no shared activity with yet, rotates names so nobody is recommended to everyone, and shows a handful — say Tracy Lin and four others. Each name is logged: "Mille recommended Tracy Lin to Lisa on this date."

Lisa writes: "connect me with Tracy Lin about 3PL." Before anything is sent, Mille checks, in order:
- Lisa is a member and eligible (during the pilot: uses Mille + Summit attendee). If not: "Intros are running as a Summit-attendee pilot right now — I'll open them up more widely after Singapore."
- Mille actually recommended Tracy to Lisa in the last 30 days. Hard rule — Lisa can only ask for people Mille herself suggested.
- Tracy is eligible too. If not: "I can't set that one up — Tracy isn't on my Summit intro list. Want me to suggest another attendee on 3PL?"
- Tracy hasn't declined Lisa before (a decline is final, and never revealed).
- No request between them is already pending.
- Lisa has fewer than 3 requests waiting; Tracy has had fewer than 3 requests this week from anyone.
- Tracy has a phone on record — otherwise Lisa hears honestly: "I can't reach Tracy on WhatsApp — want someone else, or should I pass this to the MDS team to intro by email?"

Only then does Tracy get an approved WhatsApp message: "Hi Tracy, fellow MDS member Lisa Harrington asked for an introduction to you about 3PL. Should I connect you two? Your contact details are shared only if you accept." — with Accept intro / Decline buttons. Lisa hears: "asked Tracy for their ok — I'll tell you the moment they respond. They see your name and the topic, nothing else."

Then one of three things:
- **Accept.** Tracy gets "Great — you're connected with Lisa Harrington. Start the conversation: wa.me/…" and Lisa gets "Tracy accepted your intro request — start the conversation: wa.me/…". The only moment a number appears anywhere.
- **Decline.** Tracy: "No problem — I won't share your details, and they'll simply hear the intro didn't happen." Lisa: "No connection with Tracy yet — I'll let you know if that changes." Lisa never learns it was a no; that pair is closed.
- **Silence.** After 7 days it lapses — Tracy gets zero reminders — and Lisa hears "I didn't get a response from Tracy this week, so I've let it rest. Want me to try again later — or someone else on 3PL?"

No name given? Mille shows the last people she recommended and asks which one.

**The rules.** Consent first, always. Targets only from your own recommendation log, 30 days. One pick = one request. Caps: 3 waiting per requester, 3 pings per target per week. Decline is final and never revealed. Silence lapses at 7 days, retryable, zero reminders. Unreachable members told honestly, never skipped. Pilot: both sides must be Mille users and Summit attendees. Accept is final — a later Decline is acknowledged but nothing reverses.

**What was built.** A ledger recording every request and its outcome. One piece of code owning every rule above (nothing lives in a prompt that could drift). Taps go straight to that code, never to the chatbot. Mille learned the intro tool and is told never to output a number or link herself. A background job expires silent requests. Automated safety checks run on every change — including "no reply can ever contain a number or link before an accept."

**What was tested.** Every scenario above exercised live without messaging any real member: no number leaked in any reply; an Accept tap flipped the ledger and both confirmations were delivered; "connect me with Tracy Lin" produced the real tool call and the correct refusal when a decline was on record; a backdated request expired on the next tick with the honest line delivered. An independent review asked one question — can a number ever move without a yes — and its findings were fixed before launch, including binding each tap to the exact request it answers, so a yes to one person can never be credited to another.

**Pilot limits.** Summit attendees only for now. The pick-list arrives as plain text — answering with the name works. Naming the person, or "one of the people you recommended", always works.
