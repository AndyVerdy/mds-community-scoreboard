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
