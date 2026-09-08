// scripts/olivia_loop/public_gate.js  (#169)
// The deterministic half of the Public Gate. Pure functions, no I/O, CommonJS so the
// SAME text runs under node --test here and inside the n8n code nodes (apply_169_public_gate.py
// embeds this file verbatim between the markers below).
//
// WHO A PUBLIC ANSWER IS FOR (#176, Andy 2026-09-08 — this REPLACES the #169 reading, and corrects
// the first #176 reading below it):
// "public means all members, but not people outside the MDS; restricted means this content is
// restricted to some members. Facebook is open source; it's public by definition. The only
// restricted sources are some WA chats (you should know it) and some videos (we have the spine with
// restriction rules)."
//   OPEN       = open to EVERY member: Facebook group posts and comments, WhatsApp messages and
//                digests from a chat that is not verification_required, transcripts and videos of a
//                recording whose access_restriction is 'public', published partner listings and
//                their pages, events and their pages. Named, quoted and linked freely.
//   RESTRICTED = restricted to SOME members: WhatsApp in a verification_required chat, transcripts
//                and videos of a 'restricted' recording, applications. They may INFORM an answer; no
//                exact detail crosses into it — no names, no verbatim quotes, no specifics.
// Two readings were wrong before this one. #169 read "public" as WORLD-public ("safe to leave MDS")
// and closed the Facebook group; that was the wrong AUDIENCE. The first #176 pass fixed the audience
// but kept a SOURCE-TYPE allowlist, so it closed all 18,363 WhatsApp rows and all 13,507 transcript
// rows wholesale — including twelve open chats and 8,022 chunks of recordings any member can open.
// The line is per ROW, off the restriction spine the database already carries. What is unchanged
// through all three: a name survives only when an OPEN row of the turn contains it, and unknown is
// still closed.
//
// Nothing in this file decides WHICH sources are open — digest.public_gate_classify() does, and this
// module keys everything off the class map it returns. That is why neither correction needed a
// change to the matching logic (see scripts/sql/20260908_public_gate_classify_restriction_spine_176.sql).
// --- PUBLIC_GATE_BEGIN ---
const ROLE_PHRASES = ['a member', 'a seller in the community', 'one of the speakers'];

// Capitalised English words that are also common first names — the first-name follow-up
// pass in redact() skips these so it doesn't mangle an unrelated sentence-initial word.
// 'First'/'Last' are here for the same reason and a different cause (#176, staging probe of q6): the
// live index carried a placeholder row literally called "first last", whose first token then masked
// the ordinary word — "you're not the first to get one of these letters" published as "you're not
// the they to get one of these letters". That row and 63 others are now excluded at the source
// (scripts/sql/20260908_public_gate_name_index_junk_176.sql: a row carrying a digit or an '@', a
// 'test'/'testing' token, or an English function word as its first token). These two stay here
// anyway — the index is rebuilt from three live tables and the next placeholder is one typo away.
const COMMON_WORD_FIRST_NAMES = new Set([
  'First', 'Last',
  // 'Claude' is a real member first name AND the name of the model that writes these answers, so the
  // lone-token pass turned "running two businesses via Claude + ClickUp" into "via they + ClickUp"
  // (staging probe of q10). The full name still masks; only the bare token is exempt, exactly as it
  // is for Mark, Grace, Frank, Will and the rest of this list.
  'Claude',
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
// (NFC + the same INVISIBLE_RE) plus the whitespace tidying below. Used at the top of every function
// that matches names or links against the answer text, and the normalised text is what gets
// returned/searched — never a copy kept on the side, so a downstream check can't accidentally look
// at the un-normalised original.
//
// STRUCTURE IS PART OF THE ANSWER (#176 D5, Andy 2026-09-08: "The main issue is how we present data.
// You can post such a huge chunk of text w/o any breaks, w/o any links."). This function used to end
// `.replace(/\s+/g, ' ')` — every run of whitespace, NEWLINES INCLUDED, collapsed to one space — and
// because the normalised text is what gets RETURNED, that collapse was published. Measured on
// staging execution 139221 (the q10 probe): `Public Redact` was handed a 1,832-character draft
// carrying 16 newlines — a paragraph break after the lead-in, one bullet per line, each link on its
// own line — and returned 1,827 characters with ZERO newlines and its five bullets run together
// inline behind " • ". `Public Smooth (Claude)` was innocent: it received a flat draft and returned
// a flat one; `Public Verify` and `Format Web` passed it through unchanged. The same collapse shows
// on every public turn of that eval (139183: 23 newlines in, 0 out; 139171: 26 in, 0 out) while the
// ungated answer to the identical question kept its 20.
//
// What the collapse was actually FOR is unchanged: a stray formatting artifact between the tokens of
// a name must not reopen the R1 gap. Horizontal runs still collapse to one space, so nothing changes
// WITHIN a line; a line break between two tokens of a name was never at risk in the first place,
// because every name pattern joins its tokens with NAME_SEP (`[\s\-]+`), which matches a newline
// like any other space. Line structure now survives: CR/LF and the Unicode line/paragraph separators
// normalise to \n, no space is left hugging a break, and three or more breaks in a row collapse to
// the one blank line that makes a paragraph (tidyBreaks, shared with the shape-repair pass below).
const NEWLINE_RE = /\r\n?|\u2028|\u2029/g;
const H_SPACE_RE = /[^\S\n]+/g;
function tidyBreaks(s) { return String(s == null ? '' : s).replace(/\n{3,}/g, '\n\n'); }
function normText(s) {
  return tidyBreaks(String(s == null ? '' : s).normalize('NFC').replace(INVISIBLE_RE, '')
    .replace(NEWLINE_RE, '\n').replace(H_SPACE_RE, ' ').replace(/ ?\n ?/g, '\n'));
}
function nameTokens(nm) { return normName(nm).trim().split(/[\s\-]+/).filter(Boolean); }

// THE PRE-FILTER THAT KEEPS THIS AFFORDABLE (#176 D4). The q9 probe came back
// {"message":"Error in workflow"}; the prod execution said `Task execution aborted because runner
// became unresponsive`, lastNodeExecuted `Public Redact`. Measured on the real index: backedNames()
// ran 78 evidence rows x 5,384 names = 420,000 regex compiles and tests, 19.7 SECONDS of local CPU,
// and n8n's sandboxed Code-node runner is roughly 15x slower again; redact() and leftoverNames()
// built a pattern for every name whose first token appeared as a SUBSTRING anywhere in the draft
// ("Ana" inside "management", "Sam" inside "same") — 374 of them on a 2.4KB answer.
//
// Every pattern this module builds from a name — nameSource(), firstNameSource(), and the exact
// literal backedNames() uses — is bounded by NB_L on the left and NB_R on the right, and joins its
// tokens with NAME_SEP (`[\s\-]+`). So each alphanumeric run of the name begins right after a
// non-alphanumeric character in the text and ends right before one: it is a MAXIMAL alphanumeric
// run of the text. Requiring every run of the name to be present in the text's own run set is
// therefore a NECESSARY condition for the pattern to match — the filter can skip work, never a
// match. On the same q9 turn it takes the candidate set from 374 to 17 and the sweep from ~800ms to
// ~30ms; backedNames drops from 19.7s to well under a tenth of a second.
const ALNUM_RUN_RE = /[\p{L}\p{N}]+/gu;
function runSet(text) {
  const out = new Set();
  const m = String(text == null ? '' : text).match(ALNUM_RUN_RE);
  if (m) for (const t of m) out.add(t.toLowerCase());
  return out;
}
function nameRuns(nm) {
  const m = normName(nm).match(ALNUM_RUN_RE);
  return m ? m.map(s => s.toLowerCase()) : [];
}
function runsPresent(runs, set) {
  for (const r of runs) if (!set.has(r)) return false;
  return true;
}
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
//
// #176 D1 follow-up (staging exec 138940): "shared with a BACKED name" used to mean shared with its
// FIRST token only, so an unbacked "Meredith Hudson" still masked the token "Meredith" wherever it
// stood — including inside the backed "Daniel Meredith", which published as "Daniel they tried ~15
// tools". A backed name is one an open group post entitles us to print; mangling its surname
// defeats the whole point of backing it. Every token of a backed name is protected now, not just the
// first. leftoverNames() shares this function, so the two passes still cannot disagree, and the FULL
// unbacked name ("Meredith Hudson") is still masked by the full-name pass either way.
function closedFirstNames(names, backed) {
  const backedFirst = new Set();
  for (const b of backed) for (const t of nameTokens(b)) backedFirst.add(t.toLowerCase());
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
//
// ...and it must be LONE (#176 D1, staging probes of q9/q10). The pass fired on the token wherever it
// stood, so an unbacked index name masked the first name of a DIFFERENT person: "Antonio Sanchez" in
// the index published "they Bindi echoed this" over Antonio Bindi, and "Mayank Yadav 23frqw2e4"
// published "they Sharma of Returnstack" over Mayank Sharma. A first name followed by another
// capitalised word is not a lone first name — it is somebody's FULL name, and if that full name were
// an index name the full-name pass above would already have masked it. A person the index does not
// carry is not one this gate redacts anywhere else either (an unindexed speaker's name has always
// published verbatim), so leaving it whole is the consistent reading, and mangling half of it was
// never protecting anyone. A single initial does not count as a surname, so "Sarah C." still masks.
const NOT_A_SURNAME_AHEAD = '(?![\\s\\-]+\\p{Lu}[\\p{L}])';
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

// WHAT KIND OF ROW IS THIS (#176 D3). Not every retrieval tool labels its rows. content_search /
// content_lookup return a `source` column; video_search, partner_lookup, event_lookup* and fb_thread
// do not — they are recognisable only by their shape. q10's public answer reported
// `source_summary {"other": 18}` for exactly that reason, and an unlabelled row could not be keyed,
// so nothing classified and every name was masked. A row we can recognise is MISLABELLED, not
// unknown; a row we cannot is still unknown, and unknown is still closed (rowClass decides that, and
// nothing here hands it a key it did not earn).
function rowSource(r) {
  if (r.source) return String(r.source);
  if (r.partner_url !== undefined || r.web_summary !== undefined || r.web_people !== undefined) return 'partner';
  if (r.video_url !== undefined) return 'video';
  if (r.event_url !== undefined || r.event_name !== undefined) return 'event';
  // fb_thread: kind post|comment alongside a post_id — its rows carry no `source` column at all.
  if (r.post_id !== undefined && (r.kind === 'post' || r.kind === 'comment')) {
    return r.kind === 'post' ? 'fb_post' : 'fb_comment';
  }
  return null;
}

// Collect complete JSON objects out of an array literal starting at s[start] === '['. String- and
// depth-aware, and it stops at whatever is complete: `Answer Seed` hard-caps its preload at 20,000
// characters, so the last row of a RAW MATCHES block is routinely cut in half and JSON.parse of the
// whole array is not an option. A half-written row is dropped, never guessed at.
function scanRowArray(s, start) {
  const out = [];
  let depth = 0, objStart = -1, inStr = false, esc = false, i = start + 1;
  for (; i < s.length; i++) {
    const ch = s[i];
    if (inStr) {
      if (esc) { esc = false; continue; }
      if (ch === '\\') { esc = true; continue; }
      if (ch === '"') inStr = false;
      continue;
    }
    if (ch === '"') { inStr = true; continue; }
    if (ch === '{' || ch === '[') { if (depth === 0 && ch === '{') objStart = i; depth++; continue; }
    /* end of the array */
    if (ch === ']' && depth === 0) break;
    if (ch === '}' || ch === ']') {
      depth--;
      if (depth === 0 && ch === '}' && objStart >= 0) {
        try { out.push(JSON.parse(s.slice(objStart, i + 1))); } catch (e) { /* half a row: drop it */ }
        objStart = -1;
      }
    }
  }
  return out;
}

// THE PRELOAD IS EVIDENCE (#176 D3). The single biggest evidence block of a turn is not a
// tool_result: `Answer Seed` runs a deterministic search before the model does and renders those
// rows into the final user message as TEXT — "PRELOADED EVIDENCE ... RAW MATCHES (40): [ ... ]" and
// "DIGESTS (n): [ ... ]", full content rows with their urls and their `meta.author_name`. The
// extractor only ever read tool_result blocks, so on q10 all forty of them were invisible: the group
// post that answered the question could not classify, its author could not back a name, and its link
// was stripped as unknown. Only these two named markers are parsed — arbitrary prose in the message
// is not scanned for JSON — and every row found goes through the SAME classifier as any other, so
// nothing here loosens the gate.
const PRELOAD_MARKER_RE = /(?:RAW MATCHES|DIGESTS)\s*\(\d+\)\s*:\s*/g;
function preloadRows(text) {
  const s = String(text == null ? '' : text);
  const out = [];
  const re = new RegExp(PRELOAD_MARKER_RE.source, 'g');
  let m;
  while ((m = re.exec(s))) {
    const open = s.indexOf('[', m.index + m[0].length - 1);
    if (open < 0) break;
    // the marker must be immediately followed by the array, not by prose that merely contains one
    if (s.slice(m.index + m[0].length, open).trim() !== '') { re.lastIndex = m.index + m[0].length; continue; }
    for (const r of scanRowArray(s, open)) out.push(r);
    re.lastIndex = open + 1;
  }
  return out;
}

function extractEvidenceRows(messages) {
  const rows = [], urls = new Set(), source_ids = new Set();
  // one row-shaping path, whether the rows arrived as a tool_result or in the preloaded block
  const take = (list) => {
      for (const r of list) {
        if (!r || typeof r !== 'object') continue;
        // `event_url` is what event_lookup* actually names its link (coalesce(app_url, public_page_url)).
        // #176 D3: `video_url` is what video_search names its own, and it was in NO coalesce list, so a
        // library row arrived with url null AND source_id null — keyless, therefore closed, always.
        // rowUrls() catches every other `*_url` shape a tool may grow later.
        const url = r.url || r.public_page_url || r.partner_url || r.link || r.event_url
                    || r.video_url || rowUrls(r)[0] || null;
        const src = rowSource(r);
        let sid = r.source_id != null ? String(r.source_id) : (r.video_id != null ? String(r.video_id) : null);
        // #176 D3: a library row's only id is the one inside its own link. Derived ONLY for a row
        // that carries neither `source` nor `source_id` of its own — i.e. the unlabelled
        // video_search shape. A call_transcript row's `url` is the SAME app.mds.co/videos/<id> link
        // (the recording it was cut from), so a labelled row keeps the id IT was given and is never
        // handed the bare video id instead. That guard used to be load-bearing, because the
        // classifier called every bare video id open; since the restriction-spine correction the two
        // agree by construction (a transcript inherits its recording), so the guard now only keeps
        // the keying honest — a row is classified as the thing it actually is.
        if (sid === null && r.source == null && r.source_id === undefined) {
          if (src === 'video' && typeof r.video_url === 'string') {
            const vid = VIDEO_LINK_RE.exec(r.video_url);
            if (vid) sid = vid[1];
          } else if ((src === 'fb_post' || src === 'fb_comment') && r.post_id != null) {
            sid = String(r.post_id);
          }
        }
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
        rows.push({ source: src, source_id: sid, url: url ? String(url) : null, text,
                    authors: rowAuthors(r) });
      }
  };
  for (const m of Array.isArray(messages) ? messages : []) {
    if (!m || m.role !== 'user') continue;
    if (typeof m.content === 'string') { take(preloadRows(m.content)); continue; }
    if (!Array.isArray(m.content)) continue;
    for (const c of m.content) {
      if (!c) continue;
      if (c.type === 'text') { take(preloadRows(c.text)); continue; }
      if (c.type !== 'tool_result') continue;
      const raw = typeof c.content === 'string' ? c.content : JSON.stringify(c.content);
      const parsed = parseRows(raw);
      if (parsed === null) { rows.push({ source: 'text', source_id: null, url: null, text: raw, authors: [] }); continue; }
      const list = Array.isArray(parsed) ? parsed : (parsed && Array.isArray(parsed.rows) ? parsed.rows : []);
      take(list);
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
  // One pass over the whole corpus first (#176 D4): a name that matches inside ONE haystack has all
  // of its runs in that haystack, hence in the union — so filtering on the union skips no match.
  const union = runSet(haystacks.join('\n'));
  const cands = [];
  for (const n of names) {
    const nm = String((n && n.name != null ? n.name : n) || '').trim();
    if (!nm || backed.has(nm)) continue;
    const runs = nameRuns(nm);
    if (!runsPresent(runs, union)) continue;
    cands.push({ nm: nm, runs: runs, re: boundedRe(escapeRe(normName(nm)), 'i') });
  }
  if (!cands.length) return backed;
  for (const hay of haystacks) {
    // ...and matching stays STRICTLY PER ROW: a name is backed only when one open row carries the
    // whole of it. Half a name in one row and half in another backs nothing.
    const rs = runSet(hay);
    for (const c of cands) {
      if (backed.has(c.nm) || !runsPresent(c.runs, rs)) continue;
      if (c.re.test(hay)) backed.add(c.nm);
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
// closed. Under #176 'public' means OPEN TO EVERY MEMBER, so a Facebook group post link is one we
// WANT in the answer (Andy: "3 fb links that we can share"), and so is the app link of a recording
// whose access_restriction is 'public'. What still goes is a link into something only SOME members
// can open: a verification_required WhatsApp chat, or a 'restricted' recording.
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
  // `runs` is only a cheap pre-filter: EVERY alphanumeric run of the index name must appear as a whole
  // run of the draft before the real (much more expensive) pattern is built at all — a necessary
  // condition for the bounded pattern to match, so it skips work and never a match (#176 D4; it used
  // to be a substring test on the first token alone, which let "Ana" through on "management"). 5,394
  // index rows run through this on every public turn. Re-taken after each replacement so it never
  // goes stale.
  let runs = runSet(text);
  const sorted = [...names].map(n => String(n.name || '').trim()).filter(Boolean).sort((a, b) => b.length - a.length);
  for (const full of sorted) {
    if (backed.has(full)) continue;
    const toks = nameTokens(full);
    if (!toks.length || !runsPresent(nameRuns(full), runs)) continue;
    // No 'i' here (#169 review R2): nameSource() builds its own per-token case alternation
    // (tokenAlt()) precisely because \p{Lu} inside MID_TOKEN would case-fold and stop meaning
    // "uppercase" the moment this pattern carried the flag.
    const re = boundedRe(nameSource(full), 'g');
    if (!re.test(text)) continue;
    const phrase = ROLE_PHRASES[i++ % ROLE_PHRASES.length];
    text = text.replace(re, phrase);
    runs = runSet(text);
    removed.push(full);
  }
  // First-name-only mentions — "Sarah shared a bundling tip", "Later JONATHAN added Y" — over the first
  // names of ALL unbacked index names, not only the ones whose full name happened to appear in this
  // draft (#169 review I1). A possessive is absorbed so the sentence stays readable ("Sarah's margins"
  // -> "their margins"), and the index name is recorded as removed so the GATED strip counts it.
  for (const ent of closedFirstNames(names, backed).values()) {
    if (!runs.has(ent.first.toLowerCase())) continue;
    const fre = boundedRe(firstNameSource(ent.first), 'g', "(['’]s)?" + NOT_A_SURNAME_AHEAD);
    if (!fre.test(text)) continue;
    text = text.replace(fre, (m, poss) => (poss ? 'their' : 'they'));
    runs = runSet(text);
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
  const runs = runSet(hay);
  const out = [], seen = new Set();
  for (const n of names) {
    const nm = String((n && n.name != null ? n.name : n) || '').trim();
    if (!nm || seen.has(nm) || backed.has(nm)) continue;
    const toks = nameTokens(nm);
    if (!toks.length || !runsPresent(nameRuns(nm), runs)) continue;
    // No 'i' here either (#169 review R2) — same reason as redact()'s call above.
    if (boundedRe(nameSource(nm), '').test(hay)) { seen.add(nm); out.push(nm); }
  }
  // A first name the gate would have masked on its own must not survive the smoother either: publishing
  // a partial it could not mask is the same leak as publishing the whole name (#169 review I1). Same
  // eligibility and same casings as redact(), so this never refuses a form redact() deliberately kept.
  for (const ent of closedFirstNames(names, backed).values()) {
    if (seen.has(ent.full) || !runs.has(ent.first.toLowerCase())) continue;
    if (boundedRe(firstNameSource(ent.first), '', "(['’]s)?" + NOT_A_SURNAME_AHEAD).test(hay)) { seen.add(ent.full); out.push(ent.full); }
  }
  return out;
}
// REPAIR, DON'T REFUSE (#176 D2). Until now a closed-source name or an unknown link that survived
// the smoother made the whole turn fail closed: the reader got "I could not produce a public-safe
// version of this answer" and nothing else. The 2026-09-08 eval caught q6 and q1 doing exactly that
// while their own notes listed five open group and partner sources. That is not the bar — Andy:
// "It should be like staging, but it dropped some details from gated sources. still answers, but no
// details and all the info from public sources." A leftover is a smoothing defect, not a reason to
// throw the answer away: mask the name with the same role-phrase pass, strip the link, KEEP the
// answer, and say so in the notes.
//
// The invariant is untouched — a closed-room name or link may never reach the published text. That
// is why this function RE-CHECKS its own output (`leftover`, `leftover_links`): the caller refuses
// only when a second pass still finds one, or when the repair leaves nothing worth publishing.
//
// `draftUrls` is the set of urls that were in the redacted draft handed to the smoother. A url that
// is not among them is one the smoother INVENTED, and an invented url is never publishable however
// the classifier happens to class it — so it is dropped from the map before the link pass runs.
function repairPublic(text, names, backed, classes, draftUrls) {
  const before = normText(text);
  const cls = {};
  for (const k of Object.keys(classes || {})) cls[k] = classes[k];
  const allowed = new Set((draftUrls || []).map(String));
  for (const u of extractUrls(before)) if (!allowed.has(u)) delete cls[u];
  const lk = redactLinks(before, cls);
  const rd = redact(lk.text, names, backed);
  return { text: rd.text, removed_names: rd.removed, removed_links: lk.removed,
           leftover: leftoverNames(rd.text, names, backed), leftover_links: closedUrls(rd.text, cls) };
}

// What is left to say once the repair has run. A "repaired" answer that is nothing but role phrases
// and [link removed] markers is not an answer, and that — not a single leftover name — is the one
// case the gate still refuses outright, with wording that says so.
function repairedSubstance(text) {
  let t = normText(text).split(LINK_PLACEHOLDER).join(' ');
  for (const p of ROLE_PHRASES) t = t.split(p).join(' ');
  return t.replace(urlsG(), ' ').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
}

// ============================================================================================
// SHAPE: WHAT A REWRITE MAY NOT LOSE (#176 D5, Andy 2026-09-08: "Millie much search from existing
// content, quote when can, justify and send link to the exact source.")
//
// normText() above no longer flattens the draft, so the smoother is now HANDED the shape it should
// keep, and the prompt in apply_169_public_gate.py says in as many words to keep it. This is the
// deterministic half of that pair — the belt to the prompt's braces — and it exists for the same
// reason `Public Verify` already discards a rewrite that dropped a backed name: a polish pass is
// allowed to fix grammar, not to throw away the two things that make an answer checkable, its
// STRUCTURE and its LINKS. Nothing here can loosen the gate: it never introduces a name, and the
// only urls it can put back are ones that were in the redacted draft, i.e. ones redactLinks() had
// already judged open against the class map. Everything it emits is re-checked by the caller.
// ============================================================================================

// A bullet glyph with text before it on the same line belongs on a line of its own. This is the
// exact damage the old flatten left behind — five bullets run together behind " • " on one line of
// staging execution 139221 — and a rewrite can reproduce it from a well-shaped draft too.
const BULLET_GLYPHS = '\\u2022\\u00B7\\u25AA\\u2023\\u2043';
const INLINE_BULLET_RE = new RegExp('([^\\s])[^\\S\\n]+([' + BULLET_GLYPHS + '])[^\\S\\n]+', 'g');
function unflattenBullets(text) {
  return String(text == null ? '' : text).replace(INLINE_BULLET_RE, '$1\n$2 ');
}

// Everything in `shape` that is safe to do to any text at any time: normalise, put inline bullets
// back on their own lines, and leave at most one blank line between paragraphs.
function shapeText(text) { return tidyBreaks(unflattenBullets(normText(text))); }

// The content words of one line, as lowercase runs of 3+ characters with the urls taken out. This is
// how a sentence is recognised across a rewrite: the smoother re-words, but it keeps the nouns.
function anchorTokens(line) {
  const out = new Set();
  const m = String(line == null ? '' : line).replace(urlsG(), ' ').match(ALNUM_RUN_RE);
  if (m) for (const t of m) if (t.length >= 3) out.add(t.toLowerCase());
  return out;
}
// The words that identify the line a link sat on. A link often sits on a line of its own under its
// lead-in ("Full thread:\nhttps://...") so the lines above it are folded in until there is enough to
// match on, stopping at the blank line that ends the paragraph.
const ANCHOR_MIN_TOKENS = 4;
function homeAnchor(lines, i) {
  const toks = anchorTokens(lines[i]);
  for (let k = i - 1; k >= 0 && toks.size < ANCHOR_MIN_TOKENS; k--) {
    if (!lines[k].trim()) break;
    for (const t of anchorTokens(lines[k])) toks.add(t);
  }
  return toks;
}
function anchorOverlap(want, have) {
  if (!want.size) return 0;
  let n = 0;
  for (const t of want) if (have.has(t)) n++;
  return n / want.size;
}

// A link that was in the draft and is not in the rewrite goes back to the sentence it supported —
// "a claim that came from a source carries that source's link, inline, next to the claim". The
// destination line is the one whose content words best match the line the link sat on in the draft;
// below LINK_ANCHOR_MIN the sentence is judged gone rather than re-worded, and the caller is told
// (`missing`) so it can fall back to the pre-rewrite draft instead of guessing a home for it.
const LINK_ANCHOR_MIN = 0.4;
function restoreLinks(before, after) {
  const srcLines = normText(before).split('\n');
  const dstLines = shapeText(after).split('\n');
  const have = shapeText(after);
  const restored = [], missing = [];
  for (let i = 0; i < srcLines.length; i++) {
    for (const u of extractUrls(srcLines[i])) {
      if (have.indexOf(u) >= 0 || dstLines.join('\n').indexOf(u) >= 0) continue;
      const want = homeAnchor(srcLines, i);
      let best = -1, bestScore = 0;
      for (let k = 0; k < dstLines.length; k++) {
        const s = anchorOverlap(want, anchorTokens(dstLines[k]));
        if (s > bestScore) { bestScore = s; best = k; }
      }
      if (best >= 0 && want.size >= 3 && bestScore >= LINK_ANCHOR_MIN) {
        dstLines[best] = dstLines[best].replace(/\s+$/, '') + ' ' + u;
        restored.push(u);
      } else {
        missing.push(u);
      }
    }
  }
  return { text: tidyBreaks(dstLines.join('\n')), restored: restored, missing: missing };
}

// The whole shape pass over a rewrite. `ok` false means a link the draft carried could not be put
// back anywhere honest — the caller then publishes shapeText(before), which is the pre-rewrite
// redacted draft and is already gate-clean.
function repairShape(before, after) {
  const lr = restoreLinks(before, after);
  return { text: lr.text, restored_links: lr.restored, missing_links: lr.missing, ok: lr.missing.length === 0 };
}
// --- PUBLIC_GATE_END ---
// rowClass is exported for the tests only (#176): the n8n nodes inline this whole file, so they call
// it directly. It is what decides a row is restricted, which is what drives `closed_sources` — the
// "From a call recording, paraphrased." line in the notes — so it is worth pinning. Note the note
// text keys off the row's `source` ('wa_message', 'call_transcript'), which the restriction-spine
// correction does not change: only SOME rows of those sources are restricted now, and only those
// reach `closed_sources`, so the wording stays true of every row it actually describes.
module.exports = { ROLE_PHRASES, parseRows, extractEvidenceRows, rowClass, backedNames, redact, leftoverNames,
                   extractUrls, closedUrls, redactLinks, linkDetail, repairPublic, repairedSubstance,
                   normText, tidyBreaks, unflattenBullets, shapeText, restoreLinks, repairShape };
