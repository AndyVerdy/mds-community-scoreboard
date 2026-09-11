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


_DOMAIN_LIKE = re.compile(r"^(?:[a-z0-9-]+\.)+[a-z]{2,}$")


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
                for sub in re.split(r"[,/\n]", paren):
                    s = sub.strip().lower()
                    if s:
                        excluded.add(s)
            # Splitting on "&"/"and" as if they were list separators was measured live
            # 2026-09-11 against member recPnlefVvc0Utn62: real single brand names "Home & Rowe"
            # and "Earth and Blue LLC" were cut into "home", "rowe", "earth", "blue llc" — two
            # bare dictionary words ("home", "earth") that would corroborate nearly any unrelated
            # page. "&"/"and" are commonly part of ONE brand's name (a standard consumer-branding
            # pattern); comma and slash are the only delimiters Airtable's own multi-brand fields
            # use unambiguously as separators, so only split on those (plus newline — see below).
            #
            # (#211 round 2, IMPORTANT 2): "Brand(s) URL / Name(s)" values are very commonly
            # "Name\nURL\nName\nURL" (real example, same member: "Intimate Rose\nhttps://www.
            # intimaterose.com/ \nTreat My Feet\n..."). Without splitting on the newline, a brand
            # name and the URL line after it merge into one dead anchor that can never match page
            # text — measured live: anchor "dwelling with pride\nhttps:". Newline is now a
            # separator too, and splitting on "/" still breaks each URL into its own fragment
            # ("www.intimaterose.com"), so any fragment that is itself a bare domain (not a brand
            # name) is dropped via _DOMAIN_LIKE rather than kept as if it were one.
            for part in re.split(r"[,/\n]", re.sub(r"\([^)]*\)", "", v)):
                p = part.strip().lower()
                if (len(p) >= 4 and p not in STOPWORDS and not p.startswith("http")
                        and not _DOMAIN_LIKE.match(p)):
                    out.add(p)
    return sorted(out - excluded)


_URL_RE = re.compile(r"https?://\S+", re.I)
_HOST_RE = re.compile(r"(?:[a-z0-9-]+\.)+[a-z]{2,}")


def _clean_host(host):
    host = host.lower().rsplit("@", 1)[-1]  # drop userinfo, e.g. "user@host"
    host = host.split(":", 1)[0]            # drop a port
    return host.removeprefix("www.")


def own_domains(at_fields):
    """Extract the member's own hosts with the TLD intact.

    Fix (#211 round 2, CRITICAL 1): the old pattern `[a-z0-9-]+\\.[a-z]{2,}` stops at the FIRST
    internal dot, so "https://www.example.com/shop" became "www.example" and "shop.example.com"
    became "shop.example" — the TLD silently lost. Measured live 2026-09-11: 135/734 actives have
    any own-domain data at all, and 72 of those 135 produced at least one TLD-less string; member
    recN2dGfelmx01pWf alone yielded ['endurimed.com', 'www.dwellingwithpride', 'www.intimaterose',
    'www.treatmyfeet'] — three of four unusable. A truncated own-domain means the member's own
    site (the single page most likely to contain their own brand name) survives the exclusion
    filter and self-corroborates to confidence 1.0, indistinguishable from real third-party
    corroboration — this task's whole failure mode, in reverse.

    A full URL is parsed with urlparse() for its netloc rather than regex-guessed, so a query
    string full of dots ("?ref=some.thing") can never be mistaken for part of the host. A bare
    domain with no scheme ("shop.example.com") still needs a regex, but it now matches the WHOLE
    dotted hostname (one or more "label." groups ending in a real TLD label), not just the first
    segment.
    """
    out = set()
    for field in ("Brand(s) URL / Name(s)", "Own Website & % of Revenue", "Storefront - Census"):
        for v in _values(at_fields.get(field)):
            for u in _URL_RE.findall(v):
                host = _clean_host(urlparse(u).netloc)
                if host:
                    out.add(host)
            # Strip matched URLs before the bare-domain scan so a URL's own host isn't captured
            # a second (harmlessly redundant) time via the fallback regex, and so nothing in a
            # path/query is ever scanned as if it were a bare hostname.
            rest = _URL_RE.sub(" ", v)
            for m in _HOST_RE.finditer(rest.lower()):
                out.add(_clean_host(m.group(0)))
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
                  # 400 chars is about a paragraph — too small a window to reliably contain a
                  # corroborating mention (#211 round 2, IMPORTANT 3; pass 1 fetches 3500 for the
                  # same reason). Raised to 2000; still well short of pass 1's full-page fetch,
                  # but enough to cover more than a lede paragraph.
                  "text": {"maxCharacters": 2000}},
    )
    return body.get("results") or []


def _corroboration_blob(r, url, host):
    """Text corroborate() checks against. A brand name often survives in a URL/host even when
    neither the fetched text nor the title mentions it — e.g. a slug like
    ".../big-shiny-balls-jules-..." or a subdomain naming the brand (#211 round 2, IMPORTANT 3).
    Kebab/underscore separators are normalized to spaces alongside the raw url/host so a
    multi-word anchor like "big shiny balls" can match "big-shiny-balls" as well as a one-word
    anchor matching a bare domain fragment."""
    blob = " ".join(str(r.get(k) or "") for k in ("title", "text", "summary"))
    return blob + " " + url + " " + host + " " + url.replace("-", " ").replace("_", " ")


def process_results(results, anchors, domains):
    """Drop own-domain hits and corroborate the rest — pulled out of main()'s loop (#211 round 2,
    MINOR 5) so this, the actual decision logic, is unit-testable against a fake result list
    instead of requiring a live Exa call. Returns (rows, dropped_count); rows are missing only
    at_member_id/fetched_at, added by the caller."""
    rows = []
    dropped = 0
    for r in results:
        url = r.get("url") or r.get("id") or ""
        host = urlparse(url).netloc.lower().removeprefix("www.")
        if any(host.endswith(d) for d in domains):
            dropped += 1
            continue
        hit = corroborate(_corroboration_blob(r, url, host), anchors)
        # corroboration_state (#211 round 2, IMPORTANT 4) distinguishes WHY a row is
        # uncorroborated: "no_anchor" means the member had nothing on file to test against at
        # all (the check was impossible to run), "no_match" means anchors existed and the page
        # simply didn't mention any of them. Both currently carry the same 0.4 confidence, but
        # without this field the two cases are indistinguishable in the data even though they
        # mean very different things about how much to trust the row.
        if hit:
            state, confidence = "corroborated", 1.0
        elif not anchors:
            state, confidence = "no_anchor", 0.4
        else:
            state, confidence = "no_match", 0.4
        rows.append({
            "url": url, "domain": host, "kind": classify(url, r.get("category")),
            "title": r.get("title"), "published_at": (r.get("publishedDate") or "")[:10] or None,
            "summary": r.get("summary"), "corroborated_by": hit,
            "corroboration_state": state, "confidence": confidence, "raw": r,
        })
    return rows, dropped


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
    state_counts = {"corroborated": 0, "no_match": 0, "no_anchor": 0}
    with open(path, "w") as fh:
        for i, m in enumerate(members, 1):
            f = m.get("at_fields") or {}
            anchors, domains = anchors_for(f), own_domains(f)
            results = sweep(m.get("full_name") or "", anchors, domains)
            rows, d = process_results(results, anchors, domains)
            dropped += d
            for row in rows:
                row["at_member_id"] = m["at_member_id"]
                row["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                fh.write(json.dumps(row) + "\n")
                kept += 1
                state_counts[row["corroboration_state"]] += 1
            if i % 25 == 0:
                print(f"  {i}/{len(members)}")
            time.sleep(0.2)
    print(f"{path}: {kept} rows kept · {dropped} own-domain rows dropped · {len(members)} members · "
          f"{state_counts['corroborated']} corroborated · {state_counts['no_match']} no_match · "
          f"{state_counts['no_anchor']} no_anchor")


if __name__ == "__main__":
    main()
