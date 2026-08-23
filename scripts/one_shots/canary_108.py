#!/usr/bin/env python3
"""#108 probe canary — a temporary Summit registration for the probe member.

    python3 scripts/one_shots/canary_108.py add
    python3 scripts/one_shots/canary_108.py remove   # ALWAYS run this, pass or fail
"""
import importlib.util, json, subprocess, sys

EVENT = "recrATwhUDA55iQN5"          # MDS Summit Singapore (NOT the Night Out row)
ROSTER_ID = "canary-108"
PHONE = "17866578153"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/"

spec = importlib.util.spec_from_file_location("g", "scripts/olivia_leak_gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
KEY = g.load_key()


def call(method, path, body=None, prefer=None):
    cmd = ["curl", "-s", "-X", method, BASE + path,
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "apikey: " + KEY, "-H", "Authorization: Bearer " + KEY]
    if prefer:
        cmd += ["-H", "Prefer: " + prefer]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "add":
        me = json.loads(call("GET", "members?select=at_member_id&phone=eq." + PHONE))
        assert me, "probe member not found"
        row = {"roster_record_id": ROSTER_ID, "event_at_id": EVENT,
               "member_at_id": me[0]["at_member_id"], "full_name": "CANARY 108",
               "email": "canary-108@example.invalid", "ticket_status": "Confirmed", "source": "canary"}
        print(call("POST", "event_registrations", row, prefer="return=representation")[:300])
    elif action == "remove":
        call("DELETE", "event_registrations?roster_record_id=eq." + ROSTER_ID)
    print("canary rows now:",
          call("GET", "event_registrations?select=roster_record_id&roster_record_id=eq." + ROSTER_ID).strip())


if __name__ == "__main__":
    main()
