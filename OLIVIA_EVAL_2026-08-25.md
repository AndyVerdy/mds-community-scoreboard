# Olivia eval — 2026-08-25 — 220 judged · PASS 195 · PARTIAL 3 · FAIL 22 (10.0%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 1 partial
- 🔴 **EVENT**: 11 asked · 4 fail (36%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🔴 **FB**: 30 asked · 3 fail (10%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **WA_RAW**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **GEN**: 50 asked · 2 fail (4%) · 0 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 13 | 1 | 5.9% | #1 #8 |
| **wrong_fact** | 7 | 1 | 3.2% | #1 |
| **dodge** | 0 | 1 | 0.0% | #1 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Denied having the 2015 start-year fact that ground truth confirms exists.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denies existence of an event the warehouse confirms is located in Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Wrong start time (10:00 UTC) vs expected 11:00 AM UTC, and incorrectly claims event already passed.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms this event exists with a specific time, but Olivia denied finding it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denied finding the event when warehouse confirms it exists and is Virtual.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Mr. Jeff AMZ and Seller Candy, not ecommerceChris, the specific ex-Seller Performance/Policy Enforcement partner asked for.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denied finding the $60,000 offer value that ground truth confirms exists in the partner directory.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Denies existence of the 'Claude Basics' joke which ground truth confirms occurred on 2026-05-10.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Falsely denies Mark Behnke exists and misses the GNO Partners fact from his own post.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies naming another member, but ground truth says he named George Borowski for this pattern.
- **FAIL** Q2111 [FB/llm] (false_denial) According to Prue Millsap's reply to Maxwell Sigurdson-Scott, what tactic was suggested if the price point is low?
  - Denies existence of a comment that ground truth confirms exists, missing the bundling suggestion.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Got the correct 29% figure but MCP guide misidentified as MDS video instead of WA $10k/mo playbook message.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Denies finding the Shawn/Amazon thread and WhatsApp API comparison, both of which exist per ground truth.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post topic and wrong WhatsApp comparison; doesn't mention beauty vs supplement size comparison.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Expected answer confirms WhatsApp comment exists; Olivia falsely denies finding it, missing the connection.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Denied having the SP API/Hermes info despite ground truth stating it exists and is known.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the expected ChatGPT/Artface earring WA example and answered with unrelated Claude Code/audit anecdotes.
- **FAIL** Q1003 [GEN/llm] (false_denial) What's Matteo Lombardi's current fulfillment split between FBA and FBM for his European company selling in the US?
  - Ground truth shows a March 2026 post stating 99% FBA/some FBM, but Olivia denied finding it.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong topic: expected IP/lawsuits resource, Olivia gave unrelated trade legislation citation.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Missed actual newest uploads (2026-07-23 restricted videos) and gave older Aug 21 as latest instead.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia disclosed full restricted content/summary instead of only title, date, duration, link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated a verbatim transcript quote despite no transcript search capability existing per ground truth.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (dodge) Which chapters is Kyle Dilger affiliated with?
  - Olivia surfaces OC Chapter link but hedges and omits Chapter Leads, never confirming the affiliation.
- **PARTIAL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date (July 27 vs April 29) though correct platform app.mds.co, so key fact off.
- **PARTIAL** Q2141 [CROSS/llm] (false_denial) Someone asked Brian Kelsey if he had contacts that could help, and separately a member shared a story about a contact who used to sell Nike - what happened to that Nike seller's ability to sell after years of doing it?
  - Nike seller story matches well, but Olivia falsely denies the Brian Kelsey contact question exists.
