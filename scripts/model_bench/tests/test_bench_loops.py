import unittest
import kimi_bench as kb

SEED = {"id": 1, "q": "x", "system": "SYS", "phone": "17866578153",
        "tools": [{"name": "find", "description": "finder", "input_schema": {"type": "object", "properties": {}}}],
        "messages": [{"role": "user", "content": "first"},
                     {"role": "assistant", "content": "reply"},
                     {"role": "user", "content": [{"type": "text", "text": "PRELOADED …"}, {"type": "text", "text": "MEMBER MESSAGE: now"}]}],
        "user": "PRELOADED … MEMBER MESSAGE: now"}


class Prices(unittest.TestCase):
    def test_current_list_prices(self):
        self.assertEqual(kb.PRICES["claude-sonnet-5"], {"api": "anthropic", "in": 2.00, "out": 10.00, "cache_r": 0.20, "cache_w": 2.50})
        self.assertEqual(kb.PRICES["gpt-5.6-terra"], {"api": "openai", "in": 2.00, "out": 12.00, "cache_r": 0.20, "cache_w": 0.0})

    def test_cost(self):
        m = {"in": 1000, "out": 100, "cache_r": 30000, "cache_w": 0}
        self.assertAlmostEqual(kb.cost("claude-sonnet-5", m), 0.009)
        self.assertAlmostEqual(kb.cost("gpt-5.6-terra", m), 0.0092)

    def test_run_tag(self):
        self.assertEqual(kb.run_tag("claude-sonnet-5", "medium"), "claude-sonnet-5")
        self.assertEqual(kb.run_tag("gpt-5.6-terra", "none"), "gpt-5.6-terra-none")


class Messages(unittest.TestCase):
    def test_anthropic_history_replayed_with_one_cache_mark_on_the_last_block(self):
        msgs = kb.anthropic_messages(SEED)
        self.assertEqual([m["role"] for m in msgs], ["user", "assistant", "user"])
        self.assertEqual(msgs[0]["content"], "first")
        last = msgs[-1]["content"]
        self.assertEqual(last[-1]["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("cache_control", last[0])

    def test_anthropic_single_turn_fallback(self):
        msgs = kb.anthropic_messages({"user": "only"})
        self.assertEqual(msgs, [{"role": "user", "content": [{"type": "text", "text": "only", "cache_control": {"type": "ephemeral"}}]}])

    def test_responses_input_flattens_text_blocks(self):
        items = kb.responses_input(SEED)
        self.assertEqual(items, [{"role": "user", "content": "first"}, {"role": "assistant", "content": "reply"},
                                 {"role": "user", "content": "PRELOADED …\nMEMBER MESSAGE: now"}])

    def test_responses_tools_shape(self):
        self.assertEqual(kb.responses_tools(SEED["tools"]),
                         [{"type": "function", "name": "find", "description": "finder", "parameters": {"type": "object", "properties": {}}}])


class Usage(unittest.TestCase):
    def test_openai_usage(self):
        m = kb.new_metrics()
        kb.add_openai_usage(m, {"input_tokens": 35000, "input_tokens_details": {"cached_tokens": 31000},
                                "output_tokens": 900, "output_tokens_details": {"reasoning_tokens": 400}})
        self.assertEqual((m["in"], m["cache_r"], m["out"], m["reasoning"], m["calls"]), (4000, 31000, 900, 400, 1))

    def test_anthropic_usage(self):
        m = kb.new_metrics()
        kb.add_anthropic_usage(m, {"input_tokens": 120, "output_tokens": 500, "cache_read_input_tokens": 31000, "cache_creation_input_tokens": 8000})
        self.assertEqual((m["in"], m["out"], m["cache_r"], m["cache_w"], m["reasoning"], m["calls"]), (120, 500, 31000, 8000, 0, 1))


class Retry(unittest.TestCase):
    def test_retryable_shapes(self):
        self.assertTrue(kb.retryable({"error": {"type": "rate_limit_error"}}))          # anthropic 429
        self.assertTrue(kb.retryable({"error": {"type": "overloaded_error"}}))          # anthropic 529
        self.assertTrue(kb.retryable({"error": {"code": "rate_limit_exceeded", "type": "tokens"}}))   # openai 429
        self.assertTrue(kb.retryable({"error": {"type": "server_error"}}))              # openai 5xx
        self.assertTrue(kb.retryable({"error": "curl: (28) Operation timed out"}))     # transport
        self.assertFalse(kb.retryable({"error": {"type": "invalid_request_error"}}))
        self.assertFalse(kb.retryable({"usage": {}, "output": []}))


# ---------------------------------------------------------------- the loop itself
def _anth_tool(i=1):
    return {"content": [{"type": "tool_use", "id": f"tu{i}", "name": "find", "input": {}}],
            "stop_reason": "tool_use", "usage": {"input_tokens": 10, "output_tokens": 5}}


def _anth_text(t="the answer", stop="end_turn"):
    return {"content": ([{"type": "text", "text": t}] if t else []), "stop_reason": stop,
            "usage": {"input_tokens": 10, "output_tokens": 5}}


def _oai_tool(i=1):
    return {"status": "completed", "output": [{"type": "function_call", "call_id": f"c{i}",
                                               "name": "find", "arguments": "{}"}],
            "usage": {"input_tokens": 10, "output_tokens": 5}}


def _oai_text(t="the answer", status="completed", incomplete=None):
    d = {"status": status, "output": ([{"type": "message", "content": [{"type": "output_text", "text": t}]}]
                                      if t else []), "usage": {"input_tokens": 10, "output_tokens": 5}}
    if incomplete:
        d["incomplete_details"] = {"reason": incomplete}
    return d


class LoopHarness(unittest.TestCase):
    """The loops with the API and the tools replaced — no key, no request, no spend."""

    def setUp(self):
        self.tool_calls = []
        self._post, self._run = kb.post_retry, kb.run_tool
        kb.run_tool = lambda name, args, seed: self.tool_calls.append(name) or "[]"
        kb.K.update({"anthropic": "test-not-a-key", "openai": "test-not-a-key"})   # never sent

    def tearDown(self):
        kb.post_retry, kb.run_tool = self._post, self._run
        kb.K.clear()

    def script(self, responses):
        it = iter(responses)
        kb.post_retry = lambda *a, **k: (200, next(it))


class IterationCap(LoopHarness):
    """The graph gates the TOOL branch on state.iter < max_iter, so five tool rounds are followed
    by a sixth call that answers. Stopping at five calls ran the tools and binned the results."""

    def test_anthropic_answers_on_the_sixth_call(self):
        self.script([_anth_tool(i) for i in range(5)] + [_anth_text("final")])
        ans, m = kb.loop_anthropic(SEED, "claude-sonnet-5")
        self.assertEqual(ans, "final")
        self.assertEqual((m["calls"], m["iters"]), (6, 5))
        self.assertEqual(len(self.tool_calls), 5)

    def test_anthropic_never_runs_tools_it_cannot_use(self):
        self.script([_anth_tool(i) for i in range(6)])
        ans, m = kb.loop_anthropic(SEED, "claude-sonnet-5")
        self.assertTrue(ans.startswith("[EMPTY ANSWER]"), ans)
        self.assertIn("iteration cap", ans)
        self.assertEqual((m["calls"], m["iters"]), (6, 5))
        self.assertEqual(len(self.tool_calls), 5)          # NOT 6 — the last lap must not spend

    def test_openai_answers_on_the_sixth_call(self):
        self.script([_oai_tool(i) for i in range(5)] + [_oai_text("final")])
        ans, m = kb.loop_openai(SEED, "gpt-5.6-terra", "medium")
        self.assertEqual(ans, "final")
        self.assertEqual((m["calls"], m["iters"]), (6, 5))
        self.assertEqual(len(self.tool_calls), 5)

    def test_openai_never_runs_tools_it_cannot_use(self):
        self.script([_oai_tool(i) for i in range(6)])
        ans, m = kb.loop_openai(SEED, "gpt-5.6-terra", "medium")
        self.assertTrue(ans.startswith("[EMPTY ANSWER]"), ans)
        self.assertEqual(len(self.tool_calls), 5)


class EmptyAndTruncated(LoopHarness):
    """An empty content with no tool call is an error row; hitting the output budget is counted."""

    def test_anthropic_empty_answer_is_an_error_row(self):
        self.script([_anth_text("", stop="end_turn")])
        ans, m = kb.loop_anthropic(SEED, "claude-sonnet-5")
        self.assertEqual(ans, "[EMPTY ANSWER] status=end_turn reason=no text block in the reply")
        self.assertEqual(m["truncated"], 0)

    def test_anthropic_max_tokens_counts_as_truncated(self):
        self.script([_anth_text("", stop="max_tokens")])
        ans, m = kb.loop_anthropic(SEED, "claude-sonnet-5")
        self.assertIn("status=max_tokens", ans)
        self.assertEqual(m["truncated"], 1)

    def test_a_truncated_answer_is_still_an_answer_but_is_counted(self):
        self.script([_anth_text("half a sen", stop="max_tokens")])
        ans, m = kb.loop_anthropic(SEED, "claude-sonnet-5")
        self.assertEqual((ans, m["truncated"]), ("half a sen", 1))

    def test_openai_incomplete_is_read_and_reported(self):
        self.script([_oai_text("", status="incomplete", incomplete="max_output_tokens")])
        ans, m = kb.loop_openai(SEED, "gpt-5.6-terra", "medium")
        self.assertEqual(ans, "[EMPTY ANSWER] status=incomplete reason=max_output_tokens")
        self.assertEqual(m["truncated"], 1)

    def test_openai_empty_text_on_a_completed_response(self):
        self.script([_oai_text("")])
        ans, m = kb.loop_openai(SEED, "gpt-5.6-terra", "medium")
        self.assertEqual(ans, "[EMPTY ANSWER] status=completed reason=no output_text")
        self.assertEqual(m["truncated"], 0)


class LoopErrorsAreNotGraded(unittest.TestCase):
    """A row that never produced an answer must not be handed to the judge — it returns FAIL and
    the fail % then tracks whichever vendor had the worse hour on its API."""

    def test_every_bracket_marker_is_an_error_verdict(self):
        for a in ("[API ERROR] 429 rate_limit", "[no final answer inside iteration cap]",
                  "[EMPTY ANSWER] status=incomplete reason=max_output_tokens"):
            v = kb.loop_error_verdict(a)
            self.assertEqual(v, {"verdict": "ERROR", "reason": "loop error — not graded", "fail_class": None})

    def test_a_real_answer_is_graded_normally(self):
        self.assertIsNone(kb.loop_error_verdict("The Texas chapter is led by …"))
        self.assertIsNone(kb.loop_error_verdict(""))

    def test_error_verdicts_are_excluded_from_the_scored_set(self):
        # main() scores only PASS/PARTIAL/FAIL, so an ERROR row cannot move the fail %
        self.assertNotIn(kb.loop_error_verdict("[API ERROR] x")["verdict"], ("PASS", "PARTIAL", "FAIL"))


class Metrics(unittest.TestCase):
    def test_truncated_is_a_metric(self):
        self.assertEqual(kb.new_metrics()["truncated"], 0)


if __name__ == "__main__":
    unittest.main()
