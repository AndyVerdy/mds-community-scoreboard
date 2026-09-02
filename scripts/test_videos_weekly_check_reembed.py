"""videos_weekly_check — a CHANGED video must have its embedding cleared in the upsert, so the
chain's "videos with no vector (new or re-summarised)" step re-embeds it. Without this the
173 videos that gained cliff notes on 2026-09-02 kept vectors built from title + description
only, and plain-language search never saw the notes.
`python3 scripts/test_videos_weekly_check_reembed.py`"""
import sys, os, types
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import videos_weekly_check as vwc

video = {"id": "vid1", "title": "T"}
row = {"video_id": "vid1", **{f: None for f in vwc.WATCH}}
row["title"] = "T"; row["cliff_notes"] = "now has notes"
old = dict(row); old["cliff_notes"] = None
posted = []

def fake_sb(method, path, key, body=None, prefer=None):
    if method == "GET":
        return [old]                     # catalog row lacks the notes -> CHANGED
    posted.append((path, body))
    return []

vwc.env = lambda name: {"SUPABASE_SECRET_KEY": "k"}
vwc.sb = fake_sb
vwc.load_dump = lambda path: [video]
vwc.map_video = lambda v: (dict(row), None)
vwc.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout="chain skipped in test"))

sys.argv = ["videos_weekly_check.py", "dump.json", "--apply"]
rc = vwc.main()
ups = [b for p, b in posted if p.startswith("videos_catalog")]
got = ups[0][0] if ups else {}
ok = rc == 0 and len(ups) == 1 and "embedding" in got and got["embedding"] is None
print(("ok " if ok else "FAIL"), f"rc={rc} upserts={len(ups)} embedding key present={'embedding' in got} value={got.get('embedding')!r}")
sys.exit(0 if ok else 1)
