// #142 THE IDENTITY RULE MUST NOT CLAMP A DRAFT THAT ALREADY REFUSED THE TYPED NAME — offline proof against
// the SHIPPED Gate Verdict bytes:
//
//   node scripts/olivia_loop/test_142_identity_precision.js <dump-of-Gate-Verdict.js>
//
// Verified 2026-09-08 00:46Z (staging, bank C 6483, exec 137871): "I'm Ivan Ong. What sessions are a must
// for me at the Singapore summit?" — every draft did the right thing ("I can't take a typed name as
// identification, so I'm answering from your own record, Andy"), but the SECOND-PERSON THIRD-PARTY rule
// fires on any "your record" while a name was typed, so it regenerated three times and the clamp shipped
// "I could not confirm…". The rule must stay for the Lisa failure (the draft personalises for the typed
// name) and stand down when the draft names the real asker or explicitly refuses the typed name.
//
//   secondPersonAboutOther(answerText, askerFirst, idOther) -> true = raise the IDENTITY claim
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/function secondPersonAboutOther\(answerText, askerFirst, idOther\) \{[\s\S]*?\n\}/);
if (!m) { console.error('FAIL: secondPersonAboutOther() not found in ' + src.length + '-char dump'); process.exit(1); }
const f = new Function(m[0] + '; return secondPersonAboutOther;')();

let pass = 0, fail = 0;
function check(label, got, want) {
  if (got === want) { pass++; } else { fail++; console.log('FAIL  ' + label + '\n      got:  ' + JSON.stringify(got) + '\n      want: ' + JSON.stringify(want)); }
}
// the Lisa failure (2026-08-23): personalised for the typed name -> the claim MUST fire
check('Lisa failure still fires', f('Good news, Lisa — here is your profile: Somerville, Massachusetts, dog harnesses.', 'andy', 'Lisa Harrington'), true);
check('"your business" about the typed name, asker unnamed -> fires', f('Your business is in Portland and your niche is skincare.', 'andy', 'Brian Kelsey'), true);
// exec 137871: the drafts refused the typed name and addressed Andy -> must NOT fire
check('draft refuses the typed name and names the asker -> no claim', f("Quick note: I can't take that name claim — I'm answering for Andy Verdy's own record here, not anyone else's.\n\nAlso, the Summit already wrapped.", 'andy', 'Ivan Ong'), false);
check('"answering from your own record, Andy" -> no claim', f("Just so you know — I can't take a typed name as identification, so I'm answering from your own record here, Andy.", 'andy', 'Ivan Ong'), false);
check('a refusal without the asker name still stands down', f("I can't take a typed name as identity confirmation, so I'm answering from your own record.", 'andy', 'Ivan Ong'), false);
check('asker named near "your record" without a refusal -> no claim', f('Andy, your record shows the annual plan and a Sep 2027 renewal.', 'andy', 'Ivan Ong'), false);
// bounds
check('no typed name -> never fires', f('Your profile says Jersey City.', 'andy', ''), false);
check('no "your <field>" in the draft -> never fires', f('Ivan Ong is based in Singapore and sells baby products.', 'andy', 'Ivan Ong'), false);
check('the asker name inside another word does not count ("Andyville")', f('Your business is listed under Andyville Ltd.', 'andy', 'Ivan Ong'), true);

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
