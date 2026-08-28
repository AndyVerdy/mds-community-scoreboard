#!/usr/bin/env python3
"""Send the Summit-videos announcement wave. Andy's explicit go: 2026-08-28 ("go").

Sends mds_summit_videos_live_v2 (APPROVED) with each member's 7 pre-generated
single-line params from OLIVIA_ANNOUNCE_SUMMIT_2026-08-27.json. Rate-limited to
~1 send/sec. Each result (wamid or error) is logged to a JSON report — delivery
and read counts come later from the webhook status callbacks.

Never re-runs blindly: a phone that already has a wamid in the report is skipped,
so a crash resume cannot double-send.
"""
import json
import os
import subprocess
import time

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
FILLS = "/Users/Born/Scorecard/OLIVIA_ANNOUNCE_SUMMIT_2026-08-27.json"
REPORT = "/Users/Born/Scorecard/OLIVIA_ANNOUNCE_SUMMIT_2026-08-28_SEND_REPORT.json"
TEMPLATE = "mds_summit_videos_live_v2"


def env():
    e = {}
    for line in open(ENV_PATH):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k] = v.strip().strip('"').strip("'")
    return e


def main():
    e = env()
    tok, pnid = e["META_WA_TOKEN"], e["META_WA_PHONE_NUMBER_ID"]
    fills = json.load(open(FILLS))["fills"]
    done = {}
    if os.path.exists(REPORT):
        done = {r["phone"]: r for r in json.load(open(REPORT))["results"] if r.get("wamid")}
    results = list(done.values())
    for i, f in enumerate(fills):
        if f["phone"] in done:
            continue
        payload = {"messaging_product": "whatsapp", "to": f["phone"], "type": "template",
                   "template": {"name": TEMPLATE, "language": {"code": "en_US"},
                                "components": [{"type": "body",
                                                "parameters": [{"type": "text", "text": p}
                                                               for p in f["params"]]}]}}
        p = subprocess.run(["curl", "-s", "-X", "POST",
                            f"https://graph.facebook.com/v22.0/{pnid}/messages",
                            "-H", f"Authorization: Bearer {tok}",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(payload)], capture_output=True, text=True)
        try:
            r = json.loads(p.stdout)
        except json.JSONDecodeError:
            r = {"error": {"message": p.stdout[:200]}}
        wamid = (r.get("messages") or [{}])[0].get("id")
        results.append({"phone": f["phone"], "at_member_id": f["at_member_id"],
                        "full_name": f["full_name"], "is_speaker": f["is_speaker"],
                        "wamid": wamid, "error": r.get("error")})
        ok = sum(1 for x in results if x.get("wamid"))
        print(f"[{i+1}/{len(fills)}] {f['full_name']}: {'OK' if wamid else 'ERROR ' + str(r.get('error', {}).get('message'))[:80]}  (accepted so far: {ok})", flush=True)
        json.dump({"sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "template": TEMPLATE, "results": results}, open(REPORT, "w"), indent=1)
        time.sleep(1.1)
    ok = sum(1 for x in results if x.get("wamid"))
    err = [x for x in results if not x.get("wamid")]
    print(f"\nDONE: {ok}/{len(fills)} accepted · {len(err)} errors")
    for x in err[:10]:
        print("  ERR", x["full_name"], str(x["error"])[:120])


if __name__ == "__main__":
    main()
