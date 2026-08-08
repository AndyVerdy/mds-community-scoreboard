#!/usr/bin/env python3
"""Back up a list of Typeform forms (definition + all responses) before deletion.

Writes INCREMENTALLY, one form per line of JSONL, so a stall loses at most one form
instead of the whole run — the first attempt at this died at 10 minutes with nothing
on disk because it dumped only at the end.

  python3 scripts/typeform_backup_batch.py <ids_file> <out.jsonl>

Resumable: forms already present in out.jsonl are skipped.
"""
import json, os, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
ids_file, out_path = sys.argv[1], sys.argv[2]

PAT = None
for line in open(ENV):
    if line.startswith("CENTURION_TYPEFORM_PAT="):
        PAT = line.split("=", 1)[1].strip().strip('"').strip("'")
if not PAT:
    sys.exit("missing CENTURION_TYPEFORM_PAT")


def api(path):
    p = subprocess.run(["curl", "-sS", "-m", "45", f"https://api.typeform.com{path}",
                        "-H", f"Authorization: Bearer {PAT}"], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except (ValueError, json.JSONDecodeError):
        return {"_error": p.stdout[:200]}


done = set()
if os.path.exists(out_path):
    for line in open(out_path):
        try:
            done.add(json.loads(line)["id"])
        except Exception:
            pass

ids = [l.split()[0] for l in open(ids_file) if l.strip() and not l.startswith("#")]
todo = [i for i in ids if i not in done]
print(f"{len(ids)} forms · {len(done)} already backed up · {len(todo)} to go", flush=True)

with open(out_path, "a") as f:
    for n, i in enumerate(todo, 1):
        rec = {"id": i,
               "definition": api(f"/forms/{i}"),
               "responses": api(f"/forms/{i}/responses?page_size=1000")}
        f.write(json.dumps(rec) + "\n")
        f.flush()
        print(f"  [{n}/{len(todo)}] {i} · {len(rec['responses'].get('items', []))} responses", flush=True)

print(f"done — {out_path} ({os.path.getsize(out_path)} bytes)", flush=True)
