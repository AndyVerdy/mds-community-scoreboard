// #174 NAMED ITEM = DRILL-DOWN — offline proof against the SHIPPED node code, so the test and the
// workflow can never drift:
//
//   node scripts/olivia_loop/test_174_named_item.js <dump-of-Format-Reply.js> <dump-of-Plan-Request.js>
//
// Andy, prod 2026-09-07 (turns 65488-65491, execs 137508/137515): a four-video answer, then
// "Tell me more about Alex Chiru video" was re-planned as a fresh speaker search. Two functions:
//   Format Reply  offerItemsOf(offerText, vids) -> [{id, name}]     the line she wrote for each video
//   Plan Request  namedOfferItem(po, rawText)   -> {ids, names}|null the offered item(s) a message names
//
// The fear is the FALSE BIND: a new question that happens to share a word with a listed title must
// still reach the normal lanes. Precision over recall — an unbound drill-down is today's behaviour,
// a wrongly bound question is a new defect.
const fs = require('fs');

function extract(src, name, params) {
  const re = new RegExp('function ' + name + '\\(' + params + '\\) \\{[\\s\\S]*?\\n\\}');
  const m = src.match(re);
  if (!m) { console.error('FAIL: ' + name + '() not found in ' + (src.length) + '-char dump'); process.exit(1); }
  return new Function(m[0] + '; return ' + name + ';')();
}
const offerItemsOf = extract(fs.readFileSync(process.argv[2], 'utf8'), 'offerItemsOf', 'offerText, vids');
const namedOfferItem = extract(fs.readFileSync(process.argv[3], 'utf8'), 'namedOfferItem', 'po, rawText');

const ID_INTELLIVY = '69853b206249bac2ab910453';
const ID_GULLO = '67f6e83df8bd6929dfdac122';
const ID_CHIRU = '6a8866c0b6eea7310359279e';
const ID_NGUYEN = '63e5b87443688c474cfb0737'; // the gate-appended bare URL — no naming line

// prod turn 65489, exactly as Format Reply saw it (gate-appended bare URL included)
const ANSWER = [
  'Plenty on this in MDS - both community threads and calls that walk through building the actual hypothesis.',
  '',
  '*Best places to learn the hypothesis method:*',
  '• *How Brands Turn Failed Creative Tests Into High-Converting Sales Assets* (Peter-Paul Maan & Travis, Intellivy) - his core point: most tests fail because people test "this looks better" instead of a real purchase-driver hypothesis, evaluated against actual competitors in full marketplace context, not in isolation.',
  'https://app.mds.co/videos/' + ID_INTELLIVY,
  '',
  '• *How to Run Proper A/B Tests* (Fabio Gullo, ex-Google, 800+ experiments) - the practical rulebook: test simultaneously not sequentially, and know WHICH metric you\'re actually trying to move (hero image/title → CTR; images/bullets/A+ → conversion).',
  'https://app.mds.co/videos/' + ID_GULLO,
  '',
  '• *Amazon\'s 75-Character Title Update* (Alex Chiru, Aug 2026) - covers the new title/item-highlights split and how backend attributes now outrank the title itself for indexing.',
  'https://app.mds.co/videos/' + ID_CHIRU,
  '',
  '*From members forming real hypotheses:*',
  '• Casey Xiao-Morris\'s test - single-unit vs 3-pack hero image - flat CTR but a real CVR jump: https://www.facebook.com/groups/699138040189700/posts/25092536150423216/',
  '',
  '*Tools members actually use to run the test:*',
  '• Productpinion (10% off lifetime) - polling + search simulation, one 5★ review on file',
  'https://app.mds.co/partners/67907af701681a357f8797c9',
  '• Listing Optimization AI (20% off) - built-in A/B testing on main images, no member reviews yet',
  'https://app.mds.co/partners/6a47a720a12d0048f6889cdd',
  '',
  'https://app.mds.co/videos/' + ID_NGUYEN,
  'Want me to dig into any one of these further?'
].join('\n');
const VIDS = [ID_INTELLIVY, ID_GULLO, ID_CHIRU, ID_NGUYEN];

let pass = 0, fail = 0;
function check(label, cond, got) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL  ' + label + (got !== undefined ? '\n      got: ' + JSON.stringify(got) : '')); }
}

// ───────── Format Reply: offerItemsOf ─────────
const items = offerItemsOf(ANSWER, VIDS);
check('records one item per NAMED video (the bare gate-appended URL has no naming line)', items.length === 3, items);
check('items keep the offer order', items.map(function (i) { return i.id; }).join(',') === [ID_INTELLIVY, ID_GULLO, ID_CHIRU].join(','), items);
check('name = the line above the link, bullet and bold stripped',
  items[0] && items[0].name.indexOf('How Brands Turn Failed Creative Tests Into High-Converting Sales Assets (Peter-Paul Maan & Travis, Intellivy)') === 0, items[0]);
check('speaker text survives in the name', items[2] && items[2].name.indexOf('(Alex Chiru, Aug 2026)') !== -1, items[2]);
check('name capped at 160 chars', items.every(function (i) { return i.name.length <= 160; }), items.map(function (i) { return i.name.length; }));
check('no item carries a URL in its name', items.every(function (i) { return !/https?:\/\//.test(i.name); }), items);
const sameLine = offerItemsOf('Watch the Town Hall recap here: https://app.mds.co/videos/aaaaaaaaaaaaaaaaaaaaaaaa\nWant it?', ['aaaaaaaaaaaaaaaaaaaaaaaa']);
check('a same-line link takes the prose before the URL', sameLine.length === 1 && sameLine[0].name === 'Watch the Town Hall recap here', sameLine);
const titled = offerItemsOf('*Listing Optimisation Deep Dive* (Mogul Call, Oct 2025) — Alex Chiru & Andrei Ureche tear down real listings.\nhttps://app.mds.co/videos/68e71145690f8559747275c5', ['68e71145690f8559747275c5']);
check('a title line then its link', titled.length === 1 && titled[0].name.indexOf('Listing Optimisation Deep Dive (Mogul Call, Oct 2025)') === 0, titled);
check('no videos -> no items', offerItemsOf(ANSWER, []).length === 0);
check('an unknown id -> no item', offerItemsOf(ANSWER, ['ffffffffffffffffffffffff']).length === 0);

// ───────── Plan Request: namedOfferItem ─────────
const PO = { kind: 'video', ids: VIDS, count: 4, nouns: ['further'],
  titles: ['Best places to learn the hypothesis method:', 'How Brands Turn Failed Creative Tests Into High-Converting Sales Assets', 'How to Run Proper A/B Tests', "Amazon's 75-Character Title Update"],
  items: items };
const ids = function (r) { return r ? r.ids.join(',') : null; };

check('case 1: "Tell me more about Alex Chiru video" -> the Chiru video', ids(namedOfferItem(PO, 'Tell me more about Alex Chiru video')) === ID_CHIRU, namedOfferItem(PO, 'Tell me more about Alex Chiru video'));
check('the bound item carries its name for the seed', (namedOfferItem(PO, 'Tell me more about Alex Chiru video') || {}).names[0].indexOf("Amazon's 75-Character Title Update") === 0);
check('a bare full name binds (two distinctive words, no cue needed)', ids(namedOfferItem(PO, 'Alex Chiru')) === ID_CHIRU);
check('"Summarize the Fabio one" -> the Gullo video', ids(namedOfferItem(PO, 'Summarize the Fabio one')) === ID_GULLO);
check('"what does the Intellivy video cover?" -> the Intellivy video', ids(namedOfferItem(PO, 'what does the Intellivy video cover?')) === ID_INTELLIVY);
check('title words work too: "tell me more about the title update one"', ids(namedOfferItem(PO, 'tell me more about the title update one')) === ID_CHIRU);
check('"more on Chiru" (cue + one word)', ids(namedOfferItem(PO, 'more on Chiru')) === ID_CHIRU);
check('possessive in the line does not block: "more about the amazon title one"', ids(namedOfferItem(PO, 'more about the amazon title one')) === ID_CHIRU);

// — must NOT bind —
check('a single distinctive word with no cue stays unbound ("Alex")', namedOfferItem(PO, 'Alex') === null);
check('a line-initial capital is not a name ("How about tariffs?")', namedOfferItem(PO, 'How about tariffs?') === null);
check('a new question sharing title words stays unbound ("any Creative Tests events coming up?")', namedOfferItem(PO, 'any Creative Tests events coming up?') === null);
check('"how many videos does Alex Chiru have?" is a new question', namedOfferItem(PO, 'how many videos does Alex Chiru have?') === null);
check('a bare yes is not a named item', namedOfferItem(PO, 'yes') === null);
check('a long message (17+ words) never binds', namedOfferItem(PO, 'Tell me more about Alex Chiru video and also everything else you have on titles images and split tests please now') === null);
check('no items recorded (older rows) -> null', namedOfferItem({ kind: 'video', ids: VIDS, titles: PO.titles, nouns: ['further'] }, 'Tell me more about Alex Chiru video') === null);
check('no offer -> null', namedOfferItem(null, 'Tell me more about Alex Chiru video') === null);
check('empty message -> null', namedOfferItem(PO, '') === null);
check('a word shared by two items is not distinctive', namedOfferItem({ kind: 'video', ids: [ID_INTELLIVY, ID_GULLO],
  items: [{ id: ID_INTELLIVY, name: 'Amazon Creative Tests (Peter-Paul Maan)' }, { id: ID_GULLO, name: 'Amazon Proper Tests (Fabio Gullo)' }] },
  'tell me more about the Amazon one') === null);

// — two candidates: both come back, the seed asks which —
const TWO = { kind: 'video', ids: [ID_CHIRU, '684848cdba50a5f61dbdb54d', ID_GULLO], items: [
  { id: ID_CHIRU, name: "Amazon's 75-Character Title Update (Alex Chiru, Aug 2026)" },
  { id: '684848cdba50a5f61dbdb54d', name: 'The Future of Amazon Listing Optimization (Alex Chiru & Morris Sued, Inspire 2025)' },
  { id: ID_GULLO, name: 'How to Run Proper A/B Tests (Fabio Gullo)' }] };
const two = namedOfferItem(TWO, 'Tell me more about the Alex Chiru video');
check('two items sharing the name -> both ids, in offer order', ids(two) === ID_CHIRU + ',684848cdba50a5f61dbdb54d', two);
check('an extra word narrows the pair ("the Alex Chiru Morris Sued one")', ids(namedOfferItem(TWO, 'more about the Alex Chiru Morris Sued one')) === '684848cdba50a5f61dbdb54d');

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
