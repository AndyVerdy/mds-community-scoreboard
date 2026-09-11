"""#211 — no contact data may survive the Exa client boundary, raw payload included.
`python3 scripts/test_exa_client_scrub.py`"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_client as ex
from unittest import mock

fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)

# === Original 8 checks ===
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

# === CRITICAL 1: Obfuscated emails ===
out = ex.scrub({"text": "Reach jsmith(at)example(dot)com"})
check("obfuscated (at)/(dot) removed", "jsmith(at)example(dot)com" not in repr(out))

out = ex.scrub({"text": "Reach jsmith at example dot com"})
check("space at/dot removed", "jsmith at example dot com" not in repr(out))

out = ex.scrub({"text": "Reach jsmith[at]example[dot]com"})
check("bracket [at]/[dot] removed", "jsmith[at]example[dot]com" not in repr(out))

# === IMPORTANT 2: Contact keys ===
out = ex.scrub({"cell": 6195550142})
check("cell (int) nulled", out["cell"] is None)

out = ex.scrub({"fax": "+1-619-555-0142"})
check("fax (str) nulled", out["fax"] is None)

out = ex.scrub({"contactNumber": "6195550142"})
check("contactNumber nulled", out["contactNumber"] is None)

out = ex.scrub({"contact_number": "6195550142"})
check("contact_number nulled", out["contact_number"] is None)

out = ex.scrub({"msisdn": "916195550142"})
check("msisdn nulled", out["msisdn"] is None)

# === IMPORTANT 3: Asterisk-masked phones ===
out = ex.scrub({"text": "Call ***-***-0142"})
blob = repr(out)
check("asterisk-masked phone removed", "***-***-0142" not in blob)

# === IMPORTANT 4: URL and date preservation ===
out = ex.scrub({"text": "https://www.linkedin.com/profile/view?id=123456789"})
check("URL preserved", "https://www.linkedin.com/profile/view?id=123456789" in out["text"])

out = ex.scrub({"text": "Founded on 2011-05-03 in Austin."})
check("date 2011-05-03 preserved", "2011-05-03" in out["text"])

out = ex.scrub({"text": "Published 2025-09-13T00:00:00.000Z in New York."})
check("ISO timestamp preserved", "2025-09-13T00:00:00.000Z" in out["text"])

# === Regression: original phone pattern still works ===
out = ex.scrub({"text": "+91 99717 10129"})
check("phone +code still removed", "+91 99717 10129" not in repr(out))

# === IMPORTANT 5: Curl error handling ===
# Error 1: Non-zero return code
with mock.patch('exa_client.subprocess.run') as mock_run:
    mock_run.return_value = mock.Mock(returncode=1, stderr="Connection failed", stdout="")
    try:
        ex._post("search", {"query": "test"})
        check("curl non-zero return raises", False, "no exception raised")
    except SystemExit as e:
        check("curl non-zero return raises", "curl failed" in str(e))

# Error 2: Non-2xx status code
with mock.patch('exa_client.subprocess.run') as mock_run:
    mock_run.return_value = mock.Mock(returncode=0, stderr="", stdout='{"error": "test"}\n401')
    try:
        ex._post("search", {"query": "test"})
        check("curl 401 raises", False, "no exception raised")
    except SystemExit as e:
        check("curl 401 raises", "401" in str(e))

# Error 3: Non-JSON body
with mock.patch('exa_client.subprocess.run') as mock_run:
    mock_run.return_value = mock.Mock(returncode=0, stderr="", stdout='not json\n200')
    try:
        ex._post("search", {"query": "test"})
        check("curl non-JSON raises", False, "no exception raised")
    except SystemExit as e:
        check("curl non-JSON raises", "non-JSON" in str(e))

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
