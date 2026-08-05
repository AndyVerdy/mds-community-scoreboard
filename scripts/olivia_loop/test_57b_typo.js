// Offline proof for the #57b `form` -> `from` normaliser, run against the SHIPPED code so the
// test and the workflow can never drift:
//
//   node scripts/olivia_loop/test_57b_typo.js <dump-of-Resolve-Member.js>
//
// The fear here is not the typo case (that one is obvious) — it is the FALSE POSITIVE: a member
// writing about an actual form ("the signup form is broken", "form a company") must reach the
// report/answer lanes with their words intact.
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/function askAs\(t\) \{[\s\S]*?\n\}/);
if (!m) { console.error('FAIL: askAs() not found in ' + process.argv[2]); process.exit(1); }
const askAs = new Function(m[0] + '; return askAs;')();

// [input, expected]
const CASES = [
  // — the typo must be read as a preposition —
  ['who is form africa?', 'who is from africa?'],
  ["who's form cyprus", "who's from cyprus"],
  ['whos form the balkans', 'whos from the balkans'],
  ['who are the members form germany', 'who are the members from germany'],
  ['anyone form texas?', 'anyone from texas?'],
  ['are there people form the UK', 'are there people from the UK'],
  ['is anyone form South Africa in the group', 'is anyone from South Africa in the group'],
  ['who is form Africa?', 'who is from Africa?'],

  // — a real form must survive untouched —
  ['the signup form is broken', 'the signup form is broken'],
  ['I want to form a company in Delaware', 'I want to form a company in Delaware'],
  ['where are form submissions going?', 'where are form submissions going?'],
  ['can you send me the form link', 'can you send me the form link'],
  ['is the form field required', 'is the form field required'],
  ['members form an LLC for this', 'members form an LLC for this'],
  ['the typeform form is not loading', 'the typeform form is not loading'],
  ['who is going to fill the form', 'who is going to fill the form'],
  // ACCEPTED LIMIT, asserted so it stays visible rather than hidden: `form the <noun>` is read as
  // the preposition, because the common ask really is "any members form the UK". The verb reading
  // ("people form the backbone") is therefore rewritten. Cost is nil — that sentence is not a
  // question anyone asks an assistant, and the entity-formation phrasing that IS plausible
  // ("form a company", "form an LLC") stays blocked by the a/an guard above.
  ['people form the backbone of MDS', 'people from the backbone of MDS'],

  // — nothing to do —
  ['who is from africa?', 'who is from africa?'],
  ['who is based in Cyprus', 'who is based in Cyprus'],
  ['', '']
];

let pass = 0, fail = 0;
CASES.forEach(function (c) {
  const got = askAs(c[0]);
  if (got === c[1]) { pass++; }
  else { fail++; console.log('FAIL  in: ' + JSON.stringify(c[0]) + '\n      got: ' + JSON.stringify(got) + '\n      want: ' + JSON.stringify(c[1])); }
});
console.log('rewrites ' + CASES.slice(0, 8).length + ' · form-noun preserved ' + CASES.slice(8, 16).length + ' · accepted limit 1 · noop ' + CASES.slice(17).length);
console.log(pass + '/' + CASES.length + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
