# scripts/tests/test_cache_member_photos.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timezone
from cache_member_photos import candidate_urls, best_attachment
import cache_member_photos as cmp

def test_candidate_urls_prefers_large_attachments_then_text_links():
    fields = {"Picture URL": [{"url": "https://a/att.jpg", "width": 800, "thumbnails": {"large": {"url": "https://a/large.jpg", "width": 512}}}],
              "Photo": ["https://api.typeform.com/responses/files/x/Profile3.jpg"],
              "Facebook Photo": [{"url": "https://a/fb40.jpg", "width": 40}]}
    assert candidate_urls(fields) == [("Picture URL", "https://a/large.jpg"), ("Photo", "https://api.typeform.com/responses/files/x/Profile3.jpg")]

def test_best_attachment_rejects_tiny_images():
    assert best_attachment([{"url": "https://a/fb40.jpg", "width": 40}]) is None
    assert best_attachment([{"url": "https://a/x.jpg", "width": 300}]) == "https://a/x.jpg"

def test_groupos_roster_rows_become_candidates():
    from cache_member_photos import groupos_candidates
    rows = [{"email": "mo@x.com", "avatar_url": "uploads/users/profile/thumb-1.jpeg"}]
    assert groupos_candidates(rows, {"mo@x.com": "rec1"}) == {"rec1": "https://mds-community.s3.amazonaws.com/uploads/users/profile/thumb-1.jpeg"}


# --- review round 1 additions -----------------------------------------------------------------

def test_groupos_candidates_passes_absolute_url_through_unchanged():
    """(e) an already-absolute avatar_url (a different S3 host even — the event check-in app's
    bucket, confirmed live 2026-09-04) is used as-is; only a relative path gets the S3 prefix."""
    from cache_member_photos import groupos_candidates
    rows = [{"email": "a@x.com",
             "avatar_url": "https://mds-community.s3.us-east-2.amazonaws.com/uploads/attendee/profile/x.jpg"}]
    assert groupos_candidates(rows, {"a@x.com": "rec2"}) == {
        "rec2": "https://mds-community.s3.us-east-2.amazonaws.com/uploads/attendee/profile/x.jpg"}


def test_fetch_all_builds_url_with_single_question_mark(monkeypatch):
    """(b) regression guard for the live PGRST100 bug (two '?' in one URL) — extra must be an
    &-joined fragment, never re-introduce its own '?'."""
    captured = []

    def fake_sb(method, path, key, body=None, prefer=None):
        captured.append(path)
        return []  # empty page ends pagination immediately

    monkeypatch.setattr(cmp, "sb", fake_sb)
    cmp.fetch_all("k", "member_profiles", "at_member_id", extra="&status=in.(Current%20Member)")
    assert captured[0].count("?") == 1


def test_safe_url_percent_encodes_space_and_leaves_existing_encoding_alone():
    """(c) a raw space (routine in GroupOS/Airtable filenames) is percent-encoded before curl
    ever sees it; a URL that's already validly encoded is left alone (no double-encoding)."""
    assert cmp.safe_url("https://a/x y.jpg") == "https://a/x%20y.jpg"
    assert cmp.safe_url("https://a/already%20encoded.jpg") == "https://a/already%20encoded.jpg"


def test_is_valid_image_accepts_real_formats_rejects_html():
    """(d) magic-byte sniffing, not Content-Type: JPEG/PNG/WEBP accepted, an HTML error/
    interstitial body rejected, and a non-WEBP RIFF file (e.g. WAV) rejected too — the minor
    finding: checking only the "RIFF" prefix would have accepted any RIFF container, not just
    WEBP images."""
    assert cmp.is_valid_image(b"\xff\xd8\xff\xe0\x00\x10JFIF") is True             # jpeg
    assert cmp.is_valid_image(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR") is True       # png
    assert cmp.is_valid_image(b"RIFF\x24\x00\x00\x00WEBPVP8 ") is True             # webp
    assert cmp.is_valid_image(b"RIFF\x24\x00\x00\x00WAVEfmt ") is False            # riff, not webp
    assert cmp.is_valid_image(b"<!DOCTYPE html><html><head><title>Err") is False   # html error page


def _stub_pipeline(monkeypatch, download_ok):
    """Wire download_image/convert_and_measure/upload_photo/upsert_photo_row to succeed for any
    URL where `download_ok(url)` is true, and record every URL try_candidate attempted to
    download (in call order) — that order is the proof of "groupos tried first"."""
    calls = []

    def fake_download(url, dest):
        calls.append(url)
        return download_ok(url)

    monkeypatch.setattr(cmp, "download_image", fake_download)
    monkeypatch.setattr(cmp, "convert_and_measure", lambda src, dst: 200)
    monkeypatch.setattr(cmp, "upload_photo", lambda key, rec, path: True)
    monkeypatch.setattr(cmp, "upsert_photo_row", lambda key, row: None)
    monkeypatch.setattr(cmp.time, "sleep", lambda s: None)
    return calls


def test_process_member_groupos_success_never_calls_airtable(monkeypatch):
    """(a) part 1: a working GroupOS candidate is used and Airtable is never even fetched."""
    _stub_pipeline(monkeypatch, download_ok=lambda url: True)

    def boom(pat, rec):
        raise AssertionError("airtable_fields must not be called when groupos succeeds")
    monkeypatch.setattr(cmp, "airtable_fields", boom)

    ctx = {"key": "k", "pat": "p", "groupos": {"rec1": "https://s3/groupos.jpg"},
           "now": datetime.now(timezone.utc)}
    result = cmp.process_member({"at_member_id": "rec1", "full_name": "Test"}, ctx)
    assert result == {"ok": True, "source": "groupos", "reason": None}


def test_process_member_falls_back_to_airtable_when_groupos_candidate_fails(monkeypatch):
    """(a) part 2: GroupOS is tried FIRST (proven by call order) and Airtable is only fetched +
    tried because the GroupOS candidate failed end-to-end, not because it was absent."""
    calls = _stub_pipeline(monkeypatch, download_ok=lambda url: url == "https://airtable/photo.jpg")
    monkeypatch.setattr(cmp, "airtable_fields",
                         lambda pat, rec: {"Picture URL": "https://airtable/photo.jpg"})

    ctx = {"key": "k", "pat": "p", "groupos": {"rec1": "https://s3/groupos-broken.jpg"},
           "now": datetime.now(timezone.utc)}
    result = cmp.process_member({"at_member_id": "rec1", "full_name": "Test"}, ctx)

    assert calls == ["https://s3/groupos-broken.jpg", "https://airtable/photo.jpg"]
    assert result == {"ok": True, "source": "Picture URL", "reason": None}


def test_process_member_catches_exception_and_reports_failure_never_prints_key(monkeypatch, capsys):
    """(f) / finding 1: process_member never raises — a poisoned candidate (any exception from
    the network/Supabase layer) becomes a clean failure result, and the log line names the
    member + exception class but never the secret key."""
    secret = "sb_secret_should_never_leak_zzz"

    def boom(url, dest):
        raise RuntimeError(f"transient error, key={secret}")
    monkeypatch.setattr(cmp, "download_image", boom)

    ctx = {"key": secret, "pat": "p", "groupos": {"rec1": "https://s3/x.jpg"},
           "now": datetime.now(timezone.utc)}
    result = cmp.process_member({"at_member_id": "rec1"}, ctx)

    assert result == {"ok": False, "source": None, "reason": "exception:RuntimeError"}
    out = capsys.readouterr().out
    assert secret not in out
    assert "rec1" in out and "RuntimeError" in out


def test_run_batch_aggregates_isolated_failures_from_a_stub(monkeypatch):
    """(f): run_batch's own aggregation contract — one member reporting a failure (as the real
    process_member would after catching an exception) never stops the loop over the rest."""
    processed = []

    def stub_process_member(m, ctx):
        processed.append(m["at_member_id"])
        if m["at_member_id"] == "bad":
            return {"ok": False, "source": None, "reason": "exception:RuntimeError"}
        return {"ok": True, "source": "groupos", "reason": None}

    monkeypatch.setattr(cmp, "process_member", stub_process_member)
    todo = [{"at_member_id": "a"}, {"at_member_id": "bad"}, {"at_member_id": "c"}]
    ok, src_counts, fail_reasons = cmp.run_batch(todo, {})

    assert processed == ["a", "bad", "c"]
    assert ok == 2
    assert fail_reasons == {"exception:RuntimeError": 1}


def test_batch_isolation_end_to_end_one_raising_member_others_still_cached(monkeypatch):
    """(f) end-to-end: a stub that RAISES for exactly one member (at the lowest network layer,
    upsert_photo_row) leaves the other members processed and cached, and the heartbeat detail
    computed from the result says "failed 1" — the full chain finding 1 + finding 3 promise."""
    monkeypatch.setattr(cmp, "download_image", lambda url, dest: True)
    monkeypatch.setattr(cmp, "convert_and_measure", lambda src, dst: 200)
    monkeypatch.setattr(cmp, "upload_photo", lambda key, rec, path: True)

    def flaky_upsert(key, row):
        if row["at_member_id"] == "bad":
            raise RuntimeError("Supabase error: simulated transient failure")
    monkeypatch.setattr(cmp, "upsert_photo_row", flaky_upsert)

    todo = [{"at_member_id": "a"}, {"at_member_id": "bad"}, {"at_member_id": "c"}]
    ctx = {"key": "k", "pat": "p",
           "groupos": {"a": "https://s3/a.jpg", "bad": "https://s3/bad.jpg", "c": "https://s3/c.jpg"},
           "now": datetime.now(timezone.utc)}

    ok, src_counts, fail_reasons = cmp.run_batch(todo, ctx)
    assert ok == 2
    assert fail_reasons == {"exception:RuntimeError": 1}

    status, detail = cmp.compute_status_and_detail(ok, src_counts, fail_reasons, 0, len(todo), 3)
    assert "failed 1" in detail


def test_compute_status_and_detail_error_thresholds():
    """Finding 3: heartbeat status is computed, not hardcoded "ok". Nothing attempted (everyone
    fresh) and no_source-only failures are both healthy "ok" outcomes (no_source is the
    steady-state population with no photo anywhere — folding it into "failed" would trip the
    25% threshold on every normal nightly run forever); a real technical-failure rate over 25%,
    or every attempted member technically failing, is "error"."""
    status, _ = cmp.compute_status_and_detail(0, {}, {}, 700, 0, 700)
    assert status == "ok"

    status, detail = cmp.compute_status_and_detail(
        12, {"Photo": 12}, {"no_candidate": 112}, 627, 124, 760)
    assert status == "ok"
    assert "no_source 112" in detail and "failed 0" in detail

    status, _ = cmp.compute_status_and_detail(2, {"groupos": 2}, {"download_failed": 3}, 0, 5, 5)
    assert status == "error"

    status, _ = cmp.compute_status_and_detail(0, {}, {"upload_failed": 3}, 0, 3, 3)
    assert status == "error"


def test_build_email_to_member_skips_email_on_rpc_error(monkeypatch, capsys):
    """Finding 1: a bad Supabase response for one roster email must not abort resolving the
    rest — that email is skipped (cached as unresolved) and logged without the key."""
    secret = "secret-key-123"

    def flaky_sb(method, path, key, body=None, prefer=None):
        if body.get("p_email") == "bad@x.com":
            raise RuntimeError("Supabase error: simulated")
        return "rec_good"

    monkeypatch.setattr(cmp, "sb", flaky_sb)
    rows = [{"email": "bad@x.com", "avatar_url": "a.jpg"},
            {"email": "good@x.com", "avatar_url": "b.jpg"}]
    result = cmp.build_email_to_member(secret, rows)

    assert result == {"bad@x.com": None, "good@x.com": "rec_good"}
    assert secret not in capsys.readouterr().out
