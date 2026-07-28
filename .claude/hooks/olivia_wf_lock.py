#!/usr/bin/env python3
"""PreToolUse hook — ONE editing session at a time on the LIVE Olivia workflow.

Backlog #4: two sessions have already overwritten each other on 12wj6h1TWqb0d4Dq,
and one bad edit killed every inbound for eight minutes. Remembering the rule did
not work, so it is enforced here — any n8n WRITE touching the live workflow is
blocked unless THIS session holds the lock taken with scripts/olivia_wf.py.

Reads are never blocked. The staging copy (a different workflow id) is never
blocked — that is the whole point of having it.

exit 0 = allow · exit 2 = block, with the reason on stderr.
"""
import json
import os
import sys
from datetime import datetime, timezone

REPO = "/Users/Born/Scorecard"
LOCK = os.path.join(REPO, ".olivia_wf.lock")
PROD_ID = "12wj6h1TWqb0d4Dq"

READ_ONLY_TOOLS = {
    "mcp__n8n-mcp__n8n_get_workflow",
    "mcp__n8n-mcp__n8n_list_workflows",
    "mcp__n8n-mcp__n8n_validate_workflow",
    "mcp__n8n-mcp__validate_workflow",
    "mcp__n8n-mcp__n8n_executions",
    "mcp__n8n-mcp__n8n_health_check",
    "mcp__n8n-mcp__get_node",
    "mcp__n8n-mcp__search_nodes",
    "mcp__n8n-mcp__tools_documentation",
}

HOWTO = """
The path is staging-first:
  python3 scripts/olivia_wf.py lock --reason "<what you are changing>"
  python3 scripts/olivia_wf.py stage         # prod -> test copy
  ...edit the STAGING workflow, fire probes at it...
  python3 scripts/olivia_selftest.py --staging --questions "reset" "<q>"
  python3 scripts/olivia_wf.py promote       # gate + snapshot + bounce

Emergency:  python3 scripts/olivia_wf.py rollback <snapshot>
"""


def deny(reason):
    sys.stderr.write(f"BLOCKED: write to the LIVE Olivia workflow ({PROD_ID}).\n{reason}\n{HOWTO}")
    sys.exit(2)


def is_write(tool, blob):
    if tool in READ_ONLY_TOOLS:
        return False
    if tool == "mcp__n8n-mcp__n8n_workflow_versions":
        return '"mode": "list"' not in blob and '"mode": "get"' not in blob
    if tool.startswith("mcp__n8n-mcp__"):
        return True
    if tool == "Bash":
        # raw curl straight at the n8n API, bypassing scripts/olivia_wf.py
        low = blob.lower()
        return "curl" in low and "n8n" in low and any(
            v in blob for v in ("-X PUT", "-X POST", "-X DELETE", "--request PUT"))
    return False


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)                       # never break the harness on a parse miss
    tool = event.get("tool_name", "")
    session = event.get("session_id", "")
    blob = json.dumps(event.get("tool_input", {}), indent=1)

    if PROD_ID not in blob:
        sys.exit(0)
    if not is_write(tool, blob):
        sys.exit(0)

    if not os.path.exists(LOCK):
        deny("No editing lock is held.")
    try:
        lock = json.load(open(LOCK))
        expired = datetime.now(timezone.utc) > datetime.fromisoformat(lock["expires_at"])
    except Exception as exc:
        deny(f"Lock file unreadable ({exc}).")
    if expired:
        deny("The lock has expired — take it again.")
    holder = lock.get("holder", "?")
    if not lock.get("session"):
        deny(f"The lock is held by {holder} outside this session "
             f"(reason: {lock.get('reason')}).")
    if lock["session"] != session:
        deny(f"The lock is held by another session — {holder}, "
             f"session {lock['session'][:8]} (reason: {lock.get('reason')}).")
    sys.exit(0)


if __name__ == "__main__":
    main()
