#!/usr/bin/env python3
"""#201 — tell the model the two facts the tools now carry (STAGING only).

The SQL half is already live on prod (migrations member_card_brand_201_20260911 and
video_view_count_201_20260911): `video_search` can rank by `p_order=views` and every video row
carries "N views" in strength_note, and `member_card` resolves a BRAND to its owner.

Nothing in the graph knew that, so the model would never ask for it. Three literal edits in
`Answer Seed`:
  1. video_search p_order -> document `views` next to `recent`.
  2. the #56 RANKINGS ARE TOOL FACTS rule -> extend from partners to videos.
  3. member_card description -> say a brand name resolves to its owner.

Literal string replace, never regex: a `$` in an n8n expression is a backreference in re.sub
(reference_n8n_patchnodefield_dollar). Asserts every anchor is unique before writing.
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
STAGING_ID = "bqHstPDi84uOhTCJ"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", "X-N8N-API-KEY: " + KEY,
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


EDITS = [
    # 1. the tool schema — without this the model cannot ask for a view ranking at all
    ("p_order: str('recent = newest first, for last/latest/most-recent asks')",
     "p_order: str('RANKING mode - recent = newest first, for last/latest/most-recent asks; "
     "views = most-watched first, for any most-watched / most-popular / top-N-by-views ask. "
     "Leave p_query EMPTY when you order, and use p_call_type to scope it (e.g. most watched Mogul Calls). "
     "Every row also carries its own view count in strength_note, so you can state the number')"),

    # 2. the standing rule — rankings come from the tool, and that now includes videos
    ("'- RANKINGS ARE TOOL FACTS (#56): any most/top/best-by-metric claim about partners comes ONLY "
     "from a partner_lookup p_order result.",
     "'- RANKINGS ARE TOOL FACTS (#56, extended to videos by #201): any most/top/best-by-metric claim "
     "comes ONLY from a p_order result - partner_lookup p_order for partners, video_search p_order=views "
     "for most-watched/most-popular videos. NEVER rank videos by how engaged they look, by their "
     "description, or by the order rows happened to arrive: call p_order=views and quote the counts "
     "from strength_note. If a view count is absent from every row, say plainly that the library does "
     "not carry one for those rather than implying a ranking."),

    # 3. member_card — a brand name is now a way IN to the person
    ("{ name: 'member_card', description: 'Public profile card for ONE named member",
     "{ name: 'member_card', description: 'Public profile card for ONE member, found by NAME or by the "
     "BRAND they sell under (#201: \"who owns Stylia Beauty\" -> pass p_member=\"Stylia Beauty\" and the "
     "brand owner comes back; brands are public, the exact revenue behind them is never)"),
]


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    seed = next(n for n in nodes if n["name"] == "Answer Seed")
    code = seed["parameters"]["jsCode"]
    before = code
    for old, new in EDITS:
        n = code.count(old)
        if n != 1:
            print(f"ABORT: anchor found {n} times, expected 1:\n  {old[:90]}…", file=sys.stderr)
            return 2
        code = code.replace(old, new)
    if code == before:
        print("nothing changed", file=sys.stderr)
        return 2
    seed["parameters"]["jsCode"] = code
    body = {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
            "settings": wf.get("settings") or {}}
    out = api("PUT", f"/workflows/{STAGING_ID}", body)
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    print(f"Answer Seed: {len(before)} -> {len(code)} chars, {len(EDITS)} edits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
