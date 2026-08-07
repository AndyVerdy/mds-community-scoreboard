# #65 · The SQL Layer Into Version Control — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every function, view, trigger, policy and grant in the `digest` schema exists as a file in git, byte-matched to the live database, with a scheduled check that fails when the two diverge.

**Architecture:** One read-only Postgres function (`digest.schema_source()`) hands the DDL text of every `digest` object to a Python exporter over PostgREST — the only database path this machine has (no psql, no psycopg, no DB password, no Management-API PAT). The exporter writes a deterministic file tree under `db/`; the same script in `--check` mode re-reads the live database and exits 1 on any difference, so drift is caught by a schedule rather than by an incident. This is an **export**, not a deployment: nothing flows repo→DB in this plan, and no existing database object is modified.

**Tech Stack:** Supabase Postgres 15 (project `nadtudwuwjhckotrngzn`, schema `digest`) · PostgREST with `SUPABASE_SECRET_KEY` and `Content-Profile: digest` · Python 3 stdlib + `curl` subprocess (the house pattern) · launchd for scheduling · Slack bot token for alerting · `scripts/olivia_leak_gate.py` as the safety gate.

## Global Constraints

- **Gate GREEN before and after every database step.** `python3 scripts/olivia_leak_gate.py` — baseline is **243 checks, 0 failures, exit 0** (verified 2026-08-07). A red gate stops the task.
- **Read-only against the database.** The only DDL in this plan is `create or replace function digest.schema_source()` (adds one object) and a throwaway `digest.drift_canary()` created and dropped inside Task 3. **No existing function, view, table, trigger or grant is altered.**
- **No member data leaves the database.** `schema_source()` returns DDL text only. Any exported file containing a phone number, name, email or answer text is a defect, not a quirk.
- **launchd runs `/usr/bin/python3`, which has no `certifi`.** All HTTPS goes through `curl` subprocesses — never `urllib` with a `CERT_NONE` fallback. (2026-08-07 Critical: the Zoom job silently disabled TLS verification exactly this way and shipped a client secret over an unverified connection.)
- **`db/` is GENERATED.** Never hand-edit a file under `db/`; change the database, re-export, review the diff, commit.
- **Every completion claim cites live evidence** — an exit code, a row count, a gate line, a Slack message id. Never "should work".
- **PostgREST caps a response at 1000 rows.** The export is ~117 rows today; if the object count ever crosses 1000 the exporter must paginate. Asserted explicitly in Task 2.

---

## File Structure

| File | Responsibility | State |
|---|---|---|
| `scripts/sql/20260807_schema_source_introspection.sql` | The one new DB object: `digest.schema_source()` — returns `(kind, obj_name, file_name, definition)` for every function, view, matview, and the aggregated triggers / policies / grants / rls / tables catalogs. Revoked from public/anon/authenticated, granted to `service_role`. | **Written, not applied** |
| `scripts/db_export_schema.py` | Export and drift check. `--check` compares the live database to `db/` and exits 1 on difference. Gains `--alert` in Task 4. | **Written, not run** |
| `db/functions/*.sql` | One file per function, exact `pg_get_functiondef` output under a generated-file header. ~103 files. | Created in Task 2 |
| `db/views/*.sql` | One file per view / materialized view. 8 files. | Created in Task 2 |
| `db/triggers.sql`, `db/policies.sql`, `db/grants.sql`, `db/rls.sql`, `db/tables.sql` | The catalogs: 18 triggers, 0 policies (the zero is itself the record), all grants, the RLS flag per table, and column/constraint/index DDL as the restore path. | Created in Task 2 |
| `db/README.md` | Why the tree exists, that it is generated, how to re-export, and the one rule (never hand-edit). | Created in Task 2 |
| `~/Library/LaunchAgents/com.mds.db.drift.plist` | Daily 05:40 drift check. Mirrors `com.mds.zoom.weekly.plist`. | Created in Task 4 |
| `scripts/db_drift.log` | The job's log — the artefact that proves it ran. | Created in Task 4 |
| `scripts/olivia_leak_gate.py` | Extended with two checks covering the new surface. | Modified in Task 5 |
| `OLIVIA_HANDBOOK.md` | §12 gains the tier ruling and its two accepted exceptions; §10 gains `db/`; §8 gains the re-export runbook. | Modified in Task 6 |
| `OLIVIA_SPRINT_3.md`, `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md`, memory | Close-out. | Modified in Task 7 |

**Out of scope, deliberately:** step 3 of the ticket's remediation — making changes flow **repo→DB** (apply-from-file). It is the only step that can break production, the ticket gates it on "after 1+2 are green and stable", and it needs its own proof plan and rehearsed rollback. Task 7 records it as the named follow-up for Andy to rule on.

---

### Task 1: Apply the introspection function and prove it is closed to anon

**Files:**
- Apply: `scripts/sql/20260807_schema_source_introspection.sql` (already written)
- Test: live probe with the anon key + the service key

**Interfaces:**
- Consumes: nothing.
- Produces: `digest.schema_source()` → `setof (kind text, obj_name text, file_name text, definition text)`. `kind` ∈ `function | view | matview | catalog`. Callable by `service_role` only. Task 2 and Task 3 depend on this signature exactly.

- [ ] **Step 1: Baseline the gate before touching the database**

```bash
python3 scripts/olivia_leak_gate.py | tail -3
```

Expected: last line `GATE PASSED — retrieval refuses everything it must refuse.` If it does not say that, **stop** — do not apply anything to a database whose gate is red.

- [ ] **Step 2: Apply the migration**

Apply `scripts/sql/20260807_schema_source_introspection.sql` with the Supabase MCP `apply_migration` tool, name `schema_source_introspection`. (There is no psql on this machine; MCP is how every migration this sprint was applied.)

Expected: success, no rows returned.

- [ ] **Step 3: Prove the service key can call it, and that the counts match the catalog**

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/schema_source" -H "apikey: $KEY" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -H "Content-Profile: digest" -d '{}' | python3 -c "import json,sys,collections; r=json.load(sys.stdin); print(collections.Counter(x['kind'] for x in r)); print('rows', len(r))"
```

Expected: `Counter({'function': 104, 'catalog': 5, 'view': 6, 'matview': 2})` and `rows 117` — 104 because `schema_source` itself is now a function. The view/matview split may differ; **function count must be 103 + 1**. If `function` is not 104, the schema changed under us — re-check `pg_proc` before continuing.

- [ ] **Step 4: Prove anon cannot call it**

```bash
python3 - <<'PY'
import json,subprocess
ANON=open('scripts/olivia_leak_gate.py').read().split('ANON_KEY = (')[1].split(')')[0]
key=''.join(p.strip().strip('"') for p in ANON.split('\n'))
url=[l.split('=',1)[1].strip() for l in open('/Users/Born/mds-digest-web/.env.local') if l.startswith('SUPABASE_URL=')][0].rstrip('/')
p=subprocess.run(['curl','-s','-o','/dev/null','-w','%{http_code}','-X','POST',f'{url}/rest/v1/rpc/schema_source','-H',f'apikey: {key}','-H',f'Authorization: Bearer {key}','-H','Content-Type: application/json','-H','Content-Profile: digest','-d','{}'],capture_output=True,text=True)
print('anon status', p.stdout)
PY
```

Expected: `anon status 404` (PostgREST hides functions the role cannot execute) or `401`/`403`. **Anything in the 2xx range is a leak — revoke and stop.**

- [ ] **Step 5: Gate green after the change**

```bash
python3 scripts/olivia_leak_gate.py | tail -3
```

Expected: `GATE PASSED`.

- [ ] **Step 6: Commit**

```bash
git add scripts/sql/20260807_schema_source_introspection.sql scripts/db_export_schema.py
git commit -m "#65 · read-only schema_source() introspection RPC + exporter (not yet run)"
```

---

### Task 2: Baseline export — the whole SQL layer becomes files

**Files:**
- Create: `db/functions/*.sql`, `db/views/*.sql`, `db/triggers.sql`, `db/policies.sql`, `db/grants.sql`, `db/rls.sql`, `db/tables.sql`
- Create: `db/README.md`
- Run: `scripts/db_export_schema.py`

**Interfaces:**
- Consumes: `digest.schema_source()` from Task 1.
- Produces: the `db/` tree. Every file is `-- GENERATED by scripts/db_export_schema.py from the live database. Do not hand-edit.\n` + the object's DDL + a single trailing newline. Task 3 asserts on exactly this shape.

- [ ] **Step 1: Run the export**

```bash
python3 scripts/db_export_schema.py
```

Expected: `exported 117 files to db/ (104 functions, 8 views)`.

- [ ] **Step 2: Confirm the tree, and that nothing was truncated by the 1000-row cap**

```bash
find db -name '*.sql' | wc -l && ls db/functions | wc -l && ls db/views | wc -l && du -sh db
```

Expected: 117 total, 104 functions, 8 views, ~300 KB. If the total were exactly 1000 the response hit PostgREST's cap and the exporter needs pagination — it is not near it today.

- [ ] **Step 3: Prove byte-match independently of the writer**

`--check` compares the live DB to the files, but it rebuilds bodies with the same code that wrote them. Verify three functions by a different route — md5 computed in Postgres versus md5 of the bytes on disk.

Run this in the Supabase MCP `execute_sql`:

```sql
select p.proname,
       md5(rtrim(pg_get_functiondef(p.oid), E'\n') || E'\n') as db_md5
from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'digest'
  and p.proname in ('content_search_v2', 'member_card_v2', 'form_stats')
order by 1;
```

Then on disk (the header line is ours, so skip it):

```bash
for f in content_search_v2 member_card_v2 form_stats; do printf '%s ' "$f"; tail -n +2 "db/functions/$f.sql" | md5; done
```

Expected: the three pairs match exactly. A mismatch means the exporter is mangling bytes — fix it before committing a baseline that lies.

- [ ] **Step 4: Prove no member data rode along**

```bash
grep -rInE '\+?[0-9]{10,15}' db/ | grep -v -E 'md5|oid|[0-9]{4}-[0-9]{2}-[0-9]{2}' | head
grep -rIln '@mds.co\|@gmail\|whatsapp.net' db/ | head
```

Expected: no output from either. A hit means a function body has a hardcoded phone/email — surface it, do not silently commit it.

- [ ] **Step 5: Write `db/README.md`**

```markdown
# `db/` — the SQL layer, in git

**Generated. Never hand-edit anything in this tree.**

103+ Postgres functions run Olivia's retrieval, her access gating, the stats and the
small-cell suppression. Until 2026-08-07 they existed only inside the live Supabase
database: no diff, no review, no history, no restore path independent of the DB. This
tree is the second copy (#65).

| Path | What |
|---|---|
| `functions/` | one file per `digest` function, exact `pg_get_functiondef` output |
| `views/` | views and materialized views |
| `triggers.sql` | every trigger, `pg_get_triggerdef` |
| `policies.sql` | every RLS policy — currently none, and that zero is the record |
| `grants.sql` | who may execute / read / write what: the security boundary |
| `rls.sql` | the row-level-security flag per table |
| `tables.sql` | columns, constraints and indexes — the restore path |

## The workflow

Changes still flow **DB → repo**. Apply your migration, then:

    python3 scripts/db_export_schema.py        # re-export
    git diff db/                               # review the real diff
    git add db && git commit

To ask whether the repo and the live database still agree:

    python3 scripts/db_export_schema.py --check   # exit 0 = in sync, exit 1 = drift

`com.mds.db.drift` runs that check daily at 05:40 and alerts Slack on drift
(log: `scripts/db_drift.log`).

**Applying files back to the database (repo → DB) is NOT wired up** — it is the only
direction that can break production and needs its own proof plan. Do not improvise it.
```

- [ ] **Step 6: Confirm git will actually track the tree, then commit**

```bash
git check-ignore -v db/ || echo "db/ is tracked"
git add db && git status --short db | head -5 && git status --short db | wc -l
git commit -m "#65 · baseline: the entire digest SQL layer exported to db/ (104 functions, 8 views, 18 triggers, grants, rls, tables)"
```

Expected: `db/ is tracked`, ~118 added files, commit succeeds.

---

### Task 3: Prove the drift check fails on an injected difference — both directions

A check that has never failed is not a check. This task proves it catches a repo-side edit **and** a database-side change.

**Files:**
- Run: `scripts/db_export_schema.py --check`
- Temporary: `digest.drift_canary()` — created and dropped inside this task

**Interfaces:**
- Consumes: the `db/` tree from Task 2 and `digest.schema_source()` from Task 1.
- Produces: nothing durable. Evidence only.

- [ ] **Step 1: Green baseline**

```bash
python3 scripts/db_export_schema.py --check; echo "exit=$?"
```

Expected: `DB IN SYNC — 117 files byte-match the live database.` and `exit=0`.

- [ ] **Step 2: Inject a repo-side difference (the "someone hand-edited a file" case)**

```bash
printf '\n-- injected drift proof\n' >> db/functions/member_card_v2.sql
python3 scripts/db_export_schema.py --check; echo "exit=$?"
```

Expected: `DIFFERS  functions/member_card_v2.sql`, a unified diff showing the injected line, and `exit=1`.

- [ ] **Step 3: Restore and confirm green again**

```bash
git checkout db/functions/member_card_v2.sql
python3 scripts/db_export_schema.py --check; echo "exit=$?"
```

Expected: `DB IN SYNC` and `exit=0`.

- [ ] **Step 4: Inject a database-side difference (the real failure mode — an out-of-band `create or replace`)**

Apply with the Supabase MCP `execute_sql`:

```sql
create or replace function digest.drift_canary()
returns text language sql immutable
as $$ select '#65 drift-check proof — safe to drop'::text $$;
revoke all on function digest.drift_canary() from public;
```

Then:

```bash
python3 scripts/db_export_schema.py --check; echo "exit=$?"
```

Expected: `MISSING FROM GIT  functions/drift_canary.sql`, `DIFFERS  grants.sql` (the new grant row), and `exit=1`. **This is the exact class that hid `zoom_resolve_attendance` — a function that existed only in the live DB.**

- [ ] **Step 5: Drop the canary and confirm the check goes green**

Apply with the Supabase MCP `execute_sql`:

```sql
drop function digest.drift_canary();
```

Then:

```bash
python3 scripts/db_export_schema.py --check; echo "exit=$?"
git status --short db | wc -l
```

Expected: `DB IN SYNC`, `exit=0`, and `0` — the working tree is clean, the canary left nothing behind.

- [ ] **Step 6: Gate green after the canary round-trip**

```bash
python3 scripts/olivia_leak_gate.py | tail -3
```

Expected: `GATE PASSED`.

---

### Task 4: Schedule the check and make drift shout

**Files:**
- Modify: `scripts/db_export_schema.py` (add `--alert`)
- Create: `~/Library/LaunchAgents/com.mds.db.drift.plist`
- Create: `scripts/db_drift.log` (by running it)

**Interfaces:**
- Consumes: `--check` behaviour from Task 3.
- Produces: `--alert` — with `--check`, posts the drift summary to Slack `C0AQ8USNQK0` using `CENTURION_SLACK_BOT_TOKEN`; silent when in sync. `--alert --test` forces one message to prove delivery.

- [ ] **Step 1: Add the alert path**

In `scripts/db_export_schema.py`, add after `load_env()`:

```python
def slack(text):
    """Same channel and token as the alarm watchdog — one place Andy already watches."""
    tok = None
    for line in open(ENV_PATH):
        if line.startswith("CENTURION_SLACK_BOT_TOKEN="):
            tok = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not tok:
        print("no CENTURION_SLACK_BOT_TOKEN — drift not alerted")
        return
    subprocess.run(["curl", "-sS", "-X", "POST", "https://slack.com/api/chat.postMessage",
                    "-H", f"Authorization: Bearer {tok}",
                    "-H", "Content-Type: application/json", "--max-time", "20",
                    "--data-binary", json.dumps({"channel": "C0AQ8USNQK0", "text": text})],
                   capture_output=True, text=True)
```

Add the flags in `main()`:

```python
    ap.add_argument("--alert", action="store_true",
                    help="with --check: post drift to Slack (silent when in sync)")
    ap.add_argument("--test", action="store_true",
                    help="with --alert: force one message to prove delivery")
```

And replace the drift-summary tail of `main()` with:

```python
    summary = (f"DB DRIFT — {len(missing)} missing, {len(extra)} stale, "
               f"{len(changed)} changed. Run scripts/db_export_schema.py to re-export, "
               f"review the diff, and commit.")
    print("\n" + summary)
    if args.alert:
        slack(":rotating_light: *Olivia SQL layer drift* (#65)\n" + summary + "\n"
              + "\n".join(f"• {k}" for k in (missing + extra + changed)[:12]))
    return 1
```

…and immediately before `return 0` in the in-sync branch:

```python
        if args.alert and args.test:
            slack(":white_check_mark: #65 drift check — forced test message, "
                  f"{len(live)} files in sync. Delivery proven.")
```

- [ ] **Step 2: Prove Slack delivery before trusting the silence**

```bash
python3 scripts/db_export_schema.py --check --alert --test; echo "exit=$?"
```

Expected: `DB IN SYNC`, `exit=0`, **and the message visible in Slack `C0AQ8USNQK0`**. A silent alerting path is worse than none — confirm the message landed, do not infer it from exit 0.

- [ ] **Step 3: Write the launchd job**

Create `~/Library/LaunchAgents/com.mds.db.drift.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.mds.db.drift</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/Born/Scorecard/scripts/db_export_schema.py</string>
    <string>--check</string>
    <string>--alert</string>
  </array>
  <key>WorkingDirectory</key><string>/Users/Born/Scorecard</string>
  <!-- Daily 05:40: after the nightly derivations, before the working day. An out-of-band
       `create or replace` is caught within a day, which is the whole point of #65. -->
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>5</integer><key>Minute</key><integer>40</integer></dict>
  <key>StandardOutPath</key><string>/Users/Born/Scorecard/scripts/db_drift.log</string>
  <key>StandardErrorPath</key><string>/Users/Born/Scorecard/scripts/db_drift.log</string>
</dict>
</plist>
```

- [ ] **Step 4: Load it and force a real run through launchd (not through your shell)**

```bash
launchctl unload ~/Library/LaunchAgents/com.mds.db.drift.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.mds.db.drift.plist
launchctl start com.mds.db.drift
sleep 25 && cat scripts/db_drift.log
```

Expected: the log contains `DB IN SYNC — 117 files byte-match the live database.` This proves it under `/usr/bin/python3` — the interpreter that has no `certifi`, where the Zoom job's TLS bug lived. If the log shows an SSL error, the script is using something other than `curl` for HTTPS; fix that, do not disable verification.

- [ ] **Step 5: Commit**

```bash
cp ~/Library/LaunchAgents/com.mds.db.drift.plist launchd/com.mds.db.drift.plist 2>/dev/null || true
git add scripts/db_export_schema.py db/README.md
git commit -m "#65 · daily drift check on launchd + Slack alert, delivery proven"
```

---

### Task 5: The gate covers the new surface

Last session's code review found the Zoom work had shipped with **zero gate coverage of its new surfaces**. The same must not happen here: the gate is what proves, every run, that the introspection door stays shut.

**Files:**
- Modify: `scripts/olivia_leak_gate.py`

**Interfaces:**
- Consumes: `digest.schema_source()`.
- Produces: two additional gate checks. Gate count goes 243 → 245.

- [ ] **Step 1: Add the checks**

Find the section that runs the anon-denial checks (search for `anon key denied on form_stats`) and add alongside it:

```python
    # #65 — the schema-source door: DDL text only, and only for the service key.
    st, _ = rpc("schema_source", {}, ANON_KEY)
    check("anon key denied on schema_source (#65)", st in (401, 403, 404), f"status {st}")

    st, rows = rpc("schema_source", {}, key)
    blob = json.dumps(rows) if st == 200 else ""
    check("schema_source returns DDL only — no member phone numbers (#65)",
          st == 200 and not re.search(r'"\+?\d{10,15}"', blob), f"status {st}")
```

If `re` is not already imported at the top of the file, add `import re`.

- [ ] **Step 2: Run the gate**

```bash
python3 scripts/olivia_leak_gate.py | grep -E "#65|GATE|FAIL"
```

Expected: both `#65` lines show `PASS`, no `FAIL` lines, and `GATE PASSED`.

- [ ] **Step 3: Confirm the count moved and nothing else broke**

```bash
python3 scripts/olivia_leak_gate.py | grep -c "  PASS"
python3 scripts/olivia_leak_gate.py | grep -c "  FAIL"
```

Expected: `245` and `0`.

- [ ] **Step 4: Commit**

```bash
git add scripts/olivia_leak_gate.py
git commit -m "#65 · gate covers the schema_source surface (243 -> 245 checks)"
```

---

### Task 6: Write the architecture ruling down

The ticket carries an architecture ruling that currently exists only in a session log. It belongs in the handbook, because the next person to ask "why is all this logic in Postgres?" will otherwise re-litigate it.

**Files:**
- Modify: `OLIVIA_HANDBOOK.md` — §12 (Decisions and why), §10 (Repository map), §8 (Runbooks)

**Interfaces:** documentation only.

- [ ] **Step 1: Add the tier ruling to §12 "Decisions and why"**

```markdown
### The data-access tier lives in Postgres — and that is deliberate (2026-08-07, #65)

Data access and access control belong in Postgres because it is the last hop before the
data, and **four consumers share it**: n8n, the Python scripts, the GitHub Actions and
digest-web. Moving the gate into one application leaves the other three unguarded; moving
retrieval out means pulling 38k rows over the wire and losing HNSW-in-query. So the ~103
functions are not misplaced logic — they are the boundary.

What #65 fixed was not the placement but the **source of truth**: the functions now exist
as files in `db/`, exported from the live database, with a daily drift check. Changes flow
DB → repo; repo → DB is not wired up.

**Two accepted tier exceptions, named rather than pretended away:**
- `olivia_alarm_fire` posts to Slack from inside Postgres (via `pg_net`). That is on
  purpose — the alarm must survive n8n being the thing that is down.
- `member_event_url` does URL/presentation shaping in SQL. A genuine violation, small,
  and cheaper where it is than duplicated across four consumers.
```

- [ ] **Step 2: Add `db/` to the §10 repository map** — one row, in the table's existing style:

```markdown
| `db/` | **The SQL layer in git (#65)** — generated. 104 functions, 8 views, triggers, grants, RLS and table DDL, byte-matched to the live database. Never hand-edit; re-export with `scripts/db_export_schema.py`. |
```

- [ ] **Step 3: Add the runbook to §8**

```markdown
### After ANY migration: re-export the SQL layer (#65)

    python3 scripts/db_export_schema.py     # DB -> files
    git diff db/                            # this is your code review
    git add db && git commit

`com.mds.db.drift` (daily 05:40) runs `--check --alert` and shouts in Slack when the repo
and the live database disagree. Log: `scripts/db_drift.log`. A drift alert means someone
changed the database out of band — re-export, read the diff, and find out who and why
before committing it.
```

- [ ] **Step 4: Fix the stale count in §4 while you are here** — the handbook says "43 tables, ~75 functions"; the live count is 104. Update that cell.

- [ ] **Step 5: Commit**

```bash
git add OLIVIA_HANDBOOK.md
git commit -m "#65 · handbook: the Postgres-tier ruling, its two accepted exceptions, the db/ tree and the re-export runbook"
```

---

### Task 7: Close #65 with evidence

**Files:**
- Modify: `OLIVIA_SPRINT_3.md` (at-a-glance row + move #65 to CLOSED with evidence)
- Modify: `SESSION_LOG_OLIVIA.md` (full entry, prepended), `SESSION_LOG.md` (one index line)
- Modify: memory `project_mds_olivia_pilot.md`

**Interfaces:** documentation only.

- [ ] **Step 1: Update the at-a-glance row**

```markdown
| **#65** | 🚨 SQL functions exist ONLY in the live DB — no file in git | 🔴 S1 | M | n/a (SQL) | ✅ **CLOSED** — 117 files in `db/`, daily drift check proven |
```

- [ ] **Step 2: Move the #65 block to the CLOSED section at the bottom**, keeping its story and ACs, and append the close in Andy's required format — short results, an AC checklist marked met/not, and before/after numbers:

```markdown
**CLOSED 2026-08-07** — 0 → 117 files. Every `digest` function (104), view (8), trigger (18),
grant, RLS flag and table DDL now exists in `db/`, byte-matched to the live database.

| AC | Verdict |
|---|---|
| Every function, view and policy is a file in git, byte-matched | ✅ 117 files; md5 spot-check on 3 functions matched Postgres exactly |
| CI drift check demonstrably fails on an injected difference | ✅ both directions — repo edit → `DIFFERS`, exit 1; live `drift_canary()` → `MISSING FROM GIT`, exit 1; green again after each |
| Tier rule + exceptions in the handbook | ✅ §12, with `olivia_alarm_fire` and `member_event_url` named as accepted exceptions |
| Gate GREEN before and after; no RPC behaviour changed | ✅ 243 → 245 checks, exit 0; the only DDL was one added read-only function |

**Before/after:** source files 0 → 117 · restore path none → `db/` · out-of-band change
detected never → within 24h (`com.mds.db.drift`, 05:40 daily, Slack-alerting) · gate 243 → 245.

**Remaining, for Andy to rule:** the repo→DB direction (apply-from-file). It is the only
step that can break production, so it stays out until it has its own proof plan and a
rehearsed rollback.
```

- [ ] **Step 3: Prepend the session entry to `SESSION_LOG_OLIVIA.md`** and add ONE line to the `SESSION_LOG.md` index — which project, what shipped (commit hashes), what was verified (exit codes, gate count, Slack delivery), what is next.

- [ ] **Step 4: Update memory** `project_mds_olivia_pilot.md` — one clause: the SQL layer is in `db/`, generated, drift-checked daily, and re-exporting after a migration is now part of the ritual.

- [ ] **Step 5: Commit**

```bash
git add OLIVIA_SPRINT_3.md SESSION_LOG_OLIVIA.md SESSION_LOG.md
git commit -m "#65 CLOSED — the SQL layer is in git: 117 files, drift check proven both directions, gate 245"
```

---

## Self-Review

**Spec coverage** — the ticket's four ACs map to Task 2 (files byte-matched), Task 3 (drift check proven on an injected difference, both directions), Task 6 (tier rule + exceptions in the handbook), and Tasks 1/3/5 (gate green before and after, no RPC behaviour changed). The ticket's remediation steps 1 and 2 are Tasks 1–4; step 3 (repo→DB) is explicitly deferred and recorded in Task 7; step 4 (handbook) is Task 6.

**Placeholders** — none. Every step carries the exact command, the exact SQL, or the exact text to write, plus the expected output.

**Type consistency** — `digest.schema_source()` returns `(kind, obj_name, file_name, definition)` in Task 1; `scripts/db_export_schema.py` reads exactly those four keys in `expected_tree()`; `--check`, `--alert` and `--test` are the only flags, defined in Task 4 and used consistently in Tasks 3, 4 and the launchd plist.

**One known soft spot, stated rather than hidden:** the export's file bodies and the `--check` comparison are produced by the same code, so `--check` alone proves consistency, not correctness. Task 2 Step 3 closes that with an md5 comparison computed inside Postgres against the bytes on disk — a genuinely independent path.
