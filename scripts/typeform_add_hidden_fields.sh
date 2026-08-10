#!/usr/bin/env bash
# Add the two hidden fields to the rebuilt Singapore Company Information form.
#
# WHY THIS IS A SCRIPT AND NOT A CURL I RAN: the harness allows POST /forms (create) but blocks
# PUT /forms/{id} (edit), so Claude can build a form but cannot modify one. Same restriction we hit
# on the Centurion Typeform edits — the fix is the same: Andy runs it.
#
# WHAT IT DOES: fetches the live form, adds hidden fields `restored` and `original_submitted_at`,
# PUTs it back, then re-reads and prints the result. Nothing else about the form changes.
#
# WHY THE HIDDEN FIELDS: the 7 surviving responses are going to be re-entered by hand into this
# rebuilt form. Typeform generates submitted_at server-side and it cannot be set, so every restored
# row would read today. These hidden values carry the real Jul 31 - Aug 6 dates into Typeform's own
# export, so a restored row is self-identifying instead of looking like a sponsor filled it in this
# morning.
#
#   bash scripts/typeform_add_hidden_fields.sh
set -euo pipefail

FORM_ID="GljwvNGO"
ENV_FILE="/Users/Born/mds-digest-web/.env.local"
PAT="$(grep '^CENTURION_TYPEFORM_PAT=' "$ENV_FILE" | cut -d= -f2-)"
[ -n "$PAT" ] || { echo "no CENTURION_TYPEFORM_PAT in $ENV_FILE"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -sS -H "Authorization: Bearer $PAT" \
     "https://api.typeform.com/forms/$FORM_ID" -o "$TMP/form.json"

python3 - "$TMP/form.json" "$TMP/put.json" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))

# Refuse to write if this is not the form we think it is. A PUT replaces the whole form, so a
# wrong target here would overwrite something real.
assert d.get("title", "").startswith("MDS Summit Singapore 2026 - Company Information"), \
    f"unexpected title: {d.get('title')!r} — aborting"
assert len(d.get("fields") or []) == 10, \
    f"expected 10 fields, found {len(d.get('fields') or [])} — aborting"

d["hidden"] = ["restored", "original_submitted_at"]
for k in ("id", "_links", "published_at", "last_updated_at", "created_at", "type"):
    d.pop(k, None)
json.dump(d, open(dst, "w"))
print(f"prepared: {len(d['fields'])} fields, {len(d.get('logic') or [])} logic rule(s), "
      f"hidden -> {d['hidden']}")
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
ok = d.get("hidden") == ["restored", "original_submitted_at"]
print(f"hidden fields live : {d.get('hidden')}")
print(f"fields             : {len(d.get('fields') or [])}")
print(f"logic rules        : {len(d.get('logic') or [])}")
print("RESULT             :", "OK" if ok and len(d.get("fields") or []) == 10 else "MISMATCH")
sys.exit(0 if ok else 1)
PY
