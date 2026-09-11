# Olivia eval — 2026-09-10 — 26 judged · PASS 22 · PARTIAL 1 · FAIL 3 (11.5%)  [target <1%]

## Health by source
- 🔴 **EVENT**: 4 asked · 2 fail (50%) · 0 partial
- 🟢 **AT_PROFILE**: 22 asked · 1 fail (5%) · 1 partial

## Failure classes — the per-class rates (denominator = 26 judged)
| class | fail | partial | rate | tickets |
|---|---|---|---|---|
| **false_denial** | 2 | 1 | 7.7% | #1 #8 |
| **wrong_fact** | 1 | 0 | 3.8% | #1 |

- **FAIL** Q2011 [AT_PROFILE/llm] (false_denial) What year did Adam Ackerman start his business?
  - Ground truth states 2015 but Olivia denied having any founding-year information.
- **FAIL** Q2023 [EVENT/llm] (false_denial) Where is the Billion Dollar Seller Summit Recommended Event taking place?
  - Denied finding the event despite ground truth confirming it exists and is in Kaua'i, Hawaii.
- **FAIL** Q2035 [EVENT/llm] (wrong_fact) What city is the MDS Summit being held in?
  - Olivia named Cancun 2027 instead of the expected upcoming Singapore 2026 Summit.
- **PARTIAL** Q2002 [AT_PROFILE/llm] (false_denial) Which chapters is Kyle Dilger affiliated with?
  - Correctly names Orange Co Chapter but misses his Chapter Leads affiliation, denying other chapter ties.
