# Olivia eval — 2026-08-17 — 218 judged · PASS 198 · PARTIAL 0 · FAIL 20 (9.2%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 5 fail (31%) · 0 partial
- 🔴 **FORM**: 4 asked · 1 fail (25%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 4 fail (22%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 2 fail (20%) · 0 partial
- 🟡 **AT_PROFILE**: 21 asked · 2 fail (10%) · 0 partial
- 🟡 **WA_RAW**: 22 asked · 2 fail (9%) · 0 partial
- 🟡 **REAL**: 11 asked · 1 fail (9%) · 0 partial
- 🟡 **GEN**: 49 asked · 3 fail (6%) · 0 partial
- 🟢 **EVENT**: 11 asked · 0 fail (0%) · 0 partial
- 🟢 **WA_DIGEST**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **FB**: 30 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 218 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **wrong_fact** | 10 | 0 | 4.6% | #1 |
| **false_denial** | 7 | 0 | 3.2% | #1 #8 |
| **over_refusal** | 2 | 0 | 0.9% | #3 #10 #12 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015; Olivia denied finding any founding year information.
- **FAIL** Q2012 [AT_PROFILE/llm] (over_refusal) What is Dana E. Mavros's title at her company?
  - Refused title yet leaked 'CEO' from her bio, effectively naming a title as warned against.
- **FAIL** Q2043 [PARTNER/llm] (false_denial) What member offer does Hector Ai provide to the MDS community?
  - Denies an official Hector Ai member offer that the warehouse confirms exists (MDS Pricing + Self-Serve DSP+ Managed Services).
- **FAIL** Q2050 [PARTNER/llm] (wrong_fact) Which MDS partner focused on Account Health, run by former Amazon Seller Performance/Policy Enforcement employees, helps sellers with suspensions and plan of action appeals?
  - Named Riverbend Consulting instead of the expected partner ecommerceChris.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Olivia denied finding the benefit despite warehouse containing a verified $60,000 offer value.
- **FAIL** Q2060 [PARTNER/llm] (false_denial) What's the member offer value for the New Amazon Account partner?
  - Denied the specific partner exists and gave a wrong offer instead of the $60k Account Manager value.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Ground truth confirms the joke 'Claude Basics' exists, but Olivia denied finding it.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Gave August 10 recording, but ground truth shows last call recording shared was April 29, 2026.
- **FAIL** Q2096 [FORM/llm] (over_refusal) What is my title according to my membership application?
  - User asking about their own application title is refused despite data being available and shareable to them.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - 29% matches, but MCP video is about ad optimization/analysis, not building/selling MCPs for $10k/mo.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Both cited posts are about email attribution and multi-channel journeys, not the expected referral-traffic-delay and warehouse-software concerns.
- **FAIL** Q2137 [CROSS/llm] (wrong_fact) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Wrong FB post topic and wrong WhatsApp quote/comparison versus expected supplement-sellers post and beauty-size comparison.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Correctly flags no direct link but denies the WhatsApp 'next session' comment exists, contradicting expected ground truth.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Cites unrelated Claude/Shopify examples instead of the expected ChatGPT Artface earring review example.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Wrong topic entirely—expected IP/trademarks/lawsuits resource, Olivia gave unrelated trade attorney/tariff bill story.
- **FAIL** Q1038 [GEN/llm] (wrong_fact) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - He specifically mentioned 'ad spend' charge, not a generic 'credit'—wrong specific fact.
- **FAIL** Q1046 [GEN/llm] (wrong_fact) Who asked in a comment about getting access if you don't naturally have it, regarding something not making the cut?
  - Wrong person named (Salomon Stroh) instead of Eli Zavdi as the commenter asking about access.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Wrong dates cited (Aug 5-10) instead of actual latest uploads on 2026-07-23 with correct titles.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated direct quotes and detailed transcript content despite no transcript search capability existing.
- **FAIL** Q2170 [REAL/verbatim] (false_denial) how about recap of MDS trading
  - Claims no activity despite ground truth showing 65 messages that week in MDS Trading.
