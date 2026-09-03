#!/usr/bin/env python3
"""#160 — fetch a partner's own website as plain text, for the profile extraction step.

GroupOS gives us a website for 505 of 507 published partners (168 of them as go.mdsonly.co
tracking links that resolve by a meta-refresh, 38 as other affiliate links). This script turns
one partner's site into a small JSON bundle the extraction agents read:

  {"partner_id", "name", "website", "resolved_url", "status": "ok|unreachable|empty",
   "fetched_at", "pages": [{"url", "title", "words", "text"}]}

  python3 scripts/partner_web_crawl.py sites.json --out DIR            # every partner in sites.json
  python3 scripts/partner_web_crawl.py sites.json --out DIR --slice 3/10   # partition 3 of 10
  python3 scripts/partner_web_crawl.py sites.json --out DIR --ids id1,id2  # just these

Rules: homepage + up to MAX_EXTRA internal pages whose path looks like about/team/services/
pricing/case-studies; plain curl with a browser UA and a 20 s cap; text capped per page; a
partner already in DIR is skipped unless --force. No JS rendering — a JS-only site comes back
"empty" and is listed for the browser fallback. Stdlib only.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import urljoin, urlparse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
MAX_EXTRA = 4
MAX_WORDS = 2500
INTERESTING = re.compile(r"/(about|team|our-story|company|who-we-are|services?|solutions?|what-we-do|"
                         r"pricing|plans|packages|rates|case-stud|customers|clients|results|"
                         r"portfolio|features?|products?)(/|\.|$|-)", re.I)
SKIP = re.compile(r"\.(png|jpe?g|gif|svg|pdf|zip|mp4|css|js)(\?|$)|/(blog|news|feed|tag|category|"
                  r"wp-json|wp-content|cart|checkout|login|signin|signup|register|privacy|terms|"
                  r"cookie|sitemap|xmlrpc)", re.I)


def curl(url, timeout=20):
    p = subprocess.run(["curl", "-sSL", "-m", str(timeout), "-A", UA, "--compressed",
                        "-w", "\n%{url_effective}\t%{http_code}", url],
                       capture_output=True, text=True, errors="replace")
    body, _, tail = p.stdout.rpartition("\n")
    parts = tail.split("\t")
    final = parts[0] if parts and parts[0].startswith("http") else url
    code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return body, final, code


def resolve(url):
    """Follow HTTP redirects, then one meta-refresh / JS hop (go.mdsonly.co is a Pixelfy page)."""
    body, final, code = curl(url)
    m = (re.search(r'http-equiv=["\']refresh["\'][^>]*url=["\']?\s*([^"\'>\s]+)', body, re.I)
         or re.search(r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)', body))
    if m and m.group(1).startswith("http") and urlparse(m.group(1)).netloc != urlparse(final).netloc:
        body, final, code = curl(m.group(1))
    return body, final, code


def to_text(page):
    page = re.sub(r"<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>", " ", page, flags=re.S | re.I)
    page = re.sub(r"<!--.*?-->", " ", page, flags=re.S)
    title = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
    page = re.sub(r"<br\s*/?>|</(p|div|li|h[1-6]|tr|section|article)>", "\n", page, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    words = text.split()
    if len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS]) + " …"
    return (html.unescape(title.group(1)).strip()[:160] if title else ""), text, len(words)


def internal_links(page, base):
    host = urlparse(base).netloc.lower().removeprefix("www.")
    out, seen = [], set()
    for href in re.findall(r'href=["\']([^"\'#]+)', page, re.I):
        u = urljoin(base, href.strip())
        pu = urlparse(u)
        if pu.scheme not in ("http", "https") or pu.netloc.lower().removeprefix("www.") != host:
            continue
        u = u.split("?")[0].rstrip("/")
        if u in seen or SKIP.search(u) or not INTERESTING.search(pu.path + "/"):
            continue
        seen.add(u)
        out.append(u)
    # pricing/about/services first, then the rest in page order
    out.sort(key=lambda u: (0 if re.search(r"pricing|plans|rates", u, re.I) else
                            1 if re.search(r"about|team|company|story", u, re.I) else
                            2 if re.search(r"service|solution|what-we-do", u, re.I) else 3))
    return out[:MAX_EXTRA]


def crawl_one(p):
    rec = {"partner_id": p["partner_id"], "name": p["name"], "website": p.get("website"),
           "resolved_url": None, "status": "unreachable", "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "pages": []}
    if not p.get("website"):
        rec["status"] = "no_website"
        return rec
    try:
        body, final, code = resolve(p["website"])
    except Exception as e:  # noqa: BLE001
        rec["error"] = str(e)[:200]
        return rec
    rec["resolved_url"] = final
    rec["http_code"] = code
    if code >= 400 or not body:
        return rec
    title, text, words = to_text(body)
    rec["pages"].append({"url": final, "title": title, "words": words, "text": text})
    # an affiliate deep link (demo booking, signup, /brands/mds) is not the homepage: fetch the
    # site root too, so the profile is built from what the company says, not the landing page
    pu = urlparse(final)
    root = f"{pu.scheme}://{pu.netloc}/"
    if pu.path.strip("/") or pu.query:
        try:
            b0, f0, c0 = curl(root)
            if c0 < 400 and b0:
                t0, x0, w0 = to_text(b0)
                if w0 >= 40:
                    rec["pages"].insert(0, {"url": f0, "title": t0, "words": w0, "text": x0})
                    body, final = b0, f0          # discover internal pages from the real homepage
        except Exception:  # noqa: BLE001
            pass
    for u in internal_links(body, final):
        try:
            b2, f2, c2 = curl(u)
        except Exception:  # noqa: BLE001
            continue
        if c2 >= 400 or not b2:
            continue
        t2, x2, w2 = to_text(b2)
        if w2 >= 40:
            rec["pages"].append({"url": f2, "title": t2, "words": w2, "text": x2})
    total = sum(pg["words"] for pg in rec["pages"])
    rec["status"] = "ok" if total >= 80 else "empty"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sites", help="JSON list of {partner_id,name,website}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--slice", help="i/n — take partition i (1-based) of n")
    ap.add_argument("--ids", help="comma-separated partner ids")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    sites = json.load(open(a.sites))
    if a.ids:
        want = set(a.ids.split(","))
        sites = [s for s in sites if s["partner_id"] in want]
    if a.slice:
        i, n = (int(x) for x in a.slice.split("/"))
        sites = sites[i - 1::n]
    os.makedirs(a.out, exist_ok=True)
    done = ok = 0
    for s in sites:
        path = os.path.join(a.out, s["partner_id"] + ".json")
        if os.path.exists(path) and not a.force:
            continue
        rec = crawl_one(s)
        json.dump(rec, open(path, "w"), ensure_ascii=False)
        done += 1
        ok += rec["status"] == "ok"
        print(f"{rec['status']:<11} {s['name'][:40]:<40} pages={len(rec['pages'])} "
              f"words={sum(pg['words'] for pg in rec['pages'])}", flush=True)
    print(f"done {done} · ok {ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
