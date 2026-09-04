#!/usr/bin/env python3
"""#161 — nightly job: cache member profile photos into Supabase Storage + digest.member_photos.

`personas_library()` already joins `member_photos.public_url` for every member; the table is
empty today so every card in /personas falls back to an initials tile. This job fills it.

Andy's explicit direction (2026-09-04): "You are relying on Airtable, and this is a fraud. OK
for POC but we need a better way." So the resolver order per member is:
  1. GroupOS avatar   — the community platform's own profile photo (S3 thumb, ~150px). Needs a
                         roster file dumped from the GroupOS MCP `members_list` (that tool only
                         runs inside a Claude session — see --groupos-roster below).
  2. Airtable          — attachment/text-link fields on the Member DB record, >=120px only. This
                         is the POC-era source; it stays as a fallback, never the first choice.
  3. Nothing           — the UI already renders an initials tile when member_photos has no row.
`Facebook Photo` is a named EXCLUSION regardless of pixel size — Andy's rule, not a size check
(see candidate_urls). Facebook profile-photo capture during the FB extension runs is a SEPARATE
follow-up ticket; this script never touches the extension.

Usage:
  python3 cache_member_photos.py --dry-run --limit 5 --groupos-roster roster.json   # prints the plan
  python3 cache_member_photos.py --limit 5 --groupos-roster roster.json             # real, small batch
  python3 cache_member_photos.py --groupos-roster roster.json                       # full nightly run
  python3 cache_member_photos.py --force ...                                       # ignore the 30-day-fresh skip

Building the roster file is a separate, one-time-per-run step (see #161 task notes): page
GroupOS `members_list` with limit=50 until has_more is false, and write every item with a
non-empty avatar_url as a flat JSON array of {"email":..., "avatar_url":...}.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

ENV = "/Users/Born/mds-digest-web/.env.local"
SB = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
STORAGE = "https://nadtudwuwjhckotrngzn.supabase.co/storage/v1"
PUBLIC_BASE = "https://nadtudwuwjhckotrngzn.supabase.co/storage/v1/object/public/member-photos"
AIRTABLE_BASE = "appou5JVr0WIrioWS"
AIRTABLE_TABLE = "tblfwOSROSHfuYUxv"
GROUPOS_S3 = "https://mds-community.s3.amazonaws.com/"

JOB = "cache_member_photos"
MAX_AGE_HOURS = 30
STALE_DAYS = 30

# Same five statuses personas_library() treats as active.
STATUSES = ["Current Member", "New Member", "Current Member- Not Renewing",
            "Current Member- Paused", "Staff"]

# Preference order for Airtable photo fields. "Facebook Photo" is deliberately absent — Andy's
# rule is a hard field-name exclusion (40px silhouette thumbnails dominate that field), not a
# per-record size check, so it must never appear here regardless of what any one record holds.
FIELD_ORDER = ["Picture URL", "Headshots", "Photo"]

MIN_WIDTH = 120


def env():
    v = {}
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, val = line.split("=", 1)
            v[k.strip()] = val.strip().strip('"').strip("'")
    return v


def sb(method, path, key, body=None, prefer=None):
    cmd = ["curl", "-sS", "-m", "120", "-X", method, f"{SB}/{path}",
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    p = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                        capture_output=True, text=True)
    if p.stdout.strip().startswith('{') and '"message"' in p.stdout:
        raise RuntimeError("Supabase error: " + p.stdout[:400])
    try:
        return json.loads(p.stdout) if p.stdout.strip() else []
    except Exception:
        return []


def heartbeat(key, status, detail):
    """Stamp digest.olivia_job_heartbeats. Only success stamps last_success_at (same shape as
    partners_weekly_check.py's heartbeat()) — sending it on failure would overwrite the one
    timestamp that answers "when did this last actually work"."""
    row = {"job": JOB, "last_run_at": "now()", "status": status, "detail": detail[:500],
           "max_age_hours": MAX_AGE_HOURS}
    if status == "ok":
        row["last_success_at"] = "now()"
    sb("POST", "olivia_job_heartbeats?on_conflict=job", key, [row],
       "resolution=merge-duplicates,return=minimal")


# ---------------------------------------------------------------------------
# Pure helpers (covered by scripts/tests/test_cache_member_photos.py — no network)
# ---------------------------------------------------------------------------

def best_attachment(attachments):
    """Pick a usable URL out of an Airtable attachment list, or None.

    Prefers thumbnails.large.url when its width >= MIN_WIDTH, else the attachment's own url when
    ITS width >= MIN_WIDTH, else keeps looking at the next attachment in the list. Never returns
    anything under MIN_WIDTH (that's how the 40px FB-default silhouettes get rejected when they
    show up in a field we do trust)."""
    for a in attachments or []:
        if not isinstance(a, dict):
            continue
        thumb = (a.get("thumbnails") or {}).get("large") or {}
        if thumb.get("url") and (thumb.get("width") or 0) >= MIN_WIDTH:
            return thumb["url"]
        if a.get("url") and (a.get("width") or 0) >= MIN_WIDTH:
            return a["url"]
    return None


_URL_RE = re.compile(r"https?://[^'\"\]\s,]+")


def candidate_urls(fields):
    """Airtable `fields` dict -> ordered [(field_name, url), ...] candidates, best first.

    Walks FIELD_ORDER (never "Facebook Photo" — see module docstring). A field holding a list of
    attachment dicts goes through best_attachment(); anything else (a plain string, or a list of
    URL strings/text — "Photo" is inconsistent record to record) is scanned with a URL regex and
    contributes its first match. A field with no usable candidate is skipped, not padded with a
    None."""
    out = []
    for name in FIELD_ORDER:
        value = fields.get(name)
        if not value:
            continue
        if isinstance(value, list) and value and isinstance(value[0], dict):
            url = best_attachment(value)
            if url:
                out.append((name, url))
            continue
        urls = _URL_RE.findall(str(value))
        if urls:
            out.append((name, urls[0]))
    return out


def groupos_candidates(rows, email_to_member):
    """GroupOS roster rows ({"email":..., "avatar_url":...}) -> {at_member_id: full_s3_url}.

    `email_to_member` is a pre-resolved email(lowercased) -> at_member_id map (built by calling
    the resolve_member_by_email RPC once per roster email — see build_email_to_member below).
    A row whose email doesn't resolve to exactly one member, or that has no avatar_url, is
    dropped silently — GroupOS just isn't this member's photo source."""
    out = {}
    for r in rows:
        email = (r.get("email") or "").strip().lower()
        avatar = (r.get("avatar_url") or "").strip()
        if not email or not avatar:
            continue
        member = email_to_member.get(email)
        if not member:
            continue
        # Empirically (probed live 2026-09-04) avatar_url is USUALLY a relative path under
        # GROUPOS_S3, but some rows already carry a full URL (a different host even —
        # s3.us-east-2... "attendee/profile" uploads, likely from the event check-in app rather
        # than the member-profile uploader). Pass an already-absolute URL through unchanged;
        # only relative paths get the bucket prefix. Doesn't change the given test (its
        # avatar_url is relative, still prefixed the same way).
        out[member] = avatar if avatar.startswith(("http://", "https://")) else GROUPOS_S3 + avatar.lstrip("/")
    return out


# ---------------------------------------------------------------------------
# Network / IO helpers
# ---------------------------------------------------------------------------

def fetch_all(key, table, select, extra=""):
    """Page a PostgREST GET past the 1000-row cap via limit/offset. `extra` is additional
    filter/order query fragments (already `&`-joined, e.g. "status=in.(...)&order=x.asc")."""
    rows, offset = [], 0
    while True:
        page = sb("GET", f"{table}?select={select}{extra}&limit=1000&offset={offset}", key)
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def active_members(key):
    statuses_param = ",".join(urllib.parse.quote(s, safe="") for s in STATUSES)
    return fetch_all(key, "member_profiles", "at_member_id,full_name,email",
                      extra=f"&status=in.({statuses_param})&order=at_member_id.asc")


def existing_photo_ages(key):
    rows = fetch_all(key, "member_photos", "at_member_id,fetched_at")
    return {r["at_member_id"]: r["fetched_at"] for r in rows}


def is_stale(fetched_at, now):
    if not fetched_at:
        return True
    try:
        dt = datetime.fromisoformat(str(fetched_at).replace("Z", "+00:00"))
    except ValueError:
        return True
    return (now - dt) >= timedelta(days=STALE_DAYS)


def build_email_to_member(key, roster_rows):
    """Resolve every distinct roster email to an at_member_id via the RPC, one call per email,
    cached — the roster file is already pre-filtered to rows with an avatar_url, so this is at
    most a few hundred calls, not one per GroupOS member (READ ONLY — never writes)."""
    cache = {}
    for r in roster_rows:
        email = (r.get("email") or "").strip().lower()
        if not email or email in cache:
            continue
        result = sb("POST", "rpc/resolve_member_by_email", key, {"p_email": email})
        cache[email] = result if isinstance(result, str) and result else None
    return cache


def airtable_fields(pat, rec_id):
    cmd = ["curl", "-sS", "-m", "30",
           f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{AIRTABLE_TABLE}/{rec_id}",
           "-H", f"Authorization: Bearer {pat}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
    except Exception:
        return {}
    if not isinstance(d, dict) or "fields" not in d:
        return {}
    return d.get("fields") or {}


_IMAGE_MAGIC = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF8", b"RIFF")  # jpeg, png, gif, webp(riff)


def download_image(url, dest):
    """curl the candidate URL to `dest`. Rejects non-200 and sub-2KB bodies, then sniffs the
    file's own magic bytes rather than trusting the server's Content-Type — confirmed live
    2026-09-04 that GroupOS's S3 bucket serves plenty of genuinely-valid JPEGs as
    `application/octet-stream` (no per-object content-type set at upload time), so the
    Content-Type-based check this had originally rejected ~86 real images as download_failed
    on the first full run. Magic-byte sniffing catches the actual failure case (an HTML
    interstitial/error page) without that false-positive.

    GroupOS/Airtable filenames routinely carry a raw space ("original--Screenshot 2025-08-26 at
    8.22.09 PM.png") — confirmed live 2026-09-04 that curl hard-rejects that ("URL rejected:
    Malformed input to a URL function", never even reaching the network), so every such
    candidate would silently download_failed. Percent-encode literal spaces only; every other
    character in these URLs is already well-formed."""
    url = url.replace(" ", "%20")
    cmd = ["curl", "-sSL", "-m", "40", "-A", "Mozilla/5.0", "-o", dest,
           "-w", "%{http_code} %{size_download}", url]
    p = subprocess.run(cmd, capture_output=True, text=True)
    parts = p.stdout.strip().split(" ", 1)
    if len(parts) < 2:
        return False
    code, size = parts[0], parts[1]
    try:
        size = int(size)
    except ValueError:
        size = 0
    if code != "200" or size < 2000:
        return False
    try:
        with open(dest, "rb") as f:
            head = f.read(16)
    except OSError:
        return False
    return head.startswith(_IMAGE_MAGIC)


def convert_and_measure(src, dst):
    """sips to a 320px-capped, quality-72 JPEG; returns the resulting pixel width, or None."""
    conv = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72",
                            "-Z", "320", src, "--out", dst],
                           capture_output=True, text=True)
    if conv.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) == 0:
        return None
    meas = subprocess.run(["sips", "-g", "pixelWidth", dst], capture_output=True, text=True)
    for line in meas.stdout.splitlines():
        line = line.strip()
        if line.startswith("pixelWidth:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def upload_photo(secret_key, at_member_id, path):
    """PUT the converted JPEG into the member-photos bucket. Body goes to /dev/null so stdout is
    just the %{http_code} — 200 is success.

    Needs BOTH `apikey` and `Authorization: Bearer` — confirmed live 2026-09-04: with only
    Authorization, the Storage gateway rejected the new sb_secret_... key format with
    "Invalid Compact JWS" (it was trying to decode it as a legacy JWT service-role key)."""
    cmd = ["curl", "-sS", "-m", "60", "-o", "/dev/null", "-w", "%{http_code}",
           "-X", "POST", f"{STORAGE}/object/member-photos/{at_member_id}.jpg",
           "-H", f"apikey: {secret_key}",
           "-H", f"Authorization: Bearer {secret_key}",
           "-H", "Content-Type: image/jpeg", "-H", "x-upsert: true",
           "--data-binary", f"@{path}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout.strip() == "200"


def upsert_photo_row(key, row):
    sb("POST", "member_photos?on_conflict=at_member_id", key, [row],
       "resolution=merge-duplicates,return=minimal")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--limit", type=int, default=None, help="cap how many members to process")
    ap.add_argument("--force", action="store_true", help="ignore the 30-day-fresh skip")
    ap.add_argument("--groupos-roster", default=None,
                     help="JSON array of {email, avatar_url} dumped from the GroupOS MCP")
    args = ap.parse_args()

    e = env()
    key = e["SUPABASE_SECRET_KEY"]
    pat = e["AIRTABLE_PAT"]

    members = active_members(key)
    ages = existing_photo_ages(key)
    now = datetime.now(timezone.utc)

    todo = members if args.force else [
        m for m in members if is_stale(ages.get(m["at_member_id"]), now)
    ]
    skipped_fresh = len(members) - len(todo)
    if args.limit is not None:
        todo = todo[:args.limit]

    groupos = {}
    roster_stats = ""
    if args.groupos_roster:
        roster_rows = json.load(open(args.groupos_roster))
        email_to_member = build_email_to_member(key, roster_rows)
        groupos = groupos_candidates(roster_rows, email_to_member)
        resolved = sum(1 for v in email_to_member.values() if v)
        roster_stats = (f"roster {len(roster_rows)} avatar rows, {resolved} emails resolved, "
                         f"{len(groupos)} groupos candidates; ")
        print(f"[groupos] {roster_stats}")

    ok = 0
    src_counts = {}
    fail_reasons = {}

    def try_candidate(rec, chosen_source, chosen_url):
        """Download/convert/upload/upsert one candidate. Returns a fail reason string, or None
        on success (also upserts + counts the success as a side effect)."""
        with tempfile.TemporaryDirectory() as td:
            raw = os.path.join(td, "raw")
            jpg = os.path.join(td, "out.jpg")
            if not download_image(chosen_url, raw):
                return "download_failed"
            width = convert_and_measure(raw, jpg)
            if not width:
                return "convert_failed"
            if not upload_photo(key, rec, jpg):
                return "upload_failed"
            row = {
                "at_member_id": rec,
                "storage_path": f"member-photos/{rec}.jpg",
                "public_url": f"{PUBLIC_BASE}/{rec}.jpg",
                "width": width,
                "source": chosen_source,
                "source_url": chosen_url,
                "fetched_at": now.isoformat(),
            }
            upsert_photo_row(key, row)
            nonlocal ok
            ok += 1
            src_counts[chosen_source] = src_counts.get(chosen_source, 0) + 1
            return None

    for m in todo:
        rec = m["at_member_id"]

        # GroupOS first; Airtable is only fetched — and only tried — when GroupOS has no
        # candidate OR its candidate actually fails to download/convert/upload. This keeps the
        # fast path fast (a working GroupOS photo never touches Airtable) while closing a real
        # gap found live: GroupOS's S3 bucket serves some genuinely-valid images in a shape that
        # can fail to download (see download_image's history), and earlier versions treated a
        # failed GroupOS attempt as final — never falling back to a member's perfectly good
        # Airtable photo, run after run.
        last_reason = "no_candidate"
        saved = False

        if rec in groupos:
            if args.dry_run:
                print(f"[dry-run] {rec} ({m.get('full_name')}) <- groupos: {groupos[rec]}")
                ok += 1
                src_counts["groupos"] = src_counts.get("groupos", 0) + 1
                continue
            last_reason = try_candidate(rec, "groupos", groupos[rec])
            saved = last_reason is None

        if not saved:
            fields = airtable_fields(pat, rec)
            time.sleep(0.25)
            for chosen_source, chosen_url in candidate_urls(fields):
                if args.dry_run:
                    print(f"[dry-run] {rec} ({m.get('full_name')}) <- {chosen_source}: {chosen_url}")
                    ok += 1
                    src_counts[chosen_source] = src_counts.get(chosen_source, 0) + 1
                    saved = True
                    break
                last_reason = try_candidate(rec, chosen_source, chosen_url)
                if last_reason is None:
                    saved = True
                    break

        if not saved:
            fail_reasons[last_reason] = fail_reasons.get(last_reason, 0) + 1

    fail_total = sum(fail_reasons.values())
    detail = (f"{roster_stats}{ok} ok ({src_counts}), {fail_total} failed ({fail_reasons}) "
              f"of {len(todo)} attempted, {skipped_fresh} skipped fresh, {len(members)} active")
    print(detail)

    if args.dry_run:
        print("DRY RUN — nothing written, heartbeat not stamped")
        return 0

    heartbeat(key, "ok", detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
