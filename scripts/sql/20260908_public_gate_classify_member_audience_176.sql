-- scripts/sql/20260908_public_gate_classify_member_audience_176.sql  (#176)
--
-- WHO A PUBLIC ANSWER IS FOR, AND WHAT THE GATE IS ACTUALLY HIDING.
--
-- Andy, 2026-09-07 (after comparing a gated draft against the answer Millie gives members on
-- WhatsApp):
--
--     "you do realise that Public means MDS members ... the only restiriction for public mode
--      is opt in sources"
--
-- and then, decisively:
--
--     "the whole idea behind public is that we hiding exact details from restictat chats"
--
-- WHAT THE OLD DEFINITION GOT WRONG. #169 fix round 3
-- (20260908_public_gate_classify_world_public_169.sql) read "Public mode" as "safe to leave MDS"
-- and therefore as WORLD-public: a person could be named only when a source the open internet can
-- already see backed the name, so everything else — the MDS Facebook group's posts and comments
-- included — was classified `closed`, names became role phrases and links were stripped.
--
-- That was the wrong audience. A Public answer is posted into the members-only MDS Facebook group:
-- its readers ARE the MDS membership. Gating it to what the world can see hid, from members,
-- material those same members can already scroll to themselves — and produced answers visibly
-- worse than the ones Millie gives the same people on WhatsApp. Two tells that the world-public
-- reading never actually cohered:
--   * partner listings classified `public` while their url is `https://app.mds.co/partners/<id>`
--     — a members'-app link. World-public and app-only at the same time.
--   * `content_items.access_rule->>'type' = 'public'` was dismissed as "member-visible, not
--     world-visible". Member-visible is exactly the test the correct rule wants; fix round 3 threw
--     away the right column for the wrong reason.
--
-- THE RULE THIS FUNCTION NOW IMPLEMENTS — two buckets, by ROOM, not by reach:
--
--   OPEN (`public`)     — anything a member can already see for themselves: the MDS Facebook
--                         group's posts and comments, partner listings and their pages, events and
--                         their pages, and the app's own library pages/links. May be named, quoted
--                         and linked freely.
--   RESTRICTED (`closed`) — what was said in a closed room: closed WhatsApp channel messages and
--                         private call/meeting transcripts. These may still INFORM an answer, but
--                         no exact detail crosses into it: no names, no verbatim quotes, no
--                         identifying specifics. Paraphrase only, said so in the notes.
--
-- A source that cannot be classified stays restricted. Unknown is still closed — that part of #169
-- does not change, and neither does the two-value `public` / `closed` contract this returns.
--
-- WHAT THE COLUMNS ACTUALLY HOLD (verified read-only against the live database, 2026-09-08, before
-- deciding any row's bucket — the counts below are that census):
--
--   content_items.source / access_rule->>'type' / sensitivity
--     fb_comment    16,286   'public'                       all sensitivity 'normal'
--     fb_post        4,241   'public'                       all sensitivity 'normal'
--     wa_message    17,019   'chat_member'                  all 'normal'   <- the closed rooms
--     wa_digest      1,344   'chat_member'                  all 'normal'   <- rollups of the same
--     call_transcript 8,022  'public' / 5,485 'video_access'  8,022 'normal', 5,485 'restricted'
--     application    6,530   'owner'                        1 row 'never_surface'
--   `source` is the column that carries 'fb_post'/'fb_comment'/'wa_message'/'call_transcript';
--   `kind` holds 'post'/'comment'/'text'/'chunk' and is NOT the discriminator to key on.
--   Note call_transcript rows carry access_rule 'public' too — which is why the SOURCE allowlist is
--   the primary gate here and access_rule/sensitivity are only secondary fail-closed guards on top.
--   A private call stays closed no matter how member-visible its recording is inside the app.
--
--   videos_catalog.access_restriction: 655 'public', 429 'restricted'. The restricted set is
--   overwhelmingly Mastermind (127), Chapter Event (82), Summit (77) and Coaching Call (4) — a
--   cohort's or a chapter's recording, NOT something any member can open. So the app's video
--   library is open at `access_restriction = 'public'` and a restricted recording stays closed:
--   it is materially the same thing as a private call. (Fix round 3 closed ALL videos; that goes.)
--
--   events_catalog: all 1,449 rows carry a public_page_url, 19 also carry an app_url. Both columns
--   are now `public` — an event's members'-app page is a page a member can already open, so fix
--   round 3's "an app flag is not world-public" no longer decides anything.
--
-- Everything else about the gate is unchanged: the module still masks any name no OPEN row of the
-- turn backs, still strips every link this function did not call `public`, and Public Verify still
-- refuses a turn where a closed-room name or link survived the smoother.
create or replace function digest.public_gate_classify(p_urls text[], p_source_ids text[])
returns table(key text, klass text, source text)
language sql stable security definer set search_path = digest, pg_temp as $$
  -- content rows, by url then by source_id. OPEN is the MDS Facebook group — posts and comments a
  -- member can scroll to in the group this answer gets posted into. CLOSED is every other source:
  -- wa_message / wa_digest (a closed WhatsApp channel), call_transcript (a private call or meeting),
  -- application (a member's own submission, never anyone else's to read), and anything new that
  -- lands in this table without being added to the allowlist above — unknown stays closed.
  -- access_rule / sensitivity ride along as secondary guards so a group post an admin later marks
  -- restricted or never_surface drops out of the open bucket without this function being touched.
  select c.url as key,
         case when c.source in ('fb_post', 'fb_comment')
                   and c.access_rule->>'type' = 'public'
                   and coalesce(c.sensitivity, 'normal') = 'normal'
              then 'public' else 'closed' end,
         'content:' || c.source
  from digest.content_items c where c.url = any(coalesce(p_urls, '{}'))
  union all
  select c.source_id,
         case when c.source in ('fb_post', 'fb_comment')
                   and c.access_rule->>'type' = 'public'
                   and coalesce(c.sensitivity, 'normal') = 'normal'
              then 'public' else 'closed' end,
         'content:' || c.source
  from digest.content_items c where c.source_id = any(coalesce(p_source_ids, '{}'))
  union all
  -- partners: a published listing and its page are open to every member.
  -- #169 (verified 2026-09-07): partners_catalog has no partner_url column (only logo_url, an image).
  -- partner_lookup_v2 / partner_lookup both derive their `partner_url` output via
  -- digest.member_partner_url(partner_id), so we build the same key here rather than inventing a column.
  select digest.member_partner_url(p.partner_id), 'public', 'partner' from digest.partners_catalog p
  where p.status = 'published' and digest.member_partner_url(p.partner_id) = any(coalesce(p_urls, '{}'))
  union all
  -- events, by public page url.
  select e.public_page_url, 'public', 'event'
  from digest.events_catalog e
  where e.public_page_url = any(coalesce(p_urls, '{}'))
  union all
  -- events, by app url: the SAME event keyed by the other column — this is the branch event_lookup*
  -- output actually lands on (#169 fix round 2, kept). Now equally open: an event's page in the
  -- members' app is a page a member can already open.
  select e.app_url, 'public', 'event'
  from digest.events_catalog e
  where e.app_url = any(coalesce(p_urls, '{}'))
  union all
  -- videos, by id: the app's own library. Open when access_restriction says every member can watch
  -- it; a 'restricted' recording (mastermind / chapter / coaching cohort) is a closed room and
  -- stays closed.
  select v.video_id::text,
         case when v.access_restriction = 'public' then 'public' else 'closed' end, 'video'
  from digest.videos_catalog v where v.video_id::text = any(coalesce(p_source_ids, '{}'))
  union all
  -- videos, by app link: the SAME library entry keyed by the url an answer would actually print, so
  -- an open library link survives the module's link pass instead of being stripped as unclassified.
  -- The id is pulled out of the url with the same shape public_gate.js's VIDEO_LINK_RE matches, so
  -- a trailing slash or a query string cannot hide it.
  --
  -- DELIBERATE COLLISION, and it fails closed: a call_transcript content row's OWN url is this same
  -- `app.mds.co/videos/<id>` link (verified live — 13,507 transcript rows, all of them). When a turn
  -- cites a transcript chunk, the content branch above emits `closed` for that url and this branch
  -- emits `public`; `Public Redact` collapses duplicate keys most-restrictively, so the key lands
  -- `closed` — the transcript row cannot back a name and the link is stripped. Cite the library
  -- entry WITHOUT a transcript chunk and only this row exists, so the link survives. A private call
  -- never rides in on its own recording's page.
  select u.url,
         case when v.access_restriction = 'public' then 'public' else 'closed' end, 'video'
  from (select t.url, substring(t.url from 'app\.mds\.co/videos/([0-9a-f]{24})') as vid
        from unnest(coalesce(p_urls, '{}')) as t(url)) u
  join digest.videos_catalog v on v.video_id::text = u.vid
  where u.vid is not null;
$$;
revoke all on function digest.public_gate_classify(text[], text[]) from public, anon, authenticated;
grant execute on function digest.public_gate_classify(text[], text[]) to service_role;
