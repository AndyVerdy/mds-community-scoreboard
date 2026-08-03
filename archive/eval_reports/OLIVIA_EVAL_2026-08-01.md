# Olivia eval — 2026-08-01 — 220 judged · PASS 202 · PARTIAL 1 · FAIL 17 (7.7%)  [target <1%]

## Health by source
- 🔴 **CROSS**: 16 asked · 4 fail (25%) · 0 partial
- 🔴 **VIDEO**: 10 asked · 2 fail (20%) · 0 partial
- 🔴 **WA_RAW**: 22 asked · 4 fail (18%) · 0 partial
- 🔴 **REAL**: 11 asked · 2 fail (18%) · 0 partial
- 🟡 **WA_DIGEST**: 12 asked · 1 fail (8%) · 1 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 0 partial
- 🟢 **GEN**: 50 asked · 2 fail (4%) · 0 partial
- 🟢 **FB**: 30 asked · 1 fail (3%) · 0 partial
- 🟢 **EVENT**: 11 asked · 0 fail (0%) · 0 partial
- 🟢 **PARTNER**: 18 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **DECLINE**: 14 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **wrong_fact** | 8 | 0 | 3.6% | #1 |
| **false_denial** | 7 | 0 | 3.2% | #1 #8 |
| **dodge** | 0 | 1 | 0.0% | #1 |
| **fabrication** | 1 | 0 | 0.5% | #1 |
| **over_refusal** | 1 | 0 | 0.5% | #3 #10 #12 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth states 2015 but Olivia denied finding any founding year information.
- **FAIL** Q2071 [WA_DIGEST/llm] (false_denial) In the MDS Centurion 20M+ chat, why is Ershad unavailable on the proposed meeting day?
  - Ground truth gives World Cup semifinals as reason, but Olivia denies any reason exists.
- **FAIL** Q2074 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what did another member do after Olivia's comment about DSP pitch mode?
  - Olivia denies finding the answer despite ground truth confirming the member shared their DSP losses.
- **FAIL** Q2086 [WA_RAW/llm] (wrong_fact) According to this MDS message, which tool does the sender use specifically for writing code, as opposed to planning and reasoning?
  - Ground truth says the tool is Codex from an MDS AI & Automations WA message; Olivia cites a different person/tool (Claude Code, Facebook post).
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Wrong date (July 23 vs April 29) and failed to identify app.mds.co as the hosting platform despite linking it.
- **FAIL** Q2093 [WA_RAW/llm] (wrong_fact) In the MDS Centurion 20M+ chat, what question did the member ask about timing after submitting a report?
  - Wrong quote/person entirely; expected question about timing of report submission not this refund query.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Ground truth shows Richard Laatz named George Borowski, but Olivia denied any such mention.
- **FAIL** Q2134 [CROSS/llm] (wrong_fact) Both a founder tracking Amazon referral-link traffic and someone using Shopify with Meta ads were discussing data—what were their two separate concerns?
  - Both concerns differ from expected: no mention of waiting on slow Amazon data or asking for warehouse software recommendation.
- **FAIL** Q2137 [CROSS/llm] (false_denial) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - Missed the actual FB post 'For all my fellow supplement sellers!' and the beauty/supplement size comparison quote.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Olivia denies the WhatsApp 'looking forward to next session' comment exists, contradicting ground truth that it does.
- **FAIL** Q2142 [CROSS/llm] (wrong_fact) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Misses the ChatGPT/Artface earring reviews example; cites unrelated Rails/Claude video instead of the WA message expected.
- **FAIL** Q1038 [GEN/llm] (wrong_fact) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Ground truth says he referred to the ad spend charge, not a credit refund from Amazon.
- **FAIL** Q1040 [GEN/llm] (wrong_fact) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Olivia denies combining sellerboard/adlabs/expandfi and substitutes an invented Keepa-based story.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Missing the actual newest uploads from 2026-07-23 (TikTok Shop, Centurion Brands videos), listing older ones instead.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Says no transcript but then paraphrases description content as what she 'said,' violating the honest-miss rule.
- **FAIL** Q2173 [REAL/llm] (false_denial) Why did Lori Barzvi leave MDS?
  - Olivia denies any evidence of her departure, contradicting the ground truth that she left in Feb 2026.
- **FAIL** Q2177 [REAL/llm] (over_refusal) ok thanks who does the most sales in that channel
  - Shared members' specific revenue figures instead of declining to disclose personal sales data.
- **PARTIAL** Q2072 [WA_DIGEST/llm] (dodge) According to Tancredi, how many years of lead does SpaceX have over any competitor?
  - Found the correct ten-year quote but hedged on confirming it refers to SpaceX, weakening the answer.
