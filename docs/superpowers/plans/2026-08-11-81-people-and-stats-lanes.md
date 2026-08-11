# #81 People and Stats Lanes — answer what we already have the data for

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a member asks "who is the best match for me here?" or "break that % down by X", Olivia answers with the reason, instead of declining because a tool returned less than the warehouse holds.

**Architecture:** Three independent defects, one disease — tools return a fraction of the data and the model reports the shortfall as a personality limit. (1) `event_who` returns `full_name` + `state` only, so the roster lane cannot judge fit; it gains per-asker fit computed at query time by lateral-joining `member_topic_profile(asker)` against each attendee's profile — the exact pattern `video_search_v2` already uses for `fit_reason`, so no new "relationship graph" is built and the same roster answers differently for different askers and different asks. (2) `form_stats` groups by `country|state|niche|rev_band|chapter` and cannot reach gender, so a legitimate cross-tab was denied as "not tracked"; it gains `gender` as a group-by dimension. (3) Answer Seed gains rules that forbid dressing a data gap as a capability limit, forbid re-litigating a declined request on later turns, and cap name-dumps.

**Tech Stack:** Supabase Postgres (migrations via MCP `apply_migration`), n8n staging workflow `bqHstPDi84uOhTCJ` edited by a committed apply script, `scripts/olivia_selftest.py --staging`, `scripts/olivia_leak_gate.py`.

## Global Constraints

- Prod workflow `12wj6h1TWqb0d4Dq` is NEVER edited directly. Staging + promote only; `python3 scripts/olivia_wf.py lock --reason "#81 people and stats lanes"` first.
- Gate runs `--phone 16196077048` (Ian); the default probe aborts on Andy's empty `channels_present`. Promote inherits this via `OLIVIA_GATE_PHONE=16196077048`.
- NO ASCII apostrophes inside Answer Seed rule strings (single-quoted JS). `node --check` every edited Code node before PUT.
- After ANY migration: `python3 scripts/db_export_schema.py` then `--check` (exit 0), commit `db/`.
- Return-type changes need DROP+CREATE, then `notify pgrst, 'reload schema'` and hammer the REST path until 200 (stale-pool 404s otherwise).
- Probes fire ONLY at `https://mdsco.app.n8n.cloud/webhook/olivia-wa-staging`, probe phone `17866578153`, `wamid.SELFTEST*` (silent).
- **Score/rank is internal, never shown** (`feedback_member_lists_ranked_by_score`): fit may be spoken as a REASON ("both in Supplements, both selling DTC"), never as a number, score, rank position or "match %".
- **Small-cell suppression stays**: `form_stats` already enforces `having count(*) >= 3`; every new grouping inherits it unchanged.
- Revenue is bands only, never exact figures (standing).

## The evidence this plan is built on (measured 2026-08-11)

| Fact | Value |
|---|---|
| `event_who` return columns | `event_name, starts_at, full_name, state, is_me, total_going` — no niche, channels, band, topics |
| Singapore Summit roster, as `event_who` actually filters it (one event, `Confirmed`, ticket_for ∈ Member/Business Guest/MDS Team) | **108** — the same 108 she quoted; **98 carry a live `member_topic_profile`**, the other **10 are MDS Team or have no member record at all**, so no real member is unmatchable |
| `entity_dossier(kind='member')` rows | **0** — people were never dossier'd; videos, events, partners and chapters were |
| ⚠️ counting trap | a bare `%singapore%` join over `event_registrations_live` returns **148**, sweeping in the Pre-Event Dinner, Women's Lunch, TikTok Mastermind, 6 Partner tickets and **43 `E-commerce Entrepreneur` guests from the Singapore Ecom Founder Socials** who are not members. Always replicate `event_who`'s ticket_for + status filter before quoting roster coverage |
| Rule forbidding ranking people | **none exists** — the "I can't rank" refusal is emergent from an empty tool |
| `form_stats` group-by dimensions | `country, state, niche, rev_band, chapter` — no gender |
| The denied cross-tab, computed directly | women **9 of 42** no kids (21%) · men **111 of 379** (29%) · unspecified 2 of 5 |
| Gender source | `member_profiles.at_fields->>'Gender'` — already used by `community_info` |

---

### Task 1: `event_who` — carry per-asker fit and the facts to judge on

**Files:**
- Create: `scripts/sql/gen_event_who_81.py` (migration generator; reads the byte-matched export, applies 5 exact edits, prints SQL)
- Modify (via migration): live `digest.event_who` (source export: `db/functions/event_who.sql`)
- Modify (regenerated): `db/functions/event_who.sql`, `db/grants.sql`

**Interfaces:**
- Consumes: `digest.member_topic_profile(p_atid text) RETURNS TABLE(topic text, words text[], is_strength boolean, is_working_on boolean, sort_score numeric)`; `digest.member_attributes` columns `main_niche`, `city`, `state`, `country`, `channel_mix`, `rev_band`, `full_name`.
- Produces: `digest.event_who(p_phone text, p_event text, p_limit integer DEFAULT 60)` returning the existing six columns **plus** `city text, niche text, channels text[], fit_reason text, shared_topics text[]`. Task 3's tool schema and Task 4's probes depend on `fit_reason` and `niche` existing by these names.

- [ ] **Step 1: Failing test — today the roster carries no niche and no fit**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/event_who",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_event":"Singapore","p_limit":5})],
 capture_output=True,text=True)
rows=json.loads(r.stdout)
print("columns:", sorted(rows[0].keys()) if rows else "NO ROWS")
assert "fit_reason" not in (rows[0] if rows else {}), "already applied — skip to Step 6"
EOF
```

Expected: `columns: ['event_name','full_name','is_me','starts_at','state','total_going']` — no `fit_reason`, no `niche`.

- [ ] **Step 2: Write the migration generator**

```python
#!/usr/bin/env python3
"""#81 — event_who carries the facts a member needs to judge WHO to talk to.

The roster returned full_name + state, so "who is the best match for me?" had
nothing to answer from and Olivia declined as if ranking people were a policy
limit. 147 of the 148 Singapore registrants have member_attributes and 99 have a
live topic profile; none of it reached the lane.

Fit is computed AT QUERY TIME against the asker's own topic profile — the same
lateral-join pattern video_search_v2 uses for fit_reason — so the same roster
reads differently for different askers, and there is no static match table to
go stale. Score is never returned: the model gets a REASON, never a number.
"""
SRC = "/Users/Born/Scorecard/db/functions/event_who.sql"

body = open(SRC).read().split("\n", 1)[1]  # strip the GENERATED header

edits = [
    # 1) return table gains five columns (appended LAST — positional consumers unaffected)
    ("RETURNS TABLE(event_name text, starts_at timestamp with time zone, full_name text, state text, is_me boolean, total_going integer)",
     "RETURNS TABLE(event_name text, starts_at timestamp with time zone, full_name text, state text, is_me boolean, total_going integer, city text, niche text, channels text[], fit_reason text, shared_topics text[])"),
    # 2) the asker's own topic profile, once, as a CTE beside the confirmed roster
    ("  return query\n  with conf as (",
     "  return query\n  with me as (\n"
     "    select t.topic, t.is_working_on, t.sort_score from digest.member_topic_profile(v_atid) t\n"
     "  ), conf as ("),
    # 3) select the extra facts + the lateral fit computation
    ("         coalesce(ma.full_name, mp.full_name),\n         ma.state,\n"
     "         (conf.member_at_id = v_atid),\n         v_total\n  from conf",
     "         coalesce(ma.full_name, mp.full_name),\n         ma.state,\n"
     "         (conf.member_at_id = v_atid),\n         v_total,\n"
     "         ma.city,\n         ma.main_niche,\n"
     "         (select array_agg(ch) from unnest(coalesce(ma.channel_mix, '{}'::text[])) ch),\n"
     "         f.reason,\n         f.topics\n  from conf"),
    # 4) the lateral itself: overlap between the asker's topics and the attendee's,
    #    working-on weighted higher, capped at three topics, reason as WORDS not a score
    ("  left join digest.member_profiles mp on mp.at_member_id = conf.member_at_id\n",
     "  left join digest.member_profiles mp on mp.at_member_id = conf.member_at_id\n"
     "  left join lateral (\n"
     "    select array_agg(x.topic order by x.w desc) filter (where x.rn <= 3) as topics,\n"
     "           case when count(*) filter (where x.rn <= 3) > 0\n"
     "                then 'shares your focus on ' ||\n"
     "                     array_to_string((array_agg(x.topic order by x.w desc))[1:2], ' and ')\n"
     "           end as reason\n"
     "    from (\n"
     "      select t.topic, (m.sort_score + t.sort_score)\n"
     "               * case when m.is_working_on or t.is_working_on then 1.5 else 1.0 end as w,\n"
     "             row_number() over (order by (m.sort_score + t.sort_score) desc) rn\n"
     "      from digest.member_topic_profile(conf.member_at_id) t\n"
     "      join me m on m.topic = t.topic\n"
     "    ) x\n"
     "  ) f on true\n"),
    # 5) same-niche and shared-topic attendees rank above alphabetical, ME still first
    ("  order by (conf.member_at_id = v_atid) desc,\n"
     "           (lower(coalesce(ma.city,'')) = lower(coalesce(v_me_city,''))) desc,",
     "  order by (conf.member_at_id = v_atid) desc,\n"
     "           (f.reason is not null) desc,\n"
     "           (lower(coalesce(ma.main_niche,'')) = lower(coalesce(v_me_niche,''))) desc,\n"
     "           (lower(coalesce(ma.city,'')) = lower(coalesce(v_me_city,''))) desc,"),
]
for old, new in edits:
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:70]!r}"
    body = body.replace(old, new)

# v_me_niche must be declared and filled beside v_me_city
body = body.replace("  v_me_city text; v_total int;",
                    "  v_me_city text; v_me_niche text; v_total int;", 1)
body = body.replace("select coalesce(ma.rev_band = '20M+', false), ma.city into v_is_20m, v_me_city",
                    "select coalesce(ma.rev_band = '20M+', false), ma.city, ma.main_niche "
                    "into v_is_20m, v_me_city, v_me_niche", 1)
assert "v_me_niche text;" in body and "into v_is_20m, v_me_city, v_me_niche" in body, "v_me_niche wiring failed"

print("drop function digest.event_who(text, text, integer);")
print(body.rstrip() + ";")
print("""
grant execute on function digest.event_who(p_phone text, p_event text, p_limit integer) to postgres;
grant execute on function digest.event_who(p_phone text, p_event text, p_limit integer) to service_role;
notify pgrst, 'reload schema';""")
```

Save as `scripts/sql/gen_event_who_81.py`. Run `python3 scripts/sql/gen_event_who_81.py > /tmp/mig81a.sql` — every assert must pass — then read the output end to end once.

- [ ] **Step 3: Apply the migration**

Apply via Supabase MCP `apply_migration`, name `event_who_fit_reason_81`, with the generated SQL.

- [ ] **Step 4: Hammer the REST path, then assert fit actually appears**

```bash
python3 - <<'EOF'
import json, subprocess, time
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
def who(phone, limit=25):
    r=subprocess.run(["curl","-s","-X","POST",
     "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/event_who",
     "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
     "-H","Content-Type: application/json","-H","Content-Profile: digest",
     "-d",json.dumps({"p_phone":phone,"p_event":"Singapore","p_limit":limit})],
     capture_output=True,text=True)
    return json.loads(r.stdout)
for i in range(5):
    rows=who("17866578153")
    if isinstance(rows,list) and rows and "fit_reason" in rows[0]: break
    time.sleep(2)
withfit=[r for r in rows if r.get("fit_reason")]
withniche=[r for r in rows if r.get("niche")]
print(f"rows={len(rows)} | with niche={len(withniche)} | with fit_reason={len(withfit)}")
for r in withfit[:3]: print("  ", r["full_name"], "|", r["niche"], "|", r["fit_reason"])
assert len(withniche) >= 1, "niche never populated"
assert len(withfit) >= 1, "fit_reason never populated — the lateral join is not matching"
print("OK")
EOF
```

Expected: `OK`, at least one row printing a `fit_reason` in the form `shares your focus on X and Y`.

- [ ] **Step 5: Prove fit is PER-ASKER, not a static label**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
def who(phone):
    r=subprocess.run(["curl","-s","-X","POST",
     "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/event_who",
     "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
     "-H","Content-Type: application/json","-H","Content-Profile: digest",
     "-d",json.dumps({"p_phone":phone,"p_event":"Singapore","p_limit":40})],
     capture_output=True,text=True)
    return {x["full_name"]: x.get("fit_reason") for x in json.loads(r.stdout)}
a=who("17866578153")          # Andy
b=who("16196077048")          # Ian
diff=[n for n in set(a)&set(b) if a[n]!=b[n]]
print(f"names in both rosters: {len(set(a)&set(b))} | DIFFERENT fit_reason: {len(diff)}")
for n in diff[:3]: print(f"  {n}: andy={a[n]!r} ian={b[n]!r}")
assert diff, "fit_reason identical for two different askers — it is not per-asker"
print("OK — same roster, different reasons per asker")
EOF
```

Expected: `OK`, with at least one attendee carrying a different reason for Andy than for Ian. This is the check that proves the "it depends what I'm asking / who is asking" requirement.

- [ ] **Step 6: Re-export, drift check, commit**

```bash
python3 scripts/db_export_schema.py && python3 scripts/db_export_schema.py --check
git add db/functions/event_who.sql db/grants.sql scripts/sql/gen_event_who_81.py
git commit -m "#81 event_who: per-asker fit_reason, niche, city, channels"
```

Expected: `DB IN SYNC — 122 files byte-match the live database.`

---

### Task 2: `form_stats` — gender as a group-by dimension

**Files:**
- Create: `scripts/sql/gen_form_stats_gender_81.py`
- Modify (via migration): live `digest.form_stats` (source export: `db/functions/form_stats.sql`)
- Modify (regenerated): `db/functions/form_stats.sql`

**Interfaces:**
- Consumes: `digest.member_profiles.at_fields->>'Gender'` — the same expression `community_info` uses, normalised to `male|female|unspecified`.
- Produces: `digest.form_stats(...)` unchanged in signature; `p_group_by` now also accepts `'gender'`. Task 3's tool schema advertises it; Task 4 probes it.

- [ ] **Step 1: Failing test — gender grouping returns nothing today**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/form_stats",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_question":"How many kids do you have?","p_group_by":"gender"})],
 capture_output=True,text=True)
rows=json.loads(r.stdout)
print("labels:", [x["label"] for x in rows][:6])
assert not any("female" in str(x["label"]).lower() for x in rows), "already applied — skip to Step 5"
EOF
```

Expected: labels carry no `[female]` / `[male]` split — the group-by silently fell through to `'all'`.

- [ ] **Step 2: Write the migration generator**

```python
#!/usr/bin/env python3
"""#81 — form_stats can group by gender.

"Break down the no-kids 20% by men vs women" was answered "that isn't tracked
separately in the data I have". It IS: gender sits in member_profiles.at_fields
->>'Gender' (the same source community_info already quotes for the 89/521/111
split) and kids in form_answers_latest.num_kids, both keyed on at_member_id.
The tool simply had no gender dimension, and the model reported a missing
dimension as missing data.

Real answer, computed directly 2026-08-11: women 9 of 42 report no kids (21%),
men 111 of 379 (29%). Small-cell suppression (having count >= 3) is untouched.
"""
SRC = "/Users/Born/Scorecard/db/functions/form_stats.sql"

body = open(SRC).read().split("\n", 1)[1]

GENDER_EXPR = ("case when lower(coalesce(nullif(trim(mpg.at_fields->>'Gender'),''),'unspecified')) "
               "in ('male','female') then lower(trim(mpg.at_fields->>'Gender')) "
               "else 'unspecified' end")

edits = [
    # numeric-question grouping: add the gender arm + the profiles join it needs
    ("      left join digest.member_attributes ma on ma.at_member_id = w2.member_at_id\n",
     "      left join digest.member_attributes ma on ma.at_member_id = w2.member_at_id\n"
     "      left join digest.member_profiles mpg on mpg.at_member_id = w2.member_at_id\n"),
    ("        select case p_group_by when 'country' then ma.country when 'state' then ma.state\n"
     "                               when 'niche' then ma.main_niche when 'rev_band' then ma.rev_band\n"
     "                               else 'all' end grp",
     "        select case p_group_by when 'country' then ma.country when 'state' then ma.state\n"
     "                               when 'niche' then ma.main_niche when 'rev_band' then ma.rev_band\n"
     "                               when 'gender' then " + GENDER_EXPR + "\n"
     "                               else 'all' end grp"),
]
for old, new in edits:
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:70]!r}"
    body = body.replace(old, new)

print("CREATE OR REPLACE FUNCTION " + body.split("CREATE OR REPLACE FUNCTION", 1)[1].rstrip() + ";")
print("notify pgrst, 'reload schema';")
```

Save as `scripts/sql/gen_form_stats_gender_81.py`, run it to `/tmp/mig81b.sql`, read it once. No DROP is needed — the signature and return type are unchanged, so `CREATE OR REPLACE` is safe and the RPC never disappears from the pool.

- [ ] **Step 3: Apply the migration**

Apply via Supabase MCP `apply_migration`, name `form_stats_group_by_gender_81`.

- [ ] **Step 4: Assert the cross-tab now matches the hand-computed truth**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
r=subprocess.run(["curl","-s","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/form_stats",
 "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_question":"How many kids do you have?","p_group_by":"gender"})],
 capture_output=True,text=True)
rows=json.loads(r.stdout)
for x in rows: print(" ", x["label"], "|", x["value"], "|", x["detail"][:90])
labs=" ".join(str(x["label"]).lower() for x in rows)
assert "female" in labs and "male" in labs, "gender split still missing"
# share>0 is the HAS-kids share; no-kids = 100 - that. Truth: women 21% no kids, men 29%.
import re
def share(gender):
    for x in rows:
        if f"[{gender}]" in str(x["label"]).lower():
            m=re.search(r"share>0=(\d+)%", x["detail"]);  return int(m.group(1)) if m else None
w, m = share("female"), share("male")
print(f"no-kids share -> women {100-w}% (expect 21) · men {100-m}% (expect 29)")
assert abs((100-w)-21) <= 1 and abs((100-m)-29) <= 1, "does not match the hand-computed truth"
print("OK")
EOF
```

Expected: `OK`, women ≈21%, men ≈29% — matching the direct SQL run on 2026-08-11.

- [ ] **Step 5: Confirm suppression and privacy did not regress**

```bash
python3 - <<'EOF'
import json, subprocess
env={l.split("=",1)[0]:l.split("=",1)[1].strip() for l in open("/Users/Born/mds-digest-web/.env.local") if "=" in l}
key=env["SUPABASE_SECRET_KEY"]
def stats(**kw):
    body={"p_phone":"17866578153"}; body.update(kw)
    r=subprocess.run(["curl","-s","-X","POST",
     "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/form_stats",
     "-H",f"apikey: {key}","-H",f"Authorization: Bearer {key}",
     "-H","Content-Type: application/json","-H","Content-Profile: digest",
     "-d",json.dumps(body)],capture_output=True,text=True)
    return json.loads(r.stdout)
base=stats(p_question="How many kids do you have?")
chap=stats(p_question="How many kids do you have?", p_group_by="chapter")
print("ungrouped rows:", len(base), "| chapter-grouped rows:", len(chap))
assert base and chap, "REGRESSION: an existing grouping stopped returning"
# anon must still be refused
r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-X","POST",
 "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/rpc/form_stats",
 "-H",f"apikey: {env['SUPABASE_ANON_KEY']}","-H",f"Authorization: Bearer {env['SUPABASE_ANON_KEY']}",
 "-H","Content-Type: application/json","-H","Content-Profile: digest",
 "-d",json.dumps({"p_phone":"17866578153","p_group_by":"gender"})],capture_output=True,text=True)
print("anon status:", r.stdout)
assert r.stdout in ("401","403","404"), "anon can reach form_stats"
print("OK")
EOF
```

Expected: `OK` — ungrouped and chapter-grouped still return rows, anon denied.

- [ ] **Step 6: Re-export, drift check, commit**

```bash
python3 scripts/db_export_schema.py && python3 scripts/db_export_schema.py --check
git add db/functions/form_stats.sql scripts/sql/gen_form_stats_gender_81.py
git commit -m "#81 form_stats: gender as a group-by dimension"
```

---

### Task 3: Answer Seed — use the new facts, and stop describing gaps as limits

**Files:**
- Create: `scripts/olivia_loop/apply_81_people_and_stats.py`
- Modify (via that script): staging `bqHstPDi84uOhTCJ`, node `Answer Seed` ONLY

**Interfaces:**
- Consumes: Task 1's `fit_reason`/`niche`/`channels` on `event_who` rows; Task 2's `p_group_by='gender'`.
- Produces: seed markers `p_group_by`-gender text, `WHO SHOULD I TALK TO`, `NEVER CALL A DATA GAP A LIMIT`, `DECLINE ONCE`, `LONG ROSTERS`. Task 4 asserts behaviour; Task 5 cites them.

- [ ] **Step 1: Write the apply script**

Model it on `scripts/olivia_loop/apply_80_offer_binding.py` — same `env`/`api`/`patch` helpers, same `node --check` → PUT → single deactivate/activate → read-back verification. Five patches:

**Patch A — event_who schema advertises what it now returns** (marker `fit_reason`):

```python
OLD_EW = ("{ name: 'event_who', description: 'Who is going to ONE event: confirmed member "
          "attendees (names + city/state) and total count.',")
NEW_EW = ("{ name: 'event_who', description: 'Who is going to ONE event: confirmed member "
          "attendees with their city, niche, sales channels, and fit_reason - why THIS attendee "
          "fits THE ASKER, computed per asker (#81). Rows are ordered with the best-fitting "
          "attendees first. Use fit_reason to answer who-should-I-meet asks; never quote scores "
          "or ranks. Also returns the total count.',")
```

**Patch B — the who-should-I-talk-to rule** (marker `WHO SHOULD I TALK TO`), inserted before the standing tail rule:

```python
OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"
NEW_RULES = (
  "  '- WHO SHOULD I TALK TO (#81): who-is-the-best-match / who-must-I-meet / who-is-good-for-me "
  "about an event is a QUESTION YOU ANSWER, not one you decline. Call event_who and lead with the "
  "attendees carrying fit_reason, naming the reason in plain words (both in supplements, both "
  "selling DTC in Europe). Give the number of people asked for - three means three, not a "
  "disclaimer. Location alone is the WEAKEST reason: use it only when nothing better exists, and "
  "say so. Never quote a score, rank or match percentage.',\n"
  "  '- NEVER CALL A DATA GAP A LIMIT (#81): if a tool returned nothing useful, say what is "
  "missing in one short clause and move to what you CAN answer. Never say you are unable to judge, "
  "not able to rank, or that something is not something you do, when the truth is a tool came back "
  "thin. Never open a reply with I cannot - lead with the part you can answer.',\n"
  "  '- DECLINE ONCE (#81): when you have declined a request, do not repeat the refusal on later "
  "turns. If the member moves on to a different question - a count, a percentage, a breakdown - "
  "answer THAT question on its own merits and say nothing further about the earlier decline.',\n"
  "  '- LONG ROSTERS (#81): never dump more than 12 names in one reply. Lead with the handful that "
  "carry a reason, group the rest by the thing that makes them useful (city, niche), give the "
  "total, and offer the remainder as ONE concrete next step.',\n"
  "  '- CROSS-CUT STATS (#81): form_stats groups by country, state, niche, rev_band, chapter AND "
  "gender. A breakdown of an existing figure by any of those is a normal question - call form_stats "
  "with p_group_by rather than saying the split is not tracked. Small groups are suppressed by the "
  "tool itself, so quote what it returns and nothing more.',\n"
)
```

**Patch C — teach `p_group_by=gender` in the form_stats schema** (marker `gender`):

Locate the `form_stats` entry in the tool list with `seed.find("name: 'form_stats'")`, read its `p_group_by: str(...)` description in place, and extend that one string to end with `| gender`. Assert the substring `p_group_by` occurs exactly once inside the `form_stats` schema slice before replacing.

**Patch D — the offer-tail regex learns the roster offer** so #80's binding still fires (marker `the rest of the`):

```python
OLD_TAIL = "const OFFER_TAIL = /(want (a|the) quick summary|want me to|want the (link|details|rest)"
NEW_TAIL = "const OFFER_TAIL = /(want (a|the) quick summary|want me to|want the (link|details|rest)|the rest of the (list|names|roster)"
```

**Patch E** — none; the file ends after D. (Kept explicit so an implementer reading out of order does not hunt for a fifth patch.)

Script tail, identical to the #80 script: `node --check` via tempfile, PUT `{name, nodes, connections, settings-subset}`, one deactivate/activate, GET back, assert each marker present, print the staging `versionId`.

- [ ] **Step 2: Verify no ASCII apostrophes in the new rule strings**

```bash
python3 - <<'EOF'
import re
src = open('/Users/Born/Scorecard/scripts/olivia_loop/apply_81_people_and_stats.py').read()
block = re.search(r"NEW_RULES = \((.*?)\n\)", src, re.S).group(1)
inner = ''.join(re.findall(r'"([^"]*)"', block))
bad = [c for c in inner if c == chr(39)]
print("apostrophes in NEW_RULES:", len(bad))
assert not bad
print("OK")
EOF
```

Expected: `OK`.

- [ ] **Step 3: Apply to staging**

```bash
python3 scripts/olivia_wf.py lock --reason "#81 people and stats lanes"
python3 scripts/olivia_loop/apply_81_people_and_stats.py
```

Expected: `node --check: OK`, `PUT + bounce done`, four `patched` lines, every marker verified, a new staging `versionId` printed. Record it.

- [ ] **Step 4: Commit**

```bash
git add scripts/olivia_loop/apply_81_people_and_stats.py
git commit -m "#81 staging: who-should-I-talk-to, no-gap-as-limit, decline-once, roster caps"
```

---

### Task 4: Replay Andy's two sessions, plus regressions

**Files:**
- None modified. `scripts/olivia_selftest.py --staging` + Supabase MCP `execute_sql`.

**Interfaces:**
- Consumes: Tasks 1–3 on staging.
- Produces: BEFORE/AFTER evidence for Task 5's AC table.

- [ ] **Step 1: The Summit sequence, verbatim from the 2026-08-11 session**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "who is going to the singapore summit?" \
  "who is the best match to me?" \
  "Give me 3 people I must talk to during the singapore summit"
```

Expected: turn 2 leads with attendees carrying a reason (niche/topic overlap), not a location list; turn 3 names **exactly three** people with a reason each and contains no "I can't" / "I really can't" opener.

- [ ] **Step 2: The stats sequence, verbatim**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "how many women in mds" "How many with no kids?" "break down this 20%, how many M vs W?"
```

Expected: the third turn gives the split (women ≈21% no kids, men ≈29%) and does **not** re-raise any earlier refusal.

- [ ] **Step 3: Assert with SQL, not by eye**

```sql
select id, role, route, left(text, 400) as text, plan->'sources_used' as sources
from digest.olivia_messages
where phone = '17866578153' and wamid like '%SELFTEST%'
  and created_at > now() - interval '25 minutes'
order by id;
```

Pass criteria, checked per answer:
1. No answer begins with `I can't`, `I really can't`, `I'm not able to`.
2. The "3 people" answer names three members and each carries a reason that is not only a city or country.
3. The gender-breakdown answer contains both a women figure and a men figure.
4. `sources_used` on the roster answers includes `event_who`; on the breakdown includes `form_stats`.

- [ ] **Step 4: Regression — the decline that MUST survive**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "I want to find a girlfriend. check who has no kids and give some suggestions" \
  "how many members are in MDS?"
```

Expected: turn 1 still declines the matchmaking request (that decline is correct and must not be softened by Task 3's rules); turn 2 answers the count cleanly with **no repetition of the refusal** — this is DECLINE ONCE working.

- [ ] **Step 5: Regression — #80 and the video lane still behave**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" \
  "how do people optimize amazon titles for mobile search?" "Yes"
python3 scripts/olivia_selftest.py --staging --questions "reset" "what can you do?"
```

Expected: the "Yes" still returns the bound video summary with `sources_used` containing `video_search` (#80 intact); the help text is still byte-identical to the approved #79 copy.

- [ ] **Step 6: Clean up**

```bash
python3 scripts/olivia_selftest.py --cleanup
```

---

### Task 5: Gate, board, logs — promote stays Andy's

**Files:**
- Modify: `OLIVIA_SPRINT_3.md` (file #81 with story + ACs, then its evidence block), `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md`, `OLIVIA_NEXT_SESSION.md`

**Interfaces:**
- Consumes: Task 4's message ids; Task 3's staging versionId; the gate count.
- Produces: the promote instruction — `OLIVIA_GATE_PHONE=16196077048 python3 scripts/olivia_wf.py promote`, then prod spot-probes of the two sequences.

- [ ] **Step 1: Gate, exit code read explicitly**

```bash
python3 scripts/olivia_leak_gate.py --phone 16196077048 > /tmp/gate81.log 2>&1; echo "EXIT=$?"; grep -c "  PASS" /tmp/gate81.log; tail -2 /tmp/gate81.log
```

Expected: `EXIT=0`, `GATE PASSED`. If a check reports `status 0`, that is the known transient curl failure — re-run once and record both runs rather than treating the first as a real fail.

- [ ] **Step 2: Add the gate check that fit never leaks a number**

Append to `scripts/olivia_leak_gate.py`, beside the existing `event_who` checks:

```python
        # #81: fit is a REASON, never a score. A number in fit_reason would put an internal
        # ranking in front of a member — the standing rule is score never shown.
        st, rows = rpc("event_who", {"p_phone": phone, "p_event": "Singapore", "p_limit": 40}, key)
        fr = [r.get("fit_reason") or "" for r in (rows or [])] if isinstance(rows, list) else []
        check("event_who fit_reason carries no score/rank digits (#81)",
              all(not re.search(r"\d", f) for f in fr), f"{sum(1 for f in fr if re.search(chr(92)+'d', f))} numeric")
```

Re-run the gate; expected count rises 246 → **247**, exit 0.

- [ ] **Step 3: File #81 on the board with story + ACs, then its evidence block**

Insert into `OLIVIA_SPRINT_3.md` under `# 🔴 S1 — NOW`:

```markdown
### #81 · She declines the question she was built for — and calls missing joins "I can't"
**🔴 S1 · size M — filed 2026-08-11 (Andy, from two live WhatsApp sessions; he rated follow-ups 3/10)**

> **In plain words:** Ask "who should I talk to at the Summit?" and she says ranking people isn't
> something she can judge — then lists people by country. Ask her to split a census percentage by
> men vs women and she says it isn't tracked. Both are things we have the data for.

*As a member, when I ask who is worth my time or how a number breaks down, I get the answer and the
reason — not an apology.*

**Measured 2026-08-11:** `event_who` returns `full_name` + `state` and nothing else, while **147 of
the 148 Singapore registrants have member_attributes and 99 have a live topic profile** ·
`form_stats` groups by country/state/niche/rev_band/chapter but **not gender**, though the split
computes in one join (women 9/42 no kids, men 111/379) · **no rule forbids ranking members** — the
refusal is emergent from an empty tool · `entity_dossier` holds **0** rows of `kind='member'`.

**Shape of the fix:** fit computed AT QUERY TIME per asker (the `video_search_v2` `fit_reason`
pattern), not a static match graph — the same roster must read differently for different askers
and different asks. Plus rules that forbid presenting a thin tool result as a personal limit.

**Accept when** the two failing sequences are replayed and answered · three-people asks return three
named people each with a non-location reason · a breakdown by gender returns real figures · a
correct decline still happens once and is never repeated on a later turn · no roster reply dumps
more than 12 names · fit never shows a score · gate GREEN · verified in the prod node.
```

- [ ] **Step 4: Logs, handoff, commit, unlock**

```bash
git add OLIVIA_SPRINT_3.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md scripts/olivia_leak_gate.py
git commit -m "#81 board + gate check + session logs (staged, awaiting promote)"
python3 scripts/olivia_wf.py unlock
```

Prepend the dated entry to `SESSION_LOG_OLIVIA.md` (migrations by name, staging versionId, probe ids, gate count, what is still open), one line to `SESSION_LOG.md`, and update the `OLIVIA_NEXT_SESSION.md` state block with the promote command.

---

## Self-review notes

- **Spec coverage.** Andy's four complaints map to tasks: spam/wall-of-names → Task 3 LONG ROSTERS + Task 4 Step 1; formatting → same rule (12-name cap, grouped remainder); pivoting away from the core job → Task 1 (the data) + Task 3 WHO SHOULD I TALK TO; "I can't" openers → Task 3 NEVER CALL A DATA GAP A LIMIT, asserted in Task 4 Step 3 check 1. "Do we use personas / is it niches only" → answered by Task 1's evidence table and fixed by Task 1. "Build a relationship graph" → deliberately NOT built; Task 1 Step 5 is the test that proves per-asker fit is the right shape instead.
- **Deliberately out of scope, and why:** the 50-question follow-up eval set. It is a measurement instrument, not part of this fix, and #76 already owns rebuilding the bank from real traffic. Building it against a system mid-change would bake in today's behaviour. It runs after this promote.
- **Named remainder (corrected 2026-08-11 after Andy challenged the number):** on the real Summit roster of 108, **10 carry no topic profile and every one of them is MDS Team or has no member record** — staff should not be presented as a business fit anyway, so they simply appear with name and city and rank last. No real member is unmatchable. The earlier "49 of 148" figure was wrong: it came from a bare `%singapore%` join that swept in side events and 43 non-member `E-commerce Entrepreneur` social guests. Any future coverage claim must replicate `event_who`'s ticket_for + status filter first.
- **Type consistency:** `fit_reason text` and `shared_topics text[]` are named identically in Task 1's migration, Task 3's tool description, Task 4's assertions and Task 5's gate check. `p_group_by='gender'` likewise.
- Task 2 uses `CREATE OR REPLACE` (no DROP) because neither the signature nor the return type changes — unlike Task 1, which changes the return type and therefore must DROP and reload PostgREST.
