> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Member Scorecard — System Audit & Rework Brief

_Audit date: 2026-06-02. Source of truth for this rework. Supersedes the description of the system in `CLAUDE.md`, which is stale (it describes an old Apify/`posts×10+comments×5` design that is no longer how the system works)._

---

## 1. TL;DR

- The public scorecard and Airtable API are **alive** — the live endpoint returns populated scores (top: Mo Kuhail 95.9). Nothing is "down."
- The real failure is that **the data feeding it is frozen**. The FB scraper is a **manual, local Playwright + GPT script** that was last run **2026-04-20** (~6 weeks stale and getting staler). Older pipeline tables are dead since Nov 2025 / 2024.
- The scoring model is **mid-redesign and already partially implemented** (FB engagement ≈ 50% of score, profile-completion consolidated, contribution log-normalized) — but the Airtable table is a **271-field mess** of duplicate/legacy formulas, and there are **two competing "final" scores**.
- **Security issue (unrelated to staleness, fix regardless):** the Airtable PAT is hard-coded in client-side JS on the public GitHub Pages site. Anyone can view-source and read the entire member table (emails, addresses, phones, revenue tiers, birthdates).

---

## 2. Architecture (as it actually is)

```
[FB Group]  --manual local Playwright+GPT script (~3h, Windows, Google Drive)-->  CSV
   |                                                                                |
   |                                                                         (manual import)
   v                                                                                v
[MDS App]  --Make/n8n sync--> [Airtable base appUM1F29IJsMsXRb] <----- [Event rosters, manual flags]
                                          |
                                "Member's score NEW" formula
                                          |
                          view viwRL6yJheOBwvqBr (tblbN6JVeSk2XoPst)
                                          |
                         index.html (GitHub Pages) reads Airtable directly
                              (PAT hard-coded in client JS)  ← security hole
                                          |
                                embed.js (iframe embed for MDS App / site)
```

Key IDs:
- Base: `appUM1F29IJsMsXRb`
- Members & Scorecard table: `tblbN6JVeSk2XoPst` (271 fields)
- Public view: `viwRL6yJheOBwvqBr`
- Live score field: `Member's score NEW` (`fldzEH3UZgOdE9bm2`)
- Scraper output tables: `tblZGetoyJyl2fTD7` (active, last 2026-04-20), `tblckOTP8UkC6K8Xr` (dead, last 2025-11-15)

---

## 3. Data we currently track (by source)

The score is the "Give More Get More" (GMGM) model — 5 sections: Get Visible · Get Connected · Get More · Give Back · Achieve it!. Inputs by source:

| Source | Signals | Reliability |
|---|---|---|
| **Facebook scraper** | Posts & comments (→ Engagement score 0–50), Give/Ask/#ValueAdd/Multi-ValueAdd posts, FB subgroup count, contribution points | ⚠️ Stale since 04-20; fragile manual process |
| **Events (rosters)** | Virtual/in-person/chapter registration + attendance (12/18-mo windows), calls hosted, roles in MDS, squad membership, chapter affiliation | Mixed — some synced, some manual |
| **MDS App (sync)** | Profile completion (12 custom fields → 0–5), profile photo, revenue tier, about-me, niche, hobbies, birthday, address | OK when sync runs |
| **Manual / independent** | Welcome call, coffee/lunch, perks used, vault docs, MDSonly census recency | ❌ Several have **no reliable data source** (coffee, perks, vault) — effectively always 0 |

Master rubric lives in two Airtable tables: `Member's Scorecard Fields Description` (25 scored actions, plain-English) and `Scored Actions` (versioned point values, automated/manual flags).

---

## 4. The live score, decoded

**`Member's score NEW`** = sum of:

| Component | Points | Notes |
|---|---|---|
| ~18 binary action flags (Give/Ask/ValueAdd posts, welcome call, virtual/in-person/chapter events, squad, role, MDSonly, etc.) | mostly **2** each | `IF(field, field, 0)` flags |
| Total # of Joined MDS FB subgroups | count | |
| **Contribution points Normalized** | **0–5** | `MIN(5, LOG(contribution+1)/LOG(70000)*5)` — log scale, **ignores zeros** ✅ |
| **Website profile completion score** | **0–5** | `(profile_fields_out_of_12 × 5)/12` — **consolidated & adjustable** ✅ |
| **Engagement score (0–50)** | **0–50** | FB posts+comments, the dominant term |
| **Max ≈ 107** | | `Member's score NEW Percent = score/107` |

So **FB-derived ≈ 50% of the score** (50 engagement + 5 contribution out of ~107). The directives from the Feb–Apr ClickUp thread (FB at 50%, log-scaling, ignore zeros, profile-completion as one adjustable variable) are **already partly implemented here.**

### Problems with the current scoring
1. **Two competing scores.** `Member's score NEW` (FB-dominant, max 107) vs. `Member score based on fairness assessment` (each GMGM category normalized to 25 → max 100). No decision on which is canonical.
2. **Public badges ≠ the real score.** `index.html` shows 25 badges grouped into 4 made-up categories (Connected/GiveBack/ShowUp/GoDeeper) with their own point caps (max 175). This display math is disconnected from the 107-point formula.
3. **Dead inputs still in the formula.** Coffee/lunch, perks, vault have no data source → silently always 0. Chapter-event *attendance* is in some scores but omitted from `Member's score NEW`.
4. **271-field clutter.** Dozens of `NEW`/`old`/`copy`/`DONT USE`/`outdated`/`ARCHIVE` duplicates make the table unmaintainable and error-prone.
5. **Windowing inconsistent.** Belen asked for "most data = last 12 months"; only some fields enforce it.

---

## 5. Data quality & freshness

| Table | Last refresh | Verdict |
|---|---|---|
| FB Weekly Metrics **output** (`tblZGetoyJyl2fTD7`) | **2026-04-20** | Active pipeline, ~6 wks stale |
| FB Weekly Metrics old (`tblckOTP8UkC6K8Xr`) | 2025-11-15 | Dead |
| New Member Weekly Metrics (`tblG8GnJ84QBkX8Sa`) | 2024-01-11 | Abandoned |

The weekly tables are **time-series snapshots keyed by Reporting Date** — which is the raw material we need for trends/churn, but the score itself is currently only a point-in-time number.

---

## 6. What we *want* to track (gaps for the stated goals)

Goals: track engagement → identify the **ideal member** → **predict churn** → feed events & gamification.

| Goal | Gap today | What to add |
|---|---|---|
| **Churn prediction** | Score is point-in-time only | **Score/engagement velocity** (Δ over 30/90 days), **recency** (days since last post/comment/engagement), renewal/tenure (`WA Renewal Date`, `FB Join Date`), flag drops to zero engagement |
| **Ideal member** | No profile of who scores high | Cross-reference top scorers with census attributes (revenue tier, niche, business model, tenure) — most of this already exists in the census/members data |
| **Engagement reporting** | Eyosafet's trend analysis is one-off | Eugene's ask: weekly Slack post — % engaged (score > 1) + median posts/comments (ignoring zeros), MoM/YoY |
| **New channels** | FB-only | WhatsApp subgroup membership/engagement (Eugene's "WA subgroups" add-on) |
| **Less fragility** | Manual inputs rot | Drop/automate coffee, perks, vault; lean on first-party MDS App + event data |

---

## 7. Rework tracks

1. **Secure + stabilize the public site** — remove the exposed PAT (proxy or cached snapshot), reconcile badge display with the real formula, fix stale `CLAUDE.md`.
2. **Finalize + clean the scoring model** — pick one canonical score, prune the 271-field mess to a clean set, make weights adjustable, enforce 12-month windows, drop dead inputs.
3. **Rework the data pipeline** — replace the manual local scraper with something hosted & scheduled (see §8).
4. **Add the new layer** — trend/velocity/recency fields for churn + an ideal-member view + weekly Slack reporting.

---

## 8. Data pipeline options — pros / cons

_Constraint: no local/laptop runner; off the table per Andy._

**Update 2026-06-02 (post-discussion):** FB group engagement is **scrape-only** — no first-party/API source (Meta closed the Groups API). The non-FB inputs (profile, photo, events, squads, chapters) already come first-party today (MDS App sync + rosters), so only the FB engagement signal actually needs scraping. The original Apify actor `sSX1L7hnaohLSWTdB` (account `comfortable_meal`) is **still scheduled daily but silently broken — 0 items for 30+ days** (succeeds while scraping nothing; no alerting). So "back to Apify" means **fix/rebuild + add zero-item alerting + wire output→Airtable**, not just reconnect. Leaning: Apify-hosted; prefer a maintained Store FB-group actor over the bespoke one if it yields per-member 90-day participation + #valueadd.

### Option A — Apify hosted actor (cloud Playwright, scheduled) → Airtable
- **Pros:** Fully cloud/scheduled; managed proxies + anti-bot; no machine to babysit; the old design already used an Apify actor so there's precedent; can keep the GPT structuring step.
- **Cons:** Per-run compute cost; FB DOM still breaks selectors periodically; private-group scraping is ToS-gray; GPT post-processing adds cost/latency.

### Option B — n8n-orchestrated + cloud headless browser (Browserless/Bright Data) → Airtable + Slack
- **Pros:** Andy already runs n8n heavily (lead pipeline, WA digest/approvals) — reuses infra, creds, and patterns; one place to orchestrate scrape → transform → Airtable → weekly Slack; full control over scheduling/retries.
- **Cons:** Need to bolt on a hosted browser node; still FB-brittle; more moving parts to maintain than a single managed actor.

### Option C — Reduce FB-scraping dependence; lean on first-party data (MDS App + events + WhatsApp)
- **Pros:** Durable and ToS-safe (no scraping of the brittle/risky source); aligns with the WA-subgroups direction; far less maintenance.
- **Cons:** Loses the FB engagement signal that is ~50% of today's score; requires WA data plumbing; a bigger product decision, not just an infra swap.

### Recommendation (for discussion, not yet decided)
A **hybrid: B + C.** Use n8n (already in Andy's stack, cloud, not local) to orchestrate a cloud headless-browser scrape of *just* the FB engagement signal we actually need, push to Airtable, and post the weekly Slack summary — while shifting everything that *can* come from first-party MDS App/event/WhatsApp data off of scraping entirely. This shrinks the fragile surface to the one signal that genuinely requires it and removes the local machine.

---

## 9. Open decisions for Andy

1. **Canonical score:** keep `Member's score NEW` (FB-dominant, max 107) or move to the category-balanced "fairness" model (each section = 25, max 100)?
2. **Dead inputs:** confirm we drop coffee/lunch, perks, vault from the formula until/unless a real data source exists.
3. **Pipeline:** A / B / C / hybrid (recommend B+C).
4. **Public exposure:** is the public scorecard staying public? (Drives whether we proxy the PAT vs. publish a sanitized snapshot, and what PII we must strip.)
5. **Scope/order:** which track in §7 do you want first?
