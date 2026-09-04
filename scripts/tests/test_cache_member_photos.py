# scripts/tests/test_cache_member_photos.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cache_member_photos import candidate_urls, best_attachment

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
