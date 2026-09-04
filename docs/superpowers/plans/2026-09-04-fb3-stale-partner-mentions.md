# FB #3 — Reconcile stale partner mentions: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `partner_scan.py` removes stored partner mentions that the current rules reject, scoped to the texts it re-read, and says how many it removed and why.

**Architecture:** A pure `reconcile()` decides deletions from sets the run already has (scanned refs, prefilter hits, verdicts, failed batches, catalog). `main()` fetches the stored rows for the window, calls `reconcile()`, deletes row by row through a new `supa_delete()` in `load_feed.py`, and prints the summary as the second-to-last line so `auto_import.py` logs it. `texts()` gets real paging so the same script is the backfill path.

**Tech Stack:** Python 3.12, curl via subprocess (this Mac's urllib SSL is broken), Supabase PostgREST (`digest` schema), `unittest`.

## Global Constraints

- Code lives in `/Users/Born/mds-scorecard-tools/` — NOT git-tracked. Backup already taken: `partner_scan.py.bak-prereconcile`. Take `load_feed.py.bak-prereconcile` before editing that file.
- Docs live in the Scorecard repo worktree `/Users/Born/Scorecard/.claude/worktrees/fb3-20260904` on branch `fb3-stale-mentions-20260904`. Never commit on `main`; merge with `--no-ff` only when proven.
- Conflict key of the table: `ref_kind,ref_id,partner_id`. Verdict CHECK allows only `complaint|praise|neutral`.
- Only two delete reasons exist: `re-judged not_about_partner` and `no longer matches a partner name`. Rows in failed batches, rows missing from a good reply, and rows for partners not in the published catalog are never deleted.
- Tests run from the tools folder: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan -v` (pytest is not installed).
- Ship before the 16:25 CDT autopilot run (`auto_import.py` → `partner_scan.py --days 3 --apply`).

---

### Task 1: `reconcile()` — the pure decision

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/partner_scan.py` (add `key()` and `reconcile()` above `main()`)
- Create: `/Users/Born/mds-scorecard-tools/tests/test_partner_scan.py`

**Interfaces:**
- Produces: `key(kind: str, ref: str, pid: str) -> str` returning `f"{kind}:{ref}:{pid}"` (identical to the `id` the hits already carry).
- Produces: `reconcile(stored, scanned_refs, hit_keys, verdicts, failed_keys, catalog_ids) -> (to_delete, counts)` where `stored` is a list of dicts with `ref_kind, ref_id, partner_id, partner_name, author_name, verdict`; `scanned_refs` is a set of `(ref_kind, ref_id)`; `hit_keys` a set of key strings; `verdicts` a dict key → verdict string; `failed_keys` a set of key strings; `catalog_ids` a set of partner ids. `to_delete` is a list of `(row, reason)`; `counts` is a `collections.Counter` with keys `out_of_window`, `out_of_catalog`, `unjudged`, `kept`.

- [ ] **Step 1: Write the failing tests**

```python
# /Users/Born/mds-scorecard-tools/tests/test_partner_scan.py
import unittest
import partner_scan as ps


def row(kind="post", ref="p1", pid="hector", verdict="praise"):
    return {"ref_kind": kind, "ref_id": ref, "partner_id": pid,
            "partner_name": pid, "author_name": "Anita", "verdict": verdict}


class Reconcile(unittest.TestCase):
    CAT = {"hector", "euka"}

    def test_rejudged_not_about_partner_is_deleted_with_reason(self):
        k = ps.key("post", "p1", "hector")
        dels, counts = ps.reconcile([row()], {("post", "p1")}, {k}, {k: "not_about_partner"}, set(), self.CAT)
        self.assertEqual([(r["partner_id"], why) for r, why in dels], [("hector", "re-judged not_about_partner")])
        self.assertEqual(counts["kept"], 0)

    def test_no_longer_a_hit_is_deleted_as_no_longer_matches(self):
        dels, _ = ps.reconcile([row()], {("post", "p1")}, set(), {}, set(), self.CAT)
        self.assertEqual(dels[0][1], "no longer matches a partner name")

    def test_text_not_scanned_is_untouched(self):
        dels, counts = ps.reconcile([row(ref="old")], {("post", "p1")}, set(), {}, set(), self.CAT)
        self.assertEqual(dels, [])
        self.assertEqual(counts["out_of_window"], 1)

    def test_failed_batch_is_untouched_and_counted_unjudged(self):
        k = ps.key("post", "p1", "hector")
        dels, counts = ps.reconcile([row()], {("post", "p1")}, {k}, {}, {k}, self.CAT)
        self.assertEqual(dels, [])
        self.assertEqual(counts["unjudged"], 1)

    def test_missing_from_a_good_reply_is_untouched(self):
        k = ps.key("post", "p1", "hector")
        dels, counts = ps.reconcile([row()], {("post", "p1")}, {k}, {}, set(), self.CAT)
        self.assertEqual(dels, [])
        self.assertEqual(counts["unjudged"], 1)

    def test_partner_out_of_catalog_is_untouched_and_counted(self):
        dels, counts = ps.reconcile([row(pid="gone")], {("post", "p1")}, set(), {}, set(), self.CAT)
        self.assertEqual(dels, [])
        self.assertEqual(counts["out_of_catalog"], 1)

    def test_rejudged_neutral_is_kept(self):
        k = ps.key("post", "p1", "hector")
        dels, counts = ps.reconcile([row()], {("post", "p1")}, {k}, {k: "neutral"}, set(), self.CAT)
        self.assertEqual(dels, [])
        self.assertEqual(counts["kept"], 1)

    def test_comment_and_post_with_same_ref_are_different_keys(self):
        kp, kc = ps.key("post", "x", "hector"), ps.key("comment", "x", "hector")
        stored = [row(kind="post", ref="x"), row(kind="comment", ref="x")]
        dels, _ = ps.reconcile(stored, {("post", "x"), ("comment", "x")}, {kp, kc},
                               {kp: "neutral", kc: "not_about_partner"}, set(), self.CAT)
        self.assertEqual([r["ref_kind"] for r, _ in dels], ["comment"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan -v`
Expected: every test errors with `AttributeError: module 'partner_scan' has no attribute 'key'` (or `reconcile`).

- [ ] **Step 3: Add `key()` and `reconcile()` to `partner_scan.py`** (insert directly above `def main():`, and add `from collections import Counter` to the imports at the top, removing the local `from collections import Counter` inside `main()`)

```python
def key(kind, ref, pid):
    """The identity of one mention — the same string the hits carry as `id`."""
    return f"{kind}:{ref}:{pid}"


def reconcile(stored, scanned_refs, hit_keys, verdicts, failed_keys, catalog_ids):
    """Decide which STORED mentions the current rules reject (#3 — the table used to only grow).

    stored        rows already in digest.fb_partner_mentions for the window
    scanned_refs  {(ref_kind, ref_id)} this run actually read — the ONLY rows in scope
    hit_keys      {key} the prefilter produced this run
    verdicts      {key: verdict} the model returned (judged keys only)
    failed_keys   {key} in batches the model failed on
    catalog_ids   {partner_id} currently published

    Only two reasons delete a row: the model re-judged it not_about_partner, or the name no longer
    matches any partner (the prefilter rule changed). A row in a failed batch, a row the model left
    out of an otherwise good reply, and a row for a partner no longer in the catalog are never
    deleted — they are counted so the run output says what was left alone and why.
    Returns (to_delete, counts): to_delete = [(row, reason)], counts = Counter.
    """
    to_delete, counts = [], Counter()
    for r in stored:
        if (r["ref_kind"], r["ref_id"]) not in scanned_refs:
            counts["out_of_window"] += 1
            continue
        if r["partner_id"] not in catalog_ids:
            counts["out_of_catalog"] += 1
            continue
        k = key(r["ref_kind"], r["ref_id"], r["partner_id"])
        if k not in hit_keys:
            to_delete.append((r, "no longer matches a partner name"))
            continue
        if k in failed_keys or k not in verdicts:
            counts["unjudged"] += 1
            continue
        if verdicts[k] == "not_about_partner":
            to_delete.append((r, "re-judged not_about_partner"))
            continue
        counts["kept"] += 1
    return to_delete, counts
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan -v`
Expected: `Ran 8 tests ... OK`

- [ ] **Step 5: Snapshot** — no git here; `cp partner_scan.py partner_scan.py.wip-task1` is optional. The real safety net is `partner_scan.py.bak-prereconcile`.

---

### Task 2: `supa_delete()` in `load_feed.py`

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/load_feed.py` (add below `supa_upsert`, add `from urllib.parse import quote` to imports)
- Modify: `/Users/Born/mds-scorecard-tools/tests/test_partner_scan.py` (append a test class)

**Interfaces:**
- Produces: `supa_delete(env, table, match: dict) -> list` — PostgREST DELETE on `digest.<table>` filtered by every `k=eq.v` in `match`, `Prefer: return=representation`, returns the deleted rows (empty list when nothing matched).

- [ ] **Step 1: Write the failing test** (append to `tests/test_partner_scan.py`, above the `if __name__` block)

```python
import load_feed


class SupaDelete(unittest.TestCase):
    def test_builds_a_filtered_delete_and_returns_deleted_rows(self):
        seen = {}

        def fake_curl(args, payload=None):
            seen["args"] = args
            return [{"ref_id": "abc=="}]

        real = load_feed.curl_json
        load_feed.curl_json = fake_curl
        try:
            env = {"SUPABASE_URL": "https://x.supabase.co", "SUPABASE_SECRET_KEY": "k"}
            out = load_feed.supa_delete(env, "fb_partner_mentions",
                                        {"ref_kind": "comment", "ref_id": "abc==", "partner_id": "p/1"})
        finally:
            load_feed.curl_json = real
        self.assertEqual(out, [{"ref_id": "abc=="}])
        url = seen["args"][0]
        self.assertTrue(url.startswith("https://x.supabase.co/rest/v1/fb_partner_mentions?"))
        self.assertIn("ref_kind=eq.comment", url)
        self.assertIn("ref_id=eq.abc%3D%3D", url)      # '=' must be encoded or PostgREST splits the filter
        self.assertIn("partner_id=eq.p%2F1", url)
        self.assertIn("DELETE", seen["args"])
        self.assertIn("Prefer: return=representation", seen["args"])
        self.assertIn("Content-Profile: digest", seen["args"])
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan.SupaDelete -v`
Expected: `AttributeError: module 'load_feed' has no attribute 'supa_delete'`

- [ ] **Step 3: Back up and implement**

```bash
cp /Users/Born/mds-scorecard-tools/load_feed.py /Users/Born/mds-scorecard-tools/load_feed.py.bak-prereconcile
```

Add `from urllib.parse import quote` to the imports of `load_feed.py`, then add below `supa_upsert`:

```python
def supa_delete(env, table, match):
    """PostgREST DELETE in the digest schema, filtered by every k=eq.v in `match`.
    Returns the rows PostgREST actually deleted (return=representation), so a caller counts what
    left the table instead of assuming. Values are percent-encoded: comment ids are base64 and a
    bare '=' would be read as part of the filter syntax."""
    q = "&".join(f"{k}=eq.{quote(str(v), safe='')}" for k, v in match.items())
    return curl_json([
        f"{env['SUPABASE_URL']}/rest/v1/{table}?{q}",
        "-X", "DELETE",
        "-H", f"apikey: {env['SUPABASE_SECRET_KEY']}",
        "-H", f"Authorization: Bearer {env['SUPABASE_SECRET_KEY']}",
        "-H", "Content-Profile: digest",
        "-H", "Accept-Profile: digest",
        "-H", "Prefer: return=representation",
    ]) or []
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan -v`
Expected: `Ran 9 tests ... OK`

---

### Task 3: Wire reconcile into `main()`, page `texts()`, report

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/partner_scan.py` — `texts()` (lines 88–103), `main()` (lines 139–189), imports (line 24)

**Interfaces:**
- Consumes: `key`, `reconcile` (Task 1); `supa_delete` (Task 2).
- Changes: `texts(env, since)` now takes the ISO timestamp string; `stored_mentions(env, since)` is new; `main()` computes `since` once.

- [ ] **Step 1: Change the import line** (line 24)

```python
from load_feed import env_local, curl_json, supa_upsert, supa_delete, die
```

- [ ] **Step 2: Replace `texts()` with a paged version that takes `since`**

```python
PAGE = 1000   # PostgREST caps every response at 1000 rows


def _paged(env, path, hdr):
    """Every row behind a PostgREST path, 1000 at a time. The old single-shot limits (2,000 posts,
    10 comment pages) silently truncated a long window, which is why --days 3650 was not a backfill."""
    out, off = [], 0
    while True:
        page = curl_json([f"{env['SUPABASE_URL']}/rest/v1/{path}&limit={PAGE}&offset={off}"] + hdr) or []
        out.extend(page)
        if len(page) < PAGE:
            return out
        off += PAGE


def texts(env, since):
    hdr = ["-H", f"apikey: {env['SUPABASE_SECRET_KEY']}",
           "-H", f"Authorization: Bearer {env['SUPABASE_SECRET_KEY']}", "-H", "Accept-Profile: digest"]
    out = []
    for row in _paged(env, f"fb_posts?select=post_id,author_name,text,created_time"
                           f"&created_time=gte.{since}&text=not.is.null&order=post_id", hdr):
        out.append(("post", row["post_id"], row["post_id"], row.get("author_name"), row.get("text"), row["created_time"]))
    for row in _paged(env, f"fb_comments?select=comment_id,post_id,author_name,text,created_time"
                           f"&created_time=gte.{since}&text=not.is.null&order=comment_id", hdr):
        out.append(("comment", row["comment_id"], row["post_id"], row.get("author_name"), row.get("text"), row["created_time"]))
    return out


def stored_mentions(env, since):
    """What the table already says for the window — the candidates reconcile() may remove."""
    hdr = ["-H", f"apikey: {env['SUPABASE_SECRET_KEY']}",
           "-H", f"Authorization: Bearer {env['SUPABASE_SECRET_KEY']}", "-H", "Accept-Profile: digest"]
    return _paged(env, "fb_partner_mentions?select=ref_kind,ref_id,partner_id,partner_name,author_name,verdict"
                       f"&occurred_at=gte.{since}&order=ref_id,partner_id", hdr)
```

- [ ] **Step 3: Rewrite `main()`**

```python
def main():
    apply_ = "--apply" in sys.argv
    days = next((int(sys.argv[i + 1]) for i, a in enumerate(sys.argv) if a == "--days"), 14)
    env, api_key = env_local(), env_anthropic().get("CENTURION_ANTHROPIC_API_KEY") or die("no API key")
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    pl = partners(env)
    items = texts(env, since)
    hits = []
    for kind, ident, post_id, author, text, when in items:
        for pid, name, rx in pl:
            if rx.search(text or ""):
                # The id must carry the PARTNER too. Keyed on kind:ref alone, a post naming 16
                # partners produced 16 hits sharing one id — judge() keys its dict by id, so fifteen
                # verdicts were overwritten and all sixteen took whichever came last. Anita's Summit
                # offers post (16 partners, 2026-08-31) recorded ZERO mentions because of this.
                hits.append({"id": key(kind, ident, pid), "kind": kind, "ref": ident, "post_id": post_id,
                             "partner_id": pid, "partner": name, "author": author, "text": text, "when": when})
    print(f"scanned {len(items)} posts+comments from the last {days}d → {len(hits)} partner-name matches")

    rows, skipped, verdicts, failed_keys = [], 0, {}, set()
    for i in range(0, len(hits), BATCH_JUDGE):
        batch = hits[i:i + BATCH_JUDGE]
        got = judge(batch, api_key)
        if not got:
            skipped += len(batch)
            failed_keys.update(b["id"] for b in batch)
        for b in batch:
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
        print(f"  …{min(i + BATCH_JUDGE, len(hits))}/{len(hits)}")

    if skipped:
        print(f"⚠️ {skipped} of {len(hits)} matches were NOT judged — batches the model failed to return "
              f"parseable JSON for. Those partner mentions are MISSING, not absent.")
    print("verdicts:", dict(Counter(r["verdict"] for r in rows)))
    for r in rows:
        if r["verdict"] == "complaint":
            print(f"  ❗ {r['partner_name']} — {r['author_name']}: {r['quote'][:120]}")

    # #3 — what the table already says for this window, judged again by the CURRENT rules. Scope is
    # exactly the texts read above: a --days 3 run cannot reach a row from six months ago. A batch
    # the model failed on is left alone (a missing verdict is not a rejection).
    stored = stored_mentions(env, since)
    scanned_refs = {(kind, str(ident)) for kind, ident, *_ in items}
    to_delete, counts = reconcile(stored, scanned_refs, {h["id"] for h in hits}, verdicts, failed_keys,
                                  {pid for pid, _, _ in pl})
    for r, why in to_delete:
        print(f"  🧹 {r['partner_name']} — {r['author_name']}: was {r['verdict']} — {why}")
    reasons = Counter(why for _, why in to_delete)
    detail = (f"({reasons['re-judged not_about_partner']} re-judged not_about_partner · "
              f"{reasons['no longer matches a partner name']} no longer match) · "
              f"left {counts['unjudged']} unjudged · {counts['out_of_catalog']} out of catalog")

    if not apply_:
        print(f"DRY RUN — would write {len(rows)} rows · would remove {len(to_delete)} {detail}")
        return
    if rows:
        supa_upsert(env, "fb_partner_mentions", "ref_kind,ref_id,partner_id", rows)
    gone = 0
    for r, _ in to_delete:
        gone += len(supa_delete(env, "fb_partner_mentions",
                                {"ref_kind": r["ref_kind"], "ref_id": r["ref_id"], "partner_id": r["partner_id"]}))
    print(f"🧹 removed {gone} {detail}")
    print(f"✅ wrote {len(rows)} mentions")
```

Notes for the implementer: the old `if not hits: return` is gone on purpose — with no hits there can still be rows to remove as "no longer matches". The `from collections import Counter` moved to the top of the file in Task 1. The removal line is printed BEFORE the "wrote" line so `auto_import.py`'s last-3-lines log capture always includes it.

- [ ] **Step 4: Run the unit tests again, then a live dry run**

Run: `cd /Users/Born/mds-scorecard-tools && python3 -m unittest tests.test_partner_scan -v`
Expected: `Ran 9 tests ... OK`

Run: `cd /Users/Born/mds-scorecard-tools && python3 partner_scan.py --days 5`
Expected: ends with one line `DRY RUN — would write N rows · would remove M (a re-judged not_about_partner · b no longer match) · left c unjudged · d out of catalog`. Nothing is written. Record N and M.

- [ ] **Step 5: Syntax check the whole file** — `python3 -m py_compile partner_scan.py load_feed.py`

---

### Task 4: Proof on Anita's post (AC 4) and the history pass (AC 5)

**Files:** none changed. Live runs only, in this order.

- [ ] **Step 1: Baseline SQL** (Supabase, read-only)

```sql
select verdict, count(*) from digest.fb_partner_mentions where post_id = '27084374081239403' group by 1;
select count(*) from digest.fb_partner_mentions;
```
Expected before: neutral 5, no praise; total 53.

- [ ] **Step 2: Recreate the stale state with the OLD prompt** (the copy taken before the praise rule)

```bash
cd /Users/Born/mds-scorecard-tools && python3 partner_scan.py.bak-praiserule --days 5 --apply
```
Expected: Anita's post gains praise rows (the old rule called the offer listing praise). Re-run the first SQL and record the praise count — that is the "before".

- [ ] **Step 3: Run the NEW scanner over the same window**

```bash
cd /Users/Born/mds-scorecard-tools && python3 partner_scan.py --days 5 --apply
```
Expected: the `🧹 removed …` line names the rows that flipped; then SQL shows Anita's post at neutral 5, praise 0. If the model's batch variance (#4) leaves a different neutral count, record the actual number — the AC is "no stale praise, no hand SQL".

- [ ] **Step 4: History pass**

```bash
cd /Users/Born/mds-scorecard-tools && python3 partner_scan.py --days 30 --apply
```
Expected: covers every existing row (oldest `occurred_at` is 2026-08-19). Record the removal line and the verdict counts before/after (`select verdict, count(*) from digest.fb_partner_mentions group by 1`).

- [ ] **Step 5: Confirm nothing outside the window moved** — the total row count minus the removed rows equals the new total; rows with `occurred_at < since` are unchanged (`select count(*) … where occurred_at < now() - interval '30 days'` before and after must match).

---

### Task 5: Docs, board, logs, merge

**Files:**
- Modify: `/Users/Born/mds-scorecard-tools/FB_PIPELINE.md` — new section after "Classifying ask / give / value add"
- Modify (worktree): `FB_BACKLOG.md` — move #3 block to CLOSED with results, AC checklist, before/after numbers
- Modify (worktree): `SESSION_LOG_SCORECARD.md` (prepend entry), `SESSION_LOG.md` (one index line)

- [ ] **Step 1: `FB_PIPELINE.md` section**

```markdown
## Partner mentions are reconciled, not accumulated (#3, 2026-09-04)

`partner_scan.py` used to only INSERT/UPDATE `digest.fb_partner_mentions`; a hit judged
`not_about_partner` was skipped, so a row written under an older prompt survived every later run
(Anita's Summit post kept 6 stale `praise` rows after the sponsor-listing rule; they needed hand SQL).

Now every run ends with a reconcile step: stored rows whose text this run actually re-read are
deleted when the model re-judges them `not_about_partner`, or when the name no longer matches any
partner. Scope is exactly the window scanned — `--days 3` cannot touch a six-month-old row. Rows in a
batch the model failed on, rows the model left out of a good reply, and rows for partners no longer in
the published catalog are never deleted; they are counted in the output line
(`🧹 removed N (a re-judged not_about_partner · b no longer match) · left c unjudged · d out of catalog`),
which `auto_import.py` captures in its log. Dry run prints `would remove`.

**Backfill after a rule change** — same script, bigger window (the fetch pages properly now):

```bash
python3 partner_scan.py --days 30          # dry run: shows what would move
python3 partner_scan.py --days 30 --apply
```
```

- [ ] **Step 2: Board + logs in the worktree** — write the #3 CLOSED block (story kept, results, AC 1–5 met/not with the live numbers from Task 4, before/after counts), the `SESSION_LOG_SCORECARD.md` entry (what shipped, the proof numbers, the 16:25 autopilot line if already available, next = #4), and one `SESSION_LOG.md` index line.

- [ ] **Step 3: Commit and merge**

```bash
cd /Users/Born/Scorecard/.claude/worktrees/fb3-20260904
git add docs/superpowers/specs/2026-09-04-fb3-stale-partner-mentions-design.md docs/superpowers/plans/2026-09-04-fb3-stale-partner-mentions.md FB_BACKLOG.md SESSION_LOG_SCORECARD.md SESSION_LOG.md
git commit -m "FB #3: partner mentions reconciled — scanner removes what current rules reject (spec, plan, board, log)"
git push -u origin fb3-stale-mentions-20260904
git fetch origin && git rebase origin/main
cd /Users/Born/Scorecard && git switch main && git pull --ff-only && git merge --no-ff fb3-stale-mentions-20260904 && git push
```
If `git log origin/main..main` shows a commit that is not ours before the push, stop and let its owner merge.

---

## Self-review

- Spec coverage: scope rules → Task 1 + `stored_mentions`/`scanned_refs` in Task 3; two delete reasons → Task 1; never-deleted classes → Task 1 tests; reporting line placement → Task 3 Step 3; `supa_delete` with real count → Task 2; paging/backfill → Task 3 Step 2 + Task 4 Step 4 + Task 5 docs; proof → Task 4; non-goals respected (no portal/digest/schema change).
- Placeholders: none.
- Type consistency: `key()` string equals hit `id`; `reconcile()` signature identical in Task 1 tests and Task 3 call; `supa_delete(env, table, match)` identical in Task 2 and Task 3.
