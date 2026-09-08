// scripts/olivia_loop/public_gate.js  (#169)
// The deterministic half of the Public Gate. Pure functions, no I/O, CommonJS so the
// SAME text runs under node --test here and inside the n8n code nodes (apply_169_public_gate.py
// embeds this file verbatim between the markers below). Andy, 2026-09-07: a public answer
// may name a person only when a PUBLIC source backs the name. Unknown = closed.
// --- PUBLIC_GATE_BEGIN ---
const ROLE_PHRASES = ['a member', 'a seller in the community', 'one of the speakers'];

// Capitalised English words that are also common first names — the first-name follow-up
// pass in redact() skips these so it doesn't mangle an unrelated sentence-initial word.
const COMMON_WORD_FIRST_NAMES = new Set([
  'Ace', 'Amber', 'Angel', 'April', 'Austin', 'Autumn', 'Baron', 'Bear',
  'Bill', 'Blaze', 'Brook', 'Brooklyn', 'Buck', 'Carolina', 'Carter', 'Chance',
  'Chase', 'Chelsea', 'Chip', 'Christian', 'Cliff', 'Colt', 'Cooper', 'Crystal',
  'Daisy', 'Dakota', 'Dallas', 'Dawn', 'Dean', 'Denver', 'Destiny', 'Drew',
  'Duke', 'Earl', 'Eve', 'Faith', 'Florence', 'Ford', 'Forest', 'Fox',
  'Frank', 'Gene', 'Georgia', 'Grace', 'Grant', 'Harmony', 'Hawk', 'Hazel',
  'Holly', 'Hope', 'Hunter', 'Israel', 'Ivy', 'Jack', 'Jade', 'Jay',
  'Jordan', 'Joy', 'Judge', 'June', 'Justice', 'King', 'Kingston', 'Lance',
  'Legend', 'Liberty', 'Lily', 'London', 'Madison', 'Major', 'Mark', 'Marshall',
  'Mason', 'Maverick', 'Melody', 'Merry', 'Miles', 'Montana', 'Nevada', 'Ocean',
  'Olive', 'Paris', 'Pearl', 'Penny', 'Phoenix', 'Pierce', 'Prince', 'Rain',
  'Raven', 'Rebel', 'Reed', 'Rich', 'River', 'Robin', 'Rocky', 'Rose',
  'Royal', 'Ruby', 'Rusty', 'Sage', 'Savannah', 'Sky', 'Skye', 'Star',
  'Sterling', 'Storm', 'Summer', 'Sunny', 'Sydney', 'Tanner', 'Taylor', 'Victoria',
  'Violet', 'Virginia', 'Wade', 'Walker', 'Will', 'Wolf',
]);

function escapeRe(s) { return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

// Unicode-aware word boundary (#169 review C1). JavaScript's `\b` is defined against ASCII `\w`, so a
// name whose FIRST or LAST character is not [A-Za-z0-9_] — Émile Dupont, Renée Dubé, Ólafur Jónsson —
// has no boundary at that end, and `\b...\b` therefore never matches it anywhere in ordinary prose.
// Measured on the live index: 33 of 5,394 rows. For those members redact() masked nothing AND
// leftoverNames() refused nothing, i.e. the gate failed OPEN and published the full name verbatim.
// `[\p{L}\p{N}_]` under the `u` flag is the same idea over the whole Unicode letter/number space; it
// still refuses to match "Anna Lee" inside "Arianna Leeman".
const NB_L = '(?<![\\p{L}\\p{N}_])';
const NB_R = '(?![\\p{L}\\p{N}_])';
function boundedRe(src, flags, suffix) { return new RegExp(NB_L + src + NB_R + (suffix || ''), flags + 'u'); }

// Variant tolerance (#169 review I1). Only the exact spelling was ever masked, so every ordinary
// conversational variant of an indexed name published: a middle initial ("Jonathan R. Jewett" for the
// indexed "Jonathan Jewett"; 337 index rows have 3+ words), a spelled-out middle name, hyphen-vs-space
// ("Mary Jane Smith" for "Mary-Jane Smith"; 40 hyphenated rows) and doubled spaces. Both sides are
// normalised here: the index name is split on whitespace AND hyphens, the tokens are re-joined with a
// separator that accepts either (any number of them), and ONE optional middle token — an initial or a
// middle name — may sit between the first two. Connector words are barred from that slot so "Anna and
// Lee" is never read as "Anna Lee". A possessive needs nothing: NB_R already allows a following "'".
const NAME_SEP = '[\\s\\-]+';
const MIDDLE_STOP = 'and|or|the|of|in|at|to|for|with|from|by|on';
function nameTokens(nm) { return String(nm == null ? '' : nm).trim().split(/[\s\-]+/).filter(Boolean); }
function nameSource(nm) {
  const toks = nameTokens(nm).map(escapeRe);
  if (!toks.length) return null;
  if (toks.length === 1) return toks[0];
  const mid = '(?:' + NAME_SEP + '(?!(?:' + MIDDLE_STOP + ')' + NB_R + ')\\p{L}{1,15}\\.?)?';
  return toks[0] + mid + NAME_SEP + toks.slice(1).join(NAME_SEP);
}

const COMMON_WORD_FIRST_NAMES_LC = new Set([...COMMON_WORD_FIRST_NAMES].map(s => s.toLowerCase()));

// The first names the gate is allowed to mask on their own (#169 review I1). The old first-name pass
// fired only AFTER the full name had already matched, so "Sarah shared a bundling tip" (index: Sarah
// Chen) published untouched and leftoverNames() did not refuse it either — the common conversational
// form was the one form that leaked. Eligible = the first token of an UNBACKED index name, >= 4 chars,
// not an ordinary English word (COMMON_WORD_FIRST_NAMES), and not shared with a BACKED name: masking
// "Bryce" would garble the "Bryce Alderson" a public source entitles us to print (review M8).
function closedFirstNames(names, backed) {
  const backedFirst = new Set();
  for (const b of backed) { const t = nameTokens(b)[0]; if (t) backedFirst.add(t.toLowerCase()); }
  const out = new Map();
  for (const n of names) {
    const nm = String((n && n.name != null ? n.name : n) || '').trim();
    if (!nm || backed.has(nm)) continue;
    const first = nameTokens(nm)[0] || '';
    const lc = first.toLowerCase();
    if (first.length < 4 || COMMON_WORD_FIRST_NAMES_LC.has(lc) || backedFirst.has(lc)) continue;
    if (!out.has(lc)) out.set(lc, { first: first, full: nm });
  }
  return out;
}

// A lone first name is matched in its NAME-shaped casings only — as indexed, Titlecase, and ALL CAPS
// (the review's proven miss was "Later JONATHAN added Y"). Deliberately NOT the `i` flag: the index is
// 5,394 member/speaker display names, not a curated person list, so a plain case-insensitive single
// token would let one member called e.g. "Prime ..." turn every lowercase "prime" in ordinary copy
// into "they" — and, via leftoverNames, refuse the turn. Two-token full names carry no such risk and
// stay case-insensitive.
function firstNameSource(first) {
  const forms = [first, first.charAt(0).toUpperCase() + first.slice(1), first.toUpperCase()];
  return '(?:' + [...new Set(forms)].map(escapeRe).join('|') + ')';
}

// A video is classified by its 24-hex id, but the retrieval tools hand back only the app link
// (`video_url: "https://app.mds.co/videos/<id>"`), so the id is read back out of any url field.
const VIDEO_LINK_RE = /app\.mds\.co\/videos\/([0-9a-f]{24})/;

// Fix round 2 (#169, exec 137783): a tool_result's `content` is the JSON array of rows FOLLOWED by
// a plain-text coverage note the retrieval layer appends ("... never imply coverage past
// 2026-09-05."), so a bare JSON.parse throws "Extra data" on EVERY real result — every row was
// being discarded and replaced by one unclassifiable {source:'text'} row, which is why `classes`
// came back {} and every member name was masked even when a public row backed it. Retry on the
// substring from the first bracket to the LAST one; the trailing note lives outside it. Returns
// null only when the text genuinely isn't rows — the one case the text fallback may apply to.
function parseRows(raw) {
  const s = String(raw == null ? '' : raw);
  try { return JSON.parse(s); } catch (e) { /* fall through to the slice retry below */ }
  const opens = [s.indexOf('['), s.indexOf('{')].filter(i => i >= 0);
  if (!opens.length) return null;
  const first = Math.min(...opens);
  const last = Math.max(s.lastIndexOf(']'), s.lastIndexOf('}'));
  if (last <= first) return null;
  try { return JSON.parse(s.slice(first, last + 1)); } catch (e) { return null; }
}

// Every url-shaped field on a row, whatever the tool called it (`url`, `link`, `event_url`,
// `video_url`, `public_page_url`, `partner_url`, ...) — all of them are worth classifying.
function rowUrls(row) {
  const out = [];
  for (const k of Object.keys(row)) {
    const v = row[k];
    if (typeof v !== 'string' || !v) continue;
    if (k === 'url' || k === 'link' || k.slice(-4) === '_url') out.push(v);
  }
  return out;
}

function extractEvidenceRows(messages) {
  const rows = [], urls = new Set(), source_ids = new Set();
  for (const m of Array.isArray(messages) ? messages : []) {
    if (!m || m.role !== 'user' || !Array.isArray(m.content)) continue;
    for (const c of m.content) {
      if (!c || c.type !== 'tool_result') continue;
      const raw = typeof c.content === 'string' ? c.content : JSON.stringify(c.content);
      const parsed = parseRows(raw);
      if (parsed === null) { rows.push({ source: 'text', source_id: null, url: null, text: raw }); continue; }
      const list = Array.isArray(parsed) ? parsed : (parsed && Array.isArray(parsed.rows) ? parsed.rows : []);
      for (const r of list) {
        if (!r || typeof r !== 'object') continue;
        // `event_url` is what event_lookup* actually names its link (coalesce(app_url, public_page_url)).
        const url = r.url || r.public_page_url || r.partner_url || r.link || r.event_url || null;
        const sid = r.source_id != null ? String(r.source_id) : (r.video_id != null ? String(r.video_id) : null);
        for (const u of rowUrls(r)) {
          urls.add(u);
          const vid = VIDEO_LINK_RE.exec(u);
          if (vid) source_ids.add(vid[1]);
        }
        if (sid) source_ids.add(sid);
        // Fix round 4 (#169): a partner row classifies 'public' (the directory), but it embeds
        // reviews_sample (MEMBER reviews) and strength_note/fit_reason (member-judgment text) that
        // are not the partner's own public website. Only name/web_summary/web_people/web_pricing
        // are actually world-public (crawled from the partner's own site) — restrict the backing
        // text to those fields for a partner-shaped row; every other row keeps the full-row text.
        const isPartnerRow = r.web_summary !== undefined || r.web_people !== undefined || r.partner_url !== undefined;
        const text = isPartnerRow
          ? JSON.stringify({ name: r.name, web_summary: r.web_summary, web_people: r.web_people, web_pricing: r.web_pricing })
          : JSON.stringify(r);
        rows.push({ source: r.source || null, source_id: sid, url: url ? String(url) : null, text });
      }
    }
  }
  return { rows, urls: [...urls], source_ids: [...source_ids] };
}

// classes: { [url or source_id]: 'public' | 'closed' | 'unknown' }  — anything missing is closed.
function rowClass(row, classes) {
  const byUrl = row.url && classes[row.url];
  const bySid = row.source_id && classes[row.source_id];
  return byUrl === 'public' || bySid === 'public' ? 'public' : 'closed';
}

function backedNames(rows, classes, names) {
  const backed = new Set();
  for (const row of rows) {
    if (rowClass(row, classes) !== 'public') continue;
    const text = String(row.text || '');
    for (const n of names) {
      const nm = String(n.name || '').trim();
      if (nm && boundedRe(escapeRe(nm), 'i').test(text)) backed.add(nm);
    }
  }
  return backed;
}

// Links (#169 review I2). redact() masked names but never removed a link, and Public Verify only ever
// questioned URLs that were NOT in the redacted draft — so a member-only video link
// (app.mds.co/videos/<id>), a private Facebook-group post or a WhatsApp invite that the draft carried
// was published verbatim, and the GATED strip's "1 link removed" counted whatever Haiku happened to
// drop. A url may be published only when the classifier called it 'public' (world-public, per fix
// round 3); a url no evidence row ever produced is not in the map at all, and unknown = closed.
const LINK_PLACEHOLDER = '[link removed]';
const URL_SRC = 'https?://[^\\s<>"\'`]+';
const URL_TAIL_RE = /[)\]}>.,;:!?'"]+$/;
function urlsG() { return new RegExp(URL_SRC, 'g'); }

function extractUrls(text) {
  const out = [], re = urlsG();
  let m;
  while ((m = re.exec(String(text == null ? '' : text)))) {
    const u = m[0].replace(URL_TAIL_RE, '');
    if (u && out.indexOf(u) < 0) out.push(u);
  }
  return out;
}

// host + path only: the scheme, any query string and any fragment are dropped (a query can itself
// carry a token or an email), capped at 80 chars. This string is what the page's GATED strip shows.
function linkDetail(u) {
  const s = String(u).replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('#')[0].split('?')[0];
  return s.length > 80 ? s.slice(0, 80) : s;
}

function closedUrls(text, classes) {
  const cl = classes || {};
  return extractUrls(text).filter(u => cl[u] !== 'public');
}

function redactLinks(text, classes) {
  let t = String(text == null ? '' : text);
  const closed = closedUrls(t, classes);
  /* longest first: a closed url can be the prefix of another closed url */
  for (const u of [...closed].sort((a, b) => b.length - a.length)) t = t.split(u).join(LINK_PLACEHOLDER);
  return { text: t, removed: closed.map(u => ({ kind: 'link', detail: linkDetail(u), replaced_with: LINK_PLACEHOLDER })) };
}

function redact(draft, names, backed) {
  let text = String(draft || '');
  const removed = [];
  let i = 0;
  // Every url still here is world-public (redactLinks removed the rest), but its path can carry a name
  // slug — /speakers/anna-lee — and the name passes below treat '-' as a space. Rewriting it would break
  // a public link AND, because Public Verify re-checks every url against the class map, refuse the turn.
  // Park the urls behind private-use placeholders for the name passes, then put them back verbatim.
  const links = [];
  text = text.replace(urlsG(), m => { links.push(m); return '\uE000L' + (links.length - 1) + '\uE001'; });
  // `low` is only a cheap pre-filter: the first token of the index name must appear SOMEWHERE in the
  // draft before the real (much more expensive) pattern is built at all. 5,394 index rows run through
  // this on every public turn. Re-taken after each replacement so it never goes stale.
  let low = text.toLowerCase();
  const sorted = [...names].map(n => String(n.name || '').trim()).filter(Boolean).sort((a, b) => b.length - a.length);
  for (const full of sorted) {
    if (backed.has(full)) continue;
    const toks = nameTokens(full);
    if (!toks.length || low.indexOf(toks[0].toLowerCase()) < 0) continue;
    const re = boundedRe(nameSource(full), 'gi');
    if (!re.test(text)) continue;
    const phrase = ROLE_PHRASES[i++ % ROLE_PHRASES.length];
    text = text.replace(re, phrase);
    low = text.toLowerCase();
    removed.push(full);
  }
  // First-name-only mentions — "Sarah shared a bundling tip", "Later JONATHAN added Y" — over the first
  // names of ALL unbacked index names, not only the ones whose full name happened to appear in this
  // draft (#169 review I1). A possessive is absorbed so the sentence stays readable ("Sarah's margins"
  // -> "their margins"), and the index name is recorded as removed so the GATED strip counts it.
  for (const ent of closedFirstNames(names, backed).values()) {
    if (low.indexOf(ent.first.toLowerCase()) < 0) continue;
    const fre = boundedRe(firstNameSource(ent.first), 'g', "(['’]s)?");
    if (!fre.test(text)) continue;
    text = text.replace(fre, (m, poss) => (poss ? 'their' : 'they'));
    low = text.toLowerCase();
    if (removed.indexOf(ent.full) < 0) removed.push(ent.full);
  }
  text = text.replace(/\uE000L(\d+)\uE001/g, (m, k) => links[Number(k)]);
  return { text, removed };
}

function leftoverNames(text, names, backed) {
  // URLs are not searched for names: what survives redactLinks() is world-public, so a name in its own
  // path is world-public too, and redact() deliberately leaves it intact — refusing on it would refuse
  // every turn that cites such a page. A CLOSED url is caught by closedUrls(), not here (#169 I2).
  const hay = String(text || '').replace(urlsG(), ' ');
  const low = hay.toLowerCase();
  const out = [], seen = new Set();
  for (const n of names) {
    const nm = String((n && n.name != null ? n.name : n) || '').trim();
    if (!nm || seen.has(nm) || backed.has(nm)) continue;
    const toks = nameTokens(nm);
    if (!toks.length || low.indexOf(toks[0].toLowerCase()) < 0) continue;
    if (boundedRe(nameSource(nm), 'i').test(hay)) { seen.add(nm); out.push(nm); }
  }
  // A first name the gate would have masked on its own must not survive the smoother either: publishing
  // a partial it could not mask is the same leak as publishing the whole name (#169 review I1). Same
  // eligibility and same casings as redact(), so this never refuses a form redact() deliberately kept.
  for (const ent of closedFirstNames(names, backed).values()) {
    if (seen.has(ent.full) || low.indexOf(ent.first.toLowerCase()) < 0) continue;
    if (boundedRe(firstNameSource(ent.first), '').test(hay)) { seen.add(ent.full); out.push(ent.full); }
  }
  return out;
}
// --- PUBLIC_GATE_END ---
module.exports = { ROLE_PHRASES, parseRows, extractEvidenceRows, backedNames, redact, leftoverNames,
                   extractUrls, closedUrls, redactLinks, linkDetail };
