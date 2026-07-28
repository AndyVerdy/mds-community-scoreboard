#!/usr/bin/env python3
"""
content_items equivalence harness — proves Olivia's index retrieval returns the same
rows the legacy direct queries did (the "behavior must stay identical" evidence for
the 2026-07-20 rewire, kept runnable).

For each probe member × case it runs BOTH paths over live data:
  legacy — the exact PostgREST query strings the old Plan Request node built against
           digest.summaries / digest.wa_messages (+ the old Build Prompt post-filter
           gate where the legacy pipeline had one), and
  new    — digest.content_search / digest.content_lookup (access enforced in-SQL).

Expectations:
  raw search / verbatim / monthly / question_chat  → EXACT row-set equality.
  digest search / question_general / greeting      → equality when the legacy row cap
       was not binding; when it was, new must be a SUPERSET of the legacy post-gate
       rows and 100% entitled (the old cap wasted slots on unentitled chats — that
       filter-after-fetch defect was killed deliberately, worklist item C).

Usage:  python3 scripts/verify_content_items_equivalence.py [--terms target amazon tiktok]
Exit 0 = all cases hold. Exit 1 = divergence — investigate before trusting the index.
"""
import argparse
import json
import subprocess
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
SEL = "select=airtable_id,chat_name,date,period_type,tl_dr,summary_text,topics,links_shared,msg_count,participant_count"

failures = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def load_key():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_SECRET_KEY"]


KEY = load_key()


def curl_get(path):
    p = subprocess.run(["curl", "-s", f"{BASE}/{path}", "-H", f"apikey: {KEY}",
                        "-H", f"Authorization: Bearer {KEY}", "-H", "Accept-Profile: digest"],
                       capture_output=True, text=True)
    return json.loads(p.stdout)


def rpc(fn, params):
    p = subprocess.run(["curl", "-s", f"{BASE}/rpc/{fn}", "-H", f"apikey: {KEY}",
                        "-H", f"Authorization: Bearer {KEY}", "-H", "Content-Type: application/json",
                        "-H", "Content-Profile: digest", "-d", json.dumps(params)],
                       capture_output=True, text=True)
    return json.loads(p.stdout)


def day(offset):
    return (datetime.now(timezone.utc) - timedelta(days=offset)).strftime("%Y-%m-%d")


def enc(s):
    return urllib.parse.quote(s, safe="")


def legacy_or_clause(terms):
    parts = []
    for t in terms:
        e = enc(t)
        parts += [f'summary_text.ilike."*{e}*"', f'tl_dr.ilike."*{e}*"', f'topics.ilike."*{e}*"']
    return "or=(" + ",".join(parts) + ")"


def run_member(phone, chats, terms_list):
    owned = set(chats)
    label = f"[{phone[:4]}… {len(chats)} chats]"

    for term in terms_list:
        # ---- digest search (legacy cap 80 ungated → post-gate; new gated at query)
        legacy = curl_get(f"summaries?period_type=eq.daily&{legacy_or_clause([term])}&{SEL}&order=date.desc&limit=80")
        legacy_gated = {r["airtable_id"] for r in legacy if r["chat_name"] in owned}
        new = rpc("content_search", {"p_phone": phone, "p_terms": [term],
                                     "p_sources": ["wa_digest"], "p_kinds": ["daily"], "p_limit": 80})
        new_ids = {r["source_id"] for r in new}
        cap_bound = len(legacy) >= 80
        if cap_bound:
            # At the cap, rows tying on the boundary DATE are interchangeable — legacy
            # tie order was arbitrary heap order. Inclusion is only forced strictly
            # above the boundary; there both paths must agree.
            boundary = min(r["occurred_at"][:10] for r in new) if new else ""
            legacy_above = {r["airtable_id"] for r in legacy
                            if r["chat_name"] in owned and r["date"] > boundary}
            check(f"{label} digest search '{term}': new ⊇ legacy post-gate above cap-boundary date",
                  legacy_above <= new_ids, f"missing {legacy_above - new_ids}")
        else:
            check(f"{label} digest search '{term}': exact row-set equality",
                  legacy_gated == new_ids, f"legacy-only {legacy_gated - new_ids}, new-only {new_ids - legacy_gated}")
        unentitled = [r for r in new if r["meta"]["chat_name"] not in owned]
        check(f"{label} digest search '{term}': every returned row entitled", not unentitled)

        # ---- raw search (legacy already at-query gated → exact equality)
        in_list = ",".join('"' + c.replace('"', "") + '"' for c in chats)
        legacy = curl_get("wa_messages?select=id,chat_name&text=not.is.null"
                          f"&or=(text.ilike.*{enc(term)}*)&chat_name=in.({enc(in_list)})"
                          "&order=sent_at.desc&limit=40")
        legacy_ids = {r["id"] for r in legacy}
        new = rpc("content_search", {"p_phone": phone, "p_terms": [term],
                                     "p_sources": ["wa_message"], "p_limit": 40})
        new_ids = {r["source_id"] for r in new}
        check(f"{label} raw search '{term}': exact row-set equality",
              legacy_ids == new_ids, f"legacy-only {legacy_ids - new_ids}, new-only {new_ids - legacy_ids}")

    # ---- verbatim lookup for every owned chat that has a weekly digest
    weekly_chats = {r["chat_name"] for r in curl_get(
        f"summaries?period_type=eq.weekly&select=chat_name&limit=1000") if r["chat_name"] in owned}
    ok_all, mismatch = True, ""
    for chat in sorted(weekly_chats):
        legacy = curl_get(f"summaries?period_type=eq.weekly&chat_name=eq.{enc(chat)}&{SEL}&order=date.desc&limit=1")
        new = rpc("content_lookup", {"p_phone": phone, "p_source": "wa_digest",
                                     "p_kind": "weekly", "p_chat": chat, "p_limit": 1})
        l_id = legacy[0]["airtable_id"] if legacy else None
        n_id = new[0]["source_id"] if new else None
        if l_id != n_id:
            ok_all, mismatch = False, f"{chat}: {l_id} vs {n_id}"
            break
    check(f"{label} verbatim weekly lookup identical across {len(weekly_chats)} owned chats", ok_all, mismatch)

    # ---- monthly window (one busiest owned chat)
    if weekly_chats:
        chat = sorted(weekly_chats)[0]
        legacy = curl_get(f"summaries?period_type=eq.daily&chat_name=eq.{enc(chat)}&date=gte.{day(30)}&{SEL}&order=date.desc&limit=200")
        new = rpc("content_lookup", {"p_phone": phone, "p_source": "wa_digest", "p_kind": "daily",
                                     "p_chat": chat, "p_since": day(30), "p_limit": 200})
        check(f"{label} monthly window '{chat}': exact equality",
              {r["airtable_id"] for r in legacy} == {r["source_id"] for r in new})

    # ---- question_general (legacy cap 400 ungated → post-gate)
    legacy = curl_get(f"summaries?period_type=eq.daily&date=gte.{day(7)}&{SEL}&order=date.desc&limit=400")
    legacy_gated = {r["airtable_id"] for r in legacy if r["chat_name"] in owned}
    new = rpc("content_lookup", {"p_phone": phone, "p_source": "wa_digest", "p_kind": "daily",
                                 "p_since": day(7), "p_limit": 400})
    new_ids = {r["source_id"] for r in new}
    if len(legacy) >= 400:
        check(f"{label} question_general: new ⊇ legacy post-gate (cap binding)", legacy_gated <= new_ids)
    else:
        check(f"{label} question_general: exact equality", legacy_gated == new_ids,
              f"legacy-only {legacy_gated - new_ids}, new-only {new_ids - legacy_gated}")

    # ---- greeting busiest-owned-chat choice
    legacy = curl_get(f"summaries?period_type=eq.daily&date=gte.{day(14)}&select=chat_name,msg_count&order=msg_count.desc&limit=60")
    legacy_first_owned = next((r["chat_name"] for r in legacy if r["chat_name"] in owned), None)
    new = rpc("content_lookup", {"p_phone": phone, "p_source": "wa_digest", "p_kind": "daily",
                                 "p_since": day(14), "p_order_by": "msg_count", "p_limit": 60})
    new_first = new[0]["meta"]["chat_name"] if new else None
    if legacy_first_owned is not None:
        check(f"{label} greeting busiest chat identical", legacy_first_owned == new_first,
              f"{legacy_first_owned} vs {new_first}")
    else:
        check(f"{label} greeting: legacy cap starved owned rows; new still finds one", new_first is not None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", nargs="+", default=["target", "amazon", "tiktok"])
    args = ap.parse_args()

    # Andy + the members with the fewest and median chat counts (real entitlement variety)
    members = curl_get("members?select=phone,channels_present&phone=not.is.null"
                       "&channels_present=not.is.null&order=phone&limit=1000")
    members = [m for m in members if m["channels_present"]]
    by_n = sorted(members, key=lambda m: len(m["channels_present"]))
    probes = {m["phone"]: m["channels_present"] for m in
              [next(m for m in members if m["phone"] == "17866578153"), by_n[0], by_n[len(by_n) // 2]]}

    for phone, chats in probes.items():
        run_member(phone, chats, args.terms)

    print()
    if failures:
        print(f"EQUIVALENCE FAILED — {len(failures)}: {failures}")
        sys.exit(1)
    print("EQUIVALENCE HOLDS — index retrieval matches legacy behavior "
          "(modulo the deliberate filter-after-fetch fix).")
    sys.exit(0)


if __name__ == "__main__":
    main()
