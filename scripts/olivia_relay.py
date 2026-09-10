"""The one place that knows how to get past Millie's WhatsApp webhook door (#191).

#105 closed the n8n side door on 2026-09-10: `WA Inbound (POST)` on both prod and
staging carries header auth with the `Olivia Relay Secret` credential, and the relay
(`mds-digest-web/src/lib/meta-webhook-config.ts`) sends the value as `X-Olivia-Relay`.
Every local script that posts a simulated WhatsApp payload has to send the same header
or it gets a flat 403 — which is what killed the nightly eval's 2026-09-10 08:30Z run,
220 questions fired, 180 refusals logged, no report written.

The secret is read from the Vault-backed `digest.meta_webhook_config()` at call time and
never stored in a script, so rotating it does not break these tools. Prod and staging
share the credential, so one header covers both targets.
"""

import json
import subprocess

ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"

_SECRET = None


def service_key(env_path=ENV_PATH):
    for line in open(env_path):
        line = line.strip()
        if line.startswith("SUPABASE_SECRET_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"SUPABASE_SECRET_KEY missing from {env_path}")


def relay_secret(key=None):
    """The live X-Olivia-Relay value, or "" when it cannot be read."""
    global _SECRET
    if _SECRET is None:
        _SECRET = ""
        try:
            key = key or service_key()
            p = subprocess.run(
                ["curl", "-sS", "-X", "POST", f"{BASE}/rpc/meta_webhook_config",
                 "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
                 "-H", "Accept-Profile: digest", "-H", "Content-Profile: digest",
                 "-H", "Content-Type: application/json", "-d", "{}"],
                capture_output=True, text=True)
            rows = json.loads(p.stdout) if p.stdout.strip() else []
            row = rows[0] if isinstance(rows, list) and rows else rows
            if isinstance(row, dict):
                _SECRET = row.get("relay_secret") or ""
        except Exception as e:
            print(f"  ⚠️  could not read relay_secret: {e}")
    return _SECRET


def webhook_curl_headers(key=None):
    """curl args for a simulated-inbound POST: content type plus the door's header."""
    args = ["-H", "Content-Type: application/json"]
    sec = relay_secret(key)
    if sec:
        args += ["-H", f"X-Olivia-Relay: {sec}"]
    return args
