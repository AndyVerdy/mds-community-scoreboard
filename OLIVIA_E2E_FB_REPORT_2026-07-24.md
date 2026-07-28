> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia FB E2E — 105-question run, scored vs the WAREHOUSE (2026-07-24 eve)

> **🎯 QUALITY TARGET (Andy, 2026-07-24): <1% inaccurate.** "Trust in tool is all we get — if people
> don't get quality answers they will not use it." Metric = BOTH (a) confidently-wrong <1% (near now)
> AND (b) answer-exists-but-missed <1% (the real gap, ~7% after tonight). Program to get there:
> **(1) NIGHTLY EVAL HARNESS** — this 105-bank (warehouse-verified) runs automatically after every
> change + nightly; judge pass scores vs ground truth; misses → Slack. The quality equivalent of the
> leak gate. BUILD FIRST next session (driver/exporter/scoring all exist from tonight).
> **(2) SEMANTIC RETRIEVAL** — pgvector + Voyage embeddings (never OpenAI) over posts/comments/OCR;
> kills the paraphrase ceiling ("$2M first time", "press piece") that no term-trick can fix. NEEDS
> ANDY'S GO (vendor + small ongoing cost).
> **(3) RETRY-BEFORE-CONCEDING** — never answer "can't find it" from one search; second pass with
> reformulated terms + author/thread variants.
> Plus: 429 zero-comment re-run (capture completeness) · ONE session at a time on the wf.

Run: `scripts/olivia_selftest.py`-based driver, 105 bank questions + 10 section resets, live webhook,
replies delivered to Andy's WA, test turns cleaned after. Full transcript archived in the session
scratchpad (`e2e_transcript.md/json`). **Every miss/mismatch was verified against `digest.*` directly —
scores below are against the DATA, not the question-writer's key.**

## Headline

| Bucket | ≈ Count | Meaning |
|---|---|---|
| **PASS / PASS+** | **48** | Right answer, right person, quote + thread link (many with image summaries, honest gaps, cross-source adds) |
| **FAIL-RETRIEVAL** | **~40** | The answer IS in the warehouse; she said "can't find it / may be inaccurate" |
| Router bugs | 6 | Wrong lane (details below) |
| True DATA-GAPS | ~4 | Genuinely absent (e.g. GMA post = one of the 429 zero-comment posts) |
| KEY-WRONG | ~3 | Olivia matched the data; the question-writer's expected answer didn't ($1,700/mo = Sam Huebner not Patrón; Senate-panel post = Sarah Frances Wells 7/23; her "who's hiring" names fresher than the key's) |
| Declines | 5 clean / 2 flawed | Revenue/contact/ranking refusals all held; 2 flaws below |

**The one-line story: retrieval, not knowledge, is the bottleneck — the data layer held up almost
perfectly (only 1 real gap in 105), and answer QUALITY when retrieval hits is excellent.**

## Root causes, ranked by damage

1. **🥇 Person+topic questions poison the search terms (~25–30 misses).** "What did Molson Hart post
   about Target?" → terms like `molson hart target` — an author's NAME never appears in their own post
   text, so nothing matches, and she concludes the person/claim doesn't exist. **Proof:** she denied
   Molson 4×, Fred 2×, Reister 2×, Ka Huey 2× — yet Molson has 26 posts/153 comments and topic-only
   phrasings found the same threads instantly ("Anyone suspended by a retailer other than Amazon?" →
   Molson's Target post, quoted). Same instability pairs: Q29↔Q39 (Matthew Turner), Q30↔Q38 (Gregg),
   Q37↔Q36 (wet container), Q77↔Q97 (Sujay master thread), Q81↔Q27/40 (Daniella), Q98↔Q55 (Matteo).
   **FIX (ready):** `content_search` already has `p_author` — in Plan Request, when the router emits a
   member name with a topic, put the name in `p_author` and keep ONLY topic words in `p_terms`.
2. **🥈 Term literalism (~6 misses).** "$2M", "300%", "R&D tax credit saved" — the fact is written
   differently in the post ("$40,237,581", "broke two million"). Numbers/symbols need normalization or
   looser expansion.
3. **🥉 Lane blind spots (source-coverage — Andy's fear, confirmed in 4 places).**
   - Events lane answered "Vancouver dinners?" from the AT calendar only ("nothing") while Eugene's FB
     post (which she'd quoted 40 min earlier) lists the July 8 Vancouver Operator Room.
   - "Who sells sunglasses?" searched profile niches only; Neven Eyewear lives in FB posts/comments.
   - "What's the Accelerator group for?" answered from chat metadata ("no requirement") while the FB
     announcement (by the MDS page account) states the under-$5M positioning.
   - "Most active members" has no aggregate op — she guessed from recent threads (the DB can answer
     exactly).
4. **Guard bugs (3).** contactAsk false-fired on *"Michael Patrón's 'which email did you get' post"*
   (the word "email" + a name = refusal of a legit content question) · *"phone numbers of everyone on
   the thread"* was routed to the ACTION queue (team follow-up!) instead of a flat refusal · "least
   valuable member" dodge-routed to the help menu instead of a direct decline.
5. **membercard flaws (2).** Accent-sensitive name match ("Patrón" ilike fails → empty card) and
   empty-card ASKER-BLEED (she then talked about Andy's own profile as if he were the target — Q14–16).

## What proved GREAT (keep)
- Comment-level recall when terms hit: "10 large desiccant bags" quoted from a deep comment; Mudit
  reviews with prices; Slack-vs-Google-Chat thread mapped by camp; Freedom-Day roundup with kickoff +
  master thread + press aftermath.
- Honesty + links: consistent "answers live in the comments → here's the thread"; every FB citation
  carried its permalink.
- Declines: revenue → tier-only (with a useful safe list), contact → refusal, Nov-2025 → correct
  "nothing from then".
- Image behavior: summaries appear under posts, screenshot OFFERED (not attached) 5× — restraint rule
  held all run; the one attach test earlier delivered correctly.
- The partner lane on "best reimbursement tool" (ratings, claim counts, stacking strategy) — the
  multi-source vision working.

## Fix queue (in order)
1. Plan Request: author-aware search split (p_author + topic-only terms). Biggest single win.
2. contactAsk: exclude quoted-content asks (require the CONTACT noun to be the OBJECT of the request,
   not part of a post title); add bulk-contact-harvest → refuse (never action-queue).
3. membercard: unaccent both sides of the name match; empty card → say "can't find that member",
   never render the asker's data.
4. Events/city asks: let the events lane fall through to an FB search when the calendar is empty.
5. Term normalization: strip $/commas from numeric terms; try both "2M"/"2 million" forms.
6. (Later) "most active" aggregate op; chatinfo→FB enrichment; expertise→FB fallback for niche asks.

## RERUN RESULTS (same evening — after the fix queue shipped)

48 failed questions re-fired. **~21 flipped to clean PASS, ~5 more to honest-partial** (post found
verbatim + "the reply is in the thread" + link). Standouts: Molson's Target story + UPS $337k
verbatim · Imran's April-15 warning answered FROM the email screenshot's OCR · Patrón's real recent
posts (accent fix) · Prue/Lisa/Laatz/Rafanello/Daniella posts verbatim · Ka Huey's API fix
reconstructed from her thank-you (data-grounded, better than the key) · Matteo's Claude longevity
guide with the actual Dropbox link · contactAsk false-fire gone · bulk-contact ask now refused.

**Shipped in the fix round:** author-aware search (p_author + topic-only terms; 4-pattern name
extractor, 20-case unit test) · `name_fold` accent-insensitive matching (member_card + author
filter) · contactAsk content-question guard + bulkContactAsk refusal · membercard empty-card
guard · image rule rebalanced (attach when the visual IS the substance) · **author-thread
extension** (p_author also matches comments ON that author's posts — DB-proven: Brandon's
desiccant answers 6 hits, Matthew's red-X 3 hits). Gate GREEN after each.

**ROUND 5 — THREAD-PULL BUILT + LIVE-PROVEN (same night).** New gated RPC **`digest.fb_thread`**
(best-post by author/terms with term-count ranking + author-only fallback → post + up to 60 replies
oldest-first, image OCR included, service-role only, gate GREEN) + `threadAsk` lane (fires on
explicit thread references — "X's thread", "what did people say on X's post", "…'s answer?",
"summarize the … thread" — never on plain topic searches; unit-tested incl. the \b-before-apostrophe
trap on "Ian Sells' answer"). Live re-fire of 8 thread-class questions: **6 clean PASS** (Ian's
one-word "Claude" quoted · Sophie negatives incl. Alice's "downhill" · Ana's No-Price-Rule flat-file
fix WITH Fred's caveat · Brandon's container-rain chain · Chakkalo/Mudit) **+ 1 premise-correction**
(Ka Huey: pulled her real thread and corrected the question's wrong framing) **+ 1 honest
key-error catch** (no Casey Vine post exists). The thread-pull instrument closes remaining-miss
class #1.

**ROUND 6 — "KEEP RUNNING UNTIL HAPPY" (flood class + stragglers).** Shipped + live-proven:
- **Match-count ranking** in content_search (migration `content_search_rank_by_term_matches`) —
  rows matching MORE of the ask's terms outrank common-term recency floods ("stopped crying" went
  buried-past-40 → rank 1). THE flood killer.
- **Term variants** in expandTerms: numeric tokens ride separately ("$105K in the first 8 days" also
  tries "105k") + single-letter-word strip ("r d tax credit" → "tax credit"); cap 8→10.
- **Partners→chats cross-ref** broadened (discount|promo|coupon|code triggers) + FB sources added.
- **awardAsk override** — "who won Member of the Month/challenge" forced into content search (router
  had wobbled it into a no-data lane).
- Investigated-and-cleared: fb_member_map page-UIDs are CLEAN (Neven/MDS.co posts map to null — the
  misattribution was prompt conflation, not data); April-MoM data was perfect all along (flood victim).
**Final live batch:** R&D → "Shinghi Detlefsen saved $255,815" verbatim ✓ · $105K → "Abdul Altaf"
+ dashboard numbers FROM THE SCREENSHOT'S OCR ($105,545.75 / 5,182 orders) ✓ · "stopped crying" →
Jon Spektor quoted with date ✓ · April MoM → "Fernando Becattini 🎉" + quote + link ✓ · controls
(Molson/Target, tariffs) held and got richer ✓.

**Still-open (documented, diminishing returns tonight):** $2M-first-time (semantic paraphrase — the
post doesn't literally say it) · SGS-code + Molson-300% (need exec forensics on actual router terms)
· press-piece (semantic) · 429 zero-comment cohort (burner-dependent re-run) · Casey-Vine +
Casey-3-agencies (probable test-key errors) · ONE-session rule enforcement.

**Remaining known misses (~15), by class:**
1. ~~Topic-silent replies~~ **CLOSED by Round 5 (fb_thread)**.
2. No-name generic-phrase asks ("who complained about X%", "$105K in 8 days") — router emits long
   phrases; common-term floods crowd the 40-row window. Levers: rarest-term-first ranking, numeric
   normalization.
3. Route coverage: SGS-code ask went partners-only; "22 and started in college" went profile-only;
   April MoM (winner name lives in the graphic's OCR — investigate why search_extra missed).
4. Probable KEY-WRONG: "Casey's 3-agencies post" (data suggests the Adam Chudy thread).
5. FB member-map quirk: the group page account's comments resolve to Andy — Neven answers
   misattributed (fix the page-UID mapping in fb_member_map).
- ⚠️ Second session detected editing the wf mid-evening (TRUST & CHARACTER + RECORDINGS rules
  appeared — good rules, merged into canon). ONE-session rule needs enforcing.

## Data-layer notes
- 1 true gap in 105: GMA/Tory-Johnson post comments (in the 429 zero-comment cohort — the deferred
  re-run list `~/Downloads/mds_rerun_zero.txt` remains the fix).
- Anonymous posts carry author "Anonymous member/participant" — searchable, fine.
- Official MDS announcements post under author "MDS.co - The Ecom Founders Community" (page account) —
  worth knowing for author-search UX.
