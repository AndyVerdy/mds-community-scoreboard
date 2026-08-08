#!/usr/bin/env bash
# Typeform prune, BATCH 2 — forms Andy reviewed and approved: groups F, A, B, D, E.
#
# Unlike batch 1, these forms DO have responses (1-9 each). That is deliberate and reviewed.
# Everything is safe because either:
#   * the responses are already in digest.form_responses (19 of 27), which deleting the form
#     does not touch — the loader just returns 0 for a missing form and moves on, or
#   * the form is not in our warehouse and its full definition + responses were exported to
#     typeform_backups/batch2_not_in_warehouse_2026-08-07.json first (8 of 27, 28 responses).
#
# Andy runs this, not Claude.
#
#   bash scripts/typeform_prune_batch2.sh            # DRY RUN
#   bash scripts/typeform_prune_batch2.sh --apply    # deletes
set -uo pipefail

ENV_FILE="/Users/Born/mds-digest-web/.env.local"
DIR="$(dirname "$0")"
LOG="$DIR/typeform_prune.log"
IDS_FILE="$DIR/typeform_prune_batch2_ids.txt"
BACKUP="$DIR/../typeform_backups/batch2_not_in_warehouse_2026-08-07.json"
PAT="$(grep '^CENTURION_TYPEFORM_PAT=' "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'"' ')"
[ -n "$PAT" ] || { echo "no CENTURION_TYPEFORM_PAT in $ENV_FILE"; exit 1; }

# Refuse to run at all if the backup of the not-in-warehouse forms is missing.
[ -s "$BACKUP" ] || { echo "backup missing: $BACKUP — refusing to delete"; exit 1; }

# Olivia's canonical five — never delete, whatever any list says.
NEVER="DFeK5yop FsVHzNN9 mkUJqsfM I409BFlj DXs5mhZn"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
[ $APPLY -eq 1 ] || echo "DRY RUN — nothing will be deleted. Re-run with --apply."
echo "backup present: $(wc -c < "$BACKUP" | tr -d ' ') bytes"

deleted=0; skipped=0; total=0
while read -r id title; do
  [ -z "$id" ] && continue
  total=$((total+1))
  case " $NEVER " in *" $id "*)
    echo "  SKIP  $id — Olivia canonical ($title)"; skipped=$((skipped+1)); continue;;
  esac
  if [ $APPLY -eq 0 ]; then
    echo "  would delete  $id  ($title)"; continue
  fi
  code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' -X DELETE \
           "https://api.typeform.com/forms/$id" -H "Authorization: Bearer $PAT")
  if [ "$code" = "204" ]; then
    echo "  DELETED  $id  ($title)"
    echo "$(date -u +%FT%TZ)  batch2 deleted $id  $title" >> "$LOG"
    deleted=$((deleted+1))
  else
    echo "  FAILED   $id — HTTP $code ($title)"
    echo "$(date -u +%FT%TZ)  batch2 FAILED $id http=$code  $title" >> "$LOG"
  fi
done < "$IDS_FILE"

echo
echo "$total considered · $deleted deleted · $skipped skipped"
[ $APPLY -eq 0 ] && echo "(dry run — re-run with --apply)"
