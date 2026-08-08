#!/usr/bin/env bash
# Typeform prune, BATCH 1-3Q — the 94 forms that ask 1-3 questions.
# Verdict measured, not assumed: 6,622 responses, 1,871 tied to a member but none mapping to a concept (ballots, opt-ins, superseded application starts). The 29 forms that DO carry concepts produce 0 member_fact rows - session surveys identify nobody. Keeps BKg5wDeY, j5JAS5sT, IaKWKysS via the never-delete list.
#
# Andy runs this, not Claude.
#
#   bash scripts/typeform_prune_batch1to3q.sh            # DRY RUN
#   bash scripts/typeform_prune_batch1to3q.sh --apply    # deletes
#
# Guards, learned the hard way on 2026-08-07 when batch 1 deleted two staged approval
# gates that had zero responses:
#   1. scripts/typeform_never_delete.txt is a HARD skip list, checked per form.
#   2. Any form whose title matches verif|approval|gate is skipped, listed or not.
#   3. Refuses to start unless the backup of all 62 forms is present.
set -uo pipefail

ENV_FILE="/Users/Born/mds-digest-web/.env.local"
DIR="$(dirname "$0")"
LOG="$DIR/typeform_prune.log"
IDS_FILE="$DIR/typeform_prune_batch1to3q_ids.txt"
NEVER_FILE="$DIR/typeform_never_delete.txt"
BACKUP="$DIR/../typeform_backups/batch1to3q_2026-08-07.jsonl"
PAT="$(grep '^CENTURION_TYPEFORM_PAT=' "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'"' ')"
[ -n "$PAT" ] || { echo "no CENTURION_TYPEFORM_PAT in $ENV_FILE"; exit 1; }
[ -s "$BACKUP" ] || { echo "backup missing: $BACKUP — refusing to delete"; exit 1; }
[ -s "$NEVER_FILE" ] || { echo "never-delete list missing: $NEVER_FILE — refusing"; exit 1; }

NEVER="$(grep -v '^#' "$NEVER_FILE" | awk 'NF{print $1}' | tr '\n' ' ')"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
[ $APPLY -eq 1 ] || echo "DRY RUN — nothing will be deleted. Re-run with --apply."
echo "backup: $(wc -c < "$BACKUP" | tr -d ' ') bytes · protected ids: $(echo "$NEVER" | wc -w | tr -d ' ')"

deleted=0; skipped=0; total=0
while read -r id title; do
  [ -z "$id" ] && continue
  total=$((total+1))

  case " $NEVER " in *" $id "*)
    echo "  SKIP  $id — on the never-delete list ($title)"; skipped=$((skipped+1)); continue;;
  esac
  if printf '%s' "$title" | grep -qiE 'verif|approval|gate'; then
    echo "  SKIP  $id — title looks like an approval gate ($title)"; skipped=$((skipped+1)); continue
  fi

  if [ $APPLY -eq 0 ]; then
    echo "  would delete  $id  ($title)"; continue
  fi

  code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' -X DELETE \
           "https://api.typeform.com/forms/$id" -H "Authorization: Bearer $PAT")
  if [ "$code" = "204" ]; then
    echo "  DELETED  $id  ($title)"
    echo "$(date -u +%FT%TZ)  batch1to3q deleted $id  $title" >> "$LOG"
    deleted=$((deleted+1))
  else
    echo "  FAILED   $id — HTTP $code ($title)"
    echo "$(date -u +%FT%TZ)  batch1to3q FAILED $id http=$code  $title" >> "$LOG"
  fi
done < "$IDS_FILE"

echo
echo "$total considered · $deleted deleted · $skipped skipped"
[ $APPLY -eq 0 ] && echo "(dry run — re-run with --apply)"
