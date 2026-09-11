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

# Match obfuscated emails: jsmith(at)example(dot)com, jsmith[at]example[dot]com, jsmith at example dot com
EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-*]+(?:@|\(at\)|\[at\]|\s+at\s+)[A-Za-z0-9.\-*]+(?:\.|\(dot\)|\[dot\]|\s+dot\s+)[A-Za-z*]{2,}",
    re.IGNORECASE
)

# URLs and ISO-8601 dates/timestamps to protect
URL_RE = re.compile(r"https?://[^\s]+|ftp://[^\s]+")
ISO_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?")

# Phone pattern: leading + OR 9+ digits; add asterisk to character class
PHONE_RE = re.compile(r"\+[\d\s()\-.–]*\d(?![\w.])|(?<![.\w])[\d*][\d()\-.–* ]{6,}[\d*](?![\w.])")

# Contact keys: expanded list including cell, fax, msisdn, whatsapp, and camelCase variants
CONTACT_KEYS = re.compile(
    r"(email|phone|mobile|tel|cell|fax|msisdn|whatsapp|contact[_\s]?number)",
    re.IGNORECASE
)


def env(name):
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == name:
                return v.strip().strip('"').strip("'")
    raise SystemExit(f"{name} missing from {ENV}")


def _protect_and_restore(text):
    """Protect URLs and ISO-8601 dates, apply scrubbing, restore."""
    placeholders = {}

    # Protect URLs
    for match in URL_RE.finditer(text):
        key = f"__URL_{len(placeholders)}__"
        placeholders[key] = match.group(0)

    # Protect ISO-8601 dates
    for match in ISO_DATETIME_RE.finditer(text):
        key = f"__DATE_{len(placeholders)}__"
        placeholders[key] = match.group(0)

    # Apply replacements
    for placeholder, original in placeholders.items():
        text = text.replace(original, placeholder)

    # Remove emails and phones
    text = EMAIL_RE.sub("", text)
    text = PHONE_RE.sub("", text)

    # Restore
    for placeholder, original in placeholders.items():
        text = text.replace(placeholder, original)

    return text


def _clean_text(s):
    """Clean text of contact data while preserving URLs and dates."""
    return _protect_and_restore(s)


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
           "-w", "\n%{http_code}",
           "--data-binary", "@-"]
    p = subprocess.run(cmd, input=json.dumps(payload), capture_output=True,
                       text=True, errors="replace")
    if p.returncode != 0:
        raise SystemExit(f"exa {path} curl failed: {p.stderr[:300]}")

    # Split response and status code
    parts = p.stdout.rsplit('\n', 1)
    if len(parts) != 2:
        raise SystemExit(f"exa {path} returned malformed response: {p.stdout[:300]}")

    body_str, status_str = parts
    try:
        status_code = int(status_str.strip())
    except ValueError:
        raise SystemExit(f"exa {path} invalid status code: {status_str[:100]}")

    if status_code < 200 or status_code >= 300:
        raise SystemExit(f"exa {path} HTTP {status_code}")

    try:
        body = json.loads(body_str or "{}")
    except json.JSONDecodeError:
        raise SystemExit(f"exa {path} returned non-JSON: {body_str[:300]}")
    if isinstance(body, dict) and body.get("error"):
        raise SystemExit(f"exa {path} error: {str(body['error'])[:300]}")
    return scrub(body)


def search(query, **opts):
    payload = {"query": query}
    payload.update(opts)
    return _post("search", payload)


def contents(urls, max_chars=3500):
    return _post("contents", {"urls": urls, "text": {"maxCharacters": max_chars}})
