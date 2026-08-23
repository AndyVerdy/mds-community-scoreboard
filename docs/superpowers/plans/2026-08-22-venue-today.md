# "Today" at an In-Person Event Is the Venue's Day (#114) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a member at the Summit asks Millie "what's happening today / tomorrow / on Monday", the day is
resolved in the **venue's** zone (Asia/Singapore), never from the model's US-Eastern sense of today — Ian
Sells asked on Sunday 23 Aug at 11:30 in Singapore and got Saturday's pre-event list.

**Architecture:** Root cause, read from the live prod workflow and the route: the Answer Seed injects
`TODAY is <date> (US Eastern)` and the `event_schedule` tool description says `day (one date, at=YYYY-MM-DD)`,
so the model computes "today" in Eastern (still Saturday 22 Aug at 23:30 ET) and sends `at=2026-08-22`; the
route only computes the venue-zone day when `at` is absent. Fix in code first (code beats prompt rules): a
pure resolver in `mds-digest-web` (`src/lib/schedule-day.ts`) turns `at` = `today | tomorrow | yesterday |
<weekday> | YYYY-MM-DD | ISO instant` into a venue-zone date; the `day` op uses it, the `next` op stops dying
on non-ISO `at`, and **every** schedule response carries `now_at_venue` (e.g. `Sunday 23 Aug, 11:31 am
Singapore time`) so the model anchors on the venue day. Then the Answer Seed (STAGING only) is told to pass
the WORD for relative days and to trust `now_at_venue` over the TODAY line at the venue; Andy promotes.
Virtual events are out of scope (Andy, 2026-08-22: "a bit more challenging for virtual").

**Tech Stack:** TypeScript / Next.js App Router (mds-digest-web on Render, deploys on push to `main`;
`/api/version` returns the deployed sha) · vitest (`npx vitest run`, baseline 5 files / 67 tests green) ·
n8n Olivia workflow (STAGING `bqHstPDi84uOhTCJ`, Answer Seed jsCode) · Python apply script pattern
`scripts/olivia_loop/apply_transcript_boundary_2025.py` · `scripts/olivia_leak_gate.py` · `scripts/olivia_selftest.py --staging`.

## Global Constraints

- **Two repos, two authors.** Route + lib + tests in `/Users/Born/mds-digest-web` (commit author
  `Andy Verdy <andy.verdy1@gmail.com>`: `git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit …`).
  Apply script, docs, board in `/Users/Born/Scorecard` (trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).
  Never edit one while committing the other.
- **Another agent is mid-work in both repos (#108).** In `mds-digest-web`, `src/lib/finder.test.ts` is
  modified and uncommitted on `main` — never stage it, never `git add -A`; commit only files named here.
  Pushing `main` also ships the other agent's 4 unpushed, lib-only #108 commits (baseline tests green with
  them) — state that in the task report, do not "fix" it.
- **PROD workflow `12wj6h1TWqb0d4Dq` is never edited.** Seed edits go to STAGING `bqHstPDi84uOhTCJ` under
  `python3 scripts/olivia_wf.py lock --reason "#114 venue-today"`; `node --check` on the jsCode before the PUT;
  ONE deactivate→activate bounce in the same script run; `python3 scripts/olivia_leak_gate.py; echo "EXIT $?"`
  must print `GATE PASSED` / `EXIT 0` (never pipe through `tail`); **promote = Andy** (`python3 scripts/olivia_wf.py promote`).
- **Only Andy's phone (`17866578153`) is simulated on staging.** Staging replies DELIVER to Andy's WhatsApp — he knows.
- **Time rules already encoded (keep them):** never store a member timezone; the tool returns venue-local
  wording and the model repeats it verbatim; never say "your time"; `in N minutes` is computed server-side.
- **The proof must be taken while the Eastern date ≠ the Singapore date** — i.e. between 12:00 and 23:59
  US Eastern (Singapore is ET+12 during EDT). Outside that window the bug is invisible. Say the time of the probe in the report.
- **Every "it works" claim cites a live check**: vitest output, `/api/version` sha, a curl response, a staging reply text.

---

## File Structure

| File | Responsibility |
|---|---|
| `mds-digest-web/src/lib/schedule-day.ts` (create) | Pure: `localDate`, `dayLabel`, `venueNow`, `parseInstant`, `resolveDay`. No I/O. |
| `mds-digest-web/src/lib/schedule-day.test.ts` (create) | vitest for the above with an injected "now". |
| `mds-digest-web/src/app/api/olivia/schedule/route.ts` (modify) | `day` op → resolver; `next` op → `parseInstant`; `now_at_venue` on every response; delete the route's private `localDate` copy (import the lib one). |
| `Scorecard/scripts/olivia_loop/apply_114_venue_today.py` (create) | Staging patch: tool description + TODAY line + one #85 bullet; asserts each target string occurs exactly once; node --check; PUT; one bounce. |
| `Scorecard/OLIVIA_HANDBOOK.md` §4.9 "Timezones" paragraph + §13 trap; `OLIVIA_SPRINT_4.md` #114; handoff + logs | Docs. |

---

### Task 1: The resolver — `src/lib/schedule-day.ts` (TDD)

**Files:**
- Create: `/Users/Born/mds-digest-web/src/lib/schedule-day.ts`
- Create: `/Users/Born/mds-digest-web/src/lib/schedule-day.test.ts`

**Interfaces (Produces — Task 2 imports exactly these):**
```ts
export function localDate(iso: string, timeZone: string): string;            // "2026-08-23" in the zone
export function dayLabel(ymd: string): string;                               // "Sunday 23 August"
export function venueNow(nowIso: string, timeZone: string): string;          // "Sunday 23 Aug, 11:31 am Singapore time"
export function parseInstant(at: unknown, nowIso: string): Date;             // valid ISO -> that instant, else now
export type DayResolution = { date: string; how: "today" | "relative" | "weekday" | "explicit" | "fallback" };
export function resolveDay(at: unknown, nowIso: string, timeZone: string, window?: { first: string; last: string }): DayResolution;
```

- [ ] **Step 1: Write the failing tests**

```ts
// src/lib/schedule-day.test.ts
import { describe, expect, it } from "vitest";
import { dayLabel, localDate, parseInstant, resolveDay, venueNow } from "./schedule-day";

// Sunday 23 Aug 2026, 11:31 in Singapore == Saturday 22 Aug, 23:31 US Eastern.
// This is the exact moment Ian Sells asked "what's happening at the summit today?"
const NOW = "2026-08-23T03:31:00Z";
const TZ = "Asia/Singapore";
const WINDOW = { first: "2026-08-22", last: "2026-08-26" }; // Sat pre-event day .. Wed

describe("localDate", () => {
  it("gives the calendar date in the venue zone, not UTC", () => {
    expect(localDate(NOW, TZ)).toBe("2026-08-23");
    expect(localDate(NOW, "America/New_York")).toBe("2026-08-22");
  });
});

describe("resolveDay — relative words resolve in the venue zone", () => {
  it("no `at` is today at the venue", () => expect(resolveDay(undefined, NOW, TZ, WINDOW)).toEqual({ date: "2026-08-23", how: "today" }));
  it("'today' (any case/space) is today at the venue", () => {
    expect(resolveDay("today", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-23", how: "relative" });
    expect(resolveDay(" Today ", NOW, TZ, WINDOW).date).toBe("2026-08-23");
    expect(resolveDay("now", NOW, TZ, WINDOW).date).toBe("2026-08-23");
  });
  it("'tomorrow' and 'yesterday'", () => {
    expect(resolveDay("tomorrow", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-24", how: "relative" });
    expect(resolveDay("yesterday", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-22", how: "relative" });
  });
  it("a weekday names the event's own day with that weekday", () => {
    expect(resolveDay("monday", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-24", how: "weekday" });
    expect(resolveDay("Mon", NOW, TZ, WINDOW).date).toBe("2026-08-24");
    expect(resolveDay("on Tuesday", NOW, TZ, WINDOW).date).toBe("2026-08-25");
    expect(resolveDay("wed", NOW, TZ, WINDOW).date).toBe("2026-08-26");
    // the event's Saturday is the pre-event day that already passed — still the event's Saturday
    expect(resolveDay("saturday", NOW, TZ, WINDOW).date).toBe("2026-08-22");
  });
  it("a weekday outside the window is the next such day from venue-today", () => {
    expect(resolveDay("friday", NOW, TZ, WINDOW).date).toBe("2026-08-28");
    expect(resolveDay("friday", NOW, TZ).date).toBe("2026-08-28");
  });
  it("a bare date is taken as given", () => expect(resolveDay("2026-08-25", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-25", how: "explicit" }));
  it("a full instant is converted to the venue's date", () => {
    // Saturday 23:00 Eastern is already Sunday in Singapore
    expect(resolveDay("2026-08-22T23:00:00-04:00", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-23", how: "explicit" });
  });
  it("nonsense falls back to venue-today and says so", () => expect(resolveDay("whenever", NOW, TZ, WINDOW)).toEqual({ date: "2026-08-23", how: "fallback" }));
  it("non-string input does not throw", () => expect(resolveDay(42, NOW, TZ, WINDOW).date).toBe("2026-08-23"));
});

describe("labels", () => {
  it("venueNow names the weekday, date, time and the venue city", () => expect(venueNow(NOW, TZ)).toBe("Sunday 23 Aug, 11:31 am Singapore time"));
  it("dayLabel is the heading the layout rule wants", () => expect(dayLabel("2026-08-24")).toBe("Monday 24 August"));
});

describe("parseInstant", () => {
  it("keeps a valid instant", () => expect(parseInstant("2026-08-24T01:00:00Z", NOW).toISOString()).toBe("2026-08-24T01:00:00.000Z"));
  it("falls back to now for words and garbage (today used to become Invalid Date and empty the `next` list)", () => {
    expect(parseInstant("today", NOW).toISOString()).toBe("2026-08-23T03:31:00.000Z");
    expect(parseInstant(undefined, NOW).toISOString()).toBe("2026-08-23T03:31:00.000Z");
  });
});
```

- [ ] **Step 2: Run to verify failure** — `cd /Users/Born/mds-digest-web && npx vitest run src/lib/schedule-day.test.ts 2>&1 | tail -5`
Expected: `Failed to load url ./schedule-day` (module missing).

- [ ] **Step 3: Implement `src/lib/schedule-day.ts`**

```ts
// "Today" at an in-person event is the VENUE's day. The model that calls the
// schedule lane anchors on US Eastern (Answer Seed: "TODAY is … (US Eastern)")
// and on 2026-08-22 it sent at=2026-08-22 for a member standing in Singapore on
// Sunday the 23rd. So relative words are resolved HERE, in the event's zone, and
// never by the caller — the tool description tells the model to pass the word.

const WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];

export function localDate(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("en-CA", { year: "numeric", month: "2-digit", day: "2-digit", timeZone })
    .format(new Date(iso));
}

function addDays(ymd: string, n: number): string {
  const [y, m, d] = ymd.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10);
}

function weekdayOf(ymd: string): number {
  const [y, m, d] = ymd.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d)).getUTCDay(); // 0 = Sunday, on the calendar date itself
}

export function dayLabel(ymd: string): string {
  return new Intl.DateTimeFormat("en-GB", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" })
    .format(new Date(`${ymd}T12:00:00Z`));
}

export function venueNow(nowIso: string, timeZone: string): string {
  const shown = new Intl.DateTimeFormat("en-GB", {
    weekday: "long", day: "numeric", month: "short", hour: "numeric", minute: "2-digit", hour12: true, timeZone,
  }).format(new Date(nowIso));
  const city = timeZone.split("/").pop()?.replace(/_/g, " ") || timeZone;
  return `${shown} ${city} time`;
}

export function parseInstant(at: unknown, nowIso: string): Date {
  if (typeof at === "string" && at.trim()) {
    const d = new Date(at.trim());
    if (!isNaN(d.getTime())) return d;
  }
  return new Date(nowIso);
}

export type DayResolution = { date: string; how: "today" | "relative" | "weekday" | "explicit" | "fallback" };

/**
 * at: undefined | "today" | "now" | "tomorrow" | "yesterday" | a weekday name
 *     (3+ letters, optional "on/this/next") | YYYY-MM-DD | a full ISO instant.
 * window: the event's first and last local dates, so "monday" is the event's
 *     Monday even when asked on the Saturday before, never a Monday after it.
 */
export function resolveDay(
  at: unknown,
  nowIso: string,
  timeZone: string,
  window?: { first: string; last: string },
): DayResolution {
  const today = localDate(nowIso, timeZone);
  const raw = typeof at === "string" ? at.trim().toLowerCase().replace(/^(on|this|next)\s+/, "") : "";
  if (!raw) return { date: today, how: "today" };
  if (raw === "today" || raw === "now") return { date: today, how: "relative" };
  if (raw === "tomorrow") return { date: addDays(today, 1), how: "relative" };
  if (raw === "yesterday") return { date: addDays(today, -1), how: "relative" };

  const wd = raw.length >= 3 ? WEEKDAYS.findIndex((w) => w.startsWith(raw)) : -1;
  if (wd >= 0) {
    if (window) {
      for (let d = window.first; d <= window.last; d = addDays(d, 1)) {
        if (weekdayOf(d) === wd) return { date: d, how: "weekday" };
      }
    }
    let d = today;
    for (let i = 0; i < 7; i++) {
      if (weekdayOf(d) === wd) return { date: d, how: "weekday" };
      d = addDays(d, 1);
    }
  }

  const m = raw.match(/^(\d{4}-\d{2}-\d{2})(t.*)?$/);
  if (m) {
    if (m[2]) {
      // a full instant is a moment: its date IN THE VENUE ZONE
      const inst = new Date(String(at).trim());
      if (!isNaN(inst.getTime())) return { date: localDate(inst.toISOString(), timeZone), how: "explicit" };
    }
    return { date: m[1], how: "explicit" };
  }
  return { date: today, how: "fallback" };
}
```

- [ ] **Step 4: Run to verify pass** — `npx vitest run src/lib/schedule-day.test.ts 2>&1 | tail -5` → `1 passed` file, all tests green. Then the whole suite `npx vitest run 2>&1 | tail -4` → `6 passed` files (67 + new).
If `venueNow` renders `"11:31 am"` vs `"11:31 AM"` differently on Node's ICU, match the test to the **en-GB** output actually produced and keep lowercase am/pm consistent with `localLabel` in the route (it already uses en-GB hour12 — copy its exact options).

- [ ] **Step 5: Commit (mds-digest-web, Andy's author)**

```bash
cd /Users/Born/mds-digest-web
git add src/lib/schedule-day.ts src/lib/schedule-day.test.ts
git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "#114: venue-zone day resolver for the schedule lane (today/tomorrow/weekday/date/instant) + now_at_venue label"
```

---

### Task 2: Wire the route, deploy, prove it live

**Files:**
- Modify: `/Users/Born/mds-digest-web/src/app/api/olivia/schedule/route.ts` — lines 95–102 (delete the private `localDate`), ~209 (after `const tz = ev.timezone;`), 948 (`next`), 957–960 (`day`), and every `return NextResponse.json({` inside the `try` after the event lookup.

**Interfaces:**
- Consumes (Task 1): `localDate, dayLabel, venueNow, parseInstant, resolveDay` from `@/lib/schedule-day`.
- Produces (Task 3 relies on the field names): every success response has `now_at_venue: string`; the `day` op returns `{ day: "YYYY-MM-DD", day_label: "Sunday 23 August", resolved_from: DayResolution["how"], venue, activities }`.

- [ ] **Step 1: Edit the route**

Imports (top of file, after the supabase import):
```ts
import { dayLabel, localDate, parseInstant, resolveDay, venueNow } from "@/lib/schedule-day";
```
Delete the route's own `function localDate(...)` (lines 95–102) — same behaviour, now imported.

After `const tz = ev.timezone;` add:
```ts
    // The model does not know what day it is at the venue (it anchors on US
    // Eastern). Every answer carries the venue's now so it can say the day, and
    // every relative day the caller sends is resolved here, in this zone.
    const nowIso = new Date().toISOString();
    const now_at_venue = venueNow(nowIso, tz);
    const json = (body: Record<string, unknown>, init?: ResponseInit) =>
      NextResponse.json({ now_at_venue, ...body }, init);
```
Then, for every `return NextResponse.json({` that appears AFTER this line inside the `try` (the op responses — agenda, name-lookup, remind/reminders/unremind, recommend, people, partners, speakers, speaker, next, day, where, sessions, the `found: false` paths), replace with `return json({`. Error returns before the event lookup (`invalid json`, `phone required`, `no event`) stay as they are. Mechanical check: `grep -c "return NextResponse.json" route.ts` before vs after — the count after must equal the number of pre-event-lookup returns plus the `catch` block's (leave the catch as is).

`next` op:
```ts
    if (op === "next") {
      const from = parseInstant(body.at, nowIso);
```
`day` op:
```ts
    if (op === "day") {
      const window = acts.length
        ? { first: localDate(acts[0].starts_at, tz), last: localDate(acts[acts.length - 1].starts_at, tz) }
        : undefined;
      const r = resolveDay(body.at, nowIso, tz, window);
      const same = acts.filter((a) => localDate(a.starts_at, tz) === r.date).map(card);
      return json({ event: ev.title, timezone: tz, viewing, day: r.date, day_label: dayLabel(r.date),
        resolved_from: r.how, venue: venueBlock(same), activities: same });
    }
```
(`acts` is already ordered by `starts_at` from the query, so first/last are the event's first and last visible days.)

- [ ] **Step 2: Type-check + tests + build**
`npx tsc --noEmit -p . 2>&1 | tail -3` → no errors · `npx vitest run 2>&1 | tail -3` → all green · `npx next build 2>&1 | tail -5` → compiled (the route is listed). If `tsc` is not a script, `npx next build` is the type gate — quote its last lines.

- [ ] **Step 3: Commit + push (main) + wait for Render**

```bash
cd /Users/Born/mds-digest-web
git add src/app/api/olivia/schedule/route.ts
git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "#114: schedule lane resolves today/tomorrow/weekday in the venue zone and returns now_at_venue on every answer"
git push origin main
for i in $(seq 1 40); do sleep 15; V=$(curl -s https://digest.mds.co/api/version); echo "$V"; echo "$V" | grep -q "$(git rev-parse HEAD)" && break; done
```
Expected: `/api/version` returns the new sha within ~10 minutes. (If the worktree branch is used, merge `--ff-only` into `main` first; the other agent's uncommitted `src/lib/finder.test.ts` stays untouched in the working tree.)

- [ ] **Step 4: Live proof — while ET date ≠ SGT date (12:00–23:59 ET)**

Secret: the value the n8n `Answer Tool` node sends as `X-Olivia-Secret` (read it from the newest
`Scorecard/olivia_snapshots/prod_*post-promote.json` → node `Answer Tool` → `parameters.headerParameters.parameters[]`;
never print it).

```bash
curl -s https://digest.mds.co/api/olivia/schedule -H "X-Olivia-Secret: $SECRET" -H 'Content-Type: application/json' \
  -d '{"op":"day","at":"today","phone":"17866578153"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['now_at_venue'], d['day'], d['day_label'], d['resolved_from'], [a['name'] for a in d['activities']])"
```
Expected (probe taken Sat 22 Aug ET evening = Sun 23 Aug SGT): `Sunday 23 Aug, <hh:mm> am Singapore time 2026-08-23 Sunday 23 August relative [Arrivals, Early Mixer, Event Check-in & Swag Bag Pick-Up, Welcome Reception, Meet N' Speed - Speed Networking, Welcome Dinner]` — the plain-Member day-one set (6, the golden count). Also `{"op":"day","at":"2026-08-22",…}` (what the model used to send) still returns Saturday's list with `resolved_from: explicit` — a member naming a date is still honoured. And `{"op":"day","at":"tomorrow",…}` → `2026-08-24 Monday 24 August`. And `{"op":"next","at":"today",…}` → a non-empty `next` (previously Invalid Date → empty).

- [ ] **Step 5: Record** the three curl outputs (trimmed) and the `/api/version` sha in the task report.

---

### Task 3: Answer Seed (STAGING) — pass the word, trust now_at_venue; docs

**Files:**
- Create: `/Users/Born/Scorecard/scripts/olivia_loop/apply_114_venue_today.py` (copy the structure of `scripts/olivia_loop/apply_transcript_boundary_2025.py`: `EDITS = {node: [(old, new), …]}`, assert exactly one occurrence per `old`, `node --check` per changed node, PUT, deactivate→activate once).
- Modify (Scorecard): `OLIVIA_HANDBOOK.md` §4.9 Timezones paragraph + §13 trap; `OLIVIA_SPRINT_4.md` (#114 story/ACs/close block); `OLIVIA_NEXT_SESSION.md`; `SESSION_LOG_OLIVIA.md`; `SESSION_LOG.md` (one line).

**Interfaces:**
- Consumes (Task 2): response fields `now_at_venue`, `day_label`, `resolved_from`; `at` accepts words.

- [ ] **Step 1: The three edits, verbatim** (all in node `Answer Seed`; each `old` occurs exactly once in the current prod/staging jsCode — verified 2026-08-22):

Edit A — tool description, `old`:
```
day (one date, at=YYYY-MM-DD)
```
`new`:
```
day (one DAY - at=today | tomorrow | yesterday | a weekday name | YYYY-MM-DD. For today, tomorrow or a weekday pass the WORD, never a date you computed: the tool resolves it in the venue's zone and you do not know what day it is there)
```

Edit B — the TODAY line, `old`:
```
'TODAY is ' + today + ' (US Eastern). Anchor every past/upcoming judgment to this date.',
```
`new`:
```
'TODAY is ' + today + ' (US Eastern). Anchor every past/upcoming judgment to this date - EXCEPT at an in-person event: the venue can already be on the next calendar day (Singapore runs 12 hours ahead of Eastern). For anything at the Summit the day is what event_schedule returns in now_at_venue, never this line.',
```

Edit C — one bullet appended right after the existing bullet that begins `'- PICK THE OP BY WHAT THEY NAMED.` (insert a new array element after it), `new` line:
```
  '- TODAY / TOMORROW / A WEEKDAY AT THE SUMMIT (#114): \'what is happening today\' is op=day with at=today; tomorrow is at=tomorrow; a weekday is at=monday (the word). NEVER turn a relative day into a date yourself - you anchor on US Eastern and the venue is a day ahead for half of every day; Ian Sells asked on his Sunday and got Saturday. Open the answer with the day the tool resolved (day_label) and trust now_at_venue over the TODAY line for anything at the venue.',
```
(Implement Edit C as a replacement whose `old` is the full PICK-THE-OP bullet line and whose `new` is that same line followed by `\n` and the new bullet — so the "exactly once" assertion still holds.)

- [ ] **Step 2: Apply to staging**

```bash
cd /Users/Born/Scorecard
python3 scripts/olivia_wf.py lock --reason "#114 venue-today seed"
python3 scripts/olivia_loop/apply_114_venue_today.py          # prints: 3 replacements, node --check OK, PUT ok, bounced
python3 scripts/olivia_leak_gate.py; echo "EXIT $?"           # GATE PASSED … EXIT 0
python3 scripts/olivia_wf.py diff prod staging | tail -8      # changed: ['Answer Seed'] (+ the two webhook nodes, always)
```

- [ ] **Step 3: Staging probe (Andy's phone; replies land on his WhatsApp) — inside the 12:00–23:59 ET window**

```bash
python3 scripts/olivia_selftest.py --staging --questions "reset" "What's happening at the summit today?" "What's on tomorrow?"
```
Expected: the first reply opens with **Sunday, Aug 23** (not Saturday) and lists the day-one activities; the second opens with **Monday, Aug 24**. Read the staging execution for the tool call: `tool_args` must carry `"at":"today"` / `"at":"tomorrow"` (not a computed date). Quote the reply headers and the tool_args in the report. Then `python3 scripts/olivia_selftest.py --cleanup` if the run polluted Andy's transcript (per the script's own note).

- [ ] **Step 4: Docs.** In `OLIVIA_HANDBOOK.md` §4.9, extend the **Timezones** paragraph with:

```markdown
**"Today" is the venue's day (#114, 2026-08-22).** The model anchors on US Eastern; the Summit venue is
12 hours ahead, so for half of every day "today" is already tomorrow there. The schedule route resolves
`at=today|tomorrow|yesterday|<weekday>` in the event's zone (`src/lib/schedule-day.ts`) and returns
`now_at_venue` on every answer; the seed tells the model to pass the word, never a computed date. Virtual
events are not covered — the member's zone is unknown by design.
```
and in §13 add the trap: *A relative day computed by the model is wrong at any venue east of Eastern —
Ian Sells (Singapore, Sunday 11:30) got Saturday's list on 2026-08-22. Resolve relative days in code, in the
venue zone.* Board: #114 story (*As Ian in Singapore on Sunday, "what's happening today" returns Sunday*)
+ ACs (① route resolves relative words in the venue zone, vitest ② `now_at_venue` on every answer ③ seed
passes the word ④ live curl proof while ET≠SGT ⑤ staging reply says Sunday/Monday ⑥ promote = Andy) + close
block with the proofs. Handoff: *staging carries #114; Andy: `promote` then `unlock`.* Stream log entry + one index line.

- [ ] **Step 5: Commit (Scorecard)**

```bash
cd /Users/Born/Scorecard
git add scripts/olivia_loop/apply_114_venue_today.py OLIVIA_HANDBOOK.md OLIVIA_SPRINT_4.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md
git commit -m "#114: seed passes relative days as words, trusts now_at_venue at the venue (staging); handbook + board" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
Leave the staging lock to Andy's promote/unlock (state it in the handoff).

---

## Self-review notes

- Spec coverage: venue-zone "today" ✔ Task 1–2; model stops computing dates ✔ Task 3; proof while dates differ ✔ Tasks 2–3; virtual out of scope (stated).
- Type consistency: `resolveDay(at: unknown, nowIso, timeZone, window?)` and `parseInstant(at: unknown, nowIso)` used with the same signatures in Task 2; response fields `now_at_venue`/`day_label`/`resolved_from` named identically in Tasks 2 and 3.
- Latent bug fixed alongside (same lines, not scope creep): `next` with a non-ISO `at` produced `Invalid Date` and an empty list.
