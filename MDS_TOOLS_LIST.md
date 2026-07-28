> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Tools — Master List (by builder)

> Live scan of n8n + Make + ClickUp + local repos, 2026-06-13. Make builder = verified via Make API `createdByUser`. n8n has no per-workflow creator API, but all n8n tools are your team's (confirmed by you + project docs).
> **Status:** 🟢 live · ⚠️ at-risk/partial · 🔴 broken/dead · ⏸ parked · ❓ unclear · Add your links in the right column.

---

# 🔵 BUILT BY YOU (Andy's team) — own + maintain

## n8n workflows (all yours)
### WhatsApp
| # | Tool | Runs on / ref | Status | CU doc | Link |
|---|---|---|---|---|---|
| 1 | WA Digest — Weekly | n8n `vsj4CxGBv7FgNmKA` | 🟢 | 97677 | |
| 2 | WA Digest — Daily | n8n `qo3qzeVtprhTW88F` | ⏸ parked | 97677 | |
| 3 | WA Whapi Sync | n8n `Lo45BM43boK1gM19` | 🟢 | 97677 | |
| 4 | WA Daily Stats | n8n `1VDbwlQqXcfbotic` | 🟢 | 97677 | |
| 5 | WA Approvals (+ Centurion) | n8n `ib7g9bBddhzCbj4X`, `wb9TrAL1ZdqxGbpC` + `mds-digest-web` | 🟢 | 97737 | |
| 6 | WA Approvals Bot Reports | n8n `w2zpT1dI3jt9dqF3`, `prgV70vX88cLG0QL` | 🟢 | 97737 | |
| 7 | WA Engagement Triage | n8n `4B79OVfyT2a9a3Xt` + `v9D1bROMGMivfXH2` (**not activated**) | ⚠️ | 97777 | |
| 8 | WA Error Notifier | n8n `CPPKMDdutZMF1J9V` | 🟢 | — | |

### Members / Events / Leads / Revenue
| # | Tool | Runs on / ref | Status | CU doc | Link |
|---|---|---|---|---|---|
| 9 | Intercom ⇄ Airtable | Render cron `crn-d8m2ji0g4nts7380p690`, repo `mds-intercom-lastseen-sync` | ⚠️ status leg pending | 100837 | |
| 10 | Members Deletion Trap | n8n `5pX4uCt1VFFoT641`, `s9DRiuBwjRHKGNyT` | 🟢 | — | |
| 11 | $500 Event Credit | n8n `eysq1oXPwcTXhJKM`, `qbDK69qc33QKqVZG` | ⚠️ awaits Tina | 100677 | |
| 12 | Ecompreneur Luma → Webflow | n8n `Mc2Av5YXn49R65V0` | ⚠️ page unpublished | 98597 | |
| 13 | Event / Guest syncs | n8n `9ix1Ch5043T4ULyU`, `mmmIsZwU9PyPkAd9` | 🟢 | — | |
| 14 | Lead Enrichment | n8n WF1/2/3 `BFrSqQ8Cp0KfbLIH`, `NyTauh9UtG8YMbja`, `hpIIQpgIUlmTJJZ0` | 🟢 | 97957 | |
| 15 | MRR / Stripe → Airtable (n8n side) | n8n `30OyMumvZsQIAMo8`, `m94lQxcXACs6rFJx` | 🟢 | 100897 | |
| 16 | Onboarding Slack Observer | n8n `IPTLQHFTPpdplueT` | 🔴 Airtable 429, 3/5 fail | 100897 | |

## Your Make.com scenarios (11 — the only Make ones that are yours)
| # | Scenario | ID | Status | Link |
|---|---|---|---|---|
| 17 | Stripe → AT: Subscription Update Sync | 4472150 | 🟢 | |
| 18 | AT > Stripe > AT (sub-ID change) | 4470634 | 🟢 | |
| 19 | AT > Stripe (Name & Email Update) | 4474639 | 🟢 | |
| 20 | Luma Manual Add Alert | 4688319 | 🟢 (doc 97537) | |
| 21 | Slack Action → Luma Approve/Decline | 4676523 | 🟢 | |
| 22 | Guest Multi-Event Alert ("3+ events" — alerts when a non-member registers for their 3rd+ Ecom event) | 4676457 | 🟢 | |
| 23 | All Access Dinner → Slack | 4595577 | 🟢 | |
| 24 | Conference Pass Upgrade → Slack | 4593806 | 🟢 | |
| 25 | Honorary Member — Open Modal via Slack | 4623773 | 🟢 | |
| 26 | Honorary Member — Process Modal Submission | 4623920 | 🟢 | |
| 27 | Integration Webhooks, Intercom | 4533507 | 🟢 | |

## Your apps / services (repos)
| # | Tool | Runs on / ref | Status | CU doc | Link |
|---|---|---|---|---|---|
| 28 | Skill Base | Vercel `mds-skill-base` (skills.mds.co) | 🟢 | 100637 | |
| 29 | Scorecard | AT `appUM1F29IJsMsXRb`; repo `mds-community-scoreboard` (GitHub Pages) | 🟢 | 100317 | |
| 30 | Video Platform | `mds-video-admin` (Vercel), `mds-ai-bot` (Render), `mds-ios-app` | ⚠️ Mux env | 98637 | |
| 31 | MDS AI Bot | repo `mds-ai-bot`, Render (Flask RAG) | 🟢 | — | |
| 32 | mds-digest-web | Vercel, repo `mds-digest-web` | 🟢 | — | |
| 33 | **FB Engagement processor** | **Local Mac launchd** `com.mds.scorecard.autoimport`, repo `mds-scorecard-tools` | ⚠️ alive (6/08 OK) but fragile, manual, no alerting | — | |
| 34 | FB Group Roster scraper | repo `mds-fb-group-members` (Apify) | ❓ FB-ban risk; confirm running | — | |
| 35 | mds-admin-pages | repo `mds-admin-pages` (React/Vite) | ❓ stale since Feb — still used? | — | |

---

# ⚪ BUILT BY SOMEONE ELSE

## Carmel (MDS) — Make.com, 22 active (event ops + member comms)
Notable: **Welcome Box** `4627502` 🔴 · **New Member Intro to Chapter Lead** `4717952` ⚠️ · **Honorary member form sync to AT** `4748779` 🟢 · Event Registration Extension `3936323` · Event Roster Match to Member `4270329` · Event Update to Slack `4362970` · Inspire 2026 Check-In `4562829` · MDS Squad registration (free/paid) `4523893`/`4526846` · rooming-list syncs `4108059`/`4204544` · Partner referral/ClickUp→AT `4585140`/`4764608` · Luma→beehiiv `4471880` · + others.

## Eugene Khayman (MDS) — Make.com, 20 active (platform / core / legacy)
Notable: **MDS App Profile Updates** `4221663` · **Event Registration MDS App** `4192825` · **GoHighLevel LeadConnector → AT** `4088035` · Subscription Payment `4174898` · Membership Invoice (Gmail) `3661014` · Integration Airtable↔MongoDB (GroupOS) `3615768` · Error Log Creation `2663661` · FB Leads → beehiiv `4389411` · **Execute FB Group AI Agent** `3999830` 🔴 (0 runs) · **Apify FB Data scraper** `3999804` (idle) · + others.

## Legacy Make (no creator on record — Carmel/Eugene maintain), 8 active
Wild Apricot → AT contacts `364050` ⚠️ (DLQ) · WA → AT registrants `364051` · WA → AT invoices/payments `364048`/`364049` · Airtable → Wild Apricot `2843611` · Auth0 Member Migration `2835622` · GHL warm leads `2321341`.

## GroupOS dev team (internal, separate team)
GroupOS platform + `groupos` MCP — you QA it, don't maintain it. Known data bugs: `price_cents` holds dollars, `last_seen_at` unreliable, comet_chat mojibake.

## External developer
`otter-download` — Otter.ai transcript fetcher (feeds AI Bot) — built by Nick (`TechNickAI`).

## Vendor / SaaS dependencies (you build on these)
Whapi · Intercom · Stripe · Wild Apricot · GoHighLevel · Mux · AssemblyAI · Apify · Webflow · Typeform · Resend · Luma · Apollo · Supabase · Render · Vercel · Airtable · Slack · ClickUp

## Not member tools — GroupOS sales collateral (yours, separate purpose)
Demo sites/decks: `groupos-sales`, `groupos-david-ghiyam`, `groupos-deck-content`, `groupos-eo-sandiego`, `groupos-founders-club`, `groupos-hampton`.

---

## Dead / cruft (cleanup, not the dashboard)
- Make "FB Group AI Agent" `3999830` (Eugene) — 0 executions ever (NOT the FB engagement source — #33 is)
- n8n: `My workflow 2` (active, does nothing), `My workflow`, `TEMP Diag`, 2× Partner Deliverables stubs, ~7 archived legacy workflows
- Make: ~101 inactive scenarios (duplicate/retired clutter, mostly Eugene-era)
