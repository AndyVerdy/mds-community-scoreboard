// GATE VERDICT — reads the fact-checker's output. pass -> Format Reply.
// fail (first time) -> regeneration state back to Answer Claude with the
// unsupported claims named. fail (second time) -> honest refusal text.
// Gate-infrastructure errors pass the answer through (the structural
// protections — forced fetch, SQL gates — are still on); gate_error is stamped.
const resp = $input.first().json;
const prev = $('Answer Parse').first().json;
const NL = String.fromCharCode(10);

// REPORT TURNS SKIP THE FACT GATE (2026-08-01, Andy's live test): a bare "report"
// draft ("what would you like to report?") got clamped to the canned miss — but a
// report turn has NOTHING to fact-check: the reply is the member's own words plus a
// confirmation/question, no retrieved facts. The link gate below still runs.
const _memberMsg = String(($('Plan Request').first().json || {}).text || '');
const _isReportTurn = /^\s*report\b/i.test(_memberMsg);

let verdict = null;
try {
  const txt = (resp.content || []).filter(c => c.type === 'text').map(c => c.text).join('');
  verdict = JSON.parse(txt.replace(/^[^{]*/, '').replace(/[^}]*$/, ''));
} catch (e) { verdict = null; }

const finalize = (text, extra) => [{ json: Object.assign({
  done: true, to: prev.to, content: [{ type: 'text', text: text }], metrics: prev.metrics,
}, extra || {}) }];

// #1 LINK GATE (deterministic, 2026-07-30). "Every citation resolves to a real record" — the
// machine-checkable half of the eval judge (verify_citations: EXISTS / NOT FOUND IN WAREHOUSE)
// wired into the send path. Every http(s) URL in the draft must appear VERBATIM in the evidence
// the loop retrieved — evidence rows come from the gated warehouse RPCs, so verbatim = resolves,
// and it also enforces the standing rule that she never offers a link not on file. The Haiku gate
// PASSED a rewritten link today (the model swapped the numeric FB group id for the vanity slug —
// probe 2026-07-30, it resolving was luck): an id-preserving rewrite is auto-REPAIRED back to the
// retrieved URL; a link whose id exists nowhere in the evidence is an invention and fails. Needs
// no model, so it runs on EVERY path — including gate_error, which used to skip all checking.
const evRaw = String(prev.evidence_full || prev.evidence || '');
const stripT = function (u) { return String(u).replace(/[)\]"'”’<>.,!?;:]+$/, ''); };
const urlsIn = function (s) { return (String(s).match(/https?:\/\/[^\s)\]"'<>]+/g) || []).map(stripT); };
const evUrls = urlsIn(evRaw);
let answerText = String(prev.answer_text || '');
const linkClaims = [];
let linkRepairs = 0;
urlsIn(answerText).forEach(function (u) {
  if (evRaw.indexOf(u) !== -1) { return; }                        // verbatim — resolves
  // the load-bearing id: the last path/query segment that looks like a record id
  // (>=8 chars, must contain a digit — never a vanity word like the group slug)
  const segs = u.replace(/^https?:\/\//, '').split(/[\/?#&=]/).filter(Boolean);
  let key = null;
  for (let i = segs.length - 1; i >= 0 && !key; i--) {
    if (/^[A-Za-z0-9_-]{8,}$/.test(segs[i]) && /\d/.test(segs[i])) { key = segs[i]; }
  }
  if (key && evRaw.indexOf(key) !== -1) {
    const fix = evUrls.find(function (e) { return e.indexOf(key) !== -1; });
    if (fix && fix !== u) { answerText = answerText.split(u).join(fix); linkRepairs += 1; }
    // no full URL carries the id (a bare id in a tool row): the id resolves — keep the link
    return;
  }
  linkClaims.push('link not present in any retrieved source: ' + u);
});

// DETERMINISTIC POST-FILTER (2026-07-30). Haiku cannot reliably FIND a name in 60K
// chars of evidence: it rejected "Xander Aeder Putris" as "not in evidence at all"
// while the string sat verbatim in the evidence it was handed. Recall is a string
// problem, not a judgement problem — so before honoring a rejection, check it: a
// claim whose every extractable entity (multi-word names, URLs, quoted spans,
// 4+-digit numbers) is verbatim in the evidence is a haystack false-positive and is
// dropped. A claim naming an entity the evidence truly lacks survives — the
// catastrophic class (invented people/links/quotes/figures) still blocks.
const ev = evRaw.toLowerCase();
// NUMBER MATCHING IS COMMA/FORMAT-INSENSITIVE (2026-08-03, #40 slice regression): real figures
// like "$12,464.38" / "2,808 orders" / "$21,532.19" were unmatchable by \b\d{4,}\b — the commas
// break the digit run — so when Haiku false-flagged a fully-grounded figure-dense answer, the
// figure entities could never verify and the claims survived to block it (Q3110/Q3111, execs
// 61719/61721: every flagged figure sat VERBATIM in the evidence). Strip commas/$ on BOTH sides;
// invented figures still block (they are in no evidence however formatted).
const evNum = ev.replace(/[,$]/g, '');
const entitiesOf = (s) => {
  const out = [];
  const names = String(s).match(/[A-Z][a-z][\w'’-]*(?:\s+[A-Z][\w'’-]+)+/g) || [];
  // single capitalized tokens too ("Sneha", "Euka", "GMV") — most digest claims carry only a
  // first name or a product name, and those were invisible to the filter
  const singles = (String(s).match(/\b[A-Z][A-Za-z'’-]{3,}\b/g) || [])
    .filter(w => !/^(The|This|That|These|Those|Here|There|What|When|Where|Want|With|From|Your|About|Also|Amazon|Facebook|WhatsApp|Olivia)$/.test(w));
  const urls = String(s).match(/https?:\/\/\S+/g) || [];
  const quotes = String(s).match(/["'“”‘’]([^"'“”‘’]{8,})["'“”‘’]/g) || [];
  const nums = (String(s).replace(/[,$]/g, '').match(/\b\d{4,}(?:\.\d+)?\b/g) || []);
  return out.concat(names, singles, urls, quotes.map(q => q.slice(1, -1)), nums);
};
// A URL entity is checked by its LOAD-BEARING ID, not the exact string — the same rule the
// link gate uses. Haiku listed two REAL retrieved links as inventions (staging exec 56839,
// Q3091 probe): the evidence held them with ?comment_id= / formatting differences, so the
// full-string includes() missed and the true-link claims survived to block the answer.
const idInEv = (u) => {
  const segs = String(u).replace(/^https?:\/\//, '').split(/[\/?#&=]/).filter(Boolean);
  for (let i = segs.length - 1; i >= 0; i--) {
    if (/^[A-Za-z0-9_-]{8,}$/.test(segs[i]) && /\d/.test(segs[i])) { return ev.includes(segs[i].toLowerCase()); }
  }
  return ev.includes(String(u).toLowerCase().trim());
};
let hClaims = [];
if (!_isReportTurn && verdict && verdict.verdict === 'fail' && (verdict.unsupported || []).length) {
  hClaims = (verdict.unsupported || []).filter(c => {
    const ents = entitiesOf(c);
    if (!ents.length) return true;                       // nothing checkable — trust the gate
    return !ents.every(e => /^https?:\/\//.test(String(e))
      ? idInEv(e)
      : (/^[\d.]+$/.test(String(e))
          ? evNum.includes(String(e))
          : ev.includes(String(e).toLowerCase().trim())));
  });
}
// DERIVED-AGGREGATE FILTER (Big Smoke 2026-08-01). The gate's worst real-world failure
// class: counts/sums/shares computed FROM the evidence ("20 chapters", "92 + 53 = 145",
// "~13% are agencies") appear nowhere verbatim, Haiku flags them, the regen re-derives
// them, and the second lap clamps a fully-grounded answer to the canned miss (7 of the
// Big Smoke's 15 findings). An aggregation-shaped claim whose every NON-numeric entity
// verifies in the evidence is arithmetic over retrieved rows — the rubric already calls
// that supported; enforce it deterministically. Invented PEOPLE/links/quotes still block:
// any unverified name keeps the claim.
const AGG = /\b(total|sum|combined|across|in all|add(s|ed)? up|percent|%|how many|count|breakdown|\d+\s+(members?|chapters?|chats?|partners?|videos?|events?|people|sellers?|posts?|attendees?|registered|confirmed))\b/i;
hClaims = hClaims.filter(c => {
  const s = String(c);
  if (!AGG.test(s)) return true;
  const nonNum = entitiesOf(s).filter(e => !/^[\d.]+$/.test(String(e)));
  return !nonNum.every(e => /^https?:\/\//.test(String(e))
    ? idInEv(e)
    : ev.includes(String(e).toLowerCase().trim()));
});
// SELF-DESCRIPTION BACKSTOP (2026-07-30, exec 56121). Asked "what data do you have access
// to?", Haiku listed the answer's own source bullets as inventions ("Facebook — posts and
// comments...", "Video library — past Mogul Calls...") — her sources are never IN the
// evidence, by nature. The rubric forbids this (RULE ONE); Haiku disobeyed on thin evidence
// and the honest capability answer got BLOCKED (the Q3009 over-refusal class). Deterministic
// backstop: a claim HEADED by one of her actual source names and carrying no URL and no
// number is describing a source, not citing a record — drop it. Bounded recall tradeoff,
// accepted: an invented no-link no-number "Facebook post by X" claim slips this filter, but
// invented LINKS stay fully covered by the link gate above, and record-level claims are
// normally person-headed, which this never touches.
const SRCHEAD = /^\s*["'“”‘’]?(facebook|whatsapp|the (chats?|facebook group|group)|chats?|member (profiles?|directory)|partner (deals?|directory)|video library|videos?|events?|digests?|library)\b/i;
hClaims = hClaims.filter(c => {
  const s = String(c);
  return !(SRCHEAD.test(s) && !/https?:\/\//.test(s) && !/\d{4,}/.test(s));
});
const claims = linkClaims.concat(hClaims);

if (!claims.length) {
  const extra = {};
  if (linkRepairs) { extra.link_repairs = linkRepairs; }
  if (!verdict || !verdict.verdict) { extra.gate_error = true; }   // gate broke, not the answer
  else { extra.gate = (verdict.verdict === 'pass') ? 'pass' : 'pass-postfilter'; }
  return finalize(answerText, extra);
}
// HOW MANY TIMES HAS THIS GATE ALREADY RUN THIS TURN?
// gate_attempts alone could never work: the regeneration state goes Gate Verdict ->
// Answer Claude -> Answer Parse, and Answer Parse rebuilds state from Answer Seed /
// Answer Merge only, so the flag was dropped every lap and this cap never fired. One
// question looped 36 gate checks and 41 model calls, 417s (2026-07-30). $runIndex is
// this node's own run counter inside the execution — nothing can strip it.
const attempts = Math.max(prev.gate_attempts || 0,
                          typeof $runIndex === 'number' ? $runIndex : 0);
// cap raised 1 -> 2 (Big Smoke 2026-08-01): with the derived-aggregate filter above, a
// second regeneration converges instead of re-tripping on the same arithmetic; the
// $runIndex counter still hard-stops runaway loops.
if (attempts >= 2) {
  return finalize("I looked into that, but I couldn't verify enough of the details against MDS data to give you a solid answer — I'd rather say that than guess. If you can narrow it down, I'll check again.", { gate: 'blocked', gate_claims: claims });
}
// one regeneration with the unsupported claims named
const messages = prev.messages.concat(
  [{ role: 'assistant', content: prev.answer_text }],
  [{ role: 'user', content: 'FACT-GATE: these claims in your draft are NOT supported by the tool results you retrieved: ' + JSON.stringify(claims) + '. Rewrite your answer now, KEEPING everything your tool results DO support — fix or drop ONLY the flagged claims (re-fetch if you need more data). Every name, number and LINK must come from your retrieved tool results, links copied EXACTLY as retrieved. Never replace a mostly-supported answer with a blanket cannot-verify: deliver the supported parts. Anything you cannot support, drop or say plainly you do not have it. Write the reply as a fresh standalone message - the member never saw your draft, so never open with a correction of it. Do not mention this check.' }],
);
return [{ json: {
  done: false, to: prev.to, preload: prev.preload || '', system: prev.system, tools: prev.tools, messages: messages,
  iter: Math.max(prev.iter, 1), max_iter: prev.max_iter + 2,
  in_tok: prev.in_tok, out_tok: prev.out_tok, cache_w: prev.cache_w, cache_r: prev.cache_r,
  calls: prev.calls, t0: prev.t0, gate_attempts: attempts + 1, regen: true,
} }];
