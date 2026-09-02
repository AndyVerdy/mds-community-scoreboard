// #138 — attach the link (and date) the evidence already carried for THIS item.
//
// Not a count rule. An audit over all 602 bank C answers showed every variant of
// "names N items, carries <=1 link" fires on more correct answers than wrong ones
// (65 false alarms vs 51 real at its best setting), because she legitimately lists
// members, chapters and chats that have no url to give. What is checkable per item
// is narrower: the retrieved row this item came from carried a url and the draft
// dropped it. Then we repair instead of regenerating — no second model lap, and a
// good answer can never be clamped.
//
// Silence beats a wrong link: no match, a weak match, or two close matches all
// leave the line exactly as written. A prod audit over 65 real drafts caught this
// rule attaching a video url to an unrelated item when the margin was thin, which
// is why a winner must beat the runner-up by MIN_MARGIN tokens.

// A url ends at whitespace or any JSON/markup delimiter. The evidence is a JSON
// blob, so \S+ swallows `","matched_rank":0.03` and pastes it into the answer
// (seen in prod execs 126991 and 126957 during the audit).
const URL_RE = /https?:\/\/[^\s"'`\\<>)\]}]+/g;
const TRAIL = /[.,;:!?]+$/;
const ITEM_LINE = /^\s*(?:[•\-*]\s+|\d+[.)]\s+)/;
const STOP = /^(The|This|That|These|Those|Here|There|What|When|Where|Which|Want|With|From|Your|About|Also|Just|Only|They|Their|Some|Most|More|Other|Into|Over|Under|Video|Member|Post|Chat|Group|Session)$/;
const MIN_OVERLAP = 2; // two distinctive words in common, or we do nothing
const MIN_MARGIN = 2; // and the winner must beat the runner-up by two

function tokensOf(s) {
  const words = String(s).match(/\b[A-Z][A-Za-z0-9'’&-]{3,}\b/g) || [];
  const out = new Set();
  for (const w of words) if (!STOP.test(w)) out.add(w.toLowerCase());
  return out;
}

function overlap(a, b) {
  let n = 0;
  for (const t of a) if (b.has(t)) n++;
  return n;
}

// A row is what the retrieval returned: one object with its own identity fields.
// Real evidence is JSON, so parse it — matching on a text window swept names out
// of a neighbouring post's BODY and attached two wrong links in the prod audit
// (exec 126957: a Summit line-up announcement naming half the speakers). Only
// identity fields are matched; a body is never identity.
// WHO WROTE a row is not WHAT IT IS. author_name / post_author / sender are
// excluded on purpose: a WhatsApp message with title:null carried
// author_name + post_author both "Brandon Himmel", which cleared the two-token
// bar with no runner-up and lent its permalink to an unrelated Brandon Himmel
// quote — the wrong link that reached prod on 2026-09-02 (exec 127539) and
// forced a rollback. A person is identity only where the person IS the row: a
// member profile, a speaker on a video.
const IDENT_KEYS = /^(title|name|full_name|display_name|speaker|speakers|speaker_names|chat|chat_name|event|event_name|partner|partner_name|member|member_name|question|topic)$/i;
const URL_KEYS = /^(url|link|video_url|permalink|page_url|profile_url)$/i;
const DATE_KEYS = /^(published_at|occurred_at|date|created_at|starts_on|posted_at)$/i;

function identText(obj, depth) {
  let out = "";
  for (const k of Object.keys(obj || {})) {
    const v = obj[k];
    if (v && typeof v === "object" && !Array.isArray(v) && (depth || 0) < 2) {
      out += " " + identText(v, (depth || 0) + 1);
    } else if (typeof v === "string" && IDENT_KEYS.test(k)) {
      out += " " + v.slice(0, 200);
    }
  }
  return out;
}

function dateOf(obj, depth) {
  for (const k of Object.keys(obj || {})) {
    const v = obj[k];
    if (typeof v === "string" && DATE_KEYS.test(k)) {
      const d = v.match(/\d{4}-\d{2}-\d{2}/);
      if (d) return d[0];
    }
    if (v && typeof v === "object" && !Array.isArray(v) && (depth || 0) < 2) {
      const nested = dateOf(v, (depth || 0) + 1);
      if (nested) return nested;
    }
  }
  return null;
}

function urlOf(obj, depth) {
  for (const k of Object.keys(obj || {})) {
    const v = obj[k];
    if (typeof v === "string" && URL_KEYS.test(k) && /^https?:\/\//.test(v)) return v.replace(TRAIL, "");
    if (v && typeof v === "object" && !Array.isArray(v) && (depth || 0) < 2) {
      const nested = urlOf(v, (depth || 0) + 1);
      if (nested) return nested;
    }
  }
  return null;
}

// Pull every top-level {...} out of the blob, whatever wraps them.
function jsonObjects(ev) {
  const out = [];
  let depth = 0, start = -1, inStr = false, esc = false;
  for (let i = 0; i < ev.length; i++) {
    const c = ev[i];
    if (inStr) {
      if (esc) esc = false;
      else if (c === "\\") esc = true;
      else if (c === '"') inStr = false;
      continue;
    }
    if (c === '"') { inStr = true; continue; }
    if (c === "{") { if (depth === 0) start = i; depth++; continue; }
    if (c === "}") {
      depth--;
      if (depth === 0 && start >= 0) {
        try { out.push(JSON.parse(ev.slice(start, i + 1))); } catch (e) { /* not a row */ }
        start = -1;
      }
      if (depth < 0) depth = 0;
    }
  }
  return out;
}

function rowsOf(evidenceRaw) {
  const ev = String(evidenceRaw || "");
  const rows = [];
  for (const obj of jsonObjects(ev)) {
    const url = urlOf(obj);
    if (!url) continue;
    const ident = identText(obj);
    rows.push({ url, tokens: tokensOf(ident), context: ident, date: dateOf(obj) });
  }
  // No window fallback. Matching a text window around a url attached
  // https://kos.com — a url sitting inside Zenon Labs' own description — to
  // that partner as though it were their page (exec 127638). A row lends a link
  // only from an explicit link FIELD; evidence without one simply has no link
  // to give, and the answer keeps none.
  return rows;
}

const dateIn = (s) => (String(s).match(/\b\d{4}-\d{2}-\d{2}\b/) || [])[0] || null;

/**
 * @param {string} draftText   the answer as drafted
 * @param {string} evidenceRaw the evidence the loop retrieved
 * @param {{withDate?: boolean}} [opts]
 * @returns {{text: string, repaired: number, items: Array<{line: number, url: string}>}}
 */
function repairLinks(draftText, evidenceRaw, opts) {
  const withDate = !!(opts && opts.withDate);
  const NL = String.fromCharCode(10);
  const rows = rowsOf(evidenceRaw);
  const draft = String(draftText || "");
  const used = new Set((draft.match(URL_RE) || []).map((u) => u.replace(TRAIL, "")));
  const items = [];
  let repaired = 0;

  const text = draft
    .split(NL)
    .map((line, idx) => {
      if (!ITEM_LINE.test(line)) return line; // prose is never touched
      if ((line.match(URL_RE) || []).length) return line; // already carries one

      const t = tokensOf(line);
      if (t.size === 0) return line;

      const scored = rows
        .map((r) => ({ r, score: overlap(t, r.tokens) }))
        .filter((x) => x.score >= MIN_OVERLAP)
        .sort((a, b) => b.score - a.score);

      if (!scored.length) return line; // this item is not in the evidence
      if (scored.length > 1 && scored[0].score - scored[1].score < MIN_MARGIN) return line; // too close to call
      const hit = scored[0].r;
      if (used.has(hit.url)) return line; // that link is already elsewhere in the answer

      used.add(hit.url);
      repaired++;
      items.push({ line: idx, url: hit.url });
      const d = withDate ? (hit.date || dateIn(hit.context)) : null;
      return line + (d && !line.includes(d) ? " (" + d + ")" : "") + " " + hit.url;
    })
    .join(NL);

  return { text, repaired, items };
}

module.exports = { repairLinks };
