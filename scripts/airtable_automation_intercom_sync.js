/* ============================================================================
 * Airtable Automation → Intercom real-time sync
 * Pushes "AT Database Status" to Intercom whenever it changes on a Member.
 * ----------------------------------------------------------------------------
 * SETUP (in the Airtable base appou5JVr0WIrioWS, Members table):
 *
 * 1. Automations → Create automation.
 * 2. Trigger: "When record updated"
 *      - Table: Members
 *      - Watched fields: ONLY "AT Database Status"
 * 3. Action: "Run a script"
 * 4. In the script editor, add these INPUT VARIABLES (left panel), each
 *    mapped to the trigger record's field:
 *      status          ←  field "AT Database Status"
 *      intercomUserId  ←  field "Intercom User ID"
 *      waUserId        ←  field "WA User ID"
 *      email           ←  field "Preferred Email"
 * 5. Paste this script. Set INTERCOM_TOKEN below (see note).
 * 6. Test with a record, then turn the automation ON.
 *
 * ⚠️ TOKEN: Airtable has no secret store for scripts, so the token sits in
 *    this script — visible to base admins/editors. Acceptable for an internal
 *    base. Rotate it from the Intercom Developer Hub if it ever leaks.
 * ==========================================================================*/

const INTERCOM_TOKEN = 'PASTE_INTERCOM_TOKEN_HERE';

const BASE = 'https://api.intercom.io';
const H = {
  Authorization: `Bearer ${INTERCOM_TOKEN}`,
  'Content-Type': 'application/json',
  Accept: 'application/json',
  'Intercom-Version': '2.14',
};

// Andy's rule: only these three statuses = a current member.
const CURRENT = new Set(['New Member', 'Current Member', 'Pending Group Entrance']);

const cfg = input.config();
const status = (cfg.status ?? '').toString().trim();
const intercomUserId = (cfg.intercomUserId ?? '').toString().trim();
const waUserId = (cfg.waUserId ?? '').toString().trim();
const email = (cfg.email ?? '').toString().trim().toLowerCase();

if (!status) {
  console.log('AT Database Status is empty — nothing to sync.');
} else {
  const stage = CURRENT.has(status) ? 'Current Member' : 'Not a Member';

  // Resolve Intercom contact id(s): Intercom User ID → external_id(WA) → email
  async function findIds() {
    if (intercomUserId) return [intercomUserId];
    for (const [field, value] of [['external_id', waUserId], ['email', email]]) {
      if (!value) continue;
      const res = await fetch(`${BASE}/contacts/search`, {
        method: 'POST',
        headers: H,
        body: JSON.stringify({ query: { field, operator: '=', value } }),
      });
      const j = await res.json();
      if (j.data && j.data.length) return j.data.map((c) => c.id);
    }
    return [];
  }

  const ids = await findIds();
  if (!ids.length) {
    console.log(`No Intercom contact for "${status}" (email=${email || '-'}, wa=${waUserId || '-'}).`);
  } else {
    for (const id of ids) {
      const res = await fetch(`${BASE}/contacts/${id}`, {
        method: 'PUT',
        headers: H,
        body: JSON.stringify({
          custom_attributes: { 'AT Database Status': status, 'Membership Stage': stage },
        }),
      });
      console.log(`Intercom ${id} ← "${status}" / "${stage}": HTTP ${res.status}`);
      if (res.status >= 400) {
        const t = await res.text();
        throw new Error(`Intercom update failed (${res.status}): ${t.slice(0, 300)}`);
      }
    }
  }
}
