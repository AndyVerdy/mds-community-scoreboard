#!/usr/bin/env node
// v2 — AT-driven: start from the members we care about, ask Intercom about ONLY them
// (email IN batches), write back only CHANGED last-seen. Fast + targeted.
//   --dry-run  : read + match only, no writes
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const INTERCOM = fs.readFileSync(path.join(ROOT, '.intercom_token'), 'utf8').trim();
const PAT = fs.readFileSync(path.join(ROOT, '.airtable_pat'), 'utf8').trim();
const DRY = process.argv.includes('--dry-run');

const BASE_ID = 'appou5JVr0WIrioWS', TABLE_ID = 'tblfwOSROSHfuYUxv';
const FIELD = 'Intercom Last Seen', STATUS_FIELD = 'AT Database Status', EMAIL_FIELD = 'Preferred Email';
const IC = { Authorization: `Bearer ${INTERCOM}`, Accept: 'application/json', 'Content-Type': 'application/json', 'Intercom-Version': '2.14' };
const AT = { Authorization: `Bearer ${PAT}` };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function j(method, url, headers, body) {
  for (let a = 0; a < 6; a++) {
    const res = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined });
    if (res.status === 429) { await sleep(1500); continue; }
    const t = await res.text(); let d; try { d = t ? JSON.parse(t) : {}; } catch { d = { raw: t }; }
    if (!res.ok) throw new Error(`${method} ${url.slice(0, 60)} -> ${res.status}: ${JSON.stringify(d).slice(0, 160)}`);
    return d;
  }
  throw new Error('retries exhausted');
}

const t0 = Date.now();

// 1) members we care about
const members = [];
let offset = null;
do {
  const p = new URLSearchParams({ filterByFormula: `NOT({${STATUS_FIELD}}='')`, pageSize: '100' });
  p.append('fields[]', EMAIL_FIELD); p.append('fields[]', FIELD);
  if (offset) p.set('offset', offset);
  const d = await j('GET', `https://api.airtable.com/v0/${BASE_ID}/${TABLE_ID}?${p}`, AT);
  for (const r of d.records || []) {
    const f = r.fields || {};
    const email = String(f[EMAIL_FIELD] || '').trim().toLowerCase();
    if (email) members.push({ id: r.id, email, current: f[FIELD] || null });
  }
  offset = d.offset;
} while (offset);
console.log(`members (status not empty, with email): ${members.length}`);

// 2) targeted Intercom lookup: email IN chunks
const seen = {};
const emails = [...new Set(members.map((m) => m.email))];
const chunks = [];
for (let i = 0; i < emails.length; i += 15) chunks.push(emails.slice(i, i + 15));
let searches = 0;
async function doChunk(chunk) {
  let after = null;
  do {
    const body = { query: { field: 'email', operator: 'IN', value: chunk }, pagination: { per_page: 150 } };
    if (after) body.pagination.starting_after = after;
    const d = await j('POST', 'https://api.intercom.io/contacts/search', IC, body);
    searches++;
    for (const c of d.data || []) {
      if (!c.email || c.last_seen_at == null) continue;
      const e = String(c.email).toLowerCase();
      if (!(e in seen) || c.last_seen_at > seen[e]) seen[e] = c.last_seen_at;
    }
    after = (d.pages && d.pages.next && d.pages.next.starting_after) || null;
  } while (after);
}
let ci = 0;
await Promise.all(Array.from({ length: 6 }, async () => {
  while (ci < chunks.length) await doChunk(chunks[ci++]);
}));
console.log(`intercom searches: ${searches} | members found with last_seen: ${Object.keys(seen).length}`);

// 3) diff
const updates = [];
for (const m of members) {
  const ts = seen[m.email];
  if (ts == null) continue;
  const iso = new Date(ts * 1000).toISOString();
  if (iso !== m.current) updates.push({ id: m.id, fields: { [FIELD]: iso } });
}
console.log(`changed (need write): ${updates.length}`);
console.log(`elapsed so far: ${((Date.now() - t0) / 1000).toFixed(1)}s`);

if (DRY) { console.log('DRY-RUN: no writes.'); process.exit(0); }

let written = 0;
for (let i = 0; i < updates.length; i += 10) {
  await j('PATCH', `https://api.airtable.com/v0/${BASE_ID}/${TABLE_ID}`, { ...AT, 'Content-Type': 'application/json' }, { records: updates.slice(i, i + 10) });
  written += Math.min(10, updates.length - i);
  await sleep(120);
}
console.log(`written: ${written} | total elapsed: ${((Date.now() - t0) / 1000).toFixed(1)}s`);
