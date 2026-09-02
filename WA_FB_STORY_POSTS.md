> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# WA → FB Story Posts — handoff

**Status: LIVE in production since 2026-09-01.**

Three times a week a scheduled job picks the single best conversation from the 18 MDS WhatsApp
chats, writes it up, checks it for privacy, and posts a copy-ready card to Slack. A human pastes
it into the private Facebook group. Meta removed Facebook Groups API publishing in 2024, so the
paste is a hard constraint — the system exists to make it cost one glance and one click.

## Where everything is

| Thing | Where |
|---|---|
| Code | `mds-digest-web` (a DIFFERENT repo), `src/lib/fbstory/` + `src/app/api/fbstory/` |
| Route | `GET /api/fbstory/draft?secret=…[&dry=1][&days=N][&asof=YYYY-MM-DD]` |
| Buttons | `POST /api/fbstory/interactivity` (not wired yet — see Open questions) |
| Schedule | n8n `iX7cEFrCW5apa7CS`, cron `0 9 * * 1,3,5`, tz `America/New_York`, retry OFF |
| Slack | `#automation-tests` (`C0AQ8USNQK0`) |
| Ledger | Supabase `digest.fb_group_posts` |
| Reads | `digest.summaries`, `digest.wa_messages`, `digest.members` |
| Spec / plan | `docs/superpowers/specs/2026-09-01-…-design.md` · `docs/superpowers/plans/2026-09-01-….md` |

**Airtable is never written.** No new data capture — everything read already existed.

## How to check on it

```bash
curl -s "https://mds-digest-web.onrender.com/api/fbstory/draft?secret=$FB_STORY_SECRET&dry=1" | python3 -m json.tool
```

`dry=1` computes a real pick and a real draft, posts nothing and writes nothing — safe to run
any time. **Use `mds-digest-web.onrender.com`, not `digest.mds.co`: that hostname does not
resolve on Andy's Mac** (n8n and public resolvers are fine).

Add `&asof=YYYY-MM-DD` to see what it would have said on a past week — this is how the twelve
sample drafts were reviewed before launch.

## The rules it enforces

- **Named, paraphrased.** Members are credited; their exact words never leave the chat.
  `src/lib/fbstory/gate.ts` blocks any draft reusing 8+ consecutive words from a source message —
  checked against each message AND the whole thread joined, because a sentence split across
  consecutive WhatsApp messages used to slip through.
- **Never twice.** Two dedupe axes: the story key (chat + thread root message) and message-id
  overlap. A duplicate insert is treated as already-told, so a double-fire cannot post twice.
- **Silence means broken.** Every no-post outcome — nothing good enough, below confidence, a
  repeat, a gate block, an error — posts a line to Slack and returns 500 if that line fails.
- **A ceiling, not a schedule.** A thin week posts less. "None" is a valid answer.

## Open questions for Andy

1. **Buttons are unwired.** Slack allows one callback URL per app; Centurion and Application hold
   both of ours. The card posts and copies fine and dedupe is unaffected. Missing: one-click
   "Mark posted", and skip reasons feeding back to the ranker. Fix = a new Slack app (Andy
   creates it), then set `FB_STORY_SLACK_BOT_TOKEN` + `FB_STORY_SLACK_SIGNING_SECRET` in Render.
   **No code change needed.** Note the interactivity route now 401s when no signing secret is set.
2. **Third-party names.** The gate blocks quotes and undeclared *members*. Someone named *inside*
   a message — a client, a supplier — is defended only by the writing rules and by Andy reading
   the card. A reviewer proposed scanning all 673 member names against every draft; not taken,
   because over-blocking is a real risk and a human reads every card. Say if you want it.
3. **RLS is disabled on 43 `digest.*` tables**, including the new `fb_group_posts` which stores
   draft text derived from private conversations. Pre-existing, not caused by this work.
4. **The ranker has never returned "none"** — 48 for 48 across all backfills. The none path is
   proven working, so this reads as genuine chat volume, but watch whether it ever declines.

## Known deferred items

The notable one: `draft/route.ts` has no mocked test harness — its branches are covered by live
dry runs rather than unit tests. Fast-follow, not a blocker.
