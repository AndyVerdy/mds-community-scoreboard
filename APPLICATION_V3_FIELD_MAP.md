> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Application v3 — Field Mapping Worksheet

**Typeform `FsVHzNN9` → Make `4784286` → Airtable Forms `tblblwPcgqhkPTVec`.**
For each question: the existing AT field to **confirm reuse**, or flagged **CREATE NEW / FIX / DECIDE**.
Generated 2026-06-29 from live form + live scenario mapper + AT schema (736 fields).

## ⚑ Rows needing a decision (everything else = confirm reuse)
- **7b · 7f · 7h · 7j — channel %s:** existing fields are **range buckets** (`<5%,6-15%…`) with dependencies; Eugene wants **numbers** → create new numeric, or repurpose (risky)?
- **7c — Amazon marketplaces:** no existing field → **CREATE NEW** (multi-select)
- **7e — Other channels:** no existing field → **CREATE NEW** (multi-select)
- **7d — Amazon storefront link:** **REUSE `Amazon Brand Storefront`** (confirm)
- **7g — DTC/Shopify link:** create new, or reuse generic `Website/Link`?
- **7i — TikTok shop link:** create new (url), or reuse `TikTok Shop Code`?
- **7a — Total revenue:** → `Unverified Revenue` (Centurion-style verification, not auto-trusted)
- **1f — second-seat:** FIX checkbox bug (per-choice)
- **7m · 7n — purchased/sold:** FIX to Yes/No
- **7o — acquiring:** delete polluted True/False options
- **4a · 7q · 8a — dedupe:** answer maps to 2–3 AT fields, keep one
- **1d — address:** OK (maps via 6 sub-fields into the address field)

## Full worksheet
| Slide | Form question | Existing AT field (mapped/suggested) | Action |
|---|---|---|---|
| 1a | What's your full name? | Name | confirm reuse |
| 1b | What's your email address?  | Email / Email | confirm reuse |
| 1c | What's your birthdate? | Birthdate | confirm reuse |
| 1d | What is your main address? | — | CHECK |
| 1e | What would you say is your current strongest are | Area of Expertise | confirm reuse |
| 1f | Is your business partner already an MDS member,  | Business Partner/Employee | FIX — checkbox bug (per-choice) |
| 1g | What is your business partner's or colleague's n | Name of Business Partner or Current Member | confirm reuse |
| 1h | What kinds of MDS events and activities are you  | What types of events would you be most excited to join local | confirm reuse |
| 1i | What’s one event idea or experience you’d love t | What’s one event idea or experience you’d love to see MDS ho | confirm reuse |
| 1j | Would you bring a guest to any of these events? | Would you want to bring someone to some of these events? | confirm reuse |
| 1k | How often do you see yourself attending local or | How often would you ideally attend local or regional events? | confirm reuse |
| 1l | How far would you be willing to travel for a reg | How far would you be willing to travel for a regional MDS ev | confirm reuse |
| 2a | Which of the following business models apply to  | Business Model | confirm reuse |
| 3a | What is your brand name? | Brand | confirm reuse |
| 3b | How many products do you have? | # of Products | confirm reuse |
| 4a | What is your agency / consulting company name? | Name of Company/Vendor / What is the name of your brand/comp | confirm + dedupe (2 fields) |
| 4b | How many brands do you manage? | How many brands do you currently have? | confirm reuse |
| 4c | What brands do you manage? | Brand Name(s) | confirm reuse |
| 4d | How many products do you manage? | # of Products manage | confirm reuse |
| 4e | What is your agency website? | agency website / Website/Link | confirm reuse |
| 5a | How many products do you sell? | # of Products sell | confirm reuse |
| 5b | What is your wholesale website? | wholesale website | confirm reuse |
| 6a | What is your SaaS / software company name? | Software Name | confirm reuse |
| 6b | Tell us more about your SaaS | SaaS description | confirm reuse |
| 6c | What is your software / SaaS website? | Software website | confirm reuse |
| 7a | What was your total revenue over the past 12 mon | Total TTM Revenue | → Unverified Revenue (verification flow) |
| 7b | (NEW) What percentage of your revenue comes from | Amazon US & % of Revenue (range) — OR new numeric | DECIDE: numeric vs range |
| 7c | (NEW) Which Amazon marketplaces do you sell on? | — none (per-market %-fields exist, diff shape) | CREATE NEW (multi-select) |
| 7d | (NEW) What's the link to your main Amazon storef | Amazon Brand Storefront (url) fldysNrMTERHKFHC5 | REUSE — confirm |
| 7e | (NEW) What other channels do you sell on? | — none | CREATE NEW (multi-select) |
| 7f | (NEW) What percentage of your revenue comes from | DTC % of Revenue / Own Website % (range) | DECIDE: numeric vs range |
| 7g | (MOVED) What's your DTC / Shopify store link? | Website/Link (url) — generic, or new | CREATE NEW (DTC link) or reuse |
| 7h | (NEW) What percentage of your revenue comes from | Tiktok % of Revenue (range) | DECIDE: numeric vs range |
| 7i | (NEW) What's the link to your TikTok shop? | TikTok Shop Code / Account Name (text) | CREATE NEW (url) or reuse |
| 7j | (NEW) What percentage of your revenue comes from | Retail % of Revenue (range) | DECIDE: numeric vs range |
| 7k | (MOVED) Which retailers do you sell through? | Physical retailers | confirm reuse |
| 7l | Which other channels / marketplaces do you sell  | sell on other marketplaces? | confirm reuse |
| 7m | Have you ever purchased a brand or business befo | purchased or sold an e-com business? / Bought a business | FIX — Yes/No + dedupe (2 fields) |
| 7n | Have you sold a brand or business before? | Sold a business | FIX — Yes/No |
| 7o | Are you actively acquiring ecommerce businesses? | Acquiring Ecom Business? | confirm (Yes/No ok; delete True/False opts) |
| 7p | What is one service provider or software that ha | Service Provider Big Impact | confirm reuse |
| 7q | What are your plans for business growth in the n | Plans for next year / What are your plans for your brand for | confirm + dedupe (2 fields) |
| 7r | What would you say are your competitive advantag | Competitive Advantage | confirm reuse |
| 7s | How would you best describe your current growth  | Growth posture | confirm reuse |
| 7t | What is the biggest constraint to your growth ri | Biggest constraint | confirm reuse |
| 7u | How confident do you feel heading into the next  | Confidence heading next 12 months | confirm reuse |
| 8a | What is your official role within your company? | Role / Title : / Formal Title / Job TItle | confirm + dedupe (3 fields) |
| 8b | If applicable, what other knowledge bases or gro | Knowledge bases | confirm reuse |
| 8c | What is the biggest challenge you have been faci | Biggest Challenge | confirm reuse |
| 8d | Tell us a fun, unique, or interesting fact about | Interesting/Fun Fact | confirm reuse |
| 8e | What motivated you to join MDS? | Motivation to join MDS | confirm reuse |
| 8f | Do any of the following activities describe you? | Do any Activities Describe You (Membership Requirements) | confirm reuse |
| 8g | Tell us more about how you teach, coach, or lead | how you teach, coach, or lead | confirm reuse |
| 8h | Did somebody refer you into MDS? | were you referred? | confirm reuse |
| 8i | Who referred you? | Who referred? | confirm reuse |
| 8j | Upload a Photo of Yourself | Photo of Member | confirm reuse |
| 9a | Confirm Your Information | confirm your information | confirm reuse |
| 9b | Verify Your Sales | Revenue Screenshot | confirm reuse |
| 9c | Commit to Community Engagement | commit to community engagement | confirm reuse |
| 9d | Agree to **[MDS ](https://docs.google.com/docume | agree to mds membership agreement | confirm reuse |
## Removed mappings (questions deleted from form)
| AT field | was ref |
|---|---|
| Amazon US & % of Revenue (matrix) | b6db48a3 |
| DTC % of Revenue (matrix) | cf1f131a |
| Tiktok % of Revenue (matrix) | c5ccffe9 |
| Retail % of Revenue (matrix) | f54a80bf |
| Sell Brand? | e7760e9b (plan-to-sell) |
