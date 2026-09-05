#!/usr/bin/env python3
"""#161 — nightly blurb writer for MDS Personas.

The staff-only member sheet shows `persona->>'blurb'` (2-3 warm, plain-English sentences) and
falls back to the first sentences of `persona->>'summary'` while `blurb` is missing. This job
fills `blurb` for every active member whose persona already has a `summary` and either has no
`blurb` yet, or whose `blurb` predates the persona's own last rebuild (`built_at`) -- i.e. the
persona moved on and the blurb is stale.

Builder = claude-haiku-4-5 (same model/API pattern as persona_refresh.py), one short completion
per member (max_tokens=300, thinking disabled). `blurb` and `blurb_at` are written into the same
`persona` jsonb blob member_personas already carries -- PostgREST can't `||` jsonb in a PATCH, so
each write merges into the persona dict read moments earlier and sends the whole object back,
never dropping the other keys (summary, focus, business, ...).

A member whose Haiku call still fails after retries is logged (id only) and skipped -- one bad
member never aborts the run.

  python3 persona_blurbs.py                # write everyone due
  python3 persona_blurbs.py --limit 3       # first 3 due (validation)
  python3 persona_blurbs.py --dry-run       # count only; writes nothing, calls nobody
"""
import argparse
import concurrent.futures
import datetime
import json
import subprocess
import sys
import time
import urllib.parse

ENV = "/Users/Born/mds-digest-web/.env.local"
SB = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
API = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"

JOB = "persona_blurbs"
MAX_AGE_HOURS = 30

# member_profiles.status values that count as "active" for every member-facing derivation job
# (same list cache_member_photos.py uses).
STATUSES = ["Current Member", "New Member", "Current Member- Not Renewing",
            "Current Member- Paused", "Staff"]

CHUNK = 150  # ids per in.() filter, to keep the PostgREST query string short

# One curl round-trip per member measured ~2.2s (--limit 3 live run) -- serial over 758 members
# would run ~28 min, uncomfortably close to nightly_derivations.py's 1800s per-job subprocess
# timeout. WORKERS=5 is the same value persona_refresh.py already tuned for this Supabase
# project (8 there saturated the connection pool and dropped RPCs silently).
WORKERS = 5

# Seconds to sleep before each retry after a 429/529/5xx (the initial call is immediate --
# 758 members at one sleep apiece would blow the ~10-15 min budget for nothing). 3 retries on
# top of the initial try = 4 attempts max for one member.
BACKOFF = (2, 8, 30)


def env():
    v = {}
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, val = line.split("=", 1)
            v[k.strip()] = val.strip().strip('"').strip("'")
    return v


def sb(method, path, key, body=None, prefer=None):
    cmd = ["curl", "-sS", "-m", "60", "-X", method, f"{SB}/{path}",
           "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    p = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                       capture_output=True, text=True)
    if p.stdout.strip().startswith("{") and '"message"' in p.stdout:
        raise RuntimeError("Supabase error: " + p.stdout[:400])
    try:
        return json.loads(p.stdout) if p.stdout.strip() else []
    except Exception:
        return []


def fetch_all(key, table, select, extra=""):
    """Page a PostgREST GET past the 1000-row cap via limit/offset."""
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
    """{at_member_id: full_name} for every active-status member."""
    statuses_param = ",".join(urllib.parse.quote(s, safe="") for s in STATUSES)
    rows = fetch_all(key, "member_profiles", "at_member_id,full_name",
                      extra=f"&status=in.({statuses_param})&order=at_member_id.asc")
    return {r["at_member_id"]: (r.get("full_name") or "This member") for r in rows}


def personas_for(key, ids):
    """member_personas rows (at_member_id, persona, built_at) for the given ids, chunked so the
    in.() filter stays short."""
    out = []
    for i in range(0, len(ids), CHUNK):
        chunk = ids[i:i + CHUNK]
        ids_param = ",".join(urllib.parse.quote(x, safe="") for x in chunk)
        out += sb("GET", f"member_personas?select=at_member_id,persona,built_at"
                          f"&at_member_id=in.({ids_param})", key)
    return out


def due_rows(key):
    """Active members whose persona has a summary and either no blurb yet, or a blurb written
    before the persona's own last rebuild (built_at) -- i.e. the blurb is stale."""
    names = active_members(key)
    rows = personas_for(key, list(names.keys()))
    due = []
    for r in rows:
        persona = r.get("persona") or {}
        if not (persona.get("summary") or "").strip():
            continue
        blurb = (persona.get("blurb") or "").strip()
        blurb_at = persona.get("blurb_at") or ""
        built_at = r.get("built_at") or ""
        if blurb and blurb_at >= built_at:
            continue
        r["_name"] = names.get(r["at_member_id"], "This member")
        due.append(r)
    return due


def build_prompt(name, summary):
    return (f"Write a card blurb for {name} for MDS staff: two or three sentences, warm and plain, third person, "
            "what they do, where, and how they show up in the community. Use only the summary below; "
            "no numbers of any kind -- that means no years or dates either, not just counts or dollar figures -- "
            "no jargon, no exclamation marks, no quotes, no bullet points, under 380 characters.\n\n"
            f"Summary:\n{summary}\n\nBlurb:")


def clean_blurb(text):
    t = (text or "").strip().strip('"').strip()
    return t[:420].rsplit(".", 1)[0] + "." if len(t) > 420 else t


def call_haiku(akey, prompt):
    """POST to the Messages API; body goes on stdin (never the command line) so neither the key
    nor the prompt ever shows up in a process listing. Returns (text_or_None, http_status, usage)
    where usage is the API's own {"input_tokens", "output_tokens"} (or None on failure)."""
    body = {"model": MODEL, "max_tokens": 300, "thinking": {"type": "disabled"},
            "messages": [{"role": "user", "content": prompt}]}
    p = subprocess.run(
        ["curl", "-sS", "-m", "60", "-w", "\n%{http_code}", API,
         "-H", f"x-api-key: {akey}", "-H", "anthropic-version: 2023-06-01",
         "-H", "Content-Type: application/json", "--data-binary", "@-"],
        input=json.dumps(body), capture_output=True, text=True)
    body_text, _, code_str = p.stdout.rpartition("\n")
    try:
        code = int(code_str)
    except ValueError:
        body_text, code = p.stdout, 0
    try:
        d = json.loads(body_text)
        text = "".join(c.get("text", "") for c in d.get("content", []))
        if text.strip():
            return text, code, d.get("usage")
    except Exception:
        pass
    return None, code, None


def blurb_for(akey, name, summary):
    """One member's blurb, retrying on 429/529/5xx with backoff. (None, None) if every attempt
    failed -- the caller logs the id and skips; a single member never aborts the run."""
    prompt = build_prompt(name, summary)
    attempt = 0
    while True:
        text, code, usage = call_haiku(akey, prompt)
        if text:
            return clean_blurb(text), usage
        retryable = code in (429, 529) or 500 <= code < 600
        if not retryable or attempt >= len(BACKOFF):
            return None, None
        time.sleep(BACKOFF[attempt])
        attempt += 1


def compute_status_and_detail(written, skipped, failed, failed_ids, in_tok, out_tok):
    """Turn one run's raw counts into a heartbeat (status, detail) pair. Pure -- no I/O. Mirrors
    cache_member_photos.py's compute_status_and_detail (#161 review finding: this job used to
    call heartbeat(key, "ok", detail) unconditionally, ignoring `failed` entirely).

    attempted = written + failed -- `skipped` never reaches the Haiku call (due_rows() already
    filtered for a non-empty summary; a row only skips here if a persona changed shape between
    the select and now, a rare race, not a steady-state population like cache_member_photos.py's
    "no candidate anywhere" members -- so there is no non-technical-failure carve-out to make
    here, unlike that job's compute_status_and_detail).

    error when: attempted > 0 and failed/attempted > 0.25 -- this also covers "every attempted
    member failed" (100% > 25%). Nothing attempted (every due member was skipped, or nothing was
    due at all) is "ok", a normal outcome. A population/persona-fetch failure is a separate,
    earlier error path in main() (the due_rows() try/except) -- it never reaches this function,
    same as cache_member_photos.py's own population-fetch failure path."""
    attempted = written + failed
    status = "error" if (attempted > 0 and failed / attempted > 0.25) else "ok"
    detail = f"wrote {written} · skipped {skipped} · failed {failed} · tokens in {in_tok} out {out_tok}"
    if failed_ids:
        shown = ",".join(failed_ids[:10]) + (",..." if len(failed_ids) > 10 else "")
        detail += f" ({shown})"
    return status, detail


def heartbeat(key, status, detail):
    """Stamp digest.olivia_job_heartbeats on EVERY completed run, moved or not."""
    row = {"job": JOB, "last_run_at": "now()", "status": status,
           "detail": detail[:500], "max_age_hours": MAX_AGE_HOURS}
    # Only stamp success -- sending the key on a failure would overwrite "when did this last
    # work" at the exact moment you need it. Same rule as zoom_weekly.py / partners_weekly_check.py.
    if status == "ok":
        row["last_success_at"] = "now()"
    sb("POST", "olivia_job_heartbeats?on_conflict=job", key, [row],
       "resolution=merge-duplicates,return=minimal")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="cap how many due members to write this run")
    ap.add_argument("--dry-run", action="store_true",
                     help="count only -- writes nothing, calls the Anthropic API for nobody")
    a = ap.parse_args()

    e = env()
    key, akey = e["SUPABASE_SECRET_KEY"], e["CENTURION_ANTHROPIC_API_KEY"]

    try:
        due = due_rows(key)
    except Exception as ex:
        heartbeat(key, "error", f"could not select due members: {ex}")
        raise

    if a.limit:
        due = due[:a.limit]
    print(f"due {len(due)}")
    if a.dry_run:
        print("DRY RUN -- nothing written, no API calls made")
        return 0

    def process_one(r):
        # Runs on a worker thread -- returns a result tuple, never mutates shared state
        # directly. All tallying happens back on the main thread as results come in. The whole
        # body is guarded: a failure in the Haiku call OR the write-back must skip this one
        # member, never escape the thread and abort the run for everybody else.
        atid = r["at_member_id"]
        persona = r.get("persona") or {}
        summary = (persona.get("summary") or "").strip()
        # due_rows() already filtered for a non-empty summary; this only fires if a persona
        # changed shape between the select and now.
        if not summary:
            return "skipped", atid, None
        name = r.get("_name") or "This member"
        try:
            blurb, usage = blurb_for(akey, name, summary)
            if not blurb:
                return "failed", atid, None
            merged = dict(persona)
            merged["blurb"] = blurb
            merged["blurb_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            sb("PATCH", f"member_personas?at_member_id=eq.{urllib.parse.quote(atid, safe='')}", key,
               {"persona": merged}, prefer="return=minimal")
            return "written", atid, usage
        except Exception:
            return "failed", atid, None

    written = skipped = failed = 0
    failed_ids = []
    in_tok = out_tok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for outcome, atid, usage in pool.map(process_one, due):
            if outcome == "written":
                written += 1
                if usage:
                    in_tok += usage.get("input_tokens") or 0
                    out_tok += usage.get("output_tokens") or 0
                if written % 50 == 0:
                    print(f"  ...{written} written", flush=True)
            elif outcome == "skipped":
                skipped += 1
            else:
                failed += 1
                failed_ids.append(atid)
                print(f"  FAIL {atid}", flush=True)

    status, detail = compute_status_and_detail(written, skipped, failed, failed_ids, in_tok, out_tok)
    heartbeat(key, status, detail)
    print(f"done: {detail}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
