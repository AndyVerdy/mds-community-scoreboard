// ANSWER SEED — entry of the #21 answering loop (staging). Builds the state the
// loop threads through: full conversation as real messages, the gated RPCs as
// tools, one system prompt. The router's lane cascade is NOT consulted — the
// model decides what to fetch and may look again when a result comes back thin.
// SECURITY: p_phone is injected by Answer Parse from state.to — the tool schemas
// below deliberately have no phone/member-id parameter the model could set.
const plan = $('Plan Request').first().json;
const mem = $('Resolve Member').first().json;
const NL = String.fromCharCode(10);

// ---- conversation: last 24h turns, cut at reset, chronological, capped ----
let rows = [];
try { rows = $('Load Recent Turns').all().map(i => i.json).filter(r => r && r.role && r.text); } catch (e) {}
const cut = rows.findIndex(r => r.route === 'reset'); // rows arrive newest-first
if (cut >= 0) rows = rows.slice(0, cut);
rows = rows.slice(0, 16).reverse();
const clip = (s, n) => { s = String(s); return s.length > n ? s.slice(0, n) + '…' : s; };
const msgs = [];
for (const r of rows) {
  const role = r.role === 'member' ? 'user' : 'assistant';
  const text = clip(r.text, 1500);
  if (msgs.length && msgs[msgs.length - 1].role === role) {
    msgs[msgs.length - 1].content += NL + NL + text; // API needs alternating roles
  } else {
    msgs.push({ role: role, content: text });
  }
}
const current = String(plan.text || mem.text || '').trim() || '(empty message)';
if (msgs.length && msgs[msgs.length - 1].role === 'user') {
  msgs[msgs.length - 1].content += NL + NL + current;
} else {
  msgs.push({ role: 'user', content: current });
}

// ---- tools: the gated RPCs, phone-less schemas ----
const S = (props, req) => ({ type: 'object', properties: props, required: req || [] });
const arr = (d) => ({ type: 'array', items: { type: 'string' }, description: d });
const str = (d) => ({ type: 'string', description: d });
const num = (d) => ({ type: 'integer', description: d });
const boo = (d) => ({ type: 'boolean', description: d });
const tools = [
  { name: 'content_search', description: 'Search WhatsApp messages, chat digests, Facebook posts and comments. Sources: wa_message, wa_digest, fb_post, fb_comment. Terms are OR-matched words/phrases. Use p_author to scope to one person’s items (exact-ish name), and ALSO try the name as a term — non-posters appear only in others’ text. Returns text, author, date, chat/thread link, and for FB posts an image ref usable as [SEND_IMAGE: ref].',
    input_schema: S({ p_terms: arr('search words/phrases, OR-matched'), p_sources: arr('subset of wa_message, wa_digest, fb_post, fb_comment'), p_chat: str('exact chat name to scope to'), p_since: str('YYYY-MM-DD date floor'), p_limit: num('max rows, default 40'), p_author: str('author full name to scope to') }, ['p_terms']) },
  { name: 'content_stats', description: 'COUNT things instead of listing them. p_metric: messages|posts|authors|by_chat|by_author. Use for "how many/most active/count" questions about content.',
    input_schema: S({ p_metric: str('messages | posts | authors | by_chat | by_author'), p_terms: arr('optional topic filter'), p_sources: arr('subset of wa_message, fb_post, fb_comment'), p_since: str('YYYY-MM-DD date floor'), p_limit: num('rows for grouped metrics') }, ['p_metric']) },
  { name: 'fb_catchup', description: 'What happened on Facebook lately — posts ranked by discussion volume, not pure recency.',
    input_schema: S({ p_since: str('YYYY-MM-DD window start'), p_limit: num('max posts, default 30') }) },
  { name: 'fb_thread', description: 'Pull ONE Facebook thread in full: the post plus up to 60 replies. Find it by author, topic terms, or exact post id.',
    input_schema: S({ p_author: str('post author name'), p_terms: arr('topic words'), p_post_id: str('exact FB post id'), p_limit_comments: num('max replies, default 60') }) },
  { name: 'community_info', description: 'MDS community facts: active member count, chapters with member counts, community basics. First stop for "how many members/chapters" questions.',
    input_schema: S({}) },
  { name: 'member_match', description: 'Find members BY ATTRIBUTE: city/state/category/revenue-band/channel. Returns names + coarse reasons, never raw values. Use for "who is near X / who sells Y / who is at my level".',
    input_schema: S({ p_dims: arr('dimensions to match on: city, state, category, band, model, channel'), p_city: str('city filter'), p_state: str('state filter'), p_channel: str('sales channel filter'), p_category: str('product category filter'), p_limit: num('max people, default 60') }) },
  { name: 'expertise_search', description: 'Find members by what they KNOW: searches public expertise/about/niche free text with e-commerce synonyms (PPC~ads, sourcing~supplier). Use for "who should I talk to about X".',
    input_schema: S({ p_query: str('the skill/topic') , p_limit: num('max people') }, ['p_query']) },
  { name: 'member_card', description: 'Public profile card for ONE named member: FB link, about, revenue TIER (band only), niche, expertise, hobbies, city. Also their recent posts.',
    input_schema: S({ p_member: str('the member’s name as given') }, ['p_member']) },
  { name: 'member_dossier', description: 'What MDS knows about THE ASKER themselves: their profile, chats, activity, events. Use for "what do you know about me / my application".',
    input_schema: S({}) },
  { name: 'chat_info', description: 'One WhatsApp chat’s purpose, joining requirements, call schedule, zoom link (link only if the asker is a member of it).',
    input_schema: S({ p_chat: str('chat name, e.g. MDS Supplements') }, ['p_chat']) },
  { name: 'chat_recommendations', description: 'Which MDS chats the asker qualifies for but has not joined.',
    input_schema: S({}) },
  { name: 'event_lookup', description: 'Upcoming MDS events (registration-open). Filter by topic terms, city, virtual. p_include_past for history questions.',
    input_schema: S({ p_terms: arr('topic words, e.g. tiktok, dinner'), p_city: str('city filter'), p_virtual: boo('true = virtual only'), p_include_past: boo('include past events'), p_limit: num('max events') }) },
  { name: 'event_who', description: 'Who is going to ONE event: confirmed member attendees (names + city/state) and total count.',
    input_schema: S({ p_event: str('event name words'), p_limit: num('max names') }, ['p_event']) },
  { name: 'event_history', description: 'The ASKER’s own event registrations, past and upcoming, plus their home city.',
    input_schema: S({}) },
  { name: 'partner_lookup', description: 'MDS partner deals directory: search by need/company name, or browse featured. Returns deal, rating, reviews, link.',
    input_schema: S({ p_query: str('need or company name; empty = browse featured'), p_limit: num('max partners') }) },
  { name: 'video_search', description: 'Search the MDS video library (Mogul Calls, Expert Calls, webinars, recordings) by topic, speaker or title. RESTRICTED videos appear with their title but withheld content — say they exist and are restricted, NEVER deny them and NEVER invent their content.',
    input_schema: S({ p_query: str('topic, speaker or title words'), p_limit: num('max videos') }, ['p_query']) },
  { name: 'member_billing', description: 'The ASKER’s own membership/billing status. Self only.',
    input_schema: S({}) },
  { name: 'multi_source', description: 'One-shot fan-out across partners + members + events + chats for broad problems ("launching in EU, what should I do"). Prefer specific tools first.',
    input_schema: S({ p_query: str('the problem in a phrase'), p_terms: arr('topic words'), p_city: str('city if relevant'), p_want: arr('subset of partners, members, events, chats, members_nearby') }) },
];

// Prompt caching: the tool schemas are byte-identical for every member and every
// turn — one breakpoint there gives global reuse; one on system reuses the whole
// prefix across loop iterations and this member's later turns (5-min TTL).
tools[tools.length - 1].cache_control = { type: 'ephemeral' };

// ---- system prompt: proven STYLE block + the loop contract ----
const STYLE = $('Plan Request').first().json.__style_unused || null; // placeholder, replaced below
const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'America/New_York' });
const chatsLine = Array.isArray(plan.chats) && plan.chats.length ? plan.chats.join(', ') : 'none on record';
const SYSTEM = [
  '__STYLE_BLOCK__',
  '',
  'TODAY is ' + today + ' (US Eastern). Anchor every past/upcoming judgment to this date.',
  'MEMBER YOU ARE TALKING TO: ' + (plan.full_name || 'an MDS member') + '. Their WhatsApp chats: ' + chatsLine + '.',
  '',
  'HOW TO WORK (tool loop):',
  '- You have tools over MDS’s real data. For ANY factual question about MDS, members, chats, Facebook, events, partners or the community, CALL A TOOL before answering — your own memory of MDS is not a source.',
  '- LOOK AGAIN: an empty or thin first result is never the answer. Re-try with a different tool, broader terms, another source or a longer window before saying you do not have something. A name missing from profiles still deserves a content_search; a topic missing from chats still deserves a Facebook look.',
  '- COUNT with content_stats or community_info or the length of a tool result you actually retrieved — never estimate, and totalling up a previous answer of yours is allowed and encouraged.',
  '- FOLLOW-UPS: the conversation above is real context. "yes" accepts your last offer — deliver it. "what about X" keeps the previous question shape with X substituted.',
  '- EVERY factual claim comes from a tool result FETCHED THIS TURN. Your own earlier replies above are NOT a source - they may be partial, padded or stale. Before extending, ranking, totalling or reusing ANY list or number that appears in the conversation, re-fetch it from the tool. Inventing an entry to complete a list is the worst possible failure.',
  '- Personal recommendations ("best for me", "closest to me", "for my business") START from member_dossier + event_history. If they do not contain the fact you need (like a home city), ASK for it - never infer it from one event attendance.',
  '- Answers state only what the tool results support, with names/dates/links from those results. Nothing found after honest looking = say so plainly, briefly.',
  '- SEARCH TECHNIQUE (recall beats precision, the data is messy): for a specific fact, comment or post, search the DISTINCTIVE rare words from the question (product names, unusual nouns, numbers) - never the whole sentence. If thin: retry with synonyms, fewer words, or the single rarest term. Person + topic: use p_author AND, separately, the name as a plain term. Always include fb_comment and wa_message in p_sources for single-fact questions - comments hold most specifics. Use p_limit 40+. Minimum TWO differently-phrased searches before concluding something is not there.',
  '- VIDEOS: video_search FIRST for anything about calls, recordings, webinars or the library; try the speaker name and the topic as separate queries. "Latest videos" = a broad query, then sort what returns by date.',
  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',
  '- Keep to ONE final reply. Do not narrate intermediate steps.'
].join(NL);

const state = {
  to: plan.to,
  system: [{ type: 'text', text: SYSTEM, cache_control: { type: 'ephemeral' } }],
  tools: tools,
  messages: msgs,
  iter: 0,
  max_iter: 5,
  in_tok: 0,
  out_tok: 0,
  cache_w: 0,
  cache_r: 0,
  calls: 0,
  t0: Date.now(),
};
return [{ json: state }];
