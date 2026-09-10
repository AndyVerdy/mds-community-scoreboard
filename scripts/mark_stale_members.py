#!/usr/bin/env python3
"""#148 — mark the Airtable mirror rows that stopped coming back.

`digest.members` only ever adds and updates, so a record Airtable stops returning just sits
there saying whatever it last said. Eleven rows were frozen from 2026-08-05 to 2026-09-10,
thirty-six days, and nothing anywhere said so. They then came back on their own, which is the
real shape of this: rows go absent intermittently, not permanently.

Marked, never deleted. A row that vanishes because of ONE bad Airtable call must not be
removed — deleting a member is the one thing that cannot be undone from here. The guard lives
in digest.mark_stale_members(): it only marks when the sync wave looks healthy, judged as a
share of the table so it keeps working as the roster grows.

Run by nightly_derivations.py. Manual: python3 this.
"""
import json
import subprocess
import sys

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"


def key():
    for line in open(ENV_PATH):
        if line.startswith("SUPABASE_SECRET_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"no SUPABASE_SECRET_KEY in {ENV_PATH}")


def main():
    k = key()
    r = subprocess.run(
        ["curl", "-s", "--max-time", "60", "-X", "POST", f"{BASE}/rpc/mark_stale_members",
         "-H", f"apikey: {k}", "-H", f"Authorization: Bearer {k}",
         "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
         "--data-binary", "@-"],
        input="{}", capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"curl exit {r.returncode}")
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"non-JSON: {r.stdout[:200]}")

    # An unhealthy wave is not an error — it is the guard doing its job, and saying so.
    if out.get("ok") is False:
        print(f"skipped: {out.get('skipped')} (fresh share {out.get('fresh_share')} "
              f"< {out.get('required')}) · cleared {out.get('cleared', 0)}")
        return 0

    print(f"marked {out.get('marked', 0)} · cleared {out.get('cleared', 0)} · "
          f"stale now {out.get('stale_total', 0)} · fresh share {out.get('fresh_share')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
