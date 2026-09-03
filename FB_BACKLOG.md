> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Facebook stream — backlog

Covers the Facebook surfaces: group capture (`digest.fb_*`), the admin report tab
(`/admin/facebook`), and WA → FB story posts (`/api/fbstory/*`).

Structure: **OPEN — ARCHITECTURE** first, then **OPEN — THE REST**, then **CLOSED**.
A ticket's block moves between sections; it is never copied.

---

## OPEN — ARCHITECTURE

### #1 · 🔑 Facebook posts don't reach the member spine for 11 real members · 🔴 S1

**Story.** As MDS, we want every Facebook group post attributed to the member who wrote
it, so that engagement scoring, the admin report and the WhatsApp stories all credit the
right person — and so a member's activity is never invisible because of a missing join.

**Measured 2026-09-02 (live):** 284 posts in the last 30 days; **246 reach the member
spine (87%)** via `fb_member_map.at_member_id` → `member_profiles`. The 38 that don't come
from **13 distinct authors with no `fb_member_map` row at all**:

| Author | Posts (30d) |
|---|---|
| Dan Wills | 13 |
| Ivan Ong | 9 |
| Million Dollar Sellers | 4 · *not a person — the group's own account* |
| Mouad Errafik | 3 |
| EJ Ball · Matthew Verde · Mirzad De · Ruben Alikhanyan · Abe Indig · Tamkin Amin Collins · Ben Pearson · Chris Kjeldsen | 1 each |
| Anonymous member | 1 · *unresolvable by design — FB anonymous posting* |

So **11 real people**. EJ Ball is the diagnostic case: he IS a member with a Facebook
profile link on file, so the break is the FB-uid → member mapping, not the member record.

**Acceptance criteria**
1. Each of the 11 either resolves to an `at_member_id`, or is recorded with a stated
   reason why it cannot (e.g. no FB profile link in Airtable, duplicate/ambiguous uid).
2. "Million Dollar Sellers" and "Anonymous member" are classified explicitly as
   not-a-member rather than counted as misses, so coverage stops being flattered or
   penalised by them.
3. Coverage re-measured over the same 30-day window: before **246/284 (87%)**, after
   stated. Every author counted once.
4. The root cause is named per member — a missing `FB Profile Link` in Airtable is a
   different fix from a missing `fb_member_map` row, and the two need different owners.
5. **No Airtable writes by the agent.** Where the fix belongs in Airtable, name the record
   and the field and hand it to Andy or ops.

**Notes.** `fb_member_map` is the FB-capture stream's table. ⚠️ There are ~737 duplicate
`Member ID (FB)` values in Airtable `tblVc38gw21iHLYMG` (long-standing, uninvestigated) —
worth checking whether they overlap these 11 before hunting individually. Join against
`member_profiles`, **not** `digest.members`: the latter is the WhatsApp mirror and reports
a misleading 72%.

---

## OPEN — THE REST

### #2 · 🔘 Give the story card its own Slack app so the buttons work · 🔵 S4

**Story.** As the person posting these, I want to click "Mark posted" or "Skip" on the
card, so the system records what actually went out and learns from what I reject —
instead of me pasting into Facebook and the ledger never finding out.

**Why it is off right now.** The card shipped with Open group / Mark posted / Skip. A URL
button with no `action_id` does **not** stop Slack delivering the click: Slack mints its own
id and POSTs to the Interactivity Request URL of the **app that owns the posting bot token**.
This card posts with the **MDS WA Approvals** token, so on 2026-09-01 Eugene clicking "Open
group" reached the WA Approvals handler, which read it as a join-request decision, defaulted
to reject, overwrote the card in place, and stamped `decision=rejected` onto Airtable
JoinRequests `recgrlkagHhDZH3Iv`. The Whapi call 400'd, so no member was actually rejected.
Slack allows **one callback URL per app**, and Centurion and Application already hold both of
ours — so any button on this card lands in someone else's system. The card is now inert by
design, with a test pinning it.

**Cost of leaving it.** Small: no one-click "Mark posted", and skip reasons never reach the
ranker, so rejecting a weak story teaches it nothing. Dedupe is unaffected — a story is
recorded the moment it is offered.

**Acceptance criteria**
1. A dedicated Slack app exists for this feature. **Andy creates it** — the agent does not
   create accounts.
2. `FB_STORY_SLACK_BOT_TOKEN` and `FB_STORY_SLACK_SIGNING_SECRET` set in Render, followed by
   a manual redeploy (a Render env change does not restart on its own).
3. Its Interactivity Request URL points at `/api/fbstory/interactivity`. **Centurion's and
   Application's URLs are verified untouched** — this is the step that can silently break
   another feature.
4. Buttons restored to `buildCardBlocks`, and the "contains NO interactive elements" test
   replaced by one asserting they carry *our* `action_id`s.
5. Proven live, not assumed: clicking **Mark posted** flips that ledger row to `posted`;
   **Skip** captures a reason that appears in the next run's ranker prompt.
6. Proven that the click no longer reaches WA Approvals — n8n `ib7g9bBddhzCbj4X` records no
   execution for it.

**Already built, nothing to write.** `/api/fbstory/interactivity` exists, handles both
buttons and the skip-reason modal, verifies the Slack signature via the shared
`src/lib/slack-verify.ts`, and returns 401 when no signing secret is configured. This ticket
is credentials and configuration, not code.

---

## CLOSED

*(none yet — this board opened 2026-09-02)*
