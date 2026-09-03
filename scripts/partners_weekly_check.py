#!/usr/bin/env python3
"""#17 — weekly check for NEW and CHANGED GroupOS partners.

Sibling of videos_weekly_check.py, and it exists for the same reason: the GroupOS MCP only runs
inside a Claude session, so a scheduled session dumps the listing to a file and this script does
everything headless — diff, upsert, stamp the heartbeat.

Two things this fixes, both found 2026-08-09:
  * There was no partners script at all. Partners were refreshed by hand in-session, and
    `partners_refresh` was last stamped 2026-08-01, so the alarm had been firing for nine days
    with no way to clear it even after a good refresh.
  * The row shape comes from ingest_partners.map_partner — IMPORTED, not reimplemented. A
    hand-rolled mapper wrote the API's raw HTML into description_text, where the warehouse holds
    cleaned text; that made 46 partners look "changed" on every run and would have pushed
    `<p><strong>` markup into search_tsv and the #26 re-embed trigger.

  python3 scripts/partners_weekly_check.py <dump.json>            # report only
  python3 scripts/partners_weekly_check.py <dump.json> --apply    # upsert + stamp
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, "/Users/Born/mds-digest-web/scripts")
from zoom_backfill import ENV_SB, env, sb            # noqa: E402
from ingest_partners import map_partner              # noqa: E402  (single source of the row shape)

JOB = "partners_refresh"
MAX_AGE_HOURS = 192          # weekly cadence + buffer; matches the row the alarm reads

# Fields whose change actually matters downstream. The counters (rating, reviews, claims, page
# views) tick constantly and are excluded on purpose: #26's trigger NULLS the vector on text change and
# the re-embed step below rebuilds it, so treating a view count as a content change would re-embed
# the catalog every week for nothing.
WATCH = ("name", "description_text", "offer_value", "status", "access_restriction",
         "featured", "fresh_deal")


def norm_text(v):
    """Whitespace-insensitive form, for COMPARISON only.

    The warehouse text was cleaned by an earlier html_to_text; the current one keeps NBSP and
    empty paragraphs, so 29 partners diffed on '\\n\\n\\xa0\\n\\n' versus ' ' — 97.4% identical,
    zero semantic change. Without this, every weekly run would report them as changed and the
    #26 trigger would wipe + re-embed the catalog for whitespace. Fixing the shared cleaner in
    mds-digest-web is the real repair (#17); this stops the false positives meanwhile.
    """
    if not isinstance(v, str):
        return v
    return " ".join(v.replace("\xa0", " ").split())


def heartbeat(key, status, detail):
    """Stamp digest.olivia_job_heartbeats on EVERY completed run, moved or not."""
    row = {"job": JOB, "last_run_at": "now()", "status": status,
           "detail": detail[:500], "max_age_hours": MAX_AGE_HOURS}
    # Only stamp success — sending the key on a failure would overwrite "when did this last
    # work" at the exact moment you need it. Same rule as zoom_weekly.py.
    if status == "ok":
        row["last_success_at"] = "now()"
    sb("POST", "olivia_job_heartbeats?on_conflict=job", key, [row],
       "resolution=merge-duplicates,return=minimal")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    apply = "--apply" in sys.argv
    e = env(ENV_SB)
    key = e["SUPABASE_SECRET_KEY"]

    dump = json.load(open(sys.argv[1])).get("items", [])
    if not dump:
        heartbeat(key, "error", "dump held 0 partners")
        sys.exit("dump held 0 partners — refusing to diff against an empty listing")

    rows, skipped = [], []
    for p in dump:
        row, reason = map_partner(p)
        (rows.append(row) if row else skipped.append(reason))

    have, off = {}, 0
    while True:
        page = sb("GET", f"partners_catalog?select=*&limit=1000&offset={off}", key)
        if not page:
            break
        have.update({r["partner_id"]: r for r in page})
        if len(page) < 1000:
            break
        off += 1000

    new = [r for r in rows if r["partner_id"] not in have]
    changed = []
    for r in rows:
        old = have.get(r["partner_id"])
        if not old:
            continue
        diff = [f for f in WATCH
                if norm_text(old.get(f) or None) != norm_text(r.get(f) or None)]
        if diff:
            changed.append((r, diff))

    print(f"dump {len(dump)} · mapped {len(rows)} · skipped {len(skipped)} "
          f"· warehouse {len(have)} · NEW {len(new)} · CHANGED {len(changed)}")
    for r in new:
        print(f"   + {r['partner_id']} {r['name'][:48]}")
    for r, diff in changed:
        print(f"   ~ {r['partner_id']} {r['name'][:48]} — {', '.join(diff)}")

    if not apply:
        print("REPORT ONLY — pass --apply to upsert and stamp")
        return 0
    if not (new or changed):
        heartbeat(key, "ok", f"checked {len(rows)} partners, nothing moved")
        print("nothing moved (heartbeat stamped)")
        return 0

    touched = new + [r for r, _ in changed]
    for i in range(0, len(touched), 100):
        sb("POST", "partners_catalog?on_conflict=partner_id", key, touched[i:i + 100],
           "resolution=merge-duplicates,return=minimal")
    print(f"  upserted: {len(touched)}")
    # #159: a NEW row has no vector and a CHANGED row just lost its (the #26 trigger nulls it on text
    # change). Nothing else rebuilds partner vectors — the nightly embed_content step covers
    # content_items only — so the meaning-search lane could not see 75 partners on 2026-09-03.
    # Same pass, same script the nightly chain runs (nulls-only, resumable).
    emb = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "embed_partners_events.py")],
                         capture_output=True, text=True)
    print(emb.stdout.strip()[-400:])
    if emb.returncode != 0:
        heartbeat(key, "error", f"{len(touched)} upserted but re-embed failed: {emb.stderr.strip()[-200:]}")
        print("RE-EMBED FAILED:", emb.stderr.strip()[-400:])
        return 1
    heartbeat(key, "ok", f"{len(new)} new, {len(changed)} changed, {len(touched)} upserted + re-embedded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
