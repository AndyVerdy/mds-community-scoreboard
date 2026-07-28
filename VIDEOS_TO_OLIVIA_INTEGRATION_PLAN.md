> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Videos → Olivia (source #5): integration plan

**Written 2026-07-26** by the session that built the source. **Audience: the agent leading data
connections.** Everything below the "Built and live" line is done and verified; everything under
"What integration requires" is not started.

**This plan deliberately stops at the workflow boundary.** The data layer is finished and gate-green.
The n8n wiring is a separate, single-owner job — see §6.

---

## 1. State — built, live, verified 2026-07-26

| | |
|---|---|
| Videos ingested | **1,009** — reconciles exactly to the GroupOS `with_total` (614 public / 395 restricted), 0 dups, 0 gaps |
| Reachable by a member | **614** (`access_restriction = 'public'` == the admin UI's "All members") |
| Span | 2018-06-27 → 2026-07-23 · **725 hours** |
| Categorised | 983 (97.4%) — ⚠️ **inferred**, see §4 |
| Speaker named | 399 of the 432 videos that carry speaker ids |
| Attachment text searchable | 518 videos (268 of them public) · 4.8 MB |
| Leak gate | **GREEN, 140 checks** — 22 of them video-specific |

**Objects (all in the `digest` schema, all `service_role`-only, RLS on):**

| Object | Purpose |
|---|---|
| `videos_catalog` | 1,009 rows. Catalogue + `cliff_notes` + `files_text`. Generated `search_tsv` weights title & speakers A, category/tag/cliff/files B, description C |
| `video_speakers` | 234 resolved GroupOS users (170 members · 63 guest-tier · 2 collaborators). `email` is a matching key, **never emitted** |
| `video_files` | 643 attachments + `file_kind` + `extracted_text`. `storage_path` never emitted |
| `member_video_url(text)` | The one place a video URL is constructed |
| **`video_search(p_phone, p_query, p_limit)`** | **The only retrieval entry point.** Gated, fail-closed, SECURITY DEFINER |

**Migrations:** `videos_catalog_and_search` · `videos_catalog_cliff_notes` · `video_speakers` ·
`video_files`
**Scripts:** `mds-digest-web/scripts/ingest_videos.py` (`--videos` / `--files` / `--speakers` /
`--prune-missing`) · `Scorecard/scripts/olivia_leak_gate.py` §12

### `video_search` contract

```
digest.video_search(p_phone text, p_query text default null, p_limit int default 8)
  -> title, speakers[], description_snippet, cliff_notes_snippet,
     attachments jsonb [{name, kind}], duration, categories[], tags[],
     published_at, video_url, matched_rank
```

- Gate: `p_phone` must resolve to **exactly one** member with an `at_member_id`, else zero rows.
- Filters, all three independent: `status='published'` **AND** `access_restriction='public'`
  **AND** `deleted_at is null`.
- No query ⇒ browse mode, newest first. Query ⇒ FTS with `expertise_query` synonyms + a strict-match
  bonus, same ranking approach as `partner_lookup`.
- Emits **name + kind** for attachments; never a storage path, internal id, tier or email.

---

## 2. What integration requires — not started

> ### ⚠️ STEP 0 — RECONCILE WITH THE VIRTUAL-CALL POLICY SHIPPED 2026-07-26 (added by the
> answer-quality session; the videos session did not know about this)
>
> Andy ruled that virtual calls are an unconnected source, so `Build Prompt`'s **events** lane now
> tells members: *"MDS virtual calls — Mogul, Expert and Channel Calls — are being added to what I can
> see right now."* Live and verified.
>
> **Once videos ship that statement is half false**, and Olivia will claim the gap and answer from it
> in the same reply. The line must be re-scoped, not deleted — it stays TRUE for:
> - the **395 restricted** videos (39% of the library) that remain dark, and
> - **anything said inside a recording** — there are no transcripts, so "what did X say about Y"
>   must still refuse rather than paraphrase a description.
>
> It becomes FALSE for the ~318 reachable call recordings, where she can now name the session, the
> speaker, the date and give a link. Rewrite it to that boundary, and add a DoD case proving
> *"what did <speaker> say about X"* does NOT fabricate from description text.
>
> **Also worth doing before integration — CALL TYPE IS NOT BLOCKED ON GOS-24.** §4 concludes the
> Mogul/Expert/Channel axis is unreachable because subcategory names are absent, but the TITLES carry
> it: `tag_names` covers **133** of 1,009 while a title match covers **486** (201 Mogul · 53 Expert ·
> 81 Channel; **318 reachable**). Derive a `call_type` column from the title and "show me the latest
> mogul call" — your own listed target phrasing — works today with no GroupOS dependency.

Follow the standing 8-step source-addition checklist. Concretely:

1. **`Plan Request` / `Route Request`** — new `videos` intent. Real phrasings to cover: *"is there a
   video about X"*, *"what calls do we have on X"*, *"recording of the M&A channel call"*,
   *"what did <speaker> talk about"*, *"show me the latest mogul call"*. Add `video` to the **search**
   and **solve** lanes' `p_sources` where a video is a legitimate answer.
2. **`Build Prompt`** — a FROM THE VIDEO LIBRARY block. Render **title · speaker · date · duration ·
   category**, then the cliff-notes snippet if present, else the description snippet, and **always the
   `video_url`**. Attachment names are worth surfacing (*"the deck is attached to this video"*) but
   there is no way to send the file yet — see §5.
3. **`multi_source`** — add a videos branch plus the matching Build Prompt `multi` block, so videos
   join the fan-out rather than living in their own lane only.
4. **Help capability list** (`plan.route==='help'` in Build Verbatim) — add videos; remove it from the
   "Not yet:" line.
5. **Returning-member greeting** — broaden if the headline set changed.
6. **⚠️ Remove the style-prompt line that says Olivia cannot search recordings.** It currently states
   the capability "is coming". Once this ships that line is false. It lives in `Build Prompt`.
7. **Re-run `scripts/olivia_leak_gate.py` — must be GREEN before ship.**
8. **Docs:** `MDS_OLIVIA_ASSISTANT.md` §8x + changelog, `MEMBER_ATTRIBUTES_SOURCE_MAP.md` (already
   updated for the data layer), memory.

---

## 3. Non-negotiable rules for the prompt layer

**3a. Video text is NEVER evidence of membership.**
Six video descriptions assert someone is a member. At least one of those people has since been
removed: Billy Evans (`bill@microscope.com`) is **"Removed - Canceled Membership"** in
`digest.member_profiles`, while the description of video `64cd5fa4…` calls him *"a skilled member of
MDS"*. `member_card('Billy Evans')` returns **zero rows** — so there is nothing to contradict the
video text, and silence reads as assent.

> **Rule:** membership status comes only from the member layer. Absent from `member_card` =
> **unknown, never "member"**. Never repeat a membership claim found in a video title, description,
> cliff note or attachment. Applies equally to FB posts and chat messages.

**3b. Never imply the library is complete.** 395 of 1,009 videos (39%) are invisible to Olivia because
GroupOS won't tell us who may see them. If a member asks about Centurion, TikTok-channel or
AI-Mastermind content, Olivia will find nothing and must not imply nothing exists.

**3c. Don't quote engagement numbers.** `view_count`/`like_count` are stale (0 on every 2026 video);
they are stored but excluded from `video_search` output by design.

---

## 4. Known weaknesses — read before trusting an answer

| Weakness | Detail |
|---|---|
| **Categories are inferred** | The API returns `category_names: []` for 86% of videos. Coverage went 14% → 97.4% by mining the id→name map from the 142 that resolve. Validated twice against the admin UI, but it is **inference, not source**, and will rot as categories are renamed. 36 videos remain unnamed |
| **Subcategories: zero coverage** | 957 videos carry `subcategory_ids`; **no names exist anywhere in the API** and nothing can be reverse-engineered. This is the call-type taxonomy (Mogul / Expert / TikTok / Centurion 20M+ Calls) — the axis members actually ask along |
| **No transcripts** | Nothing inside a recording is searchable. 28 Otter PDFs exist as attachments but **Andy ruled them test data (2026-07-26) — flagged `test_data`, text removed, excluded from search** |
| **Cliff notes: 1 of 1,009** | The API doesn't expose the field. The single populated row was pasted by hand as a proof |
| **Video↔event link broken** | 566 videos carry `event_ids` for 208 events; only 3 resolve against `events_catalog` (different id namespaces) |
| **36 speakers unresolved** | Likely removed users; public tier can't query `status: removed` |
| **No refresh** | One-time manual pull. New videos will not appear until someone re-runs the ingest |

---

## 5. Blocked on GroupOS — see `GROUPOS_MCP_VIDEO_REQUIREMENTS.md`

Ten items, GOS-22 → GOS-34. The ones that gate Olivia's answer quality:

- **GOS-32 (🔴🔴 security, unrelated to Olivia but ship-blocking as a priority):** restricted videos'
  attachments are publicly downloadable and the public-tier API hands out the paths.
- **GOS-25:** restriction rules invisible ⇒ 39% of the library dark.
- **GOS-22:** cliff notes absent ⇒ the best per-session summary is unreachable.
- **GOS-24:** subcategory names absent ⇒ call-type routing impossible.
- **GOS-28:** timecoded transcripts ⇒ the "at 14:32 of…" end state.
- **GOS-29:** unfetchable file URLs ⇒ attachments can't be sent to a member.

**Sending attachments on demand** reuses the existing FB-image path (private bucket → signed URL →
WhatsApp). Designed, not built, because the source URLs don't resolve safely yet.

---

## 6. Coordination — the part most likely to cause damage

- **n8n workflow `12wj6h1TWqb0d4Dq` is single-owner.** Two sessions editing it means one silently
  overwrites the other; that has already happened once (2026-07-24, ~16:2x UTC).
- **Edit the ACTIVE workflow, then ONE bounce** `[{deactivateWorkflow},{activateWorkflow}]`. Never
  deactivate first — that caused an 8.5-hour dead-webhook outage.
- **Re-fetch the node immediately before any PUT.**
- `$`-dense node rewrites use full `updateNode`, never `patchNodeField`. `Format Reply` contains a
  `'*$1*'` line that must never appear in a patch replacement.
- After any `jsCode` patch, check LIVE declaration order (a TDZ error once broke every inbound) and
  run `scripts/olivia_selftest.py --questions "..."` then **always `--cleanup`**.
- After any `DROP+CREATE` on an RPC: restore grants explicitly (a drop reset `event_who` to PUBLIC
  once), `NOTIFY pgrst, 'reload schema'`, then hammer the REST path — stale PostgREST pool caches
  cause intermittent 404s that look like random quality regressions.

---

## 7. Open decisions for Andy

1. ~~**Which video URL is canonical**~~ — **RESOLVED 2026-07-26 by the answer-quality session.**
   Measured against real member behaviour in `content_items`: **52 member-shared links use
   `app.mds.co/videos/{id}` across 11 different chats; ZERO use `app.mds.co/s/videos/{id}`.**
   The currently-implemented form is correct. (HTTP 200 on both proved nothing — the app is
   client-routed — so this was settled by what members actually paste, not by status codes.)
2. **Restricted videos** — stay dark until GOS-25, or is there an interim rule we can encode?
3. ~~**Negative membership signal**~~ — **RESOLVED + SHIPPED 2026-07-26** (Andy's ruling, built by
   the answer-quality session). `member_card` now returns PAST members with `membership_state`
   ('current'/'past') + `joined` + `left_date`, so "I don't have a member named X" is no longer said
   about someone we hold. The REMOVAL REASON is never emitted — 'Removed - For Cause' and staff notes
   stay sealed; only the coarse state leaves the DB. People who were never members (applicants, leads)
   remain invisible. 4 new leak-gate checks enforce this; gate GREEN at 145.
   **This makes rule 3a enforceable rather than advisory** — a membership claim in a video description
   can now be contradicted by the member layer instead of meeting silence. Billy Evans returns a card
   with `membership_state='past'`, so "a skilled member of MDS" in that video description is
   answerable as *was*, not *is*.
4. **Vision pass over attachments** — 54 files / ~2,154 pages have text too thin to be real content
   (design-heavy decks). Price on a 10-file sample first. Separately, 420 attachments are
   unclassifiable by filename and would benefit from a per-file read.

---

## 8. Definition of done for the integration session

1. A real member phone, over real WhatsApp, gets a correct answer with a **working** link for:
   *"is there a video about hiring a C-suite?"* → Lisa De Rosa's Mogul Call.
2. A restricted-content question returns **nothing**, and does not imply nothing exists.
3. A membership question about Billy Evans does **not** call him a member.
4. `scripts/olivia_leak_gate.py` **GREEN**.
5. `scripts/olivia_selftest.py` run, then `--cleanup`.
6. The "can't search recordings" line is gone from the style prompt.
7. `SESSION_LOG.md` entry + `OLIVIA_NEXT_SESSION.md` refreshed.

---

## 9. Refresh runbook (until a GroupOS token lands)

```
videos_list  → JSON pages on disk (date-windowed; ~11 pages at limit=100)
python3 scripts/ingest_videos.py --videos  <pages>
python3 scripts/ingest_videos.py --files   <pages>
python3 scripts/ingest_videos.py --speakers <members_list output>
re-run the category id→name backfill   # inference, re-verify against the UI
python3 scripts/olivia_leak_gate.py    # must be GREEN
```

Reconcile the row count against `videos_list … with_total` every time — drift means a silent
delete or unpublish. `--prune-missing` removes rows no longer in the library (sanity floor: 500 ids).
**GOS-30 (`updated_after`) would turn this into an incremental job; GOS-26 (field projection) would
make it cheap enough to schedule.**
