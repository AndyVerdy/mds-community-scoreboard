# Olivia — next session (handoff, written end of 2026-07-21)

Paste this file to resume. Canonical doc: `MDS_OLIVIA_ASSISTANT.md` (§8b–§8i + §9 + changelog
supersede §1–§8). Source registry: `MEMBER_ATTRIBUTES_SOURCE_MAP.md`. Full session narrative:
`SESSION_LOG.md` (newest entry 2026-07-22). **Verify against LIVE systems, not docs.**

## ✅ 2026-07-22 SHIPPED — EVENT CHAPTER-GATE · sync reliability · dashboard alert · session hooks

- **Event chapter-gate LIVE + leak-gated (gate = 114 green).** `event_lookup` now hides chapter
  events from non-chapter members (was fully open — Andy, no chapter, was shown a Vegas dinner).
  Member: `member_attributes.chapter_affiliation` + `chapter_ids` (Chapters record-links, filled by
  BEFORE trigger `fill_member_chapter`; big `derive_member_attributes` untouched). Event:
  `events_catalog.chapter_ids` from the AT **`Chapter` link** (NOT `Chapter Area` — dropped; use the
  "In Person Events – Upcoming Management" view, not the whole 368-field table). Gate = record-link
  overlap; Public/non-chapter→all; chapter-styled-but-untagged→**fail-closed**; Postponed/Canceled
  dropped. Verified: Talor (Vegas)=27 events, Andy (none)=0. **Admin/finance fields hard-excluded at
  ingest + output + gate** (14-field allowlist). Migrations: `member_attributes_chapter_fields`,
  `events_catalog_chapter_ids`, `event_lookup_chapter_gate`, `event_lookup_chapter_gate_failclosed`.
- **Sync FIXED** (was failing Jul 18/19/22, frozen a day+): `curl_json` retries on empty/5xx/timeout
  (commit 9637c99). **Dashboard `atSync` tile flips RED same-day** on a failed run + covers events
  (was soft-amber-only → the failures were invisible; that's why you weren't notified).
- **Doc-drift HOOKS** (`.claude/settings.json`): SessionStart auto-loads this file + SESSION_LOG tail
  (this is why you're reading it); Stop = once-per-session wrap-up reminder. May need one `/hooks`
  open to register.

## ▶️ NEXT ACTIONS
1. **✅ Router fix DONE + verified (2026-07-22)** — deterministic `conceptQ` demote in `Plan Request`
   (help→question for definitional Qs about a topic); bounced + live-tested (13-Q bank). Also SHIPPED
   this session: **hourly events-catalog sync** (`--catalog-only`, `events-catalog-hourly.yml`) and
   the **analytics dashboard ET-timezone + Today/Yesterday presets** (commit 43be0aa). NEW next items:
   **(a) wire events into the problem/solve path** — the test showed Olivia never suggests an event
   for "help me / meet people in person"; **(b) lane location-consistency** — the event lane uses
   Andy's city but the people-search lane says "I don't have your city"; **(c) analytics exclusion
   toggle** — Andy (17866578153) is excluded, so his own-testing days read 0 (offered a toggle).
   Full detail in `SESSION_LOG.md` (2026-07-22 entry).
2. **⚑ Flag events team** — "New York Chapter Pickle & Padel Social July 2026" (Jul 28) has no
   `Chapter` link → hidden from everyone until Keziah/Debbie tag it. (Query in SESSION_LOG.)
3. **Staff bypass (Andy confirmed 2026-07-22)** — for NOW staff are treated as **normal members**
   (strict gating = correct, already live). LATER: staff should **bypass ALL gates** (see everything).
   Implement when ready: short-circuit to full visibility in `event_lookup` (+ other gated RPCs) when
   the asker's `member_attributes.membership_status = 'Staff'`.

## (deferred) KNOWLEDGE BASE (Andy said "decide later")

Andy wants Olivia to answer CS docs + resource lists + events/community FAQs to offload the team.
**The content lives in Intercom** (workspace yn8h04m3, help.milliondollarsellers.com; Intercom MCP
available). 27 articles — but **the ~19 that ARE the FAQ ask are TITLE-ONLY DRAFT STUBS with empty
bodies** (created ~2026-07-04, author 6532986; sampled 4 = all `value:""`). Only ~3 older PUBLISHED
articles have real content. So the KB is scaffolded but UNWRITTEN → nothing to ingest yet.
**Andy picks a/b/c:** (a) team writes the ~19 answers → trivial ingest; (b) **I mine past Intercom
CONVERSATIONS to draft canonical answers for team approval** (real offload, my rec, never invent);
(c) route only what Olivia can already derive live (chapter change, recordings→video, join chats).
When content exists it's the EASY security case: `content_items` sensitivity=normal, all-members,
quote-OK, rides the existing `content_search` RPC. **And it slots straight in as a 5th `multi_source`
section** (add one branch to `digest.multi_source` + one block in Build Prompt's `multi` mode).

## State — all LIVE + verified 2026-07-21 (beta running: Eugene/Ian/Belén)

- **Lanes**: digests · cross-history search · member matching · expertise · chat recs · chat info ·
  events (+past/near-me/trip/own-history) · event who's-going · member cards · dossier · community
  stats (+chapters) · partners (+named-company chat cross-ref) · **help** (capability list) ·
  **solve** (problem → partner+chats) · **multi** (broad launch/expand → partners+members+events+chats
  via `multi_source`) · self billing/plan/price/chapter · action requests · STOP/START · 24h memory · reset.
- **Router = Haiku.** `help` + `solve` + `multi`(hook) are proper router intents (deterministic regex
  kept as backstop in Plan Request). Retrieval = gated fail-closed RPCs ONLY: content_search/lookup ·
  member_match · chat_recommendations · chat_info · event_lookup/who/history · member_card ·
  member_dossier · community_info · expertise_search · partner_lookup · member_billing[self] ·
  **multi_source** (scalable fan-out — composes the gated fns, gating preserved).
- **Global STYLE block** = one block in Build Prompt, prepended to all modes (friendly & upbeat,
  rare functional emoji, WhatsApp fmt). **The single place to tune voice.**
- **Partners (source #3)**: `partners_catalog` 486 + `partner_reviews` 922; categories named 97%;
  `partner_lookup` (FTS+synonyms, dedupes 12 dup pairs, reviewer identity never emitted); URL =
  `member_partner_url()`. Refresh = manual weekly MCP pull (runbook below); no GROUPOS_PAT.
- **Leak gate = 111 checks** (`scripts/olivia_leak_gate.py`) — MUST be green before ANY new source
  ships. **Selftest**: `scripts/olivia_selftest.py --questions "..." ` then ALWAYS `--cleanup`.
- **Relay LIVE + Meta callback FLIPPED to it** (`digest.mds.co/api/olivia/webhook`, commit 1a96549):
  forwards to n8n; n8n dead ⇒ canned "upgrading" reply (15-min limit via
  `conversation_origin='relay_maintenance'`) + 502 so Meta retries. Health tiles: webhook-liveness +
  inbound-silence (mds-digest-web `7717812`).

## WATCH at session start

1. **13:47 UTC daily sync** (member-profiles-sync, 2 steps) — `gh run list --workflow=member-profiles-sync.yml` + health tile.
2. Display name **"MDS Olivia" = APPROVED**; `verified_name` may still read "Oliva" for a day — no action.
3. Andy's real-phone tests — refine router/prompt on any misses (the E2E banks are the regression suite).

## Verified this session (2026-07-21) — don't re-litigate

- 51-question E2E → fixed → 10/10 (`OLIVIA_E2E_ANALYSIS_2026-07-21.md`).
- 12-question multi-source test → essentially flawless (all 6 multi fanned out; named-partner GETIDA
  balanced; cross-lane follow-up "tell me more about the first person" → Bea's card; guards held).
- Privacy never leaked across ~75 adversarial questions this session; every miss was routing (thinner
  answer), never data/hallucination.

## FOR ANDY (waiting on you — small, one action each)

- **KB a/b/c** (above) · **ClickUp credential in n8n** (unblocks CU-ticket-per-request) · **GROUPOS_PAT**
  (auto partners refresh + exposes contact_info websites; Andrii slow — don't wait).
- Report to GroupOS: **2 poison partner records** + **12 duplicate partner pairs** (brackets/queries in
  the registry + this file's git history).
- Members-DB cleanups (Ian Sells Staff junk · dateless "Million Dollar Squads" dup · Trading-call date
  drift) · retention window · rotate `QA_LOGIN_SECRET` · split login number before scale · delete old
  POC wf `Af2atRScbYSOTYbC` (plaintext token).

## NEXT candidates (after the KB decision)

1. **Knowledge Base** (source #4) — lead item, pending a/b/c.
2. **Virtual-events data layer** — topics/speakers/recordings/zoom (Belén owns Mogul/expert/channel
   calls; likely a separate AT table). Would also become a richer `multi_source` events section.
3. **CU-ticket-per-request** — after "Log Request (Supabase)" add a ClickUp create-task node (list
   900801254031, parent 86e2cmjyj, include request + context + member-log link). Blocked on the credential.
4. **Partner offer-clicks** · weekly proactive picks (blocked on template/24h) · videos source ·
   Member 360 restyle · schedule the question report · correction-lane write-back · census sync.
5. Small polish: promote `multi` + `solve` regexes fully into the router if they mis-fire in the wild ·
   request-card context prints newest-first (reverse for readability) · self-card lacks join/tier as
   ingestable fields (last-payment date not mirrored from Stripe).

## SOURCE / CAPABILITY ADDITION CHECKLIST — do ALL every new data layer

1. Registry row in `MEMBER_ATTRIBUTES_SOURCE_MAP.md` BEFORE the data is used.
2. Ingest + gated retrieval fn (or ride `content_search` if KB-style public content).
3. Router (`Route Request`): new intent + examples so real phrasings land.
4. `Build Prompt` / `Build Verbatim`: render the answer. **If it's a source, also add a `multi_source`
   branch + a Build Prompt `multi` block** so it joins the fan-out.
5. **⭐ HELP CAPABILITY LIST** (`plan.route==='help'` in Build Verbatim): add the capability + example;
   remove it from the "Not yet:" line. (Andy's standing ask: keep this message current.)
6. Returning-member GREETING one-liner (Build Verbatim): broaden if the headline set changed.
7. `scripts/olivia_leak_gate.py`: add checks, re-run GREEN before ship.
8. Docs (`MDS_OLIVIA_ASSISTANT.md` §8x + changelog), this file, memory.

## Guardrails (load-bearing)

Gated fail-closed RPCs only · match-don't-quote except public-in-the-app · leak gate green before any
new source touches the prompt · **wf edits: edit ACTIVE, then ONE bounce `[{deactivateWorkflow},
{activateWorkflow}]` — NEVER deactivate before editing** (the 8.5h dead-webhook incident) · `$`-dense
node/jsonBody rewrites = full updateNode, never patchNodeField · POSIX classes in SQL-migration regexes ·
bool_and coalesces NULLs · generated-column helper fns need service_role EXECUTE · content_search
returns verbatim group content (a member's own posted email there is NOT a leak — scrub only structured
sections) · simulated inbounds don't open Meta's 24h window (131047) · AT Events/Roster whole-table
never views · secrets in `mds-digest-web/.env.local` (parse in python, curl not urllib).

## Partners refresh runbook (weekly, until GROUPOS_PAT)

Pull `partners_list` w/ `updated_after=<max(app_updated_at)>` → `ingest_partners.py --partners`
+ `--reviews` (changed) + `--map-categories`; compare `with_total` (published+paused) vs row count —
drift = silent pause/delete → reconcile. Bracket the 2 poison-record windows. contact_info
(website/FB/LinkedIn) is in GroupOS admin but the API strips it — add 3 columns + backfill when a PAT lands.
