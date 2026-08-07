# Question overlap — Singapore Check-In vs New Member Application v3

Compared live via Typeform API on **2026-08-05**.

| | Form | ID | Questions (non-group, statements excluded) |
|---|---|---|---|
| **A** | MDS Summit Singapore 2026 – Check In Form | `w3kCjPAK` | 56 |
| **B** | New Member Application v3 | `FsVHzNN9` | 64 |

**Literal exact matches: 0** — no two titles are character-identical (A has no `*bold*` wrapping, B wraps every title). The matches below are on *intent*: same answer, so a member who filled v3 is being re-asked.

---

## 1. Exact-intent duplicates (10) — same question, trivially different wording

| # | A — Singapore Check-In | B — Application v3 | Evidence |
|---|---|---|---|
| 1 | `contact_info` → First name + Last name | *What's your full name?* | same data |
| 2 | `contact_info` → Email | *What's your email address?* | same data |
| 3 | Date of Birth *(Hotel check-in group)* | *What's your birthdate?* | both `date` |
| 4 | What is your address of residence? (Include city, country, postal code) | *What is your main address?* | both `address` |
| 5 | What is your main niche / category? | *What is your main niche?* | near-verbatim |
| 6 | Approximately what percentage (%) of your revenue comes from **Amazon**? | *What percentage of your revenue comes from Amazon?* | both `number` |
| 7 | …comes from **TikTok**? | *What percentage of your revenue comes from TikTok Shop?* | both `number` |
| 8 | …comes from **DTC**? | *What percentage of your revenue comes from DTC / your own website?* | both `number` |
| 9 | …comes from **Retail**? | *What percentage of your revenue comes from Retail?* | both `number` |
| 10 | Your confidence level heading into 2027 | *How confident do you feel heading into the next 12 months?* | **identical 5 choices**: Very bullish / Cautiously optimistic / Neutral – wait-and-see / Concerned / Actively defensive |

---

## 2. Fuzzy / partial overlaps (11) — same construct, different scope, window or scale

| # | A — Singapore Check-In | B — Application v3 | Why it's only fuzzy |
|---|---|---|---|
| 1 | What was your 2025 revenue? · What is your projected 2026 revenue? | *What was your total revenue over the past 12 months?* | different time windows; A splits actual vs projected |
| 2 | …% of revenue from **Other Sales Channel**? | *What other channels do you sell on?* · *Which other channels / marketplaces do you sell on?* | A asks the **%**, B asks **which** |
| 3 | Which best describes your 2026 operating posture? | *How would you best describe your current growth posture?* | same construct, different option sets (6 vs 5) |
| 4 | What are the top challenges you are currently facing in your business or personal life? | *What is the biggest challenge you have been facing this year?* | A adds "personal life"; A `short_text`, B `long_text` |
| 5 | What area of the business do you feel most behind on right now? | *What is the biggest constraint to your growth right now?* | A open text, B 5-option choice |
| 6 | What is your brand/website? | *What is your brand / company name?* + agency / wholesale / SaaS website + Amazon storefront + DTC store link | B has no single "own brand website" field; A collapses name+URL into one |
| 7 | Are there any areas you're actively investing in right now? · Your biggest priority going into 2027 | *What are your plans for business growth in the next 12 months?* | same forward-looking intent, different horizons |
| 8 | Where do you see your business in 3–5 years? (incl. "Sell or exit") | *Have you sold a brand or business before?* · growth posture → "Actively preparing for exit" | exit intent vs exit history |
| 9 | How has your CAC changed vs. 2025? | constraint option *Traffic efficiency (CAC)* | A measures it, B only lists it as a constraint |
| 10 | Channels you're betting on for 2027 | *What other channels do you sell on?* | future bets vs current channels |
| 11 | What specific AI tools are you using regularly in your business today? | *What is one service provider or software that has made the most impact on your business in the last 12 months?* | overlapping answer space (tools/software) |

---

## 3. Unique to each form

**Only in Singapore Check-In** — event logistics (MDS member? · WhatsApp group · MDS app access · NDA checkbox · arrival/departure dates), full hotel/passport block (birth city+country, passport number, place of issue, expiry, arrival time, extra guests), event topics & activity preferences, dining preference, All-Star / Hack submission, and the entire 2026-vs-2027 pulse block (AI efficiency gains, experiments, profit trend, biggest shift since January, cash cycle, Amazon margin, least predictable, Q4 focus, pulling back on, team strategy, 2027 vs 2026 revenue).

**Only in Application v3** — previous role before ecom, strongest expertise, business-partner / second-seat, event & travel preferences (types, guest, frequency, distance), business model routing (Own Brand / Agency / Wholesale / SaaS with per-model company, brands managed, product counts, websites), Amazon marketplaces, retailers list, acquisition history (bought / sold / actively acquiring), competitive advantages, official role, other communities, fun fact, motivation to join MDS, teach/coach/lead activities, referral, photo upload, membership commitments + agreement.

---

## Flag (inside form A, not a cross-form issue)

`w3kCjPAK` asks **"Are you in our MDS Summit Singapore WhatsApp group?"** twice, verbatim — fields `YobauJ0vzgbJ` and `Du9I8VQ2yp3d`.
