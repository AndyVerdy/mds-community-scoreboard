# MDS Census Forms Comparison

## Form 1: "Standard - Annual Census" (I409BFlj) — 50 questions
## Form 2: "MDSonly - Annual Census Master" (DXs5mhZn) — 32 questions
## Form 3: "Annual Census Master" (vLMf7fSS) — 49 questions

---

# CATEGORY-BY-CATEGORY COMPARISON

## 1. BASIC IDENTITY
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Full name | Q1 short_text R | Q1 short_text R | Q1 short_text R | YES - identical |
| Email | Q2 email R | Q2 email R | Q2 email R | YES - identical |
| Gsuite email (doc access) | — | Q32 email | Q48 email | YES - merge |
| Formal title | Q18 short_text R | — | Q34 short_text R | YES |
| Day-to-day responsibilities | Q19 long_text R | — | Q35 long_text R | YES |
| Education level | — | — | Q3 dropdown R | UNIQUE to F3 |

## 2. BUSINESS MODEL & INVOLVEMENT
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Business models | Q4 MC multi R (PL, Wholesale, Brand Mgmt, OEM) | — | Q8 MC multi R (Arb/Wholesale, PL, Brand Mgmt, OEM) | YES - merge options |
| Current e-commerce involvement | — | Q3 MC R (7 options re: sold/operate) | — | UNIQUE to F2 |
| Main niche | Q17 short_text R | — | Q15 short_text R | YES - identical concept |
| Strongest expertise | Q3 short_text R | — | Q6 short_text R | YES - similar |
| Prior work before Amazon | — | — | Q5 short_text R | UNIQUE to F3 |
| Validation of membership | — | — | Q4 group (teacher/coach/vendor check) | UNIQUE to F3 |

## 3. BRANDS & PRODUCTS
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Number of brands | Q6 dropdown R (0-5+) | — | Q7 dropdown R (0-5+) | YES - identical |
| Brand name(s) | Q7 short_text | — | — | YES |
| Number of products | Q8 number R (max 99999) | — | Q11 number R + Q12 number R | YES - merge |
| Product categories | Q9 MC multi R (10 cats) | — | Q14 MC multi R (same cats) | YES - nearly identical |
| Products launched last year | — | Q15 number | Q32 number | YES - merge |
| New products planned this year | — | Q16 number | Q33 number | YES - merge |
| When started selling on Amazon | — | — | Q13 dropdown R (2012-2021) | UNIQUE to F3 |

## 4. REVENUE & FINANCIALS
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| TTM revenue | Q15 number R (min 1M) | — | Q25 number R | YES |
| Projected FTM revenue | Q14 number R (min 1M) | — | Q28 number R | YES |
| % revenue off Amazon | — | — | Q10 number R + Q26 dropdown | YES - merge |
| Avg cost per CBM | — | Q10 number | — | UNIQUE to F2 |
| Avg production time | — | Q11 number | — | UNIQUE to F2 |
| Avg shipping time | — | Q12 number | — | UNIQUE to F2 |
| Customer orders shipped | — | Q13 number | Q27 number | YES - merge |
| Containers imported | — | Q14 number | Q31 number | YES - merge |
| Revenue % by business category | — | Q28 matrix | — | UNIQUE to F2 |

## 5. SALES CHANNELS
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Channels + revenue % | Q5 matrix R (9 rows) | — | — | YES |
| Where sell besides Amazon | — | — | Q9 MC multi R | Overlaps with Q5 F1 |
| Selling focus next 12 months | — | Q17 matrix (10 channels) | — | UNIQUE to F2 |

## 6. BOUGHT/SOLD BUSINESS
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Purchased a business before | Q10 yes_no R | — | Q44 yes_no R | YES |
| Sold a business before | Q11 yes_no R | — | Q45 yes_no R | YES |
| When sold | Q12 short_text R | — | — | YES |
| Still have e-com revenue | Q13 MC R | — | — | YES |
| Plan to sell in 12 months | Q16 MC R (5 options) | — | — | YES |

## 7. OPERATIONS & TEAM
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Warehousing types | — | Q4 MC multi R (FBA, 3PL, In-House) | Q16 MC multi R (FBA, 3PL, SFP, In-House) | YES - merge options |
| Product sourcing | — | Q7 MC R | Q29 MC R | YES - merge |
| Manufacturing locations | — | Q8 matrix | Q30 number | YES - merge |
| W-2 employees count | — | Q18 number | Q36 number R | YES |
| Part-time/1099 count | — | Q19 number | — | YES |
| VA/offshore employees | — | Q20 number | Q37 number R | YES |
| Staff locations | — | Q21 MC multi (10 locations) | Q42 MC multi R (6 locations) | YES - merge |
| Team positions + pay | — | Q22 matrix | Q40 MC multi | YES - merge |
| Other team positions | — | Q23 short_text | Q41 short_text | YES |
| Team building advice | — | Q24 long_text | — | UNIQUE to F2 |
| EOS/Traction usage | — | Q25 MC (Yes/No) | Q38 MC | YES |
| EOS implementation | — | Q26 MC | Q39 MC | YES |

## 8. MARKETING & OPERATIONS MANAGEMENT
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Marketing initiatives handling | — | Q5 matrix (8 channels) | — | UNIQUE to F2 |
| Business aspects handling | — | Q6 matrix (8 areas) | — | UNIQUE to F2 |
| Amazon PPC management | — | — | Q17 MC R | UNIQUE to F3 |
| External paid traffic mgmt | — | — | Q18 MC R | UNIQUE to F3 |
| Product launches mgmt | — | — | Q19 MC R | UNIQUE to F3 |
| Account admin mgmt | — | — | Q20 MC R | UNIQUE to F3 |
| Social media/PR mgmt | — | — | Q21 MC R | UNIQUE to F3 |
| Listing creation mgmt | — | — | Q22 MC R | UNIQUE to F3 |
| Photography mgmt | — | — | Q23 MC R | UNIQUE to F3 |
| Web design/dev mgmt | — | — | Q24 MC R | UNIQUE to F3 |
| (Note: F2 Q5+Q6 cover similar ground as F3 Q17-Q24 but as matrices vs individual questions) |

## 9. TOOLS & SERVICES
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Split testing tool | Q28 MC multi R + Other | — | — | YES |
| PPC management service | Q29 MC multi R + Other | — | — | YES |
| Reimbursement tool | Q30 MC multi R + Other | — | — | YES |
| 3PL management | Q31 MC R + Other | — | — | YES |
| HR/Recruitment services | Q32 MC multi R + Other | — | — | YES |

## 10. GROWTH & STRATEGY
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| How plan to grow business | Q25 long_text R | — | — | YES |
| Best thing worked in 12 months | Q26 long_text R | — | — | YES |
| Most impactful service/software | Q27 short_text R | — | — | YES |
| Competitive advantage | Q24 MC multi R + Other | — | — | YES |
| Goals for this year | Q22 long_text R | — | Q46 long_text R | YES |
| Biggest challenge | Q23 long_text R | — | — | YES |
| Business change YoY | — | Q27 matrix | — | UNIQUE to F2 |
| New business venture | — | Q29 long_text | — | UNIQUE to F2 |
| Current investments | — | Q30 long_text | — | UNIQUE to F2 |
| Industries spending 20%+ time | Q21 MC multi R + Other (10 options) | — | — | YES |

## 11. OTHER GROUPS & KNOWLEDGE BASES
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Other groups/communities | Q20 short_text R | — | Q43 short_text R | YES |

## 12. MDS FEEDBACK & NPS
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| Rank member benefits | Q33 ranking R (11 items) | — | — | YES |
| Virtual call topics | Q34 short_text R | — | — | YES |
| Visual branding resonance | Q35 opinion_scale R | — | — | YES |
| Branding improvement ideas | Q36 long_text | — | — | YES |
| MDS community impact | Q37 long_text R | — | — | YES |
| NPS - recommend to friend | Q38 opinion_scale R | — | — | YES |
| How make MDS better | Q39 long_text R | — | Q31 long_text | YES |
| Invite friends to MDS | Q40 yes_no R | — | Q47 yes_no R | YES |
| UX rating of MDS systems | Q49 opinion_scale R | — | — | YES |
| Tech enhancement areas | Q50 long_text R | — | — | YES |

## 13. PERSONAL / FAMILY
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| How many kids | Q41 number R | — | — | YES |
| Kids age ranges | Q42 short_text | — | — | YES |

## 14. MDS PROGRAMS & CHAPTERS
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| MDS Chapters group | Q43 group (3 sub-Qs) | — | — | YES |
| - Involved in chapter? | sub MC R (Yes/No) | — | — | |
| - Rate chapter events | sub opinion_scale R | — | — | |
| - What see more at chapters | sub long_text R | — | — | |
| MDS Programs group | Q44 group (3 sub-Qs) | — | — | YES |
| - Participated in programs? | sub MC R (Yes/No) | — | — | |
| - Rate programs | sub opinion_scale R | — | — | |
| - What see more at programs | sub long_text R | — | — | |
| MDS Squads | Q45 MC R (Yes/No) | — | — | YES |
| Rate Squads program | Q46 opinion_scale R | — | — | |
| What see more at Squads | Q47 long_text R | — | — | |
| What have you been up to | Q48 long_text R | — | — | YES |

## 15. LEGAL / NDA
| Topic | Form 1 | Form 2 | Form 3 | Merged? |
|-------|--------|--------|--------|---------|
| NDA/Privacy/Terms agreement | — | — | Q49 group (confirm + date) | UNIQUE to F3 |

---

# SUMMARY STATISTICS

| | Form 1 | Form 2 | Form 3 |
|---|--------|--------|--------|
| Total questions | 50 | 32 | 49 |
| Focus | Comprehensive: business + MDS feedback + programs | Deep-dive: operations, financials, team, channels | Application-style: business basics + ops management |
| Unique questions | ~20 (MDS feedback, programs, tools, personal) | ~8 (supply chain costs, production times, biz categories spend) | ~8 (education, validation, pre-Amazon career, management per-function) |
| Overlapping topics | ~30 topics shared with at least 1 other form | ~24 topics shared | ~30 topics shared |

---

# PROPOSED MDS CENSUS 2026 MERGED STRUCTURE

## Section 1: Identity & Background (5 Qs)
1. Full name (short_text, R)
2. Email (email, R)
3. Formal title in organization (short_text, R) — F1-Q18, F3-Q34
4. Highest level of education (dropdown, R) — F3-Q3
5. What did you do before e-commerce? (short_text) — F3-Q5

## Section 2: Business Overview (10 Qs)
6. Current e-commerce involvement (MC, R) — F2-Q3 (own/sold/consulting etc.)
7. Business models that apply (MC multi, R) — merged F1-Q4 + F3-Q8
8. Number of brands (dropdown, R) — F1-Q6
9. Brand name(s) (short_text) — F1-Q7
10. Number of products - parent SKUs (number, R) — F1-Q8
11. Product categories (MC multi, R) — F1-Q9 / F3-Q14
12. Main niche (short_text, R) — F1-Q17
13. Strongest area of expertise (short_text, R) — F1-Q3
14. When did you start selling on Amazon? (dropdown, R) — F3-Q13 (update years to 2012-2025)
15. Competitive advantage (MC multi + Other, R) — F1-Q24

## Section 3: Revenue & Financials (5 Qs)
16. TTM (trailing 12 months) total revenue (number, R, min 1M) — F1-Q15
17. % of revenue from off Amazon (number) — F3-Q10
18. Projected FTM (future 12 months) revenue (number, R, min 1M) — F1-Q14
19. Sales channels + revenue % (matrix, R) — F1-Q5 (updated rows)
20. How are you focusing selling efforts next 12 months? (matrix) — F2-Q17

## Section 4: Sourcing & Supply Chain (6 Qs)
21. How do you source products? (MC, R) — F2-Q7 / F3-Q29
22. Where do you manufacture? (matrix) — F2-Q8
23. Containers imported per year (number) — F2-Q14 / F3-Q31
24. Warehousing types (MC multi, R) — merged F2-Q4 + F3-Q16
25. Products launched last year (number) — F2-Q15 / F3-Q32
26. New products planned this year (number) — F2-Q16 / F3-Q33

## Section 5: Team & Operations (8 Qs)
27. W-2 employees count (number, R) — F2-Q18 / F3-Q36
28. Part-time/1099 contractors (number) — F2-Q19
29. VA/offshore employees (number, R) — F2-Q20 / F3-Q37
30. Staff locations (MC multi, R) — merged F2-Q21 + F3-Q42
31. Team positions (MC multi + Other) — F2-Q22 / F3-Q40
32. Day-to-day responsibilities (long_text, R) — F1-Q19
33. Use EOS/Traction? (MC, R) — F2-Q25 / F3-Q38
34. How implemented EOS? (MC) — F2-Q26 / F3-Q39

## Section 6: Marketing & Management (2 Qs)
35. How do you handle marketing initiatives? (matrix) — F2-Q5 (covers Amazon Ads, FB/IG, Google, SMS/Email, etc.)
36. How do you handle business operations? (matrix) — F2-Q6 (covers product dev, launches, CS, design, etc.)

## Section 7: Tools & Services (5 Qs)
37. Split testing tool (MC multi + Other) — F1-Q28
38. PPC management service/software (MC multi + Other) — F1-Q29
39. Reimbursement tool (MC multi + Other) — F1-Q30
40. 3PL management (MC + Other) — F1-Q31
41. HR/Recruitment services (MC multi + Other) — F1-Q32

## Section 8: Growth & Strategy (6 Qs)
42. Goals for this year (long_text, R) — F1-Q22 / F3-Q46
43. Biggest challenge this year (long_text, R) — F1-Q23
44. How plan to grow in next 12 months (long_text, R) — F1-Q25
45. Best thing that worked in last 12 months (long_text, R) — F1-Q26
46. Most impactful service/software (short_text, R) — F1-Q27
47. Industries spending 20%+ time on (MC multi + Other, R) — F1-Q21

## Section 9: Acquisitions (5 Qs)
48. Purchased an e-commerce business before? (yes_no, R) — F1-Q10
49. Sold an e-commerce business before? (yes_no, R) — F1-Q11
50. When did you sell? (short_text) — F1-Q12 (conditional)
51. Still have e-commerce revenue from new brands? (MC, R) — F1-Q13 (conditional)
52. Plan to sell a brand in next 12 months? (MC, R) — F1-Q16

## Section 10: Community & Groups (2 Qs)
53. Other knowledge bases/groups you're part of (short_text, R) — F1-Q20 / F3-Q43
54. What have you been up to? (long_text, R) — F1-Q48

## Section 11: MDS Feedback (10 Qs)
55. Rank member benefits (ranking, R) — F1-Q33
56. Virtual call topics you'd like more of (short_text, R) — F1-Q34
57. Does MDS visual branding resonate? (opinion_scale, R) — F1-Q35
58. Branding improvement ideas (long_text) — F1-Q36
59. How has MDS most impacted you in last 12 months? (long_text, R) — F1-Q37
60. NPS: How likely to recommend MDS? (opinion_scale, R) — F1-Q38
61. How can MDS be better for you? (long_text, R) — F1-Q39 / F2-Q31
62. Rate UX of MDS systems (opinion_scale, R) — F1-Q49
63. Tech enhancement areas (long_text, R) — F1-Q50
64. Know friends who'd qualify for MDS? (yes_no, R) — F1-Q40 / F3-Q47

## Section 12: MDS Programs (Group - 9 sub-Qs)
65. MDS Chapters group — F1-Q43
    - Involved in a chapter? (MC)
    - Rate chapter events (opinion_scale)
    - What to see more at chapters (long_text)
66. MDS Programs group — F1-Q44
    - Participated in programs? (MC)
    - Rate programs (opinion_scale)
    - What to see more at programs (long_text)
67. MDS Squads — F1-Q45-Q47
    - Involved in a squad? (MC)
    - Rate Squads program (opinion_scale)
    - What to see more at Squads (long_text)

## Section 13: Personal (2 Qs)
68. How many kids do you have? (number, R) — F1-Q41
69. Kids age ranges (short_text) — F1-Q42

## Section 14: Access & Legal (2 Qs)
70. Gsuite email for document access (email) — F2-Q32 / F3-Q48
71. NDA/Privacy/Terms agreement (group: confirm + date) — F3-Q49

## TOTAL: ~71 questions (including sub-questions in groups)

---

# KEY DECISIONS FOR MERGED FORM

1. **F2-Q5 matrix vs F3-Q17-Q24 individual questions**: F2's matrix approach is more compact (8 marketing channels in 1 matrix vs 8 separate questions in F3). Recommend keeping the matrix format.

2. **Revenue questions**: F1 asks for TTM and FTM with min $1M validation. Keep this. Add F3's "% off Amazon" question.

3. **Channel matrix**: F1-Q5 has revenue % per channel. F2-Q17 has selling focus/strategy per channel. Both are valuable — keep both.

4. **Team questions**: F2 is more detailed (W-2/1099/VA counts + locations + positions + pay). F3 asks individual management questions per function. Recommend F2's matrix approach.

5. **Education + Validation**: These are F3-only and serve application/screening purposes. Include if census doubles as re-qualification.

6. **Start year on Amazon**: F3-only, useful demographic data. Update dropdown to include 2022-2025.

7. **Supply chain costs (CBM, production time, shipping time)**: F2-only. Consider if still relevant for 2026.
