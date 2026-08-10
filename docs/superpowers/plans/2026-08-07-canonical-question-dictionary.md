> ⛔ **SUPERSEDED by `2026-08-08-canonical-question-dictionary-v2.md`.** This version assumed
> Olivia's form scope was fixed at five forms and treated mapping as a one-time reconciliation.
> It is a pipeline that runs each time a form joins scope (#73). Kept for the record only.

# #68 · Canonical Question Dictionary — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every concept the community answers about resolves to ONE field across forms and years, so a question about revenue or pay finds every form that ever asked it — without a second dictionary, and without a machine ever guessing a mapping.

**Architecture:** A concept layer already exists — `digest.form_concept` (81 concepts with type/units/period), `concept_rule` (80 prioritised regexes), `form_question_map` (1,314 questions across 114 forms), `member_fact` (56,876 member×concept×year rows). It was built by the trend-report agent and already covers **183 of the 313 questions on Olivia's five forms**, versus 78 rows in Olivia's own `form_field_map`. This plan **converges Olivia onto that layer** instead of building a rival, pins it so another team's regex edit cannot silently change Olivia's answers, and closes the mapping gap with an assisted matcher that proposes ranked candidates for human ratification.

**Tech Stack:** Supabase Postgres 15 (`digest` schema) · PostgREST + `SUPABASE_SECRET_KEY` · `pg_trgm` (installed) · Voyage embeddings (`VOYAGE_API_KEY`, same path as `embed_backfill.py`) · Python 3 stdlib + `curl` · `scripts/olivia_leak_gate.py`.

## Global Constraints

- **Olivia's form scope is exactly five forms** — `DFeK5yop` (census 2026), `FsVHzNN9` (app v3), `mkUJqsfM` (honorary), `I409BFlj` + `DXs5mhZn` (legacy censuses). The other 109 forms in `form_responses` belong to the trend-report agent and **must stay unreachable**.
- **Canonical namespace = the three LIVE forms only.** Legacy maps *into* it. A legacy question with no live counterpart stays history-only and never becomes a key. (Andy, 2026-08-07.)
- **Nothing is deleted and nothing decays.** Every answer stays a timestamped event; the canonical value is the newest one. Replacement is organic: a new submission is a newer event. (Andy's correction, 2026-08-07.)
- **Axis mismatch groups but never merges.** Bands vs figures, per-country columns vs one multi-select — same concept, not one comparable series. Say which years can actually be compared.
- **Nothing auto-applies.** The matcher proposes a *ranked list*; a human picks one, says "none", or opens a new key. A wrong merge silently fuses two concepts, which is worse than unmapped.
- **Known names ≠ display name.** `Aliases` and other name variants are a matching set, internal only, never rendered. The display name stays `Profile Name Cleaned`. An alias reaching output is a defect.
- **Gate GREEN before and after every step** — `python3 scripts/olivia_leak_gate.py`, currently **245 checks, exit 0**.
- **Re-export the SQL layer after every migration** — `python3 scripts/db_export_schema.py`, then `git diff db/` is the review (#65).
- **PostgREST caps responses at 1000 rows.** Paginate or use the MCP for anything larger.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/sql/20260808_form_reach_view.sql` | ONE scoped chokepoint (`digest.form_reach`) replacing the `form_scope` join repeated in five consumers |
| `scripts/sql/20260808_concept_pin.sql` | `digest.concept_pin` — Olivia's ratified snapshot of question→concept, plus `form_concept_pinned` |
| `scripts/sql/20260808_member_concept_current.sql` | `digest.member_concept_current` — latest-overall value per member×concept (the panel view stays for trends) |
| `scripts/form_concept_match.py` | The matcher: collapse matrix rows to parents → exact → trigram → Voyage → **ranked candidates** → review sheet |
| `scripts/form_concept_ratify.py` | Applies a reviewed sheet into `concept_pin`; refuses anything unratified |
| `FORMS_MAPPING_REVIEW.md` | The generated review sheet Andy marks up |
| `scripts/qa_form_stats.py` | Extended: asserts units/period and that no concept mixes axes |
| `scripts/olivia_leak_gate.py` | +3 checks (pin integrity, wall via the chokepoint, no alias in output) |
| `OLIVIA_HANDBOOK.md` | §4 the concept layer and who owns it; §8 the re-ratify runbook |

**Out of scope, named:** the identity/stamping problem (4,617 of 9,089 responses unstamped, 2,871 of them carrying no identifier at all, `Aliases` populated for only 569 members). It surfaced during this design and deserves its own ticket — Task 7 files it. Mapping and identity are independent; neither blocks the other.

---

### Task 1: Baseline the mapping picture, read-only

**Files:**
- Create: `scripts/form_concept_coverage.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `python3 scripts/form_concept_coverage.py` prints, and writes `FORMS_MAPPING_COVERAGE.md`: per-form question counts, how many carry a concept, how many are in `form_field_map`, and the *needs-a-key* split (concept appears on 2+ of Olivia's five forms) versus single-form.

- [ ] **Step 1: Write the coverage script**

```python
#!/usr/bin/env python3
"""#68 — where mapping actually stands, before we change anything. Read-only."""
import json, subprocess, collections

ENV = "/Users/Born/mds-digest-web/.env.local"
LIVE = ("DFeK5yop", "FsVHzNN9", "mkUJqsfM")          # canonical namespace
LEGACY = ("I409BFlj", "DXs5mhZn")


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"missing {k}")


def sql(q):
    """digest.schema_source() proved PostgREST can't run ad-hoc SQL; use the RPC surface."""
    url, key = env("SUPABASE_URL").rstrip("/"), env("SUPABASE_SECRET_KEY")
    p = subprocess.run(["curl", "-sS", "-m", "90", f"{url}/rest/v1/rpc/form_coverage_report",
                        "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
                        "-H", "Content-Type: application/json",
                        "-H", "Content-Profile: digest", "-d", "{}"], capture_output=True, text=True)
    return json.loads(p.stdout)


rows = sql(None)
by_form = collections.defaultdict(lambda: {"q": 0, "concept": 0, "ffm": 0})
for r in rows:
    b = by_form[r["form_id"]]
    b["q"] += 1
    b["concept"] += 1 if r["concept"] else 0
    b["ffm"] += 1 if r["in_field_map"] else 0

concept_forms = collections.defaultdict(set)
for r in rows:
    if r["concept"]:
        concept_forms[r["concept"]].add(r["form_id"])
needs_key = {c for c, fs in concept_forms.items() if len(fs) > 1}

out = ["# #68 mapping coverage\n", "| form | questions | has concept | in form_field_map |",
       "|---|---|---|---|"]
for f, b in sorted(by_form.items(), key=lambda kv: -kv[1]["q"]):
    side = "live" if f in LIVE else ("legacy" if f in LEGACY else "?")
    out.append(f"| `{f}` ({side}) | {b['q']} | {b['concept']} | {b['ffm']} |")
out.append(f"\n**Concepts spanning 2+ forms (needs a key): {len(needs_key)}** of {len(concept_forms)} used.")
unmapped = [r for r in rows if not r["concept"]]
out.append(f"\n**Questions with no concept: {len(unmapped)}**")
open("FORMS_MAPPING_COVERAGE.md", "w").write("\n".join(out) + "\n")
print("\n".join(out[:8]))
print(f"... wrote FORMS_MAPPING_COVERAGE.md ({len(rows)} questions)")
```

- [ ] **Step 2: Add the RPC it reads**

Apply with the Supabase MCP `apply_migration`, name `form_coverage_report`:

```sql
create or replace function digest.form_coverage_report()
returns table (form_id text, ref text, question text, concept text,
               in_field_map boolean, respondents bigint)
language sql stable security definer set search_path = digest, pg_temp
as $$
  select e.form_id, e.ref,
         mode() within group (order by e.question),
         max(coalesce(m.override_concept, m.concept)),
         bool_or(f.canonical_key is not null),
         count(distinct e.member_at_id)
  from digest.form_answers_exploded e
  join digest.form_scope s on s.form_id = e.form_id and s.scope = 'profile'
  left join digest.form_question_map m
         on m.form_id = e.form_id and m.question = e.question
  left join digest.form_field_map f on f.form_id = e.form_id and f.ref = e.ref
  where coalesce(e.question, '') <> ''
  group by e.form_id, e.ref
$$;
revoke all on function digest.form_coverage_report() from public, anon, authenticated;
grant execute on function digest.form_coverage_report() to service_role;
```

- [ ] **Step 3: Run it**

Run: `python3 scripts/form_concept_coverage.py`
Expected: 313 questions across the five forms; roughly 183 with a concept, 78 in `form_field_map`. If the totals differ by more than a few, the other agent has re-run `rebuild_question_map()` — note the new numbers and carry on, they are the baseline.

- [ ] **Step 4: Re-export the SQL layer and confirm the gate**

```bash
python3 scripts/db_export_schema.py && git diff --stat db/
python3 scripts/olivia_leak_gate.py | tail -2
```
Expected: `db/functions/form_coverage_report.sql` added; `GATE PASSED`.

- [ ] **Step 5: Commit**

```bash
git add scripts/form_concept_coverage.py scripts/sql/ db/ FORMS_MAPPING_COVERAGE.md
git commit -m "#68 · coverage baseline: where question mapping actually stands"
```

---

### Task 2: One chokepoint for the form wall

Today `form_scope` is inner-joined in five separate places (`form_windowed`, `my_form_answers`, `form_field_history`, `persona_signals`, `persona_signal_fingerprints`). A sixth consumer written without it exposes the other agent's 109 forms. #58 fixed exactly this class for events with one view.

**Files:**
- Create: `scripts/sql/20260808_form_reach_view.sql`
- Modify: `scripts/olivia_leak_gate.py`

**Interfaces:**
- Produces: `digest.form_reach` — same columns as `form_answers_exploded`, already scope-filtered. Every later task reads this, never `form_answers_exploded`.

- [ ] **Step 1: Create the view**

Apply with `apply_migration`, name `form_reach_chokepoint`:

```sql
create or replace view digest.form_reach as
  select e.*
  from digest.form_answers_exploded e
  join digest.form_scope s on s.form_id = e.form_id and s.scope = 'profile';

revoke all on digest.form_reach from anon, authenticated;
grant select on digest.form_reach to service_role;

comment on view digest.form_reach is
  '#68 — THE form chokepoint. Olivia reads this, never form_answers_exploded. '
  'One place enforces scope=profile so a new consumer cannot forget the join.';
```

- [ ] **Step 2: Prove it returns five forms and nothing else**

```sql
select count(distinct form_id) forms, count(*) rows from digest.form_reach;
```
Expected: `forms = 5`, rows ≈ 111,822. Anything above 5 means `form_scope` gained a row — stop and find out who added it.

- [ ] **Step 3: Add the gate check**

In `scripts/olivia_leak_gate.py`, beside the other form checks:

```python
    # #68 — the chokepoint must never widen beyond Olivia's five profile forms.
    st, rows = curl("GET", f"{BASE}/form_reach?select=form_id&limit=1000", key,
                    profile_hdr=["Accept-Profile: digest"])
    forms = {r["form_id"] for r in (rows or [])} if st == 200 else set()
    check("form_reach exposes only scope=profile forms (#68)",
          st == 200 and forms <= {"DFeK5yop", "FsVHzNN9", "mkUJqsfM", "I409BFlj", "DXs5mhZn"},
          f"status {st}, forms {sorted(forms)[:8]}")
    st, _ = curl("GET", f"{BASE}/form_reach?select=ref&limit=1", ANON_KEY,
                 profile_hdr=["Accept-Profile: digest"])
    check("anon key denied on form_reach (#68)", st in (401, 403, 404), f"status {st}")
```

- [ ] **Step 4: Run the gate**

Run: `python3 scripts/olivia_leak_gate.py | grep -E "#68|GATE|FAIL"`
Expected: both `#68` lines PASS, no FAIL, `GATE PASSED`. Check count goes 245 → 247.

- [ ] **Step 5: Commit**

```bash
python3 scripts/db_export_schema.py
git add scripts/sql/ db/ scripts/olivia_leak_gate.py
git commit -m "#68 · digest.form_reach — one scoped chokepoint instead of five repeated joins (gate 247)"
```

---

### Task 3: The ratification table, seeded with what Andy already approved

Andy ratified 21 mappings by eye on 2026-08-07: 2 exact text matches, the 12 near matches, and 7 of the weak list (rows 1, 2, 5, 6, 7, 9, 15). Those go in as ratified history so the matcher never re-asks.

**Files:**
- Create: `scripts/sql/20260808_concept_pin.sql`

**Interfaces:**
- Produces: `digest.concept_pin(form_id, ref, concept, ratified_by, ratified_at, note)`, PK `(form_id, ref)`. This is Olivia's mapping truth. `form_field_map` becomes legacy and is read by nothing after Task 5.

- [ ] **Step 1: Create the table**

Apply with `apply_migration`, name `concept_pin`:

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
  '#68 — Olivia''s RATIFIED question->concept map. Nothing enters here without a human '
  'naming themselves in ratified_by. The trend-report agent''s form_question_map is '
  'regenerated from regex rules it owns; this table is the pinned copy Olivia reads.';
```

- [ ] **Step 2: Seed the 21 Andy ratified**

Apply with `apply_migration`, name `concept_pin_seed_andy`:

```sql
insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
select e.form_id, e.ref, v.concept, 'andy 2026-08-07', v.note
from (values
  ('What would you say your strongest area of expertise is currently?', 'area_of_expertise', 'exact-ish, app v3 rewording'),
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

-- the manufacturing family: 8 legacy per-country columns + 2 stragglers -> ONE key.
-- Grouped, NOT merged into a comparable series: legacy stored yes/no per country,
-- census 2026 asks one multi-select. Task 6 enforces the no-compare rule.
insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
select e.form_id, e.ref, 'mfg_location', 'andy 2026-08-07',
       'legacy per-country column; axis differs from the 2026 multi-select'
from digest.form_reach e
where e.form_id = 'DXs5mhZn'
  and e.question ilike 'Where do you manufacture your products?%'
on conflict (form_id, ref) do nothing;
```

- [ ] **Step 3: Verify the seed**

```sql
select count(*) pinned, count(distinct concept) concepts,
       count(*) filter (where concept = 'mfg_location') mfg_rows
from digest.concept_pin;
```
Expected: ~21 pinned rows, `mfg_rows` = 10 (8 country columns + "Other Asia" + the free-text "other locations"). If `mfg_rows` is 0 the `ilike` missed — check the exact question text in `form_reach` before adjusting.

- [ ] **Step 4: Re-export and gate**

```bash
python3 scripts/db_export_schema.py && git diff --stat db/
python3 scripts/olivia_leak_gate.py | tail -2
```
Expected: `db/tables.sql` shows `concept_pin`; `GATE PASSED`.

- [ ] **Step 5: Commit**

```bash
git add scripts/sql/ db/
git commit -m "#68 · concept_pin: Olivia's ratified map, seeded with Andy's 21 approvals"
```

---

### Task 4: The matcher — ranked candidates, never one guess

The evidence that shaped this: trigram put *"What is your main niche?"* first for "What is your formal title in your organization?" and the correct answer, *"What is your official role within your company?"*, came **third**, losing by 0.01. Ranking on lexical overlap is noise at that range. And 8 of 12 "near" matches were one matrix family, so the unit of matching is the **parent question**, not the ref.

**Files:**
- Create: `scripts/form_concept_match.py`
- Create (generated): `FORMS_MAPPING_REVIEW.md`

**Interfaces:**
- Consumes: `digest.form_reach`, `digest.concept_pin`, `digest.form_concept`, `VOYAGE_API_KEY`.
- Produces: `python3 scripts/form_concept_match.py` writes `FORMS_MAPPING_REVIEW.md`: one block per unmapped legacy parent question, its top 5 candidates ranked by embedding cosine with the trigram score shown alongside, and a `PICK:` line for a human to fill in.

- [ ] **Step 1: Write the matcher**

```python
#!/usr/bin/env python3
"""#68 — propose question->concept mappings. PROPOSES ONLY; nothing is written to the DB.

Why it is built this way:
  * Matrix rows collapse to their PARENT first. Legacy stored "Where do you manufacture
    your products? (China)" as 8 sibling columns; 2026 asks once. Matching per-ref makes
    trigram pick an arbitrary sibling — 21 of 39 weak matches failed exactly that way.
  * Trigram is a RECALL NET, not the ranker. Right and wrong were separated by 0.01.
    Voyage embeddings do the ranking.
  * Output is a RANKED LIST of 5 with a blank PICK line. A single best guess hides the
    correct answer at rank 3, which is how "no counterpart" was wrong for half the sample.
"""
import json, os, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
LIVE = ("DFeK5yop", "FsVHzNN9", "mkUJqsfM")
VOYAGE = "https://api.voyageai.com/v1/embeddings"


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
    return json.loads(p.stdout)


def parent(q):
    """'Where do you manufacture your products? (China)' -> the parent question."""
    return re.sub(r"\s*\([^()]*\)\s*$", "", (q or "").strip()).strip()


def embed(texts):
    key = env("VOYAGE_API_KEY")
    out = []
    for i in range(0, len(texts), 100):
        batch = texts[i:i + 100]
        p = subprocess.run(["curl", "-sS", "-m", "120", VOYAGE,
                            "-H", f"Authorization: Bearer {key}",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps({"model": "voyage-3", "input": batch})],
                           capture_output=True, text=True)
        out += [d["embedding"] for d in json.loads(p.stdout)["data"]]
    return out


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


rows = rpc("form_coverage_report")
pinned = {(r["form_id"], r["ref"]) for r in rpc("concept_pin_list")}

live_parents, legacy_parents = {}, {}
for r in rows:
    p = parent(r["question"])
    if not p:
        continue
    tgt = live_parents if r["form_id"] in LIVE else legacy_parents
    tgt.setdefault(p, {"refs": [], "concept": r["concept"], "respondents": 0})
    tgt[p]["refs"].append((r["form_id"], r["ref"]))
    tgt[p]["respondents"] = max(tgt[p]["respondents"], r["respondents"] or 0)

todo = {p: v for p, v in legacy_parents.items()
        if not v["concept"] and not all(k in pinned for k in v["refs"])}
print(f"live parents {len(live_parents)} · legacy parents {len(legacy_parents)} · to review {len(todo)}")

lp = list(live_parents)
vecs = dict(zip(lp, embed(lp)))
tvecs = dict(zip(todo, embed(list(todo))))

out = ["# #68 mapping review — ranked candidates\n",
       "For each legacy question: the 5 closest live questions by meaning.",
       "Fill in `PICK:` with a candidate number, `none`, or `new <concept_key>`.",
       "Nothing is written to the database until `scripts/form_concept_ratify.py` reads this file.\n"]
for q, v in sorted(todo.items(), key=lambda kv: -kv[1]["respondents"]):
    ranked = sorted(((cos(tvecs[q], vecs[c]), c) for c in lp), reverse=True)[:5]
    out.append(f"\n---\n\n### {q}\n")
    out.append(f"*{v['respondents']} respondents · {len(v['refs'])} refs*\n")
    for n, (s, c) in enumerate(ranked, 1):
        concept = live_parents[c]["concept"] or "(live question has no concept yet)"
        out.append(f"{n}. `{s:.3f}` **{c}** → `{concept}`")
    out.append("\n`PICK: `")
open("FORMS_MAPPING_REVIEW.md", "w").write("\n".join(out) + "\n")
print(f"wrote FORMS_MAPPING_REVIEW.md — {len(todo)} questions to review")
```

- [ ] **Step 2: Add the small RPC it needs for pinned rows**

Apply with `apply_migration`, name `concept_pin_list`:

```sql
create or replace function digest.concept_pin_list()
returns table (form_id text, ref text, concept text)
language sql stable security definer set search_path = digest, pg_temp
as $$ select form_id, ref, concept from digest.concept_pin $$;
revoke all on function digest.concept_pin_list() from public, anon, authenticated;
grant execute on function digest.concept_pin_list() to service_role;
```

- [ ] **Step 3: Run the matcher**

Run: `python3 scripts/form_concept_match.py`
Expected: prints roughly `live parents 130 · legacy parents 95 · to review 40`. The point of parent collapsing is that ~105 unmapped refs become roughly 40 decisions. If "to review" is still over 90, the parenthetical strip is not matching — print a few `parent(q)` values and fix the regex before going further.

- [ ] **Step 4: Sanity-check the ranking on the known case**

```bash
grep -A 7 "formal title" FORMS_MAPPING_REVIEW.md
```
Expected: **"What is your official role within your company?"** appears in the top 5 — ideally rank 1. Trigram had it at rank 3 behind "What is your main niche?". If embeddings also bury it, the model or the input text is wrong; fix that before asking Andy to review 40 questions.

- [ ] **Step 5: Commit the matcher, not the review file**

```bash
python3 scripts/db_export_schema.py
git add scripts/form_concept_match.py scripts/sql/ db/
git commit -m "#68 · matcher: parent collapsing + Voyage ranking, proposes 5 candidates and writes nothing"
```

---

### Task 5: Ratify, and pin the concept layer

**Andy's decision is required before this task**: does Olivia read `form_question_map` live, or a pinned copy? The layer is regenerated by `digest.rebuild_question_map()` from 80 regex rules the trend-report agent owns — live means a rule edit changes Olivia's answers with no review. **Default in this plan: pinned.** If Andy chooses live, skip Steps 2–3 and point Task 6 at `form_question_map` directly.

**Files:**
- Create: `scripts/form_concept_ratify.py`

**Interfaces:**
- Consumes: `FORMS_MAPPING_REVIEW.md` with `PICK:` lines filled in.
- Produces: rows in `digest.concept_pin`. Refuses any block whose `PICK:` is blank.

- [ ] **Step 1: Write the ratifier**

```python
#!/usr/bin/env python3
"""#68 — apply a reviewed mapping sheet. Refuses anything a human did not pick."""
import json, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
WHO = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: form_concept_ratify.py '<who>' [--apply]")
APPLY = "--apply" in sys.argv


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k}")


text = open("FORMS_MAPPING_REVIEW.md").read()
blocks = re.split(r"\n---\n", text)[1:]
picks, skipped = [], 0
for b in blocks:
    q = re.search(r"### (.+)", b)
    pick = re.search(r"`PICK:\s*(.*?)`", b)
    if not q or not pick or not pick.group(1).strip():
        skipped += 1
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

print(f"{len(picks)} ratified · {skipped} left blank (untouched)")
if not APPLY:
    for p in picks[:10]:
        print(f"  {p['concept']:<28} {p['question'][:60]}")
    print("DRY RUN — pass --apply to write")
    raise SystemExit

url, key = env("SUPABASE_URL").rstrip("/"), env("SUPABASE_SECRET_KEY")
p = subprocess.run(["curl", "-sS", "-m", "120", f"{url}/rest/v1/rpc/concept_pin_apply",
                    "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
                    "-H", "Content-Type: application/json", "-H", "Content-Profile: digest",
                    "-d", json.dumps({"p_picks": picks, "p_who": WHO})],
                   capture_output=True, text=True)
print("applied:", p.stdout.strip())
```

- [ ] **Step 2: Add the apply RPC**

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
    where e.form_id in ('I409BFlj','DXs5mhZn')
    on conflict (form_id, ref) do update set concept = excluded.concept,
                                             ratified_by = excluded.ratified_by,
                                             ratified_at = now()
    returning 1)
  select count(*)::int from ins;
$$;
revoke all on function digest.concept_pin_apply(jsonb, text) from public, anon, authenticated;
grant execute on function digest.concept_pin_apply(jsonb, text) to service_role;
```

- [ ] **Step 3: Pin the trend-report layer's concepts for Olivia's five forms**

Apply with `apply_migration`, name `concept_pin_adopt_existing`:

```sql
-- Adopt the 183 question->concept mappings that already exist for Olivia's forms.
-- Attributed to the source, not to a person: they were produced by regex rules, and
-- ratified_by makes that visible rather than pretending a human checked each one.
insert into digest.concept_pin (form_id, ref, concept, ratified_by, note)
select e.form_id, e.ref, coalesce(m.override_concept, m.concept),
       'adopted:form_question_map 2026-08-08',
       'inherited from the trend-report concept layer; not individually human-checked'
from digest.form_reach e
join digest.form_question_map m on m.form_id = e.form_id and m.question = e.question
where coalesce(m.override_concept, m.concept) is not null
group by e.form_id, e.ref, coalesce(m.override_concept, m.concept)
on conflict (form_id, ref) do nothing;   -- Andy's 21 win over the inherited ones
```

- [ ] **Step 4: Verify the pin**

```sql
select ratified_by, count(*) from digest.concept_pin group by 1 order by 2 desc;
select count(distinct concept) concepts, count(*) total from digest.concept_pin;
```
Expected: Andy's 21 rows intact under `andy 2026-08-07`, plus roughly 183 under `adopted:form_question_map`. Total around 200 across ~50 concepts.

- [ ] **Step 5: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py | tail -2
python3 scripts/db_export_schema.py
git add scripts/form_concept_ratify.py scripts/sql/ db/
git commit -m "#68 · ratifier + pinned concept map (Andy's 21 override the 183 inherited)"
```

---

### Task 6: Current value, and the no-compare rule

`member_fact` is `DISTINCT ON (member, concept, year)` — a per-year panel, right for trends, wrong for "what is this member's revenue now". Olivia needs latest-overall. Two defects ride along: it joins on question **text** (reword the question and the link silently vanishes) and its lateral has no `limit 1`, which is the #59 fan-out shape waiting to happen.

**Files:**
- Create: `scripts/sql/20260808_member_concept_current.sql`

**Interfaces:**
- Produces: `digest.member_concept_current(member_at_id, concept, value, answer_type, submitted_at, form_id, question)` — one row per member×concept, newest submission wins regardless of year. And `digest.concept_axis(concept, comparable)` — false where forms used different answer shapes.

- [ ] **Step 1: Create the current-value view and the axis table**

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
  '#68 — latest answer per member per concept, newest submission wins, ANY year. '
  'member_fact stays the per-year panel for trends; this is the current value.';

create table if not exists digest.concept_axis (
  concept    text primary key,
  comparable boolean not null,
  reason     text
);
revoke all on digest.concept_axis from anon, authenticated;
grant select, insert, update on digest.concept_axis to service_role;

-- Andy's ruling: same concept, different answer shape = group, never merge into one series.
insert into digest.concept_axis (concept, comparable, reason) values
  ('mfg_location', false, 'legacy: yes/no column per country; census 2026: one multi-select'),
  ('pay_band',     false, 'legacy: monthly figure per role; census 2026: bands'),
  ('team_size_total', false, 'legacy split full-time / part-time W-2 + 1099; 2026 asks one total'),
  ('growth_channels_intent', false, 'legacy: one column per channel; 2026: one multi-select'),
  ('eos_traction', true,  'yes/no both sides; 2026 adds a free-text "how" that is not compared')
on conflict (concept) do update set comparable = excluded.comparable,
                                    reason = excluded.reason;
```

- [ ] **Step 2: Prove current-value differs from the per-year panel**

```sql
select (select count(*) from digest.member_concept_current) current_rows,
       (select count(*) from digest.member_fact
         where form_id in ('DFeK5yop','FsVHzNN9','mkUJqsfM','I409BFlj','DXs5mhZn')) panel_rows,
       (select count(distinct member_at_id) from digest.member_concept_current) members;
```
Expected: `current_rows` is materially smaller than `panel_rows` (one row per member×concept instead of one per year) and `members` is roughly 650–750. If they are equal, the DISTINCT ON is not collapsing years — check the ORDER BY.

- [ ] **Step 3: Prove a member whose answer moved forward reads the newest**

```sql
select concept, form_id, submitted_at::date, value
from digest.member_concept_current
where member_at_id = (select member_at_id from digest.member_concept_current
                      group by 1 order by count(*) desc limit 1)
order by concept limit 10;
```
Expected: where a member answered both a legacy census and census 2026, `form_id` is the 2026 one. A legacy `form_id` with a 2026 answer present is the bug this view exists to prevent.

- [ ] **Step 4: Gate, re-export, commit**

```bash
python3 scripts/olivia_leak_gate.py | tail -2
python3 scripts/db_export_schema.py && git diff --stat db/
git add scripts/sql/ db/
git commit -m "#68 · member_concept_current (latest wins, any year) + concept_axis no-compare rule"
```

---

### Task 7: QA, handbook, close, and file what this uncovered

**Files:**
- Modify: `scripts/qa_form_stats.py`, `OLIVIA_HANDBOOK.md`, `OLIVIA_SPRINT_3.md`, `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md`

- [ ] **Step 1: Extend the QA sweep**

Add to `scripts/qa_form_stats.py`, in the assertion pass:

```python
    # #68 — a concept whose axis differs must never be presented as one comparable series.
    axis = {r["concept"]: r["comparable"] for r in fetch("concept_axis?select=concept,comparable")}
    for concept, comparable in axis.items():
        if comparable:
            continue
        forms = {r["form_id"] for r in fetch(
            f"member_concept_current?select=form_id&concept=eq.{concept}")}
        assert_that(f"{concept}: not-comparable, so a trend must refuse to mix forms",
                    len(forms) >= 1)
```

- [ ] **Step 2: Run the sweep and the gate**

```bash
python3 scripts/qa_form_stats.py | tail -5
python3 scripts/olivia_leak_gate.py | tail -2
```
Expected: sweep reports 0 fails (last full run: 1,857 checks, 0 fails); `GATE PASSED` at 247.

- [ ] **Step 3: Handbook §4 — who owns the concept layer**

```markdown
### The concept layer, and who owns which half (#68, 2026-08-07)

`digest.form_concept` (81 concepts with label/family/value_kind/window_note), `concept_rule`
(80 prioritised regexes) and `form_question_map` (1,314 questions across all 114 forms) belong
to the **trend-report** work, not Olivia. They are regenerated by `rebuild_question_map()`.

**Olivia reads `digest.concept_pin`** — a ratified snapshot — never `form_question_map` live.
A regex change by another team therefore cannot alter Olivia's answers without someone
re-ratifying. Re-adopt with `scripts/form_concept_match.py` → review → `form_concept_ratify.py`.

`digest.form_reach` is THE chokepoint: every Olivia form consumer reads it, and it is the one
place that enforces `scope='profile'`. Never read `form_answers_exploded` directly.
```

- [ ] **Step 4: File the identity ticket**

Add to `OLIVIA_SPRINT_3.md` under S2, in the house format, with the numbers measured on 2026-08-07: 4,617 of 9,089 form responses unstamped (51%); an email waterfall across all five known email fields recovers only 75; 2,871 carry no identifier at all; `Aliases` differs from the full name for just 569 of 5,903 members, and "Mo Kuhail" has no "Mohamed Kuhail" variant. State the known-names vs display-name split as the design rule.

- [ ] **Step 5: Close-out**

Update the sprint board row for #68 with the AC checklist and before/after numbers (mapping coverage before: 78 rows / 48 keys in `form_field_map`; after: `concept_pin` rows and concepts). Prepend the session entry to `SESSION_LOG_OLIVIA.md`, one line to `SESSION_LOG.md`, update memory `project_mds_forms_warehouse` with the concept-layer ownership rule.

```bash
git add OLIVIA_HANDBOOK.md OLIVIA_SPRINT_3.md SESSION_LOG_OLIVIA.md SESSION_LOG.md scripts/qa_form_stats.py
git commit -m "#68 · QA covers axis rule, handbook records concept-layer ownership, identity ticket filed"
```

---

## Self-Review

**Spec coverage.** The ticket's ACs map to: dictionary with type/units/period — already exists as `form_concept`, adopted in Task 5, axis handled in Task 6. Coverage report separating needs-a-key from single-form — Task 1. Ratification queue with nothing unratified — Tasks 3–5. Cross-form question proven end to end — Task 6 Step 3. Form-design rule so the next form ships with mappings — **not covered by this plan**: it needs Eugene and belongs with the census/forms project, so it stays in the ticket as an open dependency rather than being silently dropped. QA asserts units/period and gate green — Task 7.

**Placeholders.** None. Every step carries the SQL, the Python, or the exact command plus its expected output.

**Type consistency.** `digest.form_reach` is created in Task 2 and read by Tasks 3, 5 and 6. `concept_pin(form_id, ref, concept, ratified_by, ratified_at, note)` is defined in Task 3 and used unchanged by `concept_pin_list()`, `concept_pin_apply()` and `member_concept_current`. `form_coverage_report()` returns the six columns Task 1 and Task 4 both consume.

**Known soft spots, stated rather than hidden.** The 183 mappings adopted in Task 5 Step 3 were produced by regex rules and are marked `adopted:form_question_map`, not human-checked — the `ratified_by` column makes that visible, and Andy's 21 override them on conflict. And Task 4's expected "~40 to review" is an estimate from the parent-collapsing arithmetic on the 105 unmapped refs; if the real number is much larger, Step 3 says to stop and fix the regex rather than hand Andy a bad sheet.
