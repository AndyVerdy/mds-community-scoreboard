# #82 Flagship Event Dossiers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a member asks about the Summit or Inspire, they learn what kind of event it is, what actually happens there, and who is in the room — instead of a name and a date.

**Architecture:** There are two species of event and one dossier builder. A Channel Call genuinely *is* a topic, so the existing lift-over-baseline model is right for it. A flagship (`style = 'Main'`) is a **room**, and asking "what is this about?" returns `{}` because a room that mirrors the community has no topic skew. Three additions, no rewrite: (1) a tiny curated `event_series_profile` table holding what the Summit and Inspire *are* and how they run, written from the public mds.co pages; (2) a flagship branch in `refresh_entity_dossiers` that fills `reception` with the room's real composition (top topics by HEADCOUNT, niches, revenue bands, countries) instead of leaving it empty; (3) `event_lookup_v3` surfaces both so the answering loop can use them. The lift model is untouched for topical events.

**Tech Stack:** Supabase Postgres (migrations via MCP `apply_migration`), Python 3 + `curl` for the seed script (the `sync_chapter_pages.py` pattern), n8n staging `bqHstPDi84uOhTCJ`, `scripts/olivia_selftest.py --staging`, `scripts/olivia_leak_gate.py`.

## Global Constraints

- Prod workflow `12wj6h1TWqb0d4Dq` is NEVER edited directly. Staging + promote only; `python3 scripts/olivia_wf.py lock --reason "#82 flagship dossiers"` first.
- Gate runs `--phone 16196077048` (Ian); the default probe aborts on Andy's empty `channels_present`. Promote inherits it via `OLIVIA_GATE_PHONE=16196077048`.
- **🚨 After any `DROP FUNCTION`, `revoke all ... from public, anon, authenticated` in the SAME migration.** Postgres re-grants EXECUTE to PUBLIC on a fresh CREATE; granting alone leaves it open. This shipped two live leaks on 2026-08-11. Prefer `CREATE OR REPLACE` (no DROP) whenever the signature and return type allow.
- After ANY migration: `python3 scripts/db_export_schema.py` then `--check` (exit 0), commit `db/`.
- NO ASCII apostrophes inside Answer Seed rule strings; `node --check` every edited Code node before PUT.
- Probes fire ONLY at the staging webhook, probe phone `17866578153`, `wamid.SELFTEST*` (silent). `--cleanup` after.
- **Revenue is bands only, never exact figures** — the composition block must never emit a member's revenue, only band counts.
- **Score is never shown** — headcounts and band counts are fine; expertise scores, lift and percentile stay internal.
- Small-cell suppression: any composition bucket with fewer than **3** members is dropped, matching `form_stats`.
- Idempotence markers must be UNIQUE strings — `fit_reason` was a useless marker on 2026-08-11 because four other tool descriptions already contained it.

## The evidence this plan is built on (measured 2026-08-11)

| Fact | Value |
|---|---|
| `MDS Summit Singapore` dossier today | `topic_profile: {}` · `audience: null` · `strength_note: "draws a strong member crowd"` · 116 registrations |
| Why it is empty | topics are kept only at **lift ≥ 1.3** over the community baseline; the Summit's highest is **Sourcing & Suppliers 1.29** |
| What is discarded | International Expansion **55 members**, Amazon FBA 41, Walmart / DTC & Shopify / Hiring & Team / Logistics & 3PL **38 each**, Retail & Wholesale 37, Supplements 36, Sourcing & Suppliers 36, Amazon PPC 35, TikTok Shop 24, Exits & M&A 23 |
| The flagship flag already exists | `events_catalog.style = 'Main'` — **44 events, 8 upcoming**; Summit Singapore is `Main`. Other styles: Ancillary, Channel, Chapter, Mogul, Expert Call, Hot Seat, Mastermind, … |
| Editorial source | `mds.co/mds-summit` (member-only, 4 days, Singapore Aug 23–26 2026; MDS Only Sessions, Meet N' Speed™, Dine-Arounds, Hack Contest) · `mds.co/mds-inspire` (open, 400+ founders, Las Vegas March 2027, 5th annual, 30+ speakers, 27+ workshops) |
| No description field exists | `events_catalog` has no agenda/description column — confirmed against the column list; this is Andy's own standing open question |

---

### Task 1: `event_series_profile` — what the Summit and Inspire ARE

**Files:**
- Create: `scripts/sql/event_series_profile_82.sql` (table DDL, applied as a migration)
- Create: `scripts/seed_event_series.py` (re-runnable upsert of the two rows)
- Modify (regenerated): `db/tables.sql`, `db/grants.sql`, `db/rls.sql`

**Interfaces:**
- Produces: `digest.event_series_profile(series text primary key, match_pattern text, what_it_is text, format_notes text[], audience text, source_url text, refreshed_at timestamptz)`. Task 2 joins it on `events_catalog.name ~* match_pattern`; Task 3 returns `what_it_is` and `format_notes`.

**Why curated, not scraped:** the chapter scraper works because 20 pages share one layout. These are two bespoke marketing pages whose copy changes rarely, and Andy has already ruled (#79) that member-facing copy is curated rather than generated. The row records `source_url` and `refreshed_at` so it can be re-checked against the page.

- [ ] **Step 1: Failing test — nothing describes a flagship today**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/event_series_profile?select=series&limit=1",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}","-H","Accept-Profile: digest"],
 capture_output=True,text=True)
print("status:", r.stdout)
assert r.stdout != "200", "already applied — skip to Step 5"
EOF
```

Expected: `404` (relation does not exist).

- [ ] **Step 2: Write the DDL**

```sql
-- #82 — what a flagship event IS. Two species of event share one dossier builder: a
-- Channel Call is a TOPIC (the lift model describes it well), a Summit is a ROOM (asking
-- "what is this about" returns {} because the room mirrors the community). This table
-- holds the identity and format half, curated from the public mds.co pages.
create table digest.event_series_profile (
  series        text primary key,
  match_pattern text not null,
  what_it_is    text not null,
  format_notes  text[] not null default '{}',
  audience      text,
  source_url    text,
  refreshed_at  timestamptz not null default now()
);
revoke all on digest.event_series_profile from anon, authenticated;
```

Save as `scripts/sql/event_series_profile_82.sql` and apply via `apply_migration` named `event_series_profile_82`.

- [ ] **Step 3: Write the seed script**

```python
#!/usr/bin/env python3
"""#82 — seed what the flagship event SERIES are, from the public mds.co pages.

CURATED, not scraped: two bespoke marketing pages, copy that changes rarely, and Andy's
#79 ruling that member-facing copy is written rather than generated. source_url and
refreshed_at are stored so the text can be re-checked against the page. Re-runnable.
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"

ROWS = [
    {"series": "MDS Summit",
     "match_pattern": "summit",
     "what_it_is": "The biggest gathering of MDS members all year — members only, four days, "
                   "built for peer-to-peer depth rather than panels.",
     "format_notes": [
         "MDS Only Sessions: a real challenge goes on the table and the group works through it together",
         "Meet N Speed networking rotations",
         "Dine-Arounds: curated small-group dinners",
         "Hack Contest: members share the tactical tools and wins that worked",
         "Keynotes, deep dives and breakouts across the four days"],
     "audience": "Vetted MDS members only — every attendee is an experienced operator, which is "
                 "what lets people share openly.",
     "source_url": "https://www.mds.co/mds-summit"},
    {"series": "MDS Inspire",
     "match_pattern": "inspire",
     "what_it_is": "MDS's flagship open conference — 400+ seven-to-nine-figure ecommerce founders "
                   "across Amazon, TikTok Shop and DTC. Fifth annual.",
     "format_notes": [
         "30+ speakers and 27+ workshops",
         "Keynotes on founder strategy, plus breakouts and deep dives",
         "Focus groups for small-group discussion",
         "One-on-one coffee chats with 40+ founders",
         "Speed networking rotations and a peer-driven hack contest"],
     "audience": "Ambitious ecommerce founders, CEOs and brand owners scaling from high six "
                 "figures to $100M+ — open beyond MDS membership.",
     "source_url": "https://www.mds.co/mds-inspire"},
]


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


def main():
    key = env("SUPABASE_SECRET_KEY")
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/event_series_profile?on_conflict=series",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
         "-H", "Prefer: resolution=merge-duplicates,return=representation",
         "--data-binary", json.dumps(ROWS)], capture_output=True, text=True)
    out = json.loads(r.stdout) if r.stdout.strip() else []
    assert len(out) == len(ROWS), f"upsert returned {len(out)} rows: {r.stdout[:300]}"
    for row in out:
        print(f"  {row['series']}: {len(row['format_notes'])} format notes · {row['source_url']}")
    print(f"seeded {len(out)} series")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run it and assert both series land**

```bash
python3 scripts/seed_event_series.py
```

Expected: two lines (`MDS Summit: 5 format notes`, `MDS Inspire: 5 format notes`), then `seeded 2 series`.

- [ ] **Step 5: Assert the patterns match the real catalog rows and nothing else**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/schema_source",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d","{}"],capture_output=True,text=True)
print("(schema_source reachable:", r.returncode==0, ")")
EOF
```

Then run this via Supabase MCP `execute_sql`:

```sql
select s.series, count(*) as main_events_matched,
       string_agg(distinct coalesce(c.app_title, c.name), ' | ' order by coalesce(c.app_title, c.name)) as sample
from digest.event_series_profile s
join digest.events_catalog c
  on c.style = 'Main' and coalesce(c.app_title, c.name) ~* s.match_pattern
group by s.series;
```

Expected: `MDS Summit` matches the Summit rows (Singapore, Milan, Barcelona, Denver, Mexico City…) and `MDS Inspire` matches the Inspire rows. If a pattern catches an unrelated `Main` event, tighten it before continuing — a wrong series description is worse than none.

- [ ] **Step 6: Re-export, drift check, commit**

```bash
python3 scripts/db_export_schema.py && python3 scripts/db_export_schema.py --check
git add db/tables.sql db/grants.sql db/rls.sql scripts/sql/event_series_profile_82.sql scripts/seed_event_series.py
git commit -m "#82 event_series_profile: what the Summit and Inspire actually are"
```

---

### Task 2: `refresh_entity_dossiers` — a flagship carries its room, not a topic vector

**Files:**
- Create: `scripts/sql/gen_refresh_dossiers_82.py` (migration generator over the byte-matched export)
- Modify (via migration): live `digest.refresh_entity_dossiers` (source: `db/functions/refresh_entity_dossiers.sql`)
- Modify (regenerated): `db/functions/refresh_entity_dossiers.sql`

**Interfaces:**
- Consumes: `events_catalog.style`, `event_registrations_live`, `member_expertise`, `member_attributes`, and Task 1's `event_series_profile`.
- Produces: for `style = 'Main'` rows, `entity_dossier.reception` gains `room` — `{"topics": [{"topic": t, "members": n}], "niches": [...], "rev_bands": {...}, "countries": [...]}` — and `audience` is always non-null for a flagship. `topic_profile` stays `{}` for flagships **by design**. Task 3 reads `reception->'room'`.

- [ ] **Step 1: Failing test — the flagship dossier has no room today**

Run via Supabase MCP `execute_sql`:

```sql
select name, topic_profile, reception
from digest.entity_dossier
where kind='event' and entity_id='recrATwhUDA55iQN5';
```

Expected: `topic_profile = {}`, `reception` has `member_registrations` and `audience: null`, and **no `room` key**.

- [ ] **Step 2: Write the migration generator**

```python
#!/usr/bin/env python3
"""#82 — flagship events carry the ROOM, not a topic vector.

The event branch keeps a topic only at lift >= 1.3 over the community baseline. A Summit
draws a representative slice of MDS, so lift is ~1.0 on everything and the profile computes
to {} — the Singapore Summit's best was Sourcing & Suppliers at 1.29. Measured 2026-08-11,
that discards International Expansion (55 members), Amazon FBA (41), Walmart / DTC &
Shopify / Hiring & Team / Logistics & 3PL (38 each), Supplements (36) and more.

Lift is the right question for a Channel Call and the wrong one for a Summit. So: keep lift
untouched, and for style='Main' add a `room` block built from HEADCOUNT — which is what a
member actually wants ("55 people working on international expansion"), and which needs no
score to be spoken out loud. Buckets under 3 members are suppressed, matching form_stats.
"""
SRC = "/Users/Born/Scorecard/db/functions/refresh_entity_dossiers.sql"

body = open(SRC).read().split("\n", 1)[1]

OLD_CTES = """  ), namehits as ("""
NEW_CTES = """  ), flagship as (
    -- style='Main' is the existing flagship flag (44 events, 8 upcoming). A room is
    -- described by who is in it, counted, never scored.
    select r.eid,
           jsonb_build_object(
             'topics', coalesce((
                select jsonb_agg(jsonb_build_object('topic', x.topic, 'members', x.n)
                                 order by x.n desc)
                from (select e.topic, count(distinct r2.mid) n
                        from reg r2 join digest.member_expertise e on e.at_member_id = r2.mid
                       where r2.eid = r.eid and coalesce(e.weakness_score,0) = 0 and e.score > 0
                       group by e.topic having count(distinct r2.mid) >= 3
                       order by count(distinct r2.mid) desc limit 8) x), '[]'::jsonb),
             'niches', coalesce((
                select jsonb_agg(jsonb_build_object('niche', y.niche, 'members', y.n)
                                 order by y.n desc)
                from (select coalesce(ma.main_niche, ma.categories[1]) niche, count(*) n
                        from reg r3 join digest.member_attributes ma on ma.at_member_id = r3.mid
                       where r3.eid = r.eid and coalesce(ma.main_niche, ma.categories[1]) is not null
                       group by 1 having count(*) >= 3
                       order by count(*) desc limit 6) y), '[]'::jsonb),
             'rev_bands', coalesce((
                select jsonb_object_agg(z.band, z.n)
                from (select ma.rev_band band, count(*) n
                        from reg r4 join digest.member_attributes ma on ma.at_member_id = r4.mid
                       where r4.eid = r.eid and ma.rev_band is not null
                       group by 1 having count(*) >= 3) z), '{}'::jsonb),
             'countries', coalesce((
                select jsonb_agg(jsonb_build_object('country', q.country, 'members', q.n)
                                 order by q.n desc)
                from (select ma.country, count(*) n
                        from reg r5 join digest.member_attributes ma on ma.at_member_id = r5.mid
                       where r5.eid = r.eid and ma.country is not null
                       group by 1 having count(*) >= 3
                       order by count(*) desc limit 6) q), '[]'::jsonb)
           ) room
    from (select distinct eid from reg) r
    join digest.events_catalog c2 on c2.at_record_id = r.eid and c2.style = 'Main'
  ), namehits as ("""

OLD_RECEPTION = """         jsonb_build_object('member_registrations', coalesce(d.regs,0),
                            'audience', case when coalesce(d.regs,0) > 150 then 'flagship - draws the whole community, no topic skew'
                                             when ap.tp is not null then 'selective room - topics are lift over the community baseline'
                                             end),"""
NEW_RECEPTION = """         jsonb_build_object('member_registrations', coalesce(d.regs,0),
                            'audience', case when fl.room is not null then 'flagship - a room, not a topic: describe who is in it, never what it is about'
                                             when coalesce(d.regs,0) > 150 then 'flagship - draws the whole community, no topic skew'
                                             when ap.tp is not null then 'selective room - topics are lift over the community baseline'
                                             end)
           || case when fl.room is not null then jsonb_build_object('room', fl.room) else '{}'::jsonb end,"""

OLD_JOIN = """  from ev e3 left join attprof ap on ap.eid = e3.eid"""
NEW_JOIN = """  from ev e3 left join attprof ap on ap.eid = e3.eid
  left join flagship fl on fl.eid = e3.eid"""

for old, new in ((OLD_CTES, NEW_CTES), (OLD_RECEPTION, NEW_RECEPTION), (OLD_JOIN, NEW_JOIN)):
    if new in body:
        continue
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:70]!r}"
    body = body.replace(old, new)

print("CREATE OR REPLACE FUNCTION " + body.split("CREATE OR REPLACE FUNCTION", 1)[1].rstrip() + ";")
print("notify pgrst, 'reload schema';")
```

Save as `scripts/sql/gen_refresh_dossiers_82.py`, run to `/tmp/mig82b.sql`, read it once end to end. `CREATE OR REPLACE` — the signature and return type do not change, so no DROP and no revoke needed.

- [ ] **Step 3: Apply, then rebuild the dossiers**

Apply via `apply_migration` named `refresh_entity_dossiers_flagship_room_82`, then run via `execute_sql`:

```sql
select * from digest.refresh_entity_dossiers();
```

- [ ] **Step 4: Assert the Summit now describes its room**

```sql
select name,
       reception->'audience' as audience,
       reception->'room'->'topics' as topics,
       reception->'room'->'niches' as niches,
       reception->'room'->'rev_bands' as rev_bands,
       reception->'room'->'countries' as countries
from digest.entity_dossier
where kind='event' and entity_id='recrATwhUDA55iQN5';
```

Pass criteria: `topics` leads with `International Expansion` at ~55 members and includes Amazon FBA (~41), Walmart / DTC & Shopify / Hiring & Team / Logistics & 3PL (~38), Supplements (~36); `niches`, `rev_bands` and `countries` are non-empty; `audience` is the flagship string. Every number is a **member count**, never a score.

- [ ] **Step 5: Assert topical events are untouched**

```sql
select name, topic_profile, reception->'audience' as audience, reception ? 'room' as has_room
from digest.entity_dossier
where kind='event' and name in ('MDS Summit Singapore Pre-Event Dinner','MDS TikTok Mastermind Singapore 2026');
```

Expected: both keep their lift-derived `topic_profile` (Pre-Event Dinner: Sourcing & Suppliers ≈0.654, DTC & Shopify ≈0.578, Amazon FBA ≈0.445, Walmart ≈0.442) and `audience = "selective room - topics are lift over the community baseline"`, and `has_room = false` — they are not `style='Main'`. If either lost its topics, STOP: the lift model has been damaged.

- [ ] **Step 6: Re-export, drift check, commit**

```bash
python3 scripts/db_export_schema.py && python3 scripts/db_export_schema.py --check
git add db/functions/refresh_entity_dossiers.sql scripts/sql/gen_refresh_dossiers_82.py
git commit -m "#82 refresh_entity_dossiers: flagships carry the room, topical events keep lift"
```

---

### Task 3: `event_lookup_v3` — surface the identity and the room

**Files:**
- Create: `scripts/sql/gen_event_lookup_v3_82.py`
- Modify (via migration): live `digest.event_lookup_v3` (source: `db/functions/event_lookup_v3.sql`)
- Modify (regenerated): `db/functions/event_lookup_v3.sql`, `db/grants.sql`

**Interfaces:**
- Consumes: Task 1's `event_series_profile`, Task 2's `entity_dossier.reception->'room'`.
- Produces: `event_lookup_v3` returns two more columns, appended LAST — `what_it_is text`, `room jsonb`. Task 4 asserts on them; the Answer Seed schema in Task 4 advertises them.

- [ ] **Step 1: Failing test — the lookup cannot describe the Summit today**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/event_lookup_v3",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_query":"Singapore Summit"})],capture_output=True,text=True)
rows=json.loads(r.stdout)
print("columns:", sorted(rows[0].keys()) if rows else "NO ROWS")
assert rows and "what_it_is" not in rows[0], "already applied — skip to Step 5"
EOF
```

Expected: the existing 18 columns, no `what_it_is`, no `room`.

- [ ] **Step 2: Write the generator**

```python
#!/usr/bin/env python3
"""#82 — event_lookup_v3 returns what a flagship IS and who is in the room.

The dossier now holds both (event_series_profile + entity_dossier.reception->'room'), but
the tool the loop calls to answer "tell me about the Singapore Summit" returned neither, so
the answer stayed a name and a date. Return type changes, so this is a DROP+CREATE — which
means the REVOKE is mandatory (see the leak of 2026-08-11).
"""
SRC = "/Users/Born/Scorecard/db/functions/event_lookup_v3.sql"

body = open(SRC).read().split("\n", 1)[1]

edits = [
    ("event_url text, fit_reason text, strength_note text)",
     "event_url text, fit_reason text, strength_note text, what_it_is text, room jsonb)"),
]
for old, new in edits:
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:70]!r}"
    body = body.replace(old, new)

print("drop function digest.event_lookup_v3(text, text, boolean, integer);")
print(body.rstrip() + ";")
print("""
revoke all on function digest.event_lookup_v3(text, text, boolean, integer) from public;
revoke all on function digest.event_lookup_v3(text, text, boolean, integer) from anon;
revoke all on function digest.event_lookup_v3(text, text, boolean, integer) from authenticated;
grant execute on function digest.event_lookup_v3(text, text, boolean, integer) to postgres;
grant execute on function digest.event_lookup_v3(text, text, boolean, integer) to service_role;
notify pgrst, 'reload schema';""")
```

**Before running this**, read the live signature — the parameter list above must match exactly:

```sql
select pg_get_function_identity_arguments(p.oid)
from pg_proc p join pg_namespace n on n.oid=p.pronamespace
where n.nspname='digest' and p.proname='event_lookup_v3';
```

Correct the four `drop`/`revoke`/`grant` lines to the real argument list before applying. Then add the two SELECT expressions to the function's final select list, immediately after `strength_note`, and the joins they need:

```sql
         sp.what_it_is,
         ed2.reception->'room'
```

joined by:

```sql
  left join digest.event_series_profile sp
    on c.style = 'Main' and coalesce(c.app_title, c.name) ~* sp.match_pattern
  left join digest.entity_dossier ed2
    on ed2.kind = 'event' and ed2.entity_id = c.at_record_id
```

using whatever alias the function already gives `events_catalog` — read the body and match it; do not assume `c`.

- [ ] **Step 3: Apply and hammer the REST path**

Apply via `apply_migration` named `event_lookup_v3_what_it_is_room_82`, then re-run the Step 1 script up to 5 times, 2s apart, until `what_it_is` appears (stale-pool 404s otherwise).

- [ ] **Step 4: Assert anon is still denied — the DROP wiped the ACL**

```bash
python3 - <<'EOF'
import json, re, subprocess
src=open('/Users/Born/Scorecard/scripts/olivia_leak_gate.py').read()
ns={}; exec(re.search(r'ANON_KEY = \((.*?)\)\n', src, re.S).group(0), ns); anon=ns['ANON_KEY']
r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/event_lookup_v3",
 "-H",f"apikey: {anon}","-H",f"Authorization: Bearer {anon}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"16196077048","p_query":"Singapore Summit"})],capture_output=True,text=True)
print("anon:", r.stdout)
assert r.stdout in ("401","403","404"), "LEAK: anon can call event_lookup_v3"
print("OK")
EOF
```

Expected: `401`, then `OK`. **If this fails, stop and fix the revoke before anything else.**

- [ ] **Step 5: Assert the Summit now answers with substance**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/event_lookup_v3",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_query":"Singapore Summit"})],capture_output=True,text=True)
row=[x for x in json.loads(r.stdout) if "Summit Singapore" in (x["event_name"] or "")][0]
print("what_it_is:", (row.get("what_it_is") or "")[:90])
print("room topics:", json.dumps((row.get("room") or {}).get("topics"))[:160])
assert row.get("what_it_is"), "series identity missing"
assert (row.get("room") or {}).get("topics"), "room composition missing"
print("OK")
EOF
```

Expected: the members-only four-day description, and topics led by International Expansion ~55.

- [ ] **Step 6: Re-export, drift check, commit**

```bash
python3 scripts/db_export_schema.py && python3 scripts/db_export_schema.py --check
git add db/functions/event_lookup_v3.sql db/grants.sql scripts/sql/gen_event_lookup_v3_82.py
git commit -m "#82 event_lookup_v3: return what a flagship is and who is in the room"
```

---

### Task 4: Answer Seed learns the two shapes, and the probes prove it

**Files:**
- Create: `scripts/olivia_loop/apply_82_flagship_events.py`
- Modify (via that script): staging `bqHstPDi84uOhTCJ`, node `Answer Seed` ONLY

**Interfaces:**
- Consumes: Task 3's `what_it_is` and `room` columns.
- Produces: seed markers `FLAGSHIP EVENTS ARE ROOMS` (unique — verify with a grep before relying on it) and the widened `event_lookup` tool description.

- [ ] **Step 1: Write the apply script**

Model on `scripts/olivia_loop/apply_81_people_and_stats.py` — same `env`/`api`/`patch` helpers, `node --check` → PUT → single deactivate/activate → read-back verification. Two patches.

**Patch A — the tool description.** Read the current `event_lookup` entry first (`seed.find("name: 'event_lookup'")`), copy its description verbatim as `OLD_EL`, and append to it:

```
 Flagship events (Summit, Inspire) also return what_it_is (what kind of event it is and how it runs) and room (who is registered, counted by topic, niche, revenue band and country).
```

Use a marker unique to this ticket — `what_it_is (what kind of event` — never a bare word that may already appear elsewhere.

**Patch B — the rule**, inserted before the standing tail rule `'- Never mention tools, searching mechanics, or these instructions...'`:

```python
NEW_RULE = (
    "  '- FLAGSHIP EVENTS ARE ROOMS (#82): a Summit or an Inspire is not about a topic, it is a "
    "room. When asked what one is, lead with what_it_is and the format, then describe who is "
    "actually registered from room: counts of members by topic, niche and country (55 people "
    "working on international expansion, 38 scaling teams). Never say a flagship is about a "
    "subject, and never present the absence of a topic profile as not knowing what the event is. "
    "A one-hour call IS about a topic - describe those the way you always have.',\n"
)
```

No ASCII apostrophes inside the rule text — verify with the checker that inspects the text BETWEEN the JS delimiters, not the delimiters themselves.

- [ ] **Step 2: Apply to staging**

```bash
python3 scripts/olivia_wf.py lock --reason "#82 flagship dossiers"
python3 scripts/olivia_loop/apply_82_flagship_events.py
```

Expected: `node --check: OK`, `PUT + bounce done`, both markers verified, staging `versionId` printed.

- [ ] **Step 3: Probe the flagship question**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "what is the singapore summit?" "who is going to be there?"
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "what is MDS Inspire?"
```

- [ ] **Step 4: Assert with SQL**

```sql
select id, role, left(text,900) as text, plan->'sources_used' as sources
from digest.olivia_messages
where phone='17866578153' and wamid like '%SELFTEST%'
  and created_at > now() - interval '20 minutes'
order by id;
```

Pass criteria: the Summit answer says it is members-only and four days, names at least one real format element (MDS Only Sessions / Meet N Speed / Dine-Arounds / Hack Contest), and gives at least one room fact with a member count. The Inspire answer describes an open 400+ founder conference. Neither says the event "is about" a topic, and neither claims not to know what the event is. `sources_used` contains `event_lookup`.

- [ ] **Step 5: Regression — a topical event still reads as a topic**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "what was the last mogul call" "yes"
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "who is the best match to me at the singapore summit?"
```

Expected: the Mogul Call answer is unchanged (#70c/#80 behaviour, date-correct, and "yes" summarises that call); the best-match answer still names people with reasons (#81 intact). Then `python3 scripts/olivia_selftest.py --cleanup`.

- [ ] **Step 6: Commit**

```bash
git add scripts/olivia_loop/apply_82_flagship_events.py
git commit -m "#82 staging: flagship events are rooms, not topics"
```

---

### Task 5: Gate, board, logs — promote stays Andy's

**Files:**
- Modify: `scripts/olivia_leak_gate.py`, `OLIVIA_SPRINT_3.md`, `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md`, `OLIVIA_NEXT_SESSION.md`

- [ ] **Step 1: Add the gate check — the room is counts, never scores**

Beside the existing event checks in `scripts/olivia_leak_gate.py`:

```python
        # #82: a flagship room is described in HEADCOUNTS. An expertise score, lift or
        # percentile in there would put an internal ranking in front of a member.
        st, rows = rpc("event_lookup_v3", {"p_phone": phone, "p_query": "Singapore Summit"}, key)
        rooms = [r.get("room") for r in (rows or []) if isinstance(r, dict) and r.get("room")]
        bad = []
        for rm in rooms:
            for t in (rm.get("topics") or []):
                if set(t.keys()) != {"topic", "members"} or not isinstance(t.get("members"), int):
                    bad.append(t)
        check("event_lookup_v3 room reports member COUNTS only (#82)", not bad,
              f"{len(bad)} malformed of {sum(len(r.get('topics') or []) for r in rooms)}")
```

Run `python3 scripts/olivia_leak_gate.py --phone 16196077048 > /tmp/gate82.log 2>&1; echo "EXIT=$?"`. Expected `EXIT=0` and the count rising 247 → **248**. A `status 0` on any check is the known transient curl failure — re-run once and record both.

- [ ] **Step 2: File #82 on the board with story, ACs and evidence**

Insert under `# 🔴 S1 — NOW`, then move it to CLOSED with an evidence block once probes pass. Story and ACs:

```markdown
### #82 · The biggest events have no dossier — the builder asks "what is this about?" when it should ask "what is this?"
**🔴 S1 · size M — filed 2026-08-12 (Andy: "summit is poor… missing dossier for Summit or Inspire is genuinely bad")**

> **In plain words:** The Summit and Inspire are the two biggest things MDS does, and Olivia
> knows less about them than about a one-hour call.

*As a member, when I ask about the Summit or Inspire I learn what kind of event it is, what
actually happens there, and who is in the room.*

**Measured 2026-08-11:** `MDS Summit Singapore` has `topic_profile {}`, `audience null`, 116
registrations. Topics are kept only at **lift ≥ 1.3** over the community baseline and the
Summit's best is **Sourcing & Suppliers at 1.29** — so it discards International Expansion
(**55 members**), Amazon FBA (41), Walmart · DTC & Shopify · Hiring & Team · Logistics & 3PL
(38 each), Supplements (36). A flagship mirrors the community by definition, so lift can
never fire. `style='Main'` already flags the 44 flagship events.

**Accept when** asking what the Summit is returns members-only + four days + a real format
element + a room fact with a count · the same for Inspire · a one-hour call still reads as a
topic (lift model untouched, verified on the Pre-Event Dinner) · the room reports counts, never
scores · gate GREEN · verified in the prod node.
```

- [ ] **Step 3: Logs, handoff, commit, unlock**

Prepend the dated entry to `SESSION_LOG_OLIVIA.md` (migrations by name, staging versionId, probe ids, gate count, what is open), one line to `SESSION_LOG.md`, update the `OLIVIA_NEXT_SESSION.md` state block with the promote command, then:

```bash
git add OLIVIA_SPRINT_3.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md scripts/olivia_leak_gate.py
git commit -m "#82 board + gate check + session logs (staged, awaiting promote)"
python3 scripts/olivia_wf.py unlock
```

---

## Self-review notes

- **Spec coverage.** "What kind of event it is" → Task 1 (`what_it_is`, `audience`). "What happens there" → Task 1 (`format_notes`). "Who is in the room" → Task 2 (`reception->'room'`). Reaching the member → Tasks 3 and 4. Andy's point that Summit and Inspire are *not topic-specific* is honoured by leaving `topic_profile = {}` for flagships deliberately rather than forcing a number into it.
- **Deliberately NOT done:** lowering the 1.3 lift threshold. That would put near-baseline noise into every topical event's profile to fix a problem that is not about the threshold.
- **Curated vs scraped** is a real trade-off, stated in Task 1: two bespoke pages, rarely-changing copy, and a #79 precedent for curated member-facing text. `source_url` + `refreshed_at` make a re-check cheap. If the pages are restructured the text goes stale silently — accepted, and worth a calendar reminder at sprint close rather than a scraper.
- **Type consistency:** `event_series_profile.what_it_is` / `format_notes` / `match_pattern`, `reception->'room'->'topics'[].members`, and `event_lookup_v3.what_it_is` / `room` are named identically in every task, the gate check and the probes.
- **Leak discipline:** Task 2 uses `CREATE OR REPLACE` (no DROP, no revoke needed); Task 3 changes the return type so it must DROP, and its Step 4 is a dedicated anon check that blocks the task if the revoke was missed. This is the failure that shipped twice on 2026-08-11.
- **Unknown that must be read, not assumed:** `event_lookup_v3`'s exact argument list and its `events_catalog` alias — Task 3 Step 2 says to read both from the live definition before applying, rather than guessing them here.
