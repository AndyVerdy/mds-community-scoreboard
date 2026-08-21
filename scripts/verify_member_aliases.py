#!/usr/bin/env python3
"""#100 — verify the identity alias layer.

Asserts what #100 promised: the alias table exists, all three evidenced rungs loaded,
the two cases that must resolve with no human approval do resolve (Ryan Bastuba via a
Stripe payment record, Michael Corrigan via the admin field), the resolver is the single
entry point and folds case and whitespace, an unknown address returns nothing, and a bare
name match can never become a grant.

Run:  python3 scripts/verify_member_aliases.py      # exit 0 = all PASS, exit 1 = any FAIL
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def get(path):
    cmd = ["curl", "-s", "-m", "120", f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"GET {path} failed: {out[:300]}")


class Err:
    """A distinct object per failed call.

    PostgREST returns an error as a dict. Two failed calls return EQUAL dicts, so a
    check like `alias_hit == pref_hit` would PASS while the function is missing —
    a test that goes green when the thing is broken. Every Err is unique, so any
    comparison against it is False and the check fails honestly.
    """

    def __init__(self, payload):
        self.payload = payload

    def __repr__(self):
        return f"ERR({str(self.payload)[:90]})"


def rpc(fn, body):
    cmd = ["curl", "-s", "-m", "60", "-X", "POST", f"{BASE}/rpc/{fn}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Content-Profile: digest", "-H", "Content-Type: application/json",
           "--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        val = json.loads(out)
    except Exception:
        return Err(out[:300])
    if isinstance(val, dict) and "code" in val and "message" in val:
        return Err(val)
    return val


def page_all(table, select, cap=40000):
    rows, offset = [], 0
    while offset < cap:
        page = get(f"{table}?select={select}&order=email&limit=1000&offset={offset}")
        if not isinstance(page, list) or not page:
            return rows
        rows += page
        if len(page) < 1000:
            return rows
        offset += 1000
    return rows


results, fails = [], []


def check(name, ok, detail):
    results.append(name)
    if not ok:
        fails.append(name)
    print(f"{name:<28} {'PASS' if ok else 'FAIL':<6} {detail}")


# --- Task 1: the table exists -------------------------------------------------
probe = get("member_email_alias?select=at_member_id&limit=1")
check("table exists", isinstance(probe, list), f"got {type(probe).__name__}")
if fails:
    print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
    sys.exit(1)

# --- Task 2: the three evidenced rungs ---------------------------------------
alias = page_all("member_email_alias", "at_member_id,email,source")
by_source = {}
for r in alias:
    by_source[r["source"]] = by_source.get(r["source"], 0) + 1

check("preferred rung loaded", by_source.get("preferred", 0) >= 5700,
      f"{by_source.get('preferred', 0)} rows")
check("stripe rung loaded", by_source.get("stripe", 0) >= 10,
      f"{by_source.get('stripe', 0)} rows")
check("admin_field rung loaded", by_source.get("admin_field", 0) >= 8,
      f"{by_source.get('admin_field', 0)} rows")

ryan = get("member_email_alias?select=at_member_id,source&email=eq.ryan@bastuba.com")
check("stripe alias, no approval",
      len(ryan) == 1 and ryan[0]["source"] == "stripe", f"{ryan}")

mc = get("member_email_alias?select=at_member_id,source&email=eq.michael@trtl.co.uk")
check("admin alias, no approval",
      len(mc) == 1 and mc[0]["source"] == "admin_field", f"{mc}")

check("no bare name grants",
      all(r["source"] != "name_match" for r in alias),
      "source vocabulary excludes unapproved name matches")

# --- Task 3: the resolver -----------------------------------------------------
andy = rpc("resolve_member_by_email", {"p_email": "andy.verdy1@gmail.com"})
check("resolver: preferred", andy == "recCUUw8iiUnJjac1", f"{andy}")

alias_hit = rpc("resolve_member_by_email", {"p_email": "ryan@bastuba.com"})
pref_hit = rpc("resolve_member_by_email", {"p_email": "ryan@varify.com"})
check("resolver: alias == preferred",
      alias_hit is not None and alias_hit == pref_hit,
      f"alias={alias_hit} preferred={pref_hit}")

check("resolver: case/space fold",
      rpc("resolve_member_by_email", {"p_email": "  Ryan@Bastuba.com "}) == alias_hit,
      "mixed case + padding")

check("resolver: unknown is null",
      rpc("resolve_member_by_email", {"p_email": "nobody@example.invalid"}) is None,
      "unknown address")

print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
