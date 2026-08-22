# Brokered Intros (#97) — Full Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the proven POC (consent template + ledger + tap loop) into the real member feature: a member says "connect us" after a recommendation, the target consents on their phone, and only a yes moves a phone number.

**Architecture:** One new app route (`/api/olivia/intro`) owns ALL intro policy — request, pick-resolution, tap-resolution, expiry sweep — per the "new lanes are app routes, not RPCs" rule (retrieval in SQL, POLICY in git). The gated main workflow gains one early branch that swallows intro taps before the LLM lane sees them (the POC's screenshot bug). The seed gains one tool (`member_intro`) so "connect us" resolves against the asker's own recommendation log. `digest.olivia_intros` (exists, POC-built) stays the single ledger.

**Tech Stack:** Next.js route (mds-digest-web, **Render** — digest.mds.co, manual redeploy on env change) · Meta WhatsApp Cloud API v22.0 (approved template `mds_intro_request` + interactive list + free-form) · Supabase `digest` schema · n8n (main workflow branch via `olivia_wf.py` staging; Reminder Sender for the sweep tick) · leak gate.

## Global Constraints — ANDY'S RULINGS, LOCKED 2026-08-20 (verbatim where quoted)

- **Consent-first, always:** *"no number leaves without the target's yes"* — no wa.me link, no phone digits in ANY response until `status='accepted'`. A wa.me link IS the number.
- **Targets come ONLY from the asker's own recommendation log** (`digest.olivia_recommendations`, 30 days, any lane). She can never be talked into pinging an arbitrary member.
- **One pick = one consent request.** "Connect me with all of them" is declined gently.
- **Caps (defaults Andy may adjust; enforce in CODE):** max **3 pending per requester** · max **3 consent pings per target per 7 days** across all requesters · one pending per requester→target pair (unique index exists).
- **Decline is FINAL and never revealed.** Requester line, verbatim: *"No connection with {first} yet — I'll let you know if that changes."* Target hears nothing more. No re-request of the same pair, ever.
- **Silence = 7-day expiry, retryable, ZERO reminders to the target.** Requester line, verbatim: *"I didn't get a response from {first} this week, so I've let it rest. Want me to try again later — or introduce you to someone else on {topic}?"*
- **Unreachable (no phone on record, or Meta 131026 not-on-WhatsApp):** requester line, verbatim: *"I can't reach {first} on WhatsApp. Want me to suggest someone else on {topic} — or I can pass your request to the MDS team to make the intro by email?"* Team escalation = the existing Slack `Notify Team` path. Target population is ALL actives — phone-less members are `unreachable`, never silently skipped (every-member-always).
- **Accept messages, verbatim:** target: *"Great — you're connected with {requester_full}. Start the conversation: wa.me/{requester_phone}"* · requester: *"{target_first} accepted your intro request — start the conversation: wa.me/{target_phone}"*.
- **ELIGIBILITY — REVISED 2026-08-22 (Andy: "yes, go" after seeing a confirmed attendee refused and one-row pick lists): eligible = Summit attendee (registrations ledger) WITH a phone on record — the 'Millie user' requirement is DROPPED on both sides (#107d).** Original 2026-08-21 lock kept for the record: intros run ONLY when BOTH sides are (a) **Millie users** — ≥1 real inbound member turn in `digest.olivia_messages` (SELFTEST/eval traffic excluded) — and (b) **Summit-registered** — present in the registrations ledger (`event_registrations_live`) for the REAL Summit `recrATwhUDA55iQN5` (never name-match the catalog — the "Night Out" row is the trap). Requester ineligible → *"Intros are running as a Summit-attendee pilot right now — I'll open them up more widely after Singapore. In the meantime I can still tell you who's worth meeting."* (reworded 2026-08-22 — Andy: registration is effectively closed, never invite it) Target ineligible → *"I can't set that one up — intros are Summit-locked for now and {first} isn't on my Summit intro list. Want me to suggest another attendee on {topic}?"* (wording adjustable by Andy at close). **Parked, do not implement:** last-used <30d. Probes under this lock use the CANARY pattern — temp registration row for the probe identity, DELETE same session — Andy's real registration does not exist yet.
- Template: **`mds_intro_request`, APPROVED, UTILITY** (id 1413344637359224) — vars {{1}} target first name, {{2}} requester full name, {{3}} topic. Never resubmit/rename it.
- **POC findings baked in:** template button taps arrive `msg_type='button'` and are NOT in `olivia_messages` (raw store only) · list taps arrive `type='interactive'` with `list_reply.id` · PostgREST plus-is-space (Z-suffix all timestamps in URLs) · the intro branch must run BEFORE the LLM lane (screenshot bug 2026-08-20).
- **A 200 from Meta is NOT delivery** — every send verified via `digest.olivia_sends`.
- Scores/ranks stay internal · gate EXIT 0 before ship (never `| tail`) · `python3 scripts/db_export_schema.py` + commit `db/` after every migration · CREATE OR REPLACE never DROP · staging probes before Andy promotes any workflow edit · POC scripts (`olivia_intro_poc.py`) retire when Task 6 closes.

## Prerequisites (Andy runs)

1. **RENDER env** (NOT Vercel — verified 2026-08-21: digest.mds.co serves `x-render-origin-server: Render`; README confirms service `mds-digest-web`) — Render dashboard → service `mds-digest-web` → Environment tab: add `META_WA_TOKEN` + `META_WA_PHONE_NUMBER_ID` (values = the same names in `/Users/Born/mds-digest-web/.env.local`; bare values). The intro route sends WhatsApp itself — today only n8n holds these. Then **Manual Deploy** (Render does not redeploy on env-only changes).
2. `promote` for the workflow edit (Task 4) and the seed edit (Task 5) after staging probes pass.

---

### Task 1: Ledger v2 — `unreachable` status + decision reasons

**Files:**
- Create: migration `olivia_intros_v2_20260820` (via `mcp supabase apply_migration`)
- Modify: none (table exists from POC: `digest.olivia_intros`)
- Test: SQL assertions in Step 3

**Interfaces:**
- Consumes: existing `digest.olivia_intros (id, requester_at_id, target_at_id, topic, status, consent_wamid, created_at, decided_at)` with statuses `pending|accepted|declined|expired`.
- Produces: status set grows to `pending|accepted|declined|expired|unreachable`; new column `decided_reason text NULL` (`'tap' | 'sweep' | 'no_phone' | 'wa_131026' | 'send_failed'`). Tasks 2–6 read/write exactly these.

- [ ] **Step 1: Apply the migration**

```sql
-- #97 full build: 'unreachable' joins the outcome map (no phone on record, or
-- Meta 131026 not-on-WhatsApp), and every decided row records WHY it decided.
alter table digest.olivia_intros drop constraint olivia_intros_status_check;
alter table digest.olivia_intros add constraint olivia_intros_status_check
  check (status in ('pending','accepted','declined','expired','unreachable'));
alter table digest.olivia_intros add column if not exists decided_reason text;
comment on column digest.olivia_intros.decided_reason is
  'tap = target tapped Accept/Decline · sweep = 7-day expiry · no_phone / wa_131026 / send_failed = unreachable causes (#97 ruling 2026-08-20)';
```

- [ ] **Step 2: Assert**

```sql
select conname, pg_get_constraintdef(oid) from pg_constraint
where conrelid='digest.olivia_intros'::regclass and conname='olivia_intros_status_check';
```
Expected: the CHECK lists all five statuses.

- [ ] **Step 3: Export schema and commit**

```bash
python3 scripts/db_export_schema.py
git add db/ && git commit -m "olivia_intros v2: unreachable status + decided_reason (#97 rulings)"
```

---

### Task 2: The intro route — `/api/olivia/intro` (all policy lives here)

**Files:**
- Create: `/Users/Born/mds-digest-web/src/app/api/olivia/intro/route.ts`
- Reference: `/Users/Born/mds-digest-web/src/app/api/olivia/schedule/route.ts` (copy its auth block verbatim: `OLIVIA_SCHEDULE_SECRET`/`OLIVIA_IOS_SECRET`, Bearer OR `X-Olivia-Secret`; copy its `sbRequest` helper import)
- Test: Task 3's curl matrix (route logic is thin I/O around SQL + Meta; the curl matrix IS the test)

**Interfaces:**
- Consumes: `digest.olivia_intros` (Task 1 shape) · `digest.olivia_recommendations(asker_at_id, recommended_at_id, lane, created_at)` · `digest.members(at_member_id, phone)` · `digest.member_profiles(at_fields->>'Full Name')` · env `META_WA_TOKEN`, `META_WA_PHONE_NUMBER_ID` · template `mds_intro_request`.
- Produces (JSON, consumed by the workflow branch in Task 4 and the seed tool in Task 5):
  - `POST {op:'request', phone, target_name?, topic?, dry_run?}` → `{ok, intro_id, sent:'consent_template'}` | `{ok:false, note}` (cap hit / not-in-log / unreachable — note text is member-ready) | `{ok:false, pick:[{id:'intro_pick_<intro-target-at-id>', title, description}], note}` when `target_name` is missing/ambiguous (up to 10 rows from the 30d log, equalizer-ordered).
  - `POST {op:'tap', phone, tap_id?, tap_text?}` → resolves BOTH tap kinds: `tap_text` in `('Accept intro','Decline')` = consent tap for that phone's newest pending intro; `tap_id` starting `intro_pick_` = a picker choice → runs `request` for that target. Returns `{ok, handled:true, reply}` where `reply` is the exact member-facing text the workflow should send, or `{handled:false}` when the tap is not intro-related.
  - `POST {op:'sweep'}` → expires pending rows older than 7 days, sends the verbatim expiry line to each requester, returns `{expired:n}`.

- [ ] **Step 1: Write the route.** Full skeleton (fill nothing in later — this is the logic):

```ts
import { NextRequest, NextResponse } from "next/server";
import { sbRequest, isSupabaseConfigured } from "@/lib/supabase-rest"; // same import the schedule route uses

const GRAPH = "https://graph.facebook.com/v22.0";
const TEMPLATE = "mds_intro_request";
const MAX_PENDING_PER_REQUESTER = 3;      // Andy default 2026-08-20
const MAX_PINGS_PER_TARGET_7D = 3;        // Andy default 2026-08-20
const EXPIRE_DAYS = 7;

function unauthorized() { return NextResponse.json({ error: "unauthorized" }, { status: 401 }); }
const z = (ts: string) => ts.replace("+00:00", "Z"); // PostgREST: '+' in a URL is a space

async function waSend(body: unknown) {
  const r = await fetch(`${GRAPH}/${process.env.META_WA_PHONE_NUMBER_ID}/messages`, {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.META_WA_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json() as Promise<{ messages?: Array<{ id: string }>; error?: { code?: number } }>;
}

export async function POST(req: NextRequest) {
  const secret = process.env.OLIVIA_SCHEDULE_SECRET || process.env.OLIVIA_IOS_SECRET;
  if (!secret) return NextResponse.json({ error: "secret not configured" }, { status: 500 });
  const bearer = (req.headers.get("authorization") || "") === `Bearer ${secret}`;
  const headerSecret = (req.headers.get("x-olivia-secret") || "") === secret;
  if (!bearer && !headerSecret) return unauthorized();
  if (!isSupabaseConfigured()) return NextResponse.json({ error: "supabase not configured" }, { status: 500 });

  const body = await req.json().catch(() => ({}));
  const op = String(body.op || "");
  const phone = String(body.phone || "").replace(/\D/g, "");

  // ---- shared lookups -----------------------------------------------------
  const memberByPhone = async (p: string) =>
    (await sbRequest<Array<{ at_member_id: string }>>(`members?select=at_member_id&phone=eq.${p}&limit=1`))[0] || null;
  const nameOf = async (atId: string) =>
    (await sbRequest<Array<{ at_fields: { ["Full Name"]?: string } }>>(
      `member_profiles?select=at_fields&at_member_id=eq.${encodeURIComponent(atId)}&limit=1`,
    ))[0]?.at_fields?.["Full Name"] || "an MDS member";
  const phoneOf = async (atId: string) =>
    (await sbRequest<Array<{ phone: string | null }>>(
      `members?select=phone&at_member_id=eq.${encodeURIComponent(atId)}&limit=1`,
    ))[0]?.phone || null;

  if (op === "request") {
    const me = await memberByPhone(phone);
    if (!me) return NextResponse.json({ ok: false, note: "asker is not a recognized member" });
    const since30 = z(new Date(Date.now() - 30 * 864e5).toISOString());
    // targets = ONLY people she recommended to THIS asker in 30d (Andy ruling)
    const recs = await sbRequest<Array<{ recommended_at_id: string; created_at: string }>>(
      `olivia_recommendations?select=recommended_at_id,created_at&asker_at_id=eq.${me.at_member_id}` +
      `&created_at=gte.${since30}&order=created_at.desc&limit=200`,
    );
    const candidateIds = [...new Set(recs.map((r) => r.recommended_at_id))];
    if (!candidateIds.length)
      return NextResponse.json({ ok: false, note: "I haven't recommended anyone to you recently — ask me who you should meet first, then I can make an intro." });

    // resolve the target: by name when given, else return the picker (<=10 rows)
    const profs = await sbRequest<Array<{ at_member_id: string; full_name: string | null }>>(
      `member_profiles?select=at_member_id,full_name&at_member_id=in.(${candidateIds.join(",")})`,
    );
    const wanted = String(body.target_name || "").trim().toLowerCase();
    const matches = wanted
      ? profs.filter((p) => (p.full_name || "").toLowerCase().includes(wanted))
      : [];
    if (!wanted || matches.length !== 1) {
      const attrs = await sbRequest<Array<{ at_member_id: string; main_niche: string | null; city: string | null }>>(
        `member_attributes?select=at_member_id,main_niche,city&at_member_id=in.(${candidateIds.slice(0, 10).join(",")})`,
      );
      const aBy = new Map(attrs.map((a) => [a.at_member_id, a]));
      return NextResponse.json({
        ok: false,
        pick: profs.slice(0, 10).map((p) => ({
          id: `intro_pick_${p.at_member_id}`,
          title: (p.full_name || "").slice(0, 24),
          description: [aBy.get(p.at_member_id)?.main_niche, aBy.get(p.at_member_id)?.city].filter(Boolean).join(" — ").slice(0, 72),
        })),
        note: "send this as a WhatsApp interactive LIST (10-row cap) titled 'Pick a member'; one tap = one consent request",
      });
    }
    const targetId = matches[0].at_member_id;

    // caps + pair-permanence (decline is FINAL)
    const mine = await sbRequest<Array<{ id: number; status: string; target_at_id: string }>>(
      `olivia_intros?select=id,status,target_at_id&requester_at_id=eq.${me.at_member_id}`,
    );
    if (mine.some((r) => r.target_at_id === targetId && r.status === "declined"))
      return NextResponse.json({ ok: false, note: `No connection with ${matches[0].full_name} yet — I'll let you know if that changes.` });
    if (mine.some((r) => r.target_at_id === targetId && r.status === "pending"))
      return NextResponse.json({ ok: false, note: "that request is already out — I'll tell you the moment they respond." });
    if (mine.filter((r) => r.status === "pending").length >= MAX_PENDING_PER_REQUESTER)
      return NextResponse.json({ ok: false, note: "you have 3 intro requests out already — let's hear back on those before sending more." });
    const since7 = z(new Date(Date.now() - 7 * 864e5).toISOString());
    const targetPings = await sbRequest<Array<{ id: number }>>(
      `olivia_intros?select=id&target_at_id=eq.${targetId}&created_at=gte.${since7}`,
    );
    if (targetPings.length >= MAX_PINGS_PER_TARGET_7D)
      return NextResponse.json({ ok: false, note: `${matches[0].full_name} has a few intro requests going already this week — want me to suggest someone else on this topic?` });

    // reachability (every-member-always: phone-less = unreachable, never skipped silently)
    const tgtPhone = await phoneOf(targetId);
    const topic = String(body.topic || "connecting at MDS").slice(0, 80);
    const first = (matches[0].full_name || "").split(/\s+/)[0] || "them";
    if (!tgtPhone) {
      await sbRequest(`olivia_intros`, { method: "POST", prefer: "return=minimal",
        body: [{ requester_at_id: me.at_member_id, target_at_id: targetId, topic, status: "unreachable", decided_reason: "no_phone", decided_at: new Date().toISOString() }] });
      return NextResponse.json({ ok: false, note: `I can't reach ${first} on WhatsApp. Want me to suggest someone else on ${topic} — or I can pass your request to the MDS team to make the intro by email?` });
    }
    if (body.dry_run) return NextResponse.json({ ok: true, dry_run: true, would_send_to: first, topic });

    const row = await sbRequest<Array<{ id: number }>>(`olivia_intros`, { method: "POST", prefer: "return=representation",
      body: [{ requester_at_id: me.at_member_id, target_at_id: targetId, topic }] });
    const requesterName = await nameOf(me.at_member_id);
    const send = await waSend({ messaging_product: "whatsapp", to: tgtPhone, type: "template",
      template: { name: TEMPLATE, language: { code: "en_US" }, components: [
        { type: "body", parameters: [
          { type: "text", text: first }, { type: "text", text: requesterName }, { type: "text", text: topic }] }] } });
    const wamid = send.messages?.[0]?.id;
    if (!wamid) {
      const reason = send.error?.code === 131026 ? "wa_131026" : "send_failed";
      await sbRequest(`olivia_intros?id=eq.${row[0].id}`, { method: "PATCH",
        body: { status: "unreachable", decided_reason: reason, decided_at: new Date().toISOString() } });
      return NextResponse.json({ ok: false, note: `I can't reach ${first} on WhatsApp. Want me to suggest someone else on ${topic} — or I can pass your request to the MDS team to make the intro by email?` });
    }
    await sbRequest(`olivia_intros?id=eq.${row[0].id}`, { method: "PATCH", body: { consent_wamid: wamid } });
    return NextResponse.json({ ok: true, intro_id: row[0].id, sent: "consent_template",
      note: `asked ${first} for their ok — I'll tell you the moment they respond (they see your name and the topic, nothing else)` });
  }

  if (op === "tap") {
    const tapText = String(body.tap_text || "").trim().toLowerCase();
    const tapId = String(body.tap_id || "");
    if (tapId.startsWith("intro_pick_")) {
      const targetId = tapId.slice("intro_pick_".length);
      const tgtName = await nameOf(targetId);
      // re-enter request with the resolved name (single unambiguous match by construction)
      const again = await fetch(req.url, { method: "POST",
        headers: { "x-olivia-secret": req.headers.get("x-olivia-secret") || "", "content-type": "application/json" },
        body: JSON.stringify({ op: "request", phone, target_name: tgtName, topic: body.topic || "connecting at MDS" }) });
      const out = await again.json();
      return NextResponse.json({ ok: true, handled: true, reply: out.note || "request sent" });
    }
    if (tapText !== "accept intro" && tapText !== "decline")
      return NextResponse.json({ handled: false });
    const me = await memberByPhone(phone);
    if (!me) return NextResponse.json({ handled: false });
    const pend = await sbRequest<Array<{ id: number; requester_at_id: string; target_at_id: string; topic: string }>>(
      `olivia_intros?select=id,requester_at_id,target_at_id,topic&target_at_id=eq.${me.at_member_id}&status=eq.pending&order=created_at.desc&limit=1`,
    );
    if (!pend.length) return NextResponse.json({ handled: false });
    const it = pend[0];
    const verdict = tapText === "accept intro" ? "accepted" : "declined";
    await sbRequest(`olivia_intros?id=eq.${it.id}`, { method: "PATCH",
      body: { status: verdict, decided_reason: "tap", decided_at: new Date().toISOString() } });
    const reqName = await nameOf(it.requester_at_id);
    const reqPhone = await phoneOf(it.requester_at_id);
    const tgtFirst = (await nameOf(it.target_at_id)).split(/\s+/)[0];
    if (verdict === "accepted") {
      await waSend({ messaging_product: "whatsapp", to: phone, type: "text",
        text: { preview_url: false, body: `Great — you're connected with ${reqName}. Start the conversation: wa.me/${reqPhone}` } });
      if (reqPhone) await waSend({ messaging_product: "whatsapp", to: reqPhone, type: "text",
        text: { preview_url: false, body: `${tgtFirst} accepted your intro request — start the conversation: wa.me/${phone}` } });
      return NextResponse.json({ ok: true, handled: true, reply: "" }); // links already sent; workflow sends nothing extra
    }
    if (reqPhone) await waSend({ messaging_product: "whatsapp", to: reqPhone, type: "text",
      text: { preview_url: false, body: `No connection with ${tgtFirst} yet — I'll let you know if that changes.` } });
    return NextResponse.json({ ok: true, handled: true,
      reply: "No problem — I won't share your details, and they'll simply hear the intro didn't happen." });
  }

  if (op === "sweep") {
    const cutoff = z(new Date(Date.now() - EXPIRE_DAYS * 864e5).toISOString());
    const stale = await sbRequest<Array<{ id: number; requester_at_id: string; target_at_id: string; topic: string }>>(
      `olivia_intros?select=id,requester_at_id,target_at_id,topic&status=eq.pending&created_at=lt.${cutoff}`,
    );
    for (const it of stale) {
      await sbRequest(`olivia_intros?id=eq.${it.id}`, { method: "PATCH",
        body: { status: "expired", decided_reason: "sweep", decided_at: new Date().toISOString() } });
      const reqPhone = await phoneOf(it.requester_at_id);
      const first = (await nameOf(it.target_at_id)).split(/\s+/)[0];
      if (reqPhone) await waSend({ messaging_product: "whatsapp", to: reqPhone, type: "text",
        text: { preview_url: false,
          body: `I didn't get a response from ${first} this week, so I've let it rest. Want me to try again later — or introduce you to someone else on ${it.topic}?` } });
    }
    return NextResponse.json({ ok: true, expired: stale.length });
  }

  return NextResponse.json({ error: "unknown op" }, { status: 400 });
}
```
Adapt imports to whatever the schedule route actually uses (read it first — `sbRequest` may live inline there; copy the same pattern rather than inventing a lib).

- [ ] **Step 1b (ELIGIBILITY, locked 2026-08-21 — the skeleton above predates it):** weave the eligibility constraint into `op:'request'`: requester check immediately after `me` resolves (fail → the requester-ineligible verbatim line); target check immediately after `targetId` resolves, BEFORE caps (fail → the target-ineligible verbatim line, no ledger row). Also filter the PICKER candidate list to eligible targets only — the list must never offer someone the request would then refuse. Helper `isEligible(atId)` = Millie-user AND Summit-registered per the Global Constraint; take exact table/column names from the Scorecard repo's `db/` schema export — verify, never guess. The `op:'tap'` consent path needs NO eligibility re-check (a pending row only exists if both passed at request time).

- [ ] **Step 2: Typecheck**

Run: `cd /Users/Born/mds-digest-web && npx tsc --noEmit -p tsconfig.json`
Expected: exit 0.

- [ ] **Step 3: Commit (git author must be andy.verdy1@gmail.com — Vercel requirement)**

```bash
cd /Users/Born/mds-digest-web && git add src/app/api/olivia/intro/route.ts \
  && git commit -m "#97: intro route - request/pick/tap/sweep, all rulings in code" && git push origin main
```

---

### Task 3: Route verification matrix (curl, no member touched)

**Files:**
- Test: curl against `https://digest.mds.co/api/olivia/intro` (secret from `.env.local` `OLIVIA_SCHEDULE_SECRET`/`OLIVIA_IOS_SECRET`; header `X-Olivia-Secret`)

**Interfaces:**
- Consumes: Task 2 route, deployed (poll until live). PREREQUISITE: Andy added the Meta env vars + redeployed — verify first with the dry-run case; a 500 "secret not configured"-style miss means the env is absent.

- [ ] **Step 0: Eligibility canary** — Andy is NOT Summit-registered (his canary was deleted): first call `{op:'request', phone:'17866578153'}` → expect the requester-ineligible line (this IS the requester-filter test). Then insert the CANARY registration row for Andy on `recrATwhUDA55iQN5` (same SQL shape as the #99 canary) — steps 1-6 run under it — and DELETE it at matrix end, same session.
- [ ] **Step 1: Picker case** — Andy's phone, no target: `{op:'request', phone:'17866578153'}` → expect `pick:[...]` rows (≤10, ids `intro_pick_rec…`, eligible targets only), NO phone digits anywhere in the response.
- [ ] **Step 2: Dry-run named case** — `{op:'request', phone:'17866578153', target_name:'<a name from the picker>', topic:'plan test', dry_run:true}` → `{ok:true, dry_run:true}` and NOTHING sent (verify no new `olivia_sends` row).
- [ ] **Step 3: Cap case** — insert 3 pending rows for Andy via SQL, re-run step 2 without dry_run → expect the "3 intro requests out already" note, no send. Delete the 3 rows after.
- [ ] **Step 4: Decline-permanence case** — insert a `declined` row for Andy→(picker member) via SQL, request that member → expect the verbatim "No connection with … yet" note. Delete after.
- [ ] **Step 5: tap non-intro** — `{op:'tap', phone:'17866578153', tap_text:'hello'}` → `{handled:false}`.
- [ ] **Step 6: sweep no-op** — `{op:'sweep'}` → `{expired:0}` (no stale rows).
- [ ] **Step 7: Commit nothing (read-only matrix); record results in the session log.**

---

### Task 4: Workflow branch — swallow intro taps BEFORE the LLM lane (staging → Andy promotes)

**Files:**
- Modify: staging workflow `bqHstPDi84uOhTCJ` via `python3 scripts/olivia_wf.py lock` + n8n MCP edits (never touch prod `12wj6h1TWqb0d4Dq` directly)
- Test: staging probes in Step 4

**Interfaces:**
- Consumes: inbound webhook items; Task 2 `op:'tap'` contract.
- Produces: taps never reach `Ask Claude`/`Answer Claude`; the route's `reply` (when non-empty) goes out via the existing send path.

- [ ] **Step 1: Andy (or lock-permitting session) takes the lock:** `python3 scripts/olivia_wf.py lock`.
- [ ] **Step 2: Add two nodes to STAGING** (positions near `Drop Duplicates`):
  - `Intro Tap?` — Code node AFTER `Drop Duplicates`, before `Find Member`: inspect the raw message; set `intro_tap=true` when `type==='button'` and `button.text` ∈ {'Accept intro','Decline'}, OR `type==='interactive'` and `interactive.list_reply.id` starts with `intro_pick_`. Pass `tap_text` / `tap_id` / sender phone through.
  - `Intro Route (HTTP)` — POST `https://digest.mds.co/api/olivia/intro` with `{op:'tap', phone, tap_text, tap_id}` + header `X-Olivia-Secret` (same credential the Answer Tool node uses). When the response has `handled:true` and a non-empty `reply`, wire it into the existing `Send Reply (Meta)` input shape; when `handled:false`, fall through to the normal `Find Member` path (an unrelated button keeps working).
  - Wire: `Drop Duplicates` → `Intro Tap?` → (intro) `Intro Route` → `Send Reply (Meta)` / (not intro) `Find Member`. **v1 branch order rule:** wire the intro branch FIRST.
- [ ] **Step 3: `node --check` any Code-node JS before writing it into the node** (the seed-write rule applies to all workflow JS).
- [ ] **Step 4: Staging probes:** simulate a button tap by POSTing a crafted webhook body to the staging webhook (copy a real `msg_type='button'` payload from `digest.olivia_webhook_events`, swap the wamid): expect route hit + NO LLM turn in `olivia_messages` for that wamid. Then a plain "hello" probe: expect the normal LLM answer (fall-through intact).
- [ ] **Step 5: Gate + snapshot:** `python3 scripts/olivia_leak_gate.py` EXIT 0 · `python3 scripts/olivia_wf.py snapshot`.
- [ ] **Step 6: Andy runs `promote`.** Post-promote: one real tap on Andy's phone end-to-end.

---

### Task 5: The `member_intro` seed tool — "connect us" becomes a first-class ask (staging → Andy promotes)

**Files:**
- Modify: staging workflow `Answer Seed` (tool list + rules) and `Answer Tool` (URL map) — same lock/stage/promote cycle as Task 4 (fold into the same staging session if convenient; still its own probes)
- Test: staging probes in Step 3

**Interfaces:**
- Consumes: Task 2 `op:'request'` contract.
- Produces: tool `member_intro` with `input_schema {target_name?: string, topic?: string}`; Answer Tool maps it to `https://digest.mds.co/api/olivia/intro` exactly the way `event_*`/`org_docs` map (op injected as `request`, phone injected from `Resolve Member`).

- [ ] **Step 1: Answer Tool URL map** — extend the ternary: `tool_name === 'member_intro' ? 'https://digest.mds.co/api/olivia/intro' : …` and in the body expression inject `{op:'request', phone}` alongside the tool args (mirror the event_ pattern that already injects phone).
- [ ] **Step 2: Answer Seed** — add the tool + two rules, exact text:
  - Tool: `{ name: 'member_intro', description: 'CONSENT-FIRST INTRO: when the member asks to be connected/introduced to someone I recommended ("connect us", "intro me to X", "can you message them"). NEVER share numbers or wa.me links yourself - this tool asks the OTHER member for consent first. target_name optional: omit it and the tool returns a pick list to send as an interactive LIST message.', input_schema: S({ target_name: str('who, from my recent recommendations'), topic: str('what the intro is about') }) }`
  - Rule: `'- INTROS ARE CONSENT-FIRST (#97): on "connect us / intro me / message them for me" call member_intro. Never output a phone number or wa.me link from memory or any other tool - only the intro flow may share contact, and only after the other member accepts. One person per request; "connect me with all of them" gets a friendly no + the pick list.'`
- [ ] **Step 3: Staging probes** (single-question tier, free): `"reset"`, `"connect me with <name from Andy's picker>"` → expect a member_intro tool call in the execution + the route's note as her reply, dry-run NOT set (staging probe = real template to that target — so probe with **Andy as the named target**: he is in his own rec log? If not, first ask staging "who should I meet…" to seed the log, then request a listed member with `dry_run` forced ON via a temporary route guard? NO — simpler: temporarily set `MAX_PINGS…` aside and probe with target = Andy by inserting `recCUUw8iiUnJjac1` into his own rec log via SQL, so the template goes to Andy's phone only). **Eligibility (locked 2026-08-21): the canary registration row for Andy on `recrATwhUDA55iQN5` must exist for this probe (both sides = Andy) — insert before, DELETE after, same session.** Verify: her reply says she asked for the ok; `olivia_intros` has the pending row; nothing went to any other member.
- [ ] **Step 4: Gate EXIT 0 · snapshot · Andy promotes** (with Task 4 if staged together).

---

### Task 6: The sweep tick + retire the POC scripts

**Files:**
- Modify: n8n `QhJw46Mr7LAP8fdz` ("Olivia — Reminder Sender", every minute) — add ONE HTTP node `Intro Sweep` after the reminder chain: POST the intro route `{op:'sweep'}` with the `X-Olivia-Secret` header, `onError: continueRegularOutput` (a sweep failure must never break reminders). ONE `[{deactivateWorkflow},{activateWorkflow}]` bounce, never deactivate-first.
- Delete: `scripts/olivia_intro_poc.py` (superseded; the route owns the flow) — keep `scripts/olivia_intro_template.py` (status checks stay useful).
- Test: Step 2.

**Interfaces:**
- Consumes: Task 2 `op:'sweep'`.

- [ ] **Step 1: Add the node + bounce the workflow.**
- [ ] **Step 2: Verify live:** insert a pending row backdated 8 days (SQL, Andy as requester+target), wait one tick, assert: row `expired/sweep`, Andy's phone got the verbatim expiry line, exec id recorded. Delete the test row's messages? No — leave the ledger row as the proof; note the exec id.
- [ ] **Step 3: Retire POC:** `git rm scripts/olivia_intro_poc.py && git commit -m "#97: POC script retired - the intro route owns the flow"`.

---

### Task 7: Gate checks + docs + close

**Files:**
- Modify: `scripts/olivia_leak_gate.py` · `OLIVIA_HANDBOOK.md` (§7.4 consumers + §8 route table) · `OLIVIA_SPRINT_4.md` (#97 close block) · `OLIVIA_NEXT_SESSION.md` · `SESSION_LOG_OLIVIA.md` + `SESSION_LOG.md` index
- Test: the gate run IS the test.

- [ ] **Step 1: Three new gate checks** (pattern: existing route checks; use the real secret from env):
  1. intro route without secret → 401.
  2. `{op:'request', phone:<unknown>}` → no `pick`, no send ("asker is not a recognized member" path).
  3. `{op:'request', phone:<probe>, dry_run:true}` with a named target → response JSON contains **no digit-run longer than 7** (no phone ever leaves before accept) — regex `\d{8,}` absent.
- [ ] **Step 2: Run** `python3 scripts/olivia_leak_gate.py; echo EXIT=$?` → EXIT=0.
- [ ] **Step 3: Docs:** handbook gains the intro flow (rulings verbatim from Global Constraints); board close block with AC checklist + before/after (POC loop → member-facing flow; 0 → N intros processed); handoff + logs; one commit.
- [ ] **Step 4: Accept when (the ticket's ACs):** Andy's ruling recorded ✅ (this plan) · consent flow live E2E on a phone · out-of-window template approved ✅ (`mds_intro_request`) · declines final and polite (Task 3 step 4 + Task 2 code) · gate GREEN.

---

## Self-review (done at write time)

- Spec coverage: every ruling from tonight's session maps to code — cap-from-log + picker (T2 request), one-pick-one-request (seed rule, T5), decline-final + verbatim lines (T2), 7d expiry + zero reminders (T2 sweep, T6 tick), unreachable + every-member-always (T2), tap interception before LLM (T4), 3/3 caps (T2 constants), no-number-before-accept (T2 + gate T7).
- Known unknowns made explicit: Vercel env presence (prereq + T3 step 1), `sbRequest` import location (T2 note), Andy-in-own-log probe trick (T5 step 3), lock availability (T4 step 1 fallback to Andy).
- Type consistency: `intro_pick_<at_member_id>` ids are produced by T2 request and consumed by T2 tap and T4 branch; `handled/reply` contract identical in T2 and T4; status enum matches T1 everywhere.
- Placeholder scan: every step carries real code, real strings, real expected outputs; the verbatim member-facing lines appear once in Global Constraints and again inside T2 code.
