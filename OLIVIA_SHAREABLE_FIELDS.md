> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia — the shareable-fields rulebook (#10)

**The one written list of what may be said about a member. Ruled by Andy 2026-08-01.**
Principle first: **default-deny.** Olivia reaches data only through the ~20 gated functions, and
each emits a fixed, named column set. Anything not on this page (address, payment/Stripe data,
IP, government ID, the other ~1,700 AT fields) is NEVER-BY-CONSTRUCTION — no function selects
it, so it cannot leave the database. The gate enforces the emitted sets and probes the scary
names as canaries.

**"Used" ≠ "shareable."** A field may feed calculations while being unspeakable per person —
`Most Recent Revenue` computes the band and the chapter sums but is emitted nowhere per member.

## 🟢 SHARE — fine about a named member (the public card)
name · city · state · country · **revenue BAND only** (1-5M / 5-10M / 10-20M / 20M+) ·
main niche + niches · area of expertise · about-me · hobbies · fun fact · Facebook link ·
chapter(s) · membership state (current/past — reason never) · join date · left date (past
members) · **sales channels** (Amazon US/CA/EU/Other, DTC, Walmart, Wayfair, Wholesale, TikTok
Shop) · **business model** (Private Label / OEM / Agency / Wholesale) · **product categories** ·
shared chats (always relative to the ASKER's own chats) · chapter-lead role + photo (public on
mds.co) · anything the member posted publicly in the group (verbatim content, attributed).

## 🟡 GROUP-ONLY — aggregates fine, never about one person
employee counts · SKU counts · brands count · years in business · age / age bands · TTM revenue
sums + averages · country mixes · band mixes · niche counts. (These live in `chapter_info.
live_stats` and `member_count` breakdowns; a small chapter's sum can still out a whale — Andy's
4b ruling stands open.)

## 🔴 NEVER — not about anyone, not to anyone, no phrasing
exact revenue figures per member **from OUR data** *(#12 nuance, Andy 2026-08-01: a figure the
member or the MDS page POSTED in content the asker can see — FB is fully open; WA follows chat
visibility, which retrieval enforces structurally — IS quotable, but ONLY as an attributed
quote with its link, paired with our band, never in Olivia's own voice, never as ranking fuel)* · job titles · email · phone · home/business address · payment,
card, bank, Stripe records · IP or device data · government IDs · membership-removal reasons ·
internal admin fields (event budgets, member LTV, lead scoring) · another member's persona,
billing, dossier, census/application raw answers · anything from a chat the asker is not in.
Self-exception: a member may see their OWN billing, dossier, application answers (self-only
functions, fail-closed).

## 🟠 TEAM MODE (#172) — staff only, behind the disclaimer, never reachable from WhatsApp

**Drafted 2026-09-10 from the live migration (`scripts/sql/20260911_team_sql_172.sql`); it becomes
the ruling when Andy signs it (design §9, item 2).** Team mode does not use the gated functions. It
reads through ONE read-only SQL surface — `digest.team_sql`, run as the NOLOGIN role `millie_team_ro` —
over every table and view in `digest` + `event`, so the deny-list is written as SQL, not prose:

| | Team mode |
|---|---|
| **OPENS** (the three categories #172 names) | exact revenue per member (`Most Recent Revenue`, TTM figures, bands) · contact details (email, phone, WhatsApp keys) · Stripe/billing (`stripe_customer_id`, `subscription_status`, `mrr`, `next_renewal_amount`, lifetime paid). **Open by omission** (nothing closes it): every other `at_fields` key, address keys included · all WhatsApp messages of every chat · call transcripts · FB content · event rosters · partner terms. |
| **CLOSED by the view** `digest.member_profiles_team` (the role never reads `member_profiles` itself) | every `at_fields` key matching `removal · reason · ltv · score card · member score · notes · lead scor · budget` — live 2026-09-10: 29 keys, among them `Removal Reason`, `Removal Reason Code`, `Final Reason`, `Initial Reason Code`, the three `Member LTV (…)`, `Member Score`, `Member Score from scorecard`, `Score Card at time of removal`, `Staff Notes`, `Chapter Notes`, `Interview Notes`, `2nd Interview Notes`, `Notes from Tina`, `Internal Notes (Onboarding)`, `Discovery Call Notes (Onboarding)`, `Referral Related Notes`, `Notes about Lead (…)`. |
| **CLOSED by grants** (no privilege at all, 42501) | `members.otp_code_hash` · `members.delivery_otp_hash` · `member_sessions.token_hash` · `olivia_web_messages` (other askers' Team answers) · `vault`, `auth`, `storage` · every secret-returning function (`meta_webhook_config`, `health_report_secret`, …) · **all writes** (read-only transaction, 25006) · outbound HTTP (`net.http_*`). |
| **Over-blocked by the regex — Andy's call** | `Member Removal Reconciliation Date` (+ `- YYMM`), `Member Removal/Applied Consolidated Date - Year`, `Days of Membership (From Payment to Removal)`, `Typeform Removal Link`, `Referred by from call notes` — dates and links, not reasons. Opening them = loosening the regex in the migration AND the gate, same commit. |

Enforcement: `scripts/test_172_team_sql.py` (17 live checks through PostgREST) + the `#172` section of
the leak gate. The WhatsApp, member and Public paths gain nothing: `team_sql` is `service_role`-only and
the research route accepts only the staff cookie; no n8n node and no gated function changes.

## Enforcement
- The gate (`scripts/olivia_leak_gate.py`) pins `member_card`'s exact column set to this page
  and probes canary names (address / credit / stripe / ip / email / phone keys) across outputs.
- Consistency AC: the same field asked about different members answers or refuses identically.
- Change process: edit THIS page + the gate check in the same commit, or the gate goes RED.
