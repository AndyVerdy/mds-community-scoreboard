# GroupOS MCP — Video API: staging verification pass

**From:** MDS (Andy Verdy) · **Date:** 2026-08-13
**Verifies:** `GROUPOS_MCP_VIDEO_REQUIREMENTS.md` (2026-07-26, items GOS-22 → GOS-34)

**What this is.** The dev team shipped video-API changes to staging. This is a live re-test of every
item in the July requirements doc against that build, so the outstanding list is short and specific
rather than "please re-check everything."

**How it was tested.** Staging MCP, community `68b6c8f464cb366ed7518196`, public-tier token
(`user_id 67c1a2af4a1b35142cd79e51`, `pat_id: null`). `health` returned `ok` at
`2026-08-13T17:17:37.551Z`. Every claim below is a live call made on 2026-08-13, not a doc reading.

**Two caveats that shape what can be concluded.**

1. **Staging is a 12-video sandbox**, not the 1,009-video production library. Findings that were
   measurements at library scale (GOS-23, GOS-27, GOS-34) cannot be re-measured there. They need a
   prod re-pull once this build promotes.
2. **Production is still on the old shape.** A prod `videos_list` for the Ivan Ong Milan Summit video
   (`68aaee42d6aea04127564518`) still returns `video_url` (not `video_key`), `category_names: []`, and
   no `description_text` or `cliff_notes` fields at all. Nothing below is live for members yet.

---

## Scoreboard

| # | Item | Status |
|---|---|---|
| **GOS-25** | Who may see a video | ✅ **Both top asks shipped** — needs a scoped PAT to verify behavior |
| **GOS-22** | Cliff Notes exposed | ✅ Shipped |
| **GOS-24** | Subcategory names | ✅ Shipped |
| **GOS-23** | Category / tag names | ✅ Shipped, including the unknown-vs-none marker |
| **GOS-33** | Event ids resolvable | ✅ Shipped |
| **GOS-30** | `updated_after` | ✅ Shipped, with the timestamp hazard documented |
| **GOS-31** | `members_get` id trap | ✅ Fixed |
| **GOS-26** | Payload weight | 🟡 Partial — `description_text` yes, field projection no |
| **GOS-29** | Attachment typing | 🟡 Partial — `mime_type` yes, `size_bytes` no |
| **GOS-28** | Timecoded transcripts | 🟡 Hook only — `captions_key` exists, null everywhere, no segments |
| **GOS-32** | Attachment exposure | 🔴 **Not closed** — bucket still world-readable |
| **GOS-27** | Engagement counters | ❓ Unverifiable on sandbox data |
| **GOS-34** | `files[]` completeness | ❓ Premise may be void — see below |

**7 resolved · 3 partial · 1 open · 2 unverifiable.**

---

## 🔴 GOS-32 — still open, and it is still the first item

**The ask was:** make the bucket private and serve signed, short-lived URLs, or at minimum stop
returning storage paths to callers not entitled to the parent video.

**What improved.** The video payload no longer publishes absolute URLs. `video_url` → `video_key`,
`thumbnail_url` → `thumbnail_key`, `files[].url` → `files[].key`. A consumer holding only a video
record no longer knows which host to hit. That is a real narrowing.

**What did not.** `events_get` still returns fully-qualified S3 URLs:

```
banner_url:    https://mds-community.s3.amazonaws.com/uploads/eventthumbnail/09a3577c-...jpeg
thumbnail_url: https://mds-community.s3.amazonaws.com/uploads/eventthumbnail/09a3577c-...jpeg
```

Fetched unauthenticated on 2026-08-13: **HTTP 200, 16,569 bytes.**

So the bucket is still world-readable and a neighbouring endpoint still publishes the hostname.
Key + host reassembles any file URL. The `_warnings` array still carries `legacy_video_raw_url`,
`legacy_thumbnail_raw_url` and `legacy_file_raw_url`, and no signed-URL field appeared anywhere in
the payload.

**Still outstanding, unchanged from July:**

1. Private bucket + signed short-lived URLs, served only to callers entitled to the parent resource —
   the same treatment the `.mp4` path already gets correctly.
2. Apply it to the **events** payload too, not only videos. Member `avatar_url` sits on the same
   bucket and is worth the same audit.
3. The two questions from the original doc are still unanswered: **how long has the bucket been
   public, and do access logs exist**, so MDS can judge whether anything was actually retrieved.

---

## ✅ Resolved

### GOS-25 — who may see a video

Both preferred asks shipped:

- **`can_access(community_id, resource_type, resource_id, user_id | user_email)`** — the ideal from
  the July doc. Consumers never re-implement entitlement logic.
- **`videos_list(for_user_id=…)`** — "videos this member may watch" in one call. Accepted and
  returned results.

`videos_list` now also documents that it returns only entitled rows by default.

**One blocker to confirming behavior:** `can_access` returned

```
{"error":"forbidden","detail":"Tool \"can_access\" requires scope \"access:read\"."}
```

The public-tier token has no `access:read` (nor `access:read:any`). **Please issue a PAT carrying
`access:read` + `access:read:any`** so MDS can verify the entitlement answers are correct against the
395 restricted videos — that is the check that unlocks 39% of the library, and it cannot be run today.

`restriction_access` is still the bare string `"public"` / `"restricted"`. With `can_access` and
`for_user_id` in place, the fallback ask (exposing the raw rule) is no longer needed.

### GOS-22 — Cliff Notes

`cliff_notes` (array) and `cliff_notes_title` are present on both `videos_list` and `videos_get`.
HTML, which is fine. Please confirm **how many of the 1,009 prod videos have them populated**, and
whether they are human- or AI-authored — it changes how MDS attributes them.

### GOS-24 / GOS-23 — taxonomy names

- `subcategory_names` and `video_subcategories_list` both exist. Verified: subcategory id
  `69b9492220bb871b690b8292` resolves to `"test"`.
- `category_names`, `tag_names`, `video_categories_list` all exist. Verified: 5 categories returned
  with `id` + `name` + timestamps.
- **`unresolved_category_ids`, `unresolved_subcategory_ids`, `unresolved_tag_ids`** are returned
  alongside. This was ask #2 in the July doc — "unknown" is now distinguishable from "none", which
  was the actual problem. Good fix.

This retires the MDS-side inference map (14% → 97.4% coverage by mining id→name pairs), which was
explicitly flagged as inference, not authority.

### GOS-33 — event resolution

`events_get` resolves a video's `event_ids`. Verified against `6979f98eb8eb853ec92ae640`, returning
title, `starts_at`/`ends_at`, timezone, structured `location`, `attendee_count` and `ticket_summary`.
"Show me the recordings from the Milan Summit" becomes answerable.

### GOS-30 — incremental sync

`updated_after` and `updated_before` both shipped. The timestamp-inversion bug reported in July is
now documented **in the tool description itself**, with the recommendation to pair incremental pulls
with an occasional unfiltered re-pull. Correct handling — the caveat is where an integrator will
actually read it.

### GOS-31 — `members_get` id-type trap

Fixed. `members_get` now accepts either the member-record id or a `user_id`, resolving the latter the
same way `members_list(user_ids=…)` does. The silent `not_found` that cost MDS a wrong conclusion is
gone.

---

## 🟡 Partial

### GOS-26 — payload weight

`description_text` shipped (ask #2) and works — one staging record carries ~1.5 KB of nested `<div>`
in `description` and `description_text: "small"`.

Not shipped: the `fields` / `select` parameter (ask #1), which would also have fixed **GOS-4**
(`pages_list` exceeding the token cap). Every row still carries full Quill HTML over the wire, so a
full-library sync still transfers ~2 MB of markup that gets discarded. Reading is solved; transfer
is not. Low severity now, worth doing generically.

### GOS-29 — attachment typing

`files[].mime_type` shipped and is accurate — one staging record returns `text/csv`,
`application/pdf`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `image/jpeg`,
`application/msword` across 11 attachments. This was the substance of the ask: 65% of prod
attachments were unclassifiable from filename alone.

`size_bytes` still absent — a bulk ingest can't estimate download cost in advance.

### GOS-28 — timecoded transcripts

A new field **`captions_key`** now sits alongside `video_key` and `thumbnail_key` on every video.
It is **null on all 12 staging videos**. There is no `transcript_segments_list`, no `start_ms` /
`end_ms`, no `speaker_label`.

The socket exists; the feature does not. **Two questions that decide whether this is 80% done or 0%:**

1. **Is `captions_key` populated in production, and on how many videos?**
2. **What format is the file?** If it is WebVTT, the cues carry start/end times and MDS can derive
   deep-links by parsing it — most of the ask, without a segments endpoint. If it is flat text,
   the deep-link requirement is unmet.

Speaker diarization is absent either way.

---

## ❓ Unverifiable on staging

### GOS-27 — engagement counters

Staging counters are non-zero (`view_count: 2`, `like_count: 1`, `comment_count: 4`), which proves the
fields *can* populate. It proves nothing about production, where every 2026 video sampled read 0
including a three-day-old published Channel Call.

**Still needed:** confirmation of whether prod counters populate asynchronously and with what lag,
how the admin UI's "Video starting views" seed field interacts with `view_count`, and whether the
aggregates are recomputed from `video_viewers_list` / `video_likers_list` — which do appear to hold
the real per-member data. Until answered, **MDS continues to suppress all engagement numbers**
rather than tell a member "0 views" about a packed call.

### GOS-34 — `files[]` completeness

**This item's premise may be void.** July flagged that only 28 of 642 attachments looked like
transcripts against a belief that ~300 transcripts had been uploaded. MDS has since confirmed the
platform has no transcripts — so 28 is plausibly just 28, with no gap and nothing to fix.

**Ask:** confirm `files[]` is unfiltered and uncapped, and this item closes with no dev work.

---

## New in this build (not requested, worth knowing)

- **`q`** free-text search over video titles, and engagement sort orders (`view_count`, `like_count`,
  `comment_count`, asc/desc).
- **`webhooks_list` / `webhook_deliveries_list`** — push instead of poll.
- **`tiers_create` / `tiers_update`**, and tier `benefits[]` now returns `{id, name}` objects rather
  than an empty array.
- **`modules_create` / `modules_update` / `modules_delete`** — a platform-owner-only object taking
  `name`, `description`, **`price_cents`** and a `system_id` "used for feature matching on tier
  reads." A priced, sellable feature object wired to tier `features[]`.

That last one is directly relevant to the courses work MDS is scoping. **Question for the dev: is
Courses intended to be a module?** If so, MDS should design against that primitive rather than
specify a parallel pricing path.

---

## Summary of what MDS still needs

| Priority | Ask |
|---|---|
| 🔴 1 | Close GOS-32 — private bucket + signed URLs, applied to **events** and avatars too, not only videos. Plus: how long was it public, and are there access logs? |
| 🔴 2 | A PAT with `access:read` + `access:read:any` so `can_access` can actually be verified against the 395 restricted videos |
| 🟠 3 | GOS-28 — is `captions_key` populated in prod, and in what format? |
| 🟠 4 | GOS-27 — do prod engagement counters populate, with what lag, and how does "starting views" interact? |
| 🟡 5 | GOS-22 — how many of 1,009 have cliff notes, human- or AI-authored? |
| 🟡 6 | GOS-34 — confirm `files[]` is unfiltered; likely closes with no work |
| 🟢 7 | `fields` / `select` projection (GOS-26 ask #1), also fixes GOS-4 |
| 🟢 8 | `files[].size_bytes` (GOS-29) |
| 🟢 9 | Promotion date for this build to production |
