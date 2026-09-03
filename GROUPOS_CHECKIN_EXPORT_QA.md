# Test report — Check-in table export (CSV / XLSX), pre-prod

**Ticket:** `86e2ndz5v` — Add Export Option for Check-Ins (pre-prod release 1.2.1; MDS-API #5492/#5494, MDS-APP #8296/#8298)
**Tested by:** Claude for Andy · 2026-09-03 05:29–05:36 UTC · pre-prod `vl223.groupos-test.co`, event "San Diego Chapter Hike Feb 2026" (`698337510249797c751208ee`, 3 attendees, no activities, no staff)
**Verdict: PASS.** All six of Andrii's test cases hold: the button is there, CSV and XLSX carry exactly the table's rows, filters (search and Check-in Status) are honoured, an empty result shows "No check-in data to export." and downloads nothing. TC6 (button locked while working) is not observable on a 3-row event. One unexplained extra CSV early in the session, not reproduced — see observations.

## What was run

| TC | Step | Result |
|---|---|---|
| 1 | Admin → Events → San Diego Chapter Hike → Manage attendees → Check-ins | **Export** button at the right end of the filter bar. Table 1–3 of 3, "Checked in 0 of 3" |
| 2 | Export → Export as CSV (no filters), 05:30:16 UTC | Green "Check-in data exported." File `San-Diego-Chapter-Hike-Feb-2026_CheckIns_2026-09-03.csv`, 372 bytes, UTF-8 BOM, **3 data rows** = table total, names/emails match. Columns: First Name, Last Name, Display Name, Email, Attendee Type, Tickets, Event Check-in Status, Event Check-in Time |
| 3 | Export → Export as XLSX, 05:30:32 UTC | `…_CheckIns_2026-09-03.xlsx`, 17,603 bytes, one sheet **"Check-ins"**, A1:H4 (header + 3 rows), same values as the CSV, column widths set (12.8–33.8). Header row not bold, no frozen header (cosmetic) |
| 4a | Search "Andrii" (+ Enter) → table 1–1 of 1 → Export as CSV, 05:33:34 UTC | One 207-byte download, **1 data row** (Andrii). Filter honoured |
| 4b | Check-in Status = "Check In" → table "No Data Found", 0–0 of 0 → Export as CSV, 05:36:08 UTC | Blue "No check-in data to export.", **no download** — an unfiltered export would have produced 3 rows, so the select filter is honoured too |
| 5 | Search "zzzzzz" → "No Data Found" → Export as CSV, 05:33:45 and again 05:34:24 UTC | Blue "No check-in data to export.", no download, nothing broke |
| 6 | Locking while the file is prepared | Not observable: 3 rows export instantly. A `URL.createObjectURL` tracer showed exactly one blob per click on three separate clicks (no double downloads) |

Search needs Enter (or the debounce) before the table filters — typing alone left 1–3 of 3 for several seconds; the export then follows whatever the table shows.

## Observations

1. **One CSV appeared before my first Export click.** `…_CheckIns_2026-09-03.csv` was created at 05:30:05 UTC; my first click on Export was at 05:30:15 and produced the `(1)` copy at 05:30:16. Reloading the page and waiting 25 s without clicking produced nothing, and every later click produced exactly one file, so I could not reproduce it. Possibly my tooling's accessibility read touched the button. Unconfirmed; mentioned so nobody is surprised by a stray file.
2. The green "Check-in data exported." toast stayed on screen for well over a minute and stacked with the next one; it does not auto-dismiss. Cosmetic.
3. XLSX header row is plain (not bold, not frozen). Cosmetic.
4. Not exercised on this event: per-activity columns (no activities with check-in), Staff-only exclusion (no staff), large-event timing.

## Files

Left in `~/Downloads`: `San-Diego-Chapter-Hike-Feb-2026_CheckIns_2026-09-03.csv`, `… (1).csv`, `… (2).csv` (filtered, 1 row), `….xlsx`. Nothing changed on pre-prod — export is read-only.
