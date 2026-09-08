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
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const pg = require('./public_gate.js');

const names = [{ name: 'Jonathan Jewett', kind: 'member' }, { name: 'Bryce Alderson', kind: 'member' }];
// The closed row here is a WhatsApp message — a RESTRICTED ROOM under #176, and the kind of source
// this gate actually exists to hide. It used to be a Facebook group post, which #169 also treated as
// closed; #176 corrects that (the group is where a public answer gets POSTED — see the #176 section
// at the foot of this file). Class maps in these mechanics tests are supplied by hand; which sources
// really earn `public` is digest.public_gate_classify()'s job, not the module's.
const messages = [
  { role: 'assistant', content: [{ type: 'tool_use', name: 'content_search_v2' }] },
  { role: 'user', content: [{ type: 'tool_result', content: JSON.stringify([
      { source: 'wa_message', source_id: 'p1', url: 'https://chat.whatsapp.com/ABC123', body: 'Jonathan Jewett shared a TikTok tip' },
      { source: 'event', source_id: 'e1', url: 'https://www.mds.co/summit', body: 'Bryce Alderson speaks at the Summit' },
  ]) }] },
];

test('extractEvidenceRows keeps every row and collects keys', () => {
  const ev = pg.extractEvidenceRows(messages);
  assert.equal(ev.rows.length, 2);
  assert.deepEqual(ev.urls.sort(), ['https://chat.whatsapp.com/ABC123', 'https://www.mds.co/summit']);
  assert.deepEqual(ev.source_ids.sort(), ['e1', 'p1']);
});

test('a name is backed only by a PUBLIC row that contains it', () => {
  const ev = pg.extractEvidenceRows(messages);
  const classes = { 'https://chat.whatsapp.com/ABC123': 'closed', 'https://www.mds.co/summit': 'public' };
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

// --- partner rows: not every field on one comes from the listing. #169 fix round 4 kept only
// name/web_summary/web_people/web_pricing, on the grounds that those alone are "world-public" —
// the reading #176 corrects. Partner listings AND THEIR PAGES are open to members, reviews
// included, so reviews_sample backs a name now. fit_reason/strength_note still do not: they come
// from digest.entity_dossier (aggregated across content, transcripts included), so their
// provenance is not one identifiable open source, and unknown provenance stays closed. ---

test("#176: a member named in a partner's reviews_sample IS backed — the listing page is open to members", () => {
  const raw = JSON.stringify([
    { name: 'Prosperlytics Consultants', partner_url: 'https://app.mds.co/partners/p1',
      reviews_sample: [{ author: 'Jonathan Jewett', text: 'great' }] },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { 'https://app.mds.co/partners/p1': 'public' };
  const backed = pg.backedNames(ev.rows, classes, names);
  assert.ok(backed.has('Jonathan Jewett'));
});

test('#176: a name appearing only in fit_reason / strength_note is NOT backed by the partner row', () => {
  const raw = JSON.stringify([
    { name: 'Prosperlytics Consultants', partner_url: 'https://app.mds.co/partners/p1',
      web_summary: 'Bookkeeping for sellers.',
      fit_reason: 'Bryce Alderson rated them well on a call',
      strength_note: 'Jonathan Jewett keeps recommending them' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const backed = pg.backedNames(ev.rows, { 'https://app.mds.co/partners/p1': 'public' }, names);
  assert.equal(backed.size, 0);
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

// --- C1 addendum (#169, from the #174 session's independent repro): the boundary fix alone leaves
// the other half of the 33 rows open. An index display name carrying an invisible code point
// ("John Pollock" + U+FE0F) or a differently-normalised accent never matches the clean text the model
// writes, and nothing refuses it. BOTH sides are normalised before matching. ---

test('C1: an invisible code point inside the index name does not hide the name', () => {
  const idx = [{ name: 'John Pollock️', kind: 'member' }, { name: 'Ana​ Lopez', kind: 'member' }];
  const r = pg.redact('John Pollock said X. Ana Lopez agreed.', idx, new Set());
  assert.ok(!/Pollock/.test(r.text), r.text);
  assert.ok(!/Lopez/.test(r.text), r.text);
  assert.equal(pg.leftoverNames('John Pollock said X.', idx, new Set()).length, 1);
});

test('C1: a decomposed accent matches a composed one, in both directions', () => {
  const nfd = 'Émile Dupont'.normalize('NFD'), nfc = 'Émile Dupont'.normalize('NFC');
  assert.ok(!/Dupont/.test(pg.redact(nfc + ' said X.', [{ name: nfd }], new Set()).text));
  assert.ok(!/Dupont/.test(pg.redact(nfd + ' said X.', [{ name: nfc }], new Set()).text));
  assert.deepEqual(pg.leftoverNames(nfd + ' said X.', [{ name: nfc }], new Set()), [nfc]);
});

test('C1 regression: no ASCII \\b word boundary is left anywhere in the module code', () => {
  const src = readFileSync(new URL('./public_gate.js', import.meta.url), 'utf8')
    .split('\n').filter(l => !l.trim().startsWith('//')).join('\n');
  assert.ok(!/\\b/.test(src), 'a \\b escape is back in public_gate.js — it is ASCII-only (review C1)');
});

// --- review R1 (#169, 2026-09-07 re-review): the C1 addendum normalised the INDEX name (normName())
// but never the ANSWER text itself. An invisible code point sitting inside the model's own draft —
// not the index — still defeats the match: the pattern built from a clean index name has nothing to
// find in text carrying a stray ZWSP, so redact() leaves it untouched AND leftoverNames() does not
// refuse either. Fail OPEN, same failure class as C1, just the other operand. Both sides now run
// through the same normalisation, and the normalised text is what gets returned/searched. ---

const ZWSP_NAME = 'Joh​n Pollock'; // U+200B sitting inside the ANSWER text itself, not the index

test('R1: an invisible code point inside the ANSWER text does not defeat the mask', () => {
  const r = pg.redact(ZWSP_NAME + ' walked through it.', [{ name: 'John Pollock' }], new Set());
  assert.ok(!/Pollock/.test(r.text), r.text);
  assert.deepEqual(r.removed, ['John Pollock']);
});

test('R1: leftoverNames refuses when an invisible code point sits inside a surviving name', () => {
  assert.deepEqual(pg.leftoverNames('Thanks to ' + ZWSP_NAME + '.', [{ name: 'John Pollock' }], new Set()), ['John Pollock']);
});

test('R1: an NFD-spelled name in the answer text still masks against an NFC index name', () => {
  const nfc = 'Renée Dubé'.normalize('NFC'), nfd = 'Renée Dubé'.normalize('NFD');
  const r = pg.redact(nfd + ' walked through it.', [{ name: nfc }], new Set());
  assert.ok(!/Dub/.test(r.text), r.text);
  assert.deepEqual(r.removed, ['Renée Dubé']);
  assert.deepEqual(pg.leftoverNames(nfd + ' walked through it.', [{ name: nfc }], new Set()), ['Renée Dubé']);
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

// --- review I2 (#169): redact() touched names only, so a restricted recording's link or a WhatsApp
// invite sitting in the draft was published verbatim — Public Verify only ever questioned URLs that
// were NOT already in the draft, never the ones that were. Still true under #176; what changed is
// which urls come back `public`. A Facebook group link NO evidence row produced is still stripped
// (unknown = closed) — being open as a class is not the same as being cited in this turn. ---

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

test('I2: a url classified open survives untouched', () => {
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

// --- review R2 (#169, 2026-09-07 re-review): the I1 variant pattern's optional middle slot accepted
// ANY 1-15-letter word between the first and last name, so an ordinary sentence word between two
// indexed names — "Bob emailed Ross yesterday." for the indexed "Bob Ross" — was read as a middle
// name and masked whole to "a member yesterday." Fail CLOSED (nobody's real name leaked) but broken
// copy at index scale (5,394 names, plenty of two-word ones sharing a sentence with an ordinary
// verb). The middle slot now accepts only NAME-SHAPED tokens — an initial with an optional period, or
// a capitalised word — at most two of them, so a lowercase word can never fill it. Fixture uses "Bob"
// (3 letters) rather than the "Mike"/"Sarah"-style first name used elsewhere in this file, so the
// separate standalone-first-name pass (review I1, length >= 4) never fires and only the two-word
// middle-slot pattern under test is in play. ---

test('R2: an ordinary lowercase word between two indexed names is left alone, not masked', () => {
  const bobRoss = [{ name: 'Bob Ross', kind: 'member' }];
  const draft = 'Bob emailed Ross yesterday.';
  const r = pg.redact(draft, bobRoss, new Set());
  assert.equal(r.text, draft);
  assert.deepEqual(r.removed, []);
  assert.deepEqual(pg.leftoverNames(draft, bobRoss, new Set()), []);
});

test('R2: a middle initial or a spelled-out middle name still masks', () => {
  const bobRoss = [{ name: 'Bob Ross', kind: 'member' }];
  assert.ok(!/Ross/.test(pg.redact('Bob A. Ross joined the call.', bobRoss, new Set()).text));
  assert.ok(!/Ross/.test(pg.redact('Bob Anthony Ross joined the call.', bobRoss, new Set()).text));
});

test('R2: an accented name with a middle initial still masks', () => {
  const r = pg.redact('Émile A. Dupont ran the shop.', accented, new Set());
  assert.ok(!/Dupont/.test(r.text), r.text);
});

test('R2: redact and leftoverNames never disagree across the middle-slot sweep', () => {
  const idx = [{ name: 'Bob Ross', kind: 'member' }];
  const cases = [
    ['Bob emailed Ross yesterday.', false],
    ['Bob and Ross both joined the call.', false],
    ['Bob Ross joined the call.', true],
    ['BOB ROSS JOINED THE CALL.', true],
    ['Bob A. Ross joined the call.', true],
    ['Bob Anthony Ross joined the call.', true],
    ['Bob J. R. Ross joined the call.', true],
  ];
  for (const [draft, shouldMask] of cases) {
    const r = pg.redact(draft, idx, new Set());
    const left = pg.leftoverNames(draft, idx, new Set());
    assert.equal(r.removed.length > 0, shouldMask, `redact disagreement: ${draft}`);
    assert.equal(left.length > 0, shouldMask, `leftoverNames disagreement: ${draft}`);
  }
});

// ============================================================================================
// #176 — WHO A PUBLIC ANSWER IS FOR. Andy, 2026-09-07: "you do realise that Public means MDS
// members ... the only restiriction for public mode is opt in sources", and "the whole idea behind
// public is that we hiding exact details from restictat chats". A public answer is posted into the
// members-only MDS Facebook group, so the group's own posts and comments are OPEN — a name they
// carry may be printed and their links may be shared ("3 fb links that we can share"). What stays
// hidden is exact detail from a RESTRICTED ROOM: a closed WhatsApp channel or a private call.
//
// #169 read "public" as WORLD-public and therefore closed the group too. Which sources earn `public`
// is digest.public_gate_classify()'s job (scripts/sql/20260908_public_gate_classify_member_audience_176.sql);
// what these cases pin is that the module honours the buckets it is handed, in both directions.
// ============================================================================================

const FB_POST_URL = 'https://www.facebook.com/groups/699138040189700/posts/27179812468362230/';
const WA_INVITE = 'https://chat.whatsapp.com/ABC123';
const CALL_URL = 'https://app.mds.co/videos/6a988f8a08e2e42a633350a1';

test('#176: a name that appears ONLY in a Facebook group post is backed, and survives redaction', () => {
  const raw = JSON.stringify([
    { source: 'fb_post', source_id: '27179812468362230', url: FB_POST_URL,
      body: 'Jonathan Jewett shared a TikTok bundling tip that doubled his Q4.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const backed = pg.backedNames(ev.rows, { [FB_POST_URL]: 'public' }, names);
  assert.ok(backed.has('Jonathan Jewett'));
  const r = pg.redact('Jonathan Jewett shared a bundling tip.', names, backed);
  assert.ok(r.text.includes('Jonathan Jewett'), r.text);
  assert.deepEqual(r.removed, []);
  assert.deepEqual(pg.leftoverNames(r.text, names, backed), []);
});

test('#176: a Facebook group post link survives the link pass', () => {
  const t = `A member walked through it here: ${FB_POST_URL}`;
  const r = pg.redactLinks(t, { [FB_POST_URL]: 'public' });
  assert.equal(r.text, t);
  assert.deepEqual(r.removed, []);
  assert.deepEqual(pg.closedUrls(t, { [FB_POST_URL]: 'public' }), []);
});

test('#176: a name that appears ONLY in a closed WhatsApp message is masked, and refused if it survives', () => {
  const raw = JSON.stringify([
    { source: 'wa_message', source_id: 'OsvNzPN5RzkBbQ-gjIBq53ljME8mg', url: WA_INVITE,
      body: 'Jonathan Jewett said his 3PL raised rates 12% in March.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const backed = pg.backedNames(ev.rows, { [WA_INVITE]: 'closed' }, names);
  assert.equal(backed.size, 0);
  const r = pg.redact('Jonathan Jewett said his 3PL raised rates.', names, backed);
  assert.ok(!/Jonathan|Jewett/.test(r.text), r.text);
  assert.deepEqual(r.removed, ['Jonathan Jewett']);
  assert.deepEqual(pg.leftoverNames('Thanks to Jonathan Jewett.', names, backed), ['Jonathan Jewett']);
});

test('#176: a name that appears ONLY in a call transcript is masked, and refused if it survives', () => {
  const raw = JSON.stringify([
    { source: 'call_transcript', source_id: 'chunk-42', url: CALL_URL,
      body: 'Bryce Alderson: we cut our CAC to eleven dollars on that channel.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const backed = pg.backedNames(ev.rows, { [CALL_URL]: 'closed' }, names);
  assert.equal(backed.size, 0);
  const r = pg.redact('Bryce Alderson cut CAC to eleven dollars.', names, backed);
  assert.ok(!/Bryce|Alderson/.test(r.text), r.text);
  assert.deepEqual(pg.leftoverNames('As Bryce Alderson put it, CAC fell.', names, backed), ['Bryce Alderson']);
});

test('#176: a verbatim quote from a call transcript is a closed source — the row is closed and its link goes', () => {
  const raw = JSON.stringify([
    { source: 'call_transcript', source_id: 'chunk-42', url: CALL_URL,
      body: 'Bryce Alderson: we cut our CAC to eleven dollars on that channel.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { [CALL_URL]: 'closed' };
  // rowClass drives `closed_sources`, which is what puts "From a call recording, paraphrased."
  // in the notes — the paraphrase-not-quote instruction the smoother is given.
  assert.equal(pg.rowClass(ev.rows[0], classes), 'closed');
  assert.deepEqual([...new Set(ev.rows.filter(r => pg.rowClass(r, classes) === 'closed').map(r => r.source))],
                   ['call_transcript']);
  // and the recording's own link never publishes
  const lk = pg.redactLinks(`Full recording: ${CALL_URL}`, classes);
  assert.ok(!lk.text.includes('app.mds.co'), lk.text);
  assert.equal(lk.removed.length, 1);
});

test('#176: a source the classifier never classified is still closed — unknown did not change', () => {
  const raw = JSON.stringify([
    { source: 'some_new_feed', source_id: 'n1', url: 'https://example.com/whatever',
      body: 'Bryce Alderson said something quotable.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.equal(pg.rowClass(ev.rows[0], {}), 'closed');
  assert.equal(pg.backedNames(ev.rows, {}, names).size, 0);
  assert.deepEqual(pg.closedUrls('See https://example.com/whatever for more.', {}),
                   ['https://example.com/whatever']);
});

// ============================================================================================
// #176 D1 — AN OPEN POST'S AUTHOR BACKS THEIR OWN NAME. Found by the 30-probe eval (2026-09-08):
// q10's public answer masked eight members — Daniel Meredith, Dimitri Vorona, Ben Anderson,
// Travis Reese, Jason Pratt, Richard Lo, Ryan Carey, Claude Jeanloz — that the same question
// answered ungated named freely off the same open group threads. A poster's name is not in the
// body of what they wrote; it lives in the row's author/speaker metadata (`meta.author_name` on a
// content_search row, `author` on an fb_thread row, `speakers` on a library row, `author` inside a
// partner's `reviews_sample`). Those fields now back a name — for an OPEN row only.
// ============================================================================================

test('D1: the author of an open Facebook post backs their own name, even when the body never says it', () => {
  const raw = JSON.stringify([
    { source: 'fb_post', kind: 'post', source_id: '26794200516923429', url: FB_POST_URL,
      body: 'Asking for some wisdom from the group about systems and tools.',
      meta: { has_image: false, author_name: 'Jonathan Jewett', sender_member: 'recN0ejwtEsNEGrvu' } },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.ok(ev.rows[0].authors.includes('Jonathan Jewett'), JSON.stringify(ev.rows[0].authors));
  const backed = pg.backedNames(ev.rows, { [FB_POST_URL]: 'public' }, names);
  assert.ok(backed.has('Jonathan Jewett'));
  const r = pg.redact('Jonathan Jewett asked almost this exact question.', names, backed);
  assert.ok(r.text.includes('Jonathan Jewett'), r.text);
  assert.deepEqual(r.removed, []);
});

test('D1: the author of a CLOSED row does not back their name — the room is what decides', () => {
  const raw = JSON.stringify([
    { source: 'wa_message', source_id: 'OsvNzPN5RzkBbQ', url: WA_INVITE,
      body: 'my 3PL raised rates 12% in March',
      meta: { author_name: 'Jonathan Jewett', chat_name: '#logistics' } },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.ok(ev.rows[0].authors.includes('Jonathan Jewett'));
  const backed = pg.backedNames(ev.rows, { [WA_INVITE]: 'closed' }, names);
  assert.equal(backed.size, 0);
  const r = pg.redact('Jonathan Jewett said his 3PL raised rates.', names, backed);
  assert.ok(!/Jonathan|Jewett/.test(r.text), r.text);
});

test('D1: an fb_thread row carries its author top-level, and that backs the name too', () => {
  const raw = JSON.stringify([
    { kind: 'comment', author: 'Bryce Alderson', body: 'We run Slack plus ClickUp.',
      url: FB_POST_URL + '?comment_id=24609783842031785', post_id: '26794200516923429' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { [FB_POST_URL + '?comment_id=24609783842031785']: 'public' };
  assert.ok(pg.backedNames(ev.rows, classes, names).has('Bryce Alderson'));
});

test('D1: a library row backs the names of its speakers', () => {
  const raw = JSON.stringify([
    { title: 'Mogul Call: running two businesses on ClickUp', speakers: ['Jonathan Jewett'],
      url: 'https://app.mds.co/videos/library-entry', description_snippet: 'How the workspace is laid out.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.ok(ev.rows[0].authors.includes('Jonathan Jewett'), JSON.stringify(ev.rows[0].authors));
  assert.ok(pg.backedNames(ev.rows, { 'https://app.mds.co/videos/library-entry': 'public' }, names)
              .has('Jonathan Jewett'));
});

test('D1: an author-shaped field does NOT widen what a partner row backs — fit_reason still cannot', () => {
  const raw = JSON.stringify([
    { name: 'Prosperlytics Consultants', partner_url: 'https://app.mds.co/partners/p1',
      web_summary: 'Bookkeeping for sellers.',
      fit_reason: 'Bryce Alderson rated them well on a call',
      strength_note: 'Jonathan Jewett keeps recommending them' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.equal(pg.backedNames(ev.rows, { 'https://app.mds.co/partners/p1': 'public' }, names).size, 0);
});

// ============================================================================================
// #176 D3 — A ROW THE RETRIEVAL LAYER DID NOT LABEL IS MISLABELLED, NOT UNKNOWN. q10's public
// answer reported `source_summary {"other": 18}`: not one evidence row carried a source tag, so
// no row could be keyed, nothing classified, and every name in the answer was masked. Two separate
// causes, both fixed here:
//   (a) the tools that return a row WITHOUT `source` — video_search (video_url/title/speakers),
//       partner_lookup (partner_url), fb_thread (kind/author/url/post_id) — were unrecognisable to
//       the row extractor, and video_search's link field was not even in the url coalesce list, so
//       a library row could never be keyed at all;
//   (b) the biggest evidence block of the turn is not a tool_result. `Answer Seed` renders the
//       deterministic pre-search into the final user message as "RAW MATCHES (n): [...]" TEXT —
//       40 full content rows, urls and author names included — and the extractor never read it.
//       That is where q10's eight members and its group link lived.
// Unknown is unchanged: a row nothing can be derived from is still keyless, and keyless is closed.
// ============================================================================================

const LIB_URL = 'https://app.mds.co/videos/6a97599308e2e42a631c1a35';

test('D3: a video_search row is keyed by its library id, so an open library entry can back a name', () => {
  const raw = JSON.stringify([
    { title: 'Mogul Call: two businesses on ClickUp', call_type: 'Mogul Call',
      speakers: ['Jonathan Jewett'], description_snippet: 'How the workspace is laid out.',
      video_url: LIB_URL, is_restricted: false },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.equal(ev.rows[0].source, 'video');
  assert.equal(ev.rows[0].source_id, '6a97599308e2e42a631c1a35');
  assert.equal(ev.rows[0].url, LIB_URL);
  assert.ok(pg.backedNames(ev.rows, { '6a97599308e2e42a631c1a35': 'public' }, names).has('Jonathan Jewett'));
});

test('D3: a call transcript row is NOT re-keyed by the recording it quotes — it stays closed', () => {
  // The transcript chunk's own `url` IS the recording's app link, and that link's 24-hex id is the
  // library entry the classifier calls open. Deriving an id from the url for a row that already
  // carries `source`/`source_id` would turn every transcript row open. It does not.
  const raw = JSON.stringify([
    { source: 'call_transcript', kind: 'chunk', source_id: '6a97599308e2e42a631c1a35#13',
      url: LIB_URL, body: 'Bryce Alderson: we cut our CAC to eleven dollars.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.equal(ev.rows[0].source, 'call_transcript');
  assert.equal(ev.rows[0].source_id, '6a97599308e2e42a631c1a35#13');
  const classes = { '6a97599308e2e42a631c1a35': 'public', [LIB_URL]: 'closed',
                    '6a97599308e2e42a631c1a35#13': 'closed' };
  assert.equal(pg.rowClass(ev.rows[0], classes), 'closed');
  assert.equal(pg.backedNames(ev.rows, classes, names).size, 0);
});

test('D3: an fb_thread row is labelled from its kind and keyed by its post id', () => {
  const raw = JSON.stringify([
    { kind: 'post', author: 'Ben Anderson', body: 'Asking for some wisdom from the group.',
      url: FB_POST_URL, post_id: '26794200516923429' },
    { kind: 'comment', author: 'Bryce Alderson', body: 'Slack plus ClickUp.',
      url: FB_POST_URL + '?comment_id=1', post_id: '26794200516923429' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.deepEqual(ev.rows.map(r => r.source), ['fb_post', 'fb_comment']);
  assert.deepEqual(ev.rows.map(r => r.source_id), ['26794200516923429', '26794200516923429']);
});

test('D3: a partner row is labelled `partner`', () => {
  const raw = JSON.stringify([{ name: 'ClickUp', partner_url: 'https://app.mds.co/partners/p1',
                                web_summary: 'PM tool.' }]);
  assert.equal(pg.extractEvidenceRows(toolResult(raw)).rows[0].source, 'partner');
});

test('D3: a row nothing can be derived from is still keyless, and keyless is still closed', () => {
  const raw = JSON.stringify([{ blob: 'Bryce Alderson said something quotable.', score: 0.4 }]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  assert.equal(ev.rows[0].source, null);
  assert.equal(ev.rows[0].source_id, null);
  assert.equal(ev.rows[0].url, null);
  assert.equal(pg.rowClass(ev.rows[0], { 'anything': 'public' }), 'closed');
  assert.equal(pg.backedNames(ev.rows, { 'anything': 'public' }, names).size, 0);
});

// --- the preloaded evidence block: rows, not prose ---

function preloadMsg(body) {
  return [{ role: 'user', content: [{ type: 'text', text:
    'PRELOADED EVIDENCE — a deterministic search already ran for this exact message; treat it as '
    + 'your first tool result:\n' + body + '\n\nMEMBER MESSAGE:\nwhat do people use for systems?' }] }];
}

const PRELOAD_ROWS = [
  { source: 'fb_post', kind: 'post', source_id: '26794200516923429', title: null, tl_dr: null,
    body: 'Asking for some wisdom from the group about systems and tools.',
    occurred_at: '2026-08-07T16:58:51+00:00', url: FB_POST_URL, sensitivity: 'normal',
    meta: { has_image: false, author_name: 'Jonathan Jewett', sender_member: 'recN0ejwtEsNEGrvu' } },
  { source: 'wa_message', kind: 'message', source_id: 'OsvNzPN5RzkBbQ', body: 'we moved to ClickUp',
    url: WA_INVITE, meta: { author_name: 'Bryce Alderson', chat_name: '#ops' } },
];

test('D3: the preloaded RAW MATCHES block is read as evidence, not skipped as prose', () => {
  const ev = pg.extractEvidenceRows(preloadMsg('RAW MATCHES (2):\n' + JSON.stringify(PRELOAD_ROWS)));
  assert.equal(ev.rows.length, 2);
  assert.deepEqual(ev.rows.map(r => r.source), ['fb_post', 'wa_message']);
  assert.ok(ev.urls.includes(FB_POST_URL));
  assert.ok(ev.source_ids.includes('26794200516923429'));
});

test('D3: a preloaded open post backs its author and keeps its link; the preloaded closed chat does not', () => {
  const ev = pg.extractEvidenceRows(preloadMsg('RAW MATCHES (2):\n' + JSON.stringify(PRELOAD_ROWS)));
  const classes = { [FB_POST_URL]: 'public', [WA_INVITE]: 'closed' };
  const backed = pg.backedNames(ev.rows, classes, names);
  assert.deepEqual([...backed], ['Jonathan Jewett']);
  const lk = pg.redactLinks(`Jonathan Jewett asked this too: ${FB_POST_URL} — also ${WA_INVITE}`, classes);
  assert.ok(lk.text.includes(FB_POST_URL), lk.text);
  assert.ok(!lk.text.includes('whatsapp'), lk.text);
  const r = pg.redact(lk.text + ' Bryce Alderson answered in the chat.', names, backed);
  assert.ok(r.text.includes('Jonathan Jewett'), r.text);
  assert.ok(!/Bryce|Alderson/.test(r.text), r.text);
});

test('D3: a preload truncated mid-row still yields every complete row before the cut', () => {
  // Answer Seed hard-caps the preload at 20,000 chars, so the last row is routinely cut in half.
  const full = 'RAW MATCHES (2):\n' + JSON.stringify(PRELOAD_ROWS);
  const cut = full.slice(0, full.length - 60) + ' …[truncated]';
  const ev = pg.extractEvidenceRows(preloadMsg(cut));
  assert.equal(ev.rows.length, 1);
  assert.equal(ev.rows[0].source, 'fb_post');
  assert.ok(ev.urls.includes(FB_POST_URL));
});

test('D3: a DIGESTS block is read too, and ordinary prose in the same message yields no rows', () => {
  const ev = pg.extractEvidenceRows(preloadMsg(
    'ABOUT THE ASKER (their own MDS profile):\n- sells kitchenware\n\nDIGESTS (1):\n'
    + JSON.stringify([{ source: 'wa_digest', source_id: 'd1', url: WA_INVITE, body: 'weekly roundup' }])));
  assert.equal(ev.rows.length, 1);
  assert.equal(ev.rows[0].source, 'wa_digest');
});

test('D3: a user message with no evidence block contributes nothing', () => {
  assert.equal(pg.extractEvidenceRows([{ role: 'user', content: [{ type: 'text',
    text: 'MEMBER MESSAGE:\nwhat do people use for systems? [1, 2, 3] and {a: 1}' }] }]).rows.length, 0);
});

test('#176: open and restricted rows in the SAME turn split — the group name prints, the call name does not', () => {
  const raw = JSON.stringify([
    { source: 'fb_post', source_id: '27179812468362230', url: FB_POST_URL,
      body: 'Jonathan Jewett shared a TikTok bundling tip.' },
    { source: 'call_transcript', source_id: 'chunk-42', url: CALL_URL,
      body: 'Bryce Alderson: we cut our CAC to eleven dollars.' },
  ]);
  const ev = pg.extractEvidenceRows(toolResult(raw));
  const classes = { [FB_POST_URL]: 'public', [CALL_URL]: 'closed' };
  const backed = pg.backedNames(ev.rows, classes, names);
  assert.deepEqual([...backed], ['Jonathan Jewett']);
  const lk = pg.redactLinks(`See ${FB_POST_URL} and ${CALL_URL}.`, classes);
  assert.ok(lk.text.includes(FB_POST_URL), lk.text);
  assert.ok(!lk.text.includes(CALL_URL), lk.text);
  const r = pg.redact(lk.text + ' Jonathan Jewett and Bryce Alderson both weighed in.', names, backed);
  assert.ok(r.text.includes('Jonathan Jewett'), r.text);
  assert.ok(!/Bryce|Alderson/.test(r.text), r.text);
  assert.deepEqual(pg.leftoverNames(r.text, names, backed), []);
});

// ============================================================================================
// #176 D2 — A LEFTOVER IS REPAIRED, NOT A REASON TO REFUSE. The 30-probe eval (2026-09-08) found
// q6 and q1 refusing outright — "Refused: a closed-source name or an unknown link survived the
// public pass" — while their own notes listed five open group/partner sources and their
// source_summary showed 10 fb_post + 12 fb_comment. A refusal fails Andy's bar on its face: "It
// should be like staging, but it dropped some details from gated sources. still answers, but no
// details and all the info from public sources." So a closed-room name or an unknown link that
// survives the smoother is now MASKED and the answer is kept; the turn is refused only when the
// repair cannot leave an answer behind, or when a second pass still finds a leak.
// ============================================================================================

test('D2: a closed-source name the smoother reintroduced is masked, and the answer survives', () => {
  const backed = new Set(['Bryce Alderson']);
  const smoothed = 'Bryce Alderson ran the numbers and Jonathan Jewett said his 3PL raised rates 12% in March, '
    + 'which is worth planning around before your next restock window.';
  const rep = pg.repairPublic(smoothed, names, backed, { [FB_POST_URL]: 'public' }, []);
  assert.ok(rep.text.includes('Bryce Alderson'), rep.text);
  assert.ok(!/Jonathan|Jewett/.test(rep.text), rep.text);
  assert.deepEqual(rep.removed_names, ['Jonathan Jewett']);
  assert.deepEqual(rep.leftover, []);
  assert.ok(rep.text.includes('3PL raised rates 12% in March'), rep.text);
  assert.ok(pg.repairedSubstance(rep.text).length >= 40, rep.text);
});

test('D2: a closed link the smoother put back is stripped, and the answer survives', () => {
  const classes = { [FB_POST_URL]: 'public', [WA_INVITE]: 'closed' };
  const smoothed = `Two threads cover this: ${FB_POST_URL} and the chat invite ${WA_INVITE}. `
    + 'Both land on the same answer: check the listing copy before the demand letter arrives.';
  const rep = pg.repairPublic(smoothed, names, new Set(), classes, [FB_POST_URL, WA_INVITE]);
  assert.ok(rep.text.includes(FB_POST_URL), rep.text);
  assert.ok(!/whatsapp/.test(rep.text), rep.text);
  assert.deepEqual(rep.removed_links.map(x => x.kind), ['link']);
  assert.deepEqual(rep.leftover_links, []);
});

test('D2: a url the smoother invented is stripped even when the class map calls it public', () => {
  const classes = { [FB_POST_URL]: 'public' };
  // FB_POST_URL is classified public, but it was NOT in the redacted draft — the smoother made it up.
  const rep = pg.repairPublic(`Read it here: ${FB_POST_URL} for the full thread.`, names, new Set(), classes, []);
  assert.ok(!rep.text.includes('facebook.com'), rep.text);
  assert.equal(rep.removed_links.length, 1);
  assert.deepEqual(rep.leftover_links, []);
});

test('D2: a repair leaves an untouched answer untouched', () => {
  const classes = { [FB_POST_URL]: 'public' };
  const clean = `A member walked through the whole playbook here: ${FB_POST_URL} — worth reading in full.`;
  const rep = pg.repairPublic(clean, names, new Set(), classes, [FB_POST_URL]);
  assert.equal(rep.text, clean);
  assert.deepEqual(rep.removed_names, []);
  assert.deepEqual(rep.removed_links, []);
});

test('D2: repairedSubstance measures what is left to say, so "nothing remains" is a real test', () => {
  // an answer that is nothing but role phrases and a stripped link is not an answer
  assert.ok(pg.repairedSubstance('a member said so.').length < 40);
  assert.ok(pg.repairedSubstance('a member. one of the speakers. [link removed]').length < 40);
  assert.ok(pg.repairedSubstance('a member walked through the whole playbook and it is worth reading in full').length >= 40);
});

test('D2: the repair re-checks itself — leftover and leftover_links are the second pass, not the first', () => {
  const rep = pg.repairPublic('Jonathan Jewett and Bryce Alderson both weighed in on the 3PL question this week.',
                              names, new Set(), {}, []);
  assert.deepEqual(rep.removed_names.sort(), ['Bryce Alderson', 'Jonathan Jewett']);
  assert.deepEqual(rep.leftover, []);
  assert.deepEqual(rep.leftover_links, []);
  assert.ok(!/Jonathan|Jewett|Bryce|Alderson/.test(rep.text), rep.text);
});
