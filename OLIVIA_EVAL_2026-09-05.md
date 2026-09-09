# Olivia eval — 2026-09-05 — 220 judged · PASS 193 · PARTIAL 3 · FAIL 24 (10.9%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 5 fail (31%) · 1 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **EVENT**: 11 asked · 3 fail (27%) · 1 partial
- 🔴 **FB**: 30 asked · 4 fail (13%) · 0 partial
- 🟡 **AT_PROFILE**: 22 asked · 2 fail (9%) · 1 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟡 **PARTNER**: 18 asked · 1 fail (6%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 13 | 0 | 5.9% | #1 #8 |
| **wrong_fact** | 8 | 1 | 3.6% | #1 |
| **no_count** | 0 | 2 | 0.0% | #5 |
| **dodge** | 1 | 0 | 0.5% | #1 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 as founding year, but Olivia denied finding any such information.
- **FAIL** Q2021 [AT_PROFILE/llm] (false_denial) Which member based in San Diego specializes in martial arts equipment as their main niche?
  - Olivia denies existence of Cole South despite ground truth confirming a San Diego martial arts equipment member.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denies finding the event despite ground truth confirming it exists in Kaua'i, Hawaii.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms the event exists with a specific start time, but Olivia denies finding it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Olivia denied finding the event, but expected answer confirms it exists and is Virtual.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Riverbend Consulting instead of expected ecommerceChris as the Account Health MDS partner.
- **FAIL** Q2062 [WA_DIGEST/llm] (wrong_fact) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Ground truth says bundling was the AOV lever; Olivia claims separate listings instead, contradicting expected fact.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth confirms the 'Claude Basics' joke exists, but Olivia denied finding it.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Answer gives Sept 2 video from library, missing the expected April 29 WhatsApp-shared call recording.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - Ground truth gives explicit closing date May 22, 2026, but Olivia denies finding any such date.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies Richard Laatz mentioned George Borowski's growth streak, contradicting the ground truth.
- **FAIL** Q2111 [FB/llm] (false_denial) According to Prue Millsap's reply to Maxwell Sigurdson-Scott, what tactic was suggested if the price point is low?
  - Denies existence of Prue's reply about bundling despite warehouse-verified comment confirming it.
- **FAIL** Q2122 [FB/llm] (false_denial) What destination is being discussed for the Singapore Summit side quest happening the week before the summit?
  - Ground truth says the June 18 post names Bali, but Olivia denied any destination was mentioned.
- **FAIL** Q2131 [CROSS/llm] (dodge) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Refused to give the specific comparison despite it being verifiable ground truth, offering only a menu deflection.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Both cited posts describe different concerns than expected (email tracking, multi-channel attribution) not the specified Amazon delay or warehouse software question.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - FB post about brand-for-sale, not 'For all my fellow supplement sellers!' as expected — wrong post cited.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Failed to find Hermes/1-hour SP API connection fact that ground truth confirms exists in warehouse.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Never mentions the ChatGPT Artface earring example; instead gives unrelated Claude Code DIY examples, missing expected fact.
- **FAIL** Q1003 [GEN/llm] (false_denial) What's Matteo Lombardi's current fulfillment split between FBA and FBM for his European company selling in the US?
  - Ground truth shows Matteo posted the 99% FBA split, but Olivia denied finding it.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong legal topic: expected IP/lawsuits, Olivia said international trade/customs law.
- **FAIL** Q1040 [GEN/llm] (false_denial) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Olivia denies the comment exists though warehouse confirms Joe Cowling's fb_comment about sellerboard, adlabs, expandfi.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Sept 1-2 videos, missing actual latest uploads (2026-07-23) and restricted flagged videos.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia gave detailed content/summary of a restricted video instead of only title, date, duration, link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim transcript quotes despite no transcript access, contradicting the expected honest denial.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Confirms Orange Co chapter but misses the Chapter Leads affiliation from expected answer.
- **PARTIAL** Q2039 [EVENT/llm] (no_count) On what date is the Expert Call with Clayton Atchison from Carbon 6 scheduled?
  - Found the correct video but gave only 'June 2022' publish month, not the specific June 28, 2022 date.
- **PARTIAL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - 29% matches, but MCP video guide misdescribed as connector explainer instead of the $10k/mo build-and-sell playbook.
