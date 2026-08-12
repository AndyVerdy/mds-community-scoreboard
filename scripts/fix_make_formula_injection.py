#!/usr/bin/env python3
"""#63 — close the Airtable-formula injection in the Make member-match modules.

Both form->Airtable scenarios build the member search with string interpolation:

    LOWER({Preferred Email})=LOWER("{{2.Email}}")

The email is typed by the person filling the form, so a value containing a double
quote breaks out of the string literal. Proven read-only against the live base:
the payload  " & {Preferred Email} & "  produces an always-true formula and returns
a member record, which would link the submission -- and its revenue figures -- to
somebody else.

The fix strips the only two characters that can terminate or escape the literal
(" and \\) before interpolation. \\x22 / \\x5C are used instead of the characters
themselves so the pattern cannot upset Make's own expression parser:

    LOWER({Preferred Email})=LOWER("{{replace(2.Email; /[\\x22\\x5C]/g; "")}}")

Everything else a crafted value might contain -- braces, parentheses, ampersands --
is inert inside a string literal.

Usage:
    python3 scripts/fix_make_formula_injection.py            # dry run, prints the diff
    python3 scripts/fix_make_formula_injection.py --apply    # writes it, then reads it back
"""

import argparse
import json
import os
import pathlib
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import certifi

# Verify TLS against certifi's bundle — this interpreter has no system issuer chain,
# and turning verification off is exactly the defect #70's code review found.
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

API = "https://us1.make.com/api/v2"
SCENARIOS = {
    4860042: "MDS Annual Census 2026 -> Airtable",
    4784286: "MDS New Member Application v3 -> Airtable",
}

VULNERABLE = 'LOWER({Preferred Email})=LOWER("{{2.Email}}")'
FIXED = 'LOWER({Preferred Email})=LOWER("{{replace(2.Email; /[\\x22\\x5C]/g; "")}}")'

BACKUP_DIR = pathlib.Path(__file__).parent / "make_backups"


def token() -> str:
    env = pathlib.Path("/Users/Born/mds-digest-web/.env.local")
    for line in env.read_text().splitlines():
        if line.startswith("MAKE_API_TOKEN="):
            return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("MAKE_API_TOKEN not found in mds-digest-web/.env.local")


def call(method: str, path: str, tok: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method)
    req.add_header("Authorization", f"Token {tok}")
    # Make's edge rejects the default urllib agent with a Cloudflare 1010.
    req.add_header("User-Agent", "curl/8.7.1")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        sys.exit(f"{method} {path} -> {exc.code}: {exc.read().decode()[:500]}")


def patch_flow(flow: list, hits: list, path: str = "") -> None:
    """Rewrite every vulnerable formula in place, recursing through router routes."""
    for module in flow:
        where = f"{path}/{module.get('id')}"
        mapper = module.get("mapper") or {}
        formula = mapper.get("formula")
        if isinstance(formula, str) and formula == VULNERABLE:
            mapper["formula"] = FIXED
            hits.append(where)
        elif isinstance(formula, str) and "{{" in formula and "Email" in formula:
            hits.append(f"{where} UNRECOGNISED: {formula}")
        for route in module.get("routes") or []:
            patch_flow(route.get("flow") or [], hits, where)


CENSUS_HOOK = "https://hook.us1.make.com/rkjnge32bhzvfzar21865l8k9b8sxi18"
AT_BASE = "appou5JVr0WIrioWS"
AT_FORMS = "tblblwPcgqhkPTVec"
MEMBER_LINK_FIELD = "fldT1CYVR8w20Qrr4"
MARKER = "INJECTION TEST #63 — delete me"
# Unsanitised this becomes  LOWER({PE})=LOWER("" & {Preferred Email} & "")  — true for EVERY
# member, so the submission links to whoever comes first. Sanitised it is an inert literal
# that matches nobody. The two cases are told apart by the Forms row alone: linked or not.
PAYLOAD_EMAIL = '" & {Preferred Email} & "'


def airtable_pat() -> str:
    env = pathlib.Path("/Users/Born/mds-digest-web/.env.local")
    for line in env.read_text().splitlines():
        if line.startswith("AIRTABLE_PAT="):
            return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("AIRTABLE_PAT not found in mds-digest-web/.env.local")


def at_call(method: str, path: str, query: str = "", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://api.airtable.com/v0/{path}{query}", data=data, method=method
    )
    req.add_header("Authorization", f"Bearer {airtable_pat()}")
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        return json.loads(resp.read())


def replay(tok: str) -> None:
    """Fire one crafted submission at the live census webhook and read the verdict off Airtable."""
    stamp = os.environ.get("STAMP", "manual")
    token_id = f"inj63-{stamp}"
    payload = {
        "event_id": token_id,
        "event_type": "form_response",
        "form_response": {
            "form_id": "census2026",
            "token": token_id,
            "landed_at": "2026-08-10T00:00:00Z",
            "submitted_at": "2026-08-10T00:00:01Z",
            "definition": {
                "id": "census2026",
                "title": "MDS Annual Census 2026",
                "fields": [
                    {"id": "f_email", "ref": "email", "type": "email", "title": "Email"},
                    {"id": "f_name", "ref": "full_name", "type": "short_text", "title": "Full name"},
                ],
            },
            "answers": [
                {
                    "type": "email",
                    "email": PAYLOAD_EMAIL,
                    "field": {"id": "f_email", "ref": "email", "type": "email"},
                },
                {
                    "type": "text",
                    "text": MARKER,
                    "field": {"id": "f_name", "ref": "full_name", "type": "short_text"},
                },
            ],
        },
    }
    req = urllib.request.Request(CENSUS_HOOK, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        print(f"    webhook     {resp.status} {resp.read().decode()[:40]}")

    print("    waiting 25s for the instant run…")
    time.sleep(25)

    found = at_call(
        "GET",
        f"{AT_BASE}/{AT_FORMS}",
        f"?filterByFormula={urllib.parse.quote(f'{{Name}}=\"{MARKER}\"')}&maxRecords=5",
    )
    rows = found.get("records", [])
    if not rows:
        print("    ⛔ no test row in Forms — the run errored before the create; check the execution")
        sys.exit(1)
    for row in rows:
        linked = row["fields"].get("Link to Member (restored)")
        print(f"    test row    {row['id']}  linked_member={linked!r}")
        if linked:
            print("    ⛔ FAIL — the crafted email still matched a member. ROLL BACK NOW.")
            sys.exit(1)
    print("    ✅ PASS — crafted email matched nobody; the literal can no longer be escaped.")
    print(f"    cleanup     python3 {sys.argv[0]} --cleanup")


def cleanup() -> None:
    found = at_call(
        "GET",
        f"{AT_BASE}/{AT_FORMS}",
        f"?filterByFormula={urllib.parse.quote(f'{{Name}}=\"{MARKER}\"')}&maxRecords=10",
    )
    ids = [r["id"] for r in found.get("records", [])]
    if not ids:
        print("nothing to clean")
        return
    at_call("DELETE", f"{AT_BASE}/{AT_FORMS}", "?" + "&".join(f"records[]={i}" for i in ids))
    print(f"deleted test rows: {ids}")


def rollback(tok: str) -> None:
    stamp = os.environ["STAMP"]
    for sid in SCENARIOS:
        backup = BACKUP_DIR / f"{sid}-{stamp}.json"
        blueprint = json.loads(backup.read_text())
        call("PATCH", f"/scenarios/{sid}", tok, {"blueprint": json.dumps(blueprint)})
        print(f"restored {sid} from {backup}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the change (default: dry run)")
    ap.add_argument("--only", type=int, action="append", help="limit to this scenario id (repeatable)")
    ap.add_argument("--verify", action="store_true", help="after applying, replay a crafted submission")
    ap.add_argument("--cleanup", action="store_true", help="delete the test rows the replay created")
    ap.add_argument("--rollback", action="store_true", help="restore both scenarios from STAMP backups")
    args = ap.parse_args()
    targets = {k: v for k, v in SCENARIOS.items() if not args.only or k in args.only}

    if args.cleanup:
        cleanup()
        return
    if args.rollback:
        rollback(token())
        return

    tok = token()
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = os.environ.get("STAMP", "manual")

    for sid, name in targets.items():
        blueprint = call("GET", f"/scenarios/{sid}/blueprint", tok)["response"]["blueprint"]
        backup = BACKUP_DIR / f"{sid}-{stamp}.json"
        backup.write_text(json.dumps(blueprint, indent=1))

        hits: list[str] = []
        patch_flow(blueprint["flow"], hits)
        clean = [h for h in hits if "UNRECOGNISED" not in h]
        odd = [h for h in hits if "UNRECOGNISED" in h]

        print(f"\n=== {sid} {name}")
        print(f"    backup      {backup}")
        print(f"    rewritten   {clean or 'NONE — already fixed, or the formula changed shape'}")
        if odd:
            print(f"    ⚠️  review   {odd}")
        if not clean:
            continue

        if not args.apply:
            print(f"    before      {VULNERABLE}")
            print(f"    after       {FIXED}")
            print("    (dry run — nothing written)")
            continue

        call("PATCH", f"/scenarios/{sid}", tok, {"blueprint": json.dumps(blueprint)})
        after = call("GET", f"/scenarios/{sid}", tok)["scenario"]
        after["blueprint"] = call("GET", f"/scenarios/{sid}/blueprint", tok)["response"]["blueprint"]
        live: list[str] = []

        def collect(flow: list) -> None:
            for module in flow:
                f = (module.get("mapper") or {}).get("formula")
                if isinstance(f, str):
                    live.append(f)
                for route in module.get("routes") or []:
                    collect(route.get("flow") or [])

        collect(after["blueprint"]["flow"])
        ok = FIXED in live and VULNERABLE not in live
        print(f"    live now    {[f for f in live if 'Preferred Email' in f]}")
        print(f"    isinvalid   {after.get('isinvalid')}  isActive {after.get('isActive')}")
        print(f"    VERIFIED    {'YES' if ok and not after.get('isinvalid') else 'NO — investigate'}")
        if not ok or after.get("isinvalid"):
            sys.exit(1)

    if args.apply and args.verify:
        print("\n=== replay: one crafted submission through the LIVE census webhook")
        replay(tok)


if __name__ == "__main__":
    main()
