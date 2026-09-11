#!/usr/bin/env python3
"""#211 — load pass-1 profile JSONL into digest.member_web_profile, web_entity and web_edges.

  python3 scripts/load_member_web_profiles.py /tmp/211/profiles.jsonl           # dry-run report
  python3 scripts/load_member_web_profiles.py /tmp/211/profiles.jsonl --apply   # insert

Rules: member_web_profile is APPEND-ONLY, one row per fetch; an unchanged source_hash is skipped
so a re-run writes nothing. Companies key down a three-step ladder (Exa id, domain, name) and a
name-keyed row is held below full confidence and is never surfaced. Every role edge carries the
source's own dates; a null valid_to is what "current" means. Nothing pre-existing is updated.
"""
import argparse
import json
import re
import sys
from load_partner_web_profiles import env, sb

MODEL = "exa (#211 pass 1)"
FOUNDER = re.compile(r"founder|co-?founder", re.I)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def entity_key(company):
    """Three-step ladder. Returns (entity_id, entity_key_source)."""
    raw_id = company.get("id")
    if raw_id:
        return raw_id.rstrip("/").rsplit("/", 1)[-1], "exa_id"
    domain = (company.get("domain") or "").strip().lower()
    if domain:
        return f"domain:{domain}", "domain"
    return f"name:{slug(company.get('name'))}", "name"


def edges_from(row):
    edges = []
    for w in row.get("work_history") or []:
        eid, src = entity_key({"id": w.get("company_entity_id"), "name": w.get("company_name")})
        ended = bool(w.get("to"))
        if ended:
            etype = "previously_at"
        elif FOUNDER.search(w.get("title") or ""):
            etype = "founded"
        else:
            etype = "works_at"
        edges.append({
            "a_id": row["at_member_id"], "a_kind": "member",
            "b_id": eid, "b_kind": "company",
            "edge_type": etype,
            "valid_from": w.get("from"), "valid_to": w.get("to"),
            "weight": 1.0,
            "evidence": {"title": w.get("title"), "company_name": w.get("company_name"),
                         "entity_key_source": src},
            "source_url": row["source_url"],
            "confidence": 1.0 if src == "exa_id" else 0.7,
        })
    return edges


def entities_from(row):
    seen = {}
    for w in row.get("work_history") or []:
        eid, src = entity_key({"id": w.get("company_entity_id"), "name": w.get("company_name")})
        if eid in seen or not w.get("company_name"):
            continue
        seen[eid] = {"entity_id": eid, "entity_key_source": src, "kind": "company",
                     "name": w["company_name"], "source_url": row["source_url"],
                     "confidence": 1.0 if src == "exa_id" else 0.7}
    return list(seen.values())


def profile_row(row):
    return {k: row.get(k) for k in
            ("at_member_id", "source_url", "source_kind", "fetch_status", "fetched_at",
             "headline", "location", "industry", "headcount", "entity_id",
             "work_history", "education", "raw", "source_hash")} | {"model": MODEL}


def fetch_known(key):
    """member_web_profile will outgrow PostgREST's 1000-row unpaginated GET cap the same way
    member_profiles did for scripts/exa_member_profiles.py (see its fetch_all_members) — page with
    limit/offset so the unchanged-hash skip keeps working once this table is no longer near-empty."""
    rows, offset = [], 0
    while True:
        page = sb("GET", f"member_web_profile?select=at_member_id,source_hash&limit=1000&offset={offset}", key)
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    key = env()["SUPABASE_SECRET_KEY"]

    rows = []
    for path in a.files:
        for line in open(path):
            if line.strip():
                rows.append(json.loads(line))

    known = {r["at_member_id"]: r["source_hash"] for r in fetch_known(key)}

    profiles, entities, edges, skipped = [], [], [], 0
    for r in rows:
        if r.get("source_hash") and known.get(r["at_member_id"]) == r["source_hash"]:
            skipped += 1
            continue
        profiles.append(profile_row(r))
        entities += entities_from(r)
        edges += edges_from(r)

    print(f"{len(rows)} read · {len(profiles)} to insert · {skipped} unchanged · "
          f"{len(entities)} entities · {len(edges)} edges")
    if not a.apply:
        print("dry-run; pass --apply to write")
        return

    # web_edges is deduplicated by a unique INDEX, not a primary key, so PostgREST needs the
    # conflict target spelled out; the other two upsert on their primary keys.
    EDGE_CONFLICT = "on_conflict=a_id,a_kind,b_id,b_kind,edge_type,valid_from"
    for chunk, path in ((profiles, "member_web_profile"),
                        (entities, "web_entity"),
                        (edges, f"web_edges?{EDGE_CONFLICT}")):
        for i in range(0, len(chunk), 200):
            sb("POST", path, key, chunk[i:i + 200], prefer="resolution=merge-duplicates")
    print("applied")


if __name__ == "__main__":
    main()
