#!/usr/bin/env python3
"""#211 — fill digest.partner_web_profile.people for the 281 rows where it is empty.

#160 crawled each partner's own site, which is why `people` is empty on 281 of 506 rows and on
180 of the 405 that crawled fine: founders are not on marketing sites. This asks Exa for the
company record instead. Writes ONLY the `people` column (plus `updated_at`), and ONLY where it
is currently empty — except the one-off `--backfill-roles` maintenance pass (fix round 1, below),
which re-patches already-filled rows on purpose.

An executive list alone does not settle "whose founder is this" — Hector (#5068) is the in-house
technology of an agency (Neon Digital Media, itself part of Wondrlab), and the founder Exa returns
for the Hector name (Meher Patel) is actually the founder of that agency, not of Hector. parent_edges()
below writes a `parent_of` edge in digest.web_edges whenever a result names a parent/owner
relationship, so a downstream consumer can attach the founder to the parent company instead of to
the product. Fix round 1 adds a second layer on top of the edge: every person entry now also
carries `role_class` and, when a parent exists, `parent_company` — so the wrong-founder claim
cannot be read without the correcting context sitting right next to it in the same JSON value.

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

FIX ROUND 1 (review found two Criticals — see git log for the review verbatim):

CRITICAL 1 — parent_edges() failed OPEN. `if host and host in home: continue` only excludes the
partner itself when `home` (the candidate's own parsed homepage) is non-empty; a candidate with no
parseable "Homepage:" line at all sailed straight through as if it were a stranger. Live result: 10
of the first 15 parent_of edges written were self-referential (Create With Cura, Amobeez,
NeonPanel, CBI Digital, SaneBox, Growi x2, MyFBAPrep, Mercury, Returnstack all pointed at
themselves), and one recorded a person's own LinkedIn profile
(https://www.linkedin.com/in/petersolimine, "Peter S.") as if it were a company. parent_edges() now
fails CLOSED on three checks together: (a) no parseable homepage at all -> skip, never assume a
stranger; (b) a linkedin.com/in/... URL is a person, not a company -> skip; (c) a candidate whose
name normalises (lowercased, non-alphanumerics stripped) to the partner's own name is the partner
itself under a formatting difference -> skip, even when its homepage happened to parse differently.

CRITICAL 2 — Hector's `people` entry for Meher Patel still read "Founder" with nothing beside it
saying that's the parent agency's founder, not Hector's — the literal #5068 wrong answer, sitting
right next to the (correct) parent_of edge that doesn't get read by whatever renders `people`. The
record itself is accurate (he IS listed on Hector's own LinkedIn page); what was missing was
context. Fixed by never deleting the entry and instead making it unable to mislead on its own:
role_class() classifies the verbatim title into founder/executive/staff, and enrich_people() stamps
`parent_company` onto every person entry for a partner that has a parent_of edge.

  python3 scripts/exa_partner_people.py --limit 10
  python3 scripts/exa_partner_people.py --apply
  python3 scripts/exa_partner_people.py --fix-parents --apply     # delete + re-derive parent_of
  python3 scripts/exa_partner_people.py --backfill-roles --apply  # add role_class/parent_company
                                                                   #   to rows already filled

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

# fix round 1, MINOR 4: a parsed exec line this malformed is a parser miss, not a real person —
# drop it rather than store it. 100/200 are generous (real names/titles are well under this) so
# this only ever catches genuine garbage (a line the section regex swallowed by mistake, e.g.).
MAX_NAME_LEN = 100
MAX_ROLE_LEN = 200

# fix round 1, CRITICAL 1(b): a linkedin.com/in/... URL is a PERSON's own profile, never a company.
_PERSONAL_PROFILE_RE = re.compile(r"linkedin\.com/in/", re.I)

# fix round 1, CRITICAL 2(a): title -> role_class. Checked in this order — a "CEO and Co-Founder"
# must land on "founder", not "executive", so the founder check runs first.
_FOUNDER_RE = re.compile(r"\b(founder|co-founder|owner|ceo)\b", re.I)
_EXEC_RE = re.compile(r"\b(chief|c[a-z]{1,3}o|president|vice[\s-]?president|vp|head|director)\b", re.I)


def _normalize_name(s):
    """Lowercase + strip everything but letters/digits, so "CB/I Digital" and "CBI Digital" (or
    "ReturnStack" and "Returnstack") compare equal — fix round 1, CRITICAL 1(c)."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _valid_exec_line(name, role):
    """Reject a parsed exec line that's empty, absurdly long, or carries a stray newline — fix
    round 1, MINOR 4. Malformed input from the free-text parser should be dropped, not stored."""
    if not name or not role:
        return False
    if "\n" in name or "\n" in role:
        return False
    if len(name) > MAX_NAME_LEN or len(role) > MAX_ROLE_LEN:
        return False
    return True


def role_class(title):
    """founder: title names a founder/owner/CEO. executive: other C-level/chief/president/VP/head/
    director titles. staff: everything else. Order matters — founder is checked first so "CEO and
    Co-Founder" lands on founder, not executive (fix round 1, CRITICAL 2(a))."""
    t = title or ""
    if _FOUNDER_RE.search(t):
        return "founder"
    if _EXEC_RE.search(t):
        return "executive"
    return "staff"


def enrich_people(people, parent_name=None):
    """Stamp role_class on every entry, and parent_company when the partner has one — the
    correcting context that must travel WITH the record, not sit in a side table nobody reading
    `people` would think to check (fix round 1, CRITICAL 2)."""
    out = []
    for p in people:
        q = dict(p)
        q["role_class"] = role_class(q.get("role"))
        if parent_name:
            q["parent_company"] = parent_name
        out.append(q)
    return out


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
            if _valid_exec_line(name, role):
                execs.append({"name": name, "role": role})
    return homepage, execs


def targets(key, limit=None):
    rows = sb("GET", "partner_web_profile?select=partner_id,resolved_url,summary,people", key)
    out = [r for r in rows if not r.get("people") or json.dumps(r["people"]) in EMPTY]
    return out[:limit] if limit else out


def people_from(results, host):
    """Prefer the record whose domain matches the partner's own site — that is the corroboration.
    Also returns the matched entity's own name (own_name), needed by parent_edges' CRITICAL 1(c)
    self-name check; None when nothing matched."""
    best = None
    for r in results:
        ents = r.get("entities") or []
        for e in ents:
            home, execs = _org_text_fields(r.get("text"))
            if not execs:
                continue
            match = bool(host) and host in home
            props = e.get("properties") or {}
            cand = ([{"name": x.get("name"), "role": x.get("role"),
                      "source": r.get("url") or r.get("id"),
                      "confidence": 1.0 if match else 0.5} for x in execs],
                    e.get("id"), match, props.get("name"))
            if match:
                return cand
            best = best or cand
    return best or ([], None, False, None)


def _own_name_from_results(results, host):
    """Find the entity among `results` whose own parsed homepage matches `host`, and return its
    name — used by --fix-parents, which re-runs only the parent query (not the primary leadership
    query) and so has no people_from() call to hand it own_name directly."""
    if not host:
        return None
    for r in results:
        home, _execs = _org_text_fields(r.get("text"))
        if home and host in home:
            for e in r.get("entities") or []:
                nm = (e.get("properties") or {}).get("name")
                if nm:
                    return nm
    return None


def parent_edges(results, partner_id, host, own_name=None):
    """A company-to-company edge, so a founder can attach to the parent instead of the product.

    Fails CLOSED on four checks (fix round 1, CRITICAL 1 — the original code failed OPEN whenever
    a candidate had no parseable Homepage: line, producing 10 self-referential edges plus one
    pointing at a person's own LinkedIn profile instead of a company — see module docstring):
      (a) no parseable homepage at all -> skip, never assume a stranger
      (b) a linkedin.com/in/... URL is a PERSON's profile, never a company -> skip
      (c) a candidate whose name normalises (lowercased, non-alphanumerics stripped) to the
          partner's own name is the partner itself under a formatting difference -> skip
      (d) (fix round 3, FIX 6) no name at all -> skip; entities_from_parent_edges() below builds
          the paired digest.web_entity row straight off this edge's evidence.parent_name, and
          web_entity.name is NOT NULL — an edge written with no name could never get one.
    """
    own_norm = _normalize_name(own_name) if own_name else None
    out = []
    for r in results:
        blob = " ".join(str(r.get(k) or "") for k in ("title", "text", "summary"))
        if not PARENT.search(blob):
            continue
        home, _execs = _org_text_fields(r.get("text"))
        if not home:
            continue                                  # (a) unparseable homepage: fail closed
        if host and host in home:
            continue                                  # the partner itself, by homepage
        source_url = r.get("url") or r.get("id") or ""
        if _PERSONAL_PROFILE_RE.search(source_url):
            continue                                  # (b) a person, not a company
        for e in r.get("entities") or []:
            props = e.get("properties") or {}
            cand_name = props.get("name")
            if not cand_name:
                continue                              # (d) no name: fail closed, see docstring
            if own_norm and _normalize_name(cand_name) == own_norm:
                continue                              # (c) the partner itself, by name
            eid = (e.get("id") or "").rstrip("/").rsplit("/", 1)[-1]
            if not eid:
                continue
            out.append({
                "a_id": eid, "a_kind": "company",
                "b_id": f"partner:{partner_id}", "b_kind": "partner",
                "edge_type": "parent_of", "valid_from": None, "valid_to": None,
                "weight": 1.0,
                "evidence": {"parent_name": cand_name, "phrase_matched": True},
                "source_url": source_url,
                "confidence": 0.8,
            })
    return out


def entities_from_parent_edges(edges):
    """The paired digest.web_entity row for every parent_of edge parent_edges() produces — keyed
    identically to the edge's own a_id, which is always the candidate's Exa id here (parent_edges()
    only ever emits an edge once `eid`, derived from that id, is non-empty; see check (d) above for
    why the name is guaranteed present too). Without this, every parent_of edge points at a company
    node that digest.web_entity has never heard of: unlike scripts/load_member_web_profiles.py
    (entities_from/edges_from always write both), this script used to write only the edge (#211 fix
    round 3, FIX 6). Deduped by entity_id so one candidate named by several results in the same
    batch is written once."""
    out = {}
    for e in edges:
        out[e["a_id"]] = {
            "entity_id": e["a_id"], "entity_key_source": "exa_id", "kind": "company",
            "name": (e.get("evidence") or {}).get("parent_name"),
            "source_url": e.get("source_url"), "confidence": e.get("confidence", 0.8),
        }
    return list(out.values())


def parent_query(name, summary, host):
    """A second, narrower query used only for a partner whose own record already corroborated —
    see the module docstring for why the plain leadership query never surfaces the parent page."""
    words = (summary or "").split()[:6]
    snippet = " ".join(words) if words else name
    return f"{snippet} in-house technology of agency parent company {host}".strip()


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


EDGE_CONFLICT = "on_conflict=a_id,a_kind,b_id,b_kind,edge_type,valid_from"
# #211 fix round 3, FIX 6: every parent_of edge's company endpoint must have a matching web_entity
# row — written via this same merge-duplicates upsert target, ahead of the edge (see call sites),
# so a run that crashes mid-way leaves an unreferenced entity rather than a dangling edge.
ENTITY_CONFLICT = "on_conflict=entity_id"


def _ours(people):
    """True when every entry in `people` carries our pipeline's "confidence" key — the schema
    #160's own-site crawl never wrote (its rows are {"name","role","linkedin"}). Used by
    --fix-parents to scope re-derivation to partners this script actually corroborated, not every
    partner with any people at all."""
    return bool(people) and all(isinstance(p, dict) and "confidence" in p for p in people)


def fix_parents(key, apply):
    """fix round 1: delete every parent_of edge and re-derive with the fixed parent_edges() rule,
    scoped to exactly the partners this pipeline corroborated. Re-runs only the parent_query (not
    the primary leadership search, which already produced the stored `people` correctly) — one Exa
    call per partner, same cost as the original derivation."""
    rows = sb("GET", "partner_web_profile?select=partner_id,resolved_url,summary,people", key)
    ours = [r for r in rows if _ours(r.get("people"))]
    print(f"{len(ours)} partners with our own corroborated people entries")

    before = sb("GET", "web_edges?edge_type=eq.parent_of&select=a_id", key)
    print(f"before: {len(before)} parent_of edges")

    if apply:
        sb("DELETE", "web_edges?edge_type=eq.parent_of", key)

    written = []
    for i, r in enumerate(ours, 1):
        host = urlparse(r.get("resolved_url") or "").netloc.lower().removeprefix("www.")
        name = host.split(".")[0] if host else (r.get("summary") or "")[:40]
        pbody = ex.search(parent_query(name, r.get("summary"), host),
                          numResults=8, type="auto", contents=CONTENTS_OPT)
        results = pbody.get("results") or []
        own_name = _own_name_from_results(results, host)
        row_edges = parent_edges(results, r["partner_id"], host, own_name)
        if apply and row_edges:
            row_entities = entities_from_parent_edges(row_edges)
            if row_entities:
                sb("POST", f"web_entity?{ENTITY_CONFLICT}", key, row_entities,
                   prefer="resolution=merge-duplicates")
            sb("POST", f"web_edges?{EDGE_CONFLICT}", key, row_edges, prefer="resolution=merge-duplicates")
        written += row_edges
        if i % 25 == 0:
            print(f"  {i}/{len(ours)}")
        time.sleep(0.2)

    after = sb("GET", "web_edges?edge_type=eq.parent_of&select=a_id,b_id,evidence,source_url", key) if apply else written
    print(f"after: {len(after)} parent_of edges")
    for e in after:
        parent_name = (e.get("evidence") or {}).get("parent_name")
        print(f"  {e.get('b_id')} <- {parent_name} ({e.get('a_id')})")
    if not apply:
        print("dry-run; pass --apply to delete + write")


def backfill_roles(key, apply):
    """fix round 1, CRITICAL 2: add role_class (+ parent_company where one exists) to every
    already-filled people row — not just rows filled from here on. Still writes only the `people`
    column (plus updated_at)."""
    rows = sb("GET", "partner_web_profile?select=partner_id,people", key)
    rows = [r for r in rows if r.get("people")]
    edges = sb("GET", "web_edges?edge_type=eq.parent_of&select=b_id,evidence", key)
    parents = {}
    for e in edges:
        b_id = e.get("b_id") or ""
        if b_id.startswith("partner:"):
            parents[b_id.split("partner:", 1)[1]] = (e.get("evidence") or {}).get("parent_name")

    changed = 0
    for r in rows:
        parent_name = parents.get(r["partner_id"])
        new_people = enrich_people(r["people"], parent_name)
        if new_people != r["people"]:
            changed += 1
            if apply:
                sb("PATCH", f"partner_web_profile?partner_id=eq.{r['partner_id']}", key,
                   {"people": new_people, "updated_at": _now()})
    print(f"{len(rows)} rows with people · {changed} updated with role_class/parent_company"
          + ("" if apply else " (dry-run; pass --apply to write)"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--fix-parents", action="store_true",
                    help="delete all parent_of edges and re-derive them with the fixed rule")
    ap.add_argument("--backfill-roles", action="store_true",
                    help="add role_class/parent_company to every already-filled people row")
    a = ap.parse_args()
    key = env()["SUPABASE_SECRET_KEY"]

    if a.fix_parents:
        return fix_parents(key, a.apply)
    if a.backfill_roles:
        return backfill_roles(key, a.apply)

    rows = targets(key, a.limit)
    filled = missed = uncorroborated = 0
    edges_written = 0
    for i, r in enumerate(rows, 1):
        host = urlparse(r.get("resolved_url") or "").netloc.lower().removeprefix("www.")
        name = host.split(".")[0] if host else (r.get("summary") or "")[:40]
        body = ex.search(f"category:company {name} — official company record and leadership",
                         numResults=5, type="auto", contents=CONTENTS_OPT)
        results = body.get("results") or []
        people, entity_id, matched, own_name = people_from(results, host)
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
            row_edges = parent_edges(pbody.get("results") or [], r["partner_id"], host, own_name)
            time.sleep(0.2)
        if a.apply and people and matched:
            parent_name = row_edges[0]["evidence"]["parent_name"] if row_edges else None
            sb("PATCH", f"partner_web_profile?partner_id=eq.{r['partner_id']}", key,
               {"people": enrich_people(people, parent_name), "updated_at": _now()})
        # Written per-row, not batched to the end of the run: a run over hundreds of live API
        # calls can be interrupted, and batching-to-the-end would silently lose every edge
        # computed before the interruption even though the people PATCHes for those same rows
        # had already landed (measured live 2026-09-11 — a killed run left 19 people-fills
        # committed and zero edges, because the old code only POSTed edges after the loop).
        if a.apply and row_edges:
            row_entities = entities_from_parent_edges(row_edges)
            if row_entities:
                sb("POST", f"web_entity?{ENTITY_CONFLICT}", key, row_entities,
                   prefer="resolution=merge-duplicates")
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
