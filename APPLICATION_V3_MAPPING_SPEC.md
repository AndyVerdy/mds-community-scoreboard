> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS New Member Application v3 — Make Remap (FINAL / applied spec)

**Typeform `FsVHzNN9` → Make scenario `4784286` (us1) module 2 → Airtable Forms `tblblwPcgqhkPTVec` (base `appou5JVr0WIrioWS`).**  
Regenerated 2026-07-01 from live form + mutated blueprint. Module 2 record: **71 mapped fields**.

## Members-table join key
- **M4** searches Members `tblfwOSROSHfuYUxv` by `{Preferred Email} = {{2.Email}}` (the Forms row's Email).
- **M6** links the new Form to that Member; **M7** updates 10 Member fields directly; Members lookups/rollups pull the rest from the linked Forms row.
- ⚠️ **Email vs Preferred Email:** the join needs Forms `Email` == Members `Preferred Email` exactly. New-member records with no matching Preferred Email won't link — verify in the Members-lookup pass.

## Change set applied (staged)
| # | AT field | Type | Action | Source (TF question) |
|---|---|---|---|---|
| 1 | Tiktok % of Revenue | multipleSelects | 🔁 bracket → legacy range | (NEW) What percentage of your revenue comes from |
| 2 | DTC % of Revenue | multipleSelects | 🔁 bracket → legacy range | (NEW) What percentage of your revenue comes from |
| 3 | Business Partner/Employee | checkbox | 🔧 FIX checkbox | Is your business partner already an MDS member,  |
| 4 | Retail % of Revenue | multipleSelects | 🔁 bracket → legacy range | (NEW) What percentage of your revenue comes from |
| 5 | Amazon US & % of Revenue | multipleSelects | 🔁 bracket → legacy range | (NEW) What percentage of your revenue comes from |
| 6 | (NEW) Amazon % (raw) | number | 🆕 ADD | (NEW) What percentage of your revenue comes from |
| 7 | (NEW) Amazon Marketplaces | multipleSelects | 🆕 ADD | (NEW) Which Amazon marketplaces do you sell on?* |
| 8 | (NEW) Other Sales Channels | multipleSelects | 🆕 ADD | (NEW) What other channels do you sell on?* |
| 9 | (NEW) DTC % (raw) | number | 🆕 ADD | (NEW) What percentage of your revenue comes from |
| 10 | (NEW) DTC / Shopify Link | url | 🆕 ADD | (MOVED) What's your DTC / Shopify store link?* |
| 11 | (NEW) TikTok % (raw) | number | 🆕 ADD | (NEW) What percentage of your revenue comes from |
| 12 | (NEW) TikTok Shop Link | url | 🆕 ADD | (NEW) What's the link to your TikTok shop?* |
| 13 | (NEW) Retail % (raw) | number | 🆕 ADD | (NEW) What percentage of your revenue comes from |
| 14 | (NEW) Unverified Revenue | currency | 🆕 revenue → Unverified | What was your total revenue over the past 12 mon |

**Removed (orphaned):** `Total TTM Revenue` (revenue now → Unverified Revenue only), `Sell Brand?` (plan-to-sell deleted), `sell on other marketplaces?` (question deleted).

## Bracket formula (raw % → legacy range option)
```
{{if(A=""; ""; if(A=0; "N/A"; if(A<=5; "<5%"; if(A<=15; "6-15%";
   if(A<=25; "16%-25%"; if(A<=50; "26%-50%"; "51%"))))))}}   where A = the raw % answer
```
Emits only the 6 canonical options `[N/A, <5%, 6-15%, 16%-25%, 26%-50%, 51%]` — keeps Members lookups fed with real data while the true % lands in the `(NEW) … % (raw)` fields. (Legacy range fields still carry junk options from earlier bad typecasts — cosmetic, prune later.)

## Revenue → human verification (Centurion-style, not auto-trusted)
- Self-reported total revenue → **`(NEW) Unverified Revenue`** only. `Total TTM Revenue` (feeds trusted `Most Recent Revenue`) stays **empty** until an admin approves.
- Verification flow (mds-digest-web, TO BUILD): Claude-vision reads `Verify Your Sales` screenshot → Slack card + HMAC link button → on approve write verified $ to `Total TTM Revenue` + set `(NEW) Revenue Verified By/At/Status/Notes`.

## Fixes
- **Second-seat → `Business Partner/Employee` checkbox:** `{{if(substring(<second-seat>;0;3)="Yes"; true; false)}}` — checked only for the two "Yes…" answers (was: any non-empty = checked).
- **Purchased/Sold** are `yes_no` booleans → checkbox; flow correctly, left as-is (confirm in test run).

## Status
- ✅ 15 new AT fields created, `(NEW)`-prefixed + described; all 77 Forms fields have descriptions.
- ✅ New blueprint built + validated locally (71 keys); all 11 source refs verified present in live form.
- ⏳ **Apply blocked:** Make REST token is read-only (`scenarios:write` missing). Ready to fire via `curl -d @patch_body.json` once a write-scoped token exists.
- ⬜ Revenue verification flow (mds-digest-web).  ⬜ Members lookups for the new fields (UI-only).
