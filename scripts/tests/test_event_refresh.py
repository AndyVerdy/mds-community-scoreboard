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

    def test_bool_and_stringy_int_are_not_equal(self):
        self.assertFalse(leg.same_value(True, "1"))
        self.assertFalse(leg.same_value(False, "0"))

    def test_fractional_seconds_of_different_precision_are_equal(self):
        self.assertTrue(leg.same_value("2026-08-23T09:52:31.79+00:00", "2026-08-23T09:52:31.790+00:00"))
        self.assertTrue(leg.same_value("2026-08-23T09:52:31.7+00:00", "2026-08-23T09:52:31.700000+00:00"))
        self.assertTrue(leg.same_value("2026-08-23T09:52:31.79Z", "2026-08-23T09:52:31.790+00:00"))

    def test_fractional_seconds_real_difference_still_differs(self):
        self.assertFalse(leg.same_value("2026-08-23T09:52:31.79+00:00", "2026-08-23T09:52:32.79+00:00"))


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


class SubtractProtected(unittest.TestCase):
    """C1: a row the loader SKIPPED (source defect) must never be treated as removed by
    the export. `protected` is what stands between `stale` and the DELETE."""

    def test_a_protected_stale_key_is_not_deleted(self):
        stale = {"activities": [("a",), ("b",)]}
        protected = {"activities": {("a",)}}
        self.assertEqual(leg.subtract_protected(stale, protected), {"activities": [("b",)]})

    def test_an_unprotected_stale_key_still_is(self):
        stale = {"activities": [("a",), ("b",)]}
        protected = {"activities": {("z",)}}          # protects a key that was never stale
        self.assertEqual(leg.subtract_protected(stale, protected), {"activities": [("a",), ("b",)]})

    def test_empty_protected_set_is_a_no_op(self):
        stale = {"activities": [("a",), ("b",)], "sessions": [("s1",)]}
        self.assertEqual(leg.subtract_protected(stale, {}), stale)

    def test_multi_table_only_the_named_table_is_protected(self):
        stale = {"activities": [("a",)], "sessions": [("a",)]}   # same key, different table
        protected = {"activities": {("a",)}}
        out = leg.subtract_protected(stale, protected)
        self.assertEqual(out["activities"], [])
        self.assertEqual(out["sessions"], [("a",)])              # sessions' ("a",) is untouched


class ProtectedFromSkips(unittest.TestCase):
    """A skipped ACTIVITY must also protect its own activity_audience /
    activity_person_grants rows in the pre-write snapshot — those never made it into
    `planned` either (the loop that would have added them never ran), so without this
    expansion they would independently compute as stale and get deleted even though the
    parent activity row survives (the exact 'CASCADE its audience, grants' consequence
    C1 describes). A skipped SESSION protects its session_speakers the same way."""

    def test_skipped_activity_protects_its_audience_and_grants(self):
        skipped = {"activities": {("act-1",)}, "sessions": set(), "attendees": set(),
                  "participant_types": set()}
        snapshot = {
            "activity_audience": [{"activity_id": "act-1", "participant_type_id": "Member"},
                                  {"activity_id": "act-2", "participant_type_id": "Member"}],
            "activity_person_grants": [{"activity_id": "act-1", "person_id": "p1"}],
            "session_speakers": [],
        }
        protected = leg.protected_from_skips(skipped, snapshot)
        self.assertEqual(protected["activity_audience"], {("act-1", "Member")})
        self.assertEqual(protected["activity_person_grants"], {("act-1", "p1")})
        self.assertNotIn(("act-2", "Member"), protected["activity_audience"])

    def test_skipped_session_protects_its_speakers(self):
        skipped = {"activities": set(), "sessions": {("sess-1",)}, "attendees": set(),
                  "participant_types": set()}
        snapshot = {"session_speakers": [{"session_id": "sess-1", "person_id": "p1"},
                                         {"session_id": "sess-2", "person_id": "p2"}]}
        protected = leg.protected_from_skips(skipped, snapshot)
        self.assertEqual(protected["session_speakers"], {("sess-1", "p1")})

    def test_nothing_skipped_is_a_no_op(self):
        skipped = {"activities": set(), "sessions": set(), "attendees": set(),
                  "participant_types": set()}
        snapshot = {"activity_audience": [{"activity_id": "act-1", "participant_type_id": "Member"}]}
        protected = leg.protected_from_skips(skipped, snapshot)
        self.assertEqual(protected.get("activity_audience", set()), set())

    def test_end_to_end_a_synthetic_skipped_activity_is_excluded_from_the_delete_set(self):
        """Gate 4: prove, without touching the DB, that a synthetic 'skipped' activity id
        never ends up in the set load_event_graph.py would hand to delete_stale()."""
        existing = {
            "activities": [{"id": "act-1"}, {"id": "act-2"}],
            "activity_audience": [{"activity_id": "act-1", "participant_type_id": "Member"},
                                  {"activity_id": "act-2", "participant_type_id": "Member"}],
        }
        planned = {
            "activities": [{"id": "act-2"}],                              # act-1 skipped this run
            "activity_audience": [{"activity_id": "act-2", "participant_type_id": "Member"}],
        }
        stale_raw = {
            "activities": leg.stale_keys({leg.row_key(r, ("id",)) for r in existing["activities"]},
                                         {leg.row_key(r, ("id",)) for r in planned["activities"]}),
            "activity_audience": leg.stale_keys(
                {leg.row_key(r, ("activity_id", "participant_type_id")) for r in existing["activity_audience"]},
                {leg.row_key(r, ("activity_id", "participant_type_id")) for r in planned["activity_audience"]}),
        }
        # today, unprotected: act-1 and its audience row would both be stale
        self.assertIn(("act-1",), stale_raw["activities"])
        self.assertIn(("act-1", "Member"), stale_raw["activity_audience"])

        skipped = {"activities": {("act-1",)}, "sessions": set(), "attendees": set(),
                  "participant_types": set()}
        protected = leg.protected_from_skips(skipped, existing)
        stale = leg.subtract_protected(stale_raw, protected)
        self.assertNotIn(("act-1",), stale["activities"])
        self.assertNotIn(("act-1", "Member"), stale["activity_audience"])
        self.assertEqual(stale["activities"], [])          # nothing left to delete
        self.assertEqual(stale["activity_audience"], [])


class NaturalKeyCollisions(unittest.TestCase):
    """GroupOS soft-deletes + recreates a row on a role change: same natural key,
    new document id. A plain PK diff can't see that; this is what does."""

    def test_same_key_different_id_is_a_collision(self):
        existing = [{"id": "old1", "event_id": "E", "role": "Staff"}]
        planned = [{"id": "new1", "event_id": "E", "role": "Staff"}]
        self.assertEqual(leg.natural_key_collisions(existing, planned, ("event_id", "role")),
                         [(("E", "Staff"), "old1", "new1")])

    def test_same_id_is_not_a_collision(self):
        existing = [{"id": "same", "event_id": "E", "role": "Staff"}]
        planned = [{"id": "same", "event_id": "E", "role": "Staff"}]
        self.assertEqual(leg.natural_key_collisions(existing, planned, ("event_id", "role")), [])

    def test_all_new_key_is_not_a_collision(self):
        existing = [{"id": "old1", "event_id": "E", "role": "Staff"}]
        planned = [{"id": "new2", "event_id": "E", "role": "MDS"}]
        self.assertEqual(leg.natural_key_collisions(existing, planned, ("event_id", "role")), [])

    def test_only_the_colliding_row_is_reported_among_several(self):
        existing = [{"id": "old1", "event_id": "E", "role": "Staff"},
                    {"id": "keep", "event_id": "E", "role": "Member"}]
        planned = [{"id": "new1", "event_id": "E", "role": "Staff"},
                   {"id": "keep", "event_id": "E", "role": "Member"},
                   {"id": "brand-new", "event_id": "E", "role": "MDS"}]
        self.assertEqual(leg.natural_key_collisions(existing, planned, ("event_id", "role")),
                         [(("E", "Staff"), "old1", "new1")])


class OnConflictMap(unittest.TestCase):
    def test_attendees_upserts_on_its_natural_key(self):
        self.assertEqual(leg.ON_CONFLICT["attendees"], "event_id,person_id,participant_type_id")

    def test_participant_types_is_never_on_conflict(self):
        # its id IS FK-referenced (attendees RESTRICT, activity_audience CASCADE) —
        # rewriting it would be destructive; see NaturalKeyCollisions instead.
        self.assertNotIn("participant_types", leg.ON_CONFLICT)


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



class FreshnessFailureMessage(unittest.TestCase):
    def test_names_the_http_code_and_reason(self):
        msg = leg.freshness_failure_message(500, '{"message":"upstream timeout"}')
        self.assertIn("FAILED (HTTP 500)", msg)
        self.assertIn("cannot confirm the export is current", msg)
        self.assertIn("upstream timeout", msg)

    def test_truncates_long_body_to_200_chars(self):
        msg = leg.freshness_failure_message(502, "a" * 250)
        self.assertIn("a" * 200, msg)
        self.assertNotIn("a" * 201, msg)


class EventsCatalogFailureMessage(unittest.TestCase):
    """C2(c): a 5xx on the events_catalog lookup must read as an HTTP failure, never as
    the genuine 'no events_catalog row maps this GroupOS event' case."""
    def test_names_the_http_code_and_reason(self):
        msg = leg.events_catalog_failure_message(503, '{"message":"upstream timeout"}')
        self.assertIn("FAILED (HTTP 503)", msg)
        self.assertIn("cannot check export freshness", msg)
        self.assertIn("upstream timeout", msg)

    def test_truncates_long_body_to_200_chars(self):
        msg = leg.events_catalog_failure_message(500, "c" * 250)
        self.assertIn("c" * 200, msg)
        self.assertNotIn("c" * 201, msg)


class ReminderFailureMessage(unittest.TestCase):
    def test_names_the_http_code_and_reason(self):
        msg = leg.reminder_failure_message(500, '{"message":"upstream timeout"}')
        self.assertIn("FAILED (HTTP 500)", msg)
        self.assertIn("cannot confirm no pending reminders would cascade", msg)
        self.assertIn("upstream timeout", msg)

    def test_truncates_long_body_to_200_chars(self):
        msg = leg.reminder_failure_message(503, "b" * 250)
        self.assertIn("b" * 200, msg)
        self.assertNotIn("b" * 201, msg)


if __name__ == "__main__":
    unittest.main()
