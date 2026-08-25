#!/usr/bin/env python3
"""Link a member's hidden-number WhatsApp id to their MDS record (#146).

WHY THIS EXISTS
WhatsApp now lets a member hide their phone number. When they do, Meta delivers their message with no
number at all — only an opaque country-prefixed id such as `CA.1068099432261958`. Millie identifies
members by phone, so an unpaired id means she cannot tell who is writing. Since 2026-08-25 she answers
those members honestly instead of falling silent, but she still cannot recognise them until the id is
paired with their member record once. That is what this script does.

Pairs are learned automatically for anyone whose number IS visible (the id and the number arrive
together, and `digest.member_wa_ids` is backfilled from that). This script is for the other case: a
member whose number has never reached us.

HOW TO FIND THE ID
A member reports "Millie is not answering". Run with --find and the time they wrote (their local clock
is fine, give it in UTC):

    python3 scripts/olivia_link_wa_id.py --find --since 2026-08-25T02:50:00Z

It prints every inbound in that window that arrived WITHOUT a phone, newest first, with the id decoded
out of the wamid. Match it to the member by the time they said they wrote.

THEN LINK IT — always confirm with a human who the member is before running this. An id is an identity;
pairing the wrong one hands someone another member's chats.

    python3 scripts/olivia_link_wa_id.py --uid CA.1068099432261958 --phone 14169033267

The phone must already belong to an ACTIVE member (that check is the point: this script cannot invent
membership, only connect an id to a member who is already there). It prints the resolved member and the
front-door result so the link is proven, not assumed.

    python3 scripts/olivia_link_wa_id.py --list          # every pairing on file
    python3 scripts/olivia_link_wa_id.py --unlink <uid>  # remove one (a wrong link is an identity leak)
"""
import argparse, base64, json, re, subprocess, sys, importlib.util

REPO = "/Users/Born/Scorecard"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/"

spec = importlib.util.spec_from_file_location("g", f"{REPO}/scripts/olivia_leak_gate.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
KEY = g.load_key()


def rest(method, path, body=None):
    cmd = ["curl", "-s", "-X", method, BASE + path, "-H", "Accept-Profile: digest",
           "-H", "Content-Profile: digest", "-H", "Content-Type: application/json",
           "-H", "apikey: " + KEY, "-H", "Authorization: Bearer " + KEY,
           "-H", "Prefer: return=representation"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    out = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        return out


def rpc(fn, body):
    return rest("POST", "rpc/" + fn, body)


def uid_from_wamid(wamid):
    """The sender id is base64'd inside the wamid: wamid.HBgT<b64>… -> 'CA.1068099432261958'."""
    m = re.match(r"wamid\.([A-Za-z0-9+/=]+)", str(wamid) or "")
    if not m:
        return None
    raw = m.group(1)
    for cut in range(4, 40):
        try:
            dec = base64.b64decode(raw[cut:cut + 32] + "==", validate=False).decode("utf-8", "ignore")
        except Exception:
            continue
        hit = re.search(r"[A-Z]{2}\.\d{6,}", dec)
        if hit:
            return hit.group(0)
    return None


def cmd_find(args):
    rows = rest("GET", f"olivia_seen?select=wamid,phone,seen_at&phone=is.null"
                       f"&seen_at=gte.{args.since}&order=seen_at.desc&limit=50")
    if not rows:
        print("No phone-less inbounds since", args.since,
              "— if the member still got no answer, the cause is something else.")
        return 0
    print(f"{len(rows)} inbound(s) with NO phone since {args.since} — newest first:\n")
    for r in rows:
        uid = uid_from_wamid(r["wamid"]) or "(could not decode — read the raw wamid)"
        linked = rest("GET", f"member_wa_ids?select=at_member_id&wa_user_id=eq.{uid}") if uid else []
        state = f"already linked to {linked[0]['at_member_id']}" if linked else "NOT LINKED"
        print(f"  {r['seen_at']}  {uid}   [{state}]")
    print("\nConfirm with the member (or an admin) which one is theirs, then --uid <id> --phone <number>.")
    return 0


def cmd_link(args):
    phone = re.sub(r"\D", "", args.phone)
    who = rpc("resolve_asker", {"p_phone": phone})
    if not who or who == "null":
        print(f"REFUSED: {phone} does not resolve to an active member. Fix the membership or the number "
              f"first — this script links an id to a member, it never creates one.")
        return 1
    fd = rpc("olivia_front_door", {"p_phone": phone})
    name = (fd[0].get("full_name") if isinstance(fd, list) and fd else None) or "(name not on file)"
    status = (fd[0].get("membership_status") if isinstance(fd, list) and fd else None) or "?"
    print(f"member: {name} · {status} · {who}")
    rest("POST", "member_wa_ids?on_conflict=wa_user_id",
         [{"wa_user_id": args.uid, "phone": phone, "at_member_id": who, "source": "admin_link"}])
    check = rpc("resolve_asker_by_uid", {"p_user_id": args.uid})
    door = rpc("olivia_front_door_v2", {"p_phone": None, "p_user_id": args.uid})
    ok = (check == who) and isinstance(door, list) and len(door) == 1
    print(f"linked {args.uid} -> {who}")
    print(f"verify: resolve_asker_by_uid={check} · front_door_v2 rows={len(door) if isinstance(door,list) else '?'}"
          f" · {'OK' if ok else 'NOT PROVEN — investigate before telling the member'}")
    return 0 if ok else 1


def cmd_list(_args):
    rows = rest("GET", "member_wa_ids?select=wa_user_id,phone,at_member_id,source,last_seen"
                       "&order=last_seen.desc&limit=500")
    print(f"{len(rows)} pairing(s)")
    for r in rows[:40]:
        print(f"  {r['wa_user_id']:<26} {r['phone'] or '-':<15} {r['at_member_id'] or '(unmapped)':<20} {r['source']}")
    if len(rows) > 40:
        print(f"  … {len(rows)-40} more")
    return 0


def cmd_unlink(args):
    rest("DELETE", f"member_wa_ids?wa_user_id=eq.{args.unlink}")
    left = rest("GET", f"member_wa_ids?select=wa_user_id&wa_user_id=eq.{args.unlink}")
    print("removed" if not left else "STILL PRESENT — check permissions")
    return 0 if not left else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--find", action="store_true", help="list inbounds that arrived with no phone")
    ap.add_argument("--since", default="2026-01-01T00:00:00Z", help="window start for --find (UTC)")
    ap.add_argument("--uid", help="the WhatsApp opaque id, e.g. CA.1068099432261958")
    ap.add_argument("--phone", help="the member's phone, digits only")
    ap.add_argument("--list", action="store_true", help="show every pairing on file")
    ap.add_argument("--unlink", help="remove a pairing by id")
    a = ap.parse_args()
    if a.find:
        return cmd_find(a)
    if a.list:
        return cmd_list(a)
    if a.unlink:
        return cmd_unlink(a)
    if a.uid and a.phone:
        return cmd_link(a)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
