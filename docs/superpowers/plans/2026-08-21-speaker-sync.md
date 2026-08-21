# #103 Speaker Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every video speaker becomes ONE linked entity — member speakers link to their `at_member_id`, company/partner speakers to `partner_id`, everyone else recorded as a guest — same person, same entity, across every appearance (Andy 2026-08-21: "Same means same").

**Architecture:** Three warehouse tables (`digest.speakers` identity space, `digest.speaker_aliases` variant spellings, `digest.video_speaker_links` links — `digest.video_speakers` was DISCOVERED mid-plan as an existing GroupOS mirror of 234 speaker USER accounts and becomes the PRIMARY evidence source). Ladder: catalog name → GroupOS speaker user → email through `resolve_member_by_email()` (#100) → member link ("is or was a member → linked", Andy); unresolved emails fall to member_type (GU→guest, CO→partner-ish, M→review); the ~9 names GroupOS lacks use exact-active-name/partner/guest. `member_record_id` in the mirror is GroupOS-internal (matches 0 AT records) — email is the key, per the mirror's own comment. Ambiguity goes to a review CSV, never a guess. No workflow/prompt changes in this ticket.

**Tech Stack:** Supabase Postgres (digest schema) via MCP `apply_migration` for DDL; Python 3 + curl (repo pattern — urllib has no cert store on this Mac) for loader/verify; PostgREST REST for data ops.

## Global Constraints

- Credentials from `/Users/Born/mds-digest-web/.env.local` (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`). Never hardcode, never print.
- Every PostgREST pagination carries `order=` (pages are UNSTABLE without it).
- Loaders diff-before-insert — expression indexes can't be ON CONFLICT targets via PostgREST.
- CREATE OR REPLACE, never DROP, for any existing function (DROP discards the ACL). New tables need no PostgREST RPC.
- Ambiguity NEVER guesses: a name matching >1 active member goes to the review CSV with `kind='unresolved'` — linking the wrong member is worse than not linking.
- Member matching prefers the ACTIVE record (same posture as `resolve_member_by_email`, #100); `digest.is_active_member_status()` is the authority.
- After every migration: `python3 scripts/db_export_schema.py`, commit the diff.
- Gate (`scripts/olivia_leak_gate.py`) EXIT 0 before claiming done — never `| tail`.
- Baseline truth (measured 2026-08-21): 413/1,033 videos carry `speaker_names`; 239 distinct raw names; GroupOS `video_speakers` mirror covers 230/239 by display_name (234 users: 170 M · 63 GU · 1 CO, all with email; 209 emails resolve via #100). `member_record_id` = GroupOS-internal, never an AT id. Verify against these.
- The link table is `digest.video_speaker_links` (NOT `video_speakers` — that name is taken by the GroupOS user mirror).

---

### Task 1: Schema — speakers, speaker_aliases, video_speakers

**Files:**
- Create: migration `speaker_entities_20260821` (via MCP apply_migration)
- Modify: none

**Interfaces:**
- Produces: `digest.speakers(speaker_id bigint generated always as identity PK, display_name text not null, canonical text not null unique, kind text check in ('member','partner','guest','unresolved'), at_member_id text null, partner_id text null, note text null, created_at timestamptz default now())`
- Produces: `digest.speaker_aliases(alias_canonical text PK, speaker_id bigint not null references digest.speakers)`
- Produces: `digest.video_speakers(video_id text not null, speaker_id bigint not null references digest.speakers, source text not null default 'catalog', ordinal int, primary key (video_id, speaker_id))`

- [ ] **Step 1: Apply the migration**

```sql
-- #103: speaker identity space. One person = one row, forever ("same means same",
-- Andy 2026-08-21). kind='member' carries at_member_id; kind='partner' carries
-- partner_id (company listed AS the speaker); kind='guest' is a recorded non-member
-- human; kind='unresolved' = matched >1 member record even after active-preference —
-- review file promotes these, code never guesses.
create table digest.speakers (
  speaker_id   bigint generated always as identity primary key,
  display_name text not null,
  canonical    text not null unique,
  kind         text not null check (kind in ('member','partner','guest','unresolved')),
  at_member_id text,
  partner_id   text,
  note         text,
  created_at   timestamptz not null default now(),
  constraint speakers_member_has_id  check (kind <> 'member'  or at_member_id is not null),
  constraint speakers_partner_has_id check (kind <> 'partner' or partner_id  is not null)
);
comment on table digest.speakers is
  '#103 speaker identity space (2026-08-21). canonical = lower(collapsed display_name). Same human/company across all videos = one row. unresolved = ambiguous member name awaiting review, never auto-linked.';

create table digest.speaker_aliases (
  alias_canonical text primary key,
  speaker_id      bigint not null references digest.speakers(speaker_id)
);
comment on table digest.speaker_aliases is
  '#103 variant spellings -> one speaker. Loader consults aliases BEFORE creating a new speaker, so a variant never becomes a second person.';

create table digest.video_speakers (
  video_id   text   not null,
  speaker_id bigint not null references digest.speakers(speaker_id),
  source     text   not null default 'catalog',
  ordinal    int,
  primary key (video_id, speaker_id)
);
comment on table digest.video_speakers is
  '#103 video->speaker links. source=catalog (videos_catalog.speaker_names). video_id has no FK: videos_catalog is a mirror that re-syncs; links survive re-sync and verify_speakers.py checks orphans instead.';
create index video_speakers_speaker_idx on digest.video_speakers (speaker_id);
```

- [ ] **Step 2: Verify tables exist and are empty**

Run (MCP execute_sql):
```sql
select (select count(*) from digest.speakers) s,
       (select count(*) from digest.speaker_aliases) a,
       (select count(*) from digest.video_speakers) v;
```
Expected: `0,0,0`.

- [ ] **Step 3: Re-export db/ and commit**

```bash
python3 scripts/db_export_schema.py
git add db/ && git commit -m "#103 Task 1: speaker identity schema — speakers/aliases/video_speakers"
```

### Task 2: Loader — scripts/load_speakers.py

**Files:**
- Create: `scripts/load_speakers.py`

**Interfaces:**
- Consumes: Task 1's tables; `digest.videos_catalog.speaker_names`; `digest.member_profiles.at_fields->>'Full Name'`; `digest.member_attributes.membership_status`; `digest.partners_catalog(partner_id,name)`.
- Produces: populated `speakers` + `video_speakers`; review CSV `~/Downloads/mds_speaker_review.csv` (name · candidate at_member_ids · videos); `canon(name)` normalization = `lower(regexp collapse whitespace, strip trailing parenthetical)`.

- [ ] **Step 1: Write the loader**

```python
#!/usr/bin/env python3
"""#103 — load the speaker identity space from videos_catalog.speaker_names.

  python3 scripts/load_speakers.py [--dry-run]

Ladder per distinct name (deterministic, never guesses):
  1. alias table hit                        -> existing speaker
  2. exactly ONE ACTIVE member full-name    -> kind=member, at_member_id
     (multi-record humans: active-preferred like resolve_member_by_email;
      still >1 active -> kind=unresolved + review CSV row)
  3. partners_catalog name match (exact-ish)-> kind=partner, partner_id
  4. else                                   -> kind=guest
Idempotent: existing canonical/link rows are diffed before insert (expression
indexes cannot be ON CONFLICT targets via PostgREST). Every pagination ordered.
"""
import argparse, csv, json, os, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
REVIEW = os.path.expanduser("~/Downloads/mds_speaker_review.csv")


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


def canon(name):
    n = re.sub(r"\s*\([^)]*\)\s*$", "", name)      # strip trailing "(Carbon6)"
    return re.sub(r"\s+", " ", n).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    vids = supa_all("videos_catalog?select=video_id,speaker_names&deleted_at=is.null"
                    "&speaker_names=not.is.null", "video_id")
    members = supa_all("member_profiles?select=at_member_id,at_fields", "at_member_id")
    statuses = {r["at_member_id"]: r["membership_status"] for r in supa_all(
        "member_attributes?select=at_member_id,membership_status", "at_member_id")}
    ACTIVE = {"Current Member", "New Member", "Pending Group Entrance",
              "Current Member- Not Renewing"}
    by_name = {}
    for m in members:
        fn = canon((m.get("at_fields") or {}).get("Full Name")
                   or (m.get("at_fields") or {}).get("Name") or "")
        if fn:
            by_name.setdefault(fn, []).append(m["at_member_id"])
    partners = {canon(p["name"]): p["partner_id"] for p in supa_all(
        "partners_catalog?select=partner_id,name", "partner_id")}

    existing = {s["canonical"]: s for s in supa_all(
        "speakers?select=speaker_id,canonical,kind", "speaker_id")}
    aliases = {a["alias_canonical"]: a["speaker_id"] for a in supa_all(
        "speaker_aliases?select=alias_canonical,speaker_id", "alias_canonical")}
    have_links = {(l["video_id"], l["speaker_id"]) for l in supa_all(
        "video_speakers?select=video_id,speaker_id", "video_id")}

    # distinct names + their videos, ordinal = position in the video's list
    name_videos = {}
    for v in vids:
        for i, raw in enumerate(v.get("speaker_names") or []):
            nm = re.sub(r"\s+", " ", raw).strip()
            if nm:
                name_videos.setdefault(nm, []).append((v["video_id"], i))

    new_speakers, review, stats = [], [], {"member": 0, "partner": 0,
                                           "guest": 0, "unresolved": 0, "existing": 0}
    decided = {}   # canonical -> (kind, at_member_id, partner_id, display)
    for nm in sorted(name_videos):
        c = canon(nm)
        if c in existing or c in aliases or c in decided:
            stats["existing"] += c in existing or c in aliases
            continue
        cands = by_name.get(c, [])
        active = [a for a in cands if statuses.get(a) in ACTIVE]
        if len(active) == 1:
            decided[c] = ("member", active[0], None, nm)
        elif len(cands) >= 1:
            decided[c] = ("unresolved", None, None, nm)
            review.append((nm, ";".join(cands),
                           ";".join(x[0] for x in name_videos[nm][:5])))
        elif c in partners:
            decided[c] = ("partner", None, partners[c], nm)
        else:
            decided[c] = ("guest", None, None, nm)
        stats[decided[c][0]] += 1

    print(f"names: {len(name_videos)} distinct · new: {len(decided)} "
          f"({stats}) · review rows: {len(review)}")
    if args.dry_run:
        for c, d in list(decided.items())[:15]:
            print(" ", d[0], "·", d[3])
        print("DRY RUN — no writes")
        return

    for c, (kind, at_id, p_id, disp) in decided.items():
        supa("POST", "speakers", [{"display_name": disp, "canonical": c,
                                   "kind": kind, "at_member_id": at_id,
                                   "partner_id": p_id}],
             prefer="return=minimal")
    sid = {s["canonical"]: s["speaker_id"] for s in supa_all(
        "speakers?select=speaker_id,canonical", "speaker_id")}
    links = []
    for nm, vlist in name_videos.items():
        s = sid.get(canon(nm)) or aliases.get(canon(nm))
        if not s:
            continue
        for vid, ordn in vlist:
            if (vid, s) not in have_links:
                links.append({"video_id": vid, "speaker_id": s, "ordinal": ordn})
                have_links.add((vid, s))
    for i in range(0, len(links), 500):
        supa("POST", "video_speakers", links[i:i + 500], prefer="return=minimal")
    print(f"speakers upserted: {len(decided)} · links inserted: {len(links)}")

    if review:
        with open(REVIEW, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["speaker_name", "candidate_at_member_ids", "sample_videos"])
            w.writerows(review)
        print(f"review file: {REVIEW} ({len(review)} rows)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry-run — counts must reconcile with the baseline**

```bash
python3 scripts/load_speakers.py --dry-run
```
Expected: `names: 239 distinct`; member ≈ 145, unresolved ≈ 29, partner ≈ up to 11, guest = remainder. Investigate any drift beyond ±3 before applying (canonicalization can merge a couple of raw variants — that is the point, not a bug).

- [ ] **Step 3: Apply**

```bash
python3 scripts/load_speakers.py
```
Expected: `speakers upserted` ≈ distinct canonicals; `links inserted` > 0; review CSV written with the unresolved names.

- [ ] **Step 4: Commit**

```bash
git add scripts/load_speakers.py
git commit -m "#103 Task 2: speaker loader — ladder member/partner/guest, ambiguity to review CSV"
```

### Task 3: Verification — scripts/verify_speakers.py

**Files:**
- Create: `scripts/verify_speakers.py`

**Interfaces:**
- Consumes: Task 1 tables, Task 2 data.
- Produces: exit 0 = all PASS / exit 1 = any FAIL, printed check-by-check (repo convention: `verify_video_access.py`).

- [ ] **Step 1: Write the verifier**

```python
#!/usr/bin/env python3
"""#103 — verify the speaker identity space. exit 0 = all PASS."""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")
FAILS = []


def supa_all(path, order):
    rows, off = [], 0
    while True:
        out = subprocess.run(
            ["curl", "-s", "-m", "120",
             f"{BASE}/{path}&order={order}&limit=1000&offset={off}",
             "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
             "-H", "Accept-Profile: digest"],
            capture_output=True, text=True).stdout
        page = json.loads(out)
        if isinstance(page, dict):
            sys.exit(f"GET {path}: {page}")
        rows += page
        if len(page) < 1000:
            return rows
        off += 1000


def check(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL':4}  {name} — {detail}")
    if not ok:
        FAILS.append(name)


speakers = supa_all("speakers?select=speaker_id,canonical,kind,at_member_id,partner_id",
                    "speaker_id")
links = supa_all("video_speakers?select=video_id,speaker_id", "video_id")
vids = supa_all("videos_catalog?select=video_id,speaker_names&deleted_at=is.null"
                "&speaker_names=not.is.null", "video_id")

canons = [s["canonical"] for s in speakers]
check("same-means-same", len(canons) == len(set(canons)),
      f"{len(canons)} rows, {len(set(canons))} distinct canonicals")

kinds = {}
for s in speakers:
    kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
check("kind integrity",
      all((s["kind"] != "member" or s["at_member_id"]) and
          (s["kind"] != "partner" or s["partner_id"]) for s in speakers),
      f"kinds={kinds}")

sids = {s["speaker_id"] for s in speakers}
check("links resolve", all(l["speaker_id"] in sids for l in links),
      f"{len(links)} links")

linked_videos = {l["video_id"] for l in links}
cat_videos = {v["video_id"] for v in vids}
missing = cat_videos - linked_videos
check("video coverage", len(missing) == 0,
      f"{len(linked_videos)}/{len(cat_videos)} speaker-carrying videos linked"
      + (f" · missing {sorted(missing)[:3]}" if missing else ""))

members = supa_all("member_attributes?select=at_member_id,membership_status",
                   "at_member_id")
mset = {m["at_member_id"] for m in members}
check("member links exist",
      all(s["at_member_id"] in mset for s in speakers if s["kind"] == "member"),
      f"{kinds.get('member', 0)} member links")

by = [s for s in speakers if s["canonical"] == "brandon young"]
bl = [l for l in links if by and l["speaker_id"] == by[0]["speaker_id"]]
check("brandon young one entity", len(by) == 1 and len(bl) >= 9,
      f"{len(by)} entity, {len(bl)} video links")

unres = kinds.get("unresolved", 0)
check("unresolved bounded", unres <= 35, f"{unres} awaiting review (baseline ~29)")

print(f"\n{len(FAILS)} FAIL / {7 - len(FAILS)} PASS")
sys.exit(1 if FAILS else 0)
```

- [ ] **Step 2: Run it**

```bash
python3 scripts/verify_speakers.py
```
Expected: `7 PASS`, exit 0. A `video coverage` FAIL means some raw name canonicalized to empty or collided — inspect that name by hand before touching code.

- [ ] **Step 3: Gate**

```bash
python3 scripts/olivia_leak_gate.py
```
Expected: GATE PASSED, exit 0 (new tables carry no member-facing surface yet; the gate proves nothing regressed).

- [ ] **Step 4: Commit**

```bash
git add scripts/verify_speakers.py
git commit -m "#103 Task 3: speaker verification — 7 checks incl. same-means-same"
```

### Task 4: Close — db export, board, docs

**Files:**
- Modify: `OLIVIA_SPRINT_4.md` (#103 close block)
- Modify: `db/` (re-export)

- [ ] **Step 1: Re-export db/ (tables changed in Task 1; belt-and-braces after data load)**

```bash
python3 scripts/db_export_schema.py
```

- [ ] **Step 2: Board close block** — #103 section gets: results (speakers by kind, links, review count), AC checklist (one entity per person ✅ · members linked ✅ · partners linked ✅ · guests recorded ✅ · ambiguity in review file not guessed ✅), before/after (0 links → N links; raw strings → entity space), verify 7/7, gate exit 0.

- [ ] **Step 3: Commit**

```bash
git add OLIVIA_SPRINT_4.md db/
git commit -m "#103 CLOSED: speaker identity space live — same-means-same, members/partners/guests linked"
```
