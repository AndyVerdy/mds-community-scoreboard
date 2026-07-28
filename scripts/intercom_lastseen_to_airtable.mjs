#!/usr/bin/env node
// Sync Intercom "last seen online" -> Airtable Members.Intercom Last Seen
// Scope: ONLY Members with "AT Database Status" not empty. Match: email.
//
//   node scripts/intercom_lastseen_to_airtable.mjs --dry-run   read-only, report
//   node scripts/intercom_lastseen_to_airtable.mjs --canary     write 1 record, verify
//   node scripts/intercom_lastseen_to_airtable.mjs              full daily sync

import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const INTERCOM = fs.readFileSync(path.join(ROOT, '.intercom_token'), 'utf8').trim();
const PAT = fs.readFileSync(path.join(ROOT, '.airtable_pat'), 'utf8').trim();

const BASE_ID = 'appou5JVr0WIrioWS';
const TABLE_ID = 'tblfwOSROSHfuYUxv';
const FIELD = 'Intercom Last Seen';
const STATUS_FIELD = 'AT Database Status';
const EMAIL_FIELD = 'Preferred Email';

const DRY = process.argv.includes('--dry-run');
const CANARY = process.argv.includes('--canary');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const IC = { Authorization: `Bearer ${INTERCOM}`, Accept: 'application/json', 'Content-Type': 'application/json', 'Intercom-Version': '2.14' };
const AT = { Authorization: `Bearer ${PAT}`, 'Content-Type': 'application/json' };

async function icGet(p) {
  for (let a = 0; a < 6; a++) {
    const res = await fetch('https://api.intercom.io' + p, { headers: IC });
    if (res.status === 429) { await sleep(2000); continue; }
    return res.json();
  }
  throw new Error('intercom retries exhausted');
}

// 1. Intercom: email -> last_seen_at (unix seconds), keep most recent
async function intercomLastSeen() {
  const map = new Map();
  let after = null, page = 0, withSeen = 0;
  do {
    const q = new URLSearchParams({ per_page: '150' });
    if (after) q.set('starting_after', after);
    const j = await icGet(`/contacts?${q}`);
    for (const c of j.data || []) {
      if (!c.email || c.last_seen_at == null) continue;
      const e = String(c.email).toLowerCase();
      if (!map.has(e) || c.last_seen_at > map.get(e)) map.set(e, c.last_seen_at);
      withSeen++;
    }
    const nx = j.pages && j.pages.next;
    after = !nx ? null : (typeof nx === 'string' ? new URL(nx).searchParams.get('starting_after') : nx.starting_after);
    if (++page % 15 === 0) console.log(`  …intercom ${page} pages`);
  } while (after);
  console.log(`  intercom: ${map.size} emails with last_seen (${withSeen} contacts scanned)`);
  return map;
}

// 2. Airtable: members with status not empty -> [{id, email}]
async function airtableMembers() {
  const out = [];
  let offset = null;
  do {
    const q = new URLSearchParams({ filterByFormula: `NOT({${STATUS_FIELD}}='')`, pageSize: '100' });
    q.append('fields[]', EMAIL_FIELD);
    if (offset) q.set('offset', offset);
    const res = await fetch(`https://api.airtable.com/v0/${BASE_ID}/${TABLE_ID}?${q}`, { headers: AT });
    if (res.status === 429) { await sleep(1000); continue; }
    const j = await res.json();
    if (!j.records) throw new Error('airtable read failed: ' + JSON.stringify(j).slice(0, 200));
    for (const r of j.records) out.push({ id: r.id, email: (r.fields[EMAIL_FIELD] || '').trim().toLowerCase() });
    offset = j.offset;
    await sleep(220); // ≤5 req/s
  } while (offset);
  return out;
}

async function patchBatch(records) {
  const res = await fetch(`https://api.airtable.com/v0/${BASE_ID}/${TABLE_ID}`, {
    method: 'PATCH', headers: AT, body: JSON.stringify({ records }),
  });
  const j = await res.json();
  if (!res.ok) throw new Error(`airtable patch ${res.status}: ${JSON.stringify(j).slice(0, 200)}`);
  return j.records.length;
}

async function main() {
  console.log(`Mode: ${DRY ? 'DRY-RUN' : CANARY ? 'CANARY' : 'FULL'}`);
  console.log('Building Intercom last-seen map…');
  const seen = await intercomLastSeen();
  console.log('Reading Airtable members (status not empty)…');
  const members = await airtableMembers();
  console.log(`  members in scope: ${members.length}`);

  const updates = [];
  let noEmail = 0, noMatch = 0;
  for (const m of members) {
    if (!m.email) { noEmail++; continue; }
    const ts = seen.get(m.email);
    if (ts == null) { noMatch++; continue; }
    updates.push({ id: m.id, fields: { [FIELD]: new Date(ts * 1000).toISOString() } });
  }
  console.log(`Matched ${updates.length} | no email ${noEmail} | no Intercom last-seen ${noMatch}`);

  if (DRY) {
    console.log('Sample:', updates.slice(0, 3).map((u) => `${u.id} -> ${u.fields[FIELD]}`));
    console.log('DRY-RUN: no writes.'); return;
  }

  const todo = CANARY ? updates.slice(0, 1) : updates;
  console.log(`Writing ${todo.length} records…`);
  let done = 0;
  for (let i = 0; i < todo.length; i += 10) {
    done += await patchBatch(todo.slice(i, i + 10));
    if (done % 200 === 0 || CANARY) console.log(`  …${done} written`);
    await sleep(220); // ≤5 req/s
  }
  console.log(`Done. ${done} records updated with ${FIELD}.`);
  if (CANARY) console.log('Canary record:', todo[0].id, '->', todo[0].fields[FIELD]);
}

main().catch((e) => { console.error('FATAL:', e.message); process.exit(1); });
