// #105 — verify that an inbound WhatsApp delivery really came from Meta.
//
// Meta computes HMAC-SHA256 over the RAW REQUEST BYTES using the app secret and
// sends it as `X-Hub-Signature-256: sha256=<64 hex>`. This module verifies that and
// nothing else. It is deliberately pure — no n8n globals, no I/O — so the n8n Code
// node and `meta_signature.test.mjs` exercise the same bytes.
//
// Two rules that are load-bearing:
//   1. Verify the ORIGINAL bytes. Re-serialising a parsed body produces a different
//      byte string whenever Meta's spacing or key order differ, and then nothing
//      ever verifies. The webhook's `rawBody` option carries the original bytes in
//      the item's binary property; `json.body` stays parsed for everything
//      downstream, so reading the raw bytes costs no downstream change.
//   2. A missing secret refuses everything. A check that disables itself when it is
//      misconfigured is not a check.

const { createHmac, timingSafeEqual } = require('crypto');

const HEADER = 'x-hub-signature-256';
const HEX64 = /^[0-9a-f]{64}$/i;

// Header names arrive lowercased from n8n's webhook, but not from every caller, so
// look the name up case-insensitively rather than trusting either spelling.
function signatureFromHeaders(headers) {
  if (!headers || typeof headers !== 'object') return null;
  for (const key of Object.keys(headers)) {
    if (key.toLowerCase() === HEADER) {
      const v = headers[key];
      return typeof v === 'string' && v.length ? v : null;
    }
  }
  return null;
}

function verifyMetaSignature({ raw, signature, secret }) {
  if (typeof secret !== 'string' || secret.trim() === '') return { ok: false, reason: 'missing_secret' };
  if (raw === undefined || raw === null) return { ok: false, reason: 'missing_body' };
  if (typeof signature !== 'string' || signature === '') return { ok: false, reason: 'missing_signature' };

  const prefix = 'sha256=';
  if (!signature.startsWith(prefix)) return { ok: false, reason: 'bad_format' };
  const sent = signature.slice(prefix.length);
  if (!HEX64.test(sent)) return { ok: false, reason: 'bad_format' };

  const body = Buffer.isBuffer(raw) ? raw : Buffer.from(String(raw), 'utf8');
  const expected = createHmac('sha256', secret).update(body).digest('hex');

  // Both are 64 lowercase hex characters by construction, so the buffers are always
  // the same length and timingSafeEqual cannot throw.
  const a = Buffer.from(expected, 'utf8');
  const b = Buffer.from(sent.toLowerCase(), 'utf8');
  return timingSafeEqual(a, b) ? { ok: true } : { ok: false, reason: 'mismatch' };
}

module.exports = { verifyMetaSignature, signatureFromHeaders, HEADER };
