# Eugene's feedback — what I did + how I resolved it (for review)

Form: [MDS Annual Census 2026 — Combined](https://admin.typeform.com/form/DFeK5yop/create) `DFeK5yop`. Each point: **Eugene → Did → How resolved (merges/drops/where things moved) → Where to look.** ⚠️ = still needs input.

---

### 1 · Screening question (Q4)
- **Eugene:** too many choices; don't advertise skipping; tools & team always change; family unclear.
- **Did:** cut to 6 options; removed "the rest we'll skip"; ungated Tools/Team/Communities/Interests.
- **How resolved:** **9 gated sections → 4.** One *merge* (Role + Expertise → single gate). Four *ungated* → moved to the always-shown block (everyone sees them). Remaining 4 options each still open their section; None skips all; Not-sure opens all. Branching verified forward.
- **Look:** Q4.

### 2 · Role (Q5a)
- **Eugene:** ask about the change ("new role").
- **Did / how:** simple reword → "What is your new role within your company?". No dependency impact.

### 3 · Current involvement (Q30) — ❌ NOT BUILT (open fix)
- **Eugene (exact):** "This can probably be its own question that drives decisions and branching."
- **What I actually did:** only *relocated* it (was 6b under Business; now Q30 next to M&A). **No branching wired off it.** My earlier "nothing to rewire" was wrong.
- **The fix (TODO):** move it UP (before the operational sections) and gate the operator-only block on it — Business snapshot · Operations · Revenue & channels · Supply chain · Team. Answers "sold & no longer operate / investor / exploring" skip that block → jump to M&A + MDS-feedback. "Actively operate" + "sold but still operate" get everything. Everyone still gets role/expertise, M&A, interests, communities, family, feedback, programs, disclosure.
- **Design note:** overlaps the screening question — current-involvement is the deeper gate ("do you have an operating business?"), screening ("what changed?") sits under it. Decide the two-level flow before building.

## ✅ SHIPPED & VERIFIED 2026-07-29 (PUT 200 to DFeK5yop, confirmed via re-GET)
- **Q20 EOS** — added plain description ("EOS (Entrepreneurial Operating System) — a structured framework…") + relabeled "with an implementer" → "with a **certified EOS Implementer**".
- **Q39 selling-focus** — `long_text` → **8-option multi-select** (Amazon US · Amazon intl · TikTok Shop · DTC · Walmart/Target · Wholesale/B2B · Other · Not expanding); TikTok/DTC labels match Q26.
- **Q44 member benefits** — 4 FB subgroups → **Facebook Groups**; renamed **Partner Directory/Offers**; added **WhatsApp Chats · Chapters · Squads**; `randomize`=True confirmed.

## ✅ OPEN FIXES — ALL SHIPPED 2026-07-29 (PUT 200 to DFeK5yop, verified via re-GET)
All items below are now live. Numbers here are the OLD draft numbers; see [[CENSUS_LIVE_INDEX]] for current. Rollback = `census_DFeK5yop_backup_2026-07-29.json`.
- **#1 Q30 current-involvement branching** — non-operators (sold-no-longer / consultant / investor / exploring) skip the supply-chain block → jump to selling-focus. Refs + OR-condition jump verified.
- **#2 Q9 manufacturing %** — country multi-select + per-selected-country % with `mfg_total` running total (mirrors the revenue-channel pattern). Fixed the broken single-% approach.
- **#3 Q10–12 marketing/ops** — restored as **two matrices** (channel/area × N/A·In-house·Agency·Freelancer·Other), always-asked; **Photography + Graphic Design merged**.
- **#4 Q17 team-pay** — split into **leadership roles** + **other roles** (2 questions). ⚠️ **PAY CAPTURE STILL OPEN** — matrix rejected; need Andy's decision on how to collect leadership pay without a grid.
- **Q39 selling-focus, Q44 member benefits, Q14 tools, Q20 EOS** — shipped (see above).

### Original open-fix detail (historical):
## ⚠️ OPEN FIXES found in re-review (2026-07-29)
1. **Current involvement → drive branching** (above) — not built.
2. **Manufacturing % — grab the number** (Andy): current multi-select drops the % split. Fix = mirror the revenue-channels pattern → multi-select countries, then a % per selected country with running total (single country auto-skips → 100%). [Option B: one "% from your main country" if >1 selected.] Andy leaning: get a number.
3. **Marketing + ops-handling (Q10–12) — I OVER-REDESIGNED these.** Eugene only said they "change every single time" (= keep, always-ask, don't gate) + add smart-logic. He did NOT call them confusing (that was manufacturing + team-pay). My de-matrix (in-house Q10 / outsource Q11 / ops Q12) is confusing + lost the handler detail. **Fix:** restore both as their original matrices (function × in-house/agency/freelancer), always-asked, + add smart-logic follow-up ("for anything you outsource, who?"). No branching is currently built. Also **merge Photography + Graphic Design** into one option.
4. **Team-pay (Q17) — I dropped pay; Eugene wanted a redesign that KEEPS it.** Fix = "which roles?" (multi) + **gated salary-band follow-up per selected role** (matrix data as individual questions; only selected roles ask pay). Reduce the 12-option list by splitting into **Leadership (role+pay)** + **other roles (presence-only)**. Depth decision (Andy): minimal / detailed(pay all roles) / middle(pay leadership only). Andy leaning + my rec: **middle**.
5. **Selling-focus (Q39) — open text → multi-select (DECIDED w/ Andy).** Replace the open text with one multi-select "Which channels are you planning to expand into or grow in the next 12 months?": Amazon US · Amazon international (EU/Canada/Asia/ME) · TikTok Shop · DTC/own website · Walmart.com/Target.com · Wholesale/B2B · Other · Not expanding. Align **Q26** (current channels) to the same vocabulary so now-vs-next compare 1:1 (intent = doubling-down/new-entry derivable from the pair; no matrix). Old matrix was MDSonly Q17 = 11 ch × 7 intent.
6. **Member benefits (Q44) — new list + randomize (DECIDED w/ Andy).** Combine the 4 FB subgroups → one **Facebook Groups**; rename "Partner Directory/MDS Only Offers" → **Partner Directory/Offers**; add **WhatsApp Chats · Chapters · Squads**. Final 11: Member Map/Directory · Virtual Calls · In-person Events · Video Archives · Document Repository · MDS Perks · Partner Directory/Offers · Facebook Groups · WhatsApp Chats · Chapters · Squads. Set `randomize` on the ranking field. ⚠ verify Typeform accepts `randomize` on ranking at apply time. (Flag: 11 items is heavy to drag-rank — consider "rank your top 5" if completion dips.)
7. **Tools & providers (Q14) — list sourced (DECIDED).** Use the ~14-category taxonomy in [[CENSUS_TOOLS_LIST]] (from the GroupOS partner directory). ~30 partners still need Google category-verify (classifier-blocked); taxonomy unaffected.
8. _(Andy still reviewing — more may follow.)_

### 4 · Manufacturing matrix (Q9)
- **Eugene:** confusing — find a better way.
- **How resolved:** the 2-D grid (9 countries × 6 % bands) → a **single multi-select of countries**. Trade-off: we no longer capture the *% split* per country (that was the confusing part). Easy to add a follow-up % later if needed.

### 5 · Marketing + ops-handling matrices (Q10–12)
- **Eugene:** likely change every time; add smart-logic (agency vs tool).
- **How resolved:** marketing grid (8 channels × handler) → **"which channels in-house"** (multi) + **"which outsourced, and to whom"** (open — this seeds the smart-logic). Ops grid → **"which do you outsource"** (multi; anything unselected = in-house). Trade-off: we lose the exact per-row handler label, but keep the in-house/outsourced split.

### 6 · Team-pay matrix (Q17)
- **Eugene:** hard to answer — fix the approach.
- **How resolved:** 12 roles × 9 pay bands → **"which roles do you have on your team?"** multi-select. **Salary collection dropped entirely** (also sensitive, which you flagged). Trade-off: no pay data — flag if you want a lighter pay capture back.

### 7 · EOS (Q20)
- **Eugene:** combine the two EOS questions into one.
- **How resolved:** "Do you use EOS? (Y/N)" + "How do you implement it?" → **one question** whose options encode both (No/haven't · Yes-self · Yes-implementer · Yes-other). The old conditional branch (show "how" only if Yes) is gone — no branch needed anymore.

### 8 · Employee counts (Q18–19)
- **Eugene:** 3 questions → 1–2.
- **How resolved:** **full-time + part-time merged into one number** ("employees, full + part time"); VAs/offshore kept separate → **3 → 2**. Trade-off: lose the FT-vs-PT split.

### 9 · Tools & providers (Q14–15) ⚠️
- **Eugene:** archetype changed; present to @Anita.
- **How resolved:** the 5 fixed vendor lists → **one "which services/tools do you use?"** (PPC, affiliate/creator mgmt, TikTok agency, Amazon agency, HR, reimbursement, 3PL, split-testing, Other) + **"which providers?"** open. Ungated (always shows). ⚠️ **exact list needs Anita/partnerships.**

### 10 · Interests + Communities (Q21–22)
- **Eugene:** industries too many + overlaps current-involvement; communities shouldn't be gated.
- **How resolved:** industries **stripped of the ecom options** (Amazon/DTC/wholesale — those overlap current-involvement) → kept only non-ecom (real estate, crypto, stocks, angel, new venture, other), reworded "Outside your core ecommerce business…". Both **ungated** → always shown.

### 11 · M&A / status — 5 → 2 (Q30–31)
- **Eugene:** current-involvement + plan-to-sell + purchased/acquiring/sold are overly similar.
- **How resolved:** kept **current involvement** (Q30) + one **"Which describe your M&A activity?"** multi-select (Q31: purchased / sold / actively acquiring / plan to sell next 12mo / none). **Dropped** the 4 separate yes/nos **and** their conditional follow-ups (when-did-you-sell, still-have-revenue). Trade-off: lose the sell-date + residual-revenue detail.

### 12 · Selling-focus matrix (Q39)
- **Eugene:** rethink holistically / open-ended.
- **How resolved:** 11 channels × intent grid → **open text** "Are you focusing on channel expansion? which channels?". Trade-off: no structured per-channel intent.

### 13 · The two 20% matrices (Q40)
- **Eugene:** didn't work, but keep the "what's getting more expensive/cheaper" intent.
- **How resolved:** deleted YoY-change + revenue-by-category grids → **one open question** "Which parts of your business got more (or less) expensive this year?". Trade-off: no structured cost breakdown.

### 14 · Growth (Q41–43)
- **Eugene:** goals = duplicate; growth-plan = covered by other growth Qs.
- **How resolved:** **deleted both**; kept biggest-challenge, best-thing-that-worked, most-impactful-tool.

### 15 · Member benefits (Q44) ⚠️
- **Eugene:** back to ONE ranking; list outdated.
- **How resolved:** the group of **11 separate ratings → one ranking** question. ⚠️ list is still the old 11 — **needs the current-resources list** from you/Eugene.

### 16 · Feedback & referral
- **Eugene:** keep "make MDS better" open-ended ✅; friends-qualify redundant with NPS → drop ✅; consolidate the promote/feedback cluster.
- **How resolved:** kept the open-ended one (Q50); **deleted friends-qualify** (NPS at Q48 stays — not yet re-added as an NPS follow-up). **Full cluster consolidation still open** (a design pass).

### 17 · Global
- **"e-commerce" → "ecommerce"** everywhere ✅.

---

## Still needs your/Eugene's input
1. **Tools list** — exact current tools → Anita/partnerships (Q14).
2. **Benefit ranking list** — current MDS resources → you/Eugene (Q44).
3. **Feedback/referral cluster** — full consolidation not yet done.

## Detail intentionally dropped in the matrix redesigns (confirm OK)
Per-country manufacturing %, per-channel marketing handler, **team salary bands**, FT-vs-PT split, sell-date/residual-revenue, per-channel selling intent, structured cost breakdown. All traded for simpler questions per Eugene — flag any you want back.
