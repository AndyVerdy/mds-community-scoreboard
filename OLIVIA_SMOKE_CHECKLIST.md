> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia — pre-promote smoke checklist (#33)

**Run this on STAGING before EVERY `promote`. Paste the filled result block into the
promote's session-log entry.** This is Andy's instinct filed as process (2026-07-31): five cheap
standing checks that catch what the eval bank never looks at — the member-facing feel of an
answer in flight. It is NOT an eval run and costs a few cents.

## The five checks

**1. Feedback fires early (read tick · typing · ladder armed).**
Fire one staging probe, then read the exec's per-node start times (n8n API,
`/executions/<id>?includeData=true` → runData startTime):
```bash
python3 scripts/olivia_selftest.py --staging --questions "Im having issues with 3pl, who should i talk to"
```
PASS = `Mark Read + Typing` starts **before `Route Request`** and within ~6s of exec start.
(2:40PM stall lesson, exec 57816: the branch used to run AFTER the 70s answer — no tick, no
typing, no ladder. Fixed by branch order, `apply_33_early_feedback.py`.)

**2. Ladder fires once, distinct rung copies, silent when answered.**
Read-only, no test send needed:
- Ladder wf `X1vzrW9Avqff3qRa`: `Send Holding` text ≠ `Send Delay Notice` text
  (today: "On it — checking a few sources for you 🔎" vs "Still working on this one — …🙏").
- `Holding Trigger?` on the graph being promoted anchors `arrival` on the **message
  timestamp**, never now (Meta replays fire ghost ladders otherwise — the 9:54/9:55PM
  duplicate pair, 2026-07-31).
- Latest few real prod inbounds: exactly ONE ladder exec each, ~18-20s (silent no-op) when
  the answer beat the rung.
PASS = all three hold.

**3. A solve-lane answer carries links.**
The check-1 probe doubles here. PASS = every person/thread/partner recommended as the
solution carries the link its tool row returned (FB thread URL, partner link, member_card FB
link); rows with no link are named without one; **no invented links** (the #1 link gate would
block them anyway).

**4. One counting probe.**
```bash
python3 scripts/olivia_selftest.py --staging --questions "how many chapters does MDS have?"
```
PASS = the warehouse number (20 today), **no link spam on a pure counting answer**, and any
totalling shown is `breakdown_sum` (read, never model-added — 773 vs 722 with the why).

**5. Gate GREEN.**
```bash
python3 scripts/olivia_leak_gate.py
```
PASS = every check green (167 as of 2026-07-31). A RED gate blocks the promote, full stop.

## Result block (copy, fill, paste into the session log)

```
SMOKE <date> · staging <versionId> · pre-promote
1 early-feedback : PASS/FAIL — MRT +X.Xs, before Route Request (exec <id>)
2 ladder         : PASS/FAIL — distinct copies · arrival=msg-ts · 1 exec/inbound
3 solve links    : PASS/FAIL — <who/what carried links> (exec <id>)
4 counting       : PASS/FAIL — <number> = warehouse (exec <id>)
5 gate           : PASS/FAIL — <n> checks green
```

## First run — 2026-07-31 (the #33 session, staging `bqHstPDi84uOhTCJ`)

```
SMOKE 2026-07-31 · staging post-33 · pre-promote (Release 2)
1 early-feedback : PASS — MRT +3.68s, Holding Trigger? +4.00s, Route Request +4.01s (exec 57926)
2 ladder         : PASS — rung copies distinct · arrival=message-ts LIVE ON PROD (03:24Z promote) · today's prod ladders 1/inbound, silent no-ops
3 solve links    : PASS — Casey Cutsail + Eijiro Kaga FB thread URLs attached; Jasim Eisa (no link on row) named without one (exec 57926)
4 counting       : PASS — "20 chapters", zero links (exec 57927)
5 gate           : PASS — 167/167 GREEN (run twice after the #33 edits, exit 0)
```
