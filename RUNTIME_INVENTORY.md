> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Runtime inventory — where every job runs, and whether anyone would notice it dying

**#64. Built 2026-09-10 from the live machine, not from memory.** The ticket's line is *"the failure mode is
always silence"*, and the night this was written proved it three times over: a nightly job had burned 3.5 hours
for nothing since 7 Sep (#180), a cleanup tool had deleted nothing for weeks while printing "cleanup done"
(#117), and the persona builder had been failing 61% of the time reporting only "no valid JSON" (#189).

**Re-check with:** `launchctl list | grep com.mds` (second column is the last exit status) and the log
freshness table below.

---

## 1. This Mac — 9 launchd jobs

⚠️ **They existed only here.** The plists are now copied into `ops/launchd/` so they are no longer single-copy.
That directory is a **copy, not the source** — launchd reads `~/Library/LaunchAgents/`. Re-install with
`cp ops/launchd/<x>.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/<x>.plist`.

| job | when (local) | what it runs | heartbeat? |
|---|---|---|---|
| `com.mds.scorecard.heartbeat` | Mon 02:15 | `mds-scorecard-tools/h…` | ❌ none |
| `com.mds.olivia-eval` | 03:30 | `mds-scorecard-tools/olivia_eval.py --nightly` | ❌ none |
| `com.mds.persona.refresh` | 04:15 | `mds-scorecard-tools/persona_refresh.py` | ❌ none |
| `com.mds.olivia.derivations` | 04:30 | `Scorecard/scripts/nightly_derivations.py` | ✅ 14 rows |
| `com.mds.zoom.weekly` | Mon 05:15 | `Scorecard/scripts/zoom_weekly.py` | ✅ |
| `com.mds.db.drift` | 05:40 | `Scorecard/scripts/db_export_schema.py --check --alert` | ❌ (Slacks instead) |
| `com.mds.wa.dailydigest` | 09:30 | `mds-wa-outbound/post_daily_digests.py` | ❌ none |
| `com.mds.olivia.watchdog` | every 15 min | `Scorecard/scripts/alarm_watchdog.py` | ❌ none |
| `com.mds.scorecard.autoimport` | on file drop | `mds-scorecard-tools/a…` | ❌ none |

### 🔴 The finding that matters: seven of nine run inside the sleep window

**02:15 → 05:40 is exactly when the lid is shut.** macOS wakes ~8 seconds an hour for maintenance, so a job
launched there gets seconds of CPU and then the machine sleeps mid-request. Only the 09:30 digest and the
file-triggered import sit outside it.

That single fact produced #180 and explains its whole symptom set — three and a half hours of wall clock for ten
120s-capped calls, `subprocess.run(timeout=1800)` never firing (monotonic stops during sleep on Darwin, wall
clock does not), and `cache_member_photos` at 5,749s against a normal 106s.

**Unfixed, and it needs Andy's password:** `sudo pmset repeat wakeorpoweron MTWRFSU 04:25:00`.
Confirm any suspicion with `pmset -g log | grep -E "Entering Sleep|DarkWake"`.

### 🔴 Second finding: `mds-scorecard-tools/` is not a git repository

`persona_refresh.py` and `olivia_eval.py` are **single-copy untracked files**. That is worse than the ticket's
"eight plists exist only on Andy's Mac" — these are production scripts with no history and no second copy.
`persona_refresh.py.bak-20260910` was taken before #189's fix. **Decide whether this becomes a repo.**

### Last exit status, 2026-09-10 04:0xZ

| job | exit | reading |
|---|---|---|
| `db.drift` | 1 | working as designed — it **detected** drift and Slacked. Cleared this session; check now returns 0. |
| `olivia.derivations` | 1 | #180, fixed. |
| `persona.refresh` | 1 | #189, fixed — 19 of 31 were failing. |
| `olivia-eval` | 1 | **#190** — 21 of 220 FAIL, 9.5% against Andy's <1% bar. |
| the other five | 0 | fine. |

**Log freshness is the only signal for the five with no heartbeat.** `wa.dailydigest`'s `launchd.err.log` is a
stale crash from 02 Sep; its `out.log` shows a clean "run done" on 09 Sep, so it is healthy — but **only a human
reading two files can tell**, which is the point of the ticket.

---

## 2. Off this Mac

| where | what | how it is watched |
|---|---|---|
| **n8n Cloud** | `Olivia WA` prod + staging; `Reminder Sender` (every minute, carries the #97 intro sweep) | the 5-min webhook ping, and `olivia_health_check()` inside Postgres |
| **Postgres (pg_cron)** | `olivia-health` every 5 min — fires **inside the database**, so it still alarms when n8n is down | Slack |
| **Render** | `mds-digest-web` — the relay, the Olivia route lanes, the health report | `/api/version`, and the relay's own `maintenance` rows |
| **GitHub Actions** | `member-profiles-sync.yml` (daily ~13:47 UTC), events catalog (hourly on paper — **#181**, four-hourly in fact, blocked on a PAT) | the sync-freshness tile (**#188** made it name which half is behind) |
| **Make** | Guest Multi-Event, Luma Manual Add, Slack→Luma, two Stripe⇄AT syncs | run-status tiles (**#179** made a warning read amber) |

---

## 3. What is still open

- **The sleep window** — the biggest one, needs a password.
- **`mds-scorecard-tools` under version control** — Andy's call.
- **Five jobs with no heartbeat** (`olivia-eval`, `persona.refresh`, `wa.dailydigest`, `watchdog`,
  `scorecard.heartbeat`). Each could die and only a log mtime would say so. Cheapest fix: have them stamp
  `digest.olivia_job_heartbeats` like the derivations do, which makes the existing 26h alarm cover them for free.
- **Thirteen channel-call opt-in forms still collect into nothing** (carried from the 2026-08-08 note, unverified
  tonight).
