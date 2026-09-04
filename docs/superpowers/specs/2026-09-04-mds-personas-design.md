# MDS Personas — design spec (2026-09-04)

Staff-only library of members inside the digest portal: browse faces like a streaming app, open a
member's character sheet, click any stat to see everyone strong in it. Visual design is final and
lives in the Claude Design handoff (`docs/design/mds-personas/` in mds-digest-web: `README.md`,
`MDS Personas.dc.html`). This spec covers what the handoff does not: data, plumbing, jobs, gating.

## Decisions (Andy, 2026-09-03/04)
- Staff only. Scores, ranks and evidence are visible. Gate = the existing `/admin` session (OTP, `@mds.co`).
- Population = every active member: Current, New, Not Renewing, Paused, Staff (758 today), keyed by `at_member_id`.
- No direct A-vs-B comparison. Browsing is library → sheet → cohort → sheet.
- No archetype labels. The 18 categories and 33 detail stats are the vocabulary.
- All 51 stats visible on the sheet; a stat with no signal is named, not drawn.
- Asks and gives are mapped stats (from the ledger's persona-asks / persona-gives evidence), free text underneath.
- Badges: at peak · holding · fading, from today vs the all-time peak. No "rising" until the ledger keeps history.

## Screens (see handoff README "Screens" for pixels)
1. `/admin/personas` — Library: search, 18 category chips, rails (Newest · At their peak · Strong in TikTok Shop · Strong in Logistics & 3PL · Strong in AI & Automation · Active in the chats this month).
2. `/admin/personas/[id]` — Member sheet: portrait, blurb, focus, gives/asks chips, 18 + 33 stats, similar, companions, link to Member 360.
3. `/admin/personas/stat/[key]` — Cohort: everyone ≥ 60 on the stat, sorted by today's value; detail-stat chips for a category, parent link for a detail stat.

## Data (warehouse, all existing unless marked NEW)
| View-model field | Source |
|---|---|
| name, status, joined, engagement | `digest.member_profiles` (status in the active set) |
| city, niche, channels, since, title | `digest.member_attributes` |
| persona summary, focus, gives, asks, engagement pattern | `digest.member_personas.persona` |
| **blurb** (2–3 friendly sentences) | NEW `persona.blurb`, written by the nightly persona refresh alongside the summary |
| stats: value, peak, badge, rank, signals | `digest.member_expertise`: value = `pct×100`, peak = value×peak_score/score, badge = score vs 0.85·peak, rank = `rank_in_topic`, signals = `evidence` |
| ask/give mapping | `member_expertise.evidence` keys `persona_asks_hits` / `persona_gives_hits`, plus `weakness_score > 0` = ask |
| taxonomy | `digest.expertise_topics` (18 parents, 33 children) |
| photo | NEW `digest.member_photos` (at_member_id, storage_path, width, source, fetched_at), files in Supabase Storage bucket `member-photos` |
| chats activity | `digest.members.msgs_30d` (max over the member's phones) |

### RPCs (SECURITY DEFINER, service_role only, `digest` schema)
- `personas_library()` → one row per active member: id, name, status, city, joined, level, top2 categories, photo url, msgs_30d, at_peak_count. One call feeds every rail and the search.
- `personas_sheet(p_id)` → the member row + 51 stat rows + mapped asks/gives + persona fields.
- `personas_cohort(p_stat)` → members with value ≥ 60 on that stat, sorted desc, with the stat value and top2.
- `personas_related(p_id)` → similar (cosine over the 18 category values, top 5) + companions (≥ 75 on one of the member's ask stats, top 5), each with the reason string.
Similar/companion math is SQL over `member_expertise`, not JavaScript, so it stays consistent with Millie's lanes.

### Photos
`scripts/cache_member_photos.py` (nightly, after the members mirror): for every active member without a fresh photo, read the Airtable record (`Picture URL` / `Headshots` attachment thumbnails ≥ 120 px, else the `Photo` text field's Typeform or Drive URL), resize to 320 px JPEG, upload to Storage, upsert `member_photos`. Airtable attachment URLs expire in hours, so the portal never links them live. 115 of 758 have no usable photo today → InitialsTile. Second source (GroupOS avatars) is a follow-up.

### Blurb
The persona refresh job gains one field: `blurb` — two or three sentences, warm, no numbers, no jargon, written from the persona summary. Until it exists the sheet shows the first sentences of the summary.

## Interactions and rules
- Card → sheet. Stat name, detail stat, gives chip, asks chip, "all n strong here" → cohort. Cohort "part of X" → category cohort.
- Level badge = mean of the member's top-3 category values. Gold at ≥ 70 on cards, ≥ 80 for chips.
- Rails cap at 24 cards; cohort pages page in blocks of 96.
- Search matches name, city and any stat name where the member is ≥ 60.
- Theme: dark default, light variant, toggle persisted per user.

## Out of scope (own tickets)
Rising badge (needs a nightly ledger snapshot) · GroupOS avatars as a second photo source · service topics (Accounting/Tax/Legal) in the taxonomy · member-facing version.

## Acceptance
- Every active member opens (758) and every one of the 51 stats renders or is named as no signal.
- Photos load from Storage in under a second for a rail of 24; none link to Airtable.
- Similar and companion rows match the SQL for 5 spot-checked members.
- Pixel review against the handoff at 1440 and 390, both themes, all states in README "States".
- Admin gate: an anonymous request to any `/admin/personas*` route or RPC is refused.
