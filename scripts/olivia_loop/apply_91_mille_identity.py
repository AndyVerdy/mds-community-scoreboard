#!/usr/bin/env python3
"""#91 — she is Mille now (Andy 2026-08-18: "make her reply to Mille").

The product got its name the same night the number's display name went to review
("MDS Mille", PENDING_REVIEW). Five surfaces carry the old identity; all move in
one pass, exact-string replacements only:

  Build Prompt + Answer Seed  the system identity line ("You are the MDS AI
                              Assistant…") — becomes Mille, keeps the say-you-are-
                              an-AI honesty clause, adds answers-to-the-name
  Build Generic ×3            the unidentified / inactive / unmatched greetings
  Build Verbatim Digest       the curated #79 intro first line + the beta blurb

#79's "no names" rule meant MEMBER names — the comment is updated to say so
explicitly now that she has one of her own.

Apostrophe discipline (#79's lesson, twice burned): every replacement string is
apostrophe-free ASCII or reuses the existing U+2019; node --check runs on every
changed node before the PUT, and the PUT is followed by ONE deactivate/activate
bounce.
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()
    sys.exit(f"missing {k}")


BASE = env("N8N_API_URL").rstrip("/")
KEY = env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}",
           "-H", f"X-N8N-API-KEY: {KEY}", "-H", "Content-Type: application/json",
           "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


IDENTITY_OLD = ("'You are the MDS AI Assistant, an AI assistant for MDS (Million Dollar "
                "Sellers) members, replying on WhatsApp. If asked, say plainly that you "
                "are an AI assistant.',")
IDENTITY_NEW = ("'You are Mille, the MDS AI assistant for MDS (Million Dollar Sellers) "
                "members, replying on WhatsApp. Your name is Mille — members may address "
                "you as Mille and you answer to the name naturally. If asked, say plainly "
                "that you are an AI assistant.',")

# node name -> list of (old, new, expected_count)
EDITS = {
    "Build Prompt": [(IDENTITY_OLD, IDENTITY_NEW, 1)],
    "Answer Seed": [(IDENTITY_OLD, IDENTITY_NEW, 1)],
    "Build Generic": [
        ("'Hi! I am the MDS AI Assistant, here to help MDS members. Your number is linked",
         "'Hi! I am Mille, the MDS AI assistant, here to help MDS members. Your number is linked", 1),
        ("'Hi! I am the MDS AI Assistant, here to help active MDS members.",
         "'Hi! I am Mille, the MDS AI assistant, here to help active MDS members.", 1),
        ("'Hi! I am the MDS AI Assistant, here to help MDS members. I cannot match",
         "'Hi! I am Mille, the MDS AI assistant, here to help MDS members. I cannot match", 1),
    ],
    "Build Verbatim Digest": [
        ("'Hi 👋 I’m the MDS AI assistant.',",
         "'Hi 👋 I’m *Mille* — the MDS AI assistant.',", 1),
        ("'I am the *MDS AI Assistant*. I am still in *beta* — you are one of the first members trying me.'",
         "'I am *Mille*, the MDS AI assistant. I am still in *beta* — you are one of the first members trying me.'", 1),
        ('// Andy\'s rules: identity is "the MDS AI assistant", NO names, WhatsApp bold is ONE asterisk,',
         '// Andy\'s rules: identity is "Mille, the MDS AI assistant" (named 2026-08-18), NO MEMBER names, WhatsApp bold is ONE asterisk,', 1),
    ],
}


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    changed = 0
    for node_name, edits in EDITS.items():
        code = nodes[node_name]["parameters"]["jsCode"]
        if "Mille" in code and node_name != "Build Verbatim Digest":
            print(f"{node_name}: already carries Mille — skipping")
            continue
        for old, new, want in edits:
            got = code.count(old)
            assert got == want, (f"{node_name}: anchor found {got}x, expected {want}:\n  {old[:90]}")
            code = code.replace(old, new)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(code)
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"node --check FAILED on {node_name}:\n{chk.stderr}"
        nodes[node_name]["parameters"]["jsCode"] = code
        changed += 1
        print(f"{node_name}: {len(edits)} edit(s), node --check OK")

    if not changed:
        print("nothing to do")
        return

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")
    print("PUT + one bounce done")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    for node_name in EDITS:
        c2 = n2[node_name]["parameters"]["jsCode"]
        assert "Mille" in c2, f"{node_name}: Mille missing after PUT"
    assert IDENTITY_OLD not in n2["Answer Seed"]["parameters"]["jsCode"], "old identity survived in Answer Seed"
    assert "I’m *Mille* — the MDS AI assistant" in n2["Build Verbatim Digest"]["parameters"]["jsCode"]
    print("verified on re-read: all five surfaces carry Mille, old identity gone")
    print(f"staging versionId: {wf2.get('versionId')}")


if __name__ == "__main__":
    main()
