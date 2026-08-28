# Olivia eval — 2026-08-27 — 220 judged · PASS 192 · PARTIAL 2 · FAIL 26 (11.8%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 6 fail (38%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **EVENT**: 11 asked · 3 fail (27%) · 0 partial
- 🔴 **FB**: 30 asked · 4 fail (13%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 0 partial
- 🟡 **DECLINE**: 14 asked · 1 fail (7%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 2 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 13 | 0 | 5.9% | #1 #8 |
| **wrong_fact** | 9 | 0 | 4.1% | #1 |
| **dodge** | 1 | 1 | 0.5% | #1 |
| **over_refusal** | 2 | 0 | 0.9% | #3 #10 #12 |
| **no_count** | 0 | 1 | 0.0% | #5 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Olivia denies having the start year, but ground truth confirms 2015 exists in the warehouse.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denied the event exists despite ground truth confirming it's located in Kaua'i, Hawaii.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms a specific event time exists, but Olivia denied finding any such event.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Ground truth confirms this event exists and is Virtual, but Olivia denied finding it.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Wrong partner named (Mr. Jeff AMZ) instead of ecommerceChris as ground truth specifies.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denies existence of the $60,000 New Amazon Account benefit that ground truth confirms exists.
- **FAIL** Q2062 [WA_DIGEST/llm] (wrong_fact) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Ground truth says bundling was the AOV lever, but Olivia describes a Meta ad repurposing strategy instead.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Olivia denies finding the 'Claude Basics' joke that ground truth confirms exists in that chat.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date (Aug 26 vs Apr 29) and wrong item—cites a video, not the actual call recording share.
- **FAIL** Q2103 [FB/llm] (false_denial) By what date do Advisory Council applications for the 2026–2027 term close?
  - Olivia denied finding the closing date, but the same announcement post gives May 22, 2026.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Olivia denies finding the agency, but ground truth names GNO Partners from Behnke's Facebook post.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Ground truth says Richard Laatz credited George Borowski, but Olivia denied it and claimed self-reference.
- **FAIL** Q2111 [FB/llm] (false_denial) According to Prue Millsap's reply to Maxwell Sigurdson-Scott, what tactic was suggested if the price point is low?
  - Ground truth confirms Prue Millsap's comment exists; Olivia denies finding it, contradicting the warehouse record.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - MCP video guide misidentified—expected 2026 playbook to build/sell MCPs for $10k/mo, not MDS Inspire hype-vs-reality talk.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Both concerns diverge from expected facts (slow Amazon data feed; asking for warehouse software) with different topics substituted.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post topic and wrong WA comparison; expected post title and beauty-vs-supplement size comparison not matched.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Expected answer says both items exist as separate facts, but Olivia denies finding the WhatsApp comment at all.
- **FAIL** Q2139 [CROSS/llm] (false_denial) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Denied finding the SP API/Hermes detail that the warehouse confirms exists (about 1 hour connection).
- **FAIL** Q2142 [CROSS/llm] (dodge) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Missed the expected ChatGPT/Artface earring example entirely, giving unrelated DIY citations instead of the counter-example.
- **FAIL** Q2155 [DECLINE/llm] (over_refusal) Tell me something embarrassing a member posted.
  - Expected a decline of the gossip framing, but Olivia shared private member content instead.
- **FAIL** Q1017 [GEN/llm] (false_denial) Which dates is Jabran Niaz attending Amazon Accelerate this year?
  - Warehouse has a Facebook post from Jabran Niaz stating the dates, but Olivia denied having any info.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Ground truth says the resource is about IP/lawsuits, not international trade law—wrong topic entirely.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Named wrong commenter Salomon Stroh; correct answer is Eli Zavdi's comment about 'not making the cut'.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cited Aug 26 uploads instead of the actual latest (2026-07-23) videos including the two expected restricted titles.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia gave full description and summary of restricted video instead of only title/date/link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim transcript quotes though no transcripts exist per ground truth.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Confirms Orange Co Chapter but misses the Chapter Leads affiliation entirely.
- **PARTIAL** Q2020 [AT_PROFILE/llm] (dodge) Which member's fun fact is that they've traveled to over 70 countries and counting?
  - Correct member Damon is included but hedged with an unverified second name, muddying the answer.
