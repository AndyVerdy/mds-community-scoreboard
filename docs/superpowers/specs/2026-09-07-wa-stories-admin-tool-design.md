# WA Stories — Admin Tool — Design

**Date:** 2026-09-07
**Project:** MDS WA Digest → FB story posts (sister of `2026-09-01-wa-to-fb-story-posts-design.md`)
**Status:** Design approved by Andy 2026-09-07. Visual design is Andy's, separately.
**Depends on:** `FB_BACKLOG.md` #5 ships first.

## Problem

The WA → FB story pipeline runs Mon/Wed/Fri and drops a Slack card carrying up to three
ready-to-paste posts. That card is the only surface. Three things follow from it:

- **Nothing can be steered.** If the week's picks are weak, or you want TikTok this time, the
  only move is to wait for the next scheduled run days later.
- **Nothing is recorded.** The card's buttons are dead — Slack allows one Interactivity URL per
  app and Centurion and Application hold both of ours (backlog #2). So `posted_at` is null on all
  14 ledger rows (verified 2026-09-07) and nobody can say which story reached Facebook, or whether
  the pilot works.
- **Nothing is learned.** The ranker is shown rejection reasons, but no human rejection path
  exists, so every row in that list is a system release mislabelled as a verdict (#5 AC 6).

An admin page in the existing MDS Admin portal fixes all three without a Slack app, because a page
we own can have buttons.

## Decisions

Settled with Andy on 2026-09-07. Inputs to the design, not open questions.

| # | Question | Decision |
|---|---|---|
| 1 | Who uses it | **MDS staff only** (`@mds.co`). Eugene keeps picking and pasting from the Slack card |
| 2 | What it is | A working console: check stories, pick one, reject, regenerate, choose which chats to generate from |
| 3 | Schedule | **Stays.** The page adds on-demand generation on top; both write the same ledger |
| 4 | Regenerate | **Two actions.** *Rewrite* keeps the conversation and asks for new words; *find another* sends the ranker for a different conversation |
| 5 | Scope of a generate | Tick chats and let the ranker choose, **or** open a chat and write up one specific day |
| 6 | Picking | **Copy + mark posted.** No push to Slack; Eugene's card is untouched |
| 7 | Rejecting | **Reason required**, and only these reach the ranker as human rejections |
| 8 | Editing | **Allowed, and the privacy check re-runs on save** |
| 9 | Did it work | Mark posted takes an **optional Facebook link**; the page then shows what the post earned |
| 10 | Architecture | **Lift the pipeline into a shared module** both the schedule and the page call |

## Architecture

### The module (new)

`src/lib/fbstory/pipeline.ts` takes over what `src/app/api/fbstory/draft/route.ts` does inline
today. It owns *how a story is made and claimed*; it knows nothing about Slack or HTTP.

```ts
type MakeOptions = {
  days: number;              // lookback
  asof?: Date;               // backfill anchor
  chatIds?: string[];        // restrict the candidate set (page). undefined = every eligible chat
  date?: string;             // YYYY-MM-DD — write up this exact chat-day, skipping the ranker's choice of day
  excludeStoryKeys?: string[]; // "find another" passes the story you are looking at
  max: number;               // 3 for the schedule, 1 for find-another
};

makeStories(opts): Promise<{ made: MadeStory[]; rejected: string[] }>
claimStories(made): Promise<MadeStory[]>   // ledger insert / re-offer, the race guard
rewriteStory(storyKey): Promise<MadeStory> // same thread, one fresh writer call
```

`makeStories` runs the existing sequence — candidates, signals, rank, thread, dedupe,
one-per-chat, write, `reconcileNames`, gate, tags — and returns what survived plus why the rest
did not. `claimStories` is the ledger write, including the duplicate-key handling that tells a
genuine race from a re-offer. Both are lifted from the route unchanged in behaviour.

The scheduled route becomes: `makeStories({ max: 3 })` → `claimStories` → `postCard` → release on
Slack failure. The admin routes call the same functions and never touch Slack.

**Why this and not parameters on the existing route:** that route is the longest file in the
feature and the one piece with no tests (a known deferred item from the build). Two callers of one
tested module beats one route growing a second personality — and the wrong-24-hours bug (#5)
survived precisely because a rule lived in two places.

`activity.ts` is dead code since the "Also this week" footer was removed on 2026-09-02. Delete it
in this work rather than lifting it.

### The page

`src/app/admin/(tools)/stories/page.tsx`, matching the other tools in that route group. The admin
layout already redirects anyone without an `@mds.co` session, and each write route re-checks with
`isStaffEmail` exactly as `src/app/api/admin/fb-post/route.ts` does.

Registration is two entries, both required for the card to look finished:

- `STOREFRONT_TOOLS` in `src/lib/tools/storefront-tools.ts` — id, name, tagline, keywords and the
  `doc` block that feeds search and the help panel. Needs a new `ToolCoverId` and its cover art.
- `src/lib/tools-health/registry.ts` — an entry for the n8n schedule `iX7cEFrCW5apa7CS`
  (`trigger: scheduled`, `schedule: Mon/Wed/Fri 9am ET`, `healthCheck: run status`). Without it the
  card reads NOT YET MONITORED, which is why Personas' does.

### API routes

All under `src/app/api/admin/fbstory/`, all POST, all gated by `isStaffEmail`:

| Route | Body | Does |
|---|---|---|
| `generate` | `{ chat_ids?, date?, max?, exclude_story_keys? }` | `makeStories` + `claimStories`, returns what it made and what it refused. *Find another* is this route scoped to that story's chat with its key excluded |
| `rewrite` | `{ story_key }` | New writer call on the same thread; replaces the stored draft |
| `edit` | `{ story_key, text }` | Re-gates against the original conversation, then stores `edited_text` |
| `reject` | `{ story_key, reason }` | Status `rejected`, reason and actor recorded |
| `post` | `{ story_key, url? }` | Status `posted`, `posted_at`, actor, and the Facebook link |

Reads come from the server component directly, as the other tools do.

### Editing and the gate

`checkDraft` needs the source conversation, which the ledger does not store — only
`message_ids`. `thread.ts` gains a loader that rebuilds a thread from stored ids, and `edit`
re-runs the verbatim check and the undeclared-member check against it before saving. A failed
check returns the reason and saves nothing.

This is stricter than today, not looser: Eugene can already edit freely in the Facebook composer
where nothing checks anything. Editing here is the first time an edited post is checked at all.

## Data

`digest.fb_group_posts` gains five columns and one status. No new table.

| Column | Type | Why |
|---|---|---|
| `origin` | text | `schedule` \| `admin` — where the row came from |
| `edited_text` | text | What a human made it. What was posted is `edited_text ?? draft_text`; the generated text stays in `draft_text` so the two can be compared |
| `posted_url` | text | The Facebook post, pasted on mark-posted |
| `acted_by` | text | The `@mds.co` email that posted or rejected it |
| `acted_at` | timestamptz | When |

**Status set, after this work:**

| Status | Meaning | Told? | Reaches the ranker as |
|---|---|---|---|
| `offered` | Shown to a human — a Slack card or the page | No, still eligible | "offered recently, prefer something new" |
| `posted` | A human recorded it as published | Yes | "already told" |
| `rejected` | **New.** A human turned it down, with a reason | Yes | "rejected by a human — learn from this" |
| `skipped` | A system release: a Slack failure, a manual free | No | *nothing — excluded from the prompt* |
| `blocked` | The privacy gate refused it | No — the prompt is what keeps it away | "blocked by an automated check, not an editorial call" |
| `draft` | Legacy, 2 rows from before 2026-09-02. Never written again | Yes | "already told" |

"Told" is `ledger.ts`'s `TOLD` list, which permanently removes a story from selection. It is
`["draft", "posted"]` today and **gains `rejected`**.

Splitting `rejected` out of `skipped` is what makes rejection reasons trustworthy, and it closes
#5 AC 6 and #2 AC 7. Migration: add the columns, backfill `origin = 'schedule'` on the existing 14
rows, and leave the single `skipped` row as it is — it is a genuine system release.

### What the post earned

`posted_url` carries a group post id (`…/posts/27114645448212266/`). Parse the trailing digits,
look the post up in `digest.fb_posts`, count its rows in `digest.fb_comments`, and show comments,
reactions and reach.

**Honest limits:** comment counts are reliable. `reactions` and `reach` come from the Insights
export and are null on Eugene's 2026-09-02 post, so the panel must render "not captured" rather
than zero. This is a read of data we already have, not new capture.

## Testing

- **Unit, `pipeline.ts`** — the branches the route has never had covered: an empty candidate set,
  a chat filter that matches nothing, a `date` with no messages, a gate block, a duplicate key that
  is a re-offer versus one that is a genuine race, `max` honoured. Supabase and Anthropic mocked.
- **Unit, edit gate** — an edit that reintroduces a verbatim run is refused; a clean paraphrase saves.
- **Unit, ranker prompt** — a `rejected` row appears under human rejections; a `skipped` row appears
  nowhere. This is the regression that started the whole thread.
- **Unit, FB link parse** — a group post URL with and without a trailing slash, and a junk value.
- **Live proof for the close** — generate from one chosen chat, reject one with a reason, edit and
  save one, mark one posted with a real link, and show the ranker's next prompt containing the
  rejection and not the release.

## Risks and things accepted

- **Two people can pick.** With copy-and-mark-posted and no Slack push, the ledger knows only what
  staff tell it. If Eugene pastes one from his card, nothing records it. Accepted (decision 6).
- **Cost.** A generate is two model calls, a rewrite is one. Trivial next to the value, but the page
  makes it easy to click repeatedly.
- **RLS is off** on `digest.fb_group_posts` along with 42 other `digest.*` tables. Pre-existing, and
  this work adds a second surface reading it — worth naming, not fixed here.
- **#5 first.** A console over stories built from the wrong 24 hours is a nicer view of a thin post.

## Out of scope

- Pushing a card to Slack from the page (decision 6).
- The Slack app and the card's buttons (#2). This work makes them less urgent, not done.
- Matching a posted story to its Facebook post automatically (decision 9 chose pasting the link).
- The member-spine gap (#1).
- Any member-facing view. Staff only.

## Success criteria

- A staff member can generate a story from a chat they choose, without waiting for the schedule.
- A rejected story never comes back, and its reason reaches the next ranker prompt.
- An edited story cannot be saved carrying a member's exact words.
- `posted_at` stops being null: what actually went to Facebook is recorded, with its link.
- The scheduled Mon/Wed/Fri card behaves exactly as it does today, from the shared module.
