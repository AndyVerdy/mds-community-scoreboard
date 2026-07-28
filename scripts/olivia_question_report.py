#!/usr/bin/env python3
"""
Olivia question-topics report — semantic clustering of what members actually ask.

Reads member turns from digest.olivia_messages (reset/STOP commands excluded), has
Claude group them into topics (same question asked many ways = one topic), upserts
the clusters into digest.olivia_question_topics (replacing the same period), and
prints the report. The portal reads that table for display.

Usage:  python3 scripts/olivia_question_report.py [--days 30]

Secrets from mds-digest-web/.env.local (parsed here; key = CENTURION_ANTHROPIC_API_KEY —
namespaced because Claude Code exports an EMPTY ANTHROPIC_API_KEY). curl, not urllib.
"""
import argparse
import json
import subprocess
import sys
from datetime import date, timedelta

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
SKIP = {"new question", "next question", "new topic", "reset", "start over",
        "stop", "start", "hi", "hey", "hello", "thanks", "thanks!", "thank you"}


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
    for h in headers or []:
        cmd += ["-H", h]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(p.stdout) if p.stdout.strip() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args()
    env = load_env()
    sb = env["SUPABASE_SECRET_KEY"]
    ak = env["CENTURION_ANTHROPIC_API_KEY"]
    since = (date.today() - timedelta(days=args.days)).isoformat()

    rows = curl_json(f"{BASE}/olivia_messages?role=eq.member&created_at=gte.{since}"
                     f"&select=phone,text&order=id.asc&limit=2000", sb)
    qs = [(r["phone"], r["text"].strip()) for r in rows
          if r.get("text") and r["text"].strip().lower() not in SKIP and len(r["text"].strip()) > 2]
    if not qs:
        print("no member questions in the window")
        return
    print(f"{len(qs)} member questions since {since} from {len({p for p, _ in qs})} member(s)")

    numbered = "\n".join(f"{i}. {t}" for i, (_, t) in enumerate(qs))
    resp = subprocess.run(["curl", "-s", "https://api.anthropic.com/v1/messages",
        "-H", f"x-api-key: {ak}", "-H", "anthropic-version: 2023-06-01",
        "-H", "content-type: application/json",
        "-d", json.dumps({
            "model": "claude-sonnet-5",
            "max_tokens": 2000,
            "system": "You cluster member questions asked to an MDS community assistant into topics. "
                      "Group semantically - the same intent phrased differently is ONE topic. "
                      "Output ONLY minified JSON: {\"topics\":[{\"topic\":\"short human label\","
                      "\"question_indexes\":[ints]}]} covering every index exactly once. "
                      "8-15 topics max; merge small one-offs into an 'Other' topic.",
            "messages": [{"role": "user", "content": numbered}],
        })], capture_output=True, text=True)
    out = json.loads(resp.stdout)
    text = "".join(c.get("text", "") for c in out.get("content", []))
    try:
        clusters = json.loads(text[text.index("{"):text.rindex("}") + 1])["topics"]
    except (ValueError, KeyError):
        print("clustering parse failed; raw:", text[:400])
        sys.exit(1)

    today = date.today().isoformat()
    curl_json(f"{BASE}/olivia_question_topics?period_start=eq.{since}&period_end=eq.{today}",
              sb, method="DELETE")
    payload, report = [], []
    for c in sorted(clusters, key=lambda c: -len(c["question_indexes"])):
        idx = [i for i in c["question_indexes"] if 0 <= i < len(qs)]
        examples = list(dict.fromkeys(qs[i][1] for i in idx))[:4]
        askers = len({qs[i][0] for i in idx})
        payload.append({"period_start": since, "period_end": today, "topic": c["topic"],
                        "question_count": len(idx), "example_questions": examples,
                        "askers": askers})
        report.append((c["topic"], len(idx), askers, examples))
    curl_json(f"{BASE}/olivia_question_topics", sb, method="POST", body=payload,
              headers=["Prefer: return=minimal"])

    print(f"\n=== TOP QUESTION TOPICS ({since} → {today}) ===")
    for topic, n, askers, ex in report:
        print(f"\n{topic} — {n} question(s), {askers} member(s)")
        for e in ex[:2]:
            print(f'   e.g. "{e[:90]}"')


if __name__ == "__main__":
    main()
