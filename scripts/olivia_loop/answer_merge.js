// ANSWER MERGE — pairs each tool request (from Answer Parse) with its RPC
// response (from Answer Tool, same item order), appends the assistant turn +
// tool_result turn to the thread, and loops back to Answer Claude.
const reqs = $('Answer Parse').all().map(i => i.json);
const resps = $input.all().map(i => i.json);
const state = reqs[0];
const NL = String.fromCharCode(10);

// Big result sets blow the context budget — cap each tool result's JSON.
const CAP = 14000;
const results = reqs.map((req, i) => {
  let body;
  const r = resps[i];
  if (r === undefined || r === null) {
    body = JSON.stringify({ error: 'tool returned nothing' });
  } else if (r.error || r.message && r.code) {
    body = JSON.stringify({ error: String(r.message || r.error).slice(0, 400) });
  } else {
    try { body = JSON.stringify(r); } catch (e) { body = '"unserializable result"'; }
  }
  if (body.length > CAP) body = body.slice(0, CAP) + ' …[truncated — narrow the query for more]"';
  return { type: 'tool_result', tool_use_id: req.tool_use_id, content: body };
});

const messages = state.messages.concat(
  [{ role: 'assistant', content: state.assistant_content }],
  [{ role: 'user', content: results }],
);

return [{ json: {
  to: state.to,
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
} }];
