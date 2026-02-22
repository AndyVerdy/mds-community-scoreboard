# MDS Community Scoreboard

## What this is
Gamification leaderboard for the MDS Facebook Group. Pulls member activity data from an Apify scraper, scores and ranks members, and displays them on a public dashboard. Hosted on GitHub Pages.

## Stack
- Single-file vanilla HTML/CSS/JS (`index.html`) — no frameworks, no backend
- Apify REST API called client-side for live data
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
- API returns an array of member objects with: `name`, `profilePhoto`, `posts`, `totalReactions`, `totalComments`, `score`
- **Important**: The `score` field from the API is NOT used. Score is always recalculated client-side.
- **Scraper**: Custom Apify actor (build 0.0.27+) with 3 phases:
  - Phase 1: Scroll `/members` page to get all group members
  - Phase 2: Scroll main feed, extract posts with comments & reactions using multi-strategy DOM extraction
  - Phase 3: Visit top 50 member profiles for real profile photos
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
15. OG meta tags with og-image.png
16. OG image: 1200×630 dark branded PNG in repo root
17. Single file: all in index.html
18. Responsive: desktop and mobile
19. Error handling: friendly error message + retry button
20. API token not displayed in UI
21. Fast load

### Data quality (Scraper)
22. **Scraper totals within 25% of FB Insights** (posts, comments, reactions)
23. **Member count accurate**: Matches FB group member count (±10)
24. **No junk members**: Filters out "Suggested for you", page accounts, UI elements
25. **Real profile photos**: At least 20 of top 50 members have real photos (not FB default)
26. **Post deduplication**: Content-based keys prevent duplicate counting
27. Multi-strategy comment extraction (text matching, aria-label, button siblings)
28. Multi-strategy reaction extraction (aria-label, emoji-count, toolbar, like-button siblings)

### Testing
29. **Test suite**: Accessible via `?test=1` URL parameter
30. Tests cover: scoring formula, avatar helpers, TOP_N display, search, data validation
31. **Spot-check validation**: Tests verify specific members against FB Insights
32. All tests pass on live site

### Deployment
33. Pushed to main branch
34. Live on GitHub Pages
35. Scraper running on daily schedule (6 AM ET)
36. `?test=1` passes on live site
