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

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
