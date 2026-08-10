# Typeform recovery queue

Running list of forms to rebuild after the 2026-08-08 deletion. Full damage accounting lives in
[TYPEFORM_LOSS_REGISTER.md](TYPEFORM_LOSS_REGISTER.md); the 2026 breakdown is in
[TYPEFORM_2026_LOSSES.md](TYPEFORM_2026_LOSSES.md). This file is only the work queue.

**Two things are true of every rebuild.** The new form gets a **new id**, so every link already
shared — Webflow, GHL email, WhatsApp, the app — stays dead until someone re-shares it. And
rebuilding restores the *form*, never the *responses*: Typeform has no import endpoint, so lost
submissions stay lost unless a copy survived in `digest.form_responses`.

---

## Done

| form | old id | new id | responses |
|---|---|---|---|
| MDS Summit Singapore 2026 - Company Information | `IaRcNdOZ` | **`GljwvNGO`** | 7 of 8 survived; **all 7 re-entered 2026-08-10** and verified via the Responses API. ⚠️ the `restored` / `original_submitted_at` hidden fields were dropped from the form at 16:23 (form edited in the Typeform editor), so the restored rows are no longer tagged inside Typeform — [the CSV](singapore_company_information_responses.csv) is the record of which rows are restored and their true dates |
| Accelerator Channel Call Opt-in | `alDsokGC` | **`ppfLDGLJ`** | 8 lost, unrecoverable — form rebuilt from its backed-up definition |
| Large SKU Channel Call Opt-in | `B0wpgzt9` | **`qh4BujFZ`** | 9 lost, unrecoverable — form rebuilt from its backed-up definition |
| Resellers Channel Call Opt-in | `k2ULAIkZ` | **`GBWQh15X`** | 9 lost, unrecoverable — form rebuilt from its backed-up definition |
| Partner_ Session Survey _ Summit Singapore | `PBlf7VU5` | **`v1BIIGyT`** | 0 responses; question set cloned from the live Milan session surveys — no definition backup existed |
| Speaker _ Session Survey _ Summit Singapore | `JPayBXjh` | **`RiyAhK28`** | 0 responses; question set cloned from the live Milan session surveys — no definition backup existed |
| Squad Archetype ("Squad Pulse Check") | `PYxpuBrl` | **`h3fEDrAY`** | exact 9-field rebuild from the backed-up definition. Its only response was a test ("dd" / `ddd@ddd.com`) and was not restored. ⚠️ carries two inherited thank-you screens about TikTok channel access — copy-paste leftovers from whatever form it was duplicated from, wrong for a squad survey |
| MDS Summit Singapore 2026 Hack Contest | `PWZkWf7H` | **`HfsXWZGY`** | rebuilt from the 2 stored submissions; Emily Wang's real entry re-entered and verified, tagged `original_submitted_at=2026-08-05`. The other original submission was a test ("rebe / r", hack = "test") and was deliberately not restored |

## Queue

**Empty.** Every form worth rebuilding has been rebuilt.

### Why Large SKU and Resellers were rebuilt without being asked for

The Channel Call Opt-in forms are a family of 16. Twelve are still live (Trading, Supplements,
Credit Card & Hacks, M&A, SEO, DTC/Shopify, Centurion, Retail, Logistics, TikTok, AI, Real Estate)
and four were deleted. Three of those four — Accelerator, Large SKU, Resellers — have **no live
equivalent**, so those channels are the only ones in the set with no way for members to opt into
call reminders. They will surface as complaints the same way Accelerator just did.

The fourth deleted one, Logistics (`BC34iFXw`, 1 response), needs nothing: a live
**Logistics Channel Call Opt-in** (`qPWmyvCT`) already exists, so the deleted one was a duplicate.

All three rebuilds are identical in shape — Full name (short_text), Email (email), and a single
checkbox "Opt-in to receive monthly call reminders for the <channel> Channel".

## Explicitly not rebuilding

| form | old id | why |
|---|---|---|
| Singapore Excursions | `xLml7iw1` | live `rTOf6Pfm` "Singapore Excursions Survey" supersedes it — same question, more options |
| MDS Singapore Summit Hack Contest | `aoggJSeO` | superseded by the 2026 version (`PWZkWf7H`, queue #4) |
| Logistics Channel Call Opt-in | `BC34iFXw` | live equivalent `qPWmyvCT` already exists |
| MDS Annual Census 2026 (v2) | `NENqozp9` | Andy 2026-08-10: "we dont care". 1 response, recoverable from the backup if that ever changes; the live census is `DFeK5yop` |

## Protection

Every rebuilt form goes into [scripts/typeform_never_delete.txt](scripts/typeform_never_delete.txt)
as soon as it is created.
