-- scripts/sql/20260908_public_gate_classify_restriction_spine_176.sql  (#176, correction 2)
--
-- THE RESTRICTION SPINE IS THE RULE. NOT THE SOURCE TYPE.
--
-- Andy, 2026-09-08, correcting the classifier applied earlier the same day
-- (20260908_public_gate_classify_member_audience_176.sql):
--
--     "public means all members, but not people outside the MDS; restricted means this content is
--      restricted to some members. Facebook is open source; it's public by definition. The only
--      restricted sources are some WA chats (you should know it) and some videos (we have the spine
--      with restriction rules)."
--
-- WHAT THE PREVIOUS BODY GOT WRONG. Correction 1 fixed the AUDIENCE — it stopped treating "public"
-- as world-public and opened the Facebook group, partner listings and events. But it kept #169's
-- shape for everything else: a SOURCE-TYPE allowlist. `fb_post`/`fb_comment` were open and every
-- other content source was closed WHOLESALE — all 18,363 WhatsApp rows and all 13,507 call
-- transcript rows, whatever room they came from. That is not the rule. The database already carries
-- a per-row restriction spine, and the spine — not the source type — is what says which room a row
-- was said in:
--
--   * digest.chats.verification_required. Five chats are true (MDS Centurion 20M+, MDS Large SKU,
--     MDS Real Estate, MDS Supplements, MDS TikTok), twelve are false (Accelerator, AI & Automations,
--     Credit Card & Travel Hacks, DTC/Shopify, Logistics, Mergers & Acquisitions, Mogul Call
--     announcements, Resellers, Retail, SEO & Listing Optimization, Trading, Under 30) and one —
--     MDS 2026 New Members — is NULL. A WhatsApp content row joins that spine through
--     access_rule->>'chat': every one of the 18,363 rows carries a chat name that matches a
--     digest.chats row exactly (verified read-only, 2026-09-08, zero misses). So closing all of them
--     hid twelve OPEN chats — the great majority of the corpus — from the members those chats
--     belong to.
--   * digest.videos_catalog.access_restriction: 655 'public', 429 'restricted', none NULL. A call
--     transcript is a CUT OF A RECORDING, so it inherits the recording's restriction; closing every
--     transcript closed 8,022 chunks of recordings any member can already open in the app.
--
-- HOW A TRANSCRIPT FINDS ITS RECORDING. Both keys were measured before this was written:
--     url       'https://app.mds.co/videos/<24 hex>'   13,507 of 13,507 rows  <- reliable
--     source_id '<24 hex>#<chunk>'                     10,303 of 13,507 rows
-- The other 3,204 source_ids are a base64 call id instead ('37yVhe+qTbaVUssWHoYOsQ==#41'), so the
-- URL is the join key here, taken from the row itself in both arms of the union — never from
-- whichever key the caller happened to ask by.
--
-- THE RULE THIS FUNCTION IMPLEMENTS — two buckets, decided per row by the spine:
--
--   OPEN (`public`)      — open to every member, therefore quotable, nameable and linkable:
--                          Facebook group posts and comments (Facebook is open source, public by
--                          definition) · WhatsApp messages and digests whose chat is NOT
--                          verification_required · call transcripts and videos whose recording is
--                          access_restriction = 'public' · published partner listings and their
--                          pages · events and their pages.
--   RESTRICTED (`closed`) — restricted to SOME members, so it may inform an answer but no exact
--                          detail crosses over: WhatsApp in a verification_required chat ·
--                          transcripts and videos of a 'restricted' recording · applications ·
--                          anything unclassifiable.
--
-- UNKNOWN IS STILL CLOSED, and that is load-bearing in three specific places:
--   * a chat whose verification_required is NULL (MDS 2026 New Members) — `= false` leaves NULL
--     unmatched and the CASE falls through to 'closed'. Written as `= false` rather than
--     `is not true` on purpose: `is not true` would OPEN the NULL chat.
--   * a WhatsApp row whose access_rule->>'chat' is not in digest.chats at all — the LEFT JOIN gives
--     a NULL row and it closes the same way. None exist today; the rule is what matters.
--   * a transcript whose recording is not in videos_catalog (3,204 rows have no such row) — no
--     access_restriction, so 'closed'.
--
-- SECONDARY GUARD, AND THE 401 ROWS THAT NEED IT. `sensitivity` still rides along on every content
-- row, so an admin marking a row 'restricted' or 'never_surface' drops it out of the open bucket
-- without this function being touched. It is not decoration: the two spines DISAGREE on 401
-- transcript rows (250 where the recording is 'public' but the row is sensitivity 'restricted', 151
-- the other way round). Taking the MORE restrictive of the two is the only reading that cannot leak,
-- and it lands transcripts at exactly 8,022 open / 5,485 closed.
--
-- WHAT THE `source` COLUMN NOW SAYS. It is informative on purpose — the leak gate asserts on it —
-- and it names the reason, not just the table: wa:open · wa:verified · wa:unknown (NULL flag) ·
-- wa:unknown-chat · transcript:public · transcript:restricted · transcript:unknown ·
-- video:public · video:restricted · content:fb_post · content:fb_comment · content:application ·
-- partner · event.
--
-- The signature is byte-identical to the applied version — (p_urls text[], p_source_ids text[])
-- returns table(key text, klass text, source text) — because a return-type change makes
-- `create or replace` fail. The two-value 'public'/'closed' contract is unchanged, and so is
-- everything downstream: the module masks any name no OPEN row of the turn backs, strips every link
-- this function did not call 'public', and Public Verify re-checks both.
create or replace function digest.public_gate_classify(p_urls text[], p_source_ids text[])
returns table(key text, klass text, source text)
language sql stable security definer set search_path = digest, pg_temp as $$
  with content_hits as (
    -- two index-friendly scans rather than one `url = any(...) or source_id = any(...)`, which
    -- would lose both indexes. The row's OWN url travels with it so a transcript matched by
    -- source_id still finds its recording.
    select c.url as k, c.source, c.access_rule, c.sensitivity, c.url as row_url
      from digest.content_items c where c.url = any(coalesce(p_urls, '{}'))
    union all
    select c.source_id, c.source, c.access_rule, c.sensitivity, c.url
      from digest.content_items c where c.source_id = any(coalesce(p_source_ids, '{}'))
  ),
  content_class as (
    select h.k,
           case
             -- FACEBOOK. The group is this answer's audience and the group is open source.
             when h.source in ('fb_post', 'fb_comment')
                  and h.access_rule->>'type' = 'public'
                  and coalesce(h.sensitivity, 'normal') = 'normal'
               then 'public'
             -- WHATSAPP. Open unless the chat itself is gated. `= false` so NULL (unknown) closes.
             when h.source in ('wa_message', 'wa_digest')
                  and ch.verification_required = false
                  and coalesce(h.sensitivity, 'normal') = 'normal'
               then 'public'
             -- CALL TRANSCRIPT. Inherits the recording it was cut from; no recording = closed.
             when h.source = 'call_transcript'
                  and v.access_restriction = 'public'
                  and coalesce(h.sensitivity, 'normal') = 'normal'
               then 'public'
             -- applications, and anything new that lands in this table: closed.
             else 'closed'
           end as klass,
           case
             when h.source in ('wa_message', 'wa_digest')
               then 'wa:' || case when ch.chat_name is null then 'unknown-chat'
                                  when ch.verification_required is null then 'unknown'
                                  when ch.verification_required then 'verified'
                                  else 'open' end
             when h.source = 'call_transcript'
               then 'transcript:' || coalesce(v.access_restriction, 'unknown')
             else 'content:' || h.source
           end as src
      from content_hits h
      left join digest.chats ch on ch.chat_name = h.access_rule->>'chat'
      left join digest.videos_catalog v
             on v.video_id::text = substring(h.row_url from 'app\.mds\.co/videos/([0-9a-f]{24})')
  )
  select k, klass, src from content_class
  union all
  -- partners: a published listing and its page are open to every member. All 509 published rows
  -- carry access_restriction 'public' and access_detail NULL (verified 2026-09-08), so the guard
  -- costs nothing today and closes the row the day one of them is restricted.
  -- #169 (verified 2026-09-07): partners_catalog has no partner_url column (only logo_url, an image).
  -- partner_lookup_v2 / partner_lookup both derive their `partner_url` output via
  -- digest.member_partner_url(partner_id), so we build the same key here rather than inventing a column.
  select digest.member_partner_url(p.partner_id), 'public', 'partner' from digest.partners_catalog p
  where p.status = 'published' and p.access_restriction = 'public'
    and digest.member_partner_url(p.partner_id) = any(coalesce(p_urls, '{}'))
  union all
  -- events, by public page url. events_catalog carries no restriction column of any kind: an event
  -- and its page are open to every member.
  select e.public_page_url, 'public', 'event'
  from digest.events_catalog e
  where e.public_page_url = any(coalesce(p_urls, '{}'))
  union all
  -- events, by app url: the SAME event keyed by the other column — this is the branch event_lookup*
  -- output actually lands on (#169 fix round 2, kept).
  select e.app_url, 'public', 'event'
  from digest.events_catalog e
  where e.app_url = any(coalesce(p_urls, '{}'))
  union all
  -- videos, by id: the library entry itself, straight off the spine.
  select v.video_id::text,
         case when v.access_restriction = 'public' then 'public' else 'closed' end,
         'video:' || coalesce(v.access_restriction, 'unknown')
  from digest.videos_catalog v where v.video_id::text = any(coalesce(p_source_ids, '{}'))
  union all
  -- videos, by app link: the SAME library entry keyed by the url an answer would actually print, so
  -- an open library link survives the module's link pass instead of being stripped as unclassified.
  -- The id is pulled out of the url with the same shape public_gate.js's VIDEO_LINK_RE matches, so
  -- a trailing slash or a query string cannot hide it.
  --
  -- The old body called this branch a "DELIBERATE COLLISION that fails closed": a transcript's own
  -- url is this same link, so the content arm said 'closed' and this arm said 'public', and `Public
  -- Redact` collapsed the key to 'closed'. The collision is still here and still collapses the same
  -- way, but the two arms now AGREE — both read the same videos_catalog row — so a public
  -- recording's link survives and a restricted one's does not, whether the turn cites the library
  -- entry, a transcript chunk, or both.
  select u.url,
         case when v.access_restriction = 'public' then 'public' else 'closed' end,
         'video:' || coalesce(v.access_restriction, 'unknown')
  from (select t.url, substring(t.url from 'app\.mds\.co/videos/([0-9a-f]{24})') as vid
        from unnest(coalesce(p_urls, '{}')) as t(url)) u
  join digest.videos_catalog v on v.video_id::text = u.vid
  where u.vid is not null;
$$;
revoke all on function digest.public_gate_classify(text[], text[]) from public, anon, authenticated;
grant execute on function digest.public_gate_classify(text[], text[]) to service_role;
