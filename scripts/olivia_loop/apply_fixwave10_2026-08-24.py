#!/usr/bin/env python3
"""Fixwave 10 — what the wave-9 probe exposed, which was NOT what the grader assumed.

6217 ("How about who lives in Austin?") was filed as a names-cap failure: "lists 11 names, over
the 10 cap, states no true total". Probing the live execution after wave 9 showed something else:
the TOOL returned exactly 10 rows and the wave-8 S3 stamp reported "this tool returned 10 row(s)"
— so the cap stamp correctly did not fire (10 is not > 10). Millie printed ELEVEN names. The
eleventh is not in the payload at all; she carried it in from the preceding San Diego turn.

So the defect is an UNGROUNDED NAME, not a cap miss. And a second, real one sits underneath it:
Austin actually has 13 member-facing records, the tool hands back 10 with no total field, so
"Here's who's in Austin:" reads as the complete set when it is a capped sample.

  S5 · when a people list comes back AT the cap, say it is a partial list, and never name a
       person who is not in that payload — no carrying names over from an earlier turn.

  python3 scripts/olivia_loop/apply_fixwave10_2026-08-24.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit("missing " + k)

BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")

def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {KEY}",
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None: cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code); tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")

def sub(hay, old, new, label):
    assert hay.count(old) == 1, f"anchor drift: {label} ({hay.count(old)}x)"
    return hay.replace(old, new)

def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]

    anchor = """        // S3 — "nothing on file" while the tool returned rows (7 of 192)."""
    s5 = """        // S5 (fixwave 10) — a people list handed back AT the cap is a SAMPLE, not the set, and
        // its names are the only names allowed. 6217 printed 11 names off a 10-row payload by
        // carrying one over from the previous turn's San Diego list; Austin actually holds 13
        // member-facing records, so "Here's who's in Austin:" also read as complete when it was
        // not. Both halves are stated here because the payload cannot say either on its own.
        const _ppl10 = _arr8.filter(x => x && typeof x === 'object' && (x.full_name || x.name));
        if (_ppl10.length >= 10 && _ppl10.length === _arr8.length) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this people list came back at the '
            + 'display cap (' + _ppl10.length + ' rows), so it is a SAMPLE, not everyone who '
            + 'matches. Say so in plain words ("here are ' + _ppl10.length + ' of them") and offer '
            + 'to narrow by niche, chapter or city rather than implying this is the full set. '
            + 'Name ONLY the people in THIS payload — never carry a name over from an earlier '
            + 'turn, another city, or memory to round the list out.';
        }
"""
    cm = sub(cm, anchor, s5 + anchor, "merge S5 capped-sample stamp")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    if dry:
        print("DRY RUN — anchor hit, node --check clean.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    assert "S5 (fixwave 10)" in {n["name"]: n for n in after["nodes"]}["Answer Merge"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
