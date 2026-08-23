# #108 · Member Finder — one lane for composable member filtering

**Status:** design approved by Andy 2026-08-22 · **Ticket:** #108 (Sprint 4) · **Size:** 1–2 days
**Author:** Claude (Olivia stream) · **Supersedes:** the original #108 scope ("attendees ∩ chat
membership / business model tool"), widened by Andy on 2026-08-22: *"It should work in general. Not
just for an event."*

---

## 1. The problem

Belen asked which resellers were coming to the Summit. Millie named brand owners and missed the real
resellers. Two independent causes, both verified live on 2026-08-22:

1. **No filter vocabulary for "reseller".** Every member-facing tool carries its own hand-picked
   parameter list, and none of them can express chat membership or business model as a *filter*:

   | tool | filters it accepts | names? |
   |---|---|---|
   | `member_match` / `member_match_v2` | city, state, country, sales channel, category | yes |
   | `member_count` | niche, city, state, chapter, band (+ `group_by`, which *can* group by business model) | no — counts only |
   | `event_who` / schedule `op=people` | event name, limit (matching is free-text topic words) | yes |

   So "resellers" can only arrive as topic words, and topic words are matched against
   `expertise` / `categories` text. Brand owners who *write* about wholesale match; actual resellers
   who don't, do not. #111 (results swing 7 names vs 1 with the model's free-text phrasing) is the
   same defect seen from another angle.

2. **`event_who` is misrouted.** `Answer Tool` sends every tool whose name starts with `event_` to
   `https://digest.mds.co/api/olivia/schedule`, and the `event_who` schema carries only `p_event` and
   `p_limit` — no `op`. The route defaults to `op="next"`, so the LLM lane gets the **public agenda**
   where it asked for attendees. Proof (same phone, 2026-08-22):

   ```
   POST /api/olivia/schedule {"p_event":"Summit","p_limit":5,"phone":…}
     -> {"event":"MDS Summit Singapore","viewing":"public agenda (not registered…)","next":[{"name":"Arrivals"…
   POST /api/olivia/schedule {"op":"people","phone":…}
     -> {"event":"MDS Summit Singapore","ok":false,"note":"this person is not registered…"}
   ```

   The attendee code (`op=people`) and the `digest.event_who(p_phone, p_event, p_limit)` RPC both work.
   Only the deterministic plan lane (`intent==='eventwho'` in `Plan Request`) reaches the RPC; the
   LLM's own tool call never does.

Underneath both: **filters do not compose.** "Resellers, at the Summit, in Europe, 5–10M, grouped by
country" spans three tools that cannot be combined, so Millie falls back to guessing.

## 2. Story and acceptance criteria

*As a member, I can ask for people by any combination of what they do, where they are, which chat
they are in and which event they are attending — and narrow it further in my next message — and get
real matches with the reason each person matched.*

**Accept when:**

1. `member_find` answers "which resellers are coming to the Summit" with the **union** set — chat
   membership OR declared business model — and each person carries the reason they matched.
   Live baseline (Summit `recrATwhUDA55iQN5`, 2026-08-22): **21** people = 15 in *MDS Resellers* + 9
   declared wholesale, 3 in both. Named: 10, with `total: 21` returned honestly.
2. The same question with no event ("who in MDS resells") returns the community set: **99** members.
3. A second filter narrows the first: resellers → attending the Summit → `country=Spain` runs as one
   filter set, not a new guess.
4. `mode=breakdown&group_by=country` over that set returns counts per country, no names invented.
5. `event_who` reaches attendees, not the agenda (routing fix), proven by an execution.
6. Policy holds in the new lane: ≤10 names with the true total · attendee names only for an asker
   registered for that event · no Staff/non-member rows in a names list · no scores or ranks in
   output.
7. Leak gate EXIT 0 with new finder checks · proven on **staging** · Andy promotes.

**Non-goals (this ticket):** retiring `member_match` / `member_count` / `event_who` (they keep
working; migration is a later ticket) · embedding/semantic search (stays in `expertise_search`) ·
any new database table · writing anything (the lane is read-only).

## 3. Architecture

```
Millie (Answer Seed tool: member_find)
        │  tool_args = { filters…, mode, group_by, limit }
        ▼
Answer Tool  ── tool_name === 'member_find' ──►  POST https://digest.mds.co/api/olivia/find
                                                   (mds-digest-web app route — POLICY lives here)
                                                        │  PostgREST reads, no new tables
                                                        ▼
        digest.members · digest.member_attributes · digest.member_profiles
        digest.events_catalog · digest.event_registrations_live · digest.chats
```

Why an app route and not an RPC: Andy's 2026-08-17 rule — new lanes are app routes, retrieval in SQL,
**policy in git**. It also makes the revert a `git revert` + redeploy rather than a migration.

Why one lane: the disclosure rules (name cap, event gating, staff exclusion) are today re-implemented
per tool. That divergence is what let the `test-andy-8153` row surface real names through the event
lane while the search lanes correctly excluded it (#98/#106).

### 3.1 Request contract

```jsonc
POST /api/olivia/find          // header: X-Olivia-Secret (the lane writes nothing — see 5.6)
{
  "phone": "1786…",            // the asker; required; resolves the member + their entitlements
  "filters": {
    "chat":           ["MDS Resellers"],        // chat display names
    "business_model": ["reseller"],             // free labels, normalised (see 4.2)
    "event":          "Summit Singapore",       // event name words
    "city":           ["Miami"],
    "state":          ["Texas"],
    "country":        ["Spain", "Portugal"],
    "band":           ["5-10M"],                // 1-5M | 5-10M | 10-20M | 20M+
    "niche":          ["Supplements"],
    "category":       ["Home"],
    "expertise":      "amazon ppc"              // text contains, case-insensitive
  },
  "mode":     "names",         // names | count | breakdown
  "group_by": null,            // country | state | city | band | niche | business_model | chat
  "limit":    10               // names mode only; hard-capped at 10 (§5)
}
```

Semantics: **AND across filter kinds, OR inside a kind.** Absent or empty filters are ignored. An
unknown filter key is rejected with `400 unknown filter` — the allowlist is closed, so a future tool
schema drift cannot silently widen what Millie can read.

### 3.2 Response contract

```jsonc
{
  "total": 21,                       // the honest count over the WHOLE filtered set
  "shown": 10,
  "capped": true,                    // total > shown
  "filters_echo": { … },             // the normalised filter set — the follow-up starts from this
  "event": { "name": "MDS Summit Singapore", "at_record_id": "recrATwhUDA55iQN5" },
  "people": [
    { "name": "Ariel Tung",
      "reasons": ["in MDS Resellers", "wholesale & arbitrage", "attending MDS Summit Singapore"],
      "city": "Singapore", "niche": null }
  ],
  "breakdown": null,                 // mode=breakdown: [{ "value": "Spain", "count": 4 }, …]
  "note": "…"                        // wording guidance for the model (see 5.4)
}
```

`filters_echo` is what makes follow-ups work with no server state: the normalised set rides back in
the tool result, stays in the conversation, and the next call re-sends it plus the new filter.

## 4. Filter vocabulary and data sources

### 4.1 Sources (verified live 2026-08-22)

| filter | source | live coverage |
|---|---|---|
| chat | `digest.members.channels_present` (WA DB matcher — real WhatsApp group membership) | 18 chats; 97/97 Summit attendees have chat data |
| business model | `digest.member_attributes.business_model` ← Members DB "Business Model" lookup ← **Forms** table (`tblblwPcgqhkPTVec`, census/application answers) via `derive_member_attributes()` | 91/97 Summit attendees, 521/560 active members carry a value |
| event attendance | `digest.events_catalog` (name → `at_record_id`) → `digest.event_registrations_live` — the #89/#98 authority | 97 Summit attendees hold a member row |
| city / state / country / band / niche / category / expertise | `digest.member_attributes` | expertise 88/97 |

Known data caveats, to be stated in the answer rather than hidden:

* Business model is **self-declared** and as old as the member's last form. Chat membership is
  behaviour: a private-label owner can sit in *MDS Resellers* to watch. This is exactly why the union
  is reported with a per-person reason (Andy's ruling 2026-08-22).
* The vocabulary is dirty: the legacy set (`Private Label`, `Wholesale and/or Arbitrage`,
  `OEM Design & Development`, `Brand Management and/or Agency`) and the app-v3 set (`Own Brand`,
  `Wholesale, Resale & Dropshipping`, `Agency, Consulting & Brand Management`, `Omnichannel`) both
  appear, plus one corrupt value (`OEM Design & Development'Wholesale and/or Arbitrage`, 8 rows) where
  two labels were joined by an apostrophe. The synonym map covers all of them; the corrupt value is
  reported to Andy, not silently repaired.
* **Five** catalog rows match "Summit Singapore" (verified live 2026-08-22): the Summit itself plus
  *Night Out*, *Speaker's Lunch 2026*, *Women's Lunch 2026* and *Pre-Event Dinner*. Event resolution
  prefers an exact name match, then the shortest name (side events append words), and the resolved
  name + record id always ship in the response so a wrong pick is visible.

### 4.2 Normalisation (in code, not in the prompt)

A small curated map, in the route, applied to every incoming label:

```
reseller | resellers | reselling | wholesale | wholesaler | arbitrage | dropship | dropshipping
    -> business_model ∈ { "Wholesale and/or Arbitrage", "Wholesale, Resale & Dropshipping",
                          "OEM Design & Development'Wholesale and/or Arbitrage" }
    -> chat            "MDS Resellers"          (the union, per Andy)
private label | pl                    -> { "Private Label" }
brand owner | own brand               -> { "Own Brand", "Private Label" }
agency | brand management | consulting-> { "Brand Management and/or Agency",
                                           "Agency, Consulting & Brand Management" }
oem | manufacturing                   -> { "OEM Design & Development" }
```

Chat names normalise case-insensitively against `digest.chats.chat_name`, with the `MDS ` prefix
optional ("resellers chat" → *MDS Resellers*). An unresolvable chat or model label is **not silently
dropped**: it comes back in `filters_echo.unmatched`, and the note tells Millie to say which part of
the ask she could not honour.

Putting the map in code follows [[feedback_code_beats_prompt_rules]] and neutralises #111: the
answer no longer depends on which topic words the model invents.

## 5. Policy — the reason this is one lane

1. **Name cap (#96).** At most 10 names per answer; `total` is always the true count over the whole
   filtered set. The cap is a display cap, never a processing cap.
2. **Event gating (#98).** If `filters.event` is set, names are returned only when the asker is
   present in that event's `event_registrations_live` rows. Otherwise: counts and breakdowns only,
   with the existing "answer with the count and stop" note. `event.people` is never an access
   authority — it carries staff and test rows.
3. **Staff and non-members (#106).** Rows whose `membership_status` is `Staff`, `Removed - *` or null
   never appear in a `names` result. They are also excluded from `total` — a count the asker cannot be
   shown the members of would be misleading. (#106 stays open for the lanes that do not yet route
   through the finder.)
4. **Scores stay internal, and the order is deterministic.** Ordering is `engagement_score` then
   name; no score, rank or percentile is ever emitted. The finder deliberately does **not** run the
   equalizer: a filter question has one correct answer set, and rotating it would make "which
   resellers are coming" return different people to the same asker on the same day. The equalizer
   stays where it belongs — the recommendation lanes.
5. **Self-exclusion.** The asker is never returned as their own match.
6. **Read-only, no logging.** The lane writes nothing at all — not even `olivia_recommendations`,
   because it does not run the equalizer (§5.4). That makes the `X-Olivia-Audit` header moot here:
   there is no write for an audit to suppress. If a later ticket adds equalizer behaviour to this
   lane, the header rule comes with it.

## 6. `event_who` routing fix

Smallest correct fix, kept inside this ticket because the finder is useless if the model's own
attendee call still lands on the agenda:

* `Answer Tool` maps `member_find` → `/api/olivia/find`, and `event_who` → `/api/olivia/schedule`
  **with `op: "people"` merged into the body** (the same shape the deterministic lane already proves).
* `event_who`'s tool description gains one line pointing at `member_find` for any filtered attendee
  question ("resellers who are coming", "who from Europe is attending").
* No change to `digest.event_who` or to `op=people` itself.

## 7. Gate additions (`scripts/olivia_leak_gate.py`)

* `member_find` with an unknown phone returns zero rows (fail closed).
* anon key is denied on `/api/olivia/find`.
* Staff record never appears in a `names` result (probe with the known Staff at_member_id).
* names length ≤ 10 for a filter set whose `total` exceeds 10.
* event filter + unregistered asker returns no names.
* no `score`, `rank`, `pct` or `engagement` key anywhere in the response body.

## 8. Test plan and rollback

**Staging only, then Andy promotes.**

1. Route ships first to prod (`mds-digest-web`) — dead code until a tool calls it. Revert = git revert
   + redeploy.
2. `olivia_wf.py snapshot` → edit **staging** (`bqHstPDi84uOhTCJ`) under the lock: `Answer Seed` tool
   schema, `Answer Tool` routing, `Plan Request` guard for follow-up narrowing.
3. Staging probes (silent lane, no real sends), each read from the execution:
   * "which resellers are coming to the Summit" → 21 total, ≤10 names, reasons present.
   * "who in MDS resells" → 99 total.
   * follow-up "of those, who is in Europe" → filter set carried, smaller total.
   * "group them by country" → breakdown rows, no names.
   * as a **non-registered** asker → counts only, zero names.
   * `event_who` on its own → attendees, not the agenda.
4. `python3 scripts/olivia_leak_gate.py` EXIT 0 (with the new checks).
5. Snapshot, hand to Andy for `promote`. Rollback = `olivia_wf.py rollback <snapshot>` for the
   workflow, git revert for the route.

## 9. Follow-ups (not this ticket)

* Retire or re-point `member_match`, `member_count` and the schedule `op=people` matcher at the finder
  (removes three divergent policy implementations).
* #111 closes as a side effect of §4.2 — verify with the two executions on record (97152 / 97286)
  before claiming it.
* #106 remains open for the lanes outside the finder.
* Report the 8 corrupt `OEM Design & Development'Wholesale and/or Arbitrage` rows to Andy for an
  Airtable-side fix; the finder tolerates them, it does not clean them.
