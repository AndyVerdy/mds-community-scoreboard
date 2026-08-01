// ANSWER MERGE — pairs each tool request (from Answer Parse) with its RPC
// response (from Answer Tool, same item order), appends the assistant turn +
// tool_result turn to the thread, and loops back to Answer Claude.
const reqs = $('Answer Parse').all().map(i => i.json);
const resps = $input.all().map(i => i.json);
const state = reqs[0];
const NL = String.fromCharCode(10);

// Big result sets blow the context budget. NEVER blunt-truncate — that silently
// deletes the tail rows and the model answers from half the evidence (prod's
// "280-char truncation" bug, re-learned here as 25 answer-misses on run 3).
// Instead: keep EVERY row, trim each row's long text fields by rank tier.
const CAP = 26000;
const TIER = (i) => (i < 5 ? 1600 : i < 15 ? 500 : 220);
const compact = (val) => {
  if (!Array.isArray(val)) return val;
  return val.map((row, i) => {
    if (!row || typeof row !== 'object') return row;
    const out = {};
    for (const k of Object.keys(row)) {
      const v = row[k];
      if (typeof v === 'string' && v.length > TIER(i)) out[k] = v.slice(0, TIER(i)) + '…';
      else out[k] = v;
    }
    return out;
  });
};
const results = reqs.map((req, i) => {
  let body;
  let r = resps[i];
  // fullResponse mode: the RPC's whole array arrives as ONE item's body — never
  // split into per-row items (splitting mispaired requests to stray rows and
  // silently dropped everything past row 1; the great needle-denial bug).
  if (r && typeof r === 'object' && 'body' in r && ('statusCode' in r || 'headers' in r)) r = r.body;
  if (r === undefined || r === null) {
    body = JSON.stringify({ error: 'tool returned nothing' });
  } else if (r.error || r.message && r.code) {
    body = JSON.stringify({ error: String(r.message || r.error).slice(0, 400) });
  } else {
    try { body = JSON.stringify(compact(r)); } catch (e) { body = '"unserializable result"'; }
  }
  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]"';
  return { type: 'tool_result', tool_use_id: req.tool_use_id, content: body };
});

// move the message-level cache breakpoint to the NEWEST tool_result message so
// each iteration reuses everything before it (4-breakpoint budget: tools, system,
// one moving message mark).
const stripped = state.messages.map(msg => {
  if (!Array.isArray(msg.content)) return msg;
  return { role: msg.role, content: msg.content.map(c => {
    if (c && c.cache_control) { const d = Object.assign({}, c); delete d.cache_control; return d; }
    return c;
  }) };
});
if (results.length) results[results.length - 1] = Object.assign({}, results[results.length - 1], { cache_control: { type: 'ephemeral' } });
const messages = stripped.concat(
  [{ role: 'assistant', content: state.assistant_content }],
  [{ role: 'user', content: results }],
);

return [{ json: {
  to: state.to,
  preload: state.preload || '',
  system: state.system,
  tools: state.tools,
  messages: messages,
  iter: state.iter,
  max_iter: state.max_iter,
  in_tok: state.in_tok,
  out_tok: state.out_tok,
  cache_w: state.cache_w,
  cache_r: state.cache_r,
  calls: state.calls,
  t0: state.t0,
  sources_used: state.sources_used || [],
} }];
