# WA → FB Story Posts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Three times a week, pick the single best thread from the MDS WhatsApp chats, write it up as a short story, and put it in Slack as a copy-ready card so Andy can paste it into the private Facebook group.

**Architecture:** One secret-gated Next.js route in `mds-digest-web` (`/api/fbstory/draft`) composes seven small single-purpose modules under `src/lib/fbstory/`. Everything it reads already lives in the `digest` schema of Supabase — no Airtable writes, no Whapi calls. An n8n Schedule → HTTP Request workflow is the only trigger, and holds no logic. Meta removed Facebook Groups API publishing in 2024, so a human does the final paste; the system exists to make that paste cost one click of judgement.

**Tech Stack:** Next.js App Router (Node runtime), TypeScript, Vitest, Supabase PostgREST via the existing `sbRequest` helper, `@anthropic-ai/sdk`, Slack Web API `chat.postMessage`.

**Spec:** `docs/superpowers/specs/2026-09-01-wa-to-fb-story-posts-design.md`

**Working directory:** `/Users/Born/mds-digest-web` — a DIFFERENT repo from `/Users/Born/Scorecard`, where this plan lives. All file paths below are relative to `mds-digest-web`.

## Global Constraints

- **Never write to Airtable.** Airtable is the source of truth and Andy tests against it. This feature reads nothing from Airtable and writes nothing to it. All state lives in Supabase.
- **`digest.wa_messages.sender_member` holds an Airtable record id, not a name.** It joins `digest.members.airtable_id`. It does **not** join `at_member_id` — that resolves 0 of 665 rows. Verified live 2026-09-01.
- **PostgREST treats `+` in a URL query as a space.** Always send timestamps `Z`-suffixed (`2026-09-01T00:00:00Z`), never `+00:00`.
- **PostgREST caps a response at 1000 rows.** Never fetch the whole `members` table; filter with `airtable_id=in.(...)`.
- **Slack channel is `#automation-tests` = `C0AQ8USNQK0`.** It is already the default for `config.health.slackChannel`, so no new channel id is invented.
- **Anthropic key env var is `CENTURION_ANTHROPIC_API_KEY`**, deliberately not `ANTHROPIC_API_KEY`, to dodge the Claude Code empty-env collision. Reuse it.
- **Render has no staging tier: a push to `main` deploys to production.** Every task commits to a feature branch; nothing merges until Task 10.
- **Tests never call the Anthropic API or Supabase.** Prompt building, response parsing, thread assembly, and the privacy gate are pure functions and are tested as such. The two API-calling functions are thin wrappers with no logic to test.
- **Model:** `config.fbStory.model`, default `claude-opus-5`, overridable by `FB_STORY_MODEL`.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/lib/config.ts` (modify) | Add the `fbStory` config block |
| `src/lib/fbstory/types.ts` (create) | Shared types for the whole feature |
| `src/lib/fbstory/ledger.ts` (create) | Read/write `digest.fb_group_posts`; dedupe checks |
| `src/lib/fbstory/candidates.ts` (create) | Load daily summaries, drop blocklisted chats |
| `src/lib/fbstory/thread.ts` (create) | Load a chat window's raw messages, resolve names, order by reply, mint the story key |
| `src/lib/fbstory/rank.ts` (create) | One Claude call: pick a winner or return none |
| `src/lib/fbstory/write.ts` (create) | One Claude call: produce `post_text` + `members_named` |
| `src/lib/fbstory/gate.ts` (create) | Deterministic privacy checks. No LLM, no I/O |
| `src/lib/fbstory/slack.ts` (create) | Build and post the Slack card; post the quiet line |
| `src/app/api/fbstory/draft/route.ts` (create) | Compose the run; `?secret=`, `?dry=1` |
| `src/app/api/fbstory/interactivity/route.ts` (create) | Slack button handler |

Tests are colocated as `src/lib/fbstory/<name>.test.ts`, matching the existing convention (`src/lib/channels-classify.test.ts`).

---

## Task 1: Ledger table, config, and shared types

**Files:**
- Create: `src/lib/fbstory/types.ts`
- Create: `src/lib/fbstory/ledger.ts`
- Create: `src/lib/fbstory/ledger.test.ts`
- Modify: `src/lib/config.ts` (append a `fbStory` block to the exported `config` object, after the `health` block)

**Interfaces:**
- Consumes: `sbRequest` from `@/lib/supabase`, `config` from `@/lib/config`.
- Produces: types `Candidate`, `RankResult`, `ThreadMessage`, `Thread`, `DraftPost`, `LedgerRow`; functions `isAlreadyTold(told: LedgerRow[], storyKey: string, messageIds: string[]): string | null`, `loadRecentLedger(days: number): Promise<LedgerRow[]>`, `insertLedgerRow(row: LedgerRow): Promise<void>`, `markLedgerStatus(storyKey: string, status: LedgerStatus, skipReason?: string): Promise<void>`.

- [ ] **Step 1: Create the Supabase table**

Run this against Supabase project `nadtudwuwjhckotrngzn` (MCP `apply_migration`, name `fb_group_posts`):

```sql
create table if not exists digest.fb_group_posts (
  story_key    text primary key,
  chat_id      text not null,
  chat_name    text not null,
  window_start date not null,
  window_end   date not null,
  message_ids  text[] not null default '{}',
  draft_text   text,
  why_picked   text,
  confidence   numeric,
  status       text not null default 'draft',
  skip_reason  text,
  created_at   timestamptz not null default now(),
  posted_at    timestamptz,
  constraint fb_group_posts_status_chk
    check (status in ('draft','posted','skipped','blocked'))
);

create index if not exists fb_group_posts_created_idx
  on digest.fb_group_posts (created_at desc);
create index if not exists fb_group_posts_msgids_idx
  on digest.fb_group_posts using gin (message_ids);

notify pgrst, 'reload schema';
```

The trailing `notify` matters: PostgREST caches the schema and will 404 the new table until told to reload.

- [ ] **Step 2: Verify the table is reachable through PostgREST**

Run:

```bash
curl -s -H "apikey: $SUPABASE_SECRET_KEY" -H "Authorization: Bearer $SUPABASE_SECRET_KEY" -H "Accept-Profile: digest" "$SUPABASE_URL/rest/v1/fb_group_posts?select=story_key&limit=1"
```

Expected: `[]` — an empty array, not a 404. A 404 means the `notify` did not take; re-run it.

- [ ] **Step 3: Write `src/lib/fbstory/types.ts`**

```typescript
// Shared types for the WA → FB story-post feature.
// Spec: docs/superpowers/specs/2026-09-01-wa-to-fb-story-posts-design.md (in the Scorecard repo)

/** One daily chat summary, as mirrored into digest.summaries. */
export type Candidate = {
  summary_key: string;
  date: string; // YYYY-MM-DD
  chat_id: string;
  chat_name: string;
  tl_dr: string | null;
  summary_text: string | null;
  topics: string | null;
  msg_count: number | null;
  participant_count: number | null;
};

/** What the ranker returns. It works from summaries and has no message ids,
 *  so it never mints the story key — thread.ts does that. */
export type RankPick = {
  chat_id: string;
  window_start: string; // YYYY-MM-DD
  window_end: string; // YYYY-MM-DD
  topic: string;
  why: string;
  confidence: number; // 0..1
};
export type RankResult = { pick: RankPick } | { none: string };

/** A raw WA message with its sender resolved to a member name. */
export type ThreadMessage = {
  id: string;
  sender_member: string | null; // Airtable record id
  sender_name: string | null; // resolved via digest.members.airtable_id
  sent_at: string;
  text: string;
  reply_to: string | null;
};

export type Thread = {
  story_key: string; // `${chat_id}:${rootMessageId}`
  chat_id: string;
  chat_name: string;
  window_start: string;
  window_end: string;
  root_message_id: string;
  messages: ThreadMessage[]; // ordered
  message_ids: string[];
  member_names: string[]; // distinct resolved names present in the thread
};

/** What the writer returns. members_named is declared explicitly so the gate
 *  has an exact list to check rather than guessing at capitalised words. */
export type DraftPost = {
  post_text: string;
  members_named: string[];
};

export type LedgerStatus = "draft" | "posted" | "skipped" | "blocked";

export type LedgerRow = {
  story_key: string;
  chat_id: string;
  chat_name: string;
  window_start: string;
  window_end: string;
  message_ids: string[];
  draft_text: string | null;
  why_picked: string | null;
  confidence: number | null;
  status: LedgerStatus;
  skip_reason: string | null;
};
```

- [ ] **Step 4: Add the config block**

In `src/lib/config.ts`, immediately after the closing `},` of the `health:` block and before `baseUrl:`, insert:

```typescript
  // WA → FB story posts. Picks one WhatsApp thread 3x/week, writes it up, and
  // posts a copy-ready Slack card to #automation-tests for Andy to paste into
  // the private FB group (Meta removed Groups API publishing in 2024).
  // Reuses the Centurion Anthropic key and the health Slack bot/channel.
  fbStory: {
    anthropicApiKey: process.env.CENTURION_ANTHROPIC_API_KEY || "",
    model: process.env.FB_STORY_MODEL || "claude-opus-5",
    slackBotToken:
      process.env.FB_STORY_SLACK_BOT_TOKEN || process.env.CENTURION_SLACK_BOT_TOKEN || "",
    slackChannel: process.env.FB_STORY_SLACK_CHANNEL || "C0AQ8USNQK0", // #automation-tests
    slackSigningSecret:
      process.env.FB_STORY_SLACK_SIGNING_SECRET ||
      process.env.CENTURION_SLACK_SIGNING_SECRET ||
      "",
    // Shared secret the n8n scheduler passes as ?secret=. Unset ⇒ endpoint disabled.
    draftSecret: process.env.FB_STORY_SECRET || "",
    lookbackDays: Number(process.env.FB_STORY_LOOKBACK_DAYS || 7),
    minConfidence: Number(process.env.FB_STORY_MIN_CONFIDENCE || 0.7),
    // Chats never surfaced to the FB group. Ships empty: all 18 chats eligible.
    // Comma-separated chat_id values.
    excludedChatIds: (process.env.FB_STORY_EXCLUDED_CHATS || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
  },
```

Do **not** add any of these to the `required` array at the top of the file — every one has a fallback, so a missing var must not stop the app booting.

- [ ] **Step 5: Write the failing test for the dedupe check**

Create `src/lib/fbstory/ledger.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { isAlreadyTold } from "./ledger";
import type { LedgerRow } from "./types";

function row(over: Partial<LedgerRow>): LedgerRow {
  return {
    story_key: "chatA:m1",
    chat_id: "chatA",
    chat_name: "MDS Trading",
    window_start: "2026-08-25",
    window_end: "2026-08-31",
    message_ids: ["m1", "m2"],
    draft_text: "…",
    why_picked: "…",
    confidence: 0.8,
    status: "posted",
    skip_reason: null,
    ...over,
  };
}

describe("isAlreadyTold", () => {
  it("returns null when nothing matches", () => {
    expect(isAlreadyTold([row({})], "chatB:m9", ["m9"])).toBeNull();
  });

  it("catches an exact story-key repeat", () => {
    expect(isAlreadyTold([row({})], "chatA:m1", ["m1"])).toMatch(/story key/i);
  });

  it("catches a re-rooted thread that overlaps on a message id", () => {
    // Different root ⇒ different story key, but m2 was already told.
    expect(isAlreadyTold([row({})], "chatA:m0", ["m0", "m2"])).toMatch(/message/i);
  });

  it("ignores skipped and blocked rows, so a rejected story can come back", () => {
    const skipped = row({ status: "skipped" });
    const blocked = row({ status: "blocked" });
    expect(isAlreadyTold([skipped, blocked], "chatA:m1", ["m1", "m2"])).toBeNull();
  });

  it("treats a draft as told, so a double-fire cannot produce two cards", () => {
    expect(isAlreadyTold([row({ status: "draft" })], "chatA:m1", ["m1"])).toMatch(/story key/i);
  });
});
```

- [ ] **Step 6: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/ledger.test.ts`
Expected: FAIL — cannot resolve `./ledger`.

- [ ] **Step 7: Write `src/lib/fbstory/ledger.ts`**

```typescript
// Read/write digest.fb_group_posts — the record of what has been told, and the
// only thing standing between us and telling the same story twice.
// SERVER-ONLY (sbRequest uses the secret key).

import { sbRequest } from "@/lib/supabase";
import type { LedgerRow, LedgerStatus } from "./types";

/** Rows that count as "told". A skipped or blocked story is fair game again:
 *  skipping means the draft was bad, not that the story was used up. */
const TOLD: LedgerStatus[] = ["draft", "posted"];

/**
 * Two dedupe axes. The story key catches the same thread re-picked. The
 * message-id overlap catches the case the key alone misses: a cluster with no
 * replies roots on the earliest message in the window, so an overlapping
 * window can re-root it into a different key over the same conversation.
 * Returns a human-readable reason, or null when the story is new.
 */
export function isAlreadyTold(
  told: LedgerRow[],
  storyKey: string,
  messageIds: string[],
): string | null {
  const live = told.filter((r) => TOLD.includes(r.status));
  if (live.some((r) => r.story_key === storyKey)) {
    return `already told: story key ${storyKey}`;
  }
  const seen = new Set(live.flatMap((r) => r.message_ids));
  const overlap = messageIds.filter((id) => seen.has(id));
  if (overlap.length > 0) {
    return `already told: ${overlap.length} message(s) overlap a previous story (${overlap[0]})`;
  }
  return null;
}

/** Ledger rows from the last `days` days, newest first. */
export async function loadRecentLedger(days: number): Promise<LedgerRow[]> {
  const since = new Date(Date.now() - days * 86_400_000).toISOString().replace(/\.\d+Z$/, "Z");
  return sbRequest<LedgerRow[]>(
    `fb_group_posts?created_at=gte.${since}` +
      `&select=story_key,chat_id,chat_name,window_start,window_end,message_ids,draft_text,why_picked,confidence,status,skip_reason` +
      `&order=created_at.desc&limit=200`,
  );
}

export async function insertLedgerRow(row: LedgerRow): Promise<void> {
  await sbRequest("fb_group_posts", {
    method: "POST",
    body: row,
    prefer: "return=minimal,resolution=merge-duplicates",
  });
}

export async function markLedgerStatus(
  storyKey: string,
  status: LedgerStatus,
  skipReason?: string,
): Promise<void> {
  await sbRequest(`fb_group_posts?story_key=eq.${encodeURIComponent(storyKey)}`, {
    method: "PATCH",
    body: {
      status,
      skip_reason: skipReason ?? null,
      ...(status === "posted" ? { posted_at: new Date().toISOString() } : {}),
    },
    prefer: "return=minimal",
  });
}
```

Note the `.replace(/\.\d+Z$/, "Z")` — it keeps the timestamp `Z`-suffixed. A `+00:00` offset would be read by PostgREST as a space and silently break the filter.

- [ ] **Step 8: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/ledger.test.ts`
Expected: PASS, 5 tests.

- [ ] **Step 9: Typecheck and commit**

```bash
cd /Users/Born/mds-digest-web
git checkout -b fbstory
npx tsc --noEmit
git add src/lib/fbstory/types.ts src/lib/fbstory/ledger.ts src/lib/fbstory/ledger.test.ts src/lib/config.ts
git commit -m "feat(fbstory): ledger table, config block, shared types"
```

---

## Task 2: Candidate loading

**Files:**
- Create: `src/lib/fbstory/candidates.ts`
- Create: `src/lib/fbstory/candidates.test.ts`

**Interfaces:**
- Consumes: `Candidate` from `./types`, `sbRequest` from `@/lib/supabase`, `config` from `@/lib/config`.
- Produces: `selectCandidates(rows: Candidate[], excludedChatIds: string[]): Candidate[]`, `loadCandidates(days: number, asof?: Date): Promise<Candidate[]>`, `windowBounds(days: number, today?: Date): { start: string; end: string }`.

- [ ] **Step 1: Write the failing test**

Create `src/lib/fbstory/candidates.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { selectCandidates, windowBounds } from "./candidates";
import type { Candidate } from "./types";

function cand(over: Partial<Candidate>): Candidate {
  return {
    summary_key: "k",
    date: "2026-08-30",
    chat_id: "chatA",
    chat_name: "MDS Trading",
    tl_dr: "Something happened.",
    summary_text: "## MDS Trading\n- a thing",
    topics: "crypto",
    msg_count: 20,
    participant_count: 5,
    ...over,
  };
}

describe("selectCandidates", () => {
  it("keeps everything when nothing is excluded", () => {
    const rows = [cand({}), cand({ chat_id: "chatB" })];
    expect(selectCandidates(rows, [])).toHaveLength(2);
  });

  it("drops blocklisted chats before any LLM sees them", () => {
    const rows = [cand({}), cand({ chat_id: "chatB" })];
    expect(selectCandidates(rows, ["chatB"]).map((r) => r.chat_id)).toEqual(["chatA"]);
  });

  it("drops days with no content, which carry no story", () => {
    const rows = [cand({}), cand({ tl_dr: null, summary_text: null })];
    expect(selectCandidates(rows, [])).toHaveLength(1);
  });

  it("drops days too quiet to contain a thread", () => {
    const rows = [cand({}), cand({ msg_count: 2 })];
    expect(selectCandidates(rows, [])).toHaveLength(1);
  });
});

describe("windowBounds", () => {
  it("returns an inclusive N-day window ending today", () => {
    expect(windowBounds(7, new Date("2026-09-01T12:00:00Z"))).toEqual({
      start: "2026-08-26",
      end: "2026-09-01",
    });
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/candidates.test.ts`
Expected: FAIL — cannot resolve `./candidates`.

- [ ] **Step 3: Write `src/lib/fbstory/candidates.ts`**

```typescript
// Loads the daily chat summaries a run may draw a story from.
// Pure filtering is split from I/O so the rules are testable without a network.

import { sbRequest } from "@/lib/supabase";
import type { Candidate } from "./types";

/** A day with fewer messages than this cannot hold a thread worth telling. */
const MIN_MSGS = 5;

/** Inclusive window of `days` days ending today, as YYYY-MM-DD. */
export function windowBounds(days: number, today = new Date()): { start: string; end: string } {
  const end = new Date(today);
  const start = new Date(end.getTime() - (days - 1) * 86_400_000);
  const fmt = (d: Date) => d.toISOString().slice(0, 10);
  return { start: fmt(start), end: fmt(end) };
}

/** Blocklist and emptiness filtering. Runs BEFORE any LLM call, so an excluded
 *  chat's content is never sent anywhere. */
export function selectCandidates(rows: Candidate[], excludedChatIds: string[]): Candidate[] {
  const excluded = new Set(excludedChatIds);
  return rows.filter((r) => {
    if (excluded.has(r.chat_id)) return false;
    if (!r.tl_dr && !r.summary_text) return false;
    if ((r.msg_count ?? 0) < MIN_MSGS) return false;
    return true;
  });
}

// `asof` anchors the window to a past date. Production never passes it; the
// backfill does, which is how a dozen sample drafts get read before the first
// card ever reaches Slack.
export async function loadCandidates(days: number, asof?: Date): Promise<Candidate[]> {
  const { start, end } = windowBounds(days, asof);
  return sbRequest<Candidate[]>(
    `summaries?period_type=eq.daily&date=gte.${start}&date=lte.${end}` +
      `&select=summary_key,date,chat_id,chat_name,tl_dr,summary_text,topics,msg_count,participant_count` +
      `&order=date.desc&limit=500`,
  );
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/candidates.test.ts`
Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/candidates.ts src/lib/fbstory/candidates.test.ts
git commit -m "feat(fbstory): candidate loading with blocklist and quiet-day filtering"
```

---

## Task 3: Thread reconstruction

**Files:**
- Create: `src/lib/fbstory/thread.ts`
- Create: `src/lib/fbstory/thread.test.ts`

**Interfaces:**
- Consumes: `ThreadMessage`, `Thread`, `RankPick` from `./types`, `sbRequest` from `@/lib/supabase`.
- Produces: `buildThread(pick, chatName, rows, nameByRecordId): Thread`, `loadThread(pick: RankPick, chatName: string): Promise<Thread>`.

Row shape from Supabase is `RawMessage = { id, sender_member, sent_at, text, reply_to }`.

- [ ] **Step 1: Write the failing test**

Create `src/lib/fbstory/thread.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { buildThread } from "./thread";
import type { RankPick } from "./types";

const pick: RankPick = {
  chat_id: "chatA",
  window_start: "2026-08-25",
  window_end: "2026-08-31",
  topic: "pricing",
  why: "a real question got a real answer",
  confidence: 0.9,
};

const names = new Map([
  ["recAAA", "Zach Miller"],
  ["recBBB", "Faizan Khan"],
]);

describe("buildThread", () => {
  it("resolves sender record ids to member names", () => {
    const t = buildThread(
      pick,
      "MDS Trading",
      [{ id: "m1", sender_member: "recAAA", sent_at: "2026-08-26T10:00:00Z", text: "hi", reply_to: null }],
      names,
    );
    expect(t.messages[0].sender_name).toBe("Zach Miller");
    expect(t.member_names).toEqual(["Zach Miller"]);
  });

  it("leaves an unresolvable sender null rather than inventing a name", () => {
    const t = buildThread(
      pick,
      "MDS Trading",
      [{ id: "m1", sender_member: "recZZZ", sent_at: "2026-08-26T10:00:00Z", text: "hi", reply_to: null }],
      names,
    );
    expect(t.messages[0].sender_name).toBeNull();
    expect(t.member_names).toEqual([]);
  });

  it("orders messages oldest first", () => {
    const t = buildThread(
      pick,
      "MDS Trading",
      [
        { id: "m2", sender_member: "recBBB", sent_at: "2026-08-26T11:00:00Z", text: "second", reply_to: null },
        { id: "m1", sender_member: "recAAA", sent_at: "2026-08-26T10:00:00Z", text: "first", reply_to: null },
      ],
      names,
    );
    expect(t.messages.map((m) => m.id)).toEqual(["m1", "m2"]);
  });

  it("roots the story on the earliest message of the largest reply component", () => {
    // m1 stands alone; m5 ← m6 ← m7 is the real conversation.
    const t = buildThread(
      pick,
      "MDS Trading",
      [
        { id: "m1", sender_member: "recAAA", sent_at: "2026-08-26T09:00:00Z", text: "lone", reply_to: null },
        { id: "m5", sender_member: "recAAA", sent_at: "2026-08-26T10:00:00Z", text: "q", reply_to: null },
        { id: "m6", sender_member: "recBBB", sent_at: "2026-08-26T10:05:00Z", text: "a", reply_to: "m5" },
        { id: "m7", sender_member: "recAAA", sent_at: "2026-08-26T10:09:00Z", text: "thanks", reply_to: "m6" },
      ],
      names,
    );
    expect(t.root_message_id).toBe("m5");
    expect(t.story_key).toBe("chatA:m5");
  });

  it("roots on the earliest message when nothing is a reply", () => {
    const t = buildThread(
      pick,
      "MDS Trading",
      [
        { id: "m2", sender_member: "recAAA", sent_at: "2026-08-26T11:00:00Z", text: "b", reply_to: null },
        { id: "m1", sender_member: "recBBB", sent_at: "2026-08-26T10:00:00Z", text: "a", reply_to: null },
      ],
      names,
    );
    expect(t.root_message_id).toBe("m1");
  });

  it("carries every message id, which is the second dedupe axis", () => {
    const t = buildThread(
      pick,
      "MDS Trading",
      [
        { id: "m1", sender_member: "recAAA", sent_at: "2026-08-26T10:00:00Z", text: "a", reply_to: null },
        { id: "m2", sender_member: "recBBB", sent_at: "2026-08-26T10:05:00Z", text: "b", reply_to: "m1" },
      ],
      names,
    );
    expect(t.message_ids).toEqual(["m1", "m2"]);
  });

  it("drops empty messages, which are media with no text and carry no story", () => {
    const t = buildThread(
      pick,
      "MDS Trading",
      [
        { id: "m1", sender_member: "recAAA", sent_at: "2026-08-26T10:00:00Z", text: "", reply_to: null },
        { id: "m2", sender_member: "recBBB", sent_at: "2026-08-26T10:05:00Z", text: "real", reply_to: null },
      ],
      names,
    );
    expect(t.message_ids).toEqual(["m2"]);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/thread.test.ts`
Expected: FAIL — cannot resolve `./thread`.

- [ ] **Step 3: Write `src/lib/fbstory/thread.ts`**

```typescript
// Turns a ranker pick into an ordered, name-resolved thread, and mints the
// story key the ledger dedupes on.
//
// TRAP: digest.wa_messages.sender_member is an AIRTABLE RECORD ID, not a name,
// and it joins digest.members.airtable_id. It does NOT join at_member_id —
// that resolves 0 of 665 rows over the last 7 days. Verified live 2026-09-01.

import { sbRequest } from "@/lib/supabase";
import type { RankPick, Thread, ThreadMessage } from "./types";

export type RawMessage = {
  id: string;
  sender_member: string | null;
  sent_at: string;
  text: string | null;
  reply_to: string | null;
};

/**
 * Root = the earliest message of the largest connected reply component, so the
 * key tracks the conversation rather than the window it was noticed in. With no
 * replies at all, root = the earliest message; that case is window-dependent,
 * which is exactly why the ledger also dedupes on message-id overlap.
 */
function pickRoot(messages: ThreadMessage[]): string {
  const byId = new Map(messages.map((m) => [m.id, m]));
  // Union-find would be overkill for a week of one chat; walk parents instead.
  const rootOf = new Map<string, string>();
  for (const m of messages) {
    let cur = m;
    const seen = new Set<string>([cur.id]);
    while (cur.reply_to && byId.has(cur.reply_to) && !seen.has(cur.reply_to)) {
      seen.add(cur.reply_to);
      cur = byId.get(cur.reply_to)!;
    }
    rootOf.set(m.id, cur.id);
  }
  const sizes = new Map<string, number>();
  for (const root of rootOf.values()) sizes.set(root, (sizes.get(root) ?? 0) + 1);

  let best = messages[0].id;
  let bestSize = -1;
  for (const m of messages) {
    const size = sizes.get(m.id) ?? 0;
    // messages is already oldest-first, so the first hit at a given size wins
    // and ties resolve to the earlier message deterministically.
    if (size > bestSize) {
      bestSize = size;
      best = m.id;
    }
  }
  return best;
}

export function buildThread(
  pick: RankPick,
  chatName: string,
  rows: RawMessage[],
  nameByRecordId: Map<string, string>,
): Thread {
  const messages: ThreadMessage[] = rows
    .filter((r) => (r.text ?? "").trim().length > 0)
    .map((r) => ({
      id: r.id,
      sender_member: r.sender_member,
      sender_name: (r.sender_member && nameByRecordId.get(r.sender_member)) || null,
      sent_at: r.sent_at,
      text: (r.text ?? "").trim(),
      reply_to: r.reply_to,
    }))
    .sort((a, b) => a.sent_at.localeCompare(b.sent_at));

  if (messages.length === 0) {
    throw new Error(`No messages with text in ${chatName} for ${pick.window_start}..${pick.window_end}`);
  }

  const root = pickRoot(messages);
  const memberNames = [...new Set(messages.map((m) => m.sender_name).filter((n): n is string => !!n))];

  return {
    story_key: `${pick.chat_id}:${root}`,
    chat_id: pick.chat_id,
    chat_name: chatName,
    window_start: pick.window_start,
    window_end: pick.window_end,
    root_message_id: root,
    messages,
    message_ids: messages.map((m) => m.id),
    member_names: memberNames,
  };
}

export async function loadThread(pick: RankPick, chatName: string): Promise<Thread> {
  // Z-suffixed: PostgREST reads a `+` in a query string as a space.
  const from = `${pick.window_start}T00:00:00Z`;
  const to = `${pick.window_end}T23:59:59Z`;
  const rows = await sbRequest<RawMessage[]>(
    `wa_messages?chat_id=eq.${encodeURIComponent(pick.chat_id)}` +
      `&sent_at=gte.${from}&sent_at=lte.${to}` +
      `&select=id,sender_member,sent_at,text,reply_to&order=sent_at.asc&limit=1000`,
  );

  // Fetch only the members involved — never the whole table, which PostgREST
  // caps at 1000 rows.
  const ids = [...new Set(rows.map((r) => r.sender_member).filter((v): v is string => !!v))];
  const nameByRecordId = new Map<string, string>();
  if (ids.length > 0) {
    const members = await sbRequest<Array<{ airtable_id: string; name: string | null; full_name: string | null }>>(
      `members?airtable_id=in.(${ids.map((i) => `"${i}"`).join(",")})&select=airtable_id,name,full_name`,
    );
    for (const m of members) {
      const n = m.full_name || m.name;
      if (n) nameByRecordId.set(m.airtable_id, n);
    }
  }

  return buildThread(pick, chatName, rows, nameByRecordId);
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/thread.test.ts`
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/thread.ts src/lib/fbstory/thread.test.ts
git commit -m "feat(fbstory): thread reconstruction, name resolution, story key"
```

---

## Task 4: The privacy gate

**Files:**
- Create: `src/lib/fbstory/gate.ts`
- Create: `src/lib/fbstory/gate.test.ts`

**Interfaces:**
- Consumes: `Thread`, `DraftPost` from `./types`.
- Produces: `normalise(s: string): string[]`, `longestVerbatimRun(draft: string, sources: string[]): number`, `checkDraft(draft: DraftPost, thread: Thread, knownMembers: Set<string>): { ok: true } | { ok: false; reason: string }`.

Named-and-paraphrased is the one rule that becomes a real incident if it slips, so it lives in code rather than in a prompt.

- [ ] **Step 1: Write the failing test**

Create `src/lib/fbstory/gate.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { checkDraft, longestVerbatimRun } from "./gate";
import type { DraftPost, Thread } from "./types";

const thread: Thread = {
  story_key: "chatA:m1",
  chat_id: "chatA",
  chat_name: "MDS Trading",
  window_start: "2026-08-25",
  window_end: "2026-08-31",
  root_message_id: "m1",
  message_ids: ["m1", "m2"],
  member_names: ["Zach Miller", "Faizan Khan"],
  messages: [
    {
      id: "m1",
      sender_member: "recAAA",
      sender_name: "Zach Miller",
      sent_at: "2026-08-26T10:00:00Z",
      text: "I moved our whole catalogue onto a single supplier last quarter and it halved our lead time",
      reply_to: null,
    },
    {
      id: "m2",
      sender_member: "recBBB",
      sender_name: "Faizan Khan",
      sent_at: "2026-08-26T10:05:00Z",
      text: "How did you handle the risk of that supplier going down?",
      reply_to: "m1",
    },
  ],
};

const known = new Set(["Zach Miller", "Faizan Khan", "Louisa Grant"]);

function draft(over: Partial<DraftPost>): DraftPost {
  return {
    post_text: "Zach consolidated to one supplier and cut lead times sharply. Faizan pushed on the risk.",
    members_named: ["Zach Miller", "Faizan Khan"],
    ...over,
  };
}

describe("longestVerbatimRun", () => {
  it("is zero for genuine paraphrase", () => {
    expect(longestVerbatimRun("He consolidated suppliers and lead times fell.", [thread.messages[0].text])).toBeLessThan(8);
  });

  it("counts a long lifted run", () => {
    expect(
      longestVerbatimRun("He said he moved our whole catalogue onto a single supplier last quarter and it worked", [
        thread.messages[0].text,
      ]),
    ).toBeGreaterThanOrEqual(8);
  });

  it("ignores punctuation and case, so smart quotes cannot smuggle a quote through", () => {
    expect(
      longestVerbatimRun("HOW DID YOU HANDLE THE RISK OF THAT SUPPLIER GOING DOWN!!!", [thread.messages[1].text]),
    ).toBeGreaterThanOrEqual(8);
  });
});

describe("checkDraft", () => {
  it("passes a clean paraphrased draft", () => {
    expect(checkDraft(draft({}), thread, known)).toEqual({ ok: true });
  });

  it("blocks a draft that lifts eight or more words verbatim", () => {
    const bad = draft({
      post_text: "Zach moved our whole catalogue onto a single supplier last quarter, and it paid off.",
    });
    const out = checkDraft(bad, thread, known);
    expect(out.ok).toBe(false);
    expect(out.ok === false && out.reason).toMatch(/verbatim/i);
  });

  it("blocks a declared name that is not a real member", () => {
    const bad = draft({ post_text: "Jordan Vale had the answer.", members_named: ["Jordan Vale"] });
    const out = checkDraft(bad, thread, known);
    expect(out.ok).toBe(false);
    expect(out.ok === false && out.reason).toMatch(/not a member/i);
  });

  it("blocks a thread member named in the prose but left undeclared", () => {
    const bad = draft({ post_text: "Zach Miller and Faizan Khan worked it out.", members_named: ["Zach Miller"] });
    const out = checkDraft(bad, thread, known);
    expect(out.ok).toBe(false);
    expect(out.ok === false && out.reason).toMatch(/undeclared/i);
  });

  it("accepts a first-name-only credit for a declared member", () => {
    const ok = draft({ post_text: "Zach consolidated suppliers; Faizan pushed back.", members_named: ["Zach Miller", "Faizan Khan"] });
    expect(checkDraft(ok, thread, known)).toEqual({ ok: true });
  });

  it("blocks an empty draft rather than posting a blank card", () => {
    const out = checkDraft(draft({ post_text: "   " }), thread, known);
    expect(out.ok).toBe(false);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/gate.test.ts`
Expected: FAIL — cannot resolve `./gate`.

- [ ] **Step 3: Write `src/lib/fbstory/gate.ts`**

```typescript
// Deterministic privacy checks. No LLM, no I/O.
//
// Andy's rule for the FB group is "named, paraphrased": members get credit,
// their exact words do not leave the WhatsApp chat. That is the one rule here
// whose failure is an actual incident, so it is enforced in code. A prompt
// instruction is a hope; this is a gate.

import type { DraftPost, Thread } from "./types";

/** Words to compare on: lowercased, punctuation and whitespace stripped. */
export function normalise(s: string): string[] {
  return s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/)
    .filter(Boolean);
}

const MAX_RUN = 8;

/** Length of the longest run of consecutive words the draft shares with any
 *  source message. Compared normalised, so smart quotes, casing and stray
 *  punctuation cannot smuggle a quote past it. */
export function longestVerbatimRun(draft: string, sources: string[]): number {
  const d = normalise(draft);
  let longest = 0;
  for (const src of sources) {
    const s = normalise(src);
    // Classic LCSubstring over word arrays. Threads are a few dozen short
    // messages, so the quadratic cost is irrelevant here.
    const prev = new Array<number>(s.length + 1).fill(0);
    for (let i = 1; i <= d.length; i++) {
      let diagonal = 0;
      for (let j = 1; j <= s.length; j++) {
        const above = prev[j];
        prev[j] = d[i - 1] === s[j - 1] ? diagonal + 1 : 0;
        if (prev[j] > longest) longest = prev[j];
        diagonal = above;
      }
    }
  }
  return longest;
}

export function checkDraft(
  draft: DraftPost,
  thread: Thread,
  knownMembers: Set<string>,
): { ok: true } | { ok: false; reason: string } {
  const text = draft.post_text.trim();
  if (!text) return { ok: false, reason: "draft is empty" };

  const run = longestVerbatimRun(text, thread.messages.map((m) => m.text));
  if (run >= MAX_RUN) {
    return { ok: false, reason: `draft reuses ${run} consecutive words verbatim from a WhatsApp message (limit ${MAX_RUN - 1})` };
  }

  for (const name of draft.members_named) {
    if (!knownMembers.has(name)) {
      return { ok: false, reason: `"${name}" is declared in members_named but is not a member` };
    }
  }

  // Anyone from the thread who shows up in the prose must have been declared.
  // Checked on full name and on first name, since the writer credits people the
  // way the group would say it.
  const declared = new Set(draft.members_named.flatMap((n) => [n, n.split(" ")[0]]));
  const haystack = ` ${text} `;
  for (const name of thread.member_names) {
    if (declared.has(name)) continue;
    const first = name.split(" ")[0];
    const mentioned =
      haystack.includes(` ${name} `) ||
      new RegExp(`\\b${first.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`).test(text);
    if (mentioned && !declared.has(first)) {
      return { ok: false, reason: `"${name}" appears in the post but is undeclared in members_named` };
    }
  }

  return { ok: true };
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/gate.test.ts`
Expected: PASS, 9 tests.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/gate.ts src/lib/fbstory/gate.test.ts
git commit -m "feat(fbstory): privacy gate — verbatim-run and member-name checks"
```

---

## Task 5: The ranker

**Files:**
- Create: `src/lib/fbstory/rank.ts`
- Create: `src/lib/fbstory/rank.test.ts`

**Interfaces:**
- Consumes: `Candidate`, `LedgerRow`, `RankResult` from `./types`, `config` from `@/lib/config`, `Anthropic` from `@anthropic-ai/sdk`.
- Produces: `buildRankPrompt(candidates: Candidate[], recent: LedgerRow[]): string`, `parseRankResult(raw: string): RankResult`, `rankStory(candidates: Candidate[], recent: LedgerRow[]): Promise<RankResult>`.

- [ ] **Step 1: Write the failing test**

Create `src/lib/fbstory/rank.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { buildRankPrompt, parseRankResult } from "./rank";
import type { Candidate, LedgerRow } from "./types";

const candidates: Candidate[] = [
  {
    summary_key: "k1",
    date: "2026-08-30",
    chat_id: "chatA",
    chat_name: "MDS Trading",
    tl_dr: "ZEC hype.",
    summary_text: "## MDS Trading\n- ZEC ETF",
    topics: "crypto",
    msg_count: 13,
    participant_count: 6,
  },
];

describe("buildRankPrompt", () => {
  it("includes each candidate's chat, date and summary", () => {
    const p = buildRankPrompt(candidates, []);
    expect(p).toContain("MDS Trading");
    expect(p).toContain("2026-08-30");
    expect(p).toContain("ZEC ETF");
  });

  it("lists skipped stories so the ranker learns what was rejected", () => {
    const skipped: LedgerRow[] = [
      {
        story_key: "chatA:m1",
        chat_id: "chatA",
        chat_name: "MDS Trading",
        window_start: "2026-08-18",
        window_end: "2026-08-24",
        message_ids: ["m1"],
        draft_text: "…",
        why_picked: "price chatter",
        confidence: 0.75,
        status: "skipped",
        skip_reason: "too speculative for the group",
      },
    ];
    const p = buildRankPrompt(candidates, skipped);
    expect(p).toContain("too speculative for the group");
  });

  it("does not leak already-told drafts back in as candidates", () => {
    const posted: LedgerRow[] = [
      {
        story_key: "chatA:m9",
        chat_id: "chatA",
        chat_name: "MDS Trading",
        window_start: "2026-08-18",
        window_end: "2026-08-24",
        message_ids: ["m9"],
        draft_text: "SECRET DRAFT BODY",
        why_picked: "good thread",
        confidence: 0.9,
        status: "posted",
        skip_reason: null,
      },
    ];
    expect(buildRankPrompt(candidates, posted)).not.toContain("SECRET DRAFT BODY");
  });
});

describe("parseRankResult", () => {
  it("parses a pick", () => {
    const out = parseRankResult(
      JSON.stringify({
        chat_id: "chatA",
        window_start: "2026-08-25",
        window_end: "2026-08-31",
        topic: "supplier consolidation",
        why: "a real question got a real answer",
        confidence: 0.82,
      }),
    );
    expect("pick" in out && out.pick.topic).toBe("supplier consolidation");
  });

  it("parses a none verdict", () => {
    const out = parseRankResult(JSON.stringify({ none: "nothing above small talk" }));
    expect("none" in out && out.none).toBe("nothing above small talk");
  });

  it("throws on unparseable output rather than guessing", () => {
    expect(() => parseRankResult("not json")).toThrow();
  });

  it("throws when confidence is out of range", () => {
    expect(() =>
      parseRankResult(
        JSON.stringify({ chat_id: "a", window_start: "2026-08-25", window_end: "2026-08-31", topic: "t", why: "w", confidence: 4 }),
      ),
    ).toThrow();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/rank.test.ts`
Expected: FAIL — cannot resolve `./rank`.

- [ ] **Step 3: Write `src/lib/fbstory/rank.ts`**

```typescript
// One Claude call: given a week of daily chat summaries, pick the single best
// thread to tell the Facebook group about — or say there isn't one.
//
// Saying "none" is a first-class answer. The cadence is a ceiling, not a
// schedule: a thin week should post less rather than post filler.

import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { config } from "@/lib/config";
import type { Candidate, LedgerRow, RankResult } from "./types";

const PickSchema = z.object({
  chat_id: z.string().min(1),
  window_start: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  window_end: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  topic: z.string().min(1),
  why: z.string().min(1),
  confidence: z.number().min(0).max(1),
});
const NoneSchema = z.object({ none: z.string().min(1) });

const OUTPUT_SCHEMA = {
  type: "object",
  oneOf: [
    {
      type: "object",
      properties: {
        chat_id: { type: "string" },
        window_start: { type: "string" },
        window_end: { type: "string" },
        topic: { type: "string" },
        why: { type: "string" },
        confidence: { type: "number" },
      },
      required: ["chat_id", "window_start", "window_end", "topic", "why", "confidence"],
      additionalProperties: false,
    },
    {
      type: "object",
      properties: { none: { type: "string" } },
      required: ["none"],
      additionalProperties: false,
    },
  ],
} as const;

const SYSTEM = `You choose which WhatsApp conversation from a private business community is worth writing up for the community's Facebook group.

The bar is high. A good pick is a thread where something actually happened: a real question got a real answer, someone shared a result or a number, a disagreement resolved into a useful conclusion, or a member solved a problem others plainly have.

A bad pick is price chatter, hype with no analysis, link-drops, reaction-only activity, logistics, or anything that reads as gossip. If the week only has those, return {"none": "<one line saying why>"}. Returning none is correct and expected on a thin week — never reach for a weak story to fill a slot.

Never pick anything that would embarrass a member, expose a client, or repeat a personal disclosure.

Return either a pick or a none verdict, matching the schema exactly.`;

export function buildRankPrompt(candidates: Candidate[], recent: LedgerRow[]): string {
  const lines: string[] = ["Daily chat summaries from the last week:\n"];
  for (const c of candidates) {
    lines.push(`--- ${c.chat_name} (chat_id: ${c.chat_id}) · ${c.date} · ${c.msg_count ?? 0} messages, ${c.participant_count ?? 0} people`);
    if (c.tl_dr) lines.push(`TL;DR: ${c.tl_dr}`);
    if (c.summary_text) lines.push(c.summary_text);
    lines.push("");
  }

  const told = recent.filter((r) => r.status === "posted" || r.status === "draft");
  if (told.length > 0) {
    lines.push("Already told — do not pick these again (reason only, not the draft):");
    for (const r of told) lines.push(`- ${r.chat_name}: ${r.why_picked ?? "(no reason recorded)"}`);
    lines.push("");
  }

  const skipped = recent.filter((r) => r.status === "skipped");
  if (skipped.length > 0) {
    lines.push("Rejected by a human before — learn from these:");
    for (const r of skipped) {
      lines.push(`- ${r.chat_name}: picked for "${r.why_picked ?? "?"}" — rejected because "${r.skip_reason ?? "no reason given"}"`);
    }
    lines.push("");
  }

  lines.push(
    `Pick at most one thread. window_start and window_end must be dates you saw above. confidence is 0..1 — below ${config.fbStory.minConfidence} means it will not be used, so be honest rather than generous.`,
  );
  return lines.join("\n");
}

export function parseRankResult(raw: string): RankResult {
  let json: unknown;
  try {
    json = JSON.parse(raw);
  } catch {
    throw new Error(`Ranker returned non-JSON: ${raw.slice(0, 300)}`);
  }
  const none = NoneSchema.safeParse(json);
  if (none.success) return { none: none.data.none };
  const pick = PickSchema.safeParse(json);
  if (pick.success) return { pick: pick.data };
  throw new Error(`Ranker output matched neither shape: ${raw.slice(0, 300)}`);
}

export async function rankStory(candidates: Candidate[], recent: LedgerRow[]): Promise<RankResult> {
  if (candidates.length === 0) return { none: "no chat activity in the window" };
  const client = new Anthropic({ apiKey: config.fbStory.anthropicApiKey });
  const msg = await client.messages.create({
    model: config.fbStory.model,
    max_tokens: 2000,
    system: SYSTEM,
    output_config: { format: { type: "json_schema", schema: OUTPUT_SCHEMA } },
    messages: [{ role: "user", content: buildRankPrompt(candidates, recent) }],
  });
  const block = msg.content.find((b): b is Anthropic.TextBlock => b.type === "text");
  if (!block) throw new Error("Ranker response contained no text block");
  return parseRankResult(block.text);
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/rank.test.ts`
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/rank.ts src/lib/fbstory/rank.test.ts
git commit -m "feat(fbstory): story ranker with none-is-valid verdict"
```

---

## Task 6: The writer

**Files:**
- Create: `src/lib/fbstory/write.ts`
- Create: `src/lib/fbstory/write.test.ts`

**Interfaces:**
- Consumes: `Thread`, `DraftPost` from `./types`, `config`, `Anthropic`.
- Produces: `buildWritePrompt(thread: Thread): string`, `parseDraft(raw: string): DraftPost`, `writePost(thread: Thread): Promise<DraftPost>`.

- [ ] **Step 1: Write the failing test**

Create `src/lib/fbstory/write.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { buildWritePrompt, parseDraft } from "./write";
import type { Thread } from "./types";

const thread: Thread = {
  story_key: "chatA:m1",
  chat_id: "chatA",
  chat_name: "MDS Trading",
  window_start: "2026-08-25",
  window_end: "2026-08-31",
  root_message_id: "m1",
  message_ids: ["m1", "m2"],
  member_names: ["Zach Miller", "Faizan Khan"],
  messages: [
    { id: "m1", sender_member: "recAAA", sender_name: "Zach Miller", sent_at: "2026-08-26T10:00:00Z", text: "I consolidated suppliers", reply_to: null },
    { id: "m2", sender_member: "recBBB", sender_name: null, sent_at: "2026-08-26T10:05:00Z", text: "how did you de-risk it", reply_to: "m1" },
  ],
};

describe("buildWritePrompt", () => {
  it("labels each message with its speaker", () => {
    expect(buildWritePrompt(thread)).toContain("Zach Miller: I consolidated suppliers");
  });

  it("labels an unresolved sender as unknown rather than dropping the message", () => {
    const p = buildWritePrompt(thread);
    expect(p).toContain("how did you de-risk it");
    expect(p).toContain("Unknown member");
  });

  it("names the chat so the post can say where it happened", () => {
    expect(buildWritePrompt(thread)).toContain("MDS Trading");
  });
});

describe("parseDraft", () => {
  it("parses a well-formed draft", () => {
    const out = parseDraft(JSON.stringify({ post_text: "A story.", members_named: ["Zach Miller"] }));
    expect(out.post_text).toBe("A story.");
    expect(out.members_named).toEqual(["Zach Miller"]);
  });

  it("accepts an empty members_named, since a story can credit nobody by name", () => {
    expect(parseDraft(JSON.stringify({ post_text: "A story.", members_named: [] })).members_named).toEqual([]);
  });

  it("throws on unparseable output", () => {
    expect(() => parseDraft("nope")).toThrow();
  });

  it("throws when post_text is missing", () => {
    expect(() => parseDraft(JSON.stringify({ members_named: [] }))).toThrow();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/write.test.ts`
Expected: FAIL — cannot resolve `./write`.

- [ ] **Step 3: Write `src/lib/fbstory/write.ts`**

```typescript
// One Claude call: turn a thread into a short Facebook-group post.
//
// members_named is returned explicitly rather than inferred from the prose,
// because gate.ts needs an exact list to check. A capitalisation scan would
// fire on every sentence opener and on brand names like Zcash or MSTR.

import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { config } from "@/lib/config";
import type { DraftPost, Thread } from "./types";

const DraftSchema = z.object({
  post_text: z.string().min(1),
  members_named: z.array(z.string()),
});

const OUTPUT_SCHEMA = {
  type: "object",
  properties: {
    post_text: { type: "string" },
    members_named: { type: "array", items: { type: "string" } },
  },
  required: ["post_text", "members_named"],
  additionalProperties: false,
} as const;

const SYSTEM = `You write short posts for a private Facebook group of ecommerce founders, about conversations that happened in the community's WhatsApp chats. Members of the group are not all in every WhatsApp chat, so the post is how they find out.

Rules:
- 100 to 150 words. One story, told as a story: what came up, what was tried, what came of it.
- Credit members by name. Use the names exactly as given to you.
- PARAPHRASE ALWAYS. Never quote anyone. Never reuse a run of words from a message — write the substance in your own words. This is a hard rule and a draft that quotes will be thrown away.
- Say which chat it happened in.
- Carry the actual useful content. A post that says "great discussion happened" and nothing else is worthless.
- End with one genuine question to the group.
- No hype, no emoji spam, no "🚀 HUGE thread 🚀". Write like a member, not a marketer.
- Never include a number, client name, or personal detail that would embarrass the person who shared it.

Return post_text plus members_named: the exact full names of every member you credited. If you credited nobody, return an empty list.`;

export function buildWritePrompt(thread: Thread): string {
  const lines = [
    `Chat: ${thread.chat_name}`,
    `Dates: ${thread.window_start} to ${thread.window_end}`,
    "",
    "Members you may credit, spelled exactly like this:",
    ...thread.member_names.map((n) => `- ${n}`),
    "",
    "Conversation:",
  ];
  for (const m of thread.messages) {
    lines.push(`${m.sender_name ?? "Unknown member"}: ${m.text}`);
  }
  return lines.join("\n");
}

export function parseDraft(raw: string): DraftPost {
  let json: unknown;
  try {
    json = JSON.parse(raw);
  } catch {
    throw new Error(`Writer returned non-JSON: ${raw.slice(0, 300)}`);
  }
  const parsed = DraftSchema.safeParse(json);
  if (!parsed.success) throw new Error(`Writer output failed validation: ${raw.slice(0, 300)}`);
  return parsed.data;
}

export async function writePost(thread: Thread): Promise<DraftPost> {
  const client = new Anthropic({ apiKey: config.fbStory.anthropicApiKey });
  const msg = await client.messages.create({
    model: config.fbStory.model,
    max_tokens: 2000,
    system: SYSTEM,
    output_config: { format: { type: "json_schema", schema: OUTPUT_SCHEMA } },
    messages: [{ role: "user", content: buildWritePrompt(thread) }],
  });
  const block = msg.content.find((b): b is Anthropic.TextBlock => b.type === "text");
  if (!block) throw new Error("Writer response contained no text block");
  return parseDraft(block.text);
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/write.test.ts`
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/write.ts src/lib/fbstory/write.test.ts
git commit -m "feat(fbstory): post writer with declared members_named"
```

---

## Task 7: The Slack card

**Files:**
- Create: `src/lib/fbstory/slack.ts`
- Create: `src/lib/fbstory/slack.test.ts`

**Interfaces:**
- Consumes: `Thread`, `DraftPost`, `RankPick` from `./types`, `config`.
- Produces: `buildCardBlocks(thread: Thread, draft: DraftPost, pick: RankPick): unknown[]`, `postCard(thread, draft, pick): Promise<{ ok: boolean; error?: string }>`, `postQuietLine(text: string): Promise<{ ok: boolean; error?: string }>`.

- [ ] **Step 1: Write the failing test**

Create `src/lib/fbstory/slack.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { buildCardBlocks } from "./slack";
import type { DraftPost, RankPick, Thread } from "./types";

const thread: Thread = {
  story_key: "chatA:m1",
  chat_id: "chatA",
  chat_name: "MDS Trading",
  window_start: "2026-08-25",
  window_end: "2026-08-31",
  root_message_id: "m1",
  message_ids: ["m1"],
  member_names: ["Zach Miller"],
  messages: [],
};
const draft: DraftPost = { post_text: "A story about suppliers.", members_named: ["Zach Miller"] };
const pick: RankPick = {
  chat_id: "chatA",
  window_start: "2026-08-25",
  window_end: "2026-08-31",
  topic: "supplier consolidation",
  why: "a real question got a real answer",
  confidence: 0.84,
};

describe("buildCardBlocks", () => {
  const json = () => JSON.stringify(buildCardBlocks(thread, draft, pick));

  it("puts the draft in a code block so it copies clean into Facebook", () => {
    expect(json()).toContain("```A story about suppliers.```");
  });

  it("shows the source chat and why it was picked", () => {
    expect(json()).toContain("MDS Trading");
    expect(json()).toContain("a real question got a real answer");
  });

  it("carries the story key in both button values, so the handler knows what to update", () => {
    const blocks = JSON.stringify(buildCardBlocks(thread, draft, pick));
    expect(blocks).toContain("fbstory_posted");
    expect(blocks).toContain("fbstory_skip");
    expect(blocks.match(/chatA:m1/g)?.length).toBeGreaterThanOrEqual(2);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/lib/fbstory/slack.test.ts`
Expected: FAIL — cannot resolve `./slack`.

- [ ] **Step 3: Write `src/lib/fbstory/slack.ts`**

```typescript
// The Slack card is the whole human interface: read it, copy the block, paste
// it into the FB group, click Mark posted. Everything else is upstream of this.

import { config } from "@/lib/config";
import type { DraftPost, RankPick, Thread } from "./types";

export function buildCardBlocks(thread: Thread, draft: DraftPost, pick: RankPick): unknown[] {
  return [
    {
      type: "header",
      text: { type: "plain_text", text: `WA story — ${thread.chat_name}`, emoji: false },
    },
    {
      type: "context",
      elements: [
        {
          type: "mrkdwn",
          text: `${thread.window_start} → ${thread.window_end} · ${thread.message_ids.length} messages · confidence ${pick.confidence.toFixed(2)}`,
        },
      ],
    },
    { type: "section", text: { type: "mrkdwn", text: `*Why this one:* ${pick.why}` } },
    // Code block: Slack copies it verbatim, so nothing gets mangled on the way
    // into the Facebook composer.
    { type: "section", text: { type: "mrkdwn", text: "```" + draft.post_text + "```" } },
    {
      type: "actions",
      elements: [
        {
          type: "button",
          style: "primary",
          text: { type: "plain_text", text: "Mark posted", emoji: false },
          action_id: "fbstory_posted",
          value: thread.story_key,
        },
        {
          type: "button",
          text: { type: "plain_text", text: "Skip", emoji: false },
          action_id: "fbstory_skip",
          value: thread.story_key,
        },
      ],
    },
  ];
}

async function post(body: Record<string, unknown>): Promise<{ ok: boolean; error?: string }> {
  const token = config.fbStory.slackBotToken;
  const channel = config.fbStory.slackChannel;
  if (!token || !channel) return { ok: false, error: "fbStory Slack bot token / channel not configured" };
  const res = await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({ channel, unfurl_links: false, unfurl_media: false, ...body }),
  });
  const data = (await res.json()) as { ok: boolean; error?: string };
  return data.ok ? { ok: true } : { ok: false, error: data.error || JSON.stringify(data) };
}

export function postCard(thread: Thread, draft: DraftPost, pick: RankPick) {
  return post({
    text: `WA story ready to post — ${thread.chat_name}`,
    blocks: buildCardBlocks(thread, draft, pick),
  });
}

/** A run that produces nothing still says so. Silence must mean broken, never
 *  quiet — that is the price of a quality ceiling instead of a schedule. */
export function postQuietLine(text: string) {
  return post({ text });
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/lib/fbstory/slack.test.ts`
Expected: PASS, 3 tests.

- [ ] **Step 5: Commit**

```bash
git add src/lib/fbstory/slack.ts src/lib/fbstory/slack.test.ts
git commit -m "feat(fbstory): Slack card with copy block and post/skip buttons"
```

---

## Task 8: The draft route

**Files:**
- Create: `src/app/api/fbstory/draft/route.ts`

**Interfaces:**
- Consumes: everything from Tasks 1–7.
- Produces: `GET /api/fbstory/draft?secret=…[&dry=1][&days=N]`.

- [ ] **Step 1: Write the route**

```typescript
// WA → FB story posts. Picks one WhatsApp thread, writes it up, and posts a
// copy-ready card to #automation-tests for a human to paste into the private FB
// group (Meta removed Groups API publishing in 2024, so the paste is a hard
// constraint, not a shortcut).
//
// Called by a scheduler, not a browser, so it is gated by a shared ?secret=
// rather than the admin session — same shape as /api/health/report.
//
//   ?secret=…   required (matches FB_STORY_SECRET)
//   ?dry=1      run everything, post nothing to Slack, write nothing to the
//               ledger, and return the pick + draft + gate result as JSON
//   ?days=N     override the lookback window (default FB_STORY_LOOKBACK_DAYS)
//   ?asof=DATE  anchor the window to a past date (YYYY-MM-DD). Backfill only —
//               pair it with dry=1 to sample what the pipeline would have said

import { NextRequest, NextResponse } from "next/server";
import { config } from "@/lib/config";
import { sbRequest } from "@/lib/supabase";
import { loadCandidates, selectCandidates } from "@/lib/fbstory/candidates";
import { insertLedgerRow, isAlreadyTold, loadRecentLedger } from "@/lib/fbstory/ledger";
import { rankStory } from "@/lib/fbstory/rank";
import { loadThread } from "@/lib/fbstory/thread";
import { writePost } from "@/lib/fbstory/write";
import { checkDraft } from "@/lib/fbstory/gate";
import { postCard, postQuietLine } from "@/lib/fbstory/slack";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120; // two Claude calls plus several Supabase reads

/** Ledger history the ranker sees, and the dedupe window. Wider than the
 *  lookback so a story cannot come back a fortnight later. */
const LEDGER_DAYS = 60;

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const secret = config.fbStory.draftSecret;
  if (!secret || url.searchParams.get("secret") !== secret) {
    return NextResponse.json({ error: "forbidden" }, { status: 403 });
  }
  const dry = url.searchParams.get("dry") === "1";
  const days = Number(url.searchParams.get("days") || config.fbStory.lookbackDays);
  const asofParam = url.searchParams.get("asof");
  const asof = asofParam ? new Date(`${asofParam}T12:00:00Z`) : undefined;
  if (asofParam && Number.isNaN(asof!.getTime())) {
    return NextResponse.json({ error: "asof must be YYYY-MM-DD" }, { status: 400 });
  }

  try {
    const [rawCandidates, recent] = await Promise.all([
      loadCandidates(days, asof),
      loadRecentLedger(LEDGER_DAYS),
    ]);
    const candidates = selectCandidates(rawCandidates, config.fbStory.excludedChatIds);

    const ranked = await rankStory(candidates, recent);

    if ("none" in ranked) {
      const line = `WA story: nothing cleared the bar (${candidates.length} chat-days considered) — ${ranked.none}`;
      if (!dry) await postQuietLine(line);
      return NextResponse.json({ ok: true, posted: false, reason: ranked.none, candidates: candidates.length });
    }

    const pick = ranked.pick;
    if (pick.confidence < config.fbStory.minConfidence) {
      const line = `WA story: best candidate scored ${pick.confidence.toFixed(2)}, below ${config.fbStory.minConfidence} — nothing posted.`;
      if (!dry) await postQuietLine(line);
      return NextResponse.json({ ok: true, posted: false, reason: "below confidence threshold", pick });
    }

    const chatName =
      candidates.find((c) => c.chat_id === pick.chat_id)?.chat_name ?? pick.chat_id;
    const thread = await loadThread(pick, chatName);

    const dupe = isAlreadyTold(recent, thread.story_key, thread.message_ids);
    if (dupe) {
      return NextResponse.json({ ok: true, posted: false, reason: dupe, story_key: thread.story_key });
    }

    const draft = await writePost(thread);

    // Names the gate will accept: everyone in this thread, plus anyone else the
    // members mirror knows. Fetched by name so the 1000-row cap cannot bite.
    const known = new Set(thread.member_names);
    for (const n of draft.members_named) {
      if (known.has(n)) continue;
      const hits = await sbRequest<Array<{ full_name: string | null; name: string | null }>>(
        `members?or=(full_name.eq.${encodeURIComponent(n)},name.eq.${encodeURIComponent(n)})&select=full_name,name&limit=1`,
      );
      if (hits.length > 0) known.add(n);
    }

    const gate = checkDraft(draft, thread, known);
    if (!gate.ok) {
      if (!dry) {
        await insertLedgerRow({
          story_key: thread.story_key,
          chat_id: thread.chat_id,
          chat_name: thread.chat_name,
          window_start: thread.window_start,
          window_end: thread.window_end,
          message_ids: thread.message_ids,
          draft_text: draft.post_text,
          why_picked: pick.why,
          confidence: pick.confidence,
          status: "blocked",
          skip_reason: gate.reason,
        });
        await postQuietLine(`WA story BLOCKED by the privacy gate (${thread.chat_name}): ${gate.reason}`);
      }
      return NextResponse.json({ ok: true, posted: false, blocked: gate.reason, draft, story_key: thread.story_key });
    }

    if (dry) {
      return NextResponse.json({ ok: true, dry: true, pick, story_key: thread.story_key, draft, gate });
    }

    // Ledger first: a Slack failure is recoverable, a duplicate card is not.
    await insertLedgerRow({
      story_key: thread.story_key,
      chat_id: thread.chat_id,
      chat_name: thread.chat_name,
      window_start: thread.window_start,
      window_end: thread.window_end,
      message_ids: thread.message_ids,
      draft_text: draft.post_text,
      why_picked: pick.why,
      confidence: pick.confidence,
      status: "draft",
      skip_reason: null,
    });
    const sent = await postCard(thread, draft, pick);

    return NextResponse.json({ ok: sent.ok, posted: sent.ok, error: sent.error, story_key: thread.story_key });
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    // A broken run must be as loud as a quiet one.
    if (!dry) await postQuietLine(`WA story run FAILED: ${message}`).catch(() => {});
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}
```

- [ ] **Step 2: Typecheck and lint**

Run: `npx tsc --noEmit && npx eslint src/app/api/fbstory src/lib/fbstory`
Expected: no errors.

- [ ] **Step 3: Run the full test suite to confirm nothing regressed**

Run: `npx vitest run`
Expected: PASS, including the six pre-existing suites.

- [ ] **Step 4: Dry-run locally against real data**

```bash
cd /Users/Born/mds-digest-web
echo 'FB_STORY_SECRET=localdev' >> .env.local
npm run dev
```

In a second terminal:

```bash
curl -s "http://localhost:3000/api/fbstory/draft?secret=localdev&dry=1" | python3 -m json.tool
```

Expected: JSON with either `"posted": false` and a reason, or `"dry": true` with a `pick`, a `story_key` of the form `<chat_id>:<message_id>`, a `draft.post_text` of roughly 100–150 words, and `gate: { ok: true }`. Nothing appears in Slack, and `select count(*) from digest.fb_group_posts` is still 0.

Read the draft. If it quotes, hypes, or reads like marketing, tune the `SYSTEM` prompt in `write.ts` and re-run — this step is the actual quality check, not a formality.

- [ ] **Step 5: Backfill twelve sample drafts and read them**

One dry run proves the wiring. Twelve show whether the thing is any good. With
the dev server still running:

```bash
for d in 2026-06-09 2026-06-16 2026-06-23 2026-06-30 2026-07-07 2026-07-14 2026-07-21 2026-07-28 2026-08-04 2026-08-11 2026-08-18 2026-08-25; do echo "=== $d ==="; curl -s "http://localhost:3000/api/fbstory/draft?secret=localdev&dry=1&asof=$d" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('draft',{}).get('post_text') or r.get('reason') or r.get('blocked'))"; done
```

Expected: twelve outputs, each either a post or a stated reason for no post.
`dry=1` means nothing is written and nothing is sent, so this is safe to repeat.

Read all twelve and judge against the spec's success criteria — drafts should be
pasteable more often than not. Look for: quoted material that the gate somehow
missed, marketing voice, posts that describe a discussion without carrying its
substance, and how often the ranker returns `none`. If more than about half are
weak, tune the `SYSTEM` prompt in `write.ts` (voice, substance) or `rank.ts`
(what clears the bar) and re-run the loop. Do not proceed to deploy on a bad
sample — this step is the actual product review.

- [ ] **Step 6: Commit**

```bash
git add src/lib/fbstory/candidates.ts src/app/api/fbstory/draft/route.ts
git commit -m "feat(fbstory): draft route with dry-run and asof backfill"
```

---

## Task 9: Slack button handler

**Files:**
- Create: `src/app/api/fbstory/interactivity/route.ts`

**Interfaces:**
- Consumes: `markLedgerStatus` from `@/lib/fbstory/ledger`, `config`.
- Produces: `POST /api/fbstory/interactivity`.

Modelled on `src/app/api/centurion/interactivity/route.ts`, which is the working example of Slack signature verification in this repo.

- [ ] **Step 1: Write the route**

```typescript
// Slack interactivity for the WA story card: "Mark posted" and "Skip".
// Configure the Slack app's Interactivity Request URL →
// <deployed origin>/api/fbstory/interactivity
//
// Skip records a reason, which the ranker sees on later runs — rejecting a dud
// teaches the system instead of being thrown away.

import { NextRequest, NextResponse } from "next/server";
import crypto from "node:crypto";
import { config } from "@/lib/config";
import { markLedgerStatus } from "@/lib/fbstory/ledger";

export const runtime = "nodejs";

type SlackInteractivity = {
  type?: string;
  actions?: Array<{ action_id?: string; value?: string }>;
  user?: { username?: string; name?: string };
  channel?: { id?: string };
  message?: { ts?: string };
  trigger_id?: string;
  view?: { private_metadata?: string; state?: { values?: Record<string, Record<string, { value?: string }>> } };
};

function verifySlack(raw: string, ts: string | null, sig: string | null): boolean {
  if (!config.fbStory.slackSigningSecret) return true; // not configured yet (testing)
  if (!ts || !sig) return false;
  const age = Math.abs(Date.now() / 1000 - Number(ts));
  if (!Number.isFinite(age) || age > 300) return false;
  const expected =
    "v0=" +
    crypto.createHmac("sha256", config.fbStory.slackSigningSecret).update(`v0:${ts}:${raw}`).digest("hex");
  try {
    return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
  } catch {
    return false;
  }
}

async function postThread(channel: string, threadTs: string | undefined, text: string): Promise<void> {
  if (!config.fbStory.slackBotToken) return;
  await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.fbStory.slackBotToken}`,
      "Content-Type": "application/json; charset=utf-8",
    },
    body: JSON.stringify({ channel, thread_ts: threadTs, text, unfurl_links: false, unfurl_media: false }),
  });
}

async function openSkipModal(triggerId: string, storyKey: string, channel: string, ts: string): Promise<void> {
  await fetch("https://slack.com/api/views.open", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.fbStory.slackBotToken}`,
      "Content-Type": "application/json; charset=utf-8",
    },
    body: JSON.stringify({
      trigger_id: triggerId,
      view: {
        type: "modal",
        callback_id: "fbstory_skip_modal",
        private_metadata: JSON.stringify({ storyKey, channel, ts }),
        title: { type: "plain_text", text: "Skip this story" },
        submit: { type: "plain_text", text: "Skip" },
        blocks: [
          {
            type: "input",
            block_id: "reason",
            label: { type: "plain_text", text: "Why not this one?" },
            element: { type: "plain_text_input", action_id: "value", multiline: true },
          },
        ],
      },
    }),
  });
}

export async function POST(req: NextRequest) {
  const raw = await req.text();
  if (!verifySlack(raw, req.headers.get("x-slack-request-timestamp"), req.headers.get("x-slack-signature"))) {
    return NextResponse.json({ error: "bad signature" }, { status: 401 });
  }

  const payloadStr = new URLSearchParams(raw).get("payload");
  if (!payloadStr) return NextResponse.json({ ok: true });
  let payload: SlackInteractivity;
  try {
    payload = JSON.parse(payloadStr) as SlackInteractivity;
  } catch {
    return NextResponse.json({ ok: true });
  }

  // Skip modal submitted → record the reason.
  if (payload.type === "view_submission") {
    const meta = JSON.parse(payload.view?.private_metadata || "{}") as {
      storyKey?: string;
      channel?: string;
      ts?: string;
    };
    const reason = payload.view?.state?.values?.reason?.value?.value?.trim() || "no reason given";
    if (meta.storyKey) {
      await markLedgerStatus(meta.storyKey, "skipped", reason);
      if (meta.channel) await postThread(meta.channel, meta.ts, `Skipped by ${payload.user?.username ?? "someone"}: ${reason}`);
    }
    return NextResponse.json({ response_action: "clear" });
  }

  const action = payload.actions?.[0];
  const storyKey = action?.value;
  const channel = payload.channel?.id;
  const ts = payload.message?.ts;
  if (!action || !storyKey) return NextResponse.json({ ok: true });

  if (action.action_id === "fbstory_posted") {
    await markLedgerStatus(storyKey, "posted");
    if (channel) await postThread(channel, ts, `Marked posted by ${payload.user?.username ?? "someone"}.`);
    return NextResponse.json({ ok: true });
  }

  if (action.action_id === "fbstory_skip" && payload.trigger_id && channel && ts) {
    await openSkipModal(payload.trigger_id, storyKey, channel, ts);
    return NextResponse.json({ ok: true });
  }

  return NextResponse.json({ ok: true });
}
```

- [ ] **Step 2: Typecheck and lint**

Run: `npx tsc --noEmit && npx eslint src/app/api/fbstory`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/app/api/fbstory/interactivity/route.ts
git commit -m "feat(fbstory): Slack button handler for mark-posted and skip"
```

---

## Task 10: Deploy, schedule, and prove it live

**Files:**
- Modify: `README.md` (add an `FB story posts` section under the existing env documentation, if the file documents env vars; skip if it does not)
- No new code.

- [ ] **Step 1: Merge and deploy**

```bash
cd /Users/Born/mds-digest-web
npx vitest run
npx tsc --noEmit
git checkout main
git merge --no-ff fbstory
git push origin main
```

Render auto-deploys on push to `main`. There is no staging tier — this is production the moment it lands. That is why every prior task stayed on the branch.

- [ ] **Step 2: Set the Render env vars**

In the Render dashboard for `srv-d7lg3amgvqtc73f3ni20`, **check the existing list before adding** — several of these may already exist:

| Var | Value |
|---|---|
| `FB_STORY_SECRET` | a fresh random string (`openssl rand -hex 24`) |

Everything else falls back: the Anthropic key, Slack bot token, and channel all inherit from the Centurion/health vars already set. Only add `FB_STORY_MODEL`, `FB_STORY_MIN_CONFIDENCE`, `FB_STORY_LOOKBACK_DAYS` or `FB_STORY_EXCLUDED_CHATS` if you want to override a default.

**A Render env change does not auto-redeploy — trigger a manual deploy afterwards.**

- [ ] **Step 3: Prove the deployed route works, without posting**

```bash
curl -s "https://digest.mds.co/api/fbstory/draft?secret=<FB_STORY_SECRET>&dry=1" | python3 -m json.tool
```

Expected: the same shape as the local dry run. Confirm nothing landed in Slack and the ledger is still empty:

```sql
select count(*) from digest.fb_group_posts;
```

- [ ] **Step 4: Point the Slack app at the interactivity URL**

In the Slack app that owns `CENTURION_SLACK_BOT_TOKEN`, set **Interactivity & Shortcuts → Request URL** to `https://digest.mds.co/api/fbstory/interactivity`.

If that app already points at `/api/centurion/interactivity`, do **not** overwrite it — Slack allows one URL per app. Either create a separate Slack app for fbstory and set `FB_STORY_SLACK_BOT_TOKEN` and `FB_STORY_SLACK_SIGNING_SECRET` to its credentials, or add a dispatcher. Check first; this is the one step that can silently break Centurion.

- [ ] **Step 5: Build the n8n scheduler**

Create a new n8n workflow named `MDS WA → FB Story Draft (Mon/Wed/Fri 9am ET)`, modelled on `argZgYHPgdVKJqCS` ("MDS Platform Health → Slack"):

- **Schedule Trigger** — cron `0 9 * * 1,3,5`, and set `settings.timezone` to `America/New_York`. Cron expressions evaluate in the workflow timezone, so without this it fires at 9am UTC.
- **HTTP Request** — `GET https://digest.mds.co/api/fbstory/draft?secret=<FB_STORY_SECRET>`, timeout 120000, `retryOnFail` 3× / 5s.

Activate it with a single `[{deactivateWorkflow},{activateWorkflow}]` bounce — never deactivate first.

- [ ] **Step 6: Force one real live run**

n8n cannot fire a Schedule trigger through the API. Click **Execute Workflow** in the n8n UI.

Expected, and all four must hold before this is called done:
1. The n8n execution succeeds.
2. Either a card or a quiet line appears in `#automation-tests`.
3. If a card appeared, `select story_key, status from digest.fb_group_posts` shows exactly one `draft` row.
4. Clicking **Mark posted** flips that row to `posted` and drops a confirmation in the card's thread.

Record the n8n execution id — it is the proof the ticket closes on.

- [ ] **Step 7: Commit any doc updates**

```bash
git add -A
git commit -m "docs(fbstory): env vars and scheduler notes"
git push origin main
```
