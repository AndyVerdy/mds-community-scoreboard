"""#211 — the three entities that collided on "Happy Nuts" in the 2026-09-11 sweep must all be
rejected or held below full confidence. Spec AC 9d.
`python3 scripts/test_exa_presence_corroboration.py`"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_member_presence as P

fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)

anchors = P.anchors_for({
    "Brand Name": '["Happy Nuts / Happy Curves", "Happy Innovations (Happy Nuts, Happy Curves, Happy Soles)"]',
    "Own Website & % of Revenue": "myhappynuts.com",
})
check("brand names parsed out of the array", "happy innovations" in anchors, str(anchors))

good = "Matthew Greene, CEO of Happy Innovations, launches Happy Soles, the company's third brand."
check("the real one corroborates", P.corroborate(good, anchors) is not None)

chiba = "A Visit to Happy Nuts Day's Factory in Chiba Prefecture - Kokoro Media"
vietnam = "Phuong Hoang, Founder/CEO at Happy Nuts, corporate wellness gifting, Ho Chi Minh City"
dubai = "Konstantinos Balogiannis, Co-Founder & Co-Managing Partner, Gourmet Happy Nuts LLC, Dubai"
for name, text in (("chiba factory", chiba), ("vietnam gifting", vietnam), ("dubai llc", dubai)):
    check(f"{name} is not corroborated", P.corroborate(text, anchors) is None)

check("own domain is excluded, not corroborated",
      "myhappynuts.com" in P.own_domains({"Own Website & % of Revenue": "myhappynuts.com"}))

check("speaker page classified as speaking",
      P.classify("https://amzsummits.com/speakers/ian-sells/", None) == "speaking")
check("podcast classified as podcast",
      P.classify("https://freeup.net/blog/podcast/selling-on-amazon/", None) == "podcast")
check("youtube classified as video",
      P.classify("https://www.youtube.com/watch?v=abc", None) == "video")
check("news category respected",
      P.classify("https://www.cnbc.com/2025/01/01/x.html", "news") == "news")

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
