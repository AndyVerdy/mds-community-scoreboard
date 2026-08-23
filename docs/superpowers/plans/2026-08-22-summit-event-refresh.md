# Summit Event Refresh (#113) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One command takes a GroupOS event export and makes the `event` schema EQUAL that export for the
event — additions, changes **and removals** across every table (participant types, attendees, rooms,
locations, activities, sessions, audience/grant/speaker edges, FAQs, tickets, orders, check-ins) — printing
a human-readable diff first and proof after, so the Summit can be refreshed as often as a new export lands.

**Architecture:** `scripts/load_event_graph.py` already parses the export and upserts 15 tables, keyed on
GroupOS ids. It is **upsert-only**, so anything GroupOS removed or re-gated since the last load stays behind
and keeps gating visibility (today: the old "Night Out" row is open to every Member; the new export makes it
Staff + per-buyer grants — an upsert would leave the four stale audience edges in place). This plan adds three
things to that one script: (1) a **diff report** (planned rows vs live DB rows, per table, names not ids)
that `--dry-run` prints and a real run prints before writing; (2) a **reconcile** step after the upserts
that deletes rows of this event that the export no longer contains, in FK-safe order; (3) two **guards** —
a freshness check of the export's `_meta.scannedAt` against the live registrations ledger (the file handed
over tonight was a 17-Aug scan: 4 of the 5 people who registered 18–21 Aug are absent from it) and a
warning for pending reminders that would cascade-delete — plus two provenance columns on `event.events`
so the loaded snapshot's age is visible. The lane (`/api/olivia/schedule`) and the visibility rule are
untouched: they read whatever the tables hold.

**Tech Stack:** Python 3 **stdlib only**, shelling out to `curl` (repo rule; must run under
`/usr/bin/python3` 3.9 — no `match`, no `X | None` types, no `zoneinfo` alternatives) · Supabase PostgREST
(`event` + `digest` schemas, service key from `/Users/Born/mds-digest-web/.env.local`) · `unittest`
(stdlib) for the pure helpers — this is the first test file under `scripts/`, create the directory ·
one Supabase migration via the Supabase MCP `apply_migration` tool.

## Global Constraints

- **Policy stays outside the database.** The `event` schema is **tables and foreign keys only — no views,
  no functions** (Andy's ruling, #85). The migration in this plan adds two nullable columns and comments,
  nothing else.
- **`event.people` rows are never deleted** (people are humans, not event rows; `attendees` and
  `session_speakers` RESTRICT on them; the repo rule "never delete a member record" applies). A person who
  dropped out of the export simply loses their attendee/grant/speaker rows.
- **`at_member_id` is never guessed** — the existing three-rung ladder (profile email → registration-email
  bridge → unique full name) stays exactly as it is.
- **The loader stays idempotent**: running it twice on the same export is a no-op (diff report all zeros).
- **Soft-deleted export rows (`isDelete`) are never imported** (41 of 92 activities are Milan-2025 leftovers)
  and `accessRoles` — never the legacy `member/speaker/partner/guest` booleans — is the audience.
- **Every "it works" claim cites a live check** — a printed diff, a row count, a self-test line, a curl
  result. `scripts/event_lane.py --self-test` must print `SELF-TEST PASS` after the load (golden: plain
  Member sees **6** activities on 2026-08-23, the Women's Lunch grantee sees **7**; if a genuinely fresh
  export changes those numbers, re-derive them from the data and update the script AND
  `OLIVIA_HANDBOOK.md` §4.9 in the same commit, stating why).
- **Only Andy's phone (`17866578153`) is ever simulated on staging.** Route probes in this plan are
  `curl` reads of the deployed lane with a phone in the body — no WhatsApp message is sent.
- **After the migration: `python3 scripts/db_export_schema.py`, `git diff db/`, commit `db/`** (handbook
  §8.2b). If the export covers no `event` objects, say so in the report instead of claiming a no-op silently.
- **Two repos, two authors.** Everything in this plan lives in `/Users/Born/Scorecard` (loader, tests,
  docs). Scorecard commits carry `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. Do not touch
  `/Users/Born/mds-digest-web` in this plan (the timezone fix is its own plan,
  `docs/superpowers/plans/2026-08-22-venue-today.md`).
- **Another agent is committing to Scorecard `main` (#108).** Work on the SDD worktree branch; never
  `git add -A`; stage only the files named in each task.
- **Docs written for Andy are short, normal prose** — no caveman style in files.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/load_event_graph.py` (modify) | Parse export → plan rows (unchanged) → **diff report** → upsert (unchanged) → **reconcile deletes** → **provenance stamp**. Pure helpers at module level so they import without env. |
| `scripts/tests/test_event_refresh.py` (create) | `unittest` coverage of the pure helpers: value normalisation, row diff, stale-key computation, deletion order. |
| `supabase migration event_events_load_provenance_20260822` (apply via MCP) | `event.events.source_scanned_at`, `event.events.loaded_at` + column comments. |
| `db/` (re-export) | Whatever `scripts/db_export_schema.py` changes after the migration. |
| `OLIVIA_HANDBOOK.md` §4.9 (modify) | Refresh runbook (one command, what the report shows, the freshness guard) + trap #4 (a "new" export may be an old scan). |
| `OLIVIA_SPRINT_4.md` (modify) | File #113 with story + ACs; close block with before/after numbers. |
| `OLIVIA_NEXT_SESSION.md`, `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md` | Handoff state + stream entry + one index line (session close). |

**Data facts the implementer needs (measured 2026-08-22, live DB vs `/Users/Born/Downloads/event_graph (1).json`):**

| table | DB now | export (live rows) | expected diff |
|---|---|---|---|
| events | 1 | 1 (`689cfd00f1f12d7791cf9525`, tz `Asia/Singapore`) | 0 |
| participant_types | 6 | 6 | 0 |
| attendees | 178 | 178 (Member 115 · Speaker 29 · Guest 23 · Staff 11) | 0 |
| people | 199 | 199 | 0 added (at_member_id may re-resolve — informational) |
| rooms | 6 | 6 | 0 |
| locations | 18 | 19 | **+1 `CÉ LA VI Singapore`** |
| activities | 50 | 51 | **+1 `Night Out` (Staff audience, 23 grants, 08-25 10:30 PM)** · ~`Night Out (Add-On)` (renamed from `Night Out`, location → CÉ LA VI) · ~`Closing Dinner` starts 18:03→18:30 · ~`Hotel Check Out at 12 PM` short_description |
| activity_audience | 180 | 177 | **−4** (old Night Out: Guest/Partner/Member/Partners Team) **+1** (new Night Out: Staff) |
| activity_person_grants | 183 | 318 | **+135** (112 Night Out (Add-On) buyers + 23 Night Out) |
| sessions | 31 | 31 | ~`Welcome Drinks` starts 18:03→18:30 · ~`VOTE! VOTE! VOTE!` ends 19:00→19:30 |
| session_speakers | 35 | 35 | 0 |
| faqs / tickets / orders / check_ins | 19 / 25 / 138 / 22 | same | 0 |
| reminders | 0 | — | nothing to cascade |

The export's `_meta.scannedAt` is `2026-08-17T22:16:44.734Z`. `digest.event_registrations_live` for the
Summit (`event_at_id = recrATwhUDA55iQN5`) holds 5 registrations with `order_date > 2026-08-17` — Sheng
Zheng (08-18), Anton Babiy (08-18, present in the export), Shyam Murali (08-19), Mohamed Siddique (08-20),
Farzad Zahiri (08-21). The freshness guard must name the four absent ones.

FK behaviour (verified from `information_schema`): `activity_audience`, `activity_person_grants`,
`session_speakers`, `reminders` **CASCADE** from activities/sessions; `sessions.activity_id`,
`sessions.room_id`, `check_ins.activity_id`, `activities.location_id` **SET NULL**; `rooms.location_id`
**RESTRICT**; `attendees.participant_type_id`, `attendees.person_id`, `session_speakers.person_id`,
`orders.person_id`, `check_ins.person_id` **RESTRICT**. Hence the deletion order below.

---

### Task 1: Pure helpers — value normalisation, row diff, stale keys, deletion order (TDD)

**Files:**
- Modify: `scripts/load_event_graph.py` (add module-level helpers below the existing `clean()` — nothing in `main()` yet)
- Create: `scripts/tests/__init__.py` (empty) and `scripts/tests/test_event_refresh.py`

**Interfaces:**
- Produces (used by Tasks 2–3):
  - `SCOPED: list[tuple[str, tuple[str, ...], str | None]]` — `(table, pk_columns, parent_column)` in **deletion order**.
  - `same_value(a, b) -> bool` — equality with timestamps compared as instants (`+08:00` vs `+00:00` vs `Z`), `None == missing == ""`, numbers compared as floats.
  - `diff_rows(existing: list[dict], planned: list[dict], pk: tuple[str, ...]) -> tuple[list[dict], list[dict], list[tuple[dict, list[tuple[str, object, object]]]]]` — `(added_rows, removed_rows, changed)` where `changed` pairs the planned row with `[(column, old, new), ...]` over the planned row's columns only.
  - `stale_keys(existing_keys: set[tuple], planned_keys: set[tuple]) -> list[tuple]` — sorted `existing − planned`.
  - `row_key(row: dict, pk: tuple[str, ...]) -> tuple`.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/tests/test_event_refresh.py
"""Pure-helper tests for the event refresh (load_event_graph.py).
Run: python3 -m unittest scripts.tests.test_event_refresh -v   (from the repo root)
No network, no env: these helpers must import without touching .env.local."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import load_event_graph as leg  # noqa: E402


class SameValue(unittest.TestCase):
    def test_instants_in_different_offsets_are_equal(self):
        self.assertTrue(leg.same_value("2026-08-25T10:03:00+00:00", "2026-08-25T18:03:00+08:00"))

    def test_z_suffix_is_utc(self):
        self.assertTrue(leg.same_value("2026-07-01T12:00:00.000Z", "2026-07-01T12:00:00+00:00"))

    def test_different_instants_differ(self):
        self.assertFalse(leg.same_value("2026-08-25T18:03:00+08:00", "2026-08-25T18:30:00+08:00"))

    def test_none_missing_and_empty_string_are_equal(self):
        self.assertTrue(leg.same_value(None, ""))
        self.assertTrue(leg.same_value("", None))
        self.assertTrue(leg.same_value(None, None))

    def test_numbers_compare_as_numbers(self):
        self.assertTrue(leg.same_value(1.29, "1.29"))
        self.assertTrue(leg.same_value(1000, 1000.0))
        self.assertFalse(leg.same_value(1000, 1001))

    def test_strings_compare_stripped(self):
        self.assertTrue(leg.same_value("Night Out ", "Night Out"))
        self.assertFalse(leg.same_value("Night Out", "Night Out (Add-On)"))

    def test_booleans(self):
        self.assertTrue(leg.same_value(True, True))
        self.assertFalse(leg.same_value(True, False))


class DiffRows(unittest.TestCase):
    def setUp(self):
        self.existing = [
            {"id": "a", "name": "Closing Dinner", "starts_at": "2026-08-25T10:03:00+00:00", "extra_db_col": 1},
            {"id": "b", "name": "Old Thing", "starts_at": "2026-08-25T10:00:00+00:00"},
            {"id": "c", "name": "Same", "starts_at": "2026-08-24T01:00:00+00:00"},
        ]
        self.planned = [
            {"id": "a", "name": "Closing Dinner", "starts_at": "2026-08-25T18:30:00+08:00"},
            {"id": "c", "name": "Same", "starts_at": "2026-08-24T09:00:00+08:00"},
            {"id": "d", "name": "Night Out", "starts_at": "2026-08-25T22:30:00+08:00"},
        ]

    def test_added_removed_changed(self):
        added, removed, changed = leg.diff_rows(self.existing, self.planned, ("id",))
        self.assertEqual([r["id"] for r in added], ["d"])
        self.assertEqual([r["id"] for r in removed], ["b"])
        self.assertEqual(len(changed), 1)
        row, cols = changed[0]
        self.assertEqual(row["id"], "a")
        self.assertEqual(cols, [("starts_at", "2026-08-25T10:03:00+00:00", "2026-08-25T18:30:00+08:00")])

    def test_db_only_columns_are_ignored(self):
        # the DB row may carry columns the loader never writes (extra_db_col); only planned columns count
        _, _, changed = leg.diff_rows([self.existing[0]], [self.planned[0]], ("id",))
        self.assertEqual([c for _, cols in changed for c, _, _ in cols], ["starts_at"])

    def test_composite_key(self):
        ex = [{"activity_id": "x", "participant_type_id": "Member"}, {"activity_id": "x", "participant_type_id": "Guest"}]
        pl = [{"activity_id": "x", "participant_type_id": "Member"}, {"activity_id": "x", "participant_type_id": "Staff"}]
        added, removed, changed = leg.diff_rows(ex, pl, ("activity_id", "participant_type_id"))
        self.assertEqual([leg.row_key(r, ("activity_id", "participant_type_id")) for r in added], [("x", "Staff")])
        self.assertEqual([leg.row_key(r, ("activity_id", "participant_type_id")) for r in removed], [("x", "Guest")])
        self.assertEqual(changed, [])

    def test_idempotent_when_equal(self):
        added, removed, changed = leg.diff_rows(self.planned, self.planned, ("id",))
        self.assertEqual((added, removed, changed), ([], [], []))


class StaleKeys(unittest.TestCase):
    def test_existing_minus_planned_sorted(self):
        self.assertEqual(leg.stale_keys({("b",), ("a",), ("c",)}, {("a",)}), [("b",), ("c",)])

    def test_nothing_stale_when_planned_covers_existing(self):
        self.assertEqual(leg.stale_keys({("a",)}, {("a",), ("z",)}), [])


class DeletionOrder(unittest.TestCase):
    """Children before parents, or PostgREST returns 409 on RESTRICT / we lose cascades we wanted to count."""
    def pos(self, table):
        return [t for t, _, _ in leg.SCOPED].index(table)

    def test_edges_before_their_parents(self):
        self.assertLess(self.pos("activity_audience"), self.pos("activities"))
        self.assertLess(self.pos("activity_person_grants"), self.pos("activities"))
        self.assertLess(self.pos("session_speakers"), self.pos("sessions"))

    def test_sessions_before_activities_before_rooms_before_locations(self):
        self.assertLess(self.pos("sessions"), self.pos("activities"))
        self.assertLess(self.pos("activities"), self.pos("rooms"))
        self.assertLess(self.pos("rooms"), self.pos("locations"))

    def test_attendees_before_participant_types(self):
        self.assertLess(self.pos("attendees"), self.pos("participant_types"))

    def test_people_is_never_scoped(self):
        self.assertNotIn("people", [t for t, _, _ in leg.SCOPED])

    def test_every_loader_table_except_events_and_people_is_scoped(self):
        scoped = {t for t, _, _ in leg.SCOPED}
        self.assertEqual(scoped, {"activity_audience", "activity_person_grants", "session_speakers",
                                  "sessions", "activities", "rooms", "locations", "attendees",
                                  "check_ins", "orders", "tickets", "faqs", "participant_types"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run (repo root): `touch scripts/tests/__init__.py && python3 -m unittest scripts.tests.test_event_refresh -v 2>&1 | tail -5`
Expected: `AttributeError: module 'load_event_graph' has no attribute 'same_value'` (or `SCOPED`) — every test errors.

- [ ] **Step 3: Add the helpers to `scripts/load_event_graph.py`** (place them right after `clean()`, before `main()`)

```python
# ------------------------------------------------------------ refresh
# A GroupOS export is a snapshot. Re-running the loader must make the `event`
# schema EQUAL the snapshot for this event. Upsert alone cannot: an activity
# deleted in GroupOS, an audience box unticked, a speaker removed or a
# registration cancelled all stay behind as stale rows and keep gating
# visibility (2026-08-22: the old "Night Out" row stayed open to every Member
# after GroupOS had made it Staff + per-buyer grants).
#
# SCOPED lists every event-scoped table the loader writes, in DELETION ORDER —
# children before parents, because rooms->locations and attendees->types are
# RESTRICT and the edge tables CASCADE from activities/sessions (counted here,
# not lost to a cascade). `people` is deliberately absent: people are humans,
# not event rows; attendees/speakers RESTRICT on them, and a person who left the
# export simply stops having attendee rows. `events` is the root and is never
# deleted.
#   (table, primary-key columns, parent column that scopes an edge table)
SCOPED = [
    ("activity_audience", ("activity_id", "participant_type_id"), "activity_id"),
    ("activity_person_grants", ("activity_id", "person_id"), "activity_id"),
    ("session_speakers", ("session_id", "person_id"), "session_id"),
    ("sessions", ("id",), None),
    ("activities", ("id",), None),
    ("rooms", ("id",), None),
    ("locations", ("id",), None),
    ("attendees", ("id",), None),
    ("check_ins", ("id",), None),
    ("orders", ("id",), None),
    ("tickets", ("id",), None),
    ("faqs", ("id",), None),
    ("participant_types", ("id",), None),
]
PARENT_OF = {"activity_id": "activities", "session_id": "sessions"}


def _instant(s):
    """ISO string -> aware datetime, or None when it is not a timestamp."""
    if not isinstance(s, str) or len(s) < 19 or s[4] != "-" or s[10] != "T":
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def same_value(a, b):
    """Equality for diffing a planned row against its DB row: instants compare as
    instants whatever their offset, None / missing / '' are one thing, numbers
    compare as numbers, strings compare stripped."""
    if a in (None, "") and b in (None, ""):
        return True
    if a is None or b is None:
        return False
    ia, ib = _instant(a), _instant(b)
    if ia is not None and ib is not None:
        return ia == ib
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        pass
    if isinstance(a, str) and isinstance(b, str):
        return a.strip() == b.strip()
    return a == b


def row_key(row, pk):
    return tuple(row.get(c) for c in pk)


def diff_rows(existing, planned, pk):
    """-> (added_rows, removed_rows, changed) where changed = [(planned_row, [(col, old, new), ...])].
    Only the planned row's columns are compared: the DB row may carry columns the
    loader never writes and those are not drift."""
    ex = {row_key(r, pk): r for r in existing}
    pl = {row_key(r, pk): r for r in planned}
    added = [pl[k] for k in pl if k not in ex]
    removed = [ex[k] for k in ex if k not in pl]
    changed = []
    for k, row in pl.items():
        if k not in ex:
            continue
        cols = [(c, ex[k].get(c), v) for c, v in row.items() if not same_value(ex[k].get(c), v)]
        if cols:
            changed.append((row, cols))
    return added, removed, changed


def stale_keys(existing_keys, planned_keys):
    return sorted(k for k in existing_keys if k not in planned_keys)
```

`datetime` is already imported at the top of the file (`from datetime import datetime`).

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest scripts.tests.test_event_refresh -v 2>&1 | tail -4`
Expected: `Ran 18 tests … OK`.
Also prove the 3.9 floor: `/usr/bin/python3 -m unittest scripts.tests.test_event_refresh 2>&1 | tail -2` → `OK`.

- [ ] **Step 5: Commit**

```bash
git add scripts/load_event_graph.py scripts/tests/__init__.py scripts/tests/test_event_refresh.py
git commit -m "#113: pure diff helpers for the event refresh (same_value, diff_rows, stale_keys, SCOPED order)" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: The diff report — `--dry-run` prints what a load would change, by name

**Files:**
- Modify: `scripts/load_event_graph.py` — `main()` (the `# ---- write` block, currently lines ~404–437) plus new functions `fetch_all`, `existing_rows`, `report`.

**Interfaces:**
- Consumes (Task 1): `SCOPED`, `PARENT_OF`, `diff_rows`, `row_key`, `same_value`.
- Produces (Task 3): `existing_rows(table, pk, parent_col, event_id, key, url) -> list[dict]` (select `*`, paged) and `snapshot = {table: existing_rows(...)}` computed BEFORE any write; `report(plan, snapshot, names) -> dict` returning per-table `{added, removed, changed}` lists (Task 3 reads `removed` to compute what to delete and `changed` for the summary line).

- [ ] **Step 1: Add the fetch + report functions** (after `stale_keys`)

```python
def fetch_all(path, key, url, profile="event"):
    """GET every row of a PostgREST path — PostgREST hard-caps 1000 per request, so page."""
    rows, off = [], 0
    sep = "&" if "?" in path else "?"
    while True:
        code, raw = rest("GET", f"{path}{sep}limit=1000&offset={off}", key, url, profile=profile)
        if code != 200:
            sys.exit(f"GET {path}: HTTP {code}\n{raw[:300]}")
        page = json.loads(raw or "[]")
        rows += page
        if len(page) < 1000:
            return rows
        off += 1000


def existing_rows(table, pk, parent_col, event_id, key, url):
    """Every live row of `table` that belongs to this event. Edge tables have no
    event_id; they are scoped through their parent's ids (fetched with event_id)."""
    if parent_col is None:
        return fetch_all(f"{table}?select=*&event_id=eq.{event_id}&order={pk[0]}", key, url)
    parents = [r["id"] for r in fetch_all(f"{PARENT_OF[parent_col]}?select=id&event_id=eq.{event_id}", key, url)]
    rows = []
    for i in range(0, len(parents), 100):
        chunk = ",".join(parents[i:i + 100])
        rows += fetch_all(f"{table}?select=*&{parent_col}=in.({chunk})", key, url)
    return rows


LONG_TEXT = {"long_description", "answer"}          # never printed, only flagged


def _fmt(v, tz):
    inst = _instant(v) if isinstance(v, str) else None
    if inst is not None:
        return inst.astimezone(ZoneInfo(tz)).strftime("%a %d %b %H:%M")
    s = str(v)
    return s if len(s) <= 60 else s[:57] + "..."


def report(plan, snapshot, names, tz):
    """Print and return the per-table diff. `names` maps a row key to a label so the
    operator reads 'Night Out' not 6a83823db9b13b629da3b28b."""
    out = {}
    print("\n== what this load would change (export vs live DB) ==")
    for table, rows in plan:
        if table not in snapshot:            # events, people: informational, handled by caller
            continue
        pk = next(p for t, p, _ in SCOPED if t == table)
        added, removed, changed = diff_rows(snapshot[table], rows, pk)
        out[table] = {"added": added, "removed": removed, "changed": changed}
        print(f"  {table:24} +{len(added):<4} ~{len(changed):<4} -{len(removed):<4}")
        label = names.get(table, lambda r: row_key(r, pk))
        for r in added:
            print(f"      + {label(r)}")
        for r in removed:
            print(f"      - {label(r)}")
        for r, cols in changed:
            shown = ", ".join(f"{c}: {'(changed, %d->%d chars)' % (len(str(o or '')), len(str(n or ''))) if c in LONG_TEXT else _fmt(o, tz) + ' -> ' + _fmt(n, tz)}"
                              for c, o, n in cols)
            print(f"      ~ {label(r)}: {shown}")
    return out
```

- [ ] **Step 2: Wire the report into `main()`** — replace the current `# ---- write` tail (from `print()` + the `for table, rows in plan:` upsert loop to the end of `main()`) with:

```python
    # ------------------------------------------------------------- before
    # Read the live state BEFORE writing anything: the report and the reconcile
    # both need the pre-load rows, and the counts after the load are the proof.
    snapshot = {t: existing_rows(t, pk, parent, event_id, key, url) for t, pk, parent in SCOPED}
    by_id = {t: {r["id"]: r for r in rows} for t, rows in snapshot.items() if rows and "id" in rows[0]}
    act_name = lambda aid: (by_id.get("activities", {}).get(aid) or next((r for r in act_rows if r["id"] == aid), {})).get("name", aid)
    sess_name = lambda sid: (by_id.get("sessions", {}).get(sid) or next((r for r in sess_rows if r["id"] == sid), {})).get("title", sid)
    type_name = lambda tid: (by_id.get("participant_types", {}).get(tid) or next((r for r in pt_rows if r["id"] == tid), {})).get("role", tid)
    person_name = lambda pid: next((p["name"] for p in people.values() if p["id"] == pid), pid)
    names = {
        "activities": lambda r: f"{r['name']} ({_fmt(r['starts_at'], tz)})",
        "sessions": lambda r: f"{r['title']} ({_fmt(r['starts_at'], tz)})",
        "rooms": lambda r: r["name"],
        "locations": lambda r: r["name"],
        "participant_types": lambda r: r["role"],
        "attendees": lambda r: f"{person_name(r['person_id'])} as {type_name(r['participant_type_id'])}",
        "activity_audience": lambda r: f"{act_name(r['activity_id'])} <- {type_name(r['participant_type_id'])}",
        "activity_person_grants": lambda r: f"{act_name(r['activity_id'])} <- {person_name(r['person_id'])}",
        "session_speakers": lambda r: f"{sess_name(r['session_id'])} <- {person_name(r['person_id'])}",
        "faqs": lambda r: r["question"][:60],
        "tickets": lambda r: r["name"],
        "orders": lambda r: f"order {r['id']} by {person_name(r['person_id'])}",
        "check_ins": lambda r: f"check-in {r['id']} {person_name(r['person_id'])}",
    }
    diff = report(plan, snapshot, names, tz)
    # people are informational (never deleted): how many new, how many re-linked
    existing_people = {r["id"]: r for r in fetch_all("people?select=id,name,email,at_member_id", key, url)}
    new_people = [p for p in people.values() if p["id"] not in existing_people]
    relinked = [(p["name"], existing_people[p["id"]].get("at_member_id"), p["at_member_id"])
                for p in people.values() if p["id"] in existing_people and existing_people[p["id"]].get("at_member_id") != p["at_member_id"]]
    print(f"  {'people':24} +{len(new_people):<4} ~{len(relinked):<4} -0    (people are never deleted)")
    for p in new_people:
        print(f"      + {p['name']} <{p['email']}>")
    for name, old, new in relinked:
        print(f"      ~ {name}: at_member_id {old} -> {new}")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    # -------------------------------------------------------------- write
    print()
    for table, rows in plan:
        n = upsert(table, rows, key, url, False)
        print(f"  {'loaded':<10} {n:>5}  {table}")
```

(The `ev_row`, `plan` list and `dedupe` block above this point stay exactly as they are. `act_rows`,
`sess_rows`, `pt_rows`, `people` are the locals already built earlier in `main()`.)

- [ ] **Step 3: Run the dry-run against the tonight's export and check the report against the data table above**

Run: `python3 scripts/load_event_graph.py "/Users/Born/Downloads/event_graph (1).json" --dry-run 2>&1 | tail -60`
Expected (exact numbers): `activities +1 ~3 -0` (lines: `+ Night Out (Tue 25 Aug 22:30)`, `~ Night Out (Add-On) … name: Night Out -> Night Out (Add-On), location_id: None -> 6a8382ceb9b13b629da3c7d5`, `~ Closing Dinner … starts_at: Tue 25 Aug 18:03 -> Tue 25 Aug 18:30`, `~ Hotel Check Out at 12 PM … short_description …`) · `sessions +0 ~2 -0` (`Welcome Drinks` starts_at, `VOTE! VOTE! VOTE!` ends_at) · `locations +1 ~0 -0` (`+ CÉ LA VI Singapore`) · `activity_audience +1 ~0 -4` (`+ Night Out <- Staff`, `- Night Out (Add-On) <- Guest/Partner/Member/Partners Team` — the label uses the planned name for a known id) · `activity_person_grants +135 ~0 -0` · every other table `+0 ~0 -0` · `people +0` · ends with `--dry-run: nothing written.`
If `long_description` shows as changed on many activities, that is real (the new export carries fuller HTML) and is printed only as a char-count — fine.
Expected on the OLD export (`python3 scripts/load_event_graph.py ~/Downloads/event_graph.json --dry-run | grep -c " +0    ~0    -0"`): every table zero — proves the report is idempotent against what is loaded.

- [ ] **Step 4: Run the unit tests again** — `python3 -m unittest scripts.tests.test_event_refresh 2>&1 | tail -2` → `OK`.

- [ ] **Step 5: Commit**

```bash
git add scripts/load_event_graph.py
git commit -m "#113: --dry-run prints the export-vs-DB diff by name before any write" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Reconcile (delete stale rows), reminder + freshness guards, provenance stamp

**Files:**
- Modify: `scripts/load_event_graph.py` — after the upsert loop in `main()`; new functions `delete_stale`, `reminder_warning`, `freshness_check`.
- Modify: `scripts/tests/test_event_refresh.py` — add `FreshnessMessage` tests for the pure message builder.
- Migration (Supabase MCP `apply_migration`, name `event_events_load_provenance_20260822`).
- Re-export: `db/` via `python3 scripts/db_export_schema.py`.

**Interfaces:**
- Consumes: `diff` (Task 2 `report` return), `snapshot`, `SCOPED`, `row_key`, `stale_keys`, `rest`.
- Produces: the CLI contract used by Task 4 and the runbook — `python3 scripts/load_event_graph.py <export.json> [--dry-run] [--no-reconcile]`; exit code 0; the final block prints `after:` counts per table.
- New pure helper `late_registrations_message(scanned_iso, late_rows) -> list[str]` (testable without network).

- [ ] **Step 1: Write the failing tests for the freshness message** (append to `scripts/tests/test_event_refresh.py`)

```python
class FreshnessMessage(unittest.TestCase):
    def test_names_each_late_registration(self):
        lines = leg.late_registrations_message("2026-08-17T22:16:44.734Z", [
            {"full_name": "Sheng Zheng", "order_date": "2026-08-18"},
            {"full_name": "Farzad Zahiri", "order_date": "2026-08-21"},
        ])
        self.assertEqual(lines[0], "export scanned 2026-08-17T22:16:44.734Z · 2 registration(s) in the live ledger are NEWER than this export:")
        self.assertIn("  !! Sheng Zheng (2026-08-18) — this export cannot know them", lines)
        self.assertIn("  !! Farzad Zahiri (2026-08-21) — this export cannot know them", lines)

    def test_silent_when_nothing_is_newer(self):
        self.assertEqual(leg.late_registrations_message("2026-08-17T22:16:44.734Z", []),
                         ["export scanned 2026-08-17T22:16:44.734Z · no registration in the live ledger is newer — export is current"])

    def test_missing_scanned_at_is_its_own_warning(self):
        self.assertEqual(leg.late_registrations_message(None, []), ["  !! export has no _meta.scannedAt — age unknown, compare rosters by hand"])
```

- [ ] **Step 2: Run them to verify they fail** — `python3 -m unittest scripts.tests.test_event_refresh.FreshnessMessage 2>&1 | tail -3` → `AttributeError … late_registrations_message`.

- [ ] **Step 3: Apply the provenance migration** (Supabase MCP `apply_migration`, name `event_events_load_provenance_20260822`):

```sql
alter table event.events
  add column if not exists source_scanned_at timestamptz,
  add column if not exists loaded_at timestamptz;
comment on column event.events.source_scanned_at is
  'GroupOS export _meta.scannedAt of the snapshot currently loaded. Freshness signal: compare with digest.event_registrations_live before trusting rosters — a "new" file can be an old scan (2026-08-22).';
comment on column event.events.loaded_at is
  'When scripts/load_event_graph.py last made this event equal an export (upsert + reconcile).';
```

Verify: `python3 - <<'EOF'` … `GET events?select=id,source_scanned_at,loaded_at` via the `rest()` helper returns both columns as `null`. Then `python3 scripts/db_export_schema.py && git diff --stat db/` — commit whatever changed (if nothing changed because the exporter does not cover `event`, write that sentence in the task report).

- [ ] **Step 4: Add the functions** (after `report`)

```python
def late_registrations_message(scanned_iso, late_rows):
    if not scanned_iso:
        return ["  !! export has no _meta.scannedAt — age unknown, compare rosters by hand"]
    if not late_rows:
        return [f"export scanned {scanned_iso} · no registration in the live ledger is newer — export is current"]
    lines = [f"export scanned {scanned_iso} · {len(late_rows)} registration(s) in the live ledger are NEWER than this export:"]
    lines += [f"  !! {r.get('full_name')} ({r.get('order_date')}) — this export cannot know them" for r in late_rows]
    return lines


def freshness_check(d, event_id, key, url):
    """A 'new' export can be an old scan (2026-08-22: a file handed over as new was a
    17-Aug scan missing four people who registered 18–21 Aug). The ticket ledger
    (digest.event_registrations_live) is live-synced, so anything registered after
    the export's scannedAt proves the export is stale. Returns scannedAt or None."""
    scanned = ((d.get("_meta") or {}).get("scannedAt") or {}).get("$date") if isinstance((d.get("_meta") or {}).get("scannedAt"), dict) else (d.get("_meta") or {}).get("scannedAt")
    late = []
    if scanned:
        code, raw = rest("GET", f"events_catalog?select=at_record_id&app_event_id=eq.{event_id}&limit=1", key, url, profile="digest")
        cat = json.loads(raw or "[]") if code == 200 else []
        if cat:
            code, raw = rest("GET", "event_registrations_live?select=full_name,order_date"
                                    f"&event_at_id=eq.{cat[0]['at_record_id']}&order_date=gt.{scanned[:10]}&order=order_date",
                             key, url, profile="digest")
            late = json.loads(raw or "[]") if code == 200 else []
        else:
            print("  ?? no events_catalog row maps this GroupOS event — freshness check skipped")
    for line in late_registrations_message(scanned, late):
        print(line)
    return scanned


def reminder_warning(stale_activity_ids, stale_session_ids, key, url):
    """Pending reminders hang on activities/sessions by FK and CASCADE away with
    them. That is the right outcome for a cancelled activity, but it must be
    said out loud, with ids, before it happens."""
    parts = []
    if stale_activity_ids:
        parts.append(f"activity_id.in.({','.join(stale_activity_ids)})")
    if stale_session_ids:
        parts.append(f"session_id.in.({','.join(stale_session_ids)})")
    if not parts:
        return 0
    code, raw = rest("GET", f"reminders?select=id,person_id,remind_at&status=eq.pending&or=({','.join(parts)})", key, url)
    pend = json.loads(raw or "[]") if code == 200 else []
    if pend:
        print(f"  !! {len(pend)} PENDING reminder(s) sit on activities/sessions this export removed — "
              f"they cascade-delete with them: {[p['id'] for p in pend]}")
    return len(pend)


def delete_stale(table, pk, keys, key, url, dry):
    """Delete the given rows. Single-column keys go in `in.()` chunks; composite
    keys go one DELETE each (edge tables are small and the count is the proof)."""
    if not keys:
        return 0
    if dry:
        return len(keys)
    done = 0
    if len(pk) == 1:
        ids = [k[0] for k in keys]
        for i in range(0, len(ids), 100):
            chunk = ",".join(ids[i:i + 100])
            code, raw = rest("DELETE", f"{table}?{pk[0]}=in.({chunk})", key, url,
                             extra_headers=["Prefer: return=minimal"])
            if code not in (200, 204):
                sys.exit(f"DELETE {table}: HTTP {code}\n{raw[:400]}")
            done += len(ids[i:i + 100])
        return done
    for k in keys:
        filt = "&".join(f"{c}=eq.{v}" for c, v in zip(pk, k))
        code, raw = rest("DELETE", f"{table}?{filt}", key, url, extra_headers=["Prefer: return=minimal"])
        if code not in (200, 204):
            sys.exit(f"DELETE {table}?{filt}: HTTP {code}\n{raw[:400]}")
        done += 1
    return done
```

- [ ] **Step 5: Wire it into `main()`**: add the flag, call the guards BEFORE the `--dry-run` return, run the reconcile AFTER the upsert loop, stamp provenance, print after-counts.

```python
    # in the argparse block:
    ap.add_argument("--no-reconcile", action="store_true",
                    help="upsert only; leave rows the export no longer contains (diagnostic use)")
```

Right after the `people` report lines (still before `if args.dry_run:`):

```python
    # -------------------------------------------------------------- guards
    print()
    scanned = freshness_check(d, event_id, key, url)
    planned = dict(plan)                       # table -> deduped planned rows
    stale = {t: stale_keys({row_key(r, pk) for r in snapshot[t]},
                           {row_key(r, pk) for r in planned[t]})
             for t, pk, _ in SCOPED}
    reminder_warning([k[0] for k in stale["activities"]], [k[0] for k in stale["sessions"]], key, url)
    if args.no_reconcile:
        print("  --no-reconcile: stale rows will be LEFT IN PLACE")
    for t, pk, _ in SCOPED:
        if stale[t]:
            print(f"  {'would delete' if args.dry_run else 'will delete':<12} {len(stale[t]):>5}  {t}")
```

After the upsert loop (end of `main()`):

```python
    # ---------------------------------------------------------- reconcile
    if not args.no_reconcile:
        for t, pk, _ in SCOPED:
            n = delete_stale(t, pk, stale[t], key, url, False)
            if n:
                print(f"  {'deleted':<10} {n:>5}  {t}")

    # --------------------------------------------------------- provenance
    code, raw = rest("PATCH", f"events?id=eq.{event_id}", key, url,
                     {"source_scanned_at": scanned, "loaded_at": datetime.now(timezone.utc).isoformat()},
                     extra_headers=["Prefer: return=minimal"])
    if code not in (200, 204):
        sys.exit(f"provenance stamp failed: HTTP {code}\n{raw[:300]}")

    # -------------------------------------------------------------- after
    print("\nafter:")
    for t, pk, parent in SCOPED:
        print(f"  {t:24} {len(existing_rows(t, pk, parent, event_id, key, url)):>5}")
    print(f"  {'people':24} {len(fetch_all('people?select=id', key, url)):>5}")
    print(f"  events.source_scanned_at = {scanned} · loaded_at = now")
```

Add `timezone` to the datetime import: `from datetime import datetime, timezone`.

Note on `stale`: `dict(plan)[t]` is the deduped planned rows for table `t` (the `plan` list is already
deduped by the block above). Keep the edge-table planned rows exactly as the loader builds them
(`activity_id`/`participant_type_id` etc.) so `row_key` matches the DB columns.

- [ ] **Step 6: Run the tests + the dry-run**

`python3 -m unittest scripts.tests.test_event_refresh 2>&1 | tail -2` → `OK` (21 tests).
`python3 scripts/load_event_graph.py "/Users/Born/Downloads/event_graph (1).json" --dry-run 2>&1 | tail -25`
Expected new lines: `export scanned 2026-08-17T22:16:44.734Z · 5 registration(s) in the live ledger are NEWER than this export:` followed by one `!!` line each for Sheng Zheng (2026-08-18), Anton Babiy (2026-08-18), Shyam Murali (2026-08-19), Mohamed Siddique (2026-08-20), Farzad Zahiri (2026-08-21) — the ledger query is by `order_date` (a date), so Anton Babiy is listed even though he happens to be in the export; the wording "newer than this export" stays true and no name is special-cased · `would delete     4  activity_audience` · no other `would delete` line · `--dry-run: nothing written.` The task report quotes the actual lines.

- [ ] **Step 7: Commit**

```bash
git add scripts/load_event_graph.py scripts/tests/test_event_refresh.py db/
git commit -m "#113: reconcile stale rows after upsert, reminder + export-freshness guards, events.source_scanned_at/loaded_at" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Load the designated export for real, prove it, document the runbook

**Files:**
- Run: `scripts/load_event_graph.py` (no code change expected; if the live run surfaces a bug, fix it here with a test and commit).
- Modify: `OLIVIA_HANDBOOK.md` §4.9 (refresh runbook + trap #4), `OLIVIA_SPRINT_4.md` (#113 story/ACs/close block), `OLIVIA_NEXT_SESSION.md` (state), `SESSION_LOG_OLIVIA.md` (entry), `SESSION_LOG.md` (one index line).

**Interfaces:**
- Consumes: the CLI from Task 3.
- Produces: the before/after numbers and live proofs for the ticket close.

**Which export:** the one Andy designates at execution time. Tonight's file is
`/Users/Born/Downloads/event_graph (1).json` (a 17-Aug scan — see the data table; still strictly better than
what is loaded: the Night Out visibility correction is real). When a genuinely fresh export lands, this
task is re-run unchanged with the new path — that is the point of the plan.

- [ ] **Step 1: Before numbers** — run the dry-run one more time and save it:
`python3 scripts/load_event_graph.py "<export>" --dry-run > /private/tmp/claude-501/-Users-Born-Scorecard/79470ba1-3f46-4d08-9020-f25d380bf7a1/scratchpad/113_before.txt 2>&1; tail -30 …/113_before.txt`

- [ ] **Step 2: Real run** — `python3 scripts/load_event_graph.py "<export>" 2>&1 | tee …/113_run.txt | tail -45`
Expected for tonight's file: `loaded` lines for all 15 tables · `deleted 4 activity_audience` · `after:` activities 51 · locations 19 · activity_audience 177 · activity_person_grants 318 · sessions 31 · attendees 178 · people 199 · rooms 6 · `events.source_scanned_at = 2026-08-17T22:16:44.734Z`.

- [ ] **Step 3: Idempotency** — run it again: `python3 scripts/load_event_graph.py "<export>" --dry-run | grep -E "^\s+[a-z_]+ +\+[0-9]+ +~[0-9]+ +-[0-9]+"` → every line `+0 ~0 -0` (long_description may show `~` on the very first re-run if PostgREST normalised whitespace; if so, quote it and treat `same_value` stripping as the fix only if the difference is whitespace).

- [ ] **Step 4: Golden self-test** — `python3 scripts/event_lane.py --self-test 2>&1 | tail -3` → `plain Member day one = 6 (expect 6)`, `Women's Lunch grantee day one = 7 (expect 7)`, `SELF-TEST PASS`.

- [ ] **Step 5: Live lane proof (reads only)** — the deployed route, secret = the value the n8n `Answer Tool` node sends (read it from the latest `olivia_snapshots/prod_*post-promote.json` → node `Answer Tool` → `parameters.headerParameters.parameters[]` → name `X-Olivia-Secret`; never print it). Two phones: Andy's `17866578153` (not registered → plain-Member view) and one **Night Out (Add-On)** grantee's phone — pick the grantee from the DB: `activity_person_grants?select=people(name,at_member_id)&activity_id=eq.6a745cc7f26a690e1f111d05&limit=5`, then `digest.members?select=phone&at_member_id=eq.<id>` (use only to build the curl; do not print the number in the report — print the name).

```bash
curl -s https://digest.mds.co/api/olivia/schedule -H "X-Olivia-Secret: $SECRET" -H 'Content-Type: application/json' \
  -d '{"op":"where","q":"night out","phone":"17866578153"}' | python3 -m json.tool | head -20
```
Expected: Andy → `found: false` (Night Out is Staff + buyers only now). The grantee → `found: true`, `name: "Night Out (Add-On)"`, `where: "CÉ LA VI Singapore"`, `when: "Tue 25 Aug, 10:30 pm Singapore time"`. And `{"op":"where","q":"closing dinner","phone":"17866578153"}` → `when: "Tue 25 Aug, 6:30 pm Singapore time"` (was 6:03 pm).

- [ ] **Step 6: Docs** — in `OLIVIA_HANDBOOK.md` §4.9, replace the line `Loaded from a GroupOS export by `scripts/load_event_graph.py`, idempotent.` with:

```markdown
Loaded from a GroupOS export by `scripts/load_event_graph.py`, idempotent **and reconciling** (#113,
2026-08-22): a run makes the `event` schema EQUAL the export for that event — rows the export no longer
contains are deleted in FK-safe order (children first; `people` never). Refresh runbook:

```bash
python3 scripts/load_event_graph.py ~/Downloads/<export>.json --dry-run   # diff by name + freshness guard, writes nothing
python3 scripts/load_event_graph.py ~/Downloads/<export>.json             # same report, then upsert + reconcile + after-counts
python3 scripts/event_lane.py --self-test                                  # golden 6 / 7 must still pass
```

The report names rows, not ids (`~ Closing Dinner: starts_at Tue 25 Aug 18:03 -> 18:30`). The freshness
guard compares the export's `_meta.scannedAt` with `digest.event_registrations_live` and names every
registration newer than the export. `event.events.source_scanned_at` / `loaded_at` say what is loaded.
```

and add trap **4** to the "Three traps in the export the loader absorbs" list (rename the heading to "Four
traps"):

```markdown
4. **A "new" export can be an old scan.** The file handed over on 2026-08-22 as the new event was a
   17-Aug scan — 4 of the 5 people who registered 18–21 Aug were absent. Read `_meta.scannedAt` and
   the freshness guard before believing a roster changed or did not change.
```

In `OLIVIA_SPRINT_4.md` add the #113 ticket (story: *As a Summit attendee asking Millie, I get the current
run-of-show, rooms, access and rosters — whatever GroupOS holds now — not the snapshot from the first load*;
ACs: ① `--dry-run` prints added/changed/removed by name for every table ② a run removes what the export
removed (reconcile) ③ export freshness is checked against the live ledger and stale exports are named ④
`event_lane.py --self-test` PASS after the load ⑤ live lane proof: Night Out gated to buyers/Staff, Closing
Dinner 18:30 ⑥ runbook in the handbook) and its close block with the before/after table from Steps 1–5.
Then the handoff + stream log + one index line per the session protocol.

- [ ] **Step 7: Commit**

```bash
git add OLIVIA_HANDBOOK.md OLIVIA_SPRINT_4.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md
git commit -m "#113: Summit event refreshed from the 2026-08-17T22:16Z export (reconcile proven: Night Out gated, 4 stale audience edges gone); refresh runbook + export-freshness trap" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-review notes (done while writing)

- Spec coverage: whole-event refresh (every table the loader writes) ✔ Tasks 1–3; attendee types /
  attendee lists / rooms / activities / sessions — all in `SCOPED` + report ✔; "and more" = FAQs, tickets,
  orders, check-ins, edges ✔; stale-export detection ✔ Task 3; proof + runbook ✔ Task 4.
- Not in scope (stated): `event.partner_profiles` / `partner_people` (#88, loaded from Airtable by
  `scripts/load_partner_profiles.py`, not in the GroupOS export); `digest.events_catalog` times (separate
  sync, known wrong zone, never used by the lane); the Millie timezone fix (separate plan).
- Type consistency: `SCOPED` triples `(table, pk, parent_col)` are used identically in Tasks 1–3;
  `diff_rows` returns `(added, removed, changed)` everywhere; `existing_rows` signature matches its two call sites.
- Supabase advisory seen while planning: RLS is disabled on all 18 `event.*` tables — **moot today**: only
  `service_role` holds any privilege on the schema (verified in `information_schema.role_table_grants`;
  anon/authenticated have none). Noted for Andy, not part of this plan.
