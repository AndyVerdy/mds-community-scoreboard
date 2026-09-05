# scripts/tests/test_persona_blurbs.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from persona_blurbs import build_prompt, clean_blurb, compute_status_and_detail

def test_prompt_carries_the_summary_and_the_rules():
    p = build_prompt("Sam Tester", "Sam is a lean operator in Springfield. Sam runs a garden-tools brand across a handful of SKUs.")
    assert "Sam Tester" in p and "two or three sentences" in p and "no numbers" in p

def test_clean_blurb_trims_quotes_and_caps_length():
    assert clean_blurb('"Sam runs a lean garden-tools brand from Springfield. Sam answers fast and tests before he recommends."') == "Sam runs a lean garden-tools brand from Springfield. Sam answers fast and tests before he recommends."
    assert len(clean_blurb("x. " * 400)) <= 420


# #161 review finding: this job used to call heartbeat(key, "ok", detail) unconditionally,
# ignoring `failed` entirely. Four cases, same shape as test_cache_member_photos.py's
# test_compute_status_and_detail_error_thresholds: nothing attempted is healthy "ok"; some
# failures under the 25% threshold is "ok"; over 25% is "error"; every attempted member
# failing (100%) is "error".
def test_compute_status_and_detail_nothing_attempted_is_ok():
    status, detail = compute_status_and_detail(0, 5, 0, [], 0, 0)
    assert status == "ok"
    assert "wrote 0" in detail and "skipped 5" in detail and "failed 0" in detail

def test_compute_status_and_detail_under_threshold_is_ok():
    status, detail = compute_status_and_detail(18, 0, 2, ["m1", "m2"], 4000, 900)
    assert status == "ok"  # 2 failed / 20 attempted = 10%
    assert "failed 2" in detail

def test_compute_status_and_detail_over_threshold_is_error():
    status, detail = compute_status_and_detail(2, 0, 3, ["m1", "m2", "m3"], 500, 100)
    assert status == "error"  # 3 failed / 5 attempted = 60%
    assert "failed 3" in detail

def test_compute_status_and_detail_every_attempted_failed_is_error():
    status, _ = compute_status_and_detail(0, 1, 3, ["m1", "m2", "m3"], 0, 0)
    assert status == "error"  # 3 failed / 3 attempted = 100%
