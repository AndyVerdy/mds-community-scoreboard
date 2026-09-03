> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# Facebook stream — backlog

Covers the Facebook surfaces: group capture (`digest.fb_*`), the admin report tab
(`/admin/facebook`), and WA → FB story posts (`/api/fbstory/*`).

Structure: **OPEN — ARCHITECTURE** first, then **OPEN — THE REST**, then **CLOSED**.
A ticket's block moves between sections; it is never copied.

---

## OPEN — ARCHITECTURE

### #1 · 🔑 Facebook posts don't reach the member spine for 11 real members · 🔴 S1

**Story.** As MDS, we want every Facebook group post attributed to the member who wrote
it, so that engagement scoring, the admin report and the WhatsApp stories all credit the
right person — and so a member's activity is never invisible because of a missing join.

**Measured 2026-09-02 (live):** 284 posts in the last 30 days; **246 reach the member
spine (87%)** via `fb_member_map.at_member_id` → `member_profiles`. The 38 that don't come
from **13 distinct authors with no `fb_member_map` row at all**:

| Author | Posts (30d) |
|---|---|
| Dan Wills | 13 |
| Ivan Ong | 9 |
| Million Dollar Sellers | 4 · *not a person — the group's own account* |
| Mouad Errafik | 3 |
| EJ Ball · Matthew Verde · Mirzad De · Ruben Alikhanyan · Abe Indig · Tamkin Amin Collins · Ben Pearson · Chris Kjeldsen | 1 each |
| Anonymous member | 1 · *unresolvable by design — FB anonymous posting* |

So **11 real people**. EJ Ball is the diagnostic case: he IS a member with a Facebook
profile link on file, so the break is the FB-uid → member mapping, not the member record.

**Acceptance criteria**
1. Each of the 11 either resolves to an `at_member_id`, or is recorded with a stated
   reason why it cannot (e.g. no FB profile link in Airtable, duplicate/ambiguous uid).
2. "Million Dollar Sellers" and "Anonymous member" are classified explicitly as
   not-a-member rather than counted as misses, so coverage stops being flattered or
   penalised by them.
3. Coverage re-measured over the same 30-day window: before **246/284 (87%)**, after
   stated. Every author counted once.
4. The root cause is named per member — a missing `FB Profile Link` in Airtable is a
   different fix from a missing `fb_member_map` row, and the two need different owners.
5. **No Airtable writes by the agent.** Where the fix belongs in Airtable, name the record
   and the field and hand it to Andy or ops.

**Notes.** `fb_member_map` is the FB-capture stream's table. ⚠️ There are ~737 duplicate
`Member ID (FB)` values in Airtable `tblVc38gw21iHLYMG` (long-standing, uninvestigated) —
worth checking whether they overlap these 11 before hunting individually. Join against
`member_profiles`, **not** `digest.members`: the latter is the WhatsApp mirror and reports
a misleading 72%.

---

## OPEN — THE REST

*(none)*

---

## CLOSED

*(none yet — this board opened 2026-09-02)*
