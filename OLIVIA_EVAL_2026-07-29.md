# Olivia eval — 2026-07-29 — 84 judged · PASS 77 · PARTIAL 2 · FAIL 5 (6.0%)  [target <1%]

## Health by source
- 🔴 **ORGANIC/FACEBOOK**: 7 asked · 2 fail (29%) · 1 partial
- 🔴 **ORGANIC/EVENTS**: 9 asked · 1 fail (11%) · 1 partial
- 🔴 **ORGANIC/PARTNERS**: 10 asked · 1 fail (10%) · 0 partial
- 🔴 **ORGANIC/COUNTING**: 10 asked · 1 fail (10%) · 0 partial
- 🟢 **ORGANIC/GENERAL**: 10 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/CHATS**: 10 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/PEOPLE**: 10 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/SELF**: 9 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/CAPABILITIES**: 5 asked · 0 fail (0%) · 0 partial
- 🟢 **ORGANIC/SENSITIVE**: 4 asked · 0 fail (0%) · 0 partial

## Failure classes — the per-class rates (denominator = 84 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **dodge** | 2 | 1 | 2.4% | #1 |
| **fabrication** | 1 | 1 | 1.2% | #1 |
| **no_answer** | 2 | 0 | 2.4% | infra |

- **FAIL** Q3004 [ORGANIC/PARTNERS/llm] (dodge) what are some services that might be good for my business
  - Should have used asker's own profile to narrow answer, but Olivia asked back instead of using known persona data.
- **FAIL** Q3042 [ORGANIC/EVENTS/llm] (fabrication) Recommend some calls for me to attend
  - Invented specific weekly call, host, and in-person events instead of admitting the live calls calendar isn't available yet.
- **FAIL** Q3053 [ORGANIC/FACEBOOK/llm] (no_answer) Share the best TikTok videos to watch for launch? There was a recent post in Facebook
  - Olivia produced no answer at all despite an expected real, grounded response.
- **FAIL** Q3061 [ORGANIC/FACEBOOK/ticket_offer] (dodge) Share link to Brandon’s post
  - Olivia refused and offered a ticket instead of retrieving or sharing Brandon's post link.
- **FAIL** Q3073 [ORGANIC/COUNTING/llm] (no_answer) Who has had their TikTok account reinstated
  - No answer was produced at all, failing to address the question.
- **PARTIAL** Q3044 [ORGANIC/FACEBOOK/llm] (dodge) Please post all members in the pet space
  - Admits it can't produce the requested list and offers to search instead, but never delivers the actual members list.
- **PARTIAL** Q3067 [ORGANIC/EVENTS/llm] (fabrication) I met someone in the Milan summit who sells travel accessories but I can't remember his name.
  - Gives plausible named leads but doesn't verify either attended the Milan summit specifically.
