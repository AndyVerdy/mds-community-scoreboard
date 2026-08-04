#!/usr/bin/env python3
"""#29 part B — the LOOP carries the personalization (apply to STAGING).

Diagnosis (staging execs 63567/63570): every llm lane answers via the LOOP; Build
Prompt never runs for them. Answer Seed's preload filter `(r.body || r.title)`
silently drops the zeroth fetch whenever the op returns dossier-shaped rows
(kind/label/detail), event rows (event_name) or the multi_source jsonb — so the
personalized retrieval ran and then never reached the model, which re-fetched via
tools (correct data, one wasted round-trip, and the asker context lost for lanes
that fetch partner_lookup directly).

Three Answer Seed edits:
1. Preload filter accepts dossier rows, event rows, member rows and the
   multi_source jsonb — the personalized zeroth fetch becomes guaranteed evidence.
2. ABOUT THE ASKER: when the zeroth fetch is multi_source_v2, its `me` section
   (persona focus + strengths + working-on + location) is rendered into the seed
   user message deterministically — solve/multi answers are tailored every time,
   not only when the model happens to call multi_source.
3. The PERSONA-DRIVEN rule gains the framing constraints (tailor, never recite,
   never call an area weak).

Idempotent: anchors asserted, skips when applied.
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


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = {n["name"]: n for n in wf["nodes"]}
    seed = nodes["Answer Seed"]["parameters"]["jsCode"]

    # 1. preload filter — the zeroth fetch survives for EVERY op shape
    seed = patch(seed,
        "try { preRaw = $('Fetch Raw Matches').all().map(x => x.json).filter(r => r && (r.body || r.title)); } catch (e) {}\n"
        "try { preDig = $('Fetch Summaries').all().map(x => x.json).filter(r => r && (r.body || r.title)); } catch (e) {}",
        "// #29: (body||title) dropped dossier rows (kind/label/detail), event rows and the\n"
        "// multi_source jsonb — the personalized zeroth fetch never reached the model.\n"
        "const keepRow = (r) => r && (r.body || r.title || r.kind || r.event_name || r.chat_name\n"
        "  || r.full_name || r.me || r.partners || r.members || r.events || r.chats || r.fb || r.videos);\n"
        "try { preRaw = $('Fetch Raw Matches').all().map(x => x.json).filter(keepRow); } catch (e) {}\n"
        "try { preDig = $('Fetch Summaries').all().map(x => x.json).filter(keepRow); } catch (e) {}",
        "Answer Seed preload filter")

    # 2. ABOUT THE ASKER — deterministic when the zeroth fetch carries `me`
    seed = patch(seed,
        "const finalUser = preload\n"
        "  ? 'PRELOADED EVIDENCE",
        "// #29: the asker's own context (multi_source_v2 `me`) renders deterministically —\n"
        "// tailoring never depends on the model choosing to call a tool.\n"
        "let meCtx = '';\n"
        "try {\n"
        "  const d0 = preDig.find(function (r) { return r && r.me; });\n"
        "  const me = d0 ? d0.me : null;\n"
        "  if (me) {\n"
        "    meCtx = ['ABOUT THE ASKER (their own MDS profile - tailor with it, never recite it):',\n"
        "      (me.focus ? '- ' + me.focus : null),\n"
        "      (Array.isArray(me.strengths) && me.strengths.length ? '- strong ground: ' + me.strengths.slice(0, 5).join(', ') : null),\n"
        "      (Array.isArray(me.working_on) && me.working_on.length ? '- building up right now: ' + me.working_on.slice(0, 4).join(', ') : null),\n"
        "      ((me.city || me.state) ? '- based in: ' + [me.city, me.state].filter(Boolean).join(', ') : null)\n"
        "    ].filter(Boolean).join(NL) + NL + NL;\n"
        "  }\n"
        "} catch (e) {}\n"
        "const finalUser = preload\n"
        "  ? meCtx + 'PRELOADED EVIDENCE",
        "Answer Seed meCtx")

    # 3. the framing constraints ride the existing persona rule
    seed = patch(seed,
        "never a generic list and never a bare counter-question when their persona already narrows it.',",
        "never a generic list and never a bare counter-question when their persona already narrows it. "
        "An ABOUT THE ASKER block, when present, is that profile already fetched - use it the same way. "
        "FRAMING: tailor with it silently; never recite it back, never say \\'according to your profile\\', "
        "and never call any area weak - a building-up area is what they are focused on now, mention it "
        "only when it helps the answer.',",
        "Answer Seed persona rule")

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
    print("VERIFY keepRow:", "keepRow" in s2, "meCtx:", "ABOUT THE ASKER" in s2,
          "framing:", "FRAMING: tailor" in s2,
          "active:", wf2.get("active"), "version:", str(wf2.get("versionId", ""))[:8])


if __name__ == "__main__":
    main()
