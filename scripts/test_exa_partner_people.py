"""#211 fix round 1 — the free-text parser (_org_text_fields) and the corroboration rules built on
top of it (parent_edges' three fail-closed checks, role_class, enrich_people) are the highest-risk
code in this plan: they are the only thing standing between "found a company record" and "wrote the
wrong parent, or a self-referential edge, into digest.web_edges". No network.

  python3 scripts/test_exa_partner_people.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_partner_people as P

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)


# --- CRITICAL 1(a): no parseable "Homepage:" line -> no parent edge, regardless of everything else
no_homepage_result = {
    "url": "https://www.goodfirms.co/company/hectorai",
    "title": "Hector is part of a larger agency network",
    "text": "Hector is part of a larger agency network. No structured company details here.",
    "entities": [{"id": "https://exa.ai/library/organization/abc123", "type": "company",
                  "properties": {"name": "Some Agency"}}],
}
edges = P.parent_edges([no_homepage_result], "partner1", "hectorai.live")
check("no Homepage: line in text produces NO parent edge (CRITICAL 1 regression guard)",
      edges == [], f"edges={edges}")

# --- CRITICAL 1(b): a linkedin.com/in/... URL is a person, never a company
personal_profile_result = {
    "url": "https://www.linkedin.com/in/petersolimine",
    "title": "Peter S. — Parallel Distribution is a subsidiary of Acme Holdings",
    "text": "Parallel Distribution is a subsidiary of Acme Holdings.\n"
            "## Company Details\n- Homepage: acmeholdings.com\n",
    "entities": [{"id": "https://exa.ai/library/person/xyz789", "type": "person",
                  "properties": {"name": "Peter S."}}],
}
edges = P.parent_edges([personal_profile_result], "partner2", "paralleldistribution.com")
check("a linkedin.com/in/ source URL produces no parent edge even with a parseable homepage",
      edges == [], f"edges={edges}")

# --- CRITICAL 1(c): a candidate whose name normalises to the partner's own name is the partner
# itself, even when its parsed homepage happens to differ from the partner's own host string.
self_name_variant_result = {
    "url": "https://linkedin.com/company/cbi-digital-alt-listing",
    "title": "CB/I Digital — owned by CB/I Digital, a product of CB/I Digital",
    "text": "CB/I Digital is a product of itself, listed under a different homepage entry.\n"
            "## Company Details\n- Homepage: cbidigital-alt.example\n",
    "entities": [{"id": "https://exa.ai/library/organization/def456", "type": "company",
                  "properties": {"name": "CB/I Digital"}}],
}
edges = P.parent_edges([self_name_variant_result], "partner3", "cbidigital.com",
                       own_name="CBI Digital")
check("a name differing only by punctuation/case from the partner's own name produces no edge",
      edges == [], f"edges={edges}")

# same check the other direction (ReturnStack vs Returnstack), and confirm the normalizer itself
check("_normalize_name collapses punctuation and case",
      P._normalize_name("ReturnStack") == P._normalize_name("Returnstack") == "returnstack")

# --- a genuine different-company candidate with a parseable homepage DOES produce exactly one edge
real_parent_result = {
    "url": "https://linkedin.com/company/neon-digital-media",
    "title": "Neon Digital Media",
    "text": "At the core of our ecosystem is Hector — our in-house tech.\n"
            "## Company Details\n- Homepage: neondigital.media\n",
    "entities": [{"id": "https://exa.ai/library/organization/cy5tyjxxc1d", "type": "company",
                  "properties": {"name": "Neon Digital Media"}}],
}
edges = P.parent_edges([real_parent_result], "679a26b601681a357fc083cc", "hectorai.live",
                       own_name="Hector")
check("a genuine different-company candidate with a parseable homepage produces exactly one edge",
      len(edges) == 1, f"edges={edges}")
if edges:
    e = edges[0]
    check("the edge names the real parent and has no interval (valid_from/valid_to both null)",
          e["evidence"]["parent_name"] == "Neon Digital Media"
          and e["valid_from"] is None and e["valid_to"] is None,
          str(e))
    check("the edge points a_id -> the parent entity, b_id -> the partner",
          e["a_id"] == "cy5tyjxxc1d" and e["b_id"] == "partner:679a26b601681a357fc083cc")

# --- combining all three checks in one call: a mixed batch keeps only the genuine parent. Each
# bad candidate here is scoped to the SAME partner (Hector/hectorai.live) the good one is, so
# rule (c)'s own-name comparison is actually exercised against the right own_name.
hector_self_variant_result = {
    "url": "https://linkedin.com/company/hector-ai-alt-listing",
    "title": "Hector — a product of Hector",
    "text": "Hector is a product of itself, listed under a different homepage entry.\n"
            "## Company Details\n- Homepage: hectorai-alt.example\n",
    "entities": [{"id": "https://exa.ai/library/organization/hectoralt", "type": "company",
                  "properties": {"name": "Hector"}}],
}
mixed = [no_homepage_result, personal_profile_result, hector_self_variant_result, real_parent_result]
edges = P.parent_edges(mixed, "679a26b601681a357fc083cc", "hectorai.live", own_name="Hector")
check("a mixed batch of bad candidates + one real parent yields exactly the real one",
      len(edges) == 1 and edges[0]["evidence"]["parent_name"] == "Neon Digital Media",
      f"edges={edges}")

# --- CRITICAL 2(a): role_class on real title strings
check('role_class("Founder") == founder', P.role_class("Founder") == "founder")
check('role_class("CEO and Co-Founder") == founder', P.role_class("CEO and Co-Founder") == "founder")
check('role_class("Senior Product and Technology Director") == executive',
      P.role_class("Senior Product and Technology Director") == "executive")
check('role_class("Content Operations Lead") == staff',
      P.role_class("Content Operations Lead") == "staff")
check('role_class("Chief Marketing Officer") == executive',
      P.role_class("Chief Marketing Officer") == "executive")
check('role_class("Growth Head") == executive', P.role_class("Growth Head") == "executive")
check('role_class(None) == staff (no title at all)', P.role_class(None) == "staff")

# --- CRITICAL 2(b): parent_company travels with every person entry only when a parent exists
people = [{"name": "Meher Patel", "role": "Founder", "source": "https://linkedin.com/company/hectorai",
           "confidence": 1.0}]
with_parent = P.enrich_people(people, "Neon Digital Media")
check("a person entry for a partner WITH a parent carries parent_company",
      with_parent[0].get("parent_company") == "Neon Digital Media"
      and with_parent[0].get("role_class") == "founder",
      str(with_parent))

without_parent = P.enrich_people(people, None)
check("a person entry for a partner WITHOUT a parent has no parent_company key",
      "parent_company" not in without_parent[0] and without_parent[0].get("role_class") == "founder",
      str(without_parent))

# original entry is untouched (enrich_people must not mutate its input)
check("enrich_people does not mutate the original list",
      "role_class" not in people[0] and "parent_company" not in people[0])

# --- MINOR 4: a parsed exec line that's empty, absurdly long, or carries a newline is dropped
check("empty role is rejected", P._valid_exec_line("Jane Doe", "") is False)
check("empty name is rejected", P._valid_exec_line("", "Founder") is False)
check("a name with an embedded newline is rejected", P._valid_exec_line("Jane\nDoe", "Founder") is False)
check("an absurdly long role is rejected", P._valid_exec_line("Jane Doe", "x" * 500) is False)
check("a normal name/role pair is accepted", P._valid_exec_line("Jane Doe", "Founder") is True)

# --- _org_text_fields end-to-end: homepage + exec section parse, and MINOR 4 filtering in place
text_ok = (
    "## Company Details\n- Homepage: example.com\n\n"
    "## Workforce\n- Key Executives:\n  - Jane Doe: Founder\n  - John Roe: \n- Breakdown:\n  - x\n"
)
home, execs = P._org_text_fields(text_ok)
check("_org_text_fields parses the homepage line", home == "example.com", home)
check("_org_text_fields stops the exec section at the next 0-indent bullet, and drops the "
      "empty-role line (MINOR 4)",
      execs == [{"name": "Jane Doe", "role": "Founder"}], str(execs))

# --- fix round 3, FIX 6(d): a candidate entity with no name produces NO edge, regardless of
# everything else — entities_from_parent_edges() below builds web_entity.name straight off the
# edge, and that column is NOT NULL, so an edge with no name could never get a paired entity row.
no_name_result = {
    "url": "https://linkedin.com/company/no-name-listing",
    "title": "A product of an unnamed parent",
    "text": "This is a product of its unnamed parent.\n"
            "## Company Details\n- Homepage: unnamedparent.example\n",
    "entities": [{"id": "https://exa.ai/library/organization/noname1", "type": "company",
                  "properties": {}}],
}
edges = P.parent_edges([no_name_result], "partner4", "someproduct.com")
check("a candidate entity with no name produces NO parent edge (FIX 6(d) regression guard)",
      edges == [], f"edges={edges}")

# --- fix round 3, FIX 6: entities_from_parent_edges() builds the paired web_entity row(s) that
# were previously never written, leaving every parent_of edge's company endpoint dangling.
real_edge = P.parent_edges([real_parent_result], "679a26b601681a357fc083cc", "hectorai.live",
                           own_name="Hector")
entities = P.entities_from_parent_edges(real_edge)
check("entities_from_parent_edges produces exactly one entity for the one real edge",
      len(entities) == 1, f"entities={entities}")
if entities:
    ent = entities[0]
    check("the entity is keyed identically to the edge's a_id (exa_id), with the edge's name/url",
          ent["entity_id"] == "cy5tyjxxc1d" and ent["entity_key_source"] == "exa_id"
          and ent["kind"] == "company" and ent["name"] == "Neon Digital Media"
          and ent["source_url"] == real_edge[0]["source_url"],
          str(ent))

# --- entities_from_parent_edges dedupes by entity_id: two edges sharing the same parent company
# (e.g. two different partners both owned by the same agency) must not double-insert that entity.
dup_edges = real_edge + [dict(real_edge[0], b_id="partner:another-partner-id")]
dup_entities = P.entities_from_parent_edges(dup_edges)
check("two edges naming the same parent company collapse to one entity row",
      len(dup_entities) == 1, f"entities={dup_entities}")

check("entities_from_parent_edges of no edges is empty, not an error",
      P.entities_from_parent_edges([]) == [])

print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
