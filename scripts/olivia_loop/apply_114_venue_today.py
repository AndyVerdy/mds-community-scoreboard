#!/usr/bin/env python3
"""#114: Answer Seed passes relative days as WORDS, trusts now_at_venue at the venue.

Ian Sells asked "what's happening at the summit today?" from Singapore on his
Sunday and got Saturday's list: the seed anchors TODAY on US Eastern, and the
event_schedule tool description told the model to compute `at=YYYY-MM-DD`
itself. Tasks 1-2 (mds-digest-web, LIVE prod) made the schedule route resolve
at=today|tomorrow|yesterday|<weekday>|YYYY-MM-DD in the venue's own zone and
return now_at_venue/day_label/resolved_from on every answer. This script makes
the model pass the WORD instead of computing a date, and trust now_at_venue
over the US-Eastern TODAY line for anything happening at the Summit.

Three edits, all in node `Answer Seed`, each `old` exactly once (verified
2026-08-22): the op=day tool description, the TODAY anchor line, and a new
bullet inserted right after the existing PICK-THE-OP-BY-WHAT-THEY-NAMED bullet
(implemented as old=that whole line, new=that line + \\n + the new bullet, so
the "exactly once" assertion still holds after the insert).
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


EDITS = {
    "Answer Seed": [
        # Edit A — op=day tool description: stop telling the model to compute a date.
        ("day (one date, at=YYYY-MM-DD)",
         "day (one DAY - at=today | tomorrow | yesterday | a weekday name | "
         "YYYY-MM-DD. For today, tomorrow or a weekday pass the WORD, never a "
         "date you computed: the tool resolves it in the venue\\'s zone and "
         "you do not know what day it is there)"),
        # Edit B — the TODAY anchor line: carve out the venue exception.
        ("'TODAY is ' + today + ' (US Eastern). Anchor every past/upcoming "
         "judgment to this date.',",
         "'TODAY is ' + today + ' (US Eastern). Anchor every past/upcoming "
         "judgment to this date - EXCEPT at an in-person event: the venue can "
         "already be on the next calendar day (Singapore runs 12 hours ahead "
         "of Eastern). For anything at the Summit the day is what "
         "event_schedule returns in now_at_venue, never this line.',"),
        # Edit C — new bullet right after the PICK-THE-OP-BY-WHAT-THEY-NAMED
        # bullet: old is that whole existing line, new appends "\n" + the new
        # bullet, so the array grows by one element without disturbing the
        # "exactly once" assertion.
        ("  '- PICK THE OP BY WHAT THEY NAMED. They name an activity (welcome "
         "dinner, early mixer, check-in) -> op=where with q set to that name. "
         "They name a person -> op=speaker with q. They name a date -> "
         "op=day with at. Only when they name NOTHING is it op=next. Getting "
         "this wrong makes a listed activity look missing.',",
         "  '- PICK THE OP BY WHAT THEY NAMED. They name an activity (welcome "
         "dinner, early mixer, check-in) -> op=where with q set to that name. "
         "They name a person -> op=speaker with q. They name a date -> "
         "op=day with at. Only when they name NOTHING is it op=next. Getting "
         "this wrong makes a listed activity look missing.',\n"
         "  '- TODAY / TOMORROW / A WEEKDAY AT THE SUMMIT (#114): "
         "\\'what is happening today\\' is op=day with at=today; tomorrow is "
         "at=tomorrow; a weekday is at=monday (the word). NEVER turn a "
         "relative day into a date yourself - you anchor on US Eastern and "
         "the venue is a day ahead for half of every day; Ian Sells asked on "
         "his Sunday and got Saturday. Open the answer with the day the tool "
         "resolved (day_label) and trust now_at_venue over the TODAY line "
         "for anything at the venue.',"),
    ],
}


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    changed = 0
    for n in wf["nodes"]:
        if n["name"] not in EDITS:
            continue
        code = n["parameters"]["jsCode"]
        for old, new in EDITS[n["name"]]:
            c = code.count(old)
            if c != 1:
                sys.exit(f"ABORT {n['name']}: expected 1 occurrence, found {c}\n  {old[:90]}")
            code = code.replace(old, new)
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {n['name']}: node --check failed\n{err}")
        n["parameters"]["jsCode"] = code
        changed += 1
        print(f"  {n['name']}: {len(EDITS[n['name']])} replacements, node --check OK")
    if changed != 1:
        sys.exit(f"ABORT: expected 1 node changed, got {changed}")
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok")
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"))


if __name__ == "__main__":
    main()
