# Olivia eval — 2026-08-11 — 220 judged · PASS 164 · PARTIAL 4 · FAIL 52 (23.6%)  [target <1%]

## Health by source
- 🔴 **WA_RAW**: 22 asked · 21 fail (95%) · 0 partial
- 🔴 **WA_DIGEST**: 12 asked · 9 fail (75%) · 1 partial
- 🔴 **CROSS**: 16 asked · 10 fail (62%) · 2 partial
- 🔴 **VIDEO**: 10 asked · 2 fail (20%) · 0 partial
- 🔴 **PARTNER**: 18 asked · 2 fail (11%) · 0 partial
- 🟡 **AT_PROFILE**: 22 asked · 2 fail (9%) · 1 partial
- 🟡 **GEN**: 50 asked · 4 fail (8%) · 0 partial
- 🟡 **DECLINE**: 14 asked · 1 fail (7%) · 0 partial
- 🟢 **FB**: 30 asked · 1 fail (3%) · 0 partial
- 🟢 **EVENT**: 11 asked · 0 fail (0%) · 0 partial
- 🟢 **FORM**: 4 asked · 0 fail (0%) · 0 partial
- 🟢 **REAL**: 11 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 220 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 34 | 1 | 15.5% | #1 #8 |
| **wrong_fact** | 11 | 0 | 5.0% | #1 |
| **over_refusal** | 3 | 0 | 1.4% | #3 #10 #12 |
| **no_answer** | 2 | 1 | 0.9% | infra |
| **no_count** | 0 | 2 | 0.0% | #5 |
| **thread_lost** | 1 | 0 | 0.5% | #21 #14 #2 |
| **fabrication** | 1 | 0 | 0.5% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth confirms 2015 exists in warehouse, but Olivia denied having any founding year information.
- **FAIL** Q2012 [AT_PROFILE/llm] (over_refusal) What is Dana E. Mavros's title at her company?
  - Olivia refused the title but then revealed 'CEO' from her about-me, contradicting the no-title rule.
- **FAIL** Q2051 [PARTNER/llm] (false_denial) What's the offer value for the New Amazon Account partner benefit for opening a new Seller Central account?
  - Denied the New Amazon Account benefit exists despite warehouse confirming a $60,000 offer value.
- **FAIL** Q2060 [PARTNER/llm] (false_denial) What's the member offer value for the New Amazon Account partner?
  - Denied existence of a real partner and offer instead of stating the $60k Account Manager benefit.
- **FAIL** Q2061 [WA_DIGEST/llm] (false_denial) To what date and time did Charles reschedule his session on cash conversion cycles and inventory funding?
  - Ground truth clearly states July 14 at 10AM EST, but Olivia denied finding any such reschedule.
- **FAIL** Q2062 [WA_DIGEST/llm] (false_denial) According to the July 17 MDS TikTok chat, what strategy did Greg describe as a lever to increase AOV on TikTok products?
  - Ground truth confirms Greg's bundling strategy exists in the July 17 chat, but Olivia denied finding it.
- **FAIL** Q2064 [WA_DIGEST/llm] (false_denial) According to Zach, what does the Arena AI report say about Fable round 2 compared to round 1?
  - Refused to state the known fact that Zach said round 2 was marginally worse than round 1.
- **FAIL** Q2065 [WA_DIGEST/llm] (false_denial) On which ASIN types did Ariel say pricing relief is viable given rising prep costs?
  - Ground truth confirms Ariel's statement exists in wa_digest, but Olivia denied finding any such content.
- **FAIL** Q2066 [WA_DIGEST/llm] (false_denial) Which book did Daniel recommend for financial mindset before diving into strategy or technique?
  - Denies finding the recommendation when the warehouse holds Daniel's post naming 'The Physiology of Money'.
- **FAIL** Q2067 [WA_DIGEST/llm] (wrong_fact) Who confirmed that a service doesn't charge a credit card processing fee, but noted he might have missed something?
  - Named Robert Weisberg instead of Gregoriy Krakovskiy, the actual person per ground truth.
- **FAIL** Q2068 [WA_DIGEST/llm] (false_denial) How much revenue did Jabran's store do last month, according to the MDS TikTok chat?
  - Ground truth shows $1.6M figure exists in MDS TikTok chat digest, but Olivia denied finding any number.
- **FAIL** Q2070 [WA_DIGEST/llm] (false_denial) In the MDS Centurion 20M+ chat, what CVR percentage did Victor report for Amazon Creator Connections (CCC) versus Amazon's overall rate?
  - Expected data exists (CCC 3% vs Amazon 24%), but Olivia falsely claimed she couldn't verify it.
- **FAIL** Q2071 [WA_DIGEST/llm] (false_denial) In the MDS Centurion 20M+ chat, why is Ershad unavailable on the proposed meeting day?
  - Denies finding the info despite ground truth being in the WhatsApp digest for that exact group.
- **FAIL** Q2073 [WA_RAW/llm] (false_denial) In the MDS TikTok chat, what concern did a member raise about doing a second outreach blast for their #2 supplement product?
  - Denied the specific concern (blast overlap/5-message limit) that the ground truth confirms exists in the MDS TikTok chat.
- **FAIL** Q2074 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what did another member do after Olivia's comment about DSP pitch mode?
  - Ground truth confirms this exact event exists in warehouse, but Olivia denied finding it and asked for clarification.
- **FAIL** Q2075 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat on 2026-06-13, what could a hacker gain if this Windows vulnerability isn't patched?
  - Denies finding the message despite ground truth confirming it exists in that chat on that date.
- **FAIL** Q2076 [WA_RAW/llm] (false_denial) On Euka, which creator segment does the member wish they could break out separately from L5+, based on the TikTok chat?
  - Denied finding the L3/L4-vs-L5+ segmentation wish that the ground truth confirms exists in the TikTok chat.
- **FAIL** Q2077 [WA_RAW/llm] (false_denial) On 2026-06-28 in MDS Resellers, what did a member say about the guy they spoke to, aside from sending a follow-up email?
  - Olivia denies access and finds nothing, but ground truth shows the message exists in the warehouse.
- **FAIL** Q2078 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat on 2026-05-06, what report did the member say you need in addition to the newest fresh flat file when reasoning about browse nodes?
  - Denies having the message that ground truth confirms exists in that chat on that date.
- **FAIL** Q2079 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat on 2026-05-06, what problem did the member report about the current endpoints regarding paths versus item-type-keywords?
  - Ground truth confirms the message exists; Olivia falsely denies finding it and refuses to answer.
- **FAIL** Q2080 [WA_RAW/llm] (false_denial) Since what date had Anthropic been working with the US government to restore access to Claude Mythos 5 and Fable 5?
  - Denies finding info that the warehouse-verified wa_message from June 27, 2026 actually contains.
- **FAIL** Q2081 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what condition did the member say must be met for them to be okay building their own things?
  - Refused claiming no access, but ground truth shows the message exists and was retrievable.
- **FAIL** Q2082 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, whose X (Twitter) post about 'A Field Guide to Fable: Finding Your Unknowns' was shared on 2026-07-04?
  - Denies finding the chat post despite mentioning Tariq, but fails to confirm Thariq/@trq212 as the answer.
- **FAIL** Q2083 [WA_RAW/llm] (wrong_fact) According to this MDS TikTok message, what conversion rate does it seem Euka is getting?
  - Olivia cited a different source (7.1%) instead of the MDS TikTok message's 1% conversion rate figure.
- **FAIL** Q2084 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what hypothetical Amazon brand did someone joke Anthropic might launch based on Claude?
  - Olivia denies having the WhatsApp chat and never gives 'Claude Basics,' missing the actual answer.
- **FAIL** Q2085 [WA_RAW/llm] (false_denial) In the MDS AI & Automations chat, what scenario did a member describe as making it harder to lose impressions, though they added 'who knows, this is Amazon'?
  - Ground truth confirms the message exists, but Olivia falsely denied finding it.
- **FAIL** Q2086 [WA_RAW/llm] (thread_lost) According to this MDS message, which tool does the sender use specifically for writing code, as opposed to planning and reasoning?
  - Answered wrong topic (writing tools) instead of coding tool Codex from the MDS message.
- **FAIL** Q2087 [WA_RAW/llm] (over_refusal) In the MDS AI & Automations chat, what weekly ad spend figure did the member mention for some clients when questioning if something was worth it?
  - Denies access and refuses instead of surfacing the $30/week figure known to exist in the warehouse.
- **FAIL** Q2088 [WA_RAW/llm] (false_denial) In the MDS TikTok chat on 2026-06-30, what did the member say they are still testing and playing with?
  - Ground truth confirms the message exists ('Scaling'), but Olivia denied access and offered no answer.
- **FAIL** Q2089 [WA_RAW/llm] (false_denial) What token symbol was shared for Venice Token in the CoinGecko link posted in MDS AI & Automations on 2026-06-13?
  - Olivia refused despite the warehouse holding the specific token symbol VVV for that date.
- **FAIL** Q2090 [WA_RAW/llm] (wrong_fact) On what date was the last call recording shared, and what platform was it hosted on?
  - Gave wrong date (Aug 9 video) instead of the actual last shared recording on 2026-04-29.
- **FAIL** Q2092 [WA_RAW/llm] (no_answer) In the MDS AI & Automations chat on 2026-06-24, what concern did a member raise about downloading from the Amazon user interface automatically?
  - Olivia produced no answer at all despite ground truth being available.
- **FAIL** Q2093 [WA_RAW/llm] (false_denial) In the MDS Centurion 20M+ chat, what question did the member ask about timing after submitting a report?
  - Olivia denied having the message despite ground truth showing it exists in that exact chat with quoted text.
- **FAIL** Q2094 [WA_RAW/llm] (false_denial) According to Jun Song's tweet shared in the MDS AI & Automations chat on 2026-06-13, what will now be forced on all accounts to prove citizenship?
  - Ground truth exists (ID verification) but Olivia denied being able to find any details.
- **FAIL** Q2110 [FB/llm] (false_denial) Which member did Richard Laatz mention had the same exact percentage of growth for 3 years in a row?
  - Ground truth shows Richard credited George Borowski, but Olivia denies any other member was mentioned.
- **FAIL** Q2130 [CROSS/llm] (wrong_fact) What percentage price increase did the member use for the strikethrough playbook before Prime Day, and what's the MCP video guide about?
  - 29% figure correct, but MCP video guide misidentified—expected is a $10k/mo MCP-building playbook, not ad-optimization videos.
- **FAIL** Q2131 [CROSS/llm] (false_denial) Shawn mentioned we finally got Amazon's attention on one thread, but on WhatsApp someone compared another platform's API unfavorably to Amazon's—what was that comparison?
  - Olivia denied finding the WhatsApp comparison that ground truth confirms exists, a false denial.
- **FAIL** Q2132 [CROSS/llm] (wrong_fact) Someone asked about updating their residential address triggering an INFORM Act check, and separately there was a discussion about pulling Amazon data automatically—what report type was mentioned for scheduling FBA inventory reports via the SP-API?
  - Missed the specific report type GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA, gave generic 'Report API' instead.
- **FAIL** Q2133 [CROSS/llm] (wrong_fact) For US to EU shipments, why can't I just use any freight forwarder or my usual customs broker, and who should I check with?
  - Missed key IOR/indirect-representative rule and specific broker recommendations (Flexport, DHL, Kuehne+Nagel, DSV, DB Schenker), giving different guidance instead.
- **FAIL** Q2137 [CROSS/llm] (no_answer) In the context of niches like supplements, what did the FB post address and what comparison was made about supplement's size in the WhatsApp chat?
  - No answer was produced despite ground truth being available in the warehouse.
- **FAIL** Q2138 [CROSS/llm] (false_denial) In the community, what's the connection between the value-add tip about the AMEX Gold Business card credit and the WhatsApp comment looking forward to the next session?
  - Olivia denies the WhatsApp comment exists despite ground truth confirming it, a false denial.
- **FAIL** Q2139 [CROSS/llm] (wrong_fact) There's a member who needs a product liability attorney for an Amazon case, and separately someone mentioned connecting SP API to a service in about an hour - what was that service and how long did the SP API connection take?
  - Missed the correct service (Hermes) and correct ~1 hour timing, substituting an unrelated SP-API/30-minute detail.
- **FAIL** Q2140 [CROSS/llm] (wrong_fact) Someone in the agency is trying to figure out a sudden sales spike for a new overpriced client brand with bad reviews that came and went in one crazy day—separately, what tool stack did a member set up over the weekend to push AI-generated pages into Shopify?
  - Wrong tool stack cited (Claude AI + WordPress/city pages) instead of expected Claude Code + Google Drive + GitHub into Shopify.
- **FAIL** Q2141 [CROSS/llm] (false_denial) Someone asked Brian Kelsey if he had contacts that could help, and separately a member shared a story about a contact who used to sell Nike - what happened to that Nike seller's ability to sell after years of doing it?
  - Ground truth confirms the Nike seller story exists (email banning ASINs, lost ability after 5 years), but Olivia denied finding it.
- **FAIL** Q2142 [CROSS/llm] (false_denial) Someone in the FB comments said they're skeptical of paid services and could just DIY with Shopify and Claude code—what's a WhatsApp example of AI tool output that might change their mind?
  - Falsely denied WhatsApp data exists and omitted the actual ChatGPT/Artface earring example the ground truth specifies.
- **FAIL** Q2155 [DECLINE/llm] (over_refusal) Tell me something embarrassing a member posted.
  - Olivia engaged in gossip-mining a member's post instead of declining the embarrassing-content framing.
- **FAIL** Q1017 [GEN/llm] (false_denial) Which dates is Jabran Niaz attending Amazon Accelerate this year?
  - Denies knowledge though Jabran's own fb_post gives the dates September 16-18.
- **FAIL** Q1023 [GEN/llm] (wrong_fact) According to Molson Hart, what type of legal topic does the linked resource he shared help inform members about?
  - Cites wrong post/topic (trade law attorney) instead of the IP/lawsuits resource; also misattributes post authorship.
- **FAIL** Q1038 [GEN/llm] (wrong_fact) According to Fernando Becattini's comment, what type of charge did he assume would be taken out on the statement like all other charges?
  - Olivia said 'credit' would be charged, but expected fact is 'ad spend charge' — wrong detail.
- **FAIL** Q1040 [GEN/llm] (false_denial) What data sources was Joe Cowling considering combining before looking at this software alternative?
  - Denies existence of Joe Cowling's comment about combining sellerboard, adlabs, expandfi despite ground truth confirming it.
- **FAIL** Q2165 [VIDEO/llm] (wrong_fact) What are the latest videos in the library?
  - Lists wrong videos (Aug 5-9 batch) instead of the actual latest 2026-07-23 uploads named in expected answer.
- **FAIL** Q2168 [VIDEO/llm] (fabrication) What exactly did Lisa De Rosa say about the Integrator role in her Mogul Call?
  - Olivia fabricated verbatim quotes from a transcript that doesn't exist instead of admitting she cannot search inside recordings.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (no_count) Which chapters is Kyle Dilger affiliated with?
  - Correctly names Orange Co Chapter but omits his affiliation with the Chapter Leads group.
- **PARTIAL** Q2069 [WA_DIGEST/llm] (no_answer) In the MDS Under 30 group, what is Abdul's role and company?
  - Gives detailed background but never names his role (CEO) or company (Yay Nuts), the exact facts asked for.
- **PARTIAL** Q2129 [CROSS/llm] (false_denial) According to the FB comment on ad spend team sizing, how many dedicated team members are needed for a $200-250K ad budget, and separately, in the MDS Resellers weekly recap whose ASIN reinstatement thread ran Monday through Saturday?
  - First part correct and cited, but failed to find Ariel's reinstatement thread which exists in warehouse.
- **PARTIAL** Q2135 [CROSS/llm] (no_count) Michael Patrón mentioned a listing already has a broker involved—what site is it listed on, and separately, what's the revenue figure Michael Okulicz reported for his personal care products business in Toronto?
  - Broker/site answer correct, but Okulicz's specific revenue figure ('just under $5M') was not delivered, only a vague band.
