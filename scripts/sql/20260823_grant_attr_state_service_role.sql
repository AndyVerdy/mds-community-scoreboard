-- 2026-08-23 · #108 finder — applied live via MCP execute_sql the same day.
-- digest.attr_state(text) had proacl {postgres=X/postgres} (EXECUTE revoked from PUBLIC), so the
-- finder's call to rpc/geo_state_set (which calls attr_state inside, SECURITY INVOKER) 403'd for the
-- service role and silently degraded to exact state matching. member_match_v2 never noticed because
-- it runs as its owner. Least-privilege grant: service_role only — anon/authenticated stay denied.
grant execute on function digest.attr_state(text) to service_role;
-- verify: select has_function_privilege('service_role','digest.attr_state(text)','EXECUTE');  -- true
