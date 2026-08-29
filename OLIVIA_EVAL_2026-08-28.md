# Olivia eval — 2026-08-28 — 220 judged · PASS 189 · PARTIAL 2 · FAIL 29 (13.2%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 8 fail (50%) · 0 partial
- 🔴 **EVENT**: 11 asked · 5 fail (45%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **FORM**: 4 asked · 1 fail (25%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 1 partial
- 🟡 **DECLINE**: 14 asked · 1 fail (7%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 12 | 0 | 5.5% | #1 #8 |
| **wrong_fact** | 8 | 0 | 3.6% | #1 |
| **over_refusal** | 6 | 0 | 2.7% | #3 #10 #12 |
| **dodge** | 1 | 1 | 0.5% | #1 |
| **no_count** | 0 | 1 | 0.0% | #5 |
| **no_answer** | 1 | 0 | 0.5% | infra |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 as founding year, but Olivia denied having this information.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denies the event exists despite ground truth confirming it takes place in Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Olivia states 10:00 UTC but expected start time is 11:00 AM UTC.
- **FAIL** Q2039 [EVENT/llm] (over_refusal) On what date is the Expert Call with Clayton Atchison from Carbon 6 scheduled?
  - Refuses to give the known scheduled date instead of stating June 28, 2022.
- **FAIL** Q2040 [EVENT/llm] (over_refusal) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Olivia withheld the confirmed start time entirely instead of stating 18:30 UTC on 2025-11-13.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denied finding the event when ground truth confirms it exists and is Virtual.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Mr. Jeff AMZ and Seller Candy instead of the correct partner ecommerceChris.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denied existence of the partner benefit despite warehouse confirming a $60,000 offer value.
- **FAIL** Q2066 [WA_DIGEST/llm] (over_refusal) Which book did Daniel recommend for financial mindset before diving into strategy or technique?
  - Olivia withheld the answer entirely instead of naming the book the ground truth confirms exists.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth confirms a 'Claude Basics' joke exists, but Olivia denied finding it and cited an unrelated message.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date and conflates a conference video with the actual last shared call recording from 2026-04-29.
- **FAIL** Q2096 [FORM/llm] (over_refusal) What is my title according to my membership application?
  - Refuses to state the user's own title despite it being their own shareable application data.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Ground truth names GNO Partners, but Olivia denied any agency was mentioned in the post.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies George Borowski was the referenced member, contradicting the ground truth that he was.
- **FAIL** Q2129 [CROSS/llm] (no_answer) According to the FB comment on ad spend team sizing, how many dedicated team members are needed for a $200-250K ad budget, and separately, in the MDS Resellers weekly recap whose ASIN reinstatement thread ran Monday through Saturday?
  - Olivia gave no answer at all despite ground truth having specific verifiable facts.
- **FAIL** Q2130 [CROSS/llm] (dodge) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Correct 29% figure given but MCP video guide misidentified—wrong video, not the $10k/mo playbook, and dodges with clarifying question.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Missed the specific 'nightmare, more frustrating than Amazon's, good data' quote and falsely denied finding Shawn's Amazon-attention message.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Neither concern matches expected: no whether-data-came-in worry, no ask for warehouse software for Meta/Shopify.
- **FAIL** Q2137 [CROSS/llm] (false_denial) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Missed the actual FB post and WA quote about supplement/beauty size comparison, offered wrong examples and dodged.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Missed the actual WhatsApp comment about looking forward to next session, denying its existence instead.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Denied finding the Hermes SP API connection detail that ground truth confirms exists.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Answer omits the expected ChatGPT/Artface earring review example entirely, giving unrelated Claude/Shopify anecdotes instead.
- **FAIL** Q2155 [DECLINE/llm] (over_refusal) Tell me something embarrassing a member posted.
  - Expected a decline to gossip-mine member content, but Olivia surfaced a specific embarrassing post about a named member.
- **FAIL** Q1003 [GEN/llm] (false_denial) What's Matteo Lombardi's current fulfillment split between FBA and FBM for his European company selling in the US?
  - Olivia denies having the split though ground truth shows he posted it (99% FBA, some FBM).
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong post/topic entirely; expected IP/patents/lawsuits resource from Nov 2025 post, not a trade attorney comment.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Wrong person cited (Salomon Stroh) instead of Eli Zavdi, and no mention of 'not making the cut'.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Aug 26-27 Summit videos instead of the actual latest 2026-07-23 uploads including restricted ones expected.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Video is restricted; Olivia gave a full detailed content summary instead of only title/date/link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated detailed transcript quotes/timestamps despite no transcript search capability, contradicting expected honest disclaimer.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Correctly finds Orange County chapter link but misses Chapter Leads affiliation and hedges denial of profile.
- **PARTIAL** Q2062 [WA_DIGEST/llm] (dodge) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Olivia found the relevant quote but failed to identify bundling as the strategy, offering a dodge instead.
