#!/usr/bin/env python3
"""Refresh Members-DB 'WhatsApp Chats (tags)' from 'WhatsApp Chats (live)'.

WHY THIS EXISTS: 'WhatsApp Chats (live)' is a LOOKUP, so it renders as text and can never show
badges — a lookup inherits its source type, and the source (`channels_present`) lives in a synced
mirror whose fields are locked. Badges therefore need a real multipleSelects field, and this job
keeps that copy honest.

⚠️ THE RAW DATA IS NEVER TOUCHED. This job reads and writes ONE base — the Members DB
(appou5JVr0WIrioWS). It never opens the WA DB (appT9TVZWhv7io4CN), never reads or writes
`channels_present`, and never touches the synced mirror or the matcher's links. Its only write is
the tags field on the same record it read the lookup from.

NOT the matcher's job: `4B79OVfyT2a9a3Xt` writes the member record only when MATCH STATE changes
(delta detection), so it would miss a member who stays matched but joins a new chat — which is the
common case. Hence a separate pass.

The lookup stays the truth; this copy is as fresh as the last run. Values not in the field's
option list are SKIPPED and reported, never invented — a new chat needs its option added first.

  python3 scripts/members_chat_tags_sync.py            # dry run, prints the delta
  python3 scripts/members_chat_tags_sync.py --apply
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.parse
from collections import Counter

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE = "appou5JVr0WIrioWS"          # Members DB — the ONLY base this job touches
TABLE = "tblfwOSROSHfuYUxv"
SRC = "WhatsApp Chats (live)"        # lookup (read-only here)
DST = "WhatsApp Chats (tags)"        # multipleSelects (the only thing written)


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("missing " + k)


def curl(args, tries=4):
    for attempt in range(tries):
        r = subprocess.run(["curl", "-sS", "--max-time", "120"] + args,
                           capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(1 + attempt)
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    pat = env("AIRTABLE_PAT")

    meta = curl([f"https://api.airtable.com/v0/meta/bases/{BASE}/tables",
                 "-H", "Authorization: Bearer " + pat])
    opts = set()
    for t in meta.get("tables", []):
        if t["id"] == TABLE:
            for f in t["fields"]:
                if f["name"] == DST:
                    opts = {c["name"] for c in f["options"]["choices"]}
    if not opts:
        sys.exit("field %r not found — create it before running this" % DST)

    rows, off = [], None
    while True:
        q = "&".join("fields%5B%5D=" + urllib.parse.quote(f) for f in (SRC, DST))
        u = f"https://api.airtable.com/v0/{BASE}/{TABLE}?pageSize=100&" + q
        if off:
            u += "&offset=" + urllib.parse.quote(off)
        d = curl([u, "-H", "Authorization: Bearer " + pat])
        rows += d.get("records", [])
        off = d.get("offset")
        if not off:
            break
        time.sleep(0.22)

    def live(f):
        v = f.get(SRC)
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        return sorted({x.strip() for x in (v or "").split(",") if x.strip()})

    unknown, ops = Counter(), []
    for r in rows:
        f = r.get("fields") or {}
        want = live(f)
        for w in want:
            if w not in opts:
                unknown[w] += 1
        want = [w for w in want if w in opts]
        if want != sorted(f.get(DST) or []):
            ops.append((r["id"], want))

    print("members scanned : %d" % len(rows))
    print("needing a write : %d" % len(ops))
    if unknown:
        print("⚠ chats with no matching option (SKIPPED — add the option first): %s" % dict(unknown))
    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return
    if not ops:
        print("already in sync — no writes")
        return

    done = 0
    for i in range(0, len(ops), 10):
        chunk = ops[i:i + 10]
        body = {"records": [{"id": rid, "fields": {DST: val}} for rid, val in chunk],
                "typecast": False}
        d = curl(["-X", "PATCH", f"https://api.airtable.com/v0/{BASE}/{TABLE}",
                  "-H", "Authorization: Bearer " + pat,
                  "-H", "Content-Type: application/json", "--data-binary", json.dumps(body)])
        if "records" in d:
            done += len(d["records"])
        else:
            print("  FAILED batch at %s: %s" % (chunk[0][0], str(d)[:180]))
            break
        time.sleep(0.3)          # Airtable caps at 5 req/s per base
    print("written: %d" % done)


if __name__ == "__main__":
    main()
