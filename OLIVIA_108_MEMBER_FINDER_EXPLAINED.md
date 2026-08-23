# The Member Finder — the whole story, in plain words

> ⚠️ **Written before the build — its numbers are history, not status.** Its 21 / 99, "twenty-two
> tests", "six probes", "six checks" and "nine steps" are superseded by the #108 close block on
> `OLIVIA_SPRINT_4.md` (17 / 122 over 735 actives; 57 finder tests; 9 probes + 3 re-probes; 26 gate checks; 10 tasks). The addendum at the end still stands.

*Written to be listened to. No code, no jargon. About nine minutes.*

---

## Stage one — where we are today

Millie is the assistant our members talk to on WhatsApp. She knows a lot. She knows who is in the
community, what they sell, where they live, which chats they belong to, which events they signed up
for, what was said on the calls, and which partners offer what. When a member asks her something, she
picks one of about twenty tools, looks the answer up, and writes back in her own words.

Most of the time this works. Ask her what's on at the Summit, she tells you. Ask her who knows about
Amazon ads, she finds people. Ask her for a partner deal, she brings the deal.

But every one of those twenty tools was built for one shape of question. Each tool has its own little
list of things you're allowed to ask it about. And that turns out to be the whole problem.

---

## Stage two — the moment it broke

Belen asked Millie a simple question. Which resellers are coming to the Summit?

That is not an exotic question. It is exactly the kind of thing you'd ask before flying to Singapore.
You want to know who your people are, so you can find them in the room.

Millie answered — confidently — with a list of brand owners. Not resellers. And she missed the three
people who actually are resellers and actually are going.

She wasn't guessing wildly. She did her best with what she had. But her best was wrong, and it was
wrong in the way that damages trust: it sounded right.

---

## Stage three — what was actually happening under the hood

Two separate faults, and I confirmed both against the live system before writing a line of code.

The first fault: Millie has no way to say the word "reseller" as a filter. None of her tools accept
it. So the word gets converted into topic words and matched against the text people wrote about
themselves. A brand owner who once wrote a paragraph mentioning wholesale looks like a match. An
actual reseller who never wrote about it looks like nothing. That's how the answer inverted.

The second fault is smaller and dumber. When Millie decides on her own to look up who is attending an
event, her request goes to the wrong door. Instead of the attendee list, she gets back the event
agenda — arrivals, sessions, times. A people question answered with a timetable. The attendee code
exists and works perfectly; her call just never reaches it. I proved it live: same phone number, two
requests, one comes back with the agenda, the other with the attendee logic.

And underneath both faults sits the real one. Her filters don't stack. If you ask for resellers, at
the Summit, in Europe, doing five to ten million, grouped by country, that question spans three
different tools that cannot be combined. So she falls back on guessing. Every new kind of question we
have hit this year has been answered by hand-adding one more setting to one more tool. That approach
has run out of road.

---

## Stage four — the decision you made

I laid out four ways to define a reseller, with the real numbers behind each.

There are fifteen people going to the Summit who sit in the MDS Resellers WhatsApp chat. That's
behaviour — they chose to be in the room where resellers talk.

There are nine going who ticked wholesale or arbitrage as their business model on an MDS form. That's
declaration — it's what they told us, and it's as fresh as the last form they filled in.

Only three people are both.

You chose the union — everyone in either group, twenty-one people — with the reason shown next to
each name. That is the right call, and it's the design decision the whole build hangs on. A member
sitting in the resellers chat who never filled in the form is still a real reseller. A member who
declared it but never joined the chat is still a real reseller. Instead of us silently picking which
evidence counts, Millie shows the evidence: in the resellers chat, or wholesale and arbitrage, or
both. The member decides what that's worth.

---

## Stage five — what we're building

One tool. We're calling it the member finder.

Think of it like the filters down the side of a shopping site. You tick a brand, then a size, then a
price range, and the list narrows as you go. Nobody builds a separate shop for each combination. You
build one filter panel.

That's the finder. The filters are: which WhatsApp chat someone is in, what business model they run,
which event they're attending, their city, state or country, their revenue band, their product niche
or category, and words in their expertise. You can use one. You can use six. They stack.

Three shapes of answer come out. Names, with the reason each person matched. A count, when the member
just wants the number. Or a breakdown — the same set grouped by country, or by revenue band, or by
whichever dimension they asked for.

And follow-ups finally work. When a member says "of those, who's in Europe", Millie doesn't start
over and guess again. She takes the filter set she just ran and adds one more filter to it. The
conversation narrows the way a conversation should.

One more thing matters here, and it's invisible to members. Right now the privacy rules — never show
more than ten names, always tell the truth about the total, never show staff records in a member
list, never reveal an attendee list to someone who isn't going to that event — are written separately
inside each tool. Separately means they drift. That drift is exactly how a test record of yours once
leaked real attendee names through one tool while the other tools correctly hid it. In the finder,
those rules are written once, in one place, and every question goes through them.

---

## Stage six — what it feels like after

Same member, same question, a few weeks from now.

Belen asks which resellers are coming to the Summit. Millie comes back with up to ten names, and next
to each one it says why: this person is in the MDS Resellers chat, this one declared wholesale, this
one is both. She says plainly that twenty-one match in total and offers the rest. If Belen then says
"only the ones in Europe", the list narrows. If she says "how many from each country", she gets the
breakdown.

And if someone who isn't registered for the Summit asks the same question, they get the number and
nothing else — no names — without Millie explaining our internal rules to them.

---

## Stage seven — how we prove it before it goes anywhere near members

The work is split into nine steps, and nothing touches the live assistant until the end.

The thinking part — how a word like "reseller" becomes a filter, how reasons are worded, how the caps
are enforced — is written as a separate piece of logic with twenty-two automated tests around it.
Those tests run in seconds and they run every time.

Then the lane itself gets built and shipped, but nothing calls it yet. It sits there, live and
harmless, while we test it directly.

Then the new tool goes onto the staging copy of Millie — a full duplicate that members never touch —
and we ask her the real questions there. Six of them: resellers at the Summit, resellers across MDS,
the narrowing follow-up, the group-by, the same question from someone not registered, and a plain
who's-coming to confirm the wrong-door bug is dead. For the ones that need an attendee's point of
view, we temporarily register a test row, ask, and delete it in the same sitting — the same trick we
used in an earlier ticket, and the deletion step is mandatory whether or not the test passed.

Then the safety gate runs. It's a script with a couple of hundred checks that tries to make Millie
leak something. Six new checks join it for this lane: it must refuse a request without the password,
return nothing for an unknown phone number, reject a filter it doesn't recognise, refuse to dump the
whole roster when no filter is given, never list more than ten names, and never let a staff record or
an internal score escape.

Only then does it come to you to promote. That's your command, not mine — and if anything looks wrong
afterwards, both halves roll back in about a minute.

---

## Stage eight — speed, money, and what could go wrong

Speed: I measured it rather than guessing. The finder's database work takes about seven tenths of a
second, which is the same ballpark as the tool it's replacing. Layered questions actually get faster,
because today they take two or three separate lookups and this takes one.

Money: the new tool adds roughly eight to eleven dollars a month in model costs at current volumes.
While measuring that, I found something bigger and unrelated — the node that writes Millie's answers
pays full price for the same instructions on every single message, when it could be reusing a cached
copy at about a tenth of the cost. Two of the smaller nodes already do this correctly. That finding is
now written into the cost ticket, with the steps to fix it and the honest caveat that the saving lands
on one half of the bill, not all of it.

Risk: nothing gets deleted, no data structure changes, and no existing tool changes behaviour — apart
from the wrong-door fix, and that door is already broken today, so it can only improve. The real risk
is subtler. Millie might start reaching for the new finder on questions where an older tool was
better — particularly the one that searches by meaning rather than by filters. That wouldn't break
anything, it would just make some answers worse. The way to catch it is the hundred-question test
bank, run on staging before you promote. That's a decision that costs money to run, so it's yours to
make, not mine.

---

## Stage nine — what I need from you

Two things, at the end, not now. First, run the promote when the staging proof is in front of you.
Second, tell me whether to run the hundred-question bank before that promote — I recommend yes.

Everything else is mine to build. The specification and the step-by-step plan are both written and
committed, and the next move is simply to start on step one.

---

## Addendum — three rulings you made after this was written

*About two minutes. Same plain voice.*

**One tool, not two.** You asked whether a member finder and a content finder should be separate, and
the answer was no. It is one finder with two groups of filters: *who* — what kind of seller someone
is, where they are, which chat and which event — and *what* — what was said, in which source, when,
by whom, in which video. Used together they intersect, so "what did resellers going to the Summit say
about TikTok" is one question, not a copy-and-paste between two tools. This ticket builds the *who*
half and the plumbing; content and video ride on the same plumbing next.

**Every layer, and filtering is not the same as showing.** The finder registers every data layer we
hold — people, events, chats and posts, videos, partners, forms, the dossiers, the graph, personas —
and every field carries a class. Green fields may be filtered on, grouped by, and printed beside a
name. Amber fields — SKU counts, brands, years selling, age, revenue sums, scores — may be filtered
and grouped freely, but never printed beside a name, and a question that uses one of them gets numbers
back, never names, because naming who matched "500 SKUs" gives the number away anyway. Red fields —
exact revenue, contacts, payments, personas — cannot be filtered on at all. Revenue is the example you
gave: Millie can use it to decide who is in the set; she never says it.

**Chats.** We have restricted chats, and who is in them and what they discuss is not told to someone
who is not in them. But membership is a signal Millie may use for anyone: the Resellers chat helps
identify resellers, the Supplements chat helps identify supplement sellers, and so on — and the same
idea now covers TikTok, DTC, retail, large-SKU and under-30. So a reseller who is only in the chat
still shows up in the answer. The difference is in the reason line: if you are in that chat yourself,
Millie says "in MDS Resellers"; if you are not, she just says "reseller" and leaves the chat unnamed.
And if someone asks outright who is in a chat they are not part of, they get the number, not the
names.
