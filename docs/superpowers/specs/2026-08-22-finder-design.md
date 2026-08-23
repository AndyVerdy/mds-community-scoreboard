# #108 · The Finder — one lane, composable filters, every data layer

**Status:** design approved by Andy 2026-08-22, then widened twice by him the same day · **Ticket:** #108
(Sprint 4) · **Size:** phase 1 is 1–2 days; later phases get their own plans
**Author:** Claude (Olivia stream) · **Replaces:** `2026-08-22-member-finder-design.md`

**Andy's three rulings that shape this document**

1. *"It should work in general. Not just for an event."* — the lane is not event-scoped.
2. *"Isn't it supposed to be one tool, not two? What if I need a combination of member filters on top
   of content?"* — ONE tool with two filter groups (**who** and **what**) and a switch for what comes
   back; never a member tool plus a content tool that the model has to join by hand.
3. *"Cover all data layers… and make sure our restrictions work properly: we process everything, but
   answers can be gated — revenue is not disclosed, but that doesn't mean we can't use it in
   filters."* — filtering power and disclosure are **separate axes**. §5 is that separation, written
   as a mechanism instead of a habit.

---

## 1. The problem

Belen asked which resellers were coming to the Summit. Millie named brand owners and missed the three
real resellers. Two causes, both verified live 2026-08-22:

1. **No filter vocabulary.** Every tool carries its own hand-picked parameter list, and none can
   express chat membership or business model as a *filter*:

   | tool | filters it accepts | names? |
   |---|---|---|
   | `member_match` / `_v2` | city, state, country, sales channel, category | yes |
   | `member_count` | niche, city, state, chapter, band (+ `group_by`) | no — counts only |
   | `event_who` / schedule `op=people` | event name, limit (matching is free-text topic words) | yes |
   | `content_search` / `_v2` | terms, sources, chat, date floor, author | yes |
   | `content_stats` | metric, terms, sources, date floor — **no chat, no author** | counts only |
   | `video_search` / `_v2` | query, call type, order, video id — **no speaker, no year, no category** | yes |

   So "reseller" arrives as topic words matched against self-written text: a brand owner who once
   wrote about wholesale matches; a real reseller who never wrote about it does not. #111 (7 names vs
   1, same question, different phrasing) is the same defect from another angle.

2. **`event_who` is misrouted.** Every tool named `event_*` is POSTed to `/api/olivia/schedule`, and
   `event_who` sends only `p_event` + `p_limit` — no `op` — so the route falls through to its default
   `op="next"` and returns the **public agenda**. Proof (same phone, 2026-08-22):

   ```
   {"p_event":"Summit","p_limit":5}  -> {"viewing":"public agenda…","next":[{"name":"Arrivals"…
   {"op":"people"}                    -> {"ok":false,"note":"this person is not registered…"}
   ```

Underneath both: **filters do not compose, and they do not compose across layers.** "Resellers going
to the Summit, in Europe, and what they said about TikTok" spans four tools that cannot be combined,
so Millie guesses.

## 2. Story and acceptance criteria

*As a member, I can ask for people, content, videos, events or partners by any combination of filters
— what someone does, where they are, which chat they're in, which event they're attending, what was
said, when, and by whom — narrow it further in my next message, and get real matches with the reason
each one matched, without ever being shown something I'm not allowed to see.*

**Accept when (phase 1):**

1. `find` answers "which resellers are coming to the Summit" with the **union** — chat membership OR
   declared business model — each person carrying their reason. Live baseline (Summit
   `recrATwhUDA55iQN5`, 2026-08-22): **21** = 15 in *MDS Resellers* + 9 declared wholesale, 3 both.
   Ten named, `total: 21` returned honestly.
2. The same question with no event returns the community set: **99** members.
3. A follow-up narrows the same filter set (resellers → Summit → `country`), no fresh guess.
4. `return: "breakdown"` with `group_by: "country"` returns counts per country, no invented names.
5. `event_who` reaches attendees, not the agenda.
6. **The disclosure engine holds** (§5): a green-only filter set may name people; a filter set that
   touches an amber field answers with counts only; no amber value is ever printed beside a name; no
   red field is filterable or returnable; ≤10 names with the true total; event names only for a
   registered asker; no Staff or removed records in a names list.
7. Leak gate EXIT 0 with the new finder checks · proven on **staging** · Andy promotes.

**Non-goals (phase 1):** retiring `member_match` / `member_count` / `event_who` · semantic search
(stays in `expertise_search` and the `_v2` content lanes) · any new table · any write.

## 3. One lane, two filter groups

```
Millie (Answer Seed tool: find)
        │  { who: {...}, what: {...}, return: "people|content|videos|events|partners|count|breakdown" }
        ▼
Answer Tool ── tool_name === 'find' ──►  POST https://digest.mds.co/api/olivia/find
                                            (mds-digest-web route — the DISCLOSURE ENGINE lives here)
                                                 │ PostgREST reads · no new tables · no writes
                                                 ▼
   people layer · content layer · video layer · event layer · partner layer · forms layer
```

**who** filters describe *people*; **what** filters describe *things*. Used together they intersect:
the who-set resolves to member ids and constrains the content/video query — or the authors of matching
content become the who-set.

The cross-join is real, verified 2026-08-22: `content_items.meta->>'sender_member'` carries the
author's member id on **99.1%** of WhatsApp messages, **94.5%** of Facebook comments and **87.0%** of
Facebook posts. Call transcripts carry no author — who spoke lives in `video_speaker_links` +
`speakers.at_member_id` (#103, 87% library coverage), so transcript answers join through speakers.

### 3.1 Request

```jsonc
POST /api/olivia/find              // header: X-Olivia-Secret. The lane writes nothing.
{
  "phone": "1786…",                 // the asker — resolves identity and entitlements
  "who": {
    "chat": ["MDS Resellers"], "business_model": ["reseller"], "event": "Summit Singapore",
    "city": [], "state": [], "country": ["Spain"], "band": ["5-10M"], "chapter": [],
    "niche": [], "category": [], "expertise": "amazon ppc", "speaker_of": null,
    "sku_min": null, "brands_min": null, "years_selling_min": null, "age_band": null
  },
  "what": {
    "terms": ["tiktok"], "sources": ["wa_message","fb_post","call_transcript"], "kinds": [],
    "chat": [], "since": "2026-01-01", "until": null,
    "call_type": null, "video_category": [], "speaker": [], "year": null,
    "event_type": null, "partner_category": [], "featured": null
  },
  "return": "people",               // people | content | videos | events | partners | count | breakdown
  "group_by": null,                 // country | state | city | band | niche | business_model | chat |
                                    // chapter | source | year | call_type | video_category | partner_category
  "limit": 10
}
```

**AND across kinds, OR inside a kind.** Unknown keys are rejected (`400 unknown filter: …`) — the
allowlist is closed, so a drifting tool schema can never widen what Millie may read. At least one
filter is required; there is no whole-database dump.

### 3.2 Response

```jsonc
{
  "total": 21, "shown": 10, "capped": true,
  "filters_echo": { "who": {...}, "what": {...}, "unmatched": [], "disclosure": "green" },
  "event": { "name": "MDS Summit Singapore", "at_record_id": "recrATwhUDA55iQN5" },
  "people":  [ { "name": "Ariel Tung", "reasons": ["in MDS Resellers", "wholesale & arbitrage"],
                 "city": "Singapore", "niche": null } ],
  "items":   null,      // content / videos / events / partners rows, by `return`
  "breakdown": null,    // [{ "value": "Spain", "count": 4 }, …]
  "note": "…"           // wording rules for the model, generated from the disclosure decision
}
```

`filters_echo` is how follow-ups narrow with no server state: the normalised set rides back in the tool
result, and the next call re-sends it plus the new filter.

## 4. Every data layer, and what it contributes

| Layer | Tables (live rows, 2026-08-22) | Filterable by | Returnable as |
|---|---|---|---|
| People | `members` 668 · `member_attributes` 5,751 · `member_profiles` 5,983 · `member_niches` 1,925 · `member_expertise` 15,938 · `member_state_snapshot` | chat, business model, geography, band, niche, category, expertise, chapter, tenure, activity | people |
| Events | `events_catalog` 1,443 · `event_registrations` 18,123 (view `event_registrations_live`) | event name, type, phase, chapter area, city, past/upcoming | events; attendance filter for people |
| Content | `content_items` 54,631 (`wa_message`, `wa_digest`, `fb_post`, `fb_comment`, `application`, `call_transcript`) · `summaries` 1,978 | terms, source, kind, chat, author (member id), date range | content |
| Video | `videos_catalog` 1,033 · `video_speaker_links` 1,391 · `speakers` 578 · `video_access` 34,236 | topic, call type, **speaker**, **category**, **year**, duration, entitlement | videos |
| Partners | `partners_catalog` 504 · `partner_reviews` 928 | category, featured, fresh deal, rating, reviews, access restriction | partners |
| Forms | `form_responses` 13,722 · `form_answers_exploded` 154,583 · `form_question_map` 1,314 | question, answer value, form, year — **aggregate only** | breakdown / count |
| Judgement | `entity_dossier` 3,046 (event 1,438 · video 1,033 · partner 504 · chapter 71) | — | `fit_reason` / `strength_note` on returned items |
| Graph | `member_edges` 142,758 · `member_events` 25,881 · `call_attendance` 4,372 | co-engagement, activity recency — **internal only** | never surfaced |
| Personas | `member_personas` 761 · `member_personas_history` 2,977 | the ASKER's own only | never about another member |

Caveats to state in answers rather than hide: business model is self-declared and as old as the
member's last form (91 of the 97 Summit attendees have one); chat membership is behaviour, so a brand
owner can sit in *MDS Resellers* to watch; the label vocabulary is dirty (legacy set + app-v3 set, plus
8 rows where two labels were joined by an apostrophe — matched, not repaired); and **five** catalog rows
match "Summit Singapore" (the Summit plus Night Out, Speaker's Lunch, Women's Lunch, Pre-Event Dinner),
so resolution prefers the exact name, then the shortest, and always echoes what it picked.

## 5. The disclosure engine — filtering and showing are different rights

The binding rulebook is `OLIVIA_SHAREABLE_FIELDS.md`. This section turns it into a mechanism, so a new
filter cannot quietly become a new disclosure. Every field in the registry carries one class:

- 🟢 **show** — filterable, groupable, printable beside a name. The member-card set: name,
  city/state/country, chapter, niche, categories, expertise text, about, fun fact, revenue **band**,
  sales channels, business model, Facebook link — plus chat membership and event attendance, each with
  its own gate below.
- 🟡 **aggregate** — filterable and groupable, **never printable beside a name**: SKU count, brands,
  employees, years selling, age band, revenue sums, engagement and expertise percentiles, activity
  recency, co-engagement, individual form answers.
- 🔴 **internal** — never filterable, never returned: exact revenue, email, phone, address, Stripe and
  payment data, internal record ids, removal reasons, another member's persona or billing.

**The rules the engine enforces**

- **R1 — filter rights.** A filter may use 🟢 and 🟡 fields. A 🔴 field is rejected at parse time; at
  most it is a join key.
- **R2 — naming rights.** If any 🟡 filter is active, the answer may **not name people** — it returns a
  count or a breakdown. Naming who matched "500+ SKUs" *is* disclosing their SKU count, however the
  sentence is phrased. 🟢-only filter sets may name.
- **R3 — reason rights.** Reason lines quote 🟢 values only.
- **R4 — small buckets.** With a 🟡 filter active, breakdown buckets below 3 report as "fewer than 3";
  a one-person bucket re-identifies the person the count was meant to protect.
- **R5 — event gate (#98).** Attendee names require the asker to hold a registration row for that
  event; otherwise counts only, with no explanation of internals.
- **R6 — entitlement (#101).** Video results respect `video_access`; a restricted video may be listed
  by title with content withheld — never denied, never invented.
- **R7 — content access.** Content results pass through the existing gated read path (`access_rule`,
  `sensitivity`, chat membership) rather than re-implementing it; a chat digest is visible only to a
  member of that chat.
- **R8 — population (#106).** Staff, removed and unknown-status records never appear in a names list
  and are excluded from the total — a count whose members cannot be shown is a number that lies.
- **R9 — ceilings.** ≤10 names with the true total (#96) · no score, rank or percentile in any field or
  note · the asker is never their own match · deterministic order (engagement, then name) with **no
  equalizer**, because a filter question must return the same set to the same asker twice · the lane
  writes nothing, so no audit header is needed.

**One ruling needed from Andy (default assumed, one line either way):** may Millie name *which chat*
someone is in, to an asker who is not in that chat? Default = **yes** — MDS chats are topical interest
groups, the reason line is the point of the feature, and the chat directory is already discoverable
in-app. If the answer is no, chat-only matches still appear, with the reason reading "active in
reseller discussions" and the chat name withheld.

## 6. Phases

- **Phase 1 (this ticket).** The lane, the parser with both filter groups, the full field registry and
  the disclosure engine, `return: people | count | breakdown`, and the `event_who` fix. Belen's
  question answers correctly end to end.
- **Phase 2 (own plan).** `return: content | videos` — the cross-join (who-set → author/speaker
  constraint) plus the video filters that exist in the data but in no tool today: speaker, year,
  category. Also exposes two backend parameters the model has never been able to reach: content
  `kinds`, and an end-date on search (only the browse lane has one).
- **Phase 3 (own plan).** `return: events | partners`, forms aggregates through the existing PII
  filter, and retirement of `member_match` / `member_count` / the schedule matcher once the finder has
  carried their traffic for a sprint.

Every phase reuses the same parser, registry, engine, echo and gate — that is the whole reason for one
lane.

## 7. Rollout and revert

The route ships first as dead code (revert: `git revert` + redeploy). The tool and the `event_who` fix
go on **staging** only, are probed there with the #99 canary pattern, pass the leak gate at EXIT 0, and
are snapshotted before Andy promotes (revert: `olivia_wf.py rollback <snapshot>`). Before the promote,
Andy decides whether to run the 100-question eval bank — recommended, because the one real risk is the
model reaching for `find` where `expertise_search` was the better tool.

## 8. Follow-ups (filed, not built here)

- #111 should close as a side effect of the concept map — verify against executions 97152 / 97286.
- #106 stays open for the lanes outside the finder.
- The 8 corrupt `OEM Design & Development'Wholesale and/or Arbitrage` rows need an Airtable fix.
- #32 carries the uncached-answer-node finding; caching the prefix makes this tool's schema ~free.
- `content_stats` cannot filter by chat or author while `content_search` can — phase 2 makes that
  inconsistency disappear rather than patching it twice.
