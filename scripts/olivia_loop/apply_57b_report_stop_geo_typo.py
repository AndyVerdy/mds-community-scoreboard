#!/usr/bin/env python3
"""#57/#54 named remainders (2026-08-05) — apply to STAGING (bqHstPDi84uOhTCJ).

(1) "who is FORM africa?" — the typo made her hunt a MEMBER called "Form Africa" and honestly
    decline, when the member plainly meant "who is FROM africa" (which already answers
    correctly: Benjamin, Grand Baie). `form` is normalised to `from` ONLY where a preposition
    is grammatically required (after who/is/are/based/anyone/members...) and never in front of
    a form-noun (submission, field, link, "form a company", "the form"). Done in
    `Resolve Member`, the single point every downstream consumer reads its text from — the
    member's VERBATIM words still persist, because Save Conversation files `Log Inbound`.text.

(2) REPORT CONFIRM STOPS CLEAN. #57 shipped the confirm-step, and the seed rule
    ("confirm in one warm line and STOP") did not hold: the confirmation still appended a soft
    follow-up offer ("if you tell me which event..."). Same remedy as the rest of #57 — take it
    out of the model's hands. On the confirm turn (`period === 'report_file'`), IF
    report_create actually fired, the confirmation IS the whole reply.

Idempotent: anchors asserted, hunks skip when applied.
"""
import json, subprocess, sys, tempfile, os

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


def patch(text, old, new, where):
    if new in text:
        print(f"  {where}: already applied")
        return text
    assert old in text, f"{where}: anchor NOT FOUND"
    assert text.count(old) == 1, f"{where}: anchor x{text.count(old)}"
    print(f"  {where}: patched")
    return text.replace(old, new)


# The normaliser, shared verbatim with the offline harness (test_57b_typo.js).
TYPO_BLOCK = (
    "// TYPO: \"who is FORM africa?\" (Andy 2026-08-04). She hunted a MEMBER named \"Form Africa\"\n"
    "// and honestly declined; \"who is FROM africa\" answers fine. Normalise `form` -> `from` ONLY\n"
    "// where a preposition is grammatically required, and NEVER in front of a form-noun - so\n"
    "// \"the signup form is broken\" and \"form a company\" are untouched. The member's verbatim\n"
    "// words still persist: Save Conversation files Log Inbound.text, not this.\n"
    "function askAs(t) {\n"
    "  return String(t || '').replace(\n"
    "    /\\b(who(?:'s)?|whos|is|are|was|were|based|located|living|lives?|comes?|coming|anyone|"
    "anybody|someone|somebody|people|members?|guys|folks|everyone)(\\s+)form(\\s+)"
    "(?!(?:submissions?|fields?|links?|urls?|pages?|builders?|responses?|entries|entry|data|"
    "answers?|a|an|is|are|was|were)\\b)/gi,\n"
    "    '$1$2from$3');\n"
    "}\n"
    "const askText = askAs(inbound.text);\n"
)


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    # ── (1) Resolve Member: one normalisation point for every consumer ───────
    rm = nodes["Resolve Member"]["parameters"]["jsCode"]
    if TYPO_BLOCK in rm:
        print("  Resolve Member askAs: already applied")
    elif "function askAs(" in rm:
        # An earlier revision of the normaliser is in place — swap the block, keep the wiring.
        start = rm.index("// TYPO:")
        end = rm.index("const askText = askAs(inbound.text);") + len("const askText = askAs(inbound.text);\n")
        rm = rm[:start] + TYPO_BLOCK + rm[end:]
        assert rm.count("text: askText") == 3, "Resolve Member: emitters lost"
        print("  Resolve Member askAs: block REPLACED (revised guard)")
    else:
        anchor = "const rows = $input.all().map(i => i.json).filter(r => r && r.phone);"
        assert rm.count(anchor) == 1, "Resolve Member: rows anchor"
        rm = rm.replace(anchor, TYPO_BLOCK + anchor)
        assert rm.count("text: inbound.text") == 3, "Resolve Member: expected 3 text emitters"
        rm = rm.replace("text: inbound.text", "text: askText")
        print("  Resolve Member askAs: patched (3 emitters rewired)")
    nodes["Resolve Member"]["parameters"]["jsCode"] = rm

    # ── (2) Format Reply: a filed report ends the exchange ───────────────────
    fr = nodes["Format Reply"]["parameters"]["jsCode"]
    fr = patch(fr,
        "// #38: offer-shaped replies become TAP BUTTONS;",
        "// #57 remainder: a CONFIRMED report stops clean. The seed rule (\"confirm in one warm\n"
        "// line and STOP\") kept losing to a trailing soft offer (\"if you tell me which event...\").\n"
        "// Same remedy as the rest of #57 - take it out of the model's hands. Only when\n"
        "// report_create actually fired, so a failed filing is never claimed as a success.\n"
        "try {\n"
        "  const _rp = $('Plan Request').first().json;\n"
        "  if (_rp && _rp.period === 'report_file'\n"
        "      && (sourcesUsed || []).indexOf('report_create') !== -1) {\n"
        "    text = 'Sent to the MDS team \\uD83D\\uDC4D They will see it in their portal.';\n"
        "  }\n"
        "} catch (e) {}\n"
        "// #38: offer-shaped replies become TAP BUTTONS;",
        "Format Reply report_file clamp")
    nodes["Format Reply"]["parameters"]["jsCode"] = fr

    for name in ("Resolve Member", "Format Reply"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(nodes[name]["parameters"]["jsCode"])
            tmp = f.name
        chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        assert chk.returncode == 0, f"{name}: {chk.stderr}"
    print("node --check OK x2")

    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items()
                         if k in ("errorWorkflow", "executionOrder", "executionTimeout",
                                  "saveDataErrorExecution", "saveDataSuccessExecution",
                                  "saveExecutionProgress", "saveManualExecutions", "timezone")}}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    assert r.get("id"), f"PUT failed: {str(r)[:300]}"
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    api("POST", f"/workflows/{STAGING_ID}/activate")

    wf2 = api("GET", f"/workflows/{STAGING_ID}")
    n2 = {n["name"]: n for n in wf2["nodes"]}
    print("VERIFY",
          "askAs:", "function askAs(" in n2["Resolve Member"]["parameters"]["jsCode"],
          "emitters:", n2["Resolve Member"]["parameters"]["jsCode"].count("text: askText"),
          "report_stop:", "report_file'" in n2["Format Reply"]["parameters"]["jsCode"],
          "| version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
