#!/usr/bin/env python3
"""
Olivia question LABELLING — one topic per question, stored, so the portal's period
picker can drive the topics card.

Why this exists (#25, 2026-07-31). `olivia_question_report.py` clusters a period and
writes a SNAPSHOT of counts into digest.olivia_question_topics. A snapshot cannot be
resliced by date, so the dashboard could only ever show the window some past run
happened to cover: "Yesterday" showed nothing and "Last 30 days" showed a Jun 20 - Jul 20
report against 266 questions. Labelling each question once turns every window into a
GROUP BY, so the card behaves like every other card on the page.

Idempotent: only questions with no row in digest.olivia_question_labels are sent to the
model, so re-running costs nothing and a nightly run labels just the new arrivals.

Usage:  python3 scripts/olivia_label_questions.py [--limit N] [--dry-run]

Secrets from mds-digest-web/.env.local (key = CENTURION_ANTHROPIC_API_KEY — namespaced
because Claude Code exports an EMPTY ANTHROPIC_API_KEY). curl, not urllib.
"""
import argparse
import json
import subprocess
import sys

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
MODEL = "claude-haiku-4-5-20251001"
BATCH = 40

# Commands are not questions — same list the dashboard uses, kept in sync deliberately.
SKIP = {"new question", "next question", "new topic", "reset", "start over",
        "stop", "start", "hi", "hey", "hello", "thanks", "thanks!", "thank you"}

# Seed vocabulary: the labels the first clustering run produced. Giving the model a
# stable vocabulary keeps labels consistent across runs instead of drifting into
# synonyms ("Finding an expert" vs "Expert lookup") that would fragment the counts.
SEED_TOPICS = [
    "Member location/networking", "Community chat content queries", "Automated digest/updates",
    "Application content review", "Assistant data/capabilities", "Finding an expert",
    "Specific member info lookup", "Event planning/invites", "Event registration",
    "Partner deals/discounts", "Facebook group catch-up", "Video library/recordings",
    "Billing/membership", "Account settings change", "Logistics/shipping",
    "Selling tactics/advice", "Other",
]


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def curl_json(url, key, method="GET", body=None, headers=None):
    cmd = ["curl", "-s", "-X", method, url, "-H", f"apikey: {key}",
           "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest"]
    for h in (headers or []):
        cmd += ["-H", h]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"curl failed: {r.stderr}")
    if not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"non-JSON from {url}: {r.stdout[:400]}")


def paged(url, key, page=1000):
    """PostgREST caps responses at 1000 rows; walk offsets until a short page."""
    out = []
    off = 0
    while off < 100 * page:
        batch = curl_json(f"{url}&limit={page}&offset={off}", key)
        out.extend(batch)
        if len(batch) < page:
            break
        off += page
    return out


def anthropic(key, system, user):
    body = {"model": MODEL, "max_tokens": 4000, "thinking": {"type": "disabled"},
            "system": system, "messages": [{"role": "user", "content": user}]}
    cmd = ["curl", "-s", "https://api.anthropic.com/v1/messages",
           "-H", f"x-api-key: {key}", "-H", "anthropic-version: 2023-06-01",
           "-H", "content-type: application/json", "--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(body), capture_output=True, text=True)
    resp = json.loads(r.stdout)
    if "content" not in resp:
        sys.exit(f"anthropic error: {r.stdout[:400]}")
    return "".join(c.get("text", "") for c in resp["content"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="max questions to label this run")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    env = load_env()
    sb = env["SUPABASE_SECRET_KEY"]
    ak = env["CENTURION_ANTHROPIC_API_KEY"]

    # every real member question (eval harness excluded — it is not a member asking).
    # ⚠️ PostgREST caps a response at 1000 rows whatever `limit` says, and this fetch is
    # created_at.ASC — so a single call silently returns the OLDEST 1000 and drops the newest
    # (it bit this script on its first run: 372 of 389 labelled, the 17 most recent missing —
    # the same cap that was blinding the dashboard, #25). Page until a short page comes back.
    rows = paged(f"{BASE}/olivia_messages?role=eq.member&select=id,text,wamid"
                 f"&order=created_at.asc", sb)
    done = {r["message_id"] for r in
            paged(f"{BASE}/olivia_question_labels?select=message_id&order=message_id.asc", sb)}

    todo = [r for r in rows
            if r["id"] not in done
            and (r.get("text") or "").strip()
            and (r["text"] or "").strip().lower() not in SKIP
            and not str(r.get("wamid") or "").startswith("wamid.SELFTEST")]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(rows)} member turns · {len(done)} already labelled · {len(todo)} to label")
    if not todo or a.dry_run:
        return

    system = ("You label member questions asked to an MDS (Million Dollar Sellers) community "
              "assistant with ONE topic each. Prefer a label from the VOCABULARY; invent a new "
              "short label only when nothing fits. Same question asked different ways = same "
              "label. Output ONLY minified JSON: {\"labels\":[{\"id\":<id>,\"topic\":\"label\"}]} "
              "with one entry for EVERY id given.\nVOCABULARY: " + json.dumps(SEED_TOPICS))

    labelled = 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        user = json.dumps([{"id": r["id"], "q": (r["text"] or "")[:300]} for r in chunk])
        out = anthropic(ak, system, user)
        try:
            got = json.loads(out[out.index("{"):out.rindex("}") + 1])["labels"]
        except Exception:
            print(f"  batch {i//BATCH}: unparseable, skipping")
            continue
        payload = [{"message_id": g["id"], "topic": str(g["topic"])[:80], "model": MODEL}
                   for g in got if g.get("id") and g.get("topic")]
        if payload:
            curl_json(f"{BASE}/olivia_question_labels", sb, method="POST", body=payload,
                      headers=["Prefer: resolution=merge-duplicates,return=minimal"])
            labelled += len(payload)
        print(f"  batch {i//BATCH + 1}: {len(payload)} labelled")
    print(f"done — {labelled} questions labelled")


if __name__ == "__main__":
    main()
