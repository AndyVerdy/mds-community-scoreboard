import json, unittest
import olivia_eval as oe

Q = {"id": 1, "q": "Who leads the Texas chapter?", "expect": "Names the SoTex leads", "soft": True}


class Prompt(unittest.TestCase):
    def test_rubric_and_question_and_schema(self):
        system, user, schema = oe.judge_prompt(Q, "Jane Doe leads it.")
        self.assertIn("EXPECTED (warehouse-verified ground truth): Names the SoTex leads", user)
        self.assertIn("QUESTION: Who leads the Texas chapter?", user)
        self.assertIn("OLIVIA'S ANSWER:\nJane Doe leads it.", user)
        self.assertIn("This question is SOFT", system)
        self.assertEqual(schema["properties"]["verdict"]["enum"], ["PASS", "PARTIAL", "FAIL"])
        self.assertEqual(schema["required"], ["verdict", "reason", "fail_class"])
        self.assertFalse(schema["additionalProperties"])

    def test_no_expectation_means_honest_miss_rubric(self):
        _, user, _ = oe.judge_prompt({"id": 2, "q": "x"}, "I can't find that.")
        self.assertIn("GROUND TRUTH: the asked-for content is NOT in Olivia's data", user)


class OpenAIParse(unittest.TestCase):
    def test_parses_strict_json_content(self):
        raw = json.dumps({"choices": [{"message": {"content": json.dumps(
            {"verdict": "PASS", "reason": "names match", "fail_class": "none"})}}]})
        self.assertEqual(oe.parse_openai_verdict(raw)["verdict"], "PASS")

    def test_rejects_garbage_and_unknown_verdicts(self):
        self.assertIsNone(oe.parse_openai_verdict("not json"))
        self.assertIsNone(oe.parse_openai_verdict(json.dumps({"error": {"message": "boom"}})))
        raw = json.dumps({"choices": [{"message": {"content": json.dumps({"verdict": "MAYBE", "reason": "", "fail_class": "none"})}}]})
        self.assertIsNone(oe.parse_openai_verdict(raw))


if __name__ == "__main__":
    unittest.main()
