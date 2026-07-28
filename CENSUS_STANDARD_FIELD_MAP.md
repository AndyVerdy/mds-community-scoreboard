> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Standard Annual Census — Field Sync Map (verified 2026-07-08)

**Source form:** Typeform `I409BFlj` "Standard - Annual Census" (also serves lapsed-standard-access re-qualification).

**Destination — ALL rows land here:** Base **MDS Members DB** (`appou5JVr0WIrioWS`) → Table **Forms** (`tblblwPcgqhkPTVec`).
Note: **not** the Members table. The Members table shows census data via *lookups* on the linked Forms row.

**Sync mechanism today:** Typeform's **native Airtable integration** (runs under Eugene's account). There is **no Make/n8n scenario** — the mapping lives inside Typeform's Connect panel (UI-only). This map was reverse-engineered and cross-verified against **3 live June-2026 submissions**.

**Change required for the NEW form:** revenue must write **`(NEW) Unverified Revenue`** and stamp `Form ID` + `Date Submitted` + link to Member — **not** `Total TTM Revenue`.

| # | Census question | Type | → Forms field |
|---|---|---|---|
| 1 | What's your full name? | short_text | `Full Name` |
| 2 | What's your email? | email | `Email` |
| 3 | Strongest area of expertise | short_text | `Area of Expertise` |
| 4 | What business models apply to you? | multi | `Business Model` |
| 5 | Channel matrix — Amazon US | matrix row | `Amazon US & % of Revenue` |
| 6 | Channel matrix — Amazon Canada | matrix row | `Amazon Canada & % of Revenue` |
| 7 | Channel matrix — Other Amazon Marketplaces | matrix row | `Other Amazon Marketplaces & % of Revenue` |
| 8 | Channel matrix — Walmart.com | matrix row | `Walmart.com & % of Revenue` |
| 9 | Channel matrix — Own Website (Shopify/Other) | matrix row | `Own Website & % of Revenue` |
| 10 | Channel matrix — Wayfair/Overstock/Target | matrix row | `Wayfair/Overstock/Target  & % of Revenue` |
| 11 | Channel matrix — Wholesale (Big Box) | matrix row | `Wholesale (Big Box/Large Client)  & % of Revenue` |
| 12 | Channel matrix — Wholesale (Indie/Mom&Pop) | matrix row | `Wholesale (Independent/Mom & Pop) & % of Revenue` |
| 13 | Channel matrix — Amazon EU | matrix row | `Amazon EU & % of Revenue` |
| 14 | How many brands do you currently have? | dropdown | `How many brands do you currently have?` |
| 15 | How many products do you have? | number | `# of Products` |
| 16 | Which categories apply to you? | multi | `Category` |
| 17 | Have you *purchased* an e-com brand/business? | yes_no | ⚠️ to confirm (boolean) |
| 18 | Have you *sold* an e-com brand/business? | yes_no | ⚠️ to confirm (boolean) |
| 19 | Projected FTM (future 12mo) revenue | number | `Projected FTM Revnue` *(misspelled in AT)* |
| 20 | **Total TTM (trailing 12mo) revenue** | number | **`Total TTM Revenue`** ⚠️ OLD field → new form writes `(NEW) Unverified Revenue` |
| 21 | Plan to sell a brand in next 12 months? | multi | `Sell Brand? ` |
| 22 | What is your main niche? | short_text | `Main Niche` |
| 23 | Formal title in organization | short_text | `Formal Title` |
| 24 | Day-to-day responsibilities | long_text | `Responsibilities in Company` |
| 25 | Other knowledge bases/groups you're part of | short_text | `Knowledge bases` |
| 26 | Industries you spend >20% of time on | multi | `What industries/business activities…20% of your time on?` |
| 27 | Goals for this year | long_text | `Goals` |
| 28 | Biggest challenge this year | long_text | `Biggest Challenge` |
| 29 | Competitive advantage | multi | `Competitive Advantage` |
| 30 | How you plan to grow in coming 12 months | long_text | `Plans for next year` |
| 31 | One thing that worked best last 12 months | long_text | `Worked Best For You` |
| 32 | Service/software with most impact | short_text | `Service Provider Big Impact` |
| 33 | Split testing tool | multi | `What split testing tool do you use use?` |
| 34 | PPC management service/software | multi | `What PPC management service or software do you use?` |
| 35 | Reimbursement tool | multi | `What reimbursement tool do you use?` |
| 36 | 3PL management | multi | `Which 3PL Management do you use?` |
| 37 | HR/Recruitment services | multi | `Which HR/Recruitment Services do you use?` |
| 38 | Rank member benefits | ranking | ⚠️ to confirm (ranking) |
| 39 | Virtual-call topics wanted | short_text | `Topics on Virtual Calls` |
| 40 | Does our visual branding resonate? | opinion_scale | `Brand Count` *(rating store; confirm)* |
| 41 | How MDS most impacted you (12mo) | long_text | `How has MDS Impacted You? ` |
| 42 | NPS — likely to recommend MDS | opinion_scale | `NPS Value` |
| 43 | How can we make MDS better for you? | long_text | `How can we make MDS better for you ` |
| 44 | Friends who'd qualify for MDS? | yes_no | `Has friends to refer` *(confirm)* |
| 45 | How many kids do you have? | number | `How many kids do you have?` |
| 46 | Their age ranges | short_text | `What are their age ranges?` |
| 47 | Involved in a MDS Chapter? | multi | `Involved in a MDS Chapter?` |
| 48 | Rate the Chapter events | opinion_scale | `How would you rate MDS Chapters` |
| 49 | See more at Chapter events | long_text | `See more of at Chapter Events` |
| 50 | Involved in a MDS Squad? | multi | `Involved in a MDS Squad?` |
| 51 | Rate the Squads program | opinion_scale | `How would you rate MDS Squads` |
| 52 | See more at Squads | long_text | `See more of at MDS Squads` |
| 53 | Activities that describe you | multi | `Do any Activities Describe You (Membership Requirements)` |
| 54 | Please explain further | long_text | `Explain Further` |
| 55 | Rate UX of MDS systems | opinion_scale | `Technology Score` |
| 56 | Brand name(s) | short_text | `Brand Name(s)` |
| 57 | Why you chose branding answer / improvement ideas | long_text | `We're curious to know why you chose your answer? …` |
| 58 | Participated in any MDS Programs? | multi | `Have you participated in any MDS Programs?` |
| 59 | Rate the program(s) | opinion_scale | `How would you rate the program` |
| 60 | See more with Programs | long_text | `What Would you like to see more of with programs?` |
| 61 | Tech enhancement areas | long_text | `Technology Feedback` |
| 62 | When did you sell your brand/business? | short_text | `When did you sell your brand?` *(conditional)* |
| 63 | Still have e-com revenue from new brands? | multi | `Do you still have any e-commerce revenue from new brands?` |

**Coverage:** 59/63 verified against live data; 4 to confirm (3 yes/no booleans + the ranking question — none revenue-critical). Channel matrix = 1 Typeform question → 9 Forms fields, so 63 questions → ~71 Forms columns.
