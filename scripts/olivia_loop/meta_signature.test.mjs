// Unit tests for #105 — Meta's webhook signature. `node --test meta_signature.test.mjs`
// The leak gate runs this same file, so a case pinned here is pinned on every ship.
//
// Meta signs the RAW REQUEST BYTES with the app secret and sends the result as
// `X-Hub-Signature-256: sha256=<hex>`. The whole point of this module is that it
// verifies those bytes and nothing else. Re-serialising a parsed body produces
// different bytes and will never match — that trap is pinned below and must stay
// pinned, because it is the tempting shortcut when the raw body is awkward to reach.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ms = require('./meta_signature.js');

const SECRET = 'test_app_secret_not_a_real_one';
// Byte-for-byte what a Meta delivery looks like on the wire: no spaces after the
// separators, keys in the order Meta emits them.
const RAW = '{"object":"whatsapp_business_account","entry":[{"id":"1","changes":[{"value":{"messages":[{"from":"15550001111","id":"wamid.ABC","type":"text"}]},"field":"messages"}]}]}';
const sign = (raw, secret = SECRET) => 'sha256=' + createHmac('sha256', secret).update(raw, 'utf8').digest('hex');

test('a genuine Meta delivery verifies', () => {
  const v = ms.verifyMetaSignature({ raw: RAW, signature: sign(RAW), secret: SECRET });
  assert.equal(v.ok, true);
});

test('accepts the raw bytes as a Buffer, which is how they arrive from the webhook', () => {
  const buf = Buffer.from(RAW, 'utf8');
  assert.equal(ms.verifyMetaSignature({ raw: buf, signature: sign(RAW), secret: SECRET }).ok, true);
});

test('one changed byte in the body fails', () => {
  const tampered = RAW.replace('15550001111', '15550002222');
  const v = ms.verifyMetaSignature({ raw: tampered, signature: sign(RAW), secret: SECRET });
  assert.equal(v.ok, false);
  assert.equal(v.reason, 'mismatch');
});

test('a body signed with a different secret fails', () => {
  const v = ms.verifyMetaSignature({ raw: RAW, signature: sign(RAW, 'someone_elses_secret'), secret: SECRET });
  assert.equal(v.ok, false);
  assert.equal(v.reason, 'mismatch');
});

test('a forged post with no signature header at all is refused', () => {
  for (const missing of [undefined, null, '']) {
    const v = ms.verifyMetaSignature({ raw: RAW, signature: missing, secret: SECRET });
    assert.equal(v.ok, false);
    assert.equal(v.reason, 'missing_signature');
  }
});

test('a signature that is not in sha256=<hex> form is refused, and never crashes', () => {
  for (const bad of ['deadbeef', 'sha1=abcd', 'sha256=', 'sha256=nothex!!', 'sha256=' + 'a'.repeat(63)]) {
    const v = ms.verifyMetaSignature({ raw: RAW, signature: bad, secret: SECRET });
    assert.equal(v.ok, false, `should refuse ${bad}`);
    assert.equal(v.reason, 'bad_format');
  }
});

test('an unconfigured secret refuses everything — it never falls open', () => {
  // If the n8n variable is missing we must drop, not wave traffic through. A
  // security check that disables itself when misconfigured is not a check.
  for (const noSecret of [undefined, null, '', '   ']) {
    const v = ms.verifyMetaSignature({ raw: RAW, signature: sign(RAW), secret: noSecret });
    assert.equal(v.ok, false);
    assert.equal(v.reason, 'missing_secret');
  }
});

test('hex case does not matter, but the value does', () => {
  const upper = sign(RAW).toUpperCase().replace('SHA256=', 'sha256=');
  assert.equal(ms.verifyMetaSignature({ raw: RAW, signature: upper, secret: SECRET }).ok, true);
});

test('a re-serialised body does NOT verify — only the original bytes do', () => {
  // The shortcut this pins shut: JSON.stringify(JSON.parse(raw)) is a different
  // byte string whenever Meta used different spacing or key order, so rebuilding
  // the body instead of keeping the raw bytes silently breaks every delivery.
  const reserialised = JSON.stringify(JSON.parse(RAW), null, 2);
  assert.notEqual(reserialised, RAW);
  assert.equal(ms.verifyMetaSignature({ raw: reserialised, signature: sign(RAW), secret: SECRET }).ok, false);
});

test('an empty body with a correct signature over that empty body still verifies', () => {
  assert.equal(ms.verifyMetaSignature({ raw: '', signature: sign(''), secret: SECRET }).ok, true);
});

test('a missing body is refused rather than treated as empty', () => {
  const v = ms.verifyMetaSignature({ raw: undefined, signature: sign(''), secret: SECRET });
  assert.equal(v.ok, false);
  assert.equal(v.reason, 'missing_body');
});

test('the header can be read case-insensitively, as Node lowercases some and not others', () => {
  const headers = { 'X-Hub-Signature-256': sign(RAW), 'content-type': 'application/json' };
  assert.equal(ms.signatureFromHeaders(headers), sign(RAW));
  assert.equal(ms.signatureFromHeaders({ 'x-hub-signature-256': sign(RAW) }), sign(RAW));
  assert.equal(ms.signatureFromHeaders({}), null);
  assert.equal(ms.signatureFromHeaders(null), null);
});
