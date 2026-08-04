#!/usr/bin/env python3
"""#50: refresh the entity dossiers (video/partner/event/chapter) — one RPC, set-based.

Runs inside nightly_derivations.py as the 'entity_dossiers' job. Exit 1 on any
failure so the heartbeat alarm fires. No-op friendly: the function only rewrites
rows whose profile/reception actually changed.
"""
import json, subprocess, sys

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"


def key():
    for l in open(ENV_PATH):
        if l.startswith("SUPABASE_SECRET_KEY="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("missing SUPABASE_SECRET_KEY")


k = key()
p = subprocess.run(["curl", "-sS", "-X", "POST", f"{BASE}/rpc/refresh_entity_dossiers",
                    "-H", f"apikey: {k}", "-H", f"Authorization: Bearer {k}",
                    "-H", "Content-Type: application/json",
                    "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
                    "-d", "{}", "--max-time", "300"],
                   capture_output=True, text=True)
try:
    rows = json.loads(p.stdout)
    assert isinstance(rows, list) and len(rows) == 4, p.stdout[:300]
except Exception as e:
    print(f"FAIL: {e} :: {p.stdout[:300]}")
    sys.exit(1)
print("entity dossiers refreshed:", ", ".join(f"{r['o_kind']}={r['o_rows']}" for r in rows))
