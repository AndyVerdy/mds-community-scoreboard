#!/usr/bin/env python3
"""#103 — build the speaker identity space from the video catalog.

  python3 scripts/load_speakers.py [--dry-run]          # rungs A+B (ids, then names)
  python3 scripts/load_speakers.py --rescan [--dry-run] # promote guest -> member
  python3 scripts/load_speakers.py --coverage           # library coverage by year

EVIDENCE RUNGS, strongest first (2026-08-21 rebuild — v1 used names only and
closed on a field-scoped metric; speaker_ids is a real ID join and was ignored):

  A. videos_catalog.speaker_ids -> digest.video_speakers.user_id (GroupOS mirror)
     -> email -> digest.resolve_member_by_email() (#100) -> at_member_id.
     Structural: no name guessing at all. 409 of 452 id-carrying videos resolve.
  B. videos_catalog.speaker_names (videos with no usable ids): GroupOS name match
     -> email -> resolver; else exactly ONE ACTIVE member of that name; else
     partners_catalog exact name; else guest.

Identity key is canon(display_name), so two GroupOS accounts for one human collapse
to ONE speaker (4 such display names exist) and their extra user_id is recorded as
an alias, never a second person. Ambiguity (>1 candidate member) is written to the
review CSV as kind='unresolved' — the loader never guesses.

Conflicts (a name-rung link that the id rung contradicts) are REPORTED, never
silently overwritten.
"""
import argparse, csv, datetime, json, os, re, subprocess, sys

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
    payload = json.dumps(body) if body is not None else None
    out = subprocess.run(cmd, capture_output=True, text=True, input=payload).stdout
    if not out.strip() and prefer and "representation" in prefer:
        # empty body on a representation request = transport hiccup, not success
        out = subprocess.run(cmd, capture_output=True, text=True, input=payload).stdout
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
    if not email or not str(email).strip():
        return None
    out = supa("POST", "rpc/resolve_member_by_email", {"p_email": str(email).strip()})
    return out if isinstance(out, str) and out else None


def canon(name):
    n = re.sub(r"\s*\([^)]*\)\s*$", "", str(name or ""))
    return re.sub(r"\s+", " ", n).strip().lower()


# --- rung C: names that live in the TITLE / DESCRIPTION, not in a field ---------
# 616 of 1,033 videos carry no usable speaker field; their speaker is in the title
# ("… － Nick Barnett － Expert Call") or the description ("In this session, Josh
# Taekman discusses …"). Fullwidth － is the house separator; a bare hyphen only
# splits when spaced, so hyphenated surnames survive.
DASH = re.compile(r"[–—－]|(?<=\s)-(?=\s)")
TOPIC = re.compile(
    r"\b(amazon|tiktok|walmart|shopify|temu|ranking|strateg|tactic|listing|optimiz|"
    r"shop|growth|sales|revenue|fba|awd|ads?|ppc|seo|retail|ai|launch|hiring|systems?|"
    r"logistics|deep dive|dash|profit|margin|cash|crypto|trading|brand|product|exit|"
    r"inventory|scaling|founder|challenge|playbook|masterclass|panel|discussion|session|"
    r"call|summit|inspire|chapter|boardroom|mastermind|workshop|q&a|mds|apac|emea|wmds|"
    r"20\d\d|january|february|march|april|may|june|july|august|september|october|"
    r"november|december|part \d|vol)\b", re.I)
NAMEISH = re.compile(r"^[A-Z][A-Za-z.'’\-]+(?:\s+[A-Z][A-Za-z.'’\-]+){1,2}$")
DESC_LEAD = re.compile(
    r"(?:in this (?:session|call|talk|video)|join|with)[,:]?\s+"
    r"([A-Z][A-Za-z.'’\-]+(?:\s+[A-Z][A-Za-z.'’\-]+){1,2})")


def names_from_title(title, people=(), topic_tokens=frozenset()):
    """Person-shaped segments of a title, topic segments rejected.

    A name already in the people dictionary is accepted outright. An UNKNOWN name
    must additionally avoid every corpus topic token — words that recur across many
    titles are subjects, not surnames ("Account Health and Seller Performance" used
    to yield a speaker called "Seller Performance")."""
    out = []
    for seg in DASH.split(title or ""):
        seg = seg.strip(" ,.:;")
        if not seg or TOPIC.search(seg):
            continue
        for part in re.split(r"\s*(?:,|&| and )\s*", seg):
            part = part.strip(" ,.:;")
            if not NAMEISH.match(part) or not (7 <= len(part) <= 40) or TOPIC.search(part):
                continue
            low = part.lower()
            # reject only when EVERY token is a corpus topic word ("Seller
            # Performance"); a recurring FIRST name ("Nick") must not veto a real
            # surname ("Nick Barnett") — that mistake cost 40+ real speakers.
            toks = low.split()
            if low in people or not all(t in topic_tokens for t in toks):
                out.append(part)
    return out


class World:
    """Everything the ladder consults, loaded once."""

    def __init__(self):
        self.videos = supa_all(
            "videos_catalog?select=video_id,speaker_ids,speaker_names,title,"
            "description_text,app_created_at&deleted_at=is.null", "video_id")
        gos = supa_all("video_speakers?select=user_id,display_name,email,member_type",
                       "user_id")
        self.go_by_id = {g["user_id"]: g for g in gos}
        self.go_by_name = {}
        for g in gos:
            self.go_by_name.setdefault(canon(g["display_name"]), []).append(g)
        self.statuses = {r["at_member_id"]: r["membership_status"] for r in supa_all(
            "member_attributes?select=at_member_id,membership_status", "at_member_id")}
        self.by_name = {}
        for m in supa_all("member_profiles?select=at_member_id,at_fields", "at_member_id"):
            f = m.get("at_fields") or {}
            for key in ("Full Name", "Name", "Preferred Name"):
                nm = canon(f.get(key) or "")
                if nm:
                    self.by_name.setdefault(nm, set()).add(m["at_member_id"])
        self.partners = {canon(p["name"]): p["partner_id"] for p in supa_all(
            "partners_catalog?select=partner_id,name", "partner_id")}
        self.speakers = {s["canonical"]: s for s in supa_all(
            "speakers?select=speaker_id,canonical,display_name,kind,at_member_id,"
            "partner_id,groupos_user_id,note", "speaker_id")}
        self.aliases = {a["alias_canonical"]: a["speaker_id"] for a in supa_all(
            "speaker_aliases?select=alias_canonical,speaker_id", "alias_canonical")}
        self.links = {(l["video_id"], l["speaker_id"]) for l in supa_all(
            "video_speaker_links?select=video_id,speaker_id", "video_id")}
        self.plinks = {(l["video_id"], l["partner_id"]) for l in supa_all(
            "video_partner_links?select=video_id,partner_id", "video_id")}
        # dictionary of KNOWN people for title/description matching: member full and
        # preferred names + GroupOS speaker accounts. Two-token minimum with every
        # token >= 2 chars — the Members DB holds junk rows like "A A".
        bad = {"mds community", "mds only", "mds member", "test test"}
        # junk_label speakers stay as rows (annotated) but never link again
        self.junk = {s["canonical"] for s in supa_all(
            "speakers?select=canonical,note&note=like.junk_label*", "speaker_id")}
        self.people = {}
        for nm in list(self.by_name) + list(self.go_by_name):
            t = nm.split()
            if len(t) >= 2 and all(len(x) >= 2 for x in t) and len(nm) >= 7 and nm not in bad:
                self.people[nm] = re.compile(r"\b" + re.escape(nm) + r"\b")
        tok = {}
        for v in self.videos:
            for t in set(re.findall(r"[A-Za-z][A-Za-z'’\-]+",
                                    (v.get("title") or "").lower())):
                tok[t] = tok.get(t, 0) + 1
        self.topic_tokens = {t for t, c in tok.items() if c >= 6}
        # Partner mentions: a partner whose NAME is built from topic words ("TikTok
        # Shop", "Amazon Freight") can never be evidence of a partner session, and a
        # single-word partner name ("Process") only counts when it appears in its own
        # capitalisation — otherwise every use of the plain word matches.
        self.ppats = {}
        for p in self.partners:
            if len(p) < 5 or any(x in self.topic_tokens for x in p.split()):
                continue
            proper = " ".join(x.capitalize() for x in p.split())
            flags = 0 if len(p.split()) == 1 else re.I
            self.ppats[p] = re.compile(r"\b" + re.escape(proper) + r"\b", flags)

    def classify_from_go(self, g):
        """GroupOS mirror row -> (kind, at_member_id, partner_id, note)."""
        at = rpc_resolve(g.get("email"))
        if at:
            return "member", at, None, "groupos_email"
        mt = g.get("member_type")
        if mt == "CO":
            pid = self.partners.get(canon(g["display_name"]))
            return ("partner", None, pid, "groupos_co") if pid else \
                   ("guest", None, None, "groupos_co_noPartner")
        if mt == "GU":
            return "guest", None, None, "groupos_guest"
        return "unresolved", None, None, "groupos_M_email_unresolved"

    def classify_from_name(self, nm):
        c = canon(nm)
        go = self.go_by_name.get(c)
        if go:
            return self.classify_from_go(go[0])
        cands = self.by_name.get(c, set())
        active = [a for a in cands if self.statuses.get(a) in ACTIVE]
        if len(active) == 1:
            return "member", active[0], None, "name_match"
        if cands:
            return "unresolved", None, None, "name_ambiguous"
        if c in self.partners:
            return "partner", None, self.partners[c], "partner_name"
        return "guest", None, None, "no_match"


def upsert_speaker(w, display, kind, at_id, pid, note, go_id, dry, conflicts):
    """Return speaker_id for canon(display), creating or upgrading in place."""
    c = canon(display)
    if not c:
        return None
    sid = w.aliases.get(c)
    ex = w.speakers.get(c)
    if ex:
        sid = ex["speaker_id"]
        # id-rung evidence outranks a name-rung guess; conflicts are reported.
        stronger = note.startswith("groupos") and not str(ex.get("note") or "").startswith("groupos")
        if ex["kind"] != kind or (at_id and ex.get("at_member_id") != at_id):
            if ex["kind"] == "member" and kind == "member" and at_id and ex["at_member_id"] != at_id:
                # Two member records for ONE human (known AT duplicate-human class).
                # ACTIVE record wins — same posture as resolve_member_by_email (#100);
                # the loser is recorded in note, never deleted (standing rule).
                old_active = w.statuses.get(ex["at_member_id"]) in ACTIVE
                new_active = w.statuses.get(at_id) in ACTIVE
                keep, drop = ((at_id, ex["at_member_id"]) if new_active and not old_active
                              else (ex["at_member_id"], at_id))
                conflicts.append((display, ex["at_member_id"], at_id, f"{note} -> kept {keep}"))
                if keep != ex["at_member_id"] and not dry:
                    supa("PATCH", f"speakers?speaker_id=eq.{sid}",
                         {"at_member_id": keep,
                          "note": f"{ex.get('note') or ''}; dup-human, kept active {keep}, alt {drop}"},
                         prefer="return=minimal")
                    ex["at_member_id"] = keep
                return sid
            if stronger or ex["kind"] in ("guest", "unresolved"):
                patch = {"kind": kind, "at_member_id": at_id, "partner_id": pid,
                         "note": f"{ex.get('note') or ''}; {note} {datetime.date.today()}"}
                if go_id:
                    patch["groupos_user_id"] = go_id
                if not dry:
                    supa("PATCH", f"speakers?speaker_id=eq.{sid}", patch,
                         prefer="return=minimal")
                ex.update(patch)
        elif go_id and not ex.get("groupos_user_id") and not dry:
            supa("PATCH", f"speakers?speaker_id=eq.{sid}", {"groupos_user_id": go_id},
                 prefer="return=minimal")
        return sid
    if sid:
        return sid
    if dry:
        w.speakers[c] = {"speaker_id": -1, "canonical": c, "kind": kind,
                         "at_member_id": at_id, "note": note}
        return -1
    row = supa("POST", "speakers", [{"display_name": str(display).strip(),
                                     "canonical": c, "kind": kind,
                                     "at_member_id": at_id, "partner_id": pid,
                                     "groupos_user_id": go_id, "note": note}],
               prefer="return=representation")
    new = row[0] if isinstance(row, list) and row else None
    if not new:
        sys.exit(f"insert failed for {display}")
    w.speakers[c] = new
    return new["speaker_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rescan", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    args = ap.parse_args()

    if args.coverage:
        coverage()
        return

    w = World()
    if args.rescan:
        rescan(w, args.dry_run)
        return

    new_links, new_plinks, conflicts, review = [], [], [], []
    stats = {"A_ids": 0, "B_names": 0, "C_text": 0, "D_partner": 0, "unresolvable_id": 0}
    for v in w.videos:
        vid = v["video_id"]
        ids = [i for i in (v.get("speaker_ids") or []) if i]
        used_ids = False
        for ordn, sid_ext in enumerate(ids):
            g = w.go_by_id.get(sid_ext)
            if not g:
                stats["unresolvable_id"] += 1
                continue
            kind, at, pid, note = w.classify_from_go(g)
            sp = upsert_speaker(w, g["display_name"], kind, at, pid, note,
                                g["user_id"], args.dry_run, conflicts)
            if sp and (vid, sp) not in w.links:
                new_links.append({"video_id": vid, "speaker_id": sp,
                                  "source": "speaker_ids", "ordinal": ordn})
                w.links.add((vid, sp))
            used_ids = True
            stats["A_ids"] += 1
            if kind == "unresolved":
                review.append((g["display_name"], "groupos M, email unresolved", vid))
        used_names = False
        if not used_ids:
            for ordn, nm in enumerate(v.get("speaker_names") or []):
                if not canon(nm):
                    continue
                kind, at, pid, note = w.classify_from_name(nm)
                sp = upsert_speaker(w, nm, kind, at, pid, note, None,
                                    args.dry_run, conflicts)
                if sp and (vid, sp) not in w.links:
                    new_links.append({"video_id": vid, "speaker_id": sp,
                                      "source": "catalog", "ordinal": ordn})
                    w.links.add((vid, sp))
                used_names = True
                stats["B_names"] += 1
                if kind == "unresolved":
                    review.append((nm, "ambiguous name", vid))

        # ---- rung C: title / description, for the videos no field covers -------
        title, desc = v.get("title") or "", v.get("description_text") or ""
        if not used_ids and not used_names:
            tl, dl = title.lower(), desc.lower()
            found = [(nm, "title_known") for nm in w.people if w.people[nm].search(tl)]
            if not found:
                found = [(p, "title_position")
                         for p in names_from_title(title, w.people, w.topic_tokens)]
            if not found:
                found = [(nm, "desc_known") for nm in w.people if w.people[nm].search(dl)]
            if not found:
                m = DESC_LEAD.search(desc)
                if m and not TOPIC.search(m.group(1)):
                    found = [(m.group(1), "desc_lead")]
            for ordn, (nm, ev) in enumerate(dict.fromkeys(found)):
                if canon(nm) in w.junk:
                    continue
                kind, at, pid, note = w.classify_from_name(nm)
                sp = upsert_speaker(w, nm, kind, at, pid, f"{ev}:{note}", None,
                                    args.dry_run, conflicts)
                if sp and (vid, sp) not in w.links:
                    new_links.append({"video_id": vid, "speaker_id": sp,
                                      "source": ev, "ordinal": ordn})
                    w.links.add((vid, sp))
                stats["C_text"] += 1

        # ---- rung D: partner sessions — link the VIDEO to the partner ----------
        hay = f"{title} {desc}"
        for p, pat in w.ppats.items():
            if pat.search(hay) and (vid, w.partners[p]) not in w.plinks:
                new_plinks.append({"video_id": vid, "partner_id": w.partners[p],
                                   "source": "title" if pat.search(title)
                                             else "description"})
                w.plinks.add((vid, w.partners[p]))
                stats["D_partner"] += 1

    print(f"rung A (speaker_ids): {stats['A_ids']} links considered · "
          f"unresolvable ids: {stats['unresolvable_id']}")
    print(f"rung B (speaker_names): {stats['B_names']} links considered")
    print(f"rung C (title/description): {stats['C_text']} links considered")
    print(f"rung D (partner sessions): {stats['D_partner']} video-partner links")
    print(f"new links: {len(new_links)} · conflicts: {len(conflicts)}")
    for c in conflicts[:10]:
        print(f"  CONFLICT {c[0]}: had {c[1]}, id-rung says {c[2]} ({c[3]})")
    if args.dry_run:
        print("DRY RUN — no writes")
        return
    for i in range(0, len(new_links), 500):
        supa("POST", "video_speaker_links", new_links[i:i + 500], prefer="return=minimal")
    for i in range(0, len(new_plinks), 500):
        supa("POST", "video_partner_links", new_plinks[i:i + 500], prefer="return=minimal")
    print(f"speaker links inserted: {len(new_links)} · partner links: {len(new_plinks)}")
    if review:
        with open(REVIEW, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["speaker_name", "detail", "video_id"])
            wr.writerows(review)
        print(f"review file: {REVIEW} ({len(review)} rows)")
    coverage()


def rescan(w, dry):
    """Yesterday's guest becomes today's member: promote IN PLACE, links intact."""
    spk = [s for s in w.speakers.values() if s["kind"] in ("guest", "unresolved")]
    promoted = 0
    for s in spk:
        at = None
        go = w.go_by_name.get(s["canonical"])
        if go:
            at = rpc_resolve(go[0].get("email"))
        if not at:
            active = [a for a in w.by_name.get(s["canonical"], set())
                      if w.statuses.get(a) in ACTIVE]
            at = active[0] if len(active) == 1 else None
        if at:
            promoted += 1
            print(f"  promote {s['display_name']} ({s['kind']} -> member, {at})")
            if not dry:
                supa("PATCH", f"speakers?speaker_id=eq.{s['speaker_id']}",
                     {"kind": "member", "at_member_id": at,
                      "note": f"{s.get('note') or ''}; promoted {datetime.date.today()}"},
                     prefer="return=minimal")
    print(f"rescan: {len(spk)} guest/unresolved checked · {promoted} promoted"
          + (" (DRY RUN)" if dry else ""))


def coverage():
    """LIBRARY coverage by year — the metric that matters, not field coverage."""
    vids = supa_all("videos_catalog?select=video_id,app_created_at&deleted_at=is.null",
                    "video_id")
    linked = {l["video_id"] for l in supa_all(
        "video_speaker_links?select=video_id", "video_id")}
    by_year = {}
    for v in vids:
        y = (v["app_created_at"] or "")[:4]
        t, c = by_year.get(y, (0, 0))
        by_year[y] = (t + 1, c + (1 if v["video_id"] in linked else 0))
    print("\nLIBRARY COVERAGE (videos with >=1 linked speaker):")
    tot = cov = 0
    for y in sorted(by_year):
        t, c = by_year[y]
        tot += t
        cov += c
        print(f"  {y}: {c:>4}/{t:<4} {100*c//t if t else 0:>3}%")
    print(f"  ALL: {cov}/{tot} {100*cov//tot if tot else 0}%")


if __name__ == "__main__":
    main()
