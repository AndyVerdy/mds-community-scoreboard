# Olivia eval — 2026-09-02 — 220 judged · PASS 190 · PARTIAL 3 · FAIL 27 (12.3%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 11 asked · 5 fail (45%) · 1 partial
- 🔴 **CROSS**: 16 asked · 7 fail (44%) · 1 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **FORM**: 4 asked · 1 fail (25%) · 0 partial
- 🔴 **WA_RAW**: 22 asked · 4 fail (18%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **AT_PROFILE**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟢 **GEN**: 50 asked · 1 fail (2%) · 1 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 13 | 1 | 5.9% | #1 #8 |
| **wrong_fact** | 8 | 2 | 3.6% | #1 |
| **over_refusal** | 5 | 0 | 2.3% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2002 [AT_PROFILE/llm] (false_denial) Which chapters is Kyle Dilger affiliated with?
  - Ground truth confirms Dilger is affiliated with Orange Co and Chapter Leads, but Olivia denied finding him.
- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 as start year, but Olivia denied finding it.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Ground truth confirms the event exists in Kaua'i, Hawaii, but Olivia falsely denied finding it.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Wrong start time given (10:00 UTC) versus expected 11:00 UTC on April 4, 2026.
- **FAIL** Q2039 [EVENT/llm] (over_refusal) On what date is the Expert Call with Clayton Atchison from Carbon 6 scheduled?
  - Olivia withheld the specific date instead of providing June 28, 2022 as expected.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms the event exists with a specific start time, but Olivia denied any record of it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denied finding an event that ground truth confirms exists as a Virtual event.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Mr. Jeff AMZ and Seller Candy instead of the expected ecommerceChris partner.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denies the partner exists when ground truth confirms a $60,000 offer value.
- **FAIL** Q2082 [WA_RAW/llm] (wrong_fact) In the MDS AI & Automations chat, whose X (Twitter) post about 'A Field Guide to Fable: Finding Your Unknowns' was shared on 2026-07-04?
  - Olivia attributes sharing to Guido Reyes instead of the actual poster Thariq, misidentifying whose post it was.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Olivia denied the joke exists though warehouse confirms a 'Claude Basics' message on 2026-05-10.
- **FAIL** Q2090 [WA_RAW/llm] (over_refusal) On what date was the last call recording shared, and what platform was it hosted on?
  - Withheld a directly answerable fact instead of stating the date and platform from the record.
- **FAIL** Q2091 [WA_RAW/llm] (over_refusal) Someone in the Centurion group asked about scraping Amazon reviews "
  - Refused entirely instead of surfacing the verified Claude/VS Code/Apify answer that exists in warehouse.
- **FAIL** Q2096 [FORM/llm] (over_refusal) What is my title according to my membership application?
  - User asked about their own application data; refusing to share own title is over-refusal, not protecting others' privacy.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - Denied finding the May 22, 2026 deadline that ground truth says is in Eugene Khayman's post.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Ground truth says Richard named George Borowski, but Olivia denied any member was mentioned.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - 29% figure surfaces but MCP video is wrongly described as Model Context Protocol/dashboards, not the $10k/mo MCP-selling playbook.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Ground truth confirms both the Shawn post and WhatsApp API comparison exist, but Olivia denied finding either.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Neither cited concern matches expected: no mention of waiting for referral data to arrive or asking for warehouse software recommendation.
- **FAIL** Q2137 [CROSS/llm] (false_denial) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Olivia denies finding the FB post/WA comparison that the ground truth confirms exist, missing both facts.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Olivia denies any connection and misidentifies the WhatsApp comment as a different Facebook comment, contradicting expected facts.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Olivia denied finding the Hermes/SP-API connection info that ground truth confirms exists in the warehouse.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the expected ChatGPT/Artface earring reviews example, gave unrelated Claude Code stories instead.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong topic and wrong post; expected IP/lawsuits resource, Olivia gave unrelated trade-attorney citation misattributed to Molson Hart.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites wrong date/videos entirely, missing the expected 2026-07-23 uploads including the two named titles.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia disclosed full content/summary of a restricted video instead of only title, date, duration, and link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated a verbatim transcript quote when no transcripts exist to search inside recordings.
- **PARTIAL** Q2025 [EVENT/llm] (wrong_fact) What time does the MDS Experience private dinner at Sanga Las Vegas start?
  - Correct 18:00 time given but wrongly reinterpreted as UTC, adding an incorrect conversion.
- **PARTIAL** Q2141 [CROSS/llm] (false_denial) Someone asked Brian Kelsey if he had contacts that could help, and separately a member shared a story about a contact who used to sell Nike - what happened to that Nike seller's ability to sell after years of doing it?
  - Nike-seller facts match well, but Olivia denies the Brian Kelsey contact request the ground truth confirms occurred.
- **PARTIAL** Q1018 [GEN/llm] (wrong_fact) What discount code should MDS members use to save on the DTC event of the year in San Diego?
  - Correct code and discount but wrongly attributes post to Ian Sells instead of Eugene Khayman.
