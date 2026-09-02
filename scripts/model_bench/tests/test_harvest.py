import unittest
import kimi_harvest as kh

Q = {"id": 4002, "class": "CHAPTERS", "q": "I meant MDS Chapter", "expect": "re-route", "soft": False, "seq": "chap"}


def run_data(seed):
    return {"resultData": {"runData": {"Answer Seed": [{"data": {"main": [[{"json": seed}]]}}]}}}


SEED = {"to": "17866578153",
        "system": [{"type": "text", "text": "SYSTEM PROMPT", "cache_control": {"type": "ephemeral"}}],
        "tools": [{"name": "chapter_info", "input_schema": {"type": "object"}},
                  {"name": "find", "input_schema": {"type": "object"}, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": "what chapter should i join"},
                     {"role": "assistant", "content": "Here are the WhatsApp chats…"},
                     {"role": "user", "content": [{"type": "text", "text": "PRELOADED EVIDENCE …\nMEMBER MESSAGE:\nI meant MDS Chapter",
                                                   "cache_control": {"type": "ephemeral"}}]}]}


class SeedFromExecution(unittest.TestCase):
    def test_keeps_history_strips_cache_marks_records_phone(self):
        seed, reason = kh.seed_from_execution(run_data(SEED), Q)
        self.assertIsNone(reason)
        self.assertEqual(seed["id"], 4002)
        self.assertEqual(seed["phone"], "17866578153")
        self.assertEqual(seed["system"], "SYSTEM PROMPT")
        self.assertEqual(len(seed["messages"]), 3)
        self.assertEqual(seed["history_turns"], 2)
        self.assertNotIn("cache_control", str(seed["messages"]))
        self.assertNotIn("cache_control", str(seed["tools"]))
        self.assertTrue(seed["user"].endswith("I meant MDS Chapter"))

    def test_canned_lane_has_no_seed(self):
        self.assertEqual(kh.seed_from_execution({"resultData": {"runData": {}}}, Q), (None, "no_seed"))
        bad = dict(SEED, messages=[{"role": "assistant", "content": "x"}])
        self.assertEqual(kh.seed_from_execution(run_data(bad), Q), (None, "no_seed"))


if __name__ == "__main__":
    unittest.main()
