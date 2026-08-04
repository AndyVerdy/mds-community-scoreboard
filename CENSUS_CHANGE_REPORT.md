> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Census Change Report — 2026-07-29

Form: [MDS Annual Census 2026 — Combined](https://admin.typeform.com/form/DFeK5yop/create) `DFeK5yop`. All changes live (PUT 200, verified via re-GET). Q#s = current live numbering ([[CENSUS_LIVE_INDEX]]). Rollback of the pre-batch form: `census_DFeK5yop_backup_2026-07-29.json`. "Before" = state at start of today; "legacy" = the original census matrix where relevant.

## Change log (before → now)

| Q# | Question | Before (today's start) | Now | Type |
|---|---|---|---|---|
| Q26 | EOS | "…with an implementer"; no description | + plain description; "…with a **certified EOS Implementer**" | reword + description |
| Q45 | Selling focus | **open text** "focusing on expansion? which channels?" *(legacy: 11-channel × 7-intent matrix)* | **8-option multi-select** (Amazon US · Amazon intl · TikTok Shop · DTC · Walmart/Target · Wholesale/B2B · Other · Not expanding) | retyped → structured |
| Q50 | Member benefits | ranking of 11 incl 4 separate FB subgroups; "Partner Directory/MDS Only Offers"; not randomized | 11 items: FB subgroups→**Facebook Groups**; **Partner Directory/Offers**; +**WhatsApp Chats/Chapters/Squads**; **randomized** | merge + rename + add + randomize |
| Q9 + Q10–15 | Manufacturing | 7-country multi-select, no % *(legacy: 9-country × 6 %-band matrix)* | 6-country multi-select **+ 6 new % questions** (one per country) with running total to 100 | trim + **6 added** + **logic added** |
| Q16, Q17 | Marketing / Ops | 3 flat fields: in-house multi · outsource open-text · ops-outsource multi | **2 matrices restored** (channel/area × N/A·In-house·Agency·Freelancer·Other); **Photo+Graphic Design merged** | 3 fields → 2 matrices |
| Q19 | Tools & providers | 9 options (incl Split-testing) | **12 options** (research-driven; Split-testing removed) | options replaced |
| Q22, Q23 | Team roles | 1 field, 12 roles *(legacy: 12-role × 9-pay-band matrix)* | **split into 2**: leadership/C-level roles · other roles | **split 1 → 2** |
| Q36 | Current involvement | 7 options, standalone, no logic | same options **+ non-operator skip logic** | **logic added** |

## ⚙️ Conditional logic ADDED today (2 new)
1. **Manufacturing % (Q9 → Q10–15).** Selecting countries at Q9 now shows a % question only for each selected country, with a running total (`mfg_total`) toward 100% — unselected countries are skipped. Mirrors the existing revenue-channel pattern (Q32→Q33–35).
2. **Non-operator skip (Q36 → Q37 gate).** If current involvement = *sold & no longer operate · consultant · investor · exploring*, the form **skips the supply-chain block Q38–44** (CBM cost, production/shipping time, orders shipped, containers, products launched, new products) and jumps to Q45. Active operators still see everything.

*(Pre-existing logic, unchanged: screening section-gates at Q4; revenue per-channel % at Q32; family kids-skip; program/chapter/squad "No→skip rating"; activities "None→skip explain".)*

## 🗑️ Deleted today
- **Europe** removed as a manufacturing country option (folds into "Other").
- **Split-testing tool** removed from the tools list (demoted per Eugene + low adoption).
- **3 marketing/ops fields** (in-house / outsource-text / ops-outsource) replaced by the 2 matrices.
- **"with an implementer"** wording → "certified EOS Implementer".
- *(No whole questions deleted-without-replacement today. Earlier passes deleted: goals, growth-plan, #1-team-suggestion, friends-qualify.)*

## ✂️ Split / 🔗 Merged today
- **SPLIT — Team roles:** 1 question → **2** (leadership/C-level · other roles).
- **SPLIT — Manufacturing:** 1 question → **1 + 6** (country select + per-country %).
- **MERGE — Facebook:** 4 FB subgroup benefit options → 1 "Facebook Groups".
- **MERGE — Photography + Graphic Design:** 2 ops rows → 1 matrix row.
- **MERGE — Marketing/ops:** the flat in-house/outsource fields collapsed back into single matrices.

## ⚠️ Still open (1)
- **Q22 leadership pay.** Role split shipped; **pay capture not built** (matrix rejected). Needs a decision: (a) one "total monthly leadership payroll" number, (b) gated pay-band per leadership role, or (c) no pay.
