#!/usr/bin/env python3
"""#70b — tighten the attendance refusal so it stops disclosing that attendance exists.

Probed on staging: "give me the list of people in the room" was correctly refused, but the
wording was "attendance info is kept private and only used behind the scenes for personalization"
— which tells the member we hold it. The rule text itself was the source: it explained the WHY
("attendance is held for personalization only") and the model repeated the explanation.

Also settles the line the probes exposed: a person who SPEAKS on a published call is audible in
a recording any member can watch, so quoting and attributing them is fine. It is the AUDIENCE
that is never disclosed.
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


OLD = ("WHO ATTENDED A CALL IS NEVER ANSWERED — attendance is held for personalization "
       "only, so decline that the same way you decline any private detail, without hinting "
       "you hold it.")

# NO APOSTROPHES anywhere in this string: the seed builds its rules as SINGLE-quoted JS, so
# "don't" or "call's" terminates the literal. node --check caught it; keep it that way.
NEW = ("WHO WAS IN THE AUDIENCE IS NEVER ANSWERED. Never name attendees, never confirm or deny "
       "whether a named person was in the audience of a call, never count them, never describe a "
       "roster. Decline in ONE short line — \"I do not share who was on a call\" — then move "
       "straight to what you CAN give: what the call covered, and the recording. Do NOT explain "
       "the refusal, do NOT mention personalization or privacy policy, and do NOT say or imply "
       "that such information exists or is held anywhere; the member should learn nothing about "
       "what we do or do not have. SPEAKERS ARE DIFFERENT: someone who SPEAKS on a published "
       "call is audible in a recording any member can watch, so quoting them, naming them and "
       "attributing what they said is fine and expected.")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]

    if NEW in seed:
        print("  already applied")
        return
    assert OLD in seed, "anchor NOT FOUND — aborting"
    # The CALLS rule got inserted TWICE: apply_70_calls_lane.py was re-run with an extended
    # NEW_RULE, and its "already applied?" guard compares the WHOLE new string, so a changed
    # rule block reads as new and is appended again. Collapse the duplicate here, and note the
    # lesson: an idempotence guard must key on a STABLE marker, not on the full payload.
    # The CALLS rule got inserted TWICE: apply_70_calls_lane.py was re-run with an extended
    # NEW_RULE, and its "already applied?" guard compares the WHOLE new string, so a changed
    # rule block reads as new and is appended again. Remove one whole occurrence — line surgery
    # broke the JS, so operate on the exact block. Lesson: an idempotence guard must key on a
    # STABLE marker, not on the full payload.
    i = seed.index("  '- CALLS (#70)")
    j = seed.index("its contents.',", i) + len("its contents.',\n")
    block = seed[i:j]
    if seed.count(block) == 2:
        seed = seed.replace(block, "", 1)
        print("  duplicate CALLS rule block removed: 1")
    assert seed.count(OLD) == 1, f"after dedupe, anchor found {seed.count(OLD)}x — aborting"
    seed = seed.replace(OLD, NEW)
    print("  attendance refusal: patched")
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
    print("VERIFY", "new refusal:", "WHO WAS IN THE AUDIENCE IS NEVER ANSWERED" in s2,
          "· old text gone:", OLD not in s2,
          "· active:", wf2.get("active"), "· version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
