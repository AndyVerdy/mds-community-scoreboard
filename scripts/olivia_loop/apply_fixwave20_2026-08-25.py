#!/usr/bin/env python3
"""Fixwave 20 — the three REGRESSIONS the #145 no-regression run found.

These are not new bank C failures: all three questions PASSED on 2026-08-23 and got worse
after waves 7-19. Each fix is aimed at the mechanism that made it worse, not at the symptom.

  R1 · 6083 "Would he make a good member interviewer" (was 9, now fails)
       Root cause: the TRUST & CHARACTER rule enumerates a CLOSED list of ask types -
       "trust, work with, hire or pay". A role-suitability ask ("would he make a good X")
       is outside that list, so the rule never engaged and the draft gave a hedged read:
       "That could make him a solid voice for evaluating other supplements sellers, but
       that's my read on his profile". Fix: the trigger becomes the SHAPE of the ask (any
       judgment of a person's fitness, character or quality), and the hedge is named as a
       breach in its own right - labelling a verdict "my read" is still a verdict.

  R2 · 6213 "one main takeaway from the logistics channel" (was 8, now fails)
       Root cause: S1/S14 count only the rows that HAVE a url and then demand a link per
       cited item. A WhatsApp chat digest has no public url, so the model satisfied the
       stamp by borrowing an unrelated row's Facebook permalink (verified real: post
       10009755805794497, a 2025-10-07 post) and then retracted it in the same sentence -
       "actually, that digest is WhatsApp-only with no direct link". Fix: S16 counts the
       rows that have NO url and says out loud that those items are named WITHOUT a link.
       The stamps could forbid borrowing but never told the model what the unlinkable rows
       were, so "cite one that does" read as "find any url in this payload".

  R3 · 6219 "Yeah total it up" (was 8, now fails)
       Root cause: the counting rule tells her to reconcile a number that differs from an
       earlier one and "say why it differs". Nothing tells her to attribute the other
       number to its SOURCE, so she attributed it to herself: "Correcting what I said
       earlier: the Texas count is 51, not 107" - no turn in that thread ever said 107
       (verified msg 50821: Texas 51). Fix: G9, deterministic. A self-correction sentence
       that names a number never said in this conversation regenerates.
       AUDITED over all 602 bank C answers PLUS the 134 #145 re-run answers, with each
       hit's real conversation history pulled from olivia_messages: 3 sentence-level hits,
       2 killed by the history condition (6050 "Top 5 members", 6015 "Helium 10"), 1 fire -
       6219, the real fail. Zero false positives.

  python3 scripts/olivia_loop/apply_fixwave20_2026-08-25.py [--dry]
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


# ---- R1 -----------------------------------------------------------------------------
SEED_OLD = ("'TRUST & CHARACTER: You have no vetting, trust ratings or background data on any "
            "member. If asked whether to trust, work with, hire or pay someone, say plainly you "
            "cannot judge that - never vouch for, endorse or imply a verdict about a person "
            '(no "the opposite", "seems legit", "you can trust him"). You may state neutral '
            "observable facts (their public profile, what they actually posted in the chats) "
            "WITHOUT framing it as an endorsement, and suggest they do their own due diligence.',")

SEED_NEW = ("'TRUST & CHARACTER: You have no vetting, trust ratings or background data on any "
            "member. ANY judgment of a person - whether to trust, work with, hire or pay them, and "
            "equally whether they would be GOOD AT or RIGHT FOR anything (a role, a panel, an "
            "interview, a speaking slot, a partnership, an introduction) - is one you cannot make. "
            "Say so plainly and stop; never vouch for, endorse or imply a verdict about a person "
            '(no "the opposite", "seems legit", "you can trust him", "he would be a solid X"). '
            'Labelling the verdict as your own opinion does not license it: "just my read", '
            '"could make him a good fit", "on paper he looks strong" are the same breach in a '
            "softer voice - a hedged verdict is still a verdict. You may state neutral observable "
            "facts (their public profile, what they actually posted in the chats) WITHOUT framing "
            "it as an endorsement, and suggest they do their own due diligence.',")

# ---- R2 -----------------------------------------------------------------------------
MERGE_ANCHOR = "        } catch (e) {}\n        // S12 (fixwave 17) — the FINDER shape:"

MERGE_NEW = """          // S16 (fixwave 20) — the rows that have NO url of their own. S1 and S14 count only
          // the LINKED rows and then demand a link per cited item, which is why 6213 borrowed an
          // unrelated Facebook permalink for a WhatsApp digest and retracted it in the same
          // sentence. Naming the unlinkable rows is what was missing: "cite one that does" read
          // as "find any url in this payload".
          const _nourl18 = _rows18.filter(x => x && typeof x === 'object'
            && !Object.keys(x).some(k => /(^|_)url$|link$|permalink/i.test(k) && x[k]));
          if (_nourl18.length && _urls18.length) {
            body = body + NL + 'MILLIE — DETERMINISTIC NOTE: ' + _nourl18.length + ' of these rows '
              + 'carry NO url at all (WhatsApp chat messages and chat digests have no public link). '
              + 'Name those WITHOUT a link and say so plainly if it matters — never hand one of them '
              + 'another row\\'s url, and never ship a link you then take back in the same breath. '
              + 'A link that does not belong to the thing you just named is worse than no link.';
          }
        } catch (e) {}
        // S12 (fixwave 17) — the FINDER shape:"""

# ---- R3 -----------------------------------------------------------------------------
GATE_ANCHOR = "if (!claims.length) {\n  const extra = {};"

GATE_NEW = """// fixwave 20 (G9) — A SELF-CORRECTION THAT CITES A NUMBER SHE NEVER SAID. 6219 answered
// "Correcting what I said earlier: the Texas count is 51, not 107" when no turn in that thread
// had ever said 107 (msg 50821 said 51). The counting rule tells her to reconcile numbers that
// differ and say why — it never told her to attribute the other number to its SOURCE, so she
// attributed it to herself and invented an error she had not made. Deterministic: take every
// sentence that frames itself as a correction of her own earlier answer, and check each number
// in it against the conversation history actually in front of her.
// AUDITED over all 602 bank C answers + the 134 #145 re-run answers, each hit checked against
// its real history from olivia_messages: 3 sentence hits, the history condition kills 2 of them
// ("Top 5 members" in 6050, "Helium 10" in 6015), 1 fires — 6219, a real fail. Zero FPs.
try {
  const _histG9 = String(($('Plan Request').first().json || {}).history_block || '')
    .replace(/,/g, '');
  if (_histG9) {
    const _sentG9 = String(answerText || '').match(
      /[^.!?\\n]*\\b(?:correcting|correction|i said earlier|i said before|earlier i said|i gave you|i told you|my earlier)\\b[^.!?\\n]*/ig) || [];
    const _ghost = [];
    _sentG9.forEach(function (s) {
      (s.match(/\\b\\d[\\d,]*(?:\\.\\d+)?\\b/g) || []).forEach(function (n) {
        const _n = n.replace(/,/g, '');
        if (_histG9.indexOf(_n) === -1 && _ghost.indexOf(n) === -1) { _ghost.push(n); }
      });
    });
    if (_ghost.length) {
      claims.push('INVENTED SELF-CORRECTION: the draft corrects itself over ' + _ghost.join(', ')
        + ' — a number that appears nowhere in this conversation. Do not tell the member you said '
        + 'something you never said. If a number from a tool differs from one you gave earlier, '
        + 'attribute each to WHAT PRODUCED IT (a state count vs a chapter-membership count), or '
        + 'simply give the correct number without inventing a prior mistake.');
    }
  }
} catch (e) {}

if (!claims.length) {
  const extra = {};"""


def main():
    dry = "--dry" in sys.argv
    wf = api("GET", f"/workflows/{STAGING}")
    print(f"staging versionId {wf.get('versionId')} · {len(wf['nodes'])} nodes")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]
    c = sub(seed["parameters"]["jsCode"], SEED_OLD, SEED_NEW, "R1 trust & character")
    node_check(c, "Answer Seed")
    seed["parameters"]["jsCode"] = c

    mg = nodes["Answer Merge"]
    cm = sub(mg["parameters"]["jsCode"], MERGE_ANCHOR, MERGE_NEW, "R2 S16 no-url stamp")
    node_check(cm, "Answer Merge")
    mg["parameters"]["jsCode"] = cm

    gv = nodes["Gate Verdict"]
    cg = sub(gv["parameters"]["jsCode"], GATE_ANCHOR, GATE_NEW, "R3 G9 invented self-correction")
    node_check(cg, "Gate Verdict")
    gv["parameters"]["jsCode"] = cg

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
