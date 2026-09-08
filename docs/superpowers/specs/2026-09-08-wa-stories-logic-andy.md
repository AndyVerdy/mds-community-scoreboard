# WA Stories — how it works

Screen file: `WA Stories.dc.html`. Nothing on this page publishes to Facebook. Meta removed Groups API
publishing in 2024, so every post is pasted by a human. The schedule keeps running regardless of what
happens here — this screen is a reading and recording surface, not an approval gate.

---

## 1. The pipeline

18 MDS WhatsApp chats are tracked. **16 are readable. 2 are permanently excluded:**

| Excluded chat | Why |
| --- | --- |
| MDS Centurion 20M+ | Revenue-gated tier; its conversations identify who is in it |
| MDS Credit Card & Travel Hacks | Off-topic for the Facebook group |

Neither appears in chat selection and neither is ever read by a run.

A run fires **Mon / Wed / Fri at 06:00 ET** (n8n). It:

1. Reads the last three days of every included chat.
2. Measures each chat-day: messages, distinct people, replies, questions asked, whether a question got
   answered by someone other than the asker, how many messages carry figures.
3. Ranks the chat-days and writes up the **top three** as posts (one model call to rank, one to write).
4. Files them as one run. Slack still gets its usual card; this screen is additive.

**The three stories in a run are alternatives, not a backlog.** You copy one; the other two stay
available. They are never a queue to work through.

### What gets written

Every post carries the same fixed pilot preamble (rendered dimmed on screen, but included in Copy):

```
MDS WhatsApp Stories

A new pilot we are trying to help cross post live discussions with engagements on Whatsapp
into the Facebook group to help double down and allow for more threading and eyeballs.

<Chat name> - <M/D>

The line that stopped the chat: <quotable line>.

<2–3 paragraphs naming who said what, with their numbers>

<A closing question to the group>
```

Names in the body are only ever members who spoke in that thread, and they are listed in
**TAG WHEN POSTING** so the poster knows who to @ mention.

---

## 2. Story states

| State | Meaning | Actions offered |
| --- | --- | --- |
| `available` | Written up, nothing decided | Copy the post · Mark posted · More (Edit / Rewrite / Find another) · Reject |
| `posted` | Pasted into the group | Copy again · Paste/Replace link |
| `rejected` | Killed, with a reason on record | Copy anyway · Put it back on offer |

State is per story, not per run. A run can hold one posted, one rejected and one available story.

### Mark posted

The Facebook link is **optional**. Without it the story is still recorded as posted, and both this
screen and Reports say `results not tracked` rather than showing zero. Pasting the link later starts
the comment read-back.

### Reject — the one thing to get right

A typed reason of at least 8 characters is **required**; the Reject button stays disarmed until then.
This reason is the only feedback the ranker ever receives, and it ships with the next run.

- Useless: "weak", "no"
- Useful: "Two people and no resolution. The bar is a thread, not a chat."

Rejected stories are never deleted. They stay on their run, appear in the Reports → Rejected table with
the reason, and the text stays copyable.

### Edit and the privacy check

Editing runs a check on **save**, not on type. It refuses a draft that reuses a long verbatim run from
a WhatsApp message and names the offending line back to you. Nothing is stored until the check passes.
(In the prototype the trigger is the story's own quotable line, which the draft opens with — so Save
always refuses once, demonstrating the state.)

### Rewrite vs Find another

- **Rewrite** — same conversation, new words. Measured signals and tag list are unchanged. ~2.4s.
- **Find another** — asks for a different conversation in the same chat. Usually returns "nothing else
  cleared the bar" and leaves the option untouched, because the ranker already took the best day. ~3s.

---

## 3. Results read-back

| Metric | Source | Status |
| --- | --- | --- |
| Comments | Post page, as a member sees it | Reliable |
| Time to first comment | Post page | Reliable |
| Reactions | Collapsed on the post page | `NOT CAPTURED` |
| Reach | Admin-only in Insights | `NOT CAPTURED` |

Reactions and reach read as **not captured, never as zero**, everywhere they appear. Until we have
Insights access that distinction is the whole point.

---

## 4. Navigating runs

At six months the pilot has ~79 runs and ~235 stories, so the navigator is built for that scale:

- **Latest** — always visible, leftmost. Selects the newest run and scrolls the strip back to it.
- **`‹` `›`** — step one run at a time.
- **The strip** — every run as a fixed 146×48 chip (date, one dot per story coloured by status,
  outcome). Scrolls horizontally, scrollbar hidden, auto-centres the selected run.
- **Hover a chip** — a preview card drops below it: run time, outcome, and one row per story with chat,
  day, and the story's opening line (or its reject reason in red).
- **All N runs ▾** — every run grouped by month with sticky month headers. A March run is two clicks away.

### Live vs archive presentation

| Run age | Presentation |
| --- | --- |
| ≤ 21 days | Full reading layout — post text at 14.5px on a 660px measure, one story per row, right rail with chat / measured / why / tags / actions |
| > 21 days | Archive — one line per story (chat, day, status, outcome), post text one click away |

This keeps the page the same length whether the pilot is three weeks or three years old. The threshold
is the `archiveAfterDays` prop (default 21).

---

## 5. Generate — off-schedule runs

For when the week looks thin and you would rather not wait for Wednesday.

**Date range:** Yesterday · This week · Last week · My range.
My range is a calendar: click a start date, click an end date, the span fills in. Future dates are
disabled, next-month is capped at today, and one date picked alone writes up that single day.

**Chats:** all 16 readable chats, each showing its **message volume for the selected range** (silent
ones dimmed), with All / Only active / None shortcuts. Before a range resolves, volumes show `—` rather
than claiming everything is silent.

**Refusal is a real outcome.** If the range holds under ~15 messages, or volume but no thread that
reached a resolution, Generate returns *nothing worth telling* with the actual counts, and records
nothing. It never lowers the bar to fill three slots. The scheduled run is unaffected.

A successful run is filed as an **off-schedule run** with its own timestamp (so two generations on the
same day are distinguishable) and selected immediately.

---

## 6. Reports

A separate view, so the homepage stays stories only.

- **Month pills** — All months · Sep 2026 · Aug 2026 … Mar 2026.
- **Posted table** — run, chat · day, posted at, comments, reactions, reach, link back to the story.
- **Rejected table** — run, chat · day, rejected at, the full reason, link back to the story.
- Both sortable by any column, 20 rows at a time with "Show 40 more of N", and empty states that name
  the month.

---

## 7. Data model

```js
story = {
  id, run,            // run id
  opt,                // 1..3 — which option of the run
  chat, day,          // source chat and the chat-day written up
  status,             // 'available' | 'posted' | 'rejected'
  signals: [],        // measured: messages, people, replies, question, answered?, figures
  why,                // one line on why the ranker picked it
  tags: [],           // members to @ mention
  verbatim,           // the quotable line — also what the privacy check guards
  text,               // the full post, preamble included
  // posted
  postedAt, link, results: { comments, first } | null,
  // rejected
  rejectedAt, reason,
  // edited
  rewrites, edited
}

run = { id, seq, date, chip, long, time, off? }
```

Everything on the page derives from this array — run outcomes, chip dots, footer counts, Reports totals.
Nothing is hardcoded.

---

## 8. Tweakable props

| Prop | Default | Effect |
| --- | --- | --- |
| `dimOpener` | `true` | Dims the pilot preamble so the eye lands on the story. Copy is unaffected. |
| `archiveAfterDays` | `21` | Age at which a run switches from full reading layout to archive. |
| `requireRejectReason` | `true` | Whether Reject stays disarmed until a reason is typed. |

---

## 9. Prototype data

The five most recent runs are hand-written, including the brief's verbatim MDS DTC/Shopify 9/5 story
with its real signals and comment counts. Everything before Aug 28 is generated from a 21-story topic
pool across the five main chats, seeded deterministically by date — so statuses, comment counts, reject
reasons and posting times vary run to run, and the counts add up.

Message volumes in Generate are likewise derived per chat-day from a fixed hash, so the same range
always reports the same numbers.
