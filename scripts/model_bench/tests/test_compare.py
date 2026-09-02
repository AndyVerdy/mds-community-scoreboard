import json, os, tempfile, unittest
import bench_compare as bc


def row(i, a, b, out=500, reasoning=0):
    return {"id": i, "q": f"q{i}", "class": "X", "answer": "text", "secs": 5.0, "model_secs": 4.0, "cost": 0.01,
            "metrics": {"in": 100, "out": out, "cache_r": 30000, "cache_w": 0, "reasoning": reasoning, "calls": 2},
            "verdict": a, "reason": "r", "verdicts": {"claude-sonnet-5": {"verdict": a, "reason": "r"},
                                                       "gpt-5.6-terra": {"verdict": b, "reason": "r"}}}


ROWS = [row(1, "PASS", "PASS"), row(2, "FAIL", "PASS"), row(3, "PASS", "PARTIAL", reasoning=300), row(4, "ERROR", "PASS")]


class Stats(unittest.TestCase):
    def test_primary_and_per_judge(self):
        s = bc.stats(ROWS, "claude-sonnet-5")
        self.assertEqual((s["scored"], s["fails"], s["parts"]), (3, 1, 0))
        t = bc.stats(ROWS, "claude-sonnet-5", judge="gpt-5.6-terra")
        self.assertEqual((t["scored"], t["fails"], t["parts"]), (4, 0, 1))
        self.assertAlmostEqual(s["steady"], (100 * 2.00 + 500 * 10.00 + 30000 * 0.20) / 1e6)
        self.assertEqual(s["reasoning"], 75.0)

    def test_disagreements_ignore_errors(self):
        self.assertEqual([r["id"] for r in bc.disagreements(ROWS)], [2, 3])

    def test_judge_cell_na_when_judge_not_in_run(self):
        # Run with no judges (like old July JSON)
        run_no_judges = {"judges": []}
        stats_dict = {"scored": 3, "fails": 1, "parts": 0, "fail_pct": 33.3}
        self.assertEqual(bc.judge_cell(run_no_judges, "any-judge", stats_dict, "fail_pct"), "—")
        self.assertEqual(bc.judge_cell(run_no_judges, "any-judge", stats_dict, "counts"), "—")

        # Run with judges but scored=0 (no rows evaluated by that judge)
        run_with_judges = {"judges": ["j1", "j2"]}
        zero_stats = {"scored": 0, "fails": 0, "parts": 0, "fail_pct": 0.0}
        self.assertEqual(bc.judge_cell(run_with_judges, "j1", zero_stats, "fail_pct"), "—")

        # Run with judges and scored > 0 should render values
        real_stats = {"scored": 3, "fails": 1, "parts": 0, "fail_pct": 33.3}
        self.assertEqual(bc.judge_cell(run_with_judges, "j1", real_stats, "fail_pct"), "**33.3%**")
        self.assertEqual(bc.judge_cell(run_with_judges, "j1", real_stats, "counts"), "2 / 0 / 1")


class Newest(unittest.TestCase):
    """The July regression: an HHMM-only stamp sorts lexically, so OLIVIA_MODEL_BENCH_
    claude-sonnet-5_2250.json (2026-07-29, 7 rows, no judges) beat every run of today that
    finished before 22:50."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self._rd, bc.REPORT_DIR = bc.REPORT_DIR, self.dir.name

    def tearDown(self):
        bc.REPORT_DIR = self._rd
        self.dir.cleanup()

    def write(self, name, marker):
        with open(os.path.join(self.dir.name, name), "w") as fh:
            json.dump({"model": "claude-sonnet-5", "rows": [], "marker": marker}, fh)

    def test_picks_the_later_of_two_filenames(self):
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5_20260902-1130.json", "today")
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5_20260729-2250.json", "july")
        d, f = bc.newest("claude-sonnet-5")
        self.assertEqual((d["marker"], f), ("today", "OLIVIA_MODEL_BENCH_claude-sonnet-5_20260902-1130.json"))

    def test_a_legacy_hhmm_stamp_can_never_win(self):
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5_2250.json", "july")
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5_20260902-0900.json", "today")
        self.assertEqual(bc.newest("claude-sonnet-5")[0]["marker"], "today")

    def test_a_legacy_file_alone_fails_loudly_instead_of_being_used(self):
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5_2250.json", "july")
        with self.assertRaises(SystemExit):
            bc.newest("claude-sonnet-5")

    def test_an_effort_tagged_run_is_not_picked_up_by_the_bare_tag(self):
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5_20260902-0900.json", "bare")
        self.write("OLIVIA_MODEL_BENCH_claude-sonnet-5-none_20260902-2300.json", "effort")
        self.assertEqual(bc.newest("claude-sonnet-5")[0]["marker"], "bare")
        self.assertEqual(bc.newest("claude-sonnet-5-none")[0]["marker"], "effort")


def run(tag, passes=None, parity=None, budget=None):
    return {"tag": tag, "passes": passes, "parity": parity, "budget": budget}


class Conditions(unittest.TestCase):
    """The report used to assert 'WARM … forced first fetch on' whatever the run had done."""

    def test_warm_and_forced_when_the_envelope_says_so(self):
        out = bc.conditions_sentence([run("a", 2, False), run("b", 2, False)])
        self.assertIn("WARM", out)
        self.assertIn("forced first fetch on", out)

    def test_a_single_pass_is_not_called_warm(self):
        out = bc.conditions_sentence([run("a", 1, False), run("b", 1, False)])
        self.assertNotIn("WARM", out)
        self.assertIn("No warming pass ran", out)

    def test_parity_run_is_not_called_forced(self):
        self.assertIn("DISABLED for parity", bc.conditions_sentence([run("a", 2, True)]))

    def test_an_older_envelope_without_the_fields_claims_nothing(self):
        out = bc.conditions_sentence([run("a"), run("b", 2, False)])
        self.assertIn("not recorded", out)

    def test_mixed_warm_up_is_named(self):
        self.assertIn("Warm-up differs by run", bc.conditions_sentence([run("a", 1, False), run("b", 3, False)]))


class Budget(unittest.TestCase):
    def test_a_budget_gap_is_stated_not_hidden(self):
        out = bc.budget_sentence([run("claude-sonnet-5", budget=2000), run("gpt-5.6-terra-medium", budget=8000)])
        self.assertIn("DIFFER", out)
        self.assertIn("2,000", out)
        self.assertIn("8,000", out)

    def test_equal_budgets_say_so(self):
        self.assertIn("same output budget", bc.budget_sentence([run("a", budget=2000), run("b", budget=2000)]))

    def test_missing_budget_is_not_invented(self):
        self.assertIn("not recorded", bc.budget_sentence([run("a"), run("b")]))


class Truncated(unittest.TestCase):
    def test_truncated_calls_are_summed_and_tolerate_older_rows(self):
        rows = [row(1, "PASS", "PASS"), row(2, "PASS", "PASS")]
        rows[0]["metrics"]["truncated"] = 3
        self.assertEqual(bc.stats(rows, "claude-sonnet-5")["truncated"], 3)   # row 2 has no key


if __name__ == "__main__":
    unittest.main()
