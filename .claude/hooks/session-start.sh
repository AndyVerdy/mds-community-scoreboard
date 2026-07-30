#!/usr/bin/env bash
# SessionStart hook — this folder holds MANY separate MDS projects. Surface the shared
# session log + the protocol; do NOT assume a specific project. Claude identifies the
# project from the first user message, reads THAT project's handoff, and verifies it live.
cd /Users/Born/Scorecard 2>/dev/null || exit 0
# The shared log is INDEX-ON-TOP since the 2026-07-30 split: head = preamble + one line per
# session, newest first. Full entries live in SESSION_LOG_<STREAM>.md (read the tail of the
# stream matching the session's project after identifying it).
LOG=$(head -40 SESSION_LOG.md 2>/dev/null)
CTX=$(printf 'SESSION START. This folder is a MULTI-PROJECT MDS working directory (Census, GroupOS, Application v3, Olivia, MRR, TikTok, Singapore, Member360, WA digest, Tools-health, Scorecard leaderboard, and more). Do NOT assume which project this session is about. From the first user message, identify the project, then READ that project handoff doc (e.g. OLIVIA_NEXT_SESSION.md for Olivia; CENSUS_* / GROUPOS_* / APPLICATION_V3_* etc. for those) plus its memory entry AND the head of its stream log (SESSION_LOG_OLIVIA.md / SESSION_LOG_SCORECARD.md / SESSION_LOG_MISC.md), VERIFY it against the LIVE systems that project touches (n8n / Supabase / Airtable / its gate), and fix any drift THIS session before new work. At session close: full entry to the STREAM log + ONE index line to SESSION_LOG.md. Follow the SESSION PROTOCOL at the top of CLAUDE.md. The cross-project INDEX (newest first) is below.\n\n=== SESSION_LOG.md (index head) ===\n%s\n' "$LOG")
jq -n --arg ctx "$CTX" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'
