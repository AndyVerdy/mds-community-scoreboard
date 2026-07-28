#!/usr/bin/env node
// Backfill Airtable "AT Database Status" -> Intercom custom attributes.
//
//   node scripts/intercom_import_status.mjs --dry-run   reads only; coverage + report, no writes
//   node scripts/intercom_import_status.mjs --canary     create attrs + update ONLY Ward Gahan
//   node scripts/intercom_import_status.mjs              full live run
//
// Reads token from ./.intercom_token, rows from ./tmp/at_status_export.json,
// writes ./tmp/intercom_import_report.csv.

import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const TOKEN = fs.readFileSync(path.join(ROOT, '.intercom_token'), 'utf8').trim();
const ROWS = JSON.parse(fs.readFileSync(path.join(ROOT, 'tmp/at_status_export.json'), 'utf8'));
const REPORT = path.join(ROOT, 'tmp/intercom_import_report.csv');

const DRY = process.argv.includes('--dry-run');
const CANARY = process.argv.includes('--canary');
const CANARY_ID = '646d738c130750a7bca854e2'; // Ward Gahan

const BASE = 'https://api.intercom.io';
const HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'Intercom-Version': '2.14',
};

const RAW_ATTR = 'AT Database Status';
const STAGE_ATTR = 'Membership Stage';
// Andy's definition: only these three count as a current member.
const CURRENT = new Set(['New Member', 'Current Member', 'Pending Group Entrance']);
const stageFor = (s) => (CURRENT.has(s) ? 'Current Member' : 'Not a Member');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(method, p, body) {
  for (let attempt = 0; attempt < 6; attempt++) {
    let res;
    try {
      res = await fetch(BASE + p, { method, headers: HEADERS, body: body ? JSON.stringify(body) : undefined });
    } catch (e) {
      await sleep(1000 * (attempt + 1)); continue;
    }
    if (res.status === 429) { // rate limited
      const wait = (Number(res.headers.get('retry-after')) || 2) * 1000;
      await sleep(wait); continue;
    }
    const text = await res.text();
    let json; try { json = text ? JSON.parse(text) : {}; } catch { json = { raw: text }; }
    return { status: res.status, json };
  }
  return { status: 0, json: { error: 'max retries' } };
}

async function ensureAttribute(name) {
  const { status, json } = await api('POST', '/data_attributes', { name, model: 'contact', data_type: 'string' });
  if (status >= 200 && status < 300) return 'created';
  const msg = JSON.stringify(json).toLowerCase();
  if (msg.includes('already') || msg.includes('exist')) return 'already exists';
  return `FAILED (${status}): ${JSON.stringify(json).slice(0, 160)}`;
}

function cursorFrom(pages) {
  const next = pages && pages.next;
  if (!next) return null;
  if (typeof next === 'string') { try { return new URL(next).searchParams.get('starting_after'); } catch { return null; } }
  return next.starting_after || null;
}

async function buildIndex() {
  const byId = new Set();
  const byExternalId = new Map();   // external_id -> id
  const byEmail = new Map();         // email(lower) -> [ids]
  let after = null, page = 0;
  do {
    const q = new URLSearchParams({ per_page: '150' });
    if (after) q.set('starting_after', after);
    const { status, json } = await api('GET', `/contacts?${q.toString()}`);
    if (status !== 200) throw new Error(`list contacts failed ${status}: ${JSON.stringify(json).slice(0, 200)}`);
    for (const c of json.data || []) {
      byId.add(c.id);
      if (c.external_id) byExternalId.set(String(c.external_id), c.id);
      if (c.email) {
        const e = String(c.email).toLowerCase();
        (byEmail.get(e) || byEmail.set(e, []).get(e)).push(c.id);
      }
    }
    after = cursorFrom(json.pages);
    if (++page % 10 === 0) console.log(`  …indexed ${page} pages (${byId.size} contacts)`);
  } while (after);
  return { byId, byExternalId, byEmail };
}

function matchRow(r, idx) {
  if (r.intercomUserId && idx.byId.has(String(r.intercomUserId))) return { ids: [String(r.intercomUserId)], by: 'intercom_id' };
  if (r.waUserId != null && idx.byExternalId.has(String(r.waUserId))) return { ids: [idx.byExternalId.get(String(r.waUserId))], by: 'external_id' };
  if (r.email && idx.byEmail.has(r.email)) return { ids: idx.byEmail.get(r.email), by: 'email' };
  return { ids: [], by: 'unmatched' };
}

const updateContact = (id, raw, stage) =>
  api('PUT', `/contacts/${id}`, { custom_attributes: { [RAW_ATTR]: raw, [STAGE_ATTR]: stage } });

const esc = (s) => `"${String(s ?? '').replace(/"/g, '""')}"`;
const HEADER = ['recordId', 'name', 'email', 'status', 'stage', 'matchedBy', 'intercomIds', 'result'];

async function main() {
  console.log(`Mode: ${DRY ? 'DRY-RUN' : CANARY ? 'CANARY' : 'FULL'} | rows: ${ROWS.length}`);
  if (typeof fetch !== 'function') throw new Error('Node 18+ required (global fetch missing)');

  // Attributes (writes) — skip in dry-run
  if (!DRY) {
    console.log('Ensuring attributes…');
    console.log(`  ${RAW_ATTR}: ${await ensureAttribute(RAW_ATTR)}`);
    console.log(`  ${STAGE_ATTR}: ${await ensureAttribute(STAGE_ATTR)}`);
  }

  // Canary: write only Ward, directly (fast), then stop.
  if (CANARY) {
    const row = ROWS.find((r) => String(r.intercomUserId) === CANARY_ID) || { status: 'Current Member', name: 'Ward Gahan' };
    const stage = stageFor(row.status);
    const { status, json } = await updateContact(CANARY_ID, row.status, stage);
    console.log(`Canary update ${CANARY_ID} -> "${row.status}" / "${stage}": HTTP ${status}`);
    if (status >= 400) console.log('  body:', JSON.stringify(json).slice(0, 300));
    console.log(status < 300 ? 'CANARY OK — write scope confirmed.' : 'CANARY FAILED — check scope/body above.');
    return;
  }

  // Build index for matching
  console.log('Building Intercom contact index…');
  const idx = await buildIndex();
  console.log(`  indexed: ${idx.byId.size} ids, ${idx.byExternalId.size} external_ids, ${idx.byEmail.size} emails`);

  const rows = ROWS.map((r) => ({ ...r, stage: stageFor(r.status), match: matchRow(r, idx) }));
  const matched = rows.filter((r) => r.match.ids.length);
  const unmatched = rows.filter((r) => !r.match.ids.length);
  const byKey = {}; for (const r of matched) byKey[r.match.by] = (byKey[r.match.by] || 0) + 1;
  const stageDist = {}; for (const r of rows) stageDist[r.stage] = (stageDist[r.stage] || 0) + 1;
  console.log('Match coverage:', { matched: matched.length, unmatched: unmatched.length, byKey });
  console.log('Stage distribution:', stageDist);

  const lines = [HEADER.join(',')];

  if (DRY) {
    for (const r of rows) lines.push([r.recordId, r.name, r.email, r.status, r.stage, r.match.by, r.match.ids.join('|'), '(dry-run)'].map(esc).join(','));
    fs.writeFileSync(REPORT, lines.join('\n'));
    console.log(`DRY-RUN complete. No writes. Report: ${REPORT}`);
    return;
  }

  console.log(`Updating ${matched.length} records (${matched.reduce((n, r) => n + r.match.ids.length, 0)} contacts)…`);
  let ok = 0, fail = 0, n = 0;
  for (const r of matched) {
    for (const id of r.match.ids) {
      const { status, json } = await updateContact(id, r.status, r.stage);
      const good = status >= 200 && status < 300;
      good ? ok++ : fail++;
      lines.push([r.recordId, r.name, r.email, r.status, r.stage, r.match.by, id, good ? 'updated' : `ERR ${status}: ${JSON.stringify(json).slice(0, 100)}`].map(esc).join(','));
      if (++n % 100 === 0) console.log(`  …${n} writes (${ok} ok, ${fail} fail)`);
      await sleep(110); // ~9/s
    }
  }
  for (const r of unmatched) lines.push([r.recordId, r.name, r.email, r.status, r.stage, 'unmatched', '', '(no intercom contact)'].map(esc).join(','));
  fs.writeFileSync(REPORT, lines.join('\n'));
  console.log(`Done. ${ok} updated, ${fail} failed, ${unmatched.length} unmatched. Report: ${REPORT}`);
}

main().catch((e) => { console.error('FATAL:', e.message); process.exit(1); });
