"""#211 — no contact data may survive the Exa client boundary, raw payload included.
`python3 scripts/test_exa_client_scrub.py`"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_client as ex

fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)

payload = {
    "results": [{
        "title": "Profile of Ian Sells",
        "text": "Reach me at ia****@jo****.com or ian.sells@example.com, cell +1 (619) 555-0142.",
        "emails": ["support@hectorai.live"],
        "phone": "+91 99717 10129",
        "entities": [{"properties": {"name": "Ian Sells", "email": "x@y.com"}}],
    }]
}
out = ex.scrub(payload)
blob = repr(out)

check("literal email removed", "ian.sells@example.com" not in blob)
check("masked email removed", "ia****@jo****.com" not in blob)
check("emails list emptied", out["results"][0]["emails"] == [])
check("phone field nulled", out["results"][0]["phone"] is None)
check("phone inside prose removed", "619" not in blob and "99717" not in blob)
check("nested entity email removed", "x@y.com" not in blob)
check("non-contact text survives", "Profile of Ian Sells" in blob)
check("name survives", "Ian Sells" in blob)

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
