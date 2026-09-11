#!/usr/bin/env python3
"""#211 pass 2 — what the world has said about a member, third parties only.

The member's own domains are excluded in the query, and a result counts only when the page also
names something we already know about that member. The 2026-09-11 sweep on one member returned
three wrong entities out of ten on a brand name alone; corroboration is what rejects them.

  python3 scripts/exa_member_presence.py --out DIR --limit 20
  python3 scripts/exa_member_presence.py --out DIR --ids rec1,rec2
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_client as ex
from load_partner_web_profiles import env as sb_env, sb

ACTIVE = ("Current Member", "New Member", "Current Member- Paused", "Current Member- Not Renewing")
START = "2023-01-01"
STOPWORDS = {"the", "and", "inc", "llc", "ltd", "co", "company", "brand", "brands", "several", "n/a", "none"}
PODCAST = re.compile(r"/podcast|podcasts?\.|/episode|buzzsprout|libsyn|simplecast|captivate\.fm", re.I)
SPEAKER = re.compile(r"/speakers?/|/sessions?/|summit|conference|/agenda/", re.I)
VIDEO = re.compile(r"youtube\.com|youtu\.be|vimeo\.com", re.I)
AGGREGATOR = re.compile(r"success\.ai|equilar\.com|rocketreach|zoominfo|apollo\.io|signalhire", re.I)


def _values(raw):
    """at_fields values arrive as a native list (JSONB decoded straight through — measured live
    2026-09-11: "Brand Name" and "Storefront - Census" are Airtable multi-selects and come back
    as an actual Python list, not a string), a JSON array string, or plain text. Only the string
    case can be `.strip()`-ed; a bare list crashed every member whose Brand Name is a multi-select,
    which on a live sample was most of them — not an edge case."""
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(v) for v in raw if v]
    if not isinstance(raw, str):
        return [str(raw)]
    raw = raw.strip()
    if raw.startswith("["):
        try:
            return [str(v) for v in json.loads(raw)]
        except json.JSONDecodeError:
            pass
    return [raw]


def anchors_for(at_fields):
    out = set()
    excluded = set()
    for field in ("Brand Name", "Brand(s) URL / Name(s)", "Storefront - Census"):
        for v in _values(at_fields.get(field)):
            # A "Parent (Sub1, Sub2)" value names Parent as the umbrella company and Sub1/Sub2 as
            # its product lines — exactly the shape of the real Happy Nuts collision (spec AC 9d):
            # "Happy Innovations (Happy Nuts, Happy Curves, Happy Soles)". A product-line name is a
            # generic, consumer-facing name that unrelated businesses reuse (the 2026-09-11 sweep
            # hit a Chiba nut factory, a Vietnamese gifting company and a Dubai LLC all sharing the
            # name "Happy Nuts"), so names listed in parens are excluded as standalone anchors —
            # even if the same name also shows up as a bare list item elsewhere for this member —
            # leaving the umbrella/company name as the trustworthy identity anchor.
            for paren in re.findall(r"\(([^)]*)\)", v):
                for sub in re.split(r"[,/]", paren):
                    s = sub.strip().lower()
                    if s:
                        excluded.add(s)
            # Splitting on "&"/"and" as if they were list separators was measured live
            # 2026-09-11 against member recPnlefVvc0Utn62: real single brand names "Home & Rowe"
            # and "Earth and Blue LLC" were cut into "home", "rowe", "earth", "blue llc" — two
            # bare dictionary words ("home", "earth") that would corroborate nearly any unrelated
            # page. "&"/"and" are commonly part of ONE brand's name (a standard consumer-branding
            # pattern); comma and slash are the only delimiters Airtable's own multi-brand fields
            # use unambiguously as separators, so only split on those.
            for part in re.split(r"[,/]", re.sub(r"\([^)]*\)", "", v)):
                p = part.strip().lower()
                if len(p) >= 4 and p not in STOPWORDS and not p.startswith("http"):
                    out.add(p)
    return sorted(out - excluded)


def own_domains(at_fields):
    out = set()
    for field in ("Brand(s) URL / Name(s)", "Own Website & % of Revenue", "Storefront - Census"):
        for v in _values(at_fields.get(field)):
            for m in re.finditer(r"([a-z0-9-]+\.[a-z]{2,})(?:/|\b)", v.lower()):
                out.add(m.group(1))
    return sorted(out)


def corroborate(text, anchors):
    low = (text or "").lower()
    for a in anchors:
        if a in low:
            return a
    return None


def classify(url, category):
    if AGGREGATOR.search(url):
        return "aggregator"
    if VIDEO.search(url):
        return "video"
    if PODCAST.search(url):
        return "podcast"
    if SPEAKER.search(url):
        return "speaking"
    if category in ("news", "publication", "company"):
        return "news" if category == "news" else ("publication" if category == "publication" else "company_page")
    return "publication"


def sweep(name, anchors, domains):
    body = ex.search(
        f"{name}, {anchors[0] if anchors else ''} — interviews, press and appearances",
        numResults=10, type="auto", startPublishedDate=START,
        excludeDomains=sorted(set(domains)) or None,
        contents={"summary": {"query": "In one sentence, what is this page and what does it say about this person?"},
                  "text": {"maxCharacters": 400}},
    )
    return body.get("results") or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    key = sb_env()["SUPABASE_SECRET_KEY"]
    ids = set(a.ids.split(",")) if a.ids else None
    # member_profiles holds 6,135 rows and an unpaginated PostgREST GET caps at 1000, which would
    # silently see only 111 of the 733 actives. Task 3 added fetch_all_members() for exactly this;
    # reuse it rather than a bare sb("GET", ...).
    from exa_member_profiles import fetch_all_members
    members = [r for r in fetch_all_members(key)
               if r.get("status") in ACTIVE and (not ids or r["at_member_id"] in ids)]
    if a.limit:
        members = members[:a.limit]

    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "presence.jsonl")
    kept = dropped = 0
    with open(path, "w") as fh:
        for i, m in enumerate(members, 1):
            f = m.get("at_fields") or {}
            anchors, domains = anchors_for(f), own_domains(f)
            for r in sweep(m.get("full_name") or "", anchors, domains):
                url = r.get("url") or r.get("id") or ""
                host = urlparse(url).netloc.lower().removeprefix("www.")
                if any(host.endswith(d) for d in domains):
                    dropped += 1
                    continue
                blob = " ".join(str(r.get(k) or "") for k in ("title", "text", "summary"))
                hit = corroborate(blob, anchors)
                fh.write(json.dumps({
                    "at_member_id": m["at_member_id"], "url": url, "domain": host,
                    "kind": classify(url, r.get("category")), "title": r.get("title"),
                    "published_at": (r.get("publishedDate") or "")[:10] or None,
                    "summary": r.get("summary"), "corroborated_by": hit,
                    "confidence": 1.0 if hit else 0.4, "raw": r,
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }) + "\n")
                kept += 1
            if i % 25 == 0:
                print(f"  {i}/{len(members)}")
            time.sleep(0.2)
    print(f"{path}: {kept} rows kept · {dropped} own-domain rows dropped · {len(members)} members")


if __name__ == "__main__":
    main()
