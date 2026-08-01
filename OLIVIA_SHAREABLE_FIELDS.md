> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# Olivia — the shareable-fields rulebook (#10)

**The one written list of what may be said about a member. Ruled by Andy 2026-08-01.**
Principle first: **default-deny.** Olivia reaches data only through the ~20 gated functions, and
each emits a fixed, named column set. Anything not on this page (address, payment/Stripe data,
IP, government ID, the other ~1,700 AT fields) is NEVER-BY-CONSTRUCTION — no function selects
it, so it cannot leave the database. The gate enforces the emitted sets and probes the scary
names as canaries.

**"Used" ≠ "shareable."** A field may feed calculations while being unspeakable per person —
`Most Recent Revenue` computes the band and the chapter sums but is emitted nowhere per member.

## 🟢 SHARE — fine about a named member (the public card)
name · city · state · country · **revenue BAND only** (1-5M / 5-10M / 10-20M / 20M+) ·
main niche + niches · area of expertise · about-me · hobbies · fun fact · Facebook link ·
chapter(s) · membership state (current/past — reason never) · join date · left date (past
members) · **sales channels** (Amazon US/CA/EU/Other, DTC, Walmart, Wayfair, Wholesale, TikTok
Shop) · **business model** (Private Label / OEM / Agency / Wholesale) · **product categories** ·
shared chats (always relative to the ASKER's own chats) · chapter-lead role + photo (public on
mds.co) · anything the member posted publicly in the group (verbatim content, attributed).

## 🟡 GROUP-ONLY — aggregates fine, never about one person
employee counts · SKU counts · brands count · years in business · age / age bands · TTM revenue
sums + averages · country mixes · band mixes · niche counts. (These live in `chapter_info.
live_stats` and `member_count` breakdowns; a small chapter's sum can still out a whale — Andy's
4b ruling stands open.)

## 🔴 NEVER — not about anyone, not to anyone, no phrasing
exact revenue figures per member · job titles · email · phone · home/business address · payment,
card, bank, Stripe records · IP or device data · government IDs · membership-removal reasons ·
internal admin fields (event budgets, member LTV, lead scoring) · another member's persona,
billing, dossier, census/application raw answers · anything from a chat the asker is not in.
Self-exception: a member may see their OWN billing, dossier, application answers (self-only
functions, fail-closed).

## Enforcement
- The gate (`scripts/olivia_leak_gate.py`) pins `member_card`'s exact column set to this page
  and probes canary names (address / credit / stripe / ip / email / phone keys) across outputs.
- Consistency AC: the same field asked about different members answers or refuses identically.
- Change process: edit THIS page + the gate check in the same commit, or the gate goes RED.
