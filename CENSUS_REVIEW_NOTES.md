> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# New Census (NK8EkZPd) — Andy's review punch-list

Status: **✅ APPLIED to NK8EkZPd (v2) 2026-07-08** — all comments handled except: tools (#5–9) kept, to flag Eugene in final report; ranking (#12) built as 11-per-section with a default 1–5 scale, exact format TBD by Andy. Form left **all-optional** for testing. Applied: brands→number, categories dropped, channels now conditional on "which other channels?" gate (routing verified forward), kids "Do you have kids?" gate + ages→brackets, "Do you attend…" wording, MDS Programs description, descriptions + scale labels carried from legacy, "what have you been up to" dropped.

| # | Question | Comment | Finding / recommendation | Status |
|---|---|---|---|---|
| 1 | Q7 "How many brands do you currently have?" | Should be a **number**, not a dropdown (App v3 uses number) | App v3 "How many brands do you manage?" = number. Agree → change dropdown → number. | pending |
| 2 | Q10 "Which categories apply to you?" (multi-select) + Q11 "What is your main niche?" (open text) | Asking categories then niche right after "feels too much — is it intentional?" | References don't use a category multi-select — App v3 & Summit use open-text "main niche"; Honorary uses open-text "core business" text. → Recommend **drop categories multi-select, keep main niche**. Andy's call. | pending |
| 3 | Channel % questions (Amazon/DTC/TikTok/Retail) | Revenue conditional formatting **doesn't match v3** — we ask DTC/TikTok/Retail % blindly ("who says I have DTC?") | v3 gates it: after Amazon %, ask **"What other channels do you sell on?"** (multi: DTC / TikTok Shop / Retail / Other), then show each channel's % **only if selected**. → Add that gate question + make DTC/TikTok/Retail % conditional. | pending |
| 4 | Q18 "Do you plan to sell a brand in the next 12 months?" | Check how it was asked in V3 | (to verify against V3 wording/options when applying) | pending |

| 5 | Q "What split testing tool do you use?" | **Flag — could be outdated** (tool list / whether still relevant to ask) | revisit relevance + option list | pending |

| 6 | Q25 "What PPC management service or software do you use?" | **Could be outdated — need to verify** (option list / relevance) | revisit relevance + option list | pending |

| 7 | Q "What reimbursement tool do you use?" | **Could be outdated — need to verify** (option list / relevance) | revisit relevance + option list | pending |

| 8 | Q "Which 3PL Management do you use?" | **Could be outdated — need to verify** (option list / relevance) | revisit relevance + option list | pending |

| 9 | Q "Which HR/Recruitment Services do you use?" | **Could be outdated — need to verify** (option list / relevance) | revisit relevance + option list | pending |

| 10 | Q "What would you say are your competitive advantages?" | We have this in v3 — **make sure it matches v3** (wording + options) | Built using App v3's exact option set (Brand & Story, Creative & Marketing, Product & Sourcing, Operations & Logistics, Customer Experience, Industry Relationships) — should already match; verify at apply. | pending |

| 11 | Q "What industries/business activities are you currently spending more than 20% of your time on?" | **Not sure about this question — flag to confirm** (keep / drop / rework) | awaiting Andy's decision | pending |

| 12 | Q36 "Rank the following member benefits" (ranking, 11 items) | Ranking is **very hard to answer, esp. on mobile** — make it intuitive | **Rec: replace ranking → "Which are your top 3 most valuable?" multi-select (max 3)** — one tap each, no drag. Optional follow-up "your #1?". Alts: rate each 1–5 (accurate, 11 taps) / most-vs-least pick-two. | pending |

| 13 | Q "Are you involved in a MDS Chapter?" | "Involved" is **ambiguous** — participating vs organizing? Intent (attending chapter events) unclear | Follow-ups are about *attending* events → reword to **"Do you attend MDS Chapter events?"** (or "Have you attended any MDS Chapter events?"). Same clarity fix likely applies to the Programs/Squad "involved?" gates. | pending |

| 14 | Q "Have you participated in any MDS Programs?" | **Unclear what "MDS Programs" are — needs a description** | Add a description listing examples (Masterminds, courses, cohorts, etc. — confirm exact list with Andy). | pending |

| 15 | Q "How many kids do you have?" | **Assumes you have kids** — gate it first | Add **"Do you have kids?" (yes/no)** → only if Yes show "how many" + ages. (Same don't-assume pattern as the DTC channel issue.) | pending |
| 16 | Q "What are their age ranges?" | **Format unclear** — "10-25? or 10,15,25?" | Replace open text with **multi-select age brackets** (e.g. 0–4 · 5–9 · 10–13 · 14–17 · 18+), check all that apply. | pending |

| 17 | Q "What have you been up to?" (last question) | **Unclear / "no clue where it came from"** | **Origin: legacy Standard census (was F1-Q48)** — carried over as the closer. Vague; nothing depends on it → **recommend DROP** (or reword to "Anything else you'd like to share with the MDS team?"). Andy's call. | pending → lean DROP |

| 18 | **ALL questions (global)** | **Missing descriptions/subtext** — legacy had helpful descriptions on questions; new form dropped them. "This is bad." | Pull each legacy question's description → map onto the matching new question; write fresh descriptions for reworded/new questions (channels, kids gate, etc.). | pending |

| 19 | **All opinion-scale questions (global)** | Missing **scale labels/markers** (legacy has left/center/right, e.g. "Not so great" / "Could be better" / "I LOVE IT!") | Set `properties.labels` (left/center/right) on every opinion_scale (UX, NPS, branding, chapter/program/squad ratings); carry legacy labels where present. | pending |

_(review complete — 19 comments)_

## Resolutions (2026-07-08)
- **#5–9 Tools** → **keep as-is in the form; FLAG in final report for Eugene** to confirm/refresh (lists may be dated).
- **#11 Industries >20%** → **keep** (legacy question).
- **#14 "MDS Programs" description** → use legacy definition: *"Programs include mastermind events, ecomlunches, and MDS extras."* (Legacy also has a Chapters description to carry.)
- **#12 Ranking** → RESOLVED: **keep all 11 benefits as 11 SEPARATE rating questions in ONE section** (no trim; photos were just brainstorm; exact scale/format TBD by Andy later). Default build = opinion_scale per benefit in a "Member Benefits" group.
- **#18/#19 descriptions + scale labels** → legacy text captured (revenue "enter 1MM like 1000000", # products "Parent SKUs only", scale labels "Not so great/Could be better/I LOVE IT!", etc.) → carry onto matching new questions.
- **Direct-apply batch** (staged, applies once ranking decided): brands→number · drop categories · drop "what have you been up to" · channel conditional gate · kids "Do you have kids?" gate · ages→brackets · "Do you attend…" wording · plan-to-sell v3 wording · descriptions + scale labels on all.
