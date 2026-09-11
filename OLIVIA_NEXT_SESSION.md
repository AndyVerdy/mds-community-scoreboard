> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.
- **Always show a ticket's STORY + ACs. Closing needs: short results · short AC checklist (met/not) · before/after numbers.** (Andy 2026-08-03)

# Olivia — next session

## STATE 2026-09-10 (overnight close) — 8 tickets closed · #105 ENFORCING · two things wait on Andy

**Read this first, then the board's close blocks.** Prod n8n `22d81380` · staging `ae74d26d` (clean, re-staged
from prod) · `mds-digest-web` main `588ef08` · gate GREEN · lock free · all 11 nightly jobs green.

**Closed overnight, each with live proof in its board block:** #179 (Make warning read as DOWN) · **#105**
(Meta's signature, front door AND the n8n side door, ENFORCING) · #180 (niche freeze) · #183 (storefront
reshuffle) · #148 (mirror reconcile) · #115 (`IS` folded to Iceland) · #117 (selftest cleanup) · #187 (first
turn ever timed). #152 was verified as already-fixed drift; **#72 was RETIRED** on Andy's word and its
measurement half became #187.

**⚠️ TWO THINGS WAIT ON ANDY — the second one recurs tonight if it is not done.**
1. ~~Reset the Meta app secret.~~ **ANDY'S RULING 2026-09-10: "secret stays".** Not rotating. The value is in the
   chat transcript and in Vault; it is not in the repo. **Do not raise this again** — if it is ever rotated, the
   Vault row needs `vault.update_secret` on `META_APP_SECRET` in the same minutes or the signature check fails.
2. ~~`sudo pmset repeat …`~~ **✅ DONE 2026-09-10, verified live:** `Repeating power events: wakepoweron at
   4:25AM every day`. The machine now wakes five minutes before the 04:30 job, so **#180's root cause is closed**.
   Moving these jobs off the laptop remains the durable answer (**#64**).

**✅ `mds-scorecard-tools` is now a git repository** (2026-09-10, his call) — 59 source files, 1.3MB, deny-by-default
ignores, no credentials in history. **Local only: no remote**, so revert exists but a second machine does not.
Pushing it anywhere publishes the code and is his call.

**Two more his call, neither urgent:** the 10,208-row selftest purge (`--cleanup --yes`, irreversible, his own
history) and #148's lane-skipping (refusing stale rows changes who Millie answers).

**The lesson this session paid for twice.** #105 was built against n8n because the ticket said so; Meta posts to
the RELAY and the handbook's line 72 has said so since July. **Verify a ticket's architecture claim against the
handbook and against live before building to it** — and read payloads before announcing what they are.

## STATE 2026-09-10 (close) — NEXT = **#172 Team research mode, Milestone A** · #147 SQL half live · prod `b4db92d0` · gate 346 EXIT 0 · lock free

**Read first, in this order:** `TEAM_RESEARCH_172_DESIGN.md` (the design, what was ruled and why) → `TEAM_RESEARCH_172_IMPLEMENTATION_PLAN.md`
(15 tasks, test-first, code included) → the #172 block on the board. Andy: *"this task will be the next one in the list."*

**What #172 became today.** Not "Millie with the gates off". Andy's bar: *"answers to all the questions, no gates … similar to the
result if I ask you"*, Supabase only, asker visible. Millie answers from ~20 fixed functions and n8n cannot host a minutes-long turn
(Code node 60 s, webhook ~100 s), so Team mode is a **second runtime beside her**: a Claude tool loop in `mds-digest-web` with a
read-only SQL tool on its own role, a schema catalog, and an ungated semantic search — identity from the staff cookie, a fail-closed
allowlist, per-asker budgets, every query logged and shown. `ask_millie` is deliberately OUT (prod n8n execution on the probe member,
gated evidence). The MCP door is a later ticket on the same principal.

**Before any code — five Day-0 items only Andy can do (design §9):**
1. The go on ONE migration (`scripts/sql/20260911_team_sql_172.sql`: role `millie_team_ro`, view `member_profiles_team`, RPC
   `digest.team_sql`, grants) — live on prod the moment it is applied; a policies fallback is pre-written.
2. The rulebook ruling in writing: Team mode reads through a read-only SQL surface over the deny-list view; that is the
   `OLIVIA_SHAREABLE_FIELDS.md` Team column (opens exact revenue, contacts, Stripe/billing; keeps closed removal reasons, LTV, internal
   notes, lead scoring).
3. Render env, CHECK before add, then Manual Deploy: `MILLIE_TEAM_ASKERS` (proof participants), `VOYAGE_API_KEY`, `NODE_VERSION=22`.
4. A member and an event as placeholders for Q1–Q3, Q14, Q17–Q19 (outside the repo).
5. Two or three staff read the twenty questions and swap the ones they would never ask.
Also open: subagent-per-task or inline execution.

**Milestone A is the "is it doable" half-day, no UI:** apply the migration → `python3 scripts/test_172_team_sql.py` (13 live checks;
check 2 INSERT → 25006 is a MERGE BLOCKER — if a write succeeds, stop and escalate; check 8 records the HTTP-edge cap for a 55-s RPC)
→ 7 gate checks + `olivia_snapshots/prod_pre_172.sha256` → the throwaway heartbeat route through `digest.mds.co` (≥ 300 s = stream,
else poll) → a 5-question spike. Verdict thresholds are in the plan.

**#147 — SQL half CLOSED, one lane left.** `registration_status_v2` (roster `has_ticket` gates, GroupOS `is_attending` drives the
agenda), v1 is a wrapper, `is_registered` untouched, `event_who` resolves on place; 36 → 0 contradictions; tests
`scripts/test_147_registration_authority.py` + `test_147b_event_resolver.py`; merged `1784b68`. **Not done:** the web schedule route's own
`registered = myTypes.size > 0` — needs an explicit go (Render deploys on merge).

**Rulings recorded today:** #147 roster via the Supabase mirror · #184/#185 hold for Eugene · #157 stay on Sonnet 5 (rotate the
2026-09-02 OpenAI key) · #71 the recording is the answer · **#190 = sprint-closure eval, run last**. #181's GitHub PAT exists
(fine-grained, `AndyVerdy/mds-digest-web`, repo-wide Read+Write — his call — **expires 2026-10-10**, regenerate once n8n holds it).

**Housekeeping, unanswered twice:** the shared checkout `/Users/Born/Scorecard` is parked on `186-design-request-20260909`. Until it
is moved back to `main`, **read every doc from `main`** (`git show main:OLIVIA_NEXT_SESSION.md`), never from the working tree.

## STATE 2026-09-10 (evening) — #123 + #191 CLOSED · prod `b4db92d0` · gate 346 EXIT 0 · lock free

**Read this first.** Prod n8n `b4db92d0` (promoted 17:56Z by Andy, snapshot
`olivia_snapshots/prod_2026-09-10T175648Z_123-event-catalog-routing.json`) · staging `9d91109e` · gate
**346 checks, 0 FAIL, exit 0**, re-run against prod after the promote.

**#191 — the nightly eval was dead and is not any more.** #105's header auth on `WA Inbound (POST)` refused
every post from the local harnesses: the 2026-09-10 08:30:05Z run fired 220 questions, logged 180 × `403`
and wrote no report. `scripts/olivia_relay.py` now reads `relay_secret` from `digest.meta_webhook_config()`
at call time and hands back the curl args; `olivia_eval.py`, `olivia_selftest.py`,
`olivia_reaction_canary.py` and `smoke_manual_suite.py` all send `X-Olivia-Relay`. Proven 25/25 `200`.
Three refusals in a row now abort with a Slack line and exit 2. **Tonight's 03:30 nightly is the first full
220-question report since the outage — read it.**

**#123 — event questions reach the events catalog.** `Answer Tool` routed by `startsWith('event_')`, so all
four event tools hit the Summit schedule route, which drops `p_terms` and always loads the newest row in the
`event` schema (MDS Summit Singapore, ended 2026-08-26). `event_schedule` and `event_who` are now named
explicitly; `event_lookup` and `event_history` fall through to `event_lookup_v3` / `event_history_v2`. All
three EVENT failures from the 09-09 eval now answer correctly, on prod.

**Already live and NOT staged, know this before you touch events SQL:** `digest.event_lookup` labelled the
listed clock time "UTC" and that reached an answer as "6:30 PM UTC" for a Miami evening event. It now claims
no zone. Only 19 of 1,455 catalog rows carry `app_timezone`, so rendering a real zone is not available.
A shared function is live on prod the moment it is applied — rollback is the inverse one-token replace.

**Two things for the next session, both from #123's own ACs:**
1. **Bank truth may now be stale, and the eval will blame the wrong thing.** Question 2035 "What city is the
   MDS Summit being held in?" now answers **Cancun 2027** from the catalog instead of the finished Singapore
   summit. Correct today; if the stored truth still says Singapore the judge marks it FAIL. A4071, named in
   #123's ACs, is not in the live bank at all.
2. **Andy's four rulings from this session are on the board**: #147 takes the Airtable roster as the
   authority but reads it from the Supabase mirror, which makes the mirror's freshness part of that ticket ·
   #184 holds until Eugene rules on whether members' own posts are in scope · #157 stays on Sonnet 5 (the
   OpenAI key from 2026-09-02 still wants rotating) · #71 answers "the last call" with the recording.
   **#190 is the sprint-closure eval — run it when everything else is done, not mid-sprint.**

**Still blocked on Andy:** GroupOS PAT (#182, #17) · Circleback details (#36) · #186's two-docs call ·
#118 needs him and Eugene together (it moves #96's name-disclosure rules) · #32's send. The GitHub PAT for
#181 exists now and n8n holds it once he pastes the credential — the token is broader than the job needs
(his call, recorded) and **expires 2026-10-10**, so #181's fourth AC (a failed dispatch must be loud) earns
its keep.

## STATE 2026-09-10 (close) — #179 SHIPPED · #105 SHIPPED and ENFORCING

**#179 closed and live.** A Make WARNING (`status: 2`) was mapped to error, so "Guest Multi-Event Alert" had
read DOWN since 2026-09-02 on its one and only execution, permanently, because the scenario is Airtable-triggered
and no clean run was coming. Make's own reference says 1 success · 2 warning · 3 error. Shipped `0fcb6df`, merged
`6a31026`, live on Render. Before/after on the same live data: `DOWN ✕ failed 7d ago` → `DEGRADED ⚠ warning 7d ago`,
other three Make tiles byte-identical. **Not verified: the rendered tile** — `/tools-health` needs a session and
`/api/health/report` 403s on the stale `HEALTH_REPORT_SECRET`. Open it once and confirm it is amber.

**#105 is live at the relay and refusing nothing.** Read the board's #105 block before touching it. The ticket's
spec pointed at n8n; **Meta posts to the relay** (`digest.mds.co/api/olivia/webhook`), which forwards to n8n
without the signature header — handbook line 72, true since 2026-07-21. Built to spec, promoted to prod
`021bb4b6`, **rolled back in eight minutes**; Andy's test message proved real traffic reaches n8n unsigned.
Rebuilt at the relay: secret in **Supabase Vault**, switch in `olivia_alarm_config`, both via
`digest.meta_webhook_config()`, cached 5 min — **no deploy needed to enforce or to rotate**.

**ENFORCING since 2026-09-10 04:47Z.** Andy's message recorded `ok` × 3 (genuine Meta deliveries verifying),
then the switch was flipped; an unsigned post to the relay now returns **403** and is never forwarded.
**Watch `digest.meta_webhook_verdicts` for a day** — rising `mismatch`/`missing_signature` with falling `ok` means
flip back: `update digest.olivia_alarm_config set v = '0' where k = 'meta_webhook_enforce';`, effective within the
5-minute cache, no deploy.

**Dead end, do not retry:** Meta will not self-trigger a delivery (`subscriptions_sample` = "Unknown path
components" on v18-v21, even with an app token).

**Live state.** prod n8n `12wj6h1TWqb0d4Dq` = `2b568155` (92 nodes; `rawBody` removed, `WA Inbound` header-authed) ·
staging `5a6b30c5`, re-staged from prod, clean · `mds-digest-web` main `5df00c7` · gate GREEN · lock free.

**Both doors are now locked.** The n8n side door was closed the same night (prod `2b568155`): `WA Inbound (POST)`
requires `X-Olivia-Relay`, and all four callers send it — the relay, the in-app widget, the iOS ask route and the
liveness probe — plus the Postgres health ping. A direct post without it gets 403.

**Open behind it:** ⚠️ **the app secret was pasted into chat — reset it in the Meta dashboard and update the Vault
row** (`vault.update_secret`, name `META_APP_SECRET`). Nothing else.

**Board drift fixed this session, four stale rows:** #97 (promoted 2026-08-22, not awaiting one), #165 (merged
and live), #104 (shipped 2026-08-22), and the "#105 + #97" cluster line. Verify rows against live before trusting
them.

## STATE 2026-09-09 (close) — triage + backlog session, NO code shipped · board re-evaluated · next = **#105 + #97 together**

**Nothing was promoted, merged to a live service, or changed in the workflow this session.** Prod is still
`15649d68`, web still `50ff14b` — see the 2026-09-08 state below, it is unchanged. This session produced tickets,
priorities and evidence only. All of it is on branch `health-tickets-20260909`, merged to `main`.

**Andy's word at close: "for the next one we are following your plan."** That plan is written into
`OLIVIA_SPRINT_4.md` at the top, in the **🔗 WORK THESE TOGETHER** block. Read that block before picking anything up.

**Start here — #105.** ⚠️ Corrected 2026-09-09 against live: **#97 was already promoted on 2026-08-22** (`7e4be40a`) and the 7 intro nodes are on prod `15649d68` today — the "waiting on Andy's promote" line below was 18 days stale. The cluster is really #105 alone, and what waits on it is the wide intros ANNOUNCEMENT, not a promote. #105 says
the WhatsApp webhook accepts any POST from anyone and never verifies `X-Hub-Signature-256`, and the board's own
note is "BEFORE any wide intros announcement". Promoting and announcing intros while that endpoint is
unauthenticated is the wrong order. Ship them as one piece.

**The board after the 2026-09-09 re-evaluation.** 46 open — **S1 5 · S2 14 · S3 18 · S4 6 · standing 3** (was
S1 7 · S2 26 · S3 4 · S4 5); 21 priorities changed. The bar is stated on the board: S1 = a member or member-facing
surface is wrong today, or we are exposed. ONE ticket is BUILT and awaiting Andy's promote: **#108** (the Finder). The board claimed three; two of those had already shipped and the rows were stale — corrected 2026-09-09 against live. **#97** was promoted 2026-08-22 (`7e4be40a`) and its 7 intro nodes are on prod `15649d68`. **#165** is merged into `mds-digest-web` main (`18bac76`) and live at `digest.mds.co` (`/api/version` = `15700f2e`).

**8 tickets filed 2026-09-09** — #179 Make WARNING renders DOWN · #180 `derive_niches` times out, niches frozen
since 07 Sep · #181 events cron (Sprint 5, blocked) · #182 `GROUPOS_PAT` (Sprint 5, blocked) · #183 storefront
reshuffle · **#184 + #185** the Millie unindex, act and capability, CU `86e35hm1p` · #186 Roadmap (Sprint 5).
Numbering starts at #179: **#178 was already taken** — check the highest number in use before filing.

**Blocked on Andy, nothing moves without these:** GitHub PAT `actions:write` (#181) · GroupOS PAT (#182 **and**
#17 — one token, two tickets) · Circleback details (#36) · the parse-vs-restructure fork on #186 · the Sonnet 5 vs
GPT-5.6 vendor call (#157 — a decision, not a ticket).

**Three traps this session proved, do not re-learn them:**
1. **Nothing reads link metadata.** `fb_post_links` has no title and no description, and its `display_name` is the
   literal string "youtube" on every YouTube row. A name that appears only on the far side of a link is invisible
   to Millie — which is exactly why "Roman Khan" was genuinely absent while members really had discussed him.
2. **A monitor can be the bug.** Two of three reds on 2026-09-09 were monitor defects, not outages. Get the real
   error from the source system; the triage endpoint 403s because the local `HEALTH_REPORT_SECRET` no longer
   matches Render.
3. **Read the threaded replies on a ClickUp task, not just the top-level comments.** The #184 replies reversed the
   whole instruction: MajestIQ and TraceFuse had been deleted from Wild Apricot and Airtable, Eugene reversed it,
   and both were restored. Deleting is explicitly wrong there.

## STATE 2026-09-08 (close) — #171 + #176 done: prod `15649d68` · web `50ff14b` live · open next: #177 · #170 · #172 · #173

**What is live on the web (`mds-digest-web` main `50ff14b`).** Ask Millie (`/admin/ask-millie`, unchanged from
#169) plus the Facebook Group tool's new Draft-an-answer modal on every unanswered post — calls the same Public
door with the WHOLE post text (`GET /api/admin/fb-post-text`, since `snippet` caps at 240 of up to 669 chars),
editable draft, Copy / Mark answered / Regenerate / Open in Ask Millie; "mark answered" now wired live to `POST
/api/admin/fb-post` (optimistic + read-back).

**What is live on the workflow (prod `12wj6h1TWqb0d4Dq` = versionId `15649d68`).** Public mode corrected to the
member audience, not the open internet (Andy: "you do realise that Public means MDS members … the only
restiriction for public mode is opt in sources"). OPEN = group posts/comments, partner + event pages,
non-verification WhatsApp chats, recordings flagged public. RESTRICTED = the five verification-required chats
(Centurion 20M+, Large SKU, Real Estate, Supplements, TikTok), restricted recordings, applications, anything
unclassifiable. Spine: `digest.chats.verification_required` + `digest.videos_catalog.access_restriction`. A
30-probe evaluation found and fixed 5 defects; name index 5,384 → 5,320; gate 331 → 345 GREEN. PR:
https://github.com/AndyVerdy/mds-community-scoreboard/pull/2.

**Open, per Andy's order:** #177 (Ask Millie's Public answer under-names against evidence the Facebook draft
already names from the same evidence — filed, "lets file it") · #170 (thread memory) · #172 (Team chat) · #173
(source trail + streaming).

**Standing traps this session added (handbook §13):** a shared Postgres function is live on PROD the moment it
is applied — no snapshot rides the promote, rollback is re-applying the old body · the `apply_169_*.py` scripts
now require `--dry-run DIR` or `--apply`; a bare `--help` is inert (it used to be a live write against staging).

## ✅ SESSION CLOSED 2026-09-08 03:30Z (22:30 CT) — prod `49d4a931` · staging `027bd776` · lock free · next ticket #147
**Live on prod tonight, two promotes:** `f5e9ce5d` (02:16Z) = #169 + #174 + #175 + #143 + #139 + #141 + #142 + #144, then
`49d4a931` (03:14Z) = + #169 fix round 4. Both gate-green, both snapshotted, both prod-probed. Rollback points:
`olivia_snapshots/prod_2026-09-08T031444Z_pre-promote.json` (back to `f5e9ce5d`) and `prod_2026-09-08T021615Z_pre-promote.json`
(back to `30fd7e6f`, which predates everything from tonight).
**Owned by the #169 session, not me — do not start it:** a fail-open in `public_gate.js` (ASCII `\b`; see `OLIVIA_HANDBOOK.md`
§13 for the exact shape and the 23 boundary-evading names). It fixes, stages, probes and gates; it messages before touching
staging and asks me/the next session to run the third promote. Prod has the flaw today with **no exposure** — the web door is
header-authenticated and its page has not merged.
**Evidence added, no new tickets filed:** Andy's two screenshots of the same question (15:46 CT vs 22:21 CT, turns 65489 vs
65941) are now #155's sharpest evidence — identical plan both times, link-carrying and partner-tool calls varied by run, and the
#175 orphan link is visibly gone after the promote. Andy: "if we have it as a ticket, then it's fine." Found-alongside and still
unfiled: loose `pending_offer.titles`/`items[].name` recording, and list-tool evidence clipping (from #143).
**NEXT TICKET — #147 · "Is this member registered?" is answered twice, by two sources, and they disagree** (🔴 S1, size M).
*As a member, one answer decides whether I am at an event, and every lane gives me the same answer.* The agenda lane reads the
GroupOS attendee export keyed by registration email; the who-to-meet lane reads the Airtable roster mirror, Confirmed only —
different keys, different rules, different sync clocks, and the alias bridge (`digest.member_email_alias`) exists but is not
consulted by `load_event_graph.py`. It gates the last unfixed half of #140. **Per the session protocol, present it and wait for
Andy's go before starting.**

## STATE 2026-09-08 04:40Z — #169 SHIPPED: prod `12wj6h1TWqb0d4Dq` = versionId `69665fc2` · web main `1987a2e` + `1aad368` live · branch `169-web-door-20260907` merged

**What is live.** Millie's web front door (`Web Inbound (POST)`, header secret, same-request answer, rows in
`digest.olivia_web_messages` under the staff email) and the Public Gate (classify → name index → redact → Haiku smooth
→ verify → format) on prod `69665fc2`; the Ask Millie storefront tool at `digest.mds.co/admin/ask-millie` (sessions
rail, MDS Team · Public | Staging · Prod, GATED strip, Clear); `/admin/millie/chat` and `/admin/olivia/test` forward
there; the polling test chat is gone. Gate: `python3 scripts/olivia_leak_gate.py` → **332/332** (a 9-check #169
section). Module: `node --test scripts/olivia_loop/public_gate.test.mjs` → 41/41.

**Verify first (live, not the docs):** `python3 scripts/olivia_wf.py status` should show prod `69665fc2`, staging
`d5a370b6`, no lock · a secret-less `POST https://mdsco.app.n8n.cloud/webhook/olivia-web-live` → 403 ·
`curl -s https://digest.mds.co/api/version` contains `1aad368` (or later) · gate 332 PASS.

**Open proof:** Andy's first send from the live page — it confirms `OLIVIA_WEB_SECRET` on Render (a 503 "web door not
configured" means the env var is missing; the value is in `mds-digest-web/.env.local`, never in the repo).

**Traps learned tonight (handbook §13):** a Postgres function is live on prod the moment it is applied (the name-index
RPC change did not ride staging → promote; rollback = re-apply the old body) · `apply_169_*.py` now need `--apply`
(a `--help` used to be a live write) · gate check 4 judges the SHIP target — run the gate once more after every
promote to re-assert prod · never `--help` a script you have not read.

**Deferred from #169 (on the board's close block):** partner founders over-masked when `web_people` lacks them ·
product names in the name index ("Hector AI") masked as people · CJK name inside CJK prose unbounded · source chips say
"other" for partner rows · Public latency 40–55 s → #173 · cost AC (metrics jsonb) unsummed.

**Next ticket, Andy's order:** #171 · Public answer from the Facebook tool (delivery 2) — or #170 / #172 if he
re-orders. Present NUMBER + NAME + STORY and wait for his go.

## STATE 2026-09-08 03:15Z — second promote: prod `12wj6h1TWqb0d4Dq` = versionId `49d4a931` (#169 fix round 4 on top of the eight tickets)
The #169 session finished its module tightening on staging `027bd776` and asked for the promote (Andy's conditional go: "my go to promote if another agent agrees"). **Verified before writing to prod, not taken on trust:** prod→staging diff = THREE nodes (`Public Redact`, `Public Verify`, and `Classify Evidence (Supabase)` `params.jsonBody`, which carries the same fix inline) plus the webhook path/id fields that always differ; **every other node byte-identical**; my seven edits intact on staging; the change is a TIGHTENING (a partner row's public name may be backed only by `name`/`web_summary`/`web_people`/`web_pricing` — the partner's own crawled website — never by `reviews_sample`, `strength_note` or `fit_reason`, which are member text); `node --test scripts/olivia_loop/public_gate.test.mjs` 15 pass / 0 fail.
**Promote 03:13–03:14Z:** gate GATE PASSED inside `olivia_wf.py promote` · snapshots `prod_2026-09-08T031444Z_pre-promote.json` (`f5e9ce5d`) and `prod_2026-09-08T031449Z_post-promote-169-fix4-20260908.json` · bounce 200/200 · **prod `49d4a931`, graph matches staging: True** · `PROMOTE_EXIT=0`. WA smoke after the bounce (5 turns, rows 65928–65937 deleted): all 200, lanes normal.
**Two facts recorded, both told to the #169 session:** (1) its handover said "two Code nodes … nothing else differs" — it was three nodes; (2) gate check 4 (commit `1890e62`) now judges staleness on the ship target only and treats a stale PROD as informational, so a prod that drifts from `public_gate.js` while staging is current no longer turns the gate red — right for a pre-promote run, thin for drift detection.
**Found alongside (not a ticket, for priority evaluation):** #174's offer recorder writes loose `pending_offer.titles`/`items[].name` — exec 138141 recorded a sentence as an item name and three stray titles ("before", "Productpinion", "Listing Optimization AI"). Ids were right and binding worked, so nothing failed; it is cosmetic-to-mild. Also observed and NOT a regression: exec 138144 "Tell me more about Alex Chiru video" planned a fresh video search because the previous answer offered three videos, **none of them Alex Chiru's** — the #174 bind is designed to fire only when the named item is in the recorded offer (it did fire at 02:17, exec 138068, when the previous answer named it).

## STATE 2026-09-08 02:16Z — PROMOTED: prod `12wj6h1TWqb0d4Dq` = versionId `f5e9ce5d` (92 nodes) — one graph: #169 + #174 + #175 + #143 + #139 + #141 + #142 + #144
**Andy's go** ("you have my go to promote if another agent agrees", 02:0xZ) + the #169 session's "AGREED — staging 4190faa9 is ready" (its Public-mode probes green, its gate 331 checks GREEN, its last fix SQL-only). Promote run 02:14–02:16Z under the lock: gate GATE PASSED inside `olivia_wf.py promote` · snapshots `olivia_snapshots/prod_2026-09-08T021615Z_pre-promote.json` (80 nodes, `30fd7e6f`) and `prod_2026-09-08T021621Z_post-promote-8-tickets-20260908.json` (92 nodes, `f5e9ce5d`) · 19 changed nodes (the peer's 12 web/public nodes + Load Recent Turns + Log Inbound; my Answer Seed · Format Reply · Gate Verdict · Plan Request · Prep Context) · bounce 200/200 · graph matches staging `4190faa9`: True · `PROMOTE_EXIT=0`. Prod webhooks now `olivia-wa-live` + `olivia-web-live` (the web door sits unused until #169's page merges in mds-digest-web).
**Prod probes (silent path, 18 turns 02:16–02:21Z, `Eval (silent)?` on every one, zero sends, rows 65892–65927 deleted by id):** #174 exec 138068 `offer_bind.mode:'drilldown'` → the Alex Chiru video alone · #143 ordinal 138072 "the second one" → Peter-Paul Maan drill-down · #139 138074 seven partners with deals + pages, nothing appended · #141 138080 raw `{p_author: "Fred McKinnon", p_terms: ["firearms"]}` → "Fred's firearms-adjacent brand is *TLO Outdoors*" + his post · #142 138082 one lap, real answer (the Summit's own page link appended once, no Register line — finished event) · #144 138086 events lane, "*MDS Summit Cancun 2027* … September 26, 2027" · #175 lap 2 138085 four 2027 events, no duplicate links. **All green on prod.** Lock released 02:23Z; the #169 session told.
**Rollback if needed:** `python3 scripts/olivia_wf.py rollback` to `prod_2026-09-08T021615Z_pre-promote.json` (80 nodes) — that graph predates #174/#175/#143 too.
**Next:** the #169 session takes staging for one more module tightening (public_gate.js partner-name backing) → a second small promote; then its web page merges. Open behind that: #140 remainder (#123 / #147), #155, #132 (size M each).

## STATE 2026-09-08 01:35Z — #139 · #141 · #142 · #144 BUILT, STAGED and PROVEN on staging `c28fb532` (+ #175 lap 2 · #139 lap 2) · awaiting Andy's promote · branch `174-named-item-drilldown-20260907`
**Staging `c28fb532`** = the peer's #169 (Tasks 5–6) + #174 + #175 (+ lap 2) + #143 + #139 (+ lap 2) + #142 + #141 (three laps) + #144 · 92 nodes. Prod `30fd7e6f` untouched. Gate 323 checks `GATE_EXIT=0` (01:29Z). Lock released 01:36Z, the #169 session told "staging is back c28fb532".
**Proof (execs; probe rows 65770–65885 deleted by id, 68 `olivia_seen` rows too):** #141 exec 138001 "Fred's brand is *TLO Outdoors*" + his post link · #139 138004 seven partners with deals and pages (137957: the appended "Euka (15% OFF…)" line, and the "TikTok Shop (TBA)" wart lap 2 removed) · #142 137904 / 137962 real answers (was the canned line, 137871) · #144 137902 / 137954 events lane, consistent with the turn before · #175 lap 2: replay of 137901 / 137902 appends 0 (was 2 / 2), 137953 one legitimate Cancun link · regressions: #174 138007 `offer_bind.mode:'drilldown'` · #143 ordinal 137969, yes 137910, nothing-pending 137914.
**How it was applied:** `scripts/olivia_loop/apply_batch_139_142_141_144.py` — one GET, both nodes patched by the single-ticket scripts' `patch_code()` (Gate Verdict: 139 → 142 → 175b → 139b · Plan Request: 141 → 144 → 141b), one PUT, one bounce; idempotent per marker — **re-run it after any staging overwrite**. Suites on the live bytes: 175 33/33 · 142 9/9 · 141 23/23 · 144 9/9 · 143 45/45 · 174 30/30.
**Promote (Andy's call, one graph):** #169 + #174 + #175 + #143 + #139 + #141 + #142 + #144. **Not fixed, in writing:** #140 remainder (6267 → #123, 6498 → #147) · #155 (size M) · #132 (size M) · #142's Haiku half (the fact check itself fails a draft that refuses the typed name; the clamp is untouched) · content_items 104754 unreachable by the term "firearm" (path token, handbook §13) · list-tool evidence clipping (unfiled, from #143) · 6201 dossier lane (out of #143).
**Not exercised live:** `eventsLaneCarry()` (the router chose events itself both runs) and the #142 rule on a regen lap (137962 passed first lap) — both offline-proven backstops.

## STATE 2026-09-08 00:55Z — backlog VERIFIED on staging `aa649e7b` (Andy: "verify first if issue is still present"); four fixes BUILT and unit-proven, staging apply pending the #169 handover (asked 00:46Z)
**Verified, 25 bank C cases in 54 read-only probe turns (rows cleaned by id):** #139 1/5 still fails → `apply_139_partner_link_repair.py` ·
#140 2/6 fail, both upstream (#123 misroute for 6267; #147 for 6498) · #141 1/3 fails → `apply_141_pronoun_subject.py` · #144 1/3 fails
→ `apply_144_events_lane_carry.py` (the 2027 catalog IS reachable now) · #142 1/3 clamps on an identity-rule false positive →
`apply_142_identity_precision.py` · #155 half present, size M, own session · #132 unchanged by design. Verification tables sit under
each ticket on the board. **Apply order when staging is ours: 139 → 142 (both Gate Verdict) → 141 → 144 (both Plan Request), then
re-probe 6075 · the Fred chain · the 2027 chain · 6483 · two regression chains, gate, hand back.** Tests: 175/139 19/19 · 142 9/9 ·
141 12/12 · 144 9/9 · 143 45/45 · 174 30/30 on the dry-run bytes.

## STATE 2026-09-08 00:15Z — #174 + #175 + #143 PROVEN ON STAGING `eb99c336` · awaiting Andy's promote · branch `174-named-item-drilldown-20260907` (merged to `main` for #174/#175; #143 docs follow)
**Staging `eb99c336` = #169 Task 5 + Task 6 (the peer's Public Gate) + #174 + #175 + #143. Prod `30fd7e6f` untouched. Gate EXIT 0
(four runs, last 00:14Z). Lock free; the #169 session runs its Task 7 gate checks next, then Andy decides one promote for all four.**
**#143 close block on the board (AC table, execs 137713 · 137716 · 137720 · 137739). Tried and reverted: re-issuing the previous
plan for a titles-only offer — the `chapter_info` payload is truncated in the evidence after 14 rows, the model invented the rest
and the clamp fired (137759). Found alongside, unfiled: list-tool evidence clipping.** Earlier state below kept for the story.

## STATE 2026-09-08 (evening) — #178 SHIPPED (Render `15700f2`): every Personas surface is rank-led
- Eugene's Slack question closed the loop #165 opened: the sheet said `#1 of 674`, the rails and the cohort
  page still ordered on the rounded percentile (four members tie at 100 in Logistics & 3PL, so the alphabet
  decided and Mo Kuhail rendered third). Rails, Top 10 and the cohort page now order by rank and the cards
  read `#1` / `Logistics & 3PL · #1 of 674`. Live: `personas_cohort_v2('Logistics & 3PL')` = Mo 1, William 2,
  Fernando 3, Alex Yale 4; prod `/api/version` `15700f2`.
- New RPCs, both additive (a `RETURNS TABLE` cannot grow without a DROP, and a DROP loses the ACL):
  `digest.personas_ranks()` → `{topic: [rank, pool]}` per member · `digest.personas_cohort_v2(p_stat)` →
  cohort rows + rank + pool, ordered by rank. `personas_cohort` (v1) is now unread but stays.
- **Environment, needs a hand:** `mds-digest-web/node_modules` in the shared checkout is a broken symlink to
  `/Users/node_modules` (created 2026-09-08 19:59, not by this session) — builds from that checkout, and from
  any worktree inside it, die with a Turbopack panic. Run `npm ci` there. This session used its own worktree
  at `/Users/Born/wt-178-cohort-rank` (safe to delete once the shared checkout is fixed).
- **Trap found:** `scripts/db_export_schema.py` resolves the repo from its own path, so running it inside a
  worktree writes `db/` into the MAIN checkout. Worth a `--repo` flag.
- Next is unchanged: **#163 Task 2 spend** (82 members, third-party placements only), then the persona-prompt
  structured-pointer change.

## STATE 2026-09-07 (night) — #174 + #175 PROVEN ON STAGING `2d875cb3` · awaiting Andy's promote · branch `174-named-item-drilldown-20260907`
**Staging `2d875cb3` = #169 Task 5 + #174 + #175 (the #169 session stacks Task 6 next; one promote carries all three — or
re-stage from prod and re-apply `apply_174_…` + `apply_175_…` for a one-ticket graph). Prod `30fd7e6f` untouched. Gate 324 / EXIT 0.**
Proof: Andy's exact chain exec **137664** (`offer_bind.mode:'drilldown'`, one video, its substance, one link) · speaker-named
137633 · title-named 137645 · "yes" 137637 unchanged · no-offer control 137647 unchanged · 0 gate-appended links in 33 turns.
Board close blocks under #174 / #175 carry the AC tables. Lock released 22:52Z; probe rows cleaned by id.

### ANDY'S DESK
1. **Promote** — `python3 scripts/olivia_wf.py lock … && promote` (gate re-runs inside). Then re-probe prod: your exact
   chain, and read `olivia_messages.plan.period = 'offer_bound'` on the follow-up.
2. **#143 BUILT offline after the probes (Andy: "address them one by one") — `apply_143_followup_guards.py`, 37/37 +
   #174 regression 30/30 on the dry-run of staging `2d875cb3`; staging apply + probes wait for the #169 session's next
   handover (asked). The findings it addresses:** "Yes please" after a billing answer bound to the
   bold `*$3,615.00*` as if it were an offered item — Format Reply records any bold span as a title (#112 recorder); "Is
   there any bigger revenue group" echo-bound on the word *revenue* and narrowed the PEOPLE list by band, where bank C
   expected the revenue-gated CHAT; "What do you know about me from WhatsApp?" went to the dossier lane (profile + a
   June-3 activity line, no links). A bare ordinal ("the second one") is never code-bound — right answer both times via the
   seed rule. Each is a small Plan Request / Format Reply change; none touched tonight.
3. The #169 session's WA-path ping left two rows in your real thread (65506/65507) — theirs to delete, told them.
**Andy's "poor answers check", case 1 (prod turns 65488–65491):** "Tell me more about Alex Chiru video" after a four-video
list was re-planned as a fresh speaker search (#174), and the two bare links under it came from the gate's link repair pairing
URLs with the wrong row (#175). Both on the board with story + ACs; both filed from live evidence (execs 137508 / 137515).
- **#174** `scripts/olivia_loop/apply_174_named_item_drilldown.py` (Format Reply `pending_offer.items` · Plan Request
  `namedOfferItem()` fourth acceptance signal · Answer Seed DRILL-DOWN offer block) — `test_174_named_item.js` 30/30 on the
  patched bytes · gate GREEN exit 0 (22:15Z run). **Applied to staging twice (8275f8da, 1d9a96d4) and overwritten twice by
  the #169 session's whole-graph PUTs** — the `olivia_wf.py` lock is host-level and cannot separate two sessions on one Mac
  (memory `olivia-staging-lock-is-host-level`). Agreed by message: #169 finishes its Task 5 fix, hands staging over, #174 +
  #175 apply on top, probe, gate, hand back; #169 Task 6 goes on after; the promote carries #169 + #174 + #175.
- **#175** `scripts/olivia_loop/apply_175_link_pairing.py` (Gate Verdict `linkCoverageUrls()`, depth-aware row bounds) —
  `test_175_link_pairing.js` 14/14 · replaying the real evidence of execs 137508 / 137515 appends 0 URLs (was 1 and 2).
- **Probe run (done 22:38–22:50Z on `2d875cb3`; the plan as run)** (`olivia_selftest.py --staging`, probe rows cleaned by id afterwards, never `--cleanup`
  — it deletes by the oldest SELFTEST claim and would take Andy's real turns with it): reset · Andy's split-test question ·
  "Tell me more about Alex Chiru video" (AC chain) · "Summarize the Fabio one" · "yes" · "the second one" (#112 unchanged) ·
  a title-word drill-down · the no-offer control · then #143's c117 ("How much MDS credit do I have?" → "Yes please") and c39
  ("…tiktok ballers" → "Is there any bigger revenue group" → "I thought I was in that chat already") and 6201.
- **Backlog cases queued after these (Andy: "check backlog for more cases, address them one by one"):** #143 (3 bank C
  follow-ups — 6349 is a bare "yes please" on a billing offer that replays the billing RPC; 6095/6096 are chat-tier
  context; 6201 is the profile lane answering a from-WhatsApp ask) · #155 · #139 · #140 · #141 · #142 (deliberately untouched).

## STATE 2026-09-07 (pause, late) — #165 source tags LIVE (web `main` `18bac76`) · sentence rewriter PARKED · next = #163 Task 2 spend go
**Andy: "push what we have, and lets pause for today."** Shipped the proven part only:
- **LIVE:** every GIVES / ASKS / FOCUS line on the Personas sheet carries a `self-reported` or `observed` tag, with a
  one-line legend per section and one help sentence. Classifier `src/lib/personas/signalSource.ts` (word-bounded
  keyword scan over each `;`-segment, census-key fallback, hyphen is a boundary), 33 tests. Community-wide gives:
  **987 self-reported · 1,742 observed · 118 untagged (4.1%)**; asks 487 / 1,778 / 125; focus 2,375 / 2,507 / 83.
  Merged `556b168` → web `main` `18bac76` (main had moved to `1987a2e` under other sessions; clean merge).
- **PARKED, unmerged — `parked/165-sentence-hover-20260907` (= `bf1ab62`) in mds-digest-web. DO NOT MERGE.**
  The human-sentence "Written from" hover (`signalText.ts`). The working branch `165-source-labels-20260907`, its
  worktree and its dev server are GONE; the shipped part is in `main`. **Convention from today: anything under
  `parked/` is not in flight — no session picks it up without Andy's word.** (`ff4f234`, `bf1ab62`). Two review rounds each found a new free-prose pointer shape; `bf1ab62` still garbles
  7 bracketed-list profile values. Do NOT merge it as is. The real fix is upstream: make `persona_refresh.py`'s
  prompt emit a structured `signal` pointer (`source | date | field | value`), after which the rewriter is trivial and
  the 4% untagged bucket disappears. Not filed yet — Andy's call.
- **Why this dragged (owned):** "add labels" was done and reviewed clean early; the sentence work should have been
  a separate capped ticket. Parsing model prose does not converge under review-by-sampling.
- Luke Li `recov3Xb7Vy30JTqC` is the worked example: 3/3 gives self-reported (his 2026-08-05 form), 1 observed ask
  (a 2026-09-03 WhatsApp SNS question), 14 blue chips from 3 form lines. Persona cadence: nightly 04:15, rebuild on
  missing / >30d / fingerprint change; windows 180d questions (≤60), 30 most recent authored items (no date window),
  15 events, form answers never decay — signals fall off a cliff, no half-life in this layer.

### ANDY'S DESK (pause)
1. **#163 Task 2 spend** — 82 members (60 top + 22 honest control), third-party placements only.
2. File the persona-prompt structured-pointer change (small, `mds-scorecard-tools/persona_refresh.py`).
3. Should self-reported-only chips look different from observed ones? (#163 — matching weight.)
4. Dashed typical-member mark hover text (asked, not built) · RLS disabled on 47 warehouse tables (advisor; #158).

## STATE 2026-09-07 (scoring session close) — #163 Task 1 DONE · **#165 PROMOTED — rank-led stat bar LIVE on prod (Render `b44e2d7`)**
**PROD n8n untouched all session (no promote, no lock).** Andy: "lets promote it" (2026-09-07). Both merged:
- **mds-digest-web `main` = `b44e2d7`** — merge of `165-personas-sheet-20260907` (rebased on 48851e7 → f3be5ca;
  re-verified after rebase: tsc clean, vitest 1087/1087, next build exit 0). **Render `/api/version` = b44e2d7,
  live 2026-09-07 ~17:03 local.** Sheet: `digest.mds.co/personas/recLS9VdInRcZY3vc` (Corey Smith; staff login).
- **Scorecard `main` = `4e111c1`** — merge of `165-personas-numbers-20260907` (rebased on 23ed52c → dc148cb): the
  `personas_stats` view mirror (+5 columns, live since aa9953f), board, logs, handbook.
- Both merges went through detached throwaway worktrees (`git push origin HEAD:main`) — no shared checkout moved.
  Peer sessions told to `git pull --ff-only`.
- **Scorecard `163-truth-set-20260905` @ `2dda4f6`** — #163 Task 1, complete. Merge when Andy wants the
  truth-table code on main; nothing downstream needs it until Task 3.

### What the bar now means (phase 3, `f2975cb` — the thing to explain to staff)
Andy could not read phase 2 ("humans will not read 18.62/18.69 · 100th · 1 of 461"), so the row is now: **big
number = rank `#19` over `of 38`** (members with any signal in the category) · bar on a **log scale** 0 → community
top (`ln(1+x)/ln(1+top)`), fill = today · one **dashed unlabeled mark = a typical member** (the community median —
Andy: "use the median") · a **faint ghost past the fill only when `fading`** = where they peaked · trend word
unchanged · **raw score, peak, typical, top and percentile on hover** and in "How this score was built". No today
triangle, no "median" text, no scores in the cell. No "strong" threshold on the bar — the cohort/library pages keep
their own 60th-percentile cutoff, stated as theirs. `member_expertise.pct` untouched; Millie's lanes tier on it.
Web branch `165-personas-sheet-20260907` @ `f2975cb` (phase 2 `98f40ba…04b2675` → phase 3 `aa47d70` → phone fix
`f2975cb`); reviewed on Corey AND Ryan Pace (#182–#475), 901 tests, build 0, phone truncation at parity with 04b2675.

### #163 — where it stands
Task 1 `digest.expertise_truth`: 609 rows · 42 topics · 146 members · 279 evidence events · 0 orphans · gate 328/0.
**Task 3 must exclude/footnote "SEO & keywords"** (97 of 364 speaker rows, ~95% taxonomy noise from the compound
"Marketing & SEO" video category). **Task 2 = 82 members, not 101** (Andy: "use the 22 and keep the control
honest" — 8 under value 20 + 14 actives with no ledger row; the percentile scale makes "near zero" almost empty).
Task 2 needs Andy's explicit go on the crawl spend before dispatch. Ledgers:
`.superpowers/sdd/2026-09-05-expertise-truth-set/progress.md` · `.superpowers/sdd/165-personas-numbers/progress.md`.

### ANDY'S DESK
1. **"merge"** for the two #165 branches (and #163's when convenient).
2. **#163 Task 2 spend** — 82 members, third-party placements only, same subagent pattern as #160's 506 sites.
3. Four #163 findings from #165 (posts weight 2.0 with 0 rows carrying a posts key · 1,016 detail rows under a
   zero parent · redundant `weakness > 0` · focus signals often ARE the member's own words) — fold into Task 3 or file.

### Traps this session
- `member_expertise.pct` is **0..1**; `personas_stats.value` is **0..100**. Read "under 20" against the wrong one
  and every member qualifies.
- `personas_stats.peak` is a projection, not a recorded percentile. `member_expertise.peak_score` is the real one.
- "The phrase is gone" is not "the meaning is gone" — three copy agents each fixed the sentence they were pointed
  at and left the one beside it. Verify copy by transcribing the RENDERED page sentence by sentence.
- A desktop column widening does not carry into the phone breakpoint by itself; the final review measured 375px.
- Postgres refuses `percentile_cont(...) OVER (...)`; per-topic aggregates come from one GROUP BY join.

## STATE 2026-09-07 — #165 Personas sheet BUILT, handed to the scoring-system (#163) session · #166 + #167 SHIPPED
**Andy 2026-09-07: "i need you to transfer 165 updates to Scoring system agent, ill work on it there."** Everything
below is what that session needs; nothing is left in the head of the session that built it.

### #165 · where the work is
- **Repo `mds-digest-web`, branch `165-personas-sheet-20260907`, one commit `50c7a4a`, pushed, NOT merged.** Built off
  `7ba7ea8`; `main` has since moved to `491a968` (#166 switcher, #167 survey + roster fix) — none of those touched
  #165's files (`src/app/personas/[id]/**`, `src/components/personas/StatsPanel.tsx`, `StatRow.tsx`, `StatusDot.tsx`,
  `Chip.tsx`, new `SheetHelp.tsx`, `PersonaLines.tsx`, `src/lib/personas/**`, `src/app/personas/dev/components/page.tsx`),
  so it rebases clean. Merge to `main` = Render production deploy.
- **Docs written by the build:** `docs/PERSONAS_FIELD_PROVENANCE.md` (field-by-field, two writers: `persona_refresh.py`
  → `member_personas.persona` by Haiku 4.5; `derive_member_expertise()` → `personas_stats`) and the "What #165 did" section
  of `docs/PERSONAS_OPEN_QUESTIONS.md`. Board row + story + ACs: `OLIVIA_SPRINT_4.md` §#165.
- **Local proof was on `:3165`** (a worktree at `mds-digest-web/.claude/worktrees/165-personas-sheet`, dev server may be
  down); staff cookie via `scripts/dev-session-cookie.mjs`. Gates at the commit: `tsc` 0 · 892 tests · `next build` 0.

### #165 · what shipped on the branch (all verified in the running app on Ryan Pace + two other members)
1. All 18 categories render as rows (7 with signal, 11 at zero); every sub-stat renders under its parent. The grey
   "No signal yet on:" footer and the nested "no signal yet:" line are gone.
2. Top strip states what the sheet is: a briefing assembled by MDS the member never fills in or sees; the written lines are
   a model's summary of signals, not the member's words; the numbers are ranks against the community. "Persona written
   3 Sep 2026 by Claude Haiku 4.5" beside it. "How this sheet works" panel = layer two.
3. FOCUS shows each item's stored recency (`active-now` / `recent` / `background`); hover a line → the `signal` (often the
   member's own form answer, e.g. "self-reported 2026-08-21: biggest constraint = Platform risk") and the `why`.
4. GIVES → "what they can help with", ASKS → "what they are looking for"; the model's lines first, "MATCHED CATEGORIES"
   chips second. "In their words" removed (it was Haiku's paraphrase).
5. "Top 6" → "Open top 6" with a hover saying it never filters. Rank line + evidence channels demoted into a closed
   "How this score was built" disclosure per opened category, rewritten as sentences; `band_multiplier` /
   `peak_floor_applied` shown as "scoring rules applied", not evidence.
6. Two rendering bugs fixed on the way ("Ryannever fills it in" — JSX ate a space across a line break; "Rank#179" to a
   screen reader).

### #165 · findings that belong to #163 (the scoring review) — reported, NOT touched
- **1,016 detail-stat rows across 503 members were unreachable**: a sub-stat can score while its parent is 0 and the old
  page only rendered details inside a surviving category (Ryan: M&A general 49, Amazon US 38, AI tooling 27 invisible).
  Showing all 18 fixed the display; the ledger question (why a child scores with a zero parent) is #163's.
- **The scorer weights `posts` highest (2.0) but zero of 16,762 `member_expertise` rows carry a `posts` evidence key** —
  every authored item lands as `comments`. Either the loader mislabels or the weight is dead.
- **`personas_sheet`'s `asks` filter `or weakness > 0` is redundant** (`weakness = ln(1 + persona_asks_hits)`; 0
  disagreements in 16,762 rows) — drop next time the function is touched. No DB write was made on #165.
- **The ticket's premise was half wrong:** 2,407 of 4,960 focus signals cite the member's own census/application answers
  (`self-reported <date>: <field> = <answer>`), so "never member-stated" does not hold — the *item text* is always the
  model's paraphrase, the *signal* often the member's words. The page now shows the signal.

### #165 · open calls for Andy (unchanged since the build)
1. **`StatBar` reference line sits at 70 while every other Personas surface and the new copy say 60 = strong.** The page
   literally reads "60 and above is strong" above rows marked 70. Move the line to 60 (recommended) or keep 70 and name it.
   `StatBar.tsx` was outside #165's file ownership, so it was left.
2. Heading vocabulary kept as GIVES / ASKS + plain gloss, not renamed, so the words still match the chips and the rest of
   the app. Rename if wanted.
3. Two grid icons in the Personas header after #166 (switcher far left, Browse right of search) — #166's finding, Andy's
   call on Browse's icon.
4. Ryan Pace's Member 360 is **correctly empty**, not broken: the page reads `member_profiles` synced 2026-09-06 16:29Z,
   his Stripe id landed 2026-09-07 05:00Z; fills on the next mirror run (`Stripe MRR` 665). No fix made.

### #166 · #167 — shipped tonight, for context only
`main` `b91f2a4` = switcher in the Personas top bar + both Digest headers · `41da9e7` = team pulse survey · `491a968` =
its roster fix (N of M counts the 30 Airtable Staff) · `e2d933d` = second-day-of-use rule (asked on the 2nd distinct
UTC day a staff member opens `/admin` since 2026-09-07; `digest.admin_survey_visits`). Board §#166 / §#167 carry the proof.
Andy's rulings at close: Personas bar line stays at 70 (the #165 copy must stop saying "60 is strong"); the two grid icons
in the Personas header stay; Playwright declined. Merged worktrees removed, dev servers stopped; only the #165 worktree
remains under `mds-digest-web/.claude/worktrees/`.

 — #162 CLOSED · 2026 videos 212/212 transcribed · PROD `30fd7e6f` untouched, warehouse only
**Every 2026 video now carries a transcript.** 33 in-person talks (16 AI Mastermind restricted · 8 AI Scaling Live · 4 Summit
day-2 + the 5 brand-new AI-Mastermind uploads) went through AssemblyAI ($2.62), 697 chunks, 33 Haiku summaries, embedded, gate
313/0, E2E quote proven through the live workflow. Story + numbers in `SESSION_LOG_OLIVIA.md` 2026-09-04 (afternoon); close
block on the board.

### What changed in the pipeline (no promote needed)
- **S3 links:** the dev opened `uploads/content-archive/videos/*.mp4` to anonymous GET on 2026-09-04. `aai_submit.py --year 2026
  --csv <csv>` now works from bare URLs (CSV columns: `upload_year, video_id, download_link, title, event_name, upload_date,
  duration, access, s3_key`). No presigned export needed any more — until GroupOS closes the bucket again (GOS-32/36).
- **`video_summaries.py`** counts every video with `call_transcript` chunks as transcript-backed (was `digest.calls` only) — the
  weekly chain now writes the Haiku summary for AAI videos itself; no hand-written summaries any more.
- **Entitlement sweep, tag-filtered:** `videos_list(for_user_id, tag_id=<AI Mastermind>, created_after=<last run>)` — empties
  come back inline, so a full-roster pass costs one file per ENTITLED member. Recorder/loader pattern in the log entry.
- **Never run `aai_transcripts.py` on `~/mds_transcripts/2026` again** — it would re-chunk the 161 older files with the new
  splitter and leave stale embeddings on the overwritten rows. Copy new JSONs to a batch dir and `--dir` it.

### ANDY'S DESK
1. **The opened bucket exposes restricted talks:** every `videos/*.mp4` (and the Otter transcript PDFs GroupOS attaches) is now
   world-readable by key — the GOS-32 hole, reopened to get transcripts. Decide with GroupOS: presigned links (GOS-36) and close it.
2. **32 members whose AI-Mastermind grants no longer hold in GroupOS** (CSV-era rows) — additive loader, nothing deleted; say if
   they should be revoked. 10 members gained access (incl. Danson Hui, a speaker) and now carry grants.
3. 13 target members have no GroupOS account at all (list in the #162 close block) — no grants possible until they do.
4. One chunk at 4,202 chars (target 4,000) — same sentence-bounded class as the 25 Aug batch; re-chunking the 255 older
   videos is still your priority call.

## STATE 2026-09-04 (day) — ClickUp handbook copy REGENERATED from a live-verified handbook · no prod change
**Prod `30fd7e6f` = staging `cefe0133`, gate 313/0 (run 12:40Z), lock free, 13 heartbeats green.** `OLIVIA_HANDBOOK.md` re-verified
against n8n, Supabase, Meta, launchd, GitHub, Render (header says "last verified 2026-09-04") and ClickUp `2531q-103317` pages
00–18 rewritten from it; page 00 carries the shipped-since-08-20 list, Andy's desk and the open tickets. `db/` re-exported
(the 05:40 drift alarm = `partner_lookup_v2.web_pricing`). Story in `SESSION_LOG_OLIVIA.md` 2026-09-04.
- `prod_pulse.py` reads 2 regressions against a STALE baseline (failed sends 0→3, `member_edges` fell with the nightly rebuild):
  run `python3 scripts/prod_pulse.py --save-baseline` before the next tier.
- Unfiled from this pass: the alarm's 69-min lag on the 2026-09-02 outage · no Accounting/Tax/Legal topics in the taxonomy ·
  founder↔partner FB mention matching. Andy's desk unchanged (see the 00:20Z block below).

## STATE 2026-09-04 (00:20Z) — #159 CLOSED · #160 PROMOTED — prod `30fd7e6f` = staging `cefe0133`, gate green, lock free
**Prod probe exec 131383: Shea's bookkeeping question → Prosperlytics first with site facts + pricing. Gate vector checks now ignore rows synced <30h (they wait for the nightly embed).** Earlier text of this block kept for the story:
**PROD `d40a837d` untouched. Staging = prod + ONE Answer Seed edit (`scripts/olivia_loop/apply_160_partner_web.py`: the
partner_lookup tool description names `web_summary / web_people / web_pricing` as partner-stated). Gate 313 PASS · 0 FAIL · EXIT 0.
Lock released at close.** Story in `SESSION_LOG_OLIVIA.md` 2026-09-03 (evening); board close blocks #159 / #160.

### What changed in the warehouse (no promote needed)
- `partners_catalog` / `events_catalog`: 0 rows without a vector (was 75 / 36). Nightly `embed_catalogs` step + the weekly partner
  check re-embed; gate holds it at 0. `scripts/embed_partners_events.py` is the one script for both.
- NEW `digest.partner_web_profile` (506 rows: 405 from live sites): summary · services · markets · pricing · people · profile jsonb.
  `partner_lookup_v2` LEFT JOINs it (`crawl_status='ok'`) and returns `web_summary, web_people, web_pricing` — the model already
  sees them on prod (tool result passes through); the staging edit only tells it how to frame them.
- `speakers.affiliation_partner_id`: 52 linked (Mudit Jain → Prosperlytics). Loader never overwrites an existing link.
- Partner VECTORS now include the web profile text (summary · services · pricing); the loader nulls the vector when a profile changes and the embed pass rebuilds it. All 508 published partners carry a vector.

### Weekly GroupOS task (`~/.claude/scheduled-tasks/groupos-videos-weekly/SKILL.md`) — changed
Step 4: page until `has_more=false`, check `with_total`, window = last success − 3 days; Fathom + Onsite Support break the
listing endpoint when inside a page (fetch with `partners_get`, skip with cursor = base64(id)). Step 4b (new): crawl + extract +
load web profiles for NEW/CHANGED partners (`OLIVIA_PARTNER_WEB_EXTRACT.md` is the extraction spec). The `--apply` line must end
with "re-embedded".

### ANDY'S DESK
1. ~~Promote~~ done 2026-09-04 00:17Z. 2. Two Prosperlytics rows in the directory (5-review `651f9c…` vs `6763ad…`) —
directory hygiene. 3. Eight partner links land on Typeform/Airtable/Calendly pages, not the partner (New Amazon Account, VAA
Philippines, Amazon Buy with Prime, Graphic Rhythm …) — fix in GroupOS. 4. Not filed yet, your call: founder↔partner mention
matching (22 "Mudit" FB comments never reach Prosperlytics; `fb_partner_mentions` matches on the partner name only) and FB/WA
complaints → partner `weak_signal` (today only <3.5★ directory ratings count); browser fallback for the 100 unreadable sites;
service topics (Accounting/Tax/Legal) in the 51-topic taxonomy so partner strengths stop reading as marketplaces.

## STATE 2026-09-03 (early) — video entitlement SWEPT: 424/424 restricted videos carry grants (0 uncovered)
**PROD untouched. Warehouse only:** `digest.video_access` +7,936 `source=api` rows from a per-member
`videos_list(for_user_id)` sweep of all 749 GroupOS-linked actives (AI Mastermind tag + the 2023
window). Loader `scripts/video_access_from_sweep.py`. Story + numbers in `SESSION_LOG_OLIVIA.md`
2026-09-03 (early); method in memory `reference_groupos_entitlement_sweep`.

### Weekly video run — the entitlement pass is now PART of it
1. Dump + `videos_weekly_check.py --apply` as before (`limit=100` works now — 3 pages, not 11).
2. If the dump has any NEW `restricted` video: `videos_list(for_user_id=<id>, created_after=<last run>)`
   for every id in the roster (member_profiles → GroupOS id via `members_list status=active`), record to
   JSONL, `python3 scripts/video_access_from_sweep.py <jsonl>` (dry-run first). Without this pass a new
   restricted video is invisible to everyone.
3. 5 emails never resolve to an `at_member_id` (chris55776@gmail.com, eugene@milliondollarsellers.com,
   galactbrands@gmail.com, sales@bpdistributing.com, shiva@joonhaircare.com) — rows keep the email; fix
   the alias in `member_profiles` if Andy wants them matched. 8 actives have no GroupOS account at all.

### ANDY'S DESK (added 2026-09-03)
- **S3 links for the 27 Aug–1 Sep videos** (his transcript request) = GOS-36 signed URLs — nothing sent to
  GroupOS yet; the REMAINING doc is ready, the ClickUp comment still has the OLD GOS-25 wording.
- 38 of the 2023 event recordings are visible to ONE admin account only — if members should see them,
  that is a GroupOS-side rule change, not ours.

## STATE 2026-09-02 (evening) — #156 model bench DELIVERED, read `OLIVIA_MODEL_COMPARE_2026-09-02.md`
**PROD `d40a837d` untouched all day by this ticket. Staging identical to prod. Lock free.** #156 closed on the board with
the AC table; numbers (Sonnet judge): Sonnet 5 **5.4%** fail / **$0.0211** per answer warm · GPT-5.6 Terra medium
**3.3%** / **$0.0310** · Terra none **7.6%** / **$0.0237**; latency median 10.1 s / 19.4 s / 14.2 s. Terra judge:
13.0 / 9.8 / 13.0. 92 of the locked 100 questions benched (8 canned lanes never reach the model).

### ANDY'S DESK
1. **The vendor call — filed as #157 (🟡 S2).** Terra-medium beats Sonnet by 2 questions on the Sonnet judge and loses on price (+47%) and
   latency (2×); Terra-none is a cent cheaper and 2 questions worse. Read the § Judge disagreements first — the
   Terra judge fails honest-miss answers the rubric marks PASS. Caveats in the close block (Claude-tuned prompt,
   S1–S16 stamps not replicated, post-model gates not run).
2. **Rotate the OpenAI key** pasted into chat on 2026-09-02 (stored as `OPENAI_API_KEY` in mds-digest-web `.env.local`).
3. **If Terra:** the n8n answer-loop port (Answer Seed/Parse/Merge to the Responses API shape) is a new ticket, size M,
   full through-workflow eval before any promote. Tier-1 OpenAI limits (500K TPM) would also need raising for prod traffic.

### Harness (for the next bench)
Lives in `~/mds-scorecard-tools/` (NOT a git repo; snapshot in `scripts/model_bench/`): `kimi_harvest.py` (seeds from
staging executions) → `kimi_bench.py --model … --passes 2` (Anthropic or OpenAI Responses loop, dual judge) →
`bench_compare.py <tags> --out …`; `bench_tools.py` MUST track the live `Attach Embedding` / `Answer Tool` /
`Answer Merge` nodes — re-extract them from the prod snapshot and re-run the 85 tests before any new bench.
`bench_merge_rows.py` merges a `--ids` re-run. Rate limit: OpenAI tier 1 = 500K TPM → 2 workers.

## STATE 2026-09-02 (session close) — read this first

**PROD = `d40a837d`. Staging identical (re-staged from prod before the last promote). Gate GREEN — 312 checks, EXIT 0.**
Walked `15ff4978` → `01902882` (credit-aware fallback copy) → `c00987cd` (#138 repair, PROMOTED THEN ROLLED BACK in
5 min) → `f2f4e9b8` (rollback) → `d40a837d` (#154). Render `mds-digest-web` = `8f368b3` (carries #109 `cae87c1`
and #154 finder `7a0ab94`; the peer session's fbstory commits ride the same main).

### Health triage, later the same day (2026-09-02 15:30Z) — tile GREEN, two things wait on Andy
- **Derivations tile:** 12 heartbeats · 0 stale · 0 errored (SQL). Fixed for good: dossier refresh had a 60s ceiling (now 900s,
  #152); `zoom_weekly` wrote into `~/Downloads` (launchd can't) and never stamped success on a DEGRADED run — it now stamps
  (`154e45d`); `videos_weekly_check` crashed on a clean week and never re-embedded CHANGED rows (`cd02299`); `ingest_videos`
  takes list-typed `cliff_notes` (Render `0814799`). Full story in `SESSION_LOG_OLIVIA.md` 2026-09-02 (afternoon).
- **Catalog now holds the 25 Summit-2026 / AI-Mastermind videos** published 31 Aug–2 Sep, plus cliff notes on 173 videos; all
  198 re-embedded (0 without vector). The Sunday 30 Aug `groupos-videos-weekly` scheduled task ran but left NO dump and NO
  transcript — cause unknown; its SKILL.md still says "limit 100, ~152 videos, 2 pages" (reality: 20/page, 11 pages, ~200).
- **Waiting on Andy:** FB Insights xlsx stalled since
  23 Aug — CONFIRMED real by the extension session (no download attempted since 23 Aug; SPA timing on the Download button);
  the daily conversation leg is healthy. Fix = Andy clicks "Capture Insights" in the extension. FB tile split BUILT (`b05af61`): `fb-capture` (Supabase posts, 36h/72h) + `fb-engagement` = Insights scores (AT date,
  missed week/14d) + roster on that leg. All three (`69a2ff1` `0814799` `b05af61`) PUSHED on Andy's "push"; Render serves b05af61 (16:04Z).
- **Filed late 2026-09-02:** #158 (FKs + nightly orphan check, S2) · #64 amended (decisions out of SQL, first slice #147). Both on GitHub main.
- **Verify next session:** the 08:00 card shows derivations green AND the two new FB rows (capture healthy / engagement scores degraded); Monday 07 Sep `zoom_weekly` launchd run stamps on its own;
  Sunday 06 Sep scheduled video task writes a dump (if not, run the 11-page fetch by hand as on 02 Sep).

### Shipped today
- **#109 CLOSED** — requester intro notices (accept · decline · 7-day lapse) go out as TEMPLATES; free-form only as
  fallback. `src/lib/intro-notices.ts`, 15 tests incl. a standing guard. Sweep probe expired=1/failed=0. NOT observed:
  delivery to a requester whose window is CLOSED (probe requester's window was open) — re-probe after Andy has gone
  24h without messaging Millie, or let the first real lapse prove it.
- **#154 CLOSED** — `digest.member_link()` = the ONE definition of a member's link (profile FB url → FB-map vanity →
  profile.php?id, normalised); `member_match_v2` + `expertise_search` return `link`; view `digest.member_links` for
  app routes; finder emits `link`. 718 of 741 actives resolve. Prod probe 5/5 linked. Gate +7 checks.
- **Incident 17:11–18:49Z** — Anthropic org out of API credit; every answer fell to the fallback line. Fixed by a $20
  purchase even though the console showed $99.75 the whole time (balance afterwards $118.65 — the money was there;
  the fresh charge unstuck the account). Member-facing copy now names the reason when it IS billing (Answer Parse).
  Alarm `members-getting-failure-text` fired 69 min after the first failure — too slow, file it.

### #138 — split, NOT shipped
The count-gate the ticket proposed was audited over all 602 bank C answers: 65 false alarms vs 51 real at best.
A per-item link repair was built (28 tests), promoted, and rolled back after the LIVE node attached a wrong link
(author-name match). Re-run of the 9 ids against prod: 4 fail / 3 pass / 1 borderline / 1 n/a — the symptom is real,
but its causes are retrieval (→ **#154, done**) and answer-loop binding + answer shape (→ **#155, open, S2**).
`scripts/olivia_loop/link_repair.js` + tests stay in the repo unshipped; `gate_verdict.js` local copy carries the
block for reference only. **Lesson written into the ticket:** verify the live node's own bytes over real drafts
before claiming a gate change works; n8n keeps ~1 day of executions, so audits must run and land the same day.

### Four things still wait on Andy (unchanged)
1. #147 authority shape (recommended: one function, two facets) · 2. the 16 Summit videos read `public` · 3. re-embed
the 7 (hangs off #2) · 4. v4 transactional template for the 50 undelivered — v3 came back MARKETING again.

### Traps found today
- **`digest.mds.co` SERVFAILs from this Mac's resolver** (public DNS fine, site up) — 26 route checks in the gate fail
  with status 0. Point them at `mds-digest-web.onrender.com` if it recurs. The peer session confirmed it independently.
- `mds-digest-web` checkout may be on another session's branch — check `git status -sb` before committing.
- RETURNS TABLE changes need DROP + CREATE: re-grant postgres + service_role and revoke public in the same migration,
  then verify `proacl`. Done twice today without incident.

### Next
**#155** (S2, M) is the open half of #138. Above it in S1: #72 load test (never run), #147 (blocked on Andy),
#138's siblings #139/#140, forms #73/#66/#68, #64 runtime inventory (the survey made its case stronger — 8 of 9 launchd
job definitions exist only on the Mac).



## STATE 2026-08-27 (Andy out — full pipeline run unattended)
**16 Summit Singapore talks are in the corpus. 9 are live and proven; 7 are loaded but reachable by
nobody. PROD WORKFLOW UNTOUCHED — data only, no promote.**

### What shipped
- **Batch A — 7 restricted** (`~/mds_transcripts/summit_sg_2026/`): 228 chunks, 7 summaries.
- **Batch B — 9 public** (`~/mds_transcripts/summit_sg_2026_b/`): 219 chunks, 9 summaries.
- 8.2 hr audio, **$1.88** total at AAI. Summaries hand-written in-session, zero API spend, all inside
  the corpus band (max 1,338 chars). Everything embedded. Gate GREEN (263 checks, exit 0) after each.
- Library: **410/1050 transcribed, 410 summarised, 12,762 chunks, zero unembedded rows.**
- `aai_submit.py --local` ends the presigned-export dependency (ffmpeg → AAI `/v2/upload`, resume-safe,
  manifest binds file → `video_id` explicitly). Commits `a2f4007`, `a06f57a`, `233de8f`.

### ANDY'S DESK — three calls, in this order
1. **GRANTS for the 7 restricted talks.** They are invisible to every member — proven live, not
   assumed (`content_search_v2` returns nothing from them even with `p_include_restricted=true`).
   46 restricted videos have no grants (7 new + 39 from 2023). Needs the dev's audience export;
   `scripts/load_video_access.py` already ingests it. **I did not derive grants from attendance —
   that is an access-control decision, not a data chore.**
2. **RE-CHUNK BACKLOG (priority call).** The producer is fixed, the existing rows are not:
   1,423 chunks over 4,000 chars across 255 videos, **581 of them on 138 RESTRICTED videos, worst
   23,632**. Handbook §6.2 now says plainly that the quote ruling's "~1,400-char largest retrievable
   unit" is false for those rows. Access gate unaffected; an ENTITLED asker can pull most of a talk.
3. **Eugene Khayman shows as a `guest`** — GroupOS has `eugene@ykuni.com`, Members DB has
   `eugene@mds.co`. Add the alias to record `recvSgAirIbbo9Ylb`; `member_email_alias` mirrors Airtable
   so this is yours to make, not mine. `--rescan` promotes him automatically after.

### Speaker state on the 16 (recorded, not fixed — needs #103 / Airtable)
- Linked correctly: Alex Bonilla, Brandon Himmel, Jon Jewett, Jared Mortensen, Khalid Abdulla,
  Ivan Ong, Damon Sununtnasuk, Anjie Liu, Eva Maxfield, Corey Smith, Ary Selener, Cassidy Clawson.
- **Name-shape misses:** "Douglas Iske" vs `Douglas Patrick Iske`; "John Spektor" vs `Jon Spektor`.
  Both real members, both sitting `unresolved`.
- **Correct externals:** Tamar Yaniv (Yuka AI — not in `partners_catalog`), Emily Wang (StoreClaw),
  Meher Patel (Hector AI), Hammad Yousaf.
- **Nathan Ross is in no members row** under any Ross spelling, though he says on stage he joined 2017.
- **Hack Contest has 0 speaker links** — no names in the title; ~12 presenters live in the transcript.
  Hand-patching will not stick: `load_speakers.py:287` re-patches any `guest`/`unresolved` row.

### Still open from before
- ~640 pre-2025 videos untranscribed (~$137). Local files now make this a folder + manifest away.
- #102 answer-layer wiring · #104 adjacent-turn topic lag · #72 load test (never run).

## STATE 2026-08-28 (close) — read this first

**PROD = `15ff4978`. Staging identical. Gate GREEN (306, EXIT 0).** Five promotes today; every fix
proven through the workflow, every probe row cleaned. Shipped: **#125** (an absent membership status
is not an inactive one — 53 false claims → 0), **#149** (a live event called finished + the clamp
answering a yes/no in machinery), **#150** (Summit video entitlement + the `is_restricted` flag now
per-asker), **#151** (video recommendations: count, tailoring, follow-up binding, no old-event
padding), **#153 + the #102 time-decay slice** (intent questions: recency in ranking, stated facts
beat a missing tally). **#126** closed NOT REPRODUCIBLE; **#148** and **#152** filed.

### FOUR THINGS WAIT ON ANDY — nothing else is blocked
1. **#147's authority shape.** Its SQL is already LIVE (`registration_status` · `is_registered` ·
   `member_alias_ids`; `event_who` calls them — 130 → 145 registered, **15 recovered, 0 lost**).
   Paused on: roster-only · **one-function-two-facets (recommended)** · union. The event-resolver
   half is untouched — `event_who('vegas')` still lands on a Feb 2025 chapter dinner because the
   resolver matches WORDS IN THE TITLE.
2. **All 16 Summit videos read `access_restriction = public`.** They flipped in GroupOS, not by us,
   and it contradicts his ruling ("restrict them to summit attendees and staff"). Deliberate or fix?
   Grants are written either way and harmless if public.
3. **The re-embed go** for the 7 Aug-26 videos embedded while restricted (metadata-only vectors).
   scorecard-df executes it; it correctly refused to act on a peer's say-so while Andy's answer is
   pending. Note: the decay fix already recovered the Khalid miss WITHOUT the re-embed.
4. **A v4 transactional template** for the 50 undelivered announcements — see below.
   **Live check 2026-08-28 (this session): `mds_summit_videos_live_v3` is APPROVED but Meta filed it
   MARKETING — the third reclassification in a row.** Sending v3 to the 50 would hit the same 131049
   caps. A v4 only helps if its COPY is transactional; the declared category still buys nothing.

### The announcement, and the template trap that cost three submissions
94 fills sent, **94/94 accepted, 0 send errors**; at close **26 read · 18 delivered · 50 failed** on
Meta's marketing frequency caps (131049) and experiment holdouts (130472). One recovered free-form.
**Meta reclassified UTILITY → MARKETING on v1, v2 AND v3 — even with `allow_category_change: false`.**
The declared category is not a lever; the COPY decides, and "picked for you + watch" reads
promotional. v4 should be strictly transactional (the recordings from your event are available +
button) with the personalization moving to Millie when the member taps in. Also burned: **v1 was
approved but unsendable** — Meta rejects newlines inside template VARIABLES (132018) even though it
approved the example containing them. Test-send every template before generating a wave.
Regenerate fills with `scripts/announce_summit_videos.py`; send with `scripts/announce_summit_send.py`
(resume-safe — a phone already holding a wamid is skipped, so a re-run cannot double-send).

### Traps this day earned
- **A template's approval does not mean it can be sent.** Test-send one before building the wave.
- **`allow_category_change: false` does not hold the category.** Copy decides classification.
- **n8n Cloud's execution quota can take PROD down** — 04:57-05:10Z every inbound died in 50ms at the
  webhook ("Execution limit reached"), staging and prod alike. Andy upgraded; verified back green.
- **Audit a gate before changing it** — the #149 clamp had fired 3 times in 6,017 answers and was
  wrong all three. The audit is what justified touching it; the withhold behaviour never changed.
- **A peer refusing your request can be right.** scorecard-df would not re-embed on my say-so while
  Andy's ruling was pending. Correct.
- **Bank D = 30 questions, 10 classes** (`OLIVIA_BANK_D_SUMMIT_2026-08-26.json`), written but only
  spot-run — the problem-first class came from probes that exposed what my own 8/8 wave missed.

## STATE 2026-08-25 (overnight close) — read this first

**PROD = `8bb0827d`. Staging is identical. Gate GREEN (306, EXIT 0).** Three promotes tonight:
`bbd597b7` → `91c70977` (bank C waves 7-21) → `64995b68` (#146 hidden-number identity) → `8bb0827d`
(place-question rules). Pre/post snapshots for each are in `olivia_snapshots/`.

**#145 is CLOSED: 311 of 319 previously-passing questions hold = 97.5%**, and all 8 regressions were fixed
and verified before the promote. Across the 319: links 654 → 808 · dead links 5 → 0 · dates 641 → 862 ·
route changes 0. Full detail in `SESSION_LOG_OLIVIA.md`; every verdict with its reason is in
`.superpowers/sdd/2026-08-22-finder/eval/grades145_full319.json`.

### The one rule that changed how we work
**NEVER WRITE TO AIRTABLE (Andy, 2026-08-25):** *"it's my acc I'm testing things and I don't want to change
our source of truth."* All three edits I made were reverted. A fix that needs the source of truth gets
raised with Andy or ops — named record, named field — and they make the change. Mirrors, Supabase and the
workflow are still ours to edit.

### Start here
1. **#147 — two sources answer "is this member registered?" and disagree.** Andy's agenda said yes while
   who-to-meet said no, one minute apart. MEASURE FIRST: how many members do `event.attendees` and
   `event_registrations_live` disagree about for the Summit? Three means file-and-move-on; thirty is an S1
   today. The ticket also carries the second half: the event resolver matches WORDS IN THE TITLE, so
   `event_who('vegas')` lands on a 2025 chapter dinner and Inspire 2027 is unreachable from the word Vegas.
2. **#146 leftovers** — a silent-drop alarm (this class was invisible until a member complained), and a
   hidden-number member's history being keyed by the opaque id instead of joining their phone history.
3. **6200** — the nudge answer no longer invents a search result but is still thin; it should restate where
   the thread stands.

### Loose ends nobody owns
`MY.1563712991959404` (2026-08-24 01:50Z) is an unlinked hidden-number id — somebody got silence that night
and we do not know who; `scripts/olivia_link_wa_id.py --find` shows it. · The member record for Tudor Tanase
has country CY with the city Baia-Mare (Romania), so he surfaces in Cyprus answers. · `viewing` is set to a
full sentence in `mds-digest-web/src/app/api/olivia/schedule/route.ts:384`; renaming it to a token is one
line in that repo, which deploys on push. · Andy's own Summit registration is deliberately back to "not
registered" — the gate uses him as its non-attendee control, so registering him turns the gate RED (that
coupling is in #147).

## STATE 2026-08-24 (END OF DAY) — read this first

**GOAL OF NEXT SESSION: PROMOTE.** One thing stands in the way, agreed with Andy at close.

**THE ONE JOB: re-run the 319 bank C questions that were already PASSING.** Everything measured today
was the 192 FAILURES (155 now pass, 81%). Nothing has checked what nineteen waves of rules, stamps,
gate checks and nine SQL changes cost the answers that were already good. This is not caution for its
own sake — **two questions regressed inside the fail set in the last round alone** (6500 and 6267 got
worse), and **wave 9 broke staging outright for eight hours**. A stratified sample of ~100 of the 319
is enough signal; the full 319 is better if time allows. If it holds, promote. If it does not, the
regression is on staging where it belongs and not on 700 phones during Summit week.

**State:** staging `daf8ec82` · gate **306 EXIT 0** · **PROD `bbd597b7`, untouched all day.**
The head-to-head that said stage 91% vs prod 87% **predates waves 7-19 — treat it as stale.**

### What shipped LIVE today (SQL is prod-shared; these are already serving members)
#106 staff/team never in member-facing lists · #128 the doorman counted PHONES not members (34 RPCs, 5
members getting empty results from everything) · #129 event-specific partner offers, entitlement-gated
· #130 a member with two numbers sees ALL their chats · #131 Andy's removed-member ruling · #133
partner ranking · #134 `matched_total` · #135 exact brand name outranks the embedding hybrid · #136
country counts · #137 no Airtable record id in an answer.

### Traps this day earned — read before touching anything
- **Verify THROUGH THE WORKFLOW, never by calling the RPC directly.** `Attach Embedding` injects an
  embedding into every tool call, so searches are RRF hybrids. I "proved" #133 with plain SQL and it
  proved nothing; #135 was the real cause and only a staging probe showed it.
- **One probe is not verification.** Wave 9's `const` ordering bug hid from a single probe and errored
  89 of 255 turns for eight hours. Probe several question SHAPES, then check execution status.
- **Audit a gate regex over all 602 answers BEFORE enabling it.** Two were designed and rejected —
  both fired on more correct refusals than wrong ones. "I can't check that" is often right.
- **Stamps must match the payload SHAPE.** Every stamp read the truncated `body` and silently no-opped
  on large payloads; the finder puts its count at the TOP level, not per row. Both were invisible.
- **The verbatim digest route bypasses `Format Reply` entirely.**
- **Measure before reporting.** I twice raised something as an incident before checking it.

### Open for Andy
1. **#132** capability card — real answer vs the card. His steer: lead with what she can DO, and guide
   a new member rather than dead-ending them on chat access. Not a prompt fix (the turn is routed
   `help` deliberately, documented 2026-07-30).
2. **#123** blocks 3 questions — the events catalog is unreachable.
3. **#32 cost is still untouched** and the Answer Seed grew a lot of rules today — per-turn cost and
   latency are unmeasured since.
4. The AT roster row for Belen still links a duplicate member record.

## STATE 2026-08-24 (SECOND overnight session) — read this first

**Waves 7, 8, 9 and 10 are ALL APPLIED to staging.** Staging versionId `57db4b77`; gate **297
checks EXIT 0** after every wave. PROD is unchanged at `bbd597b7` (#114 only) and still serving
members — nothing has been promoted.

### What the 50-question tranche proved (and disproved)
A stratified 50 of the 192 bank C fails was re-run after waves 7+8 and graded BY HAND on the
strict scale: **23/50 = 46% of previously-failing questions now pass.** Mechanically over the same
50: links **90 → 126**, dates cited **12 → 34**, canned non-answers **3 → 1**.

**The misses were mostly rules that never executed, not bad rules.** Two mechanical faults, both
in `Answer Merge`, found by reading the live execution rather than the code:
- **M1 — every stamp parsed the already-truncated `body`.** Order is: build body → squeeze rows →
  blunt-slice at CAP 26000 → *then* the stamps `JSON.parse(body)`. Over CAP that is invalid JSON,
  the parse throws, the stamp silently no-ops — on exactly the large payloads the stamps exist
  for. That is why counts/cap scored 0/3, freshness 1/4, partner 1/3. Wave 9: stamps read `r`.
- **M2 — `clipSafe` covered the first-pass trim but not the large-payload path.** The halving
  squeeze re-sliced every string field raw (url fields included) and the backstop blunt-sliced the
  whole string. Wave 9 makes both URL-safe and exempts url/link keys from squeezing outright.
  ⚠️ **Correcting an earlier claim in this repo: `clipSafe` was never "dead code".** It is called
  once in each node; a bad regex (subtracting the definition from a count that never included it)
  produced that false reading. It was INCOMPLETE, not absent.

### Two graders' notes that turned out to be wrong when probed
- **6217 was NOT a cap failure.** The tool returned 10 rows and the S3 stamp said so; Millie
  printed an 11th name carried over from the previous turn's San Diego list. An ungrounded name,
  not a cap miss. Austin holds 13 member-facing records against a 10-row cap with no total, so the
  answer also implied completeness. Wave 10 (S5) fixes both; verified live.
- **6222's canned line is the GATE'S HARD-STOP CLAMP**, not model text — `Gate Verdict` returns a
  fixed sentence after 2 failed regenerations and discards the draft. Not touched: it is the
  safety backstop and changing it needs Andy.

### Open for Andy
1. **The removed-member severe (6080 / 6272 / 6277) is DELIBERATELY UNFIXED.** The bank C expects
   say a removed member gets no profile at all — no dates, no link, no reason. Andy's recorded
   **2026-07-26 ruling** says past members ARE findable ("I don't have a member named Lori" was a
   lie), and the leak gate still asserts exactly that. **Two rules point opposite ways; only Andy
   settles it.** Until then these stay failing.
2. **#123 blocks 6372 / 6400** — the 2027 events the expects want (Cancun) live in the events
   catalog that every `event_*` call is misrouted away from.
3. Promote decision, after the full 192 re-run.

## STATE 2026-08-24 (overnight close) — read this first

**Millie is LAUNCHED.** She was announced on stage ~01:50Z 2026-08-24. **PROD = `bbd597b7`** (#114 venue-day
only). Launch health: 200/200 executions green, 47 members, zero errors; 62 real answers graded **87%**
(54/8). Prod is serving members right now — treat any prod change as a live change.

**STAGING = the #108 finder + fix waves 1-6 build** (`f31b8c83` after the #32 revert). This is what bank C
measured. **Nothing is promoted beyond #114 — Andy has not approved a promote.**

### Paths — read this before you look for a file
**Every `eval/...` path in this handoff is relative to the #108 worktree
`.superpowers/sdd/2026-08-22-finder/`, not to the repo root.** There is no repo-root `eval/`.

### DONE — the head-to-head is graded (no longer the first job)

**STAGE 91% (62 pass / 6 fail) vs PROD 87% (54 / 8)** on the 68 launch questions. Comparable set 49:
**stage wins 6, prod wins 1, 42 ties.** Graded by hand (three dispatched graders died; the last two were
killed to stop them overwriting the output). Files: `grade_h2h_0.json`, `grade_h2h_1.json`,
`grade_h2h_all.json`. The six wins are prod's launch defects — canned refusals became sourced answers,
all false "restricted" labels gone, the channels question fixed.

**Three items this added to wave 8:**
1. **False blanket refusals** — the one regression (9→6): "not something I share for any event, registered
   or not" is false; a refusal must state the REAL gate. Same class as bank C 6266/6267/6498.
2. **Empty gate answers** — a correct gate that offers nothing (no count, no alternative) where sibling
   answers on the same build gave both.
3. **Thin first-touch greetings** — a bare "what do you need?" where a new member needs orienting
   (partly confounded, see below).

**⚠️ CONFOUND to respect in any future prod-vs-stage run: 13 of 68 are not comparable.** Prod answered from
real members' phones (several Summit-registered); all stage answers came from the probe phone (Andy, NOT
registered). Use a registered probe identity or exclude registration-gated questions.

### Superseded — the old first job
**Grade the Summit prod-vs-stage head-to-head.** `eval/summit_compare.json` already holds all 68 launch
questions with `prod_answer` and `stage_answer` from the staging run (108 turns, EXIT 0, same build bank
C measured). **Only 62 of the 68 carry a `prod_score`** — six questions arrived after the prod-grading
harvest, so `prod_score` is null on those: they can be graded on the stage side but have no head-to-head
winner, and they are not prod passes (the launch 87% is 54/62). Grade `stage_answer` on the strict scale
(1-10, no 7, ≥8 pass), declare a winner per question, and report regressions first. Mechanical deltas already computed, prod → stage: canned over-refusals **2 → 0**,
ellipsis-URLs **0 → 1**, narration **0 → 1**. My hand-read of the 8 prod fails looked strongly better on
stage (the fabricated "at the Summit with you" framing is gone; both canned refusals became sourced
answers) — **that is a hand-read, not a verdict.**

### Then: apply the waves, then re-run the fail-set (Andy's sequence)
1. `python3 scripts/olivia_loop/apply_fixwave7_2026-08-24.py` — written, committed, dry-run clean, **not
   applied**. Carries: link placement + withheld-recap-links + the **ellipsis-URL `clipSafe()` root-cause
   fix** (the biggest single win — 20+ fails), honest counts + ≤10 cap with true totals, internals
   narration by SHAPE (11 audited fires, 0 FPs), follow-up continuity off `turn_state`, Andy's SHARING RULE.
2. **Write wave 8** from `eval/fixplan_bankC.md`. Order: the REMOVED-MEMBER severe first (6080/6272/6277 —
   full profile, join/leave dates, a hint at why she left), then ungrounded claims (fabricated attendance
   9044, invented fit reasons 6089, invented video titles 9048), wrong-source citation (6380, 9046),
   missing attribution (6094), date labeling (recorded vs added), all-sources coverage, welcome-card
   misfire (6190), leaked self-correction artifact (7030), channels routing (9031), restricted LABEL smear
   (9007/9026 — the retracted #127's real fix).
3. Keep waves 7 and 8 as **separate scripts** even though they apply together — so a regression can be
   attributed to one batch without unpicking the other.
4. Gate `python3 scripts/olivia_leak_gate.py` must be EXIT 0 (292 checks; never pipe through `tail`).
5. **Re-run the fail-set only**: `eval/bankC_failset.json` (192 ids) + `eval/launch8_probes.json` (8
   verbatim launch questions). Re-grade, count what is left. Empty → promote decision. Not empty → wave 9.

### Numbers to beat
- Bank C: **319 pass / 192 fail / 91 context = 62%** on 602 organic questions.
- Fail rate by class: **FOLLOWUP 47%** (51/108, the weakest and the biggest class) · PARTNERS 54% ·
  EVENTS 58% · SAFETY 45% · PEOPLE 41% · RECOMMENDATION 38% · EXPERTISE 32% · CONTENT 22% · VIDEOS 28%.
- Launch prod: 54/62 = 87%. Bank A (older, easier): 87-89%.

### Traps this session earned the hard way
- **The evidence clipper truncates URLs.** `Answer Seed`/`Answer Merge` clip with `slice(TIER) + '…'`;
  wave 7's `clipSafe()` fixes it. Any new clip site must use it.
- **`score_prep.py` had to be taught to paginate** — PostgREST's 1000-row cap silently hid 177 answers.
- **A judge's kill-shot is not a verdict.** Seven expect/judge errors were overruled against the live
  warehouse this session, and one pass was flipped to fail. Verify anything decisive before counting it.
- **`curl` PATCH/writes to PostgREST are classifier-blocked**; use the supabase MCP for data writes.
- **Andy's verify-first gate is load-bearing.** The #32 cost fix looked perfect and silently killed
  retrieval; only an A/B against pre-patch tool-call distributions caught it. Do that for every
  prompt/tool-shape change.
- **`caffeinate -w <runner pid>`** while a long run is in flight — a machine sleep killed a grader.

### Open, needs Andy
- **AT roster row for Belen still links a DUPLICATE member record** — repoint it in Airtable (or delete the
  duplicate "Belen Gallardo" record) or a registrations sync will undo tonight's fix.
- **#125** copy split (unlinked number vs genuinely inactive) — hit a paying member live at launch.
- **#32 cost plan** (5 levers) — sequenced after this loop closes, per Andy.
- Promote decision after the fail-set re-run.



> ⛔ **Standing tiers (Andy 2026-07-29/31): Fine without asking** = read-only diagnosis · the LEAK
> GATE (`scripts/olivia_leak_gate.py`, free) · staging edits under the `olivia_wf.py` lock ·
> single-question staging probes. **Propose + WAIT** = any eval RUN (TEST ≤50 / FULL) · **and
> STARTING ANY TICKET (Andy 2026-08-19): a new session opens with the briefing — next ticket
> NUMBER + NAME + STORY — and waits for the go. "Continue working on Olivia" = show the briefing,
> not start. Standing orders/approved plans order the queue; they never start it.** **Andy
> runs** = `promote` · prod edits (emergency rollback excepted). The session classifier blocks
> lock/promote for me — Andy runs both in his terminal (proven 2026-08-03; `lock` worked again
> later that day — try it, fall back to Andy if blocked).
> **Vocabulary: "gate 202" = 202 safety CHECKS (free) · RUN = firing the eval bank · PROBE = one question.**
> **New standing traps (2026-08-20):** ① TWO Summit-named catalog rows — "MDS Summit Singapore
> **Night Out**" (side event) vs the real `recrATwhUDA55iQN5`; naive name-matching grabs the wrong
> one ② template quick-reply taps arrive `msg_type='button'` and are NOT in `olivia_messages` —
> only `olivia_webhook_events` has them ③ audits opt out of equalizer logging via the
> `X-Olivia-Audit` header (never a p_limit heuristic — that silenced a real lane) ④ the E2E
> canary pattern: temp registration row, probe, DELETE same session.

## STATE 2026-08-23 (#113 CLOSED — the Summit event is RELOADED from the 09:52Z scan and live)
**Millie now serves the current run-of-show.** `scripts/load_event_graph.py` is a true refresh (diff
report by name → upsert → FK-safe reconcile → provenance), loaded from
`~/Downloads/event_graph_20260823T0952Z.json` (`_meta.scannedAt` 2026-08-23T09:52:31.687Z, verified
fresh against the ledger). **activities 50→86 · sessions 31→26 · attendees 178→199 · people 199→234 ·
locations 18→27 · participant_types 6→7 (`MDS`) · activity_audience 180→227 · activity_person_grants
183→698 · check_ins 22→151 · orders 138→144**; deleted 49/10/12/11/1/20 exactly as predicted; a repeat
dry-run is `+0 ~0 -0`; `events.source_scanned_at` + `loaded_at` stamped. Golden self-test re-derived:
plain Member **7** on day one, Women's Lunch grantee **8** (the +1 invariant is the test, not the
integers). Live proof: `op=day at=today` returns *Sunday 23 August* with Arrive & Check-In to the Hotel
at 3PM … Explore Singapore Beyond the Summit; Women's Lunch / Event Partner Check-in stay hidden from a
non-invited member. Runbook + six traps in `OLIVIA_HANDBOOK.md` §4.9. Three real defects were found by
running it — 3.9 vs PostgREST fractional seconds (faked 31 "changed" rows), GroupOS recreating an
attendee document on a role change (409), and curl argv vs macOS ARG_MAX on a 92 KB description — plus
a final-review fix wave (a loader SKIP is never treated as an export removal; three silent-swallowed
reads now fail loud; ordered paging; measured delete counts; `--new-event` guard). **Follow-ups filed:
#120 loader hardening · #121 `db/` excludes the `event` schema · #122 "Explore Singapore" is four daily
copies.** Next refresh = one command; read the `- ` and `!! skipping` lines before the real run.

## STATE 2026-08-23 (#114 CLOSED except AC4 — venue-day "today" LIVE on prod; #113 waits for a fresh export)
**#114 "today at the Summit" (Ian Sells, Singapore, got Saturday on his Sunday) — fixed in two
layers and PROMOTED.** mds-digest-web LIVE (`/api/version` ≥ `9d0ec41`): the schedule route resolves
`at=today|tomorrow|yesterday|<weekday>|YYYY-MM-DD|instant` in the venue's own zone
(`src/lib/schedule-day.ts`, 24 vitest cases), every answer carries `now_at_venue`, `day` returns
`day`/`day_label`/`resolved_from`, and **`next` returns the rest of the venue-day** (Task 2b,
`95eea25` — Andy's 12:42 SGT test had shown `op=next` hiding half of Sunday behind a hard 3; fix wave
`9d0ec41` labels the items' day, keeps `asked_day`, falls back on impossible dates). Olivia prompt
**promoted by Andy 2026-08-23 02:49 ET (prod versionId `bbd597b7`)** — `apply_114_venue_today.py`: the
`event_schedule` tool description says pass the WORD (today/tomorrow/a weekday), the TODAY line carves
out the venue exception, one bullet names the case. Andy promoted **#114 only**: staging was re-built
from prod (combined snapshot `staging_2026-08-23T064414Z_108-plus-114-applied` kept), #108 re-applies
its own edit and gets its own promote. Prod probe after promote (execs 100159/100160): "what's
happening at the summit today" → *"It's Sunday, 23 August at the Summit in Singapore — kickoff day!"*
+ full day; "what's on tomorrow" → *Monday, Aug 24*; tool_args literal `at:"today"/"tomorrow"`.
**AC4 CLOSED (Andy tested on WhatsApp, 2026-08-23 ET afternoon, Singapore already on the next day: working).** #114 is fully closed. **#113 (whole-event refresh, plan
`docs/superpowers/plans/2026-08-22-summit-event-refresh.md`, 4 tasks, not started): waits for a
GENUINELY fresh GroupOS export — `event_graph (1).json` was a 17-Aug scan (`_meta.scannedAt`
2026-08-17T22:16Z; 4 of 5 people registered 18–21 Aug absent); Andy's live GroupOS already shows
renames ("Arrive & Check-In to the Hotel at 3PM"), Welcome Dinner at Pool, a new "Explore Singapore
Beyond the Summit" — none of that is in any file we hold.** Two-agent rule added to CLAUDE.md (lock =
the only mutex; own-ticket doc sections; last committer rebases; message the peer session).

## STATE 2026-08-23 (#108 The Finder BUILT + PROVEN ON STAGING; Andy: promote, then decide on the 100-Q bank)
**The Finder ships one composable filter tool covering every data layer** — `find`
(`POST /api/olivia/find`, mds-digest-web, code live on Render) wired into **STAGING**
`bqHstPDi84uOhTCJ` (versionId `a49047ac`, Answer Tool + Answer Seed; `event_who` now carries
`op:'people'`). Belen's "which resellers are coming to the Summit?" now answers **17** (of 102
Summit attendees) / **122** community-wide (of 735 actives), every person with reasons; a country
breakdown sums cleanly (5 buckets); the disclosure engine (R1-R10) holds — a 🟡 filter (e.g.
`sku_min`) returns counts only, a non-member's `chat:` filter never names anyone. Gate **292 checks
EXIT 0** (26 finder checks). Full close block + AC table on `OLIVIA_SPRINT_4.md` #108. **#114 already promoted alone** (Andy
2026-08-23 06:48Z, prod `bbd597b7`); staging was rebuilt from prod (+#114) and #108 re-applies next
(`apply_108_find.py`), then **Andy promotes #108 separately** (`python3 scripts/olivia_wf.py
promote`). Before that promote, Andy decides whether to run the
**100-question eval bank** first (recommended — the real risk is the model reaching for `find`
where `expertise_search`/`content_search` was the better tool). Follow-ups filed, not blocking:
**#115** (geo/business-model data hygiene) · **#116** (finder phase 2 content+video, phase 3
events/partners/forms — own plan) · **#117** (`--cleanup` leaves probe message rows) · **#118**
(`event_who` should return a flat roster). **Lock released** (staging free for the next session). Staging re-applied after the #114-only promote — versionId `4321f06a` (snapshots
`pre-108-reapply` / `108-reapplied` / `108-final`), #114 seed edits intact. Re-probes: exec
`100210` (17 named), `100212` (Europe → 1), `100278` (breakdown by country, 5 buckets = 17,
`people:[]`, reply reports counts not names). Parser robustness (`mds-digest-web` main,
`0c46d42` + `d3fe132`): a multi-field object (`{segment,event}`) now validates as an implicit
`all` instead of 400ing ("leaf holds exactly one field"), `where` may arrive as a JSON string,
and `group_by` with no `return`/`ret` now defaults to `breakdown` — closing the two distinct LLM
tool-call flakes found re-proving this ticket.

## STATE 2026-08-22 (SESSION CLOSED — #97 PROMOTED + PROD E2E PROVEN; #105/#106 filed)
**PROMOTED 04:11Z (Andy): prod `7e4be40a` (#97) → #107 ~05:24Z prod `8f48fdb8` → #107b/c ~07:10Z prod `25ceefe1` → #107e ~08:40Z prod `d9538ca6` (picker lead: "Here are the Summit attendees I've recommended to you that I can reach for an intro…"; route `d8f8250` title-case) → **#107d ~08:00Z prod `d2961c8d`: eligibility = Summit attendee + phone (Millie-user rule DROPPED both sides, Andy); picker rows = expertise · speaker · city; route `dd02a9b`** · post-Yes = WhatsApp LIST picker (route's exact ids) · suggestions NEVER filtered/shortened (Andy) · buttons always (≤1024 inline, >1024 follow-up button message) · first-contact PS first when offer present · intro-tap path silent-gated (SELFTEST). #109 templates **APPROVED** (accepted/declined UTILITY, lapsed MARKETING — verified live 2026-08-22) — route logic next session (free-form requester notices die outside 24h window). #110 filed (tap turns not saved to history). Belen's identity split fixed (registration + roster row → her Staff record) so she can use Summit lanes + intros. PROD E2E: exec 96653 Accept tap → row 13 accepted/tap → 2 texts delivered to Andy's phone, 0 LLM rows. Andy's visibility ask → #106 filed (SQL-verified: search lanes exclude Staff; event lanes don't; `test-andy-8153` purged). Andy's lock: `python3 scripts/olivia_wf.py unlock` when done.**

### (pre-promote state)
## STATE 2026-08-22 (pre-promote — #97 BUILT + REVIEWED)
**#97 brokered intros: 7/7 tasks + final whole-branch review + 2 fix waves, all re-reviewed clean.**
LIVE on prod: route `/api/olivia/intro` (mds-digest-web `535a23a`, Render) · `olivia_intros` v2 +
`late_taps` · `Intro Sweep` on Reminder Sender `QhJw46Mr7LAP8fdz` (minute tick, exec 96624 clean).
STAGING `bqHstPDi84uOhTCJ` carries the tap branch (C1 binds taps to `consent_wamid`, C3 fail-open)
+ `member_intro` tool — **PROMOTE = Andy (`python3 scripts/olivia_wf.py promote`, lock RELEASED),
T4+T5 together**, then one real tap E2E closes the ticket (Andy is NOT Summit-registered → canary
registration for his test, or an eligible member tests). Rulings 2026-08-22: accept-is-final ·
Eugene row 2 set `declined` (his last tap) · non-attendee wording = Summit-PILOT line, never
"register" · #105 webhook-signature ticket filed (Andy: file + ship as own ticket, next session,
before any wide announcement). Reports: `OLIVIA_97_BROKERED_INTROS_REPORT.md` (Andy, listenable) ·
`OLIVIA_97_INTROS_FOR_EUGENE.md` + `_SHORT` (4,587 chars) · artifact
https://claude.ai/code/artifact/446286fc-411e-4e78-981e-9e858efa81d2. Full close block on the board.
SDD ledger `.superpowers/sdd/2026-08-20-brokered-intros-full-build/progress.md` (gitignored scratch;
secrets scrubbed). ⚠️ Scorecard main has ~15 unpushed commits from 3 parallel agents (#103, MotM,
#97) — push is Andy's/next session's call. Lesson saved: check-first before "add env var"; doc
claims about where a credential lives get a live probe.

### NEXT SESSION QUEUE (brief Andy, WAIT for go)
1. **#109** requester-side notices as templates (check `python3 scripts/olivia_intro_templates_109.py status` → APPROVED first; then route change; before any announcement).
2. **#108** (filed) attendees ∩ chat membership / business model tool — Belen's 'resellers attending' questions were answered wrong; truth table in the 08-22 log.
3. **#106** Staff/non-member records never surface in member-facing lists (staff attendees like Belen must stay usable as requesters) · **#105** webhook signature · **#110** intro-tap history.
   (#97 CLOSED: promoted + prod E2E proven; release-notes line still to post at sprint close.)
3. #103 open rungs (other agent) · #102 brainstorm · Millie promote (rides the same promote) · smoke
   partials · <2024 transcripts decision · sprint-close pair.

### (previous state below)
## STATE 2026-08-21 EVE (SESSION PAUSED mid-ticket — Andy: "i need to go, pause")
**#97 BROKERED INTROS BUILD IN FLIGHT — 4.5 of 7 plan tasks done.** Eligibility LOCKED by Andy
("lock them as-is": both sides Millie users + Summit-registered `recrATwhUDA55iQN5`; <30d parked).
Prereq resolved: env was on RENDER all along (plan said Vercel — wrong; both META_WA_* pre-existed).
DONE+reviewed: T1 ledger v2 (migration `olivia_intros_v2_20260820`, commit `9f380b1`) · T2 route
`/api/olivia/intro` (mds-digest-web `e6f8b48` DEPLOYED, 16/16 rulings, sweep isolation +
recency picker) · T3 live matrix 9/10 PASS zero real sends, DB baseline restored, SELFTEST
not.like proven 280==280 · T4 staging tap branch (7 nodes + Log Inbound button fix — PROD DROPS
Accept/Decline taps TODAY incl. Eugene's POC reject; execs 96072/96082; blast radius proven safe).
T5 implementer DONE (member_intro tool live on staging, exec 96162 chain proof, gate 264 EXIT 0)
— **REVIEW PENDING** + 3 open concerns (Plan Request regex swallows "connect me with someone" ·
picker renders prose not LIST · send branch live-proof deferred to post-promote tap).
**RESUME: SDD ledger `.superpowers/sdd/2026-08-20-brokered-intros-full-build/progress.md`** —
dispatch T5 reviewer, then T6 sweep tick, T7 close. ⚠️ staging lock HELD (claude, expires
2026-08-22T01:25Z); staging carries T4+T5 UNPROMOTED; sweep of POC row 2 will message Andy the
expiry line once T6 ships past 2026-08-27. Andy's promote covers T4+T5, then ONE real tap E2E.

### (previous close below)
## STATE 2026-08-22 (SESSION CLOSED — transcripts reached the ANSWERS; 5 promotes, all verified)
**The day's theme: the 2025-26 transcripts were live in the database but the ANSWER LAYER never used
them. Four separate causes, each found by reading executions, each fixed and promoted.**

### What shipped to PROD today (5 promotes, each: diff → gate → promote → verify → snapshot)
1. **Dead denial rule killed** — Answer Seed still said *"NO video has a transcript: what-was-SAID-in-it
   questions get a plain 'transcripts are not available yet'"*. A FOURTH stale rule I missed on 08-21.
   Replaced with TRANSCRIPTS ARE SEARCHABLE (2025+2026) + concept-term routing + pre-2025 boundary.
2. **Quote/timestamp discipline** — NEVER OFFER TO FETCH WHAT YOU WERE ASKED FOR: a quote/where/what-
   exactly question carries the verbatim line + speaker label + timestamp IN the answer.
   Proof: Bryce Alderson's SKU-expansion passage quoted at **00:37:30**.
3. **`call_transcript` enforced IN CODE** (`Attach Embedding`) — the tool schema listed only chat/FB
   sources, so the model kept passing `p_sources` without transcripts; two prompt fixes failed, so the
   third moved into code ([[feedback_code_beats_prompt_rules]]). `p_chat`-scoped asks exempt (transcripts
   carry no chat_name and would pollute digests). + conflicting-sources rule (transcript vs chat both
   reported and attributed).
4. **Gate over-refusal fixed** — the `off_topic` field added for #104 blocked short affirmatives and
   CLARIFYING QUESTIONS; "yes booth" was blocked 3× and served a canned "couldn't verify". RULE ZERO now
   exempts both.
5. **#112 CLOSED** (filed as #108, renumbered — the parallel session had already issued #105-#111) — the #80 OFFER BINDING already existed; its ACCEPT_RE end-anchor made "yes booth"
   miss. Affirmative may now carry a quantifier/typo; binding delivers EVERY offered video.

### #103 speaker work (same session, warehouse-side)
Library coverage **40% → 87%** (2025 97%, 2026 98%). Rungs: speaker_ids id-join · names · title/description ·
partner sessions · Zoom cues (participants + talk_seconds) · **AAI letter-mapping** (270 letters,
`video_speaker_letters`) · **frame-OCR** (ffmpeg from presigned URLs, 388 frames, 123 role-aware links,
moderators from "Moderated by" cards). 578 entities / 321 members / 1,391 links. Review CSVs triaged with
Andy: partner contacts resolved (Meher→Hector, Nadav→CapEc, Ben→Superfuel), 10 ASR/spelling twins merged
via speaker_aliases, Brandon Fishman created as guest on Andy's ruling, 6 unknown names left unmapped.
**Andy's rule codified: a MEMBER is never switched to partner/guest — partner-ness lives in
`affiliation_partner_id`.**

### Templates
`mds_birthday_box_address` **APPROVED as UTILITY** (id 917599728064581) — sent to Andy's number, status
`sent`. ⚠️ The test exposed bad address data: Andy's street = "street", Ian Sells = "iasi, Cimişlia,
Moldova", Eugene Khayman has TWO records (one with a Miami address, one empty). A real send needs a
which-record-wins rule + a "no usable address" path. Button taps do nothing yet (no workflow branch).

### ⚠️ TICKET NUMBERING (two sessions, one board — 2026-08-22)
The parallel #97/#107 session issued **#105-#111** while this one was running; I filed my
offer-binding ticket as #108 from a stale max and collided with its "attendees ∩ chat membership"
ticket. Nothing was overwritten — both rows survived — and mine was renumbered to **#112**.
**Rule: claim the next number from the board's CURRENT max at the moment of filing, never from
memory or from the session's own start state.**

### OPEN (next session)
1. **Jasim-class within-video ranking** — chunks of one video share the video's date, so the tiebreak is
   arbitrary; asked for a quote from later in a call, retrieval returns the opening minutes. `content_search_v2`
   change, every lane uses it — Andy's go needed.
2. **#102 answer-layer wiring** — speaker/role/talk-time/partner tables exist and NO lane reads them.
   "How many videos is Bonilla in?" / "who spoke for Riverbend?" still unanswerable. Brainstorm first.
3. #103 leftovers: moderator inference · ~134 pre-2025 videos (same OCR/letter rungs) · affiliation backfill.
4. #72 LOAD TEST — still never run, still the biggest pre-announcement risk.
5. Airtable-side dup-record merges (Andy's, never-delete rule): Meher ×2, Nadav ×3, Ben ×2, Eugene ×9.

## STATE 2026-08-21 DAY (SESSION CLOSED — Andy drove speaker work; smoke settled at 95/100)
**Smoke rerun: 5 of 10 non-PASS flipped → 95/100 effective, 0 fails** (#104 fixed at the enforcement
layer: FC `off_topic` field + Gate Verdict non-filterable; all 3 original fail-chains reproduced
clean with recreated adjacency). Remaining 5 partials: 2 data-side (4070 women-events catalog gap ·
4038 links-grading) + 3 behavioral (4095 3-day window serves latest daily · 4010 wording shades to
denial · 4100 staff-vs-member distinction) — each ticket-size, none chased.

**#103 REOPENED (I closed it on a field-scoped metric — 413/413 measured the FIELD; Andy caught it)
then REBUILT: library coverage 40% → 81%** (2026 **91%**, 2025 78%). Full state on the board block.
The load-bearing facts: identity space = `speakers`/`speaker_aliases`/`video_speaker_links`
(+`video_partner_links`); evidence rungs A `speaker_ids`→GroupOS-id→email · B names · C
title/description · D partner sessions · E Zoom cues→PARTICIPANTS (`role`+`talk_seconds` — group
calls have participants, not headline speakers, Andy's ruling; moderator ≠ speaker, inference open).
**Zoom transcripts carry REAL NAMES per cue** (quote+name+timestamp proven E2E for entitled asker);
AAI = letters (letter-mapping + frame-OCR open). **418 pre-#101 Zoom chunks were unreachable even
for ENTITLED members** (sensitivity=restricted + rule=public) — migrated, proven both ways.
**Weekly `zoom_weekly.py` now runs the ladder + guest-promotion + participants every run** (step
4.5, full dry-run green). Review CSVs on Andy's desk: `mds_speaker_review.csv` (60 unresolved) +
`mds_participant_review.csv` (12).

### NEXT SESSION QUEUE (brief Andy, WAIT for go)
1. **#103 open rungs** — AAI letter→name mapping · frame-OCR name tags · moderator inference ·
   affiliation backfill · review-CSV triage with Andy.
2. **#102 brainstorm** (ranking: decay · speaker weight · Summit bonus · WA/FB/Video equalization ·
   dossier weighting speaker>participant>FB-post) — CAPTURED-NOT-LOCKED, starts as brainstorm.
3. **Millie promote still on Andy's desk** (one promote = rename + fact-check + boundary +
   timestamps + #104 net). Meta watcher plan unchanged (submit "MDS Millie" on verdict, never
   re-register Mille).
4. 5 smoke partials + 2 bank-truth fixes · <2024 transcripts decision (~$137) · sprint-close pair.

## STATE 2026-08-21 OVERNIGHT (SESSION RAN WHILE ANDY SLEPT — his order: "in the morning; I need to see all green")
**ALL GREEN. Queue ① 2025 transcripts DONE · ② big smoke DONE (bank 90/100 effective · slice 11/11) · ④ Millie CLOSED · #103 speaker sync BUILT+CLOSED same night · gate GREEN at every step (263 checks, exit 0, run 6+×).**

### What shipped overnight (all verified live, all commits on main)
- **2025 transcript batch:** 232/233 videos (1 skip = 10s silent teaser) · 144.8 hr · $33.42 AAI ·
  6,429 chunks (0 mismatches, Zoom untouched) · 232 summaries in-session via 8 parallel subagents ·
  embedded (restricted = metadata only) · entitlement probed both ways · `scripts/aai_submit.py` is
  the persistent batch runner (curl, resume-safe).
- **Millie (queue ④):** staging says Millie everywhere; "what is your name?" fixed at the SOURCE —
  the Fact Check lane was vetoing the name as an unsupported claim (RULE ONE now names her +
  `community_info.assistant_name`). Meta: "MDS Millie" CANNOT submit while "MDS Mille" is
  PENDING_REVIEW (no cancel API) — **when watcher `a1ViYr5FT7iePdN9` fires: do NOT re-register
  Mille; submit "MDS Millie", then Andy re-registers (PIN), promote staging, DELETE watcher.**
- **THE NIGHT'S BIGGEST CATCH: `video_search_v2` (the LIVE lane — the workflow remaps
  video_search→video_search_v2 in Fetch Summaries/Fetch Raw Matches/Attach Embedding) was NEVER
  patched by #101** — entitled members still got blanket [RESTRICTED] E2E. Fixed (grant-bounded,
  attachments stay public-only, is_restricted = the video's flag), both sides proven, migration
  `video_search_v2_grant_bounded_restricted_fix_20260821`. ⚠️ trap: v1 probes pass while v2 serves
  members — always probe THROUGH the workflow.
- **4 stale "no transcripts" prompt rules purged** (Build Prompt ×2, Verbatim ×2, Answer Seed
  boundary now "2025+2026 transcribed, pre-2025 not") + **timestamp-citation rule** (quote → "At
  00:16:37" next to the link; probe proven).
- **#103 CLOSED (filed and built same night, Andy's order):** `digest.speakers` 239 entities ·
  `video_speaker_links` 480 links (413/413 videos) · **212 members EMAIL-evidenced** via the
  GroupOS mirror (`digest.video_speakers` — pre-existing table, all 234 rows have email;
  `member_record_id` is GroupOS-internal, NOT an AT id) + #100 resolver · 24 guests · 3 unresolved
  in `~/Downloads/mds_speaker_review.csv` · verify 7/7 · plan `docs/superpowers/plans/2026-08-21-speaker-sync.md`.
- **Smoke (`OLIVIA_SMOKE_2026-08-21.md`):** bank 89/7/4 → 90 effective (one "fail" is CORRECT #96
  behavior, bank truth stale); 3 real fails = ONE defect → **#104 adjacent-turn topic lag** (filed,
  S1). Slice v2 (problem-first, Andy killed the name-anchored v1 as "BS Qs"): 11/11 right videos
  unprompted, speakers+roles, multi-source answers, zero transcript denials.

### ANDY'S MORNING DESK
1. **Millie promote** (staging → prod: rename + fact-check rule + transcript boundary + timestamp
   rule — one promote covers all).
2. #104 priority call (adjacent-turn lag — 3 smoke fails).
3. Speaker review CSV (3 names) + #102/#97/#103-extension brainstorms (all CAPTURED-NOT-LOCKED).
4. 2024-and-earlier transcripts decision ("Not sure about <2024") — ~$137 for 2018-2024 at AAI rates.
5. Sprint-close pair still open: release notes post + retirement pass.

### (previous close below)
## STATE 2026-08-20 LATE (SESSION CLOSED — VIDEO DAY): PROD untouched; all ships = SQL fns + data loads.
**#100 CLOSED (identity aliases) · #101 CLOSED (video transcripts + real access gating) · gate GREEN at close (263 checks, exit 0, run 7× today).**

### What shipped tonight (all verified live)
- **#100:** `digest.member_email_alias` (5,763 rows; sources preferred/stripe/admin_field/name_match_approved)
  + `resolve_member_by_email()` (active-record-preferring; NULL on ambiguity). 29 approved aliases written to
  **Airtable FIRST** (Members DB `appou5JVr0WIrioWS`/`tblfwOSROSHfuYUxv` — ⚠️ the env's AIRTABLE_BASE_ID is the
  WhatsApp DB, wrong base for this), then mirrored. Audience resolution 634→704 active; the 10 known email
  mismatches 0/10→10/10. **`Pending Group Entrance` now counts as active** (753→754; Current+New+Pending = 718
  = Andy's export exactly).
- **#101:** AssemblyAI transcripts for **ALL 161 videos of 2026** ($26.23, `~/mds_transcripts/2026/`) →
  **2,730 chunks across the 96 videos Zoom never reached** (`meta.provenance='assemblyai'`; #70's 65 Zoom
  videos untouched, checksum identical). **`digest.video_access` = 34,236 REAL grants** (real_match only —
  panel rows are phantoms, 42 yopmail). `content_search_v2` learned the `video_access` access_rule type;
  `video_search` gates restricted treatment per asker (attachments stay PUBLIC-only — file_key leak caught).
  **96 summaries written in-session** (161/161 `summary_source='transcript'`), everything embedded
  (restricted videos embed METADATA ONLY — vector branch cannot leak). Proof: entitled asker retrieved a
  RESTRICTED TikTok-Mastermind passage at 00:05:01, timestamped. Quote ruling (Andy): quote/summarize/TLDR/
  exact-words yes — **full transcripts never**.

### THE QUEUE (Andy 2026-08-20, session close — in this order)
1. **2025 transcript batch** — same machinery (`scripts/aai_transcripts.py` + `apply_video_summaries.py`).
   ~233 videos / 145.6 hr ≈ **$33 AAI**. **Prereq: fresh presigned export from Andy's dev** (current links
   expire 2026-08-27; `04_presign.py --days 7 --year 2025`). Load video_access for 2025 restricted from the
   same pairs file (already covers all years — 375 videos). Summaries in-session again, no API.
2. **Smoke-test batch of questions, focused on the EUGENE CASE** — "best TikTok cold start videos" served the
   thin Milan title-match over the transcript-rich Beginners Panel. Content now exists (transcript chunks
   reachable); the remaining gap is intent-vs-title RANKING in `video_search` + whether the answering layer
   should show more than one video (Eugene: "maybe it should show more than one"). Overlaps #71's vocabulary
   work — read #71 before touching ranking.
3. **Members' connection tasks — #97 brokered intros build** (screenshot proof on file: template intro
   accepted end-to-end, wa.me links both ways, POC list-picker rounds "Pick a member" working). Plan pinned:
   `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`. Still blocked on Andy's RENDER env (plan said Vercel — wrong; digest.mds.co = Render, verified 2026-08-21)
   (META_WA_* onto mds-digest-web) + execution-mode pick.
4. ~~Rename the bot to "Millie"~~ **CLOSED 2026-08-21** (close block on the board). Spelling ruled
   **"MDS Millie"**; staging says Millie everywhere (12 strings, 4 nodes) + fact-check veto fixed
   (RULE ONE + community_info.assistant_name — the checker had silently stripped the name). Meta:
   "MDS Millie" can't submit while "MDS Mille" is PENDING_REVIEW (no cancel API) — **when the
   watcher (`a1ViYr5FT7iePdN9`) fires: do NOT re-register Mille; submit "MDS Millie" instead**,
   then Andy re-registers (PIN), promote staging, DELETE the watcher.

### Standing next-session rules (unchanged)
Open with the briefing (ticket NUMBER + NAME + STORY) and WAIT for the go. Verify against live before new
work. Gate before any ship. #72 LOAD TEST still never run — it remains the biggest open risk before any
announcement.

### New traps from tonight (do not relearn)
- **PostgREST pages are UNSTABLE without `order=`** — an unordered limit/offset walk returned 3,116 rows but
  only 43 of 65 distinct videos. Every pagination gets an order key.
- **Expression indexes can't ON CONFLICT via PostgREST** — loaders diff-before-insert (twice today).
- **Verify Airtable writes against Airtable itself** — `member_profiles` mirrors on its own schedule and lags.
- **The gate's restricted-transcript check is now GRANT-BOUNDED** (restricted chunks only for granted videos),
  not blanket exclusion — that is the #101 invariant, don't "fix" it back.
- **`member_identity` holds 57 NULL-`at_member_id` rows** (one `phone='sam'`) — recorded, not chased.

---
### (previous close, for context)
## STATE 2026-08-20 (SESSION CLOSED): PROD `060701be` — nothing awaits promotion; all of tonight's
## ships live in SQL functions + the digest.mds.co route (no workflow nodes touched).
**Eugene's four: #94 #95 #96 #98 #99 CLOSED · #97 POC proven + plan pinned · smoke 50/50 addressed.**

### 🔬 Eugene-arc smoke (50 Qs, RUN on Andy's go) — `OLIVIA_SMOKE_EUGENE_ARC.md` has the full table
47/50 · A 18/18 · B 12/12 after TWO in-run #95 fixes (audit header `36e1d7d` — the p_limit
heuristic had silenced logging on the plan lane; LRU cycling `0b4b418` — exhausted pools froze) ·
C 12/14 · D 5/6. **#98 CLOSED same session** (`179f6c0` — registrations-ledger authority on BOTH people branches;
re-probed clean). **#99 CLOSED** (note-in-tool; E2E proven via a temporary canary registration, deleted after —
"show me the rest" now re-calls and serves fresh ranked people). **⚠️ Andy: who-to-meet stays
OFF for your phone until you register for the Summit for real** — the canary was test-only. Wording flags → #14. Count drift
157-vs-113 = THE COUNT RULING resurfaced live. **Ian Sells ACCEPTED the real intro** (#3
accepted, links both ways); Eugene's still pending — the sweep/expiry rules are in the #97 plan.

### ⚠️ Board: **`OLIVIA_SPRINT_4.md`** (22 open tickets). **Two sprint-close items still await
Andy:** ① the SMOKE RUN on the 100-bank (the exit exam — proposed, his go) ② validate + post
`OLIVIA_RELEASE_NOTES_2026-08-19.md`.

### ✅ #94 Expertise Ledger v2 — CLOSED 2026-08-19 (this session)
Warehouse-side only (no prod workflow edit, nothing to promote): taxonomy 16→**51 topics**
(18 parents + 33 subs), derive v2.1 live (decay 12/24mo · engagement bonus · forms ×1.2 ·
40%-peak floor — floor proven by live inflate/restore), **594 members scoreable on forms alone**,
verify `scripts/verify_expertise_v2.py` **9/9 PASS**, gate EXIT 0, nightly RPC path re-run clean
(11s). Same-day catch: the substring trap re-opened by short terms (`'vat'`/`'str'`) — biz+persona
CTEs now tsquery-match. Full close block on the board. Commits `0ce7ebe`·`a1250eb`·`8d70f10`.

### ✅ #95 Equalizer for the advice lanes — CLOSED 2026-08-19 (same session, Andy's go)
The execution log showed Eugene-shaped topic asks route to **expertise_search**, so BOTH advice
lanes got the equalizer (member_match_v2 + expertise_search; multi_source/_v2 went VOLATILE to
inherit it). Proof: identical repeated asks 8/8 → 0/8 shared names (REST) and disjoint sets on
the staging workflow path; log carries member_match + expertise_search lanes; gate EXIT 0.
Commit `a31a45b`, close block on the board. ⚠️ Andy's asker row carries the probe history — his
own next real "who knows X" rotates past those names for up to 30d (correct, remember at demos).

### ✅ #96 Attendee-name disclosure — CLOSED 2026-08-20 (Andy ruled it live in-session)
**The rule now in force:** attendee-name lists cap at **10** (display cap — filters/counts always
run over the whole ledger); NAMES require the asker's own registration for THAT event
(registrations ledger = the authority, never `event.people` — Andy's test row exposed that trap
on the live route, fixed same hour); non-attendees get counts/aggregates only. `event_who`
migration + route `3e77774`/`08d42fc`, gate +3 checks EXIT 0, E2E probed both sides. Supersedes
2026-07-20 any-member-sees-names.

### 🔨 #97 Brokered intros — POC PROVEN E2E 2026-08-20 (Andy: "lets try to make a POC and then decide")
Template `mds_intro_request` **APPROVED as UTILITY** (no marketing cap on consent asks). Full
loop ran on Andy's number: `olivia_intros` pending → template delivered → Andy tapped **Accept
intro** → watcher flipped the ledger → links both ways, all `delivered` in `olivia_sends`.
Tools: `scripts/olivia_intro_template.py` (create/status) · `scripts/olivia_intro_poc.py`
(request/watch/status, HARD-LIMITED to the test number). **Findings for the real build:**
template button taps = `msg_type='button'`, NOT persisted to `olivia_messages` (only
`olivia_webhook_events` has them; Mille also answers the tap text as a message — the workflow
needs an intro-tap branch) · plus-is-space on ledger timestamps. **Full ship waits on Andy's
rulings:** conversation intent ("connect us") + workflow branch · per-target rate cap · expiry ·
decline wording · seed copy.

### NEXT SESSION OPENS HERE — brief Andy, WAIT for his go (the ⛔ rule above)
**Queue front: #97 BUILD** (plan `docs/superpowers/plans/2026-08-20-brokered-intros-full-build.md`,
rulings locked, POC proven, Ian's real accept on record) — **blocked on Andy's RENDER env prereq (service `mds-digest-web`, NOT Vercel)**
(META_WA_TOKEN + META_WA_PHONE_NUMBER_ID onto mds-digest-web, then redeploy) + execution-mode pick.
**Next unblocked: #72 LOAD TEST** (sprint goal: it runs BEFORE the announcement; never run).
1. **Andy's desk:** #97 RENDER env + execution-mode pick · **register himself for the Summit**
   (restores his who-to-meet demos — canary was test-only) · THE COUNT RULING (157-vs-113 shown
   live in one conversation) · sprint-close pair still open: 100-bank exit exam (his go) + post
   `OLIVIA_RELEASE_NOTES_2026-08-19.md` · Eugene's intro tap still pending (ledger #2; check
   `python3 scripts/olivia_intro_poc.py status`) · Mille name watcher (`a1ViYr5FT7iePdN9`) ·
   THE COUNT RULING (recommendation: 98 active members, one `event_registered_members` view) ·
   Eugene's Members-DB record pin (9-record cluster) · "MDS Mille" re-register when the watcher
   fires (PIN, 14-day window) · #72 LOAD TEST before the announcement.

### DO THIS FIRST
1. ~~Schedule the reminder sender~~ **DONE 2026-08-18: n8n `QhJw46Mr7LAP8fdz` ("Olivia — Reminder
   Sender"), every 5 min.** First tick exec 86839 (23:15 UTC): stale sweep ran, 0 due, clean stop.
   Faithful port of `olivia_reminder_sender.py` (script stays the manual/dry-run tool); chosen over
   launchd so reminders survive the Mac sleeping — and launchctl is classifier-blocked for me anyway.
   **DELIVERY PROVEN 2026-08-19 05:55 UTC:** Andy's live ask arrived on his phone — sent 05:55:08,
   `read` 05:55:11 in `olivia_sends`. Sender cadence now **EVERY MINUTE** (Andy: 10-min total lag
   too long for minute-level asks). #86 CLOSED.
2. ~~Re-register the number~~ **DONE 2026-08-18 (Andy ran it): the number is "MDS AI Assistant".**
   `POST /register` with the two-step PIN returned success; live API now shows `verified_name:
   "MDS AI Assistant"`, `name_status: APPROVED`, CONNECTED/GREEN. "Oliva" is gone. Existing threads
   may show the cached old name for a while; new threads are correct. Andy holds the PIN (password
   manager — deliberately not written down here).
   **→ NEXT NAME ALREADY SUBMITTED (Andy's call, same night): "MDS Mille" is `PENDING_REVIEW`.**
   When it approves there are **14 days to re-register** (same `POST /register` + Andy's PIN) or the
   approval lapses and must be resubmitted. Check `new_name_status` at session start:
   `GET /1306956855827812?fields=verified_name,name_status,new_display_name,new_name_status`.
   **Watcher live:** n8n `a1ViYr5FT7iePdN9` (hourly, TEMPORARY) — WhatsApps Andy's test number on
   APPROVED/DECLINED, nags hourly until re-registered, silent while pending. Limit: free-form send
   needs Andy's 24h window on …8153 open. **DELETE the watcher once Mille is live.** When the name
   flips, queue Andy's rewording pass on the intro/self-references (#79 curated copy says "the MDS
   AI assistant").
3. **Multi-event note (Andy 2026-08-19: "we will have more" schedules):** the event schema and all
   lanes are already multi-event (everything keys on `event_id`; the loader loads any export
   alongside). ONE decision waits for event #2: the lane's no-event-named default is
   latest-starting — switch to nearest-upcoming or asker's-registration when a second event loads.
   Nothing to build until then. Reminders stay schedule-anchored BY DESIGN (her refusal of
   freestanding "remind me to check fb" is correct behavior); freestanding reminders = a new
   ticket if Andy ever wants them.
4. **Ask the dev for a fresh export** — CÉ LA VI is in the admin's 19 locations but not our 18, so
   some of the 13 venue-less activities may be export gaps. Same dump un-truncates long descriptions.

### Two things NO probe can verify — test on a phone
`Eval (silent)?` routes SELFTEST traffic to `Save Conversation` and never reaches `Send Reply (Meta)`,
and both the image and reminder-delivery branches hang off that send. So:
- **images** — "show me the Summit theme post Eugene shared" must be tried on a real phone
- **reminder delivery** — likewise, once the sender is scheduled

### The demo set (nine questions, verified on prod)
Broad reading recs · full day one · which sessions suit me · who speaks Monday · where is X + map ·
show me the theme post (image) · weekly digest (summaries) · remind me (set/list/cancel) · who should
I meet (#87). Buttons need a complaint she has **not** already handled — she will not re-offer.

### The lesson this session kept teaching
**Code beats instructions.** Three prompt rules failed on images, four on reminder timing. Both were
fixed in one commit each once the work moved into the tool. And **read the execution before
theorising** — it settled in one call what rule-writing chased for rounds, twice.

### Open tickets, awaiting priority
- ~~#90~~ **CLOSED 2026-08-18: the sync never existed** (one-time xlsx load 2026-07-29, nothing ever
  wrote the table again). Now: n8n **`RpEbU47SpMVsbwqg`** hourly mirror (sibling of Members/
  Summaries), AT `{active}=1` = 18 chats, **diff 0** field-by-field, ghost row deleted, heartbeat
  `chats_mirror` (3h) under signal 4. Curated columns untouched. **Andy ruling queued:** Accelerator
  + 2026 New Members carry `required_form` in AT but are ungated in the mirror.
- ~~#89~~ **CLOSED 2026-08-18: the gap was IDENTITY, not attendance.** Zero digest fns read
  `event.attendees` (counts were single-sourced all along — now stamped as table comments,
  migration `event_roster_authority_comments_20260818`). Loader matching rebuilt (3-rung ladder):
  people matched 124→**170 of 199**, Courtney freed from a "Test Test" record. **Andy's list on the
  board:** 4 speaker roster rows linked to Max Mikhaylenko's record · dup member pairs (Brian,
  Henrik, Rebeca, Ryan, Eugene ×9) · the 151-vs-108 filter ruling. Fresh export covers the last 6
  absentees + late orders.
- **#88** 🟡 partner profiles — event-specific and type-specific; `event.attendee_profiles` designed,
  not built. Passcode never enters the warehouse.
- **#86** 🔴 sender now scheduled (n8n `QhJw46Mr7LAP8fdz`) — open only for the arrival proof on a
  real phone (Aug 23 test reminder, or an ad-hoc "remind me in 5 min").

**Closed today:** #85 (schedule lane) and #87 (who to meet — 4 of 8 not attending → **7 of 7**).
Both keep their evidence in `OLIVIA_SPRINT_3.md`; they move to `OLIVIA_BACKLOG_ARCHIVE.md` at
SPRINT close, not session close.

### Known and deliberately left
- Brandon Himmel's Aug 26 session has no parent activity → no audience → invisible to everyone.
- 5 of the 20 probe questions unfired: 13, 14, 15, 17, 18.
- `test-andy-8153` is a test row in `event.people` — remove when done testing.
- #72 load test still shelved (design only, nothing built).

### Traps in the export, all handled by the loader — do not re-learn them
- **41 of 91 activities are Milan 2025 leftovers** carrying `isDelete`. The event was cloned.
- **The `member`/`speaker`/`partner`/`guest` booleans are stale** and all false on records whose
  `accessRoles` grants three roles. `accessRoles` governs.
- **`event.timeZone` is a display label**, not IANA. Times are local wall-clock with no offset —
  which is exactly how `events_catalog.start_at` ended up 8 hours wrong.

## Watch-outs (standing)
- **NEVER fire probes at PROD against a real member's number.** On 2026-08-04 prod probes ran
  into Andy's own thread mid-test and twice sent "new question", resetting his context and
  stealing a button tap. Staging only, or a dedicated test number.
- **A 200 from Meta's `/messages` is NOT delivery.** The truth arrives asynchronously on the
  status webhook — read `digest.olivia_sends` before claiming reach (17 of 25 broadcast
  messages failed with 131049 *after* the API accepted every one).
- ~~`olivia_selftest.py` paces by sleep(20)~~ **FIXED 2026-08-03 (#52):** it now polls
  `olivia_messages` for THIS turn's reply before firing the next (`--timeout`, default 180s) and
  prints the wait — a probe in the #52 set took **50.4s** and would have raced the old pacer.
  Real-member echo: two messages <2s apart hit the same race in the workflow itself — known,
  low-frequency, still just a note.
- **FB capture SOP: rewrite `extension/seed_ids.json` from the capture file EVERY run** — 4c
  falls back to it silently (localStorage dies on tab close); a stale seed = comments for the
  wrong days. Backup pattern: `.bak-<date>`.
- Eval wamids `SELFTEST_MANU*` are not cleaned by `--cleanup`; Andy's thread carries test turns
  (accepted). Seed edits get a node syntax check BEFORE build_loop (apostrophes, twice).

## The daily routine (unchanged)
- Runs: FULL (all bank) rare; TEST = 25–35 targeted; `OLIVIA_EVAL_BANK=eval_bank_organic.json`
  or it fires 0. ONE paid run per session, after free diagnosis + probes. Retirement: 3 passes.
- Runs pace per-reply — the quiet stretches are NOT a stall; never kill the run.
- Reset between probes; gate GREEN before anything ships; Andy's number excluded from reporting.

## Open with Andy
- Q3088 MDS-Life ruling (parked) · whale ruling (chapter TTM sums) · "Oliva" display name ·
  member_match 'Apparel' vs 'Clothing & Accessories' · 👎 reactions → Slack? · bank truth fixes
  (722→723 members; supplements count drifts) · ClickUp doc refresh pending.


### #161 MDS Personas — STATE 2026-09-04 evening (SHIPPED to production) <!-- #161 -->
- LIVE at `digest.mds.co/personas`, linked in the admin nav (staff `@mds.co` session required; Render `559b0ff`). Both repos merged to `main` 2026-09-04 evening; Render deploy `e212bcf`. The nightly jobs `cache_member_photos` and `persona_blurbs` run from `main` now.
- To run locally: preview config `digest-web` (Scorecard `.claude/launch.json`); staff cookie `node --env-file=.env.local scripts/dev-session-cookie.mjs` in mds-digest-web; screenshots via the scratchpad `shot.mjs` pattern (playwright-core from mds-fb-group-members + chrome-headless-shell 1234). A stale Turbopack cache once produced `require is not defined` on `/personas/[id]` — restart the dev server before believing a 500.
- Data: view `personas_stats` + RPCs `personas_library/sheet/cohort/related/strong/fading/topic_peaks` (service_role only, exported to `db/`) · `member_photos` + Storage `member-photos` (nightly job; 121 members have no source; FB capture = own ticket) · `persona.blurb` (nightly Haiku job) · gate 323/0 with 10 personas checks.
- Andy's UI rules (override the design READMEs): all categories collapsed by default · compact legend + "?" popover · stats fonts +20% · aside scrolls independently, scrollbar hidden · "MDS member since YYYY" on sheet/cards/hover · rails: hidden scrollbars, arrows on hover · hero 10 swipeable banners · one number per stat card, badge tooltips · every number truthful.
- **NEXT SESSION STARTS HERE: `docs/superpowers/plans/2026-09-05-expertise-truth-set.md`** (#163 phase 1 — build the ruler before tuning: proxy truth, the 101-member web test with a control group, the measurement table; formula changes only after the go/no-go). Analysis and simulation results are in `OLIVIA_SPRINT_4.md` §#163.
- Open: #163 scoring review (filed, after #161) · FB profile-photo capture · GroupOS roster sweep for avatars (72 today) · `SkeletonCohortCard` dead code · Chromium-only verification.
- Ledger + briefs + reports + screenshots: `.superpowers/sdd/2026-09-04-mds-personas/` (git-ignored, on disk).
- Deferred minors: companions match category-level asks only (detail-stat asks never surface); personas_cohort recomputes personas_library per call; focus weight cast unguarded.
