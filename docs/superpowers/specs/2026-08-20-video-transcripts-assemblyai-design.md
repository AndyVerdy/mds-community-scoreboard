# AssemblyAI transcripts for the 96 videos Zoom never reached

**Date:** 2026-08-20 · **Status:** design, awaiting Andy's review · **Scope:** the 2026 GroupOS video library only (161 videos), of which 96 are net-new

#70 put transcripts into Olivia on 2026-08-07, sourced from Zoom. Zoom only transcribes calls Zoom
hosted, and only from around January 2026. Everything else in the library — Chapter Boardrooms,
Inspire sessions, the Hack Contest, hybrid rooms — has no spoken-word record anywhere. This spec
covers filling that hole with AssemblyAI transcripts, reusing #70's machinery rather than building
alongside it.

**Almost nothing in the retrieval layer changes.** No migration, no new table or column, no new RPC,
no prompt or seed edit, no workflow change. The load itself writes into tables and columns that
already exist, using a chunker and loader that already run. The one exception is a
`CREATE OR REPLACE` on `digest.video_search` and the matching leak-gate checks, required by Andy's
ruling in §3.6 on how restricted videos are answered.

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
6. **Restricted videos are answered from their summary, never their transcript.** Olivia reads the
   material, answers, and suggests the video with a short summary and a line saying the video may be
   restricted and the member may not have access. She never returns a passage or quote from one.
7. **Until the restriction rules are readable, every asker is assumed to have access.** We cannot
   compute who may see a given video (§7), so the system stops implying that it can: the caveat
   moves into the wording instead of the gate. **Andy's explicit ruling, and explicitly temporary.**
8. **Restricted summaries are written in the normal format** — names and specifics included. A
   topic-level redacted variant was proposed and ruled out, since assuming access makes it moot.

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
| `access_rule` | `{"type": "public"}` |
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

### 7.2 The temporary posture (Andy's ruling, §3.7)

Because access cannot be computed, it is not faked. Every asker is treated as having access, and the
uncertainty is disclosed in the answer instead:

- Restricted video matches → Olivia names it, gives the **short summary**, and says the video may be
  restricted and the member may not have access.
- Restricted video transcript → **never returned**, no quote, no passage, no timestamp jump.
- `video_search` is changed by `CREATE OR REPLACE` (never `DROP` — that resets EXECUTE to PUBLIC) to
  return `summary` for restricted rows, replacing today's hard-coded
  `"Never describe, summarize or guess its content."` instruction string with the new wording.
- The leak-gate checks that currently assert *restricted returns no summary* are inverted to assert
  *restricted returns the summary and no transcript passage*. The rule keeps living in the gate.

**Accepted exposure, recorded deliberately:** a member without access can receive a summary of a room
they were not in — 70 of these 96 videos, plus the 6 restricted Zoom videos already loaded. Andy was
shown this and ruled it acceptable as a temporary state.

**Reversal condition:** when the export carries the raw rule ids and the resolvers exist,
`video_search` gates on real access and the warning line is removed. **Nothing in this load is
redone at that point** — the transcripts and summaries stay exactly as written; only the gate
changes.

The restricted-recording principle from #71 still holds: a restricted recording must not hide its
event. The video stays listed by title and date regardless.

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
| A restricted transcript leaks | `sensitivity` is set from the catalog per row, not from a list; AC 3 proves it by join; the gate covers the retrieval path. Passages stay unreachable under the temporary posture too. |
| A member without access reads a summary of a room they were not in | **Accepted, temporarily** (§3.7, §7.2). Andy was shown the exposure and ruled it. Bounded to summaries — never passages — and reversed the day the rule ids land. |
| The temporary posture becomes permanent by forgetting | The reversal condition is written into §7.2, the warning wording is user-visible on every restricted answer, and the gate checks name it as temporary. |
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
