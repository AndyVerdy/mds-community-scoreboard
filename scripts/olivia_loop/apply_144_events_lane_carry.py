#!/usr/bin/env python3
"""#144: a follow-up about events stays in the events lane — apply to STAGING (on top of #141).

Verified still present 2026-09-08 00:44Z (staging, bank C 6372, rows 65729/65731): one turn after
event_lookup listed MDS Summit Cancun 2027 (Sep 26, 2027), "Can you let me know when they announce the main
meetup for 2027? This year is Singapore" was planned as a content search (`search_all`) and she answered
"I don't have anything announced yet for the main annual Summit in 2027" — contradicting her own previous
turn. The 2027 events ARE reachable now (6370 and 6400 passed on the same run through event_lookup); what
fails is lane continuity: the router reads the follow-up as a question and the plan leaves the events lane.

  Plan Request  eventsLaneCarry(rawText, prevPlan): a message of ≤20 words after an event_lookup turn that
                names an event word (summit · meetup · event · inspire · mastermind · retreat …) or a year
                keeps the events lane, with the year and the event word added to the terms. Ticket and offer
                acceptances keep their precedence (they are checked earlier in the lane chain). Pure function;
                test_144_events_lane_carry.js runs it against this node's own bytes.

  python3 scripts/olivia_loop/apply_144_events_lane_carry.py --dry-run DIR
  python3 scripts/olivia_loop/apply_144_events_lane_carry.py            # edits STAGING, one bounce

Idempotent: skipped when the node already carries the #144 marker; requires #143 (its anchor).
"""
import json, os, subprocess, sys, tempfile

STAGING_ID = "bqHstPDi84uOhTCJ"
ENV = "/Users/Born/mds-digest-web/.env.local"
MARK = "#144"
NODE = "Plan Request"


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


FUNC = r"""// #144 EVENTS-LANE CARRY (bank C 6372, staging rows 65729/65731, 2026-09-08). One turn after event_lookup
// listed Summit Cancun 2027, "when do they announce the main meetup for 2027?" was planned as a content
// search and she said nothing is announced for 2027. A short follow-up naming an event word or a year
// after an event_lookup turn stays in the events lane. Pure function; test_144_events_lane_carry.js runs it.
function eventsLaneCarry(rawText, prevPlan) {
  const t = String(rawText || '').trim();
  if (!t || t.split(/\s+/).filter(Boolean).length > 20) { return null; }
  if (!prevPlan || typeof prevPlan !== 'object' || prevPlan.op !== 'event_lookup') { return null; }
  const ev = t.match(/\b(summit|meet-?ups?|events?|inspire|masterminds?|retreats?|conferences?|gatherings?|dinners?|workshops?)\b/i);
  const yr = t.match(/\b(20[2-3][0-9])\b/);
  if (!ev && !yr) { return null; }
  const terms = [];
  if (yr) { terms.push(yr[1]); }
  if (ev) { terms.push(ev[1].toLowerCase().replace(/-/g, '').replace(/s$/, '').replace(/^meetup$/, 'meetup')); }
  return { terms: terms };
}
"""

CARRY = (
    "// #144: a follow-up about events after an event_lookup turn stays in the events lane (ticket and offer\n"
    "// acceptances are checked earlier in the chain and keep their precedence)\n"
    "try {\n"
    "  const _evc = eventsLaneCarry(rawText, ctx.prev_plan);\n"
    "  if (_evc && intent !== 'events' && intent !== 'eventwho') {\n"
    "    intent = 'events'; followup = true;\n"
    "    const _st = Array.isArray(p.search_terms) ? p.search_terms.slice() : [];\n"
    "    _evc.terms.forEach(function (w) { if (_st.indexOf(w) === -1) { _st.push(w); } });\n"
    "    p.search_terms = _st;\n"
    "  }\n"
    "} catch (e) {}\n"
)

TERMS_LINE = "const terms = (Array.isArray(p.search_terms) ? p.search_terms : [])"

EDITS = [
    ("// #143 FOLLOW-UP GUARDS (bank C 6095 / 6349", FUNC + "// #143 FOLLOW-UP GUARDS (bank C 6095 / 6349"),
    (TERMS_LINE, CARRY + TERMS_LINE),
]


def node_check(code):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
        p = f.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode == 0, r.stderr


def patch_code(code):
    if MARK + " EVENTS-LANE" in code:
        return code, False
    if "#143" not in code:
        sys.exit(f"ABORT {NODE}: #143 not present — apply #143 first")
    for old, new in EDITS:
        c = code.count(old)
        if c != 1:
            sys.exit(f"ABORT {NODE}: expected 1 occurrence, found {c}\n  {old[:100]!r}")
        code = code.replace(old, new)
    return code, True


def main():
    dry = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--dry-run" else None
    wf = api("GET", f"/workflows/{STAGING_ID}")
    if wf.get("id") != STAGING_ID:
        sys.exit(f"GET failed: {json.dumps(wf)[:300]}")
    print(f"staging {STAGING_ID} versionId {wf.get('versionId')} nodes {len(wf['nodes'])}")
    node = next((n for n in wf["nodes"] if n["name"] == NODE), None)
    if node is None:
        sys.exit(f"ABORT: node {NODE} not found")
    code, changed = patch_code(node["parameters"]["jsCode"])
    if changed:
        ok, err = node_check(code)
        if not ok:
            sys.exit(f"ABORT {NODE}: node --check failed\n{err}")
        node["parameters"]["jsCode"] = code
        print(f"  {NODE}: eventsLaneCarry() + carry, node --check OK")
    else:
        print(f"  {NODE}: already carries {MARK}, skipped")
    if dry:
        os.makedirs(dry, exist_ok=True)
        path = os.path.join(dry, "Plan_Request.js")
        open(path, "w").write(code)
        print(f"  wrote {path}\ndry run: nothing written to n8n")
        return
    if not changed:
        print("nothing to do")
        return
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
    r = api("PUT", f"/workflows/{STAGING_ID}", body)
    if r.get("id") != STAGING_ID:
        sys.exit(f"PUT failed: {json.dumps(r)[:300]}")
    print("PUT ok, versionId", r.get("versionId"))
    api("POST", f"/workflows/{STAGING_ID}/deactivate")
    r = api("POST", f"/workflows/{STAGING_ID}/activate")
    print("bounce ok, active:", r.get("active"))


if __name__ == "__main__":
    main()
