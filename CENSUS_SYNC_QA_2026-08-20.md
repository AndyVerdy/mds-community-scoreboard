# 2026 Census & Singapore Check-In sync — test results

**Tested:** 20 Aug 2026 · **Scope:** Members DB · Events base · new Census base · **Method:** live API, answer-level

Every Typeform answer from both forms was compared, value by value, against the Airtable record it
should have landed in. A question counts as landed only when its actual value is found on the record —
matching field names was not treated as proof.

---

## Verdict — PASS, 5 open items

All 85 census questions land in Airtable, three of them through transforms that were verified
individually. The Singapore check-in lands 62 of its 63 answerable items across the Members DB and the
Events base. The new base is wired correctly and its lookups populate.

The one serious defect is **not a missing field — it is an arithmetic one**. The yearly revenue rollups
average a member's submissions instead of taking the newest, and every growth-rate formula reads from
them.

---

## Coverage

| Source | Responses | Airtable rows | Matched | Questions landed |
|---|---:|---:|---:|---:|
| Annual Census 2026 | 166 | 167 | 166 | **85 / 85** |
| Summit Singapore Check-In | 110 | 107 + 108 | 110 | **62 / 63** |
| New base — Combined table | — | 303 | 273 | 167 + 107 + 29 |
| New base — Member Census Data copy | — | 717 | 217 | all members |

Check-in rows sit in two tables by design: the business-pulse answers go to the Members DB Forms table,
the hotel, passport and activity block goes to `Check In Forms` in the Events base. Counted together,
only one question is lost — see item 4.

---

## Fix queue — ordered by what breaks first

### 1. CRITICAL — the yearly revenue rollups average a member's submissions instead of taking the latest
*Members · `2022–2026 Revenue per Census`*

Pulling from every 2026 form that carries a revenue number is intended. Averaging them is not. Where a
member reported revenue more than once in a year, the field shows the mean of those figures — a number
that matches none of their answers.

```
Shawn Kolodny   6,000,000 (New Member, Apr) + 6,500,000 (Census, Aug)  → 6,250,000
Ulrich Kratz  180,000,000 (New Member, May) + 230,000,000 (Check-in)   → 205,000,000
Chris Kjeldsen    765,000 (TikTok TTM)      + 450,000,000 (Census)     → 225,382,500
Askar Bagaviev 250,000,000 + 63,000,000 + 300,000,000                  → 204,333,333
```

The forms measure different things — TikTok TTM is one channel's GMV, Centurion is a screening figure,
New Member data can be months old, the census is the whole business. Averaging them produces a quantity
that does not exist. **113 of the 349 members in the 2026 field are averages; 17 of those blend figures
more than 3× apart.** It was 24 members in 2024 and 22 in 2025 — adding the check-in as a third revenue
instrument is what took it from roughly 6% to 32%.

Everything downstream inherits it: `2025>2026 Growth Rate NEW` (143 members),
`2026>2027 Growth Rate - Projected NEW` (180), `2025>2026 Growth Rate Hit/Miss NEW` (124), and the
mirrored copy in the new base (319).

**Fix.** An Airtable rollup cannot pick "latest by date", so this needs a helper: an automation on the
Forms table that writes the newest revenue figure of the year — plus the form it came from and its date,
for provenance — into plain fields on Members, with the growth formulas repointed at those. Give it a
sanity ceiling while you are in there: one Forms row currently holds `9,999,999,999,999` and would win
any "latest" pick.

### 2. HIGH — the check-in backfill skipped two fields
*Members DB · Forms · check-in rows*

Every check-in row stamped `2026-08-10 19:05:48` — the bulk load — is missing
`Confidence heading next 12 months` and `Projected FTM Revnue`. Rows that synced individually have both.

```
Confidence heading next 12 months   Forms 22 / 107   ·   Events base 91 / 108
Projected FTM Revnue                Forms 22 / 107   ·   Events base 91 / 108
```

No data was lost — the Events base has all 91 answers. But anything reading the Members DB, including
the member-level lookups, sees 69 blanks that should hold values.

**Fix.** Re-run the backfill for those two fields only.

### 3. HIGH — the "Census Avg Salary" fields contradict the members' own answers
*New base · Member Census Data copy*

Three fields — `Census Avg Salary - Director`, `- Manager`, `- Lead/Specialist` — exist only in the new
base and disagree with the pay band the member selected in the 2026 census roughly half the time. They
are also filled for members who never answered the question at all. The comparison below ignores the
en-dash / hyphen difference between the two sets of labels.

```
Director          47 both present → 27 agree, 20 disagree   ·  24 filled with no member answer
Manager           71 both present → 41 agree, 30 disagree   ·  17 filled with no member answer
Lead/Specialist   68 both present → 44 agree, 24 disagree   ·  28 filled with no member answer

e.g. Census Avg Salary - Director = "Under $5k"   ·   member answered "$5k–8k"
```

If these are meant to be something other than the member's own answer — a team average, or a figure
carried over from an earlier census — the naming makes them read as a duplicate of the pay-band field
sitting next to them, and a report writer will pick the wrong one.

**Fix.** Say what these three fields are derived from, then either rename them to match or drop them.
Until that is settled, the trend report should read the pay-band fields, not these.

### 4. MEDIUM — city and country of birth is collected but never stored
*Events base · Check In Forms*

58 people answered it. The dedicated field `What is your city and country of birth?` is empty on all 108
rows, and the value is not folded into the address field either — checked against individual responses
("Khabarovsk, Russia", "Dalian, China", "Sydney, Australia" appear nowhere on those records).

**Fix.** Add the mapping and replay the 58 responses. This is passport-block data, so it is worth having
before the next summit rather than after.

### 5. MEDIUM — 30 submissions are not linked to a member
*New base · Combined table*

Of 303 rows, 273 carry a member link and 30 do not: 18 check-in, 10 New Member v3, 2 census. The
applications are expected — those people are not members yet. The 18 check-ins are not: they are
attendees who will simply be absent from any member-level view.

```
unlinked check-ins include:
  curtis@giveasht.com · ryanng@pearlwestgroup.com
  jonathan@onefamilycorp.com · pey_tsyr@hotmail.com · alex@cuddleclubbaby.com
```

**Fix.** Match the 18 check-ins by hand — most look like an email the member has not registered in the
Members DB.

### 6. DECISION, not a bug — the old per-role salary columns can no longer be compared year over year
*Members · Member Census Data view*

Eugene's view breaks pay out across 11 named roles — Director of Operations, Marketplace Manager,
Bookkeeper and the rest. The 2026 census does not ask that question any more; it asks four seniority
tiers instead (Director, Manager, Specialist, Admin). Those 11 columns receive nothing from the 2026
census or the check-in, so they are frozen at pre-2026 values.

No mapping can bridge the two — the questions ask about different things. Either the trend report drops
the per-role series after 2025 and starts a new tier series, or a future census asks both. That is a call
for Eugene and Andy, not something to fix in the data.

---

## Verified working — no need to re-check

- **Census question coverage.** All 85 questions land. Three arrive transformed and each was confirmed
  separately: EOS splits into two fields (120 rows), gross margin becomes a bucket (151), and the M&A
  question fans out to four legacy fields.
- **Response matching.** 166 of 166 census responses match a member record by email. All 110 check-in
  responses match once both destination tables are counted.
- **New Members fields carry through.** Director pay 65, Manager 98, Lead/Specialist 89, Admin 60,
  % of profit paid to self 129, Tariff Impact 76 — each within one or two rows of its source count.
- **The new base is wired correctly.** Combined holds exactly 167 + 107 + 29 rows; the member copy holds
  all 717. The lookups that could not be built in the Members table do populate: prior-year revenue 161,
  COGS 157, YoY change 158, margin outlook 161, staffing model 161, financing sources 161.
- **Formulas compute.** No error values anywhere in the new growth-rate fields.

---

## Housekeeping

Two pieces of test data are sitting in the live check-in set: five submissions from
`tangowithw@gmail.com` dated 30 July, and a record under `7RckAo@example.com` whose projected revenue
reads `66`. Worth clearing before anyone runs totals.

Counts in this report were read live on 20 August 2026 and will drift as new responses arrive.
