#!/usr/bin/env python3
"""#26 — Voyage-embed digest.partners_catalog + digest.events_catalog so paraphrased asks
("3PL in Europe", "fulfillment help") find the right partner or event, matching the
embed_videos.py pattern (voyage-3.5-lite, 1024 dims, nulls-only, resumable).

Only public-in-the-app fields are embedded (partner: name/categories/offer/description —
published+public rows are the only ones the RPC ever serves anyway; event: names/type/style/
area/city/date). The vector NEVER widens access: partner_lookup/event_lookup keep their gates,
the embedding only affects recall + rank inside the gated row set. Re-embed on change is
automatic: BEFORE UPDATE triggers null the embedding when source text changes (migration
partners_events_embedding_columns) and this script picks up the nulls.

  python3 embed_partners_events.py                # embed rows missing an embedding
  python3 embed_partners_events.py --all          # rebuild every row
  python3 embed_partners_events.py --query "..."  # print one query embedding as JSON (for probes)
"""
import argparse
import json
import subprocess

ENV = "/Users/Born/mds-digest-web/.env.local"
SB = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
VOYAGE = "https://api.voyageai.com/v1/embeddings"
MODEL = "voyage-3.5-lite"
DIM = 1024
BATCH = 100


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


def embed(texts, vkey, input_type="document"):
    body = {"model": MODEL, "input": texts, "input_type": input_type, "output_dimension": DIM}
    p = subprocess.run(["curl", "-sS", "-m", "120", VOYAGE,
                        "-H", "Authorization: Bearer " + vkey,
                        "-H", "Content-Type: application/json", "--data-binary", "@-"],
                       input=json.dumps(body), capture_output=True, text=True)
    d = json.loads(p.stdout)
    if "data" not in d:
        raise RuntimeError("voyage error: " + p.stdout[:300])
    return [row["embedding"] for row in sorted(d["data"], key=lambda r: r["index"])]


def partner_text(r):
    parts = [r.get("name") or ""]
    cats = r.get("category_names") or []
    if cats:
        parts.append(" ".join(str(c) for c in cats if c))
    if r.get("offer_value"):
        parts.append(str(r["offer_value"])[:600])
    if r.get("description_text"):
        parts.append(str(r["description_text"])[:2500])
    # #160: what the partner says on its OWN site (summary · services · pricing) joins the vector
    # text, so a paraphrased need ("VAT returns in the UK", "fractional CFO") finds the partner
    # whose directory blurb never used those words. Partner-stated text only shapes RECALL and
    # rank inside the gated row set; it never widens access.
    wp = r.get("partner_web_profile")
    if isinstance(wp, list):
        wp = wp[0] if wp else None
    if wp and wp.get("crawl_status") == "ok":
        if wp.get("summary"):
            parts.append(str(wp["summary"])[:1200])
        if wp.get("services"):
            parts.append("Services: " + "; ".join(str(x) for x in wp["services"] if x)[:800])
        if wp.get("pricing"):
            parts.append("Pricing: " + str(wp["pricing"])[:300])
    return " \n".join(p for p in parts if p).strip()[:8000]


def event_text(r):
    parts = [r.get("app_title") or r.get("name") or ""]
    if r.get("name") and r.get("app_title") and r["name"] != r["app_title"]:
        parts.append(r["name"])
    for k in ("event_type", "style", "chapter_hint", "chapter_area",
              "location", "city_state", "app_city"):
        if r.get(k):
            parts.append(str(r[k]))
    start = r.get("app_starts_at") or r.get("start_at") or ""
    if start:
        parts.append(str(start)[:7])          # YYYY-MM: "summit march 2026" asks
    return " \n".join(p for p in parts if p).strip()[:4000]


def run_table(table, pk, cols, textfn, key, vkey, do_all):
    flt = "" if do_all else "&embedding=is.null"
    rows = sb("GET", f"{table}?select={cols}{flt}&limit=3000", key)
    if not isinstance(rows, list) or not rows:
        print(f"{table}: nothing to embed")
        return
    print(f"{table}: embedding {len(rows)} rows")
    done = 0
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        vecs = embed([textfn(r) for r in chunk], vkey)
        # PATCH not upsert — an UPDATE touches only the embedding (embed_videos.py lesson)
        for r, vec in zip(chunk, vecs):
            sb("PATCH", f"{table}?{pk}=eq.{r[pk]}", key, {"embedding": vec})
        done += len(chunk)
        print(f"  …{done} embedded")
    print(f"{table}: done, {done} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="re-embed every row, not just missing ones")
    ap.add_argument("--query", help="print ONE query embedding as JSON and exit (probe helper)")
    a = ap.parse_args()
    e = env()
    key, vkey = e["SUPABASE_SECRET_KEY"], e["VOYAGE_API_KEY"]

    if a.query:
        print(json.dumps(embed([a.query], vkey, input_type="query")[0]))
        return

    run_table("partners_catalog", "partner_id",
              "partner_id,name,category_names,offer_value,description_text,"
              "partner_web_profile(summary,services,pricing,crawl_status)",
              partner_text, key, vkey, a.all)
    run_table("events_catalog", "at_record_id",
              "at_record_id,name,app_title,event_type,style,chapter_hint,chapter_area,"
              "location,city_state,app_city,start_at,app_starts_at",
              event_text, key, vkey, a.all)


if __name__ == "__main__":
    main()
