# Member Finder (#108) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One lane where Millie finds members by any combination of chat membership, business model, event attendance, geography, revenue band, niche and expertise — returning names with per-person reasons, a count, or a grouped breakdown.

**Architecture:** A pure-logic module (`src/lib/olivia-find.ts`, unit-tested with vitest) holds every decision — label normalisation, matching, reasons, policy caps, grouping. A thin Next.js route (`src/app/api/olivia/find/route.ts`) does auth, validation and the Supabase reads, then calls the module. The n8n workflow gains one tool (`member_find`) pointing at that route, plus a one-line fix so `event_who` stops landing on the schedule route's default op. No database migration, no new table, no change to any existing tool's behaviour.

**Tech Stack:** TypeScript / Next.js App Router (mds-digest-web, deployed on Render) · vitest · Supabase PostgREST (`digest` schema) · n8n (Olivia workflow) · Python for the n8n apply script and the leak gate.

## Global Constraints

- **Two repos.** Route + tests live in `/Users/Born/mds-digest-web`. Plan, gate, apply script, docs live in `/Users/Born/Scorecard`. Never edit one while committing the other.
- **Commit author in mds-digest-web must be `Andy Verdy <andy.verdy1@gmail.com>`** — the deploy pipeline keys on it. Scorecard commits use the normal author plus the `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer.
- **PROD workflow `12wj6h1TWqb0d4Dq` is never edited.** All workflow work happens on STAGING `bqHstPDi84uOhTCJ`. Andy runs `python3 scripts/olivia_wf.py promote`.
- **`node --check` on the Answer Seed jsCode before any PUT.** A missing comma once broke staging for 15 minutes.
- **One bounce per PUT:** `POST /workflows/{id}/deactivate` then `POST /workflows/{id}/activate`, in that order, in the same script run. Never deactivate first as a separate step.
- **Leak gate must exit 0** — run `python3 scripts/olivia_leak_gate.py; echo "EXIT $?"`. Never pipe it through `tail`; that swallows the exit code.
- **Never emit a score, rank, percentile or engagement number** in any response field or note. Ranking is internal.
- **Never probe production against a real member's phone.** Probes run on the staging webhook, or read-only against the route with Andy's own number `17866578153`.
- Andy's answers stay short: when reporting, lead with the result, then the AC checklist.

---

## File Structure

| File | Responsibility |
|---|---|
| `mds-digest-web/src/lib/olivia-find.ts` (create) | Pure logic: concept expansion, chat normalisation, per-person matching + reasons, policy filtering/cap, grouping. No I/O. |
| `mds-digest-web/src/lib/olivia-find.test.ts` (create) | Vitest unit tests for every rule in the module. |
| `mds-digest-web/src/app/api/olivia/find/route.ts` (create) | Auth, request validation against the closed allowlist, Supabase reads, response assembly. |
| `Scorecard/scripts/olivia_loop/apply_108_member_find.py` (create) | One-shot n8n patch: `member_find` tool declaration + routing rule in Answer Seed, `member_find` and `event_who` branches in Answer Tool. Staging only. |
| `Scorecard/scripts/olivia_leak_gate.py` (modify) | Six new checks for the finder lane. |
| `Scorecard/OLIVIA_SPRINT_4.md`, `OLIVIA_HANDBOOK.md`, `OLIVIA_NEXT_SESSION.md`, `SESSION_LOG_OLIVIA.md` (modify) | Close block, handbook lane entry, handoff, session log. |

---

### Task 1: Pure logic module — concepts, matching, reasons

**Files:**
- Create: `mds-digest-web/src/lib/olivia-find.ts`
- Test: `mds-digest-web/src/lib/olivia-find.test.ts`

**Interfaces:**
- Consumes: nothing (leaf module).
- Produces: `FindFilters`, `Candidate`, `FoundPerson`, `expandConcepts(filters)`, `normaliseChats(names, known)`, `matchCandidate(candidate, plan, askerId)`, `CONCEPTS`.

- [ ] **Step 1: Write the failing test**

Create `mds-digest-web/src/lib/olivia-find.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { expandConcepts, matchCandidate, normaliseChats, type Candidate } from "./olivia-find";

const KNOWN_CHATS = ["MDS Resellers", "MDS Supplements", "MDS Under 30"];

const ariel: Candidate = {
  at_member_id: "rec1",
  full_name: "Ariel Tung",
  membership_status: "Current Member",
  chats: ["MDS Resellers"],
  business_model: ["Wholesale and/or Arbitrage"],
  city: "Singapore", state: null, country: "Singapore",
  rev_band: "1-5M", main_niche: null, categories: [], expertise: null,
  engagement_score: 40,
};
const ivan: Candidate = {
  ...ariel, at_member_id: "rec2", full_name: "Ivan Ong",
  business_model: ["Private Label"], main_niche: "Baby", engagement_score: 90,
};

describe("expandConcepts", () => {
  it("turns 'reseller' into both the chat and the model labels", () => {
    const plan = expandConcepts({ business_model: ["reseller"] }, KNOWN_CHATS);
    expect(plan.concepts).toHaveLength(1);
    expect(plan.concepts[0].chats).toEqual(["MDS Resellers"]);
    expect(plan.concepts[0].models).toContain("Wholesale and/or Arbitrage");
    expect(plan.concepts[0].models).toContain("Wholesale, Resale & Dropshipping");
    expect(plan.unmatched).toEqual([]);
  });

  it("reports a label it cannot resolve instead of dropping it", () => {
    const plan = expandConcepts({ business_model: ["dropshipping", "vending machines"] }, KNOWN_CHATS);
    expect(plan.concepts[0].models).toContain("Wholesale, Resale & Dropshipping");
    expect(plan.unmatched).toEqual(["vending machines"]);
  });
});

describe("normaliseChats", () => {
  it("matches case-insensitively and with the MDS prefix optional", () => {
    expect(normaliseChats(["resellers chat", "MDS SUPPLEMENTS"], KNOWN_CHATS))
      .toEqual({ chats: ["MDS Resellers", "MDS Supplements"], unmatched: [] });
  });
  it("reports an unknown chat", () => {
    expect(normaliseChats(["MDS Yachts"], KNOWN_CHATS))
      .toEqual({ chats: [], unmatched: ["MDS Yachts"] });
  });
});

describe("matchCandidate", () => {
  it("matches on chat alone and says so", () => {
    const plan = expandConcepts({ business_model: ["reseller"] }, KNOWN_CHATS);
    const hit = matchCandidate({ ...ariel, business_model: [] }, plan, "asker");
    expect(hit?.reasons).toEqual(["in MDS Resellers"]);
  });

  it("matches on the declared model alone and says so", () => {
    const plan = expandConcepts({ business_model: ["reseller"] }, KNOWN_CHATS);
    const hit = matchCandidate({ ...ariel, chats: [] }, plan, "asker");
    expect(hit?.reasons).toEqual(["wholesale & arbitrage"]);
  });

  it("reports both reasons when both are true", () => {
    const plan = expandConcepts({ business_model: ["reseller"] }, KNOWN_CHATS);
    expect(matchCandidate(ariel, plan, "asker")?.reasons)
      .toEqual(["in MDS Resellers", "wholesale & arbitrage"]);
  });

  it("does not match a private-label member outside the chat", () => {
    const plan = expandConcepts({ business_model: ["reseller"] }, KNOWN_CHATS);
    expect(matchCandidate({ ...ivan, chats: [] }, plan, "asker")).toBeNull();
  });

  it("ANDs across filter kinds", () => {
    const plan = expandConcepts({ business_model: ["reseller"], country: ["Spain"] }, KNOWN_CHATS);
    expect(matchCandidate(ariel, plan, "asker")).toBeNull();
  });

  it("ORs inside a kind and names the matched value", () => {
    const plan = expandConcepts({ country: ["Spain", "Singapore"] }, KNOWN_CHATS);
    expect(matchCandidate(ariel, plan, "asker")?.reasons).toEqual(["Singapore"]);
  });

  it("never matches the asker themselves", () => {
    const plan = expandConcepts({ country: ["Singapore"] }, KNOWN_CHATS);
    expect(matchCandidate(ariel, plan, "rec1")).toBeNull();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/olivia-find.test.ts`
Expected: FAIL — `Failed to resolve import "./olivia-find"`.

- [ ] **Step 3: Write the module**

Create `mds-digest-web/src/lib/olivia-find.ts`:

```ts
// The member finder's decisions, with no I/O so they can be unit-tested.
//
// WHY A CONCEPT LAYER (#108, Andy 2026-08-22): "reseller" is not one field.
// A member is a reseller because they sit in the MDS Resellers WhatsApp chat
// (behaviour), or because they told MDS so on a form (declaration), or both.
// Andy's ruling: report the UNION and show which evidence each person carries.
// Chat membership without the declaration is still a real reseller; the
// declaration is only as fresh as their last form.
//
// The map lives in code, not in the prompt, because two prompt rules already
// failed to stop the model inventing topic words for this (#111).

export type FindFilters = {
  chat?: string[];
  business_model?: string[];
  event?: string;
  city?: string[];
  state?: string[];
  country?: string[];
  band?: string[];
  niche?: string[];
  category?: string[];
  expertise?: string;
};

export type Candidate = {
  at_member_id: string;
  full_name: string | null;
  membership_status: string | null;
  chats: string[];
  business_model: string[];
  city: string | null;
  state: string | null;
  country: string | null;
  rev_band: string | null;
  main_niche: string | null;
  categories: string[];
  expertise: string | null;
  engagement_score: number;
};

export type FoundPerson = {
  at_member_id: string;
  name: string;
  reasons: string[];
  city: string | null;
  niche: string | null;
  engagement_score: number; // internal only — the route strips it
};

export type Concept = {
  /** what the member said, e.g. "reseller" */
  label: string;
  /** business_model values that satisfy it */
  models: string[];
  /** chat names that satisfy it */
  chats: string[];
  /** the words used in a reason line when a model value matched */
  modelReason: string;
};

/**
 * Both label vocabularies live in the data: the legacy application set
 * ("Wholesale and/or Arbitrage") and the app-v3 set ("Wholesale, Resale &
 * Dropshipping"). One corrupt value joins two labels with an apostrophe — it is
 * matched here, not repaired here (that is an Airtable fix).
 */
export const CONCEPTS: Concept[] = [
  {
    label: "reseller",
    models: [
      "Wholesale and/or Arbitrage",
      "Wholesale, Resale & Dropshipping",
      "OEM Design & Development'Wholesale and/or Arbitrage",
    ],
    chats: ["MDS Resellers"],
    modelReason: "wholesale & arbitrage",
  },
  {
    label: "private label",
    models: ["Private Label"],
    chats: [],
    modelReason: "private label",
  },
  {
    label: "brand owner",
    models: ["Own Brand", "Private Label"],
    chats: [],
    modelReason: "own brand",
  },
  {
    label: "agency",
    models: ["Brand Management and/or Agency", "Agency, Consulting & Brand Management"],
    chats: [],
    modelReason: "agency / brand management",
  },
  {
    label: "oem",
    models: ["OEM Design & Development", "OEM Design & Development'Wholesale and/or Arbitrage"],
    chats: [],
    modelReason: "OEM design & development",
  },
];

const CONCEPT_SYNONYMS: Record<string, string> = {
  reseller: "reseller", resellers: "reseller", reselling: "reseller",
  wholesale: "reseller", wholesaler: "reseller", wholesalers: "reseller",
  arbitrage: "reseller", dropship: "reseller", dropshipping: "reseller",
  dropshipper: "reseller", resale: "reseller",
  "private label": "private label", pl: "private label",
  "brand owner": "brand owner", "brand owners": "brand owner", "own brand": "brand owner",
  agency: "agency", agencies: "agency", "brand management": "agency", consulting: "agency",
  oem: "oem", manufacturing: "oem", manufacturer: "oem",
};

export type FilterPlan = {
  concepts: Concept[];
  /** chats the member named directly, ANDed on top of any concept */
  chats: string[];
  city: string[];
  state: string[];
  country: string[];
  band: string[];
  niche: string[];
  category: string[];
  expertise: string | null;
  event: string | null;
  unmatched: string[];
};

const lower = (s: string) => s.trim().toLowerCase();
const list = (xs?: string[]) => (xs || []).map((x) => String(x).trim()).filter(Boolean);

/** "resellers chat" and "MDS RESELLERS" both resolve to the catalog name. */
export function normaliseChats(
  names: string[] | undefined,
  known: string[],
): { chats: string[]; unmatched: string[] } {
  const chats: string[] = [];
  const unmatched: string[] = [];
  for (const raw of list(names)) {
    const want = lower(raw).replace(/\bchat\b/g, "").replace(/^mds\s+/, "").trim();
    const hit = known.find((k) => lower(k).replace(/^mds\s+/, "") === want);
    if (hit) { if (!chats.includes(hit)) chats.push(hit); } else { unmatched.push(raw); }
  }
  return { chats, unmatched };
}

export function expandConcepts(filters: FindFilters, knownChats: string[]): FilterPlan {
  const unmatched: string[] = [];
  const concepts: Concept[] = [];
  for (const raw of list(filters.business_model)) {
    const key = CONCEPT_SYNONYMS[lower(raw)];
    const concept = key ? CONCEPTS.find((c) => c.label === key) : undefined;
    // An exact label from the data ("Private Label") is also accepted.
    const exact = CONCEPTS.find((c) => c.models.some((m) => lower(m) === lower(raw)));
    const found = concept || exact;
    if (found) { if (!concepts.includes(found)) concepts.push(found); } else { unmatched.push(raw); }
  }
  const chat = normaliseChats(filters.chat, knownChats);
  return {
    concepts,
    chats: chat.chats,
    city: list(filters.city),
    state: list(filters.state),
    country: list(filters.country),
    band: list(filters.band),
    niche: list(filters.niche),
    category: list(filters.category),
    expertise: filters.expertise ? String(filters.expertise).trim() : null,
    event: filters.event ? String(filters.event).trim() : null,
    unmatched: [...unmatched, ...chat.unmatched],
  };
}

const anyEq = (want: string[], have: (string | null)[]) =>
  want.find((w) => have.some((h) => h && lower(h) === lower(w))) || null;

/**
 * Returns the person with their reasons, or null when any filter kind fails.
 * AND across kinds, OR inside a kind — and a concept is satisfied by EITHER
 * its chat or its model (that is the union Andy asked for).
 */
export function matchCandidate(c: Candidate, plan: FilterPlan, askerId: string): FoundPerson | null {
  if (c.at_member_id === askerId) return null;
  const reasons: string[] = [];

  for (const concept of plan.concepts) {
    const chatHit = concept.chats.find((ch) => c.chats.some((x) => lower(x) === lower(ch))) || null;
    const modelHit = concept.models.find((m) => c.business_model.some((x) => lower(x) === lower(m))) || null;
    if (!chatHit && !modelHit) return null;
    if (chatHit) reasons.push(`in ${chatHit}`);
    if (modelHit) reasons.push(concept.modelReason);
  }

  for (const ch of plan.chats) {
    const hit = c.chats.find((x) => lower(x) === lower(ch));
    if (!hit) return null;
    if (!reasons.includes(`in ${hit}`)) reasons.push(`in ${hit}`);
  }

  if (plan.city.length) { const h = anyEq(plan.city, [c.city]); if (!h) return null; reasons.push(c.city as string); }
  if (plan.state.length) { const h = anyEq(plan.state, [c.state]); if (!h) return null; reasons.push(c.state as string); }
  if (plan.country.length) { const h = anyEq(plan.country, [c.country]); if (!h) return null; reasons.push(c.country as string); }
  if (plan.band.length) { const h = anyEq(plan.band, [c.rev_band]); if (!h) return null; reasons.push(c.rev_band as string); }
  if (plan.niche.length) { const h = anyEq(plan.niche, [c.main_niche]); if (!h) return null; reasons.push(c.main_niche as string); }
  if (plan.category.length) {
    const h = anyEq(plan.category, c.categories);
    if (!h) return null;
    reasons.push(h);
  }
  if (plan.expertise) {
    const hay = `${c.expertise || ""} ${c.main_niche || ""} ${c.categories.join(" ")}`.toLowerCase();
    if (!hay.includes(lower(plan.expertise))) return null;
    reasons.push(plan.expertise);
  }

  return {
    at_member_id: c.at_member_id,
    name: c.full_name || "",
    reasons: [...new Set(reasons)],
    city: c.city,
    niche: c.main_niche || c.categories[0] || null,
    engagement_score: c.engagement_score,
  };
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/olivia-find.test.ts`
Expected: PASS — 9 tests.

- [ ] **Step 5: Commit**

```bash
cd /Users/Born/mds-digest-web
git add src/lib/olivia-find.ts src/lib/olivia-find.test.ts
git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "#108: member finder logic — concepts, matching, per-person reasons"
```

---

### Task 2: Policy — staff exclusion, ranking, cap, grouping

**Files:**
- Modify: `mds-digest-web/src/lib/olivia-find.ts` (append)
- Test: `mds-digest-web/src/lib/olivia-find.test.ts` (append)

**Interfaces:**
- Consumes: `FoundPerson`, `Candidate` from Task 1.
- Produces: `isMemberFacing(status)`, `rank(people)`, `applyCap(people, limit)` → `{ people, total, shown, capped }`, `groupBy(candidates, matches, dimension)` → `Array<{ value: string; count: number }>`, `NAME_CAP = 10`.

- [ ] **Step 1: Write the failing test**

Append to `mds-digest-web/src/lib/olivia-find.test.ts`:

```ts
import { applyCap, groupBy, isMemberFacing, rank, NAME_CAP } from "./olivia-find";

describe("policy", () => {
  it("keeps only member-facing statuses", () => {
    expect(isMemberFacing("Current Member")).toBe(true);
    expect(isMemberFacing("New Member")).toBe(true);
    expect(isMemberFacing("Current Member- Paused ")).toBe(true);
    expect(isMemberFacing("Staff")).toBe(false);
    expect(isMemberFacing("Removed - Canceled Membership")).toBe(false);
    expect(isMemberFacing(null)).toBe(false);
  });

  it("ranks by engagement then name, deterministically", () => {
    const out = rank([
      { at_member_id: "b", name: "Bea", reasons: [], city: null, niche: null, engagement_score: 10 },
      { at_member_id: "a", name: "Al", reasons: [], city: null, niche: null, engagement_score: 90 },
      { at_member_id: "c", name: "Cy", reasons: [], city: null, niche: null, engagement_score: 10 },
    ]);
    expect(out.map((p) => p.name)).toEqual(["Al", "Bea", "Cy"]);
  });

  it("caps names at 10 but keeps the true total", () => {
    const many = Array.from({ length: 21 }, (_, i) => ({
      at_member_id: `r${i}`, name: `P${i}`, reasons: [], city: null, niche: null, engagement_score: i,
    }));
    const out = applyCap(many, 50);
    expect(out.shown).toBe(NAME_CAP);
    expect(out.people).toHaveLength(NAME_CAP);
    expect(out.total).toBe(21);
    expect(out.capped).toBe(true);
  });

  it("honours a smaller caller limit", () => {
    const three = Array.from({ length: 3 }, (_, i) => ({
      at_member_id: `r${i}`, name: `P${i}`, reasons: [], city: null, niche: null, engagement_score: i,
    }));
    expect(applyCap(three, 2)).toMatchObject({ shown: 2, total: 3, capped: true });
  });

  it("groups by a dimension and sorts by count", () => {
    const rows = [
      { value: "Spain" }, { value: "Spain" }, { value: "Singapore" },
    ].map((r, i) => ({
      at_member_id: `r${i}`, country: r.value, city: null, state: null, rev_band: null,
      main_niche: null, categories: [], business_model: [], chats: [],
    }));
    expect(groupBy(rows as never, "country")).toEqual([
      { value: "Spain", count: 2 }, { value: "Singapore", count: 1 },
    ]);
  });

  it("counts a multi-value dimension once per value", () => {
    const rows = [{
      at_member_id: "r1", country: null, city: null, state: null, rev_band: null,
      main_niche: null, categories: [], chats: [], business_model: ["Private Label", "Wholesale and/or Arbitrage"],
    }];
    expect(groupBy(rows as never, "business_model")).toEqual([
      { value: "Private Label", count: 1 }, { value: "Wholesale and/or Arbitrage", count: 1 },
    ]);
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/olivia-find.test.ts`
Expected: FAIL — `applyCap is not a function` (no such export).

- [ ] **Step 3: Append the implementation**

Append to `mds-digest-web/src/lib/olivia-find.ts`:

```ts
/** #96: a display cap, never a processing cap — `total` always counts everyone. */
export const NAME_CAP = 10;

/**
 * #106 (Andy, during #97's prod E2E: "I don't want people to see me as an
 * attendee"). Staff, removed and unknown-status records never reach a
 * member-facing list — and they are left out of the count too: a total whose
 * members cannot be shown is a number that lies.
 */
export function isMemberFacing(status: string | null): boolean {
  if (!status) return false;
  const s = status.trim().toLowerCase();
  if (s.startsWith("removed")) return false;
  if (s === "staff") return false;
  return s.startsWith("current member") || s === "new member";
}

/** Engagement first, then name. Never surfaced — ordering only (ruling §7.3). */
export function rank(people: FoundPerson[]): FoundPerson[] {
  return [...people].sort(
    (a, b) => b.engagement_score - a.engagement_score || a.name.localeCompare(b.name),
  );
}

export function applyCap(people: FoundPerson[], limit: number): {
  people: FoundPerson[]; total: number; shown: number; capped: boolean;
} {
  const max = Math.max(1, Math.min(NAME_CAP, Math.floor(limit) || NAME_CAP));
  const ranked = rank(people);
  const shown = ranked.slice(0, max);
  return { people: shown, total: ranked.length, shown: shown.length, capped: ranked.length > shown.length };
}

export type GroupDimension =
  | "country" | "state" | "city" | "band" | "niche" | "business_model" | "chat";

export function groupBy(rows: Candidate[], dimension: GroupDimension): Array<{ value: string; count: number }> {
  const pick = (c: Candidate): string[] => {
    switch (dimension) {
      case "country": return c.country ? [c.country] : [];
      case "state": return c.state ? [c.state] : [];
      case "city": return c.city ? [c.city] : [];
      case "band": return c.rev_band ? [c.rev_band] : [];
      case "niche": return c.main_niche ? [c.main_niche] : c.categories.slice(0, 1);
      case "business_model": return c.business_model;
      case "chat": return c.chats;
    }
  };
  const counts = new Map<string, number>();
  for (const row of rows) for (const v of pick(row)) counts.set(v, (counts.get(v) || 0) + 1);
  return [...counts.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/olivia-find.test.ts`
Expected: PASS — 15 tests.

- [ ] **Step 5: Commit**

```bash
cd /Users/Born/mds-digest-web
git add src/lib/olivia-find.ts src/lib/olivia-find.test.ts
git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "#108: finder policy — staff exclusion, internal ranking, name cap, grouping"
```

---

### Task 3: Request validation — the closed allowlist

**Files:**
- Modify: `mds-digest-web/src/lib/olivia-find.ts` (append)
- Test: `mds-digest-web/src/lib/olivia-find.test.ts` (append)

**Interfaces:**
- Produces: `parseRequest(body)` → `{ ok: true; phone: string; filters: FindFilters; mode: "names"|"count"|"breakdown"; group_by: GroupDimension|null; limit: number } | { ok: false; error: string }`, `FILTER_KEYS`.

- [ ] **Step 1: Write the failing test**

Append to `mds-digest-web/src/lib/olivia-find.test.ts`:

```ts
import { parseRequest } from "./olivia-find";

describe("parseRequest", () => {
  it("accepts a well-formed request", () => {
    const out = parseRequest({
      phone: "+1 (786) 657-8153",
      filters: { business_model: ["reseller"], event: "Summit Singapore" },
      mode: "names", limit: 10,
    });
    expect(out).toMatchObject({ ok: true, phone: "17866578153", mode: "names" });
  });

  it("rejects a request with no phone", () => {
    expect(parseRequest({ filters: { chat: ["MDS Resellers"] } }))
      .toEqual({ ok: false, error: "phone required" });
  });

  it("rejects an unknown filter key instead of ignoring it", () => {
    expect(parseRequest({ phone: "1", filters: { revenue_exact: ["4000000"] } }))
      .toEqual({ ok: false, error: "unknown filter: revenue_exact" });
  });

  it("rejects an empty filter set — no whole-roster dumps", () => {
    expect(parseRequest({ phone: "1", filters: {} }))
      .toEqual({ ok: false, error: "at least one filter is required" });
  });

  it("rejects breakdown mode without a group_by", () => {
    expect(parseRequest({ phone: "1", filters: { chat: ["MDS Resellers"] }, mode: "breakdown" }))
      .toEqual({ ok: false, error: "breakdown mode needs group_by" });
  });

  it("rejects an unknown group_by", () => {
    expect(parseRequest({ phone: "1", filters: { chat: ["x"] }, mode: "breakdown", group_by: "revenue" }))
      .toEqual({ ok: false, error: "unknown group_by: revenue" });
  });

  it("accepts a bare string where a list is allowed", () => {
    const out = parseRequest({ phone: "1", filters: { country: "Spain" } });
    expect(out).toMatchObject({ ok: true });
    if (out.ok) expect(out.filters.country).toEqual(["Spain"]);
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/olivia-find.test.ts`
Expected: FAIL — `parseRequest is not a function`.

- [ ] **Step 3: Append the implementation**

Append to `mds-digest-web/src/lib/olivia-find.ts`:

```ts
export const FILTER_KEYS = [
  "chat", "business_model", "event", "city", "state", "country",
  "band", "niche", "category", "expertise",
] as const;

const GROUP_DIMENSIONS: GroupDimension[] = [
  "country", "state", "city", "band", "niche", "business_model", "chat",
];

export type ParsedRequest =
  | { ok: true; phone: string; filters: FindFilters; mode: "names" | "count" | "breakdown";
      group_by: GroupDimension | null; limit: number }
  | { ok: false; error: string };

/**
 * The allowlist is CLOSED: an unknown key is a 400, never a silent ignore. A
 * tool schema that drifts must not be able to widen what Millie can read.
 */
export function parseRequest(body: unknown): ParsedRequest {
  const b = (body || {}) as Record<string, unknown>;
  const phone = String(b.phone || "").replace(/\D/g, "");
  if (!phone) return { ok: false, error: "phone required" };

  const raw = (b.filters || {}) as Record<string, unknown>;
  for (const key of Object.keys(raw)) {
    if (!(FILTER_KEYS as readonly string[]).includes(key)) {
      return { ok: false, error: `unknown filter: ${key}` };
    }
  }
  const asList = (v: unknown): string[] =>
    (Array.isArray(v) ? v : v == null || v === "" ? [] : [v]).map((x) => String(x).trim()).filter(Boolean);

  const filters: FindFilters = {
    chat: asList(raw.chat),
    business_model: asList(raw.business_model),
    city: asList(raw.city),
    state: asList(raw.state),
    country: asList(raw.country),
    band: asList(raw.band),
    niche: asList(raw.niche),
    category: asList(raw.category),
    event: raw.event ? String(raw.event).trim() : undefined,
    expertise: raw.expertise ? String(raw.expertise).trim() : undefined,
  };
  const anyFilter =
    !!filters.event || !!filters.expertise ||
    (["chat", "business_model", "city", "state", "country", "band", "niche", "category"] as const)
      .some((k) => (filters[k] || []).length > 0);
  if (!anyFilter) return { ok: false, error: "at least one filter is required" };

  const mode = String(b.mode || "names") as "names" | "count" | "breakdown";
  if (!["names", "count", "breakdown"].includes(mode)) {
    return { ok: false, error: `unknown mode: ${mode}` };
  }
  const groupRaw = b.group_by ? String(b.group_by) : null;
  if (groupRaw && !GROUP_DIMENSIONS.includes(groupRaw as GroupDimension)) {
    return { ok: false, error: `unknown group_by: ${groupRaw}` };
  }
  if (mode === "breakdown" && !groupRaw) return { ok: false, error: "breakdown mode needs group_by" };

  const limit = Number(b.limit) > 0 ? Number(b.limit) : NAME_CAP;
  return { ok: true, phone, filters, mode, group_by: (groupRaw as GroupDimension) || null, limit };
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/Born/mds-digest-web && npx vitest run src/lib/olivia-find.test.ts`
Expected: PASS — 22 tests.

- [ ] **Step 5: Commit**

```bash
cd /Users/Born/mds-digest-web
git add src/lib/olivia-find.ts src/lib/olivia-find.test.ts
git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "#108: finder request parsing with a closed filter allowlist"
```

---

### Task 4: The route — reads, event gating, response

**Files:**
- Create: `mds-digest-web/src/app/api/olivia/find/route.ts`

**Interfaces:**
- Consumes: everything exported in Tasks 1–3; `sbRequest`, `isSupabaseConfigured` from `@/lib/supabase`.
- Produces: `POST /api/olivia/find` returning `{ total, shown, capped, filters_echo, event, people[], breakdown, note }`.

- [ ] **Step 1: Write the route**

Create `mds-digest-web/src/app/api/olivia/find/route.ts`:

```ts
import { NextRequest, NextResponse } from "next/server";
import { isSupabaseConfigured, sbRequest } from "@/lib/supabase";
import {
  applyCap, expandConcepts, groupBy, isMemberFacing, matchCandidate, parseRequest,
  type Candidate, type FoundPerson,
} from "@/lib/olivia-find";

// The member finder (#108). One lane for every "who in MDS is X" question:
// filters compose, and the disclosure rules live HERE rather than being
// re-implemented per tool — that divergence is what let a test row surface
// real attendee names once (#98/#106).
//
// Route, not RPC (Andy 2026-08-17): retrieval travels in the query, POLICY
// lives in git where it is reviewed and testable.

export const dynamic = "force-dynamic";

const CANDIDATE_CAP = 2000;

function unauthorized() {
  return NextResponse.json({ error: "unauthorized" }, { status: 401 });
}

type MemberRow = { at_member_id: string; channels_present: string[] | null; membership_status: string | null };
type AttrRow = {
  at_member_id: string; full_name: string | null; membership_status: string | null;
  business_model: string[] | null; city: string | null; state: string | null; country: string | null;
  rev_band: string | null; main_niche: string | null; categories: string[] | null; expertise: string | null;
};
type ProfRow = { at_member_id: string; full_name: string | null; engagement_score: number | null };

export async function POST(req: NextRequest) {
  const secret = process.env.OLIVIA_SCHEDULE_SECRET || process.env.OLIVIA_IOS_SECRET;
  if (!secret) return NextResponse.json({ error: "finder secret not configured" }, { status: 500 });
  const bearer = (req.headers.get("authorization") || "") === `Bearer ${secret}`;
  const headerSecret = (req.headers.get("x-olivia-secret") || "") === secret;
  if (!bearer && !headerSecret) return unauthorized();
  if (!isSupabaseConfigured()) {
    return NextResponse.json({ error: "supabase not configured" }, { status: 500 });
  }

  let raw: unknown;
  try { raw = await req.json(); } catch { return NextResponse.json({ error: "invalid json" }, { status: 400 }); }

  const parsed = parseRequest(raw);
  if (!parsed.ok) return NextResponse.json({ error: parsed.error }, { status: 400 });
  const { phone, filters, mode, group_by, limit } = parsed;

  // ---- who is asking ------------------------------------------------------
  const askers = await sbRequest<Array<{ at_member_id: string | null }>>(
    `members?select=at_member_id&phone=eq.${encodeURIComponent(phone)}&limit=1`,
  ).catch(() => [] as Array<{ at_member_id: string | null }>);
  const askerId = askers[0]?.at_member_id || "";
  // An unknown phone gets nothing — fail closed, same rule as every other lane.
  if (!askerId) return NextResponse.json({ total: 0, shown: 0, capped: false, people: [], note: "unknown asker" });

  // ---- the chat catalog, for normalising chat names -----------------------
  const chatRows = await sbRequest<Array<{ chat_name: string }>>("chats?select=chat_name")
    .catch(() => [] as Array<{ chat_name: string }>);
  const knownChats = chatRows.map((c) => c.chat_name).filter(Boolean);
  const plan = expandConcepts(filters, knownChats);

  // ---- the event, when one was named --------------------------------------
  // TRAP: five catalog rows match "Summit Singapore" — the Summit itself plus
  // the Night Out, the Speaker's Lunch, the Women's Lunch and the Pre-Event
  // Dinner. Prefer an exact name, then the shortest name (side events append
  // words), and always ship what was resolved so a wrong pick is visible.
  let event: { name: string; at_record_id: string } | null = null;
  let eventMemberIds: string[] | null = null;
  let askerAttends = true;
  if (plan.event) {
    const q = encodeURIComponent(`*${plan.event.replace(/\s+/g, "%")}*`);
    const cands = await sbRequest<Array<{ at_record_id: string; name: string }>>(
      `events_catalog?select=at_record_id,name&name=ilike.${q}&limit=25`,
    ).catch(() => [] as Array<{ at_record_id: string; name: string }>);
    if (!cands.length) {
      return NextResponse.json({ total: 0, shown: 0, capped: false, people: [],
        note: `no event matches "${plan.event}" — say so plainly and do not guess an event` });
    }
    const exact = cands.find((c) => c.name.toLowerCase() === plan.event!.toLowerCase());
    event = exact || [...cands].sort((a, b) => a.name.length - b.name.length)[0];
    const regs = await sbRequest<Array<{ member_at_id: string }>>(
      `event_registrations_live?select=member_at_id&event_at_id=eq.${event.at_record_id}` +
      `&member_at_id=not.is.null&limit=${CANDIDATE_CAP}`,
    ).catch(() => [] as Array<{ member_at_id: string }>);
    eventMemberIds = [...new Set(regs.map((r) => r.member_at_id))];
    // #98: names from an event roster only for someone on that roster.
    askerAttends = eventMemberIds.includes(askerId);
  }

  // ---- the candidate id set ----------------------------------------------
  // With an event, the roster IS the population. Without one, start from the
  // narrowest filter we can push into PostgREST, then filter the rest in code.
  let ids: string[] = eventMemberIds || [];
  if (!eventMemberIds) {
    const wantChats = [...new Set([...plan.chats, ...plan.concepts.flatMap((c) => c.chats)])];
    const wantModels = [...new Set(plan.concepts.flatMap((c) => c.models))];
    const byChat = wantChats.length
      ? await Promise.all(wantChats.map((ch) =>
          sbRequest<Array<{ at_member_id: string }>>(
            // text[] containment is cs.{"MDS Resellers"} — the JSON form
            // (cs.["MDS Resellers"]) returns 22P02 malformed array literal.
            `members?select=at_member_id&channels_present=cs.${encodeURIComponent(`{"${ch}"}`)}` +
            `&at_member_id=not.is.null&limit=${CANDIDATE_CAP}`,
          ).catch(() => [] as Array<{ at_member_id: string }>)))
      : [];
    const byModel = wantModels.length
      ? await sbRequest<Array<{ at_member_id: string }>>(
          `member_attributes?select=at_member_id&business_model=ov.` +
          `${encodeURIComponent(`{${wantModels.map((m) => `"${m}"`).join(",")}}`)}&limit=${CANDIDATE_CAP}`,
        ).catch(() => [] as Array<{ at_member_id: string }>)
      : [];
    const union = new Set<string>([...byChat.flat().map((r) => r.at_member_id), ...byModel.map((r) => r.at_member_id)]);
    if (union.size) {
      ids = [...union];
    } else {
      // No chat/model filter: fall back to the member layer with one pushed-down
      // predicate so we never pull the whole population.
      const pushdown =
        plan.country.length ? `country=in.(${plan.country.map((c) => `"${c}"`).join(",")})`
        : plan.state.length ? `state=in.(${plan.state.map((c) => `"${c}"`).join(",")})`
        : plan.city.length ? `city=in.(${plan.city.map((c) => `"${c}"`).join(",")})`
        : plan.band.length ? `rev_band=in.(${plan.band.map((c) => `"${c}"`).join(",")})`
        : plan.niche.length ? `main_niche=in.(${plan.niche.map((c) => `"${c}"`).join(",")})`
        : null;
      const rows = await sbRequest<Array<{ at_member_id: string }>>(
        `member_attributes?select=at_member_id&membership_status=not.is.null` +
        (pushdown ? `&${pushdown}` : "") + `&limit=${CANDIDATE_CAP}`,
      ).catch(() => [] as Array<{ at_member_id: string }>);
      ids = rows.map((r) => r.at_member_id);
    }
  }
  if (!ids.length) {
    return NextResponse.json({ total: 0, shown: 0, capped: false, filters_echo: echo(plan), event, people: [],
      note: "nothing matched — say so plainly, never pad the answer with people who do not match" });
  }
  ids = ids.slice(0, CANDIDATE_CAP);
  const inList = ids.map((i) => `"${i}"`).join(",");

  // ---- the three reads, in parallel (measured ~0.7s for 127 ids) ----------
  const [members, attrs, profs] = await Promise.all([
    sbRequest<MemberRow[]>(`members?select=at_member_id,channels_present,membership_status&at_member_id=in.(${inList})`)
      .catch(() => [] as MemberRow[]),
    sbRequest<AttrRow[]>(
      `member_attributes?select=at_member_id,full_name,membership_status,business_model,city,state,country,` +
      `rev_band,main_niche,categories,expertise&at_member_id=in.(${inList})`,
    ).catch(() => [] as AttrRow[]),
    sbRequest<ProfRow[]>(`member_profiles?select=at_member_id,full_name,engagement_score&at_member_id=in.(${inList})`)
      .catch(() => [] as ProfRow[]),
  ]);

  const memberBy = new Map(members.map((m) => [m.at_member_id, m]));
  const profBy = new Map(profs.map((p) => [p.at_member_id, p]));
  const candidates: Candidate[] = attrs.map((a) => {
    const m = memberBy.get(a.at_member_id);
    const p = profBy.get(a.at_member_id);
    return {
      at_member_id: a.at_member_id,
      full_name: a.full_name || p?.full_name || null,
      membership_status: a.membership_status || m?.membership_status || null,
      chats: m?.channels_present || [],
      business_model: a.business_model || [],
      city: a.city, state: a.state, country: a.country, rev_band: a.rev_band,
      main_niche: a.main_niche, categories: a.categories || [], expertise: a.expertise,
      engagement_score: Number(p?.engagement_score || 0),
    };
  }).filter((c) => isMemberFacing(c.membership_status) && !!c.full_name);

  const matchedRows: Candidate[] = [];
  const matched: FoundPerson[] = [];
  for (const c of candidates) {
    const hit = matchCandidate(c, plan, askerId);
    if (hit) { matched.push(hit); matchedRows.push(c); }
  }

  const capped = applyCap(matched, limit);
  const namesAllowed = mode === "names" && askerAttends;
  const breakdown = mode === "breakdown" && group_by ? groupBy(matchedRows, group_by) : null;

  return NextResponse.json({
    total: capped.total,
    shown: namesAllowed ? capped.shown : 0,
    capped: namesAllowed ? capped.capped : false,
    filters_echo: echo(plan),
    ...(event ? { event } : {}),
    people: namesAllowed
      ? capped.people.map((p) => ({ name: p.name, reasons: p.reasons, city: p.city, niche: p.niche }))
      : [],
    breakdown,
    note: buildNote({ namesAllowed, askerAttends, mode, total: capped.total, shown: capped.shown,
                      unmatched: plan.unmatched, eventName: event?.name || null }),
  });
}

function echo(plan: ReturnType<typeof expandConcepts>) {
  return {
    concepts: plan.concepts.map((c) => c.label),
    chat: plan.chats, city: plan.city, state: plan.state, country: plan.country,
    band: plan.band, niche: plan.niche, category: plan.category,
    expertise: plan.expertise, event: plan.event,
    ...(plan.unmatched.length ? { unmatched: plan.unmatched } : {}),
  };
}

function buildNote(x: {
  namesAllowed: boolean; askerAttends: boolean; mode: string; total: number; shown: number;
  unmatched: string[]; eventName: string | null;
}): string {
  const parts: string[] = [];
  if (x.unmatched.length) {
    parts.push(`could not resolve ${x.unmatched.join(", ")} — say which part of the ask you could not honour`);
  }
  if (!x.askerAttends && x.eventName) {
    parts.push(`this person is not registered for ${x.eventName}, so answer with the count only, ` +
      `never the names, and do not explain internals`);
  } else if (x.namesAllowed && x.total > x.shown) {
    parts.push(`${x.total} people match; ${x.shown} are listed. The count is the truth — never say ` +
      `the listed names are all of them. Offer the rest if they want more.`);
  }
  parts.push("each person carries the reason they matched — say it in plain words (chat membership is " +
    "behaviour, a business model is what they told MDS on a form). Never quote scores or ranks.");
  return parts.join(". ");
}
```

- [ ] **Step 2: Typecheck and lint**

Run: `cd /Users/Born/mds-digest-web && npx tsc --noEmit && npm run lint`
Expected: no errors. Fix anything reported before continuing.

- [ ] **Step 3: Run the whole unit suite**

Run: `cd /Users/Born/mds-digest-web && npm test`
Expected: PASS, including the 22 finder tests.

- [ ] **Step 4: Probe the route locally**

```bash
cd /Users/Born/mds-digest-web && npm run dev
```

In a second shell (the secret is `OLIVIA_SCHEDULE_SECRET` in `.env.local`):

```bash
SECRET=$(grep '^OLIVIA_SCHEDULE_SECRET=' /Users/Born/mds-digest-web/.env.local | cut -d= -f2)
curl -s -X POST http://localhost:3000/api/olivia/find -H "Content-Type: application/json" \
  -H "X-Olivia-Secret: $SECRET" \
  -d '{"phone":"17866578153","filters":{"business_model":["reseller"]},"mode":"count"}'
```

Expected: `"total": 99` (the community union — 64 in the chat, 63 declared, 28 both, staff excluded).
Then the event form:

```bash
curl -s -X POST http://localhost:3000/api/olivia/find -H "Content-Type: application/json" \
  -H "X-Olivia-Secret: $SECRET" \
  -d '{"phone":"17866578153","filters":{"business_model":["reseller"],"event":"MDS Summit Singapore"},"mode":"count"}'
```

Expected: `"total": 21`, `"event": {"name":"MDS Summit Singapore", ...}` — and `people: []` with the
not-registered note, because Andy is not on that roster.

If a number differs, do NOT adjust the expectation — re-run the baseline SQL in the spec (§2) and find
out which side moved. Chat membership changes daily; a drift of one or two is real, a drift of ten is a bug.

- [ ] **Step 5: Commit**

```bash
cd /Users/Born/mds-digest-web
git add src/app/api/olivia/find/route.ts
git -c user.name="Andy Verdy" -c user.email="andy.verdy1@gmail.com" commit -m "#108: /api/olivia/find — composable member finder lane"
```

---

### Task 5: Ship the route and prove it live

**Files:**
- No new files. Deploys `mds-digest-web` main to Render.

**Interfaces:**
- Consumes: Task 4's route.
- Produces: a live `https://digest.mds.co/api/olivia/find` that nothing calls yet.

- [ ] **Step 1: Push**

```bash
cd /Users/Born/mds-digest-web && git push origin main
```

- [ ] **Step 2: Wait for the deploy, then probe production**

```bash
SECRET=$(grep '^OLIVIA_SCHEDULE_SECRET=' /Users/Born/mds-digest-web/.env.local | cut -d= -f2)
curl -s -X POST https://digest.mds.co/api/olivia/find -H "Content-Type: application/json" \
  -H "X-Olivia-Secret: $SECRET" \
  -d '{"phone":"17866578153","filters":{"business_model":["reseller"],"event":"MDS Summit Singapore"},"mode":"count"}'
```

Expected: the same `total: 21` and resolved event as the local probe. Retry for up to 3 minutes while
Render builds; a 404 means the deploy has not landed yet.

- [ ] **Step 3: Prove the auth and the allowlist on production**

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST https://digest.mds.co/api/olivia/find \
  -H "Content-Type: application/json" -d '{"phone":"17866578153","filters":{"chat":["MDS Resellers"]}}'
curl -s -X POST https://digest.mds.co/api/olivia/find -H "Content-Type: application/json" \
  -H "X-Olivia-Secret: $SECRET" -d '{"phone":"17866578153","filters":{"salary":["big"]}}'
```

Expected: `401`, then `{"error":"unknown filter: salary"}`.

- [ ] **Step 4: Record the live numbers**

Append the three probe results (community count, event count, resolved event id) to the scratch notes
you will use for the close block. The lane is dead code until Task 6 — nothing in the workflow calls it.

---

### Task 6: Wire the tool into STAGING (and fix `event_who`)

**Files:**
- Create: `Scorecard/scripts/olivia_loop/apply_108_member_find.py`

**Interfaces:**
- Consumes: the live route from Task 5.
- Produces: `member_find` in the Answer Seed tool list; `Answer Tool` routes `member_find` → `/api/olivia/find` and merges `op: "people"` into every `event_who` call.

- [ ] **Step 1: Take the staging lock**

```bash
cd /Users/Born/Scorecard && python3 scripts/olivia_wf.py lock
python3 scripts/olivia_wf.py snapshot staging pre-108
```

If `lock` is refused by the session classifier, ask Andy to run it — do not edit staging without it.

- [ ] **Step 2: Write the apply script**

Create `Scorecard/scripts/olivia_loop/apply_108_member_find.py`:

```python
#!/usr/bin/env python3
"""#108 — the member finder tool, plus the event_who routing fix.

Three edits, one PUT, one bounce (STAGING only):
  Answer Tool  url + body gain a member_find branch -> /api/olivia/find,
               and every event_who call now carries op='people' (without it the
               schedule route falls through to op='next' and answers a people
               question with the public agenda).
  Answer Seed  the member_find tool declaration (before multi_source)
  Answer Seed  one routing rule: filter-shaped people questions call member_find.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}",
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json",
           "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


TOOL_DECL = (
    "  { name: 'member_find', description: 'FIND MEMBERS BY FILTERS THAT COMBINE (#108) — chat "
    "membership, business model, event attendance, city/state/country, revenue band, niche, "
    "expertise text. THE tool for \\'which resellers are coming to the Summit\\', \\'who in MDS is "
    "an agency\\', \\'of those, who is in Europe\\'. Filters AND together; a list inside one filter "
    "ORs. Business-model words are understood (reseller, wholesale, arbitrage, dropshipping, "
    "private label, brand owner, agency, OEM) and a reseller is anyone who is EITHER in the "
    "MDS Resellers chat OR declared wholesale on a form - every person comes back with the reason "
    "they matched, so SAY the reason. mode=names returns people (at most 10, with the true total), "
    "mode=count returns the number, mode=breakdown with group_by returns counts per value. To "
    "narrow a previous answer, send the SAME filters plus the new one - filters_echo in the last "
    "result is that set. Names for an event roster are only returned to someone registered for it; "
    "otherwise answer with the count and stop. NOT for meaning-based searches of what someone knows "
    "- that is expertise_search.',\n"
    "    input_schema: S({ chat: arr('chat names, e.g. MDS Resellers'), "
    "business_model: arr('business model words, e.g. reseller, agency'), "
    "event: str('event name words, e.g. Summit Singapore'), city: arr('cities'), "
    "state: arr('US states, full names'), country: arr('countries'), "
    "band: arr('revenue bands: 1-5M, 5-10M, 10-20M, 20M+'), niche: arr('product niches'), "
    "category: arr('product categories'), expertise: str('words that must appear in their "
    "expertise text'), mode: str('names | count | breakdown'), "
    "group_by: str('country | state | city | band | niche | business_model | chat'), "
    "limit: num('max names, default 10') }) },\n"
)

RULE = (
    "  '- FILTERED PEOPLE QUESTIONS GO TO member_find (#108): any who-is / who-is-coming question "
    "that names a GROUP - a chat, a business model (resellers, agencies, private label), a country, "
    "a revenue band, an event roster, or several of those at once - is a FILTER question, not a "
    "topic search. Call member_find, combine the filters the member actually said, and say each "
    "person\\'s reason in plain words. A follow-up that narrows (\\'of those, who is in Europe\\') "
    "re-sends the same filters plus the new one. Never answer a filter question by sampling topics, "
    "and never claim the listed names are everyone when the tool reports a bigger total.',\n"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    at = nodes["Answer Tool"]["parameters"]
    if "member_find" in at["url"]:
        print("Answer Tool: already wired")
    else:
        anchor = "String($json.tool_name||'').startsWith('event_') ? 'https://digest.mds.co/api/olivia/schedule'"
        assert at["url"].count(anchor) == 1, f"Answer Tool url drifted:\n{at['url'][:300]}"
        at["url"] = at["url"].replace(
            anchor,
            "String($json.tool_name||'') === 'member_find' ? 'https://digest.mds.co/api/olivia/find' : " + anchor)

        body = at["jsonBody"]
        # event_who must carry op='people'; without it the schedule route
        # defaults to op='next' and returns the public agenda (proven live
        # 2026-08-22). member_find takes the asker's phone like the event lane.
        body_anchor = "(String($json.tool_name||'').startsWith('event_') || String($json.tool_name||'') === 'org_docs')"
        assert body.count(body_anchor) == 1, "Answer Tool body anchor not found"
        body = body.replace(
            body_anchor,
            "(String($json.tool_name||'').startsWith('event_') || String($json.tool_name||'') === 'org_docs' "
            "|| String($json.tool_name||'') === 'member_find')")
        # merge the op for event_who only
        assert "{ phone: $('Resolve Member').first().json.to }" in body, "phone-merge shape drifted"
        body = body.replace(
            "{ phone: $('Resolve Member').first().json.to }",
            "Object.assign({ phone: $('Resolve Member').first().json.to }, "
            "String($json.tool_name||'') === 'event_who' ? { op: 'people' } : {})")
        at["jsonBody"] = body
        print("Answer Tool: member_find branch + event_who op='people'")

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    if "member_find" in seed:
        print("Answer Seed: already declared")
    else:
        anchor = "  { name: 'multi_source',"
        assert seed.count(anchor) == 1, "multi_source anchor not found"
        seed = seed.replace(anchor, TOOL_DECL + anchor)
        rule_anchor = "  '- POLICY COMES FROM WRITTEN DOCUMENTS (#18)"
        assert seed.count(rule_anchor) == 1, "rule anchor not found"
        seed = seed.replace(rule_anchor, RULE + rule_anchor)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(seed); tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
        nodes["Answer Seed"]["parameters"]["jsCode"] = seed
        print("Answer Seed: tool + rule added, node --check OK")

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")
    print("PUT + one bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    assert "api/olivia/find" in n2["Answer Tool"]["parameters"]["url"]
    assert "op: 'people'" in n2["Answer Tool"]["parameters"]["jsonBody"]
    assert "member_find" in n2["Answer Seed"]["parameters"]["jsCode"]
    assert "FILTERED PEOPLE QUESTIONS GO TO member_find (#108)" in n2["Answer Seed"]["parameters"]["jsCode"]
    print(f"verified · staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Dry-check the anchors before writing anything**

Run:

```bash
cd /Users/Born/Scorecard && python3 - <<'PY'
import json
d = json.load(open(sorted(__import__('glob').glob('olivia_snapshots/staging_*.json'))[-1]))
wf = d if 'nodes' in d else d['workflow']
n = {x['name']: x for x in wf['nodes']}
at = n['Answer Tool']['parameters']
print('url anchor  :', at['url'].count("String($json.tool_name||'').startsWith('event_') ? 'https://digest.mds.co/api/olivia/schedule'"))
print('body anchor :', at['jsonBody'].count("(String($json.tool_name||'').startsWith('event_') || String($json.tool_name||'') === 'org_docs')"))
print('phone merge :', at['jsonBody'].count("{ phone: $('Resolve Member').first().json.to }"))
seed = n['Answer Seed']['parameters']['jsCode']
print('multi_source:', seed.count("  { name: 'multi_source',"))
print('rule anchor :', seed.count("  '- POLICY COMES FROM WRITTEN DOCUMENTS (#18)"))
PY
```

Expected: every count is `1`. A `0` means the node drifted — find the new anchor text and update the
script before running it. Never loosen an assertion to make it pass.

- [ ] **Step 4: Apply**

Run: `cd /Users/Born/Scorecard && python3 scripts/olivia_loop/apply_108_member_find.py`
Expected: three "added" lines, `node --check OK`, `PUT + one bounce done`, `verified · staging versionId: …`.

- [ ] **Step 5: Commit the script**

```bash
cd /Users/Born/Scorecard
git add scripts/olivia_loop/apply_108_member_find.py
git commit -m "#108: staging apply — member_find tool + event_who op fix

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Prove it on staging

**Files:**
- Create: `Scorecard/scripts/one_shots/canary_108.py` (insert/delete the temporary registration)
- No other new files. Probes run through `scripts/olivia_selftest.py --staging`.

**Interfaces:**
- Consumes: Task 6's staging workflow.
- Produces: six execution ids evidencing the ACs, and a database left exactly as it was found.

> **Only Andy's phone may be simulated** — `PROBE_PHONE = "17866578153"` in `olivia_selftest.py`,
> commented "the only member whose phone may be simulated". Never fire as another member.
> Andy is not on the Summit roster, so the registered-attendee probes need the **canary pattern**
> proven in #99: insert one temporary registration row, probe, delete it in the same session.
> `event_registrations_live` is a VIEW — write to the table `digest.event_registrations`.
> Staging replies do not reach Meta: verified 2026-08-22 by firing two staging probes and finding
> zero new rows in `digest.olivia_sends`. They DO write `digest.olivia_messages`, so clean up after.

- [ ] **Step 1: Probe the two non-registered cases first (no canary needed)**

Run each on its own line, exactly as written — the questions must be quoted arguments:

```bash
cd /Users/Born/Scorecard
python3 scripts/olivia_selftest.py --staging --questions "reset" "which resellers are coming to the Summit?"
python3 scripts/olivia_selftest.py --staging --questions "reset" "who in MDS resells?"
```

Expected: probe 1 answers with the count and **no attendee names** (Andy is not registered — AC 6
working); probe 2 names members with reasons, because with no event filter there is no roster gate.
Record both execution ids from the script output.

- [ ] **Step 2: Write the canary script**

Create `Scorecard/scripts/one_shots/canary_108.py`:

```python
#!/usr/bin/env python3
"""#108 probe canary — a temporary Summit registration for the probe member.

    python3 scripts/one_shots/canary_108.py add
    python3 scripts/one_shots/canary_108.py remove   # ALWAYS run this, pass or fail

event_registrations_live is a view; the writable table is digest.event_registrations.
"""
import importlib.util, json, subprocess, sys

EVENT = "recrATwhUDA55iQN5"          # MDS Summit Singapore (NOT the Night Out row)
ROSTER_ID = "canary-108"
PHONE = "17866578153"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/"

spec = importlib.util.spec_from_file_location("g", "scripts/olivia_leak_gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
KEY = g.load_key()


def call(method, path, body=None, prefer=None):
    cmd = ["curl", "-s", "-X", method, BASE + path,
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "apikey: " + KEY, "-H", "Authorization: Bearer " + KEY]
    if prefer:
        cmd += ["-H", "Prefer: " + prefer]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "add":
        me = json.loads(call("GET", "members?select=at_member_id&phone=eq." + PHONE))
        assert me, "probe member not found"
        row = {"roster_record_id": ROSTER_ID, "event_at_id": EVENT,
               "member_at_id": me[0]["at_member_id"], "full_name": "CANARY 108",
               "email": "canary-108@example.invalid", "ticket_status": "Confirmed",
               "source": "canary"}
        print(call("POST", "event_registrations", row, prefer="return=representation")[:300])
    elif action == "remove":
        call("DELETE", "event_registrations?roster_record_id=eq." + ROSTER_ID)
    left = call("GET", "event_registrations?select=roster_record_id&roster_record_id=eq." + ROSTER_ID)
    print("canary rows now:", left.strip())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Add the canary and confirm the asker is now registered**

```bash
cd /Users/Born/Scorecard && python3 scripts/one_shots/canary_108.py add
```

Expected: the inserted row echoes back, then `canary rows now: [{"roster_record_id":"canary-108"}]`.
If the insert 400s on a column the table does not have, read the table's columns and send only those —
never drop a NOT NULL constraint to make it fit.

- [ ] **Step 4: Run the four registered-attendee probes**

```bash
cd /Users/Born/Scorecard
python3 scripts/olivia_selftest.py --staging --questions "reset" "which resellers are coming to the Summit?" "of those, who is in Europe?" "group them by country" "who is coming to the Summit?"
```

Then read each execution's **`Answer Tool` output** (not just the reply text — a good sentence built on a
bad tool result still fails):

| probe | what must be true in the execution |
|---|---|
| resellers at the Summit | `member_find` called with `business_model:["reseller"]` and `event`; `total: 21`; at most 10 names; every person carries `reasons` |
| of those, in Europe | the SAME filters plus `country`; a smaller total; no fresh topic-word guess |
| group them by country | `mode:"breakdown"`, `breakdown` rows present, `people: []` |
| who is coming (plain) | the `event_who` result holds ATTENDEES — no `next` / `Arrivals` agenda block |

- [ ] **Step 5: Remove the canary — run this even if a probe failed**

```bash
cd /Users/Born/Scorecard && python3 scripts/one_shots/canary_108.py remove
```

Expected: `canary rows now: []`. A leftover canary row grants the probe member attendee visibility they
should not have; this step is not optional.

- [ ] **Step 6: Clean the probe conversation and snapshot**

```bash
cd /Users/Born/Scorecard
python3 scripts/olivia_selftest.py --cleanup
python3 scripts/olivia_wf.py snapshot --target staging --label 108-member-find
```

Then confirm the thread is clean:

```bash
python3 - <<'PY'
import importlib.util, subprocess
spec = importlib.util.spec_from_file_location("g", "scripts/olivia_leak_gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
key = g.load_key()
out = subprocess.run(["curl", "-s",
  "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1/olivia_messages?select=id,text"
  "&phone=eq.17866578153&order=created_at.desc&limit=5",
  "-H", "Accept-Profile: digest", "-H", "apikey: " + key,
  "-H", "Authorization: Bearer " + key], capture_output=True, text=True).stdout
print(out[:400])
PY
```

Expected: no probe rows from this run left behind. Delete any that remain by id.

### Task 8: Gate checks

**Files:**
- Modify: `Scorecard/scripts/olivia_leak_gate.py`

**Interfaces:**
- Consumes: the live route.
- Produces: six new named checks in the gate's output.

- [ ] **Step 1: Add the checks**

Add a `member_find` section to `scripts/olivia_leak_gate.py`, next to the other route-lane checks, using
the file's existing `check(...)` and `curl(...)` helpers and the `olivia_secret` already loaded in `main()`:

```python
    # ---- #108 member finder -------------------------------------------------
    FIND = "https://digest.mds.co/api/olivia/find"

    def find(body, secret_hdr=True):
        hdrs = ["Content-Type: application/json"]
        if secret_hdr:
            hdrs.append(f"X-Olivia-Secret: {olivia_secret}")
        cmd = ["curl", "-s", "-o", "-", "-w", "\n%{http_code}", "-m", "60", "-X", "POST", FIND]
        for h in hdrs:
            cmd += ["-H", h]
        cmd += ["-d", json.dumps(body)]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        text, _, code = out.rpartition("\n")
        try:
            return int(code), json.loads(text or "{}")
        except Exception:
            return int(code), {}

    st, _ = find({"phone": phone, "filters": {"chat": ["MDS Resellers"]}}, secret_hdr=False)
    check("member_find without the secret is 401", st == 401)

    st, body = find({"phone": "10000000000", "filters": {"chat": ["MDS Resellers"]}})
    check("member_find unknown phone = zero rows", st == 200 and body.get("total") == 0
          and not body.get("people"))

    st, body = find({"phone": phone, "filters": {"salary": ["big"]}})
    check("member_find rejects an unknown filter", st == 400
          and "unknown filter" in str(body.get("error", "")))

    st, body = find({"phone": phone, "filters": {}})
    check("member_find refuses a filter-less roster dump", st == 400)

    st, body = find({"phone": phone, "filters": {"business_model": ["reseller"]}, "limit": 50})
    names = body.get("people") or []
    check("member_find never lists more than 10 names", len(names) <= 10)
    check("member_find keeps the true total above the cap", int(body.get("total", 0)) >= len(names))
    check("member_find emits no scores", not re.search(r'"(engagement_score|score|rank|pct)"',
                                                       json.dumps(body)))

    staff = curl("GET", f"{BASE}/member_attributes?select=full_name&membership_status=eq.Staff&limit=5",
                 key, profile_hdr=["Accept-Profile: digest"])[1] or []
    staff_names = {s["full_name"] for s in staff if s.get("full_name")}
    st, body = find({"phone": phone, "filters": {"country": ["United States"]}, "limit": 10})
    listed = {p.get("name") for p in (body.get("people") or [])}
    check("member_find never lists a Staff record", not (staff_names & listed))

    st, body = find({"phone": phone,
                     "filters": {"business_model": ["reseller"], "event": "MDS Summit Singapore"}})
    check("member_find withholds names from a non-registered asker",
          not body.get("people") and int(body.get("total", 0)) > 0)
```

If `re` or `subprocess` is not already imported at the top of the gate, add the import.

- [ ] **Step 2: Run the gate**

Run: `cd /Users/Born/Scorecard && python3 scripts/olivia_leak_gate.py; echo "EXIT $?"`
Expected: every check passes and the last line is `EXIT 0`. A failing check is a bug in the route, not in
the check — fix the route.

- [ ] **Step 3: Commit**

```bash
cd /Users/Born/Scorecard
git add scripts/olivia_leak_gate.py
git commit -m "#108: gate — six member_find checks (auth, allowlist, cap, staff, event gating, no scores)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: Docs, close block, handoff

**Files:**
- Modify: `Scorecard/OLIVIA_SPRINT_4.md` (#108 close block), `OLIVIA_HANDBOOK.md` (the lane + the tool), `OLIVIA_NEXT_SESSION.md` (state + queue), `SESSION_LOG_OLIVIA.md` (full entry) and `SESSION_LOG.md` (one index line).

**Interfaces:**
- Consumes: the probe ids from Task 7, the gate result from Task 8, the live numbers from Task 5.

- [ ] **Step 1: Write the #108 close block**

Replace the one-line #108 row in the at-a-glance table with a full ticket block carrying: the story, the
seven ACs from the spec with met/not against each, the before/after numbers (before: topic-sample named
brand owners and missed all three resellers; after: 21 at the Summit / 99 community with per-person
reasons), the probe execution ids, `gate EXIT 0`, and the note that PROMOTE is Andy's.

- [ ] **Step 2: Update the handbook**

Add `member_find` to the tool table and a short section under the retrieval chapter: what the lane is,
the closed allowlist, where policy lives, the concept map, and the two data caveats (self-declared model,
behaviour-based chat membership).

- [ ] **Step 3: Update the handoff and the logs**

`OLIVIA_NEXT_SESSION.md`: new STATE paragraph — what is on staging, what awaits Andy's promote, the
follow-ups (#111 verification, retiring the older lanes, the #32 caching item).
`SESSION_LOG_OLIVIA.md`: full dated entry. `SESSION_LOG.md`: one index line.

- [ ] **Step 4: Commit**

```bash
cd /Users/Born/Scorecard
git add OLIVIA_SPRINT_4.md OLIVIA_HANDBOOK.md OLIVIA_NEXT_SESSION.md SESSION_LOG_OLIVIA.md SESSION_LOG.md
git commit -m "#108: close block, handbook lane entry, handoff + session log

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Hand to Andy**

Report in his format — result first, then the AC checklist (met/not), then the before/after numbers, then
exactly two asks:

1. **Promote** — `python3 scripts/olivia_wf.py promote` (staging carries the tool + the `event_who` fix).
2. **Eval run** — the 100-question bank on staging before the promote, to catch tool cannibalisation
   (the model choosing `member_find` where `expertise_search` was right). This is an eval RUN, so it needs
   his go; say so plainly rather than assuming it.

Release the lock either way: `python3 scripts/olivia_wf.py unlock`.

---

## Follow-ups (file, do not build here)

- `member_match`, `member_count` and the schedule `op=people` matcher still carry their own copies of the
  disclosure rules. Re-pointing them at the finder removes three divergent implementations.
- #111 (who-to-meet swings with the model's free-text topic query) should close as a side effect of the
  concept map — verify against executions 97152 and 97286 before claiming it.
- #106 stays open for the lanes outside the finder.
- The 8 rows whose business model reads `OEM Design & Development'Wholesale and/or Arbitrage` need an
  Airtable-side fix; the finder matches them, it does not repair them.
- #32 carries the uncached-answer-node finding — caching the prefix would make this tool's ~400 tokens free.
