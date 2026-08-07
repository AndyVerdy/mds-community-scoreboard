#!/usr/bin/env python3
"""Verify the Zoom Server-to-Server OAuth app: token exchange, granted scopes,
one participants report, and the upcoming-meetings read for the Contact MDS host.

Reads credentials from .env.zoom (gitignored). Prints only non-secret results.
"""
import base64
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ssl_ctx():
    """python.org builds ship no root certs on macOS — fall back to the system bundle."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        for pem in ("/etc/ssl/cert.pem", "/usr/local/etc/openssl/cert.pem"):
            if os.path.exists(pem):
                return ssl.create_default_context(cafile=pem)
        return ssl.create_default_context()


CTX = ssl_ctx()


def load_env(path=os.path.join(ROOT, ".env.zoom")):
    env = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def api(url, token, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:300]}


def main():
    env = load_env()
    basic = base64.b64encode(
        f"{env['ZOOM_CLIENT_ID']}:{env['ZOOM_CLIENT_SECRET']}".encode()
    ).decode()
    token_url = (
        "https://zoom.us/oauth/token?grant_type=account_credentials&account_id="
        + urllib.parse.quote(env["ZOOM_ACCOUNT_ID"])
    )
    req = urllib.request.Request(
        token_url, data=b"", headers={"Authorization": "Basic " + basic}
    )
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            tok = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print("TOKEN FAILED", e.code, e.read().decode()[:300])
        sys.exit(1)

    token = tok["access_token"]
    print(f"TOKEN OK  expires_in={tok.get('expires_in')}s")
    print("SCOPES:", " ".join(sorted(tok.get("scope", "").split())) or "(none listed)")

    users = api("https://api.zoom.us/v2/users", token, {"page_size": 30})
    if "_error" in users:
        print("USERS:", users["_error"], users["_body"])
    else:
        print("USERS:", users.get("total_records"), "->",
              ", ".join(f"{u.get('email')}({u.get('id')})" for u in users.get("users", [])[:8]))
        host = next((u for u in users.get("users", [])
                     if u.get("email", "").startswith("contact@")), None)
        if host:
            up = api(f"https://api.zoom.us/v2/users/{host['id']}/upcoming_meetings",
                     token, {"page_size": 10})
            if "_error" in up:
                print("UPCOMING:", up["_error"], up["_body"])
            else:
                print("UPCOMING:", up.get("total_records"), "->",
                      "; ".join(f"{m.get('start_time','?')} {m.get('topic','?')}"
                                for m in up.get("meetings", [])[:6]))

    # participants report for a known mogul call (25 Mar 2026); UUID needs double-encoding
    uuid = "xJVEpOqeT36qIZjY16hYlQ=="
    enc = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
    rep = api(f"https://api.zoom.us/v2/report/meetings/{enc}/participants",
              token, {"page_size": 300})
    if "_error" in rep:
        print("REPORT/participants:", rep["_error"], rep["_body"])
    else:
        ps = rep.get("participants", [])
        print("REPORT/participants:", rep.get("total_records"), "rows for 2026-03-25 mogul call")
        for p in ps[:5]:
            print("   ", p.get("name"), "|", p.get("user_email") or "-", "|",
                  p.get("duration"), "min")

    # fallback: Dashboard API (scope dashboard:read:list_meeting_participants:admin IS granted)
    dash = api(f"https://api.zoom.us/v2/metrics/meetings/{enc}/participants",
               token, {"type": "past", "page_size": 300})
    if "_error" in dash:
        print("DASHBOARD/participants:", dash["_error"], dash["_body"])
    else:
        ps = dash.get("participants", [])
        print("DASHBOARD/participants:", dash.get("total_records"), "rows for 2026-03-25 mogul call")
        for p in ps[:5]:
            print("   ", p.get("user_name"), "|", p.get("email") or "-", "|",
                  p.get("duration"), "s |", p.get("join_time"))

    # how far back does the dashboard reach? probe a few windows
    for label, frm, to in (("last 30d", "2026-07-06", "2026-08-05"),
                           ("Mar 2026", "2026-03-01", "2026-03-31"),
                           ("Aug 2025", "2025-08-01", "2025-08-31"),
                           ("Aug 2024", "2024-08-01", "2024-08-31")):
        m = api("https://api.zoom.us/v2/metrics/meetings", token,
                {"type": "past", "from": frm, "to": to, "page_size": 1})
        if "_error" in m:
            print(f"DASHBOARD/meetings {label}:", m["_error"], m["_body"][:120])
        else:
            print(f"DASHBOARD/meetings {label}: total={m.get('total_records')}")


if __name__ == "__main__":
    main()
