#!/usr/bin/env python3
"""The Summit schedule lane — retrieval + the visibility rule, in one place.

    python3 scripts/event_lane.py --self-test
    python3 scripts/event_lane.py --phone 17866578153 --op next --at 2026-08-23T13:00+08:00
    python3 scripts/event_lane.py --phone 17866578153 --op where --q "welcome dinner"
    python3 scripts/event_lane.py --phone 17866578153 --op speaker --q "himmel"

Why this exists as a script first: `Answer Tool` in n8n POSTs to
/rest/v1/rpc/<tool_name> against the `digest` schema, so today Olivia can only
call Postgres functions. Andy's rule is that the logic sits OUTSIDE Supabase.
Those two do not meet, so the rule is written here — proven against live data —
and this file is the body that gets ported into whichever home we pick.

THE RULE, written once:
    visible(person, activity) =
        (person's participant types at THIS event) ∩ (activity's audience) ≠ ∅
     OR person is on the activity's grant list
An unchecked box only blocks someone whose every type is unchecked.
Times are stored as instants and always rendered in the event's own zone.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"


def env():
    out = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k] = v.strip().strip('"').strip("'")
    return out["SUPABASE_URL"].rstrip("/"), out["SUPABASE_SECRET_KEY"]


URL, KEY = env()


def get(path, profile="event"):
    cmd = ["curl", "-s", "-m", "30", f"{URL}/rest/v1/{path}",
           "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
           "-H", f"Accept-Profile: {profile}"]
    raw = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(raw or "[]")
    except json.JSONDecodeError:
        sys.exit(f"bad response for {path}: {raw[:300]}")


# --------------------------------------------------------------- identity
def person_for_phone(phone):
    """WhatsApp gives a phone. The spine is phone -> member -> registration
    email -> event person. A member who is not registered is not an attendee,
    and sees the public agenda only."""
    digits = "".join(c for c in phone if c.isdigit())
    rows = get(f"members?select=at_member_id,email,name&phone=eq.{digits}", profile="digest")
    if not rows:
        return None
    m = rows[0]
    people = get(f"people?select=id,name,email,at_member_id&at_member_id=eq.{m['at_member_id']}")
    if not people:
        people = get(f"people?select=id,name,email,at_member_id&email=eq.{m.get('email','')}")
    return people[0] if people else None


def types_for(person_id, event_id):
    rows = get("attendees?select=participant_type_id,participant_types(role)"
               f"&person_id=eq.{person_id}&event_id=eq.{event_id}")
    return {r["participant_types"]["role"] for r in rows if r.get("participant_types")}


def grants_for(person_id):
    return {r["activity_id"] for r in get(f"activity_person_grants?select=activity_id&person_id=eq.{person_id}")}


# -------------------------------------------------------------- retrieval
def load_activities(event_id):
    return get("activities?select=id,name,short_description,starts_at,ends_at,status,"
               "locations(name,address,place_id,latitude,longitude),"
               "activity_audience(participant_types(role))"
               f"&event_id=eq.{event_id}&status=eq.published&order=starts_at")


def visible(act, my_types, my_grants):
    audience = {a["participant_types"]["role"] for a in (act.get("activity_audience") or [])
                if a.get("participant_types")}
    return bool(audience & my_types) or act["id"] in my_grants


def place_of(act, sessions_by_activity):
    """Activity location first; else the distinct place of its sessions; else
    unknown — stated, never guessed."""
    loc = act.get("locations")
    if loc:
        return loc
    places = {json.dumps(s["rooms"]["locations"], sort_keys=True)
              for s in sessions_by_activity.get(act["id"], [])
              if s.get("rooms") and s["rooms"].get("locations")}
    return json.loads(places.pop()) if len(places) == 1 else None


def maps_url(loc):
    if not loc:
        return None
    if loc.get("place_id"):
        return ("https://www.google.com/maps/search/?api=1"
                f"&query={loc.get('latitude')},{loc.get('longitude')}"
                f"&query_place_id={loc['place_id']}")
    return None


def fmt(ts, tz):
    return datetime.fromisoformat(ts).astimezone(ZoneInfo(tz)).strftime("%a %-d %b, %-I:%M%p").replace("AM", "am").replace("PM", "pm")


# ------------------------------------------------------------------- ops
def run(op, phone, q=None, at=None):
    ev = get("events?select=id,title,timezone&order=starts_at.desc&limit=1")[0]
    tz = ev["timezone"]
    person = person_for_phone(phone)
    if person:
        my_types = types_for(person["id"], ev["id"])
        my_grants = grants_for(person["id"])
    else:
        person, my_types, my_grants = {"name": None}, set(), set()
    if not my_types:
        # Andy's ruling: a member who is not attending still gets the PUBLIC
        # AGENDA. Public agenda = what a plain Member attendee would see, with
        # no grant-gated extras. Never the staff or partner rows.
        my_types, my_grants = {"Member"}, set()
        person["viewing"] = "public agenda (not registered for this event)"
    acts = [a for a in load_activities(ev["id"]) if visible(a, my_types, my_grants)]

    sessions = get("sessions?select=id,title,activity_id,starts_at,ends_at,"
                   "rooms(name,locations(name,address,place_id,latitude,longitude)),"
                   f"session_speakers(people(name))&event_id=eq.{ev['id']}&order=starts_at")
    by_act = {}
    for s in sessions:
        by_act.setdefault(s.get("activity_id"), []).append(s)

    def card(a):
        loc = place_of(a, by_act)
        return {"name": a["name"], "when": fmt(a["starts_at"], tz) + " " + tz.split("/")[-1] + " time",
                "blurb": a.get("short_description"),
                "where": (loc or {}).get("name"), "address": (loc or {}).get("address"),
                "maps": maps_url(loc)}

    if op == "next":
        now = datetime.fromisoformat(at) if at else datetime.now(ZoneInfo(tz))
        nxt = [a for a in acts if datetime.fromisoformat(a["starts_at"]) > now]
        return {"person": person["name"], "types": sorted(my_types),
                "next": [card(a) for a in nxt[:3]]}

    if op == "day":
        day = (at or datetime.now(ZoneInfo(tz)).date().isoformat())[:10]
        same = [a for a in acts
                if datetime.fromisoformat(a["starts_at"]).astimezone(ZoneInfo(tz)).date().isoformat() == day]
        return {"person": person["name"], "day": day, "count": len(same),
                "activities": [card(a) for a in same]}

    if op == "where":
        hit = [a for a in acts if q.lower() in a["name"].lower()]
        if not hit:
            return {"answer": None, "reason": "no activity by that name is visible to this person"}
        c = card(hit[0])
        if not c["where"]:
            c["note"] = "no location recorded for this activity"
        return c

    if op == "speaker":
        out = []
        for s in sessions:
            names = [sp["people"]["name"] for sp in (s.get("session_speakers") or []) if sp.get("people")]
            if not any(q.lower() in (n or "").lower() for n in names):
                continue
            parent = next((a for a in acts if a["id"] == s.get("activity_id")), None)
            if s.get("activity_id") and not parent:
                continue                      # parent not visible to this person
            if not s.get("activity_id"):
                continue                      # orphan session: no audience, never surfaced
            room = s.get("rooms") or {}
            loc = room.get("locations") or {}
            out.append({"speakers": names, "title": s["title"],
                        "when": fmt(s["starts_at"], tz) + " " + tz.split("/")[-1] + " time",
                        "room": room.get("name"), "where": loc.get("name"),
                        "address": loc.get("address"), "maps": maps_url(loc)})
        return {"sessions": out}

    return {"error": f"unknown op {op}"}


def self_test():
    ok = True
    ev = get("events?select=id,timezone&limit=1")[0]
    people = get("people?select=id,name,email&limit=400")
    by_email = {p["email"]: p for p in people}

    def visible_count(pid, day):
        my_types = types_for(pid, ev["id"])
        my_grants = grants_for(pid)
        acts = [a for a in load_activities(ev["id"]) if visible(a, my_types, my_grants)]
        return sum(1 for a in acts
                   if datetime.fromisoformat(a["starts_at"]).astimezone(
                       ZoneInfo(ev["timezone"])).date().isoformat() == day)

    # a plain Member with no grants on day one
    plain = None
    for p in people:
        t = types_for(p["id"], ev["id"])
        if t == {"Member"} and not grants_for(p["id"]):
            plain = p
            break
    # 2026-08-23 refresh (#113): GroupOS added two new day-one activities —
    # "Arrive & Check-In to the Hotel at 3PM" and "Explore Singapore Beyond the
    # Summit" — to both views; was 6/7, now 7/8. The relationship that matters
    # (grantee = plain Member + exactly the Women's Lunch) still holds.
    n = visible_count(plain["id"], "2026-08-23") if plain else -1
    print(f"  plain Member day one = {n} (expect 7) — {plain['name'] if plain else 'none found'}")
    ok &= (n == 7)

    k = by_email.get("kimberly.cruickshanks@gmail.com")
    n2 = visible_count(k["id"], "2026-08-23") if k else -1
    print(f"  Women's Lunch grantee day one = {n2} (expect 8)")
    ok &= (n2 == 8)

    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--phone")
    ap.add_argument("--op", default="next")
    ap.add_argument("--q")
    ap.add_argument("--at")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    print(json.dumps(run(a.op, a.phone, a.q, a.at), indent=1, ensure_ascii=False))
