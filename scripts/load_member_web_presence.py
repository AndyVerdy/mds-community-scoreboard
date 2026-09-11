#!/usr/bin/env python3
"""#211 — load pass-2 presence JSONL into digest.member_web_presence and featured_in edges.

  python3 scripts/load_member_web_presence.py /tmp/211/presence.jsonl
  python3 scripts/load_member_web_presence.py /tmp/211/presence.jsonl --apply

Upserts on (at_member_id, url) so a weekly re-run refreshes rather than duplicates. Every row
carries a corroboration_state (corroborated | no_anchor | no_match) from the pass-2 sweep; an
uncorroborated row is stored at confidence 0.4 and is never promoted to an edge — only rows with
a corroborated_by value become a featured_in edge in digest.web_edges.
"""
import argparse
import json
from load_partner_web_profiles import env, sb

COLS = ("at_member_id", "url", "domain", "kind", "title", "published_at",
        "summary", "corroborated_by", "corroboration_state", "confidence", "raw", "fetched_at")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    key = env()["SUPABASE_SECRET_KEY"]

    rows = []
    for p in a.files:
        for line in open(p):
            if line.strip():
                rows.append(json.loads(line))

    presence = [{k: r.get(k) for k in COLS} for r in rows]
    edges = [{
        "a_id": r["at_member_id"], "a_kind": "member",
        "b_id": r["url"], "b_kind": "external",
        "edge_type": "featured_in", "valid_from": r.get("published_at"), "valid_to": None,
        "weight": 1.0,
        "evidence": {"kind": r["kind"], "title": r.get("title"),
                     "corroborated_by": r.get("corroborated_by")},
        "source_url": r["url"], "confidence": r["confidence"],
    } for r in rows if r.get("corroborated_by")]

    by_kind = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    print(f"{len(presence)} presence rows {by_kind} · {len(edges)} corroborated edges")
    if not a.apply:
        print("dry-run; pass --apply to write")
        return
    # digest.member_web_presence's primary key is (at_member_id, url); digest.web_edges has no
    # primary key at all and is deduplicated by a NULLS NOT DISTINCT unique index over the six
    # columns below (see scripts/sql/20260911_211_web_layer.sql) — every merge-duplicates call
    # site in this codebase names its conflict target explicitly rather than relying on
    # PostgREST's default, and web_edges' target is not optional since it has no PK to fall back to.
    PRESENCE_CONFLICT = "on_conflict=at_member_id,url"
    EDGE_CONFLICT = "on_conflict=a_id,a_kind,b_id,b_kind,edge_type,valid_from"
    for chunk, path in ((presence, f"member_web_presence?{PRESENCE_CONFLICT}"),
                        (edges, f"web_edges?{EDGE_CONFLICT}")):
        for i in range(0, len(chunk), 200):
            sb("POST", path, key, chunk[i:i + 200], prefer="resolution=merge-duplicates")
    print("applied")


if __name__ == "__main__":
    main()
