#!/usr/bin/env python3
"""#82 — seed what the flagship event SERIES are, from the public mds.co pages.

CURATED, not scraped: two bespoke marketing pages, copy that changes rarely, and Andy's
#79 ruling that member-facing copy is written rather than generated. source_url and
refreshed_at are stored so the text can be re-checked against the page. Re-runnable.

Read 2026-08-12 from mds.co/mds-summit and mds.co/mds-inspire.
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"

ROWS = [
    {"series": "MDS Summit",
     "match_pattern": "summit",
     "exclude_pattern": "dinner|lunch|night out|experience|social|contest|welcome|party|golf|centurion",
     "what_it_is": "The biggest gathering of MDS members all year — members only, four days, "
                   "built for peer-to-peer depth rather than panels.",
     "format_notes": [
         "MDS Only Sessions: a real challenge goes on the table and the group works through it together",
         "Meet N Speed networking rotations",
         "Dine-Arounds: curated small-group dinners",
         "Hack Contest: members share the tactical tools and wins that worked",
         "Keynotes, deep dives and breakouts across the four days"],
     "audience": "Vetted MDS members only — every attendee is an experienced operator, which is "
                 "what lets people share openly.",
     "source_url": "https://www.mds.co/mds-summit"},
    {"series": "MDS Inspire",
     "match_pattern": "inspire",
     "exclude_pattern": "dinner|lunch|night out|experience|social|contest|welcome|party|golf|centurion",
     "what_it_is": "MDS's flagship open conference — 400+ seven-to-nine-figure ecommerce founders "
                   "across Amazon, TikTok Shop and DTC. Fifth annual.",
     "format_notes": [
         "30+ speakers and 27+ workshops",
         "Keynotes on founder strategy, plus breakouts and deep dives",
         "Focus groups for small-group discussion",
         "One-on-one coffee chats with 40+ founders",
         "Speed networking rotations and a peer-driven hack contest"],
     "audience": "Ambitious ecommerce founders, CEOs and brand owners scaling from high six "
                 "figures to $100M+ — open beyond MDS membership.",
     "source_url": "https://www.mds.co/mds-inspire"},
]


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


def main():
    key = env("SUPABASE_SECRET_KEY")
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/event_series_profile?on_conflict=series",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
         "-H", "Prefer: resolution=merge-duplicates,return=representation",
         "--data-binary", json.dumps(ROWS)], capture_output=True, text=True)
    out = json.loads(r.stdout) if r.stdout.strip() else []
    assert len(out) == len(ROWS), f"upsert returned {len(out)} rows: {r.stdout[:300]}"
    for row in out:
        print(f"  {row['series']}: {len(row['format_notes'])} format notes · {row['source_url']}")
    print(f"seeded {len(out)} series")


if __name__ == "__main__":
    main()
