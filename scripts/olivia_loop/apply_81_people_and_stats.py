#!/usr/bin/env python3
"""#81 — answer the question we already have the data for, and stop calling gaps limits.

From two live WhatsApp sessions (Andy, 2026-08-11, he rated follow-ups 3/10):
  "who is the best match to me?"           -> "I can't rank or single out one person
                                              as the best match - that's not something
                                              I can judge", then a list by country.
  "Give me 3 people I must talk to"        -> "I really can't rank people or tell you
                                              who you must talk to."
  "break down this 20%, how many M vs W?"  -> "that breakdown isn't something I can
                                              split by gender", plus a third repetition
                                              of a refusal he had moved on from.

None of that was policy. NO rule forbids ranking members - the refusal was emergent,
because event_who returned full_name + state and nothing else, and form_stats had no
gender dimension. Both tools were fixed first (event_who fit_reason; form_stats
p_group_by=gender). This script teaches the loop to USE them, and forbids the habit of
describing a thin tool result as a personal limit.

Five patches, Answer Seed ONLY.
"""
import json, os, subprocess, sys, tempfile

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


def patch(text, old, new, where, marker):
    if marker in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


# ---- A: event_who advertises what it now returns ---------------------------------------
OLD_EW = ("{ name: 'event_who', description: 'Who is going to ONE event: confirmed member "
          "attendees (names + city/state) and total count.',")
NEW_EW = ("{ name: 'event_who', description: 'Who is going to ONE event: confirmed member "
          "attendees with city, niche, sales channels and fit_reason - why THIS attendee fits "
          "THE ASKER, computed per asker (#81). Rows come back best-fit FIRST, so the top rows "
          "ARE the answer to who-should-I-meet. Only the strongest matches carry a fit_reason; "
          "an attendee without one is a weaker match, not an error. Never quote scores or ranks.',")

# ---- B: form_stats advertises gender ----------------------------------------------------
OLD_GB = "p_group_by: str('optional slice: country | state | niche | rev_band'),"
NEW_GB = "p_group_by: str('optional slice: country | state | niche | rev_band | gender | chapter'),"

# ---- C: the rules -----------------------------------------------------------------------
OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"
NEW_RULES = (
    "  '- WHO SHOULD I TALK TO (#81): who-is-the-best-match / who-must-I-meet / who-is-good-for-me "
    "about an event is a QUESTION YOU ANSWER, not one you decline. Call event_who and lead with the "
    "attendees carrying fit_reason, saying the reason in plain words. Give the NUMBER asked for - "
    "three means three names, not a disclaimer. Location alone is the weakest reason: use it only "
    "when nothing better exists, and say that is what it is. Never quote a score, rank or match "
    "percentage.',\n"
    "  '- NEVER CALL A DATA GAP A LIMIT (#81): if a tool came back thin, name what is missing in one "
    "short clause and move straight to what you CAN answer. Never say you are unable to judge, not "
    "able to rank, or that something is not something you do, when the truth is a tool returned "
    "little. Never OPEN a reply with I cannot - lead with the part you can answer.',\n"
    "  '- DECLINE ONCE (#81): once you have declined a request, never repeat that refusal on a later "
    "turn. If the member moves on to a different question - a count, a percentage, a breakdown - "
    "answer THAT question on its own merits and say nothing further about the earlier decline.',\n"
    "  '- LONG ROSTERS (#81): never dump more than 12 names in one reply. Lead with the few that "
    "carry a reason, group the rest by what makes them useful (city, niche), give the total, and "
    "offer the remainder as ONE concrete next step.',\n"
    "  '- CROSS-CUT STATS (#81): form_stats slices by country, state, niche, rev_band, chapter AND "
    "gender. Breaking an existing figure down by any of those is a normal question - call form_stats "
    "with p_group_by instead of saying the split is not tracked. The tool suppresses small groups "
    "itself, so quote what it returns and nothing more.',\n"
)

# ---- (no D) ------------------------------------------------------------------------------
# A fourth patch was drafted to teach #80's OFFER_TAIL_RE the roster offer ("want the rest of
# the list"), then dropped: #80's binding only fires when the previous message linked a VIDEO,
# so a roster offer could never bind through it, and the seed ALREADY carries
# "- DELIVERING THE REST OF A LIST", which re-calls the same tool on yes / the whole list /
# show me the rest. Format Reply's own OFFER_TAIL already matches "want the rest" for buttons.


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]

    seed = patch(seed, OLD_EW, NEW_EW, "event_who schema", "best-fit FIRST")
    seed = patch(seed, OLD_GB, NEW_GB, "form_stats p_group_by gender", "rev_band | gender")
    seed = patch(seed, OLD_RULE_TAIL, NEW_RULES + OLD_RULE_TAIL, "rules x5",
                 "WHO SHOULD I TALK TO")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED on Answer Seed:\n{chk.stderr}"
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
    print("PUT + bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    s2 = {n["name"]: n for n in wf2["nodes"]}["Answer Seed"]["parameters"]["jsCode"]
    for marker in ("best-fit FIRST", "rev_band | gender", "WHO SHOULD I TALK TO",
                   "NEVER CALL A DATA GAP A LIMIT", "DECLINE ONCE", "LONG ROSTERS",
                   "CROSS-CUT STATS"):
        assert marker in s2, f"marker {marker!r} missing after PUT"
        print(f"  verified: {marker!r}")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
