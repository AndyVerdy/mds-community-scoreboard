"""videos_weekly_check — a clean check (nothing moved) must STAMP the heartbeat and exit 0.
`python3 scripts/test_videos_weekly_check_nothing_moved.py`

The nothing-moved branch is the one that runs on most weeks. If it crashes, videos_refresh
goes stale through healthy runs and the derivations tile turns red for a job that worked."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import videos_weekly_check as vwc

video = {"id": "vid1", "title": "T"}
row = {"video_id": "vid1", **{f: None for f in vwc.WATCH}}
row["title"] = "T"
posted = []

def fake_sb(method, path, key, body=None, prefer=None):
    if method == "GET":
        return [dict(row)]          # catalog already holds the same row -> nothing moved
    posted.append((path, body))
    return []

vwc.env = lambda name: {"SUPABASE_SECRET_KEY": "k"}
vwc.sb = fake_sb
vwc.load_dump = lambda path: [video]
vwc.map_video = lambda v: (dict(row), None)

sys.argv = ["videos_weekly_check.py", "dump.json", "--apply"]
rc = vwc.main()
hb = [b for p, b in posted if p.startswith("olivia_job_heartbeats")]
ok = rc == 0 and hb and "last_success_at" in hb[0][0] and hb[0][0]["status"] == "ok"
print(("ok " if ok else "FAIL"), f"rc={rc} heartbeat posts={len(hb)}", hb[0][0].get("detail") if hb else "")
sys.exit(0 if ok else 1)
