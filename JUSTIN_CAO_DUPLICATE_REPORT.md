# Duplicate Member Record — Justin Cao (Investigation Report)

**Date:** 2026-07-29
**Base:** MDS Member Database (`appou5JVr0WIrioWS`) · table **Members** (`tblfwOSROSHfuYUxv`)
**Trigger:** Andy spotted a member record being edited "via API (using Make – Luma Leads Enrichment token)" and asked why AT data was changing.
**Investigated by:** Claude — read-only Airtable + Make audit. **No records or scenarios were modified.**

---

## TL;DR

Justin Cao has **two** records in the Member DB. The **real** one is a paid member; the **fake** one is a phantom twin **created by the Wild-Apricot → Airtable contacts sync**, then mislabeled as a "Pending 1st Interview" applicant by the new-member application scenario. Justin **never submitted a new application**, and the twin has **no email**. Every edit was an automation running on its own — none of it was Claude.

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
| Mar 24 | Record created; entered Pending Entrance; first event reg | New-member intake (App v3 / onboarding webhook) ~ |
| Apr 8 | Paid $7,497 | Stripe / GHL → AT payment sync ~ |
| Apr 9 | Member join & paid date; application date; access granted | Onboarding + App v3 ~ |
| Apr 10 | 1st interview completed; member approved | Airtable native automation ~ |
| Apr 13 | Chapter assigned; status → New Member; PGE switch | Chapter sync + AT DB Status Sync ~ |

### Fake `rec0WT79BavWKKrwN` — the phantom twin
| Date | Event | Automation |
|---|---|---|
| Apr 8–11 | Wild Apricot contact 97192412 created / Active | Wild Apricot (source system) ✓ |
| **May 15** | **AT twin created — no email**; WA membership fields written | **Contacts: Wild Apricot → Airtable (364050)** ✓ |
| Jun 29 | Application Date + "Pending 1st Interview" stamped | **New member Application v3 (4784286)** ✓ |
| Jul 29 | Access / status / PGE re-stamped | AT DB Status Sync (3036070) + AT native ~ |

---

## 3. Automations involved (Make — team MDS `103111`, zone us1)

| Scenario | ID | Role in this incident | Link |
|---|---|---|---|
| **Contacts: Wild Apricot → Airtable** | 364050 | **Created the twin** + wrote the WA fields | https://us1.make.com/103111/scenarios/364050/edit |
| **New member Application v3** | 4784286 | Stamped Application Date + "Pending 1st Interview" | https://us1.make.com/103111/scenarios/4784286/edit |
| AT DB Status Sync (copy) | 3036070 | Likely the Jul 29 status re-stamp (unverified) | https://us1.make.com/103111/scenarios/3036070/edit |

**Shared Airtable token** all three authenticate with: connection **"Luma Enrichment"** (`4746536`). This is why Airtable's revision history mislabels every one of these edits as the "Luma Leads Enrichment token" — the token name is *not* the scenario. (Connections list: https://us1.make.com/103111/connections)

> Link pattern if any 404s: `us1.make.com/103111/scenarios/<id>`

---

## 4. Root cause — a dedup gap

Justin's **real** member record (created via the application/onboarding flow, billing on Stripe) was **never stamped with his Wild Apricot contact ID** (`97192412`). When the WA → AT contacts sync (**364050**) ran on **May 15**, it found no AT record matching that WA contact, so it **created a new record** instead of updating the real one. Because it builds the record from Wild Apricot data, it never set a **Preferred Email** → the twin has no email → downstream **email-based matching can't dedupe it either**.

Then **New member Application v3 (4784286)** later wrote application-pipeline fields onto that twin (Application Date + "Pending 1st Interview"), making it look like a fresh applicant even though **no application was submitted**.

**Same failure class** as the Adam Weiler Luma duplicate and the known "Ulrich" MRR duplicates — automations create a second record when their match key doesn't line up.

---

## 5. Recommendations

1. **Do not delete the twin** (policy: never delete a member record). Have membership **merge** it into the real record `recB1s4lSjTq57Vpu` (canonical — real email, Member, paid, full tags), then archive/clear the twin via the standard merge process.
2. **Fix the source (364050):** match WA contacts on a **stable key** — stamp `WA User ID` onto member records during onboarding, and have the sync match on that (with email as fallback) so it **updates** the existing member instead of creating a twin.
3. **Stop App v3 mislabeling (4784286):** it should not stamp "Application Date / Pending 1st Interview" onto a record that came from the WA sync with no submitted application — review its trigger/match logic.
4. **Token hygiene (optional):** give each scenario its own named Airtable connection instead of the shared **"Luma Enrichment"** token, so the revision history attributes edits correctly.

---

## 6. Open items / to verify

- Confirm **364050's exact match key** (the Make API was timing out during this audit).
- Confirm the **Jul 29 edits'** source (AT DB Status Sync `3036070` vs an Airtable native automation).
- **Scan the Member DB for other twins** born the same way — pattern: *no Preferred Email + has WA User ID + Applicant status, created after the member's real record.*
- Why **App v3 (4784286)** wrote to a non-application record at all — check its trigger.

---

## Method & caveats

- Findings come from **read-only** Airtable (record fields + `createdTime`) and Make (scenario list, connection usages, App v3 blueprint field-mappings).
- Airtable's REST API does **not** expose per-field revision history, so *creation-vs-edit* attribution for the twin is inferred from timestamps + which scenario writes which fields (marked `~` where inferred; `✓` where confirmed by blueprint/field-match).
- **Claude made no edits** to these records or scenarios during the investigation.
