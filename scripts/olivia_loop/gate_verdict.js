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
if (verdict.verdict === 'pass' || !(verdict.unsupported || []).length) {
  return finalize(prev.answer_text, { gate: 'pass' });
}
if ((prev.gate_attempts || 0) >= 1) {
  return finalize("I looked into that, but I couldn't verify enough of the details against MDS data to give you a solid answer — I'd rather say that than guess. If you can narrow it down, I'll check again.", { gate: 'blocked', gate_claims: verdict.unsupported });
}
// one regeneration with the unsupported claims named
const messages = prev.messages.concat(
  [{ role: 'assistant', content: prev.answer_text }],
  [{ role: 'user', content: 'FACT-GATE: these claims in your draft are NOT supported by the tool results you retrieved: ' + JSON.stringify(verdict.unsupported) + '. Rewrite your answer now. Every name and number must come from your retrieved tool results — re-fetch if you need more data. Anything you cannot support, drop or say plainly you do not have it. Do not mention this check.' }],
);
return [{ json: {
  done: false, to: prev.to, system: prev.system, tools: prev.tools, messages: messages,
  iter: Math.max(prev.iter, 1), max_iter: prev.max_iter + 2,
  in_tok: prev.in_tok, out_tok: prev.out_tok, cache_w: prev.cache_w, cache_r: prev.cache_r,
  calls: prev.calls, t0: prev.t0, gate_attempts: 1, regen: true,
} }];
