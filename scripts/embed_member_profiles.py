#!/usr/bin/env python3
"""#7 — embed member profiles for meaning-based people search (Voyage, ~pennies).

One row per active member in digest.member_profile_embeddings. The profile text comes from
digest.profile_texts_for_embedding() — the single definition of what gets embedded (public
card fields + niches + categories, NAME EXCLUDED). Idempotent: a member is re-embedded ONLY
when their current text differs from the stored one, so a nightly run on unchanged data is
a no-op (the member-sync no-op lesson). Rows for members who left the pool are deleted.

Run:  python3 scripts/embed_member_profiles.py          # embed new/changed
      python3 scripts/embed_member_profiles.py --stats  # coverage report, exit 1 if stale
"""
import json, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
BATCH = 96
MODEL = "voyage-3.5-lite"
DIM = 1024


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("SUPABASE_URL").rstrip("/")
KEY = env("SUPABASE_SECRET_KEY")
VOYAGE = env("VOYAGE_API_KEY")


def curl(method, url, body=None, headers=None):
    cmd = ["curl", "-sS", "-X", method, url, "-H", f"apikey: {KEY}",
           "-H", f"Authorization: Bearer {KEY}", "-H", "Content-Type: application/json",
           "--max-time", "120"]
    for h in headers or []:
        cmd += ["-H", h]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else None


def paged_get(path):
    out, offset = [], 0
    while True:  # PostgREST caps at 1000 whatever limit says — ALWAYS page
        page = curl("GET", f"{BASE}/rest/v1/{path}&limit=1000&offset={offset}",
                    headers=["Accept-Profile: digest"])
        if not isinstance(page, list):
            sys.exit(f"GET {path} failed: {str(page)[:200]}")
        out += page
        if len(page) < 1000:
            return out
        offset += 1000


def voyage_embed(texts):
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", "https://api.voyageai.com/v1/embeddings",
         "-H", f"Authorization: Bearer {VOYAGE}", "-H", "Content-Type: application/json",
         "--max-time", "120", "--data-binary", "@-"],
        input=json.dumps({"model": MODEL, "input": texts, "input_type": "document",
                          "output_dimension": DIM}),
        capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "data" not in d:
        sys.exit(f"voyage error: {str(d)[:300]}")
    return [row["embedding"] for row in d["data"]]


def main():
    want = curl("POST", f"{BASE}/rest/v1/rpc/profile_texts_for_embedding", body={},
                headers=["Content-Profile: digest"])
    if not isinstance(want, list):
        sys.exit(f"profile_texts_for_embedding failed: {str(want)[:200]}")
    want_by_id = {r["at_member_id"]: r["profile_text"] or "" for r in want}

    have = paged_get("member_profile_embeddings?select=at_member_id,profile_text,embedding")
    have_by_id = {r["at_member_id"]: r for r in have}

    todo = [(mid, txt) for mid, txt in want_by_id.items()
            if txt and (mid not in have_by_id
                        or have_by_id[mid]["profile_text"] != txt
                        or have_by_id[mid]["embedding"] is None)]
    stale = [mid for mid in have_by_id if mid not in want_by_id]

    if "--stats" in sys.argv:
        print(f"pool {len(want_by_id)} · embedded {len(have_by_id)} · "
              f"pending {len(todo)} · stale {len(stale)}")
        sys.exit(1 if (todo or stale) else 0)

    for mid in stale:
        curl("DELETE", f"{BASE}/rest/v1/member_profile_embeddings?at_member_id=eq.{mid}",
             headers=["Content-Profile: digest"])

    done = 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        vecs = voyage_embed([t for _, t in chunk])
        rows = [{"at_member_id": mid, "profile_text": txt,
                 "embedding": json.dumps(vec), "built_at": "now()"}
                for (mid, txt), vec in zip(chunk, vecs)]
        curl("POST", f"{BASE}/rest/v1/member_profile_embeddings?on_conflict=at_member_id",
             body=rows, headers=["Content-Profile: digest",
                                 "Prefer: resolution=merge-duplicates,return=minimal"])
        done += len(rows)
        print(f"embedded {done}/{len(todo)}")

    print(f"DONE: pool {len(want_by_id)} · embedded now {done} · removed stale {len(stale)}")


if __name__ == "__main__":
    main()
