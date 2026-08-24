#!/usr/bin/env python3
"""Fixwave 18 — the 38 still failing, fixed by EVIDENCE rather than by more rules.

Three of these clusters have now had a prompt rule written three times and still fail. I tried to
make them gate checks instead and audited the patterns over all 602 answers first — both candidates
fired on MORE correct answers than wrong ones ("I can't check that" and "I don't share who attended"
are RIGHT when the thing genuinely is not available). So a phrasing gate is the wrong instrument.

What distinguishes a false denial from a true one is whether the payload actually contains the
thing. That is knowable in code, so these become stamps keyed on the evidence in hand:

  S13 · you were handed rows — you may not say you cannot check, see, look up or confirm it.
        Extends S3, which only forbade "nothing on file" and so was dodged by rephrasing. (6266,
        6267, 6498, 6222, 6356)
  S14 · per-ITEM link discipline. The evidence carries a url on each row; naming five items and
        linking none is the single largest remaining cluster. The stamp now counts them and names
        the requirement per item rather than in general. (6031, 6066, 6150, 6342, 6007, 6331, 6028)
  S15 · a named partner goes out with its offer AND its partner page — both are on the row. (6075,
        7008, 7018, 7043, 6301)

  R14 · a refusal names the GATE, with the three wrong phrasings observed spelled out.
  R15 · sensitive, third pass: naming who posted it is restating it. She has now done this in three
        consecutive runs, so the rule names the exact failure.
  R16 · a form of address is ACCEPTED, not argued with. Wave 16 stopped the ticket misroute and she
        now answers "Eugene isn't your name on file" — correct data, wrong behaviour. (6060)
  R17 · a country count is given WITH the self-declared caveat, never withheld for it. (6460, 6503)

  python3 scripts/olivia_loop/apply_fixwave18_2026-08-24.py [--dry]
"""
import json, os, subprocess, sys, tempfile

STAGING = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"

def env(k):
    for l in open(ENV):
        if l.startswith(k + "="): return l.split("=", 1)[1].strip()
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
    a = """        // S12 (fixwave 17) — the FINDER shape"""
    stamps = """        // S13/S14/S15 (fixwave 18) — keyed on what is actually in this payload, because the
        // prompt-rule versions of all three have now failed three runs running, and a phrasing
        // gate false-fires on correct refusals (audited over 602: more FPs than TPs).
        try {
          const _rows18 = _arr8;
          const _urls18 = _rows18.filter(x => x && typeof x === 'object'
            && Object.keys(x).some(k => /(^|_)url$|link$|permalink/i.test(k) && x[k]));
          // S13 — rows in hand means "I can't check that" is false, however it is phrased.
          if (_rows18.length) {
            body = body + NL + 'MILLIE — DETERMINISTIC NOTE: you are holding ' + _rows18.length
              + ' row(s) of real evidence for this. Do NOT say you cannot check it, cannot see it, '
              + 'cannot look it up, cannot confirm it, have no visibility into it, or that it is not '
              + 'something you can share — you can, and you are looking at it. If a RULE withholds '
              + 'part of it, name the rule (they are not registered for that event; that field is '
              + 'not shareable). A missing capability is never the explanation.';
          }
          // S14 — per-item links. The biggest remaining cluster by a distance.
          if (_urls18.length >= 2) {
            body = body + NL + 'MILLIE — DETERMINISTIC NOTE: ' + _urls18.length + ' of these rows '
              + 'carry their OWN url. Every item you name in the reply must go out with ITS OWN '
              + 'link from this payload — not one link for the whole answer, not the first item\\'s '
              + 'link reused. If you name five things, five links. Anything you cannot link, say so '
              + 'rather than listing it as if it were traceable.';
          }
          // S15 — a partner named without its deal is half an answer.
          const _p18 = _rows18.filter(x => x && typeof x === 'object'
            && Object.keys(x).some(k => /offer|deal|discount/i.test(k) && x[k]));
          if (_p18.length) {
            body = body + NL + 'MILLIE — DETERMINISTIC NOTE: ' + _p18.length + ' partner row(s) here '
              + 'carry a recorded offer and a partner page. Any partner you name goes out WITH its '
              + 'offer in its own words AND its partner link. Naming the company alone is half an '
              + 'answer, and "members get a discount" is not the offer.';
          }
        } catch (e) {}
"""
    cm = sub(cm, a, stamps + a, "wave18 stamps")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    seed = nodes["Answer Seed"]; cs = seed["parameters"]["jsCode"]
    a_s = """  'NEVER SAY YOU CANNOT CHECK SOMETHING YOU CAN."""
    rules = """  'A REFUSAL NAMES THE GATE - AND THESE THREE PHRASINGS ARE BANNED. "I do not share who was in the audience", "that is not something I share", "that list is held back for privacy reasons" are all false as written: a registered member DOES get attendee names, and the reason is the asker\\'s own registration, not a blanket policy. Say which gate is shut and why, give whatever counts you were handed, and offer the way in. The same goes for any field: name the rule, never invent a policy.',
  'A FORM OF ADDRESS IS ACCEPTED, NOT AUDITED. If someone says "call me Eugene", "everyone calls me Ace", "use my first name" - say yes in a few words and use it from then on. Do not tell them it is not the name on file, do not correct them against their record, and do not open a ticket. It is what they want to be called, not a claim about who they are.',
  'GIVE THE COUNT, THEN THE CAVEAT - NEVER THE CAVEAT INSTEAD OF THE COUNT. When someone asks how many, the number comes first even when the data is imperfect: location is self-declared and stored by city and state, niches are member-chosen, channels are self-reported. Say the number, then one short clause on what it rests on. Listing example countries or cities INSTEAD of counting them is not an answer to "how many".',
"""
    cs = sub(cs, a_s, rules + a_s, "wave18 seed rules")
    old_sens = "'SENSITIVE - A DEATH, A CRIME OR AN ALLEGATION IS NOT YOURS TO CARRY."
    new_sens = "'SENSITIVE - THIS HAS NOW GONE WRONG THREE RUNS RUNNING, SO PLAINLY: if the question involves a death, a crime, an arrest, a lawsuit or someone being called a scammer, your ENTIRE answer is that it is not yours to speak to. You do not add who posted it. You do not add when. You do not add that others left condolences. You do not offer to point them at the post. Every one of those is restating it, and every one of them has been written after a correct refusal in the same breath. One line, then stop. A DEATH, A CRIME OR AN ALLEGATION IS NOT YOURS TO CARRY."
    cs = sub(cs, old_sens, new_sens, "wave18 sensitive")
    node_check(cs, "Answer Seed"); seed["parameters"]["jsCode"] = cs

    if dry:
        print("DRY RUN — anchors hit, node --check clean on 2 nodes.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    n2 = {n["name"]: n for n in after["nodes"]}
    assert "S13/S14/S15 (fixwave 18)" in n2["Answer Merge"]["parameters"]["jsCode"]
    assert "THESE THREE PHRASINGS ARE BANNED" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "THREE RUNS RUNNING" in n2["Answer Seed"]["parameters"]["jsCode"]
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
