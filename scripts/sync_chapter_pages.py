#!/usr/bin/env python3
"""#6 Chapters — scrape the PUBLIC mds.co chapter pages into digest.chapters_catalog.

The site publishes, per chapter: leads (name + role + photo), an About paragraph, six
stats (Chapter Members, TTM Revenue, Avg TTM Revenue, Employees, Avg Employees, Avg Age)
and Top Categories. Andy's ruling 2026-07-31: that makes them SHAREABLE — but the site
may lag, so member COUNTS always come live from member records (chapter_info computes
them; site stats are stored as "as published"). Lead emails/phones are never on the page
and never stored.

Re-runnable any time ("dynamically update it in supa"): full upsert by chapter key.
Verification is part of the run — every page must yield leads + 6 stats + categories or
it is named PARTIAL and the script exits 1 (the Women's page has its own layout and is
allowed partial, named).
"""
import json, re, subprocess, sys, urllib.request
from html.parser import HTMLParser

ENV = "/Users/Born/mds-digest-web/.env.local"

# canonical warehouse name (member records) -> site page
SEED = [
    ("New York Chapter",         "New York",          "new-york-chapter",         "North America", "New York City, NY, US"),
    ("Women's Chapter",          "MDS Women",         "mds-women",                "Worldwide",     "worldwide (women founders)"),
    ("Europe Chapter",           "Europe",            "europe-chapter",           "Worldwide",     "Europe"),
    ("Asia Pacific Chapter",     "Asia Pacific",      "asia-pacific-chapter",     "Worldwide",     "Asia-Pacific: Australia, China, Southeast Asia"),
    ("SoFlo Chapter",            "South Florida",     "south-florida-chapter",    "North America", "South Florida (Miami / Fort Lauderdale), FL, US"),
    ("LA Chapter",               "Los Angeles",       "la-chapter",               "North America", "Los Angeles, CA, US"),
    ("Pacific Northwest Chapter","Pacific NorthWest", "pacific-northwest-chapter","North America", "Pacific Northwest (Seattle / Portland), US"),
    ("Chicago Chapter",          "Chicago",           "chicago-chapter",          "North America", "Chicago, IL, US"),
    ("Southside Chapter",        "Southside",         "southside-chapter",        "North America", "US Southeast (Atlanta area)"),
    ("Central Florida Chapter",  "Central Florida",   "central-florida-chapter",  "North America", "Central Florida (Orlando / Tampa), FL, US"),
    ("Orange Co Chapter",        "Orange Co",         "oc-chapter",               "North America", "Orange County, CA, US"),
    ("SoTex Chapter",            "South Texas",       "south-texas-chapter",      "North America", "South Texas (Austin / San Antonio / Houston), TX, US"),
    ("Rocky Mountain Chapter",   "Rockies",           "rockies-chapter",          "North America", "Rocky Mountains (Denver), CO, US"),
    ("UK Chapter",               "UK",                "uk-chapter",               "Worldwide",     "United Kingdom (London)"),
    ("Las Vegas Chapter",        "Las Vegas",         "las-vegas-chapter",        "North America", "Las Vegas, NV, US"),
    ("Toronto Chapter",          "Toronto",           "toronto-chapter",          "North America", "Toronto, Canada"),
    ("San Diego Chapter",        "San Diego",         "san-diego-chapter",        "North America", "San Diego, CA, US"),
    ("NorCal Chapter",           "North Cal",         "norcal-chapter",           "North America", "Northern California (Bay Area), CA, US"),
    ("NorthTex Chapter",         "North Texas",       "north-texas-chapter",      "North America", "Dallas-Fort Worth (DFW Metroplex), TX, US"),
    ("Puerto Rico Chapter",      "Puerto Rico",       "puerto-rico-chapter",      "North America", "Puerto Rico"),
]
URL_BASE = "https://www.mds.co/chapters/"
# the chapters index links MDS Women to milliondollarsellers.com/mds-women, which 404s —
# the live page is on the standard path (verified 2026-07-31): mds.co/chapters/mds-women
SPECIAL_URLS = {}
ALLOWED_PARTIAL = set()

ROLES = re.compile(r"^Chapter\s+(President|Planner|Moderator|Lead|Co-Lead)s?$", re.I)
STAT_LABELS = ["Chapter Members", "TTM Revenue", "Avg TTM Revenue", "Employees", "Avg Employees", "Avg Age"]
STAT_KEYS = ["chapter_members", "ttm_revenue", "avg_ttm_revenue", "employees", "avg_employees", "avg_age"]
VALUE_RE = re.compile(r"^\$?[\d,.]+[MBK]?\+?$")


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


class Stream(HTMLParser):
    """Flatten the page into an ordered stream of ('text', s) / ('img', src) items."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "img" and not self._skip:
            src = dict(attrs).get("src") or ""
            if src.startswith("http"):
                self.items.append(("img", src))

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        t = re.sub(r"\s+", " ", data).strip()
        if t:
            self.items.append(("text", t))


def fetch(url):
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", "45", "--retry", "1",
         "-A", "Mozilla/5.0 (mds chapter sync)", url],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl {r.returncode}: {r.stderr.strip()[:120]}")
    return r.stdout


def section(items, start, ends):
    """Items strictly after the first text == start, up to the first text in ends."""
    out, on = [], False
    for kind, v in items:
        if kind == "text" and v == start:
            on = True
            continue
        if on and kind == "text" and v in ends:
            break
        if on:
            out.append((kind, v))
    return out


def parse(html):
    p = Stream()
    p.feed(html)
    items = p.items

    # leads: img -> name -> role triples between the two headings
    # (some pages title the section "Chapter Lead", singular — Rockies, Las Vegas)
    leads = []
    img, name = None, None
    sec = section(items, "Chapter Leads", {"About the Chapter"}) or \
          section(items, "Chapter Lead", {"About the Chapter"})
    for kind, v in sec:
        if kind == "img":
            img = v
        elif ROLES.match(v):
            if name:
                leads.append({"name": name, "role": v, "photo_url": img})
            img, name = None, None
        else:
            name = v

    # about + stats live between "About the Chapter" and "Top Categories Represented"
    about_parts, stats = [], {}
    pend = None
    for kind, v in section(items, "About the Chapter", {"Top Categories Represented"}):
        if kind != "text":
            continue
        v = {"Members": "Chapter Members"}.get(v, v)  # the Women's page shortens the label
        if v in STAT_LABELS:
            if pend is not None:
                stats[STAT_KEYS[STAT_LABELS.index(v)]] = pend
            pend = None
        elif VALUE_RE.match(v):
            pend = v
        else:
            about_parts.append(v)
            pend = None
    about = " ".join(about_parts).strip() or None

    cats = [v for kind, v in section(items, "Top Categories Represented", {"Chapter Event Highlights", "How To Become A Member?"})
            if kind == "text" and not v.startswith("Discover the leading")]
    return leads, about, stats, cats


def main():
    base = env("SUPABASE_URL").rstrip("/")
    key = env("SUPABASE_SECRET_KEY")
    rows, report, bad = [], [], []

    for chapter, site_name, slug, region, geo in SEED:
        url = SPECIAL_URLS.get(slug, URL_BASE + slug)
        try:
            leads, about, stats, cats = parse(fetch(url))
        except Exception as e:
            leads, about, stats, cats = [], None, {}, []
            report.append(f"FAIL     {chapter}: fetch/parse error {e}")
            bad.append(chapter)
            continue
        ok = bool(leads) and len(stats) == 6 and bool(cats)
        status = "ok" if ok else "PARTIAL"
        if not ok and chapter not in ALLOWED_PARTIAL:
            bad.append(chapter)
        rows.append({
            "chapter": chapter, "site_name": site_name, "slug": slug, "page_url": url,
            "region": region, "geo": geo, "about": about, "leads": leads,
            "categories": cats, "site_stats": stats, "scraped_at": "now()",
        })
        report.append(f"{status:8} {chapter}: leads={len(leads)} stats={len(stats)}/6 cats={len(cats)}")

    r = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"{base}/rest/v1/chapters_catalog?on_conflict=chapter",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
         "-H", "Prefer: resolution=merge-duplicates,return=minimal",
         "--data-binary", "@-"],
        input=json.dumps(rows), capture_output=True, text=True)
    if r.stdout.strip():
        print("UPSERT response:", r.stdout[:300])

    print("\n".join(report))
    print(f"upserted {len(rows)} chapters")
    if bad:
        print(f"HARD FAILURES (not allowed partial): {bad}")
        sys.exit(1)


if __name__ == "__main__":
    main()
