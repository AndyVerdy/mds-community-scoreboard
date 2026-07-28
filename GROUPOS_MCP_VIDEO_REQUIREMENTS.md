> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS MCP — Video API: requirements for Dev

**From:** MDS (Andy Verdy) · **Date:** 2026-07-26 · **Contact for questions:** Andy
**Numbering** continues `GROUPOS_MCP_DEV_HANDOFF.md` (which ended at GOS-21).

**Why this exists.** MDS is building an AI assistant over the GroupOS video library and has just
ingested the whole thing — **all 1,009 published videos, plus all 642 attachments (958 MB, 18,484
pages)**. Everything below was found doing that, at full library scale, not from spot checks.

**Method, so you can trust the numbers.** Every figure is measured across all 1,009 records pulled via
`videos_list` on 2026-07-26, cross-checked against the GroupOS admin UI for named example videos.
Where a finding might be an artefact of our token tier rather than a real gap it is marked
**[verify at PAT tier]**.

**Auth used:** public-tier token — `whoami` → `tier: "public"`, `pat_id: null`, scope `videos:read`.
**Community:** `67011d987a2a81b28438a3d8`.

---

## Priority summary

| # | Sev | Gap | Consequence |
|---|---|---|---|
| **GOS-32** | 🔴🔴 **CRITICAL** | Restricted videos' attachments are **publicly downloadable**, and the API hands out the paths | Active data exposure — confidential member decks readable by anyone |
| **GOS-25** | 🔴 | `restriction_access` never says *who* may see a video | 39% of the library unusable; we must fail closed |
| **GOS-22** | 🔴 | Cliff Notes absent from the API | The best summary of every session is invisible |
| **GOS-28** | 🔴 | No timecoded transcripts | Can only link a 60-min video, never the moment |
| **GOS-24** | 🔴 | Subcategory names **do not exist anywhere** in the API | The entire call-type taxonomy is lost |
| **GOS-23** | 🟠 | `category_names` empty on 86% of videos | Category search silently returns nothing |
| **GOS-34** | 🟠 | `files[]` may be incomplete | Attachments we know exist aren't returned |
| **GOS-26** | 🟠 | No field projection | Payloads too heavy to bulk-read |
| **GOS-33** | 🟠 | Video `event_ids` don't resolve to any event we can look up | Can't connect a recording to its event |
| **GOS-29** | 🟠 | File URLs unfetchable; no `mime_type` / `size_bytes` | 70% of attachments unclassifiable |
| **GOS-27** | 🟡 | Engagement counters stale | Unusable; we suppress them |
| **GOS-30** | 🟢 | No `updated_after` on `videos_list` | Every refresh is a full re-pull |
| **GOS-31** | 🟢 | `members_get` id-type trap (speakers otherwise solved) | Cost us a wrong conclusion |

---

## GOS-32 · 🔴🔴 CRITICAL — restricted videos' attachments are publicly downloadable

**This is an active exposure, not a missing feature. Please treat it as the first item.**

The `.mp4` files are correctly protected. Their attachments are not:

| Asset | Request | Result |
|---|---|---|
| A **restricted** video's `video_url` (`.mp4`) | unauthenticated GET | **403 Forbidden** ✅ |
| That **same restricted video's** attached PDF | unauthenticated GET | **200 OK — full file** ⚠️ |

We downloaded complete PDFs belonging to restricted videos with **no authentication of any kind**,
including *"Building Engaging Brands — MDS Inspire"* (9 MB) and *"20 Million eCommerce Business Study —
Yoni Kozminski"* (5.5 MB). One of them carries the footer *"Proprietary and Confidential: This
presentation may not be used or disclosed to other than MDS members."*

**The exposure chain — this is what makes it serious:**
1. `videos_list` on a **public-tier token with no PAT** returns `files[].url` for every video,
   including restricted ones — **642 storage paths**, no entitlement check.
2. Those paths are keys in a publicly-readable bucket (`mds-community.s3.us-east-2.amazonaws.com`).
3. Therefore **any holder of a public-tier token can download every attachment in the library**,
   including material behind Centurion, channel and Mastermind gates. No guessing; the API supplies
   the paths.

The same applies to `thumbnail_url`, and to member `avatar_url` (also absolute S3 URLs on the same
bucket) — worth auditing the bucket policy as a whole, not just the video prefix.

**Ask (either fixes it):**
1. Make the bucket private and serve **signed, short-lived URLs** — exactly what the `.mp4` path
   already does correctly. Serve them only to callers entitled to the parent video.
2. At minimum, **stop returning `files[].url` / `thumbnail_url` to tokens not entitled to that video.**

Please also confirm how long the bucket has been public and whether access logs exist, so MDS can
judge whether anything was actually retrieved.

---

## GOS-25 · 🔴 `restriction_access` says *that* a video is restricted, never *to whom*

**Terminology first, because it caused confusion on our side:** restricted ≠ unpublished. **All 1,009
videos are `status: "published"`, including all 395 restricted ones.** Restricted = published, but
visible only to users matching a rule.

**The complete set of keys the video API returns** (verified across all 1,009 records):

```
id · title · description · video_url · thumbnail_url · duration · status · restriction_access
category_ids · category_names · subcategory_ids · tag_ids · tag_names · speaker_ids · event_ids
files · view_count · like_count · dislike_count · comment_count
created_at · updated_at · deleted_at · community_id · _warnings
```

**The only access-related key in that entire list is `restriction_access`**, whose value is the bare
string `"public"` or `"restricted"`. We diffed the key sets of the 395 restricted records against the
614 others: **zero extra fields**.

**What the admin UI holds for the same video** — `6a6301a0c32aac77a686a60f`, *"How Centurion Brands
Expand Beyond Amazon… — Centurion Channel Call July 2026"*:

| Rule component | Value in the UI |
|---|---|
| User access | **Restricted** |
| Select plans | **Staff (App)** |
| Select Tags | **Centurion Member** |
| Add users | explicit email list — **166 community members, 0 non-members, 0 errors** |
| Effective audience | **"242 users can see this event"** |

So GroupOS holds a three-part entitlement rule — **plan + tag + explicit user list** — and the API
exposes none of it. A consumer can see the door is locked and nothing about who holds a key.
`"public"` corresponds to the UI's **"All members"** (confirmed on `68aaee42…`, "849 users can see this").

The **partners** payload already does this properly: `restricted_group_ids`,
`restricted_membership_plan_ids`, `restricted_tier_ids`, `restricted_user_ids`, `restricted_tag_ids`.

**Consequence:** we fail closed and treat all 395 restricted videos as non-existent for every member.
**39% of the library is dark** — including all Centurion, TikTok-channel and AI-Mastermind content —
not because members lack entitlement, but because we cannot read entitlement that already exists.

**Ask, in priority order:**
1. **`can_access(video_id, user_id) → bool`** — the ideal. Consumers never re-implement your
   entitlement logic, and your rules can evolve server-side without breaking anyone.
2. A **`for_user_id` filter on `videos_list`** — "videos this member may watch" in one call.
3. Failing both, expose the **rule, not the audience**: `restricted_plan_ids`, `restricted_tag_ids`,
   `restricted_user_ids`, plus a `restricted_user_count`.

**Do NOT return expanded name/email lists.** A 1,000-entry audience per video is a large payload, it is
personal data we don't need, and it goes stale the moment membership changes. **IDs, never emails.**
**[verify at PAT tier]**

---

## GOS-22 · 🔴 Cliff Notes are not exposed by the API

**What the UI has.** The admin video editor has a **Cliff Notes** tab holding a long, structured,
human-grade summary of the session. For `68aaee42…` (Ivan Ong, Milan Summit) it runs ~500 words under
headings — *Company Background · Business Growth Stages · Technology and Systems · PPC and Marketing
Strategies · Supplier and Cost Management · Customer Experience and Branding* — with specifics like
*"negotiates zero deposit and net 60 payment terms"* and *"spends approximately $1 million monthly on
PPC advertising"*.

**What the API returns.** Nothing. There is no cliff-notes field under any spelling, on `videos_get`
or `videos_list`. Of 1,009 videos we hold cliff notes for exactly **one** — because Andy pasted it
into a chat by hand.

**Why this is near the top.** Cliff notes are the only written representation of what was actually
*said* inside a recording that exists anywhere in GroupOS. With them, *"what did Ivan Ong say about
supplier payment terms?"* is answerable from a single field. Without them, the alternative is
transcribing ~725 hours of audio to reconstruct information **GroupOS already has written down**.

**Ask:**
1. Add `cliff_notes` to `videos_get` **and** `videos_list`. Plain text or HTML both fine.
2. Tell us how many of the 1,009 have cliff notes populated, and whether they are human- or
   AI-authored — it changes how we attribute them.
3. **[verify at PAT tier]** — if the field is merely stripped for public-tier tokens, say so and this
   becomes a documentation fix rather than a build.

---

## GOS-28 · 🔴 No timecoded transcripts — the strategic ask

There is no transcript field and no transcript endpoint. Combined with GOS-22, the API exposes **no**
representation of spoken content.

**What we need is not a flat transcript — it is timecoded, speaker-attributed segments.** MDS has
already built and validated a working prototype: the assistant answers by naming **the specific
chapter of the specific video** and deep-linking to that timestamp, rather than handing a member a
60-minute recording. That difference — *"watch this 1-hour call"* vs *"at 14:32 Ivan explains net-60
supplier terms"* — is the whole value of the library.

**The segment shape we need** (proven in MDS's prototype store — please return this, or something
trivially mappable to it):

| Field | Type | Purpose |
|---|---|---|
| `video_id` | id | parent video |
| `text` | text | the spoken words for this segment |
| `start_ms` / `end_ms` | int | **the deep-link target — non-negotiable** |
| `chapter_title` | text | what the assistant names in its answer |
| `speaker_label` | text | diarised speaker |
| `speaker_id` | id | resolvable identity — see GOS-31 |

**Ask, in order:**
1. Confirm whether captions/transcripts exist **anywhere** in the platform today (Mux, Zoom cloud
   recording, or an internal ASR step). Even raw, unpunctuated, un-diarised output is valuable — it can
   be enriched downstream. This answer determines whether MDS budgets an external transcription build.
2. If they exist: `transcript_segments_list(video_id)` returning the shape above, plus `captions_url`
   (WebVTT/SRT) on the video record.
3. If they don't: we'd like to discuss GroupOS generating them at upload. The audio already passes
   through your pipeline, and doing it once at ingest is far cheaper than every customer
   re-transcribing the same library.

---

## GOS-24 · 🔴 Subcategories have no names anywhere — the whole taxonomy is unreachable

`subcategory_ids` is returned on **957 of 1,009 videos (95%)**. There is **no `subcategory_names`
field, and no subcategory-listing endpoint.** Unlike categories (GOS-23), there is *no* subset of
videos that resolves, so nothing can be reverse-engineered. **Coverage today: zero.**

**Worked example** — `6a60a81b8a427b8944d47a39`, *"Building an AI-Run Business: Discord Agents,
Community Monitoring & Automated Ad Funnels — Constantine Kirillov — Vancouver AI Mastermind 2026"*:

```
subcategory_ids: ["64f5ce9b3da210d4988f37ec",
                  "642db2d8752a493e486d1f6c",
                  "642db2fa752a493e486d1f88"]
subcategory_names: (field does not exist)
```

Three opaque ids, nothing else.

**Why it matters more than it sounds.** The admin UI's subcategory checkboxes are the **call-type
taxonomy** — *Mogul Calls · Expert Calls · Resellers Calls · AI Calls · Trading Calls · Real Estate
Calls · Logistics Calls · Mergers & Acquisitions Calls · DTC/Shopify Calls · Credit Card & Travel Hacks
Calls · **Centurion 20M+ Calls** · Accelerator Calls · **TikTok Calls** · Large SKU Calls · SEO Calls ·
Retail Calls*, plus content facets like *Business optimization* and *PPC*.

That is exactly the axis a member asks along — *"was there a Mogul Call about hiring?"*, *"show me the
M&A calls"*. We hold the ids for 957 videos and cannot use one of them.

**Ask:**
1. `subcategory_names` on the video payload, alongside the ids.
2. `video_subcategories_list(community_id)` so consumers can build the id→name map once.
3. Same for categories and tags — see GOS-23.

---

## GOS-23 · 🟠 `category_names` empty on 86% of videos

**Measured across all 1,009:**

| | count | share |
|---|---|---|
| Videos with **no** `category_names` | **867** | **86%** |
| Videos with **no** `tag_names` | **876** | **87%** |

Only **142 of 1,009** resolve to a category name — yet **every one of the 867 has `category_ids`
populated**. Zero videos are genuinely uncategorised. This is a pure **name-resolution failure**, not a
content gap: the taxonomy is fully assigned, the API just won't name it.

**The pattern is era-of-creation:** 2023-era ids (`642d…`) don't resolve; 2026-era ids (`6a5…`) do.

**Why the silence is the real problem:** an empty array is indistinguishable from "this video has no
categories". A member asking *"what do we have on Operations?"* gets nothing back, and nothing in the
response signals that data was withheld rather than absent.

**MDS workaround already applied, so you can judge the priority:** there are only **27 distinct category
ids** library-wide, and the 142 resolving videos expose enough pairs to name **25** of them. We mined
that map and backfilled — coverage 14% → **97.4%** (983/1,009); 2 ids (36 videos) remain unknown.
Independently validated twice against the admin UI (`642db2fa…`→Operations, `642db1d2…`→Amazon ads).
**This is inference, not authority** — it will silently rot as categories are renamed, and it cannot
be the long-term answer.

**Ask:**
1. Resolve names for all category and tag ids regardless of era.
2. If some legacy ids genuinely have no name record, return an explicit marker
   (e.g. `category_names: null` + `unresolved_ids: [...]`) so "unknown" is distinguishable from "none".
3. `video_categories_list` / `video_tags_list` endpoints.

---

## GOS-34 · 🟠 `files[]` may not be returning every attachment

Across all 1,009 videos the API returns **642 attachments on 602 videos**, of which **28** are
transcripts (filename or storage path containing `transcript` / `otter`). MDS believes roughly **300**
transcripts were added to the library. If that is right, the API is returning under 10% of them.

Cross-checks we ran, all negative:
- video **descriptions** containing an `otter.ai` link: **0**
- descriptions mentioning "transcript" at all: **1**
- `videos_get` on a recent Channel Call (`6a63fbc0…`, 2026-07-23) returns `files: []` — no attachments

**Ask:** confirm whether `files[]` is complete, or whether it is capped/filtered/paginated, or whether
attachments can live somewhere the video payload doesn't reference (for example uploaded into the
Cliff Notes tab rather than the Files tab). If content is reachable in the admin UI but absent from
`files[]`, that is a data-loss-shaped bug for any integrator.

---

## GOS-26 · 🟠 No field projection — the library is expensive to bulk-read

Every `videos_list` row carries the **full `description` HTML** — Quill/RTE output with inline CSS
custom properties on every element. A typical description is ~2 KB of markup wrapping ~90 words of
text: roughly a **10:1 markup-to-content ratio**. Across 1,009 videos that is ~2 MB of mostly-CSS.

Same class of problem as **GOS-4** (`pages_list` exceeding the token cap) — worth fixing once,
generically.

**Ask, in order of preference:**
1. A `fields` / `select` parameter (e.g. `fields=id,title,duration,category_names,created_at`) — this
   single change fixes GOS-4 too.
2. A `description_text` field alongside `description`, carrying tags-stripped plain text.
3. A `summary=true` mode returning a lightweight row shape.

---

## GOS-33 · 🟠 Video `event_ids` don't resolve to anything we can look up

**566 of 1,009 videos carry `event_ids`**, pointing at **208 distinct events**. These are GroupOS app
event ids, and they do not correspond to the event identifiers available anywhere else — of those 566,
only **3** match the event records MDS maintains.

So *"show me the recordings from the Milan Summit"* is unanswerable even though both sides hold the
data and the link is right there in the payload.

**Ask:** either expose an `events_get` that accepts these ids and returns enough to identify the event
(name, date, location), or add `event_names` to the video payload alongside the ids. Same underlying
request as GOS-23/24 — **ids without a resolver are not usable data.**

---

## GOS-29 · 🟠 File URLs are unfetchable paths, and files carry no type information

```
files: [{ "name": "$0 to US$100M in 8 years with no debt_funding - Ivan Ong - Milan Summit 2025",
          "url":  "uploads/content-archive/files/1756555218274-….pdf" }]
```

The `url` is a bare storage key, not a resolvable URL — same for `video_url` and `thumbnail_url`, all
three flagged by the API's own `_warnings: ["legacy_video_raw_url"]`. *(See GOS-32: these keys do in
fact resolve against a public bucket, which is the security problem. The correct fix is signed URLs,
not documentation of the raw path.)*

**Attachments are a distinct content layer** — not duplicates of the description or the cliff notes.
Measured: **642 attachments on 602 videos** — 178 legacy cliff-notes PDFs, 28 transcripts, 8 reports,
8 named decks, and **420 whose type cannot be determined from the filename alone (65%)**.

**What is being lost:** video `6a60abe98a427b8944d4953e` (Ali Babul, Trellis "Core") carries a 15-page
speaker deck containing the verbatim operator prompt, the ASR roll-up definition, and
`ACOS floor = TACOS_goal × (total_sales / ad_sales)` at a 15% TACOS goal. None of that appears in the
title, description or cliff notes. It exists only in the deck.

**Ask:**
1. Signed, fetchable URLs (see GOS-32).
2. **`mime_type` and `size_bytes` per file** — filename-only classification leaves 65% unclassified.
3. Document what `legacy_video_raw_url` warns about and what the non-legacy shape will be, so we don't
   hard-code something you're about to change.

⚠️ **Note for any integrator (MDS-side lesson, recorded so it isn't relearned): plain PDF text
extraction is not sufficient.** `pdftotext` over that deck yielded 880 words — slide titles and the
legal footer — and **silently dropped every formula and the verbatim prompt**, because they are
rendered as outlined vectors. Reliable extraction needs a **vision pass over rendered pages**.
Text-only extraction looks like it worked while losing exactly the parts worth quoting.

---

## GOS-27 · 🟡 Engagement counters are unreliable on current content

`view_count`, `like_count`, `dislike_count`, `comment_count` are **all 0** on every 2026 video sampled,
including a 3-day-old published Channel Call. A 2025 video does show `view_count: 100`, `like_count: 3`
— so the counters aren't universally dead, but they cannot be trusted for recent content. The admin UI
also has a separate **"Video starting views"** seed field which may or may not be conflated with the
live count.

Consistent with the stale-counter findings already logged against `review_count` and
`ticket_addons.quantity_sold`.

**Consequence:** MDS excludes all engagement counts from what the assistant may say, rather than tell a
member "0 views" about a well-attended call.

**Ask:** confirm whether these populate asynchronously (and with what lag) or are broken for new
uploads; clarify how "starting views" interacts with `view_count`. Note that
`video_viewers_list` / `video_likers_list` appear to hold the real per-member data — if the aggregate
counters are simply not being recomputed from those, that's a small fix with high value.

---

## GOS-30 · 🟢 No `updated_after` filter on `videos_list`

`videos_list` supports `created_after` / `created_before` but not `updated_after`. Videos are edited
after publication, so a created-at window cannot catch edits, and every refresh becomes a full re-pull
of the library. `partners_list` already has `updated_after`.

**Also worth a look:** on `68aaee42…` the `updated_at` (2025-08-24) is **earlier** than the
`created_at` (2025-08-29). One of the two is being set from a different clock or a migration backfill.

**Ask:** add `updated_after` to `videos_list`; explain the timestamp inversion.

---

## GOS-31 · 🟢 Speakers — solved by MDS; one id-type trap worth fixing

*(Drafted as a blocker, then solved during investigation. Recorded for awareness.)*

**`speaker_ids` are GroupOS `user_id`s** and resolve today via
`members_list(user_ids=<comma-separated>)`. MDS resolved **234 of the 270 distinct speakers** in six
batched calls.

**The trap:** `members_get(member_id)` expects the **member-record id** (`678f808b1691d2fdfa10f227`),
*not* the `user_id` (`6494ea1ddbb26945ae44e125`). Passing a user_id returns a bare `not_found` with no
hint that the caller used the wrong identifier — which led us to a wrong conclusion until Andy spotted
the member-edit URL. **Please either accept a user_id on `members_get`, or return an error that names
the mismatch.**

**What we found, FYI:** speakers are 170 `M` (members), 63 `GU` (guest tier — outside speakers, not
members) and 2 `CO`. **36 ids don't resolve at all**, most likely removed users — and `status: removed`
is explicitly unavailable on the public tier, so we can't confirm. A removed-user lookup returning at
least `{id, display_name, removed: true}` would complete historical speaker attribution.

**Remaining low-priority asks:**
1. `speaker_names` on the video payload, avoiding the second round-trip.
2. Clarify whether the Video Speakers admin list (~3,231 rows, Name + Email) is a distinct entity or a
   picker over all users — indistinguishable from the API.

**Possible bug:** `user_id 6494e9fc…` (ian@milliondollarsellers.com) returns **two member records** —
one `GU`/Guest tier, one `CO`/Basic. Duplicate member records per user look unintended and would break
any consumer keying on user_id.

---

## Not GroupOS bugs — MDS-side, listed so nothing is misattributed

- **A 6,983-page junk PDF** (*"SampleDocs-Test PDF File With Dummy Data For Testing"*) is attached to a
  real published video. It is 76% of all attachment pages in the library. MDS to delete at source.
- **`speaker_ids` is empty on 577 of 1,009 videos** — the Speakers field simply isn't filled in. API
  work above is useless on those until MDS populates them.
- **The API returns a speaker on at least one video where the admin UI shows the Speakers field
  empty** (`64cd5fa4…`, Billy Evans). Worth GroupOS confirming which surface is authoritative — the UI
  may be hiding speakers whose user record was removed.

---

## What MDS would build the day each lands

| Ships | Unlocks |
|---|---|
| GOS-32 | The exposure closes. Nothing else matters until this one does. |
| GOS-25 | 395 restricted videos become answerable for the members entitled to them — +39% of the library |
| GOS-22 | Every session becomes searchable by what was *said*, not just its title |
| GOS-24 + GOS-23 | "Was there a Mogul Call about hiring?" starts working |
| GOS-28 | "At 14:32 of Lisa De Rosa's Mogul Call…" — the end state |
