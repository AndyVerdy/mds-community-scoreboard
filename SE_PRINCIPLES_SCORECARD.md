> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# MDS Platform — Software-Engineering Principles Scorecard

> Generated 2026-06-22 via a 6-subagent audit workflow (one agent per repo, 30 principles each, file:line citations). Raw structured output archived at:
> `/private/tmp/claude-501/-Users-Born-Scorecard/29dce305-7f50-4a24-9a76-e1cf502226ad/tasks/wyuw77lub.output`

**Scope:** 6 repos under `/Users/Born/`, every source file read (node_modules / .next / venvs / data dumps excluded). 180 graded cells.
**Legend:** ✅ pass · 🟡 partial · ❌ fail · — n/a

## Starting-evidence corrections
- **"No tests in any of the 5"** → partly false for `mds-ai-bot`: it has a real 336-line suite (`tests.py`) but one case is broken (`tests.py:310` expects 400, route returns 401) and `tests/dynamic_search_quality.py` has zero asserts. Other 4 repos: zero tests confirmed. `mds-skill-base/tests/` is fixtures only.
- Everything else in the brief verified true. Two NEW findings: committed/plaintext secrets (must-fix #1 and #2).

## Health ranking

| # | Repo | ✅ / 🟡 / ❌ | Tests | One-line verdict |
|---|------|------------|-------|------------------|
| 1 | mds-intercom-lastseen-sync | 15 / 12 / 1 | none | Tight 64-line idempotent cron; only gap is untestability (no DI). |
| 2 | mds-skill-base | 15 / 12 / 2 | fixtures only | Strong HMAC/defensive boundaries; undermined by Airtable-vs-Supabase split that breaks the portal. |
| 3 | mds-digest-web | 12 / 14 / 4 | none | Clean, fail-fast, no secrets — dragged down by 1,234-line dashboard god component, Airtable client duplicated 13×, zero tests. |
| 4 | mds-video-admin | 14 / 10 / 6 | none | Low-debt; multi-tenant isolation enforced only in app code on a service-role client. |
| 5 | mds-ai-bot | 11 / 13 / 6 | partial/broken | Pragmatic RAG/Flask; committed prod auth-bypass code, fail-open auth, 2,502-line god module (web.py). |
| 6 | mds-scorecard-tools | 7 / 14 / 8 | none | Excellent cron idempotency; plaintext prod secrets, triplicated helpers, error-swallowing curl, 827-line god service-worker. |

## 🚨 Platform-wide must-fix (security + correctness)

1. **Committed prod auth bypass** — `mds-ai-bot/tests/dynamic_search_quality.py:56` hardcodes live Apple-reviewer login code `837363` (= permanent prod bypass via `auth.py:102-105`), in git history (commit `22e6189`). Rotate + purge. [HIGH]
2. **Plaintext production secrets** — `mds-scorecard-tools/config.json:3` (Airtable PAT, write to 2 prod bases) + `config.json:8` (Slack xoxb). No `.gitignore`. Rotate, move to keychain/env. [HIGH]
3. **Fail-open authorization** — `mds-ai-bot/auth.py:204` returns True on any Airtable error + when PAT unset (`auth.py:177-180`); `mux_webhook.py:90-92` returns True when secret unset. Default-deny. [HIGH]
4. **Multi-tenant isolation in app code only** — `mds-video-admin` runs every route through RLS-bypassing service-role client gated only by hand-written `eq('organization_id',…)` (`src/app/api/admin/videos/route.ts:25-35`). One forgotten filter = cross-tenant leak. Add RLS. [HIGH]
5. **Portal silently broken** — `mds-skill-base` reads approved skills from Supabase (`src/app/page.tsx:10`) but pipeline writes only Airtable (`store-airtable.ts:185`). Portal always empty. Pick one store. [HIGH]
6. **No automated tests in 5 of 6 repos** — root cause is clients hard-instantiated as module singletons (DI/IoC fails), so nothing is unit-testable without live env. [HIGH]

## The matrix

Cols: DW=digest-web · AI=ai-bot · VA=video-admin · SB=skill-base · ST=scorecard-tools · IC=intercom-sync

| Principle | DW | AI | VA | SB | ST | IC |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| *Automated tests present* | ❌ | 🟡 | ❌ | ❌ | ❌ | ❌ |
| KISS | 🟡 | 🟡 | ✅ | ✅ | 🟡 | ✅ |
| YAGNI | 🟡 | ✅ | 🟡 | 🟡 | 🟡 | ✅ |
| Rule of Three | ❌ | ❌ | ❌ | 🟡 | ❌ | ✅ |
| No Premature Optimization | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 |
| DRY | ❌ | ❌ | ❌ | 🟡 | ❌ | 🟡 |
| SSOT | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| SOLID | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| Separation of Concerns | 🟡 | 🟡 | 🟡 | ✅ | 🟡 | 🟡 |
| High Cohesion | ✅ | 🟡 | ✅ | ✅ | 🟡 | ✅ |
| Low Coupling | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | ✅ |
| Law of Demeter | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 |
| Encapsulation | 🟡 | 🟡 | ✅ | ✅ | 🟡 | ✅ |
| SLAP | 🟡 | 🟡 | 🟡 | 🟡 | ❌ | 🟡 |
| Dependency Injection / IoC | ❌ | 🟡 | ❌ | 🟡 | ❌ | ❌ |
| Tell Don't Ask | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | — |
| CQS | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| Fail Fast | ✅ | ❌ | ❌ | 🟡 | 🟡 | ✅ |
| Make Illegal States Unrepresentable | 🟡 | ❌ | 🟡 | 🟡 | ❌ | 🟡 |
| Idempotency | 🟡 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Least Astonishment | 🟡 | 🟡 | ✅ | ❌ | 🟡 | 🟡 |
| Least Privilege | 🟡 | ❌ | ❌ | ✅ | ❌ | ✅ |
| Defensive Programming | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 |
| Design by Contract | 🟡 | 🟡 | 🟡 | ✅ | ❌ | 🟡 |
| Boy Scout Rule | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ |
| Pit of Success | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |

**Clean across all 6 (collapsed):** Worse Is Better · Convention over Configuration · Composition over Inheritance · Postel's Law · Unix Philosophy — all ✅/—.

## Per-repo violations (worst → best, cited)

### mds-scorecard-tools (8 fails)
- ❌ Least Privilege — `config.json:3` PAT + `config.json:8` Slack token plaintext, no .gitignore.
- ❌ Rule of Three/DRY — `nm()/curl()/pull()/write()` dup `process_fb.py:28-69` ↔ `reconcile.py:43-107`; FB-GraphQL parser ×3 (`parse_graphql.py:105`, `background.js:478`, `background.js:342`).
- ❌ Fail Fast — `process_fb.py:39` curl swallows everything → silent 0-row writes with success summary. [HIGH]
- ❌ SLAP/SOLID — `extension/background.js` 827-line god worker; `capturePostMain` `background.js:421-571`.
- ❌ SSOT — group id `699138040189700` in `background.js:2` + `reconcile.py:142`; field names scattered.
- ❌ Make Illegal States — `recompute_script.js:75` writes NaN to Engagement Score if Cap cell blank. [MEDIUM]
- ❌ Design by Contract — no schema checks; `read_contributors` trusts shape `process_fb.py:81`.
- 🟡 Boy Scout — dead loop `parse_graphql.py:177-181`; unused `scoring-admin-mockup.html`; debug `captureOnePost('Eugene's roundtable')`.

### mds-ai-bot (6 fails)
- ❌ Least Privilege — committed bypass `tests/dynamic_search_quality.py:56`; SERVICE_ROLE_KEY for read-only (`videos.py:67`).
- ❌ Fail Fast — fail-open `auth.py:204` + `mux_webhook.py:90`; no boot env validation.
- ❌ SSOT — `AIRTABLE_BASE_ID='appT9TVZWhv7io4CN'` ×3 (`web.py:30`, `auth.py:34`, `ingest.py:31`).
- ❌ DRY — `_supabase_write()` identical `transcripts.py:115` ↔ `mux_webhook.py:45`; internal-secret guard ×4 (`web.py:2361,2392,2434,2447`).
- ❌ Make Illegal States — RAG result untyped dict in 6+ sites (`query.py:392`); source type loose string.
- ❌ SLAP — `ask()` `query.py:384` 300+ lines, 4 abstraction levels; `web.py` 2,502-line god module.
- 🟡 Least Astonishment — `email_sender.py:52` docstring contradicts code.

### mds-video-admin (6 fails)
- ❌ Least Privilege — service-role client for all reads/writes, app-only org filter (must-fix #4).
- ❌ Fail Fast — no boot env validation; `src/lib/supabase/server.ts:49` bare `process.env...!`.
- ❌ DRY/Rule of Three — ~150 lines dup between the two metadata editors; `formatDuration` ×3.
- ❌ SSOT — visibility vocabulary ×4 (`videos/[id]/route.ts:12` + 2 zod enums + 2 arrays); MAX_ROWS/ORPHAN_TTL_MS dup.
- ❌ DI/IoC — every route hard-imports supabase factories (`access.ts:9`); root cause of zero tests.
- 🟡 Design by Contract — clients use zod, server routes don't (`videos/[id]/route.ts:34`, "no Zod yet" line 5).

### mds-digest-web (4 fails)
- ❌ DRY/Rule of Three — two `atFetch` impls (`airtable.ts:13` + `admin/airtable-stats.ts:16`); 13 raw inline Airtable fetches across 7 files; MONTHS ×5; @mds.co check ×4; `classifyN8nPipeline`≈`classifyMakePipeline`.
- ❌ SSOT — base id `appUM1F29IJsMsXRb` in `scorecard.ts:9`, `fb.ts:11`, `registry.ts:77`; subs written to both new JSON + legacy fields (`subscriptions/route.ts:50-65`).
- ❌ DI/IoC — import-time singletons `new Resend` (`email.ts:4`), `new Anthropic` (`vision.ts:114`); `config.ts:27` exports secrets to every importer.
- 🟡 SoC/KISS — `dashboard/page.tsx:239` 1,234-line god component.
- 🟡 Idempotency — `centurion/verify/route.ts:30` in-memory webhook dedupe resets on redeploy → reprocesses. [MEDIUM]
- 🟢 Copy platform-wide: `config.ts:21` boot env validation, `tools-health/report.ts:30` deliberate SSOT, zod at edges, `token.ts:21` timingSafeEqual.

### mds-skill-base (2 fails)
- ❌ Least Astonishment/SSOT — broken portal (Supabase read vs Airtable write) (must-fix #5).
- ❌ SSOT (rubric) — security-review prompt in both `review-rubric.ts:6` and `~/.claude/skills/mds-skill-review.md`, aligned by a human comment (`review-rubric.ts:2-4`). [HIGH]
- 🟡 Fail Fast — `members.ts:93,110,124` matchMember swallows all errors to 'unmatched'.
- 🟡 DbC — `review.ts:51-54` casts model output checking only 2 fields.
- ⚠️ Doc hygiene: `PROJECT.md:218` live-looking PAT/Bearer strings — scrub + rotate. [LOW]

### mds-intercom-lastseen-sync (1 fail)
- ❌ DI/IoC — endpoints/headers/fetch hard-wired singletons (`sync.mjs:8-11,46`). Wrap in `run(config)`.
- 🟡 Defensive Programming — 4 top-level call sites (`sync.mjs:33,46,61`) have no try/catch.
- 🟡 Least Astonishment — `sync.mjs:17` retries HTTP 403 like 429 (intentional IP-edge workaround, uncommented).

## Cross-cutting patterns
1. Every app re-implements its own Airtable client by raw fetch AND duplicates it in-repo (digest-web 13×, ai-bot 4×, scorecard-tools 2×). A shared internal `@mds/airtable` pkg kills the #1 violation.
2. DI/IoC fails everywhere → directly causes zero-tests everywhere. The two rows move together.
3. Stringly-typed status/field vocabularies recur (visibility, mux_status, source type, RAG confidence, AT field names) — none modeled as enums.
4. Boundary defense is strong; boot-time fail-fast is inconsistent (digest-web + intercom validate at startup; the rest fail or fail-open at request time).
5. Idempotency genuinely good (4/6 ✅); one hole is digest-web Centurion in-memory dedupe.

## Next step (deferred)
User asked to offer pushing this into Tools-Health ClickUp doc `2531q-100937` as a new page ("SE Principles Scorecard — June 2026"). Not yet done — paused for an urgent WA-analytics bug.
