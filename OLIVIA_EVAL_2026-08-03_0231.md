# Olivia eval — 2026-08-03 — 33 judged · PASS 26 · PARTIAL 4 · FAIL 3 (9.1%)  [target <1%]

## Health by source
- 🔴 **ORGANIC/CHATS**: 4 asked · 1 fail (25%) · 0 partial
- 🔴 **ORGANIC/PEOPLE**: 4 asked · 1 fail (25%) · 0 partial
- 🟡 **SMOKE**: 11 asked · 1 fail (9%) · 1 partial
- 🟢 **ORGANIC/CAPABILITIES**: 1 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/GENERAL**: 4 asked · 0 fail (0%) · 3 partial
- 🟢 **ORGANIC/COUNTING**: 2 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/PARTNERS**: 2 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/SENSITIVE**: 2 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/SELF**: 1 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/FACEBOOK**: 2 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 33 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 2 | 1 | 6.1% | #1 #8 |
| **no_answer** | 0 | 1 | 0.0% | infra |
| **fabrication** | 1 | 0 | 3.0% | #1 |
| **dodge** | 0 | 1 | 0.0% | #1 |
| **over_refusal** | 0 | 1 | 0.0% | #3 #10 #12 |

- **FAIL** Q3096 [ORGANIC/PEOPLE/llm] (fabrication) Who has done a kickstarter campaign and got funded
  - Claims funded campaigns exist when ground truth says only launch posts exist and no funded campaign is confirmed.
- **FAIL** Q3110 [ORGANIC/CHATS/llm] (false_denial) Tell me what other sellers are doing for Amazon creator connection
  - Denies finding data despite expected real member posts/threads existing on Amazon Creator Connection tactics.
- **FAIL** Q9024 [SMOKE/llm] (false_denial) is there a fulfillment conference happening in the city?
  - Expected semantic search should surface a fulfillment conference event, but Olivia denied its existence outright.
- **PARTIAL** Q3010 [ORGANIC/GENERAL/llm] (no_answer) Can you pull me some info on price strikethroughs on TikTok Shop? I have a retail price below list, but am not seeing a strikethrough
  - Honest gap admission is acceptable, but offers no partial troubleshooting info that might exist for TikTok Shop pricing rules.
- **PARTIAL** Q3098 [ORGANIC/GENERAL/llm] (dodge) What's some great resources that I can share with new member so they get value immediately after joining?
  - Lists concrete resources (docs, brains, provider directory) but adds people-oriented items and offers a clarifying question instead of full resource list.
- **PARTIAL** Q3111 [ORGANIC/GENERAL/llm] (over_refusal) What are current daily task recommendations for managing an Amazon account
  - Honest decline without guessing, but offers no closest real content or links as expected fallback.
- **PARTIAL** Q9023 [SMOKE/llm] (false_denial) any events near me?
  - Offers alternatives but must verify whether truly no upcoming NY-area events exist versus expected reg link result.
