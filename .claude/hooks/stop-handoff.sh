#!/usr/bin/env bash
# Stop hook — once-per-session wrap-up reminder (non-blocking), generic across every
# project in this folder. Fires once per session (sentinel keyed to session_id).
input=$(cat)
SID=$(printf '%s' "$input" | jq -r '.session_id // "nosession"' 2>/dev/null)
SENT="/tmp/claude-handoff-${SID}"
[ -f "$SENT" ] && exit 0
touch "$SENT"
jq -n '{systemMessage:"WRAP-UP REMINDER: before ending, update the docs for whatever project you worked on this session — prepend a dated entry to SESSION_LOG.md, refresh that project handoff doc, update memory, and (decisions only) its ClickUp doc. See the SESSION PROTOCOL at the top of CLAUDE.md."}'
