# FB #4 — Grouped partner judge: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `partner_scan.py` judges each text once with every partner named in it listed underneath, so a partner plainly named in a post is judged about that partner and "Hector" becomes searchable.

**Architecture:** Three pure helpers (`group_hits`, `chunk_groups`, `grouped_listing`) replace the 8-mentions-per-call listing; `judge()` takes a chunk of texts, asks once, and maps numbered verdicts back through the existing `parse_verdicts()`. `main()` iterates chunks. Prefilter, prompt rules, upsert, #3 reconcile and reporting are untouched.

**Tech Stack:** Python 3.12, curl via subprocess, Claude Messages API (`claude-sonnet-5`, no `temperature` — deprecated), `unittest`.

## Global Constraints

- Code is in `/Users/Born/mds-scorecard-tools/`, NOT git-tracked. Take `partner_scan.py.bak-pregrouped` before editing.
- Docs go on the Scorecard branch `fb3-stale-mentions-20260904` (worktree `.claude/worktrees/fb3-20260904`); merge `--no-ff` into `main` only when proven.
- `TEXTS_PER_CALL = 8`. The system prompt and its sponsor-listing rule do not change.
- Tests: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan -v`.
- Ship before the 16:25 CDT autopilot if possible; never edit the file while a run is in progress (`ps aux | grep partner_scan`).

---

### Task 1: Grouping helpers (pure)

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/partner_scan.py` (replace `listing_for`; add `TEXTS_PER_CALL`, `group_hits`, `chunk_groups`, `grouped_listing`)
- Modify: `/Users/Born/mds-scorecard-tools/tests/test_partner_scan.py` (replace the `listing_for` test in `JudgeIds` with a `GroupedJudge` class)

**Interfaces:**
- Produces: `group_hits(hits: list[dict]) -> list[list[dict]]` (first-seen order by `(kind, ref)`); `chunk_groups(groups, n) -> list[list[list[dict]]]`; `grouped_listing(chunk) -> str`; constant `TEXTS_PER_CALL = 8`.
- Consumes: hit dicts with keys `id, kind, ref, partner, text` (as `main()` builds them).

- [ ] **Step 1: Write the failing tests** — in `tests/test_partner_scan.py`, delete `test_listing_numbers_items_instead_of_exposing_ids` and add:

```python
def hit(kind, ref, pid, partner=None, text="body"):
    return {"id": ps.key(kind, ref, pid), "kind": kind, "ref": ref, "partner": partner or pid, "text": text}


class GroupedJudge(unittest.TestCase):
    def test_hits_are_grouped_by_text_in_first_seen_order(self):
        hits = [hit("post", "p1", "a"), hit("comment", "c1", "b"), hit("post", "p1", "c")]
        self.assertEqual([[h["id"] for h in g] for g in ps.group_hits(hits)],
                         [["post:p1:a", "post:p1:c"], ["comment:c1:b"]])

    def test_listing_shows_each_text_once_and_numbers_partners_flat(self):
        chunk = [[hit("post", "p1", "a", "Alpha", "TEXT-ONE"), hit("post", "p1", "c", "Charlie", "TEXT-ONE")],
                 [hit("comment", "c1", "b", "Bravo", "TEXT-TWO")]]
        listing = ps.grouped_listing(chunk)
        self.assertEqual(listing.count("TEXT-ONE"), 1)
        self.assertEqual(listing.count("TEXT-TWO"), 1)
        for line in ("1. Alpha", "2. Charlie", "3. Bravo", "=== TEXT 1", "=== TEXT 2"):
            self.assertIn(line, listing)
        self.assertNotIn("post:p1", listing)

    def test_chunks_hold_at_most_n_texts(self):
        groups = [[hit("post", f"p{i}", "a")] for i in range(19)]
        self.assertEqual([len(c) for c in ps.chunk_groups(groups, 8)], [8, 8, 3])
```

- [ ] **Step 2: Run to verify they fail** — `python3 -m unittest tests.test_partner_scan.GroupedJudge -v` → `AttributeError: module 'partner_scan' has no attribute 'group_hits'`.

- [ ] **Step 3: Implement** — replace `listing_for()` in `partner_scan.py` with:

```python
TEXTS_PER_CALL = 8   # texts per model call; measured 2026-09-04 (partner_judge_bench.py): 3 calls, 42/43 stable


def group_hits(hits):
    """Hits that share a text, together, in first-seen order. The judge reads each text ONCE."""
    groups, order = {}, []
    for h in hits:
        k = (h["kind"], h["ref"])
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(h)
    return [groups[k] for k in order]


def chunk_groups(groups, n):
    return [groups[i:i + n] for i in range(0, len(groups), n)]


def grouped_listing(chunk):
    """Each text once, its partners numbered in ONE flat sequence across the call. The old listing put
    the same 1,200-char post in the call eight times with only '(partner: X)' changing, and the model
    answered about the post instead of the partner: Anita's 16-partner offers post came back 14
    not_about_partner in both trials of the bench (2026-09-04). Shown once with the partners listed
    under it, all 16 are neutral and Hector is found. Our ids never appear — a number cannot be
    rewritten (see parse_verdicts)."""
    parts, n = [], 0
    for gi, group in enumerate(chunk, 1):
        names = "\n".join(f"{n + j}. {h['partner']}" for j, h in enumerate(group, 1))
        n += len(group)
        parts.append(f"=== TEXT {gi} — partners named in it:\n{names}\n\nTEXT {gi}:\n{group[0]['text'][:1200]}")
    return ("Several texts, each naming one or more partners. Judge how the author of EACH text talks about "
            "EACH partner listed under it — one verdict per number.\n\n" + "\n\n".join(parts))
```

- [ ] **Step 4: Run all tests** — `python3 -m unittest tests.test_partner_scan -v` → `Ran 14 tests ... OK`.

---

### Task 2: `judge()` takes a chunk of texts; `main()` iterates chunks

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/partner_scan.py` — `judge()` and the judging loop in `main()`

**Interfaces:**
- Changes: `judge(chunk, key) -> {hit id: verdict dict}` where `chunk` is a list of groups (from `chunk_groups`).

- [ ] **Step 1: Back up** — `cp partner_scan.py partner_scan.py.bak-pregrouped`

- [ ] **Step 2: Replace `judge()`**

```python
def judge(chunk, key):
    """One model call for up to TEXTS_PER_CALL texts. Returns {hit id: verdict}; {} when the model
    failed twice (the caller marks every hit in the chunk failed, so #3's reconcile leaves them alone).
    max_tokens 4000: a 2,000 ceiling truncated the JSON mid-string on 2026-09-03 and whole batches were
    silently dropped."""
    flat = [h for g in chunk for h in g]
    payload = {"model": MODEL, "max_tokens": 4000, "system": SYSTEM,
               "messages": [{"role": "user", "content": f"Judge these {len(flat)} mentions.\n\n{grouped_listing(chunk)}"}]}
    try:
        return parse_verdicts(_ask(payload, key), flat)
    except Exception as e:
        print(f"  ⚠️ model call failed ({e}) — retrying once")
        try:
            return parse_verdicts(_ask(payload, key), flat)
        except Exception as e2:
            print(f"  ⚠️ retry failed too ({e2}) — {len(flat)} mentions in this call skipped")
            return {}
```

- [ ] **Step 3: Replace the judging loop in `main()`** (from `rows, skipped, verdicts, failed_keys = ...` through the progress print):

```python
    rows, skipped, verdicts, failed_keys, done = [], 0, {}, set(), 0
    for chunk in chunk_groups(group_hits(hits), TEXTS_PER_CALL):
        flat = [h for g in chunk for h in g]
        got = judge(chunk, api_key)
        if not got:
            skipped += len(flat)
            failed_keys.update(b["id"] for b in flat)
        for b in flat:
            v = got.get(b["id"])
            if not v:
                continue
            verdicts[b["id"]] = v.get("verdict")
            if v.get("verdict") == "not_about_partner":
                continue
            rows.append({"ref_kind": b["kind"], "ref_id": str(b["ref"]), "post_id": str(b["post_id"]),
                         "partner_id": b["partner_id"], "partner_name": b["partner"],
                         "author_name": b["author"], "verdict": v["verdict"],
                         "quote": (v.get("quote") or "")[:500],
                         "confidence": float(v.get("confidence", 0)), "occurred_at": b["when"]})
        done += len(flat)
        print(f"  …{done}/{len(hits)}")
```

Delete the now-unused `BATCH_JUDGE` constant and its comment.

- [ ] **Step 4: Verify** — `python3 -m py_compile partner_scan.py && python3 -m unittest tests.test_partner_scan` → OK; then `python3 partner_scan.py --days 14` (dry run) → hit count equals the previous 14-day count; verdict mix shows Anita's partners neutral.

---

### Task 3: Proof and rollout

- [ ] **Step 1: Baseline SQL** (before apply): complaints in the last 14 days — `select partner_name, author_name, ref_kind, ref_id from digest.fb_partner_mentions where verdict='complaint' and occurred_at >= now() - interval '14 days' order by 1,2;`
- [ ] **Step 2: Apply** — `python3 partner_scan.py --days 14 --apply`; record the verdict line, the 🧹 line, the wrote line.
- [ ] **Step 3: SQL after** — Hector row: `select verdict, quote from digest.fb_partner_mentions where post_id='27084374081239403' and partner_name ilike 'hector%';` → `neutral`. Baseline complaints still present (re-run Step 1, compare). Anita's post: 16 rows, all neutral.
- [ ] **Step 4: Ask Andy to search "Hector" on `/admin/facebook`** (period covering Aug 31, e.g. Last 30 days).
- [ ] **Step 5: 16:25 CDT autopilot** — read the `PARTNERS:` line in `auto_import.log` after 16:46.

---

### Task 4: Docs, board, logs, merge

- [ ] `FB_PIPELINE.md`: in the #3 section's id-trap paragraph, add the grouped-judge paragraph (what the model sees now, why, the bench numbers, `TEXTS_PER_CALL`).
- [ ] `FB_BACKLOG.md`: move #4 to CLOSED with the bench table, AC checklist, before/after (Hector 0 → 1 row; Anita 3 neutral → 16 neutral; calls 6 → 3 on 5 days).
- [ ] `SESSION_LOG_SCORECARD.md` entry + `SESSION_LOG.md` index line. Commit on the branch, rebase on `origin/main`, merge `--no-ff`, push.

## Self-review

- Spec coverage: grouping/chunking/listing → Task 1; judge + main → Task 2; proof AC 2/3/4 → Task 3; cost statement (AC 5) → spec Decision + board close; docs → Task 4.
- Placeholders: none. Types: `judge(chunk, key)` used identically in Task 2 Steps 2 and 3; `parse_verdicts(txt, flat)` as defined in #3.
