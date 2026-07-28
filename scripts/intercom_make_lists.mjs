#!/usr/bin/env node
// Convert the two imported attributes from plain string -> List (predefined options),
// so Intercom shows a value picker instead of a free-text box. Data on contacts is untouched.

import fs from 'node:fs';
import path from 'node:path';

const TOKEN = fs.readFileSync(path.join(process.cwd(), '.intercom_token'), 'utf8').trim();
const BASE = 'https://api.intercom.io';
const H = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'Intercom-Version': '2.14',
};

const RAW_OPTIONS = [
  'Pending - Unpaid Application', 'Pending Application', 'Pending 1st Interview', 'Pending 2nd Interview',
  'Pending Membership Payment (Invoice)', 'Pending Group Entrance', 'New Member', 'Current Member',
  'Removed Applicant', 'Declined Applicant', 'Removed - For Cause', 'Removed - Canceled Membership',
  'Removed - Replaced with other Member', 'Staff', 'Dead Lead', 'Team User',
  'Current Member- Soft Removed', 'Current Member- Not Renewing', 'Current Member- Paused',
];
const STAGE_OPTIONS = ['Current Member', 'Not a Member'];

const TARGETS = { 'AT Database Status': RAW_OPTIONS, 'Membership Stage': STAGE_OPTIONS };

async function api(method, p, body) {
  const res = await fetch(BASE + p, { method, headers: H, body: body ? JSON.stringify(body) : undefined });
  const text = await res.text();
  let json; try { json = text ? JSON.parse(text) : {}; } catch { json = { raw: text }; }
  return { status: res.status, json };
}

const { json: list } = await api('GET', '/data_attributes?model=contact');
const attrs = list.data || [];

for (const [name, options] of Object.entries(TARGETS)) {
  const a = attrs.find((x) => x.name === name);
  if (!a) { console.log(`✗ "${name}" not found`); continue; }
  // Try options as [{value}], then as [strings]
  let done = false;
  for (const opts of [options.map((v) => ({ value: v })), options]) {
    const { status, json } = await api('PUT', `/data_attributes/${a.id}`, { options: opts });
    if (status >= 200 && status < 300) {
      console.log(`✓ "${name}" -> List with ${json.options ? json.options.length : options.length} options`);
      done = true; break;
    } else {
      console.log(`  …format attempt failed (${status}): ${JSON.stringify(json).slice(0, 140)}`);
    }
  }
  if (!done) console.log(`✗ "${name}" could not be converted`);
}

// Verify
const { json: after } = await api('GET', '/data_attributes?model=contact');
for (const name of Object.keys(TARGETS)) {
  const a = (after.data || []).find((x) => x.name === name);
  console.log(`verify "${name}": data_type=${a?.data_type}, options=${a?.options ? a.options.length : 0}`);
}
