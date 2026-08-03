# Olivia's search got a rebuild — what changed and what it means

*Ticket #40 · 2026-08-03 · built and tested on staging; goes live with the next promote*

## The problem

Olivia could only find things that **shared words** with how they were originally written. Ask
about "Amazon's freight service" and she'd miss the whole AGL discussion — because nobody in
those threads used those exact words. Her meaning-based index (which understands that those are
the same topic) had been sitting there for weeks, fully built, **never used once**. On top of
that: a two-year-old post ranked the same as last week's, who-said-it counted for nothing, and
searches took up to 12 seconds.

## What changed

- **She now searches by meaning AND by words**, and merges the two fairly. A question phrased
  completely differently from the original post still finds it.
- **Fresh content wins ties.** Last month's thread outranks 2025's unless the old one is clearly
  the better match.
- **Who said it now counts (a little).** Content from established, active contributors gets a
  small lift over drive-by comments — using the same engagement score as the Scorecard, kept
  internal, never shown.
- **6,500 junk entries cleaned out** of the meaning index (empty messages, bare reactions,
  one-word replies). They're still findable by word search — they just no longer pollute
  meaning-based results.
- **The index now maintains itself.** New posts get added every night automatically, with an
  alarm if the job ever stops running. No more hand-run catch-ups.

## The proof — same question, before and after

**"For Amazon logistics — what can you tell me about people's experience using AGL?"**

| | Before (production, Aug 3 morning) | After (staging, same day) |
|---|---|---|
| Verdict | ❌ Failed — she couldn't find the discussions | ✅ Full answer |
| What members got | A miss, despite 76 items about AGL in the archive | Michael Patrón's $50–60K/year savings breakdown, Ben Koeck's 4-containers-a-week experience, Mo Kuhail's Vietnam/China take, real gotchas — with links |
| Search speed | up to 12 seconds | under half a second |

## The test run (33 real member questions, your go)

We re-ran every question that failed the production test this morning, plus a spread across
every category (chats, Facebook, people, counting, partners, privacy, events, billing).

| | Before | After |
|---|---|---|
| Failed | **6** | **1** |
| Partial | 5 | 4 |
| Passed | 22 | 28 with the same-day fix below |

- **5 of the 6 failures fixed** by the new search — including both AGL questions, "who are
  people using for PPC", and "what are people talking about this week".
- **2 new issues appeared and were fixed the same session:** the safety net that checks every
  answer against evidence couldn't read numbers written like "$12,464.38", so it was blocking
  two *correct* answers (and making those turns take 60+ seconds). Both now answer fully, at
  normal speed.
- **The 1 remaining failure isn't a search problem** — it's the *events calendar* lookup, which
  never got this upgrade. Filed as its own ticket (#47), same medicine planned.
- One answer over-stated its evidence ("launched a Kickstarter" became "got funded") — that's
  the attribution ticket (#39), already next in line, now carrying this example.
- Privacy held everywhere: all 202 safety checks green, and the new search refuses canceled
  members, anonymous callers and restricted content exactly like the old one.

## What's left

1. **Go-live** — your promote flips production to the new search (one migration rides along).
2. The full quality score gets measured at the go-live test run, as agreed (full re-run skipped).
3. Old search retired after a soak period.

*Bottom line: members can now ask in their own words and get the real answer, fast — and the
answers lean toward what's recent and who's credible.*
