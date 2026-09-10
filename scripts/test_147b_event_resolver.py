"""#147 second half — the event resolver must resolve on PLACE, not only words in the title.
`python3 scripts/test_147b_event_resolver.py`

`event_who` resolved an event with `bool_and(name ilike '%word%')`, so a member asking "who should I
meet in Seattle" could only reach events with Seattle IN THE TITLE. Measured 2026-09-10: 'seattle'
resolved to **"Private Experience - Dinner at Ltd Edition Sushi Seattle" from 2024-09-17**, while three
MDS events in Seattle on 2026-09-22/23 — twelve days away, Registration Open — were unreachable because
the city only appears in their `city_state`. `event_lookup` has always matched city_state / location /
app_city; `event_who` was the odd one out.

The rule: match the same place fields, and keep the existing preference for running-then-upcoming, so a
place question lands on the event a member could actually walk into.
"""
import json, subprocess, sys
from datetime import datetime, timezone

ENV = "/Users/Born/mds-digest-web/.env.local"
PHONE = "17866578153"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def resolved(term):
    """(event_name, starts_at) that event_who picked for this term."""
    p = subprocess.run(
        ["curl", "-sS", "-m", "90", "-X", "POST", f"{BASE}/rpc/event_who",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
         "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
         "-H", "Content-Type: application/json",
         "--data-binary", json.dumps({"p_phone": PHONE, "p_event": term, "p_limit": 3})],
        capture_output=True, text=True)
    try:
        rows = json.loads(p.stdout) if p.stdout.strip() else []
    except json.JSONDecodeError:
        return None, None
    if not isinstance(rows, list) or not rows:
        return None, None
    return rows[0].get("event_name"), rows[0].get("starts_at")


fails = 0


def check(label, ok, detail):
    global fails
    if not ok:
        fails += 1
    print(f"{'ok  ' if ok else 'FAIL'}  {label}: {detail}")


name, starts = resolved("seattle")
future = False
if starts:
    future = datetime.fromisoformat(starts.replace("Z", "+00:00")) > datetime.now(timezone.utc)
check("a place question resolves to an event a member can still attend",
      bool(name) and future, f"{name} @ {starts}")
check("and not the 2024 sushi dinner that merely has the city in its title",
      name != "Private Experience - Dinner at Ltd Edition Sushi Seattle", f"{name}")

for term, want in (("singapore", "Summit Singapore"),
                   ("inspire", "Inspire 2027"),
                   ("las vegas", "Las Vegas")):
    name, starts = resolved(term)
    check(f"'{term}' still resolves as before", bool(name) and want in name, f"{name} @ {starts}")

print("all green" if not fails else f"{fails} failing")
sys.exit(1 if fails else 0)
