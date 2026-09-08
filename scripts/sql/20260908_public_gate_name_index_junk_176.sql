-- scripts/sql/20260908_public_gate_name_index_junk_176.sql  (#176)
--
-- THE NAME INDEX IS A LIST OF PEOPLE. PLACEHOLDER ROWS ARE NOT PEOPLE.
--
-- #169 fix round 5 (20260908_public_gate_name_index_orgs_169.sql) took the ORGANISATION rows out of
-- this index because their tokens were mangling ordinary copy — "the MDS community is generous"
-- publishing as "the a member is generous". The same defect has a second population, and it is
-- worse, because it fires on ONE token: the first-name pass in public_gate.js masks the lone first
-- token of any unbacked index name that is >= 4 characters. When that token is an ordinary English
-- word, ordinary sentences come out broken. Proven on the 2026-09-08 staging probes:
--
--     index row "first last"            -> "you're not the they to get one of these letters"
--     index row "Your Mom Strueby"      -> "Great question, they" ("Your" is 4 characters)
--     index row "Mayank Yadav 23frqw2e4" -> "they Sharma of Returnstack" (over Mayank Sharma)
--     index row "andy test"             -> masks the plain word "Andy"
--
-- public_gate.js already carries COMMON_WORD_FIRST_NAMES for the real members whose first name IS an
-- English word (Grace, Hope, Faith, Will). That list is the right tool for a real person; it is the
-- wrong tool here, because these rows are not people at all. The fix belongs where the org rows'
-- fix went — in the index — and nowhere else, so there is nothing to keep in sync module-side.
--
-- THE PREDICATE, not a blocklist. Three properties, each of which disqualifies a row from being a
-- person's display name (measured against the live index, 2026-09-08 — 5,384 rows before):
--
--   1. IT CARRIES A DIGIT. A display name is letters. A digit means a phone number, an address, a
--      record id or a duplicate-account suffix has been typed into the name field:
--      "Lindsay Brown917-739-9161", "Alex Delgado. po. box. 3791. calexico. ca.92232",
--      "Andries Du Plessis2", "TL 102", "+8 +8".
--   2. IT CARRIES AN '@'. Same cause, an email address glued to (or instead of) a name:
--      "guest@gmail.com last", "Tynita Yarbroughvovob40785@exahut.com".
--   3. IT HAS A WHOLE TOKEN 'test' / 'testing', or its FIRST token is an English FUNCTION WORD.
--      Function words are a closed class — determiners, pronouns, prepositions, conjunctions,
--      wh-words, quantifiers — and no member of that class is a given name in any language this
--      index carries. That is what makes it a predicate rather than a list of the junk rows we
--      happen to have seen: "first last", "Your Mom Strueby", "The LLC", "You You", "To be Deleted",
--      "any asfdfsd" all fall out of the same rule, and so will the next one typed.
--
--      The word set is deliberately CONSERVATIVE, and it was pruned against the live index rather
--      than written from intuition: 'will', 'said', 'do', 'may', 'new', 'than', 'has', 'been' were
--      all dropped from a first draft the moment it removed Will Butera, Will Ford, Will Haire,
--      Said Butoyi and Do Nguyen — real members every one. A junk row left in over-masks a word; a
--      real member dropped out UNDER-masks a person, which is the failure this gate exists to
--      prevent. When in doubt the row stays.
--
-- WHAT THIS COSTS, stated plainly. 64 rows go, 5,384 -> 5,320. Eight of them are a real person's
-- name with a phone number, an email or a duplicate suffix glued on — Lindsay Brown917-739-9161,
-- Kyle Shaw215-375-3645pexaki8309@izkat.com, Tynita Yarbroughvovob40785@exahut.com,
-- Alex Delgado. po. box. ..., Andries Du Plessis2, John Barrett2, Bro Sina11,
-- Mayank Yadav 23frqw2e4 — and for those eight the LONE-FIRST-NAME pass stops firing. Their FULL
-- name was never masked anyway and cannot be: nameTokens() splits the glued junk into the pattern
-- ("Lindsay" + "Brown917" + "739" + "9161"), which no prose can match. So the loss is one token of
-- masking for eight people, six of whose first names (Alex, John, Kyle, Lindsay, Mayank, Michael)
-- are carried by other, clean index rows regardless. Weighed against 56 placeholder rows breaking
-- published sentences, that is the trade this takes.
create or replace function digest.public_gate_name_index()
returns table(name text, kind text)
language sql stable security definer set search_path = digest, pg_temp as $$
  select distinct trim(n) as name, k as kind from (
    select full_name as n, 'member' as k from digest.members            where full_name is not null
    union all
    select full_name,       'member'      from digest.member_attributes where full_name is not null
    union all
    select display_name,    'speaker'     from digest.speakers          where display_name is not null and kind = 'member'
  ) x
  where length(trim(n)) >= 5 and position(' ' in trim(n)) > 0   -- two-word names only; single words over-match
    and trim(n) not ilike 'MDS %'    -- org rows: MDS Community / Partners / Programs / Member / Chapters / Test
    and trim(n) not ilike '% MDS'    -- org rows: Systems MDS / Andy MDS
    -- #176, three properties that disqualify a row from being a person's name (see header):
    and trim(n) !~ '[0-9]'           -- a phone number, address, record id or duplicate suffix, not a name
    and trim(n) not like '%@%'       -- an email glued to (or instead of) a name
    and lower(trim(n)) !~ '(^|[^[:alpha:]])test(ing)?([^[:alpha:]]|$)'  -- placeholder/test accounts
    and lower(split_part(trim(n), ' ', 1)) <> all (array[               -- function-word first token
      'a','an','the','this','that','these','those','my','your','his','her','its','our','their',
      'they','them','we','you','and','but','because','from','with','without','into','onto','about',
      'over','under','for','of','to','in','on','at','as','not','none','null','unknown','undefined',
      'test','testing','first','last','next','other','another','some','any','all','both','each',
      'every','more','most','much','many','very','just','only','also','here','there','when','where',
      'what','which','who','whom','whose','how','why','same','such','etc']);
$$;
revoke all on function digest.public_gate_name_index() from public, anon, authenticated;
grant execute on function digest.public_gate_name_index() to service_role;
