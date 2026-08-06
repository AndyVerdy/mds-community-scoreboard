#!/usr/bin/env python3
"""#20b Census evergreen mechanics — apply to STAGING (on top of apply_20_census_lane).

Andy's rulings 2026-08-06: never volunteer respondent counts · a "revenue" ask returns SEVERAL
revenue data points (TTM + projected + prior + YoY), never a silent pick · the census is
EVERGREEN — "2026 census" means answers GIVEN in 2026 (p_since/p_until), same person answers
yearly · cross-form canonical keys · per-field change-over-time via form_field_history.

DB shipped: form_field_map (canonical keys = DATA) · form_stats v2 (multi-ref, windowed,
cross-form) · form_field_history (self-only event stream).
"""
import json, subprocess, sys, tempfile, os

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}",
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json",
           "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def patch(text, old, new, where):
    if new in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


OLD_FORM_STATS = """  { name: 'form_stats', description: 'AGGREGATE stats over what members answered on MDS forms — THE source for census questions ("avg revenue per Census 2026", "how many members have kids", "where do members manufacture"). Returns counts/averages/medians/distributions ONLY - never a member\\'s individual answer, never names; groups smaller than 3 members are suppressed by the database. detail carries n=, median, min, max - lead with the median when the spread is wide. Call with NO p_question first if unsure what the form asks. Absent answers mean the question was never shown to that member (logic jumps) - UNKNOWN, never "No".',
    input_schema: S({ p_question: str('the question - a few words from it ("TTM revenue", "kids", "manufacture") or its ref; omit to get the catalog of askable questions'),
                      p_form_id: str('which form: DFeK5yop = Annual Census 2026 (default), I409BFlj = legacy Standard census, DXs5mhZn = legacy MDSonly census, FsVHzNN9 = New Member Application v3'),
                      p_group_by: str('optional slice: country | state | niche | rev_band') }) },
"""

NEW_FORM_STATS = """  { name: 'form_stats', description: 'AGGREGATE stats over what members answered on MDS forms — THE source for census/survey questions. Returns EVERY matching question (a "revenue" ask returns TTM + projected + prior-year + YoY rows together - present the relevant ones or ask which they meant, never silently pick one). Aggregates ONLY - never an individual\\'s answer, never names; cells under 3 members are suppressed in the database. The census is EVERGREEN: "the 2026 census" means answers GIVEN in 2026 - use p_since/p_until (2026 census = 2026-01-01..2027-01-01; "Aug census" = that month). Omit p_form_id to unify the same question across ALL forms (canonical keys); set it only when the member names one form. detail carries median/avg/min/max and n= - n is INTERNAL sample-size honesty: NEVER say how many members answered unless the question itself asks for a count. Lead with the median on wide spreads. Absent answers = question never shown (logic jumps) = UNKNOWN, never "No". Call with NO p_question for the catalog.',
    input_schema: S({ p_question: str('the question - a few words ("revenue", "kids", "manufacture") or a canonical key (ttm_revenue, projected_revenue, prior_year_revenue, revenue_yoy_pct, main_niche, num_products, num_brands, num_kids, pct_amazon/dtc/tiktok/retail)'),
                      p_form_id: str('ONLY when the member names a form: DFeK5yop = Annual Census 2026, I409BFlj = legacy Standard census, DXs5mhZn = legacy MDSonly census, FsVHzNN9 = New Member Application v3; omit = all forms unified'),
                      p_group_by: str('optional slice: country | state | niche | rev_band'),
                      p_since: str('YYYY-MM-DD, answers submitted on/after - "2026 census" = 2026-01-01'),
                      p_until: str('YYYY-MM-DD exclusive - "2026 census" = 2027-01-01') }) },
  { name: 'form_field_history', description: 'The ASKER\\'s OWN answers to one field over TIME, across every form and year ("how has my revenue changed", "what did I answer about kids each year"). Self only. Rows are ordered oldest-to-newest - the change story.',
    input_schema: S({ p_field: str('canonical key (ttm_revenue, num_kids, num_products, main_niche...) or words from the question; omit for all fields') }) },
"""

OLD_RULE = """  '- CENSUS AND FORM DATA (#20): any census/survey aggregate ask ("avg revenue per the census", "how many members...") = form_stats, NEVER content_search - the chats and Facebook do NOT hold census results. A member\\'s own answers = my_form_answers. NEVER state another member\\'s individual form answer even if asked point-blank - aggregates and distributions only; the n= in detail is your sample-size honesty. A question someone did not answer was likely never SHOWN to them (logic jumps) - unknown, never "No".',
"""

NEW_RULE = """  '- CENSUS AND FORM DATA (#20): any census/survey aggregate ask ("avg revenue per the census", "how many members...") = form_stats, NEVER content_search - the chats and Facebook do NOT hold census results. A member\\'s own answers = my_form_answers; their own change-over-time = form_field_history. NEVER state another member\\'s individual form answer even if asked point-blank - aggregates and distributions only. NEVER volunteer how many members responded ("among the N members who answered") - n= in detail is INTERNAL; speak counts only when the question itself is a count ("how many members have kids"). When several questions match (revenue: TTM, projected, prior year, YoY), give the relevant data points or ask which they meant - never silently pick one. Period words map to the window: "2026 census" p_since=2026-01-01 p_until=2027-01-01; "Q3" and month names likewise. A question someone did not answer was likely never SHOWN to them (logic jumps) - unknown, never "No".',
"""


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed, OLD_FORM_STATS, NEW_FORM_STATS, "Answer Seed: form_stats v2 + form_field_history")
    seed = patch(seed, OLD_RULE, NEW_RULE, "Answer Seed: evergreen census rules")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
    print("node --check: OK")

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    s2 = next(n for n in wf2["nodes"] if n["name"] == "Answer Seed")["parameters"]["jsCode"]
    print("VERIFY", "evergreen:", "EVERGREEN" in s2,
          "history tool:", "'form_field_history'" in s2,
          "count rule:", "NEVER volunteer how many members responded" in s2,
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
