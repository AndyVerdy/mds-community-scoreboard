"""zoom_weekly heartbeat contract — `python3 scripts/test_zoom_weekly_heartbeat.py`.

Which run statuses advance last_success_at. A DEGRADED run (no GROUPOS_PAT) has done the
whole Zoom half — attendance, transcripts, dossiers, embeddings — and the video half is
owned by the videos_refresh heartbeat. Withholding the stamp on degraded kept the tile red
for 26 days (7 Aug → 2 Sep 2026) on a job that ran clean every week."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zoom_weekly

captured = []
zoom_weekly.sb = lambda method, path, key, rows, prefer: captured.append(rows[0])

def stamped(status):
    captured.clear()
    zoom_weekly.heartbeat("k", status, "d")
    return "last_success_at" in captured[0]

fails = 0
for status, want in (("ok", True), ("degraded", True), ("error", False)):
    got = stamped(status)
    mark = "ok " if got == want else "FAIL"
    if got != want: fails += 1
    print(f"{mark}  status={status:<9} stamps last_success_at={got} (want {want})")
print("all green" if not fails else f"{fails} failing")
sys.exit(1 if fails else 0)
