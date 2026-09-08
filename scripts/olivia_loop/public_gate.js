// scripts/olivia_loop/public_gate.js  (#169)
// The deterministic half of the Public Gate. Pure functions, no I/O, CommonJS so the
// SAME text runs under node --test here and inside the n8n code nodes (apply_169_public_gate.py
// embeds this file verbatim between the markers below).
//
// WHO A PUBLIC ANSWER IS FOR (#176, Andy 2026-09-07 — this REPLACES the #169 reading below):
// "you do realise that Public means MDS members ... the only restiriction for public mode is opt in
// sources", and "the whole idea behind public is that we hiding exact details from restictat chats".
// A Public answer is posted into the members-only MDS Facebook group, so its readers ARE the MDS
// membership. The only thing this gate hides is exact detail that came out of a RESTRICTED ROOM — a
// closed WhatsApp channel or a private call/meeting — because that was not said in the open.
//   OPEN       = anything a member can already see for themselves: the Facebook group's posts and
//                comments, partner listings and their pages, events and their pages, the app's own
//                library. Named, quoted and linked freely.
//   RESTRICTED = closed WhatsApp channels and call/meeting transcripts. They may INFORM an answer;
//                no exact detail crosses into it — no names, no verbatim quotes, no specifics.
// #169 originally read "public" as WORLD-public ("safe to leave MDS") and therefore closed the
// Facebook group too; that was the wrong audience. What is unchanged: a name survives only when an
// OPEN row of the turn contains it, and unknown is still closed.
//
// Nothing in this file decides WHICH sources are open — digest.public_gate_classify() does, and this
// module keys everything off the class map it returns. That is why the correction above needed no
// change to the matching logic (see scripts/sql/20260908_public_gate_classify_member_audience_176.sql).
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
// separator that accepts either (any number of them), and up to two optional middle tokens — an
// initial and/or a middle name — may sit between the first two (#169 review R2 widened this from one
// token and restricted what can fill it; see MID_TOKEN below). A possessive needs nothing: NB_R
// already allows a following "'".
const NAME_SEP = '[\\s\\-]+';
// Review R2 (#169, 2026-09-07 re-review): the middle slot used to accept ANY 1-15-letter word (barred
// only from an explicit connector-word deny-list), so an ordinary sentence word sitting between two
// indexed names — "Mike emailed Ross yesterday." for the indexed "Mike Ross" — was read as a middle
// name and the whole thing masked to "a member yesterday." Fail CLOSED (nobody's real name leaked)
// but broken copy at index scale: 5,394 names, plenty of them two words sharing an ordinary sentence
// with an ordinary verb in between. A middle token must now look like part of a name: a single
// capital letter with an optional period — an initial, "R." or "R" — or a capitalised word that may
// carry an internal apostrophe, hyphen or period ("Robert", "O'Brien", "Jean-Luc").
//
// \p{Lu} only works as an uppercase check on a pattern compiled WITHOUT the `i` flag: under `iu`,
// Unicode property escapes case-fold, so `/\p{Lu}/iu.test('e')` is `true` in V8 — the redact()/
// leftoverNames() `'gi'`/`'i'` flags this pattern used to run under would have silently let "emailed"
// match right back in. nameSource() below therefore builds its OWN case alternation per token
// (tokenAlt()) and runs with no `i` flag at all, so \p{Lu} here means what it says.
const MID_TOKEN = '(?:\\p{Lu}\\.?|\\p{Lu}[\\p{L}\'’.-]*)';
// A token is matched in its NAME-shaped casings only — as indexed, and ALL CAPS — the same idea as
// firstNameSource() further down, and for the same reason: compiling the whole pattern without `i`
// (see MID_TOKEN above) means every literal token needs its own case alternation instead of leaning
// on the caller's flag.
function tokenAlt(tok) {
  const forms = [tok, tok.charAt(0).toUpperCase() + tok.slice(1), tok.toUpperCase()];
  return '(?:' + [...new Set(forms)].map(escapeRe).join('|') + ')';
}
// The other half of C1's 33 rows (#169 C1 addendum, #174 session's independent repro): a boundary fix
// alone does not reach them. An index display name carrying an INVISIBLE code point — "John Pollock"
// with a trailing U+FE0F variation selector, a zero-width space inside it — or an accent stored
// decomposed (NFD) never matches the clean, composed text the model writes, and leftoverNames() does
// not refuse it either: fail OPEN again. Both sides are normalised before matching. Names are
// normalised here (they only ever become patterns); the answer text goes through the identical
// recipe in normText() below (review R1 closed the gap where the answer text itself carried the
// invisible code point — see that comment) — canonical composition changes nothing a reader sees,
// and stripping an invisible code point from a published answer is harmless too.
const INVISIBLE_RE = /[\u00AD\u200B-\u200F\u2060\uFE0F\uFEFF]/g;
function normName(s) { return String(s == null ? '' : s).normalize('NFC').replace(INVISIBLE_RE, ''); }

// Review R1 (#169, 2026-09-07 re-review): the C1 addendum above normalises the INDEX name but never
// the ANSWER text — an invisible code point sitting inside the model's OWN draft (a stray ZWSP a
// paste or a smoothing pass leaves next to a name) still defeats a pattern built from a perfectly
// clean index name: redact() finds nothing to replace and leftoverNames() finds nothing to refuse.
// Fail OPEN, same class as C1, just the other operand. This is the SAME normalisation as normName()
// (NFC + the same INVISIBLE_RE) plus one more step that only makes sense for running text, not a
// single name: runs of whitespace collapse to one space, so a stray formatting artifact between
// tokens can't reopen the same gap. Used at the top of every function that matches names or links
// against the answer text, and the normalised text is what gets returned/searched — never a copy
// kept on the side, so a downstream check can't accidentally look at the un-normalised original.
function normText(s) { return String(s == null ? '' : s).normalize('NFC').replace(INVISIBLE_RE, '').replace(/\s+/g, ' '); }
function nameTokens(nm) { return normName(nm).trim().split(/[\s\-]+/).filter(Boolean); }
function nameSource(nm) {
  const toks = nameTokens(nm);
  if (!toks.length) return null;
  if (toks.length === 1) return tokenAlt(toks[0]);
  // At most two name-shaped middle tokens, joined by a single plain space (#169 review R2).
  const mid = '(?:' + NAME_SEP + MID_TOKEN + '(?: ' + MID_TOKEN + ')?)?';
  return tokenAlt(toks[0]) + mid + NAME_SEP + toks.slice(1).map(tokenAlt).join(NAME_SEP);
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

// WHO WROTE THE ROW (#176 D1). A poster's name is not in the body of what they wrote — it is in the
// row's author/speaker metadata, and `backedNames` only ever searched the body. Measured on the
// 2026-09-08 eval: q10's public answer masked eight members (Daniel Meredith, Dimitri Vorona, Ben
// Anderson, Travis Reese, Jason Pratt, Richard Lo, Ryan Carey, Claude Jeanloz) that the ungated
// answer named freely off the same open group threads, because every one of them was the AUTHOR of
// the post/comment cited, never a name inside it. These keys are collected per row and — for an
// OPEN row only — back a name exactly as the body does.
//
// This is a WHITELIST on purpose, not a sweep of every string on the row. A partner row's
// `fit_reason`/`strength_note` are derived from digest.entity_dossier (aggregated across content,
// transcripts included), so their provenance is not one identifiable open source and they must keep
// backing nothing (see the partner-row comment in extractEvidenceRows below).
const AUTHOR_KEYS = ['author', 'author_name', 'authored_by', 'speaker', 'speakers', 'speaker_names',
                     'member', 'member_name', 'members_named', 'from', 'from_name', 'sender',
                     'sender_name', 'post_author', 'posted_by', 'commenter', 'full_name',
                     'display_name', 'host', 'hosts', 'name'];

function pushWho(out, v, depth) {
  if (v == null) return;
  if (typeof v === 'string') { const s = v.trim(); if (s && s.length < 120) out.push(s); return; }
  if (Array.isArray(v)) { for (const x of v) pushWho(out, x, depth); return; }
  // one level of nesting: web_people/[{name, role}], reviews_sample/[{author, text}]
  if (typeof v === 'object' && depth > 0) {
    for (const k of AUTHOR_KEYS) if (v[k] !== undefined) pushWho(out, v[k], depth - 1);
  }
}

// Every author-shaped value on a row: top-level, one level inside `meta` (content_search puts
// author_name/sender_name/post_author there), and inside the two list-of-people fields an open
// partner listing carries (web_people, reviews_sample).
function rowAuthors(r) {
  const out = [];
  for (const k of AUTHOR_KEYS) if (r[k] !== undefined) pushWho(out, r[k], 1);
  const meta = r.meta;
  if (meta && typeof meta === 'object' && !Array.isArray(meta)) {
    for (const k of AUTHOR_KEYS) if (meta[k] !== undefined) pushWho(out, meta[k], 1);
  }
  for (const k of ['web_people', 'reviews_sample']) if (r[k] !== undefined) pushWho(out, r[k], 1);
  return [...new Set(out)];
}

function extractEvidenceRows(messages) {
  const rows = [], urls = new Set(), source_ids = new Set();
  for (const m of Array.isArray(messages) ? messages : []) {
    if (!m || m.role !== 'user' || !Array.isArray(m.content)) continue;
    for (const c of m.content) {
      if (!c || c.type !== 'tool_result') continue;
      const raw = typeof c.content === 'string' ? c.content : JSON.stringify(c.content);
      const parsed = parseRows(raw);
      if (parsed === null) { rows.push({ source: 'text', source_id: null, url: null, text: raw, authors: [] }); continue; }
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
        // A partner row classifies 'public', but not every field on it comes from the listing.
        // #169 fix round 4 kept only name/web_summary/web_people/web_pricing, on the grounds that
        // those alone are "world-public (crawled from the partner's own site)" — the world-public
        // reading #176 corrects. Partner listings AND THEIR PAGES are open: a member can open the
        // partner page in the app and read its reviews, so reviews_sample (partner_lookup's
        // `rv.sample`) is open evidence too and a reviewer named there may be named in the answer.
        //
        // fit_reason and strength_note still do NOT back a name. They are not part of the listing:
        // both are derived from digest.entity_dossier (refresh_entity_dossiers aggregates across
        // content, transcripts included), so their provenance is not one identifiable open source —
        // and unknown provenance stays closed. They contain no personal names today, which is why
        // excluding them costs nothing; it is the rule that matters, not this month's data.
        const isPartnerRow = r.web_summary !== undefined || r.web_people !== undefined || r.partner_url !== undefined;
        const text = isPartnerRow
          ? JSON.stringify({ name: r.name, web_summary: r.web_summary, web_people: r.web_people,
                             web_pricing: r.web_pricing, reviews_sample: r.reviews_sample })
          : JSON.stringify(r);
        rows.push({ source: r.source || null, source_id: sid, url: url ? String(url) : null, text,
                    authors: rowAuthors(r) });
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

// Every index name that appears verbatim (exact spelling, any case) in any of `haystacks`.
// Split out of backedNames() so the open-row bodies and the open-row author metadata run through
// one matcher, and so the pre-filter that keeps this affordable lives in one place (#176 D4).
function matchNamesIn(haystacks, names, backed) {
  for (const hay of haystacks) {
    for (const n of names) {
      const nm = String((n && n.name != null ? n.name : n) || '').trim();
      if (nm && !backed.has(nm) && boundedRe(escapeRe(normName(nm)), 'i').test(hay)) backed.add(nm);
    }
  }
  return backed;
}

function backedNames(rows, classes, names) {
  const backed = new Set();
  // #176 D1: an OPEN row's own author/speaker metadata backs that name as surely as its body does —
  // the poster's name is never inside the post. A closed row's authors are not searched at all: the
  // `rowClass(...) !== 'public'` skip above this line is the only thing that decides.
  const open = rows.filter(row => rowClass(row, classes) === 'public')
                   .map(row => String(row.text || '').normalize('NFC')
                        + '   ' + (row.authors || []).map(a => normName(a)).join('   '));
  if (!open.length) return backed;
  return matchNamesIn(open, names, backed);
}

// Links (#169 review I2). redact() masked names but never removed a link, and Public Verify only ever
// questioned URLs that were NOT in the redacted draft — so a WhatsApp invite or a restricted
// recording's link that the draft carried was published verbatim, and the GATED strip's "1 link
// removed" counted whatever Haiku happened to drop. A url may be published only when the classifier
// called it 'public'; a url no evidence row ever produced is not in the map at all, and unknown =
// closed. Under #176 'public' means OPEN TO MEMBERS, so a Facebook group post link is one we WANT in
// the answer (Andy: "3 fb links that we can share") — what still goes is a restricted room's link.
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
  let t = normText(text);
  const closed = closedUrls(t, classes);
  /* longest first: a closed url can be the prefix of another closed url */
  for (const u of [...closed].sort((a, b) => b.length - a.length)) t = t.split(u).join(LINK_PLACEHOLDER);
  return { text: t, removed: closed.map(u => ({ kind: 'link', detail: linkDetail(u), replaced_with: LINK_PLACEHOLDER })) };
}

function redact(draft, names, backed) {
  let text = normText(draft);
  const removed = [];
  let i = 0;
  // Every url still here is open to members (redactLinks removed the rest), but its path can carry a name
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
    // No 'i' here (#169 review R2): nameSource() builds its own per-token case alternation
    // (tokenAlt()) precisely because \p{Lu} inside MID_TOKEN would case-fold and stop meaning
    // "uppercase" the moment this pattern carried the flag.
    const re = boundedRe(nameSource(full), 'g');
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
  // URLs are not searched for names: what survives redactLinks() is open to members, so a name in its
  // own path is open too, and redact() deliberately leaves it intact — refusing on it would refuse
  // every turn that cites such a page. A CLOSED url is caught by closedUrls(), not here (#169 I2).
  const hay = normText(text).replace(urlsG(), ' ');
  const low = hay.toLowerCase();
  const out = [], seen = new Set();
  for (const n of names) {
    const nm = String((n && n.name != null ? n.name : n) || '').trim();
    if (!nm || seen.has(nm) || backed.has(nm)) continue;
    const toks = nameTokens(nm);
    if (!toks.length || low.indexOf(toks[0].toLowerCase()) < 0) continue;
    // No 'i' here either (#169 review R2) — same reason as redact()'s call above.
    if (boundedRe(nameSource(nm), '').test(hay)) { seen.add(nm); out.push(nm); }
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
// rowClass is exported for the tests only (#176): the n8n nodes inline this whole file, so they call
// it directly. It is what decides a row is a closed room, which is what drives `closed_sources` —
// the "From a call recording, paraphrased." line in the notes — so it is worth pinning.
module.exports = { ROLE_PHRASES, parseRows, extractEvidenceRows, rowClass, backedNames, redact, leftoverNames,
                   extractUrls, closedUrls, redactLinks, linkDetail };
