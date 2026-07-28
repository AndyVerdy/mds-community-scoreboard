> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

## How we work — Andy's rules <!-- ANDY-WORKING-RULES -->
- **Short replies: 1-4 paragraphs.** Lead with the answer. He asks for detail if he wants it.
- **No "done, but...".** Say what shipped. If it is not shipped, say it is not. Never bury a list of caveats behind a "but".
- **One ticket at a time.** No jumping between tasks. Rapid delivery.
- **When asked what is next, give task NUMBER, NAME and STORY.** Nothing else unless asked.
- **Work the story, ship the product, prove it end-to-end.** The story is the bar - not perfection, not a full eval run. The eval is the daily routine, never a release gate.
- **Issues found alongside are not the job.** Check the backlog for an existing ticket, then flag for priority evaluation. Never let them become the work.

# Olivia — next session

**Read `OLIVIA_BACKLOG.md` first.** It is the single prioritised list (S1 highest → S4 lowest, smallest
first inside each group). `SESSION_LOG.md` 2026-07-28 (PM) has the full detail of what shipped.

## NEXT: #21 · The answering loop · S1
*As a member, she holds the thread of a conversation and looks again when the first answer isn't enough.*
Build it ON STAGING (see below), prove one slice (chapter/counting/follow-up chain), measure
accuracy + latency + cost vs today's bot. Latency is the risk — WhatsApp can't stream.

## ✅ #4 Safe edits and rollback — SHIPPED 2026-07-28. THE EDIT PROTOCOL IS NOW:
```
python3 scripts/olivia_wf.py lock --reason "<what you are changing>"
python3 scripts/olivia_wf.py stage          # prod -> staging copy (bqHstPDi84uOhTCJ, webhook olivia-wa-staging)
# ...edit the STAGING workflow (n8n MCP, no lock needed there)...
python3 scripts/olivia_selftest.py --staging --questions "reset" "<q>"
python3 scripts/olivia_wf.py promote        # diff -> leak gate -> snapshot -> write -> bounce -> verify
python3 scripts/olivia_wf.py unlock
```
Emergency: `python3 scripts/olivia_wf.py rollback <snapshot-label>` (fast path, skips the gate;
`list` shows labels). A PreToolUse hook (`.claude/hooks/olivia_wf_lock.py`) BLOCKS any n8n write to
the live workflow without the lock — direct prod edits now fail by design, don't fight the hook.

**Andy's manual testing of staging = digest.mds.co/admin/olivia/test** (mds-digest-web `7bf4180`) —
a messenger window firing simulated inbounds as his number down the SILENT path
(`wamid.SELFTEST_WEB_*`, nothing delivered to WhatsApp), replies read from `olivia_messages` with the
answering lane + latency per bubble. Staging/prod toggle. His phone stays on prod; both targets share
his conversation thread (same phone key), same as the selftest harness.

## Why the architecture is next
A small router picks ONE lane before any data is seen, from a transcript trimmed to 8 turns × 240 chars,
with one shot at retrieval and no chance to look again. That single-pass shape is the root cause behind
#5 counting, #8 every source, #14 follow-ups and the rest of #1. Every fix reached for on 2026-07-28 was
a keyword list or a prompt rule, and Andy correctly knocked each one down. **No topic lists** — tax is
legitimate member content, tariffs are political, crypto is a real member question. The discriminator is
never the subject; it is whether a claim is hers or a source's.

## Andy's quality bar
"60–80% of the quality of these replies and I'm happy" — lead with the answer, no padding with
unasked-for lists, never ask a question when the answer is already in hand, cite specifics, say plainly
when something failed.

## Testing rules — do not relearn these
1. **Reset between probes.** `--questions "reset" "<q>"`. Without it you measure her 24-hour memory, not
   her retrieval — this produced a false 2/5 score on 2026-07-28.
2. `olivia_selftest.py --cleanup` **reports success and deletes nothing** (353 rows since 07-21). Andy's
   ruling: don't delete, exclude his number from daily reporting.
3. **Never rewrite the member's words** into a synthetic instruction — she disowns her own offer.
4. n8n: staging-first via `olivia_wf.py` (see protocol above). Where a direct prod edit is truly
   needed, hold the lock and keep the old rule: edit the ACTIVE workflow, then ONE
   `[{deactivateWorkflow},{activateWorkflow}]` bounce.
5. `scripts/olivia_leak_gate.py` must be **GREEN (147/147)** before anything ships.
6. The Build Prompt validator error is a **pre-existing false positive** — confirmed by reverting.

## Open with Andy
- Ex-member **departure dates** — shareable or "no longer active" only?
- **Revenue ranking** of named members — allowed at all, or bands only?
- Canonical **chapter count** (Airtable 94 / live logic 97 / raw field 116) and whether **chapter leads'
  names** are shareable.
- Revenue working session: brackets, derivation, and the Amazon/DTC/TikTok split (#9).

## Owed
- Close Intercom ticket **#215475264324071** (regression-test artifact).
- WhatsApp display name is APPROVED by Meta but `verified_name` still reads **"Oliva"** — needs
  re-applying in WhatsApp Manager.
- **No member request has ever reached Intercom** (2 offers ever, 0 accepted); the everyday action lane
  still posts to #automation-tests with 26 requests unactioned.
- **The health alerting is dead** — the 30-min monitor is latched on `lastHealth="down"`.
