> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Signal inventory — what the dossier vision (#29) has, can derive, and is MISSING

**Written 2026-07-31 on Andy's direction: "Write all the missing bits and pieces, and we will get
it."** The vision: a dynamic dossier per member — and a file per entity (video, event, partner,
thread) — fed by every behavioral signal: what they watch, attend, ask, say, click, when they're
online. This doc is the shopping list. The MISSING table is the part to action — each row names
what to get, who owns it, and what it unlocks.

## ✅ HAVE — captured today, usable now

| signal | where | freshness |
|---|---|---|
| Member profile: niches, channels, revenue, business model, geo, age band, SKUs, brands | AT mirror (`member_attributes`/`member_profiles`) | daily sync |
| WA group messages (who says what, where, when) | `content_items` | continuous since Jul 2025 |
| FB posts + comments (incl. image text) | `content_items` | Mon/Thu manual SOP |
| Olivia Q&A history (every question = an interest signal, topic-labeled) | `olivia_messages` + labels | live |
| Olivia 👍/👎 reactions | `olivia_feedback` | live |
| Event registrations + confirmed attendance, back to 2018 | `event_registrations` (17,744) | daily |
| Partner catalog + 922 reviews | `partners_catalog` | snapshot |
| Video catalog (titles, descriptions, restrictions) | `videos_catalog` (1,009) | manual import |
| Chapter membership + chapter files | `chapters_catalog` + live stats (#6) | live |
| Personas v2 (signal-cited cards — the member file's first draft) | `member_personas` | nightly |
| Chat memberships + WA-channels-active-30d | `members` + AT | daily |
| FB engagement score | AT field | weekly |
| Application v3 answers (own answers searchable) | `content_items` source=application | on submit |

## 🔨 DERIVABLE — no one to ask, just build (lands inside #29)

| signal | derived from |
|---|---|
| Activity-hours pattern (when someone is online) | message timestamps (WA/FB/Olivia) — no presence API needed |
| Topic interests over time | their questions, posts, replies (already topic-labeled) |
| Conversation graph (who talks to whom) | WA replies/mentions + FB comment threads |
| Engagement trajectory (rising/fading) | message counts + event attendance over time |
| Entity files for videos/events/partners/threads | existing embeddings + descriptions + who-engaged lists |

## 🚨 MISSING — the "go get it" list, in priority order

| # | missing signal | who owns getting it | what exactly to ask for | what it unlocks |
|---|---|---|---|---|
| 1 | **App behavior: video views, watch time, searches, screen visits, logins** — the app logs NONE of it today | Pavel / app team | Emit events `(member_id, event_type, object_id, timestamp)` to a Supabase table or endpoint we provide (`digest.member_events` exists and is EMPTY, built for exactly this) | The single biggest dossier signal: what each member actually consumes. **Every day it's not logging is history lost** |
| 2 | **GROUPOS_PAT (API key)** — standing top infra ask | Andy / GroupOS | A PAT for the GroupOS API | Per-member partner-offer CLAIMS (real purchase intent), live video/partner refresh (#17), app last-seen |
| 3 | **Census answers into the warehouse** (#20) | us (build) + Andy (priority call) | Load the 3 census Typeforms into `content_items` / attributes | Freshest self-reported revenue, channels, likes/dislikes — the stated-preferences half of the file |
| 4 | **Video transcripts** — no video has one; content-level matching is title/description-only | Andy (Mux/AAI anchor project exists, CU `2531q-98637`) | Turn on the transcription pipeline | "This video talks about C" at the content level, not the title level — the exact match-fuel in Andy's example |
| 5 | **Call/recording attendance** — who joins Mogul/Expert calls; calls data unmapped ("coming soon") | events team / Zoom exports | Attendance lists per call | Interest + habit signal for the most engaged surface |
| 6 | **Email/digest engagement** — opens + link clicks per member | GHL / Resend consolidation (existing project) | Route sends through the tracked path with per-member click log | Passive-interest signal for members who read but never post |
| 7 | **Intercom support history** per member | us (Intercom API; sync exists for last-seen) | Pull conversation topics into the warehouse | Pain-points dimension of the file |
| 8 | **Explicit likes/dislikes flow in Olivia** — today only 👍/👎 on answers | us (build, small) | "Want more/less of this?" capture into preferences | Stated preferences with zero forms |
| 9 | **WA online presence** — not exposed by Meta/Whapi | nobody (platform limit) | — (use the derivable activity-hours pattern instead) | honesty row: don't chase it |

## Ground rules already standing
- Personas/behavior are **owner-only** — match-don't-quote across members (gate-enforced).
- "Every step, every breath" ships only behind the **written privacy position (#19)**.
- Population = **every active member by at_member_id**, never just WA/phone holders.

**Next:** #29 round 1 (the research memo) consumes this inventory; rows 1–2 are the ones to
action THIS WEEK so history starts accumulating while research runs.
