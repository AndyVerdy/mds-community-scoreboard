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
| Priority chats | **DTC/Shopify, TikTok, AI & Automations** — preferred, not exclusive (`FB_STORY_PRIORITY_CHATS`) |
| Excluded chats | **Centurion 20M+** and **Credit Card & Travel Hacks** — never surfaced (`FB_STORY_EXCLUDED_CHATS`) |
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

## What the post looks like (rewritten 2026-09-02 after Eugene posted one by hand)

Every post opens with a standing title and blurb — written by us, not the model, so
the framing cannot drift between runs — then the chat name and date, then ONE story.

```
MDS WhatsApp Stories

A new pilot we are trying to help cross post live discussions with engagements
on Whatsapp into the Facebook group to help double down and allow for more
threading and eyeballs.

MDS DTC/Shopify - 8/30

<hook: the most concrete fact — a price, a result, a reversal>

<2-4 short paragraphs, one idea each>

<one genuine question to the group>
```

**There is no "Also this week" footer, deliberately.** It existed briefly. Eugene,
who actually posts these: *"it just detracts from the purpose... the WhatsApp
stories need to be hyper-focused on one conversation that is happening and is
driving a lot of engagement, because the purpose is to continue a threaded
discussion on that conversation. Dropping other themes in this post is a
distraction and will lead to more confusion."* Andy had asked for the activity
footer earlier; Eugene's reasoning superseded it. Do not put it back without them.

## Old notes on the post (still true)

A chat name, then a hook built on the most concrete fact in the thread (a price, a
result, a reversal), then two to four short paragraphs, a question to the group, a
divider, and an "Also this week in the member chats" section of three or four
one-line hooks from OTHER chats. Roughly 200 words.

Hard-won shape, from Andy's feedback on the first live cards:
- **Keep the numbers.** The first version stripped vendor pricing because the
  prompt's "no numbers that embarrass anyone" rule over-fired. "$80k/yr cut to $5k"
  is the value; "cut their bill sharply" is worthless. The rule is about people and
  their private business, never about what software costs.
- **No roll call.** Walking through each participant in turn reads as meeting
  minutes. Two or three people, woven in.
- **No message counts.** "353 messages across 8 chats" is a vanity metric. The
  footer earns attention with what happened, not how much.
- **Plain text, no markdown.** Facebook group posts have no formatting — `**bold**`
  pastes through as literal asterisks. `stripMarkdown` in `write.ts` enforces this
  in code, before the gate, so approved text is byte-identical to pasted text.

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

## Which chats, and in what order

Eugene (2026-09-02): *"Focus on three channels: DTC, TikTok, and AI... those are the
channels that have the most meaningful, widespread impact and from where we can actually
share with others."* Andy: *"not only, but prioritize."*

So the three are **preferred, not exclusive**. The ranker sees them flagged
`[PRIORITY CHANNEL]` and is told: take one whenever it clears the bar, break a close tie
its way, but prefer a good story from elsewhere over a weak one from a priority channel.
A hard allowlist was tried first and reverted the same day — the three carry ~160
messages a week between them, and nine distinct stories a week from that alone forced
thin picks or empty runs.

## Three options per card, and no confidence score

Each run offers **up to three** ready-to-paste posts, best first, and the human picks
one. Offering exactly one made every run a coin flip: a story the poster found too
sensitive, repetitive or weak wasted the slot until the next run days later.

The ranker used to emit a self-reported `confidence` 0..1 and the route skipped runs
below 0.7. **That was theatre** — the prompt told the model the threshold, so it
cleared it on every run ever recorded (0.74–0.82, never once below, never once
declining to pick). It is gone. Ranking is now comparative (order these against each
other), and the card shows *measured* evidence instead: how many people spoke,
whether a question drew answers from others, how many messages carry figures. Those
come from `signals.ts` and are computed from the raw messages.

**`offered` is not `told`.** An offered story stays eligible — being shown is not
being used, and with three options two of every three are shown and not used by
design. This was learned the hard way: the DTC/Shopify helpdesk story was offered,
Eugene called it the best yet, and it was already unreachable. A key collision on
re-offer updates the row rather than failing; only a `draft`/`posted` row means
another run genuinely got there first.

## Spine connections (verified live 2026-09-02)

- **Partners: 27 of 27 mentions resolve to `partners_catalog`.** No orphans.
- **Members: 246 of 284 posts in 30 days reach the spine** (87%) via
  `fb_member_map.at_member_id` → `member_profiles` (6,025 rows).
- The 38 that don't come from **13 authors with no `fb_member_map` row**. Two are not
  people: "Million Dollar Sellers" (the group account) and "Anonymous member" (FB
  makes this unresolvable by design). The real gap is 11 people — Dan Wills (13
  posts), Ivan Ong (9), EJ Ball and others. EJ Ball *is* a member with a profile on
  file, so the break is the FB-uid mapping, not the member record.
- ⚠️ Join against `member_profiles`, NOT `digest.members`. The latter is the
  WhatsApp mirror and only holds members with a WA presence — it shows 72% and looks
  like a data problem that isn't one.

## Backlog

Tickets live in `FB_BACKLOG.md` (Facebook stream: capture · admin tab · story posts).
**#1 S1** member-spine gap · **#2 S4** dedicated Slack app to re-enable the card buttons.

## Open questions for Andy

1. **The card has NO buttons, deliberately — do not add any without a dedicated Slack app.**
   2026-09-01 incident: the card shipped with an "Open group" URL button carrying no
   `action_id`, on the assumption Slack would not deliver the click. **It does** — Slack mints
   its own action_id and POSTs `block_actions` to the OWNING APP's Interactivity Request URL.
   The card is posted with the MDS WA Approvals bot token, so a member clicking "Open group"
   reached the WA Approvals handler, which read it as a join-request rejection, overwrote the
   card in place, threaded a rejection reply, and stamped `decision=rejected` onto Airtable
   JoinRequests row `recgrlkagHhDZH3Iv`. The Whapi call 400'd, so no member was rejected on
   WhatsApp. The group is now a plain mrkdwn link, which sends no interaction, and a test
   asserts the card stays inert. Buttons return only with a dedicated Slack app + its own
   `FB_STORY_SLACK_BOT_TOKEN` / `FB_STORY_SLACK_SIGNING_SECRET`.
2. **Third-party names.** The gate blocks quotes and undeclared *members*. Someone named *inside*
   a message — a client, a supplier — is defended only by the writing rules and by Andy reading
   the card. A reviewer proposed scanning all 673 member names against every draft; not taken,
   because over-blocking is a real risk and a human reads every card. Say if you want it.
3. **RLS is disabled on 43 `digest.*` tables**, including the new `fb_group_posts` which stores
   draft text derived from private conversations. Pre-existing, not caused by this work.
4. **The ranker has never returned "none"** — 48 for 48 across all backfills. The none path is
   proven working, so this reads as genuine chat volume, but watch whether it ever declines.
5. **Tagging credited members (proposed, awaiting Andy).** `digest.member_links`
   (`at_member_id` → Facebook profile url, 6,021 rows, added by the Olivia session) would let
   the Slack card list credited members with their profile links, so whoever pastes can
   @-mention them in the Facebook composer — tagged members get notified and reply. Constraint
   from that view's author (#137): the link and the name are all the card needs; **never put
   `at_member_id` in the card text**, because the paste path ends on Facebook.

## Things that bit us, so they do not bite again

- **The ranker truncated mid-JSON.** It wrote 1,400-char rationales against
  `max_tokens: 2000`, so a live run 500'd with "Ranker returned non-JSON" on a
  payload that was plainly JSON — it was valid JSON that simply stopped. Budget is
  4000, the prompt caps `why` at ~300 chars, and the error now names truncation.
- **The hero changes every run, by design.** The ranker is an LLM judgement call and
  the week's top candidates sit within ~0.06 confidence of each other. You cannot
  approve a draft and re-run to reproduce it — the card IS the artifact. The ledger
  is what stops a story being told twice in normal operation.
- **Selection used to bin the week.** The footer once took one headline per chat, by
  volume, discarding everything else — a six-message day carrying "ADA lawsuits are
  hitting multiple members" lost to a busy day of chatter. Every substantive
  chat-day now goes to the writer, which picks. Volume is a bad proxy for interesting.
- **Of 18 chats in a typical week, ~7 are completely silent** and ~4 barely register.
  The material is genuinely concentrated in five or six chats. That is a community
  fact, not a pipeline bug.

## Known deferred items

The notable one: `draft/route.ts` has no mocked test harness — its branches are covered by live
dry runs rather than unit tests. Fast-follow, not a blocker.
