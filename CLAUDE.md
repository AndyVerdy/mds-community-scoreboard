> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.
- **Always show a ticket's STORY + ACs. Closing needs: short results · short AC checklist (met/not) · before/after numbers.** (Andy 2026-08-03)


# MDS Community Scoreboard

> ⚠️ **STATUS (June 2026): mid-rebuild — much of this file below is LEGACY** and describes the old Apify-scraper design that is no longer how the system works.
> - **Source of truth:** ClickUp doc **"MDS Member Scorecard"** (`2531q-100317`, Tech space).
> - **Technical audit:** `SCORECARD_AUDIT.md` · **Session log:** `SESSION_LOG.md`
> - **Current reality:** the leaderboard reads **Airtable** (base `appUM1F29IJsMsXRb`), not Apify. The FB scraper is **parked** (high ban risk); FB engagement now comes from the **native FB Group Insights xlsx export** (Plan B). The score is being **rebuilt config-driven**. Treat the Apify + scoring-formula details below as historical until this file is rewritten.

---

# 🔄 SESSION PROTOCOL — follow every session

**This folder is a MULTI-PROJECT MDS working directory** — it holds docs/scripts for many separate
initiatives: **Census · GroupOS · Application v3 · Olivia · MRR · TikTok · Singapore · Member360 · WA
digest · Tools-health · the Scorecard leaderboard** (`index.html`), and more. **Do not assume any one
project.** Each project has its **own handoff + working docs**. Session logs are SPLIT (2026-07-30):
full entries go to the **stream log** (`SESSION_LOG_OLIVIA.md` · `SESSION_LOG_SCORECARD.md` ·
`SESSION_LOG_MISC.md`) and **one index line** goes to `SESSION_LOG.md` (chronological cross-project
index on top; frozen archive below). Auto-memory index: `MEMORY.md`, loaded every session. **Canonical = this repo; if the repo and ClickUp disagree, the repo wins.**

## OPEN — at the start of every session
1. The `SessionStart` hook injects the recent `SESSION_LOG.md` tail; the memory index is already loaded.
   From the user's first ask, **identify WHICH project** this session is about — never default to one.
2. **Read that project's handoff/docs** (e.g. `OLIVIA_NEXT_SESSION.md` for Olivia; the `CENSUS_*` /
   `GROUPOS_*` / `APPLICATION_V3_*` / etc. docs for those) plus its memory entry.
3. **VERIFY against LIVE before any new work — never trust the docs alone.** Check the systems that
   project actually touches (its n8n workflow / Supabase / Airtable / API / gate). **If the docs disagree
   with live, FIX the drift THIS session** before new work — a doc can't stay wrong for more than one session.

## CLOSE — before ending (the `Stop` hook reminds once)
Update the docs for **whatever project(s) you worked on** — do NOT claim "done" until the repo reflects what shipped + was verified:
1. **Stream log + index** — prepend the full dated entry (which project, what shipped — commit hashes /
   migration names / IDs, what was verified — exec id / gate green / SQL result, what's next) to the
   project's `SESSION_LOG_<STREAM>.md`, and ONE line to the `SESSION_LOG.md` index.
2. **That project's handoff + working docs** — refresh state + next actions.
3. **Auto-memory** — only durable cross-session facts.
4. **ClickUp** (that project's doc) — decisions + high-level state only.

## How Andy wants answers
**Short and simple — 1–4 paragraphs. Not too short, not too long** (his exact words, reinforced hard
2026-07-28: "OMG stop spamming" after over-explaining). Not one-liners, not walls of text. Lead with the
answer; **he asks for details when he wants them** — do not pre-emptively expand. No option menus, no restating the question, no
re-explaining what was already said. Tables/short lists beat prose for status.
Same rule for docs he reads: keep the human-facing doc short, put depth in a `*_DETAIL.md` or
`SESSION_LOG.md`. Brevity never means dropping a real risk or a wrong result — say it in a sentence.
See memory `feedback_short_answers`.

## Non-negotiables
- Every "it works" claim cites a live check (exec id, gate green, SQL/curl result) — never "should work."
- For any gated/data change, its safety gate must be GREEN before ship (e.g. Olivia = `scripts/olivia_leak_gate.py`).
- n8n edits: edit the ACTIVE workflow, then ONE `[{deactivateWorkflow},{activateWorkflow}]` bounce — never deactivate first.
- Keep separate repos separate (e.g. `mds-ai-bot`, `mds-digest-web` are their own folders — never edit one while working another).

---

## What this is
A gamified member-engagement scorecard + public leaderboard for the MDS Facebook group (plus first-party signals: events, MDS app, WhatsApp). Hosted on GitHub Pages (`index.html`).

## Stack
- Single-file vanilla HTML/CSS/JS (`index.html`) — no frameworks, no backend
- **Airtable** (read via REST) as the live data source — *(legacy: Apify; the Apify sections below are stale)*
- GitHub Pages for hosting
- DiceBear API for fallback avatars

## Repo
`https://github.com/AndyVerdy/mds-community-scoreboard`

## Project structure
```
index.html      — The entire dashboard (HTML + CSS + JS in one file)
og-image.png    — OG share image (1200x630, dark branded)
CLAUDE.md       — This file
README.md       — Repo readme
```

## Data source
- **Apify API endpoint**: `https://api.apify.com/v2/acts/sSX1L7hnaohLSWTdB/runs/last/dataset/items?token=<APIFY_TOKEN>` (token is embedded in `index.html`)
- API returns an array of member objects with: `name`, `userId`, `profilePhoto`, `posts`, `totalReactions`, `totalComments`, `score`
- **Important**: The `score` field from the API is NOT used. Score is always recalculated client-side.
- **Important**: `userId` is the Facebook user ID, used to build profile links: `https://www.facebook.com/groups/699138040189700/user/{userId}/`
- **Scraper**: Custom Apify actor (build 0.0.34+) with 3 phases:
  - Phase 1: Scroll `/members` page to get all group members with userIds
  - Phase 2: Visit EVERY member's group profile page (`/groups/{groupId}/user/{userId}/`) to extract exact "Participation - Last 30 days" posts & comments counts + high-quality profile photos
  - Phase 3: Quick feed scan for reaction counts (attributed to post author)
- **Key**: Scraper runs in non-headless mode (`headless: false`) to avoid Facebook bot detection
- **Validation**: Scraper output compared against Facebook Group Insights engagement report (28-day window)
- **Schedule**: Daily at 6 AM ET via Apify scheduler

## Scoring formula
```
Score = (posts × 10) + (totalComments × 5) + (totalReactions × 2)
```

## Avatar strategy
1. Check for user-set override (stored in localStorage)
2. Try `profilePhoto` from API (skip Facebook default silhouettes via `isFbDefault()`)
3. Try cached photo from localStorage
4. Fall back to DiceBear initials avatar seeded by member name:
   `https://api.dicebear.com/7.x/initials/svg?seed={name}`

## Key behaviors
- Fetches live data from Apify on every page load
- Shows a loading spinner while fetching
- Shows a user-friendly error with retry button if API fails
- **Top 50 display**: Default view shows top 50 members (podium + list), not all members
- Top 3 members displayed in a podium layout (1st center-raised, 2nd left, 3rd right)
- Remaining members (rank 4-50) in a ranked list with score bars
- **Search**: filters ALL members by name (including those outside top 50)
- Shows indicator: "Showing top 50 of N members" or search result count
- Clicking any member opens a modal with score breakdown (posts/comments/reactions counts and points from each)
- **Score History chart**: Modal shows 30-day score history with line chart
- **My Profile**: Users can identify themselves to see personalized rank and tips
- **Improvement tips**: Granular tips show what rank you'd reach with 1 more post/comment/reaction
- Escape key or clicking overlay closes the modal
- Responsive — podium stacks vertically on mobile
- **Test suite**: Accessible via `?test=1` URL parameter

## Design
- Dark theme (navy/charcoal backgrounds, blue accents)
- Gold/silver/bronze podium distinction
- Inter font from Google Fonts
- Gradient accent bar and blue-to-purple gradient on title text

## Do NOT
- Use any framework (React, Vue, etc.)
- Create separate CSS or JS files — everything stays in `index.html`
- Trust the `score` field from the API — always recalculate
- Display the API token to users (it's only in the fetch URL)
- Add features not specified in the acceptance criteria

## Build / Run
No build step. Just open `index.html` in a browser or serve via any static server. For local dev:
```bash
npx serve .
# or
python3 -m http.server
```

## Deploy
Push to `main` branch. GitHub Pages serves from root of `main`.

## Acceptance checklist

### Dashboard (index.html)
1. Live data from Apify API (no hardcoded data)
2. Client-side scoring: Posts×10 + Comments×5 + Reactions×2
3. Podium: top 3 with gold/silver/bronze, 1st center-raised
4. **Top 50 display**: Default view shows only top 50 members
5. Ranked list: members rank 4-50 with rank, name, avatar, score, score bar
6. **"Showing top 50 of N members"** indicator visible in default view
7. Search: instant filtering by name across ALL members (not just top 50)
8. Search finds members ranked outside top 50
9. Profile modal: click member → breakdown of posts/comments/reactions + total
10. **Score history chart**: 30-day line chart in modal
11. **Score history caching**: History stored in localStorage, refreshed every 6 hours
12. **My Profile**: banner with personalized rank, tips, and editable avatar
13. **Improvement tips**: Granular rank-up tips for post/comment/reaction
14. Avatars: Real photo → cached photo → DiceBear fallback (skip FB default silhouettes)
15. **Profile links**: Each member card shows a clickable link to their Facebook group profile
16. **Profile link in modal**: Modal shows "View Facebook Profile" link
17. **Profile link URL format**: `https://www.facebook.com/groups/699138040189700/user/{userId}/`
18. OG meta tags with og-image.png
19. OG image: 1200×630 dark branded PNG in repo root
20. Single file: all in index.html
21. Responsive: desktop and mobile
22. Error handling: friendly error message + retry button
23. API token not displayed in UI
24. Fast load

### Data quality (Scraper)
25. **Scraper totals within 25% of FB Insights** (posts, comments, reactions)
26. **Member count accurate**: Matches FB group member count (±10)
27. **No junk members**: Filters out "Suggested for you", page accounts, UI elements
28. **High-quality profile photos**: Scraper captures 168px+ photos from profile pages (not 40px thumbnails)
29. **Real profile photos**: At least 20 of top 50 members have real photos (not FB default)
30. **userId for all members**: Scraper outputs userId for each member (for profile links)
31. **Posts & comments from profile pages**: Phase 2 visits each member's group profile to get exact participation stats
32. Multi-strategy reaction extraction from feed scan (Phase 3)
33. **Non-headless mode**: Scraper runs with `headless: false` to avoid Facebook bot detection

### Testing
34. **Test suite**: Accessible via `?test=1` URL parameter
35. Tests cover: scoring formula, avatar helpers, TOP_N display, search, data validation, profile links
36. **Profile link tests**: fbProfileUrl() helper, userId availability, link rendering
37. **Spot-check validation**: Tests verify specific members against FB Insights
38. All tests pass on live site

### Deployment
39. Pushed to main branch
40. Live on GitHub Pages
41. Scraper running on daily schedule (6 AM ET)
42. `?test=1` passes on live site
