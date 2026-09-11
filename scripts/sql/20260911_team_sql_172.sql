-- scripts/sql/20260911_team_sql_172.sql  (#172 Team research mode — the read-only SQL surface)
--
-- Andy 2026-09-10: staff get answers to ANY question over the warehouse, no member gates, Supabase only.
-- That needs a query tool nobody wrote in advance. Its safety lives HERE, in a role and a function, never
-- in a prompt: a NOLOGIN read-only role, a SECURITY DEFINER runner OWNED by that role that forces a
-- read-only transaction, a deny-list view over member_profiles so the items #172 never opened
-- (removal reasons, LTV, internal notes, lead scoring) cannot be selected, and no privilege at all on
-- olivia_web_messages (other askers' Team answers) or the two OTP hash columns.
--
-- Idempotent. CREATE OR REPLACE only (DROP discards the ACL). Live on prod the moment it is applied.
-- Re-export db/ afterwards: python3 scripts/db_export_schema.py
-- Proof: python3 scripts/test_172_team_sql.py  (live checks through PostgREST, exit code is the verdict)

-- 1. the role. BYPASSRLS because 33 digest tables have RLS ON with ZERO policies: a non-bypass role would
--    read zero rows silently, and a timeout/empty result looks exactly like "no data". Live 2026-09-10:
--    PG 17.6, postgres holds CREATEROLE + BYPASSRLS (not superuser), createrole_self_grant is empty, so the
--    creator gets ADMIN OPTION only and the SET membership below is explicit.
--    If this statement is refused, apply 20260911_team_sql_172_policies_fallback.sql instead of it.
do $do$
begin
  if not exists (select 1 from pg_roles where rolname = 'millie_team_ro') then
    create role millie_team_ro nologin bypassrls;
  end if;
end $do$;

-- postgres must be able to SET ROLE to the new owner to hand it the function (PG16+ ownership rule).
grant millie_team_ro to postgres with set true;

grant usage on schema digest, event, extensions to millie_team_ro;

-- 2. what the role may read: everything in digest + event (tables, views, materialized views) ...
grant select on all tables in schema digest to millie_team_ro;
grant select on all tables in schema event to millie_team_ro;
-- ... except: other askers' Team answers, the raw member_profiles table (the view below is the door),
--     the two OTP hash columns on members and the session token hash on member_sessions (column-list
--     grants generated from the live column sets, so a column added later is readable by default and
--     a dark column stays dark by name).
revoke all on digest.olivia_web_messages from millie_team_ro;
revoke all on digest.member_profiles from millie_team_ro;
revoke all on digest.members from millie_team_ro;
revoke all on digest.member_sessions from millie_team_ro;
do $do$
declare r record; cols text;
begin
  for r in
    select * from (values ('members', array['otp_code_hash', 'delivery_otp_hash']),
                          ('member_sessions', array['token_hash'])) as t(tbl, dark)
  loop
    select string_agg(quote_ident(column_name), ', ' order by ordinal_position) into cols
    from information_schema.columns
    where table_schema = 'digest' and table_name = r.tbl and column_name <> all (r.dark);
    execute format('grant select (%s) on digest.%I to millie_team_ro', cols, r.tbl);
  end loop;
end $do$;

-- 2b. views run as their owner for TABLE access, but a function called inside a view runs as the CALLER:
--     digest.member_identity and digest.member_phones call is_active_member_status(text), a pure IMMUTABLE
--     status test, so the role needs EXECUTE on it or the identity bridge dies with 42501 (found by the
--     Milestone B proof, applied as team_sql_172b_view_helper_20260910). This is the ONE private EXECUTE
--     grant beyond PUBLIC; the leak gate pins the set. member_link(text) reads member_profiles in its body
--     and stays dark on purpose — member_links is unreadable in Team mode; the link is in
--     member_profiles_team.at_fields->>'Facebook Profile Link'.
grant execute on function digest.is_active_member_status(text) to millie_team_ro;

-- 3. the deny-list view (#172 AC 4, the "Team mode column", as SQL not prose). Keeps the three categories
--    #172 opens — exact revenue, contact details, Stripe/billing — and drops the at_fields keys that stay
--    closed. Runs as its owner (postgres), which is why the role needs no grant on the table itself.
--    Column list = every column of digest.member_profiles on 2026-09-10 (32), at_fields filtered.
create or replace view digest.member_profiles_team as
select
  p.at_member_id, p.full_name, p.email, p.status, p.plan_name, p.subscription_status, p.subscription_started,
  p.join_date, p.paid_date, p.next_renewal, p.next_renewal_amount, p.scheduled_cancel, p.collection_paused,
  p.mrr, p.membership_fee, p.billing_cycle, p.stripe_customer_id, p.stripe_subscription_id,
  p.engagement_score, p.score_breakdown, p.score_updated,
  (select coalesce(jsonb_object_agg(e.k, e.v), '{}'::jsonb)
     from jsonb_each(coalesce(p.at_fields, '{}'::jsonb)) as e(k, v)
    where e.k !~* '(removal|reason|ltv|score ?card|member score|notes|lead scor|budget)') as at_fields,
  p.application, p.application_at, p.synced_at, p.application_form,
  p.lifetime_paid, p.lifetime_paid_first_payment, p.lifetime_paid_payments, p.lifetime_paid_synced_at,
  p.rough_benchmark_paid, p.lifetime_paid_vs_benchmark_pct
from digest.member_profiles p;
comment on view digest.member_profiles_team is
  '#172 Team research: member_profiles with the at_fields keys that stay closed in Team mode removed (removal reasons, LTV, internal notes, lead scoring). The read-only role reads this, never the table.';
grant select on digest.member_profiles_team to millie_team_ro;

-- 4. the runner. SECURITY DEFINER + OWNER millie_team_ro = the body runs AS the read-only role.
--    transaction_read_only is forced for the rest of the PostgREST transaction so that even a
--    PUBLIC-executable SECURITY DEFINER writer (31 such functions exist today) cannot write from inside
--    a query. The LIMIT wrapper makes a second statement a syntax error and bounds the payload; the
--    newline before the closing parenthesis keeps a trailing "-- comment" from swallowing the wrapper.
--    The wall-clock cap is the CALLING role's statement_timeout (service_role: 60 s), measured by the
--    pg_sleep check in scripts/test_172_team_sql.py.
create or replace function digest.team_sql(p_sql text, p_max_rows integer default 200)
returns jsonb
language plpgsql
security definer
set search_path to 'digest', 'event', 'pg_temp'
as $function$
declare
  v_cap integer := greatest(1, least(coalesce(p_max_rows, 200), 500));
  v_rows jsonb;
  v_n integer;
begin
  perform set_config('transaction_read_only', 'on', true);
  if p_sql is null or p_sql !~* '^\s*(select|with|values)\M' then
    raise exception 'team_sql: only a single SELECT / WITH / VALUES statement is allowed'
      using errcode = '42501';
  end if;
  execute format(
    E'select coalesce(jsonb_agg(t), \'[]\'::jsonb) from (select * from (%s\n) q limit %s) t',
    rtrim(p_sql, E' \n\t;'), v_cap + 1
  ) into v_rows;
  v_n := jsonb_array_length(v_rows);
  return jsonb_build_object(
    'rows', case when v_n > v_cap
                 then (select coalesce(jsonb_agg(x.e), '[]'::jsonb)
                         from jsonb_array_elements(v_rows) with ordinality as x(e, i)
                        where x.i <= v_cap)
                 else v_rows end,
    'row_count', least(v_n, v_cap),
    'truncated', v_n > v_cap
  );
end
$function$;

-- Handing an object to a role requires that role to hold CREATE on the schema at that moment
-- (first apply 2026-09-10 failed here: "permission denied for schema digest"). Grant it for the one
-- statement and take it back: the role must never be able to create anything, and the gate pins that.
grant create on schema digest to millie_team_ro;
alter function digest.team_sql(text, integer) owner to millie_team_ro;
revoke create on schema digest from millie_team_ro;
revoke all on function digest.team_sql(text, integer) from public;
grant execute on function digest.team_sql(text, integer) to service_role;
comment on function digest.team_sql(text, integer) is
  '#172 Team research: one read-only SELECT over digest+event as millie_team_ro, LIMIT-wrapped, read-only transaction forced. service_role only. Returns {rows,row_count,truncated}.';

notify pgrst, 'reload schema';
