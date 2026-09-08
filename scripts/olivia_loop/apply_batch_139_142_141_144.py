#!/usr/bin/env python3
"""Apply the verification-pass batch (#139 · #142 · #141 · #144) to STAGING in ONE PUT and ONE bounce.

The four single-ticket scripts each GET the live graph, patch one node and PUT + bounce. Run one after
another they would bounce staging four times and leave four versionIds; this runner composes their
`patch_code()` functions on one GET and ships one version:

  Gate Verdict  #139 apply_139_partner_link_repair.patch_code  ->  #142 apply_142_identity_precision.patch_code
  Plan Request  #141 apply_141_pronoun_subject.patch_code      ->  #144 apply_144_events_lane_carry.patch_code

  python3 scripts/olivia_loop/apply_batch_139_142_141_144.py --dry-run DIR   # writes both patched nodes, no n8n write
  python3 scripts/olivia_loop/apply_batch_139_142_141_144.py                 # edits STAGING, one bounce

Idempotent per ticket (each patch_code() skips on its own marker). The proof standard is unchanged: after
the apply, dump the live nodes and run test_175 + test_142 on Gate Verdict, test_141 + test_144 + test_143 +
test_174 on Plan Request (see the board's #139/#142/#141/#144 close blocks).
"""
import importlib.util, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STAGING_ID = "bqHstPDi84uOhTCJ"


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    saved = sys.argv
    sys.argv = [name]           # the modules read argv only inside main(); keep them from seeing ours
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


PLAN = [
    # lap 2 (found on staging b39b31ab, 2026-09-08 01:00Z): #175b (the #1c event repair) and #141b (the
    # pronoun carry on the member-card lane) ride the same runner — each patch_code() skips on its own marker.
    ("Gate Verdict", ["apply_139_partner_link_repair", "apply_142_identity_precision", "apply_175b_event_repair_precision", "apply_139b_partner_ask_guard"], "Gate_Verdict.js"),
    ("Plan Request", ["apply_141_pronoun_subject", "apply_144_events_lane_carry", "apply_141b_topic_carry"], "Plan_Request.js"),
]


def main():
    dry = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run" else None
    mods = {n: load(n) for _, names, _ in PLAN for n in names}
    api = mods["apply_139_partner_link_repair"].api
    node_check = mods["apply_139_partner_link_repair"].node_check
    wf = api("GET", f"/workflows/{STAGING_ID}")
    if wf.get("id") != STAGING_ID:
        sys.exit(f"GET failed: {json.dumps(wf)[:300]}")
    print(f"staging {STAGING_ID} versionId {wf.get('versionId')} nodes {len(wf['nodes'])}")
    any_change = False
    for node_name, names, fname in PLAN:
        node = next((n for n in wf["nodes"] if n["name"] == node_name), None)
        if node is None:
            sys.exit(f"ABORT: node {node_name} not found")
        code = node["parameters"]["jsCode"]
        applied = []
        for n in names:
            code, changed = mods[n].patch_code(code)
            applied.append(f"{n.split('_')[1]}:{'applied' if changed else 'present'}")
            any_change = any_change or changed
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {node_name}: node --check failed\n{err}")
        node["parameters"]["jsCode"] = code
        print(f"  {node_name}: {' '.join(applied)}, node --check OK")
        if dry:
            os.makedirs(dry, exist_ok=True)
            open(os.path.join(dry, fname), "w").write(code)
            print(f"  wrote {os.path.join(dry, fname)}")
    if dry:
        print("dry run: nothing written to n8n")
        return
    if not any_change:
        print("nothing to do")
        return
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok, versionId", r.get("versionId"))
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"), "versionId", r.get("versionId"))


if __name__ == "__main__":
    main()
