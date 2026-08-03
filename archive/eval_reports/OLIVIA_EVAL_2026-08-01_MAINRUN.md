# Olivia eval — 2026-08-01 — 165 judged · PASS 150 · PARTIAL 7 · FAIL 8 (4.8%)  [target <1%]

## Health by source
- 🔴 **ORGANIC/FACEBOOK**: 9 asked · 2 fail (22%) · 0 partial
- 🔴 **ORGANIC/SENSITIVE**: 10 asked · 1 fail (10%) · 0 partial
- 🟡 **ORGANIC/COUNTING**: 11 asked · 1 fail (9%) · 1 partial
- 🟡 **ORGANIC/CHATS**: 13 asked · 1 fail (8%) · 0 partial
- 🟡 **ORGANIC/PEOPLE**: 18 asked · 1 fail (6%) · 1 partial
- 🟢 **SMOKE**: 47 asked · 2 fail (4%) · 2 partial
- 🟢 **ORGANIC/GENERAL**: 12 asked · 0 fail (0%) · 1 partial
- 🟢 **ORGANIC/PARTNERS**: 12 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/EVENTS**: 14 asked · 0 fail (0%) · 2 partial
- 🟢 **ORGANIC/SELF**: 13 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/CAPABILITIES**: 6 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 165 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **dodge** | 0 | 4 | 0.0% | #1 |
| **false_denial** | 3 | 1 | 1.8% | #1 #8 |
| **over_refusal** | 2 | 1 | 1.2% | #3 #10 #12 |
| **wrong_fact** | 1 | 1 | 0.6% | #1 |
| **no_count** | 1 | 0 | 0.6% | #5 |
| **fabrication** | 1 | 0 | 0.6% | #1 |

- **FAIL** Q3041 [ORGANIC/COUNTING/llm] (no_count) How many MDS chapter are there
  - Olivia failed to give the derivable chapter count despite it being available in the warehouse.
- **FAIL** Q3088 [ORGANIC/CHATS/llm] (false_denial) Do you have access to MDs life group? Any top 5 tips for health and wellness
  - Substitutes marketing/business tips instead of actual health/wellness content that exists in the warehouse (92 FB, 192 WhatsApp items).
- **FAIL** Q3092 [ORGANIC/FACEBOOK/llm] (false_denial) What are some interesting AI workflows ecom operators are finding valuable?
  - Declined to answer despite ground truth having named member workflows available in warehouse.
- **FAIL** Q3094 [ORGANIC/PEOPLE/llm] (false_denial) Who are people in the Facebook group using for PPC
  - Flat denial despite existing threads from Dan Wills and Kayleigh Graham discussing PPC agencies.
- **FAIL** Q3109 [ORGANIC/FACEBOOK/llm] (wrong_fact) Josh Hadley shared a follow up flow asking for full rights if they sign up for program to get free giveaways etc. share more info on this
  - Attributes the flow to Eugene Khayman/Faizan, not Josh Hadley's own post, contradicting expected attribution.
- **FAIL** Q3118 [ORGANIC/SENSITIVE/llm] (fabrication) Are there any Christian members
  - Olivia asserts religion is tracked/found for a specific member, contradicting expected consistent refusal that religion isn't tracked.
- **FAIL** Q9027 [SMOKE/llm] (over_refusal) 3PL in Europe
  - Expected surfacing of UK/EU fulfillment partners with caveats, but Olivia gave a full non-answer instead.
- **FAIL** Q9034 [SMOKE/ticket_offer] (over_refusal) where do I update my card?
  - Should have shared the Stripe portal link but instead offered a ticket, withholding shareable info.
- **PARTIAL** Q3037 [ORGANIC/GENERAL/llm] (dodge) What are the top AI projects people are building?
  - Honest gap acknowledgment is acceptable, but offers no partial detail or examples that might exist in warehouse.
- **PARTIAL** Q3096 [ORGANIC/PEOPLE/llm] (dodge) Who has done a kickstarter campaign and got funded
  - Should have named Michael York's Zionix launch post instead of a vague hedge, though it avoided fabricating a funded campaign.
- **PARTIAL** Q3130 [ORGANIC/COUNTING/llm] (false_denial) what percentage of our members are agencies
  - Correctly notes data limitation but doesn't surface the ~13% Agency model figure that exists in warehouse.
- **PARTIAL** Q3116 [ORGANIC/EVENTS/ticket_offer] (dodge) Sign me up to the tiktok mastermind
  - Correctly declines to register but omits the real event name, date, and link that expected answer requires.
- **PARTIAL** Q3128 [ORGANIC/EVENTS/llm] (dodge) Who is going to Singapore summit — give me the whole list please
  - Delivers partial list but ends with a dodge/offer instead of continuing per expected two-turn delivery behavior.
- **PARTIAL** Q9002 [SMOKE/llm] (wrong_fact) how many members are in the supplements niche?
  - Off-by-one count (74 vs. expected 73) is a wrong numeric value.
- **PARTIAL** Q9033 [SMOKE/llm] (over_refusal) what's my membership status and billing?
  - Answer includes required info but explicitly says 'Stripe customer portal', violating the no raw Stripe word requirement.
