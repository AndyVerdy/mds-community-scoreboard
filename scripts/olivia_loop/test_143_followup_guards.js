// #143 FOLLOW-UP GUARDS — offline proof against the SHIPPED node code, so the test and the workflow can
// never drift:
//
//   node scripts/olivia_loop/test_143_followup_guards.js <dump-of-Plan-Request.js> <dump-of-Format-Reply.js>
//
// Four deterministic guards on offer binding (bank C 6095 / 6349 + the 2026-09-07 staging probes):
//   Plan Request  isNewQuestion(msg)             a new-question opener never reads as an acceptance
//   Plan Request  bareOrdinalPick(rawText, n)    "the second one" after n offered items -> index, else -1
//   Format Reply  offerTitlesOf(offerText)       bold spans count as offered titles only under an offer question, never numbers
//   Format Reply  ticketOfferLine(offerText)     her own-words offer to file a report/ticket with the team
const fs = require('fs');

function extract(src, name, params) {
  const re = new RegExp('function ' + name + '\\(' + params + '\\) \\{[\\s\\S]*?\\n\\}');
  const m = src.match(re);
  if (!m) { console.error('FAIL: ' + name + '() not found in ' + src.length + '-char dump'); process.exit(1); }
  return new Function(m[0] + '; return ' + name + ';')();
}
const pr = fs.readFileSync(process.argv[2], 'utf8');
const fr = fs.readFileSync(process.argv[3], 'utf8');
const isNewQuestion = extract(pr, 'isNewQuestion', 'msg');
const bareOrdinalPick = extract(pr, 'bareOrdinalPick', 'rawText, n');
const offerTitlesOf = extract(fr, 'offerTitlesOf', 'offerText');
const ticketOfferLine = extract(fr, 'ticketOfferLine', 'offerText');

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (ok) { pass++; } else { fail++; console.log('FAIL  ' + label + '\n      got:  ' + JSON.stringify(got) + '\n      want: ' + JSON.stringify(want)); }
}

// ───────── isNewQuestion ─────────
check('6095 shape: "Is there any bigger revenue group" is a new question', isNewQuestion('Is there any bigger revenue group'), true);
check('"any Creative Tests events coming up?" is a new question', isNewQuestion('any Creative Tests events coming up?'), true);
check('"how many videos does Alex Chiru have?" is a new question', isNewQuestion('how many videos does Alex Chiru have?'), true);
check('"who is in the 20M chat" is a new question', isNewQuestion('who is in the 20M chat'), true);
check('"Tell me more about Alex Chiru video" is not', isNewQuestion('Tell me more about Alex Chiru video'), false);
check('"yes please" is not', isNewQuestion('yes please'), false);
check('"what does the Intellivy video cover?" is not (what-does is a drill-down)', isNewQuestion('what does the Intellivy video cover?'), false);
check('"the second one" is not', isNewQuestion('the second one'), false);
check('empty is not', isNewQuestion(''), false);

// ───────── bareOrdinalPick ─────────
check('"the second one" of 3 -> 1', bareOrdinalPick('the second one', 3), 1);
check('"first" of 3 -> 0', bareOrdinalPick('first', 3), 0);
check('"The first one please." of 3 -> 0', bareOrdinalPick('The first one please.', 3), 0);
check('"the last one" of 3 -> 2', bareOrdinalPick('the last one', 3), 2);
check('"number 2" of 3 -> 1', bareOrdinalPick('number 2', 3), 1);
check('"2" of 3 -> 1', bareOrdinalPick('2', 3), 1);
check('"the third video" of 3 -> 2', bareOrdinalPick('the third video', 3), 2);
check('"the second one" of 1 -> -1 (nothing to pick from)', bareOrdinalPick('the second one', 1), -1);
check('"the fourth one" of 3 -> -1 (out of range)', bareOrdinalPick('the fourth one', 3), -1);
check('"second thoughts on this" -> -1 (not bare)', bareOrdinalPick('second thoughts on this', 3), -1);
check('"tell me more about the second one" -> -1 (handled by the named/cue path, not the bare ordinal)', bareOrdinalPick('tell me more about the second one', 3), -1);
check('"yes" -> -1', bareOrdinalPick('yes', 3), -1);
check('"" -> -1', bareOrdinalPick('', 3), -1);

// ───────── offerTitlesOf ─────────
const CREDIT = 'You\'ve got *$3,615.00* in MDS credit sitting on your account right now 🎉\n\nThat gets applied by the MDS team at renewal, or you can request it sooner if you need it used before then.';
check('a bold number with no offer question is not an offered title', offerTitlesOf(CREDIT), []);
check('a bold number under an offer question is still not a title', offerTitlesOf(CREDIT + '\n\nWant me to open a ticket with the MDS team?'), []);
const LIST = '*Best places to learn the hypothesis method:*\n• *How to Run Proper A/B Tests* (Fabio Gullo)\nhttps://app.mds.co/videos/67f6e83df8bd6929dfdac122\n• *Amazon\'s 75-Character Title Update* (Alex Chiru)\nhttps://app.mds.co/videos/6a8866c0b6eea7310359279e\n\nWant me to dig into any one of these further?';
check('bold titles under an offer question are recorded, in order', offerTitlesOf(LIST), ['Best places to learn the hypothesis method:', 'How to Run Proper A/B Tests', "Amazon's 75-Character Title Update"]);
check('the same list with NO offer question records no titles', offerTitlesOf(LIST.replace('\n\nWant me to dig into any one of these further?', '')), []);
check('an offer question in the middle does not count — only the last line', offerTitlesOf('*Fabio Gullo* ran it. Want the summary? Anyway, here is the link.\nhttps://app.mds.co/videos/67f6e83df8bd6929dfdac122'), []);
check('a percentage in bold is not a title', offerTitlesOf('Conversion moved *12.5%* on the test.\n\nWant the full breakdown?'), []);
check('a short bold word (under 6 chars) is not a title', offerTitlesOf('It was *fine*.\n\nWant more?'), []);

// ───────── ticketOfferLine ─────────
check('6349 shape: "Want me to file this as a report so the team can check…?"', ticketOfferLine('I don\'t see any credit balance.\n\nWant me to file this as a report so the team can check if there\'s a credit balance not showing up on my end?'), true);
check('the seed\'s exact sentence', ticketOfferLine('Nothing on file for that.\n\nI can open a ticket with the MDS team - reply YES and I will file it.'), true);
check('"Want me to flag this to the team?"', ticketOfferLine('Want me to flag this to the team?'), true);
check('"Should I raise a ticket for you?"', ticketOfferLine('Should I raise a ticket for you?'), true);
check('statement-form offer (staging 137712): "Let me know if you\'d like me to flag that request to them."', ticketOfferLine('You\'ve got *$3,615.00* in MDS credit.\n\nThe team applies it at renewal. Let me know if you\'d like me to flag that request to them.'), true);
check('"Happy to escalate this to the MDS team if you want" (no punctuation)', ticketOfferLine('Happy to escalate this to the MDS team if you want'), true);
check('"Want me to send you the link?" is not a ticket offer', ticketOfferLine('Want me to send you the link?'), false);
check('"Want me to send the report to you?" is not a ticket offer', ticketOfferLine('Want me to send the report to you?'), false);
check('"Want a quick summary?" is not a ticket offer', ticketOfferLine('Here it is.\n\nWant a quick summary?'), false);
check('"Want me to pull the invoice?" is not', ticketOfferLine('Want me to pull the invoice?'), false);
check('a ticket offer that is NOT the last line does not count', ticketOfferLine('Want me to file a report with the team?\nActually here is the answer instead.'), false);
check('empty -> false', ticketOfferLine(''), false);

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
