#!/usr/bin/env python3
"""
Olivia red-team leak gate — MUST PASS before any new source ships into content_items.

What it proves, against the LIVE retrieval functions (digest.content_search /
digest.content_lookup — the only two operations Olivia has):

  1. sensitivity='never_surface' rows are NEVER returned, even when the member is
     entitled and the search terms match exactly.
  2. sensitivity='restricted' rows are excluded by default (returned only with
     p_include_restricted=true — the future consent path).
  3. Rows whose access_rule names a chat the member is NOT in are never returned.
  4. Unknown access_rule types are DENIED (fail closed) — a future source with a new
     rule type is invisible until the functions learn the rule.
  5. Malformed access_rule (missing chat key) is denied.
  6. An unknown/unmatched phone gets ZERO rows (fail closed), whatever the data.
  7. Payload hygiene: retrieval output never contains sender_phone; wa_message meta
     keys stay within the allowlist.
  8. The anon (publishable) key cannot call the retrieval functions at all.
  9. Positive control: a normal row in an entitled chat IS returned (the gate itself
     is alive — silence is not proof).
 10. Events source (digest.event_lookup / digest.event_who): Tentative rows invisible
     even if ingested; banded events (20M+/50M+/100M+/Centurion) omitted from browse
     calls and their rosters return ZERO rows for non-qualifying askers; guest
     registrations (member_at_id NULL) structurally excluded from who-lists; output
     carries names + city/state ONLY (no emails/phones/bands/ticket types); unknown
     phone = zero rows; anon denied on the RPCs and on both tables.
 11. Partners source (digest.partner_lookup): non-public access_restriction rows and
     non-published rows are invisible even when ingested (fail closed); output rows
     carry ONLY the allowlisted card fields; reviews_sample never exposes the
     reviewer (app_user_id stays server-side); partner_url is always the member app
     URL shape; unknown phone = zero rows; anon denied on the RPC and both tables.
 12. Videos source (digest.video_search): a restricted video, a soft-deleted video and
     a non-published video are each invisible even when ingested and even on a direct
     topical match (fail closed); output rows carry ONLY the allowlisted catalogue
     fields; the GroupOS storage path (uploads/content-archive/...) of the video FILE
     NEVER reaches the member — video_url is always the app.mds.co/videos/<id> shape;
     preview images (thumbnail_url / partner logo_url) MAY be stored and shown (Andy
     2026-07-30) but must be images, never content files; unknown phone = zero rows;
     anon denied on the RPC and on videos_catalog.

Canary rows are inserted with source='redteam_canary' and always deleted afterwards
(pre-cleaned on start too, so a crashed run can't poison the index).

Usage:  python3 scripts/olivia_leak_gate.py [--phone 1786…]
Exit 0 = gate passed. Exit 1 = LEAK / regression — do not ship the source.

Secrets come from /Users/Born/mds-digest-web/.env.local (parsed here — sourcing it
in bash breaks). Requests go through curl: python-urllib SSL is broken on this Mac.
"""
import argparse
import re
import json
import subprocess
import sys
import time

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
# anon key is public by definition (ships in every browser page)
ANON_KEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHR1ZHd1d2poY2tvdHJuZ3puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgxODM5MTQsImV4cCI6MjA5Mzc1OTkxNH0."
            "HWFtQKFVoj-Dm661gjSWW-p0t0cW5McPn8-Teq4dDZE")
CANARY_SOURCE = "redteam_canary"
MARKER = "zebrafishxylophone"  # term that exists nowhere in real content
META_ALLOWLIST_WA_MESSAGE = {"chat_name", "chat_id", "sender_member", "sender_name"}

failures = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def load_key():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_SECRET_KEY"]


def curl(method, url, key, body=None, profile_hdr=None):
    cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method, url,
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json"]
    for h in (profile_hdr or []):
        cmd += ["-H", h]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    raw, _, code = p.stdout.rpartition("\n")
    try:
        return int(code), json.loads(raw) if raw.strip() else None
    except (ValueError, json.JSONDecodeError):
        return int(code), raw[:300]


def rpc(fn, params, key):
    return curl("POST", f"{BASE}/rpc/{fn}", key, body=params,
                profile_hdr=["Content-Profile: digest"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phone", default="17866578153", help="a real matched member phone to probe as")
    args = ap.parse_args()
    key = load_key()
    phone = args.phone

    # the member's real chats (via the retrieval path itself would be circular — read members)
    st, rows = curl("GET", f"{BASE}/members?phone=eq.{phone}&select=channels_present", key,
                    profile_hdr=["Accept-Profile: digest"])
    if st != 200 or not rows or not rows[0].get("channels_present"):
        print(f"cannot resolve probe member {phone} (status {st}) — aborting")
        sys.exit(1)
    chats = rows[0]["channels_present"]
    entitled_chat = chats[0]
    ts = int(time.time())

    def canary(source_id, sensitivity, rule, body_extra=""):
        return {
            "source": CANARY_SOURCE, "kind": "canary", "source_id": f"{source_id}_{ts}",
            "title": None, "tl_dr": None,
            "body": f"REDTEAM CANARY ({source_id}) {MARKER} {body_extra} — synthetic row, ignore",
            "occurred_at": "2026-01-01T00:00:00Z", "url": None,
            "access_rule": rule, "sensitivity": sensitivity, "meta": {"chat_name": rule.get("chat", "")},
        }

    canaries = [
        canary("never_entitled", "never_surface", {"type": "chat_member", "chat": entitled_chat}),
        canary("restricted_entitled", "restricted", {"type": "chat_member", "chat": entitled_chat}),
        canary("normal_entitled", "normal", {"type": "chat_member", "chat": entitled_chat}),
        canary("normal_unentitled", "normal", {"type": "chat_member", "chat": "Canary Private Chat (nobody)"}),
        canary("unknown_rule_type", "normal", {"type": "plan", "plans": ["gold"]}),
        canary("malformed_rule", "normal", {"type": "chat_member"}),
    ]

    def cleanup():
        curl("DELETE", f"{BASE}/content_items?source=eq.{CANARY_SOURCE}", key,
             profile_hdr=["Content-Profile: digest"])
        curl("DELETE", f"{BASE}/event_registrations?roster_record_id=like.redteamreg_*", key,
             profile_hdr=["Content-Profile: digest"])
        curl("DELETE", f"{BASE}/events_catalog?at_record_id=like.redteamevt_*", key,
             profile_hdr=["Content-Profile: digest"])
        # partner canaries: deleting catalog rows cascades their canary reviews
        curl("DELETE", f"{BASE}/partners_catalog?partner_id=like.feedface*", key,
             profile_hdr=["Content-Profile: digest"])
        curl("DELETE", f"{BASE}/videos_catalog?video_id=like.feedface*", key,
             profile_hdr=["Content-Profile: digest"])

    cleanup()  # pre-clean any residue from a crashed run
    st, body = curl("POST", f"{BASE}/content_items", key, body=canaries,
                    profile_hdr=["Content-Profile: digest", "Prefer: return=minimal"])
    if st not in (200, 201):
        print(f"canary insert failed (status {st}): {body} — aborting")
        sys.exit(1)

    try:
        print("— sensitivity & access rules (search) —")
        st, hits = rpc("content_search", {"p_phone": phone, "p_terms": [MARKER], "p_limit": 100}, key)
        ids = {h["source_id"] for h in hits} if isinstance(hits, list) else set()
        check("search returns positive control (normal + entitled)", f"normal_entitled_{ts}" in ids, f"status {st}, ids {ids}")
        check("never_surface never returned", f"never_entitled_{ts}" not in ids)
        check("restricted excluded by default", f"restricted_entitled_{ts}" not in ids)
        check("unentitled chat never returned", f"normal_unentitled_{ts}" not in ids)
        check("unknown access_rule type denied (fail closed)", f"unknown_rule_type_{ts}" not in ids)
        check("malformed access_rule denied", f"malformed_rule_{ts}" not in ids)

        st, hits = rpc("content_search", {"p_phone": phone, "p_terms": [MARKER],
                                          "p_include_restricted": True, "p_limit": 100}, key)
        ids = {h["source_id"] for h in hits} if isinstance(hits, list) else set()
        check("restricted returned ONLY with explicit consent flag", f"restricted_entitled_{ts}" in ids)
        check("never_surface stays hidden even with consent flag", f"never_entitled_{ts}" not in ids)

        print("— sensitivity & access rules (lookup) —")
        st, hits = rpc("content_lookup", {"p_phone": phone, "p_source": CANARY_SOURCE, "p_limit": 100}, key)
        ids = {h["source_id"] for h in hits} if isinstance(hits, list) else set()
        check("lookup positive control", f"normal_entitled_{ts}" in ids, f"status {st}")
        check("lookup hides never_surface", f"never_entitled_{ts}" not in ids)
        check("lookup hides restricted by default", f"restricted_entitled_{ts}" not in ids)
        check("lookup hides unentitled/unknown/malformed",
              not ({f"normal_unentitled_{ts}", f"unknown_rule_type_{ts}", f"malformed_rule_{ts}"} & ids))

        print("— identity fail-closed —")
        st, hits = rpc("content_search", {"p_phone": "19999999999", "p_terms": [MARKER], "p_limit": 100}, key)
        check("unknown phone gets zero rows", isinstance(hits, list) and len(hits) == 0, f"status {st}, got {hits}")

        print("— payload hygiene (live wa_message rows) —")
        st, hits = rpc("content_search", {"p_phone": phone, "p_terms": ["amazon"],
                                          "p_sources": ["wa_message"], "p_limit": 40}, key)
        blob = json.dumps(hits)
        check("no sender_phone anywhere in retrieval output", "sender_phone" not in blob)
        bad_meta = [k for h in (hits or []) for k in h["meta"].keys()
                    if k not in META_ALLOWLIST_WA_MESSAGE]
        check("wa_message meta keys within allowlist", not bad_meta, f"unexpected: {sorted(set(bad_meta))}")

        print("— application source: owner-gating —")
        st, me = curl("GET", f"{BASE}/members?phone=eq.{phone}&select=at_member_id,full_name", key,
                      profile_hdr=["Accept-Profile: digest"])
        my_id = me[0]["at_member_id"] if st == 200 and me else None
        my_name = me[0].get("full_name") if st == 200 and me else None
        check("probe member resolves to an at_member_id", bool(my_id))
        st, rows = rpc("content_lookup", {"p_phone": phone, "p_source": "application", "p_limit": 100}, key)
        others = [r for r in (rows or []) if r["meta"].get("member") != my_id]
        check("application lookup returns ONLY the asker's own rows", not others,
              f"{len(others)} foreign rows")
        st, rows = rpc("content_search", {"p_phone": phone, "p_terms": ["revenue", "amazon", "brand"],
                                          "p_sources": ["application"], "p_limit": 100}, key)
        others = [r for r in (rows or []) if r["meta"].get("member") != my_id]
        check("application search cannot reach other members' answers", not others)

        print("— never-ingested fields stay out (whole table, service-side) —")
        import urllib.parse as _u
        leaked = []
        for probe in ("Q: Most Recent Revenue", "Q: Address", "Q: Birthdate", "Q: Email",
                      "Q: Phone Number", "Q: Zip code", "Q: Revenue Screenshot"):
            st, hits = curl("GET", f"{BASE}/content_items?source=eq.application&select=id&limit=1"
                            f"&body=ilike.{_u.quote('*' + probe + '*')}", key,
                            profile_hdr=["Accept-Profile: digest"])
            if isinstance(hits, list) and hits:
                leaked.append(probe)
        check("no never_surface field ever ingested into any application row", not leaked, str(leaked))

        print("— expertise_search (semantic free-text) hygiene —")
        st, exp = rpc("expertise_search", {"p_phone": phone, "p_query": "PPC advertising", "p_limit": 15}, key)
        check("expertise_search answers (status 200, rows)", st == 200 and isinstance(exp, list)
              and len(exp) > 0, f"status {st}")
        # matched_text added 2026-07-29 (#21): the PUBLIC profile snippet that matched
        # (about + fun fact — both already on the public member card), so the answering
        # loop can SEE the evidence instead of a bare name+rank. No new exposure.
        EXP_KEYS = {"full_name", "city", "state", "expertise", "niche", "matched_text", "matched_rank"}
        check("expertise rows carry ONLY name/city/state/expertise/niche/snippet/rank",
              all(set(e.keys()) == EXP_KEYS for e in (exp or [])))
        check("expertise matched_text holds only public-card fields (about/fun fact)",
              all((e.get("matched_text") is None)
                  or all(seg.strip().startswith(("about:", "fun fact:"))
                         for seg in str(e["matched_text"]).split(" | "))
                  for e in (exp or [])))
        eblob = json.dumps(exp)
        # Match real CONTACT DATA, not the words. The old substring test failed on a member whose
        # niche is legitimately "Cell phone accessories" (2026-07-27) — a false positive that would
        # train us to ignore a red gate. The allowed-keys check above already guarantees no phone or
        # email FIELD can be present, so here we look for an actual address / number in the values.
        EMAIL_RE = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        PHONE_RE = r"\+?\d[\d\s().-]{7,}\d"
        # Scan the TEXT fields only — matched_rank is a float like 0.0312829, which the phone
        # pattern happily matches. (Caught 2026-07-27 while fixing the "Cell phone accessories"
        # false positive; a gate that cries wolf twice is worse than no gate.)
        etext = json.dumps([{k: v for k, v in e.items() if k != "matched_rank"} for e in (exp or [])])
        _hit = re.search(EMAIL_RE, etext) or re.search(PHONE_RE, etext)
        check("expertise output has no revenue/contact fields",
              "rev_band" not in eblob and "Most Recent Revenue" not in eblob and not _hit,
              _hit.group(0) if _hit else "")
        check("expertise results exclude the asker",
              not my_name or all(e["full_name"] != my_name for e in (exp or [])))
        st, exp2 = rpc("expertise_search", {"p_phone": phone, "p_query": "zzxqwvnothing"}, key)
        check("expertise gibberish query = zero rows", isinstance(exp2, list) and not exp2)
        st, exp2 = rpc("expertise_search", {"p_phone": "19999999999", "p_query": "PPC"}, key)
        check("expertise unknown phone = zero rows", isinstance(exp2, list) and not exp2)
        st, _b = rpc("expertise_search", {"p_phone": phone, "p_query": "PPC"}, ANON_KEY)
        check("anon denied on expertise_search", st in (401, 403, 404), f"status {st}")

        print("— member_match output hygiene —")
        st, matches = rpc("member_match", {"p_phone": phone, "p_dims": ["state", "category", "band"],
                                           "p_limit": 20}, key)
        check("member_match answers (status 200)", st == 200, f"status {st}")
        ok_shape = all(set(m.keys()) == {"full_name", "city", "state", "reasons"} for m in (matches or []))
        check("match rows carry ONLY name/city/state/reasons", ok_shape)
        import re as _re
        dirty = [m for m in (matches or [])
                 if _re.search(r"[0-9$]|\bM\+|\bband\b", " ".join(m["reasons"]), _re.I)]
        check("match reasons contain no numbers/bands/values", not dirty, str(dirty[:2]))
        check("asker never appears in their own match list",
              not my_name or all(m["full_name"] != my_name for m in (matches or [])))
        st, hits = rpc("member_match", {"p_phone": "19999999999"}, key)
        check("member_match unknown phone = zero rows", isinstance(hits, list) and not hits)
        st, _b = rpc("member_match", {"p_phone": phone}, ANON_KEY)
        check("anon denied on member_match", st in (401, 403, 404), f"status {st}")

        print("— member_count hygiene (#5, 2026-07-31) —")
        st, cnt = rpc("member_count", {"p_phone": phone, "p_niche": "Supplements"}, key)
        check("member_count answers (status 200)", st == 200, f"status {st}")
        row = (cnt or [{}])[0]
        check("count rows carry ONLY total/breakdown/breakdown_sum/population/note",
              set(row.keys()) <= {"total", "breakdown", "breakdown_sum", "population", "note"},
              str(list(row.keys())))
        st, grp = rpc("member_count", {"p_phone": phone, "p_group_by": "chapter"}, key)
        g = ((grp or [{}])[0].get("breakdown") or {})
        # breakdown values are COUNTS keyed by public dimension values — a member name as a key
        # (or anything but an integer as a value) means the aggregate started identifying people
        check("breakdown values are integers only", all(isinstance(v, int) for v in g.values()))
        check("no breakdown key matches the asker's name",
              not my_name or all(my_name.lower() not in str(k).lower() for k in g.keys()))
        st, z = rpc("member_count", {"p_phone": "19999999999", "p_niche": "Supplements"}, key)
        check("member_count unknown phone = zero rows", isinstance(z, list) and not z)
        st, _b = rpc("member_count", {"p_phone": phone}, ANON_KEY)
        check("anon denied on member_count", st in (401, 403, 404), f"status {st}")

        print("— chapter_info hygiene (#6, 2026-07-31) —")
        st, chs = rpc("chapter_info", {"p_phone": phone}, key)
        check("chapter_info answers (status 200)", st == 200, f"status {st}")
        ch_names = [r.get("chapter") for r in (chs or [])]
        check("chapter list = the 20-row catalog whitelist, no junk pseudo-chapters",
              len(ch_names) == 20 and not any(j in n for n in ch_names
                                              for j in ("Shopify", "Amazon", "Sponsor")),
              f"{len(ch_names)} rows")
        # one number everywhere: chapter_info live counts == member_count's chapter breakdown
        st, grp2 = rpc("member_count", {"p_phone": phone, "p_group_by": "chapter"}, key)
        g2 = ((grp2 or [{}])[0].get("breakdown") or {})
        mismatch = [r["chapter"] for r in (chs or []) if g2.get(r["chapter"]) != r.get("member_count")]
        check("chapter_info counts == member_count breakdown (one number everywhere)",
              bool(chs) and not mismatch, str(mismatch)[:150])
        blob = json.dumps(chs or [])
        check("no email and no email/phone KEYS in chapter output",
              "@" not in blob and '"email"' not in blob and '"phone"' not in blob)
        check("lead objects carry ONLY name/role/photo_url",
              all(set(l.keys()) <= {"name", "role", "photo_url"}
                  for r in (chs or []) for l in (r.get("leads") or [])))
        st, z = rpc("chapter_info", {"p_phone": "19999999999"}, key)
        check("chapter_info unknown phone = zero rows (fail closed)", isinstance(z, list) and not z)
        st, _b = rpc("chapter_info", {"p_phone": phone}, ANON_KEY)
        check("anon denied on chapter_info", st in (401, 403, 404), f"status {st}")

        print("— chat_recommendations hygiene —")
        st, recs = rpc("chat_recommendations", {"p_phone": phone}, key)
        check("chat_recommendations answers (status 200)", st == 200, f"status {st}")
        ok_shape = all(set(r.keys()) == {"chat_name", "verification_required", "requirement",
                                         "qualifies", "join_link"} for r in (recs or []))
        check("rec rows expose chat facts only (no member attributes)", ok_shape)
        check("no 'you do not qualify' rows (absence must stay ambiguous)",
              all(r["qualifies"] in (True, None) for r in (recs or [])))
        st, _b = rpc("chat_recommendations", {"p_phone": phone}, ANON_KEY)
        check("anon denied on chat_recommendations", st in (401, 403, 404), f"status {st}")

        print("— chat_info hygiene —")
        st, info = rpc("chat_info", {"p_phone": phone}, key)
        check("chat_info answers (status 200)", st == 200, f"status {st}")
        no_zoom_leak = all(r.get("zoom_link") is None or r.get("is_member") for r in (info or []))
        check("zoom links only for chats the asker is in", no_zoom_leak)
        gated_ok = all((not r.get("verification_required")) or r.get("is_member")
                       or "typeform" in (r.get("join_link") or "")
                       for r in (info or []))
        check("gated chats: members get the chat, others only the verification form", gated_ok)
        # probe as a member with few chats — THEY must get typeform links for gated chats
        st, few = curl("GET", f"{BASE}/members?select=phone&phone=not.is.null"
                       "&channels_present=not.is.null"
                       "&channels_present=not.cs.%7B%22MDS%20Centurion%2020M%2B%22%7D&limit=200", key,
                       profile_hdr=["Accept-Profile: digest"])
        alt_phone = next((m["phone"] for m in (few or []) if m["phone"] != phone), None)
        if alt_phone:
            st, info2 = rpc("chat_info", {"p_phone": alt_phone}, key)
            gated2 = [r for r in (info2 or []) if r.get("verification_required") and not r.get("is_member")]
            check("non-members of gated chats get verification forms, never raw invites",
                  bool(gated2) and all("typeform" in (r.get("join_link") or "") for r in gated2),
                  f"{len(gated2)} gated rows for alt member")
        st, _b = rpc("chat_info", {"p_phone": "19999999999"}, key)
        check("chat_info unknown phone = zero rows", isinstance(_b, list) and not _b)
        st, _b = rpc("chat_info", {"p_phone": phone}, ANON_KEY)
        check("anon denied on chat_info", st in (401, 403, 404), f"status {st}")

        print("— events source: catalog & roster gating —")
        chap_id = f"redteamchap_{ts}"  # a synthetic chapter NO real member belongs to
        def evt_canary(sid, name, phase, cap=None, style=None, chapter_ids=None):
            return {"at_record_id": f"redteamevt_{sid}_{ts}", "name": name,
                    "start_at": "2027-11-01T18:00:00Z", "event_type": "In Person",
                    "phase": phase, "guests_policy": "MDSonly", "venue_capacity": cap,
                    "style": style, "chapter_ids": chapter_ids,
                    "member_reg_link": "https://example.com/reg-canary"}
        evt_rows = [
            evt_canary("tent", f"REDTEAM Tentative {MARKER} Dinner", "Tentative"),
            evt_canary("band", f"100M+ REDTEAM {MARKER} Forum", "Registration Open"),
            evt_canary("norm", f"REDTEAM Normal {MARKER} Social", "Registration Open", cap=10),
            evt_canary("chap", f"REDTEAM {MARKER} Chapter Dinner", "Registration Open", cap=10,
                       style="Chapter", chapter_ids=[chap_id]),
        ]
        st, body = curl("POST", f"{BASE}/events_catalog", key, body=evt_rows,
                        profile_hdr=["Content-Profile: digest", "Prefer: return=minimal"])
        check("event canaries inserted", st in (200, 201), f"status {st}: {body}")
        # Attendance filter (2026-07-23, AMENDED 2026-07-24 — Andy: staff ARE attendees,
        # "is Eugene coming" must say yes): a row counts if Ticket Status = Confirmed AND
        # Ticket for overlaps {MDS Member, MDS Member's Business Guest, MDS Team}. Partner
        # and plus-one ticket types stay excluded, as do No-Show/Unconfirmed. Canaries:
        # confirmed member (counts), No-Show guest (excluded), Unconfirmed member (excluded),
        # Confirmed MDS Team unlinked (counts in TOTAL; unlinked ⇒ still nameless),
        # Confirmed Partner (excluded everywhere).
        reg_rows = [
            {"roster_record_id": f"redteamreg_member_{ts}", "event_at_id": f"redteamevt_norm_{ts}",
             "member_at_id": my_id, "email": "redteam-member@example.com",
             "full_name": "Redteam Membername", "ticket_type": "MDS Member",
             "ticket_status": "Confirmed", "ticket_for": ["MDS Member"], "source": "MDS App"},
            {"roster_record_id": f"redteamreg_guest_{ts}", "event_at_id": f"redteamevt_norm_{ts}",
             "member_at_id": None, "email": "redteam-guest@example.com",
             "full_name": "REDTEAM GUEST NoShow", "ticket_type": "Guest",
             "ticket_status": "No Show", "ticket_for": ["Significant Other"], "source": "MDS App"},
            {"roster_record_id": f"redteamreg_unconf_{ts}", "event_at_id": f"redteamevt_norm_{ts}",
             "member_at_id": my_id, "email": "redteam-unconf@example.com",
             "full_name": "REDTEAM UNCONFIRMED", "ticket_type": "MDS Member",
             "ticket_status": "Unconfirmed", "ticket_for": ["MDS Member"], "source": "MDS App"},
            {"roster_record_id": f"redteamreg_staff_{ts}", "event_at_id": f"redteamevt_norm_{ts}",
             "member_at_id": None, "email": "redteam-staff@example.com",
             "full_name": "REDTEAM STAFF", "ticket_type": "Staff",
             "ticket_status": "Confirmed", "ticket_for": ["MDS Team"], "source": "MDS App"},
            {"roster_record_id": f"redteamreg_partner_{ts}", "event_at_id": f"redteamevt_norm_{ts}",
             "member_at_id": None, "email": "redteam-partner@example.com",
             "full_name": "REDTEAM PARTNER", "ticket_type": "Partner",
             "ticket_status": "Confirmed", "ticket_for": ["Partner"], "source": "MDS App"},
            {"roster_record_id": f"redteamreg_bandm_{ts}", "event_at_id": f"redteamevt_band_{ts}",
             "member_at_id": my_id, "email": "redteam-band@example.com",
             "full_name": "Redteam Bandmember", "ticket_type": "MDS Member",
             "ticket_status": "Confirmed", "ticket_for": ["MDS Member"], "source": "MDS App"},
        ]
        st, body = curl("POST", f"{BASE}/event_registrations", key, body=reg_rows,
                        profile_hdr=["Content-Profile: digest", "Prefer: return=minimal"])
        check("event registration canaries inserted", st in (200, 201), f"status {st}: {body}")

        # my band decides which phone plays the non-qualifying asker
        st, my_attr = curl("GET", f"{BASE}/member_attributes?at_member_id=eq.{my_id}&select=rev_band",
                           key, profile_hdr=["Accept-Profile: digest"])
        my_band = (my_attr or [{}])[0].get("rev_band") if st == 200 and my_attr else None
        non20m_phone = phone if my_band != "20M+" else None
        if non20m_phone is None:
            st, cand = curl("GET", f"{BASE}/members?select=phone,at_member_id"
                            "&phone=not.is.null&at_member_id=not.is.null&limit=300", key,
                            profile_hdr=["Accept-Profile: digest"])
            ids = ",".join(m["at_member_id"] for m in (cand or [])[:100])
            st, bands = curl("GET", f"{BASE}/member_attributes?at_member_id=in.({ids})"
                             "&select=at_member_id,rev_band", key,
                             profile_hdr=["Accept-Profile: digest"])
            band_by_id = {b["at_member_id"]: b.get("rev_band") for b in (bands or [])}
            non20m_phone = next((m["phone"] for m in (cand or [])
                                 if band_by_id.get(m["at_member_id"]) not in ("20M+",)), None)
        check("found a non-20M+ probe asker", bool(non20m_phone))

        st, evs = rpc("event_lookup", {"p_phone": phone, "p_terms": [MARKER], "p_limit": 30}, key)
        names = {e["event_name"] for e in (evs or [])} if isinstance(evs, list) else set()
        check("event_lookup positive control (canary via terms)",
              f"REDTEAM Normal {MARKER} Social" in names, f"status {st}, got {sorted(names)}")
        check("Tentative event invisible even when ingested",
              all("Tentative" not in n for n in names))
        # CHAPTER GATE (leak-critical): an event tied to a chapter the asker is NOT a
        # member of must never surface. The probe member is not in the synthetic redteam
        # chapter, so the chapter canary must be absent from their results.
        st_mc, myc = curl("GET", f"{BASE}/member_attributes?at_member_id=eq.{my_id}"
                          "&select=chapter_ids", key, profile_hdr=["Accept-Profile: digest"])
        my_chapters = ((myc or [{}])[0].get("chapter_ids") or []) if st_mc == 200 else []
        if chap_id not in my_chapters:
            check("chapter event hidden from a non-chapter member (fail-closed)",
                  f"REDTEAM {MARKER} Chapter Dinner" not in names,
                  "chapter canary leaked to a non-member")
        # event_lookup output must never carry an admin/finance/PII field
        blob = json.dumps(evs).lower()
        admin_keys = ("budget", "roster", "managed_by", "clickup", "attendee_goal",
                      "member_goal", "partner_revenue", "revenue_goal", "expenses")
        check("event_lookup output carries no admin/finance field",
              not any(k in blob for k in admin_keys),
              f"found: {[k for k in admin_keys if k in blob]}")

        if non20m_phone:
            st, evs = rpc("event_lookup", {"p_phone": non20m_phone, "p_terms": [MARKER],
                                           "p_limit": 30}, key)
            alt_names = {e["event_name"] for e in (evs or [])} if isinstance(evs, list) else set()
            check("alt asker resolves (positive control, not vacuous)",
                  f"REDTEAM Normal {MARKER} Social" in alt_names, f"status {st}")
            st, evs = rpc("event_lookup", {"p_phone": non20m_phone, "p_limit": 30,
                                           "p_include_past": False}, key)
            browse_names = {e["event_name"] for e in (evs or [])} if isinstance(evs, list) else set()
            check("banded events omitted from browse for non-20M+ asker",
                  all("100M+" not in n and "Centurion" not in n for n in browse_names),
                  f"saw: {[n for n in browse_names if '100M+' in n or 'Centurion' in n]}")
            st, who = rpc("event_who", {"p_phone": non20m_phone,
                                        "p_event": f"100M+ REDTEAM {MARKER}"}, key)
            check("banded roster = zero rows for non-20M+ asker",
                  isinstance(who, list) and not who, f"status {st}, got {who}")

        st, who = rpc("event_who", {"p_phone": phone, "p_event": f"REDTEAM Normal {MARKER}"}, key)
        blob = json.dumps(who)
        # EUGENE'S REFINED RULING (2026-07-20): member lists are public-in-app => names OK.
        # Live-joined name, guests still structurally excluded, nothing beyond name/state.
        check("event_who returns the member registration (live-joined name)",
              isinstance(who, list) and len(who) == 1 and who[0]["is_me"] is True
              and who[0]["full_name"] == my_name, f"status {st}, got {who}")
        check("guest registrations structurally excluded", "REDTEAM GUEST" not in blob)
        # Confirmed-only + 2026-07-24 amendment: Unconfirmed members and Partner tickets are
        # excluded from names AND total; the Confirmed MDS Team row COUNTS in the total
        # (Andy: staff are attendees) but is unlinked here so it stays nameless.
        check("unconfirmed / partner rows excluded from who-list; unlinked staff nameless",
              "UNCONFIRMED" not in blob and "STAFF" not in blob and "PARTNER" not in blob)
        check("event_who total_going = confirmed members + MDS Team, partners excluded (== 2 here)",
              isinstance(who, list) and bool(who) and who[0].get("total_going") == 2,
              f"got {who}")
        check("event_who emits no emails/phones/bands/tickets",
              "@" not in blob and "rev_band" not in blob and "ticket" not in blob.lower()
              and "email" not in blob.lower())
        ok_shape = all(set(w.keys()) == {"event_name", "starts_at", "full_name", "state",
                                         "is_me", "total_going"} for w in (who or []))
        check("event_who rows carry ONLY event/name/state/is_me/total_going", ok_shape)

        print("— member_card (Eugene's public-fields ruling) —")
        # probe target must be an ACTIVE member (the card correctly excludes staff/removed —
        # the default probe asker Andy is Staff and has no card of his own)
        st, tgt = curl("GET", f"{BASE}/member_attributes?select=full_name"
                       "&membership_status=in.(%22Current%20Member%22,%22New%20Member%22)"
                       "&full_name=not.is.null&rev_band=not.is.null&limit=1", key,
                       profile_hdr=["Accept-Profile: digest"])
        card_target = (tgt or [{}])[0].get("full_name") or "Mo Kuhail"
        st, card = rpc("member_card", {"p_phone": phone, "p_member": card_target}, key)
        # +membership_state/joined/left_date — Andy's ruling 2026-07-26: a PAST member is a real
        # person whose record we hold, so "I don't have a member named Lori" was a lie. She may now
        # say someone joined, left, and which chapter they used to be in. The REMOVAL REASON stays
        # secret forever: 'Removed - For Cause' and the staff notes never leave the DB — only the
        # coarse 'current'/'past' state is emitted (asserted below).
        CARD_KEYS = {"full_name", "city", "state", "revenue_tier", "niche", "expertise",
                     "about_me", "hobbies", "fun_fact", "facebook_link", "chapter", "shared_chats",
                     "membership_state", "joined", "left_date"}
        check("member_card answers for a real member (status 200, rows)", st == 200
              and isinstance(card, list) and len(card) >= 1, f"status {st}")
        check("card rows carry ONLY the public-directory fields",
              all(set(c.keys()) == CARD_KEYS for c in (card or [])))
        cblob = json.dumps(card)
        # Andy's ruling 2026-07-27: the revenue TIER is SHAREABLE (public directory field in the
        # app); only EXACT figures are not. So the gate asserts NO PRECISE NUMBER ever appears -- a
        # coarse band like "$1-5M" or "$20M+" is fine, "$3,400,000" or "3.4M in revenue" is not.
        check("member_card never emits a PRECISE revenue figure (tier bands are allowed)",
              not re.search(r"\$\s?\d{1,3}(,\d{3})+|\$\s?\d+\.\d+\s?[Mm]\b", cblob),
              cblob[:160])
        check("card has no email/phone keys and no exact revenue",
              "email" not in cblob.lower().replace("facebook", "")
              and "phone" not in cblob.lower() and "Most Recent Revenue" not in cblob)
        st, ian = rpc("member_card", {"p_phone": phone, "p_member": "Ian Sells"}, key)
        check("member_card shared_chats never exceed the ASKER's own chats",
              all(set(c.get("shared_chats") or []) <= set(chats) for c in (ian or [])),
              f"got {[c.get('shared_chats') for c in (ian or [])]}")
        # PAST MEMBERS: findable, but the reason they left is never emitted.
        st, past = rpc("member_card", {"p_phone": phone, "p_member": "Lori Barzvi"}, key)
        pblob = json.dumps(past or [])
        check("member_card FINDS a past member (Andy 2026-07-26)",
              isinstance(past, list) and len(past) >= 1
              and (past or [{}])[0].get("membership_state") == "past", f"got {pblob[:120]}")
        check("past-member card emits state only, NEVER the removal reason",
              all(c.get("membership_state") in ("current", "past") for c in (past or []))
              and not any(w in pblob.lower() for w in
                          ("for cause", "canceled membership", "cancelled", "removed -",
                           "declined", "dead lead", "core values", "not aligned")),
              f"got {pblob[:200]}")
        check("past-member card leaks no revenue/contact/address",
              "@" not in pblob and "phone" not in pblob.lower()
              and "address" not in pblob.lower() and "Most Recent Revenue" not in pblob)
        # people who were NEVER members must stay invisible
        st, lead = rpc("member_card", {"p_phone": phone, "p_member": "Zzz Dead Lead Person"}, key)
        check("member_card never surfaces non-members (leads/applicants)",
              isinstance(lead, list) and not lead)
        st, card = rpc("member_card", {"p_phone": phone, "p_member": "Zzz Nonexistent Person"}, key)
        check("member_card unknown target = zero rows", isinstance(card, list) and not card)
        # #9: revenue leaves the DB as a BAND only — never a raw dollar figure
        st, mycard = rpc("member_card", {"p_phone": phone, "p_member": my_name}, key)
        bands_ok = all((r.get("revenue_tier") in (None, "", "1-5M", "5-10M", "10-20M", "20M+"))
                       for r in (mycard or []))
        check("member_card revenue_tier is a BAND (never a raw figure)", bool(mycard) and bands_ok,
              str([(r.get("full_name"), r.get("revenue_tier")) for r in (mycard or [])])[:150])
        cblob = json.dumps(mycard or [])
        check("member_card carries no raw revenue field",
              "Most Recent Revenue" not in cblob and not re.search(r'"revenue[^"]*":\s*[0-9]{5,}', cblob))
        st, bnd = rpc("member_count", {"p_phone": phone, "p_group_by": "band"}, key)
        bd_keys = list((((bnd or [{}])[0]).get("breakdown") or {}).keys())
        check("member_count band breakdown keys are the band vocabulary only",
              bool(bd_keys) and set(bd_keys) <= {"1-5M", "5-10M", "10-20M", "20M+", "(none on file)"},
              str(bd_keys))
        st, card = rpc("member_card", {"p_phone": "19999999999", "p_member": my_name}, key)
        check("member_card unknown asker phone = zero rows", isinstance(card, list) and not card)
        st, _b = rpc("member_card", {"p_phone": phone, "p_member": my_name}, ANON_KEY)
        check("anon denied on member_card", st in (401, 403, 404), f"status {st}")

        print("— member_dossier & community_info (own data / stats) —")
        st, dos = rpc("member_dossier", {"p_phone": phone}, key)
        check("member_dossier answers for the asker (status 200)", st == 200, f"status {st}")
        ok_kinds = all(d.get("kind") in ("active_chat", "recent_said", "upcoming_event",
                                         "past_event") for d in (dos or []))
        check("dossier rows carry only own-activity kinds", ok_kinds)
        st, dos = rpc("member_dossier", {"p_phone": "19999999999"}, key)
        check("member_dossier unknown phone = zero rows", isinstance(dos, list) and not dos)
        st, _b = rpc("member_dossier", {"p_phone": phone}, ANON_KEY)
        check("anon denied on member_dossier", st in (401, 403, 404), f"status {st}")
        st, ci = rpc("community_info", {"p_phone": phone}, key)
        check("community_info answers (status 200, one row)", st == 200 and isinstance(ci, list)
              and len(ci) == 1 and ci[0].get("active_members", 0) > 0, f"status {st}, {ci}")
        st, ci = rpc("community_info", {"p_phone": "19999999999"}, key)
        check("community_info unknown phone = zero rows", isinstance(ci, list) and not ci)
        st, _b = rpc("community_info", {"p_phone": phone}, ANON_KEY)
        check("anon denied on community_info", st in (401, 403, 404), f"status {st}")

        st, hist = rpc("event_history", {"p_phone": phone}, key)
        check("event_history answers for the asker (status 200)", st == 200, f"status {st}")
        ok_kinds = all(h.get("kind") in ("me", "upcoming", "past", "past_total") for h in (hist or []))
        check("event_history rows carry only me/upcoming/past kinds", ok_kinds)
        hblob = json.dumps(hist)
        check("event_history emits no emails/phones/bands", "@" not in hblob and "rev_band" not in hblob)
        st, hist = rpc("event_history", {"p_phone": "19999999999"}, key)
        check("event_history unknown phone = zero rows", isinstance(hist, list) and not hist)
        st, _b = rpc("event_history", {"p_phone": phone}, ANON_KEY)
        check("anon denied on event_history", st in (401, 403, 404), f"status {st}")

        st, evs = rpc("event_lookup", {"p_phone": "19999999999", "p_terms": [MARKER]}, key)
        check("event_lookup unknown phone = zero rows", isinstance(evs, list) and not evs)
        st, who = rpc("event_who", {"p_phone": "19999999999", "p_event": MARKER}, key)
        check("event_who unknown phone = zero rows", isinstance(who, list) and not who)
        st, _b = rpc("event_lookup", {"p_phone": phone, "p_terms": [MARKER]}, ANON_KEY)
        check("anon denied on event_lookup", st in (401, 403, 404), f"status {st}")
        st, _b = rpc("event_who", {"p_phone": phone, "p_event": MARKER}, ANON_KEY)
        check("anon denied on event_who", st in (401, 403, 404), f"status {st}")
        st, body = curl("GET", f"{BASE}/events_catalog?select=name&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read events_catalog",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")
        st, body = curl("GET", f"{BASE}/event_registrations?select=email&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read event_registrations",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")

        print("— partners source (partner_lookup) —")
        pc_canaries = [
            {"partner_id": "feedfacefeedfacefeed0001",
             "name": f"REDTEAM Restricted Partner {MARKER}",
             "description_text": f"partner canary {MARKER} restricted", "offer_value": "100% OFF",
             "status": "published", "access_restriction": "tier",
             "access_detail": {"restricted_tier_ids": ["deadbeefdeadbeefdeadbeef"]}},
            {"partner_id": "feedfacefeedfacefeed0002",
             "name": f"REDTEAM Paused Partner {MARKER}",
             "description_text": f"partner canary {MARKER} paused", "offer_value": "99% OFF",
             "status": "paused", "access_restriction": "public", "access_detail": None},
            {"partner_id": "feedfacefeedfacefeed0003",
             "name": f"REDTEAM Public Partner {MARKER}",
             "description_text": f"partner canary {MARKER} public", "offer_value": "50% OFF",
             "status": "published", "access_restriction": "public", "access_detail": None},
        ]
        st, body = curl("POST", f"{BASE}/partners_catalog", key, body=pc_canaries,
                        profile_hdr=["Content-Profile: digest", "Prefer: return=minimal"])
        check("partner canaries inserted", st in (200, 201), f"status {st}: {body}")
        st, body = curl("POST", f"{BASE}/partner_reviews", key, body=[
            {"review_id": "feedfacefeedfacefeed0004", "partner_id": "feedfacefeedfacefeed0003",
             "rating": 5, "review_text": f"canary review {MARKER}",
             "app_user_id": "feedfacefeedfacefeed9999", "reviewed_at": "2026-01-01T00:00:00Z"},
        ], profile_hdr=["Content-Profile: digest", "Prefer: return=minimal"])
        check("partner review canary inserted", st in (200, 201), f"status {st}: {body}")

        st, ptn = rpc("partner_lookup", {"p_phone": phone, "p_query": MARKER, "p_limit": 20}, key)
        pnames = {p["name"] for p in (ptn or [])} if isinstance(ptn, list) else set()
        check("partner_lookup positive control (public canary via search)",
              f"REDTEAM Public Partner {MARKER}" in pnames, f"status {st}, got {sorted(pnames)}")
        check("non-public access_restriction partner invisible (fail closed)",
              f"REDTEAM Restricted Partner {MARKER}" not in pnames)
        check("non-published partner invisible",
              f"REDTEAM Paused Partner {MARKER}" not in pnames)
        PARTNER_KEYS = {"name", "offer_value", "description_snippet", "categories",
                        "rating_avg", "review_count", "claim_count", "featured",
                        "fresh_deal", "partner_url", "reviews_sample", "matched_rank"}
        check("partner rows carry ONLY the allowlisted fields",
              all(set(p.keys()) == PARTNER_KEYS for p in (ptn or [])))
        pblob = json.dumps(ptn)
        check("partner output never exposes reviewer identity or user ids",
              "app_user_id" not in pblob and "feedfacefeedfacefeed9999" not in pblob)
        pub = next((p for p in (ptn or []) if p["name"] == f"REDTEAM Public Partner {MARKER}"), None)
        check("reviews_sample carries the review text (rating+text only)",
              bool(pub) and pub.get("reviews_sample")
              and all(set(r.keys()) == {"rating", "text"} for r in pub["reviews_sample"])
              and any(MARKER in (r.get("text") or "") for r in pub["reviews_sample"]),
              f"sample: {pub.get('reviews_sample') if pub else None}")
        check("partner_url is the member app shape",
              all((p.get("partner_url") or "").startswith("https://app.mds.co/partners/")
                  and "/admin/" not in (p.get("partner_url") or "") for p in (ptn or [])))
        st, browse = rpc("partner_lookup", {"p_phone": phone, "p_limit": 20}, key)
        bnames = {p["name"] for p in (browse or [])} if isinstance(browse, list) else set()
        check("browse mode returns rows (positive control)",
              isinstance(browse, list) and len(browse) > 0, f"status {st}")
        check("browse never shows paused/restricted canaries",
              not ({f"REDTEAM Restricted Partner {MARKER}", f"REDTEAM Paused Partner {MARKER}"} & bnames))
        st, ptn = rpc("partner_lookup", {"p_phone": "19999999999", "p_query": MARKER}, key)
        check("partner_lookup unknown phone = zero rows", isinstance(ptn, list) and not ptn)
        st, _b = rpc("partner_lookup", {"p_phone": phone, "p_query": MARKER}, ANON_KEY)
        check("anon denied on partner_lookup", st in (401, 403, 404), f"status {st}")
        st, body = curl("GET", f"{BASE}/partners_catalog?select=name&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read partners_catalog",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")
        st, body = curl("GET", f"{BASE}/partner_reviews?select=app_user_id&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read partner_reviews",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")

        print("— videos source (video_search) —")
        # videos_catalog deliberately has NO video_url column: the video file's GroupOS
        # storage path is dropped at ingest and can never be selected into an answer.
        # (thumbnail_url = preview image, allowed since 2026-07-30 — checked below.)
        STORAGE_PATH = "uploads/content-archive/videos/redteam-should-never-leak.mp4"
        # PostgREST bulk insert requires an identical key set on every object.
        def vcanary(vid, name, status, access, deleted_at=None, cliff=None, files_text=None):
            return {"video_id": vid,
                    "title": f"REDTEAM {name} Video {MARKER}",
                    "description_text": f"video canary {MARKER} {name.lower()}",
                    "cliff_notes": cliff,
                    # extracted attachment text — the restricted canary carries a token that exists
                    # NOWHERE else, so "is a restricted deck searchable by its contents?" is a real
                    # test rather than a trivially-passing one
                    "files_text": files_text,
                    "duration": "10:00", "status": status, "access_restriction": access,
                    "category_names": ["Channel Calls"], "tag_names": ["Channel Call"],
                    "deleted_at": deleted_at}

        vc_canaries = [
            vcanary("feedfacefeedfacefeed1001", "Restricted", "published", "restricted",
                    files_text=f"restricted deck contents deckonly{MARKER} confidential figures"),
            vcanary("feedfacefeedfacefeed1002", "Deleted", "published", "public",
                    deleted_at="2026-01-01T00:00:00Z"),
            vcanary("feedfacefeedfacefeed1003", "Draft", "draft", "public"),
            vcanary("feedfacefeedfacefeed1004", "Public", "published", "public",
                    cliff=f"cliff canary {MARKER} takeaway"),
        ]
        st, body = curl("POST", f"{BASE}/videos_catalog", key, body=vc_canaries,
                        profile_hdr=["Content-Profile: digest", "Prefer: return=minimal"])
        check("video canaries inserted", st in (200, 201), f"status {st}: {body}")

        st, vids = rpc("video_search", {"p_phone": phone, "p_query": MARKER, "p_limit": 20}, key)
        vtitles = {v["title"] for v in (vids or [])} if isinstance(vids, list) else set()
        check("video_search positive control (public canary via search)",
              f"REDTEAM Public Video {MARKER}" in vtitles, f"status {st}, got {sorted(vtitles)}")
        # POLICY CHANGE (Andy, 2026-07-26): show the WHOLE library and caveat it, because GroupOS
        # will not say WHO may see a restricted video (GOS-25) -- hiding 395 of 1,009 made Olivia
        # look empty and hid a Centurion member's own content from them. METADATA ONLY: the checks
        # below are stricter than the old blanket hide, because 250 restricted videos carry ~10.5k
        # chars of extracted deck text each.
        rv = next((v for v in (vids or []) if v["title"] == f"REDTEAM Restricted Video {MARKER}"), None)
        check("restricted video IS returned, flagged is_restricted (Andy 2026-07-26)",
              bool(rv) and rv.get("is_restricted") is True, f"got {rv}")
        # #3 (2026-07-30): a restricted row now carries an explicit in-band [RESTRICTED VIDEO ...]
        # marker instead of an ambiguous NULL (a null read as "no description" and invited the
        # model to guess from the title). The check keeps its teeth: the ONLY allowed non-null
        # value is the fixed marker, and the canary's planted content must never appear.
        _rdesc = rv.get("description_snippet") if rv else None
        check("restricted video emits NO content (fixed marker allowed, canary text never)",
              bool(rv)
              and (_rdesc is None
                   or (str(_rdesc).startswith("[RESTRICTED VIDEO") and MARKER not in str(_rdesc)))
              and rv.get("cliff_notes_snippet") is None and rv.get("attachments") is None,
              f"got {rv}")
        check("soft-deleted video invisible",
              f"REDTEAM Deleted Video {MARKER}" not in vtitles)
        check("non-published video invisible",
              f"REDTEAM Draft Video {MARKER}" not in vtitles)
        VIDEO_KEYS = {"title", "call_type", "speakers", "description_snippet", "cliff_notes_snippet",
                      "attachments", "duration", "categories", "tags", "published_at",
                      "video_url", "matched_rank", "is_restricted"}
        check("video rows carry ONLY the allowlisted fields",
              all(set(v.keys()) == VIDEO_KEYS for v in (vids or [])))
        vblob = json.dumps(vids)
        check("GroupOS storage path never reaches the member",
              "uploads/content-archive" not in vblob and "redteam-should-never-leak" not in vblob)
        # structural: the video FILE's storage path is not even persisted, so no future RPC
        # edit can leak a downloadable. thumbnail_url IS allowed (Andy's ruling 2026-07-30:
        # restricted content is surfaced-with-a-warning, never hidden, so preview images —
        # video thumbnails, partner logos — may be stored and shown; the ban stays on
        # actual content files).
        st, cols = curl("GET", f"{BASE}/videos_catalog?video_id=eq.feedfacefeedfacefeed1004", key,
                        profile_hdr=["Accept-Profile: digest"])
        stored = set(cols[0].keys()) if isinstance(cols, list) and cols else set()
        check("videos_catalog never stores the raw video-file storage path",
              bool(stored) and "video_url" not in stored,
              f"columns: {sorted(stored)}")
        # the preview columns must hold IMAGES — a video/deck file path in there would be
        # the old leak wearing a new column name
        _CONTENT_EXT = (".mp4", ".mov", ".m4v", ".webm", ".avi", ".mp3", ".wav",
                        ".pdf", ".ppt", ".pptx", ".key", ".zip", ".doc", ".docx",
                        ".xls", ".xlsx")
        def _content_files(rows, field):
            vals = [(r.get(field) or "") for r in rows] if isinstance(rows, list) else []
            return [v for v in vals if v.lower().split("?")[0].endswith(_CONTENT_EXT)]
        st, thumbs = curl("GET",
                          f"{BASE}/videos_catalog?select=thumbnail_url&thumbnail_url=not.is.null&limit=2000",
                          key, profile_hdr=["Accept-Profile: digest"])
        check("stored video thumbnails are images, never content files",
              isinstance(thumbs, list) and not _content_files(thumbs, "thumbnail_url"),
              f"status {st}, offenders: {_content_files(thumbs, 'thumbnail_url')[:3]}")
        st, logos = curl("GET",
                         f"{BASE}/partners_catalog?select=logo_url&logo_url=not.is.null&limit=2000",
                         key, profile_hdr=["Accept-Profile: digest"])
        check("stored partner logos are images, never content files",
              isinstance(logos, list) and not _content_files(logos, "logo_url"),
              f"status {st}, offenders: {_content_files(logos, 'logo_url')[:3]}")
        check("video output carries no internal ids (speaker/event/category ids)",
              "speaker_ids" not in vblob and "event_ids" not in vblob
              and "category_ids" not in vblob and "subcategory_ids" not in vblob)
        check("video_url is the member app shape",
              all((v.get("video_url") or "").startswith("https://app.mds.co/videos/")
                  and "/admin/" not in (v.get("video_url") or "") for v in (vids or [])))
        pubv = next((v for v in (vids or []) if v["title"] == f"REDTEAM Public Video {MARKER}"), None)
        check("cliff notes surface on a reachable video (fast-follow path proven)",
              bool(pubv) and MARKER in (pubv.get("cliff_notes_snippet") or ""),
              f"cliff: {pubv.get('cliff_notes_snippet') if pubv else None}")

        # A restricted video's TITLE may surface; its CONTENTS may not. The canary carries a unique
        # token only inside its extracted attachment text -- searching that token must find nothing,
        # otherwise a 1-5M member could pull Centurion/Mastermind deck contents by keyword.
        st, deep = rpc("video_search", {"p_phone": phone, "p_query": f"deckonly{MARKER}", "p_limit": 20}, key)
        dtitles = {v["title"] for v in (deep or [])} if isinstance(deep, list) else set()
        check("restricted deck CONTENTS are not searchable (metadata-only matching)",
              f"REDTEAM Restricted Video {MARKER}" not in dtitles, f"got {sorted(dtitles)}")
        st, topical = rpc("video_search", {"p_phone": phone, "p_query": "restricted", "p_limit": 20}, key)
        ttitles = {v["title"] for v in (topical or [])} if isinstance(topical, list) else set()
        check("restricted video matched on TITLE is allowed (policy 2026-07-26)",
              isinstance(topical, list))

        st, browse = rpc("video_search", {"p_phone": phone, "p_limit": 20}, key)
        bvtitles = {v["title"] for v in (browse or [])} if isinstance(browse, list) else set()
        check("video browse mode returns rows (positive control)",
              isinstance(browse, list) and len(browse) > 0, f"status {st}")
        check("video browse never shows restricted/deleted/draft canaries",
              not ({f"REDTEAM Restricted Video {MARKER}", f"REDTEAM Deleted Video {MARKER}",
                    f"REDTEAM Draft Video {MARKER}"} & bvtitles))
        st, vids = rpc("video_search", {"p_phone": "19999999999", "p_query": MARKER}, key)
        check("video_search unknown phone = zero rows", isinstance(vids, list) and not vids)
        st, _b = rpc("video_search", {"p_phone": phone, "p_query": MARKER}, ANON_KEY)
        check("anon denied on video_search", st in (401, 403, 404), f"status {st}")
        st, body = curl("GET", f"{BASE}/videos_catalog?select=title&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read videos_catalog",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")
        st, body = curl("GET", f"{BASE}/video_speakers?select=email&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read video_speakers",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")
        st, body = curl("GET", f"{BASE}/video_files?select=storage_path&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read video_files",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")

        # attachments surface name+kind only; the GroupOS storage path stays server-side
        st, att = rpc("video_search", {"p_phone": phone, "p_limit": 20}, key)
        ablob = json.dumps(att)
        check("attachment rows carry ONLY name+kind+description",
              all(set(a.keys()) == {"name", "kind", "description"}
                  for v in (att or []) for a in (v.get("attachments") or [])),
              "an attachment carried a field beyond name/kind")
        check("attachment storage paths never reach the member",
              "uploads/content-archive" not in ablob and "storage_path" not in ablob)

        # speaker names are public (they presented to the community); their EMAIL never is
        st, spk = rpc("video_search", {"p_phone": phone, "p_query": "mogul call", "p_limit": 20}, key)
        sblob = json.dumps(spk)
        check("speaker-bearing search returns rows (positive control)",
              isinstance(spk, list) and any(v.get("speakers") for v in spk),
              f"status {st}, rows {len(spk or [])}")
        check("speaker EMAIL never reaches the member",
              "@" not in sblob.replace("\\u0040", "@"),
              "an email address appeared in video_search output")
        check("speaker user_ids / member record ids never emitted",
              "user_id" not in sblob and "member_record_id" not in sblob
              and "member_type" not in sblob and "tier_name" not in sblob)

        print("— member_billing (self-only subscription facts) —")
        st, bill = rpc("member_billing", {"p_phone": phone}, key)
        check("member_billing answers for the asker (status 200, one row)",
              st == 200 and isinstance(bill, list) and len(bill) == 1, f"status {st}")
        # +4 fields 2026-07-28: the member's own next invoice (date/amount), how often they are
        # billed, and their membership fee. All are the ASKER'S OWN record — member_billing resolves
        # the member from their phone and returns exactly one row — which is the whole point of the
        # lane. Nothing here is about another member.
        BILL_KEYS = {"membership_status", "plan_name", "plan_price", "subscription_status",
                     "billing_interval", "monthly_amount", "annual_payment", "member_since",
                     "year_joined", "next_renewal", "chapter",
                     "next_invoice_date", "next_invoice_amount", "payment_frequency", "membership_fee"}
        check("billing row carries ONLY the allowlisted self fields",
              all(set(b.keys()) == BILL_KEYS for b in (bill or [])))
        bblob = json.dumps(bill)
        check("billing output has no emails/phones/stripe urls/card data",
              "@" not in bblob and "stripe.com" not in bblob.lower() and "card" not in bblob.lower())
        st, bill = rpc("member_billing", {"p_phone": "19999999999"}, key)
        check("member_billing unknown phone = zero rows", isinstance(bill, list) and not bill)
        st, _b = rpc("member_billing", {"p_phone": phone}, ANON_KEY)
        check("anon denied on member_billing", st in (401, 403, 404), f"status {st}")

        print("— multi_source (scalable fan-out) —")
        st, mres = rpc("multi_source", {"p_phone": phone, "p_query": "logistics",
                                        "p_terms": ["logistics"],
                                        "p_want": ["partners", "members", "events", "chats"]}, key)
        check("multi_source answers for the asker (status 200, object)",
              st == 200 and isinstance(mres, dict) and len(mres) >= 1, f"status {st}")
        mchats = (mres or {}).get("chats") or []
        foreign = [c.get("chat") for c in mchats if c.get("chat") and c.get("chat") not in set(chats)]
        check("multi_source chats section stays within the asker's own chats",
              not foreign, f"foreign: {foreign[:2]}")
        mblob = json.dumps(mres)
        # sender_phone + rev_band must NEVER appear anywhere; emails are scrubbed from the
        # STRUCTURED sections, but the chats section is verbatim group content (a member's
        # own posted email/LinkedIn there is ground truth, not a leak).
        non_chat = json.dumps({k: v for k, v in (mres or {}).items() if k != "chats"})
        check("multi_source structured sections carry no email/contact fields",
              "@" not in non_chat.replace("facebook", ""))
        check("multi_source emits no sender_phone or rev_band anywhere",
              "sender_phone" not in mblob and "rev_band" not in mblob)
        st, mres2 = rpc("multi_source", {"p_phone": "19999999999", "p_query": "logistics",
                                         "p_terms": ["logistics"]}, key)
        check("multi_source unknown phone = empty object",
              isinstance(mres2, dict) and len(mres2) == 0, f"got {mres2}")
        st, _b = rpc("multi_source", {"p_phone": phone, "p_query": "logistics",
                                      "p_terms": ["logistics"]}, ANON_KEY)
        check("anon denied on multi_source", st in (401, 403, 404), f"status {st}")

        print("— app_member_feed (the mobile app's identity door, #27) —")
        # a known linked member (email + at_member_id + phone) fetched live, not hardcoded
        st, mrow = curl("GET", f"{BASE}/members?select=email,full_name&email=not.is.null"
                               f"&at_member_id=not.is.null&phone=not.is.null&limit=1", key,
                        profile_hdr=["Accept-Profile: digest"])
        if st == 200 and mrow:
            f_email, f_name = mrow[0]["email"], mrow[0].get("full_name") or ""
            st, feed = rpc("app_member_feed", {"p_email": f_email}, key)
            check("app_member_feed resolves a known email to exactly that member",
                  st == 200 and isinstance(feed, dict)
                  and ((feed.get("member") or {}).get("name") or "") == f_name, f"status {st}")
            fblob = json.dumps(feed)
            check("app_member_feed emits no sender_phone/rev_band/stripe anywhere",
                  "sender_phone" not in fblob and "rev_band" not in fblob
                  and "stripe" not in fblob.lower())
        else:
            check("app_member_feed known-member fetch", False, f"status {st}")
        st, feed2 = rpc("app_member_feed", {"p_email": "nobody+gate@example.com"}, key)
        check("app_member_feed unknown email = empty object",
              st == 200 and isinstance(feed2, dict) and len(feed2) == 0, f"got {feed2}")
        st, _b = rpc("app_member_feed", {"p_email": "nobody+gate@example.com"}, ANON_KEY)
        check("anon denied on app_member_feed", st in (401, 403, 404), f"status {st}")

        print("— attributes table itself unreachable —")
        st, body = curl("GET", f"{BASE}/member_attributes?select=rev_band&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read member_attributes",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")
        # #28: personas are owner-only — they reach a member ONLY through their own
        # identity-resolved feed; the table itself is never readable
        st, body = curl("GET", f"{BASE}/member_personas?select=persona&limit=1", ANON_KEY,
                        profile_hdr=["Accept-Profile: digest"])
        check("anon cannot read member_personas",
              st in (401, 403, 404) or (isinstance(body, list) and not body), f"status {st}")

        print("— membership status gates every door (#31) —")
        # dynamic fixture: a real Removed member with a linked phone (never hardcoded)
        st, rem = curl("GET", f"{BASE}/members?select=phone,at_member_id,email"
                              f"&phone=not.is.null&membership_status=like.Removed*&limit=1", key,
                       profile_hdr=["Accept-Profile: digest"])
        if st == 200 and rem:
            rphone = rem[0]["phone"]
            st, rows = rpc("content_search", {"p_phone": rphone, "p_terms": ["amazon"], "p_limit": 5}, key)
            check("canceled member phone gets ZERO content rows",
                  isinstance(rows, list) and not rows, f"got {len(rows or [])}")
            st, rows = rpc("partner_lookup", {"p_phone": rphone, "p_query": "tiktok"}, key)
            check("canceled member phone gets ZERO partner rows",
                  isinstance(rows, list) and not rows, f"got {len(rows or [])}")
            st, rows = rpc("chapter_info", {"p_phone": rphone}, key)
            check("canceled member phone gets ZERO chapter rows",
                  isinstance(rows, list) and not rows, f"got {len(rows or [])}")
            remail = rem[0].get("email")
            if remail:
                st, feed = rpc("app_member_feed", {"p_email": remail}, key)
                check("canceled member email gets an EMPTY app feed",
                      isinstance(feed, dict) and len(feed) == 0, f"got keys {list((feed or {}).keys())}")
            else:
                check("canceled member email gets an EMPTY app feed", True, "(fixture has no email)")
        else:
            check("canceled-member fixture found", False, f"status {st}")

        print("— at_member_id asker path (#30) —")
        st, rows = rpc("event_lookup", {"p_phone": None, "p_at_member_id": "recDOESNOTEXIST0"}, key)
        check("unknown at_member_id gets ZERO event rows",
              isinstance(rows, list) and not rows, f"got {len(rows or [])}")
        st, rem2 = curl("GET", f"{BASE}/member_attributes?select=at_member_id"
                               f"&membership_status=like.Removed*&limit=1", key,
                        profile_hdr=["Accept-Profile: digest"])
        if st == 200 and rem2:
            st, rows = rpc("content_search", {"p_phone": None, "p_terms": ["amazon"],
                                              "p_at_member_id": rem2[0]["at_member_id"]}, key)
            check("canceled at_member_id gets ZERO content rows",
                  isinstance(rows, list) and not rows, f"got {len(rows or [])}")
        else:
            check("canceled at_member_id fixture found", False, f"status {st}")
        # a phone-less ACTIVE member must be SERVED through the app door (the whole point of #30)
        st, pl = curl("GET", f"{BASE}/rpc/", key)  # no-op keepalive; fixture below
        st, plrow = curl("POST", f"{BASE}/rpc/app_member_feed", key,
                         body={"p_email": None}, profile_hdr=["Content-Profile: digest"])
        check("app_member_feed null email = empty object",
              isinstance(plrow, dict) and len(plrow) == 0, f"got {plrow}")

        print("— anon key locked out —")
        st, body = rpc("content_search", {"p_phone": phone, "p_terms": [MARKER]}, ANON_KEY)
        check("anon key denied on content_search", st in (401, 403, 404), f"status {st}")
        st, body = rpc("content_lookup", {"p_phone": phone, "p_source": "wa_digest"}, ANON_KEY)
        check("anon key denied on content_lookup", st in (401, 403, 404), f"status {st}")
    finally:
        cleanup()
        st, left = curl("GET", f"{BASE}/content_items?source=eq.{CANARY_SOURCE}&select=id", key,
                        profile_hdr=["Accept-Profile: digest"])
        check("canaries cleaned up", isinstance(left, list) and len(left) == 0, f"status {st}, left {left}")
        st, left1 = curl("GET", f"{BASE}/events_catalog?at_record_id=like.redteamevt_*&select=at_record_id",
                         key, profile_hdr=["Accept-Profile: digest"])
        st2, left2 = curl("GET", f"{BASE}/event_registrations?roster_record_id=like.redteamreg_*&select=roster_record_id",
                          key, profile_hdr=["Accept-Profile: digest"])
        check("event canaries cleaned up",
              isinstance(left1, list) and not left1 and isinstance(left2, list) and not left2,
              f"catalog left {left1}, regs left {left2}")
        st, left3 = curl("GET", f"{BASE}/partners_catalog?partner_id=like.feedface*&select=partner_id",
                         key, profile_hdr=["Accept-Profile: digest"])
        st2, left4 = curl("GET", f"{BASE}/partner_reviews?review_id=like.feedface*&select=review_id",
                          key, profile_hdr=["Accept-Profile: digest"])
        check("partner canaries cleaned up (reviews cascaded)",
              isinstance(left3, list) and not left3 and isinstance(left4, list) and not left4,
              f"catalog left {left3}, reviews left {left4}")
        st, left5 = curl("GET", f"{BASE}/videos_catalog?video_id=like.feedface*&select=video_id",
                         key, profile_hdr=["Accept-Profile: digest"])
        check("video canaries cleaned up",
              isinstance(left5, list) and not left5, f"catalog left {left5}")

    print()
    if failures:
        print(f"GATE FAILED — {len(failures)} failure(s): {failures}")
        sys.exit(1)
    print("GATE PASSED — retrieval refuses everything it must refuse.")
    sys.exit(0)


if __name__ == "__main__":
    main()
