# GroupOS incoming-webhook test — Airtable sender

Test harness for ClickUp `86e2bjq8x` (Incoming Webhooks for Address / Tags / Events registered).
Scope for this pass, per Andy: **tags + address only**.

## State — 2026-08-20

**BLOCKED: pre-prod has no ingest web address.**

| Thing | Value |
|---|---|
| Environment | Pre-prod, `https://vl223.groupos-test.co` |
| Integration | `andy` — `6a868ae0bdab79b87256579c` |
| Status | Active · Receiving · Member profile · never called |
| Token | `pat_pub_KghZ…` (PAT "Incoming endpoint: andy", expires Nov 17 2026) |
| Fields allowed | Address, Tags, Events registered |
| **Web address** | **"Not configured for this environment"** |

The app's own Share-setup-details panel says: *"This environment has no web address
configured yet. Contact support before connecting a tool."*

Verified it is genuinely absent, not just unrendered:

- `vl223.groupos-test.co` is a CloudFront distribution that refuses POST on non-API paths —
  `403 "This distribution is not configured to allow the HTTP request method that was used
  for this request. The distribution supports only cachable requests."`
- 25 candidate routes probed under `vl223.groupos-test.co/api/v1/*`, `/ingest/*`, `/api/*`
  and on the real API origin `api.groupos-test.co` (44.240.58.166) — every one `404`.
- `ingest.` / `hooks.` / `gateway.` / `in.` / `events.groupos-test.co` all CNAME to the same
  wildcard CloudFront (`d37inoairifeby.cloudfront.net`) — no separate ingest host exists.

**Next action: get the pre-prod ingest URL from Andrii, or have the env var set.** Everything
below is ready to run the moment it exists — only `INGEST_URL` changes.

## Payload shape

CloudEvent, `groupos.member.profile.ingest.v1`. Match is by **preferred email**.

```json
{
  "specversion": "1.0",
  "id": "<unique per message — repeat id = repeat, not re-applied>",
  "source": "//airtable/mds-members",
  "type": "groupos.member.profile.ingest.v1",
  "time": "<ISO 8601>",
  "datacontenttype": "application/json",
  "subject": "member/<email>",
  "data": {
    "email": "<email>",
    "fields": {
      "address": "one-line address, as a person would type it",
      "tags": ["Tag A", "Tag B"]
    }
  }
}
```

### Rules that bite

- **Replace, never merge.** The tag list sent becomes the whole tag list. Send the full set
  every time or you wipe what you left out.
- **Omit a field to leave it alone.** Only send `address` when you mean to set it — an empty
  address does not clear, it errors.
- **Unknown field = 400.** Only `address`, `tags`, `eventsRegistered` are accepted.
- **No member with that email = silent no-op**, and the sender gets no error. So a 200 is not
  proof of a write — confirm on the member profile or in Message history.
- **Airtable cannot send a JSON array from a formula.** Where a list must come from a text
  field, join the values with `#%$*^` (not a comma — commas are part of the value). The
  script below splits on that delimiter and sends a real array.

## Airtable automation

Trigger: **When record matches conditions** (or manual, for the first run) on
Members DB `appou5JVr0WIrioWS` / `tblfwOSROSHfuYUxv`.

Action: **Run script**. Input variables to configure on the left panel:

| Input var | Source field |
|---|---|
| `email` | preferred email |
| `address` | one-line address |
| `tagsJoined` | `Tags n8n` `fldmSp9T859pfJ1jp` (already `#%$*^`-joined) |
| `recordId` | Airtable record ID — used for the idempotency key |

```javascript
// GroupOS member-profile ingest — tags + address
const INGEST_URL = 'PASTE_PREPROD_INGEST_URL_HERE';
const TOKEN = 'pat_pub_KghZjujvbz4jopl97IylCGy1Msp6DeV7';
const DELIM = '#%$*^';

const cfg = input.config();
const email = (cfg.email || '').trim();
if (!email) throw new Error('No email on this record — GroupOS matches by email.');

const fields = {};

const tags = (cfg.tagsJoined || '')
    .split(DELIM)
    .map(t => t.trim())
    .filter(Boolean);
fields.tags = tags; // always send the FULL list — this replaces, it does not add

const address = (cfg.address || '').trim();
if (address) fields.address = address; // omit when blank; empty does not clear

const now = new Date().toISOString();
const body = {
    specversion: '1.0',
    id: `at-${cfg.recordId}-${now}`, // unique per send; reuse the id to test dedupe
    source: '//airtable/mds-members',
    type: 'groupos.member.profile.ingest.v1',
    time: now,
    datacontenttype: 'application/json',
    subject: `member/${email}`,
    data: { email, fields },
};

const res = await fetch(INGEST_URL, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${TOKEN}`,
    },
    body: JSON.stringify(body),
});

const text = await res.text();
console.log(`HTTP ${res.status}`);
console.log(text);

// A 200 only means the message was accepted. If no member has this email the write is a
// silent no-op — confirm on the member profile or in the integration's Message history.
if (!res.ok) throw new Error(`GroupOS ingest failed: ${res.status} ${text}`);
```

Auth header is a guess (`Authorization: Bearer`) — the setup panel never states it. Confirm
with Andrii alongside the URL; if it is wrong the first call returns 401 and the header is a
one-line change.

## curl equivalent (faster first check than the automation)

```bash
curl -sS -X POST "$INGEST_URL" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer pat_pub_KghZjujvbz4jopl97IylCGy1Msp6DeV7" \
  -d '{"specversion":"1.0","id":"manual-test-001","source":"//manual/andy","type":"groupos.member.profile.ingest.v1","time":"2026-08-20T05:30:00.000Z","datacontenttype":"application/json","subject":"member/REPLACE@example.com","data":{"email":"REPLACE@example.com","fields":{"address":"1 Infinite Loop, Cupertino, CA 95014","tags":["Ingest Test A","Ingest Test B"]}}}' \
  -w '\nHTTP %{http_code}\n'
```

## Test checklist once the URL exists

1. Fire the curl at a **member that exists in the vl223 community**. Expect 2xx.
2. Member profile shows both tags and the address, address split into street / city / state /
   postcode / country, and a pin on the Members Map.
3. Integration page Message history: 1 message, **Applied**.
4. Re-send with a different tag set — old tags gone, not merged.
5. Re-send the exact same `id` — recognised as a repeat, no double-apply.
6. Send to an email that matches nobody — clean no-op, no new member created.
7. Send with no token and with a junk token — both refused.
8. Confirm nothing else on the profile moved (name, email, phone, photo, bio, membership).
