// #175 LINK REPAIR PAIRS A URL WITH ITS OWN ROW — offline proof against the SHIPPED Gate Verdict
// bytes, so the test and the workflow can never drift:
//
//   node scripts/olivia_loop/test_175_link_pairing.js <dump-of-Gate-Verdict.js>
//
// Andy's case 1 (prod 2026-09-07, execs 137508 / 137515): the #1b link-coverage repair paired each
// evidence URL with the last `title` in the 900 chars BEFORE it. A top-5 evidence row carries up to
// 3,200 chars of snippets between its title and its video_url, so the URL fell to the "after"
// fallback and was paired with the NEXT row's title — and when that next row was named and linked
// in the draft, the previous row's URL was appended bare (65ef9f07… rode on "Listing Optimisation
// Deep Dive", 63e5b874… on "How Brands Turn Failed Creative Tests…"). A restricted duplicate catalog
// row of a talk the draft already linked was appended too (67e4836b…, 8 of 10 title words).
//
//   linkCoverageUrls(evRaw, answerText) -> [url, ...]   the URLs the repair may append (max 3)
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/function linkCoverageUrls\(evRaw, answerText\) \{[\s\S]*?\n\}/);
if (!m) { console.error('FAIL: linkCoverageUrls() not found in ' + src.length + '-char dump'); process.exit(1); }
const linkCoverageUrls = new Function(m[0] + '; return linkCoverageUrls;')();

const LONG = 'x'.repeat(1300); // one snippet field longer than the old 900-char look-back
const UA = 'https://app.mds.co/videos/aaaaaaaaaaaaaaaaaaaaaaaa';
const UB = 'https://app.mds.co/videos/bbbbbbbbbbbbbbbbbbbbbbbb';
const UC = 'https://app.mds.co/videos/cccccccccccccccccccccccc';
const UD = 'https://app.mds.co/videos/dddddddddddddddddddddddd';
const row = function (title, url, extra) {
  return '{"title":"' + title + '","call_type":"Mogul Call","speakers":[],"description_snippet":"' + LONG
    + '","cliff_notes_snippet":"' + LONG + '","duration":"1:00:00","published_at":"2025-10-08","video_url":"' + url + '"' + (extra || '') + '}';
};
const T_NGUYEN = 'Why Split Test? Every 1% CR Increase Grows Sales By 5% - 10% - Anthony Nguyen - Mogul Call';
const T_MAAN = 'How Brands Turn Failed Creative Tests Into High-Converting Sales Assets - Peter-Paul Maan - Mogul Call';
const EV = 'PRELOADED (deterministic search):\nDIGESTS (2):\n[' + row(T_NGUYEN, UA) + ',' + row(T_MAAN, UB) + ']';

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (ok) { pass++; } else { fail++; console.log('FAIL  ' + label + '\n      got:  ' + JSON.stringify(got) + '\n      want: ' + JSON.stringify(want)); }
}

// — the case-1 shape: the draft names and links row B; row A is never mentioned —
check('a long row does not lend its URL to the next row (case 1, 137508)',
  linkCoverageUrls(EV, 'Start with *How Brands Turn Failed Creative Tests Into High-Converting Sales Assets* (Peter-Paul Maan).\n' + UB + '\n\nWant me to dig into it?'), []);
// — the repair itself still works: a named row with its link omitted —
check('a named row whose link the draft omits still gets its URL (B5019 shape)',
  linkCoverageUrls(EV, 'Anthony Nguyen covered this in *Why Split Test? Every 1% CR Increase Grows Sales By 5% - 10%* - worth an hour.'), [UA]);
check('both named, only one linked -> only the missing one',
  linkCoverageUrls(EV, 'Two calls: Why Split Test? Every 1% CR Increase Grows Sales By 5% - 10% (Anthony Nguyen) and How Brands Turn Failed Creative Tests Into High-Converting Sales Assets.\n' + UB), [UA]);
// — the restricted duplicate of a talk the draft already links (case 1, 137515) —
const EV_DUP = '[' + row('The Future of Amazon Listing Optimization － Alex Chiru & Morris Sued － Inspire 2025', UB)
  + ',' + row('Morris Sued & Alex Chiru － The Future of Amazon Listing Optimization － Inspire 2025', UC) + ']';
check('a duplicate catalog row of an already-linked talk is not appended',
  linkCoverageUrls(EV_DUP, '*The Future of Amazon Listing Optimization* (Inspire 2025) - Alex Chiru & Morris Sued on Cosmo.\n' + UB), []);
check('the duplicate rule needs a linked twin: unlinked, the named talk gets ONE link (the first row)',
  linkCoverageUrls(EV_DUP, '*The Future of Amazon Listing Optimization* (Inspire 2025) - Alex Chiru & Morris Sued on Cosmo.'), [UB]);
// — url-first rows (Facebook shape): the title follows the url inside the same row —
const EV_FB = '[{"source":"fb_post","url":"https://www.facebook.com/groups/1/posts/111/","title":"Tariff thread by Casey Xiao-Morris","body":"' + LONG + '"},'
  + '{"source":"fb_post","url":"https://www.facebook.com/groups/1/posts/222/","title":"Freight forwarding thread by Ryan Bastuba","body":"' + LONG + '"}]';
check('url-first rows pair with the title inside their own row',
  linkCoverageUrls(EV_FB, 'See the Freight forwarding thread by Ryan Bastuba for the rates people got.'), ['https://www.facebook.com/groups/1/posts/222/']);
check('url-first rows: the neighbour is never borrowed',
  linkCoverageUrls(EV_FB, 'See the Tariff thread by Casey Xiao-Morris.'), ['https://www.facebook.com/groups/1/posts/111/']);
// — a nested attachments array before the url (the real 684848cd row shape, 137515) —
const ATT = ',"attachments":[{"key":"' + 'bbbbbbbbbbbbbbbbbbbbbbbb' + ':0","kind":"deck","name":"The Future of Amazon Listing Optimization.pdf"}]';
const rowAtt = function (title, url) {
  return '{"title":"' + title + '","call_type":"Summit","speakers":["Morris Sued"],"description_snippet":"' + LONG + '","cliff_notes_snippet":null' + ATT
    + ',"duration":"39:32","categories":["Amazon listing"],"published_at":"2025-06-10","video_url":"' + url + '","matched_rank":0.03,"is_restricted":false}';
};
const EV_ATT = '[' + rowAtt('The Future of Amazon Listing Optimization － Alex Chiru & Morris Sued － Inspire 2025', UB)
  + ',' + row('Morris Sued & Alex Chiru － The Future of Amazon Listing Optimization － Inspire 2025', UC) + ']';
check('a row with a nested attachments array still pairs with its own title (linked twin blocks the duplicate)',
  linkCoverageUrls(EV_ATT, '*The Future of Amazon Listing Optimization* (Inspire 2025) - Alex Chiru & Morris Sued on Cosmo.\n' + UB), []);
check('a row with a nested attachments array, named and unlinked, gets its own URL',
  linkCoverageUrls('[' + rowAtt('Alpha Session One', UB) + ']', 'Watch Alpha Session One first.'), [UB]);
// — image and logo fields never become links —
const EV_IMG = '[' + row(T_NGUYEN, UA, ',"thumbnail_url":"https://cdn.example.com/a.jpg"') + ']';
check('a thumbnail_url is never appended', linkCoverageUrls(EV_IMG, 'Anthony Nguyen\'s *Why Split Test? Every 1% CR Increase Grows Sales By 5% - 10%* is the one.'), [UA]);
// — bounds —
check('nothing named -> nothing appended', linkCoverageUrls(EV, 'Plenty on this in MDS. Want the list?'), []);
check('a link already in the draft is never repeated', linkCoverageUrls(EV, T_NGUYEN + '\n' + UA), []);
const EV_MANY = '[' + row('Alpha Session One', UA) + ',' + row('Bravo Session Two', UB) + ',' + row('Charlie Session Three', UC) + ',' + row('Delta Session Four', UD) + ']';
check('at most three links are appended',
  linkCoverageUrls(EV_MANY, 'Alpha Session One, Bravo Session Two, Charlie Session Three and Delta Session Four all cover it.'), [UA, UB, UC]);
check('a scattered word match is not a citation',
  linkCoverageUrls(EV, 'Split testing is worth it. Every seller should test. Sales grow when you increase CR by 1% - Anthony said so on a call.'), []);

// ───────── #139: partner rows carry `name` + `offer_value` + `partner_url`, never `title` ─────────
const P_MEDIA = 'https://app.mds.co/partners/aaaaaaaaaaaaaaaaaaaaaaa1';
const P_SOCIAL = 'https://app.mds.co/partners/aaaaaaaaaaaaaaaaaaaaaaa2';
const prow = function (name, offer, url, extra) {
  return '{"name":"' + name + '","offer_value":"' + offer + '","description_snippet":"' + LONG + '","categories":["TikTok Shop","Working with Agencies"],"rating_avg":null,"review_count":0,"claim_count":2,"featured":false,"fresh_deal":false,"partner_url":"' + url + '","reviews_sample":null,"matched_rank":0.03,"fit_reason":null,"strength_note":null,"web_people":[{"name":"Jane Doe","role":"Founder"}]' + (extra || '') + '}';
};
const EV_P = 'TOOL partner_lookup (2 rows):\n[' + prow('Media Labs', '15% OFF first 3 months', P_MEDIA) + ',' + prow('Social Tale', 'Free audit', P_SOCIAL) + ']';
check('#139: a named partner with no link gets its page WITH its offer, as one line',
  linkCoverageUrls(EV_P, 'There are also TikTok Shop agency partner deals in the directory (Media Labs, Zainith) — none have reviews on file yet.\n\nWant the links?'),
  ['Media Labs (15% OFF first 3 months): ' + P_MEDIA]);
check('#139: an already-linked partner is left alone',
  linkCoverageUrls(EV_P, 'Media Labs (15% OFF first 3 months) is the one people mention.\n' + P_MEDIA), []);
check('#139: a partner nobody named is never appended',
  linkCoverageUrls(EV_P, 'Ask in the MDS TikTok chat — plenty of agency talk there.'), []);
check('#139: the nested web_people "name" never poses as the row name (Jane Doe is not a partner)',
  linkCoverageUrls(EV_P, 'Jane Doe founded it.'), []);
check('#139: a partner with no offer on file gets a plain "Name: page" line',
  linkCoverageUrls('[' + prow('Zainith', '', 'https://app.mds.co/partners/aaaaaaaaaaaaaaaaaaaaaaa3') + ']', 'Zainith came up too.'),
  ['Zainith: https://app.mds.co/partners/aaaaaaaaaaaaaaaaaaaaaaa3']);

// ───────── #175 lap 2 (staging b39b31ab, execs 137901 / 137902, 2026-09-08): the #1c FIELD repair ─────────
// The #1c repair (registration_url / event_url) appended a row's event_url when the draft already carried the
// SAME row's reg_link (Inspire: /s/events/u/… vs /events/u/…; Centurion: go.mdsonly.co vs /events/u/…), and
// pinned "Register: go.mdsonly.co/MDSSummitSingapore" to an answer about 2027 because "…not a repeat of
// Singapore:\n*MDS Summit Cancun 2027*" read as naming "MDS Summit Singapore" — the re-ordered-words window ran
// across a colon, a line break and a bold title, and the Summit had already ended.
//
//   _nameInAnswer(name, hay)                          -> the entity is NAMED inside one line / clause
//   fieldRepairSkip(evRaw, idx, answerText, nowMs)    -> 'linked' | 'past' | ''
const mN = src.match(/const _nameInAnswer = function \(nm, hay\) \{[\s\S]*?\n\};/);
if (!mN) { console.error('FAIL: _nameInAnswer not found'); process.exit(1); }
const nameInAnswer = new Function(mN[0] + '; return _nameInAnswer;')();
const mF = src.match(/function fieldRepairSkip\(evRaw, idx, answerText, nowMs\) \{[\s\S]*?\n\}/);
if (!mF) { console.error('FAIL: fieldRepairSkip() not found in ' + src.length + '-char dump'); process.exit(1); }
const fieldRepairSkip = new Function(mF[0] + '; return fieldRepairSkip;')();

const D2027 = 'Good news — it\'s already been announced! The next MDS Summit is set for *Cancun*, not a repeat of Singapore:\n\n*MDS Summit Cancun 2027*\n📅 Sunday, September 26, 2027\n📍 Cancun, Mexico';
check('lap 2: "…of Singapore:\\n*MDS Summit Cancun 2027*" does NOT name "MDS Summit Singapore" (exec 137902)', nameInAnswer('MDS Summit Singapore', D2027), false);
check('lap 2: the same draft DOES name "MDS Summit Cancun 2027"', nameInAnswer('MDS Summit Cancun 2027', D2027), true);
check('lap 2: the same words re-ordered inside one clause still count ("the MDS Singapore Summit")', nameInAnswer('MDS Summit Singapore', 'Are you going to the MDS Singapore Summit this year?'), true);
check('lap 2: the exact phrase counts', nameInAnswer('MDS Summit Singapore', 'MDS Summit Singapore ran Aug 23-26.'), true);
check('lap 2: one word of a three-word name is not a naming', nameInAnswer('MDS Summit Singapore', 'This year is Singapore.'), false);

const INSPIRE = '{"event_name":"MDS Inspire 2027","starts_at":"2027-03-23T01:00:00+00:00","start_display":"Mon Mar 22, 2027, 06:00 PM local time - upcoming","phase":"Registration Open","city":"Las Vegas","is_registered":false,"can_register":true,"reg_link":"https://app.mds.co/s/events/u/6999d19ee1e4872c9bef6ae8","guest_reg_link":null,"spots_left":null,"registered_count":44,"event_url":"https://app.mds.co/events/u/6999d19ee1e4872c9bef6ae8","fit_reason":"the room skews toward what you work on","room":{"niches":[{"niche":"Housewares","members":11}]}}';
const CENTURION = '{"event_name":"MDS Centurion Summit California 2027","starts_at":"2027-06-02T23:00:00+00:00","start_display":"Wed Jun 02, 2027, 04:00 PM local time - upcoming","phase":"Registration Open","reg_link":"https://go.mdsonly.co/MDSCenturionSummitCalifornia2027","guest_reg_link":null,"event_url":"https://app.mds.co/events/u/6a3ad6dc099f1da75b3b8995","room":null}';
const SG = '{"event":{"name":"MDS Summit Singapore","venue":"The Ritz-Carlton Hotel","maps_url":"https://www.google.com/maps/search/?api=1&query=1.29,103.85","event_url":"https://app.mds.co/events/u/689cfd00f1f12d7791cf9525","registration_url":"https://go.mdsonly.co/MDSSummitSingapore","starts_on":"Sun 23 Aug, 6:00 am Singapore time","ends_on":"Wed 26 Aug, 6:00 pm Singapore time","phase":"ended","is_over":true,"status_line":"The event has finished."},"day":"2026-09-08"}';
const EVX = 'TOOL event_lookup:\n[' + INSPIRE + ',' + CENTURION + ']\n' + SG;
const at = function (ev, url) { return ev.indexOf('"event_url":"' + url) >= 0 ? ev.indexOf('"event_url":"' + url) : ev.indexOf('"registration_url":"' + url); };
const NOW = Date.parse('2026-09-08T01:00:00Z');
check('lap 2: Inspire event_url is covered when the draft carries the row\'s reg_link (exec 137901)',
  fieldRepairSkip(EVX, at(EVX, 'https://app.mds.co/events/u/6999d19ee1e4872c9bef6ae8'), '• *MDS Inspire 2027* — Las Vegas, Mon Mar 22 2027. Registration is open.\nhttps://app.mds.co/s/events/u/6999d19ee1e4872c9bef6ae8', NOW), 'linked');
check('lap 2: Centurion event_url is covered by its go.mdsonly.co reg_link',
  fieldRepairSkip(EVX, at(EVX, 'https://app.mds.co/events/u/6a3ad6dc099f1da75b3b8995'), '• *MDS Centurion Summit California 2027*\nhttps://go.mdsonly.co/MDSCenturionSummitCalifornia2027', NOW), 'linked');
check('lap 2: an upcoming row with nothing of it linked is not skipped',
  fieldRepairSkip(EVX, at(EVX, 'https://app.mds.co/events/u/6999d19ee1e4872c9bef6ae8'), '• *MDS Inspire 2027* — Las Vegas, Mon Mar 22 2027.', NOW), '');
check('lap 2: a finished event never gets a Register line (is_over / phase ended)',
  fieldRepairSkip(EVX, at(EVX, 'https://go.mdsonly.co/MDSSummitSingapore'), D2027, NOW), 'past');
check('lap 2: a maps_url in the draft does not count as the row being linked',
  fieldRepairSkip(EVX, at(EVX, 'https://app.mds.co/events/u/689cfd00f1f12d7791cf9525'), 'Venue: https://www.google.com/maps/search/?api=1&query=1.29,103.85', NOW), 'past');
check('lap 2: an escaped-JSON evidence string (\\" quotes) is read the same way',
  fieldRepairSkip(JSON.stringify(EVX), JSON.stringify(EVX).indexOf('\\"event_url\\":\\"https://app.mds.co/events/u/6999d19ee1e4872c9bef6ae8'), 'https://app.mds.co/s/events/u/6999d19ee1e4872c9bef6ae8', NOW), 'linked');

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
