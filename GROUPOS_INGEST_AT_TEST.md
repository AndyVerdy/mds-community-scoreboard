# GroupOS incoming webhooks — pre-prod test

Test record for ClickUp `86e2bjq8x` (Incoming Webhooks for Address / Tags / Events registered).
Scope tested: **tags + address**. Events registered not yet exercised.

## Result — 2026-08-26: PASSES

Token `pat_pub_KghZ…` works. Address and tags both write, Google normalisation runs, overwrite
and dedupe behave as specified.

## Connection

| | |
|---|---|
| Environment | Pre-prod — `https://vl223.groupos-test.co` (community `vl223`) |
| Integration | `andy` — `6a868ae0bdab79b87256579c` |
| Web address | `https://event-ingest.groupos-test.co/api/event-ingest/api/v1/hooks/member-profile` |
| Auth | `Authorization: Bearer <token>` — bare token is rejected |
| Token | `pat_pub_KghZ…` · Active · expires Nov 17 2026 |
| Test member | `staging123@groupos.com` — "andy verdy" / display name "Andy on the map", id `698331a30249797c751200b0` |

The web address is per-environment, not per-integration — both `andy` and `AMAT Testing` share
it, and the token alone decides which integration a message belongs to.

## What was run

| # | Test | Sent | Result |
|---|---|---|---|
| 1 | No token | tags | `401 Missing or malformed Authorization header` |
| 2 | Bad token | tags | `401 Invalid, expired, or revoked token.` |
| 3 | Unmatched email | tags | `202 accepted:true` — silent no-op, logged as "needs a second look" |
| 4 | Real write | address + tags | `202 {"accepted":["address","tags"],"ignored":[]}` |
| 5 | Replace | tags only, one value | `202` — previous two tags removed, address untouched |
| 6 | Dedupe | test 4's payload resent verbatim | `202 deduped:true` — not re-applied |
| 7 | Unknown field | `phone` | `400 Unrecognized key(s) in object: 'phone'` |

## Before / after on the test member

| Field | Before | After write | After replace |
|---|---|---|---|
| Tags | *(0 tags)* | Ingest Test A, Ingest Test B | **Ingest Test C** only |
| Location | 2727 Lemmon Avenue | Infinite Loop 1, 1 Infinite Loop, Cupertino, CA 95014, USA | unchanged |
| Street | Lemmon Avenue | 1 Infinite Loop | unchanged |
| Apt | 140 | *(empty)* | unchanged |
| City | Dallas | Cupertino | unchanged |
| State | Texas | CA | unchanged |
| ZIP | 75204 | 95014 | unchanged |
| Country | United States | United States | unchanged |
| Show on map | on | on | on |

Sent as the one-line string `1 Infinite Loop, Cupertino, CA 95014, USA` and came back split
into components — Google normalisation runs on the ingested value exactly as it does on a
manual profile edit. Apartment `140` was cleared because the new address has no unit, which is
correct overwrite behaviour.

**The member is left on the Cupertino address with the tag `Ingest Test C`.** Restore it to
Dallas if that fixture matters — the apartment number `140` will need re-entering by hand,
since a one-line address can't carry it back.

## Acceptance criteria

| AC | Verdict |
|---|---|
| Admin can push Address + Tags for N members from a CRM export | **met** — endpoint accepts, auth enforced |
| Incoming values replace existing values | **met** — test 5 |
| Addresses Google-normalised, land on Members Map | **met** — components split, map flag still on |
| No other profile fields modified | **met** — name, email, display name, status, channels, custom fields all unchanged |
| Events Registered | **not tested this pass** |

## Payload

```json
{
  "specversion": "1.0",
  "id": "<unique per message — reusing an id marks it deduped and skips the write>",
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

- **Replace, never merge.** Send the full tag set every time or you wipe what you left out.
- **Omit a field to leave it alone.** Only send `address` when you mean to set it.
- **Unknown field = 400**, and the message is rejected whole.
- **No member with that email = silent 202.** A 202 is not proof of a write — confirm on the
  profile or in the integration's Message history.
- **Airtable can't send a JSON array from a formula.** Join with `#%$*^` (not a comma) and
  split it in the script.

## curl

```bash
curl -sS -X POST "https://event-ingest.groupos-test.co/api/event-ingest/api/v1/hooks/member-profile" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer pat_pub_KghZjujvbz4jopl97IylCGy1Msp6DeV7" \
  -d '{"specversion":"1.0","id":"manual-test-001","source":"//manual/andy","type":"groupos.member.profile.ingest.v1","time":"2026-08-26T04:00:00.000Z","datacontenttype":"application/json","subject":"member/staging123@groupos.com","data":{"email":"staging123@groupos.com","fields":{"address":"1 Infinite Loop, Cupertino, CA 95014, USA","tags":["Ingest Test A","Ingest Test B"]}}}' \
  -w '\nHTTP %{http_code}\n'
```

## Airtable automation

Trigger: **When record matches conditions** on Members DB `appou5JVr0WIrioWS` /
`tblfwOSROSHfuYUxv`. Action: **Run script**, with input variables `email`, `address`,
`tagsJoined` (from `Tags n8n` `fldmSp9T859pfJ1jp`, already `#%$*^`-joined), and `recordId`.

```javascript
// GroupOS member-profile ingest — tags + address
const INGEST_URL = 'https://event-ingest.groupos-test.co/api/event-ingest/api/v1/hooks/member-profile';
const TOKEN = 'pat_pub_KghZjujvbz4jopl97IylCGy1Msp6DeV7';
const DELIM = '#%$*^';

const cfg = input.config();
const email = (cfg.email || '').trim();
if (!email) throw new Error('No email on this record — GroupOS matches by email.');

const fields = {};

// always send the FULL list — this replaces, it does not add
fields.tags = (cfg.tagsJoined || '').split(DELIM).map(t => t.trim()).filter(Boolean);

const address = (cfg.address || '').trim();
if (address) fields.address = address; // omit when blank; empty does not clear

const now = new Date().toISOString();
const res = await fetch(INGEST_URL, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${TOKEN}`,
    },
    body: JSON.stringify({
        specversion: '1.0',
        id: `at-${cfg.recordId}-${now}`, // unique per send; reuse to trigger dedupe
        source: '//airtable/mds-members',
        type: 'groupos.member.profile.ingest.v1',
        time: now,
        datacontenttype: 'application/json',
        subject: `member/${email}`,
        data: { email, fields },
    }),
});

const text = await res.text();
console.log(`HTTP ${res.status}`);
console.log(text);

// 202 only means the message was accepted. If no member has this email the write is a silent
// no-op — confirm on the profile or in the integration's Message history.
if (!res.ok) throw new Error(`GroupOS ingest failed: ${res.status} ${text}`);
```

⚠️ This URL and token are **pre-prod**. Point at the production equivalents before running it
against real MDS members — and remember tags replace, so the first live run must carry every
member's full tag set or it will strip tags across the community.

## Still to test

- Events registered, including the attendee-list side effect when a name matches a real event.
- The `#%$*^` delimiter path end-to-end from an actual Airtable formula field.
- Empty tag list clears tags; empty address is refused rather than clearing.
