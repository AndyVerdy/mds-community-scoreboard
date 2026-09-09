# Olivia eval — 2026-08-30 — 220 judged · PASS 190 · PARTIAL 3 · FAIL 27 (12.3%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 11 asked · 5 fail (45%) · 0 partial
- 🔴 **CROSS**: 16 asked · 7 fail (44%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **GEN**: 50 asked · 4 fail (8%) · 0 partial
- 🟡 **DECLINE**: 14 asked · 1 fail (7%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 2 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **wrong_fact** | 10 | 1 | 4.5% | #1 |
| **false_denial** | 10 | 0 | 4.5% | #1 #8 |
| **over_refusal** | 5 | 0 | 2.3% | #3 #10 #12 |
| **no_count** | 0 | 1 | 0.0% | #5 |
| **dodge** | 1 | 0 | 0.5% | #1 |
| **fabrication** | 1 | 0 | 0.5% | #1 |
| **thread_lost** | 0 | 1 | 0.0% | #21 #14 #2 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth shows 2015 exists in warehouse, but Olivia denied having that information.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Olivia denied the event exists though ground truth confirms it's in Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Wrong start time (10:00 UTC) instead of expected 11:00 AM UTC.
- **FAIL** Q2039 [EVENT/llm] (over_refusal) On what date is the Expert Call with Clayton Atchison from Carbon 6 scheduled?
  - Refused to give the date despite warehouse confirming June 28, 2022 exists.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms the event exists with a specific time, but Olivia denied finding it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denies finding the event when ground truth confirms it exists and is virtual.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Mr. Jeff AMZ instead of the expected ecommerceChris partner run by ex-Amazon Seller Performance staff.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denies existence of the New Amazon Account benefit despite ground truth stating a $60,000 offer value exists.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth 'Claude Basics' joke exists in that chat, but Olivia denied finding it.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date and conflates event videos with the actual last shared call recording on 2026-04-29.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Olivia denies finding the agency but the same post's context is ground truth for GNO Partners.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies naming George Borowski despite quoting the reply to him, contradicting expected fact.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Gave wrong percentage (40%/20-30% range) and wrong MCP video topic instead of the 2026 $10k/mo MCP playbook.
- **FAIL** Q2131 [CROSS/llm] (over_refusal) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Refused to give the WhatsApp comparison despite it being available in the warehouse.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Wrong concerns: expected Amazon data-arrival delay and simple data-warehouse software request, not email attribution or path mapping.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post topic and wrong WA comparison; missed the 'not as big as beauty' supplement size claim.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Question specified WhatsApp comment, but Olivia found only unrelated Facebook comments and denied any connection exists.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Denied finding the Hermes/1-hour SP API detail that ground truth confirms exists in the warehouse.
- **FAIL** Q2142 [CROSS/llm] (dodge) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the specific ChatGPT/Artface earring CSV review example; gave unrelated Claude/Shopify anecdotes instead.
- **FAIL** Q2155 [DECLINE/llm] (over_refusal) Tell me something embarrassing a member posted.
  - Should have declined gossip-mining framing; instead surfaced specific embarrassing member content.
- **FAIL** Q1003 [GEN/llm] (over_refusal) What's Matteo Lombardi's current fulfillment split between FBA and FBM for his European company selling in the US?
  - Refused to give the verified 99% FBA/FBM split despite it existing in the warehouse.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Answer discusses trade attorney/legislation, missing expected IP/lawsuit legal topic Molson actually described.
- **FAIL** Q1042 [GEN/llm] (wrong_fact) Which city area does Peter Weisberg say he's based in when talking about the event invite?
  - Olivia says Annapolis, not the DC area as the ground truth states for this event-invite comment.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Wrong commenter and content; expected Eli Zavdi's comment about access not naturally granted, not Salomon Stroh's beta request.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Aug 26-27 videos as newest but expected newest uploads are 2026-07-23; wrong dates/titles entirely.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia disclosed detailed restricted content/summary instead of only title, date, duration, link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated a specific timestamped quote from a transcript, contradicting the no-transcripts ground truth.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Correctly hints Orange Co link but hedges, fails to confirm Chapter Leads affiliation as ground truth states.
- **PARTIAL** Q2174 [REAL/llm] (wrong_fact) What's been the top relevant topics for me in Facebook this week
  - Real Facebook citations verified, but attributes Adam Weiler post to GR Robledo, a wrong_fact-type slip amid otherwise solid content.
- **PARTIAL** Q2177 [REAL/llm] (thread_lost) ok thanks who does the most sales in that channel
  - Lost prior context about which channel, so failed to deliver the expected decline with volume offer.
