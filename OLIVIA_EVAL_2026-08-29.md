# Olivia eval — 2026-08-29 — 220 judged · PASS 193 · PARTIAL 3 · FAIL 24 (10.9%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 11 asked · 5 fail (45%) · 0 partial
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 1 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **GEN**: 50 asked · 2 fail (4%) · 1 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 13 | 1 | 5.9% | #1 #8 |
| **wrong_fact** | 9 | 0 | 4.1% | #1 |
| **no_count** | 0 | 2 | 0.0% | #5 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 start year, but Olivia denied the info exists.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denies existence of the event despite ground truth confirming it is in Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Stated 10:00 UTC start time, but expected ground truth is 11:00 AM UTC.
- **FAIL** Q2039 [EVENT/llm] (false_denial) On what date is the Expert Call with Clayton Atchison from Carbon 6 scheduled?
  - Denies existence of a call the ground truth confirms was scheduled for June 28, 2022.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Denied event exists despite warehouse having exact verified start time for it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denied finding the event and its type despite warehouse confirming it exists as a Virtual event.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Mr. Jeff AMZ instead of the expected ecommerceChris partner for Account Health appeals.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denied finding the New Amazon Account benefit whose value ($60,000) exists in the warehouse.
- **FAIL** Q2062 [WA_DIGEST/llm] (false_denial) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Ground truth says the lever was bundling, but Olivia declined to state it despite having the quote.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Missed the actual joke 'Claude Basics' and falsely denied finding it despite it existing in the chat.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Cited wrong date (Aug 27) and wrong recording instead of the actual last shared call recording on 2026-04-29.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Ground truth cites Behnke's fb_post naming GNO Partners, but Olivia denied finding it.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies Richard credited George Borowski despite quoting the exact line to him, then reverses the attribution.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Missed the specific 29% figure and the MCP $10k/mo build-and-sell guide, giving unrelated substitutes instead.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Denies existence of both the Shawn Chamberlain Amazon thread and WhatsApp API comparison despite ground truth confirming both exist.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Both concerns are wrong—no mention of waiting for slow referral data or asking for warehouse software recommendations.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post content and wrong WhatsApp comparison; correct facts about beauty/supplement size comparison omitted, plus a dodge.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Attorney part correct but Olivia falsely denied finding the Hermes/SP API detail that ground truth confirms exists.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the specific ChatGPT Artface earring CSV/reviews example, giving unrelated Claude/Klaviyo/Shopify anecdotes instead.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Olivia cites a trade/tariff bill topic, contradicting expected intellectual property/lawsuits resource.
- **FAIL** Q1046 [GEN/llm] (false_denial) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Ground truth shows Eli Zavdi's comment exists, but Olivia denied finding it and asked for clarification instead.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Missed the actual newest uploads (2026-07-23 restricted videos), citing older Aug dates instead.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Video is restricted to title/date/link only, but Olivia disclosed detailed discussion content and takeaways.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim quotes with timestamps despite no transcript access, exactly what the rubric forbids.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Confirms Orange Co chapter via Facebook evidence but omits 'Chapter Leads' and hedges rather than confirming.
- **PARTIAL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Found the value-add tip correctly but failed to locate the WhatsApp 'looking forward' comment, asking for clarification instead.
- **PARTIAL** Q1038 [GEN/llm] (no_count) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Confirms 'taken out on statement like other charges' but omits that it was specifically the ad spend charge.
