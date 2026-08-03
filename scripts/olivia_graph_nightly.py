#!/usr/bin/env python3
"""#44 — nightly full recompute of the expertise ledger + knowledge graph.

Full rebuild each night (10-16s total measured): backfill and updates are the same code,
so coverage can never rot into a one-time event. Error-shaped JSON exits 1 (the #46 lesson)
so the heartbeat goes stale-with-error and the #13 alarm pages. Python 3.9-safe.
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"


def env():
    v = {}
    for line in open(ENV):
        if "=" in line and not line.startswith("#"):
            k, val = line.strip().split("=", 1)
            v[k.strip()] = val.strip().strip('"').strip("'")
    return v


def rpc(fn, key):
    r = subprocess.run(["curl", "-sS", "-m", "290", "-X", "POST", BASE + "/rpc/" + fn,
                        "-H", "apikey: " + key, "-H", "Authorization: Bearer " + key,
                        "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
                        "-H", "Content-Type: application/json", "-d", "{}"],
                       capture_output=True, text=True)
    try:
        out = json.loads(r.stdout)
    except Exception:
        print(fn + " failed (non-JSON): " + r.stdout[:200])
        sys.exit(1)
    if not isinstance(out, dict) or "code" in out:
        print(fn + " errored: " + r.stdout[:200])
        sys.exit(1)
    return out


def main():
    key = env()["SUPABASE_SECRET_KEY"]
    a = rpc("derive_member_expertise", key)
    b = rpc("derive_knowledge_graph", key)
    print("done — ledger " + str(a.get("rows")) + " rows / " + str(a.get("members"))
          + " members · graph " + str(b.get("edges")) + " edges")


if __name__ == "__main__":
    main()
