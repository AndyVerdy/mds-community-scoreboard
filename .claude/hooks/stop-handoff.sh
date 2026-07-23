#!/usr/bin/env bash
# Stop hook — surfaces a wrap-up reminder ONCE per session (non-blocking) so the
# docs get updated before the session ends.
# Non-blocking by design: "Stop" fires at every turn boundary, so a hard block would
# either nag after every message (block-until-fresh) or mistime to the first hand-back
# (block-once). A once-per-session systemMessage is the reliable, non-disruptive nudge;
# the SessionStart auto-load is the actual enforcer.
input=$(cat)
SID=$(printf '%s' "$input" | jq -r '.session_id // "nosession"' 2>/dev/null)
SENT="/tmp/claude-handoff-${SID}"
[ -f "$SENT" ] && exit 0
touch "$SENT"
jq -n '{systemMessage:"WRAP-UP REMINDER: before ending this session, update SESSION_LOG.md + OLIVIA_NEXT_SESSION.md + memory and run the context-handoff-git skill so the next session starts with zero drift."}'
