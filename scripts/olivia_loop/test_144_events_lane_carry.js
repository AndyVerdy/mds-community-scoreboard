// #144 A FOLLOW-UP ABOUT EVENTS STAYS IN THE EVENTS LANE — offline proof against the SHIPPED Plan Request
// bytes:
//
//   node scripts/olivia_loop/test_144_events_lane_carry.js <dump-of-Plan-Request.js>
//
// Verified still present 2026-09-08 00:44Z (staging, bank C 6372, rows 65729/65731): one turn after
// event_lookup listed MDS Summit Cancun 2027, "Can you let me know when they announce the main meetup
// for 2027?" was planned as a content search and she said nothing is announced for the 2027 Summit —
// contradicting her own previous turn. A short follow-up naming an event word or a year after an
// event_lookup turn stays in the events lane, with the year and the event word as terms.
//
//   eventsLaneCarry(rawText, prevPlan) -> { terms: [...] } | null
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/function eventsLaneCarry\(rawText, prevPlan\) \{[\s\S]*?\n\}/);
if (!m) { console.error('FAIL: eventsLaneCarry() not found in ' + src.length + '-char dump'); process.exit(1); }
const eventsLaneCarry = new Function(m[0] + '; return eventsLaneCarry;')();

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (ok) { pass++; } else { fail++; console.log('FAIL  ' + label + '\n      got:  ' + JSON.stringify(got) + '\n      want: ' + JSON.stringify(want)); }
}
const EV = { op: 'event_lookup', params: { p_phone: '1', p_limit: 12, p_terms: ['2027'] } };
const SEARCH = { op: 'content_search', params: { p_terms: ['tariffs'] } };

check('6372: "…the main meetup for 2027? This year is Singapore" after event_lookup -> year + event word',
  eventsLaneCarry('Can you let me know when they announce the main meetup for 2027? This year is Singapore', EV), { terms: ['2027', 'meetup'] });
check('"give me the exact details for MDS Inspire 2027" after event_lookup -> year + inspire',
  eventsLaneCarry('give me the exact details for *MDS Inspire 2027*', EV), { terms: ['2027', 'inspire'] });
check('"and the summit?" after event_lookup -> summit', eventsLaneCarry('and the summit?', EV), { terms: ['summit'] });
check('"is that one virtual?" after event_lookup -> event word "one"? no: null (no event word, no year)', eventsLaneCarry('is that one virtual?', EV), null);
check('a follow-up after a content search never carries', eventsLaneCarry('Can you let me know when they announce the main meetup for 2027?', SEARCH), null);
check('no previous plan -> null', eventsLaneCarry('and the summit?', null), null);
check('a long message (21+ words) never carries', eventsLaneCarry('Can you let me know when they announce the main meetup for 2027 and also everything about every other event you have on file please', EV), null);
check('a year alone carries the year', eventsLaneCarry('what about 2028', EV), { terms: ['2028'] });
check('a non-event topic word after event_lookup -> null ("what about tariffs")', eventsLaneCarry('what about tariffs', EV), null);

console.log(pass + '/' + (pass + fail) + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
