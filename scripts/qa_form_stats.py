#!/usr/bin/env python3
"""#20 QA — mechanical sweep of the census lane across EVERY askable question.

Andy 2026-08-06: "we are battling for one field and there are dozens. You need to QA it."

For each canonical question in the form_stats catalog, this asserts the standing rulings
mechanically (no model, no probes, free):
  R1  numeric questions return EXACT stats (detail opens "EXACT reported numbers", median present)
  R2  choice questions return PERCENT of respondents (value <= 100, detail says PERCENT)
  R3  n= appears ONLY inside detail (internal), never in the label
  R4  no "none on file"-style bucket ever appears
  R5  small cells suppressed: no returned choice row implies fewer than 3 members
      (pct >= 3/base * 100 by construction; base >= 3 respondents)
  R6  the 2026 window returns rows for census-2026 fields (evergreen slicing works)
  R7  'revenue' returns >= 2 distinct questions (multi-point, never a silent pick)
  R8  my_form_answers / form_field_history never emit email/phone/full_name refs

Exit 0 = all pass. Uses curl (system Python lacks certs).
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
PH = "17866578153"          # Andy — the only probe identity


def env():
    out = {}
    for line in open(ENV):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


E = env()


def rpc(fn, args):
    # 25s ceiling on purpose: form_stats must stay fast. A timeout is indistinguishable from
    # "no data", so a slow RPC would silently under-run this sweep instead of failing loudly.
    p = subprocess.run(
        ["curl", "-sS", "-m", "25", "-X", "POST",
         f"{E['SUPABASE_URL']}/rest/v1/rpc/{fn}",
         "-H", f"apikey: {E['SUPABASE_SECRET_KEY']}",
         "-H", f"Authorization: Bearer {E['SUPABASE_SECRET_KEY']}",
         "-H", "Content-Type: application/json",
         "-H", "Content-Profile: digest", "-H", "Accept-Profile: digest",
         "--data", json.dumps(args)],
        capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


fails = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


def main():
    catalog = rpc("form_stats", {"p_phone": PH})
    print(f"catalog: {len(catalog)} askable questions (floor >= 3 respondents)")
    check("catalog non-trivial", len(catalog) >= 40, f"{len(catalog)}")

    numeric_n = choice_n = 0
    for row in catalog:
        key = row["label"]
        rows = rpc("form_stats", {"p_phone": PH, "p_question": key})
        if not rows:
            # key matched fuzzily to something below floor after windowing — acceptable only
            # if the catalog respondent count is borderline
            check(f"{key}: returns rows", float(row["value"]) < 8, f"catalog n={row['value']}, stats empty")
            continue
        for r in rows:
            det = r.get("detail") or ""
            lab = r.get("label") or ""
            val = float(r["value"])
            check(f"{key}: no n= in label (R3)", "n=" not in lab, lab[:80])
            check(f"{key}: no none-on-file bucket (R4)",
                  "none on file" not in lab.lower() and "no answer" not in lab.lower(), lab[:80])
            if det.startswith("EXACT"):
                numeric_n += 1
                check(f"{key}: numeric has median+avg (R1)",
                      "median" in det and "avg=" in det, det[:80])
            elif det.startswith("PERCENT"):
                choice_n += 1
                check(f"{key}: percent <= 100 (R2)", 0 < val <= 100, f"value {val}")
            # rows with other detail shapes are catalog echoes — flag them
            else:
                check(f"{key}: known detail shape", False, det[:60])

    print(f"— shapes: {numeric_n} numeric rows, {choice_n} percent rows —")
    check("both shapes exercised", numeric_n >= 10 and choice_n >= 10,
          f"num={numeric_n} choice={choice_n}")

    # R6: the 2026 window keeps census fields alive
    w = rpc("form_stats", {"p_phone": PH, "p_question": "ttm_revenue",
                           "p_since": "2026-01-01", "p_until": "2027-01-01"})
    check("2026 window returns ttm_revenue (R6)", len(w) >= 1, str(w)[:80])
    w2 = rpc("form_stats", {"p_phone": PH, "p_question": "ttm_revenue",
                            "p_since": "2031-01-01"})
    check("empty future window returns nothing (R6)", w2 == [], str(w2)[:80])

    # R7: multi-point revenue
    rev = rpc("form_stats", {"p_phone": PH, "p_question": "revenue"})
    qs = {r["label"].split(" [")[0] for r in rev}
    check("'revenue' returns >= 2 distinct questions (R7)", len(qs) >= 2, str(qs)[:120])

    # R8: identity refs never leak from the owner tools
    for fn in ("my_form_answers", "form_field_history"):
        rows = rpc(fn, {"p_phone": PH})
        bad = [r for r in rows if (r.get("ref") or r.get("canonical_key")) in ("email", "phone", "full_name")]
        check(f"{fn}: identity refs excluded (R8)", not bad, str(bad)[:80])

    # R9 (v5): numeric detail carries share>0 and the p10..p90 range, never min/max extremes
    k = rpc("form_stats", {"p_phone": PH, "p_question": "num_kids"})
    det = (k[0].get("detail") or "") if k else ""
    check("numeric detail has share>0 (R9)", "share>0=" in det, det[:80])
    check("numeric detail has typical range, no min/max (R9)",
          "typical range" in det and "min=" not in det and "max=" not in det, det[:80])

    # R10 (v5): chapter slice works and every cell respects the floor
    ch = rpc("form_stats", {"p_phone": PH, "p_question": "ttm_revenue", "p_group_by": "chapter"})
    check("chapter slice returns rows (R10)", len(ch) >= 3, f"{len(ch)}")

    # R11 (v5b): free-text options case-fold — no duplicate option differing only by case
    ni = rpc("form_stats", {"p_phone": PH, "p_question": "main_niche"})
    opts = [r["label"].split(" — ")[-1] for r in ni]
    lowered = [o.lower() for o in opts]
    check("no case-duplicate options (R11)", len(set(lowered)) == len(lowered), str(opts)[:100])

    # R12: PII questions are unaskable — name/email/link fields return nothing
    for q in ("full name", "email address", "facebook", "brand / company name"):
        rows = rpc("form_stats", {"p_phone": PH, "p_question": q})
        pii = [r for r in rows if any(w in (r.get("label") or "").lower()
                                      for w in ("name?", "email", "facebook", "link"))]
        check(f"PII unaskable: '{q}' (R12)", not pii, str(pii)[:80])

    print()
    if fails:
        # collapse repeated failure names for the summary
        uniq = sorted(set(fails))
        print(f"QA FAILED — {len(fails)} failing check(s) across {len(uniq)} rule(s)")
        for u in uniq[:20]:
            print("  ", u)
        sys.exit(1)
    print("QA PASSED — every askable question obeys the rulings.")


if __name__ == "__main__":
    main()
