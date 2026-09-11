#!/usr/bin/env python3
"""#206 + the over-claim rule cluster from #190's exam (STAGING only).

#206 — "can you do past posts on Facebook from many years ago?" was answered "the further back you
go the thinner it gets". The real answer is a number, and now a tool says it: content_stats gained
a `coverage` metric (migration content_stats_coverage_206_20260911), one row per source with its
count, its earliest and latest date, and how many items predate 2025 — Facebook reads 4,280 items,
2021-08-17 to 2026-09-10, 5 before 2025. A coverage question now routes there, and the existing
`stats` renderer prints it for free.

The rest of this patch is the over-claim cluster: seven exam answers named a person, a brand, a
capability or an offer the evidence never gave them. Each rule below is anchored to one of them —
5042 (four unverified expert names), 5061 (offered Ramon Gonzalez for Roman Khan), 5068 (Hector
credited to the wrong person), 5067 (StoreClaw's Summit offer detail dropped), 5008 (reminders
overclaimed beyond Summit items), 5032 (declined the roster, then listed names from Facebook),
5098 ("they" with no antecedent answered anyway), 5034 (no Montreal event and no nearest one),
5011 (a distance question refused instead of answered by city).
"""
import json
import subprocess
import sys

ENV = "/Users/Born/mds-digest-web/.env.local"
STAGING_ID = "bqHstPDi84uOhTCJ"


def env(k):
    for line in open(ENV):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(k)


BASE, KEY = env("N8N_API_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, payload=None):
    cmd = ["curl", "-sS", "-X", method, f"{BASE}/api/v1{path}", "-H", "X-N8N-API-KEY: " + KEY,
           "-H", "Content-Type: application/json", "--max-time", "180"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


PLAN_ANCHOR = "  params = { p_phone: mem.to, p_member: mname };"
PLAN_NEW = """  params = { p_phone: mem.to, p_member: mname };"""

# The coverage override rides at the very end of the chain, after op/params are settled.
COVER_ANCHOR = "return [{ json: { first_contact: first_contact, ticket_ask: ticketAsk, window_days: askWindowDays, all_sources: allSources, not_in_chat: notInChat, route: route, intent: intent, focus_chat: chat,"
COVER_NEW = """// #206 (2026-09-11): a COVERAGE question is answered with dates, not with a feeling. "Can you do
// past posts from many years ago?" got "the further back you go the thinner it gets"; the real
// answer is 4,280 Facebook items from 2021-08-17 to 2026-09-10 of which 5 predate 2025. The
// `coverage` metric on content_stats reports that per source, through the asker's own visibility,
// and the existing `stats` renderer already prints label/value/detail rows.
try {
  const _cvT = String(rawText || '');
  if (/\\b(how far back|how many years|date range|go(?:es)? back|years ago|how current|how up ?to ?date|how recent|what period|since when|how much history|full history)\\b/i.test(_cvT)
      && /\\b(post|posts|facebook|fb|chat|chats|message|messages|data|content|library|archive|see|access|records?|history)\\b/i.test(_cvT)) {
    route = 'llm'; planPeriod = 'stats';
    op = 'content_stats';
    params = { p_phone: mem.to, p_metric: 'coverage' };
    raw_op = 'content_search';
    raw_params = { p_phone: mem.to, p_terms: [], p_sources: ['fb_post'], p_limit: 0, no_embed: true };
  }
} catch (e) {}
"""

SEED_ANCHOR = ("name: 'content_stats', description: 'COUNT things instead of listing them. "
               "p_metric: messages|posts|authors|by_chat|by_author. Use for \"how many/most active/count\" "
               "questions about content.'")
SEED_NEW = ("name: 'content_stats', description: 'COUNT things instead of listing them. "
            "p_metric: messages|posts|authors|by_chat|by_author|coverage. Use for \"how many/most active/count\" "
            "questions about content. p_metric=coverage answers HOW FAR BACK you can see: one row per "
            "source with its item count, its earliest and latest date, and how many items predate 2025 - "
            "use it for any how-far-back / date-range / how-current question instead of describing "
            "coverage in words.'")

RULES_ANCHOR = "'HONESTY: Use ONLY the data provided in this message. Never guess, invent or infer facts, names, numbers, dates or links. If the answer is not here, say so plainly and, when useful, point them where they could find it.',"
RULES_NEW = RULES_ANCHOR + """
  'NAMES COME FROM THE TOOL (#190): every member, brand, partner, speaker or tool you NAME must appear in the evidence below. Four names in one answer were not there, a partner was credited to the wrong founder, and a near-miss suggestion offered somebody the tool never returned. If you can only justify two names, give two. When you offer a near match for a name we do not have, it must be a name the tool returned - otherwise say plainly that nobody by that name is on file and stop.',
  'STATE THE OFFER YOU WERE GIVEN (#190): when a partner row carries an offer, an event offer or a discount, say what it actually is - the value and how to claim it. "They have a Summit offer" without the offer is a half-answer.',
  'CAPABILITY IS THE LIST, NOT A GUESS (#190): reminders exist ONLY for Summit schedule items. There are no daily reminders, no recurring routines, no watching a thread for changes. Say what you can do and offer the ticket for the rest; never widen a capability to sound helpful.',
  'A DECLINE IS NOT A WORKAROUND (#190): if you decline to give a list - an attendee roster above all - do not then assemble the same list from Facebook, chats or anywhere else. Decline, then offer what you CAN do (who to meet on their topics, the sessions, the public posts).',
  'NO ANTECEDENT, NO ANSWER (#190): if "they", "it", "that one" or "the call" has nothing to point at in this turn or in the conversation so far, ask which one in a single line rather than picking a likely candidate and answering about it.',
  'WIDEN ONCE, AND SAY SO (#190): when a place has nothing - no event in that city, nobody in that town - widen to the region or country ONE step and say what you widened to ("nothing in Montreal; the nearest is Toronto on Sept 14"). Never answer a place question with a bare no when a neighbour is on file.',
  'DISTANCE IS NOT A FILTER (#190): members are matched by city, state and country - there are no distances or drive times. For a "within X hours/miles" question, say that plainly, then give the members in the nearby cities you DID find and offer the wider list. Refusing outright is wrong; inventing a radius is worse.',"""


def patch(node, edits, label):
    code = node["parameters"]["jsCode"]
    before = len(code)
    for old, new in edits:
        n = code.count(old)
        if n != 1:
            print(f"ABORT [{label}]: anchor x{n}, expected 1:\n  {old[:110]}…", file=sys.stderr)
            sys.exit(2)
        code = code.replace(old, new)
    node["parameters"]["jsCode"] = code
    print(f"{label}: {before} -> {len(code)} chars")


def main():
    wf = api("GET", f"/workflows/{STAGING_ID}")
    nodes = wf["nodes"]
    patch(next(n for n in nodes if n["name"] == "Plan Request"), [(COVER_ANCHOR, COVER_NEW + COVER_ANCHOR)], "Plan Request")
    patch(next(n for n in nodes if n["name"] == "Answer Seed"), [(SEED_ANCHOR, SEED_NEW)], "Answer Seed")
    patch(next(n for n in nodes if n["name"] == "Build Prompt"), [(RULES_ANCHOR, RULES_NEW)], "Build Prompt")
    out = api("PUT", f"/workflows/{STAGING_ID}",
              {"name": wf["name"], "nodes": nodes, "connections": wf["connections"],
               "settings": wf.get("settings") or {}})
    print("updated:", out.get("id"), "versionId", out.get("versionId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
