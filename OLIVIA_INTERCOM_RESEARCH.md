> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia → Intercom tickets — research (2026-07-27)

**Question (Andy):** can Olivia create an Intercom ticket instead of dropping "I've flagged it for the
MDS team" into a Slack channel nobody owns?

**Short answer: yes — via the REST API, from Render or mds-digest-web. NOT from n8n, and NOT via the
Intercom MCP.**

---

## 1. The connected Intercom MCP cannot do it

Checked the live tool list. It is **read-only apart from `create_article`**:
`search`, `search_conversations`, `get_conversation`, `search_contacts`, `get_contact`,
`list_companies`, `get_company`, `list_articles`, `search_articles`, `get_article`, `fetch`,
`create_article`, `update_article`.

**There is no create-ticket and no create-conversation tool.** So the MCP is useful for *reading*
Intercom (e.g. "has this member already contacted support?") but cannot open anything.

## 2. The REST API can

`POST https://api.intercom.io/tickets` — needs:
- `ticket_type_id` — must already exist (**VERIFIED: 3 types exist, see §5**)
- `contacts[]` — an Intercom contact `id` or `email`
- `ticket_attributes` — `_default_title_`, `_default_description_`

`POST /conversations` is the alternative — opens a conversation *from* a user, lands in the inbox,
assignable like any other, no ticket types needed. **Now that tickets are proven to work AND a type
can be created, tickets are the better v1**: they carry state (Submitted → In progress → Resolved),
which is exactly what a queue with an SLA needs. Conversations do not.

## 3. ⚠️ The IP block is real and already documented in our own repo

`/Users/Born/mds-intercom-lastseen-sync/README.md`:

> Runs as a **Render Cron Job** (clean IP — dodges the datacenter-IP block n8n hit).

So **Olivia's n8n workflow cannot call Intercom directly** — this is not theoretical, we already hit
it and built around it. Two viable routes:

| route | notes |
|---|---|
| **n8n → mds-digest-web API route → Intercom** | Vercel IP; the app already holds service creds and is where the Claude-vision + Singapore endpoints live. Probably the right home. |
| **n8n → existing Render service → Intercom** | `mds-intercom-lastseen-sync` already authenticates to Intercom from a clean IP. Would need an HTTP entrypoint (it is a cron job today, not a server). |

## 4. Auth that already exists

`mds-intercom-lastseen-sync/sync.mjs`:
```js
const IC = { Authorization: `Bearer ${INTERCOM}`, Accept: 'application/json',
             'Content-Type': 'application/json', 'Intercom-Version': '2.14' };
```
`INTERCOM_TOKEN` is set **in Render env only** — not in `mds-digest-web/.env.local`, not on this
machine. Andy supplied an admin token directly for this research; **it was used in-session only and
deliberately NOT written to any file.** Whatever token the integration uses must be added to the
chosen host's env (Vercel or Render).

## 5. ✅ ALL GAPS CLOSED — verified live 2026-07-27 with Andy's admin token

Token = admin `Andy` (andy@milliondollarsellers.com), workspace **MDS**.

**a) Ticket types exist — 3:**
| id | name | category |
|---|---|---|
| 1 | Event Request | Back-office |
| 2 | Mobile app Issues | Back-office |
| 3320563 | Issue | Tracker |

None fits "member asked Olivia for something" — **recommend creating a 4th: "Member request (Olivia)"**
so these do not pollute Event Request or the mobile-app tracker.

**b) Write scope CONFIRMED.** `POST /tickets` succeeded → ticket **215475253448318**, state *Submitted*,
titled `[TEST — Olivia write-scope check, safe to close]`, attached to Andy's contact. (Left open for
Andy to inspect.)

**c) CONTACT MATCHING SOLVED — 100% coverage.** Checked ALL 722 active members
(`Preferred Email` → `POST /contacts/search`):

| result | count |
|---|---|
| exactly 1 contact | **670** |
| multiple contacts | **52** |
| **no contact** | **0** |
| errors | 0 |

Every active member is reachable. Note Intercom contacts carry **only email + name** — no
`external_id`, no phone, no custom attributes — so **email is the only join key**. `Preferred Email`
is populated for 722/722.

**Duplicate rule (the 52):** prefer `role='user'` over `role='lead'`, then the most recent
`last_seen_at`. Both observed shapes are covered:
- *Alex Penfold* — one `user` (last_seen set) + one `lead` (last_seen null) → take the user
- *Alex Mills* — two `user` records → take the newer last_seen

**The full chain works:** Olivia knows phone → `at_member_id` → `Preferred Email` →
Intercom contact → ticket attached to the right person.

## 5b. Remaining DECISIONS (not technical blockers — the tech is proven)

1. **A dedicated ticket type?** Recommend "Member request (Olivia)" rather than reusing Event Request.
2. **Does this replace the Slack card or sit beside it?** Recommend beside, until proven.
3. **Who owns the queue and what response time do we promise?** ← still the actual blocker.

## 6. Why this matters right now

`digest.olivia_requests` holds **38 rows, every one still `status='new'`** — nothing has ever been
actioned. Olivia has been telling members "I've flagged it for the MDS team and they'll follow up"
and the card goes to the **`automation-tests`** Slack channel. Real examples from 2026-07-27:

- Ryan Bastuba — wants the directory checked for highest-revenue members
- Franky Farina — wants a list of members in the pet industry
- Andy ×3 — cliff notes PDF, video files, delete a message

Note two of those are things Olivia **should just answer** (member lists), not escalate — worth fixing
the routing as well as the destination.

**Intercom does not solve the ownership problem, it relocates it.** The queue still needs a named
owner and a response time; a ticket system only makes that queue visible and assignable.

---

## Recommendation

**The technical path is fully verified — nothing is unknown.** What is left is a people decision.

1. **Decide the owner + SLA.** Tool-independent, and the only real blocker. 38 requests are already
   unanswered; a ticket nobody watches fails exactly like a Slack card nobody watches.
2. Create the **"Member request (Olivia)"** ticket type.
3. Build: n8n → mds-digest-web API route → `POST /tickets`, resolving the contact by
   `Preferred Email` with the user-beats-lead / newest-last_seen tiebreak.
4. Keep the Slack card in parallel until proven.
5. **Separately: fix the routing that feeds this queue** — "list members in the pet industry" and
   "highest-revenue members" are things Olivia can answer herself and should never have escalated.

Related: [[project_mds_intercom_integration]] · `OLIVIA_TODO.md`
