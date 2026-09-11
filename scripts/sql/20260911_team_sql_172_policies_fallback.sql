-- scripts/sql/20260911_team_sql_172_policies_fallback.sql  (#172, variant b — only if BYPASSRLS is refused)
--
-- The role WITHOUT BYPASSRLS plus one permissive SELECT policy per RLS-enabled table, enumerated from
-- pg_class at apply time (live 2026-09-10: 33 digest tables, 0 event tables — never hard-code the list).
-- Apply INSTEAD of section 1 of 20260911_team_sql_172.sql, then that file's sections 2-4 (its own
-- role block is skipped because the role exists by then).
-- A table that gains RLS later is dark to the role until this block is re-run — the leak gate's
-- "role reads every table" check is the alarm.
do $do$
declare r record;
begin
  if not exists (select 1 from pg_roles where rolname = 'millie_team_ro') then
    create role millie_team_ro nologin;
  end if;
  for r in
    select n.nspname, c.relname
    from pg_class c join pg_namespace n on n.oid = c.relnamespace
    where c.relkind = 'r' and c.relrowsecurity and n.nspname in ('digest', 'event')
  loop
    execute format('drop policy if exists team_ro_read on %I.%I', r.nspname, r.relname);
    execute format('create policy team_ro_read on %I.%I for select to millie_team_ro using (true)', r.nspname, r.relname);
  end loop;
end $do$;
