"""#147 registration authority contract — `python3 scripts/test_147_registration_authority.py`.

One function answers "is this member registered", and it answers TWO different questions without
letting them contradict each other:

  has_ticket    the Airtable roster, read from the Supabase mirror (Andy 2026-09-10: "AT roster, but
                we need to read the data from Supa, not AT since at has bottle necks"). This is what
                GATES who-to-meet and attendee names.
  is_attending  the GroupOS attendee export. This is what drives a PERSONAL AGENDA. A speaker or a
                partner attends without buying a member ticket; stripping their agenda to make one
                number tidy would be a regression for a real person.

`is_registered()` stays the roster boolean, so every existing gate keeps its meaning and the leak
gate's non-attendee control (Andy's own record) stays intact.

Subjects are live rows for the Singapore Summit (roster `recrATwhUDA55iQN5`, GroupOS
`689cfd00f1f12d7791cf9525`), picked because they sit on opposite sides of the 36-member disagreement
this ticket measured.
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
EVENT = "recrATwhUDA55iQN5"
ROSTER_MEMBER = "recLKVEU44AWg4KCx"     # Omer Ege — on the roster AND in the GroupOS export
GROUPOS_ONLY = "recnZgt8J4LAWxWCp"      # Chirag Singla — partner/speaker, attends, no member ticket
GATE_CONTROL = "recCUUw8iiUnJjac1"      # Andy — the leak gate's deliberate non-attendee


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def rpc(fn, body):
    p = subprocess.run(
        ["curl", "-sS", "-m", "60", "-X", "POST", f"{BASE}/rpc/{fn}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
         "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
         "-H", "Content-Type: application/json", "--data-binary", json.dumps(body)],
        capture_output=True, text=True)
    try:
        return json.loads(p.stdout) if p.stdout.strip() else None
    except json.JSONDecodeError:
        return {"_raw": p.stdout[:200]}


def row(member):
    r = rpc("registration_status_v2", {"p_member": member, "p_event": EVENT})
    if isinstance(r, list):
        return r[0] if r else {}
    return r if isinstance(r, dict) else {}


fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    if not ok:
        fails += 1
    print(f"{'ok  ' if ok else 'FAIL'}  {label}: {got!r} (want {want!r})")


r = row(ROSTER_MEMBER)
check("roster member has_ticket", r.get("has_ticket"), True)
check("roster member is_attending", r.get("is_attending"), True)
check("roster member keeps the legacy is_registered column", r.get("is_registered"), True)

g = row(GROUPOS_ONLY)
check("partner/speaker has_ticket (roster is the authority)", g.get("has_ticket"), False)
check("partner/speaker is_attending (GroupOS drives their agenda)", g.get("is_attending"), True)
check("partner/speaker legacy is_registered stays roster-shaped", g.get("is_registered"), False)

c = row(GATE_CONTROL)
check("gate control has_ticket", c.get("has_ticket"), False)
check("gate control is_registered", c.get("is_registered"), False)

print(f"{'ok  ' if 'roster_synced_at' in r else 'FAIL'}  freshness reported: roster_synced_at present")
if "roster_synced_at" not in r:
    fails += 1
print(f"{'ok  ' if 'roster_stale_days' in r else 'FAIL'}  freshness reported: roster_stale_days present")
if "roster_stale_days" not in r:
    fails += 1

# the gating boolean must not drift from the roster facet
for label, member, want in (("roster member", ROSTER_MEMBER, True),
                            ("partner/speaker", GROUPOS_ONLY, False),
                            ("gate control", GATE_CONTROL, False)):
    got = rpc("is_registered", {"p_member": member, "p_event": EVENT})
    check(f"is_registered() stays roster-only for the {label}", got, want)

print("all green" if not fails else f"{fails} failing")
sys.exit(1 if fails else 0)
