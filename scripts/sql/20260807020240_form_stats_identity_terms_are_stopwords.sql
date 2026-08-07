-- Applied to Supabase (digest schema) 2026-08-07 as migration
--   20260807020240_form_stats_identity_terms_are_stopwords
-- Kept in git because the SQL layer otherwise lives only in the live DB (ticket #65).
--
-- #20 fix ① follow-through: composed matrix labels put the word "Email" into a legitimate
-- topic ("How do you handle each marketing channel? (SMS/Email Marketing)"), so an ask like
-- "what's Sherman's email" started matching a marketing statistic. No PII is exposed — the
-- values are choice labels — but the answer is nonsense, and the QA sweep's R12 caught it.
-- Identity words become query-side stop-words: an ask for a contact detail matches nothing
-- and Olivia says she does not hold it, while "who handles email marketing" still resolves
-- on "handles"/"marketing".
--
-- Rewritten FROM the live definition rather than retyped, so the stop-word list is provably
-- the only thing that changed.

do $mig$
declare d text;
begin
  d := pg_get_functiondef('digest.form_stats(text,text,text,text,date,date)'::regprocedure);
  if position('''their'',''there'')' in d) = 0 then
    raise exception 'stop-word anchor not found — form_stats changed shape, migration aborted';
  end if;
  d := replace(d,
    '''their'',''there'')',
    '''their'',''there'',''email'',''emails'',''address'',''addresses'',''phone'',''phones'',''name'',''names'')');
  execute d;
end
$mig$;

notify pgrst, 'reload schema';
