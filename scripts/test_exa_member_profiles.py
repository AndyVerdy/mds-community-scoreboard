#!/usr/bin/env python3
"""#211 — no-network checks for scripts/exa_member_profiles.py's row shape, hash stability and
entity_id normalisation (round-1 fix findings). `python3 scripts/test_exa_member_profiles.py`"""
import hashlib
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exa_member_profiles as M

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)


# --- CRITICAL 1 / IMPORTANT 3: one shape across ok, empty, unreachable and failed rows ---
ok_result = {
    "text": "# X\n\nFounder & CEO @ Acme\n\nUSA (US)\n\n500 connections • 10 followers\n",
    "entities": [{"id": "https://exa.ai/library/person/abc123xyz",
                  "properties": {"location": "USA", "workHistory": [], "educationHistory": []}}],
}
ok_row = M.shape("recOK", "https://www.linkedin.com/in/ok", ok_result)
empty_row = M.shape("recEMPTY", "https://www.linkedin.com/in/empty", {})
unreachable_row = M._base_row("recUNREACHABLE", "https://www.linkedin.com/in/unreachable", "unreachable")
failed_row = M._base_row("recFAILED", "https://www.linkedin.com/in/failed", "failed",
                          error="exa contents curl failed: timed out")

rows = {"ok": ok_row, "empty": empty_row, "unreachable": unreachable_row, "failed": failed_row}
key_sets = {name: set(row) for name, row in rows.items()}
distinct = set(frozenset(s) for s in key_sets.values())
check("ok/empty/unreachable/failed rows carry the identical key set", len(distinct) == 1,
      str(key_sets))
check("that key set is exactly ROW_FIELDS", distinct == {frozenset(M.ROW_FIELDS)} if distinct else False,
      str(distinct))

check("ok row's status is ok", ok_row["fetch_status"] == "ok")
check("empty row's status is empty", empty_row["fetch_status"] == "empty")
check("unreachable row has no error text (it wasn't a raised failure)",
      unreachable_row["error"] is None)
check("failed row carries the error text", failed_row["error"] == "exa contents curl failed: timed out")
check("ok/empty/unreachable rows have no error text", ok_row["error"] is None and empty_row["error"] is None)


# --- IMPORTANT 4: hash excludes the volatile connections/followers line ---
base = "# X\n\nFounder & CEO @ Acme\n\nUSA (US)\n\n"
text_a = base + "500 connections • 10 followers\n"
text_b = base + "812 connections • 4,001 followers\n"   # same profile, counts drifted
norm_a, norm_b = M._normalize_for_hash(text_a), M._normalize_for_hash(text_b)
check("normalising strips the connections line regardless of the counts in it", norm_a == norm_b,
      f"{norm_a!r} vs {norm_b!r}")

hash_a = hashlib.sha1(norm_a.encode("utf-8", "replace")).hexdigest()
hash_b = hashlib.sha1(norm_b.encode("utf-8", "replace")).hexdigest()
check("same profile, different connection/follower counts -> same hash", hash_a == hash_b)

changed = base.replace("Founder & CEO @ Acme", "CEO @ Acme Holdings") + "500 connections • 10 followers\n"
hash_changed = hashlib.sha1(M._normalize_for_hash(changed).encode("utf-8", "replace")).hexdigest()
check("a real change to the profile body changes the hash", hash_changed != hash_a)

# ok and empty paths must hash the same normalised text — exercise shape()'s actual source_hash
ok_row_b = M.shape("recOK2", "https://www.linkedin.com/in/ok2",
                    {**ok_result, "text": text_b, "entities": ok_result["entities"]})
check("shape() hashes ok rows the same way regardless of connection-count drift",
      ok_row["source_hash"] == ok_row_b["source_hash"],
      f"{ok_row['source_hash']} vs {ok_row_b['source_hash']}")
empty_hash = hashlib.sha1(M._normalize_for_hash("").encode("utf-8", "replace")).hexdigest()
check("shape() hashes the empty path with the same normaliser", empty_row["source_hash"] == empty_hash)


# --- IMPORTANT 5: top-level entity_id is normalised, no slashes ---
short = M._short_entity_id("https://exa.ai/library/person/2st6d86289g")
check("entity_id has no slashes", short is not None and "/" not in short, repr(short))
check("entity_id keeps the meaningful last segment", short == "2st6d86289g", repr(short))
check("entity_id is None when there is no source id", M._short_entity_id(None) is None)
check("entity_id is None for an empty string", M._short_entity_id("") is None)
check("a real shape() row's top-level entity_id has no slashes",
      ok_row["entity_id"] is not None and "/" not in ok_row["entity_id"], repr(ok_row["entity_id"]))
check("a real shape() row's top-level entity_id is the short form",
      ok_row["entity_id"] == "abc123xyz", repr(ok_row["entity_id"]))


print(("FAILED " + str(len(fails))) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
