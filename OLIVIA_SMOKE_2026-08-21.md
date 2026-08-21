# Smoke 2026-08-21 — the video-content exit exam (bank + slice)

**Context:** run overnight on Andy's go after the 2025 transcript batch landed (232 videos /
6,429 chunks / 232 summaries) and the Millie rename shipped to staging. Target: STAGING.
Two parts: the FULL 100-question organic bank (regression) + an 11-question problem-first
video slice (the new capability). Raw Q→A: `scratchpad slice_answers.txt` (v1, name-anchored,
superseded), `slice_v2_answers.txt` (problem-first, the real test), bank pairs scored by 4
parallel judges against the bank's `expect` fields, verdicts re-verified by hand on every
non-PASS.

## Bank (100 questions): 89 PASS · 7 PARTIAL · 4 FAIL → honest read 90 effective
| class | result |
|---|---|
| SAFETY | 14/14 PASS |
| CHAPTERS · FRESHNESS | 8/8 · 4/4 PASS |
| PEOPLE | 17 PASS · 1 PARTIAL (no near-match suggestion on a not-found name) |
| CONTENT | 9 PASS · 2 PARTIAL · 1 FAIL (#104 lag) |
| PARTNERS | 5 PASS · 2 FAIL (#104 lag ×2) |
| EVENTS | 6 PASS · 1 "FAIL" that is CORRECT behavior (attendee names refused — #96 gates on the asker's own registration; the test asker is unregistered; **bank truth predates the ruling — fix the expect**) |
| STATS · VIDEOS · CAPABILITY · PROFILE | 8+8+7+3 PASS · 1 PARTIAL each |

**The 3 real fails are ONE defect: #104 adjacent-turn topic lag** — in rapid seq questions the
reply serves the PREVIOUS topic (4079 got a 3PL answer, 4080 got 4079's review-tools answer,
4087 continued tariffs). Kin of the known <2s echo race. Filed on the board, not chased in-run.
Pairing skew was ruled out (timestamp re-pairing = identical pairs).

**Vs last smoke (Eugene arc, 47/50 = 94%):** 90/100 with a stricter judge and 2× the bank.
No safety regression; the 6,429-chunk corpus load broke nothing.

## Slice v2 (11 problem-first questions, zero names given): 11/11 surfaced the right videos
Andy's rejection of slice v1 ("you're asking what this person said — this is not real") produced
the real test: the member states a PROBLEM; she must FIND the video. Results:

- **Video found unprompted 11/11** — fees → Jasim Eisa ($830K/yr) + Ephraim Ausch placement-fees
  calls; bottleneck → Lisa De Rosa; cash → CapEc + Vancouver Operator Room; valuation → Scott
  Deetz; images → Dorian Gorski + Kim Cruickshank; presenting → Alan Kishk; TikTok cold start →
  Bonilla + Beginners Panel (the Eugene case, dead); PPC → AMC call + Torsten/Daniel; Canada →
  Mo Kuhail.
- **Speakers named with roles** throughout (fed by metadata; #103's entity layer now underneath).
- **Multi-source, multi-content** (Andy: "I hope some will have answers in several places") —
  ratings-drop = FB post + Centurion thread + X campaigns; fees = 3 videos + 3 partners; PPC =
  2 videos + chat SOPs + 2 partner tools; Canada = 2 FB posts + chats + video. WA/FB/Videos
  balance reads natural: video leads where strongest, live chat leads on the brand-new Amazon
  return-flow issue (correct — no video exists for it).
- **Zero "missing transcripts" denials** — the 4 stale prompt rules were purged pre-run, plus the
  night's biggest catch: **the live lane calls `video_search_v2`, which #101 never patched** —
  entitled members were still getting the blanket [RESTRICTED] refusal E2E. Fixed
  (grant-bounded restricted, attachments stay public-only), both sides re-proven.
- **Timestamps: red → green in-run.** Zero cited in the slice; one Answer Seed rule added after
  ("give the moment next to the link, never estimate") — probe now returns *"chunks 11-12, at
  16:37-16:38 … At 00:16:37 …"* with the verbatim quote.

## Follow-ups filed (not chased)
#104 adjacent-turn lag (S1) · bank-truth fixes: 4072 expect (post-#96) + 4044 near-match wording ·
retirement pass on always-passing questions = sprint-close ritual, Andy's call.
