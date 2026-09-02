#!/usr/bin/env python3
"""Merge a --ids re-run into the main bench JSON (rows replaced by id), then delete the subset file.

  python3 bench_merge_rows.py MAIN.json SUBSET.json
Rows in SUBSET whose answer is still a loop error are NOT merged (the original error row stays).
"""
import json, os, sys
main_f, sub_f = sys.argv[1], sys.argv[2]
main, sub = json.load(open(main_f)), json.load(open(sub_f))
assert main["tag"] == sub["tag"], (main["tag"], sub["tag"])
by_id = {r["id"]: r for r in main["rows"]}
merged, kept = [], []
for r in sub["rows"]:
    if r["answer"].startswith("["):
        kept.append(r["id"]); continue
    by_id[r["id"]] = r; merged.append(r["id"])
main["rows"] = [by_id[r["id"]] for r in main["rows"]]
main.setdefault("merged_reruns", []).append({"from": os.path.basename(sub_f), "ids": merged, "still_error": kept})
json.dump(main, open(main_f, "w"), indent=1)
os.remove(sub_f); md = sub_f[:-5] + ".md"
if os.path.exists(md): os.remove(md)
print(f"merged {merged} into {os.path.basename(main_f)}; still error: {kept}; subset files removed")
