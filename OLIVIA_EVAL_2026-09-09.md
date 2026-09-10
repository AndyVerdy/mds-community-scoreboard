# Olivia eval — 2026-09-09 — 220 judged · PASS 195 · PARTIAL 4 · FAIL 21 (9.5%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 5 fail (31%) · 1 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **EVENT**: 11 asked · 3 fail (27%) · 0 partial
- 🔴 **WA_DIGEST**: 12 asked · 2 fail (17%) · 0 partial
- 🔴 **FB**: 30 asked · 3 fail (10%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **WA_RAW**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **PARTNER**: 18 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 1 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 10 | 1 | 4.5% | #1 #8 |
| **wrong_fact** | 8 | 0 | 3.6% | #1 |
| **no_count** | 0 | 2 | 0.0% | #5 |
| **no_answer** | 1 | 0 | 0.5% | infra |
| **dodge** | 0 | 1 | 0.0% | #1 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 as founding year, but Olivia denied any such data exists.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Olivia denies the event exists despite ground truth confirming it's in Kaua'i, Hawaii.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Denied finding the event despite a warehouse-verified start time existing for it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Ground truth confirms the event exists and is Virtual, but Olivia denied finding it.
- **FAIL** Q2062 [WA_DIGEST/llm] (no_answer) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Olivia produced no answer at all despite an available ground-truth fact about bundling as AOV lever.
- **FAIL** Q2071 [WA_DIGEST/llm] (false_denial) In the MDS Centurion 20M+ chat, why is Ershad unavailable on the proposed meeting day?
  - Olivia denies finding Ershad's World Cup semifinal excuse despite it existing in the warehouse.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date (Sept 2 vs Apr 29) and platform explicitly denied though it's app.mds.co, contradicting expected fact.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - The May 13 post actually states the May 22, 2026 closing date, but Olivia denied finding it.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Olivia denies George Borowski had the pattern, contradicting ground truth that Richard attributed it to him.
- **FAIL** Q2111 [FB/llm] (false_denial) According to Prue Millsap's reply to Maxwell Sigurdson-Scott, what tactic was suggested if the price point is low?
  - Olivia denied the comment exists, but ground truth confirms Prue's reply suggesting bundling.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Gave wrong percentage (40% / 1-5%) instead of 29%, and MCP guide description misses the $10k/mo playbook content.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Denies finding the WhatsApp comparison that ground truth confirms exists, calling another platform's API worse.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post content and missed the actual size comparison ('bigger than beauty') present in the warehouse.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Denied finding the Hermes/SP-API connection detail that ground truth confirms exists in the warehouse.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed expected ChatGPT/Artface earring review example; cited Claude Code content instead, contradicting the DIY-skeptic counter-narrative.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Cites wrong post/date/topic (international trade law, June 2026) instead of the IP/trademark/lawsuit resource from Nov 2025.
- **FAIL** Q1038 [GEN/llm] (wrong_fact) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Says 'credit' not 'ad spend charge', misidentifying the type of charge expected.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Named wrong commenter (Salomon Stroh) instead of Eli Zavdi, and wrong post/date.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cited September 2 videos instead of the actual latest (2026-07-23) uploads including required restricted titles.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia gave a full detailed summary of restricted content instead of only the title/date/link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim transcript quotes with timestamps despite no transcript search capability existing.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Names Orange Co Chapter but omits his affiliation with Chapter Leads.
- **PARTIAL** Q2091 [WA_RAW/llm] (dodge) Someone in the Centurion group asked about scraping Amazon reviews "
  - Cites related threads but never states the expected core fact: Claude+VS Code with Apify's 15k actors/Amazon reviews category.
- **PARTIAL** Q2141 [CROSS/llm] (false_denial) Someone asked Brian Kelsey if he had contacts that could help, and separately a member shared a story about a contact who used to sell Nike - what happened to that Nike seller's ability to sell after years of doing it?
  - Correctly details the Nike seller's loss of ability but denies the Brian Kelsey contact request, which ground truth confirms occurred.
- **PARTIAL** Q2170 [REAL/verbatim] (no_count) how about recap of MDS trading
  - Gives a recap but cites only 2 messages/participants versus expected 65 messages that week.
