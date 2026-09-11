# Olivia eval — 2026-09-11 — 100 judged · PASS 78 · PARTIAL 8 · FAIL 14 (14.0%)  [target <1%]

## Health by source
- 🔴 **CHAPTERS**: 3 asked · 1 fail (33%) · 0 partial
- 🔴 **VIDEOS**: 12 asked · 4 fail (33%) · 0 partial
- 🔴 **EXPERT**: 10 asked · 3 fail (30%) · 1 partial
- 🔴 **SELF_ACCOUNT**: 4 asked · 1 fail (25%) · 0 partial
- 🔴 **FACEBOOK**: 5 asked · 1 fail (20%) · 0 partial
- 🔴 **MEMBER**: 10 asked · 2 fail (20%) · 1 partial
- 🟡 **CHAT_CONTENT**: 13 asked · 1 fail (8%) · 0 partial
- 🟡 **TACTICS**: 14 asked · 1 fail (7%) · 0 partial
- 🟢 **CAPABILITY**: 8 asked · 0 fail (0%) · 1 partial
- 🟢 **DIGEST**: 3 asked · 0 fail (0%) · 1 partial
- 🟢 **EVENTS**: 7 asked · 0 fail (0%) · 2 partial
- 🟢 **LOGISTICS**: 2 asked · 0 fail (0%) · 0 partial
- 🟢 **OTHER**: 5 asked · 0 fail (0%) · 0 partial
- 🟢 **PARTNERS**: 4 asked · 0 fail (0%) · 2 partial

## Failure classes — the per-class rates (denominator = 100 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 7 | 1 | 7.0% | #1 #8 |
| **wrong_fact** | 3 | 3 | 3.0% | #1 |
| **fabrication** | 3 | 1 | 3.0% | #1 |
| **over_refusal** | 1 | 1 | 1.0% | #3 #10 #12 |
| **thread_lost** | 0 | 1 | 0.0% | #21 #14 #2 |
| **no_count** | 0 | 1 | 0.0% | #5 |

- **FAIL** Q5011 [CHAPTERS/llm] (over_refusal) how many mds members live within 2 hours of 32250 zip code
  - Refused entirely instead of giving city-tag count and caveat that expected answer provides.
- **FAIL** Q5022 [CHAT_CONTENT/chats] (wrong_fact) how do i join the supplements channel
  - Gives unrelated TikTok chat and wrong link instead of the supplements verification form or invite link.
- **FAIL** Q5041 [EXPERT/llm] (fabrication) anybody willing to share suppliers for custom tool sets
  - Cites unrelated filling-machine supplier as a 'direct lead' for custom tool sets, an irrelevant fabricated match.
- **FAIL** Q5043 [EXPERT/llm] (false_denial) Give me an introduction message in between Joshua Asquith and Vlad from dr dent
  - Denies Vladimir Gatcan/Dr Dent exists and leaks Joshua's exact £14.5M revenue figure, both explicit failure conditions.
- **FAIL** Q5044 [EXPERT/llm] (false_denial) do we have any contacts for an amex rep
  - Omits the actual posted contact (Kevin Lutz's number) and instead offers unrelated anecdotes, dodging the real answer.
- **FAIL** Q5047 [FACEBOOK/llm] (false_denial) Can you do past posts on Facebook from many years ago?
  - Fails to disclose archive is effectively 2025-onward, implying deeper historical coverage than exists.
- **FAIL** Q5057 [MEMBER/llm] (wrong_fact) Tell me what you know about me
  - Describes a supplements-brand founder, not Andy Verdy's actual card (e-commerce/AI expertise, no such business detail given).
- **FAIL** Q5060 [MEMBER/llm] (false_denial) hey millie are you able to verify which member owns "stylia beauty" brand name
  - Denied finding brand despite Lenny Joseph's profile listing Stylia as his Brand Name field.
- **FAIL** Q5071 [SELF_ACCOUNT/llm] (false_denial) How I become a member of mds9?
  - Explicitly denies MDS 9 exists despite warehouse holding events and videos for that tier.
- **FAIL** Q5087 [TACTICS/llm] (fabrication) i'm looking for a way for AI to track changes on my listings. at least once every 6 hours, notifying me of changes in price, copy, pictures, and also competitor changes, including their promotions, price changes, etc.

here's what i asked Claude about Scale insights MCP, and it seems they can't do what i want. has anyone in the AI whatsapp chat mentioned a solution to this?

Tell me whether or not you can notify me when there have been any changes made to the listing with the current tools you have with Scale Insights MCP, be it changes in pictures, pricing, or listing copy. We would like to track whatever changes in SQP conversion, click-through rates, and overall order are just a result of certain changes in pictures, copy, and other things related to the listing.

Found tools

Straight answer: no, not fully — here's exactly what these tools can and can't see.

What's tracked vs. not
Change type	Tracked by Scale Insights MCP?
Bids, budgets, negatives, campaign status, placements	✅ get_change_history — full log, who/what/when
Price	⚠️ Partial — get_product_metadata returns current selling price, but there's no price-change log. I'd have to snapshot it myself over time to detect a move.
Title	⚠️ Same — current value only, no history
Main image	⚠️ Weakest signal — get_product_metadata returns a thumbnail URL; if it changes, that implies a main-image swap, but this isn't a reliable change log
Bullets / description / A+ content / secondary images	❌ Not exposed by any tool here at all

So there's no built-in listing-change log for pictures, copy, or A+ content — that data just isn't in this MCP's surface. get_change_history is scoped strictly to advertising actions (bids/budgets/negatives/etc.), not listing content.

What I can do about it

"Notify" — I have no push capability on my own; Scale Insights doesn't call out to me when something changes. But I can get functionally close using a scheduled task: I periodically re-pull get_product_metadata (title, price, thumbnail) for whichever ASINs you name, diff it against the last snapshot, and message you when something moves. That reliably catches price and title changes, and roughly catches main-image swaps — but it cannot see bullets, description, A+ modules, or secondary images, because Amazon doesn't expose those through this data source at all.

Correlating a change with SQP/CTR/CVR/orders — this part I can do well once I know when a change happened (from your own log, or from the price/title diff above):

get_sqp_intelligence — tells you specifically where the funnel broke: impression share holding but click share falling points at price/main-image (results-page problem); click share holding but purchase share falling points at the detail page (content/reviews/stock) — which is exactly the "was it the picture or the copy" distinction you're after.
explain_metric_change — decomposes a sales/ACOS/CVR move into CPC vs. CVR vs. AOV drivers around a given date.
What I'd suggest, given you're adding more accounts soon

Rather than track everything, tell me:

Which ASINs matter most right now (or "top sellers, auto-updated")
How often to check — daily catches things fast but is noisier; weekly aligns with SQP's own reporting cadence
Whether you want this per-account once the new connections are live, or just Benny Bradley's for now

For anything beyond price/title/main-image, the reliable source is Seller Central's own listing edit history (or your own change log) — if you tell me the date you changed a bullet or swapped images, I can run the before/after SQP and conversion read on that date immediately, no automation needed.
  - Cites Andrei Ureche's Sellametrics as an existing chat solution and omits the actual verified leads (Goldsmith/Weiler/Dan Ri/Ro Rosas replies), fabricating a solved-problem narrative.
- **FAIL** Q5094 [VIDEOS/llm] (wrong_fact) Can you provide me last MDS inspire event slides?
  - Answer points to 2025 slides as the 'last' Inspire, ignoring that 2026 is the most recent event and its slide situation.
- **FAIL** Q5097 [VIDEOS/llm] (false_denial) At MDs Singapore a speaker spoke about Trybe for social media. What was the context?
  - Explicitly denied the Singapore TikTok Mastermind Trybe mention that exists, misdirecting to an unrelated call.
- **FAIL** Q5098 [VIDEOS/llm] (fabrication) Is it true what they said about TikTok scaling isn’t for everyone
  - Ignores restricted target video and never mentions the correct Operator Room Vancouver quote; fabricates unverified chat thread details.
- **FAIL** Q5100 [VIDEOS/llm] (false_denial) What are the top 5 most watched mogul calls
  - Falsely denied view_count metric exists and gave unranked, unverified engagement list instead of actual top 5 by views.
- **PARTIAL** Q5008 [CAPABILITY/llm] (wrong_fact) Are you able to do daily reminders or routines?
  - Correctly denies recurring routines but overclaims reminders for 'any event' or 'call', not just Summit schedule items.
- **PARTIAL** Q5027 [DIGEST/llm] (thread_lost) Give me bullet updates about the latest topics in the AI and DTC channels
  - Covers both chats but misses most expected topics (Accelerate/Amazon MCP, BigQuery, Recharge/Loop, Selery, agency debate).
- **PARTIAL** Q5032 [EVENTS/llm] (over_refusal) Who are all the attendees at the Singapore event?
  - She declined the roster but then listed many names from Facebook, edging toward the disallowed dump.
- **PARTIAL** Q5034 [EVENTS/llm] (false_denial) When is the next event around Montreal, Canada and who are members near me?
  - Correctly lists Montreal members but omits Toronto Chapter Dinner Sept 14 2026 as nearest Canadian event.
- **PARTIAL** Q5042 [EXPERT/llm] (fabrication) Who are the best MDS members to talk to about TikTok affiliate programs?
  - Only Claudia Swindale overlaps with verified list; other four names are unverified and may be fabricated.
- **PARTIAL** Q5061 [MEMBER/llm] (wrong_fact) do you have any info on Roman Khan
  - Correctly denies Roman Khan but offers unrelated Ramon Gonzalez instead of the actual near-match Roman Maksimenko.
- **PARTIAL** Q5067 [PARTNERS/llm] (no_count) What does StoreClaw offer at the Summit?
  - Mentions a Summit-specific offer exists but omits the key fact: 2 months free and claim details.
- **PARTIAL** Q5068 [PARTNERS/llm] (wrong_fact) Tell me about hector the ppc tool
  - Correct core product description but wrongly attributes Hector to founder Meher Patel instead of Shaurya Ithikkat's AI Mastermind talk.
