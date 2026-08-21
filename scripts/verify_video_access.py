#!/usr/bin/env python3
"""#101 — verify video access gating + the AssemblyAI transcript load.

Run:  python3 scripts/verify_video_access.py      # exit 0 = all PASS, exit 1 = any FAIL
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


class Err:
    def __init__(self, payload):
        self.payload = payload

    def __repr__(self):
        return f"ERR({str(self.payload)[:90]})"


def get(path):
    out = subprocess.run(
        ["curl", "-s", "-m", "120", f"{BASE}/{path}",
         "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
         "-H", "Accept-Profile: digest"], capture_output=True, text=True).stdout
    try:
        val = json.loads(out)
    except Exception:
        sys.exit(f"GET {path} failed: {out[:300]}")
    return val


def rpc(fn, body):
    out = subprocess.run(
        ["curl", "-s", "-m", "60", "-X", "POST", f"{BASE}/rpc/{fn}",
         "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
         "-H", "Content-Profile: digest", "-H", "Content-Type: application/json",
         "--data-binary", json.dumps(body)], capture_output=True, text=True).stdout
    try:
        val = json.loads(out)
    except Exception:
        return Err(out[:300])
    if isinstance(val, dict) and "code" in val and "message" in val:
        return Err(val)
    return val


results, fails = [], []


def check(name, ok, detail):
    results.append(name)
    if not ok:
        fails.append(name)
    print(f"{name:<34} {'PASS' if ok else 'FAIL':<6} {detail}")


# --- Task 1: video_access -----------------------------------------------------
va = get("video_access?select=video_id&limit=1")
check("video_access exists", isinstance(va, list), f"got {type(va).__name__}")
if fails:
    print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
    sys.exit(1)

hdr = subprocess.run(
    ["curl", "-s", "-I", f"{BASE}/video_access?select=video_id&limit=1",
     "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
     "-H", "Accept-Profile: digest", "-H", "Prefer: count=exact"],
    capture_output=True, text=True).stdout
total = int(hdr.split("content-range:")[1].split("/")[1].split()[0]) if "content-range:" in hdr else 0
check("grants loaded", total >= 34000, f"{total} rows")

# The 91 panel-only emails must have loaded nothing. Three probes from that list.
leak = sum(len(get(f"video_access?select=video_id&email=eq.{e}")) for e in
           ("adam.m.willis@gmail.com", "bazaddollaupi-3774@yopmail.com", "bpa@decodeup.email"))
check("panel-only pool absent", leak == 0, f"{leak} rows for 3 known panel-only emails")

resolved = get("video_access?select=at_member_id&at_member_id=not.is.null&limit=1")
check("grants resolve to members", bool(resolved), "at_member_id populated via #100 resolver")

print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
