> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Session Log — Misc (Tools-health, WA DB, Member360, GroupOS tag sync, Membership Health, one-offs)

Newest first. **Every session close: prepend the full entry here + ONE index line to `SESSION_LOG.md`.**

---

## 2026-09-03 — GroupOS QA: `86e25hmj1` ticket.cancelled on admin cancellation (pre-prod 1.2.1)

Andy asked for a QA pass on ClickUp `86e25hmj1` ("Add ticket cancellation trigger", deployed to pre-prod in release 1.2.1 by Andrii Matiushenko together with `86e2t7834`, MDS-API PRs #5383 → #5493). Full report: `GROUPOS_TICKET_CANCEL_WEBHOOK_QA.md`.

- **Verdict: the ticket's claim passes.** Admin cancelled a $100 paid ticket on pre-prod `vl223` (order `#6a8614ebdc47075a29116304`, tx #4) at 03:08:29 UTC → `ticket.cancelled` delivery attempted 03:08:31 (`whd_69dee84e…`) with `cancellation = {reason:"paid_ticket.cancelled", type:"refund", refundAmount:100, cancelledBy:"admin"}`, then `ticket.refunded` at 03:08:34. Same 27 top-level keys as the pre-existing admin-free baseline (Doina, 2026-08-25). Evidence = the "What we sent" payload in the sending-integration delivery history (integration "Maks WH - Approvals test", endpoint dead → every delivery "Gave up" on HTTP 404, which is pre-existing and irrelevant).
- **Member-side parity FAILS:** built a throwaway event "QA webhook cancel test 86e25hmj1" (`6a98e708959c69fd82bc8ba4`, free ticket with *Allow cancellation* on), registered (inline widget, 03:24:22) and cancelled as a member ("Cancel order", 03:27:07) — order shows Cancelled, **no `ticket.purchased`, no `ticket.cancelled`**. First read as a worker stall (nothing after 03:17 had a record); corrected at 04:14: the manual test event (03:34) and the pause `event.updated` (03:38) did arrive with ~2 min latency, so the member order-level cancel and the inline-widget registration simply enqueue nothing. Correction comment posted on the ticket.
- Other findings: paid-cancel payload carries `totalPaid`/`orderAmount` `"$0.00"` for a $100 ticket; `ticket.refunded` says `refundAmount: 0`, `"No reason provided"`, no `triggerEntity.id`; sending detail opens with "Nothing has been sent yet" while 32 deliveries exist (same as receiving defect #1); direct URL to a sending detail renders no rows (defect #3); member Order details listed 3 tickets for a 1-ticket order (seen once).
- Pre-prod state left: Andrii's tx #4 refunded ($100 Stripe test refund); QA event **Paused** (not deleted); "VL 23" still holds a free San Diego Chapter Hike ticket; integration accidentally paused ~03:31–03:33 UTC and re-activated. Not tested: member cancels a paid ticket (needs a card), cancel-without-refund (`86e2t7834`).
- **Andy's call: REJECTED.** His scale: S1 fix now, S2 fix, S3 later, S4 skip — the worker stall is S1 and the `$0.00` payload is this ticket's own output (S2), so the ticket goes back. Evidence comment `90170248124142` posted on `86e25hmj1`, status set to `rejected pre-prod` (it had meanwhile been moved to `ready for release`). Nothing shipped; docs only.

---

## 2026-09-02 — WA → FB story posts: rebuilt around real feedback, now on autopilot

Shipped yesterday, rebuilt today against three rounds of feedback from Andy and Eugene.
Live, scheduled, verified end-to-end.

**What changed, and why each one mattered:**

- **Three options per card, not one.** Andy: *"if the admin doesn't like a story, then we
  are not really providing any options."* Every run wrote one story and discarded two the
  ranker had separated by almost nothing, so a story the poster disliked wasted the slot
  for days. All three are written and gated; the human picks.
- **The confidence score was theatre and is gone.** It was never computed — the model
  self-reported it AND the prompt told it the 0.7 threshold, so it cleared it on every run
  ever recorded (0.74–0.82, never below, never a "none"). Replaced with comparative
  ranking plus *measured* signals from the raw messages: voices, whether a question drew
  answers from others, messages carrying figures (`signals.ts`).
- **Post rewritten twice.** First version was a roll call with the numbers stripped out —
  the "no embarrassing numbers" rule had over-fired onto vendor pricing, which is the whole
  value. Then rewritten again to Eugene's format after he posted one by hand: standing
  title + blurb, `MDS DTC/Shopify - 8/30` header, one story, no "Also this week" footer.
- **Two chats excluded**: Centurion 20M+ (revenue-gated tier — broadcasting it gives away
  what members pay for) and Credit Card & Travel Hacks (off-topic). Closed a gap where the
  blocklist filtered stories but NOT the footer.
- **Tag links on the card** from `digest.member_links` — Eugene tags members by hand and a
  tagged member replies.
- **`offered` ≠ `told`.** My error, caught by Andy: the DTC story Eugene liked was already
  unreachable because being *shown* had marked it used.

**Incident: the card's buttons hijacked WA Approvals.** A URL button with no `action_id`
does NOT stop Slack delivering the click — it mints its own id and POSTs to the OWNING
APP's Interactivity URL. The card posts with the WA Approvals bot token, so Eugene clicking
"Open group" reached that handler, which read it as a join-request rejection, overwrote the
card in place and stamped `decision=rejected` onto Airtable JoinRequests `recgrlkagHhDZH3Iv`
(Whapi 400'd, so no member was actually rejected). **⚠️ That row still needs correcting —
Andy or ops, not the agent.** Card now carries no interactive elements at all; a test pins it.

**Spine verification (Andy asked):** partners 27/27 on `partners_catalog`. Members 246/284
posts (87%) reach `member_profiles` via `fb_member_map.at_member_id`; the 38 misses are 13
authors with no map row, two of which are not people. Join `member_profiles`, NOT
`digest.members` (WA mirror, shows a misleading 72%).

**Late additions (same session):**
- **One option per chat, enforced in code** — a run had shipped two of three from the same
  chat. Three stories from one conversation-space read as repetitive, which is the whole
  thing a choice exists to avoid. Now a hard rule alongside the two existing duplication
  guards (same story key; message-id overlap). Verified live: 3 options, 3 distinct chats.
- **`FB_BACKLOG.md` opened** for the Facebook stream (capture · admin tab · story posts), in
  Andy's structure — ARCHITECTURE, THE REST, CLOSED. **#1 (S1)** the member-spine gap (11
  real members with no FB-uid mapping); **#2 (S4)** a dedicated Slack app so the card buttons
  can be turned back on — that one is credentials and configuration, the handler is built.

**State:** prod `a8a834f`, n8n `iX7cEFrCW5apa7CS` ACTIVE
Mon/Wed/Fri 9am ET, 291 tests green, final live run 3 options / 0 rejected.

**Estate:** three sessions in `mds-digest-web` today. The shared checkout was switched under
someone mid-edit twice; I now work only in `.worktrees/fbstory`. A peer's hydration-bug
report was withdrawn as a bad measurement — I had endorsed its repro without checking it,
and said so.

Handoff `WA_FB_STORY_POSTS.md`.

---

## 2026-09-01 — WA → FB story posts: designed, built, shipped to production

**Ask (Andy, story mode):** "as an MDS community, we want to post regularly on our FB community
page about interesting things that happen in our WA chats."

**Shipped and live.** Three times a week (Mon/Wed/Fri 9am ET) a Render route picks the single
best conversation from the 18 MDS WhatsApp chats, writes it up as a ~120-word named-and-
paraphrased post, checks it against a deterministic privacy gate, and drops a copy-ready card
into `#automation-tests` for Andy to paste into the private FB group. Meta removed Groups API
publishing in 2024, so the human paste is a hard constraint, not a shortcut.

- **Merged + deployed:** `mds-digest-web` `31a438e` (merge of branch `fbstory`, 17 commits).
  Suite 17 files / 237 tests green on the merge result; `next build` clean; both routes present.
- **Deploy proven live:** `/api/version` flipped `cae87c1` → `31a438e`; `/api/fbstory/draft`
  went 404 → 403 (route live, secret gate refusing unauthenticated) → 200 once Andy set
  `FB_STORY_SECRET` in Render.
- **First live run:** HTTP 200 `posted:true`, story `120363407426452368@g.us:OpD8fwN5TDFNvg-…`,
  ledger row written (`MDS DTC/Shopify`, 22 message ids, confidence 0.78), and the card is
  visible in `#automation-tests` — which is also the first proof the Block Kit payload is valid.
- **Schedule:** n8n `iX7cEFrCW5apa7CS` ACTIVE, cron `0 9 * * 1,3,5`, tz `America/New_York`,
  timeout 180s, **retry deliberately OFF**. Holds no logic — one HTTP call.

**Data: existing only.** Reads `digest.summaries` and `digest.wa_messages` (both already
mirrored). One new table `digest.fb_group_posts` records what has been told. **Airtable is
never written.**

**The whole-branch review earned its keep.** After ten clean task reviews, the final opus review
found a CRITICAL hole every earlier review missed: the privacy gate's verbatim check ran PER
MESSAGE, so a member's sentence split across consecutive WhatsApp messages passed. Proven by
execution — 17 verbatim words scored 6 against a threshold of 8. Measured exposure: 17.6% of
messages in the last 14 days are same-sender follow-ups within 2 minutes. Fixed by also
matching against the joined thread, verified by flipping the repro to blocked and probing
three paraphrases for over-blocking.

**Other real defects found by review, all fixed:** two Criticals in the gate (non-space-delimited
scripts bypassed the verbatim check entirely; a shared first name masked a fully-named
undeclared member) · the ranker's JSON schema was rejected by the live API (`oneOf` unsupported)
— caught only because a live smoke call was required rather than assumed · a Slack `postCard`
failure silently AND permanently lost a story (row already `draft` = told) · a double-fire could
produce two cards · a gate-blocked story was re-picked every run · the draft's markdown code
fence could be broken by a backtick in LLM prose.

**Open, Andy's call:** buttons ship unwired (Slack allows one callback URL per app; Centurion and
Application hold both) — the card still works, only one-click Mark-posted and skip-reason
feedback are missing; third-party names inside messages are prompt-defended + human-read only,
not gate-checked; RLS is disabled on 43 `digest.*` tables including the new one (pre-existing).

**Estate note:** a setup mistake put branch `fbstory` in the shared main checkout and captured
peer session `scorecard-e1`'s unrelated `#109` commit. Rescued, returned to them, landed on main
as `cae87c1`; my work moved to worktree `.worktrees/fbstory`. Also: **`digest.mds.co` does not
resolve on this Mac** (n8n and public resolvers are fine) — use `mds-digest-web.onrender.com`
for local checks.

Spec `docs/superpowers/specs/2026-09-01-wa-to-fb-story-posts-design.md` · plan
`docs/superpowers/plans/2026-09-01-wa-to-fb-story-posts.md` · handoff `WA_FB_STORY_POSTS.md`

---

## 2026-08-13 — Application v3: verification cards went missing in Slack (fixed + both recovered)

**Trigger:** Sashani in `#memebers-verification`, "Has this notification stopped? The latest one
didn't come through — Benjamin Pearson."

**Not Make, not n8n.** Make `4784286` ran clean for that submission (exec `ead36343…`, status 1,
9 ops, 2026-08-11T19:58:05Z) and the validator ran too — Airtable row `rec2AIe8RG2XM0mEK` already
had `(NEW) Revenue Verdict = needs_review` + Status `Pending`. Only the Slack card was missing.

**Root cause: a fixed 4s wait for Slack to process the applicant photo.** `postApplicationCard`
uploaded the photo, slept 4s, then referenced it in a `slack_file` image block. Slack processes
images asynchronously and **the time scales with size — measured live: 17 KB → 0.5s, 411 KB → 1.8s,
1.9 MB → 4.9s, 4.5 MB → 6.8s.** Over ~1.5 MB the block was rejected, `chat.postMessage` failed, and
`verify/route.ts` swallowed the throw into a `console.error`. The verdict was already in Airtable,
so every system looked healthy and the applicant silently left the review queue.

**Two victims, not one** — Sashani only noticed the second: **Ginny Lo `recF1LGTTFFjH4aST`
(Aug 5, 1.9 MB photo)** and **Benjamin Pearson `rec2AIe8RG2XM0mEK` (Aug 11, 4.5 MB)**. Found by
listing Forms rows with a verdict set and diffing against the cards in `C0BFVA01AJ0`.

**Shipped (mds-digest-web, Render):**
- `a8dec73` — poll `files.info` until `thumb_360`/`thumb_720` exists (20s cap) instead of sleeping;
  post the card WITHOUT the image block if the photo isn't ready or the post is rejected anyway.
  A card must outrank its own thumbnail.
- `add8115` — **`files.info` only accepts form-urlencoded args**; the first poll went through the
  shared JSON helper and got `invalid_arguments` every time, so it burned the full 20s and dropped
  every photo. Caught on the first re-fire (both cards posted photo-less), then fixed. Also bails
  out immediately on a hard error instead of waiting out the timeout.

**Verified live:** prod `/api/version` = `add8115f13…`; re-fire through the deployed endpoint returns
`attachmentErrors: []`; both applicants now have exactly one card each in `C0BFVA01AJ0` **with the
photo** (ts `1786651574.906399` Ginny, `1786651605.585819` Ben) plus the revenue screenshot in
thread. Interim photo-less cards are gone (already deleted by the time I went to remove them —
`message_not_found`); the duplicate posted for the prod check was deleted along with its orphaned
attachment. Mechanism proof: the 4.5 MB photo polls ready at 8.0s and the block is accepted.
`APPLICATION_V3_VALIDATOR.md` gotcha #2 rewritten with the measurements + the `files.info` trap.

**Left open (flagged, not chased): nothing detects a missing card.** The only alarm today is a human
noticing a quiet channel — which is why the Aug 5 loss went unseen for 8 days. The audit query is
cheap: any Forms row with `(NEW) Revenue Verdict` set and no card in `C0BFVA01AJ0` was lost. Belongs
on the tools-health dashboard; Andy to rule on priority.

---

## 2026-08-06 (night) — MRR: LIFETIME PAID (membership dues) shipped — AT + Supabase + nightly sync

**Andy's ask:** a field for "how much a member paid over time", Stripe + Wild Apricot, with a rough
cross-check for deviation. Two mid-session corrections from Andy reshaped it and both were right:
(1) WA managed the subscriptions pre-2026 and **fired invoices into Stripe under WA-CREATED Stripe
customers**, which do NOT match the `Stripe Customer ID` on the member today — so joining Stripe on
that key silently returns 2026-onward only; (2) **WA also bills events** — "get data for the sub
payment only."

**What shipped.** n8n **`PkKOxdYcW0UftVMA` "MDS Lifetime Paid (membership dues) → AT"** — ACTIVE,
nightly 06:10 ET + force webhook `lifetime-paid-sync` (responseMode onReceived; the run is ~10 min,
Cloudflare kills a waiting webhook at 100s). Two sources, no double-count:
- **Wild Apricot invoices** with `OrderType` ∈ MembershipRenewal / MembershipApplication /
  MembershipLevelChange, keyed on **`WA User ID`** → **$8,768,752** / 893 contacts. Excluded:
  EventRegistration $6.47M (n=3135) and Undefined $2.18M (n=950, memos = Summit passes, credit
  transfers). Scanned 8,734 invoices, reached end.
- **Stripe paid invoices attached to a subscription**, keyed on `Stripe Customer ID` → **$3,970,416**
  / 837 customers. 3,759 of 3,996 paid invoices are subscription-linked; 237 one-off ($444,010) are
  event/store and excluded. Not truncated.
- De-dup (same amount within 5 days) for members holding both ids: **0 rows dropped** — the two
  sources are era-disjoint, which is exactly what the WA→Stripe migration implies.

**Result: 1,026 members, $11,141,235 dues. Active coverage 697/718 = 97%.** Split: 517 WA-only,
172 Stripe-only, 337 both. 21 active members have no dues found.

**Airtable Members fields (all with descriptions):** `Lifetime Paid` fldZ4t1dOsSAZIV84 ·
`Lifetime Paid — First Payment` fldZVbmFhdAdeoVGN · `Lifetime Paid — Payments` fldwt8rVEaOc7iG0o ·
`Lifetime Paid Synced At` fldbWtqB578HuNfrv · `Rough Benchmark Paid ($6k/yr)` fldwE2BoUCgcZwND2
(Andy's benchmark: full years rounded UP × $6,000) · `Lifetime Paid vs Benchmark (%)` fldjbegHvwHYyz0AI.
`zzz UNUSED — Lifetime Paid (Events & Other)` fldS3txrzNodBHXO9 is an empty leftover from the
all-cash scope (AT API cannot drop a field) — populating it is a small change if event spend is wanted.

**Benchmark validation (strong):** long-tenured annual members land on it almost exactly — six annual
payments of $5,997 = **$35,982 vs the $36,000 benchmark, 0.0% deviation**, repeatedly (Erik Fisher,
Kenneth Hayden, Jay Kamhi, Jack Hanan, Monse Lozano, Nirbhay Patel). Christian Cox $38,919/17 pmts
= +8.1%. Distribution across 1,014 members: p10 −100% · p25 −89% · **median −48%** · p75 −17% ·
p90 +8%; 43% within ±40%. The negative skew is expected — the benchmark rounds UP to a full year, so
anyone early in year one looks deeply negative, and quarterly/monthly plans bill below $6k/yr.

**Known limits (stated, not hidden).** (a) **WA's API window starts 2020-05-16** — 279 of the 1,026
joined before that and are understated; of the 234 members at ≤−90% deviation, 58% are pre-2020
joiners. (b) A tail shows only a $195 application fee or a $1 card-auth as their dues (Mike Franzini
joined 2025-02-19, $195) = missing/incorrect id link or dues taken outside both systems. (c) **$942,409
of WA cash never went through Stripe** (Credit Card $402k / Wire $265k / Mercury Bank $242k / Cash /
PayPal, 459 contacts) plus $284,514 unlabelled tender — measured but NOT yet in Lifetime Paid.

**Supabase:** `digest.member_profiles` + `lifetime_paid`, `rough_benchmark_paid`,
`lifetime_paid_vs_benchmark_pct`, `lifetime_paid_first_payment`, `lifetime_paid_payments`,
`lifetime_paid_synced_at` (migrations `member_profiles_lifetime_paid`,
`member_profiles_lifetime_paid_dues_only`); mappings added to mds-digest-web
`scripts/backfill_member_profiles.py`. **Not yet re-run — Supabase columns are still empty.**

**Traps hit (worth remembering).** n8n Cloud Code nodes die at **60s** → the WA scan is split across
4 chained nodes (WA hard-caps `$top` at 100 whatever you ask, so ~88 sequential calls). WA `$filter`
on `/payments` **silently no-ops** — it returned unfiltered rows and made a first overlap test
meaningless. Stripe rate-limited a full `/v1/charges` + `/v1/invoices` pull → dropped charges
entirely, added `requestInterval: 350`. Airtable rate-limited the writes → `batchInterval` 1500ms,
maxTries 5, `onError: continueRegularOutput`. Renaming an AT field while a workflow still requests it
by name = **422 on the whole list call**.

**DUPLICATE-RECORD MERGE added (same session, exec 68688).** Andy audited 17 blank members. Verdict:
most blanks are CORRECT — their "active" Stripe subscriptions only ever produced **$0.00 invoices**
(`due=$0 paid=$0 attempted=true`), so no dues were ever charged. Three real findings: (1) **duplicate
records split identity** — the dormant row held the payment history while the active row read blank.
Email does NOT match across these dups (Sheiva: sajadpour.sheiva@gmail.com vs sheiva@epikkproducts.com),
so **name is the only link**. Merge rule added to `Combine + Diff`, deliberately narrow: fires only
when a name group has exactly ONE record carrying an `AT Database Status`, that record has NO dues of
its own, and a sibling does; then the primary takes the union of the group's WA ids + Stripe customer
ids and siblings are cleared so nothing double-counts. Result: **Sheiva Sajadpour $29,985/5 pmts since
2021-07-19 and Adrian Markus $7,497 moved onto their active records**, 2 siblings cleared, **214
ambiguous name groups left untouched**, grand total unchanged at $11,141,235. Base-wide there are 358
multi-record name groups but only these 2 had money stranded on a non-primary. (2) **Rodrigo Gonzalez
has an OPEN, never-attempted $3,497 invoice** (2026-07-22, "Legacy, $3,497 Annual Membership") —
uncollected cash, financial action left to Andy/Tina. (3) **8 new joiners approved Jun–Jul 2026 have
no dues invoice in either system** (Waszek, Wills, Santic, Denic, Indig, Ege, Dong, Balcazar) while WA
granted Indig/Errafik/Ege $500 "MDS Event Credit" tagged "Standard Quarterly/Annual" on 2026-08-05 —
member benefits with no invoice on file. Jenny Lee has neither a WA User ID nor a Stripe customer, so
nothing to match on.

**WILD APRICOT TAKEN OUT OF THE NIGHTLY PATH (Andy: "wild is already dead").** WA no longer bills
membership, so its dues are history and re-deriving them from ~88 sequential API calls every night
reproduced yesterday's answer. Scanned once into three FROZEN Airtable fields —
`Lifetime Paid (WA history)` fldShiyG68xAxwZ56 · `— Payments` fldIFSS7oc8GK7Yom ·
`— First` fldwziAfFAOjVjLpN (854 records, $8,602,486 attributable; WA's own total is $8,768,752, the
$166,266 difference being 39 WA contacts with no Members record). The nightly job now reads those
fields and calls **Stripe only**, recomputing the live half in full so refunds/voids/corrected
customer ids still self-heal. WA nodes deleted from `PkKOxdYcW0UftVMA` (14 → 9 nodes). Run ~10 min
→ **292s**, and the remaining time is the Airtable read + writes, not WA. Rebuild tool kept INACTIVE
as `Ot4ylZgPBGe3qrpj` "WA history rebuild" for the only case that needs it.

**BUG I INTRODUCED AND FIXED — `onError: continueRegularOutput` on a WRITE node caused SILENT DATA
LOSS.** Added to survive an Airtable 429, it instead swallowed ~110 rate-limited PATCH batches while
the run still reported **success**: only 744 of 854 records got their WA history, and the next
Stripe-only run recomputed the total DOWN to $10,014,769 (−$1,126,466) with no error anywhere. Caught
by comparing totals across runs, not by any alarm. Fix: `onError: stopWorkflow`, maxTries 5,
waitBetweenTries 15s, batchInterval 2000ms, plus a one-off idempotent refill. Total restored to
**$11,141,235 / 1,026 members / 517 WA-only + 172 Stripe-only + 337 both** — identical to the
WA-scanning version, which is the proof the frozen-field swap is lossless. **Never let a write node
continue on error; a loud failure beats a silent wrong number.**

**SUPABASE + MEMBER-360 SHIPPED (staff-only).** `backfill_member_profiles.py --apply` run over all
5,902 members — `digest.member_profiles` now carries **1,026 rows / $11,141,235**, matching Airtable
exactly. Member-360 detail page gained a **"Lifetime paid" tile** (value + payment count + first-payment
year) and four rows in *Membership & billing* (dues, payments, first payment, benchmark + deviation %).
mds-digest-web **`6f4674c`, committed NOT pushed** — pushing deploys to prod, waiting on Andy.
Verified by rendering `/admin/member360/recYo5xDJEqrj2cnk` with a real QA staff session: HTTP 200,
tile reads **$29,985 · 5 payments since 2021 · first 2021-07-19 · benchmark $36,000**. (The Browser
pane can't hold the httpOnly session cookie, so the render was proven via curl, not a screenshot.)

**PRIVACY — Andy: "super important, we are not exposing this info to members." Four surfaces checked,
all closed:** (1) `/admin` redirects anything that is not an `@mds.co` OTP session, so member-360 is
staff-only; (2) the anon/publishable key gets **401 `permission denied for table member_profiles`** —
the anon role has no GRANT, so `member_profiles` having RLS disabled does not expose it (tested
directly against both `lifetime_paid` and the `at_fields` dump); (3) **no digest function anywhere
mentions `lifetime_paid`** — the only two anon-executable functions touching `at_fields`
(`fill_member_chapter`, `stamp_member_profiles_synced_at`) both return `trigger` and cannot be called
for data; (4) `digest.member_attributes` — Olivia's matching fuel, derived from `at_fields` — is an
explicit column allowlist (rev_band, niches, expertise …) with **no money column**, so Olivia cannot
read or speak the number. ⚠️ NOTE the Airtable `at_fields` jsonb dump inside `member_profiles` DOES
now contain the Lifetime Paid keys — safe today only because nothing member-facing reads that column;
any future feature that surfaces `at_fields` wholesale would leak it. Leak gate run: all Olivia
checks PASS; its single failure (`videos_catalog never stores the raw video-file storage path`) is
pre-existing drift from the video workstream, unrelated to this change.

**PUSHED to prod `e7dabfa..2897777`** (mds-digest-web main): `6f4674c` Lifetime Paid in member-360 ·
`597b6f0` Lifetime paid/Payments/First payment in the Membership rail card · `2897777` **MRR now reads
ONLY the canonical `Stripe MRR` fldbnXyjxB8StHIre** — the legacy `{MRR}` fallback was audited across
all 718 active members and fired exactly ONCE, so it was dropped (604 active carry Stripe MRR summing
$269,097/mo, in line with the official figure). The push also carried `8573bf8` (form_responses matview
refresh), which was already sitting local-unpushed from earlier work — not from this session.
⚠️ **Deploy NOT independently verified:** Vercel posts no commit status or GitHub deployment for this
repo, and the only page showing the change is behind an `@mds.co` session I will not impersonate.
Prod answers 200; a reload of `/admin/member360/<id>` by staff is the confirmation.

**Next:** confirm the prod render ·
decide whether the $942k non-Stripe WA cash and the pre-2020 gap get folded in · Rodrigo's $3,497 open
invoice + the 8 uninvoiced joiners are ops/finance calls, not sync bugs.

## 2026-08-06 (day) — FORMS WAREHOUSE scheduled: daily GH Action step 3, proven end-to-end

Census hit **49 completed** (11 → 49 in a day). Airtable kept up LIVE — 49/49 rows, 48 linked, and
the no-match Slack alert fired twice (Charles Chakkalo unlinked; Prudence Millsap alerted at 08:52
and manually linked by the team — the alert→human loop works unprompted). The Supa ledger sat at
17 because the loader was manual; caught it up (49/49, 43 auto-stamped by exact-unique email) and
**scheduled it: step 3 of `member-profiles-sync`** (daily 13:47 UTC, after profiles + events).
`CENTURION_TYPEFORM_PAT` added to the repo secrets via gh; env-var-first loading (sync_events
pattern); mds-digest-web `e7dabfa`, pushed. **Proving run 31115206987: success** — Action logs show
"total rows loaded: 2308". Cadence: AT = instant webhook, Supa ledger = daily top-up.

Olivia CANNOT read the ledger yet, deliberately — no RPC exposes it (gate 226 proves the anon
bounce). The door = Olivia #20: owner-only lane, decay-weighted dossier input, aggregates with the
≥3-member cell floor, via staging → gate → Andy's promote.

---

## 2026-08-06 — FORMS WAREHOUSE: digest.form_responses — every form, every question, per member, in Supa

Andy: *"I want all the data, all the questions… add it to his profile in supa"* + six rules
(recency/time-decay · conditional gaps ≠ No · any number of forms · feed dossiers/personas ·
raw answers OWNER-ONLY, silent personalization OK · aggregates fine incl. chapter/region slices,
small cells suppressed).

**Built:** `digest.form_responses` (token PK, form_id, member_at_id, email, submitted_at, answers
jsonb `ref→{q,t,v}`, raw jsonb) + view **`form_answers_latest`** (latest answer per member×form×ref,
submitted_at for decay) + `stamp_form_responses()` (exact-unique email, never guesses) + loader
`mds-digest-web/scripts/sync_form_responses.py` (`e02a2cb`) — config dict, new form = one line.

**Loaded 2,276 submissions, 2,048 member-stamped (90%):** census 2026 ×17 · app v3 ×21 · honorary
×7 · legacy Standard ×1,170 · legacy MDSonly ×1,061 — the legacy history is deliberate (YoY +
decay contrast). Proof of the decay axis on one member: TTM **4,000,000 (census 2026, Aug)** over
**3,200,000 (legacy census, Jun)**; same niche both years. Two loader traps fixed: Responses API
omits question titles (pull form definition), PostgREST jsonb double-encoding.

**Gate 224 → 226**: anon denied on the table AND the view; no exposing RPC exists — any future one
needs owner-gating + min cell size. Memory: `project_mds_forms_warehouse`. Olivia **#20 unblocked**
(census launched + warehouse foundation done) — dossier/persona wiring is #20's build.

Also this hour: census AT sync caught 6 more organic submissions on its own — **17/17 in AT,
17/17 member-linked** (live-delivery proof after the webhook re-enable).

---

## 2026-08-06 — CENSUS: Typeform had silently DISABLED the webhook — re-enabled + 8 backfilled, 11/11 in AT

Andy: "we have 11 now. check." Typeform showed 11 completed; **AT had 3.** Root cause: Typeform
**auto-disabled the webhook at 02:12:47** — the very first delivery (Tabrez) hit the Make hook
before the scenario existed, was rejected, and Typeform turned the webhook off. Every submission
from 02:17 on never left Typeform. **Re-enabled via `PUT /forms/DFeK5yop/webhooks/WHTP2790200`**,
backfilled the 8 missing through the proven replay pattern. **11/11 rows in AT, 11/11
member-linked** (Aaron Biner 1.9M · Daniel Meredith 4M · Eric Winkler 3.85M · Kyle Yamamoto 12M ·
Max Krishtul 1M · Merissa Cohen 2.5M · Ramon Gonzalez 1.3M · Sherman Chang 7.5M + the earlier 3).
Webhook confirmed enabled after; the next organic submission is the live-delivery proof.

⚠️ Standing risk flagged: Typeform silently disables webhooks after failures — worth a
tools-health-style check (Typeform completed count vs AT census-row count) rather than trusting
the webhook. Not built (out of scope tonight).

---

## 2026-08-06 — CENSUS SYNC v5: unmatched submissions now ALERT — router + Slack

Andy: *"how can I know if someone was not mapped?"* Scenario restructured with a router after the
member search: **exactly one match → link the Forms row** (unchanged) · **zero or multiple matches
→ Slack alert to #automation-tests** with the name, typed email, match count and a direct link to
the AT Forms row ("link it manually"). Proven live: fired a fake submission
(selftest-census-nomatch@example.com) → alert landed in the channel with match count **0** and a
working AT link; test row deleted after. Second way to see them: AT filter
`Form ID = "Annual Census 2026"` + empty `Link to Member (restored)`.

Note: Carmel's Make-error alert bot posted "scenario stopped" during the build window (the
record-link 422, fixed within minutes) — scenario has run clean since; she may ask.

---

## 2026-08-06 — CENSUS SYNC v4: Andy's four table rulings applied — 58 fields

From Andy's review of the 85-question table: ① full name also into `What is your full name?`
(kept `Name`) · ② phone also into `Phone Number` (kept the legacy question field) · ③ **two new
AT fields created** — `% in Vietnam Manufacture` + `% in Mexico Manufacture` (singleSelect, legacy
brackets, descriptions stamped); the sum-into-Other hack removed, `% in Other Manufacture` now =
"elsewhere" alone · ④ "Do you have kids? = No" now writes **0** into `How many kids do you have?`.

Re-replayed all 3 responses; verified: Ian kids **2** (have_kids Yes + num_kids 2), both phone
fields `+16196077048`, both name fields filled; VN/MX empty for all 3 respondents (none manufacture
there — bucket logic identical to the proven China/USA fields). Scenario 4860042 at **58 fields**.

---

## 2026-08-05 (latest) — CENSUS SYNC v3: full 760-field sweep found 13 more mappable questions

Andy: *"check all the fields and lets see if there are something we can map."* Swept all 760 Forms
fields (names + types + choices + descriptions) against the 52 unmapped census refs. **13 more
questions mapped into 15 existing fields — scenario now writes 54 fields; 46 of ~85 census
questions land in Airtable.**

New: manufacturing %s → the legacy `% in China/USA/India/Other Manufacture` bucket selects
(Vietnam+Mexico+elsewhere summed into "Other" — no per-country fields exist) · EOS → `EOS Business`
+ `Implement EOS` derived from one answer · M&A multi → the four legacy fields (`Bought a
business`, `Sold a business`, `purchased or sold`, `Acquiring Ecom Business?`) via contains() ·
numeric gross margin → legacy `Gross Margin` buckets · activities + explanation → the two
app-v3-reused fields · benefits ranking → `Rank Member Benfits` · staff location → `Staff located`.

Rows deleted + re-replayed a third time; verified per row: Ian China 90 → `76-99%`, purchased+sold
→ both checkboxes true + Acquiring No; Damon EOS → Yes/Self-Implemented, gross margin 40 → `> 30%`,
staff LATAM; Tabrez margin 30 → `15% - 30%`, benefits ranking joined in order. **39 questions
remain with genuinely no existing field** — tariffs, pay bands, cost-structure block, matrices,
staffing/team rosters, handling Qs, ai_depth, ratings, screening — Andy/Eugene field-creation call.

---

## 2026-08-05 (later) — CENSUS SYNC v2: app v3 is the reference — 39 fields, dual channel mapping, TTM seeded

Andy's direction: *all form responses land in the Forms table; reuse as many existing fields as
possible; app v3 = first reference; check field descriptions; revenue per the docs.* Read CU
**§G2/page 06** (`2531q-67177`) first-hand + extracted app v3's full **75-field mapper with AT
field descriptions** as the mapping reference.

**v2 changes (35 → 39 fields):** `Total TTM Revenue` **seeded = reported** (the §G2 model; the
census-gated Members lookups read this field) · the four **legacy bucket fields** (`Amazon US &
% of Revenue` / DTC / Tiktok / Retail) computed from the raw %s with app v3's exact brackets —
the doc's "dual channel-% mapping" · `Name` = **full name unsplit** (app-v3 convention; dropped my
first/last split). Deleted the 3 v1 rows, re-replayed all 3 through v2.

**Verified per row:** Damon — Unverified 4,000,000 · TTM 4,000,000 · Amazon 72 → `51%+` · TikTok
18 → `16%-25%` · linked. Tabrez — 2,500,000 · Amazon 100 → `51%+` · TikTok null → null (bucket
skips empty, no fake N/A). Ian — 1,000,000 · TikTok 5 → `<=5%`. **Members-side: Most Recent
Revenue = the census figure for all 3.**

**Flagged:** Members `Total TTM Revenue` / `Maximum TTM` lookups still show OLD census values —
their per-field conditions are gated to the legacy census Form IDs, and lookup conditions cannot
be edited via the API. Andy: either add "Annual Census 2026" to those conditions in the AT UI, or
treat `Most Recent Revenue` as the field of record (§G2 already says to trust it). **52 refs
remain unmapped** (no AT field exists) — decision list in the census memory.

---

## 2026-08-05 (night) — CENSUS: the live form now SYNCS to Airtable (Make 4860042, mirrors app v3)

**Project = Census rebuild.** Andy: census completed/launched; *"step one, its not synced at all —
lets work on this and on forms in general."* Verified live first: form `DFeK5yop` retitled **"MDS
Annual Census 2026 (Live)"** (Eugene restructured it Aug 4 — ~87 refs, pay bands, tariffs, cost
block; backups `KSQ9sVyq` + `LbQtet4c`), **10 completed responses, 0 in Airtable, no webhook, no
scenario** — truly unsynced. Only 3 responses carry answers (Tabrez · Damon · Ian); 7 are
zero-answer test walkthroughs.

**Built Make scenario `4860042` "MDS Annual Census 2026 -> Airtable"** mirroring app v3 (4784286):
Typeform webhook-INSTANT (hook `2790200`) → create Forms row (`tblblwPcgqhkPTVec`, **35 fields
mapped**, `Form ID = "Annual Census 2026"` via typecast) → member search
`LOWER({Preferred Email})=LOWER(email)` → link `Link to Member (restored)`. **Revenue per §G2:**
`ttm_revenue` → `(NEW) Unverified Revenue` (never `Total TTM Revenue`), `ftm_revenue` →
`Projected FTM Revnue`, channel %s → the `(NEW) … % (raw)` quartet.

**Proven E2E on real data:** Tabrez's organic submission flowed through the live webhook; Damon +
Ian replayed (webhook envelope rebuilt from the Responses API + form definition, POSTed to the hook).
**All 3 rows in AT, all member-linked; Damon's Members row now shows Most Recent Revenue =
4,000,000** — the census → reported-revenue pipeline works end to end. One bug found + fixed
mid-build: Make record-link values must be ARRAYS (`["{{3.id}}"]`) — bare id = `[422] Value is not
an array of record IDs`. One replay duplicate (Tabrez) deleted.

**Flagged, not silently dropped:** ~50 refs have NO AT field (screening, mfg %s, tariffs, matrices,
pay bands, cost-structure block, benefits_rank, ratings, activities…) — needs Andy/Eugene: create
AT fields vs leave Typeform-only (Olivia #20 can read Typeform directly). **No hidden field on the
live form** — matching is by typed email until personalized links ship (Andy's own July concern).

---

## 2026-07-29 — Tools-health: **"Member profiles ← Airtable sync" red was REAL — GitHub cron delivers ~half the hourly runs**

**Project = Tools-health dashboard.** Second alert Andy pasted: 🔴 **Member profiles ← Airtable sync — last write 4h ago** (generated 03:15 UTC). **Opposite verdict to yesterday's: this one was a true staleness, and the monitor was right.**

**Which leg fired.** `olivia-at-sync` probes TWO writers and surfaces the worse: `member_profiles` (daily) + `events_catalog` (hourly). Reconstructed the moment of the alert: `member_profiles` newest was 07-28 15:55 UTC (11.3h — inside the healthy daily band), so it was the **events-catalog hourly leg**. Confirmed by GH: `events-catalog-hourly.yml` ran **22:16, then 23:17, then nothing until 03:37** — a **4h20m gap** in an hourly job → `freshnessHourly` >3.5h → DOWN. Exactly the "4h ago" on the card.

**The sync is NOT broken — GitHub's scheduler is.** Over 60 consecutive scheduled runs (07-23 23:12 → 07-29 03:37): **60/60 success, zero failures.** But actual delivery is **median 1.92h · mean 2.11h · max 4.34h** against a declared `cron: "17 * * * *"`. Against the monitor's bands (healthy ≤1.75h · degraded ≤3.5h · down >3.5h): **41% healthy / 47% degraded / 12% DOWN**. Worst gaps all cluster **00:00–08:00 UTC** — GH shared-runner cron congestion. The cron comment even says `# off the top of the hour to dodge GH congestion`; that mitigation is not working. Expect this red ~every other night until the trigger moves.

**Data gotcha found:** `digest.events_catalog.synced_at` is a **full-refresh stamp** — every run rewrites all 1,419 rows, so the table holds NO history of prior runs (a gap query over it returns empty and looks reassuring). Run history must come from `gh run list`, not from the table.

**Current state: healthy, verified.** 03:37 UTC run succeeded; `events_catalog` 0.91h stale, `member_profiles` 12.6h stale (its 07-28 15:53 scheduled run succeeded — the 3-day HNSW/timeout failure fixed on 07-27 is holding). Prod triage `?tool=olivia-at-sync` → **`healthy`, `isReallyDown: false`**.

**NOT fixed, deliberately.** The root cause is GitHub cron unreliability; the fix is to trigger from **n8n via the `workflow_dispatch` API** (n8n's cron is punctual — the WA digest fires at `11:00:00.197Z`), keeping the freshness check as backstop. **Blocked on a GitHub PAT with `actions:write`, which only Andy can create.** Explicitly did NOT widen the freshness bands — that would mask a genuinely 4h-stale events catalog that Olivia answers from. Awaiting Andy's go.

---

---

## 2026-07-28 — Tools-health: **"Raw message capture → Supabase" red was a MONITOR BUG**, fixed + shipped

**Project = Tools-health dashboard** (`digest.mds.co/admin/tools-health`, code in `mds-digest-web/src/lib/tools-health/`). Andy pasted the Slack card: 🔴 **Raw message capture → Supabase — last write 6h ago** (generated 17:15 UTC).

**The tool was never down.** Forced live checks: n8n **`qo3qzeVtprhTW88F`** ("MDS WA Digest - Daily V1") exec **51110** ran 11:00:00→11:05:38 UTC **success**, and `digest.wa_messages` took **151 rows between 11:00:10 and 11:03:37 UTC**. Last 10 days all identical — every day writes at 11:00–11:07 UTC, 6/6 recent n8n execs green. The ingest was healthy the whole time.

**Root cause = a shared threshold calibrated for the wrong writer.** Commit `9637c99` (2026-07-22) added the hard *"today's run did not complete"* rule to `freshness()` in `olivia.ts`, with **hardcoded `runWindowUTC = 12:00` and `deadlineUTC = 17:00`** — correct for **member-profiles-sync (~13:47 UTC)**. But `rawCaptureCheck()` calls the *same helper*, and its writer is the **daily digest at 7am ET = 11:00 UTC (EDT)** — which **always** lands before the 12:00 window. So `now > 17:00 && lastWrite < 12:00` was true every single day: the tile flipped **DOWN at 17:00 UTC daily, ~6h after succeeding on time**. It had been false-alarming every day since 2026-07-22.

**Fix (shipped `c3cb5f7`, pushed to main, deployed — `/api/version` confirms).** Made the window **per-writer**: `freshness(iso, writer, {runWindowUTCHour, deadlineUTCHour})`. member-profiles-sync keeps `12:00/17:00`; raw capture gets **`10:00/14:00`** — clears **both DST regimes** (11:00 UTC EDT / 12:00 UTC EST) with margin, and still catches a genuine miss **2.5h earlier** than the old rule.

**Verified three ways.** (1) `npx tsc --noEmit` clean. (2) Ran the **actual shipped `getOliviaHealth()`** against prod Supabase → `rawCapture: healthy`, `atSync: healthy` (no regression on the default window). (3) Truth-table over the new window: EDT on-time → healthy, EST on-time → healthy, **real miss checked 14:30Z → DOWN**, real miss 17:15Z → DOWN, 3-days-stale → DOWN, pre-deadline 13:00Z → no false alarm. Then prod: `/api/health/triage?tool=olivia-raw-capture` → **`status: healthy`, `isReallyDown: false`**, and the full dry report → **0 non-green tools on the whole board**.

**Lesson worth keeping:** a freshness threshold is only valid for the schedule it was written against. `freshness()` was reused across two jobs that run 3h apart, and the reuse silently inverted the verdict for one of them. Any shared staleness helper needs the writer's schedule passed in, not baked in.

**Flagged, not touched (not the job).** `src/lib/tools-health/fb.ts` has a **pre-existing uncommitted** change from an earlier session — schedule-aware weekly freshness for the FB scrape (flags a missed Mon 1am CT run immediately instead of waiting for it to age past 8d). Same class of fix as this one. It typechecks and is NOT deployed. Andy to decide whether to ship it.

---

---

## 2026-07-28 — AT→GroupOS tag sync: **TikTok Channel tag SHIPPED**, `test` tag killed, WA link bug fixed

**Project = AT→GroupOS tag sync** (Members DB `appou5JVr0WIrioWS`/`tblfwOSROSHfuYUxv` → formula `Tags n8n` `fldmSp9T859pfJ1jp` → AT automation **"Tang n8n" `wfljyfEMavJBMliIq`** → n8n webhook `aa86a448-…` → GroupOS app). Doc: `GROUPOS_TAG_SYNC.md`. Andy's ask: tag everyone in the **MDS TikTok WhatsApp chat**, backfill + keep updated, and drop the scratch `test` tag. Constraint he set: **no new n8n** — Airtable-only.

**The count.** WA DB (`appT9TVZWhv7io4CN`/`tbli8B589iNbsGF0Z`) has **139 rows** with `MDS TikTok` in `channels_present` (WhatsApp UI says 138; the Chats table's own `member_count` said 137 = stale counter, `channels_present` is the fresh one — Whapi Sync `Lo45BM43boK1gM19` ran clean today, exec **51083**). Of the 139: **132 matched** to the Members DB → **131 distinct people** (Leo Limin has 2 numbers, both in the chat) = 98 Current + 22 New + 10 Staff + 1 no-status. **7 unidentified**: 2 rows with no phone, MDS Bot, Chip Ge (+1 786-863-0984), and 3 bare numbers (+63 917 270 3130, +40 738 610 340, +1 862-276-1269).

**Bug found + fixed (was silently dropping people).** The Members-DB-side link `Whatsapp Channels Sync ` (`flduRPYGBCcvbuZWW`) was **485 linked of 579 matched** — 94 missing. Cause: matcher `4B79OVfyT2a9a3Xt` node **Build Link2 Ops** only emits an op when `action==='match'|'clear'`, and it skips silently when `Find WA Mirror` returns 0 rows (mirror is an Airtable **synced** table, so it can lag the WA DB at the moment of matching) → a race that never self-heals. For TikTok this hid 7 people incl. **Daniel R, the new joiner**. Backfilled all 94 via API (10× PATCH batches, all 200) — union-merged for the 4 members who already had a link to a *second* number's mirror row, so nothing was clobbered. Now **579/579**. This also repaired the `WhatsApp Number` lookup for those 94.

**Built (Airtable only, no new n8n).** Members DB: (1) lookup **`WhatsApp Chats (live)` `fld9AnxtGiI1v6pez`** = `channels_present` through the sync link — self-updates with the 6am ET Whapi sync; (2) formula **`TikTok Channel Tag` `fldHWMuPnlBcnSgTg`** = `IF(FIND("MDS TikTok,", ARRAYJOIN({WhatsApp Chats (live)}, ", ") & ","), "TikTok Channel", "")` — the trailing comma makes it an exact token match so a future `MDS TikTok Ads` chat can't false-positive. Then **`Tags n8n` slot 3 swapped from `{test}` → `{TikTok Channel Tag}`** — same 3-slot `#%$*^` shape, minimal diff, consumer untouched. All three fields have descriptions stamped.

**Verified LIVE.** Airtable: **131** records emit `TikTok Channel`, **0** still emit `test` (719 did before). GroupOS: tag **"TikTok Channel"** `6a68c837c32aac77a6a336cf` **created 2026-07-28T15:18:15Z**, seconds after the formula flip → proves the whole chain fires (incl. that an Airtable *formula-definition* change triggers "Tang n8n", and that GroupOS auto-creates an unseen tag name). Sample: Leo Limin `Event Access - Founder#%$*^Pacific Northwest Chapter#%$*^TikTok Channel`; a non-TikTok member now ends in an empty slot instead of `test`.

**Andy confirmed in the app: 131 members carry the tag in GroupOS** — matches Airtable exactly, incl. the 10 Staff. Fully closed end-to-end. (Per-member assignment isn't visible to my public-tier PAT — `tags_list.usage_count` null, `members_get` returns no tags — so the app UI is the only way to check that side.)

**Matcher race FIXED same session** (Andy approved). Added a self-healing **`Reconcile: *` branch** (5 nodes) off `Daily 8am ET` in `4B79OVfyT2a9a3Xt`: `Unlinked Mirror Rows` (mirror rows where `match_status='matched'` AND no `Members` link — the exact set the main path drops) → `Split Rows` → `Find WA Row` → `Build Link Ops` (logs every skip, never silent) → `PATCH Mirror Link`. It writes the **mirror** side of the two-way link deliberately, so it can only ADD — it can never replace a member's link to a second phone's row. Filtering on `match_status='matched'` excludes the 62 genuinely-unmatched rows, so the single 100-row page can't be crowded out; normally returns 0.

**Verified LIVE, non-destructively.** Clearing a link to stage a repair was blocked by the tool classifier, so instead I temporarily pointed the reconcile filter at one row that was *already* linked (Menachem Lipszyc, non-TikTok so no tag could flap) — the repair then writes the identical value back. Exec **51369**: all 5 nodes ran, PATCH returned `Members: ["recJFV0r5eLynJlp2"]`. Every node exercised on real data, zero data change. Then restored the filter, removed the temp webhook wiring, bounced. After: **579 linked / 62 unlinked-and-unmatched / 131 TikTok tags** — unchanged. `n8n_validate_workflow` clean (20 nodes, 0 errors), published graph re-read to confirm.

⚠️ **Two n8n accounts.** MDS = **`mdsco.app.n8n.cloud`** (what the MCP is on, where all these workflows live). The Tags-n8n consumer is on **`groupos.app.n8n.cloud`** — a *separate account*, not another project. Cost me a 404 chasing the wrong host. Also, per Andy: GroupOS **replaces** the member's tag set from `Tags n8n` rather than adding — so a hand-added tag in the app is wiped on next sync.

**SCALED to all 18 channels, same session, ZERO new fields.** Andy: "I don't like the idea of creating 17 additional fields — we have a limited number of fields in AT." Solution = the same SUBSTITUTE trick slot 1 already uses on Event Access: **repurposed** `TikTok Channel Tag` → **`WhatsApp Chat Tags`** (same id `fldHWMuPnlBcnSgTg`, so `{Tags n8n}` needed no edit — it references by field ID) with formula `SUBSTITUTE(ARRAYJOIN({WhatsApp Chats (live)}, ", "), ", ", "#%$*^")`. The whole chat list becomes separate tags in one field. Net **-1 field** vs the TikTok-only design, and a brand-new channel now needs **no work at all** — flag it active in the Chats table and the 6am sync carries it through to a new GroupOS tag. Tag name = chat name (Andy approved over mapped names).

**Verified:** all **18 tags auto-created in GroupOS at 16:05Z**, exactly matching the 18 active chats (the 13 dead/old chats stay out because the Whapi sync only reads active ones). Sample: Serhan Ongur → `Standard Event Access#%$*^NorCal Chapter#%$*^MDS 2026 New Members#%$*^MDS AI & Automations#%$*^…`. **Duplicate-tag worry resolved empirically**: the 4 dual-number members emit repeated chat names (Leo Limin has `MDS TikTok` twice) and GroupOS deduped — one tag object per name, no doubles. `MDS Centurion 20M+` is included per Andy's explicit "I want all" — worth remembering that tag exposes who's in the invite-only $20M+ channel to anyone who can see tags.

**Open / next.** (1) **Andy deleted both dead AT fields** (`test`, `WhatsApp Channels`) — re-verified after: all 3 formulas/lookups still `isValid=true`, `Tags n8n` renders correctly. The GroupOS tag objects `test` `68083a55f7251cf241690dd1` and the interim `TikTok Channel` `6a68c837c32aac77a6a336cf` still exist with nobody on them — not worth deleting, since GroupOS *replaces* the tag set rather than accumulating. (2) The 7 unidentified TikTok numbers are candidates for the Members DB (Chip Ge looks like a real person) — Andy checking.

---

---

## 2026-07-28 — Membership Health Reporting **Phase 2 (A/B/C/D) SHIPPED** + AT dashboard + Stripe-fields doc

**Project = MDS Membership Health Reporting** (CU `2531q-103257`) — NOT the Scorecard leaderboard, NOT Olivia. All built on the Phase-1 weekly report workflow **n8n `BXN69Fg3ERcgplXd`** (now 29 nodes).

**A — recovery marking + the duplicate-snapshot fix.** Added `Status` + `Recovered Date` to Past Due Weekly Snapshot (`tbltfNL8Iue7sScjX`); recovery branch marks a recovered member's prior open rows. **Root-caused the "duplicates":** the snapshot write was a blind POST, so any re-run doubled rows (today showed 7 members × 2 test runs = 14). Fixed → **upsert** (`performUpsert` on `Snapshot Key`, which I changed to `date | member-record-id` so same-name members can't collide). Verified: ran twice → stayed **7 rows**. Proved the Recovered write on one row (then reverted).

**B — non-renewals.** New table **Non-Renewing Weekly Snapshot** (`tblYxnyGw7QC0y6pQ`, has a Member link) + branch: fetch `Current Member- Not Renewing` → upsert snapshot → diff each open row vs the member's **current** status → mark **Recovered** (→ Current/New Member) or **Churned** (→ Removed). Proven end-to-end with 2 seeded rows (→ Recovered/Churned), then cleaned.

**C — reframed from Stripe count-reconcile → mismatch FLAG** (the count-reconcile was redundant given the Make sync; Andy's call after the "Ben Lee is fine" catch). New **`Billing Mismatch`** checkbox on Members (`fldOSxFTQkd57KIbc`): AT status `Removed*` **+ a LIVE Stripe sub that's `active` and >$0** (money leaking after removal). Live check via the workflow's Stripe cred, **self-clearing**, and it **runs DAILY** now (new `Daily 13:30 UTC (mismatch)` trigger wired to *only* the MM branch — verified isolated, doesn't touch Slack/snapshots). Live list went 6 → **3** over the week ($1,540/mo); Carter York cleared automatically after Andy corrected his sub-ID.

**D — dashboard = AT Interface, not a Google Sheet** (Q2). New interface **"Membership Health"** `pbdbqK539jXDxiNWG`: **Now — live** `pagxOoDRO6udzzqjC` (live off Members — Past due / Churned-unpaid / ⚠️ Mismatch / Non-renewing / Recovered-30d, **+ "Failed this month — RAW"** and **"Removed this week"** which Andy added in-UI) and **Trend — week over week** `paghP5Cuh5gbYcpj7` (off the two snapshots). ⚠️ **Airtable interface MCP has create/delete page but NO edit** → any change I make = new page = new URL; so ongoing edits happen **in the Airtable UI** (Andy has edit access via the `/edit` builder URL; changes are draft until Publish). Slack KPI block still pending.

**Fields created** — Members: `Billing Mismatch`, `Days Past Due (live)` `fldz5WliMBUK7cvkY`, `Stripe Link` `flduB7KiWhRFP5KE3`, `AT Link` `fldvHXE9phIMnL3b6` (descriptions stamped). Snapshot: `Status`, `Recovered Date`, **`Amount Owed`** (= `Stripe Amount`, the *actual per-cycle charge* — annual amount for annual subs, not MRR).

**Slack moved** off #automation-tests → **#past-due-churn-recovery** `C0BGTPG3S11`; bot **MDS Review Agent** invited; verified the card posts there. (For test runs I mute the Post-to-Slack node so I don't spam the shared channel — remember to re-enable.)

**Verified against LIVE Stripe** (throwaway n8n workflow, deleted after each): all 11 of July's payment-failures — AT status = live Stripe, **100% match**. Charles Chakkalo & Richard Tesoriero = **1-day auto-retry blips** (invoice failed 7/9, paid 7/10) → correctly *not* stamped as recoveries (2-day rule).

**Docs:** created the **Stripe Fields reference** page — registry CU `2531q-102577` → page **`2531q-67277`** ("📊 Stripe Fields in AT — Reference & How to Read"): every Stripe field, exact source (`price.*` / `subscription.*` per the Make `4470634` map), how-to-read, the 3 traps (MRR≠charge · multi-sub · synced-status-lag), + the fields I made.

**Decisions locked:** Q1 **weekly** · Q2 **AT Interface** (not Sheet) · Q3 use `Recovered Date (Stripe)` field, snapshot-diff = safety · Q4 non-renewal recovery = Not Renewing → Current **or** New Member · C = mismatch flag (count-reconcile dropped) · **dashboards live/rolling** (current-state, last 7/30d) vs **Slack card = weekly snapshot** — they only align at Monday post; "removed this week" filter set to `is after 7 days ago` to match the card's cutoff · **raw "Failed this month"** (blips included) for reconciliation vs **judged "Recovered"** (≥2-day rule) — keep raw + judged as separate layers · `Stripe Next Invoice Date` = the renewal date for active/in-good-standing subs (caveat: not for cancelling/past-due/paused) · best "member since" = `Join Date (PGE)` (+ Source flag) for community join, `Member Paid Date - For Dashboard` `fldbUiTvT4lSSvI1O` for paid/tenure.

**Ops finding (for Tina/Anita):** manual past-due lists undercount — Anita's July sheet had 8, **Stripe shows 11** failed in July ($5,008 MRR; ~**$41,653** actual-amount at stake once annual charges are counted). The 4 missed were fast recoveries a "who's past due now" scan can't see. The dashboard's "Failed this month" now catches all of them automatically → kills the manual sheet.

**NEXT:** (1) **Slack KPI summary block** on the Monday card + ⚠️ Mismatch line (finishes D). (2) **Weekly KPI Snapshot** table — one row per Monday with every count/MRR (the workflow already computes them) → gives churned/recovered **history** *and* makes "this-week" numbers freeze to match the card (kills the rolling-vs-snapshot drift). (3) Update the registry **Weekly Past Due Report** page (`2531q-66317`) with the new nodes/tables/fields. (4) Document the interface in the CU membership-health doc.

---

---

## 2026-07-27 (NIGHT) — Member360: the AT layer had been DEAD 3 days (HNSW index vs 8s API timeout)

**Trigger:** Andy, from a Member360 profile card — *"check if sync is live / why im seeing last sync 3 d ago?"*
The badge was telling the truth. `digest.member_profiles` max `synced_at` = **Jul 24 16:37 UTC**.

**Root cause (one clean chain).** `member-profiles-sync.yml` (mds-digest-web) failed Jul 25/26/27,
all three with the same error at the same place — Airtable pulls fine, then
`batch 0: {"code":"57014","message":"canceling statement due to statement timeout"}`.
Each upserted row fires `digest.trg_derive_member_attributes` → `derive_member_attributes()`, which
writes `member_attributes` **plus two `content_items` rows**. Migration `content_items_embedding_column`
(**20260725055941**) added a **pgvector HNSW index** to `content_items` (493 MB / 36.9k rows), so every
one of those writes started paying index maintenance: measured **~650 ms/row**. At `B=200` that is ~130 s
per statement against PostgREST's **8 s** timeout (service_role had no `rolconfig`, so it inherited
`authenticator`'s 8 s). Batch 0 could never finish. Timeline is exact: last success **Jul 24 16:37** →
HNSW index **Jul 25 05:59** → first consistent failure **Jul 25 14:49**.

**Fixed**
- Migration **`member_attributes_skip_noop_writes`** — all three derived upserts (`member_attributes` +
  both `content_items`) now carry `IS DISTINCT FROM` guards, so an unchanged member costs a read, not an
  indexed write. Trigger also skips status-less mirror rows (4,421 of 5,751) unless they have an
  application on file. **~650 ms/row → ~15 ms/row** (EXPLAIN ANALYZE, 20 rows = 298 ms).
- `alter role service_role set statement_timeout = '60s'` — an 8 s API-facing default is the wrong
  governor for a batch ETL.
- `scripts/backfill_member_profiles.py` **B 200 → 50** (commit **3613575**, mds-digest-web).

**Andy's correction (drove the second half).** *"It's not a big win… all the changes, for the most part,
are happening with those whose status is not empty. 200 members updated in a day is normal."* Correct —
the status filter only shields against bulk AT edits, and the no-op guard is the real win. But it exposed
the remaining hole: an **unchanged** row is 15 ms while a **changed** row is still ~650 ms, so 200 changed
members landing in one 200-row batch = 130 s and we are straight back to the timeout. Hence B=50 (worst
case ~33 s, inside the 60 s ceiling) rather than leaving B=200.

**Verified live**
- Run **30309579195** ✅ (guards only) then **30310128926** ✅ 4m34s (B=50). `member_profiles`:
  **5,755 rows, all 5,755 written, `synced_at` fresh**. 3-day backlog moved only **16** attribute rows /
  32 content rows — proof the other ~5,700 daily writes were pure churn.
- **`scripts/olivia_leak_gate.py` GREEN — 146/146** (content_items + member_attributes are Olivia's
  retrieval tables, so the gate is the ship condition).

**Watch next**
- HNSW maintenance cost grows with `content_items`. The 650 ms/row changed-path is the ceiling that
  matters — if a real bulk AT edit ever pushes a 50-row batch past 60 s, drop B again or move the derive
  out of the row trigger into a set-based post-pass.
- `member_attributes.refreshed_at` now only moves when something actually changed (nothing reads it today).

---

---

## 2026-07-24b (WA DB — 114-member create-gap found + backfilled · full field-provenance audit · Whapi Sync create-fix SHIPPED · my own engagement-backfill error corrected)

**Trigger:** Andy asked why Alex Lushington (member, "in TikTok chat") wasn't in the WA base. Answer: his number `12053442149` is in NO group (verified against live participant lists of all 44 groups); the Alexes in TikTok are Anh Doan / Alex Yale / Alex Bonilla. But the hunt exposed the real hole.

**Found + fixed (verified live)**
- **Create-gap:** 114 people were participants of ACTIVE chats with no WA Members row (base 526→640). Root causes (all verified in code, not docs): (a) rows are only created by the digest's `Upsert Sender to Members` on a **text** message — media/link/`unknown`-type senders (~10% of 13,860 sampled events) and silent joiners never got rows; (b) **Whapi Sync `Lo45BM43boK1gM19`** (6am ET) already pulls every active chat's participants daily + maintains `channels_present`/`member_count` **but only updates existing rows**; (c) no catch-up window anywhere.
- **Backfill:** created all 114 rows (phone+channels+pushname where known). 81 matched by exactly-one phone hit; 11 more via **Andy's status rule** (dups expected → disambiguate on non-blank/ACTIVE `AT Database Status` — rule now written at the top of the matching memory); 1 unresolvable (TESTTEST/Dan Mcgill both status-blank); 21 no-match. All matcher-compatible (same rules as `4B79`).
- **PERMA-FIX SHIPPED:** Whapi Sync + 2 additive nodes (`Compute Missing Members` → `Create Missing Members`, batched 10/rec, 4 req/s), zero existing nodes touched, validated 0 errors, ONE deactivate/activate bounce. **Live proof pending: tomorrow's 6am ET exec** (expected ~0 creates steady-state; verify exec + no dup rows).
- **MY ERROR, corrected:** I backfilled 99 DailyActivity rows + 19 msgs_7d/30d counting `unknown` events as messages — prod counts only text+reactions → 98/99 were worth zero (and the 1 "keep" was a dup of an existing row). **Deleted all 99, reset the 19 stat rows** (Daniel Rybakov keeps real last-active 2026-05-15) before the next 11:00 UTC digest run could re-read them.

**Field-provenance audit (all 36 Members fields; writers verified in code + live spot checks)**
- Writers: digest daily (phone/name create + msgs_7d/30d/last_active_at), Whapi Sync (channels_present add+clear), matcher `4B79` (Member/source_member_id/source_member_link/email), portal digest-web (otp_*/session_*/subscriptions/onboarding/delivery_email), Olivia chain `12wj`→Supabase→`BfLq` 7:30am (Olivia Interactions/Last Active/Welcomed), formulas/lookups (match_status, channels_count, AT Database Status, Member Full Name, Most Revent Revenue [sic]).
- **NEW DEFECTS FOUND:** (1) **daily stats lag one day** — proven with exec 42310: rollup fetched DA at ~11:00–11:04, yesterday's 51 DA rows were written 11:04:09–11:05:13 (n8n runs the dangling save-branches last) → msgs_7d/30d/last_active always exclude yesterday; (2) **dead fields:** `last_updated` (421 rows stamped genesis 2026-04-23, no writer since), `delivery_email_verified` (no setter exists in code, 0 ever set), `subscribed_channels` + `frequency` (legacy, dead per code comment since 07-02); (3) 12 rows with NO phone + 9 WhatsApp-LID rows + 1 Twilio test number (junk rows, kept — Andy to decide); (4) `Update Members` runs 20 req/s vs Airtable 5/s cap (latent 429).
- Also: 5 Removed/Cancelled members still sit in groups (Murat Dilek, David Young, Jonathan Craddock, Catalina Leyva, Andres Murillo) — surfaced by the backfill.

**Awaiting Andy**
- Fuzzy-match confirmations (NO writes done): 🟢 Angelo Mario Filho, Chip Ge (status-blank record), Douglas Patrick Iske, Tobias Heckmann, Logan Chierotti, Gennady Belkin, Ian Sells (+373 Mogul) · 🟡 Ulrich Kratz, Ji Luo, Valentino Saint Lavigne, Ross Goodhart · 🔴 no candidate: Thomas (CY), David (512), Bill Sterry, Filip Anhera. Apply via full bundle + `WhatsApp Number (Verified)` where DB phone differs.
- Decisions: fix rollup 1-day lag? kill/repurpose dead fields? should media/link posts count as engagement? clear the 22 junk rows?

**Next session:** verify Whapi Sync 6am exec (creates=~0, no dups) + 8am matcher confirms the 92 backfill matches; then Andy's fuzzy confirmations.

---

---

## 2026-06-15 (cont.) — ALL tools-health domains wired LIVE + digest.mds.co portal hardened (auth / Violet theme / admin Digests)

> Same project, continued (app = `mds-digest-web`, Render, push `main` → deploy). Full running detail also in memory `project_mds_tools_health_dashboard.md`.

**State at session end:** Tools-health board reads **100% live** — 27 tools, all 7 domains, no dummy. The digest.mds.co **portal is hardened**: Members (AT-gated → digests only) vs Admins (`@mds.co` → every page), a new read-only **admin Digests** view, dark mode + shadcn **Violet** theme, dev-only QA login. Andy DoD-QA'd green (admin sees all incl. digests; member blocked from `/admin*` even by direct URL).

**Wired every tools-health domain live** (was WhatsApp+FB only). Reusable adapters in `src/lib/tools-health/`: `n8n.ts` (per-workflow facts + classify + pipeline rollup; event-driven vs scheduled; infra error-check **24h-windowed**), `make.ts` (us1 zone, `reached` flag, pipeline), `intercom.ts`/`scorecard.ts` (AT freshness), `uptime.ts` (HTTP ping). `page.tsx` routes live tools by `source`. Domains: Members (Deletion Trap + Intercom; **Honorary REMOVED**), Events ($500 credit + Luma→Webflow + 3 Make — needed `MAKE_API_TOKEN` scope `scenarios:read`), Leads (WF1/WF2/WF3 rollup), Revenue (MRR + Onboarding Observer [429 fixed → 15-min poll] + Stripe Make), Apps (Web Portal / Skill Base / AI Bot / Video Platform via uptime; **mds-admin-pages retired**). Dates "Jun 15, 2026". Doc links added to all but Members Deletion Trap.

**Portal auth:** admin gate in `src/app/admin/layout.tsx` = `sess.email.endsWith("@mds.co")` → else redirect `/` (NOT AT, NOT the dropped ADMIN_EMAILS allowlist). `@mds.co` staff who aren't AT members log in via a **stateless OTP** (`src/lib/staff-otp.ts`: signed `mds_otp_ticket` cookie; request-otp/verify-otp branch on `isStaffEmail()` → member-less session `memberId="staff:<email>"`). Verify redirects `@mds.co`→`/admin`, members→`/dashboard`.

**Admin Digests:** read-only `/admin/digests` (`AdminDigests.tsx` + `listRecentSummaries()` all-chats; channel filter + markdown) — added to AdminNav (member `/dashboard` needs a member row, so admins get this).

**Theme:** shadcn **Violet** preset in `globals.css` (`:root`/`.dark` OKLCH + sidebar/chart; dark `--primary` hand-brightened 0.398→0.637 for contrast). Member pages converted hardcoded zinc/blue → semantic tokens (bg-card/muted/accent/background, text-primary, border-border).

**QA:** dev-only `/api/test-login` (secret-gated `QA_LOGIN_SECRET` in gitignored `.env.local`; **404 in production**) → session without OTP for flow QA.

**Decisions:** all tools live · admin = `@mds.co` only (allowlist dropped) · `@mds.co` auths without AT · member dashboard stays personalized + admins get separate read-only digests · theme via shadcn Violet semantic tokens · n8n infra errors windowed to 24h.

**Open / next:** (1) daily/weekly filter on /admin/digests; (2) lazy-load/paginate /admin/digests (300 digests = heavy); (3) optional Base-UI primitive migration; (4) per-dependency Infra checks for the mobile stack; (5) `/admin` unauth still triggers Overview's AT fetch in parallel with the redirect (middleware = cleaner fix).

* * *

---

## 2026-06-15 (Tools Health Dashboard) — scanned all MDS tools, built + deployed the health dashboard, wired the real dependency monitor, fixed the FB capture extension

> **Different project from Scorecard scoring** (shares this working dir). Full running detail: memory `project_mds_tools_health_dashboard.md` + local docs `TOOLS_HEALTH_INVENTORY.md` / `MDS_TOOLS_LIST.md` / `MDS_TOOLS_REVIEW_WhatsApp.md` (NOT committed — Scorecard repo is public).

**State at session end:** Live at **digest.mds.co/admin/tools-health** (a "Tools" tab in the admin portal). Whole tool registry (~29, Andy's scope) grouped by domain; **WhatsApp + FB rows on LIVE Airtable data**, everything else clearly badged DUMMY. Light/dark toggle across the whole portal. **Real dependency monitor** (Infrastructure section): n8n errors, Whapi number-block, Anthropic credit-failure — all LIVE on prod; FB-offline via scrape-date freshness. FB Chrome-extension Insights bug **fixed + verified** (needs a `chrome://extensions` reload to take effect). **Pending: #5 — fix the n8n Onboarding Observer 429.**

**Built / done**
- Scanned n8n (45 wf) + Make (162 scen — 3 builders: Andy 11 / Carmel 22 / Eugene 20 active, via API `createdByUser`) + 12 CU docs + local repos. Found ~25 live automations (not the 11 Andy listed).
- `mds-digest-web`: route `/admin/tools-health` (server component, `force-dynamic`); `src/lib/tools-health/`: `registry.ts`, `whatsapp.ts` (Org Stats), `fb.ts` (FB Engagement `Reporting Date (scrape)`), `n8n.ts` / `whapi.ts` / `anthropic.ts` (Infrastructure checks). Folded into `/admin` (AdminNav "Tools" tab, `ThemeToggle`, `LogoutButton`). Whole-portal dark mode: globals `.dark` block, `next/script` no-flash init, recharts theme-aware via `useIsDark`.
- Render env added by Andy: `N8N_API_URL`, `N8N_API_KEY`, `WHAPI_TOKEN` → n8n + Whapi checks went live. (Also in local `.env.local`, gitignored.)
- Fixed `mds-scorecard-tools/extension/background.js` `clickInsightsDownload()` — FB's 2026 UI is native `<input type=checkbox>` (old code matched `[role=checkbox]` → matched nothing). Now matches by `aria-label` + native `.click()`. Verified live via Claude-in-Chrome. In-place edit (not a git repo).

**Commits (mds-digest-web, main → Render auto-deploy):** `60a5b67` POC · `b3598af` dark+portal · `b2bccf8` FB live · `bf0f42d` infra monitor · `02fd246` n8n degraded-not-down.

**Decisions:** scope = Andy's tools only · hosting = **Render, NOT Vercel** (README stale; deploy = push `main`) · Anthropic has no balance API → detect blank-summary failures instead · POC deployed ungated (beta) · ClickUp docs can't be tagged via API · n8n reachable-with-errors = degraded (not down).

**Verified:** 6/15 1am FB run completed (import OK; contributors 96, 750 rows, roster 753); dashboard FB → 6/15 fresh; n8n monitor caught 41 error runs / 5 workflows; Whapi healthy (`auth`); Anthropic healthy.

**Next steps (specific)**
1. **#5 — `IPTLQHFTPpdplueT` (Onboarding Slack Observer):** Airtable **429** on the Members-table trigger (errs 6/14/6/13/6/12). Add `retryOnFail` + backoff on the failing Airtable node, or reduce the trigger poll frequency.
2. **Andy:** reload the FB extension (`chrome://extensions` → MDS Scorecard Capture → ↻) to apply the `background.js` fix.
3. Verify next Mon 1am FB run auto-completes (no manual tick) + dashboard FB date flips.
4. Wire remaining DUMMY domains to live (Members / Events / Leads / Revenue / Apps) — same pattern as WhatsApp + FB.
5. Optional: gate `/admin/tools-health` via `checkAdminAccess()` in `src/lib/admin/access.ts`.

* * *
