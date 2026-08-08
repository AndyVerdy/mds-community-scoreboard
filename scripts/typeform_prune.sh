#!/usr/bin/env bash
# Typeform prune — delete forms that have NEVER received a response.
#
# Andy runs this, not Claude: it permanently deletes forms from the live Typeform account.
#
#   bash scripts/typeform_prune.sh            # DRY RUN — lists what it would delete
#   bash scripts/typeform_prune.sh --apply    # actually deletes
#
# Safety, in order of importance:
#   1. Every form is re-checked LIVE for its response count immediately before deletion.
#      A form that has gained even one response since the inventory is SKIPPED, not deleted.
#   2. Olivia's five canonical forms are hard-excluded by id, belt and braces.
#   3. Dry run is the default. --apply is the only way to delete anything.
#   4. Every action is appended to scripts/typeform_prune.log with a timestamp.
set -uo pipefail

ENV_FILE="/Users/Born/mds-digest-web/.env.local"
LOG="$(dirname "$0")/typeform_prune.log"
IDS_FILE="$(dirname "$0")/typeform_prune_ids.txt"
PAT="$(grep '^CENTURION_TYPEFORM_PAT=' "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'"' ')"
[ -n "$PAT" ] || { echo "no CENTURION_TYPEFORM_PAT in $ENV_FILE"; exit 1; }

# Olivia's canonical five — never delete, whatever the response count says.
NEVER="DFeK5yop FsVHzNN9 mkUJqsfM I409BFlj DXs5mhZn"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
[ $APPLY -eq 1 ] || echo "DRY RUN — nothing will be deleted. Re-run with --apply to delete."

deleted=0; skipped=0; total=0
while read -r id title; do
  [ -z "$id" ] && continue
  total=$((total+1))

  case " $NEVER " in *" $id "*)
    echo "  SKIP  $id  — Olivia canonical form ($title)"; skipped=$((skipped+1)); continue;;
  esac

  # Re-check live: only ever delete a form that still has zero responses.
  n=$(curl -sS -m 30 "https://api.typeform.com/forms/$id/responses?page_size=1" \
        -H "Authorization: Bearer $PAT" \
      | python3 -c 'import json,sys;print(json.load(sys.stdin).get("total_items","?"))' 2>/dev/null)

  if [ "$n" != "0" ]; then
    echo "  SKIP  $id  — has $n responses now ($title)"; skipped=$((skipped+1)); continue
  fi

  if [ $APPLY -eq 0 ]; then
    echo "  would delete  $id  ($title)"; continue
  fi

  code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' -X DELETE \
           "https://api.typeform.com/forms/$id" -H "Authorization: Bearer $PAT")
  if [ "$code" = "204" ]; then
    echo "  DELETED  $id  ($title)"
    echo "$(date -u +%FT%TZ)  deleted $id  $title" >> "$LOG"
    deleted=$((deleted+1))
  else
    echo "  FAILED   $id  — HTTP $code ($title)"
    echo "$(date -u +%FT%TZ)  FAILED $id http=$code  $title" >> "$LOG"
  fi
done < "$IDS_FILE"

echo
echo "$total considered · $deleted deleted · $skipped skipped"
[ $APPLY -eq 0 ] && echo "(dry run — re-run with --apply)"
