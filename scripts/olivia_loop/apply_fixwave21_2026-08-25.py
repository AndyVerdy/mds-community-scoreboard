#!/usr/bin/env python3
"""Fixwave 21 — the five regressions part 2 of #145 found, each traced to its own cause first.

  R1 · 6105 "cost segregation study services" (was 9) → "Sorry - I could not generate an answer just now."
       NOT a rule bug. Execution 109771 carries a **529** from the model API: `Answer Claude` has
       retryOnFail with maxTries 3 / 2000ms, all three tries landed inside the same overload window,
       and `Answer Parse` surfaced the failure honestly as that sentence. Fix: ride out a short
       overload — maxTries 3 → 5, waitBetweenTries 2000 → 5000ms. Worst case adds ~15s to a turn
       that was going to fail anyway.

  R2 · 7052 "Has anyone used Cuttable?" (was 9) → the gate's hard-stop clamp.
       Execution 109574: two regenerations, both blocked by ONE claim -
       "UNTESTED: Process has ZERO member reviews in the partner directory, and your draft presents it
       like an endorsement". That is a LABELLING objection, not a false statement, and the clamp threw
       away a good sourced answer over it. Fix: at the clamp, if every surviving claim is non-factual
       (UNTESTED · OFF-TOPIC · MISSING SOURCE · PLACE COVERAGE · LANGUAGE · PROMISE · IDENTITY-ANSWER),
       ship the draft instead of the canned line — and when an UNTESTED claim is among them, append the
       untested caveat deterministically so the protection survives. Everything that means something
       FALSE or LEAKING (unsupported claims, fabricated links, COUNT, IDENTITY, INTERNALS, FAKE ACK,
       ID LEAK, INVENTED SELF-CORRECTION, STATUS, GATE) keeps the hard stop untouched.

  R3 · 6353 "grrr, give me all cyprus based then pleas" (was 9) → the same clamp, but the gate was RIGHT.
       Execution 109723: blocked twice on "Tanase Tudor - Tude listed as Baia-Mare, Cyprus — evidence
       shows Baia-Mare, Judetul Maramures (Romania, not Cyprus)". A real factual error; blocking it was
       correct. What was wrong is what the member then read: a blanket "couldn't verify enough of the
       details", which reads as "she can't see anything". Fix: the hard-stop line now says plainly that
       ONE detail failed verification, that the rest existed, and what to do next — without naming
       internals.

  R4 · 6200 "hello did you see my message" (was 9) → she searched the CORPUS for a message from him and
       reported none found, discarding the open thread. Fix: a nudge with no new content is answered
       from the conversation itself, never by searching for the member's own message.

  R5 · 6088 "What kind of food do they sell" (was 8) → bound a referent-less "they" to an unrelated
       Ivan Ong line about edamame. The wave-8 R1 rule covers wrong referents but not the case where the
       antecedent is ABSENT; the model filled the hole from search. Fix: an absent antecedent is a
       reportable state, and evidence found by searching never becomes the referent.

  python3 scripts/olivia_loop/apply_fixwave21_2026-08-25.py [--dry]
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
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def node_check(code, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(code)
        tmp = fh.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED ({label}):\n{chk.stderr}"
    print(f"  node --check OK ({label})")


def sub(hay, old, new, label):
    assert hay.count(old) == 1, f"anchor drift: {label} ({hay.count(old)}x)"
    return hay.replace(old, new)


# ---- R2 + R3: the clamp ---------------------------------------------------------------
GATE_OLD = """if (attempts >= 2) {
  return finalize("I looked into that, but I couldn't verify enough of the details against MDS data to give you a solid answer — I'd rather say that than guess. If you can narrow it down, I'll check again.", { gate: 'blocked', gate_claims: claims });
}"""

GATE_NEW = """if (attempts >= 2) {
  // fixwave 21 (#145 part 2) — THE CLAMP NO LONGER THROWS AWAY AN ANSWER OVER A LABEL.
  // 7052 (exec 109574) was blocked twice by one claim: "UNTESTED: Process has ZERO member reviews
  // ... your draft presents it like an endorsement" — a labelling objection, not a false statement,
  // and a fully sourced answer was replaced by the canned line. A claim that means something FALSE
  // or LEAKING still hard-stops: unsupported claims, fabricated links, COUNT, IDENTITY, INTERNALS,
  // INTERNALS-SHAPE, STATUS, GATE, FAKE ACKNOWLEDGEMENT, INTERNAL ID LEAK, INVENTED SELF-CORRECTION.
  // 6353 (exec 109723) is the case that MUST keep stopping: "listed as Baia-Mare, Cyprus — evidence
  // shows ... Romania, not Cyprus". The gate was right there; only what the member reads changes.
  const SOFT_RE = /^(UNTESTED|OFF-TOPIC|MISSING SOURCE|PLACE COVERAGE|LANGUAGE|PROMISE|IDENTITY-ANSWER)\\b/;
  const _soft = claims.every(function (c) { return SOFT_RE.test(String(c || '')); });
  if (_soft && String(answerText || '').trim()) {
    let _out = answerText;
    if (claims.some(function (c) { return /^UNTESTED\\b/.test(String(c || '')); })) {
      _out = _out + NL + NL + '_One note: some of the partners above have no member reviews on file '
        + 'yet — treat those as untested rather than member-vetted._';
    }
    return finalize(_out, { gate: 'pass-clamp-soft', gate_claims: claims });
  }
  return finalize("I had an answer for you, but one of the details in it did not check out against MDS data — "
    + "so I would rather not send something I cannot stand behind. The rest of it is there: ask me for a "
    + "narrower slice (one name, one chat, one date range) and I will verify that piece directly.",
    { gate: 'blocked', gate_claims: claims });
}"""

# ---- R4 + R5: Answer Seed rules --------------------------------------------------------
SEED_ANCHOR = ("  'ANSWER THE THING ON THE TABLE. When the member says yes, \"that one\", \"the second\", "
               "\"those\", or corrects you, the subject is whatever YOU just put in front of them")

SEED_NEW = """  'A NUDGE IS NOT A SEARCH. "did you see my message", "hello?", "you there?", "any update?" carry no new question - they are a poke at the thread you are already in. Answer from THIS conversation: say where things stand, repeat the thing you last offered or owed them, and go on. NEVER search the corpus for a message from the member and NEVER report that you cannot find one - their message is the one you are reading. If the thread genuinely has nothing outstanding, say that in a line and ask what they want next.',
  'AN ABSENT REFERENT IS AN ANSWER. If "they", "it", "this" or "them" has no antecedent in YOUR OWN previous turn, that is the finding - say so plainly and name what the previous turn was actually about, or ask which of two candidates they mean. Do NOT go looking for a subject that fits the words: a person or product you find by searching is not what they were pointing at, and presenting one as if it were is a fabrication. Bind only to what is already on the table.',
""" + SEED_ANCHOR


def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    print(f"staging versionId {wf.get('versionId')} · {len(wf['nodes'])} nodes")
    nodes = {n["name"]: n for n in wf["nodes"]}

    gv = nodes["Gate Verdict"]
    cg = sub(gv["parameters"]["jsCode"], GATE_OLD, GATE_NEW, "R2/R3 clamp")
    node_check(cg, "Gate Verdict")
    gv["parameters"]["jsCode"] = cg

    seed = nodes["Answer Seed"]
    cs = sub(seed["parameters"]["jsCode"], SEED_ANCHOR, SEED_NEW, "R4/R5 seed rules")
    node_check(cs, "Answer Seed")
    seed["parameters"]["jsCode"] = cs

    # R1 — ride out a short model-API overload (529) instead of handing it to the member.
    ac = nodes["Answer Claude"]
    before = (ac.get("maxTries"), ac.get("waitBetweenTries"))
    ac["maxTries"] = 5
    ac["waitBetweenTries"] = 5000
    print(f"  Answer Claude retries {before} -> (5, 5000)")

    if dry:
        print("DRY RUN — nothing written")
        return 0

    payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
               "settings": wf.get("settings") or {}}
    out = api("PUT", f"/workflows/{STAGING}", payload)
    print("applied · new versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
