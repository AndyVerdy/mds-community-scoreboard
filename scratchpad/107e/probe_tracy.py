#!/usr/bin/env python3
"""#107e P1 — Tracy Lin (14133131641), staging, silent SELFTEST wamids.
Adapted from scripts/olivia_selftest.py's fire()/wait_persisted() idiom for one
named phone + a fixed 3-turn sequence instead of the Andy-only question bank.
"""
import json
import subprocess
import sys
import time

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
STAGING_WEBHOOK = "https://mdsco.app.n8n.cloud/webhook/olivia-wa-staging"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
PHONE = "14133131641"  # Tracy Lin
MARK = "wamid.SELFTEST_107e"
TURNS = ["reset", "Who should I meet in Singapore?", "Yes"]


def load_key():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env["SUPABASE_SECRET_KEY"]


def curl(method, url, key, body=None):
    cmd = ["curl", "-s", "-X", method, url, "-H", f"apikey: {key}",
           "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
           "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(p.stdout) if p.stdout.strip() else None
    except json.JSONDecodeError:
        return p.stdout


def fire(text, tag):
    ts = int(time.time())
    wamid = f"{MARK}_{tag}_{ts}"
    payload = {"entry": [{"changes": [{"value": {
        "messaging_product": "whatsapp",
        "metadata": {"display_phone_number": "19453965415", "phone_number_id": "1306956855827812"},
        "contacts": [{"profile": {"name": "Tracy"}, "wa_id": PHONE}],
        "messages": [{"from": PHONE, "id": wamid,
                      "timestamp": str(ts), "type": "text", "text": {"body": text}}]},
        "field": "messages"}]}]}
    p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", STAGING_WEBHOOK,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return p.stdout, wamid, ts


def last_id(key):
    rows = curl("GET", f"{BASE}/olivia_messages?member=eq.recPdhoIIzDnCwr74"
                       f"&order=id.desc&limit=1&select=id", key)
    return rows[0]["id"] if rows else 0


def wait_persisted(key, baseline, timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        rows = curl("GET", f"{BASE}/olivia_messages?member=eq.recPdhoIIzDnCwr74"
                           f"&id=gt.{baseline}&role=eq.olivia&order=id.desc&limit=1&select=id", key)
        if rows:
            return round(time.time() - t0, 1)
    return -1


def main():
    key = load_key()
    print(f"target: {STAGING_WEBHOOK}")
    results = []
    for i, text in enumerate(TURNS):
        baseline = last_id(key)
        code, wamid, ts = fire(text, f"T{i:02d}")
        took = wait_persisted(key, baseline, 180)
        mark = f"{took}s" if took >= 0 else "NOT PERSISTED in 180s"
        print(f"  T{i:02d} [{code}] {mark:>22}  wamid={wamid}  {text[:60]}", flush=True)
        results.append({"i": i, "text": text, "wamid": wamid, "ts": ts, "http": code, "persist_s": took})

    with open("/Users/Born/Scorecard/scratchpad/107e/probe_tracy_results.json", "w") as f:
        json.dump(results, f, indent=2)

    time.sleep(3)
    rows = curl("GET", f"{BASE}/olivia_messages?member=eq.recPdhoIIzDnCwr74"
                f"&order=id.desc&limit=8&select=id,role,route,text", key)
    print("\n=== TRANSCRIPT (newest first) ===")
    for r in rows or []:
        who = "M" if r["role"] == "member" else "O"
        print(f"\n[id={r['id']} {who}·{r.get('route')}] {r['text'][:400]}")


if __name__ == "__main__":
    main()
