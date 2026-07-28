> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Application v3 — TF → AT Mapping & Decisions

View: https://airtable.com/appou5JVr0WIrioWS/tblblwPcgqhkPTVec/viwGWCs8abBOb8yQi

**Legend** — *AT field exists?* ♻️ legacy = field already in AT (reuse) · 🆕 new = must create.  *Mapped today?* ✅ = current Make scenario already writes this · ❌ = no mapping yet (remap adds it).

Sorted in Typeform order.

| TF | Question | AT field | Type | AT field exists? | Mapped today? | Decision |
|---|---|---|---|---|---|---|
| 1a | What's your full name? | Name | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 1b | What's your email address?  | Email | email | ♻️ legacy | ✅ synced | reuse |
| 1c | What's your birthdate? | Birthdate | date | ♻️ legacy | ✅ synced | reuse |
| 1d | What is your main address? | (via 6 sub-fields) | — | ♻️ legacy | ✅ synced | ok |
| 1e | What would you say is your current str | Area of Expertise | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 1f | Is your business partner already an MD | Business Partner/Employee | checkbox | ♻️ legacy | ✅ synced | FIX checkbox bug |
| 1g | What is your business partner's or col | Name of Business Partner or Current Memb | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 1h | What kinds of MDS events and activitie | What types of events would you be most e | multipleSelects | ♻️ legacy | ✅ synced | reuse |
| 1i | What’s one event idea or experience yo | What’s one event idea or experience you’ | multilineText | ♻️ legacy | ✅ synced | reuse |
| 1j | Would you bring a guest to any of thes | Would you want to bring someone to some  | multipleSelects | ♻️ legacy | ✅ synced | reuse |
| 1k | How often do you see yourself attendin | How often would you ideally attend local | singleSelect | ♻️ legacy | ✅ synced | reuse |
| 1l | How far would you be willing to travel | How far would you be willing to travel f | singleSelect | ♻️ legacy | ✅ synced | reuse |
| 2a | Which of the following business models | Business Model | multipleSelects | ♻️ legacy | ✅ synced | reuse |
| 3a | What is your brand name? | Brand | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 3b | How many products do you have? | # of Products | number | ♻️ legacy | ✅ synced | reuse |
| 4a | What is your agency / consulting compa | Name of Company/Vendor (+1 dup) | singleLineText | ♻️ legacy | ✅ synced (2 fields) | dedupe |
| 4b | How many brands do you manage? | How many brands do you currently have? | singleSelect | ♻️ legacy | ✅ synced | reuse |
| 4c | What brands do you manage? | Brand Name(s) | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 4d | How many products do you manage? | # of Products manage | number | ♻️ legacy | ✅ synced | reuse |
| 4e | What is your agency website? | agency website | url | ♻️ legacy | ✅ synced | reuse |
| 5a | How many products do you sell? | # of Products sell | number | ♻️ legacy | ✅ synced | reuse |
| 5b | What is your wholesale website? | wholesale website | url | ♻️ legacy | ✅ synced | reuse |
| 6a | What is your SaaS / software company n | Software Name | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 6b | Tell us more about your SaaS | SaaS description | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 6c | What is your software / SaaS website? | Software website | url | ♻️ legacy | ✅ synced | reuse |
| 7a | What was your total revenue over the p | Total TTM Revenue (+ new Unverified Reve | currency | ♻️ legacy + 🆕 | ✅ synced | route to Unverified Revenue + verification flow |
| 7b | (NEW) What percentage of your revenue  | Amazon % of Revenue | Number | 🆕 new | ❌ not yet | new numeric vs reuse legacy range 'Amazon US & % of Revenue' |
| 7c | (NEW) Which Amazon marketplaces do you | Amazon Marketplaces | multi-select | 🆕 new | ❌ not yet | CREATE NEW — no legacy field |
| 7d | (NEW) What's the link to your main Ama | Amazon Brand Storefront | url | ♻️ legacy | ❌ not yet | reuse legacy — confirm |
| 7e | (NEW) What other channels do you sell  | Other Sales Channels | multi-select | 🆕 new | ❌ not yet | CREATE NEW — no legacy field |
| 7f | (NEW) What percentage of your revenue  | DTC % of Revenue | Number | 🆕 new | ❌ not yet | new numeric vs reuse legacy range |
| 7g | (MOVED) What's your DTC / Shopify stor | DTC / Shopify Link | url | 🆕 new | ⚠️ via Website/Link concat only | create new, or reuse 'Website/Link' |
| 7h | (NEW) What percentage of your revenue  | TikTok % of Revenue | Number | 🆕 new | ❌ not yet | new numeric vs reuse legacy range |
| 7i | (NEW) What's the link to your TikTok s | TikTok Shop Link | url | 🆕 new | ❌ not yet | create new, or reuse 'TikTok Shop Code' |
| 7j | (NEW) What percentage of your revenue  | Retail % of Revenue | Number | 🆕 new | ❌ not yet | new numeric vs reuse legacy range |
| 7k | (MOVED) Which retailers do you sell th | Physical retailers | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 7l | Which other channels / marketplaces do | sell on other marketplaces? | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 7m | Have you ever purchased a brand or bus | purchased or sold… / Bought a business | checkbox | ♻️ legacy | ✅ synced (2 fields) | FIX Yes/No + dedupe |
| 7n | Have you sold a brand or business befo | Sold a business | checkbox | ♻️ legacy | ✅ synced | FIX Yes/No |
| 7o | Are you actively acquiring ecommerce b | Acquiring Ecom Business? | singleSelect | ♻️ legacy | ✅ synced | delete True/False options |
| 7p | What is one service provider or softwa | Service Provider Big Impact | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 7q | What are your plans for business growt | Plans for next year (+1 dup) | long text | ♻️ legacy | ✅ synced (2 fields) | dedupe |
| 7r | What would you say are your competitiv | Competitive Advantage | multipleSelects | ♻️ legacy | ✅ synced | reuse |
| 7s | How would you best describe your curre | Growth posture | multipleSelects | ♻️ legacy | ✅ synced | reuse |
| 7t | What is the biggest constraint to your | Biggest constraint | multipleSelects | ♻️ legacy | ✅ synced | reuse |
| 7u | How confident do you feel heading into | Confidence heading next 12 months | singleSelect | ♻️ legacy | ✅ synced | reuse |
| 8a | What is your official role within your | Role/Title (+2 dup) | singleLineText | ♻️ legacy | ✅ synced (3 fields) | dedupe |
| 8b | If applicable, what other knowledge ba | Knowledge bases | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 8c | What is the biggest challenge you have | Biggest Challenge | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 8d | Tell us a fun, unique, or interesting  | Interesting/Fun Fact | multilineText | ♻️ legacy | ✅ synced | reuse |
| 8e | What motivated you to join MDS? | Motivation to join MDS | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 8f | Do any of the following activities des | Do any Activities Describe You (Membersh | multilineText | ♻️ legacy | ✅ synced | reuse |
| 8g | Tell us more about how you teach, coac | how you teach, coach, or lead | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 8h | Did somebody refer you into MDS? | were you referred? | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 8i | Who referred you? | Who referred? | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 8j | Upload a Photo of Yourself | Photo of Member | url | ♻️ legacy | ✅ synced | reuse |
| 9a | Confirm Your Information | confirm your information | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 9b | Verify Your Sales | Revenue Screenshot | url | ♻️ legacy | ✅ synced | reuse |
| 9c | Commit to Community Engagement | commit to community engagement | singleLineText | ♻️ legacy | ✅ synced | reuse |
| 9d | Agree to **[MDS ](https://docs.google. | agree to mds membership agreement | singleLineText | ♻️ legacy | ✅ synced | reuse |
