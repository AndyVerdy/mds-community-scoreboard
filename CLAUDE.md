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
- **Known issue**: `totalComments` is currently `0` for all members (upstream bug being fixed). The dashboard is built to use it once real data flows.

## Scoring formula
```
Score = (posts × 10) + (totalComments × 5) + (totalReactions × 2)
```

## Avatar strategy
1. Try `profilePhoto` from API first (Facebook Graph URL)
2. On error, fall back to DiceBear initials avatar seeded by member name:
   `https://api.dicebear.com/7.x/initials/svg?seed={name}`

## Key behaviors
- Fetches live data from Apify on every page load
- Shows a loading spinner while fetching
- Shows a user-friendly error with retry button if API fails
- Top 3 members displayed in a podium layout (1st center-raised, 2nd left, 3rd right)
- Remaining members in a ranked list with score bars
- Search filters members instantly by name
- Clicking any member opens a modal with score breakdown (posts/comments/reactions counts and points from each)
- Escape key or clicking overlay closes the modal
- Responsive — podium stacks vertically on mobile

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
1. Live data from Apify API (no hardcoded data)
2. Client-side scoring: Posts×10 + Comments×5 + Reactions×2
3. Podium: top 3 with gold/silver/bronze, 1st center-raised
4. Ranked list: remaining members with rank, name, avatar, score, score bar
5. Search: instant filtering by name
6. Profile modal: click member → breakdown of posts/comments/reactions + total
7. Avatars: profilePhoto first, DiceBear fallback on error
8. OG meta tags with og-image.png
9. OG image: 1200×630 dark branded PNG in repo root
10. Single file: all in index.html
11. Responsive: desktop and mobile
12. Error handling: friendly error message + retry button
13. API token not displayed in UI
14. Fast load
15. Pushed to main
