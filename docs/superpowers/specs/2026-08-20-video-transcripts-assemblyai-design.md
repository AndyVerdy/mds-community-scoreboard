# AssemblyAI transcripts for the 96 videos Zoom never reached

**Date:** 2026-08-20 · **Status:** ✅ SHIPPED 2026-08-20 (#101 closed — gate 263/exit 0) · **Scope:** the 2026 GroupOS video library (161 videos), 96 net-new · **Next:** the 2025 batch on the same machinery

#70 put transcripts into Olivia on 2026-08-07, sourced from Zoom. Zoom only transcribes calls Zoom
hosted, and only from around January 2026. Everything else in the library — Chapter Boardrooms,
Inspire sessions, the Hack Contest, hybrid rooms — has no spoken-word record anywhere. This spec
covers filling that hole with AssemblyAI transcripts, reusing #70's machinery rather than building
alongside it.

**The retrieval layer changes in three named places and nowhere else.** ① a new table
`digest.video_access` (who may see which restricted video, §7.2) · ② `CREATE OR REPLACE` on
`digest.video_search` to gate per asker · ③ `content_search_v2`'s access filter learns exactly one
new `access_rule` type, `video_access`. No prompt or seed edit, no workflow change, no new lane. The
transcript load itself writes into tables and columns that already exist, using a chunker and loader
that already run.

## 1. What already exists (verified live 2026-08-20)

| Piece | State |
|---|---|
| `digest.videos_catalog` | **1,033 rows**, GroupOS mirror keyed on the Mongo ObjectId, last synced 2026-08-17. 619 public / 414 restricted. All 1,033 carry an embedding. |
| `digest.content_items` `source='call_transcript'` | **3,116 chunks across 65 videos**, all embedded, newest 2026-08-05. The rows Olivia already searches. |
| `scripts/zoom_transcripts.py` | The chunker and loader: `parse_vtt()` → `chunk()` (1,400 chars ≈ 2–3 min) → `content_items` rows with `access_rule`, `sensitivity`, `url`, `meta`. |
| `scripts/video_summaries.py` | Writes `videos_catalog.summary` with `summary_source='transcript'`. Currently calls the Anthropic API (`claude-haiku-4-5`). |
| `digest.calls` | 2026 Zoom calls; `groupos_video_id` links 85 of the 161 2026 videos to a call, but only 65 of those carry a transcript. |
| Access enforcement | Chunk `sensitivity` mirrors the video's `access_restriction`. Live: 2,698 chunks `normal`, 418 `restricted`. `content_search` excludes `restricted` by default; the leak gate proves it. |

## 2. The gap this fills

The AssemblyAI batch ran 2026-08-20 against Andy's presigned S3 export.

| | |
|---|---|
| transcripts produced | **161 of 161**, zero failures, zero invalid files |
| audio | **114.8 hours** |
| output | 21,066 utterances · 1,175,887 words · 6.24M characters · 242 MB |
| cost | **$26.23** |
| wall time | 25 minutes at concurrency 5 |

**The sets are provably identical.** The md5 fingerprint of the 161 transcript `video_id`s and of
`videos_catalog`'s 161 rows dated 2026 both read `a5a76b557ba9f5fbc79611730cb2cf98`. Every
transcript has exactly one catalog row, and no catalog row is missed.

Of those 161: **65 already have Zoom chunks, 96 do not.** The same 96 are the videos with no
`summary`. One gap, two symptoms.

## 3. Decisions Andy made in this session

1. **2026 only for now.** The other 872 videos (2018–2025) are out of scope; the whole-library run
   would be 737.2 hours at $170.
2. **Zoom stays the source of truth where both exist.** The 65 Zoom transcripts are never
   overwritten, never re-chunked, never touched.
3. **Reuse `source='call_transcript'`** rather than introducing `video_transcript`. The label is
   imprecise for a Chapter Boardroom; `meta.provenance` carries the truth. Renaming would touch
   `content_search_v2`'s source vocabulary, a `multi_source` branch, a prompt block and the gate —
   the exact surfaces #70 recorded as load-bearing.
4. **No Anthropic API for the backfill.** The 96 summaries are written in-session rather than by
   metered API call, so `video_summaries.py`'s Haiku path is bypassed for this load.
5. **Precompute, never generate at query time.** Transcript, summary and TLDR are all stored, so a
   member asking twice costs nothing the second time.
6. ~~Assume access until the rules are readable~~ **SUPERSEDED same day** — the rules arrived and
   verified (§7.2). Access is computed per asker via `digest.video_access` + the #100 resolver.
7. **Entitlement decides what a restricted video returns** (Andy: *"If I can see videos, then I can
   search through transcripts"*): entitled → full treatment including transcript search, quotes,
   summary, TLDR, exact-words follow-ups; not entitled → title, speakers, date, link, restricted
   marker — never content. **Nobody ever receives a full transcript** — the ~1,400-char chunk is the
   largest retrievable unit and no lane concatenates chunks.
8. **Summaries are written in the normal format** — names and specifics included — because only
   entitled members ever see a restricted video's summary.

## 4. Evidence: Zoom versus AssemblyAI on the 65 videos where both exist

**Zoom is more verbatim.** 776,154 words against AssemblyAI's 598,933 — AssemblyAI is 0.78× on
every single video (min 0.64, max 0.87), measured after stripping Zoom's per-line `Name:` prefixes
so the comparison is speech against speech.

**That gap is not lost content.** Across all 161 videos there are **160 seconds** of unspoken gaps
in total, and time coverage differs from Zoom by an average of 3 seconds. The extra Zoom words are
filler: the batch ran with `disfluencies: false`, which strips ums and false starts that Zoom keeps,
and Zoom records each participant's own channel so cross-talk is captured twice.

**AssemblyAI is more accurate on domain vocabulary.** Same video, same second (Dorian Gorski,
11:44):

- Zoom — *"using anything from Helium, Datadive, **Keeper**, a lot of APIs"*
- AssemblyAI — *"using anything from Helium, DataDive, **Keepa**, a lot of APIs"*

Keepa is the real product. A mangled tool name is precisely what keyword search must get right in
this community.

**Zoom wins on speakers, decisively.** Zoom labels by participant, so its bodies read
`Dorian Gorski: …`. AssemblyAI returns `A`/`B`/`C` — 5.2 distinct voices per video on average, up
to 13. Anonymous attribution is the one real quality loss in this load.

Net: Zoom where it exists, AssemblyAI for the 96 it never reached.

## 5. Architecture

```
/Users/Born/Downloads/mds_transcripts_2026/<video_id>.json   (161 AssemblyAI payloads)
   │
   ├─ skip any video_id that already has call_transcript chunks   ← protects the 65
   │
   ├─ adapter: utterances[] → the cue shape parse_vtt() emits
   │            (start_sec, end_sec, speaker, text)
   │
   ├─ chunk()                     ← reused verbatim from zoom_transcripts.py
   │
   └─ digest.content_items rows   ← same shape as the 3,116 already there
```

The adapter is the only new code. `chunk()` and the row builder are reused unchanged, which is what
keeps retrieval, the prompt layer and the gate untouched.

**Raw JSON storage.** The 242 MB of payloads currently sit in `/Users/Born/Downloads/`, which is
volatile. They move to `/Users/Born/mds_transcripts/2026/` as the first step of the build, and the
loader takes that directory as a `--dir` argument. They are not committed to the repo.

## 6. The row shape

Identical to what #70 writes, with one added `meta` key:

| Column | Value |
|---|---|
| `source` | `call_transcript` |
| `kind` | `chunk` |
| `source_id` | `<video_id>#<chunk_index>` — Zoom rows use `<call_uuid>#<n>`, so the two never collide |
| `title` | the video's title from `videos_catalog` |
| `body` | speaker-prefixed text, `Speaker A: …` (see §8) |
| `occurred_at` | the video's `app_created_at` |
| `url` | `https://app.mds.co/videos/<video_id>` — the library video, never a source file (#70 ruling ①) |
| `access_rule` | `{"type": "public"}` for public videos; `{"type": "video_access", "video_id": "<id>"}` for restricted ones (§7.2) — unknown to every reader except the taught branch of `content_search_v2`, so everything else fails closed on them |
| `sensitivity` | `normal` when the video is public, `restricted` when it is restricted |
| `embedding` | voyage-3.5-lite, 1024 dims, as every other row |
| `meta` | `{chunk, start_sec, end_sec, timestamp, video_id, provenance: "assemblyai"}` |

## 7. Access

`sensitivity` mirrors `videos_catalog.access_restriction`, exactly as the Zoom rows do.

**The 96 skew heavily restricted, and this is the most important number in the spec:**

| | videos | hours |
|---|---|---|
| public — quotable in a default search | **26** | 21.8 |
| restricted — title and date only | **70** | 33.4 |

That is the inverse of the 2026 library overall (85 public / 76 restricted), and it follows from
what Zoom missed: Zoom hosted the open Mogul and Channel Calls, so what it never reached is mostly
chapter boardrooms, masterminds and Inspire sessions — the gated content. **The immediate visible
gain from this load is 26 videos and 21.8 hours**, not 96 and 55. The other 70 are stored, indexed
and ready the day their access rules become resolvable per member, which is its own ticket.

`content_search` excludes `restricted` unless the caller passes the explicit flag, and the leak gate
has covered that path since #70. **Transcript passages from restricted videos therefore remain
unreachable, and that does not change.** Nothing here is enforced by prompt.

### 7.1 What we can and cannot see about a restriction (verified live 2026-08-20)

We see **that** a video is restricted. We never see **who may view it**. Three probes:

| Probe | Result |
|---|---|
| GroupOS `videos_get` (MDS-bound PAT), restricted Rockies Hybrid Boardroom | `restriction_access: "restricted"` and nothing else. No group, tier, tag, user or event restriction field in the payload. |
| GroupOS `access_resources_list` | 6 rows — Events, Videos, News, Chats, Partners, Documents. Platform-wide permission categories, not per-video rules. |
| Andy's Mongo export | The only place `restrictedAccess{Group,MembershipPlan,Tag,Event,Tier,User}Id` exists — but `01_export_mds_videos.js` flattens them to `"tiers: 1; named users: 15"`. Event and tag *names* survive; tier and user **ids do not**. |

Even with the ids, resolving them to a member needs work that does not exist: event ids resolve
through `events_catalog.app_event_id` → `event_registrations_live` but reach only **8 of 76**
restricted 2026 videos; named users need a GroupOS-user → MDS-member bridge that today covers just
234 speaker records.

### 7.2 Real gating — SUPERSEDES the temporary assume-access posture (2026-08-20, same day)

§7.1's gap closed the same day it was written: Andy's dev produced `mds_video_audience_pairs.csv` by
mirroring the member read path itself (`userAccessRulesCommonCondition`), one row per (video,
person, rule that matched). Verified before trusting it: 76/76 restricted 2026 videos carry a real
audience, three spot-checked videos matched Andy's own admin lists exactly (10 event attendees; all
15 named users of the MDS9 video, 15/15), and the panel-vs-real discrepancy is explained — a fixed
pool of **63 test/staff subscriptions** (42 `@yopmail.com`) the panel counts globally but the read
path rejects, byte-identical across tier videos.

So access is computed, not assumed:

- **`digest.video_access`** — one row per (video_id, at_member_id, source), loaded from the pairs
  file **`real_match` rows only**. The 13,234 `panel_only` rows grant nothing in the app and loading
  them would hand 63 test accounts standing access — the loader filters them, structurally.
- Emails resolve through **`digest.resolve_member_by_email()`** (#100), never raw comparison. All
  1,171 grant-holders resolve → 1,038; to an ACTIVE member → 704. Unresolvable grants are stored
  against a NULL member and reported, never dropped — they become valid the day the person's alias
  or membership lands.
- **`video_search` gates on the table**: a restricted video the asker is entitled to returns its
  full treatment (summary, description, cliff notes); one they are not returns title, speakers,
  date, link and the restricted marker — never content. `CREATE OR REPLACE`, never `DROP`.
- **Entitled members can search inside restricted transcripts** (Andy: *"If I can see videos, then I
  can search through transcripts"*). Restricted chunks carry
  `access_rule = {"type":"video_access","video_id":…}`; `content_search_v2`'s access filter learns
  that one rule type — entitled and active → the chunk behaves as normal; otherwise excluded exactly
  as today. Unknown rule types remain DENIED, so every other reader of `content_items` fails closed
  on these rows until taught otherwise.
- **The quote ruling (Andy 2026-08-20):** Olivia processes transcripts 100% and may quote, summarize,
  give the TLDR, and answer "what exactly did he say" follow-ups — she never posts a full transcript.
  Structurally enforced: the largest retrievable unit is one ~1,400-char chunk, and no lane
  concatenates chunks.

The leak-gate grows checks for the new surface: an unentitled member gets no restricted summary, no
restricted chunk, and no `video_access`-typed row; an entitled-but-inactive member gets nothing (the
active-member gate still outranks entitlement); anon gets nothing.

The restricted-recording principle from #71 still holds: a restricted recording must not hide its
event. The video stays listed by title and date regardless of entitlement.

**Lapsed grants are correct behaviour:** 384 of the 1,171 grant-holders resolve to a lapsed/removed
record and 141 to nothing (44% — normal for a library reaching back to 2018). Their rows load and
sit inert behind `is_active_member_status()`.

### 7.3 To verify during the build, not assume

The keyword branch of `video_search` scores restricted rows on a `safe_tsv` built only from title,
speakers, categories and tags. The vector branch scores them on `videos_catalog.embedding` with no
equivalent gate. If that embedding was built from description or summary text, restricted videos are
already semantically matchable on their content. This is not a text leak, and it is pre-existing, but
it should be confirmed rather than trusted while this ticket is touching the same function.

## 8. Speaker labels

Bodies read `Speaker A:`, `Speaker B:` — the letters AssemblyAI returns. This is deliberately not
disguised: writing an unverified name onto a quote would violate the rule that a member is never
told something untrue about another member.

GroupOS metadata does not rescue it. Of the 161, only 68 carry any `speaker_ids` at all, usually
exactly one, while AssemblyAI hears up to 13 voices; the counts agree on 5 videos out of 160.
**Naming the speakers is a separate ticket**, not part of this load. The 11 single-speaker videos
are the trivial subset; the other 149 need a resolution pass over the transcripts themselves, where
people introduce and address each other by name.

## 9. Summaries

The 96 missing summaries are written from the transcripts in Andy's #70 format — one lead line, then
4–5 labelled bullets, WhatsApp bold — and stored on `videos_catalog.summary` with
`summary_source='transcript'`. The existing 65 are not regenerated.

**One format for all 96, restricted or not** (§3.8). For the 70 restricted ones this summary is the
*only* thing a member can receive about the content, which raises its importance: it must stand on
its own without the transcript behind it.

`videos_catalog.search_tsv` already indexes the summary at weight B, so filling this column also
improves video-level search independently of the chunks.

## 10. Acceptance criteria

1. **96 videos gain chunks; the 65 Zoom videos are byte-identical before and after.** Proven by row
   counts per `video_id` and a checksum over the pre-existing 3,116 rows.
2. **Every new chunk carries `meta.provenance = 'assemblyai'`** and a `start_sec` that resolves to a
   real moment in the video.
3. **`sensitivity` matches `access_restriction` on every new row**, verified by a join against
   `videos_catalog` returning zero mismatches.
4. **`source_id` collides with nothing.** `content_items_source_id_uq` already enforces
   `UNIQUE (source, source_id)`, so a collision fails the insert rather than corrupting a Zoom row —
   the AC is that the load completes without hitting it.
5. **All new rows embedded**, no NULL embeddings outside the deliberate under-30-character rule.
6. **A probe returns a passage from a non-Zoom video with its video link** — e.g. a Chapter
   Boardroom question that no Zoom transcript could have answered before.
7. **A restricted video's passage is not returned to a default search**, and its title still is.
8. **A restricted video returns its summary plus the may-be-restricted wording**, proven on a real
   probe, and returns no transcript passage in the same answer.
9. **`video_search` was replaced, not dropped** — `CREATE OR REPLACE`, EXECUTE still granted only to
   `service_role` and not to PUBLIC, verified after the change.
10. **The vector-branch question in §7.3 is answered in writing** — either the embedding excludes
    restricted content text, or it is recorded as a known pre-existing behaviour with a ticket.
11. **96 summaries written**, `summary_source='transcript'`, none of the existing 65 modified.
12. **Leak gate GREEN** (`python3 scripts/olivia_leak_gate.py`, exit 0).

## 11. Non-goals

- The other 872 videos (2018–2025).
- Naming the `A`/`B`/`C` speakers.
- Chapters or auto-highlights.
- Re-transcribing anything Zoom already covered.
- Any change to `content_search_v2`, `multi_source`, the prompt layer or the production workflow.
  (`video_search` **is** changed — see §7.2 — but only in what it returns for restricted rows.)
- Resolving who may see a restricted video. That needs the export change in §7.1 and is its own
  ticket; this spec deliberately ships the temporary posture instead.
- Hosting the videos on Mux — separate idea, separate ticket.

## 12. Risks

| Risk | Handling |
|---|---|
| A load bug damages the 65 Zoom rows | The loader filters to video_ids with zero existing chunks and never issues an UPDATE. AC 1 checksums the untouched set. |
| Anonymous speakers read as low quality | Stated plainly in the body as `Speaker A`, never guessed. Named attribution is its own ticket. |
| A restricted transcript leaks | `sensitivity` from the catalog per row; restricted chunks additionally carry `access_rule` type `video_access`, unknown to every reader except the taught branch of `content_search_v2`; gate checks cover unentitled, inactive-entitled, and anon. |
| The panel's 63 phantom accounts gain access | The loader filters to `real_match` rows structurally — `panel_only` never loads. |
| A grant attaches to the wrong human | Emails resolve only through `digest.resolve_member_by_email()`, which refuses ambiguity; unresolvable grants store against NULL and are reported. |
| `source='call_transcript'` misleads a future reader | `meta.provenance` distinguishes them, and this spec records why. |
| Presigned links expire 2026-08-27 | Irrelevant to this load — the transcripts already exist as local JSON. Only a re-transcription would need fresh links. |

## 13. Rollback

Every row this load writes is identifiable by `source='call_transcript'` plus
`meta->>'provenance' = 'assemblyai'`. Rollback is one DELETE on that predicate plus reverting
`summary` to NULL where `summary_source='transcript'` on the 96. Nothing else in the system holds a
reference to these rows.

The `video_search` change rolls back separately and independently: re-apply the previous body with
`CREATE OR REPLACE` and re-run the gate. The current definition is captured in the plan before the
change is made, so the revert is a paste rather than a reconstruction.

## 14. The access load — was "the plug-in path", now IN SCOPE

Written before the rules existed; the rules arrived the same day (§7.2), so this section is no
longer contingency — it is part of the build. Kept because its decisions still govern the loader.

### 14.1 The format — superseded by the actual file

What arrived is better than what was asked for: `mds_video_audience_pairs.csv` carries
`video_id, title, upload_date, email, name, edge_type, panel_match, real_match, verdict, can_login`
— per-rule provenance included. The loader consumes that file directly; the request below stands
only as the minimal shape for any future re-export.

One row per person per video, as CSV:

```
video_id,email
697379ce17d8f8116b1f96d4,someone@example.com
```

**Email is the identifier that matters.** `digest.member_profiles` and the Members DB key on it, so
an email list resolves cleanly and unambiguously. A list of *names* resolves at roughly the rate #89
measured on Zoom attendance — 170 of 199 after a three-rung matching ladder — and every miss is a
member wrongly denied their own content. Names are usable as a fallback; email avoids the problem
entirely.

`video_id` is the Mongo ObjectId already used everywhere here — the same value in the catalog, the
export CSV and every transcript's `_mds` block.

Expected volume is modest even at the top end: the flattened rule strings show named-user counts
from 1 to 621 per video, so the whole 2026 set lands in the low tens of thousands of rows.

### 14.2 What gets built

1. **`digest.video_access`** — `(video_id, at_member_id, source, granted_at)`, one row per entitled
   member per video, loaded idempotently from the CSV via an email → `at_member_id` resolve. Rows
   that fail to resolve are reported, never silently dropped.
2. **`video_search` gates on it.** A restricted video the asker is entitled to returns its full
   treatment; one they are not returns today's summary-plus-warning. The `p_phone` → asker
   resolution already exists in the function.
3. **`content_search_v2` becomes able to return restricted passages to entitled askers** — this is
   the actual payoff: quotes with timestamps from the rooms a member was in.
4. **The warning line comes out** for entitled members and stays for everyone else.

### 14.3 What is NOT redone

The transcripts, the chunks, the embeddings and the summaries are all unaffected — `access_rule` and
`sensitivity` are metadata on rows that already exist, so the flip is an `UPDATE`, not a reload. No
re-chunking, no re-embedding, no re-transcription, no cost.

The 6 restricted Zoom videos already in `content_items` flip in exactly the same `UPDATE`, since
they carry the same shape. That is the reason §6 keeps the new rows' `access_rule` and `sensitivity`
identical to the existing ones rather than inventing a second mechanism for the same idea.

### 14.4 The quote question — RULED (Andy 2026-08-20)

*"If I can see videos, then I can search through transcripts."* Entitled members get quotes,
summaries, TLDRs and exact-words follow-ups from restricted rooms; nobody ever gets a full
transcript. §7.2 carries the full ruling and its structural enforcement.
