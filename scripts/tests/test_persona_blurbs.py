# scripts/tests/test_persona_blurbs.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from persona_blurbs import build_prompt, clean_blurb

def test_prompt_carries_the_summary_and_the_rules():
    p = build_prompt("Mo Kuhail", "Mo is a lean operator in Ottawa. He ships 300k orders a year across 6 SKUs.")
    assert "Mo Kuhail" in p and "two or three sentences" in p and "no numbers" in p

def test_clean_blurb_trims_quotes_and_caps_length():
    assert clean_blurb('"Mo runs a lean home-goods brand from Ottawa. He answers fast and tests before he recommends."') == "Mo runs a lean home-goods brand from Ottawa. He answers fast and tests before he recommends."
    assert len(clean_blurb("x. " * 400)) <= 420
