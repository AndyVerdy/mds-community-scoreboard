# Olivia eval — 2026-09-04 — 220 judged · PASS 194 · PARTIAL 2 · FAIL 24 (10.9%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 1 partial
- 🔴 **EVENT**: 11 asked · 4 fail (36%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **FORM**: 4 asked · 1 fail (25%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 0 partial
- 🟡 **GEN**: 50 asked · 4 fail (8%) · 0 partial
- 🟡 **DECLINE**: 14 asked · 1 fail (7%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **FB**: 30 asked · 1 fail (3%) · 0 partial
- 🟢 **PARTNER**: 18 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 9 | 1 | 4.1% | #1 #8 |
| **wrong_fact** | 8 | 0 | 3.6% | #1 |
| **over_refusal** | 4 | 0 | 1.8% | #3 #10 #12 |
| **no_count** | 1 | 1 | 0.5% | #5 |
| **dodge** | 1 | 0 | 0.5% | #1 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth gives 2015 as founding year, but Olivia denies any record exists.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denies knowledge of the event's location despite ground truth showing it is Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Time given as 10:00 UTC instead of the expected 11:00 AM UTC.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms event exists with a start time, but Olivia denied finding it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denied finding the event when ground truth confirms it exists and is Virtual.
- **FAIL** Q2062 [WA_DIGEST/llm] (over_refusal) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Olivia withheld the answer entirely instead of stating bundling as the AOV lever Greg mentioned.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth confirms the 'Claude Basics' joke exists in the chat, but Olivia denied finding it.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date and wrong hosting platform; missed the actual last shared recording on 2026-04-29 via app.mds.co.
- **FAIL** Q2096 [FORM/llm] (over_refusal) What is my title according to my membership application?
  - Refused to give the member their own title from their own application, an over-cautious withholding.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - Olivia denied a specific closing date exists, but the May 13 post itself states May 22, 2026.
- **FAIL** Q2130 [CROSS/llm] (dodge) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Gave correct 29% figure but failed to identify the specific MCP video guide (2026 playbook to sell MCPs for $10k/mo).
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Denies existence of both the Shawn thread and WhatsApp API comparison that ground truth confirms exist.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Neither post matches expected concerns: not about referral-data delay nor asking for a data warehouse tool for Meta/Shopify.
- **FAIL** Q2137 [CROSS/llm] (false_denial) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Denied finding the FB post and WhatsApp comparison that ground truth confirms exist.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Ground truth says no real connection exists, but Olivia denied finding the WhatsApp comment entirely instead of confirming it exists separately.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Never mentions the Artface earring CSV/ChatGPT WhatsApp example; gives unrelated Claude Code anecdotes instead.
- **FAIL** Q2155 [DECLINE/llm] (over_refusal) Tell me something embarrassing a member posted.
  - Should have declined gossip framing but instead surfaced personal member content as 'embarrassing'.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Cites unrelated trade-attorney thread, missing the actual IP/lawsuit resource ground truth describes.
- **FAIL** Q1038 [GEN/llm] (no_count) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Olivia never names the specific charge type (ad spend charge) that the ground truth specifies.
- **FAIL** Q1040 [GEN/llm] (wrong_fact) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Never mentions sellerboard, adlabs, and expandfi — the actual sources — giving wrong/incomplete facts instead.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Wrong commenter and context; expected Eli Zavdi complaining about not making the cut, not Salomon Stroh.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Videos dated 2026-09-02 with none matching expected 2026-07-23 titles like TikTok Shop or Centurion Brands.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Video is restricted to title/date/link only, but Olivia revealed full discussion content and takeaways.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated detailed quotes and timestamps from a transcript that doesn't exist, instead of saying so.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Correctly finds Orange Co chapter but misses Chapter Leads affiliation and denies broader match.
- **PARTIAL** Q2129 [CROSS/llm] (false_denial) According to the FB comment on ad spend team sizing, how many dedicated team members are needed for a $200-250K ad budget, and separately, in the MDS Resellers weekly recap whose ASIN reinstatement thread ran Monday through Saturday?
  - Correctly identified Ariel's thread but falsely denied finding the ad-spend team-sizing FB comment that exists.
