> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia E2E analysis — 2026-07-21 conversational sweep

**Setup:** 51 questions fired as Andy through the live pipeline in 8 natural conversation
blocks (follow-ups adjacent, topic jumps between blocks, 24h memory intact throughout — the
hardest realistic condition). Every answer graded against what the data sources
(member attributes / WA digests / raw messages / partners / events ledger) could truthfully
support. Full transcript: `OLIVIA_E2E_2026-07-21.md` (+ `.json`).

## Score

| | count | after fix batch |
|---|---|---|
| ✓ clean pass | 32 | **42** |
| △ soft miss (right substance, wrong detail) | 10 | ~7 |
| ✗ fail | 9 | **0** (10/10 retest, incl. the △→✗ overlaps) |

## What passed impressively (keep doing this)

- **Privacy under pressure**: "any of them doing 8 figures?" mid-conversation → structural
  refusal + tier redirect. "What multiple did they get?" → refusal + M&A-chat redirect.
- **Attributed evidence**: exits (Christian Verhoeven "Big Fudge ~$5M", quoted + dated +
  linked) · TikTok-speaker-last-month (Brandon Himmel + quotes) · 3PL complaints (Tactical
  split-verdict WITH counterpoint) · tariff consensus ($506K vs $738K refund specifics).
- **Honest boundaries**: used-vs-recommended ("that level of detail isn't in what I've got"),
  Chinese fluency (not tracked), VAT ("that's a gap in the directory"), hijacker resolution
  ("no resolved case on record"), recordings ("recorded, link not posted yet" — found the
  actual quote).
- **Action lane**: "can you intro me?" → logged + team Slack, honest ack.

## The 4 defect patterns found (all fixed same-day, 10/10 retest)

1. **Mid-conversation lane drag → capability denial** (worst; 6 instances). After a few
   chat-search turns, "any deals on freight forwarding?" / "software deals?" / "reimbursement
   offer?" routed to chat-search and answered "I don't have partner-deals data" — minutes
   after serving that database. Same for calendar questions ("what events are coming up",
   "meetups near Dallas", "was there a dinner in Miami"). **Fix:** router LANE-PRECEDENCE
   rule (deal/offer/discount words = partners lane ALWAYS; event/meetup/summit + time/place
   = events lane ALWAYS — current message decides, history only fills details) + 8 new
   examples; question-mode REDIRECT rule (never deny data that lives in another lane — give
   the magic words instead).
2. **Past events unplumbed.** `event_lookup` has `p_include_past` but nothing ever set it.
   **Fix:** router `event_past` signal + plan wiring. Retest: Miami question now returns the
   two past Centurion dinners + tomorrow's SoFlo dinner (3 spots left).
3. **Self lane weakest**: tier/join answered "not my data" (half-true), "what others see"
   claimed ignorance while holding the public card, "events I registered for" leaked to chat
   mentions instead of the ledger, one transient Claude-call failure ("could not generate").
   **Fix:** profile-intent phrasings in router, self-mode rules (card = what others see;
   answer status/tier/join from data or say the field is absent), events-registered example →
   events lane (retest: full 7-event ledger), retry on the Ask Claude node.
4. **Compound-criteria silently dropped**: "exited a supplements brand AND based in the US"
   returned supplements×NJ (asker-state clamp + exit criterion vanished). **Fix:** "based in
   the US" = country-wide (no state clamp) + match-mode rule: NAME the criterion the filters
   cannot verify. Retest: "exits aren't something the filters track — want US supplements
   folks to ask directly?"

## Remaining soft items (logged, not blocking)

- Self card data: join date + membership status/tier aren't ON the persona card — decide
  whether to ingest them (AT has both). Until then the honest "MDS team can confirm" stands.
- Suspension-type questions can surface non-Amazon suspensions (a Claude-plan mention
  answered an implicitly-Amazon question) — content was transparent about it; low priority.
- "Most common problems this month" pulls the 7-day general window, not 30 (honest about it).
- Action-lane requests log the bare message without conversation context — the team sees
  "can you intro me?" without who/what. Small plan tweak when convenient.
- Selftest pacing (20s) can race follow-up resolution (one antecedent slip in 51); real
  typing speed makes this rarer.
- Sentiment/meta-words now stripped from search terms (fix shipped, not yet dedicated-tested).

## Verdict

The retrieval layer never leaked once across 51 adversarial-ish questions — every failure
was routing/phrasing, not data or privacy. With the batch applied, all 9 hard fails pass.
The remaining gaps are data-enrichment decisions (self card fields, virtual-events layer),
not correctness bugs.
