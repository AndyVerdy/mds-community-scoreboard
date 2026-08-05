> 📌 Member-facing. Drafted by Claude, **validated and posted by Andy**. Everything below is live
> on production (`7f7b932f`, 4 August 2026) and was verified end-to-end before promotion.

# WhatsApp message — ready to paste

> ⚠️ **Two different syntaxes — do not mix them.** WhatsApp: `*bold*` (single asterisk).
> ClickUp / Notion / docs: `**bold**` (double). Pasting the WhatsApp version into ClickUp renders
> every heading as *italic* and collapses the blank lines — that is what went wrong on the first
> paste, not the copy itself. Slack uses the WhatsApp style (`*bold*`).


*MDS Assistant — what's new* 🗓️ 4 August

*Tap instead of type* ✅
Yes/no questions now come with buttons — tap *Yes* or *No thanks* instead of typing it out. Your
billing portal arrives as a button too.

*Reports get confirmed before they're filed* 📝
Say "I want to report a bug" and I'll ask what happened, read your words back, and file it only
when you tap *Send it* — with *Add more* if you're still typing, or *Cancel* to drop it.

*Recommendations you'd actually pick* 🧠
Events, videos, partners and chats are now judged, not just listed — what each one is genuinely
good for, matched against what you're working on. Two members asking the same question get
different answers.

*Accurate partner rankings* ⭐
"Which partners have the most reviews?" · "Who's highest rated?" · "Which are most claimed?" —
the whole directory gets sorted before answering, instead of a handful being sampled.

*Your MDS credit* 💳
Ask "how much MDS credit do I have?" and you'll get your current account balance.

*Find members anywhere* 🌍
"Who's based in Germany?" · "Who's in the Balkans?" · "Who's in the Southern states?" — countries,
regions and US states all work now.

*Follow-ups stay on topic* 💬
Ask about lenders, then "how about on Facebook?" — you'll get lenders on Facebook, not a topic
from earlier in the day. Replying directly to one of my messages keeps that thread too.

*Straighter answers* 🎯
Fewer "on it, checking…" holding messages, fewer answers held back as unverified, and no invented
people — if someone isn't a member, I'll say so.

Spotted something off? React 👎 to any answer or just tell me — it goes straight to the team.

---

# Same message for ClickUp / docs (double asterisks = bold there)

**MDS Assistant — what's new** 🗓️ 4 August

**Tap instead of type** ✅

Yes/no questions now come with buttons — tap **Yes** or **No thanks** instead of typing it out. Your billing portal arrives as a button too.

**Reports get confirmed before they're filed** 📝

Say "I want to report a bug" and I'll ask what happened, read your words back, and file it only when you tap **Send it** — with **Add more** if you're still typing, or **Cancel** to drop it.

**Recommendations you'd actually pick** 🧠

Events, videos, partners and chats are now judged, not just listed — what each one is genuinely good for, matched against what you're working on. Two members asking the same question get different answers.

**Accurate partner rankings** ⭐

"Which partners have the most reviews?" · "Who's highest rated?" · "Which are most claimed?" — the whole directory gets sorted before answering, instead of a handful being sampled.

**Your MDS credit** 💳

Ask "how much MDS credit do I have?" and you'll get your current account balance.

**Find members anywhere** 🌍

"Who's based in Germany?" · "Who's in the Balkans?" · "Who's in the Southern states?" — countries, regions and US states all work now.

**Follow-ups stay on topic** 💬

Ask about lenders, then "how about on Facebook?" — you'll get lenders on Facebook, not a topic from earlier in the day. Replying directly to one of my messages keeps that thread too.

**Straighter answers** 🎯

Fewer "on it, checking…" holding messages, fewer answers held back as unverified, and no invented people — if someone isn't a member, I'll say so.

Spotted something off? React 👎 to any answer or just tell me — it goes straight to the team.

---

## Notes for Andy (not for members)

**Two claims from the first draft were removed, deliberately:**
- *"Links now also appear as proper buttons… like registrations"* — WhatsApp allows exactly **one**
  URL button per message, and only the billing portal is wired. An events answer with three
  registration links can never have three buttons. Making registrations tappable needs a list-menu
  flow (pick an event → that reply carries the button) — a build, not a copy change.
- *"…events, videos, partners **or chapters**"* — was videos-only at the time of writing. **Now
  true**: partners, events and chats consume their dossiers as of prod `7f7b932f`. Chapters
  themselves have dossiers but no dedicated lane; the copy says "chats" instead.

**Four things added that the first draft missed** — all member-visible and all shipped today:
report confirm-step, the holding message dropping from ~31% of answers to ~2%, fewer false
"couldn't verify" refusals, and the members lane no longer inventing people (former members are
named as former).

**Deliberately not announced:** quoted-reply binding is mentioned only as one clause ("replying
directly to one of my messages") — it is plumbing, not a feature members will go looking for.
