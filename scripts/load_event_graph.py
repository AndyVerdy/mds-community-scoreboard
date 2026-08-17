#!/usr/bin/env python3
"""Load a GroupOS event export into the `event` schema.

    python3 scripts/load_event_graph.py ~/Downloads/event_graph.json [--dry-run]

Rules this loader enforces, because the source cannot:
  * soft-deleted rows (isDelete) are never imported — the Singapore event was
    cloned from Milan 2025 and 41 of its 91 activities are Milan leftovers.
  * `accessRoles` is the audience. The legacy `member`/`speaker`/`partner`/
    `guest` booleans on the same document are stale and are ignored.
  * times arrive as local wall-clock strings with no zone ("08-23-2026",
    "02:30 PM"). They are converted to true instants using the event's own
    timezone; the raw strings are kept in source_* for audit only.
  * a person is one human keyed on lower(email). Two attendee rows for one
    email is two roles, not two people.
  * at_member_id is resolved from the registration email against
    digest.member_profiles. No match means NULL, never a guess.

Writes through PostgREST with the service key; `event` must be an exposed
schema. Idempotent — every table is upserted on its primary key.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime
from zoneinfo import ZoneInfo

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
CHUNK = 200


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_URL"].rstrip("/"), env["SUPABASE_SECRET_KEY"]


def rest(method, path, key, url, body=None, profile="event", extra_headers=()):
    cmd = ["curl", "-s", "-m", "60", "-w", "\n%{http_code}", "-X", method,
           f"{url}/rest/v1/{path}",
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json",
           "-H", f"Accept-Profile: {profile}", "-H", f"Content-Profile: {profile}"]
    for h in extra_headers:
        cmd += ["-H", h]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    raw, _, code = out.rpartition("\n")
    return int(code or 0), raw


def upsert(table, rows, key, url, dry):
    if not rows:
        return 0
    if dry:
        return len(rows)
    done = 0
    for i in range(0, len(rows), CHUNK):
        batch = rows[i:i + CHUNK]
        code, raw = rest("POST", table, key, url, batch,
                         extra_headers=["Prefer: resolution=merge-duplicates,return=minimal"])
        if code not in (200, 201, 204):
            sys.exit(f"{table}: HTTP {code}\n{raw[:600]}")
        done += len(batch)
    return done


# ---------------------------------------------------------------- helpers
def oid(x):
    return x.get("$oid") if isinstance(x, dict) else x


def live(rows):
    return [r for r in rows if not r.get("isDelete")]


def iana_zone(raw, default="Asia/Singapore"):
    """GroupOS stores a display LABEL, not an IANA name — the Singapore event
    reads "(UTC+08:00) Asia/Singapore Singapore Standard Time", and the API
    flags others with a `timezone_not_iana` warning. Pull the IANA name out of
    the label and prove it loads before trusting it."""
    for candidate in re.findall(r"[A-Za-z]+/[A-Za-z_]+", raw or ""):
        try:
            ZoneInfo(candidate)
            return candidate
        except Exception:
            continue
    print(f"  !! timezone {raw!r} yields no IANA zone — using {default}")
    return default


def to_instant(date_str, time_str, tz):
    """'08-23-2026' + '02:30 PM' -> aware UTC datetime. The whole timezone bug
    lives or dies here: the source number is LOCAL and is stamped as UTC
    everywhere upstream (digest.events_catalog.start_at is 8 hours wrong)."""
    if not date_str or not time_str:
        return None
    dt = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M %p")
    return dt.replace(tzinfo=ZoneInfo(tz)).isoformat()


def clean(s):
    return (s or "").strip() or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    url, key = load_env()
    d = json.load(open(args.path))
    ev = d["event"]
    event_id = oid(ev["_id"])
    tz = iana_zone(ev.get("timeZone"))
    print(f"event {event_id} · {ev.get('title')} · tz={tz}")

    acts, sess = live(d["activities"]), live(d["sessions"])
    rooms, locs = live(d["rooms"]), live(d["locations"])
    atts, ptypes = live(d["attendees"]), live(d["participantTypes"])
    users = d.get("users") or {}

    # ---------------------------------------------------------- people
    # Union of three sources: attendee rows (embedded user), the per-activity
    # grant lists, and session speakers. Keyed on lower(email); an email seen
    # twice under two ids keeps the first id and both attendee rows point at it.
    people, id_alias = OrderedDict(), {}   # email -> row ; source id -> canonical id

    def add_person(uid, name, email, city=None, country=None):
        email = (email or "").strip().lower()
        if not uid or not email:
            return None
        if email in people:
            id_alias[uid] = people[email]["id"]
        else:
            people[email] = {"id": uid, "name": clean(name), "email": email,
                             "city": clean(city), "country": clean(country),
                             "at_member_id": None}
            id_alias[uid] = uid
        return id_alias[uid]

    for a in atts:
        u = a.get("user")
        if isinstance(u, dict):
            add_person(oid(u.get("_id")), u.get("name"), u.get("email"),
                       u.get("city"), u.get("country"))
    for uid, u in users.items():
        add_person(uid, u.get("name"), u.get("email"), u.get("city"), u.get("country"))

    # resolve MDS membership by registration email, in batches
    emails = list(people)
    matched = 0
    for i in range(0, len(emails), 60):
        batch = emails[i:i + 60]
        quoted = ",".join('"%s"' % e.replace('"', '') for e in batch)
        code, raw = rest("GET", f"member_profiles?select=at_member_id,email&email=in.({quoted})",
                         key, url, profile="digest")
        if code == 200:
            for row in json.loads(raw or "[]"):
                e = (row.get("email") or "").lower()
                if e in people:
                    people[e]["at_member_id"] = row["at_member_id"]
                    matched += 1
    print(f"people {len(people)} · matched to an MDS member {matched} · unmatched {len(people)-matched}")

    # ------------------------------------------------- participant types
    used = {oid(r) for a in acts for r in (a.get("accessRoles") or [])}
    pt_rows, skipped_types = [], []
    for p in ptypes:
        pid = oid(p["_id"])
        if p.get("role") in ("New type", "TYPE") and pid not in used:
            skipped_types.append(p.get("role"))
            continue
        pt_rows.append({"id": pid, "event_id": event_id, "role": p["role"],
                        "is_default": bool(p.get("isDefault"))})
    if skipped_types:
        print(f"  skipped unreferenced test participant types: {skipped_types}")

    # ------------------------------------------------------------ places
    loc_rows = [{"id": oid(l["_id"]), "event_id": event_id, "name": l["name"].strip(),
                 "address": clean(l.get("address")), "city": clean(l.get("city")),
                 "country": clean(l.get("country")), "postal_code": clean(l.get("postalCode")),
                 "latitude": l.get("latitude") or None, "longitude": l.get("longitude") or None,
                 "place_id": clean(l.get("placeId")),
                 "image_url": (l.get("locationImages") or [None])[0],
                 "is_visible": l.get("locationVisible") is not False}
                for l in locs]
    known_locs = {r["id"] for r in loc_rows}
    room_rows = [{"id": oid(r["_id"]), "event_id": event_id,
                  "location_id": oid(r.get("location")), "name": r["name"].strip(),
                  "sort_order": r.get("order")}
                 for r in rooms if oid(r.get("location")) in known_locs]

    # -------------------------------------------------------- activities
    act_rows, audience, grants = [], [], []
    known_types = {r["id"] for r in pt_rows}
    for a in acts:
        start = to_instant(a.get("date"), a.get("startTime"), tz)
        end_date = a.get("endDate") if a.get("isEndOrNextDate") else a.get("date")
        end = to_instant(end_date or a.get("date"), a.get("endTime"), tz)
        if not start or not end:
            print(f"  !! skipping {a.get('name')!r}: unparseable time")
            continue
        if end <= start:
            print(f"  !! {a.get('name')!r} ends before it starts — check isEndOrNextDate")
            continue
        aid = oid(a["_id"])
        lid = oid(a.get("location"))
        act_rows.append({
            "id": aid, "event_id": event_id,
            "location_id": lid if lid in known_locs else None,
            "name": a["name"].strip(),
            "short_description": clean(a.get("shortDescription")),
            "long_description": clean(a.get("longDescription")),
            "starts_at": start, "ends_at": end,
            "status": a.get("status") or "published",
            "is_check_in_allowed": bool(a.get("isCheckInAllow")),
            "is_reserved": bool(a.get("reserved")),
            "reserved_url": clean(a.get("reserved_URL")),
            "icon_url": clean(a.get("icon")),
            "notify_schedule_at": None,
            "source_date": a.get("date"), "source_start_time": a.get("startTime"),
            "source_end_time": a.get("endTime")})
        for r in (a.get("accessRoles") or []):
            if oid(r) in known_types:
                audience.append({"activity_id": aid, "participant_type_id": oid(r)})
        for u in (a.get("userId") or []):
            pid = id_alias.get(oid(u))
            if pid:
                grants.append({"activity_id": aid, "person_id": pid})

    # ---------------------------------------------------------- sessions
    known_acts = {r["id"] for r in act_rows}
    known_rooms = {r["id"] for r in room_rows}
    act_of_session = {oid(s): oid(a["_id"])
                      for a in acts for s in (a.get("session") or [])}
    sess_rows, speakers = [], []
    for s in sess:
        start = to_instant(s.get("date"), s.get("startTime"), tz)
        end_date = s.get("endDate") if s.get("isEndOrNextDate") else s.get("date")
        end = to_instant(end_date or s.get("date"), s.get("endTime"), tz)
        if not start or not end or end <= start:
            print(f"  !! skipping session {s.get('title')!r}: bad time window")
            continue
        sid = oid(s["_id"])
        parent = act_of_session.get(sid)
        rid = oid(s.get("room"))
        sess_rows.append({
            "id": sid, "event_id": event_id,
            "activity_id": parent if parent in known_acts else None,
            "room_id": rid if rid in known_rooms else None,
            "title": s["title"].strip(),
            "short_description": clean(s.get("shortDescription")),
            "long_description": clean(s.get("longDescription")),
            "starts_at": start, "ends_at": end,
            "source_date": s.get("date"), "source_start_time": s.get("startTime"),
            "source_end_time": s.get("endTime")})
        for sp in (s.get("speakerId") or []):
            pid = id_alias.get(oid(sp))
            if pid:
                speakers.append({"session_id": sid, "person_id": pid})

    # --------------------------------------------------------- attendees
    att_rows = []
    for a in atts:
        u = a.get("user")
        pid = id_alias.get(oid(u.get("_id"))) if isinstance(u, dict) else None
        rid = oid(a.get("role"))
        if not pid or rid not in known_types:
            continue
        att_rows.append({"id": oid(a["_id"]), "event_id": event_id, "person_id": pid,
                         "participant_type_id": rid,
                         "is_manually_added": a.get("isManuallyAdded"),
                         "registered_at": (a.get("createdAt") or {}).get("$date")})

    # ------------------------------------------------ check-ins, faq, etc
    known_people = {r["id"] for r in people.values()}
    ci_rows = [{"id": oid(c["_id"]), "event_id": event_id,
                "person_id": id_alias.get(oid((c.get("user") or {}).get("_id"))),
                "activity_id": oid(c.get("activityId")) if oid(c.get("activityId")) in known_acts else None,
                "kind": clean(c.get("type")), "status": clean(c.get("status")),
                "checked_in_at": (c.get("checkInDateTime") or {}).get("$date")
                if isinstance(c.get("checkInDateTime"), dict) else c.get("checkInDateTime")}
               for c in live(d.get("checkIns") or [])]
    ci_rows = [r for r in ci_rows if r["person_id"] in known_people]

    faq_rows = [{"id": oid(f["_id"]), "event_id": event_id, "question": f["question"],
                 "answer": clean(f.get("answer")), "sort_order": f.get("order")}
                for f in live(d.get("faqs") or [])]

    tk_rows = [{"id": oid(t["_id"]), "event_id": event_id, "name": t["name"],
                "kind": clean(t.get("type")),
                "base_price_cents": int(round(float(t.get("basePrice") or 0) * 100)),
                "quantity": t.get("quantity"), "available_quantity": t.get("availableQuantity")}
               for t in live(d.get("tickets") or [])]

    ord_rows = []
    for o in live(d.get("orders") or []):
        pid = id_alias.get(oid((o.get("user") or {}).get("_id"))) if isinstance(o.get("user"), dict) else None
        if pid in known_people:
            ord_rows.append({"id": oid(o["_id"]), "event_id": event_id, "person_id": pid,
                             "created_at": (o.get("createdAt") or {}).get("$date")})

    # ------------------------------------------------------------- write
    ev_row = [{"id": event_id, "title": ev.get("title"), "slug": clean(ev.get("slug")),
               "timezone": tz,
               "starts_at": (ev.get("startDateTimeUTC") or {}).get("$date") if isinstance(ev.get("startDateTimeUTC"), dict) else ev.get("startDateTimeUTC"),
               "ends_at": (ev.get("endDateTimeUTC") or {}).get("$date") if isinstance(ev.get("endDateTimeUTC"), dict) else ev.get("endDateTimeUTC"),
               "status": clean(ev.get("status")),
               "city": clean((ev.get("location") or {}).get("city")) if isinstance(ev.get("location"), dict) else None,
               "country": clean((ev.get("location") or {}).get("country")) if isinstance(ev.get("location"), dict) else None,
               "short_description": clean(ev.get("shortDescription")),
               "long_description": clean(ev.get("longDescription")),
               "url": clean(ev.get("eventUrl"))}]

    plan = [("events", ev_row), ("participant_types", pt_rows), ("people", list(people.values())),
            ("attendees", att_rows), ("locations", loc_rows), ("rooms", room_rows),
            ("activities", act_rows), ("activity_audience", audience),
            ("activity_person_grants", grants), ("sessions", sess_rows),
            ("session_speakers", speakers), ("check_ins", ci_rows), ("faqs", faq_rows),
            ("tickets", tk_rows), ("orders", ord_rows)]

    # dedupe on the composite keys the DB enforces
    def dedupe(rows, keys):
        seen, out = set(), []
        for r in rows:
            k = tuple(r[x] for x in keys)
            if k not in seen:
                seen.add(k)
                out.append(r)
        return out

    # GroupOS can hold two attendee documents for the same person+type on one
    # event — same human, same role, two ids. The DB refuses it; keep the first.
    dup_att = len(att_rows) - len(dedupe(att_rows, ["event_id", "person_id", "participant_type_id"]))
    if dup_att:
        print(f"  {dup_att} duplicate attendee row(s) collapsed (same person, same type)")

    plan = [(t, dedupe(rows, ["activity_id", "participant_type_id"]) if t == "activity_audience"
             else dedupe(rows, ["activity_id", "person_id"]) if t == "activity_person_grants"
             else dedupe(rows, ["session_id", "person_id"]) if t == "session_speakers"
             else dedupe(rows, ["event_id", "person_id", "participant_type_id"]) if t == "attendees"
             else dedupe(rows, ["id"]) if rows and "id" in rows[0] else rows)
            for t, rows in plan]

    print()
    for table, rows in plan:
        n = upsert(table, rows, key, url, args.dry_run)
        print(f"  {'would load' if args.dry_run else 'loaded':<10} {n:>5}  {table}")


if __name__ == "__main__":
    main()
