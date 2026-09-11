"""#211 — the loader must key companies down a three-step ladder and date every role edge,
so Ian Sells's three true-at-different-times roles never read as a conflict.
`python3 scripts/test_load_member_web_profiles.py`"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load_member_web_profiles as L

fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)

# --- the ladder ---
eid, src = L.entity_key({"id": "https://exa.ai/library/organization/57m0gbzgjp6",
                         "name": "Happy Innovations"})
check("exa id wins", eid == "57m0gbzgjp6" and src == "exa_id", f"{eid}/{src}")

eid, src = L.entity_key({"id": None, "name": "Hector", "domain": "hectorai.live"})
check("domain is step 2", eid == "domain:hectorai.live" and src == "domain", f"{eid}/{src}")

eid, src = L.entity_key({"id": None, "name": "Million Dollar Sellers"})
check("name is step 3", eid == "name:million-dollar-sellers" and src == "name", f"{eid}/{src}")

# --- dated edges ---
row = {
    "at_member_id": "recIAN",
    "source_url": "https://www.linkedin.com/in/iansells",
    "work_history": [
        {"title": "Founder & CEO", "company_name": "Million Dollar Sellers",
         "company_entity_id": None, "from": "2016-01-01", "to": None},
        {"title": "Co-Founder", "company_name": "JoinBrands",
         "company_entity_id": None, "from": "2021-01-01", "to": None},
        {"title": "CEO", "company_name": "RebateKey",
         "company_entity_id": None, "from": "2017-01-01", "to": "2022-01-01"},
    ],
}
edges = L.edges_from(row)
check("one edge per company", len(edges) == 3, str(len(edges)))
check("eight companies would be eight edges, not one column", all(e["a_id"] == "recIAN" for e in edges))

founded = [e for e in edges if e["edge_type"] == "founded"]
works = [e for e in edges if e["edge_type"] == "works_at"]
prev = [e for e in edges if e["edge_type"] == "previously_at"]
check("a founder title makes a founded edge", len(founded) == 2, str(len(founded)))
check("an ended role is previously_at", len(prev) == 1 and prev[0]["valid_to"] == "2022-01-01")
check("a current role has a null valid_to", all(e["valid_to"] is None for e in founded + works))
check("valid_from is carried", founded[0]["valid_from"] == "2016-01-01")
check("every edge cites its source", all(e["source_url"] for e in edges))
check("name-keyed edges sit below full confidence",
      all(e["confidence"] < 1 for e in edges), str([e["confidence"] for e in edges]))

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
