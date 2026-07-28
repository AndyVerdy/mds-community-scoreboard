> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Combined Census — Build Blueprint (v1: Eugene's screening model)

Merges [Standard - Annual Census](https://admin.typeform.com/form/I409BFlj/create) + [MDSonly - Annual Census Master](https://admin.typeform.com/form/DXs5mhZn/create) into one form under Eugene's screening/branching model. **Matrices kept as-is** (no trim this pass). Questions from both forms interleaved by topic.

## Flow
**Always up front:** full name · email · **Screening Q** (multi-select): "Which of these have changed since your last MDS application or census?"
Options → gate a stable section each: Role/responsibilities · Business model/brands/products/niche · Expertise/competitive-advantage · Operations/sourcing/manufacturing · Team/staffing · Tools/providers · Other business/investment interests · Other communities · Family · **None** (skip all stable) · **I'm not sure** (open all stable).

## Stable sections (shown only if picked in screening)
| Gate | Fields (Standard + MDSonly) |
|---|---|
| Role | official role · day-to-day responsibilities |
| Business & products | business models · current e-com involvement · # brands · brand name(s) · # products · main niche |
| Expertise | strongest expertise · competitive advantage |
| Operations & sourcing | warehousing types · sourcing method · manufacturing matrix (+other) · marketing matrix · ops-handling matrix |
| Team & staffing | staff locations · team-pay matrix · EOS? → how |
| Tools & providers | split-testing · PPC · reimbursement · 3PL · HR |
| Interests | industries >20% of time |
| Communities | other knowledge bases/groups |
| Family | Do you have kids? → count → age ranges |

## Annual sections (always shown)
- **Revenue & channels:** TTM revenue · projected FTM · Amazon % · which-other-channels gate → DTC/TikTok/Retail % (running total) · plan-to-sell · purchased/acquiring/sold → when → still-have
- **Supply chain this year:** CBM cost · production time · shipping time · orders shipped · containers · products launched · new products planned · selling-focus matrix
- **Team size this year:** full-time · part-time · VAs · team-building tip
- **Goals & growth:** goals · biggest challenge · growth plan · best thing that worked · most impactful tool
- **MDS feedback:** 11 benefit ratings (section) · virtual-call topics · branding rating → why · NPS · MDS impact · how-to-improve · UX rating · tech feedback · referrals
- **MDS programs:** Chapters → rate → more · Programs → rate → more · Squads → rate → more (each gated within)
- **Disclosure:** activities → explain
- **Access:** Gsuite email

## Gating logic (how the screening branch works)
- Screening routes to the first *selected* stable section; each stable section's exit routes to the next selected section; if none selected → jump straight to the first annual section.
- **None** → all stable skipped. **I'm not sure** → all stable shown.
- Within-section gates preserved: channels (only-selected), kids (have-kids→count→ages), Chapters/Programs/Squads (involved→rate), sold (→when→still-have), activities (→explain).

## Deferred to next pass
Matrix trims/drops (per `CENSUS_DROPPED_QUESTIONS.md`), tool "Other" + Amazon-centric review (Eugene), final benefit-rating scale, required-field restore, Airtable sync.
