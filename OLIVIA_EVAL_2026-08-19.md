# Olivia eval — 2026-08-19 — 220 judged · PASS 192 · PARTIAL 2 · FAIL 26 (11.8%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 11 asked · 4 fail (36%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 4 fail (22%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 2 fail (20%) · 0 partial
- 🔴 **CROSS**: 16 asked · 3 fail (19%) · 1 partial
- 🔴 **GEN**: 50 asked · 5 fail (10%) · 0 partial
- 🟡 **AT_PROFILE**: 22 asked · 2 fail (9%) · 1 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **REAL**: 11 asked · 1 fail (9%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 14 | 0 | 6.4% | #1 #8 |
| **wrong_fact** | 8 | 0 | 3.6% | #1 |
| **no_count** | 1 | 1 | 0.5% | #5 |
| **fabrication** | 2 | 0 | 0.9% | #1 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |
| **dodge** | 0 | 1 | 0.0% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth gives 2015 as founding year, but Olivia falsely claims it isn't on file anywhere.
- **FAIL** Q2012 [AT_PROFILE/llm] (over_refusal) What is Dana E. Mavros's title at her company?
  - Olivia refused but then leaked the CEO title anyway, contradicting the required refusal.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Olivia falsely denied the event exists, contradicting the ground truth that it's in Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Olivia gave 10:00 UTC instead of the correct 11:00 AM UTC start time.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Denies event exists despite ground truth confirming a specific start time.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Ground truth says event exists and is Virtual, but Olivia denied finding it and offered a filing instead.
- **FAIL** Q2043 [PARTNER/llm] (false_denial) What member offer does Hector Ai provide to the MDS community?
  - Olivia denied finding Hector Ai despite ground truth confirming its member offer exists.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Riverbend Consulting instead of the correct partner ecommerceChris.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denies existence of a known $60,000 New Amazon Account partner benefit that ground truth confirms.
- **FAIL** Q2060 [PARTNER/llm] (false_denial) What's the member offer value for the New Amazon Account partner?
  - Denied finding a New Amazon Account partner despite ground truth confirming a specific $60k value offer exists.
- **FAIL** Q2071 [WA_DIGEST/llm] (false_denial) In the MDS Centurion 20M+ chat, why is Ershad unavailable on the proposed meeting day?
  - Denies finding the World Cup semifinal absence that ground truth confirms exists in the chat.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth confirms 'Claude Basics' joke exists in chat, but Olivia denied finding it.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date and event cited; expected 2026-04-29 call recording on app.mds.co, not an Aug 10 in-person session.
- **FAIL** Q2107 [FB/llm] (false_denial) Who hosted the Mogul Call about the Save Our Sellers campaign in place of Jamie Graham?
  - Olivia failed to provide Eugene Khayman despite ground truth confirming the fact exists in warehouse.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Denies another member was referenced, but ground truth says George Borowski was mentioned.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post topic and wrong WhatsApp comparison; neither matches the expected supplement-seller post or beauty/supplement size comparison.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Olivia denies the actual 'looking forward to next session' comment exists and fabricates unrelated ChatGPT credit content instead.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the expected ChatGPT/Artface earring example and instead cited unrelated Claude Code discussions.
- **FAIL** Q1017 [GEN/llm] (false_denial) Which dates is Jabran Niaz attending Amazon Accelerate this year?
  - Olivia falsely denied having access despite a Facebook post from Jabran Niaz stating the dates.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong topic and wrong post; expected IP/trademarks/patents/lawsuits, Olivia gave unrelated trade attorney/legislation content from a different author.
- **FAIL** Q1026 [GEN/llm] (no_count) How many products is Michael Patrón discontinuing in this inventory cleanup?
  - Olivia gave only a link, never stating the requested count of 41 products.
- **FAIL** Q1040 [GEN/llm] (fabrication) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Olivia invented Seller Central vs scraping as the data sources instead of sellerboard, adlabs, and expandfi.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Wrong commenter and date cited; expected Eli Zavdi, not Salomon Stroh.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Wrong dates given (Aug 5-10) instead of the actual latest uploads from 2026-07-23.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia presents detailed transcript-like claims as what Lisa said, despite no transcript access existing.
- **FAIL** Q2170 [REAL/verbatim] (false_denial) how about recap of MDS trading
  - Claims no activity when ground truth confirms 65 messages that week in MDS Trading.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Confirms Orange Co chapter but misses Chapter Leads affiliation entirely.
- **PARTIAL** Q2130 [CROSS/llm] (dodge) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - First part correct (29%), but MCP video guide (build/sell MCPs for $10k/mo) not identified despite naming a related Guido Reyes video.
