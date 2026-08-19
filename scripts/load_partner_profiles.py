#!/usr/bin/env python3
"""#88 — load event partner profiles from the Airtable "APP" view CSV.

  python3 scripts/load_partner_profiles.py "~/Downloads/Partners-MDS Summit  Singapore '26 - APP.csv" [--dry-run]

One row per partner COMPANY into event.partner_profiles (richest value wins when a
company spans several people-rows), one row per PERSON into event.partner_people.
Categories are enriched from the raw view dump when present (the CSV omits them).
Idempotent: upserts on (event_id, company) and (partner_id, full_name).

The GroupOS export carries no partners yet (24h behind, and Singapore's partner set
was never in it) — this CSV is Andy's direct feed (2026-08-18). When the export
gains partner attendees, linkage joins by email; this loader stays the profile
source until then. No passcodes, QR links, or form URLs — credentials and ops
fields never enter the warehouse (ticket AC).
"""
import argparse, csv, json, os, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
VIEW_DUMP = ("/private/tmp/claude-501/-Users-Born-Scorecard/"
             "844c462e-8bca-4ba2-b35c-5be36934d855/scratchpad/at_partners_view.json")


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


def supa(method, path, key, body=None, prefer=None):
    cmd = ["curl", "-s", "-m", "45", "-X", method, f"{SUPA}/{path}",
           "-H", f"Authorization: Bearer {key}", "-H", f"apikey: {key}",
           "-H", "Accept-Profile: event", "-H", "Content-Profile: event",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out or "[]")
    except json.JSONDecodeError:
        return {"_raw": out[:300]}


def clean(s):
    s = (s or "").strip()
    return s if s and s.upper() not in ("N/A", "NA", "/", "-") else None


def parse_contact(block):
    """'Name\nTitle\nphone\nemail' in any order — name is line 1, email/phone by shape."""
    block = clean(block) or ""
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    name = lines[0].strip(" <>") if lines else None
    if name and "@" in name:  # 'Name <email>' single-line form
        name = re.sub(r"<.*", "", lines[0]).strip()
    m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", block)
    email = m.group(0) if m else None
    m = re.search(r"\+?\d[\d ()-]{6,}\d", block)
    phone = m.group(0).strip() if m else None
    return name, email, phone


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    key = env("SUPABASE_SECRET_KEY")

    ev = supa("GET", "events?select=id,title&limit=2", key)
    assert isinstance(ev, list) and len(ev) == 1, f"expected exactly 1 event.events row, got {ev}"
    event_id = ev[0]["id"]
    print(f"event: {ev[0].get('title')} ({event_id})")

    cats = {}
    if os.path.exists(VIEW_DUMP):
        for r in json.load(open(VIEW_DUMP)):
            f = r.get("fields", {})
            for nm in (f.get("Full Name."), [f.get("Full Name")]):
                for n in (nm or []):
                    if n and f.get("Associated Categories (from Link to Master Partners Table)"):
                        cats[n.strip()] = f["Associated Categories (from Link to Master Partners Table)"]

    companies, people = {}, []
    with open(os.path.expanduser(args.path), newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            company = clean(row.get("Link to Master Partners Table"))
            person = clean(row.get("Full Name"))
            if not company or not person:
                continue
            c = companies.setdefault(company, {})
            for col, dest in [("Brief Company Description", "description"),
                              ("Company Snapshot", "snapshot"),
                              ("Current MDS Offer", "mds_offer"),
                              ("Event Unique Offer", "event_offer"),
                              ("Offer Instructions", "offer_instructions")]:
                v = clean(row.get(col))
                if v and len(v) > len(c.get(dest) or ""):
                    c[dest] = v
            if clean(row.get("Partner Main Contact")) and not c.get("_contact"):
                c["_contact"] = row["Partner Main Contact"]
            if person in cats and not c.get("categories"):
                c["categories"] = cats[person]
            people.append({"company": company, "full_name": person,
                           "email": clean(row.get("Email of Attendees")),
                           "role_title": clean(row.get("Role/ Title")),
                           "ticket_type": clean(row.get("Partner Ticket"))})

    assert len(companies) >= 8, f"only {len(companies)} companies parsed — wrong file? refusing"
    print(f"parsed: {len(companies)} companies · {len(people)} people")

    # Same partner in the year-round directory gets LINKED (Andy 2026-08-19) —
    # matched on normalized name (suffixes like ".Ai"/" Ai"/legal tails dropped);
    # Live + most-claimed wins when the catalog holds duplicates. NULL is fine:
    # an event can bring a partner the directory has never seen.
    def norm(s):
        s = re.sub(r"\b(a\.?i\.?|pte\.?|ltd\.?|inc\.?|llc)\b\.?", "", (s or "").lower())
        return re.sub(r"[^a-z0-9]", "", s)
    catalog = supa("GET", "partners_catalog?select=partner_id,name,status,claim_count"
                          "&limit=1000", key)
    # partners_catalog lives in the digest schema — reuse the REST helper with an override
    if isinstance(catalog, dict):
        catalog = []
    if not catalog:
        cmd_out = subprocess.run(
            ["curl", "-s", f"{SUPA}/partners_catalog?select=partner_id,name,status,claim_count&limit=1000",
             "-H", f"Authorization: Bearer {key}", "-H", f"apikey: {key}",
             "-H", "Accept-Profile: digest"], capture_output=True, text=True).stdout
        try:
            catalog = json.loads(cmd_out or "[]")
        except json.JSONDecodeError:
            catalog = []
    by_norm = {}
    for p in sorted(catalog, key=lambda p: ((p.get("status") == "Live"), p.get("claim_count") or 0), reverse=True):
        by_norm.setdefault(norm(p["name"]), p["partner_id"])

    prof_rows = []
    for company, c in sorted(companies.items()):
        name, email, phone = parse_contact(c.pop("_contact", None))
        prof_rows.append({"event_id": event_id, "company": company,
                          "description": c.get("description"), "snapshot": c.get("snapshot"),
                          "mds_offer": c.get("mds_offer"), "event_offer": c.get("event_offer"),
                          "offer_instructions": c.get("offer_instructions"),
                          "contact_name": name, "contact_email": email, "contact_phone": phone,
                          "categories": c.get("categories"),
                          "directory_partner_id": by_norm.get(norm(company))})
    if args.dry_run:
        for p in prof_rows:
            print(f"  {p['company']}: offer={'Y' if p['mds_offer'] or p['event_offer'] else '-'} "
                  f"contact={p['contact_name'] or '-'} cats={p['categories'] or '-'}")
        print("(dry run, nothing written)")
        return

    r = supa("POST", "partner_profiles?on_conflict=event_id,company", key, prof_rows,
             prefer="resolution=merge-duplicates,return=minimal")
    assert not isinstance(r, dict) or not r.get("_raw"), f"profile upsert failed: {r}"
    ids = supa("GET", f"partner_profiles?select=id,company&event_id=eq.{event_id}&limit=200", key)
    by_company = {row["company"]: row["id"] for row in ids}
    ppl_rows = [{"partner_id": by_company[p["company"]], **{k: v for k, v in p.items() if k != "company"}}
                for p in people if p["company"] in by_company]
    r = supa("POST", "partner_people?on_conflict=partner_id,full_name", key, ppl_rows,
             prefer="resolution=merge-duplicates,return=minimal")
    assert not isinstance(r, dict) or not r.get("_raw"), f"people upsert failed: {r}"

    n_prof = supa("GET", f"partner_profiles?select=id&event_id=eq.{event_id}&limit=200", key)
    n_ppl = supa("GET", "partner_people?select=id&limit=500", key)
    print(f"loaded: {len(n_prof)} partner_profiles · {len(n_ppl)} partner_people")


if __name__ == "__main__":
    main()
