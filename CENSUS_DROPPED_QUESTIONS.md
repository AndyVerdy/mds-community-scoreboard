> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Census — Dropped Questions Log (with reasoning)

Consolidated record of every question we're removing from the merged census, and why. Row-level matrix trims (kept question, fewer rows) are listed separately at the bottom.

## From the Standard Annual Census (applied in the v2 form)
| Question | Response % | Reason for dropping |
|---|---|---|
| Which categories apply to you? (multi-select, 10) | 100% | Redundant with "What is your main niche?". None of the newer forms (App v3, Honorary, Summit) use a category multi-select — they use open-text niche. Kept niche, dropped categories. |
| What have you been up to? | 0%* | Vague catch-all, unclear purpose; nothing downstream reads it. (*legacy group header — real rate ≠ 0, but the question earns its cut on clarity.) |
| Channel: Wayfair/Overstock/Target | 84% N/A | Part of channel simplification — 84% of members never sell there. Folded away when the channel grid became numeric % (Amazon/DTC/TikTok/Retail). |

## From the MDSonly Census (proposed for the merge)
| # | Question | Response % | Reason for dropping |
|---|---|---|---|
| Q23 | Are there any other essential positions not listed? | 98% | Answers are mostly "No"/"N/A" — the phrasing invites a yes/no, not an actual role. Noise, not data. |
| Q29 | What will be your new business venture? | 21% | Low fill, not actionable at the aggregate level. |
| Q30 | What are you currently investing in? | 21% | Low fill, not actionable; sensitive without clear use. |

### Matrix drops — DEFERRED (kept as-is in Combined v1)
Andy: "keep the matrices as is for now." So **Q27 (Business change YoY, 20%)** and **Q28 (Revenue % by category, 20%)** are **NOT dropped** — all 7 matrices are kept as-is in the combined form. Revisit these two (drop or trim) in a later pass.

## Deduped in the merge (not dropped — merged to one instance)
| Question | Kept from | Reason |
|---|---|---|
| Full name / Email | Standard | Identity — one instance in the merged form. |
| How can MDS be better? | Standard (86%) vs MDSonly (21%) | Same question; keep the higher-response, better-worded Standard version. |

## Matrix row-trims (question KEPT, low-signal rows removed)
| Matrix | Trim |
|---|---|
| Marketing initiatives (Q5) | drop **TV**, **Podcast/Radio** rows (dead for e-com) → 8 → 6 |
| Selling focus (Q17) | drop **Amazon Asia/Oceania**, **Amazon Middle East**, **Target.com**, **Etsy.com** → 11 → ~6 |
| Manufacturing locations (Q8) | trim to **China, USA, India, Vietnam, Mexico + Other** → 9 → 6 |
| Team positions & pay (Q22) | trim to ~7 core roles; ⚠️ confirm MDS still wants **salary data** annually |

## Open judgment calls (not decided)
- **Q8 Manufacturing** — keep as trimmed matrix vs. de-matrix into "where do you manufacture?" + %.
- **Q22 Team pay** — collect salary data at all? (sensitive)
