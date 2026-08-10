#!/usr/bin/env bash
# Put Squad Registration (paid) xCTBjrdW back into its ORIGINAL question order.
#
# WHY THIS IS A SCRIPT: the harness allows POST /forms (create) but blocks PUT /forms/{id} (edit),
# so Claude can build a form but cannot reorder one. Same restriction as the Singapore hidden
# fields — Andy runs it.
#
# WHY IT IS NEEDED: the rebuild inferred a field order, because no definition backup exists for
# this form. The true order was recoverable all along — digest.form_responses.raw stores the
# original API payload, and its `answers` array is in form order. It shows *Payment* was
# question 3, right after name and email, not last. Members paid up front before answering
# anything about themselves. This script restores that sequence.
#
# WHAT IT DOES NOT DO: add the payment field. The API only accepts a *variable* price and a
# payment field needs the Stripe connection, so question 3 still has to be inserted by hand in the
# editor. After running this, the slot for it is between "*What is your MDS account email?*" and
# "Preferred Phone Number (Call/SMS)".
#
#   bash scripts/typeform_fix_squad_paid_order.sh
set -euo pipefail

FORM_ID="xCTBjrdW"
ENV_FILE="/Users/Born/mds-digest-web/.env.local"
PAT="$(grep '^CENTURION_TYPEFORM_PAT=' "$ENV_FILE" | cut -d= -f2-)"
[ -n "$PAT" ] || { echo "no CENTURION_TYPEFORM_PAT in $ENV_FILE"; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
curl -sS -H "Authorization: Bearer $PAT" \
     "https://api.typeform.com/forms/$FORM_ID" -o "$TMP/form.json"

python3 - "$TMP/form.json" "$TMP/put.json" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))

assert d.get("title") == "Squad Registration (paid)", f"unexpected title {d.get('title')!r}"
assert len(d.get("fields") or []) == 18, f"expected 18 fields, found {len(d.get('fields') or [])}"

# Original order, read from digest.form_responses.raw -> answers[]. Payment (position 3) is
# omitted: it cannot be created over the API and must be added in the editor.
ORDER = ["sq_name", "sq_email",
         # <- *Payment* belonged here
         "sq_phone", "sq_niche", "sq_match", "sq_role", "sq_role2", "sq_want",
         "sq_family", "sq_traits", "sq_who", "sq_ttm",
         "sq_profile", "sq_photo", "sq_open", "sq_meeting", "sq_admission", "sq_nda"]

by_ref = {f["ref"]: f for f in d["fields"]}
missing = [r for r in ORDER if r not in by_ref]
extra   = [r for r in by_ref if r not in ORDER]
assert not missing and not extra, f"ref mismatch — missing {missing}, extra {extra}"

d["fields"] = [by_ref[r] for r in ORDER]
for k in ("id", "_links", "published_at", "last_updated_at", "created_at", "type"):
    d.pop(k, None)
json.dump(d, open(dst, "w"))
print(f"prepared: {len(d['fields'])} fields in original order")
PY

code=$(curl -sS -o "$TMP/res.json" -w '%{http_code}' -X PUT \
  "https://api.typeform.com/forms/$FORM_ID" \
  -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" \
  --data-binary @"$TMP/put.json")
echo "PUT HTTP $code"
[ "$code" = "200" ] || { echo "FAILED:"; head -c 600 "$TMP/res.json"; echo; exit 1; }

# Re-read from the API rather than trusting the PUT response.
curl -sS -H "Authorization: Bearer $PAT" \
     "https://api.typeform.com/forms/$FORM_ID" -o "$TMP/after.json"
python3 - "$TMP/after.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
want = ["sq_name", "sq_email", "sq_phone", "sq_niche", "sq_match", "sq_role", "sq_role2",
        "sq_want", "sq_family", "sq_traits", "sq_who", "sq_ttm", "sq_profile", "sq_photo",
        "sq_open", "sq_meeting", "sq_admission", "sq_nda"]
got = [f["ref"] for f in d["fields"]]
for i, f in enumerate(d["fields"], 1):
    print(f"  {i:2}. {f['title'].splitlines()[0][:64]}")
    if i == 2:
        print("   -> *Payment* goes here (add in the editor; needs the Stripe connection)")
print("RESULT:", "OK" if got == want else f"MISMATCH\n  got  {got}\n  want {want}")
sys.exit(0 if got == want else 1)
PY
