> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Census Crosswalk — Legacy Standard Census → New Form

Full question-by-question crosswalk. **All AT fields live in:** Base **MDS Members DB** (`appou5JVr0WIrioWS`) → Table **Forms** (`tblblwPcgqhkPTVec`).
**% responded** = share of the 1,167 completed legacy submissions that answered that question. **A low % is NOT a quality signal** — conditional questions only apply to a subset, so they *should* read below 100%. **The census is annual: it re-asks everything to capture change year over year** — so a question is NOT dropped just because the application also asks it. (Question-level dedup only applies later, when merging Standard vs MDSonly.) Action key: **KEEP** · **REMAP** (same question, new AT target) · **REPLACE** (question reworked) · **NEW**.

| Legacy TF question | Legacy → AT field | New TF question | New → AT field | % responded | Note |
|---|---|---|---|---|---|
| What's your full name? | `Full Name` | Full name | `Full Name` | 100% | KEEP |
| What's your email? | `Email` | Email | `Email` | 100% | KEEP — now the member-match key (→ Preferred Email) |
| Strongest area of expertise | `Area of Expertise` | Strongest area of expertise | `Area of Expertise` | 100% | KEEP — can change year over year |
| What business models apply to you? | `Business Model` | Business models | `Business Model` | 100% | KEEP |
| Channel matrix — Amazon US | `Amazon US & % of Revenue` | Amazon % (number) | `(NEW) Amazon % (raw)` | 100% | REPLACE — grid→numeric %, running total (app-v3) |
| Channel matrix — Amazon EU | `Amazon EU & % of Revenue` | (folded into Amazon %) | `—` | 100% | DROP — folded into single Amazon % |
| Channel matrix — Amazon Canada | `Amazon Canada & % of Revenue` | (folded into Amazon %) | `—` | 100% | DROP — folded |
| Channel matrix — Other Amazon Mktpl | `Other Amazon Marketplaces & % of Revenue` | (folded into Amazon %) | `—` | 100% | DROP — folded |
| Channel matrix — Walmart.com | `Walmart.com & % of Revenue` | (folded into Retail %) | `(NEW) Retail % (raw)` | 100% | REPLACE — folded into Retail |
| Channel matrix — Own Website (DTC) | `Own Website & % of Revenue` | DTC / Shopify % (number) | `(NEW) DTC % (raw)` | 100% | REPLACE — grid→numeric % |
| Channel matrix — Wayfair/Overstock/Target | `Wayfair/Overstock/Target  & % of Revenue` | (folded into Retail %) | `(NEW) Retail % (raw)` | 100% | DROP/fold — 70%+ N/A |
| Channel matrix — Wholesale (Big Box) | `Wholesale (Big Box/Large Client)  & % of Revenue` | Retail / Wholesale % (number) | `(NEW) Retail % (raw)` | 100% | REPLACE — grid→numeric % |
| Channel matrix — Wholesale (Indie/Mom&Pop) | `Wholesale (Independent/Mom & Pop) & % of Revenue` | (folded into Retail %) | `—` | 100% | DROP — folded |
| (no legacy question) | `—` | TikTok % (number) | `(NEW) TikTok % (raw)` | — | NEW — TikTok channel (app-v3 parity) |
| (computed, no question) | `—` | (auto) | `(NEW) Other % (calc)` | — | 100 − sum of the four % |
| How many brands | `How many brands do you currently have?` | How many brands | `How many brands do you currently have?` | 100% | KEEP |
| Brand name(s) | `Brand Name(s)` | Brand name(s) | `Brand Name(s)` | 69% | KEEP |
| How many products | `# of Products` | How many products | `# of Products` | 100% | KEEP |
| Which categories apply | `Category` | Product categories | `Category` | 100% | KEEP |
| Purchased an e-com brand? | `(to confirm)` | Purchased an e-com brand? | `(to confirm)` | 100% | KEEP — can change year over year |
| Sold an e-com brand? | `(to confirm)` | Sold an e-com brand? | `(to confirm)` | 100% | KEEP — gates when/still-have |
| When did you sell? | `When did you sell your brand?` | When did you sell? | `When did you sell your brand?` | 31% | KEEP (gated by Sold?) |
| Still have e-com revenue? | `Do you still have any e-commerce revenue from new brands?` | Still have e-com revenue? | `Do you still have any e-commerce revenue from new brands?` | 26% | KEEP (gated by Sold?) |
| Projected FTM revenue | `Projected FTM Revnue` | Projected FTM revenue | `Projected FTM Revnue` | 79% | KEEP (AT name misspelled) |
| Total TTM revenue | `Total TTM Revenue` | TTM revenue | `(NEW) Unverified Revenue` | 80% | **REMAP ⭐ — feeds Most Recent Revenue** |
| Plan to sell a brand? | `Sell Brand? ` | Plan to sell a brand? | `Sell Brand? ` | 90% | KEEP |
| Main niche | `Main Niche` | Main niche | `Main Niche` | 100% | KEEP |
| Formal title | `Formal Title` | Formal title | `Formal Title` | 100% | KEEP — can change year over year |
| Day-to-day responsibilities | `Responsibilities in Company` | Day-to-day responsibilities | `Responsibilities in Company` | 100% | KEEP — can change year over year |
| Other knowledge bases/groups | `Knowledge bases` | Other knowledge bases/groups | `Knowledge bases` | 100% | KEEP — can change year over year |
| Industries >20% of time | `What industries/business activities are you currently spending more than 20% of your time on?` | Industries >20% of time | `What industries/business activities…20% of your time on?` | 65% | KEEP |
| Goals this year | `Goals` | Goals | `Goals` | 100% | KEEP |
| Biggest challenge | `Biggest Challenge` | Biggest challenge | `Biggest Challenge` | 67% | KEEP |
| Competitive advantage | `Competitive Advantage` | Competitive advantage | `Competitive Advantage` | 66% | KEEP — can change year over year |
| How you plan to grow | `Plans for next year` | How you plan to grow | `Plans for next year` | 67% | KEEP |
| Best thing that worked | `Worked Best For You` | Best thing that worked | `Worked Best For You` | 100% | KEEP |
| Most impactful service/software | `Service Provider Big Impact` | Most impactful service/software | `Service Provider Big Impact` | 100% | KEEP |
| Split-testing tool | `What split testing tool do you use use?` | Split-testing tool | `What split testing tool do you use use?` | 66% | KEEP (fix 'use use' typo in copy) |
| PPC management | `What PPC management service or software do you use?` | PPC management | `What PPC management service or software do you use?` | 66% | KEEP |
| Reimbursement tool | `What reimbursement tool do you use?` | Reimbursement tool | `What reimbursement tool do you use?` | 66% | KEEP |
| 3PL management | `Which 3PL Management do you use?` | 3PL management | `Which 3PL Management do you use?` | 66% | KEEP |
| HR/Recruitment (10 opts) | `Which HR/Recruitment Services do you use?` | HR/Recruitment (top 5 + Other) | `Which HR/Recruitment Services do you use?` | 62% | REPLACE — trim options |
| Rank member benefits | `(to confirm)` | Rank member benefits | `(to confirm)` | 100% | KEEP |
| Virtual-call topics | `Topics on Virtual Calls` | Virtual-call topics | `Topics on Virtual Calls` | 71% | KEEP |
| Does visual branding resonate? | `Brand Count` | Does visual branding resonate? | `Brand Count` | 86% | KEEP |
| Why chose branding / ideas | `We're curious to know why you chose your answer? …` | Why chose branding / ideas | `We're curious to know why you chose your answer? …` | 57% | KEEP — gated on the branding rating |
| How MDS impacted you | `How has MDS Impacted You? ` | How MDS impacted you | `How has MDS Impacted You? ` | 100% | KEEP |
| NPS — recommend MDS | `NPS Value` | NPS | `NPS Value` | 86% | KEEP |
| How can we make MDS better | `How can we make MDS better for you ` | How can we make MDS better | `How can we make MDS better for you ` | 86% | KEEP |
| Friends who'd qualify? | `Has friends to refer` | Friends who'd qualify? | `Has friends to refer` | 100% | KEEP (confirm field) |
| How many kids | `How many kids do you have?` | How many kids | `How many kids do you have?` | 81% | KEEP — add max validation to block troll values (999) |
| Kids age ranges | `What are their age ranges?` | Kids age ranges (gated: kids ≥ 1) | `What are their age ranges?` | 53% | KEEP — 53% = members who have kids; gated, not low |
| Involved in a Chapter? | `Involved in a MDS Chapter?` | Involved in a Chapter? | `Involved in a MDS Chapter?` | 86% | KEEP — gates rating |
| Rate Chapter events | `How would you rate MDS Chapters` | Rate Chapter events | `How would you rate MDS Chapters` | 47% | KEEP (gated) |
| See more at Chapters | `See more of at Chapter Events` | See more at Chapters | `See more of at Chapter Events` | 47% | KEEP (gated) |
| Participated in Programs? | `Have you participated in any MDS Programs?` | Participated in Programs? | `Have you participated in any MDS Programs?` | 12% | KEEP — gates rating |
| Rate program(s) | `How would you rate the program` | Rate program(s) | `How would you rate the program` | 4% | KEEP (gated) |
| See more with Programs | `What Would you like to see more of with programs?` | See more with Programs | `What Would you like to see more of with programs?` | 4% | KEEP (gated) |
| Involved in a Squad? | `Involved in a MDS Squad?` | Involved in a Squad? | `Involved in a MDS Squad?` | 61% | KEEP — gates rating |
| Rate Squads | `How would you rate MDS Squads` | Rate Squads | `How would you rate MDS Squads` | 10% | KEEP (gated) |
| See more at Squads | `See more of at MDS Squads` | See more at Squads | `See more of at MDS Squads` | 10% | KEEP (gated) |
| What have you been up to? | `(long_text)` | What have you been up to? | `(to confirm)` | 0%* | KEEP — *group header, sub-answers not counted (real rate ≠ 0) |
| Activities that describe you | `Do any Activities Describe You (Membership Requirements)` | Activities that describe you | `Do any Activities Describe You (Membership Requirements)` | 100% | KEEP — gates explain |
| Please explain further | `Explain Further` | Please explain further | `Explain Further` | 11% | KEEP (gated) |
| Rate UX of MDS systems | `Technology Score` | Rate UX of MDS systems | `Technology Score` | 66% | KEEP |
| Tech enhancement areas | `Technology Feedback` | Tech enhancement areas | `Technology Feedback` | 49% | KEEP |

## Tally
- **DROP = none.** The census is annual — it re-asks everything to track change. Question-level dedup is deferred to the **Standard-vs-MDSonly merge**.
- **KEEP** every legacy question · **REMAP** 1 (TTM → `(NEW) Unverified Revenue`) · **REPLACE** channel grid (9 fields → 4 numeric %) + HR option-trim · **NEW** 1 (TikTok %).
- **Fields still to confirm:** exact AT column for *Sold?*, *Purchased?*, *Rank member benefits*.
