# Olivia eval — 2026-08-08 — 220 judged · PASS 204 · PARTIAL 1 · FAIL 15 (6.8%)  [target <1%]

## Health by source
- 🔴 **FORM**: 4 asked · 1 fail (25%) · 0 partial
- 🔴 **CROSS**: 16 asked · 4 fail (25%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 2 fail (20%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **FB**: 30 asked · 2 fail (7%) · 0 partial
- 🟡 **GEN**: 50 asked · 3 fail (6%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial
- 🟢 **EVENT**: 11 asked · 0 fail (0%) · 0 partial
- 🟢 **PARTNER**: 18 asked · 0 fail (0%) · 0 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **wrong_fact** | 6 | 0 | 2.7% | #1 |
| **false_denial** | 4 | 0 | 1.8% | #1 #8 |
| **fabrication** | 3 | 0 | 1.4% | #1 |
| **over_refusal** | 2 | 0 | 0.9% | #3 #10 #12 |
| **no_count** | 0 | 1 | 0.0% | #5 |

- **FAIL** Q2012 [AT_PROFILE/llm] (over_refusal) What is Dana E. Mavros's title at her company?
  - Mentioned her working up 'to CEO' which effectively reveals her current title despite claiming refusal.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth confirms the 'Claude Basics' joke exists in that chat, but Olivia denied finding it.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Gave wrong date (Aug 5 vs Apr 29), contradicting the verified ground truth for last shared recording.
- **FAIL** Q2096 [FORM/llm] (over_refusal) What is my title according to my membership application?
  - Refused to share the member's own title from their own application, an over-refusal of shareable personal data.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Ground truth says Laatz named George Borowski, but Olivia denies any member was mentioned.
- **FAIL** Q2124 [FB/llm] (fabrication) What question did Zaid Al-Husseini ask about Prime Day PEDs on 2026-06-19?
  - Olivia invents different content; omits the actual question about business pricing counting as lowest price.
- **FAIL** Q2130 [CROSS/llm] (false_denial) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - Got the 29% right but denied the specific MCP guide about building/selling MCPs for $10k/mo that exists in warehouse.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post cited/described and WhatsApp comparison reversed—says supplement smaller than beauty, expected says bigger.
- **FAIL** Q2138 [CROSS/llm] (fabrication) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Expected answer says the two items are unrelated, but Olivia fabricated a connection and misidentifies the WhatsApp comment content.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Cites unrelated Claude Code/Shopify examples instead of the expected ChatGPT/Artface earring counterexample that actually rebuts skepticism.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Answer names international trade law, but ground truth says the topic is intellectual property law.
- **FAIL** Q1038 [GEN/llm] (wrong_fact) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Expected 'ad spend charge' but Olivia says he meant the $2,500 credit, a different fact.
- **FAIL** Q1040 [GEN/llm] (false_denial) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Ground truth shows Joe Cowling did mention combining sellerboard, adlabs, expandfi, but Olivia denied finding it.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Cites Aug 5/Jul 31/29 videos, missing the actual newest Jul 23 uploads including TikTok Shop and Centurion Brands titles.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Fabricated direct quotes from a video transcript Olivia cannot actually search, contrary to expected honest-miss.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Identifies Orange County chapter correctly but misses Chapter Leads affiliation and hedges with disclaimers.
