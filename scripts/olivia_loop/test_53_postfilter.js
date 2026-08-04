// #53 post-filter v2 — offline test against exec 63490's real evidence + claims.
// EVIDENCE FILE: ev63490.txt = Answer Parse run-1 `evidence_full` from staging exec 63490
// (46,079 chars of member content — deliberately NOT committed; regenerate with:
//   python3 -c "import sys,json; sys.path.insert(0,'scripts'); import olivia_wf as w;
//   st,d=w.api('GET','/executions/63490?includeData=true');
//   open('ev63490.txt','w').write(d['data']['resultData']['runData']['Answer Parse'][1]['data']['main'][0][0]['json']['evidence_full'])"
// EXPECTED: run0 10->0, run1 4->0, run2 6->0 survivors; canary 4->4 survive (still block).
const fs = require('fs');
const evRaw = fs.readFileSync(process.argv[2] || 'ev63490.txt', 'utf8');
const ev = evRaw.toLowerCase();
const evNum = ev.replace(/[,$]/g, '');
// normalized word set: lowercase, non-alnum -> space
const evWords = new Set(ev.replace(/[^a-z0-9]+/g, ' ').split(' ').filter(Boolean));
const wordInEv = (w) => {
  if (evWords.has(w)) return true;
  if (evWords.has(w + 's')) return true;
  if (w.length >= 5 && w.endsWith('s') && evWords.has(w.slice(0, -1))) return true;
  return false;
};
const entitiesOf = (s) => {
  const out = [];
  const names = String(s).match(/[A-Z][a-z][\w'’-]*(?:\s+[A-Z][\w'’-]+)+/g) || [];
  const singles = (String(s).match(/\b[A-Z][A-Za-z'’-]{3,}\b/g) || [])
    .filter(w => !/^(The|This|That|These|Those|Here|There|What|When|Where|Want|With|From|Your|About|Also|Amazon|Facebook|WhatsApp|Olivia)$/.test(w));
  const urls = String(s).match(/https?:\/\/\S+/g) || [];
  const quotes = String(s).match(/["'“”‘’]([^"'“”‘’]{8,})["'“”‘’]/g) || [];
  const nums = (String(s).replace(/[,$]/g, '').match(/\b\d{4,}(?:\.\d+)?\b/g) || [])
    .concat(String(s).replace(/[,$]/g, '').match(/\b\d+(?:\.\d+)?[km]\b/gi) || []);
  return out.concat(names, singles, urls, quotes.map(q => q.slice(1, -1)), nums);
};
// #53: text entities verify at WORD level (>=80% of significant words present, plural-tolerant)
const textEntityInEv = (e) => {
  const s = String(e).toLowerCase().trim();
  if (ev.includes(s)) return true;
  const words = s.replace(/[^a-z0-9]+/g, ' ').split(' ')
    .filter(w => w.length >= 4 && /^[a-z]/.test(w));
  if (!words.length) return false;
  const hits = words.filter(wordInEv).length;
  return hits >= Math.ceil(0.8 * words.length);
};
const verify = (ents) => ents.every(e =>
  /^https?:\/\//.test(String(e)) ? ev.includes(String(e).toLowerCase())
  : (/^[\d.]+[km]?$/i.test(String(e)) ? evNum.includes(String(e).toLowerCase())
  : textEntityInEv(e)));

const RUNS = {
 run0: ["Ephraim Ausch runs Tactical Logistics Solutions",
  "Ephraim worked till 10pm and was back online at 6:30am",
  "Jon Haley asked for a SoCal DTC/dropship 3PL",
  "Mo Kuhail replied 'Check out Tactical Logistics'",
  "Ephraim ran an MDS Mogul Call on cutting placement fees",
  "Fred McKinnon warned about Flexport's $5K/month minimums",
  "Lee Assoulin vouched for Joe Penalba as 'an absolute lifesaver'",
  "Joe Penalba moved to Partner Log Group",
  "Skupreme quoted one member over $10K/month",
  "John Ward got a happy shoutout from a Florida family-run 3PL"],
 run1: ["Brian Kelsey posted a screenshot thank-you after their team stepped in during a Q4 crunch — worked till 10pm, back online at 6:30am",
  "When someone asked for a Southern California 3PL that could handle DTC dropship fulfillment, the top reply pointed straight at them",
  "They've also run an MDS Mogul Call on cutting placement fees before summer sales",
  "Lee Assoulin vouched for his rep Joe Penalba as 'an absolute lifesaver... always goes above and beyond'"],
 run2: ["Brian Kelsey posted a screenshot thank-you after their team stepped in during a Q4 crunch — worked till 10pm, back online at 6:30am",
  "When someone asked for a Southern California 3PL that could handle DTC dropship fulfillment, the top reply pointed straight at them",
  "Ephraim Ausch from Tactical Logistic Solutions ran an MDS Mogul Call on skipping placement fees before summer sales",
  "Lee Assoulin shared that their rep Joe Penalba has moved his book of business over to a new company, Partner Log Group",
  "one member said they quoted over $10K/month",
  "A Florida 'family-run 3PL' got a happy but unnamed shoutout from John Ward"],
 // canaries — MUST SURVIVE (block): entities absent from this evidence
 canary: ["Lori Barzvi runs a candle brand in Miami",
  "Xander Grimaldi said Flexport refunded him $48,200",
  "per Maria Santengelo's post: 'we switched to QuietShip 4PL and saved 60%'",
  "the fix is documented at https://app.mds.co/partners/000fake000id000"]
};

for (const [name, claims] of Object.entries(RUNS)) {
  const survivors = claims.filter(c => {
    const ents = entitiesOf(c);
    if (!ents.length) return false;   // #53: a claim with NOTHING checkable cannot block alone
    return !verify(ents);
  });
  console.log(`${name}: ${claims.length} flagged -> ${survivors.length} survive`);
  survivors.forEach(s => console.log('   SURVIVES:', s.slice(0,90)));
}
