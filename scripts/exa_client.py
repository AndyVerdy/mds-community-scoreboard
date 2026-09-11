#!/usr/bin/env python3
"""#211 — the only module that talks to Exa.

Every response passes through scrub() before a caller sees it, so no email address and no
phone number is ever stored, `raw` retention included (spec AC 9f). Stdlib only; HTTP via curl,
matching scripts/partner_web_crawl.py.

Secrets: /Users/Born/mds-digest-web/.env.local (EXA_API_KEY).
"""
import json
import re
import subprocess

ENV = "/Users/Born/mds-digest-web/.env.local"
BASE = "https://api.exa.ai"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-*]+@[A-Za-z0-9.\-*]+\.[A-Za-z*]{2,}")
# +91 99717 10129 · +1 (619) 555-0142 · 619-555-0142 — seven or more digits with separators
PHONE_RE = re.compile(r"(?<![\w.])\+?\d[\d()\-.– ]{6,}\d(?![\w.])")
CONTACT_KEYS = re.compile(r"(email|phone|mobile|tel|contact_number)", re.I)


def env(name):
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == name:
                return v.strip().strip('"').strip("'")
    raise SystemExit(f"{name} missing from {ENV}")


def _clean_text(s):
    return PHONE_RE.sub("", EMAIL_RE.sub("", s))


def scrub(value):
    """Recursively remove contact data. Dict values under a contact-ish key become None;
    list items that were only contact data are dropped; free text is cleaned in place."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if CONTACT_KEYS.search(k):
                out[k] = [] if isinstance(v, list) else None
            else:
                out[k] = scrub(v)
        return out
    if isinstance(value, list):
        cleaned = [scrub(v) for v in value]
        return [v for v in cleaned if not (isinstance(v, str) and v.strip() == "")]
    if isinstance(value, str):
        return _clean_text(value)
    return value


def _post(path, payload):
    cmd = ["curl", "-sS", "-m", "120", "-X", "POST", f"{BASE}/{path}",
           "-H", f"x-api-key: {env('EXA_API_KEY')}",
           "-H", "Content-Type: application/json",
           "--data-binary", "@-"]
    p = subprocess.run(cmd, input=json.dumps(payload), capture_output=True,
                       text=True, errors="replace")
    if p.returncode != 0:
        raise SystemExit(f"exa {path} curl failed: {p.stderr[:300]}")
    try:
        body = json.loads(p.stdout or "{}")
    except json.JSONDecodeError:
        raise SystemExit(f"exa {path} returned non-JSON: {p.stdout[:300]}")
    if isinstance(body, dict) and body.get("error"):
        raise SystemExit(f"exa {path} error: {str(body['error'])[:300]}")
    return scrub(body)


def search(query, **opts):
    payload = {"query": query}
    payload.update(opts)
    return _post("search", payload)


def contents(urls, max_chars=3500):
    return _post("contents", {"urls": urls, "text": {"maxCharacters": max_chars}})
