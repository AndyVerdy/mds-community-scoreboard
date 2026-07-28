> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Tools — Health Inventory

> Scan date: **2026-06-13**. Sources: live n8n API (`mdsco.app.n8n.cloud`), live Make.com API (org *Million Dollar Sellers* 258972 / team *MDS* 103111), and the 12 ClickUp source-of-truth docs. Read-only scan — nothing was modified.

## TL;DR
- **n8n:** 45 workflows — 28 active, 17 inactive (8 archived).
- **Make.com:** 162 scenarios — 61 active, 101 inactive (heavy duplicate/retired clutter).
- **You listed 11 tools; there are ~25 live automations** across n8n + Make + Render + Vercel.
- **Broken right now:** 3 (n8n Onboarding Observer, Make Welcome Box, Make Wild-Apricot DLQ).
- **Half-deployed:** 4 (Intercom status leg, WA Engagement Sync, $500 credit crediting, Video Mux env).
- **Monitoring is fragmented** — only the WhatsApp family has a real error-notifier. Scorecard, Video, Luma→Webflow, MRR have no runtime alerting. This is exactly why a single health view is worth building.

---

## 1. Master tool inventory (live automations)

| Tool | Doc | Platform + key IDs | Schedule | Status | Health alerting |
|---|---|---|---|---|---|
| **WhatsApp Digest (daily/weekly)** | 97677 | n8n Daily `qo3qzeVtprhTW88F` *(currently INACTIVE/parked)*, Weekly `vsj4CxGBv7FgNmKA`, Whapi Sync `Lo45BM43boK1gM19`; Whapi `DAREDL-HX9YH`; AT `appT9TVZWhv7io4CN` | Weekly Mon 7am ET; Whapi sync 6am ET | ⚠️ Weekly live, **daily parked** | n8n Error Notifier → Slack |
| **WhatsApp Daily Stats** | 97677 | n8n `1VDbwlQqXcfbotic` | Daily 9:30am ET | 🟢 Live | n8n Error Notifier |
| **WhatsApp Approvals** | 97737 | n8n `ib7g9bBddhzCbj4X` (54 nodes), Typeform sync `wb9TrAL1ZdqxGbpC`; Slack `C0AUS9DB5GX` | Webhook (Whapi join) | 🟢 Live | Slack cards + Error Notifier |
| **Centurion 20M+ verifier** | (in 97737) | Layered **inside** WA Approvals `ib7g9bBddhzCbj4X` + `mds-digest-web` `/api/centurion/verify` | Webhook | 🟢 Live (test-first) | Slack `C0AQ8USNQK0` |
| **WA Engagement triage** | 97777 | n8n Match Backfill `4B79OVfyT2a9a3Xt` (live), Engagement Sync `v9D1bROMGMivfXH2` *(BUILT, INACTIVE)* | Daily 8am / 9am ET | ⚠️ Partial — Sync not activated | Weekly Slack Mon 9am ET |
| **FB weekly engagement** | — | Make "Execute FB Group AI Agent" `3999830` *(0 executions ever)*; FB Apify scraper `3999804` *(idle)*; FB scraper n8n `hZMaAcPjFe706Jin` *(archived)* | on-demand | 🔴 **Can't confirm live** — see flags | none |
| **Intercom ⇄ Airtable** | 100837 | Render Cron `crn-d8m2ji0g4nts7380p690`; repo `mds-intercom-lastseen-sync`; dead n8n `Q6GPgQk36Muwzmi4` | Last-seen daily 6am ET | ⚠️ Last-seen live; **status→Intercom leg pending** | Render email on fail |
| **Scorecard** | 100317 | AT `appUM1F29IJsMsXRb`; n8n Attributes `odfBrs6z9IxP7ndl`, WA Sync `RPfnori7C26NcT9N`, Events `uuXBxG6lqXCV9otJ`; repo `mds-community-scoreboard` | Weekly (Mon 1am CST) | 🟢 Phase 1 done; Phase 2 = churn weights | **none** |
| **$500 Event Credit** | 100677 | n8n Detector `eysq1oXPwcTXhJKM` + Interactivity `qbDK69qc33QKqVZG`; AT log `tbl3mM08mxjT9scpI`; WA acct `314326` | Detector daily 8am ET | ⚠️ Detector live; **crediting awaiting Tina sign-off** | Slack `C0AQ8USNQK0` |
| **Lead Enrichment** | 97957 | n8n WF1 `BFrSqQ8Cp0KfbLIH`, WF2 `NyTauh9UtG8YMbja`, WF3 `hpIIQpgIUlmTJJZ0`; WF4 `zqiik1F949d4qZUe` *(off — over-firing)*, WF5 `MBh25vyKRexFYz09` *(paused)*; AT `appJC64rhJN5kFG65` | Webhook (Luma) | 🟢 Live (V4.x) | Slack `C0AU8LYCCF9` |
| **Skill Base** | 100637 | Vercel `mds-skill-base` (skills.mds.co); Typeform `z8OgRGxz`; AT `app1AKVJvXDjbFViS`; Supabase `majvlmsxhjxlvoylzszc` *(parked)* | Webhook (Typeform) | 🟢 Live (POC) | Slack card + `/api/health` |
| **MRR / Stripe→AT** | 100897 | Make `4472150`; n8n Payment-dates `30OyMumvZsQIAMo8`, Onboardings `m94lQxcXACs6rFJx`, Slack Observer `IPTLQHFTPpdplueT` *(ERRORING)*; AT `appou5JVr0WIrioWS` | Daily 12:30 UTC / 8am ET | 🔴 **Observer failing (429)** | Slack `#automation-tests` |
| **Ecompreneur Luma→Webflow** | 98597 | n8n `Mc2Av5YXn49R65V0`; Webflow site `69bc74cf9e79379254d05b2f`; Luma cal `cal-nwh04Obbq3hCUgD` | Webhook + 6:10am safety-net | ⚠️ Pipeline live; Webflow page unpublished | **none** |
| **Luma Manual-Add → AT** | 97537 | Make `4688319`; AT Roster `tblfTLRfAqBhBZlc4` | Every 30 min | 🟢 Live | Slack `C0AQ8USNQK0` |
| **Video Platform** | 98637 | Supabase `nadtudwuwjhckotrngzn`; Vercel `prj_3zNOk…` (mds-video-admin); Render `mds-ai-bot`; Mux + AssemblyAI | Push-deploy | ⚠️ In progress; **Mux env activation in flight** | **none** |
| **Members Deletion Trap** | — | n8n `5pX4uCt1VFFoT641` + webhook refresh `s9DRiuBwjRHKGNyT` | Daily 7am ET refresh | 🟢 Live (forensic alert) | Slack |
| **Chapter-intro email** | — | Make `4717952` | Every 15 min | ⚠️ **Active + being live-edited (Carmel); idempotency risk** | none |
| **Welcome Box** | — | Make `4627502` | Every 30 min | 🔴 **Auto-run failures 6/10** | none |
| **Wild Apricot → AT** | — | Make `364050` | Immediate | ⚠️ **1–2 records parked in DLQ** | none |
| **Honorary member sync** | — | Make `4748779` (+ Slack emoji `4623867` *off*) | Hourly | 🟢 Live | none |
| **GoHighLevel → AT** | — | Make `4088035` | Immediate | 🟢 Live | none |
| **Event/App/Guest syncs** | — | n8n `9ix1Ch5043T4ULyU`, `mmmIsZwU9PyPkAd9`; Make `4192825`, `4221663` | Webhook/immediate | 🟢 Live | none |

---

## 2. 🔴 Broken / needs attention NOW

1. **MDS New Member Onboarding — Slack Observer** (n8n `IPTLQHFTPpdplueT`) — Airtable **429 "too many requests"** on the Members-table trigger; **3 of last 5 runs failed** (6/13, 6/12, 6/03). Needs backoff / reduced poll frequency.
2. **Welcome Box Automation** (Make `4627502`) — 3× `Unprocessable Entity` + a 429 on auto runs 6/10. Carmel mid-fix 6/11; confirm next auto run is green and that 6/10 records were backfilled.
3. **Wild Apricot → Airtable** (Make `364050`) — core member sync, **1–2 records parked in the dead-letter queue** from a past failure. Sync runs green now but parked records are silently dropped until reprocessed.
4. **FB weekly engagement** — the Make "Execute FB Group AI Agent" (`3999830`) has **zero executions ever**, the Apify FB scraper is idle, the n8n scraper is archived. Whatever currently produces the FB weekly update could not be confirmed as a live automation — **needs you to point me at the real one** (or it's manual).

## 3. ⚠️ Half-deployed / pending activation

- **Intercom status→Intercom** real-time leg — AT automation not firing (only last-seen→AT is live).
- **WA Engagement Sync** (n8n `v9D1bROMGMivfXH2`) — built, batch-fix shipped, **never activated**.
- **$500 credit crediting** — detector live, but no real member has been credited; awaiting Tina sign-off.
- **WA Daily Digest** (n8n `qo3qzeVtprhTW88F`) — inactive/parked while weekly runs.
- **Video Platform Mux signed-URL env** — code shipped, env activation in flight.
- **Ecompreneur Webflow events page** — pipeline live but page not published.

## 4. 🧹 Cruft / cleanup candidates

- **n8n:** `My workflow 2` (active 1-node webhook doing nothing, still taking traffic), `My workflow`, `TEMP Diag — dual-sub customers`, 2× Partner Deliverables test stubs, `Meta APP integration with whatsapp`, ~7 archived legacy lead/FB workflows.
- **Make:** 101 inactive scenarios, many near-duplicate `(copy)` / retired Wild-Apricot/Auth0/Membership versions — an account-clutter pass is overdue.

## 5. Monitoring gaps (why the dashboard matters)

Only the **WhatsApp family** has a dedicated error-notifier (n8n `CPPKMDdutZMF1J9V` → Slack). These have **no runtime health alerting**: Scorecard, Video Platform, Ecompreneur Luma→Webflow, MRR ingestion, Welcome Box, Chapter-intro, Wild Apricot, Honorary, GoHighLevel. A failure in any of them is currently invisible until someone notices missing output.

---

## 6. Proposed tag taxonomy (for a tools registry)

ClickUp **docs cannot be tagged via the API/MCP** (tags exist only on *tasks*). The portable fix is a **Tools Registry** (one record per tool) with these facets:

- **Status:** `live` · `partial` · `broken` · `parked` · `in-progress`
- **Platform:** `n8n` · `make` · `render` · `vercel` · `airtable` · `supabase`
- **Domain:** `whatsapp` · `members` · `events` · `leads` · `mrr` · `scorecard` · `video` · `intercom`
- **Trigger:** `scheduled` · `webhook` · `manual`
- **Owner:** `andy` · `carmel` · …
- **Alerting:** `has-alerts` · `no-alerts`

---

## 7. Health-dashboard data sources (for the future build)

A single health view would poll, per platform:
- **n8n** — `GET /executions` per workflow → last run status, error text, timestamp (already proven in this scan).
- **Make** — `executions_list` per scenario → status code (1 ok / 2 warn / 3 error) + DLQ count.
- **Render** — service + cron run status via Render API.
- **Vercel** — deployment status for Skill Base + Video Admin.
- **Airtable / GitHub Pages** — last-sync timestamps for Scorecard.

Each maps cleanly onto the registry rows above, so the registry doubles as the dashboard's config.
