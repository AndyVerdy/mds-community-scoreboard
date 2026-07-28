> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Most Recent Revenue → verified-only (migration 2026-07-01)

**Base `appou5JVr0WIrioWS`.** `Most Recent Revenue` used to be **census-gated** — it pulled the most-recent *standard census* Total TTM Revenue, i.e. an **unverified self-report**. Decision (Andy): it must reflect **only human-verified revenue, from any source** (App v3, Centurion, honorary, …). Legacy is grandfathered in; going forward only a verified event moves the number.

## The model
- Every revenue-bearing Forms row gets a **`(NEW) Verified Revenue`** value **only when verified** (App v3 approval writes it; legacy rows were backfilled once — see below).
- `Most Recent Revenue` (Members lookup) returns the newest such row. Editing the existing lookup **in place** keeps all ~68 downstream dependencies (tiers, WA/Centurion gating, dashboards) working unchanged.

## Fields touched (descriptions updated in Airtable to match)
| Field | Table | id | Change |
|---|---|---|---|
| `(NEW) Verified Revenue` | Forms `tblblwPcgqhkPTVec` | `fldVRcG7hogbImc7z` | **Source of truth.** Set on App v3 Approve; backfilled = `Total TTM Revenue` on legacy qualifying rows. |
| `Most Recent Revenue` | Members `tblfwOSROSHfuYUxv` | `fldqZbbAAUUDptw8j` | Lookup **repointed**: source → `(NEW) Verified Revenue`; filter → `Verified Revenue is not empty` (replaced the census/Centurion condition groups); sort `Date Submitted` newest, limit 1. |

## Field descriptions (all set in Airtable, plain-English)
| Field | Table | id | Reads as |
|---|---|---|---|
| `Most Recent Revenue` | Members | `fldqZbbAAUUDptw8j` | latest **verified** revenue; updates on approval |
| `Most Recent Revenue Date Submitted` | Members | `fldeYhGSezL58KegF` | when it was **submitted** (not approved) — data age |
| `Most Recent Revenue Date` | Members | `fldCFu6bDVpW0bfaM` | date of most recent verified revenue |
| `Most Recent Revenue Source` | Members | `flduFYlZVbBp8OlWk` | link to the form it came from |
| `(NEW) Verified Revenue` | Forms | `fldVRcG7hogbImc7z` | **source of truth**; set on approval / backfilled |
| `Total TTM Revenue` | Members | `fldAEmIH9JBhXu6la` | **reported/raw** figure (unverified) — kept for reference |
| `Total TTM Revenue` | Forms | `fldaKrBFQpx4Mh1sZ` | per-form **reported** figure (unverified) |

`Total TTM Revenue` deliberately stays the **reported** number (so we never lose what a member claimed); `Most Recent Revenue` is its verified counterpart. It is **not** migrated.

## Backfill (grandfather legacy)
Copied `Total TTM Revenue → (NEW) Verified Revenue` on the **1,015** rows that currently feed Most Recent Revenue (most-recent standard census + verified Centurion). Result: Day-1 no-op.

## Proof
Before/after snapshot diff of all members' `Most Recent Revenue`: **5,555 / 5,555 unchanged** (0 changed, 0 blank, 0 gained). App v3 chain proven: setting `(NEW) Verified Revenue` on an approved application row moves that member's `Most Recent Revenue` empty → the verified figure.

## ⚠️ Still to migrate (the date/source twins — same gate change)
These were NOT touched yet, so they read **blank for a verified-app member** while the value shows:
- `Most Recent Revenue Date Submitted` (Members `fldeYhGSezL58KegF`, lookup → Forms `Date Submitted`) — **the field to read the date of the most recent revenue** (submission date, = `CREATED_TIME()`, not approval date). Needs filter → `Verified Revenue is not empty`.
- `Most Recent Revenue Date` (Members `fldCFu6bDVpW0bfaM`, rollup → `Date Submitted`) — same filter change.
- `Most Recent Revenue Source` (Members `flduFYlZVbBp8OlWk`, formula) — verify it points at the verified row.
Update each field's **description + this doc** when migrated.

## Future (not this session)
- Route **every** revenue-bearing form (Centurion, census, honorary, other) through the **same verification Slack-card flow**; App v3 validator = the template.
- **Label the source form** on the Slack card.
- Legacy forms' deeper issue: reported revenue is unverified — address during the unify.
