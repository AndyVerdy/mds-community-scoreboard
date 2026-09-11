"""#211 fix round 1 — MINOR 2: the one safety-critical rule in load_member_web_presence.py (only a
corroborated_by row becomes an edge) had no test, and IMPORTANT 1 fixed a real duplicate-edge bug
in that same rule's dated cousin. `python3 scripts/test_load_member_web_presence.py`"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load_member_web_presence as L

fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)


def conflict_key(e):
    """The tuple web_edges actually dedupes on (its NULLS NOT DISTINCT unique index)."""
    return (e["a_id"], e["a_kind"], e["b_id"], e["b_kind"], e["edge_type"], e["valid_from"])


CORROBORATED = {
    "at_member_id": "recCORR", "url": "https://example.com/interview", "domain": "example.com",
    "kind": "publication", "title": "An Interview", "published_at": "2023-03-16",
    "summary": "...", "corroborated_by": "acme brand", "corroboration_state": "corroborated",
    "confidence": 1.0, "raw": {}, "fetched_at": "2026-09-11T00:00:00Z",
}

# --- a corroborated row produces exactly one edge, dateless, date carried in evidence ---
edge = L.edge_for(CORROBORATED)
check("corroborated row produces an edge", edge is not None)
check("edge valid_from is None", edge is not None and edge["valid_from"] is None,
      str(edge and edge["valid_from"]))
check("published_at rides in evidence instead",
      edge is not None and edge["evidence"]["published_at"] == "2023-03-16",
      str(edge and edge["evidence"]))

# --- no_match: no corroborated_by, no edge ---
no_match = dict(CORROBORATED, corroborated_by=None, corroboration_state="no_match", confidence=0.4)
check("no_match row produces no edge", L.edge_for(no_match) is None)

# --- no_anchor: no corroborated_by, no edge ---
no_anchor = dict(CORROBORATED, corroborated_by=None, corroboration_state="no_anchor", confidence=0.4)
check("no_anchor row produces no edge", L.edge_for(no_anchor) is None)

# --- a corroborated row with no published_at still produces exactly one edge ---
no_date = dict(CORROBORATED, published_at=None)
edge_no_date = L.edge_for(no_date)
check("corroborated row with published_at=None still produces an edge", edge_no_date is not None)
check("its valid_from is still None", edge_no_date is not None and edge_no_date["valid_from"] is None)

# --- regression guard for IMPORTANT 1: same member+URL, different published_at -> same conflict key ---
row_a = dict(CORROBORATED, published_at="2023-03-16")
row_b = dict(CORROBORATED, published_at="2024-11-02")  # a later sweep finds a different date
edge_a, edge_b = L.edge_for(row_a), L.edge_for(row_b)
check("differing published_at yields an identical web_edges conflict key",
      edge_a is not None and edge_b is not None and conflict_key(edge_a) == conflict_key(edge_b),
      f"{conflict_key(edge_a)} vs {conflict_key(edge_b)}")

# --- end-to-end through main()'s comprehension: exactly one edge for one corroborated row among others ---
rows = [CORROBORATED, no_match, no_anchor]
edges = [e for e in (L.edge_for(r) for r in rows) if e]
check("exactly one edge survives a mixed batch", len(edges) == 1, str(len(edges)))

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
