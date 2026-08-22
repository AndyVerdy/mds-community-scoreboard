# Olivia eval — 2026-08-22 — 220 judged · PASS 197 · PARTIAL 1 · FAIL 22 (10.0%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 11 asked · 4 fail (36%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 3 fail (30%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 4 fail (22%) · 0 partial
- 🔴 **CROSS**: 16 asked · 3 fail (19%) · 1 partial
- 🟡 **AT_PROFILE**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **FB**: 30 asked · 1 fail (3%) · 0 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **wrong_fact** | 10 | 1 | 4.5% | #1 |
| **false_denial** | 9 | 0 | 4.1% | #1 #8 |
| **over_refusal** | 2 | 0 | 0.9% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth states 2015, but Olivia denied finding any founding year information.
- **FAIL** Q2012 [AT_PROFILE/llm] (over_refusal) What is Dana E. Mavros's title at her company?
  - Olivia disclosed a title-like fact (worked up to CEO) despite refusing the direct title question.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denied finding the event despite ground truth confirming it exists and is in Kaua'i, Hawaii.
- **FAIL** Q2037 [EVENT/llm] (wrong_fact) What time does the SCFest Miami 2026 Recommended Event start?
  - Olivia states 10:00 UTC while ground truth confirms 11:00 AM UTC start time.
- **FAIL** Q2040 [EVENT/llm] (false_denial) What time does the SoFlo Chapter TikTok Tour Afterparty start?
  - Ground truth confirms the event exists with a specific time, but Olivia denied finding it.
- **FAIL** Q2042 [EVENT/llm] (false_denial) What type of event is the TikTok Shop (Verified Sellers) Channel Meetup?
  - Denies finding the event and its virtual format despite it existing in warehouse data.
- **FAIL** Q2043 [PARTNER/llm] (false_denial) What member offer does Hector Ai provide to the MDS community?
  - Olivia denies Hector Ai exists despite ground truth confirming its member offer.
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Names Riverbend Consulting, not ecommerceChris, contradicting the verified partner for Account Health suspensions.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denies existence of the New Amazon Account benefit despite ground truth confirming a $60,000 offer value.
- **FAIL** Q2060 [PARTNER/llm] (false_denial) What's the member offer value for the New Amazon Account partner?
  - Denied existence of the New Amazon Account partner deal that ground truth confirms exists.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Olivia failed to find 'Claude Basics' and denied the joke exists despite it being in the warehouse.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Gave a different, later date and denied a hosting platform, contradicting expected 2026-04-29 on app.mds.co.
- **FAIL** Q2105 [FB/llm] (false_denial) Which agency did Mark Behnke use that only gave advice without execution?
  - Ground truth clearly names GNO Partners, but Olivia denied finding any information.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Correct 29% figure but MCP video described as Amazon MCP hype/reality, not the WA $10k/mo playbook guide.
- **FAIL** Q2131 [CROSS/llm] (wrong_fact) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Olivia found an unrelated message and inverted the comparison—expected was another platform's API being worse than Amazon's, not Amazon criticized.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Cites unrelated Claude Code/Shopify stories instead of the expected ChatGPT Artface earring review example.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong topic and wrong post; expected resource is about IP/lawsuits, not trade attorney/tariff legislation.
- **FAIL** Q1038 [GEN/llm] (wrong_fact) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Expected charge type was 'ad spend', but Olivia vaguely says 'credit card charge' without specifying ad spend.
- **FAIL** Q1040 [GEN/llm] (wrong_fact) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Cited data sources (sheet + Keepa) contradict expected sellerboard, adlabs, expandfi combination.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Aug 5-10 videos, missing the actual latest (2026-07-23) uploads and restricted flags entirely.
- **FAIL** Q2167 [VIDEO/llm] (over_refusal) What was discussed in the video 'How Centurion Brands Expand Beyond Amazon'?
  - Olivia gave a full content summary of a restricted video instead of only title, date, duration, and link.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim quotes and timestamps as if transcripts exist, contradicting the ground truth that none do.
- **PARTIAL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - WhatsApp comparison matches exactly, but FB post cited differs from expected 'fellow supplement sellers' post.
