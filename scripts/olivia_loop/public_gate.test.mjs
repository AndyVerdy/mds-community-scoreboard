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

test('a public row containing a longer name does not back a shorter name inside it', () => {
  const shortLongNames = [{ name: 'Anna Lee', kind: 'member' }, { name: 'Arianna Leeman', kind: 'member' }];
  const rows = [{ source: 'fb', source_id: 's1', url: 'https://example.com/p1', text: 'Arianna Leeman posted a great tip today' }];
  const classes = { 'https://example.com/p1': 'public' };
  const backed = pg.backedNames(rows, classes, shortLongNames);
  assert.ok(backed.has('Arianna Leeman'));
  assert.ok(!backed.has('Anna Lee'));
});

test('the first-name pass leaves an unrelated capitalised word alone', () => {
  const r = pg.redact('Will Turner joined the call. Will this feature ship soon?', [{ name: 'Will Turner', kind: 'member' }], new Set());
  assert.ok(pg.ROLE_PHRASES.some(p => r.text.startsWith(p)));
  assert.ok(r.text.includes('Will this feature ship soon?'));
  assert.ok(!r.text.includes('Turner'));
});

// --- fix round 2 (#169): every real tool_result appends a plain-text coverage note after the JSON
// array, so a bare JSON.parse() throws "Extra data" and every row was being thrown away. ---

function toolResult(content) {
  return [{ role: 'user', content: [{ type: 'tool_result', content }] }];
}

test('a tool result with a trailing note still yields its rows', () => {
  const raw = JSON.stringify([
    { source: 'wa_message', source_id: 'O.yyUJPiRYBSWQ', body: 'Jonathan Jewett shared a bundling tip' },
    { source: 'wa_message', source_id: 'OtcoR4suDFb47w', body: 'a reply' },
  ]) + '\n\nNOTE: coverage ends 2026-09-05';
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.equal(ev.rows.length, 2);
  assert.deepEqual(ev.rows.map(r => r.source), ['wa_message', 'wa_message']);
  assert.deepEqual(ev.source_ids.sort(), ['O.yyUJPiRYBSWQ', 'OtcoR4suDFb47w'].sort());
});

test('an app.mds.co video link yields its video id as a source id', () => {
  const raw = JSON.stringify([
    { video_url: 'https://app.mds.co/videos/6a97599308e2e42a631c1a35', title: 'TikTok Shop panel' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.ok(ev.source_ids.includes('6a97599308e2e42a631c1a35'));
});

test('event_url is collected as a url', () => {
  const raw = JSON.stringify([{ source: 'event', event_url: 'https://app.mds.co/events/summit-sg' }]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.ok(ev.urls.includes('https://app.mds.co/events/summit-sg'));
  assert.equal(ev.rows[0].url, 'https://app.mds.co/events/summit-sg');
});

test('garbage falls back to one text row', () => {
  const ev = pg.extractEvidenceRows(toolResult('no rows at all, just prose about the Summit'));
  assert.equal(ev.rows.length, 1);
  assert.equal(ev.rows[0].source, 'text');
  assert.deepEqual(ev.urls, []);
  assert.deepEqual(ev.source_ids, []);
});
