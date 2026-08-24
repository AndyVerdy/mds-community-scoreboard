#!/usr/bin/env python3
"""Fixwave 16 — every remaining fixable fail in one wave, so one run measures them all.

48 fails left after wave 15. #135 (SQL, shipped) covers the partner/name group. This wave takes
the rest that have a mechanism; what is left after it is blocked or is Andy's call.

 Plan Request
   P1 · "Call me Eugene please" was classified `action`, which routes to the ticket offer. A form
        of address is not a task she cannot do — she just uses it. (6060)

 Answer Merge
   S9  · HARD CAP people lists at 10 in the payload. She listed 12 Austin names off a 13-total
         answer even with the cap stamp present; a stamp is advice, a truncated array is not. (6217, 6275)
   S10 · a member card that carries a facebook_link must go out WITH it. (6066, 6110)
   S11 · when event_who returns counts and withholds names, give the COUNT and the REAL gate
         (not registered) — never a blanket "I don't share attendee lists". (6266, 6267, 6094)

 Answer Seed
   R9  · never claim you cannot check something you have a tool for — registrations especially. (6498)
   R10 · one review or one call is a THIN base; say so before summarising sentiment. (6040)
   R11 · location is self-declared and stored by city/state — say so when counting by country. (6503, 6460)
   R12 · third-party documentation (Amazon's own setup steps) is not MDS data; label it. (6382)
   R13 · drafting a message for a member to forward is allowed — write it addressed to the named
         person, with their requested opening. Refusing to BE someone is right; refusing to WRITE
         for them is not. (6407)

 Format Reply
   F1 · strip markdown headings — "## Week of..." renders literally on WhatsApp. (6192)

 NOT here: the gate's hard-stop clamp (6093, 6483, 7045). It fires when claims were actually
 raised, so silencing it would weaken the safety backstop for three questions. Left alone.

  python3 scripts/olivia_loop/apply_fixwave16_2026-08-24.py [--dry]
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

    # ---- P1: a form of address is not an "action" ------------------------------------
    pr = nodes["Plan Request"]; cp = pr["parameters"]["jsCode"]
    a_p1 = """} else if (intent === 'action') {"""
    n_p1 = """} else if (intent === 'action'
           && /^\\s*(please\\s+)?(call|address)\\s+me\\s+|^\\s*my name is\\b|^\\s*i(?:'m| am)\\s+called\\b/i.test(rawText)) {
  // fixwave 16 (P1): "Call me Eugene please" was classified `action` and routed to the ticket
  // offer — "that one is not something I can do myself". Using the name someone asks you to use
  // is not a task, and it is not a system write either. Answer it normally and just use the name.
  route = 'llm'; planPeriod = 'address_form'; intent = 'question';
} else if (intent === 'action') {"""
    cp = sub(cp, a_p1, n_p1, "P1 form of address")
    node_check(cp, "Plan Request"); pr["parameters"]["jsCode"] = cp

    # ---- Answer Merge stamps ---------------------------------------------------------
    mg = nodes["Answer Merge"]; cm = mg["parameters"]["jsCode"]
    a_m = """        // S8 (fixwave 15) — the payload NOW carries the real total"""
    stamps = """        // S9 (fixwave 16) — HARD CAP. 6217 listed twelve Austin names off a payload of ten with
        // the cap stamp sitting right there, and 6275 dumped a whole niche when asked for "all".
        // A stamp is advice; a shortened array is not. Ten rows go in, the true total is stated
        // by S8, and there is physically nothing else to list.
        const _people16 = _arr8.filter(x => x && typeof x === 'object' && (x.full_name || x.name));
        if (_people16.length > 10 && _people16.length === _arr8.length) {
          const _kept = _arr8.slice(0, 10);
          try { body = JSON.stringify(_kept); } catch (e) {}
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this list was cut to 10 on purpose ('
            + _people16.length + ' matched). Name these ten and no others — there are no further '
            + 'names available to you on this turn, so do not add any from earlier turns or memory.';
        }
        // S10 (fixwave 16) — a card that carries a Facebook link goes out WITH it (6066, 6110).
        const _card16 = _arr8.find(x => x && typeof x === 'object' && x.facebook_link);
        if (_card16) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: this person\\'s own Facebook link is in '
            + 'the payload. Include it when you describe them — a card without their link is an '
            + 'incomplete answer. Add what they have actually contributed if the evidence shows it.';
        }
        // S11 (fixwave 16) — an attendee result that withholds names still carries the COUNT and
        // the real reason. 6266/6267 answered "I don't share attendee lists", a blanket claim that
        // is not true: a registered asker does get names. Say which gate is shut. (R2's rule, but
        // these are the turns where it kept slipping, so the payload says it too.)
        if (_p8 && typeof _p8 === 'object' && !Array.isArray(_p8)
            && (_p8.total_going != null || _p8.matched_total != null) && _p8.ok === false) {
          body = body + NL + 'MILLIE — DETERMINISTIC NOTE: names are withheld here because the '
            + 'ASKER is not registered for this event — that is the reason, and it is the one to '
            + 'give. Never say attendee lists are something you never share: a registered member '
            + 'does get them. Give the counts you were handed and name the real gate.';
        }
"""
    cm = sub(cm, a_m, stamps + a_m, "wave16 merge stamps")
    node_check(cm, "Answer Merge"); mg["parameters"]["jsCode"] = cm

    # ---- Answer Seed rules -----------------------------------------------------------
    seed = nodes["Answer Seed"]; cs = seed["parameters"]["jsCode"]
    a_s = """  'A PAST MEMBER IS FINDABLE - WHEN AND WHY THEY LEFT IS NOT"""
    rules = """  'NEVER SAY YOU CANNOT CHECK SOMETHING YOU CAN. You hold event registrations, member records, chats, posts, partner deals and the library. "I have no way to see who is registered", "that is not something I can check for another member", "I do not have a way to look that up" are false whenever a lookup exists - and they read as broken. If a thing is WITHHELD by a rule, say the rule (they are not registered, it is not a field we hold); if a lookup came back empty, say it came back empty. Never invent a missing capability to explain either one.',
  'A THIN BASE IS PART OF THE ANSWER. One review, one call, two comments - say so before you characterise anything. "Mixed" off two opinions and "mixed" off forty are different claims, and the member cannot tell which they are getting unless you say. Give the size of what you are standing on.',
  'LOCATION IS SELF-DECLARED AND STORED BY CITY AND STATE. There is no country field: a country count is resolved from the cities and states members typed themselves, so it can miss people who left it blank or wrote it oddly. When you give a country count, say that in one short clause - and give the number anyway rather than dodging it.',
  'SOMEONE ELSE\\'S DOCUMENTATION IS NOT MDS DATA. When the real answer is a third party\\'s own process - Amazon\\'s SP-API setup, a marketplace policy, a tax form - lead with what MDS members actually said about doing it, and label the generic steps as that platform\\'s own documentation rather than something MDS holds. Never present a vendor walkthrough as community knowledge.',
  'YOU MAY WRITE A MESSAGE FOR SOMEONE TO SEND. If a member asks you to draft a reply for another person - "answer this for Dan", "write it addressed to Michael", "use this intro line" - do it: address it to that person, use the opening they asked for, and keep every source and link. What you never do is CLAIM to be someone else, sign as them, or say a message was sent when it was not. Refusing to be another person is right; refusing to write on their behalf is not, and it leaves the member with nothing.',
"""
    cs = sub(cs, a_s, rules + a_s, "wave16 seed rules")
    node_check(cs, "Answer Seed"); seed["parameters"]["jsCode"] = cs

    # ---- F1: strip markdown headings --------------------------------------------------
    fr = nodes["Format Reply"]; cf = fr["parameters"]["jsCode"]
    a_f = """text = text.replace(/\\*\\*(.+?)\\*\\*/g, '*$1*');"""
    n_f = a_f + """
// fixwave 16 (F1): markdown HEADINGS render literally on WhatsApp too — the MDS Trading digest
// went out with "## MDS Trading -- Week of 2026-08-17" and "### Macro Thesis" as visible hashes.
// Drop the hashes and keep the line as bold, which is what a heading means here.
text = text.replace(/^\\s{0,3}#{1,6}\\s+(.+?)\\s*$/gm, '*$1*');"""
    cf = sub(cf, a_f, n_f, "F1 markdown headings")
    node_check(cf, "Format Reply"); fr["parameters"]["jsCode"] = cf

    if dry:
        print("DRY RUN — all anchors hit, node --check clean on 4 nodes.")
        return
    put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {})}
    api("PUT", f"/workflows/{STAGING}", put)
    api("POST", f"/workflows/{STAGING}/deactivate")
    api("POST", f"/workflows/{STAGING}/activate")
    after = api("GET", f"/workflows/{STAGING}")
    n2 = {n["name"]: n for n in after["nodes"]}
    for node, marker in (("Plan Request", "fixwave 16 (P1)"), ("Answer Merge", "S9 (fixwave 16)"),
                         ("Answer Seed", "NEVER SAY YOU CANNOT CHECK"), ("Format Reply", "fixwave 16 (F1)")):
        assert marker in n2[node]["parameters"]["jsCode"], f"{node} did not persist"
    print("APPLIED + bounced. versionId", after.get("versionId"))

main()
