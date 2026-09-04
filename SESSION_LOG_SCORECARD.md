> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Session Log — Scorecard (leaderboard + FB capture/scraper/roster/scoring)

Newest first. **Every session close: prepend the full entry here + ONE index line to `SESSION_LOG.md`.**

---

## 2026-09-04 (pm) — FB #4 CLOSED: the judge reads each text once · Hector is searchable

**Andy's own question was Hector** ("hector" → 0 rows on the admin tab). Go given after #3 closed.

**Measured before touching anything** (`partner_judge_bench.py`, new, read-only; 43 hits over 5 days,
2–3 trials per shape): the old shape — 8 MENTIONS per call, so Anita's post appeared 8 times with only
`(partner: X)` changing — judged 14 of her 16 partners `not_about_partner` in BOTH trials (43/43
identical: wrong, and consistently wrong, not variance). One mention per call: 43 calls, 41/43 stable,
Hector flipped. One text per call with its partners listed: 16/16 neutral, Hector neutral, 43/43 stable,
23 calls. Up to 8 texts per call, each with its partner list: 16/16 neutral, Hector neutral, 42/43
stable, **3 calls**. `temperature` is deprecated for `claude-sonnet-5` — the API rejects it — so it was
never a lever (the first bench run wasted 10 calls learning that).

**Shipped** (`partner_scan.py`, backup `.bak-pregrouped`; 18 unit tests): `group_hits()` /
`chunk_groups()` / `grouped_listing()` / `judge(chunk)`, `TEXTS_PER_CALL = 8`. Then the 14-day dry run
lost two baseline complaints (Sellerboard, Activate Talent); a probe showed Activate Talent 3/3
complaint and Sellerboard 2/3 under the new shape and 1/2 under the old — borderline text, same
variance either way. So **`settle()`**: a verdict that changes a stored row needs a second independent
call to agree, else the stored verdict stands; printed as `🔁 N changed verdicts re-checked`.

**Proof.** `--days 14 --apply`: 73 hits (ticket said ~74), 61 written, 0 removed, 0 unjudged, 1 change
confirmed. SQL: **`Hector Ai · neutral` on `27084374081239403`** (found_at 19:52Z) — searchable on
`/admin/facebook`, no deploy. Anita's post 16/16 neutral. Complaints in the window 8 of 9 kept;
**Sellerboard re-judged neutral by two calls** ("beta… limited… but it's a start. I hate that I pay for
both") — Andy's call, left as the model judged it. Table 129 → 144 (complaint 21 → 20, neutral 87 → 103).

**Andy caught a regression the same hour: "what they said is wrong."** The grouped call made the model
answer with the partner's own NAME as the quote, so the admin tab read `Hector Ai` under "What they
said" — 14 rows, all from my two runs today; the other 130 were fine. First fix (quote must appear in
the text) was not enough: the model then answered with a real but generic line from the top of the post
("Here's a list of their offerings for this Summit!"), which passed the check. **Second fix, and the dry
run is what saved it:** requiring the quote to *name the partner or come from a short text* would have
REPLACED good quotes — TraceFuse's "they were charging for removals they didn't actually cause", an
A2X quote the model had elided with "...", Passport, Brandon Himmel's TikTok opinion. Printed as
«old» → «new» before writing, so I saw it. Final rule (`sane_quote()`, 12 tests): keep a model quote
only when it can be LOCATED in the text (fragments matched word-by-word, so elisions still resolve) and
sits within 300 chars of the mention, or names the partner; never keep a bare name; else use the line
that names the partner, trimmed to 200 chars, markdown stripped. New `--fix-quotes` repairs stored rows
from the text alone — no model call, no re-judging, nothing flaps. **21 corrected; 143 of 144 rows now
carry a real quote** (the 144th is a comment whose whole text is "Scale Insights").

**Found alongside, flagged:** `partners_catalog` has two published "Prosperlytics Consultants" and two
"Riverbend Consulting" rows — Anita's post carries each twice. Olivia stream owns the catalog.

**Docs:** board #4 → CLOSED with the bench table; `FB_PIPELINE.md` judge paragraph; spec + plan in
`docs/superpowers/`. **Next:** read the 16:25 CDT `PARTNERS:` line (first unattended run with reconcile
+ grouped judge); then #1 / #2 wait on Andy (Airtable links, Slack app).

---

## 2026-09-04 — FB #3 CLOSED: partner mentions reconciled, not accumulated · the model was rewriting our ids

**Opened on the handoff note** (#3 first), briefed, verified live (portal `37ddd39`, posts + content_items
both at 2026-09-03 18:26Z, `Facebook_Group_Insights_9-03-2026.xlsx` landed unattended → **ext v1.13
Insights fix is PROVEN**, reactions moved off Aug 31). Andy asked me to confirm the pick with the
"Facebook scraper Chrome extension" session: #3 before #4 because #4's verification needs a re-run you
can trust; #1 and #2 wait on Andy (Airtable links, Slack app). Andy's own question was the Hector search
(screenshot: "hector" → 0 rows of 10) — that is #4, said so, order stays #3 then #4.

**Shipped** (`partner_scan.py`, `load_feed.py` in `~/mds-scorecard-tools`, backups `*.bak-prereconcile`;
spec `docs/superpowers/specs/2026-09-04-fb3-stale-partner-mentions-design.md`, plan beside it):
- `reconcile()` — pure function: a stored row whose text this run re-read is deleted when re-judged
  `not_about_partner` or when the name no longer matches any partner; failed-batch rows, rows missing
  from a good reply, and out-of-catalog partners are never deleted, only counted. 8 unit tests.
- `supa_delete()` — PostgREST DELETE with `return=representation`, so the count is what actually left.
  Comment ids are base64: `=` must be percent-encoded or PostgREST reads it as filter syntax.
- `texts()` pages (was capped at 2,000 posts / 10 comment pages) → `--days 30` is the backfill path.
- Report line placed second-to-last so `auto_import.py`'s last-3-lines capture always logs it.

**The mistake worth keeping.** First proof run: `removed 4 · left 15 unjudged` — Anita's 7 stale praise
rows survived because the model never returned a verdict for them. Probe (Anita's 16 hits, two batches):
the model echoed every id with the `post:` prefix dropped — `post:27084374081239403:655e…` came back as
`27084374081239403:655e…`, **16 of 16 orphaned**, and `judge()` keyed its dict by the echoed id. Numbered
items 1..N per batch and mapped back → 16/16 matched, second run `left 0 unjudged`. Yesterday's "Hector is
judged not_about_partner inside a batch" was partly this: the verdict never landed at all. #4 premise
corrected on the board.

**Proof (AC 4).** Recreated the stale state with `partner_scan.py.bak-praiserule --days 5 --apply`
(Anita: 5 neutral + 7 praise, table 60). New scanner `--days 5 --apply`: removed 8 (7 of them Anita's
praise), Anita **0 praise** with no hand SQL, rows older than 5 days **27 → 27**. Neutral ended 2, not the
AC's 5: with ids fixed the batched judge calls TikTok Shop / Receive / Xorosoft `not_about_partner` on
that post (only Euka + CrediLinq neutral) — #4's variance, left to #4.

**History pass (AC 5).** `--days 30 --apply`: 1,931 texts, 199 hits, wrote 129, removed 2, 0 unjudged.
Table **53 (9 complaint · 38 neutral · 6 praise) → 129 (21 · 87 · 21)** — the scanner was born
2026-08-31 with a 14-day window, so posts Aug 5–17 had never been read: 82 new mentions, 12 new
complaints (Wayward ×2, Walmart ×4, ClickUp ×2, Melio, Sellerise, eCom Triage, Quartile). Andy's admin tab
shows those now. Anita after the pass: 3 neutral, 0 praise. Hector rows: 0.

**Docs.** `FB_PIPELINE.md` new section (reconcile + the id trap + backfill). Board: #3 → CLOSED with AC
checklist, #4 premise note. ClickUp `2531q-100317` pages 7 + 9 are from June and know nothing about the
mentions scanner or the admin tab — repo is canonical; not rewritten this session.

**Next:** #4 (judge variance inside a batch), starting from the corrected baseline; and read the 16:25 CDT
`PARTNERS:` line in `auto_import.log` — the first unattended run with reconcile.

---

## 2026-09-03 (late) — Andy searched "Hector" in Partner mentions, found nothing: THREE bugs in partner_scan.py

Anita Petrov's 31 Aug Summit-offers post names 16 catalog partners. It had recorded **zero** mentions.

1. **ID COLLISION.** `judge()` keys its verdict dict by `id`, and the id was `kind:ref` — so 16 hits on
   one post all shared `post:27084374081239403`. Fifteen verdicts were overwritten by the sixteenth and
   the whole post took one answer. Now `kind:ref:partner_id`.
2. **ONLY THE FULL CATALOG NAME MATCHED.** The catalog says "Hector Ai"; the post says "Hector:".
   The AI suffix is now optional. Deliberately narrow — stripping the other generic suffixes
   (Systems / Media / Solutions / Consultants) leaves ordinary words behind and took 14-day matches
   from 75 to 135, with "Seller" (Seller Systems) hitting 24 times and "First" (First Media) 22.
3. **WHOLE BATCHES SILENTLY DROPPED.** `max_tokens: 2000` could not hold 12 verdicts each carrying a
   200-char quote; the JSON came back cut mid-string, the parse AND its retry failed, and the batch was
   skipped with only a console warning. Two of seven batches died that way on one run. Now
   max_tokens 4000, batch 8, and a skipped batch prints a loud "these mentions are MISSING, not
   absent" line with the count.

**Result:** that post went 0 to 11 mentions; the 14-day scan went 25 to 42.

**ANDY'S CALL (2026-09-03): admin announcements STAY in the scan** — "we might get good comments".
Right: the announcement body is not sentiment, but the COMMENTS under it are. So the fix was the
verdict, not the scope. The prompt now says praise must be a MEMBER's own experience, and a sponsor
thank-you or offer listing ("2 free months", "60% off") is NEUTRAL however warm the wording. Anita's
post went from 11 praise to 5 neutral, and the stale praise rows from the pre-fix runs were deleted.

**Two things still open, both worth a ticket rather than a late-night fix:**
- Hector is FOUND by the prefilter now but the model judges it not_about_partner inside a batch (a
  dedicated call says neutral), so it still does not stick. Model variance on a listing.
- **The scanner never removes a mention it later rejects.** `supa_upsert` only writes; a row judged
  "praise" under an old prompt survives a re-run that would now call it not_about_partner. The table
  only grows, so a prompt change leaves stale verdicts behind — the same class as the classifier's
  "--apply only labels NULLs".

## 2026-09-03 — FB admin tab becomes editable: nested drill-downs, type + answered write to the DB

**Andy, five asks in one go**, all shipped (`12a9de3` + `980d454`):

1. **Numbers inside a panel now drill too, with a breadcrumb.** `FbDetail` is a STACK — a count inside
   a panel pushes another panel, the header shows the trail (`Partner complaints › Dan Wills`), Back
   or a crumb walks out, Escape pops one level, the overlay closes everything.
2. **Mark an unanswered post as answered** — a Handled toggle on every post row, undoable.
3. **Change or remove the Type tag** — value add / give / ask / none, per row.
4. **Where a partner mention came from** — a `Where` column (in a comment / in the post) off `ref_kind`.
   Today: 4 of 5 complaints came from comments.
5. **Give share is back in Members**, as a bar, using the SAME definition as the Gives tile
   ((gives + value adds) / classified) rather than the lifetime view's.

**The write design, and why it is not on `fb_posts`.** New table **`digest.fb_post_overrides`**
(migration `fb_post_overrides_v2`) + `POST /api/admin/fb-post`, gated by the same `@mds.co` session as
the pages. `classify_posts.py` rewrites `fb_posts.post_type` **every night**, so an admin edit stored
there would be silently reverted — the override lives beside it, wins in `digest.fb_report_posts`,
flags the row `type_edited`, and **deleting the row restores the classifier's own answer**. The UI
mirrors what the database returns, never what it hoped for.

**Verified against live, then cleaned up:** answered → `answered_at` set + `unanswered` false; type →
give → `"give"` + `type_edited`; clear → null; unauthenticated POST → **403**. One real click on
production wrote `answered_by: andy@mds.co`, was undone through the UI, and the overrides table is back
to **0 rows**.

**One flaw only clicking could find:** after marking a post answered the row left the unanswered list
while the **Unanswered tile still showed the server's 31** — two truths on one screen. Tiles now recount
from the same rows the tables show (`980d454`).

**Late round — classifier accuracy, then the archive (`a606979` · `83dfdac` · `df7633a`):**

*Accuracy, measured not assumed.* Scored the ask/give classifier against Airtable's 37,636 human
labels on 300 RANDOMLY sampled posts (not the export's head — it is ordered, and its first N is one
slice of history). **94–95% overall**; ask was strong (98–99% recall) and **give was the weak class at
85–91% recall**. One dominant failure: a give phrased as a question. Fixed the prompt in two passes —
the first ("a question mark does not make an ask") over-corrected and started calling real asks gives,
whose failures were themselves one class, so *comparing notes* ("anyone else seeing this? we are up
17%") is now explicitly an ASK. **Held-out validation on a sample I had not tuned against: give recall
85.4% → 91.0%, ask precision 95.0% → 97.4%.**

*Also found by the same scoring:* `tagged_value_add()` matched `#\s*valueadd\b`, so **`#valueadded`,
`#valueadds` and `#valueaddopportunity` never matched** and fell through to the model as gives. Now
`\w*`; 5 archive posts corrected.

*The archive.* `classify_posts.py --apply` only labels posts whose type IS NULL, so a corrected rule
never reaches history — wrote **`relabel_archive.py`** and ran it over all 4,190 posts with text.
**ask 2,683 → 2,619 · give 1,310 → 1,374 (+64) · value_add 197 → 197 · unclassified 0.** 64 gives had
been filed as asks. Portal reflects it with no deploy (it reads Supabase per request): 7-day view moved
33/16 → 32/17, give share 35% → 37%.

*Three more fixes from Andy's eye:*
- **Give share sorted as TEXT** — descending gave 67, 25, 100 because "6" > "2" > "1". `percent` now
  sorts numerically (`a606979`).
- **"check your math"** — the arithmetic was right (all 254 member rows add up; a value add IS a give,
  so 1 VA + 6 gives = 7/7 = 100%), but **58 members read 100% and 43 of them had posted ONCE**, so
  sorting put single-post members above consistent givers. A share now needs **3 classified posts**;
  below that a dash that explains itself (`83dfdac`).
- **A saved edit looked like a no-op** — the route returned `null` when its read-back came back empty
  and the client read that as "not answered", so Andy's mark on Brandon Himmel's post rendered as
  nothing while the database had it (`answered_by: andy@mds.co`, and a reload showed it gone from
  Unanswered 11→10). Route echoes what it wrote; client falls back to what it asked for (`df7633a`).
  **Verified at the API, not by clicking** — the automation swallows the first click and the confirm
  dialog blocks the second.

*Known and inherent:* the unanswered list is only as fresh as the last comment pass. Andy hit a post
carrying FB comments that arrived after our 21:45 check. 12 flagged unanswered, 11 checked inside 24h.

**Polish round (`d2437c0`), five from Andy — two were my own bugs:**
- **Escape stopped closing the panel.** I had it call `onBack(stack.length - 1)`, which slices the
  stack down to the panel it was meant to dismiss. It is `- 2`: pop the top, and at depth 1 that closes.
- **"Michael Pryor › Michael Pryor › Michael Pryor"** — drilling a member from inside that member's own
  panel pushed an identical level. A drill onto the subject already on top now REPLACES it.
- **Give-share bars now line up** — the number is fixed-width; "0%" vs "100%" was shifting each bar.
- **Unanswered has its own type filter** (All 31 · Value adds 2 · Gives 18 · Asks 11), separate state
  from the All-posts facet.
- **Mark-answered confirms first**, naming what actually happens. Andy asked for "permanently removes
  from the report"; it is reversible, so the copy says the truth instead — leaves Unanswered here AND
  the daily Slack card, stays in All posts where the same button undoes it.

**The Slack card had to change with it (`daily_digest.py`, backup `.bak-preoverrides`):**
`silent_posts()` read `fb_posts` + a comment lookup and knew nothing about admin edits, so a post
handled in the portal would keep being nagged about. It now reads **`digest.fb_report_posts` with
`unanswered=is.true`**, which already encodes both rules (only CHECKED posts count; an admin mark ends
it). Proven: marked one of the seven silent posts answered → dry-run card went **7 → 6** and that post
disappeared; test row deleted, overrides back to 0.

**SPINE CHECK (Andy asked for confirmation):**
- **Partners: 100%.** All 27 mentions carry `partner_id` and every one resolves in `partners_catalog`.
- **Members: 87% of posts, 91% of people.** 246/284 posts and 135/148 authors resolve to an
  `at_member_id` via `fb_member_map`. Of the 13 unmapped: the group page account and one "Anonymous
  member" are correct; **eleven are real people missing a FB Profile Link on their member record** —
  **Dan Wills (13 posts)** and **Ivan Ong (9)** are the ones worth fixing, then Mouad Errafik (3) and
  eight singles. Airtable is Andy's to change, never ours.

**Also today:** the Slack digest header now carries `<https://digest.mds.co/admin/facebook|full report>`
— test card posted to #automation-tests (ts 1788403774.701589) and read back to confirm it renders.

---

## 2026-09-02 (night) — Insights export: the ten-day "click it yourself" was a LOGIC bug, not a Chrome one (ext v1.13)

**Andy:** "if data was updated, why i need to click this? you need to resolve the logic." Correct — a
standing manual step is the bug.

**Root cause, from evidence not theory.** Today's run stored its own verdict in extension storage:
`{"insights":"FAILED (no file landed)","roster":"ran","harvest":"22 posts, stalled","comments":"ran"}`
— i.e. the click flow returned **ok** and no file existed. Reading the code:
`clickInsightsDownload()` clicks FB's Download button and returns `{ok:true}` **immediately**;
`captureInsights()` returns; the chain then calls `autoFeedCapture(myGen, tabId)` → `chainTab()` →
`chrome.tabs.update(tabId, {url: feed})` — **navigating the very tab that just submitted the export**,
seconds later, which cancels FB's server round-trip. A manual click always worked because a human
leaves the page alone. That is the whole ten days.

Note what it was NOT: not worker eviction (the v1.07 keepalive was already running), not the retry
(v1.01), not FB moving the control (v0.98-era bug, already fixed) — those were the earlier failures on
this same step, which is why the wrong diagnosis was easy to reach for.

**Fix (v1.13, `background.js`):** the step's contract is now **"a file landed"**, not "I clicked".
After submit it HOLDS the Insights tab and waits on `chrome.downloads.onCreated` + a 3s
`downloads.search` poll for up to 150s; only then does it report success and let the chain navigate on.
A timeout is named precisely (`"submitted, but no .xlsx started within 150s"`) and retried. The file
matcher accepts any Facebook-sourced `.xlsx` as well as the known name, so a rename cannot silently
reopen this.

**Unverified until it runs:** an unpacked extension keeps the code Chrome loaded, so v1.13 needs a
reload (or a Chrome restart) before tomorrow's 4:25pm run tests it. Andy chose to wait for the auto run
rather than force one tonight. Proof to look for: a new `Facebook_Group_Insights_*.xlsx` in ~/Downloads
and `digest.fb_posts.reactions` moving off its Aug 31 stamp.

**Today's data (for the record):** everything except Insights flowed — 52 posts / 230 comments / reach
on 15 / 3 images OCR'd / 1,000 classified / 8 partner mentions incl. a new complaint (Linnworks —
Molson Hart) / Slack digest sent. Live tab reads 284 posts · 148 members · 176 asks · 94 gives ·
32 unanswered · 5 complaints.

---

### Round four — a number opens its rows (Andy: "like it was on local")

The drill-downs from round two only NARROWED the page; the local `fb_report.py` page opened the data
behind a number. Rebuilt to match, in `d465e8b`:

- **New `FbDetail` panel** — a modal that reuses `FbTable`, so the rows inside it sort, filter and
  paginate like everything else. Escape or the overlay closes it; the page behind is scroll-locked.
- **Every KPI tile** opens what it counted: Posts · Posting members · Value adds · Unanswered ·
  Asks · Gives · Partner complaints · **Avg reach** (the posts the average is computed from).
- **Every count in the Members table**, including *Comments received* (their posts, busiest first)
  and *Avg reach* (their posts that have one).
- **Both hashtag counts** — its posts, and the members who used it.
- **A name** (member or partner) opens their detail with a **"Filter the page to X"** button, so the
  chip behaviour from round two is still one click away rather than the only option.

Verified locally in Chrome before shipping: the complaints tile opened the 4 complaints with quotes,
and `Dan Wills · asks` opened his 13 asks with comments and reach.

### Round three — a phantom bug, four deploys, and the one lesson worth keeping

Andy's "why nothing is clickable" had a boring, correct answer (round one had no drill-downs —
fixed in `acf1513`). I kept going anyway and manufactured a bug that never existed.

**The chain of wrong turns:**
1. Counted `__reactFiber$` keys + `window.__next_f` entries, saw ~60 elements, concluded **streamed
   content never hydrates on a hard load**. That probe reports the SAME number on a page that works
   and one that does not — it measures nothing. Told Andy, told the peer session, filed a task,
   shipped `8ce9fdb` (dropped the Suspense boundary).
2. Clicked properly, saw it work, saw **Overview work too** → withdrew the task, corrected the peer,
   reverted (`ddfe63b`).
3. Saw a click 5s into a cold load get lost on the streamed build and land on the non-streamed one,
   called it a **real early-click defect**, shipped `387854f`.
4. Then the same loss appeared on the NON-streamed build at 5s, 10s and 22s — and a second click
   always worked. **The automation tool swallows its own FIRST click while the tab takes focus.**
   No hydration bug, no streaming bug, no early-click defect, on any build. Restored streaming
   (`ae503c3`), which is where the code started.

**Net:** four deploys that changed nothing a user can see, one withdrawn task, two corrections to a
peer, three rewrites of this log entry.

**Lessons:**
1. **A proxy that reads the same for working and broken code is not evidence.** Click the thing.
2. **Then distrust the click too.** An automated first click after a page load can be eaten by focus
   — click twice before declaring a control dead. Repeat the failure on the OTHER build before
   believing the difference is real: one trial per build is a coin flip, not a comparison.
3. **The boring explanation was right the whole time.** When the user says "nothing is clickable"
   and the page has no click targets, that is the bug.

### Same session, second round — Andy: "why nothing is clickable?"

Fair hit: round one shipped a REPORT, not a tool. Fixed in `acf1513`:
- **Every KPI tile opens the rows behind its number** (Partner complaints lands on the mentions
  table already filtered to complaints).
- **A member name focuses that member across every section**; **a count in the Members table opens
  exactly the posts it counted** (Dan Wills' "13" under Asks → his 13 asks); a hashtag opens its
  posts; a partner name opens their mentions. Active filters render as chips, each clearable.
- **Facet chips with live counts** — mentions by complaint/praise/neutral, posts by
  value add / give / ask / unclassified. (The counts are computed BEFORE the verdict filter, so a
  chip never reads zero once you use it.)
- **"Today" removed** from this tab's picker (the group is captured once a day, so it is always
  empty); `?period=today` lands on Yesterday. `PeriodPicker` gained an optional `exclude`, so no
  other tab changed.

**Two traps, both worth remembering:**
1. **A predicate closed over component state read STALE.** `matchesMember` as an in-component
   closure meant the React Compiler memoized the derived lists and never saw the focused member
   change — a click scrolled but filtered nothing. Fix: the scoping logic is now
   `src/lib/admin/fb-filter.ts`, **pure functions over plain arguments, 16 tests**.
2. **Smooth scrolling is a no-op in some embedded browsers** — the drill did nothing visible.
   Scrolling is instant now, and deferred one double-rAF past the commit (a scroll started in the
   same tick as the state change gets cancelled by the re-render).

**Verification note (honest):** the Browser pane **cannot hydrate streamed Next content** — the
EXISTING production Overview page fails identically there (`S:0` container, zero react keys), so
this is the pane, not the app ([[reference_preview_pane_no_hydration]]). On the one pane instance
that DID hydrate, tiles / facet chips / member drill / count drill / partner drill were all clicked
and confirmed live. Everything since is covered by the 16 pure tests (302 total green) + `next build`.

## 2026-09-02 (evening) — FB report PROMOTED into the admin dashboard: `/admin/facebook`, live from Supabase

**Andy:** "that's what i meant to add it here" (screenshot of `digest.mds.co/admin`). The local
`fb_report.py` page was only ever a file on one laptop — the ask was to make it a tab in the admin
alongside Overview / Channels / Members / Member 360 / Olivia / Tools.

**Shipped — mds-digest-web `6653c44`** (branch `fb-admin-tab-20260902`, built in worktree
`.worktrees/fb-admin`):
- `src/app/admin/facebook/page.tsx` — server component, `force-dynamic`, read live on every request.
- `src/lib/admin/fb-report.ts` — the loader: range-scoped posts, partner mentions, weekly trend,
  KPIs **and their prior-period deltas** (the local page never had deltas).
- `src/components/admin/FbTable.tsx` — one generic table for all six sections: click-to-sort,
  filter box, 20 rows + "show all N". Column configs are PLAIN DATA (no render callbacks) so a
  server component can pass them across the client boundary.
- `AdminNav.tsx` — one line, tab sits between Member 360 and Olivia.
- Reuses the admin's own `PeriodPicker` / `ComparisonStat` / `periods.ts` rather than a bespoke
  date range, so this tab behaves exactly like every other one.

**DB — migration `fb_report_posts_view`:** new `digest.fb_report_posts` (post + its comment count,
`unanswered` = checked AND zero comments, so a never-checked post is still never called unanswered).
Hashtags and the member mix are derived PER PERIOD in the loader instead of read from the lifetime
`fb_report_hashtags` / `_member_mix` views — otherwise the tables would answer a different question
than the period picker asks. `db/` re-exported (`e70f0b4`), which also captured drift the export had
never held: the four earlier `fb_report_*` views and scorecard-fb's live `fb_group_posts` changes.

**Verified (last 30 days, live):** 268 posts · 144 posting members · 14 value adds · 164 asks ·
90 gives · 27 unanswered · 4 partner complaints · avg reach 182 — the same numbers from the loader
directly AND rendered in the KPI cards of an authenticated `GET /admin/facebook?period=30d` (200,
414KB, 74 posts linked back to Facebook). Unauthenticated GET → **307 to `/`**, so the member content
sits behind the existing `@mds.co` gate. `tsc` clean, **278 tests pass**, `next build` green.
Local QA session used the app's own dev-only `/api/test-login` (404s in production) with a neutral
`qa-fbtab@mds.co` staff identity — no Airtable write, and never Andy's identity.

**Not verified:** the click behaviour of sort/filter and the light-theme rendering — the sandbox
blocked driving a logged-in browser, and I did not route around it. Andy sees both on the live tab.

**Two-agent note:** switching the SHARED checkout to my branch disturbed scorecard-fb mid-edit (their
two `fbstory` files landed on my branch as working-tree changes; they rescued them). Fix adopted:
**both sessions now work in `.worktrees/`, and the shared checkout stays on `main`.** Worth making the
house rule.

**Open, unchanged:** the FB Insights xlsx export is still stale since **Aug 23** — every unattended
retry has failed, but every one of those failures predates the retry-with-reload (v1.01) and the MV3
keepalive (v1.07). Tonight's 4:25pm CT run is the first real test on v1.12; if it fails, v1.06+ now
records the failing step.

---

## 2026-08-22 (night) — POST REACH shipped end-to-end (ext v0.93→v0.98 + `fb_posts.reach`). Four wrong theories, one anchor-free reader, validated against the FB UI.

**Andy:** "reach is not views. its reach." Correct — `views` is the Insights Top-posts number (top-99
of 28 days); **reach** is the per-post figure an admin sees in-feed, available for EVERY post.

**The hunt (each step killed a theory, in order):**
1. v0.91 probe scanned 400 buffered GraphQL responses for `*reach*`/`impression*count` → **`{}`**.
   Reach is not in the payload at all; it is rendered text. Probe deleted, DOM reader written.
2. v0.93 read the label at SAVE time → 3 of 10. FB virtualizes the feed; scrolled-past posts are gone
   from the DOM by then. → v0.94 accumulates every loop pass (6 of 10) + v0.95 on scroll, debounced.
3. Still 6 of 10, **the same six**. My "climb capped at 12 parents fails on long posts" theory → v0.96
   rewrote traversal anchor-first, 30 levels, with a wrong-post guard. **Identical 6.** Theory dead.
4. Andy's screenshot settled it: Daniel Meredith's post plainly showed **139 post reach** — and its
   header timestamp is **not a link**. **FB renders no permalink anchor for recent feed posts** (same
   behavior that killed the old feed loop in July), so anchor-first could never see those 4.

**Shipped:** **v0.98 anchor-free reader** — match the label, climb ≤30 levels, identify the story by the
**first 60 chars of the body text** the harvester already banked from GraphQL (anchor used only when FB
provides one; assignment refused when a container matches >1 post). `reachDiag` per post
(`ok` / `rendered-no-label` / `not-rendered`) so this is never guesswork again.
**DB:** migration `fb_posts_reach_column` (+ comment recording the 139 validation);
`load_manual_meta.load_reach()` folds the capture's map in **max-wins**, already inside the daily chain
via the autopilot's META step — no extra wiring.

**Proven live:** 12 of 16 posts read, all `ok`; the other 4 `not-rendered` (Andy stopped scrolling).
**Daniel Meredith = 139, exactly the FB UI.** Max-wins visible across runs (216→219, 275→279).
Backfilled from tonight's 4 captures: **12 posts now carry reach — every one of them with `views IS NULL`**
(none had ever made a Top-posts sheet): Alex Mills 414 · Jonathan Jesper 279 · Ivan Ong 273 · Duncan
Brown 272 · Ben Pearson #valueadd 263 · Norm Lanier 250 · Ben Anderson 219 · Daniel Meredith 139 ·
Keith Mander 88 · Zaid 61 · Rich Tesoriero 38 · Michael Patrón 35.

**Also this session:** harvest stall fixed (v0.93: quit at 1 post — floor step 4, 3 flat steps, settle
0.9s→1.8s, cap 9→14); reach passed through the *recovered* payload (v0.95, it was being dropped);
two files per Stop confirmed BY DESIGN (page final save + worker safety net, autopilot takes newest).
**Chrome does not hot-reload unpacked extensions** — the 16:25 scheduled run used the stale 0.92 worker
because the last reload predated v0.93 by 16 minutes; the popup version badge is the reliable tell.

**Data health checked (Andy asked):** newest post Aug 22 15:14, newest comment Aug 22 21:12,
`content_items` matches both exactly, every one of the last 12 days has posts+comments+searchable with
**zero** blank days, **0** unembedded rows over the 30-char floor.

**Next:** tomorrow's scheduled run is the first with the whole stack live (harvest fix + reach) — check
reach coverage across a full auto-harvest. Airtable ASK/GIVE labelling still awaiting Andy's go.

---

## 2026-08-22 (early) — reach is NOT in the GraphQL (probe answered it), and the auto-harvest was stalling at 1 post. Both fixed in v0.93, unproven until tomorrow's run.

**Two runs today (Andy stopped there — enough FB signal for one day).** Run 2 produced the evidence:

**1. Reach — probe came back EMPTY.** v0.91's `reachProbe` scanned up to 400 buffered GraphQL responses
for any `*reach*` / `impression*count` key and returned `{}`. So the per-post "N post reach" an admin
sees is **rendered text, not data in the payload we capture** — the whole v0.91 approach was wrong.
**v0.93 reads the DOM instead** (`readReach()` inside `manualCaptureMain`): match the `N post reach`
label, climb ≤12 levels to the story container, take the post id from its `/posts/<id>` anchor, handle
K/M suffixes. Read-only, no clicks; a miss just leaves that post without a number. Payload now ships
`reach: {postId: n}` instead of `reachProbe`. **Still unproven — first real map arrives tomorrow.**
Reminder of why this matters: Insights `views` only covers the top-99 of a 28-day window, DOM reach
covers every post we scroll past.

**2. Auto-harvest stalled at 1 post** (run 2 status: `insights + feed (1 posts, stalled) + comments`).
Root cause: the stall rule stopped after **2** consecutive flat steps, but FB paginates the chronological
feed slower than the driver scrolls, so early flat reads are NORMAL. Fixed: never judge before step 4,
require **3** flat steps, never stall while holding <3 posts, in-page settle 900ms → **1800ms**, cap
9 → **14** steps, and `shelled` now needs 6 steps at zero (was 3 steps at ≤2). The 48h window-edge is
the intended exit again. Yesterday's 4-post harvest was the same bug, milder.

**Also today:** the hollow-post outage (see entry above) — ext v0.92 reloaded and live.

**Next session:** Andy reloads to v0.93 **before** the scheduled fire (the alarm runs whatever worker is
loaded — v0.92 would repeat the thin harvest and ship no reach). Then: confirm harvest depth ≈ the day's
real post count, read the `reach` map, and wire a `reach` column if it looks sane. Airtable ASK/GIVE
labelling (3,824 posts joinable by post_id) still awaiting Andy's go — no Supabase writes made.

---

## 2026-08-21 (late) — OUTAGE: one hollow post killed the whole daily chain. Root-caused, fixed in 3 layers, day recovered.

**Symptom:** 3x Slack warning "FB feed load FAILED for `mds_feed (30).json`" on the scheduled run.

**Root cause (not what the card implied):** the comment pass visited post `26939910595685753` and FB
served an **empty shell** - id only, no text/author/`created_time`, zero comments. That post was NOT
junk: it is **Alice Jennifer's Aug-19 TikTok Shop post**, already linked in `content_items`. Two failures
compounded:
1. `load_feed.py`'s upsert sends every key, so the shell's nulls **overwrote the real row** (body+time+author gone).
2. `fb_link_content()` then tried to insert it into `content_items` -> `occurred_at NOT NULL` (23502) ->
   PostgREST 400 -> loader `rc=1` -> **images, OCR, link cards, embeddings and the silent-post card never
   ran**. Posts/comments themselves had already landed (40 posts, 220 comments), which is why only the
   tail of the chain was missing.

**Fixed (3 layers, defense in depth):**
- **ext v0.92** - `runUrlPass` never banks a post with no text AND no comments AND no time.
- **`load_feed.py`** - skips any post with no `created_time` (prints `skipped N hollow`), and now
  **omits empty `text`/`author_name`/`author_uid` keys** so a thin re-capture cannot blank stored values
  (rows grouped by key-set for PostgREST, PGRST102).
- **`digest.fb_link_content()`** (migration `fb_link_content_skip_timeless_posts`, re-exported, EXECUTE
  re-granted to service_role + revoked from PUBLIC/anon per [[reference_drop_function_revokes_acl]])
  - skips posts/comments with `created_time is null`: one bad row now costs one post, not the day.

**Recovery (all verified live):** Alice Jennifer's row **restored from `content_items`** (body,
`occurred_at`, author_name; uid re-derived via `fb_member_map`) - deletion was refused by my own guard
because the linked row existed, which is what surfaced the truth. Re-ran the day: feed 39 posts/220
comments + `skipped 1 hollow`, linker 4 posts/79 comments, images 0 new (none in this capture),
link-previews clean, **144 rows embedded**, silent-post card fired (1 post, Slack ts 1787374587.810419).
Audit: `created_time is null` rows = **0**; the other 17 empty-text posts checked against `content_items`
- genuinely image-only, **not** overwrite victims (0 recoverable), so Alice's was the only casualty.

**Committed:** `db/functions/fb_link_content.sql` re-export. SOP: new "hollow-post trap" section in
`/Users/Born/mds-scorecard-tools/FB_PIPELINE.md` with the restore-from-content_items recipe.

**Next:** reload the extension to pick up v0.92 (guard is only in the file until then).

---

## 2026-08-19 — FULL AUTOPILOT SHIPPED (ext v0.87→v0.90): one-button/scheduled daily chain — insights + humanized auto-scroll + comment pass; roster demoted to weekly

**Andy's ask:** "full autopilot option. auto scroll, auto capture comments, process images, everything."

**Shipped (extension, `.bak-v085` kept · autopilot scripts):**
- **v0.87:** `autoFeedCapture` (auto feed harvest reusing the untouched passive `manualCaptureMain`) +
  scheduled chain roster→insights→feed→comments; `commentsForManual` seeds = tab localStorage **∪
  seed_ids.json**, newest-first, **CAP 40/run**; `load_manual_meta.write_seed` now writes **ALL DB posts
  <7d** (not just the capture's) — this is how 3-6d-old posts keep getting comment checks daily, which
  is what keeps the silent-post card honest across its whole 7d window; `auto_import.newest()` variadic
  (auto harvest saves `mds_manual_capture.json`, human Recover saves `_recovered`); popup "Run full
  capture now".
- **v0.88 (bugfix, from the worker's own persisted status in Chrome's LevelDB):** phase 3 died on
  `No tab with id` — it queried for any group tab and grabbed one that closed mid-settle. Chain now
  CREATES AND OWNS ONE TAB end-to-end (`chainTab()`), every phase navigates it (members→insights→feed);
  phase toasts 1/4…4/4 (Andy: "no clue what stage I'm in").
- **v0.89 (bugfix):** roster gate read a storage stamp only v0.88 writes → re-ran a roster captured 3h
  earlier. Gate now reads **Chrome's download history** (`downloads.search` for `mds_roster_full`),
  stamp = fallback. **Roster runs at most every 7d** (Andy: deep members scroll = bad FB signal; a
  joiner only surfaces via weekly reconcile anyway, so mapping lag ≤7d is the accepted cost).
- **v0.90 (Andy watched the scroll):** humanized + worker-side stepper — depth mix 60% normal
  700-1700px / 15% shallow / 15% deep / 10% BACK-UP scroll; pauses 2.2-5.5s + 15% "reading" 6-12s;
  ≤9 steps; stops on window-edge (oldest >48h) / 2-step stall / shelled (≤2 posts after 3 steps →
  abort + toast, comment pass skipped) / Stop. Loop lives in the WORKER (one `feedScrollStep` injection
  per step — a single long in-page script risks the MV3 30s idle reaper); per-step status line.

**Proven live (one button, v0.89 driver):** roster skipped ✓ → insights 15:09 (99 top posts → TOPPOSTS
21 updated) → harvest 16 posts / 8 image URLs, stopped at 48h edge ✓ → comment pass **40/40 seeded,
166 comments** (by day 19th:11 · 18th:11 · 17th:10 · 16th:3 · 15th:5 — the 3-6d tail is the DB-seed
refresh working; every Aug-19 post came from the harvest = new-post discovery works with zero human
scroll) → autopilot 15:48: 4 images OCR'd, 1 link card, 215 embedded, seed → 61 posts, **SILENT card
5 posts (was 7 — two got comments and correctly dropped off)**, Slack ts 1787172567.001709.

**Traps for next time:** worker status lines are readable from
`~/Library/.../Local Extension Settings/<ext-id>/*.log` via `strings` — that's how the No-tab-with-id
root cause was found without touching the user's Chrome. Comment-pass cap 40 starves the oldest tail
if a week ever holds >40 posts — raise cap or rotate if a card ever looks stale.

**Next:** tomorrow's scheduled fire = first true zero-touch day on v0.90 (humanized scroll's first live run).

---

## 2026-08-18 (later) — Extension v0.86: dead feed-loop removed, scheduler now DAILY + self-healing, drifted copy fixed

**Andy's ask:** review the popup — descriptions drifting, unneeded features, check the scheduler.

**Review verdicts:** button 3 "Capture Conversations" was the dead automated feed loop (every
`mds_feed*.json` since Aug 7 says `_diag.source: manual-seeded-url-pass` — the 4+4c workflow); 5 copy
drifts (Mon/Thu cadence ×2, "last 4 days" on a 6-day button, footer's "run process_fb.py"); scheduler
had a real trap — **Chrome clears alarms on every extension update/reload but the toggle kept reading
`scheduled: true` from storage, so it showed armed while dead** — and was weekly-only against daily runs.

**Shipped (v0.85 → v0.86, `mds-scorecard-tools/extension/`, no git — `.bak-v085` copies kept):**
- **Deleted** `captureFeedMain` + `captureConversations` + their 3 message routes (~43KB, 120KB→77KB);
  popup button 3 removed, buttons renumbered 4/4b/4c/5 → 3/3b/3c/4. The 4c/URL-pass path they shared
  (`capturePostMain`, cap_inject) is untouched.
- **Scheduler: weekly → DAILY** (`scheduleDaily`, alarm `dailyCapture`, time-only picker) and
  **re-armed from storage on every worker start** (`rearmSchedule` on onInstalled/onStartup/load — fixes
  the silent-death trap; also clears the pre-0.86 `weeklyCapture` ghost). Still roster + insights only.
- Copy fixes: 4c label now "Get comments (last 6 days)" (it always ran days=6), footer now says the
  autopilot ingests files, CONV_DAYS comment de-Mon/Thu'd.

**Verified:** `node --check` green on background.js + popup.js · manifest JSON valid @ 0.86 · every
popup.js id ↔ popup.html id cross-checked (zero orphans both directions) · zero remaining refs to the
deleted functions (only the two intentional `weeklyCapture` clears). **Not yet live: Andy must reload
the extension** (chrome://extensions → ↻); the daily toggle is OFF by default, flip + pick a time to arm.

---

## 2026-08-18 — FB capture: per-post hashtags + REAL reactions/views, and a silent-post Slack card

**Andy's asks:** (1) store hashtags per post so we can query "first / total / most-engaged #valueadd",
(2) fire a Slack card for posts still at zero comments 24h+ after posting.

**Shipped (all in `mds-scorecard-tools`, no git — plus the Scorecard `db/` export, commit `8e94a99`):**
- **`digest.fb_posts` + `hashtags text[]` (GIN), `reactions int`, `views int`.** Tags are derived from
  post text in the loaders (`load_feed.hashtags()`), not taken from the capture's own array, so
  manual-only posts get them and the backfill used the identical rule. Backfilled all **4,058** posts
  (**313** carry tags).
- **`load_manual_meta.py`** (new): folds the manual scroll capture into `fb_posts` — inserts posts the
  feed pass never saw (it only opens posts that HAVE comments) and refreshes text/hashtags only when
  the manual text is longer.
- **`load_insights_posts.py`** (new): reads the Insights export's **"Top posts (last 28 days)"** sheet
  (99-100 rows of FB's own Comments/Reactions/Views + post link) into `reactions`/`views`, max-wins.
  Backfilled 23 exports → **319 posts** with true counts, max **142**.
- **`no_comment_alert.py`** (new): >24h old, within 7 days, zero comments → ONE Slack card to
  `#automation-tests`; silent when there are none; re-lists a still-empty post each run (Andy's rule).
- **`auto_import.py`** wired: `META` (manual meta) before the image chain, `SILENT` (the card) at the
  end of `process_feed()`, `TOPPOSTS` after a successful xlsx import.

**The catch worth remembering:** the extension DOES capture a post reaction count
(`feedback.reactors.count` off the Story) and it is **wrong** — 0 on a post with 9 comments, while the
same export's Daily-numbers sheet shows ~72 reactions/day group-wide. Loading it was reverted; the
Insights Top-posts sheet is the authority. `reactions IS NULL` = "never made a Top-posts sheet" (low
engagement), NOT zero. The extension itself needed **no change** for either feature.

**Verified (live):** top `#valueadd` post = Jasim Eisa, **110 reactions / 581 views / 15 comments**
(Jun 30). Slack card posted to `#automation-tests`, ts **1787110600.332079**, 10 silent posts listed
(Keith Mander 6d 12h … Kevin Tao 2d 7h) — read back from the channel, renders correctly.
`auto_import.py --dry-run` clean. SOP updated: `/Users/Born/mds-scorecard-tools/FB_PIPELINE.md`.

**Next:** first unattended daily run is the real proof of the wiring (the card fired here by hand).

---

## 2026-08-11 — #61 FB conversation+image leg WIRED into the autopilot (was hand-run, stalled 4 days). Image content now searchable by Olivia. Committed + documented.

**Root cause (#61):** `auto_import.py` (launchd `com.mds.scorecard.autoimport`, WatchPaths `~/Downloads`)
only ran **Leg A** (scorecard Insights xlsx). **Leg B** — `load_feed.py` → `fb_posts`/`fb_comments` →
`content_items` → embed, plus the whole **image chain** — was never wired in and was run by hand, so it
silently stalled after Aug 7 while the leaderboard kept updating. The `content_items` linker was
raw SQL typed each run; the day it got skipped, the search layer lagged the raw tables.

**Fix (shipped):**
- `process_feed()` added to `auto_import.py` (call site line 194, after the lock). Runs the FULL leg on
  every fire: `load_feed.py` → `download_images.py <manual>` → `upload_images.py` → `vision_decode.py`
  → re-call `fb_link_content()` → `embed_backfill.py`. Idempotent + state-guarded (`last_feed`).
- The linker is now a **DB function** `digest.fb_link_content()` (in git), extended this session to do
  three things in one idempotent call: link posts/comments into `content_items`, stamp `storage_path`
  on uploaded images, and **fold each image's Claude-vision description+OCR into the parent post's
  `search_extra`** (nulling its embedding so `embed_backfill` re-vectorizes). `search_tsv` is a
  generated col over `tl_dr||body||search_extra`, and `embed_backfill.py:68` embeds `search_extra`
  too — so image text is live on BOTH the keyword and vector paths.
- One-time catch-up run: 12 new + ~718 historical image-posts downloaded, transcribed, folded in,
  **1,050 rows re-embedded**.

**Verified (live):**
- Olivia's real RPC `content_search_v2(p_terms => ARRAY['TACOS'])` returned posts `25507096442300516`
  and `26213128778363942` — both have "TACOS" **only in the image** (a PPC-spreadsheet column header),
  confirmed `body_has_tacos=false` / `image_has_tacos=true`. So a member asking about TACOS surfaces
  posts where the word exists only inside a screenshot. (First probe "QSBS" was discarded — that term
  was also in the post body; systematic check caught it.)
- Autopilot armed: `launchctl list` shows `com.mds.scorecard.autoimport` (last exit 0); plist runs
  `auto_import.py`, WatchPaths `/Users/Born/Downloads`. `auto_import.py --dry-run` reaches `process_feed`.

**Committed:** `5fff683` (Scorecard `db/functions/fb_link_content.sql` + `db/grants.sql`, re-exported via
`db_export_schema.py`). SOP rewritten: `/Users/Born/mds-scorecard-tools/FB_PIPELINE.md` (images now automated).
`auto_import.py`, `load_feed.py`, the image scripts, FB_PIPELINE.md all live in `mds-scorecard-tools`
(**NO git** — not committable). **Next:** first unattended Thursday run is the real proof; Andy just
drops `mds_feed*.json` + `mds_manual_recovered*.json` in Downloads (capture stays the manual Chrome step).

---

## 2026-07-27 (LATE NIGHT) — INCIDENT: 745 duplicate FB-Engagement rows → 200-ghost card. Cleaned, guarded, corrected card posted.

**Andy's report:** weekly-review Slack card listed **200 "ghosts"** incl. obvious members (Fabio HD,
Michael Patrón) — suspected the capture pipeline.

**Root cause (traced via record createdTime, then found documented in reconcile.py):** during the
afternoon reconcile, **one failed page-1 Airtable read returned `{}` silently** → `existing_uids`
empty → all 745 roster people "looked new" → **745 duplicate rows inserted**. The 184 copies the
automation couldn't re-link became the fake ghosts. **Not the capture** (roster file was full, 745)
and not the Supabase pipeline (never writes AT); a bad READ became a mass WRITE.

**Guards** (added 22:18 by the parallel session, verified): `at()` raises instead of returning
nothing; reconcile ABORTS + Slack-alerts if it reads back <500 existing ids.

**Cleanup (this session, Andy's explicit go):** deleted exactly **737** rows that were (a) created
2026-07-27 AND (b) uid already on an older row AND (c) **carrying zero real data** (field-level check:
no scores/engagement/anything beyond uid+name+url — 0 rows skipped, i.e. every copy was a pure clone).
Originals with links/scores untouched; **8 genuinely-new joiners kept** (Kevin Zhen, Dan Wills, Jared
Zientz, ...). **Full pre-delete backup: `mds-scorecard-tools/at_dedup_backup_20260727.json`.**
**After: 781 rows · 0 duplicate uids · 33 unlinked (normal).** Re-ran `reconcile.py --apply` under the
new guard: spine +0, FB rows +0, corrected card posted to C0AQ8USNQK0.

**Watch-out:** scores were written BEFORE the duplication (process_fb runs before reconcile in
auto_import), which is why the copies were empty — that ordering is what made surgical cleanup safe.

---

---

## 2026-07-27 (PM) — FB capture: feed loop broken by FB, replaced with manual-seeded URL pass

**Context:** Monday FB capture. Roster + Insights ran fine; **Capture Conversations opened 0 posts.**

**Root cause (proved from artifacts, not guesswork).** Facebook **stopped rendering `<a href="/posts/...">`
permalink anchors for recent feed posts.** The feed loop opens posts by clicking those anchors, so opens
went to 0. Worse, the post list itself grows mainly *by opening posts* (each open fires more GraphQL) —
so with 0 opens the list collapsed. Proof: `mds_feed (17).json` (Jul 23) = **banked 39, opened 39**;
today the same code path banked 12–13 and opened 0. The 34 anchors still in the DOM all pointed at
49–60-day-old pinned posts.

**What shipped — ext v0.82** (`/Users/Born/mds-scorecard-tools/extension/`)
- **URL pass** (`runUrlPass`): visits each post permalink in the BACKGROUND worker (survives navigation,
  unlike the page-side loop) and reads comments via the existing `capturePostMain`. Guards: verifies the
  URL still holds the post id after load, rejects wrong-post/empty/dup, reports skip counts.
- **`commentsForManual`** — seeds that pass from the **manual capture** (Andy's own scrolling; 1,700+
  posts, every postId + date). Manual = good enumerator/no comments; URL pass = good comments/needs a
  list. Joining them is the fix.
- `captureThisPost` — single-post capture for the current tab (zero automation).
- Feed-loop repairs kept: `skipIds` split from `processed`, `pendingInWindow()` shared by the hand-off
  and the `list-done` check (list-done was firing at noProgress=1 and pre-empting everything).

**Verified live**
- Manual-seeded run: **seeded 23 → captured 23**, **202 comments / 57 replies**, 4-day window, **0 redirects**.
  vs the broken feed loop the same afternoon: 12 posts / 46 comments with **Jul 26 = 0 posts**.
- Cross-checked against a screenshot: Fabio HD "75 chars rule" post — FB shows **5 comments**, capture got
  **5** (3 top-level + 2 replies). In Supabase: 5 comments, 2 replies, **5/5 linked to a member**.
- Supabase after load: **23 posts / 207 comments / 57 replies** in the 4d window.
- **`scripts/olivia_leak_gate.py` — 147/147 PASS.**

**Fixed along the way**
- `load_feed.py` 500'd on EVERY run: `refresh_member_map` upserted duplicate `fb_uid`s in one command
  (`ON CONFLICT DO UPDATE command cannot affect row a second time`). Now dedupes, preferring the row with
  an `at_member_id`, and **prints the collisions** instead of hiding them. Backup `/tmp/load_feed.py.bak`.

**Open / next**
- ⚠️ **737 duplicate `Member ID (FB)` in AT FB-Engagement `tblVc38gw21iHLYMG`** — ~781 unique uids across
  ~1,518 rows, names identical on both copies (e.g. "Anita Petrov / Anita Petrov"). Systematic 2x, not
  sporadic. Table was rebuilt clean to 749 in June — something re-duplicated it. **Not investigated
  (Andy paused scraper work). Do NOT delete member records.**
- **Images: 0 of 23.** The URL pass doesn't extract them; they live in the *manual* capture file, same
  `postId` — needs a join step before `download_images.py` can run its half of the SOP.
- **Polls not captured.** Fabio's post kept only the question; the 3 options + 24/23/53% are lost.
- `inlineAdded == commentCount` is **NOT** a truncation signal — FB ships full comment data inline even
  when it renders it collapsed behind "View more comments". (I wrongly flagged this as truncation.)

**Process note:** several iterations were guesses tested against live Facebook, which spends ban risk to
answer questions the local artifacts already answered. Reading `~/Downloads/mds_feed*.json` gave the root
cause in two minutes. **Check the artifacts before asking for another live run.**

---

---

## 2026-07-24 (FB COMMENT BACKFILL — overnight "all-in" run COMPLETE; warehouse now 12,795 comments)

**Standing goal reached: comments for (nearly) the whole 2026 post archive are now in Supabase.** Ran the remaining **1,469 posts** through `dz_omar/facebook-comment-scraper` (actor `K5EXlxalV2BCYfgKM`) in ONE overnight "all-in" run (`GSMuFC7VaRnFajwZE`, Max Comments/URL=75, replies ON, burner cookies, 256 MB). Andy launched it from the Console (harness blocks cookie-launch); I ran an unattended watcher + heartbeat all night.

**Result:** run SUCCEEDED — **9,012 comments across 1,083 posts, $6.74, 38 auto-recoveries.** Warehouse (`digest.fb_comments`) now **12,795 comments / 97.5% member-matched (12,473) / 1,624 of 2,093 posts have comments (78%).** **Only 10 posts still un-scraped** (poison/hung posts skipped across resurrect cycles) — a 2-min follow-up batch mops them up (`export_remaining.py` → 10 URLs).

**THE watcher fix (hard-won, `watch_run.py` rewritten twice tonight):** the OOM-only resurrect watcher was BLIND to a **hung-but-RUNNING** post (a bad/restricted post whose comment GraphQL query never returns — status stays RUNNING, so it sits forever; hit at posts 80/168/184…). First fix = stall-detect on a frozen post-counter → but that **FALSE-FIRED on legit heavy posts**, because **dz_omar writes a post's comments only when the post COMPLETES**, so items stay flat for a heavy post's whole duration (aborting good posts + redoing them = the wasted-resurrect/slow-window symptom). **REAL fix = detect hangs by LOG SILENCE:** a heavy post keeps emitting `fetched N direct replies` lines every few seconds; a genuine hang goes silent. Watcher now: items-flat > `PROBE_AFTER`(60s) → fetch log tail → if last log line older than `STALL_SECS`(120s) → abort+resurrect; else hold fire. After that fix: 0 false-fires, only genuine hangs caught. Also handles FAILED/TIMED-OUT/ABORTED → resurrect, SUCCEEDED → load+mark+exit. Runs token-only (no cookies) so the harness allows it unattended. `caffeinate -dimsu` kept the Mac awake; `mark_checked.py` marks every processed post (incl 0-comment) so `export_remaining.py` converges.

**Gotchas learned:** (1) Apify **resurrect resets an in-flight request's retry count**, so abort+resurrect can LOOP on a single poison post — but the log-silence watcher advances past them fine in practice. (2) `dz_omar` **does NOT use the Apify request queue** (handled/pending counts all 0) — no cheap progress signal there; the run **log's `[N/1469]` counter** is the only post-progress signal. (3) Apify log endpoint **ignores HTTP Range** (returns 200 + whole log) but the log stayed small enough (~400 KB) to fetch each poll. (4) A single big run DID work despite the memory's "overnight big-runs = NO" — the watcher's self-healing is what made it viable; slowdowns were localized **bad-post clusters** (e.g. ~727–760), not a throttle death-spiral (each cleared on its own). Tools: `apify_fb_run.py`, `watch_run.py`, `export_remaining.py`, `load_comments.py`, `mark_checked.py` (all in `/Users/Born/mds-scorecard-tools/`).

### 2026-07-24 (afternoon) — POST TEXT SOLVED: 7.9% → 99.7% via extension v0.70 "Manual Capture"

**The blocker nobody had measured:** with comments banked, a coverage audit against the FB Insights CSV (`Facebook_Group_Insights_7-23-2026.csv` — the **"Daily numbers" sheet has full-year daily Posts/Comments counts**, unlike "Top posts" which is 28-day-locked) exposed that **`fb_posts.text` was only 165/2,093 = 7.9%.** Comments were 99.6% texted but posts were empty shells — Olivia would have had 12.7k replies with no idea what they replied *to*. Not shippable.

**Built extension v0.70 — "Manual Capture (you scroll)"** (`manualCaptureMain` + `startManualCapture` in background.js, popup button 4). Passive harvester: opens the CHRONOLOGICAL feed and reads GraphQL the page already fetched while a HUMAN scrolls. **It never scrolls/clicks/navigates — that passivity IS the safety property; do not add auto-scroll.** Fixes the 2026-07-23 console-snippet bug (text 0/2085) by reusing the SAME walk-based extraction `captureFeedMain` already proved: walk the Story, keep the LONGEST `message.text`. HUD shows posts / text% / **oldest-date-reached** (the scroll odometer). 3 save layers: localStorage every 2s → partial file every 90s → final on Stop. **Partials are CUMULATIVE (each rewrites the full set) → only the LAST file is needed.**

**Result: Andy scrolled the whole year in one pass → 2,116 posts @ 99.7% text, back to 2025-12-26.** Loaded via new **`load_manual_text.py`** → **19 new posts + 1,919 text-fills**. Warehouse now **2,124 posts / 2,118 with text (99.7%)**.

**⚠️ CORRECTION — the overlap principle does NOT recover old missing posts.** I predicted a 2nd scroll would recover most of the 243 posts missing vs FB's count (Jan–Jun 20: we have 1,816 of FB's 2,059 = **88.2%**). It recovered **ZERO** — post coverage was byte-identical after the full scroll. Two independent full scrolls months apart missing the SAME 243 ⇒ those posts are **deleted/removed, not missed**. Overlap self-healing works for RECENT posts still live in the feed (the Mon/Thu case); it does NOT transfer to months-old history. **Treat 88.2% as the practical ceiling = ~100% of posts that still exist.** Don't burn another scroll chasing them.

**Comment coverage audit (same method): 11,153 of FB's 17,194 = 64.9%** for Jan–Jun 20 (Feb worst at 41.1%). Diagnosed: **429 posts sit at 0 comments** — and that's **my pipeline's fault**: `mark_checked.py` stamps a post "checked" whenever the log says `Scraped N comments` **including `Scraped 0`**, so posts whose query failed during a hang/abort cycle look done and `export_remaining` stops offering them. Re-run list staged at `~/Downloads/mds_rerun_zero.txt` (429 urls, Feb=131). **DEFERRED by Andy** — burner took another FB warning; comments aren't the blocker.

**Tooling gotchas (cost real time):** (1) `load_manual.py` uses `resolution=ignore-duplicates` — correct when the capture had BLANK text (protects good data), but **inverted now**: it would silently drop text onto the 1,928 empty rows. Hence `load_manual_text.py` = two-pass **fill-only-if-empty** merge (insert new; PATCH text ONLY where DB text is null/empty; never overwrite a non-empty body). (2) `fb_posts.group_slug` is **NOT NULL** — omit it and inserts 400. (3) **curl with `input=` sends NOTHING without `--data-binary @-`** → PostgREST `PGRST102 "Empty or invalid json"`. Same trap as the events curl fix.

**Validated against 3 posts Andy screenshotted** (Dan Wills intro / Sarah Wells USTR / Khalid force-majeure): text matches verbatim start-and-end, full length (725 / 1,819 / 1,242 chars), **emoji 🚨, `**bold**`, unicode "Türkiye", and line breaks all preserved**; longest capture 12,569 chars uncut. **KNOWN LIMIT: images/attachments are NOT captured** — Khalid's post carries the quoted Amazon policy in an image we don't have.

**NEXT (Andy's order):** (1) **IMAGES FIRST** — add image capture to the extension (FB CDN urls are **signed + expire in hours/days**, so they must be DOWNLOADED promptly, not stored as urls; decode via Claude vision, precedent = Centurion verifier in mds-digest-web). Andy re-scrolls for images. (2) **While he scrolls → Olivia hookup E2E** — derive `content_items` from fb_posts/fb_comments, extend `olivia_leak_gate.py` (unknown access_rule types are DENIED fail-closed → FB needs its own rule + canaries), exclude the Aytac murder-suicide thread, gate GREEN before ship. (3) 429-comment re-run + last 10 posts — deferred until the burner is healthy.

---

## 2026-07-23 (FB HISTORICAL BACKFILL — cracked it: manual scroll → ALL of 2026 in Supabase)

**Standing goal (Andy): full-2026 FB archive — "skipping is not an option."** After exhausting the feed/Apify/export routes, the thing that WORKED = **a human manual scroll + a GraphQL-capture console snippet.** Result: **2,085 posts, Dec 30 2025 → Jul 23 2026 (all of 2026), 100% author UID+name+date.** Loaded via `load_manual.py` (resolution=ignore-duplicates → never overwrites existing text/comments): **1,928 NEW → `digest.fb_posts` now 2,093 posts, 92% member-resolved.** The complete 2026 enumeration is now durable in Supabase.

**Why manual scroll won (key learning):** FB shells the CHRONOLOGICAL feed for BOTS at ~40-69 posts (~10 weeks) — a throttle on fast/headless/datacenter scrolling, NOT a hard cap. A **human scrolling slowly in a real trusted session** paginates the whole year. The snippet patches fetch/XHR to harvest every feed GraphQL Story (post_id + actors[0].id/name + creation_time). **GAP: snippet's `message.text` path was wrong → text empty (0/2085).** Post text + comments = pass 2 (open each URL).

**What DIDN'T work (don't retry):**
- **Apify `whoareyouanas/facebook-group-scraper`** (private via cookies, 99% healthy, $0.01/post): cookies auth into the private group ✓, but **chronological feed WALLS at ~69 posts** — log: `[SCROLL] Stalled after 15/15 iterations with no new posts` (`GraphQL:100` then FB stops). Same bot wall. RECENT_ACTIVITY opens each post (full text+comments) but reached only 1 (shallow). Tool `apify_fb_run.py` (curl+token: launch/status/pull/inspect/store/log). **Harness auto-mode classifier BLOCKS Bash that sends FB cookies to Apify (launch); reads/status/pull fine; can't self-edit autoMode config** → user-launches-in-Console workaround. **Deleted `.apify_token`+`.burner_cookies.json` after (sensitive; re-add next session).** Pass-2 comment actor identified: **`dz_omar/facebook-comment-scraper`** (COOKIES+COMMENTS+POST-URLS).
- **FB Insights export "Top posts" LOCKED to last-28-days** — tested Jan/Feb/Mar/Apr/May picker ranges, all returned the SAME 99 recent posts. Dead for history. BUT the **"Daily numbers" sheet = full-2026 ground truth: 2,229 posts / 17,957 comments** (2,085 captured ≈ 93%). Tool `extract_top_posts.py` (csv+xlsx).

**PASS-2 (comments) — PIPELINE PROVEN + RUNNING (2026-07-23 ~20:00):**
- **TEXT** = `whoareyouanas` fed POST URLs (not group URL) → 100% post text (0 comments/author). Fills the null-text backbone. Not yet run at scale (budget: prioritize comments).
- **COMMENTS** = **`dz_omar/facebook-comment-scraper`** (actor `K5EXlxalV2BCYfgKM`). Input: `urls`[] + `customCookies` + `fetchReplies` + `maxCommentsPerUrl`. Pricing **$0.50/1,000 comments** (~$8-15 for the year). Output 1 item/comment = `{source.id, comment:{id,parent_id,author:{id,name},text,created_at,total_reactions}}`. **`load_comments.py`** maps → `fb_comments` (upsert comment_id, depth=0 if parent_id null else 1). **160 test comments loaded, member-resolved in fb_activity (incl 2021/2024).** Runs stall INTERMITTENTLY on the flagged burner (datacenter IP): full run `UhxU1fVDNNAwo8O6S` died at ~10 posts (right at the security-flag event); a 50-post batch `s8DNpoHMt65B5q1Vw` (post-recovery) got **36/50 posts / 378 comments then stalled** (CPU 1%, idle). **Warehouse now: 1,288 comments / 193 of 2,093 posts / 94% member-matched (~7% of the year's 17,957).** **KEY: overnight big-runs DON'T work — they stall at ~30-40 posts then idle for hours. BLOCKER = dz_omar has NO residential-proxy option → datacenter IP → FB throttles/flags the burner cumulatively.** Proven-good pipeline (post_id join + uid→member + upsert dedup); a June-10 Fabio Gullo thread reconstructed fully member-resolved as proof.
- **GOTCHAS:** (1) URL input via "Text file" upload = SILENTLY 0 URLs (log: "No URLs provided"); use **Bulk-edit / JSON paste** of `[{"url":...}]` (watch for leftover `requestsFromUrl` file-refs = double-processing). (2) Console memory greys to 256MB but plan allows 64GB + **256MB runs dz_omar fine** (empty-URL was the real bug, not memory); resurrect-at-8GB via API if it OOMs. (3) **Apify RESURRECT (API, no cookies → classifier allows) continues a FAILED run where it left off** — I drive the resume loop; but a SUCCEEDED-with-0 run has nothing to resume. (4) **Burner got FB "account hacked" security flag** (cumulative datacenter logins) — Andy recovered it; scrape kept working through the warning. Datacenter-IP = flag risk; dz_omar has NO residential-proxy option. New `apify_fb_run.py` cmds: resurrect/abort/runs/actor. `.apify_token` re-added (test value).
- **NEXT — finish comments. THE REAL FIX = find/config a private-group comment actor WITH RESIDENTIAL PROXY** (dz_omar has none → the whole stalling problem). Research Apify store for a cookies+comments+POST-URLS+proxy actor, OR check if dz_omar has a hidden proxy input / can run behind Apify Proxy. Until then: small attended batches only (~each stalls at 10-40 posts; resume = `select post_id from fb_posts where not exists(comment) and created_time in 2026` → build `[{"url":...}]` JSON → paste into dz_omar → load with `load_comments.py`; upsert-safe, order-independent). Recent comments keep flowing via the extension (Mon/Thu). **OVERNIGHT BIG-RUNS = NO (stall early + idle).** Olivia hookup (derive content_items behind leak gate) waits until comments are fuller. Then: **fix manual-scroll snippet text-path + bake "Manual Capture" button into extension** (FB blocks console-paste; reload loses scroll → inject via ext). Raw scroll: `mds_backfill_manual.json` (Downloads). **Post-text fill = `whoareyouanas` on POST urls (100% text, no throttle issue — it's lighter). Consider doing TEXT via whoareyouanas + COMMENTS via small dz_omar batches.**

---

---

## 2026-07-23 (Scorecard / FB digest — SUPABASE STORE LIVE: who-said-what-where, member-resolved)

**FB conversations now land in the member-360 warehouse** (digest schema, same Supabase as WA/Olivia — NOTE: it's the `digest` SCHEMA of the video-platform project `nadtudwuwjhckotrngzn`, `SUPABASE_DB_SCHEMA=digest` in mds-digest-web/.env.local; the account-level MCP shows only public schemas, which cost 20 min of confusion).

**Shipped (migration `fb_digest_store` + `mds-scorecard-tools/load_feed.py`):**
- `digest.fb_posts` + `digest.fb_comments` — FB stable ids as PKs → upsert = idempotent + overlap-safe (Mon/Thu windows merge, counts derived). `first_seen` never overwritten / `last_seen` bumps.
- `digest.fb_member_map` — FB uid → `at_member_id`, refreshed from AT FB-Engagement each load (SSOT = AT; **`at_member_id` = the tail of `MDS Member URL`**, verified joining `member_profiles`).
- `digest.fb_activity` view — one row per utterance: kind, author (canonical `member_profiles.full_name`, falls back FB profile name), at_member_id, status, text, clickable fb_url (post permalink; comments get `?comment_id=<legacy_id>`). RLS on all 3 tables, no policies (service-role only, content_items posture); view `security_invoker`.
- Loader = curl-based (this Mac's python urllib SSL is broken), creds from mds-digest-web/.env.local, `Content-Profile: digest`, chunked merge-duplicates upserts. No args → newest final in ~/Downloads.

**Loaded + verified (exec: both files, live SQL):** Mon `mds_feed (16)` + Thu `(17)` → **49 unique posts / 160 comments / 0 FK orphans** (21+40 posts in → 49 out = the 12 overlaps dedup'd). Map: 773 uids, 715 with at_member_id. **Match rate 194/209 utterances (93%).** Money proof — Michael Patrón's Summit thread reads as one merged 10-comment timeline across both runs with **canonical DB names** (FB "Michael Patrón" → **Michael Wilson**; "Prue Millsap" → **Prudence Tweedie-Millsap**). Aaron Fuhrman's OPENAI post (10 cmts), Richard Laatz, Lian Sun (Mon-only, survived) all present.

**Known gap (15 unmatched utterances):** MDS.co page account (correct — not a member) + 3 real members whose **Members-DB `FB Profile Link` (fldOMkijXdtTAWYoy) is EMPTY** (same root cause as their ghost mislabeling): Tamkin Collins (uid 199306344), Matthew Kalatsky (uid 100000458378012; legacy 1239367399), Ivan Ong (**2 FB accounts**: 100002563332728 linked in engagement, but he COMMENTS as 807920466 — which is real? → Andy). Fix = fill the SSOT field, next member_profiles sync carries it; engagement rows' `MDS Member URL` stays null for hand-linked rows (whatever fills it didn't backfill) — the map's URL-tail parse handles everyone else (715).

**Olivia connection = STAGED, not wired (deliberate):** the pattern is her existing pipeline — derive `digest.content_items` rows (source `fb_post`/`fb_comment`, access-tagged member) so `content_search()/content_lookup()` finds FB organically. That is OLIVIA-project work: extend `scripts/olivia_leak_gate.py` (111 checks) with the FB source FIRST, then the content_items derivation, then gate GREEN, then ship. Sensitivity flag for that session: FB content includes e.g. the Aytac murder-suicide thread (Eugene publicly closed it) — decide match-don't-quote posture / exclusions before Olivia can surface FB.

**Also surfaced (pre-existing, decide separately):** Supabase advisor flags **RLS DISABLED on 6 digest tables** (`chats`, `olivia_sends`, `olivia_messages`, `olivia_seen`, `member_profiles`, `at_field_catalog`) — anon-key readable if the digest schema is REST-exposed. Don't blanket-enable (would break nothing for service_role but needs a policy pass) — schedule a security session.

**Weekly flow now:** Mon/Thu capture (button, tab frontmost) → `python3 mds-scorecard-tools/load_feed.py` (auto-picks newest final) → done. Next build: content_items derivation behind the leak gate (Olivia session), then the digest summary job.

**Full-history stitch (same day, Andy's ask):** loaded ALL 18 final capture files Jun 20 → Jul 23 in capturedAt order (oldest first so freshest text wins; partials/recovered skipped — subsets of finals; every historical file had proper FB comment ids). Warehouse now: **165 posts / 709 comments / 0 orphans / 95% member-matched**, incl. **181 replies from the pre-softening June era** (top-level-only going forward; filter `depth=0`). Verified id-diff of all 31 Downloads jsons (finals+partials+recovered) vs DB: nothing missing. Coverage: solid Jun 12–19 (56/311), Jun 29–30, Jul 16–23; thin Jun 22–28 + Jul 1–12 (throttle-pause/parked era); a few genuinely old posts (oldest = Courtney Lee's 2021 Perks pin) that deep scans reached. Gap analysis: only real holes = **Jul 1–6 + Jul 10–15** (June 1-2-day holes ≈ weekends).

**Backfill attempt (Jul 1–15) FAILED — parked.** v0.67/0.68: `CONV_DAYS=23` + new `BACKFILL_FROM/TO` target-range skip (open ONLY gap-dated posts; known-date-outside → processed without an open). Two runs: enumerate banked 85 then 51 (shrinking = throttle warming), **0 opens both** — after a deep enumerate FB serves the feed back shelled/thin, so Phase 2 finds no anchors. Andy called it ("no way we scrape 23 days"). Stop button dead (MV3 worker died); `window.__mdsStop=true` via console set but no file downloaded (loop likely already dead; possibly also Chrome's fb.com auto-download block — CHECK the address-bar blocked-download icon before Monday). Nothing lost (0 opens = no new data). **v0.69 = production config restored (CONV_DAYS=4, backfill 0/0 — mechanism kept for future SHALLOW slices).** Andy reloaded to v0.69, toggle re-enabled, fb.com downloads = Allow (verified). **SUPERSEDED verdict: Andy set the standing goal — FULL-2026 archive, "skipping is not an option"** (missing Jan–Jun 11 ≈ 1,200–1,500 posts). **Andy has a SECONDARY FB account, group member, disposable** → removes ban-risk on aggressive methods (use it, NEVER main).

**Enumeration recon (live, main acct, 2026-07-23) — the hard truth:** to reach months-deep history you must *enumerate all post ids in an arbitrary past window*. Tested every free surface: (1) feed CHRONOLOGICAL scroll SHELLS past ~3wk on any account (proven); (2) **mbasic.facebook.com DEAD** — FB redirects to www; (3) **FB group search + date filter** — the filter IS custom-range to the day + URL-constructable (`filters=`base64), reaches 2023 for lookups, BUT relevance-RANKS+CAPS: same Jul 20–21 window (~15 posts) → `q=the`=5, `q=a`=3, DIFFERENT subsets; no query complete, union never provably complete → **lookup-only, NOT an archive enumerator**; (4) GraphQL replay DROPPED (Andy skeptical, right — brittle/detectable). **Conclusion: free routes can't do exhaustive months-deep enumeration. Only path = Apify maintained FB-group actor + burner cookies.** Blockers only Andy can clear: reconnect Apify connector (token INVALID, none in any project file — grepped), paste burner cookie into actor input himself (credential boundary), small $; our old custom actor capped ~390 → maintained actor, UNPROVEN at 6-mo depth. **Next: vet best FB-group actor → JUNE test on burner (ground-truth vs data we hold) → run Jan–Jun.** Spec in NEW_SESSION_PLAN step 3.

---

---

## 2026-07-23 (Scorecard / FB digest scraper — Thursday cadence run PASSED; capture VALIDATED, code freeze holds)

**The Mon/Thu validation is complete — v0.66 is production.** Thursday 4-day run (`mds_feed (17).json`, 15:53Z): **39/39 banked→opened, `list-done`**, 40 posts / **139 comments**, 0 replies leaked, window Jul 18→23 ✓ — 2× Monday's volume, same clean execution.

**Both Monday misses self-healed (the overlap design working):** Aaron Fuhrman's "OPENAI Ads" post (Jul 21 14:14, missed Mon, proven FB-side omission) captured Thu **with 10 comments**; Richard Laatz's FBA post (Jul 21 13:37, miss #2 confirmed via search-page embedded `creation_time`) captured Thu with 2. **Gap-filler stays parked** — only build if misses recur. Overlap refresh verified: 12 shared posts re-captured with grown threads (Michael Patrón 3→10, Cou Ka 2→8, Razvan 6→9); loader will upsert so Thursday supersedes. Boundary note: Lian Sun's Jul-18 post (4.9d) fell off Thursday's tail — normal at the enumerate edge (4.5d brake vs 5d output grace); it's complete in Monday's file, upsert merges.

**Monday's screenshot-vs-capture audit (2026-07-21, drove the misses hunt):** Brandon 6/6 top-level + 13 replies excluded ✓; Lian 1/1 + 3 replies excluded ✓; Michael snapshot-correct (later comments arrived post-capture) ✓; Richard = miss. Diagnosis method that ended the DOM guessing: **live-attach to Andy's real Chrome (claude-in-chrome), read-only** — feed probes + group-search `creation_time` extraction from embedded page JSON. FB's chronological listing provably omits ~5-10% of posts per serve (cursor gaps) while serving their neighbors; search + "New posts" views still show them.

**v0.64→v0.66 (shipped Mon–Tue, all proven in these two runs):** v0.64 = structural featured-skip (bank only inside `[role="feed"]`; Featured carousel lives OUTSIDE it — replaced two failed heuristics, proven via Andy's console dump). v0.65 = chronological kill-switch (`window-edge` stop; bottom-jumps disabled past the edge — killed the "scrolled to Jul 15" dive). v0.66 = `CONV_DAYS` 1→4. Both stop paths seen live: `window-edge` (1-day run, `mds_feed (15)`) + `list-done` (both 4-day runs).

**Next:** 1) `load_feed.py` + apply `supabase_fb_digest.sql` (upsert on FB ids; both Monday+Thursday files land clean). 2) Digest summary job (reuse WA-digest machinery vs standalone). 3) Keep Mon/Thu manual runs (Capture conversations button, tab frontmost) until the loader proves out, then consider scheduling.

---

---

## 2026-07-08 (FB conversation-digest scraper, session 15) — Scraper UN-PARKED + opener fully redesigned (enumerate-then-capture, chronological sort, flyout fix, junk filter, configurable window) v0.46→**v0.56**. Landed at **84% coverage** on a 4-day window (banked 45 / opened 38, 140 comments, clean Jul 4-8). Validated vs FB export (join works; tail-miss found). Supabase storage schema designed + migration written. **Continue tomorrow with a FRESH run.**

> This is the FB **conversation-digest** scraper (feeds a future digest), SEPARATE from the scorecard roster/insights capture. Code = `/Users/Born/mds-scorecard-tools/extension/` (not under git → this log is the record). Extension reload = **Remove + Load unpacked** (MV3). Node syntax-check only; real validation = Andy's live run (I can't drive FB).

**Throttle cleared.** Was tool-flagged (rapid extension clicks), NOT account-wide — Andy hand-scrolled the feed back to Jun 22 (healthy pagination). So capture resumed.

**Root cause of the old ~21% coverage:** the opener found the next post to open ONLY via a rendered `/posts/`|`/permalink/` anchor, which only exist inside expanded COMMENT blocks. Virtualized/collapsed posts expose none → most posts never opened.

**The redesign — decouple ENUMERATE from CAPTURE** (the core fix, `captureFeedMain`):
- **Phase 1 enumerate** — slow-scroll the window once, bank every post id (`order`/`seenId`) via `bankFromDom()`. A banked id survives FB shelling the post out. A read-only probe proved a full scroll surfaces ~88% of post permalinks (vs the old on-the-fly ~21%).
- **Phase 2 capture** — walk the banked set, open each post via its on-screen permalink anchor (the proven modal-open → expand → `history.back` cycle, untouched), bounded to `seenId`.

**Bugs found + fixed, in order (each a real live-run finding):**
- **v0.48 flyout trap** — `document.querySelector('[role="dialog"]')` grabbed the **Messenger chat flyout** (also `[role="dialog"]`) → loop thought a modal was always open → froze at `0/N`. SAME trap as the Insights-export bug. Fix: a dialog only counts when `urlPostId()` is truthy, and target the **largest** dialog (`postDialog()`), never the flyout. Also reverted Phase-2 open to the proven "click any on-screen anchor" (the strict per-id lookup was too fragile).
- **v0.49** — Stop felt dead (loop only re-checked the flag after the 3.5–6.5s human-gap). Added `napStop()` interruptible sleep (~0.2s reaction). Partial-file save 30→8 posts.
- **v0.50** — `stopCapture()` now also fires `recoverLastCapture()` → writes a file on Stop. **Andy's Chrome clears localStorage on tab-close**, so we rely on **downloaded files**, NOT localStorage/Recover.
- **v0.51 chronological switch** — RECENT_ACTIVITY floats old posts up (recent comments) so there was no clean date cutoff → enumerate ran to mid-June. Switched `FEED_URL` to `sorting_setting=CHRONOLOGICAL` (post-date order = monotonic); brake on the oldest `Story.creation_time` read from the captured feed GraphQL (reliable network JSON, not DOM) + 120-post backstop. HUD shows `back to ~Xd`.
- **v0.52 pinned-post early-stop** — 2 pinned posts (Jun 25-26) sit above the chronological feed, get opened first, and their >7d age tripped the `postAgeDays` `oldStreak` "7d-window" stop after just 2 opens. Removed that early-stop (enumerate now bounds the window); bounded Phase-2 opens to `seenId`.
- **v0.53 scroll-restore + junk filter** — feed reset toward the top on each modal close → plateau at ~29. Save/restore `feedY` across close. Skip `[role="complementary"]` sidebar ("Recent media/files" = ancient 2021-2025 posts). Date-filter the output (`snapshot()`) to `WINDOW_DAYS+1`. `noProgress` 12→18.
- **v0.54** — added `banked`/`opened` to the saved `_diag` (was debugging blind).
- **v0.55** — `WINDOW_DAYS = days` (configurable); `CONV_DAYS = 4`. Andy's insight: smaller window (Mon/Thu cadence) = fewer posts/run = less throttle load AND the opener covers a bigger fraction. Popup label 7→4 days.
- **v0.56** — cleanup: removed the ⚡ Test capture (5), ⚡ Feed test (15), 🐛 Dump Raw GraphQL debug buttons + listeners (kept Roster/Insights/Conversations/Recover/Stop/Schedule). Background handlers left as harmless dead code.

**RESULT (4-day run, v0.55):** `banked 45, opened 38 = 84%`, 22 posts w/ comments, **140 comments**, all Jul 4-8. Opener climbed steadily 8→16→24→38 (no plateau); reached deep posts it never used to (Advisory Council 18 comments, was 0).

**Validation vs FB "Top posts (last 28d)" export** (per-post comment counts + permalinks): (1) **our `postId` == FB's permalink id — the JOIN WORKS**, which de-risks the `authorUid`→AT-member mapping. (2) Where we open, we're accurate (4/5 met-or-exceeded FB's count; over = our capture ran later than the export snapshot). (3) **Miss found: Kim's "Fable extended" post — FB 31 comments, we captured 0.** It's the OLDEST post in the window; opener quit (`end-of-feed`) before reaching it. So misses are **high-value tail posts, not low-activity junk** — coverage to ~100% of the window matters (correcting my earlier hand-wave).

**Storage/mapping designed (Supabase, the member-360 warehouse):** `fb_posts (post_id PK)` + `fb_comments (comment_id PK)`. **Upsert on FB's stable ids = idempotent + incremental** — re-scraping a post inserts NEW comments, updates existing in place, thread stays connected via `post_id`+`parent_comment_id`. **Counts are DERIVED** (`COUNT(*)`), never accumulated → double-counting is structurally impossible → **overlapping Mon/Thu windows are SAFE (a feature, not a risk)**. `first_seen` = "new this period" (incremental digests); `last_seen` = detect deletions. `author_uid` stays raw → **live join** to Members via FB Engagement `Member ID (FB)` (same key as `reconcile.py`; non-members don't resolve = correct). Migration written to `mds-scorecard-tools/supabase_fb_digest.sql` — **NOT applied to Supabase yet.** Summary job can reuse the WA-digest machinery.

**KEY GOTCHAS:** (1) keep the FB tab **FRONTMOST** the whole run — background-tab timer throttling stalls the loop into a premature `end-of-feed`. (2) ~8 capture runs today; throttle is CUMULATIVE (last time 30+ over 2 days) → don't hammer; one paced run at a time.

**Files touched:** `mds-scorecard-tools/extension/background.js` (→ **v0.56**, the whole opener redesign), `popup.html` + `popup.js` (4-day label + cleanup), `manifest.json` (v0.56); new `mds-scorecard-tools/supabase_fb_digest.sql`. No git (tools not a repo). Downloads has the working `mds_feed*.json` captures.

**NEXT (tomorrow, FRESH run):** (1) **Opener tail-fix** — before giving up (`end-of-feed`), retry the still-unreached `seenId` posts (scroll to each) so we catch the oldest-in-window posts like Fable; validate ONE run reaches ~100% of a 4-day window. (2) **Apply the Supabase migration + build the loader** (`load_feed.py`: upsert `mds_feed.json`, resolve `author_uid`→member). (3) **Summary query** (weekly/biweekly, reuse WA-digest pattern). Decide: FB digest reuses WA-digest pipeline vs standalone.

* * *

---

## 2026-07-06 (Scorecard scoring, session 14) — Weekly FB engagement re-imported + validated end-to-end; Insights auto-tick root-caused & fixed (v0.46); export + roster SAFEGUARDS added (auto_import validate → Slack warn); health freshness made schedule-aware (staged). FB digest scraper still THROTTLED (parked). **→ detailed next-session plan = `NEW_SESSION_PLAN.md`**

> Code in `/Users/Born/mds-scorecard-tools/` (extension + python) + `/Users/Born/mds-digest-web/` (health app), both SIBLINGS of this repo. **Full next-session plan lives in `NEW_SESSION_PLAN.md` (read that first).** This entry is the record.

**Point 1 — FB engagement current + VALIDATED end-to-end.** `process_fb.py` on the 7-06 export → **768 rows @ 2026-07-06, 95 contributors**. Andy pushed "1000% sure?" → validated three links: source xlsx == FB Engagement table (`tblVc38gw21iHLYMG`, Michael Patrón 15/79) == leaderboard mirror lookup (`tblbN6JVeSk2XoPst`, Mo Kuhail `FB Posts [2]`/`Comments [47]` == his source row); `Member's score NEW` (fldzEH3UZgOdE9bm2) is a formula off the lookups → auto-current. Non-contributors also stamped 7-06 w/ 0 (whole table). **Note:** filterByFormula `{Reporting Date (scrape)}="2026-07-06"` returns 0 (date-field string-compare quirk) — the data IS 7-06; don't trust that filter.

**Point 2 — Insights export fixed + guarded.**
- **2a root cause (v0.46):** `clickInsightsDownload`'s `dlg()` = `document.querySelector('[role="dialog"]')` returned the FIRST dialog = the **Messenger chat flyout**, so it searched the wrong dialog → the tick silently no-op'd (why Andy had to tick All by hand). Fixed: target the dialog holding the `Growth`/`All` checkbox (inspected LIVE — the boxes are native `input[type=checkbox]` with `aria-label="Engagement"` etc.), click **All**, and a HARD SAFEGUARD aborts+warns unless Engagement+Members are ticked. **Andy confirmed 2a works.**
- **2b (`auto_import.py`):** added `validate_xlsx()` — before import, checks the export has Contributors + Daily-numbers tabs; if not → **`slack_warn()` + does NOT run process_fb** (a Growth-only export can't zero the scores). Tested (7-06 passes, bad flagged).
- **#3 (`auto_import.py` + `reconcile.py`):** roster <500 → Slack warn + **skip reconcile** (that's what produced the wrong Jul-6 card: 3 ghosts on the partial 70-roster). reconcile also internally falls back to exclude-only ghosts + no departed when roster<500. Extension roster capture warns if <500 (v0.45).

**Health monitor — freshness made schedule-aware (STAGED, not deployed).** `mds-digest-web/src/lib/tools-health/fb.ts`: was `staleDays<=8=healthy` (so a just-missed Monday run at 6 days stale read green — why Andy got no warning). Now: past Monday's run window + latest scrape < this Monday ⇒ `degraded`. Proven (old=healthy→new=degraded). **On the `mobile-adaptive` branch, UNCOMMITTED — deploy is push-to-main (Vercel), git author `andy.verdy1@gmail.com`.** Also found: the `scorecard` tool's live check reads the **WhatsApp** stamp (fresh via n8n) not FB — a second reason it stayed green.

**FB conversation-digest scraper — still THROTTLED, PARKED.** Feed caps at ~1–4 posts + won't paginate; 3-day rest didn't clear it (verified live via Claude-in-Chrome). Coverage on a healthy feed is only ~21% (12 of 58 weekly posts) — needs an opener redesign, not scroll patches. Save safeguards (page-file + localStorage + Recover button, v0.40→0.44) shipped; scroll logic reverted to working v0.42. See `NEW_SESSION_PLAN.md` ⏸ section.

**Files touched:** `mds-scorecard-tools/extension/background.js` (→ **v0.46**), `auto_import.py` (validate_xlsx + slack_warn + roster gate), `reconcile.py` (partial-roster guard); `mds-digest-web/src/lib/tools-health/fb.ts` (schedule-aware, staged). `~/Downloads/mds_roster_full (5).json` = 743 (complete). Ran `process_fb.py` (write). No git commits.

**Open / next → see `NEW_SESSION_PLAN.md`:** (1) fresh ghost/team/joiner card from roster (5); (2) deploy fb.ts + add health data-quality checks; (3) Claude weekly routine (#6); (4) confirm recompute/leaderboard; (5) confirm 2a live; (⏸) FB digest opener redesign when un-throttled.

* * *

---

## 2026-06-29 (Scorecard scoring, session 13) — Roster ghost-pollution fixed at the SCRAPE (banned-card sweep, extension v0.37) + exclude-list cleanup → clean 22-ghost list; weekly Slack card rebuilt into 3 sections (ghosts / team / new joiners) with group-profile links, posted

> Roster + ghost-reporting hardening. Code lives in **`/Users/Born/mds-scorecard-tools/`** (extension + `reconcile.py`), a SIBLING of this repo, NOT under git — these notes are the only written record. Source of truth = ClickUp `2531q-100317`.

**Headline:** Root-caused the "Dafne Michan is a ghost but she's not even a member" incident — the roster scrape was sweeping in the admin members page's **"Banned · 10+" sidebar card**. Fixed at the scrape level (extension **v0.37**, heading-anchored card detection, verified live by inspecting the members-page DOM via Claude-in-Chrome). Ghost list cleaned to **22** via a two-layer model (scrape filter + data-level exclude list). Rebuilt the weekly **Slack card** into 3 sections — every name a group-profile deep link — and posted to #automation-tests.

**1. Roster scrape — banned-card pollution fixed (extension v0.36 → v0.37).**
- **Root cause (found by inspecting the LIVE `/members` DOM via Claude-in-Chrome):** `scrapeRoster` harvests every `a[href*="/user/"]`, which includes the right-rail **Banned** card (Dafne Michan `100085535750272`, David Young `837164735`, Dom Mohler `100001538603697`). The v0.36 "skip if 'Unban' within 4 ancestors" filter FAILED because a banned person's **name-anchor and the "Unban" button sit in separate DOM branches that only converge ~8–10 levels up** (the name-anchor's first 8 ancestors are all just the name; "Unban" never appears). Per-anchor proximity can't see it.
- **Fix (`extension/background.js` `scrapeRoster`):** anchor on the **card heading**. `markBannedCards()` finds the "Banned" / "Suggested for you" heading (`textContent.startsWith`, <40 chars), climbs to the first ancestor holding `/user/` links (= the card), excludes those uids — with a **≤20 cap** so a DOM change can never make the climb over-reach into the ~700-row main list. Backup `markUnbanBackup()` (a `/user/` link whose ≤300-char ancestor carries "Unban"). Final `seen.delete(banned)` scrub catches any uid harvested before its card rendered.
- **Verified live (Chrome, real members page):** detection returns exactly the 3 banned; full harvest excludes all 3, keeps real members. Calibration: banned card surfaces at ancestor depth 5–7 (3 uids); >10 starts bleeding the main list (D12 → 25) — the ≤20 cap guards this.
- **Verified in Andy's actual capture:** v0.37 roster `(3)` → David/Dafne/Dom GONE, zero real members wrongly removed (clean prefix: first 383 of scroll order captured 378).

**2. `mds_exclude.json` — data-level non-member filter (17 entries).** staff/admin (Eugene Khayman, Fer Arguelles, Ian Mds Sells, Tomi Calonge, Andy Verdy, Iliana Panag, Maria Katrina, Keziah Castillo), group page (MDS.co), Andy's alt (Andy Andy), banned (Dafne/David/Dom — belt-and-suspenders with the scrape fix), duplicate accounts (Chris Kjeldsen, Ivan Ong, Sanjay Gupta, Yana Yatseviuk — the unmatched alt-uid of a real member). `reconcile.py` ghost stage applies EXCLUDE + a current-roster cross-check (a ghost must still be in THIS week's roster, else it's "departed", not a ghost).

**Two-layer ghost-cleaning model (the design):** scrape level (v0.37) = dynamic sidebar pollution (Banned/Suggested), auto-handles future bans; data level (`mds_exclude.json`) = stable known non-members (staff/page/alts/dupes); roster cross-check = departed drop out automatically. Result: **39 raw blank-status FB rows → 14 excluded → 3 departed → 22 clean ghosts.**

**3. Weekly Slack card rebuilt (`reconcile.py` `build_card()`).** Was ghosts-only, plain `name (uid)`, posted only on `--apply`. Now **3 sections — 👻 Ghosts / 🛠️ Team / 🎉 New joiners** — every name a **group-profile deep link** (`<https://www.facebook.com/groups/699138040189700/user/{uid}/|Name>`), `unfurl_links:false` so 31 FB links don't explode into previews. Posts whenever slack token+channel exist (no longer gated on `--apply` finding ghosts). Helpers added: `grp_url()`, `load_team()` (exclude rows noted staff/admin), `load_joiners()` (reads `~/Downloads/mds_new_joiners.json`). **Posted live to #automation-tests** (ts `1782756635`): 22 ghosts, 8 team, 1 joiner.

**4. New joiners — from FB "New members this week" card.** This week: **Justin Cao** is a member-DB lead only (*Pending 1st Interview*, NOT in the FB group → no group link); the real FB-group joiner is **Julie Kirschey** (`61588929476556`), pulled from the members-page "New members this week" card via Chrome → `~/Downloads/mds_new_joiners.json`. **Manual this week** — a small roster-page add (capture that card during the weekly scrape, same heading-climb, KEEP these) would auto-fill it; not built.

**5. FB posts scraper (digest capture) — UNBLOCKED + VALIDATED (extension v0.37 → v0.38 → v0.39).** The in-feed GraphQL modal-cycle capture that FB throttling stalled all of s12 now WORKS. Two fixes:
- **v0.38 — hardened `captureFeedMain`:** human pacing (modal *opens* spaced ~4–9s randomized, vs ~2s), a 7-day **activity**-window stop (`postAgeDays` = newest comment time; feed is RECENT_ACTIVITY-ordered so once posts pass 7d it stops), **throttle detection** (4 modals opened-but-no-comment-fetch-served in a row ⇒ stop, `stoppedReason:"throttled"`), and a per-post `localStorage` **checkpoint** the orchestrator recovers if the MV3 worker is killed mid-run.
- **v0.39 — the actual unblocker:** FB changed the feed DOM. The RECENT_ACTIVITY feed is now **heavily virtualized — post containers are EMPTY shells**, and the `/posts/{id}` permalink link the opener clicks lives in the rendered **comment** blocks. The opener now scans ALL `[role="article"]` blocks (post + comment), dedupes by post id. **Diagnosed LIVE via Claude-in-Chrome** — confirmed NOT a block (feed + comments + 735-members rendered, no banner; the v0.38 run had `processed:0` because the opener found 0 clickable post links in the now-empty post containers).
- **VALIDATED:** `~/Downloads/mds_feed (9).json` = **12 posts / 82 comments**, `stoppedReason:end-of-feed`, fully threaded (depth 0/1/2). **Spot-check PASSED** vs Andy's live FB screenshots — Mehmet 10/10, Albert 6/6, Eugene "July is Packed" 14, Lisa "Seller Growth Summit" 20 — including collapsed **"X replied · 1 reply"** stubs expanded to their text (the part the old DOM scrape always missed).
- ⚠ NOTE: `(9)` was the **15-cap test**, which *skips* the 7-day window → it grabbed the 12 most-recently-active posts incl. two older ones (Sohail 06-11, Lisa 06-16) that still have recent comments. **The full run (no cap → 7-day window enforced) is TODO TOMORROW on a fresh session** — that confirms whole-week coverage + a clean `stop: 7d-window`/`end-of-feed` (not `throttled`).

**Findings / data-quality:**
- **Last week's roster (Jun 22) was a partial capture (116 of ~750)** → no reliable FB-group joiner diff this week. The complete 753 (Jun 29) is the first full baseline; next Monday is the first real new-to-group diff.
- **The v0.37 verify capture `(3)` stalled at 383/750** — clean tail-stop (first half 378/383 captured, back half 5/367), i.e. the scroll halted ~midpoint (FB throttle after many captures today / tab lost focus). NOT a filter bug. **Do not feed `(3)` to `reconcile.py --apply`** (would false-flag ~370 as departed). The complete 753 `(2)` stands.

**Decisions (for CU decisions page):** (a) ghost pollution fixed at TWO layers — scrape (banned/suggested cards) + data (`mds_exclude.json`) + roster cross-check (departed); (b) banned-card detection = heading-anchored climb + ≤20 cap, NOT per-anchor proximity (name-anchor too far from the Unban control); (c) weekly Slack card = 3 sections with group-profile deep links, unfurl off; (d) new-joiner source = FB "New members this week" card.

**Files / services touched:** `mds-scorecard-tools/extension/background.js` (→ **v0.37**) + `manifest.json`; `mds-scorecard-tools/reconcile.py` (`build_card` + `grp_url`/`load_team`/`load_joiners` + exclude/cross-check ghost stage); `mds-scorecard-tools/mds_exclude.json` (→17); `~/Downloads/mds_new_joiners.json` (new); `~/Downloads/mds_ghosts.json` + `mds_ghosts_report.md` (regenerated); Slack #automation-tests (posted); Airtable `appUM1F29IJsMsXRb` (read-only via reconcile dry-run). **No git commits** (tools live outside the repo; SESSION_LOG kept as a local working doc).

**Open / next:**
1. **Get one COMPLETE roster from a fresh (un-throttled) session** — first capture of the day, keep the members tab foregrounded ~1–2 min — then ghost/joiner detection is clean end-to-end.
2. **Extension v0.38** (offered, optional) — capture FB "New members this week" → `mds_new_joiners.json` so the card's joiners auto-fill weekly (same `markBannedCards`-style heading-climb, but KEEP the people).
3. **Re-trigger the Monday recompute `UCxyzY1RXzrIHtmX`** (still pending Andy's go) so the public leaderboard reflects today's FB data.
4. **FB posts scraper — ⛔ FB FEED NOW THROTTLED (self-inflicted, 2026-06-30). DO NOT run capture for several days.** After 30+ capture runs over 2 days, FB soft-throttled the group feed: verified live via Claude-in-Chrome that the RECENT_ACTIVITY feed caps at **~4 posts and won't paginate on scroll** (scrollHeight frozen ~13k px; NO block banner, logged in, group loads). It had degraded 12→~4. This is the anti-automation wall from the s12 notes — **the CODE is fine** (it produced the validated 70-post and 12-post runs on a healthy feed). **Fix = time, not code:** stop all capture several days to let the throttle reset, then run ONCE on the weekly cadence and reassess. Extension is at **v0.44** (save layers below; v0.43's aggressive deep-scroll STALLED → reverted to the working v0.42 scroll logic).
   - **Save safeguards (v0.40→v0.44), so a run can't lose data:** (1) the PAGE writes `mds_feed.json` at end + `mds_feed_partial.json` every 30 posts (survives Chrome killing the MV3 worker on long runs — the bug that lost a 70-post run); (2) a continuous `localStorage` copy (has been FLAKY — don't rely on it); (3) a **"💾 Recover last capture"** popup button. The **file save (layer 1) is the reliable one.**
   - **Coverage reality (measured on a healthy feed, before the throttle):** a full run got 12 posts / 92 comments = only **~21% of the week** (Insights `Facebook_Group_Insights_6-30-2026.xlsx` Daily-numbers 6/23–6/29 = **58 posts, 386 comments**). The opener only finds `/posts/{id}` links in rendered COMMENT blocks (~top 12); deeper posts render as empty shells → the scroll-and-click approach caps low. **Full coverage needs a redesigned opener, NOT another scroll patch — design it fresh, on a healthy (un-throttled) feed.**
   - Then: once a clean full-week capture exists → **load to Supabase via the n8n webhook** (`scorecard.fb_posts`/`fb_comments`; needs a Supabase Postgres cred in n8n) → n8n search + weekly digest.
5. Carry-over from session 12 (still open): eliminate the 1am laptop dependency (independent/cloud capture).

* * *

---

## 2026-06-22 (Scorecard scoring, session 12) — FB digest capture rebuilt on GraphQL → IN-FEED modal capture (per-post nav is a dead end: FB redirects); FB throttles rapid automation. + Monday weekly run verified

> Continuation of the FB conversation-digest build (approach B). Capture work is in **`/Users/Born/mds-scorecard-tools/extension`** (a SIBLING of this repo, NOT under git) — so these notes are the only written record of those edits. Source of truth = ClickUp `2531q-100317`.

**Headline:** The capture parser now works (complete, correctly-threaded comments from FB's own GraphQL). But the *delivery* mechanism fought us all session, and the real wall is FB's anti-automation throttling — not the code.

**Capture method — the full arc this session (extension v0.16 → v0.34):**
1. **DOM extraction → GraphQL.** First raw dumps came back EMPTY because **FB serves comment GraphQL over `XMLHttpRequest`, not `fetch`** — `cap_inject.js` (document_start MAIN-world patch) only patched `fetch`. Patched XHR → captures started landing.
2. **Parser built + validated.** Comment node = `{id, body.text, created_time, author{id,name}, depth, comment_direct_parent.id, feedback.reactors.count_reduced, legacy_fbid}`. Post body/author/time = `Story.message.text` / `actors[0]` / a descendant `creation_time` (NOT comments' `created_time`). Per-post **scoping** = response post id from `Story.post_id` (dialog `CometSinglePostDialogContentQuery`) or base64-decoded `data.node` Feedback id → `feedback:{POST_ID}_…`. Threading via `comment_direct_parent.id`. Reference parser = **`mds-scorecard-tools/parse_graphql.py`**. Validated against the spot-check EU-expansion post (`postId 26241168602226626`): **16 comments fully threaded incl. an 8-deep reply chain, vs 5/0 from the old DOM scrape.**
3. **Per-post permalink navigation = DEAD END.** Navigating to `/posts/{id}/` (or `/permalink/{id}/`, SPA or full reload) **redirects to the feed's top post** for most posts (66/80 in one run; confirmed on screen: opened the target, then bounced to the feed's newest post). So we only ever got the navigated post from inline feed data (truncated for big posts).
4. **IN-FEED modal capture (current, v0.30→v0.34).** Clicking a post's "N comments" in the feed opens **that post's** modal (the CORRECT post — no redirect) which fires its GraphQL. Loop: scroll feed → open a post's modal → expand (click "view more"/"view N replies") → `history.back()` to close (opening pushed the permalink URL, so back restores the feed) → next post. Parser groups all captured GraphQL + inline by `post_id`. Validated: one run returned 3 distinct posts with complete, correctly-threaded comments (incl. an 8-comment post at depth 0/1/2).

**THE WALL — FB throttling (the real blocker):** Across identical-logic runs the result was wildly inconsistent — **v0.33 returned 9 posts, v0.34 returned 1** (v0.34 only added a diagnostic; capture logic identical). The diagnostic confirmed it: a run with `processed:2` (2 modals opened) had `capResponses:1` — the 2nd modal opened but **FB served no comment fetch.** This is session-side throttling after ~20 rapid automated runs today — the *same* anti-automation wall that killed the Apify scraper. The top/freshest post always works; rapidly-opened older posts get starved. **Paused testing** (more runs deepen the throttle). The slow **weekly** cadence is exactly the mitigation; today we did the opposite.

**Supabase (store) — verified ready, NOT loaded:** `scorecard.fb_posts` / `fb_comments` already fit the new shape (`created_time`, `parent_comment_id`, `reactions`, numeric uids; `parent_author`/`raw_aria` go null). The 6 posts / 20 comments currently there are the OLD DOM test data (17-digit ids, null parents, computed timestamps) — clear before the real load. Real backfill is too big to hand-load via the MCP → load via the n8n webhook (needs a Supabase Postgres cred in n8n).

**Monday 2026-06-22 weekly SCORING run — verified live (separate from the digest):**
- **FB data DID update:** `FB Engagement (NEW)` `tblVc38gw21iHLYMG` = **749 / 764 rows dated 2026-06-22**, 97 contributors with real engagement; History appended; `reconcile.py` applied (+5 FB rows, spine 1295→1296).
- **⚠️ Scores are STALE:** recompute trigger `UCxyzY1RXzrIHtmX` fired **02:30 CDT** (07:30 UTC) but the FB capture landed **05:08 CDT** (xlsx captured 02:56) — so scores were computed from LAST week's (06-15) FB data. **Root: the 1am capture ran late because the Mac was asleep** (the standing laptop-dependency open item). Fix pending Andy's go: re-trigger the recompute to rescore on today's data.
- **⚠️ Roster under-captured** (116 vs ~753) → false "departed 648" in the log; `reconcile.py` is non-destructive so **nothing was removed** — joiner/leaver report is just noisy this week.

**Decisions (logged on CU page 7):** capture = in-feed GraphQL modal cycle (not per-post nav, not DOM); per-post permalink nav abandoned (FB redirects); FB-throttle ⇒ weekly slow cadence + don't rapid-test; Supabase backfill loads via n8n webhook.

**Files / services touched:** `mds-scorecard-tools/extension/*` (→ v0.34; cap_inject XHR, captureFeedMain, parse_graphql.py); Airtable `appUM1F29IJsMsXRb` (read-verified); n8n recompute timing (read); Supabase `scorecard` schema (read-verified). **No commits to this repo** (the extension lives outside git).

**Open / next:**
1. **Re-test the in-feed capture on a FRESH (un-throttled) FB session** (v0.34, the ⚡ Feed-test button). If it pulls 10-15 complete posts → wire the full 7-day run (7-day stop + incremental save + slow human-paced timing to avoid re-throttling).
2. **Re-trigger the Monday recompute** (Andy's go) → rescore all 1,296 on today's FB data.
3. **Load the backfill to Supabase via the n8n webhook** (needs the Supabase Postgres cred in n8n).
4. Standing: **eliminate the 1am laptop dependency** (cloud/independent capture) — root cause of both this week's late capture AND the throttle risk.

* * *

---

## 2026-06-19 (Scorecard scoring, session 11 cont.) — FB digest capture: DOM extraction UNDER-CAPTURES deep threads → PIVOT to GraphQL (approach B)

> Continuation of the FB conversation digest build. **Supersedes the "Phase 1 capture DONE" claim in the s11 entry below** — capture is NOT reliably complete yet.

**What happened:** iterated the DOM-extraction capture (extension `mds-scorecard-tools/extension`, v0.11→v0.17). Fixed many bugs en route — author names from aria-labels, dedup, "about an hour ago" times, post-author/time attempts, and **replies via `reply_comment_id`** (FB shares one `comment_id` across a comment + all its replies; the reply's own id is `reply_comment_id`; id-based parent threading works). **But Andy's spot-check killed it:** the EU-expansion post (`postId 26241168602226626`) has **16 comments + deep nested reply threads**; the capture got only **5 comments, 0 replies**. Root cause: the DOM "expand-everything-then-scrape" step isn't exhaustive on busy threads (FB hides comments behind repeated "View more comments" + each thread behind nested "View N replies") → a partial DOM gets scraped. Also post **body** is mis-grabbed on SHORT posts (the "longest dir=auto on the page" heuristic picks a neighboring post's body), and post **author/time** are unreliable (the post header isn't aria-labeled like comments + uses vanity links).

**DECISION (Andy): approach B — capture FB's GraphQL responses, not the DOM.** Proven earlier: clicking "view more comments" fires a GraphQL POST to `/api/graphql/` that returns the **full thread as structured JSON** (one 399 KB response had 29 comments + reply structures; `doc_id 27201942402808991`). The JSON is complete and also carries post body/author/time. The DOM approach kept surfacing completeness gaps; GraphQL gives the whole thread at once.

**Next (resume here):**
1. ⚠️ **First raw dump (v0.17) came back EMPTY — 0 graphql calls.** Two fixes before the next dump: **(a)** `rawCaptureMain` reads `window.__raw`, but `cap_inject.js` (document_start) patches fetch into `window.__mdsCap` — the page's initial comment fetch likely landed there; the dump must read **both buffers**. **(b)** the expander clicks may not have matched FB's real "View more comments" / "View N replies" buttons → no pagination fetch fired; verify the selectors fire a fetch. (Evidence B works: a `window.fetch` patch DID catch a 399 KB comment response once via Claude-in-Chrome right after clicking "View more comments" — so fetch-on-click works; the extension just needs the right buffer + reliable clicks.) **If a fixed dump is STILL empty → these threads are fully server-rendered; parse FB's inline JSON (e.g. RelayPrefetchedStreamCache `<script>` blobs) or fall back to exhaustive DOM expansion.**
2. Once a non-empty dump exists: analyze that JSON locally → build a parser (comments + nested replies + author + time + post body from the GraphQL).
3. Rewire `captureConversations` to capture GraphQL + parse (instead of the DOM scrape). Re-validate completeness against the 16-comment post.
4. THEN load the real backfill + build the n8n load/search workflows.

**Still solid (unchanged):** Supabase `scorecard` schema (`fb_posts`/`fb_comments` + pgvector); **idempotent upsert/dedup PROVEN** (criterion 2); **full-text search retrieval PROVEN** (criterion 3 retrieval). **NOT loaded with real data yet** (capture incomplete). The DOM-based "Capture Conversations" button (≤v0.16) exists but **under-captures — do not trust its output.**

**Key facts for B:** comment GraphQL fires on pagination clicks (initial comments are server-rendered → no fetch); unique comment id = `reply_comment_id || comment_id`; a reply's `comment_id` = its parent thread id; `cap_inject.js` (document_start MAIN-world fetch patch) is registered; Supabase writes go through the supabase MCP (project = the Video-Platform/mds-ai-bot one, `scorecard` schema).

* * *

---

## 2026-06-19 (Scorecard scoring, session 11) — FB conversation digest: Phase 1 (capture) + Phase 2 (Supabase store) BUILT + verified

> Building the FB conversation digest (open Q#3; feasibility proven s10). Goal (Andy): a weekly "who said what" digest **+** a cumulative, **searchable knowledge base** (FB now; WhatsApp/videos later) powering a member portal — that's why Supabase. Source of truth = ClickUp `2531q-100317`. Capture code = `mds-scorecard-tools/extension/`.

**Phase 1 — capture (DONE, extension v0.12):** new **"Capture Conversations"** button (manual/standalone; NOT on the weekly alarm yet). `captureConversations()`: opens the group feed (RECENT_ACTIVITY) → collects recent post ids (cap 25; 6 for testing) → per post `chrome.tabs.update` → permalink → `capturePostMain` (MAIN world) → `mds_feed.json` in Downloads. Incremental save to `chrome.storage` + per-post **60s timeout** (a hang can't lose the run or stall it).
- **Key finding:** FB renders comments **server-side** on permalink pages — they do NOT traverse `window.fetch`, so GraphQL interception (`cap_inject.js`) can't catch them there. Pivoted to **DOM extraction via aria-labels**: each comment is a `[role="article"]` whose aria reads `"Comment by X <time>"` / `"Reply by X to Y's comment <time>"` → type + author + parent; text via `dir="auto"`; uid via profile link; `commentId` via comment permalink. **Deduped** (FB renders the thread 2×). Relative times → ISO.
- Output per post: `{postId, permalink, text, hashtags[], comments:[{commentId, type, author, authorUid, parentAuthor, text, time, rawAria}]}`. Verified clean on the live group (names, threading, `#ValueAdd`, full post text, timestamps).
- **Known gap:** post **author + timestamp** still null (the post itself has no aria-label like comments do) — source from the feed/permalink header next pass.

**Phase 2 — Supabase store (DONE):** Andy chose **existing project (the mds-ai-bot / Video-Platform Supabase), separate `scorecard` schema** — co-located with the video transcripts so search can span FB + transcripts (the future cross-activity KB). Tables `scorecard.fb_posts` + `scorecard.fb_comments` (PK postId/commentId; `created_time`; pgvector `embedding` cols for later semantic search; RLS on). Loaded the first `mds_feed.json` via the Supabase MCP (idempotent upsert; dollar-quoted JSON → temp table → `jsonb` unnest).

**Success criteria status (Andy's):** (1) **7-day backfill ✅** loaded. (2) **Monday no-dupes ✅ PROVEN** — re-sent an existing post+comment → posts stayed 6, only the new comment added (upsert on postId/commentId). (3) **search via Anthropic ⏳** — retrieval proven (Postgres full-text, ranked); Claude-answer + n8n wrapper next. (4) **all-tested-in-n8n ⏳** pending.

**Architecture for the rest:** capture local → POST `mds_feed.json` to an **n8n webhook** → n8n upserts to Supabase (in-n8n ✓). **Search** = n8n workflow: query → Supabase retrieve (full-text now, Voyage/vector later) → **Claude** answer w/ citations. Future: member portal reads the same Supabase, cross-searching WA + FB + videos.
- **Gating dep:** a **Supabase Postgres credential in n8n** (Andy adding it) — needed to build/test the n8n load + search workflows. Anthropic cred already in n8n (lead-enrichment).

**Next:** (a) Andy adds the n8n Supabase cred. (b) build + test the n8n load webhook + search workflow. (c) fix post author/timestamp + wire local capture → webhook. (d) Phase 3: embeddings + weekly Claude digest + portal.

* * *

---

## 2026-06-18 (Scorecard scoring, session 10) — verified Mon-6/22 readiness · FIXED layer-sync cron drift (was firing 1:00, not 1:30/1:40/1:50) · scheduled 6/22 verify · FB conversation digest = feasibility PROVEN (GraphQL interception)

> The **Scorecard scoring** project (source of truth = ClickUp doc `2531q-100317`). This session was verification + one fix + a feasibility probe — no code shipped to the repo; the fix is in n8n, and the FB-digest build plan is logged on CU page 7.

**Verification — the s9 weekly cycle, against LIVE systems.** The first run on the new schedule is **Mon 2026-06-22** (a *future* run — can't be verified yet; verified the system is *configured* for it instead). Live state confirmed: spine `tblbmLb5D1kVpuJD1` = **1,295**; FB Engagement (NEW) = **759**; **720** spine rows have the `Member ID (FB)` lookup resolved; the 13 s9-onboarded members are on the spine scored **0** (deferred — will populate Monday). `reconcile.py` **dry-run clean** (spine missing 0, 37 ghosts, 6 departed, 763 members linked). launchd `com.mds.scorecard.autoimport` loaded (WatchPaths ~/Downloads); extension **v0.9** weekly alarm + roster/Insights capture intact; `auto_import.py` correctly chains → `reconcile.py --apply`.

**🔧 FIXED a real drift — the 3 layer syncs were firing at 01:00, not the intended 1:30/1:40/1:50.** s9's reschedule **silently failed**: a malformed `interval[0]` sibling key left the published cron at `0 1 * * 1`. Execution history proved it (Events ran 06:00 UTC = 01:00 CT on 6/08 **and** 6/15) — and since the FB import lands ~01:07, the layer syncs were running **before** the data + spine growth every week. Fixed all three on the published graph via `updateNode` (clean single `interval`, dead key removed): **Events `uuXBxG6lqXCV9otJ` → `30 1 * * 1` (1:30)**, **WhatsApp `RPfnori7C26NcT9N` → `40 1 * * 1` (1:40)**, **Member Attributes `odfBrs6z9IxP7ndl` → `50 1 * * 1` (1:50)**; workflow titles corrected. Recompute `UCxyzY1RXzrIHtmX` was already correct at `30 2 * * 1` (2:30). (Node names still read "Mon 1am CST" internally — cosmetic.)

**Ghost→Slack:** wiring verified (test message posted as the bot to `#automation-tests` C0AQ8USNQK0). The real 37-ghost report **first posts Mon 6/22** — in s9 the `reconcile --apply` ran (21:47) *before* the Slack creds were added to config.json (22:04), so only `mds_ghosts.json` was written.

**Scheduled** a one-time cloud verification, **Mon 2026-06-22** (task `verify-scorecard-first-weekly-run`, fires ~08:00 local / 13:00 UTC, auto-disables): checks the capture+reconcile ran, the 3 syncs fired at the new times, the 2:30 recompute ran, the ghost report posted, and the 13 new members now score non-zero.

**FB conversation digest (Andy's open question #3) — feasibility PROVEN via live probe** (full plan + build on **CU page 7**). Verdict: **feasible**, via the **extension** (real session, weekly, paced — NOT Apify), using **passive GraphQL interception** (read FB's own `fetch`), not DOM scraping. Proof on the live group: MAIN-world access works (read `fb_dtsg`; `window.fetch` patchable) → intercepted FB's comment GraphQL (`doc_id 27201942402808991`) → **399 KB JSON, 29 comments**. Data model confirmed: **names** (author objects), **timestamps** (`created_time`), **comment text**, **replies**; **comment→post** via feedback id; **reply→comment** via parent/depth; **hashtags** (`#ValueAdd` ×6, in-text entity links). FB group "Topics" (+Add topic) field is separate and barely used here. Key robustness point: passive interception means the rotating `doc_id` never breaks us (only a JSON-schema change needs a parser tweak).

**Decisions:** layer syncs must run *after* the 1am capture+reconcile → restored the staggered cron (longer-term, chain via the existing per-workflow webhooks instead of fixed clock times — noted, not built). FB digest = extension + GraphQL interception over DOM scraping (clean JSON, no doc_id maintenance).

**Open / next:**
1. **Mon 6/22** — confirm the first live run (scheduled task will check; fix any drift).
2. **FB digest** — greenlight the build (capture component + Airtable table + n8n→Claude, cloned from the WA digest; plan on CU p7).
3. Still open: **laptop dependency** (#2) — independent/cloud capture so the 1am run doesn't need Andy's Mac awake.

* * *

---

## 2026-06-17 (Scorecard scoring, session 9) — FB-ID identity EXECUTED: id→live lookup + cross-base sync · weekly onboarding + ghosts + auto-recompute · syncs rescheduled

> The **Scorecard scoring** project (source of truth = ClickUp doc `2531q-100317`). Local tooling: `mds-scorecard-tools/` (extension, `auto_import.py`, `process_fb.py`, **`reconcile.py`**, `config.json` holds the Airtable PAT **+ Slack token**). No git commits this session — work is in `mds-scorecard-tools/` (not a git repo) + Airtable + n8n + the ClickUp doc (all 10 pages refreshed). Executed the s8 locked plan.

**Done this session:**
- **Identity → `Member ID (FB)` is now a LIVE LOOKUP on the Members DB, not a hand-kept field.** Pre-check: 0 references in 46 n8n workflows or local scripts (safe to rename). Renamed Members-DB `FB User ID` → `Member ID (FB)` (bootstrap key) → stood up a **cross-base sync** `FB Engagement (synced)` `tblnL4oFhFBgqGJDS` + Members link `fldnsHLeBjsShCL1k` + **lookup** `Member ID (FB)` `fldVq5CTU5nu3Yqnc` → then (per Andy) renamed the text field → `FB ID (match key)` and **DELETED** it. One clean lookup, auto-sourced from the scraper table. Same lookup on the spine `flddiHdh0xsbnm4N5`. **758 resolve.** ⛔ `Facebook Profile Link` `fldOMkijXdtTAWYoy` untouched.
- **`reconcile.py` (NEW)** — weekly via `auto_import.py --apply` after `process_fb`: **A** spine growth (1,282→**1,295**, the 13 incl. Ary Selener/George Dille) · **B** FB-roster completeness (`FB Engagement (NEW)` 750→**759**, all FB people; name-match a member only if unique + no existing FB row of that name → twins stay ghosts; +9 Member-link backfill) · **C** ghosts (blank `AT Database Status` AND not on spine = **37**) → `mds_ghosts.json` + **Slack `#automation-tests` `C0AQ8USNQK0`** (Centurion bot token, verified) · **D** link maintenance (match member ↔ synced FB row on `Facebook Profile Link`) · + joiner/leaver report + `mds_to_resolve.json`. **Chrome extension → v0.9** + "Resolve member FB IDs" tool.
- **Every datapoint + score, weekly.** Rescheduled cloud syncs after onboarding: Events `uuXBxG6lqXCV9otJ` **1:30**, WhatsApp `RPfnori7C26NcT9N` **1:40**, Member Attributes `odfBrs6z9IxP7ndl` **1:50** (Mon CST) + a webhook trigger each. New cron **`Score Recompute Trigger (Mon 2:30am)`** `UCxyzY1RXzrIHtmX` touches `Recompute Ping` `fldaRDlMIK3CDMuzR` → fires the existing recompute → all 1,295 rescore on fresh data (closes the config-edit-only gap). Verified: new member None→0; existing unchanged (Manol 32.9).

**Decisions / architecture:**
- **`Member ID (FB)` = a lookup, sourced from `FB Engagement (NEW)`** (Andy's model). Airtable can't do a *direct* cross-base lookup → use a synced table + link + `reconcile.py` matching. Text id field deleted (no hand-maintenance).
- **Ghost = blank status + NOT on spine** (an on-spine blank-status row is a real member missing its mirror link, not a ghost — 14 false-positives excluded/backfilled). Report-only, no auto-removal.
- **Recompute fires weekly (2:30am cloud cron)** in addition to on-config-edit. All cloud → laptop only needed ~1am for the FB capture.

**Open / next (2 new questions on CU page 7):**
1. **Eliminate the laptop dependency** — independent/cloud capture system (local server?) so the 1am FB capture doesn't rely on Andy's personal Mac.
2. **FB conversation digest** — expand the scraper to capture posts + threaded replies for a weekly "who said what" digest (like WhatsApp); no backfill; feasibility TBD (ban-risk).
- ⏸ Deferred: the *immediate* full data refresh for the 13 new members (scored 0 until Monday's syncs).
- ClickUp doc `2531q-100317` — **all 10 pages refreshed** this session.

* * *

---

## 2026-06-17 (Scorecard scoring) — Stripe lookups · FB pipeline audit (Mon 06-15 verified) · FB-ID identity plan LOCKED

> The **Scorecard scoring** project (source of truth = ClickUp doc `2531q-100317`; the Tools-Health entries below are a *different* project sharing this dir). Local tooling: `mds-scorecard-tools/` (extension, `auto_import.py`, `process_fb.py`, `config.json` holds the Airtable PAT).

**Done this session:**
- **Stripe context on the spine — 5 lookups** on `Member Scorecard (NEW)` via `Member` → `Members & Scorecard` mirror: Stripe Next Invoice Date / Product Name / Price Name / Subscription Status / ARR. Added those fields to the mirror's **sync source view** ("Sync to New Member ScoreCard", Members DB) + set that sync to **all-fields-in-view**. Source-tagged; informational, **not scored**.
- **FB pipeline audited end-to-end + Mon 06-15 verified.** extension (Mon 1am `chrome.alarms`) → roster + 28d Insights → `~/Downloads` → launchd `com.mds.scorecard.autoimport` (**WatchPaths on ~/Downloads — a file-watcher, NOT a timer**; the cadence is the extension alarm) → `auto_import.py` (lock + state idempotency + 48h stale-guard) → `process_fb.py` (overwrite engagement by name, append History; roster diff **flags** joiners/departed — never adds). 06-15: 96 contributors, FB Engagement 750 rows @ 06-15, +720 History, roster 753 / 9 joiners / 6 departed. 716 matched · 720 spine-linked · 34 ghosts.

**Findings / decisions:**
- **Two onboarding gaps:** (1) the spine doesn't auto-grow → recent MDS members unscored (George Dille 6/08, Ary Selener 6/11; 9 active missing); (2) new FB joiners flagged-not-added (incl. Tancredi Ingrassia). The FB↔MDS match was a one-time backfill (s2–s3), not weekly.
- **FB ID = the key.** Members-DB `FB User ID` is 93% filled (677/725 trackable), unique, and == scorecard `Member ID (FB)` 715/715. Caught a duplicate (Travis Reese). **"Trackable" = `Stripe Subscription Status` active/trialing (708, live)**, NOT "New Member" (sticky; oldest joined 7.7 yrs). 47 trackable w/o id: 28 vanity link · 2 numeric · 17 blank/"N/A".

**⏭ LOCKED PLAN (next session — NOT started):**
0. Pre-check nothing reads these fields by name in n8n/scripts.
1. Rename Members-DB `FB User ID` → **`Member ID (FB)`** + identical description (scorecard field keeps its name — `process_fb.py` reads it). ⛔ **never modify `Facebook Profile Link` `fldOMkijXdtTAWYoy`** (admin source-of-truth).
2. **Partial backfill — test subjects only:** (a) Chris Kjeldsen (has link, in group), (b) Justin Adams (link, not in group), (c) Cory Krehbiel ("N/A" link), (d) + a departed member + a numeric-link one.
3. Chrome-extension add-on to auto-capture/resolve a new member's FB id (numeric=extract; vanity=resolve via profile redirect; roster already gives uid+name).
4. Weekly roster↔members reconciliation: joiner → match+seed `Member ID (FB)`+add to scorecard; departed → flag left the group.
Goal: one verified FB id per member; catch joiners + leavers every week.

ClickUp updated: page 5 (FB pipeline + matching + gaps), page 6 (Game Plan = the locked plan), page 8 (this entry).

* * *

---

## 2026-06-05 (session 6) — Config-driven scoring REBUILT (Pillars + Attributes admin model) + per-pillar subscores + auto-recompute + Scoring Admin interface

**State at session end:** **Phase 1 (the admin tool) is functionally done + verified.** The Engagement Score is now **config-driven** — an admin edits plain-language tables (no formulas): **Scoring Pillars** (4 buckets: weight/cap + include) and **Scoring Attributes** (per-action points + optional cap + include). Editing either fires a **"When record updated" automation → Run-script** that recomputes every member's score, writes it to the spine, and now also writes **4 per-pillar subscores** + a human-readable breakdown. A **Scoring Admin interface** page holds 3 grids (Pillars + Attributes editable, Preview read-only/sorted). Verified live (scored 1,282 in ~20s). **Layout polish left to Andy** (3 freeform-canvas drags the browser automation can't do cleanly). **Weights are placeholders → Phase 2 = calibration (the big work).**

**Done**
- **Renamed table** `Scoring Signals (NEW)` → **`Scoring Attributes (NEW)`** `tbl8pN2A2pzq3v513`; fields **Signal→Attribute**, **Points per unit→Points / action**, **Cap (optional)→Cap** (via Meta API). Updated all 10 rows to friendly names + **Andy's points model**: FB **post 10 / comment 1 / reaction 0.5 (cap 20)**, WA **message 1 / active-channels 2**, **in-person 15 / virtual 10**; Recognition/Membership (MoM 25, profile 10, tenure 5) stay **Include=off ("needs data")**.
- **`Scoring Pillars (NEW)`** `tblvIKa52ZROfSedD`: renamed **Weight/Cap → Cap (max points)**; added **Explanation** (singleLineText) + **Attributes** (number count). Set explanations + counts (Social 5, Events 2, Recognition 1, Membership 2). Caps Social 50 / Events 30 / Recognition 10 / Membership 10 (=100).
- **Spine** `tblbmLb5D1kVpuJD1`: added **4 number fields (prec 1)** — `Social Score`, `Events Score`, `Recognition Score`, `Membership Score` (field ids fldu…/fldP…/fldp…/fldX…).
- **Recompute script REWRITTEN** (config-driven): reads Pillars + Attributes, per attribute = `count × points` capped at the attribute `Cap`, summed per pillar, capped at the pillar `Cap`; writes `Engagement Score` + `Score Breakdown` + the 4 subscores. Source in `/Users/Born/mds-scorecard-tools/recompute_script.js`.
- **Two auto-recompute automations LIVE + applied** (same script in each): **"Recompute Engagement Score"** `wfltDzQ0oZq3JvbnE` (trigger = Scoring Pillars updated) + **"Recompute Engagement Score copy"** `wfll84GogQazgf2DM` (trigger = Scoring Attributes updated). Both tested "ran successfully", scored 1,282.
- **Scoring Admin interface** page `pag0fxWK6jgyeVO1p`: 3 grids, correct columns, live data — **Pillars** (editable, widened so all 5 cols fit): Pillar·Explanation·Attributes·Cap (max points)·Include; **Attributes** (editable): Attribute·Pillar·Points / action·Cap·Include; **Preview** (read-only, sorted by Engagement Score desc, trimmed ~10 rows): Member·Social·Events·Recognition·Membership·Engagement Score. Dead standalone "Recompute" button removed.

**Decisions / findings**
- **Admin model = points-per-action is the lever** (Andy: window was the wrong lever + inaccurate). Caps at **both** levels (pillar + attribute) + on/off toggles. **Window demoted** to a fixed per-attribute data property (kept as a hidden `Window` field, not surfaced/editable).
- **Exclude an attribute** = flip its **Include/On** toggle (keeps the points value) — not zero it out.
- **Per-pillar subscores stored on the spine** (4 fields) to power the Preview breakdown.
- **No trigger loop:** the script writes **only to the spine** (never back to Pillars/Attributes); attribute counts are static, not script-written.
- **🚧 SATURATION (Phase-2 signal):** placeholder weights make the top **tie at 80** (Social capped 50 + Events capped 30; Recognition/Membership 0 = no data). The score doesn't separate the top yet → must calibrate.
- **Interface = freeform canvas:** programmatic block-move/rename detaches into a "click-to-place" mode that can't be targeted reliably → **preview→bottom, 3 section labels, page rename** left for Andy (~10s each, manual). I backed out every drag to protect the working grids.
- **Engine is usable now without the interface** — edit a Cap/Points in the **Data** tab → recompute in ~10–20s.
- **Members-DB push (deferred):** use the existing record-matching across tables, **not n8n** (Andy's call from session reframe).

**Next steps**
1. **Andy — finish interface layout** (Scoring Admin draft): drag Preview block to the bottom, add 3 Text section labels, rename the "Untitled" page, then **Publish**. Optionally turn **off** "Allow users to add/delete records inline" on the two config grids (prevents accidental pillar/attribute deletion).
2. **PHASE 2 — calibration (the big work, weights NOT agreed):** use buckets **New / Current-tenured / Churned**; profile **zero-score tenured** members (≈44% of spine had 0 under the prior model); raise caps / retune points so the leaderboard separates; calibrate against **churn** (score at week-of-cancel). Be data-driven — only score what we actually have/can get (app/read data does **not** exist).
3. ⏰ **Mon 2026-06-08** — verify the 3 scheduled syncs ran (WA `RPfnori7C26NcT9N`, Events `uuXBxG6lqXCV9otJ`, FB capture+import) — carryover from sessions 4/5.

**Key IDs (this session)**
- Scorecard base `appUM1F29IJsMsXRb`: **Scoring Pillars (NEW)** `tblvIKa52ZROfSedD`, **Scoring Attributes (NEW)** `tbl8pN2A2pzq3v513`, spine `tblbmLb5D1kVpuJD1`.
- Automations: `wfltDzQ0oZq3JvbnE` (Pillars-trigger) + `wfll84GogQazgf2DM` (Attributes-trigger). Interface page `pag0fxWK6jgyeVO1p`.
- Script source: `/Users/Born/mds-scorecard-tools/recompute_script.js`. Admin-UI mockup (local, served on :8765): `/Users/Born/mds-scorecard-tools/scoring-admin-mockup.html`.

---

---

## 2026-06-05 (session 5) — WhatsApp layer (NEW) built + field-doc hygiene + PAT leak closed

**State at session end:** The **WhatsApp engagement layer is live** — `WhatsApp (NEW)` table (one row/member: Posts + Channels-Active over 7/30/90d, Channels Registered, Tier, Last Active, Updated stamp), refreshed weekly by a new n8n sync (**active**, first scheduled run Mon 2026-06-08 1am CST), and **surfaced on the spine** as lookups. Sourced **only from the MDS WhatsApp DB** (not the Members DB). All 5 NEW Scorecard tables now carry **field descriptions stating the datasource**. The **public-leaderboard PAT leak is closed** (Andy revoked the over-scoped "scorecard" token).

**Done**
- **`WhatsApp (NEW)`** `tbllZ4REuRYkuVyri` (Scorecard base) — per-member **Posts 7/30/90d**, **Channels Active 7/30/90d**, **Channels Registered**, **Tier**, **Last Active**, `Members DB` deep-link, `Updated (WhatsApp)`. 1,282 rows.
- **n8n "MDS Scorecard - WhatsApp Sync (Mon 1am CST)"** `RPfnori7C26NcT9N` — reads spine + MDS WhatsApp DB (Member Stats + DailyActivity + Members) → upserts WhatsApp (NEW), matched to spine by MDS record-id. **ACTIVE** (cron `0 1 * * 1`, America/Chicago; first run Mon 2026-06-08). Validated end-to-end via a temp webhook (since removed).
- **Sourcing (Andy's correction — don't recompute what exists):** 7d/30d Posts + Channels-Active + Tier + Last Active are **copied verbatim** from **Member Stats** (`tblJn5aftV1wSGQ7v`, maintained daily by the existing `MDS WA - Daily Stats Builder` `1VDbwlQqXcfbotic`); **only 90d** is derived from **DailyActivity** (`tblikCGQmNqNrhNJs`) since no 90d is pre-computed anywhere; **Channels Registered** = `Members.channels_count`.
- **Spine surfaced:** added the WA fields to `Member Scorecard (NEW)` as **lookups via the new `WhatsApp (NEW)` link** (done in the Airtable UI by browser automation — API can't create lookups): Posts 7/30/90, Channels Active 7/30/90, Channels Registered, Updated (WhatsApp).
- **Validation:** 1,282 rows; **0 invariant violations** (7d≤30d≤90d, Active≤Registered); **20/20** top posters match Member Stats exactly; **20/20** match an independent DailyActivity 90d recompute; Σ Posts 30d (matched) = 2,294 vs Org Stats 2,737 (lower = matched-members-only, correct).
- **Field-doc hygiene:** wrote **51 field descriptions** (each stating the datasource) across all 5 NEW tables → 0 missing.
- **Security — PAT leak CLOSED:** the public `index.html` embedded the read-only "scorecard" PAT (`patg5Hbe6RM5QjZbt`) scoped to **All workspaces and bases** → any visitor could read member PII across Member ScoreCard + MDS Member DB + WhatsApp DB via view-source. **Andy revoked the token** (kills the live page + the git-history copies). Dead POC page can be stripped/taken-down later.

**Decisions / findings**
- **WA windows = 7d / 30d / 90d** (Andy chose, incl. 90d). 90d reads low until ~2026-07-22 (per-member history starts 2026-04-23) → noted in the field description.
- **"Members present + active" = per-member channel breadth** (Registered = subscribed; Active = posted-in), not org totals.
- **Thin n8n transport is justified** (vs native Airtable sync): cross-base + spine keys on MDS-rec-id while WA keys on phone (needs a join) + combine two WA tables + derive 90d. It does NOT recompute 7/30.
- **🚧 Wrong-attribution (deferred):** spine "Elan Klaristenfeld" carries Eugene Khayman's WA numbers — bad `source_member_id` in WA `Members` (same Eugene/Yevgeniy dup-record class as the Events undercount). 1 genuine of 399 matched; logged to Known Issues.
- **Unused fields:** `Reactions 30d/90d (WA)` + `Channel Breakdown 30d (WA)` are reserved/empty (scoped out) — removable in the UI (API can't delete fields).

**Next steps**
1. ⏰ **Mon 2026-06-08 — verify all THREE scheduled runs:** WA sync (`RPfnori7C26NcT9N`), Events sync (`uuXBxG6lqXCV9otJ`), FB capture+import. Confirm `Updated` stamps = 06-08.
2. **Rubric / weights (#5)** — NEXT: all 3 engagement pillars (FB + Events + WhatsApp) now on the spine → config-driven weights → one score → push to Members DB. Calibrate with churn (#6).
3. Optional cleanup: strip `index.html` / disable GitHub Pages (POC retired); delete the unused WA fields in the UI.

**Key IDs (this session)**
- Scorecard base `appUM1F29IJsMsXRb`: **WhatsApp (NEW)** `tbllZ4REuRYkuVyri`, spine `tblbmLb5D1kVpuJD1`.
- MDS WhatsApp DB `appT9TVZWhv7io4CN`: **Member Stats** `tblJn5aftV1wSGQ7v`, **DailyActivity** `tblikCGQmNqNrhNJs`, **Members** `tbli8B589iNbsGF0Z` (maintained by `1VDbwlQqXcfbotic`, daily 9:30am ET).
- n8n WA sync `RPfnori7C26NcT9N` (cron `0 1 * * 1`, TZ America/Chicago).
- Revoked leaked token: "scorecard" `patg5Hbe6RM5QjZbt` (read-only, All workspaces/bases).

---

---

## 2026-06-05 (session 4) — Events layer built (Events NEW + n8n) + dedup bug fixed + validated vs roster

**State at session end:** The **Events layer is live** — `Events (NEW)` table (one row/member: In-Person + Virtual counts over 12/6/3/1 mo, live AT status lookup, Member link, Updated date), refreshed weekly by an n8n sync (**now live** — first run Mon 2026-06-08 1am CST). The 8 counts are surfaced on the spine via lookups; Events (NEW) also carries per-member event lists + a Members DB deep-link. A **dedup bug** (counting duplicate roster rows) was found + fixed → distinct-event counts. **Validated: 45/46 members with 10+ in-person (12mo) match the Event Roster exactly**; the 1 miss is a duplicate-member-record undercount, logged for later.

**Done**
- **`Events (NEW)`** `tblUxgYPMgaXOnS9k` (Scorecard base) — per-member In-Person/Virtual 12/6/3/1mo, live `AT Database Status` lookup, `Member` link → spine, `Updated` date. 1,282 rows.
- **n8n "MDS Scorecard - Events Sync (Mon 1am CST)"** `uuXBxG6lqXCV9otJ` — reads spine + Event Roster (12mo) + virtual links + Events dim → computes in-person/virtual split → **upserts** (PATCH existing + POST new joiners). Validated (0 errors), tested end-to-end. **ACTIVE** (activated this session; first scheduled run Mon 2026-06-08 1am CST). Also writes per-member **event lists** + a **Members DB** deep-link. Not the Mac mini — n8n is the mechanism.
- **Events (NEW) spot-check fields:** `In-Person Events` + `Virtual Events` (newline list of `date — event`, last 12mo → list length = the 12mo count; **rich-text fields — each entry is a clickable link to that event's roster record**, event-record fallback for virtual-attendance-only) + `Members DB` (URL deep-link to the member's Members-DB record, like the FB table). n8n maintains them weekly (markdown links).
- **Spine surfaced:** added the **8 in-person/virtual count fields** to `Member Scorecard (NEW)` as **live lookups** (through the Events (NEW) link, via the Airtable UI — API can't create lookups). Values nest correctly + match Events (NEW).
- **In-person/virtual rule:** `Events.Type == "In Person"` → in-person; else (incl. empty) → virtual.
- **Dedup fix:** count **distinct events** (dedupe by `Match to Event`), not roster rows.
- **Windows past-only** (Event Start Date ≤ today); future registrations excluded.
- **Validation harness** (Python): per-member roster recompute (distinct, in-person, past) vs the table → 45/46 exact.

**Decisions / findings**
- **Dedup was the bug:** roster has duplicate registration rows (Max 25 rows → 14 events; group-wide 6,719 rows → 3,546 distinct member+event pairs; worst 39 rows on one event).
- **Past-only windowing** is correct: future-dated registrations can't be "attended" and would break window nesting (a future event would also land in the 1-mo bucket). Explains Brandon's "20 (mine) vs 24 (roster, incl. 4 future)".
- **Registration-based metric:** `Check-in` ~84% blank → can't use attendance. Broad-RSVPers inflate (Max = 9 chapters' Holiday parties, same-day across cities). Optional guard: collapse same-day registrations across different chapters.
- **NY chapter cadence = 1–2/month (max 2, never 3)** across 5-yr history; high per-member totals come from breadth (chapter + summits + Operator Rooms + conference socials).
- **🚧 Duplicate member records (deferred):** events split across alias records → undercount. Eugene Khayman (`rec8JRXh66EOZ2835`, 13 ev) vs spine's "Yevgeniy Khayman" (`recvS…`). ~25 spine members affected; ~291 orphan roster names are out-of-scope. Logged → Known Issues. Andy: cover later (merge at source vs aggregate aliases).

**Next steps**
1. ⏰ **Mon 2026-06-08 — verify BOTH first scheduled runs:** (a) Events n8n sync (`uuXBxG6lqXCV9otJ`, 1am CST) refreshed Events (NEW) + the spine lookups; (b) FB capture (extension) + `process_fb.py` import refreshed FB Engagement (NEW).
2. Andy: decide **dup-record handling** (merge at source vs aggregate aliases — see Known Issues).
3. WhatsApp layer; rubric/weights; churn analysis.

**Key IDs (this session)**
- Scorecard base `appUM1F29IJsMsXRb`: **Events (NEW)** `tblUxgYPMgaXOnS9k`, spine **Member Scorecard (NEW)** `tblbmLb5D1kVpuJD1`.
- Members DB `appou5JVr0WIrioWS`: **Event Roster** `tblfTLRfAqBhBZlc4` (`Match to Member`, `Match to Event`, `Event Start Date`, `Order Date`), **Events** dim `tblbDtU6DxpoeZF8i` (`Type`, `Start Date`, `Event ID`, `Chapter`).
- n8n workflow `uuXBxG6lqXCV9otJ` (cron `0 1 * * 1`, TZ America/Chicago). Validation tooling in `/Users/Born/mds-scorecard-tools/`.

---

---

## 2026-06-04 (session 3) — FB capture autopilot (Chrome extension v0.8) + Events-field verification

**State at session end:** FB capture is now a **one-button + scheduled Chrome extension** (`mds-scorecard-tools/extension/`) running in Andy's own logged-in Chrome — roster + 28-day Insights export, both verified end-to-end. **`process_fb.py`** turns the two downloads into Airtable updates. Events layer (#3) scoped: the DB's pre-built event fields were **verified untrustworthy** → build from clean primitives.

**Done**
- **Chrome extension (autopilot piece) — v0.8, MV3** in `mds-scorecard-tools/extension/`:
  - **Capture roster** — scrolls `/members`, harvests uid+name → `mds_roster_full.json`. Verified 757 (byte-identical to the manual scrape).
  - **Capture Insights** — opens Insights, drives the **Download dialog**, saves the 28-day `.xlsx`. Verified end-to-end.
  - **Stop** (cancels mid-run; reads the tab from storage → survives MV3 worker restarts), **adjustable weekly schedule** (any day/time, machine-local TZ), **version badge** (reload verifier), **Open Downloads** link.
  - **PAT stays in the local `process_fb.py` + `config.json` — never the extension** (same posture as the index.html leak).
- **`process_fb.py`** — reusable weekly processor: A) overwrite `FB Engagement (NEW)` from the Insights **Contributors** sheet + set Reporting Date, append a dated 28d snapshot to `FB Engagement History (NEW)` (idempotent); B) roster diff vs known FB IDs → joiners / departed; C) summary.

**Decisions / findings**
- **FB Insights Download is a DIALOG, not a straight download** (earlier assumption corrected). Modal = Date range (default Last 28d ✓), Format (Excel ✓), category checkboxes: **Growth** (default; group-level "Daily numbers" only), **Engagement**, **Members** (=Top contributors), **Admins**, **All**. The per-member **Contributors** sheet the processor reads needs **Members/Engagement (or All)** ticked → extension ticks **All**. The checkboxes render a beat AFTER the dialog → must wait for the checkbox element before ticking (this was the bug that produced a Growth-only file).
- **Event "Registered…" fields are mostly untrustworthy** (verified vs real roster rows; full table in CU Known Issues): the two "within 12 months" twins disagree; "MULTIPLE" rollups sit on `Event Type` which is uniformly "In Person"; the "Virtual" field measures attendance not registration; "Chapter Events Registered" returns ALL events. **Build the Events layer from clean primitives:** `Order Date`, `Event Start Date`, `Check-in` (attendance = the real signal), `Event Chapter`.

**Lessons**
- **MV3 service workers only refresh on a full Remove + Load unpacked** — ↻ frequently keeps the OLD worker, so new message actions silently no-op. Cost several confused rounds. Mitigation: in-popup **version badge** = at-a-glance proof the new code loaded.
- **Chrome popups always close when a tab takes focus** → can't keep the popup open during capture. Fix = **Side Panel** (next).
- FB heavy pages freeze `javascript_tool` (CDP timeouts) under repeated modal interaction — verify on a fresh tab, keep injected scripts short.

**Next steps**
1. **Build the Events layer (#3)** from the clean primitives (link + attendance/registration rollups onto the spine, like the FB layer).
2. **Side Panel** conversion (persistent UI + visible Stop during capture).
3. Side: `process_fb.py` auto-find the latest Insights xlsx in Downloads (for an unattended Mac-mini cron).

**Key IDs (this session)**
- Star schema (base `appou5JVr0WIrioWS`): **Event Roster** `tblfTLRfAqBhBZlc4` (fact), **Events** `tblbDtU6DxpoeZF8i` (dim). Master member link `Website Event Registration - In Person` `fldG234qZdfAMlyS4` (inverse `Match to Member` `fldgcQ9q7erpDNFqn`). Clean Event Roster primitives: `Order Date` `fldncG8l0iwnnvSAx`, `Event Start Date` `fldQYXisJRdaXr4Zt`, `Check-in` `fld4aIgiVMdT6M97S`, `Event Chapter` `fldsERiDFNvAXjeXC`; `Event Type` `fldYCdRzAgiLYUqmr` (uniformly "In Person" — unreliable).
- Tooling at `/Users/Born/mds-scorecard-tools/` (config.json has the PAT; extension/ is MV3 v0.8).

---

---

## 2026-06-03 (session 2) — FB roster captured (own-browser), table → FB-roster model, vanity backfill

**State at session end:** `Member Engagement (NEW)` is now a clean **FB-roster-driven** table — **749 rows = the live FB group members**, each with Member ID (FB) + Group/Personal Profile URLs + Profile Name. **746/749 now carry `Vanity URL (FB)`** (the field that lets us match to the Members DB). 95 rows have engagement (Insights 28-day). **FB ↔ Members-DB matching is NOT done yet** — that's the next step, and it's now unblocked.

**Done**
- **Engagement backfill (Plan B):** loaded FB Group Insights "Contributors (last 28d)" → Posts / Comments / Reactions onto 95 rows (matched by name; Insights "Likes" → our `Reactions`; 28-day window). Remaining ~650 members = 0 for that window. Source file: `~/Downloads/Facebook_Group_Insights_6-03-2026.xlsx`.
- **FB roster — the unblock.** Built an **own-browser console snippet** (scrolls `/members`, reads each member's userId + group + personal URL) that Andy runs in his real logged-in session. Pulled the full roster (~745–757) with **0 ban risk** — beats the parked Apify scraper (capped ~390 and kept getting the FB session killed). This is the FB-data method going forward.
- **Re-modeled the table to FB-roster-driven** (Andy's correction): the table holds **everyone in FB** (incl. ex-members / ghosts / staff) as a backfill, then matches to the Members DB for status — it is NOT seeded from the DB-member set. Wiped + rebuilt clean to **749** (v2 roster − page account − Andy's 2 accounts − 4 dup accounts).
- **Added `Vanity URL (FB)` field** (`fldGFl0Qec4HyOen0`) and populated it. Resolved each member's numeric FB URL → canonical **vanity** by following the profile redirect in-browser (e.g. `…/user/700320640/` → `facebook.com/jared.mortensen`). 757 resolved, 0 blocks. **746/749 populated** (the ~3 blanks are numeric-only profiles with no custom handle — they match by ID).

**Decisions**
- **Matching method (DECIDED):** match Members-DB field **`fldOMkijXdtTAWYoy`** (FB Profile Link — *source of truth*) against **3 roster fields**: `Member ID (FB)` (covers the DB's numeric + group-URL forms) **+** `Vanity URL (FB)` (covers the ~632 vanity DB links). DB link breakdown for the 703 members: **632 vanity / 56 numeric (53 profile.php + 3 group-url) / 15 junk-or-empty**.
- **"Normalize" ≠ "convert".** A numeric URL cannot be turned into a vanity by string ops — it requires *resolving* the live profile. Hence the resolve step + storing vanity as a **3rd** field. Keep the numeric URL too: the **ID is permanent, the vanity can change** when a member renames.
- **FB scraping posture:** own-browser console snippet (Andy's session, paced) is the path. Apify cloud and a local curl-with-cookies script are higher ban-risk and were rejected.

**Tooling lessons (cost real time — read before the next browser-data session)**
- **Browser → Airtable export is brutal.** Programmatic downloads get blocked (Chrome flips facebook.com to "block" after repeated auto-downloads); clipboard-write is blocked for automation ("document not focused"); `pbpaste` reads Andy's clipboard but needs his manual `copy()`; reading Chrome localStorage off disk is flaky (memtable flush timing + LevelDB 32 KB block-framing on large values). **What finally worked: render the data into the page DOM, strip the page down to just that, and read it with `get_page_text` (50 K-char limit) — this bypasses the `javascript_tool` ~1 KB output truncation.** Use this for any bulk browser→tool transfer.
- **DATA-LOSS incident (my error):** reloaded the FB tab while ~300 resolved vanities lived only in `window.__van` (volatile) → lost them. **Never reload / hold volatile — save to Airtable incrementally and prove the save before resolving more.**

**Next steps (specific)**
1. **Run the match** (unblocked): pull `fldOMkijXdtTAWYoy` + `AT Database Status` from the Members DB; normalize each DB link to a numeric-ID-or-vanity-slug key; compare to roster `Member ID (FB)` / `Vanity URL (FB)`; set the `Member` link + copy `AT Database Status`. Output 3 buckets: **matched · FB-not-in-DB** (ghost/staff) **· DB-not-in-FB** (invite list).
2. After matching: event-rosters layer → config-driven score → push score to Members DB.
3. Still open from session 1: public site security — kill the hardcoded Airtable PAT in `index.html`.

**Key IDs (this session)**
- Table `tblVc38gw21iHLYMG` (base `appUM1F29IJsMsXRb`) — 749 rows · new field `Vanity URL (FB)` `fldGFl0Qec4HyOen0` · other fields: Member ID (FB) `fld7r4Bi48MAuuABY`, Group Profile URL (FB) `fldYP6h4nvvcmTKKM`, Personal Profile Link (FB) `fldkuMYAxOloZqAe2`, Posts/Comments/Reactions 30d `fldD1RbOnpWLtRJZZ`/`fldgS0LgXNRup90dX`/`fldl5Z3q3xoqzwQOR`
- Members DB match field `fldOMkijXdtTAWYoy` (FB Profile Link, source of truth) in `appou5JVr0WIrioWS/tblfwOSROSHfuYUxv`

---

---

## 2026-06-03 — Audit, new Airtable table + 703 backfill, scraper rebuild, Plan B (Insights export)

**Context:** the scorecard data pipeline died ~April 2026. Full audit + rebuild kickoff.

**Done**
- Wrote `SCORECARD_AUDIT.md` (full system audit). Flagged `CLAUDE.md` as stale (it describes a dead Apify design; the live system reads Airtable).
- New Airtable table **`Member Engagement (NEW)`** (`tblVc38gw21iHLYMG`, base `appUM1F29IJsMsXRb`): source-tagged fields, `Member` link → synced members mirror `tblbN6JVeSk2XoPst`, `MDS Member URL`, `AT Database Status`.
- **Backfilled all 703 members** (607 Member IDs, 692 personal URLs, 703 AT status). IDs from the legacy weekly-metrics table + the Members-DB CSV; `userId` = canonical key.
- Scraper rebuild in `scraper/` (Apify actor `sSX1L7hnaohLSWTdB`, build 0.0.59): added Phase 0 member-discovery, `useResidentialProxy` flag, 3-hr handler timeout. **BLOCKED** — FB session dies within ~1 run even with residential proxy; FB security + password change killed it. Parked as best-effort.

**Decisions**
- Rebuild the score **config-driven** (Social / Events / Recognition / Membership; base = social+events; weights data-calibrated). Retire `Member's score NEW`.
- Matching must be **AT-native + daily**, keyed on personal/group URLs.
- **FB engagement:** Plan A scraper = best-effort/parked (high ban risk; Groups API dead 2024; 2025 mass admin bans). **Plan B = native FB Group Insights xlsx export** (Contributors sheet = per-member posts/comments/likes) = compliant primary source.

**Next**
- Backfill engagement from the weekly Insights export; SOP + Chrome-extension bot to auto-export.
- Finalize scoring + churn signal; run active-vs-canceled analysis for weights.
- Wire the AT-native match; add Events + WhatsApp (Whapi) layers; push score → Members DB.
- Public site: remove the hardcoded Airtable PAT, make it members-only, fix `CLAUDE.md`.

**Key IDs**
- Scorecard base `appUM1F29IJsMsXRb` · new table `tblVc38gw21iHLYMG` · synced members mirror `tblbN6JVeSk2XoPst`
- MDS Members DB `appou5JVr0WIrioWS` / `tblfwOSROSHfuYUxv` · status field `fldVd9OZHWKZhWIua`
- Apify actor `sSX1L7hnaohLSWTdB` (account `comfortable_meal`)
- ClickUp project doc `2531q-100317` · original task `86dxz1akn` · scraper guide doc `2531q-86017`
