> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# New MDS Census — Form Design + Logic Jumps (v0.2)

Standard-census content, cleaned. **The census is annual — it keeps every question** (re-captures what changes year over year); nothing dropped for "the application already asks it." Only changes = revenue **REMAP**, channel matrix → **numeric % (app-v3 style)**, HR **option-trim**, copy fixes.

**Forward-only jumps** (a backward jump ends the form in Typeform). Each question shows its **→ Airtable Forms field** (per `CENSUS_STANDARD_FIELD_MAP.md`), so this doubles as the sync map.
Legend: **R** = required · *(cond)* = shown only via a jump · ⭐ = changed vs today.

## S1 · Identity & role
- **Q1 Full name** (short_text, R) → `Full Name`
- **Q2 Email** (email, R) → `Email` — the member-match key (→ AT Preferred Email); hidden `member_id`/`email` from the link may prefill but is not relied on.
- **Q3 Formal title** (short_text) → `Formal Title`
- **Q4 Day-to-day responsibilities** (long_text) → `Responsibilities in Company`

## S2 · Business snapshot
- **Q5 Business models** (multi, R) → `Business Model`
- **Q6 Strongest area of expertise** (short_text) → `Area of Expertise`
- **Q7 How many brands** (dropdown, R) → `How many brands do you currently have?`
- **Q8 Brand name(s)** (short_text) → `Brand Name(s)`
- **Q9 How many products** (number, R) → `# of Products`
- **Q10 Product categories** (multi, R) → `Category`
- **Q11 Main niche** (short_text, R) → `Main Niche`

## S3 · Revenue
- **Q12 TTM (trailing 12mo) revenue** (number, R) → ⭐ **`(NEW) Unverified Revenue`** *(was `Total TTM Revenue`)*
- **Q13 Projected FTM (next 12mo) revenue** (number) → `Projected FTM Revnue`
- **Channel % — numeric with running total** ⭐ *(replaces the grid — app-v3 mechanism)*. Each `number` 0–100; TF var **`pct_total`** sums via `add`; follow-up descriptions recall **`{{var:pct_total}}`** → *"So far you've allocated X%."*
  - **Q14 Amazon %** → `(NEW) Amazon % (raw)`
  - **Q15 DTC / Shopify %** → `(NEW) DTC % (raw)`
  - **Q16 TikTok %** → `(NEW) TikTok % (raw)`
  - **Q17 Retail / Wholesale %** → `(NEW) Retail % (raw)`
  - *(auto)* `(NEW) Other % (calc)` = `100 − SUM(above)` — no question
- **Q18 Plan to sell a brand next 12mo?** (multi, R) → `Sell Brand? `
- **Q19 Purchased an e-com brand?** (yes_no) → *(sold/purchased field — to confirm)*
- **Q20 Sold an e-com brand before?** (yes_no) → *(to confirm)*
  - **JUMP:** Yes → Q21 · No → **Q23**
- **Q21 When did you sell?** *(cond)* (short_text) → `When did you sell your brand?`
- **Q22 Still have e-com revenue from new brands?** *(cond)* (multi) → `Do you still have any e-commerce revenue from new brands?`

## S4 · Tools
- **Q23 Split-testing tool** (multi) → `What split testing tool do you use use?` *(fix "use use" typo in copy)*
- **Q24 PPC management** (multi) → `What PPC management service or software do you use?`
- **Q25 Reimbursement tool** (multi) → `What reimbursement tool do you use?`
- **Q26 3PL management** (multi) → `Which 3PL Management do you use?`
- **Q27 HR/Recruitment** (multi, top 5 + Other) ⭐ *(trimmed from 10)* → `Which HR/Recruitment Services do you use?`

## S5 · Growth
- **Q28 Goals this year** (long_text, R) → `Goals`
- **Q29 Biggest challenge** (long_text, R) → `Biggest Challenge`
- **Q30 Competitive advantage** (multi) → `Competitive Advantage`
- **Q31 How you plan to grow (next 12mo)** (long_text) → `Plans for next year`
- **Q32 Best thing that worked (last 12mo)** (long_text) → `Worked Best For You`
- **Q33 Most impactful service/software** (short_text) → `Service Provider Big Impact`
- **Q34 Industries you spend >20% time on** (multi) → `What industries/business activities…20% of your time on?`

## S6 · MDS feedback
- **Q35 Rank member benefits** (ranking) → *(to confirm)*
- **Q36 Virtual-call topics wanted** (short_text) → `Topics on Virtual Calls`
- **Q37 Does our visual branding resonate?** (opinion_scale) → `Brand Count`
- **Q38 Why / branding improvement ideas** *(cond on Q37)* (long_text) → `We're curious to know why you chose your answer? …`
- **Q39 NPS — likely to recommend MDS** (opinion_scale, R) → `NPS Value`
- **Q40 How MDS impacted you (12mo)** (long_text) → `How has MDS Impacted You? `
- **Q41 How can we make MDS better?** (long_text) → `How can we make MDS better for you `
- **Q42 Rate UX of MDS systems** (opinion_scale) → `Technology Score`
- **Q43 Tech enhancement areas** (long_text) → `Technology Feedback`
- **Q44 Other knowledge bases/groups you're in** (short_text) → `Knowledge bases`
- **Q45 Friends who'd qualify for MDS?** (yes_no) → `Has friends to refer`

## S7 · Programs (gated)
- **Q46 Involved in a MDS Chapter?** (multi, R) → `Involved in a MDS Chapter?`
  - **JUMP:** Yes → Q47 · No → **Q49**
- **Q47 Rate the Chapter events** *(cond)* (opinion_scale) → `How would you rate MDS Chapters`
- **Q48 See more at Chapters** *(cond)* (long_text) → `See more of at Chapter Events`
- **Q49 Participated in any MDS Programs?** (multi, R) → `Have you participated in any MDS Programs?`
  - **JUMP:** Yes → Q50 · No → **Q52**
- **Q50 Rate the program(s)** *(cond)* (opinion_scale) → `How would you rate the program`
- **Q51 See more with Programs** *(cond)* (long_text) → `What Would you like to see more of with programs?`
- **Q52 Involved in a MDS Squad?** (multi, R) → `Involved in a MDS Squad?`
  - **JUMP:** Yes → Q53 · No → **Q55**
- **Q53 Rate the Squads program** *(cond)* (opinion_scale) → `How would you rate MDS Squads`
- **Q54 See more at Squads** *(cond)* (long_text) → `See more of at MDS Squads`

## S8 · Personal
- **Q55 How many kids do you have?** (number) → `How many kids do you have?` *(add max validation to block troll values)*
  - **JUMP:** ≥ 1 → Q56 · 0 → **Q57**
- **Q56 Their age ranges** *(cond)* (short_text) → `What are their age ranges?`

## S9 · Classification & closer
- **Q57 Activities that describe you** (multi, R) → `Do any Activities Describe You (Membership Requirements)`
  - **JUMP:** coach/teacher/vendor-type selected → Q58 · else → **Q59**
- **Q58 Please explain further** *(cond)* (long_text) → `Explain Further`
- **Q59 What have you been up to?** (long_text) → *(to confirm)*

**End** → thank-you screen.

---

## Member matching (design assumption for now: email = match)
1. Primary: TF **Email (Q2)** → search AT **Members.Preferred Email**.
2. **No hidden field / secondary email:** if no Preferred-Email match → try hidden `email` (if present), then name (Q1) as a tiebreaker → flag *needs-review* rather than mis-link or create.
3. Hidden `member_id` link param = a **later** enhancement to prefill/skip identity; form works fully without it.
4. Never create a Member from the census — only link/update an existing one, or flag unmatched.

## Nothing dropped
The census keeps every legacy question (annual re-capture). Question-level dedup is deferred to the **Standard-vs-MDSonly merge**. Only structural changes: revenue REMAP (Q12), channel matrix → numeric % (Q14–17), HR trim (Q27), the "use use" copy fix (Q23).

## ~59 questions (conditionals keep the per-member seen-count lower)
