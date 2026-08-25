Millie status report, August twenty-fourth, evening.

Start with the headline. We had a hundred and ninety-two bad answers from the big
test. A hundred and seventeen of them are now good. That's sixty-one percent
fixed, up from zero this morning.

Now the part that actually mattered most. Dead links are gone. Completely. Before,
thirty-two answers went out with a link that was chopped in half and didn't work.
Now it's zero. That was the single worst thing she did, because a broken link makes
every other good thing in the answer look unreliable. It's fixed at the source, in
the code, not patched with a prompt.

Dates went from twenty-eight to ninety-nine across the same questions. So when she
tells you about a post or a call, she now tells you when it happened. That was the
biggest complaint in the whole test.

What's still weak, honestly. Partner offers are the worst area. When someone asks
for help with something a partner covers, she names the partner but often skips the
actual deal and the link. Three out of ten fixed. Second worst, she still sometimes
says nothing is on file when it is. One out of seven fixed. And counts. When she
gives you a list of members, she often doesn't tell you the real total. Five out of
thirteen fixed.

Now the important thing I found today, which wasn't part of the plan at all.

Eugene flagged that Millie couldn't find Hector for Khalid. It wasn't an Anthropic
outage. It was a real bug, and it was live. Khalid has two phone numbers. Our system
keeps one row per phone number, not per person. Every one of Millie's thirty-four
lookup tools started by checking that you match exactly one row. Two phones meant
two rows, which meant refused. So for Khalid, every single lookup came back empty,
and Millie confidently told him nothing was on file when the answer was right there.

Five members were in that state. Khalid, Vic Tor, Itamar Eshet, Leo Limin and
Christian Verhoeven. It's fixed and live now. I checked his exact question. She
returns Hector, the offer, twenty member mentions and five videos.

There was a second half to that same bug. Because each phone carries its own chat
list, she was only seeing half of Khalid's chats. He's in four, she saw two, so she
was hiding his own content from him. Also fixed. Three of the five members got chats
back.

And one more, which is worth a look before the twenty-first. Hector has a Summit
offer. Integrate before the thirty-first of August and get Hector's tool free for a
month. That offer lives in the event data, and the partner lookup never read it, so
nobody asking about Hector would ever hear about it. Now they will, but only if
they're actually registered for the Summit. That's live too.

Two things I need you to decide, because they're genuinely your call and I didn't
want to guess.

First. Removed members. Your ruling from July twenty-sixth says past members should
be findable, because saying "I don't have a member named Lori" was a lie. The test
says the opposite, that a removed member should get no profile at all. Those two
rules point in opposite directions and three answers are failing on it. Which one
stands?

Second, same shape. When someone asks what data Millie has access to, she gives the
capability menu. A previous session decided that deliberately, because her own
written answer kept getting blocked. The test says she should give an honest list of
her sources instead. Your call.

Last thing. All of this is on staging. Production is untouched and still running the
build from the launch. Nothing gets promoted without you.

That's the report.
