import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const pg = require('./public_gate.js');

const names = [{ name: 'Jonathan Jewett', kind: 'member' }, { name: 'Bryce Alderson', kind: 'member' }];
const messages = [
  { role: 'assistant', content: [{ type: 'tool_use', name: 'content_search_v2' }] },
  { role: 'user', content: [{ type: 'tool_result', content: JSON.stringify([
      { source: 'fb', source_id: 'p1', url: 'https://www.facebook.com/groups/699138040189700/posts/1', body: 'Jonathan Jewett shared a TikTok tip' },
      { source: 'event', source_id: 'e1', url: 'https://www.mds.co/summit', body: 'Bryce Alderson speaks at the Summit' },
  ]) }] },
];

test('extractEvidenceRows keeps every row and collects keys', () => {
  const ev = pg.extractEvidenceRows(messages);
  assert.equal(ev.rows.length, 2);
  assert.deepEqual(ev.urls.sort(), ['https://www.facebook.com/groups/699138040189700/posts/1', 'https://www.mds.co/summit']);
  assert.deepEqual(ev.source_ids.sort(), ['e1', 'p1']);
});

test('a name is backed only by a PUBLIC row that contains it', () => {
  const ev = pg.extractEvidenceRows(messages);
  const classes = { 'https://www.facebook.com/groups/699138040189700/posts/1': 'closed', 'https://www.mds.co/summit': 'public' };
  const backed = pg.backedNames(ev.rows, classes, names);
  assert.ok(backed.has('Bryce Alderson'));
  assert.ok(!backed.has('Jonathan Jewett'));
});

test('redact replaces every occurrence of an unbacked name and keeps backed ones', () => {
  const backed = new Set(['Bryce Alderson']);
  const r = pg.redact('Jonathan Jewett said X. Bryce Alderson said Y. Jonathan Jewett again.', names, backed);
  assert.ok(!r.text.includes('Jonathan'));
  assert.ok(r.text.includes('Bryce Alderson'));
  assert.deepEqual(r.removed, ['Jonathan Jewett']);
  assert.match(r.text, /^a member said X/);
});

test('redact also catches first-name-only mentions after a full-name hit', () => {
  const r = pg.redact('Jonathan Jewett said X. Later Jonathan added Y.', names, new Set());
  assert.ok(!/Jonathan/.test(r.text));
});

test('leftoverNames finds an unbacked name the smoother reintroduced', () => {
  assert.deepEqual(pg.leftoverNames('Thanks to Jonathan Jewett.', names, new Set()), ['Jonathan Jewett']);
  assert.deepEqual(pg.leftoverNames('Thanks to a member.', names, new Set()), []);
});

test('an unknown row class counts as closed', () => {
  const ev = pg.extractEvidenceRows(messages);
  const backed = pg.backedNames(ev.rows, {}, names);
  assert.equal(backed.size, 0);
});
