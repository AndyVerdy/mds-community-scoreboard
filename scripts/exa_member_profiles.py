#!/usr/bin/env python3
"""#211 pass 1 — read each active member's OWN profile URL and write one JSONL row per member.

Identity is anchored on a URL the member gave us, so this pass cannot return the wrong person.
Members with no such URL are out of scope here; they are phase 2 (spec, "Identity and the phase
split"). Never writes the database — that is load_member_web_profiles.py.

  python3 scripts/exa_member_profiles.py --out DIR              # every active with a LinkedIn URL
  python3 scripts/exa_member_profiles.py --out DIR --ids rec1,rec2
  python3 scripts/exa_member_profiles.py --out DIR --limit 20   # a sample
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_client as ex
from load_partner_web_profiles import env as sb_env, sb  # reuse the proven Supabase helpers

ACTIVE = ("Current Member", "New Member", "Current Member- Paused", "Current Member- Not Renewing")

# LinkedIn's own "contents" text always carries this line right after location, one blank line
# apart. Anchoring on it (rather than a fixed line index) is what makes headline extraction survive
# a member with no headline set — see _headline_from_text.
CONNECTIONS_RE = re.compile(r"^[\d,]+\+?\s+connections\b", re.IGNORECASE)


def fetch_all_members(key):
    """member_profiles has 6000+ rows; PostgREST caps an unpaginated GET at 1000, so this pages
    with limit/offset the same way scripts/cache_member_photos.py does — otherwise most active
    members are silently missed (measured live 2026-09-11: 111/733 active seen without paging)."""
    rows, offset = [], 0
    while True:
        page = sb("GET", f"member_profiles?select=at_member_id,at_fields,status&limit=1000&offset={offset}", key)
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def actives_with_url(key, ids=None):
    rows = fetch_all_members(key)
    out = []
    for r in rows:
        if r.get("status") not in ACTIVE:
            continue
        if ids and r["at_member_id"] not in ids:
            continue
        f = r.get("at_fields") or {}
        url = (f.get("Linkedin handle") or "").strip()
        if "linkedin.com" not in url.lower():
            continue
        out.append((r["at_member_id"], url))
    return out


def _headline_from_text(text):
    """The brief's `text.splitlines()[2]` assumes the headline always sits at a fixed line index.
    A live 2026-09-11 run of five members showed that assumption breaks whenever the member has
    not set a LinkedIn headline: the layout is

        [0] "# Name"                     [4] location (or, when no headline: connections line)
        [1] ""                           [5] ""
        [2] headline (or: location)      [6] "N connections • M followers" (when no headline: absent)
        [3] ""

    so with no headline, location shifts up to index 2 and the fixed-index read returns the
    location as a fake headline (confirmed live: Anh Doan's headline came back "Netherlands (NL)",
    which is her location, not anything she wrote as a headline). The "N connections" line is a
    stable LinkedIn-authored marker that always follows location by exactly one blank line, so
    anchoring on it locates the headline slot correctly whether or not it is populated."""
    lines = text.splitlines()
    conn_idx = next((i for i, ln in enumerate(lines) if CONNECTIONS_RE.match(ln.strip())), None)
    if conn_idx is None:
        return None
    headline_idx = conn_idx - 4  # connections -> blank -> location -> blank -> headline
    if headline_idx <= 0:        # 0 is the "# Name" line itself: no headline was set
        return None
    return lines[headline_idx].strip() or None


def shape(at_member_id, url, result):
    ents = result.get("entities") or []
    props = (ents[0].get("properties") if ents else {}) or {}
    work = []
    for w in props.get("workHistory") or []:
        comp = w.get("company") or {}
        dates = w.get("dates") or {}
        work.append({"title": w.get("title"), "company_name": comp.get("name"),
                     "company_entity_id": comp.get("id"),
                     "from": dates.get("from"), "to": dates.get("to")})
    edu = []
    for e in props.get("educationHistory") or []:
        inst = e.get("institution") or {}
        dates = e.get("dates") or {}
        edu.append({"institution": inst.get("name"), "from": dates.get("from"), "to": dates.get("to")})
    text = result.get("text") or ""
    return {
        "at_member_id": at_member_id,
        "source_url": url,
        "source_kind": "linkedin",
        "fetch_status": "ok" if (text or props) else "empty",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "headline": _headline_from_text(text),
        "location": props.get("location"),
        "industry": None,
        "headcount": None,
        "entity_id": (ents[0].get("id") if ents else None),
        "work_history": work,
        "education": edu,
        "raw": result,
        "source_hash": hashlib.sha1((text or "").encode("utf-8", "replace")).hexdigest(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    key = sb_env()["SUPABASE_SECRET_KEY"]
    ids = set(a.ids.split(",")) if a.ids else None
    targets = actives_with_url(key, ids)
    if a.limit:
        targets = targets[:a.limit]
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "profiles.jsonl")

    ok = empty = failed = 0
    with open(path, "w") as fh:
        for i, (mid, url) in enumerate(targets, 1):
            try:
                body = ex.contents([url])
                results = body.get("results") or []
                row = (shape(mid, url, results[0]) if results
                       else {"at_member_id": mid, "source_url": url, "source_kind": "linkedin",
                             "fetch_status": "unreachable",
                             "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                             "work_history": [], "education": [], "raw": None, "source_hash": ""})
            except SystemExit as e:
                print(f"  ! {mid} {e}", file=sys.stderr)
                failed += 1
                continue
            fh.write(json.dumps(row) + "\n")
            ok += row["fetch_status"] == "ok"
            empty += row["fetch_status"] in ("empty", "unreachable")
            if i % 25 == 0:
                print(f"  {i}/{len(targets)}")
            time.sleep(0.2)
    print(f"{path}: {ok} ok · {empty} empty/unreachable · {failed} errored · {len(targets)} targeted")


if __name__ == "__main__":
    main()
