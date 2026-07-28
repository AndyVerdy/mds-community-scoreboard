> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Matching fields — where each one comes from

**Scope (Andy, 2026-07-20): ALL member data is matching fuel by default** — every field from
every source feeds matching (hidden, semantic where free-text); the classification rules control
only what SURFACES to a member, never what the matcher may consider.

**SURFACING POLICY (Eugene, FINAL 2026-07-20 night): "public-in-the-app = shareable."** The six
directory-public member fields surface to any member via `member_card`: **Facebook Profile Link ·
About Me · revenue TIER (band only) · Main Niche · Area of Expertise · Hobbies** (+ name / city /
state / fun fact, already public in matches). `shared_chats` = asker∩target chat intersection only.
Who-is-going lists = member names. Everything else (exact revenue, contacts, addresses, channels,
age) keeps the structural refusal. Gate (`olivia_leak_gate.py`, now **114 checks**) enforces per function.

**⚙ 2026-07-22 — CHAPTER (events gating).** `member_attributes.chapter_affiliation` (from AT Members
"Chapter Affiliation" multi-select = SoT) + `chapter_ids` (from "Link to Chapters" **record-links** =
exact match key, immune to name drift); filled by BEFORE trigger `fill_member_chapter()`. Events carry
`events_catalog.chapter_ids` from the AT Events **`Chapter`** link — pulled from the **"In Person Events
– Upcoming Management" view**, NOT the whole 368-field table (`Chapter Area` is blank-prone + WRONG,
dropped). `event_lookup` shows a chapter event only to members whose `chapter_ids` overlap; untagged
chapter-styled events fail closed. Events field allowlist is HARD member-safe — admin/finance/PII
(Partner Revenue Goal, Var/Fixed Budget, Partner Revenue Actual, Min/Max Member+Attendee Goals, Event
Roster Link, Managed By, Host, Clickup) is **never requested from Airtable**.

The table below is the subset needing exact per-field sourcing: the **hard filters** (eligibility
+ precise criteria — bands, flags, location), where a wrong source means wrong numbers. The rest
of the profile (free-text answers, future census/events/GroupOS data) flows into semantic
matching wholesale as each source syncs — no per-field table needed, the source registry rule
still applies (new source → mapped here before use).

Counts = active members with the field filled, out of 743. "Backup" = used only when the main
field is empty for that member.

| What the matcher needs | Field name | Table | DB | Filled | Backup (adds) |
|---|---|---|---|---|---|
| City | City | Members table | Members DB | 711 | City on the application form (+2 → 713) |
| State | State | Members table | Members DB | 709 | State on the application form (+3 → 712) |
| Country | Country | Members table | Members DB | 710 | — |
| Revenue → band only | Most Recent Revenue (+ Most Recent Revenue Verified) | Members table | Members DB | 629 | application revenue answers (+6 → 635) |
| Age → under-30 flag only | Birthdate | Members table | Members DB | 688 | Birthdate on the application form (+5 → 693) |
| Categories / sells supplements | Category | Members table | Members DB | 684 | — (form answers add nobody) |
| Business model | Business Model | Members table | Members DB | 665 | — |
| SKU count (Large SKU chat) | SKU Count - per census/application | Members table | Members DB | 682 | — |
| Brand count | How many brands do you currently have? | Members table | Members DB | 679 | — |
| Expertise | Area of Expertise | Members table | Members DB | 626 | — |
| Main niche | Main Niche | Members table | Members DB | 469 | — |
| Fun fact | Interesting / Fun fact | Members table | Members DB | 420 | — |
| Year started selling | Started Selling | **Forms table (application)** | Members DB | 431 | Started Selling on the Members table (+9 → 440) |
| Title (CEO etc.) | Formal Title | **Forms table (application)** | Members DB | 450 | — (no Members-table field exists) |
| TikTok seller | TikTok Presence (Onboarding) | Members table | Members DB | **41** ⚠️ | — see gaps |

Every stored value remembers its exact field + table + date, so we always know what we're
reading and how old it is.

## The gaps

1. **TikTok: 41 of 743.** The real signal is in the TikTok chat verification Typeform — and I
   haven't verified where those submissions land (Forms table or nowhere). Until that's synced,
   TikTok chat recommendations stay off.
2. **Real Estate chat: no field anywhere** captures property ownership. Olivia can describe the
   requirement, never pre-qualify.
3. **Census forms (735 filled, Forms table) are not in Supa yet.** Likely fresher than
   application answers for revenue/channels/SKUs. When they sync, they slot in as a backup
   source per field — nothing has to be redone.

## Events (source #2 — ✅ SHIPPED 2026-07-20; model per Andy + Debbie huddle)

**Live:** `digest.events_catalog` (**1,412 as of 2026-07-26** — was 49 at write time on 2026-07-20;
the sync now loads the WHOLE historical table: **2018-05-31 → 2027-03-22**, 632 Virtual / 780 other,
incl. **360 named Mogul / Expert / Channel Calls**. Source = `sync_events.py`, AT base
`appou5JVr0WIrioWS` table `tblbDtU6DxpoeZF8i`, hourly via `events-catalog-hourly.yml`. NOTE: this is
CALENDAR data only — name/date/type. The call CONTENT/recordings are a separate unconnected source,
see `VIDEOS_TO_OLIVIA_NEW_SESSION.md`) + `digest.event_registrations` (424; 355 member-linked,
69 guests never surfaced) · daily sync = 2nd step of member-profiles-sync (PR #17) · retrieval =
gated RPCs `event_lookup` / `event_who` (NOT content_items — structured data follows the
chat_info precedent; deliberate deviation from the original content_items plan) · leak gate 57
checks green · router intents `events`/`eventwho` live-verified. Spots left = Venue Capacity −
live roster count. `/admin/` URLs in reg-link fields are sanitized in SQL, never emitted.
**Open flags:** descriptions (Andy checking the app API) · Trading Channel Call date drift (app
Jul 20 vs AT Jul 21 — Virtual rows display AT wall time "as listed") · Puerto Rico Member
Registration Link = admin URL in AT (fix at source) · TikTok dinner Reg Open w/o member link.

**Source of truth: Airtable Events table (Andy's ruling; Debbie's flow confirms every event is
born there).** The app (GroupOS) + Luma are the registration/render surfaces. Verified first-hand
2026-07-20 against all three systems + the Debbie transcript.

**The flow (Debbie):** chapter lead/Eugene announces → row created in AT Events →
`Event Planning Status (Phase)`: Tentative (radar, no date) → Confirmed (date locked, will
happen) → **Registration Open** (reg page exists = the ONLY "alive/registerable" state) /
Postponed / Canceled. Descriptions are written straight into the reg page (app or Luma), NOT
into AT ("we're not giving descriptions here") — reg page stays updated and is SoT for details.

| What | Where | Notes |
|---|---|---|
| Catalog (which events exist) + phase | AT Events, Debbie's view "In Person Events - Upcoming Management" `viwmNcdupIgb6kTdN` | 47 upcoming in-person; ingest Confirmed + Registration Open; skip Tentative; carry Postponed/Canceled as status |
| Audience rule | AT `Guests?` = **MDSonly / Open to Guests / Public Event** (46/47 filled) | answers "can I bring someone?"; Public = Luma-registered, anyone |
| Chapter targeting | AT `Chapter Area`/`Chapter` (sparse) + chapter name in title (reliable) | relevance hint, NOT a secrecy gate (Andy's Dallas use-case needs cross-chapter visibility) |
| Capacity / spots left | AT `Venue Capacity` (sparse, 12/47) + app `sold_count` | only when both exist |
| Member reg link | AT `Member Registration Link` (= always the app link, Debbie) | lags humans (TikTok dinner: Reg Open, link empty — Keziah case); fall back to app event by name+date join |
| Authoritative datetime/tz, marketing title, city, prices | App (GroupOS) `events_list`/`events_get` | AT datetimes drift (Trading call Jul 20 app vs Jul 21 AT) + are tz-naive |
| Descriptions | Luma API for Public/Luma events; app API has NONE (`long_description` null even on Singapore Summit — copy lives in app page-builder); AT `Public Description` 3/59 | v1: title/city/date/audience only, honestly; titles carry topic ("TikTok Strategy Dinner", "Mogul Call with StoreClaw.Ai") |
| Registrations (who's registered where) | **AT Event Roster — WHOLE TABLE, never the view** (`viwrGk8AlHP2hHGiW` filters rows; a view-scoped read shows 7 rows where the table holds all 10 TikTok-dinner rows, Source='MDS App', record-linked to Member AND Event) | the per-registration ledger: rec-id links (not name matching), Order Date, Ticket Type, Source. App→AT sync PROVEN LIVE 2026-07-20. Earlier "roster feed dead" claim = WRONG (view artifact). Member-side rollups (`Upcoming Events Registered`, `All Events Registered` 1,162, `Events Attended` 1,143, `Last Event Registration`) already land in Supa daily via member_profiles. App roster (`events_attendees_list`, email join proven 10/10) = secondary/backstop + sold_count. Matching fuel; name-surfacing per Andy's exposure ruling |
| Virtual calls (channel/Mogul/expert) | AT rows (Type=Virtual, phase unused) + app registration | Belén owns Mogul/channel; expert calls = partnerships; ask her when virtual layer is built |

**Junk guards at ingest:** drop no-date rows, "test"/"new event"/template rows, same-name+same-date
dups (8 pairs exist), the app's "Doina Testing Event".

## Partners (source #3 — LIVE 2026-07-21; Andy's call, Supa over live MCP)

**Shipped state:** `digest.partners_catalog` **486 rows** (= all 488 published minus 2 records the
GroupOS API itself cannot serve — see poison records below) + `digest.partner_reviews` **922 rows**
(reconciles exactly to the sum of every partner's review_count). `category_names` filled on 470/486
(97%): authoritative AT name-join (398) + confident co-occurrence id-map (53 ids). Retrieval =
`digest.partner_lookup()` (dedupes the app's 12 duplicate-name pairs, best record per name).
Leak gate = 100 checks green. Router intent `partners` live; live-fire verified ("tiktok deals" →
Reacher w/ offer + app link).

**⚠️ Poison records (GroupOS API bug, for Andy to report):** 2 of 608 partners are unfetchable —
ANY partners_list page containing one times out deterministically. Bracketed precisely:
(a) created between 2023-10-04T10:23:30Z and 10:24:00Z (between "Onsite Support by Threecolts"
and "Outlinematic"); (b) created between 2024-08-13T07:33:00.766Z and 2024-08-15T08:22:17.000Z
(immediately after "Teamwork.com" in desc order). Id/name unknowable via the API; suspected
oversized/corrupt description. Workaround for refreshes: bracket with created_before/after.

**Source of truth: the GroupOS app partner directory** (community `67011d987a2a81b28438a3d8`),
read via the GroupOS MCP (`partners_list`/`partners_get`/`partner_reviews_list`). The AT Partner
tables (326-field Partners, Offers, Payments, W-9, contacts, pipeline) are the partnerships
team's OPS data — internal, never ingested for Olivia.

**Scope: PUBLISHED partners only (488)** — paused (120) and draft (5) are invisible in the app,
so under "public-in-the-app = shareable" they don't exist for Olivia. Verified counts 2026-07-21.

| What | Where | Notes |
|---|---|---|
| Catalog (name, description, offer, rating, claims, categories) | app `partners_list` → `digest.partners_catalog` | descriptions ARE fully in the API (verified vs app page, byte-identical — unlike events); `offer_value` = the deal label; `offer_description`/`offer_instructions` null everywhere sampled |
| Access rule | `access_restriction` + `restricted_*` lists per row | sampled rows all "public"; stored per row at ingest; non-public rows fail closed until a rule is written |
| Member reviews | `partner_reviews_list` → `digest.partner_reviews` | rating + text + app user_id; review TEXT is public-in-the-app; reviewer identity NOT attributed by Olivia (app-side name display unverified); `app_user_id` stored for provenance only, never emitted |
| Member-facing URL | `app.mds.co/partners/{partner_id}` | pattern confirmed by Andy 2026-07-21; encode in ONE place (`digest.member_partner_url()`), like `member_event_url()` |
| Offer clicks (who claimed what, when) | app `partner_offer_clicks_list` | **DEFERRED** — engagement/matching fuel, never a who-list; not ingested in v1 |
| Freshness | MCP snapshot pull (in-session) | **no `GROUPOS_PAT` yet** → manual refresh, same wart as app_events_snapshot; PAT converts this to a daily curl step in member-profiles-sync |

**Junk guards at ingest:** skip "Untitled Partner" rows, empty-name rows, `deleted_at` non-null.

## Videos (source #5 — INGESTED 2026-07-26: 1,009 rows, gate green; not yet wired into the n8n workflow)

**Shipped state:** `digest.videos_catalog` **1,009 rows** — reconciles exactly to the MCP's
`with_total` (1,009 total · 614 public · 395 restricted), 0 duplicates, 0 gaps. **725.3 hours** of
content spanning **2018-06-27 → 2026-07-23**. Pulled in 5 parallel date windows, each page written
byte-identical from the raw API responses. Retrieval = `digest.video_search()`. Live-fire verified:
*"hiring a c-suite executive"* → "Hire a C-Suite That Duplicates You — Mogul Call with Lisa De Rosa".

**Field coverage measured at ingest (not sampled):** description 1,008/1,009 · duration 1,008 ·
event link **566** · attachments **605** · cliff notes **0** (not in the API).

**Two gaps closed in-session without waiting on GroupOS:**
- **Category names 14% → 97.4%** (983/1,009). Only 27 distinct category ids exist library-wide; the
  142 videos whose names DO resolve yield 25 of them. Map mined + backfilled. Verified against the
  admin UI (`642db2fa…`→Operations, `642db1d2…`→Amazon ads). ⚠️ **Inference, not authority** — it will
  rot as categories are renamed; GOS-23 stays open. 2 ids (36 videos) unknown.
- **Speakers named on 399 of 432 videos.** `speaker_ids` ARE GroupOS `user_id`s → resolved via
  `members_list(user_ids=…)` into `digest.video_speakers` (234 of 270 distinct speakers: 170 members,
  63 guest-tier outsiders, 2 collaborators; 36 unresolvable, probably removed users). Speaker names
  are weighted 'A' in search — "David Ghiyam" returns his two sessions.
  ⚠️ **`members_get` takes the member-RECORD id, not the user_id** — passing a user_id returns a bare
  `not_found`. This trap cost a wrong conclusion; use `members_list(user_id=…)`.

**Source of truth: the GroupOS content library** (community `67011d987a2a81b28438a3d8`), read via the
GroupOS MCP (`videos_list` / `videos_get`). **Verified live 2026-07-26: 1,009 videos, ALL `published`
(draft = 0), split 614 `public` / 395 `restricted`; newest 2026-07-23.** Supabase `public.videos` +
`transcript_segments` are the *abandoned May-2026 video-admin POC* (15 test rows, 7 soft-deleted) —
NOT this library, never ingest them.

**Scope: `published` + `restriction_access='public'` reaches members.** ⚠️ **Restricted ≠ unpublished —
ALL 1,009 videos are `published`, including all 395 restricted ones.** `public` == the admin UI's
"User access: All members" (video `68aaee42…`, "849 users can see this"); `restricted` == published but
gated by a rule.

**The rule is invisible to the API.** Verified across all 1,009 records: the ONLY access key returned is
`restriction_access` ("public"/"restricted") — restricted rows carry zero extra fields. The admin UI for
`6a6301a0…` (Centurion Channel Call) shows the real rule is **plan (Staff (App)) + tag (Centurion
Member) + an explicit 166-address user list → 242 users can see it**. None of that is fetchable.
So the 395 are **fail-closed and dark** until GOS-25 lands — not a policy choice, a data gap.

**Phase 1 = catalogue (metadata) only. There are NO transcripts** — `videos_get` has no transcript
field. Searching *inside* a recording needs ~1,000 hrs transcribed (~$120–370 AssemblyAI + pipeline):
a separate, priced, unapproved Phase 2.

| What | Where | Notes |
|---|---|---|
| Catalogue (title, description, duration, categories, tags, dates) | `videos_list` → `digest.videos_catalog` | description HTML→text at ingest; carries the "TOPICS:" bullets = the best search signal |
| Retrieval | `digest.video_search(p_phone, p_query, p_limit)` | gated fail-closed, service_role only; FTS w/ `expertise_query` synonyms + strict-match bonus; no query = browse newest-first |
| Access rule | `restriction_access` stored per row | RPC filters to `public` AND `published` AND `deleted_at is null` — three independent guards |
| Member-facing URL | `digest.member_video_url()` → `app.mds.co/videos/{id}` | shape taken from **real member-shared links in the WA archive**; ⚠️ Andy quoted `app.mds.co/s/videos/{id}` from the admin UI — **unresolved, verify before wiring** |
| Storage paths | `video_url` / `thumbnail_url` | **never persisted** — dropped at ingest, so no future RPC edit can leak them (gate-asserted) |
| **Cliff Notes** | admin UI only — **NOT in the MCP** (verified `videos_get` 2026-07-26) | the single highest-value field: a ~500-word structured summary of what was *said*. Column + search weight already built; a pure backfill once the API exposes it |
| Engagement counts | `view_count` / `like_count` / `comment_count` | stored, **never emitted** — 0 on every 2026 video sampled (stale-counter bug in the GroupOS QA notes) |
| Speakers | `speaker_ids` → stored | **432/1,009 populated** — but ids are unresolvable (no speakers endpoint, no names). Speaker→member matching is the open ask (GOS-31) |
| Attached files | `files[]` → **`digest.video_files`** | **640 attachments on 602 videos** (178 legacy cliff-notes PDFs · 8 reports · 8 decks · 446 unclassifiable by name). Andy's ruling 2026-07-26: files are a THIRD layer, separate from description and cliff notes — classify the artefact, extract its text into the video's search body, and send on demand. `file_kind` + `extracted_text` columns live; `extracted_text` blocked on GOS-29 (paths unfetchable). Output carries **name + kind only** — never the storage path (gate-asserted) |
| ⚠️ Attachment text extraction | vision, NOT `pdftotext` | Proven on the Ali Babul deck: `pdftotext` returned 880 words (titles + legal footer) and **silently dropped every formula and the verbatim prompt** — they're outlined vectors. Reuse the FB-image vision pipeline over rendered pages |
| Freshness | MCP snapshot pull (in-session) | same `GROUPOS_PAT` wart as partners — no PAT ⇒ manual refresh |

**Category names are unreliable in the API:** `category_names`/`tag_names` come back **empty for
older videos** (2023-era ids `642d…`) but populated for 2026-era ids (`6a5…`). Subcategories have no
name field at all. Same wound partners had (which needed an AT join + co-occurrence vote to reach 97%).

**Junk guards at ingest:** skip non-`published`, `deleted_at` non-null, "Untitled*" titles, non-24-hex ids.

### 🚨 WIRING RULE — video text is NEVER evidence of membership (Andy, 2026-07-26)

**6 video descriptions assert that someone is a member**, and at least one of those people has since
been removed:

| Video says | Reality (`digest.member_profiles`) |
|---|---|
| Billy Evans — *"a skilled member of MDS"* (`64cd5fa4…`) | `bill@microscope.com` → **Removed - Canceled Membership** |
| Greg Krakovskiy — *"member of MDS since 2020"* | — |
| Leo Limin — *"the first member of MDS"* | — |

**Why this is dangerous rather than merely untidy:** `member_card('Billy Evans')` returns **zero rows**
(verified) — the directory correctly excludes removed people. So Olivia has *nothing* to contradict the
video text, and the description becomes her only statement about his status. Silence reads as assent.

**The rule:** membership status comes ONLY from the member layer. Absent from `member_card` = **unknown,
never "member"**. Never repeat a membership claim found in a video title, description, cliff note or
attachment. Applies equally to FB posts and chat messages, which carry the same kind of language.

**Recommended (needs Andy's ruling — touches member-surface policy, not the videos source):** give the
member layer a deliberate *negative* signal — a lookup that answers "not a current member" for
Removed/Declined statuses instead of returning nothing. `member_profiles` already holds the truth
(278 Removed–Canceled · 142 Removed–For Cause); today only `member_card`/`expertise_search` read it,
and both filter to current members. Silence is the weak link.

**Leak gate:** 18 video checks in `scripts/olivia_leak_gate.py` (§12) — gate **GREEN at 133 checks**
2026-07-26. Restricted / soft-deleted / draft videos each proven invisible, including on a direct
topical match.

## Rules

- **Members table first, form answers as backup** — proven per field above (two exceptions:
  Year started + Title, where the application is the better/only source).
- Revenue and Birthdate never enter the matching layer as raw values — only the derived band/flag.
- **Any new data source (census, GroupOS, Stripe, events) gets its fields added to this table
  BEFORE its data is used anywhere.**
- **Validate every canonical/legacy derived field (rollup/formula/lookup) against its raw
  ledger BEFORE relying on it — whole table, population-scale diff — then stamp the verdict +
  date into the field's Airtable description** (Andy 2026-07-20). Case study: the four Members
  event rollups ride ONE link (the inverse of roster 'Match to Member', misleadingly named
  "Website Event Registration - In Person") — rows are all linked; the rollups' HIDDEN filter
  conditions (API-invisible) exclude e.g. virtual/program rows → `All Events Registered`
  undercounts 953 members, `Last Event Registration` wrong for 24% of dated members,
  `Events Attended` not validatable (derived-on-derived); `Upcoming Events Registered` 99.3%
  OK ("No events" = placeholder string). All four now carry
  validation-stamped descriptions in AT. Pipelines read `event_registrations` (the ledger),
  never these rollups. Validator: `mds-digest-web/scripts/validate_event_rollups.py`.
- **Event URLs: member-facing = `app.mds.co/events/u/{id}`; `/admin/` links are transformed,
  never emitted** (`digest.member_event_url()` = the one place; custom slugs coming → re-verify
  structure when they ship).
