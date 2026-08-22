#!/usr/bin/env python3
"""#107e — verify the NEW empty-pick fallback text does not accidentally match
OFFER_TAIL (extracted live from Format Reply, scratchpad/107e/offer_tail_pattern.txt)
or the other offer-shaped triggers in the same node (reply YES, the ticket phrase).
Run via node so the regex semantics are exactly what n8n will execute (JS /i regex,
not a Python re.IGNORECASE re-implementation that could silently diverge).
"""
import json
import subprocess

NEW_LEAD = (
    "Here are the Summit attendees I've recommended to you that I can reach for "
    "an intro. Pick one and I'll ask them for their ok — they see your name and "
    "the topic, nothing else. I'll message you the moment they respond; if "
    "there's no answer in 7 days I'll let you know and we can try someone else."
)
NEW_FALLBACK = (
    "None of the attendees I've recommended to you can take an intro request "
    "right now. Want other names?"
)

offer_tail_src = open("/Users/Born/Scorecard/scratchpad/107e/offer_tail_pattern.txt").read().strip()

js = f"""
const OFFER_TAIL = {offer_tail_src};
const cases = {{
  lead: {json.dumps(NEW_LEAD)},
  fallback: {json.dumps(NEW_FALLBACK)},
}};
for (const [name, text] of Object.entries(cases)) {{
  const t = text.trim();
  const offerTail = OFFER_TAIL.test(t);
  const replyYes = /reply\\s+YES\\b/i.test(t);
  const ticketPhrase = t.toLowerCase().indexOf('open a ticket with the mds team') !== -1;
  const introOfferTail = /would you like me to connect you with one of them\\?\\s*$/i.test(t);
  console.log(`${{name}} | len=${{t.length}} | OFFER_TAIL=${{offerTail}} | replyYES=${{replyYes}} | ticketPhrase=${{ticketPhrase}} | INTRO_OFFER_TAIL=${{introOfferTail}}`);
}}
"""
open("/Users/Born/Scorecard/scratchpad/107e/offer_tail_check.js", "w").write(js)
r = subprocess.run(["node", "/Users/Born/Scorecard/scratchpad/107e/offer_tail_check.js"], capture_output=True, text=True)
print(r.stdout)
if r.returncode != 0:
    print("NODE ERROR:", r.stderr)
