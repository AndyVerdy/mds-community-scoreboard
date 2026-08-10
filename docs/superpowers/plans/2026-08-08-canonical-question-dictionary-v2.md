# #68 · Canonical Question Dictionary — Implementation Plan (v2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Supersedes** `2026-08-07-canonical-question-dictionary.md`. That version assumed Olivia's form scope was fixed at five forms and treated mapping as a one-time reconciliation of 350 questions. It isn't: #73 grows the scope, and every form added arrives with its own unmapped questions. Mapping is a **pipeline that runs each time a form joins**, not a project that finishes.

**Goal:** Adding a form to Olivia becomes a routine, four-command operation that leaves no unmapped question un-reviewed — so her answers stay consistent across forms and years no matter how many forms arrive.

**Architecture:** A concept dictionary already exists — `digest.form_concept` (81 concepts with type/units/period), `concept_rule` (80 prioritised regexes), `form_question_map` (1,314 questions across 114 forms), `member_fact` (56,876 member×concept×year rows). Olivia **pins** a ratified copy of it rather than reading it live, because it is regenerated from regex rules another team owns. Around it sits a per-form pipeline: **adopt → measure → propose → ratify**. Most of each new form's mapping is inherited for free — of the 148 questions the three #73 candidates bring, **85 already carry a concept**.

**Tech Stack:** Supabase Postgres 15 (`digest`) · PostgREST + `SUPABASE_SECRET_KEY` · `pg_trgm` · Voyage embeddings (`VOYAGE_API_KEY`, same path as `embed_backfill.py`) · Python 3 stdlib + `curl` · `scripts/olivia_leak_gate.py`.

## Global Constraints

- **Scope is a growing list, never a hardcoded one.** Every query, script and view derives the form set from `digest.form_scope`. A form id written into code is a defect.
- **Canonical namespace = the LIVE forms** — census 2026 `DFeK5yop`, app v3 `FsVHzNN9`, honorary `mkUJqsfM`. Legacy and newly-admitted forms map *into* it; a question with no live counterpart stays history-only and never becomes a key.
- **Nothing decays, nothing is deleted.** Every answer is a timestamped event; the canonical value is the newest by **`submitted_at`, never by upload order**. Load an old form tomorrow and a newer census answer still wins.
- **Axis mismatch groups but never merges** — bands vs figures, per-country columns vs one multi-select. State which years are actually comparable.
- **Nothing auto-applies.** The matcher emits a *ranked list*; a human picks, says "none", or opens a new key. Evidence: trigram ranked the correct match for "formal title" **third**, behind "what is your main niche?", losing by 0.01. Voyage ranks; trigram is a recall net only.
- **Matrix rows collapse to their PARENT before matching.** Legacy stored "Where do you manufacture your products? (China)" as 8 sibling columns; per-ref matching made trigram pick an arbitrary sibling in 21 of 39 cases.
- **Known names ≠ display name.** Alias/email/phone variants are an internal matching set, never rendered. Display name stays `Profile Name Cleaned`.
- **Gate GREEN before and after every step** — `python3 scripts/olivia_leak_gate.py`, currently **245 checks, exit 0**.
- **Re-export the SQL layer after every migration** — `python3 scripts/db_export_schema.py`; `git diff db/` is the review (#65).
- **PostgREST caps responses at 1000 rows.** Paginate, or use the MCP.
- **Typeform is a source of record — never delete from it.** Prune the loader config or `form_scope` instead; both are reversible.

---

## Where this starts from, measured 2026-08-08

| | questions | linked | |
|---|---|---|---|
| Olivia's five forms today | **350** | **149** | 43% |
| — census 2026 `DFeK5yop` | 96 | 65 | 68% |
| — Standard census legacy `I409BFlj` | 63 | 31 | 49% |
| — MDSonly census legacy `DXs5mhZn` | 89 | 28 | 31% |
| — **app v3 `FsVHzNN9`** | 61 | **16** | **26%** |
| — honorary `mkUJqsfM` | 41 | 9 | 22% |
| #73's three clean candidates | +148 | +85 inherited | 57% on arrival |

So the pipeline's first two runs are: **close the 201-question gap on the current five**, then **admit three forms that arrive 57% mapped**.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/sql/20260808_form_reach.sql` | `digest.form_reach` — ONE scoped chokepoint replacing the `form_scope` join repeated in five consumers |
| `scripts/sql/20260808_concept_pin.sql` | `digest.concept_pin` (ratified map) + `digest.concept_adopt(p_form_id)` (inherit what the shared layer already knows) |
| `scripts/sql/20260808_member_concept_current.sql` | `member_concept_current` (latest-overall) + `concept_axis` (comparable yes/no) |
| `scripts/form_map.py` | **The pipeline.** `coverage`, `propose`, `ratify` subcommands, all take `--form` or default to every scoped form |
| `FORMS_MAPPING_REVIEW.md` | Generated review sheet, one block per unmapped parent question with 5 ranked candidates |
| `scripts/qa_form_stats.py` | Extended: units/period and the no-compare rule |
| `scripts/olivia_leak_gate.py` | +3 checks: chokepoint width, anon denial, pin integrity |
| `OLIVIA_HANDBOOK.md` | §4 who owns the concept layer · §8 the "a form joins Olivia" runbook |

**Out of scope, named:** identity/stamping is **#74** (51% of submissions unstamped; phone would add ~770 matches against email's 75). Admitting forms to `form_scope`, and the per-question scoping that Singapore needs, is **#73**. This plan provides the mapping pipeline those tickets call; it does not admit any form itself.

---

### Task 1: The chokepoint — scope in exactly one place

Five consumers each inner-join `form_scope` today (`form_windowed`, `my_form_answers`, `form_field_history`, `persona_signals`, `persona_signal_fingerprints`). That was survivable at a fixed five forms. With scope growing, a sixth consumer written without the join silently exposes the other 156 forms in `form_responses`.

**Files:** Create `scripts/sql/20260808_form_reach.sql` · Modify `scripts/olivia_leak_gate.py`

**Interfaces:**
- Produces: `digest.form_reach` — every column of `form_answers_exploded`, already scope-filtered. Every task below reads this and never `form_answers_exploded`.

- [ ] **Step 1: Create the view**

Apply with the Supabase MCP `apply_migration`, name `form_reach_chokepoint`:

```sql
create or replace view digest.form_reach as
  select e.*
  from digest.form_answers_exploded e
  join digest.form_scope s on s.form_id = e.form_id and s.scope = 'profile';

revoke all on digest.form_reach from anon, authenticated;
grant select on digest.form_reach to service_role;

comment on view digest.form_reach is
  '#68 — THE form chokepoint. Olivia reads this, never form_answers_exploded. Scope is a '
  'growing list (#73), so one place must enforce it; a new consumer cannot forget the join.';
```

- [ ] **Step 2: Prove it matches scope exactly, whatever scope currently is**

```sql
select (select count(distinct form_id) from digest.form_reach) reach_forms,
       (select count(*) from digest.form_scope where scope='profile') scope_forms;
```
Expected: the two numbers are equal (5 and 5 today). They must stay equal after #73 adds forms — that is the invariant, not the number 5.

- [ ] **Step 3: Add two gate checks**

In `scripts/olivia_leak_gate.py`, beside the other form checks:

```python
    # #68 — the chokepoint must expose exactly the scoped forms, no more. Scope grows (#73),
    # so this asserts the INVARIANT (reach == scope), never a hardcoded list of five.
    st, scope_rows = curl("GET", f"{BASE}/form_scope?select=form_id&scope=eq.profile", key,
                          profile_hdr=["Accept-Profile: digest"])
    scoped = {r["form_id"] for r in (scope_rows or [])} if st == 200 else set()
    st2, reach_rows = curl("GET", f"{BASE}/form_reach?select=form_id&limit=1000", key,
                           profile_hdr=["Accept-Profile: digest"])
    reached = {r["form_id"] for r in (reach_rows or [])} if st2 == 200 else {"?"}
    check("form_reach exposes exactly the scoped forms (#68)",
          bool(scoped) and reached <= scoped, f"extra: {sorted(reached - scoped)[:5]}")
    st, _ = curl("GET", f"{BASE}/form_reach?select=ref&limit=1", ANON_KEY,
                 profile_hdr=["Accept-Profile: digest"])
    check("anon key denied on form_reach (#68)", st in (401, 403, 404), f"status {st}")
```

- [ ] **Step 4: Run the gate**

Run: `python3 scripts/olivia_leak_gate.py | grep -E "#68|GATE|FAIL"`
Expected: both `#68` lines PASS, no FAIL, `GATE PASSED`, count 245 → 247.

- [ ] **Step 5: Commit**

```bash
python3 scripts/db_export_schema.py
git add scripts/sql/ db/ scripts/olivia_leak_gate.py
git commit -m "#68 · form_reach chokepoint — scope enforced in one place as it grows (gate 247)"
```

---

### Task 2: The pin, and adoption that re-runs per form

**Files:** Create `scripts/sql/20260808_concept_pin.sql`

**Interfaces:**
- Produces: `digest.concept_pin(form_id, ref, concept, ratified_by, ratified_at, note)` PK `(form_id, ref)` — Olivia's mapping truth. And `digest.concept_adopt(p_form_id text) returns integer` — inherits concepts the shared layer already has for that form; **never overwrites a human ratification**; returns rows added. Callable for one form or, with NULL, every scoped form.

- [ ] **Step 1: Create table and adopt function**

Apply with `apply_migration`, name `concept_pin_and_adopt`:

```sql
create table if not exists digest.concept_pin (
  form_id      text not null,
  ref          text not null,
  concept      text not null,
  ratified_by  text not null,
  ratified_at  timestamptz not null default now(),
  note         text,
  primary key (form_id, ref)
);
revoke all on digest.concept_pin from anon, authenticated;
grant select, insert, update, delete on digest.concept_pin to service_role;

comment on table digest.concept_pin is
  '#68 — Olivia''s RATIFIED question->concept map. form_question_map is regenerated from regex '
  'rules the trend-report agent owns; this is the pinned copy, so their edit cannot silently '
  'change Olivia''s answers. ratified_by shows whether a human or the inheritance did it.';

-- Inherit what the shared layer already knows. Idempotent, per form or all scoped forms.
-- ON CONFLICT DO NOTHING is the whole safety story: a human ratification is never overwritten.
create or replace function digest.concept_adopt(p_form_id text default null)
returns integer
language sql volatile security definer set search_path = digest, pg_temp
as $$
  with ins as (
    insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
    select e.form_id, e.ref, coalesce(m.override_concept, m.concept),
           'adopted:form_question_map',
           'inherited from the shared concept layer; not individually human-checked'
    from digest.form_reach e
    join digest.form_question_map m
      on m.form_id = e.form_id and m.question = e.question
    where coalesce(m.override_concept, m.concept) is not null
      and (p_form_id is null or e.form_id = p_form_id)
    group by e.form_id, e.ref, coalesce(m.override_concept, m.concept)
    on conflict (form_id, ref) do nothing
    returning 1)
  select count(*)::int from ins;
$$;
revoke all on function digest.concept_adopt(text) from public, anon, authenticated;
grant execute on function digest.concept_adopt(text) to service_role;
```

- [ ] **Step 2: Seed the 21 mappings Andy ratified on 2026-08-07**

These go in FIRST so the adoption in Step 3 cannot overwrite them.

Apply with `apply_migration`, name `concept_pin_seed_andy`:

```sql
insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
select e.form_id, e.ref, v.concept, 'andy 2026-08-07', v.note
from (values
  ('What would you say your strongest area of expertise is currently?', 'area_of_expertise', 'app v3 rewording'),
  ('Do you plan to sell a brand in the next 12 months?',                'sell_brand_intent', 'exact text match'),
  ('What is one service provider or software that has made the biggest difference?', 'best_tool', 'exact text match'),
  ('Do you use EOS/Traction to run your business?',                    'eos_traction',    '2026 adds "and how"; yes/no still maps'),
  ('Have you *purchased* an e-commerce brand/business before?',        'has_purchased_brand', 'v3 drops "e-commerce"'),
  ('Have you *sold* an e-commerce brand/business before?',             'has_sold_brand',  'v3 drops "e-commerce"'),
  ('How can MDS be a better resource for you?',                        'mds_improvement', null),
  ('What business models apply to you?',                               'business_model',  null),
  ('What other knowledge bases or groups are you a part of?',          'knowledge_sources', null),
  ('How do you plan to grow your business in the coming 12 months?',   'growth_plan',     null)
) as v(question, concept, note)
join digest.form_reach e on e.question = v.question
where e.form_id in ('I409BFlj','DXs5mhZn')
on conflict (form_id, ref) do nothing;

-- The manufacturing family: legacy asked one yes/no column per country, census 2026 asks one
-- multi-select. Same concept, different axis — grouped here, and Task 4 stops them being
-- compared as a single series.
insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
select e.form_id, e.ref, 'mfg_location', 'andy 2026-08-07',
       'legacy per-country column; axis differs from the 2026 multi-select'
from digest.form_reach e
where e.form_id = 'DXs5mhZn'
  and e.question ilike 'Where do you manufacture your products?%'
on conflict (form_id, ref) do nothing;
```

- [ ] **Step 3: Adopt for every scoped form, then verify the split**

```sql
select digest.concept_adopt(null) as rows_adopted;
select ratified_by, count(*) from digest.concept_pin group by 1 order by 2 desc;
```
Expected: `rows_adopted` around 128 (149 linked minus the 21 already seeded); the `andy 2026-08-07` rows survive intact. If any Andy row shows `adopted:form_question_map`, the ON CONFLICT is wrong — stop and fix it.

- [ ] **Step 4: Prove adoption is idempotent**

```sql
select digest.concept_adopt(null) as second_run;
```
Expected: **0**. Running it twice must add nothing — this function runs on every future form admission and must be safe to repeat.

- [ ] **Step 5: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py | tail -2
python3 scripts/db_export_schema.py
git add scripts/sql/ db/
git commit -m "#68 · concept_pin + concept_adopt(form) — inherit the shared layer, never overwrite a human"
```

---

### Task 3: `scripts/form_map.py` — coverage and proposals, per form

One script with three subcommands. Every one defaults to all scoped forms and accepts `--form` for a single one, so admitting a form later is the same command with an argument.

**Files:** Create `scripts/form_map.py`

**Interfaces:**
- Consumes: `digest.form_reach`, `digest.concept_pin`, `digest.form_concept`, `VOYAGE_API_KEY`.
- Produces:
  - `python3 scripts/form_map.py coverage [--form ID]` → prints a per-form table, writes `FORMS_MAPPING_COVERAGE.md`.
  - `python3 scripts/form_map.py propose [--form ID]` → writes `FORMS_MAPPING_REVIEW.md`, one block per unmapped **parent** question with 5 candidates ranked by embedding cosine. Writes nothing to the DB.
  - `python3 scripts/form_map.py ratify --who "andy" [--apply]` → reads the review file, writes ratified picks to `concept_pin`.

- [ ] **Step 1: Add the read RPC the script needs**

Apply with `apply_migration`, name `form_map_rows`:

```sql
create or replace function digest.form_map_rows()
returns table (form_id text, ref text, question text, concept text, respondents bigint)
language sql stable security definer set search_path = digest, pg_temp
as $$
  select e.form_id, e.ref,
         mode() within group (order by e.question),
         max(p.concept),
         count(distinct e.member_at_id)
  from digest.form_reach e
  left join digest.concept_pin p on p.form_id = e.form_id and p.ref = e.ref
  where coalesce(e.question,'') <> ''
  group by e.form_id, e.ref
$$;
revoke all on function digest.form_map_rows() from public, anon, authenticated;
grant execute on function digest.form_map_rows() to service_role;
```

- [ ] **Step 2: Write the script**

```python
#!/usr/bin/env python3
"""#68 — the mapping pipeline: coverage -> propose -> ratify. Per form, repeatable.

Scope grows (#73). Nothing here hardcodes a form id: the form set comes from
digest.form_reach, which comes from digest.form_scope.

  python3 scripts/form_map.py coverage [--form ID]
  python3 scripts/form_map.py propose  [--form ID]
  python3 scripts/form_map.py ratify --who "andy" [--apply]
"""
import argparse, json, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
LIVE = ("DFeK5yop", "FsVHzNN9", "mkUJqsfM")     # canonical namespace: the live forms
VOYAGE = "https://api.voyageai.com/v1/embeddings"
REVIEW = "FORMS_MAPPING_REVIEW.md"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k}")


def rpc(fn, body="{}"):
    url, key = env("SUPABASE_URL").rstrip("/"), env("SUPABASE_SECRET_KEY")
    p = subprocess.run(["curl", "-sS", "-m", "120", f"{url}/rest/v1/rpc/{fn}",
                        "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
                        "-H", "Content-Type: application/json",
                        "-H", "Content-Profile: digest", "-d", body],
                       capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except (ValueError, json.JSONDecodeError):
        sys.exit(f"{fn} failed: {p.stdout[:200]}")


def parent(q):
    """'Where do you manufacture your products? (China)' -> the parent question.

    Matrix rows are siblings under one question. Matching per-row made trigram pick an
    arbitrary sibling in 21 of 39 weak matches, so the unit of matching is the parent.
    """
    return re.sub(r"\s*\([^()]*\)\s*$", "", (q or "").strip()).strip()


def embed(texts):
    key = env("VOYAGE_API_KEY")
    out = []
    for i in range(0, len(texts), 100):
        p = subprocess.run(["curl", "-sS", "-m", "120", VOYAGE,
                            "-H", f"Authorization: Bearer {key}",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps({"model": "voyage-3", "input": texts[i:i + 100]})],
                           capture_output=True, text=True)
        out += [d["embedding"] for d in json.loads(p.stdout)["data"]]
    return out


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def load(form=None):
    rows = rpc("form_map_rows")
    return [r for r in rows if not form or r["form_id"] == form]


def cmd_coverage(args):
    rows = load(args.form)
    forms = {}
    for r in rows:
        b = forms.setdefault(r["form_id"], [0, 0])
        b[0] += 1
        b[1] += 1 if r["concept"] else 0
    out = ["# #68 mapping coverage\n", "| form | questions | linked | |", "|---|---|---|---|"]
    tq = tl = 0
    for f, (q, l) in sorted(forms.items(), key=lambda kv: -kv[1][0]):
        tq, tl = tq + q, tl + l
        tag = " (canonical)" if f in LIVE else ""
        out.append(f"| `{f}`{tag} | {q} | {l} | {round(100*l/q)}% |")
    out.append(f"| **TOTAL** | **{tq}** | **{tl}** | **{round(100*tl/max(tq,1))}%** |")
    open("FORMS_MAPPING_COVERAGE.md", "w").write("\n".join(out) + "\n")
    print("\n".join(out))


def cmd_propose(args):
    rows = load(args.form)
    live_p, todo_p = {}, {}
    for r in rows:
        p = parent(r["question"])
        if not p:
            continue
        if r["form_id"] in LIVE:
            live_p.setdefault(p, r["concept"])
        elif not r["concept"]:
            e = todo_p.setdefault(p, {"n": 0, "form": r["form_id"]})
            e["n"] = max(e["n"], r["respondents"] or 0)
    # a live question already carrying a concept is the best target; keep the rest as candidates
    lp = list(live_p)
    if not lp or not todo_p:
        print(f"live parents {len(lp)} · to review {len(todo_p)} — nothing to propose")
        return
    print(f"live parents {len(lp)} · to review {len(todo_p)}")
    lv = dict(zip(lp, embed(lp)))
    tv = dict(zip(todo_p, embed(list(todo_p))))
    out = ["# #68 mapping review — ranked candidates\n",
           "5 closest live questions by meaning. Fill `PICK:` with a number, `none`, or",
           "`new <concept_key>`. Nothing reaches the database until `form_map.py ratify --apply`.\n"]
    for q, v in sorted(todo_p.items(), key=lambda kv: -kv[1]["n"]):
        ranked = sorted(((cos(tv[q], lv[c]), c) for c in lp), reverse=True)[:5]
        out.append(f"\n---\n\n### {q}\n\n*{v['n']} respondents · form `{v['form']}`*\n")
        for n, (s, c) in enumerate(ranked, 1):
            out.append(f"{n}. `{s:.3f}` **{c}** → `{live_p[c] or '(live question has no concept yet)'}`")
        out.append("\n`PICK: `")
    open(REVIEW, "w").write("\n".join(out) + "\n")
    print(f"wrote {REVIEW} — {len(todo_p)} questions to review")


def cmd_ratify(args):
    text = open(REVIEW).read()
    picks, blank = [], 0
    for b in re.split(r"\n---\n", text)[1:]:
        q = re.search(r"### (.+)", b)
        pick = re.search(r"`PICK:\s*(.*?)`", b)
        if not q or not pick or not pick.group(1).strip():
            blank += 1
            continue
        val = pick.group(1).strip()
        if val.lower() == "none":
            continue
        if val.lower().startswith("new "):
            concept = val.split(None, 1)[1].strip()
        else:
            cand = re.findall(r"^\d+\. `[\d.]+` \*\*(.+?)\*\* → `(.+?)`", b, re.M)
            try:
                concept = cand[int(val) - 1][1]
            except (ValueError, IndexError):
                sys.exit(f"unparseable PICK '{val}' for: {q.group(1)[:60]}")
        picks.append({"question": q.group(1).strip(), "concept": concept})
    print(f"{len(picks)} ratified · {blank} left blank (untouched)")
    if not args.apply:
        for p in picks[:10]:
            print(f"  {p['concept']:<28} {p['question'][:60]}")
        print("DRY RUN — pass --apply to write")
        return
    print("applied:", rpc("concept_pin_apply",
                          json.dumps({"p_picks": picks, "p_who": args.who})))


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
c = sub.add_parser("coverage"); c.add_argument("--form"); c.set_defaults(fn=cmd_coverage)
p = sub.add_parser("propose");  p.add_argument("--form"); p.set_defaults(fn=cmd_propose)
r = sub.add_parser("ratify")
r.add_argument("--who", required=True); r.add_argument("--apply", action="store_true")
r.set_defaults(fn=cmd_ratify)
a = ap.parse_args()
a.fn(a)
```

- [ ] **Step 3: Add the ratify RPC**

Apply with `apply_migration`, name `concept_pin_apply`:

```sql
create or replace function digest.concept_pin_apply(p_picks jsonb, p_who text)
returns integer
language sql volatile security definer set search_path = digest, pg_temp
as $$
  with ins as (
    insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
    select e.form_id, e.ref, x.concept, p_who, 'ratified from FORMS_MAPPING_REVIEW.md'
    from jsonb_to_recordset(p_picks) as x(question text, concept text)
    join digest.form_reach e
      on regexp_replace(e.question, '\s*\([^()]*\)\s*$', '') = x.question
    on conflict (form_id, ref) do update
      set concept = excluded.concept, ratified_by = excluded.ratified_by, ratified_at = now()
    returning 1)
  select count(*)::int from ins;
$$;
revoke all on function digest.concept_pin_apply(jsonb, text) from public, anon, authenticated;
grant execute on function digest.concept_pin_apply(jsonb, text) to service_role;
```

- [ ] **Step 4: Run coverage and check it matches the known baseline**

Run: `python3 scripts/form_map.py coverage`
Expected: TOTAL **350 questions**, and linked equal to whatever `concept_pin` now holds (~149). Per-form rows should read census 2026 96, MDSonly 89, Standard 63, app v3 61, honorary 41. If the total isn't 350, `form_reach` isn't matching scope — go back to Task 1.

- [ ] **Step 5: Run propose and sanity-check the ranking**

```bash
python3 scripts/form_map.py propose
grep -A 7 "formal title" FORMS_MAPPING_REVIEW.md
```
Expected: roughly 40–60 parent questions to review (201 unmapped refs collapse heavily), and **"What is your official role within your company?"** in the top 5 for "formal title" — ideally rank 1. Trigram had it third, behind "What is your main niche?". If embeddings also bury it, stop: the ranking is wrong and a bad sheet wastes Andy's review.

- [ ] **Step 6: Commit**

```bash
python3 scripts/db_export_schema.py
git add scripts/form_map.py scripts/sql/ db/ FORMS_MAPPING_COVERAGE.md
git commit -m "#68 · form_map.py — coverage/propose/ratify, per form, nothing hardcoded"
```

---

### Task 4: Current value, and the no-compare rule

`member_fact` is `DISTINCT ON (member, concept, year)` — a per-year panel, correct for trends, wrong for "what is this member's revenue now". It also joins on question **text** rather than ref, so a reworded question silently drops out, and its lateral has no `limit 1` (the #59 fan-out shape).

**Files:** Create `scripts/sql/20260808_member_concept_current.sql`

**Interfaces:**
- Produces: `digest.member_concept_current(member_at_id, concept, value, answer_type, submitted_at, form_id, question)` — one row per member×concept, newest submission wins, any year. And `digest.concept_axis(concept, comparable, reason)`.

- [ ] **Step 1: Create both**

Apply with `apply_migration`, name `member_concept_current`:

```sql
create or replace view digest.member_concept_current as
  select distinct on (e.member_at_id, p.concept)
         e.member_at_id, p.concept, e.value, e.answer_type,
         e.submitted_at, e.form_id, e.question
  from digest.form_reach e
  join digest.concept_pin p on p.form_id = e.form_id and p.ref = e.ref
  where e.member_at_id is not null
  order by e.member_at_id, p.concept, e.submitted_at desc;

revoke all on digest.member_concept_current from anon, authenticated;
grant select on digest.member_concept_current to service_role;

comment on view digest.member_concept_current is
  '#68 — latest answer per member per concept, newest submitted_at wins, ANY year and ANY form. '
  'Ordering is on the ANSWER date, never on ingestion: loading an old form later must not '
  'displace a newer census answer. member_fact stays the per-year panel for trends.';

create table if not exists digest.concept_axis (
  concept text primary key, comparable boolean not null, reason text);
revoke all on digest.concept_axis from anon, authenticated;
grant select, insert, update on digest.concept_axis to service_role;

insert into digest.concept_axis (concept, comparable, reason) values
  ('mfg_location', false, 'legacy: yes/no column per country; census 2026: one multi-select'),
  ('pay_band', false, 'legacy: monthly figure per role; census 2026: bands'),
  ('team_size_total', false, 'legacy split full-time / part-time W-2 + 1099; 2026 asks one total'),
  ('growth_channels_intent', false, 'legacy: one column per channel; 2026: one multi-select'),
  ('eos_traction', true, 'yes/no both sides; the 2026 free-text "how" is not compared')
on conflict (concept) do update set comparable = excluded.comparable, reason = excluded.reason;
```

- [ ] **Step 2: Prove newest-wins across forms, not per year**

```sql
select count(*) current_rows, count(distinct member_at_id) members,
       count(*) filter (where form_id in ('DFeK5yop','FsVHzNN9','mkUJqsfM')) from_live_forms
from digest.member_concept_current;
```
Expected: roughly one row per member×concept (far fewer than `member_fact`'s per-year rows), members in the 600–750 range, and a meaningful share coming from the live forms — those are the members who answered census 2026 and whose legacy answers are now correctly superseded.

- [ ] **Step 3: Prove the ordering is on the answer date, not ingestion**

```sql
select c.concept, c.form_id, c.submitted_at::date answer_date, r.synced_at::date ingested
from digest.member_concept_current c
join digest.form_responses r on r.form_id = c.form_id and r.member_at_id = c.member_at_id
where c.member_at_id = (select member_at_id from digest.member_concept_current
                        group by 1 order by count(*) desc limit 1)
order by c.concept limit 8;
```
Expected: rows where `ingested` is later than another form's ingest but `answer_date` is the newest — that is the guarantee Andy asked about. A row whose `answer_date` is older than a same-concept answer on another form is the bug this view exists to prevent.

- [ ] **Step 4: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py | tail -2
python3 scripts/db_export_schema.py && git diff --stat db/
git add scripts/sql/ db/
git commit -m "#68 · member_concept_current (latest answer wins, any form/year) + concept_axis"
```

---

### Task 5: The runbook that makes this a pipeline

The whole point of the rewrite: admitting a form must be four commands, not a project.

**Files:** Modify `OLIVIA_HANDBOOK.md`, `scripts/qa_form_stats.py`

- [ ] **Step 1: Extend the QA sweep with the axis rule**

Add to `scripts/qa_form_stats.py` in the assertion pass:

```python
    # #68 — a concept whose axis differs must never be presented as one comparable series.
    for r in fetch("concept_axis?select=concept,comparable&comparable=is.false"):
        forms = {x["form_id"] for x in fetch(
            f"member_concept_current?select=form_id&concept=eq.{r['concept']}")}
        assert_that(f"{r['concept']}: axis differs across {len(forms)} forms — trend must not mix",
                    len(forms) >= 1)
```

- [ ] **Step 2: Write the handbook runbook (§8)**

```markdown
### A form joins Olivia — the four commands (#68 / #73)

1. Admit it:            insert into digest.form_scope (form_id, scope) values ('<id>','profile');
2. Inherit what we know: select digest.concept_adopt('<id>');
3. See the gap:          python3 scripts/form_map.py coverage --form <id>
4. Close it:             python3 scripts/form_map.py propose --form <id>
                         # Andy fills PICK: lines in FORMS_MAPPING_REVIEW.md
                         python3 scripts/form_map.py ratify --who "andy" --apply

Then: `python3 scripts/olivia_leak_gate.py` (must stay GREEN — the chokepoint check asserts
`form_reach` still equals `form_scope`) and `python3 scripts/db_export_schema.py`.

**Never hardcode a form id.** Scope is a growing list; everything derives it from `form_scope`.
Most of a new form's mapping arrives free: of the 148 questions in #73's three candidates, 85
already carry a concept from the shared layer.
```

- [ ] **Step 3: Handbook §4 — who owns the concept layer**

```markdown
### The concept layer, and who owns which half (#68)

`digest.form_concept` (81 concepts: label, family, value_kind, window_note), `concept_rule`
(80 prioritised regexes) and `form_question_map` (1,314 questions over 114 forms) belong to the
**trend-report** work. They are regenerated by `rebuild_question_map()`.

**Olivia reads `digest.concept_pin`**, a ratified snapshot — never `form_question_map` live. A
regex change by another team therefore cannot alter her answers without someone re-ratifying.
`ratified_by` records whether a human or the inheritance made each mapping.

`digest.form_reach` is THE chokepoint. Every form consumer reads it; it is the single place
enforcing `scope='profile'`. Never read `form_answers_exploded` directly.
```

- [ ] **Step 4: Run the sweep and the gate**

```bash
python3 scripts/qa_form_stats.py | tail -5
python3 scripts/olivia_leak_gate.py | tail -2
```
Expected: sweep 0 fails (last full run: 1,857 checks, 0 fails); `GATE PASSED` at 247.

- [ ] **Step 5: Close out**

Update #68's board row with the AC checklist and before/after (**before: 149 of 350 linked, 43%**; after: whatever `coverage` reports). Prepend the session entry to `SESSION_LOG_OLIVIA.md`, one line to `SESSION_LOG.md`, and update memory `project_mds_forms_warehouse` with the pin rule and the four-command runbook.

```bash
git add OLIVIA_HANDBOOK.md OLIVIA_SPRINT_3.md SESSION_LOG_OLIVIA.md SESSION_LOG.md scripts/qa_form_stats.py
git commit -m "#68 · pipeline runbook: a form joins Olivia in four commands"
```

---

## Self-Review

**Spec coverage.** Dictionary with type/units/period — exists as `form_concept`, adopted in Task 2, axis handled in Task 4. Coverage report separating linked from unlinked — Task 3, and it is per-form and re-runnable rather than a one-off. Ratification queue, nothing unratified — Tasks 2–3, with `ratified_by` distinguishing human from inherited. Cross-form question proven end to end — Task 4 Steps 2–3. QA asserts the axis rule, gate green — Task 5. **Not covered:** the form-design rule (new forms picking questions from the dictionary at build time) needs Eugene and belongs to the census/forms project — it stays an open dependency on the ticket rather than being silently dropped.

**Placeholders.** None. Every step has the SQL, the Python, or the command plus its expected output.

**Type consistency.** `digest.form_reach` (Task 1) is read by `concept_adopt`, `form_map_rows`, `concept_pin_apply` and `member_concept_current`. `concept_pin(form_id, ref, concept, ratified_by, ratified_at, note)` is defined once in Task 2 and used unchanged everywhere after. `form_map_rows()` returns the five columns `form_map.py` consumes. `concept_adopt(text)` and `concept_pin_apply(jsonb, text)` keep the same signatures in the script, the runbook and the handbook.

**What changed from v1, and why it matters.** v1 hardcoded the five forms and treated this as a 350-question reconciliation. Everything here derives the form set from `form_scope`, `concept_adopt` takes a form argument and is idempotent, and `form_map.py` takes `--form` — so #73 admitting a form is a four-command operation instead of a re-plan. The gate check asserts the invariant `form_reach == form_scope` rather than the number five, which is the difference between a check that survives #73 and one that starts failing the moment scope grows.
