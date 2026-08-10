---
name: groupos-videos-weekly
description: Weekly GroupOS 2026 video check (new + changed) that feeds the Zoom transcript/dossier chain
---

Weekly GroupOS video check for the MDS Olivia project (ticket #70, working around #17).

WHY THIS IS A SCHEDULED CLAUDE TASK AND NOT A CRON SCRIPT: the GroupOS MCP only runs inside a Claude session, so nothing headless can call it. There is no GROUPOS_PAT yet. Your only job is to fetch the listing and hand it to the headless script; the script does everything else.

Do exactly this, and nothing else:

1. Call the GroupOS MCP tool `videos_list` with:
     community_id: 67011d987a2a81b28438a3d8
     limit: 100
     created_after: 2026-01-01T00:00:00Z
   Page with the returned `cursor` until `has_more` is false. Expect roughly 152 videos across 2 pages. Scope is 2026 only — do NOT re-read all 1,024 videos.

2. Write every returned item into ONE file as {"items": [ ... ]}:
     /Users/Born/Scorecard/scripts/.videos_2026_dump.json
   Keep the raw objects exactly as returned — do not trim fields.

3. Run:
     python3 /Users/Born/Scorecard/scripts/videos_weekly_check.py /Users/Born/Scorecard/scripts/.videos_2026_dump.json --apply

   That script diffs the dump against digest.videos_catalog, reports NEW and CHANGED videos, upserts what moved, and — only if something moved — runs scripts/zoom_weekly.py, which links the Zoom call by its GMT<date>-<time> filename, ingests the transcript into content_items, embeds it, and refreshes that video's entity dossier.

4. PARTNERS, same pattern (added 2026-08-09 — `partners_refresh` had no job at all and its alarm
   fired for nine days with nothing able to clear it). Call the GroupOS MCP tool `partners_list`:
     community_id: 67011d987a2a81b28438a3d8
     limit: 100
     updated_after: <the date of the last successful partners run, or 30 days ago>
     with_total: true
   The result is large — it will be saved to a file rather than returned inline. Do NOT read that
   file into context. Convert it to {"items": [ ... ]} at
     /Users/Born/Scorecard/scripts/.partners_delta_dump.json
   with a one-line python call, then run:
     python3 /Users/Born/Scorecard/scripts/partners_weekly_check.py /Users/Born/Scorecard/scripts/.partners_delta_dump.json --apply

5. Report back in 3-6 lines: how many videos the dump held, NEW count with titles, CHANGED count
   with the fields that changed, the tail of the chain output (calls, attendance rows, transcript
   chunks, dossiers refreshed), and the partners line (NEW / CHANGED / upserted). If either script
   exits non-zero, say so plainly and quote the failing line — do not describe it as successful.

Notes that matter:
- Attendance is STORED, NEVER SHOWN to members (Andy's ruling 2026-08-07). Do not build anything that surfaces who attended a call.
- Transcripts cite the LIBRARY video (app.mds.co/videos/<id>), never a Zoom URL.
- Do not edit any SQL, workflow or n8n. This task only fetches, diffs and runs the two scripts above.