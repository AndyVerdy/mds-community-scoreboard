#!/usr/bin/env python3
"""#103 — load the speaker identity space from videos_catalog.speaker_names.

  python3 scripts/load_speakers.py [--dry-run]

Ladder per distinct catalog name (deterministic, never guesses):
  0. speaker_aliases / existing canonical      -> existing speaker
  1. GroupOS speaker user (digest.video_speakers, matched on collapsed
     display_name) -> email through digest.resolve_member_by_email() (#100):
       resolves      -> kind=member, at_member_id   ("is or was a member -> linked")
       no resolution -> member_type GU -> guest · CO -> partner-by-name else guest
                        · M -> unresolved + review row
  2. exactly ONE ACTIVE member full-name match -> kind=member
     (>1 candidate even active-preferred       -> unresolved + review row)
  3. partners_catalog exact name               -> kind=partner
  4. else                                      -> kind=guest

member_record_id in the GroupOS mirror is GroupOS-internal (matches 0 AT
records) — EMAIL is the key, per that table's own comment. Idempotent:
canonicals and links are diffed before insert. Every pagination ordered.
"""
import argparse, csv, json, os, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
REVIEW = os.path.expanduser("~/Downloads/mds_speaker_review.csv")
ACTIVE = {"Current Member", "New Member", "Pending Group Entrance",
          "Current Member- Not Renewing"}


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def supa(method, path, body=None, prefer=None):
    cmd = ["curl", "-s", "-m", "120", "-X", method, f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    out = subprocess.run(cmd, capture_output=True, text=True,
                         input=json.dumps(body) if body is not None else None).stdout
    if not out.strip():
        return []
    val = json.loads(out)
    if isinstance(val, dict) and "code" in val:
        sys.exit(f"{method} {path}: {val}")
    return val


def supa_all(path, order):
    rows, off = [], 0
    while True:
        page = supa("GET", f"{path}&order={order}&limit=1000&offset={off}")
        rows += page
        if len(page) < 1000:
            return rows
        off += 1000


def rpc_resolve(email):
    if not email or not email.strip():
        return None
    out = supa("POST", "rpc/resolve_member_by_email", {"p_email": email.strip()})
    return out if isinstance(out, str) and out else None


def canon(name):
    n = re.sub(r"\s*\([^)]*\)\s*$", "", name)      # strip trailing "(Carbon6)"
    return re.sub(r"\s+", " ", n).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    vids = supa_all("videos_catalog?select=video_id,speaker_names&deleted_at=is.null"
                    "&speaker_names=not.is.null", "video_id")
    gos = supa_all("video_speakers?select=user_id,display_name,email,member_type",
                   "user_id")
    go_by_name = {}
    for g in gos:
        go_by_name.setdefault(canon(g["display_name"] or ""), []).append(g)
    members = supa_all("member_profiles?select=at_member_id,at_fields", "at_member_id")
    statuses = {r["at_member_id"]: r["membership_status"] for r in supa_all(
        "member_attributes?select=at_member_id,membership_status", "at_member_id")}
    by_name = {}
    for m in members:
        fn = canon((m.get("at_fields") or {}).get("Full Name")
                   or (m.get("at_fields") or {}).get("Name") or "")
        if fn:
            by_name.setdefault(fn, []).append(m["at_member_id"])
    partners = {canon(p["name"]): p["partner_id"] for p in supa_all(
        "partners_catalog?select=partner_id,name", "partner_id")}

    existing = {s["canonical"] for s in supa_all(
        "speakers?select=canonical", "speaker_id")}
    aliases = {a["alias_canonical"]: a["speaker_id"] for a in supa_all(
        "speaker_aliases?select=alias_canonical,speaker_id", "alias_canonical")}
    have_links = {(l["video_id"], l["speaker_id"]) for l in supa_all(
        "video_speaker_links?select=video_id,speaker_id", "video_id")}

    name_videos = {}
    for v in vids:
        for i, raw in enumerate(v.get("speaker_names") or []):
            nm = re.sub(r"\s+", " ", raw).strip()
            if nm:
                name_videos.setdefault(nm, []).append((v["video_id"], i))

    decided, review = {}, []
    stats = {"member": 0, "partner": 0, "guest": 0, "unresolved": 0, "existing": 0}
    for nm in sorted(name_videos):
        c = canon(nm)
        if not c:
            continue
        if c in existing or c in aliases or c in decided:
            stats["existing"] += 1
            continue
        go = go_by_name.get(c, [])
        if go:
            g = go[0]
            at = rpc_resolve(g.get("email"))
            if at:
                decided[c] = ("member", at, None, g["user_id"], "groupos_email", nm)
            elif g.get("member_type") == "GU":
                decided[c] = ("guest", None, None, g["user_id"], "groupos_guest", nm)
            elif g.get("member_type") == "CO":
                pid = partners.get(c)
                decided[c] = (("partner", None, pid, g["user_id"], "groupos_co", nm)
                              if pid else
                              ("guest", None, None, g["user_id"], "groupos_co_noPartner", nm))
            else:
                decided[c] = ("unresolved", None, None, g["user_id"],
                              "groupos_M_email_unresolved", nm)
                review.append((nm, "groupos M, email unresolved",
                               ";".join(x[0] for x in name_videos[nm][:5])))
        else:
            cands = by_name.get(c, [])
            active = [a for a in cands if statuses.get(a) in ACTIVE]
            if len(active) == 1:
                decided[c] = ("member", active[0], None, None, "name_match", nm)
            elif len(cands) >= 1:
                decided[c] = ("unresolved", None, None, None, "name_ambiguous", nm)
                review.append((nm, ";".join(cands),
                               ";".join(x[0] for x in name_videos[nm][:5])))
            elif c in partners:
                decided[c] = ("partner", None, partners[c], None, "partner_name", nm)
            else:
                decided[c] = ("guest", None, None, None, "no_match", nm)
        stats[decided[c][0]] += 1

    print(f"catalog names: {len(name_videos)} raw / "
          f"{len(set(canon(n) for n in name_videos if canon(n)))} canonical · "
          f"new speakers: {len(decided)} · {stats} · review rows: {len(review)}")
    if args.dry_run:
        for c, d in sorted(decided.items())[:20]:
            print(f"  {d[0]:<10} {d[5]:<40} {d[4]}")
        print("DRY RUN — no writes")
        return

    rows = [{"display_name": d[5], "canonical": c, "kind": d[0],
             "at_member_id": d[1], "partner_id": d[2], "groupos_user_id": d[3],
             "note": d[4]} for c, d in decided.items()]
    for i in range(0, len(rows), 200):
        supa("POST", "speakers", rows[i:i + 200], prefer="return=minimal")

    sid = {s["canonical"]: s["speaker_id"] for s in supa_all(
        "speakers?select=speaker_id,canonical", "speaker_id")}
    links = []
    for nm, vlist in name_videos.items():
        c = canon(nm)
        s = sid.get(c) or aliases.get(c)
        if not s:
            continue
        for vid, ordn in vlist:
            if (vid, s) not in have_links:
                links.append({"video_id": vid, "speaker_id": s, "ordinal": ordn})
                have_links.add((vid, s))
    for i in range(0, len(links), 500):
        supa("POST", "video_speaker_links", links[i:i + 500], prefer="return=minimal")
    print(f"speakers inserted: {len(rows)} · links inserted: {len(links)}")

    if review:
        with open(REVIEW, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["speaker_name", "detail", "sample_videos"])
            w.writerows(review)
        print(f"review file: {REVIEW} ({len(review)} rows)")


if __name__ == "__main__":
    main()
