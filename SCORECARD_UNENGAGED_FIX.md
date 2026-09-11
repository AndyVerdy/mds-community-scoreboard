> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# "Unengaged" is wrong in two different places — ClickUp `86e37cjc5`

Belen reported three things on 2026-09-11. All three are real, and they are **three separate
breaks**, not one. Measured live the same day.

---

## 1. The Airtable field reads a table that died in November

`Members & Scorecard` → **`FB Group 90 Day Post Score`** (`fldR66HCZ7ynqGEyz`) is
`MIN(20, {Accumulative Groups 90 Day Posts} × 4)`. That input sums three rollups — *Amazon /
Investments / Shopify 90 Day Posts* — and **all three roll up the same dead table**,
`Facebook Group Weekly Metrics` (`tblckOTP8UkC6K8Xr`), whose newest row is **2025-11-15**.

So the field is 0 for every member, and the **"Unengaged 90 days" view (`viwywSN4BSgunz2Ts`)
holds 176 people, all scored 0**. Of those 176, **17 posted or commented in the MDS group in
the last 28 days** — Dan Wills among them (8 posts, 10 comments, 15 reactions, scraped
2026-09-10, in `FB Engagement (NEW)` `tblVc38gw21iHLYMG`). Exactly Belen's example.

**Needs a decision from you — an Airtable change, so I have not touched it.** There is no live
90-day count anywhere: the scraper captures a 28-day window and `FB Engagement History (NEW)`
only stores `28d` snapshots. Three options, my pick first:

1. **Retire the field and rebuild the view on the 28-day signal** (`Posts 28d (FB)` +
   `Comments 28d (FB)` on the spine). Honest, live today, no new plumbing.
2. Sum ~3 consecutive `28d` history snapshots into a 90-day figure. Approximate, and the
   history only goes back to 2026-06.
3. Add a 90-day window to the Chrome-extension capture. Real 90-day data, most work.

Whichever you pick, the three `… 90 Day Posts` rollups on `Members & Scorecard` are pointed at
a table nothing writes to and should be retired with it.

---

## 2. Digest score 0 — one blank join key, 68 members — **FIXED, awaiting your apply**

The digest mirrors Airtable faithfully (`scripts/backfill_member_profiles.py` copies
`Engagement Score` off `Member Scorecard (NEW)` by email), so the bug is upstream of it.

The three weekly n8n layer syncs — Events `uuXBxG6lqXCV9otJ`, WhatsApp `RPfnori7C26NcT9N`,
Member Attributes `odfBrs6z9IxP7ndl` — find a member's Members-DB record by **regex-pulling the
rec id out of the spine's `MDS Member URL` text field**. They have to: the spine's `Member` link
points at the *synced mirror*, whose record ids are its own and carry nothing of the source.

`reconcile.py` created spine rows with only the mirror link and the name, so the key stayed
blank and all three syncs wrote 0.

| Measure | Live 2026-09-11 |
|---|---|
| Spine rows | 1350 |
| Blank `MDS Member URL` | 68 |
| Of those, Engagement Score 0 | **68 of 68** |
| Blank rows that are New Members | 40 |

**Shipped** (`~/mds-scorecard-tools`, commit `066e9bf`, 11 unit tests, 126 green): `reconcile.py`
section **A2** resolves the Members-DB record from the mirror row (unique email, else unique
name), fills the key on existing rows *and* on rows it creates, and **reports ambiguous rows
instead of guessing**. Dry run: 68 blank → **62 resolved, 6 unresolved**.

The 6 are all duplicate member records, for ops not for code: two "Andy Delete Me" rows,
**Justin Cao** and **Brian Williams** (name on 2 and 5 Members-DB records),
**Christopher Hytry Derrington** and **Adrian Markus** (email on 2 records each).

**Your one command** — I do not write to Airtable:

```bash
cd ~/mds-scorecard-tools && python3 reconcile.py --apply
```

That run writes 62 `MDS Member URL` values and nothing else (spine +0, FB rows +0, link
backfill 0, links 0 in the dry run). The Monday 01:30–02:30 CST syncs then score them.

## 3. Summit attendance — same blank key, and it is proven to clear

Belen is right that Ginny Lo, Omer Ege and Tamkin Collins attended. The registrations are in the
roster and **Confirmed**. Replaying the Events sync's own window maths against the live roster
with the key filled in (read-only, no writes):

| Member | In-Person events that would land, last 3 months |
|---|---|
| Ginny Lo | 3 — Summit Singapore, Women's Lunch, TikTok Mastermind |
| Omer Ege | 1 — Summit Singapore |
| Tamkin Collins | 6 — incl. Summit, Women's Lunch, Night Out, TikTok Mastermind |

The same blank key is why their `Profile % Complete`, `Years a Member`, `In Squad`, `App Active`
and **`MoM/MVP count`** all read 0 — which is why Tamkin's MVP scores nothing.

---

## Flagged, not fixed — belongs to `FB_BACKLOG.md` #1

**88 of 808 `FB Engagement (NEW)` rows carry no `Member Scorecard (NEW)` link**, so their
Facebook numbers never reach the spine. Six of them posted in the last 28 days: Mouad Errafik,
Ginny Lo, Tamkin Amin Collins, **Dan Wills**, Ivan Ong, Chris Kjeldsen. Dan Wills and Ivan Ong
are rows 1 and 2 of #1's table, so this is that ticket, not a new one. Until it is done, Dan
Wills scores 0 on the Facebook pillar even after the fix above.
