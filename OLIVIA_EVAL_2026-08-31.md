# Olivia eval — 2026-08-31 — 220 judged · PASS 196 · PARTIAL 3 · FAIL 21 (9.5%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **EVENT**: 11 asked · 3 fail (27%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🔴 **FB**: 30 asked · 3 fail (10%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **WA_RAW**: 22 asked · 1 fail (5%) · 0 partial
- 🟢 **GEN**: 50 asked · 2 fail (4%) · 1 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 1 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 11 | 0 | 5.0% | #1 #8 |
| **wrong_fact** | 8 | 0 | 3.6% | #1 |
| **no_count** | 0 | 2 | 0.0% | #5 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |
| **dodge** | 0 | 1 | 0.0% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth gives 2015, but Olivia denies having any founding year on file.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Olivia denies finding the event, but ground truth confirms it exists at Kaua'i, Hawaii.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms a real event with a specific start time that Olivia denied finding.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denies finding the event when ground truth confirms it exists and is Virtual.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Failed to name ecommerceChris, the correct partner, offering wrong alternatives instead.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denied existence of the New Amazon Account benefit worth $60,000 that ground truth confirms exists.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date given (2026-08-27) instead of ground-truth 2026-04-29, though platform matches.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - Missed the exact closing date (May 22, 2026) that is stated in Khayman's own May 13 post per ground truth.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Olivia found GNO Partners in the thread but denied it was Mark's answer, missing the expected fact.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Expected answer names George Borowski, but Olivia denies any other member was mentioned.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Missed the specific 29%/26-hour figure and gave wrong MCP video topic instead of the $10k/mo MCP playbook guide.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Ground truth confirms both messages exist, but Olivia falsely denies finding either.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Neither answer matches expected concerns: no mention of yesterday's referral traffic delay or request for warehouse software recommendation.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post and wrong source for size comparison; missed the 'For all my fellow supplement sellers!' post and correct WA quote.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Denies finding the Hermes/SP API story despite ground truth confirming it exists with specific details.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Wrong example entirely—omits ChatGPT/Artface earring CSV case and instead invents unrelated Claude Code narratives.
- **FAIL** Q1003 [GEN/llm] (false_denial) What's Matteo Lombardi's current fulfillment split between FBA and FBM for his European company selling in the US?
  - Denies having the fulfillment split despite a specific fb_post from Matteo stating 99% FBA/some FBM.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Olivia cited an unrelated international trade post, missing the expected IP/lawsuit resource from Molson Hart.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Aug 26-27 videos, missing the actual newest 2026-07-23 uploads including restricted ones expected.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia revealed detailed discussion content for a restricted video that should only get title/date/link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim transcript quotes and timestamps when no transcripts exist to search.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Correctly names Orange Co Chapter but omits the Chapter Leads affiliation, missing part of the expected answer.
- **PARTIAL** Q1038 [GEN/llm] (no_count) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Olivia omits the key detail that the charge was specifically the ad spend charge, giving only vague phrasing.
- **PARTIAL** Q2177 [REAL/llm] (dodge) ok thanks who does the most sales in that channel
  - Should have declined sales-figures directly instead of only asking which channel, missing required refusal.
