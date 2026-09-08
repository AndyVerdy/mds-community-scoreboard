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
        rows.push({ source: r.source || null, source_id: sid, url: url ? String(url) : null, text: JSON.stringify(r) });
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
      if (nm && new RegExp('\\b' + escapeRe(nm) + '\\b', 'i').test(text)) backed.add(nm);
    }
  }
  return backed;
}

function redact(draft, names, backed) {
  let text = String(draft || '');
  const removed = [];
  let i = 0;
  const sorted = [...names].map(n => String(n.name || '').trim()).filter(Boolean).sort((a, b) => b.length - a.length);
  for (const full of sorted) {
    if (backed.has(full)) continue;
    const re = new RegExp('\\b' + escapeRe(full) + '\\b', 'gi');
    if (!re.test(text)) continue;
    const phrase = ROLE_PHRASES[i++ % ROLE_PHRASES.length];
    text = text.replace(re, phrase);
    removed.push(full);
    // first-name-only follow-ups ("Later Jonathan added") — only once the full name was present.
    // Conservative: case-sensitive, length >= 4, and skip words that are also common first names
    // (COMMON_WORD_FIRST_NAMES) so an unrelated sentence-initial word isn't mangled.
    const first = full.split(/\s+/)[0];
    if (first.length >= 4 && !COMMON_WORD_FIRST_NAMES.has(first)) {
      text = text.replace(new RegExp('\\b' + escapeRe(first) + '\\b', 'g'), 'they');
    }
  }
  return { text, removed };
}

function leftoverNames(text, names, backed) {
  const hay = String(text || '');
  return [...names].map(n => String(n.name || '').trim()).filter(Boolean)
    .filter(nm => !backed.has(nm) && new RegExp('\\b' + escapeRe(nm) + '\\b', 'i').test(hay));
}
// --- PUBLIC_GATE_END ---
module.exports = { ROLE_PHRASES, parseRows, extractEvidenceRows, backedNames, redact, leftoverNames };
