-- #65 · Source-of-truth for the SQL layer — READ-ONLY introspection RPC.
--
-- Why this exists: there is no direct-Postgres path from this machine (no psql, no
-- psycopg, no DB password, no Management-API PAT). Every script reaches the database
-- through PostgREST with SUPABASE_SECRET_KEY, and PostgREST cannot read pg_catalog.
-- So the exporter (scripts/db_export_schema.py) needs ONE function to hand it the DDL
-- text of every digest object. Byte-exactness is the whole point of #65, so the export
-- must be machine-driven — a model retyping 262 KB cannot be byte-matched.
--
-- Safety profile:
--   * STABLE, reads only pg_catalog. Writes nothing.
--   * SECURITY INVOKER — no elevated rights. pg_get_functiondef needs none.
--   * Returns DDL text only. No member data of any kind passes through it.
--   * EXECUTE revoked from public/anon/authenticated; granted to service_role only,
--     which already holds full access to the database this describes.

create or replace function digest.schema_source()
returns table (kind text, obj_name text, file_name text, definition text)
language sql
stable
security invoker
set search_path = pg_catalog, public
as $fn$
  -- ── functions ────────────────────────────────────────────────────────────────
  with fns as (
    select p.oid,
           p.proname,
           pg_get_function_identity_arguments(p.oid) as args,
           pg_get_functiondef(p.oid)                 as def,
           count(*) over (partition by p.proname)    as n_same_name
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'digest'
  )
  select 'function'::text,
         proname || '(' || args || ')',
         -- overloads share a proname, so disambiguate those (and only those) by arg hash
         case when n_same_name > 1
              then proname || '__' || substr(md5(args), 1, 8)
              else proname
         end || '.sql',
         def
  from fns

  -- ── views ────────────────────────────────────────────────────────────────────
  union all
  select 'view'::text,
         c.relname,
         c.relname || '.sql',
         'create or replace view digest.' || quote_ident(c.relname) || ' as' || E'\n'
           || pg_get_viewdef(c.oid, true)
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'digest' and c.relkind = 'v'

  -- ── materialized views ───────────────────────────────────────────────────────
  union all
  select 'matview'::text,
         c.relname,
         c.relname || '.sql',
         'create materialized view digest.' || quote_ident(c.relname) || ' as' || E'\n'
           || pg_get_viewdef(c.oid, true)
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'digest' and c.relkind = 'm'

  -- ── triggers ─────────────────────────────────────────────────────────────────
  union all
  select 'catalog'::text, 'triggers', 'triggers.sql',
         coalesce((
           select string_agg(pg_get_triggerdef(t.oid, true) || ';', E'\n' order by
                             c.relname, t.tgname)
           from pg_trigger t
           join pg_class c     on c.oid = t.tgrelid
           join pg_namespace n on n.oid = c.relnamespace
           where n.nspname = 'digest' and not t.tgisinternal
         ), '-- no triggers in schema digest')

  -- ── row-level-security policies ──────────────────────────────────────────────
  union all
  select 'catalog'::text, 'policies', 'policies.sql',
         coalesce((
           select string_agg(
                    format('create policy %I on digest.%I as %s for %s to %s%s%s;',
                           policyname, tablename, permissive, cmd,
                           array_to_string(roles, ', '),
                           coalesce(' using (' || qual || ')', ''),
                           coalesce(' with check (' || with_check || ')', '')),
                    E'\n' order by tablename, policyname)
           from pg_policies where schemaname = 'digest'
         ), '-- no row-level-security policies in schema digest')

  -- ── grants: who may execute / read / write what ──────────────────────────────
  union all
  select 'catalog'::text, 'grants', 'grants.sql',
         coalesce((
           select string_agg(line, E'\n' order by line) from (
             select format('grant execute on function digest.%I(%s) to %s;',
                           p.proname, pg_get_function_identity_arguments(p.oid),
                           coalesce(r.rolname, 'public')) as line
             from pg_proc p
             join pg_namespace n on n.oid = p.pronamespace
             cross join lateral aclexplode(coalesce(p.proacl,
                                acldefault('f', p.proowner))) a
             left join pg_roles r on r.oid = a.grantee
             where n.nspname = 'digest' and a.privilege_type = 'EXECUTE'
             union all
             select format('grant %s on digest.%I to %s;',
                           lower(a.privilege_type), c.relname,
                           coalesce(r.rolname, 'public'))
             from pg_class c
             join pg_namespace n on n.oid = c.relnamespace
             cross join lateral aclexplode(coalesce(c.relacl,
                                acldefault('r', c.relowner))) a
             left join pg_roles r on r.oid = a.grantee
             where n.nspname = 'digest' and c.relkind in ('r', 'v', 'm', 'p')
           ) g
         ), '-- no grants in schema digest')

  -- ── RLS enablement per table (the flag, separate from the policies above) ─────
  union all
  select 'catalog'::text, 'rls', 'rls.sql',
         coalesce((
           select string_agg(
                    case when c.relrowsecurity
                         then format('alter table digest.%I enable row level security;',
                                     c.relname)
                         else format('-- digest.%I: row level security DISABLED',
                                     c.relname) end,
                    E'\n' order by c.relname)
           from pg_class c
           join pg_namespace n on n.oid = c.relnamespace
           where n.nspname = 'digest' and c.relkind in ('r', 'p')
         ), '-- no tables in schema digest')

  -- ── tables: columns, defaults, constraints, indexes (the restore path) ───────
  union all
  select 'catalog'::text, 'tables', 'tables.sql',
         coalesce((
           select string_agg(block, E'\n\n' order by relname) from (
             select c.relname,
                    format('-- digest.%I', c.relname)
                    || E'\n' || coalesce((
                         select string_agg(
                                  format('--   %-34s %s%s%s', a.attname,
                                         format_type(a.atttypid, a.atttypmod),
                                         case when a.attnotnull then ' not null' else '' end,
                                         coalesce(' default ' || pg_get_expr(d.adbin, d.adrelid), '')),
                                  E'\n' order by a.attnum)
                         from pg_attribute a
                         left join pg_attrdef d on d.adrelid = a.attrelid
                                               and d.adnum   = a.attnum
                         where a.attrelid = c.oid and a.attnum > 0 and not a.attisdropped
                       ), '--   (no columns)')
                    || coalesce(E'\n' || (
                         select string_agg(format('alter table digest.%I add constraint %I %s;',
                                                  c.relname, con.conname,
                                                  pg_get_constraintdef(con.oid)),
                                           E'\n' order by con.conname)
                         from pg_constraint con where con.conrelid = c.oid
                       ), '')
                    || coalesce(E'\n' || (
                         select string_agg(pg_get_indexdef(i.indexrelid) || ';',
                                           E'\n' order by pg_get_indexdef(i.indexrelid))
                         from pg_index i where i.indrelid = c.oid
                       ), '') as block
             from pg_class c
             join pg_namespace n on n.oid = c.relnamespace
             where n.nspname = 'digest' and c.relkind in ('r', 'p')
           ) t
         ), '-- no tables in schema digest');
$fn$;

revoke all on function digest.schema_source() from public;
revoke all on function digest.schema_source() from anon;
revoke all on function digest.schema_source() from authenticated;
grant execute on function digest.schema_source() to service_role;

comment on function digest.schema_source() is
  '#65 — read-only DDL export for scripts/db_export_schema.py. No member data. service_role only.';
