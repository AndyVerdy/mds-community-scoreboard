# FB #4 — The partner judge reads each text once, with every partner named in it

**Ticket:** `FB_BACKLOG.md` #4 · The partner judge is inconsistent inside a batch, "Hector Ai" disappears · S3
**Date:** 2026-09-04 · **Go:** Andy ("do #3 then #4", "go")
**Code:** `~/mds-scorecard-tools/partner_scan.py` (not git-tracked; backup `partner_scan.py.bak-pregrouped`), bench `partner_judge_bench.py`, tests `tests/test_partner_scan.py`.

## Measured first (AC 1)

`partner_judge_bench.py --days 5 --trials 3`, 43 prefilter hits, Anita's Summit offers post = 16 partners (all should be neutral: it is a sponsor listing), 3 known complaints in the window. Read-only.

| variant | shape | calls | Anita's 16 | Hector | complaints kept | stable across trials |
|---|---|---|---|---|---|---|
| batched (today) | 8 mentions per call; the same post repeated once per partner | 6 | 14 not_about_partner · 2 neutral | not_about_partner | 3/3 | 43/43 (2 trials) — wrong, and consistently wrong |
| single | 1 mention per call | 43 | 15–16 neutral | flips (not_about → neutral) | 3/3 | 41/43 |
| grouped | 1 call per text, all its partners listed | 23 | 16 neutral | neutral | 3/3 | 43/43 (3 trials) |
| grouped8 | up to 8 texts per call, each with its partner list | 3 | 16 neutral | neutral | 3/3 | 42/43 (3 trials) |

`temperature` is deprecated for `claude-sonnet-5` (the API rejects it), so it is not a lever.

The original suspicion was right: repeating one 1,200-char post eight times with only the `(partner: X)` header changing makes the model answer about the post, not the partner. It is not random variance; batched was wrong the same way in both trials. Showing the text once and listing the partners under it fixes it, and packing several texts into one call does not bring the problem back.

## Decision

Judge by text. `partner_scan.py` groups prefilter hits by `(ref_kind, ref_id)`, packs up to `TEXTS_PER_CALL = 8` texts into one model call, shows each text once with its partners numbered in one flat sequence across the call, and maps the numbered verdicts back with the existing `parse_verdicts()`. Calls per run go down (6 → 3 on the 5-day window), so the cost statement for AC 5 is: cheaper than today, not one-partner-per-call.

Rejected: single mention per call (7× the calls, less stable, Hector still flipped); one call per text (perfect on this sample but 4× today's calls for one extra stable row — `TEXTS_PER_CALL` is the knob if that ever matters).

## Components

- `group_hits(hits) -> [[hit]]` — groups in first-seen order, hits inside a group in prefilter order.
- `chunk_groups(groups, n) -> [[group]]` — up to `n` texts per call.
- `grouped_listing(chunk) -> str` — `=== TEXT k — partners named in it:` + numbered partner lines (flat numbering across the chunk) + `TEXT k:` + the text once (first 1,200 chars). Our ids never appear.
- `judge(chunk, key) -> {hit id: verdict}` — builds the flat hit list, asks once (retry once, as today), parses with `parse_verdicts(txt, flat)`. A failed chunk marks every hit in it `failed` for #3's reconcile, exactly as a failed batch did.
- `main()` — iterates chunks instead of 8-mention batches; the progress line counts mentions judged. Nothing else changes: prefilter, prompt rules, upsert, reconcile, report.

## Prompt text (the user turn)

```
Several texts, each naming one or more partners. Judge how the author of EACH text talks about EACH partner listed under it — one verdict per number.

=== TEXT 1 — partners named in it:
1. TikTok Shop
2. Receive

TEXT 1:
<text once>

=== TEXT 2 — partners named in it:
3. Veeqo

TEXT 2:
<text once>
```

The system prompt is unchanged, including the sponsor-listing rule (AC 3).

## Tests

`tests/test_partner_scan.py`: grouping keeps first-seen order and puts the same text's hits together; the listing shows each text once and numbers partners flat across texts; chunks hold at most `n` texts; the old `listing_for` test is replaced by these.

## Proof (AC 2, 4) and rollout

1. Baseline SQL: complaints in the 14-day window (partner, author, ref) before the change.
2. `partner_scan.py --days 14` dry run: hit count unchanged (prefilter untouched); read the verdict mix.
3. `--days 14 --apply`: Hector row on post `27084374081239403` exists with verdict `neutral` (SQL); every baseline complaint still present; removal line from #3's reconcile reported.
4. Andy searches "Hector" on `/admin/facebook` (period covering Aug 31) — the portal reads the table per request, no deploy.
5. The 16:25 CDT autopilot runs the new judge unattended; read its `PARTNERS:` line.

## Non-goals

- Changing verdict rules or the prompt's definitions.
- Touching the portal, the digest, the view, or the schema.
