# Duplicate Member Record — Justin Cao (Investigation Report)

**Date:** 2026-07-29 (rev. 2 — GHL/LeadConnector chain added)
**Base:** MDS Member Database (`appou5JVr0WIrioWS`) · table **Members** (`tblfwOSROSHfuYUxv`)
**Trigger:** Andy spotted a member record being edited "via API (using Make – Luma Leads Enrichment token)" and asked why AT data was changing.
**Investigated by:** Claude — read-only Airtable + Make audit. **No records or scenarios were modified.**

---

## TL;DR

Justin Cao has **two** records in the Member DB. The **real** one is a paid member. The **fake** one is a phantom twin born from a **GHL → Wild Apricot → sync chain**:

1. Justin paid → the GHL scenario **"GoHighLevel LeadConnector, Airtable" (4088035)** created his **Wild Apricot contact** `97192412` and updated his real record.
2. Weeks later the **"Contacts: Wild Apricot → Airtable" sync (364050)** pulled that WA contact, **couldn't match it to his real record, and created a second Members row** — no email.
3. **"New member Application v3" (4784286)** then updated that twin with applicant fields — even though **Justin never submitted an application.**

Every edit was an automation running on its own — **none was Claude.**

- **Real:** `recB1s4lSjTq57Vpu` — `justin@sojosvision.com`, **New Member**, paid $7,497, created 2026‑03‑24.
- **Fake:** `rec0WT79BavWKKrwN` — **no email**, **Pending 1st Interview / Applicant**, created 2026‑05‑15.

---

## 1. The two records

| Field | Real `recB1s4lSjTq57Vpu` | Fake `rec0WT79BavWKKrwN` |
|---|---|---|
| Created (Airtable) | **2026-03-24** | **2026-05-15** |
| Preferred Email | justin@sojosvision.com | **(blank)** |
| AT Database Status | **New Member** | **Pending 1st Interview** |
| Member / Applicant | Member | Applicant |
| Completed Application Form | true | **false** |
| WA User ID | — (no WA link) | **97192412** |
| WA Membership Status | — | Active |
| Level | MDS Membership – Annual | MDS Membership – Annual |
| Paid | **$7,497** (Apr 8–9) | $0 |
| Tags (n8n) | full chapter/tag set | "Standard Event Access" only |
| Submission ID | Justin Cao-04/09/2026 | Justin Cao-04/08/2026 |

---

## 2. Timeline (annotated)   ✓ confirmed · ~ inferred

### Real `recB1s4lSjTq57Vpu` — the legitimate member
| Date | Event | Automation |
|---|---|---|
| Mar 24 | Members row **created**; entered Pending Entrance; first event reg | **First-event / warm-lead intake** (Airtable-native automation) ~ |
| Apr 8–9 | Paid $7,497; **Wild Apricot contact 97192412 created**; Members record updated | **GoHighLevel LeadConnector, Airtable (4088035)** ✓ |
| Apr 10 | 1st interview completed; member approved | Airtable native automation ~ |
| Apr 13 | Chapter assigned; status → New Member; PGE switch | Chapter sync + AT DB Status Sync ~ |

### Fake `rec0WT79BavWKKrwN` — the phantom twin
| Date | Event | Automation |
|---|---|---|
| Apr 8–11 | (Justin's WA contact 97192412 exists — created by 4088035 above) | GHL → Wild Apricot ✓ |
| **May 15** | **Members twin created — no email**; WA fields written | **Contacts: Wild Apricot → Airtable (364050)** ✓~ |
| Jun 29 | Application Date + "Pending 1st Interview" stamped (no application was submitted) | **New member Application v3 (4784286)** ✓ |
| Jul 29 | Access / status / PGE re-stamped | AT DB Status Sync (3036070) + AT native ~ |

---

## 3. Automations involved (Make — team MDS `103111`, zone us1)

| Scenario | ID | Trigger | Role in this incident | Creates in | Link |
|---|---|---|---|---|---|
| **GoHighLevel LeadConnector, Airtable** | 4088035 | GHL LeadConnector webhook (hook 2321134), on payment | **Root of the dup** — creates the member's **Wild Apricot contact** + *updates* Members | Wild Apricot contact (not AT) | https://us1.make.com/103111/scenarios/4088035/edit |
| **Contacts: Wild Apricot → Airtable** | 364050 | Wild Apricot *(unconfirmed — blueprint won't load)* | **Created the twin** from the unmatched WA contact | **Members** `tblfwOSROSHfuYUxv` | https://us1.make.com/103111/scenarios/364050/edit |
| **New member Application v3** | 4784286 | **Typeform** submission | **Updated** the twin with Application Date + "Pending 1st Interview" | Applications `tblblwPcgqhkPTVec` (not Members) | https://us1.make.com/103111/scenarios/4784286/edit |
| Warm Member Leads GHL | 2321224 | GHL webhook (hook 1326357) | Creates warm-lead records (not the Members row) | Warm Member Leads `tblD4UbH8JvmGANNF` | https://us1.make.com/103111/scenarios/2321224/edit |
| AT DB Status Sync (copy) | 3036070 | — | Likely the Jul 29 status re-stamp *(unverified)* | — | https://us1.make.com/103111/scenarios/3036070/edit |

**Key correction (rev. 2):** neither **App v3 (4784286)** nor **GoHighLevel LeadConnector (4088035)** creates the Members row — App v3 creates an *applications* row (`tblblwPcgqhkPTVec`) and 4088035 creates a *Wild Apricot contact*; both only **update** the Members table. The only scenario that **creates** Members rows in this chain is the WA→AT sync **364050** — which is what produced the twin.

**Shared Airtable token** these authenticate with: connection **"Luma Enrichment"** (`4746536`) — this is why Airtable's revision history mislabels every edit as the "Luma Leads Enrichment token." The token name is *not* the scenario. (Connections: https://us1.make.com/103111/connections)

> Link pattern if any 404s: `us1.make.com/103111/scenarios/<id>`

---

## 4. Root cause — GHL → Wild Apricot → duplicate

1. Justin's **real** member record (created Mar 24 by the warm-lead/event intake) was set up and paid; his billing runs on **Stripe** ("billing migrated").
2. On payment, **GoHighLevel LeadConnector, Airtable (4088035)** created his **Wild Apricot contact** (`97192412`) — but **the WA User ID was never stamped back onto his Members record.**
3. When the **Wild Apricot → Airtable contacts sync (364050)** ran (May 15), it found no Members record carrying that WA contact and **created a new one** instead of updating the real record. Built from WA data, it set **no Preferred Email** → the twin has no email → downstream **email-based matching also can't dedupe it.**
4. **New member Application v3 (4784286)** later matched that twin (by name, since it has no email) and stamped applicant fields on it — making it *look* like a fresh applicant, though no application was submitted.

**Same failure class** as the Adam Weiler Luma duplicate and the known "Ulrich" MRR dups — an automation creates a second record when its match key doesn't line up.

---

## 5. Recommendations

1. **Do not delete the twin** (policy: never delete a member record). Have membership **merge** it into the real record `recB1s4lSjTq57Vpu` (canonical — real email, Member, paid, full tags), then archive/clear the twin via the standard merge process.
2. **Fix the seam (root):** when **4088035** creates the Wild Apricot contact, **stamp the resulting `WA User ID` back onto the Members record**, and have **364050** match on that WA User ID (email as fallback). Then the WA sync **updates** the existing member instead of creating a twin.
3. **Stop App v3 mislabeling (4784286):** it should not stamp "Application Date / Pending 1st Interview" onto a record with no submitted application — and it matched a no-email twin by name. Tighten its Members match (and skip when no application exists).
4. **Token hygiene (optional):** give each scenario its own named Airtable connection instead of the shared **"Luma Enrichment"** token, so the revision history attributes edits correctly.

---

## 6. Open items / to verify

- **364050's blueprint won't load** (Make API timed out 5×). Confirm its exact trigger (WA event vs scheduled poll) and its Members `CreateRecord` + match key when the API is responsive.
- **Pin the real-record creator (Mar 24):** ruled out App v3, 4088035, and 2321224 (they create in the applications / warm-leads tables or only update Members). The Members row is almost certainly created by an **Airtable-native automation** that promotes a warm lead into Members — needs the base's automations list to name it.
- Confirm the **Jul 29** edits' source (AT DB Status Sync `3036070` vs an Airtable native automation).
- **Scan the Member DB for other twins** born the same way — pattern: *no Preferred Email + has WA User ID + Applicant status, created after the member's real record.*

---

## Method & caveats

- Findings come from **read-only** Airtable (record fields + `createdTime`) and Make (scenario list, connection usages, and full blueprints for 4784286 / 4088035 / 2321224 — each Airtable module mapped to its table by line order).
- Airtable's REST API does **not** expose per-field revision history, so *creation-vs-edit* attribution is inferred from timestamps + which scenario writes which fields (`~` inferred; `✓` confirmed by blueprint/field-match; `✓~` = confirmed-by-elimination but blueprint not openable).
- **364050** could not be opened (repeated Make API timeouts); its role as the twin's creator is established by elimination + the fact that only the twin carries Wild-Apricot contact data.
- **Claude made no edits** to these records or scenarios during the investigation.
