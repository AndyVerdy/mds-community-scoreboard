// GATE VERDICT — reads the fact-checker's output. pass -> Format Reply.
// fail (first time) -> regeneration state back to Answer Claude with the
// unsupported claims named. fail (second time) -> honest refusal text.
// Gate-infrastructure errors pass the answer through (the structural
// protections — forced fetch, SQL gates — are still on); gate_error is stamped.
const resp = $input.first().json;
const prev = $('Answer Parse').first().json;
const NL = String.fromCharCode(10);

let verdict = null;
try {
  const txt = (resp.content || []).filter(c => c.type === 'text').map(c => c.text).join('');
  verdict = JSON.parse(txt.replace(/^[^{]*/, '').replace(/[^}]*$/, ''));
} catch (e) { verdict = null; }

const finalize = (text, extra) => [{ json: Object.assign({
  done: true, to: prev.to, content: [{ type: 'text', text: text }], metrics: prev.metrics,
}, extra || {}) }];

if (!verdict || !verdict.verdict) {
  return finalize(prev.answer_text, { gate_error: true });      // gate broke, not the answer
}

// DETERMINISTIC POST-FILTER (2026-07-30). Haiku cannot reliably FIND a name in 60K
// chars of evidence: it rejected "Xander Aeder Putris" as "not in evidence at all"
// while the string sat verbatim in the evidence it was handed. Recall is a string
// problem, not a judgement problem — so before honoring a rejection, check it: a
// claim whose every extractable entity (multi-word names, URLs, quoted spans,
// 4+-digit numbers) is verbatim in the evidence is a haystack false-positive and is
// dropped. A claim naming an entity the evidence truly lacks survives — the
// catastrophic class (invented people/links/quotes/figures) still blocks.
const ev = String(prev.evidence_full || prev.evidence || '').toLowerCase();
const entitiesOf = (s) => {
  const out = [];
  const names = String(s).match(/[A-Z][a-z][\w'’-]*(?:\s+[A-Z][\w'’-]+)+/g) || [];
  // single capitalized tokens too ("Sneha", "Euka", "GMV") — most digest claims carry only a
  // first name or a product name, and those were invisible to the filter
  const singles = (String(s).match(/\b[A-Z][A-Za-z'’-]{3,}\b/g) || [])
    .filter(w => !/^(The|This|That|These|Those|Here|There|What|When|Where|Want|With|From|Your|About|Also|Amazon|Facebook|WhatsApp|Olivia)$/.test(w));
  const urls = String(s).match(/https?:\/\/\S+/g) || [];
  const quotes = String(s).match(/["'“”‘’]([^"'“”‘’]{8,})["'“”‘’]/g) || [];
  const nums = String(s).match(/\b\d{4,}\b/g) || [];
  return out.concat(names, singles, urls, quotes.map(q => q.slice(1, -1)), nums);
};
let claims = (verdict.unsupported || []);
if (verdict.verdict === 'fail' && claims.length) {
  claims = claims.filter(c => {
    const ents = entitiesOf(c);
    if (!ents.length) return true;                       // nothing checkable — trust the gate
    return !ents.every(e => ev.includes(String(e).toLowerCase().trim()));
  });
}
if (verdict.verdict === 'pass' || !claims.length) {
  return finalize(prev.answer_text, {
    gate: (verdict.verdict === 'pass') ? 'pass' : 'pass-postfilter',
  });
}
verdict = { verdict: 'fail', unsupported: claims };
// HOW MANY TIMES HAS THIS GATE ALREADY RUN THIS TURN?
// gate_attempts alone could never work: the regeneration state goes Gate Verdict ->
// Answer Claude -> Answer Parse, and Answer Parse rebuilds state from Answer Seed /
// Answer Merge only, so the flag was dropped every lap and this cap never fired. One
// question looped 36 gate checks and 41 model calls, 417s (2026-07-30). $runIndex is
// this node's own run counter inside the execution — nothing can strip it.
const attempts = Math.max(prev.gate_attempts || 0,
                          typeof $runIndex === 'number' ? $runIndex : 0);
if (attempts >= 1) {
  return finalize("I looked into that, but I couldn't verify enough of the details against MDS data to give you a solid answer — I'd rather say that than guess. If you can narrow it down, I'll check again.", { gate: 'blocked', gate_claims: verdict.unsupported });
}
// one regeneration with the unsupported claims named
const messages = prev.messages.concat(
  [{ role: 'assistant', content: prev.answer_text }],
  [{ role: 'user', content: 'FACT-GATE: these claims in your draft are NOT supported by the tool results you retrieved: ' + JSON.stringify(verdict.unsupported) + '. Rewrite your answer now. Every name and number must come from your retrieved tool results — re-fetch if you need more data. Anything you cannot support, drop or say plainly you do not have it. Do not mention this check.' }],
);
return [{ json: {
  done: false, to: prev.to, preload: prev.preload || '', system: prev.system, tools: prev.tools, messages: messages,
  iter: Math.max(prev.iter, 1), max_iter: prev.max_iter + 2,
  in_tok: prev.in_tok, out_tok: prev.out_tok, cache_w: prev.cache_w, cache_r: prev.cache_r,
  calls: prev.calls, t0: prev.t0, gate_attempts: 1, regen: true,
} }];
