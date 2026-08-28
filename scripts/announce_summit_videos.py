#!/usr/bin/env python3
"""Summit video announcement — per-attendee personalized fills. GENERATES ONLY, NEVER SENDS.

Andy 2026-08-28: "Let's prepare the message for Singapore attendees. don't send, confirm
with me first." Copy approved 2026-08-28 on his own test fill, with the "More sessions
are landing daily." line deleted (his edit).

Per member:
  - top-2 Summit sessions by topic fit (the same entity_dossier x member_topic_profile
    scoring video_search_v2 uses), never their own session
  - a SPEAKER gets "your own session is up" + 2 picks from the rest (Andy's Alex Bonilla
    rule: never recommend a speaker their own talk as advice)
  - every link COPIED from videos_catalog.video_id verbatim. Never reconstructed - the
    2026-08-26 test send shipped a fabricated link rebuilt from an id tail; that class
    of error is why this loop only ever formats ids it selected.

Output: OLIVIA_ANNOUNCE_SUMMIT_<date>.json (all fills) + _PREVIEW.md (stats + samples).
Speakers are parsed from the title's fullwidth-dash segments; unmatched or ambiguous
speaker names are listed in the preview for review, never guessed.
"""
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
SUMMIT_GROUPOS = "689cfd00f1f12d7791cf9525"
SUMMIT_ROSTER = "recrATwhUDA55iQN5"


def load_key():
    env = {}
    for line in open(ENV_PATH):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_SECRET_KEY"]


def rpc_sql(key, query):
    """Read-only helper via PostgREST /rpc is not generic; use the REST table reads below instead."""
    raise NotImplementedError


def rest(key, path):
    out = subprocess.run(
        ["curl", "-s", f"{BASE}/{path}",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Accept-Profile: digest"],
        capture_output=True, text=True)
    return json.loads(out.stdout)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()


def parse_title(title):
    """'Clean Title － Speaker A + Speaker B － Singapore Summit 2026' -> (clean, [speakers])."""
    parts = [p.strip() for p in re.split(r"[－]", title) if p.strip()]
    clean = parts[0] if parts else title.strip()
    speakers = []
    if len(parts) >= 2:
        # the speaker segment is the one before the event-name segment (or the 2nd of 2)
        seg = parts[1]
        if re.search(r"summit|singapore|2026", seg, re.I) and len(parts) == 2:
            seg = ""
        for name in re.split(r"[+&,]| and ", seg):
            name = name.strip()
            if name and not re.search(r"summit|singapore|2026", name, re.I):
                speakers.append(name)
    return clean, speakers


def main():
    key = load_key()
    stamp = date.today().isoformat()

    videos = rest(key, "videos_catalog?select=video_id,title,summary"
                       f"&event_ids=cs.%7B{SUMMIT_GROUPOS}%7D&deleted_at=is.null&status=eq.published"
                       "&order=app_created_at")
    vids = []
    for v in videos:
        clean, speakers = parse_title(v["title"])
        vids.append({"video_id": v["video_id"], "clean": clean, "speakers": speakers})
    n_vids = len(vids)

    # recipients: roster ∪ door list, active, not internal, with a phone on file
    roster = rest(key, f"event_registrations_live?select=member_at_id&event_at_id=eq.{SUMMIT_ROSTER}"
                       "&member_at_id=not.is.null")
    door = rest(key, "rpc/") if False else None
    # door list via the event schema needs Accept-Profile: event — separate call
    out = subprocess.run(
        ["curl", "-s", f"{BASE}/attendees?select=person_id,people(at_member_id)"
                       f"&event_id=eq.{SUMMIT_GROUPOS}",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Accept-Profile: event"],
        capture_output=True, text=True)
    door_rows = json.loads(out.stdout)
    ids = {r["member_at_id"] for r in roster} | {
        (r.get("people") or {}).get("at_member_id") for r in door_rows}
    ids.discard(None)

    members = rest(key, "member_attributes?select=at_member_id,full_name,membership_status,city"
                        f"&at_member_id=in.({','.join(sorted(ids))})")
    phones = rest(key, "members?select=at_member_id,phone,full_name"
                       f"&at_member_id=in.({','.join(sorted(ids))})&phone=not.is.null")
    phone_by = {m["at_member_id"]: m["phone"] for m in phones if m.get("phone")}
    name_fallback = {m["at_member_id"]: m.get("full_name") for m in phones}

    INTERNAL = {"Staff", "Team User"}
    ACTIVE = {"Current Member", "New Member", "Current Member- Not Renewing"}
    recipients = [m for m in members
                  if m.get("membership_status") in ACTIVE
                  and m["at_member_id"] in phone_by]
    skipped_internal = [m for m in members if m.get("membership_status") in INTERNAL]
    skipped_no_phone = [m for m in members
                        if m.get("membership_status") in ACTIVE and m["at_member_id"] not in phone_by]

    # fit scores per member x video, via the dossier topic profiles
    dossiers = rest(key, "entity_dossier?select=entity_id,topic_profile&kind=eq.video"
                         f"&entity_id=in.({','.join(v['video_id'] for v in vids)})")
    dprof = {d["entity_id"]: (d.get("topic_profile") or {}) for d in dossiers}

    speaker_norm = {}
    for v in vids:
        for s in v["speakers"]:
            speaker_norm.setdefault(norm(s), []).append(v["video_id"])

    fills, speaker_fills, unmatched_speakers = [], [], sorted(
        s for s in speaker_norm
        if not any(norm(m.get("full_name")) == s for m in members))

    for m in recipients:
        atid = m["at_member_id"]
        first = ((m.get("full_name") or name_fallback.get(atid) or "there").split() or ["there"])[0]
        prof = rest(key, f"rpc/member_topic_profile?p_member=eq.x") if False else None
        # topic profile via REST rpc:
        out = subprocess.run(
            ["curl", "-s", "-X", "POST", f"{BASE}/rpc/member_topic_profile",
             "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
             "-H", "Content-Type: application/json",
             "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
             "-d", json.dumps({"p_member": atid})],
            capture_output=True, text=True)
        try:
            topics = json.loads(out.stdout)
            assert isinstance(topics, list)
        except Exception:
            topics = []
        tmap = {t["topic"]: (t.get("sort_score") or 0, bool(t.get("is_working_on"))) for t in topics}

        own = speaker_norm.get(norm(m.get("full_name")), [])
        scored = []
        for v in vids:
            if v["video_id"] in own:
                continue
            fit = 0.0
            for topic, (score, working) in tmap.items():
                w = dprof.get(v["video_id"], {}).get(topic)
                if w is not None and float(w) >= 0.2:
                    fit += float(w) * (1.5 if working else 1.0)
            scored.append((fit, v))
        scored.sort(key=lambda x: -x[0])
        picks = [v for fit, v in scored[:2]]

        lines = [f"\U0001F3AC Hi {first} — the first {n_vids} session recordings from the *MDS Summit Singapore* are live."]
        if own:
            own_titles = [v["clean"] for v in vids if v["video_id"] in own]
            lines.append("")
            lines.append(f"\U0001F3AC Your own session is up: *{own_titles[0]}* — share it proudly.")
            lines.append("And picked for you from the rest:")
        else:
            lines.append("")
            lines.append("Picked for you:")
        for v in picks:
            lines.append("")
            spk = " + ".join(v["speakers"])
            lines.append(f"• *{v['clean']}*" + (f" — {spk}" if spk else ""))
            lines.append(f"https://app.mds.co/videos/{v['video_id']}")
        lines += ["",
                  "Full transcripts are searchable too — just ask me here: \"what did Tamar say about sampling?\", "
                  "\"summarize Ivan's AMA\", \"which session should I watch first?\" — I'll pull quotes, timestamps "
                  "and summaries for you.",
                  "",
                  "All Summit sessions so far: https://app.mds.co/videos"]
        fill = {"at_member_id": atid, "phone": phone_by[atid],
                "full_name": m.get("full_name"), "is_speaker": bool(own),
                "picks": [v["video_id"] for v in picks], "text": "\n".join(lines)}
        fills.append(fill)
        if own:
            speaker_fills.append(fill)

    out_json = f"OLIVIA_ANNOUNCE_SUMMIT_{stamp}.json"
    json.dump({"built": stamp, "videos": n_vids, "recipients": len(fills),
               "skipped_internal": len(skipped_internal), "skipped_no_phone": len(skipped_no_phone),
               "unmatched_speaker_names": unmatched_speakers, "fills": fills},
              open(out_json, "w"), indent=1, ensure_ascii=False)

    md = [f"# Summit announcement preview — {stamp}",
          f"videos: {n_vids} · recipients: {len(fills)} ({len(speaker_fills)} speakers) · "
          f"skipped: {len(skipped_internal)} internal, {len(skipped_no_phone)} active-but-no-phone",
          f"speaker names parsed from titles but matching NO attendee record: {unmatched_speakers or 'none'}",
          ""]
    samples = speaker_fills[:2] + [f for f in fills if not f["is_speaker"]][:3]
    for s in samples:
        md += [f"## {s['full_name']} ({'SPEAKER' if s['is_speaker'] else 'attendee'}) · …{s['phone'][-4:]}",
               "```", s["text"], "```", ""]
    open(f"OLIVIA_ANNOUNCE_SUMMIT_{stamp}_PREVIEW.md", "w").write("\n".join(md))
    print(f"videos {n_vids} · fills {len(fills)} · speakers {len(speaker_fills)} · "
          f"no-phone {len(skipped_no_phone)} · internal skipped {len(skipped_internal)}")
    print(f"wrote {out_json} + preview")


if __name__ == "__main__":
    main()
