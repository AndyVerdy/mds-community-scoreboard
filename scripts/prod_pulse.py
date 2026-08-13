#!/usr/bin/env python3
"""Production liveness check — run BEFORE and AFTER every step of the schema rework.

The leak gate proves retrieval REFUSES what it must refuse. It does not prove Olivia
is still answering members. This does.

Everything here is READ-ONLY. It never writes a row, never sends a message, never
calls a function that writes. It is safe to run at any time, including mid-migration.

Every check is DIRECTIONAL against a saved baseline, not absolute — production
ingests continuously (content_items grew 43,877 -> 44,043 in one morning) and
already carries known-firing alarms. Absolute thresholds would be red from the
start and would teach us to ignore them. A check fails only when something got
WORSE than it was before the step.

Usage:
  python3 scripts/prod_pulse.py --save-baseline   # once, before starting a tier
  python3 scripts/prod_pulse.py                   # before and after every step
  python3 scripts/prod_pulse.py --json            # machine-readable, for CI

Exit codes:
  0  production is no worse than baseline
  1  a regression was detected — STOP, do not proceed to the next step
  2  could not run the check at all (missing key, no baseline)
"""

import argparse
import json
import os
import subprocess
import sys
import time

BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "prod_pulse_baseline.json")

# Read-only RPCs that must keep returning HTTP 200. Chosen to span the lanes the
# schema rework touches: identity, retrieval, people, events, forms.
SMOKE_RPCS = [
    ("member_card", lambda phone: {"p_phone": phone, "p_member": "Andy"}),
    ("member_count", lambda phone: {"p_phone": phone}),
    ("chapter_info", lambda phone: {"p_phone": phone}),
    ("community_info", lambda phone: {"p_phone": phone}),
    ("event_history", lambda phone: {"p_phone": phone}),
    ("expertise_search", lambda phone: {"p_phone": phone, "p_query": "PPC"}),
    ("content_search", lambda phone: {"p_phone": phone, "p_terms": ["amazon"]}),
]

# Tables whose row count must never go DOWN. A drop means data loss.
ROW_COUNT_TABLES = [
    "content_items", "member_profiles", "member_attributes", "members",
    "event_registrations", "form_responses", "wa_messages", "member_edges",
    "olivia_messages", "entity_dossier",
]

failures = []
warnings = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (f"  — {detail}" if detail else ""))
    if not ok:
        failures.append(f"{name}: {detail}")


def warn(name, detail=""):
    print(f"  WARN  {name}" + (f"  — {detail}" if detail else ""))
    warnings.append(f"{name}: {detail}")


def load_key():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_SECRET_KEY"]


def curl(method, url, key, body=None, profile_hdr=None):
    """One retry on transport failure or 5xx only — same policy as the leak gate."""
    cmd = ["curl", "-s", "-m", "45", "-w", "\n%{http_code}", "-X", method, url,
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json"]
    for h in (profile_hdr or []):
        cmd += ["-H", h]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    icode = 0
    raw = ""
    for attempt in (1, 2):
        p = subprocess.run(cmd, capture_output=True, text=True)
        raw, _, code = p.stdout.rpartition("\n")
        try:
            icode = int(code)
        except ValueError:
            icode = 0
        if 200 <= icode < 500:
            break
        if attempt == 1:
            time.sleep(2)
    try:
        return icode, json.loads(raw) if raw.strip() else None
    except (ValueError, json.JSONDecodeError):
        return icode, raw[:300]


def rpc(fn, params, key):
    return curl("POST", f"{BASE}/rpc/{fn}", key, body=params,
                profile_hdr=["Content-Profile: digest"])


def get(path, key):
    return curl("GET", f"{BASE}/{path}", key, profile_hdr=["Accept-Profile: digest"])


def count_of(table, key, where=""):
    """Exact row count via PostgREST's count header trick, using a HEAD-like select."""
    q = f"{table}?select=count" + (f"&{where}" if where else "")
    st, body = get(q, key)
    if st != 200 or not isinstance(body, list) or not body:
        return None
    return body[0].get("count")


def collect(key, phone):
    """Gather the full production state. Pure reads."""
    s = {}

    # --- is Olivia answering? ---
    # Inbound member messages older than 10 minutes that have no assistant reply after
    # them on the same phone. This is the single most important number in the file.
    st, body = rpc("prod_pulse_unanswered", {}, key)
    if st == 404:
        # helper RPC not installed — fall back to a coarser signal
        st2, rows = get("olivia_messages?role=eq.member&order=created_at.desc&limit=1"
                        "&select=created_at,phone", key)
        s["last_inbound_at"] = rows[0]["created_at"] if (st2 == 200 and rows) else None
        st3, rows3 = get("olivia_messages?role=eq.olivia&order=created_at.desc&limit=1"
                         "&select=created_at", key)
        s["last_answer_at"] = rows3[0]["created_at"] if (st3 == 200 and rows3) else None
        s["unanswered"] = None
    else:
        s["unanswered"] = body if isinstance(body, int) else None

    # --- sends actually delivering? a 200 from Meta is NOT delivery ---
    s["sends_failed_24h"] = count_of(
        "olivia_sends", key, "status=eq.failed&updated_at=gte." + iso_ago(24))
    s["sends_ok_24h"] = count_of(
        "olivia_sends", key, "status=in.(delivered,read)&updated_at=gte." + iso_ago(24))

    # --- alarms and heartbeats ---
    st, rows = get("olivia_alarm_state?is_firing=is.true&select=alarm_key", key)
    s["alarms_firing"] = sorted(r["alarm_key"] for r in rows) if st == 200 and rows else []
    st, rows = get("olivia_job_heartbeats?select=job,last_run_at", key)
    s["heartbeats"] = {r["job"]: r["last_run_at"] for r in rows} if st == 200 and rows else {}

    # --- swallowed errors (table exists only after Tier 1 Task 10) ---
    c = count_of("job_errors", key)
    s["job_errors"] = c  # None means the table does not exist yet

    # --- portal still serving ---
    s["portal_sessions_24h"] = count_of(
        "member_sessions", key, "last_seen_at=gte." + iso_ago(24))

    # --- row counts that must never drop ---
    s["rows"] = {t: count_of(t, key) for t in ROW_COUNT_TABLES}

    # --- read-only RPC smoke ---
    smoke = {}
    for fn, mk in SMOKE_RPCS:
        st, _b = rpc(fn, mk(phone), key)
        smoke[fn] = st
    s["smoke"] = smoke

    return s


def iso_ago(hours):
    import datetime as _dt
    return (_dt.datetime.now(_dt.timezone.utc)
            - _dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")


def compare(base, now):
    print("\n— is Olivia answering? —")
    if now.get("unanswered") is not None and base.get("unanswered") is not None:
        check("no new unanswered member messages",
              now["unanswered"] <= base["unanswered"],
              f"{base['unanswered']} -> {now['unanswered']}")
    else:
        if now.get("last_answer_at"):
            check("an assistant reply exists", True, f"last at {now['last_answer_at']}")
        else:
            check("an assistant reply exists", False, "none found")

    print("\n— are messages reaching members? —")
    if now["sends_failed_24h"] is not None and base["sends_failed_24h"] is not None:
        check("failed sends did not increase",
              now["sends_failed_24h"] <= base["sends_failed_24h"],
              f"{base['sends_failed_24h']} -> {now['sends_failed_24h']}")

    print("\n— alarms and jobs —")
    new_alarms = sorted(set(now["alarms_firing"]) - set(base["alarms_firing"]))
    check("no NEW alarm is firing", not new_alarms, ", ".join(new_alarms))
    if base["alarms_firing"]:
        warn("alarms already firing at baseline", ", ".join(base["alarms_firing"]))

    regressed = [j for j, t in now["heartbeats"].items()
                 if j in base["heartbeats"] and t and base["heartbeats"][j]
                 and t < base["heartbeats"][j]]
    check("no heartbeat went backwards", not regressed, ", ".join(regressed))

    print("\n— swallowed errors —")
    if now["job_errors"] is None:
        warn("digest.job_errors does not exist yet",
             "Tier 1 Task 10 creates it; until then errors are still swallowed")
    elif base["job_errors"] is None:
        check("job_errors readable", True, f"{now['job_errors']} rows (new baseline)")
    else:
        check("no new swallowed errors",
              now["job_errors"] <= base["job_errors"],
              f"{base['job_errors']} -> {now['job_errors']}")

    print("\n— portal —")
    if now["portal_sessions_24h"] is not None:
        check("portal sessions present", now["portal_sessions_24h"] > 0,
              f"{now['portal_sessions_24h']} in 24h")

    print("\n— row counts (must never drop) —")
    for t in ROW_COUNT_TABLES:
        b, n = base["rows"].get(t), now["rows"].get(t)
        if b is None or n is None:
            warn(f"{t} count unavailable")
            continue
        check(f"{t} did not lose rows", n >= b, f"{b} -> {n}")

    print("\n— read-only RPC smoke —")
    for fn, _ in SMOKE_RPCS:
        b, n = base["smoke"].get(fn), now["smoke"].get(fn)
        check(f"{fn} still responds", n == 200, f"HTTP {n} (baseline {b})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phone", default="17866578153",
                    help="a matched member phone to probe read-only RPCs as")
    ap.add_argument("--save-baseline", action="store_true",
                    help="record the current state as the comparison point")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    try:
        key = load_key()
    except (OSError, KeyError) as e:
        print(f"cannot read SUPABASE_SECRET_KEY from {ENV_PATH}: {e}", file=sys.stderr)
        return 2

    now = collect(key, args.phone)

    if args.save_baseline:
        with open(BASELINE_PATH, "w") as f:
            json.dump(now, f, indent=2, sort_keys=True)
        print(f"baseline saved to {BASELINE_PATH}")
        print(json.dumps(now, indent=2, sort_keys=True))
        return 0

    if not os.path.exists(BASELINE_PATH):
        print("no baseline — run with --save-baseline first", file=sys.stderr)
        return 2
    with open(BASELINE_PATH) as f:
        base = json.load(f)

    if args.json:
        print(json.dumps({"baseline": base, "now": now}, indent=2, sort_keys=True))
        return 0

    print("PROD PULSE — production must be no worse after this step than before it\n")
    compare(base, now)

    print()
    if failures:
        print(f"PULSE FAILED — {len(failures)} regression(s). STOP. Do not run the next step.")
        for f_ in failures:
            print(f"  - {f_}")
        return 1
    print(f"PULSE OK — production is no worse than baseline"
          + (f" ({len(warnings)} pre-existing warning(s))" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
