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

# --- punctuation-only / non-Latin names must not collapse onto the bare "name:" node ---
eid_a, src_a = L.entity_key({"id": None, "name": "!!!"})
eid_b, src_b = L.entity_key({"id": None, "name": "北京烤鸭"})
check("punctuation-only and non-Latin names don't collapse to the same key",
      eid_a != eid_b and eid_a != "name:" and eid_b != "name:",
      f"{eid_a} vs {eid_b}")

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

# --- repeated vs. distinct company names must key to the same vs. different nodes ---
row_dup = {
    "at_member_id": "recDUP",
    "source_url": "https://www.linkedin.com/in/dupcheck",
    "work_history": [
        {"title": "Advisor", "company_name": "Acme Corp",
         "company_entity_id": None, "from": "2018-01-01", "to": None},
        {"title": "Consultant", "company_name": "Acme Corp",
         "company_entity_id": None, "from": "2019-01-01", "to": None},
        {"title": "Board Member", "company_name": "Globex Corp",
         "company_entity_id": None, "from": "2020-01-01", "to": None},
        {"title": "Investor", "company_name": "Initech",
         "company_entity_id": None, "from": "2021-01-01", "to": None},
    ],
}
edges_dup = L.edges_from(row_dup)
b_ids = {e["b_id"] for e in edges_dup}
check("two entries naming the same company collapse to one node; distinct companies don't",
      len(edges_dup) == 4 and len(b_ids) == 3, f"edges={len(edges_dup)} distinct_b_ids={len(b_ids)}")

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

# --- a work_history entry with no usable company name produces no edge and no entity ---
row_noname = {
    "at_member_id": "recNONAME",
    "source_url": "https://www.linkedin.com/in/noname",
    "work_history": [
        {"title": "Something", "company_name": None,
         "company_entity_id": None, "from": "2020-01-01", "to": None},
        {"title": "Something Else", "company_name": "",
         "company_entity_id": None, "from": "2019-01-01", "to": None},
    ],
}
edges_noname = L.edges_from(row_noname)
entities_noname = L.entities_from(row_noname)
check("a null company_name produces no edge and no entity",
      len(edges_noname) == 0 and len(entities_noname) == 0,
      f"edges={len(edges_noname)} entities={len(entities_noname)}")
check("both no-name entries are counted as skipped",
      L.skipped_work_entries(row_noname) == 2, str(L.skipped_work_entries(row_noname)))

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
