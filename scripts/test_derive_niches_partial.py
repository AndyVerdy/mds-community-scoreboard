#!/usr/bin/env python3
"""#180 — a run that is cut short must commit what it finished and touch nothing else.

`python3 scripts/test_derive_niches_partial.py`

The failure this pins shut. `derive_niches` writes by DELETING a member's rows and inserting
the new ones, so "commit what you finished" cannot mean "write the dictionary as it stands".
Step 1 fills that dictionary for EVERY member from their controlled categories; only step 2
adds the niches a member typed themselves, one batch of 40 at a time. Committing everything
after batch 3 of 10 would delete the stated niches of the ~280 members in batches 4 to 10 and
replace them with category-derived ones — a silent downgrade of two thirds of the corpus,
which is worse than the stale data the ticket is about.

So the writable set is: every member who needed no model call at all, plus the members in the
batches that actually completed. Everyone else keeps the rows they already have.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from olivia_derive_niches import writable_ids  # noqa: E402

FAILS = []


def check(name, got, want):
    if got == want:
        print(f"  PASS  {name}")
    else:
        FAILS.append(name)
        print(f"  FAIL  {name}\n        got  {sorted(got) if isinstance(got, set) else got}"
              f"\n        want {sorted(want) if isinstance(want, set) else want}")


def main():
    # 9 members: a, b, c need no model call; d..i were queued for it, 2 per batch.
    all_ids = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    need_llm = [("d", "x"), ("e", "x"), ("f", "x"), ("g", "x"), ("h", "x"), ("i", "x")]
    batch = 2

    check("a complete run writes everyone",
          writable_ids(all_ids, need_llm, batches_done=3, batch=batch), set(all_ids))

    check("nothing done: only the members who never needed the model",
          writable_ids(all_ids, need_llm, batches_done=0, batch=batch), {"a", "b", "c"})

    check("one batch done: adds exactly that batch, and nobody after it",
          writable_ids(all_ids, need_llm, batches_done=1, batch=batch), {"a", "b", "c", "d", "e"})

    check("two batches done",
          writable_ids(all_ids, need_llm, batches_done=2, batch=batch),
          {"a", "b", "c", "d", "e", "f", "g"})

    check("more batches claimed than exist is clamped, never over-writes",
          writable_ids(all_ids, need_llm, batches_done=99, batch=batch), set(all_ids))

    check("no member ever needed the model: everyone is writable even at zero batches",
          writable_ids(all_ids, [], batches_done=0, batch=batch), set(all_ids))

    check("an empty corpus writes nothing rather than raising",
          writable_ids([], [], batches_done=0, batch=batch), set())

    # The regression the whole helper exists to prevent, stated as its own case.
    partial = writable_ids(all_ids, need_llm, batches_done=1, batch=batch)
    unfinished = {mid for mid, _ in need_llm} - partial
    check("members in unfinished batches are EXCLUDED, so their stated niches are not deleted",
          unfinished, {"f", "g", "h", "i"})

    print()
    if FAILS:
        print(f"{len(FAILS)} FAILED: {', '.join(FAILS)}")
        return 1
    print("all partial-commit checks pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
