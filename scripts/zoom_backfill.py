#!/usr/bin/env python3
"""#70 — load 2026 Zoom calls + attendance into digest.calls / digest.call_attendance.

Andy's rulings (2026-08-07):
  ① transcripts are vectorized so they drive the best VIDEO suggestions, and Olivia quotes and
     links the LIBRARY video (app.mds.co/videos/<id>) — never a Zoom URL;
  ② attendance is STORED, NEVER SHOWN — it feeds member_events, co_attended edges and the
     personalization layer, and no member-facing lane reports who was in a room.
Scope ruling (2026-08-06): 2026 only.

Idempotent: digest.calls upserts on call_uuid, digest.call_attendance on
(call_uuid, display_name, joined_at). Re-running changes 0 rows.

  python3 scripts/zoom_backfill.py            # dry run — counts only, writes nothing
  python3 scripts/zoom_backfill.py --apply
"""
import base64
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
ENV_SB = "/Users/Born/mds-digest-web/.env.local"

# Proven in the #70 research pass (scripts/zoom_groupos_match.py) — a call is member-facing when
# its topic names a community call and is not an internal team meeting.
MEMBER = re.compile(r"mogul|expert call|channel call|chapter .*call|wmds|large catalog"
                    r"|advisory council|resellers", re.I)
INTERNAL = re.compile(r"huddle|l-10|all-team|leadership|check-in|moderator|1:1|sync", re.I)
GMT = re.compile(r"GMT(\d{8})-(\d{6})")          # Zoom recording_start, UTC, inside the filename

# NEVER disable verification here: every request below carries either the Zoom client secret
# or a bearer token. The old fallback set CERT_NONE when certifi was missing — and /usr/bin/python3
# (which launchd runs) has no certifi, so the scheduled job sent credentials over an unverified
# connection while every manual run from a shell verified correctly. Prod-only and silent.
# The system trust store verifies api.zoom.us fine; certifi is used only when present.
CTX = ssl.create_default_context()
try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    pass


def env(path):
    out = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def zoom_token():
    e = env(os.path.join(ROOT, ".env.zoom"))
    basic = base64.b64encode(
        f"{e['ZOOM_CLIENT_ID']}:{e['ZOOM_CLIENT_SECRET']}".encode()).decode()
    url = ("https://zoom.us/oauth/token?grant_type=account_credentials&account_id="
           + urllib.parse.quote(e["ZOOM_ACCOUNT_ID"]))
    req = urllib.request.Request(url, data=b"", headers={"Authorization": "Basic " + basic})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return json.loads(r.read())["access_token"]


def zoom_get(url, tok, params=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as ex:
        return {"_err": ex.code, "_body": ex.read()[:300].decode("utf-8", "replace")}


def sb(method, path, key, body=None, prefer=None):
    cmd = ["curl", "-sS", "-m", "120", "-X", method, f"{SB}/{path}",
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    p = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                       capture_output=True, text=True)
    # A write with return=minimal succeeds with an EMPTY body — and so does a DNS failure, a
    # timeout or a TLS error. Without this check both landed in `return []` and the caller
    # happily printed "upserted: 253" having written nothing.
    if p.returncode != 0:
        raise RuntimeError(f"curl failed rc={p.returncode} on {method} {path[:80]}: "
                           f"{(p.stderr or '').strip()[:300]}")
    if p.stdout.strip().startswith("{") and '"message"' in p.stdout:
        raise RuntimeError("Supabase error: " + p.stdout[:400])
    if not p.stdout.strip():
        return []
    try:
        return json.loads(p.stdout)
    except Exception as ex:
        raise RuntimeError(f"unparseable Supabase response on {method} {path[:80]}: "
                           f"{ex} · body={p.stdout[:200]}")


def sb_all(path, key, page=1000):
    """Read EVERY row. PostgREST caps a response at 1000 rows whatever `limit` says, so a
    plain read silently returns 1000 of 1024 and the caller cannot tell. Pages until short."""
    out, off = [], 0
    sep = "&" if "?" in path else "?"
    while True:
        rows = sb("GET", f"{path}{sep}offset={off}&limit={page}", key)
        out += rows
        if len(rows) < page:
            return out
        off += page


def fold(name):
    """The alias join key: lowercased, punctuation-stripped, whitespace-collapsed."""
    s = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower())
    return re.sub(r"\s+", " ", s).strip()


URL_KEYS = re.compile(r"(url|link)$", re.I)


def strip_urls(obj):
    """Drop every *_url / *_link key, at any depth. Zoom's payload carries play_url,
    download_url and share_url on each recording file; none of it may be stored."""
    if isinstance(obj, dict):
        return {k: strip_urls(v) for k, v in obj.items() if not URL_KEYS.search(k)}
    if isinstance(obj, list):
        return [strip_urls(x) for x in obj]
    return obj


def call_type(topic):
    t = (topic or "").lower()
    if "mogul" in t:
        return "mogul"
    if "expert call" in t:
        return "expert"
    if "channel call" in t:
        return "channel"
    if "chapter" in t:
        return "chapter"
    return "other"


SCOPE_FROM_YEAR = 2026     # scope ruling 2026-08-06: 2026 onward (Zoom transcription starts here)


def months_in_scope():
    """Every month from the scope year to today. Derived, never hardcoded to one year —
    otherwise the weekly job silently stops ingesting on 1 January."""
    today = date.today()
    for y in range(SCOPE_FROM_YEAR, today.year + 1):
        for m in range(1, 13):
            first = date(y, m, 1)
            if first > today:
                return
            last = date(y + 1, 1, 1) - timedelta(days=1) if m == 12 \
                else date(y, m + 1, 1) - timedelta(days=1)
            yield first.isoformat(), min(last, today).isoformat()


def fetch_calls(tok):
    out = []
    for frm, to in months_in_scope():
        meetings, nxt = [], None
        while True:
            params = {"from": frm, "to": to, "page_size": 300}
            if nxt:
                params["next_page_token"] = nxt
            d = zoom_get("https://api.zoom.us/v2/accounts/me/recordings", tok, params)
            if "_err" in d:
                # a truncated month is silent data loss, so fail rather than press on
                raise RuntimeError(f"recordings {frm}: HTTP {d['_err']} {d.get('_body','')[:160]}")
            meetings += d.get("meetings", [])
            nxt = d.get("next_page_token")
            if not nxt:
                break
        for m in meetings:
            files = m.get("recording_files", [])
            types = {f.get("file_type") for f in files}
            starts = sorted(f["recording_start"] for f in files if f.get("recording_start"))
            topic = m.get("topic", "")
            out.append({
                "call_uuid": m["uuid"],
                "meeting_id": m.get("id"),
                "topic": topic,
                "call_type": call_type(topic),
                "host_email": m.get("host_email"),
                "started_at": m.get("start_time"),
                "duration_min": m.get("duration"),
                "has_recording": "MP4" in types or "M4A" in types,
                "has_transcript": "TRANSCRIPT" in types,
                "is_member_facing": bool(MEMBER.search(topic)) and not INTERNAL.search(topic),
                "recording_start": starts[0] if starts else None,
                # always present, even when unlinked: PostgREST rejects a batch whose objects
                # do not all carry the same keys ("All object keys must match")
                "groupos_video_id": None,
                "link_method": None,
                # strip every Zoom URL before storing: the same rule that keeps the video
                # storage path out of videos_catalog — a stored URL is one bug away from
                # being emitted, and members must only ever get the library link.
                "raw": strip_urls(m),
            })
    return out


def norm_words(t):
    """Significant words for title comparison — the library titles are marketing-styled
    ("… － Dorian Gorski － Mogul Call") while Zoom topics are plain ("Mogul Call with Dorian
    Gorski"), so compare on the words that survive both."""
    stop = {"the", "and", "for", "with", "your", "you", "how", "call", "mds", "from", "into",
            "using", "what", "why", "channel", "mogul", "expert", "chapter", "2026", "2025"}
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower())
            if len(w) >= 4 and w not in stop}


def link_videos(calls, key):
    """Two-signal join.

    PRIMARY — the exact stamp: GroupOS keeps Zoom's original filename and GMT<date>-<time> IS
    recording_start in UTC. Authoritative when present.

    FALLBACK (Andy 2026-08-07) — if the file was RENAMED on upload the stamp is gone, and the
    old code silently reported the call as "no video". So unlinked calls get a second pass on
    signals a rename cannot destroy: the video was published within a few days of the call, its
    DURATION matches within 3 minutes, and the titles share real words. Only a UNIQUE candidate
    links; ties are left unlinked rather than guessed, because a wrong link would attach one
    call's transcript to another call's video.

    Title or duration ALONE were tried in research and rejected — nearly every call runs ~55
    minutes, so duration by itself paired Dorian Gorski with a CAC/LTV video.
    """
    vids = sb_all("videos_catalog?select=video_id,title,duration_sec,zoom_recording_stamp,"
                  "app_created_at&deleted_at=is.null&status=eq.published", key)
    by_stamp = {}
    for v in vids:
        st = (v.get("zoom_recording_stamp") or "").replace("-", "")
        if st:
            by_stamp[st] = v["video_id"]

    linked = 0
    for c in calls:
        if not c["recording_start"]:
            continue
        stamp = c["recording_start"].replace("-", "").replace(":", "").replace("T", "").rstrip("Z")
        vid = by_stamp.get(stamp)
        if vid:
            c["groupos_video_id"], c["link_method"] = vid, "stamp"
            linked += 1

    taken = {c["groupos_video_id"] for c in calls if c.get("groupos_video_id")}
    recovered = []
    for c in calls:
        if c.get("groupos_video_id") or not c["is_member_facing"] or not c["started_at"]:
            continue
        cd = datetime.strptime(c["started_at"][:10], "%Y-%m-%d").date()
        cw = norm_words(c["topic"])
        cands = []
        for v in vids:
            if v["video_id"] in taken or not v.get("duration_sec") or not v.get("app_created_at"):
                continue
            vd = datetime.strptime(v["app_created_at"][:10], "%Y-%m-%d").date()
            if abs((vd - cd).days) > 7:
                continue
            if abs(v["duration_sec"] / 60.0 - (c["duration_min"] or 0)) > 3:
                continue
            overlap = len(cw & norm_words(v["title"]))
            gap = abs((vd - cd).days)
            dur = abs(v["duration_sec"] / 60.0 - (c["duration_min"] or 0))
            # Two words is the normal bar. ONE distinctive word is enough when the other two
            # signals are tight — same day and within 2 minutes. Found by probing the misses:
            # "MDS Expert Call with AppLovin" shares only "applovin" with its video title once
            # call/expert/mds are treated as stop-words, yet it is published the same day at
            # 55 vs 54 minutes. Requiring two words there discarded a certain match.
            if overlap < 2 and not (overlap >= 1 and gap == 0 and dur <= 2):
                continue
            cands.append(v)
        if len(cands) == 1:
            c["groupos_video_id"], c["link_method"] = cands[0]["video_id"], "duration+title"
            taken.add(cands[0]["video_id"])
            linked += 1
            recovered.append(f"{c['started_at'][:10]} {c['topic'][:44]} -> {cands[0]['title'][:44]}")
    for r in recovered:
        print(f"  ~ recovered by duration+title (filename was renamed): {r}")
    return linked, len(by_stamp), len(recovered)


def unlinked_report(calls, key):
    """A member call with a transcript and NO video is either genuinely unpublished or a link
    we failed to make. Those look identical in the data, so say which are suspicious: a video
    published within a day of the call means something was published and we did not match it."""
    vids = sb_all("videos_catalog?select=video_id,title,app_created_at"
                  "&deleted_at=is.null&status=eq.published", key)
    days = {}
    for v in vids:
        if v.get("app_created_at"):
            days.setdefault(v["app_created_at"][:10], []).append(v["title"])
    suspicious = []
    for c in calls:
        if c.get("groupos_video_id") or not c["is_member_facing"] or not c["has_transcript"]:
            continue
        cd = datetime.strptime(c["started_at"][:10], "%Y-%m-%d").date()
        near = [t for d, ts in days.items() for t in ts
                if abs((datetime.strptime(d, "%Y-%m-%d").date() - cd).days) <= 1]
        if near:
            suspicious.append((c["started_at"][:10], c["topic"], near[:2]))
    return suspicious


def fetch_attendance(tok, call_uuid):
    # Zoom requires the UUID double-encoded when it starts with '/' or contains '//'
    enc = urllib.parse.quote(urllib.parse.quote(call_uuid, safe=""), safe="")
    rows, token_pg = [], None
    while True:
        params = {"page_size": 300}
        if token_pg:
            params["next_page_token"] = token_pg
        d = zoom_get(f"https://api.zoom.us/v2/report/meetings/{enc}/participants", tok, params)
        if "_err" in d:
            # 400/404 = genuinely outside Zoom's ~13-month participant window. ANYTHING else
            # (429 throttling, 5xx) is an error, and returning [] here would have been recorded
            # as "this call had no attendees" — permanent loss, since the window keeps moving.
            if d["_err"] in (400, 404):
                return None
            raise RuntimeError(f"participants {call_uuid}: HTTP {d['_err']} "
                               f"{d.get('_body','')[:160]}")
        rows += d.get("participants", [])
        token_pg = d.get("next_page_token")
        if not token_pg:
            return rows


def main():
    apply = "--apply" in sys.argv
    key = env(ENV_SB)["SUPABASE_SECRET_KEY"]
    tok = zoom_token()

    calls = fetch_calls(tok)
    member = [c for c in calls if c["is_member_facing"]]
    linked, vid_stamps, recovered = link_videos(calls, key)
    print(f"calls 2026: {len(calls)} · member-facing {len(member)} · "
          f"with transcript {sum(c['has_transcript'] for c in calls)} · "
          f"video-linked {linked} (stamp {linked - recovered}, duration+title {recovered}; "
          f"catalog stamps {vid_stamps})")
    sus = unlinked_report(calls, key)
    if sus:
        print(f"  ! {len(sus)} member call(s) with a transcript, NO link, but a video published "
              f"within a day — a rename or a missed match, NOT simply unpublished:")
        for d_, topic, near in sus[:8]:
            print(f"      {d_} {topic[:46]} — near: {near[0][:52]}")

    if apply:
        for i in range(0, len(calls), 100):
            sb("POST", "calls?on_conflict=call_uuid", key, calls[i:i + 100],
               "resolution=merge-duplicates,return=minimal")
        print(f"  calls upserted: {len(calls)}")

    # Attendance: member-facing calls only. Zoom ages participants out on a ~13-month rolling
    # window, which is exactly why this has to be captured rather than queried on demand.
    att, no_data = [], 0
    for c in member:
        rows = fetch_attendance(tok, c["call_uuid"])
        if rows is None:
            no_data += 1
            continue
        for p in rows:
            nm = (p.get("name") or "").strip()
            if not nm:
                continue
            att.append({"call_uuid": c["call_uuid"], "display_name": nm,
                        "name_folded": fold(nm), "joined_at": p.get("join_time"),
                        "left_at": p.get("leave_time"), "seconds": p.get("duration")})
    # Zoom can report the same person twice with an identical join_time (two devices, or a
    # rejoin logged at the same second). Those collide on the unique key, and Postgres refuses
    # an upsert that would touch one row twice — so collapse them here, keeping the longest
    # session, rather than letting the batch fail.
    dedup = {}
    for r in att:
        k = (r["call_uuid"], r["display_name"], r["joined_at"])
        if k not in dedup or (r["seconds"] or 0) > (dedup[k]["seconds"] or 0):
            dedup[k] = r
    collapsed = len(att) - len(dedup)
    att = list(dedup.values())
    print(f"attendance rows: {len(att)} over {len(member) - no_data} calls "
          f"({no_data} calls past Zoom's rolling window, {collapsed} duplicate joins collapsed)")

    if not apply:
        print("DRY RUN — pass --apply to write")
        return

    for i in range(0, len(att), 500):
        sb("POST", "call_attendance?on_conflict=call_uuid,display_name,joined_at", key,
           att[i:i + 500], "resolution=merge-duplicates,return=minimal")
    print(f"  attendance upserted: {len(att)}")

    seeded = sb("POST", "rpc/zoom_resolve_attendance", key, {})
    print("name resolution:", json.dumps(seeded))


if __name__ == "__main__":
    main()
