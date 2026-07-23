#!/usr/bin/env bash
# SessionStart hook — injects the Olivia handoff into context so it is ALWAYS read
# at the start of a session, and forces a live drift-check before trusting the docs.
cd /Users/Born/Scorecard 2>/dev/null || exit 0
NEXT=$(cat OLIVIA_NEXT_SESSION.md 2>/dev/null)
LOG=$(tail -40 SESSION_LOG.md 2>/dev/null)
CTX=$(printf 'SESSION START — read this handoff BEFORE doing anything. Then VERIFY against LIVE systems (n8n / Supabase / the leak gate), never the docs alone, and drift-check the docs against live + fix any drift THIS session.\n\n=== OLIVIA_NEXT_SESSION.md ===\n%s\n\n=== SESSION_LOG.md (tail 40) ===\n%s\n' "$NEXT" "$LOG")
jq -n --arg ctx "$CTX" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'
