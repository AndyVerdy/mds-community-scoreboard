import json, unittest
import bench_tools as bt

TOOLS = [
    {"name": "content_search", "input_schema": {"type": "object", "properties": {
        "p_query": {"type": "string"}, "p_terms": {"type": "array"}, "p_sources": {"type": "array"},
        "p_chat": {"type": "string"}}}},
    {"name": "find", "input_schema": {"type": "object", "properties": {
        "where": {"type": "object"}, "limit": {"type": "integer"}, "want": {"type": "string"}}}},
]
NOKEYS = {"supa": "", "voyage": "", "olivia_secret": ""}


class ExecName(unittest.TestCase):
    def test_last_duplicate_key_wins_as_in_the_js_literal(self):
        self.assertEqual(bt.EXEC_NAME["event_lookup"], "event_lookup_v3")
        self.assertEqual(bt.EXEC_NAME["chat_recommendations"], "chat_recommendations_v3")
        self.assertEqual(bt.EXEC_NAME["content_search"], "content_search_v2")
        self.assertNotIn("expertise_search", bt.EXEC_NAME)


class TranscriptRule(unittest.TestCase):
    def test_appends_call_transcript(self):
        out = bt.transcript_rule("content_search", {"p_sources": ["wa_message"]})
        self.assertEqual(out["p_sources"], ["wa_message", "call_transcript"])

    def test_chat_scoped_untouched(self):
        a = {"p_sources": ["wa_message"], "p_chat": "MDS AI"}
        self.assertEqual(bt.transcript_rule("content_search", a), a)

    def test_no_sources_untouched_and_other_tools_untouched(self):
        self.assertEqual(bt.transcript_rule("content_search", {"p_query": "x"}), {"p_query": "x"})
        self.assertEqual(bt.transcript_rule("video_search", {"p_sources": ["a"]}), {"p_sources": ["a"]})


class VoyageQuery(unittest.TestCase):
    """Voyage Embed node: q = a.p_query || (Array.isArray(a.p_terms) ? a.p_terms.join(' ') : '')
    then input: [String(q).slice(0, 400) || '(empty)']."""

    def test_query_wins_and_is_capped_at_400(self):
        self.assertEqual(bt.voyage_query({"p_query": "resellers in Singapore"}), "resellers in Singapore")
        self.assertEqual(len(bt.voyage_query({"p_query": "z" * 900})), 400)

    def test_terms_list_is_space_joined(self):
        self.assertEqual(bt.voyage_query({"p_terms": ["reseller", "Summit"]}), "reseller Summit")

    def test_string_p_terms_is_never_char_joined(self):
        # the node's Array.isArray guard: a STRING p_terms yields '' -> '(empty)', not 'r e s'
        self.assertEqual(bt.voyage_query({"p_terms": "reseller"}), "(empty)")

    def test_blank_embeds_the_literal_empty(self):
        self.assertEqual(bt.voyage_query({}), "(empty)")
        self.assertEqual(bt.voyage_query({"p_query": "", "p_terms": []}), "(empty)")


class Coerce(unittest.TestCase):
    def test_comma_string_becomes_array(self):
        out = bt.coerce_args("content_search", {"p_terms": "reseller, Summit; Singapore"}, TOOLS)
        self.assertEqual(out["p_terms"], ["reseller", "Summit", "Singapore"])

    def test_empty_array_arg_is_dropped(self):
        self.assertNotIn("p_terms", bt.coerce_args("content_search", {"p_terms": ""}, TOOLS))

    def test_array_arg_known_only_by_fallback_list(self):
        out = bt.coerce_args("member_match", {"p_want": "a|b"}, TOOLS)   # no schema for member_match
        self.assertEqual(out["p_want"], ["a", "b"])

    def test_object_string_parsed_and_bad_json_left_alone(self):
        out = bt.coerce_args("find", {"where": '{"state":"TX"}'}, TOOLS)
        self.assertEqual(out["where"], {"state": "TX"})
        out = bt.coerce_args("find", {"where": "not json"}, TOOLS)
        self.assertEqual(out["where"], "not json")

    def test_integer_string_and_list_to_string(self):
        out = bt.coerce_args("find", {"limit": " 12 ", "want": ["a", "", "b"]}, TOOLS)
        self.assertEqual(out["limit"], 12)
        self.assertEqual(out["want"], "a, b")

    def test_unknown_keys_pass_through(self):
        out = bt.coerce_args("find", {"p_phone": "1", "p_embedding": "[0.1]"}, TOOLS)
        self.assertEqual(out, {"p_phone": "1", "p_embedding": "[0.1]"})


class Route(unittest.TestCase):
    def test_supabase_rpc_uses_exec_name(self):
        url, body = bt.route("event_lookup", {"p_query": "x"}, "1786")
        self.assertEqual(url, "https://digest.mds.co/api/olivia/schedule")   # event_* goes to the app
        url, body = bt.route("member_match", {"p_state": "TX"}, "1786")
        self.assertEqual(url, bt.SUPA + "/rpc/member_match_v2")
        self.assertEqual(body, {"p_state": "TX"})

    def test_find_and_event_who_get_phone_and_op(self):
        url, body = bt.route("find", {"where": {}}, "1786")
        self.assertEqual((url, body["phone"]), ("https://digest.mds.co/api/olivia/find", "1786"))
        url, body = bt.route("event_who", {"p_event": "summit"}, "1786")
        self.assertEqual(body, {"p_event": "summit", "phone": "1786", "op": "people"})
        url, body = bt.route("event_schedule", {"op": "day"}, "1786")
        self.assertEqual(body, {"op": "day", "phone": "1786"})

    def test_org_docs_carries_phone_like_the_live_answer_tool(self):
        # Answer Tool's jsonBody adds { phone } for event_* OR org_docs OR find — org_docs included.
        self.assertEqual(bt.route("org_docs", {"q": "x"}, "1786"),
                         ("https://digest.mds.co/api/olivia/kb", {"q": "x", "phone": "1786"}))

    def test_member_intro_gets_op_request_and_phone(self):
        url, body = bt.route("member_intro", {"target": "rec1"}, "1786")
        self.assertEqual((url, body["op"], body["phone"]), ("https://digest.mds.co/api/olivia/intro", "request", "1786"))


class ClipSafe(unittest.TestCase):
    """Answer Merge ~24-34. Every case here was run through the live JS and matched byte for byte."""

    def test_short_string_untouched(self):
        self.assertEqual(bt.clip_safe("short", 99), "short")

    def test_plain_cut_gets_an_ellipsis(self):
        self.assertEqual(bt.clip_safe("x" * 2000, 1600), "x" * 1600 + "…")

    def test_never_ends_inside_a_url(self):
        out = bt.clip_safe("a b https://mds.co/very/long/path/that/keeps/going", 20)
        self.assertEqual(out, "a b…")           # the half-eaten link fragment is dropped whole
        self.assertNotIn("https", out)

    def test_url_that_ended_before_the_cut_survives(self):
        self.assertEqual(bt.clip_safe("ends here https://a.co/z", 24), "ends here https://a.co/z")


class RestrictFix(unittest.TestCase):
    """Answer Merge ~45-58 — the flag is the LIBRARY's, not this asker's."""

    def test_flag_and_note_dropped_on_a_row_this_asker_was_served(self):
        row = bt.restrict_fix({"is_restricted": True, "access_note": "you hold a grant",
                               "description_snippet": "A talk about pricing"})
        self.assertEqual(row, {"description_snippet": "A talk about pricing"})

    def test_a_row_really_withheld_keeps_its_sentinel_and_flag(self):
        row = bt.restrict_fix({"is_restricted": True, "access_note": "n",
                               "description_snippet": "[RESTRICTED VIDEO] withheld"})
        self.assertTrue(row["is_restricted"])
        self.assertIn("access_note", row)

    def test_unrestricted_row_untouched(self):
        self.assertEqual(bt.restrict_fix({"is_restricted": False}), {"is_restricted": False})


class ResultBody(unittest.TestCase):
    def test_nothing_at_all(self):
        self.assertEqual(json.loads(bt.result_body(None)), {"error": "tool returned nothing"})

    def test_rpc_error_is_a_tool_error_with_the_failnote_not_a_miss(self):
        out = bt.result_body({"code": "22P02", "message": "malformed array literal"}, tool="content_search")
        head, _, note = out.partition("\n")
        self.assertEqual(json.loads(head), {"tool_error": True, "tool": "content_search",
                                            "detail": "malformed array literal"})
        self.assertEqual(note, bt.FAILNOTE)

    def test_http_status_survives_even_when_the_body_is_not_an_error_shape(self):
        out = bt.result_body([{"a": 1}], tool="find", http_status=500)
        head = json.loads(out.split("\n")[0])
        self.assertEqual((head["tool_error"], head["tool"], head["http_status"]), (True, "find", 500))
        self.assertTrue(head["detail"].startswith("HTTP 500 — "))
        self.assertTrue(out.endswith(bt.FAILNOTE))

    def test_401_from_an_app_route(self):
        head = json.loads(bt.result_body({"error": "unauthorized"}, tool="org_docs", http_status=401).split("\n")[0])
        self.assertEqual(head["http_status"], 401)

    def test_transport_failure_scrapes_the_status_out_of_the_message(self):
        head = json.loads(bt.result_body({"error": "curl: (22) The requested URL returned error: 502"},
                                         tool="find").split("\n")[0])
        self.assertEqual(head["http_status"], 502)

    def test_error_with_no_status_at_all(self):
        head = json.loads(bt.result_body({"error": "boom"}, tool="find").split("\n")[0])
        self.assertEqual((head["http_status"], head["detail"]), ("error", "boom"))

    def test_full_response_unwrapped(self):
        self.assertEqual(json.loads(bt.result_body({"statusCode": 200, "headers": {}, "body": [{"a": 1}]})), [{"a": 1}])

    def test_tiered_trim_keeps_every_row(self):
        rows = [{"t": "x" * 2000} for _ in range(20)]
        out = json.loads(bt.result_body(rows))
        self.assertEqual(len(out), 20)
        self.assertEqual(len(out[0]["t"]), 1601)     # 1600 + ellipsis
        self.assertEqual(len(out[6]["t"]), 501)
        self.assertEqual(len(out[19]["t"]), 221)

    def test_over_cap_squeezes_the_text_and_keeps_every_row(self):
        # 5×1500 + 10×501 + 85×221 ≈ 31K > CAP. The live node halves the per-tier budget until it
        # fits and keeps all 100 rows; the old blunt slice dropped the tail (the fb_post bug).
        # Byte-identical to the live JS on this input (16,851 chars).
        body = bt.result_body([{"t": "y" * 1500} for _ in range(100)])
        rows = json.loads(body)
        self.assertEqual(len(rows), 100)
        self.assertLessEqual(len(body), bt.CAP)
        self.assertEqual(len(rows[0]["t"]), 801)     # TIER 1600 × 0.5, + ellipsis
        self.assertEqual(len(rows[99]["t"]), 111)    # TIER 220 × 0.5, + ellipsis
        self.assertFalse(body.endswith(bt.TRUNC))

    def test_url_fields_are_exempt_from_the_squeeze_and_the_backstop_still_exists(self):
        body = bt.result_body([{"t": "z" * 3000, "post_url": "https://facebook.com/" + "p" * 400}
                               for _ in range(60)])
        self.assertLessEqual(len(body), bt.CAP + 60)
        self.assertTrue(body.endswith(bt.TRUNC))     # unsqueezable: the exempt urls alone blow CAP
        self.assertIn("https://facebook.com/" + "p" * 400, body)


class WriteStubs(unittest.TestCase):
    """Nothing that reaches a real member or the MDS team is ever executed by the bench."""

    def test_member_intro_never_leaves_the_machine(self):
        out = bt.run_tool("member_intro", {"target": "rec1"}, TOOLS, NOKEYS, "1786")
        self.assertIn("member_intro is disabled in the bench", out)

    def test_report_create_never_files_a_real_report(self):
        out = bt.run_tool("report_create", {"p_text": "the wifi is broken"}, TOOLS, NOKEYS, "1786")
        self.assertIn("report_create is disabled in the bench", out)
        self.assertIn("olivia_reports", out)

    def test_event_schedule_remind_and_unremind_are_short_circuited(self):
        for op in ("remind", "unremind"):
            out = bt.run_tool("event_schedule", {"op": op, "q": "keynote"}, TOOLS, NOKEYS, "1786")
            self.assertIn(f"event_schedule op={op} is disabled in the bench", out)
            self.assertIn("WhatsApp", out)

    def test_read_only_event_schedule_ops_are_not_stubbed(self):
        for op in ("agenda", "next", "day", "where", "reminders"):
            self.assertIsNone(bt.write_stub("event_schedule", {"op": op}))
        self.assertIsNone(bt.write_stub("content_search", {"p_query": "x"}))


class Post(unittest.TestCase):
    def test_returns_status_and_body_and_reports_a_transport_failure_as_status_zero(self):
        # nothing listens on 127.0.0.1:1 — curl fails without leaving the machine
        status, body = bt.post("http://127.0.0.1:1/", {}, {"a": 1}, timeout=2)
        self.assertEqual(status, 0)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
