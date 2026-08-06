#!/usr/bin/env python3
"""#20 Census into the warehouse — apply to STAGING.

DB shipped: digest.form_responses (raw Typeform ledger, 5 forms, daily GH-Action sync) +
form_answers_latest (latest answer per member x form x ref) + two gated doors:
  form_stats       — aggregates only, n<3 suppressed, optional group_by country/state/niche/rev_band
  my_form_answers  — the ASKER's own submissions, self-only by construction

This teaches the loop the two tools + the census rules (aggregates-only exposure,
conditional-absence is UNKNOWN never No, census-2026 asks go to form_stats not content_search).
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


TOOLS_ADD = """  { name: 'form_stats', description: 'AGGREGATE stats over what members answered on MDS forms — THE source for census questions ("avg revenue per Census 2026", "how many members have kids", "where do members manufacture"). Returns counts/averages/medians/distributions ONLY - never a member\\'s individual answer, never names; groups smaller than 3 members are suppressed by the database. detail carries n=, median, min, max - lead with the median when the spread is wide. Call with NO p_question first if unsure what the form asks. Absent answers mean the question was never shown to that member (logic jumps) - UNKNOWN, never "No".',
    input_schema: S({ p_question: str('the question - a few words from it ("TTM revenue", "kids", "manufacture") or its ref; omit to get the catalog of askable questions'),
                      p_form_id: str('which form: DFeK5yop = Annual Census 2026 (default), I409BFlj = legacy Standard census, DXs5mhZn = legacy MDSonly census, FsVHzNN9 = New Member Application v3'),
                      p_group_by: str('optional slice: country | state | niche | rev_band') }) },
  { name: 'my_form_answers', description: 'The ASKER\\'s OWN form submissions - census and application answers exactly as they gave them ("what did I say on my census?", "what did I put on my application?"). Self only - never anyone else\\'s. p_form_id narrows to one form (DFeK5yop = Census 2026).',
    input_schema: S({ p_form_id: str('optional: one form id') }) },
"""

RULE_ADD = """  '- CENSUS AND FORM DATA (#20): any census/survey aggregate ask ("avg revenue per the census", "how many members...") = form_stats, NEVER content_search - the chats and Facebook do NOT hold census results. A member\\'s own answers = my_form_answers. NEVER state another member\\'s individual form answer even if asked point-blank - aggregates and distributions only; the n= in detail is your sample-size honesty. A question someone did not answer was likely never SHOWN to them (logic jumps) - unknown, never "No".',
"""


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed,
        "  { name: 'multi_source', description:",
        TOOLS_ADD + "  { name: 'multi_source', description:",
        "Answer Seed tools: form_stats + my_form_answers")
    seed = patch(seed,
        "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',",
        RULE_ADD + "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',",
        "Answer Seed rules: census lane")
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
    print("VERIFY", "form_stats:", "'form_stats'" in s2,
          "my_form_answers:", "'my_form_answers'" in s2,
          "census rule:", "CENSUS AND FORM DATA (#20)" in s2,
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
