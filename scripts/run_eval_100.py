#!/usr/bin/env python3
"""Fire an organic eval bank at a target webhook and dump Q->A for scoring.

Multi-turn sequences (`seq`) fire ADJACENT with no reset between them -- correction
handling is a live defect class and cannot be tested with isolated questions.
A `new question` reset is inserted between classes so a stale intent cannot leak
across and produce a false pass.

Banks are interchangeable: `--bank <file>` runs any bank with the same schema
(`id, class, q, expect, soft, asker, first_asked, seq, regression, retired`).

Usage:
  python3 scripts/run_eval_100.py --staging                              # bank A (100), candidate build
  python3 scripts/run_eval_100.py                                        # bank A, prod
  python3 scripts/run_eval_100.py --bank eval_bank_B_2026-08-23.json --staging
  python3 scripts/run_eval_100.py --bank eval_bank_B_2026-08-23.json --dry-run
"""
import argparse
import json
import subprocess
import sys

BANK = "eval_bank_100_2026-08-16.json"   # default: the frozen 100-question bank (2026-07-19..08-16)


def build_sequence(bank=BANK):
    qs = json.load(open(bank))["questions"]
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
    ap.add_argument("--bank", default=BANK,
                    help=f"bank file to run (default: {BANK})")
    args = ap.parse_args()

    seq, qs = build_sequence(args.bank)
    meta = json.load(open(args.bank)).get("meta") or {}
    resets = sum(1 for s in seq if s in ("reset", "new question"))
    print(f"bank: {args.bank}" + (f" ({meta['name']}, {meta.get('window','')})" if meta.get("name") else ""))
    print(f"{len(qs)} questions + {resets} resets = {len(seq)} turns")
    print(f"target: {'STAGING' if args.staging else 'PROD'}")
    if args.dry_run:
        for i, s in enumerate(seq):
            print(f"  {i:3} {s.replace(chr(10), ' / ')[:90]}")
        return 0

    cmd = [sys.executable, "scripts/olivia_selftest.py"]
    if args.staging:
        cmd.append("--staging")
    cmd += ["--questions"] + seq
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
