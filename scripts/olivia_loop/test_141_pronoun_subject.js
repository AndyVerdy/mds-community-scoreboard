// #141 PRONOUN FOLLOW-UP KEEPS THE PREVIOUS TURN'S PERSON — offline proof against the SHIPPED Plan Request
// bytes:
//
//   node scripts/olivia_loop/test_141_pronoun_subject.js <dump-of-Plan-Request.js>
//
// Verified still present 2026-09-08 00:39Z (staging, bank C 6500, exec 137838): after two turns about Fred
// McKinnon, "What is his firearms business called?" ran a topic search for "fred firearms", the evidence
// filled with another member's firearms posts, and she rebound "his" to Tamkin Collins — while Fred's own
// firearm/tactical-gear posts (content_items 104754, 105132) never came back. A short third-person follow-up
// with no new name keeps the person the previous plan was about, and the search is scoped to them.
//
//   pronounSubject(rawText, prevPlan) -> the person to scope to, or null
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/function pronounSubject\(rawText, prevPlan\) \{[\s\S]*?\n\}/);
if (!m) { console.error('FAIL: pronounSubject() not found in ' + src.length + '-char dump'); process.exit(1); }
const pronounSubject = new Function(m[0] + '; return pronounSubject;')();

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (ok) { pass++; } else { fail++; console.log('FAIL  ' + label + '\n      got:  ' + JSON.stringify(got) + '\n      want: ' + JSON.stringify(want)); }
}
const FRED = { op: 'member_card', params: { p_phone: '1', p_member: 'Fred McKinnon' } };
const RYAN = { op: 'content_search', params: { p_phone: '1', p_terms: ['tiktok'], p_author: 'Ryan Ebel' } };

check('6500: "What is his firearms business called?" after a Fred turn -> Fred', pronounSubject('What is his firearms business called?', FRED), 'Fred McKinnon');
check('"Where is he based?" -> Fred', pronounSubject('Where is he based?', FRED), 'Fred McKinnon');
check('"Tell me about his TikTok agency" -> Fred', pronounSubject('Tell me about his TikTok agency', FRED), 'Fred McKinnon');
check('"what did she post about it" after an author-scoped search -> that author', pronounSubject('what did she post about it', RYAN), 'Ryan Ebel');
check('a NEW name in the message wins ("What is Tamkin\'s brand?")', pronounSubject("What is Tamkin's brand?", FRED), null);
check('a name plus a pronoun ("Is Brandon in his chat?") is not a bare pronoun follow-up', pronounSubject('Is Brandon in his chat?', FRED), null);
check('no pronoun -> null ("Is there any bigger revenue group")', pronounSubject('Is there any bigger revenue group', FRED), null);
check('no previous person -> null', pronounSubject('What is his firearms business called?', { op: 'content_search', params: { p_terms: ['firearms'] } }), null);
check('no previous plan -> null', pronounSubject('What is his brand?', null), null);
check('first-person pronouns never bind ("what did I post")', pronounSubject('what did I post about tiktok', FRED), null);
check('a long message (17+ words) never binds', pronounSubject('What is his firearms business called and also tell me everything about the brands of everyone else in the group please', FRED), null);
check('"their" after a people search with no single person -> null', pronounSubject('what is their revenue?', { op: 'member_match', params: { p_dims: ['band'] } }), null);

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
