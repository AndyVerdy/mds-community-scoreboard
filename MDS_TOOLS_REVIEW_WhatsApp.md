> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# WhatsApp cluster — verified tool review

> Ground-truth review, 2026-06-14. Sources: live n8n workflow definitions (node-by-node), live Airtable schemas, n8n run history, `mds-digest-web` source on `main`, and ClickUp docs 97677 / 97737 / 97777. Where the live source contradicts a doc, the live source wins (noted as **drift**). Items I could not confirm are marked **UNCONFIRMED**.
>
> Shared infra: Airtable **WA DB `appT9TVZWhv7io4CN`** (Chats `tblcNf3e65LH4fpzi`, Members `tbli8B589iNbsGF0Z`, Summaries `tbl8XXaQMiqskOn8X`, DailyActivity `tblikCGQmNqNrhNJs`). MDS CRM = `appou5JVr0WIrioWS/tblfwOSROSHfuYUxv`. Scorecard base = `appUM1F29IJsMsXRb`. Whapi cred `TW0Jzhp9z9mKUZQV` (channel `DAREDL-HX9YH`, bound to Andy's personal `+17866578153`). Slack bot app `A0B0MC1LGUQ`.

---

## TOOL 1 — Digests (daily + weekly email, Slack reports)
**Workflows:** Weekly `vsj4CxGBv7FgNmKA` · Daily `qo3qzeVtprhTW88F` · Whapi Sync `Lo45BM43boK1gM19` (feeder) · Error Notifier `CPPKMDdutZMF1J9V`

### Weekly digest `vsj4CxGBv7FgNmKA` — ACTIVE
- **Flow:** Mon 7am ET → load members + active chats → per chat: fetch 7d Whapi messages (paginated) → Claude summary (`claude-sonnet-4-6`, `weekly-v2`) → upsert summary → build per-recipient email → send via **Resend** (`digest@mds.co`) → Slack success report.
- **Schedule:** cron `0 7 * * 1` America/New_York.
- **Recipients:** member gets email only if `email_subscribed` AND `email` AND a `channel_subscriptions` entry with freq `both`/`weekly` for a channel in their `channels_present`. Format per `email_format_preference` (combined/separate).
- **Slack:** success report → channel `C0AQ8USNQK0` (bot cred `vUi5klXA8N2A987t`).
- **Health = healthy only if** it emailed a non-empty digest to the eligible recipients — NOT just "ran". Failure modes: **silent zero-recipient run (only ~3 of 475 members have `channel_subscriptions` set)**, blank summaries on Anthropic credit exhaustion (still "success"), Whapi token expiry.
- **Status:** only 1 run in history (2026-06-08, success) — activated ~2026-06-03, next due Mon 06-15.

### Daily digest `qo3qzeVtprhTW88F` — **ACTIVE** (blueprint said parked — WRONG)
- **Flow:** same as weekly (24h window, `prompt_version v5`) PLUS it writes engagement data: DailyActivity rows (per-sender msg + reaction counts) and Member rollups (`msgs_7d`, `msgs_30d`, `last_active_at`). Engagement branch runs **pre-Claude**, so an AI failure no longer destroys counts (fix #28).
- **Schedule:** cron `0 7 * * *` America/New_York.
- **Status:** **active.** Failed once 2026-06-13 (exec 21874) on a transient Whapi `/messages/list` timeout (one chat hung 5 min); the workflow was hardened (retry 3× / skip / continue) and ran success on 06-14. NOT deactivated.
- **Same zero-recipient + blank-summary failure modes as weekly.**

### Whapi Sync `Lo45BM43boK1gM19` — ACTIVE (entitlement feeder)
- **Flow:** daily 6am ET → per active chat: Whapi `/groups/{id}` → compute `member_count` + recompute each member's `channels_present` (sorted chat-name set; only clears if previously non-empty). Pure Airtable writer, no email/Slack.
- **Schedule:** cron `0 6 * * *` America/New_York (1h before digests — correct ordering).
- **Health:** the entitlement data it produces must be current or every digest mis-routes/zero-routes. **No `errorWorkflow` wired** → its failures don't even hit the notifier. `@lid` participants (~30%) dropped from matching.
- **Status:** last 10 runs success (last 2026-06-13 10:00 UTC).

### Error Notifier `CPPKMDdutZMF1J9V` — ACTIVE (error-triggered)
- **Flow:** on error of a workflow that names it as `errorWorkflow` → build Block Kit failure report → `chat.postMessage` to `C0AQ8USNQK0`.
- **Wired on:** Daily + Weekly digests, Daily Stats, Match Backfill, Engagement Sync. **NOT wired on:** Whapi Sync, the Approvals workflows, Scorecard WA Sync.
- **DRIFT:** ClickUp #29 still describes it posting to a **dead Slack incoming-webhook**; the live node actually uses `chat.postMessage` with a bot token to `C0AQ8USNQK0`. The dead-URL description is stale — but the real risk (is anyone watching that channel?) is unresolved.
- **Health = delivery to a watched channel**, which n8n's status can't measure. The May 15–26 outage: this fired 11× with `status success` and **nobody saw any of them**. On 2026-06-13 Andy learned of the failure from n8n's own native email, not this.

---

## TOOL 2 — WhatsApp auto-approval
**Workflows:** Core `ib7g9bBddhzCbj4X` (54 nodes) · Typeform→DB `wb9TrAL1ZdqxGbpC` · Daily report `w2zpT1dI3jt9dqF3` · Weekly report `prgV70vX88cLG0QL`

### Core approvals `ib7g9bBddhzCbj4X` — ACTIVE
- **Flow:** Whapi `groups` webhook → filter join requests → extract phone (recover real phone if `@lid`) → Whapi pending apps + contact → **Airtable match** against MDS CRM (`appou5JVr0WIrioWS/tblfwOSROSHfuYUxv`) → `Compute Recommendation` (300-line brain) → log to JoinRequests (`tbl3FV9pAFCi1AhnC`) → pull Typeform form + response → post Slack decision card to **`C0AUS9DB5GX`** → auto-act or wait for button.
- **Two webhooks:** `/webhook/wa-join-request` (Whapi) + `/webhook/slack-interactivity` (Slack buttons). No cron.
- **Auto-approval logic:** `Compute Recommendation` → APPROVE/REVIEW/REJECT; `Decide Auto-Action` only lets the bot act when phone+name/phone match + qualifying status + no form required. Master gate `auto_actions_enabled=true` (live). Hardcoded manual-only set: MDS Supplements + **MDS Centurion 20M+** (recommend-only).
- **Outputs:** Whapi approve/reject (`continueOnFail`), Resend welcome/form email (BCC `tangowithw@gmail.com`), Airtable JoinRequests upsert, Slack card update + thread reply.
- **Health:** healthy needs (a) Whapi `groups` webhook still subscribed — **biggest blind spot, no n8n signal if Whapi silently stops**; (b) cards post; (c) buttons action through to Whapi `success:true`; (d) our number stays group-admin. **No `errorWorkflow`** → failures silent.
- **Known bugs:** `at_member_id` logged with `?blocks=hide` suffix (cosmetic); `Post Image to Thread` node disabled (screenshot-to-thread broken); Whapi on Andy's personal number (prod risk).
- **Status:** ACTIVE, last 10 success. Verified live auto-approve 2026-06-14 (Ryan Bastuba → MDS Accelerator: Whapi success + email + AT update + thread reply).

### Typeform→DB `wb9TrAL1ZdqxGbpC` — ACTIVE
- **Flow:** Typeform webhook (5 verification forms, tag `mds-wa-sync`) → parse → match member by email/phone → upsert `DB for WA` (`tblUFg4y1c4lyuvXH`) → patch matched member's `WA Forms Completed`.
- **Forms:** TikTok `gILdcvsp`, Centurion `IaKWKysS`, Large SKU `BKg5wDeY`, Supplements `j5JAS5sT`, Real Estate `N1BkcKGe`.
- **Health:** feeds the core workflow's form-on-file check — if its webhook unsubscribes, real members get wrongly bounced to REVIEW. Known: `tf_raw_response` is mangled by a quote-stripping `.replace` (worked around by re-fetching at REVIEW-time).
- **Status:** ACTIVE, last 10 success (last 2026-06-11 18:08).

### Daily report `w2zpT1dI3jt9dqF3` / Weekly report `prgV70vX88cLG0QL` — ACTIVE
- **Flow:** scheduled → search JoinRequests for the window → aggregate by decision_source/decision/tf_required (+ per-channel, + bot_share% on weekly) → Slack report → `C0AUS9DB5GX`.
- **Schedules:** daily `1 0 * * *` / weekly `1 0 * * 1`, America/Chicago (12:01 AM CT).
- **Health:** correct buckets depend on the core workflow writing accurate decision tags. Risk: **pageSize 100 cap silently truncates** >100 requests/window. No `errorWorkflow`.
- **Status:** both ACTIVE, clean cadence (daily last 2026-06-14 05:01; weekly last 2026-06-08).

---

## TOOL 3 — Centurion auto-approval
**Components:** Centurion verifier `mds-digest-web /api/centurion/verify` (Render, `digest.mds.co`) + the Centurion matrix inside core approvals `ib7g9bBddhzCbj4X`

- **Flow (verifier):** Typeform `IaKWKysS` webhook → ack 200 + process detached → download uploads → **Claude vision** (`claude-opus-4-8`, all files one call, JSON schema, anti-hallucination rule #1) returns per-file revenue + `combined_total_usd` → match member by `Preferred Email` + status gate → `computeVerdict` → **write verdict to Airtable** → Slack card + screenshots to `C0AQ8USNQK0`.
- **Verdict logic:** `eligible | not_eligible | needs_review` (NOT approve/reject). Screenshot total ≥ $20M = eligible; proof < a higher typed/AT claim = needs_review; unreadable/range>366d/non-marketplace = needs_review. **Human-in-the-loop** — it does NOT touch WhatsApp; it writes the AT fields (`Centurion 20M+ Verdict`, `Centurion Verified Revenue`) that the n8n Centurion matrix reads (Phase 1 = recommend-only). Full autopilot = **Phase 3, parked.**
- **Health:** each submission → card in `C0AQ8USNQK0` within ~1-2 min, defensible vision number, verdict persisted to AT. Failure modes: **Typeform signature check is OFF** (no `CENTURION_TYPEFORM_WEBHOOK_SECRET`) → spoofable + silent if delivery stops; **in-memory dedupe resets on every Render redeploy** → double-process risk near a deploy; no automated failure alerting (console.error only).
- **DRIFT:** ClickUp page 07 header says "No Airtable writes / test-phase only", but live `main` **does** write the verdict to AT (commit `56c90bf`, "Phase 1 + Phase 2"). Phase 2 is live.
- **Status:** code is deployed `main`, working tree clean. Render runtime + a recent live submission **UNCONFIRMED** (no runtime logs pulled).

---

## TOOL 4 — Daily statistic + WhatsApp DB update
**Workflow:** Daily Stats Builder `1VDbwlQqXcfbotic` — ACTIVE

- **Flow:** daily 9:30am ET → read DailyActivity (60d) + matched members + active chats → `Compute Stats` (last 5 days: org/channel/member rolling 24h/7d/30d posts+senders, tiers, deltas, newly silent/active) → upsert (key `Stats Key`, self-healing 5-day window).
- **Schedule:** cron `30 9 * * *` America/New_York.
- **WRITES three tables INSIDE the WA DB `appT9TVZWhv7io4CN`** (this is "the WhatsApp DB it updates"):
  - `Org Stats` `tblkbPR7DT38dSJ3n` — 1 row/day
  - `Channel Stats` `tblm11h4rr56aBo4U` — 1 row/chat/day
  - `Member Stats` `tblJn5aftV1wSGQ7v` — 1 row/member/day
- **Feeds:** the `/admin` dashboard at digest.mds.co AND the Scorecard WA sync (Tool 5).
- **Health:** healthy = ran AND `DailyActivity` had fresh rows for yesterday. **Failure mode: if the daily-digest's DailyActivity write fails, stats silently freeze with no error here.** `errorWorkflow` wired.
- **Status:** ACTIVE, last 5 runs success (~1.5 min).

---

## TOOL 5 — Weekly scorecard updates with WhatsApp data
**Primary:** Scorecard WA Sync `RPfnori7C26NcT9N` · **Underpinning:** Match Backfill `4B79OVfyT2a9a3Xt` · **Related (CRM, not Scorecard):** Engagement Sync `v9D1bROMGMivfXH2`

### Scorecard WA Sync `RPfnori7C26NcT9N` — ACTIVE (this is Andy's "weekly scorecard updates")
- **Flow:** Mon 1am CST → read Scorecard spine ("Member Scorecard (NEW)" `tblbmLb5D1kVpuJD1`) + existing "WhatsApp (NEW)" rows → read DailyActivity (100d) + WA members + latest Member Stats → compute 7d/30d (from Member Stats) + 90d (from DailyActivity) → PATCH/POST **Scorecard base `appUM1F29IJsMsXRb` table "WhatsApp (NEW)" `tbllZ4REuRYkuVyri`**.
- **Schedule:** cron `0 1 * * 1` America/Chicago.
- **Writes fields:** `Updated (WhatsApp)`, `Posts 7d/30d/90d (WA)`, `Channels Active 7d/30d/90d (WA)`, `Channels Registered (WA)`, `Tier (WA)`, `Last Active (WA)`. The "Member Scorecard (NEW)" spine lookups these into `Engagement Score` — this is how WA data reaches the public leaderboard.
- **GAP → FIXED 2026-06-14 (reactions).** The `Compute WA stats` node read `reaction_count` but never wrote `Reactions 30d/90d (WA)` — old values were stale leftovers. Fix applied via `patchNodeField` (surgical, atomic): `actByPhone` now captures `rx`, `stat90` computes `r30`/`r90`, and both branches of `c` write `Reactions 30d (WA)` + `Reactions 90d (WA)`. Verified: `n8n_validate_workflow` clean (0 errors) + local dry-run against live data → 1,282 rows patched, 140 get R30 / 173 get R90 (sum 870 / 1,415), 0 errors. Goes live on the next Mon 1am CST run (or a manual "Execute workflow"). Upstream `reaction_count` confirmed real: 572/1,137 DailyActivity rows non-zero, ~1,003 reactions/30d, fresh daily.
- **STILL OPEN:** `Channel Breakdown 30d (WA)` (text field) is still not written by the sync — left as-is for now (not requested).
- **VERIFIED WORKING:** as of 2026-06-14 all 800 `WhatsApp (NEW)` rows carry `Updated (WhatsApp) = 2026-06-08` (last Monday's cron) with real values — Posts/Channels/Tier/Last Active populated (e.g. Guido Reyes 615 posts/90d, Champion). The weekly sync IS updating the table; data is "as of last Monday" by design (weekly cadence, next run Mon 06-15).
- **DRIFT:** doc 97777 doesn't mention this workflow at all (created 2026-06-05, after the doc). **No `errorWorkflow`** wired.
- **Health:** healthy = weekly run succeeds AND a meaningful share of spine rows resolve a WA match (non-zero posts for active members) AND `Updated (WhatsApp)` = today. Failure: URL-parse match miss → member written all-zeros/Dormant.
- **Status:** ACTIVE but thin history — only ~1 real weekly cron run (2026-06-08, success) since 06-05 creation.

### Match Backfill `4B79OVfyT2a9a3Xt` — ACTIVE (prerequisite for everything)
- **Flow:** daily 8am ET → find unmatched WA members → match against MDS CRM by phone-last10 (+ name fallback) → write `source_member_id` + `source_member_link` back to WA Members.
- **Every other WA-data workflow filters on `source_member_id != ''`** — if this degrades, downstream coverage silently shrinks. Match rate ~377/475 (79%); remainder mostly LID/invite-only/no-name (known-unmatchable). `errorWorkflow` wired.
- **Status:** ACTIVE, last 5 success (~8-25s).

### Engagement Sync `v9D1bROMGMivfXH2` — **ACTIVE** (blueprint said "not activated" — WRONG)
- **Flow:** daily 9am ET → matched WA members + DailyActivity (30d) → PATCH **MDS CRM** `appou5JVr0WIrioWS/tblfwOSROSHfuYUxv` fields `WhatsApp msgs (30d)`, `WhatsApp Last Active`, `WhatsApp Channels Active (30d)`. A 4th field `WhatsApp Engagement Tier` is an Airtable formula off those three.
- **This writes the CRM (Belen's internal triage view), NOT the public Scorecard** — distinct from the Scorecard WA Sync. Both active.
- **Status:** **ACTIVE and healthy**, last 5 success (~2.5 min). Was activated 2026-04-30; had a 4-day silent 429 failure 04-30→05-04, fixed via batch endpoint + 600ms interval. No current blocker. (The "inactive" label survives only in stale doc pages 01/03/04.)

---

## Cross-cutting findings (for the dashboard + for Andy)
1. **"Ran" ≠ "healthy"** for: digests (can email ~0 recipients — only ~3/475 subscribed), Error Notifier (succeeds even if unwatched), Daily Stats (freezes silently if DailyActivity stale).
2. **Alerting is fragile:** only some workflows wire the Error Notifier (Whapi Sync, all Approvals, Scorecard WA Sync do NOT). And the notifier posts to `C0AQ8USNQK0` — **is anyone watching it?** (May outage went unseen.)
3. **Doc drift (live source wins):** Error Notifier no longer uses the dead webhook; Centurion DOES write to AT (Phase 2 live); Scorecard WA Sync absent from doc 97777.
4. **Single point of failure:** Whapi bound to Andy's personal number `+17866578153`.
5. **Two "scorecards":** Scorecard base (`appUM1F29IJsMsXRb`, public leaderboard) vs MDS CRM (`appou5JVr0WIrioWS`, Belen's triage). Tool 5 = the former; Engagement Sync = the latter.
