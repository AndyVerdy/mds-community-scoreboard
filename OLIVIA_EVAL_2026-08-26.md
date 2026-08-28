# Olivia eval — 2026-08-26 — 220 judged · PASS 196 · PARTIAL 2 · FAIL 22 (10.0%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 1 partial
- 🔴 **EVENT**: 11 asked · 3 fail (27%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 2 fail (20%) · 0 partial
- 🔴 **WA_DIGEST**: 12 asked · 2 fail (17%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **WA_RAW**: 22 asked · 1 fail (5%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 12 | 1 | 5.5% | #1 #8 |
| **wrong_fact** | 6 | 0 | 2.7% | #1 |
| **over_refusal** | 2 | 0 | 0.9% | #3 #10 #12 |
| **dodge** | 0 | 1 | 0.0% | #1 |
| **no_answer** | 1 | 0 | 0.5% | infra |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 exists, but Olivia denied any business start year is available.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Falsely denies the Billion Dollar Seller Summit exists despite it being in the warehouse with a location.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms event exists with a specific start time, but Olivia denied its existence.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denies the event exists though ground truth confirms it as a Virtual event.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Mr. Jeff AMZ instead of expected ecommerceChris as the account health partner.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denied existence of the New Amazon Account deal worth $60,000 that ground truth confirms exists.
- **FAIL** Q2062 [WA_DIGEST/llm] (wrong_fact) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Olivia said separate product listing, but expected answer is bundling as the AOV lever.
- **FAIL** Q2071 [WA_DIGEST/llm] (false_denial) In the MDS Centurion 20M+ chat, why is Ershad unavailable on the proposed meeting day?
  - Ground truth clearly states World Cup semifinals reason, but Olivia denies finding it and asks for more info.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Denies finding the joke and asks for clarification instead of giving 'Claude Basics' from the chat.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Denies finding relevant post despite warehouse-verified Mark Behnke fb_post naming GNO Partners.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies George Borowski was the mentioned member, contradicting the verified ground truth that he was.
- **FAIL** Q2129 [CROSS/llm] (no_answer) According to the FB comment on ad spend team sizing, how many dedicated team members are needed for a $200-250K ad budget, and separately, in the MDS Resellers weekly recap whose ASIN reinstatement thread ran Monday through Saturday?
  - Olivia gave no answer at all despite specific verified facts (20-30 members; Ariel's thread) being available.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Missed the specific 29% for 26 hours figure and misidentified MCP video as an AI protocol rather than the $10k/mo playbook guide.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Denies both the Shawn Amazon-attention thread and the WhatsApp API comparison that ground truth confirms exist.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Wrong specifics: expected concerns about delayed Amazon data and best warehouse software, not what Olivia described.
- **FAIL** Q2137 [CROSS/llm] (false_denial) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Missed the actual FB post and the size comparison ('bigger than beauty'), giving unrelated content instead.
- **FAIL** Q2142 [CROSS/llm] (over_refusal) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Refused entirely despite a verified WA example (ChatGPT/Artface) existing in the warehouse.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong topic: expected IP/lawsuits resource, Olivia describes an unrelated international trade attorney thread.
- **FAIL** Q1040 [GEN/llm] (wrong_fact) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Missed the specific data sources (sellerboard, adlabs, expandfi) and substituted unrelated fabricated details.
- **FAIL** Q1046 [GEN/llm] (false_denial) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Ground truth confirms Eli Zavdi's comment exists, but Olivia falsely denied finding it.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia disclosed detailed content/summary of a restricted video instead of only title, date, duration, link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricates specific transcript content instead of admitting no transcripts exist to search.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (dodge) Which chapters is Kyle Dilger affiliated with?
  - Correctly identifies Orange County chapter but omits Chapter Leads affiliation and hedges with a dodge offer.
- **PARTIAL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Correctly IDs the FB tip but fails to find the unrelated WhatsApp comment, which expected answer says exists separately.
