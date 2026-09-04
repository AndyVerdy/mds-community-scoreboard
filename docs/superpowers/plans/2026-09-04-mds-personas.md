# MDS Personas (#161) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A staff-only `/personas` area in the digest portal (mds-digest-web) — library of member faces, a member "character sheet" with the 18 categories and 33 detail stats, and a cohort page per stat — built to the Claude Design handoff, running locally first.

**Architecture:** Three Next.js server pages under `src/app/personas/` with their own layout (staff gate, scoped design tokens, fonts). Four PostgREST RPCs in the `digest` schema shape the view models in SQL (library cards, one sheet, one cohort, similar + companions) so the numbers are the same ones Millie's lanes use. Pure TypeScript helpers (`src/lib/personas/model.ts`) hold every formatting rule and are unit-tested. Two Scorecard jobs feed the two fields the warehouse lacks: cached photos (`member_photos` + Storage) and a short persona `blurb`.

**Tech Stack:** Next.js 16 (app router, server components), React 19, Tailwind 4 with CSS variables, vitest, PostgREST RPCs on Supabase (`digest` schema), Python 3 scripts in `/Users/Born/Scorecard/scripts` for jobs.

## Global Constraints

- Staff only: every `/personas*` request passes the same gate as `/admin` — a session cookie whose email ends with `@mds.co`; anything else redirects to `/`.
- Population = `digest.member_profiles.status IN ('Current Member','New Member','Current Member- Not Renewing','Current Member- Paused','Staff')`, keyed by `at_member_id`. Never by phone.
- Stat value = `round(pct*100)`, peak = `min(100, round(value * peak_score/score))` when `peak_score > score` else value; badge = `at peak` when `score >= peak_score`, `holding` when `score >= 0.85*peak_score`, else `fading`.
- Strong = value ≥ 70 (gold), chip gold = category ≥ 80, cohort = value ≥ 60, companions = ≥ 75 on an ask stat, level = mean of the member's top-3 category values.
- Fonts: Instrument Sans (500/600/700) display, IBM Plex Sans (400/500/600) body, IBM Plex Mono (500) numbers — via `next/font/google`. No serif faces anywhere.
- Design values (colors, sizes, radii, states, responsive breakpoints 1180 / 1000 / 640) come from `docs/design/mds-personas/README.md` in mds-digest-web; copy them, do not invent.
- Never link an Airtable attachment URL from the UI (they expire). Photos come from Supabase Storage or an initials tile.
- Repos stay separate: pages and components in `/Users/Born/mds-digest-web`; SQL exports and jobs in `/Users/Born/Scorecard`. One branch per session in each: `personas-20260904`.
- Commit messages end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. mds-digest-web commits use `git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com"`; Scorecard commits use `GIT_AUTHOR_NAME="A Verdy" GIT_AUTHOR_EMAIL="Born@MacBook-Pro-9.local"` (and the same committer vars).
- Local first: nothing merges to `main` of mds-digest-web (Render deploys on push) until Andy says so. Verify on `npm run dev` with headless screenshots (`~/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell --headless --screenshot=… --window-size=1440,1200 http://localhost:3000/personas`); the Browser pane does not hydrate Next pages.

---

## File structure

mds-digest-web (`/Users/Born/mds-digest-web`):
- `docs/design/mds-personas/{README.md, MDS Personas.dc.html, support.js}` — the handoff, unzipped (reference only).
- `src/app/personas/layout.tsx` — staff gate, fonts, `.theme-dark` root, top bar shell.
- `src/app/personas/personas.css` — the token set from README "Design tokens" (dark + light) and the few global rules of the handoff.
- `src/app/personas/page.tsx` — Library (server) + `src/app/personas/LibraryClient.tsx` (client: search, rails).
- `src/app/personas/[id]/page.tsx` — Member sheet.
- `src/app/personas/stat/[key]/page.tsx` — Cohort.
- `src/app/personas/dev/components/page.tsx` — component sheet for review (dev only).
- `src/lib/personas/gate.ts` — `isStaffEmail`.
- `src/lib/personas/model.ts` (+ `model.test.ts`) — types and every formatting rule.
- `src/lib/personas/data.ts` — typed RPC wrappers.
- `src/components/personas/{InitialsTile,PortraitCard,Chip,StatusDot,StatBar,StatRow,SearchBar,RailHeader,CohortCard,Rail}.tsx`.

Scorecard (`/Users/Born/Scorecard`):
- `db/functions/personas_*.sql` — exported after the migrations (run `python3 scripts/db_export_schema.py`).
- `scripts/cache_member_photos.py` (+ `scripts/tests/test_cache_member_photos.py`) — nightly photo cache.
- `scripts/persona_blurbs.py` (+ `scripts/tests/test_persona_blurbs.py`) — nightly blurb writer.
- `scripts/nightly_derivations.py` — two new steps.
- `OLIVIA_SPRINT_4.md`, `OLIVIA_HANDBOOK.md`, `SESSION_LOG_OLIVIA.md` — docs.

---

### Task 1: Route shell — gate, tokens, fonts, handoff files

**Files:**
- Create: `src/lib/personas/gate.ts`, `src/lib/personas/gate.test.ts`
- Create: `src/app/personas/layout.tsx`, `src/app/personas/personas.css`, `src/app/personas/page.tsx` (placeholder, replaced in Task 7)
- Create: `docs/design/mds-personas/` (unzip `~/Downloads/Member 360 Admin Design System.zip` → the three files)

**Interfaces:**
- Produces: `isStaffEmail(email: string | null | undefined): boolean`; CSS custom properties `--bg --surface --surface-2 --surface-3 --track --border --border-strong --text --text-2 --muted --faint --accent --accent-text --accent-weak --accent-border --strong --strong-text --strong-weak --strong-border --below --below-text --below-weak --below-border --peak --peak-text --peak-weak --peak-border --holding --holding-text --fading --fading-text --fading-weak --fading-border --scrim --shadow --card-shadow --font-display --font-body --font-mono` on `.theme-dark` / `.theme-light`.

- [ ] **Step 1: Write the failing gate test**

```ts
// src/lib/personas/gate.test.ts
import { describe, it, expect } from "vitest";
import { isStaffEmail } from "./gate";

describe("isStaffEmail", () => {
  it("accepts @mds.co, any case, trimmed", () => {
    expect(isStaffEmail("andy@mds.co")).toBe(true);
    expect(isStaffEmail("  Belen@MDS.CO ")).toBe(true);
  });
  it("rejects members, look-alikes and empties", () => {
    expect(isStaffEmail("someone@gmail.com")).toBe(false);
    expect(isStaffEmail("x@mds.co.evil.com")).toBe(false);
    expect(isStaffEmail("")).toBe(false);
    expect(isStaffEmail(null)).toBe(false);
  });
});
```

- [ ] **Step 2: Run it, expect failure**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/personas/gate.test.ts`
Expected: FAIL — cannot find module `./gate`.

- [ ] **Step 3: Implement the gate helper**

```ts
// src/lib/personas/gate.ts
/** The same rule as src/app/admin/layout.tsx: only MDS staff (@mds.co logins) see /personas. */
export function isStaffEmail(email: string | null | undefined): boolean {
  const e = (email || "").trim().toLowerCase();
  return e.length > "@mds.co".length && e.endsWith("@mds.co");
}
```

- [ ] **Step 4: Run the test, expect pass**

Run: `npx vitest run src/lib/personas/gate.test.ts` — Expected: 2 passed.

- [ ] **Step 5: Unzip the handoff and write the token sheet**

```bash
mkdir -p /Users/Born/mds-digest-web/docs/design/mds-personas
cd /Users/Born/mds-digest-web/docs/design/mds-personas && unzip -o -j "/Users/Born/Downloads/Member 360 Admin Design System.zip"
```

`src/app/personas/personas.css` — copy the two token blocks verbatim from README "Design tokens" (they are also the first `<style>` block of `MDS Personas.dc.html`), then add:

```css
.personas-root { background: var(--bg); color: var(--text); min-height: 100vh; font-family: var(--font-body); font-size: 14.5px; line-height: 1.5; -webkit-font-smoothing: antialiased; }
.personas-root * { box-sizing: border-box; }
.personas-root a { color: var(--accent-text); text-decoration: none; }
.personas-root a:hover { color: var(--accent); text-decoration: underline; }
.personas-root ::-webkit-scrollbar { height: 8px; width: 8px; }
.personas-root ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 6px; }
.personas-root .num { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.personas-root .label { font-size: 10.5px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--faint); }
```

- [ ] **Step 6: Write the layout with gate and fonts**

```tsx
// src/app/personas/layout.tsx
import { redirect } from "next/navigation";
import { Instrument_Sans, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import { readSessionCookie } from "@/lib/session";
import { isStaffEmail } from "@/lib/personas/gate";
import "./personas.css";

const display = Instrument_Sans({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-display" });
const body = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--font-body" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["500"], variable: "--font-mono" });

export const metadata = { title: "MDS Personas" };

export default async function PersonasLayout({ children }: { children: React.ReactNode }) {
  const sess = await readSessionCookie();
  if (!isStaffEmail(sess?.email)) redirect("/");
  return (
    <div className={`personas-root theme-dark ${display.variable} ${body.variable} ${mono.variable}`}>
      {children}
    </div>
  );
}
```

`src/app/personas/page.tsx` placeholder for now:

```tsx
export default function PersonasPage() {
  return <main style={{ padding: 40 }}><h1 style={{ fontFamily: "var(--font-display)" }}>MDS Personas</h1></main>;
}
```

- [ ] **Step 7: Run the dev server and check the gate**

The dev server is the existing `.claude/launch.json` config `mds-digest-web` (`npm run dev`, port 3000) — start it with `preview_start {name: "mds-digest-web"}`, never with Bash.
Run: `curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://localhost:3000/personas` — Expected: `307 http://localhost:3000/` (no session → redirect). Then sign in as staff in a browser (Andy's OTP) and load `/personas`: the heading renders in Instrument Sans on `#090b11`.

- [ ] **Step 8: Commit**

```bash
cd /Users/Born/mds-digest-web && git switch -c personas-20260904 && git add docs/design/mds-personas src/app/personas src/lib/personas && git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "personas: route shell, staff gate, design tokens and fonts (#161)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: View-model rules in TypeScript

**Files:**
- Create: `src/lib/personas/model.ts`, `src/lib/personas/model.test.ts`

**Interfaces:**
- Produces:
```ts
export type Badge = "peak" | "holding" | "fading" | "none";
export type Stat = { key: string; name: string; parent: string | null; value: number; peak: number; badge: Badge; rank: number | null; signals: string; ask: boolean; give: boolean };
export type Category = Stat & { details: Stat[] };
export type MemberCard = { id: string; name: string; initials: string; city: string; status: string; isNew: boolean; isStaff: boolean; joined: string | null; level: number; top: { name: string; value: number }[]; photoUrl: string | null; msgs30: number; atPeakCount: number };
export type MemberSheet = MemberCard & { niche: string | null; channels: string[]; since: number | null; blurb: string; focus: string[]; gives: string[]; asks: string[]; givesText: string[]; asksText: string[]; categories: Category[]; silent: string[] };
export function badgeFor(score: number, peakScore: number): Badge;
export function valueOf(pct: number): number;               // round(pct*100)
export function peakOf(value: number, score: number, peakScore: number): number;
export function levelOf(categoryValues: number[]): number;   // mean of top 3, rounded
export function initialsOf(name: string): string;            // "Mo Kuhail" -> "MK"
export function tileHue(name: string): number;               // 0..5, stable hash
export function blurbFallback(summary: string | null, max?: number): string; // first sentences ≤ max chars
export function signalsText(evidence: Record<string, unknown> | null): string;
export function statKey(topic: string): string;              // "Amazon FBA" -> "amazon-fba"
export function topTwo(categories: { name: string; value: number }[]): { name: string; value: number }[];
```

- [ ] **Step 1: Write the failing tests**

```ts
// src/lib/personas/model.test.ts
import { describe, it, expect } from "vitest";
import { badgeFor, valueOf, peakOf, levelOf, initialsOf, tileHue, blurbFallback, signalsText, statKey, topTwo } from "./model";

describe("stat rules", () => {
  it("badge from score vs peak", () => {
    expect(badgeFor(2.85, 2.85)).toBe("peak");
    expect(badgeFor(2.6, 2.85)).toBe("holding");   // ≥ 85%
    expect(badgeFor(2.0, 2.85)).toBe("fading");
    expect(badgeFor(0, 0)).toBe("none");
  });
  it("value is the percentile in 0-100, peak scales by peak/score", () => {
    expect(valueOf(0.7106)).toBe(71);
    expect(peakOf(71, 2.51, 3.174)).toBe(90);
    expect(peakOf(71, 2.85, 2.85)).toBe(71);
    expect(peakOf(40, 1.0, 9.0)).toBe(100);
  });
  it("level is the mean of the top three categories", () => {
    expect(levelOf([100, 90, 80, 10, 0])).toBe(90);
    expect(levelOf([50])).toBe(50);
    expect(levelOf([])).toBe(0);
  });
});

describe("presentation helpers", () => {
  it("initials and a stable tile hue", () => {
    expect(initialsOf("Mo Kuhail")).toBe("MK");
    expect(initialsOf("Prosperlytics")).toBe("P");
    expect(tileHue("Mo Kuhail")).toBe(tileHue("Mo Kuhail"));
    expect(tileHue("Mo Kuhail")).toBeGreaterThanOrEqual(0);
    expect(tileHue("Mo Kuhail")).toBeLessThan(6);
  });
  it("blurb fallback keeps whole sentences under the cap", () => {
    const s = "Mo is a lean operator in Ottawa. He sells six products across Amazon US, Canada and EU. He ships 300k orders a year.";
    expect(blurbFallback(s, 80)).toBe("Mo is a lean operator in Ottawa. He sells six products across Amazon US, Canada and EU.");
    expect(blurbFallback(null)).toBe("");
  });
  it("signals text drops the multiplier and reads plainly", () => {
    expect(signalsText({ comments: 2.47, band_multiplier: 1.3, persona_asks_hits: 2, biz_affinity: true }))
      .toBe("comments 2.47 · persona asks hits 2 · biz affinity");
    expect(signalsText(null)).toBe("");
  });
  it("stat keys and top two", () => {
    expect(statKey("Amazon FBA")).toBe("amazon-fba");
    expect(statKey("AWD / Amazon warehousing")).toBe("awd-amazon-warehousing");
    expect(topTwo([{ name: "A", value: 10 }, { name: "B", value: 90 }, { name: "C", value: 50 }])).toEqual([{ name: "B", value: 90 }, { name: "C", value: 50 }]);
  });
});
```

- [ ] **Step 2: Run, expect failure** — `npx vitest run src/lib/personas/model.test.ts` → FAIL (module missing).

- [ ] **Step 3: Implement**

```ts
// src/lib/personas/model.ts
export type Badge = "peak" | "holding" | "fading" | "none";
export type Stat = { key: string; name: string; parent: string | null; value: number; peak: number; badge: Badge; rank: number | null; signals: string; ask: boolean; give: boolean };
export type Category = Stat & { details: Stat[] };
export type MemberCard = { id: string; name: string; initials: string; city: string; status: string; isNew: boolean; isStaff: boolean; joined: string | null; level: number; top: { name: string; value: number }[]; photoUrl: string | null; msgs30: number; atPeakCount: number };
export type MemberSheet = MemberCard & { niche: string | null; channels: string[]; since: number | null; blurb: string; focus: string[]; gives: string[]; asks: string[]; givesText: string[]; asksText: string[]; categories: Category[]; silent: string[] };

export function badgeFor(score: number, peakScore: number): Badge {
  if (!score || !peakScore) return "none";
  if (score >= peakScore) return "peak";
  return score >= 0.85 * peakScore ? "holding" : "fading";
}
export function valueOf(pct: number): number { return Math.round((pct || 0) * 100); }
export function peakOf(value: number, score: number, peakScore: number): number {
  if (!score || peakScore <= score) return value;
  return Math.min(100, Math.round(value * (peakScore / score)));
}
export function levelOf(categoryValues: number[]): number {
  const top = [...categoryValues].filter((v) => v > 0).sort((a, b) => b - a).slice(0, 3);
  return top.length ? Math.round(top.reduce((a, b) => a + b, 0) / top.length) : 0;
}
export function initialsOf(name: string): string {
  return name.trim().split(/\s+/).map((w) => w[0]?.toUpperCase() ?? "").join("").slice(0, 2);
}
export function tileHue(name: string): number {
  let h = 0;
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return h % 6;
}
export function blurbFallback(summary: string | null, max = 430): string {
  if (!summary) return "";
  const parts = summary.match(/[^.!?]+[.!?]+(\s|$)/g) ?? [summary];
  let out = "";
  for (const p of parts) { if (out && (out + p).length > max) break; out += p; }
  return out.trim();
}
export function signalsText(evidence: Record<string, unknown> | null): string {
  if (!evidence) return "";
  return Object.entries(evidence)
    .filter(([k]) => k !== "band_multiplier")
    .map(([k, v]) => k.replace(/_/g, " ") + (v === true ? "" : ` ${v}`))
    .join(" · ");
}
export function statKey(topic: string): string {
  return topic.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").replace(/-and-/g, "-");
}
export function topTwo(categories: { name: string; value: number }[]) {
  return [...categories].sort((a, b) => b.value - a.value).slice(0, 2);
}
```
(`statKey("Amazon FBA")` → `amazon-fba`; `"AWD / Amazon warehousing"` → `awd-amazon-warehousing`; `"Exits & M&A"` → `exits-m-a`. The cohort route uses this key; the SQL side receives the display name, so `data.ts` keeps a key→name map from the taxonomy.)

- [ ] **Step 4: Run, expect pass** — `npx vitest run src/lib/personas/model.test.ts` → all passed.

- [ ] **Step 5: Commit** — `git add src/lib/personas && git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "personas: view-model rules with tests (#161)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"`

---

### Task 3: SQL — the stat view, `personas_library()` and `personas_cohort()`

**Files:**
- Apply migrations with the Supabase MCP `apply_migration` (project `nadtudwuwjhckotrngzn`, schema `digest`), names below.
- Then in Scorecard: `python3 scripts/db_export_schema.py` and commit `db/`.

**Interfaces:**
- Produces: view `digest.personas_stats` (one row per member × topic: `at_member_id, topic, parent, value int, peak int, badge text, rank int, weakness numeric, evidence jsonb`); RPC `digest.personas_library()` → rows `(id text, name text, status text, city text, joined date, level int, top jsonb, photo_url text, msgs30 int, at_peak_count int)`; RPC `digest.personas_cohort(p_stat text)` → rows `(id, name, status, city, level, value int, top jsonb, photo_url)` ordered by value desc.

- [ ] **Step 1: Migration `personas_stats_view_161`**

```sql
create or replace view digest.personas_stats as
select e.at_member_id, e.topic, t.parent,
       round(coalesce(e.pct,0)*100)::int as value,
       case when e.score > 0 and e.peak_score > e.score
            then least(100, round(coalesce(e.pct,0)*100 * e.peak_score / e.score))::int
            else round(coalesce(e.pct,0)*100)::int end as peak,
       case when e.score is null or e.score = 0 then 'none'
            when e.score >= e.peak_score then 'peak'
            when e.score >= 0.85 * e.peak_score then 'holding' else 'fading' end as badge,
       e.rank_in_topic as rank, e.weakness_score as weakness, e.evidence
from digest.member_expertise e
join digest.expertise_topics t on t.topic = e.topic;
revoke all on digest.personas_stats from anon, authenticated;
grant select on digest.personas_stats to service_role;
```

- [ ] **Step 2: Migration `personas_library_161`**

```sql
create or replace function digest.personas_library()
returns table(id text, name text, status text, city text, joined date, level int, top jsonb, photo_url text, msgs30 int, at_peak_count int)
language sql stable security definer set search_path = digest, pg_temp as $$
  with act as (
    select p.at_member_id, p.full_name, p.status, p.join_date
    from digest.member_profiles p
    where p.status in ('Current Member','New Member','Current Member- Not Renewing','Current Member- Paused','Staff')
  ), cat as (
    select s.at_member_id, s.topic, s.value, s.badge from digest.personas_stats s where s.parent is null
  ), lvl as (
    select at_member_id,
           round(avg(value)) filter (where rn <= 3)::int as level,
           count(*) filter (where badge = 'peak' and value >= 50)::int as at_peak_count
    from (select c.*, row_number() over (partition by at_member_id order by value desc) rn from cat c) x
    group by at_member_id
  ), top2 as (
    select at_member_id, jsonb_agg(jsonb_build_object('name', topic, 'value', value) order by value desc) as top
    from (select c.*, row_number() over (partition by at_member_id order by value desc) rn from cat c) x
    where rn <= 2 group by at_member_id
  ), chats as (
    select m.at_member_id, max(coalesce(m.msgs_30d,0))::int as msgs30 from digest.members m group by m.at_member_id
  )
  select a.at_member_id, a.full_name, a.status,
         concat_ws(', ', at.city, case when coalesce(at.country,'') in ('United States','US','USA','') then at.state else at.country end),
         a.join_date, coalesce(l.level,0), coalesce(t.top,'[]'::jsonb), ph.public_url, coalesce(ch.msgs30,0), coalesce(l.at_peak_count,0)
  from act a
  left join digest.member_attributes at on at.at_member_id = a.at_member_id
  left join lvl l on l.at_member_id = a.at_member_id
  left join top2 t on t.at_member_id = a.at_member_id
  left join chats ch on ch.at_member_id = a.at_member_id
  left join digest.member_photos ph on ph.at_member_id = a.at_member_id
  order by a.full_name;
$$;
revoke all on function digest.personas_library() from public, anon, authenticated;
grant execute on function digest.personas_library() to postgres, service_role;
```
`digest.member_photos` does not exist yet — create it in this migration so the join compiles (Task 10 fills it):
```sql
create table if not exists digest.member_photos (
  at_member_id text primary key references digest.member_profiles(at_member_id) on delete cascade,
  storage_path text not null, public_url text not null, width int, source text, source_url text, fetched_at timestamptz not null default now());
revoke all on digest.member_photos from anon, authenticated;
grant select, insert, update, delete on digest.member_photos to service_role;
```
Put the table before the function in the same migration text.

- [ ] **Step 3: Migration `personas_cohort_161`**

```sql
create or replace function digest.personas_cohort(p_stat text)
returns table(id text, name text, status text, city text, level int, value int, top jsonb, photo_url text)
language sql stable security definer set search_path = digest, pg_temp as $$
  select l.id, l.name, l.status, l.city, l.level, s.value, l.top, l.photo_url
  from digest.personas_stats s
  join digest.personas_library() l on l.id = s.at_member_id
  where s.topic = p_stat and s.value >= 60
  order by s.value desc, l.name;
$$;
revoke all on function digest.personas_cohort(text) from public, anon, authenticated;
grant execute on function digest.personas_cohort(text) to postgres, service_role;
notify pgrst, 'reload schema';
```

- [ ] **Step 4: Verify with SQL (execute_sql)**

```sql
select count(*), count(*) filter (where level > 0), count(photo_url) from digest.personas_library();
-- expect 758-ish rows, most with level > 0, photo_url null until Task 10
select id, name, value from digest.personas_cohort('TikTok Shop') limit 3;   -- values ≥ 60, descending
select proname, proacl from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'digest' and proname like 'personas_%';
-- expect {postgres=X/postgres,service_role=X/postgres} on both
```
Then `cd /Users/Born/Scorecard && git switch personas-20260904 && python3 scripts/db_export_schema.py && git add db && GIT_AUTHOR_NAME="A Verdy" GIT_AUTHOR_EMAIL="Born@MacBook-Pro-9.local" GIT_COMMITTER_NAME="A Verdy" GIT_COMMITTER_EMAIL="Born@MacBook-Pro-9.local" git commit -m "#161 db: personas_stats view, personas_library, personas_cohort, member_photos

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"`

---

### Task 4: SQL — `personas_sheet()` and `personas_related()`

**Interfaces:**
- Produces: RPC `digest.personas_sheet(p_id text)` → one jsonb: `{member:{…library row…, niche, channels, since, title, summary, blurb, focus[], gives_text[], asks_text[], pattern}, stats:[{topic,parent,value,peak,badge,rank,weakness,evidence}], asks:[topic], gives:[topic]}`; RPC `digest.personas_related(p_id text)` → jsonb `{similar:[{id,name,city,level,photo_url,pct:int,shared:[topic]}], companions:[{id,name,city,level,photo_url,cover:[topic],shared:[topic]}]}`.

- [ ] **Step 1: Migration `personas_sheet_161`**

```sql
create or replace function digest.personas_sheet(p_id text)
returns jsonb language sql stable security definer set search_path = digest, pg_temp as $$
  select jsonb_build_object(
    'member', (select to_jsonb(l) || jsonb_build_object(
                 'niche', at.main_niche, 'channels', coalesce(to_jsonb(at.channel_mix),'[]'::jsonb), 'since', at.started_year, 'title', at.title,
                 'summary', mp.persona->>'summary', 'blurb', mp.persona->>'blurb',
                 'focus', coalesce((select jsonb_agg(f->>'item' order by (f->>'weight')::numeric desc nulls last) from jsonb_array_elements(coalesce(mp.persona->'focus','[]'::jsonb)) f), '[]'::jsonb),
                 'gives_text', coalesce((select jsonb_agg(g->>'item') from jsonb_array_elements(coalesce(mp.persona->'gives','[]'::jsonb)) g), '[]'::jsonb),
                 'asks_text', coalesce((select jsonb_agg(g->>'item') from jsonb_array_elements(coalesce(mp.persona->'asks','[]'::jsonb)) g), '[]'::jsonb),
                 'pattern', mp.persona->'engagement'->>'pattern')
               from digest.personas_library() l
               left join digest.member_attributes at on at.at_member_id = l.id
               left join digest.member_personas mp on mp.at_member_id = l.id
               where l.id = p_id),
    'stats', coalesce((select jsonb_agg(to_jsonb(s) - 'at_member_id' order by s.parent nulls first, s.value desc) from digest.personas_stats s where s.at_member_id = p_id), '[]'::jsonb),
    'asks',  coalesce((select jsonb_agg(distinct s.topic) from digest.personas_stats s where s.at_member_id = p_id and (s.evidence ? 'persona_asks_hits' or coalesce(s.weakness,0) > 0)), '[]'::jsonb),
    'gives', coalesce((select jsonb_agg(distinct s.topic) from digest.personas_stats s where s.at_member_id = p_id and s.evidence ? 'persona_gives_hits'), '[]'::jsonb)
  );
$$;
revoke all on function digest.personas_sheet(text) from public, anon, authenticated;
grant execute on function digest.personas_sheet(text) to postgres, service_role;
```

- [ ] **Step 2: Migration `personas_related_161`**

```sql
create or replace function digest.personas_related(p_id text)
returns jsonb language sql stable security definer set search_path = digest, pg_temp as $$
  with me as (select topic, value from digest.personas_stats where at_member_id = p_id and parent is null),
  asks as (select topic from digest.personas_stats where at_member_id = p_id and (evidence ? 'persona_asks_hits' or coalesce(weakness,0) > 0)),
  others as (select s.at_member_id, s.topic, s.value from digest.personas_stats s
             join digest.member_profiles p on p.at_member_id = s.at_member_id
             where s.parent is null and s.at_member_id <> p_id
               and p.status in ('Current Member','New Member','Current Member- Not Renewing','Current Member- Paused','Staff')),
  cos as (select o.at_member_id,
                 sum(o.value * me.value) / nullif(sqrt(sum(o.value*o.value)) * sqrt((select sum(value*value) from me)), 0) as sim,
                 array_agg(o.topic order by o.value desc) filter (where o.value >= 70 and me.value >= 70) as shared
          from others o join me on me.topic = o.topic group by o.at_member_id),
  sim as (select c.*, l.name, l.city, l.level, l.photo_url from cos c join digest.personas_library() l on l.id = c.at_member_id
          where c.sim is not null order by c.sim desc limit 5),
  comp as (select o.at_member_id, array_agg(o.topic order by o.value desc) as cover, sum(o.value) as score
           from others o join asks a on a.topic = o.topic where o.value >= 75 group by o.at_member_id),
  compx as (select c.*, l.name, l.city, l.level, l.photo_url,
                   (select array_agg(o2.topic order by o2.value desc) from others o2 join me on me.topic = o2.topic where o2.at_member_id = c.at_member_id and o2.value >= 70 and me.value >= 70) as shared
            from comp c join digest.personas_library() l on l.id = c.at_member_id order by c.score desc limit 5)
  select jsonb_build_object(
    'similar', coalesce((select jsonb_agg(jsonb_build_object('id', at_member_id, 'name', name, 'city', city, 'level', level, 'photo_url', photo_url,
                          'pct', round(sim*100)::int, 'shared', coalesce(to_jsonb(shared[1:2]),'[]'::jsonb)) order by sim desc) from sim), '[]'::jsonb),
    'companions', coalesce((select jsonb_agg(jsonb_build_object('id', at_member_id, 'name', name, 'city', city, 'level', level, 'photo_url', photo_url,
                          'cover', to_jsonb(cover[1:2]), 'shared', coalesce(to_jsonb(shared[1:2]),'[]'::jsonb)) order by score desc) from compx), '[]'::jsonb));
$$;
revoke all on function digest.personas_related(text) from public, anon, authenticated;
grant execute on function digest.personas_related(text) to postgres, service_role;
notify pgrst, 'reload schema';
```

- [ ] **Step 3: Verify**

```sql
select jsonb_array_length(personas_sheet('recjLusFLFDlnY7d9')->'stats'), personas_sheet('recjLusFLFDlnY7d9')->'asks';
select personas_related('recjLusFLFDlnY7d9')->'similar'->0, jsonb_array_length(personas_related('recjLusFLFDlnY7d9')->'companions');
```
Expected: 51 or fewer stat rows (only topics with a row), asks includes "Amazon FBA" for Mo Kuhail; 5 similar with pct 60–99, up to 5 companions whose `cover` topics are in Mo's asks. Time both: `explain analyze select personas_related('recjLusFLFDlnY7d9')` under 300 ms. Export `db/` and commit as in Task 3 (`#161 db: personas_sheet, personas_related`).

---

### Task 5: Data layer

**Files:**
- Create: `src/lib/personas/data.ts`, `src/lib/personas/data.test.ts`

**Interfaces:**
- Consumes: `sbRequest<T>(pathAndQuery, {method, body})` from `@/lib/supabase`; the four RPCs; `model.ts`.
- Produces:
```ts
export const TAXONOMY: { name: string; parent: string | null }[]; // loaded once from digest.expertise_topics
export function keyToTopic(key: string): string | null;          // "amazon-fba" -> "Amazon FBA"
export async function getLibrary(): Promise<MemberCard[]>;      // cached 60 s in module scope
export async function getSheet(id: string): Promise<MemberSheet | null>;
export async function getCohort(topic: string): Promise<{ card: MemberCard; value: number }[]>;
export async function getRelated(id: string): Promise<{ similar: RelatedRow[]; companions: RelatedRow[] }>;
export type RelatedRow = { id: string; name: string; city: string; level: number; photoUrl: string | null; reason: string };
```

- [ ] **Step 1: Failing test for the pure shaping functions** (`toCard`, `toSheet`, `reasonSimilar`, `reasonCompanion` are exported for tests):

```ts
// src/lib/personas/data.test.ts
import { describe, it, expect } from "vitest";
import { toCard, toSheet, reasonSimilar, reasonCompanion } from "./data";

const row = { id: "rec1", name: "Mo Kuhail", status: "New Member", city: "Ottawa, Canada", joined: "2026-08-30", level: 82,
  top: [{ name: "Amazon FBA", value: 100 }, { name: "Logistics & 3PL", value: 100 }], photo_url: null, msgs30: 4, at_peak_count: 7 };

describe("shaping", () => {
  it("card from a library row", () => {
    const c = toCard(row);
    expect(c.isNew).toBe(true); expect(c.isStaff).toBe(false); expect(c.initials).toBe("MK");
    expect(c.top[0].name).toBe("Amazon FBA"); expect(c.photoUrl).toBeNull();
  });
  it("sheet nests details under categories and lists silent ones", () => {
    const sheet = toSheet({
      member: { ...row, niche: "Home", channels: ["Amazon US"], since: 2019, summary: "Mo is lean. He ships a lot.", blurb: null, focus: [], gives_text: [], asks_text: [], pattern: null },
      stats: [
        { topic: "Amazon FBA", parent: null, value: 100, peak: 100, badge: "peak", rank: 1, weakness: 0, evidence: { comments: 4 } },
        { topic: "Amazon US", parent: "Amazon FBA", value: 71, peak: 71, badge: "peak", rank: 5, weakness: 0, evidence: {} },
      ],
      asks: ["Amazon FBA"], gives: [],
    }, [{ name: "Amazon FBA", parent: null }, { name: "Amazon US", parent: "Amazon FBA" }, { name: "Walmart", parent: null }]);
    expect(sheet!.categories[0].details[0].name).toBe("Amazon US");
    expect(sheet!.categories[0].ask).toBe(true);
    expect(sheet!.silent).toEqual(["Walmart"]);
    expect(sheet!.blurb).toBe("Mo is lean. He ships a lot.");
  });
  it("reasons", () => {
    expect(reasonSimilar(84, ["PPC", "Amazon US"])).toBe("84% profile match · both strong in PPC, Amazon US");
    expect(reasonCompanion("Mo", ["Listing optimization"], ["Amazon FBA"])).toBe("strong in Listing optimization, which Mo is asking about · shares Amazon FBA");
  });
});
```

- [ ] **Step 2: Run, expect failure.**

- [ ] **Step 3: Implement `data.ts`**

```ts
import { sbRequest } from "@/lib/supabase";
import { blurbFallback, initialsOf, signalsText, statKey, type Badge, type Category, type MemberCard, type MemberSheet, type Stat } from "./model";

type LibraryRow = { id: string; name: string; status: string; city: string | null; joined: string | null; level: number; top: { name: string; value: number }[]; photo_url: string | null; msgs30: number; at_peak_count: number };
type StatRow = { topic: string; parent: string | null; value: number; peak: number; badge: Badge; rank: number | null; weakness: number | null; evidence: Record<string, unknown> | null };
type SheetPayload = { member: LibraryRow & { niche: string | null; channels: string[] | null; since: number | null; summary: string | null; blurb: string | null; focus: string[]; gives_text: string[]; asks_text: string[]; pattern: string | null }; stats: StatRow[]; asks: string[]; gives: string[] };
export type Taxon = { name: string; parent: string | null };
export type RelatedRow = { id: string; name: string; city: string; level: number; photoUrl: string | null; reason: string };

let taxonomy: Taxon[] | null = null;
export async function getTaxonomy(): Promise<Taxon[]> {
  if (!taxonomy) taxonomy = (await sbRequest<{ topic: string; parent: string | null }[]>("expertise_topics?select=topic,parent&order=parent.nullsfirst,topic")).map((t) => ({ name: t.topic, parent: t.parent }));
  return taxonomy;
}
export async function keyToTopic(key: string): Promise<string | null> {
  return (await getTaxonomy()).find((t) => statKey(t.name) === key)?.name ?? null;
}

export function toCard(r: LibraryRow): MemberCard {
  return { id: r.id, name: r.name, initials: initialsOf(r.name), city: r.city ?? "", status: r.status, isNew: r.status === "New Member", isStaff: r.status === "Staff",
    joined: r.joined, level: r.level ?? 0, top: r.top ?? [], photoUrl: r.photo_url, msgs30: r.msgs30 ?? 0, atPeakCount: r.at_peak_count ?? 0 };
}
export function toSheet(p: SheetPayload | null, tax: Taxon[]): MemberSheet | null {
  if (!p?.member) return null;
  const byTopic = new Map(p.stats.map((s) => [s.topic, s]));
  const asks = new Set(p.asks), gives = new Set(p.gives);
  const stat = (t: Taxon): Stat => {
    const s = byTopic.get(t.name);
    return { key: statKey(t.name), name: t.name, parent: t.parent, value: s?.value ?? 0, peak: s?.peak ?? 0, badge: s?.badge ?? "none",
      rank: s?.rank ?? null, signals: signalsText(s?.evidence ?? null), ask: asks.has(t.name), give: gives.has(t.name) };
  };
  const cats: Category[] = tax.filter((t) => !t.parent).map((t) => ({ ...stat(t), details: tax.filter((d) => d.parent === t.name).map(stat) }));
  const withSignal = cats.filter((c) => c.value > 0).sort((a, b) => b.value - a.value);
  const m = p.member;
  return { ...toCard(m), niche: m.niche, channels: m.channels ?? [], since: m.since, blurb: (m.blurb || "").trim() || blurbFallback(m.summary),
    focus: m.focus ?? [], gives: p.gives, asks: p.asks, givesText: m.gives_text ?? [], asksText: m.asks_text ?? [],
    categories: withSignal, silent: cats.filter((c) => !c.value).map((c) => c.name) };
}
export const reasonSimilar = (pct: number, shared: string[]) => `${pct}% profile match` + (shared.length ? ` · both strong in ${shared.join(", ")}` : "");
export const reasonCompanion = (first: string, cover: string[], shared: string[]) =>
  (cover.length ? `strong in ${cover.join(" & ")}, which ${first} is asking about` : "") + (shared.length ? `${cover.length ? " · " : ""}shares ${shared.join(", ")}` : "");

let libCache: { at: number; rows: MemberCard[] } | null = null;
export async function getLibrary(): Promise<MemberCard[]> {
  if (libCache && Date.now() - libCache.at < 60_000) return libCache.rows;
  const rows = (await sbRequest<LibraryRow[]>("rpc/personas_library", { method: "POST", body: {} })).map(toCard);
  libCache = { at: Date.now(), rows };
  return rows;
}
export async function getSheet(id: string): Promise<MemberSheet | null> {
  const [payload, tax] = await Promise.all([sbRequest<SheetPayload>("rpc/personas_sheet", { method: "POST", body: { p_id: id } }), getTaxonomy()]);
  return toSheet(payload, tax);
}
export async function getCohort(topic: string) {
  const rows = await sbRequest<(LibraryRow & { value: number })[]>("rpc/personas_cohort", { method: "POST", body: { p_stat: topic } });
  return rows.map((r) => ({ card: toCard(r), value: r.value }));
}
export async function getRelated(id: string, first: string) {
  const r = await sbRequest<{ similar: any[]; companions: any[] }>("rpc/personas_related", { method: "POST", body: { p_id: id } });
  const row = (x: any, reason: string): RelatedRow => ({ id: x.id, name: x.name, city: x.city ?? "", level: x.level ?? 0, photoUrl: x.photo_url ?? null, reason });
  return { similar: (r.similar ?? []).map((x) => row(x, reasonSimilar(x.pct, x.shared ?? []))),
           companions: (r.companions ?? []).map((x) => row(x, reasonCompanion(first, x.cover ?? [], x.shared ?? []))) };
}
```

- [ ] **Step 4: Run tests, expect pass; commit** — `personas: data layer over the four RPCs (#161)`.

---

### Task 6: Primitives and the component sheet

**Files:**
- Create: `src/components/personas/InitialsTile.tsx, PortraitCard.tsx, Chip.tsx, StatusDot.tsx, StatBar.tsx, StatRow.tsx, SearchBar.tsx, RailHeader.tsx, Rail.tsx, CohortCard.tsx`
- Create: `src/app/personas/dev/components/page.tsx`
- Reference: README "Components" (exact sizes, colors, hover), `MDS Personas.dc.html` markup for each.

**Interfaces:**
- Produces:
```tsx
<InitialsTile name={string} size="card"|"sheet"|"row" />
<PortraitCard member={MemberCard} variant="split"|"poster" statName?={string} statValue?={number} />   // Link to /personas/[id]
<Chip kind="category"|"gold"|"gives"|"new"|"staff" href?={string}>{text}</Chip>
<StatusDot badge={Badge} />                            // dot + word
<StatBar value={number} peak={number} size="cat"|"detail" />
<StatRow stat={Stat} variant="category"|"detail" defaultOpen?={boolean}>{children /* details */}</StatRow>
<SearchBar value onChange categories={string[]} />    // client
<RailHeader title subtitle? allHref? allCount? />
<Rail>{cards}</Rail>                                   // horizontal scroll, snap
<CohortCard member={MemberCard} value={number} />
```
Every href is built from `statKey`: `/personas/stat/${statKey(name)}`; member links are `/personas/${id}`.

- [ ] **Step 1: Build each component with the README values.** StatBar is the one with logic — write it first with a test of its geometry helper:

```ts
// src/components/personas/statbar.test.ts
import { describe, it, expect } from "vitest";
import { barGeometry } from "./StatBar";
describe("barGeometry", () => {
  it("fills to value, marks peak, hides the tick at peak", () => {
    expect(barGeometry(62, 80)).toEqual({ fillPct: 62, tickPct: 80, showTick: true, stub: false });
    expect(barGeometry(71, 71)).toEqual({ fillPct: 71, tickPct: 71, showTick: false, stub: false });
    expect(barGeometry(0, 0)).toEqual({ fillPct: 2, tickPct: 0, showTick: false, stub: true });
  });
});
```
```tsx
// src/components/personas/StatBar.tsx
export function barGeometry(value: number, peak: number) {
  const stub = value <= 0;
  return { fillPct: stub ? 2 : value, tickPct: peak, showTick: peak > value, stub };
}
export function StatBar({ value, peak, size }: { value: number; peak: number; size: "cat" | "detail" }) {
  const g = barGeometry(value, peak);
  const h = size === "cat" ? 6 : 5;
  return (
    <div style={{ position: "relative", height: h, borderRadius: 3, background: "var(--track)", margin: "5px 0 13px" }} aria-label={`${value} of 100, peak ${peak}`}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 3, clipPath: `inset(0 ${100 - g.fillPct}% 0 0 round 3px)`,
        background: g.stub ? "var(--border-strong)" : "linear-gradient(90deg in oklch, oklch(66% .19 25) 0%, oklch(74% .17 60) 22%, oklch(80% .16 95) 42%, oklch(74% .17 150) 66%, oklch(72% .17 152) 100%)" }} />
      {!g.stub && <span style={{ position: "absolute", left: `calc(${g.fillPct}% - 3px)`, top: -6, width: 0, height: 0, borderLeft: "3.5px solid transparent", borderRight: "3.5px solid transparent", borderTop: "5px solid var(--text)", filter: "drop-shadow(0 1px 1px rgba(0,0,0,.6))" }} />}
      <span style={{ position: "absolute", left: "70%", top: -3, bottom: -3, width: 1, background: "var(--border-strong)" }} />
      <span className="num" style={{ position: "absolute", left: "calc(70% - 6px)", top: h + 3, fontSize: 10, color: "var(--faint)" }}>70</span>
      {g.showTick && <span style={{ position: "absolute", left: `${g.tickPct}%`, top: -2, bottom: -2, width: 2, background: "var(--text)", opacity: .45 }} />}
    </div>
  );
}
```
Then the rest, straight from README "Components" (PortraitCard with `split`/`poster`, hover scale 1.045 + shadow via CSS class in `personas.css`; InitialsTile with the six oklch hues by `tileHue`; Chip kinds mapped to `--strong-*`, `--below-*`, `--peak-*`, `--accent-*`; StatusDot filled/ring per badge; StatRow as `<details open={defaultOpen}>` with the raised summary tile grid `minmax(190px,1fr) minmax(110px,200px) 64px 78px`; SearchBar client component with the "/" hotkey and the category-suggestion dropdown; RailHeader; Rail with `scroll-snap-type: x proximity`; CohortCard poster-style with the value mono 26px).

- [ ] **Step 2: Component sheet page** `src/app/personas/dev/components/page.tsx`: renders every primitive with sample props (two fake `MemberCard`s built inline, one with `photoUrl: null`), each labelled — this is the reviewer's surface. Gate it with `process.env.NODE_ENV !== "production"` → `notFound()` otherwise.

- [ ] **Step 3: Verify** — `npx vitest run src/components/personas` passes; `npx tsc --noEmit` clean; screenshot `http://localhost:3000/personas/dev/components` at 1440×1600 with the headless shell and compare against the handoff's "Components" view (open `docs/design/mds-personas/MDS Personas.dc.html`, tab Components). Fix sizes until they match.

- [ ] **Step 4: Commit** — `personas: primitives + component sheet (#161)`.

---

### Task 7: Library page

**Files:**
- Replace: `src/app/personas/page.tsx`; Create: `src/app/personas/LibraryClient.tsx`, `src/components/personas/TopBar.tsx`

**Interfaces:**
- Consumes: `getLibrary()`, `getTaxonomy()`, primitives.
- Produces: route `/personas`.

- [ ] **Step 1: Server page** — `page.tsx` (`export const dynamic = "force-dynamic"`) loads `getLibrary()` + taxonomy and renders `<TopBar/>` and `<LibraryClient members={cards} categories={parents} />`. Rails are computed in the client from the one payload (758 cards, ~200 KB):
  - Newest members: sort by `joined` desc, 24.
  - At their peak: `atPeakCount >= 4`, sort by level desc, 24.
  - Strong in TikTok Shop / Logistics & 3PL / AI & Automation: needs the stat value per member → the library row's `top` only has two. Add to `personas_library()` a `strong jsonb` column: `jsonb_object_agg(topic, value)` of the member's categories ≥ 60 (small; at most 18 keys). Do that as migration `personas_library_strong_161` (recreate the function with the extra column; keep the grants) and add `strong: Record<string, number>` to `MemberCard` in `model.ts` + `toCard`.
  - Active in the chats this month: `msgs30 > 0`, sort desc, 24.
- [ ] **Step 2: Client search** — `LibraryClient.tsx` (`"use client"`): state `q`; empty → rails; typing → results grid (`repeat(auto-fill, minmax(184px,1fr))`) of members where name, city or any `strong` key contains `q` (case-insensitive); focused + empty → the "BROWSE A STRENGTH" dropdown with 18 chips linking to `/personas/stat/[key]`. "/" focuses the input.
- [ ] **Step 3: Meta line** under the bar: `{n} members · 18 categories · 33 detail stats · rebuilt nightly` (mono count).
- [ ] **Step 4: Verify** — screenshot `/personas` at 1440×1400 and 390×1200; every rail has cards; "all N strong here →" links resolve (`curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/personas/stat/tiktok-shop` with the session cookie → 200). Commit: `personas: library page with rails and search (#161)`.

---

### Task 8: Member sheet page

**Files:**
- Create: `src/app/personas/[id]/page.tsx`, `src/components/personas/StatsPanel.tsx` (client: Top 6 / Expand all / Collapse all), `src/components/personas/RelatedList.tsx`

- [ ] **Step 1:** `page.tsx` awaits `params.id`, loads `getSheet(id)` (→ `notFound()` when null) and `getRelated(id, first name)` in parallel. Layout per README "Member sheet": grid `320px minmax(0,1fr)`, aside sticky (portrait 300px, `InitialsTile size="sheet"` fallback, level badge, name 32px, tagline `{niche} · {channels} · {city} · selling since {since}` (skip empties), blurb, FOCUS RIGHT NOW chips, "Full Member 360 →" → `/admin/member360/${id}`).
- [ ] **Step 2:** `StatsPanel` renders `categories` as `StatRow variant="category"` with details inside (`StatRow variant="detail"`), the top 6 open by default, the segmented control switching `open` on all `<details>` via state; after the details: `no signal yet: …` for details with value 0, and `Rank #n in the community · signals: …`; below the panel: `No signal yet on: {silent}`.
- [ ] **Step 3:** Gives / Asks tile: `Chip kind="gives"` for each of `sheet.gives`, `Chip kind="gold"` for `sheet.asks`, both `href=/personas/stat/[key]`; under each "In their words: …" from `givesText` / `asksText`.
- [ ] **Step 4:** `RelatedList` twice (Similar members: "closest stat profile" · Good companions: "strong where {first} is asking"), rows `48px 240px minmax(0,1fr) 40px`, each row a Link to the member.
- [ ] **Step 5: Verify** — screenshots of `/personas/recjLusFLFDlnY7d9` at 1440×2400 and 390×2400; the numbers on screen equal `select value, peak, badge from digest.personas_stats where at_member_id='recjLusFLFDlnY7d9' and topic='Amazon FBA'`; similar/companion rows equal `personas_related('recjLusFLFDlnY7d9')`. Commit: `personas: member sheet (#161)`.

---

### Task 9: Cohort page

**Files:**
- Create: `src/app/personas/stat/[key]/page.tsx`, `src/components/personas/CohortGrid.tsx` (client: "Show 96 more · n left")

- [ ] **Step 1:** resolve `keyToTopic(key)` (→ `notFound()`), load `getCohort(topic)` and the taxonomy. Title `Strong in {topic}` 34px; subtitle `{n} members at 60 or above · sorted by today's value` + ` · part of {parent}` link for a detail stat; for a category a chip row of its detail stats (30px pills, `href` per key).
- [ ] **Step 2:** `CohortGrid`: `repeat(auto-fill, minmax(184px,1fr))`, `CohortCard` per member, first 96, button reveals 96 more; 0 members → dashed tile "Nobody is at 60 yet".
- [ ] **Step 3: Verify** — `/personas/stat/tiktok-shop` and `/personas/stat/gmv-max` render; the count equals `select count(*) from digest.personas_cohort('TikTok Shop')`. Commit: `personas: cohort page (#161)`.

---

### Task 10: Photos — cache job, Storage bucket, wiring

**Files (Scorecard):**
- Create: `scripts/cache_member_photos.py`, `scripts/tests/test_cache_member_photos.py`
- Modify: `scripts/nightly_derivations.py` (add `("cache_member_photos", [f"{REPO}/scripts/cache_member_photos.py"])` after `sync_chapter_pages`)
- Supabase: create Storage bucket `member-photos` (public) — Supabase MCP `execute_sql`: `insert into storage.buckets (id, name, public) values ('member-photos','member-photos', true) on conflict (id) do nothing;`
- Seed the heartbeat row: `insert into digest.olivia_job_heartbeats (job, status, detail, max_age_hours) values ('cache_member_photos','ok','seeded (#161)',30) on conflict (job) do nothing;`

**Interfaces:**
- Produces rows in `digest.member_photos` (`public_url` = `https://nadtudwuwjhckotrngzn.supabase.co/storage/v1/object/public/member-photos/<at_member_id>.jpg`) which `personas_library()` already joins.

- [ ] **Step 1: Failing tests for the pure parts**

```python
# scripts/tests/test_cache_member_photos.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cache_member_photos import candidate_urls, best_attachment

def test_candidate_urls_prefers_large_attachments_then_text_links():
    fields = {"Picture URL": [{"url": "https://a/att.jpg", "width": 800, "thumbnails": {"large": {"url": "https://a/large.jpg", "width": 512}}}],
              "Photo": ["https://api.typeform.com/responses/files/x/Profile3.jpg"],
              "Facebook Photo": [{"url": "https://a/fb40.jpg", "width": 40}]}
    assert candidate_urls(fields) == [("Picture URL", "https://a/large.jpg"), ("Photo", "https://api.typeform.com/responses/files/x/Profile3.jpg")]

def test_best_attachment_rejects_tiny_images():
    assert best_attachment([{"url": "https://a/fb40.jpg", "width": 40}]) is None
    assert best_attachment([{"url": "https://a/x.jpg", "width": 300}]) == "https://a/x.jpg"

def test_groupos_roster_rows_become_candidates():
    from cache_member_photos import groupos_candidates
    rows = [{"email": "mo@x.com", "avatar_url": "uploads/users/profile/thumb-1.jpeg"}]
    assert groupos_candidates(rows, {"mo@x.com": "rec1"}) == {"rec1": "https://mds-community.s3.amazonaws.com/uploads/users/profile/thumb-1.jpeg"}
```

- [ ] **Step 2: Run, expect failure.** `cd /Users/Born/Scorecard && python3 -m pytest scripts/tests/test_cache_member_photos.py -q`

- [ ] **Step 3: Implement** `scripts/cache_member_photos.py` (stdlib + curl + `sips`, same env loader as `scripts/embed_partners_events.py`):
  - `candidate_urls(fields)`: attachments (`Picture URL`, `Headshots`, `Photo` when attachment) via `best_attachment` (largest of `thumbnails.large` / `url` with width ≥ 120), then text/list fields (`Photo`) via `re.findall(r"https?://[^'\"\]\s,]+", str(v))`; skip `Facebook Photo` (40 px).
  - `groupos_candidates(rows, email_to_member)`: optional `--groupos-roster roster.json` (the weekly GroupOS task dumps `members_list` items) → S3 URL `https://mds-community.s3.amazonaws.com/` + `avatar_url`; resolved to `at_member_id` by email through `digest.resolve_member_by_email` (call the RPC per email, cache).
  - Main: for each active member (statuses above) without a `member_photos` row younger than 30 days: try GroupOS candidate first (if roster given), then Airtable (`GET https://api.airtable.com/v0/appou5JVr0WIrioWS/tblfwOSROSHfuYUxv/{rec}` with `AIRTABLE_PAT`, 0.25 s apart); download; `sips -s format jpeg -s formatOptions 72 -Z 320`; upload with `curl -X POST "$SUPABASE_URL/storage/v1/object/member-photos/<rec>.jpg" -H "Authorization: Bearer <SUPABASE_SECRET_KEY>" -H "Content-Type: image/jpeg" -H "x-upsert: true" --data-binary @file`; upsert the row (`source` = field name or `groupos`, `width`); stamp `olivia_job_heartbeats` `cache_member_photos` ok/error with counts (same `heartbeat()` shape as `partners_weekly_check.py`).
  - `--dry-run` prints the plan; `--limit N` for tests.

- [ ] **Step 4: Run tests, then the job for real** — `python3 scripts/cache_member_photos.py --limit 5` then without limit (~10 min). Verify: `select count(*), min(width), max(width) from digest.member_photos;` (expect ≥ 600 rows, widths 120–320) and one `public_url` opens in a browser. `personas_library()` now returns `photo_url` for those members; reload `/personas` — faces appear.
- [ ] **Step 5: Commit** (Scorecard): `#161 photos: cache_member_photos job -> Storage member-photos + digest.member_photos`.

---

### Task 11: Blurb — nightly writer

**Files (Scorecard):**
- Create: `scripts/persona_blurbs.py`, `scripts/tests/test_persona_blurbs.py`
- Modify: `scripts/nightly_derivations.py` (add `("persona_blurbs", [f"{REPO}/scripts/persona_blurbs.py"])` after `entity_dossiers`); seed heartbeat `persona_blurbs` (max_age_hours 30).

**Interfaces:**
- Writes `member_personas.persona->>'blurb'` (jsonb key added with `persona || jsonb_build_object('blurb', …)` via PATCH); `personas_sheet()` already reads it.

- [ ] **Step 1: Failing test for the prompt + parse**

```python
# scripts/tests/test_persona_blurbs.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from persona_blurbs import build_prompt, clean_blurb

def test_prompt_carries_the_summary_and_the_rules():
    p = build_prompt("Mo Kuhail", "Mo is a lean operator in Ottawa. He ships 300k orders a year across 6 SKUs.")
    assert "Mo Kuhail" in p and "two or three sentences" in p and "no numbers" in p

def test_clean_blurb_trims_quotes_and_caps_length():
    assert clean_blurb('"Mo runs a lean home-goods brand from Ottawa. He answers fast and tests before he recommends."') == "Mo runs a lean home-goods brand from Ottawa. He answers fast and tests before he recommends."
    assert len(clean_blurb("x. " * 400)) <= 420
```

- [ ] **Step 2: Run, expect failure.**

- [ ] **Step 3: Implement** — reuse the API pattern of `/Users/Born/mds-scorecard-tools/persona_refresh.py` (its `MODEL`, key loading and curl call to `https://api.anthropic.com/v1/messages`), but with `model="claude-haiku-4-5-20251001"`, `max_tokens=300`, and this prompt:

```python
def build_prompt(name, summary):
    return (f"Write a card blurb for {name} for MDS staff: two or three sentences, warm and plain, third person, "
            "what they do, where, and how they show up in the community. Use only the summary below. "
            "No numbers, no jargon, no exclamation marks, no quotes, no bullet points, under 380 characters.\n\n"
            f"Summary:\n{summary}\n\nBlurb:")
def clean_blurb(text):
    t = (text or "").strip().strip('"').strip()
    return t[:420].rsplit(".", 1)[0] + "." if len(t) > 420 else t
```
Main: select active members whose persona has a `summary` and no `blurb` (or whose `built_at` is newer than the blurb's `blurb_at`); write `blurb` + `blurb_at`; 3 tries with backoff on 429/529; stamp the heartbeat. `--limit`, `--dry-run`.

- [ ] **Step 4: Run tests; run the job with `--limit 3`, read the three blurbs (SQL) and judge them; then the full run** (758 × Haiku ≈ under $1). Reload a sheet: the blurb replaces the summary sentences.
- [ ] **Step 5: Commit** (Scorecard): `#161 blurbs: persona_blurbs nightly writer (Haiku 4.5)`.

---

### Task 12: States, responsive, light theme, verification, docs

**Files:**
- Modify: `src/app/personas/personas.css` (breakpoints 1180 / 1000 / 640 per README "Responsive"), `TopBar.tsx` (theme toggle → `.theme-light`, persisted in `localStorage` key `personas-theme`), `src/app/personas/loading.tsx` (skeleton cards with the exact card geometry), `src/app/personas/[id]/not-found.tsx`.
- Docs (Scorecard): `OLIVIA_SPRINT_4.md` (#161 close block with the AC table), `OLIVIA_HANDBOOK.md` (data layer rows for `member_photos`, `personas_*` RPCs, `persona.blurb`), `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md` index line, memory.

- [ ] **Step 1:** States per README: no persona → dashed tile (initials 80px, name, "{city} · joined this week", explainer); empty search → "Nobody matches “q”"; cohort 0 → "Nobody is at 60 yet"; loading skeletons. Category with no signal already handled (silent list).
- [ ] **Step 2:** Responsive rules from README "Responsive"; verify with screenshots at 1440, 1000, 390 for all three pages (headless shell `--window-size`).
- [ ] **Step 3:** Light theme: toggle swaps `theme-dark`/`theme-light` on the root; screenshot both.
- [ ] **Step 4: Gate check** — `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/personas/stat/tiktok-shop` without a cookie → 307; PostgREST with the anon key: `curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/personas_library" -H "apikey: $ANON" -H "Authorization: Bearer $ANON" -H "Content-Profile: digest"` → 401/403/404. Add both as checks to `scripts/olivia_leak_gate.py` (pattern: the `anon denied on …` checks) and run the gate: EXIT 0.
- [ ] **Step 5: Acceptance walk** (the spec's list): 758 open · 51 stats · photos from Storage only (grep the rendered HTML for `airtableusercontent` → none) · 5 members spot-checked against `personas_related` · pixel review at 1440 and 390 both themes.
- [ ] **Step 6: Docs + commits** on both branches; push both branches; do NOT merge mds-digest-web to `main` (Render deploy) until Andy's go. Board row: "✅ BUILT locally, READY TO DEPLOY (Andy)".

---

## Self-review notes
- Spec coverage: gate (T1, T12) · population + stat rules (T3/T4 SQL, T2) · three screens (T7–T9) · all 51 stats + silent (T4/T8) · asks/gives mapped (T4/T8) · badges (T2/T3) · rails incl. "Strong in" (T7 with the `strong` column) · photos (T10) · blurb (T11) · similar/companions in SQL (T4) · states/responsive/light (T12) · acceptance (T12).
- Out of scope stays out: rising badge, GroupOS/FB photo sources beyond the roster hook, taxonomy changes, member-facing.
- Consistency: `MemberCard.strong` is introduced in T7 (model + toCard + SQL); `statKey` is the single key rule used by T5–T9; badge names `peak|holding|fading|none` everywhere; RPC names `personas_library / personas_sheet / personas_cohort / personas_related`.
