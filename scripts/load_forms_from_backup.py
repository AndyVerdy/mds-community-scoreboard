#!/usr/bin/env python3
"""One-off: load the 94 pruned forms into digest.form_responses FROM THE BACKUP.

Why from the backup and not the normal loader: these forms are about to be deleted from
Typeform, so adding them to sync_form_responses.FORMS would leave 94 permanent entries
that fetch nothing forever — the exact stale-config mess we just cleaned out. The backup
already holds every definition and every response, so this loads once and never again.

Row shape is produced by the loader's own build_row()/answer_value(), imported rather
than reimplemented, so these rows are byte-identical in structure to every other row.

⚠️ These forms are NOT added to digest.form_scope. Olivia's five-form wall is untouched;
this data is queryable by the warehouse and invisible to her.

  python3 scripts/load_forms_from_backup.py            # dry run
  python3 scripts/load_forms_from_backup.py --apply
"""
import importlib.util, json, os, subprocess, sys

BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "typeform_backups", "batch1to3q_2026-08-07.jsonl")
LOADER = "/Users/Born/mds-digest-web/scripts/sync_form_responses.py"
ENV = "/Users/Born/mds-digest-web/.env.local"
APPLY = "--apply" in sys.argv

spec = importlib.util.spec_from_file_location("syncforms", LOADER)
sf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sf)


def env():
    e = {}
    for line in open(ENV):
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            e[k] = v.strip().strip('"').strip("'")
    return e


def titles_from_definition(d):
    """Same composition rule as the loader's fetch_titles, but reading the stored definition."""
    titles = {}

    def walk(fields, parent=""):
        for f in fields:
            title = (f.get("title") or "").strip()
            if parent and title:
                title = f"{parent} ({title})"
            titles[f.get("ref") or f["id"]] = title
            sub = (f.get("properties") or {}).get("fields")
            if sub:
                walk(sub, title if f["type"] == "matrix" else parent)
    walk(d.get("fields") or [])
    return titles


e = env()
rows, skipped = [], 0
for line in open(BACKUP):
    rec = json.loads(line)
    fid, name = rec["id"], rec.get("title") or rec["id"]
    titles = titles_from_definition(rec.get("definition") or {})
    for item in (rec.get("responses") or {}).get("items", []):
        if not item.get("answers"):
            skipped += 1          # a walkthrough with no answers says nothing
            continue
        rows.append(sf.build_row(fid, name, item, titles))

forms = len({r["form_id"] for r in rows})
print(f"{len(rows)} rows from {forms} forms ({skipped} answerless responses skipped)")
if not APPLY:
    print("DRY RUN — pass --apply to write")
    raise SystemExit

for i in range(0, len(rows), 200):
    sf.sb(e, "POST", "form_responses?on_conflict=token",
          json.dumps(rows[i:i + 200]), "resolution=merge-duplicates,return=minimal")
print(f"upserted {len(rows)} rows")

print("stamp pass:", sf.sb(e, "POST", "rpc/stamp_form_responses", "{}").strip() or "(no output)")
