# Olivia eval — 2026-09-07 — 220 judged · PASS 192 · PARTIAL 3 · FAIL 25 (11.4%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 11 asked · 6 fail (55%) · 0 partial
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 2 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **FB**: 30 asked · 3 fail (10%) · 0 partial
- 🟡 **AT_PROFILE**: 22 asked · 2 fail (9%) · 1 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **WA_RAW**: 22 asked · 1 fail (5%) · 0 partial
- 🟢 **PARTNER**: 18 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 9 | 1 | 4.1% | #1 #8 |
| **wrong_fact** | 9 | 0 | 4.1% | #1 |
| **dodge** | 3 | 1 | 1.4% | #1 |
| **over_refusal** | 3 | 0 | 1.4% | #3 #10 #12 |
| **no_answer** | 0 | 1 | 0.0% | infra |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth shows 2015 exists in warehouse, but Olivia falsely denied finding it.
- **FAIL** Q2012 [AT_PROFILE/llm] (over_refusal) What is Dana E. Mavros's title at her company?
  - Olivia refused but then leaked her title (CEO) via the about-me notes, contradicting the refusal.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Olivia denies the event exists though warehouse confirms it's located in Kaua'i, Hawaii.
- **FAIL** Q2035 [EVENT/llm] (wrong_fact) What city is the MDS Summit being held in?
  - Claims Singapore already happened and next is Cancún 2027, contradicting expected upcoming Singapore 2026 Summit.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Wrong start time given (10:00 UTC) versus expected 11:00 AM UTC.
- **FAIL** Q2039 [EVENT/llm] (false_denial) On what date is the Expert Call with Clayton Atchison from Carbon 6 scheduled?
  - Olivia denied a Carbon6 session exists despite citing its exact video, missing the June 28, 2022 date.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms a specific event/time exists, but Olivia denied finding it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Olivia denied finding the event while ground truth confirms it exists and is Virtual.
- **FAIL** Q2062 [WA_DIGEST/llm] (dodge) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Ground truth clearly identifies bundling, but Olivia refused to name it despite having the message context.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date and platform; expected 2026-04-29 on app.mds.co, not Sept 2 video with no platform.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - Missed the May 22, 2026 close date explicitly given in the same May 13 post source.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Ground truth confirms Mark Behnke posted about this agency, but Olivia denied finding him.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Ground truth says Richard mentioned George Borowski's growth pattern, but Olivia denies it and flips attribution.
- **FAIL** Q2129 [CROSS/llm] (dodge) According to the FB comment on ad spend team sizing, how many dedicated team members are needed for a $200-250K ad budget, and separately, in the MDS Resellers weekly recap whose ASIN reinstatement thread ran Monday through Saturday?
  - Olivia withheld both concrete facts (20-30 members and Ariel's thread) despite them being verified in warehouse.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - MCP video guide should be the WA 2026 playbook to build/sell MCPs for $10k/mo, not the MDS Inspire video Olivia cited.
- **FAIL** Q2131 [CROSS/llm] (over_refusal) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Refused to provide the WhatsApp comparison despite it being available in the ground truth.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Both cited posts are about email tracking and cross-channel attribution, not the specific referral-lag or warehouse-software concerns expected.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post topic and wrong WhatsApp comparison; neither matches the expected supplement-sellers post or beauty/supplement size comparison.
- **FAIL** Q2142 [CROSS/llm] (dodge) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the expected ChatGPT/Artface earring example entirely; gave unrelated tools instead of the counter-example.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Expected topic is intellectual property/lawsuits; Olivia gave a different unrelated post about international trade law.
- **FAIL** Q1040 [GEN/llm] (false_denial) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Ground truth shows Joe Cowling's comment naming sellerboard, adlabs, expandfi, but Olivia denied finding it.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Wrong commenter and quote; expected Eli Zavdi's comment about not making the cut, not Ivan Ong's.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Sept 2 Mastermind videos instead of the actual newest 2026-07-23 uploads including restricted ones expected.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia disclosed full restricted content/summary instead of only title, date, duration, and link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia invented verbatim transcript quotes/timestamps despite no transcripts existing, per expected answer.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_answer) Which chapters is Kyle Dilger affiliated with?
  - Correctly hints at Orange County tie but fails to confirm Chapter Leads affiliation or give a clear answer.
- **PARTIAL** Q2138 [CROSS/llm] (dodge) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Correctly identifies unrelated threads but fails to surface the expected WhatsApp 'looking forward to next session' comment.
- **PARTIAL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Attorney part correct, but falsely denied finding the Hermes SP API one-hour connection claim.
