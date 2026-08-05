> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Olivia — FRESH EVAL LIST (organic sweep, 2026-08-04)

Built from the **live conversation log since 2026-07-28** — every 👎, every report, and every
real member ask not already in the bank. **Nothing authored.** Ids **3140–3173** (34 questions),
added to `eval_bank_organic.json` (100 → 134) and `eval_bank_smoke.json` (178 → 212) — then **retirement cut the fired set to 110** (see below).

## What the sweep found

**Reactions (uncleared):** 5 👎 · 4 👍. Every 👎 is now a banked question.
**Reports filed by real members:** Etienne ×2 (Cyprus members, MDS credit) — both now shipped.
**Real askers since 07-28:** Eugene 37 · Etienne 14 · Ian 9 · Kayleigh 8 · Belén 5 · Sam 4 ·
Morris 4 · Adam 4 · then a tail of 1–3 each.
**Already banked:** 14 of the 48 candidate asks. **Unbanked → added: 34.**

## THE REPORTED ONES (Ian + Eugene, Slack today) — every run must include these

| id | asker | question | proves |
|---|---|---|---|
| 3140 | Ian | What are the most reviewed partners in the MDS database? | #56 — true top 5 (Helium 10 82), not a sample |
| 3141 | Ian | *"That doesn't sound right. I know JoinBrands has way more reviews"* | #56 — corrects the assertion, never adopts it |
| 3142 | Ian | Can't you just sort the entire directory and give me the top five? | #56 — no "can't sort" hedge |
| 3143→3144 | Eugene | Best lenders in our portal? → **"How about based on mentions in Facebook?"** | **#52 — THE 👎.** Must stay on lenders |
| 3145 | Etienne | How much MDS credit do I have? | #55 — real balance, no "overpaid" |
| 3146→3147 | Etienne | Members based in Cyprus? → who is the 5th one? | #54 — names them; #53 — no canned clamp |
| 3148 | Etienne | FB profile links for Larnaka/Limassol members | #54 |

## The other 👎s (all four now banked)

3149 Eugene *TikTok account went down, who can help* · 3150 Eugene *"I thought I was in that chat
already"* (never argue past a member — offer the ticket) · 3151 Etienne *"I DID answer to a few
post…"* (find his own comments) · 3152 Kayleigh *MDS Life access + wellness tips*.

## New organic coverage (3153–3173)

Pressure-holding (Feedvisor ×2) · attribution (Euka/Brandon, Khalid's hiring post) · solve-lane
(ASIN merging, cost segregation, Shopify CRO, supply-chain director, off-niche travel funnel) ·
partners (Kalo Data, Accelerate promo code) · events (2027 announcement — no reminder capability)
· self (own FB history) · capabilities ("Hi Millie") · sensitive (credit-card info refusal) ·
general (top-10 tips, what's new today, lunch reimbursement policy).

## Truths

Verified truths are written in for the shipped classes (partner leaderboard, credit balances,
Cyprus roster, JoinBrands rank). Rows whose truth needs a live check say **"verify at run"** in
the `truth` field rather than carrying a guess — fill them from the run's own retrieval, never
from memory.

## Multi-turn rows (cannot survive the auto-reset)

3141 · 3144 · 3147 · 3150 · 3151 · 3154 · 3162 — fire these by hand right after the auto run,
in their pairs, the way the member actually asked them.

## RETIREMENT — the bank now shrinks as well as grows

**Andy 2026-08-04: "are you even removing questions that are working well?"** He was right: the
retirement rule existed in the routine doc but had **no mechanism** — nothing anywhere recorded
per-question pass history, so the bank only ever grew (212 and climbing).

Fixed in three parts:
1. **Reconstructed the history** from 45 judged reports — 74 current-generation questions have
   failed or partialed at least once; everything else has been clean every time it fired.
2. **Retired the clean ones** (`retired: true` in the bank — kept in the file for history and
   rotate-back-in, never fired). **Smoke fired set 212 → 110. Organic 134 → 96.**
3. **Canary floor of 3 per class** — retirement emptied SMOKE/ATTRIBUTION and SMOKE/REPORTS and
   left SENSITIVE at 1; those are catastrophic-class guards, so 7 clean questions were restored
   as explicit canaries. No class is traded for another.

`olivia_eval.py` now fires **non-retired only**; `OLIVIA_EVAL_ALL=1` fires everything for a
regression sweep. Verified: default 110 · ALL 212.

**What the fired 110 is made of:** every question that ever failed (they stay until 3 consecutive
clean passes) + the 34 new organics + the per-class canaries. Backups: `*.bak-preretire-0804`.

## Status

**List built and STORED; the RUN waits for SPRINT COMPLETION** (Andy 2026-08-04: "big smoke
after sprint completion"). Snapshots live in `eval_bank_snapshots/`. The run is Andy's call — standing tier: eval runs = propose + wait.
Prod is `01a94c1a` with nine tickets live, so this run doubles as the post-promote check on
#52 · #53 · #51 · #54 · #55 · #56 · #29 · #50 · #38.
