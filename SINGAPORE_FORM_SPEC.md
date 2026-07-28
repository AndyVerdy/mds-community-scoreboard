> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Summit Singapore 2026 — Prep/Check-In Form

**Date:** 2026-07-21 · **Requested by:** events team (via Andy) · **Reference:** Milan form by Alejandro
**Prototype:** `singapore-form/index.html` (this repo) · **Target host:** custom subdomain `singapore.mds.co`

---

## 1. How the Milan reference actually works (extracted from live site)

- **Platform:** Softr page on custom domain `events.milliondollarsellers.com`, form block → **Airtable**.
- **Airtable:** MDS Events base **`appYa7blqkHazLMYf`** → table **Check In Forms (`tblX1jjXE010ButSV`)**, 225 cols, shared across events. Each submission tagged by hidden field **`Events` = "MDS Summit Milan"**. Linked to Attendee List.
- **Member detection:** if visitor is a logged-in Softr user → hidden prefill `{LOGGED_IN_USER:Email/Full Name}` + `USER::Ticket Type - Single Select` drives branching (`Member` / `Guest` / `MDS Team` / `Business Guest` / `Partner`). Anonymous visitors self-declare via "I'm attending as a" (MDS Member / Guest) pill select.
- **Per-type chat links** (the answer to Courtney's WhatsApp question — Milan did it this way):
  - Member → Messenger group `m.me/j/Abbyxt5kkbToFuav`
  - Guest → **WhatsApp** invite `chat.whatsapp.com/F3F9DfEuV6JKGzxcg2EZbW`
  - Partner → MDS app channel `app.mds.co/channel/invite/67d2fd8a...`
- **Step flow (Milan):**
  1. **User access** — name/email (if not logged in), attending-as, per-type "Confirm your (Member) Access" block: Download MDS App link + confirm checkbox, Open Event Chat link + confirm checkbox
  2. **General** (everyone) — Hotel info (DOB, birth city/country, address, passport #/place/expiry, arrival time — *optional*, "expedite check-in at Hotel Principe di Savoia"), Event Topics (deep-dive topic*, top challenges*), Activities (top choice + 2nd/3rd, "Learn more" link)
  3. **Members** (members only) — Dining (seating pref, dine-around), Hack Contest checkbox, business/AI questions + conditional follow-ups (TikTok Shop revenue if Yes, creator tools if Yes, hot-seat topic unless "No")
  4. **Summit Prep** (members only) — Ecommerce Involvement gate → business deep-dive vs "What is your next venture?"
  5. **Partners** (members only) — partner 1:1 multi-select, partner focus-group multi-select
  6. **Agreements** (everyone) — link to combined **Event Liability Waiver / MDS Event NDA / Code of Ethics / Media Release** doc + acknowledgment dropdown (options auto-synced from AT `NDA` column) → Submit
  - Ending: "Thank you for submitting the form" → redirect `www.mds.co`
- **Guests skip steps 3–5** (routed General → Agreements).
- Milan's Arrival/Departure date fields exist but were **hidden behind a test condition** (visible only to alejandro@milliondollarsellers.com) — never live. Singapore wants them live.
- Extras on page: Intercom widget; reCAPTCHA off; validation = inline red "<label> is required".
- Full extraction: `scratchpad/MILAN_FORM_FULL.txt` + `milan_form_block.json` (raw config), `milan_at_schema.json` (AT schema).

## 2. Singapore form (built from the Google Doc "New Version" + comment decisions)

**Source:** [Singapore 2026 Summit Prep Questions doc](https://docs.google.com/document/d/1uxEmTHLaQ3GGdqjfl6Qt-ckDrR27gd59HkHWl0tRwtY/) — "New Version" section.
**Decisions from doc comments:** one conditional form, not two (Courtney); chat link conditional by ticket type (member vs guest WhatsApp); Rebeca checking who built last year's form → it was the Softr page above.

### Flow

| Step | Audience | Content |
|---|---|---|
| 1. Who you are | all | First Name*, Last Name*, Email*, Brand/website*, **Are you an MDS member?*** (Yes/No) → per-branch access block: Singapore **WhatsApp group** link (member vs guest link) + in-group? *, MDS app link + access? *, **NDA acknowledgment checkbox*** ([NDA doc](https://docs.google.com/document/d/14RpcITqmKRWlH1oIdsuL81lrSuGMJJsNjDJPUapWR3w/)) |
| 2. Travel & hotel | all | Arrival Date/Time*, Departure Date/Time*; optional **Ritz check-in block** (DOB, birth city/country, residence address, passport #/place/expiry, SG arrival time); non-attending room guests + names |
| 3. Topics & activities | all | Deep-dive topic*, top challenges*; activity 1st choice* + 2nd/3rd prefs* (Island Hoppers / Wellness / Rooftop Pool Bar / Chinatown Hawkers Tour / Vespa Sidecar / Lunch at JAAN); dinner-seating pref (guest ticket holders); dine-around placement (⚠ pending, see open Qs) |
| 4. Hack + your business | members | Hack contest Yes/No* → conditional "Submit your hack" textarea; MDS impact, AI tools, AI gains, new experiment, most-behind area, **2025 revenue***, **projected 2026***, **% Amazon/TikTok/DTC***, main niche |
| 5. 2026 → 2027 outlook | members | 2026 trend*, operating posture, biggest shift*, benchmark area*, least predictable*, decision input*, Q4 focus*, 2027 plan changes*, investing now, 2027 priority*, 2027 channels* (multi), pulling back*, confidence*, 2027 vs 2026*, team strategy*, biggest concern*, 3–5 yr vision* |
| 6. Partners | members | Partner 1:1 (15 min) + partner focus group (30–60 min breakfast) — **partner list TBD (Anita)** |
| 7. Agreements | all | Combined [waiver/NDA/ethics/media doc](https://docs.google.com/document/d/1u-pXf19g7dmjgnpjHq8z0TCtssCiNOQtEGiGXocDPXw/) + acknowledgment select* → Submit |

Guests: 1 → 2 → 3 → 7. Members: all steps.

### AT sync plan (after form verification)
- Same pattern as Milan: rows into **Check In Forms** table, `Events` = `"MDS Summit Singapore"`, `Ticket For`/ticket type column, link to Attendee List. **Awaiting the AT link from the requester to confirm target** (their message's AT link didn't come through).
- Prototype already emits a flat `{AT column: value}` payload (see `buildPayload()` in index.html) — wiring = one n8n webhook → Airtable create (or Softr if rebuilt there).

## 3. Open questions before launch
1. **Dine-around question is stale** — no vegan restaurant this time (Rebeca comment); Eugene may want assigned seating logic. Keep/drop/reword?
2. **Partner list** for step 6 — waiting on Anita.
3. **Singapore WhatsApp links** — need member + guest invite links (Milan used Messenger for members; doc says WhatsApp for Singapore).
4. **Brand/website for guests** — doc marks it required for everyone; keep required for guests too, or optional?
5. Revenue brackets dropped `< $1M` in New Version — intentional?
6. Event dates + banner artwork for header (and og-image) — Andy's Claude design pass.
7. Hosting/AT confirmation: custom build on `singapore.mds.co` (prototype path) — submissions via webhook (n8n) into the Events base. Confirm base/table with the requester's AT link.

## 4. Prototype notes (`singapore-form/index.html`)
- Single-file, zero dependencies, config-driven (`FORM` array — steps → fields; edit questions there).
- Mobile-first (100% width card <640px, 48px touch targets, `inputmode` numeric keyboards, native date/time pickers), Milan-style pill selects, inline validation + scroll-to-error, dynamic "Step X of Y" per branch.
- Submit: `ENDPOINT` const at top of the script — empty = demo mode (shows payload for QA). Point it at an n8n webhook to go live.
- TODO placeholders marked `⚠ TODO` in config: WhatsApp links, partner list, activities info link, banner.
