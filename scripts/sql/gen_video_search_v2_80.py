#!/usr/bin/env python3
"""#80 — regenerate digest.video_search_v2 with p_video_id + a summary return column.

Reads the byte-matched export (db/functions/video_search_v2.sql), applies FOUR exact
edits, and prints the full migration SQL (DROP + CREATE + grants + pgrst reload).
Return-type changes require DROP; DROP on a PostgREST RPC requires the reload notify.

Why: the loop's video_search tool executes video_search_v2, which returned NO summary
column — so an accepted "Want a quick summary?" offer could never be delivered from
the video itself (ans #28131/#28133/#29905, week of 2026-08-04). p_video_id gives the
loop an exact-row fetch for the video its own previous message linked.
"""
SRC = "/Users/Born/Scorecard/db/functions/video_search_v2.sql"

body = open(SRC).read().split("\n", 1)[1]  # strip the GENERATED header line

edits = [
    # 1) signature: add p_video_id
    ("p_order text DEFAULT NULL::text)",
     "p_order text DEFAULT NULL::text, p_video_id text DEFAULT NULL::text)"),
    # 2) return table: trailing summary column
    ("is_restricted boolean, fit_reason text, strength_note text)",
     "is_restricted boolean, fit_reason text, strength_note text, summary text)"),
    # 3) base CTE: exact-id filter (published/deleted/restriction logic untouched)
    ("where v.status = 'published' and v.deleted_at is null",
     "where v.status = 'published' and v.deleted_at is null\n       and (p_video_id is null or v.video_id = p_video_id)"),
    # 4) final select: emit the summary (never for restricted videos)
    ("         f.snote\n    from fused f",
     "         f.snote,\n         case when f.restricted then null else f.summary end\n    from fused f"),
]
for old, new in edits:
    assert body.count(old) == 1, f"anchor not unique ({body.count(old)}x): {old[:60]!r}"
    body = body.replace(old, new)

print("drop function digest.video_search_v2(text, text, integer, text, text, text, text);")
print(body.rstrip() + ";")
print("""
grant execute on function digest.video_search_v2(p_phone text, p_query text, p_limit integer, p_embedding text, p_at_member_id text, p_call_type text, p_order text, p_video_id text) to postgres;
grant execute on function digest.video_search_v2(p_phone text, p_query text, p_limit integer, p_embedding text, p_at_member_id text, p_call_type text, p_order text, p_video_id text) to service_role;
notify pgrst, 'reload schema';""")
