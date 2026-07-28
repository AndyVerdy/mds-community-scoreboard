#!/usr/bin/env python3
"""
One-off backfill: Airtable Summaries.source_messages_json -> Supabase digest.wa_messages

Why this exists: the raw WhatsApp messages have only ever lived in Airtable, squeezed
into a long-text field and sliced at 95,000 chars. digest.wa_messages was modelled for
them and never populated (0 rows). This parses the history out and lands it in Postgres.

Safe by construction:
  - digest.wa_messages PK is the Whapi message id -> upsert, so re-running never duplicates
  - sender_member is FK'd to digest.members.airtable_id -> unresolved phones become NULL
  - the 10 rows whose JSON was truncated mid-structure are salvaged object-by-object
    with a string-aware scanner (braces inside message text do not fool it)

DRY RUN by default. Pass --apply to write.

Env comes from mds-digest-web/.env.local: AIRTABLE_PAT, AIRTABLE_BASE_ID,
AIRTABLE_SUMMARIES_TABLE_ID, SUPABASE_URL, SUPABASE_SECRET_KEY
"""
import json, os, sys, subprocess, collections, datetime

APPLY = "--apply" in sys.argv
SCHEMA = "digest"
ENV_FILE = "/Users/Born/mds-digest-web/.env.local"

def load_env(path):
    """Read KEY=VALUE ourselves. `. .env.local` in bash chokes on unquoted values
    with spaces (e.g. RESEND_FROM=MDS Digest <digest@mds.co>) and silently drops
    everything after it."""
    vals = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip(); v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            vals[k] = v
    return vals

ENV = load_env(ENV_FILE)

def env(name):
    v = ENV.get(name) or os.environ.get(name)
    if not v:
        sys.exit(f"missing env {name}")
    return v

AT_PAT   = env("AIRTABLE_PAT")
AT_BASE  = env("AIRTABLE_BASE_ID")
AT_TABLE = env("AIRTABLE_SUMMARIES_TABLE_ID")
SB_URL   = env("SUPABASE_URL").rstrip("/")
SB_KEY   = env("SUPABASE_SECRET_KEY")

def curl(url, headers, method="GET", body=None):
    cmd = ["curl", "-sS", "-X", method, url]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    if body is not None:
        cmd += ["--data-binary", body]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed: {r.stderr[:400]}")
    return r.stdout

# ---------- string-aware salvage for truncated JSON ----------
def extract_objects(s):
    """Pull every COMPLETE top-level {...} out of a (possibly truncated) JSON array.
    String-aware: braces inside message bodies don't corrupt the depth count."""
    out = []
    depth = 0; start = None; in_str = False; esc = False
    for i, ch in enumerate(s):
        if in_str:
            if esc:            esc = False
            elif ch == "\\":   esc = True
            elif ch == '"':    in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0: start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    try: out.append(json.loads(s[start:i + 1]))
                    except Exception: pass
                    start = None
    return out

# ---------- 1. member map: phone -> members.airtable_id (FK target) ----------
print("loading member map from Supabase ...")
members = json.loads(curl(
    f"{SB_URL}/rest/v1/members?select=airtable_id,phone",
    {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Accept-Profile": SCHEMA},
))
phone_to_member = {m["phone"]: m["airtable_id"] for m in members if m.get("phone") and m.get("airtable_id")}
print(f"  members with phone: {len(phone_to_member)}")

# ---------- 2. read every summary row ----------
print("reading Airtable Summaries ...")
rows = []; offset = ""; page = 0
while True:
    url = (f"https://api.airtable.com/v0/{AT_BASE}/{AT_TABLE}"
           f"?pageSize=100&fields%5B%5D=source_messages_json&fields%5B%5D=date"
           f"&fields%5B%5D=chat_name&fields%5B%5D=chat_id")
    if offset:
        url += f"&offset={offset}"
    d = json.loads(curl(url, {"Authorization": f"Bearer {AT_PAT}"}))
    rows += d.get("records", [])
    offset = d.get("offset", "")
    page += 1
    if not offset or page >= 40:
        break
print(f"  summary rows: {len(rows)}")

# ---------- 3. parse -> message rows ----------
by_id = {}
stats = collections.Counter()
salvaged_rows = []

for r in rows:
    f = r.get("fields", {})
    raw = f.get("source_messages_json")
    if not raw:
        stats["rows_no_json"] += 1
        continue
    try:
        msgs = json.loads(raw); stats["rows_clean"] += 1
    except Exception:
        msgs = extract_objects(raw)
        stats["rows_salvaged"] += 1
        salvaged_rows.append((f.get("date"), f.get("chat_name"), len(msgs)))
    if not isinstance(msgs, list):
        continue
    for m in msgs:
        mid = m.get("id")
        cid = m.get("chat_id") or f.get("chat_id")
        ts  = m.get("timestamp")
        if not mid or not cid or not ts:
            stats["skipped_missing_key_fields"] += 1
            continue
        if mid in by_id:
            stats["dupe_ids_across_rows"] += 1
            continue
        phone = m.get("from")
        body  = (m.get("text") or {}).get("body") if isinstance(m.get("text"), dict) else None
        ctx   = m.get("context") or {}
        by_id[mid] = {
            "id": mid,
            "chat_id": cid,
            "chat_name": f.get("chat_name"),
            "sender_phone": phone,
            "sender_member": phone_to_member.get(phone),   # NULL if unmatched (FK-safe)
            "sent_at": datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat(),
            "type": m.get("type"),
            "text": body,
            "reply_to": ctx.get("quoted_id"),
            "raw": m,
        }
        stats["messages"] += 1
        if not phone:                      stats["no_phone_lid"] += 1
        elif not phone_to_member.get(phone): stats["phone_unmatched"] += 1
        else:                              stats["attributed"] += 1

out = list(by_id.values())
types = collections.Counter(r["type"] for r in out)

print("\n================ DRY RUN REPORT ================")
for k, v in stats.most_common():
    print(f"  {k:28} {v}")
print(f"\n  rows to write: {len(out)}")
print(f"  with text body: {sum(1 for r in out if r['text'])}")
print(f"  attributed to a member: {stats['attributed']} "
      f"({round(100*stats['attributed']/max(stats['messages'],1),1)}%)")
print(f"  date range: {min(r['sent_at'] for r in out)[:10]} -> {max(r['sent_at'] for r in out)[:10]}")
print("\n  types:", dict(types.most_common(6)))
print("\n  salvaged rows (were truncated):")
for d, c, n in sorted(salvaged_rows):
    print(f"    {d}  {c:26} -> {n} messages recovered")

if not APPLY:
    print("\nDRY RUN — nothing written. Re-run with --apply to write.")
    sys.exit(0)

# ---------- 4. upsert ----------
print("\nwriting to Supabase ...")
H = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
     "Content-Type": "application/json", "Content-Profile": SCHEMA,
     "Prefer": "resolution=merge-duplicates,return=minimal"}
B = 500; written = 0
for i in range(0, len(out), B):
    chunk = out[i:i + B]
    resp = curl(f"{SB_URL}/rest/v1/wa_messages", H, "POST", json.dumps(chunk))
    if resp.strip():
        print(f"  batch {i//B}: {resp[:300]}")
    written += len(chunk)
    print(f"  {written}/{len(out)}")
print("done.")
