// ANSWER PARSE — reads Claude's response; either finalizes the answer or emits
// one item per requested tool call for Answer Tool. State comes from whichever
// of Answer Seed / Answer Merge ran most recently (n8n cycle).
const resp = $input.first().json;
const state = $('Answer Merge').isExecuted ? $('Answer Merge').first().json : $('Answer Seed').first().json;
const usage = resp.usage || {};
const in_tok = (state.in_tok || 0) + (usage.input_tokens || 0);
const out_tok = (state.out_tok || 0) + (usage.output_tokens || 0);
const calls = (state.calls || 0) + 1;
const cache_w = (state.cache_w || 0) + (usage.cache_creation_input_tokens || 0);
const cache_r = (state.cache_r || 0) + (usage.cache_read_input_tokens || 0);

const content = Array.isArray(resp.content) ? resp.content : [];
const textOf = () => content.filter(c => c && c.type === 'text' && c.text).map(c => c.text).join('\n').trim();

// evidence = every tool_result body retrieved THIS turn — what the fact-gate
// checks the final answer against. NEVER cut the tail off: the gate used to see
// evidence sliced to 24K while the draft was written from 36K, so every true claim
// sourced from the truncated tail graded as invention and the gate blocked real
// answers (Xander/TikTok, Meher/Hector — 2026-07-30). Same lesson as Answer Merge:
// keep EVERY block, trim each proportionally to fit the budget.
const EV_BUDGET = 60000;
const evParts = [(state.preload ? 'PRELOADED (deterministic search):' + '\n' + state.preload : '')]
  .filter(Boolean)
  .concat(state.messages
    .filter(m => m && m.role === 'user' && Array.isArray(m.content))
    .flatMap(m => m.content)
    .filter(c => c && c.type === 'tool_result')
    .map(c => String(typeof c.content === 'string' ? c.content : JSON.stringify(c.content))));
let evTotal = evParts.reduce((a, s) => a + s.length, 0);
const evidence = (evTotal <= EV_BUDGET ? evParts
  : evParts.map(s => s.slice(0, Math.max(2000, Math.floor(EV_BUDGET * (s.length / evTotal))))))
  .join('\n---\n');
// UNTRIMMED copy for the deterministic post-filter in Gate Verdict. The trimmed copy is a
// TOKEN budget for Haiku; the post-filter is a STRING check and costs nothing, so it must
// look at everything the model actually saw — a claim sourced from trimmed-away text graded
// as invention and blocked 4 real answers on 2026-07-30 (capability, topics, resources).
const evidence_full = evParts.join('\n---\n');

const finalize = (text) => [{ json: {
  done: true,
  to: state.to,
  content: [{ type: 'text', text: text }],
  answer_text: text,
  evidence: evidence,
  evidence_full: evidence_full,
  gate_attempts: state.gate_attempts || 0,
  preload: state.preload || '',
  system: state.system,
  tools: state.tools,
  messages: state.messages,
  iter: state.iter,
  max_iter: state.max_iter,
  in_tok: in_tok, out_tok: out_tok, cache_w: cache_w, cache_r: cache_r, calls: calls, t0: state.t0,
  metrics: { calls: calls, iters: state.iter, ms: Date.now() - state.t0, in_tok: in_tok, out_tok: out_tok, cache_w: cache_w, cache_r: cache_r },
} }];

// API-level failure surfaced as data (retryOnFail exhausted) — honest fallback.
if (resp.type === 'error' || (!content.length && !resp.stop_reason)) {
  return finalize('Sorry — I could not generate an answer just now.');
}

const toolUses = content.filter(c => c && c.type === 'tool_use');
if (resp.stop_reason === 'tool_use' && toolUses.length && state.iter < state.max_iter) {
  // one item per tool call; each carries the full state so Answer Merge can
  // rebuild the thread whichever item it reads first
  return toolUses.map(tu => ({ json: {
    done: false,
    to: state.to,
    system: state.system,
    tools: state.tools,
    messages: state.messages,
    assistant_content: content,
    iter: state.iter + 1,
    max_iter: state.max_iter,
    in_tok: in_tok,
    out_tok: out_tok,
    cache_w: cache_w,
    cache_r: cache_r,
    calls: calls,
    t0: state.t0,
    preload: state.preload || '',
    gate_attempts: state.gate_attempts || 0,
    tool_use_id: tu.id,
    tool_name: String(tu.name || ''),
    // SECURITY: p_phone is set HERE from the resolved member — the model's
    // schemas have no phone field, and anything it smuggled in is overwritten.
    tool_args: JSON.stringify(Object.assign({}, tu.input || {}, { p_phone: state.to })),
  } }));
}

// end_turn (or max iterations reached — answer with what we have)
const text = textOf();
return finalize(text || 'Sorry — I could not generate an answer just now.');
