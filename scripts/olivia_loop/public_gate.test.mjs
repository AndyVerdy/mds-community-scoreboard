// Unit tests for the deterministic half of the Public Gate (#169). `node --test public_gate.test.mjs`
// — the leak gate runs this same file, so a case pinned here is pinned on every ship.
//
// ORGANISATION ROWS ARE THE RPC'S JOB, NOT THE MODULE'S (#169 review I3). The module masks whatever
// the name index hands it, by design — there is no NEVER_MASK list here and no test for one. The
// organisation rows that used to turn "the MDS community" into "the a member" (MDS Community, MDS
// Partners, MDS Programs, MDS Member, MDS Chapters, MDS Test, Systems MDS, Andy MDS) are excluded at
// the source by digest.public_gate_name_index(): scripts/sql/20260908_public_gate_name_index_orgs_169.sql
// (mirrored in db/functions/public_gate_name_index.sql). One guard, in one place, deliberately.
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

// --- fix round 4 (#169): a partner row classifies 'public' (the directory), but it embeds
// reviews_sample (MEMBER reviews) and strength_note/fit_reason (member-judgment text) that are not
// the partner's own public website. Only name/web_summary/web_people/web_pricing are actually
// world-public (crawled from the partner's own site) — those alone may back a name. ---

test("a member named only in a partner's reviews_sample is NOT backed by that public partner row", () => {
  const raw = JSON.stringify([
    { name: 'Prosperlytics Consultants', partner_url: 'https://app.mds.co/partners/p1',
      reviews_sample: [{ author: 'Jonathan Jewett', text: 'great' }] },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { 'https://app.mds.co/partners/p1': 'public' };
  const backed = pg.backedNames(ev.rows, classes, names);
  assert.ok(!backed.has('Jonathan Jewett'));
});

test('a founder named in web_people IS backed', () => {
  const raw = JSON.stringify([
    { name: 'Finaloop', partner_url: 'https://app.mds.co/partners/p2',
      web_people: [{ name: 'Mudit Jain', role: 'Founder' }] },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { 'https://app.mds.co/partners/p2': 'public' };
  const backed = pg.backedNames(ev.rows, classes, [{ name: 'Mudit Jain', kind: 'partner_staff' }]);
  assert.ok(backed.has('Mudit Jain'));
});

test('a non-partner public row still backs a name found anywhere in it', () => {
  const raw = JSON.stringify([
    { source: 'event', public_page_url: 'https://www.mds.co/summit', body: 'Bryce Alderson speaks at the Summit' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { 'https://www.mds.co/summit': 'public' };
  const backed = pg.backedNames(ev.rows, classes, names);
  assert.ok(backed.has('Bryce Alderson'));
});

// --- review C1 (#169): JS `\b` is ASCII-only, so a name whose FIRST or LAST character is accented
// had no word boundary at that end and never matched — 33 live index rows were published verbatim
// and leftoverNames() did not refuse either (the gate failed OPEN). ---

const accented = [{ name: 'Émile Dupont', kind: 'member' }, { name: 'Renée Dubé', kind: 'member' }];

test('C1: a name that starts or ends with an accented letter is masked', () => {
  const r = pg.redact('Émile Dupont runs a 7-figure shop. Renée Dubé agreed.', accented, new Set());
  assert.ok(!/Dupont/.test(r.text), r.text);
  assert.ok(!/Dubé/.test(r.text), r.text);
  assert.deepEqual(r.removed.sort(), ['Renée Dubé', 'Émile Dupont'].sort());
});

test('C1: an accented name the smoother left in refuses the turn', () => {
  assert.deepEqual(pg.leftoverNames('Thanks to Renée Dubé.', accented, new Set()), ['Renée Dubé']);
  assert.deepEqual(pg.leftoverNames('Émile Dupont said so.', accented, new Set()), ['Émile Dupont']);
});

test('C1: an accented name is backed only by a public row, same as an ASCII one', () => {
  const rows = [{ source: 'event', source_id: 'e9', url: 'https://www.mds.co/summit', text: 'Émile Dupont speaks at the Summit' }];
  const backed = pg.backedNames(rows, { 'https://www.mds.co/summit': 'public' }, accented);
  assert.ok(backed.has('Émile Dupont'));
  assert.ok(!backed.has('Renée Dubé'));
});

// --- review I1 (#169): only the exact spelling was ever masked. A middle initial, a hyphen-vs-space
// variant, ALL CAPS, a possessive, or a first-name-only mention all passed BOTH passes — redact()
// left them in and leftoverNames() did not refuse them, so they published. ---

test('I1: a middle initial or a middle name between the two tokens does not hide the name', () => {
  const r = pg.redact('Jonathan R. Jewett said X. Jonathan Robert Jewett said it again.', names, new Set());
  assert.ok(!/Jewett/.test(r.text), r.text);
  assert.deepEqual(pg.leftoverNames('Jonathan R. Jewett said X.', names, new Set()), ['Jonathan Jewett']);
});

test('I1: hyphen, space and doubled space are the same separator', () => {
  const hy = [{ name: 'Mary-Jane Smith', kind: 'member' }];
  assert.ok(!/Smith/.test(pg.redact('Mary Jane Smith said X.', hy, new Set()).text));
  assert.ok(!/Smith/.test(pg.redact('Mary-Jane  Smith said X.', hy, new Set()).text));
  assert.deepEqual(pg.leftoverNames('Mary Jane Smith said X.', hy, new Set()), ['Mary-Jane Smith']);
});

test('I1: an ALL CAPS full name and an ALL CAPS first-name follow-up are both masked', () => {
  const r = pg.redact('ÉMILE DUPONT ran the test. Later ÉMILE added Y.', accented, new Set());
  assert.ok(!/DUPONT|ÉMILE/.test(r.text), r.text);
});

test('I1: a possessive form is masked and stays grammatical', () => {
  const r = pg.redact("Émile Dupont's shop grew. Émile's margins doubled.", accented, new Set());
  assert.ok(!/Dupont|Émile/.test(r.text), r.text);
  assert.match(r.text, /^a member's shop grew\./);
  assert.ok(r.text.includes('their margins doubled.'), r.text);
});

test('I1: a first-name-only mention of an indexed closed name is masked, and refuses if it survives', () => {
  const sarah = [{ name: 'Sarah Chen', kind: 'member' }];
  const r = pg.redact('Sarah shared a bundling tip.', sarah, new Set());
  assert.ok(!/Sarah/.test(r.text), r.text);
  assert.deepEqual(r.removed, ['Sarah Chen']);
  assert.deepEqual(pg.leftoverNames('Sarah shared a bundling tip.', sarah, new Set()), ['Sarah Chen']);
});

test('I1: a short first name, a common word and a lowercase word are all left alone', () => {
  const mixed = [{ name: 'Bob Lee', kind: 'member' }, { name: 'Will Turner', kind: 'member' }, { name: 'Prime Wilson', kind: 'member' }];
  const draft = 'Bob is short. Will this ship? The prime slot is 9am.';
  assert.equal(pg.redact(draft, mixed, new Set()).text, draft);
  assert.deepEqual(pg.leftoverNames(draft, mixed, new Set()), []);
});

// --- review I2 (#169): redact() touched names only, so a member-only video link, a private
// Facebook-group post or a WhatsApp invite sitting in the draft was published verbatim — Public
// Verify only ever questioned URLs that were NOT already in the draft, never the ones that were. ---

const VIDEO_LINK = 'https://app.mds.co/videos/6a97599308e2e42a631c1a35';
const linkClasses = { 'https://www.mds.co/summit': 'public', [VIDEO_LINK]: 'closed' };

test('I2: a closed-source link is removed from the body and recorded as a redaction', () => {
  const r = pg.redactLinks(`Watch ${VIDEO_LINK} for the panel.`, linkClasses);
  assert.ok(!r.text.includes('app.mds.co'), r.text);
  assert.ok(r.text.includes('[link removed]'), r.text);
  assert.deepEqual(r.removed, [{ kind: 'link', detail: 'app.mds.co/videos/6a97599308e2e42a631c1a35', replaced_with: '[link removed]' }]);
});

test('I2: a url no evidence row classified is closed too (unknown = closed)', () => {
  const r = pg.redactLinks('Join https://chat.whatsapp.com/ABC123 or https://www.facebook.com/groups/699138040189700/posts/1 today.', linkClasses);
  assert.ok(!/whatsapp|facebook/.test(r.text), r.text);
  assert.equal(r.removed.length, 2);
  assert.deepEqual(r.removed.map(x => x.kind), ['link', 'link']);
});

test('I2: a world-public url survives untouched', () => {
  const t = 'The agenda is at https://www.mds.co/summit — see you there.';
  const r = pg.redactLinks(t, linkClasses);
  assert.equal(r.text, t);
  assert.deepEqual(r.removed, []);
});

test('I2: trailing punctuation and markdown wrapping do not hide a closed link', () => {
  const r = pg.redactLinks(`See [the panel](${VIDEO_LINK}).`, linkClasses);
  assert.ok(!r.text.includes('app.mds.co'), r.text);
  assert.equal(r.removed[0].detail, 'app.mds.co/videos/6a97599308e2e42a631c1a35');
});

test('I2: a closed link the smoother re-introduced refuses the turn', () => {
  assert.deepEqual(pg.closedUrls(`Watch ${VIDEO_LINK} now.`, linkClasses), [VIDEO_LINK]);
  assert.deepEqual(pg.closedUrls('The agenda is at https://www.mds.co/summit.', linkClasses), []);
});

test('I2: a name slug inside a surviving public url is neither rewritten nor a refusal reason', () => {
  const speakers = [{ name: 'Anna Lee', kind: 'member' }];
  const classes = { 'https://www.mds.co/speakers/anna-lee': 'public' };
  const t = 'Details: https://www.mds.co/speakers/anna-lee';
  const lk = pg.redactLinks(t, classes);
  const r = pg.redact(lk.text, speakers, new Set());
  assert.equal(r.text, t);
  assert.deepEqual(pg.leftoverNames(r.text, speakers, new Set()), []);
});

test('I1: a first name shared with a BACKED name is left alone so the backed name survives intact', () => {
  const both = [{ name: 'Bryce Alderson', kind: 'member' }, { name: 'Bryce Smith', kind: 'member' }];
  const backed = new Set(['Bryce Alderson']);
  const r = pg.redact('Bryce Alderson spoke publicly. Bryce Smith did not.', both, backed);
  assert.ok(r.text.includes('Bryce Alderson spoke publicly.'), r.text);
  assert.ok(!r.text.includes('Bryce Smith'), r.text);
  assert.deepEqual(pg.leftoverNames(r.text, both, backed), []);
});
