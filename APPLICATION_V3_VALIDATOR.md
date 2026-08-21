> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# New Member Application v3 — full flow + revenue verification (MASTER doc)

> ⚠️ **This flow is fragile and spans 4 systems** (Typeform → Make → Airtable → mds-digest-web/Slack). Read the **Gotchas** section before touching anything. Last updated 2026-07-02.

## Systems & IDs
| Thing | ID / location |
|---|---|
| Typeform (responder) | `FsVHzNN9` — form.typeform.com/to/FsVHzNN9 ("New Member Application v3") |
| Make scenario | **4784286** (zone **us1**, team 103111, org 258972, hookId 2746269) — webhook trigger, **ACTIVE** |
| Airtable base | `appou5JVr0WIrioWS` (MDS Member Database) |
| Forms table | `tblblwPcgqhkPTVec` (census/applications, ~720 fields) |
| Members table | `tblfwOSROSHfuYUxv` (~5,555 records) |
| Validator app | **mds-digest-web** (Render, `https://digest.mds.co`) |
| Slack channel | `C0AQ8USNQK0` (`#automation-tests`, workspace mdsoperations) |
| Slack app (cards) | **"MDS Verifier"** — app `A0B0MC1LGUQ`, bot user `mds_verifier` `U0BEQMZ07E0` (dedicated; NOT the WA-Approvals bot) |

## End-to-end flow
```
Applicant submits Typeform FsVHzNN9
  → Make 4784286 webhook (instant)
     → [M2] Airtable Create → Forms row (72 mapped fields)      (see "Mapping")
     → [M3] Router:
         route A: [M4] Search Members by {Preferred Email}={{2.Email}}
                  [M6] link Forms row → Member ("Link to Member (restored)")
                  [M7] Update Member (⚠ downgrade bug, see Gotchas)
         route B: [M5] Slack "…ready for 1st Interview" (legacy notice)
         route C: [M8] HTTP POST digest.mds.co/api/application/verify {recordId:{{2.id}}}   ← AUTO-TRIGGER
  → /api/application/verify: read row → download screenshot → Claude vision → verdict
     → write (NEW) Revenue Verdict + Status=Pending → post Slack card (MDS Verifier) + screenshot in thread
  → admin clicks Approve/Reject on card
     → /api/application/interactivity: verify Slack sig + HMAC → write decision → upsert+link Member → collapse card
  → on Approve: (NEW) Verified Revenue set → Members "Most Recent Revenue" lookup picks it up
```

## Mapping (Make M2 → Forms), 72 keys
- **Revenue → `(NEW) Unverified Revenue`** (`flddUz4Dazt9hG7eU`) ONLY. `Total TTM Revenue` (`fldaKrBFQpx4Mh1sZ`) is left empty at submit — filled only on human approval.
- **⭐ Each channel % is DUAL-mapped (important):** the applicant enters an **EXACT number** in Typeform (e.g. DTC = `10`), and Airtable stores it **two ways**:
  1. **Exact** — in the new `… % (raw)` **number** field.
  2. **Bucketed into a range group** — in the **LEGACY range field**, computed by a **BRACKET formula** in Make. Why: existing Members lookups + reporting expect the old range buckets (`<5%`, `6-15%`, …), not raw numbers, so we keep feeding them while also capturing the exact value.
  Bracket formula: `{{if(A=""; ""; if(A=0;"N/A"; if(A<=5;"<5%"; if(A<=15;"6-15%"; if(A<=25;"16%-25%"; if(A<=50;"26%-50%";"51%"))))))}}` where A = the raw % answer; emits ONLY the 6 canonical options (older junk options ignored).
  **Raw → legacy-bucket field pairs (same pattern for every source):**
  | Channel | Exact (raw) field | Legacy range-bucket field |
  |---|---|---|
  | Amazon % | `fldM2aBYBCJkoB4o8` | Amazon US & % of Revenue `fldkHF3aAHvrh66cR` |
  | DTC % | `fld8FknCxRJY3G0tM` | DTC % of Revenue `fldBag84Ccup8XQHN` |
  | TikTok % | `fld2IyHp5sf77Ezpq` | Tiktok % of Revenue `fld9kEjN30yKv0xh2` |
  | Retail % | `fldusJqIQWbw2dJ9X` | Retail % of Revenue `fldXWnACm5yFSWmUG` |
- **Other new channel fields:** Amazon Marketplaces `fldTI0Rs7EguK6LdE`, Other Sales Channels `fldgM672pjGuMKz3P`, DTC/Shopify Link `fldAzqovr4scmY8GT`, TikTok Shop Link `fldZ63DC7QuIupreg`, Amazon Brand Storefront `fldysNrMTERHKFHC5` (reused legacy url).
- **Second-seat checkbox fix:** `Business Partner/Employee` `fldODDbPi5NBZ8og4` = `{{if(substring(<1746afbe>;0;3)="Yes";true;false)}}` (was: any non-empty answer = checked).
- **Removed orphans:** Total TTM Revenue mapping (revenue now → Unverified), `Sell Brand?`. **Re-added** `sell on other marketplaces?` (`fld1dw38uZuErg1Uv` ← ref `07a1055e`) — had been wrongly dropped from a stale form snapshot.
- **Form % running total:** variable `pct_total` + `add` actions on each channel % + descriptions "Your channels so far add up to {{var:pct_total}}%".
- Full audit vs a real submission: 71/72 landed; named (non-uuid) refs (Name/Email/Formal Title) map without backticks.
- Spec detail: `APPLICATION_V3_MAPPING_SPEC.md`.

## Revenue verification (mds-digest-web)
**Files:** `src/lib/application/{airtable,verdict,token,slack,vision}.ts`, `src/app/api/application/{verify,interactivity}/route.ts`. Reuses `centurion/{vision,files,typeform}.ts`. Config: `config.application` (formsBaseId/formsTableId, revenueFloor 1_000_000, revenueTolerance 0.05, slackBotToken, slackSigningSecret, verifySecret).

**`POST /api/application/verify {recordId}`** (auto-fired by Make M8; also manual): read Forms row (`returnFieldsByFieldId=true` — see Gotchas) → download `Revenue Screenshot` (`fldIpj6kCpNT1Vuq8`, a Typeform file URL, needs TF PAT) + `Photo of Member` (`fldO5omBl7pkc2pC6`) → `ingestFiles` (unzips archives, normalizes HEIC/TIFF, flags rar/7z) → `analyzeApplicationScreenshots` (Claude vision, own MDS prompt: any proof format OK, $1M framing) → `computeAppVerdict` → write `(NEW) Revenue Verdict` `fldKCE3DsoDzTlGwy` + Status=Pending `fldm70WJAOk28MqKj` → `postApplicationCard`.

**Verdict (`verdict.ts`) — MDS rule, NOT Centurion's $20M:**
- ❌ no/unopenable proof, or unreadable figure → **needs_review**
- ❌ `screenshotTotal < $1M` (revenueFloor) → **reject** ("suggest reject")
- ❌ proof vs entered differ by **> 5%** (revenueTolerance) → **needs_review**
- ✅ else → **matches** ("OK — meets $1M+ bar")
- Verified-only: an unverified self-report never counts. Vision's soft concerns (multi-account, source type, date range) are shown as a card NOTE, not a verdict gate.

**Slack card (`slack.ts`)** — posted by the **MDS Verifier** app (its OWN interactivity URL):
- Header = verdict pill; Applicant (name·email); Business; Revenue (self-reported vs screenshot + Δ%); Per-file; Why; flags; Airtable link.
- **Photo on the card** = `slack_file` image block (upload photo → **wait ~4s for Slack to process** → reference; else `invalid_blocks`).
- **Screenshot in the thread reply** (v2 upload).
- **Approve / Reject = real interactive buttons** (action_ids `app_revenue_approve` / `app_revenue_reject`), value = signed JSON `{r,a,d,t}` where `t` = HMAC over (recordId,amount,decision) via SESSION_SECRET.
- Buttons only render when `APPLICATION_SLACK_BOT_TOKEN` is set (dedicated app); otherwise a "buttons disabled" note.

**`POST /api/application/interactivity`** (MDS Verifier's interactivity URL): verify Slack request signature (`APPLICATION_SLACK_SIGNING_SECRET`) + HMAC token → `recordDecision`:
- **Approve** → `(NEW) Verified Revenue` `fldVRcG7hogbImc7z` = amount, `Total TTM Revenue` = amount, Status=Approved, `(NEW) Revenue Verified By` `fldNY3y8CizX8f1El` = clicker, `(NEW) Revenue Verified At` `fldqONVzFYnArVcVn` = now; then **upsert+link Member** (`upsertAndLinkMember`: find by Preferred Email → create "Pending 1st Interview" if none → link Forms row via `fldT1CYVR8w20Qrr4`; never downgrades an existing member).
- **Reject** → Status=Rejected + by/at.
- Then **collapse the card** to one line (`✅/❌ {name} — decided by @x · $amt · member note`) + Airtable link, via `response_url`. On write failure → keep full card + buttons for retry.

## Most Recent Revenue = VERIFIED-ONLY (migrated 2026-07-01)
See `MOST_RECENT_REVENUE_VERIFIED.md`. Summary: `Most Recent Revenue` (Members `fldqZbbAAUUDptw8j`, ~68 deps) lookup was **repointed** — source → `(NEW) Verified Revenue`, filter → `Verified Revenue is not empty`, sort `Date Submitted` newest, limit 1. Backfilled 1,015 legacy rows (=Total TTM on most-recent-census + verified-Centurion). Before/after diff = **5,555/5,555 unchanged**. Approve→MRR proven (empty → verified figure).

### All lookups / cluster fields (Members) and status
| Field | id | type | status |
|---|---|---|---|
| Most Recent Revenue | `fldqZbbAAUUDptw8j` | lookup → `(NEW) Verified Revenue` | ✅ migrated verified-only |
| Most Recent Revenue Date Submitted | `fldeYhGSezL58KegF` | lookup → `Date Submitted` | ⚠️ **still census-gated** (blank for verified-app member) |
| Most Recent Revenue Date | `fldCFu6bDVpW0bfaM` | rollup → `Date Submitted` | ⚠️ **still census-gated** |
| Most Recent Revenue Source | `flduFYlZVbBp8OlWk` | formula | ⚠️ check/repoint |
| Total TTM Revenue | `fldAEmIH9JBhXu6la` | lookup → Forms Total TTM | reported/raw (unverified) — **kept as-is by design** |
| Member Forms (link) | `fldfV4vhqPKeIehyX` | link → Forms | inverse = Forms `fldT1CYVR8w20Qrr4` |
- `Date Submitted` (Forms `fldgkldiwLVhkx3EI`) = `CREATED_TIME()` → submission date, NOT approval. Approval date = `(NEW) Revenue Verified At`.
- All 7 cluster fields have plain-English descriptions set in Airtable.

## GOTCHAS (the fragile bits — read before editing)
1. **Slack buttons fire the app's interactivity URL — even URL-only buttons.** The WA-Approvals bot's single interactivity URL is owned by LIVE n8n. Posting buttons via that bot got a card auto-"rejected" by n8n on 2026-07-01. → cards MUST use the dedicated **MDS Verifier** app.
2. **`slack_file` image block 400s (`invalid_blocks`) if referenced before Slack finishes processing the upload.** Processing time scales with file size — **measured 0.5s at 17 KB but 6.8s at 4.5 MB** — so the original fixed 4s wait silently killed the card for every applicant with a big photo (Ginny Lo 2026-08-05, Benjamin Pearson 2026-08-11: verdict written to Airtable, no card, failure swallowed into a `console.error`). Now: **poll `files.info` until `thumb_360`/`thumb_720` exists** (20s cap), and post the card WITHOUT the image block if it still isn't ready or the post is rejected anyway. Fixed in `a8dec73` + `add8115`.
   - ⚠️ **`files.info` only accepts form-urlencoded arguments.** Sent as JSON it returns `invalid_arguments` — the first version of the poll used the shared JSON helper, so every poll failed and every photo was dropped. `chat.postMessage`/`files.completeUploadExternal` take JSON; the read methods do not.
   - **A missing card is invisible** — the verdict still lands in Airtable, so Airtable looks healthy and only a human noticing the quiet channel catches it. Rows with `(NEW) Revenue Verdict` set are the audit list: any row with a verdict and no card in `C0BFVA01AJ0` was lost.
3. **Typeform draft vs published:** API PUTs change the LIVE form (responders see them immediately) but the builder shows "unpublished edits". **Do NOT click Publish** in the builder — it can revert to a stale draft. Sync via Version History → load "(Live)".
4. **AT Meta API cannot create/edit lookups or rollups** (UI-only). The MRR repoint was done in the Airtable UI. It also can't set view field visibility.
5. **Airtable record read must use `returnFieldsByFieldId=true`** when addressing fields by ID (else the response is keyed by field NAME → everything reads empty). This bit us once ("no proof uploaded").
6. **Make token needs `scenarios:write`** — the `MAKE_API_TOKEN` in `.env.local` is read-only. Blueprint edits (M2 remap, M8 trigger) used a write-scoped token pasted in-session (not persisted). Apply pattern: `stop → PATCH /scenarios/{id}/blueprint (stringified) → start`, then read-back verify.
7. **Vision needs Anthropic credits** — `CENTURION_ANTHROPIC_API_KEY`'s account ran dry mid-session (took Centurion down too, same key). Watch the balance.
8. **Typeform screenshot URLs expire** — stale test rows lose their screenshot → vision reads nothing. Fresh submissions have live URLs; the validator fires within seconds so it's fine in prod.
9. **Members downgrade bug (M7, pre-existing):** M7 sets Status="Pending 1st Interview" + Standard access on a matched member with NO guard → re-submitting member gets downgraded. Use a **non-member email** to test. Fix pending.
10. **New applicants weren't created in Members** by the Make scenario (M4 only searches). Now handled by the validator's Members-upsert on Approve.

## Environment (Render + .env.local)
`APPLICATION_SLACK_BOT_TOKEN` (MDS Verifier xoxb), `APPLICATION_SLACK_SIGNING_SECRET`, `APPLICATION_VERIFY_SECRET` (optional gate on /verify). Reuses: `CENTURION_ANTHROPIC_API_KEY`, `CENTURION_TYPEFORM_PAT`, `CENTURION_SLACK_BOT_TOKEN` (fallback bot, no buttons), `CENTURION_TEST_SLACK_CHANNEL`=C0AQ8USNQK0, `AIRTABLE_PAT`, `SESSION_SECRET`, `NEXT_PUBLIC_BASE_URL`. Make blueprint edits need a write-scoped `MAKE_API_TOKEN`.

## OPEN ITEMS / TODO
- [ ] **Approve should let the admin choose which figure to record** — screenshot amount vs entered amount (e.g. two buttons: "Approve screenshot $35M" / "Approve entered $1M"). Currently defaults to screenshot ?? entered.
- [ ] **Migrate the MRR date/source twins** (`fldeYhGSezL58KegF`, `fldCFu6bDVpW0bfaM`, `flduFYlZVbBp8OlWk`) to the same verified gate — currently blank for verified-app members.
- [ ] **Unify all revenue-bearing forms** (Centurion, census, honorary) through this SAME verification card; **label the source form** on the card. (Centurion write-to-Verified-Revenue intentionally skipped for now.)
- [ ] **Registry pages** in ClickUp `2531q-102577` for every touched field (list below) — deferred.
- [ ] Strip `(NEW)`/`(MOVED)` tags (10 left) + restore required fields (form is in all-optional review mode) before go-live.
- [ ] Members-table: verify email↔Preferred Email join; create lookups for the new fields (UI-only) if needed on Members.
- [ ] M7 downgrade guard.
- [ ] Cleanup test artifacts: member `recp0cONtb9zuWIcQ`, `andydelete@me.co` row `recIXwcKEQGuh4nSI`, junk n8n WA log `recgrlkagHhDZH3Iv`, stray test Slack cards.

### Fields touched (for the deferred registry pages)
Forms: `(NEW) Verified/Unverified Revenue`, Revenue Verdict/Status/Verified By/At, Amazon/DTC/TikTok/Retail %(raw), Amazon Marketplaces, Other Sales Channels, DTC/TikTok Shop Link, Amazon Brand Storefront, the 4 legacy range (bracket) fields, Total TTM Revenue. Members: Most Recent Revenue + Date + Date Submitted + Source, Total TTM Revenue (lookup).
