#!/usr/bin/env python3
"""#160 — load extracted partner web profiles into digest.partner_web_profile and link people.

Input: one or more JSONL files, one object per partner, the shape the extraction agents write:

  {"partner_id": "...", "name": "...", "resolved_url": "...", "crawl_status": "ok|empty|unreachable|no_website",
   "summary": "<= 600 chars, what the partner says it does (partner-stated)",
   "services": ["..."], "markets": ["Amazon US", "Shopify", ...], "pricing": "text or null",
   "people": [{"name": "...", "role": "...", "linkedin": "... or null"}],
   "integrations": ["..."], "proof": ["case studies / named clients / awards"],
   "founded": "year or null", "hq": "city, country or null", "confidence": 0.0-1.0,
   "pages": [{"url": "...", "words": 123}]}

  python3 scripts/load_partner_web_profiles.py profiles/*.jsonl            # dry-run report
  python3 scripts/load_partner_web_profiles.py profiles/*.jsonl --apply    # upsert + link people

Rules: upsert on partner_id (a re-crawl replaces the profile); `source_hash` = sha1 of the page
urls+words so an unchanged site is a no-op; people are linked to digest.speakers by canonical
name ONLY when the speaker has no partner yet (never overwrite a human-made link); web copy is
partner-stated and is stored as such — never merged into reviews or member sentiment.
Secrets: /Users/Born/mds-digest-web/.env.local (SUPABASE_SECRET_KEY). Requests via curl.
"""
import argparse
import glob
import hashlib
import json
import re
import subprocess
import sys
import time

ENV = "/Users/Born/mds-digest-web/.env.local"
SB = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
MODEL = "claude-sonnet-5 (Claude Code subagents, #160)"


def env():
    v = {}
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, val = line.split("=", 1)
            v[k.strip()] = val.strip().strip('"').strip("'")
    return v


def sb(method, path, key, body=None, prefer=None):
    cmd = ["curl", "-sS", "-m", "120", "-X", method, f"{SB}/{path}",
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    p = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                       capture_output=True, text=True)
    out = p.stdout.strip()
    if out.startswith("{") and '"message"' in out:
        raise RuntimeError(f"Supabase error on {method} {path}: {out[:300]}")
    return json.loads(out) if out else []


def canon(name):
    return re.sub(r"[^a-z0-9 ]", "", (name or "").lower()).strip()


def source_hash(rec):
    pages = rec.get("pages") or []
    return hashlib.sha1(json.dumps([(p.get("url"), p.get("words")) for p in pages]).encode()).hexdigest()


def row_for(rec):
    return {
        "partner_id": rec["partner_id"],
        "website": rec.get("website"),
        "resolved_url": rec.get("resolved_url"),
        "crawl_status": rec.get("crawl_status") or "ok",
        "crawled_at": rec.get("fetched_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pages": rec.get("pages") or [],
        "profile": {k: rec.get(k) for k in ("services", "markets", "pricing", "people", "integrations",
                                            "proof", "founded", "hq", "confidence")},
        "summary": (rec.get("summary") or "")[:1200] or None,
        "services": [str(s)[:120] for s in (rec.get("services") or [])][:30],
        "markets": [str(s)[:60] for s in (rec.get("markets") or [])][:30],
        "pricing": (rec.get("pricing") or None),
        "people": rec.get("people") or [],
        "source_hash": source_hash(rec),
        "model": MODEL,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    key = env()["SUPABASE_SECRET_KEY"]

    recs = {}
    for pattern in a.files:
        for f in glob.glob(pattern):
            for line in open(f):
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r.get("partner_id"):
                    recs[r["partner_id"]] = r          # last write wins
    print(f"profiles read: {len(recs)}")

    known = {r["partner_id"] for r in sb("GET", "partners_catalog?select=partner_id&limit=2000", key)}
    unknown = [pid for pid in recs if pid not in known]
    if unknown:
        print(f"  ! {len(unknown)} partner_ids not in partners_catalog, skipped: {unknown[:5]}")
    rows = [row_for(recs[pid]) for pid in recs if pid in known]
    by_status = {}
    for r in rows:
        by_status[r["crawl_status"]] = by_status.get(r["crawl_status"], 0) + 1
    print(f"  rows: {len(rows)} · by status: {by_status}")
    people = [(r["partner_id"], p.get("name")) for r in rows for p in (r["people"] or []) if p.get("name")]
    print(f"  people named: {len(people)}")

    # speaker links: canonical name match, only where the speaker has no partner yet
    speakers = sb("GET", "speakers?select=speaker_id,display_name,canonical,partner_id,affiliation_partner_id&limit=5000", key)
    by_canon = {}
    for s in speakers:
        by_canon.setdefault(s.get("canonical") or canon(s.get("display_name")), []).append(s)
    links = []
    for pid, name in people:
        for s in by_canon.get(canon(name), []):
            if not s.get("affiliation_partner_id") and not s.get("partner_id"):
                links.append((s["speaker_id"], s["display_name"], pid))
    print(f"  speaker links to set: {len(links)}" + (f" e.g. {links[:3]}" if links else ""))

    if not a.apply:
        print("DRY RUN — pass --apply to upsert and link")
        return 0
    before = {r["partner_id"]: r.get("source_hash")
              for r in sb("GET", "partner_web_profile?select=partner_id,source_hash&limit=2000", key)}
    for i in range(0, len(rows), 50):
        sb("POST", "partner_web_profile?on_conflict=partner_id", key, rows[i:i + 50],
           "resolution=merge-duplicates,return=minimal")
    print(f"  upserted {len(rows)} profiles")
    # #160: the web text is part of the partner's search vector — a new or changed profile means
    # the vector is stale. Null it; scripts/embed_partners_events.py (nightly + weekly) rebuilds.
    stale = [r["partner_id"] for r in rows
             if r["crawl_status"] == "ok" and before.get(r["partner_id"]) != r["source_hash"]]
    for i in range(0, len(stale), 100):
        ids = ",".join(stale[i:i + 100])
        sb("PATCH", f"partners_catalog?partner_id=in.({ids})", key, {"embedding": None})
    print(f"  vectors nulled for re-embed: {len(stale)}")
    for sid, disp, pid in links:
        sb("PATCH", f"speakers?speaker_id=eq.{sid}", key, {"affiliation_partner_id": pid})
    print(f"  linked {len(links)} speakers (affiliation_partner_id)")
    n = sb("GET", "partner_web_profile?select=partner_id&limit=2000", key)
    print(f"  partner_web_profile rows now: {len(n)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
