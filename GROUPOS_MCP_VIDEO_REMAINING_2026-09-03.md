# GroupOS MCP — Video API: what is still outstanding

**From:** MDS (Andy Verdy) · **Date:** 2026-09-03 · **Contact for questions:** Andy
**Supersedes nothing** — this is the follow-up to `GROUPOS_MCP_VIDEO_REQUIREMENTS.md` (2026-07-26,
GOS-22 … GOS-34). New findings continue the numbering at **GOS-35**.

**Method.** Every figure below is measured across the **206 videos created in 2026**, pulled via
`videos_list` on 2026-09-03 across 11 pages, plus targeted `videos_get` / `can_access` probes.
Auth: `whoami` → `tier: "public"`, `pat_id: null`. Community `67011d987a2a81b28438a3d8`.
Where something could not be tested from our tier it is marked **[untested]** rather than asserted.

---

## First — what shipped. Thank you, this was a large delivery.

| Item | Was | Now |
|---|---|---|
| **GOS-22** cliff notes | absent | `cliff_notes` + `cliff_notes_title` on **206/206 (100%)** |
| **GOS-26** payload weight | full HTML only | `description_text` on **206/206** |
| **GOS-23** category names | 14% resolved | **194/206 (94%)** |
| **GOS-24** subcategory names | field did not exist | **175/206 (85%)** |
| **GOS-23** unknown-vs-absent | indistinguishable | `unresolved_category_ids` · `unresolved_subcategory_ids` · `unresolved_tag_ids` |
| **GOS-24** taxonomy endpoints | none | `video_categories_list` (32) · `video_subcategories_list` |
| **GOS-27** engagement counters | 0 on every 2026 video | **156/206 have view_count > 0** — we can stop suppressing these |
| **GOS-29** file typing | filename guessing only | `mime_type` per file, on 126 videos carrying files |
| **GOS-30** delta pulls | `created_after` only | `updated_after` shipped, with an honest reliability note in the description |
| **GOS-25** entitlement | nothing | `can_access` tool + `for_user_id` filter both exist |

The unresolved-id markers and the caveat written into the `updated_after` description are both
better than what we asked for. Noted and appreciated.

---

## GOS-25 · 🟡 entitlement — `for_user_id` WORKS (verified 2026-09-03); `can_access` still one scope away

**Correction to the first draft of this section:** `videos_list(for_user_id=<member id>)` is callable
at our tier and returns exactly the set that member may watch — verified across all 749 active MDS
members on 2026-09-03 (two windows, 1,498 calls, results loaded into our access table). So the
entitlement answer IS reachable today, one member at a time. What follows is what would make it
cheap instead of a 750-call sweep.

```
can_access(community_id, resource_type="video", resource_id="6a8e4e209614296a636efb15")
→ {"error":"forbidden","detail":"Tool \"can_access\" requires scope \"access:read\"."}
```

Our token's scopes include `videos:read`, `members:read`, `partners:read`, `events:read` and 20
others — but not `access:read`. So the entitlement answer exists on your side and is unreachable
from ours.

**Current cost of that.** Of the 206 videos created in 2026, **85 (41%) are
`restriction_access: "restricted"`.** We fail closed, so all 85 are invisible to every member,
including the entire Singapore Summit and AI Mastermind sets. That is the same 39%-dark problem
from the original doc, unchanged in effect.

**Also still missing:** the fallback from the original GOS-25 ask #3. We diffed the key set of the
85 restricted videos against the 121 public ones — **no `restricted_plan_ids`, `restricted_tag_ids`,
`restricted_user_ids` or any other rule field appears on the video payload.** The partners payload
still carries all five of those fields; videos carry none.

**Ask, in order:**
1. **Expose the rule fields on the video payload** (`restricted_plan_ids`, `restricted_tag_ids`,
   `restricted_user_ids`, `restricted_event_ids`) as the partners payload already does. One listing
   call would then replace ~750 per-member calls per refresh.
2. **Add `access:read` to the MDS community token** so `can_access` answers a single
   member-and-video question without a listing call.
3. `for_user_id` needs no extra scope — confirmed working. Please keep it that way.

---

## GOS-28 · 🔴 Transcripts — `captions_key` exists but is empty on every video

A `captions_key` field now appears on the video payload. It is **populated on 0 of 206 videos**.
There is no `transcript_segments_list`, and no captions content is reachable.

So the field is a placeholder, which is genuinely useful to know — it says the shape is planned.

**Ask (unchanged from GOS-28, now narrower):**
1. Tell us whether `captions_key` is intended to be populated, and on what timeline. If GroupOS is
   going to generate captions at upload, MDS will not budget an external transcription build —
   this single answer decides a spend on our side.
2. If captions will land as WebVTT/SRT only, say so; we can derive segments ourselves. Timecodes
   are the non-negotiable part, not the segmentation.
3. If captions are **not** planned, tell us plainly and we will stop waiting.

**Context so the priority is fair:** MDS has now transcribed and embedded these calls independently
(85 of the 2026 videos carry a Zoom recording stamp we link ourselves). The assistant answers from
those transcripts today. So this is no longer blocking us — it is a duplication-of-effort question,
not an outage.

---

## GOS-35 · 🟠 NEW — four breaking field renames shipped with no changelog

Between the 2026-08-27 pull and the 2026-09-03 pull, the video payload changed shape:

| Before | After |
|---|---|
| `video_url` | `video_key` |
| `thumbnail_url` | `thumbnail_key` |
| `files[].url` | `files[].key` |
| `cliff_notes` (HTML string) | `cliff_notes` (list of HTML fragments) |

No deprecation window, no changelog entry, no note on the ticket. We found them by reading a
payload, not by being told.

**What it cost us.** Our loader derives each video's Zoom-call link from the `GMT<date>-<time>`
marker inside the storage path. Reading `video_url` it returned `NULL` for every video. Because
that field is watched by our change-detector, the next scheduled run would have marked **every**
video changed, written NULL over **67 live recording stamps**, and severed the join between each
published video and its transcript. We caught it by inspecting the payload before applying, not
because anything failed loudly. A silent rename is the most expensive kind.

Note this is precisely what **GOS-29 ask #3** asked you to prevent: *"Document what
`legacy_video_raw_url` warns about and what the non-legacy shape will be, so we don't hard-code
something you're about to change."* The rename then shipped without that documentation.

**Ask:**
1. A changelog for the MCP surface — even a dated list of field additions/renames in the repo.
   We do not need advance notice; we need a place to look.
2. During a rename, return **both** keys for one release, then drop the old one.
3. Confirm the intended final shape of `video_key` / `thumbnail_key` / `files[].key`, because all
   three still emit `_warnings: legacy_video_raw_url` / `legacy_thumbnail_raw_url` /
   `legacy_file_raw_url`. If another change is coming, we would rather absorb it once.

---

## GOS-32 · 🔴 Attachment exposure — status unconfirmed, please confirm in writing

The payload no longer hands out absolute S3 URLs; it returns bucket **keys**. That is a real
improvement to the API surface. It does **not** by itself tell us the exposure is closed, because
the keys still address the same bucket and all three `legacy_*_raw_url` warnings are still emitted.

We deliberately did **not** test whether the bucket still serves those keys unauthenticated — that
would mean downloading member-confidential decks again, and once was enough to make the point.

**Ask (small, and it closes the most serious item in the original doc):**
1. State whether `mds-community.s3.us-east-2.amazonaws.com` is still publicly readable.
2. The original questions stand: how long was the bucket public, and do access logs exist?

The "how do we fetch an asset now" half of this is a requirement in its own right — see GOS-36.

---

## GOS-36 · 🔴 NEW — there is now no way to fetch an asset at all

> **2026-09-04 update.** To get transcripts for the 27 Aug–2 Sep uploads, the dev opened `uploads/content-archive/videos/*.mp4`
> to anonymous GET (all 30 requested links went from `403 AccessDenied` to `206`). That solves the fetch, but it does it by
> reopening the GOS-32 exposure: RESTRICTED talks' mp4s — and the Otter "Transcript – …pdf" attachments, which were already
> public — are readable by anyone holding the key. The ask below (signed, entitlement-checked URLs) stands.

This is the other half of the GOS-32 fix, and it needs stating plainly because the current state is
worse for an integrator than before the change.

| | Before | Now |
|---|---|---|
| What the payload returns | absolute S3 URL | bare storage key |
| Can an **entitled** caller fetch the asset? | yes (bucket was public) | **no — no fetchable URL is returned anywhere** |
| Can an **unentitled** caller fetch it? | yes (the exposure) | unknown, pending GOS-32 answer |

Closing the hole by removing the URLs is the right instinct, but the entitled path was removed at
the same time and nothing replaced it. `video_key`, `thumbnail_key`, `captions_key` and
`files[].key` are all storage keys against a bucket whose policy we cannot see. There is no
`*_url` field, no signed-URL endpoint, and no documented way to turn a key into something a client
can GET.

**Concretely, MDS cannot today:** show a partner or video thumbnail in any surface we build; let an
entitled member open an attachment we have told them exists; or re-fetch a deck for OCR when a
document is revised. All three worked before, by accident, via the public bucket.

**Ask — this is the requirement, not a question:**
1. **Return a signed, short-lived, fetchable URL for every asset the caller is entitled to** —
   video, thumbnail, captions and each entry in `files[]`. Same treatment the `.mp4` path already
   gets correctly. Expiry of minutes-to-hours is fine; we fetch on demand and do not cache URLs.
2. Either as an extra field alongside the key (`video_url` / `files[].url`, signed), or as an
   endpoint that exchanges a key for a signed URL (`asset_url(key)`), whichever fits your model.
3. **Entitlement must be checked at signing time**, so an unentitled caller gets no URL rather than
   a URL that happens to work. That is what makes this the fix for GOS-32 rather than a reopening
   of it.
4. Keep returning the raw key as well. It is a stable identity for change detection, which the
   signed URL cannot be.

**Note on our own dependency, so the priority is honest:** MDS does not derive the asset path for
playback — we extract only the `GMT<date>-<time>` stamp from the key to join a video to its Zoom
call, and our leak gate forbids us storing the path at all. So we are not blocked on playback. We
are blocked on thumbnails, attachments and any future document re-fetch.

---

## Still open, unchanged, lower priority

- **GOS-31 · `speaker_names`** — not added. `speaker_ids` still requires a second `members_list`
  round-trip. Low priority; we have this working.
- **GOS-33 · event resolution** — not added. **150 of 206** 2026 videos carry `event_ids`, and there
  is still no `event_names` on the payload. *"Show me the Singapore Summit recordings"* still cannot
  be answered from the video record alone.
- **GOS-29 · `size_bytes`** — `mime_type` landed, `size_bytes` did not. Minor; `mime_type` solved
  most of the classification problem on its own.
- **GOS-34 · `files[]` completeness** — still unverified from outside. 126 of 206 2026 videos carry
  files. We cannot tell whether that is all of them.

---

## Acceptance — how we would verify each remaining item

1. `can_access` returns a boolean for a restricted video instead of a scope error.
2. A member entitled to a Centurion video gets `true`; a member who is not gets `false`.
3. `captions_key` is populated on at least one video, and the content behind it is fetchable — **or**
   a written answer that captions are not planned.
4. A dated changelog entry exists for the `video_key` rename, and the next rename appears there
   before it ships.
5. A written statement on the bucket's public/private status.
6. A signed URL is returned for a video, its thumbnail and each of its attachments, it fetches
   successfully for an entitled caller, and the equivalent request for an unentitled caller returns
   no URL at all.
7. `event_names` present on the payload, or `events_get` accepting a video's `event_ids`.

---

## Not GroupOS — recorded so nothing is misattributed

- Our MCP client currently sends `limit` and `with_total` as strings, which your validator correctly
  rejects (`Expected number, received string`). That caps our listing calls at the default 20/page
  and made this pull 11 round-trips instead of 3. **We believe this is our client, not your API**,
  and we are not asking you to change anything — noted only so the page counts above make sense.
- `speaker_ids` is still empty on many videos because the MDS team has not filled the field in.
