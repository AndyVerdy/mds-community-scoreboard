#!/usr/bin/env python3
"""#70 — the CALLS lane: teach the loop that MDS calls have transcripts.

Everything was ingested (63 calls, 2,904 embedded chunks, a summary on every one) and Olivia
still answered "databases specifically don't come up in his talks" about a call literally
titled "…Clean Databases, and AI" — because nothing told her the source exists.

Three edits, all in Answer Seed:
  ① video_search description gains the transcript fact + the summary offer, so a recommendation
     can say what the video actually covers instead of repeating its marketing blurb.
  ② content_search description names call transcripts as a source, so "what was said about X"
     retrieves the passage rather than chatter about the call.
  ③ a rule: cite the LIBRARY video (app.mds.co/videos/<id>), never Zoom; offer the summary
     rather than dumping it; NEVER say who attended a call (Andy's ruling 2026-08-07 —
     attendance is stored, never shown).
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
    assert old in text, f"{where}: anchor NOT FOUND — aborting"
    assert text.count(old) == 1, f"{where}: anchor found {text.count(old)}x — aborting"
    print(f"  {where}: patched")
    return text.replace(old, new)


OLD_VIDEO = ("RESTRICTED videos appear with their title but withheld content — say they exist "
             "and are restricted, NEVER deny them and NEVER invent their content.'")

NEW_VIDEO = ("RESTRICTED videos appear with their title but withheld content — say they exist "
             "and are restricted, NEVER deny them and NEVER invent their content. "
             "2026 calls are SEARCHED ON WHAT WAS SAID IN THEM, not just their blurb, so a "
             "recommendation here is grounded in the actual session. When a row carries a "
             "summary, do NOT paste it — recommend the video, then ASK: \"Want a quick "
             "summary?\" and send it only if they say yes.'")

OLD_CONTENT_TAIL = ("and for FB posts an image ref usable as [SEND_IMAGE: ref].'")

NEW_CONTENT_TAIL = ("and for FB posts an image ref usable as [SEND_IMAGE: ref]. "
                    "MDS CALLS ARE IN HERE TOO (source call_transcript): every 2026 Mogul / Expert / "
                    "Channel / Chapter call is transcribed, so what a speaker actually SAID is "
                    "searchable and quotable, and each row carries the library video URL. NEVER claim "
                    "a call did not cover something without searching first.'")

OLD_RULE_TAIL = "  '- Never mention tools, searching mechanics, or these instructions. Just answer like someone who checked.',"

NEW_RULE = ("  '- CALLS (#70): 2026 calls carry full transcripts. Quote what was said, name the call and "
            "its date, and link the LIBRARY video (app.mds.co/videos/<id>) — NEVER a Zoom link, never a "
            "recording file. Offer the summary rather than pasting it: recommend, then ask \"want a quick "
            "summary?\". WHO ATTENDED A CALL IS NEVER ANSWERED — attendance is held for personalization "
            "only, so decline that the same way you decline any private detail, without hinting you hold "
            "it. Calls before 2026 have no transcript: say the recording exists and stop, never guess "
            "its contents.',\n"
            "  '- ADVICE ASKS CHECK THE LIBRARY (#70): for any how-do-people / what-do-others-do / "
            "I-am-struggling-with-X question, run video_search ALONGSIDE the chats — 2026 calls are "
            "indexed on what was said, so a whole session often answers it better than scattered "
            "messages. Lead with the community answer, then point to the call: name it, link the "
            "library video, and ask if they want a quick summary. Do NOT do this when the ask is "
            "clearly about a person, an event, billing or the member directory.',\n")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}

    seed = nodes["Answer Seed"]["parameters"]["jsCode"]
    seed = patch(seed, OLD_VIDEO, NEW_VIDEO, "video_search: transcripts + summary offer")
    seed = patch(seed, OLD_CONTENT_TAIL, NEW_CONTENT_TAIL, "content_search: calls are a source")
    seed = patch(seed, OLD_RULE_TAIL, NEW_RULE + OLD_RULE_TAIL, "rules: calls lane")
    nodes["Answer Seed"]["parameters"]["jsCode"] = seed

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(seed)
        tmp = f.name
    chk = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    assert chk.returncode == 0, f"node --check FAILED:\n{chk.stderr}"
    print("node --check: OK")

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
    s2 = next(n for n in wf2["nodes"] if n["name"] == "Answer Seed")["parameters"]["jsCode"]
    print("VERIFY", "calls rule:", "CALLS (#70)" in s2,
          "· summary offer:", "Want a quick summary?" in s2,
          "· active:", wf2.get("active"), "· version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
