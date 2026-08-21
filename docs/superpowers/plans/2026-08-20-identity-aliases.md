# Identity Aliases (#100) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recognise a member by every email address they have ever used with MDS, so an email-keyed grant made under a second address still resolves to them.

**Architecture:** One new table, `digest.member_email_alias`, holds `(at_member_id, email, source)` rows built from three evidence rungs — the member's Preferred Email, their `Stripe Customer Email`, and Airtable's `Associated Emails (Admin)` field. A fourth rung, name matching, only ever *proposes* rows into a review CSV; a human approves them and they are written back to Airtable, which stays the system of record. One SQL resolver, `digest.resolve_member_by_email()`, is the single entry point everything else uses.

**Tech Stack:** Postgres (Supabase project `nadtudwuwjhckotrngzn`, schema `digest`), Python 3 scripts driving the PostgREST API over `curl` (house pattern — see `scripts/load_org_docs.py`), Airtable REST for the write-back.

## Global Constraints

- Credentials come from `/Users/Born/mds-digest-web/.env.local`. Keys: `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `AIRTABLE_PAT`. Never hardcode a key; never print one.
- Supabase REST base is `https://nadtudwuwjhckotrngzn.supabase.co/rest/v1` with headers `Accept-Profile: digest` and `Content-Profile: digest`.
- **`CREATE OR REPLACE` for functions, never `DROP` + `CREATE`.** A drop resets EXECUTE to PUBLIC and ships an anon-callable RPC.
- Every new function: `SECURITY DEFINER`, `SET search_path TO 'digest', 'pg_temp'`, then `revoke all on function … from public;` and `grant execute on function … to service_role;`.
- **After any migration:** `python3 scripts/db_export_schema.py`, then `git diff db/` as the code review, then commit `db/`.
- **Before claiming anything ships:** `python3 scripts/olivia_leak_gate.py` must exit 0.
- Emails compare as `lower(btrim(email))` everywhere. Never compare raw.
- A name match is a **proposal**, never a grant. `andy test` matches a real member record — that is the false positive this rule exists to stop.
- Airtable is the system of record for `Associated Emails (Admin)`. Supabase holds a mirror, never the master.
- Scripts take `--dry-run` and print what they would change. Re-running a backfill must change zero rows.

---

## File Structure

| File | Responsibility |
|---|---|
| `db/tables.sql` (regenerated) | The `member_email_alias` table definition, exported from live |
| `db/functions/` (regenerated) | `resolve_member_by_email` |
| `scripts/load_member_email_aliases.py` | Backfill rungs 1–3 into the table; idempotent; `--dry-run` |
| `scripts/propose_member_email_aliases.py` | Rung 4 — name matching → review CSV. Grants nothing. |
| `scripts/writeback_member_email_aliases.py` | Applies an approved review CSV to Airtable `Associated Emails (Admin)` |
| `scripts/verify_member_aliases.py` | The ticket's ACs as pass/fail checks; exit 0 / 1 |

---

### Task 1: The alias table

**Files:**
- Migration: applied via the Supabase MCP `apply_migration`, name `member_email_alias_20260820`
- Modify (regenerated): `db/tables.sql`
- Test: `scripts/verify_member_aliases.py` (created here, extended in later tasks)

**Interfaces:**
- Produces: table `digest.member_email_alias(at_member_id text, email text, source text, added_at timestamptz)`, unique on `(at_member_id, lower(btrim(email)))`, and a plain index on `lower(btrim(email))`.

- [ ] **Step 1: Write the failing check**

Create `scripts/verify_member_aliases.py`:

```python
#!/usr/bin/env python3
"""#100 — verify the identity alias layer.

Run:  python3 scripts/verify_member_aliases.py     # exit 0 = all PASS, exit 1 = any FAIL
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def get(path):
    cmd = ["curl", "-s", "-m", "60", f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"GET {path} failed: {out[:300]}")


results, fails = [], []


def check(name, ok, detail):
    results.append(name)
    if not ok:
        fails.append(name)
    print(f"{name:<28} {'PASS' if ok else 'FAIL':<6} {detail}")


rows = get("member_email_alias?select=at_member_id&limit=1")
check("table exists", isinstance(rows, list), f"got {type(rows).__name__}")

print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 scripts/verify_member_aliases.py`
Expected: FAIL — PostgREST returns an error object, not a list, because the table does not exist.

- [ ] **Step 3: Create the table**

Apply this migration (Supabase MCP `apply_migration`, name `member_email_alias_20260820`):

```sql
create table if not exists digest.member_email_alias (
  at_member_id text not null,
  email        text not null,
  source       text not null check (source in ('preferred','stripe','admin_field','name_match_approved')),
  added_at     timestamptz not null default now()
);

create unique index if not exists member_email_alias_uq
  on digest.member_email_alias (at_member_id, lower(btrim(email)));

create index if not exists member_email_alias_email_idx
  on digest.member_email_alias (lower(btrim(email)));

comment on table digest.member_email_alias is
  '#100 Every email address known to belong to a member. source records the evidence: preferred = the Members-DB Preferred Email; stripe = Stripe Customer Email (payment record); admin_field = Airtable "Associated Emails (Admin)"; name_match_approved = a name match a human approved. Airtable stays the system of record — this table is a mirror. Read via digest.resolve_member_by_email().';

alter table digest.member_email_alias enable row level security;
```

- [ ] **Step 4: Run the check to verify it passes**

Run: `python3 scripts/verify_member_aliases.py`
Expected: `1/1 PASS`

- [ ] **Step 5: Re-export the schema and commit**

```bash
python3 scripts/db_export_schema.py
git diff db/
git add db scripts/verify_member_aliases.py
git commit -m "#100: digest.member_email_alias — the identity alias table"
```

---

### Task 2: Backfill rungs 1–3

**Files:**
- Create: `scripts/load_member_email_aliases.py`
- Modify: `scripts/verify_member_aliases.py`

**Interfaces:**
- Consumes: `digest.member_email_alias` from Task 1.
- Produces: `python3 scripts/load_member_email_aliases.py [--dry-run]`, filling `source` in `('preferred','stripe','admin_field')`. Reads `digest.member_profiles` (`at_member_id`, `email`, `at_fields`).

Reference numbers measured 2026-08-20, for the run report to be checked against: 5,972 profiles, 5,717 with a Preferred Email, 827 with a `Stripe Customer Email` of which **10 differ** from preferred, and **8** with `Associated Emails (Admin)` populated.

- [ ] **Step 1: Write the failing checks**

Append to `scripts/verify_member_aliases.py`, before the summary print:

```python
alias = get("member_email_alias?select=at_member_id,email,source&limit=20000")
by_source = {}
for r in alias:
    by_source[r["source"]] = by_source.get(r["source"], 0) + 1

check("preferred rung loaded", by_source.get("preferred", 0) >= 5700,
      f"{by_source.get('preferred', 0)} rows")
check("stripe rung loaded", by_source.get("stripe", 0) >= 10,
      f"{by_source.get('stripe', 0)} rows")
check("admin_field rung loaded", by_source.get("admin_field", 0) >= 8,
      f"{by_source.get('admin_field', 0)} rows")

# Ryan Bastuba: preferred ryan@varify.com, Stripe ryan@bastuba.com
ryan = get("member_email_alias?select=at_member_id,source&email=ilike.ryan@bastuba.com")
check("stripe alias resolves", len(ryan) == 1 and ryan[0]["source"] == "stripe",
      f"{ryan}")

# Michael Corrigan: Associated Emails (Admin) holds michael@trtl.co.uk
mc = get("member_email_alias?select=at_member_id,source&email=ilike.michael@trtl.co.uk")
check("admin_field alias resolves", len(mc) == 1 and mc[0]["source"] == "admin_field",
      f"{mc}")
```

- [ ] **Step 2: Run to verify the new checks fail**

Run: `python3 scripts/verify_member_aliases.py`
Expected: FAIL on all five new checks — the table is empty.

- [ ] **Step 3: Write the loader**

Create `scripts/load_member_email_aliases.py`:

```python
#!/usr/bin/env python3
"""#100 — backfill digest.member_email_alias from the three evidenced rungs.

  python3 scripts/load_member_email_aliases.py [--dry-run]

Rungs, in order of authority:
  preferred     member_profiles.email                              — the Members-DB Preferred Email
  stripe        at_fields->>'Stripe Customer Email'                — a payment record
  admin_field   at_fields->>'Associated Emails (Admin)'            — recorded by an admin

Name matches are NOT loaded here. They are proposals: see
scripts/propose_member_email_aliases.py. Idempotent — a second run changes zero rows.
"""
import argparse, json, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
EMAIL_RE = re.compile(r"[^\s,;<>]+@[^\s,;<>]+\.[^\s,;<>]+")


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


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
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    if not out.strip():
        return []
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"{method} {path} failed: {out[:300]}")


def fetch_profiles():
    rows, offset = [], 0
    while True:
        page = supa("GET", f"member_profiles?select=at_member_id,email,at_fields"
                           f"&order=at_member_id&limit=1000&offset={offset}")
        if not isinstance(page, list):
            sys.exit(f"unexpected profiles page: {str(page)[:300]}")
        rows += page
        if len(page) < 1000:
            return rows
        offset += 1000


def clean(v):
    return (v or "").strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    profiles = fetch_profiles()
    seen, rows = set(), []

    def add(mid, email, source):
        e = clean(email)
        if not e or "@" not in e:
            return
        key = (mid, e)
        if key in seen:
            return
        seen.add(key)
        rows.append({"at_member_id": mid, "email": e, "source": source})

    for p in profiles:
        mid = p.get("at_member_id")
        if not mid:
            continue
        f = p.get("at_fields") or {}
        add(mid, p.get("email"), "preferred")
        add(mid, f.get("Stripe Customer Email"), "stripe")
        for m in EMAIL_RE.findall(f.get("Associated Emails (Admin)") or ""):
            add(mid, m, "admin_field")

    counts = {}
    for r in rows:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    print(f"profiles read: {len(profiles)}")
    print(f"alias rows to upsert: {len(rows)}  {counts}")

    if args.dry_run:
        print("dry run — nothing written")
        return

    for i in range(0, len(rows), 500):
        supa("POST", "member_email_alias", rows[i:i + 500],
             prefer="resolution=ignore-duplicates,return=minimal")
    print("done")


main()
```

- [ ] **Step 4: Dry run, then load**

```bash
python3 scripts/load_member_email_aliases.py --dry-run
python3 scripts/load_member_email_aliases.py
```

Expected dry run: `profiles read: 5972` and an alias row count near 5,735 with `preferred` ≈ 5,717, `stripe` ≈ 10, `admin_field` ≈ 8. (`stripe` and `admin_field` rows equal to a member's preferred address are deduped by `add()`, which is why stripe shows ~10 rather than 827.)

- [ ] **Step 5: Run the checks to verify they pass**

Run: `python3 scripts/verify_member_aliases.py`
Expected: `6/6 PASS`

- [ ] **Step 6: Prove idempotence**

```bash
python3 scripts/load_member_email_aliases.py
python3 scripts/verify_member_aliases.py
```

Expected: identical counts — the unique index absorbs the re-insert.

- [ ] **Step 7: Commit**

```bash
git add scripts/load_member_email_aliases.py scripts/verify_member_aliases.py
git commit -m "#100: backfill member_email_alias from preferred, stripe and admin_field"
```

---

### Task 3: The resolver

**Files:**
- Migration: `resolve_member_by_email_20260820`
- Modify (regenerated): `db/functions/`
- Modify: `scripts/verify_member_aliases.py`

**Interfaces:**
- Produces: `digest.resolve_member_by_email(p_email text) returns text` — the `at_member_id`, or NULL when the address is unknown or ambiguous.

- [ ] **Step 1: Write the failing checks**

Append to `scripts/verify_member_aliases.py`, before the summary print:

```python
def rpc(fn, body):
    cmd = ["curl", "-s", "-m", "60", "-X", "POST", f"{BASE}/rpc/{fn}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Content-Profile: digest", "-H", "Content-Type: application/json",
           "--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"rpc {fn} failed: {out[:300]}")


andy = rpc("resolve_member_by_email", {"p_email": "andy.verdy1@gmail.com"})
check("resolver: preferred", andy == "recCUUw8iiUnJjac1", f"{andy}")

alias_hit = rpc("resolve_member_by_email", {"p_email": "ryan@bastuba.com"})
pref_hit = rpc("resolve_member_by_email", {"p_email": "ryan@varify.com"})
check("resolver: alias == preferred", alias_hit is not None and alias_hit == pref_hit,
      f"alias={alias_hit} preferred={pref_hit}")

check("resolver: case/space insensitive",
      rpc("resolve_member_by_email", {"p_email": "  Ryan@Bastuba.com "}) == alias_hit,
      "mixed case + padding")

check("resolver: unknown is null",
      rpc("resolve_member_by_email", {"p_email": "nobody@example.invalid"}) is None,
      "unknown address")
```

- [ ] **Step 2: Run to verify the new checks fail**

Run: `python3 scripts/verify_member_aliases.py`
Expected: FAIL — the RPC does not exist.

- [ ] **Step 3: Create the resolver**

Apply this migration (`resolve_member_by_email_20260820`):

```sql
create or replace function digest.resolve_member_by_email(p_email text)
returns text
language sql
stable
security definer
set search_path to 'digest', 'pg_temp'
as $$
  select case when count(distinct a.at_member_id) = 1
              then min(a.at_member_id) end
    from digest.member_email_alias a
   where lower(btrim(a.email)) = lower(btrim(p_email))
     and nullif(btrim(p_email), '') is not null
$$;

revoke all on function digest.resolve_member_by_email(text) from public;
grant execute on function digest.resolve_member_by_email(text) to service_role;
```

Ambiguity returns NULL on purpose: one address mapping to two members is a data defect, and guessing which one would attach a grant to the wrong person.

- [ ] **Step 4: Reload PostgREST, then run the checks**

In the Supabase MCP, run:

```sql
notify pgrst, 'reload schema';
```

Then call the RPC over REST three times in a row before trusting a result — a stale connection-pool cache produces *intermittent* 404s that look exactly like a random regression:

```bash
for i in 1 2 3; do
  curl -s -X POST "$(grep '^SUPABASE_URL=' /Users/Born/mds-digest-web/.env.local | cut -d= -f2- | tr -d '"'"'"'')/rest/v1/rpc/resolve_member_by_email" \
    -H "apikey: $(grep '^SUPABASE_SECRET_KEY=' /Users/Born/mds-digest-web/.env.local | cut -d= -f2- | tr -d '"'"'"'')" \
    -H "Authorization: Bearer $(grep '^SUPABASE_SECRET_KEY=' /Users/Born/mds-digest-web/.env.local | cut -d= -f2- | tr -d '"'"'"'')" \
    -H "Content-Profile: digest" -H "Content-Type: application/json" \
    --data-binary '{"p_email":"andy.verdy1@gmail.com"}'; echo; done
```

Expected: `"recCUUw8iiUnJjac1"` three times, no 404.

Run: `python3 scripts/verify_member_aliases.py`
Expected: `10/10 PASS`

- [ ] **Step 5: Re-export and commit**

```bash
python3 scripts/db_export_schema.py
git diff db/
git add db scripts/verify_member_aliases.py
git commit -m "#100: digest.resolve_member_by_email — one email-to-member entry point"
```

---

### Task 4: Name-match proposals (grants nothing)

**Files:**
- Create: `scripts/propose_member_email_aliases.py`
- Modify: `scripts/verify_member_aliases.py`

**Interfaces:**
- Consumes: `digest.resolve_member_by_email` from Task 3.
- Produces: `python3 scripts/propose_member_email_aliases.py <audience_pairs.csv> --out review.csv`, writing columns `member_at_member_id,member_name,member_email,unresolved_email,unresolved_name,videos,approve`.

The input is the GroupOS audience export `mds_video_audience_pairs.csv` (columns include `video_id`, `email`, `name`, `real_match`). Only rows with a non-empty `real_match` count — a `panel_only` row is an admin-panel phantom and grants nothing in the app.

- [ ] **Step 1: Write the failing check**

Append to `scripts/verify_member_aliases.py`, before the summary print:

```python
# A name match must never become a grant on its own.
andytest = get("member_email_alias?select=at_member_id,source&source=eq.name_match_approved")
approved_emails = {r["email"] for r in get(
    "member_email_alias?select=email&source=eq.name_match_approved")} if andytest else set()
check("no unapproved name grants",
      all(r["source"] != "name_match" for r in alias),
      "source vocabulary excludes bare name matches")
```

- [ ] **Step 2: Run to verify it passes trivially, then write the proposer**

Run: `python3 scripts/verify_member_aliases.py`
Expected: PASS — the CHECK constraint from Task 1 makes a bare `name_match` source impossible to insert. This check is a regression guard, not a red test.

- [ ] **Step 3: Write the proposer**

Create `scripts/propose_member_email_aliases.py`:

```python
#!/usr/bin/env python3
"""#100 — propose email aliases by name match. GRANTS NOTHING.

  python3 scripts/propose_member_email_aliases.py mds_video_audience_pairs.csv --out review.csv

Reads a GroupOS audience export, keeps only rows with a real (not panel-only) match,
drops every address that already resolves, and for what remains looks for a member whose
full_name matches exactly after folding. Each hit becomes a row in the review CSV with
approve left blank for a human.

'andy test' matches a real member record. That is why nothing here writes to the database.
"""
import argparse, csv, json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


BASE = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
KEY = env("SUPABASE_SECRET_KEY")


def get(path):
    cmd = ["curl", "-s", "-m", "120", f"{BASE}/{path}",
           "-H", f"Authorization: Bearer {KEY}", "-H", f"apikey: {KEY}",
           "-H", "Accept-Profile: digest"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"GET {path} failed: {out[:300]}")


def fold(s):
    return " ".join((s or "").lower().split())


ap = argparse.ArgumentParser()
ap.add_argument("pairs_csv")
ap.add_argument("--out", required=True)
args = ap.parse_args()

rows = [r for r in csv.DictReader(open(args.pairs_csv)) if r.get("real_match")]
counts, names = {}, {}
for r in rows:
    e = (r.get("email") or "").strip().lower()
    if not e:
        continue
    counts[e] = counts.get(e, 0) + 1
    names.setdefault(e, r.get("name") or "")

known = set()
for i in range(0, 40000, 1000):
    page = get(f"member_email_alias?select=email&limit=1000&offset={i}")
    if not page:
        break
    known |= {(r["email"] or "").strip().lower() for r in page}

members = []
for i in range(0, 40000, 1000):
    page = get(f"member_profiles?select=at_member_id,full_name,email&limit=1000&offset={i}")
    if not page:
        break
    members += page
by_name = {}
for m in members:
    by_name.setdefault(fold(m.get("full_name")), []).append(m)

out = []
for e, n in sorted(names.items()):
    if e in known:
        continue
    cands = by_name.get(fold(n), [])
    if len(cands) != 1:
        continue
    m = cands[0]
    out.append({"member_at_member_id": m["at_member_id"], "member_name": m.get("full_name"),
                "member_email": m.get("email"), "unresolved_email": e,
                "unresolved_name": n, "videos": counts[e], "approve": ""})

with open(args.out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["member_at_member_id", "member_name", "member_email",
                                      "unresolved_email", "unresolved_name", "videos", "approve"])
    w.writeheader()
    w.writerows(sorted(out, key=lambda r: -r["videos"]))

print(f"unresolved addresses: {len({e for e in names if e not in known})}")
print(f"proposals written:    {len(out)} -> {args.out}")
print("Nothing was written to the database. Mark approve=yes and run writeback.")
```

- [ ] **Step 4: Run it against the real export**

```bash
python3 scripts/propose_member_email_aliases.py \
  "/Users/Born/Downloads/mds_video_audience_pairs.csv" \
  --out /Users/Born/Downloads/mds_alias_review.csv
```

Expected: the ten known cases appear — Michelle Xu, Michael Corrigan, Ryan Bastuba, Guido Reyes, Jason Ko, Michael Hartman, Kyle Goguen, June Lai, David Ghiyam, Justin Cao — minus any already resolved by Task 2 (Ryan via stripe, Michael Corrigan via admin_field), so roughly **8 rows**, plus name-matched rows from the wider unresolved tail.

- [ ] **Step 5: Commit**

```bash
git add scripts/propose_member_email_aliases.py scripts/verify_member_aliases.py
git commit -m "#100: name-match proposals into a review CSV — grants nothing"
```

---

### Task 5: Airtable write-back — **needs Andy's explicit approval before running**

**Files:**
- Create: `scripts/writeback_member_email_aliases.py`
- Modify: `scripts/verify_member_aliases.py`

**Interfaces:**
- Consumes: the review CSV from Task 4 with `approve` filled in.
- Produces: `python3 scripts/writeback_member_email_aliases.py review.csv [--dry-run]` — appends approved addresses to Airtable `Associated Emails (Admin)` on the Members DB (`appou5JVr0WIrioWS`), then re-reads the field to confirm, then inserts matching `name_match_approved` rows locally.

**Do not run this task's Step 4 without Andy saying yes.** It writes to the system of record.

- [ ] **Step 1: Establish the existing field format**

```bash
python3 - <<'PY'
import json,subprocess
ENV="/Users/Born/mds-digest-web/.env.local"
def env(k):
    for l in open(ENV):
        if l.startswith(k+"="): return l.split("=",1)[1].strip().strip('"').strip("'")
BASE=env("SUPABASE_URL").rstrip("/")+"/rest/v1"; KEY=env("SUPABASE_SECRET_KEY")
cmd=["curl","-s",f"{BASE}/member_profiles?select=full_name,at_fields&limit=5000",
     "-H",f"Authorization: Bearer {KEY}","-H",f"apikey: {KEY}","-H","Accept-Profile: digest"]
for r in json.loads(subprocess.run(cmd,capture_output=True,text=True).stdout):
    v=(r.get("at_fields") or {}).get("Associated Emails (Admin)")
    if v: print(repr(v), "|", r["full_name"])
PY
```

Expected: the 8 populated values. Read them and match their separator convention exactly — do not invent one. Record the convention in a comment at the top of the write-back script.

- [ ] **Step 2: Write the write-back script**

Create `scripts/writeback_member_email_aliases.py`:

```python
#!/usr/bin/env python3
"""#100 — write approved aliases back to Airtable, then mirror them locally.

  python3 scripts/writeback_member_email_aliases.py review.csv [--dry-run]

Airtable's "Associated Emails (Admin)" is the system of record. Per approved row this
reads the field, appends the address only if absent, PATCHes, RE-READS to confirm the
value landed, and only then inserts source='name_match_approved' into
digest.member_email_alias. Any failure stops the run — a half-written alias set is worse
than none. SEPARATOR is set from the existing 8 populated values (Task 5 Step 1).
"""
import argparse, csv, json, subprocess, sys, time

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE_ID = "appou5JVr0WIrioWS"
FIELD = "Associated Emails (Admin)"
SEPARATOR = "\n"          # confirm against the existing 8 values before running


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


SUPA = env("SUPABASE_URL").rstrip("/") + "/rest/v1"
SKEY = env("SUPABASE_SECRET_KEY")
ATPAT = env("AIRTABLE_PAT")


def curl(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    if not out.strip():
        return {}
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"request failed: {out[:400]}")


def at_table_id():
    meta = curl(["curl", "-s", f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables",
                 "-H", f"Authorization: Bearer {ATPAT}"])
    for t in meta.get("tables", []):
        if any(f["name"] == FIELD for f in t.get("fields", [])):
            return t["id"]
    sys.exit(f'no table in {BASE_ID} has a "{FIELD}" field')


def at_get(tid, rec):
    return curl(["curl", "-s", f"https://api.airtable.com/v0/{BASE_ID}/{tid}/{rec}",
                 "-H", f"Authorization: Bearer {ATPAT}"])


def at_patch(tid, rec, value):
    return curl(["curl", "-s", "-X", "PATCH",
                 f"https://api.airtable.com/v0/{BASE_ID}/{tid}/{rec}",
                 "-H", f"Authorization: Bearer {ATPAT}",
                 "-H", "Content-Type: application/json",
                 "--data-binary", json.dumps({"fields": {FIELD: value}})])


def supa_insert(rows):
    curl(["curl", "-s", "-X", "POST", f"{SUPA}/member_email_alias",
          "-H", f"Authorization: Bearer {SKEY}", "-H", f"apikey: {SKEY}",
          "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
          "-H", "Content-Type: application/json",
          "-H", "Prefer: resolution=ignore-duplicates,return=minimal",
          "--data-binary", json.dumps(rows)])


ap = argparse.ArgumentParser()
ap.add_argument("review_csv")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

approved = [r for r in csv.DictReader(open(args.review_csv))
            if (r.get("approve") or "").strip().lower() in ("y", "yes", "true", "1")]
if not approved:
    sys.exit("no rows marked approve=yes — nothing to do")

tid = at_table_id()
print(f"table {tid} · {len(approved)} approved rows")

done = []
for r in approved:
    rec, addr = r["member_at_member_id"], r["unresolved_email"].strip().lower()
    cur = at_get(tid, rec).get("fields", {}).get(FIELD, "") or ""
    if addr in cur.lower():
        print(f"  = {rec} {addr} already present")
        done.append({"at_member_id": rec, "email": addr, "source": "name_match_approved"})
        continue
    new = (cur.rstrip() + SEPARATOR + addr) if cur.strip() else addr
    print(f"  {'DRY ' if args.dry_run else ''}{rec} {r['member_name']}")
    print(f"      before: {cur!r}")
    print(f"      after : {new!r}")
    if args.dry_run:
        continue
    at_patch(tid, rec, new)
    time.sleep(0.25)                     # Airtable: 5 req/s per base
    back = at_get(tid, rec).get("fields", {}).get(FIELD, "") or ""
    if addr not in back.lower():
        sys.exit(f"STOP: {rec} did not persist {addr}; field now {back!r}")
    done.append({"at_member_id": rec, "email": addr, "source": "name_match_approved"})

if args.dry_run:
    print("dry run — nothing written")
else:
    supa_insert(done)
    print(f"wrote {len(done)} aliases to Airtable and mirrored them locally")
```

Airtable allows 5 requests per second per base, hence the sleep. `at_table_id()` finds the Members table by looking for the field rather than hardcoding a table id.

- [ ] **Step 3: Dry run**

```bash
python3 scripts/writeback_member_email_aliases.py /Users/Born/Downloads/mds_alias_review.csv --dry-run
```

Expected: one before/after pair per approved row, nothing written.

- [ ] **Step 4: STOP — get Andy's go, then run for real**

```bash
python3 scripts/writeback_member_email_aliases.py /Users/Born/Downloads/mds_alias_review.csv
```

- [ ] **Step 5: Verify both sides agree**

Append to `scripts/verify_member_aliases.py`:

```python
approved = get("member_email_alias?select=at_member_id,email&source=eq.name_match_approved")
mismatch = []
for a in approved:
    prof = get(f"member_profiles?select=at_fields&at_member_id=eq.{a['at_member_id']}")
    blob = ((prof[0].get("at_fields") or {}).get("Associated Emails (Admin)") or "").lower() if prof else ""
    if a["email"].lower() not in blob:
        mismatch.append(a["email"])
check("airtable mirror agrees", not mismatch, f"{len(approved)} approved, {len(mismatch)} missing in AT")
```

Run: `python3 scripts/verify_member_aliases.py`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/writeback_member_email_aliases.py scripts/verify_member_aliases.py
git commit -m "#100: write approved aliases back to Airtable, the system of record"
```

---

### Task 6: Gate, close-out numbers, docs

**Files:**
- Modify: `OLIVIA_SPRINT_4.md` (the #100 close block)
- Modify: `OLIVIA_HANDBOOK.md` §4 (the alias layer, one short subsection)

- [ ] **Step 1: Run the leak gate**

Run: `python3 scripts/olivia_leak_gate.py`
Expected: exit 0. Do not pipe it through `tail` — that discards the exit code.

- [ ] **Step 2: Capture the before/after numbers**

```bash
python3 scripts/verify_member_aliases.py
```

Record: alias rows by source, and how many of the 1,171 video-audience people now resolve (before: 1,034 of 1,171 by email alone).

- [ ] **Step 3: Write the close block on the board**

Under `### #100` add: short results, the AC checklist marked met/not, and the before/after numbers.

- [ ] **Step 4: Document the layer in the handbook**

Add to §4 a short subsection naming `digest.member_email_alias`, the four `source` values, `digest.resolve_member_by_email()` as the single entry point, and the rule that Airtable's `Associated Emails (Admin)` is the system of record.

- [ ] **Step 5: Commit**

```bash
git add OLIVIA_SPRINT_4.md OLIVIA_HANDBOOK.md
git commit -m "#100: close block + handbook entry for the identity alias layer"
```

---

## Out of scope

- Applying `Pending Group Entrance` to `is_active_member_status()`. Approved by Andy 2026-08-20 and shipped as its own one-line change before this plan starts, because it is about *who counts as a member*, not about which addresses belong to one.
- The GroupOS video-access load (`digest.video_access`). That is the next ticket and depends on this one.
- The 57 `member_identity` rows with a NULL `at_member_id`.
- Wiring `resolve_member_by_email()` into existing retrieval functions. This plan creates the resolver and proves it; adopting it call-site by call-site is separate work with its own gate run.
