# FB #3 — Stale partner mentions are reconciled, not accumulated

**Ticket:** `FB_BACKLOG.md` #3 · A rejected partner mention is never removed, the table only grows · S2
**Date:** 2026-09-04 · **Approved by:** Andy ("do #3 then #4")
**Code:** `~/mds-scorecard-tools/partner_scan.py` (+ `load_feed.py` helper, `tests/test_partner_scan.py`). Not git-tracked; backup `partner_scan.py.bak-prereconcile` taken before the edit.

## Problem

`partner_scan.py` ends with `supa_upsert(env, "fb_partner_mentions", "ref_kind,ref_id,partner_id", rows)`. A hit the model judges `not_about_partner` is skipped, so a row written by an earlier run under an older prompt survives every later run. The table only grows. On 2026-09-03, after the praise rule was tightened (a sponsor listing is neutral), Anita Petrov's Summit post (`27084374081239403`) still carried 6 stale `praise` rows; they were deleted by hand. Same lesson as `classify_posts.py --apply` labelling only NULLs, fixed there by `relabel_archive.py`.

Consumers of the table: `/admin/facebook` Partner mentions (reads rows by `occurred_at` window), `daily_digest.py` complaints section (24h, `verdict=complaint`), view `digest.fb_report_partner_sentiment`.

## Decision

Reconcile in place. The scanner keeps its upsert and adds one step after judging: delete stored rows that the current rules reject, but only inside the set of texts this run actually re-read, and only for explicit reasons.

Rejected: (B) wipe the window then rewrite — a failed batch or a crash mid-run erases real complaints, the same silent-loss class as the truncated batches of 2026-09-03. (C) soft-delete column — touches schema, view, portal and digest, and the table still only grows.

## Scope of a run (AC 2)

A stored row is *in scope* when all three hold:

1. its `(ref_kind, ref_id)` is one of the posts/comments `texts()` returned for this run (window by `created_time >= now - days`, `text is not null`);
2. its `partner_id` is in the current published catalog (`partners()`);
3. its `occurred_at >= since` (cheap pre-filter for the fetch; equal to the text's `created_time`).

Rows outside scope are never read for deletion. A run with `--days 3` cannot touch a row from six months ago because that text was not fetched.

## Delete reasons (only these two)

- **re-judged `not_about_partner`** — the key `(kind, ref, partner)` was a prefilter hit this run and the model's verdict for it is `not_about_partner`.
- **no longer matches** — the key is in scope but was not a prefilter hit at all (the name rule changed, e.g. a COMMON word tightened). Included on purpose: "current rules" means the prefilter too.

Never deleted, always counted and printed:

- key was in a batch the model failed on (`judge()` returned `{}`) — *unjudged*;
- key was in a successful batch but missing from the reply — *unjudged* (an omission is not a rejection);
- `partner_id` not in the current catalog — *out of catalog* (out of scope by rule 2; reported so a disappearing partner is visible, not silent).

A row whose key was re-judged `complaint` / `praise` / `neutral` is refreshed by the existing upsert.

## Reporting (AC 3)

Second-to-last stdout line, so `auto_import.py` (which logs the last 3 lines) always carries it:

```
🧹 removed 6 (6 re-judged not_about_partner · 0 no longer match) · left 2 unjudged · 0 out of catalog
```

Dry run (no `--apply`) prints the same numbers as `would remove`. Each removed row is also listed one per line above the summary (`partner — author — old verdict — reason`) so the run output says exactly what left the table.

## Mechanism

- `load_feed.supa_delete(env, table, match)` — PostgREST `DELETE /rest/v1/<table>?k=eq.v&…` with `Prefer: return=representation`; returns the deleted rows so the count is real, not assumed. One call per row (typical volume 0–10 a day).
- `partner_scan.reconcile(stored, scanned_refs, hit_keys, verdicts, failed_keys, catalog_ids)` — pure function, no I/O: returns `(to_delete, counts)` where each `to_delete` entry carries its reason. This is the unit under test.
- `texts()` pages properly (posts and comments both loop in pages of 1000 until a short page) so `--days 3650` reads history instead of silently truncating at 2,000 posts / 10,000 comments. Comments are ordered by `comment_id` as today; posts by `post_id`.

## Backfill path (AC 5)

Same script, larger window: `python3 partner_scan.py --days 30 --apply` today (every existing row has `occurred_at >= 2026-08-19`), `--days 3650` for full history if ever wanted. Documented in `FB_PIPELINE.md` next to `relabel_archive.py`. No second script: one reconcile logic, one place to drift.

## Tests

`tests/test_partner_scan.py` (unittest, no network): a row in scope re-judged `not_about_partner` is deleted with that reason; a row in scope with no hit is deleted as *no longer match*; a row whose text was not scanned is untouched; a row in a failed batch is untouched and counted unjudged; a row missing from a good reply is untouched; a row for an out-of-catalog partner is untouched and counted; a row re-judged neutral is not in the delete list.

## Proof (AC 4) and rollout

1. Run the old-prompt copy `python3 partner_scan.py.bak-praiserule --days 5 --apply` to recreate the stale state on Anita's post (writes wrong praise rows to the live table for a few minutes; only the admin tab shows praise, the Slack card reads complaints only).
2. Run the new scanner `--days 5 --apply`. Expect Anita's post to end at 5 neutral, 0 praise, and the removal line to name the count. Verify with SQL after, never before.
3. Run `--days 30 --apply` as the history pass; record the removal line.
4. Ship before the 16:25 CDT autopilot (`auto_import.py` runs `partner_scan.py --days 3 --apply`); its log line is the second live proof.

## Non-goals

- Fixing the in-batch judge variance (Hector) — that is #4, next.
- Any change to the portal, the digest, the view, or the schema.
