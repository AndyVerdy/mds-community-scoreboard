#!/usr/bin/env python3
"""
Derive ONE canonical, countable niche set per member  (#5, 2026-07-31).

THE PROBLEM. Airtable holds eight niche/category fields and none of them can be counted:
  Members.Category / Members.Main Niche  multipleLookupValues off the application form
  Forms.Category                         19 choices = 10 real values + punctuation duplicates
  Forms.Main Niche                       singleLineText, written by Application v3 from a
                                         Typeform answer named `main_niche_open_text`
  Members.Categories                     NOT niches at all — skills (Accounting/Taxes, FB Ads)
  Members.Niche-WA / Category NEW        same 10 values again, dashes / subset
  Members.Niche Top Selection            a DIFFERENT, finer 12-value list
  Members.Niche Status                   a TRUE/FALSE flag
Application v3 no longer writes any controlled category, so the countable field decays as new
members join, while Main Niche — the field that IS maintained — is free text (334 distinct values
across 466 members).

THE FIX. Map every source into ONE vocabulary and store the result multi-valued.

PRECEDENCE (Andy): Main Niche first. It is what the member calls their MAIN niche, and it is the
only source that can split the coarse "Health/ Beauty/ & Supplements (Consumables)" bucket into
Supplements vs Beauty vs Health — which is why "how many members in Supplements" was unanswerable.
Controlled fields then ADD their values (a member sells in several categories; all are kept).

VOCABULARY. MDS's own "Niche Top Selection" (12), plus the two it omits that "Category NEW" covers.
Not invented here — extended from what MDS already uses.

Idempotent: rebuilds each member's rows from scratch, so re-running is safe and cheap.
Usage:  python3 scripts/olivia_derive_niches.py [--limit N] [--dry-run]
"""
import argparse
import json
import subprocess
import sys
import time

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
MODEL = "claude-haiku-4-5-20251001"
BATCH = 40
ACTIVE = ("Current Member", "New Member", "Current Member- Not Renewing")

CANON = [
    "Supplements", "Beauty", "Health and Personal Care", "Food & Beverage",
    "Home & Kitchen", "Housewares & Office", "Pets", "Baby & Kids",
    "Clothing & Apparel", "Electronics & Accessories", "Toys & Games",
    "Sports & Outdoors", "Automotive & Home Improvement", "Other",
]

# Controlled values map deterministically — no model needed, no drift. Keyed on a squashed form
# so every punctuation variant ("Health/ Beauty/ &", "Health/Beauty/", "Health - Beauty - &")
# collapses to the same entry.
def squash(s: str) -> str:
    return "".join(ch for ch in str(s).lower() if ch.isalnum())


CONTROLLED = {
    "artscraftstoysgames": ["Toys & Games"],
    "automotive": ["Automotive & Home Improvement"],
    "baby": ["Baby & Kids"],
    "babykids": ["Baby & Kids"],
    "clothingaccessories": ["Clothing & Apparel"],
    "clothingapparel": ["Clothing & Apparel"],
    "consumerelectronics": ["Electronics & Accessories"],
    "electronicsaccessories": ["Electronics & Accessories"],
    # the coarse bucket: kept as BOTH so a member is findable either way, and Main Niche
    # overrides it as primary when the member said which one they actually are
    "healthbeautysupplementsconsumables": ["Health and Personal Care", "Beauty"],
    "healthandpersonalcare": ["Health and Personal Care"],
    "beauty": ["Beauty"],
    "supplements": ["Supplements"],
    "wellness": ["Health and Personal Care"],
    "personalcare": ["Health and Personal Care"],
    "foodbeverageandotherconsumablesnonsupplement": ["Food & Beverage"],
    "foodbeverageotherconsumablesnonsupplement": ["Food & Beverage"],
    "housewaresofficepetproductsnonconsumable": ["Housewares & Office", "Pets"],
    "homekitchen": ["Home & Kitchen"],
    "pets": ["Pets"],
    "pet": ["Pets"],
    "toys": ["Toys & Games"],
    "toysgames": ["Toys & Games"],
    "sportsoutdoorsandotherhealthnonconsumable": ["Sports & Outdoors"],
    "sportsoutdoorsotherhealthnonconsumable": ["Sports & Outdoors"],
    "sportsoutdoors": ["Sports & Outdoors"],
    "oversizedtoolshomeimprovementotherpatiooutdoor": ["Automotive & Home Improvement"],
    "automotivehomeimprovement": ["Automotive & Home Improvement"],
    "womensfashion": ["Clothing & Apparel"],
    "resale": ["Other"],
    "logistics": ["Other"],
    "advertisingtechnology": ["Other"],
    "ecommercecontentcreation": ["Other"],
    "anti3pl": ["Other"],
}
DROP = {"na", "nadefault", "hello", "auto", "", "?"}   # junk choices in Niche-WA


def load_env():
    env = {}
    for line in open(ENV_PATH):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip('"').strip("'")
    return env


def curl_json(url, key, method="GET", body=None, headers=None):
    cmd = ["curl", "-s", "--max-time", "120", "-X", method, url, "-H", f"apikey: {key}",
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
        sys.exit(f"non-JSON from {url}: {r.stdout[:300]}")


def paged(url, key, page=1000):
    """PostgREST caps responses at 1000 rows whatever `limit` says — always page (#25)."""
    out, off = [], 0
    while off < 100 * page:
        b = curl_json(f"{url}&limit={page}&offset={off}", key)
        out.extend(b)
        if len(b) < page:
            break
        off += page
    return out


def anthropic(key, system, user, tries=3):
    """⚠️ ALWAYS bounded. This call had NO timeout until 2026-08-05, and on 2026-08-03 it hung
    mid-batch: the nightly job sat on batch 2/10 for 16,203s (4.5 HOURS), never finished, and
    derive_niches went stale for two days while the alarm repeated every 30 minutes. curl with no
    --max-time waits forever, so one wedged connection = a dead nightly job. Bounded + retried:
    a transient now costs 120s and a retry instead of the whole run."""
    body = {"model": MODEL, "max_tokens": 4000, "thinking": {"type": "disabled"},
            "system": system, "messages": [{"role": "user", "content": user}]}
    last = ""
    for attempt in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "120",
                            "https://api.anthropic.com/v1/messages",
                            "-H", f"x-api-key: {key}", "-H", "anthropic-version: 2023-06-01",
                            "-H", "content-type: application/json", "--data-binary", "@-"],
                           input=json.dumps(body), capture_output=True, text=True)
        if r.returncode != 0:                      # 28 = timed out
            last = f"curl exit {r.returncode}"
        else:
            try:
                resp = json.loads(r.stdout)
            except json.JSONDecodeError:
                resp, last = {}, f"non-JSON: {r.stdout[:200]}"
            if "content" in resp:
                return "".join(c.get("text", "") for c in resp["content"])
            last = last or f"api error: {r.stdout[:200]}"
        if attempt < tries - 1:
            print(f"  anthropic retry {attempt + 1}/{tries - 1} after {last}")
            time.sleep(3 * (attempt + 1))
    sys.exit(f"anthropic failed after {tries} tries: {last}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    env = load_env()
    sb, ak = env["SUPABASE_SECRET_KEY"], env["CENTURION_ANTHROPIC_API_KEY"]

    rows = paged(f"{BASE}/member_attributes?select=at_member_id,membership_status,categories,main_niche"
                 f"&order=at_member_id.asc", sb)
    members = [r for r in rows if r.get("membership_status") in ACTIVE]
    if a.limit:
        members = members[:a.limit]
    print(f"{len(members)} active members")

    # 1) controlled values -> canonical, deterministic
    derived = {}          # at_member_id -> {niche: (source, raw)}
    need_llm = []         # (at_member_id, main_niche_text)
    for m in members:
        mid = m["at_member_id"]
        got = {}
        for raw in (m.get("categories") or []):
            for c in CONTROLLED.get(squash(raw), []):
                got.setdefault(c, ("category", raw))
        mn = (m.get("main_niche") or "").strip()
        if mn:
            hit = CONTROLLED.get(squash(mn))
            if hit:
                for c in hit:
                    got[c] = ("main_niche", mn)      # stated by the member
            elif squash(mn) not in DROP:
                need_llm.append((mid, mn))
        derived[mid] = got

    print(f"{len(need_llm)} free-text Main Niche values need classifying")
    if a.dry_run:
        return

    # 2) free-text Main Niche -> canonical, via the model (the only part that needs judgement)
    # 21.8% of members (104 of 477 on 2026-07-31) name SEVERAL niches in a field called "Main
    # Niche" — "Supplements, Board Games, Pets". Andy's ruling: if they typed three, all three
    # ARE their main niche — treat them equally. We do NOT rank by the order they happened to
    # type, because the member gave no signal that the first matters more. So every stated niche
    # is captured and every one is flagged is_main_niche; there is no single "primary".
    system = ("Map each MDS member's self-described product niche(s) to labels from the LIST. "
              "They may name SEVERAL — return EVERY one they mention, deduplicated, with no "
              "ranking. If they name only one, return one. Use Other only when nothing fits. "
              "Output ONLY minified JSON: "
              '{"m":[{"id":"<id>","niches":["<label>",...]}]} with one entry per id given.\n'
              "LIST: " + json.dumps(CANON))
    for i in range(0, len(need_llm), BATCH):
        chunk = need_llm[i:i + BATCH]
        out = anthropic(ak, system,
                        json.dumps([{"id": mid, "niche": t[:120]} for mid, t in chunk]))
        try:
            got = json.loads(out[out.index("{"):out.rindex("}") + 1])["m"]
        except Exception:
            print(f"  batch {i//BATCH+1}: unparseable, skipped")
            continue
        raw_by_id = dict(chunk)
        for g in got:
            mid = g.get("id")
            if mid not in derived:
                continue
            for niche in [n for n in (g.get("niches") or []) if n in CANON]:
                derived[mid][niche] = ("main_niche", raw_by_id.get(mid, ""))
        print(f"  batch {i//BATCH+1}/{(len(need_llm)+BATCH-1)//BATCH} classified")

    # 3) rebuild rows. is_primary = the Main-Niche-sourced value (Andy's precedence); when the
    #    member never gave one, no row is primary rather than guessing which category is "main".
    payload = []
    for mid, got in derived.items():
        # is_main_niche = the member stated it themselves. Several can be true and they rank
        # equally; a member who never stated one simply has none flagged.
        for niche, (src, raw) in sorted(got.items()):
            payload.append({"at_member_id": mid, "niche": niche,
                            "is_main_niche": (src == "main_niche"),
                            "source": src, "raw_value": (raw or "")[:200]})
    print(f"writing {len(payload)} member-niche rows…")
    ids = list(derived.keys())
    for i in range(0, len(ids), 200):          # clear then insert, so removals propagate
        batch = ",".join(f'"{x}"' for x in ids[i:i + 200])
        curl_json(f"{BASE}/member_niches?at_member_id=in.({batch})", sb, method="DELETE",
                  headers=["Prefer: return=minimal"])
    for i in range(0, len(payload), 400):
        curl_json(f"{BASE}/member_niches", sb, method="POST", body=payload[i:i + 400],
                  headers=["Prefer: resolution=merge-duplicates,return=minimal"])
    print("done")


if __name__ == "__main__":
    main()
