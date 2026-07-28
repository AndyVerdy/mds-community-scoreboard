> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Supabase Member-360 — Schema Proposal

> **Status: PROPOSAL. Nothing has been executed.** Written 2026-07-09.
> Scope: `digest` schema in Supabase project `nadtudwuwjhckotrngzn`.
> Trigger: WA DB ↔ Members DB audit. Supabase is meant to be the member-360 warehouse for
> WhatsApp **+ video summaries + FB summaries + future sources** — the current schema cannot absorb them.

---

## 1. Where we are today (verified, not assumed)

### `digest` schema — 5 tables

| Table | Rows | Notes |
|---|---|---|
| `members` | **514** | one row per **WhatsApp sender**, PK = `airtable_id` (the **WA-DB row id**) |
| `summaries` | 1078 | read-only AT mirror; members referenced only as free text |
| `wa_messages` | **0** | modeled ("who said what"); **Supabase** ingestion never switched on — but see ⚠ note below: the raw IS already stored in Airtable |
| `member_events` | **0** | in-app actions, never switched on |
| `member_sessions` | 35 | portal session telemetry |

> **⚠ Correction (2026-07-10):** an earlier draft said the pipeline "discards raw messages / who-said-what is not stored." **That is wrong.** The daily digest already stores the full conversation in **Airtable `Summaries`** — `raw_log` (formatted transcript with names) + `source_messages_json` (raw Whapi payload: phone, `from_name`, text, timestamp, chat_id), one blob per chat/day. So populating `digest.wa_messages` is a **parse/backfill of existing data** (history recoverable), not new capture. Two bugs to fix in that parse: `source_messages_json` is `JSON.stringify(...).slice(0, 95000)` → busy days become **invalid JSON**; and `raw_log` carries names, not phones, so attribute from `source_messages_json` instead.

### Every foreign key points at the WhatsApp row, not the member

```
wa_messages.sender_member  → members.airtable_id
member_sessions.member     → members.airtable_id
member_events.member       → members.airtable_id
```

### `digest.members` column semantics (misleading names)

| Column | What it actually is | Filled |
|---|---|---|
| `airtable_id` (PK) | **WA-DB** `Members` row id (`tbli8B589iNbsGF0Z`) | 514 |
| `phone` | WhatsApp phone (digits) | 504 |
| `name` | **WhatsApp handle / pushname** (e.g. `Prem`) — *not* the real name | 294 |
| `crm_member_id` | ⚠️ **MISNAMED + WRONG ID.** Mirror writes `crm_member_id: first(f.Member)` — i.e. the **`Member` link = the SYNCED-COPY record id** (`tblUlfrPXjJtrPS0L`), **not** the Members-DB id. `src/lib/supabase.ts:169` reads it back as `Member: [r.crm_member_id]`. | 445 |
| `membership_status` | AT Database Status, mirrored | 442 |
| *(none)* | **the real name (`Member Full Name`)** | ⛔ **absent** |
| *(none)* | **a stable Members-DB record id (`source_member_id`)** | ⛔ **absent** |

> **Verified 2026-07-10** (row-level diff, all 515 rows): rows 515↔515, **email drift 0**, **status drift 0**, but **`crm_member_id` differs from `source_member_id` on all 446 matched rows**. Example: Oran → Airtable `source_member_id` = `recIkCERUPNZ1y4LZ` (exists in Members DB); Supabase `crm_member_id` = `recuNMFLkSNgeH7aN` (exists ONLY in the synced copy).
>
> **Why this is dangerous:** synced-copy record ids **regenerate whenever the synced table re-syncs** (a Members-DB schema change does it — the documented 438→0 link wipe). So *any* FK or cross-source join built on `crm_member_id` silently breaks. It is unusable as the member-360 key.

Plus WhatsApp/portal-specific state on the same row: `channels_present`, `channel_subscriptions`,
`msgs_7d`, `msgs_30d`, `wa_last_active_at`, `otp_code_hash`, `delivery_email`, `onboarding_*`, …

### The three structural problems

1. **`members` is not a members table.** It is the WhatsApp sender list (514) wearing the name
   "members". The Members DB holds ~5.5k members. A member active on **Facebook or video but not
   WhatsApp has no row to attach to.** FB/video would be forced to mint fake WA rows or build a
   second parallel members table.
2. **The canonical key is WhatsApp-shaped.** Everything FKs to `airtable_id` (a WA row id). The
   stable, source-agnostic key is the **Members-DB record id** — already what the Scorecard and the
   FB layer join on.
3. **Identity and per-source state are fused.** Real-name/email/status (member facts) sit in the same
   row as WhatsApp channel presence, message counts, and portal OTP/onboarding state.

Corollary: 69 of the 514 rows have **no** `crm_member_id` — they are WhatsApp identities with no
member behind them (unmatched senders / guests). They still send messages, so they must be
representable.

---

## 2. Target model

Three concerns, three tables.

### 2.1 `members` — canonical identity (source-agnostic)

One row per **Members-DB member** (~5.5k), not per WhatsApp sender.

```sql
create table digest.members (
  at_member_id      text primary key,          -- Members-DB record id (tblfwOSROSHfuYUxv)
  full_name         text,                      -- Member Full Name  (the REAL name)
  preferred_email   text,
  membership_status text,                      -- AT Database Status
  synced_at         timestamptz not null default now()
);
```

### 2.2 `member_identities` — the per-source mapping

One row per (member, source). **This is the WA id / WA phone / WA name / AT name / AT id mapping**,
and it is what lets FB, video, and future sources attach with **zero schema churn**.

```sql
create table digest.member_identities (
  id            bigserial primary key,
  source        text not null,                 -- 'whatsapp' | 'facebook' | 'video' | ...
  external_id   text not null,                 -- WA: phone   FB: userId   video: its own id
  display_name  text,                          -- WA: handle/pushname   FB: profile name
  at_member_id  text references digest.members(at_member_id),  -- NULLABLE: unmatched identity
  wa_row_id     text,                          -- optional provenance (the old airtable_id)
  first_seen_at timestamptz default now(),
  last_seen_at  timestamptz,
  unique (source, external_id)
);
```

Why nullable `at_member_id`: the 69 unmatched WhatsApp senders (and group guests) are real
identities with no member. They get a row here and resolve later when the matcher links them —
**without** touching any message rows.

### 2.3 Per-source state (unchanged in spirit, re-keyed)

WhatsApp/portal-specific fields move out of canonical `members`:

```sql
create table digest.wa_member_state (
  identity_id  bigint primary key references digest.member_identities(id),
  channels_present text[], channel_subscriptions jsonb,
  msgs_7d int, msgs_30d int, wa_last_active_at timestamptz,
  email_subscribed boolean, email_format_preference text, digest_min_activity text,
  delivery_email text, delivery_email_verified boolean,
  otp_code_hash text, otp_expires_at timestamptz,
  onboarding_scope text, onboarding_complete boolean, onboarding_banner_dismissed boolean
);
```

### 2.4 Event/content tables FK to the **identity**, roll up to the **member**

A message is sent by a *WhatsApp identity*, which may or may not be a known member:

```sql
-- wa_messages.sender_identity → member_identities(id)
-- future: fb_posts.author_identity → member_identities(id)
-- future: video_views.viewer_identity → member_identities(id)
```

Member-level analytics = `event → member_identities → members`. Unmatched senders simply have a
null `at_member_id` and fall out of member rollups — no fake rows, no data loss.

---

## 3. Name resolution (be honest about coverage)

There is **no** clean "use real names instead of WA names" swap. Coverage today:

| Source | Coverage (of 514 WA rows) |
|---|---|
| `Member Full Name` (real) | **445** |
| WA handle `name` | 294 |
| neither (phone only) | remainder |

Also: the WA handle **differs** from the real name in **143 of the 270** rows that have both
(e.g. real `Yevgeniy Khayman` → handle `Eugene Khayman`; `Tuan Hung Ngo` → `Hung`).

**Mandated cascade** (single helper, used everywhere — digest, portal, stats, summaries):

```
display_name = full_name            (Members DB, real)
            ?? identity.display_name (WA handle / pushname)
            ?? 'Member-N'            (stable anonymized token)
```

Today the digest (`qo3qzeVtprhTW88F` → `labelFor`) has this **inverted**: pushname first, real name
never (its `Load Members` node does not even fetch `Member Full Name`).

---

## 4. Migration path (each phase independently safe)

**Timing matters:** `wa_messages` and `member_events` are **empty (0 rows)**. Re-keying is nearly free
*now* and gets expensive the moment message capture turns on or FB/video data lands.

| Phase | Change | Breaks? |
|---|---|---|
| **0** | Add **two** columns to `digest.members`: `full_name` (mirror `Member Full Name`) **and `at_member_id` (mirror `source_member_id` — the stable Members-DB id, which Supabase does not have today)**. One-line change each in `Oy7RYcgLfDYhrPvw` → `Map to Supabase rows`. **Leave `crm_member_id` alone** — `src/lib/supabase.ts:169` reconstructs `Member: [r.crm_member_id]` from it. | **Nothing.** Purely additive. Unlocks real names *and* the stable join key. |
| **1** | Create `member_identities`; backfill from `members` (`source='whatsapp'`, `external_id=phone`, `display_name=name`, `at_member_id=crm_member_id`, `wa_row_id=airtable_id`). | **Nothing.** Additive; old table untouched. |
| **2** | Create canonical `members_v2` keyed on `at_member_id`; populate from the Members DB (all ~5.5k). Repoint `wa_messages` + `member_events` FKs to `member_identities` (**free — both empty**). Migrate `member_sessions` (35 rows). | Low. Reads still hit the old table until Phase 4. |
| **3** | Move WA/portal state into `wa_member_state`. | Medium — see §5. |
| **4** | Repoint digest-web reads; drop the old table; rename. | See §5. |

Phase 0 alone fixes the user-visible name problem. Phases 1–2 buy the FB/video future. Phases 3–4
are cleanup and can wait.

---

## 5. What breaks in `mds-digest-web` (per code audit)

Everything below reads Supabase only when `MEMBER_SOURCE=supabase` (set on Render).

| Area | File | Impact |
|---|---|---|
| Member row shape | `src/lib/supabase.ts` (`MemberRow`, `rowToMember` ~:137-192) | Shape changes; must map `full_name`. Today `rowToMember` never populates `Member Full Name`. |
| Mirror writer | `src/lib/supabase.ts` (`upsertMemberFromAirtable` ~:216) | Writes only the WA handle `name`; must also write `full_name`. |
| Lookups | `src/lib/supabase.ts` (`resolveMemberByEmail` / `ByPhone` / `BySessionHash` ~:301-328, :467-499) | `phone` moves to `member_identities` → these become a join (Phase 3+). Email/session stay on the member/state row. |
| Member's own name | `src/app/api/me/route.ts:67` (`name: f.name`) → dashboard `:815, :1050` | **Bug today:** shows the member their WhatsApp handle. Fix in Phase 0. |
| Access gating | `src/lib/airtable.ts` (`memberLiveStatus` :101-104, `isMemberAllowed` :113-125) | Unaffected — status mirrors to `membership_status` and maps back. |
| Login / admin | `src/lib/airtable.ts` (`findMemberByEmail` :127-136), `src/lib/admin/access.ts:17-27` | Unaffected by Phase 0–2 (email-keyed; admin path reads Airtable directly). |
| Delivery email | onboarding + `/api/me` | Contract `delivery_email || email` preserved; field moves in Phase 3. |
| Dead code | `src/lib/airtable.ts:70` declares `Member Full Name`, read nowhere | Becomes live in Phase 0. |

### n8n impact

| Workflow | Impact |
|---|---|
| `Oy7RYcgLfDYhrPvw` — Supabase Mirror (Members) | Must mirror `Member Full Name` (Phase 0), then write identities (Phase 1). |
| `qo3qzeVtprhTW88F` — WA Digest Daily | `Load Members` must fetch `Member Full Name`; `labelFor` cascade inverted (§3). |
| `1VDbwlQqXcfbotic` — Daily Stats Builder | Writes `Member Name` snapshot — should write the real name. (Today: mix of real / handle / raw phone.) |
| `RPfnori7C26NcT9N` — Scorecard WA Sync | Keys DailyActivity by `member_phone`; unaffected. |
| `9D2pdDHc2WjKyZVp` — Supabase Mirror (Summaries) | Summaries have **no member FK** — only free-text `notable_members`. Optional: emit identity ids. |

---

## 6. Open decisions (for Andy)

1. **Canonical key** — confirm `at_member_id` (Members-DB record id) as the cross-source member key.
   It is already what the Scorecard and FB layer join on.
2. **Scope of canonical `members`** — all ~5.5k Members-DB members, or only members seen in at least
   one source? (All is simpler and future-proof; costs a bigger mirror.)
3. **Unmatched identities** — confirm nullable `at_member_id` on `member_identities` (vs. dropping
   unmatched senders entirely).
4. **Summaries** — keep free-text `notable_members`, or emit structured identity ids so "who said
   what" is queryable?
5. **`wa_messages` ingestion** — still gated on a **privacy call**. Schema is ready; turning it on is
   a separate decision.
6. **Naming** — rename misleading columns (`name` → `wa_display_name`, `crm_member_id` →
   `at_member_id`). "CRM" is not MDS terminology (it's the **Members DB**).

---

## 7. Recommendation

Do **Phase 0 now** (additive, zero breakage) — it fixes the real, user-visible defect: members and
digests showing WhatsApp handles instead of real names.

Do **Phases 1–2 before** message capture is switched on or FB/video data lands — while
`wa_messages` and `member_events` are still empty and re-keying costs nothing.

Defer Phases 3–4.
