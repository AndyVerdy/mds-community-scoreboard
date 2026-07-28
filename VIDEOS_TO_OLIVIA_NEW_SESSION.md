> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Videos → Olivia (source #5) — NEW SESSION BRIEF

**Paste this whole file as the first message of the new session.**

Written 2026-07-26 by the Olivia answer-quality session, which is running **concurrently**. Every
number below was verified live against Supabase at write time — but per the SOP you must **re-verify
before building**, not trust this doc.

---

## 0. THE BOUNDARY — read this first, it is the whole reason this doc exists

Another session is **actively editing Olivia's retrieval and prompt layer right now**. n8n has no
merge: two sessions editing the same workflow means one silently overwrites the other.

**DO NOT TOUCH — owned by the concurrent session:**
- n8n workflow `12wj6h1TWqb0d4Dq` (Olivia POC v3) — **any node, for any reason**
- Supabase RPCs `digest.content_search`, `digest.multi_source`
- The `Plan Request` / `Build Prompt` node code

**YOURS — fully additive, zero collision risk:**
- Everything in `public.videos` / `public.transcript_segments`
- A **new** gated RPC (suggested name `digest.video_search`)
- New rows in `digest.content_items` (if you choose that route — see §2)
- New checks appended to `scripts/olivia_leak_gate.py`

**Your session ENDS at a proven RPC.** The final "wire it into Olivia" step is a handoff back, done
once, by one session. Build right up to that line and stop. Say so clearly in your close-out.

---

## 1. WHERE THE REAL DATA IS — verified live 2026-07-26

**The real video library is in GroupOS, not Supabase.** An earlier draft of this brief claimed the
data was already in Olivia's database — that was **wrong**, and the correction is the most important
thing in this document.

**GroupOS = the real library (current, rich, 1,009 videos).** Verified via the GroupOS MCP
(`videos_list`, community `67011d987a2a81b28438a3d8`):

- **1,009 published videos**, newest **2026-07-23** — i.e. 3 days old. This is live production content.
- Real MDS content: Mogul Calls, Expert Calls, Channel Calls (TikTok/M&A/Logistics/AI), Vancouver AI
  Mastermind, Hot Seats.
- Per-video fields: `title`, `description` (HTML), `duration`, `category_names` (e.g. "Channel Calls",
  "TikTok"), `tag_names`, `speaker_ids`, `event_ids`, `view_count`/`like_count`/`comment_count`,
  `restriction_access` (**"restricted"** on the sample), `status`, `created_at`, `deleted_at`.
- ⚠️ **NO transcript field.** There is no spoken-word text anywhere in the GroupOS record.

**Supabase `public.videos` = abandoned POC test data. IGNORE IT.** All 15 rows were uploaded in a
single dev session on **2026-05-07/08** (2.5 months stale): titles are `Untitled` ×8, `Test 1`,
`Test 2`, `Test 3`, `hello`, `Alex Chiru`; **7 of 15 are soft-deleted**; `recorded_at` is NULL on
every row. Exactly one row has a real title. The 2,488 `transcript_segments` belong to these test
uploads. **None of this is MDS's video library** — do not build on it, and do not let its schema
mislead you into thinking transcripts exist at scale.

---

## 2. THE PROJECT IS TWO PHASES WITH VERY DIFFERENT PRICE TAGS

Decide with Andy which one you are doing. Do not silently slide from one into the other.

### Phase 1 — the catalogue (cheap, days, high value)
Index the 1,009 videos' **metadata**: title, description, category, tags, speaker, duration, link.
- Embedding ~1,009 short records on `voyage-3.5-lite`: **pennies**.
- Unlocks today: *"what videos do we have on TikTok?"*, *"was there a Mogul Call about hiring?"*,
  *"show me the M&A channel call"* — with a direct link.
- **This alone is a legitimate, shippable source #5.** Recommend doing exactly this first.

**⭐ THE VIRTUAL CALLS ARE HERE — Andy's point 2026-07-26.** MDS's recurring virtual calls are a data
source Olivia has **never been connected to**, and they live in this video library, cleanly tagged:

| tag | count (verified 2026-07-26) |
|---|---|
| `Mogul Call` | **201** |
| `Channel Call` | **81** |
| `Expert Call` | **53** |

That is **335 of the 1,009** videos. Two things make this much cheaper than it looks:
- **`description` already contains a written session summary + a numbered TOPICS list** (e.g. the July
  2026 TikTok Channel Call lists "Managing TikTok creators and affiliate communities / Fulfillment and
  operations setup for TikTok orders / GMV Max strategy and creator outreach"). **You can answer "what
  was covered on the X call" from Phase 1 alone — NO transcription required.**
- Many records carry **`event_ids`**, linking the video to the very `digest.events_catalog` row Olivia
  already answers date/time questions from. Join on it and one answer can give the date AND the content
  AND the link.

⚠️ The events lane was fixed on 2026-07-26 to answer Mogul/Expert/Channel Call **calendar** questions
(date, time, host). It has **no idea what was discussed** on any of them. Do not assume that fix
covers this — it is exactly the gap you are closing.

### Phase 2 — transcripts (expensive, weeks, transformative)
Searching *inside* videos needs transcripts, which **do not exist** for the 1,009.
- ~1,009 videos × ~1 hour ≈ **~1,000 hours of audio**.
- AssemblyAI at roughly $0.12–0.37/hr ⇒ **~$120–370 one-time**, plus the pipeline to fetch each
  `video_url`, transcribe, chunk, embed and store. **Price it precisely and get Andy's explicit
  approval before spending a cent** — see §5.
- Only after this can Olivia answer *"what did Lisa say about hiring a C-suite"* with a timestamp.

**Do not promise Phase 2 value on a Phase 1 budget.**

---

## 3. NON-NEGOTIABLE — access control

- **`restriction_access`** is `"restricted"` on the sampled video. Find out what restricted means in
  GroupOS (which tiers/roles) **before** any video becomes reachable through Olivia. Do not assume
  every member may see every video.
- **`status`** — index `published` only; never `draft`, `scheduled`, `paused` or `archived`.
- **`deleted_at IS NOT NULL` → never surface.** Ever.
- **Auth ceiling:** `whoami` reports `tier: "public"`, `pat_id: null`, scope `videos:read`. The
  **`GROUPOS_PAT` is a long-standing top ask** and may gate what you can legitimately read. Establish
  early whether the public tier is enough; if not, that is a blocker to raise, not to work around.
- **Video URLs** are storage paths (`uploads/content-archive/videos/...`), not playable links.
  **Safest for v1: link to the video in the MDS app, never a raw storage/Mux URL.** If signed playback
  comes up, read memory `reference_mux_signing.md` first.

**The gate is the ship criterion:** `python3 scripts/olivia_leak_gate.py` (111 checks) must be
**GREEN**, and you must **add video-specific checks to it** — a deleted video, a wrong-org video, and
a non-public video must each be provably unreachable. A source without gate checks is not done.

---

## 4. SOP (from CLAUDE.md — this folder is multi-project, the rules are real)

- **Verify against live before building.** This doc, ClickUp and memory can all be stale.
- Every "it works" claim cites a live check — exec id, SQL result, gate green. Never "should work."
- **Close-out:** prepend a dated entry to `SESSION_LOG.md`, update this doc's successor, update
  memory with durable facts only, then ClickUp (decisions + high-level state only).
- ⚠️ `SESSION_LOG.md` is **shared with the concurrent session** — expect a git conflict and merge it,
  don't clobber.
- SQL migration traps already paid for: POSIX regex classes only; `bool_and` ignores NULLs;
  generated-column helper fns need `service_role EXECUTE`; and after any `DROP+CREATE` on an RPC run
  `NOTIFY pgrst, 'reload schema'` **and hammer the REST path** — stale PostgREST pool caches cause
  intermittent 404s that look exactly like random quality regressions (memory:
  `reference_pgrst_reload_after_rpc_ddl.md`).

---

## 5. SPEND — please read, this is live context

On **Jul 24–26 the Anthropic bill was ~$161**, against a normal all-tools baseline of **$1–3/day**.
It drained the account and took Olivia **down in production** — real members got "Sorry — I could not
generate an answer just now." Cause: an eval harness looping expensive full runs unguarded.

Practical rules for you:
- Embeddings (Voyage) are cheap — fine. **LLM loops are what kill you.**
- Never put an LLM call inside an unbounded `while`/retry without a hard cap.
- Prefer Haiku for mechanical passes; reserve Sonnet/Opus for genuine reasoning.
- `mds-scorecard-tools/olivia_eval.py` now has a **$15/day spend guard**; don't route around it.

---

## 6. RELATED CONTEXT — read first-hand, don't take my summary for it

- **Video platform anchor:** CU doc `2531q-98637` (11 pages). **Read `/Users/Born/mds-video-admin/SESSION_LOG.md`
  top entry FIRST** — that's the migrated Page 11 and holds current state.
- **Separate repos stay separate:** `/Users/Born/mds-video-admin/` and `/Users/Born/mds-ai-bot/` are
  their own projects. `mds-ai-bot` already embeds ~9,879 transcript chunks for its *own* RAG — that is
  **not** Olivia's retrieval path and must not be confused with it.
- **GroupOS MCP** exposes `videos_list` / `videos_get` / `video_comments_list` — a possible source of
  view/engagement metadata later. Not needed for v1.

---

## 7. ONE THING TO FLAG AT HANDOFF, NOT NOW

Olivia's style prompt currently tells her, verbatim, that she **cannot** search inside recordings and
that the capability "is coming." Once videos are wired in, that line becomes a lie and must be
removed — it lives in the `Build Prompt` node, which is **owned by the other session**. Put it in
your close-out as a required wiring-step action. Do not edit it yourself.

---

## Suggested first three moves

1. **Re-verify §1 yourself** against GroupOS (`videos_list` with `with_total`) — confirm the 1,009 and
   pull the distinct `status`, `restriction_access` and `category_names` values. Write down what
   "surfaceable to a member" means before indexing anything.
2. **Answer the auth question early:** can the current public-tier token legitimately read the
   restricted videos Olivia would cite? If not, raise `GROUPOS_PAT` as a blocker immediately — do not
   build a source on access you are not sure you have.
3. **Build Phase 1 only** (catalogue → gated RPC), prove it with a real member phone, extend
   `scripts/olivia_leak_gate.py` with video checks and get it **GREEN**. Then stop and hand off.
   Bring Phase 1 numbers *and* a precise Phase 2 transcription quote to Andy as one decision.
