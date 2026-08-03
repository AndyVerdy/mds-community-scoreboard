# Olivia eval — 2026-08-03 — 169 judged · PASS 153 · PARTIAL 10 · FAIL 6 (3.6%)  [target <1%]

## Health by source
- 🟡 **ORGANIC/COUNTING**: 11 asked · 1 fail (9%) · 0 partial
- 🟡 **ORGANIC/CHATS**: 13 asked · 1 fail (8%) · 0 partial
- 🟡 **SMOKE**: 47 asked · 3 fail (6%) · 1 partial
- 🟡 **ORGANIC/PEOPLE**: 18 asked · 1 fail (6%) · 1 partial
- 🟢 **ORGANIC/GENERAL**: 13 asked · 0 fail (0%) · 3 partial
- 🟢 **ORGANIC/PARTNERS**: 12 asked · 0 fail (0%) · 2 partial
- 🟢 **ORGANIC/EVENTS**: 14 asked · 0 fail (0%) · 1 partial
- 🟢 **ORGANIC/SELF**: 13 asked · 0 fail (0%) · 2 partial
- 🟢 **ORGANIC/CAPABILITIES**: 7 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/FACEBOOK**: 9 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/SENSITIVE**: 10 asked · 0 fail (0%) · 0 partial
- 🟢 **SMOKE/REPORTS**: 2 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 169 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **wrong_fact** | 2 | 4 | 1.2% | #1 |
| **dodge** | 0 | 5 | 0.0% | #1 |
| **false_denial** | 3 | 1 | 1.8% | #1 #8 |
| **fabrication** | 1 | 0 | 0.6% | #1 |

- **FAIL** Q3094 [ORGANIC/PEOPLE/llm] (fabrication) Who are people in the Facebook group using for PPC
  - Omits Dan Wills' and Kayleigh Graham's specific threads and cites unverified named quotes not in the ground truth.
- **FAIL** Q3106 [ORGANIC/CHATS/llm] (false_denial) for amazon logistics - what can you tell me about peoples experience using AGL
  - Denies having verifiable data when ground truth shows member AGL experiences exist in threads.
- **FAIL** Q3107 [ORGANIC/COUNTING/llm] (wrong_fact) how much do people save on shiping with AGL>
  - Second post misattributed to Mo Kuhail when machine-verified author is Michael Patrón, a wrong attribution.
- **FAIL** Q9016 [SMOKE/llm] (false_denial) what are people talking about this week?
  - Expected a labelled roundup from FB and chats; Olivia gave a blanket refusal instead of any data.
- **FAIL** Q9024 [SMOKE/llm] (false_denial) is there a fulfillment conference happening in the city?
  - Ground truth indicates semantic search should surface a matching event, but Olivia denied finding anything.
- **FAIL** Q9032 [SMOKE/llm] (wrong_fact) how many members in MDS?
  - Gives 723 active members instead of verified 722, an off-by-one factual error.
- **PARTIAL** Q3010 [ORGANIC/GENERAL/llm] (wrong_fact) Can you pull me some info on price strikethroughs on TikTok Shop? I have a retail price below list, but am not seeing a strikethrough
  - Cites Amazon-focused posts as TikTok mechanics and misattributes Fred McKinnon's comment quote authorship, muddying grounding despite useful content.
- **PARTIAL** Q3048 [ORGANIC/PEOPLE/llm] (dodge) Who are our 717 members?
  - Corrects the count but never names any actual members despite question asking who they are.
- **PARTIAL** Q3059 [ORGANIC/EVENTS/llm] (dodge) Of the attendees, who has never been to a summit before ?
  - Asking which event is reasonable but expected answer requires grounded attendee data, not just a clarifying question.
- **PARTIAL** Q3065 [ORGANIC/PARTNERS/llm] (wrong_fact) tell me everything you know about avask
  - Mostly grounded but one citation misattributed (post authored by Victor Vintu, not Wei Lin as quoted).
- **PARTIAL** Q3068 [ORGANIC/SELF/llm] (wrong_fact) If my Amazon account just got flagged for review manipulation...Does anyone have a POA (plan of action) they can share to help me submit to Amazon
  - Attributes Lee Leathers' POA offer to wrong post and misattributes Dan Ri's thread to a different author than warehouse shows.
- **PARTIAL** Q3069 [ORGANIC/GENERAL/llm] (dodge) Give me our top five members
  - Reasonable clarification given ambiguity, but offers no concrete data at all, unlike expected grounded answer.
- **PARTIAL** Q3072 [ORGANIC/PARTNERS/llm] (dodge) Its a partner
  - Reasonable clarifying question given vague input, but no partner info actually delivered.
- **PARTIAL** Q3086 [ORGANIC/SELF/llm] (false_denial) What did I post in Facebook or WhatsApp ?
  - Provides some activity but hedges with no visible text and denies Facebook posts without confirming search completeness.
- **PARTIAL** Q3098 [ORGANIC/GENERAL/llm] (dodge) What's some great resources that I can share with new member so they get value immediately after joining?
  - Gives real resources (documents, brains, providers) but omits events calendar/video library and adds people-focused chat suggestion.
- **PARTIAL** Q9008 [SMOKE/llm] (wrong_fact) tell me about the Europe chapter
  - Member count (62 vs 61) and TTM revenue ($862M vs ~$742M) both off, though structure/leads/niches match direction.
