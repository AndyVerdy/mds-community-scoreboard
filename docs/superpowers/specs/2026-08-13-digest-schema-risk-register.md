# Risk register — digest schema rework, all five phases

**Date:** 2026-08-13 · **Companion to:** `2026-08-13-digest-schema-architecture-design.md` and the five phase plans

Written after Andy asked whether risks had been evaluated per phase. They had not — the design doc
carried a Low/Medium/High label per work item and one rollback procedure across four plans. This
document is the actual evaluation, and writing it changed the plan: see §2, which is a sequencing
error that would have made the system worse mid-flight.

## 0. Live context that sets the stakes

- **The member portal is in active use.** 102 sessions, 55 distinct members, most recent
  2026-08-13 14:37 UTC. This is not a quiet system being renovated at night.
- **Olivia is in production** on prod `e988a6a3`, answering real members over WhatsApp.
- **`service_role` carries `BYPASSRLS`.** `anon` and `authenticated` cannot log in at all
  (`rolcanlogin = false`); they are switched into by `authenticator`. Everything in our stack runs
  as `service_role`.
- **Working hours matter.** Any step that can fail a live write should not run while members are
  active.

---

## 1. The three risks that actually matter

Ranked by expected harm, not by phase order.

| # | Risk | Phase | Worst case | Why it is ranked here |
|---|---|---|---|---|
| **R1** | **A member is shown content they should not see** | 4 | Privacy breach, unrecoverable — you cannot un-show something | The only risk whose damage cannot be rolled back |
| **R2** | **A live loader starts failing and nobody notices** | 3 | Silent data loss for days; form submissions, event rosters or WA messages stop landing | Detection today is weak — this is why Phase 1 Task 2 must come first |
| **R3** | **The assistant answers worse than before** | 2, 3 | Members get degraded answers; trust cost, recoverable | Most likely to occur; least permanent |

Everything else is a subset of these or is cosmetic.

---

## 2. Sequencing error found while writing this — Phase 2 must be reordered

**As written, Phase 2 creates a window where the system is worse than today.**

Task 3 backfills the 13,450 WhatsApp rows to `at_member_id`. Task 4 repoints the consumers to join
`member_profiles`. Between those two commits, **every** consumer joins `members.airtable_id`
against a column that now contains `at_member_id` — so author attribution returns zero for *all*
sources. Today it at least works for WhatsApp.

If the session ends between Task 3 and Task 4, production sits in that state.

**Corrected order — consumers first, tolerant of both keys:**

1. **New Task 3a.** Repoint the six consumers to a transitional join that accepts either key:
   ```sql
   left join digest.member_profiles mm
     on mm.at_member_id = ci.meta->>'sender_member'
     or mm.at_member_id = (select m.at_member_id from digest.members m
                           where m.airtable_id = ci.meta->>'sender_member')
   ```
   After this commit, attribution works for **both** key spaces — strictly better than today,
   because Facebook now resolves too. This is the safe resting state.
2. **Then** the writers (old Task 2) and the backfill (old Task 3).
3. **Then** a final commit simplifying the transitional join back to a single condition.

Every intermediate state is now at least as good as production. Apply this reordering to
`2026-08-13-phase2-fix-live-defects.md` before executing it.

---

## 3. Per-phase evaluation

### Phase 2 — fix live defects

| Step | Blast radius | Detection | Rollback |
|---|---|---|---|
| Chapter dossier fix | None member-facing — no live reader of `kind='chapter'` | Assertion query | **Snapshot the 51 rows before deleting** (missing from the plan — add it) |
| `sender_member` (reordered per §2) | Author attribution, expertise, graph | Assertion + eval | `digest._phase2_task3_rollback` snapshot; consumers revert by function replace |
| Phone index | 17 members gain access | Assertion | Function replace |
| `multi_source_v2` routing | Main Q&A lane answers change | Probe + eval | Function replace |
| `video_speakers` rename | **Unknown — see below** | Grep | Rename back |
| Column comments | None | — | — |
| Fail-loud | **Can fail a live member write** | `job_errors` | Function replace |

**Two gaps in the Phase 2 plan, both to be fixed before execution:**

- **The 51 chapter rows are deleted with no snapshot.** They are fabricated and will not regenerate,
  so this is irreversible. Add `create table digest._phase2_task1_rollback as select * from
  digest.entity_dossier where kind='chapter';` before the delete.
- **The `video_speakers.member_record_id` rename greps `db/` and `scripts/` only.** `mds-digest-web`
  is a **separate repository** and is not searched. A rename that breaks the portal — which has 55
  live members — would be found by users, not by us. Either grep that repo too, or use the safer
  path: add the new column, keep the old one as a generated alias, and drop it in a later session.

**Fail-loud, specifically.** The mitigation (triggers log and continue, only the health check
raises) is right. Two additions: `digest.job_errors` has no retention policy and a persistent error
could fill it — add a 90-day cleanup. And the conversion must be done **one trigger at a time**,
because all three fire on live member activity.

### Phase 3 — declare the structure

**The dominant risk is R2: a constraint rejects a write that a live loader depends on.**

`NOT VALID` protects new writes *immediately* — which is the point, and also the hazard. From the
moment the constraint exists, a loader that inserts a child before its parent **fails**, in
production, silently as far as today's monitoring is concerned.

- **Hard dependency: Phase 1 Task 2 must ship before Phase 3 starts.** Without `job_errors` and
  fail-loud, a foreign-key violation inside a trigger is swallowed and reports green. Running Phase 3
  first means the primary detection mechanism for its own primary risk does not exist.
- **Ordering fix in Task 4 (forms registry):** the plan adds the FK at Step 4 and updates the loader
  at Step 5. That is backwards — the first submission from a new form between those steps is
  **rejected and lost**. Update the loader first.
- **Timing:** add constraints outside member-active hours. Validation takes `SHARE UPDATE EXCLUSIVE`,
  which does not block reads or writes but does block concurrent DDL and autovacuum.
- **`ON DELETE CASCADE` is a behaviour change.** Deleting a `member_profiles` row now removes derived
  data that previously survived as orphans. Consistent with the standing never-delete-a-member rule,
  but it must be stated, not discovered.
- **Task 7 (version collapse) is the riskiest in this phase** — it touches n8n and changes every tool
  call. Snapshot the workflow before and after; edit the active workflow and bounce with one
  `[{deactivateWorkflow},{activateWorkflow}]` call, never deactivate first (8.5h outage, 2026-07-21).

**Rollback for the whole phase:** `alter table … drop constraint …` per constraint. Fast, complete,
no data loss. Phase 3 is the most reversible of the five.

### Phase 4 — the three abstractions

**R1 lives here.** Task 2 moves the privacy boundary while 55 members are actively logged in.

The plan's mitigation — diff visibility against a baseline, require 0 newly-visible rows — is the
right shape but **too small a sample**. Fixes:

- Baseline must cover **every** active member, not 20, and every `content_items` row. It is a
  cross join of ~750 × 43,877 ≈ 33M rows; materialise it as a table, run it once, and keep it for
  the duration of the task.
- Stratify the check: report newly-visible counts **per `rule_type`**, so an owner-rule regression
  cannot hide inside a public-rule majority.
- **`can_see` takes `at_member_id` as a parameter and is `SECURITY DEFINER`.** If any caller passes
  a member id derived from user input rather than from `resolve_asker`, that is a direct IDOR — a
  member could read another member's owner-scoped content by supplying their id. **Every call site
  must derive the id from `resolve_asker(phone)` and never from an argument the member controls.**
  This constraint is not in the plan and must be added as an explicit review step per call site.
- **A row with a NULL `audience_rule_id` becomes invisible** — fail-closed, which is correct, but
  silent. Add an alarm on `count(*) where audience_rule_id is null > 0`.

**Task 1 (`member_link`) dual-write window:** during migration both old and new tables are written.
They can drift. Add a daily consistency check comparing counts per source for the full parity week,
not just a check at the end.

**Rollback:** each task keeps its old tables for a week, so rollback is repointing readers. But once
`access_rule` is dropped (Task 2 Step 8), rollback requires a restore. **Do not drop it until the
full-population baseline has been clean for a week.**

### Phase 1 (tests) and Phase 5 (RLS)

Lowest risk phase by a wide margin. That is the argument
for running Task 1 first.

- **pgTAP tests roll back**, so they cannot corrupt data. The only hazard is a test that forgets its
  `rollback` — mitigate by making the runner assert the transaction is not left open.
- **CI needs the database URL as a secret.** Andy adds it; an agent session must not handle it.
- **RLS: the honest finding is that policies would protect nothing today.** Everything runs as
  `service_role`, which carries `BYPASSRLS`, and `anon`/`authenticated` cannot log in and hold zero
  table privileges. Adding policies is defence against a *future* architecture where the portal
  connects as `authenticated` — real value, but not a current gap being closed. **This should change
  how option (b)/(c) is costed in the decision:** the work is preparation, not remediation. Option
  (a) — turn RLS off and record why — is more defensible than it first appeared, provided the reason
  is written where the next reader will find it.

---

## 4. Irreversible steps — the complete list

Everything else in all five phases is undoable by dropping a constraint or replacing a function.

| Step | Phase | Mitigation |
|---|---|---|
| Delete the 51 fabricated chapter dossiers | 1 | Snapshot first (**to be added**) |
| Backfill `sender_member` on 13,450 rows | 1 | `_phase2_task3_rollback` snapshot exists |
| Rename `video_speakers.member_record_id` | 1 | Prefer add-new-column over rename; grep `mds-digest-web` first |
| Drop `form_answers_latest` | 2 | Definition is in git; recreatable |
| Drop v1 functions in the version collapse | 2 | Definitions in `db/functions/`; recreatable |
| Drop `content_items.access_rule` | 3 | **Wait a full clean week; this is the one to be slowest about** |
| Retire `fb_member_map`, `zoom_name_alias`, `member_phone_index` | 3 | One-week parity rule already in the plan |

---

## 4b. How production is kept alive through every step

Andy's point, and it was a genuine hole: the plans verified *the thing being changed* and the
security gate, but nothing verified that **production still works** after each step. The leak gate
proves retrieval refuses what it must refuse. It does not prove Olivia is still answering anyone.

**`scripts/prod_pulse.py` closes that.** Read-only, seconds to run, and every check is
**directional against a saved baseline** rather than absolute — production ingests continuously
(`content_items` moved 43,877 → 44,043 in a single morning) and already carries known-firing
alarms, so absolute thresholds would be red from the start and would train us to ignore them. A
check fails only when something got *worse* than it was before the step.

What it verifies:

| check | why it is there |
|---|---|
| No new unanswered member messages | The single most important number — is Olivia still replying |
| Failed sends did not increase | A 200 from Meta is not delivery (`reference_wa_send_200_is_not_delivery`) |
| No **new** alarm firing | Pre-existing alarms do not mask a new one |
| No heartbeat went backwards | A job that was running has stopped |
| No new rows in `digest.job_errors` | Errors that used to be swallowed now surface here |
| Portal sessions present | 55 members are logged in right now |
| **No table lost rows** | 10 critical tables; a drop is data loss |
| 7 read-only RPCs still return 200 | Spans identity, retrieval, people, events |

**Usage, and it is not optional:**

```bash
python3 scripts/prod_pulse.py --save-baseline   # once at the start of a phase
python3 scripts/prod_pulse.py                   # before EVERY step, and again after it
```

**Exit 1 means stop and roll back that step** — not "finish this one first".

**Proven to work in both directions, 2026-08-13:** a forced regression (baseline claiming 500 more
`content_items` rows) produced `PULSE FAILED — content_items did not lose rows: 44543 -> 44043`
and **exit 1**; restoring the true baseline gave **exit 0**. A check that has never been seen to
fail has not been seen to work.

**Known gap, deliberately accepted:** the pulse cannot verify the *content* of an answer without
sending a WhatsApp message, and the standing rule forbids probing production against a real
member's number. It proves the machinery is alive, not that the answer is good. Answer quality is
the eval bank's job, and Phase 2 Task 5 and Phase 3 Task 7 both require one.

---

## 5. What would make me stop

Stop conditions, so they are decided now rather than under pressure:

- **`prod_pulse.py` exits 1.** This is the first and broadest stop condition — it fires on any of
  the eight regressions in §4b. Roll back the step, diagnose, do not continue.
- **Any newly-visible row** in the Phase 4 Task 2 visibility diff. Halt, do not continue to the next
  consumer.
- **A foreign-key violation appearing in `digest.job_errors`** from a scheduled job. Halt Phase 3,
  drop that constraint, fix the loader.
- **Eval pass rate down more than 2 points** after Phase 2 Task 5 or Phase 3 Task 7. Revert the
  function, keep the data change.
- **The leak gate falling below 253 checks or exiting non-zero.** Nothing ships past a red gate.
- **A heartbeat going stale for a job that was healthy before the change.** Treat as caused by the
  change until proven otherwise (`feedback_health_down_verification_protocol`).

---

## 6. Recommended execution order, revised

The phase numbering IS the execution order — run them 1, 2, 3, 4, 5:

1. **Phase 1 Task 1** — pgTAP suite. Its opening test fails today; everything after is safer.
2. **Phase 1 Task 2** — fail-loud. Required before Phase 3 can be detected at all.
3. **Phase 2, remaining tasks**, in the §2 corrected order.
4. **Phase 3**, constraints outside member-active hours.
5. **Decide Phase 4 with Phase 3's loader-reading experience in hand** — that read is the real
   estimate for Phase 4.
6. **Phase 5 (RLS)** last, as an explicit ruling, now understood as preparation rather than
   remediation.
