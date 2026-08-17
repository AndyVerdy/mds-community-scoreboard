#!/usr/bin/env python3
"""Fire the 100-question bank at a target webhook and dump Q->A for scoring.

Multi-turn sequences (`seq`) fire ADJACENT with no reset between them -- correction
handling is a live defect class and cannot be tested with isolated questions.
A `new question` reset is inserted between classes so a stale intent cannot leak
across and produce a false pass.

Usage:
  python3 scripts/run_eval_100.py --staging          # the candidate build
  python3 scripts/run_eval_100.py                    # prod
"""
import argparse
import json
import subprocess
import sys

BANK = "eval_bank_100_2026-08-16.json"


def build_sequence():
    qs = json.load(open(BANK))["questions"]
    out, last_class, last_seq = ["reset"], None, None
    for q in qs:
        same_seq = q.get("seq") and q["seq"] == last_seq
        if q["class"] != last_class and not same_seq:
            out.append("new question")
        out.append(q["q"])
        last_class, last_seq = q["class"], q.get("seq")
    return out, qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    seq, qs = build_sequence()
    resets = sum(1 for s in seq if s in ("reset", "new question"))
    print(f"{len(qs)} questions + {resets} resets = {len(seq)} turns")
    print(f"target: {'STAGING' if args.staging else 'PROD'}")
    if args.dry_run:
        for i, s in enumerate(seq):
            print(f"  {i:3} {s[:90]}")
        return 0

    cmd = [sys.executable, "scripts/olivia_selftest.py"]
    if args.staging:
        cmd.append("--staging")
    cmd += ["--questions"] + seq
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
