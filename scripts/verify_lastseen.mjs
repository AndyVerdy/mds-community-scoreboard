#!/usr/bin/env node
// Spot-check: compare Airtable "Intercom Last Seen" vs Intercom's live last_seen for a few members.
import fs from 'node:fs';
const INTERCOM = fs.readFileSync('.intercom_token', 'utf8').trim();
const PAT = fs.readFileSync('.airtable_pat', 'utf8').trim();
const BASE = 'appou5JVr0WIrioWS', TABLE = 'tblfwOSROSHfuYUxv';

// 1) grab 8 members that have a stored Intercom Last Seen
const q = new URLSearchParams({ filterByFormula: "NOT({Intercom Last Seen}='')", pageSize: '8' });
q.append('fields[]', 'Full Name'); q.append('fields[]', 'Preferred Email'); q.append('fields[]', 'Intercom Last Seen');
const at = await (await fetch(`https://api.airtable.com/v0/${BASE}/${TABLE}?${q}`, { headers: { Authorization: `Bearer ${PAT}` } })).json();
const rows = at.records.map(r => ({
  name: r.fields['Full Name'] || '?',
  email: String(r.fields['Preferred Email'] || '').trim().toLowerCase(),
  stored: r.fields['Intercom Last Seen'] || '(none)',
}));

// 2) ask Intercom for those exact emails (one IN query)
const emails = rows.map(r => r.email).filter(Boolean);
const ic = await (await fetch('https://api.intercom.io/contacts/search', {
  method: 'POST',
  headers: { Authorization: `Bearer ${INTERCOM}`, 'Content-Type': 'application/json', 'Intercom-Version': '2.14' },
  body: JSON.stringify({ query: { field: 'email', operator: 'IN', value: emails }, pagination: { per_page: 50 } }),
})).json();
const live = {};
for (const c of (ic.data || [])) {
  if (c.email && c.last_seen_at != null) { const e = c.email.toLowerCase(); if (!(e in live) || c.last_seen_at > live[e]) live[e] = c.last_seen_at; }
}

// 3) side-by-side
console.log('NAME'.padEnd(22) + '| AIRTABLE (stored)'.padEnd(27) + '| INTERCOM (live now)'.padEnd(27) + '| MATCH');
console.log('-'.repeat(92));
let ok = 0;
for (const r of rows) {
  const ts = live[r.email];
  const liveIso = ts != null ? new Date(ts * 1000).toISOString() : '(no last_seen)';
  const match = liveIso === r.stored ? '✅' : '⚠️';
  if (liveIso === r.stored) ok++;
  console.log(`${r.name.slice(0, 21).padEnd(22)}| ${r.stored.padEnd(25)}| ${liveIso.padEnd(25)}| ${match}`);
}
console.log('-'.repeat(92));
console.log(`${ok}/${rows.length} match exactly. (⚠️ = member was active since the last sync — expected; the daily run will refresh it.)`);
