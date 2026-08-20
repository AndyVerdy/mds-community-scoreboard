# Mille In-App Widget (POC) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put Mille inside the MDS iOS app as an Intercom-style panel — a launcher opens a hosted chat over the app, one thread, no chat code in the app.

**Architecture:** A token-gated page on `digest.mds.co` (`/widget/mille`) holds the entire messenger — history, send, thinking state, retry. The app presents it in a `WKWebView` modal sheet. Two thin API routes back the page, both reusing the pipe that is already live: fire a `wamid.SELFTEST*` inbound at the prod n8n webhook (silent — never delivered via Meta), poll `digest.olivia_messages` for the reply. **Nothing in Mille changes:** no workflow edit, no migration, no prompt or seed change, no new retrieval path.

**Tech Stack:** Next.js 16 route handlers + React 19 client component (mds-digest-web, Render) · `jose` JWT cookie · Supabase PostgREST via `sbRequest` · SwiftUI + WKWebView (mds-ios-app, XcodeGen) · vitest.

**Spec:** `docs/superpowers/specs/2026-08-20-mille-in-app-widget-design.md`

## Global Constraints

- **The `wamid.SELFTEST` prefix is what keeps the turn silent.** Every widget send must use `wamid.SELFTEST_WIDGET_<ts>_<rand>`. Lose the prefix and the widget starts sending real WhatsApp messages to Andy's phone.
- **The asking identity is a server-side constant and never a request parameter** — `PROBE_PHONE = "17866578153"`, `PROBE_NAME = "Andy"`.
- **Target is prod only.** No staging toggle in the widget; `target` is not accepted from the client.
- **One thread.** No Messages list, no thread selection.
- **No secret in page JavaScript.** The widget token is exchanged for an httpOnly cookie on entry; page JS only ever calls same-origin routes.
- **The widget page is `noindex`.**
- **Out of scope, do not build:** per-user identity, a `channel` column, images, quick-reply buttons, push, streaming, rate limiting.
- **iOS: bump `CFBundleVersion` in `project.yml` in the same commit as any app change** (standing rule).
- **Gate `python3 scripts/olivia_leak_gate.py` must EXIT 0 before ship** — run it directly, never piped through `tail`.
- Repos stay separate: `mds-digest-web` and `mds-ios-app` are their own git repos with their own commits. The spec/plan/board live in `Scorecard`.

## Prerequisites (Andy runs)

1. Generate the widget token and add it to the **Render** service for `digest.mds.co` as `OLIVIA_WIDGET_TOKEN`, then **manually redeploy** (Render does not redeploy on an env change):
   ```bash
   openssl rand -hex 24
   ```
2. Hand that same value back so it can go into the Swift constant (Task 6).

---

### Task 1: Widget auth helpers

**Files:**
- Create: `src/lib/mille-widget.ts` (mds-digest-web)
- Test: `src/lib/mille-widget.test.ts`

**Interfaces:**
- Consumes: `jose` (already a dependency), node `crypto`.
- Produces: `MILLE_WIDGET_COOKIE: string` · `MILLE_WIDGET_TTL_HOURS: number` · `widgetTokenMatches(supplied: string | null | undefined, expected: string | undefined): boolean` · `issueWidgetJwt(secret: string): Promise<string>` · `widgetJwtIsValid(jwt: string | undefined, secret: string): Promise<boolean>`. Tasks 2 and 3 use exactly these names.

- [ ] **Step 1: Write the failing test**

Create `src/lib/mille-widget.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import {
  MILLE_WIDGET_COOKIE,
  issueWidgetJwt,
  widgetJwtIsValid,
  widgetTokenMatches,
} from "./mille-widget";

const SECRET = "test-secret-at-least-32-characters-long!!";

describe("widgetTokenMatches", () => {
  it("accepts the exact token", () => {
    expect(widgetTokenMatches("abc123", "abc123")).toBe(true);
  });
  it("rejects a wrong token of equal length", () => {
    expect(widgetTokenMatches("abc124", "abc123")).toBe(false);
  });
  it("rejects a wrong token of different length", () => {
    expect(widgetTokenMatches("abc", "abc123")).toBe(false);
  });
  it("rejects a missing supplied token", () => {
    expect(widgetTokenMatches(null, "abc123")).toBe(false);
    expect(widgetTokenMatches("", "abc123")).toBe(false);
  });
  it("rejects when the server has no token configured", () => {
    expect(widgetTokenMatches("abc123", undefined)).toBe(false);
    expect(widgetTokenMatches("abc123", "")).toBe(false);
  });
});

describe("widget jwt", () => {
  it("issues a jwt that verifies with the same secret", async () => {
    const jwt = await issueWidgetJwt(SECRET);
    expect(await widgetJwtIsValid(jwt, SECRET)).toBe(true);
  });
  it("rejects a jwt signed with another secret", async () => {
    const jwt = await issueWidgetJwt("another-secret-at-least-32-chars-long!!!");
    expect(await widgetJwtIsValid(jwt, SECRET)).toBe(false);
  });
  it("rejects a tampered jwt", async () => {
    const jwt = await issueWidgetJwt(SECRET);
    expect(await widgetJwtIsValid(jwt + "x", SECRET)).toBe(false);
  });
  it("rejects an absent jwt", async () => {
    expect(await widgetJwtIsValid(undefined, SECRET)).toBe(false);
  });
  it("names the cookie", () => {
    expect(MILLE_WIDGET_COOKIE).toBe("mds_mille_widget");
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/Born/mds-digest-web && npx vitest run src/lib/mille-widget.test.ts
```
Expected: FAIL — cannot resolve `./mille-widget`.

- [ ] **Step 3: Write the implementation**

Create `src/lib/mille-widget.ts`:

```ts
import { timingSafeEqual } from "crypto";
import { SignJWT, jwtVerify } from "jose";

// Auth for the in-app Mille widget (POC). The app holds an opaque token; the
// entry route trades it for an httpOnly cookie so page JavaScript never sees a
// secret. POC-grade on purpose: the identity behind it is Andy's own and the
// token is rotatable from env. Real per-member identity is a separate build.

const enc = new TextEncoder();

export const MILLE_WIDGET_COOKIE = "mds_mille_widget";
export const MILLE_WIDGET_TTL_HOURS = 12;

/** Constant-time compare that never throws on length mismatch. */
export function widgetTokenMatches(
  supplied: string | null | undefined,
  expected: string | undefined,
): boolean {
  if (!supplied || !expected) return false;
  const a = Buffer.from(supplied, "utf8");
  const b = Buffer.from(expected, "utf8");
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}

export async function issueWidgetJwt(secret: string): Promise<string> {
  return new SignJWT({ kind: "mille_widget" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(`${MILLE_WIDGET_TTL_HOURS}h`)
    .sign(enc.encode(secret));
}

export async function widgetJwtIsValid(
  jwt: string | undefined,
  secret: string,
): Promise<boolean> {
  if (!jwt) return false;
  try {
    const { payload } = await jwtVerify(jwt, enc.encode(secret));
    return payload.kind === "mille_widget";
  } catch {
    return false;
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd /Users/Born/mds-digest-web && npx vitest run src/lib/mille-widget.test.ts
```
Expected: PASS, 10 tests.

- [ ] **Step 5: Commit**

```bash
cd /Users/Born/mds-digest-web && git add src/lib/mille-widget.ts src/lib/mille-widget.test.ts && git commit -m "feat(mille-widget): token + cookie auth helpers"
```

---

### Task 2: Entry route — token in, cookie out

**Files:**
- Create: `src/app/api/olivia/widget/enter/route.ts` (mds-digest-web)

**Interfaces:**
- Consumes: `widgetTokenMatches`, `issueWidgetJwt`, `MILLE_WIDGET_COOKIE`, `MILLE_WIDGET_TTL_HOURS` from Task 1; `config.session.secret` from `@/lib/config`; env `OLIVIA_WIDGET_TOKEN`.
- Produces: `GET /api/olivia/widget/enter?k=<token>` → `302` to `/widget/mille` with the httpOnly cookie set, or `401` plain text. This is the only URL the app ever loads.

- [ ] **Step 1: Write the route**

Create `src/app/api/olivia/widget/enter/route.ts`:

```ts
import { NextRequest, NextResponse } from "next/server";
import { config } from "@/lib/config";
import {
  MILLE_WIDGET_COOKIE,
  MILLE_WIDGET_TTL_HOURS,
  issueWidgetJwt,
  widgetTokenMatches,
} from "@/lib/mille-widget";

// The app's single entry point into the widget: it carries the opaque token in
// the URL, we trade it for an httpOnly cookie and redirect to the panel. The
// token never reaches page JavaScript, and the cookie expires on its own.
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const supplied = req.nextUrl.searchParams.get("k");
  if (!widgetTokenMatches(supplied, process.env.OLIVIA_WIDGET_TOKEN)) {
    return new NextResponse("unauthorized", {
      status: 401,
      headers: { "content-type": "text/plain" },
    });
  }

  const jwt = await issueWidgetJwt(config.session.secret);
  const res = NextResponse.redirect(new URL("/widget/mille", req.url));
  res.cookies.set(MILLE_WIDGET_COOKIE, jwt, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: MILLE_WIDGET_TTL_HOURS * 3600,
  });
  return res;
}
```

- [ ] **Step 2: Verify locally against a dev server**

```bash
cd /Users/Born/mds-digest-web && OLIVIA_WIDGET_TOKEN=localtoken npm run dev
```
In a second shell:
```bash
curl -si "http://localhost:3000/api/olivia/widget/enter?k=wrong" | head -3
```
Expected: `HTTP/1.1 401`.
```bash
curl -si "http://localhost:3000/api/olivia/widget/enter?k=localtoken" | egrep -i "^HTTP|^location|set-cookie"
```
Expected: `307`/`302`, `location: /widget/mille`, `set-cookie: mds_mille_widget=…; HttpOnly`.

- [ ] **Step 3: Commit**

```bash
cd /Users/Born/mds-digest-web && git add src/app/api/olivia/widget/enter/route.ts && git commit -m "feat(mille-widget): entry route trades the app token for a session cookie"
```

---

### Task 3: Messages route — history and send

**Files:**
- Create: `src/app/api/olivia/widget/messages/route.ts` (mds-digest-web)
- Reference (do not modify): `src/app/api/olivia/test-chat/route.ts`

**Interfaces:**
- Consumes: `MILLE_WIDGET_COOKIE`, `widgetJwtIsValid` (Task 1); `sbRequest`, `isSupabaseConfigured` from `@/lib/supabase`; `config.session.secret`.
- Produces:
  - `GET /api/olivia/widget/messages` → `{ rows: WidgetRow[] }`, the last 30 turns oldest-first.
  - `GET /api/olivia/widget/messages?after=<id>` → `{ rows }`, turns newer than `<id>`, oldest-first.
  - `POST /api/olivia/widget/messages` with `{ text }` → `{ ok: true, wamid }` or `4xx/502` `{ error }`.
  - `export type WidgetRow = { id: number; role: string; route: string | null; text: string; created_at: string }`. Task 4 renders exactly this shape.

- [ ] **Step 1: Write the route**

Create `src/app/api/olivia/widget/messages/route.ts`:

```ts
import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { config } from "@/lib/config";
import { MILLE_WIDGET_COOKIE, widgetJwtIsValid } from "@/lib/mille-widget";
import { isSupabaseConfigured, sbRequest } from "@/lib/supabase";

// The in-app widget's only data route. Same pipe as the admin test chat:
// simulate a Meta inbound at the PROD workflow with a SELFTEST wamid (the
// workflow's Eval (silent)? branch saves the turn and never sends via Meta),
// then read her reply back out of the conversation log.
//
// Safety properties:
//   - The asking identity is a server constant, never a request parameter.
//   - Target is prod, hardcoded: the widget has no staging toggle.
//   - Auth is the widget cookie issued by /api/olivia/widget/enter.
export const dynamic = "force-dynamic";

const PROBE_PHONE = "17866578153"; // Andy — the only member whose phone may be simulated
const PROBE_NAME = "Andy";
const WEBHOOK =
  process.env.OLIVIA_N8N_WEBHOOK_URL ||
  "https://mdsco.app.n8n.cloud/webhook/olivia-wa-live";
const FIRE_TIMEOUT_MS = 15_000;

export type WidgetRow = {
  id: number;
  role: string;
  route: string | null;
  text: string;
  created_at: string;
};

async function requireWidgetSession(): Promise<NextResponse | null> {
  const store = await cookies();
  const jwt = store.get(MILLE_WIDGET_COOKIE)?.value;
  if (!(await widgetJwtIsValid(jwt, config.session.secret))) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!isSupabaseConfigured()) {
    return NextResponse.json({ error: "supabase not configured" }, { status: 500 });
  }
  return null;
}

export async function GET(req: NextRequest) {
  const gate = await requireWidgetSession();
  if (gate) return gate;

  const after = Number(req.nextUrl.searchParams.get("after") || 0);
  const base = `olivia_messages?phone=eq.${PROBE_PHONE}&select=id,role,route,text,created_at`;
  const rows = await sbRequest<WidgetRow[]>(
    after > 0
      ? `${base}&id=gt.${after}&order=id.asc&limit=50`
      : `${base}&order=id.desc&limit=30`,
  );
  return NextResponse.json({ rows: after > 0 ? rows : rows.slice().reverse() });
}

export async function POST(req: NextRequest) {
  const gate = await requireWidgetSession();
  if (gate) return gate;

  let body: { text?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
  const text = String(body.text || "").trim();
  if (!text) return NextResponse.json({ error: "empty message" }, { status: 400 });
  if (text.length > 4096) {
    return NextResponse.json({ error: "message too long" }, { status: 400 });
  }

  const ts = Math.floor(Date.now() / 1000);
  const wamid = `wamid.SELFTEST_WIDGET_${ts}_${Math.random().toString(36).slice(2, 8)}`;
  const payload = {
    entry: [
      {
        changes: [
          {
            value: {
              messaging_product: "whatsapp",
              metadata: {
                display_phone_number: "19453965415",
                phone_number_id: "1306956855827812",
              },
              contacts: [{ profile: { name: PROBE_NAME }, wa_id: PROBE_PHONE }],
              messages: [
                {
                  from: PROBE_PHONE,
                  id: wamid,
                  timestamp: String(ts),
                  type: "text",
                  text: { body: text },
                },
              ],
            },
            field: "messages",
          },
        ],
      },
    ],
  };

  try {
    const res = await fetch(WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(FIRE_TIMEOUT_MS),
    });
    if (!res.ok) {
      return NextResponse.json(
        { error: `webhook returned ${res.status}` },
        { status: 502 },
      );
    }
  } catch (err) {
    return NextResponse.json(
      { error: `webhook unreachable: ${err instanceof Error ? err.message : "error"}` },
      { status: 502 },
    );
  }

  return NextResponse.json({ ok: true, wamid });
}
```

- [ ] **Step 2: Verify the auth gate locally**

With the dev server from Task 2 still running:
```bash
curl -si http://localhost:3000/api/olivia/widget/messages | head -2
```
Expected: `HTTP/1.1 401` and `{"error":"unauthorized"}` — no cookie, no data.

```bash
curl -s -c /tmp/mille.jar "http://localhost:3000/api/olivia/widget/enter?k=localtoken" -o /dev/null && curl -s -b /tmp/mille.jar http://localhost:3000/api/olivia/widget/messages | head -c 200
```
Expected: a `{"rows":[…]}` payload with real turns.

- [ ] **Step 3: Commit**

```bash
cd /Users/Born/mds-digest-web && git add src/app/api/olivia/widget/messages/route.ts && git commit -m "feat(mille-widget): history + send route on the silent prod pipe"
```

---

### Task 4: The panel — bare layout, page, client component

**Files:**
- Create: `src/app/widget/layout.tsx` (mds-digest-web)
- Create: `src/app/widget/mille/page.tsx`
- Create: `src/components/olivia/MilleWidget.tsx`
- Reference (do not modify): `src/components/admin/OliviaTestChat.tsx`, `src/app/singapore/layout.tsx`

**Interfaces:**
- Consumes: `GET/POST /api/olivia/widget/messages` and the `WidgetRow` type from Task 3.
- Produces: the page at `/widget/mille`. Its close button calls `window.webkit.messageHandlers.mille.postMessage("close")` when that handler exists — Task 6's Swift coordinator listens for exactly the string `"close"`.

- [ ] **Step 1: Write the bare layout**

Create `src/app/widget/layout.tsx`:

```tsx
import type { Metadata, Viewport } from "next";

// The widget renders inside a native WebView, so it carries none of the site
// chrome — no nav, no footer, no theme switcher.
export const metadata: Metadata = {
  title: "Mille",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  viewportFit: "cover",
};

export default function WidgetLayout({ children }: { children: React.ReactNode }) {
  return <div className="min-h-dvh bg-white dark:bg-zinc-950">{children}</div>;
}
```

- [ ] **Step 2: Write the page**

Create `src/app/widget/mille/page.tsx`:

```tsx
import { cookies } from "next/headers";
import { config } from "@/lib/config";
import { MILLE_WIDGET_COOKIE, widgetJwtIsValid } from "@/lib/mille-widget";
import { MilleWidget } from "@/components/olivia/MilleWidget";

// Reached only via /api/olivia/widget/enter, which sets the cookie this page
// checks. Loading it directly without the cookie shows nothing.
export const dynamic = "force-dynamic";

export default async function MilleWidgetPage() {
  const store = await cookies();
  const ok = await widgetJwtIsValid(
    store.get(MILLE_WIDGET_COOKIE)?.value,
    config.session.secret,
  );
  if (!ok) {
    return (
      <div className="flex min-h-dvh items-center justify-center p-8 text-center">
        <p className="text-sm text-zinc-500">
          This chat isn&apos;t available. Close and reopen it from the app.
        </p>
      </div>
    );
  }
  return <MilleWidget />;
}
```

- [ ] **Step 3: Write the client component**

Create `src/components/olivia/MilleWidget.tsx`:

```tsx
"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// The whole messenger: header, thread, composer, thinking state, retry. It
// lives here rather than in the app so wording and behaviour ship on a deploy
// instead of an app release — the Intercom model.
//
// Send → POST /api/olivia/widget/messages → poll GET until her reply lands.
// The pipe is silent (SELFTEST wamid), so nothing reaches WhatsApp.

type Row = {
  id: number;
  role: string;
  route: string | null;
  text: string;
  created_at: string;
};

const POLL_MS = 2500;
const POLL_MAX_MS = 120_000;

/** WhatsApp-ish rendering: *bold*, newlines, tappable links. */
function renderText(text: string) {
  return text.split("\n").map((line, i) => {
    const parts = line.split(/(\*[^*\n]+\*|https?:\/\/\S+)/g).map((part, j) => {
      if (/^\*[^*\n]+\*$/.test(part)) return <strong key={j}>{part.slice(1, -1)}</strong>;
      if (/^https?:\/\//.test(part)) {
        return (
          <a
            key={j}
            href={part}
            target="_blank"
            rel="noreferrer"
            className="underline decoration-dotted underline-offset-2 break-all"
          >
            {part}
          </a>
        );
      }
      return <span key={j}>{part}</span>;
    });
    return (
      <span key={i}>
        {i > 0 && <br />}
        {parts}
      </span>
    );
  });
}

function timeOf(iso: string) {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  } catch {
    return "";
  }
}

/** Ask the native host to dismiss the sheet; no-op in a plain browser. */
function closeWidget() {
  const host = (window as unknown as {
    webkit?: { messageHandlers?: { mille?: { postMessage: (m: string) => void } } };
  }).webkit;
  host?.messageHandlers?.mille?.postMessage("close");
}

export function MilleWidget() {
  const [rows, setRows] = useState<Row[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFailed, setLastFailed] = useState<string | null>(null);
  const lastIdRef = useRef(0);
  const pollTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollUntilRef = useRef(0);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const mergeRows = useCallback((incoming: Row[]) => {
    if (!incoming.length) return false;
    let sawReply = false;
    setRows((prev) => {
      const known = new Set(prev.map((r) => r.id));
      const fresh = incoming.filter((r) => !known.has(r.id));
      if (!fresh.length) return prev;
      for (const r of fresh) {
        lastIdRef.current = Math.max(lastIdRef.current, r.id);
        if (r.role !== "member") sawReply = true;
      }
      return [...prev, ...fresh].sort((a, b) => a.id - b.id);
    });
    return sawReply;
  }, []);

  const fetchRows = useCallback(
    async (after: number) => {
      const res = await fetch(
        `/api/olivia/widget/messages${after ? `?after=${after}` : ""}`,
      );
      if (!res.ok) throw new Error(`could not load the conversation (${res.status})`);
      const data = (await res.json()) as { rows: Row[] };
      return mergeRows(data.rows);
    },
    [mergeRows],
  );

  useEffect(() => {
    fetchRows(0).catch((e: Error) => setError(e.message));
  }, [fetchRows]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [rows, waiting]);

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) clearTimeout(pollTimerRef.current);
    pollTimerRef.current = null;
    setWaiting(false);
  }, []);

  const pollOnce = useCallback(async () => {
    try {
      const gotReply = await fetchRows(lastIdRef.current);
      if (gotReply) {
        stopPolling();
        return;
      }
      if (Date.now() > pollUntilRef.current) {
        stopPolling();
        setError("Mille didn't answer in time.");
        return;
      }
    } catch {
      // transient — keep polling until the deadline
    }
    pollTimerRef.current = setTimeout(pollOnce, POLL_MS);
  }, [fetchRows, stopPolling]);

  useEffect(() => () => stopPolling(), [stopPolling]);

  const send = useCallback(
    async (textOverride?: string) => {
      const text = (textOverride ?? input).trim();
      if (!text || sending) return;
      setError(null);
      setLastFailed(null);
      setSending(true);
      try {
        const res = await fetch("/api/olivia/widget/messages", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        const data = (await res.json()) as { error?: string };
        if (!res.ok) throw new Error(data.error || `send failed (${res.status})`);
        if (!textOverride) setInput("");
        setWaiting(true);
        pollUntilRef.current = Date.now() + POLL_MAX_MS;
        if (pollTimerRef.current) clearTimeout(pollTimerRef.current);
        pollTimerRef.current = setTimeout(pollOnce, POLL_MS);
      } catch (e) {
        setError(e instanceof Error ? e.message : "send failed");
        setLastFailed(text);
      } finally {
        setSending(false);
      }
    },
    [input, sending, pollOnce],
  );

  return (
    <div className="flex h-dvh flex-col bg-white dark:bg-zinc-950">
      {/* Header */}
      <div className="bg-emerald-700 px-5 pb-5 pt-[calc(env(safe-area-inset-top)+1rem)] text-white">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-2xl font-semibold leading-tight">Hi Andy 👋</p>
            <p className="text-2xl font-semibold leading-tight opacity-90">
              How can I help?
            </p>
          </div>
          <button
            onClick={closeWidget}
            aria-label="Close"
            className="-mr-1 rounded-full bg-white/15 px-3 py-1 text-lg leading-none"
          >
            ×
          </button>
        </div>
        <p className="mt-2 text-sm text-emerald-100">
          Mille — the MDS assistant. Answers take about half a minute.
        </p>
      </div>

      {/* Thread */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {rows.length === 0 && !error && (
          <p className="py-16 text-center text-sm text-zinc-400">Loading…</p>
        )}
        <div className="flex flex-col gap-2">
          {rows.map((r) => {
            const mine = r.role === "member";
            return (
              <div key={r.id} className={"flex " + (mine ? "justify-end" : "justify-start")}>
                <div
                  className={
                    "max-w-[85%] rounded-2xl px-3.5 py-2 text-[15px] leading-relaxed shadow-sm " +
                    (mine
                      ? "rounded-br-sm bg-emerald-600 text-white"
                      : "rounded-bl-sm bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100")
                  }
                >
                  <div className="whitespace-pre-wrap break-words">{renderText(r.text)}</div>
                  <div
                    className={
                      "mt-1 text-[10px] " +
                      (mine ? "text-emerald-100/80" : "text-zinc-400 dark:text-zinc-500")
                    }
                  >
                    {timeOf(r.created_at)}
                  </div>
                </div>
              </div>
            );
          })}
          {waiting && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-sm bg-zinc-100 px-3.5 py-2 text-sm text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500">
                Mille is thinking…
              </div>
            </div>
          )}
        </div>
        <div ref={bottomRef} />
      </div>

      {/* Error + retry */}
      {error && (
        <div className="flex items-center justify-between gap-3 border-t border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          <span>{error}</span>
          {lastFailed && (
            <button
              onClick={() => send(lastFailed)}
              className="rounded-md border border-red-300 px-2 py-1 font-medium dark:border-red-800"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Composer */}
      <div className="flex items-end gap-2 border-t border-zinc-200 p-3 pb-[calc(env(safe-area-inset-bottom)+0.75rem)] dark:border-zinc-800">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          rows={1}
          placeholder="Ask Mille…"
          className="max-h-32 min-h-[42px] flex-1 resize-none rounded-2xl border border-zinc-200 bg-white px-4 py-2.5 text-[15px] text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
        />
        <button
          onClick={() => send()}
          disabled={sending || !input.trim()}
          className="rounded-full bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {sending ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Verify locally in a phone-sized viewport**

With the dev server running, open `http://localhost:3000/api/olivia/widget/enter?k=localtoken` in the browser pane at the mobile preset (375×812). Confirm: header renders, existing turns load, composer sits above the keyboard area, no site nav is visible. Send "what is the MDS Summit venue?" and confirm the thinking state appears and her answer lands.

- [ ] **Step 5: Lint and build**

```bash
cd /Users/Born/mds-digest-web && npx eslint src/app/widget src/components/olivia src/app/api/olivia/widget src/lib/mille-widget.ts && npm run build
```
Expected: no lint errors, build succeeds.

- [ ] **Step 6: Commit**

```bash
cd /Users/Born/mds-digest-web && git add src/app/widget src/components/olivia/MilleWidget.tsx && git commit -m "feat(mille-widget): the in-app panel — header, thread, composer, retry"
```

---

### Task 5: Ship the web side and prove it live

**Files:**
- Modify: none (deploy + verification only)

**Interfaces:**
- Consumes: Tasks 1–4, plus `OLIVIA_WIDGET_TOKEN` on Render (prerequisite).
- Produces: a working `https://digest.mds.co/api/olivia/widget/enter?k=<token>` — the exact URL Task 6 compiles into the app.

- [ ] **Step 1: Push and let Render deploy**

```bash
cd /Users/Born/mds-digest-web && git push origin main
```

- [ ] **Step 2: Confirm the deploy is live**

```bash
curl -s -o /dev/null -w "%{http_code}\n" "https://digest.mds.co/api/olivia/widget/enter?k=wrong"
```
Expected: `401`. A `404` means the deploy has not finished — wait and repeat.

- [ ] **Step 3: Prove the full loop from the command line**

```bash
cd /Users/Born/mds-digest-web && curl -s -c /tmp/mille.jar -o /dev/null "https://digest.mds.co/api/olivia/widget/enter?k=$OLIVIA_WIDGET_TOKEN" && curl -s -b /tmp/mille.jar -X POST https://digest.mds.co/api/olivia/widget/messages -H 'content-type: application/json' -d '{"text":"what time does day one start?"}'
```
Expected: `{"ok":true,"wamid":"wamid.SELFTEST_WIDGET_…"}`. Record the wamid.

Then poll for her answer:
```bash
curl -s -b /tmp/mille.jar https://digest.mds.co/api/olivia/widget/messages | tail -c 600
```
Expected: her reply present as the newest row. Record the round-trip time.

- [ ] **Step 4: Prove nothing reached WhatsApp**

Run against Supabase (MCP `execute_sql`):
```sql
select count(*) as sends
from digest.olivia_sends
where created_at > now() - interval '15 minutes'
  and phone = '17866578153';
```
Expected: `0`. Any row here means the silent branch was bypassed — stop and fix before continuing.

- [ ] **Step 5: Run the leak gate**

```bash
cd /Users/Born/Scorecard && python3 scripts/olivia_leak_gate.py; echo "EXIT=$?"
```
Expected: `GATE PASSED` and `EXIT=0`.

- [ ] **Step 6: Commit the evidence into the spec**

Append a short "Proven live" block to `docs/superpowers/specs/2026-08-20-mille-in-app-widget-design.md` recording: deploy confirmed, the wamid, the round-trip seconds, `olivia_sends` count 0, gate EXIT 0.

```bash
cd /Users/Born/Scorecard && git add docs/superpowers/specs/2026-08-20-mille-in-app-widget-design.md && git commit -m "docs: Mille widget web side proven live (wamid + timing + gate)"
```

---

### Task 6: The iOS app — launcher and WebView sheet

**Files:**
- Create: `MDSKnowledgeBase/Views/MilleWidgetView.swift` (mds-ios-app)
- Modify: `MDSKnowledgeBase/ContentView.swift` (launcher button + sheet)
- Modify: `project.yml` (bump `CFBundleVersion` 73 → 74)

**Interfaces:**
- Consumes: the entry URL from Task 5; the `"close"` message the page posts to `window.webkit.messageHandlers.mille`.
- Produces: `MilleWidgetView(onClose:)` — a SwiftUI view presentable in a `.sheet`.

- [ ] **Step 1: Write the WebView wrapper**

Create `MDSKnowledgeBase/Views/MilleWidgetView.swift`:

```swift
//
//  MilleWidgetView.swift
//
//  POC: Mille lives on the web. The app hosts a WebView and nothing else — no
//  chat models, no networking, no message state. Wording and behaviour ship
//  from digest.mds.co, so changing them needs a deploy, not an app release.
//
//  ⚠️ Single-user test rig, NOT member-facing: the identity behind the widget
//  is hardcoded server-side to Andy's member record, and the token below is a
//  shared secret compiled into the binary — same exposure class as
//  OliviaClient's. Real per-member identity is a separate build.
//

import SwiftUI
import WebKit

enum MilleWidget {
    /// Matches OLIVIA_WIDGET_TOKEN on the digest.mds.co service.
    static let token = "REPLACE_WITH_OLIVIA_WIDGET_TOKEN"

    /// Entry route: validates the token, sets the session cookie, redirects to
    /// the panel. The app never loads the panel URL directly.
    static var entryURL: URL {
        URL(string: "https://digest.mds.co/api/olivia/widget/enter?k=\(token)")!
    }
}

struct MilleWidgetView: UIViewRepresentable {
    let onClose: () -> Void

    func makeCoordinator() -> Coordinator { Coordinator(onClose: onClose) }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default() // the widget cookie survives dismissals
        config.userContentController.add(context.coordinator, name: "mille")

        let web = WKWebView(frame: .zero, configuration: config)
        web.allowsBackForwardNavigationGestures = false
        web.scrollView.keyboardDismissMode = .interactive
        web.load(URLRequest(url: MilleWidget.entryURL))
        return web
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKScriptMessageHandler {
        private let onClose: () -> Void
        init(onClose: @escaping () -> Void) { self.onClose = onClose }

        func userContentController(
            _ userContentController: WKUserContentController,
            didReceive message: WKScriptMessage
        ) {
            guard message.name == "mille", message.body as? String == "close" else { return }
            Task { @MainActor in self.onClose() }
        }
    }
}
```

- [ ] **Step 2: Add the launcher to ContentView**

In `MDSKnowledgeBase/ContentView.swift`, add the state next to the existing `@State private var tab: KBTab = .search`:

```swift
    @State private var showMille = false
```

Then, inside the outer `ZStack(alignment: .bottom)`, immediately **before** the `if !videoPresentation.isFullscreen { GlassTabBar(...) }` block, add the floating launcher:

```swift
            // Mille launcher (POC) — opens the hosted widget over the app.
            if !videoPresentation.isFullscreen {
                HStack {
                    Spacer()
                    Button {
                        showMille = true
                    } label: {
                        Image(systemName: "bubble.left.and.text.bubble.right.fill")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(width: 56, height: 56)
                            .background(Circle().fill(Color.accentColor))
                            .shadow(radius: 8, y: 4)
                    }
                    .accessibilityLabel("Ask Mille")
                    .padding(.trailing, 20)
                }
                .padding(.bottom, kKBTabBarHeight + 12)
                .ignoresSafeArea(.keyboard)
            }
```

And attach the sheet to the outer `ZStack`, next to the existing `.animation(...)` modifiers:

```swift
        .sheet(isPresented: $showMille) {
            MilleWidgetView(onClose: { showMille = false })
                .ignoresSafeArea()
        }
```

- [ ] **Step 3: Paste the real token and bump the build number**

Replace `REPLACE_WITH_OLIVIA_WIDGET_TOKEN` in `MilleWidgetView.swift` with the value Andy generated in the prerequisites. In `project.yml`, change `CFBundleVersion: "73"` to `CFBundleVersion: "74"`.

- [ ] **Step 4: Regenerate the project and build**

```bash
cd /Users/Born/mds-ios-app && xcodegen && xcodebuild -project MDSKnowledgeBase.xcodeproj -scheme MDSKnowledgeBase -destination 'platform=iOS Simulator,name=iPhone 16' -configuration Debug build 2>&1 | tail -5
```
Expected: `** BUILD SUCCEEDED **`.

- [ ] **Step 5: Run it and prove the loop on the simulator**

Attach the live panel first, then launch the built app (`mcp__Claude_Code_iOS_Simulator__control`: `attach`, then `launch` with the built `.app` path). Then, headlessly:
1. Screenshot the launcher button.
2. Tap it — screenshot the sheet: header, existing history, composer.
3. Type "who should I meet at the Summit?" and send — screenshot the thinking state.
4. Wait for the answer — screenshot her reply in the panel.
5. Tap the × — screenshot to confirm the sheet dismissed back to the app.

Every one of those five is a required acceptance criterion; a missing screenshot means the step is unproven.

- [ ] **Step 6: Commit**

```bash
cd /Users/Born/mds-ios-app && git add MDSKnowledgeBase/Views/MilleWidgetView.swift MDSKnowledgeBase/ContentView.swift project.yml && git commit -m "feat: Mille in-app widget POC — launcher + hosted panel in a WebView sheet"
```

---

### Task 7: Board, logs and handoff

**Files:**
- Modify: `OLIVIA_SPRINT_4.md` (Scorecard) — file **#100 · Mille in the mobile app (POC)** and close it with evidence
- Modify: `SESSION_LOG_OLIVIA.md`, `SESSION_LOG.md` (Scorecard)
- Modify: `OLIVIA_NEXT_SESSION.md` (Scorecard)

**Interfaces:**
- Consumes: the evidence recorded in Tasks 5 and 6.
- Produces: the sprint board's record of this work, in the house close format.

- [ ] **Step 1: File and close #100 on the board**

Add to `OLIVIA_SPRINT_4.md` — a row in the At-a-glance table and a ticket block carrying: the story (*"As a member, I tap one button in the MDS app and ask Mille without leaving it"*), the ACs from the spec §6, and a close block with results, an AC checklist marked met/not, and before/after numbers (before: Mille reachable only over WhatsApp or the admin page; after: reachable in-app, round-trip Xs measured).

- [ ] **Step 2: Write the session log entries**

Prepend the full dated entry to `SESSION_LOG_OLIVIA.md` (what shipped — commit hashes in both repos; what was verified — wamid, `olivia_sends` count 0, gate EXIT 0, simulator screenshots; what is next — Flutter needs only the URL) and one index line to `SESSION_LOG.md`.

- [ ] **Step 3: Refresh the handoff**

Update `OLIVIA_NEXT_SESSION.md`: the widget is live at the entry URL, the token lives in Render env and the Swift binary, POC identity is Andy's, and the next step for the Flutter app is the same URL in a WebView once the dev hands over the repo.

- [ ] **Step 4: Commit**

```bash
cd /Users/Born/Scorecard && git add OLIVIA_SPRINT_4.md SESSION_LOG_OLIVIA.md SESSION_LOG.md OLIVIA_NEXT_SESSION.md && git commit -m "#100 closed: Mille in-app widget POC proven in the iOS app"
```

---

## Self-review

**Spec coverage:** §3 architecture → Tasks 1–4 · §4 auth → Tasks 1–2 · §5 latency and errors → Task 4 (thinking state, retry, 120s poll ceiling) · §6 acceptance → Task 5 (silent-pipe proof, gate) and Task 6 (in-app sheet, history, answer, dismissal) · §7 out-of-scope items appear in no task · §8 traps → Global Constraints.

**Placeholders:** none. The one literal placeholder, `REPLACE_WITH_OLIVIA_WIDGET_TOKEN`, is replaced in Task 6 Step 3 from the value Andy generates in the prerequisites.

**Type consistency:** `WidgetRow` (Task 3) matches the `Row` type the component reads (Task 4) field for field. `MILLE_WIDGET_COOKIE`, `widgetTokenMatches`, `issueWidgetJwt`, `widgetJwtIsValid` keep the same names across Tasks 1–4. The `"close"` string posted by `closeWidget()` (Task 4) is the exact string the Swift coordinator matches (Task 6).
