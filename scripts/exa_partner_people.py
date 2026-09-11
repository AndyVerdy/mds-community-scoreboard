#!/usr/bin/env python3
"""#211 — fill digest.partner_web_profile.people for the 281 rows where it is empty.

#160 crawled each partner's own site, which is why `people` is empty on 281 of 506 rows and on
180 of the 405 that crawled fine: founders are not on marketing sites. This asks Exa for the
company record instead. Writes ONLY the `people` column, and ONLY where it is currently empty.

An executive list alone does not settle "whose founder is this" — Hector (#5068) is the in-house
technology of an agency (Neon Digital Media, itself part of Wondrlab), and the founder Exa returns
for the Hector name (Meher Patel) is actually the founder of that agency, not of Hector. parent_edges()
below writes a `parent_of` edge in digest.web_edges whenever a result names a parent/owner
relationship, so a downstream consumer can attach the founder to the parent company instead of to
the product — that edge, not the people column, is the actual fix.

DEVIATION FROM THE ORIGINAL BRIEF, measured live 2026-09-11: the brief's people_from/parent_edges
read `properties.keyExecutives` and `properties.homepage` off each result's `entities[]`. Live
against the real API, neither field is ever populated — `entities[].properties` only carries
name/foundedYear/description/workforce/headquarters/financials/webTraffic/research. The homepage
and the "Key Executives" list only exist in the entity's free-text `text` (the markdown Exa
renders for an organization, e.g. "- Homepage: hectorai.live" / "- Key Executives:\n  - X: Y").
_org_text_fields() below parses those two facts out of `text` instead. This requires the search
call to request contents at all — the brief's bare `ex.search(query, numResults=5, type="auto")`
never returns an `entities` key on any result; `entities` only appears once a `contents` option is
present (confirmed live: identical query with vs. without `contents={"text": ...}` on the same
company). Both changes are additive fixes to how data is *read*; the writes are unchanged, still
gated on `matched` (homepage corroboration), still People-column-only + parent_of-edge-only.

The parent search: Exa's neural ranking for the plain "{name} — official company record and
leadership" query does not surface Neon Digital Media in Hector's results even at numResults=10
(measured live) — it returns LinkedIn/Tracxn/Companies-House pages about Hector itself, never the
agency's own page where the "our in-house tech" phrase actually lives. A second, narrower query run
only when the primary pass already found a corroborated match — the exact moment a wrong founder
could get written — reliably surfaces it instead (measured live, 4/4 stable). This costs one extra
Exa call for the subset of partners that resolve to a real company record, not for all 506.

  python3 scripts/exa_partner_people.py --limit 10
  python3 scripts/exa_partner_people.py --apply

Note (PostgREST 1000-row cap): targets() issues a single unpaginated GET. partner_web_profile has
506 rows today so this is complete; past 1000 rows PostgREST truncates the response and this would
silently miss targets. See scripts/exa_member_profiles.py's fetch_all_members for the paging
pattern (limit/offset) this would need if the table grows past that.
"""
import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_client as ex
from load_partner_web_profiles import env, sb

EMPTY = ("null", "[]", "{}", '""')

PARENT = re.compile(r"\b(in-?house (tech|technology|product|platform)|a (product|brand|platform) (of|by)|"
                    r"owned by|powered by|part of|subsidiary of)\b", re.I)

CONTENTS_OPT = {"text": {"maxCharacters": 3000}}

_HOMEPAGE_RE = re.compile(r"(?im)^-\s*Homepage:\s*(\S+)\s*$")
# The "Key Executives:" bullet sits at 0 indent under "## Workforce"; its own entries are indented
# 2+ spaces ("  - Name: Role"). Requiring 2+ spaces on the continuation lines is what stops the
# match at the next 0-indent bullet ("- Breakdown:") instead of swallowing it and everything below.
_EXEC_SECTION_RE = re.compile(r"(?im)^-\s*Key Executives:\s*\n((?:^[ \t]{2,}-.*\n?)+)", re.M)


def _org_text_fields(text):
    """Pull homepage + key-executive name/role pairs out of an entity's free-text org write-up —
    see the module docstring for why these live only in text, not in `properties`."""
    text = text or ""
    hm = _HOMEPAGE_RE.search(text)
    homepage = (hm.group(1) if hm else "").lower()
    execs = []
    sm = _EXEC_SECTION_RE.search(text)
    if sm:
        for raw in sm.group(1).splitlines():
            line = raw.strip()
            if not line.startswith("-"):
                continue
            line = line[1:].strip()
            if ":" not in line:
                continue
            name, role = line.split(":", 1)
            name = name.strip()
            role = role.strip()
            if name:
                execs.append({"name": name, "role": role or None})
    return homepage, execs


def targets(key, limit=None):
    rows = sb("GET", "partner_web_profile?select=partner_id,resolved_url,summary,people", key)
    out = [r for r in rows if not r.get("people") or json.dumps(r["people"]) in EMPTY]
    return out[:limit] if limit else out


def people_from(results, host):
    """Prefer the record whose domain matches the partner's own site — that is the corroboration."""
    best = None
    for r in results:
        ents = r.get("entities") or []
        for e in ents:
            home, execs = _org_text_fields(r.get("text"))
            if not execs:
                continue
            match = bool(host) and host in home
            cand = ([{"name": x.get("name"), "role": x.get("role"),
                      "source": r.get("url") or r.get("id"),
                      "confidence": 1.0 if match else 0.5} for x in execs],
                    e.get("id"), match)
            if match:
                return cand
            best = best or cand
    return best or ([], None, False)


def parent_edges(results, partner_id, host):
    """A company-to-company edge, so a founder can attach to the parent instead of the product."""
    out = []
    for r in results:
        blob = " ".join(str(r.get(k) or "") for k in ("title", "text", "summary"))
        if not PARENT.search(blob):
            continue
        home, _execs = _org_text_fields(r.get("text"))
        for e in r.get("entities") or []:
            props = e.get("properties") or {}
            if host and host in home:
                continue                      # the partner itself, not its parent
            eid = (e.get("id") or "").rstrip("/").rsplit("/", 1)[-1]
            if not eid:
                continue
            out.append({
                "a_id": eid, "a_kind": "company",
                "b_id": f"partner:{partner_id}", "b_kind": "partner",
                "edge_type": "parent_of", "valid_from": None, "valid_to": None,
                "weight": 1.0,
                "evidence": {"parent_name": props.get("name"), "phrase_matched": True},
                "source_url": r.get("url") or r.get("id") or "",
                "confidence": 0.8,
            })
    return out


def parent_query(name, summary, host):
    """A second, narrower query used only for a partner whose own record already corroborated —
    see the module docstring for why the plain leadership query never surfaces the parent page."""
    words = (summary or "").split()[:6]
    snippet = " ".join(words) if words else name
    return f"{snippet} in-house technology of agency parent company {host}".strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    key = env()["SUPABASE_SECRET_KEY"]

    rows = targets(key, a.limit)
    filled = missed = uncorroborated = 0
    edges_written = 0
    EDGE_CONFLICT = "on_conflict=a_id,a_kind,b_id,b_kind,edge_type,valid_from"
    for i, r in enumerate(rows, 1):
        host = urlparse(r.get("resolved_url") or "").netloc.lower().removeprefix("www.")
        name = host.split(".")[0] if host else (r.get("summary") or "")[:40]
        body = ex.search(f"category:company {name} — official company record and leadership",
                         numResults=5, type="auto", contents=CONTENTS_OPT)
        results = body.get("results") or []
        people, entity_id, matched = people_from(results, host)
        if not people:
            missed += 1
        elif not matched:
            uncorroborated += 1
        else:
            filled += 1
        row_edges = []
        if matched:
            # Only spend the second call where a wrong founder could actually get written: a
            # corroborated match is exactly the case #5068 is about.
            pbody = ex.search(parent_query(name, r.get("summary"), host),
                              numResults=8, type="auto", contents=CONTENTS_OPT)
            row_edges = parent_edges(pbody.get("results") or [], r["partner_id"], host)
            time.sleep(0.2)
        if a.apply and people and matched:
            sb("PATCH", f"partner_web_profile?partner_id=eq.{r['partner_id']}", key, {"people": people})
        # Written per-row, not batched to the end of the run: a run over hundreds of live API
        # calls can be interrupted, and batching-to-the-end would silently lose every edge
        # computed before the interruption even though the people PATCHes for those same rows
        # had already landed (measured live 2026-09-11 — a killed run left 19 people-fills
        # committed and zero edges, because the old code only POSTed edges after the loop).
        if a.apply and row_edges:
            sb("POST", f"web_edges?{EDGE_CONFLICT}", key, row_edges, prefer="resolution=merge-duplicates")
            edges_written += len(row_edges)
        if i % 25 == 0:
            print(f"  {i}/{len(rows)}")
        time.sleep(0.2)
    print(f"{len(rows)} targeted · {filled} filled (corroborated) · "
          f"{uncorroborated} found but uncorroborated (not written) · {missed} no executives")
    if a.apply:
        print(f"  wrote {edges_written} parent_of edges")
    if not a.apply:
        print("dry-run; pass --apply to write")


if __name__ == "__main__":
    main()
